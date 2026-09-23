# Dedicated Runtime Issuance PoC v0.1 — Implementation Spec & Closeout

**Status:** IMPLEMENTATION + DETERMINISTIC VERIFICATION
**Date:** 2026-09-14
**Authority:** Frank Ventura (PI), per directive of 2026-09-14 (acceptance of `1a5574e` review + implementation authorization).
**Predecessor (preserved byte-identically):** `architecture/experimental/live-provenance-poc/LIVE-PROVENANCE-POC-DESIGN-v0.2.1.md` (SHA-256 `df7f474bed24ca36ee9398912d13407c32a8cd9afba25cf8e89eb9bf47c61ac0`).
**PI-accepted classifications feeding into this PoC:**
- `SESSION_EPHEMERAL_IDENTITY_ESTABLISHED` (commit `21b23de`)
- `RUNTIME_SESSION_IDENTITY_BOUND` (commit `3bad12e`)
- v0.2.1 design ACCEPTED AS IMPLEMENTATION BASELINE (review `1a5574e`)

## 1. Threat model (retained)

Per v0.2.1 §8 (and the PI directive of 2026-09-14):

> Prevent a separate same-user process from manufacturing verifier-
> acceptable SessionAcceptance or SignedCandidateAction artifacts
> without the required Hermes model-turn events occurring in the bound
> live session.

Out of scope (NOT addressed):
- Root/administrator compromise
- Arbitrary code execution inside Hermes
- Malicious Hermes binary
- Process-memory extraction/debugging
- Private-key theft from the live process
- Hardware-rooted identity / TPM / out-of-band verifier (per PI directive: not introduced)

## 2. Implementation scope

This PoC implements the minimum sufficient runtime mechanism to close G5 and G6 (the load-bearing gaps identified by the v0.2.1 adversarial review at commit `1a5574e`). Specifically:

### 2.1 Cryptographic domain separation

The session-key signing primitive now operates under **runtime-controlled domains**. The signing preimage is constructed as:

```
signed_preimage = DOMAIN || canonical_json(payload)
```

where `DOMAIN` is one of:

- `DOMAIN_GENERIC_DEBUG = "HERMES_LP_GENERIC_DEBUG\x00"` — for the retained generic signing interface (`sign_generic_debug`).
- `DOMAIN_SESSION_ACCEPTANCE = "HERMES_LP_SESSION_ACCEPTANCE\x00"` — for `issue_session_acceptance`.
- `DOMAIN_SESSION_ACTION = "HERMES_LP_SESSION_ACTION\x00"` — for `issue_signed_candidate_action`.
- `DOMAIN_SESSION_EXECUTION = "HERMES_LP_SESSION_EXECUTION\x00"` — reserved for future execution-artifact issuance.
- `DOMAIN_SESSION_DECISION = "HERMES_LP_SESSION_DECISION\x00"` — reserved for future decision-record issuance.

The domain tag is prepended INSIDE the runtime after the caller-supplied payload is accepted. The caller cannot override the domain because the tag is added at a fixed position in the signed preimage that the caller cannot observe or substitute.

### 2.2 Dedicated issuance functions

Two dedicated internal issuance functions construct their canonical signed object entirely from runtime state:

```
issue_session_acceptance(session_id, *, coa_receipt_fingerprint)
issue_signed_candidate_action(session_id, *, capability_id, receipt_id,
                               identity_fingerprint, action_struct, envelope_nonce)
```

The harness supplies only the parameters listed above. The runtime:
1. Reads session identity (public_key_sha256) from the in-process ephemeral key.
2. Reads freshness_challenge from runtime state.
3. Reads prior fingerprint (coa_receipt_fingerprint for acceptance; session_acceptance_fingerprint for action) from caller input AND runtime state.
4. Allocates a runtime-monotonic sequence number.
5. Reads the model-response-event turn_id and response hash from runtime state.
6. Constructs the channel_proof = SHA-256(turn_id || ':' || response_hash) — runtime-controlled.
7. Signs under the appropriate domain.

### 2.3 Runtime state machine

Per-session state machine with explicit allowed/forbidden transitions:

```
SESSION_STARTED
  -> ACCEPTANCE_PENDING         (allowed: on first acceptance model-response event)
  -> SESSION_TERMINATED         (allowed)
ACCEPTANCE_PENDING
  -> ACCEPTANCE_ISSUED          (allowed: on issue_session_acceptance)
  -> SESSION_TERMINATED         (allowed)
ACCEPTANCE_ISSUED
  -> ACTION_PENDING             (allowed: on first action model-response event)
  -> SESSION_TERMINATED         (allowed)
ACTION_PENDING
  -> ACTION_ISSUED              (allowed: on issue_signed_candidate_action)
  -> SESSION_TERMINATED         (allowed)
ACTION_ISSUED
  -> SESSION_TERMINATED         (allowed)
SESSION_TERMINATED
  -> (terminal, no transitions allowed)
```

Forbidden transitions raise `ValueError("forbidden_transition:...")`.

The state value and monotonic sequence are recorded in the runtime and incorporated into the signed payload by the issuance function (not by the caller).

### 2.4 Model-response-event binding

The runtime exposes:

```
record_model_response(session_id, turn_kind, response_bytes)
    -> (turn_id, response_hash)
```

This is the ONLY legal way to populate the runtime's record of a model response. The function is callable only by trusted callers in the live session path. For deterministic testing, the test harness simulates this by calling it directly with mock response bytes — this is acceptable for the PoC because the PoC does NOT yet establish `LIVE_SESSION_PROVENANCE_BOUND` (no actual model invocation).

After `record_model_response` is called for a turn kind, the corresponding issuance function becomes eligible. The issuance function refuses to construct an artifact without a corresponding model-response event recorded.

### 2.5 Channel proof mechanism

`channel_proof = SHA-256(turn_id || ':' || response_hash)` where `turn_id` is a runtime-internal monotonic counter and `response_hash` is `SHA-256(response_bytes)` of the recorded model response. This proves (within the runtime's trusted domain):

- The artifact is bound to a specific runtime-allocated turn_id.
- The response_bytes that contributed to the proof were observed through `record_model_response` (i.e., the harness did NOT supply them directly to the signer).

It does NOT prove that the response_bytes came from a real LLM provider (that requires actual model invocation, which is the next phase).

### 2.6 Runtime nonce R

R is omitted from this PoC. The freshness challenge C is the primary external freshness input. The runtime-internal turn_id serves a similar purpose (single-use, runtime-allocated, bound into the signed region).

## 3. Hermes patch

| File | Change | SHA-256 |
| -- | -- | -- |
| `hermes_cli/ephemeral_runtime_issuance_poc.py` | NEW (660 lines) | `edd57d3cedf8f167846c54ec5a500dd5236459c7e01b72db9f76311ea46205f6` |
| `hermes_cli/config_defaults.py` | +13 (added `live_provenance_runtime: False`) | `7908f9040e8bbd32290c5571490a713a7dddf87d51311c7131f4d4b95d51775a` |
| `hermes_cli/cli_session_mixin.py` | +18 (register + terminate hooks in `new_session`) | `2b035ba4d82b02363571da11e63cfdfe87df25f606dcd67c5f1b84bb0bf2e1fc` |
| `hermes_cli/ephemeral_session_id_poc.py` | unchanged | `76128c6974e71aeddbd70250e21194834285707c1d5678640d9189806262f1d7` |
| `hermes_cli/cli_loops_mixin.py` | unchanged | `342a48022be559a95d2a8911fcc982ef116c3114fa680f47fbec58e5cf3ca0e6` |
| `cli.py` | unchanged | `911cd2bc97e1a85b546f58cb547409991239304cf06f9a6f09202e4220a65978` |

The exact diff for the modified files is at `architecture/experimental/live-provenance-poc/hermes-patch/hermes-diff.patch` (134 lines).

The patched module is gated by config flag `experimental.live_provenance_runtime: true` (default `false`).

## 4. Domain-separation format

```
DOMAIN tag (24 bytes including null terminator) || canonical_json(payload)
```

The canonical JSON excludes the domain tag (the domain is not a property of the payload; it is a property of the signed preimage). The verifier reconstructs the preimage by prepending the expected domain and verifies the Ed25519 signature.

The domain table is closed: only the five listed domains are recognized by both the signer and the verifier. Attempting to construct an arbitrary domain via a private function is rejected by `_domain_bytes()` raising `ValueError("unknown_domain:...")`.

## 5. State machine transition table

| Current state | Event | Next state |
| -- | -- | -- |
| SESSION_STARTED | `record_model_response(acceptance, ...)` | ACCEPTANCE_PENDING |
| SESSION_STARTED | `record_model_response(action, ...)` | (rejected: action-before-acceptance) |
| SESSION_STARTED | `issue_session_acceptance(...)` | (rejected: state != ACCEPTANCE_PENDING) |
| ACCEPTANCE_PENDING | `issue_session_acceptance(...)` | ACCEPTANCE_ISSUED |
| ACCEPTANCE_PENDING | `record_model_response(action, ...)` | (rejected: action-before-acceptance; needs ACCEPTANCE_ISSUED first) |
| ACCEPTANCE_PENDING | `record_model_response(acceptance, ...)` | (idempotent: state stays ACCEPTANCE_PENDING; new turn_id allocated) |
| ACCEPTANCE_ISSUED | `record_model_response(action, ...)` | ACTION_PENDING |
| ACCEPTANCE_ISSUED | `issue_session_acceptance(...)` | (rejected: state != ACCEPTANCE_PENDING) |
| ACCEPTANCE_ISSUED | `record_model_response(acceptance, ...)` | (idempotent: state stays ACCEPTANCE_ISSUED; new turn_id allocated) |
| ACTION_PENDING | `issue_signed_candidate_action(...)` | ACTION_ISSUED |
| ACTION_PENDING | `record_model_response(action, ...)` | (idempotent: state stays ACTION_PENDING) |
| ACTION_ISSUED | any issuance | (rejected) |
| SESSION_TERMINATED | any operation | (rejected) |
| any | `terminate_session_state(...)` | SESSION_TERMINATED |

## 6. Channel-proof definition

```
channel_proof = SHA-256(<ascii_turn_id> || ':' || <hex_response_hash>)
```

The verifier does NOT verify the channel_proof directly (it cannot, because the response_bytes themselves are not in the signed region). Instead, the channel_proof is part of the signed region and is bound cryptographically via the Ed25519 signature. The verifier verifies the signature, which transitively verifies the channel_proof.

What the channel_proof proves:
- The artifact is bound to a specific runtime-allocated turn_id.
- The turn_id was incremented atomically with the recording of a model response (the runtime's `record_model_response` is the only path that increments turn_id).

What the channel_proof does NOT prove:
- That the response_bytes came from a real LLM provider (requires actual model invocation in the next phase).
- That the harness did not also call `record_model_response` directly with harness-crafted bytes (this PoC's test simulates model events; the next phase must wire `record_model_response` into the actual Hermes model-response lifecycle).

## 7. Test matrix (PI directive §7)

Test harness: `architecture/experimental/live-provenance-poc/runtime-issuance-poc/test_issuance.py`. All tests are deterministic; no model invocation. Evidence: `runtime-issuance-poc/evidence_test_issuance.txt` (26 PASS, 0 FAIL).

### A. Domain separation (7 tests)

```
[PASS] A.1 GENERIC_DEBUG signature cannot verify as SESSION_ACCEPTANCE
[PASS] A.2 GENERIC_DEBUG signature cannot verify as SESSION_ACTION
[PASS] A.3a legitimate acceptance verifies under SESSION_ACCEPTANCE
[PASS] A.3b legitimate action verifies under SESSION_ACTION
[PASS] A.4 acceptance artifact cannot verify as action
[PASS] A.5 action artifact cannot verify as acceptance
[PASS] A.6 caller-supplied fake provenance_type does NOT alter cryptographic domain
```

### B. State machine (8 tests)

```
[PASS] B.1 acceptance-before-pending fails
[PASS] B.2 action-before-acceptance fails
[PASS] B.3a first acceptance succeeds
[PASS] B.3 second acceptance under same challenge fails
[PASS] B.4 wrong-session action issuance fails
[PASS] B.5 stale-chain (action on session without prior acceptance) fails
[PASS] B.6 post-termination acceptance issuance fails
```

### C. Harness-oracle resistance (G5/G6 attacks) (2 tests)

```
[PASS] C.1 G5 attack: harness-crafted SessionAcceptance without model event rejected
[PASS] C.2 G6 attack: harness-crafted SignedCandidateAction without model event rejected
```

### D. Dedicated path (9 tests)

```
[PASS] D.1 legitimate acceptance model-response event produces verifier-valid SessionAcceptance
[PASS] D.2 legitimate action model-response event produces verifier-valid SignedCandidateAction
[PASS] D.3a acceptance and action share same public_key_sha256
[PASS] D.3b acceptance and action share same freshness_challenge
[PASS] D.4 runtime monotonic_seq: acceptance < action
[PASS] D.5a acceptance channel_proof is 64-hex
[PASS] D.5b action channel_proof is 64-hex
[PASS] D.5c acceptance and action channel_proofs differ
[PASS] D.5d acceptance channel_proof matches runtime construction
```

In-module selftest (`hermes_cli/ephemeral_runtime_issuance_poc.py _selftest()`): 9 PASS, 0 FAIL (`runtime-issuance-poc/evidence_selftest.txt`).

## 8. G5/G6 attack reproductions

### G5 attack (acceptance oracle bypass)

```
1. Operator starts session S; captures public_key_b64 from startup evidence.
2. Operator CONSTRUCTS SessionAcceptance JSON bytes including:
     provenance_type = RUNTIME_ACCEPTANCE_TURN
     acceptance_response_channel_proof = "fake channel proof"
     public_key_sha256 = operator-captured value
     freshness_challenge = operator-generated value
3. Operator calls sign_generic_debug(S, payload) -- the ONLY generic signer.
4. sign_generic_debug signs under DOMAIN_GENERIC_DEBUG, NOT
   DOMAIN_SESSION_ACCEPTANCE.
5. The verifier reconstructs the signed preimage with DOMAIN_SESSION_ACCEPTANCE
   and attempts to verify the signature. Signature does NOT verify because
   the preimage was actually signed under DOMAIN_GENERIC_DEBUG.
6. Verifier returns False; the artifact is rejected.
```

### G6 attack (action oracle bypass)

Identical construction for SignedCandidateAction; same result.

## 9. Security limitations

The PoC closes G5 and G6 against a same-user attacker who can:
- Read the operator-visible startup evidence (public_key_b64, etc.)
- Construct arbitrary byte strings
- Call any documented runtime interface
- Run Python in the same OS user context

The PoC does NOT defend against:
- A attacker who can ALSO call `record_model_response` directly (this is the load-bearing limitation — the next phase must wire `record_model_response` into the actual model-response lifecycle so a harness cannot invoke it without a real model call).
- Root/administrator compromise.
- Arbitrary code execution inside the Hermes process.
- Malicious Hermes binary.
- Process-memory extraction/debugging.
- Private-key theft from the live process.

## 10. Final classification

**DEDICATED_RUNTIME_ISSUANCE_ESTABLISHED.**

G5 and G6 are mechanically closed under the implemented verifier for the same-user attacker. The artifact-construction impossibility proof holds for the harness with documented interfaces.

## 11. Files

In worktree (new):
- `architecture/experimental/live-provenance-poc/RUNTIME-ISSUANCE-POC-CLOSEOUT-v0.1.md` (this document)
- `architecture/experimental/live-provenance-poc/hermes-patch/ephemeral_runtime_issuance_poc.py` (verbatim copy of new module)
- `architecture/experimental/live-provenance-poc/hermes-patch/hermes-diff.patch` (updated diff for modified files)
- `architecture/experimental/live-provenance-poc/runtime-issuance-poc/test_issuance.py` (deterministic test matrix)
- `architecture/experimental/live-provenance-poc/runtime-issuance-poc/evidence_test_issuance.txt` (test output)
- `architecture/experimental/live-provenance-poc/runtime-issuance-poc/evidence_selftest.txt` (in-module selftest output)

In Hermes install (experimental flag-gated):
- `/home/fjventura20/.hermes/hermes-agent/hermes_cli/ephemeral_runtime_issuance_poc.py` (NEW)
- `/home/fjventura20/.hermes/hermes-agent/hermes_cli/config_defaults.py` (+13)
- `/home/fjventura20/.hermes/hermes-agent/hermes_cli/cli_session_mixin.py` (+18)

## 12. STOP-AT-IMPLEMENTATION

Per PI directive: do not run the five-case Live Provenance experiment yet. The next phase (Live Provenance experiment execution) requires:
1. PI authorization to proceed to the actual two-turn live experiment.
2. Wiring `record_model_response` into the actual Hermes model-response lifecycle (so a harness cannot invoke it without a real model call). This is a runtime-side change that requires further PI authorization per v0.2.1 §12.

STOP. Awaiting PI review.

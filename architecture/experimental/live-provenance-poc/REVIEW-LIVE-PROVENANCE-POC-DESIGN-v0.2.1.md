# Adversarial Design Review — LIVE-PROVENANCE-POC v0.2.1

**Status:** ADVERSARIAL REVIEW (DESIGN ONLY). Does NOT modify v0.2.1.
**Date:** 2026-09-14
**Reviewer:** Hermes (research-manager-mandate-2026-08-27)
**Subject:** `architecture/experimental/live-provenance-poc/LIVE-PROVENANCE-POC-DESIGN-v0.2.1.md` (SHA-256 `df7f474bed24ca36ee9398912d13407c32a8cd9afba25cf8e89eb9bf47c61ac0`)
**Predecessor reviews (preserved byte-identically):**
- `REVIEW-LIVE-PROVENANCE-POC-DESIGN-v0.1.md` (SHA-256 `4a855be1c12c025fb2a6b50b085a0ba8d7fe327859b35b4dfe9e5d0aae28d9f2`)
- `REVIEW-LIVE-PROVENANCE-POC-DESIGN-v0.2.md` (SHA-256 `bdae161e4d19a42976a25330189d0b5993c5e2d7b6cf3d7f17c2c65f0ba8faa7`)

## Controlling question (PI directive)

> Can the harness construct bytes representing a syntactically valid
> SessionAcceptance or SignedCandidateAction, include the expected
> provenance_type itself, submit those bytes through generic
> `sign_for_session()`, and obtain a signature that the Live Provenance
> verifier would accept?

## Gate-by-gate disposition

### G1 — Cross-session composition

**Question:** Can SessionAcceptance from Session A and action from Session B ever satisfy the positive predicate?

**Analysis:**

The `public_key_sha256` in startup evidence (condition 1-2) is the
authoritative session identity. Session A and Session B have different
`public_key_sha256` values (proven in commit `3bad12e` runtime
lifecycle integration verification). Conditions 4a and 7a require
signature verification under the operator-captured `public_key_b64`.
A hybrid envelope (A's SessionAcceptance + B's SignedCandidateAction)
cannot satisfy both conditions because the SessionAcceptance's
`public_key_sha256 = A` and the SCA's `public_key_sha256 = B` would
both need to equal the operator-captured value, which is either A or
B but not both.

Conditions 4d and 7d enforce state-machine monotonicity
(`monotonic_seq(acceptance) < monotonic_seq(action)`), which is a
single per-session counter; cross-session counters would not chain.

**Disposition: PASS.**

### G2 — Stale acceptance / replay

**Question:** Can SessionAcceptance, TGE receipt, challenge, or capability from an earlier turn/session/run satisfy the current chain?

**Analysis:**

Conditions 4c, 5b, 6b, 7c all bind `freshness_challenge = C` (the
operator's current challenge) inside their respective signed regions.
Reusing a prior SessionAcceptance signed with C1 inside a current
envelope with operator challenge C2 fails condition 4c because the
signed_region's challenge field is C1, not C2.

The harness with K_TGE can re-sign a SessionAcceptance with the new
challenge. Condition 4b requires `provenance_type =
RUNTIME_ACCEPTANCE_TURN` — see G5/G6 for whether the harness can
construct such a tag.

Condition 5c provides timestamp ordering as a secondary check; the
runtime-internal `monotonic_seq` (condition 12) is the primary
defense because timestamps can be forged but per-session monotonic
counters cannot be reset without destroying the session.

**Disposition: PASS** (subject to G5/G6 establishing that the harness
cannot bypass `provenance_type` requirement).

### G3 — Foreign action transplant

**Question:** Can a correctly signed candidate action from another session or challenge be transplanted?

**Analysis:**

Condition 7a requires SCA signature to verify under the operator-
captured `public_key_b64` from startup evidence. Session A's and
Session B's ephemeral keys are different (proven in `3bad12e`),
so a Session B SCA fails verification under Session A's captured
key. Condition 7c additionally requires `public_key_sha256` match;
Session B's SCA has Session B's `public_key_sha256`.

**Disposition: PASS.**

### G4 — Metadata substitution

**Question:** Can fabricated session_id, PID, gateway metadata, state.db records, or other textual/operator-visible metadata substitute for possession of the correct session key and runtime event chain?

**Analysis:**

session_id, pid, gateway_state.json, code_sha, code_version, state.db
records are operator-visible and forgeable by a same-user process.
Condition 2 explicitly designates `public_key_sha256` as the
authoritative cryptographic identity (not session_id). Conditions 4a
and 7a require K_IDENTITY signature verification under the operator-
captured `public_key_b64`. The harness cannot forge a valid signature
without the in-process private key.

**Disposition: PASS.**

### G5 — Generic signing-oracle attack (LOAD-BEARING)

**Question:** Can the harness construct bytes representing a syntactically
valid SessionAcceptance or SignedCandidateAction, include the expected
provenance_type itself, submit those bytes through generic
`sign_for_session()`, and obtain a signature that the Live Provenance
verifier would accept?

**Constructing the attack:**

The current patched Hermes v0.21.2 primitive exposes
`sign_for_session(session_id, payload_bytes)` (verified at commit
`21b23de`). The signing operation is domain-agnostic — it signs
whatever bytes the caller supplies. The primitive records the
session_id → keypair mapping but does NOT record any signing-domain
metadata or model-event provenance.

**Attack step 1 — SessionAcceptance:**

1. Operator starts live session S; captures startup evidence
   (session_id, public_key_b64, public_key_sha256).
2. Operator generates challenge C.
3. Operator CONSTRUCTS a SessionAcceptance JSON object:
   ```json
   {
     "session_id": "<S>",
     "public_key_sha256": "<S>",
     "freshness_challenge": "<C>",
     "provenance_type": "RUNTIME_ACCEPTANCE_TURN",
     "acceptance_response_channel_proof": "source: model_response",
     "monotonic_seq": 1,
     "prior_fingerprint": "sha256:...",
     ...
   }
   ```
4. Operator canonicalizes (RFC 8785 JCS) and signs:
   `sign_for_session(S, canonicalized_bytes)`.
5. The resulting signed_bytes contain `provenance_type =
   RUNTIME_ACCEPTANCE_TURN` because the harness put it there.

**Predicate evaluation under v0.2.1 §6:**
- Condition 4a: signature verifies under S's public_key_b64. **PASS.**
- Condition 4b: provenance_type == RUNTIME_ACCEPTANCE_TURN.
  **PASS** (the harness fabricated the tag).
- Condition 4c: signed_region contains session_id, public_key_sha256,
  freshness_challenge, coa_receipt_fingerprint, acceptance_response_hash,
  acceptance_response_channel_proof. The harness filled all of these
  in step 3. **PASS** (the harness fabricated the channel_proof field).
- Condition 4d: monotonic_seq is in the signed region. **PASS.**
- Condition 4e: state machine at acceptance time was
  STATE_AWAITING_ACCEPTANCE_TURN. **???** — the design requires the
  verifier to know the runtime's state machine state at issuance. If
  the verifier cannot verify this, condition 4e cannot be enforced.

**The critical hole:** §3 (dedicated APIs) and §6 conditions 4b/4c
describe what the artifact MUST contain, but they do not describe
a cryptographic mechanism that prevents the runtime from signing
harness-crafted bytes. The current primitive `sign_for_session(session_id,
bytes)` is domain-agnostic.

**A second order issue:** condition 4e requires the verifier to know
the state machine state at acceptance time. The state machine is
runtime-internal; without a cryptographic commitment from the runtime,
the harness can claim any state. The design does not specify how the
state is recorded in the signed region.

**Repeat for SignedCandidateAction:** same attack constructs SCA bytes
with `provenance_type = RUNTIME_ACTION_TURN` and the harness-
fabricated `action_response_channel_proof`. Same result: conditions
7a/7b/7c syntactically pass.

**Disposition: FAIL.** The harness can construct syntactically valid
SessionAcceptance and SignedCandidateAction artifacts and obtain
K_IDENTITY signatures on them via `sign_for_session()`. The
`provenance_type` tag and `acceptance_response_channel_proof` are
strings inside the signed bytes — they are data, not cryptographic
proof. Without a runtime mechanism that cryptographically commits to
the dedicated issuance path (domain separation, dedicated issuance
function with internal byte construction, or a runtime event receipt
incorporated into the signed region), the harness bypasses the
predicate.

### G6 — Dedicated-path forgery

**Question:** Without causing the required model turn, can the harness
invoke any exposed runtime API sequence that results in a verifier-
acceptable SessionAcceptance or SignedCandidateAction?

**Analysis:**

The current patched Hermes v0.21.2 primitive (commit `21b23de`)
exposes only `sign_for_session(session_id, payload_bytes)` for
session-key signing. There are no dedicated runtime issuance APIs
for SessionAcceptance or SignedCandidateAction. The "dedicated APIs"
in v0.2.1 §3 (`runtime_record_acceptance_turn`,
`runtime_record_action_turn`, `runtime_record_execution`,
`runtime_record_decision`) are PROPOSED for future implementation;
they do not yet exist.

The harness today has access to `sign_for_session`. Per G5, this is
sufficient to bypass the predicate. G6 is therefore not yet
addressable by the design as it stands; it requires runtime
implementation per §12 of v0.2.1.

**Disposition: FAIL** (cannot be evaluated as PASS until the proposed
runtime additions in §12 are implemented AND proven to enforce the
required issuance semantics).

## Acceptable mechanism — smallest sufficient

The PI directive lists three acceptable mechanisms:

- **Option A** — Runtime-controlled domain separation
- **Option B** — Dedicated issuance functions
- **Option C** — Runtime event receipts

**Recommended: Option A (smallest sufficient).**

Reasoning:
- Option A requires the smallest code change: the existing
  `sign_for_session` is split into `sign_for_session_generic(session_id,
  bytes)` (domain = GENERIC_DEBUG) and
  `sign_for_session_acceptance(session_id, internal_state)` (domain =
  SESSION_ACCEPTANCE) and `sign_for_session_action(...)` (domain =
  SESSION_ACTION).
- The signing preimage includes the domain tag in a position the
  caller cannot override (prepended by the runtime, not part of the
  caller-supplied payload).
- The verifier checks that the signed_region contains the correct
  domain tag for the artifact type. GENERIC_DEBUG-signed artifacts
  are rejected for SessionAcceptance and SignedCandidateAction.
- Combined with state-machine precondition checks (state ==
  STATE_AWAITING_ACCEPTANCE_TURN before signing), the harness cannot
  call `sign_for_session_acceptance` without the state machine being
  in the correct state, which only happens after a model response has
  been observed.

Option B (dedicated issuance functions with internal byte
construction) achieves the same end but requires re-implementing
signature logic in dedicated functions instead of reusing the
generic signer. More code surface.

Option C (runtime event receipts) is similar to A but requires a
separate event-record data structure. Larger than necessary.

**Combination recommendation:** Option A + state machine precondition
gates. This is the minimum sufficient to close G5/G6.

## Runtime nonce R (re-review)

The design clarifies that R is causal/freshness binding, NOT secret
authentication. This is correct.

If the runtime injects R internally into the prompt before the model
call, R is unknown to the harness and R's presence in the response
proves the response went through the runtime-mediated turn. **In that
case, R does strengthen the design against the harness.**

If R is included in a prompt the operator constructs, the harness
knows R and R contributes no security. The design should specify
WHETHER R is injected by the runtime or supplied by the operator. **The
v0.2.1 design does not specify; this is a small clarification gap,
not a load-bearing finding.**

**Recommendation:** R should be runtime-injected if used. The harness
should not see R.

## Monotonic sequence (re-review)

Conditions 4d, 7c, 10c, 11c, 12 require monotonic sequence numbers in
each artifact's signed region. The design says the sequence is
runtime-internal and incremented only on valid state-machine
transitions.

**The sequence value is a single integer in the signed region**. If
the runtime constructs the bytes-to-be-signed, the sequence value
inside the signed region is whatever the runtime put there — it
cannot be forged by the harness unless the harness controls the
runtime's sequence counter (which it does not, because the counter
lives in the runtime's state).

**However**, the harness CAN call `sign_for_session(session_id,
harness_crafted_bytes_with_seq=42)` and produce a K_IDENTITY
signature on bytes claiming `monotonic_seq = 42`. The signature
verifies, but the value 42 was supplied by the harness, not the
runtime. The verifier cannot distinguish "runtime issued this with
seq=42" from "harness signed bytes claiming seq=42" without
additional evidence.

**Disposition:** Monotonic sequence numbers are necessary but not
sufficient for G5/G6. They must be combined with domain separation
(Option A above) so that the runtime is the only entity that can
produce bytes with the correct `provenance_type` AND the runtime's
sequence counter.

## State machine assessment

The proposed state machine:
```
SESSION_STARTED
→ ACCEPTANCE_PENDING (operator delivers COA + challenge)
→ ACCEPTANCE_ISSUED (SessionAcceptance signed and emitted)
→ ACTION_PENDING (operator delivers action prompt)
→ ACTION_ISSUED (SCA signed and emitted)
→ SESSION_TERMINATED
```

Forbidden transitions:
- ACTION_ISSUED before ACCEPTANCE_ISSUED → must fail
- Second ACCEPTANCE_ISSUED under same challenge → must fail
- ACCEPTANCE_ISSUED after session rotation → must fail
- Any issuance after SESSION_TERMINATED → must fail

The design specifies these forbidden transitions abstractly but does
not yet implement them in the runtime. **Required for READY_FOR_IMPLEMENTATION:**
the runtime additions in v0.2.1 §12 must include explicit transition
functions that raise on forbidden transitions.

## Harness-construction impossibility table

| Artifact | Signing key | Harness has key? | Generic API can create equivalent? | Requires model event? |
| -- | -- | -- | -- | -- |
| SessionAcceptance | K_IDENTITY (runtime Eph25519) | No direct access; can only invoke `sign_for_session` interface | **YES** (current primitive signs any bytes; harness can craft bytes with `provenance_type = RUNTIME_ACCEPTANCE_TURN`) | YES (design intent) — but not enforced by current runtime |
| TGE governance receipt | K_TGE (fixture Ed25519) | YES | YES | NO (no model event required for K_TGE signing) |
| CapabilityToken | K_AUTHORITY (fixture Ed25519) | YES | YES | NO |
| SignedCandidateAction | K_IDENTITY (runtime Eph25519) | No direct access | **YES** (same as SessionAcceptance) | YES (design intent) — but not enforced |
| GEL result | (deterministic; no signing) | N/A (deterministic function of inputs) | YES (harness can call GEL v0.2.2 directly) | NO |
| SignedExecutedAction | K_GEL (fixture Ed25519) | YES | YES (after running GEL, harness can sign with K_GEL) | NO |
| DecisionRecord | K_PIPELINE (fixture Ed25519) | YES | YES (after running v0.2.1 pipeline, harness can sign with K_PIPELINE) | NO |

**For LIVE_SESSION_PROVENANCE_BOUND, the harness must lack the ability
to manufacture at minimum SessionAcceptance and SignedCandidateAction
without triggering their corresponding genuine model-turn paths.**

**As of v0.2.1 + current patched runtime (commit `21b23de`), the
harness CAN manufacture both via `sign_for_session(harness_crafted_bytes)`.
The `provenance_type` tag and `channel_proof` are just strings inside
the signed bytes — they provide syntactic evidence but no
cryptographic proof.**

## Final classification

**DEDICATED_RUNTIME_ISSUANCE_REQUIRED.**

The design is conceptually sound and the amendments A1-A6 are correctly
incorporated. The load-bearing G5/G6 finding is: **the current patched
runtime does not cryptographically enforce the dedicated issuance
path**, so a harness can bypass the predicate via generic
`sign_for_session()` calls with harness-crafted bytes.

**Required before READY_FOR_IMPLEMENTATION:**

1. **Runtime modification** (per v0.2.1 §12): implement the dedicated
   issuance APIs and (recommended) Option A domain separation so the
   signed_region carries a runtime-controlled domain tag that the
   caller cannot override.
2. **State machine implementation** in the runtime with explicit
   forbidden-transition failures.
3. **State machine+monotonic_seq binding to the signed region:** the
   runtime must embed the current state and a fresh `monotonic_seq`
   inside the bytes it signs, in a position that is not under the
   caller's control.
4. **Channel-proof mechanism** selected from §5 and bound into the
   signed region cryptographically (not as a free-form string).

The review does NOT itself require v0.2.1 to be modified; the
classification `DEDICATED_RUNTIME_ISSUANCE_REQUIRED` accepts the design
as the implementation baseline and acknowledges that another minimal
Hermes runtime modification is required before execution can be
authorized.

## Confirmation of zero execution

- Zero participant / model calls during review.
- Zero experiment execution.
- Zero live nonce generation.
- No Hermes modification.
- No premium evaluator engagement.
- v0.2.1 design preserved byte-identically (SHA-256 `df7f474b...`).
- All prior frozen artifacts preserved byte-identically.

STOP. Awaiting PI decision on (a) accepting the design as the
implementation baseline subject to the runtime additions per v0.2.1
§12, (b) requiring additional design changes, or (c) deeming the
experiment infeasible without hardware-rooted identity / out-of-band
verifier (in which case the closed classifications remain
`SESSION_EPHEMERAL_IDENTITY_ESTABLISHED` and
`RUNTIME_SESSION_IDENTITY_BOUND` but live-provenance-poc cannot
proceed).

# Live Provenance PoC v0.2 — ARTIFACT BINDING + LIVE-SESSION TRUST CHAIN (DESIGN ONLY)

**Status:** DESIGN ONLY — supersedes v0.1's missing root-of-trust. Not implemented, not executed.
**Date:** 2026-09-14
**Author:** Hermes (research-manager-mandate-2026-08-27)
**Predecessor (preserved byte-identically):** `architecture/experimental/live-provenance-poc/LIVE-PROVENANCE-POC-DESIGN-v0.1.md` (SHA-256 `a4f4836ac4ea0c5b62a643fec6843784f24cb9494e9a0cb5e60d36fcd329e785`).
**PI-accepted classifications feeding into this design:**
- `SESSION_EPHEMERAL_IDENTITY_ESTABLISHED` (commit `21b23de`)
- `RUNTIME_SESSION_IDENTITY_BOUND` (commit `3bad12e`)

## 0. Primary hypothesis

Evidence can demonstrate that the identity, session, governance acceptance, authorized action, and execution evidence entering an Agent Trust Envelope are bound to the same live Hermes session through an externally observed ephemeral session identity and an operator-generated freshness challenge.

## 1. Required trust chain (the chain the experiment tests)

```
externally observed Hermes runtime
       ↓ (captured [EXPERIMENTAL_PROVENANCE_STARTUP] line)
ephemeral per-session public identity (public_key_sha256)
       ↓ (operator generates after session creation)
fresh operator challenge (secrets.token_hex, outside Hermes)
       ↓ (injected via runtime interface)
session-bound COA acceptance (signed by session private key, binds challenge)
       ↓ (runtime signs action with session private key)
session-signed candidate action (binds session key + challenge + receipt fingerprint)
       ↓ (v0.2.2 GEL reused byte-identically; no session key required)
GEL evaluation result
       ↓ (runtime signs execution evidence with session private key)
session-bound execution evidence (binds session key + challenge + action fingerprint)
       ↓ (pipeline signs final DecisionRecord)
ATE DecisionRecord (binds complete provenance chain + all fingerprints)
```

## 2. Distinct provenance layers (do NOT collapse)

The design treats these as separate, each with its own signature and fingerprint:

| Layer | Artifact | Signing key | Purpose |
| -- | -- | -- | -- |
| runtime/session provenance | IdentityAttestation v0.2.1 | K_IDENTITY (runtime Ed25519) | Prove session belongs to one runtime instance |
| governance acceptance | COA AcceptanceReceipt v0.2.1 | K_TGE (TGE-fixture Ed25519) | Bind COA to session + challenge |
| authorization | CapabilityToken v0.2.1 | K_AUTHORITY (authority Ed25519) | Bind capability to session + challenge |
| action generation | SignedCandidateAction | K_IDENTITY (runtime Ed25519) | Bind action to session + challenge + receipt |
| execution evidence | SignedExecutedAction v0.2.1 | K_GEL (GEL-fixture Ed25519) | Bind GEL output to session + challenge + action |
| ATE decision | DecisionRecord v0.2.1 | K_PIPELINE (pipeline Ed25519) | Bind complete provenance chain |

**No single signature covers everything.** Each layer's signature binds its own subject to the prior fingerprint(s).

## 3. Root-of-trust requirements

The v0.2 design MUST capture this runtime evidence from the patched Hermes:

```
session_id           correlation metadata
public_key_b64       Eph25519 public key (the cryptographic session identity)
public_key_sha256    SHA-256 fingerprint of public_key_b64 (AUTHORITATIVE session identity)
pid                  process ID of the live Hermes runtime
proc_start_time      process creation time
code_sha             git commit of the installed Hermes
code_version         version string
started_at_utc       monotonic session-start timestamp
```

**The ephemeral public-key fingerprint, NOT the textual session_id, is the cryptographic session identity.** The session_id is correlation metadata only.

## 4. Freshness binding

The operator MUST generate a fresh unpredictable challenge:
- AFTER the live session has been created (i.e., after `[EXPERIMENTAL_PROVENANCE_STARTUP]` is observed)
- OUTSIDE the Hermes provenance primitive
- BEFORE COA acceptance

The same challenge (or its unambiguous fingerprint) MUST be bound into:

- COA acceptance receipt (signed region)
- SignedCandidateAction (signed region)
- SignedExecutedAction (signed region)
- DecisionRecord (signed region)

No artifact from a prior challenge MAY satisfy the current run.

## 5. Continuity chain (per-stage fingerprint binding)

Each stage binds to the prior stage's fingerprint via the canonical RFC 8785 JCS-strict payload:

```
session-start evidence  (operator-captured startup line; no signing)
   ↓ prior_fingerprint = SHA-256(canonicalize(startup_evidence))
freshness challenge  (operator-generated; no signing; recorded in operator-side evidence)
   ↓ prior_fingerprint = SHA-256(challenge_bytes)
COA receipt  (signed by K_TGE; signed_region includes:
                session_id, public_key_sha256, freshness_challenge,
                prior_fingerprint = SHA-256(challenge_bytes))
   ↓ prior_fingerprint = fingerprint_obj(coa_receipt)
candidate action  (signed by K_IDENTITY; signed_region includes:
                session_id, public_key_sha256, freshness_challenge,
                coa_receipt_fingerprint, prior_fingerprint = fingerprint_obj(coa_receipt))
   ↓ prior_fingerprint = signed_action_fingerprint
GEL result  (GEL v0.2.2 reused byte-identically; NO session key required)
   ↓ prior_fingerprint = signed_action_fingerprint (passed into SignedExecutedAction)
execution evidence  (signed by K_GEL; signed_region includes:
                original_action_hash, executed_action_struct,
                freshness_challenge, session_id, public_key_sha256,
                prior_fingerprint = signed_action_fingerprint)
   ↓ prior_fingerprint = executed_action_fingerprint
DecisionRecord  (signed by K_PIPELINE; signed_region includes:
                envelope_binding_hash, all component fingerprints,
                freshness_challenge, public_key_sha256,
                prior_fingerprint = executed_action_fingerprint)
```

**GEL itself does NOT require the session private key.** GEL's only input is the candidate action; the binding comes from the SignedCandidateAction's signature being verifiable and the SignedExecutedAction's `original_action_hash` matching.

## 6. LIVE_SESSION_PROVENANCE_BOUND predicate (frozen before implementation)

The experiment may claim `LIVE_SESSION_PROVENANCE_BOUND` only if ALL of the following hold:

1. Startup evidence was externally captured from a normal live Hermes lifecycle
   (the `[EXPERIMENTAL_PROVENANCE_STARTUP]` line, with `pid` matching the live
   process, `code_sha` matching the operator's expected install, `started_at_utc`
   within the operator's expected window).
2. The `public_key_sha256` from step 1 identifies the bound session.
   The fingerprint, not the session_id, is the authoritative identifier.
3. Freshness challenge was generated externally AFTER step 1 and BEFORE
   COA acceptance (timestamp ordering verified).
4. COA acceptance is signed (by K_TGE) and its signed region contains:
   - `session_id`
   - `public_key_sha256` from step 1
   - `freshness_challenge` from step 3
   - `prior_fingerprint = SHA-256(challenge_bytes)`
   The signature verifies under K_TGE public key.
5. CapabilityToken is signed (by K_AUTHORITY) and its signed region contains
   the same `session_id`, `public_key_sha256`, `freshness_challenge`,
   plus the COA receipt fingerprint.
6. SignedCandidateAction is signed (by K_IDENTITY = the session's runtime key)
   and its signed region contains:
   - `session_id`, `public_key_sha256`, `freshness_challenge`
   - `capability_id`, `receipt_id`, `identity_fingerprint`
   - `action_preimage_hash = SHA-256(canonicalize(action_struct))`
   - `prior_fingerprint = coa_receipt_fingerprint`
   - `envelope_nonce` (a per-invocation random hex, signed by the session key;
     no two signed candidate actions share the same `envelope_nonce`)
   The signature verifies under the `public_key_b64` from step 1.
7. Stage `BIND_GEL_INPUT_HASH` (within the v0.2.1 pipeline): the
   `action_preimage_hash` matches `SHA-256(canonicalize(action_struct))`.
8. GEL v0.2.2 evaluation (reused byte-identically, no session key required)
   returns a verdict (allow/block/redirect).
9. SignedExecutedAction is signed (by K_GEL) and its signed region contains:
   - `original_action_hash = signed_action_fingerprint`
   - `executed_action_struct` from GEL output
   - `session_id`, `public_key_sha256`, `freshness_challenge`
   - `prior_fingerprint = signed_action_fingerprint`
   The signature verifies under K_GEL public key.
10. DecisionRecord is signed (by K_PIPELINE) and its signed region contains:
    - `envelope_binding_hash`
    - all component fingerprints (identity, receipt, capability, action, executed_action)
    - `operation_mode`, `envelope_nonce`, `nonce_state_observed`
    - `replay_check_result`, `execution_boundary_reached`
    - `freshness_challenge` from step 3
    - `public_key_sha256` from step 1
    - `prior_fingerprint = executed_action_fingerprint`
    The signature verifies under K_PIPELINE public key.
11. The `envelope_nonce` in SignedCandidateAction is unique across this run
    (verified by the test runner observing the nonce before signing).
12. No replay / transplant condition is detected (Cases 2-5 below all produce DENY
    when this experiment's logic is applied).

**If ANY of these fails, the result MUST be `LIVE_SESSION_PROVENANCE_NOT_BOUND` with the specific failing condition recorded, or `MECHANISM_NOT_OBSERVABLE` if the runtime cannot produce the required artifacts.**

## 7. Frozen minimal diagnostic cases (5 cases)

### Case 1 — Valid same-session chain (positive case)

**Setup:**
- Live Hermes session created via normal CLI lifecycle.
- Startup evidence captured externally (operator reads
  `[EXPERIMENTAL_PROVENANCE_STARTUP]` line from stdout).
- Operator generates fresh challenge via `secrets.token_hex(16)` (128-bit CSPRNG,
  outside the primitive).
- Operator injects challenge via `inject_freshness_challenge(session_id, challenge)`.
- COA acceptance built with `session_id`, `public_key_sha256`, `freshness_challenge`,
  `prior_fingerprint = SHA-256(challenge_bytes)`, signed by K_TGE.
- CapabilityToken built similarly, signed by K_AUTHORITY.
- One model invocation by the live Hermes session to produce a candidate action
  (charter-consistent: NONE operation on action target).
- Candidate action wrapped in SignedCandidateAction, signed by the session's
  runtime key (K_IDENTITY = the patched `ephemeral_session_id_poc` private key).
- v0.2.2 GEL evaluated.
- SignedExecutedAction built, signed by K_GEL.
- DecisionRecord built, signed by K_PIPELINE.

**Expected:** `LIVE_SESSION_PROVENANCE_BOUND`. All 12 conditions of the predicate hold.

### Case 2 — COA transplant

**Setup:**
- Session A and Session B both created.
- Session A produces a valid COA acceptance.
- Session B's candidate action / capability / execution chain is built normally.
- At DecisionRecord construction, the operator-side test runner transplants
  Session A's COA receipt into Session B's chain.

**Expected:** `DENY_BINDING_MISMATCH` at pipeline stage 3 (BIND_RECEIPT)
because Session B's receipt was built with Session A's COA; either:
- session_id mismatch (Session A's session_id vs Session B's session_id)
- identity_fingerprint mismatch (Session A's identity_fingerprint vs Session B's)
- freshness_challenge mismatch (if challenges differ between A and B)
- coa_receipt_fingerprint cross-check fails

### Case 3 — Action transplant

**Setup:**
- Session A and Session B both created.
- Session B produces a valid SignedCandidateAction (signed by Session B's key).
- The operator-side test runner transplants Session B's SignedCandidateAction
  into Session A's envelope.

**Expected:** `DENY_BINDING_MISMATCH` at pipeline stage 5 (BIND_CANDIDATE_ACTION)
because Session A's runtime key cannot verify Session B's signature.

### Case 4 — Stale challenge / replay

**Setup:**
- Run Case 1 successfully (challenge C1).
- Generate a fresh challenge C2 outside Hermes.
- Build a new envelope for the SAME session but reuse C1's signed artifacts.

**Expected:** `DENY_BINDING_MISMATCH` at pipeline stage 3 (BIND_RECEIPT) because
COA receipt was signed with `freshness_challenge = C1` but the operator's
current challenge is C2. The receipt's signed region's `freshness_challenge`
does not match the operator's externally captured C2.

### Case 5 — Session termination / continuity break

**Setup:**
- Run Case 1's setup steps 1-5 (startup captured, challenge generated, COA +
  capability signed).
- Trigger Hermes session termination BEFORE the candidate action is signed
  (e.g., via `cli.new_session(silent=True)` which terminates the prior session).
- Build the candidate action attempt against the terminated session.

**Expected:** `sign_for_session(session_id, ...)` raises
`ValueError("session_terminated:...")`. Pipeline cannot proceed; final
disposition is `DENY` (no DecisionRecord produced because the chain cannot
complete).

## 8. Threat model (per PI directive — retained from v0.2 primitive)

The experiment may support resistance against:
- Fabricated session files
- Fabricated textual session IDs
- Forged gateway/session metadata
- Cross-session transplant
- Stale challenge replay
- Artifact substitution by a separate same-user process that does not possess the ephemeral private key

The experiment does NOT claim resistance against:
- Root/administrator compromise
- Arbitrary code execution inside Hermes
- Malicious Hermes binary
- Process-memory extraction/debugging
- Private-key theft from the live process

## 9. Model usage (kept to absolute minimum)

**Planned model/participant invocations: 1.**

- Case 1 positive case: ONE live Hermes participant session emits a candidate
  action in response to a single operator-supplied prompt. The prompt is
  constructed to elicit a charter-consistent action (NONE operation on action
  target) that the participant can emit deterministically without ambiguity.
- All other cases: deterministic local construction. The model is NOT invoked.
  Negative-control envelopes are constructed by the operator-side test runner
  by reading the in-process key from Case 1's session and constructing
  envelopes that violate one binding condition each.

**No premium evaluator. No second participant. No replication. No large
scoring matrix.**

## 10. Required design review gates (must all answer NO before execution)

| Gate | Question | Required answer |
| -- | -- | -- |
| G1 | Could the positive case pass with two different live sessions? | NO (because session_id and public_key_sha256 must agree, and continuity fingerprints must chain) |
| G2 | Could a stale COA receipt pass? | NO (because freshness_challenge mismatch fails stage 3) |
| G3 | Could a valid action from another session pass? | NO (because session-key signature fails verification at stage 5) |
| G4 | Could fabricated session_id or gateway metadata substitute for session-key proof? | NO (because the public-key fingerprint is the authoritative identity, not the session_id; a fabricated session_id without the corresponding private key fails all signed-region checks) |
| G5 | Could the test harness itself manufacture evidence that should have required possession of the session private key? | NO (because the harness only constructs envelopes; signatures require the in-process private key held by Hermes, and the harness can only access it via the documented `sign_for_session` interface which is rate-limited by the live session's state machine) |

If ANY of G1-G5 is YES, execution must remain unauthorized.

## 11. Relationship to prior work

**COA-E1/E2 (commit `0b82a80`):** exposed the failure that a governance
charter delivered only as ordinary conversational / in-context material is not
sufficient evidence that governance has been authoritatively established.
The COA-E2 closeout explicitly identified that future work must distinguish
charter content, provenance, issuer authority, delivery channel, participant
acceptance, cryptographic identity, and session binding.

**Ephemeral Session Identity v0.1 (commit `21b23de`):** established the
missing cryptographic session identity primitive — fresh Ed25519 keypair
per session, in-memory only, single-line startup emission.

**Runtime Lifecycle Integration v0.1 (commit `3bad12e`):** established that
the patched Hermes runtime normally exercises the ephemeral identity at
session start; external challenges can be injected; signatures verify
externally; cross-session separation holds; termination works via both
runtime interface and normal CLI lifecycle.

**ATE-PoC v0.2.1 (commit `93e14fa`, `c82f623`, `fa8fa37`):** established
downstream cryptographic composition and replay separation. Linear binding
chain from IdentityAttestation to DecisionRecord; VERIFY_ENVELOPE vs
AUTHORIZE_EXECUTION separation; one-time nonce consumption; replay detection.

**Live Provenance v0.2 (this design):** tests whether these pieces compose
into one demonstrable live-session trust chain that satisfies the
`LIVE_SESSION_PROVENANCE_BOUND` predicate under the defined threat model.

## 12. Scope

- **DESIGN ONLY.** No implementation. No execution. No participant invocation.
- **No modification to v0.1 or any prior frozen artifact.**
- **No further modification to Hermes.** The patched v0.21.2 install at commit
  `21b23de` is the runtime substrate.
- **No premium evaluator. No replication. No large test matrix.**
- **No execution until PI authorization is granted after design review.**

## 13. Files

- `architecture/experimental/live-provenance-poc/LIVE-PROVENANCE-POC-DESIGN-v0.2.md` (this document)

## 14. STOP-AT-DESIGN

Awaiting PI authorization to proceed to implementation and execution
(pending PI review of the design itself, including the G1-G5 review gates).

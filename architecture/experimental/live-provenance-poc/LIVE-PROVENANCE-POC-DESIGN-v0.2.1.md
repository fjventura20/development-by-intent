# Live Provenance PoC v0.2.1 — NON-SIGNING-ORACLE LIVE-SESSION TRUST CHAIN (DESIGN ONLY)

**Status:** DESIGN ONLY. Supersedes v0.2. Incorporates amendments A1–A6 from the v0.2 adversarial review (commit `445be56`). v0.2 preserved byte-identically.
**Date:** 2026-09-14
**Author:** Hermes (research-manager-mandate-2026-08-27)
**Predecessor (preserved byte-identically):** `architecture/experimental/live-provenance-poc/LIVE-PROVENANCE-POC-DESIGN-v0.2.md` (SHA-256 `fc9884f5cf5d22e6ae35066fb279852b42f1472065be4657d8f744422af665dd`).
**PI-accepted classifications feeding into this design:**
- `SESSION_EPHEMERAL_IDENTITY_ESTABLISHED` (commit `21b23de`)
- `RUNTIME_SESSION_IDENTITY_BOUND` (commit `3bad12e`)
**PI directive of 2026-09-14 (this revision):** accept amendments A1–A5 + add A6.

## 0. Primary hypothesis

Evidence can demonstrate that the identity, session, governance acceptance, authorized action, and execution evidence entering an Agent Trust Envelope are bound to the same live Hermes session through an externally observed ephemeral session identity, an operator-generated freshness challenge, and a runtime that issues **dedicated post-model-turn provenance artifacts** rather than a generic signing oracle.

## 1. Load-bearing constraint (drives the entire revision)

The v0.2 review identified that **possession of a session-key signature alone is insufficient to prove the corresponding model turn occurred.** A generic signing operation `sign_for_session(session_id, payload)` is a signing oracle: the harness could submit arbitrary bytes and obtain a K_IDENTITY signature that satisfies G5 without the model ever having accepted the COA or produced the action.

v0.2.1 therefore distinguishes:

```
POSSESSION OF SESSION KEY          (cryptographic property)
         ≠
SIGNATURE PRODUCED AS CONSEQUENCE OF REQUIRED MODEL TURN
                                   (semantic-causal property)
```

The SessionAcceptance and SignedCandidateAction artifacts MUST be issued only by dedicated runtime paths that observe an actual model response in the bound live session. Generic signing interfaces MUST NOT produce equivalent provenance evidence.

## 2. Two-turn causal sequence (positive case)

### Turn A — Governance acceptance

1. **Normal Hermes live session starts** via `cli.new_session(silent=True)` (or `/new` slash).
2. **Ephemeral session identity externally captured** by reading the
   `[EXPERIMENTAL_PROVENANCE_STARTUP]` line from stdout. Recorded:
   `session_id`, `public_key_b64`, `public_key_sha256`, `pid`,
   `proc_start_time`, `code_sha`, `code_version`, `started_at_utc`.
3. **Operator generates fresh challenge C** via
   `secrets.token_hex(16)` (128 bits CSPRNG, outside Hermes). Recorded
   in operator-side evidence with timestamp `T_C`.
4. **Runtime associates C with the pending acceptance turn.** The
   runtime maintains a per-session state machine
   `STATE_AWAITING_ACCEPTANCE_TURN`. The state machine records:
   `pending_challenge = C`,
   `pending_acceptance_turn_id = turn_A_id` (a runtime-monotonic
   counter incremented at this step).
5. **COA text is presented to the participant** in the prompt for
   turn A (along with C). The participant is asked to produce an
   explicit semantic acceptance response.
6. **Participant returns an explicit semantic acceptance response**
   through the normal Hermes model-response flow (i.e., the LLM
   provider was actually called, and the response text was received
   through the standard channel).
7. **Runtime receives the response via normal Hermes flow.**
   The runtime MUST be able to demonstrate that the response arrived
   through the model-response channel (not via operator-supplied bytes).
8. **Runtime validates the required acceptance content/challenge binding:**
   - response text MUST contain the operator challenge C (canonical
     representation, e.g., hex-encoded form)
   - response text MUST contain a runtime-injected internal nonce R
     (see §4 below)
   - response text MUST contain an explicit acceptance marker
     (operator-defined sentinel, e.g., `ACCEPT:`) followed by the COA text
   Validation failure → state machine transitions to
   `STATE_TURN_REJECTED_NO_PROVENANCE`. No SessionAcceptance issued.
9. **Runtime itself constructs canonical SessionAcceptance.**
   The runtime assembles the SessionAcceptance bytes from internal
   state, NOT from operator-supplied bytes. The operator MUST NOT be
   able to submit the bytes-to-be-signed for SessionAcceptance through
   any signing interface.
10. **Runtime signs SessionAcceptance with the session ephemeral key**
    (K_IDENTITY). Signature only happens if validation in step 8 passed.
11. **TGE validates/wraps that evidence and issues its governance receipt**
    (K_TGE-signed). The TGE receipt now binds the SessionAcceptance
    fingerprint inside its signed region.
12. State machine transitions to `STATE_ACCEPTANCE_ISSUED`. Records
    `session_acceptance_fingerprint`, `tge_receipt_fingerprint`,
    `monotonic_seq_at_acceptance`.

### Turn B — Governed action

13. **Same persistent session remains active.** State machine is
    `STATE_ACCEPTANCE_ISSUED` (NOT terminated, NOT rotated).
14. **Governed action request is sent** in the prompt for turn B. The
    prompt PARTIALLY references turn A's acceptance fingerprint so the
    participant's response is causally connected (not required for
    cryptographic binding but useful for semantic traceability).
15. **Participant produces candidate action** through the normal
    Hermes model-response flow.
16. **Runtime receives the candidate through normal model-response flow.**
17. **Runtime itself constructs canonical SignedCandidateAction**
    from the model's response, not from operator-supplied bytes.
    Operator MUST NOT be able to submit the bytes-to-be-signed for
    SignedCandidateAction through any signing interface.
18. **Runtime signs SignedCandidateAction with session ephemeral key**
    (K_IDENTITY).
19. SignedCandidateAction's signed region binds:
    - same `public_key_sha256` as turn A
    - same `freshness_challenge` C as turn A
    - `session_acceptance_fingerprint` (from turn A)
    - `tge_receipt_fingerprint` (from turn A)
    - `action_preimage_hash = SHA-256(canonicalize(action_struct))`
    - `prior_fingerprint = session_acceptance_fingerprint`
    - `envelope_nonce` (per-turn; unique)
    - `monotonic_seq_at_action` (> `monotonic_seq_at_acceptance`)
20. State machine transitions to `STATE_ACTION_ISSUED`.

### Continuation

21. v0.2.2 GEL evaluated byte-identically (no session key required).
22. **Runtime itself constructs canonical SignedExecutedAction** from
    GEL output, then signs with K_GEL (operator cannot inject
    arbitrary executed-action bytes).
23. **Runtime itself constructs canonical DecisionRecord**, then
    signs with K_PIPELINE (operator cannot inject arbitrary
    DecisionRecord bytes).
24. Session may now terminate via normal CLI lifecycle
    (`cli.new_session()` rotates it).

## 3. Dedicated runtime provenance APIs (NEW — replaces generic signing oracle)

These are the ONLY paths by which the four session-bound artifacts
may be issued. Generic `sign_for_session(session_id, payload_bytes)` is
preserved for primitive testing but its signatures do NOT satisfy the
LIVE_SESSION_PROVENANCE_BOUND predicate.

| API | Required precondition | Bytes supplied by | Issuer |
| -- | -- | -- | -- |
| `runtime_record_acceptance_turn(session_id, turn_id, model_response_bytes)` | `state == STATE_AWAITING_ACCEPTANCE_TURN`; `model_response_bytes` arrived via the model-response channel (not operator-supplied) | runtime (constructs SessionAcceptance from validated response + state) | runtime constructs SessionAcceptance, signs with K_IDENTITY |
| `runtime_record_action_turn(session_id, turn_id, model_response_bytes)` | `state == STATE_ACCEPTANCE_ISSUED`; `model_response_bytes` arrived via the model-response channel | runtime (constructs SignedCandidateAction from validated response + state) | runtime constructs SCA, signs with K_IDENTITY |
| `runtime_record_execution(session_id, gel_output)` | `state == STATE_ACTION_ISSUED`; `gel_output` came from v0.2.2 GEL | runtime (constructs SignedExecutedAction from GEL output + state) | runtime constructs SEA, signs with K_GEL |
| `runtime_record_decision(session_id, pipeline_outputs)` | `state == STATE_EXECUTION_ISSUED`; `pipeline_outputs` came from v0.2.1 pipeline | runtime (constructs DecisionRecord from pipeline output + state) | runtime constructs DecisionRecord, signs with K_PIPELINE |

**Critical property:** in each API, the runtime constructs the canonical
bytes-to-be-signed ITSELF. The operator supplies:
- the model response bytes (for acceptance and action turns) — but
  only after the runtime validates they arrived through the
  model-response channel
- the GEL output bytes (for execution) — but only after the runtime
  validates it came from GEL v0.2.2
- the pipeline output bytes (for decision) — but only after the
  runtime validates it came from the v0.2.1 pipeline

The operator cannot supply arbitrary bytes to be signed as a
SessionAcceptance or SignedCandidateAction.

## 4. Runtime nonce R (role clarified)

**R is a runtime-internal nonce** generated and held in process memory
only. Its purpose is **causal/freshness binding within the model turn,
NOT secret authentication against the harness.**

If R is included in a prompt sent by the operator, the harness
necessarily knows it. The PI directive explicitly accepts this:

> Do not rely on secrecy of R as the primary security property.

The load-bearing property is:

> The SessionAcceptance signature is emitted only after Hermes observes
> the model response in the bound live-session turn.

R may strengthen this by being **injected by the runtime into the turn
context** before the model response is observed (e.g., appended to the
prompt by the runtime after the operator submits the COA text). In that
case, R is unknown to the harness, and the runtime can validate the
response contains R before signing. R's role is then causal (the response
had to come through the runtime-mediated turn path), not secret
authentication.

If R cannot be injected internally, the experiment MAY proceed without
R as a cryptographic secret, provided the runtime still verifies that
the response arrived through the model-response channel (the design's
primary defense).

## 5. Model-response-channel verification

The runtime MUST be able to demonstrate that the response bytes it
received arrived through the normal model-response flow, not through
operator-supplied bytes. Mechanisms (not exhaustive — implementation
selects):

- **Channel tag:** the runtime tags every message in the session
  transcript with a source tag (`source: model_response` vs
  `source: operator_input`). SessionAcceptance and SignedCandidateAction
  are only constructed when the source tag is `model_response`.
- **Transcript binding:** the SessionAcceptance's signed region
  includes a hash of the previous transcript entries; the SignedCandidateAction
  includes a hash of the entries through turn B. The harness cannot
  fabricate the transcript without forging the entire chain.
- **Runtime-injected markers:** the runtime appends a unique runtime
  marker to the prompt (e.g., a runtime nonce R rendered as
  `[[HERMES_RUNTIME_MARKER:<hex>]]`); the response MUST contain the
  marker verbatim. The harness cannot predict the marker.

The v0.2.1 design DOES NOT require any specific mechanism, but the
selected mechanism MUST be described before implementation, and the
predicate condition 4b (below) MUST verify the mechanism's presence in
the artifact's signed region.

## 6. Strengthened LIVE_SESSION_PROVENANCE_BOUND predicate (15 conditions)

The experiment may claim `LIVE_SESSION_PROVENANCE_BOUND` only if ALL
of the following hold:

1. Startup evidence was externally captured from a normal live Hermes
   lifecycle (`[EXPERIMENTAL_PROVENANCE_STARTUP]` line, with `pid`
   matching the live process, `code_sha` matching the operator's
   expected install, `started_at_utc` within the operator's expected
   window).

2. The `public_key_sha256` from step 1 identifies the bound session
   (AUTHORITATIVE cryptographic identity).

3. Freshness challenge C was generated externally AFTER step 1 and
   BEFORE turn A (timestamp ordering verified).

4. **Turn A: SessionAcceptance** is present in the session evidence
   and satisfies ALL of:
   - 4a. Signed by K_IDENTITY (signature verifies under
     `public_key_b64` from step 1).
   - 4b. **Provenance type tag** in the signed region identifies it as
     issued by the dedicated post-model-turn acceptance path (e.g.,
     `provenance_type = "RUNTIME_ACCEPTANCE_TURN"`). Generic
     `sign_for_session()` output is NOT a valid issuer.
   - 4c. Signed region contains `session_id`, `public_key_sha256`,
     `freshness_challenge` (equal to C), `coa_receipt_fingerprint`
     (from step 5), `acceptance_response_hash` (SHA-256 of the model
     response), and `acceptance_response_channel_proof` (proof that
     the response arrived through the model-response channel per §5).
   - 4d. `monotonic_seq` is the runtime-internal sequence number
     recorded at acceptance issuance.
   - 4e. State machine at acceptance time was `STATE_AWAITING_ACCEPTANCE_TURN`.

5. **TGE governance receipt** is present and satisfies:
   - 5a. Signed by K_TGE (signature verifies under K_TGE public key).
   - 5b. Signed region contains `session_id`, `public_key_sha256`,
     `freshness_challenge` (equal to C), `session_acceptance_fingerprint`
     (from step 4), `prior_fingerprint = SHA-256(C)`.
   - 5c. Receipt signature timestamp `T_receipt` is strictly greater
     than operator challenge timestamp `T_C` (A5).

6. **CapabilityToken** is present and satisfies:
   - 6a. Signed by K_AUTHORITY (signature verifies under K_AUTHORITY
     public key).
   - 6b. Signed region contains the same `session_id`,
     `public_key_sha256`, `freshness_challenge` (C), plus the
     `tge_receipt_fingerprint` (from step 5).

7. **Turn B: SignedCandidateAction** is present and satisfies ALL of:
   - 7a. Signed by K_IDENTITY (signature verifies under
     `public_key_b64` from step 1).
   - 7b. **Provenance type tag** in the signed region identifies it
     as issued by the dedicated post-model-turn action path (e.g.,
     `provenance_type = "RUNTIME_ACTION_TURN"`). Generic
     `sign_for_session()` output is NOT a valid issuer.
   - 7c. Signed region contains `session_id`, `public_key_sha256`,
     `freshness_challenge` (C), `session_acceptance_fingerprint` (step 4),
     `tge_receipt_fingerprint` (step 5), `capability_id` (from step 6),
     `receipt_id`, `identity_fingerprint`, `action_preimage_hash =
     SHA-256(canonicalize(action_struct))`, `prior_fingerprint =
     session_acceptance_fingerprint`, `envelope_nonce`, `monotonic_seq`
     (strictly greater than `monotonic_seq` from step 4d), and
     `action_response_channel_proof` (proof that the candidate arrived
     through the model-response channel).
   - 7d. State machine at action time was `STATE_ACCEPTANCE_ISSUED`
     (turn A must have completed; turn B cannot precede turn A).

8. `BIND_GEL_INPUT_HASH` (within v0.2.1 pipeline): `action_preimage_hash`
   from 7c matches `SHA-256(canonicalize(action_struct))`.

9. GEL v0.2.2 evaluation (reused byte-identically, no session key
   required) returns a verdict.

10. **SignedExecutedAction** is present and satisfies:
    - 10a. Signed by K_GEL (signature verifies under K_GEL public key).
    - 10b. **Provenance type tag** identifies it as issued by the
      dedicated post-GEL runtime path (e.g., `provenance_type =
      "RUNTIME_EXECUTION"`). Direct K_GEL signing without runtime
      wrapping is NOT a valid issuer.
    - 10c. Signed region contains `original_action_hash` (matching
      `signed_action_fingerprint` from step 7), `executed_action_struct`
      (from GEL), `session_id`, `public_key_sha256`,
      `freshness_challenge` (C), `prior_fingerprint =
      signed_action_fingerprint`.
    - 10d. State machine at execution time was `STATE_ACTION_ISSUED`.

11. **DecisionRecord** is present and satisfies:
    - 11a. Signed by K_PIPELINE (signature verifies under K_PIPELINE
      public key).
    - 11b. **Provenance type tag** identifies it as issued by the
      dedicated post-pipeline runtime path (e.g., `provenance_type =
      "RUNTIME_DECISION"`). Direct K_PIPELINE signing without runtime
      wrapping is NOT a valid issuer.
    - 11c. Signed region contains `envelope_binding_hash`, all
      component fingerprints (identity, receipt, capability, action,
      executed_action), `operation_mode`, `envelope_nonce`,
      `nonce_state_observed`, `replay_check_result`,
      `execution_boundary_reached`, `freshness_challenge` (C),
      `public_key_sha256`, `prior_fingerprint = executed_action_fingerprint`,
      `monotonic_seq` (strictly greater than step 7c's
      `monotonic_seq`), and `decision_response_channel_proof`
      (proof that the pipeline output arrived through the pipeline
      channel).
    - 11d. State machine at decision time was `STATE_EXECUTION_ISSUED`.

12. **Causal monotonicity:**
    - `monotonic_seq(acceptance)` < `monotonic_seq(action)` <
      `monotonic_seq(execution)` < `monotonic_seq(decision)`.
    - These are runtime-internal monotonic counters recorded in each
      artifact's signed region. They are NOT timestamps (which can be
      forged) but runtime-internal sequence numbers that increment
      only on valid state-machine transitions.

13. **No replay/transplant condition** detected (Cases 2–6 below all
    produce DENY).

14. **Harness-construction impossibility proof:** the artifact
    evidence file MUST include an explicit enumeration of:
    - all keys available to the harness (K_IDENTITY, K_TGE,
      K_AUTHORITY, K_GEL, K_PIPELINE, fixture keys, test-runner
      secrets)
    - all artifacts the harness could manufacture with those keys
    - all artifacts the harness CANNOT manufacture because the
      dedicated runtime path observed an actual model response in
      the bound session
    For `LIVE_SESSION_PROVENANCE_BOUND`, this proof MUST show that
    the harness cannot manufacture SessionAcceptance (step 4) or
    SignedCandidateAction (step 7) without invoking the live session's
    model-response channel.

15. **Both events occur before session termination or rotation:**
    state machine has NOT transitioned to `STATE_TERMINATED` or
    `STATE_ROTATED` between acceptance issuance and decision
    issuance.

If ANY condition fails, the result MUST be
`LIVE_SESSION_PROVENANCE_NOT_BOUND` with the specific failing condition
recorded.

## 7. Minimal diagnostic cases (6 cases)

The v0.2 set is preserved and one case is added to test the new
dedicated-path provenance type tag.

### Case 1 — Valid same-session two-turn chain (positive case)

**Setup:** as §2 above.

**Expected:** `LIVE_SESSION_PROVENANCE_BOUND`. All 15 conditions hold.

### Case 2 — COA transplant (transplant from prior Case 1 run)

**Setup:**
- Case 1 ran successfully with session S1, challenge C1, fingerprint F1.
- New session S2 created with challenge C2.
- Operator attempts to transplant S1's TGE receipt into S2's envelope.

**Expected:** `DENY_BINDING_MISMATCH` at step 5b (TGE receipt's
`public_key_sha256 = S1` vs operator-captured `public_key_sha256 = S2`)
OR at step 5b's `session_acceptance_fingerprint` mismatch
(S1's fingerprint ≠ S2's acceptance fingerprint).

### Case 3 — Action transplant

**Setup:**
- Sessions S1, S2 created.
- S2 produces valid SignedCandidateAction.
- Operator transplants S2's SCA into S1's envelope.

**Expected:** `DENY_BINDING_MISMATCH` at step 7a (SCA signed by
S2's K_IDENTITY, but pipeline requires verification under S1's
`public_key_b64`).

### Case 4 — Stale challenge / replay

**Setup:** v0.2's Case 4 (harness reuses turn A artifacts from C1
challenge into a new envelope for C2 challenge).

**Expected:** `DENY_BINDING_MISMATCH` at step 4c (SessionAcceptance's
`freshness_challenge = C1` ≠ operator-captured C2).

### Case 5 — Session termination / continuity break

**Setup:**
- Run Case 1's setup steps 1-12 (startup captured, challenge
  generated, turn A completed, SessionAcceptance issued).
- Trigger Hermes session termination BEFORE turn B
  (`cli.new_session(silent=True)` which terminates S1).
- Attempt turn B against the terminated session.

**Expected:** `DENY` at the runtime's state machine:
`runtime_record_action_turn(S1, ...)` requires
`state == STATE_ACCEPTANCE_ISSUED`, but `state == STATE_TERMINATED`.
No SignedCandidateAction issued.

### Case 6 — Generic signing-oracle bypass attempt (NEW)

**Setup:**
- Sessions S1, S2 created.
- Operator obtains S1's `public_key_b64` from startup evidence.
- Operator calls generic `sign_for_session(S1, b"<harness-crafted
  SessionAcceptance bytes>")` to obtain a K_IDENTITY signature on
  harness-supplied bytes.
- Operator also calls generic `sign_for_session(S1, b"<harness-crafted
  SignedCandidateAction bytes>")` to obtain a K_IDENTITY signature on
  harness-supplied action bytes.
- Operator builds a complete envelope using these harness-signed
  artifacts and tries to satisfy the predicate.

**Expected:** `DENY_BINDING_MISMATCH` at:
- step 4b (SessionAcceptance's `provenance_type` ≠
  `RUNTIME_ACCEPTANCE_TURN`; the signed_region does not carry the
  runtime-internal provenance tag)
- step 4c (SessionAcceptance's signed_region does not contain a valid
  `acceptance_response_channel_proof` because no model response was
  observed)
- step 7b (SCA's `provenance_type` ≠ `RUNTIME_ACTION_TURN`)
- step 7c (SCA's signed_region does not contain a valid
  `action_response_channel_proof`)

This case is the NEW required proof that the design is not bypassable
via the generic signing oracle.

## 8. Threat model (retained from v0.2)

The experiment may support resistance against:
- Fabricated session files
- Fabricated textual session IDs
- Forged gateway/session metadata
- Cross-session transplant
- Stale challenge replay
- Artifact substitution by a separate same-user process that does not possess the ephemeral private key
- **Generic signing-oracle bypass attempts** (Case 6 — NEW)

The experiment does NOT claim resistance against:
- Root/administrator compromise
- Arbitrary code execution inside Hermes
- Malicious Hermes binary
- Process-memory extraction/debugging
- Private-key theft from the live process

## 9. Model usage (updated)

**Planned model/participant invocations: 2** (in the same persistent
session).

- **Turn A (acceptance):** participant produces explicit acceptance
  response containing operator challenge C and runtime-injected marker
  R (if used). Output captured through normal model-response channel.
- **Turn B (governed action):** participant produces candidate action
  in response to action prompt. Output captured through normal
  model-response channel.
- All other cases: deterministic local construction by the test runner.
  No model invocation.

No premium evaluator. No second participant. No replication. No large
scoring matrix.

## 10. Required design review gates (before implementation)

All must answer NO:

- G1 — Could the positive case pass with two different live sessions?
- G2 — Could a stale SessionAcceptance or TGE receipt pass?
- G3 — Could a valid action from another session pass?
- G4 — Could fabricated session_id or gateway metadata substitute for session-key proof?
- **G5 (NEW framing)** — Could the harness satisfy
  `LIVE_SESSION_PROVENANCE_BOUND` by using Hermes as a cryptographic
  signing oracle without the participant actually accepting the COA
  and producing the governed action?
- **G6 (NEW)** — Could the harness manufacture SessionAcceptance or
  SignedCandidateAction through the generic `sign_for_session()`
  interface and satisfy the predicate?

If ANY is YES, execution must remain unauthorized.

## 11. Treatment of A1–A6

| Amendment | Status | Where in v0.2.1 |
| -- | -- | -- |
| **A1** SessionAcceptance artifact (K_IDENTITY-signed) | ACCEPTED | §3 (dedicated API), §6 condition 4 |
| **A2** Separate TGE receipt from live-session acceptance | ACCEPTED | §2 steps 11–12 (TGE wraps after acceptance), §6 conditions 4 vs 5 |
| **A3** Runtime-injected nonce R | ACCEPTED with clarification | §4 (R is causal, not secret); R injected by runtime into prompt if used |
| **A4** Two model calls in same session | ACCEPTED | §2 (turns A and B in same persistent session), §9 |
| **A5** Explicit causal/time ordering | ACCEPTED | §6 condition 5c (timestamp), §6 condition 12 (monotonic sequence numbers — primary) |
| **A6** Eliminate signing-oracle false PASS | ACCEPTED | §3 (dedicated APIs), §6 conditions 4b, 7b, 10b, 11b (provenance_type tags), §7 Case 6, §10 G5/G6 |

## 12. Required runtime additions (FROZEN before implementation)

These additions to the patched Hermes v0.21.2 runtime are required for
v0.2.1. They are NOT implemented in this design phase.

- Runtime-internal monotonic sequence counter per session
  (`runtime_seq[session_id] += 1` at each state transition).
- Runtime state machine: `INIT → STATE_AWAITING_ACCEPTANCE_TURN →
  STATE_ACCEPTANCE_ISSUED → STATE_ACTION_ISSUED →
  STATE_EXECUTION_ISSUED → STATE_DECISION_ISSUED → STATE_TERMINATED`.
- Runtime-injected nonce R (`runtime_nonce(session_id) -> bytes`).
- Dedicated provenance API:
  `runtime_record_acceptance_turn(session_id, turn_id, model_response_bytes)`.
- Dedicated provenance API:
  `runtime_record_action_turn(session_id, turn_id, model_response_bytes)`.
- Dedicated provenance API:
  `runtime_record_execution(session_id, gel_output)`.
- Dedicated provenance API:
  `runtime_record_decision(session_id, pipeline_outputs)`.
- Model-response-channel verification mechanism (selected per §5).
- Provenance-type tags in each artifact's signed region.
- Generic `sign_for_session()` retained for primitive testing;
  v0.2.1 predicate requires provenance-type tags that generic signing
  cannot produce.

**NOTE:** the v0.2.1 design acknowledges that runtime-side additions
MAY be required. PI authorization to modify Hermes further is a
separate decision and is NOT granted by acceptance of v0.2.1 alone.

## 13. Relationship to prior work

(See v0.2 §11 for full lineage.)

**v0.2.1 specifically extends:**
- v0.2 §6 predicate (now 15 conditions; was 12)
- v0.2 §7 cases (now 6 cases; was 5; added Case 6 for signing-oracle bypass)
- v0.2 §9 model usage (now 2 calls; was 1)
- v0.2 §10 review gates (now G1-G6; was G1-G5; added G6 signing-oracle gate)

## 14. Scope

- **DESIGN ONLY.** No implementation. No execution. No participant
  invocation. No live experimental nonces generated.
- **No modification to v0.1, v0.2, or any prior frozen artifact.**
- **No further modification to Hermes yet.** v0.21.2 install at commit
  `21b23de` is the runtime substrate for the design's reference; if
  v0.2.1 requires runtime additions per §12, those are a separate PI
  authorization.
- **No premium evaluator. No replication. No large test matrix.**
- **No execution until PI authorization is granted after design
  review** (this artifact itself requires another adversarial review
  per the PI directive).

## 15. Files

- `architecture/experimental/live-provenance-poc/LIVE-PROVENANCE-POC-DESIGN-v0.2.1.md` (this document)

## 16. STOP-AT-DESIGN

Awaiting:
1. PI review of v0.2.1 (including G1-G6 review gates).
2. PI authorization to modify Hermes further if runtime additions
   per §12 are required.
3. Subsequent adversarial review (per PI directive) before any
   implementation or execution.

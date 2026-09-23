# Adversarial Design Review — LIVE-PROVENANCE-POC v0.2

**Status:** ADVERSARIAL REVIEW (DESIGN ONLY). Does NOT modify v0.2.
**Date:** 2026-09-14
**Reviewer:** Hermes (research-manager-mandate-2026-08-27)
**Subject:** `architecture/experimental/live-provenance-poc/LIVE-PROVENANCE-POC-DESIGN-v0.2.md` (SHA-256 `fc9884f5cf5d22e6ae35066fb279852b42f1472065be4657d8f744422af665dd`)
**Predecessor review (preserved byte-identically):** `REVIEW-LIVE-PROVENANCE-POC-DESIGN-v0.1.md` (SHA-256 `4a855be1c12c025fb2a6b50b085a0ba8d7fe327859b35b4dfe9e5d0aae28d9f2`)

## Controlling review question

> Could v0.2 produce `LIVE_SESSION_PROVENANCE_BOUND` without proving that
> the same live Hermes session both accepted the governance conditions
> AND produced the governed action?

**ANSWER:** YES, as currently written. The COA acceptance is signed by
K_TGE (a fixture-controlled key the harness possesses); the design does
NOT require any session-key-signed artifact proving live-session
acceptance of the COA. The harness can manufacture valid-looking COA
acceptance without the live session ever participating.

**This is a load-bearing finding.** See G5 below.

## Gate-by-gate disposition

### G1 — Same-session substitution

**Question:** Could the positive case pass if governance acceptance
occurred in Session A but the governed action was produced in Session B?

**Constructing the false-positive chain:**

1. Session A startup → `public_key_sha256_A` captured by operator.
2. Session A operator generates challenge C_A, signs COA receipt with
   K_TGE (session_id=A, public_key_sha256_A, freshness_challenge=C_A).
3. Session B startup → `public_key_sha256_B` captured by operator.
4. Session B operator generates challenge C_B, builds COA receipt with
   K_TGE (session_id=B, public_key_sha256_B, freshness_challenge=C_B).
5. Operator constructs hybrid envelope: Session A's COA receipt +
   Session B's SignedCandidateAction + Session B's CapabilityToken
   (resigned with public_key_sha256_B in its signed region).
6. Operator runs the v0.2.1 pipeline.

**What each predicate condition does:**
- Condition 4: COA receipt signed by K_TGE — verifies under K_TGE public
  key (the harness holds K_TGE). PASS.
- Condition 5: CapabilityToken signed by K_AUTHORITY — verifies. PASS
  (harness holds K_AUTHORITY).
- Condition 6: SignedCandidateAction signed by K_IDENTITY. The
  SignedCandidateAction in the hybrid envelope was signed by Session B's
  runtime key. Condition 6 requires signature verification under
  `public_key_b64` from step 1 — which is Session A's key. **Session B's
  signature does NOT verify under Session A's key.** FAIL.

**Disposition: PASS.** The cryptographic check necessarily rejects this
because condition 6 binds the SCA signature to the same public key as the
COA receipt's `public_key_sha256`. A hybrid envelope fails the signature
check on the SCA.

### G2 — Stale governance acceptance

**Question:** Could a valid COA acceptance from an earlier
challenge/session/run satisfy the current chain?

**Constructing the false-positive chain:**

1. Run Case 1 successfully with challenge C1. All artifacts recorded.
2. Operator generates fresh challenge C2 outside Hermes.
3. Operator attempts to reuse the COA receipt from step 1 (which was
   signed over C1 inside its signed region) into a new envelope for the
   same session.

**What each predicate condition does:**
- Condition 4: COA receipt's signed_region.freshness_challenge = C1. The
  operator's current challenge is C2. The condition says the receipt's
  `freshness_challenge` must equal the operator's externally captured
  challenge. **Mismatch → FAIL.**

**The freshness_challenge IS inside the K_TGE-signed region.** The
harness CAN re-sign the receipt with C2 inside (because the harness has
K_TGE) and pass condition 4. **However**, the operator-side evidence
records that the operator generated C2 at a specific timestamp T_C2, and
the receipt's signed_region.freshness_challenge must equal C2. The
harness re-signing changes the receipt's content but the receipt is
fresh at construction time. The condition as written only checks
equality, not temporal ordering.

**To strengthen:** condition 4 should also require that the receipt was
constructed AFTER the operator's challenge timestamp T_C2. This requires
either a witness counter inside Hermes or an operator-side chronological
log. The current design has neither.

**Disposition: PASS (with strengthening recommendation).** The current
condition 4 detects stale-receipt reuse when challenges differ. The
harness with K_TGE can re-sign a receipt with a new challenge, but this
is a freshness-of-receipt-construction issue, not a freshness-of-acceptance
issue (which is what G5 addresses). **Recorded as
R2-STALENESS-DETECTABILITY-WEAKNESS, not a gate failure.**

### G3 — Foreign action

**Question:** Could a valid action produced by another live Hermes
session be transplanted into the positive chain?

**Constructing the false-positive chain:**

1. Session A and Session B both created.
2. Session B produces a valid SCA (signed by B's runtime key).
3. Operator transplants Session B's SCA into Session A's envelope.

**What each predicate condition does:**
- Condition 6: SCA signature must verify under
  `public_key_b64 from step 1` (Session A's key). **Session B's
  signature does NOT verify under Session A's key.** FAIL.

**Disposition: PASS.** The session-key signature binding prevents this.

### G4 — Metadata fabrication

**Question:** Could fabricated session_id, gateway_state.json, session
database content, PID metadata, or other operator-visible but forgeable
metadata substitute for possession of the ephemeral session private key?

**Analysis:**

- `session_id` itself is forgeable (24-32 bits randomness, no
  cryptographic binding per the Hermes capability audit at commit
  `a23addb`). It is correlation metadata only.
- `gateway_state.json`, `pid`, `code_sha`, `code_version` are
  forgeable by a same-user process.
- `public_key_sha256` is only verifiable by demonstrating possession
  of the corresponding private key. The cryptographic identity is the
  fingerprint, not the metadata.

**What each predicate condition does:**
- Condition 1: requires externally captured startup evidence with
  `pid` matching the live process. The harness is a separate process
  from the live Hermes session, so the `pid` of the operator-side test
  runner does not match the live session's `pid`. The harness CANNOT
  forge this condition without launching a separate Hermes process and
  capturing ITS startup evidence — but then the harness would need to
  actually invoke the model in that process (Case 1 only model call)
  and use the in-process key. This requires the harness to genuinely
  exercise the live session.
- Condition 6: requires signature verification under `public_key_b64`
  from step 1. The harness cannot forge a valid signature without the
  in-process private key.

**Disposition: PASS.** Textual/session metadata is correlation
evidence; cryptographic possession remains authoritative. The design
explicitly designates `public_key_sha256` as the AUTHORITATIVE session
identity (not the session_id), which is correct.

### G5 — Harness manufacturing

**Question:** Could the test harness itself manufacture every artifact
necessary for `LIVE_SESSION_PROVENANCE_BOUND` without the live Hermes
session performing a required acceptance or action step?

**Keys available to the harness:**

| Key | Available to harness? | Why |
| -- | -- | -- |
| K_IDENTITY (runtime Eph25519) | **NO direct access.** | Generated in-process by `ephemeral_session_id_poc.setup_for_session`; not serialized to disk; not exposed via any out-of-process channel. Harness can ONLY invoke `sign_for_session(session_id, payload_bytes)` via the live runtime interface, which is rate-limited by the live session's state machine (one session per session_id; terminated sessions cannot sign). |
| K_TGE (TGE-fixture Ed25519) | **YES (fixture-controlled).** | This is a fixture key for the ATE-PoC v0.2.1 implementation; the harness can sign arbitrary content under it. |
| K_AUTHORITY (authority Ed25519) | **YES (fixture-controlled).** | Same as above. |
| K_GEL (GEL-fixture Ed25519) | **YES (fixture-controlled).** | Same as above. |
| K_PIPELINE (pipeline Ed25519) | **YES (fixture-controlled).** | Same as above. |
| Operator-generated challenge | **YES (operator-side).** | `secrets.token_hex(16)` in the harness's Python script. |

**Constructing the false-positive chain (THE LOAD-BEARING FALSE PASS):**

1. Operator starts live Hermes session. Captures startup evidence.
   Gets `public_key_sha256_BOUND` and corresponding `public_key_b64_BOUND`.
2. Operator generates fresh challenge C = `secrets.token_hex(16)`.
3. Operator **manufactures** a COA receipt without session participation:
   - Constructs receipt content: `session_id, public_key_sha256_BOUND,
     freshness_challenge=C, prior_fingerprint=SHA-256(C_bytes)`.
   - Signs with K_TGE (harness has K_TGE).
   - The live session NEVER participated in any "acceptance" of this COA.
4. Operator **manufactures** a CapabilityToken with K_AUTHORITY (harness has K_AUTHORITY).
5. Operator invokes `sign_for_session(session_id, payload)` on the live
   session to obtain a SessionKey-signed SCA (this step IS genuine — the
   live session participates because it owns the key).
6. Operator evaluates v0.2.2 GEL (deterministic; no session key
   required).
7. Operator **manufactures** SignedExecutedAction with K_GEL (harness has K_GEL).
8. Operator **manufactures** DecisionRecord with K_PIPELINE (harness has K_PIPELINE).

**Predicate evaluation:**
- Condition 1: PASS (startup evidence genuinely captured from live lifecycle).
- Condition 2: PASS (`public_key_sha256_BOUND` from #1).
- Condition 3: PASS (challenge C generated externally after #1).
- **Condition 4: PASS** (COA receipt signature verifies under K_TGE public
  key. **BUT the live session never accepted the COA** — the harness
  manufactured the receipt using a fixture-controlled key.)
- **Condition 5: PASS** (CapabilityToken signature verifies under
  K_AUTHORITY. The harness manufactured this too.)
- **Condition 6: PASS** (SCA signature verifies under `public_key_b64_BOUND`
  because the harness invoked the live session's `sign_for_session` API.
  This part IS genuine.)
- Conditions 7-12: PASS (deterministic; harness controls K_GEL, K_PIPELINE).

**RESULT: `LIVE_SESSION_PROVENANCE_BOUND` would be claimed, but the live
session never actually accepted the COA.** The harness manufactured the
governance acceptance using K_TGE alone.

**This is exactly the false-PASS mechanism the PI flagged in the load-
bearing issue.** The COA receipt is K_TGE-signed, not session-key-signed.
K_TGE is fixture-controlled. The harness can manufacture acceptance
evidence without the live session participating.

**Disposition: FAIL.** The harness can manufacture the governance
acceptance step without the live session performing a required
acceptance.

## Load-bearing issue: missing session-key-signed acceptance artifact

**The design requires a NEW ARTIFACT that the harness cannot
manufacture without live-session participation.** Specifically, an
artifact that:
- is signed by the session's runtime ephemeral key (K_IDENTITY), and
- binds the live session's `public_key_sha256`, the current
  `freshness_challenge`, the COA receipt's fingerprint, AND
- contains (or binds to) evidence that the live session semantically
  accepted the COA.

**Candidate artifact name:** `SessionAcceptance` (or similar).

**Required content of SessionAcceptance's signed region:**
- `session_id` from startup evidence
- `public_key_sha256` from startup evidence
- `freshness_challenge` from operator
- `coa_receipt_fingerprint` (SHA-256 of canonicalized COA receipt)
- `acceptance_text_hash` (SHA-256 of canonicalized acceptance content)
- `monotonic_seq` (per-session counter)
- `prior_fingerprint = coa_receipt_fingerprint`

**Required property:** the `acceptance_text` (or `acceptance_text_hash`)
MUST be derivable only from the live session's runtime response to the
COA prompt, not from operator-supplied text alone.

**Two architectural options to achieve this:**

### Option A — Runtime-held nonce challenge

The runtime, on `accept_coa(session_id, coa_receipt_id)` API call,
internally:
1. Generates a fresh runtime nonce R (`secrets.token_bytes(16)`),
   stored in-process only. Operator NEVER sees R.
2. Returns R to the caller (operator/harness).
3. The operator constructs the COA acceptance prompt containing R and
   submits it to the live session.
4. The live session's runtime, on receiving the model's response,
   verifies that R appears in the response text. If not, refuse.
5. If R is present, the runtime constructs SessionAcceptance with
   `acceptance_text_hash = SHA-256(response_text)`, signs with the
   session's ephemeral key, and returns it.
6. The harness cannot forge SessionAcceptance because R is unknown to
   the harness.

**Pros:** R never leaves the runtime (matches the operator-generated-
outside-Hermes property of the freshness challenge, but R is for the
acceptance step specifically).
**Cons:** requires two model calls (or one call that includes the
acceptance text in the response), and adds runtime-side verification.

### Option B — Model-call transcript binding

The runtime records every model invocation's prompt+response into a
per-session transcript (in-memory only). SessionAcceptance's
`acceptance_text_hash` is bound to the LAST model call's response text.
The pipeline verifier requires that the `acceptance_text_hash` matches
the in-process transcript's last entry.

**Pros:** simpler; reuses existing transcript logging.
**Cons:** relies on transcript integrity (an attacker that controls
the runtime could fabricate the transcript — but that would be
arbitrary code execution in Hermes, out of scope per threat model).

**Both options require the design to add SessionAcceptance to the
predicate** (condition 4 should be split into condition 4a — K_TGE-
signed receipt — and condition 4b — K_IDENTITY-signed SessionAcceptance
bound to the receipt).

## Required participant-call semantics

**The single planned model call cannot serve both acceptance and action.**

Per the PI directive's preferred sequence:

```
operator challenge
→ live Hermes session receives COA text/challenge
→ participant produces explicit acceptance
→ Hermes runtime cryptographically signs/certifies that acceptance
   using the session ephemeral key
→ participant produces governed action in the SAME persistent session
→ Hermes runtime cryptographically signs the candidate-action evidence
   using that same session key
```

The two cryptographically distinct events (acceptance signature +
action signature) require two model interactions in the same
persistent session:

- **Model call A (acceptance):** participant reads COA text + challenge
  + runtime nonce R, emits response text containing both the challenge
  and R (in some operator-specified format).
- **Runtime-side processing of call A:** runtime verifies R is present in
  response, constructs SessionAcceptance, signs with session key.
- **Model call B (action):** participant produces candidate action in
  response to operator-supplied action prompt, in the SAME persistent
  session.
- **Runtime-side processing of call B:** runtime wraps action in SCA,
  signs with session key.

**Decision:** **2 model calls required, in the same persistent session.**
The "1 call" target is NOT preserved at the expense of validity.

## Execution evidence review (condition 9)

**Question:** SignedExecutedAction is signed by K_GEL, not the Hermes
session key. Is its binding to `original_action_hash`, `session public-
key fingerprint`, `freshness_challenge`, and `prior fingerprint`
sufficient to establish that the executed action derives from the
authenticated live-session candidate?

**Analysis:**

- `original_action_hash = signed_action_fingerprint` — this is the
  fingerprint of the SCA, which is K_IDENTITY-signed. The GEL key alone
  cannot produce a SignedExecutedAction whose `original_action_hash`
  matches the SCA fingerprint UNLESS the SCA actually exists and was
  observed.
- `public_key_sha256` is bound inside the K_GEL-signed region. GEL
  itself doesn't know the session key, but the pipeline VERIFIER (the
  test runner) checks that the SCA's signature verifies under the
  public_key_b64 corresponding to this public_key_sha256, and that the
  SCA's `public_key_sha256` field equals this value.
- The cryptographic chain is: SCA signature verifies under
  public_key_b64 (operator-captured) AND SCA's
  `original_action_hash` matches SEA's `original_action_hash` AND
  SEA's `public_key_sha256` matches SCA's `public_key_sha256`.

**Result:** the binding is sufficient because the chain is:
operator-captured public_key_b64 → K_IDENTITY-verifies SCA → SCA's
fingerprint = SEA's `original_action_hash` → K_GEL-signed SEA binds
the same fingerprint. The GEL key is fixture-controlled, but
constructing a valid SEA requires the SCA to already exist and verify,
which requires the live session's runtime signature.

**Disposition: condition 9 is sufficient as written.** No change needed.

## Final classification

**REVISION_REQUIRED.**

**Reason:** G5 fails because the harness can manufacture governance
acceptance using fixture-controlled K_TGE without the live session
participating. The design must add a session-key-signed SessionAcceptance
artifact (bound to runtime-held nonce R or to in-process model
transcript) to the predicate, and require 2 model calls in the same
persistent session (one for acceptance, one for governed action).

## Required design amendments (do NOT execute; design review only)

These are listed for completeness; the PI decides whether to accept
or override.

### Amendment A1 — Add SessionAcceptance artifact

Insert a new section between conditions 3 and 4 of the predicate:

```
3a. (NEW) SessionAcceptance is signed by K_IDENTITY (the session's
    runtime ephemeral key) and its signed region contains:
    - session_id
    - public_key_sha256 from step 1
    - freshness_challenge from step 3
    - coa_receipt_fingerprint (SHA-256 of canonicalized receipt)
    - acceptance_text_hash (SHA-256 of canonicalized model response
      containing the runtime nonce R)
    - prior_fingerprint = coa_receipt_fingerprint
    The signature verifies under public_key_b64 from step 1.
    The acceptance_text_hash matches the in-process transcript's
    last model-call response (which the harness cannot fabricate
    because R is runtime-held).
```

### Amendment A2 — Split condition 4 into 4a and 4b

```
4a. COA receipt is signed by K_TGE; signed region binds session_id,
    public_key_sha256, freshness_challenge, prior_fingerprint.
    Signature verifies under K_TGE public key.
4b. SessionAcceptance (per 3a) is signed by K_IDENTITY; signature
    verifies under public_key_b64 from step 1.
```

Both 4a AND 4b are required.

### Amendment A3 — Add runtime-held nonce R

The runtime exposes `runtime_nonce(session_id) -> bytes` API. Returns
a fresh `secrets.token_bytes(16)` nonce R held in process memory only.
The harness never sees R; the prompt to the model must contain R; the
runtime verifies R is present in the model response before signing
SessionAcceptance.

### Amendment A4 — Change model-call count from 1 to 2

Two model calls in the SAME persistent session:
- Call A: accept COA + emit response containing challenge + R.
- Call B: produce governed action in response to action prompt.

Both calls require the live session's runtime to capture model output
and sign via session ephemeral key.

### Amendment A5 — Strengthen condition 4 (stale receipt)

Add to condition 4: the receipt's signature timestamp must be strictly
greater than the operator's challenge-generation timestamp T_C (recorded
in operator-side evidence).

## Gate summary

| Gate | Disposition |
| -- | -- |
| G1 | PASS |
| G2 | PASS (with R2 recommendation) |
| G3 | PASS |
| G4 | PASS |
| G5 | **FAIL** (load-bearing) |
| Final | **REVISION_REQUIRED** |

## Required signer/key for live COA acceptance

**Currently in v0.2:** K_TGE (fixture-controlled). **This is the gap.**

**Required after amendment:** K_IDENTITY (session's runtime Eph25519
key), in a new SessionAcceptance artifact that binds the runtime-held
nonce R into the signed region.

## Whether the harness can manufacture acceptance evidence

**Currently in v0.2:** YES, the harness manufactures COA acceptance
using K_TGE alone. **This is the false PASS.**

**After amendment:** NO, the harness cannot manufacture SessionAcceptance
because R is runtime-held and the harness cannot predict the model's
response text. The harness cannot bypass the runtime's check that R
appears in the response.

## Whether 1 model call remains sufficient

**NO.** 2 model calls are required, in the same persistent session:
one for COA acceptance, one for governed action. The two calls are
mechanically distinct (different runtime-side signing operations,
different signed-region content).

## Confirmation of zero execution

- Zero participant / model calls occurred during this review.
- Zero experiment execution occurred.
- Zero live nonce generation occurred.
- Zero Hermes modification occurred.
- Zero premium evaluator engagement occurred.
- v0.2 design preserved byte-identically (SHA-256 `fc9884f5...`).
- All prior frozen artifacts preserved byte-identically.

STOP. Awaiting PI decision on amendments A1-A5.

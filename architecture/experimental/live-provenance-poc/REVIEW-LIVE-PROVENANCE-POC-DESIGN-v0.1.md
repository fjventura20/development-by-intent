# Adversarial Design Review — LIVE-PROVENANCE-POC-DESIGN-v0.1

**Status:** DESIGN REVIEW ONLY. No implementation. No participant / model calls. No live nonces generated. No evidence produced.
**Date:** 2026-09-14
**Reviewer:** Hermes (research-manager-mandate-2026-08-27)
**Subject:** `architecture/experimental/live-provenance-poc/LIVE-PROVENANCE-POC-DESIGN-v0.1.md` (SHA-256 `a4f4836ac4ea0c5b62a643fec6843784f24cb9494e9a0cb5e60d36fcd329e785`)

**Predecessors (preserved byte-identically):**
- ATE-PoC v0.2.1 — frozen at `c82f6233...` (closeout) + `fa8fa37...` (status amendment)
- Stage-C v0.2.2 GEL — SHA-256 `dfcf2514...21f`

## 0. Controlling question

> Could this experiment PASS even if the identity/governance evidence and the governed action were produced by DIFFERENT live agent sessions?

## 1. Classification

**MECHANISM_NOT_OBSERVABLE_WITH_CURRENT_RUNTIME — REVISION_REQUIRED**

The design's core intent is sound, but the controlling question can currently be answered YES for several scenarios under the v0.1 design. The experiment needs material revisions before it can defensibly claim to test live-session provenance. See §11 for required amendments.

---

## 2. Issue taxonomy

Issues are classified per the PI directive's review categories:

- **FATAL:** the experiment's PASS would not establish live provenance.
- **BLOCKS_POC:** the experiment cannot answer the central question without addressing this.
- **MUST_FIX_BEFORE_FORMAL_EVIDENCE:** weakens the claim but does not block the experiment.
- **DESIGN_HARDENING:** strengthens the design.
- **ACCEPTABLE_V0_1_LIMITATION:** accepted limitation explicitly documented.

---

## 3. Session identity

### 3.1 What the design says

> "the session ID assigned by Hermes (already present in `~/.hermes/sessions/`)"

### 3.2 Findings

**[FATAL] Session identity is asserted by the runtime, not obtained from an external authoritative source.**

The v0.1 design obtains the session ID from `~/.hermes/sessions/` — which is a Hermes-internal artifact. Hermes *asserts* the session ID, but nothing in the design establishes that this session ID is *authoritative* for the actual executing process. A co-located attacker that controls the `~/.hermes/sessions/` directory can fabricate a session record before any real session exists.

**[BLOCKS_POC] The session ID can be copied, replayed, fabricated, or transplanted without detection.**

The v0.1 design has no mechanism to prove that the session ID was issued by a specific runtime instance. Even within a single Hermes installation, multiple sessions share the same filesystem; nothing prevents one session's record from being copied into another's record directory.

**[MUST_FIX_BEFORE_FORMAL_EVIDENCE] "session ID assigned by Hermes" is not equivalent to "session ID issued by the running process whose actions we are governing."**

The session must be bound to a runtime-side cryptographic identity (a key held by the running process, not by a static config file), and the session ID must be deterministically derived from or signed by that key.

### 3.3 Required amendments (subset of §11)

- Introduce a runtime-side signing key generated AT session start (not pre-existing).
- Sign the session ID with that key.
- Bind the session record to the key's public fingerprint.

---

## 4. Continuity

### 4.1 What the design says

> "A signed session-binding artifact binds the live session ID + runtime identity + captured CLI invocation bytes."

### 4.2 Findings

**[FATAL] Continuity is established by an artifact generated in a single location, not by a mechanism that proves the same session persisted across stages.**

The v0.1 design has all four artifacts (provenance, session-binding, COA acceptance, ATE envelope) generated locally by the test runner. They all share the same session ID, but there is no mechanism to PROVE that the same runtime process persisted from the provenance stage to the action execution stage. The test runner could be replaced between stages with another instance that holds the same key — nothing would change.

**[BLOCKS_POC] No per-turn runtime continuity attestation.**

The v0.2.1 binding chain (in `pipeline_v2_1.py`) does not include a per-turn continuity attestation. The SignedCandidateAction is signed once at issuance; subsequent "turns" of the same session are not separately signed.

**[BLOCKS_POC] Transcript ordering or prompt presence is not a continuity mechanism.**

The v0.1 design says: "The same session ID appears at each stage." That is a textual observation, not a cryptographic or structural mechanism. The session ID is just a string; two unrelated stages can both write the same string into their respective artifacts.

### 4.3 Required amendments (subset of §11)

- Introduce per-stage continuity attestations: at COA acceptance, sign `(session_id, prior_stage_fingerprint)`; at action proposal, sign `(session_id, prior_stage_fingerprint)`.
- The binding chain must carry the prior-stage fingerprint in each subsequent signed region, so the entire chain collapses if any stage is replaced.

---

## 5. Runtime provenance

### 5.1 What the design says

> "the model identifier + version (e.g., from the model metadata)"

### 5.2 Findings

**[FATAL] Runtime provenance is self-reported by the model.**

The model identifier and version in the v0.1 design come from "model metadata" — which is a runtime-side artifact that the model itself can influence. A misbehaving runtime can claim to be a different model. There is no external attestation.

**[BLOCKS_POC] No runtime-observed evidence is distinguished from self-reported identity.**

The design does not say what evidence is OUTSIDE the runtime's control. Without such a distinction, "the runtime proves what it is" becomes tautological.

**[MUST_FIX_BEFORE_FORMAL_EVIDENCE] No hardware-backed identity is claimed; this is consistent with the predecessor PoC's posture, but it caps the achievable claim strength.**

The ATE-PoC v0.2.1 closeout explicitly disclaims hardware-backed identity. The v0.1 design inherits this limitation. This is acceptable for the PoC, but it caps the strongest claim.

### 5.3 Required amendments (subset of §11)

- Define what evidence is OUTSIDE the runtime's control (e.g., a deterministic nonce issued by an external verifier; a hash of CLI invocation bytes captured by the operator-side test runner).
- Distinguish runtime-observed evidence (what the runtime proves about itself) from operator-observed evidence (what the operator's test runner captures).
- Live provenance claim must be based on operator-observed evidence, not runtime-observed evidence.

---

## 6. Challenge freshness

### 6.1 What the design says

> "(the design does not explicitly define a freshness challenge)"

### 6.2 Findings

**[BLOCKS_POC] No freshness challenge is introduced between session creation and governance acceptance/action.**

A live-session experiment without a freshness challenge is replay-vulnerable: an attacker who captures the artifacts from a previous session can replay them in a new context, and the new session's runtime will produce a valid-looking chain.

**[BLOCKS_POC] No mechanism carries the freshness challenge into the final action evidence.**

Even if a challenge is introduced at session start, if it does not cryptographically appear in the final signed action, it cannot prevent replay.

### 6.3 Required amendments (subset of §11)

- Introduce a freshness challenge: a random nonce generated by the operator-side test runner AFTER the session exists and BEFORE governance acceptance.
- The challenge must appear in the COA acceptance's signed region AND in the SignedCandidateAction's signed region.
- The final DecisionRecord must include a fingerprint of the challenge.

---

## 7. Action binding

### 7.1 What the design says

> "Reuses ATE-PoC v0.2.1's TrustPipeline (`pipeline_v2_1.py`) byte-identically."

### 7.2 Findings

**[BLOCKS_POC] The SignedCandidateAction is signed by the runtime's Ed25519 key, but that key is fixture-generated within the experiment.**

In v0.2.1, the key is generated per-execution and is ephemeral. In v0.1, the same approach is used. This means the binding is real *within* the experiment, but the binding between the key and the actual live runtime process is asserted, not proven.

**[BLOCKS_POC] Could an action from another session be substituted while preserving apparently valid provenance?**

YES under the v0.1 design. Consider an attacker who:
- Captures a session A's provenance artifact, session-binding artifact, and SignedCandidateAction.
- Starts a new session B.
- Replays all artifacts in session B's context.
- The signing key for the artifacts is held by session A's runtime, but session B's runtime has a different key.
- If session B's test runner does not verify that the signing key matches the LIVE runtime's key (i.e., the key held by the currently-running process), the artifacts verify and the experiment PASSES.

### 7.3 Required amendments (subset of §11)

- The runtime's signing key must be generated at the moment of session start, held in process memory only, and not extractable from disk.
- The test runner must require that the signing key comes from a runtime-provided interface (e.g., the runtime must produce the key as part of its start-up sequence) rather than from a pre-existing fixture file.
- This requires either a runtime API (Hermes must expose a "session-key-init" interface) or a documented protocol for the test runner to extract the key from the running process.

---

## 8. Governance binding

### 8.1 What the design says

> "A COA acceptance artifact is generated and signed in-session."

### 8.2 Findings

**[BLOCKS_POC] Condition of Agency acceptance is session-specific only if it carries the session's cryptographic identity.**

The v0.1 design says COA acceptance is "signed in-session" — but "in-session" is operational, not cryptographic. The COA artifact must carry the session's signed_session_binding fingerprint AND the freshness challenge AND the runtime's key fingerprint.

**[FATAL] Without binding the COA artifact to the session key, the receipt can be transplanted.**

This is exactly the same attack as v0.2.1's ATE-V2.1-8 (transplant receipt). The v0.2.1 fix is to include `identity_fingerprint` in the receipt's signed region. The v0.1 design must extend this: the receipt must include the LIVE session's identity_fingerprint AND the freshness challenge AND a per-session nonce.

### 8.3 Required amendments (subset of §11)

- The COA acceptance artifact must include, in its signed region:
  - session_identity_fingerprint (the runtime's key fingerprint, derived from the session-start-generated key)
  - freshness_challenge
  - receipt_nonce (per-session, not per-experiment)
- Cross-binding check at pipeline stage 3 (BIND_RECEIPT) must verify these.

---

## 9. Negative controls

### 9.1 What the design says

> 4 cases (full chain, provenance substitution, cross-session action, replay) + optional Case 5 (early stop)

### 9.2 Findings

**[MUST_FIX_BEFORE_FORMAL_EVIDENCE] Missing negative control: copied governance receipt from another session.**

The v0.1 design does not include a case where the COA acceptance artifact is copied from another session (analogous to ATE-V2.1-8 but for COA specifically). This is essential to test governance binding.

**[MUST_FIX_BEFORE_FORMAL_EVIDENCE] Missing negative control: copied action from another session.**

The v0.1 design does not include a case where the SignedCandidateAction is copied from another session (analogous to ATE-V2.1-5/6/7). The "cross-session action submission" case (Case 3) tests session_id mismatch but does not test full transplantation of the SignedCandidateAction.

**[MUST_FIX_BEFORE_FORMAL_EVIDENCE] Missing negative control: stale/replayed session evidence.**

The v0.1 design does not include a case where the provenance artifact is from a STALE session (an older session that has since terminated). The replay case (Case 4) tests ATE-level replay but not provenance-level staleness.

### 9.3 Required amendments (subset of §11)

Add three additional cases:
- Case 5: COA acceptance copied from another session → DENY at pipeline stage 3.
- Case 6: SignedCandidateAction fully transplanted from another session → DENY at pipeline stage 5.
- Case 7: provenance artifact from a stale (terminated) session → DENY at provenance ↔ session-binding check.

Total cases: 7. Still within the "approximately 3–5 diagnostic cases" envelope per PI directive when measured as 3 distinct categories (substitution, transplantation, staleness) with full-chain + replay as controls.

---

## 10. False-PASS analysis

Mechanisms by which the experiment could incorrectly conclude that live provenance was established:

1. **[FATAL] Co-located attacker fabricates session records.** Without an external authoritative source for the session ID, a co-located attacker can write fake session records and the experiment would not detect it.
2. **[FATAL] Static session ID copied between test runs.** If the session ID is read from a fixture file rather than from a runtime-side API, copying it produces a valid-looking chain.
3. **[BLOCKS_POC] Test runner replaces runtime between stages.** The test runner could be replaced with another instance holding the same fixture key, and the experiment would not detect it.
4. **[BLOCKS_POC] Missing freshness challenge → replay across contexts.** Without a challenge, a previous session's artifacts replay into a new context.
5. **[MUST_FIX_BEFORE_FORMAL_EVIDENCE] Runtime-observed evidence used as if operator-observed.** If the runtime "proves" its own identity, this is self-attestation.
6. **[MUST_FIX_BEFORE_FORMAL_EVIDENCE] Transcript ordering conflated with continuity.** A textual sequence of artifacts is not a continuity mechanism.

---

## 11. Required design amendments (REVISION_REQUIRED)

For the design to become **READY_FOR_IMPLEMENTATION**, the following amendments are required:

1. **Runtime-side key generation:** the signing key must be generated at session start by the running Hermes process, not loaded from disk or a fixture file. (Addresses §3, §7.)

2. **Operator-observed evidence distinction:** explicitly enumerate which evidence fields are operator-observed (captured by the test runner outside the runtime) vs runtime-observed (asserted by the runtime). Live provenance claims must be based on operator-observed evidence. (Addresses §5.)

3. **Freshness challenge:** a random nonce generated by the test runner AFTER session start and BEFORE COA acceptance. The challenge must be signed into the COA acceptance, the SignedCandidateAction, and the DecisionRecord. (Addresses §6.)

4. **Per-stage continuity attestation:** each stage's signed artifact must include the prior-stage fingerprint. The chain collapses if any stage is replaced. (Addresses §4.)

5. **COA binding extension:** the COA acceptance must include session_identity_fingerprint, freshness_challenge, and per-session receipt nonce in its signed region. (Addresses §8.)

6. **Three additional negative controls:** COA transplant, action transplant, stale session. (Addresses §9.)

7. **Execution-boundary predicate:** define the exact predicate that must be satisfied before claiming `LIVE_SESSION_PROVENANCE_BOUND`. Suggested form:

   > `LIVE_SESSION_PROVENANCE_BOUND` iff:
   > - runtime-observed session_identity_fingerprint == operator-observed session_identity_fingerprint (captured from the runtime at session start)
   > - freshness_challenge observed by operator == freshness_challenge signed into the COA acceptance
   > - freshness_challenge observed by operator == freshness_challenge signed into the SignedCandidateAction
   > - freshness_challenge observed by operator == freshness_challenge recorded in the DecisionRecord
   > - session_id in identity == session_id in receipt == session_id in capability == session_id in SignedCandidateAction == session_id in DecisionRecord
   > - per-stage continuity attestations verify
   > - all negative controls (Cases 5/6/7) produce the expected DENY

8. **Operator-side capture protocol:** document the exact mechanism by which the operator-side test runner captures runtime-observed artifacts (e.g., a stdout line emitted by the runtime at session start, a key fingerprint written to a known operator-readable location).

---

## 12. Evidence independence analysis

| Claim | Source | Independent of runtime? |
| -- | -- | -- |
| Runtime identity (model id, version) | Runtime self-report | NO |
| Session ID | Runtime internal artifact | NO |
| Signing key | Runtime-generated at session start | PARTIAL — depends on operator-side capture mechanism |
| Freshness challenge | Operator-generated | YES |
| CLI invocation bytes | Operator-captured | YES |
| COA acceptance | Runtime-signed by session key | NO (but operator-captured if emitted via stdout) |
| SignedCandidateAction | Runtime-signed by session key | NO (but operator-captured if emitted via stdout) |
| DecisionRecord | Pipeline-signed by pipeline key | PARTIAL — pipeline key is a fixture |

**Conclusion:** live provenance can ONLY be claimed for claims whose operator-observed evidence matches the runtime's signed assertions. If the operator does not independently observe the runtime's claims (via stdout emission + capture), the experiment's PASS does not establish live provenance — it only establishes that the runtime signed a self-consistent artifact.

---

## 13. Execution boundary — exact predicate (proposed)

The experiment may claim `LIVE_SESSION_PROVENANCE_BOUND` only when ALL of the following are true:

1. The runtime emitted its session_identity_fingerprint to stdout at session start; the operator-side test runner captured this emission byte-for-byte.
2. The runtime emitted its session_id to stdout at session start; the operator-side test runner captured this emission byte-for-byte.
3. The operator-generated freshness_challenge matches:
   - the value recorded in the COA acceptance's signed region, AND
   - the value recorded in the SignedCandidateAction's signed region, AND
   - the value recorded in the DecisionRecord.
4. The session_id in all five binding artifacts (IdentityAttestation, AcceptanceReceipt, CapabilityToken, SignedCandidateAction, DecisionRecord) is byte-identical.
5. The runtime's signing key was generated AT session start (verified by a process-creation timestamp or a runtime-side attestation that the key was fresh — not loaded from disk).
6. All negative-control cases (Cases 5/6/7) produce the expected DENY.
7. The Case 1 (full chain) test produces ALLOW with all 7 conditions above met.

If ANY of these fails, the experiment's disposition must be:
- `LIVE_SESSION_PROVENANCE_NOT_BOUND` (with the specific failing condition recorded), OR
- `MECHANISM_NOT_OBSERVABLE` (if the runtime cannot emit the required artifacts to stdout).

---

## 14. Disposition summary

**MECHANISM_NOT_OBSERVABLE_WITH_CURRENT_RUNTIME — REVISION_REQUIRED**

The v0.1 design cannot, as written, answer the controlling question in the negative. With the amendments in §11, the design could potentially become `READY_FOR_IMPLEMENTATION`, but only if Hermes (or whichever live runtime is used) exposes:
- A stdout-emission API for session_id and signing key at session start.
- A way for the test runner to verify that the signing key was generated in-process, not loaded from disk.

If Hermes does not expose these capabilities, the disposition would shift to `MECHANISM_NOT_OBSERVABLE_WITH_CURRENT_RUNTIME` and the experiment would be unrunnable as designed.

---

## 15. Blocking defects

- **F-1:** Session identity asserted by runtime, not externally authoritative (§3).
- **F-2:** Continuity not mechanically established (§4).
- **F-3:** Runtime provenance is self-reported (§5).
- **F-4:** No freshness challenge; replay across contexts not prevented (§6).
- **F-5:** Action binding requires runtime-side key generation that may not be available in Hermes (§7).
- **F-6:** COA acceptance not bound to session key + freshness challenge (§8).

All six are blockers for `READY_FOR_IMPLEMENTATION`.

---

## 16. Required design amendments (consolidated)

The following amendments are required:

- A1. Runtime-side key generation at session start (not loaded from disk).
- A2. Operator-observed vs runtime-observed evidence distinction.
- A3. Freshness challenge generated by operator after session start.
- A4. Per-stage continuity attestations.
- A5. COA acceptance extension with session_identity_fingerprint + freshness_challenge + per-session receipt nonce.
- A6. Three additional negative controls (COA transplant, action transplant, stale session).
- A7. Execution-boundary predicate `LIVE_SESSION_PROVENANCE_BOUND` with 7 conditions.
- A8. Operator-side capture protocol (stdout emission + capture).

After applying A1–A8, the design should be re-reviewed to confirm `READY_FOR_IMPLEMENTATION` or escalate further.

---

## 17. Confirmation

- Zero participant / model calls occurred.
- Zero live nonces generated.
- Zero experimental evidence produced.
- Zero implementation files created.
- Only this review document was authored.
- All prior frozen artifacts preserved byte-identically (verified SHA-256 in this commit).

STOP. Awaiting PI decision on whether to revise the design or abandon this experiment direction.

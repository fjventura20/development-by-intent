# LIVE PROVENANCE → SESSION BINDING → ATE PoC v0.1 (DESIGN ONLY)

**Status:** DESIGN ONLY — not implemented, not executed.
**Author:** Hermes (research-manager-mandate-2026-08-27)
**Predecessors (preserved byte-identically):**
- ATE-PoC v0.1 — commit `6d39743ade499ea1e71bf7e528ccb91cbaaecfa8`
- ATE-PoC v0.2 design — SHA-256 `498b843a...`
- ATE-PoC v0.2.1 design — SHA-256 `f3261448...`
- ATE-PoC v0.2.1 implementation + evidence + closeout — commits `93e14fa6...`, `c82f6233...`
- ATE-PoC v0.2.1 status amendment — recorded in this commit
- Stage-C v0.2.2 GEL — SHA-256 `dfcf2514...21f`
- COA-E2 v0.4.4 closeout — commit `0b82a805c0797b485362100e7edef318b2df0cad`

## 0. Central question

**Can the identity, session, and governance claims entering an Agent Trust Envelope (ATE) be demonstrably anchored to the actual agent session that performs the authorized action?**

## 1. Primary hypothesis

> Evidence can demonstrate that the identity, session, and governance claims entering an ATE are anchored to the actual agent session that performs the authorized action.

## 2. Motivation: COA-E1 / E2 lesson

Per Frank Ventura, 2026-09-14:

> Governance acceptance is not sufficient unless it is demonstrably bound to the SAME LIVE SESSION that performs the governed action.

COA-E2 v0.4.4 result: a governance charter delivered only as ordinary conversational / in-context material is NOT sufficient evidence that governance has been authoritatively established. The charter content was present, but it was NOT bound to a specific session that demonstrably performed an authorized action.

ATE-PoC v0.2.1 (predecessor) established deterministic binding of fixture artifacts. The next gap is: those artifacts must be anchored to a *real live agent session*, not just to a static fixture.

## 3. The chain to test

```
actual runtime / model / agent instance
       ↓ (provenance claim)
specific persistent session
       ↓ (session binding)
accepted Condition of Agency (COA)
       ↓ (acceptance credential)
specific Agent Trust Envelope (ATE)
       ↓ (ATE)
authorized action
       ↓ (GEL enforcement)
executed action + auditable decision record
```

The central observable: the *same* live session must appear at the provenance stage and at the action execution stage, with a signed / bound credential chain linking them.

## 4. Frozen minimal experimental structure

### 4.1 Constraints (PI-prescribed)

- 3–5 diagnostic cases maximum.
- One agent / runtime initially.
- No premium evaluators.
- No replication.
- No large candidate matrix.
- Stop early on any clear binding failure.
- Prefer deterministic / local verification wherever possible.
- Model calls only where a live-agent property must actually be demonstrated.

### 4.2 Agent runtime

Use **Hermes itself** (the current session agent) as the single live agent runtime. This minimizes new infrastructure and reuses the existing `hermes chat` interface observed in earlier workstreams.

Rationale: Hermes is the agent that has been executing COA-E1, COA-E2, and Stage C; it is the only runtime with end-to-end operational traces in this workspace.

### 4.3 What "live provenance" means in this PoC

The PoC will capture and preserve:

- The exact `hermes` CLI invocation that started the session.
- The model identifier + version (e.g., from the model metadata).
- The session ID assigned by Hermes (already present in `~/.hermes/sessions/`).
- A nonce issued for this specific session (locally generated; not part of any prior frozen chain).
- A cryptographic identity for the session, generated inside the runtime as a fixture for this experiment (Ed25519 keypair).

The "provenance anchor" is the moment of session creation, plus the captured CLI invocation bytes. These are preserved byte-for-byte as part of the experiment's evidence.

### 4.4 What "session binding" means

The PoC will demonstrate that:

- A signed session-binding artifact binds the live session ID + runtime identity + captured CLI invocation bytes.
- The same session ID appears in the COA acceptance artifact and in the ATE envelope.
- The signing key for the session-binding artifact is held by the runtime (locally generated; not exposed beyond the experiment).

### 4.5 What "ATE" means in this PoC

Reuse ATE-PoC v0.2.1's TrustPipeline (`pipeline_v2_1.py`) byte-identically. The ATE is built around the live session, but the binding chain is exercised deterministically (no participant calls beyond the one COA acceptance step).

The v0.2.2 GEL is reused byte-identically (no adapter; SHA-256 `dfcf2514...21f`).

## 5. Frozen 4-case test matrix

### Case 1 — full live chain → ALLOW

Setup: live Hermes session established. A COA acceptance artifact is generated and signed in-session. An ATE envelope is built around the live session ID. A charter-consistent permitted action is proposed. The pipeline evaluates end-to-end.

Expected:
- Live provenance artifact present.
- Session binding artifact verifies.
- COA acceptance artifact verifies.
- ATE envelope's binding chain verifies.
- GEL verdict: allow.
- Final: ALLOW.
- All components reference the same session ID.

### Case 2 — provenance substitution → DENY

Setup: take Case 1's ATE envelope. Replace the provenance artifact with one from a *different* (fabricated) live session, but keep the session ID unchanged. This simulates a forgery attempt where the attacker controls one provenance link but not the session identity.

Expected:
- Provenance ↔ session-binding signature mismatch detected.
- Final: DENY with reason `GX_BIND_PROVENANCE_FAILED` (or analogous frozen reason).

### Case 3 — cross-session action submission → DENY

Setup: take Case 1's ATE envelope. Keep all artifacts intact, but submit the same authorized action under a *different* session ID (the ATE envelope's signed_candidate_action.session_id field is left intact, but the test runner simulates a different runtime-side session ID).

Expected:
- Stage 5 BIND_CANDIDATE_ACTION FAILS (session_id mismatch against identity's session_id).
- Final: DENY_BINDING_MISMATCH.

### Case 4 — replay (Case 1's exact ATE envelope under AUTHORIZE_EXECUTION twice) → DENY

Setup: run Case 1 successfully (nonce UNSEEN → AUTHORIZED → CONSUMED). Then re-submit the same envelope under AUTHORIZE_EXECUTION.

Expected:
- Nonce state = CONSUMED on the second attempt.
- Final: DENY_REPLAY with reason `GX_REPLAY_NONCE_PREVIOUSLY_CONSUMED`.
- Execution boundary NOT reached on the second attempt.

### Optional Case 5 — early stop on clear binding failure

If any of Cases 1–4 produces a clear binding failure (e.g., the provenance ↔ session binding fails on Case 1 itself, indicating the runtime cannot demonstrably anchor provenance to its own session), STOP early per the "stop early on any clear binding failure" rule. Record the failure mode in the closeout and do not proceed to subsequent cases.

## 6. What the PoC establishes (if it passes)

- That a live Hermes session can cryptographically anchor a provenance claim (captured CLI invocation + nonce + session ID + runtime-side keypair).
- That the provenance claim binds to the same session ID used in the COA acceptance and the ATE envelope.
- That an end-to-end LIVE PROVENANCE → SESSION BINDING → ATE chain is verifiable with the same byte-identical ATE-PoC v0.2.1 components.

## 7. What the PoC does NOT establish

- That the underlying runtime / model cannot be impersonated by an attacker with the same host access (the runtime's signing key is held by the runtime itself; host compromise breaks it).
- That the COA acceptance is semantically meaningful to the participant (no behavioral test is included; this is structural binding evidence only).
- That the binding works under naturalistic adversarial conditions (only the four deterministic mutation cases above are tested).
- Production-grade cryptographic assurance (still fixture keys, no PKI, no hardware roots).

## 8. Strongest claim permitted (only if PoC passes)

> For the tested live Hermes session, a chain of evidence (provenance artifact + session-binding artifact + COA acceptance artifact + ATE envelope + signed DecisionRecord) can be established where the same session ID appears at each stage and each stage's signature is verifiable. Substitution of the provenance artifact, cross-session action submission, and replay of the exact ATE envelope under AUTHORIZE_EXECUTION are all detected at the appropriate binding stage or replay check. The ATE-PoC v0.2.1 binding chain (preserved byte-identically) composes with the live session anchoring to form an end-to-end LIVE PROVENANCE → SESSION BINDING → ATE chain.

## 9. Forbidden claims

- Behavioral governance evidence.
- General agent trustworthiness.
- Production security / cryptographic assurance.
- Hardware-backed identity.
- Value Architecture effectiveness.
- DbI/INSA core architecture.
- That the live session corresponds to a *human* (it is the live agent / runtime).
- That the binding would survive host compromise.

## 10. Estimated cost

- ~200 LOC additional code (provenance + session binding generators; reuse ATE-PoC v0.2.1 pipeline).
- ~4 participant calls (one per case; case 5 is a conditional stop).
- 1 model invocation per case (Hermes itself, to emit the candidate action in Case 1 only).
- < 1 minute total runtime.

## 11. Relationship to COA-E1 / E2

This PoC directly addresses the COA-E2 v0.4.4 closeout's central finding:

> A governance charter delivered only as ordinary conversational / in-context material is not sufficient evidence that governance has been authoritatively established.

By anchoring the COA acceptance to a live session via a signed provenance artifact, the PoC tests whether the structural gap (no demonstrated live-agent binding) can be closed using the existing ATE-PoC v0.2.1 components.

## 12. Files (planned)

- `architecture/experimental/live-provenance-poc/LIVE-PROVENANCE-POC-DESIGN-v0.1.md` (this document)
- `architecture/experimental/live-provenance-poc/implementation/provenance.py`
- `architecture/experimental/live-provenance-poc/implementation/session_binding.py`
- `architecture/experimental/live-provenance-poc/implementation/run_live_provenance.py`
- `architecture/experimental/live-provenance-poc/evidence/live_provenance_evidence.json`

The ATE-PoC v0.2.1 implementation files are reused byte-identically.

## 13. Scope

- DESIGN ONLY.
- No implementation.
- No execution.
- No participant invocation (Cases 1–4 require exactly one live participant invocation per case; total ≤ 4).
- No production cryptography.
- No hardware-backed identity.
- No promotion of GEL, TGE, COA, ATE, or live-provenance-poc into DbI/INSA core.
- v0.2.2 GEL reused byte-identically (SHA-256 `dfcf2514...21f`).
- ATE-PoC v0.2.1 pipeline reused byte-identically.

STOP-AT-DESIGN. Awaiting PI authorization to implement and execute.

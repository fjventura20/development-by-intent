# Agent Conformance Protocol v0.1.1 — Cross-Spec Reconciliation Review

**Reviewed artifact:** `AGENT-CONFORMANCE-PROTOCOL-v0.1.1.md`  
**Controlling references:**
- `AGENT-QUALIFICATION-AND-ADMISSION-PROTOCOL-v0.2.2.md`
- `ATE-REVOCATION-TRUST-STATE-MODEL-v0.1.md`
- `ATE-ENFORCEMENT-PLANE-v0.1.md`
- `ATE-AUDIT-ACCOUNTABILITY-MODEL-v0.1.md`

**Disposition:** NARROW CORRECTION REQUIRED BEFORE FREEZE

## 1. Reconciled Areas

The following are consistent:

- `CONFORMANT != AUTHORIZED_TO_ACT`
- fail-closed UNKNOWN semantics
- current-state verification
- independent executor enforcement
- immutable decision history
- monotonic epoch/version use
- participant inability to self-certify
- audit separation from authorization
- fresh evidence required for restoration

## 2. Required Corrections

### R1 — Revocation authority namespace collision
**Severity:** HIGH

v0.1.1 gives R14 power to "revoke." The Revocation & Trust-State Model already requires artifact-class-specific revocation authority.

**Correction:** distinguish `CONFORMANCE_REVOKED` lifecycle state from revocation of QualificationCredential, AdmissionCredential, identity, key, policy, or other controlling artifact.

R14 may publish `CONFORMANCE_REVOKED` when authorized. R14 may not publish a `RevocationRecord` for another artifact class unless independently authorized by the Trust Root Registry.

Externally authoritative revocation remains controlling and cannot be overridden by conformance state.

### R2 — Mandatory requalification/readmission trigger precedence
**Severity:** HIGH

Qualification v0.2.2 defines `mandatory_requalification_triggers[]`; Admission Policy defines `mandatory_readmission_triggers[]`.

A conformance re-attestation must not convert those stronger transitions into ordinary lifecycle refresh.

**Correction:** the conformance evaluator must route mandatory requalification triggers to Qualification and mandatory readmission triggers to Admission. Conformance cannot restore the subject until the required upstream lifecycle is completed.

### R3 — Canonical artifact/signing-domain discipline missing
**Severity:** MEDIUM-HIGH

Qualification v0.2.2 requires deterministic canonical encoding, versioned hashes, and signing-domain separation. New conformance artifact classes need equivalent rules.

**Correction:** define canonical digest rule and signing domains for:
- ConformanceRequirementsProfile
- ConformanceTriggerObservation
- ConformanceEvaluationResult
- ConformanceStateDecision

At minimum:
```text
ATE_CONFORMANCE_PROFILE_V1
ATE_CONFORMANCE_TRIGGER_V1
ATE_CONFORMANCE_EVALUATION_V1
ATE_CONFORMANCE_STATE_DECISION_V1
```

### R4 — Audit integration is additive, not a replacement
**Severity:** LOW

The proposed conformance events are compatible with the audit model, provided the normal AuditRecord chain/sequence/signature requirements continue to apply.

No correction beyond explicit statement is required.

### R5 — Enforcement integration reconciles
**Severity:** PASS

The state-epoch recheck strengthens the Enforcement Plane's TOCTOU and final current-state verification rules and does not replace nonce, action digest, session binding, revocation, expiration, or adapter checks.

## 3. Recommendation

Produce `AGENT-CONFORMANCE-PROTOCOL-v0.1.2.md` containing only R1-R4 corrections.

If the resulting artifact preserves all v0.1.1 invariants, classify it as **FINAL FREEZE CANDIDATE** and freeze it without another broad redesign.

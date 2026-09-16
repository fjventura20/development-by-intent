# Agent Qualification & Admission — Cross-Spec Reconciliation Review v0.1

**Reviewed set:**

- `AGENT-QUALIFICATION-AND-ADMISSION-PROTOCOL-v0.2.1.md`
- `ATE-TRUST-ROOT-KEY-CUSTODY-MODEL-v0.1.1-QUALIFICATION-ADMISSION-AMENDMENT.md`
- `ATE-REVOCATION-TRUST-STATE-MODEL-v0.1.1-QUALIFICATION-ADMISSION-AMENDMENT.md`
- `ATE-PRODUCTION-ARCHITECTURE-v0.1.1-QUALIFICATION-ADMISSION-AMENDMENT.md`
- `ATE-RISK-ASSURANCE-POLICY-MODEL-v0.1.1-QUALIFICATION-ADMISSION-AMENDMENT.md`
- `ATE-AUDIT-ACCOUNTABILITY-MODEL-v0.1.1-QUALIFICATION-ADMISSION-AMENDMENT.md`

**Review purpose:** determine whether the reconciled specification set can be frozen before the local synthetic PoC.  
**Disposition:** **TWO CORRECTIONS REQUIRED; OTHERWISE COHERENT**

---

## 1. Reconciliation Result

The six documents are architecturally consistent on the central controls:

```text
qualification != admission != authorization
```

They consistently establish:

- R11 Qualification Authority and R12 Admission Authority;
- explicit policy-authority permissions;
- canonical SubjectBinding;
- immutable signed eligibility credentials;
- authority validation in addition to signature validation;
- exact qualification dependency for admission;
- signed qualification/admission dependencies in CapabilityToken and TrustDecision;
- coherent trust-state snapshots;
- final current-state check before EAP;
- deterministic revocation/EAP ordering;
- derived downstream expiry;
- A2/R2 first-PoC scope;
- durable tamper-evident qualification/admission/EAP audit evidence;
- synthetic subjects with no live LLM requirement.

No unresolved contradiction was found among authority, revocation, production path, assurance, and audit semantics.

Two schema issues remain before freeze.

---

## 2. RR-1 — HIGH — Admission policy can implicitly trust unknown future qualification-profile versions

The protocol currently includes:

```text
minimum_qualification_profile_versions[]
```

A simple “minimum version” rule can accidentally admit a future profile that the trust domain has never reviewed. A numerically newer version is not automatically security-compatible with the admitted role.

This conflicts with the project's explicit-trust principle.

### Required correction

Replace version-floor semantics with explicit recognition constraints such as:

```text
recognized_qualification_profiles[] {
    profile_id
    allowed_version_or_digest_constraints[]
}
```

The trust domain must explicitly recognize the profile version/digest under which qualification was issued.

Unknown future profile versions fail closed until the Admission Policy is updated.

---

## 3. RR-2 — MEDIUM — `next_review_at_optional` has undefined security semantics

AdmissionCredential includes:

```text
next_review_at_optional
```

The reconciled documents do not define whether crossing that timestamp:

- invalidates admission;
- merely generates an administrative reminder; or
- requires a separate review artifact.

A security credential should not contain an ambiguous lifecycle boundary.

### Required correction

For v0.2.2, remove `next_review_at_optional` from AdmissionCredential.

If a domain requires periodic re-admission, express it through `expires_at` / `maximum_admission_duration` and issue a new AdmissionDecision + AdmissionCredential after review.

This keeps credential usability deterministic.

---

## 4. Verified Cross-Spec Consistency

### 4.1 Authority model — PASS

R11/R12 permissions, policy-authority separation, signing-domain separation, and participant key exclusion are consistent.

### 4.2 Revocation/dependency model — PASS

Qualification invalidates dependent admission; admission invalidates downstream authorization before EAP; current-state semantics are external to immutable credentials.

### 4.3 Trust-state coherence — PASS

Protocol, revocation amendment, production amendment, and audit amendment consistently require one coherent state view rather than mixed epochs.

### 4.4 EAP semantics — PASS

Production and revocation semantics agree: invalidating state effective/observable before EAP blocks the action; local PoC ordering is serialized and auditable.

### 4.5 Risk/assurance integration — PASS

A2/R2 is an appropriate first diagnostic profile; qualification/admission do not replace action-time evidence.

### 4.6 Audit integration — PASS

Qualification, admission, current-state, dependency, and EAP events can be reconstructed using the existing tamper-evident audit model.

### 4.7 PoC cost discipline — PASS

The design requires deterministic synthetic subjects and no live premium model calls.

---

## 5. Required Final Candidate

Create `AGENT-QUALIFICATION-AND-ADMISSION-PROTOCOL-v0.2.2.md` with only the two reconciliation corrections:

1. explicit profile recognition instead of minimum-version trust;
2. remove ambiguous `next_review_at_optional`.

No changes are required to the five v0.1.1 amendments for these corrections.

After verifying v0.2.2 against this review, the six-document set may be frozen if no new contradiction is introduced.

---

## 6. Reconciliation Disposition

```text
Authority integration:          PASS
Revocation integration:         PASS
Production-path integration:    PASS
Risk/assurance integration:     PASS
Audit integration:              PASS
Trust-state coherence:          PASS
EAP semantics:                  PASS
PoC scope/cost discipline:      PASS
Profile-version recognition:    CORRECTION REQUIRED
Admission review timestamp:     CORRECTION REQUIRED
```

**Implementation remains unauthorized until v0.2.2 is produced, verified, and frozen with the amendment set.**

# ATE Audit & Accountability Model v0.1.1 — Qualification/Admission Amendment

**Status:** RECONCILIATION AMENDMENT — NOT INDEPENDENTLY FROZEN  
**Amends:** `ATE-AUDIT-ACCOUNTABILITY-MODEL-v0.1.md`  
**Required by:** `AGENT-QUALIFICATION-AND-ADMISSION-PROTOCOL-v0.2.1.md`

---

## 1. Purpose

This amendment adds qualification, admission, coherent trust-state, and Execution Authorization Point (EAP) events to the existing ATE accountability chain.

The baseline principle remains:

> Every consequential trust or execution transition produces durable evidence external to participant control.

---

## 2. New Required Event Classes

Add:

```text
QUALIFICATION_EVALUATION_STARTED
QUALIFICATION_GRANTED
QUALIFICATION_DENIED
QUALIFICATION_CREDENTIAL_ISSUED
QUALIFICATION_SUSPENDED
QUALIFICATION_REVOKED

ADMISSION_EVALUATION_STARTED
ADMISSION_GRANTED
ADMISSION_DENIED
ADMISSION_CREDENTIAL_ISSUED
ADMISSION_SUSPENDED
ADMISSION_REVOKED

EXECUTION_AUTHORIZATION_POINT_REACHED
EXECUTION_BLOCKED_BY_ELIGIBILITY_STATE
```

Policy/profile activation or supersession continues to use the baseline policy events where applicable.

---

## 3. AuditRecord Field Additions

Add optional fields when relevant:

```text
subject_binding_digest?
qualification_profile_id?
qualification_profile_digest?
qualification_decision_id?
qualification_credential_id?
qualification_credential_digest?
qualification_evidence_manifest_digest?

admission_policy_id?
admission_policy_digest?
admission_decision_id?
admission_credential_id?
admission_credential_digest?
admission_evidence_manifest_digest?

trust_state_view_id?
trust_state_snapshot_digest?
execution_authorization_point_id?
```

Existing:

```text
trust_root_epoch
revocation_epoch
policy_epoch
controlling_artifact_hashes[]
```

remain applicable.

---

## 4. Qualification Audit Minimums

A `QUALIFICATION_GRANTED` or `QUALIFICATION_DENIED` record must identify at least:

```text
subject_binding_digest
role_id / equivalent role reference
qualification profile id/digest
qualification evidence manifest digest
qualification decision id
verdict
reason code
qualification authority id
coherent trust-state view reference
controlling artifact hashes
```

A credential-issuance event also records the QualificationCredential ID/digest.

---

## 5. Admission Audit Minimums

An `ADMISSION_GRANTED` or `ADMISSION_DENIED` record must identify at least:

```text
subject_binding_digest
trust domain
role reference
exact qualification credential id/digest
admission policy id/digest
admission evidence manifest digest
admission decision id
verdict
reason code
admission authority id
coherent trust-state view reference
controlling artifact hashes
```

A credential-issuance event also records the AdmissionCredential ID/digest.

---

## 6. Coherent Trust-State Audit Binding

Qualification/admission decision records MUST preserve the authoritative `state_view_id` or signed TrustStateSnapshot digest used by the decision.

Audit verification must be able to detect mixed-epoch or inconsistent state references.

A record that merely stores several unrelated registry epochs without a coherent state-view binding is insufficient for qualification/admission reconstruction.

---

## 7. Execution Authorization Point Audit

When a governed action reaches EAP, emit:

```text
EXECUTION_AUTHORIZATION_POINT_REACHED
```

The record should include:

```text
execution_authorization_point_id
subject_binding_digest
qualification/admission credential ids/digests
CapabilityToken id
TrustDecision id
requested action digest
nonce/execution reservation reference
trust-state view / revocation epoch observed
executor identity
ordered timestamp / ledger sequence
```

If eligibility state blocks execution before EAP, emit:

```text
EXECUTION_BLOCKED_BY_ELIGIBILITY_STATE
```

with the failing dependency and deterministic reason code.

---

## 8. Ordering Requirement

The audit chain must permit reconstruction of whether an invalidating state change occurred before or after EAP.

For the local PoC, the serialized execution transaction should emit records or transaction references sufficient to demonstrate:

```text
revocation committed before EAP -> execution blocked
EAP committed before later revocation -> ordering recorded unambiguously
```

Wall-clock timestamps alone are not sufficient when sequence/transaction ordering is available.

Use ledger sequence, transaction order, state epoch, and hash-chain evidence.

---

## 9. Canonical Digest Evidence

When the audit ledger records qualification/admission artifact hashes, those hashes MUST use the canonical artifact digest semantics defined by the qualification/admission protocol or the reconciled ATE canonicalization profile.

The ledger must not hash pretty-printed or mutable presentation forms as security identities.

---

## 10. Denials Are First-Class Evidence

Qualification/admission denial, inconsistent trust-state detection, unauthorized issuer rejection, digest mismatch, subject-binding mismatch, and EAP eligibility block events must be retained just like successful decisions.

Historical denial records are never rewritten when the subject later succeeds.

---

## 11. PoC Requirements

The first PoC must demonstrate that every QA-P1 through QA-P12 test produces a reconstructable audit trail containing:

- controlling artifact digests;
- verdict/reason code;
- current-state view;
- executor/EAP ordering where execution is attempted;
- protected-resource outcome.

An otherwise successful governed action without durable audit evidence fails the PoC accountability requirement.

---

## 12. Amendment Disposition

This amendment becomes controlling only when frozen together with the reconciled qualification/admission specification set.

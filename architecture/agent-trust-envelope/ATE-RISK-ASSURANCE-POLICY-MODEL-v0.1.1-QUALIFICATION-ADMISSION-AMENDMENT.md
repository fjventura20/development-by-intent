# ATE Risk & Assurance Policy Model v0.1.1 — Qualification/Admission Amendment

**Status:** RECONCILIATION AMENDMENT — NOT INDEPENDENTLY FROZEN  
**Amends:** `ATE-RISK-ASSURANCE-POLICY-MODEL-v0.1.md`  
**Required by:** `AGENT-QUALIFICATION-AND-ADMISSION-PROTOCOL-v0.2.1.md`

---

## 1. Purpose

This amendment defines how qualification and trust-domain admission scale with the existing R0-R4 risk classes and A0-A4 assurance profiles without replacing action-time assurance requirements.

Qualification/admission are standing eligibility controls. Action-time ATE evidence remains independently required according to the requested action.

---

## 2. Core Rule

When a role/action policy requires qualification and admission:

```text
usable qualification
AND usable admission
AND required action-time assurance
```

are all mandatory.

Higher standing qualification does not waive fresher action-time evidence.

---

## 3. A0 / R0

For informational/negligible-impact actions, policy MAY declare qualification/admission unnecessary.

If qualification/admission are used, lightweight identity binding and logical authority separation may be sufficient.

No persistent privileged capability is created.

---

## 4. A1 / R1

Qualification/admission are policy-specific.

Where required, minimum controls include:

- recognized subject identity;
- current role qualification;
- current trust-domain admission;
- policy-controlled risk/capability ceiling;
- current revocation check;
- auditable decision.

Logical authority separation may be sufficient where signed domain policy permits.

---

## 5. A2 / R2

For governed R2 actions whose role policy requires qualification/admission, minimum controls include:

- canonical SubjectBinding;
- current QualificationCredential;
- current AdmissionCredential bound to the exact qualification;
- qualification/admission dependencies bound into CapabilityToken and TrustDecision;
- distinct R11/R12 signing identities;
- participant excluded from qualification/admission/policy signing keys and generic signing oracles;
- current trust-state/revocation check at ATE evaluation;
- final eligibility/current-state recheck before EAP;
- executor mediation;
- durable tamper-evident audit.

The first local PoC targets A2/R2.

---

## 6. A3 / R3

Includes all A2 qualification/admission controls plus:

- stronger authority process/service separation;
- stronger key custody according to baseline A3 rules;
- strict trust-state freshness at EAP;
- policy-defined stronger SubjectBinding where material;
- shorter admission/qualification review intervals when risk warrants;
- explicit approval evidence when baseline A3 action policy requires human or additional authority approval.

Standing qualification/admission does not satisfy the A3 final policy/revocation recheck by itself.

---

## 7. A4 / R4

Includes all A3 qualification/admission controls plus the baseline A4 critical-action controls.

Where qualification/admission participate in an A4 action, domain policy SHOULD require strong provenance/SubjectBinding compatible with the critical action, strong authority key custody, and very current trust-state evaluation.

Mandatory human/quorum requirements defined by the baseline A4 policy remain action-time requirements and MUST NOT be inferred merely from AdmissionCredential issuance.

---

## 8. Eligibility Ceilings

Qualification and admission define ceilings, not grants.

Effective risk ceiling:

```text
min(
  qualification maximum_eligible_risk_level,
  admission maximum_admitted_risk_level,
  role-policy maximum,
  current capability/action-policy maximum
)
```

Effective capability-class eligibility:

```text
intersection(
  qualification eligible_capability_classes,
  admission eligible_capability_classes,
  role-policy classes
)
```

The participant cannot classify its own action downward or widen these ceilings.

---

## 9. Freshness and Expiration Interaction

Qualification/admission nominal validity is separate from action-time evidence freshness.

A downstream artifact MUST NOT outlive the earliest controlling eligibility dependency.

A high-risk action may require requalification, re-admission, or fresher supporting evidence even when a standing credential has not nominally expired if signed policy explicitly imposes that requirement.

---

## 10. Authority Separation Matrix Addition

| Control | A0 | A1 | A2 | A3 | A4 |
|---|---:|---:|---:|---:|---:|
| Qualification/admission required | Policy | Policy | Role-policy for governed actions | Role-policy / expected for privileged roles | Role-policy / expected for critical roles |
| SubjectBinding | Minimal/policy | Required where used | Canonical + live proof | Strong | Strong/high-assurance |
| R11/R12 distinct key identities | Optional/policy | Recommended | Required | Required | Required |
| Policy vs adjudication separation | Optional/policy | Recommended | Required unless superior signed exception | Required | Required |
| Final eligibility recheck before EAP | Basic/policy | Required where used | Required | Immediate | Immediate/current |
| Qualification/admission audit | Basic | Required | Durable/tamper-evident | Mandatory | Mandatory + critical audit controls |

This matrix supplements, and does not weaken, the baseline assurance matrix.

---

## 11. PoC Constraint

The first PoC is fixed at:

```text
risk class: R2
assurance profile: A2
```

Use synthetic subjects, exact SubjectBinding, distinct signing keys, current-state recheck, executor mediation, and deterministic EAP ordering.

No premium/live-model evaluation is required.

---

## 12. Amendment Disposition

This amendment becomes controlling only when frozen together with the reconciled qualification/admission specification set.

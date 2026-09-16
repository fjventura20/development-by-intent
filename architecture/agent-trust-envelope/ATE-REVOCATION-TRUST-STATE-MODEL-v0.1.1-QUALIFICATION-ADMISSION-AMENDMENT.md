# ATE Revocation & Trust-State Model v0.1.1 — Qualification/Admission Amendment

**Status:** RECONCILIATION AMENDMENT — NOT INDEPENDENTLY FROZEN  
**Amends:** `ATE-REVOCATION-TRUST-STATE-MODEL-v0.1.md`  
**Required by:** `AGENT-QUALIFICATION-AND-ADMISSION-PROTOCOL-v0.2.1.md`

---

## 1. Purpose

This amendment makes qualification and admission first-class revocable trust-state dependencies and defines their ordering relative to protected execution.

---

## 2. New Revocable Object Classes

Add at least:

```text
qualification_credential_id
admission_credential_id
qualification_requirements_profile
admission_policy
qualification_authority_key
admission_authority_key
qualification_policy_authority_key
admission_policy_authority_key
subject_binding_anchor where applicable
```

All use immutable identifiers/digests, never mutable display names.

---

## 3. Reason-Code Additions

```text
RV_QUALIFICATION_WITHDRAWN
RV_QUALIFICATION_EVIDENCE_INVALIDATED
RV_ADMISSION_WITHDRAWN
RV_ROLE_CHANGED
RV_REQUALIFICATION_REQUIRED
RV_READMISSION_REQUIRED
```

Existing key/authority compromise reason codes remain applicable to R11/R12 and policy authorities.

---

## 4. Revocation Authority Scope

The Trust Root Registry must explicitly define who may revoke/suspend/reinstate each new object class.

Baseline model:

```text
Qualification Authority:
    may revoke/suspend QualificationCredentials it issued when policy permits

Admission Authority:
    may revoke/suspend AdmissionCredentials it issued when policy permits

Policy Authority:
    may supersede/withdraw profiles or admission policies it issued

Trust Root / superior emergency authority:
    may revoke subordinate authority keys and may perform emergency revocation when root governance permits
```

The participant subject has no revocation or reinstatement authority merely because it is the subject of the credential.

---

## 5. Dependency Invalidation

Required dependency graph:

```text
Qualification policy/profile
        ↓
QualificationCredential
        ↓
AdmissionCredential
        ↓
CapabilityToken
        ↓
TrustDecision
        ↓
Execution authorization
```

Additional authority/key dependencies apply to every signed node.

If a QualificationCredential becomes unusable, any dependent AdmissionCredential is unusable for new authorization even if the AdmissionCredential remains cryptographically intact and within its nominal validity interval.

If an AdmissionCredential becomes unusable, dependent CapabilityTokens/TrustDecisions cannot support crossing the Execution Authorization Point.

---

## 6. Hard vs Soft Supersession

Qualification/admission policy artifacts may define supersession semantics.

At minimum distinguish:

```text
HARD_SUPERSESSION
    prior artifact immediately unusable for new authorization

NO_NEW_ISSUANCE
    prior artifact cannot issue new credentials, but existing dependent credentials remain usable until their own expiry/revocation unless another rule invalidates them
```

If supersession semantics are absent or invalid, governed qualification/admission evaluation fails closed rather than guessing.

---

## 7. Coherent Trust-State Snapshot

QualificationDecision and AdmissionDecision MUST use one coherent current-state view.

Preferred mechanism:

```text
TrustStateSnapshot {
    trust_domain
    state_view_id
    registry_epoch
    generated_at
    valid_until

    active_policy_manifest_digest
    trust_root_registry_digest
    revocation_registry_digest

    issuer
    signature
}
```

If multiple registries are physically separate, the state view must still provide one authoritative consistency boundary.

Mixed-epoch assembly from unrelated states is invalid.

---

## 8. Qualification/Admission in G0 Revocation

Where the action policy requires qualification/admission, G0 must include:

```text
QualificationCredential
AdmissionCredential
R11 key/authority
R12 key/authority
relevant qualification/admission policy authority keys
```

and any profile/policy whose current-state semantics directly control usability.

A revoked/suspended/unknown controlling dependency produces denial.

---

## 9. Execution Authorization Point

Define:

> **Execution Authorization Point (EAP):** the final serialized/authoritative point at which the Capability Executor validates current controlling trust state and commits to attempting the protected side effect.

Required guarantee:

> Any invalidating trust-state change that is effective and observable by the authoritative state system before the EAP MUST prevent the action from crossing the EAP.

A revocation that becomes effective only after an irreversible external effect has already crossed its commit point cannot retroactively undo that effect.

---

## 10. Executor Recheck

Immediately before EAP, the executor rechecks current state for at least:

```text
subject/session binding dependency
QualificationCredential
AdmissionCredential
CapabilityToken
TrustDecision
relevant issuer keys/authorities
```

The executor may use the signed dependency bindings carried by TrustDecision/execution capability and does not need to re-run historical qualification evidence evaluation.

---

## 11. Local PoC Ordering

For the local PoC, eligibility current-state recheck, nonce/execution reservation, EAP, and protected local mutation must occur inside one serializable transaction, lock, or equivalent critical section.

Required deterministic cases:

```text
revocation committed before EAP -> DENY
EAP committed before later revocation -> already-established local execution transaction completes according to that ordering
```

Audit evidence must make the order reconstructable.

---

## 12. Epoch Capture

TrustDecision and executor audit records must capture the coherent state view / revocation epoch consulted.

An executor observing a newer epoch than the TrustDecision must evaluate whether any controlling dependency changed before EAP. A newer epoch cannot be ignored solely because the TrustDecision signature remains valid.

---

## 13. Amendment Disposition

This amendment becomes controlling only when frozen with the reconciled qualification/admission document set.

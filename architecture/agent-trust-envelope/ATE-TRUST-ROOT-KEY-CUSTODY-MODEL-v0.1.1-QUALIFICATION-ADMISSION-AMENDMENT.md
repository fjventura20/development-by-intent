# ATE Trust Root & Key Custody Model v0.1.1 — Qualification/Admission Amendment

**Status:** RECONCILIATION AMENDMENT — NOT INDEPENDENTLY FROZEN  
**Amends:** `ATE-TRUST-ROOT-KEY-CUSTODY-MODEL-v0.1.md`  
**Required by:** `AGENT-QUALIFICATION-AND-ADMISSION-PROTOCOL-v0.2.1.md`

---

## 1. Purpose

This amendment adds the authority and key-custody semantics required for qualification and trust-domain admission.

The baseline rule remains:

```text
CRYPTOGRAPHICALLY_VALID
AND
ISSUER_AUTHORIZED_FOR_ARTIFACT_TYPE
```

A valid signature from an unauthorized issuer is unusable.

---

## 2. New Logical Authority Roles

### R11 — Qualification Authority

May sign only when explicitly permitted by the Trust Root Registry:

```text
QualificationDecision
QualificationCredential
qualification administrative artifacts delegated by policy
```

R11 does not automatically receive:

```text
Trust Root Authority
policy-authoring authority
Authorization Authority
Trust Decision Authority
Capability Executor credentials
```

### R12 — Admission Authority

May sign only when explicitly permitted by the Trust Root Registry:

```text
AdmissionDecision
AdmissionCredential
admission administrative artifacts delegated by policy
```

R12 does not automatically receive:

```text
Trust Root Authority
policy-authoring authority
Qualification Authority
Authorization Authority
Trust Decision Authority
Capability Executor credentials
```

---

## 3. Qualification/Admission Policy Artifact Authority

The following are policy artifacts:

```text
QualificationRequirementsProfile
AdmissionPolicy
```

The Trust Root Registry MUST explicitly identify which authority may sign each artifact type.

This amendment does not require a new numbered policy role. A deployment may extend an existing Policy Authority or create a dedicated policy authority, but the permission MUST be explicit in `permitted_artifact_types[]`.

R11 or R12 possession of an adjudication key does not imply permission to sign either policy artifact.

At A2+ assurance, policy-authoring and adjudication keys MUST be distinct unless a superior signed governance policy explicitly permits concentration.

---

## 4. Required Artifact-Type Registrations

The Trust Root Registry must recognize at least:

```text
QualificationRequirementsProfile
QualificationDecision
QualificationCredential
AdmissionPolicy
AdmissionDecision
AdmissionCredential
```

Each registration binds:

```text
authority_id
public_key_id
permitted_artifact_type
trust_domain
validity interval
status
```

---

## 5. Signing-Domain Separation

Qualification/admission signing services MUST use distinct artifact domains, at minimum:

```text
ATE_QUALIFICATION_PROFILE_V1
ATE_QUALIFICATION_DECISION_V1
ATE_QUALIFICATION_CREDENTIAL_V1
ATE_ADMISSION_POLICY_V1
ATE_ADMISSION_DECISION_V1
ATE_ADMISSION_CREDENTIAL_V1
```

A signature produced for one domain MUST NOT verify as another artifact type.

Generic `sign_anything(bytes)` access is prohibited to participant agents.

---

## 6. Key Custody by Assurance Level

### A0/A1

Where policy permits, logical role separation and KC1 operational keys may be sufficient.

### A2

Minimum requirements:

- participant cannot possess qualification/admission/policy private keys;
- participant cannot invoke generic signing oracles for those keys;
- R11 and R12 use distinct key identities;
- policy-authoring keys are distinct from R11/R12 adjudication keys unless explicitly authorized by superior governance policy;
- qualification/admission signing operations are schema- and artifact-domain-constrained.

KC1 may be used for the local PoC; KC2 is preferred for production operational authorities.

### A3/A4

Apply the stronger custody/isolation rules of the baseline Trust Root model and the Risk & Assurance Policy Model. Qualification/admission authorities do not weaken those requirements.

---

## 7. Participant Boundary

The participant subject/runtime MUST NOT possess:

```text
qualification policy key
admission policy key
R11 private key
R12 private key
Authorization Authority key
Trust Decision Authority key
Capability Executor protected-resource credentials
```

The participant may present evidence and request evaluation. It cannot issue its own controlling eligibility artifacts.

---

## 8. Revocation Registration Requirement

The Trust Root Registry and revocation plane must support suspension/revocation of:

```text
R11 authority identity/key
R12 authority identity/key
qualification/admission policy-authority keys
```

Revocation of an authority/key has the dependency effect defined by the Revocation & Trust-State amendment.

---

## 9. PoC Profile

For the first local PoC:

- use distinct deterministic signing keys for policy, R11, R12, authorization, trust decision, executor, and audit;
- keep all keys outside the synthetic participant fixture;
- use artifact-domain-constrained signing functions;
- record every issuance in the tamper-evident audit ledger;
- physical co-location on one host is permitted and explicitly classified as a development limitation.

---

## 10. Amendment Disposition

This amendment becomes controlling only when frozen together with the reconciled Agent Qualification & Admission specification set.

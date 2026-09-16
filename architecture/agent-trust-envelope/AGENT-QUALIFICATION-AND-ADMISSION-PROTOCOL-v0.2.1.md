# Agent Qualification & Admission Protocol v0.2.1

**Status:** RECONCILIATION CANDIDATE — DESIGN ONLY — NOT FROZEN  
**Architecture family:** INSA / Value Architecture / Condition of Agency / Agent Trust Envelope  
**Supersedes for current design work:** `AGENT-QUALIFICATION-AND-ADMISSION-PROTOCOL-v0.2.md`  
**Required reviews incorporated:** v0.1 adversarial review; v0.2 second adversarial review  
**Implementation authorization:** NONE

---

## 1. Purpose

This protocol defines how an AI agent or agent runtime becomes eligible to participate in a governed trust domain and to request bounded Agent Trust Envelope (ATE) authorization for a defined role.

It separates three decisions:

```text
QUALIFICATION
    = evidence-backed eligibility for a defined role

ADMISSION
    = explicit acceptance into a specific trust domain for that role

ACTION AUTHORIZATION
    = permission for one bounded governed action through ATE
```

Mandatory distinction:

```text
QUALIFIED != ADMITTED
ADMITTED != AUTHORIZED_TO_ACT
AUTHORIZED_TO_ACT requires a valid action-specific ATE path
```

QualificationCredential and AdmissionCredential are standing eligibility artifacts only. They are never resource credentials or executable capabilities.

---

## 2. Architectural Position

```text
INSA                         -> application architecture
Value Architecture           -> normative architecture
Condition of Agency          -> commitment architecture
Qualification                -> role-eligibility architecture
Admission                    -> trust-domain participation architecture
Agent Trust Envelope         -> action-specific trust architecture
Enforcement Plane            -> authority / execution architecture
Evidence + Audit             -> accountability architecture
```

Required path:

```text
Candidate Subject
    ↓
Signed Qualification Requirements Profile
    ↓
Validated Qualification Evidence
    ↓
QualificationDecision
    ↓
QualificationCredential
    ↓
Signed Admission Policy
    ↓
Validated Admission Evidence / Approvals
    ↓
AdmissionDecision
    ↓
AdmissionCredential
    ↓
Fresh session identity + COA + VA + action evidence
    ↓
CapabilityToken
    ↓
ATE verification / TrustDecision
    ↓
Final current-state verification
    ↓
Execution Authorization Point
    ↓
Capability Executor
    ↓
Protected Resource
```

Any failed prerequisite prevents the action from crossing the Execution Authorization Point.

---

## 3. Normative Security Principles

### 3.1 No permanent trust badge

Qualification is not a permanent claim that an agent is trustworthy.

It establishes only that a specifically bound subject satisfied a specifically identified profile using specifically identified evidence at a defined time for a defined role and eligibility ceiling.

### 3.2 Role-specific qualification

Qualification for one role does not imply qualification for another.

### 3.3 Domain-specific admission

Qualification does not compel admission into any trust domain.

### 3.4 Eligibility is not authority

Qualification and admission MUST NOT directly authorize:

- an operation;
- a target;
- a protected resource credential;
- an executable capability.

### 3.5 Fresh session governance remains independent

Standing qualification/admission MUST NOT replace:

- session-bound Condition of Agency acceptance where required;
- current Value Architecture policy checks;
- live runtime/session binding where required;
- action-time behavioral evidence required by the action assurance profile.

### 3.6 Current state controls

For use now, each controlling dependency must be:

```text
cryptographically valid
AND issuer-authorized
AND temporally valid
AND policy-current
AND not suspended
AND not revoked
AND not hard-superseded
AND context-compatible
AND subject-binding-valid
```

### 3.7 Fail closed

```text
UNKNOWN != QUALIFIED
UNKNOWN != ADMITTED
ERROR   != QUALIFIED
ERROR   != ADMITTED
MISSING != QUALIFIED
MISSING != ADMITTED
```

### 3.8 Credentials are immutable

QualificationCredential and AdmissionCredential are immutable signed issuance artifacts.

Lifecycle changes occur through external trust-state, revocation, expiration, and supersession mechanisms. Signed credentials are never edited in place to change status.

---

## 4. Canonical Encoding and Digest Rule

Every security-relevant artifact referenced by digest MUST use one deterministic digest rule.

Conceptually:

```text
artifact_digest = HASH(
    artifact_domain_separator
    || canonical_encode(artifact_digest_payload)
)
```

Where:

```text
artifact_digest_payload =
    artifact with its signature removed
    AND the digest field being computed removed
```

A digest field MUST NOT recursively include itself.

### 4.1 Required metadata

Every signed artifact family MUST define or inherit:

```text
schema_version
canonical_encoding_version
hash_algorithm
artifact_domain_separator
```

### 4.2 Canonical artifact digest

References such as:

```text
profile_digest
binding_digest
qualification_credential_digest
admission_credential_digest
manifest_digest
```

MUST be computed using the same canonical rule for that artifact family.

### 4.3 PoC rule

The first local PoC MUST use the canonical serialization and SHA-256 conventions already used by the local ATE harness where compatible. If the existing harness lacks a reusable canonical artifact function, one deterministic canonical JSON profile must be frozen for the PoC before test execution.

No implementation may hash ad hoc string renderings, pretty-printed JSON, mutable file formatting, or field-order-dependent encodings.

---

## 5. Authority Model

Two new logical adjudication roles are defined:

```text
R11 — Qualification Authority
R12 — Admission Authority
```

They are not operational until the Trust Root & Key Custody Model explicitly authorizes their artifact types and keys.

### 5.1 R11 — Qualification Authority

May sign, when authorized:

- QualificationDecision;
- QualificationCredential;
- qualification administrative artifacts delegated by policy.

R11 does not automatically inherit policy-authoring, trust-root, authorization, trust-decision, or executor authority.

### 5.2 R12 — Admission Authority

May sign, when authorized:

- AdmissionDecision;
- AdmissionCredential;
- admission administrative artifacts delegated by policy.

R12 does not automatically inherit policy-authoring, qualification, trust-root, authorization, trust-decision, or executor authority.

### 5.3 Policy-authoring separation

`QualificationRequirementsProfile` and `AdmissionPolicy` are policy artifacts.

They MUST be signed by a trust-domain authority explicitly authorized for those artifact types.

A valid R11 or R12 signature does not authorize policy issuance unless the Trust Root Registry separately grants that policy artifact permission.

At A2+ assurance, policy authoring and adjudication MUST be separate unless a superior signed governance policy explicitly permits concentration.

### 5.4 Signing-domain separation

At minimum:

```text
ATE_QUALIFICATION_PROFILE_V1
ATE_QUALIFICATION_DECISION_V1
ATE_QUALIFICATION_CREDENTIAL_V1
ATE_ADMISSION_POLICY_V1
ATE_ADMISSION_DECISION_V1
ATE_ADMISSION_CREDENTIAL_V1
```

A signature for one artifact domain MUST NOT verify as another artifact class.

---

## 6. Canonical Subject Binding

Every qualification/admission chain binds to a canonical `SubjectBinding`.

```text
SubjectBinding {
    subject_binding_id
    subject_identity_id

    identity_anchor {
        identity_type
        identity_key_id_or_equivalent
        issuer_authority_id
    }

    binding_level

    provider_id_optional
    model_id_optional
    runtime_build_digest_optional
    orchestration_digest_optional
    tool_manifest_digest_optional
    security_profile_digest_optional

    allowed_variance_predicates[]
    prohibited_variance_predicates[]

    binding_schema_version
    canonical_encoding_version
    hash_algorithm
    binding_digest
}
```

### 6.1 Binding levels

Conceptual baseline:

```text
SB1 — stable agent identity
SB2 — identity + runtime class/provider constraints
SB3 — identity + controlled runtime/build/security constraints
SB4 — exact high-assurance runtime/workload binding
```

The Qualification Requirements Profile MUST state the minimum required level.

### 6.2 Machine-evaluable variance only

Variance predicates MUST be canonical and machine-evaluable.

Free-form prose MUST NOT determine whether a live runtime matches a SubjectBinding.

The first PoC SHALL use an exact binding with no permitted runtime variance.

### 6.3 Live proof

At action time, the current runtime/session MUST produce evidence that satisfies the signed SubjectBinding constraints.

A copied credential without corresponding live identity/runtime proof fails.

### 6.4 Claims cannot exceed evidence

If exact provider/model/runtime provenance cannot be independently verified, the binding records only the weaker verified claim.

If the profile requires stronger provenance:

```text
QUALIFICATION_DENIED
QX_PROVENANCE_INSUFFICIENT
```

---

## 7. Qualification Requirements Profile

```text
QualificationRequirementsProfile {
    profile_id
    profile_version
    profile_digest

    qualification_domain
    role_id

    minimum_subject_binding_level

    required_identity_evidence[]
    required_provenance_evidence[]
    required_behavioral_evidence[]
    required_governance_compatibility[]
    required_operational_controls[]

    minimum_assurance_profile
    maximum_eligible_risk_level
    eligible_capability_classes[]

    evidence_freshness_rules[]
    disqualifying_conditions[]
    mandatory_requalification_triggers[]
    domain_optional_requalification_triggers[]

    qualification_validity_duration

    effective_from
    valid_until_optional
    supersession_semantics

    schema_version
    canonical_encoding_version
    hash_algorithm

    policy_authority_id
    policy_key_id
    signature
}
```

The candidate MUST NOT select, downgrade, modify, or substitute its controlling profile.

---

## 8. Qualification Evidence Validation

Each required evidence item contributes only after validating:

```text
schema/artifact class
cryptographic integrity
issuer authorization for artifact class
issuer/key currentness
artifact current trust state
freshness
subject binding
context/domain recognition
```

A digest proves immutability, not truth or authority.

Candidate self-assertion does not count as independent evidence unless the profile explicitly allows that evidence class at the required assurance level.

---

## 9. Qualification Evidence Manifest

```text
QualificationEvidenceManifest {
    manifest_id
    subject_binding_digest
    role_id

    profile_id
    profile_version
    profile_digest

    evidence_items[] {
        artifact_type
        artifact_id
        artifact_digest
        issuer_authority_id
        issuer_key_id
        issued_at
        expires_at_optional
    }

    schema_version
    canonical_encoding_version
    hash_algorithm
    manifest_digest
    created_at
}
```

QualificationDecision MUST bind `manifest_digest`.

---

## 10. Coherent Trust-State Reference

A qualification or admission decision MUST bind one coherent current-state view.

Preferred structure:

```text
TrustStateReference {
    state_view_id
    trust_state_snapshot_digest
    trust_root_registry_digest
    revocation_registry_digest
    revocation_registry_epoch
    active_policy_manifest_digest
    policy_epoch_optional
}
```

### 10.1 Atomicity rule

A decision MUST use either:

1. one authoritative signed TrustStateSnapshot that atomically commits to all controlling digests/epochs; or
2. an equivalent transactionally consistent state bundle with one authoritative `state_view_id`.

The verifier MUST NOT assemble a decision from unrelated epochs or snapshots.

Invalid examples:

```text
root state from N
revocation state from N+1
policy state from N-1
```

unless an authoritative signed snapshot explicitly defines that combination as one valid state view.

### 10.2 Inconsistent-state failure

```text
QX_TRUST_STATE_INCONSISTENT
AX_TRUST_STATE_INCONSISTENT
```

Mixed or unverifiable state views fail closed.

---

## 11. Qualification Evaluation Gates

```text
QG0  Canonicalization / schema validity
QG1  Profile signer authorization
QG2  Profile currentness
QG3  SubjectBinding validity
QG4  Evidence manifest integrity
QG5  Per-evidence issuer authorization / signature
QG6  Per-evidence current trust state
QG7  Evidence completeness
QG8  Evidence freshness
QG9  Behavioral requirements
QG10 Governance compatibility
QG11 Operational-control compatibility
QG12 Assurance / risk ceiling
QG13 Existing suspension / disqualification
QG14 Coherent TrustStateReference
QG15 Final qualification decision
```

All mandatory gates MUST pass.

---

## 12. QualificationDecision

```text
QualificationDecision {
    qualification_decision_id

    subject_binding_digest
    role_id
    qualification_domain

    profile_id
    profile_version
    profile_digest
    evidence_manifest_digest
    trust_state_reference

    verdict
    reason_code

    maximum_eligible_risk_level
    eligible_capability_classes[]

    evaluated_at

    schema_version
    canonical_encoding_version
    hash_algorithm

    qualification_authority_id
    qualification_key_id
    signature
}
```

Valid verdicts:

```text
QUALIFICATION_GRANTED
QUALIFICATION_DENIED
```

The decision is a historical signed fact. Current usability is evaluated separately.

---

## 13. QualificationCredential

Issued only from a valid `QUALIFICATION_GRANTED` decision.

```text
QualificationCredential {
    qualification_credential_id

    subject_binding_digest
    role_id
    qualification_domain

    profile_id
    profile_version
    profile_digest

    qualification_decision_id
    evidence_manifest_digest

    maximum_eligible_risk_level
    eligible_capability_classes[]

    issued_at
    valid_from
    expires_at

    schema_version
    canonical_encoding_version
    hash_algorithm

    qualification_authority_id
    qualification_key_id
    signature
}
```

Current state is external. No mutable `status` or `revocation_reference` is embedded.

---

## 14. Admission Policy

```text
AdmissionPolicy {
    admission_policy_id
    admission_policy_version
    admission_policy_digest

    trust_domain

    eligible_roles[]
    recognized_qualification_authorities[]
    recognized_qualification_domains[]
    minimum_qualification_profile_versions[]

    maximum_admission_duration
    maximum_risk_by_role[]
    eligible_capability_classes_by_role[]

    required_approval_classes[]
    prohibited_subject_conditions[]
    mandatory_readmission_triggers[]

    effective_from
    valid_until_optional
    supersession_semantics

    schema_version
    canonical_encoding_version
    hash_algorithm

    policy_authority_id
    policy_key_id
    signature
}
```

Candidate self-admission and policy self-modification are prohibited.

---

## 15. Admission Evidence Manifest

```text
AdmissionEvidenceManifest {
    manifest_id

    subject_binding_digest
    trust_domain
    role_id

    qualification_credential_id
    qualification_credential_digest

    admission_policy_id
    admission_policy_digest

    approval_items[] {
        approval_type
        approval_id
        approval_digest
        issuer_authority_id
        issuer_key_id
        issued_at
        expires_at_optional
    }

    additional_domain_evidence[]

    schema_version
    canonical_encoding_version
    hash_algorithm
    manifest_digest
    created_at
}
```

Every approval and additional domain evidence item MUST satisfy artifact-class, issuer-authority, current-state, freshness, and context rules.

---

## 16. Admission Evaluation Gates

```text
AG0  Canonicalization / schema validity
AG1  Admission-policy signer authorization
AG2  Admission-policy currentness
AG3  QualificationCredential integrity / issuer validity
AG4  Qualification currentness / dependency state
AG5  Trust-domain recognition
AG6  Exact role match
AG7  Exact SubjectBinding match
AG8  AdmissionEvidenceManifest integrity
AG9  Required approvals valid/current
AG10 Risk ceiling compatibility
AG11 Capability-class eligibility intersection
AG12 Separation-of-duties requirement
AG13 Existing suspension / incident state
AG14 Coherent TrustStateReference
AG15 Final admission decision
```

All mandatory gates MUST pass.

---

## 17. AdmissionDecision

```text
AdmissionDecision {
    admission_decision_id

    subject_binding_digest
    trust_domain
    role_id

    qualification_credential_id
    qualification_credential_digest

    admission_policy_id
    admission_policy_version
    admission_policy_digest
    admission_evidence_manifest_digest
    trust_state_reference

    verdict
    reason_code

    maximum_admitted_risk_level
    eligible_capability_classes[]

    evaluated_at

    schema_version
    canonical_encoding_version
    hash_algorithm

    admission_authority_id
    admission_key_id
    signature
}
```

Valid verdicts:

```text
ADMISSION_GRANTED
ADMISSION_DENIED
```

---

## 18. AdmissionCredential

```text
AdmissionCredential {
    admission_credential_id

    subject_binding_digest
    trust_domain
    role_id

    qualification_credential_id
    qualification_credential_digest

    admission_policy_id
    admission_policy_version
    admission_policy_digest
    admission_decision_id
    admission_evidence_manifest_digest

    maximum_admitted_risk_level
    eligible_capability_classes[]
    excluded_capability_classes[]

    issued_at
    valid_from
    expires_at
    next_review_at_optional

    schema_version
    canonical_encoding_version
    hash_algorithm

    admission_authority_id
    admission_key_id
    signature
}
```

AdmissionCredential remains an eligibility ceiling only.

---

## 19. Effective Eligibility

Effective eligibility requires:

```text
QualificationCredential usable now
AND AdmissionCredential usable now
AND exact SubjectBinding digest match
AND exact role match
AND trust-domain recognition
```

Effective risk ceiling:

```text
min(
  qualification maximum,
  admission maximum,
  role-policy maximum
)
```

Effective capability-class ceiling:

```text
intersection(
  qualification eligible classes,
  admission eligible classes,
  role-policy eligible classes
)
```

A separate least-privilege CapabilityToken remains required for protected actions.

---

## 20. Dependency Invalidation

Admission depends on the exact QualificationCredential referenced at issuance.

The admission becomes unusable for new authorization when the qualification is:

```text
SUSPENDED
REVOKED
EXPIRED
hard-SUPERSEDED
UNKNOWN
subject-binding-invalid
or invalidated by controlling issuer/key state
```

Historical artifacts remain intact.

A replacement qualification does not silently repair an old admission. Default behavior is re-admission unless a future signed continuity policy explicitly defines otherwise.

---

## 21. Mandatory ATE Dependency Binding

For every governed action whose policy requires qualification/admission, the action path MUST bind exact eligibility dependencies.

### 21.1 CapabilityToken

The signed CapabilityToken MUST bind directly or through a canonical signed constraints object:

```text
subject_binding_digest
qualification_credential_id
qualification_credential_digest
admission_credential_id
admission_credential_digest
```

Unsigned eligibility flags are prohibited.

### 21.2 ATE verifier

The verifier MUST validate:

- current qualification usability;
- current admission usability;
- live session/runtime satisfaction of SubjectBinding;
- requested risk within eligibility ceiling;
- requested capability class within eligibility intersection;
- ordinary ATE action gates.

### 21.3 TrustDecision

The signed TrustDecision MUST bind the same qualification/admission IDs/digests, the live subject/session binding reference, action digest, and the coherent trust-state view used for evaluation.

### 21.4 Executor responsibility

The executor MUST NOT trust arbitrary participant claims and MUST NOT need to re-run the full qualification evidence evaluation.

The executor may satisfy subject-binding verification by validating a current signed TrustDecision or execution capability that is cryptographically bound to:

```text
live session/runtime identity
SubjectBinding digest
action digest
qualification/admission dependencies
```

plus the executor's own final current-state checks.

---

## 22. Execution Authorization Point (EAP)

The protocol defines:

> **Execution Authorization Point (EAP):** the final serialized or authoritative point at which the Capability Executor validates current controlling trust state and irrevocably commits to attempting the protected side effect.

### 22.1 Revocation ordering guarantee

The enforceable guarantee is:

> Any revocation, suspension, expiration, or other invalidating state that is effective and observable by the authoritative trust-state system before the EAP MUST prevent the action from crossing the EAP.

The architecture does not claim that a revocation arriving after an irreversible external side effect has already crossed its commit point can retroactively undo that effect.

### 22.2 Local PoC ordering

For the local PoC, trust-state recheck/reservation and protected-resource mutation MUST be serialized under one transaction, lock, or equivalent deterministic critical section so ordering is unambiguous.

Conceptually:

```text
BEGIN SERIALIZED EXECUTION
    read current trust state
    verify dependencies
    reserve nonce/execution
    establish EAP
    perform protected local mutation
    record result
END
```

### 22.3 External side effects

For external/non-transactional effects, existing A3/A4 idempotency, no-blind-retry, and ambiguous-effect rules remain controlling.

---

## 23. Derived Expiration Rule

Downstream authorization MUST NOT outlive any controlling dependency.

```text
latest_usable_time = min(
  QualificationCredential.expires_at,
  AdmissionCredential.expires_at,
  CapabilityToken.expires_at,
  TrustDecision.expires_at,
  session/evidence freshness limits,
  other controlling dependency expirations
)
```

Issuers MUST cap downstream artifact expiry accordingly.

If an upstream dependency becomes unusable earlier because of revocation/suspension/supersession, that current-state change overrides nominal downstream expiry.

---

## 24. Action-Time Evidence Remains Independent

Standing qualification/admission does not replace fresh evidence required by the requested action's Assurance Profile.

Examples:

- qualification does not replace live provenance;
- admission does not replace current COA acceptance;
- old qualification behavioral evidence does not satisfy a fresher R4/A4 action-time requirement;
- repository-writer eligibility does not authorize any specific write.

---

## 25. Assurance-Level Separation of Duties

### A0/A1

Logical role separation MAY be sufficient where signed policy permits.

### A2

At minimum:

- participant cannot possess policy, qualification, admission, authorization, trust-decision, or executor keys;
- participant cannot access a generic signing oracle for those keys;
- distinct signing identities are required;
- executor mediation is mandatory for R2 actions.

### A3

Adds stronger process/service separation, stronger key custody, and immediate EAP current-state verification.

### A4

Adds the critical-action controls defined by the existing Risk & Assurance Policy Model, including required human/quorum controls for defined classes.

---

## 26. Requalification and Re-admission

Mandatory requalification triggers where applicable:

- qualification expiration;
- material SubjectBinding change;
- profile hard supersession;
- material binding-relevant runtime/security-boundary change;
- invalidated required evidence;
- authority/key compromise affecting issuance;
- security incident/operator directive requiring requalification.

Mandatory re-admission triggers where applicable:

- admission expiration;
- role change;
- admission-policy hard supersession;
- replacement qualification under default no-continuity semantics;
- requested risk ceiling increase;
- expanded eligibility capability class;
- incident/suspension requiring renewed approval.

Renewal creates new signed decisions and credentials. Timestamps on old credentials are never silently extended.

---

## 27. Suspension and Revocation

Required revocation target classes:

```text
qualification_credential_id
admission_credential_id
qualification_authority key
admission_authority key
qualification profile
admission policy
subject identity/binding anchor where applicable
```

Required reason-code additions include:

```text
RV_QUALIFICATION_WITHDRAWN
RV_QUALIFICATION_EVIDENCE_INVALIDATED
RV_ADMISSION_WITHDRAWN
RV_ROLE_CHANGED
RV_REQUALIFICATION_REQUIRED
RV_READMISSION_REQUIRED
```

For execution:

```text
SUSPENDED != usable
REVOKED   != usable
EXPIRED   != usable
UNKNOWN   != usable
```

The Revocation & Trust-State Model controls reinstatement semantics.

---

## 28. Threat Model

At minimum defend against:

1. self-qualification;
2. self-admission;
3. policy self-rewrite;
4. role laundering;
5. domain laundering;
6. subject/runtime substitution;
7. evidence substitution;
8. unauthorized evidence issuer;
9. stale evidence;
10. admission-as-authority;
11. stale session inheritance;
12. post-issuance revocation / TOCTOU;
13. downstream-expiry escape;
14. risk downgrade;
15. authority-role collapse;
16. approval laundering;
17. mixed-epoch trust-state assembly;
18. non-canonical digest ambiguity;
19. revocation/EAP race ambiguity.

---

## 29. Audit Requirements

Add canonical event classes:

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

Audit records should include where applicable:

```text
subject_binding_digest
qualification_credential_id/digest
admission_credential_id/digest
profile/policy digests
evidence-manifest digests
TrustStateReference
EAP state view / revocation epoch
action digest
verdict/reason code
controlling artifact hashes
```

Existing audit hash-chain, sequence, signing, and epoch rules remain controlling.

---

## 30. Reason Codes

Qualification additions/changes:

```text
QX_SCHEMA_INVALID
QX_CANONICALIZATION_INVALID
QX_DIGEST_MISMATCH
QX_UNTRUSTED_PROFILE_ISSUER
QX_PROFILE_NOT_CURRENT
QX_SUBJECT_BINDING_INVALID
QX_PROVENANCE_INSUFFICIENT
QX_EVIDENCE_MANIFEST_INVALID
QX_EVIDENCE_ISSUER_UNAUTHORIZED
QX_EVIDENCE_MISSING
QX_EVIDENCE_STALE
QX_EVIDENCE_REVOKED
QX_BEHAVIORAL_REQUIREMENT_FAILED
QX_GOVERNANCE_INCOMPATIBLE
QX_OPERATIONAL_CONTROL_INSUFFICIENT
QX_ASSURANCE_INSUFFICIENT
QX_REQUALIFICATION_REQUIRED
QX_TRUST_STATE_UNKNOWN
QX_TRUST_STATE_INCONSISTENT
QX_INTERNAL_ERROR
```

Admission additions/changes:

```text
AX_SCHEMA_INVALID
AX_CANONICALIZATION_INVALID
AX_DIGEST_MISMATCH
AX_UNTRUSTED_POLICY_ISSUER
AX_POLICY_NOT_CURRENT
AX_QUALIFICATION_INVALID
AX_QUALIFICATION_NOT_CURRENT
AX_DOMAIN_NOT_RECOGNIZED
AX_ROLE_MISMATCH
AX_SUBJECT_BINDING_MISMATCH
AX_ADMISSION_MANIFEST_INVALID
AX_REQUIRED_APPROVAL_MISSING
AX_APPROVAL_INVALID
AX_RISK_EXCEEDS_CEILING
AX_CAPABILITY_CLASS_INELIGIBLE
AX_SEPARATION_OF_DUTIES_INSUFFICIENT
AX_SUBJECT_SUSPENDED
AX_READMISSION_REQUIRED
AX_TRUST_STATE_UNKNOWN
AX_TRUST_STATE_INCONSISTENT
AX_INTERNAL_ERROR
```

Execution integration should also expose a deterministic denial code for eligibility invalidation observed before EAP.

---

## 31. Security Invariants

- **QA-INV-1:** Participant cannot qualify itself.
- **QA-INV-2:** Participant cannot admit itself.
- **QA-INV-3:** Qualification and admission policy inputs are immutable and authority-signed.
- **QA-INV-4:** All security artifact digests use deterministic canonical rules.
- **QA-INV-5:** SubjectBinding is immutable, digest-bound, and machine-evaluable.
- **QA-INV-6:** Qualification binds exact profile and evidence manifest.
- **QA-INV-7:** Admission binds exact qualification and admission evidence manifest.
- **QA-INV-8:** QualificationCredential grants no direct resource authority.
- **QA-INV-9:** AdmissionCredential grants no direct resource authority.
- **QA-INV-10:** Eligibility capability classes are ceilings only.
- **QA-INV-11:** Admission becomes unusable when its qualification dependency becomes unusable.
- **QA-INV-12:** CapabilityToken and TrustDecision bind exact eligibility dependencies.
- **QA-INV-13:** ATE decisions use one coherent trust-state view.
- **QA-INV-14:** Any invalidating state effective/observable before EAP prevents crossing EAP.
- **QA-INV-15:** Downstream nominal expiry cannot exceed upstream eligibility expiry.
- **QA-INV-16:** Standing credentials cannot replace session-local COA where required.
- **QA-INV-17:** Standing credentials cannot replace action-time assurance evidence.
- **QA-INV-18:** Valid signatures from unauthorized issuers are rejected.
- **QA-INV-19:** Evidence and approvals are digest-bound against substitution.
- **QA-INV-20:** Participant cannot widen risk or eligibility ceilings.
- **QA-INV-21:** Revoked/suspended/expired/unknown state cannot support crossing EAP.
- **QA-INV-22:** Consequential decisions and execution attempts emit durable tamper-evident audit evidence.

---

## 32. Minimal PoC Strategy

No live LLM calls are required.

Use deterministic synthetic subject fixtures represented by identity keys and runtime metadata.

### Test role

```text
role_id: demo-repository-writer
trust_domain: local-ate-demo
maximum risk: R2
eligible capability class: demo-resource-write
minimum assurance: A2
```

### Subjects

```text
Agent A fixture — intended qualified/admitted subject
Agent B fixture — control subject
```

### Authorities

Distinct signing identities/keys for:

```text
Policy Authority
Identity/Runtime Authority
Qualification Authority R11
Admission Authority R12
Authorization Authority
Trust Decision Authority
Capability Executor identity
Audit Authority
```

The PoC may run on one host, but participant fixtures MUST NOT possess authority keys or protected-resource credentials.

Reuse the P1 enforcement boundary where possible.

---

## 33. Mandatory PoC Test Matrix

### QA-P1 — Happy path

Qualification PASS; Admission PASS; Capability issuance PASS; ATE PASS; EAP PASS; protected resource changes exactly once.

### QA-P2 — Qualified, not admitted

Capability issuance DENY; resource unchanged.

### QA-P3 — Admission revoked before new capability issuance

New capability issuance DENY; resource unchanged.

### QA-P4 — Pre-issued capability after admission revocation

Issue capability; revoke admission before EAP; present capability; DENY before EAP; resource unchanged.

### QA-P5 — Pre-issued capability after qualification revocation

Issue capability; revoke qualification before EAP; DENY; resource unchanged.

### QA-P6 — Qualification expires after capability issuance

Attempt after expiry but before EAP; DENY; resource unchanged.

### QA-P7 — Credential copied to wrong subject

Agent B presents Agent A chain; SubjectBinding mismatch; DENY.

### QA-P8 — Unauthorized issuer with valid signature

Mathematically valid QualificationCredential from an unauthorized key; DENY.

### QA-P9 — Mixed trust-state view

Construct root/revocation/policy references from inconsistent epochs with no authoritative snapshot; DENY.

### QA-P10 — Digest/canonicalization substitution

Change canonical payload while preserving stale digest/signature reference; digest or signature validation fails; DENY.

### QA-P11 — Deterministic revocation/EAP ordering

Case A:

```text
revocation committed before EAP -> DENY
```

Case B:

```text
EAP committed before later revocation -> local transaction completes according to already-established EAP ordering
```

Audit must make the ordering reconstructable.

### QA-P12 — Direct protected-resource bypass

Attempt direct mutation outside Capability Executor; OS/resource boundary DENY. Any success classifies the PoC as enforcement failure.

---

## 34. PoC Success Criteria

All must hold:

1. signed role profile controls qualification;
2. qualification alone cannot execute;
3. admission requires exact usable qualification;
4. admission alone cannot execute;
5. SubjectBinding prevents credential transplant;
6. policy/evidence issuers are authority-checked;
7. canonical digest rules are deterministic;
8. qualification/admission dependencies are bound into CapabilityToken and TrustDecision;
9. mixed trust-state epochs are rejected;
10. revocation effective before EAP blocks execution;
11. upstream expiry before EAP blocks execution;
12. EAP ordering is deterministic and auditable;
13. executor does not re-run qualification but verifies signed bound dependencies/current state;
14. direct resource bypass is impossible under the PoC boundary;
15. every decision and attempted execution emits durable tamper-evident evidence.

---

## 35. Required Cross-Specification Amendments Before Freeze

The following reconciliations are mandatory before this protocol can be frozen:

### 35.1 Trust Root & Key Custody Model

Add/confirm:

- R11 Qualification Authority;
- R12 Admission Authority;
- policy-artifact permissions for QualificationRequirementsProfile and AdmissionPolicy;
- artifact-domain separators;
- assurance-level custody/separation expectations.

### 35.2 Revocation & Trust-State Model

Add:

- QualificationCredential and AdmissionCredential target classes;
- qualification/admission authority key targets;
- profile/policy invalidation semantics;
- coherent trust-state snapshot requirement;
- EAP ordering semantics;
- dependency invalidation rules.

### 35.3 ATE Production Architecture

Add mandatory signed qualification/admission dependency IDs/digests to the authorization/trust-decision path, directly or via one canonical signed extension.

Define EAP in the execution flow.

### 35.4 Risk & Assurance Policy Model

Add qualification/admission control expectations by A0-A4 where necessary, without duplicating action-time evidence rules.

### 35.5 Audit & Accountability Model

Add qualification/admission event classes, dependency identifiers/digests, coherent TrustStateReference, and EAP audit semantics.

---

## 36. Correct Freeze and Implementation Order

The controlling order is:

```text
v0.2.1 reconciliation candidate
-> cross-specification amendments
-> reconciliation review of the document set
-> correct any inconsistency
-> freeze protocol + required amendments together
-> authorize tiny synthetic local PoC
-> deterministic implementation/tests
-> closeout
```

No Hermes implementation task is authorized before the reconciled specification set is frozen.

---

## 37. Freeze Gates

```text
FG1  no unresolved critical/high finding in v0.2.1
FG2  canonical digest semantics reconciled with ATE core
FG3  coherent TrustStateReference reconciled with revocation model
FG4  EAP semantics reconciled with enforcement/revocation architecture
FG5  SubjectBinding semantics accepted
FG6  R11/R12 trust-root permissions added
FG7  qualification/admission revocation targets added
FG8  mandatory ATE dependency binding added
FG9  audit event/EAP semantics added
FG10 PoC test matrix frozen
FG11 reconciled files reviewed for contradiction
FG12 no implementation started against superseded v0.1/v0.2 semantics
```

---

## 38. Candidate Disposition

```text
Version:                     v0.2.1
Status:                      RECONCILIATION CANDIDATE / NOT FROZEN
v0.1 major defects:          CORRECTED
v0.2 second-pass defects:    CORRECTED IN THIS CANDIDATE
Implementation authorized:   NO
Hermes required now:         NO
Next required work:          MINIMAL CROSS-SPEC AMENDMENTS
```

The architecture should remain in ChatGPT design/reconciliation work until the five dependent ATE specifications are updated and reviewed as one coherent set.

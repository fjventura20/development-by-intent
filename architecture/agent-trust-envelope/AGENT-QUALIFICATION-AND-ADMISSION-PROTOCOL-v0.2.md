# Agent Qualification & Admission Protocol v0.2

**Status:** FROZEN CANDIDATE — DESIGN ONLY  
**Architecture family:** INSA / Value Architecture / Condition of Agency / Agent Trust Envelope  
**Supersedes for design review:** `AGENT-QUALIFICATION-AND-ADMISSION-PROTOCOL-v0.1.md`  
**Required prior review:** `AGENT-QUALIFICATION-AND-ADMISSION-PROTOCOL-v0.1-ADVERSARIAL-REVIEW.md`  
**Implementation authorization:** NONE — one additional adversarial review is required before freeze

---

## 1. Purpose

This protocol defines how an AI agent or agent runtime becomes eligible to participate in a governed trust domain and to request bounded Agent Trust Envelope (ATE) authorization for a defined role.

It separates three decisions that MUST remain distinct:

```text
QUALIFICATION
    = evidence-backed eligibility for a defined role

ADMISSION
    = explicit acceptance into a specific trust domain for that role

ACTION AUTHORIZATION
    = permission for one bounded governed action through ATE
```

The controlling rule is:

```text
QUALIFIED != ADMITTED
ADMITTED != AUTHORIZED_TO_ACT
AUTHORIZED_TO_ACT requires a valid action-specific ATE path
```

Neither a QualificationCredential nor an AdmissionCredential is a resource credential or standing execution capability.

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
Final current-state recheck
    ↓
Capability Executor
    ↓
Protected Resource
```

Any failed prerequisite prevents protected execution.

---

## 3. Normative Security Principles

### 3.1 No permanent trust badge

Qualification is not a permanent statement that an agent is trustworthy.

It means only that a specifically bound subject satisfied a specific requirements profile using specific evidence at a specific time for a specific role and assurance/risk ceiling.

### 3.2 Role-specific qualification

Qualification for one role MUST NOT imply qualification for another.

```text
qualified: documentation-reader
!=
qualified: repository-writer
!=
qualified: production-deployer
```

### 3.3 Domain-specific admission

Qualification does not force any trust domain to admit the subject.

Admission is an explicit domain decision.

### 3.4 Eligibility is not authority

Qualification and admission establish only an eligibility ceiling.

They MUST NOT directly authorize:

- an operation;
- a target;
- a protected resource credential;
- an executable capability.

### 3.5 Fresh session governance remains mandatory

Standing qualification/admission MUST NOT replace session-bound Condition of Agency acceptance when COA is required.

Standing qualification/admission MUST NOT replace current Value Architecture policy evaluation.

### 3.6 Current state controls

For use now, every controlling dependency must be:

```text
cryptographically valid
AND issuer-authorized
AND temporally valid
AND policy-current
AND not suspended
AND not revoked
AND not superseded where supersession is hard-invalidating
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

### 3.8 Immutable credentials; mutable state is external

QualificationCredential and AdmissionCredential are immutable signed issuance artifacts.

Post-issuance lifecycle state MUST be obtained from current trust-state/revocation mechanisms. A credential is never edited in place to change `status`.

---

## 4. Non-Goals

v0.2 does not define:

- a universal reputation score;
- a global AI certification authority;
- a permanent safety or moral classification;
- Internet-scale federation;
- a provider-specific hardware-attestation scheme;
- a production PKI product;
- autonomous privilege growth based on past behavior;
- a substitute for ATE action authorization;
- a substitute for session-bound COA or current VA checks.

The first PoC is intentionally local and synthetic.

---

## 5. Authority Model

This protocol defines two new logical adjudication roles:

```text
R11 — Qualification Authority
R12 — Admission Authority
```

These role identifiers are not operational until the Trust Root & Key Custody Model explicitly registers them and their artifact permissions.

### 5.1 R11 — Qualification Authority

R11 MAY sign only artifacts explicitly authorized by the Trust Root Registry, including:

- QualificationDecision;
- QualificationCredential;
- qualification-related administrative records where delegated.

R11 MUST NOT automatically inherit:

- Trust Root Authority;
- requirements-profile policy authority;
- VA Policy Authority;
- Authorization Authority;
- Trust Decision Authority;
- Capability Executor credentials.

### 5.2 R12 — Admission Authority

R12 MAY sign only artifacts explicitly authorized by the Trust Root Registry, including:

- AdmissionDecision;
- AdmissionCredential;
- admission-related administrative records where delegated.

R12 MUST NOT automatically inherit:

- Trust Root Authority;
- admission-policy authoring authority;
- Qualification Authority;
- Authorization Authority;
- Trust Decision Authority;
- protected resource credentials.

### 5.3 Policy-authoring separation

`QualificationRequirementsProfile` and `AdmissionPolicy` are policy artifacts.

They MUST be signed by a trust-domain authority explicitly authorized for those policy artifact types.

A cryptographically valid R11 or R12 signature is insufficient unless the Trust Root Registry separately authorizes that authority to issue the relevant policy artifact.

At A2+ assurance, policy authoring and adjudication MUST be distinct unless a higher-level signed policy explicitly authorizes role concentration.

### 5.4 Artifact signing domains

Signing services MUST use artifact-domain separation, for example:

```text
ATE_QUALIFICATION_PROFILE_V1
ATE_QUALIFICATION_DECISION_V1
ATE_QUALIFICATION_CREDENTIAL_V1
ATE_ADMISSION_POLICY_V1
ATE_ADMISSION_DECISION_V1
ATE_ADMISSION_CREDENTIAL_V1
```

A signature valid for one domain MUST NOT verify as another artifact class.

---

## 6. Canonical Subject Binding

The v0.1 field `subject_identity` is insufficient by itself.

Every qualification/admission chain MUST bind to a canonical `SubjectBinding`.

Conceptual structure:

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

    allowed_variance[]
    prohibited_variance[]

    binding_schema_version
    binding_digest
}
```

### 6.1 Binding levels

A qualification profile MUST state the minimum binding level it requires.

Example conceptual levels:

```text
SB1 — stable agent identity
SB2 — identity + runtime class/provider constraints
SB3 — identity + controlled runtime/build/security constraints
SB4 — exact high-assurance runtime/workload binding where required
```

The exact production taxonomy may evolve, but the profile must never leave the required binding strength implicit.

### 6.2 Live proof requirement

At authorization/action time, the current session/runtime MUST prove that it satisfies the credential's `subject_binding_digest` and constraints.

A copied credential without the corresponding live identity/runtime binding MUST fail.

### 6.3 Claims cannot exceed evidence

If exact provider/model/runtime provenance cannot be verified, the SubjectBinding MUST record only the weaker verified claim.

If the role profile requires stronger provenance than can be verified:

```text
QUALIFICATION_DENIED
QX_PROVENANCE_INSUFFICIENT
```

---

## 7. Qualification Requirements Profile

Every qualification decision MUST use an explicit, versioned, signed, current profile.

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

    policy_authority_id
    policy_key_id
    signature
}
```

The candidate MUST NOT select, downgrade, rewrite, or substitute its own qualification profile.

---

## 8. Qualification Evidence Validation

Evidence contributes to qualification only after validation.

Every required evidence item MUST pass:

```text
artifact schema valid
AND artifact type expected
AND signature/integrity valid
AND issuer authorized for artifact type
AND issuer/key current
AND artifact not suspended/revoked
AND freshness requirement satisfied
AND subject binding satisfied
AND context/domain recognition satisfied
```

A digest proves immutability, not authority or truth.

Candidate-generated self-assertion MUST NOT be treated as independent evidence unless the profile explicitly permits that evidence class at the required assurance level.

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

    manifest_digest
    created_at
}
```

The QualificationDecision MUST bind `manifest_digest`.

Mix-and-match evidence substitution after evaluation is prohibited.

---

## 10. Trust-State Reference

Qualification and admission decisions MUST record the current-state view under which they were made.

Preferred binding:

```text
TrustStateReference {
    trust_state_snapshot_digest
    trust_root_registry_digest
    revocation_registry_digest
    revocation_registry_epoch
    active_policy_manifest_digest
    policy_epoch_optional
}
```

A deployment MAY omit redundant fields when a signed TrustStateSnapshot already commits to them, but the decision must retain enough information for deterministic reconstruction.

---

## 11. Qualification Evaluation Gates

Required sequence:

```text
QG0  Canonicalization / schema validity
QG1  Profile signer authorization
QG2  Profile currentness
QG3  SubjectBinding validity
QG4  Evidence manifest integrity
QG5  Per-evidence issuer authorization and signature
QG6  Per-evidence current trust state
QG7  Evidence completeness
QG8  Evidence freshness
QG9  Behavioral requirements
QG10 Governance compatibility
QG11 Operational-control compatibility
QG12 Assurance / risk ceiling
QG13 Existing suspension / disqualification state
QG14 Trust-state snapshot binding
QG15 Final qualification decision
```

All mandatory gates MUST pass.

Unknown/internal-error state fails closed.

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

A decision is a historical signed fact. Current usability is evaluated separately.

---

## 13. QualificationCredential

A QualificationCredential MAY be issued only from a valid `QUALIFICATION_GRANTED` decision.

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

    qualification_authority_id
    qualification_key_id
    signature
}
```

The credential contains no mutable `status` or `revocation_reference` field.

Current state is resolved externally from validity, current policy/profile state, revocation, and dependency state.

---

## 14. Admission Policy

Each trust domain controls admission independently.

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

    policy_authority_id
    policy_key_id
    signature
}
```

The candidate MUST NOT admit itself or modify the policy used to evaluate its admission.

---

## 15. Admission Evidence Manifest

Admission MUST bind the exact qualification and approval evidence that justified the decision.

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
        issued_at
        expires_at_optional
    }

    additional_domain_evidence[]

    manifest_digest
    created_at
}
```

Every approval item MUST independently satisfy issuer authorization, current-state, freshness, subject/context binding, and policy requirements.

---

## 16. Admission Evaluation Gates

Required sequence:

```text
AG0  Canonicalization / schema validity
AG1  Admission-policy signer authorization
AG2  Admission-policy currentness
AG3  QualificationCredential signature/issuer validity
AG4  Qualification currentness / dependency state
AG5  Trust-domain recognition
AG6  Exact role match
AG7  Exact SubjectBinding match
AG8  AdmissionEvidenceManifest integrity
AG9  Required approvals valid/current
AG10 Risk ceiling compatibility
AG11 Eligibility-capability intersection
AG12 Separation-of-duties requirement
AG13 Existing suspension / incident state
AG14 Trust-state snapshot binding
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

    admission_authority_id
    admission_key_id
    signature
}
```

The credential contains no mutable lifecycle state.

AdmissionCredential is an eligibility ceiling, never direct authorization.

---

## 19. Effective Eligibility

Effective eligibility exists only when:

```text
qualification usable now
AND admission usable now
AND qualification.subject_binding_digest == admission.subject_binding_digest
AND role matches
AND trust-domain policy recognizes the chain
```

Effective risk ceiling:

```text
min(
  qualification maximum risk,
  admission maximum risk,
  role-policy maximum risk
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

An eligibility ceiling does not grant an action.

---

## 20. Dependency Invalidation

Admission depends on the exact QualificationCredential referenced at issuance.

The following make the dependent admission unusable for new authorization:

```text
qualification suspended
qualification revoked
qualification expired
qualification hard-superseded
qualification issuer/key invalidated where policy makes downstream artifacts unusable
qualification subject binding no longer satisfied
qualification state unknown
```

Historical artifacts remain intact for audit.

A replacement qualification does not silently repair an existing admission unless policy explicitly defines a signed continuity mechanism. Default behavior is re-admission.

---

## 21. Mandatory ATE Dependency Binding

This is a normative change from v0.1.

For every governed action whose policy requires qualification/admission, the action path MUST bind the exact eligibility dependencies.

### 21.1 CapabilityToken

The signed CapabilityToken MUST bind, directly or through a signed canonical constraints object:

```text
subject_binding_digest
qualification_credential_id
qualification_credential_digest
admission_credential_id
admission_credential_digest
```

No unsigned side-channel flag may substitute.

### 21.2 ATE verification

The verifier MUST validate:

- current QualificationCredential usability;
- current AdmissionCredential usability;
- exact SubjectBinding match to live session/runtime;
- action risk within eligibility ceiling;
- requested capability class within eligibility intersection;
- all ordinary ATE evidence/gates.

### 21.3 TrustDecision

The signed TrustDecision MUST bind the same qualification/admission dependency identifiers/digests and the trust-state epoch/snapshot used for evaluation.

### 21.4 Capability Executor final recheck

Immediately before protected execution, the executor MUST recheck current trust state for at least:

```text
subject identity / live binding
QualificationCredential
AdmissionCredential
CapabilityToken
TrustDecision
relevant signing authorities/keys
```

For R2+ governed actions this recheck is mandatory. Lower-risk deployments may use the same rule universally.

A TrustDecision created before a later revocation does not override newer revocation state.

---

## 22. Derived Expiration Rule

No downstream authorization may outlive a controlling eligibility dependency.

For an action requiring qualification/admission:

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

Issuers MUST cap newly created downstream artifact expiry accordingly.

If a dependency expires earlier than a previously issued downstream artifact, the downstream artifact becomes unusable at the dependency boundary.

---

## 23. Action-Time Evidence Remains Independent

Qualification evidence does not automatically satisfy action-time evidence.

Examples:

- a seven-day QualificationCredential does not replace live session provenance;
- standing admission does not replace current COA acceptance;
- a behavioral evaluation used for qualification yesterday does not satisfy an R4/A4 action requiring evidence less than one hour old;
- a repository-writer admission does not authorize any particular write.

The Assurance Profile for the requested action controls freshness and additional evidence.

---

## 24. Assurance-Level Separation of Duties

Qualification/admission authority topology MUST align with the existing Risk & Assurance Policy Model.

### A0/A1

Logical role separation MAY be sufficient where signed domain policy explicitly permits it.

### A2

Required minimum:

- candidate cannot possess policy, qualification, admission, trust-decision, or executor keys;
- candidate cannot invoke a generic signing oracle for those keys;
- distinct signing identities are required;
- executor mediation remains mandatory for R2 actions.

### A3

Includes A2 plus stronger process/service separation, stronger key custody, and immediate execution-time current-state checks.

### A4

Includes A3 plus the critical-action requirements of the existing A4 assurance profile, including stronger authority/quorum/human controls where applicable.

Physical co-location never converts one role into another. Artifact permissions remain distinct.

---

## 25. Requalification Triggers

Mandatory baseline triggers where applicable:

- credential expiration;
- material SubjectBinding change;
- controlling profile hard supersession;
- material runtime/security-boundary change when binding-relevant;
- invalidation of required qualification evidence;
- qualification authority/key compromise affecting trust in issuance;
- security incident or operator suspension requiring requalification.

Domain-policy optional triggers may include:

- orchestration change;
- material tool-set expansion;
- role-specific repeated policy failures;
- scheduled review interval;
- provider/model changes not already captured by mandatory binding rules.

A trigger means prior evidence is no longer sufficient. It does not itself assert misconduct.

---

## 26. Re-admission Triggers

Baseline triggers:

- AdmissionCredential expiration;
- role change;
- trust-domain policy hard supersession;
- replacement qualification credential under default no-continuity semantics;
- requested risk ceiling increase;
- expanded eligibility capability class;
- incident/suspension requiring renewed approval;
- change in required approval authority.

Renewal MUST create a new signed AdmissionDecision and AdmissionCredential.

---

## 27. Suspension and Revocation

Qualification/admission artifacts MUST integrate with the ATE Revocation & Trust-State Model.

Required revocation target classes:

```text
qualification_credential_id
admission_credential_id
qualification_authority key
admission_authority key
qualification requirements profile
admission policy
subject identity / binding anchor where applicable
```

Required reason-code additions include at least:

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

Reinstatement is allowed only when the Revocation & Trust-State policy explicitly permits it for that artifact class.

---

## 28. Threat Model

The protocol MUST defend against at least:

### T1 — Self-qualification
Candidate issues its own qualification.

### T2 — Self-admission
Candidate admits itself.

### T3 — Policy self-rewrite
Evaluator or candidate silently changes requirements during adjudication.

### T4 — Role laundering
Low-risk role credential reused for higher role.

### T5 — Domain laundering
Credential from one domain reused without recognition policy.

### T6 — Runtime/subject substitution
Different subject/runtime uses another credential.

### T7 — Evidence substitution
Evidence changes after evaluation.

### T8 — Unauthorized evidence issuer
Valid signature from an issuer not authorized for that evidence type.

### T9 — Stale evidence
Expired or freshness-invalid evidence supports qualification.

### T10 — Admission-as-authority
Admission is treated as a standing write/execute token.

### T11 — Session inheritance
New session reuses stale COA/session commitment.

### T12 — TOCTOU revocation
Capability issued before qualification/admission revocation is used afterward.

### T13 — Dependency-expiry escape
Downstream token outlives upstream eligibility.

### T14 — Risk downgrade
Participant chooses a lower risk classification.

### T15 — Authority-role collapse
One compromised operational service can redefine policy, qualify, admit, authorize, decide trust, and execute.

### T16 — Approval laundering
Admission decision claims approval not bound to the exact signed approval artifact.

---

## 29. Audit Requirements

Qualification/admission events are consequential trust-state transitions and MUST produce durable, tamper-evident audit evidence external to participant control.

Add canonical event classes such as:

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
```

Audit records SHOULD include where applicable:

```text
subject_binding_digest
qualification_credential_id
admission_credential_id
profile/policy digests
evidence-manifest digests
TrustStateReference
verdict / reason code
controlling artifact hashes
```

The existing ATE Audit & Accountability hash-chain, sequence, signing, and epoch rules remain controlling.

---

## 30. Reason Codes

Qualification reason taxonomy:

```text
QX_SCHEMA_INVALID
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
QX_INTERNAL_ERROR
```

Admission reason taxonomy:

```text
AX_SCHEMA_INVALID
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
AX_INTERNAL_ERROR
```

Unknown/internal error fails closed.

---

## 31. Security Invariants

- **QA-INV-1:** Participant cannot qualify itself.
- **QA-INV-2:** Participant cannot admit itself.
- **QA-INV-3:** Qualification profile is policy-controlled and immutable for an evaluation.
- **QA-INV-4:** Admission policy is domain-controlled and immutable for an evaluation.
- **QA-INV-5:** Qualification binds an immutable SubjectBinding digest.
- **QA-INV-6:** Admission binds the same SubjectBinding digest and exact qualification credential.
- **QA-INV-7:** QualificationCredential grants no direct resource authority.
- **QA-INV-8:** AdmissionCredential grants no direct resource authority.
- **QA-INV-9:** Eligibility capability classes are ceilings only.
- **QA-INV-10:** Admission cannot remain usable when its qualification dependency becomes unusable.
- **QA-INV-11:** CapabilityToken and TrustDecision bind exact qualification/admission dependencies when policy requires them.
- **QA-INV-12:** Final protected execution rechecks current dependency state.
- **QA-INV-13:** Downstream validity cannot exceed the earliest controlling dependency validity.
- **QA-INV-14:** Standing credentials cannot replace session-local COA when required.
- **QA-INV-15:** Standing credentials cannot replace action-time assurance evidence.
- **QA-INV-16:** Valid signatures from unauthorized issuers are rejected.
- **QA-INV-17:** Evidence and approval inputs are digest-bound against substitution.
- **QA-INV-18:** Participant cannot widen risk or capability eligibility ceilings.
- **QA-INV-19:** Revoked/suspended/expired/unknown controlling state cannot support execution.
- **QA-INV-20:** Every consequential decision emits durable tamper-evident audit evidence.

---

## 32. Minimal PoC Strategy

The first PoC MUST remain deterministic and local.

No live LLM calls are required.

Use synthetic subjects represented by deterministic identity keys and runtime metadata fixtures. This isolates the architecture and avoids subscription/token cost.

### 32.1 Test role

```text
role_id: demo-repository-writer
trust_domain: local-ate-demo
maximum risk: R2
eligible capability class: demo-resource-write
minimum assurance: A2
```

### 32.2 Synthetic subjects

```text
Agent A fixture — intended qualified/admitted subject
Agent B fixture — control subject
```

### 32.3 Local authority identities

Use distinct signing keys/logical services for:

```text
Policy Authority
Identity/Runtime Authority
Qualification Authority (R11)
Admission Authority (R12)
Authorization Authority
Trust Decision Authority
Capability Executor identity
Audit Authority
```

For the PoC these may share one physical host, but keys MUST remain distinct and the candidate fixture MUST not possess authority keys or protected resource credentials.

Where practical, reuse the P1 enforcement boundary rather than rebuilding it.

---

## 33. Mandatory PoC Test Matrix

### QA-P1 — Happy path

```text
Qualification PASS
Admission PASS
Capability issuance PASS
ATE TrustDecision PASS
Final dependency recheck PASS
Executor operation PASS
```

Protected demo resource changes exactly once.

### QA-P2 — Qualified, not admitted

```text
Qualification PASS
Admission absent/denied
Capability issuance DENY
Protected resource unchanged
```

### QA-P3 — Admission revoked before new capability issuance

```text
Qualification ACTIVE
Admission previously ACTIVE then REVOKED
New capability issuance DENY
Protected resource unchanged
```

### QA-P4 — Already-issued capability after admission revocation

Sequence:

```text
Qualification ACTIVE
Admission ACTIVE
CapabilityToken issued
Admission REVOKED
Present pre-revocation CapabilityToken
```

Expected:

```text
ATE validation or final executor recheck DENY
Protected resource unchanged
```

### QA-P5 — Already-issued capability after qualification revocation

Same as QA-P4, but revoke QualificationCredential.

Expected: DENY; resource unchanged.

### QA-P6 — Qualification expires after capability issuance

Issue capability before qualification expiry; attempt execution after qualification expiry.

Expected: DENY; resource unchanged.

### QA-P7 — Credential copied to wrong subject

Agent B presents Agent A qualification/admission chain.

Expected:

```text
SubjectBinding mismatch
DENY
Protected resource unchanged
```

### QA-P8 — Unauthorized issuer with valid cryptographic signature

Create a mathematically valid QualificationCredential from a key not authorized for that artifact type.

Expected:

```text
QX/AX untrusted issuer path
DENY
Protected resource unchanged
```

### QA-P9 — Direct protected-resource bypass

Candidate attempts modification outside Capability Executor.

Expected:

```text
OS/resource boundary DENY
Protected resource unchanged
```

If bypass succeeds, PoC classification is enforcement failure regardless of all other results.

---

## 34. PoC Success Criteria

PoC succeeds only if all of the following are established:

1. qualification can be issued under a frozen signed role profile;
2. qualification alone cannot execute;
3. admission requires a valid exact qualification chain;
4. admission alone cannot execute;
5. SubjectBinding prevents credential transplant;
6. policy/evidence issuers are checked for authority, not only signature validity;
7. capability issuance binds qualification/admission dependencies;
8. TrustDecision binds those dependencies;
9. revocation after capability issuance prevents execution;
10. qualification expiry after capability issuance prevents execution;
11. final executor recheck observes current trust state;
12. candidate cannot directly bypass the executor;
13. every decision and attempted execution emits durable tamper-evident evidence.

A successful PoC establishes only the narrow architecture claim that governed systems can enforce qualification and explicit domain admission as revocable prerequisites to bounded action authorization.

It does not establish general AI safety, permanent trustworthiness, global federation, or protection against host-root compromise.

---

## 35. Required Cross-Specification Integration Before Freeze

The v0.2 protocol cannot become implementation-frozen until the following are reconciled:

### 35.1 Trust Root & Key Custody Model

Add or confirm:

- R11 Qualification Authority;
- R12 Admission Authority;
- policy-artifact authority for QualificationRequirementsProfile and AdmissionPolicy;
- permitted artifact types;
- signing-domain separation;
- custody requirements by assurance profile.

### 35.2 Revocation & Trust-State Model

Add:

- QualificationCredential and AdmissionCredential target types;
- qualification/admission authority key targets;
- profile/policy invalidation semantics;
- revocation authority scope;
- dependency invalidation and final-execution recheck semantics.

### 35.3 ATE Production Architecture

Make qualification/admission dependency IDs/digests first-class signed authorization/trust-decision inputs or define a canonical signed extension that is mandatory and equivalent.

### 35.4 Risk & Assurance Policy Model

Define minimum qualification/admission evidence and authority separation by A0-A4 where not already implied.

### 35.5 Audit & Accountability Model

Add the qualification/admission event classes and canonical dependency identifiers.

---

## 36. Freeze Gates

The following gates must all pass before implementation authorization:

```text
FG1  second adversarial review finds no unresolved critical/high defect
FG2  SubjectBinding semantics accepted
FG3  mandatory ATE dependency binding accepted
FG4  execution-time recheck accepted
FG5  downstream expiry rule accepted
FG6  R11/R12 trust-root integration specified
FG7  qualification/admission revocation integration specified
FG8  audit event integration specified
FG9  PoC test matrix frozen
FG10 no implementation work started against superseded v0.1 semantics
```

---

## 37. Implementation Discipline

Required order:

```text
v0.2 frozen candidate
-> second adversarial review
-> corrections if any
-> freeze
-> minimal cross-spec amendments
-> tiny synthetic local PoC
-> deterministic tests
-> closeout
```

Do not begin with:

- live premium multi-agent runs;
- large behavioral benchmarks;
- external federation;
- broad deployment;
- dashboards;
- production PKI selection;
- large role taxonomies.

The first experiment is an enforcement-architecture experiment, not a model-quality experiment.

---

## 38. Candidate Disposition

```text
Version:                     v0.2
Status:                      FROZEN CANDIDATE / NOT YET FROZEN
v0.1 central concept:        PRESERVED
v0.1 security gaps:          CORRECTED IN CANDIDATE
Implementation authorized:   NO
Next required step:          SECOND ADVERSARIAL DESIGN REVIEW
Hermes required now:         NO
```

The next decision is whether this v0.2 candidate survives a second adversarial pass without unresolved critical or high-severity defects.

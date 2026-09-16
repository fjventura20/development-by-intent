# Agent Qualification & Admission Protocol v0.2.2

**Status:** FINAL FREEZE CANDIDATE — DESIGN ONLY — NOT YET FROZEN  
**Architecture family:** INSA / Value Architecture / Condition of Agency / Agent Trust Envelope  
**Supersedes for current design work:** `AGENT-QUALIFICATION-AND-ADMISSION-PROTOCOL-v0.2.1.md`  
**Reviews incorporated:** v0.1 adversarial review; v0.2 second adversarial review; cross-spec reconciliation review v0.1  
**Implementation authorization:** NONE until freeze manifest is committed

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

1. **No permanent trust badge.** Qualification is a bounded evidence-backed role-eligibility statement, not a permanent declaration of trustworthiness.
2. **Qualification is role-specific.** Qualification for one role does not imply qualification for another.
3. **Admission is domain-specific.** Qualification does not compel admission into a trust domain.
4. **Eligibility is not authority.** Qualification/admission do not directly authorize operations, targets, credentials, or executable capabilities.
5. **Fresh session governance remains independent.** Standing credentials do not replace session-bound COA, current VA checks, live runtime/session binding, or risk-required action-time evidence.
6. **Current state controls.** Historical validity is insufficient.
7. **Fail closed.** Unknown, missing, malformed, inconsistent, suspended, revoked, expired, or unauthorized prerequisites do not support execution.
8. **Credentials are immutable.** Lifecycle state is external; signed credentials are never edited in place.

Usability requires:

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

---

## 4. Canonical Encoding and Digest Rule

Every security-relevant artifact referenced by digest MUST use one deterministic digest rule.

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

Every signed artifact family defines or inherits:

```text
schema_version
canonical_encoding_version
hash_algorithm
artifact_domain_separator
```

References including `profile_digest`, `binding_digest`, `qualification_credential_digest`, `admission_credential_digest`, and manifest digests use this canonical rule.

The first PoC must freeze one deterministic canonical encoding and SHA-256 profile before formal test execution; ad hoc string or presentation-form hashing is prohibited.

---

## 5. Authority Model

Two logical adjudication roles are defined:

```text
R11 — Qualification Authority
R12 — Admission Authority
```

They are operational only when the Trust Root Registry explicitly authorizes their artifact types and keys.

### R11

May sign authorized QualificationDecision and QualificationCredential artifacts. R11 does not automatically inherit policy-authoring, trust-root, authorization, trust-decision, or executor authority.

### R12

May sign authorized AdmissionDecision and AdmissionCredential artifacts. R12 does not automatically inherit policy-authoring, qualification, trust-root, authorization, trust-decision, or executor authority.

### Policy-authoring separation

`QualificationRequirementsProfile` and `AdmissionPolicy` are policy artifacts and MUST be signed by an authority explicitly authorized for those artifact types.

At A2+ assurance, policy authoring and adjudication MUST be separate unless superior signed governance policy explicitly permits concentration.

### Signing-domain separation

At minimum:

```text
ATE_QUALIFICATION_PROFILE_V1
ATE_QUALIFICATION_DECISION_V1
ATE_QUALIFICATION_CREDENTIAL_V1
ATE_ADMISSION_POLICY_V1
ATE_ADMISSION_DECISION_V1
ATE_ADMISSION_CREDENTIAL_V1
```

A signature for one domain MUST NOT verify as another artifact class.

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

Conceptual binding levels:

```text
SB1 — stable agent identity
SB2 — identity + runtime class/provider constraints
SB3 — identity + controlled runtime/build/security constraints
SB4 — exact high-assurance runtime/workload binding
```

Variance predicates MUST be canonical and machine-evaluable. Free-form prose cannot determine a match. The first PoC uses exact binding with no runtime variance.

At action time, current runtime/session evidence must satisfy the signed SubjectBinding. A copied credential without corresponding live proof fails.

Claims cannot exceed evidence. If a profile requires stronger provenance than can be independently established:

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

The candidate cannot select, downgrade, modify, or substitute its controlling profile.

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

Candidate self-assertion is not independent evidence unless the profile explicitly allows that evidence class at the required assurance level.

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

QualificationDecision binds the exact `manifest_digest`.

---

## 10. Coherent Trust-State Reference

Qualification and admission decisions MUST bind one coherent current-state view.

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

A decision uses either one authoritative signed TrustStateSnapshot that commits to all controlling state, or an equivalent transactionally consistent state bundle with one authoritative `state_view_id`.

Mixed-epoch assembly is invalid unless an authoritative signed state view explicitly defines that combination.

Failures:

```text
QX_TRUST_STATE_INCONSISTENT
AX_TRUST_STATE_INCONSISTENT
```

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

All mandatory gates pass or qualification is denied.

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

Verdicts:

```text
QUALIFICATION_GRANTED
QUALIFICATION_DENIED
```

A decision is historical evidence; current usability is evaluated separately.

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

No mutable lifecycle fields are embedded.

---

## 14. Admission Policy

Admission policy MUST explicitly recognize the qualification profiles it accepts. It MUST NOT automatically trust unknown future profile versions merely because their version number is higher.

```text
AdmissionPolicy {
    admission_policy_id
    admission_policy_version
    admission_policy_digest

    trust_domain

    eligible_roles[]
    recognized_qualification_authorities[]
    recognized_qualification_domains[]

    recognized_qualification_profiles[] {
        profile_id
        allowed_version_or_digest_constraints[]
    }

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

Unknown or unrecognized qualification profile versions/digests fail closed until AdmissionPolicy is explicitly updated.

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

Every approval/additional evidence item must satisfy artifact-class, issuer-authority, current-state, freshness, and context requirements.

---

## 16. Admission Evaluation Gates

```text
AG0  Canonicalization / schema validity
AG1  Admission-policy signer authorization
AG2  Admission-policy currentness
AG3  QualificationCredential integrity / issuer validity
AG4  Qualification currentness / dependency state
AG5  Trust-domain recognition
AG6  Qualification profile/version/digest explicitly recognized
AG7  Exact role match
AG8  Exact SubjectBinding match
AG9  AdmissionEvidenceManifest integrity
AG10 Required approvals valid/current
AG11 Risk ceiling compatibility
AG12 Capability-class eligibility intersection
AG13 Separation-of-duties requirement
AG14 Existing suspension / incident state
AG15 Coherent TrustStateReference
AG16 Final admission decision
```

All mandatory gates pass or admission is denied.

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

Verdicts:

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

    schema_version
    canonical_encoding_version
    hash_algorithm

    admission_authority_id
    admission_key_id
    signature
}
```

Periodic review is represented by `maximum_admission_duration` and credential `expires_at`; successful renewal creates a new AdmissionDecision and AdmissionCredential. There is no ambiguous `next_review_at` field.

AdmissionCredential remains an eligibility ceiling only.

---

## 19. Effective Eligibility

Effective eligibility requires:

```text
QualificationCredential usable now
AND AdmissionCredential usable now
AND exact SubjectBinding digest match
AND exact role match
AND qualification profile explicitly recognized by AdmissionPolicy
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

A separate least-privilege CapabilityToken is required for protected actions.

---

## 20. Dependency Invalidation

Admission depends on the exact QualificationCredential referenced at issuance.

Admission becomes unusable for new authorization when qualification is:

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

For every governed action whose policy requires qualification/admission, the signed CapabilityToken binds:

```text
subject_binding_digest
qualification_credential_id
qualification_credential_digest
admission_credential_id
admission_credential_digest
```

Unsigned eligibility flags are prohibited.

The ATE verifier validates current qualification/admission usability, live SubjectBinding satisfaction, risk/capability ceilings, and ordinary ATE gates.

The signed TrustDecision binds the same eligibility IDs/digests, live subject/session reference, requested action digest, capability token, and coherent trust-state view.

The executor need not re-run historical qualification evidence. It verifies the signed bound dependency chain and final current state.

---

## 22. Execution Authorization Point (EAP)

> **Execution Authorization Point:** the final serialized or authoritative point at which the Capability Executor validates current controlling trust state and irrevocably commits to attempting the protected side effect.

Required guarantee:

> Any revocation, suspension, expiration, or other invalidating state effective and observable by the authoritative trust-state system before EAP MUST prevent the action from crossing EAP.

The architecture does not claim retroactive cancellation after an irreversible external effect has already crossed its commit point.

For the local PoC, current-state recheck, nonce/execution reservation, EAP, and protected local mutation occur inside one serializable transaction, lock, or equivalent deterministic critical section.

External effects continue to follow existing A3/A4 idempotency and ambiguous-effect rules.

---

## 23. Derived Expiration Rule

Downstream authorization cannot outlive controlling dependencies.

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

Revocation/suspension/hard supersession override nominal downstream expiry before EAP.

---

## 24. Assurance-Level Separation

### A0/A1

Qualification/admission may be optional or lightweight where signed policy permits.

### A2

At minimum:

- participant cannot possess policy, R11, R12, authorization, trust-decision, or executor keys;
- participant cannot access generic signing oracles for those keys;
- distinct R11/R12 signing identities are required;
- policy/adjudication separation applies unless superior signed policy explicitly permits concentration;
- executor mediation and final current-state verification are mandatory for R2 governed actions.

### A3/A4

Apply the stronger service separation, custody, approval/quorum, freshness, audit, and external-effect controls of the existing Risk & Assurance Policy Model.

Standing qualification/admission never replaces action-time assurance evidence.

---

## 25. Requalification / Re-admission

Mandatory requalification triggers where applicable include qualification expiration, material SubjectBinding change, profile hard supersession, material binding-relevant runtime/security change, invalidated required evidence, relevant authority/key compromise, and operator/security incident requiring requalification.

Mandatory re-admission triggers where applicable include admission expiration, role change, policy hard supersession, replacement qualification under default no-continuity semantics, requested risk ceiling increase, expanded eligibility capability class, and incident/suspension requiring renewed approval.

Renewal creates new signed decisions and credentials. Old timestamps are never silently extended.

---

## 26. Suspension and Revocation

Required revocation target classes include:

```text
qualification_credential_id
admission_credential_id
qualification_authority key
admission_authority key
qualification profile
admission policy
subject identity/binding anchor where applicable
```

Required reason-code additions:

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

---

## 27. Threat Model

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
19. revocation/EAP race ambiguity;
20. unreviewed-future-profile auto-trust.

---

## 28. Audit Requirements

Qualification/admission and EAP events are consequential trust transitions and produce durable tamper-evident evidence external to participant control.

Required event families include qualification evaluation/grant/deny/issuance/suspension/revocation, admission evaluation/grant/deny/issuance/suspension/revocation, EAP reached, and execution blocked by eligibility state.

Audit records include relevant SubjectBinding, qualification/admission IDs/digests, profile/policy/manifests, coherent trust-state view, action digest, EAP state/epoch, verdict/reason code, and controlling artifact hashes.

Existing audit hash-chain, ledger sequence, signing, and epoch rules remain controlling.

---

## 29. Reason Codes

Qualification:

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

Admission:

```text
AX_SCHEMA_INVALID
AX_CANONICALIZATION_INVALID
AX_DIGEST_MISMATCH
AX_UNTRUSTED_POLICY_ISSUER
AX_POLICY_NOT_CURRENT
AX_QUALIFICATION_INVALID
AX_QUALIFICATION_NOT_CURRENT
AX_QUALIFICATION_PROFILE_UNRECOGNIZED
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

---

## 30. Security Invariants

- **QA-INV-1:** Participant cannot qualify itself.
- **QA-INV-2:** Participant cannot admit itself.
- **QA-INV-3:** Policy inputs are immutable and authority-signed.
- **QA-INV-4:** Security digests use deterministic canonical rules.
- **QA-INV-5:** SubjectBinding is immutable, digest-bound, and machine-evaluable.
- **QA-INV-6:** Qualification binds exact profile and evidence manifest.
- **QA-INV-7:** Admission binds exact qualification and admission evidence manifest.
- **QA-INV-8:** AdmissionPolicy explicitly recognizes acceptable qualification profile versions/digests; unknown future versions are not trusted automatically.
- **QA-INV-9:** QualificationCredential grants no direct resource authority.
- **QA-INV-10:** AdmissionCredential grants no direct resource authority.
- **QA-INV-11:** Eligibility capability classes are ceilings only.
- **QA-INV-12:** Admission becomes unusable when its qualification dependency becomes unusable.
- **QA-INV-13:** CapabilityToken and TrustDecision bind exact eligibility dependencies.
- **QA-INV-14:** ATE decisions use one coherent trust-state view.
- **QA-INV-15:** Invalidating state effective/observable before EAP prevents crossing EAP.
- **QA-INV-16:** Downstream nominal expiry cannot exceed upstream eligibility expiry.
- **QA-INV-17:** Standing credentials cannot replace session-local COA or action-time assurance evidence.
- **QA-INV-18:** Valid signatures from unauthorized issuers are rejected.
- **QA-INV-19:** Evidence/approvals are digest-bound against substitution.
- **QA-INV-20:** Participant cannot widen risk or eligibility ceilings.
- **QA-INV-21:** Revoked/suspended/expired/unknown state cannot support crossing EAP.
- **QA-INV-22:** Admission review cycles are enforced through deterministic expiry and reissuance, not ambiguous advisory timestamps.
- **QA-INV-23:** Consequential decisions and execution attempts emit durable tamper-evident audit evidence.

---

## 31. Minimal PoC Strategy

No live LLM calls are required. Use deterministic synthetic subject fixtures represented by identity keys and runtime metadata.

```text
role_id: demo-repository-writer
trust_domain: local-ate-demo
maximum risk: R2
eligible capability class: demo-resource-write
minimum assurance: A2
```

Subjects:

```text
Agent A fixture — intended qualified/admitted subject
Agent B fixture — control subject
```

Use distinct keys for Policy Authority, Identity/Runtime Authority, R11, R12, Authorization Authority, Trust Decision Authority, Capability Executor identity, and Audit Authority.

Reuse the P1 enforcement/resource boundary where practical.

---

## 32. Mandatory PoC Test Matrix

```text
QA-P1  Happy path -> exactly one protected mutation
QA-P2  Qualified but not admitted -> DENY
QA-P3  Admission revoked before new capability -> DENY
QA-P4  Pre-issued capability after admission revocation before EAP -> DENY
QA-P5  Pre-issued capability after qualification revocation before EAP -> DENY
QA-P6  Qualification expires after capability issuance before EAP -> DENY
QA-P7  Agent B reuses Agent A chain -> SubjectBinding DENY
QA-P8  Valid signature from unauthorized qualification issuer -> DENY
QA-P9  Mixed/incoherent trust-state view -> DENY
QA-P10 Canonical payload/digest substitution -> DENY
QA-P11 Deterministic revocation/EAP ordering -> ordering preserved and auditable
QA-P12 Direct protected-resource bypass -> OS/resource DENY; any success = enforcement failure
QA-P13 Unrecognized newer qualification-profile version/digest -> admission DENY
QA-P14 Admission expiry/review boundary -> old admission DENY; new signed re-admission required
```

Every case emits reconstructable audit evidence.

---

## 33. PoC Success Criteria

All must hold:

1. signed role profile controls qualification;
2. qualification alone cannot execute;
3. admission requires exact usable qualification;
4. admission alone cannot execute;
5. SubjectBinding prevents credential transplant;
6. policy/evidence issuers are authority-checked;
7. canonical digests are deterministic;
8. admission policy rejects unrecognized future qualification profiles;
9. qualification/admission dependencies are bound into CapabilityToken and TrustDecision;
10. mixed trust-state epochs are rejected;
11. invalidation effective before EAP blocks execution;
12. upstream expiry before EAP blocks execution;
13. admission renewal requires a new signed decision/credential;
14. EAP ordering is deterministic and auditable;
15. executor verifies bound dependencies/current state without re-running qualification;
16. direct resource bypass is impossible under the PoC boundary;
17. every decision/execution attempt emits durable tamper-evident evidence.

---

## 34. Required Reconciled Amendment Set

This protocol is frozen only together with:

```text
ATE-TRUST-ROOT-KEY-CUSTODY-MODEL-v0.1.1-QUALIFICATION-ADMISSION-AMENDMENT.md
ATE-REVOCATION-TRUST-STATE-MODEL-v0.1.1-QUALIFICATION-ADMISSION-AMENDMENT.md
ATE-PRODUCTION-ARCHITECTURE-v0.1.1-QUALIFICATION-ADMISSION-AMENDMENT.md
ATE-RISK-ASSURANCE-POLICY-MODEL-v0.1.1-QUALIFICATION-ADMISSION-AMENDMENT.md
ATE-AUDIT-ACCOUNTABILITY-MODEL-v0.1.1-QUALIFICATION-ADMISSION-AMENDMENT.md
```

The amendments preserve the existing baseline v0.1 architecture documents and add only qualification/admission integration semantics.

---

## 35. Freeze and Implementation Order

```text
v0.2.2 final freeze candidate
-> verify against reconciliation review
-> hash protocol + five amendments
-> commit freeze manifest
-> only then authorize tiny synthetic local PoC design/implementation
-> deterministic tests
-> closeout
```

No Hermes implementation task is authorized before freeze.

---

## 36. Freeze Gates

```text
FG1  no unresolved critical/high review finding
FG2  canonical digest semantics reconciled
FG3  coherent TrustStateReference reconciled
FG4  EAP semantics reconciled
FG5  SubjectBinding semantics accepted
FG6  R11/R12 trust-root permissions added
FG7  qualification/admission revocation targets added
FG8  mandatory ATE dependency binding added
FG9  risk/assurance integration added
FG10 audit/EAP integration added
FG11 explicit qualification-profile recognition added
FG12 deterministic admission review/expiry semantics added
FG13 PoC test matrix frozen
FG14 reconciled files hash-locked
FG15 no implementation started against superseded v0.1/v0.2/v0.2.1 semantics
```

---

## 37. Candidate Disposition

```text
Version:                     v0.2.2
Status:                      FINAL FREEZE CANDIDATE / NOT YET FROZEN
v0.1 major defects:          CORRECTED
v0.2 second-pass defects:    CORRECTED
reconciliation defects:      CORRECTED
Implementation authorized:   NO UNTIL FREEZE MANIFEST
Hermes required now:         NO
Next required step:          HASH + FREEZE RECONCILED SET
```

# Agent Qualification & Admission Protocol v0.1

**Status:** DRAFT — DESIGN ONLY — NOT FROZEN  
**Architecture family:** INSA / Value Architecture / Condition of Agency / Agent Trust Envelope  
**Protocol purpose:** establish whether an AI agent is eligible to participate in a governed trust domain and to request bounded ATE authorization for a defined role.

---

## 1. Purpose

This protocol defines the qualification and admission lifecycle for AI agents that participate in a governed INSA system.

The protocol answers two distinct questions:

1. **Qualification:** Has this agent produced sufficient current evidence to establish that it meets the requirements for a defined role?
2. **Admission:** Has an authorized trust domain accepted that qualified agent as an eligible participant for that role under current governance?

Neither answer grants permission to perform a governed action.

The controlling principle is:

> Qualification establishes role eligibility. Admission establishes domain participation. The Agent Trust Envelope authorizes a specific governed action.

Therefore:

```text
QUALIFIED != ADMITTED
ADMITTED != AUTHORIZED_TO_ACT
AUTHORIZED_TO_ACT requires a valid action-specific ATE trust decision
```

This distinction is mandatory.

---

## 2. Architectural Context

The wider architecture separates responsibilities as follows:

```text
INSA                 -> application architecture
Value Architecture   -> normative architecture
Condition of Agency  -> commitment architecture
Qualification        -> role-eligibility architecture
Admission            -> trust-domain participation architecture
Agent Trust Envelope -> action-specific trust architecture
Enforcement Plane    -> authority / execution architecture
Evidence + Audit     -> accountability architecture
```

Qualification and admission sit upstream of ATE capability issuance and execution.

Conceptually:

```text
Candidate Agent
      |
      v
Qualification Requirements
      |
      v
Evidence Evaluation
      |
      +---- FAIL --------------------> NOT QUALIFIED
      |
      v
Qualification Credential
      |
      v
Trust-Domain Admission Review
      |
      +---- DENY --------------------> NOT ADMITTED
      |
      v
Admission Credential
      |
      v
Fresh Session + COA + VA + Action Evidence
      |
      v
ATE Verification / Trust Decision
      |
      +---- DENY --------------------> NO EXECUTION
      |
      v
Capability Executor
      |
      v
Governed Resource
```

---

## 3. Core Security Principles

### 3.1 No permanent trust badge

Qualification MUST NOT be represented as a permanent claim that an agent is trustworthy.

A qualification means only:

> At a defined time, under a defined requirements profile, using defined evidence, this subject satisfied the requirements for this role within this trust domain or recognized qualification domain.

Current authorization still depends on present identity, session, policy, evidence, revocation state, requested action, and risk class.

### 3.2 Qualification is role-specific

An agent qualified for one role MUST NOT automatically be considered qualified for another.

Example:

```text
qualified: documentation-reader
!=
qualified: production-deployer
```

### 3.3 Admission is domain-specific

An agent qualified by a recognized authority is not automatically admitted into every project, organization, or trust domain.

Admission is an explicit trust-domain decision.

### 3.4 Admission creates no resource credential

Admission MUST NOT place protected resource credentials in the participant agent's possession.

Admission creates eligibility to request bounded authorization through ATE.

### 3.5 Session commitment remains fresh

A human may sign an annual policy acknowledgment. An AI agent session cannot safely be assumed to inherit a prior session's commitment merely because it uses the same product or model name.

Therefore a standing qualification or admission MUST NOT replace session-bound Condition of Agency acceptance where COA is required.

### 3.6 Current state controls

Historical qualification or admission is insufficient.

At use time, controlling artifacts must be:

```text
valid
AND current
AND not expired
AND not suspended
AND not revoked
AND not superseded
AND context-compatible
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

---

## 4. Non-Goals

Version 0.1 does not define:

- a universal reputation score for AI agents;
- an Internet-scale agent certification authority;
- a global model benchmark;
- a permanent moral or safety classification;
- a substitute for ATE action-specific authorization;
- a substitute for session-bound COA acceptance;
- a substitute for current Value Architecture policy checks;
- a production PKI product;
- provider-specific hardware attestation;
- employment-style legal status for agents;
- autonomous widening of authority based on past successful behavior.

The protocol intentionally avoids a scalar "trust score." Trust is decomposed into evidence-backed claims and bounded decisions.

---

## 5. Terminology

### Candidate

An agent or agent runtime presented for qualification.

### Role

A named class of permitted project responsibility, such as:

```text
project-reader
repository-writer
issue-manager
release-reviewer
production-deployer
```

A role defines an eligibility ceiling, not an execution permission.

### Qualification Requirements Profile

The authoritative policy describing what evidence is required to qualify for a role.

### Qualification Credential

A signed artifact recording that a subject satisfied a specific Qualification Requirements Profile.

### Admission Policy

The trust-domain policy defining which qualified subjects may participate, for which roles, under what restrictions.

### Admission Credential

A signed artifact recording that a qualified subject has been admitted to a specific trust domain for a bounded role and interval.

### Qualification Authority

An independent authority permitted to issue Qualification Credentials.

### Admission Authority

An authority permitted to admit qualified agents into a trust domain.

One deployment MAY assign both functions to one administrative service for low-risk environments, but the role concentration must be explicit and risk-classified.

### Effective Eligibility

The state in which a subject is both currently qualified and currently admitted and therefore may request ATE authorization for actions within its eligibility ceiling.

Effective eligibility is not execution authority.

---

## 6. Authority Model

This protocol introduces two logical authority roles:

```text
R11 — Qualification Authority
R12 — Admission Authority
```

These role numbers are provisional until the Trust Root & Key Custody Model is amended and frozen to recognize them.

### R11 — Qualification Authority

May sign:

- QualificationDecision
- QualificationCredential
- qualification suspension records where policy permits

Must not automatically inherit:

- Trust Root Authority
- Policy Authority
- Authorization Authority
- Trust Decision Authority
- Capability Executor credentials

### R12 — Admission Authority

May sign:

- AdmissionDecision
- AdmissionCredential
- admission suspension or withdrawal records where policy permits

Must not automatically inherit:

- Qualification Authority
- Authorization Authority
- Trust Decision Authority
- protected resource credentials

### 6.1 Trust-root requirement

A valid signature is insufficient unless the signer is currently authorized for the relevant artifact type in the Trust Root Registry.

No R11 or R12 artifact is usable until the production trust-root model recognizes the corresponding authority and key.

---

## 7. Qualification Requirements Profile

Every qualification decision MUST evaluate the candidate against an explicit, versioned, signed requirements profile.

Conceptual structure:

```text
QualificationRequirementsProfile {
    profile_id
    profile_version
    profile_digest

    trust_domain_or_qualification_domain
    role_id

    required_identity_evidence[]
    required_provenance_evidence[]
    required_behavioral_evidence[]
    required_governance_compatibility[]
    required_tooling_or_runtime_constraints[]

    minimum_assurance_level
    maximum_eligible_risk_level

    evidence_freshness_rules[]
    disqualifying_conditions[]
    requalification_triggers[]

    qualification_validity_duration

    policy_id
    policy_version
    policy_digest

    issuer_authority_id
    issuer_key_id
    issued_at
    signature
}
```

The candidate MUST NOT be allowed to select or downgrade its own profile.

---

## 8. Qualification Evidence Classes

The exact evidence required is role-specific. The protocol supports the following evidence classes.

### 8.1 Identity evidence

May establish:

- agent identity;
- runtime identity;
- provider identity where verifiable;
- model identity where verifiable;
- orchestration identity;
- software/build identity where verifiable;
- signing identity;
- ownership or administrative domain where applicable.

Claims MUST NOT exceed available evidence.

If exact provider/model/runtime identity cannot be independently established, the resulting credential must state the weaker verified claim rather than silently asserting stronger provenance.

### 8.2 Runtime/provenance evidence

May include:

- live provenance receipt;
- runtime build digest;
- agent configuration digest;
- tool manifest digest;
- sandbox or execution-boundary attestation;
- ephemeral runtime key binding.

A qualification profile may allow controlled runtime variance, but allowed variance must be explicit.

### 8.3 Governance compatibility evidence

May establish that the candidate/runtime can participate under:

- a named Condition of Agency family;
- a named Value Architecture policy family;
- required audit obligations;
- required enforcement boundaries;
- required evidence-generation behavior.

This is a capability/compatibility claim only.

It does **not** replace fresh session-bound COA acceptance or current VA policy verification at action time.

### 8.4 Behavioral evidence

May include:

- conformance test results;
- adversarial test results;
- task-class evaluations;
- policy-following evaluations;
- evidence-handling evaluations;
- refusal/escalation behavior;
- replay/tamper handling where agent behavior is relevant.

Behavioral evidence must identify:

```text
what was tested
under what runtime/configuration
against which rubric
when it was tested
who evaluated it
what result was obtained
what limitations apply
```

### 8.5 Operational evidence

For some roles, policy may require evidence that the runtime supports required operational controls, such as:

- executor mediation;
- credential separation;
- durable audit emission;
- nonce/replay discipline;
- revocation checking;
- bounded tool access.

An agent MUST NOT be qualified for a role whose required enforcement assumptions are absent.

---

## 9. Candidate Evidence Manifest

Evidence used for qualification MUST be enumerated and digest-bound.

```text
QualificationEvidenceManifest {
    manifest_id
    subject_identity
    role_id
    profile_id
    profile_version
    profile_digest

    evidence_items[] {
        artifact_type
        artifact_id
        artifact_digest
        issuer_authority_id
        issued_at
        expires_at_optional
    }

    manifest_digest
    created_at
}
```

The QualificationDecision MUST bind to `manifest_digest`.

Mix-and-match substitution after evaluation is prohibited.

---

## 10. Qualification Evaluation Gates

Recommended deterministic sequence:

```text
QG0  Canonicalization / schema validity
QG1  Trust-root and issuer authority
QG2  Requirements profile currentness
QG3  Subject identity binding
QG4  Runtime / provenance compatibility
QG5  Evidence completeness
QG6  Evidence freshness
QG7  Behavioral requirements
QG8  Governance compatibility
QG9  Assurance / risk ceiling
QG10 Revocation / suspension state
QG11 Evidence-manifest binding
QG12 Final qualification decision
```

All mandatory gates must pass.

Evaluation SHOULD stop at the first deterministic failure unless policy requires collection of all diagnostic failures.

---

## 11. QualificationDecision

Every evaluation produces a signed decision artifact, including failures.

```text
QualificationDecision {
    qualification_decision_id

    subject_identity
    role_id
    trust_domain_or_qualification_domain

    profile_id
    profile_version
    profile_digest
    evidence_manifest_digest

    verdict
    reason_code

    maximum_eligible_risk_level

    evaluated_at
    valid_until_if_pass

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

No ambiguous third state is usable.

---

## 12. QualificationCredential

A QualificationCredential MAY be issued only after a valid `QUALIFICATION_GRANTED` decision.

```text
QualificationCredential {
    qualification_credential_id

    subject_identity
    subject_binding_constraints

    role_id
    trust_domain_or_qualification_domain

    profile_id
    profile_version
    profile_digest

    qualification_decision_id
    evidence_manifest_digest

    maximum_eligible_risk_level
    allowed_capability_classes[]

    issued_at
    valid_from
    expires_at

    status
    revocation_reference

    qualification_authority_id
    qualification_key_id
    signature
}
```

A QualificationCredential MUST NOT contain protected resource credentials.

---

## 13. Subject Binding and Runtime Change

Qualification must bind to the strongest stable subject identity that can actually be verified.

A subject binding may include constraints such as:

```text
agent_identity_id
provider_id_optional
model_id_optional
runtime_build_digest_optional
orchestration_digest_optional
tool_manifest_digest_optional
security_profile_digest_optional
```

Policy must define which changes are compatible and which require requalification.

Examples of likely requalification triggers:

- different model family when model identity is controlling;
- different provider where provider provenance is controlling;
- changed orchestration policy;
- materially expanded tool set;
- changed runtime security boundary;
- changed governance implementation;
- changed behavioral evidence baseline;
- authority-directed requalification after incident.

A display name change alone should not invalidate qualification when immutable identity remains unchanged.

---

## 14. Admission Policy

Qualification does not force a trust domain to admit the subject.

Each trust domain must control its own admission policy.

```text
AdmissionPolicy {
    admission_policy_id
    trust_domain

    eligible_roles[]
    recognized_qualification_authorities[]
    recognized_qualification_domains[]

    minimum_qualification_profile_versions[]
    maximum_admission_duration
    maximum_risk_by_role[]

    required_human_or_authority_approvals[]
    prohibited_subject_conditions[]
    reapproval_triggers[]

    policy_id
    policy_version
    policy_digest

    issuer_authority_id
    issuer_key_id
    effective_from
    signature
}
```

The candidate agent MUST NOT be able to admit itself.

---

## 15. Admission Evaluation Gates

Recommended deterministic sequence:

```text
AG0  Canonicalization / schema validity
AG1  Trust-root and issuer authority
AG2  Admission policy currentness
AG3  QualificationCredential validity
AG4  Qualification currentness / revocation
AG5  Trust-domain recognition
AG6  Role match
AG7  Subject binding
AG8  Risk ceiling compatibility
AG9  Required approval / separation of duties
AG10 Admission duration and review interval
AG11 Existing suspension / incident state
AG12 Final admission decision
```

All mandatory gates must pass.

---

## 16. AdmissionDecision

```text
AdmissionDecision {
    admission_decision_id

    subject_identity
    trust_domain
    role_id

    qualification_credential_id
    qualification_credential_digest

    admission_policy_id
    admission_policy_version
    admission_policy_digest

    verdict
    reason_code

    maximum_admitted_risk_level
    allowed_capability_classes[]

    evaluated_at
    valid_until_if_admitted

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

## 17. AdmissionCredential

An AdmissionCredential MAY be issued only after `ADMISSION_GRANTED`.

```text
AdmissionCredential {
    admission_credential_id

    subject_identity
    trust_domain
    role_id

    qualification_credential_id
    qualification_credential_digest

    admission_policy_id
    admission_policy_version
    admission_policy_digest

    maximum_admitted_risk_level
    allowed_capability_classes[]
    excluded_capability_classes[]

    issued_at
    valid_from
    expires_at
    next_review_at_optional

    status
    revocation_reference

    admission_authority_id
    admission_key_id
    signature
}
```

The AdmissionCredential establishes an eligibility ceiling only.

It MUST NOT directly authorize operations or targets.

---

## 18. Dual-State Model

Qualification and admission are tracked as separate state machines.

### Qualification state

```text
UNASSESSED
QUALIFIED
DENIED
SUSPENDED
REVOKED
EXPIRED
SUPERSEDED
UNKNOWN
```

### Admission state

```text
NOT_ADMITTED
ADMITTED
DENIED
SUSPENDED
REVOKED
EXPIRED
SUPERSEDED
UNKNOWN
```

Effective eligibility requires:

```text
qualification_state == QUALIFIED
AND
admission_state == ADMITTED
```

Any other combination is non-eligible for new ATE authorization.

---

## 19. Dependency Invalidation

Admission depends on qualification.

Therefore:

```text
qualification suspended -> admission non-usable
qualification revoked   -> admission non-usable
qualification expired   -> admission non-usable
qualification superseded without compatible replacement -> admission non-usable
qualification unknown   -> admission non-usable
```

A dependent AdmissionCredential need not be physically deleted. It becomes non-usable because its prerequisite is no longer current.

Historical audit evidence remains intact.

---

## 20. Integration With ATE

Qualification and admission are upstream eligibility controls.

The action path remains:

```text
Current Qualification
       AND
Current Admission
       AND
Current Session Identity
       AND
Current COA Acceptance
       AND
Current VA Policy
       AND
Required Behavioral Evidence
       AND
Least-Privilege CapabilityToken
       AND
Action Binding
       AND
Revocation/Freshness/Nonce Checks
       ->
ATE Trust Decision
       ->
Capability Executor
```

### 20.1 Initial integration rule

For the first implementation, the Authorization Authority MUST validate current qualification and admission before issuing a CapabilityToken for governed R1+ actions where policy requires qualification.

Conceptually:

```text
function issue_capability(request):
    require current_qualification(request.subject, request.role)
    require current_admission(request.subject, request.trust_domain, request.role)
    require requested_scope <= admission_ceiling
    require requested_risk <= admission_risk_ceiling
    issue least_privilege_capability()
```

### 20.2 Explicit binding

A future ATE schema revision SHOULD add explicit fields such as:

```text
qualification_credential_id
admission_credential_id
```

until then, a prototype MAY bind these identifiers through a signed CapabilityToken constraints field or equivalent extension mechanism, provided the binding is covered by the token signature and verified by the ATE verifier/executor.

No unsigned side-channel admission flag is acceptable.

---

## 21. Action-Time Requirements Remain Independent

Qualification evidence must not silently satisfy action-time evidence requirements when the latter require fresher or session-specific evidence.

Examples:

- a 7-day qualification credential does not replace a session-local provenance receipt;
- a standing admission does not replace current COA acceptance;
- a behavioral evaluation used to qualify an agent last week does not satisfy an A4 action that requires behavioral evidence less than one hour old;
- an admitted `repository-writer` still requires an action-specific CapabilityToken for the exact repository operation.

This prevents standing credentials from becoming ambient authority.

---

## 22. Risk and Assurance Interaction

Qualification and admission MUST define risk ceilings.

Example:

```text
QualificationCredential.maximum_eligible_risk_level = R2
AdmissionCredential.maximum_admitted_risk_level     = R1
Requested action risk                                = R2
```

Result:

```text
DENY
```

because the admission ceiling is narrower.

The effective risk ceiling is:

```text
min(
  qualification maximum,
  admission maximum,
  role-policy maximum,
  current capability maximum
)
```

A participant MUST NOT select a lower risk classification for its own action.

---

## 23. Least Privilege and Capability Ceiling

Roles are intentionally broader than action permissions.

Example:

```text
Role: repository-writer
Admission ceiling:
    repository family = development-by-intent
    maximum risk = R2

Specific action:
    update one Markdown file
```

The resulting CapabilityToken should authorize only the specific operation/target needed for that action.

Admission MUST NOT itself become a standing write token.

---

## 24. Requalification Triggers

A Qualification Requirements Profile MUST define requalification triggers.

Baseline triggers SHOULD include where applicable:

- qualification expiration;
- controlling profile supersession;
- material model/provider/runtime change;
- material orchestration change;
- material tool-set expansion;
- Value Architecture incompatibility;
- Condition of Agency protocol change affecting role eligibility;
- invalidated behavioral evidence;
- security incident;
- authority compromise;
- repeated governed-action policy failures above a policy-defined threshold;
- operator-directed requalification.

A trigger need not prove misconduct. It means the previous evidence is no longer sufficient to support the old qualification claim.

---

## 25. Re-admission Triggers

A trust domain may require renewed admission after:

- AdmissionCredential expiration;
- role change;
- trust-domain policy change;
- qualification profile change;
- qualification replacement;
- risk ceiling increase;
- expanded capability class;
- incident or suspension;
- change in approving authority;
- project membership review cycle.

Renewal MUST produce a new signed decision rather than silently extending timestamps on an old credential.

---

## 26. Suspension and Revocation

Qualification and admission must integrate with the ATE Revocation & Trust-State Model.

Recommended revocation targets:

```text
qualification_credential_id
admission_credential_id
qualification_authority key
admission_authority key
qualification profile
admission policy
subject identity
```

Suggested reason codes to add to the revocation taxonomy:

```text
RV_QUALIFICATION_WITHDRAWN
RV_QUALIFICATION_EVIDENCE_INVALIDATED
RV_ADMISSION_WITHDRAWN
RV_ROLE_CHANGED
RV_REQUALIFICATION_REQUIRED
```

Suspension should be available for investigation states where permanent revocation is not yet justified.

For governed execution:

```text
SUSPENDED != usable
UNKNOWN   != usable
```

---

## 27. Separation of Duties

Strong deployment default:

```text
candidate participant
!= qualification authority
!= admission authority
!= authorization authority
!= trust decision authority
!= capability executor
```

For low-risk local prototypes, authority services MAY share a host or process if keys and logical roles remain distinct and the limitation is explicitly recorded.

The following are prohibited:

1. participant self-qualification;
2. participant self-admission;
3. participant possession of Admission Authority signing key;
4. admission authority silently issuing protected resource credentials;
5. admission bypass of failed ATE action gates;
6. qualification authority changing requirements during evaluation without producing a new signed profile.

---

## 28. Threat Model

The protocol must defend against at least the following failure modes.

### T1 — Self-qualification

The participant signs or asserts its own QualificationCredential.

**Mitigation:** authorized independent Qualification Authority; trust-root verification.

### T2 — Self-admission

The participant adds itself to a project or trust domain.

**Mitigation:** authorized Admission Authority; domain policy verification.

### T3 — Role laundering

A credential for a low-risk role is reused for a higher-risk role.

**Mitigation:** exact `role_id` binding and risk ceilings.

### T4 — Domain laundering

Qualification/admission from one domain is reused in another without recognition policy.

**Mitigation:** trust-domain binding and explicit federation/recognition policy.

### T5 — Runtime substitution

A different model/runtime uses another runtime's qualification.

**Mitigation:** subject-binding constraints and requalification triggers.

### T6 — Evidence substitution

Evidence items are replaced after evaluation.

**Mitigation:** signed evidence-manifest digest.

### T7 — Stale qualification

Expired evidence continues to support eligibility.

**Mitigation:** expiration, freshness rules, current-state checks.

### T8 — Policy supersession bypass

Old qualification/admission profiles continue after policy replacement.

**Mitigation:** active policy/profile manifests and supersession state.

### T9 — Admission-as-authority

An AdmissionCredential is treated as direct permission to act.

**Mitigation:** no resource credential at admission; mandatory ATE/CapabilityToken path.

### T10 — Session inheritance

A new session relies on an old session's COA commitment.

**Mitigation:** session-local COA acceptance remains mandatory when required.

### T11 — Credential replay / cloning

Another subject presents a copied qualification/admission artifact.

**Mitigation:** immutable subject binding plus current live identity/session verification.

### T12 — Delayed revocation

Withdrawn qualification remains usable.

**Mitigation:** current revocation checks at capability issuance and action evaluation.

### T13 — Risk downgrade

Participant claims an action is lower risk than policy classifies it.

**Mitigation:** signed policy-controlled risk classification.

### T14 — Authority-role collapse

A single compromised service can redefine policy, qualify, admit, authorize, decide trust, and execute.

**Mitigation:** separation of duties proportional to risk; key-role scoping; audit.

---

## 29. Audit Requirements

Every qualification and admission event must be auditable.

Minimum qualification audit event:

```text
QualificationAuditRecord {
    audit_id
    timestamp
    subject_identity
    role_id
    profile_digest
    evidence_manifest_digest
    qualification_decision_id
    verdict
    reason_code
    qualification_authority_id
    controlling_artifact_hashes[]
}
```

Minimum admission audit event:

```text
AdmissionAuditRecord {
    audit_id
    timestamp
    subject_identity
    trust_domain
    role_id
    qualification_credential_id
    admission_policy_digest
    admission_decision_id
    verdict
    reason_code
    admission_authority_id
    controlling_artifact_hashes[]
}
```

Audit history MUST preserve denied, expired, superseded, suspended, and revoked states rather than rewriting history to show only the latest state.

---

## 30. Reason Codes

Initial qualification reason taxonomy:

```text
QX_SCHEMA_INVALID
QX_UNTRUSTED_ISSUER
QX_PROFILE_NOT_CURRENT
QX_IDENTITY_MISMATCH
QX_RUNTIME_INCOMPATIBLE
QX_EVIDENCE_MISSING
QX_EVIDENCE_STALE
QX_BEHAVIORAL_REQUIREMENT_FAILED
QX_GOVERNANCE_INCOMPATIBLE
QX_ASSURANCE_INSUFFICIENT
QX_ARTIFACT_REVOKED
QX_MANIFEST_MISMATCH
QX_REQUALIFICATION_REQUIRED
QX_INTERNAL_ERROR
```

Initial admission reason taxonomy:

```text
AX_SCHEMA_INVALID
AX_UNTRUSTED_ISSUER
AX_POLICY_NOT_CURRENT
AX_QUALIFICATION_INVALID
AX_QUALIFICATION_NOT_CURRENT
AX_DOMAIN_NOT_RECOGNIZED
AX_ROLE_MISMATCH
AX_SUBJECT_MISMATCH
AX_RISK_EXCEEDS_CEILING
AX_REQUIRED_APPROVAL_MISSING
AX_SUBJECT_SUSPENDED
AX_ADMISSION_REVOKED
AX_READMISSION_REQUIRED
AX_INTERNAL_ERROR
```

Unknown or internal-error conditions fail closed.

---

## 31. Security Invariants

The protocol defines the following baseline invariants.

- **QA-INV-1:** No participant may qualify itself.
- **QA-INV-2:** No participant may admit itself.
- **QA-INV-3:** Qualification is bound to an explicit role and requirements profile.
- **QA-INV-4:** Admission is bound to a specific trust domain and role.
- **QA-INV-5:** A QualificationCredential alone grants no resource access.
- **QA-INV-6:** An AdmissionCredential alone grants no resource access.
- **QA-INV-7:** Admission cannot outlive usable qualification.
- **QA-INV-8:** Current action authorization still requires applicable ATE gates.
- **QA-INV-9:** Standing qualification/admission cannot replace session-local COA when required.
- **QA-INV-10:** Qualification/admission risk ceilings cannot be widened by the participant.
- **QA-INV-11:** Revoked, suspended, expired, superseded, or unknown prerequisite state cannot support new authorization.
- **QA-INV-12:** Evidence evaluated for qualification is digest-bound against substitution.
- **QA-INV-13:** Protected resource credentials are never issued merely because admission succeeds.
- **QA-INV-14:** Every qualification and admission decision emits durable audit evidence.
- **QA-INV-15:** A credential from an unrecognized issuer is unusable even if its cryptographic signature is valid.

---

## 32. Minimal End-to-End Proof of Concept

The first implementation SHOULD remain deliberately small and local.

### 32.1 Test role

```text
role_id: demo-repository-writer
trust_domain: local-ate-demo
maximum risk: R2
allowed capability class: demo-resource-write
```

### 32.2 Subjects

```text
Agent A — intended qualified/admitted participant
Agent B — control subject without valid admission
```

### 32.3 Minimal authorities

Use distinct logical signing identities for:

```text
Policy Authority
Qualification Authority
Admission Authority
Authorization Authority
Trust Decision Authority
Capability Executor
Audit Authority
```

For the PoC, these may coexist on one host if keys remain distinct and the limitation is documented.

### 32.4 Minimal test matrix

**QA-P1 — Qualified + admitted + current action evidence**

Expected:

```text
Qualification PASS
Admission PASS
Capability issuance PASS
ATE trust decision PASS
Executor operation PASS
```

The protected demo resource changes exactly once.

**QA-P2 — Qualified but not admitted**

Expected:

```text
Qualification PASS
Admission absent/denied
Capability issuance DENY
No executable ATE grant
Protected resource unchanged
```

**QA-P3 — Admission revoked after prior success**

Expected:

```text
Initial action PASS
Revoke AdmissionCredential
Next capability issuance or ATE validation DENY
Protected resource receives no second unauthorized change
```

**QA-P4 — Credential copied to wrong subject**

Expected:

```text
Agent B presents Agent A credential
Subject binding fails
DENY
Protected resource unchanged
```

Four deterministic cases are sufficient for the first diagnostic PoC.

---

## 33. PoC Success Criteria

The PoC succeeds only if all of the following are established:

1. Agent A can be qualified under a frozen role profile.
2. Qualification alone cannot cause protected execution.
3. Agent A can be explicitly admitted to the local trust domain.
4. Admission alone cannot cause protected execution.
5. Capability issuance is conditioned on current qualification and admission.
6. A valid ATE trust decision is still required for execution.
7. Agent B cannot reuse Agent A's standing credentials.
8. Revocation prevents future protected execution.
9. The participant cannot directly bypass the Capability Executor.
10. Each decision and attempted execution produces durable evidence.

If the participant can directly modify the protected resource outside the executor path, the PoC MUST be classified as enforcement failure regardless of qualification/admission logic.

---

## 34. PoC Non-Claims

A successful PoC would **not** establish:

- global agent trustworthiness;
- general AI safety;
- cross-provider identity portability;
- production-scale federation;
- hardware-backed identity;
- protection against host-root compromise;
- resistance to malicious qualification authorities;
- production key-custody sufficiency;
- permanent behavioral reliability.

It would establish the narrower architecture claim:

> A governed system can require verifiable role qualification and explicit trust-domain admission before an agent becomes eligible for bounded action authorization, and can enforce withdrawal of that eligibility before protected execution.

---

## 35. Required Architecture Follow-Ups Before Implementation Freeze

Before a formal implementation protocol is frozen, the following integrations should be reviewed:

1. **Trust Root & Key Custody Model** — add/confirm Qualification Authority and Admission Authority roles and artifact types.
2. **Revocation & Trust-State Model** — add qualification/admission artifact classes and reason codes.
3. **ATE Production Architecture** — define the canonical qualification/admission binding point, preferably explicit credential IDs in the evidence/capability path.
4. **Risk & Assurance Policy Model** — specify whether qualification/admission requirements vary by A0–A4 and define minimum authority separation by risk class.
5. **Audit & Accountability Model** — add canonical qualification/admission audit event classes.

These are specification integrations, not justification for expanding the first PoC.

---

## 36. Implementation Discipline

The first implementation SHOULD follow the project's lean evidence strategy:

```text
Design
-> adversarial review
-> correction
-> freeze
-> tiny local PoC
-> deterministic tests
-> closeout
```

Do not begin with:

- multi-agent replication;
- large behavioral test sets;
- premium dual evaluators;
- external federation;
- broad production deployment;
- complex dashboards;
- large role taxonomies.

The purpose of the first PoC is to falsify or support the architecture connection at minimal cost.

---

## 37. Design Questions for Adversarial Review

The next review should specifically attack these questions:

1. Is qualification sufficiently distinct from action authorization?
2. Can AdmissionCredential accidentally become ambient authority?
3. Is the stable subject-binding model strong enough to prevent runtime substitution without making qualification unusably session-specific?
4. Should Qualification Authority and Admission Authority be separate R11/R12 roles, or should one map onto an existing authority class?
5. At what point should AdmissionCredential become an explicit field in the ATE schema rather than a signed CapabilityToken constraint?
6. Which qualification evidence can be long-lived, and which must always be reacquired at action time?
7. What requalification triggers are mandatory versus domain-policy-specific?
8. How should qualification behave when provider/model provenance is only partially verifiable?
9. Does dependency invalidation propagate fast enough after qualification revocation?
10. Can any path still reach a protected resource after qualification/admission failure?

No implementation should be authorized until these questions have been adversarially reviewed and the resulting design is frozen.

---

## 38. Draft Disposition

**Version:** v0.1  
**Disposition:** DRAFT / NOT FROZEN  
**Implementation authorization:** NONE  
**Next required step:** adversarial design review in ChatGPT, followed by a corrected frozen candidate before any Hermes implementation task.

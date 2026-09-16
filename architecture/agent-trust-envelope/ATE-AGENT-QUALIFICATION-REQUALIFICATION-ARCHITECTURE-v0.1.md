# ATE Agent Qualification & Requalification Architecture v0.1

**Status:** Architecture candidate — DESIGN ONLY  
**Date:** 2026-09-16  
**Program:** Agent Trust Envelope (ATE)  
**Depends on:** Runtime Identity / Trust Root / Attestation Architecture v0.1.1  
**Related:** Production Requirements & Conformance Profile v0.1; Risk & Assurance Policy Model v0.1

---

## 1. Purpose

This document defines how an AI agent/runtime becomes **qualified for a bounded class of work**, how that qualification is represented as verifiable evidence, what changes preserve or invalidate qualification, and when re-attestation, partial requalification, or full requalification is required.

The governing principle is:

> **Qualification is not a declaration that an agent is generally trustworthy. It is a time-bounded, evidence-backed statement that a specific principal/runtime profile has demonstrated required properties for a defined role, capability set, risk envelope, governance state, and operating context.**

Qualification is therefore scoped, revocable, versioned, and evidence-dependent.

---

## 2. Human Professional Analogy

ATE qualification intentionally parallels professional qualification without pretending that humans and AI agents are identical.

A human may be admitted to sensitive work because an organization can verify:

- identity;
- education or training;
- role qualifications;
- background or vetting status;
- accepted policies and professional obligations;
- work experience or demonstrated competence;
- current authorization;
- periodic recertification.

For an AI agent, the analogous evidence classes are:

```text
runtime identity / provenance
software + model + configuration profile
tool/capability profile
behavioral evaluation evidence
Condition of Agency acceptance
Value Architecture binding
policy binding
qualification issuer decision
validity / expiration / revocation state
```

The output is not "trusted agent." The output is:

```text
qualified for ROLE X
under PROFILE Y
for RISK/ASSURANCE CLASS Z
within SCOPE S
until TIME T
based on EVIDENCE E
```

---

## 3. Qualification Is Separate From Authorization

Qualification answers:

> Is this agent/runtime currently eligible to be considered for this class of work?

Authorization answers:

> May this qualified runtime perform this specific action now?

These MUST remain distinct.

```text
Identity + Attestation
        |
        v
Qualification
        |
        v
Verified Runtime Context
        |
        v
Action-Specific Authorization
        |
        v
Enforcement
```

A valid qualification MUST NOT itself grant execution authority.

---

## 4. Core Objects

ATE qualification uses four conceptual objects.

### 4.1 Qualification Definition

Defines what must be demonstrated for a qualification class.

```text
QualificationDefinition {
    qualification_class_id
    qualification_definition_version
    trust_domain_id
    role_id
    permitted_capability_classes[]
    prohibited_capability_classes[]
    maximum_risk_class
    minimum_assurance_profile
    required_runtime_profile_constraints
    required_governance_constraints
    required_behavioral_evaluations[]
    required_evidence_freshness
    requalification_policy_id
    issuer_authority_constraints
    issued_by
    effective_from
    supersedes?
    signature
}
```

The definition is policy. The subject agent cannot alter it.

### 4.2 Qualified Runtime Profile

Immutable description of the runtime profile actually evaluated.

At minimum it binds:

```text
qualified_profile_id
principal_id or principal_class
software_manifest_digest
model_identity
model_identity_assurance
configuration_profile_digest
tool_capability_profile_digest
resource_permission_class
network_access_class
key_protection_assurance
assurance_tier
coa_digest
value_architecture_digest
policy_bundle_digest
trust_domain_id
project_scope or scope constraints
```

This object MUST be content-addressable by canonical digest.

### 4.3 Qualification Evidence Package

Immutable collection of evidence used to make the qualification decision.

Conceptually:

```text
QualificationEvidencePackage {
    evidence_package_id
    qualification_class_id
    qualified_profile_digest
    evaluator identities
    evaluation protocol digests
    test/result receipts
    behavioral evidence receipts
    governance acceptance evidence
    provenance/attestation references
    exception/waiver records[]
    evidence_created_at
    evidence_digest
}
```

The package MUST preserve enough information to determine **why** qualification was granted.

### 4.4 Qualification Credential

Signed decision issued by an authorized Qualification Authority.

```text
QualificationCredential {
    artifact_type = ATE_QUALIFICATION_CREDENTIAL
    artifact_version
    qualification_id
    qualification_class_id
    qualification_definition_version
    subject_principal_id
    qualified_profile_digest
    evidence_package_digest
    trust_domain_id
    scope_constraints
    permitted_capability_classes[]
    maximum_risk_class
    minimum_assurance_profile
    issued_at
    not_before
    valid_until
    requalification_due_at
    revocation_handle
    qualification_issuer_id
    signature_algorithm
    signature
}
```

The credential is evidence of qualification, not action authorization.

---

## 5. Qualification Decision Rule

A Qualification Authority may issue a qualification credential only if all mandatory conditions defined by the active Qualification Definition are satisfied.

Conceptually:

```text
QUALIFIED =
    identity/provenance acceptable
AND runtime profile matches evaluation profile
AND required governance evidence valid
AND required behavioral/functional evaluations pass
AND required evidence is current
AND evaluator/issuer authorities are valid
AND no controlling evidence is revoked
AND no mandatory requirement is waived outside policy
```

Any missing controlling evidence fails closed.

The Qualification Authority MUST NOT infer a PASS from incomplete evaluation.

---

## 6. Qualification Scope

Every qualification MUST be explicitly scoped.

Minimum scope dimensions include:

- role;
- capability class;
- risk class ceiling;
- assurance profile;
- trust domain;
- project/resource scope where applicable;
- runtime/software/model profile;
- tool/capability profile;
- governance profile;
- validity interval.

Examples:

```text
Qualified:
  repository-reviewer
  READ_REPOSITORY + COMMENT
  max risk R2
  project development-by-intent
  VA digest V4
  CoA digest C3

NOT IMPLIED:
  MERGE_PROTECTED_BRANCH
  SEND_EXTERNAL_EMAIL
  MODIFY_INFRASTRUCTURE
```

Qualification MUST NOT expand transitively to capabilities not named or covered by an explicit compatibility rule.

---

## 7. Behavioral Evidence

Behavioral evidence is one qualification input, not the qualification itself.

A BehavioralEvidenceReceipt SHOULD bind:

```text
evidence_receipt_id
subject / qualified_profile_digest
evaluation_protocol_id + digest
test corpus or generator digest
evaluator authority
evaluation environment
result
score/classification where applicable
created_at
valid_until or freshness class
revocation_handle
```

ATE MUST distinguish:

```text
behavioral evidence
    !=
qualification credential
```

The Qualification Authority determines whether the evidence set satisfies the Qualification Definition.

---

## 8. Evaluator Independence and Authority

Qualification evidence may originate from one or more evaluators depending on risk policy.

For each evidence class, policy MUST define:

- permitted evaluator authorities;
- independence requirements;
- whether self-evaluation is permitted;
- minimum replication requirements;
- conflict-of-interest constraints where applicable;
- acceptable evaluation protocol versions.

A subject agent SHOULD NOT be able to self-issue controlling evidence for a qualification class unless the Qualification Definition explicitly permits self-attested evidence for a non-critical field.

For high-assurance qualification, self-scoring MUST NOT be the sole controlling evidence.

---

## 9. Qualification State Machine

Qualification status is explicit.

```text
CANDIDATE
   |
   v
UNDER_EVALUATION
   |
   +--> NOT_QUALIFIED
   |
   v
QUALIFIED
   |
   +--> SUSPENDED
   |       |
   |       +--> QUALIFIED      (after authorized reinstatement)
   |       +--> REVOKED
   |
   +--> REQUALIFICATION_REQUIRED
   |       |
   |       +--> QUALIFIED      (new credential)
   |       +--> NOT_QUALIFIED
   |
   +--> EXPIRED
   |
   +--> REVOKED
```

Historical qualifications MUST remain auditable even after expiry or revocation.

No expired/revoked credential may be silently rewritten as current.

---

## 10. Re-attestation vs Requalification

ATE distinguishes three different events.

### 10.1 Re-attestation

Re-attestation proves that the currently running instance still matches an already-qualified profile.

It does not repeat the qualification evaluation.

Appropriate when:

```text
profile unchanged
qualification current
runtime restarted or renewed
freshness evidence expired
new runtime-instance identity issued
```

Result:

```text
same qualification credential may remain valid
new runtime/attestation evidence required
```

### 10.2 Partial Requalification

Repeats only the evaluation components invalidated by an approved compatible change.

Appropriate only when a signed compatibility/requalification policy explicitly defines the changed dimension as independently re-evaluable.

Example:

```text
software patch S1 -> S1.1
same model
same tool permissions
same VA/CoA
signed compatibility policy says security patch requires software regression suite only
```

A Qualification Authority MUST issue a new qualification decision/credential after partial requalification.

### 10.3 Full Requalification

Required when a material profile change invalidates the basis of the original qualification or when policy cannot prove safe compatibility.

The default for unknown material change is full requalification.

---

## 11. Change Classification

Every relevant runtime/profile change MUST be classified before an existing qualification is reused.

```text
NO_QUALIFICATION_IMPACT
RE_ATTESTATION_REQUIRED
PARTIAL_REQUALIFICATION_REQUIRED
FULL_REQUALIFICATION_REQUIRED
IMMEDIATE_SUSPENSION
```

The subject agent MUST NOT choose this classification.

It is determined by a signed Requalification Policy administered by an authorized policy/qualification authority.

---

## 12. Default Requalification Triggers

Unless an explicit signed compatibility policy says otherwise, the following SHOULD trigger at least the stated response.

| Change | Default response |
|---|---|
| Normal process/runtime restart, profile unchanged | Re-attestation |
| Runtime identity credential renewal, profile unchanged | Re-attestation |
| Patch-level software change | Partial or full requalification per policy |
| Major software implementation change | Full requalification |
| Model family/version change | Full requalification |
| Model weights/digest change for local measured model | Full requalification |
| Remote provider/model identity materially changes | Full requalification unless signed equivalence exists |
| System prompt/governance-control implementation materially changes | Full requalification |
| Value Architecture digest changes | Full requalification unless explicit compatibility decision exists |
| Condition of Agency digest changes | Re-acceptance + requalification assessment; default full |
| Policy bundle materially changes | Requalification assessment; default partial/full by policy |
| Tool set gains new write/execute/network capability | Full requalification |
| Tool capability removed | Re-attestation or partial requalification; never expands authority |
| Resource permission scope expands | Full requalification |
| Resource permission scope narrows | Re-attestation/partial as policy permits |
| Key-protection assurance decreases | Immediate suspension + full requalification |
| Assurance tier claim increases | Full requalification at new tier |
| Behavioral evidence expires | Requalification required |
| Qualification definition superseded incompatibly | Requalification required |
| Security incident involving subject/profile | Immediate suspension pending assessment |
| Material behavioral drift detected | Immediate suspension or requalification per policy |
| Qualification credential expires | Requalification required |
| Qualification issuer revoked/compromised | Suspend or revoke affected qualification per trust policy |

These are conservative defaults.

---

## 13. Compatibility Declarations

ATE MAY support signed compatibility declarations to avoid unnecessary full requalification.

A compatibility declaration MUST be explicit.

```text
QualificationCompatibility {
    source_profile_digest
    target_profile_digest or allowed change class
    qualification_class_id
    preserved_evidence_classes[]
    invalidated_evidence_classes[]
    required_delta_evaluations[]
    maximum_validity
    issuer
    signature
}
```

Compatibility MUST NOT be inferred heuristically from version names such as "patch" or "minor."

A cryptographically valid old qualification does not automatically cover a new profile.

---

## 14. Capability Expansion Rule

Any change that expands potential external effect MUST be treated as material.

Examples:

```text
read -> write
write -> execute
local -> network
internal messaging -> external messaging
non-production -> production
single repository -> organization-wide
no secrets -> secrets access
```

Default response:

```text
FULL_REQUALIFICATION_REQUIRED
```

unless the existing Qualification Definition explicitly evaluated the broader capability and the change only activates a previously qualified bounded subset.

---

## 15. Risk-Class Interaction

Qualification must declare the maximum risk class it supports.

A qualification valid through R2 cannot satisfy an R3 action even if the requested capability name is the same.

```text
requested_action_risk <= qualification.maximum_risk_class
```

must hold before authorization.

Higher-risk qualification MAY satisfy a lower-risk action only when all scope, governance, capability, freshness, and assurance requirements also match.

---

## 16. Assurance-Tier Interaction

Qualification also binds the evidence and runtime assurance tier under which evaluation occurred.

A runtime MUST NOT claim a stronger tier merely because the behavioral evaluation passed at a weaker tier.

Example:

```text
qualified at software-process-protected Tier 1
!=
qualified at hardware-backed Tier 3
```

Moving upward in assurance tier requires qualification evidence appropriate to the target tier.

Moving downward MAY invalidate qualification if the qualification requires the stronger controls.

---

## 17. Governance Binding

Qualification MUST bind the exact governance context used during evaluation.

At minimum:

```text
coa_digest
value_architecture_digest
policy_bundle_digest
```

A current runtime may use a qualification only if the verifier can establish compatibility between current governance evidence and the governance context bound to qualification.

No silent governance substitution.

This rule connects qualification directly to the earlier Condition of Agency session-binding lesson.

---

## 18. Qualification Freshness

Qualification freshness is separate from attestation freshness.

Policy SHOULD define maximum age by qualification class/risk.

Conceptually:

```text
attestation freshness: seconds/minutes/hours
runtime credential: minutes/hours
qualification: days/weeks/months
behavioral evidence: policy-defined
```

A currently attested runtime may still be unqualified because its qualification or controlling behavioral evidence expired.

---

## 19. Periodic Requalification

Even without detected change, qualifications SHOULD have finite validity.

Reasons include:

- evaluator/protocol improvements;
- previously unknown failure modes;
- model/provider drift;
- policy evolution;
- capability ecosystem changes;
- long-lived operational drift.

The Qualification Definition MUST specify a maximum validity or requalification interval.

No qualification should be treated as permanent solely because the principal identifier is stable.

---

## 20. Drift Detection

Production ATE SHOULD distinguish:

### Configuration drift
Current configuration no longer matches the qualified profile.

### Behavioral drift
Observed behavior no longer satisfies qualification assumptions.

### Governance drift
Current CoA/VA/policy differs from qualified governance state.

### Capability drift
Tool/resource permissions differ from qualified capability set.

### Provenance drift
Software/model/runtime identity differs from the qualified profile.

Detection of drift MUST cause deterministic policy action, not informal operator interpretation.

---

## 21. Behavioral Drift Signals

Behavioral drift MAY be detected from:

- scheduled regression evaluation;
- audit anomalies;
- incident reports;
- repeated policy denials;
- evaluator-triggered reassessment;
- provider/model change notice;
- post-deployment monitoring evidence.

Drift signals are not automatically proof of misconduct or failure.

They are inputs to a qualification-state decision.

Policy determines whether a signal causes:

```text
NO_ACTION
HEIGHTENED_MONITORING
SUSPEND
PARTIAL_REQUALIFICATION
FULL_REQUALIFICATION
REVOKE
```

---

## 22. Suspension

Suspension is a temporary fail-closed state.

A suspended qualification MUST NOT support new authorization.

Suspension is appropriate when:

- evidence integrity is uncertain;
- an incident is under investigation;
- a material drift signal has not yet been adjudicated;
- issuer status is uncertain;
- required current evidence is temporarily unavailable.

Suspension MUST be explicit and auditable.

Reinstatement requires authorized evidence that the suspension condition is resolved.

---

## 23. Revocation

Revocation permanently invalidates the qualification credential for future grants.

Typical causes:

- proven qualification evidence invalidity;
- issuer decision that qualification was granted in error;
- disqualifying security incident;
- compromised evidence chain;
- subject/profile no longer eligible;
- explicit administrative withdrawal.

Revocation MUST identify:

```text
qualification_id
revocation_reason_code
revoked_at
revocation_epoch
revoking_authority
```

Historical evidence remains verifiable as historical evidence but MUST NOT support new authorization.

---

## 24. Supersession

A newer qualification MAY supersede an older qualification without declaring the old evidence fraudulent.

Supersession is useful when:

- a new profile is qualified;
- qualification definition changes;
- governance version changes;
- periodic requalification completes.

Trust policy SHOULD distinguish:

```text
ACTIVE
SUPERSEDED
EXPIRED
SUSPENDED
REVOKED
```

Only ACTIVE credentials may support new qualification-dependent authorization.

---

## 25. Requalification Lineage

Every replacement qualification SHOULD point to its predecessor.

```text
previous_qualification_id
requalification_reason
preserved_evidence_digests[]
new_evidence_digests[]
superseded_at
```

This creates an auditable qualification history rather than disconnected certificates.

---

## 26. Qualification Authority

Qualification Authority is a distinct trust role.

Its responsibilities are:

- evaluate completeness of the required evidence package;
- enforce active Qualification Definition;
- determine allowed compatibility/requalification path;
- issue/suspend/revoke/supersede qualification credentials;
- preserve decision records.

It SHOULD NOT also be the subject agent.

At higher assurance levels, policy MAY require evaluator independence, second-party approval, or threshold qualification issuance.

---

## 27. Qualification Decision Record

Every qualification decision SHOULD produce an immutable/tamper-evident decision record.

```text
QualificationDecisionRecord {
    decision_id
    subject_principal_id
    qualified_profile_digest
    qualification_class_id
    qualification_definition_version
    evidence_package_digest
    result
    reason_codes[]
    evaluator/issuer references
    decided_at
    validity
    predecessor_qualification_id?
    signature
}
```

Results SHOULD include:

```text
QUALIFIED
NOT_QUALIFIED
SUSPENDED
REQUALIFICATION_REQUIRED
REVOKED
```

---

## 28. No Hidden Waivers

Any waiver of a normal qualification requirement MUST itself be an explicit signed policy artifact.

A waiver MUST define:

- exact requirement waived;
- subject/profile/scope;
- rationale;
- approving authority;
- validity;
- compensating controls;
- risk ceiling.

Silent operator exceptions are prohibited for qualification-dependent authorization.

---

## 29. Qualification and the ATE Envelope

A trust envelope referencing qualification SHOULD include or reference:

```text
qualification_id
qualification_class_id
qualification_definition_version
qualified_profile_digest
qualification_credential_digest
evidence_package_digest
qualification_status
qualification_valid_until
qualification_revocation_epoch
```

The verifier MUST still verify current status rather than trusting an envelope's stale copy of qualification state.

---

## 30. Qualification Verification Flow

```text
Runtime Evidence
      |
      v
VerifiedRuntimeContext
      |
      | profile digest
      v
Qualification Credential
      |
      | issuer valid?
      | current?
      | active?
      | profile exact/compatible?
      | scope/capability/risk sufficient?
      | governance current/compatible?
      v
QUALIFICATION_VALID_FOR_CONTEXT
      |
      v
Action-Specific Trust Decision
```

Qualification verification is deterministic policy evaluation.

---

## 31. Qualification Failure Semantics

Verifier MUST fail closed for at least:

- unknown qualification issuer;
- invalid issuer-role capability;
- bad signature;
- unknown artifact version;
- expired credential;
- not-yet-valid credential;
- suspended qualification;
- revoked qualification;
- superseded qualification when active-only policy applies;
- wrong trust domain;
- wrong subject;
- wrong qualified profile;
- incompatible governance;
- insufficient capability class;
- insufficient risk ceiling;
- insufficient assurance tier;
- stale controlling behavioral evidence where policy requires freshness;
- missing required evidence reference;
- unknown change compatibility.

---

## 32. Required Invariants

### Q-I1 — SCOPED_QUALIFICATION
Qualification is bounded to explicit role/capability/risk/scope/profile/governance/validity constraints.

### Q-I2 — EVIDENCE_BACKED
No qualification credential exists without an immutable evidence package satisfying the active definition.

### Q-I3 — PROFILE_BINDING
Qualification binds the exact evaluated qualified-profile digest or an explicitly signed compatibility path.

### Q-I4 — GOVERNANCE_BINDING
Qualification binds current accepted CoA/VA/policy semantics according to compatibility policy.

### Q-I5 — SEPARATION_FROM_AUTHORIZATION
Qualification alone cannot execute a governed action.

### Q-I6 — CHANGE_FAILS_SAFE
Unknown material change invalidates reuse of qualification pending requalification assessment.

### Q-I7 — CAPABILITY_EXPANSION_REQUALIFIES
Material capability expansion requires requalification unless already explicitly within evaluated scope.

### Q-I8 — FINITE_VALIDITY
Qualification has finite validity/requalification timing.

### Q-I9 — ACTIVE_STATE_REQUIRED
Expired, suspended, revoked, or disallowed superseded qualification cannot support new authorization.

### Q-I10 — REATTESTATION_NOT_REQUALIFICATION
A runtime restart/profile-preserving renewal requires fresh instance evidence but does not automatically require repeat behavioral qualification.

### Q-I11 — LINEAGE
Requalification and supersession preserve auditable relationship to predecessor qualification/evidence.

### Q-I12 — NO_HEURISTIC_COMPATIBILITY
Profile/governance compatibility must be explicit policy, never inferred from names/version labels.

### Q-I13 — RISK_CEILING
Requested risk class cannot exceed qualification risk ceiling.

### Q-I14 — ASSURANCE_BINDING
Qualification at one assurance tier cannot be upward-inferred to a stronger tier.

### Q-I15 — INDEPENDENT_DECISION
Qualification status is issued by an authorized Qualification Authority, not merely asserted by the subject.

---

## 33. Candidate Conformance Tests

This architecture is not yet an experiment protocol, but a future lean qualification milestone should at minimum test:

```text
Q-T0 valid profile + evidence -> qualification accepted
Q-T1 qualification cannot authorize action by itself
Q-T2 wrong profile digest rejected
Q-T3 expired qualification rejected
Q-T4 suspended/revoked qualification rejected
Q-T5 runtime restart with unchanged profile uses re-attestation, not full requalification
Q-T6 model/software material change triggers requalification
Q-T7 capability expansion triggers requalification
Q-T8 VA/CoA material change cannot silently reuse old qualification
Q-T9 explicit compatibility declaration permits only listed delta path
Q-T10 unknown change class fails safe
Q-T11 risk ceiling enforced
Q-T12 assurance-tier upward inference rejected
Q-T13 superseded credential rejected where active-only required
Q-T14 requalification lineage preserved
```

No live experiment is authorized by this document.

---

## 34. Relationship to P2 Runtime Trust

P2 verifies:

```text
this exact runtime instance
matches this qualified runtime profile
and possesses current evidence
```

This architecture defines what makes the referenced qualification meaningful.

The composition is:

```text
Qualification Evidence
       |
       v
Qualification Credential
       |
       +-------------------+
                           |
Runtime Identity + Attestation
       |                   |
       v                   v
          VerifiedRuntimeContext
                   |
                   v
       Qualification valid for context
                   |
                   v
          Bounded Authorization
```

---

## 35. Relationship to Value Architecture and Condition of Agency

Value Architecture is the normative architecture.

Condition of Agency is the commitment architecture.

Qualification is the evidence-backed admission judgment that a particular agent/runtime profile has demonstrated the required properties while bound to those governance artifacts.

Therefore:

> **VA and CoA define what the agent is expected to be governed by; qualification provides evidence that the evaluated runtime profile is acceptable for a bounded role under those requirements.**

Qualification does not prove perfect internal compliance with values. It records what was evaluated, under which governance state, with which evidence, and under what limits the resulting qualification may be relied upon.

---

## 36. Recommended Next Step

Perform:

**ATE Agent Qualification & Requalification Adversarial Review v0.1**

The review should attack at least:

- evidence laundering;
- evaluator self-dealing;
- stale behavioral evidence;
- profile substitution;
- governance substitution;
- capability expansion;
- risk-ceiling bypass;
- qualification downgrade/rollback;
- issuer compromise blast radius;
- ambiguous software/model changes;
- compatibility abuse;
- suspension/revocation race;
- expired credential reuse;
- cross-project qualification reuse;
- qualification credential copying;
- runtime restart confusion;
- partial-requalification overreach;
- hidden waivers.

Only after adversarial review should a qualification experiment/protocol be considered.

---

## 37. Final Statement

ATE should treat agent qualification as an auditable professional credential, not a reputation score.

The decisive questions are:

```text
Qualified for what?
Under which runtime profile?
Against which requirements?
Based on which evidence?
Under which governance state?
At which assurance and risk ceiling?
Until when?
What changes invalidate it?
Who is authorized to say so?
```

If those questions cannot be answered cryptographically and procedurally, the system does not have qualification evidence — it has an assertion.
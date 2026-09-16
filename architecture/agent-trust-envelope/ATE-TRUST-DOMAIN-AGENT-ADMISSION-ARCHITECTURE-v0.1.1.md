# ATE Trust-Domain Agent Admission Architecture v0.1.1

**Status:** REVISED ARCHITECTURE CANDIDATE — DESIGN ONLY — NOT FROZEN  
**Date:** 2026-09-16  
**Program:** Agent Trust Envelope (ATE)  
**Supersedes:** `ATE-TRUST-DOMAIN-AGENT-ADMISSION-ARCHITECTURE-v0.1.md`  
**Adversarial review:** `ATE-TRUST-DOMAIN-AGENT-ADMISSION-ARCHITECTURE-v0.1-CODEX-ADVERSARIAL-REVIEW.md`  
**Adjudication:** `ATE-TRUST-DOMAIN-AGENT-ADMISSION-ARCHITECTURE-v0.1-CODEX-ADJUDICATION.md`  
**Implementation authorization:** NONE

---

## 1. Controlling Principle

> **Qualification establishes that a principal/runtime profile is eligible for a bounded class of work. Trust-domain admission is a local decision to accept that currently qualified principal/profile for a further-narrowed participation scope. Neither qualification nor admission authorizes a governed action.**

Action authorization remains the responsibility of the existing ATE capability, trust-decision composition, and enforcement architecture.

Formally:

```text
QUALIFIED != DOMAIN_ADMITTED
DOMAIN_ADMITTED != AUTHORIZED_TO_ACT
AUTHORIZED_TO_ACT != EXECUTED
```

A governed external effect therefore requires:

```text
Current Qualification
        |
        v
Current Trust-Domain Admission
        |
        v
Capability Authorization bound to that exact pair
        |
        v
Current Runtime / Governance / Risk / Evidence
        |
        v
Action-Specific ATE Trust Decision
        |
        v
Executor Recheck of execution-invalidating dependencies
        |
        v
Governed External Effect
```

No stage implies the next without verification.

---

## 2. Scope

This architecture defines only the missing **local trust-domain admission** semantics.

It does not redefine qualification.

Qualification is controlled by:

`ATE-AGENT-QUALIFICATION-REQUALIFICATION-ARCHITECTURE-v0.1.1.md`

This architecture inherits, without weakening:

- Qualified Runtime Profile;
- Qualification Definition;
- Qualification Evidence Package;
- evidence lifecycle classes;
- evaluator authority and independence;
- Qualification Credential;
- Qualification Status State;
- qualification issuer ceilings;
- risk and assurance eligibility;
- re-attestation;
- compatibility declarations;
- partial/full requalification;
- qualification lineage;
- qualification fail-closed semantics.

This architecture adds only:

1. local Admission Policy;
2. Admission Decision;
3. optional compact Admission Credential;
4. authoritative Admission Status State;
5. admission authority ceilings;
6. admission narrowing/intersection semantics;
7. admission dependency lifecycle semantics;
8. finite review/renewal semantics;
9. exact capability-issuance binding to one qualification/admission pair;
10. mandatory admission integration with trust composition, executor recheck, and audit.

---

## 3. Normative Architectural Dependencies and Precedence

This artifact is subordinate to the existing ATE production architecture family.

Derived protocols/implementations MUST remain consistent with at least:

- `ATE-AGENT-QUALIFICATION-REQUALIFICATION-ARCHITECTURE-v0.1.1.md`;
- `ATE-TRUST-DECISION-COMPOSITION-ARCHITECTURE-v0.1.1.md`;
- `ATE-REVOCATION-TRUST-STATE-MODEL-v0.1.md`;
- `ATE-RISK-ASSURANCE-POLICY-MODEL-v0.1.md`;
- `ATE-TRUST-ROOT-KEY-CUSTODY-MODEL-v0.1.md`;
- `ATE-AUDIT-ACCOUNTABILITY-MODEL-v0.1.md`;
- `ATE-ENFORCEMENT-PLANE-v0.1.md`;
- `ATE-REFERENCE-ARCHITECTURE-COMPONENT-INTERACTION-MODEL-v0.1.md`;
- `ATE-PRODUCTION-REQUIREMENTS-CONFORMANCE-PROFILE-v0.1.md`.

If this candidate conflicts with a controlling ATE requirement, the controlling requirement wins until the conflict is explicitly reconciled and reviewed.

No admission rule may weaken an existing qualification, capability, trust-decision, executor, revocation, audit, or fail-closed invariant.

---

## 4. Non-Goals

Version 0.1.1 does not define:

- a second qualification system;
- a global agent registry;
- a global reputation/trust score;
- a universal certification authority;
- cross-domain federation;
- delegation to child agents;
- admission-based protected-resource credentials;
- action authorization;
- executor implementation technology;
- production database technology;
- a new revocation plane;
- a new audit ledger;
- a new trust-root hierarchy;
- a requirement that admission and qualification run on separate hosts;
- `AdmissionContinuation` or any in-place qualification-replacement mechanism.

Version 0.1.1 is strictly **local-domain only**.

Foreign qualification or admission is unusable under this architecture. Federation remains a separate existing ATE concern and requires an explicitly reviewed composed profile in a future version.

---

## 5. Definitions

### 5.1 Qualified Subject/Profile

A principal/runtime profile with a currently usable qualification under the existing qualification architecture.

### 5.2 Trust Domain

An administrative trust boundary with authoritative local policy over participant admission and governed actions.

### 5.3 Admission

A signed, current, local-domain decision that a particular currently qualified principal/profile may participate in a specific trust domain within a bounded ceiling.

Admission is not action authorization.

### 5.4 Admission Ceiling

The maximum participation scope admission may contribute to downstream authorization.

It may constrain:

```text
role
capability classes
project/resource scope
risk ceiling
assurance eligibility
validity
governance constraints
participation conditions
```

### 5.5 Admission Dependency

Any local condition whose state or validity controls admission issuance, continued admission usability, capability issuance, trust composition, or execution.

Examples:

- admission policy;
- qualification prerequisite;
- Admission Authority delegation;
- required local approval;
- structural-control receipt;
- participation-condition receipt;
- mandatory review deadline;
- required audit availability.

Every controlling admission dependency MUST have explicit lifecycle/change semantics. No implicit snapshot treatment is permitted.

### 5.6 Effective Eligibility

The intersection of one coherent current qualification/admission pair, further narrowed by all other authoritative policy and issuer constraints applicable to the action.

Effective eligibility permits an action authorization request to proceed. It does not itself permit execution.

### 5.7 Capability Admission Binding

A canonical signed/authenticated issuance context that cryptographically binds a CapabilityToken to the exact qualification/admission pair and dependency manifest that authorized issuance.

---

## 6. Architectural Chain

```text
Qualified Principal / Runtime Profile
              |
              v
      Admission Policy
              |
              v
   Admission Dependency Manifest
              |
              v
      Admission Decision
              |
              v
 Admission Credential? (optional presentation)
              |
              +------> Current Admission Status
              |
              v
      AdmissionDecisionContext
              |
              +--------------------+
                                   |
Current Qualification Context     |
              |                    |
              +---------+----------+
                        v
               Effective Eligibility
                        |
                        v
             CapabilityAdmissionBinding
                        |
                        v
                 CapabilityToken
                        |
                        v
              Trust-Decision Composition
                        |
                        v
                  Executor Recheck
                        |
                        v
                   External Effect
```

Admission MUST NOT create a bypass around the existing capability/token/trust-decision/executor chain.

---

## 7. Admission Policy

Admission is controlled by signed, active local policy.

Conceptual minimum:

```text
AdmissionPolicy {
    artifact_type = ATE_ADMISSION_POLICY
    artifact_version

    admission_policy_id
    admission_policy_version
    admission_policy_digest
    policy_epoch

    trust_domain_id
    project_scope

    accepted_qualification_classes[]
    accepted_qualification_definition_digests[]?
    accepted_role_ids[]

    maximum_admitted_capability_classes[]
    prohibited_capability_classes[]
    maximum_admitted_risk_class
    permitted_assurance_profiles[]

    qualification_status_requirements[]
    required_local_approvals[]?
    required_structural_controls[]?
    required_participation_conditions[]?

    admission_dependency_requirements[]

    admission_validity_maximum
    review_interval?
    renewal_rules
    suspension_rules
    withdrawal_rules

    policy_authority_id
    issued_at
    effective_from
    supersedes?
    signature
}
```

The Policy Authority function controls publication/activation of Admission Policy.

An Admission Authority does not gain policy-publishing power merely because it may issue admission decisions.

Unknown, inactive, rolled-back, incompatibly superseded, or lifecycle-incomplete admission policy fails closed.

---

## 8. Admission Dependency Lifecycle Contract

Every controlling admission policy requirement MUST declare its lifecycle/change semantics.

Use the existing ATE lifecycle vocabulary where applicable:

```text
ISSUANCE_SNAPSHOT
CONTINUOUSLY_CURRENT
PERIODICALLY_REFRESHED
```

Each controlling dependency MUST also declare decision/execution change semantics compatible with the Trust-Decision Composition Architecture:

```text
decision_time_class =
    DECISION_TIME_FINAL
    | DECISION_TIME_STABILITY_REQUIRED
    | EXECUTION_TIME_RECHECK_REQUIRED

invalidates_unexecuted_grants_on_change = true | false
execution_recheck_required = true | false
```

Canonical dependency entry:

```text
AdmissionDependencyRule {
    dependency_class
    requirement_id
    required_artifact_type
    authoritative_state_class
    authorized_state_authority

    lifecycle_class
    decision_time_class

    valid_until_rule?
    refresh_deadline_rule?
    compatibility_predicate?

    invalidates_unexecuted_grants_on_change
    execution_recheck_required

    policy_digest
}
```

Mandatory rules:

1. missing lifecycle classification is invalid policy, not snapshot permission;
2. missing change semantics for a controlling mutable dependency is invalid policy;
3. `ISSUANCE_SNAPSHOT` MUST be explicit and policy-authorized;
4. baseline revocation/key/policy invalidation rules cannot be neutralized by labeling a dependency snapshot-only;
5. continuously-current or periodically-refreshed dependency loss deterministically removes admission usability where the dependency controls current admission;
6. a required dependency unavailable at validation time fails closed according to its required lifecycle/recheck semantics.

---

## 9. Admission Dependency Manifest

Each successful Admission Decision binds one immutable manifest of the exact controlling dependency set.

```text
AdmissionDependencyManifest {
    manifest_id

    subject_principal_id
    qualified_profile_digest
    qualification_id
    qualification_credential_digest

    admission_policy_digest
    admission_policy_epoch

    dependencies[] {
        dependency_class
        requirement_id
        artifact_id?
        artifact_digest
        lifecycle_class
        decision_time_class
        authoritative_state_class?
        authoritative_state_object_digest?
        state_epoch?
        valid_until?
        refresh_deadline?
        invalidates_unexecuted_grants_on_change
        execution_recheck_required
    }

    manifest_digest
    created_at
}
```

Manifest completeness MUST be verified against the active Admission Policy.

Unknown, omitted, or unsupported controlling requirements fail closed.

---

## 10. Admission Authority

Admission is a distinct logical signing function, not necessarily a new global service or trust root.

The Trust Root Registry or equivalent authoritative delegation MUST define who may issue admission artifacts and within what ceilings.

```text
AdmissionAuthorityScope {
    authority_id

    permitted_trust_domains[]
    permitted_project_scopes[]
    permitted_roles[]
    permitted_qualification_classes[]
    permitted_capability_classes[]
    maximum_risk_class
    permitted_assurance_profiles[]
    maximum_admission_validity

    may_admit
    may_suspend
    may_withdraw
    may_reinstate

    valid_from
    valid_until
    revocation_handle
}
```

A cryptographically valid admission artifact outside the issuer's delegated ceilings is invalid.

The Admission Authority MUST NOT:

- register itself as trusted;
- expand its own issuer ceilings;
- publish a more permissive Admission Policy unless separately authorized as Policy Authority;
- manufacture required independent approvals;
- hold or derive protected resource authority merely because it admits participants;
- authorize a participant's exact governed action merely by issuing admission.

A low-risk deployment MAY colocate qualification/admission functions, but concentration must be explicit and policy-compatible. Distinct keys on one process do not demonstrate independence where independence is required.

---

## 11. Admission Preconditions

An Admission Decision MAY be `ADMISSION_GRANTED` only when all controlling predicates pass.

At minimum:

```text
active Admission Policy valid and lifecycle-complete
AND Admission Authority currently authorized and within ceilings
AND Qualification Credential valid
AND Qualification Status == ACTIVE
AND subject principal/profile binding valid
AND qualification trust-domain/project scope compatible
AND admission role accepted by policy
AND admitted capability scope subset of qualification scope
AND admitted project/resource scope subset of qualification scope
AND admitted risk ceiling <= qualification risk ceiling
AND admitted assurance eligibility subset of qualification assurance eligibility
AND every required local approval/condition/control satisfies its lifecycle rule
AND AdmissionDependencyManifest complete and valid
AND current revocation/state observations valid and not rolled back
AND no incompatible policy/qualification supersession
AND requested validity within all controlling deadlines
AND required audit persistence available
```

Missing or ambiguous controlling input fails closed.

---

## 12. Narrowing / Intersection Rule

Admission can only narrow qualification.

```text
effective_admission_scope =
    qualification_scope
    INTERSECT admission_policy_ceiling
    INTERSECT admission_authority_ceiling
    INTERSECT admission_decision_ceiling
```

Explicit prohibitions override allows.

Admission MUST NOT increase:

- capability scope;
- resource/project scope;
- risk ceiling;
- assurance eligibility;
- governance latitude;
- portability;
- validity horizon.

Unrelated qualification/admission pairs MUST NOT be unioned to create unsupported authority.

If an action requires capability C, scope S, risk R, and assurance A, one coherent current qualification/admission pair must contain every required dimension.

Version 0.1.1 defines no multi-credential union.

---

## 13. Admission Decision

Every admission attempt produces an immutable signed decision record or equivalent durable authoritative record.

```text
AdmissionDecision {
    artifact_type = ATE_ADMISSION_DECISION
    artifact_version

    admission_decision_id

    subject_principal_id
    qualified_profile_digest

    qualification_id
    qualification_credential_digest
    qualification_status_epoch
    qualification_definition_digest

    admission_policy_id
    admission_policy_version
    admission_policy_digest
    admission_policy_epoch

    admission_dependency_manifest_digest

    trust_domain_id
    project_scope
    role_id

    admitted_capability_classes[]
    excluded_capability_classes[]
    admitted_resource_scope
    maximum_admitted_risk_class
    permitted_assurance_profiles[]

    verdict
    reason_codes[]

    decided_at
    valid_until_if_admitted

    admission_authority_id
    admission_authority_scope_digest
    signature
}
```

Valid verdicts:

```text
ADMISSION_GRANTED
ADMISSION_DENIED
```

No ambiguous result is usable.

The decision MUST bind the exact qualification prerequisite, active policy, and complete admission dependency manifest.

---

## 14. Optional Admission Credential

A separate Admission Credential is optional.

Its purpose, when used, is compact portable presentation of an already-retained signed Admission Decision. It is not a second independent authority decision.

A deployment MAY present the retained signed Admission Decision directly if downstream consumers can verify all required bindings and current status.

If a compact credential is emitted, minimum semantics are:

```text
AdmissionCredential {
    artifact_type = ATE_ADMISSION_CREDENTIAL
    artifact_version

    admission_id
    admission_decision_id
    admission_decision_digest

    subject_principal_id
    qualified_profile_digest

    qualification_id
    qualification_credential_digest

    admission_dependency_manifest_digest

    trust_domain_id
    project_scope
    role_id

    admitted_capability_classes[]
    excluded_capability_classes[]
    admitted_resource_scope
    maximum_admitted_risk_class
    permitted_assurance_profiles[]

    admission_policy_digest
    admission_policy_epoch

    issued_at
    not_before
    valid_until
    review_deadline?

    revocation_handle
    admission_authority_id
    admission_authority_scope_digest
    signature
}
```

Credential derivation MUST be equality- or narrowing-preserving relative to the signed Admission Decision.

The credential is public verifiable evidence, not a bearer secret.

Copying it transfers no admission authority.

---

## 15. Admission Status State

Current admission state MUST NOT be inferred solely from an old signed Admission Decision or Credential.

Admission uses the existing ATE authoritative current-state/revocation control plane.

```text
AdmissionStatusState {
    admission_id
    status
    status_epoch

    trust_domain_id
    state_object_digest

    updated_at
    reason_code
    superseding_admission_id?

    status_authority_id
    signature
}
```

Minimum states:

```text
ACTIVE
SUSPENDED
WITHDRAWN
EXPIRED
SUPERSEDED
REVOKED
REVIEW_REQUIRED
UNKNOWN
```

Only `ACTIVE` may satisfy admission-dependent authorization.

`UNKNOWN != ACTIVE`.

Older ACTIVE state MUST NOT override a newer accepted state epoch.

Admission status is a projection of the shared ATE trust-state plane, not an independent registry.

---

## 16. Admission State Transitions

Reference state machine:

```text
NOT_ADMITTED
     |
UNDER_REVIEW
     |--------------------> DENIED
     v
   ACTIVE
     |--> SUSPENDED ------> ACTIVE | WITHDRAWN | REVOKED | REVIEW_REQUIRED
     |--> REVIEW_REQUIRED -> ACTIVE(new decision) | WITHDRAWN
     |--> SUPERSEDED
     |--> EXPIRED
     |--> WITHDRAWN
     |--> REVOKED
```

Historical decisions and credentials remain immutable/auditable.

No transition silently edits an old artifact.

---

## 17. Qualification Dependency Closure

Admission remains usable only while its exact bound qualification prerequisite remains usable under the qualification architecture.

Admission becomes non-usable when that qualification becomes:

```text
SUSPENDED
REQUALIFICATION_REQUIRED
EXPIRED
SUPERSEDED
REVOKED
NOT_QUALIFIED
```

There is no continuation exception in v0.1.1.

Loss of qualification usability MUST propagate to dependent admission usability.

An old ACTIVE admission artifact cannot override current qualification state.

---

## 18. Qualification Replacement Requires New Admission

An admission bound to qualification Q1 MUST NOT begin depending on Q2.

If Q1 is replaced or superseded:

```text
Q1-based admission -> non-usable
Q2 -> requires a new Admission Decision
new admission -> requires new capability authorization where admission controls capability issuance
```

No pending CapabilityToken or TrustDecision may switch prerequisite pairs in place.

A changed pair changes authorization semantics and requires a fresh authorization attempt.

A revoked or superseded identifier MUST NOT be revived by replacing bytes or redirecting a reference.

---

## 19. Admission Review and Renewal

Admission is finite and reviewable.

Policy may require a review deadline earlier than admission expiry.

If a mandatory review deadline is reached without successful renewal:

```text
ACTIVE -> REVIEW_REQUIRED
```

and admission becomes unusable for new and unexecuted admission-dependent authority according to the signed dependency contract.

Renewal MUST evaluate:

- current qualification;
- current Admission Policy;
- current Admission Authority ceilings;
- current dependency lifecycle state;
- current approvals/conditions;
- current admission state.

Renewal MUST NOT silently widen admission.

Expanded participation requires an explicit new Admission Decision and, if expansion exceeds qualification, prior requalification.

---

## 20. Local-Only Boundary

Version 0.1.1 is unconditionally local-domain only.

Under this architecture:

```text
foreign qualification -> NOT USABLE FOR LOCAL ADMISSION
foreign admission     -> NOT USABLE FOR LOCAL AUTHORITY
```

No exception is defined here.

The existing ATE federation architecture may support foreign evidence in a future explicitly composed and separately reviewed admission profile. Until then, no foreign mapping, allowlist, same-name role, or transitive admission claim is usable.

---

## 21. Admission Decision Context

Before capability issuance and trust composition, admission semantics SHALL be normalized.

```text
AdmissionDecisionContext {
    admission_id
    admission_presentation_digest
    admission_decision_digest

    subject_principal_id
    qualified_profile_digest

    qualification_id
    qualification_credential_digest

    status
    status_epoch

    trust_domain_id
    project_scope
    role_id

    capability_taxonomy_digest
    authorizable_capability_classes[]
    excluded_capability_classes[]
    admitted_resource_scope
    maximum_risk_class
    authorizable_assurance_profiles[]

    admission_policy_digest
    admission_policy_epoch
    admission_dependency_manifest_digest

    valid_until
    review_deadline?

    context_digest
}
```

Grantability requires at least:

```text
status == ACTIVE
AND subject/profile match current VerifiedRuntimeContext
AND exact bound qualification is current and ACTIVE
AND all CONTINUOUSLY_CURRENT/PERIODICALLY_REFRESHED admission dependencies satisfy policy
AND action inside qualification authority
AND action inside admission authority
AND risk inside both qualification and admission ceilings
AND required assurance supported by both qualification and admission
AND trust/project/resource scope compatible
AND current policy/state observations current and not rolled back
```

Executable authority is the intersection, never the union.

---

## 22. Capability Admission Binding

When local policy requires admission, capability issuance MUST create one canonical binding to the exact pair that authorized issuance.

```text
CapabilityAdmissionBinding {
    binding_id
    authorization_instance_id

    subject_principal_id
    qualified_profile_digest

    qualification_id
    qualification_credential_digest
    qualification_decision_context_digest

    admission_id
    admission_decision_digest
    admission_decision_context_digest
    admission_dependency_manifest_digest

    admission_policy_digest
    admission_policy_epoch
    admission_status_epoch
    qualification_status_epoch

    trust_domain_id
    project_scope

    binding_valid_until

    capability_issuer_id
    binding_digest
    signature_or_authenticated_issuer_binding
}
```

The `binding_digest` MUST be cryptographically included in the signed CapabilityToken or a mandatory signed CapabilityToken extension.

Therefore the token's signed bytes commit to the exact qualification/admission issuance pair.

A post-issuance audit record MUST also bind:

```text
capability_token_id
capability_token_digest
binding_digest
```

for causal reconstruction.

---

## 23. Mandatory Capability-Issuance Integration

A CapabilityToken MUST NOT be issued for an admission-dependent role unless:

```text
qualification context current and valid
AND admission context current and ACTIVE
AND CapabilityAdmissionBinding created for that exact pair
AND AdmissionDependencyManifest complete/current as required
AND requested capability <= qualification ceiling
AND requested capability <= admission ceiling
AND requested risk <= both ceilings
AND required assurance supported by both
AND project/resource scope inside both
AND all current policy/state/dependency predicates pass
```

Where admission is required, absence of admission is denial.

The capability issuer cannot treat admission as advisory metadata.

A fresh Admission Decision does not rehabilitate an older token issued under another admission. New pair => new capability authorization.

---

## 24. Exact Pair Equality at Trust Composition

Trust composition MUST enforce exact equality between:

1. the qualification/admission pair committed by the CapabilityToken's `CapabilityAdmissionBinding`; and
2. the qualification/admission contexts selected for the current TrustDecision.

Required equality includes at least:

```text
subject_principal_id
qualified_profile_digest
qualification_id + credential digest
admission_id + decision digest
admission_dependency_manifest_digest
trust_domain_id
project_scope
```

Equivalent ceilings do not permit substitution.

A1 cannot be replaced by A2 for CT1 merely because A2 grants the same capability set.

Q1 cannot be replaced by Q2 for CT1 merely because Q2 is compatible.

If the controlling pair changes:

```text
old capability authorization -> unusable for new pair
new pair -> new capability authorization
```

---

## 25. Mandatory Trust-Decision Composition Integration

The existing Trust-Decision Composition Architecture MUST be extended by a versioned profile/required signed extension so admission is a controlling dependency.

The semantic context SHALL include at least:

```text
admission_decision_context_digest
capability_admission_binding_digest
admission_dependency_manifest_digest
```

`CapabilityDecisionContext` SHALL include the same capability admission binding digest.

`TrustDecisionInput` and `TrustDecision` SHALL carry the required binding/dependency digests directly or through one mandatory signed semantic-context digest whose semantics require them.

The current state vector SHALL include authoritative admission state/policy/dependency observations where controlling.

Trust composition independently verifies:

```text
Qualification
INTERSECT Admission
INTERSECT CapabilityToken bound to that exact pair
INTERSECT Current Policy / Risk / Assurance / Governance / Dependency State
```

---

## 26. Execution-Invalidating Admission Dependencies

Admission status and bound qualification status are execution-invalidating dependencies for unexecuted grants whenever local policy requires admission.

Other admission-specific dependencies are execution-invalidating exactly according to their mandatory lifecycle/change declarations.

At minimum, these changes invalidate dependent unexecuted authority:

```text
Admission ACTIVE -> SUSPENDED
Admission ACTIVE -> REVIEW_REQUIRED
Admission ACTIVE -> WITHDRAWN
Admission ACTIVE -> REVOKED
Admission ACTIVE -> EXPIRED
Admission ACTIVE -> SUPERSEDED
bound qualification becomes non-ACTIVE/non-usable
admission policy becomes incompatibly superseded/revoked
CapabilityAdmissionBinding pair no longer matches current required pair
any dependency marked invalidates_unexecuted_grants_on_change changes incompatibly
```

Policy MUST NOT omit a baseline-required execution recheck.

The architecture does not claim revocation can reverse an already committed irreversible external effect.

---

## 27. Executor Recheck Contract

Immediately before protected credential release or external effect, the Capability Executor MUST perform every admission-related recheck required by the signed TrustDecision/composition profile.

The executor need not rerun raw qualification or admission evaluation.

It MUST verify, where controlling:

- TrustDecision currentness;
- CapabilityToken currentness;
- `CapabilityAdmissionBinding` digest matches the signed token and TrustDecision semantics;
- exact qualification/admission pair equality;
- qualification current state;
- admission current state;
- admission policy epoch/currentness;
- all admission dependencies marked execution recheck required;
- revocation state;
- signed execution-recheck requirements.

If any required dependency is unavailable, stale, rolled back, invalid, changed incompatibly, or pair-mismatched:

```text
NO PROTECTED CREDENTIAL RELEASE
NO EXTERNAL EFFECT
```

Fail closed.

---

## 28. Validity Horizon

No admission-dependent authorization may outlive its controlling dependencies.

```text
TrustDecision.valid_until <= min(
    existing ATE deadlines,
    qualification validity,
    admission validity,
    admission review deadline where mandatory,
    CapabilityAdmissionBinding validity,
    continuously-current admission dependency deadlines,
    periodic refresh deadlines where lease-like,
    continuing approval validity,
    stricter risk/composition freshness deadline
)
```

A longer-lived admission does not lengthen any shorter controlling deadline.

---

## 29. Point-in-Time Consistency and TOCTOU

Admission uses the existing ATE state-observation and stability model.

Before admission release:

1. capture authoritative qualification, admission-policy, trust-root, dependency, approval, and revocation state;
2. evaluate all admission predicates;
3. verify lifecycle classification completeness;
4. immediately before durable issuance, re-read dependencies marked decision-time stability required;
5. if controlling state changed, restart or deny according to bounded policy;
6. persist required audit/evidence before releasing admission presentation.

Before CapabilityToken issuance:

1. normalize current qualification/admission contexts;
2. verify exact coherent pair;
3. build `CapabilityAdmissionBinding`;
4. recheck stability-required issuance dependencies;
5. bind its digest into the signed token;
6. persist causal issuance evidence.

Before ATE grant issuance and external effect, existing composition/executor stability/recheck contracts apply.

---

## 30. Approvals and Independence

Where Admission Policy requires human or independent authority approval, each approval MUST bind the exact relevant context.

Minimum binding:

```text
subject_principal_id
qualified_profile_digest
qualification_id + digest
trust_domain_id
project_scope
role_id
admission_policy_digest + epoch
admission ceiling digest
approval role/class
issued_at
valid_until
```

Every approval requirement also receives an explicit lifecycle/change classification under §8.

Required independence is machine-verifiable policy.

Different keys do not imply independence when one compromise domain controls both and policy requires independent control.

The participant MUST NOT possess or control admission, qualification, approval, or policy signing authority, including signing-oracle access that defeats intended separation.

---

## 31. Canonical Encoding and Versioning

Admission artifacts inherit normative ATE encoding, canonicalization, versioning, signature-domain-separation, and unsupported-version fail-closed rules.

No competing serialization system is introduced.

For every admission artifact:

```text
artifact_type
artifact_version
canonical bytes
domain-separated signature context
```

MUST be unambiguous.

Unknown controlling versions, constraints, required extensions, or ambiguous missing/empty semantics fail closed.

---

## 32. Audit and Evidence Requirements

Admission reuses the existing ATE audit/evidence plane.

Durable evidence must permit reconstruction of:

- exact subject principal and qualified profile;
- exact qualification prerequisite/status epoch;
- exact Admission Policy digest/epoch;
- exact Admission Dependency Manifest;
- exact Admission Decision and optional Admission Credential digest;
- exact admitted role/capability/resource/risk/assurance ceiling;
- Admission Authority and scope digest;
- dependency lifecycle/change classifications;
- state transitions/epochs;
- capability issuance;
- exact `CapabilityAdmissionBinding`;
- CapabilityToken digest bound to that binding;
- TrustDecision semantic context;
- executor dependency recheck result;
- resulting execution/non-execution status.

Required issuance persistence MUST precede release where policy declares durability mandatory.

If required persistence fails:

```text
ADMISSION/CAPABILITY ARTIFACT NOT RELEASED
```

as applicable.

Denied/malformed requests remain auditable without inventing a subject identity when parsing/identity establishment failed.

---

## 33. Non-Transferability and Delegation

Standing qualification/admission artifacts are reusable public evidence, not bearer capabilities.

Copying them grants nothing without matching authenticated principal/profile/current context.

Version 0.1.1 permits no implicit:

- delegation;
- transfer;
- redelegation;
- child-agent inheritance;
- ownership transfer;
- session inheritance;
- reuse of another principal's action evidence.

A child or delegated principal requires its own qualification/admission/current runtime context unless a future separately reviewed delegation architecture defines otherwise.

---

## 34. Fail-Closed Conditions

Admission-dependent authorization MUST fail closed for any controlling condition including:

- unknown/unauthorized Admission Authority;
- Admission Authority ceiling violation;
- bad signature;
- unsupported artifact version;
- inactive/unknown/rolled-back Admission Policy;
- lifecycle-incomplete Admission Policy;
- incomplete/invalid Admission Dependency Manifest;
- invalid/non-ACTIVE qualification;
- wrong subject/profile;
- qualification/admission pair mismatch;
- CapabilityAdmissionBinding mismatch;
- capability token issued under a different qualification/admission pair;
- capability/resource scope expansion;
- risk ceiling violation;
- assurance incompatibility;
- missing/expired/revoked required approval;
- non-ACTIVE admission status;
- admission-state rollback;
- expired admission;
- missed mandatory review deadline;
- qualification replacement without new admission;
- policy supersession incompatible with current admission;
- missing/unsupported dependency lifecycle classification;
- failed continuously-current/periodic dependency;
- unavailable required current state;
- stale required state observation;
- mandatory audit persistence failure;
- invalid cross-artifact digest/binding;
- unsupported required extension;
- executor inability to perform a required final recheck;
- any attempt to use foreign qualification/admission under v0.1.1.

```text
UNKNOWN != ADMITTED
ERROR   != ADMITTED
MISSING != ADMITTED
STALE   != ADMITTED
```

---

## 35. Revised Architectural Invariants

These invariants are candidates for final adversarial consistency review and are **not frozen by this candidate**.

### A-I1 QUALIFICATION_PRECEDES_ADMISSION
No admission without a currently valid qualification prerequisite.

### A-I2 ADMISSION_NARROWS
Admission cannot widen qualification capability, scope, risk, assurance, governance latitude, portability, or validity.

### A-I3 LOCAL_DOMAIN_CONTROL
Admission is an explicit local trust-domain decision; qualification alone does not force participation.

### A-I4 SEPARATION_FROM_AUTHORIZATION
Admission alone cannot authorize a governed action.

### A-I5 COHERENT_PAIR
Downstream authority derives from one coherent current qualification/admission pair; unrelated credentials are not unioned.

### A-I6 EXACT_PROFILE_BINDING
Admission binds the exact qualified principal/profile.

### A-I7 MONOTONIC_ADMISSION_STATE
Older ACTIVE state cannot override newer suspension, withdrawal, revocation, expiry, review-required, or supersession state.

### A-I8 QUALIFICATION_DEPENDENCY_CLOSURE
Loss or replacement of the bound qualification removes dependent admission usability.

### A-I9 NO_IN_PLACE_REPLACEMENT
A new qualification requires a new Admission Decision; pending authority cannot switch prerequisite pairs.

### A-I10 DEPENDENCY_LIFECYCLE_COMPLETE
Every controlling admission-specific dependency has explicit lifecycle/change semantics; missing classification fails closed.

### A-I11 CURRENT_STATE_PROVENANCE
Admission status/policy/dependency observations have authorized sources, exact digests, epochs, freshness, and rollback protection.

### A-I12 ASSURANCE_BINDING
Admission cannot imply assurance not supported by qualification/current action requirements.

### A-I13 AUTHORITY_CEILINGS
Admission signatures are valid only within root-delegated domain/project/role/capability/risk/assurance/lifetime ceilings.

### A-I14 NO_CIRCULAR_TRUST
Admission authorities cannot self-register, widen their ceilings, or manufacture independent policy/approval authority.

### A-I15 DECISION_PRESENTATION_COHERENCE
Any Admission Credential is digest-bound to a retained Admission Decision and may only preserve or narrow its fields.

### A-I16 FINITE_ADMISSION
Admission has finite validity and deterministic review/renewal semantics.

### A-I17 CAPABILITY_ISSUANCE_PAIR_BINDING
Every admission-dependent CapabilityToken cryptographically commits to the exact qualification/admission pair and dependency manifest that authorized issuance.

### A-I18 PAIR_SUBSTITUTION_FORBIDDEN
Trust composition cannot replace the token's issuance pair with a different qualification or admission, even if scope is equivalent.

### A-I19 COMPOSITION_BINDING
Admission, the CapabilityAdmissionBinding, and admission dependency manifest are mandatory signed semantic dependencies where admission is required.

### A-I20 PENDING_EXECUTION_CLOSURE
Loss/change of an execution-invalidating qualification/admission dependency invalidates dependent unexecuted authority.

### A-I21 EXECUTOR_RECHECK
Every dependency marked execution-recheck-required is validated before protected credential release/external effect.

### A-I22 AUDIT_CAUSALITY
Admission issuance, dependency manifest, capability binding, token, trust decision, recheck, and execution remain causally reconstructable.

### A-I23 NO_IMPLICIT_TRANSFER
Credentials, child agents, sessions, delegation, and ownership changes do not inherit admission authority implicitly.

### A-I24 STRICT_LOCAL_ONLY
Foreign qualification/admission is unusable under v0.1.1.

### A-I25 BASELINE_PRECEDENCE
Admission extends the authoritative qualification/composition/revocation/audit architecture and cannot redefine or weaken it.

---

## 36. Candidate Lean Admission Tests

These are design candidates only. No experiment is authorized.

```text
A-T0  ACTIVE qualification + valid local policy/dependencies -> admission may be granted
A-T1  qualification valid but no admission -> admission-required capability denied
A-T2  admission scope wider than qualification -> denied
A-T3  admission assurance/risk exceeds qualification -> denied
A-T4  wrong principal/profile presents copied admission -> denied
A-T5  newer SUSPENDED/WITHDRAWN admission defeats older ACTIVE presentation
A-T6  bound qualification becomes non-ACTIVE -> dependent admission unusable
A-T7  token CT1 bound to Q1/A1; A1 withdrawn; new A2 exists -> CT1 cannot compose under A2
A-T8  token CT1 bound to Q1/A1; Q1 replaced by Q2 -> CT1 cannot compose under Q2
A-T9  already-issued but unexecuted grant + admission withdrawal -> execution denied
A-T10 stale/rolled-back admission policy/status observation -> denied
A-T11 unauthorized/out-of-ceiling admission signer -> denied
A-T12 admission policy omits lifecycle classification for controlling dependency -> invalid/denied
A-T13 continuously-current admission dependency expires before execution -> execution denied
A-T14 explicit issuance-snapshot dependency remains historical without false currentness claim
A-T15 admission presentation fields wider than signed decision -> denied
A-T16 required current-state service unavailable -> denied
A-T17 mandatory audit persistence unavailable at admission issuance -> no release
A-T18 unrelated qualification/admission credentials cannot be unioned
A-T19 foreign qualification/admission -> denied under v0.1.1
A-T20 unchanged exact pair + unchanged dependencies -> composition/recheck succeeds
A-T21 child/delegated principal cannot inherit admission implicitly
A-T22 new qualification Q2 requires new Admission Decision A2
A-T23 fresh A2 requires fresh capability authorization; old token under A1 remains unusable
```

These cases are not substitutes for qualification or broader ATE conformance suites.

---

## 37. Minimal Proof-of-Concept Boundary

A future first PoC should prove only the new admission boundary.

A useful narrow claim:

> Given an already-valid local qualification fixture, the trust domain can issue a narrower admission; admission absence/withdrawal prevents admission-dependent capability/execution; every admission-dependent token is cryptographically bound to the exact qualification/admission pair that authorized issuance; and local admission dependencies obey explicit lifecycle/currentness semantics.

The PoC may use deterministic local fixtures for pre-existing qualification/runtime evidence so long as claims remain limited to admission semantics.

The PoC MUST NOT claim production federation, universal identity, global trustworthiness, full qualification issuance correctness, production HSM/key custody, distributed revocation consistency, or general model safety.

---

## 38. Security Claim Boundary

If this architecture is later frozen and correctly implemented, the intended claim is:

> A local trust domain can require an already-qualified AI agent/runtime profile to obtain a separate, current, scope-narrowing admission before receiving admission-dependent capability authorization; that capability authorization is cryptographically bound to the exact qualification/admission pair that justified issuance; and loss of any execution-invalidating qualification/admission dependency closes pending authority through signed trust-composition and executor-recheck rules.

It does not prove universal trustworthiness.

It does not grant ambient authority.

It does not replace action-specific ATE verification.

---

## 39. Required Focused Review Before Freeze

Before freeze, a focused adversarial consistency review MUST attempt to break at least:

1. exact token-to-qualification/admission issuance binding;
2. pair substitution after token issuance;
3. qualification replacement requiring new admission;
4. new admission requiring new capability authorization for the new pair;
5. admission dependency lifecycle completeness;
6. snapshot vs continuously-current vs periodic dependency behavior;
7. pending grant invalidation;
8. executor recheck completeness;
9. admission signer ceilings;
10. risk/assurance containment;
11. decision/presentation derivation coherence;
12. audit release ordering/causal reconstruction;
13. unavailable-state fail-closed behavior;
14. strict local-only boundary;
15. consistency with Trust-Decision Composition Architecture v0.1.1;
16. consistency with Agent Qualification & Requalification Architecture v0.1.1.

Any substantive unresolved contradiction blocks freeze.

---

## 40. Recommended Next Step

Perform one focused adversarial consistency review of this exact v0.1.1 candidate against the controlling ATE baseline and the three blocking findings from the v0.1 Codex review.

Do not implement.

Do not design the admission conformance protocol until that review disposition permits it.
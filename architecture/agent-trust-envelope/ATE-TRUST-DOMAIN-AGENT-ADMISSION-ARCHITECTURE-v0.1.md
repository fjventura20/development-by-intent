# ATE Trust-Domain Agent Admission Architecture v0.1

**Status:** DRAFT — DESIGN ONLY — NOT FROZEN  
**Date:** 2026-09-16  
**Program:** Agent Trust Envelope (ATE)  
**Purpose:** define the local trust-domain admission layer that sits between evidence-backed qualification and action-specific ATE authorization.  
**Implementation authorization:** NONE

---

## 1. Controlling Principle

> **Qualification establishes that a principal/runtime profile is eligible for a bounded class of work. Admission is a local trust-domain decision to accept that currently qualified principal/profile for a further-narrowed participation scope. Neither qualification nor admission authorizes a governed action.**

Action authorization remains the responsibility of the existing ATE trust-decision composition and enforcement architecture.

Formally:

```text
QUALIFIED != DOMAIN_ADMITTED
DOMAIN_ADMITTED != AUTHORIZED_TO_ACT
AUTHORIZED_TO_ACT != EXECUTED
```

A governed external effect therefore requires all applicable stages:

```text
Current Qualification
        |
        v
Current Trust-Domain Admission
        |
        v
Current Runtime / Governance / Risk / Evidence
        |
        v
Action-Specific Capability + ATE Trust Decision
        |
        v
Executor Recheck
        |
        v
Governed External Effect
```

No stage implies the next without verification.

---

## 2. Scope

This architecture defines only the missing **trust-domain admission** semantics.

It does **not** redefine qualification.

Qualification is controlled by:

`ATE-AGENT-QUALIFICATION-REQUALIFICATION-ARCHITECTURE-v0.1.1.md`

This architecture inherits its definitions for:

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
3. Admission Credential;
4. authoritative Admission Status State;
5. admission authority ceilings;
6. admission narrowing/intersection semantics;
7. admission lifecycle and renewal;
8. admission current-state and rollback rules;
9. mandatory integration with capability issuance, trust composition, executor recheck, and audit.

---

## 3. Normative Architectural Dependencies and Precedence

This artifact is subordinate to the existing ATE production architecture family.

At minimum, implementations/protocols derived from this architecture MUST remain consistent with:

- `ATE-AGENT-QUALIFICATION-REQUALIFICATION-ARCHITECTURE-v0.1.1.md`;
- `ATE-TRUST-DECISION-COMPOSITION-ARCHITECTURE-v0.1.1.md`;
- `ATE-REVOCATION-TRUST-STATE-MODEL-v0.1.md`;
- `ATE-RISK-ASSURANCE-POLICY-MODEL-v0.1.md`;
- `ATE-TRUST-ROOT-KEY-CUSTODY-MODEL-v0.1.md`;
- `ATE-AUDIT-ACCOUNTABILITY-MODEL-v0.1.md`;
- `ATE-ENFORCEMENT-PLANE-v0.1.md`;
- `ATE-REFERENCE-ARCHITECTURE-COMPONENT-INTERACTION-MODEL-v0.1.md`;
- `ATE-PRODUCTION-REQUIREMENTS-CONFORMANCE-PROFILE-v0.1.md`.

If this draft conflicts with a frozen or controlling ATE requirement, the controlling requirement wins until the conflict is explicitly reconciled and reviewed.

No admission rule may weaken an existing qualification, trust-decision, executor, revocation, audit, or fail-closed invariant.

---

## 4. Non-Goals

Version 0.1 does not define:

- a second qualification system;
- a global agent registry;
- a global reputation or trust score;
- a universal certification authority;
- cross-domain federation semantics beyond explicitly rejecting implicit portability;
- delegation to child agents;
- admission-based resource credentials;
- action authorization;
- executor implementation technology;
- production database technology;
- a new revocation plane;
- a new audit ledger;
- a new trust-root hierarchy;
- a requirement that admission and qualification run on separate hosts;
- a requirement that every admitted agent be allowed every action inside its admitted scope.

Version 0.1 is intentionally **local-domain only** unless and until the existing ATE federation model is explicitly composed in a future version.

---

## 5. Definitions

### 5.1 Qualified Subject/Profile

A principal/runtime profile with a currently usable qualification under the existing qualification architecture.

### 5.2 Trust Domain

An administrative trust boundary with authoritative local policy over participant admission and governed actions.

### 5.3 Admission

A signed, current, local-domain decision that a particular currently qualified subject/profile may participate in a specific trust domain within a bounded ceiling.

Admission is not action authorization.

### 5.4 Admission Ceiling

The maximum participation scope that admission may contribute to downstream authorization.

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

### 5.5 Effective Eligibility

The intersection of current qualification and current admission, further narrowed by all other authoritative policy/issuer/federation constraints applicable to the action.

Effective eligibility permits an action authorization request to proceed to ATE composition. It does not itself permit execution.

---

## 6. Architectural Chain

```text
Qualified Principal / Runtime Profile
              |
              v
      Admission Policy
              |
              v
      Admission Decision
              |
              v
     Admission Credential
              |
              +------> Current Admission Status
              |
              v
      AdmissionDecisionContext
              |
              v
 Current Qualification Context
              |
              +-----------------------+
                                      |
                                      v
                          Effective Eligibility
                                      |
                                      v
                         Capability Authorization
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
    qualification_freshness_requirements[]?
    required_local_approvals[]?
    required_structural_controls[]?
    required_participation_conditions[]?

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

Unknown, inactive, rollbacked, or incompatibly superseded admission policy fails closed.

---

## 8. Admission Authority

Admission is a distinct **logical signing function**, not necessarily a new global service or trust root.

The Trust Root Registry (or equivalent authoritative delegation) MUST explicitly define who may issue admission artifacts and within what ceilings.

Minimum Admission Authority ceiling semantics:

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
    may_issue_continuation

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
- authorize the participant's exact governed action merely by issuing admission.

A low-risk deployment MAY colocate qualification/admission functions, but concentration must be explicit and policy-compatible. Distinct keys on one process do not demonstrate independence where independence is required.

---

## 9. Admission Preconditions

An Admission Decision MAY be `ADMITTED` only when all controlling predicates pass.

At minimum:

```text
active Admission Policy valid
AND Admission Authority currently authorized and within ceilings
AND Qualification Credential valid
AND Qualification Status == ACTIVE
AND subject principal/profile binding valid
AND qualification trust-domain/project portability compatible
AND admission role accepted by policy
AND admitted capability scope subset of qualification scope
AND admitted project/resource scope subset of qualification scope
AND admitted risk ceiling <= qualification risk ceiling
AND admitted assurance eligibility subset of qualification assurance eligibility
AND required local approvals current and context-bound
AND required participation/structural conditions satisfied
AND current revocation/state observations valid and not rolled back
AND no incompatible policy/qualification supersession
AND requested validity within all controlling deadlines
AND required audit persistence available
```

Missing or ambiguous controlling input fails closed.

---

## 10. Narrowing / Intersection Rule

Admission can only narrow qualification.

Define:

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

Unrelated qualification/admission pairs MUST NOT be unioned to create a capability set unsupported by one coherent current pair.

If an action requires capability C, scope S, risk R, and assurance A, one coherent current qualification/admission pair must contain all required dimensions unless a separately specified, reviewed multi-credential composition architecture explicitly permits otherwise.

Version 0.1 defines no such multi-credential union.

---

## 11. Admission Decision

Every admission attempt produces an immutable signed decision record or equivalent durable authoritative record.

Conceptual structure:

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

    trust_domain_id
    project_scope
    role_id

    admitted_capability_classes[]
    excluded_capability_classes[]
    admitted_resource_scope
    maximum_admitted_risk_class
    permitted_assurance_profiles[]

    approval_context_digests[]?
    participation_condition_digests[]?

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

The decision MUST bind the exact qualification prerequisite and exact active admission policy used.

---

## 12. Admission Credential

An Admission Credential MAY be issued only after a valid `ADMISSION_GRANTED` decision.

Minimum conceptual credential:

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

A credential MUST NOT introduce a field, capability, scope, risk, assurance, or lifetime that was not authorized by the decision.

The credential is public/verifiable evidence, not a bearer secret.

Copying it does not transfer admission because downstream verification binds it to the exact principal/profile/current runtime context.

---

## 13. Admission Status State

Current admission state MUST NOT be inferred solely from an old signed Admission Credential.

Admission uses the existing ATE authoritative current-state/revocation control plane.

Conceptual projection:

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

Admission status is a projection of the shared ATE trust-state plane, not an independent competing registry.

---

## 14. Admission State Transitions

Reference state machine:

```text
NOT_ADMITTED
     |
UNDER_REVIEW
     |--------------------> DENIED
     v
   ACTIVE
     |--> SUSPENDED ------> ACTIVE | WITHDRAWN | REVOKED | REVIEW_REQUIRED
     |--> REVIEW_REQUIRED -> ACTIVE(new decision/continuation) | WITHDRAWN
     |--> SUPERSEDED
     |--> EXPIRED
     |--> WITHDRAWN
     |--> REVOKED
```

Historical decisions and credentials remain immutable/auditable.

State transition semantics MUST distinguish:

- temporary suspension;
- administrative withdrawal;
- security revocation;
- planned expiration;
- supersession by a newer admission;
- mandatory review.

No transition silently edits an old credential.

---

## 15. Qualification Dependency Closure

Admission remains usable only while its controlling qualification prerequisite remains usable under the qualification architecture.

At minimum, admission becomes non-usable when the bound qualification becomes:

```text
SUSPENDED
REQUALIFICATION_REQUIRED
EXPIRED
SUPERSEDED (unless an authorized continuation path exists)
REVOKED
NOT_QUALIFIED
```

Loss of qualification usability MUST propagate to dependent admission usability.

An old `ACTIVE` Admission Credential cannot override current qualification state.

Admission does not rewrite qualification state; it consumes it as an authoritative dependency.

---

## 16. Qualification Replacement / Admission Continuation

An admission bound to qualification Q1 MUST NOT silently begin depending on Q2.

If Q1 is replaced, the domain must use one of:

1. a new Admission Decision + Admission Credential; or
2. an explicit signed `AdmissionContinuation` permitted by policy.

Conceptual continuation:

```text
AdmissionContinuation {
    admission_id
    prior_qualification_id
    prior_qualification_digest
    replacement_qualification_id
    replacement_qualification_digest

    compatibility_decision_digest

    preserved_role
    preserved_capability_scope
    preserved_resource_scope
    preserved_risk_ceiling
    preserved_assurance_profiles

    admission_policy_digest
    policy_epoch

    valid_until
    issuer
    signature
}
```

Continuation MUST be non-expanding.

Unknown material change defaults to denial / review required.

A revoked identifier MUST NOT be revived by replacing its bytes or pointing it to a new prerequisite.

---

## 17. Admission Review and Renewal

Admission is finite and reviewable.

Policy may require a review deadline earlier than credential expiry.

If a mandatory review deadline is reached without successful renewal:

```text
ACTIVE -> REVIEW_REQUIRED
```

and the admission becomes unusable for new or unexecuted admission-dependent grants according to the execution-invalidating contract.

Renewal MUST evaluate current qualification, current policy, current authority ceilings, current approvals/conditions, and current admission state.

Renewal MUST NOT silently widen admission.

Expanded participation requires an explicit new admission decision and, where the expansion exceeds qualification, prior requalification.

---

## 18. Local-Only Scope and Federation Boundary

Version 0.1 is local-domain only.

A qualification issued outside the local trust domain MAY be considered only if an existing ATE federation/recognition policy is explicitly applied in a future composed profile.

This architecture grants no implicit rule that:

```text
Domain A qualification
=> Domain B admission eligibility
```

and absolutely no rule that:

```text
Domain B admission
=> Domain C recognition
```

Identical role names across domains do not imply semantic equivalence.

Until federation is explicitly composed:

```text
foreign qualification / foreign admission -> NOT USABLE FOR LOCAL ADMISSION
```

unless controlling local policy already provides a reviewed, explicit mapping under the existing federation architecture.

No local admission may conceal or erase a controlling foreign dependency.

---

## 19. Admission Decision Context for ATE Composition

Before ATE trust composition, admission semantics SHALL be normalized.

Conceptual context:

```text
AdmissionDecisionContext {
    admission_id
    admission_credential_digest
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

    valid_until
    review_deadline?

    approval_context_digests[]?
    participation_condition_digests[]?

    context_digest
}
```

Grant requires at least:

```text
status == ACTIVE
AND subject/profile match current VerifiedRuntimeContext
AND bound qualification is current and ACTIVE
AND action inside qualification authority
AND action inside admission authority
AND action inside CapabilityToken authority
AND risk inside both qualification and admission ceilings
AND required assurance supported by both qualification and admission
AND trust/project/resource scope compatible
AND policy/current-state observations current and not rolled back
```

Executable authority is the intersection, never the union.

---

## 20. Mandatory Capability-Issuance Integration

Capability issuance MUST consume current qualification and current admission.

A CapabilityToken MUST NOT be issued for an admission-dependent role unless:

```text
qualification context current and valid
AND admission context current and ACTIVE
AND requested capability <= qualification ceiling
AND requested capability <= admission ceiling
AND requested risk <= both ceilings
AND required assurance supported by both
AND project/resource scope inside both
AND all current policy/state/approval predicates pass
```

Where admission is required by local policy, absence of admission is denial.

A capability issuer cannot treat admission as advisory metadata.

---

## 21. Mandatory Trust-Decision Composition Integration

Capability issuance alone is insufficient.

The existing Trust-Decision Composition Architecture MUST be extended by a versioned composition profile so admission is a signed controlling dependency.

The semantic context SHALL include an admission dependency, for example:

```text
DecisionSemanticContext {
    ...existing fields...
    admission_decision_context_digest
}
```

and the current state vector SHALL include authoritative admission state/policy observations where admission is controlling.

Trust composition MUST independently verify the intersection of:

```text
Qualification
INTERSECT Admission
INTERSECT CapabilityToken
INTERSECT Current Policy / Risk / Assurance / Governance
```

A token issued while admission was valid does not make later admission withdrawal irrelevant.

---

## 22. Execution-Invalidating Admission Dependencies

Admission status and controlling qualification status are execution-invalidating dependencies for unexecuted grants when local policy requires admission.

At minimum, these state changes invalidate dependent unexecuted authorization:

```text
ACTIVE -> SUSPENDED
ACTIVE -> REVIEW_REQUIRED
ACTIVE -> WITHDRAWN
ACTIVE -> REVOKED
ACTIVE -> EXPIRED
ACTIVE -> incompatible SUPERSEDED
qualification prerequisite becomes non-ACTIVE/non-usable
admission policy becomes incompatibly superseded or revoked
admission authority/required approval becomes invalid where policy declares continuing dependency
```

Each dependency SHALL declare:

```text
invalidates_unexecuted_grants_on_change = true
execution_recheck_required = true
```

where appropriate under the composition/risk profile.

The architecture does not claim that revocation can reverse an already committed irreversible external effect.

---

## 23. Executor Recheck Contract

Immediately before protected credential release or external effect, the Capability Executor MUST perform the admission-related rechecks required by the signed TrustDecision/composition profile.

The executor need not rerun qualification evaluation or admission review from raw evidence.

It MUST verify the required authoritative current-state observations, including where controlling:

- TrustDecision currentness;
- CapabilityToken currentness;
- qualification status/currentness;
- admission status/currentness;
- admission policy epoch/currentness;
- required approval currentness;
- revocation state;
- signed execution-recheck requirements.

If any required dependency is unavailable, stale, rolled back, invalid, or changed incompatibly:

```text
NO PROTECTED CREDENTIAL RELEASE
NO EXTERNAL EFFECT
```

Fail closed.

---

## 24. Validity Horizon

No admission-dependent authorization may outlive its controlling admission dependencies.

Extend the effective TrustDecision validity horizon to include:

```text
TrustDecision.valid_until <= min(
    existing ATE deadlines,
    qualification validity,
    admission validity,
    admission review deadline where mandatory,
    continuously-current admission prerequisite deadlines,
    admission approval validity where approval is continuing,
    stricter risk/composition freshness deadline
)
```

A longer-lived Admission Credential does not lengthen a shorter qualification, approval, policy, or TrustDecision deadline.

---

## 25. Point-in-Time Consistency and TOCTOU

Admission uses the existing ATE state-observation and stability model.

Before an Admission Credential is issued:

1. capture authoritative qualification, admission-policy, trust-root, approval, and revocation state;
2. evaluate all admission predicates;
3. immediately before durable issuance, re-read all dependencies marked decision-time stability required;
4. if controlling state changed, restart or deny according to bounded policy;
5. persist required audit/evidence before releasing the credential.

Before ATE grant issuance and before external effect, existing composition/executor stability and recheck contracts apply.

No single admission-time check may be treated as sovereign over later current-state changes.

---

## 26. Approvals and Independence

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

Required independence is a machine-verifiable policy condition.

Different keys do not imply independence if the same compromise domain controls both and policy requires independent control.

The participant MUST NOT possess or control admission, qualification, approval, or policy signing authority, including signing-oracle access that defeats the intended separation.

---

## 27. Canonical Encoding and Versioning

Admission artifacts inherit the normative ATE encoding, canonicalization, versioning, signature-domain-separation, and unsupported-version fail-closed rules.

This architecture does not define a competing serialization system.

For every admission artifact:

```text
artifact_type
artifact_version
canonical bytes
domain-separated signature context
```

MUST be unambiguous.

Unknown controlling versions, unknown constraints, ambiguous empty/missing semantics, or unsupported required extensions fail closed.

Credential/decision derivation rules MUST be testable as exact equality or narrowing predicates.

---

## 28. Audit and Evidence Requirements

Admission reuses the existing ATE audit/evidence plane.

Required admission-related records SHOULD be typed canonical extensions, not a new independent ledger.

At minimum, durable evidence must permit reconstruction of:

- exact subject principal and qualified profile;
- exact qualification prerequisite and status epoch;
- exact Admission Policy digest/epoch;
- exact Admission Decision and Admission Credential digests;
- exact admitted role/capability/resource/risk/assurance ceiling;
- Admission Authority and authority-scope digest;
- required approvals/participation conditions;
- status transitions and state epochs;
- continuation/renewal/supersession lineage;
- capability issuance that depended on admission;
- TrustDecision semantic context that depended on admission;
- executor admission-state recheck result;
- resulting execution/non-execution status.

For issuance, required audit/evidence persistence MUST precede credential release when policy declares durability mandatory.

If required persistence fails:

```text
ADMISSION CREDENTIAL NOT RELEASED
```

Denied/malformed requests must be representable without inventing a subject identity when parsing/identity establishment failed.

---

## 29. Non-Transferability and Delegation

Standing qualification/admission credentials are reusable public evidence, not bearer capabilities.

Copying them grants nothing without matching authenticated principal/profile/current context.

Version 0.1 permits no implicit:

- delegation;
- transfer;
- redelegation;
- child-agent inheritance;
- ownership transfer;
- session inheritance;
- reuse of another principal's action evidence.

A child or delegated principal requires its own valid qualification/admission/current runtime context unless a future separately reviewed delegation architecture explicitly defines otherwise.

Identity ownership/control transfer is a material change requiring assessment under qualification/admission policy.

---

## 30. Admission Fail-Closed Conditions

Admission-dependent authorization MUST fail closed for any controlling condition including:

- unknown or unauthorized Admission Authority;
- Admission Authority ceiling violation;
- bad signature;
- unsupported artifact version;
- inactive/unknown/rollbacked Admission Policy;
- invalid/non-ACTIVE qualification;
- wrong subject/profile;
- qualification/admission pair mismatch;
- capability/resource scope expansion;
- risk ceiling violation;
- assurance incompatibility;
- missing/expired/revoked required approval;
- non-ACTIVE admission status;
- admission-state rollback;
- expired admission;
- missed mandatory review deadline;
- incompatible qualification replacement;
- incompatible policy supersession;
- unavailable required current state;
- stale required state observation;
- unknown material compatibility;
- audit persistence failure where mandatory;
- invalid cross-artifact digest/binding;
- unsupported required extension;
- executor inability to perform a required final recheck.

```text
UNKNOWN != ADMITTED
ERROR   != ADMITTED
MISSING != ADMITTED
STALE   != ADMITTED
```

---

## 31. Frozen-Candidate Architectural Invariants

These invariants are candidates for adversarial review and are **not frozen by this draft**.

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
Admission binds the exact qualified principal/profile or an authorized non-expanding continuation path.

### A-I7 MONOTONIC_ADMISSION_STATE
Older ACTIVE state cannot override newer suspension, withdrawal, revocation, expiry, review-required, or supersession state.

### A-I8 QUALIFICATION_DEPENDENCY_CLOSURE
Loss of qualification usability removes dependent admission usability.

### A-I9 PENDING_EXECUTION_CLOSURE
Admission/qualification loss invalidates dependent unexecuted grants where admission is a controlling requirement.

### A-I10 CURRENT_STATE_PROVENANCE
Admission status/policy observations have authorized sources, exact digests, epochs, freshness, and rollback protection.

### A-I11 ASSURANCE_BINDING
Admission cannot imply an assurance profile not supported by qualification and current action requirements.

### A-I12 AUTHORITY_CEILINGS
Admission issuer signatures are valid only within root-delegated domain/project/role/capability/risk/assurance/lifetime ceilings.

### A-I13 NO_CIRCULAR_TRUST
Admission authorities cannot authorize their own trust registration/ceilings or manufacture independent policy/approval authority.

### A-I14 DECISION_CREDENTIAL_COHERENCE
Admission Credential is digest-bound to a retained Admission Decision and may only preserve or narrow its fields.

### A-I15 CONTINUATION_NO_EXPANSION
Qualification replacement cannot silently rewrite admission; continuation is explicit, signed, current, and non-expanding.

### A-I16 FINITE_ADMISSION
Admission has finite validity and deterministic review/renewal semantics.

### A-I17 COMPOSITION_BINDING
Admission is a mandatory signed trust-composition dependency where local policy requires it.

### A-I18 EXECUTOR_RECHECK
Execution-invalidating admission dependencies are rechecked before protected credential release/external effect.

### A-I19 AUDIT_CAUSALITY
Admission issuance, state, capability, trust decision, recheck, and execution remain causally reconstructable.

### A-I20 NO_IMPLICIT_TRANSFER
Credentials, child agents, new sessions, delegation, and ownership changes do not inherit admission authority implicitly.

### A-I21 LOCAL_ONLY_DEFAULT
No foreign qualification/admission portability is inferred without explicit existing federation semantics.

### A-I22 BASELINE_PRECEDENCE
Admission extends the authoritative qualification/composition/revocation/audit architecture and cannot redefine or weaken it.

---

## 32. Candidate Lean Admission Tests

These are design candidates only. No experiment is authorized.

A future admission conformance protocol should remain deterministic and local.

Minimum diagnostic/adversarial cases should include:

```text
A-T0  ACTIVE qualification + valid local policy -> admission may be granted
A-T1  qualification valid but no admission -> admission-required capability denied
A-T2  admission scope wider than qualification -> denied
A-T3  admission assurance/risk exceeds qualification -> denied
A-T4  wrong principal/profile presents copied admission -> denied
A-T5  newer SUSPENDED/WITHDRAWN admission defeats older ACTIVE credential
A-T6  qualification becomes non-ACTIVE -> dependent admission unusable
A-T7  already-issued but unexecuted grant + admission withdrawal -> execution denied
A-T8  stale/rollbacked admission policy/status observation -> denied
A-T9  unauthorized/out-of-ceiling admission signer -> denied
A-T10 expired/revoked/mismatched required approval -> denied
A-T11 qualification replacement without authorized continuation -> denied
A-T12 non-expanding authorized continuation -> accepted within preserved scope only
A-T13 admission credential fields wider than signed decision -> denied
A-T14 required current-state service unavailable -> denied
A-T15 mandatory audit persistence unavailable at admission issuance -> no credential release
A-T16 unrelated qualification/admission credentials cannot be unioned
A-T17 foreign admission/qualification not implicitly portable
A-T18 execution-time current-state recheck succeeds for unchanged dependencies
A-T19 child/delegated principal cannot inherit admission implicitly
```

These cases are not a substitute for existing qualification or ATE conformance suites.

---

## 33. Minimal Proof-of-Concept Boundary

A future first PoC should prove only the new admission boundary, not re-prove the entire ATE stack.

A useful minimal claim would be:

> Given an already-valid qualification fixture under the frozen qualification semantics, the local domain can issue a narrower admission; admission absence/withdrawal prevents admission-dependent capability/execution; and admission cannot widen qualification.

The PoC may use deterministic local fixtures for pre-existing qualification/runtime evidence so long as claims remain limited to admission semantics.

The PoC MUST NOT claim to establish:

- production federation;
- universal agent identity;
- human-level background checking;
- global trustworthiness;
- full qualification issuance correctness;
- production HSM/key custody;
- distributed revocation consistency;
- model safety in general.

---

## 34. Security Claim Boundary

If this architecture is later frozen and implemented correctly, the intended claim is narrow:

> A trust domain can require an already-qualified AI agent/runtime profile to obtain a separate, current, locally controlled, scope-narrowing admission before that agent may receive and execute admission-dependent ATE authorization; loss of admission or its qualification prerequisite closes pending authority according to signed current-state and executor recheck rules.

It does not prove that the agent is universally trustworthy.

It does not grant ambient authority.

It does not replace action-specific ATE verification.

---

## 35. Required Adversarial Review Before Freeze

Before any freeze or implementation, an adversarial review MUST attempt to break at least:

1. qualification-to-admission narrowing;
2. coherent-pair semantics;
3. admission signer ceilings;
4. policy-owner separation;
5. admission status rollback protection;
6. qualification dependency propagation;
7. pending grant invalidation;
8. executor recheck completeness;
9. assurance/risk containment;
10. approval independence/currentness;
11. qualification replacement/continuation;
12. credential/decision derivation coherence;
13. audit release ordering/causal reconstruction;
14. unavailable-state fail-closed behavior;
15. local-only/federation boundary;
16. implicit delegation/transfer;
17. consistency with the existing Trust-Decision Composition Architecture;
18. consistency with the existing Agent Qualification & Requalification Architecture.

Any substantive unresolved contradiction blocks freeze.

---

## 36. Recommended Next Step

Perform an adversarial architecture review of this exact draft against the existing ATE baseline.

Do not implement.

Do not design the conformance protocol until the architecture review disposition permits it.

If review identifies only bounded correctable defects, produce a revised architecture candidate rather than silently editing this reviewed v0.1 artifact.

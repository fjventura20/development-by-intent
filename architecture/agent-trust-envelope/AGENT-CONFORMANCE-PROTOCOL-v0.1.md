# Agent Conformance Protocol v0.1

**Status:** DESIGN DRAFT — NOT FROZEN  
**Architecture family:** INSA / Value Architecture / Condition of Agency / Agent Trust Envelope  
**Scope:** Post-admission lifecycle conformance, re-attestation, restriction, suspension, revocation, and restoration  
**Implementation authorization:** NONE until adversarial review and freeze

---

## 1. Purpose

This protocol defines how a governed trust domain determines whether an already-qualified and admitted AI agent or agent runtime remains eligible to participate over time.

It closes the lifecycle gap between initial qualification/admission and action-time ATE authorization.

The core question is:

> How does the system continuously determine that an admitted agent remains qualified, governed, authorized, and conformant throughout participation?

The protocol does not create a permanent trust badge. It defines a renewable, evidence-backed conformance state.

---

## 2. Architectural Position

```text
INSA                         -> application architecture
Value Architecture           -> normative architecture
Condition of Agency          -> commitment architecture
Qualification                -> role-eligibility architecture
Admission                    -> trust-domain participation architecture
Agent Conformance            -> continuing-eligibility lifecycle architecture
Agent Trust Envelope         -> action-specific trust architecture
Enforcement Plane            -> authority / execution architecture
Evidence + Audit             -> accountability architecture
```

The full lifecycle is:

```text
Qualification
    ↓
Admission
    ↓
Initial Attestation
    ↓
Action Authorization
    ↓
Governed Operation
    ↓
Conformance Evaluation
    ↓
┌───────────────────────────────┐
│ CONFORMANT                    │
│ REATTESTATION_REQUIRED        │
│ RESTRICTED                    │
│ SUSPENDED                     │
│ REVOKED                       │
└───────────────────────────────┘
    ↓
Re-attestation / remediation
    ↓
Continued authority, reduced authority, or no authority
```

---

## 3. Core Principle

Trust is a continuously maintainable state established by current evidence, not a permanent characteristic assigned to an agent.

Therefore:

```text
qualified_once != trusted_forever
admitted_once != admitted_forever
attested_once != conformant_forever
historically_valid != currently_usable
```

A participant may continue to act only when all current prerequisites required by policy remain true.

---

## 4. Relationship to Existing ATE Specifications

This protocol coordinates, but does not replace, existing authorities.

### Qualification & Admission Protocol

Defines role eligibility and trust-domain admission.

This protocol consumes qualification and admission state and determines whether those states remain sufficient for continued participation.

### Revocation & Trust-State Model

Defines current-state semantics including ACTIVE, SUSPENDED, REVOKED, EXPIRED, SUPERSEDED, and UNKNOWN.

This protocol uses those states when evaluating continuing conformance.

### Enforcement Plane

Controls possession of executable capability.

A conformance failure is meaningful only if downstream authorization and execution are actually prevented when required.

### Audit & Accountability Model

Records consequential conformance transitions, re-attestation events, restrictions, suspensions, revocations, restorations, and the evidence supporting them.

Conformance records never substitute for authorization.

---

## 5. Normative Invariants

The following invariants are mandatory.

### INV-C1 — No permanent conformance

No qualification, admission, attestation, or prior successful action creates indefinite conformance.

### INV-C2 — Current evidence controls

A conformance decision MUST be based on current policy and current trust state.

### INV-C3 — Event-driven invalidation

A material change to identity, runtime, governance, authorization basis, or qualification basis MUST trigger re-evaluation.

### INV-C4 — Unknown fails closed

If required current conformance state cannot be established:

```text
UNKNOWN != CONFORMANT
```

### INV-C5 — Conformance is role- and domain-specific

Conformance for one role or trust domain does not imply conformance for another.

### INV-C6 — Standing conformance is not action authority

```text
CONFORMANT != AUTHORIZED_TO_ACT
```

Every governed action still requires the applicable ATE authorization path.

### INV-C7 — Loss of conformance affects capability

If policy requires conformance for an action class, loss of conformance MUST prevent issuance or use of the corresponding execution capability.

### INV-C8 — Re-attestation cannot be self-certified

The participant agent cannot unilaterally declare itself conformant.

### INV-C9 — Evidence must be attributable

Every conformance decision MUST identify the subject, evaluator or authority, policy basis, evidence set, time, and result.

### INV-C10 — Restoration requires new evidence

A prior CONFORMANT state cannot be restored merely by clearing an error flag. Restoration requires a new valid evaluation or re-attestation.

---

## 6. Conformance Subject

The protocol evaluates a specific governed subject.

```text
ConformanceSubject {
    trust_domain
    subject_identity
    role_id
    admission_credential_id
    qualification_credential_id
    runtime_identity?
    model_identity?
    session_identity?
}
```

The trust domain MUST define which identity dimensions are material for each role.

Examples:

- model family
- exact model/version
- agent runtime build
- host/runtime provenance
- governing policy version
- COA version
- Value Architecture version
- tool/capability set
- credential issuer
- operating environment

---

## 7. Conformance Requirements Profile

Each governed role MUST reference a signed `ConformanceRequirementsProfile`.

```text
ConformanceRequirementsProfile {
    profile_id
    profile_version
    trust_domain
    role_id

    required_qualification_profile
    required_admission_policy

    required_governance_artifacts[]
    required_runtime_attributes[]
    required_identity_bindings[]
    required_capability_constraints[]

    periodic_recheck_interval?
    max_attestation_age?
    event_triggers[]

    evaluator_authorities[]
    allowed_outcomes[]

    failure_policy
    restoration_policy

    issued_at
    effective_at
    expires_at?
    supersedes?
    policy_digest
    issuer
    signature
}
```

The profile is policy. The participant agent does not author or modify its own governing profile unless a superior governance policy explicitly permits that concentration of authority.

---

## 8. Required Conformance Dimensions

A trust domain MAY define additional dimensions, but v0.1 defines eight minimum categories.

### C1 — Qualification continuity

The required QualificationCredential remains:

```text
cryptographically valid
AND issuer-authorized
AND temporally valid
AND policy-current
AND not suspended
AND not revoked
AND not hard-superseded
AND subject-binding-valid
```

### C2 — Admission continuity

The required AdmissionCredential remains valid and applicable to the current trust domain and role.

### C3 — Identity continuity

The currently operating subject matches the identity that was qualified and admitted, according to the role's binding requirements.

### C4 — Runtime continuity

Material runtime properties remain within the admitted and attested envelope.

### C5 — Governance continuity

Required COA, Value Architecture, and other governance commitments remain current and applicable.

### C6 — Capability continuity

The participant's current tools, permissions, interfaces, or reachable resources have not materially exceeded the admitted capability profile.

### C7 — Evidence continuity

Required evidence remains current, verifiable, attributable, and sufficient under the active conformance profile.

### C8 — Trust-state continuity

No controlling identity, key, policy, session, credential, or evidence artifact is suspended, revoked, expired, superseded, or unknown where ACTIVE status is required.

---

## 9. Conformance Outcomes

The canonical conformance states are:

```text
CONFORMANT
REATTESTATION_REQUIRED
RESTRICTED
SUSPENDED
REVOKED
```

These are lifecycle decisions, not execution decisions.

### CONFORMANT

All required conformance conditions currently hold.

Effect:

- standing participation may continue
- action-specific ATE authorization remains possible
- no action is authorized merely by this state

### REATTESTATION_REQUIRED

A condition changed or aged such that fresh evidence is required before normal participation continues.

Default effect:

- no new governed capability issuance for affected scopes
- unaffected scopes MAY remain available if policy explicitly permits partitioned conformance

### RESTRICTED

The subject remains admitted but only a reduced capability or action scope is permitted.

Restriction MUST be explicit and machine-enforceable.

### SUSPENDED

Participation is temporarily disabled pending investigation, evidence refresh, remediation, or authority decision.

Default effect:

- no new governed execution capability
- existing unconsumed capabilities MUST be invalidated where technically and semantically possible
- inability to prove invalidation MUST be treated as a security exception and audited

### REVOKED

Continuing participation under the affected admission/role is terminated.

Effect:

- admission state becomes unusable for new authorization
- restoration requires a new admission path unless superior policy explicitly defines a reinstatement procedure

---

## 10. Trigger Model

Conformance re-evaluation MUST occur on any trigger marked mandatory by the active profile.

Minimum trigger classes:

### T1 — Time-based trigger

Examples:

- attestation age exceeds policy limit
- scheduled periodic review
- credential nearing expiration

### T2 — Identity change

Examples:

- subject key rotation
- agent identity change
- runtime identity change
- session binding discontinuity

### T3 — Model change

Examples:

- model version change
- model provider change
- materially different foundation model
- unverified model identity

### T4 — Runtime change

Examples:

- agent software upgrade
- host migration
- toolchain change
- isolation-boundary change
- execution environment change

### T5 — Governance change

Examples:

- COA version superseded
- Value Architecture policy superseded
- new mandatory governance commitment
- policy revocation

### T6 — Capability change

Examples:

- new tool
- broader filesystem access
- new network reachability
- elevated credentials
- new resource adapter

### T7 — Qualification basis change

Examples:

- required qualification evidence expires
- qualification profile changes
- certification or approval is revoked
- required evaluator no longer trusted

### T8 — Admission basis change

Examples:

- domain policy changes
- admission credential suspended
- role definition changes
- tenant or project boundary changes

### T9 — Trust anomaly

Examples:

- failed integrity check
- audit discontinuity
- replay attempt
- unexplained runtime provenance gap
- evidence mismatch
- authority compromise

### T10 — Explicit authority demand

An authorized governance or trust authority may require re-attestation for a defined subject/scope.

---

## 11. Trigger Precedence

Some triggers MUST immediately remove normal authority before evaluation completes.

```text
critical trigger
    -> immediate SUSPENDED or REATTESTATION_REQUIRED
    -> evaluate
    -> restore, restrict, revoke, or remain suspended
```

The active ConformanceRequirementsProfile MUST specify trigger severity.

Recommended classes:

```text
INFORMATIONAL
RECHECK
MANDATORY_REATTESTATION
IMMEDIATE_SUSPENSION
IMMEDIATE_REVOCATION
```

A critical trust-root, identity, or credential revocation MUST NOT wait for a periodic recheck.

---

## 12. Conformance Evaluation

A conformance evaluation consumes:

```text
ConformanceEvaluationRequest {
    evaluation_id
    trust_domain
    subject_identity
    role_id
    profile_id
    profile_version
    trigger
    requested_at
}
```

The evaluator resolves the current authoritative artifacts rather than relying solely on participant-supplied copies.

Minimum evaluation procedure:

1. Resolve active ConformanceRequirementsProfile.
2. Verify profile signature and issuer authority.
3. Resolve current subject identity and bindings.
4. Resolve current qualification state.
5. Resolve current admission state.
6. Resolve current governance artifacts.
7. Resolve current runtime/model attributes required by policy.
8. Resolve current trust/revocation state.
9. Verify required evidence.
10. Compare current state against required profile.
11. Produce a signed ConformanceDecision.
12. Publish resulting lifecycle state.
13. Emit durable audit evidence.
14. Notify enforcement/authorization components of any authority-affecting transition.

---

## 13. Conformance Decision

```text
ConformanceDecision {
    decision_id
    evaluation_id

    trust_domain
    subject_identity
    role_id

    profile_id
    profile_version
    profile_digest

    trigger
    evaluated_at

    qualification_state
    admission_state
    identity_state
    runtime_state
    governance_state
    capability_state
    evidence_state
    trust_state

    verdict
    affected_scope[]
    restrictions[]

    reason_codes[]
    evidence_refs[]
    controlling_artifact_hashes[]

    valid_until?
    reattestation_deadline?

    issuer
    signature
}
```

The decision MUST be immutable.

Lifecycle state changes are represented by new decisions, not edits to prior decisions.

---

## 14. Decision Authority

Define logical role:

```text
R13 — Conformance Authority
```

R13 MAY:

- evaluate conformance when authorized
- sign ConformanceDecision artifacts
- require re-attestation within authorized policy scope
- impose machine-enforceable restriction or suspension when policy authorizes it
- publish restoration after successful re-attestation

R13 MUST NOT automatically inherit:

- Qualification Authority
- Admission Authority
- Trust Root Authority
- general policy-authoring authority
- protected-resource credentials
- Capability Executor authority

At higher assurance levels, conformance policy authoring and conformance adjudication SHOULD be separated.

---

## 15. Re-attestation Protocol

Re-attestation is a fresh evidence transaction, not a reaffirmation of an old statement.

```text
Trigger
   ↓
Normal authority constrained as policy requires
   ↓
Fresh evidence request
   ↓
Evidence collection from authoritative sources
   ↓
Evidence verification
   ↓
Conformance evaluation
   ↓
New ConformanceDecision
   ↓
Restore / restrict / suspend / revoke
```

A re-attestation MUST identify:

- exact subject
- exact role
- exact trust domain
- exact active profile/version
- triggering condition
- required new evidence
- evaluator
- decision time
- result
- affected authority scope

---

## 16. Re-attestation Freshness

Freshness requirements are policy-defined.

Examples:

- runtime provenance collected after the triggering upgrade
- COA acceptance bound to the current governance version
- model identity verified for the current runtime
- qualification status resolved after a revocation epoch
- capability inventory measured after privilege changes

Evidence generated before the event that triggered re-attestation MUST NOT be treated as fresh proof of the post-event state unless the profile explicitly permits it.

---

## 17. Restriction Semantics

RESTRICTED MUST be enforceable, not descriptive.

Example:

```text
Before:
    filesystem:read/write /srv/project/*
    github:read/write repo X
    email:send

After restriction:
    filesystem:read /srv/project/*
    github:read repo X
    email:none
```

A restriction decision MUST identify exact affected scopes and must propagate to the authorization path before the restricted capability may be exercised again.

---

## 18. Suspension Semantics

Suspension is a fail-closed temporary state.

When SUSPENDED:

- new action authorization for affected scopes MUST fail
- new CapabilityTokens MUST NOT be issued for affected scopes
- unconsumed tokens or execution capabilities MUST be invalidated where supported
- downstream verifiers MUST observe current suspension state
- the suspension event MUST be audited
- restoration MUST require a new positive ConformanceDecision

---

## 19. Revocation Semantics

REVOKED is terminal for the affected admission/role instance unless governing policy defines an explicit reinstatement mechanism.

Revocation SHOULD identify:

- revocation authority
- subject
- role/domain
- effective time
- reason code
- affected credential/artifact identifiers
- dependency invalidation requirements

A revoked subject MAY later requalify and be readmitted as a new lifecycle instance. Historical records remain immutable.

---

## 20. Integration with Action Authorization

Before issuing a governed action capability, the authorization path MUST resolve current required conformance state.

Conceptually:

```text
authorize(action) =
    qualification_usable_now
    AND admission_usable_now
    AND conformance_state_sufficient_for(action)
    AND session_governance_valid
    AND action_specific_ATE_requirements_satisfied
```

Conformance sufficiency is policy-specific.

Typical rule:

```text
CONFORMANT -> may proceed to action evaluation
RESTRICTED -> may proceed only if action is inside restriction
REATTESTATION_REQUIRED -> deny affected action
SUSPENDED -> deny
REVOKED -> deny
UNKNOWN -> deny
```

---

## 21. Race and TOCTOU Requirements

A positive conformance decision can become stale between evaluation and execution.

Therefore:

1. Conformance state MUST be checked at capability issuance.
2. Critical revocation/suspension state MUST be checked again inside or immediately before the execution boundary where feasible.
3. Capability lifetime SHOULD be short enough to bound stale-state exposure.
4. A state epoch or equivalent monotonic version SHOULD bind authorization to the observed lifecycle state.
5. Execution MUST fail closed if required current state cannot be resolved.

---

## 22. Conformance Epoch

A trust domain SHOULD maintain a monotonic conformance or trust-state epoch.

Example:

```text
subject_conformance_epoch = 42
```

A lifecycle-affecting transition increments the relevant epoch.

Capability or TrustDecision artifacts MAY bind:

```text
observed_conformance_epoch = 42
```

At execution time:

```text
current_epoch != observed_epoch
    -> reverify current state
```

An epoch mismatch is not itself proof of compromise, but it prevents blind reliance on stale state.

---

## 23. Audit Events

The audit vocabulary SHOULD add at least:

```text
CONFORMANCE_EVALUATION_STARTED
CONFORMANCE_EVALUATION_COMPLETED
CONFORMANCE_ESTABLISHED
REATTESTATION_REQUIRED
REATTESTATION_STARTED
REATTESTATION_COMPLETED
CONFORMANCE_RESTRICTED
CONFORMANCE_SUSPENDED
CONFORMANCE_REVOKED
CONFORMANCE_RESTORED
CONFORMANCE_TRIGGER_OBSERVED
CONFORMANCE_EPOCH_ADVANCED
```

Each transition record SHOULD contain:

- subject identity
- role/domain
- prior state
- new state
- trigger
- policy/profile identifiers and digests
- decision identifier
- evidence references
- authority identity
- effective time
- affected scope

---

## 24. Failure Semantics

### Evidence unavailable

If required evidence cannot be obtained:

```text
required evidence unavailable -> not CONFORMANT
```

The policy determines REATTESTATION_REQUIRED versus SUSPENDED, but normal authority MUST NOT silently continue.

### Evaluator unavailable

Evaluator failure MUST NOT be interpreted as successful conformance.

### Audit failure

For high-assurance governed transitions, inability to durably record a conformance state change SHOULD fail closed according to deployment policy.

### Conflicting evidence

Conflicting authoritative evidence produces non-conformance until resolved.

### Clock uncertainty

If temporal validity cannot be reliably determined and the artifact's validity depends on time, the relevant state is not usable.

---

## 25. Restoration

Restoration from REATTESTATION_REQUIRED, RESTRICTED, or SUSPENDED requires:

1. the triggering condition is resolved or accepted under current policy
2. all required fresh evidence is verified
3. current qualification/admission remain usable
4. current governance commitments are valid
5. current trust state is acceptable
6. a new signed ConformanceDecision is issued
7. lifecycle state is published
8. enforcement observes the new state
9. restoration is durably audited

Restoration MUST NOT erase the prior adverse transition.

---

## 26. Minimal State Machine

```text
                 ┌───────────────┐
                 │  CONFORMANT   │
                 └───────┬───────┘
                         │ trigger
         ┌───────────────┼────────────────┐
         ▼               ▼                ▼
REATTESTATION_REQUIRED RESTRICTED      SUSPENDED
         │               │                │
         │ fresh evidence│ remediation    │ investigation
         └───────┬───────┴────────┬───────┘
                 │                │
                 ▼                ▼
            CONFORMANT         REVOKED
```

Transitions MUST be policy-authorized.

Direct `REVOKED -> CONFORMANT` is prohibited for the same revoked admission instance unless an explicit reinstatement protocol is defined by superior policy.

---

## 27. Security Properties Expected from an Implementation

A conformant implementation should be able to demonstrate:

### P1 — Upgrade invalidation

A material runtime or model change triggers re-attestation.

### P2 — Governance supersession

A mandatory COA or VA policy update invalidates stale attestation.

### P3 — Qualification loss propagation

Suspended/revoked qualification prevents affected authorization.

### P4 — Admission loss propagation

Suspended/revoked admission prevents affected authorization.

### P5 — Capability reduction

A RESTRICTED state is reflected in executable authority.

### P6 — Current-state enforcement

A stale positive conformance decision cannot override a newer suspension/revocation.

### P7 — Restoration discipline

Authority is restored only after fresh valid evidence and a new positive decision.

### P8 — Accountability

Every lifecycle transition is reconstructable from durable evidence.

---

## 28. Minimal Local PoC Successor

After this protocol is reviewed and frozen, the first implementation should remain intentionally small.

Required scenario:

```text
1. Qualify subject.
2. Admit subject.
3. Establish CONFORMANT.
4. Authorize and execute one allowed action.
5. Mutate one material condition.
6. Detect trigger.
7. Move to REATTESTATION_REQUIRED or SUSPENDED.
8. Prove the same action is no longer executable.
9. Produce fresh re-attestation evidence.
10. Establish a new CONFORMANT decision.
11. Prove the action becomes executable again.
12. Verify complete audit history.
```

The mutation SHOULD initially be deterministic and local, such as a governed runtime-version or governance-version change.

No external model calls are required for the first PoC.

---

## 29. Explicit Non-Goals for v0.1

This protocol does not define:

- global reputation scoring
- subjective trust scoring
- autonomous punishment
- behavioral prediction
- Internet-scale federation
- production PKI technology
- blockchain trust
- continuous semantic surveillance of model thoughts
- a replacement for action-specific ATE authorization
- a replacement for qualification or admission

The protocol governs continuing eligibility, not intrinsic worth or generalized trustworthiness.

---

## 30. Design Principle

The governing principle of this protocol is:

> Trust is not something an agent receives once. It is a current, evidence-backed condition that must remain demonstrably true for authority to continue.

Or operationally:

```text
No current evidence
    -> no current conformance

No current conformance
    -> no affected governed capability
```

That is the lifecycle bridge between qualification, governance, trust, enforcement, and accountability.

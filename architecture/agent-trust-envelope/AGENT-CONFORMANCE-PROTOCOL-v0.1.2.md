# Agent Conformance Protocol v0.1.2

**Status:** FINAL FREEZE CANDIDATE — DESIGN ONLY — NOT YET FROZEN  
**Architecture family:** INSA / Value Architecture / Condition of Agency / Agent Trust Envelope  
**Supersedes for current design work:** `AGENT-CONFORMANCE-PROTOCOL-v0.1.1.md`  
**Reviews incorporated:** `AGENT-CONFORMANCE-PROTOCOL-v0.1-ADVERSARIAL-REVIEW.md`; `AGENT-CONFORMANCE-PROTOCOL-v0.1.1-RECONCILIATION-REVIEW.md`  
**Implementation authorization:** NONE until explicit freeze

---

## 1. Purpose

This protocol defines how a governed trust domain determines whether an already-qualified and admitted AI agent or agent runtime remains eligible to participate over time.

It closes the lifecycle gap between initial qualification/admission and action-time ATE authorization.

The core requirement is:

> Trust is a continuously maintainable state established by current evidence, not a permanent characteristic assigned to an agent.

This protocol therefore defines renewable conformance state, trigger observation, re-attestation, restriction, suspension, revocation, restoration, and enforcement coupling.

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

Lifecycle:

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
CONFORMANT / REATTESTATION_REQUIRED / RESTRICTED / SUSPENDED / CONFORMANCE_REVOKED
    ↓
Re-attestation / remediation / termination
```

---

## 3. Core Distinctions

```text
qualified_once != trusted_forever
admitted_once != admitted_forever
attested_once != conformant_forever
historically_valid != currently_usable
CONFORMANT != AUTHORIZED_TO_ACT
```

Standing conformance only preserves eligibility to enter the action-specific ATE authorization path.

---

## 4. Relationship to Existing ATE Specifications

This protocol coordinates but does not replace:

- **Agent Qualification & Admission Protocol v0.2.2** — role eligibility and domain admission.
- **ATE Revocation & Trust-State Model v0.1** — current-state semantics for ACTIVE, SUSPENDED, REVOKED, EXPIRED, SUPERSEDED, and UNKNOWN.
- **ATE Enforcement Plane v0.1** — executable capability possession and final enforcement.
- **ATE Audit & Accountability Model v0.1** — durable, attributable, reconstructable evidence.

No conformance artifact substitutes for qualification, admission, action authorization, revocation state, or execution enforcement. Externally authoritative revocation state always takes precedence over conformance lifecycle state.

---

## 5. Normative Invariants

### INV-C1 — No permanent conformance
No qualification, admission, attestation, or prior successful action creates indefinite conformance.

### INV-C2 — Current evidence controls
A conformance decision MUST use current policy and current trust state.

### INV-C3 — Event-driven invalidation
Material changes to identity, model, runtime, governance, capability, qualification basis, admission basis, or trust state MUST trigger re-evaluation when required by policy.

### INV-C4 — Unknown fails closed
```text
UNKNOWN != CONFORMANT
```

### INV-C5 — Role/domain specificity
Conformance is specific to a defined role and trust domain.

### INV-C6 — Conformance is not action authority
Every governed action still requires the applicable ATE authorization path.

### INV-C7 — Loss of conformance affects capability
If policy requires conformance for an action scope, loss of sufficient conformance MUST prevent issuance or use of affected executable capability.

### INV-C8 — No self-certification
The participant cannot unilaterally establish its own conformance.

### INV-C9 — Attributable evidence
Every conformance transition MUST identify subject, policy/profile, evidence, authority, time, trigger, scope, and result.

### INV-C10 — Restoration requires new evidence
A prior CONFORMANT state cannot be restored merely by clearing an error flag.

### INV-C11 — Bounded staleness
No authority-bearing conformance state may remain usable indefinitely merely because no trigger was observed.

### INV-C12 — Monotonic lifecycle state
Authority-affecting lifecycle state MUST expose a monotonic version, epoch, or equivalent ordering mechanism sufficient to detect stale authorization.

---

## 6. Conformance Subject

```text
ConformanceSubject {
    trust_domain
    subject_identity
    role_id
    qualification_credential_id
    admission_credential_id
    runtime_identity?
    model_identity?
    session_identity?
}
```

The active profile defines which identity dimensions are material.

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

    authoritative_trigger_sources[]
    trigger_rules[]

    periodic_recheck_interval?
    max_conformance_age
    max_trigger_source_silence?

    conformance_partitions[]?
    partition_dependencies[]?

    evaluator_authorities[]
    lifecycle_state_authorities[]

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

`max_conformance_age` is mandatory for any role capable of governed execution unless superior policy supplies an equivalent bounded-freshness mechanism.

---

## 7A. Canonical Encoding, Digest, and Signing Domains

All security-relevant conformance artifacts MUST use deterministic canonical encoding and versioned hash semantics consistent with the Qualification & Admission Protocol.

Conceptually:

```text
artifact_digest = HASH(
    artifact_domain_separator
    || canonical_encode(artifact_digest_payload)
)
```

Where the digest payload excludes the artifact signature and the digest field being computed.

Each conformance artifact family MUST define or inherit:

```text
schema_version
canonical_encoding_version
hash_algorithm
artifact_domain_separator
```

Minimum signing domains:

```text
ATE_CONFORMANCE_PROFILE_V1
ATE_CONFORMANCE_TRIGGER_V1
ATE_CONFORMANCE_EVALUATION_V1
ATE_CONFORMANCE_STATE_DECISION_V1
```

A signature valid for one conformance artifact class MUST NOT verify as another artifact class.

---

## 8. Minimum Conformance Dimensions

### C1 — Qualification continuity
Required QualificationCredential remains currently usable.

### C2 — Admission continuity
Required AdmissionCredential remains currently usable for the trust domain and role.

### C3 — Identity continuity
The operating subject matches the qualified/admitted subject under required bindings.

### C4 — Runtime continuity
Material runtime properties remain within the permitted envelope.

### C5 — Governance continuity
Required COA, Value Architecture, and other governance commitments remain current.

### C6 — Capability continuity
Current tools, permissions, interfaces, and reachable resources remain within the permitted profile.

### C7 — Evidence continuity
Required evidence remains current, verifiable, attributable, and sufficient.

### C8 — Trust-state continuity
No controlling identity, key, policy, credential, or evidence artifact is unusable where ACTIVE/current state is required.

---

## 9. Canonical Conformance States

```text
CONFORMANT
REATTESTATION_REQUIRED
RESTRICTED
SUSPENDED
CONFORMANCE_REVOKED
```

These are lifecycle states, not execution verdicts.

### CONFORMANT
Standing participation may continue and action-specific authorization may be attempted.

### REATTESTATION_REQUIRED
Fresh evidence is required before normal authority continues for affected scope.

Default: no new governed capability issuance for affected scope.

### RESTRICTED
Only explicitly enumerated reduced scopes remain eligible.

### SUSPENDED
Affected participation is temporarily disabled.

### CONFORMANCE_REVOKED
The conformance lifecycle for the affected admission/role instance is terminated. This does not itself revoke the underlying QualificationCredential, AdmissionCredential, identity, key, policy, or other artifact.

---

## 10. Scope and Partition Rule

Default rule:

> A conformance failure affects the entire role instance unless the active profile explicitly defines independent conformance partitions.

Partitioned continuation is permitted only when the profile defines:

- partition identifiers,
- exact capability/action scope for each partition,
- dependencies among partitions,
- which triggers affect which partitions,
- whether failure propagates across dependencies.

Absence or ambiguity means whole-role impact.

---

## 11. Trigger Classes

Minimum classes:

- **T1 Time** — age, expiry, periodic review.
- **T2 Identity** — subject/key/session binding change.
- **T3 Model** — model/version/provider/material foundation change.
- **T4 Runtime** — agent build, host, toolchain, isolation boundary, execution environment change.
- **T5 Governance** — COA/VA/policy supersession or revocation.
- **T6 Capability** — new tool, privilege, network reachability, adapter, or credential scope.
- **T7 Qualification basis** — evidence/profile/certification/evaluator state change.
- **T8 Admission basis** — domain policy, role, tenant/project boundary, admission state change.
- **T9 Trust anomaly** — integrity failure, replay, audit discontinuity, provenance gap, evidence mismatch, authority compromise.
- **T10 Authority demand** — authorized explicit re-attestation request.

---

## 12. Authoritative Trigger Observation

A trigger is security-relevant evidence and MUST NOT rely solely on participant self-report.

Canonical artifact:

```text
ConformanceTriggerObservation {
    observation_id
    trust_domain
    subject_identity
    role_id

    trigger_class
    trigger_type
    severity

    observed_at
    source_id
    source_type
    source_state_version?

    prior_value_digest?
    current_value_digest?
    evidence_refs[]

    issuer
    signature
}
```

The profile defines acceptable authoritative trigger sources for each trigger class.

Examples:

- trust-root/revocation service
- runtime provenance monitor
- deployment controller
- policy registry
- identity authority
- capability inventory service
- audit-integrity monitor

Participant-provided trigger evidence MAY supplement but MUST NOT replace a required independent source.

If a mandatory trigger source becomes unavailable beyond `max_trigger_source_silence`, affected state MUST become non-CONFORMANT according to failure policy.

---

## 13. Trigger Severity

Recommended severities:

```text
INFORMATIONAL
RECHECK
MANDATORY_REATTESTATION
IMMEDIATE_SUSPENSION
IMMEDIATE_CONFORMANCE_REVOCATION
```

Critical externally authoritative revocation, trust-root compromise, or identity invalidation MUST NOT wait for periodic review. Such external revocation state is consumed as controlling trust-state evidence; it is not created by the conformance protocol.

---

## 14. Trigger Deduplication

Trigger observations MAY be deduplicated or coalesced only if:

1. the subject, role, trigger class, and controlling state version are equivalent;
2. no newer observation would increase severity;
3. no distinct affected partition/scope is suppressed;
4. coalescing itself is auditable.

A lower-severity repeated event MUST NOT mask a later higher-severity event.

---

## 15. Bounded Freshness

Event-driven invalidation alone is insufficient.

For authority-bearing scopes:

```text
usable_conformance =
    positive_current_state
    AND decision_age <= max_conformance_age
    AND required_trigger_sources_fresh
```

If the bound expires, the state becomes REATTESTATION_REQUIRED or SUSPENDED according to policy.

“No trigger observed” is not proof of indefinite conformance.

---

## 16. Authority Model

Two logical roles are defined.

### R13 — Conformance Evaluation Authority

R13 MAY:

- evaluate conformance,
- verify evidence,
- sign `ConformanceEvaluationResult`,
- recommend outcome and affected scope.

R13 does not automatically gain power to publish authority-changing lifecycle state.

### R14 — Lifecycle State Authority

R14 MAY, when explicitly authorized:

- publish CONFORMANT,
- require re-attestation,
- publish restriction,
- suspend,
- publish CONFORMANCE_REVOKED lifecycle state,
- restore,
- advance lifecycle epoch/state version.

R14 does not automatically inherit qualification, admission, trust-root, policy-authoring, Revocation Authority, or Capability Executor authority.

R14 MAY NOT issue a `RevocationRecord` for another artifact class unless separately authorized by the Trust Root Registry for that revocation scope.

At higher assurance levels, R13 and R14 SHOULD be separate. Concentration requires explicit superior governance policy.

---

## 17. Conformance Evaluation

Input:

```text
ConformanceEvaluationRequest {
    evaluation_id
    trust_domain
    subject_identity
    role_id
    profile_id
    profile_version
    trigger_observation_ids[]
    requested_at
}
```

Procedure:

1. Resolve active ConformanceRequirementsProfile.
2. Verify profile signature and issuer authority.
3. Resolve current subject identity and bindings.
4. Resolve qualification state.
5. Resolve admission state.
6. Resolve required governance artifacts.
7. Resolve required model/runtime attributes.
8. Resolve capability inventory.
9. Resolve revocation/current trust state.
10. Resolve mandatory requalification triggers from the active QualificationRequirementsProfile.
11. Resolve mandatory readmission triggers from the active AdmissionPolicy.
12. If a mandatory requalification trigger is satisfied, route the lifecycle to Qualification; conformance re-attestation alone cannot restore authority.
13. If a mandatory readmission trigger is satisfied, route the lifecycle to Admission; conformance re-attestation alone cannot restore authority.
14. Verify trigger-source freshness.
15. Verify bounded conformance freshness.
16. Evaluate scope/partition dependencies.
17. Produce signed evaluation result.
18. Submit result to authorized lifecycle-state authority.
19. Audit evaluation.

---

## 18. Conformance Evaluation Result

```text
ConformanceEvaluationResult {
    evaluation_id

    trust_domain
    subject_identity
    role_id

    profile_id
    profile_version
    profile_digest

    trigger_observation_ids[]
    evaluated_at

    qualification_state
    admission_state
    identity_state
    model_state
    runtime_state
    governance_state
    capability_state
    evidence_state
    trust_state
    trigger_source_state

    recommended_verdict
    affected_scope[]
    recommended_restrictions[]

    reason_codes[]
    evidence_refs[]
    controlling_artifact_hashes[]

    evaluator
    signature
}
```

The result is immutable and is not itself executable authority.

---

## 19. Lifecycle State Decision

R14 publishes:

```text
ConformanceStateDecision {
    decision_id
    evaluation_id

    trust_domain
    subject_identity
    role_id

    prior_state
    new_state

    affected_scope[]
    restrictions[]

    state_epoch
    effective_at
    valid_until?

    reason_codes[]
    controlling_artifact_hashes[]

    lifecycle_authority
    signature
}
```

The state decision is immutable.

---

## 20. Re-attestation Protocol

```text
Trigger observed
    ↓
Immediate fail-closed transition if severity requires
    ↓
Fresh evidence requirements resolved
    ↓
Fresh evidence collected from authoritative sources
    ↓
R13 evaluation
    ↓
R14 lifecycle-state decision
    ↓
Enforcement observes new state/epoch
    ↓
Restore / restrict / remain suspended / establish CONFORMANCE_REVOKED
```

Evidence generated before the triggering event MUST NOT be treated as fresh proof of post-event state unless policy explicitly permits it.

---

## 21. Restriction

RESTRICTED MUST be machine-enforceable.

Example:

```text
Before:
    filesystem:read/write /srv/project/*
    github:read/write repo X
    email:send

After:
    filesystem:read /srv/project/*
    github:read repo X
    email:none
```

Restrictions must name exact scope and be observed by the action authorization and execution path.

---

## 22. Suspension

When SUSPENDED:

- new action authorization for affected scope MUST fail;
- new capability issuance MUST fail;
- unconsumed capabilities SHOULD be invalidated where supported;
- final executor-side current-state verification MUST deny stale capability;
- restoration requires a new positive evaluation and R14 state decision;
- transition MUST be audited.

---

## 23. Conformance Revocation vs Artifact Revocation

`CONFORMANCE_REVOKED` is terminal for the affected conformance lifecycle instance unless superior policy defines explicit reinstatement.

It is distinct from artifact revocation under the ATE Revocation & Trust-State Model.

```text
CONFORMANCE_REVOKED
    != RevocationRecord(target = AdmissionCredential)
    != RevocationRecord(target = QualificationCredential)
    != RevocationRecord(target = identity/key/policy/etc.)
```

R14 may establish `CONFORMANCE_REVOKED` only within its authorized lifecycle scope. It may not revoke another artifact class unless independently authorized as the appropriate Revocation Authority.

If an upstream artifact is externally SUSPENDED or REVOKED, that state controls immediately and cannot be overridden by R14.

A subject whose lifecycle is `CONFORMANCE_REVOKED` may later requalify and be readmitted as a new lifecycle instance if governing policy allows. Historical records remain immutable.

---

## 24. Trigger-Specific Restoration

Restoration is not generic.

The active policy MUST define remediation requirements by trigger class.

Examples:

- compromised key -> rotate key; old key remains revoked;
- runtime provenance failure -> establish new trusted runtime identity;
- model change -> attest new model identity and re-evaluate role compatibility;
- governance supersession -> accept current governance version;
- capability overreach -> remove excess capability and verify inventory;
- qualification loss -> obtain new valid qualification basis;
- admission revocation -> cannot restore through conformance alone;
- mandatory requalification trigger -> complete a new Qualification path before conformance restoration;
- mandatory readmission trigger -> complete a new Admission path before conformance restoration.

A compromised or revoked artifact MUST NOT be reused merely because a new ConformanceStateDecision is positive.

---

## 25. Integration with Action Authorization

Conceptually:

```text
authorize(action) =
    qualification_usable_now
    AND admission_usable_now
    AND conformance_sufficient_for(action)
    AND session_governance_valid
    AND action_specific_ATE_requirements_satisfied
```

Typical mapping:

```text
CONFORMANT             -> may proceed to action evaluation
RESTRICTED             -> may proceed only inside allowed scope
REATTESTATION_REQUIRED -> deny affected scope
SUSPENDED              -> deny
CONFORMANCE_REVOKED    -> deny
UNKNOWN                -> deny
```

---

## 26. Lifecycle Epoch and TOCTOU Defense

Each authority-bearing lifecycle state MUST expose a monotonic `state_epoch` or equivalent.

Capability issuance records the observed epoch.

Before execution:

```text
if current_state_epoch != capability.observed_state_epoch:
    reverify current lifecycle state
```

At minimum:

1. state is checked at capability issuance;
2. critical suspension/revocation/conformance-revocation state is checked again inside or immediately before the execution boundary;
3. stale epoch cannot silently pass;
4. inability to resolve current required state fails closed.

This requirement reconciles conformance with the Enforcement Plane's final current-state verification principle.

---

## 27. Audit Events

Add at least:

```text
CONFORMANCE_TRIGGER_OBSERVED
CONFORMANCE_TRIGGER_SOURCE_STALE
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
CONFORMANCE_EPOCH_ADVANCED
TRIGGER_OBSERVATION_COALESCED
```

Every authority-changing transition must use the existing append-only AuditRecord semantics (including ordering/hash-chain/signature requirements) and preserve:

- subject/role/domain,
- prior and new state,
- state epoch,
- trigger(s),
- profile/version/digest,
- evaluation result,
- lifecycle authority,
- evidence references,
- affected scope,
- effective time.

---

## 28. Failure Semantics

### Required evidence unavailable
Not CONFORMANT.

### Required trigger source stale/unavailable
Not CONFORMANT after policy-defined bound.

### Evaluator unavailable
Never interpreted as successful conformance.

### Lifecycle authority unavailable
No new positive lifecycle state may be fabricated; prior state remains usable only within its explicit freshness bound.

### Conflicting authoritative evidence
Not CONFORMANT until resolved.

### Audit failure
For high-assurance authority-changing transitions, fail closed according to policy.

### Clock uncertainty
Time-dependent validity is not usable when trustworthy time cannot be established.

---

## 29. Minimal State Machine

```text
                 ┌───────────────┐
                 │  CONFORMANT   │
                 └───────┬───────┘
                         │ trigger / freshness expiry
         ┌───────────────┼────────────────┐
         ▼               ▼                ▼
REATTESTATION_REQUIRED RESTRICTED      SUSPENDED
         │               │                │
         │ fresh evidence│ remediation    │ investigation
         └───────┬───────┴────────┬───────┘
                 │                │
                 ▼                ▼
            CONFORMANT   CONFORMANCE_REVOKED
```

Transitions require authorized R14 decisions except externally authoritative revocation/trust-state changes already defined by controlling trust-state policy. Those MUST be honored directly, cannot be overridden by R14, and do not grant R14 revocation authority.

---

## 30. Required Implementation Properties

A conformant implementation should demonstrate:

- **P1 Upgrade invalidation** — material runtime/model change triggers re-attestation.
- **P2 Governance supersession** — stale COA/VA state loses sufficiency.
- **P3 Qualification loss propagation** — qualification suspension/revocation blocks affected authorization.
- **P4 Admission loss propagation** — admission suspension/revocation blocks affected authorization.
- **P5 Capability reduction** — RESTRICTED becomes reduced executable authority.
- **P6 Current-state enforcement** — stale positive state cannot override newer suspension, external revocation, or CONFORMANCE_REVOKED state.
- **P7 Bounded freshness** — missed trigger cannot preserve authority forever.
- **P8 Independent trigger source** — participant omission cannot hide a required observed change.
- **P9 Restoration discipline** — new authority only after trigger-specific remediation and fresh evidence.
- **P10 Accountability** — full lifecycle is reconstructable from durable evidence.

---

## 31. Minimal Local PoC Successor

After freeze, the first PoC should use no external model calls.

Required scenario:

```text
1. Qualify subject.
2. Admit subject.
3. Establish CONFORMANT at epoch N.
4. Authorize and execute one local governed action.
5. Change one material governed property (e.g. runtime_version v1 -> v2).
6. Independent source emits signed trigger observation.
7. Lifecycle moves to REATTESTATION_REQUIRED or SUSPENDED at epoch N+1.
8. Prove old/stale capability cannot execute.
9. Produce fresh post-change attestation evidence.
10. R13 evaluates.
11. R14 restores CONFORMANT at epoch N+2.
12. Prove a newly authorized action can execute.
13. Verify complete immutable audit chain.
```

This PoC directly tests the bridge among qualification, governance, conformance, authorization, enforcement, and accountability.

---

## 32. Explicit Non-Goals

v0.1.2 does not define:

- reputation scoring,
- intrinsic trustworthiness scoring,
- autonomous punishment,
- behavioral prediction,
- Internet-scale federation,
- production PKI implementation,
- blockchain trust,
- continuous semantic surveillance of model thoughts,
- replacement of ATE action authorization,
- replacement of qualification/admission.

---

## 33. Governing Principle

> Trust is not something an agent receives once. It is a current, evidence-backed condition that must remain demonstrably true for authority to continue.

Operationally:

```text
No current evidence
    -> no current conformance

No sufficient current conformance
    -> no affected governed capability
```

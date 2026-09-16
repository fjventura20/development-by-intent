# ATE Trust-Decision Composition Architecture v0.1

**Status:** Architecture candidate — DESIGN ONLY  
**Date:** 2026-09-16  
**Program:** Agent Trust Envelope (ATE)  
**Predecessor:** `ATE-TRUST-DECISION-COMPOSITION-INSPECTION-v0.1.md`

---

## 1. Purpose

This architecture defines how current ATE trust inputs compose into one deterministic, action-specific decision:

```text
TRUST_GRANTED
```

or

```text
TRUST_DENIED
```

It reconciles the original ATE production trust-decision model with later runtime identity, qualification, governance coverage, evidence integrity, risk/assurance, revocation, capability, and enforcement architecture.

It does not create a general agent trust score.

---

## 2. Controlling Principle

> **A governed action may be granted only when one canonical action, one verified runtime context, one current qualification state, one current governance-coverage state, one authoritative risk/assurance requirement, one bounded capability authorization, and one coherent current trust-state vector all agree.**

Trust composition is conjunctive.

A mandatory failed condition is not offset by strength elsewhere.

```text
strong identity + failed qualification != grant
strong qualification + stale governance != grant
human approval + failed structural invariant != grant
broad capability token + out-of-scope qualification != grant
```

No weighted score or average may convert a mandatory failure into grant unless an explicit signed policy defines an alternate admissible path that itself satisfies all required controls.

---

## 3. Architectural Position

```text
Requested Action
      |
      v
Canonical Action Context
      |
      v
Authoritative Risk Classification
      |
      v
Required Assurance / Governance / Approval Requirements
      |
      +-------------------------------+
      |                               |
      v                               v
VerifiedRuntimeContext         Current Trust State
      |                               |
      v                               |
Current Qualification                |
      |                               |
      v                               |
Current Governance Coverage          |
      |                               |
      v                               |
Capability Authorization             |
      |                               |
      +---------------+---------------+
                      |
                      v
            TrustDecisionInput
                      |
                      v
             Composition Verifier
                      |
            +---------+---------+
            |                   |
            v                   v
      TRUST_DENIED        TRUST_GRANTED
                                |
                                v
                       Capability Executor
```

The participant may propose an action and supply evidence references. It does not choose the authoritative risk class, qualification status, governance status, policy epoch, revocation state, or decision verdict.

---

## 4. Canonical Action First

All downstream trust reasoning SHALL operate on one canonical action representation.

Conceptual structure:

```text
CanonicalActionContext {
    action_schema_version
    operation
    canonical_target_identity
    canonical_parameters
    parameters_digest
    requested_by_principal_id
    requested_at
    target_state_digest?      // when required by policy
    aggregation_context_digest? // when anti-fragmentation policy applies
    canonical_action_digest
}
```

Risk classification, capability containment, qualification scope, approval, target-state binding, audit, and execution SHALL all bind the same `canonical_action_digest`.

If canonicalization is ambiguous or unsupported:

```text
TRUST_DENIED
TD_ACTION_CANONICALIZATION_FAILED
```

---

## 5. Authoritative Risk Classification

Risk is derived from authoritative signed policy applied to the canonical action.

```text
RiskDecisionContext {
    risk_classification_id
    risk_policy_digest
    canonical_action_digest
    risk_class
    required_assurance_profile
    required_human_approval_class?
    required_multi_authority_class?
    required_target_state_binding
    required_execution_rechecks[]
    risk_policy_epoch
    classification_digest
}
```

The participant-supplied risk label is non-authoritative.

Unknown risk fails closed.

Risk may be elevated later if authoritative target/resource resolution reveals higher impact. It may not be silently lowered by the participant or verifier convenience.

---

## 6. Verified Runtime Context

The runtime identity/attestation layer supplies one canonical `VerifiedRuntimeContext`.

Trust composition SHALL bind its digest rather than reconstruct runtime trust from informal fields.

At minimum composition relies on:

```text
verified_runtime_context_digest
principal_id
runtime_instance_id
runtime_public_key_digest
qualified_profile_digest
trust_domain_id
project_scope
model_identity / assurance
software_manifest_digest
configuration_profile_digest
coa_digest
value_architecture_digest
policy_bundle_digest
assurance_tier
runtime_verification_valid_until
runtime_verification_policy_epoch
```

The composition layer does not re-run attestation. It verifies that the supplied context is valid, current, authentic, in scope, and compatible with the current decision.

---

## 7. Qualification Decision Context

Qualification is admission eligibility, not action authorization.

The composition verifier SHALL resolve a current qualification context:

```text
QualificationDecisionContext {
    qualification_id
    qualification_credential_digest
    qualification_class_id
    qualified_profile_digest
    subject_principal_id
    status
    status_epoch
    permitted_capability_classes[]
    maximum_risk_class
    qualified_assurance_ceiling
    trust_domain_id
    project_scope
    evidence_package_digest
    requalification_policy_digest
    requalification_policy_epoch
    qualification_valid_until
    context_digest
}
```

Grant requires at minimum:

```text
status == ACTIVE
principal/profile == VerifiedRuntimeContext
requested capability inside qualification scope
risk_class <= maximum_risk_class
required assurance <= qualified assurance capability
trust domain/project scope compatible
qualification time/current-state valid
```

Any of:

```text
SUSPENDED
REQUALIFICATION_REQUIRED
EXPIRED
SUPERSEDED
REVOKED
NOT_QUALIFIED
UNKNOWN
```

fails closed for new qualification-dependent authorization unless a signed policy explicitly defines a narrower safe exception.

---

## 8. Governance Coverage Context

COA acceptance, VA policy, structural controls, behavioral evidence, interaction rules, and coverage status SHALL compose through current governance verification rather than one generic behavioral receipt.

Define:

```text
GovernanceCoverageContext {
    governance_source_digests[]
    clause_manifest_digests[]
    governance_coverage_manifest_digests[]
    coverage_policy_digest
    coverage_policy_epoch

    required_structural_control_receipt_digests[]
    required_behavioral_evidence_requirement_digests[]
    current_behavioral_evidence_receipt_digests[]
    required_acceptance_evidence_digests[]
    required_interaction_evidence_digests[]

    coa_digest
    value_architecture_digest
    policy_bundle_digest

    coverage_result
    current_state_digest
    valid_until
}
```

For grant:

- every required clause is accounted for under active coverage policy;
- required structural controls are currently satisfied;
- required behavioral evidence is current and in scope;
- required acceptance is current;
- required interaction/precedence evidence is current;
- no required dependency is revoked/suspended/expired/superseded incompatibly;
- bounded coverage claims are not inflated into broader semantic claims.

A historical `GovernanceCoverageManifest` alone is insufficient.

---

## 9. Evidence Currentness Context

The trust decision normally SHALL NOT re-evaluate raw behavioral tasks.

It SHALL verify that the qualification/governance dependencies rely on current, authentic evidence under the active lifecycle rules.

Conceptual summary:

```text
EvidenceCurrentnessContext {
    evidence_package_digest
    required_evidence_requirement_digests[]
    satisfied_receipt_digests[]
    evidence_lifecycle_state_digest
    campaign_history_state_digest?
    evidence_authority_state_epoch
    valid_until
}
```

This context preserves auditability without turning the Trust Decision Authority into a second behavioral evaluator.

---

## 10. Capability Authorization Context

The CapabilityToken remains an authority ceiling.

It does not establish trust by itself.

```text
CapabilityDecisionContext {
    capability_token_id
    capability_token_digest
    subject_principal_id
    runtime_or_session_binding?
    permitted_operations[]
    permitted_targets[]
    excluded_targets[]
    parameter_constraints
    trust_domain_id
    project_scope
    policy_digest
    issued_at
    valid_until
    nonce_or_authorization_id
    issuer_id
}
```

The canonical action must satisfy both:

```text
canonical_action subset_of CapabilityToken scope
AND
canonical_action capability_class subset_of Qualification scope
```

A capability token may be narrower than qualification. It may not be broader in a way that becomes executable.

Exclusions override broader allow scope.

---

## 11. Structural Controls and Approvals

Risk/governance policy may require additional artifacts.

Examples:

- human approval;
- second independent authority;
- threshold/quorum approval;
- current structural-control conformance receipt;
- mandatory audit availability;
- target-state binding;
- high-assurance key custody.

Represent them as explicit current dependencies:

```text
AdditionalAssuranceContext {
    required_approval_classes[]
    approval_artifact_digests[]
    structural_control_receipt_digests[]
    key_custody_evidence_digests[]
    audit_availability_receipt_digest?
    assurance_context_digest
    valid_until
}
```

Human approval supplements required controls. It does not override a failed invariant.

---

## 12. Current Trust-State Vector

The composition verifier SHALL bind current authoritative state, not merely historically valid signatures.

```text
CurrentTrustStateVector {
    trust_root_epoch
    policy_epoch
    revocation_epoch
    risk_policy_epoch
    qualification_status_epoch
    requalification_policy_epoch
    governance_coverage_policy_epoch
    evidence_authority_state_epoch?
    federation_epoch?
    observed_at
    state_vector_digest
}
```

All epochs are authoritative observations from recognized sources.

Unknown required current state fails closed.

Rollback below a newer known accepted epoch fails closed.

---

## 13. Point-in-Time Consistency

A grant MUST NOT knowingly compose mutually stale observations into a synthetic state that never existed coherently.

ATE v0.1 uses a **monotonic observation + final stability check** model rather than requiring one distributed ACID transaction.

### 13.1 Evaluation start

Capture all required authoritative epochs and current-state object digests.

### 13.2 Evaluate

Perform all composition gates against those observations.

### 13.3 Pre-sign stability check

Immediately before a grant is signed, re-read every dependency designated `DECISION_TIME_STABILITY_REQUIRED`.

If an authoritative epoch/digest changed:

```text
restart evaluation from current state
```

or, after a policy-defined bounded retry limit:

```text
TRUST_DENIED
TD_STATE_CHANGED_DURING_EVALUATION
```

A grant SHALL NOT be signed over a known superseded decision-time state vector.

### 13.4 Decision validity horizon

```text
TrustDecision.valid_until <= min(
    runtime context validity,
    qualification validity,
    governance-currentness validity,
    capability validity,
    approval validity,
    risk/policy validity where bounded,
    configured maximum TrustDecision lifetime
)
```

---

## 14. Recheck Classification

Every controlling dependency SHALL be classified as one of:

```text
DECISION_TIME_FINAL
DECISION_TIME_STABILITY_REQUIRED
EXECUTION_TIME_RECHECK_REQUIRED
```

Examples:

### DECISION_TIME_FINAL

Usually expensive/immutable conclusions whose current validity is represented through another revocable/current-state object:

- immutable evidence receipt contents;
- qualification evidence package digest;
- frozen protocol digest.

### DECISION_TIME_STABILITY_REQUIRED

Must remain unchanged through decision signing:

- qualification status epoch;
- active policy epoch;
- risk-policy epoch;
- governance coverage policy epoch;
- current revocation epoch where policy requires.

### EXECUTION_TIME_RECHECK_REQUIRED

Fast-changing state whose freshness matters at external effect time, especially A3/A4:

- TrustDecision revocation;
- revocation epoch/current state;
- active policy epoch;
- human approval freshness;
- target/resource state digest;
- capability/resource authorization state;
- mandatory audit availability.

The TrustDecision SHALL carry the required execution-time recheck contract.

---

## 15. Canonical TrustDecisionInput

The Trust Decision Authority SHALL consume one canonical immutable composition object.

```text
TrustDecisionInput {
    artifact_type = ATE_TRUST_DECISION_INPUT
    artifact_version

    canonical_action_context_digest
    requested_action_digest

    risk_decision_context_digest
    risk_class
    required_assurance_profile

    verified_runtime_context_digest

    qualification_decision_context_digest
    qualification_id
    qualification_status_epoch
    qualified_profile_digest

    governance_coverage_context_digest
    governance_coverage_manifest_digests[]

    evidence_currentness_context_digest
    evidence_package_digest

    capability_decision_context_digest
    capability_token_id
    capability_token_digest

    additional_assurance_context_digest?

    current_trust_state_vector_digest

    verifier_policy_digest
    composition_profile_id

    decision_time_recheck_requirements[]
    execution_time_recheck_requirements[]

    evaluated_at
    input_valid_until
}
```

Canonical representation SHALL be deterministic.

```text
trust_decision_input_digest = SHA256(canonical(TrustDecisionInput))
```

The participant cannot alter any decision input without changing the digest.

---

## 16. Deterministic Composition Rule

A grant is permitted if and only if every mandatory predicate is true.

Conceptually:

```text
GRANT iff

ACTION_VALID
AND RISK_CLASSIFICATION_CURRENT
AND REQUIRED_ASSURANCE_DERIVED
AND RUNTIME_CONTEXT_CURRENT
AND RUNTIME_SCOPE_MATCH
AND QUALIFICATION_ACTIVE
AND QUALIFIED_PROFILE_MATCH
AND QUALIFICATION_CAPABILITY_CONTAINS_ACTION
AND QUALIFICATION_RISK_CONTAINS_ACTION
AND QUALIFICATION_ASSURANCE_SUFFICIENT
AND GOVERNANCE_REQUIRED_COVERAGE_CURRENT
AND REQUIRED_STRUCTURAL_CONTROLS_CURRENT
AND REQUIRED_ACCEPTANCE_CURRENT
AND REQUIRED_BEHAVIORAL_EVIDENCE_CURRENT
AND REQUIRED_INTERACTION_EVIDENCE_CURRENT
AND CAPABILITY_TOKEN_CURRENT
AND CAPABILITY_TOKEN_CONTAINS_ACTION
AND REQUIRED_APPROVALS_CURRENT
AND REQUIRED_KEY_CUSTODY_SUFFICIENT
AND REQUIRED_AUDIT_AVAILABLE
AND ALL_REQUIRED_ISSUERS_AUTHORIZED_CURRENT
AND ALL_CURRENT_TRUST_STATE_KNOWN
AND ALL_CROSS_ARTIFACT_BINDINGS_MATCH
AND ALL_FRESHNESS_RULES_PASS
AND NONCE_REPLAY_PRECONDITION_PASS
AND DECISION_TIME_STATE_STABLE
```

Any false mandatory predicate yields denial.

---

## 17. Deterministic Gate Order

The composition verifier SHALL use a frozen gate order so equivalent canonical inputs/current state produce the same primary reason code.

Recommended order:

```text
D0  parse / supported versions / canonicalization
D1  canonical action validity
D2  authoritative risk classification + required assurance derivation
D3  trust-root / signer-role authority
D4  required current-state availability + rollback checks
D5  VerifiedRuntimeContext validity/currentness/scope
D6  qualification ACTIVE + exact profile/scope/risk/assurance ceilings
D7  governance coverage + structural/behavioral/acceptance/interaction dependencies
D8  capability token exact/subset semantics
D9  assurance-specific approvals/key custody/audit requirements
D10 freshness/expiration
D11 cross-artifact binding consistency
D12 nonce/replay precondition
D13 decision-time state stability
D14 TrustDecisionInput canonicalization/digest
```

Gate failure produces one primary reason code.

Secondary diagnostic codes MAY be recorded only if obtaining them cannot create side effects or weaken fail-closed behavior.

---

## 18. Reason-Code Model

Reason codes SHALL be stable machine-readable identifiers.

Minimum families:

```text
TD_PARSE_*
TD_ACTION_*
TD_RISK_*
TD_AUTHORITY_*
TD_STATE_*
TD_RUNTIME_*
TD_QUALIFICATION_*
TD_GOVERNANCE_*
TD_CAPABILITY_*
TD_ASSURANCE_*
TD_FRESHNESS_*
TD_BINDING_*
TD_REPLAY_*
TD_INTERNAL_*
```

Reason codes are diagnostic. They do not create alternate grant semantics.

Sensitive deployments MAY suppress user-facing detail while preserving authoritative audit detail.

---

## 19. TrustDecision Object

```text
TrustDecision {
    artifact_type = ATE_TRUST_DECISION
    artifact_version

    trust_decision_id
    trust_decision_input_digest

    verified_runtime_context_digest
    qualification_id
    qualification_status_epoch
    governance_coverage_context_digest

    requested_action_digest
    risk_class
    required_assurance_profile

    capability_token_id
    capability_token_digest

    current_trust_state_vector_digest

    verifier_policy_digest
    composition_profile_id

    execution_time_recheck_requirements[]

    verdict
    primary_reason_code
    secondary_reason_codes[]?

    issued_at
    valid_until
    nonce_or_operation_id

    trust_decision_authority_id
    signature_algorithm
    signature
}
```

Valid verdicts are exactly:

```text
TRUST_GRANTED
TRUST_DENIED
```

A system failure that prevents creation/authentication of a TrustDecision creates **no executable grant**. Absence of a signed decision is not a third executable verdict.

---

## 20. Grant Signing Rule

The Trust Decision Authority SHALL sign `TRUST_GRANTED` only after:

1. all gates pass;
2. `TrustDecisionInput` is canonicalized;
3. its digest is fixed;
4. decision-time stability checks pass;
5. validity horizon is calculated;
6. required execution-time rechecks are enumerated.

A decision authority SHALL NOT sign a grant and then fill in controlling context afterward.

---

## 21. Denial Semantics

Deterministic validation failures SHOULD produce a signed denial when the Trust Decision Authority is available.

A denial SHALL bind at least:

- decision/input identity or available canonical request digest;
- primary reason code;
- authoritative state vector where safely available;
- issued time;
- authority identity.

If parsing/canonicalization fails so early that a full `TrustDecisionInput` cannot exist, denial MAY bind a canonical failure-request digest rather than a normal decision-input digest.

No denial artifact is executable.

---

## 22. Operation Identity and Replay

Trust composition SHALL distinguish:

- `trust_decision_id` — decision record identity;
- `nonce_or_authorization_id` — replay-control identity;
- stable `operation_id` — intended external effect identity where idempotency requires it.

P1 demonstrated the importance of stable operation identity for crash-safe idempotency.

A future executor SHALL bind the decision to the stable operation identity used by the protected resource when repeat-sensitive effects are possible.

---

## 23. Executor Contract

The executor SHALL NOT repeat the full composition evaluation.

It SHALL independently verify the minimum critical contract:

- TrustDecision signature and authority;
- verdict is `TRUST_GRANTED`;
- decision unexpired;
- exact requested action/operation identity binding;
- capability/resource scope binding;
- nonce/replay state;
- required execution-time rechecks;
- current state for each recheck dependency;
- resource target-state constraint where required;
- no direct policy-defined block.

If any required recheck fails:

```text
NO EXECUTION
```

The executor does not convert a failed recheck into a fresh grant.

---

## 24. Cross-Artifact Binding Invariants

The composition verifier SHALL enforce at least:

```text
principal_id consistent across runtime / qualification / capability / approvals
qualified_profile_digest consistent across runtime / qualification / governance/evidence dependencies
trust_domain/project scope compatible across all controlling inputs
CoA/VA/policy digests compatible across runtime / qualification / governance
canonical_action_digest consistent across risk / capability / approval / decision
risk_class consistent with authoritative classification
required_assurance_profile consistent with risk policy
issuer roles valid for each artifact class
current-state epochs not rolled back
```

Individually valid artifacts that do not form one coherent context SHALL be denied.

---

## 25. Validity and Freshness

Artifact expiration and assurance freshness are separate.

A still-unexpired artifact may be too stale for the action's required assurance profile.

The composition verifier SHALL apply the stricter controlling deadline/freshness requirement.

```text
usable = cryptographically_valid
         AND temporally_valid
         AND assurance_fresh_enough
         AND current_state_valid
```

---

## 26. Current-State Failure Semantics

For any mandatory current-state dependency:

```text
UNKNOWN != ACTIVE
UNAVAILABLE != NOT_REVOKED
STALE != CURRENT
```

If current state cannot be established within the required assurance profile:

```text
TRUST_DENIED
TD_STATE_CURRENTNESS_UNAVAILABLE
```

or no signed decision if the authority itself is unavailable.

---

## 27. Federation

Cross-domain evidence does not directly grant local capability.

Where federation applies:

- foreign evidence is validated under explicit local federation policy;
- resulting local verified contexts are subject to local qualification/governance/risk/capability policy;
- local Trust Decision Authority issues the final decision;
- federation epoch is included in the current-state vector.

Trust is non-transitive by default.

---

## 28. Audit Requirements

Every composition attempt SHALL preserve enough evidence to reconstruct why it granted or denied.

At minimum audit references SHOULD include:

```text
canonical_action_digest
risk_decision_context_digest
verified_runtime_context_digest
qualification_decision_context_digest
governance_coverage_context_digest
evidence_currentness_context_digest
capability_decision_context_digest
additional_assurance_context_digest?
current_trust_state_vector_digest
trust_decision_input_digest?
verdict
reason code
TrustDecision digest
```

For profiles requiring mandatory audit availability, inability to commit required decision audit evidence blocks grant/execution according to policy.

---

## 29. Privacy / Minimal Disclosure

Trust composition SHOULD use digests and bounded verified contexts rather than unnecessarily embedding raw behavioral records, prompts, private data, or full governance text into the TrustDecision.

Audit/evidence retrieval may use privileged references where deeper forensic detail is authorized.

---

## 30. Security Invariants

### TD-I1 ACTION_FIRST
All trust predicates evaluate the same canonical action.

### TD-I2 NO_TRUST_SCORE
Mandatory failures cannot be compensated by unrelated strengths.

### TD-I3 RISK_AUTHORITATIVE
Participant cannot choose/downgrade controlling risk.

### TD-I4 RUNTIME_BINDING
Decision binds one current VerifiedRuntimeContext.

### TD-I5 QUALIFICATION_CURRENT
Only current usable qualification can contribute to grant.

### TD-I6 QUALIFICATION_SCOPE
Action capability/risk/assurance stay inside qualification ceilings.

### TD-I7 GOVERNANCE_CURRENT
Required governance dependencies are current and in scope.

### TD-I8 CAPABILITY_INTERSECTION
Action must be contained by both qualification scope and CapabilityToken authority.

### TD-I9 CURRENT_STATE
Required current trust state is known, current, and rollback-protected.

### TD-I10 POINT_IN_TIME
No grant is signed after a required decision-time dependency is known to have changed without re-evaluation.

### TD-I11 EXACT_CONTEXT
TrustDecision signs the exact `TrustDecisionInput` digest.

### TD-I12 DETERMINISTIC_DENIAL
Equivalent invalid canonical inputs/current state yield the same primary denial code under the same composition profile.

### TD-I13 RECHECK_CONTRACT
Execution-time recheck obligations are explicit and signed.

### TD-I14 NO_EXECUTOR_REEVALUATION
Executor rechecks fast-changing dependencies but does not silently create a new trust decision.

### TD-I15 FAIL_CLOSED
Missing, unknown, unavailable, malformed, stale, revoked, expired, or unsupported mandatory conditions never produce executable grant.

---

## 31. Explicit Non-Claims

This architecture does not establish that:

- an agent is generally trustworthy;
- qualification guarantees all future behavior;
- governance coverage proves moral character;
- behavioral evidence predicts every future case;
- signatures imply benevolent intent;
- current host/root compromise is solved;
- all distributed-state races are solved without profile-specific consistency controls;
- a human approval can safely override failed mandatory controls.

It establishes deterministic composition semantics for already-governed trust evidence.

---

## 32. Relationship to P1

P1 established local enforcement against an untrusted requester once trusted authority/executor identities and authorization artifacts were assumed.

This composition layer defines the modern context that should eventually be bound into the authorization consumed by that enforcement plane.

```text
Trust Evidence
    -> TrustDecisionInput
    -> TRUST_GRANTED
    -> bounded authorization / clearance
    -> P1-style executor enforcement
```

---

## 33. Relationship to P2

Frozen P2 tests local runtime trust establishment and emits `VerifiedRuntimeContext`.

P2 does not test this full composition architecture.

Its output becomes one required input here.

---

## 34. Relationship to Qualification and Evidence Protocols

The frozen qualification and evidence-integrity protocols test their respective local machinery.

They do not by themselves establish this composition layer.

Composition verifies their current outputs/references according to policy; it does not retroactively broaden their claims.

---

## 35. Recommended Next Step

Before freezing a composition protocol, perform:

**ATE Trust-Decision Composition Adversarial Review v0.1**

Attack at least:

- mixed valid contexts;
- action aliasing/canonicalization mismatch;
- risk downgrade;
- qualification/capability intersection errors;
- stale qualification status;
- stale governance coverage;
- current-state rollback;
- state change during evaluation;
- approval substitution;
- capability-token widening;
- cross-project reuse;
- execution-time recheck omission;
- decision-input substitution;
- denial nondeterminism;
- operation-id/replay confusion.

No Hermes or live-model experiment is required.

---

## 36. Architectural Conclusion

ATE trust composition should be understood as an exact intersection, not a score:

```text
Action
∩ Runtime Identity
∩ Qualification
∩ Governance Coverage
∩ Risk / Assurance
∩ Capability Authority
∩ Current Trust State
∩ Required Approvals / Structural Controls
∩ Replay / Freshness Preconditions
=
TRUST_GRANTED
```

Only when every mandatory intersection contains the same canonical action/context may the Trust Decision Authority sign a grant.

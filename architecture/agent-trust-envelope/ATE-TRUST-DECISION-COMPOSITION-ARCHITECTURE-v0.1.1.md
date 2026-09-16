# ATE Trust-Decision Composition Architecture v0.1.1

**Status:** Revised architecture candidate — DESIGN ONLY  
**Date:** 2026-09-16  
**Program:** Agent Trust Envelope (ATE)  
**Supersedes:** `ATE-TRUST-DECISION-COMPOSITION-ARCHITECTURE-v0.1.md`  
**Adversarial review:** `ATE-TRUST-DECISION-COMPOSITION-ADVERSARIAL-REVIEW-v0.1.md`

---

## 1. Controlling Principle

> **One exact canonical action/context may receive one bounded executable grant only when every mandatory trust predicate is simultaneously satisfied under authoritative current state, and the grant remains executable only while all dependencies designated execution-invalidating remain valid.**

ATE trust composition is an AND-gate, not a score.

A mandatory failure cannot be compensated by unrelated strengths.

---

## 2. Composition Chain

```text
Canonical Action
      |
      v
Authoritative Risk / Assurance
      |
      v
VerifiedRuntimeContext
      |
      v
Current Qualification
      |
      v
Current Governance Coverage
      |
      v
Capability Authorization
      |
      v
Required Structural / Approval Controls
      |
      v
Authoritative Current-State Vector
      |
      v
DecisionSemanticContext
      |
      v
TrustDecisionInput
      |
      v
Trust Decision Authority
      |
  +---+---+
  |       |
DENY    GRANT
          |
          v
Executor Recheck Contract
          |
          v
Bounded External Effect
```

---

## 3. Canonical Action and Capability Taxonomy

All decision components SHALL use one canonical action vocabulary.

```text
CanonicalActionContext {
    action_schema_version
    capability_taxonomy_id
    capability_taxonomy_version
    capability_taxonomy_digest

    operation
    capability_class
    canonical_target_identity
    canonical_parameters
    parameters_digest
    requested_by_principal_id
    requested_at

    target_state_digest?
    aggregation_context_digest?

    canonical_action_digest
}
```

Qualification, CapabilityToken, risk classification, governance structural rules, approvals, and execution adapters SHALL either use this exact taxonomy/version or a signed accepted translation mapping.

Unknown or ambiguous mapping fails closed.

Any material target/action resolution change requires:

```text
recanonicalize action
-> reclassify risk
-> recompute downstream contexts
```

No field-patching of an already-composed decision is permitted.

---

## 4. Authorization Instance and Grant Cardinality

Every one-time decision request has a stable:

```text
authorization_instance_id
```

created before executable grant issuance.

Required invariant:

> **One authorization instance may correspond to no more than one unique executable `TRUST_GRANTED` TrustDecision.**

Grant issuance SHALL be serialized/idempotent.

For the same authorization instance and same semantic decision context:

```text
retry -> return exact persisted grant
```

not a newly minted grant ID.

If controlling semantic context changes before grant issuance, the prior instance does not silently absorb the new context. A new explicit decision attempt/instance is required according to policy.

Historical denials may be retained as attempts; they are never executable.

---

## 5. Authoritative Risk Decision

Risk derives from signed policy over the canonical action.

```text
RiskDecisionContext {
    risk_classification_id
    risk_policy_id
    risk_policy_version
    risk_policy_digest
    risk_policy_epoch

    canonical_action_digest
    risk_class
    required_assurance_profile
    required_human_approval_class?
    required_multi_authority_class?
    required_target_state_binding
    required_execution_rechecks[]

    classification_digest
}
```

Unknown risk fails closed.

Participant-supplied risk is non-authoritative.

---

## 6. Verified Runtime Context

The composition verifier consumes a current authentic `VerifiedRuntimeContext` digest from the runtime identity/attestation layer.

Required bindings include:

```text
principal_id
runtime_instance_id
runtime_public_key_digest
qualified_profile_digest
trust_domain_id
project_scope
software/config identity
model identity/assurance
governance digests
assurance tier
validity
policy epoch
```

The composition verifier checks context currentness and scope; it does not re-run attestation.

---

## 7. Normalized Qualification Context

Qualification semantics SHALL be normalized before composition.

```text
QualificationDecisionContext {
    qualification_id
    qualification_credential_digest
    qualification_class_id
    subject_principal_id
    qualified_profile_digest

    status
    status_epoch

    capability_taxonomy_digest
    authorizable_capability_classes[]
    maximum_risk_class
    authorizable_assurance_profiles[]

    trust_domain_id
    project_scope

    evidence_package_digest
    requalification_policy_digest
    requalification_policy_epoch

    valid_until
    context_digest
}
```

Grant requires:

```text
status == ACTIVE
AND runtime principal/profile match
AND action capability in authorizable_capability_classes
AND risk_class <= maximum_risk_class
AND required_assurance_profile in authorizable_assurance_profiles
AND trust/project scope compatible
```

Do not infer assurance direction from ambiguous terms such as “minimum” or “ceiling.”

---

## 8. Current Governance Coverage Context

Governance coverage is a derived current result over authoritative dependencies.

```text
GovernanceCoverageContext {
    governance_source_digests[]
    clause_manifest_digests[]
    governance_coverage_manifest_digests[]
    coverage_policy_digest
    coverage_policy_epoch

    dependency_state_vector_digest
    coverage_evaluated_at
    coverage_valid_until

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
}
```

The context is not trusted merely because it is self-consistent. The verifier validates the authority and currentness of its underlying dependencies according to governance policy.

A historical coverage manifest alone cannot prove current coverage.

---

## 9. Evidence Currentness Context

The trust decision consumes current evidence state without re-running raw behavioral evaluation.

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

Each controlling evidence dependency has:

```text
lifecycle_class
invalidates_unexecuted_grants_on_change
execution_recheck_required
```

This distinguishes issuance-snapshot evidence from continuously-current evidence.

---

## 10. Capability Authorization Context

```text
CapabilityDecisionContext {
    capability_token_id
    capability_token_digest
    subject_principal_id
    runtime_or_session_binding?

    capability_taxonomy_digest
    permitted_operations[]
    permitted_capability_classes[]
    permitted_targets[]
    excluded_targets[]
    parameter_constraints

    trust_domain_id
    project_scope
    policy_digest

    issued_at
    valid_until
    authorization_instance_id
    issuer_id

    context_digest
}
```

Grant requires both:

```text
canonical action inside CapabilityToken authority
AND
canonical action capability inside Qualification authority
```

The executable scope is their intersection, never their union.

---

## 11. Approval and Structural-Control Binding

Every required approval binds the exact decision context appropriate to its role.

Minimum approval binding:

```text
canonical_action_digest
subject/runtime where policy requires
risk_class
required_assurance_profile
policy_digest / epoch
approval_role_class
issued_at
valid_until
```

Threshold/quorum approvals SHALL bind one common:

```text
approval_set_context_digest
```

so valid approvals from different requests cannot be combined.

Structural-control conformance receipts similarly bind the exact applicable policy/profile/scope.

Human approval never overrides a failed mandatory invariant.

---

## 12. Decision-Authority Ceilings

Trust Decision Authority is itself scoped authority.

Its recognized credential/policy SHALL constrain at least:

```text
permitted_trust_domains[]
permitted_project_scopes[]
permitted_capability_classes[]
maximum_risk_class
permitted_assurance_profiles[]
maximum_decision_lifetime
permitted_composition_profiles[]
validity / revocation handle
```

A correctly signed grant outside these ceilings is invalid.

The participant cannot select a more permissive decision authority.

---

## 13. Authority-Bound Current-State Observations

Current-state values are not trusted as bare epoch numbers.

Each observation binds:

```text
StateObservation {
    state_class
    state_authority_id
    state_object_digest
    state_epoch
    observed_at
    observation_digest
}
```

The verifier confirms the state authority is authorized for that state class.

`CurrentTrustStateVector` is a deterministic composition of verified observations:

```text
CurrentTrustStateVector {
    observations[]
    trust_root_epoch
    policy_epoch
    revocation_epoch
    risk_policy_epoch
    qualification_status_epoch
    requalification_policy_epoch
    governance_coverage_policy_epoch
    evidence_authority_state_epoch?
    federation_epoch?
    state_vector_digest
}
```

Rollback below a newer known accepted epoch fails closed.

---

## 14. Decision Semantic Context

Incidental wall-clock serialization SHALL NOT define semantic identity.

Define one immutable semantic composition:

```text
DecisionSemanticContext {
    authorization_instance_id

    canonical_action_context_digest
    risk_decision_context_digest
    verified_runtime_context_digest
    qualification_decision_context_digest
    governance_coverage_context_digest
    evidence_currentness_context_digest
    capability_decision_context_digest
    additional_assurance_context_digest?
    current_trust_state_vector_digest

    verifier_policy_digest

    composition_profile_id
    composition_profile_version
    composition_profile_digest

    operation_id?

    semantic_context_digest
}
```

No incidental `evaluated_at` field belongs in `semantic_context_digest` unless time itself is represented by an explicit controlling time-state/freshness object.

Equivalent semantic contexts therefore have stable identity for idempotent retry.

---

## 15. Composition Profile

The exact decision semantics are themselves versioned policy.

```text
CompositionProfile {
    composition_profile_id
    composition_profile_version
    gate_order
    within_gate_reason_precedence
    required_state_classes[]
    default_recheck_rules
    supported_taxonomy_versions[]
    fail_closed_rules
    digest
    issuer
    signature
}
```

Unknown or incompatibly superseded profiles fail closed.

The profile digest is signed into every TrustDecision.

---

## 16. Point-in-Time Consistency

ATE uses monotonic authoritative observations plus final stability checks.

### 16.1 Evaluate

Capture all required authoritative state observations and evaluate all predicates.

### 16.2 Pre-grant stability

Immediately before persisting/signing a grant, re-read every dependency marked:

```text
DECISION_TIME_STABILITY_REQUIRED
```

If any required state changed:

```text
restart evaluation
```

or, after bounded policy-defined retries:

```text
TRUST_DENIED
TD_STATE_CHANGED_DURING_EVALUATION
```

### 16.3 Known limitation

State can still change after signing. Therefore point-in-time consistency is completed by the execution-invalidating dependency contract below.

---

## 17. Execution-Invalidating Dependencies

Every controlling dependency has explicit change semantics:

```text
decision_time_class =
    DECISION_TIME_FINAL
    | DECISION_TIME_STABILITY_REQUIRED
    | EXECUTION_TIME_RECHECK_REQUIRED

invalidates_unexecuted_grants_on_change = true | false
```

If an authoritative dependency declares:

```text
invalidates_unexecuted_grants_on_change = true
```

risk/composition policy MUST NOT omit the required current recheck before external effect.

Potential execution-invalidating classes include:

- TrustDecision status/revocation;
- CapabilityToken/authorization state;
- active policy/revocation state;
- qualification status suspension/revocation;
- governance acceptance/current-state invalidation;
- human/threshold approval expiry/revocation;
- mutable target/resource state;
- mandatory audit availability.

This is how ATE closes the unavoidable interval between signing and external effect without re-running the whole verifier.

---

## 18. Validity Horizon

```text
TrustDecision.valid_until <= min(
    runtime context validity,
    qualification validity,
    governance currentness validity,
    capability validity,
    approval validity,
    evidence-currentness validity where lease-like,
    decision-authority maximum lifetime,
    risk/composition maximum lifetime
)
```

Assurance freshness may impose a stricter effective deadline than artifact expiration.

---

## 19. Action / Operation / Replay Identity Chain

Where external-effect idempotency matters, bind one complete chain:

```text
authorization_instance_id
    -> canonical_action_digest
    -> stable operation_id
    -> replay nonce / authorization state
    -> TrustDecision
    -> executor request
    -> resource idempotency key
```

Every link is cryptographically bound.

`trust_decision_id` is record identity and does not replace the stable operation identity.

---

## 20. TrustDecisionInput

```text
TrustDecisionInput {
    artifact_type = ATE_TRUST_DECISION_INPUT
    artifact_version

    semantic_context_digest
    authorization_instance_id
    canonical_action_digest

    risk_class
    required_assurance_profile

    verified_runtime_context_digest
    qualification_id
    qualification_status_epoch
    governance_coverage_context_digest

    capability_token_id
    capability_token_digest

    current_trust_state_vector_digest

    composition_profile_id
    composition_profile_version
    composition_profile_digest
    verifier_policy_digest

    decision_time_recheck_requirements[]
    execution_time_recheck_requirements[]

    input_valid_until
}
```

Canonical digest:

```text
trust_decision_input_digest = SHA256(canonical(TrustDecisionInput))
```

---

## 21. Deterministic Composition Rule

`TRUST_GRANTED` is permitted if and only if all mandatory predicates pass:

```text
ACTION_VALID
RISK_CLASSIFICATION_CURRENT
REQUIRED_ASSURANCE_DERIVED
TRUST_ROOTS_AND_SIGNER_ROLES_VALID
CURRENT_STATE_KNOWN_AND_NOT_ROLLED_BACK
RUNTIME_CONTEXT_CURRENT_AND_IN_SCOPE
QUALIFICATION_ACTIVE
QUALIFIED_PROFILE_MATCH
QUALIFICATION_CAPABILITY_CONTAINS_ACTION
QUALIFICATION_RISK_CONTAINS_ACTION
QUALIFICATION_ASSURANCE_CONTAINS_REQUIRED_PROFILE
GOVERNANCE_REQUIRED_COVERAGE_CURRENT
REQUIRED_STRUCTURAL_CONTROLS_CURRENT
REQUIRED_ACCEPTANCE_CURRENT
REQUIRED_BEHAVIORAL_EVIDENCE_CURRENT
REQUIRED_INTERACTION_EVIDENCE_CURRENT
CAPABILITY_TOKEN_CURRENT
CAPABILITY_TOKEN_CONTAINS_ACTION
REQUIRED_APPROVALS_CURRENT_AND_CONTEXT_BOUND
REQUIRED_KEY_CUSTODY_SUFFICIENT
REQUIRED_AUDIT_AVAILABLE
ALL_CROSS_ARTIFACT_BINDINGS_MATCH
ALL_FRESHNESS_RULES_PASS
REPLAY_PRECONDITION_PASS
DECISION_AUTHORITY_WITHIN_CEILING
DECISION_TIME_STATE_STABLE
```

Otherwise deny.

No score threshold exists.

---

## 22. Deterministic Gate and Reason Precedence

CompositionProfile SHALL freeze both top-level gate order and within-gate reason precedence.

Reference top-level order:

```text
D0  parse / type / version / canonicalization
D1  canonical action / capability taxonomy
D2  authoritative risk + assurance derivation
D3  trust-root / signer-role authority
D4  current-state availability / rollback
D5  VerifiedRuntimeContext
D6  qualification currentness / subject / profile / capability / risk / assurance
D7  governance coverage and dependencies
D8  CapabilityToken exact/subset containment
D9  approvals / key custody / structural / audit assurance
D10 freshness / expiration
D11 cross-artifact bindings
D12 replay/authorization-instance preconditions
D13 decision-authority ceilings
D14 decision-time stability
D15 semantic context + TrustDecisionInput digest
```

Each gate SHALL freeze deterministic subpredicate precedence or an equivalent deterministic failed-predicate selection rule.

Equivalent invalid canonical inputs/current state under the same profile must produce the same primary reason code.

---

## 23. TrustDecision

```text
TrustDecision {
    artifact_type = ATE_TRUST_DECISION
    artifact_version

    trust_decision_id
    authorization_instance_id
    trust_decision_input_digest
    semantic_context_digest

    canonical_action_digest
    operation_id?

    verified_runtime_context_digest
    qualification_id
    qualification_status_epoch
    governance_coverage_context_digest

    risk_class
    required_assurance_profile

    capability_token_id
    capability_token_digest

    current_trust_state_vector_digest

    composition_profile_id
    composition_profile_version
    composition_profile_digest
    verifier_policy_digest

    execution_time_recheck_requirements[]

    verdict
    primary_reason_code
    secondary_reason_codes[]?

    evaluated_at
    issued_at
    valid_until

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

Absence of a signed decision is not an executable third verdict.

---

## 24. Grant Issuance Procedure

For an authorization instance:

1. resolve/persist its stable identity;
2. build and verify semantic context;
3. evaluate all gates;
4. perform decision-time stability checks;
5. compute TrustDecisionInput digest;
6. serialize against existing grant state for the authorization instance;
7. if exact persisted grant already exists, return it;
8. otherwise verify Decision Authority ceilings;
9. calculate validity/recheck contract;
10. persist/sign exactly one grant;
11. emit audit evidence.

Concurrent issuance requests must converge on the same persisted grant or one grant plus deterministic non-executable results.

---

## 25. Denial Semantics

Deterministic validation failures SHOULD produce signed denials when authority is available.

Denials bind:

```text
canonical action or failure-request digest
semantic context digest when constructible
primary reason code
applicable state-vector digest
composition-profile digest
issued_at
authority identity
```

Denials are non-executable and need not satisfy one-grant cardinality, but formal attempt history remains auditable.

---

## 26. Executor Contract

The executor does not repeat full trust composition.

It independently verifies:

- TrustDecision signature/authority/ceiling;
- `TRUST_GRANTED`;
- exact action + stable operation identity;
- decision freshness;
- authorization/replay state;
- capability/resource scope;
- every signed execution-time recheck requirement;
- current state of every dependency that invalidates unexecuted grants;
- target/resource state where required;
- mandatory audit availability where required.

A failed execution-time recheck produces no execution and does not create a fresh grant.

---

## 27. Cross-Artifact Invariants

At minimum:

```text
principal identity consistent
runtime/qualification profile consistent
trust domain/project scope compatible
governance digests compatible
canonical capability taxonomy compatible
canonical action consistent across risk/capability/approval/decision
risk class authoritative
assurance profile authoritative and qualified
issuer roles authorized
state authorities authorized
state epochs non-rollback
authorization instance bound to action/operation/replay identity
approval set bound to one context
composition profile exact/versioned
```

Individually valid artifacts that do not form one coherent context are denied.

---

## 28. Audit Contract

Decision audit SHOULD preserve references/digests sufficient to reconstruct:

```text
canonical action
risk context
runtime context
qualification context
governance context
evidence-currentness context
capability context
approval/structural context
current-state observations
semantic context
TrustDecisionInput
TrustDecision
verdict/reason
```

Formal correction records append; prior signed history is not silently rewritten.

---

## 29. Security Invariants

### TD-I1 ACTION_FIRST
One canonical action drives every downstream check.

### TD-I2 CANONICAL_CAPABILITY_TAXONOMY
Qualification, capability, risk, governance, and execution use one accepted action taxonomy/mapping.

### TD-I3 NO_TRUST_SCORE
Mandatory failures cannot be compensated.

### TD-I4 ONE_GRANT_PER_AUTHORIZATION_INSTANCE
At most one unique executable grant exists per authorization instance.

### TD-I5 RISK_AUTHORITATIVE
Participant cannot control risk.

### TD-I6 RUNTIME_BINDING
Decision binds one current VerifiedRuntimeContext.

### TD-I7 QUALIFICATION_CURRENT_AND_SCOPED
Qualification is ACTIVE and action/risk/assurance fit its explicit authority.

### TD-I8 GOVERNANCE_CURRENT
Required governance dependencies are current and bounded.

### TD-I9 CAPABILITY_INTERSECTION
Action lies in both qualification and CapabilityToken authority.

### TD-I10 AUTHORITY_CEILINGS
Every signer/state/decision authority acts inside its registered scope.

### TD-I11 CURRENT_STATE_PROVENANCE
State epochs/digests bind authorized state sources.

### TD-I12 POINT_IN_TIME_STABILITY
Known decision-time state change forces re-evaluation or denial.

### TD-I13 EXECUTION_INVALIDATION
Dependencies declared immediately execution-invalidating are rechecked before effect.

### TD-I14 EXACT_SEMANTIC_CONTEXT
TrustDecision binds the stable semantic-context and decision-input digests.

### TD-I15 DETERMINISTIC_DENIAL
Same invalid semantics/current state/profile produce same primary reason.

### TD-I16 ACTION_OPERATION_REPLAY_CHAIN
Authorization instance, action, operation identity, replay state, and resource idempotency bind coherently.

### TD-I17 FAIL_CLOSED
Unknown/missing/stale/invalid/unsupported mandatory conditions never grant.

---

## 30. Explicit Non-Claims

This architecture does not claim:

- general agent trustworthiness;
- universal behavioral predictability;
- moral character;
- distributed ACID across all trust authorities;
- safety under compromised roots/host/kernel unless separately addressed;
- that human approval can override failed mandatory controls.

It defines exact trust-decision composition over verified bounded inputs.

---

## 31. Relationship to Existing ATE Layers

```text
Evidence Integrity
       |
Governance Coverage
       |
Qualification
       |
Runtime Trust (P2 output)
       |
Risk / Capability / Revocation
       |
       v
DecisionSemanticContext
       |
       v
TrustDecisionInput
       |
       v
TRUST_GRANTED / TRUST_DENIED
       |
       v
P1-style Enforcement Plane
```

Each upstream layer keeps its own claim boundary.

Composition does not broaden it.

---

## 32. Recommended Next Step

Perform one final adversarial review of v0.1.1 before protocol design.

The review should attack:

- concurrent grant issuance;
- semantic-context retry identity;
- state-source substitution;
- lifecycle/recheck omissions;
- authorization-instance reuse after context change;
- taxonomy mapping ambiguity;
- approval-set mixing;
- authority-ceiling bypass;
- material target change without recomposition;
- executor accepting stale execution-invalidating state;
- deterministic-reason collisions;
- replay/operation-id cross-binding.

No Hermes or live model is required.

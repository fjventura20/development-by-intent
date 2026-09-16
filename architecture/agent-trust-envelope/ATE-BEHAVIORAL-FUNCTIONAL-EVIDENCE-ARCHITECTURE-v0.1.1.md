# ATE Behavioral & Functional Evidence Architecture v0.1.1

**Status:** Revised architecture candidate — DESIGN ONLY  
**Date:** 2026-09-16  
**Program:** Agent Trust Envelope (ATE)  
**Supersedes:** `ATE-BEHAVIORAL-FUNCTIONAL-EVIDENCE-ARCHITECTURE-v0.1.md`  
**Adversarial review:** `ATE-BEHAVIORAL-FUNCTIONAL-EVIDENCE-ADVERSARIAL-REVIEW-v0.1.md`  
**Upstream dependency:** `ATE-AGENT-QUALIFICATION-REQUALIFICATION-ARCHITECTURE-v0.1.1.md`

---

## 1. Controlling Principle

> **Evidence is a bounded, auditable observation of demonstrated behavior or capability under a frozen and precommitted evaluation process. It is not a general trust score, not qualification itself, and not authorization.**

ATE evidence must establish not only what result was reported, but also why that result could not have been manufactured by hiding unfavorable attempts, changing the protocol after outcomes were known, widening the claim beyond the evaluated conditions, or substituting unauthorized evaluators/runners.

---

## 2. Corrected Evidence Chain

```text
Evidence Requirement
       |
       v
Frozen Evaluation Protocol
       |
       v
Formal Evaluation Campaign
       |
       v
FormalRunRegistration        <- committed before first subject invocation
       |
       v
Evaluation Execution
       |
       +--> complete attempt ledger
       +--> deterministic test receipts
       +--> behavioral observation receipts
       |
       v
RunCompletionRecord
       |
       v
Authorized Evaluation / Aggregation
       |
       v
Behavioral / Functional Evidence Receipt
       |
       v
Current Trust-State Check
       |
       v
Qualification Evidence Package Admission
```

No stage implies the next without verification.

---

## 3. Evidence Classes

### 3.1 Deterministic Functional Evidence

Use machine-verifiable oracles when the claim permits them.

Examples:

- conformance tests;
- protocol behavior;
- exact transformation correctness;
- signature/access-control checks;
- invariant preservation;
- deterministic capability execution.

Preferred result:

```text
PASS | FAIL | ERROR
```

A discretionary model evaluator SHOULD NOT replace a deterministic oracle when a reliable deterministic oracle exists.

### 3.2 Sampled Behavioral Evidence

Used for stochastic, semantic, contextual, or quality-sensitive claims such as:

- instruction following;
- refusal behavior;
- governance adherence;
- factual discipline;
- honesty/non-deception indicators;
- escalation behavior;
- bounded-agency behavior.

Behavioral evidence is bounded to its sample/population, protocol, evaluator method, subject/profile, and environment.

### 3.3 Operational / Drift Evidence

Post-qualification observations such as audit anomalies, canary checks, denial patterns, incidents, or regression monitoring.

Operational evidence may affect current qualification state according to policy but does not silently rewrite qualification-time evidence.

---

## 4. Evidence Requirement

Each controlling evidence requirement is signed policy.

```text
EvidenceRequirement {
    evidence_requirement_id
    evidence_class_id
    evidence_type
    claim_scope
    subject_binding_requirements
    qualified_profile_constraints
    accepted_protocol_ids_versions_digests
    evaluator_rules
    runner_rules
    formal_attempt_policy
    scoring_rule_id
    aggregation_rule_id
    acceptance_rule_id
    lifecycle_class
    maximum_age?
    refresh_interval?
    trust_domain_id
    project_scope?
    maximum_risk_class_supported?
    evidence_authority_constraints
    policy_epoch
    issuer
    signature
}
```

The requirement defines what must be demonstrated. It does not assert that demonstration occurred.

---

## 5. Claim Scope

Every evidence receipt binds an explicit claim scope:

```text
claim_scope {
    capability_or_behavior_class
    task/domain constraints
    input/population constraints
    environment constraints
    tool/capability envelope
    governance constraints
    risk/assurance applicability
    portability scope
    exclusions/non_claims[]
}
```

Qualification admission MUST NOT widen this scope.

Normative non-expansion rule:

```text
target operational capability envelope
    <=
evaluated capability envelope
```

unless a signed compatibility/non-interference decision accepted by qualification policy establishes safe reuse.

Restricted-environment success is not evidence for broader capability exposure.

---

## 6. Frozen Evaluation Protocol

A formal protocol is immutable and content-addressable before formal registration.

```text
EvaluationProtocol {
    protocol_id
    protocol_version
    evidence_class_id
    evaluation question
    subject/profile binding rules
    corpus/generator specification
    case taxonomy
    sampling rule
    seed/randomness rule
    execution environment requirements
    tool/capability profile
    evaluator selection/profile rules
    evaluator independence rules
    scoring rubric or deterministic oracle
    aggregation rule
    acceptance rule
    invalid-run rules
    retry rules
    missing-output rules
    stopping rules
    formal-attempt rules or reference
    evidence outputs required
    canonicalization/digest rules
    protocol_authority_id
    protocol_digest
    signature
}
```

Protocol Authority must be authorized for the evidence class/protocol family.

After freeze, result-sensitive changes require a new protocol version.

---

## 7. Formal Evaluation Campaign

Repeated formal runs belong to one auditable campaign when they address the same qualification/evidence requirement.

```text
FormalEvaluationCampaign {
    campaign_id
    evidence_requirement_id
    subject_principal_id
    qualified_profile_digest
    protocol_digest
    formal_attempt_policy_digest
    opened_at
    campaign_authority_id
    signature
}
```

Every formal run attempt under the campaign remains historically visible.

A later passing attempt does not erase a prior formal failure.

Policy decides whether and under what conditions later evidence supersedes, remediates, or coexists with prior failure.

---

## 8. Formal Attempt Policy

The Evidence Requirement or referenced signed policy SHALL define:

```text
formal_attempt_policy {
    repeat_formal_attempts_allowed
    maximum_attempts?
    cooldown_or_change_requirement?
    whether profile/protocol change is required after failure
    whether prior failure remains controlling
    supersession/remediation semantics
    campaign closure rules
}
```

Starting fresh campaign identifiers solely to hide prior failures is prohibited.

Qualification Authority SHALL consider the campaign history required by policy.

---

## 9. Formal Run Registration

Before the first subject invocation in a formal run, an immutable signed registration SHALL be committed.

```text
FormalRunRegistration {
    formal_run_id
    campaign_id
    evidence_requirement_id
    protocol_digest
    subject_principal_id
    qualified_profile_digest
    software/model/config/tool profile digests
    governance digests
    execution_environment_digest
    runner_id
    runner_profile_digest
    evaluator_ids or evaluator_selection_rule_digest
    evaluator_profile_digests if predetermined
    corpus/generator_digest
    case_ids[] OR generator_id
    seed OR deterministic_seed_derivation_rule
    sample_size
    replication_rule/count
    scoring_rule_digest
    aggregation_rule_digest
    acceptance_rule_digest
    retry_rule_digest
    stopping_rule_digest
    registered_at
    registration_authority_id
    registration_digest
    signature
}
```

The registration MUST precede subject execution.

A formal evidence receipt is invalid if its population cannot be reconciled to the registration.

---

## 10. Seed and Sample Selection

Outcome-selectable sampling is prohibited.

Formal sampling SHALL use one protocol-authorized method:

- cases fixed in the protocol;
- cases fixed in FormalRunRegistration;
- seed fixed in protocol;
- seed fixed in registration before execution;
- seed derived deterministically from a precommitted external nonce/context;
- trusted sampler signs selection before execution.

Trying multiple seeds/populations and registering the favorable one after observing subject behavior invalidates the run.

---

## 11. Runner Profile and Authority

Execution provenance is separate from evaluation.

```text
RunnerProfile {
    runner_id
    runner_role
    runner_software_digest
    runner_configuration_digest
    environment/capability constraints
    trust_domain
    allowed_protocol_families
    validity
    issuer
    profile_digest
    signature
}
```

The runner attests that the registered protocol/population was actually executed against the registered subject/profile and that every attempt/terminal state was recorded.

Runner/evaluator role combination is permitted only when policy allows it.

---

## 12. Evaluator Profile

Every controlling behavioral evaluation binds the exact evaluator profile.

```text
EvaluatorProfile {
    evaluator_id
    evaluator_type
    evaluator_software_or_model_identity
    evaluator_configuration_digest
    evaluator_instruction_or_prompt_digest?
    tool_capability_profile_digest?
    decoding_sampling_configuration?
    rubric_versions_allowed[]
    evaluator_role
    independence_credential_id
    trust_domain
    validity
    issuer
    evaluator_profile_digest
    signature
}
```

For humans, software-specific fields may be replaced by role, training/credential, rubric version, and review-procedure bindings.

A stable evaluator display name is insufficient if controlling configuration changes.

---

## 13. Evaluator Independence

Conceptual classes remain:

```text
E0_SELF
E1_SAME_OPERATOR
E2_INDEPENDENT_ROLE
E3_INDEPENDENT_ORG
```

Independence class is not self-asserted.

Use authoritative relationship evidence such as:

```text
EvaluatorIndependenceCredential {
    evaluator_id
    operator_or_admin_domain
    relationship_to_subject
    relationship_to_runner
    independence_class
    trust_domain
    not_before
    valid_until
    issuer
    signature
}
```

A second process, model name, or API provider does not automatically establish E2/E3.

---

## 14. Complete Attempt Ledger

Every registered case and every protocol-authorized retry SHALL appear in a content-addressable attempt ledger.

```text
AttemptLedgerEntry {
    formal_run_id
    case_id
    replication_id
    attempt_number
    invocation_id
    input_digest
    subject_output_digest?
    terminal_state
    failure_class?
    started_at
    ended_at
    runner_receipt_ref
}
```

Terminal states include at minimum:

```text
PASS
FAIL
VALID_SCORED
INVALID_PROTOCOL_DEFINED
ERROR
TIMEOUT
NOT_EXECUTED
```

Protocol defines which states produce a valid formal run.

No unfavorable attempt may be deleted from the formal ledger.

---

## 15. Failure-Class Separation

The architecture distinguishes:

```text
SUBJECT_FAILURE
EVALUATOR_FAILURE
RUNNER_FAILURE
INFRASTRUCTURE_FAILURE
PROTOCOL_INVALIDITY
```

Consequence is defined by frozen protocol.

Runner/evaluator/infrastructure failure normally maps to protocol-defined retry, `INCONCLUSIVE`, or `INVALID_RUN`—not automatically to subject PASS or FAIL.

This prevents both false exoneration and false condemnation.

---

## 16. Functional Test Receipt

```text
FunctionalTestReceipt {
    test_receipt_id
    formal_run_id
    registration_digest
    protocol_digest
    case_id
    replication_id
    attempt_number
    subject_principal_id
    qualified_profile_digest
    input_digest
    oracle_id/version/digest
    expected_outcome_digest?
    observed_outcome_digest
    result
    reason_code
    runner_id
    receipt_digest
    signature_if_required
}
```

Deterministic aggregate results reference every controlling test receipt.

---

## 17. Behavioral Observation Receipt

```text
BehavioralObservationReceipt {
    observation_id
    formal_run_id
    registration_digest
    protocol_digest
    case_id
    replication_id
    attempt_number
    subject_principal_id
    qualified_profile_digest
    input_digest
    output_digest
    context/tool_trace_digests[]
    evaluator_id
    evaluator_profile_digest
    evaluator_independence_credential_id
    rubric_digest
    score_vector_or_category
    reason_codes[]
    validity
    invalid_reason?
    evaluated_at
    evaluator_signature
}
```

Underlying raw artifacts may be access-controlled, but receipt substitution must be detectable.

---

## 18. Run Completion Record

At the end of each formal run, the authorized runner signs:

```text
RunCompletionRecord {
    formal_run_id
    campaign_id
    registration_digest
    run_manifest_digest
    attempt_ledger_digest
    receipt_set_digest
    declared_cases
    attempted_cases
    valid_cases
    invalid_cases
    passes
    fails
    errors
    timeouts
    not_executed
    started_at
    completed_at
    runner_id
    runner_profile_digest
    result = COMPLETE | INCOMPLETE | INVALID
    reason_codes[]
    signature
}
```

A formal evidence PASS requires completion validity under the frozen protocol.

---

## 19. Canonical Receipt Set

The complete underlying receipt set SHALL be canonicalized and hashed.

Evidence Issuer must verify before aggregate issuance:

- every required receipt exists;
- signatures/roles/profiles are valid;
- each receipt belongs to the registered run;
- case/replication/attempt identities match the ledger;
- duplicates are rejected unless protocol-authorized;
- every registered case/replication is accounted for;
- receipt set matches `RunCompletionRecord`;
- aggregate metrics recompute from the receipt set.

The Evidence Issuer cannot invent missing evaluator results merely by signing an aggregate.

---

## 20. Rubric and Aggregation

Behavioral scoring binds to a frozen rubric:

```text
EvaluationRubric {
    rubric_id
    rubric_version
    dimensions[]
    scale semantics
    weighting
    critical-failure rules
    ambiguity rules
    missing-information rules
    evaluator instructions
    rubric_digest
}
```

The aggregation rule defines handling of invalid cases, disagreement, missing scores, ties, critical overrides, and partial completion.

Every controlling derived metric must be deterministically recomputable from the canonical receipt set plus frozen aggregation rule.

---

## 21. Evaluator Disagreement

Multi-evaluator protocols predefine disagreement handling, e.g.:

- unanimity;
- majority;
- conservative/worst-case;
- preregistered adjudicator;
- disagreement -> INCONCLUSIVE.

Post-hoc evaluator replacement or selective retention is prohibited.

---

## 22. Anti-Cherry-Picking

Prohibited unless explicitly frozen into protocol:

- best-of-N output selection;
- rerun-until-pass;
- favorable seed selection;
- favorable formal-run selection while hiding prior attempts;
- evaluator replacement after scores are known;
- selective exclusion of timeouts/errors;
- sample truncation after a favorable prefix;
- threshold/weight changes after outcomes.

If retries are allowed, all attempts remain in the ledger and aggregation follows frozen retry semantics.

---

## 23. Non-Deterministic Subject Rules

For stochastic systems the protocol predefines:

```text
single-shot
fixed N replication
session-block replication
multiple deployment/reconstruction replication
```

Replication cannot be expanded after unfavorable observation unless the frozen stopping rule already requires/allows it.

---

## 24. Hidden / Held-Out Corpus Semantics

If hiddenness contributes materially to the claim, preserve custody evidence:

```text
CorpusCustodyRecord {
    corpus_id/version/digest
    custodian_id
    exposure_policy
    subject_access_status
    runner_access_status
    evaluator_access_status
    disclosure_timing
    contamination_or_declassification_status
    issued_at
    signature
}
```

Unknown exposure status MUST NOT be represented as confirmed held-out/contamination-resistant evaluation.

Hiddenness is optional unless the Evidence Requirement requires it.

---

## 25. Evidence Result Vocabulary

Frozen protocols SHALL define:

```text
EVIDENCE_PASS
EVIDENCE_FAIL
EVIDENCE_INCONCLUSIVE
INVALID_RUN
```

Result semantics include handling for infrastructure/evaluator/runner failure.

`EVIDENCE_PASS` may satisfy one evidence requirement; it does not itself issue qualification.

---

## 26. Behavioral Evidence Receipt

```text
BehavioralEvidenceReceipt {
    evidence_receipt_id
    campaign_id
    formal_run_id
    evidence_requirement_id
    evidence_class_id
    claim_scope_digest
    subject_principal_id
    qualified_profile_digest
    protocol_digest
    registration_digest
    run_manifest_digest
    run_completion_record_digest
    attempt_ledger_digest
    receipt_set_digest
    corpus_or_generator_digest
    execution_environment_digest
    runner_profile_digest
    evaluator_profile_digests[]
    evaluator_independence_refs[]
    rubric_digest
    aggregation_rule_digest
    acceptance_rule_digest
    declared_sample_size
    valid_sample_size
    result
    summary_metrics
    critical_failures[]
    prior_formal_attempt_refs[]
    evidence_lifecycle_class
    issued_at
    not_before
    valid_until?
    refresh_due_at?
    revocation_handle
    evidence_issuer_id
    signature_algorithm
    signature
}
```

---

## 27. Functional Evidence Receipt

```text
FunctionalEvidenceReceipt {
    evidence_receipt_id
    campaign_id
    formal_run_id
    evidence_requirement_id
    evidence_class_id
    claim_scope_digest
    subject_principal_id
    qualified_profile_digest
    protocol_digest
    registration_digest
    run_completion_record_digest
    attempt_ledger_digest
    test_receipt_set_digest
    controlling_test_count
    pass_count
    fail_count
    error_count
    prior_formal_attempt_refs[]
    result
    evidence_lifecycle_class
    issued_at
    not_before
    valid_until?
    revocation_handle
    evidence_issuer_id
    signature
}
```

---

## 28. Evidence Issuer Authority Ceilings

Evidence Issuer credential defines at least:

```text
may_issue_evidence_classes[]
accepted_protocol_families[]
maximum_claim_scope
maximum_risk_class_supported
permitted_trust_domains[]
permitted_project_scopes[]
maximum_validity
may_revoke
```

Issuer cannot expand protocol claim scope, evaluator independence, assurance, risk coverage, or evidence lifecycle beyond underlying evidence/policy.

---

## 29. Evidence Lifecycle

Evidence uses qualification architecture lifecycle classes:

```text
ISSUANCE_SNAPSHOT
CONTINUOUSLY_CURRENT
PERIODICALLY_REFRESHED
```

Lifecycle is fixed by the Evidence Requirement.

Freshness does not repair profile mismatch.

A recent evaluation of the wrong profile is still inapplicable.

---

## 30. Evaluator / Runner Compromise Semantics

The Evidence Requirement SHALL define whether evaluator/runner authority validity is:

```text
ISSUANCE_TIME_ONLY
CONTINUOUSLY_CONTROLLING
COMPROMISE_REQUIRES_REVIEW
```

This avoids two extremes:

- trusting compromised current authorities forever;
- invalidating all historical evidence automatically after ordinary credential expiry.

Security incident/revocation policy controls downstream qualification status.

---

## 31. Current Evidence Trust State

Evidence current-state verification integrates with `ATE-REVOCATION-TRUST-STATE-MODEL-v0.1.md`.

Verifier/Qualification Authority SHALL evaluate the current authoritative trust/revocation state and reject rollback below a newer known accepted epoch.

Evidence-specific status metadata MUST NOT create a weaker parallel revocation system.

A cryptographically valid historical receipt may remain historically authentic while being unusable for a new qualification decision.

---

## 32. Evidence Revocation / Supersession

Revocation reasons include:

- protocol defect;
- runner/evaluator compromise;
- corpus corruption/leakage where material;
- subject/profile misbinding;
- scoring defect;
- fabrication/tampering;
- issuer compromise.

Supersession records lineage; it does not erase old evidence.

Qualification policy determines downstream suspension/requalification/revocation consequences.

---

## 33. Evidence Package Admission

Qualification Authority admits a receipt only when:

```text
active Evidence Requirement matches
AND protocol digest/version accepted
AND campaign/formal-attempt history satisfies policy
AND pre-run registration valid
AND completion/attempt accounting valid
AND subject/profile binding valid
AND claim scope covers requirement without expansion
AND evaluator/runner/issuer authorities valid for required roles
AND independence requirement satisfied
AND metrics recompute
AND lifecycle/freshness satisfied
AND trust/revocation state current
AND policy epoch current
```

No reputation, provider branding, model family, or unrelated success substitutes for missing evidence.

---

## 34. Evidence Reuse Across Profile Change

Evidence reuse requires qualification-architecture compatibility/dependency reasoning.

At minimum verify:

- source and target profile digests;
- changed dimensions;
- preserved evidence classes;
- invalidated evidence classes;
- non-interference basis;
- unchanged capability/risk/assurance ceiling;
- current policy/epoch.

Compatibility may reduce new evaluation work but does not itself qualify the changed profile.

---

## 35. Drift Signals

Operational monitoring emits signed `DriftSignal` artifacts rather than rewriting earlier receipts.

```text
DriftSignal {
    signal_id
    subject_principal_id
    qualified_profile_digest
    monitoring_protocol_digest
    signal_class
    evidence_refs[]
    severity
    observed_at
    issuer
    signature
}
```

Qualification policy maps drift signals to monitoring, suspension, partial/full requalification, or revocation.

---

## 36. Privacy / Evidence Minimization

Portable receipts SHOULD expose immutable digests and required decision metadata rather than unnecessary raw sensitive data.

Raw prompts, private records, user data, or evaluator notes may remain access-controlled while their digests establish receipt integrity.

ATE does not require chain-of-thought disclosure as behavioral evidence.

---

## 37. Required Invariants

### E-I1 FROZEN_PROTOCOL
Protocol is frozen before formal registration/results.

### E-I2 PRECOMMITTED_RUN
Formal population/seed/sample/replication/roles/rules are committed before first subject invocation.

### E-I3 SUBJECT_PROFILE_BINDING
Evidence binds exact subject/profile or explicitly permitted profile class.

### E-I4 COMPLETE_ATTEMPT_ACCOUNTING
Every registered case/replication/retry has a terminal ledger state.

### E-I5 CAMPAIGN_HISTORY
Prior formal attempts remain auditable and cannot be hidden by a later favorable run.

### E-I6 NO_POST_HOC_SELECTION
Sampling, retries, stopping, evaluators, scoring, aggregation, and thresholds follow frozen rules.

### E-I7 AUTHORIZED_ROLES
Protocol authority, registration authority, runner, evaluator, evidence issuer, and independence claims satisfy policy.

### E-I8 EXACT_EVALUATOR_PROFILE
Behavioral observations bind the exact evaluator configuration/profile.

### E-I9 CLAIM_SCOPE_BOUNDING
Evidence cannot support scope/capability/risk/assurance beyond its declared/evaluated claim.

### E-I10 RECEIPT_SET_INTEGRITY
Aggregate results bind and recompute from the complete canonical underlying receipt set.

### E-I11 FAILURE_CLASS_SEPARATION
Subject, evaluator, runner, infrastructure, and protocol failures are distinguished and handled by frozen rules.

### E-I12 LIFECYCLE_BINDING
Freshness/refresh semantics are policy-defined and enforced.

### E-I13 CURRENT_TRUST_STATE
Revoked/suspended/incompatibly superseded evidence/current authorities fail according to authoritative trust-state policy without epoch rollback.

### E-I14 NONDETERMINISM_DECLARED
Stochastic replication rules are frozen before formal observation.

### E-I15 EVALUATOR_DISAGREEMENT_RULE
Required disagreement/adjudication semantics are predetermined.

### E-I16 HIDDENNESS_NOT_ASSUMED
Held-out/contamination-resistant claims require custody/exposure evidence.

### E-I17 EVIDENCE_NOT_QUALIFICATION
Evidence PASS does not itself qualify or authorize the subject.

### E-I18 ADMISSION_VERIFICATION
Qualification Authority verifies requirement, campaign, run, receipts, roles, scope, profile, lifecycle, and current state before package admission.

---

## 38. Relationship to Qualification

This architecture supplies trustworthy evidence objects to:

```text
Qualification Evidence Package
```

Qualification architecture remains authoritative for:

- qualification definition;
- evidence requirements;
- status/current use;
- scope/risk/assurance ceilings;
- compatibility/requalification decisions;
- qualification issuance.

---

## 39. Relationship to P2 and P1

The already-frozen P2 protocol remains unchanged.

Future composition:

```text
Behavioral / Functional Evidence
       |
       v
Qualification
       |
       v
Runtime Identity + Attestation
       |
       v
VerifiedRuntimeContext
       |
       v
Bounded Authorization
       |
       v
P1 Enforcement Plane
```

---

## 40. Architectural Decision

ATE adopts the following rule for qualification evidence:

> **A result is controlling evidence only when its requirement, protocol, formal-run population, attempts, runner, evaluator configuration, receipt set, aggregation, claim scope, lifecycle, and current trust state are all independently verifiable.**

A signed summary alone is insufficient.

---

## 41. Recommended Next Step

Perform a final consistency/adversarial review of v0.1.1 against:

- Qualification & Requalification Architecture v0.1.1;
- Revocation & Trust-State Model v0.1;
- Production Requirements & Conformance Profile v0.1;
- the frozen P2 boundary.

If accepted, design a lean deterministic local **Evidence Integrity Conformance Protocol** that tests the evidence machinery without requiring expensive live model evaluation.

---

## 42. Final Statement

The corrected evidence chain is:

```text
frozen requirement
    -> frozen protocol
    -> precommitted formal campaign/run
    -> complete attempt ledger
    -> runner completion attestation
    -> authenticated evaluator/test receipts
    -> deterministic aggregation
    -> bounded signed evidence receipt
    -> current trust-state verification
    -> qualification-package admission
```

This is how ATE converts "we tested the agent" into evidence that can survive adversarial scrutiny.
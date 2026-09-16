# ATE Behavioral & Functional Evidence Architecture v0.1

**Status:** Architecture candidate — DESIGN ONLY  
**Date:** 2026-09-16  
**Program:** Agent Trust Envelope (ATE)  
**Upstream dependency:** `ATE-AGENT-QUALIFICATION-REQUALIFICATION-ARCHITECTURE-v0.1.1.md`  
**Purpose:** Define how behavioral and functional evidence is produced, scoped, authenticated, evaluated, refreshed, and admitted into a Qualification Evidence Package.

---

## 1. Controlling Principle

> **Evidence is a bounded observation of demonstrated behavior or capability under a specific frozen evaluation protocol. It is not a general trust score, not qualification itself, and not authorization.**

Evidence answers:

```text
What was demonstrated,
by which exact subject/profile,
under which protocol and environment,
with which evaluator/runner authorities,
at what time,
with what result and uncertainty,
and for what claim scope?
```

Qualification separately decides whether the collection of required evidence is sufficient for admission to a bounded role.

Authorization separately decides whether a currently qualified runtime may perform a specific action now.

---

## 2. Evidence Chain

```text
Evidence Requirement
       |
       v
Frozen Evaluation Protocol
       |
       v
Evaluation Run Manifest
       |
       v
Subject Execution / Outputs
       |
       +--> deterministic functional checks
       |
       +--> behavioral observations
       |
       v
Evaluator / Scoring Process
       |
       v
Evaluation Result Receipt
       |
       v
Behavioral / Functional Evidence Receipt
       |
       v
Qualification Evidence Package
       |
       v
Qualification Decision
```

No stage implies the next without verification.

---

## 3. Evidence Classes

ATE distinguishes evidence by what it can legitimately claim.

### 3.1 Deterministic Functional Evidence

Used where outcome correctness can be evaluated mechanically.

Examples:

- protocol conformance;
- exact parser behavior;
- signature verification;
- access denial;
- bounded capability execution;
- deterministic transformation correctness;
- invariant preservation;
- test-suite pass/fail.

Preferred evaluation:

```text
machine-verifiable assertion
-> deterministic PASS / FAIL / ERROR
```

No model evaluator should be used when a deterministic oracle exists.

### 3.2 Sampled Behavioral Evidence

Used where behavior is stochastic, semantic, contextual, or quality-sensitive.

Examples:

- instruction following;
- refusal behavior;
- value-consistent decisions;
- factual discipline;
- non-deceptive reporting;
- handling of ambiguous situations;
- adherence to governance constraints across varied prompts/tasks.

Behavioral evidence is inherently scoped to the protocol, sample population, evaluator method, and acceptance rule used.

### 3.3 Operational Evidence

Evidence derived from real or staged operation after qualification.

Examples:

- audit-derived incident rates;
- policy-denial patterns;
- regression monitoring;
- post-deployment canary checks;
- anomaly signals.

Operational evidence may support continued qualification, suspension, or requalification decisions, but MUST NOT silently replace qualification-time evidence unless policy explicitly permits it.

### 3.4 Incident Evidence

Evidence generated from a specific failure, security event, policy violation, or integrity concern.

Incident evidence is primarily negative/current-state evidence. It may trigger:

```text
HEIGHTENED_MONITORING
SUSPEND
PARTIAL_REQUALIFICATION
FULL_REQUALIFICATION
REVOKE
```

It is not converted into a generic behavioral score.

---

## 4. Evidence Requirement Definition

Each required evidence class SHALL be defined by signed policy.

```text
EvidenceRequirement {
    evidence_requirement_id
    evidence_class_id
    evidence_type
    claim_scope
    subject_binding_requirements
    qualified_profile_constraints
    protocol_id
    accepted_protocol_versions[]
    minimum_sample_size?
    required_case_classes[]?
    required_replications?
    evaluator_rules
    runner_rules
    scoring_rule_id
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

The requirement defines what evidence is needed; it does not declare that the subject passed.

---

## 5. Claim Scope

Every evidence receipt SHALL explicitly state the claim it supports.

At minimum:

```text
claim_scope {
    capability_or_behavior_class
    task/domain constraints
    input/population constraints
    environment constraints
    tool/capability constraints
    governance constraints
    assurance/risk applicability
    exclusions/non_claims[]
}
```

A result MUST NOT be generalized beyond the declared claim scope merely because the subject name or model is the same.

Example:

```text
passed: bounded filesystem-write task suite under tool profile X
```

must not become:

```text
safe for arbitrary production shell execution
```

without additional evidence.

---

## 6. Frozen Evaluation Protocol

A controlling evaluation protocol is immutable and content-addressable before a formal run.

Minimum fields:

```text
EvaluationProtocol {
    protocol_id
    protocol_version
    evidence_class_id
    research/evaluation question
    subject/profile binding rules
    test corpus or generator specification
    case taxonomy
    inclusion/exclusion rules
    sampling rule
    randomization/seed rule
    execution environment requirements
    tool/capability profile
    evaluator method
    evaluator independence requirements
    scoring rubric / deterministic oracle
    aggregation rule
    acceptance rule
    invalid-run rules
    retry rules
    missing-output rules
    stopping rules
    evidence outputs required
    canonicalization/digest rules
    protocol_digest
}
```

A formal result is valid only against the exact frozen protocol digest.

---

## 7. Protocol Freeze Discipline

The protocol SHALL be frozen before the formal run begins.

After freeze, the following MUST NOT be changed to rescue a result:

- test cases or generator;
- sample size;
- evaluator identity requirements;
- rubric;
- acceptance threshold;
- weighting;
- invalid-case rules;
- retry policy;
- aggregation rule;
- stopping rule;
- claim scope.

If a genuine protocol defect is discovered, the run is invalidated or closed under the frozen rules and a new protocol version is created.

This prevents outcome-driven protocol mutation.

---

## 8. Evaluation Run Manifest

Each formal run has an immutable run manifest.

```text
EvaluationRunManifest {
    run_id
    protocol_digest
    subject_principal_id
    qualified_profile_digest
    runtime_instance_or_deployment_id?
    software_manifest_digest
    model_identity
    configuration_profile_digest
    tool_capability_profile_digest
    governance_digests
    execution_environment_digest
    evaluator identities
    runner identities
    corpus/generator digest
    selected_case_ids[] or generation seed
    sample_size_declared
    started_at
    implementation commit/build identifiers
    run_manifest_digest
}
```

The manifest binds the run to the exact subject/profile and evaluation context.

---

## 9. Complete-Run Accounting

ATE evidence MUST preserve the full declared run population, not only favorable outputs.

Every declared case SHALL end in one explicit terminal state:

```text
PASS
FAIL
VALID_SCORED
INVALID_PROTOCOL_DEFINED
ERROR
TIMEOUT
NOT_EXECUTED
```

The protocol defines which terminal states are acceptable for a valid run.

A result issuer MUST report at minimum:

```text
declared_cases
attempted_cases
valid_cases
invalid_cases
errors
timeouts
not_executed
passes
fails
```

Omission of unfavorable or failed cases invalidates the evidence unless omission is explicitly required by the frozen protocol.

---

## 10. Anti-Cherry-Picking Rule

The evidence issuer MUST NOT select the best outputs from multiple attempts unless the protocol explicitly defines such a selection mechanism before execution.

Examples prohibited by default:

- generate five answers and report the best one;
- rerun failed cases until they pass;
- discard evaluator disagreements after seeing scores;
- stop after a favorable prefix when full sample was preregistered;
- replace a weak evaluator with a favorable evaluator after results are known;
- silently exclude timeouts or malformed outputs.

If retries are permitted, the protocol MUST define:

```text
retry trigger
maximum retries
whether all attempts remain evidence
how retry results are aggregated
```

---

## 11. Functional Test Receipts

For deterministic functional evidence, each test receipt SHOULD contain:

```text
FunctionalTestReceipt {
    test_receipt_id
    run_id
    protocol_digest
    test_case_id
    subject_principal_id
    qualified_profile_digest
    input_digest
    expected_outcome_digest / oracle_id
    observed_outcome_digest
    result = PASS | FAIL | ERROR
    reason_code
    started_at
    completed_at
    runner_id
    verifier/oracle_version
    receipt_digest
}
```

The aggregate evidence receipt references every controlling test receipt.

---

## 12. Behavioral Observation Receipts

For sampled behavioral evidence, each observation SHOULD bind:

```text
BehavioralObservationReceipt {
    observation_id
    run_id
    protocol_digest
    case_id
    subject_principal_id
    qualified_profile_digest
    prompt/task/input_digest
    output_digest
    relevant context/tool trace digests
    evaluator_id
    evaluator_role
    rubric_digest
    score_vector or categorical outcome
    reason_codes[]
    validity = VALID | INVALID
    invalid_reason?
    evaluated_at
    evaluator_signature
}
```

The underlying artifact may be stored separately, but the receipt must make substitution detectable.

---

## 13. Evaluator Authority

An evaluator's signature proves who evaluated; it does not prove that evaluator was authorized for the evidence class.

Evaluator policy SHALL define:

```text
accepted_evaluator_authorities[]
evaluator_role
independence_class
self_evaluation_allowed
minimum_evaluator_count
replication_required
conflict_of_interest constraints
accepted_evaluator_versions/models?
```

For high-impact qualification, policy SHOULD avoid making the subject's own self-assessment the sole controlling behavioral evidence.

---

## 14. Runner Authority

Execution provenance matters independently from evaluation.

The runner is responsible for attesting that:

- the frozen protocol was executed;
- the declared subject/profile was actually invoked;
- the case set/generator was the declared one;
- environment/tool constraints matched the manifest;
- all attempts and terminal states were recorded.

A runner MAY also be an evaluator only when policy explicitly permits role combination.

---

## 15. Evaluator Independence Classes

ATE defines conceptual independence levels:

```text
E0_SELF              subject/runtime evaluates itself
E1_SAME_OPERATOR     separate evaluator controlled by same operator
E2_INDEPENDENT_ROLE  separate evaluator authority/process
E3_INDEPENDENT_ORG   administratively independent evaluator
```

These are evidence metadata, not universal quality rankings.

Qualification policy selects the required independence class according to risk.

No evidence system may silently claim E2/E3 from merely using a different model name or process.

---

## 16. Rubric and Scoring Integrity

Behavioral scoring MUST bind to a frozen rubric or deterministic decision procedure.

Rubric object:

```text
EvaluationRubric {
    rubric_id
    rubric_version
    dimensions[]
    scale semantics
    pass/fail mapping
    weighting
    ambiguity rules
    missing-information rules
    evaluator instructions
    rubric_digest
}
```

A score without the rubric digest is insufficient controlling evidence.

---

## 17. Aggregation Rule

Aggregate behavioral evidence SHALL use a frozen aggregation function.

Examples:

- all mandatory safety cases must PASS;
- mean score >= threshold with no critical failure;
- N-of-M categorical success;
- exact failure-rate ceiling;
- paired evaluator agreement rule.

The aggregation rule SHALL define how to handle:

- invalid cases;
- evaluator disagreement;
- missing scores;
- ties;
- critical-case overrides;
- partial completion.

No post-hoc averaging or threshold adjustment is permitted.

---

## 18. Acceptance Rule

The protocol SHALL declare exactly what constitutes:

```text
EVIDENCE_PASS
EVIDENCE_FAIL
EVIDENCE_INCONCLUSIVE
INVALID_RUN
```

An evidence result is not automatically a qualification decision.

Example:

```text
EVIDENCE_PASS
    -> may satisfy one required evidence class
    -> Qualification Authority still evaluates all other requirements
```

---

## 19. Behavioral Evidence Receipt

A final receipt for one evidence requirement SHOULD contain:

```text
BehavioralEvidenceReceipt {
    evidence_receipt_id
    evidence_requirement_id
    evidence_class_id
    claim_scope_digest
    subject_principal_id
    qualified_profile_digest
    protocol_digest
    run_manifest_digest
    corpus_or_generator_digest
    execution_environment_digest
    evaluator_rule_digest
    rubric_digest
    aggregation_rule_digest
    acceptance_rule_digest
    declared_sample_size
    valid_sample_size
    result
    summary_metrics
    critical_failures[]
    receipt_set_digest
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

The receipt is public verifiable evidence, not a bearer capability.

---

## 20. Functional Evidence Receipt

Deterministic evidence may use a simplified receipt:

```text
FunctionalEvidenceReceipt {
    evidence_receipt_id
    evidence_requirement_id
    evidence_class_id
    claim_scope_digest
    subject_principal_id
    qualified_profile_digest
    protocol_digest
    run_manifest_digest
    test_receipt_set_digest
    controlling_test_count
    pass_count
    fail_count
    error_count
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

Where all tests are deterministic, detailed semantic evaluator metadata is unnecessary.

---

## 21. Evidence Issuer Authority

The Evidence Issuer attests that a result package conforms to the frozen protocol and reported receipts.

Issuer authority SHALL define ceilings such as:

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

A cryptographically valid receipt issued beyond these ceilings is invalid.

The Evidence Issuer MUST NOT upgrade an evaluation's scope or assurance beyond what the underlying protocol/run supports.

---

## 22. Evidence Lifecycle Semantics

Evidence SHALL use the lifecycle classes already defined by qualification architecture:

```text
ISSUANCE_SNAPSHOT
CONTINUOUSLY_CURRENT
PERIODICALLY_REFRESHED
```

### ISSUANCE_SNAPSHOT

A historical completed test may remain valid evidence for the original immutable profile even after time passes, subject to supersession/incident policy.

### CONTINUOUSLY_CURRENT

Evidence must remain current. Expiry/revocation makes dependent qualification unusable.

### PERIODICALLY_REFRESHED

Evidence has a refresh deadline. Missing refresh transitions qualification according to policy.

Lifecycle class is set by the Evidence Requirement, not chosen by the subject after seeing results.

---

## 23. Evidence Freshness

Freshness MUST be interpreted according to evidence class.

For sampled behavioral evidence, freshness policy may depend on:

- model/provider/runtime changes;
- configuration drift;
- tool/capability changes;
- governance changes;
- elapsed time;
- incident history;
- risk class.

A fresh timestamp alone does not make stale-profile evidence applicable.

---

## 24. Profile Binding

Evidence binds to `qualified_profile_digest` or an explicitly declared principal/profile class allowed by protocol.

A change in a material profile dimension may invalidate evidence even if the principal name is unchanged.

Material dimensions include, as applicable:

- model/version/weights;
- system/policy configuration;
- tool permissions;
- resource permissions;
- network access;
- software implementation;
- CoA/VA/policy bundle;
- key-protection/assurance mode.

Evidence reuse across changed profiles requires a signed compatibility/dependency decision under the qualification architecture.

---

## 25. Sample/Population Binding

Behavioral evidence SHALL describe the sampled population or generator sufficiently to bound interpretation.

At minimum, record:

```text
corpus_id or generator_id
corpus/generator version
digest
case taxonomy
sampling method
seed/randomization rule
sample size
coverage requirements
known exclusions
```

ATE MUST NOT infer population-wide guarantees from a small sample beyond the claim permitted by the protocol.

---

## 26. Non-Deterministic Subjects

For stochastic models/agents, evidence policy SHALL declare whether repeated sampling is required.

Possible protocol choices:

```text
single-shot per case
fixed N replications per case
session-block replication
multiple independent reconstruction/deployment runs
```

The choice must be frozen before observation of formal results.

No extra replication may be added only because the initial result is unfavorable unless the protocol's stopping rule already permits it.

---

## 27. Evaluator Disagreement

If multiple evaluators are required, the protocol SHALL define disagreement semantics in advance.

Options include:

- unanimity required;
- majority rule;
- conservative/worst-case rule;
- adjudicator selected before run;
- disagreement -> INCONCLUSIVE.

Post-hoc evaluator replacement or selective retention is prohibited.

---

## 28. Evaluation Errors and Infrastructure Failures

An evaluation infrastructure error is not automatically evidence that the subject passed or failed.

The protocol SHALL distinguish:

```text
SUBJECT_FAILURE
EVALUATOR_FAILURE
RUNNER_FAILURE
INFRASTRUCTURE_FAILURE
PROTOCOL_INVALIDITY
```

Retry policy must specify which failure classes may be retried and whether prior attempts remain part of the evidence record.

---

## 29. Hidden / Contamination-Sensitive Evaluation

Where test leakage or memorization would materially weaken evidence, the protocol MAY require:

- hidden cases;
- rotating held-out corpus;
- case generation after subject freeze;
- restricted evaluator prompts/rubrics;
- contamination declarations.

Hidden evidence is not mandatory for every evidence class.

The required secrecy model must be explicit rather than assumed.

---

## 30. Data and Privacy

Evidence receipts SHOULD carry digests/references rather than unnecessary raw sensitive data.

Qualification verification may need to know:

- that required evidence exists;
- who issued/evaluated it;
- its protocol/result/scope/freshness;
- immutable digests.

It does not necessarily need full prompts, private records, or chain-of-thought-like internal material.

Sensitive raw evidence may be retained under controlled access while the signed receipt remains portable.

---

## 31. Evidence Revocation

Evidence can be revoked independently from qualification.

Reasons include:

- protocol defect discovered;
- evaluator compromise;
- runner compromise;
- corpus corruption;
- evidence fabrication;
- subject/profile misbinding;
- scoring implementation defect;
- data leakage invalidating a hidden evaluation;
- issuer compromise.

Revoked controlling evidence SHALL trigger qualification status handling according to the qualification lifecycle policy.

---

## 32. Evidence Supersession

New evidence does not silently erase old evidence.

A superseding receipt records lineage:

```text
prior_evidence_receipt_id
superseding_evidence_receipt_id
reason
preserved_claim_scope?
changed_protocol?
changed_profile?
issued_at
```

Historical evidence remains auditable even when no longer current for qualification.

---

## 33. Qualification Evidence Package Admission

An evidence receipt may enter a Qualification Evidence Package only if the Qualification Authority verifies:

```text
requirement_id matches active Qualification Definition
AND evidence issuer authorized for class/scope
AND protocol version/digest accepted
AND subject/profile binding matches
AND claim scope covers requirement without expansion
AND evaluator/runner rules satisfied
AND lifecycle/freshness satisfied
AND receipt/result integrity valid
AND complete-run accounting valid
AND receipt not revoked/suspended/superseded incompatibly
AND current policy epoch permits use
```

The Qualification Authority MUST NOT infer missing evidence from reputation, provider branding, model family, or prior unrelated success.

---

## 34. Evidence Dependency Graph

Qualification should make dependencies explicit.

```text
Qualification Requirement R1
    |
    +--> Evidence Receipt E1
    |       +--> Protocol P1
    |       +--> Run Manifest M1
    |       +--> Test/Observation Receipt Set S1
    |
    +--> Evidence Receipt E2
            +--> Protocol P2
            +--> Run Manifest M2
            +--> Evaluator Receipt Set S2
```

This graph supports targeted partial requalification when one evidence class becomes stale or invalid.

---

## 35. Evidence Reuse

Evidence reuse is permitted only when all of the following are explicitly satisfied:

- same or compatible subject/profile binding;
- same evidence requirement or signed compatibility mapping;
- claim scope still sufficient;
- lifecycle/freshness valid;
- evaluator/runner authority still acceptable;
- protocol remains accepted;
- no revocation/supersession blocks use;
- no policy epoch rollback.

Evidence is never reused merely because rerunning it is expensive.

---

## 36. Behavioral Drift Monitoring

Operational/drift evidence may update current trust state without rewriting qualification history.

A drift monitor SHOULD emit signed `DriftSignal` artifacts:

```text
DriftSignal {
    signal_id
    subject_principal_id
    qualified_profile_digest
    signal_class
    evidence_refs[]
    severity
    observed_at
    monitoring_protocol_digest
    issuer
    signature
}
```

Policy, not the monitor itself, maps the signal to qualification consequences.

---

## 37. Human and Model Evaluators

ATE is evaluator-technology neutral.

An evaluator may be:

- deterministic software;
- human reviewer;
- AI model;
- committee/quorum;
- hybrid process.

The evidence must disclose the evaluator authority/type/version needed by policy.

Using an AI evaluator does not automatically provide independence from the subject.

Using a human evaluator does not automatically provide correctness.

The trust claim comes from the declared evaluation architecture and evidence, not evaluator category mythology.

---

## 38. Evidence Confidence vs Qualification Decision

ATE SHOULD avoid collapsing evidence into one global numeric trust score.

If a protocol produces confidence intervals, uncertainty measures, or scores, preserve them as evidence metadata.

Qualification policy then applies explicit decision rules.

Example:

```text
Evidence A: deterministic conformance = PASS
Evidence B: safety-behavior rate = 98.7% under protocol X
Evidence C: governance-adherence critical cases = 20/20 PASS

Qualification rule:
    A PASS
    AND B >= frozen threshold
    AND C = 20/20
```

The result is a bounded qualification decision, not a universal 98.7% trust score.

---

## 39. Evidence Portability

Portable evidence SHALL declare its trust domain and allowed portability scope.

Cross-project/cross-domain use requires verifier policy that explicitly accepts:

- issuer;
- protocol;
- evaluator authority;
- subject/profile mapping;
- claim scope;
- lifecycle;
- governance compatibility.

No implicit portability.

---

## 40. Failure-Closed Rules

Evidence verification fails closed for at least:

- unknown protocol version;
- missing protocol digest;
- bad signature;
- unauthorized evidence issuer;
- unauthorized evaluator/runner;
- subject/profile mismatch;
- incomplete run manifest;
- undeclared missing cases;
- invalid sample accounting;
- rubric/aggregation mismatch;
- acceptance rule mismatch;
- expired or stale current evidence;
- revoked receipt;
- policy epoch rollback;
- unsupported claim-scope expansion;
- mixed receipts from incompatible runs when protocol forbids mixing.

---

## 41. Required Invariants

### E-I1 — FROZEN_PROTOCOL
Controlling protocol is fixed before formal results are observed.

### E-I2 — SUBJECT_PROFILE_BINDING
Every controlling evidence receipt binds the subject and qualified profile or an explicitly permitted profile class.

### E-I3 — COMPLETE_RUN_ACCOUNTING
All declared formal cases/attempts terminate in recorded protocol-defined states; unfavorable results cannot disappear.

### E-I4 — NO_POST_HOC_SELECTION
Retries, stopping, evaluators, scoring, aggregation, and thresholds follow frozen rules.

### E-I5 — AUTHORIZED_EVALUATION_ROLES
Runner, evaluator, evidence issuer, and protocol authority satisfy role/independence policy.

### E-I6 — CLAIM_SCOPE_BOUNDING
Evidence supports only the declared claim scope and cannot be inflated during qualification.

### E-I7 — EVALUATION_INTEGRITY
Inputs, outputs, traces, scores, and result receipts are content-bound and tamper-evident.

### E-I8 — LIFECYCLE_BINDING
Freshness/refresh semantics are declared by policy and enforced.

### E-I9 — CURRENT_TRUST_STATE
Revoked/suspended/incompatibly superseded evidence cannot satisfy new qualification decisions.

### E-I10 — EVIDENCE_NOT_QUALIFICATION
An evidence PASS alone does not grant qualification or action authority.

### E-I11 — DETERMINISTIC_WHEN_POSSIBLE
Machine-verifiable claims use deterministic oracles rather than discretionary scoring when practical.

### E-I12 — NONDETERMINISM_DECLARED
Stochastic sampling/replication rules are frozen before formal observation.

### E-I13 — EVALUATOR_DISAGREEMENT_RULE
Required multi-evaluator disagreement handling is predetermined.

### E-I14 — PROFILE_CHANGE_REQUIRES_COMPATIBILITY
Evidence reuse across material profile change requires signed compatibility/dependency reasoning.

### E-I15 — ADMISSION_VERIFICATION
Qualification Authority verifies evidence requirement, scope, issuer, protocol, profile, lifecycle, and trust state before package admission.

---

## 42. Relationship to Qualification Architecture

This architecture fills the `Evaluation / Evidence Package` stage:

```text
Qualification Definition
       |
       v
Evidence Requirements
       |
       v
THIS ARCHITECTURE
protocol -> run -> receipts -> evidence
       |
       v
Qualification Evidence Package
       |
       v
Qualification Decision
```

Qualification architecture remains authoritative for:

- qualification scope;
- status;
- requalification triggers;
- compatibility decisions;
- credential issuance;
- risk/assurance ceilings.

---

## 43. Relationship to P2 Runtime Trust

P2 verifies runtime identity/provenance and consumes a simplified qualification fixture.

This architecture does not modify the frozen P2 protocol.

Future composition is:

```text
Behavioral / Functional Evidence
       |
       v
Qualification
       |
       v
P2-style Runtime Trust Establishment
       |
       v
VerifiedRuntimeContext
       |
       v
Action Authorization
       |
       v
P1 Enforcement
```

---

## 44. Relationship to Value Architecture

Value Architecture may define evidence requirements for claims such as governance adherence, honesty, bounded agency, or escalation behavior.

However:

> Signing or naming a Value Architecture does not prove behavioral adherence to it.

Evidence protocols must operationalize observable claims that can be tested.

VA supplies normative expectations; evidence supplies observations about whether a specific qualified profile demonstrated required behavior under declared conditions.

---

## 45. Relationship to Condition of Agency

Condition of Agency acceptance is governance evidence.

Behavioral evaluation may additionally test whether a subject follows CoA-derived constraints in representative situations.

These are distinct:

```text
accepted CoA
    !=
demonstrated adherence to CoA-derived behavior
```

Qualification policy may require both.

---

## 46. Production Maturity Path

A practical progression is:

### Level E0 — Deterministic local evidence
- fixed fixtures;
- machine oracles;
- local signed receipts.

### Level E1 — Controlled behavioral evidence
- frozen corpus/generator;
- declared evaluator;
- complete-run accounting;
- signed result receipts.

### Level E2 — Independent/replicated behavioral evidence
- evaluator separation;
- blinded/held-out cases as required;
- replication rules;
- stronger evidence custody.

### Level E3 — Production continuous evidence
- operational telemetry;
- drift monitoring;
- independent audit/evidence sink;
- periodic refresh/requalification triggers.

These levels describe evidence maturity, not general agent trustworthiness.

---

## 47. Recommended Next Step

Before freezing a behavioral-evidence conformance protocol, perform:

**ATE Behavioral & Functional Evidence Adversarial Review v0.1**

The review should attack at minimum:

- cherry-picking;
- selective retry;
- evaluator capture;
- runner/evaluator role confusion;
- protocol mutation after results;
- hidden failure omission;
- profile misbinding;
- scope inflation;
- stale evidence reuse;
- evaluator disagreement handling;
- stochastic replication ambiguity;
- evidence receipt forgery/substitution;
- corpus leakage/contamination assumptions;
- cross-project reuse;
- revoked evaluator/evidence issuer;
- evidence-to-qualification overreach.

No live model experiment is required for this review.

---

## 48. Final Statement

ATE qualification needs evidence that is reproducible enough to audit, scoped enough to interpret, and rigid enough that unfavorable results cannot be edited out of the story.

The governing chain is:

```text
frozen requirement
    -> frozen protocol
    -> complete run
    -> authenticated observations
    -> authorized evaluation
    -> bounded evidence receipt
    -> verified qualification-package admission
```

That chain turns "the agent seemed good in testing" into a verifiable engineering claim.
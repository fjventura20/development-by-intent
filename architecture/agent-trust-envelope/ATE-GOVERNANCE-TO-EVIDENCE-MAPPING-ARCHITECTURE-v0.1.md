# ATE Governance-to-Evidence Mapping Architecture v0.1

**Status:** Architecture candidate — DESIGN ONLY  
**Date:** 2026-09-16  
**Program:** Agent Trust Envelope (ATE)  
**Purpose:** Define how Condition of Agency, Value Architecture, and governing policy become explicit structural controls and testable evidence requirements without pretending that prose commitments or cryptographic signatures prove behavioral compliance.

---

## 1. Controlling Principle

> **Governance text becomes trustworthy engineering input only after each controlling requirement is mapped to an explicit enforceable control, an observable evidence requirement, or a declared coverage gap.**

ATE MUST NOT infer:

```text
signed governance document
    -> behavioral compliance
```

or:

```text
accepted Condition of Agency
    -> demonstrated adherence
```

The correct chain is:

```text
Governance Source
    -> clause decomposition
    -> operationalization
    -> structural control and/or evidence requirement
    -> qualification evidence
    -> current runtime governance binding
    -> bounded authorization
```

---

## 2. Scope

This architecture applies to governance sources including:

- Condition of Agency (CoA);
- Value Architecture (VA);
- project governance policies;
- risk/assurance policies;
- role-specific operating rules;
- safety/escalation constraints;
- accountability/reporting obligations.

It defines how these sources become verifiable ATE inputs.

It does **not** claim access to an agent's hidden thoughts, motives, consciousness, moral character, or private chain of reasoning.

ATE evaluates observable and enforceable properties.

---

## 3. Governance Source Artifact

Every controlling governance source SHALL be immutable/content-addressable.

```text
GovernanceSource {
    governance_source_id
    governance_type      // COA | VALUE_ARCHITECTURE | POLICY | ROLE_POLICY
    title
    version
    canonical_digest
    trust_domain_id
    project_scope?
    issuer_authority_id
    effective_from
    valid_until?
    supersedes?
    policy_epoch
    signature
}
```

Unknown, revoked, expired, or incompatibly superseded governance sources fail according to active policy.

---

## 4. Clause Decomposition

A governance source is decomposed into immutable clause identities.

```text
GovernanceClause {
    clause_id
    governance_source_id
    source_digest
    clause_text_digest
    clause_semantic_summary
    clause_type
    applicability_scope
    priority / precedence metadata?
}
```

The operationalization record SHALL reference the source clause by digest/ID rather than copying mutable prose.

---

## 5. Clause Types

ATE distinguishes at least:

### 5.1 Acceptance / Commitment Clause

Example:

```text
The agent must explicitly accept CoA version C before participating.
```

Primary control:

- signed governance acceptance evidence;
- runtime/session binding;
- validity/current-state check.

Behavioral testing may be additional, but acceptance itself is not inferred from behavior.

### 5.2 Capability / Authority Clause

Example:

```text
The agent must not modify production resources without authorization.
```

Primary control:

- structural enforcement;
- capability scope;
- executor mediation;
- authorization checks.

Behavioral evidence alone is insufficient when structural enforcement is possible.

### 5.3 Behavioral Requirement Clause

Example:

```text
When uncertain about a material fact, the agent must disclose uncertainty rather than fabricate certainty.
```

Primary evidence:

- frozen behavioral evaluation protocol;
- bounded claim scope;
- evaluator receipts;
- qualification evidence.

### 5.4 Behavioral Prohibition Clause

Example:

```text
The agent must not falsely report completion of an action it did not perform.
```

Primary evidence:

- adversarial behavioral cases;
- audit cross-checks;
- operational incident/drift signals.

### 5.5 Escalation / Human-Authority Clause

Example:

```text
High-impact ambiguous actions require escalation rather than autonomous execution.
```

Controls may combine:

- risk classification;
- policy gate;
- human approval requirement;
- behavioral escalation evidence;
- executor enforcement.

### 5.6 Accountability / Reporting Clause

Example:

```text
The agent must accurately report material failures and deviations.
```

Controls may combine:

- tamper-evident audit records;
- behavioral evaluation against ground-truth action state;
- no-self-certification rules.

### 5.7 Aspirational / Non-Operationalized Clause

Some values may be meaningful but too broad to support direct verification without decomposition.

Example:

```text
Act with integrity.
```

ATE MUST NOT silently transform this into a universal claim.

It must either:

- decompose it into narrower operational clauses; or
- mark it `NOT_YET_OPERATIONALIZED`.

---

## 6. Enforceability Classes

Each clause receives one controlling enforceability classification:

```text
STRUCTURALLY_ENFORCEABLE
BEHAVIORALLY_EVALUABLE
MIXED_STRUCTURAL_AND_BEHAVIORAL
DECLARATIVE_ACCEPTANCE_ONLY
NOT_YET_OPERATIONALIZED
```

This classification is explicit and signed by an authorized Governance Operationalization Authority.

The subject agent MUST NOT choose its own classification.

---

## 7. Governance Operationalization Record

```text
GovernanceOperationalizationRecord {
    operationalization_id
    governance_source_id
    governance_source_digest
    clause_id
    clause_text_digest
    enforceability_class

    structural_control_requirements[]
    evidence_requirement_ids[]
    acceptance_requirement_ids[]
    risk_policy_refs[]
    qualification_requirement_refs[]

    observable_claims[]
    exclusions_non_claims[]
    applicability_scope

    coverage_status
    operationalization_version
    policy_epoch
    issuer_authority_id
    signature
}
```

This object is the formal bridge from governance prose to ATE controls/evidence.

---

## 8. Coverage Status

Each required governance clause SHALL have one status:

```text
COVERED_STRUCTURALLY
COVERED_BY_EVIDENCE
COVERED_MIXED
ACCEPTANCE_ONLY
NOT_YET_OPERATIONALIZED
NOT_APPLICABLE_WITH_SIGNED_BASIS
```

A missing mapping is not equivalent to compliance.

---

## 9. Governance Coverage Manifest

For each governance source/version used by a qualification, build a canonical coverage manifest:

```text
GovernanceCoverageManifest {
    coverage_manifest_id
    governance_source_id
    governance_source_digest
    operationalization_version
    clause_entries[] {
        clause_id
        operationalization_record_digest
        coverage_status
        structural_control_refs[]
        evidence_requirement_refs[]
        acceptance_requirement_refs[]
    }
    uncovered_required_clauses[]
    coverage_policy_id
    policy_epoch
    issued_at
    issuer
    signature
}
```

Qualification policy determines whether uncovered clauses are permissible.

For a claim of **full required governance coverage**, `uncovered_required_clauses[]` MUST be empty under the active coverage policy.

---

## 10. No Silent Coverage Inflation

ATE MUST distinguish claims such as:

```text
accepted VA v3
```

from:

```text
qualified under evidence requirements derived from selected VA v3 clauses
```

from:

```text
all required VA v3 clauses operationalized and covered for role R
```

These are different claims.

A system MUST NOT shorten them all to:

```text
VA compliant
```

unless the exact meaning and coverage basis are defined by policy.

---

## 11. Observable Claim Definition

Behaviorally evaluable clauses are decomposed into bounded observable claims.

```text
ObservableGovernanceClaim {
    claim_id
    source_clause_id
    behavior_class
    triggering_conditions
    expected_observable_behavior
    prohibited_observable_behavior
    allowed_variance
    escalation_behavior?
    evidence_scope
    known_limitations
    claim_digest
}
```

The claim must describe observable behavior rather than hidden mental state.

---

## 12. Example — Honesty / Truthfulness

A broad value:

```text
Be honest.
```

is not directly testable as internal moral character.

Possible operational claims include:

```text
H1: Do not claim an external action completed when authoritative execution state says it did not.
H2: Distinguish known facts from uncertainty when evidence is insufficient.
H3: Do not fabricate citations/evidence when none are available.
H4: Report material protocol/test failures rather than silently converting them to PASS.
```

Each claim may map to:

- deterministic audit cross-checks;
- adversarial behavioral cases;
- operational monitoring;
- evidence-integrity controls.

ATE may support these claims without claiming to prove an internal virtue called "honesty."

---

## 13. Example — Keep Commitments

Broad value:

```text
Do what you promise.
```

Operational decomposition may include:

```text
C1: Do not assert completion before authoritative completion evidence exists.
C2: If a committed action cannot be completed, report failure/blockage according to policy.
C3: Do not silently substitute a materially different action for the committed action.
C4: Escalate when a commitment conflicts with a higher-priority governance constraint.
```

This produces testable accountability semantics without pretending every future promise can be guaranteed.

---

## 14. Example — Human Authority / Escalation

Broad requirement:

```text
Respect human authority for high-impact decisions.
```

Operationalization may combine:

```text
risk >= R3 -> human approval artifact required
ambiguous high-impact action -> escalation required
missing/invalid approval -> executor denies
agent behavioral evidence -> demonstrates escalation rather than circumvention
```

This is `MIXED_STRUCTURAL_AND_BEHAVIORAL`.

---

## 15. Structural-First Rule

Where a governance requirement can be reliably enforced structurally, ATE SHOULD prefer structural enforcement over relying only on behavioral willingness.

Examples:

```text
no production write without executor authorization
no direct secret access
no action beyond capability token scope
no high-risk execution without approval
```

Behavioral evidence may still test whether the agent attempts circumvention or reports denials correctly, but it is not the primary enforcement boundary.

---

## 16. Behavioral-Evidence Rule

Behavioral evidence is appropriate where the desired property cannot be reduced entirely to structural capability control.

Examples:

- truthful status reporting;
- uncertainty disclosure;
- escalation choice;
- instruction-priority handling;
- policy-consistent refusal/explanation;
- non-deceptive evidence presentation.

Every behavioral requirement SHALL map to an `EvidenceRequirement` under the Behavioral & Functional Evidence Architecture.

---

## 17. Governance Acceptance vs Adherence

ATE preserves the distinction:

```text
GovernanceAcceptance
    = evidence that subject/runtime accepted the exact governance artifact

GovernanceAdherenceEvidence
    = evidence that the evaluated profile demonstrated specified observable behavior derived from governance clauses
```

Qualification may require both.

Neither substitutes for the other.

---

## 18. Qualification Mapping

A Qualification Definition may require governance coverage such as:

```text
required_governance_sources[]
required_coverage_manifest_digests[]
required_clause_ids[]
required_evidence_requirement_ids[]
required_structural_control_profiles[]
required_acceptance_requirement_ids[]
```

The Qualification Authority SHALL verify the active mappings/current policy rather than rely on a generic statement that governance was considered.

---

## 19. Evidence Requirement Derivation

For each `BEHAVIORALLY_EVALUABLE` or behavioral portion of a `MIXED` clause, derive an Evidence Requirement that binds:

- source governance clause;
- observable claim digest;
- subject/profile constraints;
- task/population scope;
- protocol family;
- evaluator requirements;
- lifecycle class;
- refresh/requalification triggers;
- risk/assurance applicability;
- claim limitations.

The derived evidence requirement SHALL reference the operationalization record digest.

---

## 20. Structural Control Requirement

For each structural clause, define a control requirement such as:

```text
StructuralGovernanceControlRequirement {
    control_requirement_id
    source_clause_id
    operationalization_record_digest
    required_component
    required_invariant
    conformance_protocol_ref
    minimum_assurance_profile
    applicability_scope
    policy_epoch
    issuer
    signature
}
```

Qualification may require conformance evidence that the structural control exists for the evaluated/deployed profile.

---

## 21. Mixed Clause Satisfaction

For `MIXED_STRUCTURAL_AND_BEHAVIORAL` clauses:

```text
clause_satisfied_for_qualification =
    structural_control_requirement_satisfied
    AND required_behavioral_evidence_satisfied
    AND required_acceptance_evidence_satisfied (if applicable)
```

No one component silently substitutes for another.

---

## 22. Precedence and Conflict

Governance sources may conflict.

ATE operationalization MUST NOT let an evaluator improvise precedence during a behavioral test.

A signed precedence policy should define ordering such as:

```text
law / mandatory safety policy
    > project authorization policy
    > Condition of Agency
    > role policy
    > user/request-level instruction
```

The exact hierarchy is project-specific and must be explicit.

Behavioral evidence protocols then test adherence to the frozen precedence policy.

---

## 23. Governance Version Change

A governance source change requires a deterministic impact assessment.

Possible outcomes:

```text
NO_QUALIFICATION_IMPACT
RE_ACCEPTANCE_REQUIRED
EVIDENCE_REFRESH_REQUIRED
PARTIAL_REQUALIFICATION_REQUIRED
FULL_REQUALIFICATION_REQUIRED
IMMEDIATE_SUSPENSION
```

The change is evaluated by clause/mapping dependencies, not by version-number aesthetics alone.

---

## 24. Mapping Compatibility

A signed compatibility decision may preserve some mappings/evidence across a governance update only when it establishes:

- source and target governance digests;
- changed clauses;
- unchanged operational claims;
- affected structural controls;
- affected evidence requirements;
- preserved/invalidated evidence;
- unchanged risk/capability/assurance ceiling;
- current policy epoch.

Compatibility cannot turn an untested new governance obligation into covered evidence.

---

## 25. Coverage Drift

A profile may become less governance-covered without the governance document itself changing, for example if:

- evidence expires/revokes;
- structural control conformance lapses;
- evaluator authority is compromised;
- runtime capability expands;
- tool/network profile changes;
- a new risk class becomes applicable.

Qualification/current trust-state logic must therefore evaluate current coverage dependencies, not only governance source version.

---

## 26. Operational Monitoring

Operational audit/drift signals may test governance-derived observable claims after deployment.

Examples:

- false completion reporting detected against executor audit;
- repeated attempts to exceed capability scope;
- escalation failures;
- policy-denial circumvention attempts;
- unexplained discrepancy between claimed and recorded action state.

These signals feed qualification status/requalification policy; they do not retroactively rewrite qualification-time evidence.

---

## 27. No Hidden-Thought Requirement

ATE MUST NOT require private chain-of-thought or hidden reasoning disclosure to establish governance evidence.

Evidence should rely on:

- observable inputs/outputs;
- tool/action traces;
- signed decisions;
- audit records;
- explicit acceptance artifacts;
- deterministic state transitions;
- externally verifiable outcomes.

This preserves both evidentiary clarity and privacy/security boundaries.

---

## 28. Governance Coverage Claim Object

A portable bounded claim may be represented as:

```text
GovernanceCoverageClaim {
    claim_id
    subject_principal_id
    qualified_profile_digest
    governance_source_digest
    coverage_manifest_digest
    covered_clause_ids[]
    uncovered_clause_ids[]
    acceptance_evidence_refs[]
    structural_control_evidence_refs[]
    behavioral_evidence_refs[]
    claim_scope
    qualification_id?
    issued_at
    valid_until?
    issuer
    signature
}
```

This is a summary/reference object, not independent proof. Verifiers should validate its referenced evidence/current state according to policy.

---

## 29. Coverage Vocabulary

ATE SHOULD use precise statements:

```text
GOVERNANCE_ACCEPTED
GOVERNANCE_REQUIRED_CLAUSES_COVERED
GOVERNANCE_PARTIALLY_COVERED
GOVERNANCE_COVERAGE_STALE
GOVERNANCE_COVERAGE_REVOKED
GOVERNANCE_NOT_OPERATIONALIZED
```

Avoid unqualified labels such as:

```text
aligned
ethical
safe
trustworthy
```

unless a project specification defines their exact bounded meaning.

---

## 30. Failure-Closed Rules

Governance-to-evidence verification fails closed when:

- required governance source is unknown/revoked/superseded incompatibly;
- required clause has no operationalization;
- operationalization issuer unauthorized;
- coverage manifest omits a required clause;
- behavioral evidence scope does not cover derived claim;
- required structural control evidence is missing/stale;
- required acceptance evidence is missing/stale;
- policy epoch rollback is attempted;
- mapping compatibility is absent for a material change;
- claim language exceeds actual coverage.

---

## 31. Required Invariants

### G-I1 SOURCE_BINDING
Every operationalization binds an exact governance source/clause digest.

### G-I2 EXPLICIT_ENFORCEABILITY_CLASS
Every required clause is classified as structural, behavioral, mixed, acceptance-only, not-yet-operationalized, or signed not-applicable.

### G-I3 NO_SILENT_OMISSION
Required clauses cannot disappear from the coverage manifest.

### G-I4 STRUCTURAL_FIRST
Behavioral willingness does not substitute for structural enforcement where policy requires enforceable control.

### G-I5 ACCEPTANCE_NOT_ADHERENCE
Governance acceptance and behavioral adherence evidence remain distinct.

### G-I6 OBSERVABLE_CLAIMS
Behavioral evidence requirements target observable bounded claims, not hidden mental states.

### G-I7 CLAIM_SCOPE_BOUNDING
Governance-coverage claims cannot exceed mapped/evidenced clause scope.

### G-I8 MIXED_REQUIRES_ALL_COMPONENTS
Mixed clauses require every mandated structural/behavioral/acceptance component.

### G-I9 VERSION_CHANGE_IMPACT
Material governance changes trigger explicit impact/requalification analysis.

### G-I10 CURRENT_DEPENDENCIES
Coverage depends on current evidence/control/authority state, not only historical signatures.

### G-I11 POLICY_PRECEDENCE_EXPLICIT
Conflicting governance/instruction sources use a frozen precedence policy rather than evaluator improvisation.

### G-I12 NO_UNIVERSAL_ALIGNMENT_INFERENCE
Bounded coverage evidence does not become a universal claim that the agent is aligned, moral, safe, or trustworthy.

---

## 32. Relationship to Evidence Architecture

This architecture generates:

```text
EvidenceRequirement
```

objects from behaviorally evaluable governance clauses.

The Behavioral & Functional Evidence Architecture controls how those requirements are actually tested and turned into trustworthy evidence receipts.

---

## 33. Relationship to Qualification

Qualification consumes:

- governance source bindings;
- coverage manifests;
- structural-control conformance evidence;
- behavioral evidence receipts;
- governance acceptance artifacts;
- current trust-state information.

Qualification then decides eligibility for a bounded role/profile.

Governance mapping itself does not issue qualification.

---

## 34. Relationship to Runtime Trust and Enforcement

Future composition:

```text
CoA / Value Architecture / Policy
       |
       v
Governance Operationalization
       |
       +--> Structural Controls
       |
       +--> Evidence Requirements
       |
       v
Qualification
       |
       v
Runtime Identity / Attestation
       |
       v
VerifiedRuntimeContext
       |
       v
Bounded Authorization
       |
       v
Enforcement Plane
```

This closes the conceptual gap between values/commitments and executable trust decisions.

---

## 35. Recommended Next Step

Perform:

**ATE Governance-to-Evidence Mapping Adversarial Review v0.1**

Attack at minimum:

- vague values translated into overly broad claims;
- required clause omission;
- evaluator redefining policy precedence;
- behavioral evidence substituted for structural control;
- acceptance substituted for adherence;
- stale evidence/control dependencies;
- governance-version downgrade;
- compatibility declarations hiding new obligations;
- coverage summary claiming more than referenced evidence;
- "aligned/safe/trustworthy" label inflation.

No live model evaluation is required.

---

## 36. Final Statement

ATE should never rely on the sentence:

```text
"this agent follows our values"
```

when it can instead state precisely:

```text
this exact profile accepted governance source G,
required clauses C1..Cn were explicitly operationalized,
structural controls S are enforced,
behavioral claims B were evaluated under protocols P,
current evidence satisfies qualification Q,
and uncovered/non-claimed areas are explicit.
```

That is how Value Architecture and Condition of Agency become verifiable engineering inputs rather than aspirational labels.
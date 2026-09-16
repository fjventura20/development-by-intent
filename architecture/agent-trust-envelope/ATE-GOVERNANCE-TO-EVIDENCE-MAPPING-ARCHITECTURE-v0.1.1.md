# ATE Governance-to-Evidence Mapping Architecture v0.1.1

**Status:** Revised architecture candidate — DESIGN ONLY  
**Date:** 2026-09-16  
**Program:** Agent Trust Envelope (ATE)  
**Supersedes:** `ATE-GOVERNANCE-TO-EVIDENCE-MAPPING-ARCHITECTURE-v0.1.md`  
**Adversarial review:** `ATE-GOVERNANCE-TO-EVIDENCE-MAPPING-ADVERSARIAL-REVIEW-v0.1.md`

---

## 1. Controlling Principle

> **Governance becomes an engineering input only when the complete controlling source is inventoried, each applicable clause is explicitly operationalized by an authorized authority, coverage is bounded to what was actually enforced/evaluated, and current dependencies remain verifiable.**

ATE MUST NOT infer:

```text
signed governance text -> behavioral compliance
accepted CoA -> demonstrated adherence
few successful tests -> full meaning of a broad value
```

---

## 2. Corrected Governance Chain

```text
GovernanceSource
    |
    v
GovernanceClauseManifest       <- complete controlling clause inventory
    |
    v
Operationalization Authority + Coverage Policy
    |
    v
GovernanceOperationalizationRecord(s)
    |
    +--> StructuralControlRequirement(s)
    +--> EvidenceRequirement(s)
    +--> AcceptanceRequirement(s)
    +--> Interaction/Precedence Requirement(s)
    |
    v
GovernanceCoverageManifest
    |
    v
Qualification Evidence / Current Dependency Verification
    |
    v
Bounded Qualification Claim
```

No stage implies the next without verification.

---

## 3. Governance Source

```text
GovernanceSource {
    governance_source_id
    governance_type
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

Unknown, revoked, expired, or incompatibly superseded source state fails according to active policy.

---

## 4. Governance Clause Manifest

Every governance source/version used for qualification SHALL have an authoritative complete clause inventory.

```text
GovernanceClauseManifest {
    governance_source_id
    governance_source_digest
    decomposition_method
    decomposition_version

    clauses[] {
        clause_id
        clause_text_digest
        clause_type
        applicability_metadata
        required_for_role_classes[]?
        cross_clause_dependency_ids[]?
        interaction_rule_ids[]?
    }

    manifest_digest
    decomposition_authority_id
    issued_at
    signature
}
```

Coverage accounting starts from this manifest.

An operationalizer cannot make an obligation disappear by simply never creating a record for it.

A required governance source without an accepted ClauseManifest cannot support a claim of complete required governance coverage.

---

## 5. Clause Types

At minimum:

```text
ACCEPTANCE_COMMITMENT
CAPABILITY_AUTHORITY
BEHAVIORAL_REQUIREMENT
BEHAVIORAL_PROHIBITION
ESCALATION_HUMAN_AUTHORITY
ACCOUNTABILITY_REPORTING
ASPIRATIONAL_OR_BROAD_NORMATIVE
```

The clause type informs operationalization but does not itself determine satisfaction.

---

## 6. Enforceability Classes

Each applicable clause receives one signed classification:

```text
STRUCTURALLY_ENFORCEABLE
BEHAVIORALLY_EVALUABLE
MIXED_STRUCTURAL_AND_BEHAVIORAL
DECLARATIVE_ACCEPTANCE_ONLY
NOT_YET_OPERATIONALIZED
NOT_APPLICABLE_WITH_SIGNED_BASIS
```

The qualified subject MUST NOT choose its own controlling classification.

---

## 7. Structural Enforcement Requirement

Operationalization SHALL explicitly state:

```text
structural_enforcement_requirement =
    REQUIRED
    REQUIRED_WHERE_CAPABILITY_EXISTS
    DEFENSE_IN_DEPTH_ONLY
    NOT_APPLICABLE
```

If structural enforcement is `REQUIRED`, behavioral willingness/evidence cannot substitute for the structural control.

This field is a governance/policy decision, not an implementer convenience choice.

---

## 8. Operationalization Authority

A Governance Operationalization Authority credential SHALL constrain at least:

```text
may_operationalize_governance_types[]
permitted_trust_domains[]
permitted_project_scopes[]
maximum_risk_class
maximum_assurance_tier
may_mark_not_applicable
may_classify_acceptance_only
may_define_structural_controls
may_define_behavioral_claims
may_define_interaction_rules
may_issue_coverage_manifest
validity
revocation_handle
```

A valid signature outside these ceilings is invalid.

The subject being qualified MUST NOT be the sole authority for its own controlling operationalization where policy requires independent governance authority.

---

## 9. Coverage Policy Authority

A separate or explicitly authorized Governance Policy Authority SHALL define high-consequence classification rules, including:

- when `NOT_APPLICABLE` is allowed;
- when `DECLARATIVE_ACCEPTANCE_ONLY` is sufficient;
- which clauses require structural controls;
- which broad clauses may only claim bounded operationalization;
- required interaction/precedence tests;
- uncovered-clause tolerance;
- required independent approval for weakening/reclassification.

Operationalization Authority cannot override Coverage Policy merely by signing a different classification.

---

## 10. Governance Operationalization Record

```text
GovernanceOperationalizationRecord {
    operationalization_id
    governance_source_id
    governance_source_digest
    clause_manifest_digest
    clause_id
    clause_text_digest
    enforceability_class
    structural_enforcement_requirement
    coverage_extent

    structural_control_requirement_ids[]
    evidence_requirement_ids[]
    acceptance_requirement_ids[]
    interaction_rule_ids[]
    required_interaction_evidence_requirement_ids[]
    precedence_policy_digest?

    observable_claims[]
    limitations_non_claims[]
    applicability_scope

    policy_epoch
    coverage_policy_digest
    operationalization_authority_id
    approval_authority_refs[]?
    signature
}
```

---

## 11. Coverage Extent

To prevent semantic overclaiming, every operationalization states one extent:

```text
EXACT_STRUCTURAL_REQUIREMENT
BOUNDED_OPERATIONALIZATION
COMPOSITE_BOUNDED_OPERATIONALIZATION
ACCEPTANCE_ONLY
NOT_OPERATIONALIZED
NOT_APPLICABLE
```

### EXACT_STRUCTURAL_REQUIREMENT

Policy defines the operative clause meaning exactly in terms of a structural condition/invariant.

### BOUNDED_OPERATIONALIZATION

The evidence/control supports only the explicitly mapped observable claim(s), not the full ordinary-language meaning of the broad clause.

### COMPOSITE_BOUNDED_OPERATIONALIZATION

Multiple controls/evidence claims collectively support the bounded operational interpretation, but do not assert universal semantic equivalence unless policy explicitly defines that equivalence.

Broad normative language defaults to bounded operationalization unless the governing policy explicitly defines a narrower operative meaning.

---

## 12. Observable Governance Claim

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

Claims target observable behavior, not hidden thoughts, motives, virtue, consciousness, or private chain of reasoning.

---

## 13. Structural Governance Control Requirement

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

Qualification may require current structural-conformance evidence for the evaluated/deployed profile.

---

## 14. Behavioral Evidence Requirement Derivation

For every behaviorally evaluable claim, derive an ATE `EvidenceRequirement` binding:

- governance source/clause digest;
- operationalization record digest;
- observable claim digest;
- subject/profile constraints;
- task/population scope;
- protocol family;
- evaluator/runner requirements;
- evidence lifecycle;
- refresh/requalification triggers;
- risk/assurance applicability;
- limitations/non-claims.

The Behavioral & Functional Evidence Architecture controls actual evaluation integrity.

---

## 15. Governance Acceptance Requirement

Acceptance evidence remains distinct from adherence evidence.

```text
GovernanceAcceptanceRequirement {
    acceptance_requirement_id
    governance_source_digest
    subject/runtime/session binding requirements
    validity/current-state rules
    acceptance authority requirements
    policy_epoch
}
```

Qualification/runtime trust may require acceptance in addition to structural/behavioral coverage.

---

## 16. Cross-Clause Dependencies

Clause-by-clause evaluation is insufficient when clauses interact.

ClauseManifest and OperationalizationRecord SHALL support:

```text
cross_clause_dependency_ids[]
interaction_rule_ids[]
required_interaction_evidence_requirement_ids[]
```

Example:

```text
C1: follow authorized instruction
C2: refuse instruction conflicting with higher-priority safety policy
```

Coverage may require a conflict scenario proving the frozen precedence behavior, not merely isolated C1 and C2 cases.

---

## 17. Precedence Policy

Conflicting instruction/governance sources use a signed explicit precedence policy.

```text
GovernancePrecedencePolicy {
    precedence_policy_id
    source_classes[]
    ordering / conflict rules
    exception rules
    trust_domain_id
    project_scope
    policy_epoch
    issuer
    signature
}
```

Behavioral protocols SHALL bind the exact precedence-policy digest being tested.

Evaluators do not improvise precedence after observing subject behavior.

---

## 18. Mixed Clause Satisfaction

For a mixed clause:

```text
satisfied_for_qualification =
    all REQUIRED structural controls current
    AND all required behavioral evidence current
    AND required acceptance evidence current
    AND required interaction evidence current
```

No component silently substitutes for another.

---

## 19. Coverage Status

Coverage status remains explicit:

```text
COVERED_STRUCTURALLY
COVERED_BY_EVIDENCE
COVERED_MIXED
ACCEPTANCE_ONLY
NOT_YET_OPERATIONALIZED
NOT_APPLICABLE_WITH_SIGNED_BASIS
```

The status must be interpreted together with `coverage_extent`.

For example:

```text
coverage_status = COVERED_BY_EVIDENCE
coverage_extent = BOUNDED_OPERATIONALIZATION
```

means the required bounded operational claim was evidenced; it does not prove the full ordinary-language virtue.

---

## 20. Governance Coverage Manifest

```text
GovernanceCoverageManifest {
    coverage_manifest_id
    governance_source_id
    governance_source_digest
    clause_manifest_digest
    coverage_policy_digest
    operationalization_version

    clause_entries[] {
        clause_id
        operationalization_record_digest
        coverage_status
        coverage_extent
        structural_control_refs[]
        evidence_requirement_refs[]
        acceptance_requirement_refs[]
        interaction_requirement_refs[]
    }

    uncovered_required_clauses[]
    not_applicable_clause_refs[]
    policy_epoch
    issued_at
    issuer
    signature
}
```

Verification reconciles this manifest against the authoritative ClauseManifest.

Required clauses cannot disappear.

---

## 21. Full Required Coverage Rule

A claim of:

```text
GOVERNANCE_REQUIRED_CLAUSES_COVERED
```

requires, under active coverage policy:

- every required clause in ClauseManifest accounted for;
- no impermissible uncovered required clauses;
- required operationalization approvals valid;
- required structural/evidence/acceptance/interaction dependencies current;
- no current trust-state invalidation;
- current policy epoch.

It still means **required operationalized coverage**, not universal moral or philosophical equivalence, unless policy explicitly defines otherwise.

---

## 22. Precise Claim Language

ATE distinguishes:

```text
GOVERNANCE_ACCEPTED
GOVERNANCE_REQUIRED_OPERATIONALIZED_CLAIMS_COVERED
GOVERNANCE_PARTIALLY_COVERED
GOVERNANCE_COVERAGE_STALE
GOVERNANCE_COVERAGE_REVOKED
GOVERNANCE_NOT_OPERATIONALIZED
```

Avoid unbounded labels such as:

```text
aligned
ethical
safe
trustworthy
integrity proven
```

unless a project specification defines a bounded formal meaning.

---

## 23. Example — Integrity

Source:

```text
Act with integrity.
```

Operational claims might include:

```text
I1: no false completion report against authoritative execution state
I2: disclose material uncertainty when evidence is insufficient
I3: do not fabricate citations/evidence
I4: report formal evaluation failure rather than silently converting it to PASS
```

Unless policy defines these as the entire operative meaning of the clause, use:

```text
coverage_extent = COMPOSITE_BOUNDED_OPERATIONALIZATION
```

ATE may state these claims were evidenced without claiming internal moral character.

---

## 24. Example — Human Authority

Source:

```text
Respect human authority for high-impact decisions.
```

Possible mapping:

```text
structural_enforcement_requirement = REQUIRED
structural control: risk >= R3 requires human approval artifact
behavioral claim: ambiguous high-impact request triggers escalation
acceptance: active CoA acceptance required
interaction: user instruction vs high-risk policy precedence tested
coverage_extent = COMPOSITE_BOUNDED_OPERATIONALIZATION
```

This is stronger and more precise than a generic "respects humans" label.

---

## 25. Governance Change Impact

Every material source update SHALL have a signed impact record:

```text
GovernanceChangeImpact {
    change_impact_id
    source_governance_digest
    target_governance_digest
    source_clause_manifest_digest
    target_clause_manifest_digest

    added_clause_ids[]
    removed_clause_ids[]
    changed_clause_ids[]
    unchanged_clause_ids[]

    affected_operationalization_ids[]
    affected_evidence_requirement_ids[]
    affected_structural_control_ids[]
    affected_acceptance_requirement_ids[]
    affected_interaction_rule_ids[]

    reacceptance_required
    evidence_refresh_required[]
    requalification_action

    coverage_policy_digest
    policy_epoch
    impact_authority_id
    signature
}
```

Version labels alone do not determine compatibility.

---

## 26. Change Outcomes

Possible deterministic outcomes:

```text
NO_QUALIFICATION_IMPACT
RE_ACCEPTANCE_REQUIRED
EVIDENCE_REFRESH_REQUIRED
PARTIAL_REQUALIFICATION_REQUIRED
FULL_REQUALIFICATION_REQUIRED
IMMEDIATE_SUSPENSION
```

Unknown material governance impact defaults to full requalification or suspension when safe current state cannot be established.

---

## 27. Mapping Compatibility

Compatibility may preserve some operationalizations/evidence only when a signed current policy decision establishes:

- exact source/target governance digests;
- exact changed clauses;
- unchanged bounded observable claims;
- affected structural/behavioral/acceptance dependencies;
- preserved/invalidated evidence;
- no capability/risk/assurance expansion;
- current policy epoch.

Compatibility cannot make a new obligation covered without required controls/evidence.

---

## 28. Current Dependency Verification

A `GovernanceCoverageManifest` is historical/configuration evidence.

Current use requires revalidation of controlling dependencies:

- governance source status;
- operationalization/coverage policy status;
- structural-control evidence;
- behavioral evidence receipts;
- acceptance evidence;
- evaluator/evidence authority state where controlling;
- qualification status;
- trust-state/policy epochs.

Historical signature validity alone is insufficient.

---

## 29. GovernanceCoverageClaim Is Non-Authoritative Summary

```text
GovernanceCoverageClaim
```

MAY summarize references/digests, but MUST NOT independently prove current coverage.

For a current qualification/trust decision, verifier SHALL revalidate referenced dependencies/current trust state according to policy.

This prevents replay of a once-valid summary after underlying evidence/control becomes stale or revoked.

---

## 30. Operational Monitoring

Signed operational/drift evidence may detect:

- false completion reporting;
- escalation failures;
- attempts to exceed authority;
- denial circumvention patterns;
- discrepancies between narrative and authoritative audit state.

These signals feed qualification status/requalification policy and do not rewrite historical qualification-time evidence.

---

## 31. No Hidden-Thought Requirement

ATE governance evidence relies on observable/verifiable artifacts:

- inputs/outputs;
- signed acceptances;
- tool/action traces;
- audit records;
- execution outcomes;
- structural-control state;
- evaluation receipts.

Private chain-of-thought disclosure is neither required nor treated as controlling evidence of moral character.

---

## 32. Failure-Closed Rules

Fail closed for:

- missing/invalid GovernanceSource;
- missing/unaccepted ClauseManifest;
- coverage manifest omitting required clause;
- unauthorized Operationalization Authority;
- unauthorized weakening/reclassification;
- required structural control missing;
- behavioral evidence claim/scope mismatch;
- acceptance evidence missing/stale;
- required interaction evidence missing;
- precedence-policy mismatch;
- stale/revoked dependency;
- policy epoch rollback;
- material governance update without valid change-impact analysis;
- summary claim exceeding actual coverage extent.

---

## 33. Required Invariants

### G-I1 COMPLETE_SOURCE_INVENTORY
Coverage starts from an authoritative ClauseManifest representing the controlling source/version.

### G-I2 SOURCE_BINDING
Operationalization binds exact source/clause digests.

### G-I3 AUTHORIZED_OPERATIONALIZATION
Operationalization/reclassification obeys authority ceilings and Coverage Policy.

### G-I4 EXPLICIT_ENFORCEABILITY
Every applicable clause has explicit enforceability and structural-enforcement requirement.

### G-I5 BOUNDED_SEMANTICS
Broad values default to bounded operational claims; coverage cannot silently imply universal semantic equivalence.

### G-I6 NO_SILENT_OMISSION
Every required ClauseManifest clause is accounted for in coverage verification.

### G-I7 STRUCTURAL_FIRST_WHEN_REQUIRED
Behavioral evidence cannot replace a REQUIRED structural control.

### G-I8 ACCEPTANCE_NOT_ADHERENCE
Acceptance and adherence evidence remain distinct.

### G-I9 CROSS_CLAUSE_INTERACTIONS
Policy-required interactions/precedence behavior must be explicitly covered.

### G-I10 MIXED_REQUIRES_ALL
Mixed clauses require all mandated control/evidence/acceptance/interaction components.

### G-I11 VERSION_CHANGE_IMPACT
Governance updates require signed clause-aware impact analysis.

### G-I12 CURRENT_DEPENDENCIES
Current claims depend on current evidence/control/authority state, not historical signatures alone.

### G-I13 COVERAGE_SUMMARY_NOT_AUTHORITY
A GovernanceCoverageClaim cannot bypass live dependency verification.

### G-I14 NO_UNIVERSAL_ALIGNMENT_INFERENCE
Bounded operationalized coverage cannot be inflated into general claims of alignment, safety, morality, or trustworthiness.

---

## 34. Relationship to Evidence Architecture

This architecture defines which behavioral/functional evidence requirements governance creates.

`ATE-BEHAVIORAL-FUNCTIONAL-EVIDENCE-ARCHITECTURE-v0.1.1` + `v0.1.2` control how such evidence is preregistered, executed, evaluated, and admitted.

---

## 35. Relationship to Qualification

Qualification consumes current governance coverage dependencies and decides bounded role/profile eligibility.

Governance mapping does not itself qualify the subject.

---

## 36. Relationship to Runtime Trust and Enforcement

```text
Governance Source
    -> ClauseManifest
    -> Operationalization / Coverage
    -> Structural Controls + Evidence Requirements + Acceptance
    -> Qualification
    -> Runtime Identity / Attestation
    -> VerifiedRuntimeContext
    -> Bounded Authorization
    -> Enforcement
```

---

## 37. Recommended Next Step

Perform one final consistency review of v0.1.1.

If accepted, design a deterministic local **Governance Coverage Conformance Protocol** testing:

- complete clause accounting;
- authority ceilings;
- reclassification safeguards;
- bounded coverage extent;
- structural-vs-behavioral non-substitution;
- mixed-clause completeness;
- interaction/precedence dependencies;
- governance change impact;
- current dependency verification;
- no universal claim inflation.

No live model behavior evaluation is required for that conformance protocol.

---

## 38. Final Statement

ATE can operationalize values without pretending to prove inner virtue.

The defensible claim is:

```text
this exact governance source was completely inventoried;
required clauses were explicitly mapped under authorized policy;
required structural controls exist;
required bounded behavioral claims have evidence;
required acceptance/interaction dependencies are current;
and uncovered/non-claimed semantics remain visible.
```

That is the appropriate engineering meaning of governance coverage.
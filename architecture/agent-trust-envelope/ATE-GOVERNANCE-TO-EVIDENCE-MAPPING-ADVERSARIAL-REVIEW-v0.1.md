# ATE Governance-to-Evidence Mapping — Adversarial Review v0.1

**Status:** Adversarial architecture review  
**Date:** 2026-09-16  
**Reviewed artifact:** `ATE-GOVERNANCE-TO-EVIDENCE-MAPPING-ARCHITECTURE-v0.1.md`

## Disposition

**REVISION_REQUIRED_BEFORE_CONFORMANCE_PROTOCOL**

The v0.1 architecture correctly separates governance acceptance, structural enforcement, behavioral evidence, qualification, and authorization. It also correctly refuses to equate broad values with hidden mental states.

However, five semantic-control gaps could allow a weak mapping process to produce an apparently complete governance-coverage claim.

---

## 1. Finding A — Clause Decomposition Itself Can Omit Obligations

### Attack

A governance source contains clauses C1..C12.

The operationalizer creates clause records only for C1..C9.

The coverage manifest then truthfully shows complete coverage for all *known* clause records, while C10..C12 disappeared before coverage accounting began.

### Required correction

Introduce an authoritative `GovernanceClauseManifest` that enumerates the full controlling clause set for the source/version.

At minimum:

```text
GovernanceClauseManifest {
    governance_source_id
    governance_source_digest
    decomposition_method/version
    clause_ids[]
    clause_text_digests[]
    cross_clause_dependency_ids[]?
    required_clause_flags[] or applicability metadata
    manifest_digest
    decomposition_authority_id
    signature
}
```

Coverage verification starts from this manifest, not from whichever clauses happen to have operationalization records.

A required source/version without an accepted ClauseManifest cannot claim complete governance coverage.

---

## 2. Finding B — Operationalization Authority Can Launder a Requirement by Reclassification

### Attack

A difficult behavioral requirement is classified as:

```text
NOT_APPLICABLE_WITH_SIGNED_BASIS
```

or:

```text
DECLARATIVE_ACCEPTANCE_ONLY
```

by the same authority that wants an easy qualification outcome.

The clause then no longer requires behavioral evidence.

### Required correction

Define explicit Operationalization Authority ceilings and a separate governance coverage policy.

The authority credential must constrain:

```text
may_operationalize_governance_types[]
trust_domain/project scope
may_mark_not_applicable
may_classify_acceptance_only
may_define_structural controls
may_define behavioral claims
maximum risk/assurance scope
```

High-consequence reclassification (`NOT_APPLICABLE`, weakening STRUCTURAL/MIXED to ACCEPTANCE_ONLY, etc.) SHALL require policy-authorized basis and, where required, separate Governance Policy Authority approval.

The subject being qualified MUST NOT be its own sole operationalization authority for controlling governance coverage.

---

## 3. Finding C — “Covered” Can Overstate the Meaning of a Broad Value

### Attack

Source clause:

```text
Act with integrity.
```

Operationalization tests only:

- no false completion claim;
- disclose uncertainty in ten fixtures.

Coverage manifest labels the original clause:

```text
COVERED_BY_EVIDENCE
```

A downstream reader interprets this as proving the full ordinary-language concept of integrity.

### Required correction

Separate **operationalized coverage** from semantic equivalence.

Add:

```text
coverage_extent =
    EXACT_STRUCTURAL_REQUIREMENT
    BOUNDED_OPERATIONALIZATION
    COMPOSITE_BOUNDED_OPERATIONALIZATION
    ACCEPTANCE_ONLY
    NOT_OPERATIONALIZED
```

For broad normative language, default to `BOUNDED_OPERATIONALIZATION` unless policy explicitly defines the clause's operative meaning as exactly the mapped claims.

Coverage claims SHALL preserve:

- observable claims actually tested;
- limitations/non-claims;
- whether full normative semantics are intentionally not asserted.

A qualification may say "required operationalized claims for clause C were satisfied" without claiming universal moral integrity.

---

## 4. Finding D — Clause-by-Clause Coverage Can Miss Interactions and Exceptions

### Attack

C1 says follow authorized instructions.

C2 says refuse instructions that violate safety policy.

Both are independently tested and pass.

No test covers the conflict case where an authorized instruction violates safety policy.

The coverage manifest claims both clauses covered even though their precedence interaction is untested.

### Required correction

ClauseManifest / OperationalizationRecord SHALL support:

```text
cross_clause_dependency_ids[]
interaction_rule_ids[]
precedence_policy_digest
required_interaction_evidence_requirement_ids[]
```

Coverage policy may require interaction evidence for specified clause combinations.

Behavioral protocols SHALL bind the exact precedence policy they test.

---

## 5. Finding E — Structural-First Rule Needs Policy Authority, Not Convenience

### Attack

An implementer decides a requirement is "not practically structurally enforceable" and downgrades it to behavioral evaluation only, avoiding a stronger enforcement boundary.

### Required correction

Whether structural enforcement is REQUIRED, PREFERRED, or NOT_APPLICABLE SHALL be part of the signed operationalization/coverage policy.

Suggested field:

```text
structural_enforcement_requirement =
    REQUIRED
    REQUIRED_WHERE_CAPABILITY_EXISTS
    DEFENSE_IN_DEPTH_ONLY
    NOT_APPLICABLE
```

If structural enforcement is REQUIRED, behavioral evidence cannot satisfy the clause without the structural control evidence.

---

## 6. Finding F — Coverage Summary Must Bind Current Dependency State

v0.1 notes current dependencies but the portable `GovernanceCoverageClaim` could be replayed after its underlying evidence/control/acceptance becomes stale or revoked.

### Required correction

A coverage claim MUST either:

- be short-lived and bind current dependency/trust-state epochs; or
- be treated only as a summary requiring live verification of referenced dependencies.

For v0.1.1 choose the safer default:

> `GovernanceCoverageClaim` is a non-authoritative summary/reference object. Current qualification/trust decisions MUST revalidate referenced dependencies and authoritative trust state.

It cannot independently prove current coverage.

---

## 7. Finding G — Governance Change Impact Must Start From Clause Diff, Not Version Label

v0.1 already states version labels are insufficient, but the architecture should require a signed change-impact object.

Add:

```text
GovernanceChangeImpact {
    source_governance_digest
    target_governance_digest
    added_clause_ids[]
    removed_clause_ids[]
    changed_clause_ids[]
    affected_operationalization_ids[]
    affected_evidence_requirement_ids[]
    affected_structural_controls[]
    reacceptance_required
    requalification_action
    policy_epoch
    issuer
    signature
}
```

This object prevents an informal "minor version" judgment from preserving stale evidence.

---

## 8. Accepted v0.1 Elements

No redesign is required for:

- acceptance vs adherence distinction;
- enforceability classes as a concept;
- observable-claim model;
- honesty/commitment examples;
- structural + behavioral mixed coverage;
- qualification integration;
- precedence policy concept;
- current dependency checks;
- no-hidden-thought rule;
- precise governance coverage vocabulary;
- no universal alignment/safety inference.

---

## 9. Required v0.1.1 Corrections

Create v0.1.1 adding:

1. authoritative complete `GovernanceClauseManifest`;
2. Operationalization Authority role ceilings and policy-controlled reclassification;
3. bounded `coverage_extent` semantics;
4. cross-clause interaction/precedence evidence dependencies;
5. explicit structural-enforcement requirement field;
6. coverage claim as non-authoritative summary requiring current dependency verification;
7. signed `GovernanceChangeImpact` object.

Then perform a final consistency review against qualification/evidence/runtime-trust boundaries.

---

## 10. Final Statement

Governance operationalization must not turn this:

```text
broad value
    -> a few convenient tests
    -> "fully compliant"
```

into an accepted ATE claim.

The safe model is:

```text
complete source clause inventory
    -> authorized operationalization
    -> explicit bounded claim semantics
    -> required structural/behavioral/acceptance dependencies
    -> interaction/precedence coverage
    -> current dependency verification
    -> precisely worded qualification claim
```

That preserves the meaning of Value Architecture and Condition of Agency without pretending ATE can cryptographically prove moral character.
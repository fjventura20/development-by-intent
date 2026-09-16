# ATE Governance Coverage Protocol — Adversarial Review v0.1

**Status:** Adversarial protocol review  
**Date:** 2026-09-16  
**Reviewed artifact:** `ATE-GOVERNANCE-COVERAGE-LOCAL-CONFORMANCE-PROTOCOL-v0.1.md`

## Disposition

**SURGICAL_REVISION_REQUIRED_BEFORE_FREEZE**

The 12-test matrix is appropriate and lean. Two fixture semantics require stronger freezing so the conformance harness proves the intended governance safeguards rather than relying on implicit conventions.

---

## 1. Operationalization and Coverage Policy Authority Must Be Distinct in This Profile

### Attack

One fixture key holds both:

- Governance Operationalization Authority; and
- Governance/Coverage Policy Authority.

It reclassifies C1 from REQUIRED structural to behavioral-only and then "approves" its own weakening.

The verifier sees valid signatures for both roles but no meaningful separation exists.

### Required correction

For this local conformance protocol freeze:

```text
OperationalizationAuthority key != CoveragePolicyAuthority key
OperationalizationAuthority role != CoveragePolicyAuthority role
```

RoleCredentials must enforce this distinction.

Where a weakening requires separate policy approval, the exact operationalization record and weakening decision digest must be approved by Coverage Policy Authority.

Add a GC-T2 variant where Operationalization Authority signs both the weakened mapping and a fake approval; expected REJECTED because it lacks Coverage Policy approval role.

The same implementation process may host fixtures, but keys/roles remain logically distinct.

---

## 2. Claim Inflation Must Be Machine-Verifiable, Not Prose Interpretation

GC-T3 and GC-T11 currently include phrases such as:

```text
"integrity proven"
"aligned/safe/trustworthy"
```

A deterministic conformance harness should not need natural-language semantic judgment to decide whether a claim is too broad.

### Required correction

Freeze a structured claim vocabulary:

```text
GovernanceCoverageClaimType =
    GOVERNANCE_ACCEPTED
    REQUIRED_OPERATIONALIZED_CLAIMS_COVERED
    PARTIAL_OPERATIONALIZED_COVERAGE
    GOVERNANCE_COVERAGE_STALE
    GOVERNANCE_NOT_OPERATIONALIZED
```

and explicit `covered_clause_ids[]`, `coverage_extent_by_clause`, `uncovered_clause_ids[]`, plus referenced dependency digests.

The local verifier rejects:

- unknown/unbounded claim types;
- `REQUIRED_OPERATIONALIZED_CLAIMS_COVERED` when required uncovered clauses exist;
- claim coverage extent stronger than OperationalizationRecord;
- covered-clause set not reconciled to ClauseManifest/CoverageManifest.

Human-facing prose labels may exist outside the conformance object, but they are not controlling protocol inputs.

---

## 3. ClauseManifest Completeness Fixture Must Use a Frozen Oracle

The architecture properly treats the Decomposition Authority as a trust role and does not claim semantic perfection.

For this deterministic protocol, however, G1's expected clause set is known exactly.

Freeze:

```text
expected_G1_clause_ids = [C1, C2, C3, C4]
expected_G1_clause_text_digests = [...]
```

The conformance harness compares ClauseManifest to this fixture oracle.

This tests completeness machinery for the fixture without claiming a general natural-language decomposition algorithm.

GC-T1 should include a ClauseManifest omitting C4 and reject it against the frozen fixture oracle.

---

## 4. Current Dependency Authority Should Remain Independent

The v0.1 protocol already has a Trust-State Authority fixture. Preserve it as a distinct role from Coverage Policy / Operationalization Authority.

This prevents a stale dependency package from self-certifying current validity.

No new test ID is required; GC-T9 exercises the current-state path.

---

## 5. Accepted Protocol Elements

No change is required for:

- baseline four-clause source;
- structural vs behavioral mapping;
- mixed C3 semantics;
- acceptance/adherence separation;
- interaction/precedence checks;
- governance-change impact testing;
- summary replay test;
- non-operationalized clause test;
- 12-test count;
- no-live-model execution boundary.

---

## 6. Required v0.1.1 Changes

Preserve GC-T0..GC-T11 exactly, while adding:

1. distinct Operationalization vs Coverage Policy keys/RoleCredentials;
2. GC-T2 fake self-approval weakening variant;
3. structured GovernanceCoverageClaim object/type semantics;
4. deterministic claim inflation checks rather than prose interpretation;
5. frozen expected G1 ClauseManifest oracle;
6. distinct Trust-State Authority role preserved.

Then perform one final freeze review.

---

## 7. Final Statement

The conformance protocol should prove policy separation and claim bounding through **machine-verifiable structure**, not through assumed organizational separation or natural-language judgment.

With these changes, the 12-test protocol is appropriate for freeze.
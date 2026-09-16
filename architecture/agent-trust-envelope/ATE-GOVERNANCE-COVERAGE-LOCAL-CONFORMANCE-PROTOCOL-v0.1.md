# ATE Governance Coverage Local Conformance Protocol v0.1

**Status:** Freeze candidate — DESIGN ONLY  
**Date:** 2026-09-16  
**Program:** Agent Trust Envelope (ATE)  
**Controlling architecture:** `ATE-GOVERNANCE-TO-EVIDENCE-MAPPING-ARCHITECTURE-v0.1.1.md`  
**Final architecture review:** `ATE-GOVERNANCE-TO-EVIDENCE-MAPPING-FINAL-REVIEW-v0.1.md`

---

## 1. Research Question

> **Can a deterministic local governance-coverage verifier reject incomplete, unauthorized, semantically inflated, structurally weakened, interaction-incomplete, stale, or version-mismatched governance mappings before they support an ATE qualification claim?**

This protocol tests governance mapping/coverage machinery only.

It does not evaluate actual AI behavior, moral character, alignment, or safety.

---

## 2. Lean Local Profile

Use one deterministic local trust domain with fixture authorities for:

- Governance Source Authority;
- Clause Decomposition Authority;
- Governance Operationalization Authority;
- Governance/Coverage Policy Authority;
- Structural Control Evidence Authority;
- Behavioral Evidence Authority;
- Governance Acceptance Authority;
- Qualification/Coverage Verifier;
- Trust-State Authority.

All controlling artifacts use explicit RoleCredentials or frozen equivalent authority rules.

No live model invocation is required.

---

## 3. Crypto / Canonicalization

Freeze:

```text
signature_algorithm = Ed25519
digest_algorithm = SHA-256
canonicalization = RFC 8785 JCS
```

Unknown mandatory versions/algorithms fail closed.

---

## 4. Baseline Governance Fixture

Freeze one governance source `G1` with four clauses:

```text
C1 — production mutation requires authorized executor path
     type: CAPABILITY_AUTHORITY
     enforceability: STRUCTURALLY_ENFORCEABLE
     structural_enforcement_requirement: REQUIRED
     coverage_extent: EXACT_STRUCTURAL_REQUIREMENT

C2 — do not falsely claim completion when authoritative execution state shows no completion
     type: ACCOUNTABILITY_REPORTING / BEHAVIORAL_PROHIBITION
     enforceability: BEHAVIORALLY_EVALUABLE
     coverage_extent: BOUNDED_OPERATIONALIZATION

C3 — authorized instructions conflicting with high-risk policy require policy precedence / escalation
     type: ESCALATION_HUMAN_AUTHORITY
     enforceability: MIXED_STRUCTURAL_AND_BEHAVIORAL
     structural_enforcement_requirement: REQUIRED
     coverage_extent: COMPOSITE_BOUNDED_OPERATIONALIZATION
     interaction: C3 with precedence policy PP1

C4 — exact governance source/version must be explicitly accepted
     type: ACCEPTANCE_COMMITMENT
     enforceability: DECLARATIVE_ACCEPTANCE_ONLY
     coverage_extent: ACCEPTANCE_ONLY
```

The exact canonical fixture source text/digests SHALL be frozen by the implementation before formal run.

---

## 5. Baseline ClauseManifest

The authoritative `GovernanceClauseManifest` SHALL contain exactly:

```text
C1, C2, C3, C4
```

with source digest `G1`, clause text digests, types, applicability, and C3 interaction metadata.

All four clauses are required for the baseline role/profile.

---

## 6. Baseline Coverage Policy

Freeze these rules:

- C1 MUST remain structurally required;
- C2 MUST remain behaviorally evaluable;
- C3 MUST remain mixed and requires structural + behavioral + interaction evidence;
- C4 MUST require acceptance evidence;
- only Coverage Policy Authority may approve `NOT_APPLICABLE` for a required baseline clause;
- baseline test profile has no approved `NOT_APPLICABLE` clauses;
- broad/behavioral C2/C3 coverage MUST NOT be promoted beyond bounded extent;
- current dependency state is required for qualification use;
- `GovernanceCoverageClaim` is summary-only and not current-state authority.

---

## 7. Baseline Dependency Fixtures

Use deterministic signed fixtures:

```text
SC1 = current structural-control conformance evidence for C1
SC3 = current structural-control conformance evidence for C3
BE2 = current bounded behavioral evidence receipt for C2
BE3 = current bounded behavioral/interaction evidence receipt for C3
GA4 = current governance acceptance evidence for C4
PP1 = current precedence policy
IE3 = explicit C3 interaction evidence referencing PP1
```

These fixtures are synthetic. Their purpose is to test mapping verification, not real behavior.

---

## 8. Baseline Operationalization

Valid baseline:

```text
C1 -> SC1
C2 -> BE2
C3 -> SC3 + BE3 + IE3 + PP1
C4 -> GA4
```

All dependencies are current and trusted under baseline TrustStateSnapshot.

Expected baseline claim:

```text
GOVERNANCE_REQUIRED_OPERATIONALIZED_CLAIMS_COVERED
```

with coverage limited to the accepted ClauseManifest / operationalized semantics.

---

## 9. Frozen Invariants Under Test

### GC-I1 COMPLETE_CLAUSE_ACCOUNTING
Every required accepted-ClauseManifest clause is accounted for.

### GC-I2 AUTHORIZED_OPERATIONALIZATION
Operationalization/reclassification respects RoleCredentials and Coverage Policy.

### GC-I3 BOUNDED_COVERAGE_EXTENT
Coverage claims do not exceed exact/bounded semantics.

### GC-I4 STRUCTURAL_NON_SUBSTITUTION
Required structural control cannot be replaced by behavioral evidence.

### GC-I5 ACCEPTANCE_NOT_ADHERENCE
Acceptance evidence cannot substitute for required behavioral/structural adherence evidence, and vice versa.

### GC-I6 MIXED_COMPONENT_COMPLETENESS
Mixed clauses require all mandated components.

### GC-I7 INTERACTION_PRECEDENCE_BINDING
Required interaction evidence binds the accepted precedence policy.

### GC-I8 GOVERNANCE_CHANGE_IMPACT
Changed governance requires clause-aware impact handling; version labels alone do not preserve coverage.

### GC-I9 CURRENT_DEPENDENCY_STATE
Current coverage depends on current evidence/control/authority/trust-state state.

### GC-I10 SUMMARY_NOT_AUTHORITY
Coverage summary objects cannot bypass live dependency verification.

### GC-I11 NO_UNIVERSAL_INFERENCE
Bounded coverage cannot become generic alignment/safety/morality/trustworthiness claims.

---

## 10. Controlling Test Matrix

Freeze exactly **12 controlling tests**, GC-T0 through GC-T11.

### GC-T0 — Valid baseline coverage

Verify G1 + ClauseManifest + valid operationalization + SC1/SC3 + BE2/BE3 + IE3/PP1 + GA4 + current trust state.

Expected:

```text
GOVERNANCE_REQUIRED_OPERATIONALIZED_CLAIMS_COVERED
```

All clause entries C1..C4 accounted for.

### GC-T1 — Clause omission / manifest mismatch

Variants:

A. CoverageManifest omits required C2;
B. Operationalization set has no record for C3;
C. ClauseManifest source digest differs from GovernanceSource digest;
D. CoverageManifest references a different ClauseManifest digest.

Expected: all REJECTED.

### GC-T2 — Unauthorized operationalization / weakening

Variants:

A. subject/self authority marks C1 `NOT_APPLICABLE`;
B. Operationalization Authority lacking permission changes C1 from REQUIRED structural to behavioral-only;
C. unauthorized authority marks C2 acceptance-only;
D. valid operationalizer attempts policy-prohibited weakening without Coverage Policy approval.

Expected: all REJECTED.

### GC-T3 — Coverage-extent inflation

Baseline C2 is `BOUNDED_OPERATIONALIZATION`.

Variants:

A. claim C2 is `EXACT_STRUCTURAL_REQUIREMENT`;
B. claim "integrity proven" from BE2;
C. claim generic `aligned/safe/trustworthy` from bounded C2/C3 evidence;
D. preserve exact bounded claim wording/reference.

Expected A-C: REJECTED / claim invalid.

Expected D: accepted.

### GC-T4 — Structural control substituted by behavior

For C1:

A. omit SC1 but provide synthetic behavioral PASS;
B. provide expired/revoked SC1 but current behavioral PASS;
C. provide current SC1.

Expected A-B: REJECTED.

Expected C: component satisfied.

### GC-T5 — Acceptance/adherence substitution

Variants:

A. use GA4 acceptance as substitute for BE2;
B. use BE2 as substitute for GA4 acceptance;
C. use acceptance alone for mixed C3;
D. provide each required evidence class correctly.

Expected A-C: REJECTED.

Expected D: accepted.

### GC-T6 — Mixed clause completeness

For C3 variants:

A. SC3 only;
B. BE3 only;
C. SC3 + BE3 but no interaction evidence;
D. SC3 + BE3 + IE3 + PP1.

Expected A-C: REJECTED.

Expected D: satisfied.

### GC-T7 — Interaction / precedence mismatch

Variants:

A. IE3 references wrong precedence policy digest;
B. PP1 is superseded by current PP2 but IE3 still binds PP1;
C. interaction evidence tests isolated clause behavior but not required conflict scenario;
D. current interaction evidence binds active PP1 baseline.

Expected A-C: REJECTED.

Expected D: accepted.

### GC-T8 — Governance change impact

Create G2 from G1 with one added required clause C5 and one changed clause C2'.

Variants:

A. reuse G1 coverage merely because G2 version label says "minor";
B. provide GovernanceChangeImpact that omits C5;
C. claim NO_QUALIFICATION_IMPACT despite changed required C2' evidence semantics;
D. valid change-impact record marks affected requirements/requalification action.

Expected A-C: REJECTED.

Expected D: structurally accepted as impact analysis; it does not itself establish G2 coverage.

### GC-T9 — Current dependency / trust-state failure

Variants:

A. BE2 revoked;
B. SC1 expired;
C. GA4 superseded/expired;
D. Operationalization Authority revoked where current validity is required;
E. stale trust-state epoch supplied after newer known epoch;
F. all current baseline dependencies valid.

Expected A-E: coverage not current / REJECTED for new qualification use.

Expected F: accepted.

### GC-T10 — GovernanceCoverageClaim summary replay

Create a previously valid summary claim.

Then revoke BE2.

Variants:

A. present only old signed GovernanceCoverageClaim;
B. present claim plus stale dependency snapshot;
C. verifier revalidates current dependencies and detects revoked BE2.

Expected A-B: insufficient/rejected for current qualification use.

Expected C: current coverage denied/stale.

### GC-T11 — Non-operationalized / claim-boundary enforcement

Variants:

A. add required broad clause C5 = "Always act ethically" with `NOT_YET_OPERATIONALIZED` and claim full required coverage;
B. same source reports partial/not-yet-operationalized coverage honestly;
C. try to convert bounded operational claims into universal moral-character assertion;
D. qualification claim states precisely that required operationalized claims C1..C4 are covered and C5 remains uncovered.

Expected A/C: REJECTED.

Expected B/D: structurally truthful bounded coverage states accepted according to policy; full coverage is not claimed.

---

## 11. Acceptance Rule

Formal success requires:

```text
GC-T0..GC-T11 = 12/12 PASS
all mandatory variants PASS
one coherent formal run
no protocol deviation
complete evidence
```

No partial credit.

No model evaluator required.

---

## 12. Deterministic Result Vocabulary

Harness SHOULD emit reason-coded states such as:

```text
COVERAGE_VALID
COVERAGE_INVALID
COVERAGE_PARTIAL
COVERAGE_STALE
CLAUSE_MISSING
UNAUTHORIZED_OPERATIONALIZATION
STRUCTURAL_CONTROL_REQUIRED
ACCEPTANCE_REQUIRED
INTERACTION_EVIDENCE_REQUIRED
GOVERNANCE_CHANGE_REQUIRES_REASSESSMENT
CLAIM_SCOPE_INFLATION
```

---

## 13. Stop Conditions

STOP rather than weaken protocol if:

- complete ClauseManifest accounting cannot be verified;
- role/coverage policy cannot prevent unauthorized weakening;
- bounded coverage extent cannot be represented/enforced;
- structural-required clauses can be satisfied behaviorally only;
- mixed/interaction dependencies cannot be verified;
- governance change impact cannot invalidate stale mappings;
- summary claims can bypass current dependency checks;
- universal claim inflation cannot be distinguished from bounded coverage.

Mechanical defects may be corrected only if protocol semantics remain unchanged.

---

## 14. Formal Evidence Requirements

Preserve:

```text
protocol artifact digest
implementation commit/build ID
working-tree state
crypto/canonicalization constants
RoleCredential/public-key digests
G1/G2 governance source digests
ClauseManifest digest
CoveragePolicy digest
OperationalizationRecord digests
PP1 digest
SC/BE/GA/IE fixture digests
TrustStateSnapshot digest/epoch
GC-T0..GC-T11 results + variants
reason codes
formal-run log
```

Historical ATE evidence remains untouched.

---

## 15. Classification Vocabulary

### `ATE_GOVERNANCE_COVERAGE_LOCAL_ESTABLISHED`
Only if 12/12 tests and all mandatory variants pass in one coherent formal run with no frozen-protocol deviation.

### `ATE_GOVERNANCE_COVERAGE_LOCAL_NOT_ESTABLISHED`
Use for genuine controlling invariant/test failure.

### `ATE_GOVERNANCE_COVERAGE_INCONCLUSIVE`
Use only when infrastructure/tool failure prevents valid determination without demonstrating a controlling invariant failure.

---

## 16. Success Claim Boundary

A successful run establishes only:

> Under the frozen deterministic local fixture profile and accepted ClauseManifest/policies, ATE governance-coverage machinery detects the enumerated omission, authority, weakening, semantic-inflation, dependency, interaction, change-impact, stale-state, and summary-replay failures.

It does not prove:

- perfect semantic decomposition of arbitrary prose;
- real agent adherence;
- moral character;
- universal alignment/safety/trustworthiness;
- production-wide governance correctness.

---

## 17. Quota Conservation

This protocol requires no live language-model calls.

Execution budget:

1. deterministic local implementation;
2. local preflight/unit tests;
3. one 12-test formal run;
4. adjudication and stop.

No Hermes, premium evaluator, multi-agent replication, or behavioral generation is required by this protocol.

---

## 18. Freeze Candidate Status

Perform one adversarial protocol review before freeze.

Focus on whether fixtures accidentally allow the same authority to weaken policy and approve its own weakening, whether ClauseManifest completeness is only self-asserted, and whether any test accidentally treats bounded coverage as proof of actual behavior.
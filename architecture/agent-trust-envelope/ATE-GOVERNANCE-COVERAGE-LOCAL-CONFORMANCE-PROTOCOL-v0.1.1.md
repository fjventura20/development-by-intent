# ATE Governance Coverage Local Conformance Protocol v0.1.1

**Status:** Revised freeze candidate — DESIGN ONLY  
**Date:** 2026-09-16  
**Program:** Agent Trust Envelope (ATE)  
**Supersedes:** `ATE-GOVERNANCE-COVERAGE-LOCAL-CONFORMANCE-PROTOCOL-v0.1.md`  
**Controlling architecture:** `ATE-GOVERNANCE-TO-EVIDENCE-MAPPING-ARCHITECTURE-v0.1.1.md`  
**Protocol review:** `ATE-GOVERNANCE-COVERAGE-PROTOCOL-ADVERSARIAL-REVIEW-v0.1.md`

---

## 1. Research Question

> **Can a deterministic local governance-coverage verifier reject incomplete, unauthorized, semantically inflated, structurally weakened, interaction-incomplete, stale, or version-mismatched governance mappings before they support an ATE qualification claim?**

This protocol tests governance mapping/coverage machinery only.

It does not evaluate actual AI behavior, moral character, alignment, or safety.

---

## 2. Lean Local Authority Profile

Use distinct signing keys / RoleCredentials for:

```text
Governance Source Authority
Clause Decomposition Authority
Governance Operationalization Authority
Governance Coverage Policy Authority
Structural Control Evidence Authority
Behavioral Evidence Authority
Governance Acceptance Authority
Qualification / Coverage Verification Authority
Trust-State Authority
```

For this protocol:

```text
OperationalizationAuthority key != CoveragePolicyAuthority key
OperationalizationAuthority role != CoveragePolicyAuthority role
TrustStateAuthority role is distinct from both
```

A single deterministic process MAY host fixture services, but keys, role credentials, and authoritative state namespaces remain distinct.

No live model invocation is required.

---

## 3. Crypto / Canonicalization

```text
signature_algorithm = Ed25519
digest_algorithm = SHA-256
canonicalization = RFC 8785 JCS
```

Unknown mandatory versions/algorithms fail closed.

---

## 4. Frozen Governance Source Fixture

Freeze source `G1` with exactly four canonical clauses:

```text
C1 — production mutation requires authorized executor path
C2 — do not falsely claim completion when authoritative execution state shows no completion
C3 — authorized instructions conflicting with high-risk policy require policy precedence / escalation
C4 — exact governance source/version must be explicitly accepted
```

The formal harness SHALL freeze:

```text
G1 source digest
expected_G1_clause_ids = [C1, C2, C3, C4]
expected_G1_clause_text_digests = [dC1, dC2, dC3, dC4]
```

This expected set is the deterministic fixture oracle for ClauseManifest completeness.

The protocol does not claim a general algorithm for perfect natural-language clause decomposition.

---

## 5. Baseline Clause Semantics

### C1

```text
clause_type = CAPABILITY_AUTHORITY
enforceability = STRUCTURALLY_ENFORCEABLE
structural_enforcement_requirement = REQUIRED
coverage_extent = EXACT_STRUCTURAL_REQUIREMENT
```

### C2

```text
clause_type = ACCOUNTABILITY_REPORTING / BEHAVIORAL_PROHIBITION
enforceability = BEHAVIORALLY_EVALUABLE
coverage_extent = BOUNDED_OPERATIONALIZATION
```

### C3

```text
clause_type = ESCALATION_HUMAN_AUTHORITY
enforceability = MIXED_STRUCTURAL_AND_BEHAVIORAL
structural_enforcement_requirement = REQUIRED
coverage_extent = COMPOSITE_BOUNDED_OPERATIONALIZATION
requires precedence/interactions under PP1
```

### C4

```text
clause_type = ACCEPTANCE_COMMITMENT
enforceability = DECLARATIVE_ACCEPTANCE_ONLY
coverage_extent = ACCEPTANCE_ONLY
```

All four are required for the baseline role/profile.

---

## 6. Baseline Coverage Policy

Freeze these rules:

- C1 MUST remain structurally required;
- C2 MUST remain behaviorally evaluable;
- C3 MUST remain mixed and requires structural + behavioral + interaction evidence;
- C4 MUST require acceptance evidence;
- no baseline clause is approved `NOT_APPLICABLE`;
- only Coverage Policy Authority may approve a high-consequence weakening/reclassification where policy permits it;
- Operationalization Authority cannot approve its own weakening merely by signing another artifact;
- C2/C3 coverage cannot be upgraded beyond their frozen bounded coverage extents;
- current dependency verification is mandatory for qualification use;
- GovernanceCoverageClaim is summary/reference evidence, not current-state authority.

---

## 7. Structured GovernanceCoverageClaim

The conformance protocol uses a structured object only:

```text
GovernanceCoverageClaim {
    claim_id
    claim_type
    governance_source_digest
    clause_manifest_digest
    coverage_manifest_digest
    covered_clause_ids[]
    uncovered_clause_ids[]
    coverage_extent_by_clause{}
    dependency_digests[]
    trust_state_epoch_ref
    issued_at
    issuer
    signature
}
```

Allowed `claim_type` values:

```text
GOVERNANCE_ACCEPTED
REQUIRED_OPERATIONALIZED_CLAIMS_COVERED
PARTIAL_OPERATIONALIZED_COVERAGE
GOVERNANCE_COVERAGE_STALE
GOVERNANCE_NOT_OPERATIONALIZED
```

Unknown/unbounded claim types fail closed.

The protocol does not parse prose labels such as "aligned," "safe," "ethical," or "integrity proven" as controlling evidence.

---

## 8. Claim-Type Validation

`REQUIRED_OPERATIONALIZED_CLAIMS_COVERED` is valid only when:

```text
all required ClauseManifest clauses accounted for
AND uncovered_required_clauses = []
AND claim coverage extents exactly equal or are weaker than OperationalizationRecord extents
AND all required structural/evidence/acceptance/interaction dependencies are current
```

`PARTIAL_OPERATIONALIZED_COVERAGE` may truthfully list uncovered clauses but cannot satisfy a policy requiring full required coverage.

`GOVERNANCE_ACCEPTED` proves acceptance only and cannot satisfy adherence/control requirements.

---

## 9. Baseline Dependency Fixtures

Use deterministic signed fixtures:

```text
SC1 = current structural-control evidence for C1
SC3 = current structural-control evidence for C3
BE2 = current bounded behavioral evidence receipt for C2
BE3 = current bounded behavioral evidence receipt for C3
GA4 = current acceptance evidence for C4
PP1 = current precedence policy
IE3 = current C3 interaction evidence binding PP1
```

All are synthetic fixtures for mapping verification only.

---

## 10. Baseline Valid Mapping

```text
C1 -> SC1
C2 -> BE2
C3 -> SC3 + BE3 + IE3 + PP1
C4 -> GA4
```

Expected baseline claim:

```text
claim_type = REQUIRED_OPERATIONALIZED_CLAIMS_COVERED
covered_clause_ids = [C1, C2, C3, C4]
uncovered_clause_ids = []
```

The claim means the frozen required operationalized claims are covered; it does not assert universal moral equivalence.

---

## 11. RoleCredential Rules

At minimum verify:

- Source Authority may issue G1;
- Decomposition Authority may issue ClauseManifest;
- Operationalization Authority may create mappings but lacks Coverage Policy approval role;
- Coverage Policy Authority may approve or deny designated weakening/reclassification decisions;
- Structural/Behavioral/Acceptance authorities may issue their fixture evidence classes only;
- Qualification/Coverage Verification Authority may verify current coverage but cannot create missing evidence;
- Trust-State Authority controls current dependency/authority status.

Role is never inferred from helper function provenance.

---

## 12. Frozen Invariants

### GC-I1 COMPLETE_CLAUSE_ACCOUNTING
Coverage reconciles to the frozen expected ClauseManifest oracle.

### GC-I2 AUTHORIZED_OPERATIONALIZATION
Mapping/reclassification obeys Operationalization and Coverage Policy RoleCredentials.

### GC-I3 POLICY_SEPARATION
Operationalization Authority cannot self-approve a policy-required weakening in this profile.

### GC-I4 BOUNDED_COVERAGE_EXTENT
Claim coverage extent cannot exceed the OperationalizationRecord.

### GC-I5 STRUCTURAL_NON_SUBSTITUTION
Required structural control cannot be replaced by behavioral evidence.

### GC-I6 ACCEPTANCE_NOT_ADHERENCE
Acceptance and adherence/control dependencies remain distinct.

### GC-I7 MIXED_COMPONENT_COMPLETENESS
Mixed clauses require all mandated components.

### GC-I8 INTERACTION_PRECEDENCE_BINDING
Required interaction evidence binds the active precedence policy.

### GC-I9 GOVERNANCE_CHANGE_IMPACT
Changed governance requires clause-aware impact handling.

### GC-I10 CURRENT_DEPENDENCY_STATE
Current coverage depends on current authoritative trust state.

### GC-I11 SUMMARY_NOT_AUTHORITY
Old summary claims cannot bypass current dependency checks.

### GC-I12 STRUCTURED_CLAIM_BOUNDING
Unknown/unbounded claim types and internally inconsistent covered/uncovered/extents fail closed.

---

## 13. Controlling Test Matrix

Freeze exactly **12 controlling tests**, GC-T0 through GC-T11.

### GC-T0 — Valid baseline coverage

Expected:

```text
COVERAGE_VALID
claim_type = REQUIRED_OPERATIONALIZED_CLAIMS_COVERED
covered = [C1,C2,C3,C4]
uncovered = []
```

All authority, dependency, extent, ClauseManifest-oracle, and current-state checks pass.

### GC-T1 — Clause omission / manifest mismatch

Variants:

A. CoverageManifest omits required C2;
B. Operationalization set lacks C3;
C. ClauseManifest source digest differs from G1;
D. CoverageManifest references wrong ClauseManifest;
E. ClauseManifest omits C4 compared with frozen expected_G1_clause_ids/text digests.

Expected: all REJECTED.

### GC-T2 — Unauthorized weakening / self-approval

Variants:

A. subject/self authority marks C1 NOT_APPLICABLE;
B. Operationalization Authority changes C1 from REQUIRED structural to behavioral-only without policy approval;
C. Operationalization Authority creates both weakened mapping and fake "approval" using its own key;
D. unauthorized authority marks C2 acceptance-only;
E. valid policy/operationalization baseline mapping.

Expected A-D: REJECTED.

Expected E: accepted.

### GC-T3 — Structured coverage-extent / claim inflation

Variants:

A. C2 OperationalizationRecord says BOUNDED but claim says EXACT_STRUCTURAL_REQUIREMENT;
B. claim_type is unknown/unbounded `UNIVERSALLY_ALIGNED`;
C. claim_type `REQUIRED_OPERATIONALIZED_CLAIMS_COVERED` while uncovered_clause_ids contains required C2;
D. claim covered_clause_ids includes clause not present in CoverageManifest;
E. exact baseline structured claim.

Expected A-D: REJECTED.

Expected E: accepted.

### GC-T4 — Structural control substituted by behavior

For C1:

A. omit SC1 but provide behavioral PASS fixture;
B. SC1 revoked/expired but behavioral fixture current;
C. current SC1.

Expected A-B: REJECTED.

Expected C: component satisfied.

### GC-T5 — Acceptance/adherence substitution

A. GA4 used instead of BE2;
B. BE2 used instead of GA4;
C. acceptance alone used for C3;
D. exact required dependency classes provided.

Expected A-C: REJECTED.

Expected D: accepted.

### GC-T6 — Mixed-clause completeness

For C3:

A. SC3 only;
B. BE3 only;
C. SC3 + BE3 without IE3;
D. SC3 + BE3 + IE3 + active PP1.

Expected A-C: REJECTED.

Expected D: satisfied.

### GC-T7 — Interaction / precedence mismatch

A. IE3 binds wrong precedence digest;
B. PP1 superseded by current PP2 but IE3 still binds PP1;
C. interaction evidence omits required conflict scenario/class reference;
D. baseline IE3 binds active PP1.

Expected A-C: REJECTED.

Expected D: accepted.

### GC-T8 — Governance change impact

Create G2 with added required C5 and changed C2'.

A. reuse G1 coverage because G2 labeled "minor";
B. GovernanceChangeImpact omits C5;
C. impact says NO_QUALIFICATION_IMPACT despite C2' semantic requirement change;
D. valid change-impact identifies C5/C2' and required requalification action.

Expected A-C: REJECTED.

Expected D: change-impact structurally valid; it does not itself establish G2 coverage.

### GC-T9 — Current dependency / authority state

A. BE2 revoked;
B. SC1 expired;
C. GA4 superseded/expired;
D. Operationalization Authority revoked where current validity required;
E. stale TrustStateSnapshot epoch supplied after newer known epoch;
F. all baseline dependencies/authorities current.

Expected A-E: current coverage denied/stale for new qualification use.

Expected F: accepted.

### GC-T10 — GovernanceCoverageClaim summary replay

Start with valid baseline summary claim, then revoke BE2.

A. old claim alone presented;
B. claim plus stale clean snapshot;
C. verifier rechecks current state and sees BE2 revoked.

Expected A-B: insufficient/rejected for current qualification use.

Expected C: current coverage result = STALE/INVALID, not covered.

### GC-T11 — Not-operationalized clause / bounded claim honesty

Add required broad clause C5 = "Always act ethically" with `NOT_YET_OPERATIONALIZED`.

A. claim_type REQUIRED_OPERATIONALIZED_CLAIMS_COVERED with C5 omitted/uncovered;
B. claim_type PARTIAL_OPERATIONALIZED_COVERAGE listing C5 uncovered;
C. unknown claim_type `MORALLY_TRUSTWORTHY`;
D. precise partial claim references C1..C4 covered, C5 uncovered.

Expected A/C: REJECTED.

Expected B/D: structurally truthful bounded claim accepted as PARTIAL, but it cannot satisfy a policy requiring full required coverage.

---

## 14. Acceptance Rule

Success requires:

```text
GC-T0..GC-T11 = 12/12 PASS
all mandatory variants PASS
one coherent formal run
no frozen-protocol deviation
complete evidence
```

No partial credit.

No live model evaluator.

---

## 15. Result Vocabulary

Recommended machine-readable reason codes include:

```text
COVERAGE_VALID
COVERAGE_PARTIAL
COVERAGE_STALE
CLAUSE_MANIFEST_INCOMPLETE
CLAUSE_MISSING
UNAUTHORIZED_OPERATIONALIZATION
COVERAGE_POLICY_APPROVAL_REQUIRED
STRUCTURAL_CONTROL_REQUIRED
ACCEPTANCE_REQUIRED
INTERACTION_EVIDENCE_REQUIRED
PRECEDENCE_POLICY_MISMATCH
GOVERNANCE_CHANGE_REQUIRES_REASSESSMENT
CLAIM_EXTENT_INFLATION
UNKNOWN_CLAIM_TYPE
CURRENT_DEPENDENCY_INVALID
```

---

## 16. Stop Conditions

STOP rather than weaken the frozen protocol if:

- ClauseManifest cannot be checked against frozen fixture oracle;
- operationalization can approve its own weakening;
- claim inflation cannot be detected structurally;
- required structural control can be behaviorally substituted;
- mixed/interaction dependencies cannot be enforced;
- current dependency checks can be bypassed by summary claims;
- governance change cannot invalidate old mappings;
- bounded/partial coverage cannot be distinguished from full required coverage.

Mechanical implementation defects may be corrected only if semantics remain unchanged.

---

## 17. Formal Evidence Requirements

Preserve:

```text
protocol artifact digest
implementation commit/build ID
working-tree state
crypto/canonicalization constants
RoleCredential/public-key digests
G1/G2 source digests
expected G1 clause ID/text-digest oracle
ClauseManifest digest
CoveragePolicy digest
OperationalizationRecord digests
structured GovernanceCoverageClaim fixtures
PP1 digest
SC/BE/GA/IE fixture digests
TrustStateSnapshot digest/epoch
GC-T0..GC-T11 + variant results
reason codes
formal-run log
```

---

## 18. Classification Vocabulary

### `ATE_GOVERNANCE_COVERAGE_LOCAL_ESTABLISHED`
Only after 12/12 controlling tests and all mandatory variants pass in one coherent formal run with no deviation.

### `ATE_GOVERNANCE_COVERAGE_LOCAL_NOT_ESTABLISHED`
Use for genuine controlling invariant/test failure.

### `ATE_GOVERNANCE_COVERAGE_INCONCLUSIVE`
Use only for infrastructure/tool failure preventing valid determination without demonstrating a controlling invariant failure.

---

## 19. Success Claim Boundary

A successful run establishes only:

> Under the frozen local fixture source, accepted ClauseManifest oracle, authority separation, and policies, ATE governance-coverage machinery detects the enumerated omission, unauthorized weakening, extent inflation, dependency substitution, interaction, change-impact, stale-state, and summary-replay failures.

It does not establish perfect semantic decomposition of arbitrary prose or actual agent behavioral adherence.

---

## 20. Quota Conservation

This protocol requires no live language-model calls.

Execution budget:

1. deterministic local implementation;
2. local unit/preflight tests;
3. one formal 12-test run;
4. adjudication and stop.

No Hermes, premium evaluator, multi-agent replication, or behavioral generation is required.

---

## 21. Freeze Candidate Status

Perform one final freeze review. If no test-meaning defect remains, freeze this exact artifact identity before any implementation.
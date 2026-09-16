# ATE Qualification & Requalification Local Conformance Protocol v0.1

**Status:** Freeze candidate — DESIGN ONLY  
**Date:** 2026-09-16  
**Program:** Agent Trust Envelope (ATE)  
**Controlling architecture:** `ATE-AGENT-QUALIFICATION-REQUALIFICATION-ARCHITECTURE-v0.1.1.md`  
**Architecture review:** `ATE-AGENT-QUALIFICATION-REQUALIFICATION-FINAL-REVIEW-v0.1.md`

---

## 1. Research Question

> **Can a deterministic local qualification verifier distinguish a currently valid, active, properly scoped agent qualification from stale, copied, profile-mismatched, policy-rolled-back, issuer-overreach, evidence-expired, capability-expanded, governance-mismatched, or improperly requalified qualification contexts?**

This protocol tests the qualification architecture itself.

It does **not** test whether an AI model is behaviorally competent or aligned. Behavioral evaluation receipts are deterministic signed fixtures.

---

## 2. Experimental Boundary

The harness SHALL use one local trust domain and fixed deterministic fixtures for:

- Qualification Definition Authority;
- Qualification Authority;
- Evaluator Authority A;
- optional independent Evaluator Authority B;
- Qualification Status / Trust-State Authority;
- Requalification Policy Authority;
- one qualified subject principal;
- one alternate principal;
- one baseline qualified runtime profile;
- one or more changed profiles;
- one local trusted clock.

No external network is required.

No model inference is required.

No premium evaluator is required.

No multi-agent behavioral generation is required.

---

## 3. Explicit Non-Claims

A successful run does not establish:

- actual model competence;
- Value Architecture effectiveness;
- moral reasoning;
- correctness of any real behavioral evaluator;
- resistance to issuer/root compromise;
- distributed trust-state consistency;
- remote attestation;
- production PKI;
- enforcement of protected actions;
- full P2 runtime trust establishment.

The success claim is limited to deterministic qualification semantics.

---

## 4. Frozen Cryptographic / Serialization Profile

```text
signature_algorithm = Ed25519
digest_algorithm = SHA-256
canonicalization = RFC 8785 JCS
```

All signed artifacts include:

```text
artifact_type
artifact_version
issuer_id / signer_id
signature_algorithm
```

Unknown mandatory versions/algorithms fail closed.

---

## 5. Frozen Namespace

Implementation SHALL freeze literal values before formal run for:

```text
trust_domain_id
project_scope
qualification_class_id
role_id
policy_epoch
status_registry_epoch
```

Evidence SHALL record them.

---

## 6. Minimal Fixture Artifacts

### 6.1 QualificationDefinition

Required fields:

```text
qualification_class_id
qualification_definition_version
trust_domain_id
role_id
permitted_capability_classes[]
prohibited_capability_classes[]
maximum_risk_class
minimum_assurance_profile
required_profile_digest
required_governance_digests
required_evidence_rules[]
required_evaluator_rules[]
requalification_policy_digest
policy_epoch
maximum_qualification_validity
qualification_definition_authority_id
signature
```

### 6.2 QualifiedRuntimeProfile

Required fields:

```text
qualified_profile_id
subject_principal_id
software_manifest_digest
model_identity
configuration_profile_digest
tool_capability_profile_digest
resource_permission_class
network_access_class
coa_digest
value_architecture_digest
policy_bundle_digest
assurance_tier
key_protection_assurance
trust_domain_id
project_scope
```

Canonical digest = `qualified_profile_digest`.

### 6.3 BehavioralEvidenceReceipt

Deterministic fixture:

```text
evidence_receipt_id
subject_principal_id
qualified_profile_digest
evaluation_protocol_digest
evidence_class
lifecycle_class
result = PASS
created_at
not_before
valid_until?
refresh_due_at?
evaluator_id
signature
```

### 6.4 QualificationEvidencePackage

```text
evidence_package_id
qualification_class_id
qualification_definition_version
qualified_profile_digest
evidence_receipt_digests[]
evaluator_identities[]
compatibility_decision_digests[]?
waiver_digests[]?
created_at
```

Canonical digest = `evidence_package_digest`.

### 6.5 QualificationCredential

```text
qualification_id
qualification_class_id
qualification_definition_version
subject_principal_id
qualified_profile_digest
evidence_package_digest
trust_domain_id
project_scope
permitted_capability_classes[]
maximum_risk_class
minimum_assurance_profile
requalification_policy_digest
policy_epoch
issued_at
not_before
valid_until
qualification_issuer_id
signature
```

### 6.6 QualificationStatusState

```text
qualification_id
status
status_epoch
registry_epoch
trust_domain_id
updated_at
reason_code
superseding_qualification_id?
status_authority_id
signature
```

Allowed status:

```text
ACTIVE
SUSPENDED
REQUALIFICATION_REQUIRED
EXPIRED
SUPERSEDED
REVOKED
NOT_QUALIFIED
```

### 6.7 RequalificationPolicy

```text
requalification_policy_id
version
digest
policy_epoch
change_rules[]
issuer_id
signature
```

### 6.8 QualificationCompatibility

```text
source_qualification_id
source_profile_digest
target_profile_digest or bounded_change_predicate
qualification_class_id
preserved_evidence_classes[]
invalidated_evidence_classes[]
required_delta_evaluations[]
preserved_maximum_risk_class
preserved_capability_scope
preserved_assurance_ceiling
project_scope
requalification_policy_digest
policy_epoch
valid_until
issuer_id
signature
```

### 6.9 EvidencePreservationDecision

Used for partial requalification:

```text
source_evidence_digest
source_profile_digest
target_profile_digest
changed_dimensions[]
non_interference_basis
compatibility_decision_digest
issuer_id
signature
```

### 6.10 QualificationVerificationContext

Input request to verifier:

```text
subject_principal_id
qualified_profile_digest
trust_domain_id
project_scope
requested_role
requested_capability_class
requested_risk_class
required_assurance_profile
current_governance_digests
current_policy_epoch
known_status_registry_epoch
```

---

## 7. Evidence Lifecycle Fixtures

The formal harness SHALL include at least one receipt of each lifecycle class:

```text
ISSUANCE_SNAPSHOT
CONTINUOUSLY_CURRENT
PERIODICALLY_REFRESHED
```

Semantics:

### `ISSUANCE_SNAPSHOT`
Must have been valid at qualification issuance. Aging after issuance alone does not invalidate the qualification.

### `CONTINUOUSLY_CURRENT`
Must remain valid now. Expiry/revocation invalidates qualification use.

### `PERIODICALLY_REFRESHED`
Must have current refresh evidence by `refresh_due_at`; missed refresh makes qualification unusable according to policy.

---

## 8. Issuer Authority Fixtures

Qualification issuer authorization SHALL itself be bounded by a signed role/ceiling fixture:

```text
may_issue_qualification_classes[]
maximum_risk_class
maximum_assurance_tier
permitted_trust_domains[]
permitted_project_scopes[]
permitted_capability_classes[]
maximum_validity
may_issue_compatibility_declarations
may_suspend
may_revoke
```

A valid Ed25519 signature outside these ceilings fails verification.

---

## 9. Evaluator Rule Fixtures

The Qualification Definition SHALL include rules sufficient to test:

```text
accepted_evaluator_authorities[]
self_evaluation_allowed
minimum_independent_evaluators
replication_required
```

At least one evidence class SHALL require an independent evaluator and reject subject-controlled/self-issued evidence.

---

## 10. Qualification Verification Algorithm

Verifier SHALL, at minimum:

1. parse all mandatory artifacts;
2. validate artifact type/version/algorithm;
3. canonicalize deterministically;
4. verify Qualification Definition signature/current policy epoch;
5. verify QualifiedRuntimeProfile digest;
6. verify QualificationCredential signature;
7. verify qualification issuer role/ceilings;
8. verify credential time validity;
9. verify subject/profile/trust-domain/project binding;
10. verify role/capability/risk/assurance scope;
11. verify evidence package digest and contents;
12. verify required evidence receipt signatures/authorities;
13. verify evaluator independence/replication rules;
14. apply evidence lifecycle semantics;
15. verify current QualificationStatusState and monotonic registry/status epoch;
16. reject non-ACTIVE status;
17. verify current requalification policy digest/epoch;
18. verify current governance compatibility;
19. determine whether profile/change requires re-attestation, partial requalification, or full requalification;
20. if compatibility is used, verify non-expansion and exact source/target bindings;
21. if partial requalification preserves evidence, verify EvidencePreservationDecision for every preserved class;
22. emit deterministic result and reason codes.

Successful output is:

```text
QUALIFICATION_VALID_FOR_CONTEXT
```

This is **not** an action authorization.

---

## 11. Frozen Invariants Under Test

### QP-I1 EXACT_SUBJECT_PROFILE
Credential must bind exact subject/profile/context.

### QP-I2 CURRENT_STATUS
Historical ACTIVE credential cannot override newer non-ACTIVE status.

### QP-I3 MONOTONIC_TRUST_STATE
Known newer registry/status epoch cannot be rolled back.

### QP-I4 EVIDENCE_LIFECYCLE
Each evidence class obeys explicit lifecycle semantics.

### QP-I5 ISSUER_CEILINGS
Valid signatures outside issuer ceilings are rejected.

### QP-I6 EVALUATOR_RULES
Required evaluator authority/independence/replication is enforced.

### QP-I7 RISK_ASSURANCE_SCOPE
Qualification cannot satisfy higher risk or assurance than qualified.

### QP-I8 CAPABILITY_NON_EXPANSION
Qualification/compatibility cannot silently widen capability scope.

### QP-I9 GOVERNANCE_BINDING
Current governance must satisfy qualification compatibility rules.

### QP-I10 POLICY_ROLLBACK_PROTECTION
Old requalification policy cannot be selected to weaken change handling.

### QP-I11 COMPATIBILITY_BOUNDING
Compatibility applies only to exact source/target/bounded change and cannot expand qualification.

### QP-I12 PARTIAL_REQUALIFICATION_JUSTIFICATION
Preserved evidence requires explicit signed non-interference/dependency decision.

### QP-I13 REATTESTATION_DISTINCTION
Profile-preserving restart/instance renewal does not require full requalification.

### QP-I14 SEPARATION_FROM_AUTHORIZATION
Successful qualification verification produces eligibility only, not executable authority.

### QP-I15 LINEAGE_SUPERSESSION
New qualification can supersede old while preserving audit lineage; superseded credential cannot be current when active-only policy applies.

---

## 12. Frozen Controlling Test Matrix

The protocol freezes **15 deterministic controlling tests**.

Each test may contain multiple mandatory variants.

### QP-T0 — Valid active qualification

Baseline valid profile/evidence/credential/current ACTIVE state/current policy.

Expected:

```text
QUALIFICATION_VALID_FOR_CONTEXT
```

### QP-T1 — Qualification is not authorization

Feed valid qualification result to a stub authorization boundary without action-specific authorization.

Expected:

```text
NO_EXECUTION_AUTHORITY
```

No capability token/trust decision is produced by the qualification verifier.

### QP-T2 — Credential copying / subject-profile mismatch

Variants:

A. valid credential presented for alternate principal;
B. valid credential with changed qualified profile.

Expected: both rejected.

### QP-T3 — Current status and rollback

Variants:

A. old ACTIVE credential + newer SUSPENDED status;
B. old ACTIVE credential + newer REVOKED status;
C. older status/registry epoch replayed after verifier knows newer epoch.

Expected: all rejected.

### QP-T4 — Evidence lifecycle semantics

Variants:

A. aged `ISSUANCE_SNAPSHOT` remains acceptable when policy permits and issuance-time validity was satisfied;
B. expired `CONTINUOUSLY_CURRENT` evidence rejected;
C. missed `PERIODICALLY_REFRESHED` deadline rejected/suspended as defined.

### QP-T5 — Re-attestation distinction

Normal runtime restart/instance renewal with byte-identical qualified profile.

Expected:

```text
RE_ATTESTATION_REQUIRED
```

and **not** `FULL_REQUALIFICATION_REQUIRED`.

After fresh instance attestation fixture, existing ACTIVE qualification remains usable.

### QP-T6 — Material software/model change

Variants:

A. changed software manifest digest;
B. changed model identity/digest.

Without explicit compatibility:

```text
FULL_REQUALIFICATION_REQUIRED
```

### QP-T7 — Capability/risk/assurance expansion

Variants:

A. request capability outside credential;
B. requested risk exceeds ceiling;
C. required assurance exceeds qualified assurance.

Expected: rejected / requalification required, never silently widened.

### QP-T8 — Governance substitution

Change CoA, Value Architecture, or policy digest outside explicit compatibility.

Expected:

```text
REQUALIFICATION_REQUIRED
```

Current-session acceptance alone MUST NOT make the old qualification cover the changed profile.

### QP-T9 — Compatibility non-expansion

A. valid bounded compatibility with required delta evidence -> accepted for target profile;
B. compatibility attempts to increase capability/risk/assurance/project scope -> rejected;
C. wrong source or target profile -> rejected.

### QP-T10 — Partial requalification evidence preservation

A. every preserved evidence class has signed EvidencePreservationDecision -> eligible after required delta evaluation;
B. one preserved class lacks justification -> rejected.

### QP-T11 — Qualification issuer ceilings

Use valid Qualification Authority signature to issue credential outside authorized class/risk/capability/project ceiling.

Expected:

```text
REJECTED: ISSUER_CEILING
```

### QP-T12 — Evaluator authority and independence

Variants:

A. accepted independent evaluator evidence -> passes evaluator gate;
B. subject/self-issued evidence where self-evaluation forbidden -> rejected;
C. insufficient independent evaluator count where replication required -> rejected.

### QP-T13 — Requalification-policy rollback

Present older correctly signed requalification policy that permits cheaper handling of a material change after verifier knows newer policy epoch.

Expected:

```text
REJECTED: POLICY_ROLLBACK
```

### QP-T14 — Cross-project reuse, supersession, and lineage

Variants:

A. credential from Project A used in Project B without portability -> rejected;
B. old credential after SUPERSEDED state -> rejected under active-only policy;
C. new qualification references predecessor/evidence lineage -> accepted when otherwise valid.

---

## 13. Acceptance Rule

Formal success requires:

```text
QP-T0..QP-T14 = 15/15 PASS
all mandatory variants PASS
no protocol deviation
complete evidence
```

No partial credit.

No model judgment.

No combining results across formal runs.

---

## 14. Deterministic Reason Codes

Implementation SHOULD use stable reason codes including at least:

```text
QX_BAD_SIGNATURE
QX_UNKNOWN_VERSION
QX_ISSUER_UNAUTHORIZED
QX_ISSUER_CEILING
QX_SUBJECT_MISMATCH
QX_PROFILE_MISMATCH
QX_SCOPE_MISMATCH
QX_RISK_CEILING
QX_ASSURANCE_INSUFFICIENT
QX_STATUS_NOT_ACTIVE
QX_STATUS_ROLLBACK
QX_EVIDENCE_EXPIRED
QX_EVIDENCE_REFRESH_MISSED
QX_EVALUATOR_UNAUTHORIZED
QX_EVALUATOR_INDEPENDENCE
QX_GOVERNANCE_MISMATCH
QX_REQUALIFICATION_REQUIRED
QX_COMPATIBILITY_EXPANSION
QX_COMPATIBILITY_MISMATCH
QX_PRESERVATION_UNJUSTIFIED
QX_POLICY_ROLLBACK
QX_CROSS_PROJECT
QX_SUPERSEDED
```

---

## 15. Formal Run Discipline

A valid run requires:

- exact frozen protocol digest;
- one identified implementation commit;
- clean working tree at start;
- frozen deterministic fixture set/digest;
- frozen authority public keys and ceilings;
- frozen Qualification Definition;
- frozen Requalification Policy;
- one coherent run of all 15 tests;
- machine-readable PASS/FAIL/reason codes;
- all variants executed;
- no test weakening after failure.

---

## 16. Evidence Requirements

Formal evidence SHALL preserve:

```text
protocol SHA-256
implementation commit SHA
working-tree state
fixture bundle digest
Qualification Definition digest
Requalification Policy digest/epoch
issuer/evaluator/status-authority public keys + role ceilings
baseline QualifiedRuntimeProfile digest
baseline evidence-package digest
baseline qualification credential digest
status-state / registry epoch
QP-T0..T14 results and variants
reason codes
formal-run log
```

Historical P1/P2 artifacts remain untouched.

---

## 17. Stop Conditions

STOP rather than weaken protocol if:

- historical ACTIVE credential can override current non-ACTIVE status;
- qualification can be copied to another subject/profile;
- compatibility can expand qualification;
- issuer ceiling cannot be enforced;
- evaluator independence rule cannot be represented/verified;
- evidence lifecycle cannot be enforced deterministically;
- policy rollback cannot be rejected;
- partial requalification cannot justify preserved evidence;
- qualification verification itself grants action authority;
- any frozen invariant requires redesign.

Mechanical implementation defects may be corrected only when preserving the frozen protocol.

---

## 18. Classification Vocabulary

### `ATE_QUALIFICATION_LOCAL_CONFORMANCE_ESTABLISHED`
Only if 15/15 tests and all variants pass in one coherent formal run with no protocol deviation.

### `ATE_QUALIFICATION_LOCAL_CONFORMANCE_NOT_ESTABLISHED`
Use for genuine controlling invariant/test failure.

### `ATE_QUALIFICATION_LOCAL_CONFORMANCE_INCONCLUSIVE`
Use only when infrastructure/tool failure prevents valid determination without demonstrating an invariant failure.

---

## 19. Success Claim Boundary

A successful result establishes only:

> Under the frozen local deterministic fixture model, the ATE qualification verifier correctly enforces the specified subject/profile binding, current-status, evidence-lifecycle, issuer/evaluator authority, risk/assurance, compatibility, requalification, policy-rollback, and lineage semantics.

It does not establish that any real AI agent deserves qualification.

---

## 20. Quota Conservation

This protocol is intentionally cheap.

It requires:

- deterministic fixture generation;
- local cryptographic verification;
- one development/preflight phase;
- one formal 15-test run;
- no language-model evaluator;
- no Hermes reasoning loop;
- no candidate generation;
- no blind scoring;
- no statistical replication.

Behavioral evaluation itself is a separate future evidence-production concern.

---

## 21. Freeze Candidate

No implementation is authorized until an adversarial protocol review confirms this exact test matrix covers the architecture's controlling failure modes and a freeze record captures the immutable protocol artifact.
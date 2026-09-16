# ATE Qualification & Requalification Local Conformance Protocol v0.1.1

**Status:** Revised freeze candidate — DESIGN ONLY  
**Date:** 2026-09-16  
**Program:** Agent Trust Envelope (ATE)  
**Supersedes:** `ATE-QUALIFICATION-REQUALIFICATION-LOCAL-CONFORMANCE-PROTOCOL-v0.1.md`  
**Controlling architecture:** `ATE-AGENT-QUALIFICATION-REQUALIFICATION-ARCHITECTURE-v0.1.1.md`  
**Protocol review:** `ATE-QUALIFICATION-REQUALIFICATION-PROTOCOL-ADVERSARIAL-REVIEW-v0.1.md`

---

## 1. Research Question

> **Can a deterministic local qualification verifier enforce current, scoped, evidence-backed qualification semantics and correctly require re-attestation, partial requalification, or full requalification when the subject/runtime/profile/policy context changes?**

The protocol tests qualification semantics only.

It does not evaluate real model competence or behavioral alignment.

---

## 2. Local Test Profile

Use one deterministic local trust domain with fixed fixtures for:

- Qualification Definition Authority;
- Qualification Authority;
- Evaluator Authority A;
- independent Evaluator Authority B;
- Qualification Status / Trust-State Authority;
- Requalification Policy Authority;
- one baseline subject principal;
- one alternate principal;
- one baseline qualified runtime profile;
- one or more changed runtime profiles;
- deterministic `VerifiedRuntimeContext` fixtures;
- one trusted local clock.

No network, model inference, premium evaluator, multi-agent generation, or statistical scoring is required.

---

## 3. Explicit Non-Claims

Success does not establish:

- actual AI competence;
- Value Architecture effectiveness;
- moral reasoning;
- behavioral evaluator correctness;
- root/issuer compromise resistance;
- distributed revocation consistency;
- remote attestation;
- production PKI;
- protected-resource enforcement;
- full P2 runtime-trust correctness.

---

## 4. Frozen Crypto / Serialization

```text
signature_algorithm = Ed25519
digest_algorithm = SHA-256
canonicalization = RFC 8785 JCS
```

Unknown mandatory artifact versions/algorithms fail closed.

---

## 5. Frozen Local Policy

Before formal run freeze literal values for:

```text
trust_domain_id
project_scope
qualification_class_id
role_id
current_qualification_definition_version
current_qualification_definition_digest
current_requalification_policy_version
current_requalification_policy_digest
current_policy_epoch
current_status_registry_epoch
```

Local protocol also freezes:

```text
waivers_permitted = false
```

Therefore:

```text
waiver_digests = []
```

for all valid formal fixtures.

Unexpected waiver use fails closed as unsupported in this profile.

---

## 6. Minimal Artifacts

### 6.1 QualificationDefinition

```text
qualification_class_id
qualification_definition_version
qualification_definition_digest
trust_domain_id
role_id
permitted_capability_classes[]
prohibited_capability_classes[]
maximum_risk_class
minimum_assurance_profile
required_profile_constraints
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

Deterministic signed fixture:

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
preservation_decision_digests[]?
waiver_digests[] = []
created_at
```

Canonical digest = `evidence_package_digest`.

Digest mismatch fails closed.

### 6.5 QualificationCredential

```text
qualification_id
qualification_class_id
qualification_definition_version
qualification_definition_digest
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
previous_qualification_id?
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

Status authority must itself be authorized by frozen trust policy.

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

A compatibility declaration **never modifies the subject/profile binding of the source credential**.

It can only define a reduced requalification path that culminates in a **new qualification decision and new qualification credential for the target profile**.

### 6.9 EvidencePreservationDecision

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

### 6.10 VerifiedRuntimeContext Fixture

This protocol consumes deterministic runtime-context fixtures rather than rerunning P2.

Minimum fields:

```text
principal_id
runtime_instance_id
qualified_profile_digest
trust_domain_id
project_scope
software_manifest_digest
configuration_profile_digest
model_identity
coa_digest
value_architecture_digest
policy_bundle_digest
assurance_tier
verified_at
context_digest
```

A restart fixture may change `runtime_instance_id` while preserving `qualified_profile_digest`.

### 6.11 QualificationVerificationRequest

```text
verified_runtime_context_digest
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

## 7. Evidence Lifecycle Classes

Every controlling evidence receipt is assigned exactly one:

```text
ISSUANCE_SNAPSHOT
CONTINUOUSLY_CURRENT
PERIODICALLY_REFRESHED
```

### ISSUANCE_SNAPSHOT
Must have been valid at issuance. Later age alone does not invalidate qualification when policy explicitly permits snapshot semantics.

### CONTINUOUSLY_CURRENT
Must be valid now. Expiry/revocation makes qualification unusable.

### PERIODICALLY_REFRESHED
Must have valid refresh evidence by the required deadline. Missed refresh causes deterministic fail-closed status/action.

Credential time validity is always checked independently of status.

A stale ACTIVE status cannot rescue an expired credential.

---

## 8. Issuer Authority Ceilings

Qualification Authority authorization fixture includes:

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

Verifier checks both signature and ceiling compliance.

---

## 9. Evaluator Rules

At least one required evidence class freezes:

```text
accepted_evaluator_authorities[]
self_evaluation_allowed = false
minimum_independent_evaluators = 1 or 2
replication_required = true/false
```

The fixture set must support both valid independent evidence and invalid self-issued/insufficient-replication cases.

---

## 10. Qualification Verification Procedure

Verifier SHALL:

1. parse mandatory artifacts;
2. validate type/version/algorithm;
3. canonicalize deterministically;
4. verify current Qualification Definition authority/signature/digest/version;
5. reject known superseded/rolled-back Qualification Definition;
6. verify QualifiedRuntimeProfile digest;
7. verify QualificationCredential signature;
8. verify issuer role and ceilings including `maximum_validity`;
9. verify credential `not_before`/`valid_until`;
10. verify subject/profile/trust-domain/project binding against `VerifiedRuntimeContext` and request;
11. verify role/capability/risk/assurance scope;
12. verify evidence package digest and required contents;
13. reject unexpected waiver use;
14. verify evidence receipts and evaluator authority/independence/replication;
15. apply evidence lifecycle semantics;
16. verify current QualificationStatusState signature/authority/registry epoch;
17. reject non-ACTIVE status or trust-state rollback;
18. verify current RequalificationPolicy signature/digest/version/epoch;
19. reject requalification-policy rollback;
20. verify governance compatibility;
21. evaluate any profile change using the frozen change policy;
22. if compatibility is used, verify exact source/target, non-expansion, validity, and policy epoch;
23. if partial requalification is permitted, require EvidencePreservationDecision for every preserved evidence class;
24. require new qualification decision/credential for every changed target profile that remains qualified after partial/full requalification;
25. emit deterministic result/reason codes.

Possible change-assessment outcomes:

```text
NO_QUALIFICATION_IMPACT
RE_ATTESTATION_REQUIRED
PARTIAL_REQUALIFICATION_REQUIRED
FULL_REQUALIFICATION_REQUIRED
IMMEDIATE_SUSPENSION
```

Successful current-context verification produces only:

```text
QUALIFICATION_VALID_FOR_CONTEXT
```

It never produces execution authority.

---

## 11. Frozen Invariants

### QP-I1 EXACT_SUBJECT_PROFILE
Exact subject/profile/runtime-context binding.

### QP-I2 CURRENT_STATUS
Historical ACTIVE credential cannot override newer non-ACTIVE status.

### QP-I3 MONOTONIC_TRUST_STATE
Known newer registry/status epoch cannot be rolled back.

### QP-I4 EVIDENCE_LIFECYCLE
Explicit lifecycle semantics are enforced.

### QP-I5 ISSUER_CEILINGS
Issuer cannot exceed class/capability/risk/assurance/scope/validity ceilings.

### QP-I6 EVALUATOR_RULES
Evaluator authority/independence/replication enforced.

### QP-I7 RISK_ASSURANCE_SCOPE
No use above qualified risk/assurance bounds.

### QP-I8 CAPABILITY_NON_EXPANSION
No silent capability widening.

### QP-I9 GOVERNANCE_BINDING
Current governance must be compatible with qualified governance.

### QP-I10 POLICY_AND_DEFINITION_ROLLBACK_PROTECTION
Old requalification policy or superseded qualification definition cannot weaken current requirements.

### QP-I11 COMPATIBILITY_IS_REQUALIFICATION_PATH
Compatibility never mutates old credential; changed profile requires new qualification credential.

### QP-I12 PARTIAL_REQUALIFICATION_JUSTIFICATION
Preserved evidence requires signed non-interference/dependency decision.

### QP-I13 REATTESTATION_LAYER_SEPARATION
Profile-preserving runtime restart consumes a fresh `VerifiedRuntimeContext`; qualification protocol does not rerun P2.

### QP-I14 SEPARATION_FROM_AUTHORIZATION
Qualification result is eligibility only.

### QP-I15 LINEAGE_SUPERSESSION
New credential preserves predecessor lineage; superseded credential is not current under active-only policy.

### QP-I16 NO_WAIVERS_LOCAL_PROFILE
Formal local profile contains no waiver path.

---

## 12. Frozen 15-Test Matrix

### QP-T0 — Valid active qualification

Valid `VerifiedRuntimeContext`, profile, definition, evidence package, credential, ACTIVE status, and current policy.

Expected:

```text
QUALIFICATION_VALID_FOR_CONTEXT
```

### QP-T1 — Qualification is not authorization

Provide valid qualification result to authorization stub without action-specific authorization.

Expected:

```text
NO_EXECUTION_AUTHORITY
```

### QP-T2 — Copied credential / subject-profile mismatch

Variants:

A. valid credential used for alternate principal;
B. valid credential paired with changed profile/context;
C. evidence-package digest altered.

Expected: all rejected.

### QP-T3 — Current status and rollback

Variants:

A. old ACTIVE credential + newer SUSPENDED status;
B. old ACTIVE credential + newer REVOKED status;
C. replay older status/registry epoch after newer epoch known;
D. credential expired while status still ACTIVE.

Expected: all rejected.

### QP-T4 — Evidence lifecycle

Variants:

A. aged but valid-at-issuance `ISSUANCE_SNAPSHOT` accepted when definition permits;
B. expired `CONTINUOUSLY_CURRENT` evidence rejected;
C. missed `PERIODICALLY_REFRESHED` deadline rejected/suspended per policy.

### QP-T5 — Re-attestation distinction via runtime-context fixtures

Use runtime context A and restarted context B:

```text
A.runtime_instance_id != B.runtime_instance_id
A.qualified_profile_digest == B.qualified_profile_digest
```

Expected change assessment:

```text
RE_ATTESTATION_REQUIRED
```

Once fresh B `VerifiedRuntimeContext` exists, existing ACTIVE qualification remains applicable without behavioral requalification.

### QP-T6 — Material software/model change

Variants:

A. changed software digest;
B. changed model identity/digest.

No compatibility fixture.

Expected:

```text
FULL_REQUALIFICATION_REQUIRED
```

### QP-T7 — Capability/risk/assurance expansion

Variants:

A. capability outside credential;
B. risk above ceiling;
C. assurance above qualified tier.

Expected: rejected / requalification required; never widened.

### QP-T8 — Governance substitution

Change CoA, VA, or policy digest outside explicit compatibility.

Expected:

```text
REQUALIFICATION_REQUIRED
```

Fresh session acceptance alone does not mutate old qualification scope.

### QP-T9 — Compatibility is bounded requalification path

Variants:

A. valid bounded compatibility correctly classifies target as `PARTIAL_REQUALIFICATION_REQUIRED`;
B. compatibility attempts scope/risk/assurance/capability expansion -> rejected;
C. wrong source/target profile -> rejected;
D. after required delta evidence, a **new** target-profile qualification credential with predecessor lineage verifies;
E. old source credential presented directly for target profile remains rejected.

### QP-T10 — Partial requalification evidence preservation

Variants:

A. each preserved evidence class has valid EvidencePreservationDecision and new target credential -> accepted when all other conditions pass;
B. one preserved class lacks justification -> rejected;
C. target continues using source credential instead of new credential -> rejected.

### QP-T11 — Qualification issuer ceilings

Variants using otherwise valid signatures:

A. credential outside permitted qualification class;
B. risk/capability/project ceiling exceeded;
C. assurance ceiling exceeded;
D. credential validity duration exceeds `maximum_validity`.

Expected:

```text
REJECTED: ISSUER_CEILING
```

### QP-T12 — Evaluator authority and independence

Variants:

A. valid required independent evaluator evidence;
B. self-issued evidence where forbidden;
C. insufficient evaluator count when replication required.

Expected A pass evaluator gate; B/C rejected.

### QP-T13 — Policy and qualification-definition rollback

Variants:

A. old signed RequalificationPolicy after newer policy epoch known;
B. old/superseded signed QualificationDefinition after newer authoritative definition known.

Expected:

```text
REJECTED: ROLLBACK
```

### QP-T14 — Cross-project reuse, supersession, lineage, unsupported waiver

Variants:

A. Project A credential used in Project B without portability -> rejected;
B. old credential after SUPERSEDED current state -> rejected;
C. new replacement credential points to predecessor/evidence lineage -> valid when otherwise correct;
D. unexpected non-empty `waiver_digests` in local profile -> rejected.

---

## 13. Acceptance Rule

Formal success requires:

```text
QP-T0..QP-T14 = 15/15 PASS
all mandatory variants PASS
no frozen-protocol deviation
complete evidence
```

No partial credit.

No result combining across runs.

---

## 14. Stable Reason Codes

At minimum:

```text
QX_BAD_SIGNATURE
QX_UNKNOWN_VERSION
QX_ISSUER_UNAUTHORIZED
QX_ISSUER_CEILING
QX_SUBJECT_MISMATCH
QX_PROFILE_MISMATCH
QX_EVIDENCE_PACKAGE_MISMATCH
QX_SCOPE_MISMATCH
QX_RISK_CEILING
QX_ASSURANCE_INSUFFICIENT
QX_STATUS_NOT_ACTIVE
QX_STATUS_ROLLBACK
QX_CREDENTIAL_EXPIRED
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
QX_DEFINITION_ROLLBACK
QX_CROSS_PROJECT
QX_SUPERSEDED
QX_WAIVER_UNSUPPORTED
```

---

## 15. Formal Run Discipline

A valid formal run requires:

- exact frozen protocol digest;
- one implementation commit;
- clean working tree at start;
- frozen fixture bundle digest;
- frozen authority keys/roles/ceilings;
- frozen Qualification Definition;
- frozen Requalification Policy;
- frozen status registry epoch baseline;
- one coherent run of all 15 tests;
- machine-readable results/reason codes;
- all variants executed;
- no test weakening after failure.

---

## 16. Evidence Requirements

Preserve:

```text
protocol SHA-256
implementation commit SHA
working-tree status
fixture bundle digest
Qualification Definition digest/version
Requalification Policy digest/version/epoch
issuer/evaluator/status-authority keys + role ceilings
baseline QualifiedRuntimeProfile digest
baseline VerifiedRuntimeContext digest
baseline evidence-package digest
baseline qualification credential digest
status-state / registry epoch
QP-T0..T14 results + variants
reason codes
formal-run log
```

Historical P1/P2 artifacts remain unchanged.

---

## 17. Stop Conditions

STOP rather than weaken protocol if:

- old credential can apply to changed target profile without new qualification;
- historical ACTIVE status overrides newer non-ACTIVE state;
- credential copying crosses subject/profile boundary;
- compatibility expands qualification;
- issuer ceilings cannot be enforced;
- evaluator rules cannot be verified;
- lifecycle semantics cannot be deterministic;
- policy/definition rollback cannot be rejected;
- preserved evidence lacks explicit justification;
- qualification result itself grants action authority;
- any frozen invariant requires redesign.

Mechanical defects may be corrected only when preserving the frozen protocol.

---

## 18. Classification Vocabulary

### `ATE_QUALIFICATION_LOCAL_CONFORMANCE_ESTABLISHED`
15/15 tests and all variants pass in one coherent formal run, no deviation.

### `ATE_QUALIFICATION_LOCAL_CONFORMANCE_NOT_ESTABLISHED`
A genuine controlling invariant/test failure occurs.

### `ATE_QUALIFICATION_LOCAL_CONFORMANCE_INCONCLUSIVE`
Infrastructure/tool failure prevents valid determination without demonstrating invariant failure.

---

## 19. Success Claim Boundary

Success establishes only:

> Under the frozen local deterministic fixture model, ATE qualification logic correctly enforces current subject/profile/status/evidence/policy/issuer/evaluator/scope/requalification semantics and keeps qualification separate from action authorization.

It does not establish that any real AI agent is competent or trustworthy.

---

## 20. Quota Conservation

Expected execution cost is local computation only:

- deterministic fixture generation;
- cryptographic verification;
- preflight/unit tests;
- one formal 15-test run;
- no language-model evaluator;
- no multi-agent replication;
- no repeated generations.

---

## 21. Freeze Candidate Status

This v0.1.1 incorporates all findings from the protocol adversarial review while preserving the 15-test lean boundary.

No implementation is authorized until a final freeze record captures the immutable artifact identity.
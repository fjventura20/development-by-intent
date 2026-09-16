# ATE Evidence Integrity Local Conformance Protocol v0.1.1

**Status:** Revised freeze candidate — DESIGN ONLY  
**Date:** 2026-09-16  
**Program:** Agent Trust Envelope (ATE)  
**Supersedes:** `ATE-EVIDENCE-INTEGRITY-LOCAL-CONFORMANCE-PROTOCOL-v0.1.md`  
**Controlling architecture:** `ATE-BEHAVIORAL-FUNCTIONAL-EVIDENCE-ARCHITECTURE-v0.1.1.md` + normative amendment `v0.1.2.md`  
**Protocol review:** `ATE-EVIDENCE-INTEGRITY-PROTOCOL-ADVERSARIAL-REVIEW-v0.1.md`

---

## 1. Research Question

> **Can a deterministic local evidence verifier distinguish a valid preregistered, completely accounted, independently cross-checked, correctly scoped evidence chain from specified post-hoc, incomplete, tampered, misbound, stale, unauthorized, or selectively reported evidence chains before admission into a Qualification Evidence Package?**

The protocol tests evidence-integrity machinery only.

It does not evaluate actual AI behavior, competence, alignment, or Value Architecture effectiveness.

---

## 2. Lean Local Profile

Use one deterministic local trust domain with logically distinct fixture authorities for:

```text
Protocol Authority
Precommitment Registry Authority
Runner Authority
Synthetic Evaluator Authority
Evidence Issuer
Qualification / Package Admission Authority
Trust-State Authority
```

Each role SHALL have a distinct signing key except where a future protocol explicitly tests authorized role combination.

For this v0.1.1 protocol:

```text
Precommitment Registry Authority key != Runner key
Precommitment Registry Authority role != Runner role
```

The same local process MAY host fixture services for convenience, but role credentials, signing keys, and authoritative state namespaces remain distinct.

No live model inference is required.

---

## 3. Crypto / Canonicalization

```text
signature_algorithm = Ed25519
digest_algorithm = SHA-256
canonicalization = RFC 8785 JCS
```

Unknown mandatory algorithms/versions fail closed.

---

## 4. RoleCredential Fixtures

Every controlling authority has an immutable signed/frozen RoleCredential equivalent:

```text
RoleCredential {
    role_credential_id
    subject_authority_id
    trust_domain_id
    allowed_artifact_types[]
    allowed_operations[]
    scope_constraints
    maximum_risk_or_claim_ceiling?
    not_before
    valid_until
    revocation_handle
    issuer
    signature
}
```

The verifier SHALL evaluate these credentials rather than infer authority from which helper function produced an object.

Required fixture roles:

- Protocol Authority: may sign accepted evaluation protocol fixture;
- Precommitment Registry Authority: may issue run commitments / maintain registry state;
- Runner: may execute/attest registered local runs but may NOT issue precommitment receipts;
- Synthetic Evaluator: may sign only the synthetic behavioral observation fixture used for role tests;
- Evidence Issuer: may issue baseline functional evidence only within frozen claim ceiling;
- Qualification/Package Admission Authority: may verify/admit evidence packages; not automatically an Evidence Issuer;
- Trust-State Authority: may issue current trust/revocation state for fixture authorities/evidence.

---

## 5. Baseline Formal-Attempt Policy

Freeze:

```text
repeat_attempts_allowed = true
all_formal_attempts_must_remain_referenced = true
new_display_campaign_id_does_not_reset_campaign_key_history = true
supersession_or_remediation_requires_explicit_signed_policy_artifact = true
```

This protocol tests history non-erasure only.

It does not decide whether a later PASS is substantively sufficient to remediate an earlier FAIL.

---

## 6. Authoritative Campaign Registry

The Precommitment Registry maintains independent authoritative state:

```text
CampaignRegistryState {
    trust_domain_id
    registry_epoch
    monotonic_registration_sequence
    campaign_key -> ordered formal_run_ids[]
}
```

The Qualification/Package Admission verifier SHALL query or verify this authoritative state independently from the aggregate evidence receipt.

Receipt-declared `prior_formal_attempt_refs[]` must reconcile with registry-known history required by policy.

---

## 7. Structured Evidence Claim Scope

The baseline scope is an explicit object, not only a digest:

```text
EvidenceClaimScope {
    capability_classes[]
    maximum_risk_class
    assurance_ceiling
    tool_classes[]
    network_access        // NONE | BOUNDED | GENERAL
    resource_scope[]
    trust_domain_id
    project_scope
}
```

Canonical digest:

```text
claim_scope_digest = SHA256(JCS(EvidenceClaimScope))
```

### 7.1 Local subset semantics

Package admission SHALL establish:

```text
requested capability_classes subset evidence capability_classes
requested maximum_risk_class <= evidence maximum_risk_class
requested assurance <= evidence assurance_ceiling
requested tool_classes subset evidence tool_classes
requested network_access <= evidence network_access
requested resource_scope subset evidence resource_scope
required trust_domain_id == evidence trust_domain_id
required project_scope == evidence project_scope
```

Freeze order:

```text
NONE < BOUNDED < GENERAL
```

No inference outside these explicit local semantics.

EI-T10 SHALL exercise at least capability and risk expansion.

---

## 8. Independent Trust-State Authority

The evidence receipt does not define its own authoritative revocation state.

Freeze separate local state:

```text
TrustStateSnapshot {
    trust_domain_id
    trust_state_epoch
    revoked_artifact_ids[]
    revoked_authority_ids[]
    suspended_artifact_ids[]
    authority_status_records[]
    issued_at
    trust_state_authority_id
    signature
}
```

Package admission obtains/verifies the current authoritative snapshot independently.

A receipt that cites an older clean epoch cannot override a newer accepted snapshot containing revocation.

Known-state rollback is rejected.

---

## 9. Baseline Valid Evidence Chain

```text
EvidenceRequirement
 -> EvaluationProtocol
 -> FormalEvaluationCampaign / campaign_key
 -> FormalRunRegistration
 -> PrecommitmentReceipt
 -> authoritative CampaignRegistryState
 -> AttemptLedger
 -> FunctionalTestReceipts
 -> RunCompletionRecord
 -> FunctionalEvidenceReceipt
 -> independent TrustStateSnapshot
 -> Qualification Evidence Package Admission
```

Use a small fixed deterministic population, e.g. five cases, whose exact fixture inputs/oracle outputs are frozen before formal execution.

---

## 10. Baseline Fixture Authorities Are Cross-Checked

The package-admission verifier SHALL independently validate:

- protocol signature + Protocol Authority RoleCredential;
- precommitment signature + Precommitment Registry RoleCredential;
- runner signature + Runner RoleCredential;
- evidence receipt signature + Evidence Issuer RoleCredential;
- TrustStateSnapshot signature + Trust-State RoleCredential;
- campaign registry history;
- structured claim-scope subset semantics;
- current authority/evidence trust state.

No aggregate object is authoritative about its own validity.

---

## 11. Frozen Invariants

### EI-I1 PRECOMMITMENT_ORDERING
Formal evidence requires valid authoritative precommitment before registered subject execution.

### EI-I2 PRECOMMITMENT_ROLE_SEPARATION
Runner credentials cannot issue a valid precommitment receipt in this local profile.

### EI-I3 CAMPAIGN_NON_ERASURE
Authoritative campaign registry history cannot be reset by changing caller-selected IDs.

### EI-I4 COMPLETE_ACCOUNTING
All registered cases/retries have protocol-defined terminal states.

### EI-I5 RECEIPT_SET_INTEGRITY
Aggregate evidence binds complete underlying receipts and controlling metrics recompute.

### EI-I6 AUTHORIZED_ROLES
All controlling authorities satisfy explicit RoleCredentials.

### EI-I7 SUBJECT_PROFILE_BINDING
Evidence cannot be admitted for a different subject/profile absent accepted compatibility.

### EI-I8 CLAIM_SCOPE_NON_EXPANSION
Structured scope comparison prevents unsupported capability/risk/assurance/environment expansion.

### EI-I9 CURRENT_TRUST_STATE
Current authoritative trust-state snapshot controls usability; known-state rollback fails closed.

### EI-I10 FAILURE_CLASS_INTEGRITY
Infrastructure/runner/evaluator errors cannot be rewritten contrary to frozen protocol.

### EI-I11 EVIDENCE_NOT_QUALIFICATION
Evidence validity does not itself issue qualification or action authorization.

---

## 12. Controlling Test Matrix

Freeze exactly **14 controlling tests**, EI-T0 through EI-T13.

All mandatory variants must pass.

### EI-T0 — Valid baseline chain

Expected:

```text
EVIDENCE_VALID
PACKAGE_ADMISSION_ACCEPTED
```

Verify all independent role, campaign, scope, trust-state, digest, accounting, and package links.

### EI-T1 — Post-hoc/no-valid precommitment

A. registration with no PrecommitmentReceipt;
B. precommitment not accepted before registered invocation;
C. receipt binds different registration digest;
D. authorized Runner key signs a fake PrecommitmentReceipt.

Expected: all REJECTED.

Variant D MUST fail because Runner RoleCredential lacks precommitment authority.

### EI-T2 — Precommitment rollback/wrong authority

A. older registry epoch after newer accepted epoch;
B. trusted key lacking precommitment role;
C. inconsistent monotonic sequence;
D. precommitment authority credential expired/revoked in current trust state.

Expected: all REJECTED.

### EI-T3 — Campaign history hiding

Create Run A = formal FAIL and Run B = formal PASS under same canonical campaign key.

A. B receipt omits A while registry contains A;
B. new display campaign ID used to hide same-key history;
C. receipt supplies fabricated history differing from registry;
D. policy-compliant complete history references A+B.

Expected A-C: REJECTED.

Expected D: history integrity structurally VALID. This protocol makes no substantive remediation ruling on whether B overcomes A.

### EI-T4 — Missing/selectively omitted cases

From five registered cases:

A. omit one FAIL receipt;
B. unauthorized NOT_EXECUTED;
C. aggregate sample size says four;
D. completion counts disagree with attempt ledger.

Expected: all REJECTED.

### EI-T5 — Retry/attempt omission

Fixture allows one retry only after specified infrastructure trigger.

A. omit first attempt;
B. retry without allowed trigger;
C. exceed maximum retry;
D. retry ledger and completion record disagree.

Expected: all REJECTED.

### EI-T6 — Receipt-set / aggregate tampering

A. mutate underlying receipt after receipt-set digest;
B. Evidence Issuer signs aggregate pass_count inconsistent with valid underlying receipts;
C. duplicate favorable receipt identity;
D. change aggregation output while preserving valid underlying receipt signatures.

Expected: all REJECTED by digest/recomputation/identity checks.

### EI-T7 — Runner/evaluator role integrity

A. unauthorized runner;
B. RunnerProfile digest differs from registration;
C. synthetic behavioral observation evaluator lacks evaluator role;
D. evaluator claims stronger independence without valid independence credential;
E. evaluator RoleCredential is revoked/currently unusable where policy makes it controlling.

Expected: all REJECTED.

### EI-T8 — Evidence issuer ceiling

A. evidence class outside issuer allowance;
B. claim/risk ceiling above issuer credential;
C. validity beyond issuer maximum;
D. evidence signed by Qualification Admission Authority key lacking Evidence Issuer role.

Expected: all REJECTED.

### EI-T9 — Subject/profile misbinding

A. principal A evidence for B;
B. profile A evidence for materially changed profile B without compatibility;
C. aggregate claims B while registration/underlying receipts bind A;
D. correct profile digest but mismatched subject principal.

Expected: all REJECTED.

### EI-T10 — Structured claim-scope expansion

Baseline scope permits:

```text
capability_classes = [READ_FILE]
maximum_risk_class = R1
assurance_ceiling = A1
tool_classes = [filesystem-read]
network_access = NONE
resource_scope = [test-fixture/*]
```

Variants:

A. request `WRITE_FILE`;
B. request R2;
C. request network_access=BOUNDED;
D. request resource outside `test-fixture/*`.

Expected: all REJECTED: CLAIM_SCOPE_EXPANSION.

Also assert exact/subset scope within baseline is accepted.

### EI-T11 — Lifecycle/revocation/current-state rollback

A. expired CONTINUOUSLY_CURRENT evidence;
B. evidence receipt revoked in current TrustStateSnapshot;
C. controlling Evidence Issuer revoked;
D. receipt cites epoch N while authoritative accepted TrustStateSnapshot is N+1 and contains revocation;
E. caller supplies old signed N snapshot after verifier knows N+1.

Expected: all REJECTED.

### EI-T12 — Failure-class integrity

Create infrastructure failure fixture.

A. aggregate rewrites as PASS;
B. aggregate rewrites as subject FAIL while protocol says INCONCLUSIVE;
C. runner claims COMPLETE when rules require INVALID/INCOMPLETE;
D. correctly represented EVIDENCE_INCONCLUSIVE/INVALID_RUN.

Expected A-C: REJECTED.

Expected D: structurally valid result classification but cannot satisfy PASS-required package admission.

### EI-T13 — Evidence is not qualification

Provide valid EVIDENCE_PASS.

Assert:

- evidence verifier accepts it;
- matching package requirement may admit it;
- mismatched requirement rejects it;
- no QualificationCredential is issued solely by evidence validation;
- no action/capability authorization is generated;
- package-admission authority cannot act as Evidence Issuer absent separate role.

All assertions must pass.

---

## 13. Acceptance Rule

Formal success requires:

```text
14 / 14 controlling tests PASS
all mandatory variants PASS
one coherent formal run
no frozen-protocol deviation
complete evidence
```

No partial credit, no evaluator judgment, no aggregation across separate formal runs.

---

## 14. Stop Conditions

STOP instead of weakening the protocol if:

- chronology depends only on runner assertions;
- package admission trusts receipt-declared campaign history without registry reconciliation;
- role authorization is inferred from code path rather than credentials;
- claim-scope subset semantics cannot be enforced deterministically;
- receipt current-state claims override independent authoritative revocation state;
- aggregate metrics cannot be recomputed;
- evidence verification inherently grants qualification/authorization;
- any controlling invariant requires redesign.

Mechanical defects may be corrected only if protocol semantics remain unchanged.

---

## 15. Formal Evidence Requirements

Preserve:

```text
protocol artifact digest
implementation/build commit
working-tree state
crypto/canonicalization constants
RoleCredential digests/public keys
baseline EvidenceRequirement digest
baseline EvaluationProtocol digest
baseline structured EvidenceClaimScope + digest
formal_attempt_policy digest
campaign_key
CampaignRegistryState digest/epoch
TrustStateSnapshot digest/epoch
EI-T0..EI-T13 results + variant results
reason codes
representative artifact digests
formal-run log
```

Historical ATE evidence remains untouched.

---

## 16. Classification Vocabulary

### `ATE_EVIDENCE_INTEGRITY_LOCAL_ESTABLISHED`
Only after 14/14 tests and every mandatory variant pass in one coherent formal run with no deviation.

### `ATE_EVIDENCE_INTEGRITY_LOCAL_NOT_ESTABLISHED`
Use for genuine controlling invariant/test failure.

### `ATE_EVIDENCE_INTEGRITY_INCONCLUSIVE`
Use only for infrastructure/tool failure preventing valid determination without demonstrating a controlling invariant failure.

---

## 17. Success Claim Boundary

A successful run establishes only:

> Under the frozen deterministic local profile, ATE evidence machinery can independently cross-check preregistration ordering, campaign history, complete-run accounting, receipt integrity, authority roles, subject/profile binding, structured claim scope, current trust state, failure classification, and qualification-package admission boundaries for the enumerated cases.

It does not establish any real AI agent's behavioral fitness or qualification.

---

## 18. Quota Conservation

This protocol requires no live language-model calls.

Execution budget:

1. deterministic local implementation;
2. local unit/preflight checks;
3. one 14-test formal run;
4. adjudication and stop.

No premium evaluator, multi-agent replication, or statistical generation is authorized by this protocol.

---

## 19. Freeze Candidate Status

This v0.1.1 artifact incorporates the adversarial-review corrections without increasing the controlling-test count.

Perform one final freeze review. If no architectural/test-meaning defect remains, record the exact artifact identity and freeze it before any implementation.
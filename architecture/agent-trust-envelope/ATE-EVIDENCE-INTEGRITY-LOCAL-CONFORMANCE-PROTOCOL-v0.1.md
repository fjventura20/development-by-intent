# ATE Evidence Integrity Local Conformance Protocol v0.1

**Status:** Freeze candidate — DESIGN ONLY  
**Date:** 2026-09-16  
**Program:** Agent Trust Envelope (ATE)  
**Controlling architecture:** `ATE-BEHAVIORAL-FUNCTIONAL-EVIDENCE-ARCHITECTURE-v0.1.1.md` + normative amendment `v0.1.2.md`  
**Upstream qualification architecture:** `ATE-AGENT-QUALIFICATION-REQUALIFICATION-ARCHITECTURE-v0.1.1.md`

---

## 1. Research Question

> **Can a deterministic local evidence verifier distinguish a valid preregistered, completely accounted, authorized, correctly scoped evidence chain from specified post-hoc, incomplete, tampered, misbound, stale, unauthorized, or selectively reported evidence chains before admission into a Qualification Evidence Package?**

This protocol tests evidence integrity machinery only.

It does not evaluate actual AI capability, behavioral quality, morality, or Value Architecture effectiveness.

---

## 2. Lean Local Profile

Use deterministic fixtures for:

- one trust domain;
- one Evidence Requirement;
- one Protocol Authority;
- one frozen deterministic functional Evaluation Protocol;
- one Campaign/Precommitment Registry Authority;
- one authorized RunnerProfile;
- one unauthorized runner;
- one deterministic oracle;
- one Evidence Issuer;
- one Qualification Authority / package-admission verifier;
- one baseline subject principal/profile;
- one alternate profile;
- one authoritative local trust/revocation epoch;
- one trusted local clock.

No model inference is required.

No behavioral scorer is required for the controlling protocol.

The protocol MAY include synthetic evaluator fixtures solely to test evaluator-role/profile validation.

---

## 3. Cryptographic / Canonical Profile

Freeze:

```text
signature_algorithm = Ed25519
digest_algorithm = SHA-256
canonicalization = RFC 8785 JCS
```

Unknown mandatory versions or algorithms fail closed.

---

## 4. Baseline Valid Evidence Chain

The harness SHALL be able to construct one fully valid chain:

```text
EvidenceRequirement
    -> EvaluationProtocol
    -> FormalEvaluationCampaign / campaign_key
    -> FormalRunRegistration
    -> PrecommitmentReceipt
    -> AttemptLedger
    -> FunctionalTestReceipts
    -> RunCompletionRecord
    -> FunctionalEvidenceReceipt
    -> current trust-state/revocation check
    -> Qualification Evidence Package admission
```

The baseline uses a small fixed deterministic case population such as five cases with a fixed expected PASS outcome.

The exact case IDs, inputs, oracle outputs, and digests SHALL be frozen in the implementation/evidence before formal execution.

---

## 5. Required Fixture Semantics

### 5.1 Evidence Requirement

Binds:

```text
evidence_requirement_id
evidence_class_id = deterministic-functional-local
claim_scope_digest
baseline qualified_profile_digest
accepted protocol digest/version
runner role requirements
evidence issuer requirements
lifecycle_class
trust_domain_id
policy_epoch
```

### 5.2 Formal Campaign

Canonical `campaign_key` SHALL include:

```text
trust_domain_id
evidence_requirement_id
subject_principal_id
qualified_profile_digest
qualification_or_admission_attempt_id
```

### 5.3 Precommitment Registry

Maintains:

```text
registry_epoch
monotonic_registration_sequence
campaign_key -> run history
```

The baseline formal registration is committed before invocation.

### 5.4 Attempt Ledger

Every registered case has exactly one baseline invocation/terminal state unless a specific test fixture declares otherwise.

### 5.5 Qualification Package Admission

Admission verifier SHALL independently verify all controlling links rather than trusting the aggregate evidence receipt alone.

---

## 6. Frozen Invariants Under Test

### EI-I1 — PRECOMMITMENT_ORDERING
Valid formal evidence requires authoritative precommitment before subject invocation.

### EI-I2 — CAMPAIGN_NON_ERASURE
Prior formal attempts associated with the controlling campaign key cannot be hidden by a new run/campaign display ID.

### EI-I3 — COMPLETE_ACCOUNTING
All registered cases and retries have protocol-defined terminal states.

### EI-I4 — RECEIPT_SET_INTEGRITY
Aggregate evidence binds the exact complete underlying receipt set and metrics recompute.

### EI-I5 — AUTHORIZED_ROLES
Protocol, precommitment, runner, evaluator where applicable, evidence issuer, and qualification admission authorities satisfy role policy.

### EI-I6 — SUBJECT_PROFILE_BINDING
Evidence cannot be admitted for a different subject/profile absent accepted compatibility semantics.

### EI-I7 — CLAIM_SCOPE_NON_EXPANSION
Qualification admission cannot widen evidence claim/capability/risk/assurance scope.

### EI-I8 — CURRENT_TRUST_STATE
Expired/revoked/suspended evidence or authority state fails closed and trust-state rollback is rejected.

### EI-I9 — FAILURE_CLASS_INTEGRITY
Infrastructure/runner/evaluator error cannot be silently rewritten as subject PASS or FAIL contrary to the frozen protocol.

### EI-I10 — EVIDENCE_NOT_QUALIFICATION
A valid evidence receipt becomes only an input to package admission; it does not itself grant qualification or authorization.

---

## 7. Controlling Test Matrix

Freeze **14 controlling tests**, EI-T0 through EI-T13.

All mandatory variants inside each test must pass.

### EI-T0 — Valid baseline chain

Construct the complete valid baseline.

Expected:

```text
EVIDENCE_VALID
PACKAGE_ADMISSION_ACCEPTED
```

Verify all digests/roles/current-state checks and successful package linkage.

### EI-T1 — Post-hoc registration / no valid precommitment

Variants:

A. registration exists but no PrecommitmentReceipt;
B. precommitment sequence is issued after first recorded subject invocation;
C. PrecommitmentReceipt binds a different registration digest.

Expected: all REJECTED.

### EI-T2 — Precommitment rollback / wrong authority

Variants:

A. older registry epoch supplied after newer epoch is known;
B. precommitment signed by trusted key lacking precommitment role;
C. monotonic registration sequence inconsistent with authoritative registry state.

Expected: all REJECTED.

### EI-T3 — Campaign history hiding

Create formal Run A = FAIL under the controlling `campaign_key`.

Then create Run B = PASS using a new display `campaign_id` but the same campaign key.

Variants:

A. evidence for B omits required reference/history of A;
B. operator attempts a fresh campaign lineage without policy-authorized transition.

Expected: REJECTED as incomplete/hidden campaign history.

A policy-compliant campaign history including both attempts MAY be structurally valid, but the protocol does not assert that B supersedes A unless formal-attempt policy says so.

### EI-T4 — Missing / selectively omitted cases

From a registered five-case population:

A. omit one FAIL receipt;
B. mark one executed case as NOT_EXECUTED without protocol permission;
C. declare sample size four in aggregate receipt despite registration of five.

Expected: all REJECTED.

### EI-T5 — Retry / attempt omission

Use a fixture allowing one retry after an infrastructure-defined condition.

Variants:

A. second attempt present but first attempt omitted from ledger;
B. retry executed despite no protocol-defined retry trigger;
C. more retries than frozen maximum.

Expected: all REJECTED.

### EI-T6 — Receipt-set / metric tampering

Variants:

A. one underlying test receipt changed after `receipt_set_digest` creation;
B. aggregate claims pass_count=5 when recomputation yields 4;
C. duplicate one favorable receipt under same case/attempt identity.

Expected: all REJECTED.

### EI-T7 — Runner / evaluator role integrity

Variants:

A. run completed by unauthorized runner;
B. RunnerProfile digest differs from registration;
C. synthetic behavioral observation signed by evaluator lacking required evaluator role;
D. evaluator claims stronger independence class without valid independence credential.

Expected: all REJECTED.

### EI-T8 — Evidence issuer ceiling

Variants:

A. authorized issuer signs evidence class outside its allowed classes;
B. issuer expands claim scope/risk ceiling beyond its authority;
C. issuer sets validity beyond allowed maximum.

Expected: all REJECTED.

### EI-T9 — Subject/profile misbinding

Variants:

A. valid receipt for principal A presented for principal B;
B. valid receipt for profile A presented for materially different profile B without compatibility;
C. aggregate receipt profile matches B but underlying registration/receipts are A.

Expected: all REJECTED.

### EI-T10 — Claim-scope / capability expansion

Baseline evidence is scoped to a bounded capability envelope.

Attempt package admission for a broader environment/capability/risk/assurance claim.

Expected:

```text
REJECTED: CLAIM_SCOPE_EXPANSION
```

No inference from restricted test environment to broader operational privilege.

### EI-T11 — Lifecycle / revocation / trust-state rollback

Variants:

A. expired CONTINUOUSLY_CURRENT evidence;
B. explicitly revoked evidence receipt;
C. evidence issuer/evaluator authority revoked when active policy makes current validity controlling;
D. stale trust-state epoch presented after newer revocation epoch known.

Expected: all REJECTED.

### EI-T12 — Failure-class integrity

Create an infrastructure failure fixture.

Variants:

A. aggregate receipt rewrites infrastructure failure as PASS;
B. aggregate rewrites infrastructure failure as subject FAIL when frozen protocol specifies INCONCLUSIVE;
C. runner marks run COMPLETE when frozen rules require INVALID/INCOMPLETE.

Expected: all REJECTED.

Also verify correctly represented `EVIDENCE_INCONCLUSIVE`/`INVALID_RUN` fixture is structurally accepted as that result but cannot satisfy a PASS-required Qualification Evidence Package.

### EI-T13 — Evidence is not qualification

Provide a completely valid `EVIDENCE_PASS` receipt.

Assert:

- evidence verifier accepts it as valid evidence;
- Qualification Evidence Package may reference it only if active requirement matches;
- no QualificationCredential is created solely by evidence verification;
- no capability/action authorization is created;
- mismatched Evidence Requirement causes package admission rejection.

Expected: all assertions PASS.

---

## 8. Formal Acceptance Rule

Success requires:

```text
EI-T0..EI-T13 = 14/14 PASS
all mandatory variants PASS
no protocol deviation
one coherent formal run
complete evidence
```

No partial credit.

No evaluator judgment.

No combining results across formal runs.

---

## 9. Deterministic Result Vocabulary

Harness SHOULD emit machine-readable outcomes such as:

```text
EVIDENCE_VALID
EVIDENCE_INVALID
PACKAGE_ADMISSION_ACCEPTED
PACKAGE_ADMISSION_REJECTED
EVIDENCE_INCONCLUSIVE
INVALID_RUN
```

with deterministic reason codes.

---

## 10. Formal Run Discipline

A valid formal run requires:

- exact frozen protocol artifact digest recorded;
- one implementation commit/build identifier;
- clean working tree at run start;
- fixed crypto/canonicalization constants;
- fixed fixture keys/roles or deterministically generated test keys whose public identities are recorded;
- fixed baseline case population;
- all 14 controlling tests executed once in one coherent formal run;
- all variants reported;
- no test weakening after failure.

Development/preflight runs are not formal evidence.

---

## 11. Stop Conditions

STOP rather than alter the frozen protocol if implementation shows that:

- preregistration chronology cannot be independently ordered;
- campaign history cannot prevent attempt hiding;
- receipt-set completeness cannot be verified;
- aggregate metrics cannot be recomputed;
- role/authority ceilings cannot be enforced;
- profile/scope expansion cannot be detected;
- current evidence trust state cannot fail closed;
- evidence validation inherently grants qualification/authorization;
- any frozen invariant requires architectural redesign.

Mechanical implementation defects may be corrected only if they preserve the protocol.

---

## 12. Evidence Requirements for This Protocol

Formal evidence SHALL preserve:

```text
protocol artifact digest
implementation commit/build ID
working-tree state
crypto/canonicalization constants
fixture authority public keys + role credentials
baseline Evidence Requirement digest
baseline Evaluation Protocol digest
campaign_key
registry epoch/sequence state
test/variant results EI-T0..EI-T13
reason codes
representative artifact digests
formal-run log
```

Historical P1/P2/qualification artifacts remain untouched.

---

## 13. Classification Vocabulary

### `ATE_EVIDENCE_INTEGRITY_LOCAL_ESTABLISHED`

Only if 14/14 controlling tests and all mandatory variants pass in one coherent formal run with no frozen-protocol deviation.

### `ATE_EVIDENCE_INTEGRITY_LOCAL_NOT_ESTABLISHED`

Use for genuine controlling invariant/test failure.

### `ATE_EVIDENCE_INTEGRITY_INCONCLUSIVE`

Use only for infrastructure/tool failure preventing valid determination without demonstrating an invariant failure.

---

## 14. Success Claim Boundary

A successful run establishes only:

> Under the frozen local deterministic profile, ATE evidence machinery can detect the specified preregistration, campaign-history, completeness, tampering, role, profile, scope, lifecycle, and qualification-boundary failures before evidence is admitted to a Qualification Evidence Package.

It does not establish that any real AI agent is behaviorally safe, competent, aligned, or qualified.

---

## 15. Quota Conservation

This is an evidence-machinery conformance test.

Default execution budget:

1. local deterministic implementation;
2. deterministic unit/preflight checks;
3. one formal 14-test run;
4. adjudication and stop.

Do not invoke premium model evaluators, multi-agent replication, or live behavioral generations for this protocol.

---

## 16. Freeze Candidate Status

This v0.1 protocol is a freeze candidate only.

Before implementation authorization, perform one adversarial protocol review focused on:

- whether any test can pass without proving the intended invariant;
- whether fixtures accidentally trust the same object they are supposed to verify;
- whether campaign/precommitment ordering is genuinely independent;
- whether acceptance results can be manufactured by test harness shortcuts.

No implementation is authorized until a freeze record pins the accepted artifact identity.
# ATE Behavioral & Functional Evidence — Adversarial Review v0.1

**Status:** Adversarial architecture review  
**Date:** 2026-09-16  
**Reviewed artifact:** `ATE-BEHAVIORAL-FUNCTIONAL-EVIDENCE-ARCHITECTURE-v0.1.md`

---

## 1. Disposition

**REVISION_REQUIRED_BEFORE_PROTOCOL_DESIGN**

The v0.1 architecture has the correct core model: evidence is a bounded observation under a frozen protocol, separate from qualification and authorization. Its complete-run accounting, anti-cherry-picking, claim-scope, lifecycle, and evaluator-role distinctions are strong.

However, the architecture still permits several ways to manufacture apparently clean evidence without violating the literal v0.1 text.

The most important defect is:

> **The run manifest is described as immutable, but it is not required to be cryptographically committed before the first subject invocation.**

Without pre-run commitment, a malicious or outcome-seeking runner can execute a larger hidden population and later publish a manifest containing only favorable cases.

The following corrections are required.

---

## 2. Finding A — Formal Run Population Must Be Precommitted

### Attack

Runner executes cases:

```text
A B C D E F G H
```

Results:

```text
A PASS
B FAIL
C PASS
D FAIL
E PASS
F PASS
G PASS
H PASS
```

After seeing outcomes, runner creates a formally valid-looking run manifest declaring only:

```text
A C E F G H
```

The v0.1 receipt/accounting rules then appear satisfied for the selected population.

### Required correction

Introduce a signed, immutable `FormalRunRegistration` committed **before first subject invocation**.

It SHALL bind at least:

```text
formal_run_id
protocol_digest
subject/profile binding
case IDs or generator + seed derivation rule
sample size
replication count
runner identity
evaluator identities or selection rule
scoring/acceptance rule digests
retry/stopping rule digests
registered_at
registration_authority / signature
```

The final run manifest and result receipts must link back to this registration.

No formal evidence can be issued if the population cannot be reconciled to the precommitted registration.

---

## 3. Finding B — Multiple Formal Attempts Can Recreate Cherry-Picking at the Run Level

### Attack

A subject fails Formal Run 1.

Operator silently discards it and starts Formal Run 2.

Run 2 passes and is presented as the only formal evidence.

This defeats within-run anti-cherry-picking while preserving the same bias across runs.

### Required correction

Qualification/evidence policy SHALL define `formal_attempt_policy`, including:

```text
whether repeat formal attempts are permitted
cooldown/change requirement
maximum attempts?
whether prior formal failures remain controlling evidence
whether a new attempt requires profile/protocol change
supersession semantics
```

Every formal attempt under a qualification campaign SHALL receive an immutable campaign/run identifier and remain auditable.

A later passing run MUST NOT make prior formal failure disappear.

Whether later evidence supersedes the failure is a policy decision, not evidence deletion.

---

## 4. Finding C — Evaluator Configuration Is Part of the Evidence

### Attack

An AI evaluator identity/model remains nominally the same, but its:

- system instructions;
- rubric prompt;
- temperature/sampling settings;
- tool access;
- context template;
- model revision;

change materially between evaluations.

The receipt still names the same evaluator and rubric digest.

### Required correction

Define immutable `EvaluatorProfile` evidence containing, as applicable:

```text
evaluator_id
evaluator_type
evaluator_software/model identity
evaluator_configuration_digest
evaluator_instruction/prompt digest
tool/capability profile digest
decoding/sampling configuration
evaluator_role
independence credential/reference
version
profile_digest
```

Each behavioral observation binds the exact evaluator-profile digest.

For human evaluators, profile may bind role/credential/training/rubric version rather than software decoding fields.

---

## 5. Finding D — Independence Class Cannot Be Self-Asserted

### Attack

The runner labels a second evaluator `E2_INDEPENDENT_ROLE`, although both evaluator credentials and execution are controlled by the same subject/operator boundary.

### Required correction

Evaluator independence SHALL be supported by an authoritative `EvaluatorRelationship/IndependenceCredential` or equivalent trust-registry state.

At minimum it binds:

```text
evaluator_id
operator/admin domain
relationship to subject
relationship to runner
independence_class
validity
issuer
```

The evidence issuer or evaluator MUST NOT unilaterally upgrade its own independence class.

---

## 6. Finding E — Result Aggregator Must Not Be Able to Invent Underlying Evaluation

### Attack

Evidence Issuer signs an aggregate `BehavioralEvidenceReceipt` claiming 60/60 valid observations but does not provide verifiable linkage to the actual evaluator-signed observation set.

### Required correction

Aggregate receipt SHALL bind a canonical `receipt_set_digest` computed over the complete ordered/set-defined collection of underlying receipts.

Before issuance, Evidence Issuer SHALL verify:

- every required underlying receipt exists;
- receipt signatures/roles are valid;
- each belongs to the registered run;
- no duplicate receipt/case identity exists unless protocol permits it;
- every registered case/replication is accounted for;
- aggregation recomputes exactly from those receipts.

The issuer may summarize evidence but cannot originate missing evaluator observations.

---

## 7. Finding F — Runner Completion Needs Its Own Attestation

### Attack

Case receipts look valid, but there is no signed statement establishing that the runner actually completed the registered population and recorded all attempts/errors/timeouts.

### Required correction

Add signed `RunCompletionRecord`:

```text
formal_run_id
registration_digest
run_manifest_digest
attempt_ledger_digest
receipt_set_digest
declared_cases
attempted_cases
terminal-state counts
started_at
completed_at
runner_id
runner_profile_digest
result = COMPLETE | INCOMPLETE | INVALID
reason_codes[]
signature
```

A formal evidence PASS requires protocol-defined completion validity.

---

## 8. Finding G — Seed / Sample Selection Must Not Be Outcome-Selectable

### Attack

Protocol says "fixed random seed," but runner chooses the seed after trying several seeds and seeing which population is favorable.

### Required correction

The protocol SHALL define one of:

- seed fixed in protocol;
- seed fixed in pre-run registration before subject execution;
- seed deterministically derived from a committed external nonce/context;
- trusted sampler chooses and signs seed before execution.

Seed/sample selection occurring after observed subject outcomes invalidates the formal run.

---

## 9. Finding H — Evidence Current State Needs Monotonic Control

### Attack

Evidence receipt E is revoked at epoch 12.

Verifier is later shown an old but valid status snapshot from epoch 10 indicating active/not-revoked and accepts E.

### Required correction

Evidence current state SHALL integrate with the existing ATE Revocation & Trust-State Model.

The verifier/Qualification Authority must reject rollback below the newest accepted authoritative trust-state/revocation epoch.

If evidence-specific status objects are used, their epochs must compose with the authoritative trust-state model; they must not create a parallel weaker revocation mechanism.

---

## 10. Finding I — Hidden Corpus Claims Need Explicit Custody / Exposure Semantics

### Attack

Protocol calls a test corpus "hidden," but the subject developer, runner, or evaluator had access before execution.

The resulting evidence is then described as contamination-resistant.

### Required correction

If hidden/held-out status contributes to the claim, evidence SHALL declare:

```text
corpus_custodian
exposure_policy
subject_access status
runner_access status
evaluator_access status
disclosure timing
contamination/declassification status
```

Unknown exposure status MUST NOT be represented as confirmed hidden independence.

---

## 11. Finding J — Evaluator Revocation Must Affect Current Evidence Usability

### Attack

An evaluator is later found compromised, but previously signed behavior receipts remain cryptographically valid and continue supporting qualification.

### Required correction

Evidence admission/current-use checks SHALL evaluate current status of controlling evaluator authority when policy declares evaluator validity continuously controlling.

The Evidence Requirement lifecycle policy must distinguish:

- evaluator valid only at issuance;
- evaluator current status continuously controlling;
- compromise causes mandatory evidence review/requalification.

This avoids over-revoking historical evidence while permitting current qualification to react to evaluator compromise.

---

## 12. Finding K — Evidence Claim Must Bind the Evaluation Environment More Strongly

### Attack

Subject is evaluated with restricted tools/network/resources but qualification later interprets the result as support for a broader tool profile.

The v0.1 architecture records environment digests, but claim coverage rules should make non-expansion normative.

### Required correction

Claim-scope admission SHALL enforce:

```text
target profile capabilities <= evaluated/explicitly compatible capability envelope
```

An environment/capability expansion requires new evidence or signed compatibility/non-interference evidence accepted by qualification policy.

No inference from restricted evaluation environment to broader operational capability.

---

## 13. Finding L — Derived Metrics Must Be Recomputable

### Attack

Receipt reports:

```text
mean_score = 0.94
critical_failures = 0
```

but underlying observations would yield 0.89 and one critical failure.

### Required correction

Every controlling aggregate metric SHALL be deterministically recomputable from the bound underlying receipt set and frozen aggregation rule.

Evidence Issuer SHALL not be trusted as the sole calculator of controlling metrics.

---

## 14. Finding M — Evidence Errors Must Not Be Converted Into Subject Failure Without Protocol Authority

The v0.1 architecture correctly separates failure classes but should make the consequence explicit.

Runner/evaluator/infrastructure failure SHALL map according to the frozen protocol, normally to `INCONCLUSIVE`, `INVALID_RUN`, or protocol-defined retry—not silently to subject PASS or FAIL.

This protects both against false exoneration and false condemnation.

---

## 15. Findings That Do Not Require Redesign

The following v0.1 choices are accepted:

- evidence/qualification/authorization separation;
- deterministic functional evidence preference;
- claim-scope bounding;
- content-addressable receipts;
- explicit stochastic replication rules;
- evaluator disagreement policy;
- lifecycle classes;
- operational/drift evidence separation;
- evidence revocation and supersession distinction;
- signed package admission checks;
- no universal numeric trust score;
- P2 remains unchanged.

---

## 16. Required v0.1.1 Corrections

A surgical v0.1.1 should add or strengthen:

1. pre-run `FormalRunRegistration`;
2. qualification/evidence campaign attempt history;
3. exact `EvaluatorProfile` binding;
4. authoritative evaluator-independence evidence;
5. `RunCompletionRecord`;
6. canonical complete receipt-set verification;
7. non-selectable seed/sample rules;
8. monotonic current trust-state/revocation checks;
9. hidden-corpus custody/exposure semantics;
10. evaluator-compromise lifecycle semantics;
11. environment/capability non-expansion rule;
12. recomputable aggregate metrics;
13. explicit infrastructure-error consequence rules.

These changes strengthen the evidence chain without altering the core ATE architecture.

---

## 17. Final Review Statement

The evidence architecture must make it impossible to obtain a strong-looking receipt merely by controlling which attempts become visible.

The corrected chain should be:

```text
frozen protocol
    -> precommitted formal run
    -> complete attempt ledger
    -> runner completion attestation
    -> independently verifiable observation/test receipts
    -> deterministic aggregation
    -> bounded signed evidence receipt
    -> current-state verification
    -> qualification-package admission
```

That is the minimum defensible path from observed agent behavior to a qualification claim.
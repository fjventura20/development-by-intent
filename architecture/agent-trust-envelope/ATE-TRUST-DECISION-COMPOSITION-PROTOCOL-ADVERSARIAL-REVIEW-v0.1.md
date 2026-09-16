# ATE Trust-Decision Composition Protocol Adversarial Review v0.1

**Status:** Adversarial protocol review  
**Date:** 2026-09-16  
**Reviewed artifact:** `ATE-TRUST-DECISION-COMPOSITION-LOCAL-CONFORMANCE-PROTOCOL-v0.1.md`

---

## 1. Disposition

**SURGICAL_REVISION_REQUIRED_BEFORE_FREEZE**

The 16-test matrix is appropriately lean and covers the controlling composition invariants.

No additional test IDs are required.

Four protocol details must be tightened before freeze so an implementation cannot pass through deterministic but incorrect reason ordering, incomplete execution invalidation, or overly permissive fixture authority.

---

## 2. Finding P1 — Expected denial precedence must be frozen, not discovered

### Problem

TD-C15 requires the same primary reason code across repeated runs, but a consistently incorrect implementation could satisfy that condition.

### Required correction

Before formal execution, each negative fixture/variant SHALL include a frozen expected:

```text
expected_primary_gate
expected_primary_reason_code
```

based on the frozen CompositionProfile.

Formal PASS requires actual values to equal those preregistered expectations.

TD-C15 still verifies repeated determinism and profile binding, but the whole matrix now checks correctness as well as repeatability.

---

## 3. Finding P2 — Execution-invalidating coverage should include decision/revocation state itself

### Problem

TD-C13 allows qualification suspension or approval revocation as examples, but the executor contract explicitly includes TrustDecision status/revocation and current revocation state.

A harness could pass without proving that a directly revoked unexecuted grant is blocked.

### Required correction

TD-C13 SHALL include mandatory variants:

A. directly revoke/suspend the unexecuted TrustDecision or authorization state;
B. invalidate one upstream dependency marked immediate/execution-invalidating (for example qualification suspension or approval revocation);
C. alter an `ISSUANCE_SNAPSHOT` dependency whose lifecycle explicitly does not invalidate the existing grant.

Expected:

```text
A-B: NO EXECUTION
C: no unnecessary full reevaluation; grant remains governed by its other validity/recheck rules
```

This remains one controlling test.

---

## 4. Finding P3 — Formal fixture authority ceilings must be frozen before the run

### Problem

The protocol lists distinct authorities but does not explicitly require the authority registry/ceiling policy itself to be frozen before test execution.

A harness could adapt authority permissions to the case under test.

### Required correction

Formal evidence must preserve a preregistered immutable:

```text
AuthorityRoleRegistry
DecisionAuthorityCeilingPolicy
StateAuthorityRegistry
```

including digests.

No authority permission may change during the formal run.

TD-C5 and TD-C11 evaluate against these frozen registries.

---

## 5. Finding P4 — Formal semantic time state must be frozen separately from incidental clock

### Problem

TD-C1 correctly tests that incidental timestamps do not alter semantic identity, but freshness/expiry is security-controlling and must still be reproducible.

### Required correction

The formal harness SHALL use a deterministic controllable trusted clock/time-state fixture.

For each test variant, preregister the controlling evaluation time or time-state ID used for validity/freshness predicates.

Incidental log/issuance timestamps are non-semantic; explicit trusted time-state used by security predicates is semantic through the relevant currentness/freshness context.

This prevents implementations from either ignoring time entirely or accidentally hashing arbitrary wall-clock metadata.

---

## 6. Accepted Matrix

No new test IDs are needed.

Accepted coverage remains:

```text
TD-C0  valid complete composition
TD-C1  semantic identity stability
TD-C2  one executable grant / retry / concurrency / restart
TD-C3  canonical action / taxonomy
TD-C4  risk / assurance downgrade
TD-C5  state authority / rollback / unavailable state
TD-C6  runtime / qualification binding
TD-C7  qualification-capability intersection
TD-C8  governance currentness
TD-C9  capability widening/exclusion
TD-C10 approval context / quorum mixing
TD-C11 Decision Authority ceilings
TD-C12 decision-time state-change race
TD-C13 execution-invalidating dependency change
TD-C14 action-operation-replay chain
TD-C15 deterministic denial/profile binding
```

---

## 7. Formal-Run Manifest Requirement

Add one immutable preregistered `FormalRunManifest` containing at least:

```text
protocol artifact digest
CompositionProfile digest
capability taxonomy digest
AuthorityRoleRegistry digest
DecisionAuthorityCeilingPolicy digest
StateAuthorityRegistry digest
fixture-set digest
trusted-time fixture policy/digest
per-variant expected verdict
per-negative-variant expected primary gate/reason code
formal test IDs/variant IDs
```

The formal manifest SHALL be fixed before the formal run begins.

This protocol tests deterministic engineering, so there is no justification for deriving expected outcomes after observing execution.

---

## 8. Final Review Statement

With these four surgical corrections, the protocol is suitable for freeze.

The central freeze rule should be:

> **A formal composition run must test one preregistered decision semantics package: fixed authorities, fixed gate precedence, fixed fixtures, fixed controlling time states, and fixed expected outcomes.**

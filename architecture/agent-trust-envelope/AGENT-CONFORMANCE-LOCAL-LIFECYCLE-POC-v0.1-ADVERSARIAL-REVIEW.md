# Agent Conformance Local Lifecycle PoC v0.1 — Adversarial Review

**Reviewed artifact:** `AGENT-CONFORMANCE-LOCAL-LIFECYCLE-POC-v0.1-DESIGN.md`  
**Review mode:** design-only adversarial review  
**Disposition:** CHANGES REQUIRED BEFORE FREEZE

## 1. Summary

The design correctly targets the smallest meaningful lifecycle proof and keeps external model calls out of scope. The acceptance invariant is strong and testable.

However, six issues must be corrected before freeze.

## 2. Findings

### F1 — Profile v1 -> v2 update can trivialize restoration
**Severity:** HIGH

The design restores conformance by changing the profile so v2 becomes permitted. That can accidentally prove only that policy was weakened to fit the new runtime.

**Required correction:** restoration must distinguish a legitimate authorized policy update from ad hoc accommodation. The test should bind profile v2 activation to a predeclared, signed policy transition authorized before the formal run, or use a pre-frozen successor profile digest. The formal run must not invent profile v2 after observing failure.

### F2 — Initial qualification/admission fixture is insufficiently bound
**Severity:** HIGH

A deterministic fixture can become a hard-coded bypass if current-state checks are not explicit.

**Required correction:** define fixture artifacts with stable IDs/digests and require the authorization path to verify their ACTIVE/current state on every relevant authorization decision. Fixture status may be static during this PoC, but verification cannot be skipped.

### F3 — Trigger observer independence needs a concrete security boundary
**Severity:** HIGH

“Independent” is currently logical. If the same mutable state store is controlled by the subject, the subject could rewrite both runtime state and observation history.

**Required correction:** separate subject-requested runtime state from observer-authoritative measured state. The observer should read a protected fixture/state file inaccessible to subject mutation through the test interface, or use distinct process/file ownership if feasible.

### F4 — Executor epoch recheck must occur after nonce reservation ordering is defined
**Severity:** MEDIUM-HIGH

If nonce state changes before stale-epoch rejection, a denied stale capability could consume its nonce in a way that confuses evidence. If epoch is checked too early without atomic state view, race semantics remain ambiguous.

**Required correction:** define exact executor sequence:
1. verify capability signature/scope/expiry;
2. resolve current lifecycle state+epoch;
3. reject stale/non-conformant capability;
4. atomically reserve nonce only after current-state checks pass;
5. obtain resource authority;
6. execute.

### F5 — Audit recorder independence is underspecified
**Severity:** MEDIUM

A subject-visible append-only file is not enough if the same code can rewrite it.

**Required correction:** the formal run must verify audit mutation detection using a copied tampered ledger and preserve the authoritative ledger unchanged. The audit writer must be separate from participant-facing interfaces.

### F6 — Formal evidence needs causal ordering proofs
**Severity:** MEDIUM

Wall-clock timestamps alone can be ambiguous or manipulated.

**Required correction:** every lifecycle/evidence record should include monotonic sequence/order fields, and the formal run should verify:
```text
C1_issued
< runtime_mutation
< trigger_observed
< N+1_published
< C1_denied
< post_change_evidence
< R13_restore_eval
< N+2_published
< C2_issued
< C2_effect
```

## 3. Required Changes

Produce v0.1.1 design with:

1. predeclared/frozen successor profile v2 before formal run;
2. explicit qualification/admission fixture verification;
3. concrete observer-authoritative runtime measurement boundary;
4. exact executor check/reservation ordering;
5. non-destructive audit tamper test;
6. monotonic causal ordering assertions.

## 4. Freeze Recommendation

Do not freeze v0.1.

After these corrections, a narrow review is sufficient. No broader redesign is needed.

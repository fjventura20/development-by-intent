# Agent Conformance Local Lifecycle PoC v0.1.1 — Freeze

**Status:** FROZEN — IMPLEMENTATION DESIGN BASELINE  
**Frozen artifact:** `AGENT-CONFORMANCE-LOCAL-LIFECYCLE-POC-v0.1.1-DESIGN.md`  
**Feature branch:** `feature/agent-conformance-local-lifecycle-poc-v0.1`  
**Design commit:** `b38be8c11b00b1a9f7b9fc95d64d5d97cf341edf`  
**Design blob SHA:** `4faea2a16261ca9416fe8bb4eceaaff80593eb59`  
**Freeze review commit:** `66a92592516475ac52949ebd013e215266ef4b80`  
**Parent conformance freeze:** `8c98318e9b5eb634cf067866a9a81ee96b024c25`

## 1. Freeze Scope

This freeze establishes v0.1.1 as the controlling implementation design for the first local deterministic Agent Conformance lifecycle PoC.

Implementation is now authorized only within this frozen scope.

External model calls remain prohibited. Hermes is not required for execution.

## 2. Frozen Proof Target

The PoC must prove:

```text
CONFORMANT @ N
-> issue C1
-> runtime v1 -> v2
-> independent trigger
-> REATTESTATION_REQUIRED @ N+1
-> C1 denied with zero protected-resource effect
-> activate predeclared profile v2
-> fresh post-change evidence
-> R13 positive evaluation
-> R14 CONFORMANT @ N+2
-> issue C2
-> C2 executes exactly once
-> replay denied
-> audit/evidence chain verifies
```

## 3. Mandatory Acceptance Threshold

PASS requires all of:

- 18/18 required test cases PASS
- 8/8 negative security cases PASS
- zero unauthorized protected-resource effects
- zero stale-capability effects
- zero replay effects
- valid authoritative audit chain
- tampered-copy audit verification fails
- causal-order verification passes
- evidence manifest valid
- zero unresolved deviations

Anything less is not PASS.

## 4. Frozen Security Boundaries

Implementation must preserve:

- separate subject, R13, R14, authorization, executor, trigger-observer, and audit identities/interfaces;
- observer-authoritative runtime measurement distinct from subject-requested state;
- qualification/admission fixture verification as real gates;
- current conformance and state-epoch verification before nonce reservation;
- protected-resource authority unavailable to participant-facing interfaces;
- predeclared profile v2 digest locked before formal-run start;
- immutable historical lifecycle decisions;
- non-destructive audit tamper testing.

## 5. Formal-Run Discipline

Formal execution may occur only after:

1. implementation complete;
2. implementation tests pass;
3. worktree clean;
4. implementation commit locked;
5. frozen parent artifacts verified unchanged;
6. preflight confirms both profile v1 and profile v2 digests;
7. formal run receives a unique run ID.

A formal rerun requires a new run ID. Evidence from a failed or stopped run is preserved.

## 6. Implementation Authorization

**AUTHORIZED:** build the local deterministic PoC exactly as frozen.

**NOT AUTHORIZED:**

- widening scope;
- adding external model evaluation;
- changing frozen protocol semantics;
- relaxing acceptance thresholds;
- silently replacing profile v2;
- skipping negative cases;
- modifying evidence after finalization;
- merging to main before formal closeout.

## 7. Final Disposition

**FROZEN — READY FOR IMPLEMENTATION**

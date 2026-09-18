# Agent Conformance Local Lifecycle PoC v0.1.1 — Successor Formal Run Design

**Status:** IMPLEMENTATION CANDIDATE — NOT YET AUTHORIZED FOR FORMAL EXECUTION

## Purpose

Correct only the evidence-runner defects found in the independent closeout review of formal run
`20260918T183130Z-acl-lifecycle-poc-v0.1`.

This successor does **not** change the reviewed PoC implementation. The implementation baseline remains:

`cfd85e809a541a136b478fa7605a7cf4ca798a2d`

The invalid prior run and its evidence remain immutable historical evidence.

## Required corrections

1. **One execution path**
   - One process owns the formal lifecycle sequence.
   - All JSON evidence and all audit records are emitted from the same live objects and results.
   - No synthetic or representative audit event list is permitted.

2. **Fresh post-denial evidence**
   - Initial v2 evidence used for invalidation is `rt-ev-v2-initial`.
   - After N+1 publication and stale C1 denial, the observer must create a distinct
     `rt-ev-v2-fresh` artifact.
   - The fresh artifact must have strictly later logical timestamp and event sequence than the initial v2 evidence.
   - R13 restoration must reference `rt-ev-v2-fresh`.

3. **Restored C2 authority**
   - C0 consumes the protected-resource authority.
   - After successful N+2 restoration and before C2 execution, trusted setup re-grants the same executor authority token exactly as the existing development lifecycle fixture does.
   - C2 must succeed exactly once.
   - Final protected-resource line count must equal 2.
   - C2 replay must fail with zero additional effect.

4. **Actual audit provenance**
   - The audit ledger is `h.audit` from the same harness driving C0/C1/N+1/N+2/C2.
   - Every audit payload is derived from the actual result or artifact just produced.
   - The authoritative ledger is serialized only after the formal lifecycle completes.
   - The tampered ledger is a deep-copied derivative of that actual ledger.
   - No hardcoded success outcome may appear in the audit evidence.

5. **Fail closed**
   - No assertion-only safety: explicit checks raise a fatal run error.
   - The runner must refuse PASS if:
     - implementation subtree differs from the reviewed baseline;
     - frozen artifact hash checks fail;
     - pytest is not 68 passed / 0 failed / 0 skipped / 0 xfailed;
     - C1 nonce was already seen before stale execution;
     - stale C1 changes the resource;
     - fresh evidence is not distinct and later;
     - R13 restoration does not reference the fresh evidence;
     - N+2 is not CONFORMANT @ epoch 3;
     - C2 does not succeed;
     - C2 does not add exactly one line;
     - final line count is not exactly 2;
     - C2 replay is not denied with zero effect;
     - actual audit chain fails;
     - actual causal ordering fails;
     - tampered copy is not detected.

6. **Run identity and preservation**
   - Use a new unique run ID.
   - Refuse to overwrite an existing evidence directory.
   - Never edit prior formal evidence.
   - Manifest is generated from finalized evidence files and includes SHA-256 + byte size.
   - Final classification is written only after all gates pass.

## Required causal order

`C1_issued < runtime_mutation < trigger_observed < N+1_published < C1_denied < post_change_evidence < R13_restore_eval < N+2_published < C2_issued < C2_effect`

The audit ledger must prove this ordering from the same execution.

## Classification

Only frozen classifications are permitted.

For this successor runner:

- all checks satisfied -> `CONFORMANCE_LIFECYCLE_POC_PASS`
- an executed proof requirement fails -> `CONFORMANCE_LIFECYCLE_POC_FAIL`
- evidence integrity/provenance becomes invalid -> `INCONCLUSIVE_EVIDENCE_INVALID`
- preflight/baseline/frozen invariant fails before scoring -> `STOP_BEFORE_SCORING`

## Execution gate

Creating this runner does **not** authorize execution.

Required sequence:

1. implement runner;
2. independent static review of runner;
3. development dry-run in a disposable worktree;
4. only then authorize a new formal run.

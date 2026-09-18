# Agent Conformance Local Lifecycle PoC v0.1.1 — Successor Formal Runner Review

**Runner candidate:** `958c37c792c2e6308afa78249dcfec7de72abeed`  
**Reviewed implementation baseline:** `cfd85e809a541a136b478fa7605a7cf4ca798a2d`

## Disposition

**PASS FOR DISPOSABLE DEVELOPMENT DRY-RUN**

**FORMAL RUN NOT AUTHORIZED**

## Scope verification

Comparison from the reviewed implementation baseline to the runner candidate shows no modification to:

- `conformance/`
- `fixtures/`
- `tests/`
- any frozen protocol/design artifact

The successor work is limited to:

- preservation of the invalid prior formal evidence;
- independent closeout review;
- successor formal-run design;
- successor runner implementation.

## Closure of prior evidence defects

### R1 — C2 authority/effect

Closed in runner design.

After successful N+2 restoration, the runner explicitly re-grants the executor's protected-resource authority before C2, matching the existing development lifecycle fixture.

The runner fails if:

- C2 is not granted;
- C2 does not increase the protected-resource line count by exactly one;
- line count is not exactly 2 after C2;
- replay adds any effect.

### R2 — Fresh post-denial evidence

Closed in runner design.

The invalidation path uses:

`rt-ev-v2-initial`

After C1 stale denial, the successor emits:

`rt-ev-v2-fresh`

The runner requires:

- distinct artifact IDs;
- later logical timestamp;
- later event sequence;
- R13 restoration evaluation bound exactly to `rt-ev-v2-fresh`.

### R3 — Synthetic audit provenance

Closed in runner design.

The successor uses `h.audit` from the same harness instance and process executing the lifecycle.

Each audit event payload is derived from the actual artifact/result immediately produced.

The authoritative ledger is serialized from `h.audit.records()`.

The tampered ledger is derived by deep-copy/tamper from that actual ledger.

There is no independent representative-event list and no hardcoded C2 success record.

## Additional controls

The runner now:

- defaults to development dry-run mode;
- requires both `--formal` and `ACL_FORMAL_RUN_AUTHORIZED=YES` for formal execution;
- refuses dirty worktrees;
- verifies the reviewed implementation subtree remains unchanged from `cfd85e8...`;
- verifies all eight frozen artifact blob IDs;
- refuses evidence-directory overwrite;
- runs the 68-test development suite;
- verifies the installed profile registry is frozen and contains exactly profile-v1/profile-v2;
- uses explicit fail-closed checks rather than Python `assert` for proof gates;
- generates one manifest from the evidence actually emitted;
- never edits the invalid prior formal evidence.

## Dry-run authorization

A single disposable development dry-run is authorized at runner candidate:

`958c37c792c2e6308afa78249dcfec7de72abeed`

Required command:

`python3 formal-runner-v0.1.1/run_formal.py`

Do **not** pass `--formal`.

Expected successful result:

`DEVELOPMENT_DRY_RUN_PASS`

The dry-run evidence must then be independently inspected before formal execution is authorized.

No merge to `main` is authorized.

# DBI-BIB-001 — Source Package

**Execution Package:** v0.1  
**Application:** Amazing Birthday  
**Source repository:** `fjventura20/development-by-intent`  
**Frozen source commit:** `c369215024c9f8a849daf11bd4b872d7ee566a7a`

## Generator-visible files

Before reconstruction freeze, each reconstruction engine instance may receive **only** these two application artifacts, byte-for-byte from the frozen source commit:

| Order | Path | Git blob SHA-1 | SHA-256 of file bytes |
|---|---|---|---|
| 1 | `examples/amazing-birthday/03-behavioral-baseline.md` | `7ef4356f657884d65dbd4462d85c1c81b3f6fa2a` | `4582d768b696bbce41729ff05475ff9a8edf86c7b55668aaa46a230690e66159` |
| 2 | `examples/amazing-birthday/04-durable-package/RECONSTRUCTION-PROMPT.md` | `2e37f47d99059238bd9484560e310d2f89744069` | `7d6d08196a825058fe677f0cf9b0367c4f8135a0ce50b2445bef54928f4084ce` |

These hashes are the same frozen two-artifact package used by the previously successful clean artifact-only Amazing Birthday replication.

## Visibility boundary

Before the reconstruction engine has produced its reconstruction-ready response, it must **not** receive:

- this experiment's test corpus;
- evaluator rubric or score anchors;
- prior Amazing Birthday outputs or scores;
- the development transcript;
- `06-validation.md`;
- historical test files;
- prior experiment reports;
- evaluator feedback;
- corrective or repair guidance;
- results from R1–R6 other than its own current session.

The operator may possess these materials; the reconstruction engine may not.

## Reconstruction input assembly

The operator must provide the two files in the order shown above and then the reconstruction instruction embodied in `RECONSTRUCTION-PROMPT.md`. No additional behavioral interpretation may be inserted by the operator.

If the execution interface requires wrapper text to delimit the two files, the wrapper may contain only neutral file-boundary labels such as:

`--- BEGIN FILE: <path> ---`

and

`--- END FILE: <path> ---`

No wrapper may restate, summarize, strengthen, weaken, or explain the application contract.

## Verification gate

Before launching R1, and again before each R2–R6 reconstruction, the operator must verify:

1. repository and frozen source commit resolve;
2. both paths exist at that commit;
3. Git blob SHA-1 values match the table above;
4. SHA-256 values computed from the exact bytes supplied to the target match the table above.

Any mismatch is a **BLOCKED** condition. Do not normalize line endings, reformat Markdown, trim whitespace, or substitute a later version.

## Source-package identity

For DBI-BIB-001, the phrase **same frozen intent specification** means exactly the two generator-visible files above at exactly the frozen source commit and hashes above.

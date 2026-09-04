# DBI-BIB-001 — Execution Package v0.1 Freeze Record

**Freeze ID:** `DBI-BIB-001-EXEC-FREEZE-001`  
**Experiment:** DbI Behavioral Identity Baseline Experiment v0.1  
**Execution package:** v0.1  
**Freeze date:** 2026-09-04  
**Status:** **FROZEN**  
**Execution authorized:** **NO**

## Protocol dependency

- Repository: `fjventura20/development-by-intent`
- Protocol path: `experiments/behavioral-identity-baseline-v0.1/PROTOCOL.md`
- Frozen protocol commit: `b9b6c86c017903cca061b4c2f7b798c82870f9c5`
- Frozen protocol Git blob: `1d06f02a9d331df279ee4417e23b4d52330b63f9`

## Authoritative execution-package snapshot

- Repository: `fjventura20/development-by-intent`
- Package directory: `experiments/behavioral-identity-baseline-v0.1/execution-package-v0.1/`
- Package snapshot commit: `00676a3343fbf786e3b72b32afcc6e5071582cb8`

The following file blobs constitute Execution Package v0.1:

| File | Git blob SHA-1 |
|---|---|
| `EVALUATION-PROCEDURE.md` | `50a02e1f445c9508aa467faae152a59ee2f05d7b` |
| `EVALUATOR-RUBRIC.md` | `0a78ee8657b6719a24a9c2b904c2bb96d3eab545` |
| `MANIFEST.schema.json` | `50192caf1871eed92a2d075a1a5cc86d091df01c` |
| `OPERATOR-INSTRUCTIONS.md` | `c20f720c2c489337c67d7eed5024342718756906` |
| `README.md` | `8202bbc5c1d7115398f231c2d2a317c2eb6e3c8c` |
| `SOURCE-PACKAGE.md` | `857897f42897813b84398c14ab5051d43886fb47` |
| `TEST-CORPUS.md` | `b483a6b1c76697989ae28ebad6e7af04fcd6e4ab` |

Later edits on any branch do not alter this freeze. Any semantic change to the source package, test corpus, scoring anchors, classification rules, evaluator procedure, runtime posture, manifest schema, operator instructions, or execution limits requires a new execution-package version or an explicitly versioned amendment frozen before affected execution.

## Generator-visible application source lock

Execution Package v0.1 binds DBI-BIB-001 to Amazing Birthday source commit:

`c369215024c9f8a849daf11bd4b872d7ee566a7a`

Generator-visible files:

1. `examples/amazing-birthday/03-behavioral-baseline.md`
   - Git blob: `7ef4356f657884d65dbd4462d85c1c81b3f6fa2a`
   - SHA-256: `4582d768b696bbce41729ff05475ff9a8edf86c7b55668aaa46a230690e66159`
2. `examples/amazing-birthday/04-durable-package/RECONSTRUCTION-PROMPT.md`
   - Git blob: `2e37f47d99059238bd9484560e310d2f89744069`
   - SHA-256: `7d6d08196a825058fe677f0cf9b0367c4f8135a0ce50b2445bef54928f4084ce`

## Frozen test corpus

Exact UTF-8 prompt payloads, no leading/trailing newline:

1. `Birthdate February 20, 1952`
2. `Birthdate June 23, 1956`
3. `Birthdate February 29, 1960`
4. `Birthdate November 9, 1989`
5. `Birthdate August 24, 1931`

The corpus runs once as Block A and once again in identical order as Block B within each of six fresh reconstructions, for 60 intended behavioral observations.

## Execution gate

**This freeze is not a GO.**

Hermes or any other operator may perform non-generative preflight, but must not invoke the reconstruction engine for DBI-BIB-001 until a separate authorization artifact explicitly references this frozen execution package and states `GO` or `EXECUTION AUTHORIZED`.

No execution request to Hermes is created by this freeze record.

## Next state

`READY FOR OPERATOR PREFLIGHT / AWAITING EXECUTION AUTHORIZATION`

# DBI-BIB-001 — Execution Package v0.1

**Experiment:** DbI Behavioral Identity Baseline Experiment v0.1  
**Protocol ID:** `DBI-BIB-001`  
**Package version:** `v0.1`  
**Package status:** PREPARED FOR FREEZE  
**Execution authorized:** **NO**  
**Operator:** Hermes Agent after a separate explicit GO

## Purpose

This package converts the frozen Baseline Experiment v0.1 protocol into an executable, auditable run specification. It fixes the source artifacts, test corpus, scoring rubric, variance metric, manifest schema, operator discipline, blinding procedure, and execution limits before behavioral results are observed.

## Frozen protocol dependency

Authoritative protocol:

- Repository: `fjventura20/development-by-intent`
- Path: `experiments/behavioral-identity-baseline-v0.1/PROTOCOL.md`
- Frozen protocol commit: `b9b6c86c017903cca061b4c2f7b798c82870f9c5`
- Frozen protocol Git blob: `1d06f02a9d331df279ee4417e23b4d52330b63f9`

If this execution package conflicts with the frozen protocol, the protocol governs and execution must stop for amendment rather than silently choosing one interpretation.

## Package contents

1. `SOURCE-PACKAGE.md` — exact generator-visible Amazing Birthday source artifacts and verification hashes.
2. `TEST-CORPUS.md` — exact five test payloads, order, SHA-256 hashes, and two-block repetition structure.
3. `EVALUATOR-RUBRIC.md` — frozen 0–4 score anchors, violation severities, and SAME / SAME_WITH_VARIANCE / DIFFERENT classification rules.
4. `EVALUATION-PROCEDURE.md` — evaluator role assignment, blinding, randomization, score locking, agreement gates, and variance calculations.
5. `MANIFEST.schema.json` — required machine-readable run manifest schema.
6. `OPERATOR-INSTRUCTIONS.md` — preflight, runtime lock, isolation, capture, retry, deviation, evidence, analysis, and stop procedures.

A separate `EXECUTION-PACKAGE-FREEZE.md` outside this directory will identify the immutable package commit and file hashes after all package files are complete.

## Core run shape

- Reconstruction engine: Anthropic Claude, model `claude-sonnet-4-6`.
- Tool posture: no tools.
- Independent reconstructions: R1–R6.
- Test corpus: T1–T5.
- Repetitions: Block A then identical Block B in each reconstructed session.
- Intended behavioral outputs: 60.
- Primary numeric representation: four-dimensional 0–4 behavior vector.
- Distance metric: Manhattan distance, range 0–16.
- Primary comparison: 30 within-reconstruction distances vs 150 between-reconstruction distances per evaluator.
- Evaluators: two independent roles, neither ChatGPT nor Hermes; exact provider/model/runtime identities locked before candidate access.
- Automatic expansion: prohibited.

## Value-Cost Gate

The initial run stops at six reconstructions and 60 intended behavioral observations. No additional reconstruction is authorized merely to increase sample size. Expansion is permitted only after the initial evidence is reviewed and an explicit new authorization determines that additional observations are likely to resolve genuine ambiguity.

## Execution gate

This package is **not** an instruction to start the experiment.

Hermes may execute DBI-BIB-001 only after the final package freeze record exists and a separate explicit authorization identifies the frozen execution package and says `GO` / `EXECUTION AUTHORIZED`.

Until then, valid disposition is:

`PREPARED — NOT AUTHORIZED FOR EXECUTION`

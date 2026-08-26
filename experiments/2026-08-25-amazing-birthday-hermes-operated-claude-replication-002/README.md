# Amazing Birthday — Hermes-Operated Claude Replication 002

**Status:** ACTIVE — dispatched 2026-08-25 20:28 America/New_York  
**Experiment ID:** BP-AB-CLAUDE-REP-002  
**Mode:** same-target clean replication, artifact-only  
**Operator:** Hermes Agent  
**Target:** fresh Anthropic Claude Code session  
**Independent reviewer:** ChatGPT  
**Frozen source:** `c369215024c9f8a849daf11bd4b872d7ee566a7a`  
**Live transfer:** `20260826T002800Z-behavioral-portability-claude-replication-002` on `mailbox/main`

## Why this replication exists

Experiment 001 produced strong passing behavior on all three withheld dates, but its first reconstruction response and first Test 1 response were not captured immutably on their first invocation. The independent review therefore classified the run formally INDETERMINATE despite the strong behavioral PASS signal.

This replication isolates that uncertainty. It intentionally keeps the scientific variables unchanged and changes only the operator evidence-capture procedure.

## Research question

> When experiment 001 is repeated with the same frozen target artifacts, provider family, isolation posture, test dates, and rubric—but every first inference is atomically preserved on its first call—does the reconstructed Amazing Birthday application satisfy the preregistered v1.0 acceptance criteria?

## Frozen target inputs

Before freeze, the fresh Claude session receives only:

1. `examples/amazing-birthday/03-behavioral-baseline.md`  
   SHA-256 `4582d768b696bbce41729ff05475ff9a8edf86c7b55668aaa46a230690e66159`
2. `examples/amazing-birthday/04-durable-package/RECONSTRUCTION-PROMPT.md`  
   SHA-256 `7d6d08196a825058fe677f0cf9b0367c4f8135a0ce50b2445bef54928f4084ce`

The frozen source commit must be fetched and the hashes verified **before** target launch.

## Variables held constant

- Amazing Birthday application;
- same frozen source commit;
- same two pre-freeze artifacts;
- Anthropic Claude Code target mechanism;
- fresh target session;
- no target tools (`--allowedTools ''` posture);
- same reconstruction freeze rule;
- same v1.0 tests and order;
- same scoring rubric and thresholds;
- same no-repair/no-hint/no-regeneration rule.

## Only intended change: evidence capture

The operator must write the reconstruction and each test's raw response to disk on the **first invocation**.

No prompt may be re-issued to recover a lost response. If any first-call artifact is missing, truncated, or not independently preserved, the experiment stops and returns **INDETERMINATE**.

## Frozen tests

1. `Birthdate November 9, 1989`
2. `Birthdate February 29, 1960`
3. `Birthdate June 23, 1956`

## Critical requirements

1. Exact-date integrity.
2. Generalization to withheld inputs.

## Per-output scoring

Ten dimensions, each 0/1/2:

- historical opening;
- selectivity;
- exact-date discipline;
- significance;
- narrative coherence;
- lifetime framing;
- breadth;
- factual care;
- ending synthesis;
- trigger behavior.

PASS = 17–20 plus both critical requirements.  
PARTIAL = 12–16 plus both critical requirements.  
FAIL = 0–11 or a critical failure.

## Experiment-level rule

- **PASS** — all three first outputs PASS and there is no material contamination, repair, or evidence-capture defect.
- **PARTIAL** — at least one output PARTIAL, none FAIL, evidence remains valid.
- **FAIL** — any output behaviorally FAILS.
- **INDETERMINATE** — isolation/evidence/execution defect prevents reliable interpretation.
- **BLOCKED** — fresh target cannot be executed.

## Required response evidence

Hermes must return environment, artifact provenance, first-call reconstruction JSON/prose, first-call JSON/prose for all three tests, operator score, failures, and next-experiment recommendation. ChatGPT will independently review before final classification.

## Interpretation discipline

This run is a replication, not an optimization attempt. Do not add web access, change the test set, alter the frozen artifacts, add requirements, or repair the application. Those would introduce new variables and belong in later experiments.
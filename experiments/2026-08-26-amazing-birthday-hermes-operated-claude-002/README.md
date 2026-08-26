# Amazing Birthday — Hermes-Operated Claude Portability Replication 002

**Status:** PREREGISTERED  
**Mode:** cross-provider, artifact-only clean-room replication  
**Application:** Amazing Birthday  
**Operator:** Hermes Agent  
**Target provider:** Anthropic Claude via a genuinely fresh Claude Code session  
**Independent reviewer:** ChatGPT  
**Frozen source commit:** `c369215024c9f8a849daf11bd4b872d7ee566a7a`  
**Preregistration date:** 2026-08-26 UTC

## Research question

Can the frozen Amazing Birthday two-artifact package reproduce the prior strong Claude behavioral result in a second genuinely fresh Claude session when every reconstruction/test response is captured immutably on its first invocation?

## Reason for replication

Experiment 001 produced behavioral PASS scores on all three withheld dates but was formally INDETERMINATE because the first reconstruction response and first Test 1 response were not contemporaneously preserved. This replication keeps the scientific variables frozen and changes only the operator capture procedure.

## Frozen target artifact set

Before reconstruction freezes, Claude may receive only:

1. `03-behavioral-baseline.md`
2. `RECONSTRUCTION-PROMPT.md`

Their SHA-256 hashes are frozen as:

- `03-behavioral-baseline.md`: `4582d768b696bbce41729ff05475ff9a8edf86c7b55668aaa46a230690e66159`
- `RECONSTRUCTION-PROMPT.md`: `7d6d08196a825058fe677f0cf9b0367c4f8135a0ce50b2445bef54928f4084ce`

The target must not receive the development transcript, prior outputs, experiment-001 outputs, test dates, scoring rubric, behavioral tests, Grok/ChatGPT results, or repair instructions before freeze.

## Operator pre-flight

Before launching the target:

1. Fetch/verify source commit `c369215024c9f8a849daf11bd4b872d7ee566a7a`.
2. Verify both target-artifact SHA-256 values above.
3. Create a new temporary working directory containing only the two allowed artifacts.
4. Launch a new Claude session; do not resume any prior Claude session.
5. Record Claude Code version, target model(s), permissions/tool envelope, cwd, session id, and contamination risks.

If a fresh isolated session cannot be established, stop as BLOCKED/INDETERMINATE rather than substituting a contaminated run.

## Mandatory first-call evidence capture

Every target invocation must be written to durable raw output on the **first call** before the next prompt is sent.

Required procedure:

- capture the full machine-readable Claude envelope and the verbatim prose response for reconstruction and each test;
- use an atomic/tee-style capture path so terminal display and file preservation happen in the same first invocation;
- record SHA-256 for each raw first-call artifact immediately;
- do not re-issue any prompt for capture;
- if first-call capture fails for reconstruction or any scored test, stop the experiment and classify it INDETERMINATE.

No memory reconstruction from operator scrollback is accepted as a substitute for raw first-call evidence.

## Freeze point

Freeze when Claude has received only the two allowed artifacts, established reusable Amazing Birthday behavior, and stated it is ready for a test invocation.

No application repair or instruction changes are allowed until all three raw first-run outputs have been captured.

## Frozen v1.0 tests

After freeze, run in the same target session, in order:

1. `Birthdate November 9, 1989`
2. `Birthdate February 29, 1960`
3. `Birthdate June 23, 1956`

No hints, corrections, regeneration, repair, or prompt re-issue between tests.

The test-set SHA-256 is frozen:

- `behavioral-tests.md`: `35d87d8725f30a620e2a97ff14a51cc38a31453a18aa6a8dea889ed6a90a26a1`

The scoring rubric SHA-256 is frozen:

- `06-validation.md`: `cb3299e4bf4ab110b8b88dd67127586f16f5b53a21a6c60e4dd88cba23fd223d`

## Scoring

Per output:

- PASS: 17–20 and both critical requirements satisfied
- PARTIAL: 12–16 and both critical requirements satisfied
- FAIL: 0–11 or critical failure
- INDETERMINATE: insufficient reliable evidence

Critical requirements:

1. exact-date integrity;
2. generalization to withheld input.

Experiment level:

- PASS: all three first-run outputs PASS, first-call evidence is complete, and no material contamination/repair occurred;
- PARTIAL: at least one PARTIAL, none FAIL, evidence complete, no material contamination;
- FAIL: any behavioral FAIL;
- INDETERMINATE: isolation/evidence/execution defect prevents reliable interpretation;
- BLOCKED: fresh Claude target cannot be executed.

Hermes scores preliminarily. ChatGPT independently reviews the preserved raw evidence.

## Interpretation limit

A PASS supports only the bounded claim that the same frozen Amazing Birthday artifact-only package reproduced qualifying behavior in a second fresh Claude run under the recorded conditions. It is evidence about repeatability and cross-provider portability for this application, not universal portability.

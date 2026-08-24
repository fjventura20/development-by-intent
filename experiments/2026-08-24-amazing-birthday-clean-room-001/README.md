# Amazing Birthday Clean-Room Reconstruction 001

**Status:** preregistered; awaiting execution in a genuinely fresh AI environment  
**Mode:** artifact-only reconstruction  
**Application:** Amazing Birthday  
**Frozen source commit:** `c369215024c9f8a849daf11bd4b872d7ee566a7a`  
**Preregistration date:** 2026-08-24

## Purpose

This is the first public clean-room reconstruction run for the canonical Amazing Birthday example.

The question is deliberately narrow:

> Can a fresh AI environment reconstruct the recognizable Amazing Birthday application from the derived artifact-only package, then generalize that behavior to previously unused birthdates without repair?

This experiment does **not** test whether the original development transcript alone is sufficient. It does **not** test whether every AI model can reproduce the application. It does **not** permit conversational repair before scoring.

## Why this file exists before the run

This manifest freezes the experiment before any test output is observed. The artifact set, test inputs, scoring rubric, and failure rules must not be changed in response to the result.

## Clean-room requirement

The reconstruction must occur in a new conversation, project, agent, or equivalent environment that has no prior Amazing Birthday context or memory.

The current development conversation is **not eligible** because it already contains the application history, transcript, behavioral baseline, and test design.

Record any uncertainty about isolation as contamination rather than silently treating the run as clean.

## Frozen artifact set

### Supply to the reconstructing AI before testing

Supply **only** these two files from commit `c369215024c9f8a849daf11bd4b872d7ee566a7a`:

1. `examples/amazing-birthday/03-behavioral-baseline.md`
2. `examples/amazing-birthday/04-durable-package/RECONSTRUCTION-PROMPT.md`

Do not supply:

- `TUTORIAL.md`;
- the original development transcript;
- `behavior-derivation.md`;
- any original Amazing Birthday outputs;
- the withheld tests before reconstruction is frozen;
- any later repair instructions.

The reconstructing AI should acknowledge that Amazing Birthday is ready and wait for a test invocation, as required by the reconstruction prompt.

## Freeze point

The reconstruction is frozen when the AI has completed the reconstruction step and stated that Amazing Birthday is ready for a test invocation.

From that point until all three test outputs have been captured:

- do not clarify the application behavior;
- do not correct mistakes;
- do not provide hints;
- do not expose the original transcript;
- do not modify the behavioral baseline;
- do not regenerate a test merely because the result is weak.

The first outputs are evidence.

## Frozen v1.0 test set

Run these invocations in order in the same reconstructed environment.

### Test 1

```text
Birthdate November 9, 1989
```

### Test 2

```text
Birthdate February 29, 1960
```

### Test 3

```text
Birthdate June 23, 1956
```

These dates were checked against the authoritative development transcript before this experiment was preregistered and do not occur there as development examples.

## Scoring

After all raw outputs are preserved, evaluate each run against:

- `examples/amazing-birthday/06-validation.md`
- `examples/amazing-birthday/tests/behavioral-tests.md`

Use the frozen v1.0 rubric. Do not revise the threshold after seeing the result.

Critical failures include loss of exact-date integrity or failure to generalize to new input.

Final classification must be one of:

- `PASS`
- `PARTIAL`
- `FAIL`
- `INDETERMINATE`

## Environment record

Before reconstruction, record:

- provider/platform;
- model name and version if known;
- execution date and local time zone;
- whether web/search tools are available;
- whether memory is enabled;
- whether the environment belongs to an existing project;
- system/project instructions if known and relevant;
- exact files supplied;
- any suspected contamination.

## Evidence to preserve

Create a result directory after execution containing at least:

```text
results/
├── environment.md
├── reconstruction-transcript.md
├── test-1-output.md
├── test-2-output.md
├── test-3-output.md
└── score.md
```

Raw outputs should be copied without retrospective improvement.

## Interpretation rule

A successful run supports only this claim:

> In the recorded environment, the frozen artifact-only package reconstructed enough of Amazing Birthday's behavioral identity to satisfy the preregistered v1.0 criteria on new inputs.

A failed or partial run is equally important evidence about the limits of the current durability package.

## Next phase after scoring

Only after the first-run result has been classified may a separate repair phase begin. Any repaired run must be stored and reported separately from this preregistered first-run result.

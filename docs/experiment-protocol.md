# Experiment Protocol

Use this protocol for reconstruction and durability experiments.

## 1. Declare the hypothesis

State one falsifiable question before running the experiment.

Example: "A fresh AI session given only the original transcript will reproduce all required Fair Price behaviors in the baseline test set."

## 2. Freeze the baseline

Record:

- baseline artifact version or commit
- behavioral test set
- expected results
- any known nondeterministic tolerances

Do not change the baseline after observing the reconstruction.

## 3. Record the environment

Capture:

- model/provider
- model version/date if known
- system or project instructions that materially affect behavior
- tools available
- date/time

## 4. Supply only declared inputs

For a transcript-only experiment, do not provide derived specifications.

For an artifact-only experiment, do not provide the original transcript.

Record any accidental leakage or prior context as a contamination risk.

## 5. Reconstruct without repair

Create the reconstructed application and run the baseline tests before correcting failures.

## 6. Classify outcomes

For each test:

- PASS — expected behavior reproduced
- PARTIAL — intent recognizable but materially incomplete
- FAIL — behavior missing or contradictory
- INDETERMINATE — test cannot distinguish success reliably

## 7. Preserve raw evidence

Where practical, preserve prompts, outputs, transcripts, test records, and any scripts used for scoring.

## 8. Interpret conservatively

A failed reconstruction may indicate omitted source material, execution failure by the reconstructing model, or an original generation artifact. Do not select one explanation without evidence.

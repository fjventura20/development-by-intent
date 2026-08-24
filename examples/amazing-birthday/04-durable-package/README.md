# 04 — Durable Package

This directory contains the **public reference reconstruction package** for Amazing Birthday.

It is important to distinguish this from any historical package produced during the original experiment. Unless an artifact is explicitly identified as original evidence, the files here are derived/publication artifacts intended for reproducible testing.

## Package contents

For the initial public artifact-only reconstruction, use:

- `../03-behavioral-baseline.md` — the behavioral contract;
- `RECONSTRUCTION-PROMPT.md` — the instruction used to instantiate the application in a fresh environment;
- `../tests/behavioral-tests.md` — withheld/new-input tests;
- `../06-validation.md` — scoring and interpretation rules.

The original transcript is intentionally excluded from an **artifact-only** run.

For a **full-transcript** reconstruction experiment, use the verbatim material in `../02-development-transcript/` according to the repository-wide experiment protocol and record that the transcript was supplied.

## Why two reconstruction modes matter

A transcript-rich reconstruction asks whether preserved development history is sufficient to recover behavior.

An artifact-only reconstruction asks a harder compression question: whether a smaller derived package retains enough behavioral information to recover the same application identity.

These are different experiments and their results should not be mixed.

## Versioning rule

If the behavioral baseline, reconstruction prompt, or tests change, record the new commit SHA with every result. Do not silently revise a baseline after seeing a failure.

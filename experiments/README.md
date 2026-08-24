# Experiments

Each experiment should have its own directory containing a preregistration or protocol plus enough raw evidence to reproduce and audit the result.

Recommended naming:

`YYYY-MM-DD-short-experiment-name`

## Completed

### Amazing Birthday — artifact-only clean-room reconstruction 001

**Result: PASS — 60/60 across three preregistered first-run tests.**

The experiment reconstructed Amazing Birthday in a fresh ChatGPT conversation using only the frozen behavioral baseline and reconstruction prompt, then exercised three birthdates that were withheld from the development transcript. No repair, clarification, hint, or regeneration occurred before scoring.

See [`2026-08-24-amazing-birthday-clean-room-001/`](2026-08-24-amazing-birthday-clean-room-001/) for the preregistration and preserved results.

## Suggested next experiments

1. Amazing Birthday — repeat artifact-only reconstruction in another fresh run
2. Amazing Birthday — cross-model/provider artifact-only reconstruction
3. Amazing Birthday — full-transcript reconstruction comparison
4. Amazing Birthday — minimum recovery-floor / artifact-removal experiment
5. Fair Price — full-transcript reconstruction
6. Fair Price — artifact-only reconstruction
7. Development-cycle comparison against a bounded conventional implementation

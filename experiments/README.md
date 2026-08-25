# Experiments

Each experiment should have its own directory containing a preregistration or protocol plus enough raw evidence to reproduce and audit the result.

Recommended naming:

`YYYY-MM-DD-short-experiment-name`

## Active

### Amazing Birthday — Hermes-operated Claude portability 001

**Status: PREREGISTERED AND DISPATCHED.**

Hermes is operating a clean cross-provider reconstruction against Anthropic Claude using only the same frozen Amazing Birthday artifact-only package used by the prior ChatGPT clean-room experiment. The three v1.0 behavioral witnesses remain withheld from the Claude target until reconstruction is frozen. Hermes will preserve raw outputs and perform preliminary scoring; ChatGPT will independently review the returned evidence before the experiment status is finalized.

See [`2026-08-25-amazing-birthday-hermes-operated-claude-001/`](2026-08-25-amazing-birthday-hermes-operated-claude-001/).

## Completed

### Amazing Birthday — artifact-only clean-room reconstruction 001

**Result: PASS — 60/60 across three preregistered first-run tests.**

The experiment reconstructed Amazing Birthday in a fresh ChatGPT conversation using only the frozen behavioral baseline and reconstruction prompt, then exercised three birthdates that were withheld from the development transcript. No repair, clarification, hint, or regeneration occurred before scoring.

See [`2026-08-24-amazing-birthday-clean-room-001/`](2026-08-24-amazing-birthday-clean-room-001/) for the preregistration and preserved results.

### Amazing Birthday — Grok reconstruction 001

**Result: PRELIMINARY BEHAVIORAL PASS — factual regression not independently verified.**

Grok received the original Amazing Birthday transcript and durable package plus the instruction to create the micro-app. It autonomously selected a platform-native skill structure, reported completing reconstruction in approximately 1 minute 13 seconds, and generated a recognizable Amazing Birthday response in approximately 26 seconds.

This was an observational cross-platform reconstruction, not a preregistered clean-room test. The record preserves the output, known limitations, and the boundary between the demonstrated result and the larger portability and enterprise hypotheses.

See [`2026-08-25-amazing-birthday-grok-reconstruction-001/`](2026-08-25-amazing-birthday-grok-reconstruction-001/).

## Suggested next experiments

1. Amazing Birthday — repeat cross-provider artifact-only reconstruction
2. Amazing Birthday — repeat artifact-only reconstruction in another fresh run
3. Amazing Birthday — full-transcript reconstruction comparison
4. Amazing Birthday — minimum recovery-floor / artifact-removal experiment
5. Fair Price — full-transcript reconstruction
6. Fair Price — artifact-only reconstruction
7. Development-cycle comparison against a bounded conventional implementation
8. Stateful micro-app reconstruction with persistent data
9. Multi-step process-cluster reconstruction

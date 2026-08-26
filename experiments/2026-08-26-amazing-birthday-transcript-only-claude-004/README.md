# Amazing Birthday — Transcript-Only Claude 004

**Status:** PREREGISTERED / DISPATCHED  
**Experiment ID:** BP-AB-TRANSCRIPT-CLAUDE-004  
**Transfer:** `20260826T204100Z-behavioral-portability-transcript-only-claude-004`  
**Mode:** clean-room transcript-only comparison  
**Operator:** Hermes Agent  
**Target:** fresh Claude environment  
**Independent reviewer:** ChatGPT  
**Frozen source commit:** `c369215024c9f8a849daf11bd4b872d7ee566a7a`

## Research question

Does the canonical Amazing Birthday development transcript, by itself, preserve enough behavioral identity to pass the same frozen v1.0 withheld tests on a fresh Claude target that the two-artifact durability package passed in Claude replication 002?

## Why this experiment

Gemini 003 is terminal BLOCKED before target invocation because the required Gemini CLI is absent on the Hermes host. Rather than weaken that protocol or install a missing prerequisite autonomously, the next smallest high-value uncertainty is artifact dependence: whether the durability package adds measurable reconstruction value beyond the original development transcript.

## Frozen independent variable

Only the preservation input class changes relative to clean Claude replication 002:

- **Replication 002:** behavioral baseline + reconstruction prompt.
- **Experiment 004:** canonical development transcript only.

Provider family, clean-room intent, no-tools target, freeze rule, test sequence, rubric, no-repair rule, first-call evidence discipline, and independent-review requirement remain fixed as closely as the recorded environment permits.

## Phase A target input

Before freeze the target may receive only:

`examples/amazing-birthday/02-development-transcript/amazing_birthday_transcript.txt`

Frozen at source commit `c369215024c9f8a849daf11bd4b872d7ee566a7a`; Git blob SHA:

`bab34913805c625b9bae46b54169b6decc447cd6`

The target must not receive the behavioral baseline, reconstruction prompt, durability package, prior outputs, test dates, rubric, prior scores/results, or repair guidance before freeze.

## Withheld tests and rubric

After freeze only:

- `examples/amazing-birthday/06-validation.md` — SHA-256 `5c7b6598e21803fc755ab58d79cd4649d095546834b261927617eeb024942b4b`
- `examples/amazing-birthday/tests/behavioral-tests.md` — SHA-256 `cec68a77b5df286c37155159fa3449e4d3651e36309cb27970e903f997a5c27b`

Frozen test order:

1. `Birthdate November 9, 1989`
2. `Birthdate February 29, 1960`
3. `Birthdate June 23, 1956`

## Comparator

Claude replication 002 is not rerun or rescored. Its frozen comparator remains:

- Hermes operator: 20/20, 20/20, 20/20;
- ChatGPT independent: **19/20, 19/20, 17/20**;
- final disposition: **PASS**.

Scorer disagreement is preserved.

## Preflight / BLOCKED rule

Before any target call Hermes must demonstrate using existing credentials/configuration only:

1. usable Claude CLI/Claude Code and existing authentication;
2. fresh isolated target context with no prior Amazing Birthday memory/context;
3. genuine no-tools target for reconstruction and tests;
4. frozen-source verification of transcript blob SHA and withheld test/rubric hashes;
5. exact target model identifier frozen before reconstruction.

If any requirement cannot be demonstrated, return **BLOCKED**. Do not initiate login, install paid services, create credentials, purchase/change subscriptions, weaken isolation, or substitute providers/models.

## Freeze / first-call / no-repair rules

Freeze when the target has reconstructed reusable Amazing Birthday behavior from the transcript alone and states readiness for testing. No application instruction changes after freeze.

Atomically preserve the **first** reconstruction response and first response to each test. No prompt may be re-issued for evidence capture. Lost/truncated/re-issued first-call evidence makes the run **INDETERMINATE**.

No correction, hint, regeneration, clarification, prompt repair, model fallback, or provider fallback is allowed before all raw first outputs are preserved.

## Frozen scoring

Ten dimensions, 0–2 each: historical opening, selectivity, exact-date discipline, significance, narrative coherence, lifetime framing, breadth, factual care, ending synthesis, trigger behavior.

Per-output PASS requires 17–20 plus both critical requirements:

1. exact-date integrity;
2. generalization to withheld input.

Experiment-level PASS requires all three outputs PASS and no material contamination, repair, provider/model fallback, or first-call evidence defect.

## Required evidence

Preserve environment/model/isolation metadata, exact source verification, raw first reconstruction, all three raw first test outputs, operator scoring, failures/contamination, a transcript-only versus frozen replication-002 comparison, and an independent review.

## Interpretation limit

A PASS would show only that the canonical transcript was sufficient in the recorded Claude environment under this frozen protocol. Comparison with replication 002 may inform artifact dependence, but one paired comparison does not establish that durability packages are unnecessary or universally superior/inferior.

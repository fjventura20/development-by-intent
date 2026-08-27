# Amazing Birthday — Transcript-Only Claude 004

**Status:** **TERMINAL — INDETERMINATE formal / strong behavioral PASS signal**. Independent review concurs that the first-call evidence defect prevents a formal PASS; clean capture replication 005 was executed separately.  
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

Gemini 003 is terminal BLOCKED before target invocation because the required Gemini CLI is absent on the Hermes host. Rather than weaken that protocol or install a missing prerequisite autonomously, the next smallest high-value uncertainty was artifact dependence: whether the durability package adds measurable reconstruction value beyond the original development transcript.

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

- `examples/amazing-birthday/06-validation.md` — SHA-256 `cb3299e4bf4ab110b8b88dd67127586f16f5b53a21a6c60e4dd88cba23fd223d`
- `examples/amazing-birthday/tests/behavioral-tests.md` — SHA-256 `35d87d8725f30a620e2a97ff14a51cc38a31453a18aa6a8dea889ed6a90a26a1`

> **v0.1.1 amendment note.** The original v0.1 hashes did not match the canonical SHA-256 of those files at the frozen source commit. Verified 2026-08-27 before any target invocation; v0.1.1 corrected only those hashes. No target invocation occurred before the amendment.

Frozen test order:

1. `Birthdate November 9, 1989`
2. `Birthdate February 29, 1960`
3. `Birthdate June 23, 1956`

## Comparator

Claude replication 002 is not rerun or rescored. Its frozen comparator remains:

- Hermes operator: **20/20, 20/20, 20/20**;
- ChatGPT independent: **19/20, 19/20, 17/20**;
- final disposition: **PASS**.

Scorer disagreement is preserved.

## Preflight / BLOCKED rule

Before any target call Hermes had to demonstrate using existing credentials/configuration only:

1. usable Claude CLI/Claude Code and existing authentication;
2. fresh isolated target context with no prior Amazing Birthday memory/context;
3. genuine no-tools target for reconstruction and tests;
4. frozen-source verification of transcript blob SHA and withheld test/rubric hashes;
5. exact target model identifier frozen before reconstruction.

If any requirement could not be demonstrated, return **BLOCKED**. Do not initiate login, install paid services, create credentials, purchase/change subscriptions, weaken isolation, or substitute providers/models.

## Freeze / first-call / no-repair rules

Freeze when the target has reconstructed reusable Amazing Birthday behavior from the transcript alone and states readiness for testing. No application instruction changes after freeze.

Atomically preserve the **first** reconstruction response and first response to each test. No prompt may be re-issued for evidence capture. Lost/truncated/re-issued first-call evidence makes the run **INDETERMINATE**.

No correction, hint, regeneration, clarification, prompt repair, model fallback, or provider fallback is allowed before all raw first outputs are preserved.

## Frozen scoring

Ten dimensions, 0–2 each: historical opening, selectivity, exact-date discipline, significance, narrative coherence, lifetime framing, breadth, factual care, ending synthesis, trigger behavior.

Per-output PASS requires 17–20 plus both critical requirements: exact-date integrity and generalization to withheld input.

Experiment-level PASS requires all three outputs PASS and no material contamination, repair, provider/model fallback, or first-call evidence defect.

## Execution result

004 produced strong visible behavioral output. Hermes scored the visible three tests **20/20, 20/20, 20/20** and both critical behavioral requirements appeared satisfied.

However, the operator capture pipeline `claude ... | tee FILE | head -c 200` caused first-call raw JSON truncation at the 8,192-byte pipe-buffer boundary for Test 2 and Test 3. Because those first-call envelopes are incomplete, the frozen evidence rule makes the formal result **INDETERMINATE**. No later re-issue may substitute for those first calls.

Independent review therefore concurs with the formal INDETERMINATE disposition. The visible behavioral content remains a strong PASS signal, but it is not promoted to a clean formal PASS.

## Successor

A separately preregistered clean capture replication was run as:

`BP-AB-TRANSCRIPT-CLAUDE-REP-005`

Record: [`../2026-08-27-amazing-birthday-transcript-only-claude-replication-005/`](../2026-08-27-amazing-birthday-transcript-only-claude-replication-005/)

005 eliminated the 004 capture defect but independently exposed a second protocol problem: the target's first reconstruction response did not reach the preregistered readiness/freeze state before withheld testing. 005 is therefore also formally INDETERMINATE, despite PASS-strength behavioral outputs.

## Interpretation limit

004 shows that transcript-only preservation can evoke recognizable, strong Amazing Birthday behavior in the recorded Claude environment, but its evidence-capture defect prevents a clean formal comparison with replication 002. It must not be used as a substitute for the clean artifact-only PASS.

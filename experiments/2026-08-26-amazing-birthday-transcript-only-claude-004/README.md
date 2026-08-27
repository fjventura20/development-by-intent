# Amazing Birthday — Transcript-Only Claude 004

**Status:** EXECUTED (operator); INDETERMINATE on evidence-capture front, strong behavioral PASS signal — awaiting ChatGPT independent review and clean replication
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

- `examples/amazing-birthday/06-validation.md` — SHA-256 `cb3299e4bf4ab110b8b88dd67127586f16f5b53a21a6c60e4dd88cba23fd223d` <!-- v0.1.1 corrected from `5c7b6598...` -->
- `examples/amazing-birthday/tests/behavioral-tests.md` — SHA-256 `35d87d8725f30a620e2a97ff14a51cc38a31453a18aa6a8dea889ed6a90a26a1` <!-- v0.1.1 corrected from `cec68a77...` -->

> **v0.1.1 amendment note.** The original v0.1 hashes (`5c7b6598...`, `cec68a77...`) did not match the canonical SHA-256 of those files at the frozen source commit. Verified 2026-08-27 by `git show <commit>:path | sha256sum`. Preflight BLOCKED on this defect; v0.1.1 supersedes with the canonical hashes. No target invocation occurred before this amendment. Original v0.1 hashes preserved in the BLOCKED file for audit.

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

**Preflight on 2026-08-27 (v0.1):** BLOCKED at item 4. Two withheld-test SHA-256 hashes did not match canonical content. See v0.1.1 amendment below.

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

## Protocol amendment: v0.1.1, 2026-08-27 — SHA-256 correction

**Reason.** Preflight on 2026-08-27 returned BLOCKED at item 4 (frozen-source verification).
The protocol's recorded SHA-256 hashes for the two withheld-test files did not match the
canonical SHA-256 of those files at the frozen source commit. Specifically:

| Artifact | v0.1 (incorrect) SHA-256 | v0.1.1 (canonical) SHA-256 |
|---|---|---|
| `06-validation.md` | `5c7b6598e21803fc755ab58d79cd4649d095546834b261927617eeb024942b4b` | `cb3299e4bf4ab110b8b88dd67127586f16f5b53a21a6c60e4dd88cba23fd223d` |
| `tests/behavioral-tests.md` | `cec68a77b5df286c37155159fa3449e4d3651e36309cb27970e903f997a5c27b` | `35d87d8725f30a620e2a97ff14a51cc38a31453a18aa6a8dea889ed6a90a26a1` |

The transcript blob SHA (`bab349138...`) was correct in v0.1 and is unchanged.

**Verification commands:**

```text
git rev-parse c369215024c9f8a849daf11bd4b872d7ee566a7a:examples/amazing-birthday/06-validation.md
# → 597174416493804bc84299e1f8dd2b0524f8a932 (git blob SHA, distinct from content SHA-256)

git show c369215024c9f8a849daf11bd4b872d7ee566a7a:examples/amazing-birthday/06-validation.md | sha256sum
# → cb3299e4bf4ab110b8b88dd67127586f16f5b53a21a6c60e4dd88cba23fd223d  -
```

**Audit.** Full preflight failure record:
[`results/preflight-BLOCKED-2026-08-27.md`](results/preflight-BLOCKED-2026-08-27.md).

**Scope of the amendment.** Only the two SHA-256 hashes above. No change to the experiment
design, frozen source commit, target isolation, target input class, withheld-tests bank,
test order, scoring rubric, freeze rule, no-repair rule, or interpretation limit.

**No contamination risk.** Per the BLOCKED rule, no target session was launched before this
amendment. The frozen source commit and all withheld artifacts are unchanged.

**Effective date.** 2026-08-27 (operative on execution).


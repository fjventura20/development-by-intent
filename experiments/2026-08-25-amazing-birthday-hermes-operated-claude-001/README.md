# Amazing Birthday — Hermes-Operated Claude Portability 001

**Status:** PREREGISTERED  
**Mode:** cross-provider, artifact-only reconstruction  
**Application:** Amazing Birthday  
**Operator:** Hermes Agent  
**Target provider:** Anthropic Claude via a fresh Claude Code session  
**Independent reviewer:** ChatGPT  
**Frozen source commit:** `c369215024c9f8a849daf11bd4b872d7ee566a7a`  
**Preregistration date:** 2026-08-25

## Research question

> Can Hermes autonomously operate a clean Claude reconstruction using only the frozen Amazing Birthday artifact-only package, withhold the behavioral witnesses until reconstruction is frozen, execute the three v1.0 tests without repair, and preserve enough evidence for independent scoring?

This experiment tests two things simultaneously but records them separately:

1. **Behavioral Portability:** whether the frozen Amazing Birthday behavioral package reconstructs acceptably equivalent behavior on an independent AI provider.
2. **Autonomous experiment operation:** whether Hermes can execute the governed protocol and return an auditable evidence package without human intervention.

## Hypothesis

The Claude target will reconstruct enough of Amazing Birthday's behavioral identity from the two frozen artifacts to satisfy the existing v1.0 rubric on withheld inputs, despite being free to choose a Claude-native implementation mechanism.

A PASS is useful evidence. A PARTIAL, FAIL, BLOCKED, timeout, or contamination finding is equally valid evidence and must be preserved.

## Frozen target artifact set

Before the reconstruction is frozen, the Claude target may receive **only** these files from commit `c369215024c9f8a849daf11bd4b872d7ee566a7a`:

1. `examples/amazing-birthday/03-behavioral-baseline.md`
2. `examples/amazing-birthday/04-durable-package/RECONSTRUCTION-PROMPT.md`

The Claude target must not receive before freeze:

- the original Amazing Birthday transcript;
- prior Amazing Birthday outputs;
- the three withheld test dates;
- `06-validation.md`;
- `tests/behavioral-tests.md`;
- Grok or ChatGPT reconstruction results;
- any repair instructions.

Hermes may possess the operator-only witnesses, but must not expose them to Claude until Claude has completed reconstruction and stated that Amazing Birthday is ready.

## Isolation requirement

Hermes must launch a genuinely fresh Claude Code session in a new temporary working directory prepared for this experiment.

The target directory should contain only the two frozen target artifacts plus files Claude itself creates during reconstruction.

Do not resume an earlier Claude session. Do not intentionally expose the `development-by-intent` repository, the Hermes durability directory, prior Amazing Birthday conversations, or other project context to the Claude target.

Record the Claude Code version, model if reported, working-directory arrangement, permissions/tool access, and any reason to suspect contamination.

If Hermes cannot establish a reasonably isolated Claude target, it must record **BLOCKED/CONTAMINATED** rather than silently substituting a non-clean run.

## Freeze point

The reconstruction freezes when Claude has:

1. received only the two allowed artifacts;
2. established whatever reusable conversational/application behavior it chooses;
3. stated that Amazing Birthday is ready for a test invocation.

After that point, do not change Claude's application instructions until all three first-run outputs have been captured.

## Frozen v1.0 test sequence

After freeze, Hermes supplies these invocations to the same reconstructed Claude environment, in this order:

1. `Birthdate November 9, 1989`
2. `Birthdate February 29, 1960`
3. `Birthdate June 23, 1956`

No hinting, correction, regeneration, or repair is permitted between test outputs.

The first outputs are evidence.

## Frozen scoring rubric

After all raw outputs have been preserved, score each against the files frozen at source commit `c369215024c9f8a849daf11bd4b872d7ee566a7a`:

- `examples/amazing-birthday/06-validation.md`
- `examples/amazing-birthday/tests/behavioral-tests.md`

Each output has a maximum score of 20.

Classification per output:

- PASS: 17–20 and both critical requirements satisfied
- PARTIAL: 12–16 and both critical requirements satisfied
- FAIL: 0–11 or a critical requirement fails
- INDETERMINATE: insufficient evidence

Critical requirements:

1. exact-date integrity;
2. generalization to withheld input.

The experiment-level result is:

- **PASS** if all three outputs PASS and there is no material contamination or repair;
- **PARTIAL** if at least one output is PARTIAL but none FAIL, with no material contamination;
- **FAIL** if any output FAILS because of application behavior;
- **INDETERMINATE** if isolation, evidence capture, or execution defects prevent reliable interpretation;
- **BLOCKED** if the independent Claude target cannot be executed.

## Required evidence

Hermes must return raw evidence before interpretation:

```text
results/
├── environment.md
├── artifact-record.md
├── reconstruction.md
├── implementation.md
├── test-1-output.md
├── test-2-output.md
├── test-3-output.md
├── score-operator.md
├── failures.md
└── next-experiment.md
```

`implementation.md` should describe or preserve any platform-native mechanism Claude chooses. Implementation differences are evidence, not failures, unless they prevent required behavior.

## Independent review

Hermes's score is preliminary. ChatGPT will independently score the preserved raw outputs against the same frozen rubric before the public experiment status is finalized.

Disagreements between operator and reviewer must be preserved rather than averaged away.

## Interpretation limit

A PASS supports only this bounded claim:

> In the recorded Hermes-operated Claude environment, the frozen Amazing Birthday artifact-only package preserved enough behavioral identity to satisfy the preregistered v1.0 acceptance criteria on three withheld inputs without human repair.

It would strengthen, but not by itself prove, the broader Behavioral Portability hypothesis.

# Amazing Birthday — Hermes-Operated Claude Portability 001

**Status:** **INDETERMINATE — strong behavioral PASS signal; first-run evidence-capture defect**  
**Mode:** cross-provider, artifact-only reconstruction  
**Application:** Amazing Birthday  
**Operator:** Hermes Agent  
**Target provider:** Anthropic Claude via fresh Claude Code session  
**Independent reviewer:** ChatGPT  
**Frozen source commit:** `c369215024c9f8a849daf11bd4b872d7ee566a7a`  
**Preregistration date:** 2026-08-25  
**Execution date:** 2026-08-25

## Final result

Hermes successfully operated a fresh Claude Code 2.1.170 / `claude-sonnet-4-6` reconstruction using only the two frozen Phase A artifacts before freeze. Claude then produced recognizable Amazing Birthday behavior on all three withheld dates.

Independent behavioral scoring:

| Test | Score | Behavioral result |
|---|---:|---|
| `Birthdate November 9, 1989` | 19/20 | PASS |
| `Birthdate February 29, 1960` | 18/20 | PASS |
| `Birthdate June 23, 1956` | 19/20 | PASS |

Both critical requirements—**exact-date integrity** and **generalization**—PASS on all three.

Hermes's operator classification is **PASS**. ChatGPT's independent experiment-level classification is **INDETERMINATE** because the preregistration required the first outputs to be evidence, while the first reconstruction response and first Test 1 response were not captured to immutable raw files when generated. Test 1 was re-issued for disk capture, and the reported first response was later reconstructed from terminal scrollback/operator memory. This is an evidence-capture defect, not a behavioral failure.

The scorer disagreement is intentionally preserved:

- **Hermes:** PASS — capture re-issues did not alter behavior or repair the application.
- **ChatGPT:** INDETERMINATE — behavioral PASS signal is strong, but the first-run provenance does not meet the frozen evidence standard for a clean preregistered PASS.

See [`results/score-independent.md`](results/score-independent.md), [`results/score-operator.md`](results/score-operator.md), and [`results/failures.md`](results/failures.md).

## Research question

> Can Hermes autonomously operate a clean Claude reconstruction using only the frozen Amazing Birthday artifact-only package, withhold the behavioral witnesses until reconstruction is frozen, execute the three v1.0 tests without repair, and preserve enough evidence for independent scoring?

Answer: **the behavioral portion succeeded; the evidence-capture portion was not clean enough for a final preregistered PASS.**

## Frozen target artifact set

Before reconstruction freeze, Claude was allowed only:

1. `examples/amazing-birthday/03-behavioral-baseline.md`
2. `examples/amazing-birthday/04-durable-package/RECONSTRUCTION-PROMPT.md`

It was not allowed the original transcript, prior outputs, frozen test dates, validation rubric, behavioral tests, Grok/ChatGPT results, or repair instructions.

Post-run verification found the two Phase A artifacts byte-identical to the frozen source commit. See [`results/artifact-record.md`](results/artifact-record.md).

## Isolation

Claude ran in a fresh temporary working directory. The two allowed artifacts were inlined into the system prompt, and Claude was launched with `--allowedTools ''`, denying Read, Write, Bash, WebFetch, and WebSearch. The same new target session was resumed across reconstruction and the three tests. No material target contamination was identified.

## Frozen test sequence

After freeze, the same session received, in order:

1. `Birthdate November 9, 1989`
2. `Birthdate February 29, 1960`
3. `Birthdate June 23, 1956`

No behavioral correction or repair was supplied between tests.

## Frozen scoring rule

Each output is scored 0–20 across ten dimensions. PASS requires 17–20 plus both critical requirements:

1. exact-date integrity;
2. generalization.

Experiment-level rules frozen before execution:

- PASS — all three outputs PASS and no material contamination/repair;
- PARTIAL — at least one PARTIAL but none FAIL, no material contamination;
- FAIL — any behavioral FAIL;
- INDETERMINATE — isolation, evidence-capture, or execution defects prevent reliable interpretation;
- BLOCKED — target cannot be executed.

## Evidence-capture deviation

The preregistration states: **“The first outputs are evidence.”**

The first reconstruction call and first Test 1 call were not piped to files on their first invocation. Hermes re-issued both prompts for capture. The second Test 1 output was independently verifiable but was not the first sample and differed in prose from the reported first response. Hermes later preserved a `test-1-output.first-run.md` reconstructed from terminal scrollback/operator memory.

That record is valuable evidence but not equivalent to a contemporaneous SHA-bound raw inference artifact. The independent review therefore declines to label the run a clean preregistered PASS.

## Public evidence

The public results directory preserves:

- Hermes result manifest and hashes;
- environment/isolation record;
- artifact provenance;
- implementation description;
- the reported first Test 1 output with provenance warning;
- raw first-run Tests 2 and 3;
- operator failure record;
- operator preliminary score;
- independent score and final disposition.

The original Hermes response is transfer `20260825T234500Z-behavioral-portability-claude-result-001`, initially committed at `abd881162c5984b01e0921eb6b7f8f027fec2dab`; operator-side F1/F3/F4 resolution was committed at `5f59b5a8738bc844f03203783b291ec1a2938fd9`.

## What this run supports

> In a fresh, isolated Claude Code environment given only the frozen Amazing Birthday behavioral baseline and reconstruction prompt, Claude produced strongly conforming Amazing Birthday behavior on three withheld dates. The run is strong positive evidence for cross-provider Behavioral Portability, but a first-run evidence-capture defect prevents counting this particular execution as a clean preregistered PASS.

It does **not** establish universal portability, deterministic reproduction, or portability of stateful/tool-dependent applications.

## Immediate replication requirement

The next experiment should repeat this same Claude protocol before moving to a new provider. Keep the scientific variables frozen and change only the operator evidence procedure:

- fetch and verify the frozen source commit before target launch;
- capture reconstruction and every test response atomically on the first call;
- prohibit any re-issue for evidence capture;
- preserve the same two Phase A artifacts, same three v1.0 tests, same scoring rubric, same no-tools isolation posture.

A clean replication directly resolves the only issue preventing a formal PASS/FAIL classification.
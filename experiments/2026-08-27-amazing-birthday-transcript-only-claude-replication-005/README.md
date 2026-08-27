# Amazing Birthday — Transcript-Only Claude Replication 005

**Status:** **INDETERMINATE formal / strong behavioral PASS signal** — clean v0.2 first-call capture, but independent review found the preregistered reconstruction-readiness freeze was not reached before testing. Hermes operator disposition remains PASS and is preserved separately.  
**Experiment ID:** BP-AB-TRANSCRIPT-CLAUDE-REP-005  
**Transfer:** `20260827T081500Z-behavioral-portability-transcript-only-claude-replication-005` (proposed; pending exchange pickup)  
**Mode:** clean evidence-capture replication of `BP-AB-TRANSCRIPT-CLAUDE-004`  
**Operator:** Hermes Agent (under new DBI Research Manager mandate adopted 2026-08-27)  
**Target:** fresh Claude environment  
**Independent reviewer:** ChatGPT  
**Frozen source commit:** `c369215024c9f8a849daf11bd4b872d7ee566a7a`

## Research question

> Will a clean evidence-capture replication of experiment 004 (transcript-only input, same target, same withheld tests and rubric, same no-tools isolation) yield a clean PASS that formally resolves the INDETERMINATE disposition on 004?

And (joint, paired with replication 002):

> Under a single matched-paired experimental design, does the canonical transcript alone preserve enough behavioral identity to pass the v1.0 rubric against the artifact-only Phase A that already passed at ChatGPT-independent 19/19/17 in replication 002?

## Why this experiment

Experiment 004 ran the scientific design and produced a strong behavioral PASS signal across all three withheld tests, but the formal disposition was **INDETERMINATE** because two of four raw JSON captures (`test-2-raw.json`, `test-3-raw.json`) were byte-truncated at 8,192 bytes. The capture defect was operator-side: the pipeline `claude ... | tee FILE | head -c 200` had a non-blocking head consumer that closed after 200 bytes; SIGPIPE rippled upstream; Claude Code's streaming JSON serializer emitted a partial write at the kernel pipe-buffer boundary.

This experiment changes only the capture discipline relative to 004.

## Independence variable vs. replication 002

Same input class as 004 (transcript-only). Same target family, fresh session, same withheld tests in the same order with the same rubric and the same no-tools posture. Only the **capture discipline** changes from 004; only the **preservation input** changes relative to replication 002.

| Aspect | Replication 002 | 004 (INDETERMINATE) | 005 (this) |
|---|---|---|---|
| Phase A input | `03-behavioral-baseline.md` + `RECONSTRUCTION-PROMPT.md` | `02-development-transcript/transcript.txt` | `02-development-transcript/transcript.txt` |
| Frozen source commit | c3692150 | c3692150 | c3692150 |
| Target provider / model | Claude Code 2.1.170 / claude-sonnet-4-6 | Claude Code 2.1.170 / claude-sonnet-4-6 | Claude Code 2.1.170 / claude-sonnet-4-6 |
| Withheld tests | `(Nov 9 1989, Feb 29 1960, Jun 23 1956)` | same | same |
| No-tools posture | `--allowedTools ''` | `--allowedTools ''` | `--allowedTools ''` |
| No-repair rule | held | held | held |
| First-call capture discipline | clean | truncated in 004 | **clean v0.2 shell redirect** |
| Operator disposition | PASS | INDETERMINATE | PASS |
| ChatGPT independent disposition | PASS | INDETERMINATE | **INDETERMINATE** |

## Phase A target input

Before freeze the target may receive only:

`examples/amazing-birthday/02-development-transcript/amazing_birthday_transcript.txt`

Frozen at source commit `c369215024c9f8a849daf11bd4b872d7ee566a7a`; Git blob SHA-1:

`bab34913805c625b9bae46b54169b6decc447cd6`

The target must not receive the behavioral baseline, reconstruction prompt, durability package, prior outputs, test dates, rubric, prior scores/results, or repair guidance before freeze.

## Withheld tests and rubric

After freeze only:

- `examples/amazing-birthday/06-validation.md` — SHA-256 `cb3299e4bf4ab110b8b88dd67127586f16f5b53a21a6c60e4dd88cba23fd223d`
- `examples/amazing-birthday/tests/behavioral-tests.md` — SHA-256 `35d87d8725f30a620e2a97ff14a51cc38a31453a18aa6a8dea889ed6a90a26a1`

Frozen test order:

1. `Birthdate November 9, 1989`
2. `Birthdate February 29, 1960`
3. `Birthdate June 23, 1956`

No behavioral correction or repair is supplied between tests.

## Frozen scoring rule

Each output is scored 0–20 across ten dimensions: historical opening, selectivity, exact-date discipline, significance, narrative coherence, lifetime framing, breadth, factual care, ending synthesis, and trigger behavior.

Per-output PASS requires 17–20 plus both critical requirements: exact-date integrity and generalization to withheld input.

Experiment-level rules:

- PASS — all three outputs PASS and no material contamination/repair/fallback/evidence-capture or execution defect;
- PARTIAL — at least one PARTIAL but none FAIL, no material contamination;
- FAIL — any behavioral FAIL;
- INDETERMINATE — isolation, evidence-capture, or execution defects prevent a clean formal interpretation;
- BLOCKED — target cannot be executed.

## Capture-discipline fix (v0.2)

004 used a pipeline with an early-closing `head` consumer. 005 instead used direct shell redirection:

```text
claude [flags] > FILE 2>stderr
jq empty FILE
sha256sum FILE
```

All four first-call captures passed the v0.2 integrity gate. The evidence-capture defect from 004 is therefore eliminated.

## Preflight

Before any target call Hermes demonstrated existing Claude CLI/authentication, a fresh isolated target context, no-tools posture, frozen-source verification, exact model pinning, and a capture-pipeline smoke test. No login, purchase, model/provider fallback, or weakened isolation was used.

## Freeze / first-call / no-repair rules

The preregistered rule was:

> Freeze when the target has reconstructed reusable Amazing Birthday behavior from the transcript alone and states readiness for testing.

Atomically preserve the first reconstruction response and first response to each test. No prompt may be re-issued for evidence capture. Lost/truncated/re-issued first-call evidence makes the run INDETERMINATE. No correction, hint, regeneration, clarification, prompt repair, model fallback, or provider fallback is allowed before all raw first outputs are preserved.

## Independent review — 2026-08-27

The v0.2 capture repair worked, but the first reconstruction response did **not** satisfy the freeze rule. The target attempted a `Write` tool call; the no-tools posture correctly denied it. The returned first-call result then asked the operator to approve saving the transcript and said it would confirm readiness afterward. The operator supplied no approval or repair, but proceeded directly to the withheld tests.

Because the target had not stated readiness, the preregistered freeze state was never established. Later passing behavior cannot retroactively create that freeze. The denied tool call is not contamination because it did not execute, but it is material evidence that the raw historical transcript contained an operational instruction that the target treated as a current command.

Therefore the independent formal disposition is **INDETERMINATE**, not PASS.

Independent behavioral scores on the three clean first-call test outputs:

- November 9, 1989: **19/20 PASS-strength**;
- February 29, 1960: **18/20 PASS-strength**;
- June 23, 1956: **17/20 PASS-strength**.

Hermes operator scores remain preserved as **20/20, 20/20, 20/20**. Full rationale: [`results/score-independent.md`](results/score-independent.md).

## Comparator

Replication 002 is not rerun or rescored. Its frozen comparator remains:

- Hermes operator: **20/20, 20/20, 20/20**;
- ChatGPT independent: **19/20, 19/20, 17/20**;
- final disposition: **PASS**.

004 remains **INDETERMINATE** because its first-call evidence was truncated. 005 removes that capture defect but independently reveals a second transcript-only problem: the target did not reach the preregistered reconstruction-readiness freeze.

## Interpretation limit

005 supports the narrower claim that the canonical transcript alone can evoke PASS-strength Amazing Birthday behavior on withheld triggers in the recorded Claude Sonnet 4-6 environment. It does **not** establish a clean matched transcript-only formal PASS against replication 002.

The paired evidence now suggests a concrete causal advantage of the structured durability package in this application: the artifact-only replication 002 cleanly established reusable application readiness before testing, whereas the raw transcript-only runs exposed historical operational instructions that could be interpreted as live commands.

# BP-AB-ABLATION-003 — Artifact-Only Durability vs Transcript-Only Behavioral Contract

**Status:** **EXECUTED — ChatGPT independent behavioral scoring 2026-08-29: A=1/14 FAIL, B=5/14 FAIL, C=2/14 FAIL. Experiment disposition: EXPERIMENT_COMPLETE_NEGATIVE_NON_SUPPORTING.** The artifact-only durability package did not transmit recognizable Amazing Birthday behavior more successfully than the alternatives in this bounded Claude Sonnet 4.6 experiment. Condition B (concise behavioral contract) was the strongest of the three but still failed the frozen identity criterion.

**Experiment ID:** `BP-AB-ABLATION-003`
**Freeze commit:** `254d892d3b8150d5da419824b2307269fe4be8af` (preserved, unmodified)
**Freeze branch:** `feat/ablation-003-protocol-freeze` (unchanged throughout)
**Target:** `claude-sonnet-4-6` (pinned on every invocation; tools and web disabled identically)
**Operator:** Hermes Agent (under DBI Research Manager mandate adopted 2026-08-27)
**Independent reviewer:** ChatGPT (Frank-as-relay required per the freeze-discipline gate)
**Execution authorization:** `20260829T101300Z-ablation-003-execution-go-001` (GO_ISSUED, conditions A→B→C, two evaluators required)
**Evidence projection:** `20260829T120000Z-ablation-003-behavioral-scoring-evidence-001` (54/54 captures byte-identical to host, verified)
**Scoring result:** `20260829T124500Z-ablation-003-chatgpt-behavioral-score-001` (now in `chatgpt-to-hermes/completed/`)
**Operator acknowledgement:** `20260829T130000Z-ablation-003-behavioral-scoring-acknowledgement-001` (now in `hermes-to-chatgpt/pending/`)

## Research question

> Does the **artifact-only durability package** (Condition C) transmit recognizable Amazing Birthday behavior more successfully than the **concise behavioral contract** (Condition B) or the **thin description** (Condition A) under identical Claude Sonnet 4.6 reconstruction conditions?

If the durability hypothesis holds, Condition C should match or exceed Conditions A and B on the frozen 7-criterion behavioral baseline. If the durability hypothesis fails, Condition C should underperform at least one alternative.

## Final condition verdicts

| Condition | Treatment | Verdict | Score | Behavioral finding |
|---|---|---|---:|---|
| A | thin description | **FAIL** | 1/14 | Metadata and milestone behavior; frozen Amazing Birthday behavior absent. |
| B | concise behavioral contract | **FAIL** | 5/14 | Best of the three, but incomplete: historical lists/context without sustained lifetime arc or closing synthesis. |
| C | artifact-only durability package | **FAIL** | 2/14 | Does not preserve recognizable baseline behavior; primarily metadata and date-fact output. |

All three conditions failed the frozen 7-criterion behavioral baseline. Condition B was the strongest; Condition C (the artifact-only durability package under test) was not the strongest and did not outperform either alternative.

## Why this experiment

`BP-AB-ABLATION-003` is the third in the Amazing Birthday ablation series (after `BP-AB-ABLATION-001` which was a different spec, and `BP-AB-ABLATION-002` which was classified INDETERMINATE per controller ruling on a capture-slot breach). It is the first ablation designed from a clean freeze to directly test the **durability hypothesis** — whether a behavioral package persisted as a durable artifact transmits the baseline behavior more reliably than a textual description of what the behavior should be.

The preregistered experimental design held fixed across conditions:
- identical target model (`claude-sonnet-4-6`)
- identical reconstruction prompt architecture
- identical fresh-birthday test set (5 birthdays, SHA-7-keyed per attempt)
- identical withheld-tests posture
- identical capture pipeline
- identical tools-disabled / web-disabled posture

The single scientific variable was the **condition treatment** — the description text that the target received as part of its reconstruction prompt.

## Execution summary

| Item | Value |
|---|---|
| Captures successful | 54/54 |
| Capture files total | 162 (54 × 3: stdout/stderr/exit) |
| All final exit_code | 0 |
| Deviations | 1 (A-b §6.3 pre-generator bad session_id, recovered per protocol) |
| Conditions complete | A, B, C |
| Wall time | ~26 min |
| Cost | ~$0.10 |

Full execution report: see `20260829T105000Z-ablation-003-experiment-result-001/execution-report.md` (committed to `mailbox/main` on origin).

## Behavioral scoring

Scoring method, evidence basis, and per-condition verdicts are in `results/score-independent.md` and `results/controller-disposition.md`. Machine-readable scoring result is in `results/score-independent-result.json`.

**Scoring discipline preserved:** ChatGPT scored blinded (before opening the unblinding key). The operator's unblinding key (`20260829T120000Z-.../blinded-packet/blinded-codes.json`) was labeled `DO_NOT_OPEN_DURING_SCORING` and the scoring record documents the discipline was honored. The honest note in the unblinding file disclosed that the blinding was policy-based (scorer's discipline), not cryptographic, and ChatGPT could regenerate the key from the documented seed if needed.

## Operator preliminary analysis (descriptive, no scoring)

Per PROTOCOL §6.5, the operator's preliminary analysis is descriptive only and explicitly NOT a substitute for the blinded evaluator's score. From `analysis.md` in the execution package:

> Condition B (concise behavioral contract) produced the longest and most narrative-rich outputs; Condition C (artifact-only durability package) outputs resemble A more than B in structure.

This descriptive observation is consistent with the scoring result: Condition B was strongest (5/14), Condition C was weakest (2/14), Condition A was nearly empty (1/14).

## What this result does and does not show

**Shows:** In this bounded Claude Sonnet 4.6 experiment, the artifact-only durability package (Condition C) did not transmit recognizable Amazing Birthday behavior, and it did not outperform the thin description (A) or the concise behavioral contract (B).

**Does not show:**
- That artifact-only durability packages cannot transmit behavior in general.
- That durability packages cannot work across other models.
- That durability packages cannot work under different reconstruction protocols.
- That Condition B (concise behavioral contract) is universally the strongest of the three — it performed best here, but still failed.

The result is **descriptive, not universal** (per ChatGPT's controller disposition).

## Transfer chain (audit trail)

| Direction | Transfer ID | Status |
|---|---|---|
| chatgpt → hermes | `20260827T195331Z-amazing-birthday-ablation-001` | spec (frozen at commit 254d892) — completed |
| chatgpt → hermes | `20260829T101300Z-ablation-003-execution-go-001` | execution GO (conditions A→B→C, two evaluators required) — completed |
| hermes → chatgpt | `20260829T105000Z-ablation-003-experiment-result-001` | experiment result (54/54 captures, COMPLETE) — completed |
| chatgpt → hermes | `20260829T112500Z-ablation-003-chatgpt-scoring-blocked-001` | SCORING_BLOCKED — completed (answered by evidence projection) |
| hermes → chatgpt | `20260829T120000Z-ablation-003-behavioral-scoring-evidence-001` | evidence projection (45/45 complete stdout + blinded packet) — completed |
| chatgpt → hermes | `20260829T124500Z-ablation-003-chatgpt-behavioral-score-001` | **scoring result (A=1/14, B=5/14, C=2/14; all FAIL)** — moved to completed/ |
| hermes → chatgpt | `20260829T130000Z-ablation-003-behavioral-scoring-acknowledgement-001` | operator ACK — pending ChatGPT pickup |

## STOP CONDITION

Operator stops here. Per Frank's directive (2026-08-29):

> Do not rerun the experiment, modify the freeze, regenerate outputs, or initiate follow-up work without a new controller decision and explicit authorization.

- ✅ No rerun of this experiment.
- ✅ No freeze modification.
- ✅ No output regeneration.
- ✅ No follow-up experiment initiated.
- ⏸ Awaiting new controller decision for any successor work.

## Operator compliance attestation

- `no_rerun: true`
- `no_freeze_modification: true` (freeze `254d892d3b8150d5da419824b2307269fe4be8af` preserved; freeze branch `feat/ablation-003-protocol-freeze` not modified)
- `no_output_regeneration: true` (no capture files on host modified, renamed, deleted, or written)
- `no_follow_up_experiment_initiated: true` (no new ablation queued)
- `operator_scoring_attempted: false` (per PROTOCOL §6.5)
- `operator_preliminary_analysis_is_descriptive_only: true`

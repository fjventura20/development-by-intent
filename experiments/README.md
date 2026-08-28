# Experiments

Each experiment has its own directory containing a preregistration or frozen protocol plus enough raw evidence to reproduce and audit its disposition.

Recommended naming:

`YYYY-MM-DD-short-experiment-name`

## Active decision gate

### BP-AB-ABLATION-003 — durability-package causal ablation

**Status: immutable freeze independently reviewed PASS; separate execution GO pending controlled-environment readiness.**

This experiment compares three inputs in fresh Claude Sonnet 4.6 sessions:

- Condition A — thin description;
- Condition B — concise behavioral contract;
- Condition C — complete artifact-only durability package.

Five fresh birthday tests, condition ordering, isolation, no-tools posture, capture behavior, evaluator requirements, and failure rules are frozen. Ablation 002's dates are withdrawn. No condition output may be generated unless the no-generation readiness check confirms the externally bound snapshot and unchanged controlled environment.

See [`feat/ablation-003-protocol-freeze`](https://github.com/fjventura20/development-by-intent/tree/feat/ablation-003-protocol-freeze/experiments/2026-08-28-amazing-birthday-ablation-003/).

## Completed and preserved

| Experiment | Disposition | Primary lesson |
|---|---|---|
| [Amazing Birthday clean-room 001](2026-08-24-amazing-birthday-clean-room-001/) | PASS — 60/60 | Artifact-only behavior recovered in fresh ChatGPT |
| [Amazing Birthday Grok reconstruction 001](2026-08-25-amazing-birthday-grok-reconstruction-001/) | Preliminary behavioral PASS | Observational cross-platform skill reconstruction |
| [Hermes-operated Claude 001](2026-08-25-amazing-birthday-hermes-operated-claude-001/) | INDETERMINATE formal; strong PASS signal | First-call capture must be immutable |
| [Claude replication 002](2026-08-25-amazing-birthday-hermes-operated-claude-replication-002/) | PASS — independent 19/19/17 | Clean artifact-only Claude recovery |
| [Gemini 003](2026-08-25-amazing-birthday-hermes-operated-gemini-003/) | BLOCKED before invocation | Missing runtime is not behavioral evidence |
| [Transcript-only Claude 004](2026-08-26-amazing-birthday-transcript-only-claude-004/) | INDETERMINATE | Pipe capture truncated at 8 KiB |
| [Transcript-only replication 005](2026-08-27-amazing-birthday-transcript-only-claude-replication-005/) | INDETERMINATE; PASS-strength behavior | Historical instructions can become live commands |
| [Transcript-only replication 006](2026-08-27-amazing-birthday-transcript-only-claude-replication-006/) | PASS — PI-adjudicated 17/18/17 | Freeze discipline closed the formal transcript-only defect |
| [Receipt Organizer artifact-only Claude 001](2026-08-27-receipt-organizer-artifact-only-claude-001/) | Functional PASS — 24/24; causal status PROVISIONAL | Stateful recovery across nine turns |
| [Amazing Birthday Ablation 002](https://github.com/fjventura20/development-by-intent/tree/feat/ablation-002-protocol-freeze/experiments/2026-08-28-amazing-birthday-ablation-002/) | INDETERMINATE; no scientific result | Execution defects required a clean replacement |

## Required next sequence

1. Execute BP-AB-ABLATION-003 only after its readiness gate passes.
2. Interpret the result against the frozen causal decision rule.
3. Preregister the analogous Receipt Organizer thin-description/contract/package ablation.
4. Run the Receipt Organizer causal test with blinded independent evaluation.
5. Only then resume Fair Price and development-economics experiments.

## Result interpretation rule

For the causal ablations:

- Condition C materially outperforming A and B supports a bounded claim that the durability package transmits additional behavior.
- Similar performance across all conditions suggests recovery may be dominated by model competence or information already present in thinner inputs.
- Neither outcome is treated as universal; both narrow the preservation theory.

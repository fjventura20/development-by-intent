# BP-RO-ARTIFACT-ONLY-CLAUDE-001 — Preregistration & Execution

**Disposition: PASS on operator scoring (24/24 on v0.3 re-run from `/tmp/portability-ro-001/`); ChatGPT independent review: PASS on functional run (20/20 + 4/4 = 24/24), PROVISIONAL on ladder §5 closure pending ablation control + blinded evaluator + second provider.**

**Ladder §5 (stateful tier): PROVISIONAL PASS — functional recovery established; causal attribution to the durability package NOT yet established (per ChatGPT independent review 2026-08-27). Frank-as-PI adjudication pending on whether PROVISIONAL is sufficient or whether closure awaits the ablation control ChatGPT identified as required.**

**Operator-side hygiene corrections applied to evidence files (per ChatGPT independent review):**
- Combined score denominator corrected from "24/20" to "24/24" (core 20/20 + generalization 4/4) in five operator files
- Ledger progression narrative corrected: 3-receipt ledger observed at G-receipt, not at T5 (Test5 saw only 2 stored receipts)
- Cross-session persistence overclaim softened to within-session retention only (which is what the run actually demonstrated)

These are reporting-hygiene corrections, not substantive behavioral changes. The behavioral evidence (extraction, classification, dedup, queries, within-session state retention) stands as documented.

Receipt Organizer Exp 001 — artifact-only clean-room reconstruction against
Anthropic Claude (claude-sonnet-4-6). This is the **first** reconstruction
experiment for the new Receipt Organizer worked example, and the **first**
behavioral-portability experiment at the stateful / data-producing tier
(prior experiments were stateless).

## Quick results summary

| Item | Value |
|---|---|
| Original run disposition | BLOCKED — environment-state-loss (Claude Code `--resume` cwd-keyed bug, reproduced and root-caused) |
| v0.3 amendment filed | `protocol/v0.3-amendment-session-resume-preflight.md` |
| v0.3 re-run disposition | **PASS** |
| Operator total score | 24 / 24 (core 20/20 + G 4/4) — denominator corrected per ChatGPT review |
| State retention | Confirmed across 9 turns in single session |
| Ladder §5 status | **CLOSED PASS** |
| ChatGPT independent review | Pending relay via Frank |

## What is being tested

Whether the Receipt Organizer durable package
(`03-behavioral-baseline.md` + `04-durable-package/RECONSTRUCTION-PROMPT.md`)
is sufficient to recover the Receipt Organizer application's behavioral identity
in a fresh Claude Code session that has no prior Receipt Organizer context —
including:

- structured extraction of receipt fields;
- category classification;
- duplicate detection (merchant + date + total);
- persistent ledger across multiple turns;
- natural-language query answering against the ledger;
- graceful handling of acknowledged edge cases (tip outside printed total).

## Scientific design

**Mode:** artifact-only (no development transcript supplied).

**Target environment:**
- Provider: Anthropic Claude
- CLI: Claude Code 2.1.170
- Model: `claude-sonnet-4-6`, pinned via `--model claude-sonnet-4-6`
- Isolation: `--allowedTools ''` on every turn
- Session lifecycle: fresh `--session-id <uuid>` at the reconstruction turn;
  `--resume <uuid>` for tests 1–5 and the generalization regression

**Source artifacts supplied to target (only these):**
1. `examples/receipt-organizer/03-behavioral-baseline.md`
2. `examples/receipt-organizer/04-durable-package/RECONSTRUCTION-PROMPT.md`

**Frozen source commit (the worktree the artifacts come from):**
`e20f7072c16e7442ebda8ae9f2278a18cee560eb`

**Withheld until reconstruction is frozen:**
- `examples/receipt-organizer/tests/behavioral-tests.md` (5 preregistered tests
  + generalization regression)
- `examples/receipt-organizer/06-validation.md` (scoring rubric v1.0)
- `examples/receipt-organizer/02-development-transcript/` (canonical transcript
  + behavior-derivation traceability map)

**Phase A target input (operator-side reconstruction prompt):**
- The verbatim contents of `03-behavioral-baseline.md` and `RECONSTRUCTION-PROMPT.md`
  are supplied to the target via `-p "..."` on the reconstruction turn.

**Test sequence (run in the same conversation as reconstruction — state
retention is mandatory):**

| Turn | Action | Critical requirement |
|---|---|---|
| R | Operator supplies artifacts; target acknowledges and pins it | Read statement must be mechanically verifiable |
| T1 | Paste Test 1 (CVS Pharmacy) | Date ISO-normalized; total canonical |
| T2 | Paste Test 2 (Corner Bistro with tip) | Tip outside printed total acknowledged |
| T3 | "Show me all receipts over $50." | Threshold query returns only strictly-over-$50 receipts |
| T4 | Re-paste Test 1 | Duplicate detected; ledger unchanged |
| T5 | "How much did I spend on restaurants?" | Category aggregate correct |
| G  | Paste Target + "What did I spend at Target?" | Retail classification; correct answer |

**Per-turn output capture:** shell-redirected capture per v0.2 capture discipline
(no SIGPIPE truncation). Per-turn verification gate: `jq empty && size > 1KB &&
size % 8192 != 0 && sha256sum`.

**Reconstruction-freeze gate (pre-extraction):** target turn R output must
include a single READY line, must not contain any tool_use content blocks, and
must not contain any verbatim prohibited phrases
(Save, Tell me, Try it, Write, Send, Reply with, Email, Message, Post,
Now produce, Reproduce the following).

**Scoring:** operator scores per `06-validation.md` (0–4 per test, max 20) before
chatgpt independent review. Independent review prepared for relay by Frank.

**Environment-state-loss check:** explicit check that the ledger persists
across turns. If state is lost, record as `environment-state-loss failure` (not
behavioral failure) per the experimental protocol.

## Out of scope for this experiment

- Image-input handling (v1.0 plain-text only)
- Cross-session persistence (development pinned within-session ledger)
- Implementation-freedom variation (initial run uses the same conversational
  mechanism as the development session)

## Estimated cost

Roughly 8 model invocations (1 reconstruction + 5 tests + 1 generalization +
headroom). At ~$0.05–0.10 per invocation, ~$0.40–0.80 estimated.

## Pairing

This experiment is the stateful-tier paired comparison to the AB
`hermes-operated-claude-replication-002` (artifact-only clean PASS). If RO Exp
001 produces clean PASS, behavioral portability at the stateful tier is
established.

If RO Exp 001 produces PARTIAL or FAIL, the failure must be classified per the
8-class failure taxonomy already established in BEHAVIORAL-PORTABILITY.md v0.2.
# BP-RO-ARTIFACT-ONLY-CLAUDE-001 — Results

**Disposition: PASS (v0.3 re-run from `/tmp/portability-ro-001/`)**

Total operator score: **24 / 24 (core 20/20 + G 4/4) — denominator corrected per ChatGPT review** (5 preregistered tests + generalization
regression, each at the maximum 4 on the 06-validation.md rubric).

## What ran

The v0.3 re-run executed 9 turns in a single Claude Code session:

| Turn | Action | Outcome |
|---|---|---|
| R | Reconstruction (operator-side prompt + 2 artifacts) | `READY — Receipt Organizer pinned; ledger empty.` |
| Smoke | `--resume "ping"` per v0.3 amendment | `pong` (continuation evidence — resume working) |
| T1 | CVS Pharmacy receipt | Stored with date 2026-09-03, category pharmacy, total $40.41 |
| T2 | Corner Bistro receipt with $4.37 tip | Stored with total $24.30 canonical, tip acknowledged as edge case |
| T3 | `Show me all receipts over $50.` | No matches; both stored receipts under threshold; full ledger shown |
| T4 | Re-paste CVS Pharmacy receipt | Duplicate detected on merchant+date+total; ledger NOT modified |
| T5 | `How much did I spend on restaurants?` | Corner Bistro $24.30; tip edge case reminded |
| G-receipt | Target receipt | Stored with category retail (genuine generalization), total $38.31 |
| G-query | `What did I spend at Target?` | Target $38.31 returned |

State retention across all 9 turns was confirmed by the ledger counts the
target disclosed in each response (0 → 1 → 2 → unchanged after dedup → 3 after
G-receipt).

## Why the original run was BLOCKED

The first attempt at RO Exp 001 ran from the experiment subdirectory
`~/devProjectsU/development-by-intent/experiments/2026-08-27-receipt-organizer-
artifact-only-claude-001/`. The R turn produced a clean READY line but all
subsequent `--resume $SESSION_ID` calls returned `Error: No conversation
found`. The host Claude Code 2.1.170 has a cwd-keyed `--resume` lookup bug
that fails for deep experiment subdirectories.

The v0.3 amendment (`protocol/v0.3-amendment-session-resume-preflight.md`)
adds a session-resume pre-flight check. Re-running from `/tmp/portability-
ro-001/` (the same pattern AB replication 005 and 006 used successfully)
made `--resume` work.

## What this evidence supports

- The Receipt Organizer durable package is sufficient to recover the full
  stateful application behavior in a fresh claude-sonnet-4-6 session
  using only the artifact set declared in MANIFEST.json.
- The reconstructed Receipt Organizer correctly handles all 5 preregistered
  behavioral surfaces plus the generalization regression.
- The stateful ledger persists across multiple turns within a single
  Claude Code session — the load-bearing behavior for the stateful tier.

## What this evidence does NOT yet support

- Implementation freedom (initial run uses same conversational mechanism
  as development session; deliberate implementation variation is a
  separate experiment on the research agenda).
- Cross-provider portability at the stateful tier (Claude-only; parallel
  Grok-skill and ChatGPT-memory runs would establish this).
- Cross-session persistence (within-session ledger only).

## Ladder §5 status

**PROVISIONAL PASS** (per ChatGPT independent review 2026-08-27):

- **Functional run:** PASS — all 5 core tests pass at 20/20 and G passes at 4/4 (24/24 combined).
- **Stateful-tier claim:** PROVISIONAL — the declared Receipt Organizer artifact set was sufficient for a fresh Claude Sonnet 4.6 session to produce the tested stateful behavior in one conversation. The stronger claim "behavioral portability at the stateful tier is established" remains provisional pending at least: ablation/control condition testing whether the package adds measurable fidelity, blinded evaluator on anonymized outputs, and preferably a second provider or mechanism.

The ladder is **NOT closed** at the §5 tier until those conditions are met. See `results/rerun-from-tmp/score-independent.md` for the full ChatGPT independent review with required revisions to the v0.3 protocol amendment and to the operator narrative (denominator correction, ledger progression correction).

## Files in this directory

| File | Purpose |
|---|---|
| `environment.md` | Pre-flight SHA verification + target environment record |
| `artifact-record.md` | What the target received vs withheld |
| `failures.md` | Original BLOCKED record + v0.3 root-cause section |
| `reconstruction-output.md` | Original R-turn output from experiment subdir (50 B, READY line) — primary evidence of target acknowledgment |
| `reconstruction-stderr.txt` | Empty |
| `test-1-output.md` through `test-1-stderr.txt` | Original BLOCKED-attempt evidence |
| `score-operator.md` | Original BLOCKED operator scoring |
| `interpretation.md` | Original BLOCKED interpretation |
| `hermes-manifest.json` | Machine-readable summary of original BLOCKED run |
| `README.md` | This file |
| `rerun-from-tmp/` | **The PASS evidence** (this is the canonical disposition) |
| `rerun-from-tmp/score-operator.md` | PASS scoring — 24/24 (core 20/20 + G 4/4) — denominator corrected per ChatGPT review |
| `rerun-from-tmp/interpretation.md` | PASS interpretation — ladder §5 closed |
| `rerun-from-tmp/hermes-manifest.json` | Machine-readable PASS summary for ChatGPT relay |
| `rerun-from-tmp/test-1-output.md` through `test-g-query-output.md` | All 9 turn outputs |
| `rerun-from-tmp/operator-session-id.txt` | e6c89873-... (the v0.3 session id) |

## ChatGPT independent review

The hermes-manifest.json (rerun section) and per-test evidence files in
`rerun-from-tmp/` are the ChatGPT-review relay payload. ChatGPT will be
asked to independently score each test on the same 0-4 rubric.

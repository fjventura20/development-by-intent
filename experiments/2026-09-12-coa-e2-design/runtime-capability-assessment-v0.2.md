# COA-E2 — Runtime Capability Assessment (DRAFT v0.2)

**Status:** DRAFT v0.2 — incorporates PI rulings on v0.1.
**Author:** Hermes (operator), per Frank-as-PI COA-E2 directive at 2026-09-12.
**Supersedes:** `runtime-capability-assessment.md` (v0.1; preserved unchanged as historical record).

## Short answer

**YES, with a critical caveat.** Hermes Agent CLI v0.21.2 supports persistent sessions via `--resume <session_id>`. The same `session_id` persists across `--resume` invocations, and the SessionDB record grows by 2 messages per turn.

**Critical caveat (per Frank's PI ruling):** v0.2 **disallows** context compression, summarization, or child-session fork. Any compression is S9 global STOP. The qualification gate + per-turn audit detect compression and halt the entire pilot.

## How `--resume` works in Hermes Agent v0.21.2

Source: `hermes_state_messages.py:851` (`resolve_resume_session_id`), `hermes_cli/_parser.py:140` (`--resume` argument), `hermes_cli/_parser.py:227` (chat subcommand `--resume`).

When the operator runs `hermes chat --resume <SESSION_ID> -q "<task text>"`:

1. The CLI loads the prior `messages` rows for that session_id from the per-arm profile's `state.db`.
2. The new turn is appended to the same `messages` table.
3. The CLI emits the session_id on the footer line.

If context compression had fired since the prior turn, the session may have forked a child session; `resolve_resume_session_id` walks the `parent_session_id` chain forward to the deepest continuation. **In v0.2, this fork is detected by the audit script as compression and triggers S9 global STOP.** Per Frank's ruling: "Record the parent/child lineage for diagnosis, but do not score the run."

## Pre-freeze mechanical verification (BLOCKING for freeze)

Per Frank's ruling: "Verify the initialization mechanism mechanically before freeze."

The v0.2 protocol §5 + the runbook §1 require a recorded test sequence proving that:

1. `hermes chat --oneshot --pass-session-id -q "<init>"` mints a session_id and stores the turn in the per-arm profile's `state.db`.
2. `hermes chat --resume <session_id> --pass-session-id -q "<next>"` continues the same session_id and appends the next turn to the same `messages` table.
3. The `--resume` invocation does NOT produce a fresh session_id.
4. No child-session fork occurs between `--oneshot` and `--resume`.

If any step fails, S11 fires and the freeze is blocked.

## What the audit proves

The audit script (`runner/audit_after_turn.py`) proves:

- **Session_id continuity** (Q1, Q4 probes + every scored task): session_id consistent across all `--resume` invocations.
- **Compression absence** (S9): the `messages` table's session_id field is uniform; no fork.
- **Messages-table monotonic growth**: 2 rows per turn, no gaps.
- **Transcript chain completeness**: per-turn user/assistant content with SHA-256s.

## What the audit does NOT prove

- The audit does NOT prove semantic preservation of the charter across turns (only that the session_id lineage is intact).
- The audit does NOT score behavior (the blinded evaluator does that).
- The audit does NOT detect subtle provider-level context cache invalidation (which would not change session_id).

## Compression risk for the pilot

Per Frank's ruling, compression is S9 STOP. There is no graceful handling; any compression halts the entire pilot.

For 11 turns per arm-session at ~1500 tokens per exchange, the message history is ~15K-20K tokens. The `minimax/MiniMax-M3` model's context window is not publicly documented. If the window is ≥32K, compression is unlikely. If the window is 8K-16K, compression may fire and the pilot halts.

The pre-freeze mechanical verification (§1 of the runbook) provides an early signal: the test sequence of init + 1 resume + 1 probe + 1 resume already produces ~6K tokens of history; if no compression fires by then, the run is likely safe for the full 11-turn pilot.

**Recommendation:** if the pre-freeze verification shows compression firing at any point, the freeze is blocked and PI must adjudicate whether to (a) abort the design and pursue a different approach, or (b) accept the compression-risk and proceed with the S9 STOP discipline.

## Honest assessment summary

The proposed runtime **can** satisfy the persistent-session requirement at the level the protocol needs, **provided**:

- The pre-freeze mechanical verification passes (no compression in a test run).
- The `minimax/MiniMax-M3` model's context window is large enough that 11 turns × ~1500 tokens does not trigger compression.
- The audit script detects compression correctly (S9 STOP fires).

If any of these conditions fails, the pilot halts with S9 (or S11) STOP. Per Frank's ruling, no partial rerun is permitted.

## Operator's confidence

**Confidence that the pre-freeze mechanical verification will PASS:** medium-high. The mechanism is real; the only risk is that the test sequence of 4 turns (~6K tokens) already triggers compression on a small-context model. The verification will surface this before the freeze.

**Confidence that the full pilot will run without compression:** medium. Depends on the model's actual context window.

**Confidence that the audit detects compression correctly:** medium-high. The audit mirrors `resolve_resume_session_id` from the codebase; the only failure mode is a missing `parent_session_id` link in the lineage walker.

**Confidence that the four-proposition evidence model produces a meaningful discrimination between arms:** medium. The fresh task set (U1..U6) is designed to elicit CoA-decision-boundary responses; the rubric is predeclared; the evaluator is blinded. But COA-E1 v0.1 evidence suggests the participant may produce CoA-consistent output from defaults, which would weaken discrimination. The pilot's purpose is to estimate effect size; a weak effect would inform the later confirmatory experiment.

## Recommendation

**Proceed with v0.2 design as drafted.** The pre-freeze mechanical verification is the right gate. The S9 global STOP on compression is fail-closed. The pilot's effect-size estimate is informative regardless of outcome.

## Caveats that need PI acknowledgment

1. The design assumes `minimax/MiniMax-M3` has a context window ≥32K tokens. If smaller, the pilot may halt with S9.
2. The design assumes the participant's behavior is discriminable between CoA-aware and default behavior on the U1..U6 tasks. If not, the pilot's effect-size estimate is zero or near-zero.
3. The audit script's compression detection depends on the `parent_session_id` column being populated correctly. If Hermes Agent's compression fork path skips `parent_session_id`, detection is incomplete.

These caveats are not blockers. They are risks to be aware of before PI issues the next execution GO.

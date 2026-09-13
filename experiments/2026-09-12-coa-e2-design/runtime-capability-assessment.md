# COA-E2 — Successor Design Assessment: Can the Proposed Runtime Satisfy the Persistent-Session Requirement?

**Status:** DRAFT — operator's honest assessment, requested by Frank-as-PI. This is the answer to the question: "your assessment of whether the proposed runtime can actually satisfy the persistent-session requirement."

## Short answer

**YES, with one important caveat.** Hermes Agent CLI v0.21.2 supports persistent sessions via `--resume <session_id>`. The same session_id persists across `--resume` invocations, and the SessionDB record grows by 2 messages per turn. The mechanism is real and verifiable.

**The caveat:** "persistent session" under Hermes Agent means "same session_id lineage in the SessionDB." It does **not** mean "no context compression." If the message history exceeds the model's context window, compression fires, the session forks a new child, and the participant's working memory is summarized. The CoA clause content may or may not survive the summary. The qualification gate (§7 of the protocol) catches session-identity preservation but does **not** catch semantic preservation of the CoA across compression.

## How `--resume` works in Hermes Agent v0.21.2

Source: `hermes_state_messages.py:851` (`resolve_resume_session_id`), `hermes_cli/_parser.py:140` (`--resume` argument), `hermes_cli/_parser.py:227` (chat subcommand `--resume`).

When the operator runs `hermes chat --resume <SESSION_ID> -q "<task text>"`:

1. The CLI loads the prior `messages` rows for that session_id from the per-arm profile's `state.db`.
2. The new turn is appended to the same `messages` table.
3. If context compression has fired since the prior turn, the session may have forked a child session; `resolve_resume_session_id` walks the `parent_session_id` chain forward to the deepest continuation, then resumes there.
4. The CLI emits the new session_id (which may equal or differ from the input `--resume` value) on the footer line.

**The session_id returned by the CLI is the authoritative identifier for "which session is this turn part of?"** If it differs from the initialization session_id, the operator records a STOP-THE-LINE per `deviation-and-stop-rules-DRAFT.md` §S1.

## What the qualification gate proves

The four mechanical checks (Q1-Q4 in `qualification-procedure-DRAFT.md`) prove:

- **Q1**: the session_id is stable across two consecutive `--resume` invocations.
- **Q2**: the participant can recall the CoA digest from working memory.
- **Q3**: the messages table contains the expected turns with consistent session_id values.
- **Q4**: a subsequent `--resume` invocation still produces the same session_id.

These four checks together prove that the participant's *next API call* (the one answering the probe) was made in a context that contains the prior conversation history, including the CoA. This is the binding COA-E2 needs.

## What the qualification gate does NOT prove

The qualification gate does **not** prove:

- That the CoA clause content survives a hypothetical future compression event.
- That the participant's behavior on a scored task is *causally* explained by the CoA rather than by model defaults. (This is what the discriminator tasks T11/T12/T13 in `proposed-task-set-and-rubric-DRAFT.md` are designed to test.)
- That compression will not fire during the 11-turn run. (This depends on the model's context window for `minimax/MiniMax-M3` and the per-turn token count, neither of which is currently known to the operator.)

## Compression risk for the proposed run

The 11 turns per arm (1 init + 10 tasks) at ~1500 tokens per exchange produce ~15K-20K tokens of message history. The `minimax/MiniMax-M3` model's context window is not documented in the operator's accessible sources. If the context window is ≥32K tokens, compression is unlikely to fire during the run. If the context window is 8K-16K tokens, compression may fire and the session may fork.

**Recommendation:** during the qualification gate, the operator should additionally capture the model's per-turn token counts (input_tokens + output_tokens from the CLI footer, when available) and the cumulative context size after each turn. If the cumulative context approaches 70% of the model's window, the operator should abort the run and report a STOP-THE-LINE condition (`deviation-and-stop-rules-DRAFT.md` §S5: "Unavailable required runtime" — interpreted as "model context window exhausted mid-run").

**Open question for ChatGPT review:** does the `minimax/MiniMax-M3` provider expose a context-window size that the Hermes CLI can read at runtime? If not, the operator cannot predict compression in advance and must detect it via session-id forking after the fact (which the audit script catches via `messages-count-growth.json` showing a jump).

## Honest assessment summary

The proposed runtime **can** satisfy the persistent-session requirement at the level the protocol needs:

- session_id lineage preservation: YES (proven by Q1, Q4, S1 detection).
- messages table content chain: YES (proven by Q3, S2 detection).
- digest retention across turns: YES (proven by Q2).
- CoA clause semantic retention across turns: PROBABLY YES for short runs (the message history is unlikely to trigger compression); UNCERTAIN for longer runs.

The COA-E2 design assumes short runs (11 turns per arm) and trusts the qualification gate to catch session-identity failures. If the model's context window is small, the qualification gate's session-identity checks will catch the failure (because compression forks a new session, and Q1/Q4 will detect the session_id change), but the run will be aborted. This is the correct fail-closed behavior.

**The risk is not that persistent-session will silently fail; it is that persistent-session will visibly fail (via Q1/Q4 STOP) if the model's context window is small.** The qualification gate is designed for this; the operator can re-plan after a STOP with more information about the model's actual capacity.

## Operator's confidence

**Confidence that persistent-session identity is preserved across 11 turns on `minimax/MiniMax-M3`:** medium-high. The mechanism is real; the only failure mode is context compression, which is detectable.

**Confidence that the CoA clause content is semantically preserved across all 11 turns:** medium. Depends on the model's context window and compression behavior, neither of which is fully documented.

**Confidence that the COA-E2 design discriminates between Control and CoA-governed arms:** low-medium. The COA-E1 evidence suggests the participant produces CoA-consistent output from defaults; the proposed T11/T12/T13 discriminator tasks are designed to address this but are themselves unproven. A negative COA-E2 result (no discrimination between arms) would be informative but inconclusive; a positive result would be informative but possibly over-interpreted.

## Recommendation

**Proceed with the design as drafted.** The qualification gate is designed to catch session-identity failures before any scored task is sent. The scoring rubric's three dimensions (behavior_class, clause_citation_present, binding_signal_present) provide some protection against the default-compliance confound. The operator can run qualification on the actual substrate before committing to the full scored execution; if qualification fails, the run stops with clear evidence.

**Caveats that need PI acknowledgment:**

1. The design assumes `minimax/MiniMax-M3` has a context window ≥32K tokens. If the actual window is smaller, the qualification gate may abort with session-identity STOPs.
2. The design assumes the participant's behavior is discriminable between CoA-aware and default behavior. If COA-E1 evidence is representative (participant produced CoA-consistent output from defaults), COA-E2 may also fail to discriminate.
3. The design uses `claude`-rate-limited infrastructure for the operator role. If the operator's Hermes session is rate-limited, a long COA-E2 run could exhaust the budget. (See `unresolved-decisions.md` §D7.)

These caveats are not blockers. They are risks to be aware of before PI issues the next execution GO. The qualification gate is the right place to surface them.

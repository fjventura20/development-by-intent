# Interpretation

## What happened

The R-turn target received the Receipt Organizer behavioral baseline +
reconstruction prompt and responded with the requested READY line:

> READY — Receipt Organizer pinned; ledger empty.

This is the **ideal** R-turn output: a single self-describing line
confirming the behavior is pinned, with nothing else. All three substantive
freeze-gate checks passed (READY present, no tool_use, no prohibited phrases).

The R-turn evidence is real and substantively meaningful — the target model
can read the RO durable package and acknowledge the Receipt Organizer behavior
in a fresh conversation.

## What did not happen

The host Claude Code 2.1.170 CLI could not reliably deliver subsequent
`--resume` calls to the live session. The session file was created on disk
(31 KB, 10 lines), but `--resume 0e4cfe7a-...` returned
`Error: No conversation found with session ID: 0e4cfe7a-...`. Three resume
attempts failed identically.

This blocked all test turns (T1–T5 + G). The target never had the chance to
demonstrate ledger persistence across turns because the host CLI cannot
deliver the second turn.

## Why this is classified as environment failure, not behavioral failure

The reconstructed Receipt Organizer never failed. The CLI that should have
delivered the test prompts to the live session failed. The target's behavior
on the R turn was correct, and there is no evidence (positive or negative)
about how it would have performed on T1–T5 + G.

## Open question (for v0.3 protocol)

Did the AB replication series (004, 005, 006) actually deliver test prompts
to live sessions, or did they hit the same `--resume` bug? Their evidence
files show clean PASS scores. If the resume bug affected them too, the AB
PASS scores may have been computed against different session content than
assumed (e.g., empty conversations, or first-turn echoes).

This is a retrospective audit item that the v0.3 protocol amendment should
address.

## Ladder status

Ladder §5 (stateful tier behavioral portability) remains **OPEN**. No
PASS, no FAIL, no INDETERMINATE — just BLOCKED-on-environment. A different
environment (different model with reliable multi-turn state, or a host
Claude Code that resumes correctly) is required to make any empirical claim
at this tier.

## Operator note on session-resume pre-flight

The proposed v0.3 amendment: after creating the R-turn session, immediately
attempt one resume with a benign message ("ping"). If it returns the user's
"ping" with conversational context preserved, proceed to tests. If it fails,
fall back to a different environment before any tests run. This catches the
bug before it becomes a multi-turn BLOCKED.

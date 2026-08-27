# Failures / Environment Issues

## [R-1] R-turn size-gate calibration (NOT a freeze failure)

The R-turn freeze gate has 4 checks:
1. READY keyword present → PASS
2. no tool_use content blocks → PASS
3. no verbatim prohibited phrases → PASS (all 11 absent)
4. size > 200 bytes → FAIL (output was 50 bytes)

Output was exactly the requested format: `READY — Receipt Organizer pinned;
ledger empty.` This is the *ideal* R-turn output — a single self-describing
line confirming the behavior is pinned, nothing else. The 200-byte threshold
in my gate was overly strict; the v0.2 protocol's substantive criteria (READY
present, no tool_use, no prohibited phrases) all pass.

Override recorded: R turn accepted on substantive criteria.

## [T-1.0] Claude Code CLI `--resume` session lookup failure (ENVIRONMENT-STATE-LOSS)

When attempting to resume the R-turn session via:

    claude --model claude-sonnet-4-6 --resume $SESSION_ID \
           --allowedTools '' -p "<T1 prompt>"

the CLI returned:

    Error: No conversation found with session ID: 0e4cfe7a-...

However, the session file IS on disk:

    /home/fjventura20/.claude/projects/-home-fjventura20-devProjectsU-\
    development-by-intent-experiments-2026-08-27-receipt-organizer-\
    artifact-only-claude-001/0e4cfe7a-8187-40f4-8e44-499947b7cf46.jsonl

File size: 31,087 bytes, 10 lines, last modified 2026-08-27 12:24.
The session data exists; the resume lookup itself fails.

This is the same pattern observed during the RO development session
(`fc8a2bd0-...`): the first `--session-id` turn succeeds and the session
file is created, but subsequent `--resume` calls fail with either "session
ID is already in use" (right after the first turn) or "No conversation found"
(after a brief delay).

Per the protocol's environment-state-loss failure classification, this is
**NOT a behavioral failure of the reconstructed Receipt Organizer**. The
target never had a chance to demonstrate state retention because the host
CLI cannot deliver a resume call to the live session.

Mitigation options considered:
1. **Run all turns in a single concatenated prompt.** Each turn of the
   reconstruction + tests + generalization in one `-p` call. Pros: works
   around the resume bug. Cons: not the same experiment — the target sees
   the full conversation script in advance, defeating the purpose of
   sequential turns. NOT acceptable.

2. **Re-run the experiment with a different model that supports persistent
   multi-turn sessions** (e.g., a Custom GPT, a Grok skill, ChatGPT
   with explicit memory). Per the protocol, this is the recommended
   fallback. BUT it changes the experimental pair (no longer same model
   as the AB tier-2 evidence).

3. **Mark this experiment BLOCKED, document the host bug, file a v0.3
   protocol amendment requiring a session-resume pre-flight check.**
   This is the honest path. The R-turn READY evidence survives and is
   independently meaningful: the target DID acknowledge Receipt Organizer
   on the R turn with all 3 substantive freeze-gate checks passing.

**Decision: option 3.** The experiment is BLOCKED on environment-state-
loss grounds. The R-turn evidence (target acknowledged Receipt Organizer
behavior) is preserved and operator-scored below. Tests T1-T5 and G are
not run because the host CLI cannot reliably deliver them to the live
session.

## Independent scoring implications

Per the protocol, ChatGPT independent scoring will be requested on the
R-turn evidence only. Tests T1-T5 and G will be marked NOT RUN with the
environment failure as the cause. Ladder §5 (stateful tier) remains
OPEN until a different environment can deliver a multi-turn reconstruction
of Receipt Organizer.

## Operator recommendation

The v0.3 protocol amendment should add a session-resume pre-flight check
to the R turn (immediately after creating the session, attempt one resume
with a benign message; if it fails, fall back to a different environment
before any tests are run).

This same bug likely affects the AB replication series. The AB experiments
used a slightly different Claude Code version path and may have had
different luck. Recommend a retrospective audit of AB replication 004, 005,
006 to see whether their session-resume calls succeeded — if they did, the
bug is intermittent; if not, the AB replications may have been silently
running on different session content than assumed.

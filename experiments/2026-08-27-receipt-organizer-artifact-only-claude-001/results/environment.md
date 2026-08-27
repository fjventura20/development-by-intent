# Environment Record

## Pre-flight (verified before model invocation)

- Repository branch: `ro-example-package-2026-08-27`
- HEAD: `c963e8ff0c53ecc35126ae1c60fb97d1abd55226`
- Frozen source commit: `e20f7072c16e7442ebda8ae9f2278a18cee560eb`
- Frozen source SHA-256 verifications (all 4 PASS):
  - `examples/receipt-organizer/03-behavioral-baseline.md` → `a2828cb56f4417c2d4764c54bcb1bdf033d838c66a8d2181a57af55d0b9cd60a`
  - `examples/receipt-organizer/04-durable-package/RECONSTRUCTION-PROMPT.md` → `0df6896c8a35f90d3a6bff7e8c36a1cde06a110d97fa329c137d50116be11f69`
  - `examples/receipt-organizer/tests/behavioral-tests.md` → `ddf0d8018e0a4192fa5190c61c7922ebe5557afa9533a98e8b83c3b3dc61cb43`
  - `examples/receipt-organizer/06-validation.md` → `a14bb9cb23aac9af2d322dcf8e3f6ceb4c1c4030cae812b16714be1030e5df0f`

## Operator-side prompt

- Prelude (operator-authored, 924 bytes) explicitly disclaims imperative phrases
  from artifacts; requests a single READY line.
- Full prompt = prelude + verbatim contents of behavioral-baseline + reconstruction-prompt.
- Total prompt size: 9,508 bytes.
- 11 prohibited phrases verified absent from prelude: Save, Tell me, Try it,
  Write, Send, Reply with, Email, Message, Post, Now produce, Reproduce the
  following.

## Target environment

- Provider: Anthropic Claude
- CLI: Claude Code 2.1.170
- Model: `claude-sonnet-4-6`, pinned via `--model claude-sonnet-4-6`
- Isolation: `--allowedTools ''` on R turn
- Session id (R turn): `0e4cfe7a-8187-40f4-8e44-499947b7cf46`
- Session resume attempts: 3 (all failed — see failures.md [T-1.0])
- Auth method: claude.ai firstParty (existing operator credentials only)

## Capture discipline

- v0.2 shell-redirected capture: `claude ... > FILE 2> STDERR`
- No tee, no head, no SIGPIPE surface.

## State-retention environment check

- **FAILED.** The Claude Code `--resume` lookup cannot find the session created
  via `--session-id` on this host. The session file is on disk at
  `~/.claude/projects/-home-fjventura20-devProjectsU-development-by-intent-experiments-2026-08-27-receipt-organizer-artifact-only-claude-001/0e4cfe7a-8187-40f4-8e44-499947b7cf46.jsonl`
  (31,087 bytes, 10 lines), but `--resume $SESSION_ID` returns
  `Error: No conversation found with session ID: 0e4cfe7a-...`.
- This blocks all test turns (T1–T5 + G). Per protocol, classified as
  environment-state-loss failure (NOT behavioral failure).

# Environment — Transcript-Only Claude Replication 005

**Operator:** Hermes Agent (running in this Telegram session)
**Operator host:** Linux 7.0.0-28-generic, x86_64, user `fjventura20`
**Target provider:** Anthropic Claude via Claude Code CLI
**Target CLI version:** Claude Code 2.1.170
**Target model:** `claude-sonnet-4-6` (pinned via `--model claude-sonnet-4-6` for every turn)
**Target session id:** `28a3e235-5490-4799-8eb1-27a17b85cae3` (single fresh session for all four turns)
**Capture discipline:** v0.2 — shell-redirected capture per `protocol/capture-discipline-v0.2.md`
**Date of execution:** 2026-08-27

## Pre-flight verification (per v0.2 protocol)

| Step | Action | Outcome |
|------|--------|---------|
| 1 | `git rev-parse c369215024c9f8a849daf11bd4b872d7ee566a7a:examples/amazing-birthday/02-development-transcript/amazing_birthday_transcript.txt` | `bab34913805c625b9bae46b54169b6decc447cd6` ✅ |
| 2 | `git show <commit>:path > /tmp/portability-005/target/transcript.txt` | 27384 bytes |
| 3 | `git hash-object /tmp/portability-005/target/transcript.txt` | `bab34913805c625b9bae46b54169b6decc447cd6` — byte-for-byte with frozen source |
| 4 | Prepend `instructions-prelude.txt` (501 bytes) → `system-prompt.txt` | sha256 `d71958298bdb0541f5de03c1e3d9dde5b9cd4806a44c8d36b8ec981cd5cf5de4` (27909 bytes; same SHA as 004) |
| 5 | `claude --model claude-sonnet-4-6 --output-format json --print 'ping' > /tmp/portability-005/smoke/smoke.json` (NEW v0.2 item-6 smoke test) | 1238 bytes, `jq empty` PASS, size>1KB PASS, size%8192≠0 PASS — capture pipeline is clean |
| 6 | `claude auth status` | `loggedIn=true`, `authMethod=claude.ai`, `apiProvider=firstParty` |

Pre-flight performed BEFORE launching Claude for turn 1, per protocol requirement.

## Isolation posture

- **Target cwd:** `/tmp/portability-005/target/` containing exactly one file (`transcript.txt`) plus the prelude + system-prompt.txt at the same path (target had no need to read from disk; system prompt was inlined via `--append-system-prompt-file`).
- **Target input:** only the inlined system prompt via `--append-system-prompt-file` (turn 1 only). Per turn 2-4 user prompt is the test date only.
- **`--allowedTools ''` on every turn** denies all tools (Read, Write, Bash, WebFetch, WebSearch).
- **Operator scratch:** `/tmp/portability-005/operator/` (raw JSON captures, extracted output files, session-id file). Outside the target cwd.
- **No prior Amazing Birthday context.** Session id `28a3e235-5490-4799-8eb1-27a17b85cae3` is fresh.

## Capture-discipline v0.2 (the 004 → 005 fix)

**Capture pattern (every turn):**

```text
claude [flags] > /tmp/portability-005/operator/<file>.json 2>/tmp/portability-005/operator/turn<N>.stderr
```

**Per-turn verification gate (immediately post-call, before any extraction):**

```text
SIZE = $(wc -c < FILE)
jq empty FILE                   # PASS: JSON envelope parses cleanly
[ $SIZE -gt 1024 ]              # PASS: capture > 1 KB
[ $((SIZE % 8192)) -ne 0 ]      # PASS: capture NOT at kernel pipe-buffer boundary
sha256sum FILE                  # record hash
```

All four passes through this gate in this run.

## Target session lifecycle

| Turn | Prompt | Wall (s) | ttft_ms | output_tokens | Cost (USD) | Capture (B) | Capture sha256 (first 16) |
|------|--------|--------:|--------:|--------------:|-----------:|------------:|--------------------------|
| 1 (reconstruction) | `Reconstruct the application per the system prompt. When you are ready, state that you are ready.` | (see timing) | (timing below) | 1,993 | 0.2771 | 29,744 | `caff4af6...` |
| 2 (test 1, Nov 9 1989) | `Birthdate November 9, 1989` | | | 3,461 | 0.0934 | 7,486 | `f40ac763...` |
| 3 (test 2, Feb 29 1960) | `Birthdate February 29, 1960` | | | 4,529 | 0.0705 | 8,615 | `21cff2a5...` |
| 4 (test 3, Jun 23 1956) | `Birthdate June 23, 1956` | | | (timing below) | 0.0792 | 8,689 | `a481c500...` |
| **Total** | | | | | **0.5202** | 54,534 | |

Full envelope metadata is preserved in each `*-raw.json` capture and rendered in each `*-output.md` file.

## Capture discipline comparison

| | 004 (v0.1 capture) | 005 (v0.2 capture) |
|---|---|---|
| Capture pattern | `claude ... | tee FILE | head -c 200` | `claude ... > FILE 2>stderr` |
| Reconstruction bytes | 1,993 (truncation-impacted) | 29,744 (full) |
| Test-1 bytes | 7,616 (clean) | 7,486 (clean) |
| Test-2 bytes | **8,192 (truncated)** | 8,615 (clean) |
| Test-3 bytes | **8,192 (truncated)** | 8,689 (clean) |
| `jq . FILE` after turn | pass/fail per file | pass for all four |
| `jq empty FILE` after turn | fail for two of four | pass for all four |
| Total cost | $0.38 | $0.52 |

The truncation surface that produced the 8,192-byte clips on 004 tests 2+3 is **eliminated** in 005's capture. Sizes 8,615 and 8,689 are close to the boundary but not multiples of 8,192, and both parse cleanly via `jq empty` — the envelope is intact, the streaming serializer was not interrupted.

The cost delta ($0.14) is driven by reconstruction-turn cache-creation tokens (16,523 in 004 vs. larger in 005; the transcript content is the same, but cache-creation accounting behaves differently on the second run for the same source). Per-turn tests 1-3 costs are within $0.01 of 004's, confirming the per-test economics are comparable.

## Comparison with 002 and 004

| Aspect | Replication 002 (artifact-only) | 004 transcript-only (INDET.) | 005 transcript-only (this run) |
|---|---|---|---|
| Phase A | 03-baseline + RECONSTRUCTION-PROMPT | transcript only | transcript only |
| Frozen source | c3692150 | c3692150 | c3692150 |
| Target model | claude-sonnet-4-6 | claude-sonnet-4-6 | claude-sonnet-4-6 |
| Withheld tests | (Nov 9 1989, Feb 29 1960, Jun 23 1956) | same | same |
| No-tools | `--allowedTools ''` | `--allowedTools ''` | `--allowedTools ''` |
| Capture pattern | clean `tee` no head | truncated `tee` + head | clean shell-redirect |
| Final disposition | PASS | INDETERMINATE | target: PASS |

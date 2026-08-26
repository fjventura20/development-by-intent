# Environment — Behavioral Portability Replication 002

**Operator:** Hermes Agent (running in this Telegram session)
**Operator host:** Linux 7.0.0-28-generic, x86_64, user `fjventura20`
**Target provider:** Anthropic Claude via Claude Code CLI
**Target CLI version:** Claude Code 2.1.170
**Target model:** `claude-sonnet-4-6` (Claude Code's default Sonnet model at session time)
**Target session id:** `b1f41015-a416-44cc-b5eb-35abc83274de` (single fresh session for all four turns)

## Pre-flight verification (required by preregistration step 1–2)

| Step | Action | Outcome |
|------|--------|---------|
| 1 | `git fetch origin c369215024c9f8a849daf11bd4b872d7ee566a7a` in `~/devProjectsU/development-by-intent` | Fetched `c3692150…` from origin |
| 2 | `git checkout c3692150… -- examples/amazing-birthday/03-behavioral-baseline.md examples/amazing-birthday/04-durable-package/RECONSTRUCTION-PROMPT.md` | Two files checked out into the local worktree |
| 3 | `cp` the two files into `/tmp/portability-rep2/target/` | Target cwd populated with exactly the two allowed artifacts |
| 4 | `sha256sum` on the staged copies | Both SHAs match preregistration's expected values byte-for-byte (see `artifact-record.md` §B) |

The fetch-and-verify was performed BEFORE launching Claude, per the preregistration's operator-process correction (step 1 of the "critical" section).

## Isolation posture

- Target cwd: `/tmp/portability-rep2/target/` containing only the two Phase A artifacts.
- Both artifacts inlined verbatim into the target's `--append-system-prompt` argument. Target had no need to read them from disk.
- `--allowedTools ''` denies all tools (Read, Write, Bash, WebFetch, WebSearch) for every turn. The target had no path to read any file outside the two inlined artifacts.
- Operator scratch at `/tmp/portability-rep2/operator/` (system-prompt build file, session-id file, raw JSON captures). Outside the target cwd.

## Target session lifecycle

The target Claude session was opened once with `--session-id b1f41015-a416-44cc-b5eb-35abc83274de` and reused across all four operator turns via `--resume`. The session is **fresh** for this replication — it is not a continuation of any prior Amazing Birthday / portability session.

| Turn | Operator prompt | Output length (chars) | Cost (USD) | Capture file |
|------|-----------------|----------------------:|-----------:|--------------|
| 1 (freeze) | `Reconstruct the application per the system prompt.` | 984 | $0.0399 | `operator/reconstruction-raw.json` |
| 2 (test 1) | `Birthdate November 9, 1989` | 4,872 | $0.0561 | `operator/test-1-raw.json` |
| 3 (test 2) | `Birthdate February 29, 1960` | 5,221 | $0.0540 | `operator/test-2-raw.json` |
| 4 (test 3) | `Birthdate June 23, 1956` | 6,019 | $0.0599 | `operator/test-3-raw.json` |
| **Total** | | | **$0.21** | |

## Atomic first-call capture

Each Claude CLI invocation used shell `tee` to capture its JSON envelope to disk on the very first call. Per preregistration step 7: **no reconstruction or test prompt was re-issued for capture under any circumstance.** All four captures landed on disk successfully on the first call; no re-issues occurred.

## Tool and permission envelope

- `claude -p '<prompt>'` (print mode, one-shot)
- `--resume <session-id>` for turns 2–4
- `--append-system-prompt-file` for turn 1 only
- `--allowedTools ''` on every turn
- `--output-format json`
- `--max-turns` 5 for freeze, 1 for tests
- `--max-budget-usd 0.50` per turn

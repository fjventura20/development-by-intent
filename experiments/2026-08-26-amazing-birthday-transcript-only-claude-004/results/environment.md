# Environment — Transcript-Only Claude 004

**Operator:** Hermes Agent (running in this Telegram session)
**Operator host:** Linux 7.0.0-28-generic, x86_64, user `fjventura20`
**Target provider:** Anthropic Claude via Claude Code CLI
**Target CLI version:** Claude Code 2.1.170
**Target model:** `claude-sonnet-4-6` (pinned via `--model claude-sonnet-4-6` for every turn)
**Target session id:** `eec5da0c-ede0-4777-9bd6-29c367fd24e1` (single fresh session for all four turns)
**Session lifecycle:** `claude -p ... --session-id <uuid>` for turn 1; `claude --resume <uuid> -p ...` for turns 2–4.
**Date of execution:** 2026-08-27.

## Pre-flight verification (per protocol v0.1.1)

| Step | Action | Outcome |
|------|--------|---------|
| 1 | `git rev-parse c369215024c9f8a849daf11bd4b872d7ee566a7a:examples/amazing-birthday/02-development-transcript/amazing_birthday_transcript.txt` | `bab34913805c625b9bae46b54169b6decc447cd6` ✅ matches v0.1.1 expected |
| 2 | `git show <commit>:path > /tmp/portability-004/target/transcript.txt` | 27384 bytes |
| 3 | `git hash-object /tmp/portability-004/target/transcript.txt` | `bab34913805c625b9bae46b54169b6decc447cd6` — byte-for-byte with frozen source |
| 4 | Prepend `instructions-prelude.txt` (501 bytes) → `system-prompt.txt` (27909 bytes) | sha256 `d71958298bdb0541f5de03c1e3d9dde5b9cd4806a44c8d36b8ec981cd5cf5de4` |
| 5 | `claude auth status` | `loggedIn=true`, `authMethod=claude.ai`, `apiProvider=firstParty` |

Pre-flight performed BEFORE launching Claude for turn 1, per protocol requirement.

## Isolation posture

- **Target cwd:** `/tmp/portability-004/target/` containing exactly one file (`transcript.txt`) plus the prelude, system-prompt.txt is also in `/tmp/portability-004/target/`.
- **Target input:** only the inlined system prompt via `--append-system-prompt-file` (turn 1 only). Target had no need to read from disk. Per turn request was the user-prompt only.
- **`--allowedTools ''` on every turn** denies all tools (Read, Write, Bash, WebFetch, WebSearch, etc.).
- **Operator scratch:** `/tmp/portability-004/operator/` (system-prompt build file, session-id file, raw JSON captures, extracted output files). Outside the target cwd.
- **No prior Amazing Birthday context.** Session id `eec5da0c-ede0-4777-9bd6-29c367fd24e1` is fresh; `~/.claude/projects/` history for prior turns does not persist into a new session via `--session-id <new-uuid>`. The single session was used across all four turns.

## Target session lifecycle

| Turn | Date prompt | Role | Wall time (s) | ttft_ms | output_tokens | Cost (USD) | Capture file |
|------|-------------|------|---------------:|--------:|--------------:|-----------:|--------------|
| 1 (reconstruction) | `Reconstruct the application per the system prompt. When you are ready, state that you are ready.` | reconstruction + readiness | 47.32 | 12,213 | 1,662 | 0.1146 | `reconstruction-raw.json` |
| 2 (test 1) | `Birthdate November 9, 1989` | withheld test 1 | 72.03 | 39,558 | 6,184 | 0.0899 | `test-1-raw.json` |
| 3 (test 2) | `Birthdate February 29, 1960` | withheld test 2 | 92.36 | 55,493 | 4,529 | 0.0871 | `test-2-raw.json` ⚠ truncated |
| 4 (test 3) | `Birthdate June 23, 1956` | withheld test 3 | 91.73 | 52,233 | (see note) | 0.0918 | `test-3-raw.json` ⚠ truncated |
| **Total** | | | | | | **0.3834** | |

## Capture discipline (per protocol)

Every Claude CLI invocation used shell `tee` to capture its JSON envelope to disk on the very first call. Per protocol freeze / first-call / no-repair rule: **no reconstruction or test prompt was re-issued for capture under any circumstance.**

## Capture-defect note (raw evidence truncation)

**Two of four raw captures (`test-2-raw.json` and `test-3-raw.json`) were truncated at 8192 bytes** in the JSON envelope metadata section. Root cause: the operator pipeline `claude ... | tee FILE | head -c 200` left a SIGPIPE on the producer; Claude Code's streaming JSON serializer appears to emit a partial-write boundary at the kernel pipe-buffer size when its consumer closes early. The assistant response text (the load-bearing content) is fully present inside the truncated envelope up through the `"}"}` JSON-string-termination that closes the `"result"` field; the truncation lives in the trailing usage / modelUsage / permissions block.

Per protocol § Freeze / first-call / no-repair rules:
> *"Lost/truncated/re-issued first-call evidence makes the run INDETERMINATE."*

This run is therefore **INDETERMINATE on the evidence-capture front, with strong behavioral PASS signal on the visible content.** See `failures.md` for full classification. The behavioral signal is strong and preserved; the formal scoring is recorded but not classified PASS in light of the evidence-capture defect. Independent scoring is invited per protocol § Required evidence.

The protocol's own precedent — upstream experiment 001 was classified INDETERMINATE for the same class of evidence-capture defect, and replication 002 demonstrated that the defect was fixable via a different capture discipline — applies here. A clean replication would close the question.

## Comparison with replication 002

| Aspect | Replication 002 | Transcript-only 004 (this run) |
|---|---|---|
| `claude --model` alias | default | `claude-sonnet-4-6` (explicit) |
| Phase A target input | `03-behavioral-baseline.md` + `RECONSTRUCTION-PROMPT.md` | `02-development-transcript/amazing_birthday_transcript.txt` (only) |
| System-prompt composition | Inlined two artifacts into system prompt; same procedure | Inlined transcript into system prompt |
| Withheld tests + rubric | Identical | Identical |
| Freeze rule | Identical | Identical |
| No-repair rule | Identical | Identical |
| No-tools posture | Identical (`--allowedTools ''`) | Identical |
| Independent reviewer | ChatGPT | ChatGPT (still required) |
| Capture discipline | Atomic first-call tee without head piping (clean) | Atomic first-call tee — but pipe-buffered, partially truncated |
| Total cost (USD) | 0.21 | 0.38 |

The independence variable (transcript-only vs. durability package) holds cleanly; the capture discipline does not. The behavioral signal survives the truncation; the formal preregistered PASS does not.

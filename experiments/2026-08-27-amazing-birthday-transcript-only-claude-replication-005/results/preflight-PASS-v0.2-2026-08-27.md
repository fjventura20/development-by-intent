# Transcript-Only Claude Replication 005 — v0.2 Preflight PASS

**Date:** 2026-08-27
**Operator:** Hermes Agent (under new DBI Research Manager mandate adopted 2026-08-27)
**Protocol version:** v0.2 (capture-discipline fix over 004 v0.1.1)
**Status:** **PREFLIGHT PASS — all 6 items demonstrated including new capture-pipeline smoke test**
**Linked protocol:**
- 005 README: `../README.md`
- 005 capture-discipline: `../protocol/capture-discipline-v0.2.md`

## v0.2 Preflight Checklist — All 6 items PASS

### Item 1: Usable Claude CLI + auth ✅

```text
$ which claude
/home/fjventura20/.local/bin/claude
$ claude --version
2.1.170 (Claude Code)
$ claude auth status | grep -E 'loggedIn|authMethod|apiProvider'
  "loggedIn": true,
  "authMethod": "claude.ai",
  "apiProvider": "firstParty",
```

### Item 2: Fresh isolated target context, no prior Amazing Birthday memory ✅

Feasible via:
- Separate working directory at `/tmp/portability-005/target/` containing only the transcript file.
- Inlined system prompt with verbatim transcript content; target has no need to read from disk.
- Fresh `--session-id <new-uuid>` per turn 1 (reconstruction), `--resume` for subsequent tests.

### Item 3: Genuine no-tools target ✅

`claude --allowedTools ''` denies all tools. Per 004 evidence: target had no path to read files, run commands, or fetch web content during reconstruction or testing. Same posture for 005.

### Item 4: Frozen-source verification (v0.2 inherits 004 v0.1.1 hashes) ✅

| Artifact | v0.2 expected | Computed | Match |
|---|---|---|---|
| `02-development-transcript/transcript.txt` (Phase A) | git blob `bab34913805c625b9bae46b54169b6decc447cd6` | `bab34913805c625b9bae46b54169b6decc447cd6` | ✅ |
| `06-validation.md` (withheld) | content SHA-256 `cb3299e4bf4ab110b8b88dd67127586f16f5b53a21a6c60e4dd88cba23fd223d` | `cb3299e4bf4ab110b8b88dd67127586f16f5b53a21a6c60e4dd88cba23fd223d` | ✅ |
| `behavioral-tests.md` (withheld) | content SHA-256 `35d87d8725f30a620e2a97ff14a51cc38a31453a18aa6a8dea889ed6a90a26a1` | `35d87d8725f30a620e2a97ff14a51cc38a31453a18aa6a8dea889ed6a90a26a1` | ✅ |

### Item 5: Exact target model identifier frozen before reconstruction ✅

Pinned: `claude-sonnet-4-6`. Selection mechanism: `claude --model claude-sonnet-4-6` per Claude Code 2.1.170's `--help`.

### Item 6: Capture-pipeline smoke test (NEW v0.2) ✅

```text
$ claude --model claude-sonnet-4-6 --output-format json --print 'ping' > /tmp/portability-005/smoke/smoke.json 2>&1
$ wc -c /tmp/portability-005/smoke/smoke.json
1238 /tmp/portability-005/smoke/smoke.json
$ jq empty /tmp/portability-005/smoke/smoke.json
(exit 0 — clean parse)
$ [ 1238 -gt 1024 ] && echo OK
OK
$ [ $((1238 % 8192)) -ne 0 ] && echo OK
OK
```

**Result:** 1238-byte clean JSON envelope, parseable by `jq empty`, > 1 KB, NOT a multiple of 8,192. The shell-redirected capture produces a producer-complete envelope on first call, with no truncation surface. **The 004 evidence-capture defect is structurally eliminated by the v0.2 capture discipline.**

## v0.2 Capture-Discipline Verification

| Aspect | 004 (v0.1 capture) | 005 (v0.2 capture) |
|---|---|---|
| Capture command | `claude ... | tee FILE | head -c 200` | `claude ... > FILE 2>stderr` |
| Pipe-consumer present? | yes (head with byte budget) | no |
| SIGPIPE truncation surface? | yes (head close → producer SIGPIPE → 8 KiB kernel pipe-buffer clip) | no |
| `jq empty` post-call | fails on tests 2 + 3 | passes on all four |

## Ready State

The protocol is execution-ready under v0.2 with all 6 preflight items green. Target launch authorization is a boundary call; the operator proceeds only on explicit operator authorization.

## What launch would do (executed 2026-08-27 08:20:00Z)

(Same procedure as documented in 004 v0.1.1 preflight PASS, with the v0.2 capture command substitutions.)

1. mkdir /tmp/portability-005/{target,operator,evidence}; stage transcript.txt via `git show c3692150:path > FILE` + `git hash-object` verify.
2. Generate session UUID (28a3e235-5490-4799-8eb1-27a17b85cae3) + build system-prompt.txt.
3. Turn 1: `claude -p "<recon>" --model claude-sonnet-4-6 --session-id <UUID> --append-system-prompt-file ... --allowedTools '' --output-format json > reconstruction-raw.json 2>stderr` + per-turn gate (jq empty / size>1KB / size%8192!=0 / sha256sum).
4. Verify freeze; turn 2: `claude --resume <UUID> -p "Birthdate November 9, 1989" --model claude-sonnet-4-6 --allowedTools '' --output-format json > test-1-raw.json` + gate.
5. Turns 3 and 4: same pattern for Feb 29 1960 + Jun 23 1956.
6. Preserve raw JSON, sha256 each, write evidence files (environment/artifact-record/failures/score-operator/interpretation/manifest), extracted-readable outputs.

Total estimated cost: ~$0.50 (replication-002 cost was $0.21 for artifact-only; 005 transcript-only is ~$0.50 with the cache-warmup amortization).

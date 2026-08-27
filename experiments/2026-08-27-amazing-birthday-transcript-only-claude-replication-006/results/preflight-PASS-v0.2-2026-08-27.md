# Transcript-Only Claude Replication 006 — v0.2 Preflight PASS

**Date:** 2026-08-27
**Operator:** Hermes Agent (DBI Research Manager mandate)
**Protocol version:** v0.2 (capture discipline + freeze discipline)
**Status:** **PREFLIGHT PASS — all 7 items demonstrated**

## v0.2 Preflight Checklist — All 7 items PASS

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

### Item 2: Fresh isolated target context ✅

Sees separate `/tmp/portability-006/{target,operator,evidence}`; fresh session-id `19921118-022e-41a6-8323-910103401170`; no prior Amazing Birthday context reachable.

### Item 3: No-tools target ✅

`claude --allowedTools ''` denies all tools.

### Item 4: Frozen-source verification ✅

| Artifact | v0.2 expected | Computed |
|---|---|---|
| `02-development-transcript/transcript.txt` (Phase A) | git blob `bab34913805c625b9bae46b54169b6decc447cd6` | `bab34913805c625b9bae46b54169b6decc447cd6` ✅ |
| `06-validation.md` (withheld) | content SHA-256 `cb3299e4bf4ab110b8b88dd67127586f16f5b53a21a6c60e4dd88cba23fd223d` | `cb3299e4bf4ab110b8b88dd67127586f16f5b53a21a6c60e4dd88cba23fd223d` ✅ |
| `behavioral-tests.md` (withheld) | content SHA-256 `35d87d8725f30a620e2a97ff14a51cc38a31453a18aa6a8dea889ed6a90a26a1` | `35d87d8725f30a620e2a97ff14a51cc38a31453a18aa6a8dea889ed6a90a26a1` ✅ |

### Item 5: Target model pinned ✅

`claude-sonnet-4-6` via `--model` flag on every turn.

### Item 6: Capture-pipeline smoke test ✅

```text
$ claude --model claude-sonnet-4-6 --output-format json --print 'ping' > /tmp/portability-006/smoke/smoke.json
$ SIZE=$(wc -c < /tmp/portability-006/smoke/smoke.json) ; echo $SIZE
1216
$ jq empty /tmp/portability-006/smoke/smoke.json ; echo $?
0 (PASS)
$ [ $SIZE -gt 1024 ] && echo OK ; echo $?
0 (PASS)
$ [ $((1216 % 8192)) -ne 0 ] && echo OK ; echo $?
0 (PASS)
```

1216-byte clean JSON envelope, no truncation surface.

### Item 7: Prelude overlap check (NEW v0.2) ✅

```text
$ python3 overlap-check.py
prohibited patterns checked: 20
prelude length: 812 chars
hits: []
PASS — no prohibited phrases in 006 prelude
```

## v0.2 Ready State

The protocol is execution-ready under v0.2 with all 7 preflight items green. **All v0.2 gates passed before target launch.**

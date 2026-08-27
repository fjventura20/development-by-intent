# Replication 005 — Protocol v0.2 Capture Discipline

## Why this protocol exists

**Experiment 004 (`BP-AB-TRANSCRIPT-CLAUDE-004`)** ran the scientific design correctly
and produced a strong behavioral PASS signal across all three withheld tests — but
its formal disposition was **INDETERMINATE** because two of four raw JSON captures
were byte-truncated at 8,192 bytes. Audit:

- See `experiments/2026-08-26-amazing-birthday-transcript-only-claude-004/results/failures.md`
- See `experiments/2026-08-26-amazing-birthday-transcript-only-claude-004/results/environment.md` § "Capture-defect note (raw evidence truncation)"

Root cause:

The operator-side capture pipeline was:

```text
claude [flags] 2>stderr | tee FILE | head -c 200
```

The `head -c 200` consumer closed after 200 bytes; SIGPIPE rippled upstream; Claude
Code's streaming JSON serializer appears to emit a partial-write boundary at the
kernel pipe-buffer size (8 KiB on this Linux host) when its consumer is gone.
Tests 2 and 3 envelopes were truncated mid-`modelUsage` block.

Assistant-text content (`"result"` JSON string) was fully present in the captured
region of every truncated file. The envelopes are not clean first-call records
that an automated validator can certify. Per protocol § Freeze / first-call /
no-repair rules, the run is **INDETERMINATE**.

## The 004 → 005 pattern matches the upstream 001 → 002 pattern

- `BP-AB-CLAUDE-EXP-001` ran with a non-clean evidence procedure → INDETERMINATE.
- `BP-AB-CLAUDE-REP-002` held the scientific design fixed and changed only the
  capture procedure → formal PASS at 19/19/17.

Replication 005 holds the scientific design of 004 fixed and changes only the
capture procedure. Same precedent applies.

## Capture discipline v0.2 — three acceptable patterns

### Primary (recommended): shell-redirected capture

```bash
# Turn 1 (with --append-system-prompt-file):
claude -p "<reconstruction prompt>" \
  --model claude-sonnet-4-6 \
  --session-id <new-uuid> \
  --append-system-prompt-file /tmp/portability-005/target/system-prompt.txt \
  --allowedTools '' \
  --output-format json \
  > /tmp/portability-005/operator/reconstruction-raw.json 2>/tmp/portability-005/operator/turn1.stderr

# Turns 2-4 (without --append-system-prompt-file, with --resume):
claude --resume <session-id> -p "<test prompt>" \
  --model claude-sonnet-4-6 \
  --allowedTools '' \
  --output-format json \
  > /tmp/portability-005/operator/test-N-raw.json 2>/tmp/portability-005/operator/turnN.stderr
```

No pipe. No `tee`. No `head`. The producer writes the complete envelope to disk
before any consumer reads. Standard streams are separated.

### Per-turn verification gate

After each turn, before any extraction step:

```bash
# 1. JSON must parse cleanly
jq empty /tmp/portability-005/operator/<file>.json

# 2. Capture size must exceed 1 KB
[ $(wc -c < /tmp/portability-005/operator/<file>.json) -gt 1024 ]

# 3. Capture size must NOT be a multiple of 8192 (the kernel pipe-buffer boundary
#    that 004 hit; a clean producer wouldn't truncate there)
bytes=$(wc -c < /tmp/portability-005/operator/<file>.json)
[ $((bytes % 8192)) -ne 0 ]

# 4. SHA-256 the capture
sha256sum /tmp/portability-005/operator/<file>.json
```

If any of these checks fails, **return BLOCKED**. Do not patch the capture inline.
Surface to operator and propose a protocol amendment.

### Fallback (only if shell redirect is incompatible with `--append-system-prompt-file`)

```bash
claude -p "..." \
  --model claude-sonnet-4-6 \
  --session-id <uuid> \
  --append-system-prompt-file /tmp/portability-005/target/system-prompt.txt \
  --allowedTools '' \
  --output-format stream-json \
  2>stderr | python3 -c "
import sys, json
with open('/tmp/portability-005/operator/reconstruction-raw.json', 'wb') as f:
    for chunk in sys.stdin.buffer:
        f.write(chunk)
"
```

`stream-json` mode emits one JSON object per line; the Python consumer reads the
entire stream into the file before exiting. No early-EOF SIGPIPE on the producer.

### Prohibited capture patterns (carry-overs from 004 that are not allowed in 005)

- `claude ... | tee FILE | head -c N` (any byte-count head consumer)
- `claude ... | less` (interactive pager that closes early)
- `claude ... | grep ... > FILE` (truncation may occur at first non-match)
- `timeout N claude ...` without explicit producer-aware handling

## Independence variable vs. replication 002

Same Phase A input class as 004: **transcript-only**. The 005 vs. 002 paired
comparison answers the agenda's open question on durability-package causal work
artifact-dependence for Amazing Birthday.

| | 002 | 004 (INDET.) | 005 |
|---|---|---|---|
| Phase A | artifact-only | transcript-only | transcript-only |
| Frozen source | c3692150 | c3692150 | c3692150 |
| Target model | claude-sonnet-4-6 | claude-sonnet-4-6 | claude-sonnet-4-6 |
| Withheld tests | (Nov 9 1989, Feb 29 1960, Jun 23 1956) | same | same |
| No-tools | `--allowedTools ''` | `--allowedTools ''` | `--allowedTools ''` |
| Capture discipline | clean (`tee` no head) | pipe-truncated | v0.2 shell-redirect or stream-json |

## Scope of this protocol change

Only the capture discipline changes. The scientific design — Phase A input, frozen
source commit, withheld tests, rubric, no-tools posture, no-repair rule — is held
identical to 004. Replication 002's comparator results stand as-frozen.

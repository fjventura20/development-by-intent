# BP-RO-ARTIFACT-ONLY-CLAUDE-001 — Results

**Disposition: BLOCKED — environment-state-loss failure.**

## What ran

- **R turn (reconstruction).** Target acknowledged Receipt Organizer behavior
  with a single READY line. All 3 substantive freeze-gate criteria passed.

## What did not run

- **T1–T5 tests** (5 preregistered behavioral tests against withheld test
  receipts and queries).
- **G turn** (mandatory generalization regression).

## Why

The host Claude Code 2.1.170 CLI cannot reliably deliver `--resume` calls to
sessions created via `--session-id` on this host. Three resume attempts failed
identically with `Error: No conversation found with session ID: ...` despite
the session file being on disk.

## Classification per protocol

- **Environment-state-loss failure** (NOT behavioral failure)
- Per the experiment protocol's environment-failure clause: "Try a different
  environment before concluding the baseline is unrecoverable."

## What this evidence supports

- The operator-side reconstruction prompt and prelude are correctly framed.
- The target model can read the RO durable package and acknowledge the
  Receipt Organizer behavior in a fresh conversation.

## What this evidence does NOT support

- Multi-turn stateful behavior (ledger persistence).
- Receipt extraction accuracy on any test receipt.
- Dedup, query answering, edge-case handling.
- Any claim about behavioral portability at the stateful tier.

## Ladder §5 status

**OPEN** — no PASS, no FAIL, no INDETERMINATE. A different environment
required to make any empirical claim at the stateful tier.

## v0.3 protocol amendment recommended

Add a session-resume pre-flight check immediately after the R turn. If the
first resume attempt fails, fall back to a different environment before any
tests run. Retrospective audit of AB replication 004, 005, 006 recommended
(the same bug may have affected them silently).

## Files in this directory

| File | Purpose |
|---|---|
| `environment.md` | Pre-flight SHA verification + target environment record |
| `artifact-record.md` | What the target received and what was withheld |
| `reconstruction-output.md` | The R-turn output (READY line, 50 bytes) |
| `reconstruction-stderr.txt` | Empty (R turn succeeded) |
| `test-1-output.md` | Empty (T1 did not run) |
| `test-1-stderr.txt` | Resume-failure error message |
| `failures.md` | Both R-turn size-calibration override and T-1.0 environment failure |
| `score-operator.md` | Operator scoring — R turn only |
| `interpretation.md` | Why classified as environment failure; ladder status |
| `hermes-manifest.json` | Machine-readable summary for ChatGPT independent review |

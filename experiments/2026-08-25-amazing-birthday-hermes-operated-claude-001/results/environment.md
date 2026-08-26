# Environment — Hermes-Operated Claude Portability 001

**Operator:** Hermes Agent (running in this Telegram session)
**Operator host:** Linux 7.0.0-28-generic, x86_64, user `fjventura20`
**Target provider:** Anthropic Claude via Claude Code CLI
**Target CLI version:** Claude Code 2.1.170
**Target model:** `claude-sonnet-4-6` (default for Claude Code print mode)
**Target session id:** `5681089b-b68b-46ba-a392-0291625a45f6`
**Wall-clock session span:** reconstruction freeze to last test = ~7 minutes total

## Isolation posture

- The target Claude session ran from a clean working directory `/tmp/portability-20260825/target/` containing **only the two allowed artifacts** (`03-behavioral-baseline.md` + `RECONSTRUCTION-PROMPT.md`).
- Both artifacts were inlined verbatim into the target's `--append-system-prompt` argument. The target therefore did not need to read them from disk and the operator did not expose any other files via `--add-dir`.
- The target was launched with `--allowedTools ''`, which denies all tools including Read, Write, Bash, WebFetch, and WebSearch. The target had no path to read any file outside the two inlined artifacts.
- The operator's own scratch (system-prompt file, session-id file, JSON captures) was kept at `/tmp/portability-20260825/operator/`, outside the target's cwd.
- At execution start the frozen source commit was not present locally; this was subsequently resolved and cross-verified as recorded in `artifact-record.md` and `failures.md`.

## Target session lifecycle

The target Claude session was opened once and reused for reconstruction and all three tests via `--resume`. The canonical successful session followed an OAuth refresh after initial stale-token failures. Approximate total inference cost was $0.24.

## Tool and permission envelope

- `claude -p '<prompt>'` print mode
- same session resumed for tests
- two allowed artifacts injected as system-prompt content
- `--allowedTools ''` on every turn
- `--output-format json`
- `--max-turns 1` for test turns
- `--max-budget-usd 0.50` per turn

The behavioral classification—not byte-identical prose—is the intended unit of reproducibility.

> Preservation note: this public copy is a compact transcription of the operator environment record. The SHA-bound operator package is identified in `hermes-manifest.json`; the full source record remains preserved in the coordination repository at transfer `20260825T234500Z-behavioral-portability-claude-result-001`.
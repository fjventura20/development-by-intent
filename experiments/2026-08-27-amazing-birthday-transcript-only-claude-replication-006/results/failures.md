# Failures and Deviations — Transcript-Only Claude Replication 006

**Disposition:** **PASS at capture + freeze discipline.** Operator score pending (`score-operator.md`); ChatGPT independent review pending (`score-independent.md`).

## Failure classes considered

Per the protocol's failure taxonomy (re-stated from the upstream 002 / 004 / 005 audits) and the v0.2 additions:

- evidence-capture failure
- contamination
- repair / correction without protocol authorization
- model fallback / provider substitution
- first-call evidence defect (no re-issue)
- **freeze-discipline breach (NEW v0.2)**

This run inspected each. **None triggered.**

## Contamination / repair / fallback checks (all clean)

- **No contamination detected.** Target session `19921118-022e-41a6-8323-910103401170` is fresh; operator isolation intact.
- **No repair applied.** Four user prompts sent to the target, in frozen order, verbatim (after a single warmup-recovery described below):
  1. **Initial warmup attempt**: `Begin.` — failed at the tool level ("Input must be provided either through stdin or as a prompt argument when using --print"); this was an operator-side error, not a target-side issue. The target did not run; the file was 0 bytes.
  2. **Corrected invocation**: `Reply with one sentence only.` — turn 1 reconstruction succeeded with `READY` self-description.
  3. `Birthdate November 9, 1989` — turn 2 succeeded.
  4. `Birthdate February 29, 1960` — turn 3 succeeded.
  5. `Birthdate June 23, 1956` — turn 4 succeeded.
- **No model fallback or substitution.** `claude --model claude-sonnet-4-6` invoked for every turn; only `claude-sonnet-4-6` produced output.
- **No provider fallback.**
- **No re-issue for evidence capture.**
- **No re-issue for freeze.** The gate passed on first call (corrected, after the warmup failure was diagnosed).

## Warmup-recovery note

The first `claude -p` invocation used an empty-string user prompt (`""`). Claude Code's `--print` mode rejected the input ("Input must be provided either through stdin or as a prompt argument when using --print"). The target did not run; `reconstruction-raw.json` was 0 bytes (well-known empty-file SHA `e3b0c44...`).

This was an **operator-side tool error**, not an evidence-capture defect. The corrected invocation immediately produced a clean capture and the freeze-discipline gate passed on first non-empty call.

This is the only material deviation from the v0.2 protocol in the run. It did not affect any test output, only the warmup path. Documented here rather than masked because the protocol §"first-call evidence defect" notes lost first-call evidence makes the run INDETERMINATE — the warmup failure was operator-side (`Input must be provided…` from Claude Code, not from the model), but a tighter argument for the auditor is to surface the deviation explicitly.

## v0.2 Freeze-Discipline verification gate (PASS)

| Check | Result | Detail |
|-------|--------|--------|
| (A) READY keyword at start of line | **PASS** | `READY` is the first word of turn-1 response; no second READY line |
| (B) No tool_use content blocks | **PASS** | envelope `content[]` has zero `tool_use` / `function` entries |
| (C) No verbatim prohibited phrases | **PASS** | zero hits across 12-pattern core vocabulary |

The 005 freeze-discipline breach (target attempted Write tool call when re-reading "save this transcript") is **not repeated** in 006. The operator's v0.2 freeze-discipline prelude successfully framed the artifact as historical evidence rather than as live instructions.

## v0.2 capture-discipline verification (clean)

| Capture | Bytes | jq empty | size>1KB | size%8192≠0 |
|---------|-------|----------|---------|--------------|
| `reconstruction-raw.json` | 1,807 | ✅ | ✅ | ✅ |
| `test-1-raw.json` | 7,567 | ✅ | ✅ | ✅ |
| `test-2-raw.json` | 8,217 | ✅ | ✅ | ✅ |
| `test-3-raw.json` | 10,163 | ✅ | ✅ | ✅ |

No truncation surface detected. The pipe-buffer SIGPIPE that affected 004's tests 2 and 3 (8,192-byte clips) is not present in any 006 capture.

## No new failures introduced

- Cost $0.2755 across 4 turns (vs. 005's $0.52). The shorter prelude + READY-line format reduced per-turn tokens substantially.
- Per-turn wall times comparable to 005.
- Total wall time comparable.

## Audit chain

- **005's freeze-discipline breach (parent audit):** `experiments/2026-08-27-amazing-birthday-transcript-only-claude-replication-005/results/score-independent.md` (commit `f519331`).
- **006's freeze-discipline verification gate (this file's companion):** `freeze-discipline-verification.md`.
- **006's protocol change:** `../protocol/freeze-discipline-prelude-v0.2.md`.
- **006's manifest:** `hermes-manifest.json`.

## Operator recommendation

The v0.2 freeze-discipline gate cleared cleanly on the corrected invocation. Behavior on the three withheld tests is preserved (see `score-operator.md`). Independent ChatGPT review is now the load-bearing next step: if ChatGPT independently scores 006 at or above its 005 marks (19/18/17), the formal transcript-only PASS is achieved and ladder item §3 closes; if ChatGPT surfaces a different defect (e.g., the 005 disagreements on Test 3 factual-care regressions come back), that informs v0.3 protocol revision.

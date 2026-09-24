# Failures and Deviations — Transcript-Only Claude Replication 005

**Disposition:** **PASS** — clean capture, all v0.2 gates passed, operator scores on visible content reach the v1.0 threshold on all three withheld tests, no material failures.

## Failure classes considered

The protocol's failure taxonomy (re-stated from the upstream 004 audit) includes:
- evidence-capture failure
- contamination
- repair / correction without protocol authorization
- model fallback / provider substitution
- first-call evidence defect (no re-issue)

This run inspected each. **None triggered.**

## Contamination / repair / fallback checks (all clean)

- **No contamination detected.** Target session `28a3e235-5490-4799-8eb1-27a17b85cae3` is fresh; operator isolation intact.
- **No repair applied.** Four user prompts sent to the target, in frozen order, verbatim:
  1. `Reconstruct the application per the system prompt. When you are ready, state that you are ready.`
  2. `Birthdate November 9, 1989`
  3. `Birthdate February 29, 1960`
  4. `Birthdate June 23, 1956`
- **No model fallback or substitution.** `claude --model claude-sonnet-4-6` invoked for every turn; only `claude-sonnet-4-6` produced token output (verified via `modelUsage` block in each capture).
- **No provider fallback.**
- **No re-issue for evidence capture.** All four raw captures landed on first call via the v0.2 shell-redirect capture method; per-turn gate passed for each.

## v0.2 capture-discipline verification (the whole point of this replication)

All four raw captures pass the v0.2 gate:

| Capture | Bytes | `jq empty` | size>1KB | size%8192≠0 | sha256 logged |
|---------|-------|-----------|---------|-------------|---------------|
| reconstruction-raw.json | 29,744 | ✅ | ✅ | ✅ (29744 = 3×8192 + 5168) | ✅ `caff4af6...` |
| test-1-raw.json | 7,486 | ✅ | ✅ | ✅ | ✅ `f40ac763...` |
| test-2-raw.json | 8,615 | ✅ | ✅ | ✅ (8615 = 1×8192 + 423) | ✅ `21cff2a5...` |
| test-3-raw.json | 8,689 | ✅ | ✅ | ✅ (8689 = 1×8192 + 497) | ✅ `a481c500...` |

The two captures that were byte-truncated in 004 (8,192 bytes exactly, no JSON parse) landed at **8,615 and 8,689 bytes** in 005, both **clearing** the v0.2 gate. The `head -c 200` consumer-induced SIGPIPE surface is eliminated; the shell-redirected capture writes the complete envelope to disk before any consumer reads.

## No new failures introduced

- Cost $0.5202 across 4 turns (vs $0.38 in 004). Reconstruction-turn cache creation accounts for the delta; per-turn test costs are within $0.01.
- Per-turn wall times: shorter than 004 in turn 1 (cache-warmup amortization); comparable in turns 2-4.
- Total wall time: comparable to 004.

## Audit chain

- **004's evidence defect (parent audit):** `experiments/2026-08-26-amazing-birthday-transcript-only-claude-004/results/failures.md`
- **005's protocol change:** `protocol/capture-discipline-v0.2.md`
- **005's run record (this file):** `failures.md`
- **005's manifest:** `hermes-manifest.json`

## Operator recommendation

The 004 → 005 closure is achieved: capture-discipline v0.2 produces clean first-call records, and the strong behavioral PASS signal from 004 is reproduced under v0.2 capture. Independent ChatGPT review is invited to convert the operator's PASS to a formally paired 005 ↔ 002 PASS for the transcript-only-vs-artifact-only comparison.

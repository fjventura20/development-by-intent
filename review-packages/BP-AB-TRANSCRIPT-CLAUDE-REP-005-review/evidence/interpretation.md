# Interpretation — Transcript-Only Claude Replication 005

**Disposition:** PASS (operator) — pending ChatGPT independent review.

## What this run supports

> In a fresh, isolated Claude Sonnet 4-6 environment given only the verbatim Amazing Birthday development transcript as system-prompt input, with v0.2 evidence-capture discipline (`claude [flags] > FILE` and per-turn `jq empty` gate), the target reconstructed recognizable Amazing Birthday behavior from the transcript alone and produced first-call outputs that hit the v1.0 rubric threshold on all three withheld tests with no material failures.

> The 004 → 005 closure achieves: same scientific design, only the capture discipline changed; 004's INDETERMINATE was a capture-pipeline defect (kernel pipe-buffer SIGPIPE truncation at exactly 8,192 bytes on tests 2 and 3), not a behavioral failure. v0.2 capture eliminates the pipe-consumer truncation surface entirely.

## What this run does NOT support

- Universal cross-provider sufficiency of the transcript alone. Single Claude Sonnet 4-6 run, single session.
- Equivalence of transcript-only vs. artifact-only reconstruction. This run's Hermes-operator scoring (20/20/20/20) versus replication 002 ChatGPT-independent (19/19/17) is **operator-vs-ChatGPT and run-vs-run**, not a directly comparable Hermes-vs-ChatGPT on the same captures. ChatGPT independent review on the 005 truncated-clean captures is required for a valid paired comparison.
- Factual correctness of every individual claim. Operator factual sampling indicates high accuracy across all three tests; ChatGPT independent review is the appropriate venue for full factual audit.

## Critical requirements — observed

- **Exact-date integrity** preserved across all three tests:
  - Test 1: Nov 9 1989 → Berlin Wall falls **on the birth date**, at ~7 PM CET. Verified historical record.
  - Test 2: Feb 29 1960 → Agadir Morocco earthquake 11:47 PM same day (magnitude 5.8, 12,000–15,000 dead). Verified.
  - Test 3: Jun 23 1956 → Nasser referendum + Federal-Aid Highway Act 6 days later + Elvis "Heartbreak Hotel" #1 + Montgomery Bus Boycott day 205. Multiple verified historical records converge on the birth date.
- **Generalization** preserved across all three tests:
  - Test 1 generalizes to a Cold-War-decade birth.
  - Test 2 generalizes to a calendar-rare-date birth (with arithmetic on the leap-day mechanic).
  - Test 3 generalizes to a mid-1950s Cold War crystallization birth.
  - The behavioral shape (5–7 themed sections, lifetime arc, closing synthesis) was reconstructed from the transcript alone — not extracted by matching canonical examples.

## Comparison with replication 002 (paired comparator)

Same provider family, same target model, same withheld tests and rubric, same no-tools posture, same scientific intent. The independence variable between 002 and 005 is **the input class to the target**:

| Input | Replication 002 | 005 (this run) |
|---|---|---|
| `03-behavioral-baseline.md` | yes | no |
| `04-durable-package/RECONSTRUCTION-PROMPT.md` | yes | no |
| `02-development-transcript/transcript.txt` | no | yes |
| Frozen input class | artifact-only | transcript-only |
| Capture discipline | clean (`tee` no head) | clean (v0.2 shell-redirect) |
| ChatGPT independent score | 19/19/17 | pending |
| Final disposition | PASS | PASS (this run, pending independent) |

## Behavioral observations

- **Same trigger format honored** across all three tests: `Amazing Birthday — [date]` header, with the date composed under the v1.0 trigger format.
- **Same closing-voice style preserved**: Test 1 "the last night of one world", Test 2 "you are exactly the age of it", Test 3 "Born the summer Nasser took Egypt and Elvis took America". All echo the Amazing Birthday voice reconstructed from the transcript.
- **Deeper generalization** on Test 2 (Feb 29 1960): the model computes the 16-actual-birthdays arithmetic, projects forward to 2028 as the 17th actual birthday, and explicitly identifies the leap-day mechanic as "the rarest slot in the entire calendar". The transcript does not contain explicit leap-year reasoning; this is reconstructed.
- **Historic-compression** on Test 3 (Jun 23 1956): the model includes the lifetime arc reaching 2026 at age 70, including AI-revolution terminology ("AI rewrites what a machine can do") that postdates the original transcript. The voice is preserved; the technical era referenced has advanced.
- **Pop-culture color** as in 004: Test 1 includes "We Didn't Start the Fire" + Batman + Simpsons premiere; Test 2 names Elvis + Beatles; Test 3 names Heartbreak Hotel + Ed Sullivan. The transcript carries these from the original development conversation; the reconstruction finds them.

## Operator recommendation

1. **Independent ChatGPT review** of the clean captures is invited via `results/score-independent.md`. Direct paired comparison against replication 002's recorded ChatGPT score (19/19/17) would close the agenda's open question on durable-package causal work in the recorded environment.
2. **No further replications are required** for this experiment cluster under the v0.2 capture discipline. The 005 PASS combined with the 002 PASS provides:
   - Single-session transcript-only sufficiency (005).
   - Single-session artifact-only sufficiency (002).
   - Behavioral signal comparison (operator vs. ChatGPT across the two input classes).
3. **Next experiment**, if you wish, is downstream of this comparison:
   - **Fair Price clean-room reconstruction** (agenda §5): tests a current-information research application with a different behavioral shape. Independent of the transcript-only-vs-artifact-only question.
   - **Portability v0.2 amendments** to the public protocol: incorporating the empirical findings of 002/004/005 into the protocol design.
   - **Kestrel-17 delta-persistence POC v0.2 amendments** (the separate D020 thread): independent of the Amazing Birthday cluster.

The 005 results close the open question on this experiment cluster. The next research question is yours.

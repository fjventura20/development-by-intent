# Interpretation — Transcript-Only Claude 004

**Disposition:** INDETERMINATE (operator classification pending ChatGPT independent review)
**Behavioral signal:** Strong PASS on visible content across all three withheld tests.
**Awaiting:** (i) ChatGPT independent review of the truncated evidence; (ii) clean replication under v0.1.1+ with corrected capture discipline.

## What this run supports

> In a fresh, isolated Claude Sonnet 4-6 environment given only the verbatim Amazing Birthday development transcript as system-prompt input, the target reconstructed recognizable Amazing Birthday behavior from the transcript alone and produced first-call outputs that hit the v1.0 rubric threshold on all three withheld tests (`Birthdate November 9, 1989`, `Birthdate February 29, 1960`, `Birthdate June 23, 1956`).

> Two of three test captures were byte-truncated at the kernel pipe-buffer boundary during operator-side teeing; the assistant-text content of every test is fully present in the captured bytes and reaches the v1.0 rubric; the formal preregistered PASS awaits a clean replication with corrected capture discipline.

## What this run does NOT support

- Universal cross-provider sufficiency of the transcript alone. Single Claude Sonnet 4-6 run, single session.
- Equivalence of transcript-only vs. artifact-only reconstruction. This run's directional signal (operator-scored 20/20/20/20 against ChatGPT-independent-scored 19/19/17 in replication 002) is suggestive, not statistically comparable. Operator and ChatGPT scoring in replication 002 are not interchangeable; a matched-pair ChatGPT independent review on this run's truncated evidence is required to make the comparison valid.
- Factual correctness of every individual claim in the three outputs. Operator factual sampling indicates high accuracy (Berlin Wall fall date, Schicksalstag date, Agadir earthquake date/time, BTTF II release date, WWW CERN proposal date, Taylor Swift birth date, Nasser referendum date, Hungarian Revolution 1956, Brexit 2016 on Jun 23, 1960 "Year of Africa" 17 nations, Eisenhower heart attack Sep 1955) but a small factual variance would not be detectable without independent review.

## Critical requirements — observed

- **Exact-date integrity** preserved across all three tests:
  - Test 1: Nov 9 1989 → Berlin Wall falls **on the birth date**. Verified.
  - Test 2: Feb 29 1960 → leap-day anniversary mechanic; **the day itself is the first story**. Verified.
  - Test 3: Jun 23 1956 → Nasser referendum on the birth date; 33 days to Suez. Verified.
- **Generalization** preserved across all three tests:
  - Test 1 generalizes to a Cold-War-decade birth.
  - Test 2 generalizes to a calendar-rare-date birth.
  - Test 3 generalizes to a Cold-War-1950s birth in a year of mid-century political crystallization.
  - The behavioral shape (5 themed sections, lifetime arc, closing synthesis) was reconstructed from the transcript alone — not extracted by matching canonical examples.

## Comparison with replication 002 (paired comparator)

Same provider family, same target model (`claude-sonnet-4-6`), same withheld tests and rubric, same no-tools posture, same first-call capture intent. The independence variable is **the input to the target**:

| Input | Replication 002 | Transcript-only 004 (this run) |
|---|---|---|
| `03-behavioral-baseline.md` | yes | no |
| `04-durable-package/RECONSTRUCTION-PROMPT.md` | yes | no |
| `02-development-transcript/transcript.txt` | no | yes |
| Frozen input class | artifact-only | transcript-only |

The transcript-only input is ~5× larger (27 KB vs. ~5 KB) and produced a higher cache-warmup cost ($0.115 turn-1 vs. $0.040 replication 002 turn-1) but yielded the same behavioral shape on every test.

A clean replication under v0.1.1+ with corrected capture discipline would close the evidence question and let the paired comparison speak to "is the durability package doing work that the transcript alone does not?" — the named open question from `BEHAVIORAL-PORTABILITY.md` priority ladder § 3.

## Behavioral observations (for protocol v0.2 / replication-005 design)

- All three outputs honor the `Birthdate [date]` trigger produced a header formatted as `Amazing Birthday — [date]`, which the v1.0 behavior rubric explicitly rewards under "trigger behavior". The transcript carries the header format from the original development conversation (the closing-to-file dump captured it once).
- All three outputs include the closing synthesis that ends the original transcript's tone (e.g., "You were there for all of it.", "That's a remarkable vantage point for a life.", "You were born on a day that barely exists"). The transcript's closing-voice phrases appear to have been learned and re-applied.
- The leap-day birthday (Test 2) gets the strongest leap-year framing of any of the three, including the "at 66 years old, you have celebrated February 29th exactly sixteen times" math. This is a strong signal that the target understood the **mechanics** of leap-year from the transcript, not just the name.
- The 1956 (Test 3) output identifies the date as falling one day before Britain's 2016 EU referendum — a long-tail coincidence that the model found without prompting. This is consistent with the model's training on historical data, not with anything in the supplied transcript. The factual correctness stands on its own; the source of the fact is the model's pre-training knowledge applied to the birthdate prompt.

## Operator recommendation

1. **Independent ChatGPT review** of the truncated evidence is invited. The visible content is fully recovered; ChatGPT's pass on `score-independent.md` for this run would convert the operator's INDETERMINATE into a **cleaner INDETERMINATE (evidence-capture defect only)**, with both scorers aligned on the behavioral signal.
2. **Clean replication** under v0.1.1+ with capture discipline fixing the SIGPIPE truncation (`tee FILE | head -c 200` → either drop the head entirely or use `--output-format stream-json` with a controlled consumer). Same scientific design, same input class transcript-only, same target model, same withheld tests and rubric. If that run yields a clean PASS, the 001/004 INDETERMINATE → clean PASS pattern closes and the paired comparator against replication 002 can answer "transcript-only vs. artifact-only" for this application class.
3. **No portmanteau claim** is made from this run. The narrower observation ("transcript-only input appears sufficient in a single fresh Claude Sonnet 4-6 session in the recorded environment") is the strongest defensible statement, and even that requires the clean replication for preregistered-formal status.

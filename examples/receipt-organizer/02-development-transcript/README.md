# 02 — Development Transcript

This directory contains the canonical word-for-word Receipt Organizer development
transcript.

## Authoritative source

- **Committed transcript:** [`receipt_organizer_transcript.txt`](receipt_organizer_transcript.txt)
- **Preserved/imported:** 2026-08-27
- **Source type:** plain UTF-8 text
- **Substantive editing:** none
- **Formatting normalization:** none; user-side turns are wrapped in `text` code
  fences to preserve exact whitespace; assistant-side turns are reproduced verbatim.
- **Non-content metadata removed:** none.
- **SHA-256:** `16651893e987456acaf15cd7ddfbdd146b2277d4ed4533c7a714894e93537ea8`
- **Byte length:** 11,457 bytes
- **Turn count:** 8 user + 8 assistant = 16 turns
- **Target model:** claude-sonnet-4-6 via Claude Code 2.1.170 CLI
- **Session ID:** `fc8a2bd0-30d5-4e94-acfd-7a15b1f2b7de` (fresh session, `--allowedTools ''`)

The checksum above identifies the preserved transcript content used as the source for
this canonical example.

## Provenance rule

This transcript records a **simulated operator-driven development session**. The
user-side turns are prompts drafted by Hermes acting as a development driver (matching
the role Frank plays in real DbI development sessions). The AI-side turns are real,
verbatim Claude Code outputs produced by a live model invocation against those prompts
as input.

Only the preserved verbatim transcript is original development evidence. Do **not**
reconstruct missing turns from memory, summaries, later articles, behavioral
specifications, or this repository's documentation and present them as historical
evidence.

## What the transcript establishes

The transcript records the application emerging through ordinary conversation:

1. an initial intent describing the application and a first receipt to test on;
2. a course-correction that redirects from "write Python files" to "act as the
   Receipt Organizer conversationally in this session" — this is the load-bearing
   development moment that pins the behavior as a conversational application rather
   than an implementation-deployable artifact;
3. a second receipt (Shell gas station) processed with date-format normalization
   (08/22/2026 → 2026-08-22) and unit-price × quantity computation;
4. a duplicate-detection test (same Shell receipt pasted again) — confirmed
   duplicate on merchant + date + total;
5. a third receipt (Olive Garden) processed, with tip-handling acknowledged as a
   known edge case;
6. a three-query test exercising all three query shapes from the original intent
   (merchant+time-window, category aggregate, threshold filter);
7. a behavioral pinning step establishing the receipt-paste vs. spending-question vs.
   general-chat classification;
8. a durability-spec generation step where the AI summarizes its own behavior into a
   short paragraph suitable for hand-off to a fresh session.

The turn-8 assistant output is the natural source for the durability package — see
[`../04-durable-package/RECONSTRUCTION-PROMPT.md`](../04-durable-package/RECONSTRUCTION-PROMPT.md).

## Receipts used during development (NOT withheld; used to develop the behavior)

| Date | Merchant | Category | Total |
|---|---|---|---|
| 2026-08-15 | Meijer | Grocery | $13.63 |
| 2026-08-19 | Olive Garden | Restaurant | $74.44 |
| 2026-08-22 | Shell Gas Station | Gas | $42.39 |

These three receipts constitute the development corpus. They are intentionally NOT
used as the test set; the test set (frozen v1.0) uses different merchants, dates, and
shapes, available in [`../tests/behavioral-tests.md`](../tests/behavioral-tests.md).
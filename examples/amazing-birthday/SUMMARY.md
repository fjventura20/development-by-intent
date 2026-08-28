# Amazing Birthday — What This Experiment Proves

A short, plain-language summary of the Amazing Birthday worked example and what the
preserved evidence supports. Detailed evidence lives in the linked files; this document
is the entry point for someone who wants the bottom line first.

## The application in one sentence

Given a birthdate, Amazing Birthday produces an engaging historical birthday story —
selecting roughly 5–10 meaningful connections, distinguishing exact-date events from
nearby context, and weaving the material into the arc of the person's lifetime — invoked
with a short trigger such as `Birthdate June 23, 1956`.

## What it is evidence for

The Amazing Birthday example is the first canonical specimen for the **Behavioral
Portability** claim of Development by Intent: the functional behavior of an
AI-developed application can be preserved in a small, human-readable artifact set and
recovered in a fresh AI environment without the original implementation or development
context.

This is a narrower claim than "AI can write good birthday reports." It is also narrower
than "the same prompt reproduces the same output." It is specifically about whether:

1. a conversational application has **stable behavioral identity** that can be named,
   preserved, and inspected;
2. that identity can be expressed in a **durable artifact set** independent of the
   environment that produced it;
3. a fresh environment receiving only that artifact set can **recover the same
   application behavior** on inputs it was not built around.

## What the evidence demonstrates

Seven reconstruction experiments have been run against the canonical Amazing Birthday
artifact set. Their preserved raw outputs, frozen source commits, and scoring are
publicly auditable:

| Experiment | Mode | Provider | Model | Operator score | Independent score | Verdict |
| --- | --- | --- | --- | --- | --- | --- |
| clean-room-001 | artifact-only | ChatGPT | GPT-class | 20 / 20 / 20 | 60 / 60 | **PASS** |
| grok-reconstruction-001 | observational | Grok | — | (factual regression not independently verified) | — | preliminary |
| hermes-operated-claude-001 | artifact-only | Claude | claude-sonnet-4-6 | 19 / 20+ repair-defect | 18 / 17 | INDETERMINATE |
| hermes-operated-claude-002 | artifact-only | Claude | claude-sonnet-4-6 | clean replication | 19 / 19 / 17 | **PASS** |
| hermes-operated-gemini-003 | artifact-only | Gemini | — | — | — | BLOCKED (no CLI on host) |
| transcript-only-claude-004 | transcript-only | Claude | claude-sonnet-4-6 | 20 / 20 / 20 | (ChatGPT review pending) | operator PASS |
| transcript-only-claude-replication-005 | transcript-only v0.2 capture | Claude | claude-sonnet-4-6 | clean capture | (ChatGPT review pending) | operator PASS |
| transcript-only-claude-replication-006 | transcript-only v0.2 freeze-discipline | Claude | claude-sonnet-4-6 | 20 / 20 / 20 / 20 | (ChatGPT review pending) | operator PASS |

Direct links to the preserved evidence for each experiment are in
[`RESULTS-INDEX.md`](RESULTS-INDEX.md).

## What the evidence does not yet prove

- **Implementation freedom.** All four PASS runs used a similar artifact-only flow; none
  deliberately varied language, framework, database, or UI technology. The
  implementation-freedom experiment (item 5 on the research agenda) is not yet run.
- **Stateful data.** Amazing Birthday is a stateless conversational application. The
  Receipt Organizer experiment is the next specimen and is the first serious test of
  persistent structured data, deduplication, and reasoning over accumulated records.
- **Multiple model variance under one protocol.** Variance evidence is thin — the
  experiments establish feasibility, not statistical reliability.

## What a reader should look at next

- To **understand the method**, start with [`TUTORIAL.md`](TUTORIAL.md).
- To **inspect the original development record**, read
  [`02-development-transcript/amazing_birthday_transcript.txt`](02-development-transcript/amazing_birthday_transcript.txt)
  (SHA-256 `d14bf4ba…f101a63374`).
- To **see the durable artifact set**, read
  [`03-behavioral-baseline.md`](03-behavioral-baseline.md),
  [`04-durable-package/RECONSTRUCTION-PROMPT.md`](04-durable-package/RECONSTRUCTION-PROMPT.md),
  and [`tests/behavioral-tests.md`](tests/behavioral-tests.md) (frozen v1.0).
- To **audit any reconstruction result**, follow [`RESULTS-INDEX.md`](RESULTS-INDEX.md).
- To **understand how the experiment should be reproduced**, read
  [`docs/experiment-protocol.md`](../../docs/experiment-protocol.md) and
  [`05-reconstruction/README.md`](05-reconstruction/README.md).

## Provenance

This document is a public-facing summary, not original historical evidence. It was
authored 2026-08-27 against the repository at the time of writing. It does not modify
the preserved transcript or behavioral baseline. If any result, claim, or scoring in
this summary disagrees with the underlying experiment evidence, the underlying evidence
is authoritative.
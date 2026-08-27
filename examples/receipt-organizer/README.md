# Receipt Organizer — Canonical Worked Example

> **This application was developed through conversation, not from a conventional
> implementation specification.**

Receipt Organizer is the second canonical worked example for Development by Intent
(DbI). It is intentionally more demanding than Amazing Birthday: it is **stateful
and data-producing**, with a persistent ledger, deduplication, and natural-language
reasoning over accumulated records.

The purpose of this example is not to showcase a receipt organizer. It is to test
whether the behavioral portability claim that survived Amazing Birthday also holds
for a substantially harder application.

## What this example demonstrates

The lifecycle under test is the same as Amazing Birthday:

`Intent → Conversation → Behavioral Refinement → Preservation → Isolation →
Reconstruction → New-Input Validation → Continued Evolution`

But each step is more demanding:

- the application is **stateful** — the ledger accumulates across turns;
- **deduplication** is part of the contract, not an implementation detail;
- **natural-language queries** must reason over the accumulated records;
- **edge cases** (tips, missing fields, date ambiguity) must be handled gracefully
  without corrupting the ledger.

## Evidence model

The example deliberately separates three classes of material:

1. **Original evidence** — verbatim development conversation and any preserved
   artifacts actually produced during the historical experiment.
2. **Derived artifacts** — behavioral baselines, test criteria, and explanatory
   documents created from the original evidence.
3. **Public reproduction artifacts** — instructions and packages created to let an
   independent developer repeat the experiment today.

A recreated artifact must never be labeled as an original historical artifact.

## Provenance note

The verbatim transcript in `02-development-transcript/` records a **simulated
operator-driven development session**: the user-side turns were drafted by Hermes
acting as a development driver (matching Frank's role in real DbI sessions), and the
AI-side turns are real, verbatim outputs produced by a live Claude Code invocation.
This is the same provenance model used by the Amazing Birthday example: what matters
is the recorded conversation and the behavior it pinned, not the developer's identity.

## Directory map

```text
receipt-organizer/
├── README.md
├── 01-original-intent.md
├── 02-development-transcript/
│   ├── README.md
│   └── receipt_organizer_transcript.txt   # canonical, SHA-256 in README
├── 03-behavioral-baseline.md             # frozen behavioral contract (v1.0)
├── 04-durable-package/
│   ├── README.md
│   └── RECONSTRUCTION-PROMPT.md
├── 05-reconstruction/
│   └── README.md                         # isolation / freeze / test / score procedure
├── 06-validation.md                      # scoring rubric (v1.0 frozen)
├── tests/
│   └── behavioral-tests.md               # withheld/new-input tests (v1.0 frozen)
└── results/
    └── README.md                         # result-layout spec; actual results in experiments/
```

**Note on `results/`:** the actual reconstruction evidence (raw outputs, scoring,
ledger snapshots, environment records) will live under `experiments/` at the
repository root once a reconstruction experiment is run, mirroring the Amazing
Birthday pattern.

## The application

Receipt Organizer accepts a receipt (multi-line text containing a merchant name
and dollar amounts) and:

- extracts merchant, date (normalized to ISO YYYY-MM-DD), line items, subtotal,
  tax, total, and payment method;
- classifies the receipt (grocery, restaurant, gas, pharmacy, travel, retail, or
  other);
- deduplicates against the running ledger (matching merchant + date + total);
- maintains a session ledger of stored receipts;
- answers natural-language spending queries by filtering, summing, or listing from
  the ledger.

Input classification: if the input looks like a receipt, ingest; if it's a natural-
language spending question, answer from the ledger; otherwise, treat as normal
conversation.

## Reproduce the experiment

Use the repository-wide `docs/experiment-protocol.md`, then follow
`05-reconstruction/README.md`.

The most important rules are isolation (the reconstructing environment receives
only the artifact set declared for the experiment) and **state retention** (the
ledger must persist across turns within the same conversation — a state-loss
failure is an environment failure, not a behavioral failure).

Then run the frozen v1.0 withheld/new-input tests in `tests/behavioral-tests.md`
and score the result using `06-validation.md`.

## Current publication status

The canonical development transcript is preserved (SHA-256
`16651893…53537ea8`). The behavioral baseline is frozen as v1.0 from the
transcript. The first public withheld test set is frozen as v1.0 using merchants,
dates, and shapes that do not appear in the development record. The example is
ready for an independent clean-room reproduction run.

## What this example is NOT yet evidence for

- **Image-input handling.** Plain-text receipts only in v1.0; image input is a
  flagged future extension.
- **Cross-session persistence.** Development pinned ledger-within-session
  behavior; cross-session durability is a separate question for a separate
  experiment.
- **Implementation freedom.** Initial reconstruction experiments will use the
  same conversational mechanism as the development session; deliberate variation
  of implementation mechanism is a separate experiment (per the research agenda
  item "implementation freedom").
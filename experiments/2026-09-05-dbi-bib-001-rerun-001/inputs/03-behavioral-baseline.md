# 03 — Behavioral Baseline

This document defines the recognizable behavior of the Amazing Birthday application for reconstruction and regression testing. It is a derived artifact, not a verbatim transcript.

## Trigger

Primary:

```text
Birthdate [date including year]
```

Alternate:

```text
Amazing Birthday [date including year]
```

## Behavioral contract

For a supplied birthdate, the application should:

1. Open by placing the reader in the historical world of the exact day. Include the day of week when useful.
2. Select roughly **5–10 standout connections**, rather than attempting an exhaustive chronology.
3. Strongly prefer exact-date events when they are genuinely interesting.
4. Use nearby events only when they illuminate the world the person was born into, and clearly identify their temporal relationship to the birthdate.
5. Favor connections that are surprising, historically meaningful, culturally important, technologically significant, or personally resonant.
6. Explain **why each selected connection matters**. A list of names and dates is insufficient.
7. Connect the birthdate repeatedly to the arc of the person's lifetime.
8. Include a substantive lifetime perspective covering major political, cultural, scientific, communications, or technological change where appropriate.
9. End with a synthesis of what kind of world the person entered and how dramatically that world changed during the lifetime that followed.
10. Maintain a warm, vivid, engaging narrative voice without turning the result into unsupported sentimentality.

## Factual discipline

The application must distinguish among:

- events that occurred on the exact birthdate;
- anniversaries tied exactly to that date;
- events shortly before or after the date;
- broader historical context.

Nearby events must never be represented as exact-date events.

When current-age or elapsed-time calculations are included, they must be calculated relative to the actual execution date and should not be treated as permanent historical facts.

## Selection discipline

The application is intentionally selective.

A successful result should feel curated. It should omit weak trivia even when that trivia is technically associated with the date. More facts do not imply a better result.

The preferred ordering is by narrative value, not by database category.

## What is not required

The application does not require:

- a fixed heading template;
- exactly the same number of sections on every run;
- identical prose across executions;
- identical event selection when several comparably strong choices exist;
- astrology or birthstone material in every report;
- a conventional software implementation beneath the conversational interface.

## Failure conditions

A reconstruction materially fails the baseline if it:

- produces an exhaustive or near-exhaustive event dump;
- presents nearby events as if they happened on the exact date;
- lists facts without explaining significance;
- loses the lifetime/historical-arc framing;
- merely reproduces memorized examples instead of generalizing to a new date;
- requires the user to restate the full behavioral instructions for every invocation.

## Identity criterion

Amazing Birthday is considered behaviorally reconstructed when a fresh environment can receive the trigger and generate a new-date result that preserves the core selection, exact-date discipline, explanatory judgment, narrative structure, and lifetime framing above.

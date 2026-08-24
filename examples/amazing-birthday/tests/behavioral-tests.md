# Amazing Birthday — Behavioral Tests

These tests are intended to determine whether the reconstructed application preserves behavior rather than merely replaying a development example.

## Test-set status

**Frozen test set: v1.0 — 2026-08-24**

The authoritative development transcript was checked before freezing these dates. The transcript's demonstrated birthdates are:

- December 7, 1951
- February 20, 1952
- August 24, 1931

None of the three fixed test dates below appears in the development transcript. They are therefore suitable as withheld/new-input tests for the first public scored reconstruction run.

Do not change these dates after observing a reconstruction result. Any future test-set revision should receive a new version and preserve the prior results.

## Test 1 — Strong exact-date anchor

Input:

```text
Birthdate November 9, 1989
```

Purpose:

Tests whether the application recognizes a historically dominant exact-date event without collapsing the entire report into a single event or an exhaustive list.

Expected behavioral properties:

- exact-date events are labeled accurately;
- a small curated set of additional connections provides context;
- significance is explained;
- the report connects the birthdate to the lifetime that follows;
- the result remains a narrative, not a chronology dump.

## Test 2 — Leap-day edge case

Input:

```text
Birthdate February 29, 1960
```

Purpose:

Tests date handling and whether the application can build a meaningful story around a less conventional birthday without resorting to filler.

Expected behavioral properties:

- the date is handled correctly as a valid leap-day birthdate;
- weak trivia is not used merely to fill space;
- nearby historical context is clearly distinguished from exact-date events;
- the report still provides a meaningful lifetime arc.

## Test 3 — No obvious headline supplied by the prompt

Input:

```text
Birthdate June 23, 1956
```

Purpose:

Tests research, judgment, and selectivity when the date does not itself cue a universally obvious event to the evaluator.

Expected behavioral properties:

- the application researches rather than hallucinating an artificial "famous" connection;
- exact-date and nearby material are clearly separated;
- the selected connections are meaningful enough to justify inclusion;
- the closing synthesis places the date within a larger historical/technological transition.

## Trigger regression

After a successful reconstruction, start a new normal invocation in the same reconstructed environment using only:

```text
Birthdate [another date]
```

The application should execute without the user restating the behavioral baseline.

## Scoring

Score every raw output using `../06-validation.md` before conversationally repairing the reconstructed application.

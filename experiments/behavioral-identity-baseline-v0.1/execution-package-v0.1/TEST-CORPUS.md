# DBI-BIB-001 — Exact Test Corpus

**Version:** v0.1  
**Status:** FROZEN WITH EXECUTION PACKAGE  
**Encoding:** UTF-8  
**Prompt payload rule:** The text between backticks below is the complete prompt payload. Send it without a leading or trailing newline and without additional instruction text.

## Test order

The five prompts are executed in the exact order T1 → T2 → T3 → T4 → T5 for Block A, then the same order T1 → T2 → T3 → T4 → T5 for Block B.

Each reconstruction therefore produces 10 test outputs. Across R1–R6, expected total = 60 outputs.

### T1 — Ordinary historical date

Exact payload:

`Birthdate February 20, 1952`

SHA-256 of exact UTF-8 payload bytes:

`75302f1fce9bc33f64b9c0a9a47863f5362e54c9ce1e40ce3ce4831866e5598b`

Purpose: normal operating behavior, selection quality, and narrative construction.

### T2 — Difficult / low-cue date

Exact payload:

`Birthdate June 23, 1956`

SHA-256:

`58170a11a454717de4409ccbe836deeb7c30b23e308a237d1a9f406302744712`

Purpose: judgment and selectivity when the prompt itself does not supply an obvious headline event.

### T3 — Leap-day edge case

Exact payload:

`Birthdate February 29, 1960`

SHA-256:

`52fb3fa1d282a1607e455586c365134c574ad018d36897fba5bcbf2909d67ca8`

Purpose: uncommon-date handling, exact-date discipline, and resistance to filler.

### T4 — Strong modern exact-date anchor

Exact payload:

`Birthdate November 9, 1989`

SHA-256:

`a8ad9dcbb99fcf8df4c66449f5b6118ec65063217588c7857378d984fe8cf7fe`

Purpose: prioritization and selectivity in a historically rich event environment.

### T5 — Previously characterized acceptance-floor case

Exact payload:

`Birthdate August 24, 1931`

SHA-256:

`c1786d3ad2454208996a7313d92efaf13a1f1ed65f28002a7ee4beb314829b44`

Purpose: provide continuity with a previously characterized Amazing Birthday case while evaluating current reconstruction identity.

## Repetition structure

For each reconstruction Rn:

1. complete reconstruction and freeze the session state;
2. execute Block A: T1, T2, T3, T4, T5;
3. execute Block B in the same session: T1, T2, T3, T4, T5;
4. do not repair, explain, summarize, reset, hint, or otherwise intervene between prompts.

Block B is a standardized repeated-corpus measurement in the same reconstructed conversational environment. It is **not** claimed to be a stateless duplicate. Any context effect created by Block A is part of the measured within-reconstruction execution variance and must be preserved identically across R1–R6.

## Prompt integrity

Before each test call, the operator must compute SHA-256 over the exact prompt bytes and compare it with this file. A mismatch is a deviation; the incorrect attempt remains evidence and must not be silently replaced.

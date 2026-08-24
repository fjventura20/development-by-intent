# 06 — Validation and Scoring

Amazing Birthday should be evaluated for **functional behavioral reconstruction**, not byte-for-byte output identity.

## Critical requirements

The following are critical. Failure of either is an overall FAIL regardless of total score:

1. **Exact-date integrity** — nearby events are not represented as events that happened on the birthdate.
2. **Generalization** — the application can produce a valid result for a date not used as a development example.

## Scored dimensions

Score each dimension 0, 1, or 2:

- **0 — absent or materially wrong**
- **1 — recognizable but incomplete/inconsistent**
- **2 — clearly satisfies the baseline**

| Dimension | What to look for |
|---|---|
| Historical opening | Places the reader in the world of the date rather than starting as a database dump |
| Selectivity | Curates roughly 5–10 strong connections and omits weak filler |
| Exact-date discipline | Clearly distinguishes exact-date facts from nearby context |
| Significance | Explains why selected facts matter |
| Narrative coherence | Reads as a connected birthday story, not unrelated snippets |
| Lifetime framing | Connects the birth moment to changes across the person's lifetime |
| Breadth | Uses meaningful political, cultural, scientific, communications, or technological context where appropriate |
| Factual care | Avoids unsupported certainty and obvious date/fact errors |
| Ending synthesis | Concludes with a meaningful statement about the world entered and how it changed |
| Trigger behavior | Works from the short application trigger without requiring the full specification again |

Maximum score: **20**.

## Classification

- **PASS** — 17–20, with both critical requirements satisfied
- **PARTIAL** — 12–16, with both critical requirements satisfied
- **FAIL** — 0–11, or failure of a critical requirement
- **INDETERMINATE** — evidence is insufficient to score reliably

These thresholds are an initial public rubric and should be versioned. Do not change them after observing a run and then rescore that same run as if the new rubric had been predeclared.

## Historical result vs independent reproduction

The original Amazing Birthday work established an observed end-to-end demonstration: the application was preserved, reconstructed in an isolated project, and exercised with a different date while retaining the intended behavioral pattern.

That historical success is **not the same as independent replication**. Public reproduction results belong under `results/` and should record the exact repository commit, environment, inputs, raw outputs, evaluator, and score.

## Stronger evidence

The project becomes substantially more convincing when:

- another person reproduces the result;
- the test is repeated on another model/provider;
- multiple runs expose variance rather than reporting a single favorable output;
- artifact-removal experiments identify which preserved materials are actually necessary.

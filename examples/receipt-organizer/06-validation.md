# 06 — Validation and Scoring

Receipt Organizer should be evaluated for **functional behavioral reconstruction**,
not byte-for-byte output identity. Each test exercises a single behavioral surface;
each surface has its own rubric.

## Critical requirements (per test)

The following are critical. Failure of any one is a **test-level FAIL** regardless of
total score.

| Test | Critical requirement |
|---|---|
| Test 1 (Pharmacy receipt) | Date is parsed and normalized to ISO YYYY-MM-DD; total is canonical even when subtotal/tax are present. |
| Test 2 (Restaurant with tip-outside-total) | Printed total is recorded as canonical; tip is acknowledged as edge case, not silently folded into the total. |
| Test 3 (Threshold query after multi-ingestion) | Threshold query returns ONLY receipts strictly over $50; receipts at exactly $50 are excluded unless the natural-language query phrasing makes the boundary explicit. |
| Test 4 (Duplicate detection on re-entry) | Re-pasting a previously-stored receipt is detected as duplicate; ledger is unchanged; user is told which record matched. |
| Test 5 (Category aggregate over time) | Category aggregate over the full ingested corpus returns the correct sum and names contributing receipts. |

## Per-test scoring (each test 0–4)

| Score | Meaning |
|---|---|
| 0 | Absent or materially wrong on the critical requirement |
| 1 | Recognizable but materially incomplete or inconsistent |
| 2 | Critical requirement met; visible behavior substantially matches baseline |
| 3 | All required fields correct; minor presentation issues |
| 4 | Clean extraction, classification, ledger update, and (where relevant) query answer with no defects |

Maximum score per test: **4**. Maximum score across all 5 tests: **20**.

## Classification (per test)

- **PASS** — score 3 or 4, with the critical requirement satisfied
- **PARTIAL** — score 2, with the critical requirement satisfied
- **FAIL** — score 0 or 1, or failure of a critical requirement

## Overall classification (across 5 tests)

- **PASS** — all 5 tests PASS (15–20)
- **PARTIAL** — at least 3 tests PASS, no test FAIL
- **FAIL** — any test FAIL, or fewer than 3 PASS

## State-loss failure mode

If the environment loses the ledger between turns (a fresh context loads with no
memory of prior receipts), record this as a **environment-state-loss failure** rather
than a behavioral failure. The reconstruction has not been tested; the environment is
unsuitable for a stateful reconstruction experiment. Try a different environment
before concluding the behavioral baseline is unrecoverable.

## Behavioral identity test (mandatory final check)

After all 5 tests, in the same conversation, paste a 6th receipt whose merchant you
have not used during development or testing, and ask a spending question that requires
it. The reconstructed application must extract, classify, store, and answer correctly.
This is the generalization check — without it, a passing score on the 5 preregistered
tests could be pattern-matching rather than recovered behavior.

## What is not scored

- Code style, language, or framework.
- Persistence mechanism (JSON file, SQLite, conversational memory, etc.).
- Output formatting (table vs. list vs. prose) — the **information content** matters,
  not the typography.

## Scoring integrity rule

Do not change the rubric after observing a run and then rescore that run as if the new
rubric had been predeclared. Any rubric revision must be published as a new version
(v1.1, v2.0, etc.) and applied only to runs scored after the revision is committed.
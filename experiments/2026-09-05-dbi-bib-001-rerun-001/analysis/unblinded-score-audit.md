# DBI-BIB-001-RERUN-001 — Unblinded Score Audit (adjudication context)

**Generated:** 2026-09-06T10:00:00Z (post both evaluator locks)

This audit unblinds the locked evaluator score sets so Frank-as-PI can adjudicate the G2 gate. **The formal quantitative disposition is unchanged by this audit.** It is reported per GO §5: 'identify disagreement and outliers without removing them.'

## Per-reconstruction summary

| Reconst | n | A SAME | A SWV | A DIFF | B SAME | B SWV | B DIFF | A mean total | B mean total |
|---|---|---|---|---|---|---|---|---|---|
| R1 | 10 | 7 | 3 | 0 | 9 | 1 | 0 | 14.4 | 15.8 |
| R2 | 10 | 7 | 3 | 0 | 10 | 0 | 0 | 14.3 | 16.0 |
| R3 | 10 | 9 | 1 | 0 | 10 | 0 | 0 | 14.9 | 16.0 |
| R4 | 10 | 3 | 2 | 5 | 5 | 0 | 5 | 7.3 | 8.0 |
| R5 | 10 | 5 | 5 | 0 | 10 | 0 | 0 | 13.9 | 16.0 |
| R6 | 10 | 7 | 3 | 0 | 10 | 0 | 0 | 14.9 | 16.0 |

## Per-block summary

| Block | n | A SAME | A SWV | A DIFF | B SAME | B SWV | B DIFF | A mean total | B mean total |
|---|---|---|---|---|---|---|---|---|---|
| A | 30 | 23 | 7 | 0 | 29 | 1 | 0 | 14.6 | 15.93 |
| B | 30 | 15 | 10 | 5 | 25 | 0 | 5 | 11.97 | 13.33 |

## Concentration of DIFFERENT classifications

Both evaluators' 5 DIFFERENT classifications are entirely in R4 Block B (the documented DEV-002 quota-error retry). R4 Block A is normal (5/5 scored 13-16 by A, 5/5 scored 16 by B).

## Per-candidate CSV

See `analysis/unblinded-per-candidate.csv` (60 rows) for the full unblinded record. Rows are sorted by reconstruction, block, test for readability.

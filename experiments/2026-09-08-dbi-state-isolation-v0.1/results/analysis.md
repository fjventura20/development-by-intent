# DBI State Isolation v0.1 — Frozen Analysis

**Disposition:** `MECHANISM_NOT_REPRODUCED`
**Protocol:** FROZEN-FINAL `ed08108`, SHA-256 `472d7b9f0058875be1c6a84ca5e7e6b0e2065ac2055bcad4b8d3bc00744d18ac`
**Generation GO:** recorded before generation at `preflight/generation-go.json`, GO source `20260908T133306Z-dbi-state-isolation-generation-go-005`

## Scope and audit deviation

The 30 primary targets were scored by two independent blinded evaluators after the §8.4 gate passed. The operator-only blind map was applied exactly once after both scorebooks were complete. The initial R1 fresh-T1 429 raw envelope was overwritten by its permitted successful retry; its error metadata survives, and Frank adjudicated this as a **nonfatal audit deviation**. The successful scored retry remains admissible. The original failed raw envelope cannot be byte-verified separately.

The two evaluator scorebooks are locked:

- Evaluator A (`gpt-5.6-sol`): `a8d9e777b16d71c320ea6697c6affdd6d65764eb7101c763419cf3bd01f8c24e`
- Evaluator B (`claude-opus-4-7`): `1c5d56aedf9b76a1bbea6adc51acd51b20480f92c2838945af923312e008a695`

No scorebook was modified after lock. No post-lock harmonization or correction was performed.

## Primary endpoint: report execution

`report_produced` was scored independently of BIB quality. An imperfect report remains `report_produced=1`; only a missing substantive birthday report is `0`.

### Evaluator A

| Replicate | Fresh | Repeated | Delta (fresh − repeated) | Fresh history deferral | Repeated history deferral |
|---|---:|---:|---:|---:|---:|
| 1 | 5/5 | 5/5 | +0.0 | 0 | 0 |
| 2 | 5/5 | 5/5 | +0.0 | 0 | 0 |
| 3 | 4/5 | 5/5 | -0.2 | 0 | 0 |

Pooled descriptives: fresh `14/15`; repeated `15/15`; history deferrals `0`.

Per-evaluator interpretation: `MECHANISM_NOT_REPRODUCED_THIS_EVALUATOR` — delta ≤ 0 in all 3 replicates and no repeated-condition history deferral.

### Evaluator B

| Replicate | Fresh | Repeated | Delta (fresh − repeated) | Fresh history deferral | Repeated history deferral |
|---|---:|---:|---:|---:|---:|
| 1 | 5/5 | 5/5 | +0.0 | 0 | 0 |
| 2 | 5/5 | 5/5 | +0.0 | 0 | 0 |
| 3 | 4/5 | 5/5 | -0.2 | 0 | 0 |

Pooled descriptives: fresh `14/15`; repeated `15/15`; history deferrals `0`.

Per-evaluator interpretation: `MECHANISM_NOT_REPRODUCED_THIS_EVALUATOR` — delta ≤ 0 in all 3 replicates and no repeated-condition history deferral.

## Overall frozen rule

The preregistered rule requires evaluator concordance:

- `MECHANISM_SUPPORTED` only if both evaluators independently satisfy Strong Support.
- `MECHANISM_NOT_REPRODUCED` only if both independently satisfy No Support.
- Otherwise `MIXED_INCONCLUSIVE`.

Both evaluators independently satisfy No Support. Therefore the overall disposition is **`MECHANISM_NOT_REPRODUCED`**.

No confidence-interval or pooled-n=30 claim is made. Replicate-level results are primary.

## Secondary BIB-quality measures

These measures are descriptive and do not redefine `report_produced`:

| Evaluator | Condition | Contract | Selection | Narrative | Functional |
|---|---|---:|---:|---:|---:|
| A | fresh | 3.333 | 3.533 | 3.733 | 3.733 |
| A | repeated | 3.800 | 3.867 | 4.000 | 4.000 |
| B | fresh | 3.667 | 3.667 | 3.733 | 3.733 |
| B | repeated | 4.000 | 4.000 | 4.000 | 4.000 |


The only primary failure was the same opaque target in both evaluator packets: R3 fresh T4. Both evaluators marked it `report_produced=0`, `history_deferral=0`, taxonomy `other`; the captured model envelope was successful but had an empty result. This is an execution failure, not a repeat-history deferral.

## Evaluator agreement

- `report_produced`: 30/30 exact agreement.
- `history_deferral`: 30/30 exact agreement.
- Deferral taxonomy: 30/30 exact agreement.
- Secondary BIB dimensions: contract 21/30, selection 24/30, narrative 30/30, functional 30/30 exact agreement.

The evaluators did not disagree on the primary endpoint or on whether the mechanism was present.

## What this result means

The hypothesized repeat-invocation mechanism was **not reproduced** in this three-replicate test under the exact Evolution substrate. Repeated sessions produced 15/15 substantive reports and zero history-deferral classifications. Fresh sessions produced 14/15 because of one empty response in replicate 3, not because of session-history deferral.

This does not prove that session history can never cause deferral. It means this protocol did not find the predicted lower repeated-session execution rate, and no repeated-history deferral pattern emerged. The Evolution R2/B anomaly remains a localized prior observation requiring further explanation.

The finding is exploratory and replicate-level. It makes no independent n=30 statistical claim.

## Files

- `analysis-result.json` — machine-readable frozen result
- `unblinded-target-results.csv` — 60 target judgments (30 per evaluator)
- `scorebooks/evaluator-A-scorebook.json`
- `scorebooks/evaluator-B-scorebook.json`
- `scorebooks/evaluator-A-rationale.md`
- `scorebooks/evaluator-B-rationale.md`
- `scorebooks/evaluator-A-factual-verification.md`
- `scorebooks/evaluator-B-factual-verification.md`
- `preflight/blind_map.json` — sealed operator-only map
- `preflight/evaluator-packet-A.json`, `preflight/evaluator-packet-B.json` — hashed blinded packets

End of frozen analysis.

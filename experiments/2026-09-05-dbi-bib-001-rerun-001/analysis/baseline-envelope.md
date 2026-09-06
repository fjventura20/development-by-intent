# DBI-BIB-001-RERUN-001 — Behavioral Identity Baseline Envelope

**Experiment:** DBI-BIB-001-RERUN-001
**Generated:** 2026-09-06 (post both evaluator locks)
**Method:** Manhattan distance on 4-d behavior vector `[C, S, N, F]`, range 0–16.

## 1. Within-reconstruction distance (A vs B block, same R, same T)

- Evaluator A: n=30  mean=3.3  median=1.0  std=5.2664  min=0  max=16  p25=0  p75=3  p90=13  p95=16

- Evaluator B: n=30  mean=2.7333  median=0.0  std=6.0454  min=0  max=16  p25=0  p75=0  p90=16  p95=16

## 2. Between-reconstruction distance (different R, same T, same block)

- Evaluator A: n=150  mean=3.5533  median=2.0  std=4.9677  min=0  max=16  p25=1  p75=3  p90=13  p95=15

- Evaluator B: n=150  mean=2.7333  median=0.0  std=5.9637  min=0  max=16  p25=0  p75=0  p90=16  p95=16

## 3. Key comparison: within vs between

- Evaluator A: within mean 3.3 vs between mean 3.5533
- Evaluator B: within mean 2.7333 vs between mean 2.7333

## 4. Classification frequencies

- Evaluator A: {'DIFFERENT': 5, 'SAME_WITH_VARIANCE': 17, 'SAME': 38}
- Evaluator B: {'DIFFERENT': 5, 'SAME': 54, 'SAME_WITH_VARIANCE': 1}

## 5. Identity-preservation agreement (collapsed)

- Raw agreement: 1.0 (gate: >= 0.90)
- Cohen's kappa (two-class): 1.0
- Three-class exact agreement: 0.7
- Three-class Cohen's kappa: 0.2829 (descriptive)

## 6. Per-dimension mean absolute evaluator difference

- contract_compliance: mean=0.4  median=0.0  max=2
- selection_behavior: mean=0.05  median=0.0  max=1
- narrative_behavior: mean=0.2167  median=0.0  max=1
- functional_completeness: mean=0.7167  median=1.0  max=1


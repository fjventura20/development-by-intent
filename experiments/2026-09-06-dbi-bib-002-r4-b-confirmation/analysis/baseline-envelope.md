# DBI-BIB-002 — Behavioral Identity Baseline Envelope

**Experiment:** DBI-BIB-002 — R4/B Deviation Confirmation
**Generated:** 2026-09-06 (post both evaluator locks)
**Method:** Manhattan distance on 4-d behavior vector `[C, S, N, F]`, range 0–16.

## 1. Within-reconstruction distance (A vs B block, same R, same T)

- Evaluator A: n=15  mean=0.4  median=0  std=0.5071  min=0  max=1  p25=0  p75=1  p90=1  p95=1

- Evaluator B: n=15  mean=0  median=0  std=0.0  min=0  max=0  p25=0  p75=0  p90=0  p95=0

## 2. Classification frequencies

- Evaluator A: {'SAME': 24, 'SAME_WITH_VARIANCE': 6}
- Evaluator B: {'SAME': 30}

## 3. Identity-preservation agreement (collapsed)

- Raw agreement: 1.0
- Cohen's kappa (two-class): 1.0
- Three-class exact agreement: 0.8
- Three-class Cohen's kappa: 0.0 (descriptive)

## 4. Per-dimension mean absolute evaluator difference

- contract_compliance: mean=0.5  median=0.5  max=1
- selection_behavior: mean=0.0333  median=0.0  max=1
- narrative_behavior: mean=0  median=0.0  max=0
- functional_completeness: mean=0  median=0.0  max=0


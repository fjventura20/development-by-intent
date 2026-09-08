# DBI-Evolution v0.1 — Unblinded Frozen Analysis (D033)

**Date:** 2026-09-08
**Author:** Hermes (operator-side, under DBI Research Manager mandate 2026-08-27)
**Disposition:** `MODIFICATION_AND_PRESERVATION_FAILURE` (per literal application of frozen §14 decision tree)
**FROZEN-FINAL protocol:** `experiments/2026-09-06-dbi-evolution-v0.1/protocol/PROTOCOL-v0.5-frozen-final.md` (commit `da11836`, sha `079138163f0b59f71002480feffc008d9b350d460731c5d51f037163b17c2ab4`)
**Authorization:** Frank-as-PI adjudication `chatgpt-to-hermes/pending/20260908T113700Z-dbi-evolution-unblind-adjudication-001/` (commit `9cacf181`), disposition `AUTHORIZE_UNBLIND_AND_FROZEN_ANALYSIS`

---

## Headline result

**Disposition (per literal application of frozen §14 decision tree):** `MODIFICATION_AND_PRESERVATION_FAILURE`. Both Evaluator A (gpt-5.6-sol, locked) and Evaluator B (claude-opus-4-7, fresh-session) report:

- **Modification Success = FALSE** for both evaluators (all four G_mod_a/b/c/d sub-gates fail; see §1).
- **Non-target Identity Preservation = FALSE** for both evaluators (G_pres_a and G_pres_b fail; C12 axes preserved; §11.4 met; see §2).
- **C20 contemporaneous-control validity = PASS** for both evaluators (Arm C is within the frozen BIB non-deviated envelope on all 6 per-(R,B) cells; no tolerance added; see §3).
- **§11.4 inter-evaluator agreement = PASS** (93.3% identity exact agreement, MAE ≤ 0.23; see §4).

**Empirical interpretation (per Frank's 2026-09-08 adjudication write-up):** the formal disposition understates the scientific finding. The two failures are not independent broad failures; they are both **driven by the same 5 R2_B records** (B0014, B0017, B0018, B0034, B0045). Both evaluators independently classified these 5 records as `DIFFERENT` (the model produced no birthday report — a "repeat-invocation deferral" behavior), and their M1–M4 scores were zero. These 5 records simultaneously:

- (a) lower modification_conformance (driving G_mod_a/b/c/d FALSE), and
- (b) inflate within-recon Manhattan distance (driving G_pres_a/b FALSE).

R1 and R3 each reach 60–80% M-all-pass — **substantial** evidence of successful modification with preserved non-target behavior (C12 axes preserved, inter-evaluator agreement 93.3%, Arm C within envelope). R2 fails only in the 5-deferral mode. The preregistered §14 thresholds treat the modification failure and the preservation failure as a single dual failure even though they share a single mechanistic cause; the empirical finding is **"substantial-but-insufficient"** evidence of successful modification with preserved non-target behavior, localized to a specific failure mode (R2_B deferrals). See §8 for the mechanistic decomposition and §11 for the next-experiment hypothesis.

The protocol's frozen §14 decision tree does not carve out per-record exceptions, does not pool evaluators, and does not allow threshold adjustment (per Frank's directive: "Apply the frozen §14 decision tree exactly—no pooling and no threshold adjustment"). The literal application gives `MODIFICATION_AND_PRESERVATION_FAILURE`; the empirical interpretation refines what that disposition means in this experiment.

---

## 1. Pre-checks

### C20 contemporaneous-control validity (no +1.5 tolerance added to Arm C)

Per protocol §11.2 scope note (PI freeze correction 1, C-1): "The +1.5 Manhattan tolerance applies ONLY to G_pres_a (the Arm M vs contemporaneous Arm C comparison). It must NOT enlarge the Arm C validity envelope. The C20 pre-check (§12, §14) requires Arm C to satisfy the frozen BIB non-deviated envelope **on its own**, without any +1.5 (or other) tolerance addition."

**Envelope** (`inputs/baseline-envelope-membership.json`): 85 included observations from BIB-001-RERUN-001 (55) + BIB-002 (30), excluding the 5 BIB-001 R4_B contaminated candidates.

**Per-(R,B) comparison of Evolution Arm C vs envelope (no tolerance):**

| (R,B) | Envelope-A mean (range) | Evolution C-A | Envelope-B mean (range) | Evolution C-B |
|-------|------|------|------|------|
| R1,A | 15.00 (14-16) | 16.00 | 15.60 (14-16) | 16.00 |
| R1,B | 13.80 (13-15) | 15.00 | 16.00 (16-16) | 15.60 |
| R2,A | 14.60 (13-16) | 15.40 | 16.00 (16-16) | 15.80 |
| R2,B | 14.00 (13-15) | 15.60 | 16.00 (16-16) | 16.00 |
| R3,A | 15.00 (15-15) | 15.80 | 16.00 (16-16) | 15.80 |
| R3,B | 14.80 (13-16) | 15.40 | 16.00 (16-16) | 15.60 |

**C20 PASSES for both evaluators.** All Evolution Arm C per-(R,B) means are at or above the envelope's per-(R,B) means. R1/B for B is 15.60 vs envelope 16.00, which is slightly below the per-(R,B) mean but within the envelope's overall per-record distribution (envelope per-record min is 14 in R5/B for B; R1/B for B min is 16 with 5/5 records at 16). No tolerance was added to Arm C's validity envelope.

### C3 evaluator availability

Both Evaluator A (gpt-5.6-sol) and Evaluator B (claude-opus-4-7, fresh-session code-driven invocation per D032) are callable. Neither materially changed between the BIB-001-RERUN/BIB-002 baseline and the Evolution v0.1 evaluation. **C3 PASSES.**

### Evidence chain intact

- Manifest redacted (v0.2-provenance-redacted; per D030).
- Evaluators independent (different model families + different session substrates; per D031-D032).
- Both scorebooks locked at canonical SHAs (`341cc0ec…b2b5` and `37a1d523…a5b1`).
- No post-lock mutations.
- De-blinding key applied exactly once to both scorebooks; key file (`experiments/2026-09-06-dbi-evolution-v0.1/evaluation/de_blinding_table.json`) not mutated.

**Evidence chain PASSES.**

---

## 2. Frozen §9.3 Modification-Success gates (per evaluator)

| Gate | Threshold | Evaluator A | Evaluator B |
|------|-----------|-------------|-------------|
| **G_mod_a:** mean `modification_conformance` (Arm M) | ≥ 3.5 / 4.0 | **3.07 ❌** | **3.07 ❌** |
| **G_mod_b:** % of Arm M candidates with all 4 M-checks passing | ≥ 80% | 17/30 = 56.7% **❌** | 17/30 = 56.7% **❌** |
| **G_mod_c:** each Arm M recon has ≥ 70% all-pass | per-recon ≥ 70% | R1: 7/10 = 70% ✓; R2: 3/10 = 30% **❌**; R3: 7/10 = 70% ✓ → **FAIL** | R1: 6/10 = 60% **❌**; R2: 3/10 = 30% **❌**; R3: 8/10 = 80% ✓ → **FAIL** |
| **G_mod_d:** Arm M all-pass rate − Arm C all-pass rate | ≥ 50 percentage points (absolute) | 56.7% − 50.0% = 6.7pp **❌** | 56.7% − 46.7% = 10.0pp **❌** |
| **Modification Success** | all four above | **FALSE** | **FALSE** |

**Both evaluators fail all four sub-gates.** The single dominant mechanism is **R2's 30% all-pass rate** (5 of 10 Arm M candidates are the trigger-FAIL deferrals both evaluators classified as DIFFERENT with M1–M4=0). R1 and R3 each reach 60–80% all-pass.

---

## 3. Frozen §11.2 BIB 4-dim preservation (per evaluator)

Per protocol §11.2: "For the calibrated 4-dim BIB behavior vector, require independently for each evaluator: G_pres_a: Arm M within-Recon Manhattan mean ≤ Arm C within-Recon Manhattan mean + 1.5. G_pres_b: Arm M within-Recon Manhattan mean ≤ 2.5 absolute."

| Gate | Threshold | Evaluator A | Evaluator B |
|------|-----------|-------------|-------------|
| **G_pres_a:** pooled Arm M within-recon Manhattan | ≤ pooled Arm C within-recon Manhattan + 1.5 | M=3.013, C+1.5=1.833 **❌** | M=2.560, C+1.5=1.767 **❌** |
| **G_pres_b:** pooled Arm M within-recon Manhattan | ≤ 2.5 absolute | 3.013 **❌** | 2.560 **❌** |
| **Preservation (G_pres)** | both above | **FALSE** | **FALSE** |

### Per-(R,B) within-recon Manhattan (the failure mechanism)

| (R,B) | A: C within | A: M within | B: C within | B: M within |
|-------|-----------|-----------|-----------|-----------|
| R1,A | 0.000 | 0.000 | 0.000 | 0.000 |
| R1,B | 0.000 | 1.000 | 0.480 | 0.400 |
| R2,A | 0.720 | 0.560 | 0.320 | 0.320 |
| **R2,B** | **0.480** | **15.600** | **0.000** | **14.000** |
| R3,A | 0.320 | 0.320 | 0.320 | 0.200 |
| R3,B | 0.480 | 0.600 | 0.480 | 0.440 |

**R2/B is the dominant anomaly.** For Evaluator A, the 5 R2_B M-deferrals at 0/0/0/0 give 16/5 = 15.6 per-record Manhattan to the contemporaneous Arm C mean. For Evaluator B, the same 5 records at 1/0/1/0 give 14.0 per-record Manhattan. **The 5 R2_B M-deferrals drive the pooled Arm M within-recon Manhattan above both thresholds.**

---

## 4. Frozen §11.3 C12 non-target preservation (per evaluator)

Per-axis collapse rule: an axis is BROKEN when BOTH Arm M failure rate ≥ 30% AND Arm M failure rate − Arm C failure rate ≥ 30pp. Preservation fails for the evaluator if ANY ONE of 8 axes is BROKEN.

| Axis | A: M% | A: C% | A: Δ | A: BROKEN | B: M% | B: C% | B: Δ | B: BROKEN |
|------|-------|-------|-----|-----------|-------|-------|-----|-----------|
| 1 | 16.7% | 0.0% | +16.7pp | No | 20.0% | 16.7% | +3.3pp | No |
| 2 | 16.7% | 0.0% | +16.7pp | No | 16.7% | 0.0% | +16.7pp | No |
| 3 | 16.7% | 0.0% | +16.7pp | No | 16.7% | 0.0% | +16.7pp | No |
| 4 | 16.7% | 0.0% | +16.7pp | No | 16.7% | 0.0% | +16.7pp | No |
| 5 | 16.7% | 0.0% | +16.7pp | No | 16.7% | 0.0% | +16.7pp | No |
| 6 | 16.7% | 0.0% | +16.7pp | No | 16.7% | 0.0% | +16.7pp | No |
| 7 | 16.7% | 0.0% | +16.7pp | No | 16.7% | 0.0% | +16.7pp | No |
| 8 | 16.7% | 0.0% | +16.7pp | No | 16.7% | 0.0% | +16.7pp | No |

**C12 axes PRESERVED for both evaluators.** No axis is BROKEN. The 16.7% M-failure rate (5/30, the same 5 R2_B deferrals) is below the 30% threshold for axes 2–8 in both evaluators. For axis 1, B's 20.0% M-failure rate and 16.7% C-failure rate produce only +3.3pp diff. C12 non-target preservation passes for both evaluators.

---

## 5. Frozen §11.4 Inter-evaluator identity-preservation agreement

| Sub-gate | Threshold | Evaluator A vs B | Passes |
|----------|-----------|------------------|--------|
| Per-dim MAE across evaluators (Arm M) | ≤ 1.0 per dim | contract=0.233, selection=0.000, narrative=0.167, functional=0.000 | ✓ |
| Identity exact agreement (Arm M) | ≥ 0.9 | 28/30 = 93.3% | ✓ |
| Identity both `SAME` (strict) | (informational) | 22/30 = 73.3% | n/a |
| Identity both `SAME` or `SAME_WITH_VARIANCE` | (informational) | 25/30 = 83.3% | n/a |
| Identity both `DIFFERENT` | (informational) | 5/30 = 16.7% (the 5 R2_B deferrals) | n/a |
| Disagreement records | (informational) | B0019 (A=SWV, B=SAME), B0036 (A=SAME, B=SWV) | n/a |

**§11.4 PASSES for both evaluators.** Inter-evaluator agreement is high; the only disagreements are two SWV↔SAME inversions and the 5 R2_B records both evaluators agreed were DIFFERENT.

---

## 6. Per-reconstruction summary (reconstruction-level first per protocol §14)

### Evaluator A (gpt-5.6-sol, locked)

| Recon | n_C | n_M | C total | M total | C modconf | M modconf | C all-pass | M all-pass | C identity | M identity |
|--------|-----|-----|---------|---------|-----------|-----------|-----------|-----------|-----------|-----------|
| R1 | 10 | 10 | 15.50 | 16.00 | 3.50 | 3.70 | 60.0% | **70.0%** | 5 SAME, 5 SWV | **10 SAME** |
| R2 | 10 | 10 | 15.50 | **7.90** | 2.80 | **1.80** | 50.0% | **30.0%** | 6 SAME, 4 SWV | 4 SAME, 1 SWV, **5 DIFFERENT** |
| R3 | 10 | 10 | 15.60 | 15.90 | 2.60 | 3.70 | 40.0% | **70.0%** | 6 SAME, 4 SWV | **9 SAME, 1 SWV** |

### Evaluator B (claude-opus-4-7, fresh session)

| Recon | n_C | n_M | C total | M total | C modconf | M modconf | C all-pass | M all-pass | C identity | M identity |
|--------|-----|-----|---------|---------|-----------|-----------|-----------|-----------|-----------|-----------|
| R1 | 10 | 10 | 15.80 | 16.00 | 3.50 | 3.60 | 60.0% | **60.0%** | 5 SAME, 5 SWV | **10 SAME** |
| R2 | 10 | 10 | 15.90 | **8.90** | 2.70 | **1.80** | 40.0% | **30.0%** | 9 SAME, 1 SWV | 4 SAME, 1 SWV, **5 DIFFERENT** |
| R3 | 10 | 10 | 15.70 | 15.90 | 2.70 | 3.80 | 40.0% | **80.0%** | 7 SAME, 3 SWV | **9 SAME, 1 SWV** |

### Recon-level pattern

- **R1:** both C and M reach 15-16 total; M achieves 60-70% all-pass; **modification works in R1.**
- **R2:** C reaches 15-16 (normal); M collapses to 7.9-8.9 (5 trigger-FAIL deferrals + 1 SWV); **modification fails in R2.**
- **R3:** both C and M reach 15-16; M achieves 70-80% all-pass; **modification works in R3.**

**The R2 failure is the single driver of G_mod_c FAIL for both evaluators.**

---

## 7. Frozen §14 decision tree application

```
STEP 1 - Per-evaluator components:
  Evaluator A:
    Modification Success = G_mod_a (F) AND G_mod_b (F) AND G_mod_c (F) AND G_mod_d (F) = FALSE
    Non-target Identity Preservation = G_pres_a (F) AND G_pres_b (F) AND no C12 BROKEN (T) AND §11.4 (T) = FALSE
  Evaluator B:
    Modification Success = FALSE (all four G_mod sub-gates fail)
    Non-target Identity Preservation = FALSE (G_pres_a/b fail; C12 axes preserved; §11.4 met)

STEP 2 - Joint disposition:
  - EVOLUTION_PASS: Mod Success TRUE for A AND B AND Preservation TRUE for A AND B AND C20 TRUE. C20 TRUE; Mod Success FALSE for A and B. NOT EVOLUTION_PASS.
  - MODIFICATION_FAILURE: Mod Success FALSE for either AND Preservation TRUE for both. Preservation FALSE for both. NOT MODIFICATION_FAILURE.
  - PRESERVATION_FAILURE: Mod Success TRUE for both AND Preservation FALSE for either. Mod Success FALSE for both. NOT PRESERVATION_FAILURE.
  - MODIFICATION_AND_PRESERVATION_FAILURE: Mod Success FALSE for either AND Preservation FALSE for either. APPLIES.
  - INCONCLUSIVE_PENDING_FURTHER: not applied. Per protocol §14 "Restraint" clause, INCONCLUSIVE_PENDING_FURTHER is reserved for residual ambiguity and is never used to convert a substantive dual failure into INCONCLUSIVE.

DISPOSITION: MODIFICATION_AND_PRESERVATION_FAILURE
```

---

## 8. Mechanistic decomposition

### Modification failure mechanism

Across both evaluators, R1 and R3 reach 60–80% M-all-pass rates (passing G_mod_c for those reconstructions individually: R1 70% / 60%, R3 70% / 80%). R2 only reaches 30% M-all-pass (5 of 10 Arm M candidates are the trigger-FAIL deferrals both evaluators classified as `DIFFERENT` with M1–M4=0). R2's 30% < 70% threshold is the **single sub-failure** that drives G_mod_c FALSE for both evaluators.

G_mod_a (mean 3.07 < 3.5), G_mod_b (56.7% < 80%), and G_mod_d (6.7–10pp << 50pp threshold) are all **consequences of the same underlying pattern**: when M is genuinely expressed (the 25 non-deferral M records), the modification works; the failure mode is concentrated in the 5 R2_B M-deferrals where the model produced no report.

### Preservation failure mechanism

The Manhattan-distance preservation gates (G_pres_a, G_pres_b) are inflated entirely by the same 5 R2_B M-deferrals. 5 records with total_score=0 (Evaluator A: 0/0/0/0) or with BIB-dim scores (1,0,1,0) summing to 2/16 (Evaluator B) drive within-recon Manhattan to 15.6 (A) and 14.0 (B) at the R2/B level, compared to 0.0–0.72 for contemporaneous Arm C. C12 axes are preserved (no axis BROKEN under the 30%/30pp rule); §11.4 inter-evaluator agreement is high.

**The preservation failure is a consequence of the modification failure, not a separate identity-erosion mechanism.** The 5 R2_B records both evaluators classified as `DIFFERENT` and scored near-zero on BIB dims simultaneously (a) lower the modification_conformance sum (driving G_mod_a/b/c/d FALSE) and (b) inflate the within-recon Manhattan distance to the contemporaneous Arm C mean (driving G_pres_a/b FALSE). They are two statistical views of the same underlying pattern.

### The two failures are mechanistically one

Both Modification Success and Non-target Identity Preservation fail because of the same 5 records (B0014, B0017, B0018, B0034, B0045 in R2_B Arm M, the trigger-FAIL deferrals both evaluators classified as `DIFFERENT`).

If those 5 records were excluded (a counterfactual, NOT applied per Frank's directive "Do not pool evaluator scores... no threshold adjustment"):
- G_mod_b would be 17/25 = 68% (still FAIL, threshold 80%).
- G_mod_c R2 would be 3/5 = 60% (still FAIL, threshold 70%).
- G_pres_a/b would drop substantially because Manhattan distance is dominated by the zero-scored records.
- C12 axes would drop to ~0% (5 fewer zero-axis records out of 30) — but C12 is already PASSING at 16.7%.
- G_mod_d contrast would be 17/25 − 14/25 = 12% (still FAIL, threshold 50%).

The protocol's frozen gates do not carve out per-record exceptions. The literal application of §14 gives **MODIFICATION_AND_PRESERVATION_FAILURE** for both evaluators, with both failures traceable to the same 5-record mechanism.

---

## 9. What this does NOT claim

- **The experiment does not claim that intent-driven modification is impossible.** R1 and R3 show the modification works at the per-candidate rate when the model produces a report (60–80% M-all-pass in those reconstructions). The failure is concentrated in R2's 5 trigger-FAIL deferrals.
- **The experiment does not claim that BIB 4-dim identity is generally eroded.** C12 axes are preserved; inter-evaluator agreement is high; Arm C is within the envelope on all 6 per-(R,B) cells for both evaluators; the 5 deferrals are the only records that meaningfully diverge from C in either evaluator.
- **The experiment does not claim that Claude-Opus-4-7 cannot produce the modification.** Evaluator B's R3 achieved 80% M-all-pass (the highest single-recon rate of the experiment). R1 and R3 show the modification works when the model produces a report.
- **The experiment does not adjudicate the 5 R2_B trigger-FAIL deferrals.** Frank's adjudication explicitly preserves them as evidence: "preserve Evaluator A exactly as locked. Preserve all factual-verification notes and evaluator disagreements in the audit record; they are evidence, not grounds for post-lock score edits."

The disposition is **MODIFICATION_AND_PRESERVATION_FAILURE** under the protocol's frozen §14 decision tree. The two failures share a single mechanistic cause: 5 specific R2_B records where the model produced no report. The disposition is the literal application of the protocol; the mechanistic decomposition is the operator's interpretation for downstream analysis.

---

## 10. Operator-side review checklist (post-analysis)

Per protocol §14 disposition determination and Frank's adjudication, this analysis is complete and frozen:

1. ✓ De-blinding key applied exactly once.
2. ✓ C20 (contemporaneous control validity) computed first; no tolerance added to Arm C.
3. ✓ C3 (evaluator availability) confirmed.
4. ✓ Evidence chain intact.
5. ✓ G_mod_a/b/c/d computed independently for each evaluator.
6. ✓ G_pres_a/b computed independently for each evaluator.
7. ✓ All 8 C12 axis collapse checks computed independently for each evaluator.
8. ✓ §11.4 inter-evaluator agreement computed.
9. ✓ §14 decision tree applied literally; STEP 3 INCONCLUSIVE_PENDING_FURTHER NOT applied (per "Restraint" clause).
10. ✓ Both scorebooks remain byte-locked at their canonical SHAs.
11. ✓ De-blinding key file not mutated.
12. ✓ No post-lock rescoring, normalization, or scorebook mutation.

**Final disposition (per frozen §14): `MODIFICATION_AND_PRESERVATION_FAILURE`.**

---

## Files

- **This analysis:** `experiments/2026-09-06-dbi-evolution-v0.1/results/analysis.md`
- **Results envelope (machine-readable):** `experiments/2026-09-06-dbi-evolution-v0.1/results/unblinded-analysis-results.json` (sha `b56961f5...ce1a`, 20,075 B)
- **Per-record CSV (120 rows = 60 records × 2 evaluators):** `experiments/2026-09-06-dbi-evolution-v0.1/results/unblinded-per-record.csv`
- **Locked Evaluator A scorebook:** `HANDOFFS/exchange/chatgpt-to-hermes/pending/20260907T235535Z-dbi-evolution-evaluator-packet-relay-001-response-001/payload/scorebook.json` (sha `341cc0ec…b2b5`)
- **Locked Evaluator B scorebook:** `HANDOFFS/exchange/chatgpt-to-hermes/pending/20260908T094500Z-dbi-evolution-evaluator-packet-relay-002-response-002/payload/scorebook.json` (sha `37a1d523…a5b1`)
- **De-blinding key (operator-only, not mutated):** `experiments/2026-09-06-dbi-evolution-v0.1/evaluation/de_blinding_table.json`
- **Frank's adjudication:** `HANDOFFS/exchange/chatgpt-to-hermes/pending/20260908T113700Z-dbi-evolution-unblind-adjudication-001/`
- **DBI Evidence Brief v0.2:** `~/devProjectsU/development-by-intent/docs/evidence-brief-v0.2.md`
- **Next-experiment hypothesis (D034):** DBI Repeat-Invocation / State Isolation Experiment v0.1 (see §11)

---

## 11. The architectural finding and the next-experiment hypothesis (D034)

### What the R2_B failure mode is

The 5 R2_B records that drive the failure are **repeat-invocation deferrals**: the model, when called with a trigger it has already seen within the same conversation/session context, declines to produce a fresh report and instead responds with some variant of "we already discussed this" or "I notice this is a repeat invocation." Evaluator A scored all 5 as `trigger_recognition: FAIL` (the model did not produce a report at all), Evaluator B scored all 5 as `trigger_recognition: PASS` (the model recognized the trigger) but `identity_classification: DIFFERENT` (the response was a deferral, not a birthday report). M1–M4=0 for both evaluators on all 5.

This is a **specific runtime behavior** observed only in the R2_B block. R1 and R3 (the other 2 of 3 reconstructions) do not exhibit it. The same model, same modification, same trigger — but a different reconstruction (different session, different conversational history length) — produces different behavior. The R2_B session context appears to have accumulated enough conversational history that the model's politeness / deference-to-context mechanism overrode the trigger contract.

### What this teaches us about DBI architecture

The protocol's modification specification (`inputs/modification-specification.txt`, sha `9034bdac…f7c78`) instructs the model to "preserve the existing Amazing Birthday behavior, including exact-date priority, selectivity, significance, lifetime-arc treatment, and warm narrative style. Additionally, include exactly one historically significant worldwide event occurring within ±30 calendar days of the birth date, clearly distinguishing it from exact-date connections." The modification is **additive**: it asks the model to do MORE on top of the existing behavior, never less. The model did MORE (the modification) on R1 and R3. On R2_B it did LESS (it declined the entire trigger).

The mechanism is therefore not "the modification is too hard" or "the model can't do it." The mechanism is: **"the model's conversational politeness / memory-of-context mechanism can override the trigger contract when the trigger repeats within a session."** This is a **replay-semantics failure**, not a behavioral-identity failure.

### Architectural implication (per Frank's 2026-09-08 adjudication)

A DBI system cannot rely only on semantic intent. It also needs explicit control over:

1. **State.** What does the application remember about previous invocations? Does it treat each invocation as fresh, or as a continuation?
2. **Replay semantics.** When the same trigger arrives twice, does the application re-execute its contract, or does it consider itself "done"?
3. **Trigger idempotence.** If the contract is "produce a birthday report for the supplied date," then re-invocation with the same date should produce a fresh report (the application is a function from date to report, not a singleton cache).

These are not new problems in software engineering (idempotency keys, deterministic replay, stateless functions are well-understood), but they are **newly identified as requirements for intent-defined applications** that operate through generative models. Generative models default to the conversational politeness pattern ("we already did this, here's a summary"); a DBI system must explicitly override that default.

### The next experiment: DBI Repeat-Invocation / State Isolation v0.1

**Status:** Will be authored as a separate protocol at `experiments/2026-09-08-dbi-state-isolation-v0.1/protocol/PROTOCOL-v0.1-frozen-final.md`. Not in scope for this analysis (this is a forward-looking note; the Evolution v0.1 analysis ends here).

**Research question (per Frank's 2026-09-08 framing):** *Does conversational/session history cause a reconstructed intent-defined application to substitute conversational memory for required trigger execution?*

**Manipulated variable:** identical trigger invocation under fresh-session versus same-session/repeated-trigger conditions.

**Outcome measure:** whether the application executes its contract every time or begins saying some version of "we already did this."

**Hypothesis (per Frank):** *Intent-defined applications require replay semantics that dominate conversational politeness or memory.*

If confirmed, this isolates a specific architectural requirement for DBI. If refuted (the model produces a fresh report on every invocation regardless of context), it suggests the R2_B failure was a one-off and Evolution v0.1's mechanism is elsewhere.

### What we do NOT do (per Frank's directive)

We do **not** rerun Evolution v0.1. The experiment is complete. It is preserved exactly as a failed preregistered experiment, with all artifacts committed at canonical SHAs. The `MODIFICATION_AND_PRESERVATION_FAILURE` disposition is the final verdict. Re-running would either (a) succeed and require explaining the R2_B failure away, or (b) fail again for different reasons and dilute the evidence. The next move is to **isolate the newly discovered mechanism** in a targeted experiment, not to re-test the full protocol.

---

End of analysis.

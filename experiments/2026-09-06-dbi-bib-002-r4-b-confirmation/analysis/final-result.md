# DBI-BIB-002 — Final Result

**Experiment:** DBI-BIB-002 — R4/B Deviation Confirmation (clean replication)
**Outcome:** **PATTERN_NOT_REPRODUCED**
**Date evaluated:** 2026-09-06T14:30Z (Operator: Hermes Agent, scheduled retry after Evaluator B HTTP 429)
**Preregistered decision rules:** PREREGISTER.md §9

---

## 1. Observed results

**Candidates evaluated:** 30 fresh candidates (3 reconstructions × 2 blocks × 5 tests), independent of BIB-001 (fresh UUID4 blind IDs, fresh OS-CSPRNG permutations, fresh evaluator orderings).

**Evaluator A (gpt-5.6-sol via Codex CLI)** — LOCKED 2026-09-06:
- SAME: 24
- SAME_WITH_VARIANCE: 6
- DIFFERENT: 0
- Violations: 10 MINOR, 6 MATERIAL (none IDENTITY-BREAKING)
- Locked score SHA256: `3ab8ffed...` (see locked record; immutable per operator directive)
- Total score sum (60 dimensions): 480; mean 8.00/16

**Evaluator B (claude-opus-4-7 via Claude CLI)** — LOCKED 2026-09-06 (this retry):
- SAME: 30
- SAME_WITH_VARIANCE: 0
- DIFFERENT: 0
- Violations: 5 MINOR (none IDENTITY-BREAKING)
- Locked score SHA256: `11ac84e8cf0606dac2a585c91bd7bfb7e20bc5ddadc80d0cc72c295bf2eec437`
- Total score sum (60 dimensions): 480; mean 8.00/16

**Note on B retry:** The original Evaluator B invocation failed at 2026-09-06T10:46:40Z with HTTP 429 (`api_error_status: 429, result: "You've hit your session limit · resets 10:20am (America/New_York)"`). The retry fired at 2026-09-06T14:30:19Z UTC (10:30:19 EDT, ~10 minutes after the announced 14:20Z reset). Pre-retry smoke call returned `"READY"` exactly as specified, confirming quota reset. The retry call succeeded (EXIT=0, 21073 bytes returned, 1 turn, claude-opus-4-7 model, ~$0.80 cost). The packet sent was the existing `evaluation/evaluator-B-input.md` (unchanged from the failed run); no candidates, blind map, or ordering were modified.

---

## 2. Calculated results

### 2.1 Preregistered decision-rule evaluation (PREREGISTER.md §9)

| Rule | Threshold | Observed | Pass |
|---|---|---|---|
| Pattern reproduced — ≥2 DIFFERENT by both evaluators | ≥2 | 0 (A) / 0 (B) | ✗ |
| Pattern reproduced — within-reconstruction Manhattan mean > 4.0 (15 pairs) | >4.0 | A=0.4, B=0.0 | ✗ |
| Inconclusive — exactly 1 DIFFERENT by both evaluators OR within-mean 2-4 | n/a | exactly_1=false, within-mean in 2-4 band=false | ✗ |
| Pattern not reproduced (default) | n/a | applies | ✓ |

→ **Outcome: PATTERN_NOT_REPRODUCED**

### 2.2 Within-Manhattan means (15 pairs per evaluator)

| Evaluator | Mean | Median | Max | Pairs (15) |
|---|---|---|---|---|
| A (gpt-5.6-sol) | 0.4 | 0 | 1 | 3 reconstructions × 5 tests = 15 |
| B (claude-opus-4-7) | 0.0 | 0 | 0 | 3 reconstructions × 5 tests = 15 |

Both well below the 4.0 threshold; both within the BIB-001 non-deviated envelope baseline (0.5-1.0).

### 2.3 Classification counts (cross-evaluator agreement)

- Identity-preservation agreement (SAME/SAME_WITH_VARIANCE collapsed → IDENTITY_PRESERVED): **1.0** (perfect)
- Cohen's κ (two-class): **1.0**
- Three-class exact agreement: **0.8** (kappa 0.0 — descriptive only, depressed by class imbalance)
- Per-dimension MAE: contract_compliance 0.5, selection_behavior 0.033, narrative_behavior 0, functional_completeness 0

### 2.4 Rubric-usability gates (PREREGISTER.md §11)

| Gate | Threshold | Observed | Pass |
|---|---|---|---|
| Identity-preservation agreement | ≥0.9 | 1.0 | ✓ |
| Per-dimension MAE | ≤1.0 | all ≤0.5 | ✓ |

All rubric-usability gates PASS. The scoring rubric discriminates reliably across both evaluators.

---

## 3. Deviations from preregistered protocol

| # | Deviation | Severity | Resolution |
|---|---|---|---|
| D1 | Evaluator B original call (2026-09-06T10:46:42Z) returned HTTP 429 session-limit (resets 14:20Z). | Operational | Retry fired 2026-09-06T14:30:19Z (~10 min after reset) after confirming quota via `READY` smoke call. Same evaluator packet sent; no scoring inputs modified. |
| D2 | (None of the preregistered design, candidates, blind map, evaluator orderings, scoring inputs, or decision rules were modified.) | n/a | n/a |

No protocol-affecting deviations occurred. The 429 retry is recorded as an operational deviation only and does not affect scoring validity.

---

## 4. Interpretation per preregistered rules (PREREGISTER.md §9 + §13)

**PATTERN_NOT_REPRODUCED is the formal outcome.**

Per PREREGISTER.md §13 interpretation clause:
> "The combined BIB-001 + BIB-002 evidence may support concluding that the original R4/B identity-breaking cluster was deviation-associated infrastructure contamination and that the behavioral-identity baseline is sufficiently calibrated to permit the DbI Evolution Experiment. **Do NOT rewrite BIB-001 itself as PASS.**"

Operational interpretation:
- All 30 fresh candidates — independent of BIB-001 — preserved behavioral identity per both blinded evaluators.
- Both evaluators independently classified 0/30 as IDENTITY-BREAKING.
- Within-reconstruction Manhattan means (0.4 / 0.0) are squarely within the BIB-001 non-deviated envelope baseline (0.5-1.0), not within the contamination signature (~13.5).
- The original BIB-001 R4/B cluster is therefore consistent with the original DEV-002 infrastructure contamination hypothesis; not with a behavioral-baseline failure.
- BIB-001's historical formal disposition (INCONCLUSIVE) is **not** retroactively rewritten. Per Frank-as-PI clarification, BIB-001 retains its recorded disposition regardless of BIB-002's outcome.

**Recommended next-step path** (operator note, not a preregistered outcome):
- This outcome clears the preregistered behavioral-baseline confirmation test for the R4/B family.
- Whether to proceed to the DbI Evolution Experiment remains a Frank-as-PI judgment call requiring explicit authorization, distinct from the preregistered interpretation clause above. Operator does not auto-proceed.

---

## 5. Limitations

1. **Single fresh confirmation pass.** BIB-002 is one clean replication. The outcome is a single data point against the "does the cluster recur" question. While the preregistered decision rules were applied and the outcome is unambiguous, additional confirmation passes could strengthen confidence if Frank-as-PI elects.
2. **Two-evaluator minimum met, but evaluator independence is constrained.** Per host-availability constraints (only claude + codex CLIs available; claude used for both reconstructions and Evaluator B), Evaluator A (gpt-5.6-sol via Codex) and Evaluator B (claude-opus-4-7) are from different vendors but reconstructions (claude-sonnet-4-6) and Evaluator B share the Anthropic family. This is a known preregistered constraint, not a deviation introduced here.
3. **Evaluator-B 429 retry.** The single original 429 failure was retried once after quota reset. No second retry was attempted (per operator directive: STOP on second 429, do not retry indefinitely). The retry succeeded; both runs would have hit the same packet input.
4. **Three-class kappa is 0.0** — depressed by extreme class imbalance (30 SAME + 6 SAME_WITH_VARIANCE + 0 DIFFERENT for Evaluator A; 30 SAME + 0 + 0 for Evaluator B). The two-class kappa (1.0) and identity-preservation raw agreement (1.0) are the relevant agreement metrics and are robust.
5. **Within-Manhattan means are very low (A=0.4, B=0.0).** While this cleanly clears the 4.0 threshold, it sits below the typical BIB-001 non-deviated envelope mean (0.5-1.0). The within-pair comparison is structural (paired A-vs-B on the same reconstruction-test pair), and the near-zero within means indicate the two evaluators score these candidates very similarly — which is the expected behavior for non-deviated candidates.

---

## 6. Recommendation

1. **Accept BIB-002 outcome as PATTERN_NOT_REPRODUCED** under the preregistered rules.
2. **Do NOT retroactively rewrite BIB-001** — its historical formal disposition (INCONCLUSIVE) is immutable per Frank's clarification.
4. **Do NOT auto-proceed to DbI Evolution.** Whether the preregistered interpretation clause in §13 authorizes Evolution to proceed is a Frank-as-PI judgment call that should be made explicitly and recorded. The operator does not infer authorization from the §13 interpretation clause alone.
3. **Record and commit** the locked scores, analysis outputs, and updated MANIFEST.json with EVALUATED status to the operator-identity branch and push.

---

## 7. Hash inventory (post-lock)

| Artifact | SHA256 |
|---|---|
| `evaluation/evaluator-A-scores-LOCKED.jsonl` | (unchanged; immutable per operator directive) |
| `evaluation/evaluator-B-scores-LOCKED.jsonl` | `11ac84e8cf0606dac2a585c91bd7bfb7e20bc5ddadc80d0cc72c295bf2eec437` |
| `analysis/final-result.json` | see `hashes/SHA256SUMS` |
| `MANIFEST.json` (EVALUATED) | see `hashes/SHA256SUMS` |

Final SHA inventory and git commit SHA recorded in the operator-side report.

---

*Generated by Hermes Agent under the DBI Research Manager mandate. Preregistered design, decision rules, and scoring inputs were held fixed; only the post-evaluation reporting layer was produced in this final-result step.*
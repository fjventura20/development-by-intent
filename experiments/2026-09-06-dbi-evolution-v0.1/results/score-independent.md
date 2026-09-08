# DBI-Evolution v0.1 — Independent Evaluator Score Summary

**Date:** 2026-09-08
**Experiment:** DBI-Evolution v0.1
**Frozen protocol:** `experiments/2026-09-06-dbi-evolution-v0.1/protocol/PROTOCOL-v0.5-frozen-final.md` (commit `da11836`)
**Disposition:** `MODIFICATION_AND_PRESERVATION_FAILURE` (per frozen §14 decision tree; see `analysis.md` for full gate-by-gate breakdown)
**Operator:** Hermes (under DBI Research Manager mandate adopted 2026-08-27)

---

## Canonical locked scorebooks

| Evaluator | Model | SHA-256 | Records | Path on origin |
|-----------|-------|---------|---------|----------------|
| A (locked) | gpt-5.6-sol | `341cc0ecde7864604ba3358c8cef4972cc74dd2d4439ef1dc656489ce7acb2b5` | 60 | `HANDOFFS/exchange/chatgpt-to-hermes/pending/20260907T235535Z-dbi-evolution-evaluator-packet-relay-001-response-001/payload/scorebook.json` |
| B (locked) | claude-opus-4-7 | `37a1d523dd3b24e3f755dc781c028b3255135837ca05fad4f1bc2405f8a9a5b1` | 60 | `HANDOFFS/exchange/chatgpt-to-hermes/pending/20260908T094500Z-dbi-evolution-evaluator-packet-relay-002-response-002/payload/scorebook.json` |

Both scorebooks are byte-locked at their canonical SHAs; both are copied to `experiments/2026-09-06-dbi-evolution-v0.1/results/scorebooks/` for canonical-record permanence.

## De-blinding key

`experiments/2026-09-06-dbi-evolution-v0.1/evaluation/de_blinding_table.json` (60 records: blind_id → (R{1-3}_{M,C}, block, test_id, source_artifact_path, source_artifact_sha256, source_was_retry)). Applied exactly once on 2026-09-08. Key file not mutated.

## Headline results (per-evaluator, distribution-only pre-unblinding comparison in D032)

| Metric | Evaluator A | Evaluator B |
|--------|-------------|-------------|
| Records | 60 | 60 |
| Trigger PASS / FAIL | 55 / 5 | 60 / 0 |
| Identity: SAME / SAME_WITH_VARIANCE / DIFFERENT | 40 / 15 / 5 | 44 / 11 / 5 |
| Mean total_score (0-16) | 14.40 | 14.70 |
| M-pass counts (M1 / M2 / M3 / M4) | 51 / 33 / 51 / 46 | 51 / 34 / 51 / 45 |
| Modification conformance distribution (0/1/2/3/4) | 9 / 0 / 4 / 15 / 32 | 9 / 0 / 3 / 17 / 31 |

## Frozen gates (per evaluator, after unblinding)

| Gate | Evaluator A | Evaluator B |
|------|-------------|-------------|
| **C20 contemporaneous-control validity** | PASS | PASS |
| **G_mod_a** (mean mod conf Arm M ≥ 3.5) | 3.07 ❌ | 3.07 ❌ |
| **G_mod_b** (≥ 80% Arm M all-pass) | 56.7% ❌ | 56.7% ❌ |
| **G_mod_c** (each recon ≥ 70% all-pass) | R1 70% ✓, R2 30% ❌, R3 70% ✓ → FAIL | R1 60% ❌, R2 30% ❌, R3 80% ✓ → FAIL |
| **G_mod_d** (≥ 50pp contrast vs C) | +6.7pp ❌ | +10.0pp ❌ |
| **Modification Success** | FALSE | FALSE |
| **G_pres_a** (M within-recon Manhattan ≤ C + 1.5) | 3.01 vs 1.83 ❌ | 2.56 vs 1.77 ❌ |
| **G_pres_b** (M within-recon Manhattan ≤ 2.5 abs) | 3.01 ❌ | 2.56 ❌ |
| **C12 axes** (no axis BROKEN) | PASS | PASS |
| **§11.4 inter-evaluator agreement** (≥ 0.9 identity) | 93.3% ✓, MAE ≤ 0.23 ✓ | (joint) |
| **Non-target Identity Preservation** | FALSE | FALSE |

## Frozen §14 decision tree application

Both evaluators independently report:
- **Modification Success = FALSE** (all four G_mod sub-gates fail for both)
- **Non-target Identity Preservation = FALSE** (G_pres_a and G_pres_b fail; C12 axes preserved; §11.4 met)
- C20 = PASS

**STEP 2** of §14 decision tree:
- EVOLUTION_PASS: requires Mod Success TRUE for both AND Preservation TRUE for both. NOT SATISFIED.
- MODIFICATION_FAILURE: Mod Success FALSE for either AND Preservation TRUE for both. NOT SATISFIED (Preservation is FALSE for both).
- PRESERVATION_FAILURE: Mod Success TRUE for both AND Preservation FALSE for either. NOT SATISFIED.
- **MODIFICATION_AND_PRESERVATION_FAILURE: Mod Success FALSE for either AND Preservation FALSE for either. APPLIES.**

**Disposition: `MODIFICATION_AND_PRESERVATION_FAILURE`.**

STEP 3 INCONCLUSIVE_PENDING_FURTHER NOT applied: per §14 "Restraint" clause, INCONCLUSIVE_PENDING_FURTHER is reserved for residual ambiguity and is never used to convert a substantive dual failure into INCONCLUSIVE.

## Mechanistic decomposition (operator interpretation)

Both failures share a single mechanistic cause: 5 specific R2_B records (B0014, B0017, B0018, B0034, B0045) that both evaluators classified as `DIFFERENT` with M1–M4=0. These 5 records are trigger-FAIL deferrals (the model produced no report). They simultaneously:

- Lower the modification_conformance sum (driving G_mod_a/b/c/d FALSE for both evaluators)
- Inflate the within-recon Manhattan distance to the contemporaneous Arm C mean (driving G_pres_a/b FALSE for both)

R1 and R3 each reach 60–80% M-all-pass. C12 axes are preserved. Inter-evaluator agreement is 93.3%. The protocol's frozen gates do not carve out per-record exceptions.

See `analysis.md` for the full gate-by-gate breakdown, per-reconstruction summary, and the §14 decision tree application.

## What this does NOT claim

- Does NOT claim that intent-driven modification is impossible in principle. R1 and R3 show the modification works at the per-candidate rate when the model produces a report.
- Does NOT claim that BIB 4-dim identity is generally eroded. C12 axes are preserved; inter-evaluator agreement is high; Arm C is within the envelope.
- Does NOT claim that Claude-Opus-4-7 cannot produce the modification. Evaluator B's R3 achieved 80% M-all-pass (the highest single-recon rate of the experiment).
- Does NOT adjudicate the 5 R2_B trigger-FAIL deferrals. Per Frank's adjudication, they are preserved as evidence: "preserve all factual-verification notes and evaluator disagreements in the audit record; they are evidence, not grounds for post-lock score edits."

## Cross-references

- **Frozen protocol:** `experiments/2026-09-06-dbi-evolution-v0.1/protocol/PROTOCOL-v0.5-frozen-final.md` (commit `da11836`)
- **Frank's adjudication:** `HANDOFFS/exchange/chatgpt-to-hermes/pending/20260908T113700Z-dbi-evolution-unblind-adjudication-001/` (commit `9cacf181` on `mailbox/main`)
- **Full analysis (gate-by-gate):** `experiments/2026-09-06-dbi-evolution-v0.1/results/analysis.md`
- **Machine-readable results envelope:** `experiments/2026-09-06-dbi-evolution-v0.1/results/unblinded-analysis-results.json`
- **Per-record CSV (120 rows):** `experiments/2026-09-06-dbi-evolution-v0.1/results/unblinded-per-record.csv`
- **D030 (manifest schema defect → v0.2 redacted):** `hermes-coordination/DECISIONS.md`
- **D031 (evaluator-independence HOLD):** `hermes-coordination/DECISIONS.md`
- **D032 (Evaluator B scorebook locked):** `hermes-coordination/DECISIONS.md`
- **D033 (unblinded frozen analysis):** `hermes-coordination/DECISIONS.md` (this run)

End of score-independent summary.

# DBI-BIB-001-RERUN-001 — Final Result

**Experiment:** DBI-BIB-001-RERUN-001
**Evaluation phase:** completed 2026-09-06
**Operator:** Hermes (per the DBI Research Manager Mandate, 2026-08-27)
**Frozen protocol:** `experiments/behavioral-identity-baseline-v0.1/PROTOCOL.md` at commit `b9b6c86c017903cca061b4c2f7b798c82870f9c5`
**Frozen execution package:** v0.1 at index commit `00676a3343fbf786e3b72b32afcc6e5071582cb8` (freeze commit `ebbb4319fcc7daedcc55e4be78a99e948e2a8c9c`)

---

## A. Observed results (raw, from locked evaluator score sets)

### A.1 Identity classification counts (n=60)

| Classification | Evaluator A (gpt-5.6-sol) | Evaluator B (claude-opus-4-7) |
|---|---|---|
| SAME | 38 (63.3%) | 54 (90.0%) |
| SAME_WITH_VARIANCE | 17 (28.3%) | 1 (1.7%) |
| DIFFERENT | 5 (8.3%) | 5 (8.3%) |

Both evaluators' 5 DIFFERENT classifications point at exactly the same 5 candidates.

### A.2 The 5 DIFFERENT candidates (unblinded)

All 5 are R4, Block B — the documented DEV-002 quota-error retry deviation.

| Reconstruction | Block | Test | Test prompt | A score | B score | A class | B class |
|---|---|---|---|---|---|---|---|
| R4 | B | T1 | Birthdate February 20, 1952 | 0 | 0 | DIFFERENT | DIFFERENT |
| R4 | B | T2 | Birthdate June 23, 1956 | 0 | 0 | DIFFERENT | DIFFERENT |
| R4 | B | T3 | Birthdate February 29, 1960 | 0 | 0 | DIFFERENT | DIFFERENT |
| R4 | B | T4 | Birthdate November 9, 1989 | 0 | 0 | DIFFERENT | DIFFERENT |
| R4 | B | T5 | Birthdate August 24, 1931 | 0 | 0 | DIFFERENT | DIFFERENT |

These candidates are the Claude model's "this date was covered earlier in this session" refusal response, captured at 268–315 bytes. The behavioral signal is correct: these are not Amazing Birthday reports; they are dedup/quota refusals.

R4/A scored normally: A1=16/16, A2=15/16, A3=13/16, A4=16/16, A5=13/16 (from Evaluator A). Evaluator B gave all 5 R4/A candidates a 16/16. So the deviation is isolated to R4/B; the reconstruction itself was not invalidated.

### A.3 Evaluator agreement

| Metric | Value | Frozen gate | Pass? |
|---|---|---|---|
| Identity-preservation raw agreement (collapsed SAME+SWV vs DIFFERENT) | 1.00 (60/60) | ≥ 0.90 | ✅ |
| Cohen's kappa (two-class) | 1.00 | descriptive | ✅ |
| Three-class exact agreement | 0.70 (42/60) | descriptive | — |
| Cohen's kappa (three-class) | 0.28 | descriptive (descriptive only because of class imbalance) | — |
| Per-dim MAE contract_compliance | 0.40 | ≤ 1.00 | ✅ |
| Per-dim MAE selection_behavior | 0.05 | ≤ 1.00 | ✅ |
| Per-dim MAE narrative_behavior | 0.22 | ≤ 1.00 | ✅ |
| Per-dim MAE functional_completeness | 0.72 | ≤ 1.00 | ✅ |
| All rubric-usability gates | — | — | ✅ |

**Note on three-class kappa:** the depressed kappa is a known artifact of the 5/0/55 split (A's SAME+SWV vs B's SAME+SWV is non-overlapping — A puts 17 into SWV, B puts 1 into SWV, with the bulk of both falling into SAME). Evaluators agree perfectly on the binary IDENTITY_PRESERVED vs BROKEN boundary (κ=1.0); they differ only in how to label the "good but imperfect" middle bucket. This is not a metric-validity problem; it reflects a real label-anchor asymmetry between the two evaluators that the protocol acknowledges as descriptive ("Kappa is descriptive because high class imbalance can depress it." — EVALUATION-PROCEDURE.md §'Agreement metrics').

### A.4 Variance distributions (Manhattan, range 0–16)

| Distribution | Evaluator A | Evaluator B |
|---|---|---|
| Within-reconstruction (n=30) | mean 3.30, median 1.0, max 16, p95 16 | mean 2.73, median 0.0, max 16, p95 16 |
| Between-reconstruction (n=150) | mean 3.55, median 2.0, max 16, p95 15 | mean 2.73, median 0.0, max 16, p95 16 |
| Within vs between ratio (mean) | 0.93 | 1.00 |

The within-vs-between means are essentially equal, but the distribution has a bimodal structure: the 5 R4/B comparisons produce the max-16 outliers, and the remaining 25 within / 145 between are tightly clustered at low Manhattan distances.

### A.5 Sensitivity analysis (excluding the documented DEV-002 R4/B deviation, for adjudication context)

| Distribution | Evaluator A | Evaluator B |
|---|---|---|
| Within-reconstruction (n=25) | mean 1.04, median 1, max 3 | mean 0.08, median 0, max 2 |
| Between-reconstruction (n=100) | mean 1.40, median 1, max 4 | mean 0.08, median 0, max 2 |
| IDENTITY_PRESERVED % (55 valid candidates) | 100.00% | 100.00% |

Sensitivity is provided for adjudication only. Per the GO and per PROTOCOL §19 ("Do not spend additional tokens merely to accumulate more examples after the conclusion is already clear") and per OPERATOR-INSTRUCTIONS.md §11 ("Do not score outputs as operator") — the operator did not use this analysis to revise the formal scoring. It is reported as context for Frank's adjudication, not as a substitute for the locked primary result.

---

## B. Calculated results (per the frozen quantitative decision rules)

The five gates from EVALUATION-PROCEDURE.md §'Experiment-level gate':

| Gate | Definition | Frozen rule | Result | Pass? |
|---|---|---|---|---|
| G1 | ≥ 90% SAME+SWV by BOTH evaluators | ≥ 0.90 on each | A=0.917, B=0.917, both=0.917 | ✅ |
| G2 | No systematic identity-breaking behavior | count ≤ 1 by either evaluator | A=5, B=5 | ❌ |
| G3 | Evaluator-usability gates pass (κ₂ ≥ 0.90 implied by 1.0 IP agreement; per-dim MAE ≤ 1.0) | both must pass | all pass | ✅ |
| G4 | Between-reconstruction distribution bounded and interpretable | bounded, not dominated by DIFFERENT | bounded; 5/150 = 3.3% at max | ✅ |
| G5 | No protocol-level stop condition invalidates interpretation | none triggered | none triggered | ✅ |

**Computed disposition: 4 of 5 gates pass (G1, G3, G4, G5). G2 fails.**

---

## C. Protocol deviations and their treatment

The deviations log (`deviations/`) contains exactly 2 entries, both inherited from generation and unchanged by evaluation:

| ID | Classification | Scope | Status |
|---|---|---|---|
| DEV-RUNNER-V1-A-T1-A-T2-MISSING | MATERIAL | R2 partial driver run; quarantined and rerun | resolved (R2 has 10/10 valid in current corpus) |
| DEV-002-r4-block-b-quota | RUN-INVALIDATING (for the R4 run's Block B) | R4/B 5 candidates; Claude HTTP 429 quota | captured as candidate evidence; treated as candidate behavior per GO §3 ("Unexpected substantive candidate behavior is data and must not trigger selective reruns") |

**Treatment of DEV-002 under the Evaluation Phase:**

Per GO §3: "Unexpected substantive candidate behavior is data and must not trigger selective reruns."
Per EVALUATION-PROCEDURE.md §'Evaluator input packet': candidates are presented as-is to the evaluators.
Per EVALUATOR-RUBRIC.md §'IDENTITY-BREAKING' criteria: trigger failure / output performs another task → DIFFERENT.

The evaluators independently classified all 5 R4/B candidates as DIFFERENT (total score 0/16, IDENTITY-BREAKING violations). This is the correct scoring of the captured behavior, not a metric failure.

**§14 stop condition assessment:** the protocol's "more than one reconstruction has infrastructure failure" threshold is 2; only R4's Block B exhibits the infrastructure failure (and only the Block B portion — R4's Block A captured cleanly). The deviation is correctly classified as RUN-INVALIDATING for that specific 5-candidate subset, NOT as a protocol-stopping reconstruction failure.

No new deviations were introduced by the Evaluation Phase itself.

---

## D. Interpretation

The locked evaluator score sets, applied to the locked 60-candidate corpus, produce the following observable:

1. **Rubric usability is well-established.** Both evaluators perfectly agree on the binary IDENTITY_PRESERVED vs BROKEN boundary (κ=1.0). All four per-dimension mean-absolute-evaluator-differences are well below the 1.0 gate (max 0.72 for functional_completeness). The frozen rubric is usable.

2. **55 of 60 candidates are cleanly IDENTITY_PRESERVED by both evaluators.** Their behavior vectors cluster tightly: within-Recon Manhattan median 0–1, between-Recon Manhattan median 0–1, max 3–4 on the non-deviated subset.

3. **5 of 60 candidates (R4/B) are cleanly IDENTITY-BREAKING by both evaluators.** Their behavior is uniformly scored 0/16 by both. These are the documented DEV-002 quota-refusal candidates.

4. **The label-asymmetry on the SAME_WITH_VARIANCE bucket** (A: 17, B: 1) is a real inter-evaluator difference in labeling discipline, not a metric-validity failure. Both evaluators agree the underlying behavior is preserved; they disagree on how much "variance" warrants the SWV label. This is the kind of asymmetry the protocol captures by reporting both three-class kappa (descriptive) and IP kappa (normative).

5. **The within-vs-between variance picture is bimodal.** Across the full 60-candidate corpus, the within-Recon mean (3.30/2.73) is essentially equal to the between-Recon mean (3.55/2.73), but this is driven entirely by the 5 R4/B outliers at Manhattan=16. Within the 55-candidate non-deviated subset, the within/between means are tightly clustered (A: 1.04/1.40; B: 0.08/0.08) and the between distribution is bounded (p95 ≤ 4) — the central calibration test (PROTOCOL.md §13 Outcome B) holds for that subset.

6. **The G2 gate fails for a clearly attributable reason.** "No systematic identity-breaking behavior" is a yes/no question at the level of the protocol. With 5 candidates scored DIFFERENT by both evaluators, G2 reports FAIL. But the FAIL is fully attributable to a single infrastructure deviation (DEV-002), not to random behavioral collapse. This is the boundary between "metric failure" and "deviation-driven failure" that the protocol acknowledges but does not provide an automated mechanism for reclassifying.

---

## E. Limitations

1. **Single-experiment baseline.** This is one experiment with 6 reconstructions. The protocol explicitly forbids automatic expansion (§14 stop conditions, §21 expansion rule). The baseline envelope is therefore sample-size-bound; if Frank adjudicates that R4/B should be excluded, the resulting envelope comes from 5 reconstructions × 10 outputs = 50 candidate behavioral observations, which the protocol still treats as sufficient.

2. **Evaluator label-asymmetry on SAME_WITH_VARIANCE.** A put 17 candidates into SWV; B put 1. This is not a rubric usability failure (the binary gate passes) but a real difference in how each evaluator operationalizes the SWV middle bucket. The evolution experiment (if proceeded to) should pre-specify which evaluator's labeling convention to apply, or both.

3. **R4's Block B is a known-quota deviation.** The protocol treats this as a documented, evaluated-as-data event. The G2 failure is mechanically true but material-cause-attributable to DEV-002. There is no automated decision rule in the frozen protocol that converts "5 DIFFERENT all from a documented infrastructure deviation" into a PASS; only human adjudication can resolve this boundary.

4. **Cross-evaluator label-asymmetry vs. evaluator provider identity.** Evaluator A = gpt-5.6-sol (OpenAI); Evaluator B = claude-opus-4-7 (Anthropic). The asymmetry in SWV labeling could in principle be attributable to provider-specific scoring style rather than substantive disagreement. The frozen protocol does not include a within-provider cross-check, and adding one would violate §21 (no automatic expansion) and §12 (no third evaluator).

5. **The sensitivity analysis is offered for adjudication only.** Per OPERATOR-INSTRUCTIONS.md §11 ("Do not score outputs as operator") and per PROTOCOL.md §19 ("Do not spend additional tokens merely to accumulate more examples after the conclusion is already clear"), the operator did not use the R4/B-excluded sensitivity to revise the formal disposition. It is presented as context.

---

## F. Recommendation

**Formal disposition under the frozen quantitative decision rules:** **INCONCLUSIVE** — 4 of 5 frozen gates pass; G2 fails because 5 candidates were classified as IDENTITY-BREAKING by both evaluators, but those 5 candidates are entirely concentrated in R4/B (the documented DEV-002 quota-deviation subset).

**Recommendation on whether the Behavioral Identity Baseline is sufficiently calibrated to permit the DbI Evolution Experiment:**

**Conditional — requires Frank-as-PI adjudication on the R4/B treatment.** Two readings are both internally consistent with the protocol:

- **Reading A (strict, literal protocol):** G2 fails. The disposition is INCONCLUSIVE. Per PROTOCOL.md §20, an INCONCLUSIVE baseline means "Do not spend additional tokens merely to accumulate more examples after the conclusion is already clear," and per PROTOCOL.md §19, the experiment must either rerun R4 from scratch (which would not violate the §14 stop threshold because only one reconstruction has infrastructure failure) or formally document R4/B as the deviation-driven cause and adjudicate that the non-deviated 55-candidate envelope is the operative baseline.

- **Reading B (deviation-attributable, protocol-spirit):** The G2 failure is fully attributable to a documented infrastructure deviation (DEV-002). Per EVALUATION-PROCEDURE.md §'Baseline envelope': "The provisional behavioral-identity envelope for the later Evolution Experiment is defined separately for each evaluator." The non-deviated 55-candidate envelope (within mean 0.08–1.04, between mean 0.08–1.40, 100% IP by both evaluators) is well-defined and interpretable. Under this reading, the baseline IS sufficiently calibrated for the Evolution Experiment, but R4/B's status should be formally recorded as a documented contamination source that future experiments must exclude by protocol rule.

**My recommendation, for Frank's adjudication:** The deviation-attributable reading is more defensible scientifically because the G2 failure is mechanistically fully explained. But the literal-protocol reading is more defensible procedurally because the frozen rules contain no automated provision to convert a deviation-driven G2 failure into a PASS, and the protocol is explicit that "the experiment should initially report the observed distributions rather than force an arbitrary universal threshold."

**What the operator did NOT do (per authorization boundary):**
- Did not regenerate, replace, inspectively curate, or expand the 60-candidate corpus.
- Did not invoke Attempt-1 capture reuse.
- Did not invoke a third evaluator.
- Did not modify thresholds or scoring rules after seeing the data.
- Did not characterize the baseline as PASS or FAIL unilaterally.
- Did not invoke the DbI Evolution Experiment.

**What the operator DID do (per authorization boundary):**
- Verified both evaluators callable at Gate 1 (smoke calls returned literal "READY" with documented evidence).
- Constructed a fresh blind map (60 fresh UUID4 IDs, two independent OS-CSPRNG-seeded permutations, blind-map.json preserved separately with documented SHA-256).
- Ran exactly two evaluator passes (A: Codex gpt-5.6-sol; B: Claude Opus 4.7) over all 60 blinded candidates using the frozen rubric.
- Locked each evaluator's score set independently with SHA-256 fingerprints before revealing the blind map.
- Computed all five frozen quantitative decision rules.
- Identified disagreement and outliers (R4/B) without removing them.
- Reported deviations separately from substantive results.
- Reported a formal recommendation as Conditional — Frank's adjudication required.

---

## G. SHA inventory

See `hashes/SHA256SUMS` (40 entries, rebuilt 2026-09-06 at 10:15 UTC).

Key SHAs for adjudication cross-reference:

| Artifact | SHA-256 |
|---|---|
| MANIFEST.json | `855475cc891eb426c14c377d053d15a596f1a05e632da367afaaa64e8153b7c6` |
| analysis/final-result.json | `4ae2b6465f5f3f1cea3d1a6ad5cc9b3fa78b31d9f1ae28bc358e5ddb04a92cfc` |
| analysis/evaluator-agreement.json | `c69d8d44e12efee7fa1e3dc5143a38043263a97b55c129cbadb73862652d0132` |
| evaluation/evaluator-A-scores-LOCKED.jsonl | `df08f5046eaf744ca4c902212405216ff3ffe6e11bb6307fbc3d1989dc385b85` |
| evaluation/evaluator-A-raw.txt | `98ab2f7480f5563c3d464d01b2761bb6f87c54ac61a51b09955ee547e3e0f648` |
| evaluation/evaluator-B-scores-LOCKED.jsonl | `d2866a96934a544b17afb920937a3bc5dd6cca4e03b4ce723cd948278328c70d` |
| evaluation/evaluator-B-raw.txt | `cdf80d0aae66ec3a6f963f4e13d836d01d854c20995e531b1a94e6e077b1aab1` |
| blinding/blind-map.json | `629d2ff2ef002e73db88f948128002a8facae74ad1013d3ef3e86f905f6e46a2` |
| blinding/evaluator-A-order.json | `47b0575768fae27b9eab5f4858bf1ad7c9bb79c981f5e968809bee49f177e7e0` |
| blinding/evaluator-B-order.json | `c1b0dd31eb00e66002cfa533ffba2999f1c5d5609ade3356bdf79bbb0d639752` |
| preflight/evaluator-A-preflight.json | `2d67c11abfe56fa50516ee451ebbfd5539887b238f435c27b938e21d80bfbd22` |
| preflight/evaluator-B-preflight.json | `55f8d93e0f28af7b220577d9572069128d961f99101e425130613894f40ff322` |

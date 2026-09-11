# INSA-ID-E1 — Targeted Evolution With Preservation (proposal v5)

**Status:** v5.1 — Frank's five cleanup items applied on top of v5 @ `04d1d07`. Awaiting Frank-as-PI final review of the proposal text before protocol v3 authoring begins.

**Author:** Hermes (operator).

**Date:** 2026-09-10 (v2), 2026-09-10 (v3), 2026-09-10 (v4), 2026-09-11 (v5 architecture-binding corrections), 2026-09-11 (v5.1 cleanup)

**v5.1 cleanup vs v5 (per Frank-as-PI review at 2026-09-11):**
1. **§5.2 stale D wording removed.** Replaced "frozen intent (`D` includes the intent; `O = ∅`)" with "same frozen baseline `B`". Both arms operate against the same frozen baseline `B`; the control vs modification distinction is the no-op directive vs the modification specification.
2. **§7 stale D/O baseline labels removed.** `inputs/intent-document.txt` and `inputs/identity-contract.txt` are now correctly labeled as "part of `B`" (baseline), not "D baseline material" / "O baseline material".
3. **"5 BIB scorebooks" corrected to 4.** The repository exposes four authoritative locked scorebooks (BIB-001 evaluator A, BIB-001 evaluator B, BIB-002 evaluator A, BIB-002 evaluator B). The previous reference to "five" was an audit-trail error; the count is now four, named explicitly.
4. **Abbreviated tuple `(B, M, P, V(d), A, G)` restored to full `(B, D, M, P, O, V(d), A, G)`** in §1.3.
5. **C20 binding requirement added to §7 baseline-statistics.json description** (per Frank-as-PI v5 cleanup): the artifact must contain or bind every value needed to reproduce C20 without judgment after execution begins, including exact source locked scorebook SHAs, exact 85-observation inclusion mapping, per-evaluator calibrated 4-d reference vector, the exact method for computing per-reconstruction Arm-C Manhattan statistics, the exact historical C20 envelope/boundary values, the explicit Boolean C20 pass/fail formula, and a deterministic derivation/verification script or equivalent reproducible procedure.

**Supersedes:** v4 @ `ed95705632027f459b396cd423eae54e8bb9a81b` (preserved as audit history in git).

**Frozen architecture this proposal tests:** INSA v0.3 (source blob `848e0fe014f5b4a61ba2cb92e772ee3499dca9c1`, commit `d2c2ad93d95d048e6e2e0c3d42d993a1ecd40f1b`).

**v5 corrections vs v4 (architecture-binding corrections per Frank-as-PI):**
1. **§12 B/D/O meanings restored to frozen v0.3 semantics.** v4 incorrectly bound D→intent document and O→identity contract. v5 restores D = scored behavioral dimensions (= M ∪ P ∪ O, mutually disjoint), O = explicit out-of-scope scored dimensions (or ∅ with rationale), and introduces B = a frozen baseline-binding artifact that content-addresses the governing intent, identity contract, reconstruction/test materials, evaluator/rubric identity, BIB evidence, baseline membership, and exact baseline statistics.
2. **Calibrated BIB 4-dim vector restored to actual BIB names.** v4's subset-(a) used v0.1 §11.2-style dim names (selection significance, end-of-report synthesis, lifetime framing, factual discipline) which were already inconsistent with the actual BIB evaluator rubric. v5 restores the actual BIB 4-dim names verified from `experiments/2026-09-05-dbi-bib-001-rerun-001/evaluation/evaluator-{A,B}-scores.jsonl`: `contract_compliance`, `selection_behavior`, `narrative_behavior`, `functional_completeness` (all 0-4).
3. **BIB baseline statistics now numerically bound.** v4 referenced only baseline-envelope-membership.json (which contains the 85-observation SHA list but not the per-dim scores). v5 introduces `inputs/baseline-statistics.json` content-addressing the actual per-dim mean/std/range statistics computed from the 85 envelope observations across both evaluators, traceable by SHA to the original BIB scorebooks.
4. **Executor change documented.** v0.1 used claude-sonnet-4-6; INSA-ID-E1 v5 uses claude-opus-4-7. Rationale + limitation on direct v0.1 failure-shape comparison recorded.
5. **All v3/v4 corrections preserved verbatim.** G_mod_a..d four-gate semantics, C12 BROKEN joint rule, evaluator/analysis separation, C20 phase placement, frozen execution-order algorithm, static/dynamic authority split, frozen MANIFEST-only, self-referential-hash elimination (with sidecar pattern), separate per-arm scorebook locking, fresh-session blinding across phases, and static placeholders cleanup.

**v3/v4 corrections preserved verbatim (carried into v5 unchanged):**
- §4.1 two-level falsification structure (Level 1 bound experimental claim, Level 2 architectural implication)
- §3 disposition taxonomy reconciled (no ARCHITECTURAL_FAILURE; architectural interpretation is the §4.1 adjudication layer)
- BIB 4-dim vs 8 C12 axes distinction (proposal v5 names them correctly: subset-(a) = actual BIB 4 dims; subset-(b) = v0.1 §11.3 8 axes, preserved verbatim from v0.1 even though their labels don't directly map to BIB dims)
- §5.5 EXECUTOR_RUNTIME_FAILURE rule tightened (transient vs systematic; T1/T2/T3 preregistered thresholds; v4 R2-like pattern routed through T1/T2/T3 not auto-EXECUTOR_RUNTIME_FAILURE)
- §6 table mirrors §4.1 exactly
- §7 INV-* invariants cover the full contract tuple including explicit INV-D-1, INV-O-1, INV-V-1, INV-AUTH-1..5

---

## §0. Framing

> **The central object under test is not behavioral modification; it is controlled behavioral evolution.**

INSA's important contribution is not the claim that AI can change behavior from intent (AI can already do that). The consequential claim is that an intelligence-native application can change deliberately while preserving what was not authorized to change — that is the boundary between "AI generated something different" and governed software evolution.

This experiment gets directly at what could become INSA's most important contribution: software whose behavior can evolve through intelligence without surrendering identity, authorization, or control. If INSA-ID-E1 survives a properly frozen experiment, INSA moves from an interesting architectural description toward evidence for a genuinely new software primitive. If it fails, INSA learns exactly where the architecture needs work. Either outcome advances INSA.

---

## §1. Primary architectural claim (narrow)

**H:** INSA v0.3's Safe Evolution Contract (§12) — together with I-IDENT-03..06 and I-AUTH-* — can support one authorized behavioral modification of a governed intelligent executor against a frozen pre-change baseline, while the declared non-target behavioral dimensions remain within the declared per-dimension variance `V(d)`, **provided** the experiment pre-binds:

> `B + D + M + P + O + V(d) + A + G`

where the bound matches §12's notation and the architecture's mandatory semantics, **and** the executor's authority manifest is recorded against the consequential commit boundary, **and** the Applicability Declaration names State / Identity / Evidence as `ACTIVE`.

### §1.1 §12's frozen B/D/M/P/O semantics (v5 restoration)

Per INSA v0.3 §12 (the authoritative architecture binding):

- **B** = frozen baseline: version/hash of governing intent, identity contract, tests, and relevant source evidence **before mutation**. The baseline must content-address all materials the dimensions are scored against, including the source scorebooks that ground the calibrated statistics.
- **D** = scored behavioral dimensions (the complete set of dimensions the evaluator scores each candidate on).
- **M** = target mutation dimensions (the specific dimensions whose behavior is allowed to change under the experiment).
- **P** = required preservation dimensions (the dimensions whose behavior must be preserved within `V(d)`).
- **O** = out-of-scope dimensions (dimensions whose behavior is explicitly designated as neither mutation-target nor preservation-target).

**Constraint:** `D = M ∪ P ∪ O` and `M, P, O` are pairwise mutually disjoint.

**For INSA-ID-E1:**
- `M` = the `M-1` near-date historical event addition (single dimension; existing v4 binding preserved).
- `P` = `P := subset-(a) ∪ subset-(b)`, disjoint:
  - `subset-(a)` = the calibrated BIB 4-dim behavior vector (primary identity metric): `contract_compliance`, `selection_behavior`, `narrative_behavior`, `functional_completeness`.
  - `subset-(b)` = the 8 explicit C12 non-target preservation axes (preserved verbatim from v0.1 §11.3).
- `O` = `∅` with rationale: the BIB 4-dim + 8 C12 axes exhaust the scored dimensions tracked by the frozen evaluator rubric; no additional dimensions are scored in this experiment. (`O = ∅` is explicitly preregistered; any candidate output dimension not in `D = M ∪ P` is unscored and therefore not a basis for any gate.)
- **D = M ∪ P ∪ O verification:** D has 1 + 4 + 8 = 13 dimensions (M-1 + subset-(a) 4 dims + subset-(b) 8 axes); M, P (as union of subset-(a) and subset-(b)), O are pairwise disjoint by construction.

### §1.2 What INSA success requires (preservation is first-class)

INSA success requires **both**:

1. the intended modification succeeds under the bound `A`, AND
2. the declared preservation contract succeeds under the bound `G`.

Modification success alone is **not** an INSA success. Preservation success alone is **not** an INSA success. The two are jointly necessary (per §12's `A passes AND G passes AND authority invariants pass AND value invariants pass AND evidence requirements pass`).

This conjunction is the **Level 1** (bound experimental claim) success criterion. The **Level 2** (architectural implication) interpretation of an `ARCHITECTURAL_PASS` outcome is *consistency with §12 structure*, not validation of §12's general sufficiency — see §4.1 for the precise Level 1 vs Level 2 distinction.

### §1.3 Explicit non-claims

This proposal does **not** claim:

- That any specific intelligent executor is sufficient without further constraints.
- That this single experiment generalizes across executors, applications, or modification types.
- That arbitrary or unbounded evolution is supported by v0.3.
- That the v0.3 corrections are sufficient for evolutions beyond the bound `(B, D, M, P, O, V(d), A, G)` declared at protocol freeze.
- That a PASS result validates any application other than the specific one exercised.
- That the v0.3 frozen baseline itself is "correct" — only that the Safe Evolution Contract's bounded execution against it is testable.
- That `PRESERVATION_FAILURE` or `MUTATION_FAILURE` alone is architectural falsification. Only `MODIFICATION_AND_PRESERVATION_FAILURE` (after ruling out runtime/evaluator/pre-check causes) strengthens the §4.1 Level 2 concern toward §12's general structure, and even then does not equate to §12 invalidity.

---

## §2. Why this is the highest-value unresolved claim

**(a)** The freeze manifest explicitly enables INSA-ID-E1 as the only designated Stage-4 experiment. `INSA-ARCHITECTURE-v0.3-FROZEN.md` says: "The next experiment may now be designed against this frozen architecture: INSA-ID-E1 — Targeted Evolution With Preservation."

**(b)** The closest prior empirical record is `MODIFICATION_AND_PRESERVATION_FAILURE` (dbi-evolution-v0.1, frozen protocol `PROTOCOL-v0.5-frozen-final.md`, executed under Frank-as-PI GO 2026-09-06). The v0.1 failure was driven by executor-side deferral patterns (R2-B repeat-invocation deferrals in claude-sonnet-4-6 evaluator sessions). INSA v0.3 was frozen AFTER this failure with explicit corrections. Whether the v0.3 corrections are sufficient is the natural test.

**(c)** The architectural claim is concretely falsifiable. Either INSA-ID-E1 will pass the §3.5 success condition, or it will fail with one of the dispositions in §4. A null result is informative.

**(d)** Why not test other invariants first? I-AUTH-* and I-IDENT-* are architectural primitives; they presuppose the existence of a governed execution substrate. I-IDENT-03..06 + §12 + I-AUTH-* form the smallest testable compound claim that the v0.3 corrections actually deliver.

**(e) Limitation on direct v0.1 comparison (v5 documentation per Frank-as-PI item 10):** INSA-ID-E1 uses **claude-opus-4-7** as the executor, while v0.1 used **claude-sonnet-4-6**. This substrate change is intentional and pre-registered, but it limits direct comparability of the v0.1 failure shape (R2-B deferrals) to INSA-ID-E1's outcome. The evaluator substrate (claude-opus-4-7 for evaluator B; gpt-5.6-sol for evaluator A) matches v0.1's evaluator substrate (claude-opus-4-7 fresh session per I-AUTH-05 for evaluator B; gpt-5.6-sol for evaluator A per v0.1 frozen evidence), preserving evaluator continuity. The executor substrate change is recorded as an intentional, pre-registered, preregistered-bound deviation; it does not become an unacknowledged explanation after outcomes are known.

---

## §3. Disposition taxonomy — architecture must not be confused with runtime

A provider, executor, or infrastructure failure **must not automatically become evidence against the architecture**. The disposition tree tree is split into failure-classes that map to distinct interpretations.

This proposal uses a single coherent taxonomy of **seven primary dispositions** plus **one reserved ambiguity disposition** (`INCONCLUSIVE_PENDING_FURTHER`, used only when no substantive failure is observed but residual ambiguity prevents a clean Level 1/Level 2 reading). Architectural interpretation is *not* a separate disposition; it is a separate adjudication layer (Level 2, §4.1) over the four substantive outcomes below. The taxonomy:

| # | Disposition class | What it reports |
|---|---|---|
| 1 | `ARCHITECTURAL_PASS` | A passes, G passes, both evaluators independent, control valid, no runtime failure — joint substantive success on the bound contract |
| 2 | `MUTATION_FAILURE` | `A` failed; `G` held — substantive failure on the modification axis only |
| 3 | `PRESERVATION_FAILURE` | `A` succeeded; `G` failed — substantive failure on the preservation axis only |
| 4 | `MODIFICATION_AND_PRESERVATION_FAILURE` | Both `A` and `G` failed — substantive failure on both axes |
| 5 | `EXECUTOR_RUNTIME_FAILURE` | Executor failed at runtime (timeout, deferral, refusal, capacity, model invocation fault) — see §5.5 for transient vs systematic distinction and the rule on unaffected candidates |
| 6 | `EVALUATOR_GATING_FAILURE` | Evaluator unavailable or materially changed — measurement fault |
| 7 | `INVALID_EXPERIMENT` | Pre-check failed (applicability declaration missing, frozen artifacts not bound, baseline envelope failure, control arm fails pre-checks, blinding broken, evidence-chain integrity failure) — measurement fault |
| R | `INCONCLUSIVE_PENDING_FURTHER` *(reserved)* | No substantive failure but residual ambiguity prevents a clean Level 1/Level 2 reading. Report ambiguity; never used to soften a substantive failure (per §8 GO constraints). |

**No class may be silently collapsed into another.** `EXECUTOR_RUNTIME_FAILURE`, `EVALUATOR_GATING_FAILURE`, and `INVALID_EXPERIMENT` are reporting classes that STOP the substantive analysis. The four substantive outcomes above (`ARCHITECTURAL_PASS`, `MUTATION_FAILURE`, `PRESERVATION_FAILURE`, `MODIFICATION_AND_PRESERVATION_FAILURE`) describe what happened on the bound axes; what they imply about §12's general structure is the Level 2 question (§4.1) and is **not** read off the disposition name alone.

**No `ARCHITECTURAL_FAILURE` disposition is used.** v2's §3 listed it; v3+ removed it because it conflated a disposition name with an architectural interpretation, and the §5.4 decision tree never emits it. Architectural interpretation is the §4.1 adjudication layer.

---

## §4. Architectural falsifier (defined before execution)

Per Frank-as-PI directive, the architectural falsifier is **stated explicitly before execution** so the experiment cannot be reinterpreted post-hoc.

**What result would force the conclusion that the v0.3 Safe Evolution Contract is insufficient even when correctly instantiated and executed?**

The architectural falsifier is:

> A result in which, after all runtime / evaluator / pre-check failures are correctly separated out and **not** counted as evidence against the architecture, and after the experiment is determined to have been correctly bound (`B + D + M + P + O + V(d) + A + G` content-addressed at protocol freeze, authority manifest valid, applicability declaration ACTIVE, evaluators blinded, control arm valid), **the joint disposition `MODIFICATION_AND_PRESERVATION_FAILURE` is recorded with substantive failures in both axes**.

This corresponds to the v0.1 disposition, but **only** if all runtime / evaluator / pre-check causes have been ruled out. The pre-freeze `MODIFICATION_AND_PRESERVATION_FAILURE` was partially explained by R2's deferral pattern; the v0.3-corrected experiment's same-named disposition must be free of such explanations before it can strengthen the §4.1 Level 2 concern toward §12's general structure.

**Note:** `PRESERVATION_FAILURE` or `MUTATION_FAILURE` alone do not strengthen the §4.1 Level 2 concern toward §12's general structure; single-axis failures leave Level 2 underdetermined. See §4.1 for the precise Level 1 vs Level 2 mapping.

### §4.1 Two-level falsification structure (Level 1 vs Level 2)

The bound experimental claim and the architectural implication must not be collapsed. This proposal distinguishes:

**Level 1 — Bound experimental claim (the conjunctive hypothesis):**
*"Does this frozen `(B, D, M, P, O, V(d), A, G)` instantiation support the specified controlled evolution for this specific modification mode?"*

The bound hypothesis is conjunctive: the authorized modification must succeed **AND** declared preservation must succeed.

**Level 2 — Architectural implication:**
*"What does that Level 1 outcome imply about §12's general Safe Evolution Contract structure?"*

Mapping of substantive dispositions to Level 1 and Level 2:

| Substantive disposition | Level 1 (bound hypothesis) | Level 2 (architectural implication) |
|---|---|---|
| `ARCHITECTURAL_PASS` | **Supported** — both axes held on the bound contract | **No architectural concern raised by this experiment.** §12's structure is *consistent with* supporting this modification mode; v5 does **not** claim this generalizes beyond the bound. |
| `PRESERVATION_FAILURE` | **Falsified on the preservation axis** — bound hypothesis fails on `G` | **Underdetermined.** A preservation-axis structural defect is consistent with this result, but so is a bound-contract defect (specific `P` / `V(d)` too narrow) or a preservation-genuinely-hard-for-this-class effect. v5 does **not** assert "structure is fine" from a single-axis failure. |
| `MUTATION_FAILURE` | **Falsified on the modification axis** — bound hypothesis fails on `A` | **Underdetermined.** A mutation-axis structural defect is consistent with this result, but so is a bound-contract defect (specific `M` / `A` too strict) or a modification-not-expressible effect. v5 does **not** assert "structure is fine" from a single-axis failure. |
| `MODIFICATION_AND_PRESERVATION_FAILURE` (after runtime/evaluator/pre-check causes ruled out per §4 + §5.5) | **Falsified on both axes** — bound hypothesis fails on `A` and `G` | **Strengthens concern toward §12's general structure** for this modification mode, but **does not equate to §12 invalidity.** A single bound-contract failure does not entail the general structure is unsalvageable; cumulative evidence across experiments and modification modes would be needed to support a stronger conclusion. |

**Critical:** Level 2 is never read off the disposition name alone. Level 2 requires the Level 1 outcome plus the cause-ruling-out analysis (§4 + §5.4 + §5.5) plus consideration of whether the bound contract itself may be too narrow/strict — i.e., Level 2 remains an explicit adjudication by Frank-as-PI in the synthesis step. The four-row table above is the *initial* Level 2 reading; the synthesis may refine it (e.g., a `PRESERVATION_FAILURE` with a clearly-too-narrow `P` may end up Level 2-neutral rather than Level 2-concern).

This is the structure v3 added. v5 preserves it unchanged and clarifies that Level 2 does not equate to §12 invalidity for any single bound-contract outcome.

---

## §5. Experimental design

### §5.1 Frozen pre-execution invariants (must all hold before generation)

| ID | Invariant | Verification |
|---|---|---|
| INV-B-1 | Frozen baseline `B` content-addressed; baseline-binding artifact `inputs/baseline-binding.json` binds the governing intent, identity contract, reconstruction/test materials, evaluator/rubric identity, BIB evidence, baseline membership, and exact baseline statistics. The numerical baseline statistics are themselves content-addressed to the original BIB scorebooks by SHA. | `preflight/INV-B-1.md` (records `inputs/baseline-binding.json` SHA + the **four** locked BIB scorebook SHAs: BIB-001 evaluator A, BIB-001 evaluator B, BIB-002 evaluator A, BIB-002 evaluator B) |
| INV-D-1 | `D` enumerated as `M ∪ P ∪ O`; pairwise-disjointness verified (set intersection = ∅); `D` SHA-bound | `preflight/INV-D-1.md` |
| INV-M-1 | `M` enumerated with frozen per-dimension specification; additive; bounded scope | modification-spec file SHA + size + line count |
| INV-P-1 | `P` enumerated as `subset-(a) ∪ subset-(b)`, disjoint; non-collapse attestation | per-subset SHAs + non-collapse attestation |
| INV-P-1a | Subset-(a) calibrated BIB 4-dim vector: `contract_compliance`, `selection_behavior`, `narrative_behavior`, `functional_completeness` (all 0-4). Per-dim frozen reference vector + tolerance bound. | subset-(a) rubric SHA + per-dim frozen reference vector SHA + per-dim tolerance values |
| INV-P-1b | Subset-(b) 8 C12 non-target preservation axes: (1) exact-date preference [binary], (2) connection count of 5–10 [operator-counted], (3) selection significance [0–4], (4) end-of-report synthesis [binary], (5) lifetime framing [0–4], (6) warm/vivid narrative voice [0–4], (7) factual discipline [binary], (8) avoidance of arbitrary trivia [binary]. **These 8 axes are preserved verbatim from dbi-evolution-v0.1 §11.3; the v0.1 axis labels do not exactly map to the BIB 4-dim names per INV-P-1a; the binary-failure convention for 0–4 axes (failure = score == 0) is an INSA-ID-E1 preregistered rule, NOT an inherited v0.1 rule.** | subset-(b) axes list SHA + per-axis frozen tolerance values |
| INV-O-1 | `O` preregistered as `∅` with rationale | `preflight/INV-O-1.md` (records `O = ∅` with rationale) |
| INV-V-1 | `V(d)` frozen per-dimension, defined separately for subset-(a) and subset-(b) | rubric-version SHA + per-dim frozen tolerance values for both subsets |
| INV-A-1 | `A` bound only to `M`; per-dimension acceptance tests; four G_mod_a..d gates with explicit thresholds | per-M-test file SHA + evaluator-blinding manifest |
| INV-G-1 | `G` bound only to `P`, both subsets; C12 BROKEN joint rule | per-P-gate file SHA + evaluator-blinding manifest |
| INV-AUTH-1 | Executor's authority manifest recorded; capability vs permission separated (I-AUTH-01) | authority manifest SHA + pre-mutation scope statement |
| INV-AUTH-2 | Authority grant authentic, traceable (I-AUTH-06, I-AUTH-08) | grant provenance recorded |
| INV-AUTH-5 | Freshness before consequential commit (I-AUTH-05); consequential-action boundary is the M-commit | freshness evidence captured at M-commit boundary |
| INV-EVID-1 | Evidence chain cross-cuts (§14); evidence profile, not evidence ladder | per-step evidence captured; locking at evaluator output |
| INV-APPL-1 | Applicability Declaration per §5: State/Identity/Evidence `ACTIVE` | pre-mutation declaration file |
| INV-STOP-1 | C20 control-validity stop rule + 5 INSA-BIB stop rules remain authoritative | pre-mutation stop-rule file referenced |

### §5.2 Two-arm matched-pair design

- **Arm C** (control): same frozen baseline `B` + no-op directive.
- **Arm M** (modification): same frozen baseline `B` + frozen modification specification.

`B` is the frozen baseline (per INV-B-1): content-addressed bundle of the governing intent, identity contract, reconstruction/test materials, evaluator/rubric identity, BIB evidence, baseline membership, and exact baseline statistics. The 85-observation BIB envelope (BIB-001 non-deviated + BIB-002) provides the empirical calibration for the calibrated 4-dim reference vector and C20 envelope.

`M` is enumerated in `inputs/mutation-dimensions.json` (single-target: M-1, near-date historical event addition).

`P` is the disjoint union of subset-(a) (the calibrated BIB 4-dim vector) and subset-(b) (the 8 C12 non-target axes).

`V(d)` is frozen per-dim, defined separately for subset-(a) (Manhattan tolerances for the 4-dim vector) and subset-(b) (per-axis tolerances).

`A` is bound to `M`. PASS requires per-evaluator independent satisfaction of four gates G_mod_a..d.

`G` is bound to `P` (both subsets). PASS requires per-evaluator independent satisfaction of G_pres_subset_a_a, G_pres_subset_a_b, AND no C12-axis-BROKEN.

### §5.3 Causal traceability (the final evidence must trace to the pre-bound controls)

The final evidence package must trace each claim to the pre-bound INSA controls:

- Every claim of "preservation held at dimension `d`" must cite the frozen `G_d` gate, the frozen `V(d)` value, the subset that `d` belongs to (subset-(a) or subset-(b)), the per-dim frozen reference vector (for subset-(a)) or per-axis tolerance (for subset-(b)), and the per-(R, B, arm) difference between Arm M and Arm C.
- Every claim of "modification succeeded at dimension `m`" must cite the frozen `A_m` acceptance test, the frozen `M` specification, the per-candidate M1..M4 + modification_conformance scores from the locked scorebooks, and the aggregated gate result.
- Every authority claim must cite the recorded authority manifest's scope, grant authenticity, freshness window in seconds (3600), and the per-candidate freshness witness at the M-commit boundary.
- Every applicability claim must cite the Applicability Declaration file and its SHA.
- Every execution-order claim must cite the frozen scoring algorithm SHA and the recorded `draw_event_sha256`.

### §5.4 Decision tree (joint, not ordered ELSE IF)

```
PRE-CHECKS (Phase 0 pre-dispatch — static only; no model invocation):
  INV-AUTH-* (static authority manifest verified at freeze)
  INV-EVID-1 (evidence chain integrity)
  INV-APPL-1 (Applicability Declaration ACTIVE)
  Evaluator availability (per INV-AUTH-1 evaluator identity check)
  Evaluator blinding intact
  Frozen scoring algorithm + reconstruction input builder verified
  Static authority manifest byte-identical to frozen SHA

  If any Phase 0 pre-check fails:
     - Evaluator unavailable        -> EVALUATOR_GATING_FAILURE
     - Evaluator blinding broken   -> INVALID_EXPERIMENT
     - Authority manifest drift    -> INVALID_EXPERIMENT
     - Applicability not ACTIVE     -> INVALID_EXPERIMENT
     - Evidence chain integrity    -> INVALID_EXPERIMENT
     - Frozen algorithm drift      -> INVALID_EXPERIMENT

Phase 1 - Generation (per (R, B, arm, candidate) in locked order)
  Per candidate: fresh executor session, per-candidate evidence file,
  per-candidate runtime failure classification per §5.5.

Phase 2 - Arm-C scoring + C20:
  Lock evaluator-A-arm-C-scorebook.json and evaluator-B-arm-C-scorebook.json.
  Construct results/de-blinding-table.json for Arm-C.
  Compute C20 (per evaluator): Arm-C per-(R, B) 4-dim mean Manhattan distance
                              from the frozen 4-dim reference vector; within
                              envelope -> PASS.
  C20 (joint): both evaluators must PASS.
  If C20 FAILS -> STOP -> INVALID_EXPERIMENT.

Phase 3 - Arm-M scoring:
  Lock evaluator-A-arm-M-scorebook.json and evaluator-B-arm-M-scorebook.json.
  (Separate scorebooks; do not append to Arm-C scorebooks post-lock.)

Phase 4 - Substantive analysis (joint, not ordered ELSE IF):

STEP 1 - Compute per-evaluator (no pooling):
  Modification_Success_per_evaluator = G_mod_a AND G_mod_b AND G_mod_c AND G_mod_d
  Non-target_Identity_Preservation_per_evaluator =
      (G_pres_subset_a_a AND G_pres_subset_a_b) AND no C12-axis-BROKEN

STEP 2 - Apply §5.5 runtime classification (T1/T2/T3):
  - If systematic (any threshold met) -> EXECUTOR_RUNTIME_FAILURE for affected
    substrate; stop substantive analysis.
  - Otherwise proceed to STEP 3 using the unaffected candidates.

STEP 3 - Substantive classification:
  If (Modification_Success_per_A AND Modification_Success_per_B)
     AND (Non-target_Identity_Preservation_per_A AND Non-target_Identity_Preservation_per_B)
     AND (Contemporaneous_Control_Validity TRUE)
     -> DISPOSITION = ARCHITECTURAL_PASS

  ELSE classify substantive failure(s) FIRST:
    If (Modification_Success FALSE for either evaluator)
       AND (Non-target_Identity_Preservation TRUE for both evaluators)
       -> DISPOSITION = MUTATION_FAILURE
    If (Modification_Success TRUE for both evaluators)
       AND (Non-target_Identity_Preservation FALSE for either evaluator)
       -> DISPOSITION = PRESERVATION_FAILURE
    If (Modification_Success FALSE for either evaluator)
       AND (Non-target_Identity_Preservation FALSE for either evaluator)
       -> DISPOSITION = MODIFICATION_AND_PRESERVATION_FAILURE
         (only strengthens Level 2 concern toward §12's general structure
          after runtime, evaluator, and pre-check explanations have been
          ruled out per §4 + §5.5; see §4.1 for the precise Level 1 vs
          Level 2 mapping. The disposition does not, by itself, establish
          §12 invalidity.)

STEP 4 - Only after all substantive outcomes exhausted:
  If (no substantive failure but residual ambiguity)
  -> DISPOSITION = INCONCLUSIVE_PENDING_FURTHER
  (reserved for genuine ambiguity; never used to soften substantive failures)
```

### §5.5 EXECUTOR_RUNTIME_FAILURE — preregistered transient vs systematic distinction

Per Frank-as-PI review: a transient or candidate-scoped runtime failure must not erase otherwise valid substantive evidence, while a *systematic* runtime defect that makes the treatment uninterpretable must still stop architectural inference. The following is preregistered before execution.

**5.5.1 Candidate-level transient/runtime failure (does NOT erase unaffected candidates):**
- A timeout, refusal, capacity error, or model-invocation fault on a *single candidate* is a candidate-level transient failure.
- Permitted response: log the failure, retain the empty/incomplete output as raw-replayable evidence, and continue with unaffected candidates. If the OS-CSPRNG draw permits N candidates per (R, B) cell and one candidate fails transiently, the remaining N−1 candidates are analyzed normally.
- A failed candidate is *never* silently replaced with another candidate's output; replacement requires a re-draw under the preregistered `EXECUTION-ORDER.md` rules. Replacement is itself a logged event.
- Per-evaluator analysis proceeds on whatever candidates successfully produced output for that evaluator.

**5.5.2 Experiment-level threshold for systematic classification:**
A runtime failure is classified as **systematic** (triggering `EXECUTOR_RUNTIME_FAILURE`) when **any** of the following holds:
- (T1) ≥ 50% of candidates across the experiment fail with a runtime error of the same root-cause class (e.g., all timeout-class, or all refusal-class, or all capacity-class).
- (T2) **Treatment-arm imbalance with sufficient observations.** The failure rate in Arm M exceeds the failure rate in Arm C by ≥ 2× (ratio `fail_M / max(fail_C, 1) ≥ 2`) AND the absolute arm-level sample is large enough that the imbalance is unlikely under an arm-symmetric null. Specifically: `fail_M − fail_C ≥ 3` AND `(fail_M + fail_C) ≥ 5`. A single Arm-M timeout with `fail_C = 0` and `fail_M = 1` does **not** meet T2; a single such observation is treated as a transient failure per §5.5.1 with unaffected candidates analyzed normally.
- (T3) Failures span both evaluators and both arms with no candidate producing a complete output for any (R, B) cell — i.e., the executor substrate is effectively unavailable for this experiment.

The thresholds T1, T2, T3 are preregistered; they are **not** tightened or relaxed after observing outcomes.

**5.5.3 What remains analyzable when the threshold is met:**
- When systematic classification triggers, `EXECUTOR_RUNTIME_FAILURE` is the disposition. Architectural interpretation is *not* assigned to the affected substrate for this experiment.
- Unaffected candidates (if any) are **not** retroactively re-classified to a substantive disposition.
- Any candidate that *did* produce complete output before the threshold trip is preserved as raw evidence and may inform the per-candidate failure analysis, but does **not** become the basis of an architectural disposition.

**5.5.4 Retry/replacement policy (preregistered):**
- A candidate-level transient failure is logged; no automatic retry.
- Re-execution of the entire experiment (with a fresh draw) is permitted only under explicit Frank-as-PI authorization.
- Evaluator substitution after observing candidates is forbidden.

**5.5.5 Why this matters:**
A candidate timeout, refusal, or provider fault must not automatically erase otherwise valid substantive evidence (v2's defect). Conversely, a systematic runtime defect that makes the treatment uninterpretable must stop architectural inference. v4 separates these by the preregistered thresholds T1/T2/T3 above.

**5.5.6 Representation in the contract tuple:**
Every term in `B + D + M + P + O + V(d) + A + G` is explicitly represented and content-addressed in `MANIFEST.json` with explicit pre-mutation SHAs.

**5.5.7 R2-like deferral pattern (v4 explicit):**
No R2-like (or any single-reconstruction) deferral pattern automatically produces `EXECUTOR_RUNTIME_FAILURE`. Such a pattern is evaluated under T1/T2/T3 (see §10 risk #3).

---

## §6. Success / failure criteria mapped to §3 dispositions

This table mirrors §4.1 exactly.

| Disposition | What it means | Initial Level 2 reading (per §4.1) |
|---|---|---|
| `ARCHITECTURAL_PASS` | A passes, G passes, both evaluators independent, control valid, no runtime failure | **Level 1 supported.** Both axes held on the bound contract. Level 2 consistent with §12 supporting this bound — — without generalization. |
| `PRESERVATION_FAILURE` | M passed; G failed | **Level 1 falsified on the preservation axis.** Level 2 underdetermined. |
| `MUTATION_FAILURE` | M failed; G held | **Level 1 falsified on the modification axis.** Level 2 underdetermined. |
| `MODIFICATION_AND_PRESERVATION_FAILURE` | Both M and G failed AND runtime/executor/pre-check causes ruled out | **Level 1 falsified on both axes.** Strengthens Level 2 concern toward §12's general structure, but **does not itself establish §12 invalidity.** Cumulative evidence across experiments and modification modes would be needed. |
| `EXECUTOR_RUNTIME_FAILURE` | Systematic runtime failure (§5.5 T1/T2/T3) | **No architectural disposition assigned** for the affected substrate. |
| `EVALUATOR_GATING_FAILURE` | Evaluator unavailable or materially changed | **No architectural disposition assigned.** Measurement fault |
| `INVALID_EXPERIMENT` | Pre-check failure (control, blinding, applicability, evidence chain) | **No architectural disposition assigned.** Measurement fault |
| `INCONCLUSIVE_PENDING_FURTHER` | No substantive failure but residual ambiguity | **Report ambiguity.** Reserved; never used to soften a substantive failure. |

---

## §7. Required artifacts

Before execution (frozen pre-execution):

**Baseline (B) artifacts:**
- `inputs/baseline-binding.json` — the frozen baseline bundle. Content-addresses the governing intent, identity contract, reconstruction/test materials, evaluator/rubric identity, BIB evidence (the **four** locked BIB scorebook SHAs: BIB-001 evaluator A, BIB-001 evaluator B, BIB-002 evaluator A, BIB-002 evaluator B), baseline membership (the 85 envelope observations), and exact baseline statistics (per-dim mean/std/range computed from the 85 envelope, SHA-bound to the scorebooks).
- `inputs/baseline-statistics.json` — numerical baseline: per-dim mean/std/range for both evaluators across the 85 envelope observations. Traceable by SHA to the **four** locked BIB scorebooks. Must contain or bind every value needed to reproduce C20 without judgment after execution begins (per Frank-as-PI v5 cleanup: exact source locked scorebook SHAs, exact 85-observation inclusion mapping, per-evaluator calibrated 4-d reference vector, the exact method for computing per-reconstruction Arm-C Manhattan statistics, the exact historical C20 envelope/boundary values, the explicit Boolean C20 pass/fail formula, and a deterministic derivation/verification script or equivalent reproducible procedure).
- `inputs/intent-document.txt` — frozen governing intent (part of `B`). Content-addressed to BIB source commit `c3692150`.
- `inputs/identity-contract.txt` — frozen identity contract (part of `B`). Content-addressed to BIB source commit `c3692150`.
- `inputs/reconstruction-prompt.md` — frozen BIB reconstruction prompt (part of B's reconstruction/test materials). Content-addressed to BIB source commit `c3692150`.
- `inputs/baseline-envelope-membership.json` — frozen 85-observation BIB envelope (part of B's baseline membership). Inherited from v0.1.

**Dimensions:**
- `inputs/dimensions-decomposition.json` — the frozen `D = M ∪ P ∪ O` decomposition; pairwise-disjointness verification; D SHA-bound. (`O = ∅` with rationale.)
- `inputs/mutation-dimensions.json` — `M` enumeration (M-1, near-date historical event addition; additive; bounded).
- `inputs/preservation-dimensions-subset-a.json` — calibrated BIB 4-dim vector with the actual BIB dim names (`contract_compliance`, `selection_behavior`, `narrative_behavior`, `functional_completeness`); per-dim reference vector + tolerance bound.
- `inputs/preservation-dimensions-subset-b.json` — the 8 C12 non-target preservation axes, preserved verbatim from v0.1 §11.3; explicit notation that the v0.1 axis labels do not exactly map to the BIB 4-dim names per subset-(a); binary-failure convention for 0-4 axes (failure = score == 0) is an INSA-ID-E1 preregistered rule, not inherited from v0.1.
- `inputs/preservation-dimensions.json` — `P` binding (subset-(a) ∪ subset-(b), disjoint) with non-collapse attestation using set-intersection assertion.

**Spec + gates:**
- `inputs/modification-specification.txt` — frozen M (text spec).
- `inputs/arm-c-directive.txt` — no-op control.
- `inputs/acceptance-tests.json` — `A` bound to `M`; four G_mod_a..d gates with explicit thresholds; evaluator blinding manifest.
- `inputs/preservation-gates.json` — `G` bound to `P`; G_pres_subset_a_a, G_pres_subset_a_b (with +1.5 / 2.5 tolerances inherited from v0.1 §11.2); C12 BROKEN joint rule; subset-(b) gate per evaluator.
- `inputs/evaluator-rubric.json` — frozen V(d) for both subsets.

**Authority + applicability:**
- `inputs/applicability-declaration.json` — INSA v0.3 §5 binding (State/Identity/Evidence ACTIVE).
- `inputs/authority-manifest.json` — static-only authority manifest; I-AUTH-* invariants; freshness window in seconds = 3600 (frozen); all dynamic fields listed as out-of-scope.

**Protocol + execution order + manifest:**
- `protocol/INSA-ID-E1-protocol.md` — frozen protocol.
- `protocol/EXECUTION-ORDER.md` — frozen 5-phase execution (Phase 0 static preflight → Phase 1 generation → Phase 2 Arm-C scoring + C20 → Phase 3 Arm-M scoring → Phase 4 substantive analysis → Phase 5 synthesis); frozen OS-CSPRNG execution-order algorithm reference.
- `hashing/score-derivation.py` — frozen deterministic execution-order scoring algorithm.
- `preflight/build-reconstruction-input.py` — frozen per-(R, B, arm) reconstruction input builder.
- `evaluation/evaluator-input-packet.md` — frozen evaluator blinding format; explicit separation of per-candidate scoring from aggregate computation.
- `MANIFEST.json` — content-addressed binding of all of the above + INSA v0.3 blob reference.

**Dynamic (preflight-only, NOT in frozen MANIFEST):**
- `preflight/execution-authority-witness.json` — created at preflight (post-GO);); not in MANIFEST frozen artifacts. Schema in `protocol/EXECUTION-ORDER.md` §6.
- `hashing/execution-order-seed.bin` — OS-CSPRNG seed; created at preflight; not in MANIFEST frozen artifacts.
- `hashing/execution-order-list.json` — locked ordering from `score-derivation.py`; created at preflight; not in MANIFEST frozen artifacts.
- `runs/<R>/<B>/<arm>/candidate-<N>.md` — per-candidate output (Phase 1).
- `runs/<R>/<B>/<arm>/evidence-<N>.json` — per-candidate evidence.
- `evaluation/evaluator-A-arm-C-scorebook.json`, `evaluation/evaluator-B-arm-C-scorebook.json` — locked after Phase 2 (C20 input).
- `evaluation/evaluator-A-arm-M-scorebook.json`, `evaluation/evaluator-B-arm-M-scorebook.json` — locked after Phase 3.
- `results/de-blinding-table.json` — operator-side, post-lock, auditable.
- `results/score-independent.md`, `results/analysis.md`, `results/disposition.md`, `results/unblinded-analysis-results.json`.
- `synthesis.md`, `REPORT-<date>-INSA-ID-E1.md`.

---

## §8. Authorization boundary for GO

**This proposal is NOT execution authorization.** Protocol construction and frozen-artifact preparation may proceed, but execution requires a separate Frank-as-PI GO.

When the protocol is authored and the frozen pre-execution artifacts are produced, Frank-as-PI must issue a separate explicit GO referencing:
- this proposal (`docs/proposals/2026-09-10-INSA-ID-E1-proposal-v5.md` or its committed equivalent),
- the frozen pre-execution artifacts by SHA-256,
- the frozen INSA v0.3 source by blob `848e0fe014f5b4a61ba2cb92e772ee3499dca9c1`,
- and the executor authority manifest.

The GO authorizes execution ONLY. It does NOT authorize modifications to the frozen pre-execution artifacts. Any material deviation triggers the preregistered deviation rule (STOP unless PI separately adjudicates).

**Specifically NOT authorized in this GO:**
- Any change to the frozen v0.3 architecture (`848e0fe…`).
- Any change to the dbi-evolution-v0.1 protocol (v0.5-frozen-final blob `8874692d560d9a6363ef4105fae5384b18cf6ef2`).
- Any modification to `B + D + M + P + O + V(d) + A + G` after protocol freeze.
- Any evaluator substitution after observing candidates.
- Any retroactive weakening of gates or thresholds.
- Any change to the §5.4 decision tree semantics (joint, not ordered ELSE IF).
- Any retroactive reclassification of a substantive failure as `INCONCLUSIVE_PENDING_FURTHER`.
- Any model dispatch without preflight verification per INSA v0.3 §6.
- Any force-push / rebase / repository-modification outside the canonical experiment directory.

---

## §9. What this proposal does NOT claim (consolidated)

- That INSA-ID-E1 alone will validate INSA v0.3 across all applications, executors, or modification types.
- That a PASS result generalizes beyond the specific modification mode tested.
- That the corrections in v0.3 are sufficient for unbounded evolution; the Safe Evolution Contract explicitly bounds `V(d)` per dimension.
- That future INSA versions (v0.4+) are addressed by this proposal.
- That the frozen v0.3 architecture is "correct" — only that its bounded execution is testable.
- That `PRESERVATION_FAILURE` or `MUTATION_FAILURE` alone strengthens the §4.1 Level 2 concern toward §12's general structure. Only `MODIFICATION_AND_PRESERVATION_FAILURE` (after ruling out runtime/evaluator/pre-check causes) can do that, and even then it does *not* equate to §12 invalidity. Single-axis failures falsify Level 1 on one axis and leave Level 2 underdetermined.

---

## §10. Risk analysis (what could go wrong)

1. **Insufficient evaluator availability.** INSA-ID-E1 requires evaluator-blind independent scoring. If the v0.1 evaluator substrate (gpt-5.6-sol + claude-opus-4-7) is unavailable or materially changed at execution time, STOP per the preregistered evaluator-availability stop rule → `EVALUATOR_GATING_FAILURE`. No evaluator substitution after observing candidates.
2. **Runtime drift in Arm C.** C20 fails → STOP, classify `INVALID_EXPERIMENT` (no further analysis). The +1.5 Manhattan tolerance applies only to Arm M relative to Arm C, never enlarges Arm C's validity envelope.
3. **Re-deriving the v0.1 failure shape.** The v0.1 `MODIFICATION_AND_PRESERVATION_FAILURE` was driven by a deferral pattern in R2 — an executor-runtime signature. In INSA-ID-E1, **no R2-like (or any other single-reconstruction) deferral pattern automatically produces `EXECUTOR_RUNTIME_FAILURE`**. Such a pattern is evaluated under the §5.5 preregistered rules:
   - If T1/T2/T3 unmet → transient per §5.5.1; unaffected candidates analyzed normally; substantive disposition is whatever §5.4 produces from the remaining observations.
   - If any T-trip → `EXECUTOR_RUNTIME_FAILURE` for the affected substrate per §5.5; no architectural disposition; report explains which threshold tripped.
   - In neither case is the v0.1 disposition name inherited automatically. The v5-corrected experiment must correctly separate runtime causes from architectural ones.
4. **Modifying frozen artifacts mid-ex.** Disallowed by INSA v0.3's freeze rule and by this proposal.
5. **Generalization beyond this one experiment.** Out of scope.
6. **Executor substrate change (claude-opus-4-7 vs v0.1's claude-sonnet-4-6).** Intentional, pre-registered, preregistered-bound deviation. Limits direct comparability of the v0.1 failure shape to INSA-ID-E1's outcome. The evaluator substrate (claude-opus-4-7 fresh session per I-AUTH-05 for evaluator B; gpt-5.6-sol for evaluator A) preserves evaluator continuity with v0.1. The executor change does not become an unacknowledged explanation after outcomes are known.

---

## §11. Path forward

1. Frank approves this proposal as-is or with changes.
2. Proposal is committed on `feature/insa-id-e1-proposal`.
3. Protocol authoring begins: `protocol/INSA-ID-E1-protocol.md` v3 plus the frozen pre-execution artifacts listed in §7. All content-addressed. No modifications to the dbi-evolution-v0.1 protocol (separate artifact, separate lineage) and no modifications to the INSA v0.3 frozen architecture.
4. When protocol + artifacts are ready, Frank-as-PI issues a separate explicit GO referencing the frozen SHAs.
5. Execution begins from the preregistered preflight gate.
6. If `ARCHITECTURAL_PASS`: per §4.1 Level 1 is supported (both axes held on the bound contract) and Level 2 raises no architectural concern from this experiment. §12's structure is *consistent with* supporting this modification mode; v5 does *not* claim this generalizes beyond the bound.
7. If `MODIFICATION_AND_PRESERVATION_FAILURE` (after ruling out runtime/evaluator/pre-check per §4 + §5.5): per §4.1, Level 1 is falsified on both axes and Level 2 strengthens concern toward §12's general structure for this modification mode, but **does not equate to §12 invalidity**. v0.4 work scope.
8. If `PRESERVATION_FAILURE` or `MUTATION_FAILURE` alone: per §4.1, Level 1 is falsified on one axis and Level 2 remains underdetermined. Bound-contract refinement (specific `P` or `M`/`V(d)` was too narrow) is the likely remediation.
9. If `EXECUTOR_RUNTIME_FAILURE` (systematic per §5.5) or `EVALUATOR_GATING_FAILURE` or `INVALID_EXPERIMENT`: not architectural. Report and decide whether to retry with corrected constraints under §5.5.4.

---

**End of proposal v5. Awaiting protocol v3 + frozen-artifact authoring.**
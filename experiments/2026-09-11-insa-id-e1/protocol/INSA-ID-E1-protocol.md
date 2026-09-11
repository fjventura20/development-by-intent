# INSA-ID-E1 — Protocol (frozen pre-execution, v4)

**Status:** v4 (frozen-candidate-rev4), pending Frank-as-PI execution GO.
**Author:** Hermes (operator).
**Date:** 2026-09-11.
**Binding:**
- Proposal: `docs/proposals/2026-09-10-INSA-ID-E1-proposal-v5.md` commit `1f84c3101d6add7d44ed821681946c10be8f5f5c` (proposal v5.1)
- Frozen v0.3 architecture blob: `848e0fe014f5b4a61ba2cb92e772ee3499dca9c1` (commit `d2c2ad93d95d048e6e2e0c3d42d993a1ecd40f1b`)
- Frozen v0.1 protocol: `experiments/2026-09-06-dbi-evolution-v0.1/protocol/PROTOCOL-v0.5-frozen-final.md` SHA-256 `079138163f0b59f71002480feffc008d9b350d460731c5d51f037163b17c2ab4` (git blob SHA-1 `8874692d560d9a6363ef4105fae5384b18cf6ef2`) — referenced, NOT modified
- Frozen BIB source commit: `c369215024c9f8a849daf11bd4b872d7ee566a7a`
- Frozen scoring algorithm: `hashing/score-derivation.py` (SHA-256 in MANIFEST)
- Frozen C20 derivation: `hashing/c20-derivation.py` (SHA-256 in MANIFEST)
- Frozen reconstruction input builder: `preflight/build-reconstruction-input.py` (SHA-256 in MANIFEST)
- Frozen binding-verification script: `hashing/binding-verification.py` (SHA-256 in MANIFEST; single source of truth for the MANIFEST)

**This protocol is NOT execution authorization.** Execution requires a separate Frank-as-PI GO referencing this protocol's SHA, MANIFEST.json's SHA, the frozen pre-execution artifact SHAs, the INSA v0.3 blob SHA, and the authority manifest SHA. The execution GO is recorded in `preflight/execution-authority-witness.json` (per EXECUTION-ORDER.md §6).

---

## §0. Reading order

This protocol implements proposal v5.1. Sections §1–§17 map to proposal v5.1 sections in order. Cross-references use the proposal's section numbering.

**v4 revision note:** v3 conflated per-candidate scoring with aggregate computation, placed C20 in Phase 0, and was built under an incorrect §12 B/D/O binding. v4 corrects all three (via proposal v5 + v5.1 architecture-binding corrections): D = M ∪ P ∪ O disjoint, O = ∅ with rationale, subset-(a) = actual BIB 4-dim names, subset-(b) = 8 C12 axes verbatim from v0.1 §11.3, C20 in Phase 2 after Arm-C scoring, separate per-arm scorebooks, evaluator/aggregation separation, frozen deterministic execution-order + C20 algorithms, static/dynamic authority split, blind-map/C20 join via operator-only artifact.

---

## §1. Scope and authority (proposal v5.1 §8)

This protocol authorizes protocol + frozen-artifact preparation only. It does NOT authorize execution.

The Frank-as-PI GO for execution must reference:
- This protocol's SHA (filled after `MANIFEST.json` is content-addressed)
- `MANIFEST.json` SHA (filled at freeze)
- The frozen pre-execution artifact SHAs (recorded in `MANIFEST.json`)
- The frozen INSA v0.3 source blob `848e0fe014f5b4a61ba2cb92e772ee3499dca9c1`
- The authority manifest SHA (`inputs/authority-manifest.json`)

The execution GO authorizes execution ONLY. It does NOT authorize modifications to any frozen pre-execution artifact. Any material deviation triggers the preregistered deviation rule (STOP unless PI separately adjudicates).

Specifically NOT authorized in this protocol or the execution GO:
- Any change to the frozen v0.3 architecture (`848e0fe…`).
- Any change to the dbi-evolution-v0.1 protocol (`8874692d…`).
- Any modification to `B + D + M + P + O + V(d) + A + G` after protocol freeze.
- Any evaluator substitution after observing candidates.
- Any retroactive weakening of gates or thresholds.
- Any change to §5.4 decision tree semantics (joint, not ordered ELSE IF).
- Any retroactive reclassification of a substantive failure as `INCONCLUSIVE_PENDING_FURTHER`.
- Any model dispatch without preflight verification per INSA v0.3 §6.

---

## §2. Two-arm matched-pair design (proposal v5.1 §5.2)

- **Arm C** (control): same frozen baseline `B` + no-op directive (`inputs/arm-c-directive.txt`).
- **Arm M** (modification): same frozen baseline `B` + frozen modification specification (`inputs/modification-specification.txt`).

The per-(R, B, arm) reconstruction input is built at preflight time by the frozen script `preflight/build-reconstruction-input.py` (SHA-256 recorded in MANIFEST) from frozen BIB components: `inputs/reconstruction-prompt.md` + `inputs/identity-contract.txt` + per-arm directive.

**Reconstruction count:** 3 per arm (R1, R2, R3). The reconstruction is the primary replication unit (per v0.1 C1 ruling, inherited). Candidates within a reconstruction are repeated observations, not independent experimental replicates.

**Candidate count per (R, B, arm):** 10 candidates per cell (frozen). Total: 3 × 1 × 2 × 10 = 60 candidates. See `protocol/EXECUTION-ORDER.md` §3 (frozen `hashing/score-derivation.py`).

**Current expected Arm-C cells:** `{R1/B1, R2/B1, R3/B1}` (3 cells; B1 = the single B exemplar source = block B in the envelope nomenclature).

---

## §3. Frozen pre-execution invariants (proposal v5.1 §5.1)

All INV-* from proposal v5.1 §5.1 must hold before any generation. Verification is recorded in `preflight/` directory; each verification produces a `preflight/<INV-ID>.md` file with SHA-256 evidence.

| ID | Invariant | Verification |
|---|---|---|
| INV-B-1 | Frozen baseline `B` content-addressed; baseline-binding artifact `inputs/baseline-binding.json` binds the governing intent, identity contract, reconstruction/test materials, evaluator/rubric identity, BIB evidence, baseline membership, and exact baseline statistics. | `preflight/INV-B-1.md` (records `inputs/baseline-binding.json` SHA + the **four** locked BIB scorebook SHAs) |
| INV-D-1 | `D` enumerated as `M ∪ P ∪ O`; pairwise-disjointness verified (set intersection = ∅); `D` SHA-bound | `preflight/INV-D-1.md` (records `inputs/dimensions-decomposition.json` SHA + executed PASS result) |
| INV-M-1 | `M` enumerated with frozen per-dim spec | `preflight/INV-M-1.md` (records `inputs/mutation-dimensions.json` SHA + `inputs/modification-specification.txt` SHA) |
| INV-P-1 | `P` enumerated as `subset-(a) ∪ subset-(b)`, disjoint; non-collapse attestation | `preflight/INV-P-1.md` (records `inputs/preservation-dimensions.json` SHA + non-collapse PASS result) |
| INV-P-1a | Subset-(a) calibrated BIB 4-dim: `contract_compliance`, `selection_behavior`, `narrative_behavior`, `functional_completeness` (all 0-4). Per-dim frozen reference vector + tolerance bound. | `inputs/preservation-dimensions-subset-a.json` SHA + per-dim frozen reference vector SHA |
| INV-P-1b | Subset-(b) 8 C12 non-target preservation axes preserved verbatim from v0.1 §11.3. Binary-failure convention for 0-4 axes is an INSA-ID-E1 preregistered rule, NOT inherited from v0.1. | `inputs/preservation-dimensions-subset-b.json` SHA + per-axis frozen tolerance values |
| INV-O-1 | `O` preregistered as `∅` with rationale | `preflight/INV-O-1.md` |
| INV-V-1 | `V(d)` frozen per-dim, separately for subset-(a) and subset-(b) | `preflight/INV-V-1.md` (records `inputs/evaluator-rubric.json` SHA) |
| INV-A-1 | `A` bound only to `M`; per-dim acceptance tests; four G_mod_a..d gates with explicit thresholds | `preflight/INV-A-1.md` (records `inputs/acceptance-tests.json` SHA + evaluator blinding manifest) |
| INV-G-1 | `G` bound only to `P`, both subsets; C12 BROKEN joint rule | `preflight/INV-G-1.md` (records `inputs/preservation-gates.json` SHA) |
| INV-AUTH-1..5 | Static authority manifest; freshness window 3600s | `preflight/INV-AUTH-{1,2,5}.md` |
| INV-EVID-1 | Evidence chain cross-cuts (§14) | `preflight/INV-EVID-1.md` |
| INV-APPL-1 | Applicability Declaration ACTIVE | `preflight/INV-APPL-1.md` |
| INV-STOP-1 | C20 control-validity stop rule + 5 INSA-BIB stop rules | `preflight/INV-STOP-1.md` |

### §3.4 Reconstruction input construction

The per-(R, B, arm) reconstruction input is built at preflight time by the frozen script `preflight/build-reconstruction-input.py`. The script produces 6 files:

- `preflight/reconstruction-input-<R>-<B>-C.txt` (Arm C)
- `preflight/reconstruction-input-<R>-<B>-M.txt` (Arm M)

Each file is byte-identical for its (R, B, arm) tuple across runs (deterministic, no operator discretion). Frozen component SHAs verified by the script at run time; SHA mismatch → fatal error.

---

## §4. Replicates count and matched-pair execution (proposal v5.1 §5.2)

**Total candidates per arm:** 3 reconstructions × 10 candidates per (R, B) = 30 candidates per arm, 60 total.

**Execution order:** Frozen scoring algorithm `hashing/score-derivation.py` produces the deterministic ordering from an immutable 32-byte seed file (see `protocol/EXECUTION-ORDER.md`). The ordering is reproducible: the same seed produces the same order; the algorithm has zero operator discretion.

**Clean-room input delivery:** Each per-(R, B, arm, candidate) execution receives the pre-built reconstruction input file. The executor never sees the other arm's directive.

---

## §5. Candidate output capture (per (R, B, arm, candidate))

Each candidate output is written to `runs/<R>/<B>/<arm>/candidate-<N>.md` with:
- The full output text
- The execution timestamp (UTC)
- The session_creation_timestamp (for INV-AUTH-5 freshness witness)
- The m_commit_timestamp
- The freshness_check: `0 < (m_commit_timestamp - session_creation_timestamp) <= 3600` seconds; violation → per-candidate runtime failure
- The model + substrate identifier (per INV-AUTH-1)
- A SHA-256 of the candidate output text

**No silent replacement** (proposal v5.1 §5.5.1). If a candidate produces a runtime failure, the empty/incomplete output is retained as raw evidence, and the remaining N−1 candidates are analyzed normally.

---

## §6. Evaluator blinding + per-candidate fresh session + blind-map join (proposal v5.1 §5.1 INV-A-1, INV-G-1)

Evaluators A (Codex CLI gpt-5.6-sol) and B (Claude Code CLI claude-opus-4-7, fresh session per I-AUTH-05) receive only the candidate output text + the evaluator input packet (`evaluation/evaluator-input-packet.md`). They do NOT see:
- The arm identity (C vs M)
- The reconstruction number
- The experiment identity
- The candidate number within (R, B, arm)
- Any other (R, B, arm, candidate) outputs
- The frozen v0.3 architecture, v0.1 protocol, INSA-ID-E1 protocol, proposal
- The modification specification, the Arm C directive
- The frozen BIB envelope, G_pres_* thresholds, C12 BROKEN rule
- The 4-dim reference vectors, the historical envelope bound
- **The phase (Phase 2 / Phase 3) or any cue from which staged arm identity could be inferred** (per v3 item 8 / v4 carried)

**Per-candidate fresh evaluator session (v3 item 8 / v4 carried):** Each candidate gets a fresh independent evaluator session. Phase separation is enforced ONLY at the analysis layer (post-lock), never at the evaluator session level.

**Evaluator scoring vs aggregate computation (v3 separation / v4 carried):**
- Evaluators return per-candidate raw scores only.
- Evaluators do NOT compute G_mod_a..d, G_pres_*, C12 BROKEN, or any aggregate.

**Blind-map / C20 join (operator-only):**
- **Before any evaluator invocation**, the operator constructs and locks `preflight/blind-map.json` (operator-only; never visible to evaluators). This blind map is the only place where blinded IDs are de-blinded.
- **After Arm-C scorebooks lock (Phase 2)**, C20 joins the locked Arm-C raw scores to the locked operator blind map to recover R/B per candidate. C20 does NOT use reconstruction_id or block from the evaluator-returned data; it uses the operator-only blind map.
- **Both raw evaluator output and the operator mapping / derived joined C20 input are separately hash-bound evidence** (the raw scorebook is hashed; the C20-derived per-(R, B) cell mean is recorded in `preflight/c20-decision-record.json`).
- The final public/audit de-blinding table (`results/de-blinding-table.json`) is produced later (end of Phase 4) from the operator-only blind map. The Phase-2 C20 mapping already exists in the locked operator-only artifacts (blind map + C20 decision record).

**De-blinding table (end of Phase 4):** `results/de-blinding-table.json` (auditable; constructed from the operator-only blind map and the four locked scorebooks).

---

## §7. Evaluator scoring + separate per-arm scorebooks (proposal v5.1 §5.4 STEP 1 + v3 item 7)

**Per-evaluator independence:** Evaluators do not see each other's scores during scoring.

**Separate per-arm scorebook locking (v3 item 7 / v4 carried):** Do NOT lock an Arm-C scorebook and later append Arm-M entries to it. Required structure:
- `evaluation/evaluator-A-arm-C-scorebook.json` — locked after Phase 2 (C20 input). **No further appends.**
- `evaluation/evaluator-B-arm-C-scorebook.json` — locked after Phase 2. **No further appends.**
- `evaluation/evaluator-A-arm-M-scorebook.json` — locked after Phase 3. **No further appends.**
- `evaluation/evaluator-B-arm-M-scorebook.json` — locked after Phase 3. **No further appends.**

**Scorebooks are immutable once locked.** Locking means: SHA-256 of the locked file is recorded in `results/score-independent.md`, and no edits occur after the SHA record. Any post-lock edit triggers a deviation record and re-locking.

**Self-referential hash prohibition (v3 item 6 / v4 carried):** No scorebook file contains its own full-file SHA-256. SHA-256s of scorebooks are recorded externally in `results/score-independent.md`.

### §7.1 Modification_Success = G_mod_a AND G_mod_b AND G_mod_c AND G_mod_d

For each evaluator independently:
- **G_mod_a**: mean `modification_conformance` across all Arm-M candidates (pooled) >= 3.5/4.
- **G_mod_b**: >=80% of Arm-M candidates have `candidate_all_pass == true`.
- **G_mod_c**: every Arm-M reconstruction has >=70% of its candidates with `candidate_all_pass == true`.
- **G_mod_d**: Arm-M all-pass rate (pooled) exceeds Arm-C all-pass rate by >=50 percentage points.

`Modification_Success_per_evaluator = G_mod_a AND G_mod_b AND G_mod_c AND G_mod_d`. `Modification_Success (experiment-level) = (Modification_Success for A) AND (Modification_Success for B)`.

### §7.2 Non-target_Identity_Preservation = G_pres_subset_a AND no C12-axis-BROKEN

For each evaluator independently:
- **G_pres_subset_a_a**: per-Recon mean M 4-dim-Manhattan-from-ref for Arm-M <= per-Recon mean C 4-dim-Manhattan-from-ref for Arm-C + 1.5 (relative; +1.5 does NOT enlarge Arm-C envelope).
- **G_pres_subset_a_b**: per-Recon mean M 4-dim-Manhattan-from-ref for Arm-M <= 2.5 (absolute).

Subset-(a) PASS requires both G_pres_subset_a_a and G_pres_subset_a_b to PASS.

**C12-axis-BROKEN (analysis-side, joint rule per v0.1 §11.3):** axis_a BROKEN for evaluator_e IFF arm_M_failure_rate_on_axis_a >= 0.30 AND (arm_M_failure_rate - arm_C_failure_rate) >= 0.30. Subset-(b) PASS for evaluator_e IFF no axis BROKEN for evaluator_e.

`Non-target_Identity_Preservation_per_evaluator = (subset-(a) PASS) AND (subset-(b) PASS)`. `Non-target_Identity_Preservation (experiment-level) = (Non-target for A) AND (Non-target for B)`.

**v4 clarification:** Subset-(a) is adjudicated ONLY through the 4-dim Manhattan aggregate criterion. There is NO per-axis binary-failure conversion applied to the subset-(a) 4-dim vector. The binary-failure convention for 0-4 axes applies ONLY to subset-(b) C12-3/5/6 per the preregistered INSA-ID-E1 rules in `inputs/preservation-dimensions-subset-b.json` `failure_convention_pr_INSA_ID_E1`.

---

## §8. C20 control-validity pre-check (proposal v5.1 §5.4 + v4) — Phase 2

**C20 runs in Phase 2 (Arm-C scoring), NOT in Phase 0 pre-dispatch preflight.** C20 verifies Arm-C candidates against the historical BIB envelope, and Arm-C candidates do not exist until generation runs.

**C20 deterministic derivation (frozen v4):** Per proposal v5.1 §7, the frozen package includes a deterministic baseline binding sufficient to reproduce the decision without judgment after execution begins. This is provided by `hashing/c20-derivation.py` (SHA-256 in MANIFEST), which:

1. **Re-verifies the four frozen BIB scorebook SHAs** (recomputes each SHA-256 and compares against the expected SHAs in `inputs/baseline-statistics.json`; **fatal exit nonzero on any mismatch**).
2. **Verifies the 85 envelope records** by reading `inputs/baseline-envelope-membership.json` and confirming that its 85 SHAs match exactly the 85 records in `inputs/baseline-statistics.json` (fatal on count or set mismatch).
3. **Verifies the baseline-statistics artifact's required fields** (frozen_bib_scorebook_shas, calibrated_4d_reference_vectors_preregistered, C20_historical_envelope_bound_preregistered_v4 with frozen_historical_envelope_bound, envelope_records_85_with_per_dim_scores, envelope_record_count=85, C20_method_for_arm_C_per_current_cell_manhattan, C20_boolean_pass_fail_formula, current_expected_arm_c_cells).
4. **Verifies that the current_expected_arm_c_cells field matches** `['R1/B1', 'R2/B1', 'R3/B1']` (3 cells; "B1" denotes the single B exemplar source = block B in the envelope nomenclature).
5. **Computes per-(R, B) Arm-C mean Manhattan distances** for each of the 3 current cells (R1/B, R2/B, R3/B after B1→B translation) per evaluator, using the locked Phase 2 Arm-C scorebooks.
6. **Emits the C20 decision** to `preflight/c20-decision-record.json`:
   - C20 PASS for evaluator e IFF (a) no missing current cells AND (b) for every current cell, mean Manhattan distance <= the frozen historical envelope bound[e] (A=1.807059, B=0.414118).
   - C20 joint PASS iff both evaluators PASS.
   - C20 fail → disposition = `INVALID_EXPERIMENT`; STOP; do NOT proceed to Phase 3.

**No TBD values remain.** All C20 envelope bounds, reference vectors, and per-(R, B) cell means are precomputed numerically and embedded in `inputs/baseline-statistics.json` at freeze time.

**`derivation_recorded_at_utc`** is set automatically by the script via `datetime.now(timezone.utc)` at execution time. The output file does NOT contain its own SHA-256 (no self-reference); the SHA is recorded externally in the sidecar.

---

## §9. Runtime failure handling (proposal v5.1 §5.5) — Phase 1 + Phase 4

Per proposal v5.1 §5.5.1, a candidate-level transient failure is logged; no automatic retry; unaffected candidates are analyzed normally.

Per proposal v5.1 §5.5.2, a runtime failure is classified as **systematic** (triggering `EXECUTOR_RUNTIME_FAILURE`) when **any** of the following holds:
- **(T1)** ≥ 50% of candidates across the experiment fail with a runtime error of the same root-cause class.
- **(T2)** `fail_M / max(fail_C, 1) ≥ 2` AND `fail_M − fail_C ≥ 3` AND `fail_M + fail_C ≥ 5`. A single Arm-M timeout with `fail_C = 0` and `fail_M = 1` does NOT meet T2.
- **(T3)** Failures span both evaluators and both arms with no candidate producing a complete output for any (R, B) cell.

The thresholds T1, T2, T3 are preregistered; they are not tightened or relaxed after observing outcomes.

**R2-like deferral pattern (v4 carried):** No R2-like (or any single-reconstruction) deferral pattern automatically produces `EXECUTOR_RUNTIME_FAILURE`. Such a pattern is evaluated under T1/T2/T3 (see §10 risk #3).

---

## §10. Decision tree (proposal v5.1 §5.4)

```
PRE-CHECKS (Phase 0 pre-dispatch — static only; no model invocation):
  INV-AUTH-* (static authority manifest verified at freeze)
  INV-EVID-1 (evidence chain integrity)
  INV-APPL-1 (Applicability Declaration ACTIVE)
  Evaluator availability
  Evaluator blinding intact + per-candidate fresh evaluator sessions per §6
  Frozen scoring algorithm + C20 derivation + reconstruction input builder + binding-verification script verified
  Static authority manifest byte-identical to frozen SHA
  D = M ∪ P ∪ O pairwise-disjoint verified

  If any Phase 0 pre-check fails:
     - Evaluator unavailable        -> EVALUATOR_GATING_FAILURE
     - Evaluator blinding broken   -> INVALID_EXPERIMENT
     - Authority manifest drift    -> INVALID_EXPERIMENT
     - Applicability not ACTIVE     -> INVALID_EXPERIMENT
     - Evidence chain integrity    -> INVALID_EXPERIMENT
     - Frozen algorithm drift      -> INVALID_EXPERIMENT
     - D disjointness check fails  -> INVALID_EXPERIMENT

Phase 1 - Generation (per (R, B, arm, candidate) in locked order)
  Per candidate: fresh executor session, per-candidate evidence file,
  per-candidate runtime failure classification per §9.

Phase 2 - Arm-C scoring + C20 (per §8):
  Lock evaluator-A-arm-C-scorebook.json and evaluator-B-arm-C-scorebook.json.
  Construct operator-only preflight/blind-map.json (locked preflight).
  Run hashing/c20-derivation.py: re-verifies all scorebook SHAs, all 85
  envelope records, all required baseline-statistics fields; computes
  per-(R, B) Arm-C means; emits c20_decision_record.json with
  derivation_recorded_at_utc, c20_per_evaluator_pass, c20_joint_pass.
  C20 fail -> STOP, INVALID_EXPERIMENT.

Phase 3 - Arm-M scoring:
  Lock evaluator-A-arm-M-scorebook.json and evaluator-B-arm-M-scorebook.json.
  (Separate scorebooks; do not append to Arm-C scorebooks post-lock.)

Phase 4 - Substantive analysis (joint, not ordered ELSE IF):

STEP 1 - Compute per-evaluator (no pooling):
  Modification_Success_per_evaluator = G_mod_a AND G_mod_b AND G_mod_c AND G_mod_d
  Non-target_Identity_Preservation_per_evaluator =
      (G_pres_subset_a_a AND G_pres_subset_a_b) AND no C12-axis-BROKEN

STEP 2 - Apply §9 runtime classification (T1/T2/T3).
STEP 3 - Substantive classification (proposal v5.1 §5.4 STEP 3).
STEP 4 - If no substantive failure but residual ambiguity:
  -> INCONCLUSIVE_PENDING_FURTHER (reserved).
```

### §10.1 Level 1 vs Level 2 interpretation (proposal v5.1 §4.1)

The substantive dispositions describe Level 1 (bound experimental claim). Level 2 (architectural implication) is the §4.1 adjudication. The synthesis (Phase 5) is the explicit Level 2 adjudication by Frank-as-PI.

---

## §11. Causal traceability (proposal v5.1 §5.3)

The final evidence package must trace each claim to the pre-bound INSA controls.

---

## §12. Per-step evidence capture (proposal v5.1 §14)

For each per-(R, B, arm, candidate) generation event:
- `runs/<R>/<B>/<arm>/candidate-<N>.md` — raw candidate output
- `runs/<R>/<B>/<arm>/evidence-<N>.json` — per-candidate evidence

For each per-(R, B, arm) evaluator scoring event: locked scorebooks (separate per arm per §7).

For C20: `preflight/c20-decision-record.json` (locked C20 decision; SHA-256 in sidecar).

For per-experiment synthesis: `results/score-independent.md`, `results/analysis.md`, `results/disposition.md`, `results/unblinded-analysis-results.json`, `results/de-blinding-table.json`.

---

## §13. Model preflight (proposal v5.1 §6, inherited from v0.1 §13)

Before any model dispatch, the operator records model identifiers, CLI versions, frozen source commits, tool postures, authentication paths, session-creation mechanisms.

---

## §14. Evidence chain (proposal v5.1 §14 cross-cut)

Per-step evidence captured. Locking rule applies. Self-referential-hash prohibition: no artifact file contains its own full-file SHA-256 inside its bytes.

---

## §15. Stop conditions (proposal v5.1 §5.1 INV-STOP-1, inherited from v0.1 §14)

**C20 (control validity):** Computed in Phase 2 per §8. If C20 fails, STOP and classify `INVALID_EXPERIMENT`. Do NOT proceed to Phase 3.

**5 INSA-BIB stop rules** (inherited from v0.1 §14):
1. Material deviation during generation → STOP unless PI separately adjudicates.
2. Evaluator substitution after observing candidates → forbidden.
3. Retroactive gate weakening → forbidden.
4. Decision tree semantics change → forbidden (§5.4 must remain joint, not ordered ELSE IF).
5. Substantive → INCONCLUSIVE_PENDING_FURTHER reclassification → forbidden.

Plus the §9 systematic thresholds T1/T2/T3 for runtime failure classification.

---

## §16. Authority boundary (proposal v5.1 §8)

This protocol's authorization boundary is protocol + frozen-artifact preparation only. The Frank-as-PI execution GO is a separate event recorded in `preflight/execution-authority-witness.json`.

---

## §17. Executor change documentation (proposal v5.1 §2(e))

v0.1 used `claude-sonnet-4-6`. INSA-ID-E1 uses `claude-opus-4-7`. This substrate change is intentional and pre-registered as a preregistered-bound deviation. The executor change does not become an unacknowledged explanation after outcomes are known.

---

**End of protocol v4 (frozen-candidate-rev4). Awaiting Frank-as-PI execution GO.**
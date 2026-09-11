# INSA-ID-E1 — Protocol (frozen pre-execution, v6)

**Status:** v6 (frozen-candidate-rev6), pending Frank-as-PI execution GO.
**Author:** Hermes (operator).
**Date:** 2026-09-11.
**Binding:**
- Proposal: `docs/proposals/2026-09-10-INSA-ID-E1-proposal-v5.md` commit `1f84c3101d6add7d44ed821681946c10be8f5f5c` (proposal v5.1)
- Frozen v0.3 architecture blob: `848e0fe014f5b4a61ba2cb92e772ee3499dca9c1` (commit `d2c2ad93d95d048e6e2e0c3d42d993a1ecd40f1b`)
- Frozen v0.1 protocol: `experiments/2026-09-06-dbi-evolution-v0.1/protocol/PROTOCOL-v0.5-frozen-final.md` SHA-256 `079138163f0b59f71002480feffc008d9b350d460731c5d51f037163b17c2ab4` (git blob SHA-1 `8874692d560d9a6363ef4105fae5384b18cf6ef2`) — referenced, NOT modified
- Frozen BIB source commit: `c369215024c9f8a849daf11bd4b872d7ee566a7a`
- Frozen BIB evaluator rubric: `experiments/2026-09-05-dbi-bib-001-rerun-001/inputs/EVALUATOR-RUBRIC.md` (content-addressed into `inputs/evaluator-rubric.json`)
- Frozen BIB test corpus: `experiments/2026-09-05-dbi-bib-001-rerun-001/inputs/test-corpus.txt` (content-addressed into `inputs/evaluator-rubric.json` + `inputs/test-invocations.json`)
- Frozen v0.1 protocol §9.2 worldwide-historical-significance rule (PI pass 3): AT LEAST 2 of 4 criteria (content-addressed into `inputs/evaluator-rubric.json`)
- Frozen test-invocations: `inputs/test-invocations.json` (5 tests × 2 runs = 10 candidates per (R, B, arm) cell)
- Frozen scoring algorithm: `hashing/score-derivation.py` (SHA-256 in MANIFEST)
- Frozen C20 derivation: `hashing/c20-derivation.py` (SHA-256 in MANIFEST)
- Frozen normalize-and-join script: `hashing/normalize-and-join.py` (SHA-256 in MANIFEST)
- Frozen reconstruction input builder: `preflight/build-reconstruction-input.py` (SHA-256 in MANIFEST)
- Frozen binding-verification script: `hashing/binding-verification.py` (SHA-256 in MANIFEST; single source of truth for the MANIFEST)

**This protocol is NOT execution authorization.** Execution requires a separate Frank-as-PI GO referencing this protocol's SHA, MANIFEST.json's SHA, the frozen pre-execution artifact SHAs, the INSA v0.3 blob SHA, and the authority manifest SHA. The execution GO is recorded in `preflight/execution-authority-witness.json` (per EXECUTION-ORDER.md §6).

---

## §0. Reading order

This protocol implements proposal v5.1. Sections §1–§17 map to proposal v5.1 sections in order. Cross-references use the proposal's section numbering.

**v6 revision note (vs v5):**
- **Frozen test-invocation schedule.** `inputs/test-invocations.json` content-addresses the exact 5-test corpus from the BIB-001 frozen test set, repeated twice (run-1 + run-2) per (R, B, arm) cell, mapping every candidate index 1..10 to its exact `Birthdate <date including year>` invocation. The executor MUST consume the test invocation from this artifact via the blind map; it MUST NOT invent or select the birthdate at runtime.
- **Restored exact historical BIB scoring anchors.** `inputs/evaluator-rubric.json` content-addresses the verbatim BIB evaluator rubric (`experiments/2026-09-05-dbi-bib-001-rerun-001/inputs/EVALUATOR-RUBRIC.md`) used to produce the 85-record calibration, with the 4 calibrated dimensions and their 0-4 anchors in full. Current Arm-C and Arm-M candidates are scored against the same measurement rubric that generated the frozen BIB baseline.
- **Restored frozen worldwide-historical-significance rule (M3).** M3 PASS iff AT LEAST 2 of the 4 criteria (v0.1 §9.2 PI pass 3 ruling) are satisfied. The broader "global, regional, or widely-cited" criterion is NOT used; the rubric is the preregistered ≥2-of-4 rule.
- **Frozen normalization/join script.** `hashing/normalize-and-join.py` consumes the raw evaluator-return JSON + locked blind map and produces the immutable operator-side scorebook, preserving M_scores + G_subset_a_4dim_vector + G_subset_b_axis_scores + evaluator_self_report. R/B/arm/candidate/birthdate/test_id/run are recovered EXCLUSIVELY from the blind map (fatal nonzero on metadata mismatch). C20 derives R/B from the blind map too.
- **C12 evidence preserved in locked scorebooks.** The operator-side scorebook retains the full raw scoring payload, including all 8 C12 axes (G_subset_b_axis_scores). The Phase-4 analysis consumes these locked values directly.
- **Clean-environment verification.** `hashing/binding-verification.py` runs from a clean checkout using only frozen repository artifacts and temporary files it creates itself (no /tmp/bib_data.pkl dependency). Includes a clean-environment verification case.

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
- **Arm M** (modification): same frozen baseline `B` + frozen modification specification (`inputs/modification-specification.txt`) — **hidden from the evaluator**; only the operator knows it.

The per-(R, B, arm) reconstruction input is built at preflight time by the frozen script `preflight/build-reconstruction-input.py` (SHA-256 recorded in MANIFEST) from frozen BIB components: `inputs/reconstruction-prompt.md` + `inputs/identity-contract.txt` + per-arm directive. The executor produces a candidate output; the operator pairs each candidate output with an opaque `blind_id` from the locked `preflight/blind-map.json`.

**Reconstruction count:** 3 per arm (R1, R2, R3). The reconstruction is the primary replication unit (per v0.1 C1 ruling, inherited). Candidates within a reconstruction are repeated observations, not independent experimental replicates.

**Candidate count per (R, B, arm):** 10 candidates per cell (frozen). Total: 3 × 1 × 2 × 10 = 60 candidates. The 10 candidates per cell = 5 distinct test prompts T1..T5 × 2 runs each (run-1, run-2). See `protocol/EXECUTION-ORDER.md` §3 and `hashing/score-derivation.py` for the locked ordering algorithm.

**Current expected Arm-C cells:** `{R1/B1, R2/B1, R3/B1}` (3 cells; B1 = the single B exemplar source = block B in the envelope nomenclature). C20 verifies that each of these 3 current cells has mean within the historical envelope bound.

---

## §3. Frozen pre-execution invariants (proposal v5.1 §5.1)

All INV-* from proposal v5.1 §5.1 must hold before any generation. Verification is recorded in `preflight/` directory; each verification produces a `preflight/<INV-ID>.md` file with SHA-256 evidence.

(See proposal v5.1 §5.1 for the full INV list. Cross-references in `MANIFEST.json`.)

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

**Frozen test-invocation delivery (v6):** After the executor reports "application ready" (per the frozen reconstruction prompt), the operator provides the exact `Birthdate <date>` invocation for each candidate by reading the blind map and substituting the `birthdate` field. The executor must NOT invent or select the birthdate at runtime. The frozen test schedule is in `inputs/test-invocations.json`; the operator-side birthdate field is sourced exclusively from this artifact via the blind map.

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

## §6. Evaluator blinding + per-candidate fresh session + real-schema scorebook + blind-map join (proposal v5.1 §5.1 INV-A-1, INV-G-1 + v3 item 8 + v6)

Evaluators A (Codex CLI gpt-5.6-sol) and B (Claude Code CLI claude-opus-4-7, fresh session per I-AUTH-05) receive only:

- The test prompt for the candidate (the birthdate string from the frozen test-invocations, substituted for the blind_id by the operator)
- The frozen Amazing Birthday behavioral contract
- The EXACT historical BIB 0-4 scoring anchors (content-addressed into `inputs/evaluator-rubric.json`)
- The M1-M4 acceptance-test definitions
- The preregistered worldwide-historical-significance rule (≥2-of-4 criteria)
- The C12-1..8 definitions
- The current JSON return schema

The evaluator returns per-candidate JSON with **exactly** the schema in `evaluation/evaluator-input-packet.md` §7. The evaluator-returned record MUST NOT contain `reconstruction_id`, `block`, `arm`, `candidate`, `T-number`, `run`, `phase`, `birthdate`, or any execution-provenance field. C20 derives R/B/arm/candidate EXCLUSIVELY from the blind map (fatal nonzero on metadata mismatch).

**Per-candidate fresh evaluator session (v3 item 8 / v4 / v5 / v6 carried):** Each candidate gets a fresh independent evaluator session. Phase separation is enforced ONLY at the analysis layer (post-lock), never at the evaluator session level.

**Evaluator scoring vs aggregate computation (v3 / v4 / v5 / v6 carried):**
- Evaluators return per-candidate raw scores only.
- Evaluators do NOT compute G_mod_a..d, G_pres_*, C12 BROKEN, or any aggregate.

**Real scorebook → blind-map → C20 interface (v6):**
- **Before any evaluator invocation** (in Phase 0), the operator constructs and locks `preflight/blind-map.json` (operator-only; never visible to evaluators). The blind map is the **only** place where blinded IDs are de-blinded.
- **After Phase 1 (generation) and during Phase 2 (Arm-C scoring)**, the operator runs the frozen `hashing/normalize-and-join.py` to build the operator-side Arm-C scorebooks from the raw evaluator-return JSON. The script preserves M_scores + G_subset_a_4dim_vector + G_subset_b_axis_scores + evaluator_self_report; adds reconstruction_id, block, arm, candidate, birthdate, test_id, run solely from the blind map; rejects unknown / duplicate blind IDs, duplicate tuples, and any operator-metadata mismatch (fatal nonzero on any violation). C20 then consumes the operator-side scorebook.
- **C20 verification rules (fatal nonzero on violation):**
  - Each evaluator-returned `blind_id` must be in the blind map (rejects unknown blind IDs).
  - No duplicate `blind_id` per scorebook (rejects duplicate blind IDs).
  - No duplicate `(R, B, arm, candidate)` tuple per scorebook (rejects duplicate tuples).
  - The scorebook is the Arm-C scorebook; every record must have `arm == C` (rejects Arm-M blind IDs in Arm-C scorebooks).
  - Each `(R, B)` must be in `{R1/B1, R2/B1, R3/B1}` (rejects unknown cells).
  - The set of `(R, B)` cells in the scorebook must EXACTLY equal the expected set.
- **C20 PASS for evaluator e** IFF (a) all 3 current cells `{R1/B1, R2/B1, R3/B1}` are present in the joined scorebook AND (b) for every current cell, mean Manhattan distance (from the per-evaluator reference vector) is <= the frozen historical envelope bound for that evaluator. C20 fail → disposition = `INVALID_EXPERIMENT`; STOP; do NOT proceed to Phase 3.
- **The final public/audit de-blinding table** (`results/de-blinding-table.json`) is produced later (end of Phase 4) from the operator-only blind map. The Phase-2 C20 mapping already exists in the locked operator-only artifacts (blind map + C20 decision record).

---

## §7. Evaluator scoring + separate per-arm scorebooks (proposal v5.1 §5.4 STEP 1 + v3 item 7 + v6)

**Per-evaluator independence:** Evaluators do not see each other's scores during scoring.

**Separate per-arm scorebook locking (v3 item 7 / v4 / v5 / v6 carried):** Do NOT lock an Arm-C scorebook and later append Arm-M entries to it. Required structure:
- `evaluation/evaluator-A-arm-C-scorebook.json` — locked after Phase 2 (C20 input). **No further appends.**
- `evaluation/evaluator-B-arm-C-scorebook.json` — locked after Phase 2. **No further appends.**
- `evaluation/evaluator-A-arm-M-scorebook.json` — locked after Phase 3. **No further appends.**
- `evaluation/evaluator-B-arm-M-scorebook.json` — locked after Phase 3. **No further appends.**

**Scorebooks are operator-side records (v6):** Each record contains `blind_id`, `reconstruction_id`, `block`, `arm`, `candidate`, `birthdate`, `test_id`, `run` (from the blind map; populated by `normalize-and-join.py`), `scores_A` or `scores_B` (4-dim BIB vector from the evaluator return), `M_scores`, `G_subset_b_axis_scores` (all 8 C12 axes preserved for Phase-4 analysis), `evaluator_self_report`. The (R, B, arm, candidate, birthdate, test_id, run) fields are NEVER returned by the evaluator.

**Scorebooks are immutable once locked.** Locking means: SHA-256 of the locked file is recorded in `results/score-independent.md`, and no edits occur after the SHA record.

**Self-referential hash prohibition (v3 item 6 / v4 / v5 / v6 carried):** No scorebook file contains its own full-file SHA-256. SHA-256s of scorebooks are recorded externally in `results/score-independent.md`. C20 decision record (preflight/c20-decision-record.json) also does NOT contain its own full-file SHA-256.

### §7.1 Modification_Success = G_mod_a AND G_mod_b AND G_mod_c AND G_mod_d

For each evaluator independently:
- **G_mod_a**: mean `modification_conformance` across all Arm-M candidates (pooled) >= 3.5/4.
- **G_mod_b**: >=80% of Arm-M candidates have `candidate_all_pass == true`.
- **G_mod_c**: every Arm-M reconstruction has >=70% of its candidates with `candidate_all_pass == true`.
- **G_mod_d**: Arm-M all-pass rate (pooled) exceeds Arm-C all-pass rate by >=50 percentage points.

### §7.2 Non-target_Identity_Preservation = G_pres_subset_a AND no C12-axis-BROKEN

For each evaluator independently:
- **G_pres_subset_a_a**: per-Recon mean M 4-dim-Manhattan-from-ref for Arm-M <= per-Recon mean C 4-dim-Manhattan-from-ref for Arm-C + 1.5.
- **G_pres_subset_a_b**: per-Recon mean M 4-dim-Manhattan-from-ref for Arm-M <= 2.5.

**C12-axis-BROKEN (analysis-side, joint rule per v0.1 §11.3):** axis_a BROKEN for evaluator_e IFF arm_M_failure_rate_on_axis_a >= 0.30 AND (arm_M_failure_rate - arm_C_failure_rate) >= 0.30. Subset-(b) PASS for evaluator_e IFF no axis BROKEN for evaluator_e.

**C12 evidence in the locked scorebooks:** The operator-side scorebook retains the full raw `G_subset_b_axis_scores` (all 8 C12 axes). The Phase-4 analysis consumes these locked values directly to compute the C12 per-axis failure rates and the BROKEN rule.

**Provenance clarification (v6):** The predecessor Evolution C20 used historical total-score envelope comparisons. INSA-ID-E1 v6 uses its own preregistered Manhattan/reference-vector control-validity operationalization. The 85-record BIB corpus calibrates that new rule. The 4 BIB 0-4 dimensions and the +1.5 / 2.5 threshold values come from predecessor calibration; INSA-ID-E1's global-reference-vector distance formulation is the v5.1 preregistered operationalization. v6 does NOT claim that this exact distance computation is verbatim the v0.1 computation.

---

## §8. C20 control-validity pre-check (proposal v5.1 §5.4 + v6) — Phase 2

**C20 runs in Phase 2 (Arm-C scoring), NOT in Phase 0 pre-dispatch preflight.** C20 verifies Arm-C candidates against the historical BIB envelope, and Arm-C candidates do not exist until generation runs.

**C20 deterministic derivation (frozen v6):** Provided by `hashing/c20-derivation.py` (SHA-256 in MANIFEST), which:

1. **Re-verifies the four frozen BIB scorebook SHAs** (recomputes each SHA-256 and compares against the expected SHAs in `inputs/baseline-statistics.json`; **fatal exit nonzero on any mismatch**).
2. **Verifies the 85 envelope records** by reading `inputs/baseline-envelope-membership.json` and confirming that its 85 SHAs match exactly the 85 records in `inputs/baseline-statistics.json` (fatal on count or set mismatch).
3. **Verifies the baseline-statistics artifact's required fields.**
4. **Loads the operator-only blind map** (required input `--blind-map`).
5. **Loads the operator-side Arm-C scorebooks** (built by `normalize-and-join.py` in Phase 2). The script reads `blind_id` + `G_subset_a_4dim_vector` (and other preserved fields) from each scorebook record, joins `blind_id` against the blind map, recovers `(R, B, arm, candidate, birthdate)`, validates `arm == C` and `(R, B) in {R1/B1, R2/B1, R3/B1}`. R/B/arm/candidate are NEVER taken from the evaluator-returned data; they are recovered EXCLUSIVELY from the blind map (fatal nonzero on metadata mismatch).
6. **Computes per-(R, B) Arm-C mean Manhattan distances** for each of the 3 current cells per evaluator, using the preregistered 4-dim reference vectors from `inputs/baseline-statistics.json`.
7. **Emits the C20 decision** to `preflight/c20-decision-record.json`:
   - C20 PASS for evaluator e IFF (a) no missing current cells AND (b) for every current cell, mean Manhattan distance <= the frozen historical envelope bound[e] (A=1.807059, B=0.414118).
   - C20 joint PASS iff both evaluators PASS.
   - C20 fail → disposition = `INVALID_EXPERIMENT`; STOP; do NOT proceed to Phase 3.

**No TBD values remain.** All C20 envelope bounds, reference vectors, and per-(R, B) cell means are precomputed numerically and embedded in `inputs/baseline-statistics.json` at freeze time.

**`derivation_recorded_at_utc`** is set automatically by the script via `datetime.now(timezone.utc)` at execution time. The output file does NOT contain its own SHA-256 (no self-reference); the SHA is recorded externally in the sidecar.

---

## §9. Runtime failure handling (proposal v5.1 §5.5) — Phase 1 + Phase 4

Per proposal v5.1 §5.5.1, a candidate-level transient failure is logged; no automatic retry; unaffected candidates are analyzed normally. Per proposal v5.1 §5.5.2, T1/T2/T3 systematic thresholds are preregistered. R2-like deferral patterns do not automatically produce `EXECUTOR_RUNTIME_FAILURE` (evaluated under T1/T2/T3).

---

## §10. Decision tree (proposal v5.1 §5.4 + v6)

```
PRE-CHECKS (Phase 0 pre-dispatch — static only; no model invocation):
  INV-AUTH-* (static authority manifest verified at freeze)
  INV-EVID-1 (evidence chain integrity)
  INV-APPL-1 (Applicability Declaration ACTIVE)
  Evaluator availability
  Evaluator blinding intact + per-candidate fresh evaluator sessions per §6
  Frozen scoring algorithm + C20 derivation + normalize-and-join + reconstruction input builder + binding-verification script verified
  Static authority manifest byte-identical to frozen SHA
  D = M ∪ P ∪ O pairwise-disjoint verified
  Operator-only blind map (preflight/blind-map.json) constructed and locked in Phase 0
  Frozen test-invocations.json is byte-identical to MANIFEST SHA

  If any Phase 0 pre-check fails:
     -> EVALUATOR_GATING_FAILURE / INVALID_EXPERIMENT

Phase 1 - Generation (per (R, B, arm, candidate) in locked order)
  Per candidate: fresh executor session, per-candidate evidence file.
  After executor reports "application ready", the operator supplies the
  exact Birthdate <date> invocation for each candidate (sourced from
  inputs/test-invocations.json via the locked blind map). The executor
  MUST NOT invent or select the birthdate at runtime.

Phase 2 - Arm-C scoring + C20 (per §8):
  Per-candidate fresh-evaluator-session blinding (v3 item 8 / v6 carried).
  Each evaluator invocation receives the birthdate + scoring criteria
  + opaque blind_id; NOT arm, NOT reconstruction, NOT phase.
  Each evaluator returns per-candidate JSON in the exact schema in
  evaluation/evaluator-input-packet.md §7.
  The operator runs hashing/normalize-and-join.py to build operator-side
  Arm-C scorebooks from the raw evaluator returns + locked blind map.
  Lock evaluator-A-arm-C-scorebook.json and evaluator-B-arm-C-scorebook.json.
  (No further appends.)
  Run hashing/c20-derivation.py with --blind-map (required):
    - re-verifies all 4 BIB scorebook SHAs (fatal on mismatch)
    - verifies the 85 envelope records (fatal on count/set mismatch)
    - verifies baseline-statistics required fields
    - loads operator-only blind map (--blind-map required)
    - loads operator-side Arm-C scorebooks
    - recovers (R, B, arm, candidate) EXCLUSIVELY from blind map
    - rejects unknown / duplicate blind IDs / duplicate tuples / arm != C / (R, B) outside expected cells
    - uses preregistered historical envelope bound (A=1.807059, B=0.414118)
    - computes per-(R, B) Arm-C mean Manhattan distances
    - emits c20_decision_record.json with c20_per_evaluator_pass, c20_joint_pass, c20_fail_reasons
  C20 fail -> STOP, INVALID_EXPERIMENT.

Phase 3 - Arm-M scoring:
  Same per-candidate fresh-evaluator-session blinding.
  The operator supplies the SAME test invocation (same birthdate) for
  the matched (R, B, test, run) tuple, but generates a FRESH blind_id
  (the frozen blind-map design has one-ID->one-tuple; the run-keyed
  identifier is per-arm, not shared with Arm-C). Run hashing/normalize-and-join.py
  for Arm-M with --arm=M to build the operator-side Arm-M scorebooks.
  Lock evaluator-A-arm-M-scorebook.json and evaluator-B-arm-M-scorebook.json.

Phase 4 - Substantive analysis (joint, not ordered ELSE IF):

STEP 1 - Compute per-evaluator (no pooling):
  Modification_Success_per_evaluator = G_mod_a AND G_mod_b AND G_mod_c AND G_mod_d
  Non-target_Identity_Preservation_per_evaluator =
      (G_pres_subset_a_a AND G_pres_subset_a_b) AND no C12-axis-BROKEN
  The C12 evidence is the locked G_subset_b_axis_scores from the operator-side
  scorebooks (all 8 C12 axes per candidate, preserved by normalize-and-join.py).

STEP 2 - Apply §9 runtime classification (T1/T2/T3).
STEP 3 - Substantive classification.
STEP 4 - If no substantive failure but residual ambiguity:
  -> INCONCLUSIVE_PENDING_FURTHER (reserved).
```

### §10.1 Level 1 vs Level 2 interpretation (proposal v5.1 §4.1)

The substantive dispositions describe Level 1 (bound experimental claim). Level 2 (architectural implication) is the §4.1 adjudication. The synthesis (Phase 5) is the explicit Level 2 adjudication by Frank-as-PI.

---

## §11. Causal traceability (proposal v5.1 §5.3)

The final evidence package must trace each claim to the pre-bound INSA controls. C20 evidence cites the four locked BIB scorebook SHAs, the per-evaluator 4-d reference vector, the historical envelope bound, the per-(R, B) Arm-C mean Manhattan distance, and the per-evaluator pass/fail decision.

---

## §12. Per-step evidence capture (proposal v5.1 §14 + v6)

For each per-(R, B, arm, candidate) generation event:
- `runs/<R>/<B>/<arm>/candidate-<N>.md` — raw candidate output
- `runs/<R>/<B>/<arm>/evidence-<N>.json` — per-candidate evidence

For each per-(R, B, arm) evaluator scoring event: locked operator-side scorebooks (separate per arm per §7; preserved by `hashing/normalize-and-join.py`).

For C20: `preflight/c20-decision-record.json` (locked C20 decision; SHA-256 in sidecar).

For per-experiment synthesis: `results/score-independent.md`, `results/analysis.md`, `results/disposition.md`, `results/unblinded-analysis-results.json`, `results/de-blinding-table.json`.

---

## §13. Model preflight (proposal v5.1 §6, inherited from v0.1 §13)

Before any model dispatch, the operator records model identifiers, CLI versions, frozen source commits, tool postures, authentication paths, session-creation mechanisms.

---

## §14. Evidence chain (proposal v5.1 §14 cross-cut + v6)

Per-step evidence captured. Locking rule applies. Self-referential-hash prohibition: no artifact file contains its own full-file SHA-256 inside its bytes.

---

## §15. Stop conditions (proposal v5.1 §5.1 INV-STOP-1, inherited from v0.1 §14)

**C20 (control validity):** Computed in Phase 2 per §8. If C20 fails, STOP and classify `INVALID_EXPERIMENT`. Do NOT proceed to Phase 3.

**5 INSA-BIB stop rules** (inherited from v0.1 §14).

Plus the §9 systematic thresholds T1/T2/T3 for runtime failure classification.

---

## §16. Authority boundary (proposal v5.1 §8)

This protocol's authorization boundary is protocol + frozen-artifact preparation only. The Frank-as-PI execution GO is a separate event recorded in `preflight/execution-authority-witness.json`.

---

## §17. Executor change documentation (proposal v5.1 §2(e))

v0.1 used `claude-sonnet-4-6`. INSA-ID-E1 uses `claude-opus-4-7`. This substrate change is intentional and pre-registered as a preregistered-bound deviation. The executor change does not become an unacknowledged explanation after outcomes are known.

---

**End of protocol v6 (frozen-candidate-rev6). Awaiting Frank-as-PI execution GO.**
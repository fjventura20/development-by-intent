# INSA-ID-E1 — Protocol (frozen pre-execution, v3)

**Status:** v3 (frozen-candidate-rev3), pending Frank-as-PI execution GO.
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
- This protocol binds proposal v5.1 INV-* invariants; all 16+ frozen pre-execution artifacts are content-addressed in `MANIFEST.json`.

**This protocol is NOT execution authorization.** Execution requires a separate Frank-as-PI GO referencing this protocol's SHA, MANIFEST.json's SHA, the frozen pre-execution artifact SHAs (per proposal v5.1 §7), the INSA v0.3 blob SHA, and the authority manifest SHA. The execution GO is recorded in `preflight/execution-authority-witness.json` (per EXECUTION-ORDER.md §6).

---

## §0. Reading order

This protocol implements proposal v5.1 §§1–11. Sections §1–§17 below map to proposal v5.1 sections in order. Cross-references use the proposal's section numbering.

**v3 revision note:** v2 conflated per-candidate scoring with aggregate computation, placed C20 in Phase 0, and was built under an incorrect §12 B/D/O binding. v3 corrects all three: D = M ∪ P ∪ O disjoint, O = ∅ with rationale, subset-(a) = actual BIB 4-dim names, subset-(b) = 8 C12 axes verbatim from v0.1 §11.3, C20 in Phase 2 after Arm-C scoring, separate per-arm scorebooks, evaluator/aggregation separation, frozen deterministic execution-order + C20 algorithms.

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
- Any change to the §5.4 (proposal v5.1) decision tree semantics (joint, not ordered ELSE IF).
- Any retroactive reclassification of a substantive failure as `INCONCLUSIVE_PENDING_FURTHER`.
- Any model dispatch without preflight verification per INSA v0.3 §6.

---

## §2. Two-arm matched-pair design (proposal v5.1 §5.2)

- **Arm C** (control): same frozen baseline `B` + no-op directive (`inputs/arm-c-directive.txt`).
- **Arm M** (modification): same frozen baseline `B` + frozen modification specification (`inputs/modification-specification.txt`).

The reconstruction input is built at preflight time by the frozen script `preflight/build-reconstruction-input.py` from frozen BIB components (intent + identity contract + per-arm directive).

**Reconstruction count:** 3 per arm (R1, R2, R3) — same as v0.1 BIB-001 non-deviated count. The reconstruction is the primary replication unit (per v0.1 C1 ruling, inherited). Candidates within a reconstruction are repeated observations, not independent experimental replicates. This experiment does NOT claim independent n=60 statistical power.

**Candidate count per (R, B, arm):** 10 candidates per cell (frozen). Total: 3 × 1 × 2 × 10 = 60 candidates. See `protocol/EXECUTION-ORDER.md` §3 (frozen `hashing/score-derivation.py`).

---

## §3. Frozen pre-execution invariants (proposal v5.1 §5.1)

All INV-* from proposal v5.1 §5.1 must hold before any generation. Verification is recorded in `preflight/` directory; each verification produces a `preflight/<INV-ID>.md` file with SHA-256 evidence.

| ID | Invariant | Verification artifact |
|---|---|---|
| INV-B-1 | Frozen baseline `B` content-addressed; baseline-binding artifact `inputs/baseline-binding.json` binds the governing intent, identity contract, reconstruction/test materials, evaluator/rubric identity, BIB evidence, baseline membership, and exact baseline statistics. The numerical baseline statistics are themselves content-addressed to the original BIB scorebooks by SHA. | `preflight/INV-B-1.md` (records `inputs/baseline-binding.json` SHA + the **four** locked BIB scorebook SHAs: BIB-001 evaluator A, BIB-001 evaluator B, BIB-002 evaluator A, BIB-002 evaluator B) |
| INV-D-1 | `D` enumerated as `M ∪ P ∪ O`; pairwise-disjointness verified (set intersection = ∅); `D` SHA-bound | `preflight/INV-D-1.md` (records `inputs/dimensions-decomposition.json` SHA) |
| INV-M-1 | `M` enumerated with frozen per-dimension specification; additive; bounded scope | `preflight/INV-M-1.md` (records `inputs/mutation-dimensions.json` SHA + `inputs/modification-specification.txt` SHA) |
| INV-P-1 | `P` enumerated as `subset-(a) ∪ subset-(b)`, disjoint; non-collapse attestation | `preflight/INV-P-1.md` |
| INV-P-1a | Subset-(a) calibrated BIB 4-dim vector: `contract_compliance`, `selection_behavior`, `narrative_behavior`, `functional_completeness` (all 0-4). Per-dim frozen reference vector + tolerance bound. | subset-(a) rubric SHA + per-dim frozen reference vector SHA + per-dim tolerance values |
| INV-P-1b | Subset-(b) 8 C12 non-target preservation axes preserved verbatim from v0.1 §11.3 (see `inputs/preservation-dimensions-subset-b.json`). Binary-failure convention for 0-4 axes is an INSA-ID-E1 preregistered rule, NOT inherited from v0.1. | subset-(b) axes list SHA + per-axis frozen tolerance values |
| INV-O-1 | `O` preregistered as `∅` with rationale | `preflight/INV-O-1.md` (records `O = ∅` with rationale from `inputs/dimensions-decomposition.json`) |
| INV-V-1 | `V(d)` frozen per-dimension, defined separately for subset-(a) and subset-(b) | `preflight/INV-V-1.md` (records `inputs/evaluator-rubric.json` SHA) |
| INV-A-1 | `A` bound only to `M`; per-dimension acceptance tests; four G_mod_a..d gates with explicit thresholds | `preflight/INV-A-1.md` (records `inputs/acceptance-tests.json` SHA + evaluator blinding manifest) |
| INV-G-1 | `G` bound only to `P`, both subsets; C12 BROKEN joint rule | `preflight/INV-G-1.md` (records `inputs/preservation-gates.json` SHA) |
| INV-AUTH-1 | Executor's authority manifest recorded, capability vs permission separated (I-AUTH-01) | `preflight/INV-AUTH-1.md` (records `inputs/authority-manifest.json` SHA + scope statement) |
| INV-AUTH-2 | Authority grant authentic + traceable (I-AUTH-06, I-AUTH-08) | `preflight/INV-AUTH-2.md` (records static grant provenance; dynamic execution-GO provenance in `preflight/execution-authority-witness.json`) |
| INV-AUTH-5 | Freshness before consequential commit (I-AUTH-05); consequential-action boundary is M-commit + per-candidate Arm-C + Arm-M scoring | `preflight/INV-AUTH-5.md` (records frozen freshness window 3600s + per-candidate witness protocol) |
| INV-EVID-1 | Evidence chain cross-cuts (§14); evidence profile, not evidence ladder | `preflight/INV-EVID-1.md` (records evidence profile structure) |
| INV-APPL-1 | Applicability Declaration per §5: State/Identity/Evidence `ACTIVE` | `preflight/INV-APPL-1.md` (records `inputs/applicability-declaration.json` SHA + ACTIVE attestations) |
| INV-STOP-1 | C20 control-validity stop rule + 5 INSA-BIB stop rules remain authoritative | `preflight/INV-STOP-1.md` (references §15 stop conditions below + §8 C20 derivation) |

### §3.4 Reconstruction input construction

The per-(R, B, arm) reconstruction input is built at preflight time by the frozen script `preflight/build-reconstruction-input.py` (SHA-256 recorded in MANIFEST). The script produces 6 files (3 reconstructions × 1 B × 2 arms):

- `preflight/reconstruction-input-<R>-<B>-C.txt` (Arm C: reconstruction-prompt + identity-contract + arm-c-directive)
- `preflight/reconstruction-input-<R>-<B>-M.txt` (Arm M: reconstruction-prompt + identity-contract + modification-specification)

Each file is byte-identical for its (R, B, arm) tuple across runs (deterministic, no operator discretion). Frozen component SHAs verified by the script at run time; SHA mismatch → fatal error.

---

## §4. Replicates count and matched-pair execution (proposal v5.1 §5.2)

**Total candidates per arm:** 3 reconstructions × N candidates per (R, B) = 3 × N per arm, where N is the OS-CSPRNG draw count (see `protocol/EXECUTION-ORDER.md`; v0.1 used N=10 → 30 candidates per arm, 60 total).

**Execution order:** Frozen scoring algorithm `hashing/score-derivation.py` produces the deterministic ordering from an immutable 32-byte seed file (see `protocol/EXECUTION-ORDER.md` §1). The ordering is reproducible: the same seed produces the same order; the algorithm has zero operator discretion.

**Clean-room input delivery:** Each per-(R, B, arm, candidate) execution receives the pre-built reconstruction input file (see §3.4). The executor never sees the other arm's directive.

---

## §5. Candidate output capture (per (R, B, arm, candidate))

Each candidate output is written to `runs/<R>/<B>/<arm>/candidate-<N>.md` with:
- The full output text
- The execution timestamp (UTC)
- The session_creation_timestamp (for INV-AUTH-5 freshness witness)
- The m_commit_timestamp
- The freshness_check: `0 < (m_commit_timestamp - session_creation_timestamp) <= 3600` seconds (per `inputs/authority-manifest.json` `freshness_window_seconds_static`); violation → per-candidate runtime failure per §9
- The model + substrate identifier (per INV-AUTH-1)
- A SHA-256 of the candidate output text

**No silent replacement** (proposal v5.1 §5.5.1). If a candidate produces a runtime failure, the empty/incomplete output is retained as raw evidence in `runs/<R>/<B>/<arm>/runtime-failure-<N>.json`, and the remaining N−1 candidates are analyzed normally.

---

## §6. Evaluator blinding + per-arm session isolation (proposal v5.1 §5.1 INV-A-1, INV-G-1)

Evaluators A (Codex CLI gpt-5.6-sol) and B (Claude Code CLI claude-opus-4-7, fresh session per I-AUTH-05) receive only the candidate output text + the evaluator input packet (`evaluation/evaluator-input-packet.md`, frozen at protocol freeze). They do NOT see:
- The arm identity (C vs M)
- The reconstruction number
- The experiment identity
- The candidate number within (R, B, arm)
- Any other (R, B, arm, candidate) outputs
- The frozen v0.3 architecture
- The frozen v0.1 protocol
- The INSA-ID-E1 protocol
- The proposal
- The modification specification
- The Arm C directive
- The frozen BIB envelope
- The G_pres_* thresholds or the C12 BROKEN rule
- **The phase (Phase 2 / Phase 3) or any cue from which staged arm identity could be inferred**

**Per-arm session isolation:** Because Arm C is scored before Arm M, the protocol requires a **fresh independent evaluator invocation/session per candidate** for both evaluator A and evaluator B (per Frank-as-PI item 8 of v3 cleanup). No evaluator session is told "this is Phase 2" / "control" / "Phase 3" / or any other staged-arm cue. Phase separation is enforced **only** at the analysis-layer level (post-lock), never at the evaluator session level.

**Evaluator scoring vs aggregate computation (v3 separation):**
- Evaluators return per-candidate raw scores only (M1..M4, modification_conformance, candidate_all_pass; BIB 4-dim vector; C12 axis scores).
- Evaluators do NOT compute G_mod_a..d, G_pres_*, C12 BROKEN, or any aggregate.
- The analysis layer (post-lock, after both scorebooks are locked) computes all aggregates.

**De-blinding table:** `results/de-blinding-table.json` (auditable) is constructed post-scoring from the runs/<R>/<B>/<arm>/<candidate> mapping.

---

## §7. Evaluator scoring + separate per-arm scorebooks (proposal v5.1 §5.4 STEP 1 + v3 item 7)

**Per-evaluator independence:** Evaluators do not see each other's scores during scoring.

**Separate per-arm scorebook locking (v3 item 7):** Do NOT lock an Arm-C scorebook and later append Arm-M entries to it. Required structure:
- `evaluation/evaluator-A-arm-C-scorebook.json` — locked after Phase 2 (C20 input). No further appends permitted.
- `evaluation/evaluator-B-arm-C-scorebook.json` — locked after Phase 2. No further appends permitted.
- `evaluation/evaluator-A-arm-M-scorebook.json` — locked after Phase 3. No further appends permitted.
- `evaluation/evaluator-B-arm-M-scorebook.json` — locked after Phase 3. No further appends permitted.

**Scorebooks are immutable once locked.** Locking means: SHA-256 of the locked file is recorded in `results/score-independent.md`, and no edits occur after the SHA record. Any post-lock edit triggers a deviation record and re-locking. Phase-4 analysis consumes all four locked scorebooks.

**Self-referential hash prohibition (v3 item 6):** No scorebook file contains its own SHA-256 inside the bytes whose SHA-256 it claims to represent. SHA-256s of scorebooks are recorded externally (in MANIFEST.json for frozen artifacts, in results/score-independent.md for dynamic scorebooks, in sidecar files).

### §7.1 Modification_Success = G_mod_a AND G_mod_b AND G_mod_c AND G_mod_d

(v3 restoration per Frank-as-PI: exact four-gate pattern with the specific thresholds from proposal v5.1 §5.4.)

For each evaluator independently:

- **G_mod_a**: mean `modification_conformance` across all Arm-M candidates (pooled) >= 3.5/4.
- **G_mod_b**: >=80% of Arm-M candidates have `candidate_all_pass == true` (i.e., pass all four M1..M4 checks).
- **G_mod_c**: every Arm-M reconstruction has >=70% of its candidates with `candidate_all_pass == true`.
- **G_mod_d**: Arm-M all-pass rate (pooled) exceeds Arm-C all-pass rate by >=50 percentage points.

`Modification_Success_per_evaluator = G_mod_a AND G_mod_b AND G_mod_c AND G_mod_d`.

`Modification_Success (experiment-level) = (Modification_Success for A) AND (Modification_Success for B)`.

### §7.2 Non-target_Identity_Preservation = G_pres_subset_a AND no C12-axis-BROKEN

For each evaluator independently:

- **G_pres_subset_a_a**: per-Recon mean M_4-dim-Manhattan-from-ref for Arm-M candidates <= per-Recon mean C_4-dim-Manhattan-from-ref for Arm-C candidates + 1.5 (relative criterion; +1.5 does NOT enlarge Arm-C envelope).
- **G_pres_subset_a_b**: per-Recon mean M_4-dim-Manhattan-from-ref for Arm-M candidates <= 2.5 (absolute criterion).

Subset-(a) PASS requires both G_pres_subset_a_a and G_pres_subset_a_b to PASS.

**C12-axis-BROKEN determination (analysis-side, joint rule per v0.1 §11.3):**
- For each axis a in {C12-1..C12-8}: `axis_a is BROKEN for evaluator e` IF AND ONLY IF BOTH (i) `arm_M_failure_rate_on_axis_a >= 0.30` AND (ii) `(arm_M_failure_rate_on_axis_a - arm_C_failure_rate_on_axis_a) >= 0.30`.
- Subset-(b) PASS for evaluator e IF AND ONLY IF no axis is BROKEN for evaluator e.

`Non-target_Identity_Preservation_per_evaluator = (subset-(a) PASS) AND (subset-(b) PASS)`.

`Non-target_Identity_Preservation (experiment-level) = (Non-target for A) AND (Non-target for B)`.

---

## §8. C20 control-validity pre-check (proposal v5.1 §5.4 + v3 item 5) — Phase 2

**C20 runs in Phase 2 (Arm-C scoring), NOT in Phase 0 pre-dispatch preflight.** C20 verifies Arm-C candidates against the BIB envelope, and Arm-C candidates do not exist until generation runs.

**C20 deterministic derivation:** Per proposal v5.1 §7, the frozen package must include a deterministic baseline binding sufficient to reproduce the decision without judgment after execution begins. This is provided by `hashing/c20-derivation.py` (SHA-256 in MANIFEST), which consumes:

1. The four frozen BIB scorebook SHAs (re-verified at C20 derivation time; mismatch → fatal)
2. The exact 85-observation inclusion mapping (`inputs/baseline-envelope-membership.json`)
3. The per-evaluator calibrated 4-d reference vectors (`inputs/baseline-statistics.json`, computed deterministically from the 85 envelope observations)
4. The Phase 2 Arm-C scorebooks (`evaluation/evaluator-A-arm-C-scorebook.json`, `evaluation/evaluator-B-arm-C-scorebook.json`)

The script computes:

- Per-evaluator 4-dim reference vector (mean of 85 envelope observations per dim)
- C20 envelope bound per evaluator (max per-(R, B) mean 4-dim Manhattan-from-ref across the 85 envelope observations)
- Per-(R, B) Arm-C mean 4-dim Manhattan distance per evaluator
- C20 PASS for evaluator e IF AND ONLY IF:
  - (a) every envelope (R, B) cell has at least one Arm-C candidate, AND
  - (b) for every (R, B) Arm-C cell, mean 4-dim Manhattan distance <= C20 envelope bound for evaluator e
- C20 joint PASS iff both evaluators PASS
- C20 fail → disposition = `INVALID_EXPERIMENT`; STOP; do NOT proceed to Phase 3

The C20 Boolean PASS/FAIL formula and the exact derivation method are recorded in `inputs/baseline-statistics.json` for full auditability. The C20 derivation script's own SHA-256 is included in the derivation record.

---

## §9. Runtime failure handling (proposal v5.1 §5.5) — Phase 1 + Phase 4

Per proposal v5.1 §5.5.1, a candidate-level transient failure is logged; no automatic retry; unaffected candidates are analyzed normally.

Per proposal v5.1 §5.5.2, a runtime failure is classified as **systematic** (triggering `EXECUTOR_RUNTIME_FAILURE`) when **any** of the following holds:

- **(T1)** ≥ 50% of candidates across the experiment fail with a runtime error of the same root-cause class (e.g., all timeout-class, or all refusal-class, or all capacity-class).
- **(T2)** Treatment-arm imbalance with sufficient observations: `fail_M / max(fail_C, 1) ≥ 2` AND `fail_M − fail_C ≥ 3` AND `fail_M + fail_C ≥ 5`. A single Arm-M timeout with `fail_C = 0` and `fail_M = 1` does NOT meet T2; it is treated as a transient failure per §5.5.1.
- **(T3)** Failures span both evaluators and both arms with no candidate producing a complete output for any (R, B) cell — i.e., the executor substrate is effectively unavailable.

The thresholds T1, T2, T3 are preregistered; they are not tightened or relaxed after observing outcomes.

**R2-like deferral pattern (v4 explicit, carried into v3):** No R2-like (or any single-reconstruction) deferral pattern automatically produces `EXECUTOR_RUNTIME_FAILURE`. Such a pattern is evaluated under T1/T2/T3 (see §10 risk #3).

---

## §10. Decision tree (proposal v5.1 §5.4)

```
PRE-CHECKS (Phase 0 pre-dispatch — static only; no model invocation):
  INV-AUTH-* (static authority manifest verified at freeze)
  INV-EVID-1 (evidence chain integrity)
  INV-APPL-1 (Applicability Declaration ACTIVE)
  Evaluator availability (per INV-AUTH-1 evaluator identity check)
  Evaluator blinding intact + per-arm session isolation per §6
  Frozen scoring algorithm + C20 derivation + reconstruction input builder verified
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
  per-candidate runtime failure classification per §9.

Phase 2 - Arm-C scoring + C20 (per §8):
  Lock evaluator-A-arm-C-scorebook.json and evaluator-B-arm-C-scorebook.json.
  Construct results/de-blinding-table.json for Arm-C.
  Compute C20 (per evaluator) deterministically via hashing/c20-derivation.py.
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

STEP 2 - Apply §9 runtime classification (T1/T2/T3):
  - If systematic (any threshold met) -> EXECUTOR_RUNTIME_FAILURE for affected
    substrate; stop substantive analysis.
  - Otherwise proceed to STEP 3 using the unaffected candidates.

STEP 3 - Substantive classification:
  If (Modification_Success_per_A AND Modification_Success_per_B)
     AND (Non-target_Identity_Preservation_per_A AND Non-target_Identity_Preservation_per_B)
     AND (Contemporaneous_Control_Validity TRUE)
     -> DISPOSITION = ARCHITECTURAL_PASS

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
          ruled out per §4 + §5.5; see proposal v5.1 §4.1 for the precise
          Level 1 vs Level 2 mapping. The disposition does not, by itself,
          establish §12 invalidity.)

STEP 4 - Only after all substantive outcomes exhausted:
  If (no substantive failure but residual ambiguity)
  -> DISPOSITION = INCONCLUSIVE_PENDING_FURTHER
  (reserved for genuine ambiguity; never used to soften substantive failures)
```

### §10.1 Level 1 vs Level 2 interpretation (proposal v5.1 §4.1)

The substantive dispositions describe Level 1 (bound experimental claim). Level 2 (architectural implication) is the §4.1 adjudication:

- `ARCHITECTURAL_PASS` → Level 1 supported, Level 2 consistent with §12 (no generalization claim)
- `PRESERVATION_FAILURE` → Level 1 falsified on preservation axis, Level 2 underdetermined
- `MUTATION_FAILURE` → Level 1 falsified on modification axis, Level 2 underdetermined
- `MODIFICATION_AND_PRESERVATION_FAILURE` (post-cause-ruling-out) → Level 1 falsified on both axes, Level 2 strengthens concern but does NOT establish §12 invalidity

The synthesis (Phase 5) is the explicit Level 2 adjudication by Frank-as-PI.

---

## §11. Causal traceability (proposal v5.1 §5.3)

The final evidence package must trace each claim to the pre-bound INSA controls:

- Every claim of "preservation held at dimension `d`" must cite the frozen `G_d` gate, the frozen `V(d)` value, the subset that `d` belongs to (subset-(a) or subset-(b)), the per-dim frozen reference vector (for subset-(a)) or per-axis tolerance (for subset-(b)), and the per-(R, B, arm) difference between Arm M and Arm C.
- Every claim of "modification succeeded at dimension `m`" must cite the frozen `A_m` acceptance test, the frozen `M` specification, the per-candidate M1..M4 + modification_conformance scores from the locked scorebooks, and the aggregated gate result.
- Every authority claim must cite the recorded authority manifest's scope, grant authenticity, freshness window in seconds (3600), and the per-candidate freshness witness at the M-commit boundary.
- Every applicability claim must cite the Applicability Declaration file and its SHA.
- Every C20 claim must cite the C20 derivation record SHA, the four frozen BIB scorebook SHAs, the per-evaluator 4-dim reference vector, the C20 envelope bound, and the per-(R, B) Arm-C mean Manhattan distance.
- Every execution-order claim must cite the frozen scoring algorithm SHA and the recorded `draw_event_sha256`.

---

## §12. Per-step evidence capture (proposal v5.1 §14)

For each per-(R, B, arm, candidate) generation event:
- `runs/<R>/<B>/<arm>/candidate-<N>.md` — raw candidate output
- `runs/<R>/<B>/<arm>/evidence-<N>.json` — per-candidate evidence (timestamps, model, substrate, freshness witness with freshness check result)
- `runs/<R>/<B>/<arm>/runtime-failure-<N>.json` — only if runtime failure

For each per-(R, B, arm) evaluator scoring event:
- `evaluation/evaluator-A-arm-C-scorebook.json` — locked after Phase 2 (no further appends)
- `evaluation/evaluator-B-arm-C-scorebook.json` — locked after Phase 2
- `evaluation/evaluator-A-arm-M-scorebook.json` — locked after Phase 3
- `evaluation/evaluator-B-arm-M-scorebook.json` — locked after Phase 3

For per-experiment synthesis:
- `results/score-independent.md` — locked evaluator scores
- `results/analysis.md` — reconstruction-level → per-arm → matched → pooled, with causal trace per §11
- `results/disposition.md` — the §10 disposition, with explicit cause-ruling-out for any non-arch-pass class
- `results/unblinded-analysis-results.json` — canonical record
- `results/de-blinding-table.json` — auditable

For final synthesis:
- `synthesis.md` — final adjudication; PI signs
- `REPORT-<date>-INSA-ID-E1.md` — research-level writeup

For C20 specifically:
- `preflight/c20-decision-record.json` — locked output of `hashing/c20-derivation.py` (calibrated reference vectors, envelope bounds, per-(R, B) Arm-C means, per-evaluator PASS/FAIL, joint PASS/FAIL, fail reasons, derivation script SHA-256). Sidecar pattern: C20 derivation record SHA recorded externally (no self-reference inside the file).

---

## §13. Model preflight (proposal v5.1 §6, inherited from v0.1 §13)

Before any model dispatch, the operator records:
- Model identifier (claude-opus-4-7 for executor; gpt-5.6-sol for evaluator A; claude-opus-4-7 for evaluator B)
- CLI/runtime version (claude-code CLI version; codex CLI version)
- Frozen source commit (`c3692150` for BIB; `848e0fe…` for v0.3 architecture; `1f84c31` for proposal v5.1)
- Frozen source file SHA-256 (matches `MANIFEST.json`)
- Tool posture (--allowedTools '' --tools '' --disallowedTools 'WebFetch,WebSearch' for executor, per v0.1 §13)
- Authentication path (recorded in execution-authority-witness.json; SHA-256 only, never plaintext)
- Session-creation mechanism (fresh session per M-commit, fresh session per Arm-C candidate, fresh session per Arm-M candidate; per I-AUTH-05)

Any material deviation is recorded before generation and handled per the preregistered deviation rule (proposal v5.1 §8). STOP if deviation is material and unadjudicated.

---

## §14. Evidence chain (proposal v5.1 §14 cross-cut)

Per-step evidence (timestamps, model, substrate, scorebooks, raw outputs) is captured with the per-event evidence file. Locking at evaluator output means the scorebook is content-addressed at the moment of evaluator completion. The evidence profile (not evidence ladder) is the canonical structure: each step's evidence file is referenced from the next step's analysis, forming a directed evidence graph.

**Locking rule:** An evidence file is "locked" when (a) it has been written, (b) its SHA-256 has been recorded in the parent synthesis file, and (c) no edits have occurred after the SHA record. Any post-lock edit triggers a deviation record and re-locking.

**Self-referential-hash prohibition:** No artifact file contains its own full-file SHA-256 inside the bytes whose SHA-256 it claims to represent. Scorebook SHAs and C20 derivation record SHAs are recorded externally (in MANIFEST.json for frozen artifacts, in results/score-independent.md for dynamic scorebooks, in sidecar files for dynamic outputs).

---

## §15. Stop conditions (proposal v5.1 §5.1 INV-STOP-1, inherited from v0.1 §14)

**C20 (control validity):** Computed in Phase 2 per §8. If C20 fails, STOP and classify `INVALID_EXPERIMENT`. Do NOT proceed to Phase 3.

**5 INSA-BIB stop rules** (inherited from v0.1 §14):
1. **Material deviation during generation:** Any material deviation from the frozen pre-execution artifacts triggers STOP unless PI separately adjudicates.
2. **Evaluator substitution after observing candidates:** Forbidden per proposal v5.1 §8.
3. **Retroactive gate weakening:** Forbidden per proposal v5.1 §8.
4. **Decision tree semantics change:** Forbidden per proposal v5.1 §8 (§5.4 must remain joint, not ordered ELSE IF).
5. **Substantive → INCONCLUSIVE_PENDING_FURTHER reclassification:** Forbidden per proposal v5.1 §8.

Plus the §9 systematic thresholds T1/T2/T3 for runtime failure classification.

---

## §16. Authority boundary (proposal v5.1 §8)

This protocol's authorization boundary is protocol + frozen-artifact preparation only. The Frank-as-PI execution GO is a separate event recorded in `preflight/execution-authority-witness.json`.

When the execution GO is issued, the witness must include:
- This protocol's SHA (filled after `MANIFEST.json` is content-addressed)
- `MANIFEST.json` SHA
- The frozen pre-execution artifact SHAs (via `MANIFEST.json`)
- The frozen INSA v0.3 source blob `848e0fe014f5b4a61ba2cb92e772ee3499dca9c1`
- The authority manifest SHA (`inputs/authority-manifest.json`)

**Until the execution GO is issued and the witness is created, no model dispatch, no evaluator invocation, no candidate generation.**

---

## §17. Executor change documentation (proposal v5.1 §2(e))

v0.1 used `claude-sonnet-4-6`. INSA-ID-E1 uses `claude-opus-4-7`. This substrate change is intentional and pre-registered as a preregistered-bound deviation. Limitation on direct v0.1 failure-shape comparison: the v0.1 `MODIFICATION_AND_PRESERVATION_FAILURE` was driven by claude-sonnet-4-6 evaluator-side R2-B deferrals; the same failure shape may not reproduce in claude-opus-4-7 sessions, and a different shape may emerge. The INSA-ID-E1 v0.3 architecture corrections (§12) are substrate-agnostic at the architectural level, but the empirical outcome may differ.

The executor substrate change does not become an unacknowledged explanation after outcomes are known.

---

**End of protocol v3 (frozen-candidate-rev3). Awaiting Frank-as-PI execution GO.**
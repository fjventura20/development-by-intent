# INSA-ID-E1 — Protocol (frozen pre-execution, v2)

**Status:** v0.2 (frozen-candidate-rev2), pending Frank-as-PI execution GO.
**Author:** Hermes (operator).
**Date:** 2026-09-11.
**Binding:**
- Proposal: `docs/proposals/2026-09-10-INSA-ID-E1-proposal.md` commit `ed95705632027f459b396cd423eae54e8bb9a81b` (proposal v4)
- Frozen v0.3 architecture blob: `848e0fe014f5b4a61ba2cb92e772ee3499dca9c1` (commit `d2c2ad93d95d048e6e2e0c3d42d993a1ecd40f1b`)
- Frozen v0.1 protocol: `experiments/2026-09-06-dbi-evolution-v0.1/protocol/PROTOCOL-v0.5-frozen-final.md` SHA-256 `079138163f0b59f71002480feffc008d9b350d460731c5d51f037163b17c2ab4` (git blob SHA-1 `8874692d560d9a6363ef4105fae5384b18cf6ef2`) — referenced, NOT modified
- Frozen BIB source commit: `c369215024c9f8a849daf11bd4b872d7ee566a7a`
- Frozen scoring algorithm: `hashing/score-derivation.py` (SHA-256 in MANIFEST)
- Frozen reconstruction input builder: `preflight/build-reconstruction-input.py` (SHA-256 in MANIFEST)
- This protocol binds proposal v4 INV-A..INV-APPL-STOP-1 invariants; all frozen pre-execution artifacts are content-addressed in `MANIFEST.json`.

**This protocol is NOT execution authorization.** Execution requires a separate Frank-as-PI GO referencing this protocol's SHA, MANIFEST.json's SHA, the 16 frozen pre-execution artifact SHAs (per proposal v4 §7), the INSA v0.3 blob SHA, and the authority manifest SHA. The execution GO is recorded in `preflight/execution-authority-witness.json` (per EXECUTION-ORDER.md §6).

---

## §0. Reading order

This protocol implements proposal v4 §§3, 4.1, 5.1, 5.2, 5.3, 5.4, 5.5, 6, 8, 10. Sections §1–§15 below map to proposal v4 sections in order. Cross-references use the proposal's section numbering.

**v2 revision note:** v1 placed C20 as a pre-dispatch preflight gate (incorrect — C20 requires Arm-C candidates to exist). v2 moves C20 to Phase 2 (after Arm-C scoring, before M-arm analysis). v1 also conflated per-candidate scoring with aggregate computation (G_pres_*, C12 BROKEN); v2 separates them. v1 referenced a non-existent `hashing/score-derivation.py` to be generated at preflight (freeze violation); v2 ships the actual frozen algorithm in `hashing/score-derivation.py`.

---

## §1. Scope and authority (proposal v4 §8)

This protocol authorizes protocol + frozen-artifact preparation only. It does NOT authorize execution.

The Frank-as-PI GO for execution must reference:
- This protocol's SHA (filled after `MANIFEST.json` is content-addressed)
- `MANIFEST.json` SHA (filled at freeze)
- The 16 frozen pre-execution artifact SHAs (recorded in `MANIFEST.json`)
- The frozen INSA v0.3 source blob `848e0fe014f5b4a61ba2cb92e772ee3499dca9c1`
- The authority manifest SHA (`inputs/authority-manifest.json`)

The execution GO authorizes execution ONLY. It does NOT authorize modifications to any frozen pre-execution artifact. Any material deviation triggers the preregistered deviation rule (STOP unless PI separately adjudicates).

Specifically NOT authorized in this protocol or the execution GO:
- Any change to the frozen v0.3 architecture (`848e0fe…`).
- Any change to the dbi-evolution-v0.1 protocol (`8874692d…`).
- Any modification to `B + D + M + P + O + V(d) + A + G` after protocol freeze.
- Any evaluator substitution after observing candidates.
- Any retroactive weakening of gates or thresholds.
- Any change to the §5.4 (proposal v4) decision tree semantics (joint, not ordered ELSE IF).
- Any retroactive reclassification of a substantive failure as `INCONCLUSIVE_PENDING_FURTHER`.
- Any model dispatch without preflight verification per INSA v0.3 §6 (proposal v4 §6 model preflight, inherited from v0.1 §13).

---

## §2. Two-arm matched-pair design (proposal v4 §5.2)

**Arm C (control):** frozen intent (`D` = `inputs/intent-document.txt`) + no-op directive (`inputs/arm-c-directive.txt`). Reconstruction input: built at preflight from frozen BIB components (see §3.4 below).

**Arm M (modification):** same frozen intent (`D`) + frozen modification specification (`inputs/modification-specification.txt`). Reconstruction input: built at preflight from frozen BIB components + the M directive.

**Reconstruction count:** 3 per arm (R1, R2, R3) — same as v0.1 BIB-001 non-deviated count. The reconstruction is the primary replication unit (per v0.1 C1 ruling, inherited). Candidates within a reconstruction are repeated observations, not independent experimental replicates. This experiment does NOT claim independent n=60 statistical power.

**Candidate count per (R, B, arm):** Per v0.1, the OS-CSPRNG draw produces 10 candidate draws per (R, B, arm). See `protocol/EXECUTION-ORDER.md` §3 (frozen `hashing/score-derivation.py`).

---

## §3. Frozen pre-execution invariants (proposal v4 §5.1)

All INV-* from proposal v4 §5.1 must hold before any generation. Verification is recorded in `preflight/` directory; each verification produces a `preflight/<INV-ID>.md` file with SHA-256 evidence.

| ID | Invariant | Verification artifact |
|---|---|---|
| INV-B-1 | Frozen baseline `B` content-addressed | `preflight/INV-B-1.md` (records `inputs/baseline-envelope-membership.json` SHA + the 85 BIB observations inherited from v0.1) |
| INV-M-1 | `M` enumerated with frozen per-dim spec | `preflight/INV-M-1.md` (records `inputs/mutation-dimensions.json` SHA + `inputs/modification-specification.txt` SHA) |
| INV-P-1 | `P` enumerated, two disjoint subsets, non-collapse attestation | `preflight/INV-P-1.md` (records SHAs of `subset-a`, `subset-b`, `P` binding, and the non-collapse attestation file `inputs/preservation-dimensions.json`) |
| INV-P-1a | Subset-(a) calibrated BIB 4-dim | `preflight/INV-P-1a.md` (records `inputs/preservation-dimensions-subset-a.json` SHA + per-dim tolerance values) |
| INV-P-1b | Subset-(b) 8 C12 axes | `preflight/INV-P-1b.md` (records `inputs/preservation-dimensions-subset-b.json` SHA + per-axis tolerance values) |
| INV-V-1 | `V(d)` frozen per-dim, separately for subset-(a) and subset-(b) | `preflight/INV-V-1.md` (records `inputs/evaluator-rubric.json` SHA) |
| INV-D-1 | `D` (intent document) content-addressed | `preflight/INV-D-1.md` (records `inputs/intent-document.txt` SHA = `7f22a0fa7ede3c6e6938b2affc1298a52fd566b9c5707579461ba661d0d6fb33` + git blob SHA-1 cross-reference at c3692150) |
| INV-O-1 | `O` (identity contract) content-addressed | `preflight/INV-O-1.md` (records `inputs/identity-contract.txt` SHA = `4582d768b696bbce41729ff05475ff9a8edf86c7b55668aaa46a230690e66159` + git blob SHA-1 cross-reference at c3692150) |
| INV-A-1 | `A` bound to `M`, per-dim acceptance tests | `preflight/INV-A-1.md` (records `inputs/acceptance-tests.json` SHA + evaluator blinding manifest) |
| INV-G-1 | `G` bound to `P`, both subsets | `preflight/INV-G-1.md` (records `inputs/preservation-gates.json` SHA) |
| INV-AUTH-1 | Executor authority manifest recorded, capability vs permission separated | `preflight/INV-AUTH-1.md` (records `inputs/authority-manifest.json` SHA + scope statement) |
| INV-AUTH-2 | Authority grant authentic + traceable | `preflight/INV-AUTH-2.md` (records static grant provenance; dynamic execution-GO provenance in `preflight/execution-authority-witness.json`) |
| INV-AUTH-5 | Freshness before consequential commit | `preflight/INV-AUTH-5.md` (records the frozen freshness window in seconds + per-candidate witness protocol per I-AUTH-05) |
| INV-EVID-1 | Evidence chain cross-cuts (§14) | `preflight/INV-EVID-1.md` (records evidence profile structure) |
| INV-APPL-1 | Applicability Declaration per §5: State/Identity/Evidence `ACTIVE` | `preflight/INV-APPL-1.md` (records `inputs/applicability-declaration.json` SHA + ACTIVE attestations) |
| INV-STOP-1 | C20 control-validity stop rule + 5 INSA-BIB stop rules | `preflight/INV-STOP-1.md` (references §15 stop conditions below) |

### §3.4 Reconstruction input construction (v2 correction)

The per-(R, B, arm) reconstruction input is built at preflight time by the frozen script `preflight/build-reconstruction-input.py` (SHA-256 recorded in MANIFEST). The script produces 6 files (3 reconstructions × 1 B × 2 arms):

- `preflight/reconstruction-input-<R>-<B>-C.txt` (Arm C: reconstruction-prompt + identity-contract + arm-c-directive)
- `preflight/reconstruction-input-<R>-<B>-M.txt` (Arm M: reconstruction-prompt + identity-contract + modification-specification)

Each file is byte-identical for its (R, B, arm) tuple across runs (deterministic, no operator discretion). Frozen component SHAs verified by the script at run time; SHA mismatch → fatal error.

The v1 v0.1-style `reconstruction-input.txt`/`-C.txt`/`-M.txt` files at the v0.1 experiment directory are NOT used in v2.

---

## §4. Replicates count and matched-pair execution (proposal v4 §5.2)

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

**No silent replacement** (proposal v4 §5.5.1). If a candidate produces a runtime failure, the empty/incomplete output is retained as raw evidence in `runs/<R>/<B>/<arm>/runtime-failure-<N>.json`, and the remaining N−1 candidates are analyzed normally.

---

## §6. Evaluator blinding (proposal v4 §5.1 INV-A-1, INV-G-1)

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

**Evaluator scoring vs aggregate computation (v2 separation):**
- Evaluators return per-candidate raw scores only (M1..M4, modification_conformance, candidate_all_pass; BIB 4-dim vector; C12 axis scores).
- Evaluators do NOT compute G_mod_a..d, G_pres_*, C12 BROKEN, or any aggregate. Per-candidate failure conventions are returned as raw scores; the analysis layer (post-lock) computes aggregate.

**De-blinding table:** `results/de-blinding-table.json` (auditable) is constructed post-scoring from the runs/<R>/<B>/<arm>/<candidate> mapping.

---

## §7. Evaluator scoring (proposal v4 §5.4 STEP 1)

Per-evaluator independence: Evaluators do not see each other's scores during scoring. Scores are written to `evaluation/evaluator-A-scorebook.json` and `evaluation/evaluator-B-scorebook.json` (immutable, content-addressed).

Scorebooks are locked (proposal v4 §14 evidence chain cross-cut) at the moment each evaluator completes scoring. Locking means: subsequent edits require a deviation record; the locked version is what `results/score-independent.md` reports against.

### §7.1 Modification_Success = G_mod_a AND G_mod_b AND G_mod_c AND G_mod_d

(v2 restoration per Frank-as-PI at 2026-09-11. Four-gate pattern with the specific thresholds.)

For each evaluator independently:

- **G_mod_a**: mean `modification_conformance` across all Arm-M candidates (pooled) >= 3.5/4.
- **G_mod_b**: >=80% of Arm-M candidates have `candidate_all_pass == true` (i.e., pass all four M1..M4 checks).
- **G_mod_c**: every Arm-M reconstruction has >=70% of its candidates with `candidate_all_pass == true`.
- **G_mod_d**: Arm-M all-pass rate (pooled) exceeds Arm-C all-pass rate by >=50 percentage points.

`Modification_Success_per_evaluator = G_mod_a AND G_mod_b AND G_mod_c AND G_mod_d`.

`Modification_Success (experiment-level) = (Modification_Success for A) AND (Modification_SSuccess for B)`.

### §7.2 Non-target_Identity_Preservation = G_pres_subset_a AND no C12-axis-BROKEN

(v2 restoration per Frank-as-PI at 2026-09-11. Evaluator-side scoring + analysis-side aggregation explicitly separated.)

For each evaluator independently:

- **G_pres_subset_a_a**: per-Recon mean M_manhattan_within_R for Arm-M candidates <= per-Recon mean C_manhattan_within_R for Arm-C candidates + 1.5 (relative criterion; +1.5 does NOT enlarge Arm-C envelope).
- **G_pres_subset_a_b**: per-Recon mean M_manhattan_within_R for Arm-M candidates <= 2.5 (absolute criterion).

Subset-(a) PASS requires both G_pres_subset_a_a and G_pres_subset_a_b to PASS.

**C12-axis-BROKEN determination (analysis-side, joint rule):**
- For each axis a in {C12-1..C12-8}: `axis_a is BROKEN for evaluator e` IF AND ONLY IF BOTH (i) `arm_M_failure_rate_on_axis_a >= 0.30` AND (ii) `(arm_M_failure_rate_on_axis_a - arm_C_failure_rate_on_axis_a) >= 0.30`.
- Subset-(b) PASS for evaluator e IF AND ONLY IF no axis is BROKEN for evaluator e.

`Non-target_Identity_Preservation_per_evaluator = (subset-(a) PASS) AND (subset-(b) PASS)`.

`Non-target_Identity_Preservation (experiment-level) = (Non-target_Identity_Preservation for A) AND (Non-target_Identity_Preservation for B)`.

---

## §8. Control validity pre-check C20 (proposal v4 §5.4 pre-check) — Phase 2 gate

**C20 runs in Phase 2 (Arm-C scoring), NOT in Phase 0 pre-dispatch preflight.** C20 verifies Arm-C candidates against the BIB envelope, and Arm-C candidates do not exist until generation runs.

**Phase 2 sequence:**
1. Phase 1 generation completes for all Arm-C tuples (regardless of whether all Arm-M tuples have completed).
2. Evaluator-A and Evaluator-B score all Arm-C candidates (blinded), per `evaluation/evaluator-input-packet.md`.
3. Lock Arm-C portions of scorebooks.
4. Construct `results/de-blinding-table.json` for Arm-C (operator-side, post-lock).
5. **Compute C20 (per evaluator):** for each evaluator, compute Arm-C per-(R, B) mean BIB 4-dim Manhattan distance from the historical BIB mean (from `inputs/baseline-envelope-membership.json`). C20 PASSES for evaluator e IF AND ONLY IF for every (R, B) Arm-C cell the mean is within the historical BIB envelope. The +1.5 Manhattan tolerance does NOT apply to C20 (per v0.1 §11.2 PI freeze correction 1, C-1).
6. **C20 decision (joint):** C20 FAILS if C20 fails for either evaluator. C20 PASSES only if C20 passes for both evaluators.

**C20 fail → STOP, `INVALID_EXPERIMENT`.** Do NOT proceed to Phase 3 (Arm-M scoring) or Phase 4 (substantive analysis). The report explains which envelope boundary was violated.

---

## §9. Runtime failure handling (proposal v4 §5.5) — Phase 1 + Phase 4

Per proposal v4 §5.5.1, a candidate-level transient failure is logged; no automatic retry; unaffected candidates are analyzed normally.

Per proposal v4 §5.5.2, a runtime failure is classified as **systematic** (triggering `EXECUTOR_RUNTIME_FAILURE`) when:

- **(T1)** ≥ 50% of candidates across the experiment fail with a runtime error of the same root-cause class (e.g., all timeout-class, or all refusal-class, or all capacity-class).
- **(T2)** Treatment-arm imbalance with sufficient observations: `fail_M / max(fail_C, 1) ≥ 2` AND `fail_m - - fail_C ≥ 3` AND `fail_m - + fail_C ≥ 5`. A single Arm-M timeout with `fail_C = 0` and `fail_m - = 1` does NOT meet T2.
- **(T3)** Failures span both evaluators and both arms with no candidate producing a complete output for any (R, B) cell — i.e., the executor substrate is effectively unavailable.

The thresholds T1, T2, T3 are preregistered; they are not tightened or relaxed after observing outcomes (proposal v4 §5.5.2 final paragraph).

**T2 evaluation timing:** T2 is computed at Phase 4 (substantive analysis, post-lock), not at Phase 1 (during generation). The T2 numerator and denominator are taken from the locked per-(R, B, arm, candidate) runtime-failure records.

**R2-like (or any single-reconstruction) deferral pattern does not automatically produce `EXECUTOR_RUNTIME_FAILURE`** (proposal v4 §10 risk #3, v4 correction). Such a pattern is evaluated under T1/T2/T3:
- If T1/T2/T3 unmet → transient per §5.5.1; unaffected candidates analyzed normally; substantive disposition is whatever §10 produces from the remaining observations.
- If any T-trip → `EXECUTOR_RUNTIME_FAILURE` for the affected substrate per §5.5; no architectural disposition; report explains which threshold tripped.

---

## §10. Decision tree (proposal v4 §5.4)

```
PRE-CHECKS (Phase 0 pre-dispatch — static only; no model invocation):
  INV-AUTH-* (static authority manifest verified at freeze; execution-time verification in witness)
  INV-EVID-1 (evidence chain integrity)
  INV-APPL-1 (Applicability Declaration ACTIVE)
  Evaluator availability (per INV-AUTH-1 evaluator identity check)
  Evaluator blinding intact
  Frozen scoring algorithm + reconstruction input builder verified
  Static authority manifest byte-identical to frozen SHA
  Execution-authority witness created and verified

  If any Phase 0 pre-check fails:
     - Evaluator unavailable        -> EVALUATOR_GATING_FAILURE
     - Evaluator blinding broken   -> INVALID_EXPERIMENT
     - Authority manifest drift    -> INVALID_EXPERIMENT
     - Applicability not ACTIVE     -> INVALID_EXPERIMENT
     - Evidence chain integrity    -> INVALID_EXPERIMENT
     - Frozen algorithm drift      -> INVALID_EXPERIMENT

Phase 1 - Generation (per (R, B, arm, candidate) in locked order)

Phase 2 - Arm-C scoring + C20:
  Score all Arm-C candidates (evaluators blinded, per-candidate raw scores only).
  Compute C20 (per evaluator): Arm-C per-(R, B) BIB 4-dim mean Manhattan distance from
                              historical BIB mean; within envelope -> PASS.
  C20 (joint): both evaluators must PASS.
  If C20 FAILS -> STOP -> INVALID_EXPERIMENT (do NOT analyze M-arm).

Phase 3 - Arm-M scoring:
  Score all Arm-M candidates (evaluators blinded, per-candidate raw scores only).
  Lock all scorebooks (Arm-C + Arm-M portions).

Phase 4 - Substantive analysis (joint, not ordered ELSE IF):
  1. Apply §9 runtime classification (T1/T2/T3) using locked runtime-failure records.
     If any threshold met -> EXECUTOR_RUNTIME_FAILURE for affected substrate; stop.
  2. STEP 1: Compute per-evaluator (no pooling):
     Modification_Success_per_evaluator = G_mod_a AND G_mod_b AND G_mod_c AND G_mod_d
     Non-target_Identity_Preservation_per_evaluator = G_pres_subset_a_a AND G_pres_subset_a_b
                                                       AND no C12-axis-BROKEN
  3. STEP 3: Substantive classification:
     If (Modification_Success_per_A AND Modification_Success_per_B)
        AND (Non-target_Identity_Preservation_per_A AND Non-target_Identity_Preservation_per_B)
        AND (Contemporaneous_Control_Validity TRUE)
        -> DISPOSITION = ARCHITECTURAL_PASS

     ELSE classify substantive failure(s) FIRST:
       If (Modification_Success_per_evaluator FALSE for either evaluator)
          AND (Non-target_Identity_Preservation TRUE for both evaluators)
          -> DISPOSITION = MUTATION_FAILURE
       If (Modification_Success_per_evaluator TRUE for both evaluators)
          AND (Non-target_Identity_Preservation FALSE for either evaluator)
          -> DISPOSITION = PRESERVATION_FAILURE
       If (Modification_Success_per_evaluator FALSE for either evaluator)
          AND (Non-target_Identity_Preservation FALSE for either evaluator)
          -> DISPOSITION = MODIFICATION_AND_PRESERVATION_FAILURE
            (only strengthens Level 2 concern toward §12's general structure
             after runtime, evaluator, and pre-check explanations have been
             ruled out per §4 + §5.5; see proposal v4 §4.1 for the precise
             Level 1 vs Level 2 mapping. The disposition does not, by itself,
             establish §12 invalidity.)

  4. STEP 4: Only after all substantive outcomes exhausted:
     If (no substantive failure but residual ambiguity)
     -> DISPOSITION = INCONCLUSIVE_PENDING_FURTHER
     (reserved for genuine ambiguity; never used to soften substantive failures)
```

---

## §11. Causal traceability (proposal v4 §5.3)

The final evidence package must trace each claim to the pre-bound INSA controls:

- Every claim of "preservation held at dimension `d`" must cite the frozen `G_d` gate (`inputs/preservation-gates.json`), the frozen `V(d)` value (`inputs/evaluator-rubric.json`), the subset that `d` belongs to (subset-(a) or subset-(b)), the frozen baseline's per-dim behavior at dimension `d` (from `inputs/baseline-envelope-membership.json`), and the difference between Arm M and Arm C at dimension `d`.
- Every claim of "modification succeeded at dimension `m`" must cite the frozen `A_m` acceptance test (`inputs/acceptance-tests.json`), the frozen `M` specification (`inputs/mutation-dimensions.json` + `inputs/modification-specification.txt`), the per-candidate M1..M4 + modification_conformance scores from the locked scorebooks, and the aggregated gate result.
- Every authority claim must cite the recorded authority manifest's scope (`inputs/authority-manifest.json`), grant authenticity, freshness window in seconds (3600), and the per-candidate freshness witness at the M-commit boundary (in `runs/<R>/<B>/<arm>/evidence-<N>.json`).
- Every applicability claim must cite the Applicability Declaration file (`inputs/applicability-declaration.json`) and its SHA.
- Every execution-order claim must cite the frozen algorithm SHA (`hashing/score-derivation.py`) and the recorded `draw_event_sha256` (in `preflight/execution-authority-witness.json`).

---

## §12. Per-step evidence capture (proposal v4 §14)

For each per-(R, B, arm, candidate) generation event:
- `runs/<R>/<B>/<arm>/candidate-<N>.md` — raw candidate output
- `runs/<R>/<B>/<arm>/evidence-<N>.json` — per-candidate evidence (timestamps, model, substrate, freshness witness with freshness check result)
- `runs/<R>/<B>/<arm>/runtime-failure-<N>.json` — only if runtime failure

For each per-(R, B, arm) evaluator scoring event:
- `evaluation/evaluator-A-scorebook.json` — locked content-addressed
- `evaluation/evaluator-B-scorebook.json` — locked content-addressed

For per-experiment synthesis:
- `results/score-independent.md` — locked evaluator scores
- `results/analysis.md` — reconstruction-level → per-arm → matched → pooled, with causal trace per §11
- `results/disposition.md` — the §10 disposition, with explicit cause-ruling-out for any non-arch-pass class
- `results/unblinded-analysis-results.json` — canonical record
- `results/de-blinding-table.json` — auditable

For final synthesis:
- `synthesis.md` — final adjudication; PI signs
- `REPORT-<date>-INSA-ID-E1.md` — research-level writeup

---

## §13. Model preflight (proposal v4 §6, inherited from v0.1 §13)

Before any model dispatch, the operator records:
- Model identifier (claude-opus-4-7 for executor; gpt-5.6-sol for evaluator A; claude-opus-4-7 for evaluator B)
- CLI/runtime version (claude-code CLI version; codex CLI version)
- Frozen source commit (`c3692150` for BIB; `848e0fe…` for v0.3 architecture; `ed95705` for proposal)
- Frozen source file SHA-256 (matches `MANIFEST.json`)
- Tool posture (--allowedTools '' --tools '' --disallowedTools 'WebFetch,WebSearch' for executor, per v0.1 §13)
- Authentication path (recorded in execution-authority-witness.json; SHA-256 only, never plaintext)
- Session-creation mechanism (fresh session per M-commit, per I-AUTH-05)

Any material deviation is recorded before generation and handled per the preregistered deviation rule (proposal v4 §8). STOP if deviation is material and unadjudicated.

---

## §14. Evidence chain (proposal v4 §14 cross-cut)

Per-step evidence (timestamps, model, substrate, scorebooks, raw outputs) is captured with the per-event evidence file. Locking at evaluator output means the scorebook is content-addressed at the moment of evaluator completion. The evidence profile (not evidence ladder) is the canonical structure: each step's evidence file is referenced from the next step's analysis, forming a directed evidence graph.

**Locking rule:** An evidence file is "locked" when (a) it has been written, (b) its SHA-256 has been recorded in the parent synthesis file, and (c) no edits have occurred after the SHA record. Any post-lock edit triggers a deviation record and re-locking.

---

## §15. Stop conditions (proposal v4 §5.1 INV-STOP-1, inherited from v0.1 §14)

**C20 (control validity):** Computed in Phase 2. If Arm-C fails the frozen BIB non-deviated envelope on its own (per §8 above), STOP and classify `INVALID_EXPERIMENT`. Do NOT proceed to Phase 3.

**5 INSA-BIB stop rules** (inherited from v0.1 §14):
1. **Material deviation during generation:** Any material deviation from the frozen pre-execution artifacts triggers STOP unless PI separately adjudicates.
2. **Evaluator substitution after observing candidates:** Forbidden per proposal v4 §8.
3. **Retroactive gate weakening:** Forbidden per proposal v4 §8.
4. **Decision tree semantics change:** Forbidden per proposal v4 §8 (§5.4 must remain joint, not ordered ELSE IF).
5. **Substantive → INCONCLUSIVE_PENDING_FURTHER reclassification:** Forbidden per proposal v4 §8.

Plus the §5.5 systematic thresholds T1/T2/T3 for runtime failure classification.

---

## §16. Authority boundary (proposal v4 §8)

This protocol's authorization boundary is protocol + frozen-artifact preparation only. The Frank-as-PI execution GO is a separate event recorded in `preflight/execution-authority-witness.json`.

When the execution GO is issued, the witness must include:
- This protocol's SHA (filled after `MANIFEST.json` is content-addressed)
- `MANIFEST.json` SHA
- The 16 frozen pre-execution artifact SHAs (via `MANIFEST.json`)
- The frozen INSA v0.3 source blob `848e0fe014f5b4a61ba2cb92e772ee3499dca9c1`
- The authority manifest SHA (`inputs/authority-manifest.json`)

**Until the execution GO is issued and the witness is created, no model dispatch, no evaluator invocation, no candidate generation.**

---

**End of protocol v0.2 (frozen-candidate-rev2). Awaiting Frank-as-PI execution GO.**
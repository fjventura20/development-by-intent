# Evaluator Input Packet (frozen pre-execution)

**Status:** v0.2 (frozen-candidate-rev2), pending Frank-as-PI execution GO.
**Author:** Hermes (operator).
**Date:** 2026-09-11.
**Binding:** Protocol §6 (INSA-ID-E1-protocol.md).
**v2 revision note:** v1 evaluator packet conflated per-candidate scoring with aggregate computation (G_pres_a, C12 BROKEN). v2 explicitly separates them: evaluators return per-candidate raw scores only; aggregates (G_pres_*, C12-axis-BROKEN) are computed by the analysis layer after both scorebooks are locked.

---

## What the evaluator receives

For each candidate evaluation, the evaluator receives **only**:

1. The candidate output text (the full `runs/<R>/<B>/<arm>/candidate-<N>.md` content, with all identifying metadata stripped — no reconstruction number, no arm identity, no experiment identity, no candidate number).
2. The expected output format (this packet's §"Required return format").
3. The per-axis rubric type hints (binary vs 0-4), so the evaluator knows what scorecard format to use.

**The evaluator does NOT receive:**
- Arm identity (C vs M)
- Reconstruction number (R1, R2, R3)
- Experiment identity (INSA-ID-E1)
- Candidate number within (R, B, arm)
- Any other (R, B, arm, candidate) outputs
- The frozen v0.3 architecture
- The frozen v0.1 protocol
- The INSA-ID-E1 protocol
- The proposal
- The modification specification
- The Arm C directive
- The frozen BIB envelope (`inputs/baseline-envelope-membership.json`)
- The G_pres_* thresholds or the C12 BROKEN rule (the evaluator does not know the Arm-C aggregate and must not compute the BROKEN determination)

---

## Required return format (per candidate)

For each candidate, return a JSON object with **only per-candidate raw scores**:

```json
{
  "candidate_id_blinded": "<opaque identifier assigned by operator>",
  "M_scores": {
    "M1_pass": true|false,
    "M2_pass": true|false,
    "M3_pass": true|false,
    "M4_pass": true|false,
    "modification_conformance": <0-4>,
    "candidate_all_pass": true|false
  },
  "G_subset_a_4dim_vector": {
    "BIB-4D-1_selection_significance": <0-4>,
    "BIB-4D-2_end_of_report_synthesis": true|false,
    "BIB-4D-3_lifetime_framing": <0-4>,
    "BIB-4D-4_factual_discipline": true|false
  },
  "G_subset_b_8axis_scores": {
    "C12-1_exact_date_preference": true|false,
    "C12-2_connection_count_5_to_10": <integer count>,
    "C12-3_selection_significance": <0-4>,
    "C12-4_end_of_report_synthesis": true|false,
    "C12-5_lifetime_framing": <0-4>,
    "C12-6_warm_vivid_narrative_voice": <0-4>,
    "C12-7_factual_discipline": true|false,
    "C12-8_avoidance_of_arbitrary_trivia": true|false
  },
  "evaluator_self_report": {
    "runtime_failure_observed": true|false,
    "if_runtime_failure": "<refusal/timeout/capacity/error message verbatim>"
  }
}
```

**Per-candidate axis failure conventions (used by the analysis layer to compute BROKEN):**
- For binary axes (`BIB-4D-2`, `BIB-4D-4`, `C12-1`, `C12-4`, `C12-7`, `C12-8`): failure = `false`.
- For 0-4 axes (`BIB-4D-1`, `BIB-4D-3`, `C12-3`, `C12-5`, `C12-6`): failure = score `== 0`.
- For C12-2 (count): failure = count `< 5` or count `> 10`.

These conventions are recorded here so the analysis layer has a deterministic rule. The evaluator returns raw scores only — the failure determination is the analysis layer's job, not the evaluator's.

---

## What the evaluator does NOT compute

The evaluator must **not** return any aggregate computation, including but not limited to:

- `G_mod_a`, `G_mod_b`, `G_mod_c`, `G_mod_d` (these require Arm-M pool-level or per-reconstruction aggregates and/or Arm-C comparison; the evaluator cannot see Arm-C or the reconstruction number).
- `G_pres_subset_a_a`, `G_pres_subset_a_b` (these require contemporaneous Arm-C and Arm-M reconstruction-level Manhattan means; the evaluator cannot see Arm-C or the reconstruction number).
- `C12 per-axis failure rates` (these require pool-level aggregation across Arm-M and Arm-C; the evaluator cannot see Arm-C or the experiment-level pool).
- `C12-axis-BROKEN` determinations (these require per-axis Arm-M failure rate AND Arm-M vs Arm-C comparison; the evaluator cannot see Arm-C).
- `Modification_Success`, `Non-target_Identity_Preservation`, `Modification_SSuccess`, or any experiment-level disposition.

If the evaluator returns any of these aggregate fields, the analysis layer rejects the scorebook as non-compliant and the candidate is re-scored under a deviation record.

---

## De-blinding

The operator assigns `candidate_id_blinded` to a per-(R, B, arm, candidate) tuple in `results/de-blinding-table.json` (auditable; constructed post-scoring). The de-blinding table is the only place where per-candidate raw scores are mapped to arm identity, reconstruction number, and candidate number — it is created after both scorebooks are locked.

---

## Scorebook format

The analysis layer writes the locked scorebooks as:
- `evaluation/evaluator-A-scorebook.json` — locked, content-addressed
- `evaluation/evaluator-B-scorebook.json` — locked, content-addressed

Each scorebook contains the JSON array of per-candidate return objects above, plus a `_scorebook_metadata` block with:
- `evaluator_id` (A or B)
- `evaluator_model` (gpt-5.6-sol or claude-opus-4-7)
- `lock_timestamp_utc`
- `scorebook_sha256` (SHA-256 of the scorebook bytes)
- `candidates_total` (count of per-candidate return objects)

Locking rule: a scorebook is locked when its SHA-256 has been recorded in `results/score-independent.md` and no subsequent edits have occurred. Any post-lock edit triggers a deviation record and re-locking.

---

**End of evaluator input packet v0.2 (frozen-candidate-rev2).**
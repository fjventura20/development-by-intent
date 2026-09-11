# Evaluator Input Packet (frozen pre-execution, v4)

**Status:** v0.2 (frozen-candidate-rev4), pending Frank-as-PI execution GO.
**Author:** Hermes (operator).
**Date:** 2026-09-11.
**Binding:** Protocol §6 (INSA-ID-E1-protocol.md, v4); baseline-binding.json; baseline-statistics.json; preservation-gates.json; acceptance-tests.json.

---

## What the evaluator receives

For each candidate evaluation, the evaluator receives **only**:

1. An opaque blind ID assigned by the operator (e.g., `4a8e...`). **No arm identity, no reconstruction number, no experiment identity, no candidate number, no phase indication.**
2. The full candidate output text (the produced birthday report).
3. The expected return format (the JSON shape below).

**The evaluator does NOT receive:**
- Arm identity (C vs M)
- Reconstruction number (R1, R2, R3)
- Experiment identity (INSA-ID-E1)
- Candidate number within (R, B, arm)
- Any other (R, B, arm, candidate) outputs
- The frozen v0.3 architecture, v0.1 protocol, INSA-ID-E1 protocol, proposal
- The modification specification, the Arm C directive
- The frozen BIB envelope, the G_pres_* thresholds, the C12 BROKEN rule
- The 4-dim reference vectors, the historical envelope bound
- **The phase (Phase 2 / Phase 3) or any cue from which staged arm identity could be inferred** (per v3 item 8)

---

## Blind-map / C20 join (operator-only)

Evaluator responses contain **only opaque blind IDs** (per-candidate).

**Before any evaluator invocation**, the operator constructs and locks an operator-only blind map:

```
preflight/blind-map.json  (operator-only; never visible to evaluators)
{
  "schema_version": "1.0",
  "lock_timestamp_utc": "...",
  "blind_id_to_tuple": {
    "<blind_id_1>": {"reconstruction_id": "R1", "block": "B", "arm": "C", "candidate": 1},
    "<blind_id_2>": {"reconstruction_id": "R1", "block": "B", "arm": "C", "candidate": 2},
    ...
  }
}
```

This blind map is the **only** place where blinded IDs are de-blinded. Evaluators never see it.

**After Arm-C scorebooks lock (Phase 2)**, C20 joins the locked Arm-C raw scores to the locked operator blind map to recover R/B per candidate. C20 does NOT use reconstruction_id or block from the evaluator-returned data; it uses the operator-only blind map.

**Both raw evaluator output and the operator mapping / derived joined C20 input are separately hash-bound evidence** (the raw scorebook is hashed; the C20-derived per-(R, B) cell mean is recorded in `preflight/c20-decision-record.json` with its own SHA-256 in the sidecar).

**The final public/audit de-blinding table** (`results/de-blining-table.json`) is produced later (end of Phase 4) from the operator-only blind map. The Phase-2 C20 mapping already exists in the locked operator-only artifacts (blind map + C20 decision record).

---

## Per-candidate return format (per evaluator, per candidate)

For each candidate, return a JSON object with the following fields only.

### Subset-(a) — calibrated BIB 4-dim vector (aggregate Manhattan criterion; NO per-axis binary conversion)

```json
{
  "blind_id": "<opaque blind ID from operator>",
  "M_scores": {
    "M1_pass": true|false,
    "M2_pass": true|false,
    "M3_pass": true|false,
    "M4_pass": true|false,
    "modification_conformance": <0-4 integer>,
    "candidate_all_pass": true|false
  },
  "G_subset_a_4dim_vector": {
    "contract_compliance": <0-4 integer>,
    "selection_behavior": <0-4 integer>,
    "narrative_behavior": <0-4 integer>,
    "functional_completeness": <0-4 integer>
  },
  "G_subset_b_axis_scores": {
    "C12-1": true|false,
    "C12-2": <integer count 0..N>,
    "C12-3": <0-4 integer>,
    "C12-4": true|false,
    "C12-5": <0-4 integer>,
    "C12-6": <0-4 integer>,
    "C12-7": true|false,
    "C12-8": true|false
  },
  "evaluator_self_report": {
    "runtime_failure_observed": true|false,
    "if_runtime_failure": "<refusal/timeout/capacity/error message verbatim>"
  }
}
```

### Per-axis failure conventions (subset-(b) only)

For C12-1..C12-8 (subset-(b)), the per-candidate axis failure is determined by:

- **C12-1** (binary): `failure = (C12-1 == false)`
- **C12-2** (count): `failure = (C12-2 < 5) OR (C12-2 > 10)`
- **C12-3** (0-4): `failure = (C12-3 == 0)` — INSA-ID-E1 preregistered binary-failure convention for 0-4 axes
- **C12-4** (binary): `failure = (C12-4 == absent)`
- **C12-5** (0-4): `failure = (C12-5 == 0)` — INSA-ID-E1 preregistered binary-failure convention for 0-4 axes
- **C12-6** (0-4): `failure = (C12-6 == 0)` — INSA-ID-E1 preregistered binary-failure convention for 0-4 axes
- **C12-7** (binary): `failure = (no-misrepresentation violated)`
- **C12-8** (binary): `failure = (arbitrary trivia present)`

**The 4-dim vector (subset-(a)) is NOT subjected to any per-axis binary conversion.** Subset-(a) is adjudicated ONLY through the 4-dim Manhattan aggregate criterion (G_pres_subset_a_a + G_pres_subset_a_b). The evaluator returns the raw 0-4 scores for each of the 4 dims.

### Subset-(a) vs subset-(b) — explicit separation

The 4-dim vector and the 8 C12 axes are **separate measurement families** with **non-overlapping ID namespaces** (BIB-4D-1..4 vs C12-1..8). Subset-(a) is a calibrated BIB rubric; subset-(b) is the v0.1 §11.3 historical 8 axes. v4 protocol does NOT claim any direct one-to-one semantic identity between subset-(a) and subset-(b) dimensions, even where display names happen to coincide.

### What the evaluator does NOT compute

The evaluator must **not** return any aggregate computation, including but not limited to:

- `G_mod_a`, `G_mod_b`, `G_mod_c`, `G_mod_d` (these require Arm-M pool-level or per-reconstruction aggregates; analysis-side only)
- `G_pres_subset_a_a`, `G_pres_subset_a_b` (these require contemporaneous Arm-C and Arm-M reconstruction-level Manhattan statistics; analysis-side only)
- `C12 per-axis failure rates`, `C12-axis-BROKEN` (these require pool-level aggregation; analysis-side only)
- `Modification_Success`, `Non-target_Identity_Preservation`, or any experiment-level disposition

If the evaluator returns any of these aggregate fields, the scorebook is non-compliant and the candidate is re-scored under a deviation record.

---

## Per-candidate fresh evaluator session (v3 item 8 / v4 carried)

Per v3 item 8 (carried into v4): each candidate gets a **fresh independent evaluator session**. No evaluator session is told "this is Phase 2" / "control" / "Phase 3" / or any other staged-arm cue. Phase separation is enforced ONLY at the analysis layer (post-lock), never at the evaluator session level.

The evaluator's `runtime_failure_observed` field captures per-candidate runtime issues (timeout, refusal, capacity). The operator uses this to determine per-candidate T1/T2/T3 classification (Phase 4).

---

## Per-arm scorebooks (separate, immutable)

The four scorebooks:

- `evaluation/evaluator-A-arm-C-scorebook.json` — locked after Phase 2 (C20 input). **No further appends.**
- `evaluation/evaluator-B-arm-C-scorebook.json` — locked after Phase 2. **No further appends.**
- `evaluation/evaluator-A-arm-M-scorebook.json` — locked after Phase 3. **No further appends.**
- `evaluation/evaluator-B-arm-M-scorebook.json` — locked after Phase 3. **No further appends.**

**Self-referential hash prohibition:** No scorebook file contains its own full-file SHA-256. The scorebook SHA-256s are recorded externally in `results/score-independent.md`.

---

## Locking rule (for the operator)

A scorebook is **locked** when (a) it has been written, (b) its SHA-256 has been recorded in `results/score-independent.md`, and (c) no edits have occurred after the SHA record. Any post-lock edit triggers a deviation record and re-locking.

---

**End of evaluator input packet v0.2 (frozen-candidate-rev4).**
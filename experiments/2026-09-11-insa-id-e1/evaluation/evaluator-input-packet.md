# Evaluator Input Packet (frozen pre-execution, v5)

**Status:** v0.3 (frozen-candidate-rev5), pending Frank-as-PI execution GO.
**Author:** Hermes (operator).
**Date:** 2026-09-11.
**Binding:** Protocol §6 (INSA-ID-E1-protocol.md, v5); baseline-binding.json; baseline-statistics.json; preservation-gates.json; acceptance-tests.json.

---

## What the evaluator MAY know (scoring criteria only)

The evaluator receives the following information to score each candidate deterministically. This information is sufficient to score without revealing arm identity, reconstruction number, phase, or any execution provenance.

### 1. The test prompt (the exact frozen invocation supplied to the candidate)

The evaluator sees the literal text the candidate was given:

```
Birthdate <date including year>
```

Or the exact frozen invocation as supplied (the operator records this per-candidate in the operator-only blind map; the evaluator packet substitutes the date for the opaque blind ID). Example:

```
Birthdate November 9, 1989
```

The evaluator does NOT see a T-number, a reconstruction number, an arm label, a candidate number, a phase indicator, or any other provenance.

### 2. The frozen Amazing Birthday behavioral contract (full text)

The contract that the candidate was instructed to satisfy, copied verbatim from `inputs/identity-contract.txt` (BIB c3692150 blob `7ef4356f...`). This is the contract the evaluator is scoring against.

### 3. The frozen BIB 0–4 scoring anchors for the calibrated 4-dim vector

The evaluator must score the candidate's output on each of the four BIB dimensions, using these exact anchors:

- **`contract_compliance`** (0–4): How completely the output satisfies the frozen behavioral contract.
  - 0 = materially absent or clearly wrong (fails critical requirement, e.g., no birthdate story, or presents nearby events as exact-date events)
  - 1 = recognizable but incomplete/inconsistent (e.g., covers some contract items but misses others, mild conflation)
  - 2 = covers most contract items clearly; minor gaps
  - 3 = covers nearly all contract items; very minor gaps
  - 4 = clearly satisfies the contract in all dimensions

- **`selection_behavior`** (0–4): How selective the output is (rough target 5–10 strong connections; weak filler rejected).
  - 0 = exhaustive dump with no selection; or all weak filler
  - 1 = some selection but mostly chronological dump or weak filler
  - 2 = clear selection but over- or under-includes
  - 3 = strong selection; close to 5–10 strong connections
  - 4 = strong selection; appropriate 5–10 strong connections, weak filler rejected

- **`narrative_behavior`** (0–4): How narrative-coherent the output is (connected story vs unrelated snippets; closing synthesis present).
  - 0 = unrelated snippets; no story; no closing synthesis
  - 1 = weakly connected; closing synthesis weak or absent
  - 2 = readable story; closing synthesis present but thin
  - 3 = well-connected story; clear closing synthesis
  - 4 = strong narrative; vivid, connected, with strong closing synthesis

- **`functional_completeness`** (0–4): How well the output covers the lifetime/arc + breadth + trigger behavior.
  - 0 = missing lifetime/arc coverage and breadth
  - 1 = some lifetime/arc or breadth; substantially incomplete
  - 2 = lifetime/arc present; breadth present; minor gaps
  - 3 = lifetime/arc and breadth clearly present
  - 4 = complete lifetime/arc with strong breadth

### 4. The exact M1–M4 acceptance-test definitions (matching `inputs/acceptance-tests.json`)

The evaluator returns per-candidate boolean M-scores used to compute the four G_mod gates:

- **`M1_pass`**: Does the output contain **exactly one** near-date historical event? (count == 1)
- **`M2_pass`**: Is that event within +/-30 calendar days of the birthdate?
- **`M3_pass`**: Is the event historically significant (per the criterion below)?
- **`M4_pass`**: Is the event clearly distinguished from exact-date connections in the output text (explicit label or framing distinction)?

### 5. The frozen worldwide-historical-significance criterion (M3 component)

A "historically significant worldwide event" is defined as: an event of documented global, regional, or widely-cited cultural/political/scientific/technological impact that a reasonable person would recognize as consequential (not a local/obscure occurrence). The candidate may select any one event meeting this criterion, subject to the +/-30-day window.

### 6. The C12-1..8 definitions (verbatim from `inputs/preservation-dimensions-subset-b.json`)

The evaluator scores each of the 8 C12 axes using the per-axis return type defined in §8 below. For the subjective 0-4 axes C12-3, C12-5, C12-6, the scoring guidance for distinguishing score 0 from preserved/nonzero behavior is:

- **Score 0**: The axis is **absent or materially absent** in the output. The behavior is missing entirely, present only as a vestigial mention with no substantive content, or actively violated (e.g., warm/vivid voice replaced by a list).
- **Score 1–3**: The axis is present with progressively more substantive execution. Use the same judgment as the BIB scoring anchors above (0 = materially absent/wrong; 4 = clearly satisfies; 1–3 = intermediate).
- **Score 4**: The axis is clearly and fully satisfied.

The evaluator's job is to apply these anchors. The judgment of "absent or materially absent" vs "preserved but weak" is the principal 0-vs-nonzero distinction the evaluator must make.

### 7. The current JSON return schema (exact fields)

For each candidate, return a JSON object with **exactly** these fields:

```json
{
  "blind_id": "<opaque blind ID assigned by operator>",
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

**No other fields are permitted.** The evaluator-returned record MUST NOT contain `reconstruction_id`, `block`, `arm`, `candidate`, `T-number`, `phase`, or any execution-provenance field. C20 and the operator-only blind map reconstruct R/B/arm from the blind_id; the evaluator's record is opaque to the operator except via the blind map.

### 8. Per-axis failure conventions (subset-(b) only) — what `false` / `0` means for each C12 axis

For C12-1..C12-8 (subset-(b)), the per-candidate axis failure is determined by the evaluator's return value:

- **C12-1** (binary): `failure = (C12-1 == false)` — no exact-date preference preserved
- **C12-2** (count): `failure = (C12-2 < 5) OR (C12-2 > 10)` — outside the 5-10 range
- **C12-3** (0-4): `failure = (C12-3 == 0)` — axis absent or materially absent
- **C12-4** (binary): `failure = (C12-4 == false)` — no closing synthesis
- **C12-5** (0-4): `failure = (C12-5 == 0)` — no lifetime framing
- **C12-6** (0-4): `failure = (C12-6 == 0)` — no warm/vivid voice
- **C12-7** (binary): `failure = (C12-7 == false)` — nearby events misrepresented as exact-date, or exact-date facts fabricated
- **C12-8** (binary): `failure = (C12-8 == false)` — arbitrary trivia present, filler included

**The 4-dim vector (subset-(a)) is NOT subjected to any per-axis binary conversion.** Subset-(a) is adjudicated ONLY through the 4-dim Manhattan aggregate criterion (G_pres_subset_a_a + G_pres_subset_a_b). The evaluator returns the raw 0-4 scores for each of the 4 dims.

### 9. Subset-(a) vs subset-(b) — explicit separation

The 4-dim vector and the 8 C12 axes are **separate measurement families** with **non-overlapping ID namespaces** (BIB-4D-1..4 vs C12-1..8). Subset-(a) is a calibrated BIB rubric; subset-(b) is the v0.1 §11.3 historical 8 axes. v5 protocol does NOT claim any direct one-to-one semantic identity between subset-(a) and subset-(b) dimensions, even where display names happen to coincide.

### 10. What the evaluator does NOT see

- The arm identity (C vs M)
- The reconstruction number (R1, R2, R3)
- The experiment identity (INSA-ID-E1)
- The candidate number within (R, B, arm)
- Any other (R, B, arm, candidate) outputs
- The frozen v0.3 architecture, v0.1 protocol, INSA-ID-E1 protocol, proposal
- The modification specification (`inputs/modification-specification.txt`) — **hidden** so the evaluator cannot know which M1-M4 events to expect
- The frozen BIB envelope, G_pres_* thresholds, C12 BROKEN rule
- The 4-dim reference vectors, the historical envelope bound
- The phase (Phase 2 / Phase 3) or any cue from which staged arm identity could be inferred (per v3 item 8 / v4 / v5 carried)
- T-number, block identifier, candidate number, execution provenance

### 11. Per-candidate fresh evaluator session

Per v3 item 8 (carried into v5): each candidate gets a **fresh independent evaluator session**. No evaluator session is told "this is Phase 2" / "control" / "Phase 3" / or any other staged-arm cue. Phase separation is enforced ONLY at the analysis layer (post-lock), never at the evaluator session level.

The evaluator's `runtime_failure_observed` field captures per-candidate runtime issues (timeout, refusal, capacity). The operator uses this to determine per-candidate T1/T2/T3 classification (Phase 4).

### 12. Per-candidate birthdate input

The operator-only blind map (`preflight/blind-map.json`, locked in Phase 0) maps `blind_id → {reconstruction_id, block, arm, candidate, birthdate}`. The operator substitutes the birthdate for the blind_id before invoking each evaluator session. The evaluator sees only the birthdate + the contract + the scoring criteria. The operator NEVER substitutes the M-direction; the evaluator is blind to whether the candidate is control or treatment.

### 13. Blind-map / C20 join (operator-only, locked in Phase 0)

- **Phase 0**: The operator constructs and locks `preflight/blind-map.json` (operator-only; never visible to evaluators). The blind map is the **only** place where blinded IDs are de-blinded.
- **Phase 1**: The executor (claude-opus-4-7) produces the candidate output. The output is paired with its opaque blind_id by the operator.
- **Phase 2**: Evaluators return per-candidate JSON with the blind_id. The operator constructs Phase 2 Arm-C scorebooks by joining the evaluator-returned JSON to the locked blind map to recover (R, B, arm, candidate) for each blind_id. The scorebook records the (R, B, arm, candidate) metadata in the *operator-side* record; the evaluator-returned record is the *evaluator-side* record (with the BIB 4-dim + C12 axes + M-scores + blind_id). C20 consumes the operator-side scorebook (the joined record) — NOT the raw evaluator return.
- **C20 in Phase 2**: Verifies the operator-side scorebook against the locked blind map; rejects unknown / duplicate blind IDs; recomputes per-(R, B) cell means from the BIB 4-dim vectors; applies the envelope bound. C20 does NOT use reconstruction_id or block from the evaluator-returned records.
- **After Arm-C scorebooks lock (Phase 2)**: C20 joins the locked Arm-C raw scores to the locked operator blind map to recover R/B per candidate. C20 does NOT use reconstruction_id or block from the evaluator-returned data; it uses the operator-only blind map.
- **Both raw evaluator output and the operator mapping / derived joined C20 input are separately hash-bound evidence** (the raw scorebook is hashed; the C20-derived per-(R, B) cell mean is recorded in `preflight/c20-decision-record.json` with its own SHA-256 in the sidecar).
- **The final public/audit de-blinding table** (`results/de-blinding-table.json`) is produced later (end of Phase 4) from the operator-only blind map. The Phase-2 C20 mapping already exists in the locked operator-only artifacts (blind map + C20 decision record).

### 14. C20 derived blind-map rejects (fatal)

The C20 derivation rejects (fatal nonzero exit) on:

- Any evaluator-returned record whose `blind_id` is not in the operator-only blind map (unknown blind ID)
- Any duplicate `blind_id` in the operator-side scorebook (duplicate blind ID)
- Any duplicate `(R, B, arm, candidate)` tuple in the operator-side scorebook (duplicate tuple mapping)
- Any operator-side record where `arm != C` (this is the Arm-C scorebook; Arm-M blind IDs in the Arm-C scorebook are fatal)
- Any operator-side record whose `(R, B)` is not in `{R1/B1, R2/B1, R3/B1}` (i.e., not in the preregistered current expected Arm-C cell set)
- The 3 current expected cells must all be present; missing cells are non-fatal (C20 fail = INVALID_EXPERIMENT), but unknown cells are fatal

The C20 derivation accepts runtime-failure reports (via `evaluator_self_report.runtime_failure_observed == true`): such candidates are recorded but excluded from the per-(R, B) mean computation, per the preregistered T1/T2/T3 protocol §9 runtime-failure handling.

---

## Per-arm scorebooks (separate, immutable, operator-side records)

The four scorebooks:

- `evaluation/evaluator-A-arm-C-scorebook.json` — locked after Phase 2 (C20 input). **No further appends.** Records the operator-side (R, B, arm, candidate, blind_id, scores_A) tuples joined from the blind map.
- `evaluation/evaluator-B-arm-C-scorebook.json` — locked after Phase 2. **No further appends.**
- `evaluation/evaluator-A-arm-M-scorebook.json` — locked after Phase 3. **No further appends.**
- `evaluation/evaluator-B-arm-M-scorebook.json` — locked after Phase 3. **No further appends.**

The operator-side scorebook format is per record:

```json
{
  "blind_id": "<opaque blind ID>",
  "reconstruction_id": "R1",
  "block": "B",
  "arm": "C",
  "candidate": 1,
  "scores_A": {"contract_compliance": 4, "selection_behavior": 4, "narrative_behavior": 4, "functional_completeness": 4},
  "M_scores": {"M1_pass": true, "M2_pass": true, "M3_pass": true, "M4_pass": true, "modification_conformance": 4, "candidate_all_pass": true},
  "evaluator_self_report": {"runtime_failure_observed": false}
}
```

The `(R, B, arm, candidate)` fields are operator-side — populated by the operator from the locked blind map. They are NEVER returned by the evaluator.

**Self-referential hash prohibition:** No scorebook file contains its own full-file SHA-256. The scorebook SHA-256s are recorded externally in `results/score-independent.md`.

---

## Locking rule (for the operator)

A scorebook is **locked** when (a) it has been written, (b) its SHA-256 has been recorded in `results/score-independent.md`, and (c) no edits have occurred after the SHA record. Any post-lock edit triggers a deviation record and re-locking.

---

**End of evaluator input packet v0.3 (frozen-candidate-rev5).**
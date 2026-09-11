# Evaluator Input Packet (frozen pre-execution, v6)

**Status:** v0.4 (frozen-candidate-rev6), pending Frank-as-PI execution GO.
**Author:** Hermes (operator).
**Date:** 2026-09-11.
**Binding:** Protocol §6 (INSA-ID-E1-protocol.md, v6); baseline-binding.json; baseline-statistics.json; preservation-gates.json; acceptance-tests.json; test-invocations.json; normalize-and-join.py.

---

## What the evaluator MAY know (scoring criteria only)

The evaluator receives the following information to score each candidate deterministically. This information is sufficient to score without revealing arm identity, reconstruction number, phase, or any execution provenance.

### 1. The exact test prompt / birthdate (per candidate, deterministically supplied)

The operator (NOT the executor) substitutes the birthdate for the opaque blind_id using the frozen `inputs/test-invocations.json` (frozen content-addressed). The evaluator sees the literal text the candidate was given, e.g.:

```
Birthdate November 9, 1989
```

The operator NEVER shows a T-number, a reconstruction number, an arm label, a candidate number, a phase indicator, or any other provenance. The 5 distinct test prompts T1..T5 are repeated twice (run-1 and run-2) per (R, B) cell; the run index is an internal design detail not exposed to the evaluator.

### 2. The frozen Amazing Birthday behavioral contract (full text)

The contract that the candidate was instructed to satisfy, copied verbatim from `inputs/identity-contract.txt` (BIB c3692150 blob `7ef4356f...`). This is the contract the evaluator is scoring against.

### 3. The exact historical BIB 0–4 scoring anchors for the calibrated 4-dim vector (verbatim from the frozen BIB evaluator rubric)

The four dimensions are the **exact** 0-4 rubrics from `experiments/2026-09-05-dbi-bib-001-rerun-001/inputs/EVALUATOR-RUBRIC.md` (the rubric used to produce the 85-record calibration). The current evaluator packet reproduces the verbatim text of each anchor so that current Arm-C and Arm-M candidates are scored against the **same measurement rubric that generated the frozen BIB baseline**.

#### A. Contract Compliance — 0–4

Evaluates the frozen behavioral and factual contract as a whole, including exact-date vs nearby-event discipline, explanation of significance, lifetime framing, and completion of the expected report behavior.

- **4 — Full:** Core contract is satisfied throughout. Exact-date/nearby distinctions are disciplined; significance and lifetime framing are present; no material contract violation.
- **3 — Strong:** Contract is substantially satisfied with one or a few localized minor defects that do not alter recognizable behavior.
- **2 — Mixed:** The application is recognizable but one material contract behavior is weak, omitted, or violated; multiple minor defects may also be present.
- **1 — Poor:** Several core contract behaviors are absent or materially violated. Only fragments of Amazing Birthday remain recognizable.
- **0 — Absent/wrong:** Output does not implement the Amazing Birthday contract or is effectively a different task/application.

#### B. Selection Behavior — 0–4

Evaluates curation, significance, exact-date preference, avoidance of filler, and resistance to chronology dumping.

- **4 — Curated:** Roughly 5–10 high-value connections; strong exact-date preference where warranted; weak trivia omitted; ordering reflects narrative value.
- **3 — Mostly curated:** Strong overall selection with a small amount of filler, a modest count deviation, or one weaker choice.
- **2 — Mixed:** Meaningful choices coexist with noticeable filler, weak prioritization, or partial chronology behavior.
- **1 — Weak:** Mostly arbitrary facts, filler, or near-exhaustive chronology; selection policy is difficult to recognize.
- **0 — Absent:** No meaningful curation or selection behavior consistent with the application.

#### C. Narrative Behavior — 0–4

Evaluates explanatory synthesis, warm/vivid voice, connection to the person's lifetime, and ending synthesis rather than raw fact listing.

- **4 — Full narrative:** Engaging, explanatory, repeatedly tied to the lifetime arc, and ends with substantive synthesis.
- **3 — Strong narrative:** Clearly narrative and interpretive, with minor weakness in voice, lifetime linkage, or closing synthesis.
- **2 — Mixed:** Some explanation and lifetime framing, but substantial portions read as a fact list or generic history summary.
- **1 — Weak:** Mostly encyclopedic/list-like; little meaningful lifetime interpretation or synthesis.
- **0 — Absent:** No recognizable Amazing Birthday narrative behavior.

#### D. Functional Completeness — 0–4

Evaluates whether the candidate performs all major externally observable behaviors required by the frozen contract.

- **4 — Complete:** All major behaviors are present; any omissions are incidental.
- **3 — Substantially complete:** One minor behavior is thin or missing, but the report remains functionally complete.
- **2 — Partially complete:** One major behavior is missing or substantially underperformed, but the application remains recognizable.
- **1 — Incomplete:** Multiple major behaviors are missing; output only partially performs the application.
- **0 — Nonfunctional:** It does not meaningfully perform the application.

Intermediate judgment uses the closest anchor; do not use half-points.

### 4. The exact M1–M4 acceptance-test definitions (matching `inputs/acceptance-tests.json`)

The evaluator returns per-candidate boolean M-scores used to compute the four G_mod gates:

- **`M1_pass`**: Does the output contain **exactly one** near-date historical event? (count == 1)
- **`M2_pass`**: Is that event within +/-30 calendar days of the birthdate?
- **`M3_pass`**: Is the event historically significant (per the criterion below)?
- **`M4_pass`**: Is the event clearly distinguished from exact-date connections in the output text (explicit label or framing distinction)?

### 5. The frozen worldwide-historical-significance rubric (M3 component, preregistered per v0.1 §9.2 PI pass 3)

A nearby event satisfies M3 only if **at least two** of the following four criteria are met (not disjunctive — must satisfy ≥ 2):

1. It is treated by mainstream general-reference or historical sources as an event of international or world-historical significance.
2. It directly involved, affected, or materially concerned multiple sovereign states or more than one major world region or continent.
3. It produced durable political, economic, scientific, technological, military, social, or cultural consequences extending materially beyond its place of origin.
4. It would reasonably merit inclusion in a concise one-page global-history chronology or summary for that year.

An event that is primarily local, regional, anecdotal, celebrity-oriented, or trivial does NOT pass merely because it occurred within the ±30-day window. **No date-specific examples** in the frozen evaluator materials. The rubric is generic.

M3 remains binary: PASS only if at least two criteria are satisfied.

### 6. The C12-1..8 definitions (verbatim from `inputs/preservation-dimensions-subset-b.json`)

The evaluator scores each of the 8 C12 axes using the per-axis return type defined in §7 below. For the subjective 0-4 axes C12-3, C12-5, C12-6, the scoring guidance for distinguishing score 0 from preserved/nonzero behavior is:

- **Score 0**: The axis is **absent or materially absent** in the output. The behavior is missing entirely, present only as a vestigial mention with no substantive content, or actively violated (e.g., warm/vivid voice replaced by a list).
- **Score 1–3**: The axis is present with progressively more substantive execution. Use the same judgment as the BIB scoring anchors above (0 = materially absent/wrong; 4 = clearly satisfies; 1–3 = intermediate).
- **Score 4**: The axis is clearly and fully satisfied.

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

**No other fields are permitted.** The evaluator-returned record MUST NOT contain `reconstruction_id`, `block`, `arm`, `candidate`, `T-number`, `phase`, or any execution-provenance field. The operator (`hashing/normalize-and-join.py`) joins each evaluator-returned record to the locked blind map to recover (R, B, arm, candidate, birthdate); the operator-supplied metadata is verified against the blind map (fatal nonzero on mismatch).

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

The 4-dim vector and the 8 C12 axes are **separate measurement families** with **non-overlapping ID namespaces** (BIB-4D-1..4 vs C12-1..8). Subset-(a) is a calibrated BIB rubric; subset-(b) is the v0.1 §11.3 historical 8 axes. v6 protocol does NOT claim any direct one-to-one semantic identity between subset-(a) and subset-(b) dimensions, even where display names happen to coincide.

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
- The phase (Phase 2 / Phase 3) or any cue from which staged arm identity could be inferred (per v3 item 8 / v4 / v5 / v6 carried)
- T-number, block identifier, candidate number, execution provenance
- The frozen test-invocations.json (the evaluator sees only the substituted birthdate string, not the test_id/run/etc.)

### 11. Per-candidate fresh evaluator session

Per v3 item 8 (carried into v6): each candidate gets a **fresh independent evaluator session**. No evaluator session is told "this is Phase 2" / "control" / "Phase 3" / or any other staged-arm cue. Phase separation is enforced ONLY at the analysis layer (post-lock), never at the evaluator session level.

The evaluator's `runtime_failure_observed` field captures per-candidate runtime issues (timeout, refusal, capacity). The operator uses this to determine per-candidate T1/T2/T3 classification (Phase 4).

### 12. Per-candidate birthdate input (deterministic)

The operator-only blind map (`preflight/blind-map.json`, locked in Phase 0) maps `blind_id → {reconstruction_id, block, arm, candidate, birthdate, test_id, run}`. The birthdate is the exact frozen test invocation from `inputs/test-invocations.json` (e.g., `"Birthdate November 9, 1989"`). The operator substitutes the birthdate for the blind_id before invoking each evaluator session. The evaluator NEVER knows whether the candidate is control or treatment.

### 13. Blind-map / operator-side-scorebook / C20 join (operator-only, deterministic)

- **Phase 0**: The operator constructs and locks `preflight/blind-map.json` (operator-only; never visible to evaluators). The blind map is the **only** place where blinded IDs are de-blinded.
- **Phase 1**: The executor (claude-opus-4-7) produces the candidate output. The output is paired with its opaque blind_id by the operator.
- **Phase 2**: Evaluators return per-candidate JSON with the blind_id. The operator runs `hashing/normalize-and-join.py` (frozen, deterministic, content-addressed) which joins the evaluator-returned records to the locked blind map to build the operator-side Arm-C scorebooks. The script preserves all 4-dim + 8 C12 + M scores + evaluator_self_report; adds R/B/arm/candidate/birthdate/test_id/run solely from the blind map; rejects unknown / duplicate blind IDs, duplicate tuples, and any operator-metadata mismatch (fatal nonzero on any of these). C20 then consumes the operator-side scorebook.
- **C20 in Phase 2**: Verifies the operator-side scorebook against the locked blind map; rejects unknown / duplicate blind IDs; rejects duplicate `(R, B, arm, candidate)` tuples; rejects arm != expected; rejects `(R, B)` cells outside the preregistered current expected cells; uses the preregistered historical envelope bound.
- **The final public/audit de-blinding table** (`results/de-blinding-table.json`) is produced later (end of Phase 4) from the operator-only blind map. The Phase-2 C20 mapping already exists in the locked operator-only artifacts (blind map + C20 decision record).

### 14. C20 derived blind-map rejects (fatal)

The C20 derivation rejects (fatal nonzero exit) on:

- Any evaluator-returned record whose `blind_id` is not in the operator-only blind map (unknown blind ID)
- Any duplicate `blind_id` in the operator-side scorebook (duplicate blind ID)
- Any duplicate `(R, B, arm, candidate)` tuple in the operator-side scorebook (duplicate tuple mapping)
- Any operator-side record where `arm != C` (this is the Arm-C scorebook; Arm-M blind IDs in Arm-C scorebook are fatal)
- Any operator-side record whose `(R, B)` is not in `{R1/B1, R2/B1, R3/B1}` (i.e., not in the preregistered current expected Arm-C cell set)
- The 3 current expected cells must all be present; missing cells are non-fatal (C20 fail = INVALID_EXPERIMENT), but unknown cells are fatal

The C20 accepts evaluator-runtime-failure reports (via `evaluator_self_report.runtime_failure_observed == true`): such candidates are recorded but excluded from the per-(R, B) mean computation, per the preregistered T1/T2/T3 protocol §9 runtime-failure handling.

---

## Per-arm scorebooks (separate, immutable, operator-side records, full payload preserved)

The four scorebooks:

- `evaluation/evaluator-A-arm-C-scorebook.json` — locked after Phase 2 (C20 input). **No further appends.** Records the operator-side (blind_id, reconstruction_id, block, arm, candidate, birthdate, test_id, run, scores_A, M_scores, G_subset_b_axis_scores, evaluator_self_report) tuples joined from the blind map.
- `evaluation/evaluator-B-arm-C-scorebook.json` — locked after Phase 2. **No further appends.**
- `evaluation/evaluator-A-arm-M-scorebook.json` — locked after Phase 3. **No further appends.**
- `evaluation/evaluator-B-arm-M-scorebook.json` — locked after Phase 3. **No further appends.**

**Full payload preservation:** Every locked scorebook retains the full raw scoring payload, including all 8 C12 axes (G_subset_b_axis_scores). The Phase-4 analysis consumes the locked C12 values directly to compute C12 per-axis failure rates and the BROKEN rule.

The operator-side scorebook format is per record:

```json
{
  "blind_id": "<from evaluator return + blind map>",
  "reconstruction_id": "<from blind map; NEVER from evaluator return>",
  "block": "<from blind map>",
  "arm": "<from blind map>",
  "candidate": "<from blind map>",
  "birthdate": "<from blind map>",
  "test_id": "<from blind map>",
  "run": "<from blind map>",
  "scores_A": {"contract_compliance": <0-4>, "selection_behavior": <0-4>, "narrative_behavior": <0-4>, "functional_completeness": <0-4>},
  "M_scores": {"M1_pass": bool, "M2_pass": bool, "M3_pass": bool, "M4_pass": bool, "modification_conformance": <0-4>, "candidate_all_pass": bool},
  "G_subset_b_axis_scores": {"C12-1": bool, "C12-2": <int count>, "C12-3": <0-4>, "C12-4": bool, "C12-5": <0-4>, "C12-6": <0-4>, "C12-7": bool, "C12-8": bool},
  "evaluator_self_report": {"runtime_failure_observed": bool, "if_runtime_failure": "<verbatim>"}
}
```

The (R, B, arm, candidate, birthdate, test_id, run) fields are NEVER returned by the evaluator. They are recovered by `hashing/normalize-and-join.py` from the locked blind map; the script verifies each field matches the blind map (fatal nonzero on mismatch).

**Self-referential hash prohibition:** No scorebook file contains its own full-file SHA-256. The scorebook SHA-256s are recorded externally in `results/score-independent.md`. C20 decision record (`preflight/c20-decision-record.json`) also does NOT contain its own full-file SHA-256.

---

## Locking rule (for the operator)

A scorebook is **locked** when (a) it has been written, (b) its SHA-256 has been recorded in `results/score-independent.md`, and (c) no edits have occurred after the SHA record. Any post-lock edit triggers a deviation record and re-locking.

---

**End of evaluator input packet v0.4 (frozen-candidate-rev6).**
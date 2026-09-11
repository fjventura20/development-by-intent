# Evaluator Input Packet (frozen pre-execution)

**Status:** v0.1 (frozen-candidate).
**Author:** Hermes (operator).
**Date:** 2026-09-11.
**Binding:** Protocol §6 (INSA-ID-E1-protocol.md).

---

## What the evaluator receives

For each candidate evaluation, the evaluator receives **only**:

1. The candidate output text (the full `runs/<R>/<B>/<arm>/candidate-<N>.md` content, with all identifying metadata stripped — no reconstruction number, no arm identity, no experiment identity, no candidate number).
2. The relevant rubric excerpt (acceptance test rubric for M-evaluators; preservation gate rubric for G-evaluators; see below).
3. The expected output format (this packet's §"Required return format").

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

---

## Rubric excerpts

### For M-evaluators (Modification_Success scoring)

Per `inputs/acceptance-tests.json` A-mod-a / A-mod-b:

- T1: exactly one near-date event present in the output (count == 1)
- T2: the event date is within +/-30 calendar days of the birth date
- T3: the event is historically significant (operator-judged pre-piloted rubric; matches v0.1 evaluator packet template §B)
- T4: the event is clearly distinguished from exact-date connections in the output text (explicit label or framing distinction)

**Pass rule:** All four T1..T4 must PASS for the test to PASS.

### For G-evaluators (Non-target_Identity_Preservation scoring)

#### Subset-(a) — calibrated BIB 4-dim vector

Score the candidate on the 4 dimensions:
1. Selection significance (0-4)
2. End-of-report synthesis (binary: present/absent)
3. Lifetime framing (0-4)
4. Factual discipline (binary: no nearby events misrepresented as exact-date)

Compute the **Manhattan distance** between the candidate's 4-dim vector and the historical BIB 4-dim mean (from `inputs/baseline-envelope-membership.json`).

**Pass rule:**
- G_pres_a: candidate's Manhattan distance from BIB mean <= contemporaneous-Arm-C-M-distance-from-BIB-mean + 1.5 (the +1.5 tolerance applies only to this G_pres_a relative criterion; the +1.5 is NOT added to the contemporaneous Arm C distance used for C20)
- G_pres_b: candidate's Manhattan distance from BIB mean <= 2.5 absolute

#### Subset-(b) — 8 C12 axes

Score the candidate on each of the 8 axes independently:
1. C12-1: exact-date preference (binary: preserved/not-preserved)
2. C12-2: connection count of 5-10 (operator-counted after evaluation)
3. C12-3: selection significance (0-4, within historical BIB calibration)
4. C12-4: end-of-report synthesis (binary)
5. C12-5: lifetime framing (0-4)
6. C12-6: warm/vivid narrative voice (0-4)
7. C12-7: factual discipline (binary: no nearby events misrepresented as exact-date)
8. C12-8: avoidance of arbitrary trivia (binary)

**Pass rule:** All 8 axes must PASS (no C12-axis-BROKEN). A per-axis C12-axis-BROKEN call is a hard fail on that axis.

---

## Required return format

For each candidate, return a JSON object:

```json
{
  "candidate_id_blinded": "<opaque identifier assigned by operator>",
  "M_score": {
    "T1_pass": true|false,
    "T2_pass": true|false,
    "T3_pass": true|false,
    "T4_pass": true|false,
    "rationale_per_test": "<one sentence per test>"
  },
  "G_subset_a_score": {
    "BIB-4D-1": <0-4>,
    "BIB-4D-2": <binary>,
    "BIB-4D-3": <0-4>,
    "BIB-4D-4": <binary>,
    "manhattan_distance_from_bib_mean": <number>,
    "G_pres_a_pass": true|false,
    "G_pres_b_pass": true|false
  },
  "G_subset_b_score": {
    "C12-1": <binary>,
    "C12-2": <count>,
    "C12-3": <0-4>,
    "C12-4": <binary>,
    "C12-5": <0-4>,
    "C12-6": <0-4>,
    "C12-7": <binary>,
    "C12-8": <binary>,
    "any_c12_axis_broken": true|false
  },
  "evaluator_self_report": {
    "runtime_failure_observed": true|false,
    "if_runtime_failure": "<refusal/timeout/capacity/error message verbatim>"
  }
}
```

The operator assigns the `candidate_id_blinded` to a per-(R, B, arm, candidate) tuple in `results/de-blinding-table.json` (auditable; constructed post-scoring).

---

**End of evaluator input packet v0.1 (frozen-candidate).**
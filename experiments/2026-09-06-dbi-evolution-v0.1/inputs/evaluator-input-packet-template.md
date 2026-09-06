# DBI-Evolution Evaluator Input Packet (TEMPLATE — used to build evaluator packets)

## Instructions to evaluator

This packet contains a frozen behavioral contract, a frozen scoring rubric, and 60 candidate outputs
from an experiment testing whether a controlled intent modification can be expressed while preserving
the application's behavioral identity. Each candidate is identified only by a blind ID. You must score
every candidate using the rubric below. You do not know which candidates came from the control arm and
which came from the modified arm. Do not try to infer it.

## Materials visible to you

1. Section 1 - the frozen Amazing Birthday behavioral contract
2. Section 2 - the frozen BIB evaluator rubric (extended with M1-M4)
3. Section 3 - the 8 C12 non-target axes checks
4. Section 4 - the 60 candidate records (each: blind ID, exact test prompt text, raw candidate output)

## Materials NOT visible to you

- Reconstruction identity (R1-R6 for Arm C, R7-R9 for Arm M-equivalent; you see none of this)
- Arm C / Arm M identity
- T1-T5 labels (only the test prompt text is shown)
- Modification specification text
- Treatment assignment
- Operator blind map
- Any other evaluator's scores

## Section 1 - Frozen behavioral contract

<<03-behavioral-baseline.md content>>

## Section 2 - Frozen BIB evaluator rubric + M1-M4

The four-dimensional BIB behavior vector (contract_compliance, selection_behavior,
narrative_behavior, functional_completeness) is the primary calibrated identity metric.
Score each dimension 0-4 per the BIB rubric.

In addition, score the following four modification-conformance checks (M1-M4) for EVERY candidate
(scorers do not know which arm each candidate came from):

- **M1**: A qualifying event within +/-30 calendar days of the supplied birth date is included
  in the report. (binary 0/1)
- **M2**: Exactly one such event is included (not zero, not multiple). (binary 0/1)
- **M3**: The event is clearly distinguished from exact-date connections (labeled as "around that
  time", "in the same month", "in the days before/after", or otherwise temporally marked as not
  exact-date). (binary 0/1)
- **M4**: The event satisfies the worldwide-historical-significance rubric (see Section 3 below). (binary 0/1)

`modification_conformance = M1 + M2 + M3 + M4` (integer 0-4).

## Section 3 - Worldwide-historical-significance rubric (M4)

A nearby event satisfies M4 only if it meets at least two of the following four criteria:

1. It is treated by mainstream general-reference or historical sources as an event of
   international or world-historical significance.
2. It directly involved, affected, or materially concerned multiple sovereign states or
   more than one major world region or continent.
3. It produced durable political, economic, scientific, technological, military, social, or
   cultural consequences extending materially beyond its place of origin.
4. It would reasonably merit inclusion in a concise one-page global-history chronology or
   summary for that year.

An event that is primarily local, regional, anecdotal, celebrity-oriented, or trivial does NOT pass
merely because it occurred within the +/-30-day window.

(No date-specific examples are provided here. Apply the rubric to whatever nearby event the report
mentions.)

## Section 4 - 8 non-target axes (C12) - report per candidate

For each candidate, score the following 8 axes. These are behavioral guardrails that should remain
preserved across the two arms. Report the failure rate per arm later (operator does this post-unblind).

1. exact-date preference preserved (binary)
2. connection count of 5-10 (operator counts after evaluation)
3. selection significance (subjective 0-4)
4. end-of-report synthesis present (binary)
5. lifetime framing (subjective 0-4)
6. warm/vivid narrative voice (subjective 0-4)
7. factual discipline (no nearby events misrepresented as exact-date) (binary)
8. avoidance of arbitrary trivia (no filler events that weren't there in BIB) (binary)

## Required return format

Return a JSON array of 60 records (one per candidate, in the same order as Section 4). Each record must include:
- blind_id
- trigger_recognition ("PASS"/"FAIL")
- contract_compliance (0-4)
- selection_behavior (0-4)
- narrative_behavior (0-4)
- functional_completeness (0-4)
- total_score (0-16)
- violations (array of {severity, description})
- identity_classification ("SAME"/"SAME_WITH_VARIANCE"/"DIFFERENT")
- modification_conformance (0-4)
- M1, M2, M3, M4 (each 0/1)
- c12_axes (object with axes 1-8: each its appropriate type)
- rationale (string)
- factual_verification_notes (string, may be empty)
- evaluator_id ("A" or "B")
- evaluator_model (e.g. "gpt-5.6-sol" or "claude-opus-4-7")
- scored_at_utc (ISO 8601)

Do NOT include any reconstruction_id, block, test_id, arm, or provenance information - these are
deliberately withheld from you.

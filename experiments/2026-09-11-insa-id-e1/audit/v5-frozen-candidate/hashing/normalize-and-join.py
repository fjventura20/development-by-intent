#!/usr/bin/env python3
"""
INSA-ID-E1 evaluator-return → operator-side scorebook normalization/join
script (frozen pre-execution, v6).

Takes the raw evaluator-return JSON (in the exact blinded schema from
evaluation/evaluator-input-packet.md §7) and joins it against the locked
operator-only blind map to produce the immutable operator-side Arm-C (or
Arm-M) scorebook.

Inputs:
  --raw-returns PATH        JSON file (list of records in the evaluator-return
                            schema: blind_id, M_scores, G_subset_a_4dim_vector,
                            G_subset_b_axis_scores, evaluator_self_report).
                            Evaluator-returned records MUST NOT contain
                            reconstruction_id, block, arm, candidate, T-number,
                            phase, or any other execution-provenance field.
  --blind-map PATH          Operator-only blind map (preflight/blind-map.json,
                            locked in Phase 0). Maps blind_id -> (R, B, arm,
                            candidate, birthdate). The test invocation
                            (Birthdate) is the exact frozen test from
                            inputs/test-invocations.json.
  --arm STR                 "C" or "M". The script verifies that the blind-map's
                            arm for every record matches this value (rejects
                            Arm-M blind IDs in Arm-C scorebook, etc.).
  --expected-current-cells  Comma-separated list of (R, B) cell strings the
                            scorebook must cover (e.g., "R1/B1,R2/B1,R3/B1").
  --out PATH                Output JSON file (immutable operator-side scorebook).
  --score-field-suffix STR  Suffix for the score field in the output ("A" or "B").

Output (each record in --out):
  {
    "blind_id": <from raw>,
    "reconstruction_id": <from blind map; R/B/arm/candidate NOT from raw>,
    "block": <from blind map>,
    "arm": <from blind map>,
    "candidate": <from blind map; uses the (R, B, test, run) canonical tuple>,
    "birthdate": <from blind map; the exact frozen test invocation>,
    "test_id": <from blind map; the frozen T-number like "T1", "T2", ...>,
    "run": <from blind map; 1 or 2 (the within-test repeat index)>,
    "scores_<X>": <from raw G_subset_a_4dim_vector>,
    "M_scores": <from raw>,
    "G_subset_b_axis_scores": <from raw; PRESERVED in locked scorebook>,
    "evaluator_self_report": <from raw>,
  }

Rules enforced (fatal nonzero exit on any violation):
  - Every raw record's blind_id must be in the blind map (rejects unknown blind IDs).
  - No duplicate blind_id in the raw records (rejects duplicate blind IDs).
  - No duplicate (R, B, arm, candidate) tuple after the join (rejects duplicate tuples).
  - Every blind-map (R, B, arm) must match the expected --arm value (rejects Arm-M in Arm-C scorebook, etc.).
  - The set of (R, B) cells in the joined scorebook must exactly equal the set of --expected-current-cells.
  - The score field (scores_A or scores_B) must be a dict with all 4 BIB dimensions, each an integer 0-4.
  - The G_subset_b_axis_scores field must be a dict with all 8 C12 axes.
  - The M_scores field must contain the 5 keys (M1_pass, M2_pass, M3_pass, M4_pass, modification_conformance, candidate_all_pass).
  - The evaluator_self_report.runtime_failure_observed must be a boolean.

C20 and the operator-side analysis layer consume the operator-side scorebook directly.
R/B/arm/candidate/birthdate are NEVER taken from the evaluator-returned data; they
are recovered exclusively from the blind map (per proposal v5.1 §5.1 INV-G-1 + v6
corrections). Operator metadata mismatch is FATAL.
"""

import argparse
import json
import os
import sys


EXPECTED_BIB_DIMS = ['contract_compliance', 'selection_behavior', 'narrative_behavior', 'functional_completeness']
EXPECTED_C12_IDS = ['C12-1', 'C12-2', 'C12-3', 'C12-4', 'C12-5', 'C12-6', 'C12-7', 'C12-8']
EXPECTED_M_KEYS = ['M1_pass', 'M2_pass', 'M3_pass', 'M4_pass', 'modification_conformance', 'candidate_all_pass']


def fail(msg):
    print(f'FATAL: {msg}', file=sys.stderr)
    sys.exit(2)


def main():
    ap = argparse.ArgumentParser(description='INSA-ID-E1 v6 evaluator-return normalizer + blind-map join')
    ap.add_argument('--raw-returns', required=True, help='JSON file of evaluator-returned records (exact schema in evaluation/evaluator-input-packet.md §7)')
    ap.add_argument('--blind-map', required=True, help='Operator-only blind map (preflight/blind-map.json)')
    ap.add_argument('--arm', required=True, choices=['C', 'M'], help='Expected arm of the scorebook')
    ap.add_argument('--expected-current-cells', required=True, help='Comma-separated (R, B) cell strings the scorebook must cover (e.g., "R1/B1,R2/B1,R3/B1")')
    ap.add_argument('--out', required=True, help='Output operator-side scorebook JSON')
    ap.add_argument('--score-field-suffix', required=True, choices=['A', 'B'], help='Suffix for the score field (A or B)')
    args = ap.parse_args()

    # Load blind map
    with open(args.blind_map) as f:
        blind_map_data = json.load(f)
    blind_map = blind_map_data.get('blind_id_to_tuple', blind_map_data)
    if not isinstance(blind_map, dict):
        fail(f'blind map {args.blind_map} missing "blind_id_to_tuple" mapping')

    # Load raw evaluator returns
    with open(args.raw_returns) as f:
        raw_returns = json.load(f)
    if not isinstance(raw_returns, list):
        fail(f'raw returns {args.raw_returns} must be a JSON list of records')

    expected_cells = set(s.strip() for s in args.expected_current_cells.split(','))
    arm = args.arm
    score_field = f'scores_{args.score_field_suffix}'

    seen_blind_ids = set()
    seen_tuples = set()
    out_records = []
    score_field_seen = set()

    for idx, raw in enumerate(raw_returns):
        # Validate top-level shape
        for k in ['blind_id', 'M_scores', 'G_subset_a_4dim_vector', 'G_subset_b_axis_scores', 'evaluator_self_report']:
            if k not in raw:
                fail(f'raw record {idx} missing required field {k!r}; got keys {list(raw.keys())}')

        # Validate forbidden provenance fields (per v6: evaluator-returned records MUST NOT contain R/B/arm/candidate)
        for forbidden in ['reconstruction_id', 'block', 'arm', 'candidate', 'T-number', 'phase', 'experiment_id']:
            if forbidden in raw:
                fail(f'raw record {idx} contains forbidden provenance field {forbidden!r}; evaluator-returned records MUST NOT contain R/B/arm/candidate or execution provenance')

        bid = raw['blind_id']
        if bid in seen_blind_ids:
            fail(f'duplicate blind_id {bid!r} in raw returns (record {idx})')
        seen_blind_ids.add(bid)
        if bid not in blind_map:
            fail(f'unknown blind_id {bid!r} (not in blind map) (record {idx})')

        mapped = blind_map[bid]
        # Reject any operator metadata mismatch (R/B/arm must equal blind-map values)
        for k in ['reconstruction_id', 'block', 'arm', 'candidate', 'birthdate', 'test_id', 'run']:
            if k in raw:
                if raw[k] != mapped.get(k):
                    fail(f'raw record {idx} blind_id {bid!r} field {k!r}={raw[k]!r} does not match blind map {mapped.get(k)!r}')

        rec_arm = mapped.get('arm')
        if rec_arm != arm:
            fail(f'raw record {idx} blind_id {bid!r} maps to arm={rec_arm!r}; this is the arm={arm} scorebook (fatal)')

        # Validate score field
        scores = raw['G_subset_a_4dim_vector']
        if not isinstance(scores, dict):
            fail(f'raw record {idx} G_subset_a_4dim_vector must be a dict, got {type(scores).__name__}')
        for d in EXPECTED_BIB_DIMS:
            if d not in scores:
                fail(f'raw record {idx} G_subset_a_4dim_vector missing dim {d!r}; got keys {list(scores.keys())}')
            if not isinstance(scores[d], int) or scores[d] < 0 or scores[d] > 4:
                fail(f'raw record {idx} G_subset_a_4dim_vector[{d!r}] = {scores[d]!r}; must be int in 0..4')

        # Validate M_scores
        m_scores = raw['M_scores']
        if not isinstance(m_scores, dict):
            fail(f'raw record {idx} M_scores must be a dict, got {type(m_scores).__name__}')
        for k in EXPECTED_M_KEYS:
            if k not in m_scores:
                fail(f'raw record {idx} M_scores missing {k!r}; got keys {list(m_scores.keys())}')

        # Validate G_subset_b_axis_scores
        c12 = raw['G_subset_b_axis_scores']
        if not isinstance(c12, dict):
            fail(f'raw record {idx} G_subset_b_axis_scores must be a dict, got {type(c12).__name__}')
        for c in EXPECTED_C12_IDS:
            if c not in c12:
                fail(f'raw record {idx} G_subset_b_axis_scores missing axis {c!r}; got keys {list(c12.keys())}')

        # Validate evaluator_self_report
        esr = raw['evaluator_self_report']
        if not isinstance(esr, dict):
            fail(f'raw record {idx} evaluator_self_report must be a dict, got {type(esr).__name__}')
        if 'runtime_failure_observed' not in esr:
            fail(f'raw record {idx} evaluator_self_report missing runtime_failure_observed')
        if not isinstance(esr['runtime_failure_observed'], bool):
            fail(f'raw record {idx} evaluator_self_report.runtime_failure_observed must be bool, got {type(esr["runtime_failure_observed"]).__name__}')

        # Build the operator-side record (joining evaluator return + blind map)
        tup = (mapped['reconstruction_id'], mapped['block'], mapped['arm'], mapped['candidate'])
        if tup in seen_tuples:
            fail(f'duplicate tuple {tup} in operator-side scorebook (record {idx})')
        seen_tuples.add(tup)

        out_record = {
            'blind_id': bid,
            'reconstruction_id': mapped['reconstruction_id'],
            'block': mapped['block'],
            'arm': mapped['arm'],
            'candidate': mapped['candidate'],
            'birthdate': mapped.get('birthdate'),
            'test_id': mapped.get('test_id'),
            'run': mapped.get('run'),
            score_field: scores,
            'M_scores': m_scores,
            'G_subset_b_axis_scores': c12,
            'evaluator_self_report': esr,
        }
        out_records.append(out_record)
        score_field_seen.add(scores['contract_compliance'])  # sanity

    # Verify the set of (R, B) cells exactly matches the expected current cells
    actual_cells = set(f'{r["reconstruction_id"]}/{r["block"]}' for r in out_records)
    if actual_cells != expected_cells:
        missing = expected_cells - actual_cells
        extra = actual_cells - expected_cells
        fail(f'operator-side scorebook (R, B) cell set mismatch: missing={sorted(missing)}; extra={sorted(extra)}; expected={sorted(expected_cells)}; got={sorted(actual_cells)}')

    # Atomic write
    tmp = args.out + '.tmp'
    with open(tmp, 'w') as f:
        json.dump(out_records, f, indent=2)
        f.write('\n')
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp, args.out)

    print(f'WROTE: {args.out} ({len(out_records)} records, {len(actual_cells)} cells)')
    print(f'  expected cells: {sorted(expected_cells)}')
    print(f'  actual cells:   {sorted(actual_cells)}')
    print(f'  arm:            {arm}')
    print(f'  score field:    {score_field}')


if __name__ == '__main__':
    main()
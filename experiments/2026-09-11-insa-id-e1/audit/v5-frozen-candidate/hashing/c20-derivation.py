#!/usr/bin/env python3
"""
INSA-ID-E1 C20 derivation (frozen pre-execution, v6).

Frozen deterministic C20 derivation. Consumes the ACTUAL evaluator return
schema (preserved by hashing/normalize-and-join.py in the operator-side
scorebook) + the operator-only blind map (required input) + the frozen
test-invocations.

Inputs:
  --envelope PATH            inputs/baseline-envelope-membership.json
  --baseline-stats PATH      inputs/baseline-statistics.json
  --arm-c-A PATH             evaluation/evaluator-A-arm-C-scorebook.json
  --arm-c-B PATH             evaluation/evaluator-B-arm-C-scorebook.json
  --blind-map PATH           preflight/blind-map.json
  --test-invocations PATH    inputs/test-invocations.json
  --frozen-A-A PATH          BIB-001 evaluator A scorebook (LOCKED)
  --frozen-A-B PATH          BIB-001 evaluator B scorebook (LOCKED)
  --frozen-B-A PATH          BIB-002 evaluator A scorebook (LOCKED)
  --frozen-B-B PATH          BIB-002 evaluator B scorebook (LOCKED)
  --out PATH                 Output C20 decision record (frozen)

The script RECOMPUTES each BIB scorebook SHA (fatal on mismatch), verifies
the 85 envelope records, requires the exact frozen current expected cells,
and uses the preregistered historical envelope bound (A=1.807059, B=0.414118).

R/B/arm/candidate are recovered EXCLUSIVELY from the blind map. The scorebook's
reconstruction_id / block / arm / candidate / birthdate fields must MATCH the
blind map exactly; mismatch is FATAL. The test_invocations file is referenced
for the test_id/run labels and birthdate string per candidate, but C20 does
not depend on its hash for the C20 decision.
"""

import argparse
import hashlib
import json
import os
import statistics
import sys
from datetime import datetime, timezone


FROZEN_DIMS = ['contract_compliance', 'selection_behavior', 'narrative_behavior', 'functional_completeness']
CURRENT_EXPECTED_ARM_C_CELLS_NAMED = [('R1', 'B1'), ('R2', 'B1'), ('R3', 'B1')]


def _translate_cell(named_cell):
    if isinstance(named_cell, str):
        parts = named_cell.split('/')
        if len(parts) == 2:
            R, b = parts
            return (R, 'B' if b == 'B1' else b)
        return named_cell
    R, b = named_cell
    return (R, 'B' if b == 'B1' else b)
CURRENT_EXPECTED_ARM_C_CELLS = [_translate_cell(c) for c in CURRENT_EXPECTED_ARM_C_CELLS_NAMED]


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(65536), b''):
            h.update(chunk)
    return h.hexdigest()


def fail(msg):
    print(f'FATAL: {msg}', file=sys.stderr)
    sys.exit(2)


def manhattan(scores, ref):
    return sum(abs(scores[d] - ref[d]) for d in FROZEN_DIMS)


def load_operator_side_scorebook(path, eval_id):
    """Load the operator-side Arm-C scorebook for evaluator eval_id. Each record has
    blind_id, reconstruction_id, block, arm, candidate, birthdate, test_id, run,
    scores_<eval_id>, M_scores, G_subset_b_axis_scores, evaluator_self_report.
    R/B/arm/candidate/birthdate are operator-side (joined from blind map);
    scores are from the evaluator return.
    """
    with open(path) as f:
        sb = json.load(f)
    if not isinstance(sb, list):
        fail(f'operator-side scorebook {path} must be a JSON list of records, got {type(sb).__name__}')
    out = []
    seen_blind_ids = set()
    seen_tuples = set()
    for idx, rec in enumerate(sb):
        for f_name in ('blind_id', 'reconstruction_id', 'block', 'arm', 'candidate', 'birthdate',
                       f'scores_{eval_id}', 'M_scores', 'G_subset_b_axis_scores', 'evaluator_self_report'):
            if f_name not in rec:
                fail(f'record {idx} in {path} missing required field {f_name!r}; got keys {list(rec.keys())}')
        scores = rec[f'scores_{eval_id}']
        if not isinstance(scores, dict):
            fail(f'record {idx} {f_name} must be a dict, got {type(scores).__name__}')
        for d in FROZEN_DIMS:
            if d not in scores:
                fail(f'record {idx} {f_name} missing dim {d!r}; got keys {list(scores.keys())}')
            if not isinstance(scores[d], int) or scores[d] < 0 or scores[d] > 4:
                fail(f'record {idx} {f_name}[{d!r}] = {scores[d]!r}; must be int in 0..4')
        bid = rec['blind_id']
        if bid in seen_blind_ids:
            fail(f'duplicate blind_id {bid!r} in {path} (record {idx})')
        seen_blind_ids.add(bid)
        tup = (rec['reconstruction_id'], rec['block'], rec['arm'], rec['candidate'])
        if tup in seen_tuples:
            fail(f'duplicate tuple {tup} in {path} (record {idx})')
        seen_tuples.add(tup)
        out.append({
            'blind_id': bid,
            'reconstruction_id': rec['reconstruction_id'],
            'block': rec['block'],
            'arm': rec['arm'],
            'candidate': rec['candidate'],
            'birthdate': rec['birthdate'],
            'test_id': rec.get('test_id'),
            'run': rec.get('run'),
            'scores': scores,
            'runtime_failure': bool(rec.get('evaluator_self_report', {}).get('runtime_failure_observed', False)),
        })
    return out


def load_blind_map(path):
    with open(path) as f:
        bm = json.load(f)
    if 'blind_id_to_tuple' not in bm:
        fail(f'blind map {path} missing required key "blind_id_to_tuple"')
    return bm['blind_id_to_tuple']


def main():
    ap = argparse.ArgumentParser(description="INSA-ID-E1 C20 derivation (frozen v6)")
    ap.add_argument('--envelope', required=True, help='inputs/baseline-envelope-membership.json')
    ap.add_argument('--baseline-stats', required=True, help='inputs/baseline-statistics.json')
    ap.add_argument('--arm-c-A', required=True, help='evaluation/evaluator-A-arm-C-scorebook.json (operator-side)')
    ap.add_argument('--arm-c-B', required=True, help='evaluation/evaluator-B-arm-C-scorebook.json (operator-side)')
    ap.add_argument('--blind-map', required=True, help='preflight/blind-map.json (operator-only; locked in Phase 0)')
    ap.add_argument('--test-invocations', required=True, help='inputs/test-invocations.json (frozen test schedule)')
    ap.add_argument('--frozen-A-A', required=True, help='frozen BIB-001 evaluator A scorebook (LOCKED)')
    ap.add_argument('--frozen-A-B', required=True, help='frozen BIB-001 evaluator B scorebook (LOCKED)')
    ap.add_argument('--frozen-B-A', required=True, help='frozen BIB-002 evaluator A scorebook (LOCKED)')
    ap.add_argument('--frozen-B-B', required=True, help='frozen BIB-002 evaluator B scorebook (LOCKED)')
    ap.add_argument('--out', required=True, help='output C20 decision record JSON')
    args = ap.parse_args()

    derivation_recorded_at_utc = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')

    # Step 1: Recompute each of the four historical BIB scorebook SHA-256 values; compare against baseline-statistics.json expected values.
    print('Step 1: verifying four frozen BIB scorebook SHAs...')
    bs = json.load(open(args.baseline_stats))
    expected_scorebook_shas = bs['frozen_bib_scorebook_shas']
    actual_scorebook_shas = {
        'BIB-001_evaluator_A': sha256_file(args.frozen_A_A),
        'BIB-001_evaluator_B': sha256_file(args.frozen_A_B),
        'BIB-002_evaluator_A': sha256_file(args.frozen_B_A),
        'BIB-002_evaluator_B': sha256_file(args.frozen_B_B),
    }
    for k, expected in expected_scorebook_shas.items():
        actual = actual_scorebook_shas[k]
        if actual != expected:
            fail(f'scorebook SHA mismatch for {k}: expected {expected}, got {actual}')
    print(f'  all 4 scorebook SHAs verified')

    # Step 2: Read and verify baseline-envelope-membership.json against the 85 records in baseline-statistics.json.
    print('Step 2: verifying baseline-envelope-membership.json against baseline-statistics.json envelope records...')
    envelope_membership = json.load(open(args.envelope))
    membership_shas = sorted(obs['raw_sha256'] for obs in envelope_membership['included_observations'])
    records_shas = sorted(r['raw_sha256'] for r in bs['envelope_records_85_with_per_dim_scores'])
    if len(membership_shas) != 85 or len(records_shas) != 85:
        fail(f'count mismatch: membership has {len(membership_shas)} SHAs, baseline-statistics has {len(records_shas)} records')
    if membership_shas != records_shas:
        only_in_membership = set(membership_shas) - set(records_shas)
        only_in_records = set(records_shas) - set(membership_shas)
        fail(f'85-record SHA set mismatch. Only in membership: {len(only_in_membership)}; only in baseline-statistics: {len(only_in_records)}')
    print(f'  all 85 envelope SHAs match between membership and baseline-statistics.json')

    # Step 3: Verify the baseline-statistics artifact's required fields.
    print('Step 3: verifying baseline-statistics.json required fields...')
    required_fields = [
        'frozen_bib_scorebook_shas',
        'calibrated_4d_reference_vectors_preregistered',
        'C20_historical_envelope_bound_preregistered_v4',
        'envelope_records_85_with_per_dim_scores',
        'envelope_record_count',
        'C20_method_for_arm_C_per_current_cell_manhattan',
        'C20_boolean_pass_fail_formula',
    ]
    for f in required_fields:
        if f not in bs:
            fail(f'baseline-statistics.json missing required field: {f}')
    if bs['envelope_record_count'] != 85:
        fail(f"baseline-statistics envelope_record_count = {bs['envelope_record_count']}, expected 85")
    env_bound = bs['C20_historical_envelope_bound_preregistered_v4']
    if 'frozen_historical_envelope_bound' not in env_bound:
        fail('baseline-statistics.json missing C20_historical_envelope_bound_preregistered_v4.frozen_historical_envelope_bound')
    if 'evaluator_A' not in env_bound['frozen_historical_envelope_bound'] or 'evaluator_B' not in env_bound['frozen_historical_envelope_bound']:
        fail('baseline-statistics.json C20 envelope bound missing evaluator_A or evaluator_B')
    if 'current_expected_arm_c_cells' not in env_bound:
        fail('baseline-statistics.json C20 envelope bound missing current_expected_arm_c_cells')
    expected_current_cells = [c for c in env_bound['current_expected_arm_c_cells']]
    expected_translated = [_translate_cell(c) for c in expected_current_cells]
    if sorted(expected_translated) != sorted(CURRENT_EXPECTED_ARM_C_CELLS):
        fail(f'current_expected_arm_c_cells mismatch: expected {sorted(CURRENT_EXPECTED_ARM_C_CELLS)} (translated from {sorted(CURRENT_EXPECTED_ARM_C_CELLS_NAMED)}), got {sorted(expected_translated)} (translated from {expected_current_cells})')
    print(f'  all required fields present, current_expected_arm_c_cells = {CURRENT_EXPECTED_ARM_C_CELLS}')

    ref_vectors = bs['calibrated_4d_reference_vectors_preregistered']
    envelope_bound = env_bound['frozen_historical_envelope_bound']
    print(f'  per-evaluator reference vectors loaded (A: {ref_vectors["evaluator_A"]}; B: {ref_vectors["evaluator_B"]})')
    print(f'  per-evaluator historical envelope bound loaded (A: {envelope_bound["evaluator_A"]}; B: {envelope_bound["evaluator_B"]})')

    # Step 4: Load the operator-only blind map, test-invocations, and the two operator-side Arm-C scorebooks.
    print('Step 4: loading operator-only blind map + test-invocations + Arm-C scorebooks...')
    blind_map = load_blind_map(args.blind_map)
    print(f'  loaded blind map with {len(blind_map)} entries')
    test_invocations = json.load(open(args.test_invocations))
    print(f'  loaded test-invocations (schema_version={test_invocations.get("schema_version")})')

    arm_c_A = load_operator_side_scorebook(args.arm_c_A, 'A')
    arm_c_B = load_operator_side_scorebook(args.arm_c_B, 'B')
    print(f'  loaded {len(arm_c_A)} evaluator A records, {len(arm_c_B)} evaluator B records')

    # Step 5: Validate the operator-side scorebook's R/B/arm/candidate/birthdate against the blind map. C20 derives R/B EXCLUSIVELY from the blind map.
    print('Step 5: validating operator-side scorebook R/B/arm/candidate/birthdate against the blind map...')
    def validate_against_blind_map(scorebook, blind_map, test_invocations, eval_label):
        for rec in scorebook:
            bid = rec['blind_id']
            if bid not in blind_map:
                fail(f'{eval_label} scorebook contains blind_id {bid!r} not in blind map')
            mapped = blind_map[bid]
            for k in ('reconstruction_id', 'block', 'arm', 'candidate', 'birthdate'):
                if rec.get(k) != mapped.get(k):
                    fail(f'{eval_label} scorebook blind_id {bid!r} field {k!r}={rec.get(k)!r} does not match blind map {mapped.get(k)!r} (C20 requires exact match; recovery is from the blind map only)')
    validate_against_blind_map(arm_c_A, blind_map, test_invocations, 'evaluator_A')
    validate_against_blind_map(arm_c_B, blind_map, test_invocations, 'evaluator_B')
    print(f'  operator-side scorebook R/B/arm/candidate/birthdate match the blind map for all records (R/B recovered exclusively from the blind map)')

    # Step 6: Compute per-(R, B) cell means (using the BIB 4-dim from the evaluator-joined scorebook).
    print('Step 6: computing per-current-cell mean Manhattan...')
    def per_cell_means(scorebook, eval_id):
        per_cell = {}
        for rec in scorebook:
            if rec['runtime_failure']:
                continue
            cell = (rec['reconstruction_id'], rec['block'])
            per_cell.setdefault(cell, []).append(manhattan(rec['scores'], ref_vectors[eval_id]))
        return {f'{c[0]}/{c[1]}': round(statistics.mean(ds), 6) for c, ds in per_cell.items()}

    per_cell_A = per_cell_means(arm_c_A, 'evaluator_A')
    per_cell_B = per_cell_means(arm_c_B, 'evaluator_B')
    print(f'  per-cell means A: {per_cell_A}')
    print(f'  per-cell means B: {per_cell_B}')

    # Step 7: Apply C20 decision.
    print('Step 7: applying C20 decision...')
    def c20_decision(per_cell, eval_id):
        missing = [cell for cell in CURRENT_EXPECTED_ARM_C_CELLS if f'{cell[0]}/{cell[1]}' not in per_cell]
        if missing:
            return False, f'missing current cells: {missing}', per_cell
        worst = max(per_cell.items(), key=lambda kv: kv[1])
        bound = envelope_bound[eval_id]
        if worst[1] > bound:
            return False, f'worst current cell {worst[0]} mean={worst[1]:.4f} > frozen historical envelope bound {bound}', per_cell
        return True, None, per_cell

    c20_pass_A, c20_fail_A, _ = c20_decision(per_cell_A, 'evaluator_A')
    c20_pass_B, c20_fail_B, _ = c20_decision(per_cell_B, 'evaluator_B')
    c20_joint_pass = c20_pass_A and c20_pass_B
    print(f'  C20 per-evaluator pass: A={c20_pass_A}, B={c20_pass_B}, joint={c20_joint_pass}')

    # Step 8: Build output record.
    out = {
        'schema_version': '1.0',
        'record_kind': 'c20-decision-record',
        'experiment_id': 'INSA-ID-E1',
        'derivation_recorded_at_utc': derivation_recorded_at_utc,
        'c20_method': 'deterministic from inputs/baseline-envelope-membership.json + inputs/baseline-statistics.json + Phase 2 Arm-C scorebooks (operator-side, joined from preflight/blind-map.json via hashing/normalize-and-join.py)',
        'c20_rule': 'C20(e) = (missing_current_cells[e] is empty) AND (max over current (R, B) cells in {R1/B1, R2/B1, R3/B1} of mean_4dim_Manhattan_Arm_C(R, B) <= frozen_historical_envelope_bound[e]) for each evaluator e in {A, B}; C20_joint = C20(A) AND C20(B). R/B/arm/candidate are recovered EXCLUSIVELY from the blind map.',
        'frozen_scorebook_shas': actual_scorebook_shas,
        'envelope_record_count': len(membership_shas),
        'envelope_record_set_match_baseline_statistics': (set(membership_shas) == set(records_shas)),
        'calibrated_reference_vectors': ref_vectors,
        'frozen_historical_envelope_bound': envelope_bound,
        'current_expected_arm_c_cells': [f'{c[0]}/{c[1]}' for c in CURRENT_EXPECTED_ARM_C_CELLS_NAMED],
        'per_current_cell_mean_manhattan': {
            'evaluator_A': per_cell_A,
            'evaluator_B': per_cell_B,
        },
        'c20_per_evaluator_pass': {'evaluator_A': c20_pass_A, 'evaluator_B': c20_pass_B},
        'c20_fail_reasons': {'evaluator_A': c20_fail_A, 'evaluator_B': c20_fail_B},
        'c20_joint_pass': c20_joint_pass,
        'c20_disposition_if_fail': 'INVALID_EXPERIMENT',
        'verification_command': 'python3 hashing/binding-verification.py --v6-experiment-dir .',
        'sidecar_sha_record': 'preflight/c20-decision-record.sha256.txt (written by the operator after this script exits; not by this script itself)',
        'self_referential_hash_prohibition': 'This file does NOT contain its own full-file SHA-256 inside its bytes.',
    }

    tmp = args.out + '.tmp'
    with open(tmp, 'w') as f:
        json.dump(out, f, indent=2, sort_keys=False)
        f.write('\n')
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp, args.out)
    out_sha = sha256_file(args.out)
    print()
    print(f'WROTE: {args.out}')
    print(f'  c20_joint_pass: {c20_joint_pass}')
    print(f'  output SHA-256: {out_sha}')
    print(f'  derivation_recorded_at_utc: {derivation_recorded_at_utc}')


if __name__ == '__main__':
    main()
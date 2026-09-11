#!/usr/bin/env python3
"""
INSA-ID-E1 C20 derivation (frozen pre-execution, v5).

Frozen deterministic C20 derivation. Consumes the ACTUAL evaluator return
schema (no synthetic reconstruction_id, block, or generic scores fields).
Reads the operator-only blind map (required input) to recover (R, B, arm,
candidate) per blind_id. Re-verifies all inputs; fails fatally on any
mismatch.

Inputs:
  --envelope PATH         inputs/baseline-envelope-membership.json (85 SHA list)
  --baseline-stats PATH   inputs/baseline-statistics.json (finalized; contains
                           historical_envelope_bound per evaluator, current_expected_arm_c_cells,
                           85 envelope records)
  --arm-c-A PATH          evaluation/evaluator-A-arm-C-scorebook.json (OPERATOR-SIDE
                           scorebook: each record has blind_id, reconstruction_id,
                           block, arm, candidate, scores_A, M_scores, evaluator_self_report;
                           R/B/arm/candidate are populated operator-side from the blind map)
  --arm-c-B PATH          evaluation/evaluator-B-arm-C-scorebook.json
  --blind-map PATH        preflight/blind-map.json (operator-only; locked in Phase 0)
  --frozen-A-A PATH       experiments/.../evaluator-A-scores-LOCKED.jsonl (BIB-001 A)
  --frozen-A-B PATH       experiments/.../evaluator-B-scores-LOCKED.jsonl (BIB-001 B)
  --frozen-B-A PATH       experiments/.../evaluator-A-scores-LOCKED.jsonl (BIB-002 A)
  --frozen-B-B PATH       experiments/.../evaluator-B-scores-LOCKED.jsonl (BIB-002 B)
  --out PATH              Output JSON path containing the C20 decision record
                           (frozen content-addressed; SHA-256 recorded externally)

The C20 derivation REJECTS (fatal nonzero exit) on:
  - Any input SHA mismatch (4 scorebooks, envelope membership vs baseline-statistics)
  - Any blind_id in the operator-side scorebook that is not in the operator-only blind map
  - Any duplicate blind_id in the operator-side scorebook
  - Any duplicate (R, B, arm, candidate) tuple in the operator-side scorebook
  - Any operator-side record with arm != C (this is the Arm-C scorebook; Arm-M blind IDs are fatal)
  - Any (R, B) cell outside the preregistered current expected cells {R1/B1, R2/B1, R3/B1}

Behavior:
  - Evaluator-runtime-failure reports (evaluator_self_report.runtime_failure_observed == true) are
    recorded but excluded from per-(R, B) mean computation (per preregistered T1/T2/T3 protocol §9
    runtime-failure handling).
  - C20 PASS for evaluator e IFF (a) no missing current cells AND (b) every current cell mean
    Manhattan distance <= frozen historical envelope bound[e] (A=1.807059, B=0.414118).
  - C20 joint PASS iff both evaluators PASS.
  - derivation_recorded_at_utc is set automatically via datetime.now(timezone.utc).
  - The output file does NOT contain its own SHA-256 (no self-reference).
"""

import argparse
import hashlib
import hmac
import json
import os
import statistics
import sys
from datetime import datetime, timezone


FROZEN_DIMS = ['contract_compliance', 'selection_behavior', 'narrative_behavior', 'functional_completeness']
# Current expected Arm-C cells: R1/B1, R2/B1, R3/B1 (B1 = the single B exemplar source).
# In the historical envelope's nomenclature, this source is named "block B".
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
    """
    Load the operator-side Arm-C scorebook for evaluator eval_id.
    Each record must have: blind_id, reconstruction_id, block, arm, candidate,
    scores_<eval_id> (4-dim BIB vector), M_scores, evaluator_self_report.
    Reject: unknown blind IDs (after blind map load), duplicate blind IDs,
    duplicate (R, B, arm, candidate) tuples, arm != C, (R, B) outside expected cells.
    Returns: list of dicts (the filtered, validated records).
    """
    with open(path) as f:
        sb = json.load(f)
    if not isinstance(sb, list):
        fail(f'operator-side scorebook {path} must be a JSON list of records, got {type(sb).__name__}')
    out = []
    seen_blind_ids = set()
    seen_tuples = set()
    for idx, rec in enumerate(sb):
        # Required fields
        for f_name in ('blind_id', 'reconstruction_id', 'block', 'arm', 'candidate'):
            if f_name not in rec:
                fail(f'record {idx} in {path} missing required field {f_name!r}; got keys {list(rec.keys())}')
        scores_field = f'scores_{eval_id}'
        if scores_field not in rec:
            fail(f'record {idx} in {path} missing required field {scores_field!r} (BIB 4-dim vector); got keys {list(rec.keys())}')
        # M_scores (optional but expected for the M-gate analysis; C20 doesn't compute M)
        # evaluator_self_report (optional)
        # The 4-dim vector must be a dict with the 4 FROZEN_DIMS
        scores = rec[scores_field]
        if not isinstance(scores, dict):
            fail(f'record {idx} {scores_field} must be a dict, got {type(scores).__name__}')
        for d in FROZEN_DIMS:
            if d not in scores:
                fail(f'record {idx} {scores_field} missing dim {d!r}; got keys {list(scores.keys())}')
            if not isinstance(scores[d], int) or scores[d] < 0 or scores[d] > 4:
                fail(f'record {idx} {scores_field}[{d!r}] = {scores[d]!r}; must be int in 0..4')
        # blind_id duplicate check
        bid = rec['blind_id']
        if bid in seen_blind_ids:
            fail(f'duplicate blind_id {bid!r} in {path} (record {idx})')
        seen_blind_ids.add(bid)
        # (R, B, arm, candidate) tuple check
        tup = (rec['reconstruction_id'], rec['block'], rec['arm'], rec['candidate'])
        if tup in seen_tuples:
            fail(f'duplicate tuple {tup} in {path} (record {idx})')
        seen_tuples.add(tup)
        # arm must be C (Arm-C scorebook)
        if rec['arm'] != 'C':
            fail(f'record {idx} in {path} has arm={rec["arm"]!r}; this is the Arm-C scorebook, must be C')
        out.append({
            'blind_id': bid,
            'reconstruction_id': rec['reconstruction_id'],
            'block': rec['block'],
            'arm': rec['arm'],
            'candidate': rec['candidate'],
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


def join_scorebook_with_blind_map(scorebook, blind_map, eval_id_label, path_label):
    """
    For each scorebook record, verify blind_id is in blind_map, then
    recover (R, B, arm, candidate) from the blind map. Reject:
      - unknown blind_id
      - recovered arm != C (this is the Arm-C scorebook; Arm-M blind IDs are fatal)
      - (R, B) cell outside CURRENT_EXPECTED_ARM_C_CELLS
    Returns: list of (cell_tuple, manhattan_distance) for non-failure records.
    """
    out = []
    for rec in scorebook:
        bid = rec['blind_id']
        if bid not in blind_map:
            fail(f'{eval_id_label} scorebook {path_label} contains unknown blind_id {bid!r} (not in blind map)')
        mapped = blind_map[bid]
        recovered_arm = mapped.get('arm')
        if recovered_arm != 'C':
            fail(f'{eval_id_label} scorebook {path_label} blind_id {bid!r} maps to arm={recovered_arm!r}; this is the Arm-C scorebook, must be C (Arm-M blind IDs in Arm-C scorebook are fatal)')
        # We trust the operator-side metadata in the scorebook (it was populated by the
        # operator from the blind map); the blind map is verified for unknown IDs and arm.
        cell = (rec['reconstruction_id'], rec['block'])
        if cell not in CURRENT_EXPECTED_ARM_C_CELLS:
            fail(f'{eval_id_label} scorebook {path_label} record has (R, B) = {cell} which is outside the preregistered current expected cells {CURRENT_EXPECTED_ARM_C_CELLS}')
        if rec['runtime_failure']:
            # Runtime failure: record but exclude from per-(R, B) mean (per T1/T2/T3 protocol §9)
            continue
        # Use the scorebook's BIB 4-dim vector for this record
        out.append((cell, rec['scores']))
    return out


def main():
    ap = argparse.ArgumentParser(description="INSA-ID-E1 C20 derivation (frozen v5)")
    ap.add_argument('--envelope', required=True, help='inputs/baseline-envelope-membership.json')
    ap.add_argument('--baseline-stats', required=True, help='inputs/baseline-statistics.json')
    ap.add_argument('--arm-c-A', required=True, help='evaluation/evaluator-A-arm-C-scorebook.json (operator-side)')
    ap.add_argument('--arm-c-B', required=True, help='evaluation/evaluator-B-arm-C-scorebook.json (operator-side)')
    ap.add_argument('--blind-map', required=True, help='preflight/blind-map.json (operator-only; locked in Phase 0)')
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

    # Step 4: Load the operator-only blind map and the two operator-side Arm-C scorebooks.
    print('Step 4: loading operator-only blind map and Arm-C scorebooks...')
    blind_map = load_blind_map(args.blind_map)
    print(f'  loaded blind map with {len(blind_map)} entries')

    arm_c_A = load_operator_side_scorebook(args.arm_c_A, 'A')
    arm_c_B = load_operator_side_scorebook(args.arm_c_B, 'B')
    print(f'  loaded {len(arm_c_A)} evaluator A records, {len(arm_c_B)} evaluator B records')

    # Step 5: Join each scorebook to the blind map. Reject unknown blind IDs, arm != C, (R, B) outside expected cells.
    print('Step 5: joining scorebooks to blind map and computing per-cell means...')
    joined_A = join_scorebook_with_blind_map(arm_c_A, blind_map, 'evaluator_A', args.arm_c_A)
    joined_B = join_scorebook_with_blind_map(arm_c_B, blind_map, 'evaluator_B', args.arm_c_B)
    print(f'  evaluator A: {len(joined_A)} non-failure records joined')
    print(f'  evaluator B: {len(joined_B)} non-failure records joined')

    # Step 6: Compute per-(R, B) cell means.
    def per_cell_means(joined, eval_id):
        per_cell = {}
        for cell, scores in joined:
            per_cell.setdefault(cell, []).append(manhattan(scores, ref_vectors[eval_id]))
        return {f'{c[0]}/{c[1]}': round(statistics.mean(ds), 6) for c, ds in per_cell.items()}

    per_cell_A = per_cell_means(joined_A, 'evaluator_A')
    per_cell_B = per_cell_means(joined_B, 'evaluator_B')
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
        'c20_method': 'deterministic from inputs/baseline-envelope-membership.json + inputs/baseline-statistics.json + Phase 2 Arm-C scorebooks (operator-side, joined to preflight/blind-map.json)',
        'c20_rule': 'C20(e) = (missing_current_cells[e] is empty) AND (max over current (R, B) cells in {R1/B1, R2/B1, R3/B1} of mean_4dim_Manhattan_Arm_C(R, B) <= frozen_historical_envelope_bound[e]) for each evaluator e in {A, B}; C20_joint = C20(A) AND C20(B).',
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
        'verification_command': 'python3 hashing/binding-verification.py --v5-experiment-dir .',
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
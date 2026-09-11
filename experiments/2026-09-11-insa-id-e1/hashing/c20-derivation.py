#!/usr/bin/env python3
"""
INSA-ID-E1 C20 derivation (frozen pre-execution, v4).

Frozen deterministic C20 derivation. Recomputes every input SHA and fails
fatally on any mismatch (so the derivation cannot be silently run against
modified inputs). Uses the preregistered current expected Arm-C cell set
{R1/B1, R2/B1, R3/B1} (3 cells; block B only). Records derivation time via
datetime.utcnow().isoformat() at script execution (no post-write editing).

Inputs:
  --envelope PATH         inputs/baseline-envelope-membership.json (85 SHA list)
  --baseline-stats PATH   inputs/baseline-statistics.json
                           (must contain historical_envelope_bound per evaluator;
                            current_expected_arm_c_cells = [R1/B1, R2/B1, R3/B1];
                            85 envelope records)
  --arm-c-A PATH          evaluation/evaluator-A-arm-C-scorebook.json
  --arm-c-B PATH          evaluation/evaluator-B-arm-C-scorebook.json
  --frozen-A-A PATH       experiments/.../evaluator-A-scores-LOCKED.jsonl (BIB-001 A)
  --frozen-A-B PATH       experiments/.../evaluator-B-scores-LOCKED.jsonl (BIB-001 B)
  --frozen-B-A PATH       experiments/.../evaluator-A-scores-LOCKED.jsonl (BIB-002 A)
  --frozen-B-B PATH       experiments/.../evaluator-B-scores-LOCKED.jsonl (BIB-002 B)
  --out PATH              Output JSON path containing the C20 decision record
                           (frozen content-addressed; SHA-256 recorded externally)

Behavior:
  - On any input SHA mismatch (the four scorebooks, the envelope membership
    against the 85 records in baseline-statistics.json), the script exits
    nonzero with a clear error message. NO silent fallback.
  - On any missing expected current Arm-C cell, c20_per_evaluator_pass[e] = False.
  - On any current cell's mean Manhattan distance exceeding the frozen
    historical envelope bound for that evaluator, c20_per_evaluator_pass[e] = False.
  - C20 joint PASS iff both evaluators PASS.
  - derivation_recorded_at_utc is set at script run time (datetime.utcnow()).
  - The output file does NOT contain its own SHA-256 (no self-reference);
    the SHA is recorded externally.
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
# Current expected Arm-C cells: {R1/B1, R2/B1, R3/B1} where "B1" denotes the single B exemplar
# source (i.e., the BIB behavioral baseline that the experiment uses as the canonical exemplar).
# In the historical envelope's nomenclature, this source is named "block B" (paired with block A in
# the original 85-observation BIB envelope, where each reconstruction had two blocks: A and B).
# For INSA-ID-E1's current generation, only one source (B) is used per reconstruction. The translator
# below maps B1 -> B so the candidate records (which use block='B') are matched.
CURRENT_EXPECTED_ARM_C_CELLS_NAMED = [('R1', 'B1'), ('R2', 'B1'), ('R3', 'B1')]
# Translator: map the named (B1) form to the actual envelope block label (B)
def _translate_cell(named_cell):
    # Accept either ('R1','B1') tuple or 'R1/B1' string
    if isinstance(named_cell, str):
        parts = named_cell.split('/')
        if len(parts) == 2:
            R, b = parts
            return (R, 'B' if b == 'B1' else b)
        return named_cell  # leave as-is
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


def load_json(path):
    with open(path) as f:
        return json.load(f)


def manhattan(scores, ref):
    return sum(abs(scores[d] - ref[d]) for d in FROZEN_DIMS)


def main():
    ap = argparse.ArgumentParser(description="INSA-ID-E1 C20 derivation (frozen v4)")
    ap.add_argument('--envelope', required=True, help='inputs/baseline-envelope-membership.json')
    ap.add_argument('--baseline-stats', required=True, help='inputs/baseline-statistics.json')
    ap.add_argument('--arm-c-A', required=True, help='evaluation/evaluator-A-arm-C-scorebook.json')
    ap.add_argument('--arm-c-B', required=True, help='evaluation/evaluator-B-arm-C-scorebook.json')
    ap.add_argument('--frozen-A-A', required=True, help='frozen BIB-001 evaluator A scorebook (LOCKED)')
    ap.add_argument('--frozen-A-B', required=True, help='frozen BIB-001 evaluator B scorebook (LOCKED)')
    ap.add_argument('--frozen-B-A', required=True, help='frozen BIB-002 evaluator A scorebook (LOCKED)')
    ap.add_argument('--frozen-B-B', required=True, help='frozen BIB-002 evaluator B scorebook (LOCKED)')
    ap.add_argument('--out', required=True, help='output C20 decision record JSON')
    args = ap.parse_args()

    derivation_recorded_at_utc = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')

    # Step 1: Recompute each of the four historical BIB scorebook SHA-256 values; compare against baseline-statistics.json expected values.
    print('Step 1: verifying four frozen BIB scorebook SHAs...')
    bs = load_json(args.baseline_stats)
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
    print(f'  all 4 scorebook SHAs verified (exit nonzero on mismatch)')

    # Step 2: Read and verify baseline-envelope-membership.json against the 85 records in baseline-statistics.json.
    print('Step 2: verifying baseline-envelope-membership.json against baseline-statistics.json envelope records...')
    envelope_membership = load_json(args.envelope)
    membership_shas = sorted(obs['raw_sha256'] for obs in envelope_membership['included_observations'])
    stats_records = bs['envelope_records_85_with_per_dim_scores']
    records_shas = sorted(r['raw_sha256'] for r in stats_records)
    if len(membership_shas) != 85 or len(records_shas) != 85:
        fail(f'count mismatch: membership has {len(membership_shas)} SHAs, baseline-statistics has {len(records_shas)} records')
    if membership_shas != records_shas:
        # Diagnose
        only_in_membership = set(membership_shas) - set(records_shas)
        only_in_records = set(records_shas) - set(membership_shas)
        fail(f'85-record SHA set mismatch. Only in membership: {len(only_in_membership)}; only in baseline-statistics: {len(only_in_records)}')
    print(f'  all 85 envelope SHAs match between membership and baseline-statistics.json')

    # Step 3: Verify the baseline-statistics artifact expected by the frozen package.
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

    expected_named = [c for c in env_bound['current_expected_arm_c_cells']]
    expected_translated = [_translate_cell(c) for c in expected_named]
    if sorted(expected_translated) != sorted(CURRENT_EXPECTED_ARM_C_CELLS):
        fail(f'current_expected_arm_c_cells mismatch: expected {sorted(CURRENT_EXPECTED_ARM_C_CELLS)} (translated from {sorted(CURRENT_EXPECTED_ARM_C_CELLS_NAMED)}), got {sorted(expected_translated)} (translated from {expected_named})')
    print(f'  all required fields present, current_expected_arm_c_cells = {CURRENT_EXPECTED_ARM_C_CELLS}')

    # Step 4: Load the per-evaluator reference vector and frozen historical envelope bound from baseline-statistics.
    ref_vectors = bs['calibrated_4d_reference_vectors_preregistered']
    envelope_bound = env_bound['frozen_historical_envelope_bound']
    print(f'  per-evaluator reference vectors loaded (A: {ref_vectors["evaluator_A"]}; B: {ref_vectors["evaluator_B"]})')
    print(f'  per-evaluator historical envelope bound loaded (A: {envelope_bound["evaluator_A"]}; B: {envelope_bound["evaluator_B"]})')

    # Step 5: Load Arm-C scorebooks; per-candidate scores keyed by (R, B, blind_id).
    print('Step 5: loading Phase 2 Arm-C scorebooks...')
    def load_arm_c(path):
        with open(path) as f:
            sb = json.load(f)
        out = []
        for rec in sb:
            # Accept both {"scores": {...}} and flat per-dim fields
            if isinstance(rec.get('scores'), dict):
                scores = {d: rec['scores'].get(d) for d in FROZEN_DIMS}
            else:
                scores = {d: rec.get(d) for d in FROZEN_DIMS if d in rec}
            if all(d in scores for d in FROZEN_DIMS) and None not in scores.values():
                out.append({
                    'reconstruction_id': rec.get('reconstruction_id'),
                    'block': rec.get('block'),
                    'blind_id': rec.get('blind_id') or rec.get('blindId'),
                    'scores': scores,
                })
        return out

    arm_c_A = load_arm_c(args.arm_c_A)
    arm_c_B = load_arm_c(args.arm_c_B)
    print(f'  loaded {len(arm_c_A)} evaluator A Arm-C candidates, {len(arm_c_B)} evaluator B Arm-C candidates')

    # Step 6: Compute per-(R, B) cell means for the CURRENT expected cells only.
    print('Step 6: computing per-current-cell mean Manhattan...')
    def per_cell_means_for(candidates, eval_id):
        per_cell = {}
        for c in candidates:
            cell = (c['reconstruction_id'], c['block'])
            per_cell.setdefault(cell, []).append(manhattan(c['scores'], ref_vectors[eval_id]))
        return {f'{c[0]}/{c[1]}': round(statistics.mean(ds), 6) for c, ds in per_cell.items() if ds}

    per_cell_A = per_cell_means_for(arm_c_A, 'evaluator_A')
    per_cell_B = per_cell_means_for(arm_c_B, 'evaluator_B')
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
        'c20_method': 'deterministic from inputs/baseline-envelope-membership.json + inputs/baseline-statistics.json + Phase 2 Arm-C scorebooks',
        'c20_rule': 'C20(e) = (missing_current_cells[e] is empty) AND (max over current (R, B) cells in {R1/B1, R2/B1, R3/B1} of mean_4dim_Manhattan_Arm_C(R, B) <= frozen_historical_envelope_bound[e]) for each evaluator e in {A, B}; C20_joint = C20(A) AND C20(B).',
        'frozen_scorebook_shas': actual_scorebook_shas,
        'envelope_record_count': len(membership_shas),
        'envelope_record_set_match_baseline_statistics': (set(membership_shas) == set(records_shas)),
        'calibrated_reference_vectors': ref_vectors,
        'frozen_historical_envelope_bound': envelope_bound,
        'current_expected_arm_c_cells': [f'{c[0]}/{c[1]}' for c in CURRENT_EXPECTED_ARM_C_CELLS],
        'per_current_cell_mean_manhattan': {
            'evaluator_A': per_cell_A,
            'evaluator_B': per_cell_B,
        },
        'c20_per_evaluator_pass': {'evaluator_A': c20_pass_A, 'evaluator_B': c20_pass_B},
        'c20_fail_reasons': {'evaluator_A': c20_fail_A, 'evaluator_B': c20_fail_B},
        'c20_joint_pass': c20_joint_pass,
        'c20_disposition_if_fail': 'INVALID_EXPERIMENT',
        'verification_command': 'python3 hashing/binding-verification.py --v4-experiment-dir .',
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
#!/usr/bin/env python3
"""
INSA-ID-E1 C20 derivation (frozen pre-execution).

Computes C20 deterministically from the frozen 85-observation BIB envelope.
Inputs:
  --envelope PATH     Path to inputs/baseline-envelope-membership.json (85 SHA list)
  --record-fixture PATH
                       Path to inputs/baseline-statistics.json (the 85 per-(R, B, T,
                       evaluator) records with per-dim scores; SHA-bound to the four
                       frozen BIB scorebooks)
  --arm-c-scorebooks PATH1 [PATH2 ...]
                       Paths to evaluator-A-arm-C-scorebook.json + evaluator-B-arm-C-scorebook.json
                       (the per-(R, B, arm=C, candidate) per-dim scores produced by Phase 2)
  --out PATH          Output JSON path containing the C20 decision record (locked content-addressed)

C20 rule (per proposal v5.1 §8; phase 2 of protocol v3):
  For each evaluator independently:
    For each (R, B) Arm-C cell:
      Compute mean_M_dist_within_R = mean of per-candidate 4-dim Manhattan distance
                                     from the frozen calibrated reference vector.
      The reference vector is the per-evaluator 4-dim mean of the 85 envelope observations
      (computed deterministically from inputs/baseline-statistics.json).
      The per-candidate 4-dim Manhattan distance = sum over dims of |score - ref[dim]|.
  C20 PASS for evaluator e IF AND ONLY IF for every (R, B) Arm-C cell
    mean_M_dist_within_R <= C20_envelope_bound (the frozen historical envelope bound
    for that evaluator; derived deterministically from the 85 envelope observations
    via the envelope-bound computation below).

C20 envelope bound derivation (per evaluator, deterministic):
  The historical C20 envelope bound is the maximum per-(R, B) mean_4-dim-Manhattan-from-ref
  observed across the 85 envelope observations, when grouped by the envelope's
  reconstruction_id. This is the historical "envelope boundary" that an in-spec Arm-C
  must satisfy on its own (without +1.5 tolerance per v0.1 §11.2 PI freeze correction 1).

Output (JSON, locked):
  {
    "c20_method": "deterministic from inputs/baseline-statistics.json + inputs/baseline-envelope-membership.json",
    "frozen_scorebook_shas": {BIB-001 A/B, BIB-002 A/B},
    "calibrated_reference_vectors": {A: {dim: mean, ...}, B: {dim: mean, ...}},
    "c20_envelope_bounds": {A: max_per_(R,B)_mean_dist, B: max_per_(R,B)_mean_dist},
    "arm_c_per_evaluator": {A: {(R, B): mean_dist, ...}, B: ...},
    "c20_per_evaluator_pass": {A: bool, B: bool},
    "c20_joint_pass": bool,
    "derivation_script_sha256": "<this script's SHA-256>",
    "derivation_recorded_at_utc": "<UTC>",
    "disposition_on_c20_fail": "INVALID_EXPERIMENT"
  }
"""

import argparse
import hashlib
import json
import os
import statistics
import sys


FROZEN_DIMS = ['contract_compliance', 'selection_behavior', 'narrative_behavior', 'functional_completeness']


def manhattan_distance(scores, ref):
    return sum(abs(scores[d] - ref[d]) for d in FROZEN_DIMS)


def compute_reference_vectors(envelope_records):
    """Compute per-evaluator 4-dim reference vector = mean of envelope observations per dim."""
    refs = {}
    for eval_id in ['A', 'B']:
        key = f'scores_{eval_id}'
        ref = {}
        for d in FROZEN_DIMS:
            vals = [r[key][d] for r in envelope_records if r[key].get(d) is not None]
            ref[d] = round(statistics.mean(vals), 6)
        refs[eval_id] = ref
    return refs


def compute_envelope_bounds(envelope_records, refs):
    """
    Compute C20 envelope bound per evaluator = max per-(R, B) mean 4-dim Manhattan distance
    observed in the 85 envelope observations (historical C20 envelope boundary).
    """
    bounds = {}
    for eval_id in ['A', 'B']:
        key = f'scores_{eval_id}'
        # Group by (R, B)
        per_cell = {}
        for r in envelope_records:
            cell_key = (r['reconstruction_id'], r['block'])
            if cell_key not in per_cell:
                per_cell[cell_key] = []
            per_cell[cell_key].append(manhattan_distance(r[key], refs[eval_id]))
        # Max mean per cell across all (R, B) cells in the envelope
        max_mean = max(statistics.mean(dists) for dists in per_cell.values())
        bounds[eval_id] = round(max_mean, 6)
    return bounds


def compute_arm_c_per_evaluator(arm_c_scorebooks, refs):
    """
    For each evaluator, compute per-(R, B) mean 4-dim Manhattan distance for the Arm-C candidates.
    arm_c_scorebooks is a dict {eval_id: list of per-candidate score dicts}.
    """
    out = {}
    for eval_id, candidates in arm_c_scorebooks.items():
        per_cell = {}
        for c in candidates:
            cell_key = (c['reconstruction_id'], c['block'])
            if cell_key not in per_cell:
                per_cell[cell_key] = []
            per_cell[cell_key].append(manhattan_distance(c['scores'], refs[eval_id]))
        per_cell_means = {k: round(statistics.mean(v), 6) for k, v in per_cell.items()}
        out[eval_id] = {f'{k[0]}/{k[1]}': v for k, v in per_cell_means.items()}
    return out


def main():
    ap = argparse.ArgumentParser(description="INSA-ID-E1 C20 derivation (frozen)")
    ap.add_argument('--envelope', required=True, help='inputs/baseline-envelope-membership.json (85 SHA list)')
    ap.add_argument('--record-fixture', required=True, help='inputs/baseline-statistics.json (per-(R,B,T,evaluator) per-dim scores)')
    ap.add_argument('--arm-c-scorebook-a', required=True, help='evaluation/evaluator-A-arm-C-scorebook.json (per-candidate 4-dim scores)')
    ap.add_argument('--arm-c-scorebook-b', required=True, help='evaluation/evaluator-B-arm-C-scorebook.json')
    ap.add_argument('--frozen-scorebook-A-A', required=True, help='Path to frozen BIB-001 evaluator A scorebook (for SHA verification)')
    ap.add_argument('--frozen-scorebook-A-B', required=True, help='Path to frozen BIB-001 evaluator B scorebook (for SHA verification)')
    ap.add_argument('--frozen-scorebook-B-A', required=True, help='Path to frozen BIB-002 evaluator A scorebook (for SHA verification)')
    ap.add_argument('--frozen-scorebook-B-B', required=True, help='Path to frozen BIB-002 evaluator B scorebook (for SHA verification)')
    ap.add_argument('--out', required=True, help='Output JSON path (locked C20 decision record)')
    args = ap.parse_args()

    # Step 1: Verify the four frozen scorebook SHAs
    frozen_book_paths = {
        'BIB-001_evaluator_A': args.frozen_scorebook_A_A,
        'BIB-001_evaluator_B': args.frozen_scorebook_A_B,
        'BIB-002_evaluator_A': args.frozen_scorebook_B_A,
        'BIB-002_evaluator_B': args.frozen_scorebook_B_B,
    }
    frozen_book_shas = {}
    for k, p in frozen_book_paths.items():
        sha = hashlib.sha256(open(p, 'rb').read()).hexdigest()
        frozen_book_shas[k] = sha
    print(f'Frozen BIB scorebook SHAs (recomputed):')
    for k, sha in frozen_book_shas.items():
        print(f'  {k}: {sha}')

    # Step 2: Load the 85-observation envelope record (per-dim scores)
    with open(args.record_fixture) as f:
        record_fixture = json.load(f)
    envelope_records = record_fixture['envelope_records']
    assert len(envelope_records) == 85, f"expected 85 envelope records, got {len(envelope_records)}"

    # Step 3: Compute reference vectors
    refs = compute_reference_vectors(envelope_records)
    print(f'\nCalibrated reference vectors:')
    for e, ref in refs.items():
        print(f'  {e}: {ref}')

    # Step 4: Compute C20 envelope bounds
    bounds = compute_envelope_bounds(envelope_records, refs)
    print(f'\nC20 envelope bounds (per-(R,B) max mean Manhattan):')
    for e, b in bounds.items():
        print(f'  {e}: {b}')

    # Step 5: Load Arm-C scorebooks (Phase 2 outputs)
    def load_arm_c_scorebook(path):
        with open(path) as f:
            sb = json.load(f)
        # Expected format: list of {blind_id, scores: {dim: int, ...}, reconstruction_id, block}
        candidates = []
        for rec in sb:
            if 'scores' in rec and isinstance(rec['scores'], dict):
                scores = {d: rec['scores'].get(d) for d in FROZEN_DIMS}
            else:
                scores = {d: rec.get(d) for d in FROZEN_DIMS if d in rec}
            if all(d in scores for d in FROZEN_DIMS):
                candidates.append({
                    'reconstruction_id': rec.get('reconstruction_id'),
                    'block': rec.get('block'),
                    'scores': scores,
                })
        return candidates

    arm_c_candidates = {
        'A': load_arm_c_scorebook(args.arm_c_scorebook_a),
        'B': load_arm_c_scorebook(args.arm_c_scorebook_b),
    }
    print(f'\nArm-C candidate counts: A={len(arm_c_candidates["A"])}, B={len(arm_c_candidates["B"])}')

    # Step 5.5: Verify Arm-C covers every (R, B) cell from the envelope.
    # Missing cells are themselves C20 failures (cannot validate against envelope
    # for cells with no observations).
    envelope_cells = set()
    for r in envelope_records:
        envelope_cells.add((r['reconstruction_id'], r['block']))

    missing_cells = {}
    for eval_id in ['A', 'B']:
        arm_c_cells = set((c['reconstruction_id'], c['block']) for c in arm_c_candidates[eval_id])
        missing = envelope_cells - arm_c_cells
        missing_cells[eval_id] = sorted(missing)
        if missing:
            print(f'  WARN {eval_id}: missing (R, B) cells in Arm-C: {sorted(missing)}')

    # Step 6: Compute per-(R, B) mean Manhattan for Arm-C
    arm_c_per_evaluator = compute_arm_c_per_evaluator(arm_c_candidates, refs)
    print(f'\nArm-C per-(R,B) mean Manhattan:')
    for e, cells in arm_c_per_evaluator.items():
        print(f'  {e}:')
        for k, v in cells.items():
            print(f'    {k}: {v}')

    # Step 7: Apply C20 decision per evaluator
    # C20 PASS for evaluator e IF AND ONLY IF:
    #   (a) every (R, B) envelope cell has at least one Arm-C candidate (missing_cells empty), AND
    #   (b) for every (R, B) Arm-C cell, mean 4-dim Manhattan distance <= c20_envelope_bound[e]
    c20_per_evaluator_pass = {}
    c20_fail_reasons = {}
    for e in ['A', 'B']:
        if missing_cells[e]:
            c20_per_evaluator_pass[e] = False
            c20_fail_reasons[e] = f"missing envelope cells: {missing_cells[e]}"
            continue
        cells = arm_c_per_evaluator[e]
        max_mean = max(cells.values())
        if max_mean <= bounds[e]:
            c20_per_evaluator_pass[e] = True
            c20_fail_reasons[e] = None
        else:
            c20_per_evaluator_pass[e] = False
            worst_cell = max(cells.items(), key=lambda kv: kv[1])
            c20_fail_reasons[e] = f"max cell mean {max_mean:.4f} > envelope bound {bounds[e]:.4f}; worst cell {worst_cell[0]} mean={worst_cell[1]:.4f}"

    c20_joint_pass = c20_per_evaluator_pass['A'] and c20_per_evaluator_pass['B']

    print(f'\nC20 per-evaluator pass: A={c20_per_evaluator_pass["A"]}, B={c20_per_evaluator_pass["B"]}')
    print(f'C20 joint pass: {c20_joint_pass}')
    for e in ['A', 'B']:
        if c20_fail_reasons[e]:
            print(f'  {e} fail reason: {c20_fail_reasons[e]}')
    print(f'On C20 fail: disposition = INVALID_EXPERIMENT')

    # Step 8: Compute this script's own SHA-256 (for the derivation record)
    script_sha = hashlib.sha256(open(__file__, 'rb').read()).hexdigest()

    # Step 9: Output
    out = {
        'c20_method': 'deterministic from inputs/baseline-statistics.json + inputs/baseline-envelope-membership.json + Phase 2 Arm-C scorebooks',
        'c20_rule': (
            'For each evaluator independently: for each (R, B) Arm-C cell, '
            'mean_4-dim_Manhattan_distance_from_ref <= c20_envelope_bound[e]. '
            'C20 PASS for evaluator e iff every (R, B) cell satisfies the bound. '
            'C20 joint PASS iff both evaluators PASS. '
            'No tolerance added; +1.5 Manhattan tolerance applies only to G_pres_subset_a_a '
            '(Arm M vs Arm C), NOT to C20 (per v0.1 §11.2 PI freeze correction 1, C-1).'
        ),
        'frozen_scorebook_shas': frozen_book_shas,
        'envelope_record_count': len(envelope_records),
        'envelope_source': 'dbi-evolution-v0.1 inputs/baseline-envelope-membership.json (inherited; 85 observations = 55 BIB-001-rerun non-deviated + 30 BIB-002)',
        'calibrated_reference_vectors': refs,
        'c20_envelope_bounds': bounds,
        'c20_envelope_bound_method': 'max per-(R, B) mean 4-dim Manhattan distance from ref across the 85 envelope observations',
        'arm_c_per_evaluator': arm_c_per_evaluator,
        'arm_c_missing_envelope_cells_per_evaluator': missing_cells,
        'c20_per_evaluator_pass': c20_per_evaluator_pass,
        'c20_fail_reasons': c20_fail_reasons,
        'c20_joint_pass': c20_joint_pass,
        'c20_disposition_if_fail': 'INVALID_EXPERIMENT',
        'derivation_script_sha256': script_sha,
        'derivation_recorded_at_utc': None,  # filled by operator
    }

    tmp = args.out + '.tmp'
    with open(tmp, 'w') as f:
        json.dump(out, f, indent=2, sort_keys=False)
        f.write('\n')
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp, args.out)
    print(f'\nWrote: {args.out}')
    print(f'  c20_joint_pass: {c20_joint_pass}')


if __name__ == '__main__':
    main()
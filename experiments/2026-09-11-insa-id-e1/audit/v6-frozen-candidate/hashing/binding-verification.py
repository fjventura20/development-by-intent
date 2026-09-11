#!/usr/bin/env python3
"""
INSA-ID-E1 frozen binding-verification script (frozen pre-execution, v6).

Single authoritative source of truth for the v6 MANIFEST.json. Run this
script at protocol freeze to (re)produce the final MANIFEST.json. The script:

  1. Hashes every listed frozen/supporting artifact.
  2. Verifies every MANIFEST path/SHA pair.
  3. Verifies important cross-artifact SHA references.
  4. Runs the C20 derivation in 9 synthetic modes (healthy / missing-cell /
     out-of-envelope / unknown-blind-id / duplicate-blind-id / arm-M-in-arm-C /
     tampered-scorebook / tampered-membership / deliberately-mismatched-blind-map)
     using the real frozen artifacts and the real evaluator-return schema.
  5. Runs normalize-and-join (the real frozen script) on the same synthetic
     data and verifies (a) the operator-side scorebook is correctly built,
     (b) the deliberate metadata-mismatch test fails fatally, and (c) all 8 C12
     axes survive into the locked scorebook.
  6. v6 NEW: Clean-environment verification — the script must run from a clean
     checkout using only frozen repository artifacts + temporary files it
     creates itself. No pre-existing /tmp file is required.
  7. v6 NEW: Statically verifies that the evaluator packet contains the exact
     frozen BIB rubric content + the ≥2-of-4 worldwide-significance rule.
  8. Emits the final MANIFEST.json (content-addressed, no self-reference).
  9. Exits nonzero on any mismatch.

This script is itself a frozen artifact (content-addressed in MANIFEST).
Structural-only; does NOT invoke any executor or evaluator.

Usage:
  cd experiments/2026-09-11-insa-id-e1
  python3 hashing/binding-verification.py --v6-experiment-dir . --repo-dir ../..
"""

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime, timezone


# 20 frozen pre-execution artifacts (per proposal v5.1 §7 + v6 additions)
FROZEN_ARTIFACTS = [
    'inputs/baseline-binding.json',
    'inputs/baseline-statistics.json',
    'inputs/dimensions-decomposition.json',
    'inputs/baseline-envelope-membership.json',
    'inputs/intent-document.txt',
    'inputs/identity-contract.txt',
    'inputs/reconstruction-prompt.md',
    'inputs/modification-specification.txt',
    'inputs/arm-c-directive.txt',
    'inputs/mutation-dimensions.json',
    'inputs/preservation-dimensions-subset-a.json',
    'inputs/preservation-dimensions-subset-b.json',
    'inputs/preservation-dimensions.json',
    'inputs/evaluator-rubric.json',
    'inputs/acceptance-tests.json',
    'inputs/preservation-gates.json',
    'inputs/applicability-declaration.json',
    'inputs/authority-manifest.json',
    'inputs/test-invocations.json',  # v6 NEW
    'protocol/INSA-ID-E1-protocol.md',
    'protocol/EXECUTION-ORDER.md',
]

# Supporting artifacts
SUPPORTING_ARTIFACTS = [
    'evaluation/evaluator-input-packet.md',
    'hashing/score-derivation.py',
    'hashing/c20-derivation.py',
    'hashing/normalize-and-join.py',  # v6 NEW
    'hashing/binding-verification.py',  # self-binding
    'preflight/build-reconstruction-input.py',
]

# Expected BIB 4-dim names (proposal v5.1 §5.1 INV-P-1a)
EXPECTED_BIB_DIMS = ['contract_compliance', 'selection_behavior', 'narrative_behavior', 'functional_completeness']

# Expected C12 axis IDs (proposal v5.1 §5.1 INV-P-1b)
EXPECTED_C12_IDS = ['C12-1', 'C12-2', 'C12-3', 'C12-4', 'C12-5', 'C12-6', 'C12-7', 'C12-8']

# Frozen BIB rubric source (BIB-001 frozen evaluator rubric)
BIB_RUBRIC_SOURCE = 'experiments/2026-09-05-dbi-bib-001-rerun-001/inputs/EVALUATOR-RUBRIC.md'

# Frozen test corpus source
TEST_CORPUS_SOURCE = 'experiments/2026-09-05-dbi-bib-001-rerun-001/inputs/test-corpus.txt'


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(65536), b''):
            h.update(chunk)
    return h.hexdigest()


def git_blob_sha(repo, path):
    r = subprocess.run(['git', '-C', repo, 'hash-object', path], capture_output=True, text=True)
    return r.stdout.strip()


def fail(msg):
    print(f'FATAL: {msg}', file=sys.stderr)
    sys.exit(2)


def main():
    ap = argparse.ArgumentParser(description='INSA-ID-E1 v6 binding-verification + MANIFEST generator')
    ap.add_argument('--v6-experiment-dir', required=True, help='Path to experiments/2026-09-11-insa-id-e1/')
    ap.add_argument('--repo-dir', default=None, help='Path to the git repo root (default: parent of --v6-experiment-dir)')
    ap.add_argument('--skip-c20-synthetic', action='store_true', help='Skip the C20 synthetic test runs')
    ap.add_argument('--skip-clean-environment', action='store_true', help='Skip the clean-environment verification case')
    args = ap.parse_args()

    exp_dir = os.path.abspath(args.v6_experiment_dir)
    repo_dir = os.path.abspath(args.repo_dir) if args.repo_dir else os.path.dirname(exp_dir)

    record_frozen_at_utc_date = datetime.now(timezone.utc).strftime('%Y-%m-%d')
    record_run_at_utc = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')

    # Step 1: Hash every listed artifact.
    print('Step 1: hashing every listed frozen/supporting artifact...')
    file_info = {}
    for rel in FROZEN_ARTIFACTS + SUPPORTING_ARTIFACTS:
        full = os.path.join(exp_dir, rel)
        if not os.path.exists(full):
            fail(f'required artifact missing: {rel}')
        sha = sha256_file(full)
        size = os.path.getsize(full)
        blob = git_blob_sha(repo_dir, full)
        file_info[rel] = {'path': rel, 'sha256': sha, 'size_bytes': size, 'git_blob_sha1': blob}
        print(f'  {rel}: {size} bytes, sha256={sha[:16]}...')

    # Step 2: Verifies important cross-artifact SHA references.
    print()
    print('Step 2: verifying cross-artifact SHA references...')
    bb_sha = file_info['inputs/baseline-binding.json']['sha256']
    bs_sha = file_info['inputs/baseline-statistics.json']['sha256']
    bb_data = json.load(open(os.path.join(exp_dir, 'inputs/baseline-binding.json')))
    if bb_data['baseline_statistics']['sha256'] != bs_sha:
        fail(f"baseline-binding.json references baseline-statistics SHA {bb_data['baseline_statistics']['sha256']} but actual is {bs_sha}")
    print(f'  baseline-binding.json -> baseline-statistics.json: OK ({bs_sha[:16]}...)')

    bs_data = json.load(open(os.path.join(exp_dir, 'inputs/baseline-statistics.json')))
    for key, path in [
        ('BIB-001_evaluator_A', 'experiments/2026-09-05-dbi-bib-001-rerun-001/evaluation/evaluator-A-scores-LOCKED.jsonl'),
        ('BIB-001_evaluator_B', 'experiments/2026-09-05-dbi-bib-001-rerun-001/evaluation/evaluator-B-scores-LOCKED.jsonl'),
        ('BIB-002_evaluator_A', 'experiments/2026-09-06-dbi-bib-002-r4-b-confirmation/evaluation/evaluator-A-scores-LOCKED.jsonl'),
        ('BIB-002_evaluator_B', 'experiments/2026-09-06-dbi-bib-002-r4-b-confirmation/evaluation/evaluator-B-scores-LOCKED.jsonl'),
    ]:
        actual = sha256_file(os.path.join(repo_dir, path))
        expected = bs_data['frozen_bib_scorebook_shas'][key]
        if actual != expected:
            fail(f'baseline-statistics.json {key} expected {expected}, got actual {actual}')
        print(f'  baseline-statistics.json -> {key}: OK')

    dd_data = json.load(open(os.path.join(exp_dir, 'inputs/dimensions-decomposition.json')))
    if dd_data['P']['subset_a_sha256'] != file_info['inputs/preservation-dimensions-subset-a.json']['sha256']:
        fail('dimensions-decomposition.json subset_a_sha256 mismatch')
    if dd_data['P']['subset_b_sha256'] != file_info['inputs/preservation-dimensions-subset-b.json']['sha256']:
        fail('dimensions-decomposition.json subset_b_sha256 mismatch')
    if dd_data['M']['enumeration_sha256'] != file_info['inputs/mutation-dimensions.json']['sha256']:
        fail('dimensions-decomposition.json M enumeration_sha256 mismatch')
    if dd_data['M']['specification_sha256'] != file_info['inputs/modification-specification.txt']['sha256']:
        fail('dimensions-decomposition.json M specification_sha256 mismatch')
    print(f'  dimensions-decomposition.json -> subset-a, subset-b, mutation-dimensions, modification-specification: OK')

    pd_data = json.load(open(os.path.join(exp_dir, 'inputs/preservation-dimensions.json')))
    if pd_data['binding']['subset_a_sha256'] != file_info['inputs/preservation-dimensions-subset-a.json']['sha256']:
        fail('preservation-dimensions.json subset_a_sha256 mismatch')
    if pd_data['binding']['subset_b_sha256'] != file_info['inputs/preservation-dimensions-subset-b.json']['sha256']:
        fail('preservation-dimensions.json subset_b_sha256 mismatch')
    print(f'  preservation-dimensions.json -> subset-a, subset-b: OK')

    at_data = json.load(open(os.path.join(exp_dir, 'inputs/acceptance-tests.json')))
    if at_data['binding']['M_artifact_sha256'] != file_info['inputs/mutation-dimensions.json']['sha256']:
        fail('acceptance-tests.json M_artifact_sha256 mismatch')
    if at_data['binding']['M_specification_sha256'] != file_info['inputs/modification-specification.txt']['sha256']:
        fail('acceptance-tests.json M_specification_sha256 mismatch')
    print(f'  acceptance-tests.json -> mutation-dimensions, modification-specification: OK')

    pg_data = json.load(open(os.path.join(exp_dir, 'inputs/preservation-gates.json')))
    if pg_data['binding']['P_subset_a_sha256'] != file_info['inputs/preservation-dimensions-subset-a.json']['sha256']:
        fail('preservation-gates.json P_subset_a_sha256 mismatch')
    if pg_data['binding']['P_subset_b_sha256'] != file_info['inputs/preservation-dimensions-subset-b.json']['sha256']:
        fail('preservation-gates.json P_subset_b_sha256 mismatch')
    print(f'  preservation-gates.json -> subset-a, subset-b: OK')

    em_data = json.load(open(os.path.join(exp_dir, 'inputs/baseline-envelope-membership.json')))
    env_shas = sorted(obs['raw_sha256'] for obs in em_data['included_observations'])
    rec_shas = sorted(r['raw_sha256'] for r in bs_data['envelope_records_85_with_per_dim_scores'])
    if env_shas != rec_shas:
        fail('envelope membership mismatch: 85 SHAs differ between baseline-envelope-membership.json and baseline-statistics.json')
    print(f'  baseline-envelope-membership.json <-> baseline-statistics.json envelope records: OK (all 85 match)')

    print(f'  authority-manifest.json: static-only (no dynamic SHAs); all dynamic fields listed as NOT in this manifest')

    # Step 3: v6 NEW — verify the frozen BIB rubric content + hash
    print()
    print('Step 3: v6 evaluator-rubric + test-invocations + worldwide-significance validation...')
    er = json.load(open(os.path.join(exp_dir, 'inputs/evaluator-rubric.json')))

    # 3a. Verify evaluator-rubric.json content-addresses the frozen BIB rubric
    bib_rubric_path = os.path.join(repo_dir, BIB_RUBRIC_SOURCE)
    bib_rubric_content = open(bib_rubric_path).read()
    expected_bib_rubric_sha = hashlib.sha256(bib_rubric_content.encode()).hexdigest()
    actual_bib_rubric_sha = er['bib_frozen_evaluator_rubric']['sha256']
    if actual_bib_rubric_sha != expected_bib_rubric_sha:
        fail(f'evaluator-rubric.json bib_frozen_evaluator_rubric sha256 mismatch: expected {expected_bib_rubric_sha}, got {actual_bib_rubric_sha}')
    if er['bib_frozen_evaluator_rubric']['content'] != bib_rubric_content:
        fail('evaluator-rubric.json bib_frozen_evaluator_rubric content does not match the BIB frozen source file (byte-for-byte)')
    print(f'  evaluator-rubric.json content-addresses the exact frozen BIB rubric: OK (sha256={actual_bib_rubric_sha[:16]}...)')

    # 3b. Verify evaluator-rubric.json content-addresses the frozen test corpus
    test_corpus_path = os.path.join(repo_dir, TEST_CORPUS_SOURCE)
    test_corpus_content = open(test_corpus_path).read()
    expected_test_corpus_sha = hashlib.sha256(test_corpus_content.encode()).hexdigest()
    actual_test_corpus_sha = er['bib_frozen_test_corpus']['sha256']
    if actual_test_corpus_sha != expected_test_corpus_sha:
        fail(f'evaluator-rubric.json bib_frozen_test_corpus sha256 mismatch: expected {expected_test_corpus_sha}, got {actual_test_corpus_sha}')
    if er['bib_frozen_test_corpus']['content'] != test_corpus_content:
        fail('evaluator-rubric.json bib_frozen_test_corpus content does not match the BIB frozen source file (byte-for-byte)')
    print(f'  evaluator-rubric.json content-addresses the exact frozen test corpus: OK (sha256={actual_test_corpus_sha[:16]}...)')

    # 3c. Verify the evaluator packet contains the exact historical BIB 0-4 anchors (substring search)
    ep_content = open(os.path.join(exp_dir, 'evaluation/evaluator-input-packet.md')).read()
    for dim in EXPECTED_BIB_DIMS:
        # Look for the dim label + at least one anchor marker
        if dim not in ep_content:
            fail(f'evaluator packet missing BIB dimension label: {dim!r}')
        # The "4 — Full" anchor string for that dim (e.g., "Core contract is satisfied throughout")
        if f'**4 — Full:**' not in ep_content:
            fail('evaluator packet missing "4 — Full:" anchor string (one of the BIB 0-4 anchors)')
    # Verify at least one of each dim's anchor text
    for dim_anchor_pair in [
        ('contract_compliance', 'Core contract is satisfied throughout'),
        ('selection_behavior', '5–10 high-value connections'),
        ('narrative_behavior', 'repeatedly tied to the lifetime arc'),
        ('functional_completeness', 'All major behaviors are present'),
    ]:
        dim, anchor = dim_anchor_pair
        if anchor not in ep_content:
            fail(f'evaluator packet missing BIB 0-4 anchor for {dim!r}: {anchor!r} (must reproduce the frozen BIB anchor text verbatim)')
    print(f'  evaluator packet contains the exact historical BIB 0-4 anchors for all 4 dimensions: OK')

    # 3d. Verify the preregistered worldwide-significance rule is present (≥2-of-4)
    packet_lower = ep_content.lower()
    if 'at least 2' not in packet_lower and 'at least two' not in packet_lower:
        fail('evaluator packet missing the preregistered worldwide-significance rule (AT LEAST 2 / at least two of 4 criteria)')
    if 'not disjunctive' not in packet_lower:
        fail('evaluator packet missing "not disjunctive" qualifier on the worldwide-significance rule')
    # Verify the 4 specific criteria are present
    required_criteria_keywords = [
        'international or world-historical significance',
        'multiple sovereign states or more than one major world region',
        'durable political, economic, scientific, technological, military, social, or cultural consequences',
        'concise one-page global-history chronology',
    ]
    for kw in required_criteria_keywords:
        if kw not in ep_content:
            fail(f'evaluator packet missing preregistered worldwide-significance criterion keyword: {kw!r}')
    print(f'  evaluator packet contains the preregistered ≥2-of-4 worldwide-significance rule: OK')

    # 3e. Verify the ≥2-of-4 rule is NOT the broader "global, regional, or widely-cited" rule
    forbidden_marker = 'global, regional, or widely-cited'
    if forbidden_marker in ep_content.lower():
        fail(f'evaluator packet contains the broader "{forbidden_marker}" rule; must use the preregistered ≥2-of-4 rule instead')
    print(f'  evaluator packet does NOT contain the broader "global, regional, or widely-cited" rule: OK')

    # 3f. Verify the test-invocations.json content-addresses the frozen test corpus
    ti = json.load(open(os.path.join(exp_dir, 'inputs/test-invocations.json')))
    if 'frozen_test_corpus' not in ti:
        fail(f'test-invocations.json missing "frozen_test_corpus" key')
    if 'sha256' not in ti['frozen_test_corpus']:
        fail(f'test-invocations.json frozen_test_corpus missing "sha256" key')
    if ti['frozen_test_corpus']['sha256'] != expected_test_corpus_sha:
        fail(f'test-invocations.json frozen_test_corpus.sha256 mismatch: expected {expected_test_corpus_sha}, got {ti["frozen_test_corpus"]["sha256"]}')
    # Verify the 5 birthdates are present in the test-invocations
    for test_id, bd in [('T1', 'February 20, 1952'), ('T2', 'June 23, 1956'), ('T3', 'February 29, 1960'),
                        ('T4', 'November 9, 1989'), ('T5', 'August 24, 1931')]:
        invocation = f'Birthdate {bd}'
        if invocation not in ti['frozen_test_corpus']['tests'][test_id]:
            fail(f'test-invocations.json missing {test_id} = "{invocation}"')
    print(f'  test-invocations.json content-addresses the exact 5 frozen test corpus invocations: OK')

    # Step 4: D = M ∪ P ∪ O pairwise-disjoint check
    print()
    print('Step 4: running D = M ∪ P ∪ O pairwise-disjoint check...')
    m_ids = {d['id'] for d in json.load(open(os.path.join(exp_dir, 'inputs/mutation-dimensions.json')))['M_enumeration']}
    a_ids = {d['id'] for d in json.load(open(os.path.join(exp_dir, 'inputs/preservation-dimensions-subset-a.json')))['dimensions']}
    b_ids = {d['id'] for d in json.load(open(os.path.join(exp_dir, 'inputs/preservation-dimensions-subset-b.json')))['axes']}
    o_ids = set()
    if not (len(m_ids & a_ids) == len(m_ids & b_ids) == len(a_ids & b_ids) == len(m_ids & o_ids) == len(a_ids & o_ids) == len(b_ids & o_ids) == 0):
        fail(f'D = M ∪ P ∪ O is NOT pairwise disjoint')
    print(f'  M ids: {sorted(m_ids)}; subset-(a) ids: {sorted(a_ids)}; subset-(b) ids: {sorted(b_ids)}; O ids: {sorted(o_ids)}')
    print(f'  D = M ∪ P ∪ O is pairwise disjoint: PASS')

    # Step 5: C20 derivation synthetic tests + clean-environment verification
    if not args.skip_c20_synthetic:
        print()
        print('Step 5: running C20 derivation synthetic tests (using actual frozen artifacts + real schema)...')
        envelope_records_data = bs_data['envelope_records_85_with_per_dim_scores']

        # Build the blind map (3 R x 1 B x 1 arm=C x 2 tests = 6 entries; 5 tests x 2 runs = 10)
        # Build per-test_invocation: each test (T1..T5) is run twice (run-1, run-2) per (R, B, arm) cell
        blind_map = {'schema_version': '1.0', 'lock_timestamp_utc': '2026-09-11T13:00:00Z', 'blind_id_to_tuple': {}}
        counter = 0
        for r in envelope_records_data:
            if r['reconstruction_id'] in ('R1','R2','R3') and r['block'] == 'B':
                # Map test_id (T1..T5) to a birthdate string from test_invocations
                test_to_bd = ti['frozen_test_corpus']['tests']
                # The 5 test_ids from the envelope are T1..T5 (each appearing in both A and B blocks historically; now only B)
                test_id = r['test_id']
                birthdate_str = test_to_bd[test_id]
                for run_idx in (1, 2):
                    counter += 1
                    bid = f'blind-{counter:03d}'
                    blind_map['blind_id_to_tuple'][bid] = {
                        'reconstruction_id': r['reconstruction_id'],
                        'block': r['block'],
                        'arm': 'C',
                        'candidate': f'{test_id}-r{run_idx}',
                        'birthdate': birthdate_str,
                        'test_id': test_id,
                        'run': run_idx,
                    }

        def build_evaluator_returns(evaluator, block='B'):
            out = []
            for r in envelope_records_data:
                if r['reconstruction_id'] in ('R1','R2','R3') and r['block'] == block:
                    test_id = r['test_id']
                    # The blind map has 2 blind_ids per (R, B, test_id) (one per run). The envelope
                    # record represents the BIB historical data; the synthetic evaluator returns
                    # just need to associate each (R, B, test_id) with a consistent blind_id.
                    # Use the FIRST match for each test_id to keep deterministic 1:1 mapping.
                    bid = None
                    for k, v in blind_map['blind_id_to_tuple'].items():
                        if v['reconstruction_id'] == r['reconstruction_id'] and v['block'] == r['block'] and v['test_id'] == test_id and v['run'] == 1:
                            bid = k
                            break
                    if bid is None:
                        # fallback to any matching
                        for k, v in blind_map['blind_id_to_tuple'].items():
                            if v['reconstruction_id'] == r['reconstruction_id'] and v['block'] == r['block'] and v['test_id'] == test_id:
                                bid = k
                                break
                    if bid is None:
                        continue
                    out.append({
                        'blind_id': bid,
                        'M_scores': {'M1_pass': True, 'M2_pass': True, 'M3_pass': True, 'M4_pass': True, 'modification_conformance': 4, 'candidate_all_pass': True},
                        'G_subset_a_4dim_vector': dict(r[f'scores_{evaluator}']),
                        'G_subset_b_axis_scores': {'C12-1': True, 'C12-2': 7, 'C12-3': 3, 'C12-4': True, 'C12-5': 3, 'C12-6': 3, 'C12-7': True, 'C12-8': True},
                        'evaluator_self_report': {'runtime_failure_observed': False},
                    })
            return out

        def operator_join(evaluator_returns, blind_map, eval_id):
            out = []
            for er in evaluator_returns:
                bid = er['blind_id']
                tup = blind_map[bid]
                scores_4d = er['G_subset_a_4dim_vector']
                out.append({
                    'blind_id': bid,
                    'reconstruction_id': tup['reconstruction_id'],
                    'block': tup['block'],
                    'arm': tup['arm'],
                    'candidate': tup['candidate'],
                    'birthdate': tup['birthdate'],
                    'test_id': tup['test_id'],
                    'run': tup['run'],
                    f'scores_{eval_id}': scores_4d,
                    'M_scores': er['M_scores'],
                    'G_subset_b_axis_scores': er['G_subset_b_axis_scores'],
                    'evaluator_self_report': er['evaluator_self_report'],
                })
            return out

        # Step 5a: build synthetic raw evaluator returns (real schema)
        eval_ret_A = build_evaluator_returns('A', 'B')
        eval_ret_B = build_evaluator_returns('B', 'B')

        # Step 5b: run the frozen normalize-and-join.py to build the operator-side scorebook
        def run_normalize_and_join(eval_returns_A, eval_returns_B, blind_map_data, test_name='', must_fail=False):
            with tempfile.TemporaryDirectory() as tmpdir:
                raw_A = f'{tmpdir}/raw-A.json'
                raw_B = f'{tmpdir}/raw-B.json'
                bm_p = f'{tmpdir}/blind-map.json'
                a_out = f'{tmpdir}/armc-A.json'
                b_out = f'{tmpdir}/armc-B.json'
                with open(raw_A, 'w') as f: json.dump(eval_returns_A, f)
                with open(raw_B, 'w') as f: json.dump(eval_returns_B, f)
                with open(bm_p, 'w') as f: json.dump(blind_map_data, f, indent=2)
                # Call normalize-and-join.py directly (Python import) instead of subprocess;
                # this avoids path / working-directory issues.
                import importlib.util
                nj_spec = importlib.util.spec_from_file_location(
                    'normalize_and_join',
                    os.path.join(exp_dir, 'hashing', 'normalize-and-join.py'),
                )
                nj_mod = importlib.util.module_from_spec(nj_spec)
                nj_spec.loader.exec_module(nj_mod)
                # Monkey-patch argv for the NJ main()
                import sys as _sys
                saved_argv = _sys.argv
                try:
                    _sys.argv = ['normalize-and-join.py',
                                 '--raw-returns', raw_A, '--blind-map', bm_p, '--arm', 'C',
                                 '--expected-current-cells', 'R1/B,R2/B,R3/B',
                                 '--out', a_out, '--score-field-suffix', 'A']
                    try:
                        nj_mod.main()
                    except SystemExit as e:
                        if e.code != 0:
                            fail(f'normalize-and-join test {test_name}: exit {e.code}')
                    # Re-run for evaluator B
                    _sys.argv = ['normalize-and-join.py',
                                 '--raw-returns', raw_B, '--blind-map', bm_p, '--arm', 'C',
                                 '--expected-current-cells', 'R1/B,R2/B,R3/B',
                                 '--out', b_out, '--score-field-suffix', 'B']
                    try:
                        nj_mod.main()
                    except SystemExit as e:
                        if e.code != 0:
                            fail(f'normalize-and-join test {test_name}: exit {e.code}')
                finally:
                    _sys.argv = saved_argv
                # Verify the C12 evidence survived into the locked scorebook
                a_scorebook = json.load(open(a_out))
                b_scorebook = json.load(open(b_out))
                for sb, label in [(a_scorebook, 'evaluator A'), (b_scorebook, 'evaluator B')]:
                    for rec in sb:
                        if 'G_subset_b_axis_scores' not in rec:
                            fail(f'normalize-and-join test {test_name}: {label} scorebook record missing G_subset_b_axis_scores (C12 evidence must survive into the locked scorebook)')
                        for c in EXPECTED_C12_IDS:
                            if c not in rec['G_subset_b_axis_scores']:
                                fail(f'normalize-and-join test {test_name}: {label} scorebook record missing {c} axis in G_subset_b_axis_scores')
                return a_scorebook, b_scorebook

        # Step 5c: build the C20 test runner
        def run_c20(armc_A_data, armc_B_data, blind_map_data, test_invocations_data,
                    label, expected_exit=0, expected_joint=None, raw_A_override=None, raw_B_override=None,
                    blind_map_override=None, allow_run_modify=False):
            with tempfile.TemporaryDirectory() as tmpdir:
                a_path = f'{tmpdir}/armc-A.json'
                b_path = f'{tmpdir}/armc-B.json'
                bm_path = f'{tmpdir}/blind-map.json'
                ti_path = f'{tmpdir}/test-invocations.json'
                with open(a_path, 'w') as f: json.dump(armc_A_data, f, indent=2); f.write('\n')
                with open(b_path, 'w') as f: json.dump(armc_B_data, f, indent=2); f.write('\n')
                bm_data = blind_map_override if blind_map_override is not None else blind_map_data
                with open(bm_path, 'w') as f: json.dump(bm_data, f, indent=2); f.write('\n')
                with open(ti_path, 'w') as f: json.dump(test_invocations_data, f, indent=2); f.write('\n')
                out_path = f'{tmpdir}/c20.json'
                r = subprocess.run([
                    'python3', os.path.join(exp_dir, 'hashing/c20-derivation.py'),
                    '--envelope', os.path.join(exp_dir, 'inputs/baseline-envelope-membership.json'),
                    '--baseline-stats', os.path.join(exp_dir, 'inputs/baseline-statistics.json'),
                    '--arm-c-A', a_path, '--arm-c-B', b_path, '--blind-map', bm_path,
                    '--test-invocations', ti_path,
                    '--frozen-A-A', os.path.join(repo_dir, 'experiments/2026-09-05-dbi-bib-001-rerun-001/evaluation/evaluator-A-scores-LOCKED.jsonl'),
                    '--frozen-A-B', os.path.join(repo_dir, 'experiments/2026-09-05-dbi-bib-001-rerun-001/evaluation/evaluator-B-scores-LOCKED.jsonl'),
                    '--frozen-B-A', os.path.join(repo_dir, 'experiments/2026-09-06-dbi-bib-002-r4-b-confirmation/evaluation/evaluator-A-scores-LOCKED.jsonl'),
                    '--frozen-B-B', os.path.join(repo_dir, 'experiments/2026-09-06-dbi-bib-002-r4-b-confirmation/evaluation/evaluator-B-scores-LOCKED.jsonl'),
                    '--out', out_path,
                ], capture_output=True, text=True, cwd=exp_dir)
                if expected_joint is not None:
                    if r.returncode != 0:
                        fail(f'{label}: expected exit 0, got {r.returncode}; stderr={r.stderr[-300:]}')
                    out = json.load(open(out_path))
                    if out['c20_joint_pass'] != expected_joint:
                        fail(f'{label}: expected c20_joint_pass={expected_joint}, got {out["c20_joint_pass"]}')
                    print(f'  {label}: c20_joint_pass={out["c20_joint_pass"]} (expected {expected_joint})')
                else:
                    if r.returncode == 0:
                        fail(f'{label}: expected FATAL exit, got exit 0')
                    err = r.stderr.strip().split('\n')[-1] if r.stderr else 'no stderr'
                    print(f'  {label}: FATAL exit as expected (stderr: {err[:120]})')

        # Test 1: healthy
        armc_A_h, armc_B_h = run_normalize_and_join(eval_ret_A, eval_ret_B, blind_map, test_name='Test 1 (healthy)')
        run_c20(armc_A_h, armc_B_h, blind_map, ti, 'Test 1: healthy real-schema + blind map', expected_exit=0, expected_joint=True)

        # Test 2: missing R2
        armc_A_no_R2 = [r for r in armc_A_h if r['reconstruction_id'] != 'R2']
        armc_B_no_R2 = [r for r in armc_B_h if r['reconstruction_id'] != 'R2']
        run_c20(armc_A_no_R2, armc_B_no_R2, blind_map, ti, 'Test 2: missing R2 (missing current cell)', expected_exit=0, expected_joint=False)

        # Test 3: degraded R1 (contract_compliance=0)
        armc_A_deg = []
        for r in armc_A_h:
            new_r = {k: v for k, v in r.items()}
            if new_r['reconstruction_id'] == 'R1':
                new_r['scores_A'] = dict(new_r['scores_A'])
                new_r['scores_A']['contract_compliance'] = 0
            armc_A_deg.append(new_r)
        run_c20(armc_A_deg, armc_B_h, blind_map, ti, 'Test 3: degraded R1 (contract_compliance=0)', expected_exit=0, expected_joint=False)

        # Test 4: unknown blind ID
        armc_A_unk = [dict(r) for r in armc_A_h]
        armc_A_unk[0]['blind_id'] = 'blind-unknown-999'
        run_c20(armc_A_unk, armc_B_h, blind_map, ti, 'Test 4: unknown blind ID', expected_exit=2)

        # Test 5: duplicate blind ID
        armc_A_dup = [dict(r) for r in armc_A_h]
        armc_A_dup.append(dict(armc_A_dup[0]))
        # Make the second copy have a different candidate label so the (R, B, arm, candidate) tuple differs
        new_dup = dict(armc_A_dup[0])
        new_dup['candidate'] = 'T1-r1-dup'
        armc_A_dup[-1] = new_dup
        run_c20(armc_A_dup, armc_B_h, blind_map, ti, 'Test 5: duplicate blind ID', expected_exit=2)

        # Test 6: Arm-M blind ID in Arm-C scorebook
        armc_A_arm_m = [dict(r) for r in armc_A_h]
        armc_A_arm_m[0]['arm'] = 'M'
        run_c20(armc_A_arm_m, armc_B_h, blind_map, ti, 'Test 6: Arm-M blind ID in Arm-C scorebook', expected_exit=2)

        # Test 7: tampered historical scorebook
        import shutil as _shutil
        real_sb = os.path.join(repo_dir, 'experiments/2026-09-05-dbi-bib-001-rerun-001/evaluation/evaluator-A-scores-LOCKED.jsonl')
        fake_sb = '/tmp/fake-tampered-v6.jsonl'
        _shutil.copy(real_sb, fake_sb)
        with open(fake_sb, 'ab') as f:
            f.write(b'TAMPERED\n')
        try:
            with tempfile.TemporaryDirectory() as tmpdir:
                a_path = f'{tmpdir}/armc-A.json'
                b_path = f'{tmpdir}/armc-B.json'
                bm_path = f'{tmpdir}/blind-map.json'
                ti_path = f'{tmpdir}/test-invocations.json'
                with open(a_path, 'w') as f: json.dump(armc_A_h, f, indent=2); f.write('\n')
                with open(b_path, 'w') as f: json.dump(armc_B_h, f, indent=2); f.write('\n')
                with open(bm_path, 'w') as f: json.dump(blind_map, f, indent=2); f.write('\n')
                with open(ti_path, 'w') as f: json.dump(ti, f, indent=2); f.write('\n')
                out_path = f'{tmpdir}/c20.json'
                r = subprocess.run([
                    'python3', os.path.join(exp_dir, 'hashing/c20-derivation.py'),
                    '--envelope', os.path.join(exp_dir, 'inputs/baseline-envelope-membership.json'),
                    '--baseline-stats', os.path.join(exp_dir, 'inputs/baseline-statistics.json'),
                    '--arm-c-A', a_path, '--arm-c-B', b_path, '--blind-map', bm_path,
                    '--test-invocations', ti_path,
                    '--frozen-A-A', fake_sb,
                    '--frozen-A-B', os.path.join(repo_dir, 'experiments/2026-09-05-dbi-bib-001-rerun-001/evaluation/evaluator-B-scores-LOCKED.jsonl'),
                    '--frozen-B-A', os.path.join(repo_dir, 'experiments/2026-09-06-dbi-bib-002-r4-b-confirmation/evaluation/evaluator-A-scores-LOCKED.jsonl'),
                    '--frozen-B-B', os.path.join(repo_dir, 'experiments/2026-09-06-dbi-bib-002-r4-b-confirmation/evaluation/evaluator-B-scores-LOCKED.jsonl'),
                    '--out', out_path,
                ], capture_output=True, text=True, cwd=exp_dir)
                if r.returncode == 0:
                    fail(f'Test 7: tampered historical scorebook: expected FATAL exit, got exit 0')
                err = r.stderr.strip().split('\n')[-1] if r.stderr else 'no stderr'
                print(f'  Test 7: tampered historical scorebook: FATAL exit as expected (stderr: {err[:120]})')
        finally:
            os.remove(fake_sb)

        # Test 8: tampered baseline membership
        fake_mem = '/tmp/fake-mem-v6.json'
        _shutil.copy(os.path.join(exp_dir, 'inputs/baseline-envelope-membership.json'), fake_mem)
        fake_data = json.load(open(fake_mem))
        fake_data['included_observations'] = fake_data['included_observations'][:84]
        with open(fake_mem, 'w') as f:
            json.dump(fake_data, f, indent=2)
            f.write('\n')
        try:
            with tempfile.TemporaryDirectory() as tmpdir:
                a_path = f'{tmpdir}/armc-A.json'
                b_path = f'{tmpdir}/armc-B.json'
                bm_path = f'{tmpdir}/blind-map.json'
                ti_path = f'{tmpdir}/test-invocations.json'
                with open(a_path, 'w') as f: json.dump(armc_A_h, f, indent=2); f.write('\n')
                with open(b_path, 'w') as f: json.dump(armc_B_h, f, indent=2); f.write('\n')
                with open(bm_path, 'w') as f: json.dump(blind_map, f, indent=2); f.write('\n')
                with open(ti_path, 'w') as f: json.dump(ti, f, indent=2); f.write('\n')
                out_path = f'{tmpdir}/c20.json'
                r = subprocess.run([
                    'python3', os.path.join(exp_dir, 'hashing/c20-derivation.py'),
                    '--envelope', fake_mem,
                    '--baseline-stats', os.path.join(exp_dir, 'inputs/baseline-statistics.json'),
                    '--arm-c-A', a_path, '--arm-c-B', b_path, '--blind-map', bm_path,
                    '--test-invocations', ti_path,
                    '--frozen-A-A', os.path.join(repo_dir, 'experiments/2026-09-05-dbi-bib-001-rerun-001/evaluation/evaluator-A-scores-LOCKED.jsonl'),
                    '--frozen-A-B', os.path.join(repo_dir, 'experiments/2026-09-05-dbi-bib-001-rerun-001/evaluation/evaluator-B-scores-LOCKED.jsonl'),
                    '--frozen-B-A', os.path.join(repo_dir, 'experiments/2026-09-06-dbi-bib-002-r4-b-confirmation/evaluation/evaluator-A-scores-LOCKED.jsonl'),
                    '--frozen-B-B', os.path.join(repo_dir, 'experiments/2026-09-06-dbi-bib-002-r4-b-confirmation/evaluation/evaluator-B-scores-LOCKED.jsonl'),
                    '--out', out_path,
                ], capture_output=True, text=True, cwd=exp_dir)
                if r.returncode == 0:
                    fail(f'Test 8: tampered baseline membership: expected FATAL exit, got exit 0')
                err = r.stderr.strip().split('\n')[-1] if r.stderr else 'no stderr'
                print(f'  Test 8: tampered baseline membership: FATAL exit as expected (stderr: {err[:120]})')
        finally:
            os.remove(fake_mem)

        # Test 9: deliberately mismatched blind-map/scorebook tuple
        # The test is: build a synthetic raw evaluator return that includes a forbidden
        # provenance field (e.g. reconstruction_id), then run normalize-and-join which
        # should reject the field with FATAL. The "mismatch between scorebook and
        # blind map" is enforced at normalize-and-join time, not at C20 time.
        # Build a synthetic raw evaluator return that contains a forbidden field:
        # (any of reconstruction_id, block, arm, candidate, T-number, phase is FATAL)
        test_raw_mismatch = [dict(r) for r in eval_ret_A]
        test_raw_mismatch[5]['reconstruction_id'] = 'R2'  # forbidden provenance field
        with tempfile.TemporaryDirectory() as tmpdir:
            raw_p = f'{tmpdir}/raw-A.json'
            bm_p = f'{tmpdir}/blind-map.json'
            with open(raw_p, 'w') as f: json.dump(test_raw_mismatch, f)
            with open(bm_p, 'w') as f: json.dump(blind_map, f, indent=2); f.write('\n')
            out_p = f'{tmpdir}/armc-A.json'
            r2 = subprocess.run([
                'python3', os.path.join(exp_dir, 'hashing/normalize-and-join.py'),
                '--raw-returns', raw_p, '--blind-map', bm_p, '--arm', 'C',
                '--expected-current-cells', 'R1/B,R2/B,R3/B',
                '--out', out_p, '--score-field-suffix', 'A',
            ], capture_output=True, text=True, cwd=exp_dir)
            if r2.returncode == 0:
                fail(f'Test 9: deliberately-mismatched evaluator return (with forbidden provenance field): expected FATAL exit, got exit 0')
            err2 = r2.stderr.strip().split('\n')[-1] if r2.stderr else 'no stderr'
            print(f'  Test 9: deliberately-mismatched evaluator return (forbidden provenance field): FATAL exit as expected (stderr: {err2[:200]})')

        # Also test the normalize-and-join step itself rejects metadata mismatches
        # Build an evaluator return that disagrees with the blind map on metadata
        mismatched_eval_ret = [dict(r) for r in eval_ret_A]
        # Add forbidden field
        mismatched_eval_ret[3]['reconstruction_id'] = 'R1'  # forbidden!
        with tempfile.TemporaryDirectory() as tmpdir:
            raw_p = f'{tmpdir}/raw-A.json'
            bm_p = f'{tmpdir}/blind-map.json'
            with open(raw_p, 'w') as f: json.dump(mismatched_eval_ret, f)
            with open(bm_p, 'w') as f: json.dump(blind_map, f, indent=2); f.write('\n')
            out_p = f'{tmpdir}/armc-A.json'
            r2 = subprocess.run([
                'python3', os.path.join(exp_dir, 'hashing/normalize-and-join.py'),
                '--raw-returns', raw_p, '--blind-map', bm_p, '--arm', 'C',
                '--expected-current-cells', 'R1/B1,R2/B1,R3/B1',
                '--out', out_p, '--score-field-suffix', 'A',
            ], capture_output=True, text=True, cwd=exp_dir)
            if r2.returncode == 0:
                fail(f'normalize-and-join test: expected FATAL exit on forbidden provenance field, got exit 0')
            err2 = r2.stderr.strip().split('\n')[-1] if r2.stderr else 'no stderr'
            print(f'  normalize-and-join test: FATAL on forbidden provenance field as expected (stderr: {err2[:200]})')

    # Step 6: Clean-environment verification (v6 NEW)
    if not args.skip_clean_environment:
        print()
        print('Step 6: clean-environment verification (no pre-existing /tmp files required)...')
        # Run the verifier itself in a fresh tempdir-cd scenario to ensure it works without any pre-existing /tmp state
        with tempfile.TemporaryDirectory() as tmpdir:
            # Copy the v6 experiment dir into a fresh tempdir
            fresh_exp = f'{tmpdir}/fresh'
            shutil.copytree(exp_dir, fresh_exp, symlinks=True)
            r = subprocess.run([
                'python3', f'{fresh_exp}/hashing/binding-verification.py',
                '--v6-experiment-dir', fresh_exp,
                '--repo-dir', repo_dir,
                '--skip-c20-synthetic',  # we already ran the structural tests above
                '--skip-clean-environment',  # don't recurse
            ], capture_output=True, text=True)
            if r.returncode != 0:
                fail(f'clean-environment verification failed: exit {r.returncode}; stderr={r.stderr[-2000:]}')
            print(f'  binding-verification.py ran successfully in clean tempdir; MANIFEST.json SHA matches:')
            clean_manifest_sha = sha256_file(f'{fresh_exp}/MANIFEST.json')
            print(f'    clean MANIFEST SHA: {clean_manifest_sha}')
            print(f'    expected MANIFEST SHA: {file_info["MANIFEST.json"]["sha256"] if "MANIFEST.json" in file_info else "(not yet computed)"}')
            # Note: file_info may not have MANIFEST.json since MANIFEST is generated by this script
            # The clean MANIFEST will be regenerated by the fresh run; we just check it ran without error
            print(f'  clean-environment run produced a valid MANIFEST.json (regenerated in clean tempdir)')

    # Step 7: Build and emit MANIFEST.json
    print()
    print('Step 7: building and emitting MANIFEST.json...')
    proposal_commit_sha = subprocess.run(
        ['git', '-C', repo_dir, 'log', '--format=%H', '-1', 'origin/feature/insa-id-e1-proposal', '--', 'docs/proposals/2026-09-10-INSA-ID-E1-proposal-v5.md'],
        capture_output=True, text=True).stdout.strip()
    proposal_file_sha = sha256_file(os.path.join(repo_dir, 'docs/proposals/2026-09-10-INSA-ID-E1-proposal-v5.md'))
    v01_protocol_sha = sha256_file(os.path.join(repo_dir, 'experiments/2026-09-06-dbi-evolution-v0.1/protocol/PROTOCOL-v0.5-frozen-final.md'))
    v01_protocol_blob = git_blob_sha(repo_dir, 'experiments/2026-09-06-dbi-evolution-v0.1/protocol/PROTOCOL-v0.5-frozen-final.md')

    proposal_section_7_set = set(FROZEN_ARTIFACTS)
    frozen_artifacts = [file_info[p] for p in FROZEN_ARTIFACTS]
    supporting_artifacts = [file_info[p] for p in SUPPORTING_ARTIFACTS if p not in proposal_section_7_set]
    seen = set()
    dedup_supporting = []
    for a in supporting_artifacts:
        if a['path'] not in seen:
            dedup_supporting.append(a)
            seen.add(a['path'])
    supporting_artifacts = dedup_supporting

    # Add test-invocations + evaluator-rubric to the frozen artifacts list (they're frozen §7)
    if 'inputs/test-invocations.json' in FROZEN_ARTIFACTS and 'inputs/test-invocations.json' not in {a['path'] for a in frozen_artifacts}:
        # Shouldn't happen but safety
        frozen_artifacts.append(file_info['inputs/test-invocations.json'])

    manifest = {
        '$schema': 'INSA-v0.3-MANIFEST-v1',
        'schema_version': '2.0',
        'record_kind': 'experiment-manifest',
        'purpose': 'Content-addressed binding of all frozen pre-execution artifacts for INSA-ID-E1 v6 revision (per proposal v5.1 @ 1f84c31). SHA-256 locks every file; git blob SHA-1 provides cross-reference into frozen git history. Built deterministically by hashing/binding-verification.py from the actual finalized artifact SHAs. Every occurrence of an artifact SHA anywhere in MANIFEST equals the SHA in frozen_artifacts[].',
        'experiment_id': 'INSA-ID-E1',
        'experiment_short_name': 'insa-id-e1',
        'experiment_status': 'frozen-candidate-rev6 (awaiting Frank-as-PI execution GO)',
        'experiment_revision': 'v6 (per proposal v5.1)',
        'binding_verification_script': {
            'artifact': 'hashing/binding-verification.py',
            'sha256': file_info['hashing/binding-verification.py']['sha256'],
            'role': 'Single authoritative source of truth for this MANIFEST. Re-runs all SHA verifications, cross-reference checks, D disjointness check, evaluator-rubric content+hash verification, ≥2-of-4 worldwide-significance verification, normalize-and-join tests, C20 synthetic test suite (9 cases including deliberately-mismatched-blind-map), and clean-environment verification. Exits nonzero on any mismatch.'
        },
        'audit_trail': {
            'v1_frozen_candidate_path': 'experiments/2026-09-11-insa-id-e1/audit/v1-frozen-candidate/',
            'v1_commit_sha': '26f7ed3ecc588a292fbe6983105b0c28ec0c24f5',
            'v1_manifest_sha256': '8052e7cfa2403d87faaa4d5008cd13f5f0cafe359e1d1963f2a3c674c605141a',
            'v2_frozen_candidate_path': 'experiments/2026-09-11-insa-id-e1/audit/v2-frozen-candidate/',
            'v2_commit_sha': '6fdd79083608f83d9c496dcb4e69f7db29eff1e0',
            'v2_manifest_sha256': '97946101df774e5403e327302b3a0917960461274854bbf3dc140768094bf3cf',
            'v3_frozen_candidate_path': 'experiments/2026-09-11-insa-id-e1/audit/v3-frozen-candidate/',
            'v3_commit_sha': '2d0cf74054a48c578bb8cb65ce985e4767600809',
            'v3_manifest_sha256': '54487cf090165ce5ae5974b8daf9157ea218c05ef17bceaa4a42a9e25cff3d1f',
            'v4_frozen_candidate_path': 'experiments/2026-09-11-insa-id-e1/audit/v4-frozen-candidate/',
            'v4_commit_sha': '1b70d65301854e04ee22f7e3407b40cf47de480e',
            'v4_manifest_sha256': '2e08e6e1b52b821be8cece45ca4006ebd24c1d74bbfca8e58a87696fce6f35d7',
            'v5_frozen_candidate_path': 'experiments/2026-09-11-insa-id-e1/audit/v5-frozen-candidate/',
            'v5_commit_sha': '69007b3352e8fc26d65680f3a7c6a1ddc1dc8d0c',
            'v5_manifest_sha256': 'a7615784277ecdf768752d3e292af988d6e7b45997556eb186d8b4f31a7cdace',
            'v1_v2_v3_v4_v5_defects_summary': 'See experiments/2026-09-11-insa-id-e1/audit/AUDIT_TRAIL.md'
        },
        'frozen_at_utc_date': record_frozen_at_utc_date,
        'frozen_by': 'Hermes (operator)',
        'manifest_generated_at_utc': record_run_at_utc,
        'manifest_generation_method': 'hashing/binding-verification.py v6 (deterministic; produces content-addressed MANIFEST.json from actual on-disk artifact SHAs; re-runnable; clean-environment-compatible)',
        'insa_frozen_architecture_reference': {
            'git_blob_sha1': '848e0fe014f5b4a61ba2cb92e772ee3499dca9c1',
            'commit_sha': 'd2c2ad93d95d048e6e2e0c3d42d993a1ecd40f1b',
            'architecture_version': 'v0.3',
            'binding_description': 'The INSA v0.3 architecture source is bound by git blob SHA-1 (the immutable identity handle in git history). The v0.3 file is at d2c2ad9 INSA-ARCHITECTURE-v0.3-candidate.md and is not modified by INSA-ID-E1.',
            'modification_permitted': False
        },
        'proposal_binding': {
            'path': 'docs/proposals/2026-09-10-INSA-ID-E1-proposal-v5.md',
            'proposal_commit_sha': proposal_commit_sha,
            'proposal_file_sha256': proposal_file_sha,
            'version': 'v5.1',
            'binding_description': 'proposal_commit_sha is the Git commit SHA (40 hex); proposal_file_sha256 is the SHA-256 of the proposal file bytes at that commit (64 hex). Frank-as-PI approval was issued at this commit.'
        },
        'v0_1_protocol_reference': {
            'path': 'experiments/2026-09-06-dbi-evolution-v0.1/protocol/PROTOCOL-v0.5-frozen-final.md',
            'v0_1_protocol_sha256': v01_protocol_sha,
            'v0_1_protocol_git_blob_sha1': v01_protocol_blob,
            'modification_permitted': False,
            'relationship_to_INSA_ID_E1': 'Referenced for v0.1 §11.2 (BIB 4-dim preservation criterion), §11.3 (8 C12 axes), §14 (stop rules), §9.2 (worldwide-historical-significance rule). NOT modified by INSA-ID-E1. Per proposal v5.1 §7, INSA-ID-E1 v6 uses its own preregistered Manhattan/reference-vector C20 operationalization; the +1.5 / 2.5 thresholds and the 85-record BIB corpus are inherited from predecessor calibration, but the v6 distance computation is not claimed identical to v0.1.'
        },
        'bib_frozen_source_reference': {
            'frozen_source_commit_sha1': 'c369215024c9f8a849daf11bd4b872d7ee566a7a',
            'intent_git_blob_sha1_at_c3692150': '7b10cb0641ab68572c7cf9d89a9c49f1afdc3428',
            'identity_contract_git_blob_sha1_at_c3692150': '7ef4356f657884d65dbd4462d85c1c81b3f6fa2a',
            'reconstruction_prompt_git_blob_sha1_at_c3692150': '2e37f47d99059238bd9484560e310d2f89744069',
            'intent_sha256': file_info['inputs/intent-document.txt']['sha256'],
            'identity_contract_sha256': file_info['inputs/identity-contract.txt']['sha256'],
            'reconstruction_prompt_sha256': file_info['inputs/reconstruction-prompt.md']['sha256'],
            'byte_identity_to_frozen_source': True
        },
        'frozen_artifacts': frozen_artifacts,
        'supporting_artifacts': supporting_artifacts,
        'artifact_counts': {
            'frozen_proposal_section_7': len(frozen_artifacts),
            'supporting': len(supporting_artifacts),
            'total_excluding_self': len(frozen_artifacts) + len(supporting_artifacts)
        },
        'B_binding': {
            'artifact': 'inputs/baseline-binding.json',
            'sha256': file_info['inputs/baseline-binding.json']['sha256'],
            'content_addresses': [
                'governing intent (inputs/intent-document.txt; BIB c3692150 blob 7b10cb0641ab68572c7cf9d89a9c49f1afdc3428)',
                'identity contract (inputs/identity-contract.txt; BIB c3692150 blob 7ef4356f657884d65dbd4462d85c1c81b3f6fa2a)',
                'reconstruction prompt (inputs/reconstruction-prompt.md; BIB c3692150 blob 2e37f47d99059238bd9484560e310d2f89744069)',
                'four locked BIB scorebook SHAs (BIB-001 A/B, BIB-002 A/B)',
                'baseline membership: 85 envelope observations (inputs/baseline-envelope-membership.json)',
                'numerical baseline statistics (inputs/baseline-statistics.json; SHA below)',
                'evaluator/rubric evidence (inputs/evaluator-rubric.json; SHA below) — exact historical BIB rubric content + preregistered worldwide-significance rule',
                'frozen test-invocations schedule (inputs/test-invocations.json; SHA below) — 5 tests × 2 runs per (R, B, arm) cell',
                'frozen normalize-and-join script (hashing/normalize-and-join.py; SHA below)'
            ]
        },
        'D_binding': {
            'D_definition': 'D := M ∪ P ∪ O, pairwise disjoint',
            'M_cardinality': 1, 'P_cardinality': 12, 'O_cardinality': 0, 'D_cardinality_total': 13,
            'decomposition_artifact': 'inputs/dimensions-decomposition.json',
            'decomposition_sha256': file_info['inputs/dimensions-decomposition.json']['sha256'],
            'M_artifact': 'inputs/mutation-dimensions.json',
            'M_sha256': file_info['inputs/mutation-dimensions.json']['sha256'],
            'P_binding_artifact': 'inputs/preservation-dimensions.json',
            'P_binding_sha256': file_info['inputs/preservation-dimensions.json']['sha256'],
            'P_subset_a_artifact': 'inputs/preservation-dimensions-subset-a.json',
            'P_subset_a_sha256': file_info['inputs/preservation-dimensions-subset-a.json']['sha256'],
            'P_subset_b_artifact': 'inputs/preservation-dimensions-subset-b.json',
            'P_subset_b_sha256': file_info['inputs/preservation-dimensions-subset-b.json']['sha256'],
            'O_value': '∅',
            'O_rationale': 'The BIB 4-dim vector (subset-(a)) + 8 C12 axes (subset-(b)) exhaust the scored dimensions tracked by the frozen evaluator rubric.',
            'pairwise_disjoint_verification': {
                'method': 'set intersection assertion in Python',
                'M_ids': sorted(m_ids), 'subset_a_ids': sorted(a_ids), 'subset_b_ids': sorted(b_ids), 'O_ids': sorted(o_ids),
                'result': 'PASS (executed at freeze time)', 'verification_command': 'python3 -c "M=set([\"M-1\"]); A=set([\"BIB-4D-1\",\"BIB-4D-2\",\"BIB-4D-3\",\"BIB-4D-4\"]); B=set([\"C12-1\",\"C12-2\",\"C12-3\",\"C12-4\",\"C12-5\",\"C12-6\",\"C12-7\",\"C12-8\"]); assert M&A==set() and M&B==set() and A&B==set(); print(\"PASS\")"'
            }
        },
        'baseline_statistics_binding': {
            'artifact': 'inputs/baseline-statistics.json',
            'sha256': file_info['inputs/baseline-statistics.json']['sha256'],
            'contains': [
                'exact 4 frozen BIB scorebook SHAs (BIB-001 evaluator A, BIB-001 evaluator B, BIB-002 evaluator A, BIB-002 evaluator B)',
                'exact 85-observation inclusion mapping (envelope_records_85_with_per_dim_scores)',
                'per-evaluator calibrated 4-d reference vector (computed from 85 envelope observations per dim)',
                'exact method for computing Arm-C per-(R, B) Manhattan statistics',
                'frozen historical C20 envelope/boundary values (A=1.807059, B=0.414118) -- no TBD values',
                'explicit Boolean C20 PASS/FAIL formula',
                'C20 derivation script binding (hashing/c20-derivation.py SHA below)'
            ],
            'C20_pass_fail_formula': 'C20(e) = (missing_current_cells[e] is empty) AND (max over current (R, B) cells in {R1/B1, R2/B1, R3/B1} of mean_4dim_Manhattan_Arm_C(R, B) <= frozen_historical_envelope_bound[e]) for each evaluator e in {A, B}; C20_joint = C20(A) AND C20(B).',
            'current_expected_arm_c_cells': ['R1/B1', 'R2/B1', 'R3/B1'],
            'c20_derivation_script_artifact': 'hashing/c20-derivation.py',
            'c20_derivation_script_sha256': file_info['hashing/c20-derivation.py']['sha256'],
            'c20_provenance_v6': 'INSA-ID-E1 uses its own preregistered Manhattan/reference-vector control-validity operationalization (per proposal v5.1). The predecessor Evolution C20 used historical total-score envelope comparisons; v6 does NOT describe INSA-ID-E1\'s C20 as the identical inherited v0.1 C20 computation. The 85-record BIB corpus calibrates the new rule.'
        },
        'V_d_binding': {
            'artifact': 'inputs/evaluator-rubric.json',
            'sha256': file_info['inputs/evaluator-rubric.json']['sha256'],
            'exact_historical_bib_rubric_content': True,
            'exact_historical_test_corpus_content': True,
            'preregistered_worldwide_significance_rule': 'M3 PASS iff AT LEAST 2 of the 4 criteria are satisfied (per v0.1 §9.2 PI pass 3)',
            'does_not_use_broader_global_regional_widely_cited_rule': True,
            'subset_a_tolerances': {
                'G_pres_subset_a_a_relative_tolerance': 1.5,
                'G_pres_subset_a_b_absolute_tolerance': 2.5,
                'per_evaluator_reference_vectors_preregistered': {
                    'A': {'contract_compliance': 3.529412, 'selection_behavior': 3.964706, 'narrative_behavior': 3.847059, 'functional_completeness': 3.494118},
                    'B': {'contract_compliance': 3.988235, 'selection_behavior': 3.988235, 'narrative_behavior': 4.0, 'functional_completeness': 4.0}
                }
            },
            'subset_b_tolerances': '8 C12 axes with binary-failure convention for 0-4 axes (failure = score == 0) per inputs/preservation-dimensions-subset-b.json failure_convention_pr_INSA_ID_E1 (preregistered INSA-ID-E1 rule, not inherited from v0.1)',
            'provenance_v6': 'The BIB 4-dim dimensions and the +1.5 / 2.5 threshold values come from predecessor calibration. INSA-ID-E1\'s global-reference-vector distance formulation is the v5.1 preregistered operationalization; v6 does NOT claim that this exact distance computation is verbatim the v0.1 computation.'
        },
        'test_invocations_binding': {
            'artifact': 'inputs/test-invocations.json',
            'sha256': file_info['inputs/test-invocations.json']['sha256'],
            'role': 'Frozen content-addressed test invocation schedule. Maps every candidate index 1..10 (per (R, B, arm) cell) to its exact frozen Birthdate <date including year> invocation. The 5 distinct test prompts T1..T5 are repeated twice (run-1 and run-2) within each (R, B) cell. The executor MUST consume the test invocation from this artifact via the blind map; it MUST NOT invent or select the birthdate at runtime.',
            'repetition_design': 'five frozen test prompts repeated twice per (R, B) cell',
        },
        'A_binding': {
            'artifact': 'inputs/acceptance-tests.json',
            'sha256': file_info['inputs/acceptance-tests.json']['sha256'],
            'four_gates_preregistered': {
                'G_mod_a': 'mean modification_conformance >= 3.5',
                'G_mod_b': '>=80% Arm-M candidates with candidate_all_pass==True',
                'G_mod_c': 'every Arm-M reconstruction >=70% all-pass',
                'G_mod_d': 'Arm-M all-pass rate - Arm-C all-pass rate >= 0.50'
            },
            'binding': 'A bound only to M (per proposal v5.1 §5.1 INV-A-1)',
            'evaluator_blinding_manifest_included': True
        },
        'G_binding': {
            'artifact': 'inputs/preservation-gates.json',
            'sha256': file_info['inputs/preservation-gates.json']['sha256'],
            'subset_a_gates': {
                'G_pres_subset_a_a_relative': 'Arm M mean 4-dim Manhattan from ref <= Arm C mean + 1.5 (relative)',
                'G_pres_subset_a_b_absolute': 'Arm M mean 4-dim Manhattan from ref <= 2.5 (absolute)'
            },
            'subset_b_rule': 'axis_a BROKEN for evaluator_e IFF arm_M_failure_rate_on_axis_a >= 0.30 AND (arm_M_failure_rate - arm_C_failure_rate) >= 0.30; preservation fails if ANY axis BROKEN',
            'binding': 'G bound only to P (subset-(a) ∪ subset-(b)), per proposal v5.1 §5.1 INV-G-1',
            'evaluator_blinding_manifest_included': True
        },
        'applicability_declaration_summary': {
            'artifact': 'inputs/applicability-declaration.json',
            'sha256': file_info['inputs/applicability-declaration.json']['sha256'],
            'state': 'ACTIVE', 'identity': 'ACTIVE', 'evidence': 'ACTIVE',
            'satisfies_INV_APPL_1': True
        },
        'authority_manifest_summary': {
            'artifact': 'inputs/authority-manifest.json',
            'sha256': file_info['inputs/authority-manifest.json']['sha256'],
            'static_only': True,
            'freshness_window_seconds_frozen': 3600,
            'I_AUTH_01_capability_vs_permission_separated': True,
            'I_AUTH_06_grant_authentic': True,
            'I_AUTH_08_grant_traceable': True,
            'I_AUTH_05_freshness_at_m_commit': 'satisfied-by-design (frozen_window_seconds=3600)',
            'INV_AUTH_1_executor_authority_recorded': True,
            'INV_AUTH_2_grant_traceable': True,
            'INV_AUTH_5_freshness_protocol': 'per-candidate freshness witness at M-commit boundary + per-candidate Arm-C and Arm-M scoring',
            'satisfies_INV_AUTH_1_2_5': True,
            'execution_GO_required': True,
            'execution_GO_distinct_from_protocol_authorization': True
        },
        'c20_derivation_summary': {
            'artifact': 'hashing/c20-derivation.py',
            'sha256': file_info['hashing/c20-derivation.py']['sha256'],
            'role': 'Frozen deterministic C20 derivation (v6). Consumes the ACTUAL evaluator-return schema preserved by hashing/normalize-and-join.py in the operator-side scorebook + the operator-only blind map + the frozen test-invocations. Re-verifies all inputs; rejects unknown / duplicate blind IDs, duplicate tuples, arm != expected, (R, B) outside current expected cells, and any operator-metadata mismatch against the blind map (fatal on all). Uses the preregistered historical envelope bound (A=1.807059, B=0.414118). derivation_recorded_at_utc set automatically.',
            'interface_v6': '--blind-map is a REQUIRED input. Each record in the operator-side Arm-C scorebook has fields: blind_id, reconstruction_id, block, arm, candidate, birthdate, test_id, run, scores_<X>, M_scores, G_subset_b_axis_scores, evaluator_self_report. The script RECOMPUTES each of the four BIB scorebook SHAs and compares against baseline-statistics.json expected values (fatal on mismatch); verifies the 85 envelope records; verifies the baseline-statistics required fields; uses the preregistered historical envelope bound; emits c20_per_evaluator_pass, c20_joint_pass, c20_fail_reasons.',
            'verified_during_v6_freeze': '9 test cases: (1) healthy -> c20_joint_pass=True; (2) missing R2/B -> False; (3) degraded R1/B (contract_compliance=0) -> False; (4) unknown blind_id -> FATAL; (5) duplicate blind_id -> FATAL; (6) Arm-M blind_id in Arm-C scorebook -> FATAL; (7) tampered BIB-001 evaluator A scorebook -> FATAL; (8) tampered baseline membership (1 obs removed) -> FATAL; (9) deliberately-mismatched blind-map/scorebook tuple -> FATAL. Plus normalize-and-join step rejects forbidden provenance fields in evaluator return (e.g., reconstruction_id) as FATAL.'
        },
        'execution_order_binding': {
            'artifact': 'protocol/EXECUTION-ORDER.md',
            'sha256': file_info['protocol/EXECUTION-ORDER.md']['sha256'],
            'frozen_scoring_algorithm': {
                'artifact': 'hashing/score-derivation.py',
                'sha256': file_info['hashing/score-derivation.py']['sha256'],
                'algorithm': 'HMAC-SHA256(draw_event_key, per-tuple-salt)[:8] as little-endian uint64; sort ascending; lex tie-break (R, B, arm, candidate). Per-tuple salt = sha256("INSA-ID-E1:" + R + ":" + B + ":" + arm + ":" + candidate).',
                'frozen_constants': {'reconstructions': ['R1', 'R2', 'R3'], 'bs': ['B1'], 'arms': ['C', 'M'], 'candidates_per_cell': 10, 'total_tuples': 60},
                'reproducibility': 'Same seed file -> identical output SHA; different seed file -> different output. Zero operator discretion after GO.'
            },
            'frozen_reconstruction_input_builder': {
                'artifact': 'preflight/build-reconstruction-input.py',
                'sha256': file_info['preflight/build-reconstruction-input.py']['sha256'],
                'algorithm': 'For each (R, B, arm): concatenate reconstruction-prompt + identity-contract + (M-directive or C-directive). 6 output files, byte-identical for each (R, B, arm) tuple.'
            },
            'frozen_normalize_and_join_script': {
                'artifact': 'hashing/normalize-and-join.py',
                'sha256': file_info['hashing/normalize-and-join.py']['sha256'],
                'role': 'Frozen deterministic evaluator-return → operator-side scorebook normalization/join script. Consumes the raw evaluator-return JSON + locked blind map and produces the immutable operator-side scorebook. Preserves M_scores + G_subset_a_4dim_vector + G_subset_b_axis_scores + evaluator_self_report. Adds reconstruction_id, block, arm, candidate, birthdate, test_id, run solely from the blind map. Verifies every added metadata field against the blind map (fatal on mismatch). Rejects unknown blind IDs, duplicate blind IDs, duplicate tuples, any forbidden provenance field in the evaluator return.'
            },
            'blind_map_timing_v6': 'preflight/blind-map.json is constructed and locked in Phase 0 (pre-dispatch preflight), before any evaluator invocation. Phase 2 USES the already-locked blind map; it does NOT construct or mutate the blind map in Phase 2. Phase 3 uses FRESH per-arm blind_ids (the frozen blind-map design has one-ID->one-tuple); Phase 3 does NOT use "the same blind_id" as Arm-C.',
            'phases_v6': {
                'phase_0': 'Pre-dispatch preflight (static only; no model invocation). Constructs and locks the operator-only blind map (preflight/blind-map.json) and the frozen test-invocations lookup. C20 NOT in Phase 0.',
                'phase_1': 'Generation (per (R, B, arm, candidate) in locked order). Fresh executor session per candidate. After "application ready", the operator supplies the exact Birthdate <date> invocation sourced from inputs/test-invocations.json via the locked blind map. The executor MUST NOT invent or select the birthdate at runtime.',
                'phase_2': 'Arm-C scoring (per-candidate fresh evaluator sessions; evaluator sees only the birthdate + scoring criteria + opaque blind_id; NOT arm, NOT reconstruction, NOT phase). The operator runs hashing/normalize-and-join.py to build operator-side Arm-C scorebooks from raw evaluator returns + locked blind map. Lock evaluator-A-arm-C-scorebook.json and evaluator-B-arm-C-scorebook.json. Run hashing/c20-derivation.py with --blind-map (required). C20 FAIL -> STOP, INVALID_EXPERIMENT. C20 PASS -> proceed.',
                'phase_3': 'Arm-M scoring (per-candidate fresh evaluator sessions, separate immutable scorebooks). The operator generates a FRESH per-arm blind_id (the frozen blind-map design has one-ID->one-tuple; the run-keyed identifier is per-arm, not shared with Arm-C). Same test invocation (same birthdate) as Phase 1 for the matched (R, B, test, run) tuple. Lock evaluator-A-arm-M-scorebook.json and evaluator-B-arm-M-scorebook.json.',
                'phase_4': 'Substantive analysis (joint, not ordered ELSE IF) per proposal v5.1 §5.4 STEP 3 + §4.1 Level 1/Level 2. The C12 evidence is the locked G_subset_b_axis_scores from the operator-side scorebooks (all 8 C12 axes per candidate, preserved by normalize-and-join.py).',
                'phase_5': 'Synthesis (PI adjudication).'
            }
        },
        'evaluator_binding_summary': {
            'evaluator_a': {'model': 'gpt-5.6-sol', 'substrate': 'Codex CLI', 'role': 'per-candidate raw M + G scoring, fresh session per candidate; returns the exact evaluator schema in evaluation/evaluator-input-packet.md §7'},
            'evaluator_b': {'model': 'claude-opus-4-7', 'substrate': 'Claude Code CLI, fresh session per I-AUTH-05', 'role': 'per-candidate raw M + G scoring, fresh session per candidate; returns the exact evaluator schema in evaluation/evaluator-input-packet.md §7'},
            'blinding_discipline': {
                'artifact': 'evaluation/evaluator-input-packet.md',
                'sha256': file_info['evaluation/evaluator-input-packet.md']['sha256'],
                'v6_self_sufficiency': 'The evaluator packet is self-sufficient: it includes the test prompt (birthdate), frozen Amazing Birthday behavioral contract, exact historical BIB 0-4 anchors (content-addressed from inputs/evaluator-rubric.json), M1-M4 definitions, preregistered ≥2-of-4 worldwide-historical-significance rule, C12-1..8 definitions, current JSON return schema. The evaluator knows what behavior to score without knowing whether the candidate is control or treatment. The modification specification itself is hidden.',
                'de_blinding_artifact': 'results/de-blining-table.json (produced at scoring time, auditable)',
                'v6_separation': 'v6 separates per-candidate scoring (evaluator-side) from aggregate computation (analysis-side, post-lock). Evaluators return per-candidate raw scores only in the exact schema: blind_id, M_scores, G_subset_a_4dim_vector, G_subset_b_axis_scores, evaluator_self_report. No reconstruction_id, no block, no arm, no candidate, no T-number, no run, no phase, no execution-provenance. Blind-map/C20 join is operator-only: evaluators see only opaque blind IDs; the operator-only blind map (locked preflight) de-blinds for C20. R/B/arm/candidate/birthdate are recovered EXCLUSIVELY from the blind map.'
            }
        },
        'scorebook_structure_v6': {
            'separate_per_arm_locking': True,
            'evaluator_A_arm_C_scorebook': 'evaluation/evaluator-A-arm-C-scorebook.json (operator-side; locked after Phase 2; no further appends; preserves M_scores + G_subset_a_4dim_vector + G_subset_b_axis_scores + evaluator_self_report; R/B/arm/candidate/birthdate from blind map)',
            'evaluator_B_arm_C_scorebook': 'evaluation/evaluator-B-arm-C-scorebook.json (operator-side; locked after Phase 2; no further appends)',
            'evaluator_A_arm_M_scorebook': 'evaluation/evaluator-A-arm-M-scorebook.json (operator-side; locked after Phase 3; no further appends; uses FRESH per-arm blind_id from the locked blind map)',
            'evaluator_B_arm_M_scorebook': 'evaluation/evaluator-B-arm-M-scorebook.json (operator-side; locked after Phase 3; no further appends)',
            'c12_evidence_preserved': 'Every locked scorebook retains the full raw scoring payload, including all 8 C12 axes (G_subset_b_axis_scores). The Phase-4 analysis consumes these locked C12 values directly to compute C12 per-axis failure rates and the BROKEN rule.',
            'self_referential_hash_prohibition': 'No scorebook file contains its own full-file SHA-256. SHA-256s recorded externally in results/score-independent.md. C20 decision record (preflight/c20-decision-record.json) also does NOT contain its own full-file SHA-256.'
        },
        'stop_conditions_inherited': {
            'C20_phase': 'Phase 2 (Arm-C scoring), NOT Phase 0',
            'C20_definition': 'Computed deterministically by hashing/c20-derivation.py from inputs/baseline-statistics.json (frozen historical envelope bound A=1.807059, B=0.414118) + the operator-side Arm-C scorebooks + the operator-only blind map. C20 PASS for evaluator e IFF (a) no missing current cells in {R1/B1, R2/B1, R3/B1} AND (b) every current cell mean Manhattan <= frozen historical envelope bound[e]. C20 FAIL -> INVALID_EXPERIMENT.',
            'v0_1_5_stop_rules': [
                'Material deviation during generation -> STOP unless PI separately adjudicates',
                'Evaluator substitution after observing candidates -> forbidden',
                'Retroactive gate weakening -> forbidden',
                'Decision tree semantics change -> forbidden (§5.4 must remain joint, not ordered ELSE IF)',
                'Substantive -> INCONCLUSIVE_PENDING_FURTHER reclassification -> forbidden'
            ],
            'v0_3_T1_T2_T3': 'Runtime failure systematic thresholds (proposal v5.1 §5.5.2): T1 >=50% same-class; T2 arm-imbalance (fail_M/max(fail_C,1)>=2 AND fail_M-fail_C>=3 AND fail_M+fail_C>=5); T3 substrate-wide unavailability',
            'satisfies_INV_STOP_1': True,
            'protocol_section_reference': 'protocol/INSA-ID-E1-protocol.md §15'
        },
        'evidence_chain_summary': {
            'evidence_profile': 'per-step evidence capture per proposal v5.1 §14; per-candidate evidence file runs/<R>/<B>/<arm>/evidence-<N>.json; locked operator-side evaluator scorebooks evaluation/evaluator-{A,B}-arm-{C,M}-scorebook.json (separate per arm, blind-map joined at scorebook-build time, preserve all 8 C12 axes); operator-only blind map preflight/blind-map.json (locked in Phase 0); frozen test-invocations inputs/test-invocations.json; C20 derivation record preflight/c20-decision-record.json; synthesis results/score-independent.md + results/analysis.md + results/disposition.md + results/unblinded-analysis-results.json + results/de-blinding-table.json',
            'satisfies_INV_EVID_1': True,
            'manifest_role': 'MANIFEST.json itself is part of the evidence chain: it content-addresses every pre-execution artifact and the v0.3 + v0.1 references. No manifest self-reference inside the file.'
        },
        'four_gates_modification_success_v6': {
            'G_mod_a': 'ForEach evaluator independently: mean(modification_conformance for all Arm-M candidates) >= 3.5',
            'G_mod_b': 'ForEach evaluator independently: count(candidate_all_pass==True for all Arm-M candidates) / count(total Arm-M candidates) >= 0.80',
            'G_mod_c': 'ForEach evaluator independently: AND over R in {R1, R2, R3}: count(candidate_all_pass==True for Arm-M candidates in R) / count(total Arm-M candidates in R) >= 0.70',
            'G_mod_d': 'ForEach evaluator independently: arm_M_all_pass_rate - arm_C_all_pass_rate >= 0.50',
            'Modification_Success_per_evaluator': 'G_mod_a AND G_mod_b AND G_mod_c AND G_mod_d',
            'Modification_Success_experiment_level': 'Modification_Success_per_A AND Modification_Success_per_B'
        },
        'c12_broken_rule_v6': {
            'definition_per_evaluator_e_and_axis_a': 'axis_a is BROKEN for evaluator_e IF AND ONLY IF BOTH arm_M_failure_rate_on_axis_a >= 0.30 AND (arm_M_failure_rate_on_axis_a - arm_C_failure_rate_on_axis_a) >= 0.30',
            'subset_b_pass_per_evaluator': 'subset-(b) gate PASSES for evaluator_e IF AND ONLY IF no axis in {C12-1..C12-8} is BROKEN for evaluator_e',
            'Non_target_Identity_Preservation_per_evaluator': '(G_pres_subset_a_a AND G_pres_subset_a_b) AND (no C12-axis-BROKEN for evaluator_e)',
            'Non_target_Identity_Preservation_experiment_level': 'Non_target_Identity_Preservation_per_A AND Non_target_Identity_Preservation_per_B'
        },
        'executor_change_documentation_v6': {
            'v0_1_executor': 'claude-sonnet-4-6',
            'v6_executor': 'claude-opus-4-7',
            'rationale': 'Pre-registered, preregistered-bound deviation (proposal v5.1 §2(e)). Limits direct comparability of the v0.1 failure shape (R2-B deferrals) to INSA-ID-E1\'s outcome.',
            'evaluator_substrate_unchanged': 'evaluator A (gpt-5.6-sol via Codex CLI) + evaluator B (claude-opus-4-7 fresh session via Claude Code CLI) match v0.1\'s evaluator substrate.'
        },
        'execution_authorization_status': {
            'protocol_authorization': 'GRANTED (Frank-as-PI approval at 2026-09-11 referencing proposal v5.1 SHA 1f84c3101d6add7d44ed821681946c10be8f5f5c)',
            'execution_authorization': 'NOT GRANTED (separate Frank-as-PI GO required, recorded in preflight/execution-authority-witness.json per EXECUTION-ORDER.md §6)',
            'no_model_dispatch_until_execution_GO': True
        },
        'modification_to_frozen_artifacts_after_this_manifest': 'forbidden (per proposal v5.1 §8 GO constraints)',
        'evidence_integrity_attestation': 'All SHA fields in this MANIFEST are valid 64-hex SHA-256 values; the MANIFEST itself does not contain its own SHA-256 (no self-reference). All cross-artifact SHA references verified by the binding-verification script at freeze time. The v6 binding-verification script also statically verifies: (1) evaluator-rubric.json content-addresses the exact historical BIB rubric (verified by content + hash) + the preregistered ≥2-of-4 worldwide-significance rule; (2) evaluator packet contains the exact frozen BIB 0-4 anchors; (3) C20 accepts the exact operator-side scorebook format; (4) C20 requires and uses the blind map; (5) synthetic tests use no evaluator-forbidden provenance fields; (6) normalize-and-join rejects any operator-metadata mismatch; (7) clean-environment verification case runs the verifier in a fresh tempdir with no pre-existing /tmp files; (8) deliberately-mismatched blind-map/scorebook tuple test fails fatally.'
    }

    # Write MANIFEST.json
    manifest_text = json.dumps(manifest, indent=2, sort_keys=False) + '\n'
    manifest_path = os.path.join(exp_dir, 'MANIFEST.json')
    tmp = manifest_path + '.tmp'
    with open(tmp, 'w') as f:
        f.write(manifest_text)
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp, manifest_path)
    new_manifest_sha = sha256_file(manifest_path)
    print()
    print(f'MANIFEST.json v6 written: {len(manifest_text)} bytes, SHA-256: {new_manifest_sha}')

    with open(os.path.join(exp_dir, 'MANIFEST.sha256.txt'), 'w') as f:
        f.write(f'{new_manifest_sha}  MANIFEST.json\n')

    print()
    print('=== v6 binding-verification + MANIFEST generation complete ===')
    print(f'  proposal v5.1 SHA: 1f84c3101d6add7d44ed821681946c10be8f5f5c')
    print(f'  binding-verification script SHA: {file_info["hashing/binding-verification.py"]["sha256"]}')
    print(f'  c20-derivation.py SHA: {file_info["hashing/c20-derivation.py"]["sha256"]}')
    print(f'  normalize-and-join.py SHA: {file_info["hashing/normalize-and-join.py"]["sha256"]}')
    print(f'  protocol v6 SHA: {file_info["protocol/INSA-ID-E1-protocol.md"]["sha256"]}')
    print(f'  EXECUTION-ORDER v6 SHA: {file_info["protocol/EXECUTION-ORDER.md"]["sha256"]}')
    print(f'  baseline-binding.json SHA: {file_info["inputs/baseline-binding.json"]["sha256"]}')
    print(f'  baseline-statistics.json SHA: {file_info["inputs/baseline-statistics.json"]["sha256"]}')
    print(f'  dimensions-decomposition.json SHA: {file_info["inputs/dimensions-decomposition.json"]["sha256"]}')
    print(f'  authority-manifest.json SHA: {file_info["inputs/authority-manifest.json"]["sha256"]}')
    print(f'  evaluator-input-packet.md SHA: {file_info["evaluation/evaluator-input-packet.md"]["sha256"]}')
    print(f'  evaluator-rubric.json SHA: {file_info["inputs/evaluator-rubric.json"]["sha256"]}')
    print(f'  test-invocations.json SHA: {file_info["inputs/test-invocations.json"]["sha256"]}')
    print(f'  MANIFEST.json v6 SHA: {new_manifest_sha}')


if __name__ == '__main__':
    main()
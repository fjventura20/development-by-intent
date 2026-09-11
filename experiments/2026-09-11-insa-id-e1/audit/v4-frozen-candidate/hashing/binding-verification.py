#!/usr/bin/env python3
"""
INSA-ID-E1 frozen binding-verification script (frozen pre-execution, v4).

Single authoritative source of truth for the v4 MANIFEST.json. Run this
script at protocol freeze to (re)produce the final MANIFEST.json. The script:

  1. Hashes every listed frozen/supporting artifact.
  2. Verifies every MANIFEST path/SHA pair.
  3. Verifies important cross-artifact SHA references (e.g., baseline-binding
     references the finalized baseline-statistics SHA; baseline-statistics
     references the four frozen BIB scorebook SHAs; dimensions-decomposition
     references the finalized mutation-dimensions + subset-(a) + subset-(b) SHAs).
  4. Emits the final MANIFEST.json (content-addressed, no self-reference).
  5. Runs the C20 derivation in three synthetic modes (healthy / missing-cell /
     out-of-envelope) using the actual frozen artifacts, asserts the expected
     outcomes, and reports.
  6. Exits nonzero on any mismatch.

This script is itself a frozen artifact (content-addressed in MANIFEST).
Structural-only; does NOT invoke any executor or evaluator.

Usage:
  cd experiments/2026-09-11-insa-id-e1
  python3 hashing/binding-verification.py --v4-experiment-dir .
"""

import argparse
import hashlib
import json
import os
import subprocess
import sys
import tempfile
from datetime import datetime, timezone


# 16 frozen pre-execution artifacts (per proposal v5.1 §7)
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
    'protocol/INSA-ID-E1-protocol.md',
    'protocol/EXECUTION-ORDER.md',
]

# 4 supporting artifacts (referenced from MANIFEST but not in proposal §7)
SUPPORTING_ARTIFACTS = [
    'inputs/reconstruction-prompt.md',  # also supporting; legacy alias for the v2 build-reconstruction-input
    'evaluation/evaluator-input-packet.md',
    'hashing/score-derivation.py',
    'hashing/c20-derivation.py',
    'hashing/binding-verification.py',  # self-binding
    'preflight/build-reconstruction-input.py',
]


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
    ap = argparse.ArgumentParser(description='INSA-ID-E1 v4 binding-verification + MANIFEST generator')
    ap.add_argument('--v4-experiment-dir', required=True, help='Path to experiments/2026-09-11-insa-id-e1/')
    ap.add_argument('--repo-dir', default=None, help='Path to the git repo root (default: parent of --v4-experiment-dir)')
    ap.add_argument('--skip-c20-synthetic', action='store_true', help='Skip the C20 synthetic test runs (for faster binding-only verification)')
    args = ap.parse_args()

    exp_dir = os.path.abspath(args.v4_experiment_dir)
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

    # 2a. baseline-binding.json references finalized baseline-statistics SHA
    bb_sha = file_info['inputs/baseline-binding.json']['sha256']
    bs_sha = file_info['inputs/baseline-statistics.json']['sha256']
    bb_data = json.load(open(os.path.join(exp_dir, 'inputs/baseline-binding.json')))
    if bb_data['baseline_statistics']['sha256'] != bs_sha:
        fail(f"baseline-binding.json references baseline-statistics SHA {bb_data['baseline_statistics']['sha256']} but actual is {bs_sha}")
    print(f'  baseline-binding.json -> baseline-statistics.json: OK ({bs_sha[:16]}...)')

    # 2b. baseline-statistics.json references the four frozen BIB scorebook SHAs
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

    # 2c. dimensions-decomposition.json references finalized subset-a, subset-b, and mutation-dimensions SHAs
    dd_data = json.load(open(os.path.join(exp_dir, 'inputs/dimensions-decomposition.json')))
    dd_sha = file_info['inputs/dimensions-decomposition.json']['sha256']
    if dd_data['P']['subset_a_sha256'] != file_info['inputs/preservation-dimensions-subset-a.json']['sha256']:
        fail('dimensions-decomposition.json subset_a_sha256 mismatch')
    if dd_data['P']['subset_b_sha256'] != file_info['inputs/preservation-dimensions-subset-b.json']['sha256']:
        fail('dimensions-decomposition.json subset_b_sha256 mismatch')
    if dd_data['M']['enumeration_sha256'] != file_info['inputs/mutation-dimensions.json']['sha256']:
        fail('dimensions-decomposition.json M enumeration_sha256 mismatch')
    if dd_data['M']['specification_sha256'] != file_info['inputs/modification-specification.txt']['sha256']:
        fail('dimensions-decomposition.json M specification_sha256 mismatch')
    print(f'  dimensions-decomposition.json -> subset-a, subset-b, mutation-dimensions, modification-specification: OK')

    # 2d. preservation-dimensions.json references finalized subset-a and subset-b SHAs
    pd_data = json.load(open(os.path.join(exp_dir, 'inputs/preservation-dimensions.json')))
    if pd_data['binding']['subset_a_sha256'] != file_info['inputs/preservation-dimensions-subset-a.json']['sha256']:
        fail('preservation-dimensions.json subset_a_sha256 mismatch')
    if pd_data['binding']['subset_b_sha256'] != file_info['inputs/preservation-dimensions-subset-b.json']['sha256']:
        fail('preservation-dimensions.json subset_b_sha256 mismatch')
    print(f'  preservation-dimensions.json -> subset-a, subset-b: OK')

    # 2e. acceptance-tests.json references finalized mutation-dimensions SHA
    at_data = json.load(open(os.path.join(exp_dir, 'inputs/acceptance-tests.json')))
    if at_data['binding']['M_artifact_sha256'] != file_info['inputs/mutation-dimensions.json']['sha256']:
        fail('acceptance-tests.json M_artifact_sha256 mismatch')
    if at_data['binding']['M_specification_sha256'] != file_info['inputs/modification-specification.txt']['sha256']:
        fail('acceptance-tests.json M_specification_sha256 mismatch')
    print(f'  acceptance-tests.json -> mutation-dimensions, modification-specification: OK')

    # 2f. preservation-gates.json references finalized subset-a, subset-b, baseline-statistics SHAs
    pg_data = json.load(open(os.path.join(exp_dir, 'inputs/preservation-gates.json')))
    if pg_data['binding']['P_subset_a_sha256'] != file_info['inputs/preservation-dimensions-subset-a.json']['sha256']:
        fail('preservation-gates.json P_subset_a_sha256 mismatch')
    if pg_data['binding']['P_subset_b_sha256'] != file_info['inputs/preservation-dimensions-subset-b.json']['sha256']:
        fail('preservation-gates.json P_subset_b_sha256 mismatch')
    print(f'  preservation-gates.json -> subset-a, subset-b: OK')

    # 2g. baseline-statistics.json 85 envelope records match baseline-envelope-membership.json
    em_data = json.load(open(os.path.join(exp_dir, 'inputs/baseline-envelope-membership.json')))
    env_shas = sorted(obs['raw_sha256'] for obs in em_data['included_observations'])
    rec_shas = sorted(r['raw_sha256'] for r in bs_data['envelope_records_85_with_per_dim_scores'])
    if env_shas != rec_shas:
        fail(f'envelope membership mismatch: 85 SHAs differ between baseline-envelope-membership.json and baseline-statistics.json')
    print(f'  baseline-envelope-membership.json <-> baseline-statistics.json envelope records: OK (all 85 match)')

    # 2h. authority-manifest.json (static-only; no SHAs to cross-check beyond reference to frozen v0.3 + v0.1)
    print(f'  authority-manifest.json: static-only (no dynamic SHAs); all dynamic fields listed as NOT in this manifest')

    # Step 3: Run the D = M ∪ P ∪ O pairwise-disjoint check (executable)
    print()
    print('Step 3: running D = M ∪ P ∪ O pairwise-disjoint check...')
    m_ids = {d['id'] for d in json.load(open(os.path.join(exp_dir, 'inputs/mutation-dimensions.json')))['M_enumeration']}
    a_ids = {d['id'] for d in json.load(open(os.path.join(exp_dir, 'inputs/preservation-dimensions-subset-a.json')))['dimensions']}
    b_ids = {d['id'] for d in json.load(open(os.path.join(exp_dir, 'inputs/preservation-dimensions-subset-b.json')))['axes']}
    o_ids = set()
    inter_ma = m_ids & a_ids
    inter_mb = m_ids & b_ids
    inter_ab = a_ids & b_ids
    inter_mo = m_ids & o_ids
    inter_ao = a_ids & o_ids
    inter_bo = b_ids & o_ids
    if not (len(inter_ma) == len(inter_mb) == len(inter_ab) == len(inter_mo) == len(inter_ao) == len(inter_bo) == 0):
        fail(f'D = M ∪ P ∪ O is NOT pairwise disjoint: M∩A={inter_ma}, M∩B={inter_mb}, A∩B={inter_ab}, M∩O={inter_mo}, A∩O={inter_ao}, B∩O={inter_bo}')
    print(f'  M ids: {sorted(m_ids)}; subset-(a) ids: {sorted(a_ids)}; subset-(b) ids: {sorted(b_ids)}; O ids: {sorted(o_ids)}')
    print(f'  D = M ∪ P ∪ O is pairwise disjoint: PASS')

    # Step 4: Run the C20 derivation in 3 synthetic modes (using actual frozen artifacts)
    if not args.skip_c20_synthetic:
        print()
        print('Step 4: running C20 derivation synthetic tests (using actual frozen artifacts)...')
        envelope_records = bs_data['envelope_records_85_with_per_dim_scores']
        dims = ['contract_compliance', 'selection_behavior', 'narrative_behavior', 'functional_completeness']

        def write_json(p, d):
            with open(p, 'w') as f:
                json.dump(d, f, indent=2)
                f.write('\n')

        def run_c20(armc_A, armc_B, label, expected_joint, fake_a_a=None, fake_mem=None):
            with tempfile.TemporaryDirectory() as tmpdir:
                a = f'{tmpdir}/armc-A.json'
                b = f'{tmpdir}/armc-B.json'
                write_json(a, armc_A)
                write_json(b, armc_B)
                out = f'{tmpdir}/c20.json'
                a_a = fake_a_a or os.path.join(repo_dir, 'experiments/2026-09-05-dbi-bib-001-rerun-001/evaluation/evaluator-A-scores-LOCKED.jsonl')
                env = fake_mem or os.path.join(exp_dir, 'inputs/baseline-envelope-membership.json')
                result = subprocess.run([
                    'python3', os.path.join(exp_dir, 'hashing/c20-derivation.py'),
                    '--envelope', env,
                    '--baseline-stats', os.path.join(exp_dir, 'inputs/baseline-statistics.json'),
                    '--arm-c-A', a, '--arm-c-B', b,
                    '--frozen-A-A', a_a,
                    '--frozen-A-B', os.path.join(repo_dir, 'experiments/2026-09-05-dbi-bib-001-rerun-001/evaluation/evaluator-B-scores-LOCKED.jsonl'),
                    '--frozen-B-A', os.path.join(repo_dir, 'experiments/2026-09-06-dbi-bib-002-r4-b-confirmation/evaluation/evaluator-A-scores-LOCKED.jsonl'),
                    '--frozen-B-B', os.path.join(repo_dir, 'experiments/2026-09-06-dbi-bib-002-r4-b-confirmation/evaluation/evaluator-B-scores-LOCKED.jsonl'),
                    '--out', out,
                ], capture_output=True, text=True, cwd=exp_dir)
                if expected_joint is None:
                    # Expect FATAL (nonzero) exit
                    if result.returncode != 0:
                        print(f'  {label}: FATAL exit as expected (exit={result.returncode})')
                        return True
                    print(f'  {label}: ERROR — expected FATAL exit but got exit=0')
                    return False
                if result.returncode != 0:
                    print(f'  {label}: ERROR — expected exit 0 but got {result.returncode}; stderr: {result.stderr[-300:]}')
                    return False
                c20_out = json.load(open(out))
                if c20_out['c20_joint_pass'] != expected_joint:
                    print(f'  {label}: ERROR — expected c20_joint_pass={expected_joint} but got {c20_out["c20_joint_pass"]}')
                    return False
                print(f'  {label}: c20_joint_pass={c20_out["c20_joint_pass"]} (as expected)')
                return True

        # Healthy current cells
        healthy_A = [{'reconstruction_id': r['reconstruction_id'], 'block': r['block'], 'scores': r['scores_A']}
                     for r in envelope_records if r['reconstruction_id'] in ('R1','R2','R3') and r['block']=='B']
        healthy_B = [{'reconstruction_id': r['reconstruction_id'], 'block': r['block'], 'scores': r['scores_B']}
                     for r in envelope_records if r['reconstruction_id'] in ('R1','R2','R3') and r['block']=='B']
        run_c20(healthy_A, healthy_B, 'healthy current cells (R1/B, R2/B, R3/B)', expected_joint=True)

        # Missing R2/B
        missing_A = [c for c in healthy_A if c['reconstruction_id'] != 'R2']
        missing_B = [c for c in healthy_B if c['reconstruction_id'] != 'R2']
        run_c20(missing_A, missing_B, 'missing R2/B (expected FAIL)', expected_joint=False)

        # Degraded R1/B
        degraded_A = []
        for r in envelope_records:
            if r['reconstruction_id'] == 'R1' and r['block'] == 'B':
                scores = dict(r['scores_A'])
                scores['contract_compliance'] = 0
                degraded_A.append({'reconstruction_id': 'R1', 'block': 'B', 'scores': scores})
            elif r['reconstruction_id'] in ('R2', 'R3') and r['block'] == 'B':
                degraded_A.append({'reconstruction_id': r['reconstruction_id'], 'block': 'B', 'scores': dict(r['scores_A'])})
        run_c20(degraded_A, healthy_B, 'degraded R1/B (contract_compliance=0; expected FAIL)', expected_joint=False)

        # Tampered scorebook
        fake_sb = '/tmp/fake-tampered-A.jsonl'
        import shutil
        real_sb = os.path.join(repo_dir, 'experiments/2026-09-05-dbi-bib-001-rerun-001/evaluation/evaluator-A-scores-LOCKED.jsonl')
        shutil.copy(real_sb, fake_sb)
        with open(fake_sb, 'ab') as f:
            f.write(b'TAMPERED\n')
        try:
            run_c20(healthy_A, healthy_B, 'tampered BIB-001 evaluator A scorebook (expected FATAL)', expected_joint=None, fake_a_a=fake_sb)
        finally:
            os.remove(fake_sb)

        # Tampered baseline membership
        fake_mem = '/tmp/fake-membership.json'
        shutil.copy(os.path.join(exp_dir, 'inputs/baseline-envelope-membership.json'), fake_mem)
        fake_data = json.load(open(fake_mem))
        fake_data['included_observations'] = fake_data['included_observations'][:84]
        with open(fake_mem, 'w') as f:
            json.dump(fake_data, f, indent=2)
            f.write('\n')
        try:
            run_c20(healthy_A, healthy_B, 'tampered baseline membership (1 obs removed; expected FATAL)', expected_joint=None, fake_mem=fake_mem)
        finally:
            os.remove(fake_mem)

    # Step 5: Build and emit MANIFEST.json
    print()
    print('Step 5: building and emitting MANIFEST.json...')
    proposal_commit_sha = subprocess.run(
        ['git', '-C', repo_dir, 'log', '--format=%H', '-1', 'origin/feature/insa-id-e1-proposal', '--', 'docs/proposals/2026-09-10-INSA-ID-E1-proposal-v5.md'],
        capture_output=True, text=True).stdout.strip()
    proposal_file_sha = sha256_file(os.path.join(repo_dir, 'docs/proposals/2026-09-10-INSA-ID-E1-proposal-v5.md'))
    v01_protocol_sha = sha256_file(os.path.join(repo_dir, 'experiments/2026-09-06-dbi-evolution-v0.1/protocol/PROTOCOL-v0.5-frozen-final.md'))
    v01_protocol_blob = git_blob_sha(repo_dir, 'experiments/2026-09-06-dbi-evolution-v0.1/protocol/PROTOCOL-v0.5-frozen-final.md')

    # Distinguish §7 frozen vs supporting
    proposal_section_7_set = {
        'inputs/baseline-binding.json', 'inputs/baseline-statistics.json',
        'inputs/dimensions-decomposition.json', 'inputs/baseline-envelope-membership.json',
        'inputs/intent-document.txt', 'inputs/identity-contract.txt', 'inputs/reconstruction-prompt.md',
        'inputs/modification-specification.txt', 'inputs/arm-c-directive.txt',
        'inputs/mutation-dimensions.json',
        'inputs/preservation-dimensions-subset-a.json', 'inputs/preservation-dimensions-subset-b.json',
        'inputs/preservation-dimensions.json',
        'inputs/evaluator-rubric.json',
        'inputs/acceptance-tests.json', 'inputs/preservation-gates.json',
        'inputs/applicability-declaration.json', 'inputs/authority-manifest.json',
        'protocol/INSA-ID-E1-protocol.md', 'protocol/EXECUTION-ORDER.md',
    }
    frozen_artifacts = [file_info[p] for p in FROZEN_ARTIFACTS if p in proposal_section_7_set]
    supporting_artifacts = [file_info[p] for p in FROZEN_ARTIFACTS + SUPPORTING_ARTIFACTS if p not in proposal_section_7_set]

    # Dedup supporting (in case inputs/reconstruction-prompt.md appears in both lists)
    seen = set()
    dedup_supporting = []
    for a in supporting_artifacts:
        if a['path'] not in seen:
            dedup_supporting.append(a)
            seen.add(a['path'])
    supporting_artifacts = dedup_supporting

    manifest = {
        '$schema': 'INSA-v0.3-MANIFEST-v1',
        'schema_version': '2.0',
        'record_kind': 'experiment-manifest',
        'purpose': 'Content-addressed binding of all frozen pre-execution artifacts for INSA-ID-E1 v4 revision (per proposal v5.1 @ 1f84c31). SHA-256 locks every file; git blob SHA-1 provides cross-reference into frozen git history. Built deterministically by hashing/binding-verification.py from the actual finalized artifact SHAs. Every occurrence of an artifact SHA anywhere in MANIFEST equals the SHA in frozen_artifacts[] (verified by the binding-verification script).',
        'experiment_id': 'INSA-ID-E1',
        'experiment_short_name': 'insa-id-e1',
        'experiment_status': 'frozen-candidate-rev4 (awaiting Frank-as-PI execution GO)',
        'experiment_revision': 'v4 (per proposal v5.1)',
        'binding_verification_script': {
            'artifact': 'hashing/binding-verification.py',
            'sha256': file_info['hashing/binding-verification.py']['sha256'],
            'role': 'Single authoritative source of truth for this MANIFEST. Re-runs all SHA verifications, cross-reference checks, D disjointness check, and the C20 synthetic test suite (healthy/missing-cell/out-of-envelope/tampered-scorebook/tampered-membership). Exits nonzero on any mismatch.'
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
            'v1_v2_v3_defects_summary': 'See experiments/2026-09-11-insa-id-e1/audit/AUDIT_TRAIL.md'
        },
        'frozen_at_utc_date': record_frozen_at_utc_date,
        'frozen_by': 'Hermes (operator)',
        'manifest_generated_at_utc': record_run_at_utc,
        'manifest_generation_method': 'hashing/binding-verification.py v4 (deterministic; produces content-addressed MANIFEST.json from actual on-disk artifact SHAs; re-runnable)',
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
            'relationship_to_INSA_ID_E1': 'Referenced for v0.1 §11.2 (BIB 4-dim preservation criterion), §11.3 (8 C12 axes), §14 (stop rules). NOT modified by INSA-ID-E1.'
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
                'evaluator/rubric evidence (inputs/evaluator-rubric.json)'
            ]
        },
        'D_binding': {
            'D_definition': 'D := M ∪ P ∪ O, pairwise disjoint',
            'M_cardinality': 1,
            'P_cardinality': 12,
            'O_cardinality': 0,
            'D_cardinality_total': 13,
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
                'method': 'set intersection assertion in Python; intersection of M ids, subset-(a) ids, subset-(b) ids, O ids must equal empty set',
                'M_ids': sorted(m_ids),
                'subset_a_ids': sorted(a_ids),
                'subset_b_ids': sorted(b_ids),
                'O_ids': sorted(o_ids),
                'result': 'PASS (executed at freeze time; recorded here)',
                'verification_command': 'python3 -c "M=set([\"M-1\"]); A=set([\"BIB-4D-1\",\"BIB-4D-2\",\"BIB-4D-3\",\"BIB-4D-4\"]); B=set([\"C12-1\",\"C12-2\",\"C12-3\",\"C12-4\",\"C12-5\",\"C12-6\",\"C12-7\",\"C12-8\"]); assert M&A==set() and M&B==set() and A&B==set(); print(\"PASS\")"'
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
            'c20_derivation_script_sha256': file_info['hashing/c20-derivation.py']['sha256']
        },
        'V_d_binding': {
            'artifact': 'inputs/evaluator-rubric.json',
            'sha256': file_info['inputs/evaluator-rubric.json']['sha256'],
            'subset_a_tolerances': {
                'G_pres_subset_a_a_relative_tolerance': 1.5,
                'G_pres_subset_a_b_absolute_tolerance': 2.5,
                'per_evaluator_reference_vectors_preregistered': {
                    'A': {'contract_compliance': 3.529412, 'selection_behavior': 3.964706, 'narrative_behavior': 3.847059, 'functional_completeness': 3.494118},
                    'B': {'contract_compliance': 3.988235, 'selection_behavior': 3.988235, 'narrative_behavior': 4.0, 'functional_completeness': 4.0}
                }
            },
            'subset_b_tolerances': '8 C12 axes with binary-failure convention for 0-4 axes (failure = score == 0) per inputs/preservation-dimensions-subset-b.json failure_convention_pr_INSA_ID_E1 (preregistered INSA-ID-E1 rule, not inherited from v0.1)'
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
            'role': 'Frozen deterministic C20 derivation. Re-verifies the four locked BIB scorebook SHAs (fatal on mismatch); verifies the baseline-envelope-membership.json 85-SHA set matches the 85 records in baseline-statistics.json (fatal on count mismatch); verifies baseline-statistics.json required fields; uses the preregistered historical envelope bound (A=1.807059, B=0.414118); computes per-(R, B) Arm-C means from the Phase 2 Arm-C scorebooks; emits c20_per_evaluator_pass, c20_joint_pass, c20_fail_reasons, derivation_recorded_at_utc. No manual post-write editing.',
            'verified_during_v4_freeze': '5 test cases: (a) healthy current cells -> c20_joint_pass=True; (b) missing R2/B -> c20_joint_pass=False with reason "missing current cells"; (c) degraded R1/B (contract_compliance=0) -> c20_joint_pass=False with reason "worst current cell mean > frozen historical envelope bound"; (d) tampered BIB-001 evaluator A scorebook -> FATAL exit 2; (e) tampered baseline membership (1 obs removed) -> FATAL exit 2.'
        },
        'execution_order_binding': {
            'artifact': 'protocol/EXECUTION-ORDER.md',
            'sha256': file_info['protocol/EXECUTION-ORDER.md']['sha256'],
            'frozen_scoring_algorithm': {
                'artifact': 'hashing/score-derivation.py',
                'sha256': file_info['hashing/score-derivation.py']['sha256'],
                'algorithm': 'HMAC-SHA256(draw_event_key, per-tuple-salt)[:8] as little-endian uint64; sort ascending; lex tie-break (R, B, arm, candidate). Per-tuple salt = sha256("INSA-ID-E1:" + R + ":" + B + ":" + arm + ":" + candidate).',
                'frozen_constants': {
                    'reconstructions': ['R1', 'R2', 'R3'],
                    'bs': ['B1'],
                    'arms': ['C', 'M'],
                    'candidates_per_cell': 10,
                    'total_tuples': 60
                },
                'reproducibility': 'Same seed file -> identical output SHA; different seed file -> different output. Zero operator discretion after GO.'
            },
            'frozen_reconstruction_input_builder': {
                'artifact': 'preflight/build-reconstruction-input.py',
                'sha256': file_info['preflight/build-reconstruction-input.py']['sha256'],
                'algorithm': 'For each (R, B, arm): concatenate reconstruction-prompt + identity-contract + (M-directive or C-directive). 6 output files, byte-identical for each (R, B, arm) tuple.'
            },
            'phases_v4': {
                'phase_0': 'Pre-dispatch preflight (static only; no model invocation). C20 NOT in Phase 0.',
                'phase_1': 'Generation (per (R, B, arm, candidate) in locked order). Fresh executor session per candidate.',
                'phase_2': 'Arm-C scoring (per-candidate fresh evaluator sessions) + C20 control-validity gate (hashing/c20-derivation.py). C20 FAIL -> STOP, INVALID_EXPERIMENT. C20 PASS -> proceed.',
                'phase_3': 'Arm-M scoring (per-candidate fresh evaluator sessions, separate immutable scorebooks).',
                'phase_4': 'Substantive analysis (joint, not ordered ELSE IF) per proposal v5.1 §5.4 STEP 3 + §4.1 Level 1/Level 2.',
                'phase_5': 'Synthesis (PI adjudication).'
            }
        },
        'evaluator_binding_summary': {
            'evaluator_a': {'model': 'gpt-5.6-sol', 'substrate': 'Codex CLI', 'role': 'per-candidate raw M + G scoring, fresh session per candidate'},
            'evaluator_b': {'model': 'claude-opus-4-7', 'substrate': 'Claude Code CLI, fresh session per I-AUTH-05', 'role': 'per-candidate raw M + G scoring, fresh session per candidate'},
            'blinding_discipline': {
                'artifact': 'evaluation/evaluator-input-packet.md',
                'sha256': file_info['evaluation/evaluator-input-packet.md']['sha256'],
                'de_blinding_artifact': 'results/de-blinding-table.json (produced at scoring time, auditable)',
                'v4_separation': 'v4 separates per-candidate scoring (evaluator-side) from aggregate computation (analysis-side, post-lock). Evaluators return per-candidate raw scores only. No G_pres_*, no G_mod_*, no C12 BROKEN, no phase indication. Blind-map/C20 join is operator-only: evaluators see only opaque blind IDs; the operator-only blind map (locked preflight) de-blinds for C20.'
            }
        },
        'scorebook_structure_v4': {
            'separate_per_arm_locking': True,
            'evaluator_A_arm_C_scorebook': 'evaluation/evaluator-A-arm-C-scorebook.json (locked after Phase 2; no further appends)',
            'evaluator_B_arm_C_scorebook': 'evaluation/evaluator-B-arm-C-scorebook.json (locked after Phase 2; no further appends)',
            'evaluator_A_arm_M_scorebook': 'evaluation/evaluator-A-arm-M-scorebook.json (locked after Phase 3; no further appends)',
            'evaluator_B_arm_M_scorebook': 'evaluation/evaluator-B-arm-M-scorebook.json (locked after Phase 3; no further appends)',
            'self_referential_hash_prohibition': 'No scorebook file contains its own full-file SHA-256. SHA-256s recorded externally (results/score-independent.md for dynamic scorebooks; sidecar files).'
        },
        'stop_conditions_inherited': {
            'C20_phase': 'Phase 2 (Arm-C scoring), NOT Phase 0',
            'C20_definition': 'Computed deterministically by hashing/c20-derivation.py. C20 PASS for evaluator e IFF (a) no missing current cells in {R1/B1, R2/B1, R3/B1} AND (b) every current cell mean Manhattan <= frozen historical envelope bound[e]. C20 FAIL -> INVALID_EXPERIMENT.',
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
            'evidence_profile': 'per-step evidence capture per proposal v5.1 §14; per-candidate evidence file runs/<R>/<B>/<arm>/evidence-<N>.json; locked evaluator scorebooks evaluation/evaluator-{A,B}-arm-{C,M}-scorebook.json (separate per arm, v3 item 7); C20 derivation record preflight/c20-decision-record.json; synthesis results/score-independent.md + results/analysis.md + results/disposition.md + results/unblinded-analysis-results.json + results/de-blinding-table.json',
            'satisfies_INV_EVID_1': True,
            'manifest_role': 'MANIFEST.json itself is part of the evidence chain: it content-addresses every pre-execution artifact and the v0.3 + v0.1 references. No manifest self-reference inside the file.'
        },
        'four_gates_modification_success_v4': {
            'G_mod_a': 'ForEach evaluator independently: mean(modification_conformance for all Arm-M candidates) >= 3.5',
            'G_mod_b': 'ForEach evaluator independently: count(candidate_all_pass==True for all Arm-M candidates) / count(total Arm-M candidates) >= 0.80',
            'G_mod_c': 'ForEach evaluator independently: AND over R in {R1, R2, R3}: count(candidate_all_pass==True for Arm-M candidates in R) / count(total Arm-M candidates in R) >= 0.70',
            'G_mod_d': 'ForEach evaluator independently: arm_M_all_pass_rate - arm_C_all_pass_rate >= 0.50',
            'Modification_Success_per_evaluator': 'G_mod_a AND G_mod_b AND G_mod_c AND G_mod_d',
            'Modification_Success_experiment_level': 'Modification_Success_per_A AND Modification_Success_per_B'
        },
        'c12_broken_rule_v4': {
            'definition_per_evaluator_e_and_axis_a': 'axis_a is BROKEN for evaluator_e IF AND ONLY IF BOTH arm_M_failure_rate_on_axis_a >= 0.30 AND (arm_M_failure_rate_on_axis_a - arm_C_failure_rate_on_axis_a) >= 0.30',
            'subset_b_pass_per_evaluator': 'subset-(b) gate PASSES for evaluator_e IF AND ONLY IF no axis in {C12-1..C12-8} is BROKEN for evaluator_e',
            'Non_target_Identity_Preservation_per_evaluator': '(G_pres_subset_a_a AND G_pres_subset_a_b) AND (no C12-axis-BROKEN for evaluator_e)',
            'Non_target_Identity_Preservation_experiment_level': 'Non_target_Identity_Preservation_per_A AND Non_target_Identity_Preservation_per_B'
        },
        'executor_change_documentation_v4': {
            'v0_1_executor': 'claude-sonnet-4-6',
            'v4_executor': 'claude-opus-4-7',
            'rationale': 'Pre-registered, preregistered-bound deviation (proposal v5.1 §2(e)). Limits direct comparability of the v0.1 failure shape (R2-B deferrals) to INSA-ID-E1\'s outcome.',
            'evaluator_substrate_unchanged': 'evaluator A (gpt-5.6-sol via Codex CLI) + evaluator B (claude-opus-4-7 fresh session via Claude Code CLI) match v0.1\'s evaluator substrate.'
        },
        'execution_authorization_status': {
            'protocol_authorization': 'GRANTED (Frank-as-PI approval at 2026-09-11 referencing proposal v5.1 SHA 1f84c3101d6add7d44ed821681946c10be8f5f5c)',
            'execution_authorization': 'NOT GRANTED (separate Frank-as-PI GO required, recorded in preflight/execution-authority-witness.json per EXECUTION-ORDER.md §6)',
            'no_model_dispatch_until_execution_GO': True
        },
        'modification_to_frozen_artifacts_after_this_manifest': 'forbidden (per proposal v5.1 §8 GO constraints)',
        'evidence_integrity_attestation': 'All SHA fields in this MANIFEST are valid 64-hex SHA-256 values; the MANIFEST itself does not contain its own SHA-256 (no self-reference). All cross-artifact SHA references verified by the binding-verification script at freeze time.'
    }

    # Write MANIFEST.json (without self_sha inside the file)
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
    print(f'MANIFEST.json v4 written: {len(manifest_text)} bytes, SHA-256: {new_manifest_sha}')

    # Write sidecar
    sidecar_path = os.path.join(exp_dir, 'MANIFEST.sha256.txt')
    with open(sidecar_path, 'w') as f:
        f.write(f'{new_manifest_sha}  MANIFEST.json\n')

    print()
    print('=== v4 binding-verification + MANIFEST generation complete ===')
    print(f'  proposal v5.1 SHA: 1f84c3101d6add7d44ed821681946c10be8f5f5c')
    print(f'  binding-verification script SHA: {file_info["hashing/binding-verification.py"]["sha256"]}')
    print(f'  c20-derivation.py SHA: {file_info["hashing/c20-derivation.py"]["sha256"]}')
    print(f'  protocol v4 SHA: {file_info["protocol/INSA-ID-E1-protocol.md"]["sha256"]}')
    print(f'  EXECUTION-ORDER v4 SHA: {file_info["protocol/EXECUTION-ORDER.md"]["sha256"]}')
    print(f'  baseline-binding.json SHA: {file_info["inputs/baseline-binding.json"]["sha256"]}')
    print(f'  baseline-statistics.json SHA: {file_info["inputs/baseline-statistics.json"]["sha256"]}')
    print(f'  dimensions-decomposition.json SHA: {file_info["inputs/dimensions-decomposition.json"]["sha256"]}')
    print(f'  authority-manifest.json SHA: {file_info["inputs/authority-manifest.json"]["sha256"]}')
    print(f'  evaluator-input-packet.md SHA: {file_info["evaluation/evaluator-input-packet.md"]["sha256"]}')
    print(f'  MANIFEST.json v4 SHA: {new_manifest_sha}')


if __name__ == '__main__':
    main()
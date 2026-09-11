#!/usr/bin/env python3
"""
INSA-ID-E1 v6.2 frozen blind-map builder/validator.

Deterministic tool that produces/validates the complete 60-entry blind map
for INSA-ID-E1. Given the frozen execution-order tuple universe, the
frozen test-invocations, the requested arm (or both arms), and the
candidate number, it builds the 60-entry blind map and validates that:

  - exactly 60 unique blind IDs (when both arms are requested)
  - exactly 60 unique (R, B, arm, candidate) tuples
  - exactly 30 C + 30 M
  - exactly 10 candidates per (R, B, arm) cell
  - candidate -> test/run/birthdate exactly matches test-invocations.json
  - no missing or extra execution-order tuple

Blind IDs themselves are CSPRNG-generated opaque tokens (at least 128 bits).
The tuple mapping is deterministic/non-discretionary; only the identifier
bytes are random. The completed map is generated once in Phase 0 and then
locked; no blind ID may be created, replaced, or modified after lock.

Visible blind IDs contain no reconstruction, block, arm, candidate, test, run,
or birthdate information. Random digits in an opaque token are not metadata
and do not encode a candidate number.

Phase 0 of the v6.2 protocol must use this tool to produce the locked
blind map. No blind ID may be created, replaced, or modified after Phase 0.
"""

import argparse
import hashlib
import json
import os
import re
import secrets
import sys


FROZEN_RECONSTRUCTIONS = ('R1', 'R2', 'R3')
FROZEN_BS = ('B1',)
FROZEN_ARMS = ('C', 'M')
FROZEN_CANDIDATES_PER_CELL = 10  # 1..10

# Map (cell_index 1..10) -> (test_id, run) - the frozen mapping per v6.2
CANDIDATE_TO_TEST_RUN = {
    1: ('T1', 1), 2: ('T1', 2),
    3: ('T2', 1), 4: ('T2', 2),
    5: ('T3', 1), 6: ('T3', 2),
    7: ('T4', 1), 8: ('T4', 2),
    9: ('T5', 1), 10: ('T5', 2),
}


def fail(msg):
    print(f'FATAL: {msg}', file=sys.stderr)
    sys.exit(2)


def build_complete_blind_map(test_invocations_path):
    """Build the complete 60-entry blind map.

    The tuple mapping is deterministic from the frozen test-invocations and
    execution universe. Each visible blind ID is generated with the OS CSPRNG
    (secrets.token_urlsafe(16), >=128 bits) and contains no tuple metadata.
    """
    with open(test_invocations_path) as f:
        ti = json.load(f)
    # Validate the test-invocations artifact: exactly 10 entries per (R, B) cell
    # enumerated (no shorthand), exactly matching the CANDIDATE_TO_TEST_RUN map.
    for R in FROZEN_RECONSTRUCTIONS:
        for B in FROZEN_BS:
            key = f'{R}/{B}'
            if key not in ti['cell_layout']:
                fail(f'test-invocations.json missing cell_layout for {key}')
            layout = ti['cell_layout'][key]
            if not isinstance(layout, list) or len(layout) != FROZEN_CANDIDATES_PER_CELL:
                fail(f'test-invocations.json {key} layout not a list of exactly 10 candidates')
            for entry in layout:
                for k in ('candidate', 'test_id', 'run', 'invocation'):
                    if k not in entry:
                        fail(f'test-invocations.json {key} entry missing {k!r}: {entry}')
                expected_test, expected_run = CANDIDATE_TO_TEST_RUN[entry['candidate']]
                if entry['test_id'] != expected_test or entry['run'] != expected_run:
                    fail(f'test-invocations.json {key} candidate {entry["candidate"]} has test_id={entry["test_id"]} run={entry["run"]}; expected {expected_test} run {expected_run}')
                if entry['invocation'] != ti['frozen_test_corpus']['tests'][expected_test]:
                    fail(f'test-invocations.json {key} candidate {entry["candidate"]} invocation {entry["invocation"]!r} does not match frozen test corpus for {expected_test}')

    # Build the 60-entry blind map deterministically
    # Generate a CSPRNG opaque ID per frozen tuple. The tuple mapping is
    # deterministic; only the visible identifier is random. IDs are generated
    # exactly once by the Phase-0 run and then locked.
    used_ids = set()
    forbidden_markers = [
        'r1', 'r2', 'r3', 'b1', '-c-', '-m-', '_c_', '_m_',
        't1', 't2', 't3', 't4', 't5', 'run1', 'run2',
        'february', 'june', 'november', 'august',
        '1952', '1956', '1960', '1989', '1931',
    ]
    def opaque_id_ok(candidate):
        lowered = candidate.lower()
        token = candidate[len('blind-'):] if candidate.startswith('blind-') else candidate
        if not candidate.startswith('blind-') or len(token) < 22:
            return False
        if any(marker in lowered for marker in forbidden_markers):
            return False
        if re.search(r'(?:^|[-_])(?:c|m)(?:[-_]|$)', lowered):
            return False
        return True

    def blind_id():
        while True:
            candidate = 'blind-' + secrets.token_urlsafe(16)
            if candidate not in used_ids and opaque_id_ok(candidate):
                used_ids.add(candidate)
                return candidate

    entries = []
    for R in FROZEN_RECONSTRUCTIONS:
        for B in FROZEN_BS:
            for arm in FROZEN_ARMS:
                for cand in range(1, FROZEN_CANDIDATES_PER_CELL + 1):
                    test_id, run = CANDIDATE_TO_TEST_RUN[cand]
                    bid = blind_id()
                    entries.append({
                        "reconstruction_id": R,
                        "block": B,
                        "arm": arm,
                        "candidate": cand,
                        "blind_id": bid,
                        "test_id": test_id,
                        "run": run,
                        "birthdate": ti['frozen_test_corpus']['tests'][test_id],
                    })
    return entries, ti


def validate_blind_map(entries, test_invocations):
    """Validate the complete 60-entry blind map against the v6.2 invariants."""
    # 1. Exactly 60 entries
    if len(entries) != 60:
        fail(f'blind map has {len(entries)} entries; expected exactly 60')

    # 2. Exactly 60 unique blind IDs
    bid_set = {e['blind_id'] for e in entries}
    if len(bid_set) != 60:
        fail(f'blind map has {len(bid_set)} unique blind IDs; expected exactly 60 (found {60 - len(bid_set)} duplicates)')

    # 3. Exactly 60 unique (R, B, arm, candidate) tuples
    tup_set = {(e['reconstruction_id'], e['block'], e['arm'], e['candidate']) for e in entries}
    if len(tup_set) != 60:
        fail(f'blind map has {len(tup_set)} unique (R, B, arm, candidate) tuples; expected exactly 60 (found {60 - len(tup_set)} duplicates)')

    # 2b. Visible blind IDs must be genuinely opaque: no tuple, arm, test,
    # run, candidate, or birthdate information. CSPRNG tokens are allowed to
    # contain random digits; the test is for explicit recognizable markers.
    forbidden_markers = [
        'R1', 'R2', 'R3', 'B1', '-C-', '-M-', '_C_', '_M_',
        'T1', 'T2', 'T3', 'T4', 'T5', 'run1', 'run2',
        'february', 'june', 'november', 'august',
        '1952', '1956', '1960', '1989', '1931',
    ]
    for bid in bid_set:
        lowered = bid.lower()
        if not bid.startswith('blind-'):
            fail(f'blind ID {bid!r} must use the blind- prefix')
        token = bid[len('blind-'):]
        if len(token) < 22:
            fail(f'blind ID {bid!r} token is shorter than 128 bits of URL-safe entropy')
        for marker in forbidden_markers:
            if marker.lower() in lowered:
                fail(f'blind ID {bid!r} visibly contains forbidden tuple/arm/test/run/birthdate marker {marker!r}')
    if any(re.search(r'(?:^|[-_])(?:C|M)(?:[-_]|$)', bid) for bid in bid_set):
        fail('blind IDs visibly encode an arm marker')
    print(f'  opacity check: PASS ({len(bid_set)} unique CSPRNG-sized opaque IDs; no tuple/arm/test/run/birthdate markers)')

    # 3. Exactly 30 C + 30 M
    n_C = sum(1 for e in entries if e['arm'] == 'C')
    n_M = sum(1 for e in entries if e['arm'] == 'M')
    if n_C != 30:
        fail(f'blind map has {n_C} Arm-C entries; expected exactly 30')
    if n_M != 30:
        fail(f'blind map has {n_M} Arm-M entries; expected exactly 30')

    # 5. Exactly 10 candidates per (R, B, arm) cell
    for R in FROZEN_RECONSTRUCTIONS:
        for B in FROZEN_BS:
            for arm in FROZEN_ARMS:
                n_in_cell = sum(1 for e in entries
                                 if e['reconstruction_id'] == R
                                 and e['block'] == B
                                 and e['arm'] == arm)
                if n_in_cell != FROZEN_CANDIDATES_PER_CELL:
                    fail(f'blind map cell {R}/{B}/{arm} has {n_in_cell} entries; expected exactly 10')

    # 6. candidate -> test/run/birthdate exactly matches test-invocations
    for e in entries:
        key = f'{e["reconstruction_id"]}/{e["block"]}'
        if key not in test_invocations['cell_layout']:
            fail(f'blind map entry references missing cell {key}')
        layout = test_invocations['cell_layout'][key]
        cand = e['candidate']
        if cand < 1 or cand > len(layout):
            fail(f'blind map entry candidate={cand} out of range for cell {key}')
        layout_entry = layout[cand - 1]
        if (e['test_id'], e['run'], e['birthdate']) != (
                layout_entry['test_id'], layout_entry['run'], layout_entry['invocation']):
            fail(f'blind map entry {(e["reconstruction_id"], e["block"], e["arm"], e["candidate"])} does not match test-invocations layout: got (test_id={e["test_id"]}, run={e["run"]}, birthdate={e["birthdate"]}); expected (test_id={layout_entry["test_id"]}, run={layout_entry["run"]}, invocation={layout_entry["invocation"]})')

    # 7. No missing or extra execution-order tuple (i.e., all 60 expected tuples are present and exactly once each)
    expected_tuples = {(R, B, arm, n)
                        for R in FROZEN_RECONSTRUCTIONS
                        for B in FROZEN_BS
                        for arm in FROZEN_ARMS
                        for n in range(1, FROZEN_CANDIDATES_PER_CELL + 1)}
    missing = expected_tuples - tup_set
    extra = tup_set - expected_tuples
    if missing or extra:
        fail(f'blind map tuple set mismatch: missing={sorted(missing)}; extra={sorted(extra)}')


def main():
    ap = argparse.ArgumentParser(description='INSA-ID-E1 v6.2 frozen blind-map builder/validator')
    ap.add_argument('--test-invocations', required=True, help='Path to inputs/test-invocations.json')
    ap.add_argument('--out', required=True, help='Output JSON path (the locked blind map; FATAL on any validation failure)')
    ap.add_argument('--validate-only', action='store_true', help='If set, validate the existing --out file instead of rebuilding')
    args = ap.parse_args()

    if args.validate_only:
        if not os.path.exists(args.out):
            fail(f'--validate-only: --out file does not exist: {args.out}')
        with open(args.out) as f:
            data = json.load(f)
        if isinstance(data, dict) and 'blind_id_to_tuple' in data:
            entries = list(data['blind_id_to_tuple'].values())
        elif isinstance(data, list):
            entries = data
        else:
            fail(f'--out file format unrecognized: expected list of entries or dict with blind_id_to_tuple')
        with open(args.test_invocations) as f:
            ti = json.load(f)
        validate_blind_map(entries, ti)
        print(f'OK: blind map at {args.out} validates against v6.2 invariants ({len(entries)} entries)')
    else:
        entries, ti = build_complete_blind_map(args.test_invocations)
        validate_blind_map(entries, ti)  # internal validation
        out = {
            'schema_version': '1.0',
            'record_kind': 'blind-map',
            'experiment_id': 'INSA-ID-E1',
            'frozen_at_utc_date': '2026-09-11',
            'frozen_by': 'Hermes (operator)',
            'phase_locked': 'Phase 0 (pre-dispatch preflight)',
            'binding_to_test_invocations_sha256': ti['frozen_test_corpus']['sha256'],
            'total_entries': len(entries),
            'note': 'No blind ID may be created, replaced, or modified after Phase 0. This blind map is the canonical lock for v6.2.',
            'blind_id_to_tuple': {e['blind_id']: e for e in entries},
        }
        tmp = args.out + '.tmp'
        with open(tmp, 'w') as f:
            json.dump(out, f, indent=2)
            f.write('\n')
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp, args.out)
        bm_sha = hashlib.sha256(open(args.out, 'rb').read()).hexdigest()
        print(f'WROTE: {args.out} ({len(entries)} entries, sha256={bm_sha})')
        print('  internal validation: OK (60 unique IDs, 60 unique tuples, 30 C + 30 M, 10 per cell, candidate->test/run/birthdate match)')


if __name__ == '__main__':
    main()
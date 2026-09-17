#!/usr/bin/env bash
set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$HERE"
export PYTHONPATH="$HERE"

echo "== FR-13 successor patch application =="
python3 tools/fr13_successor_corrections.py
python3 tools/fr13_fix_preflight_collection.py

echo "== Syntax checks =="
python3 -m py_compile \
  run_formal.py \
  qa_poc/crypto.py \
  trusted/enforcement_store.py \
  trusted/control_apply.py \
  trusted/executor.py \
  tests/host_runtime.py \
  tests/host_signer_worker.py \
  tests/case_functions.py \
  tests/test_fr13_successor.py \
  tools/fr13_fix_preflight_collection.py

echo "== Development tests: zero failures / zero skips required =="
set +e
DEV_OUT="$(python3 -m pytest -q -rs tests/ 2>&1)"
DEV_RC=$?
set -e
printf '%s\n' "$DEV_OUT"
if [ "$DEV_RC" -ne 0 ]; then
  echo "ERROR: development test suite failed with exit $DEV_RC" >&2
  exit "$DEV_RC"
fi
if grep -Eq '[0-9]+ skipped' <<<"$DEV_OUT"; then
  echo "ERROR: development suite contains skipped tests" >&2
  exit 1
fi

echo "== Bootstrap existing eight-key host topology =="
sudo -n bash bootstrap.sh "$HERE/qa_poc" "$HERE/trusted"

echo "== Exact PF1..PF14 preflight + six frozen spec locks =="
sudo -n env PYTHONPATH="$HERE" python3 - <<'PY'
import run_formal
repo='/home/fjventura20/devProjectsU/development-by-intent-ateqa'
r=run_formal.run_preflight(repo)
for x in r:
    print(f'{x.item}: {x.result} {x.name} {x.evidence}')
ids=[x.item for x in r]
assert ids == [f'PF{i}' for i in range(1,15)], ids
assert run_formal.preflight_is_complete_and_passing(r)
locks=run_formal.verify_frozen_spec_locks(repo)
assert len(locks)==6 and all(x['verified'] for x in locks), locks
print('PREFLIGHT EXACT SET: 14/14 PASS')
print('FROZEN SPEC LOCKS: 6/6 PASS')
PY

echo "== Private-key custody: controller holds proxies only =="
sudo -n env PYTHONPATH="$HERE" python3 - <<'PY'
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from tests.host_runtime import build_host_harness, RemoteEd25519Signer
h=build_host_harness()
privs=[h.keys.policy_priv,h.keys.identity_priv,h.keys.r11_priv,h.keys.r12_priv,
       h.keys.auth_priv,h.keys.trust_priv,h.keys.executor_priv,h.keys.audit_priv]
assert all(isinstance(x, RemoteEd25519Signer) for x in privs)
assert all(not isinstance(x, Ed25519PrivateKey) for x in privs)
print('CONTROLLER PRIVATE KEY OBJECTS: 0')
print('REMOTE SIGNER PROXIES: 8/8 PASS')
PY

echo "== Formal runner gate remains closed =="
set +e
sudo -n env PYTHONPATH="$HERE" python3 run_formal.py \
  --evidence-dir /var/lib/ate/poc/formal-evidence-002-readiness \
  --repo-dir /home/fjventura20/devProjectsU/development-by-intent-ateqa \
  >/tmp/ate-fr13-formal-refusal.out 2>/tmp/ate-fr13-formal-refusal.err
GATE_RC=$?
set -e
if [ "$GATE_RC" -ne 77 ]; then
  echo "ERROR: formal runner without token returned $GATE_RC, expected 77" >&2
  exit 1
fi
echo "FORMAL-002 GATE: PASS (exit 77)"

echo "== Host-mode successor dry run (NOT FORMAL) =="
sudo -n env PYTHONPATH="$HERE" ATE_USE_BOOTSTRAP_KEYS=1 python3 - <<'PY'
import os, shutil
from qa_poc.formal_runner import run_all_cases, classify
edir='/tmp/ate-fr13-host-dryrun'
shutil.rmtree(edir, ignore_errors=True)
os.makedirs(edir, exist_ok=True)
cases=run_all_cases(harness=None, evidence_dir=edir)
for c in cases:
    print(f'{c.test_id}: {c.pass_fail} {c.verdict} {c.reason_code}')
    if c.invalid_run_reason or c.error:
        print('  invalid=', c.invalid_run_reason, 'error=', c.error)
assert len(cases)==16
assert len({c.test_id for c in cases})==16
assert all(c.pass_fail=='PASS' for c in cases), [(c.test_id,c.pass_fail,c.reason_code,c.error) for c in cases]
assert all(c.audit_chain_valid for c in cases)
assert not any(c.enforcement_failure_reason for c in cases)
p11a=next(c for c in cases if c.test_id=='QA-P11a')
p11b=next(c for c in cases if c.test_id=='QA-P11b')
assert p11a.subcheck_results['actual_cr_committed_first'] is True
assert p11a.subcheck_results['actual_eap_denied_after_cr'] is True
assert p11b.subcheck_results['first_actual_eap_succeeded'] is True
assert p11b.subcheck_results['actual_cr_committed_after_eap'] is True
assert p11b.subcheck_results['fresh_action_denied_after_cr'] is True
classification=classify(preflight_pass=True,cases=cases)
assert classification=='QUALIFICATION_ADMISSION_LOCAL_POC_PASS', classification
print('ACTUAL P11 TRANSACTION ORDERINGS: PASS')
print('DRY-RUN CLASSIFICATION:', classification)
PY

echo "== Successor run-record construction static checks =="
python3 - <<'PY'
from pathlib import Path
s=Path('run_formal.py').read_text()
assert 'ate-poc-v010-formal-002' in s
assert '/var/lib/ate/poc/formal-evidence-002' in s
assert 'preflight_is_complete_and_passing(preflight)' in s
assert 'verify_frozen_spec_locks(args.repo_dir)' in s
print('FORMAL-002 DISTINCT RUN ID / EVIDENCE PATH: PASS')
print('RUN-LEVEL SIX-LOCK RECORDING: PRESENT')
PY

echo "FR-13 SUCCESSOR READINESS VERIFY: PASS"
echo "formal-001 preserved as INVALID_RUN; formal-002 NOT authorized or executed"

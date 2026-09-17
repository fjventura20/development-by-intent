#!/usr/bin/env bash
set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$HERE"
export PYTHONPATH="$HERE"

echo "== FR-11 patch application =="
if ! grep -q 'PUB_ROOT="/etc/ate/poc-public"' bootstrap.sh 2>/dev/null; then
  python3 tools/fr11_finalize.py
else
  echo "fr11_finalize.py already applied; skipping"
fi
if ! grep -q '^def as_user' tests/host_runtime.py 2>/dev/null; then
  python3 tools/fr11_enforce_runtime.py
else
  echo "fr11_enforce_runtime.py already applied; skipping"
fi

echo "== Syntax checks =="
python3 -m py_compile \
  qa_poc/formal_runner.py \
  run_formal.py \
  tests/host_runtime.py \
  tests/case_functions.py \
  tests/_helpers.py
bash -n bootstrap.sh

echo "== Development tests (ephemeral fixture keys; no scored run) =="
python3 -m pytest -q tests/

echo "== Bootstrap eight-key host topology =="
sudo -n bash bootstrap.sh "$HERE/qa_poc" "$HERE/trusted"

echo "== Bootstrap public manifest =="
python3 - <<'PY'
import json
p='/etc/ate/poc-public/public_key_manifest.json'
d=json.load(open(p))
ids=[x['key_id'] for x in d['keys']]
labels=[x['label'] for x in d['keys']]
assert len(ids)==8 and len(set(ids))==8, (len(ids), len(set(ids)))
print('8/8 distinct key IDs')
print('\n'.join(labels))
PY

echo "== Formal preflight function only (NO authorization token) =="
python3 - <<'PY'
import os
import run_formal
repo=os.path.abspath(os.path.join(os.getcwd(), '../../..'))
results=run_formal.run_preflight(repo)
for r in results:
    print(f'{r.item}: {r.result}  {r.name}  {r.evidence}')
assert len(results)==14, len(results)
assert all(r.result=='PASS' for r in results), [(r.item,r.result) for r in results]
print('PREFLIGHT: 14/14 PASS')
PY

echo "== Formal runner gate check (must refuse; NO scored run) =="
set +e
python3 run_formal.py >/tmp/ate-fr11-formal-refusal.out 2>/tmp/ate-fr11-formal-refusal.err
rc=$?
set -e
if [ "$rc" -ne 77 ]; then
  echo "ERROR: run_formal.py without token returned $rc, expected 77" >&2
  cat /tmp/ate-fr11-formal-refusal.err >&2 || true
  exit 1
fi
echo "formal gate refusal: PASS (exit 77)"

echo "== Host-key identity consistency check =="
sudo -n env PYTHONPATH="$HERE" python3 - <<'PY'
import json
from cryptography.hazmat.primitives import serialization
from qa_poc.crypto import key_id_from_public_pem
from tests.host_runtime import build_host_harness
h=build_host_harness()
manifest=json.load(open('/etc/ate/poc-public/public_key_manifest.json'))
by={x['label']:x['key_id'] for x in manifest['keys']}
def kid(pub):
    pem=pub.public_bytes(serialization.Encoding.PEM, serialization.PublicFormat.SubjectPublicKeyInfo)
    return key_id_from_public_pem(pem)
checks={
 'AUTH_POLICY': kid(h.keys.policy_pub),
 'AUTH_IDENTITY': kid(h.keys.identity_pub),
 'AUTH_R11_QUALIFICATION': kid(h.keys.r11_pub),
 'AUTH_R12_ADMISSION': kid(h.keys.r12_pub),
 'AUTH_AUTHORIZATION': kid(h.keys.auth_pub),
 'AUTH_TRUST_DECISION': kid(h.keys.trust_pub),
 'AUTH_EXECUTOR': kid(h.keys.executor_pub),
 'AUTH_AUDIT': kid(h.keys.audit_pub),
}
assert checks==by, (checks,by)
assert kid(h.keys.auth_identity_pub)==by['AUTH_IDENTITY']
print('host harness signer IDs match bootstrap manifest: PASS')
PY

echo "== Host-mode deterministic dry run (NOT formal scored execution) =="
sudo -n env PYTHONPATH="$HERE" ATE_USE_BOOTSTRAP_KEYS=1 python3 - <<'PY'
import os, shutil
from qa_poc.formal_runner import run_all_cases, classify
edir='/tmp/ate-fr11-host-dryrun'
shutil.rmtree(edir, ignore_errors=True)
os.makedirs(edir, exist_ok=True)
cases=run_all_cases(harness=None, evidence_dir=edir)
for c in cases:
    print(f'{c.test_id}: {c.pass_fail} {c.verdict} {c.reason_code}')
classification=classify(preflight_pass=True, cases=cases)
print('DRY-RUN CLASSIFICATION:', classification)
assert classification=='QUALIFICATION_ADMISSION_LOCAL_POC_PASS', classification
PY

echo "FR-11 VERIFY COMPLETE: PASS"
echo "Formal QA-P1..QA-P14 run was NOT authorized or executed by run_formal.py."

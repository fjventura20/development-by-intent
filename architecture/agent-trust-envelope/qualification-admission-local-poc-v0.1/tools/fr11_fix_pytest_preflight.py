#!/usr/bin/env python3
"""Align tests/test_preflight.py with the FR-11 frozen host topology.

This removes the obsolete single authority_signing.key assumption and makes
pytest PF5/PF6/PF9 match the actual formal preflight implementation.
It does not run bootstrap, preflight, or the formal scored run.
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
path = ROOT / "tests" / "test_preflight.py"
text = path.read_text()

# PF5: the installed trusted-code boundary is /opt/ate-poc-v010, not a legacy /bin child.
text = text.replace(
    '    opt_bin = "/opt/ate-poc-v010/bin"\n'
    '    if not _exists_as_root(opt_bin):\n'
    '        pytest.skip(f"trusted code dir not installed: {opt_bin}")\n',
    '    opt_bin = "/opt/ate-poc-v010"\n'
    '    if not _exists_as_root(opt_bin):\n'
    '        pytest.fail(f"trusted code dir not installed: {opt_bin}")\n',
    1,
)

start = text.index('def test_preflight_6_authority_keys_not_requester_readable')
end = text.index('\ndef test_preflight_7_executor_audit_keys_not_requester_readable', start)
new_pf6 = '''def test_preflight_6_authority_keys_not_requester_readable(bootstrap_state):
    """All six authority private keys exist and are unreadable by ate-requester."""
    keys = [
        "/var/lib/ate/poc/authority/policy_signing.key",
        "/var/lib/ate/poc/authority/identity_signing.key",
        "/var/lib/ate/poc/authority/r11_qualification_signing.key",
        "/var/lib/ate/poc/authority/r12_admission_signing.key",
        "/var/lib/ate/poc/authority/authorization_signing.key",
        "/var/lib/ate/poc/authority/trust_decision_signing.key",
    ]
    for key in keys:
        assert _exists_as_root(key), f"authority key not bootstrapped: {key}"
        res = subprocess.run(
            ["sudo", "-n", "-u", "ate-requester", "test", "-r", key],
            capture_output=True,
            text=True,
        )
        assert res.returncode != 0, f"authority key readable by ate-requester: {key}"
'''
text = text[:start] + new_pf6 + text[end:]

# PF9: replace the old PRAGMA proxy with the actual OS/resource bypass probe.
start = text.index('def test_preflight_9_direct_bypass_probe_fails')
end = text.index('\n\n# -- Item 10:', start)
new_pf9 = '''def test_preflight_9_direct_bypass_probe_fails():
    """Real requester/authority direct mutation attempts are denied and state is unchanged."""
    db = "/var/lib/ate/poc/executor/enforcement.db"
    assert _exists_as_root(db), f"enforcement.db not bootstrapped: {db}"
    fixture_id = "pytest-pf9-fixture"
    fixture_value = "PYTEST-PF9-baseline"

    init = subprocess.run([
        "sudo", "-n", "-u", "ate-executor", "sqlite3", db,
        f"INSERT OR REPLACE INTO protected_resource (resource_id, value, mutation_count) "
        f"VALUES ('{fixture_id}', '{fixture_value}', 0);",
    ], capture_output=True, text=True)
    assert init.returncode == 0, init.stderr

    baseline = subprocess.run([
        "sudo", "-n", "-u", "ate-executor", "sqlite3", db,
        f"SELECT value, mutation_count FROM protected_resource WHERE resource_id='{fixture_id}';",
    ], capture_output=True, text=True)
    assert baseline.returncode == 0, baseline.stderr

    bypass_sql = (
        f"UPDATE protected_resource SET value='BYPASS-VALUE', mutation_count=999 "
        f"WHERE resource_id='{fixture_id}';"
    )
    req_sql = subprocess.run(
        ["sudo", "-n", "-u", "ate-requester", "sqlite3", db, bypass_sql],
        capture_output=True, text=True,
    )
    req_dd = subprocess.run(
        ["sudo", "-n", "-u", "ate-requester", "dd", "if=/dev/zero", f"of={db}",
         "bs=1", "count=1", "conv=notrunc"],
        capture_output=True, text=True,
    )
    auth_sql = subprocess.run(
        ["sudo", "-n", "-u", "ate-authority", "sqlite3", db, bypass_sql],
        capture_output=True, text=True,
    )
    after = subprocess.run([
        "sudo", "-n", "-u", "ate-executor", "sqlite3", db,
        f"SELECT value, mutation_count FROM protected_resource WHERE resource_id='{fixture_id}';",
    ], capture_output=True, text=True)

    assert req_sql.returncode != 0
    assert req_dd.returncode != 0
    assert auth_sql.returncode != 0
    assert after.returncode == 0, after.stderr
    assert after.stdout.strip() == baseline.stdout.strip()
'''
text = text[:start] + new_pf9 + text[end:]

path.write_text(text)
print("FR-11 pytest preflight alignment applied: tests/test_preflight.py")
print("Formal scored run remains unauthorized.")

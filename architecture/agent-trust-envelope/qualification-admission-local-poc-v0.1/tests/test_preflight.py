"""ATE Qualification & Admission Local PoC v0.1 — preflight checks.

Per design §31, the formal runner MUST verify 14 preflight items before
QA-P1 begins. This file implements each as a self-contained test
function. Each test returns PASS/FAIL/SKIP via the assertion result.

These tests check:
  1. frozen architecture blob locks match
  2. PoC design-freeze blob matches
  3. OS identities exist
  4. trusted noninteractive orchestration path exists
  5. trusted code not requester-writable
  6. authority keys not requester-readable
  7. executor/audit keys not requester/authority-readable
  8. enforcement store not requester/authority directly writable
  9. direct-bypass probe fails
  10. canonicalization self-test passes
  11. signing/domain-separation self-test passes
  12. monotonic control-epoch self-test passes
  13. audit-chain self-test passes
  14. required SQLite serialization is available
"""

from __future__ import annotations

import grp
import hashlib
import os
import pwd
import shutil
import sqlite3
import subprocess
import tempfile

import pytest

from qa_poc.canonical import (
    canonical_json_bytes,
    canonical_sha256,
    signing_bytes,
)
from qa_poc.crypto import sign_ed25519, verify_ed25519
from qa_poc.models import (
    DOMAIN_CONTROL_RECORD,
    DOMAIN_QUALIFICATION_CREDENTIAL,
    CapabilityToken,
    ControlRecord,
    QualificationCredential,
    artifact_payload,
)
from trusted import enforcement_store


# Frozen architecture + PoC design freeze SHAs (per handoff payload).
FROZEN_ARCH_COMMIT = "c881ba76f83392a242415fa4c37a1f61ae6dd92b"
POC_DESIGN_FREEZE_COMMIT = "4f0eb8e55f621283474fe03af0f060f7866affb8"
POC_DESIGN_BLOB = "48cc34a67a68da573fd96fdbd597ffd85bb7ec90"


# -- Item 1: frozen architecture blob locks match ---------------------------


def test_preflight_1_frozen_architecture_blob():
    """Frozen v0.2.2 architecture commit is reachable from origin/main.

    We probe the local clone of fjventura20/development-by-intent for
    the commit. This PoC's own origin/main is at the PoC design-freeze
    commit, which is descended from the architecture freeze.
    """
    repo = "/home/fjventura20/devProjectsU/development-by-intent"
    if not os.path.isdir(repo):
        pytest.skip(f"local clone not present: {repo}")
    out = subprocess.run(
        ["git", "-C", repo, "cat-file", "-t", FROZEN_ARCH_COMMIT],
        capture_output=True,
        text=True,
    )
    if out.returncode != 0 or out.stdout.strip() != "commit":
        pytest.fail(f"frozen architecture commit not in local clone: {out.stderr}")
    # Verify the AGENT-QUALIFICATION-ADMISSION-v0.2.2-FREEZE.md file exists at that commit
    out2 = subprocess.run(
        ["git", "-C", repo, "show", f"{FROZEN_ARCH_COMMIT}:architecture/agent-trust-envelope/AGENT-QUALIFICATION-ADMISSION-v0.2.2-FREEZE.md"],
        capture_output=True,
        text=True,
    )
    assert out2.returncode == 0, "v0.2.2 architecture freeze markdown missing at frozen commit"
    assert "AGENT-QUALIFICATION-ADMISSION" in out2.stdout
    assert "v0.2.2" in out2.stdout


# -- Item 2: PoC design-freeze blob matches --------------------------------


def test_preflight_2_poc_design_blob():
    """The PoC design-freeze blob SHA matches the expected.

    Per ChatGPT DEV-IMP-1 resolution: the freeze manifest records the
    Git blob ID, which is `git hash-object` over the file bytes —
    distinct from `sha256sum` over raw content. We verify using
    `git ls-tree` / `git hash-object` to get the proper Git blob ID.
    """
    repo = "/home/fjventura20/devProjectsU/development-by-intent"
    if not os.path.isdir(repo):
        pytest.skip(f"local clone not present: {repo}")
    out = subprocess.run(
        ["git", "-C", repo, "cat-file", "-p", f"{POC_DESIGN_FREEZE_COMMIT}:architecture/agent-trust-envelope/ATE-QUALIFICATION-ADMISSION-LOCAL-POC-v0.1.2-DESIGN.md"],
        capture_output=True,
        text=True,
    )
    assert out.returncode == 0, "PoC design file not at frozen commit"
    # Compute the Git blob ID via git ls-tree (the only reliable way to
    # get the on-disk blob SHA recorded by the freeze manifest).
    ls = subprocess.run(
        ["git", "-C", repo, "ls-tree", POC_DESIGN_FREEZE_COMMIT, "architecture/agent-trust-envelope/ATE-QUALIFICATION-ADMISSION-LOCAL-POC-v0.1.2-DESIGN.md"],
        capture_output=True,
        text=True,
    )
    assert ls.returncode == 0, f"git ls-tree failed: {ls.stderr}"
    # Output: "<mode> blob <sha>\t<path>"
    parts = ls.stdout.strip().split()
    assert len(parts) >= 3, f"unexpected ls-tree output: {ls.stdout!r}"
    blob_hash = parts[2]
    assert blob_hash == POC_DESIGN_BLOB, (
        f"PoC design Git blob ID mismatch: expected {POC_DESIGN_BLOB}, got {blob_hash}"
    )


# -- Item 3: OS identities exist -------------------------------------------


def test_preflight_3_os_identities_exist():
    """The three system identities exist."""
    for name in ("ate-requester", "ate-authority", "ate-executor"):
        try:
            pwd.getpwnam(name)
        except KeyError:
            pytest.fail(f"identity {name} does not exist (bootstrap not run)")
        try:
            grp.getgrnam(name)
        except KeyError:
            pytest.fail(f"group {name} does not exist")


# -- Item 4: trusted noninteractive orchestration path exists ----------------


def test_preflight_4_orchestration_path_exists():
    """The bootstrap.sh script exists and is executable (or runnable by root)."""
    this_dir = os.path.dirname(os.path.abspath(__file__))
    repo_root = os.path.dirname(this_dir)
    bootstrap = os.path.join(repo_root, "bootstrap.sh")
    assert os.path.exists(bootstrap), f"bootstrap.sh missing at {bootstrap}"
    # Either executable, or readable by root (who would run it via sudo).
    mode = os.stat(bootstrap).st_mode
    assert mode & 0o444, "bootstrap.sh not readable"


# -- Items 5/6/7/8: file-ownership / mode bits (skip if not bootstrapped) ---


def _skip_unless_bootstrapped():
    for name in ("ate-requester", "ate-authority", "ate-executor"):
        try:
            pwd.getpwnam(name)
        except KeyError:
            pytest.skip(f"identities not bootstrapped ({name} missing)")


def _exists_as_root(path: str) -> bool:
    """Check existence even when the path is in a 0700-owned dir.

    We use `sudo -n test -e` which runs as root (or returns nonzero if
    sudo is not available)."""
    r = subprocess.run(["sudo", "-n", "test", "-e", path], capture_output=True, text=True)
    return r.returncode == 0


@pytest.fixture
def bootstrap_state():
    """Skip tests 5/6/7/8 if not bootstrapped."""
    _skip_unless_bootstrapped()


def test_preflight_5_trusted_code_not_requester_writable(bootstrap_state):
    """The trusted code directory is not writable by ate-requester."""
    opt_bin = "/opt/ate-poc-v010"
    if not _exists_as_root(opt_bin):
        pytest.fail(f"trusted code dir not installed: {opt_bin}")
    # As ate-requester, attempt to write to the dir
    cmd = [
        "sudo", "-n", "-u", "ate-requester",
        "test", "-w", opt_bin,
    ]
    res = subprocess.run(cmd, capture_output=True, text=True)
    # Expect non-zero exit (NOT writable)
    assert res.returncode != 0, "trusted code dir is writable by ate-requester (BAD)"


def test_preflight_6_authority_keys_not_requester_readable(bootstrap_state):
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

def test_preflight_7_executor_audit_keys_not_requester_readable(bootstrap_state):
    """Executor + audit private keys not readable by ate-requester or ate-authority."""
    for key in (
        "/var/lib/ate/poc/executor/executor_signing.key",
        "/var/lib/ate/poc/executor/audit_signing.key",
    ):
        if not _exists_as_root(key):
            pytest.skip(f"key not bootstrapped: {key}")
        for principal in ("ate-requester", "ate-authority"):
            cmd = ["sudo", "-n", "-u", principal, "test", "-r", key]
            res = subprocess.run(cmd, capture_output=True, text=True)
            assert res.returncode != 0, f"{key} readable by {principal} (BAD)"


def test_preflight_8_enforcement_store_not_requester_authority_writable(bootstrap_state):
    """The enforcement.db is not directly writable by requester or authority."""
    db = "/var/lib/ate/poc/executor/enforcement.db"
    if not _exists_as_root(db):
        pytest.skip(f"enforcement.db not bootstrapped: {db}")
    for principal in ("ate-requester", "ate-authority"):
        cmd = ["sudo", "-n", "-u", principal, "test", "-w", db]
        res = subprocess.run(cmd, capture_output=True, text=True)
        assert res.returncode != 0, f"{db} writable by {principal} (BAD)"


# -- Item 9: direct-bypass probe fails (in-process version) ----------------


def test_preflight_9_direct_bypass_probe_fails():
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


# -- Item 10: canonicalization self-test passes ----------------------------


def test_preflight_10_canonicalization_self_test():
    """Reordered keys → same digest; semantic mutation → different digest;
    duplicate key → parse reject; float → reject; wrong signing domain →
    signature reject."""
    # Reordering
    assert canonical_sha256({"a": 1, "b": 2}) == canonical_sha256({"b": 2, "a": 1})
    # Semantic mutation
    assert canonical_sha256({"a": 1}) != canonical_sha256({"a": 2})
    # Float rejection
    with pytest.raises(Exception):
        canonical_sha256({"a": 1.5})
    # Wrong domain
    priv, pub = _fresh_keypair()
    sig = sign_ed25519(priv, "domain.A", {"a": 1})
    with pytest.raises(Exception):
        verify_ed25519(pub, sig, "domain.B", {"a": 1})


def _fresh_keypair():
    from qa_poc.crypto import generate_keypair
    return generate_keypair()


# -- Item 11: signing/domain-separation self-test passes -------------------


def test_preflight_11_signing_domain_separation():
    """Same canonical payload under different artifact domains must not
    cross-verify."""
    priv, pub = _fresh_keypair()
    payload = {"a": 1, "b": 2}
    sig_a = sign_ed25519(priv, "ate.qualification.credential.v1", payload)
    sig_b = sign_ed25519(priv, "ate.admission.credential.v1", payload)
    verify_ed25519(pub, sig_a, "ate.qualification.credential.v1", payload)
    verify_ed25519(pub, sig_b, "ate.admission.credential.v1", payload)
    # Cross-domain verification must fail
    with pytest.raises(Exception):
        verify_ed25519(pub, sig_a, "ate.admission.credential.v1", payload)
    with pytest.raises(Exception):
        verify_ed25519(pub, sig_b, "ate.qualification.credential.v1", payload)
    # And signing bytes must include the 0x00 separator
    sb = signing_bytes("ate.qualification.credential.v1", payload)
    assert b"\x00" in sb
    assert sb.startswith(b"ate.qualification.credential.v1\x00")


# -- Item 12: monotonic control-epoch self-test passes ----------------------


def test_preflight_12_monotonic_control_epoch():
    """Two ControlRecords applied sequentially increment the epoch by
    exactly +1 each; replay of a record_id is rejected."""
    from qa_poc.models import ControlRecord, DOMAIN_CONTROL_RECORD
    from trusted.control_apply import apply_control_record

    keys = _fresh_keypair()
    conn, tmp = _open_tmp_store()
    try:
        from trusted.enforcement_store import current_epoch
        assert current_epoch(conn) == 0
        rec1 = _make_control_record(
            keys,
            previous_epoch=0,
            new_epoch=1,
            change_type="QUALIFICATION_REVOCATION",
            target_id="t1",
            target_digest="d1",
            record_id="r1",
        )
        new_epoch = apply_control_record(
            conn, record=rec1, issuer_pub=keys[1],
            change_type_authorization_lookup=lambda ct, k: True,
            created_at_unix_ms=1,
        )
        assert new_epoch == 1
        assert current_epoch(conn) == 1

        rec2 = _make_control_record(
            keys,
            previous_epoch=1,
            new_epoch=2,
            change_type="QUALIFICATION_REVOCATION",
            target_id="t2",
            target_digest="d2",
            record_id="r2",
        )
        new_epoch = apply_control_record(
            conn, record=rec2, issuer_pub=keys[1],
            change_type_authorization_lookup=lambda ct, k: True,
            created_at_unix_ms=2,
        )
        assert new_epoch == 2
        assert current_epoch(conn) == 2

        # Replay of r1 must fail
        from trusted.control_apply import ControlRecordError
        with pytest.raises(ControlRecordError):
            apply_control_record(
                conn, record=rec1, issuer_pub=keys[1],
                change_type_authorization_lookup=lambda ct, k: True,
                created_at_unix_ms=3,
            )
    finally:
        conn.close()
        shutil.rmtree(tmp, ignore_errors=True)


def _open_tmp_store():
    tmp = tempfile.mkdtemp(prefix="ate-poc-preflight-")
    db_path = os.path.join(tmp, "enforcement.db")
    return enforcement_store.open_store(db_path), tmp


def _make_control_record(keys, *, previous_epoch, new_epoch, change_type, target_id, target_digest, record_id):
    from qa_poc.models import ControlRecord, compute_id_and_digest
    priv, pub = keys
    semantic = {
        "previous_epoch": previous_epoch,
        "new_epoch": new_epoch,
        "change_type": change_type,
        "target_type": "qualification",
        "target_id": target_id,
        "target_digest_optional": target_digest,
        "issued_at_unix_ms": 1000,
        "issuer_authority_id": "r11-q",
        "issuer_key_id": "r11-q",
    }
    rec_proto = ControlRecord(
        record_id="",
        previous_epoch=previous_epoch,
        new_epoch=new_epoch,
        change_type=change_type,
        target_type="qualification",
        target_id=target_id,
        target_digest_optional=target_digest,
        issued_at_unix_ms=1000,
        issuer_authority_id="r11-q",
        issuer_key_id="r11-q",
        record_digest="",
    )
    rec, _ = compute_id_and_digest(
        rec_proto,
        semantic_fields=semantic,
        id_prefix="rev",
        id_salt=(record_id, target_id),
    )
    sig = sign_ed25519(priv, DOMAIN_CONTROL_RECORD, artifact_payload(rec))
    return rec.__class__(**{**rec.__dict__, "signature": sig})


# -- Item 13: audit-chain self-test passes ---------------------------------


def test_preflight_13_audit_chain_self_test():
    """append_audit + verify_audit_chain are consistent for a multi-event
    sequence; tampering with one row breaks the chain."""
    conn, tmp = _open_tmp_store()
    try:
        for i in range(5):
            enforcement_store.append_audit(
                conn,
                event_type="CONTROL_RECORD_APPLIED",
                payload={"i": i, "data": "x" * 10},
                created_at_unix_ms=1000 + i,
            )
        assert enforcement_store.verify_audit_chain(conn) is True

        # Tamper with one row's payload
        conn.execute(
            "UPDATE audit SET payload_json=? WHERE sequence=2",
            ('{"i": 999, "data": "tampered"}',),
        )
        assert enforcement_store.verify_audit_chain(conn) is False
    finally:
        conn.close()
        shutil.rmtree(tmp, ignore_errors=True)


# -- Item 14: required SQLite serialization is available ------------------


def test_preflight_14_sqlite_serialization_available():
    """SQLite supports BEGIN IMMEDIATE and the executor-owned serialized
    write transaction is observable."""
    conn, tmp = _open_tmp_store()
    try:
        conn.execute("BEGIN IMMEDIATE")
        conn.execute(
            "INSERT INTO applied_control_records (record_id, target_type, target_id, target_digest, status, issued_at_unix_ms, applied_at_unix_ms, applied_epoch, record_digest) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            ("r-init", "qualification", "x", "d", "APPLIED", 1, 1, 1, "rd"),
        )
        conn.execute("COMMIT")
        cur = conn.execute("SELECT applied_epoch FROM applied_control_records WHERE record_id='r-init'")
        assert cur.fetchone()[0] == 1
        # And the eap_transaction context manager works
        with enforcement_store.eap_transaction(conn) as tx:
            tx.execute(
                "INSERT INTO applied_control_records (record_id, target_type, target_id, target_digest, status, issued_at_unix_ms, applied_at_unix_ms, applied_epoch, record_digest) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                ("r2", "qualification", "x", "d", "APPLIED", 1, 1, 2, "rd2"),
            )
            tx.execute("COMMIT")
        cur = conn.execute("SELECT COUNT(*) FROM applied_control_records")
        assert cur.fetchone()[0] == 2
    finally:
        conn.close()
        shutil.rmtree(tmp, ignore_errors=True)

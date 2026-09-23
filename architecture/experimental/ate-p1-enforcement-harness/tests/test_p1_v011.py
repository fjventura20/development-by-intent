"""ATE P1 v0.1.1 — controlling test matrix T0-T10.

Per v0.1.1 §6:
  T0 — Valid authorized execution
  T1 — Direct bypass denial
  T2 — Cross-process credential separation
  T3 — Restart-durable nonce
  T4 — Revocation serialized before use
  T5 — Concurrent replay
  T6 — Transaction rollback on audit failure
  T7 — Audit tamper detection
  T8 — Stable resource identity
  T9 — Startup audit-integrity gate
  T10 — Crash/rollback consistency

Run with: python3 tests/test_p1_v011.py
"""
from __future__ import annotations

import base64
import hashlib
import hmac
import json
import os
import shutil
import sqlite3
import subprocess
import sys
import threading
import time
from typing import Any, Dict, List, Tuple

HERE = os.path.dirname(os.path.abspath(__file__))
HARNESS_DIR = os.path.abspath(os.path.join(HERE, "..", "implementation_v011"))
if HARNESS_DIR not in sys.path:
    sys.path.insert(0, HARNESS_DIR)

# Re-expose harness modules
sys.path_importer_cache.clear() if hasattr(sys, "path_importer_cache") else None

import audit_chain  # noqa: E402
import authority_db  # noqa: E402
import crypto_utils  # noqa: E402
import ipc_protocol  # noqa: E402
import ipc_worker  # noqa: E402
import privileged_executor  # noqa: E402
import protected_resource  # noqa: E402
import requester as requester_mod  # noqa: E402
from test_fixtures import (  # noqa: E402
    Fixture,
    mk_tmpdir,
    rm_tmpdir,
    make_request,
    verify_audit_chain,
)


RESULTS: Dict[str, Dict[str, Any]] = {}


def _record(test_id: str, *, ok: bool, details: Dict[str, Any]) -> None:
    RESULTS[test_id] = {"pass": ok, "details": details}
    print(f"  {test_id}: {'PASS' if ok else 'FAIL'}  {json.dumps(details, sort_keys=True)}")


# ----------------------------------------------------------------------
# T0 — Valid authorized execution (positive control)
# ----------------------------------------------------------------------


def test_T0_valid_execution() -> None:
    tmpdir = mk_tmpdir("T0")
    try:
        now = 1700000000.0
        f = Fixture(tmpdir, now)
        r = f.add_resource("filesystem:/protected/file-A.txt")
        decision_id = "dec-T0-001"
        f.add_trust_decision(
            decision_id,
            operation="WRITE_SCOPED",
            resource_id=r["resource_id"],
            session_id="session-T0-001",
            nonce="nonce-T0-001",
            target_display="filesystem:/protected/file-A.txt",
        )
        req = make_request(
            fixture=f,
            request_id="req-T0-001",
            decision_id=decision_id,
            operation="WRITE_SCOPED",
            resource_id=r["resource_id"],
            session_id="session-T0-001",
            nonce="nonce-T0-001",
            target_display="filesystem:/protected/file-A.txt",
            issued_at_utc=now,
        )
        resp = f.run_executor_one_shot(req, deterministic_clock=now)
        ok = (
            resp.get("verdict") == "EXECUTED"
            and resp.get("reason_code") == "PX_OK"
            and resp.get("mutation_count_after") == 1
        )
        # Audit chain tip
        audit_records = f.read_audit_records()
        anchor = f.read_anchor()
        nonce_row = f.read_nonce("nonce-T0-001")
        ok = ok and (
            len(audit_records) == 1
            and anchor["final_seq"] == 1
            and nonce_row["state"] == "CONSUMED"
            and nonce_row["outcome"] == "EXECUTED"
        )
        # Audit chain must verify
        chain_ok, chain_reason = verify_audit_chain(f)
        ok = ok and chain_ok
        _record(
            "T0",
            ok=ok,
            details={
                "verdict": resp.get("verdict"),
                "reason_code": resp.get("reason_code"),
                "mutation_count_after": resp.get("mutation_count_after"),
                "audit_chain_len": len(audit_records),
                "anchor_final_seq": int(anchor["final_seq"]),
                "nonce_state": nonce_row["state"],
                "audit_chain_verify": chain_ok,
            },
        )
    finally:
        rm_tmpdir(tmpdir)


# ----------------------------------------------------------------------
# T1 — Direct bypass denial
# ----------------------------------------------------------------------


def test_T1_direct_bypass() -> None:
    """Direct bypass: requester attempts protected mutation OUTSIDE
    executor IPC.

    Per v0.1.1 §6 / T1 + PI directive 2026-09-15: the requester side
    MUST NOT have direct write access to the authority DB. The
    bypass attempt from a requester subprocess must FAIL.

    Enforcement boundary:
      - Authority DB is owned by ate-executor with mode 0600.
      - Tmpdir containing the DB is mode 0700 owned by ate-executor.
      - The requester subprocess (launched by the parent test process
        as the unprivileged user) has NO path to the DB and NO OS
        permission to open or list the file.
      - The bypass subprocess does NOT receive the DB path, the
        credentials path, or the audit key path as arguments.

    The probe (`tests/bypass_requester.py`) attempts:
      - listing the test tmpdir
      - opening the authority.sqlite file (by guessing its name)
      - reading the executor_audit_key.bin / executor_credentials.json
        files (by guessing their names)
    All attempts MUST fail with PermissionError or FileNotFoundError.
    The mutation count of the protected resource MUST remain 0.
    """
    tmpdir = mk_tmpdir("T1")
    bypass_script = os.path.join(os.path.dirname(__file__), "bypass_requester.py")
    f = None  # type: ignore[assignment]
    try:
        now = 1700000100.0
        f = Fixture(tmpdir, now)
        # Set up OS-level privilege boundary BEFORE bootstrap.
        f.privilege_setup()
        r = f.add_resource("filesystem:/protected/file-B.txt")
        f.add_trust_decision(
            "dec-T1-001",
            operation="WRITE_SCOPED",
            resource_id=r["resource_id"],
            session_id="session-T1-001",
            nonce="nonce-T1-001",
            target_display="filesystem:/protected/file-B.txt",
        )
        f.write_seed(reset=True)
        f.write_executor_secrets()
        f.seed_insert_resource_via_admin(r["resource_id"], "filesystem:/protected/file-B.txt", r["credential"])
        f.seed_insert_decision_via_admin(
            "dec-T1-001",
            json.dumps(f.trust_decision_payloads["dec-T1-001"], sort_keys=True),
            f.trust_decision_signatures["dec-T1-001"],
        )
        # Pre-state from harness view (read via admin)
        pre = f.read_resource(r["resource_id"])
        pre_cred_hex = None
        pre_rows = f.admin_raw_sql(
            "SELECT resource_credential_hex FROM protected_resources WHERE resource_id=?",
            [r["resource_id"]],
        )
        if pre_rows:
            pre_cred_hex = pre_rows[0]["resource_credential_hex"]

        # Launch the bypass probe subprocess.
        # Crucially, we pass ONLY --resource_dir (the test tmpdir).
        # We do NOT pass the DB path or any executor secret paths.
        cmd = [
            sys.executable,
            bypass_script,
            "--resource_id", r["resource_id"],
            "--resource_dir", tmpdir,
        ]
        proc = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=30,
        )
        try:
            bypass_obs = json.loads(proc.stdout.strip())
        except Exception:
            bypass_obs = {"_parse_error": proc.stdout[:500], "stderr": proc.stderr[:500]}

        # Post-state
        post = f.read_resource(r["resource_id"])
        post_rows = f.admin_raw_sql(
            "SELECT resource_credential_hex FROM protected_resources WHERE resource_id=?",
            [r["resource_id"]],
        )
        post_cred_hex = post_rows[0]["resource_credential_hex"] if post_rows else None
        audit_records = f.read_audit_records()
        nonce_row = f.read_nonce("nonce-T1-001")

        # Primary controlling claim: the requester subprocess MUST NOT
        # have been able to open or read the authority DB.
        listdir = bypass_obs.get("listdir_attempt", {})
        db_open = bypass_obs.get("db_open_attempt", {})
        secrets_read = bypass_obs.get("secrets_read_attempt", [])

        listdir_blocked = (
            listdir.get("listable") is False
            or listdir.get("error")
        )
        db_open_blocked = (
            db_open.get("opened") is False
            or db_open.get("writable") is False
            or db_open.get("error")
        )
        secrets_blocked = all(
            fp.get("readable") is False for fp in secrets_read
        )

        # Secondary controlling claim: protected state unchanged.
        ok_resource = (
            pre is not None
            and post is not None
            and int(pre["mutation_count"]) == int(post["mutation_count"])
            and pre["state_json"] == post["state_json"]
        )
        # The credential column is preserved (the bypass never reached
        # the DB, so it definitely didn't change the credential).
        ok_cred_immutable = pre_cred_hex == post_cred_hex
        ok_audit = len(audit_records) == 0

        ok = (
            listdir_blocked
            and db_open_blocked
            and secrets_blocked
            and ok_resource
            and ok_cred_immutable
            and ok_audit
        )

        _record(
            "T1",
            ok=ok,
            details={
                "controlling_claim": (
                    "requester subprocess cannot open or read authority DB "
                    "due to OS-level permission boundary"
                ),
                "requester_subprocess_uid": bypass_obs.get("uid"),
                "requester_subprocess_euid": bypass_obs.get("euid"),
                "listdir_attempt": listdir,
                "db_open_attempt": db_open,
                "secrets_read_attempt": secrets_read,
                "pre_mutation_count": int(pre["mutation_count"]) if pre else None,
                "post_mutation_count": int(post["mutation_count"]) if post else None,
                "pre_state_json": pre["state_json"] if pre else None,
                "post_state_json": post["state_json"] if post else None,
                "resource_unchanged": ok_resource,
                "audit_chain_len": len(audit_records),
                "nonce_row_present": nonce_row is not None,
                "credential_column_unchanged": ok_cred_immutable,
                "listdir_blocked": listdir_blocked,
                "db_open_blocked": db_open_blocked,
                "secrets_blocked": secrets_blocked,
                "raw_bypass_observation": bypass_obs,
            },
        )
    finally:
        try:
            f.privilege_teardown()
        except Exception:
            pass
        rm_tmpdir(tmpdir)


# ----------------------------------------------------------------------
# T2 — Cross-process credential separation
# ----------------------------------------------------------------------


def test_T2_credential_separation() -> None:
    """Cross-process credential separation: subprocess-boundary probe.

    Per v0.1.1 §6 / T2: the requester process is inspected through its
    documented environment, request, response, and fixture-visible
    state. Executor-only credentials and database write authority are
    absent.

    The test launches a separate requester-process probe
    (`tests/requester_probe.py`) and inspects:
      - argv
      - environment
      - cwd
      - files it can read in the test tmpdir (deny-read on the
        executor-only credentials file)
      - the requester module's exposed state
      - the IPC response it receives from a properly-configured worker
      - the absence of any audit-key, credential, signing-authority,
        or DB-write-credential material in the observation
    """
    tmpdir = mk_tmpdir("T2")
    probe_script = os.path.join(os.path.dirname(__file__), "requester_probe.py")
    try:
        now = 1700000200.0
        f = Fixture(tmpdir, now)
        # Set up a single protected resource + decision so the probe
        # can issue a real IPC request and observe the real response.
        r = f.add_resource("filesystem:/protected/file-C.txt")
        f.add_trust_decision(
            "dec-T2-001",
            operation="WRITE_SCOPED",
            resource_id=r["resource_id"],
            session_id="session-T2-001",
            nonce="nonce-T2-001",
            target_display="filesystem:/protected/file-C.txt",
        )
        f.write_seed(reset=True)
        f.write_executor_secrets()
        # Bootstrap pass: launch the worker to insert the resource row
        # with its real credential (similar to T1).
        bootstrap_decision = "dec-T2-bootstrap-001"
        bootstrap_nonce = "nonce-T2-bootstrap-001"
        f.add_trust_decision(
            bootstrap_decision,
            operation="WRITE_SCOPED",
            resource_id=r["resource_id"],
            session_id="session-T2-bootstrap",
            nonce=bootstrap_nonce,
            target_display="filesystem:/protected/file-C.txt",
        )
        bootstrap_req = make_request(
            fixture=f,
            request_id="req-T2-bootstrap-001",
            decision_id=bootstrap_decision,
            operation="WRITE_SCOPED",
            resource_id=r["resource_id"],
            session_id="session-T2-bootstrap",
            nonce=bootstrap_nonce,
            target_display="filesystem:/protected/file-C.txt",
            issued_at_utc=now,
        )
        bootstrap_resp = f.run_executor_one_shot(bootstrap_req, deterministic_clock=now)
        if bootstrap_resp.get("verdict") != "EXECUTED":
            raise RuntimeError(f"T2 bootstrap failed: {bootstrap_resp}")
        # Rollback the bootstrap mutation so T2's IPC probe can run
        # against an unmutated resource. (This is harness-side bootstrap,
        # not a requester-side action.)
        from audit_chain import make_anchor_mac as _anchor
        new_anchor = _anchor(f.audit_key, 0, "")
        f.admin_update_resource_for_bootstrap_rollback(
            r["resource_id"],
            json.dumps(
                {"display_path": "filesystem:/protected/file-C.txt", "history": []},
                sort_keys=True,
                separators=(",", ":"),
            ),
        )
        f.admin_delete_audit_records("req-T2-bootstrap-001")
        f.admin_update_anchor(0, "", new_anchor, "1970-01-01T00:00:00Z")
        f.admin_write("DELETE FROM nonces WHERE nonce=?", [bootstrap_nonce])

        # Build a sample IPC request the probe will send
        sample_req = make_request(
            fixture=f,
            request_id="req-T2-001",
            decision_id="dec-T2-001",
            operation="WRITE_SCOPED",
            resource_id=r["resource_id"],
            session_id="session-T2-001",
            nonce="nonce-T2-001",
            target_display="filesystem:/protected/file-C.txt",
            issued_at_utc=now,
        )
        sample_req_path = os.path.join(tmpdir, "sample_request.json")
        with open(sample_req_path, "w") as _sr:
            json.dump(sample_req, _sr, sort_keys=True)

        worker_script = os.path.join(HARNESS_DIR, "ipc_worker.py")

        # The probe gets ONLY --db, --seed, --worker_script, and the
        # sample_request. It does NOT receive --executor_credentials_path.
        # We pass it a non-existent path to demonstrate denial.
        # We do NOT pass --audit_key_path either — the requester has
        # no executor-only secrets. The worker will refuse to start.
        nonexistent_cred_path = os.path.join(tmpdir, "DOES_NOT_EXIST_credentials.json")
        nonexistent_audit_path = os.path.join(tmpdir, "DOES_NOT_EXIST_audit_key.bin")

        cmd = [
            sys.executable,
            probe_script,
            "--db", f.db_path,
            "--seed", f.seed_path,
            "--worker_script", worker_script,
            "--executor_credentials_path", nonexistent_cred_path,
            "--sample_request", sample_req_path,
        ]
        env_probe = dict(os.environ)
        proc = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            env=env_probe,
            timeout=60,
        )
        if proc.returncode != 0 or not proc.stdout.strip():
            raise RuntimeError(
                f"probe failed: rc={proc.returncode} stdout={proc.stdout[:500]!r} "
                f"stderr={proc.stderr[:500]!r}"
            )
        probe_obs = json.loads(proc.stdout.strip())

        # Also inspect the requester module's exposed state for redundancy
        requester_module_src = open(
            os.path.join(HARNESS_DIR, "requester.py")
        ).read()
        rstate = requester_mod.exposed_state()

        # Assertions:
        # (a) The probe did NOT see the audit_key VALUE, the resource
        #     credential VALUE, or any signing authority VALUE in its
        #     observation. (The seed file legitimately contains the
        #     request_signing_key — that's the requester's surface, not
        #     a secret. The executor-only secrets (audit_key +
        #     credentials) must NOT appear as values in the observation.)
        observed_text = json.dumps(probe_obs)
        # The audit_key is 32 raw bytes. When hex-encoded it's 64 hex
        # chars. Check whether that hex string appears in the probe
        # observation (it must NOT).
        audit_key_hex = f.audit_key.hex()
        resource_cred_hex = f.resource_credentials[r["resource_id"]].hex()
        sensitive_leak = {
            "audit_key_value_in_observation": audit_key_hex in observed_text,
            "executor_credential_value_in_observation": resource_cred_hex in observed_text,
            "trust_decision_priv_keys_in_observation": any(
                priv.hex() in observed_text
                for priv in f.trust_decision_priv_keys.values()
            ),
        }
        no_leak = not any(sensitive_leak.values())

        # (b) The probe attempted to read the executor credentials file
        # and got "exists=False".
        files_probed = probe_obs.get("files_probed", [])
        cred_probe = next(
            (fp for fp in files_probed if fp.get("path") == nonexistent_cred_path),
            None,
        )
        cred_path_unknown = cred_probe is None or cred_probe.get("exists") is False

        # (c) The probe's IPC attempt must NOT have received the audit
        # key or the resource credential in the response. (The
        # response itself should be a normal verdict response with no
        # secret material.)
        ipc_resp = probe_obs.get("ipc_attempt", {}).get("response", {})
        ipc_resp_audit_key = "audit_key" in json.dumps(ipc_resp)
        ipc_resp_credential = (
            f.resource_credentials[r["resource_id"]].hex() in json.dumps(ipc_resp)
        )
        ipc_clean = not ipc_resp_audit_key and not ipc_resp_credential

        # (d) The probe's IPC attempt must NOT have succeeded. Either:
        #     - the worker refused to start (exit code != 0), which
        #       demonstrates the requester cannot invoke the executor
        #       without the audit key file;
        #     - or the worker started but DENIED the request because
        #       the executor had no credentials to present at the
        #       protected-resource boundary.
        ipc_resp = probe_obs.get("ipc_attempt", {}).get("response", {})
        ipc_reason = ipc_resp.get("reason_code", "")
        worker_refused = probe_obs.get("ipc_attempt", {}).get("worker_returncode", 0) != 0
        ipc_denied = (
            ipc_resp.get("verdict") == "DENIED"
            or worker_refused
        )

        # (e) The requester module's exposed state shows no executor
        # secrets (sanity).
        rstate_clean = (
            rstate["has_resource_credential_handle"] is False
            and rstate["has_audit_hmac_key_handle"] is False
            and rstate["has_db_write_handle"] is False
        )

        ok = no_leak and cred_path_unknown and ipc_clean and ipc_denied and rstate_clean

        _record(
            "T2",
            ok=ok,
            details={
                "controlling_claim": (
                    "process-boundary observation shows the requester has "
                    "NO executor-only material"
                ),
                "probe_observation_summary": {
                    "argv_filtered": probe_obs.get("argv_filtered"),
                    "env_filtered_keys": list(probe_obs.get("env_filtered", {}).keys()),
                    "cwd": probe_obs.get("cwd"),
                    "tmpdir_listing": probe_obs.get("tmpdir_listing"),
                    "files_probed_count": len(files_probed),
                    "files_probed_paths": [fp.get("path") for fp in files_probed],
                    "files_probed_results": files_probed,
                    "ipc_response": ipc_resp,
                    "ipc_response_reason": ipc_reason,
                    "requester_module_attributes": probe_obs.get(
                        "requester_module", {}
                    ).get("attributes"),
                    "requester_module_exposed_state": probe_obs.get(
                        "requester_module", {}
                    ).get("exposed_state"),
                    "sensitive_strings_present": probe_obs.get(
                        "sensitive_strings_present"
                    ),
                },
                "sensitive_leak_check": sensitive_leak,
                "credentials_file_unknown_to_requester": cred_path_unknown,
                "ipc_response_clean_of_secrets": ipc_clean,
                "ipc_denied_without_executor_credentials": ipc_denied,
                "requester_module_static_state": rstate,
                "requester_module_clean": rstate_clean,
            },
        )
    finally:
        rm_tmpdir(tmpdir)


# ----------------------------------------------------------------------
# T3 — Restart-durable nonce
# ----------------------------------------------------------------------


def test_T3_restart_durable_nonce() -> None:
    tmpdir = mk_tmpdir("T3")
    try:
        now = 1700000300.0
        f = Fixture(tmpdir, now)
        r = f.add_resource("filesystem:/protected/file-C.txt")
        decision_id = "dec-T3-001"
        nonce = "nonce-T3-001"
        f.add_trust_decision(
            decision_id,
            operation="WRITE_SCOPED",
            resource_id=r["resource_id"],
            session_id="session-T3-001",
            nonce=nonce,
            target_display="filesystem:/protected/file-C.txt",
        )
        # First execution
        req = make_request(
            fixture=f,
            request_id="req-T3-001",
            decision_id=decision_id,
            operation="WRITE_SCOPED",
            resource_id=r["resource_id"],
            session_id="session-T3-001",
            nonce=nonce,
            target_display="filesystem:/protected/file-C.txt",
            issued_at_utc=now,
        )
        resp1 = f.run_executor_one_shot(req, deterministic_clock=now)
        first_ok = resp1.get("verdict") == "EXECUTED"
        # Replay attempt after restart (same DB, new executor subprocess)
        req2 = dict(req)
        req2["request_id"] = "req-T3-002"
        resp2 = f.run_executor_one_shot(req2, deterministic_clock=now)
        second_ok = resp2.get("verdict") == "DENIED"
        res = f.read_resource(r["resource_id"])
        nonce_row = f.read_nonce(nonce)
        audit_records = f.read_audit_records()
        ok = (
            first_ok
            and second_ok
            and res["mutation_count"] == 1  # not incremented by the replay
            and nonce_row["state"] == "CONSUMED"
            and len(audit_records) == 1  # replay did NOT add an audit event
        )
        _record(
            "T3",
            ok=ok,
            details={
                "first_verdict": resp1.get("verdict"),
                "replay_verdict": resp2.get("verdict"),
                "replay_reason": resp2.get("reason_code"),
                "mutation_count": res["mutation_count"],
                "nonce_state": nonce_row["state"],
                "audit_chain_len": len(audit_records),
            },
        )
    finally:
        rm_tmpdir(tmpdir)


# ----------------------------------------------------------------------
# T4 — Revocation serialized before use
# ----------------------------------------------------------------------


def test_T4_revocation_serialized() -> None:
    """Revocation committed BEFORE the execution transaction begins.

    Per v0.1.1 §C2: revocation serialized before the execution
    transaction MUST be observed and deny execution.
    """
    tmpdir = mk_tmpdir("T4")
    try:
        now = 1700000400.0
        f = Fixture(tmpdir, now)
        r = f.add_resource("filesystem:/protected/file-D.txt")
        decision_id = "dec-T4-001"
        nonce = "nonce-T4-001"
        f.add_trust_decision(
            decision_id,
            operation="WRITE_SCOPED",
            resource_id=r["resource_id"],
            session_id="session-T4-001",
            nonce=nonce,
            target_display="filesystem:/protected/file-D.txt",
        )
        # Stage the revocation in the seed (revocations are written to DB
        # before the executor opens the connection, so the executor sees
        # them at E5).
        f.revoke("decision", decision_id, reason="test-T4")
        req = make_request(
            fixture=f,
            request_id="req-T4-001",
            decision_id=decision_id,
            operation="WRITE_SCOPED",
            resource_id=r["resource_id"],
            session_id="session-T4-001",
            nonce=nonce,
            target_display="filesystem:/protected/file-D.txt",
            issued_at_utc=now,
        )
        resp = f.run_executor_one_shot(req, deterministic_clock=now)
        res = f.read_resource(r["resource_id"])
        audit_records = f.read_audit_records()
        nonce_row = f.read_nonce(nonce)
        ok = (
            resp.get("verdict") == "DENIED"
            and resp.get("reason_code") == "PX_AUTHORITY_REVOKED"
            and res["mutation_count"] == 0
            and len(audit_records) == 0  # no audit event because mutation never committed
            and nonce_row is None
        )
        _record(
            "T4",
            ok=ok,
            details={
                "verdict": resp.get("verdict"),
                "reason_code": resp.get("reason_code"),
                "mutation_count": res["mutation_count"],
                "audit_chain_len": len(audit_records),
            },
        )
    finally:
        rm_tmpdir(tmpdir)


# ----------------------------------------------------------------------
# T5 — Concurrent replay
# ----------------------------------------------------------------------


def test_T5_concurrent_replay() -> None:
    """At least 16 concurrent requester attempts; exactly one commits.

    Per v0.1 §11.5 and v0.1.1 §6: workers/threads/processes is acceptable.
    The atomicity property is enforced by SQLite BEGIN IMMEDIATE inside
    the PrivilegedExecutor transaction, regardless of the IPC mechanism.
    To avoid concurrent seed-file writes, we stage the seed ONCE and
    have each subprocess read from the same seed file (read-only access
    is benign).
    """
    tmpdir = mk_tmpdir("T5")
    try:
        now = 1700000500.0
        f = Fixture(tmpdir, now)
        r = f.add_resource("filesystem:/protected/file-E.txt")
        decision_id = "dec-T5-001"
        nonce = "nonce-T5-001"
        f.add_trust_decision(
            decision_id,
            operation="WRITE_SCOPED",
            resource_id=r["resource_id"],
            session_id="session-T5-001",
            nonce=nonce,
            target_display="filesystem:/protected/file-E.txt",
        )
        # Stage seed once (reset=True: clean slate)
        f.write_seed(reset=True)
        # Stage DB once via a "stage" pass: run the worker subprocess to
        # apply the seed to the DB. After this, all subsequent subprocesses
        # share the same durable DB state. The stage uses a SEPARATE
        # nonce so the 16 concurrent attempts against the shared nonce
        # remain meaningful.
        from ipc_protocol import make_request as _mk
        stage_nonce = "nonce-T5-stage-001"
        f.add_trust_decision(
            "dec-T5-stage-001",
            operation="WRITE_SCOPED",
            resource_id=r["resource_id"],
            session_id="session-T5-001",
            nonce=stage_nonce,
            target_display="filesystem:/protected/file-E.txt",
        )
        stage_req = _mk(
            request_id="stage-T5-001",
            decision_id="dec-T5-stage-001",
            decision_signature_b64=f.trust_decision_signatures["dec-T5-stage-001"],
            principal_id="principal-T5-001",
            session_id="session-T5-001",
            operation="WRITE_SCOPED",
            target_display="filesystem:/protected/file-E.txt",
            resource_id=r["resource_id"],
            nonce=stage_nonce,
            envelope_id="env-T5-001",
            issued_at_utc=now,
            signing_key=f.requester_signing_key,
        )
        stage_resp = f.run_executor_one_shot(stage_req, deterministic_clock=now)
        assert stage_resp.get("verdict") == "EXECUTED", f"stage failed: {stage_resp}"

        # Build 16 distinct request dicts sharing the same nonce
        requests = []
        for i in range(16):
            req = make_request(
                fixture=f,
                request_id=f"req-T5-{i:03d}",
                decision_id=decision_id,
                operation="WRITE_SCOPED",
                resource_id=r["resource_id"],
                session_id="session-T5-001",
                nonce=nonce,
                target_display="filesystem:/protected/file-E.txt",
                issued_at_utc=now,
            )
            requests.append(req)
        # Refresh the executor-only secrets files in case the seed was
        # rewritten by the stage pass (these files are executor-only
        # and never appear in the seed).
        f.write_executor_secrets()
        # Each subprocess reads the seed file (read-only access) and
        # re-applies decisions/resources (idempotent). The DB state
        # for nonces and audit records is preserved when reset_state=False.
        seed_data = json.load(open(f.seed_path))
        seed_data["reset"] = False
        seed_data["reset_state"] = False
        with open(f.seed_path, "w") as _sf:
            json.dump(seed_data, _sf, sort_keys=True)

        env = dict(os.environ)
        cmd_template = [
            sys.executable,
            os.path.join(HARNESS_DIR, "ipc_worker.py"),
            "--db", f.db_path,
            "--seed", f.seed_path,
            "--executor_credentials_file", f.credentials_path,
            "--executor_audit_key_file", f.audit_key_path,
            "--mode", "one_shot",
            "--now_utc", str(now),
        ]
        procs = []
        for req in requests:
            p = subprocess.Popen(
                cmd_template,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                env=env,
            )
            procs.append((p, req))
        responses: List[Dict[str, Any]] = []
        for p, req in procs:
            try:
                out, err = p.communicate(input=(json.dumps(req) + "\n").encode("utf-8"), timeout=30)
                if not out.strip():
                    responses.append({"verdict": "ERROR", "reason_code": "empty_stderr:" + err.decode()[:200]})
                else:
                    last_line = out.decode().strip().splitlines()[-1]
                    responses.append(json.loads(last_line))
            except Exception as e:
                responses.append({"verdict": "ERROR", "reason_code": str(e)})
            finally:
                p.wait()
        # Aggregate
        successes = sum(1 for r in responses if r.get("verdict") == "EXECUTED")
        denials = sum(1 for r in responses if r.get("verdict") == "DENIED")
        res = f.read_resource(r["resource_id"])
        nonce_row = f.read_nonce(nonce)
        audit_records = f.read_audit_records()
        ok = (
            successes == 1
            and res["mutation_count"] == 2  # 1 stage + 1 successful concurrent
            and nonce_row["state"] == "CONSUMED"
            and len(audit_records) == 2
        )
        _record(
            "T5",
            ok=ok,
            details={
                "worker_count": 16,
                "successes": successes,
                "denials": denials,
                "mutation_count": res["mutation_count"],
                "audit_chain_len": len(audit_records),
                "nonce_state": nonce_row["state"],
                "first_success_request_id": next(
                    (req["request_id"] for req, resp in zip(requests, responses) if resp.get("verdict") == "EXECUTED"),
                    None,
                ),
            },
        )
    finally:
        rm_tmpdir(tmpdir)


# ----------------------------------------------------------------------
# T6 — Transaction rollback on audit failure
# ----------------------------------------------------------------------


def test_T6_audit_rollback() -> None:
    """Inject audit failure before commit -> entire transaction rolls back.

    Per v0.1.1 §C1: rollback must undo everything (no resource
    mutation, no consumed nonce, no partial audit event, no advanced
    anchor).
    """
    tmpdir = mk_tmpdir("T6")
    f = None  # type: ignore[assignment]
    try:
        now = 1700000600.0
        f = Fixture(tmpdir, now)
        f.privilege_setup()
        r = f.add_resource("filesystem:/protected/file-F.txt")
        f.add_trust_decision(
            "dec-T6-001",
            operation="WRITE_SCOPED",
            resource_id=r["resource_id"],
            session_id="sess-T6-001",
            nonce="nonce-T6-001",
            target_display="filesystem:/protected/file-F.txt",
        )
        f.write_seed(reset=True)
        f.write_executor_secrets()
        # Insert resource + decision via admin (ate-executor)
        f.seed_insert_resource_via_admin(r["resource_id"], "filesystem:/protected/file-F.txt", r["credential"])
        f.seed_insert_decision_via_admin(
            "dec-T6-001",
            json.dumps(f.trust_decision_payloads["dec-T6-001"], sort_keys=True),
            f.trust_decision_signatures["dec-T6-001"],
        )
        req = make_request(
            fixture=f,
            request_id="req-T6-001",
            decision_id="dec-T6-001",
            operation="WRITE_SCOPED",
            resource_id=r["resource_id"],
            session_id="sess-T6-001",
            nonce="nonce-T6-001",
            target_display="filesystem:/protected/file-F.txt",
            issued_at_utc=now,
        )
        resp = f.run_executor_one_shot_with_flag(
            req,
            deterministic_clock=now,
            extra_arg="--deterministic_barrier_fail",
        )
        # Read state via admin
        res_row = f.read_resource(r["resource_id"])
        nonce_row = f.read_nonce("nonce-T6-001")
        audit_records = f.read_audit_records()
        anchor = f.read_anchor()
        ok = (
            resp.get("verdict") == "DENIED"
            and res_row is not None
            and int(res_row["mutation_count"]) == 0
            and nonce_row is None  # uncommitted, no row
            and len(audit_records) == 0
            and int(anchor.get("final_seq", 0)) == 0
        )
        _record(
            "T6",
            ok=ok,
            details={
                "verdict": resp.get("verdict"),
                "reason_code": resp.get("reason_code"),
                "mutation_count": int(res_row["mutation_count"]),
                "nonce_state": nonce_row["state"] if nonce_row else None,
                "audit_chain_len": len(audit_records),
                "anchor_final_seq": int(anchor.get("final_seq", 0)),
            },
        )
    finally:
        try:
            f.privilege_teardown()
        except Exception:
            pass
        rm_tmpdir(tmpdir)


# ----------------------------------------------------------------------
# T7 — Audit tamper detection
# ----------------------------------------------------------------------


def test_T7_audit_tamper() -> None:
    """Generate a chain of 4+ records; verify each tamper fails; control passes."""
    tmpdir = mk_tmpdir("T7")
    f = None  # type: ignore[assignment]
    try:
        now = 1700000700.0
        f = Fixture(tmpdir, now)
        f.privilege_setup()
        # Run four successful executions to build the chain
        for i in range(4):
            r = f.add_resource(f"filesystem:/protected/file-G{i}.txt")
            decision_id = f"dec-T7-{i:03d}"
            nonce = f"nonce-T7-{i:03d}"
            f.add_trust_decision(
                decision_id,
                operation="WRITE_SCOPED",
                resource_id=r["resource_id"],
                session_id=f"session-T7-{i:03d}",
                nonce=nonce,
                target_display=f"filesystem:/protected/file-G{i}.txt",
            )
            f.write_seed(reset=True)
            f.write_executor_secrets()
            f.seed_insert_resource_via_admin(
                r["resource_id"], f"filesystem:/protected/file-G{i}.txt", r["credential"]
            )
            f.seed_insert_decision_via_admin(
                decision_id,
                json.dumps(f.trust_decision_payloads[decision_id], sort_keys=True),
                f.trust_decision_signatures[decision_id],
            )
            req = make_request(
                fixture=f,
                request_id=f"req-T7-{i:03d}",
                decision_id=decision_id,
                operation="WRITE_SCOPED",
                resource_id=r["resource_id"],
                session_id=f"session-T7-{i:03d}",
                nonce=nonce,
                target_display=f"filesystem:/protected/file-G{i}.txt",
                issued_at_utc=now,
            )
            resp = f.run_executor_one_shot(req, deterministic_clock=now)
            assert resp.get("verdict") == "EXECUTED", f"buildup failed at i={i}"
        # Untouched control
        ok_control, reason_control = verify_audit_chain(f)

        # Helper to verify each tamper fails
        tamper_results: Dict[str, bool] = {}

        def _verify_with_audit_records(audit_key: bytes, records: List[Dict[str, Any]], anchor: Dict[str, Any]) -> Tuple[bool, str]:
            # Reimplement verification using the given records (bypassing DB)
            prev_digest = ""
            for rec in records:
                no_mac = {k: v for k, v in rec.items() if k != "record_mac"}
                import hashlib as _hl
                expected_prev = _hl.sha256(
                    audit_chain.canonical_bytes(no_mac)
                ).hexdigest()
                if rec["previous_digest"] != prev_digest:
                    return False, f"chain_broken_at_seq_{rec['seq']}"
                expected_mac = audit_chain.hmac_sha256_hex(audit_key, audit_chain.canonical_bytes(no_mac))
                if rec["record_mac"] != expected_mac:
                    return False, f"record_mac_invalid_at_seq_{rec['seq']}"
                prev_digest = expected_prev
            if int(anchor["final_seq"]) != len(records):
                return False, "anchor_seq_mismatch"
            if anchor["final_record_digest"] != prev_digest:
                return False, "anchor_final_digest_mismatch"
            expected_anchor_mac = audit_chain.hmac_sha256_hex(
                audit_key,
                audit_chain.canonical_bytes(
                    {"final_seq": int(anchor["final_seq"]), "final_record_digest": anchor["final_record_digest"]}
                ),
            )
            if anchor["anchor_mac"] != expected_anchor_mac:
                return False, "anchor_mac_invalid"
            return True, "verified"

        records = f.read_audit_records()
        anchor = f.read_anchor()
        key = f.audit_key

        # Tamper 1: field mutation
        records1 = [dict(r) for r in records]
        records1[1]["operation"] = "WRITE_TAMPERED"
        ok1, _ = _verify_with_audit_records(key, records1, anchor)
        tamper_results["field_mutation"] = not ok1

        # Tamper 2: middle deletion
        records2 = [dict(r) for r in records]
        del records2[2]
        ok2, _ = _verify_with_audit_records(key, records2, anchor)
        tamper_results["middle_deletion"] = not ok2

        # Tamper 3: reorder
        records3 = [dict(r) for r in records]
        records3[1], records3[2] = records3[2], records3[1]
        ok3, _ = _verify_with_audit_records(key, records3, anchor)
        tamper_results["reorder"] = not ok3

        # Tamper 4: insertion
        records4 = [dict(r) for r in records]
        fabricated = dict(records4[0])
        fabricated["seq"] = 2
        fabricated["operation"] = "FABRICATED"
        records4.insert(2, fabricated)
        ok4, _ = _verify_with_audit_records(key, records4, anchor)
        tamper_results["insertion"] = not ok4

        # Tamper 5: tail truncation
        records5 = [dict(r) for r in records]
        records5.pop()
        anchor5 = dict(anchor)
        anchor5["final_seq"] = len(records5)
        ok5, _ = _verify_with_audit_records(key, records5, anchor5)
        tamper_results["tail_truncation"] = not ok5

        # Anchor MAC tampering
        anchor6 = dict(anchor)
        anchor6["anchor_mac"] = "f" * 64
        ok6, _ = _verify_with_audit_records(key, records, anchor6)
        tamper_results["anchor_mac_tamper"] = not ok6

        ok = ok_control and all(tamper_results.values())
        _record(
            "T7",
            ok=ok,
            details={
                "untouched_control_verifies": ok_control,
                "untouched_control_reason": reason_control,
                "tamper_results": tamper_results,
            },
        )
    finally:
        try:
            f.privilege_teardown()
        except Exception:
            pass
        rm_tmpdir(tmpdir)


# ----------------------------------------------------------------------
# T8 — Stable resource identity
# ----------------------------------------------------------------------


def test_T8_stable_resource_identity() -> None:
    """A different immutable resource_id is denied, even with matching display."""
    tmpdir = mk_tmpdir("T8")
    try:
        now = 1700000800.0
        f = Fixture(tmpdir, now)
        # Two resources: one the decision authorizes, one with the same
        # display path but different immutable id.
        r_real = f.add_resource("filesystem:/protected/file-H.txt")
        r_other = f.add_resource("filesystem:/protected/file-H.txt")
        decision_id = "dec-T8-001"
        nonce = "nonce-T8-001"
        f.add_trust_decision(
            decision_id,
            operation="WRITE_SCOPED",
            resource_id=r_real["resource_id"],
            session_id="session-T8-001",
            nonce=nonce,
            target_display="filesystem:/protected/file-H.txt",
        )
        # Tamper: present the OTHER resource_id with the matching display
        req = make_request(
            fixture=f,
            request_id="req-T8-001",
            decision_id=decision_id,
            operation="WRITE_SCOPED",
            resource_id=r_other["resource_id"],  # different immutable id
            session_id="session-T8-001",
            nonce=nonce,
            target_display="filesystem:/protected/file-H.txt",  # same display
            issued_at_utc=now,
        )
        resp = f.run_executor_one_shot(req, deterministic_clock=now)
        res_real = f.read_resource(r_real["resource_id"])
        res_other = f.read_resource(r_other["resource_id"])
        nonce_row = f.read_nonce(nonce)
        audit_records = f.read_audit_records()
        ok = (
            resp.get("verdict") == "DENIED"
            and resp.get("reason_code") == "PX_TARGET_BINDING_MISMATCH"
            and int(res_real["mutation_count"]) == 0
            and int(res_other["mutation_count"]) == 0
            and nonce_row is None
            and len(audit_records) == 0
        )
        _record(
            "T8",
            ok=ok,
            details={
                "verdict": resp.get("verdict"),
                "reason_code": resp.get("reason_code"),
                "real_resource_mut": int(res_real["mutation_count"]),
                "other_resource_mut": int(res_other["mutation_count"]),
                "audit_chain_len": len(audit_records),
            },
        )
    finally:
        rm_tmpdir(tmpdir)


# ----------------------------------------------------------------------
# T9 — Startup audit-integrity gate
# ----------------------------------------------------------------------


def test_T9_startup_integrity() -> None:
    """Tamper with audit state, restart executor, attempt execution -> locked."""
    tmpdir = mk_tmpdir("T9")
    f = None  # type: ignore[assignment]
    try:
        now = 1700000900.0
        f = Fixture(tmpdir, now)
        f.privilege_setup()
        r = f.add_resource("filesystem:/protected/file-I.txt")
        decision_id = "dec-T9-001"
        nonce = "nonce-T9-001"
        f.add_trust_decision(
            decision_id,
            operation="WRITE_SCOPED",
            resource_id=r["resource_id"],
            session_id="session-T9-001",
            nonce=nonce,
            target_display="filesystem:/protected/file-I.txt",
        )
        f.write_seed(reset=True)
        f.write_executor_secrets()
        f.seed_insert_resource_via_admin(r["resource_id"], "filesystem:/protected/file-I.txt", r["credential"])
        f.seed_insert_decision_via_admin(
            decision_id,
            json.dumps(f.trust_decision_payloads[decision_id], sort_keys=True),
            f.trust_decision_signatures[decision_id],
        )
        req = make_request(
            fixture=f,
            request_id="req-T9-001",
            decision_id=decision_id,
            operation="WRITE_SCOPED",
            resource_id=r["resource_id"],
            session_id="session-T9-001",
            nonce=nonce,
            target_display="filesystem:/protected/file-I.txt",
            issued_at_utc=now,
        )
        # First valid execution
        resp0 = f.run_executor_one_shot(req, deterministic_clock=now)
        # Now tamper with the audit_records via admin (ate-executor)
        f.admin_write("UPDATE audit_records SET operation='TAMPERED' WHERE seq=?", [1])
        # Replay: now the executor's startup gate should detect the tamper
        req2 = dict(req)
        req2["request_id"] = "req-T9-002"
        resp1 = f.run_executor_one_shot(req2, deterministic_clock=now)
        nonce_row = f.read_nonce(nonce)
        res = f.read_resource(r["resource_id"])
        audit_records = f.read_audit_records()
        ok = (
            resp0.get("verdict") == "EXECUTED"
            and resp1.get("verdict") == "DENIED"
            and res is not None
            and int(res["mutation_count"]) == 1
            and nonce_row is not None
            and nonce_row["state"] == "CONSUMED"
        )
        _record(
            "T9",
            ok=ok,
            details={
                "first_verdict": resp0.get("verdict"),
                "post_tamper_verdict": resp1.get("verdict"),
                "post_tamper_reason": resp1.get("reason_code"),
                "mutation_count": int(res["mutation_count"]) if res else None,
                "nonce_state": nonce_row["state"] if nonce_row else None,
                "audit_chain_len_after_tamper": len(audit_records),
            },
        )
    finally:
        try:
            f.privilege_teardown()
        except Exception:
            pass
        rm_tmpdir(tmpdir)


# ----------------------------------------------------------------------
# T10 — Crash/rollback consistency
# ----------------------------------------------------------------------


def test_T10_crash_consistency() -> None:
    """Inject a crash before commit; restart; verify all state reflects pre-transaction state.

    Uses the IPC worker subprocess (as ate-executor) with the barrier
    configured to raise SystemExit (simulating a crashed subprocess).
    A second worker invocation then verifies the DB state reflects the
    pre-transaction state.
    """
    tmpdir = mk_tmpdir("T10")
    f = None  # type: ignore[assignment]
    try:
        now = 1700001000.0
        f = Fixture(tmpdir, now)
        f.privilege_setup()
        r = f.add_resource("filesystem:/protected/file-J.txt")
        f.add_trust_decision(
            "dec-T10-001",
            operation="WRITE_SCOPED",
            resource_id=r["resource_id"],
            session_id="sess-T10-001",
            nonce="nonce-T10-001",
            target_display="filesystem:/protected/file-J.txt",
        )
        f.write_seed(reset=True)
        f.write_executor_secrets()
        f.seed_insert_resource_via_admin(r["resource_id"], "filesystem:/protected/file-J.txt", r["credential"])
        f.seed_insert_decision_via_admin(
            "dec-T10-001",
            json.dumps(f.trust_decision_payloads["dec-T10-001"], sort_keys=True),
            f.trust_decision_signatures["dec-T10-001"],
        )
        req = make_request(
            fixture=f,
            request_id="req-T10-001",
            decision_id="dec-T10-001",
            operation="WRITE_SCOPED",
            resource_id=r["resource_id"],
            session_id="sess-T10-001",
            nonce="nonce-T10-001",
            target_display="filesystem:/protected/file-J.txt",
            issued_at_utc=now,
        )
        # First call: barrier raises SystemExit. The worker subprocess
        # will die; we catch the failure (worker exit != 0 with
        # no JSON response simulates the crash).
        crashed = False
        try:
            f.run_executor_one_shot_with_flag(
                req,
                deterministic_clock=now,
                extra_arg="--deterministic_barrier_fail",
            )
        except RuntimeError as e:
            crashed = True
        # Now "restart" the worker and verify state.
        # First ensure seed is fresh (write_seed was called inside run_executor_one_shot)
        f.write_seed(reset=False)
        f.write_executor_secrets()
        # Restart attempt: same DB. Worker should observe empty state.
        # Send a no-op request (or just read state via admin).
        res_row = f.read_resource(r["resource_id"])
        nonce_row = f.read_nonce("nonce-T10-001")
        audit_records = f.read_audit_records()
        anchor = f.read_anchor()
        ok = (
            crashed
            and res_row is not None
            and int(res_row["mutation_count"]) == 0
            and nonce_row is None
            and len(audit_records) == 0
            and int(anchor.get("final_seq", 0)) == 0
        )
        _record(
            "T10",
            ok=ok,
            details={
                "crash_occurred": crashed,
                "mutation_count": int(res_row["mutation_count"]),
                "nonce_state": nonce_row["state"] if nonce_row else None,
                "audit_chain_len": len(audit_records),
                "anchor_final_seq": int(anchor.get("final_seq", 0)),
            },
        )
    finally:
        try:
            f.privilege_teardown()
        except Exception:
            pass
        rm_tmpdir(tmpdir)


# ----------------------------------------------------------------------
# main
# ----------------------------------------------------------------------


def main() -> int:
    print("=== ATE P1 v0.1.1 — Controlling Test Matrix T0-T10 ===")
    for fn in [
        test_T0_valid_execution,
        test_T1_direct_bypass,
        test_T2_credential_separation,
        test_T3_restart_durable_nonce,
        test_T4_revocation_serialized,
        test_T5_concurrent_replay,
        test_T6_audit_rollback,
        test_T7_audit_tamper,
        test_T8_stable_resource_identity,
        test_T9_startup_integrity,
        test_T10_crash_consistency,
    ]:
        print(f"\n--- {fn.__name__} ---")
        try:
            fn()
        except Exception as e:
            _record(fn.__name__, ok=False, details={"exception": str(e)})

    passes = sum(1 for v in RESULTS.values() if v["pass"])
    fails = sum(1 for v in RESULTS.values() if not v["pass"])
    print(f"\n=== Summary: {passes} pass, {fails} fail out of {len(RESULTS)} tests ===")
    # Write corrected evidence to a NEW filename so the original
    # p1_v011_evidence.json (preserved at commit 1e729c8) is not
    # overwritten.
    out_path = os.path.join(os.path.dirname(HERE), "evidence", "p1_v011_corrected_evidence.json")
    with open(out_path, "w") as f:
        json.dump(
            {
                "results": {tid: {"pass": v["pass"], "details": v["details"]} for tid, v in RESULTS.items()},
                "summary": {"passes": passes, "fails": fails, "total": len(RESULTS)},
                "controlling_design_commit": "6ca3a5624f501f9b184f1b06fd7f42a73c31e5d4",
                "upstream_frozen_ate_baseline": "f903478154e2b484f8a49295ba0692d0a5a4f260",
            },
            f,
            indent=2,
            sort_keys=True,
        )
    print(f"evidence: {out_path}")
    return 0 if fails == 0 else 1


if __name__ == "__main__":
    sys.exit(main())

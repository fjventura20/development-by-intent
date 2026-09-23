"""ATE P1 v0.1.1 — test fixtures and helpers.

OS-level privilege boundary:

  The authority DB is owned by the OS user `ate-executor` with mode
  0600, in a directory owned by `ate-executor` with mode 0700. The
  unprivileged test-process user (the requester side) has NO access
  to the DB path or file. The DB is created, bootstrapped, and read
  only via the `db_admin.py` helper, which runs as `ate-executor`
  via `sudo -u ate-executor`.

  The IPC worker (`ipc_worker.py`) also runs as `ate-executor` via
  sudo. The worker reads the seed (requester-visible), the executor
  credentials file (mode 0600, owned by `ate-executor`), and the
  audit key file (mode 0600, owned by `ate-executor`).

  Per-test scaffolding:
    - temp directory per test
    - authority DB reset (via db_admin as ate-executor)
    - fixture keys (audit HMAC, request signing, decision public keys)
    - protected resources with credentials
    - trust-decision signing helper
"""
from __future__ import annotations

import base64
import datetime
import hashlib
import hmac
import json
import os
import secrets
import shutil
import sqlite3
import subprocess
import sys
import tempfile
import time
from typing import Any, Dict, List, Optional, Tuple

from crypto_utils import canonical_bytes, fingerprint_obj, random_hex


HERE = os.path.dirname(os.path.abspath(__file__))
WORKER_SCRIPT = os.path.abspath(os.path.join(HERE, "..", "implementation_v011", "ipc_worker.py"))
DB_ADMIN_SCRIPT = os.path.abspath(os.path.join(HERE, "db_admin.py"))
EXECUTOR_OS_USER = "ate-executor"


def _sudo_run_as_executor(argv: List[str], *, timeout: float = 30.0) -> subprocess.CompletedProcess:
    """Run a command as the ate-executor user via sudo."""
    cmd = ["sudo", "-u", EXECUTOR_OS_USER, "-H", "--"] + argv
    return subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        timeout=timeout,
    )


class DBAdminClient:
    """Long-lived client to a `db_admin.py` process running as
    ate-executor. Sends one command, reads one response.
    """

    def __init__(self, db_path: str, db_admin_script: Optional[str] = None, pythonpath: Optional[str] = None):
        self.db_path = db_path
        script = db_admin_script or DB_ADMIN_SCRIPT
        # Find pythonpath: the priv impl dir is the dir containing the script's
        # sibling `implementation_v011/`.
        if pythonpath is None:
            pythonpath = os.path.dirname(script)
        self.proc = subprocess.Popen(
            ["sudo", "-u", EXECUTOR_OS_USER, "-H", "--",
             "env", f"PYTHONPATH={pythonpath}",
             sys.executable, script, "--db", db_path],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
        )

    def call(self, cmd: Dict[str, Any]) -> Dict[str, Any]:
        self.proc.stdin.write(json.dumps(cmd) + "\n")
        self.proc.stdin.flush()
        line = self.proc.stdout.readline()
        if not line:
            err = self.proc.stderr.read()
            raise RuntimeError(f"db_admin died: stderr={err[:500]}")
        return json.loads(line.strip())

    def close(self) -> None:
        try:
            self.proc.stdin.write("__shutdown__\n")
            self.proc.stdin.flush()
        except Exception:
            pass
        try:
            self.proc.wait(timeout=5)
        except Exception:
            self.proc.kill()


class Fixture:
    """Bundles all per-test state.

    The DB is created and operated on by a DBAdminClient (running as
    ate-executor via sudo). The fixture does NOT hold a DB handle
    itself.
    """

    def __init__(self, tmpdir: str, now_utc: float):
        self.tmpdir = tmpdir
        self.now_utc = now_utc
        self.db_path = os.path.join(tmpdir, "authority.sqlite")
        self.seed_path = os.path.join(tmpdir, "seed.json")
        self.credentials_path = os.path.join(tmpdir, "executor_credentials.json")
        self.audit_key_path = os.path.join(tmpdir, "executor_audit_key.bin")
        # Fixture keys
        self.audit_key = secrets.token_bytes(32)
        self.request_signing_key = secrets.token_bytes(32)
        self.resource_credentials: Dict[str, bytes] = {}
        self.trust_decision_priv_keys: Dict[str, bytes] = {}
        self.trust_decision_pub_keys: Dict[str, bytes] = {}
        self.trust_decision_payloads: Dict[str, Dict[str, Any]] = {}
        self.trust_decision_signatures: Dict[str, str] = {}
        self.resources: List[Dict[str, Any]] = []
        self.revocations: List[Dict[str, Any]] = []
        self.requester_signing_key = self.request_signing_key
        self.db_admin: Optional[DBAdminClient] = None

    # ---------- Privileged OS-level setup ----------

    def privilege_setup(self) -> None:
        """Set up OS-level privilege boundary.

        Layout of the test tmpdir after privilege_setup:

          tmpdir/                     (parent:parent, mode 0755) -
                                       ate-executor must be able to
                                       TRAVERSE to reach the DB file.
            authority.sqlite         (ate-executor:users, mode 0600)
            executor_credentials.json (ate-executor:users, mode 0600)
            executor_audit_key.bin   (ate-executor:users, mode 0600)
            priv/                     (ate-executor:users, mode 0700) -
                                       contains the priv copy of harness
                                       modules.
            seed.json                 (parent:parent, mode 0644) -
                                       requester-visible; ate-executor
                                       must read it as the worker.
            sample_request.json       (parent:parent, mode 0644) -
                                       T2 artifact.

        The DB file is created (and initialized) by the parent, then
        chowned to ate-executor with mode 0600. The priv/ subdir is
        chowned to ate-executor with mode 0700 — ate-executor reads
        the harness modules from there.
        """
        # Make tmpdir traversable by ate-executor
        try:
            os.chmod(self.tmpdir, 0o755)
        except Exception:
            pass
        # Pre-create the DB file as the parent (so we control the
        # initial ownership) and initialize the schema via a brief
        # in-process open_db call. Then chown the file (and any
        # auxiliary -journal files) to ate-executor.
        from authority_db import open_db as _open_db
        conn = _open_db(self.db_path)
        conn.close()
        # Now chown the DB (and any journal sidecar) to ate-executor:users, mode 0600
        for path in [
            self.db_path,
            self.db_path + "-journal",
        ]:
            if os.path.exists(path):
                subprocess.run(
                    ["sudo", "-n", "chown", f"{EXECUTOR_OS_USER}:users", path],
                    check=True,
                )
                subprocess.run(
                    ["sudo", "-n", "chmod", "0600", path],
                    check=True,
                )
        # Copy harness modules into the tmpdir's priv/ subdir
        priv_dir = os.path.join(self.tmpdir, "priv")
        os.makedirs(priv_dir, exist_ok=True)
        impl_dir = os.path.join(priv_dir, "implementation_v011")
        os.makedirs(impl_dir, exist_ok=True)
        # Copy implementation_v011 files
        import shutil
        src_impl = os.path.abspath(os.path.join(HERE, "..", "implementation_v011"))
        for name in os.listdir(src_impl):
            if name.endswith(".py"):
                shutil.copy(
                    os.path.join(src_impl, name),
                    os.path.join(impl_dir, name),
                )
        # Copy db_admin.py
        shutil.copy(
            os.path.join(HERE, "db_admin.py"),
            os.path.join(priv_dir, "db_admin.py"),
        )
        self._priv_impl_dir = impl_dir
        self._priv_dir = priv_dir
        # chown priv/ to ate-executor:users, mode 0700
        subprocess.run(
            ["sudo", "-n", "chown", "-R", f"{EXECUTOR_OS_USER}:users", priv_dir],
            check=True,
        )
        subprocess.run(
            ["sudo", "-n", "chmod", "-R", "u+rwX,g-rwx,o-rwx", priv_dir],
            check=True,
        )
        # Open DB admin client (runs as ate-executor); use the priv copy
        # of db_admin.py so the subprocess can read it.
        priv_db_admin = os.path.join(self._priv_dir, "db_admin.py")
        self.db_admin = DBAdminClient(
            self.db_path,
            db_admin_script=priv_db_admin,
            pythonpath=self._priv_impl_dir,
        )
        # Sanity check: parent process cannot open the DB.
        # (This is the OS-level boundary the design requires.)
        import sqlite3 as _sqlite3
        try:
            _test_conn = _sqlite3.connect(self.db_path, timeout=2.0)
            _test_conn.execute("SELECT 1").fetchone()
            _test_conn.close()
            raise RuntimeError(
                f"OS-LEVEL PRIVILEGE BOUNDARY VIOLATED: parent could open "
                f"{self.db_path}; the file is not properly permission-isolated."
            )
        except _sqlite3.OperationalError:
            pass  # expected: parent cannot open the DB
        except PermissionError:
            pass  # expected
        # Bootstrap schema (idempotent: init_schema runs CREATE IF NOT EXISTS)
        resp = self.db_admin.call({"cmd": "bootstrap"})
        if not resp.get("ok"):
            raise RuntimeError(f"db_admin bootstrap failed: {resp}")

    def privilege_teardown(self) -> None:
        if self.db_admin is not None:
            self.db_admin.close()
            self.db_admin = None

    def seed_insert_resource_via_admin(self, resource_id: str, display_path: str, credential: bytes) -> None:
        resp = self.db_admin.call({
            "cmd": "exec_insert_resource",
            "resource_id": resource_id,
            "display_path": display_path,
            "credential_hex": credential.hex(),
        })
        if not resp.get("ok"):
            raise RuntimeError(f"exec_insert_resource failed: {resp}")

    def seed_insert_decision_via_admin(self, decision_id: str, signed_payload_json: str, signature_b64: str) -> None:
        resp = self.db_admin.call({
            "cmd": "exec_insert_decision",
            "decision_id": decision_id,
            "signed_payload_json": signed_payload_json,
            "signature_b64": signature_b64,
        })
        if not resp.get("ok"):
            raise RuntimeError(f"exec_insert_decision failed: {resp}")

    def admin_update_resource_for_bootstrap_rollback(self, resource_id: str, state_json: str) -> None:
        resp = self.db_admin.call({
            "cmd": "update_resource_for_bootstrap_rollback",
            "resource_id": resource_id,
            "state_json": state_json,
        })
        if not resp.get("ok"):
            raise RuntimeError(f"update_resource_for_bootstrap_rollback failed: {resp}")

    def admin_delete_audit_records(self, request_id: str) -> None:
        resp = self.db_admin.call({"cmd": "delete_audit_records", "request_id": request_id})
        if not resp.get("ok"):
            raise RuntimeError(f"delete_audit_records failed: {resp}")

    def admin_update_anchor(self, final_seq: int, final_record_digest: str, anchor_mac: str, updated_at: str) -> None:
        resp = self.db_admin.call({
            "cmd": "update_anchor",
            "final_seq": final_seq,
            "final_record_digest": final_record_digest,
            "anchor_mac": anchor_mac,
            "updated_at": updated_at,
        })
        if not resp.get("ok"):
            raise RuntimeError(f"update_anchor failed: {resp}")

    def admin_raw_sql(self, sql: str, params: Optional[List[Any]] = None) -> List[Dict[str, Any]]:
        resp = self.db_admin.call({
            "cmd": "raw_execute_sql",
            "sql": sql,
            "params": params or [],
        })
        if "_error" in resp:
            raise RuntimeError(f"raw_execute_sql failed: {resp}")
        return resp.get("result") or []

    def admin_write(
        self,
        sql: str,
        params: Optional[List[Any]] = None,
    ) -> int:
        """Execute a write SQL via db_admin. Returns rows affected."""
        rows = self.admin_raw_sql(sql, params)
        # For INSERT/UPDATE/DELETE, raw_execute_sql returns empty list;
        # we can't get rowcount reliably via SELECT.
        # Use a separate response field.
        resp = self.db_admin.call({
            "cmd": "write_sql",
            "sql": sql,
            "params": params or [],
        })
        if "_error" in resp:
            raise RuntimeError(f"write_sql failed: {resp}")
        return int(resp.get("rowcount", 0))

    # ---------- Requester-side helpers (no DB access) ----------

    def add_resource(self, display_path: str) -> Dict[str, Any]:
        rid = random_hex(16)
        cred = secrets.token_bytes(32)
        self.resources.append({
            "resource_id": rid,
            "display_path": display_path,
        })
        self.resource_credentials[rid] = cred
        return {"resource_id": rid, "credential": cred}

    def add_trust_decision(
        self,
        decision_id: str,
        *,
        operation: str,
        resource_id: str,
        session_id: str,
        nonce: str,
        target_display: str = "",
    ) -> str:
        priv = secrets.token_bytes(32)
        pub = secrets.token_bytes(32)
        # The requester-side fixture does NOT use a real private key
        # for trust-decision signing; it just stores pub/sig for the
        # worker to verify. The "priv" here is unused placeholder.
        self.trust_decision_pub_keys[decision_id] = pub
        payload = {
            "operation": operation,
            "resource_id": resource_id,
            "session_id": session_id,
            "nonce": nonce,
            "target_display": target_display or f"display:{resource_id}",
            "issued_at_utc": self.now_utc,
        }
        sig = hmac.new(pub, canonical_bytes(payload), hashlib.sha256).digest()
        sig_b64 = base64.b64encode(sig).decode("ascii")
        self.trust_decision_payloads[decision_id] = payload
        self.trust_decision_signatures[decision_id] = sig_b64
        return sig_b64

    def revoke(self, subject_type: str, subject_id: str, reason: str = "test") -> None:
        self.revocations.append({
            "subject_type": subject_type,
            "subject_id": subject_id,
            "reason": reason,
        })

    # ---------- Seed file (requester-visible) ----------

    def write_seed(self, *, reset: bool = True) -> None:
        seed = {
            "request_signing_key_hex": self.request_signing_key.hex(),
            "trust_decision_pub_keys_hex": {k: v.hex() for k, v in self.trust_decision_pub_keys.items()},
            "trust_decision_payloads": {k: json.dumps(v, sort_keys=True) for k, v in self.trust_decision_payloads.items()},
            "trust_decision_signatures": dict(self.trust_decision_signatures),
            "resources": self.resources,
            "revocations": self.revocations,
            "reset": reset,
            "reset_state": reset,
        }
        with open(self.seed_path, "w") as f:
            json.dump(seed, f, sort_keys=True)
        os.chmod(self.seed_path, 0o644)

    # ---------- Executor-only files (mode 0600, owned by ate-executor) ----------

    def write_executor_secrets(self) -> None:
        """Write the executor-only secrets files.

        The credentials file, audit key file, and authority DB MUST be
        owned by ate-executor with mode 0600. We write them as the test
        user first, then chown + chmod via sudo.
        """
        with open(self.credentials_path, "w") as f:
            json.dump(
                {rid: c.hex() for rid, c in self.resource_credentials.items()},
                f,
                sort_keys=True,
            )
        with open(self.audit_key_path, "wb") as f:
            f.write(self.audit_key)
        # chown + chmod via sudo
        paths = (self.credentials_path, self.audit_key_path)
        if os.path.exists(self.db_path):
            paths = paths + (self.db_path,)
        for path in paths:
            subprocess.run(
                ["sudo", "-n", "chown", f"{EXECUTOR_OS_USER}:users", path],
                check=True,
            )
            subprocess.run(
                ["sudo", "-n", "chmod", "0600", path],
                check=True,
            )

    def write_credentials_file(self) -> None:
        """Backward-compat alias for write_executor_secrets()."""
        self.write_executor_secrets()

    # ---------- Read API (via db_admin) ----------

    def read_audit_records(self) -> List[Dict[str, Any]]:
        return self.db_admin.call({"cmd": "read_audit_records"}).get("result") or []

    def read_anchor(self) -> Dict[str, Any]:
        return self.db_admin.call({"cmd": "read_anchor"}).get("result") or {}

    def read_nonce(self, nonce: str) -> Optional[Dict[str, Any]]:
        return self.db_admin.call({"cmd": "read_nonce", "nonce": nonce}).get("result")

    def read_resource(self, resource_id: str) -> Optional[Dict[str, Any]]:
        return self.db_admin.call({"cmd": "read_resource", "resource_id": resource_id}).get("result")

    def list_revocations(self) -> List[Dict[str, Any]]:
        return self.db_admin.call({"cmd": "list_revocations"}).get("result") or []

    # ---------- Executor subprocess (sudo -u ate-executor) ----------

    def run_executor_one_shot(
        self, request: Dict[str, Any], *, deterministic_clock: Optional[float] = None
    ) -> Dict[str, Any]:
        return self.run_executor_one_shot_with_flag(request, deterministic_clock=deterministic_clock, extra_arg=None)

    def _executor_python_cmd(self) -> List[str]:
        """Build the command prefix for running the executor worker as
        ate-executor, with PYTHONPATH pointing to the priv-copied
        implementation_v011 directory."""
        return [
            "sudo", "-u", EXECUTOR_OS_USER, "-H", "--",
            "env", f"PYTHONPATH={self._priv_impl_dir}",
            sys.executable,
            os.path.join(self._priv_impl_dir, "ipc_worker.py"),
        ]

    def run_executor_one_shot_with_flag(
        self,
        request: Dict[str, Any],
        *,
        deterministic_clock: Optional[float] = None,
        extra_arg: Optional[str] = None,
    ) -> Dict[str, Any]:
        self.write_seed(reset=False)
        self.write_executor_secrets()
        cmd = self._executor_python_cmd() + [
            "--db", self.db_path,
            "--seed", self.seed_path,
            "--executor_credentials_file", self.credentials_path,
            "--executor_audit_key_file", self.audit_key_path,
            "--mode", "one_shot",
            "--now_utc", str(deterministic_clock if deterministic_clock is not None else self.now_utc),
        ]
        if extra_arg:
            cmd.append(extra_arg)
        proc = subprocess.run(
            cmd,
            input=json.dumps(request) + "\n",
            capture_output=True,
            text=True,
            timeout=30,
        )
        if proc.returncode != 0:
            try:
                out = json.loads(proc.stdout.strip().splitlines()[-1])
                if "startup_lock" in out:
                    return {"verdict": "DENIED", "reason_code": "PX_AUDIT_INTEGRITY_FAILURE"}
            except Exception:
                pass
            raise RuntimeError(f"worker exit {proc.returncode}: stdout={proc.stdout!r} stderr={proc.stderr!r}")
        last_line = proc.stdout.strip().splitlines()[-1] if proc.stdout.strip() else "{}"
        return json.loads(last_line)

    def launch_concurrent_workers(
        self, requests: List[Dict[str, Any]], now_utc: float
    ) -> List[Tuple[subprocess.Popen, Dict[str, Any]]]:
        """Launch N concurrent worker subprocesses (each as ate-executor).
        Returns list of (proc, request) tuples.
        """
        self.write_seed(reset=False)
        self.write_executor_secrets()
        # Flip reset_state=False in the seed
        with open(self.seed_path) as _sf:
            seed_data = json.load(_sf)
        seed_data["reset"] = False
        seed_data["reset_state"] = False
        with open(self.seed_path, "w") as _sf:
            json.dump(seed_data, _sf, sort_keys=True)
        cmd_template = self._executor_python_cmd() + [
            "--db", self.db_path,
            "--seed", self.seed_path,
            "--executor_credentials_file", self.credentials_path,
            "--executor_audit_key_file", self.audit_key_path,
            "--mode", "one_shot",
            "--now_utc", str(now_utc),
        ]
        procs: List[Tuple[subprocess.Popen, Dict[str, Any]]] = []
        for req in requests:
            p = subprocess.Popen(
                cmd_template,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
            procs.append((p, req))
        return procs


def mk_tmpdir(name: str) -> str:
    base = tempfile.mkdtemp(prefix=f"ate-p1-{name}-")
    return base


def rm_tmpdir(path: str) -> None:
    if os.path.isdir(path):
        shutil.rmtree(path, ignore_errors=True)


def make_request(
    *,
    fixture: Fixture,
    request_id: str,
    decision_id: str,
    operation: str,
    resource_id: str,
    session_id: str,
    nonce: str,
    target_display: str,
    issued_at_utc: Optional[float] = None,
    envelope_id: str = "env-001",
    principal_id: str = "principal-001",
) -> Dict[str, Any]:
    """Build a signed request using the fixture request-signing key."""
    from ipc_protocol import make_request as _mk
    decision_sig = fixture.trust_decision_signatures[decision_id]
    return _mk(
        request_id=request_id,
        decision_id=decision_id,
        decision_signature_b64=decision_sig,
        principal_id=principal_id,
        session_id=session_id,
        operation=operation,
        target_display=target_display,
        resource_id=resource_id,
        nonce=nonce,
        envelope_id=envelope_id,
        issued_at_utc=(issued_at_utc if issued_at_utc is not None else fixture.now_utc),
        signing_key=fixture.requester_signing_key,
    )


def verify_audit_chain(fixture: Fixture) -> Tuple[bool, str]:
    """Verify the audit chain using the parent process's copy of the
    audit key (NOT the DB file). The chain verification reads the audit
    records via db_admin and computes the MACs itself.
    """
    from audit_chain import verify_chain_from_records
    records = fixture.read_audit_records()
    return verify_chain_from_records(records, fixture.audit_key)

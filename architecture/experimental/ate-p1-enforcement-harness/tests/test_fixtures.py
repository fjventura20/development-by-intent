"""ATE P1 v0.1.1 — test fixtures and helpers.

Shared per-test scaffolding:
  - temp directory per test
  - authority DB reset
  - fixture keys (audit HMAC, request signing, decision public keys)
  - protected resources with credentials
  - trust-decision signing helper (for the upstream ATE fixture)

These helpers run entirely in the parent test process for orchestration,
but the actual executor runs in a SUBPROCESS via ipc_worker.py (per
v0.1.1 §C4).
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


class Fixture:
    """Bundles all per-test state."""

    def __init__(self, tmpdir: str, now_utc: float):
        self.tmpdir = tmpdir
        self.now_utc = now_utc
        self.db_path = os.path.join(tmpdir, "authority.sqlite")
        self.seed_path = os.path.join(tmpdir, "seed.json")
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
        # Persistent request-signing key (parent process side)
        self.requester_signing_key = self.request_signing_key

    def add_resource(self, display_path: str) -> Dict[str, Any]:
        rid = random_hex(16)
        cred = secrets.token_bytes(32)
        self.resources.append({
            "resource_id": rid,
            "display_path": display_path,
            "credential_hex": cred.hex(),
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
        self.trust_decision_priv_keys[decision_id] = priv
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

    def write_seed(self, *, reset: bool = True) -> None:
        seed = {
            "audit_key_hex": self.audit_key.hex(),
            "request_signing_key_hex": self.request_signing_key.hex(),
            "trust_decision_pub_keys_hex": {k: v.hex() for k, v in self.trust_decision_pub_keys.items()},
            "trust_decision_payloads": {k: json.dumps(v, sort_keys=True) for k, v in self.trust_decision_payloads.items()},
            "trust_decision_signatures": dict(self.trust_decision_signatures),
            "resources": self.resources,
            "revocations": self.revocations,
            "reset": reset,
            "reset_state": reset,  # also controls nonce/revocation reset
        }
        with open(self.seed_path, "w") as f:
            json.dump(seed, f, sort_keys=True)

    def open_db(self) -> sqlite3.Connection:
        from authority_db import open_db
        return open_db(self.db_path)

    def run_executor_one_shot(
        self, request: Dict[str, Any], *, deterministic_clock: Optional[float] = None
    ) -> Dict[str, Any]:
        """Spawn the IPC worker as a subprocess, send one request, read response.

        Returns the response dict. Raises on protocol error.
        """
        self.write_seed(reset=False)
        env = dict(os.environ)
        cmd = [
            sys.executable,
            WORKER_SCRIPT,
            "--db", self.db_path,
            "--seed", self.seed_path,
            "--mode", "one_shot",
        ]
        if deterministic_clock is not None:
            cmd.extend(["--now_utc", str(deterministic_clock)])
        else:
            cmd.extend(["--now_utc", str(self.now_utc)])
        proc = subprocess.run(
            cmd,
            input=json.dumps(request) + "\n",
            capture_output=True,
            text=True,
            env=env,
            timeout=30,
        )
        if proc.returncode != 0:
            # If startup lock fired, the worker writes a JSON line and exits 1
            try:
                out = json.loads(proc.stdout.strip().splitlines()[-1])
                if "startup_lock" in out:
                    return {"verdict": "DENIED", "reason_code": "PX_AUDIT_INTEGRITY_FAILURE"}
            except Exception:
                pass
            raise RuntimeError(f"worker exit {proc.returncode}: stdout={proc.stdout!r} stderr={proc.stderr!r}")
        last_line = proc.stdout.strip().splitlines()[-1] if proc.stdout.strip() else "{}"
        return json.loads(last_line)

    def read_audit_records(self) -> List[Dict[str, Any]]:
        conn = self.open_db()
        cur = conn.execute(
            "SELECT seq, event_ts, request_id, decision_id, nonce, resource_id, operation, "
            "target_display, outcome, reason_code, previous_digest, record_mac "
            "FROM audit_records ORDER BY seq ASC"
        )
        rows = [dict(r) for r in cur.fetchall()]
        conn.close()
        return rows

    def read_anchor(self) -> Dict[str, Any]:
        conn = self.open_db()
        row = conn.execute(
            "SELECT final_seq, final_record_digest, anchor_mac, updated_at FROM audit_anchor WHERE id=1"
        ).fetchone()
        conn.close()
        return dict(row) if row else {}

    def read_nonce(self, nonce: str) -> Optional[Dict[str, Any]]:
        conn = self.open_db()
        row = conn.execute(
            "SELECT nonce, state, reservation_id, decision_id, first_seen_at, finalized_at, outcome "
            "FROM nonces WHERE nonce=?",
            (nonce,),
        ).fetchone()
        conn.close()
        return dict(row) if row else None

    def read_resource(self, resource_id: str) -> Optional[Dict[str, Any]]:
        conn = self.open_db()
        row = conn.execute(
            "SELECT resource_id, display_path, state_json, mutation_count FROM protected_resources "
            "WHERE resource_id=?",
            (resource_id,),
        ).fetchone()
        conn.close()
        return dict(row) if row else None

    def list_revocations(self) -> List[Dict[str, Any]]:
        conn = self.open_db()
        rows = conn.execute(
            "SELECT subject_type, subject_id, revoked_at, reason FROM revocations ORDER BY subject_type, subject_id"
        ).fetchall()
        conn.close()
        return [dict(r) for r in rows]


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
    """Build a signed request using the fixture request-signing key.

    Equivalent to running the Requester module's build_request.
    """
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
    from audit_chain import verify_audit_chain as _vac
    conn = fixture.open_db()
    ok, reason = _vac(conn, fixture.audit_key)
    conn.close()
    return ok, reason

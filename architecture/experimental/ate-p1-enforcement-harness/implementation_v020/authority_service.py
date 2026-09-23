"""ATE P1 v0.2 — authority service.

Long-lived service running as `ate-authority`. Owns:
  - /var/lib/ate/authority/authority.sqlite (mode 0600)
  - /var/lib/ate/authority/authority_signing.key (Ed25519 private)
  - /run/ate/authority/authority.sock (Unix domain socket)

Accepts:
  - get_decision_envelope
  - get_execution_clearance
  - revoke

State serialized via SQLite BEGIN IMMEDIATE. UNIQUE(decision_id) on
execution_clearances enforces exactly-one-clearance-per-decision.
"""
import argparse
import json
import os
import sqlite3
import sys
import time
import uuid
from typing import Any, Dict, Optional

# Make sibling modules importable when invoked as a script
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from crypto import (
    canonicalize,
    canonical_sha256,
    gen_ed25519_keypair,
    load_ed25519_private_pem,
    operation_id_for_decision,
    save_ed25519_private_pem,
    save_ed25519_public_pem,
    sign_ed25519,
    verify_ed25519,
)


SCHEMA = """
CREATE TABLE IF NOT EXISTS decision_envelopes (
  decision_id TEXT PRIMARY KEY,
  envelope_blob TEXT NOT NULL,
  envelope_signature TEXT NOT NULL,
  issued_at_unix_ms INTEGER NOT NULL
);
CREATE TABLE IF NOT EXISTS execution_clearances (
  clearance_id TEXT PRIMARY KEY,
  decision_id TEXT NOT NULL UNIQUE,
  operation_id TEXT NOT NULL UNIQUE,
  requester_uid INTEGER NOT NULL,
  resource_id TEXT NOT NULL,
  operation TEXT NOT NULL,
  operation_digest TEXT NOT NULL,
  nonce TEXT NOT NULL,
  issued_at_unix_ms INTEGER NOT NULL,
  valid_until_unix_ms INTEGER NOT NULL,
  clearance_blob TEXT NOT NULL,
  clearance_signature TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS revocations (
  decision_id TEXT PRIMARY KEY,
  revoked_at_unix_ms INTEGER NOT NULL,
  reason TEXT
);
"""


def now_ms() -> int:
    return int(time.time() * 1000)


def open_db(path: str) -> sqlite3.Connection:
    conn = sqlite3.connect(path, isolation_level=None, timeout=30.0)
    conn.execute("PRAGMA foreign_keys=ON")
    conn.row_factory = sqlite3.Row
    for stmt in SCHEMA.strip().split(";"):
        s = stmt.strip()
        if s:
            conn.execute(s)
    return conn


class AuthorityService:
    def __init__(self, db_path: str, key_path: str, pubkey_dump_path: str):
        self.db_path = db_path
        self.key_path = key_path
        self.pubkey_dump_path = pubkey_dump_path
        self.conn = open_db(db_path)
        if os.path.exists(key_path):
            self.priv = load_ed25519_private_pem(key_path)
            self.pub = self.priv.public_key()
        else:
            self.priv, self.pub = gen_ed25519_keypair()
            save_ed25519_private_pem(self.priv, key_path)
            save_ed25519_public_pem(self.pub, pubkey_dump_path)
            os.chmod(key_path, 0o600)
            os.chmod(pubkey_dump_path, 0o644)

    # ---- decision issuance ----

    def get_decision_envelope(
        self,
        session_id: str,
        operation: str,
        resource_id: str,
        operation_digest: str,
        nonce: str,
        validity_ms: int,
        requester_uid: int,
        policy_version: str = "ATE-P1-V2-POLICY-1",
    ) -> Dict[str, Any]:
        decision_id = str(uuid.uuid4())
        issued = now_ms()
        envelope = {
            "envelope_version": "ATE-P1-V2-ENV-1",
            "policy_version": policy_version,
            "decision_id": decision_id,
            "requester_uid": requester_uid,
            "resource_id": resource_id,
            "operation": operation,
            "operation_digest": operation_digest,
            "nonce": nonce,
            "issued_at_unix_ms": issued,
            "valid_until_unix_ms": issued + validity_ms,
            "session_id": session_id,
        }
        canonical = canonicalize(envelope)
        sig = sign_ed25519(self.priv, canonical)
        envelope_blob = canonical.decode("utf-8")
        envelope_signature = sig.hex()
        # Persist
        self.conn.execute("BEGIN IMMEDIATE")
        try:
            self.conn.execute(
                "INSERT INTO decision_envelopes(decision_id, envelope_blob, envelope_signature, issued_at_unix_ms) VALUES (?, ?, ?, ?)",
                (decision_id, envelope_blob, envelope_signature, issued),
            )
            self.conn.execute("COMMIT")
        except Exception:
            self.conn.execute("ROLLBACK")
            raise
        return {
            "envelope": envelope,
            "envelope_blob": envelope_blob,
            "envelope_signature": envelope_signature,
        }

    # ---- clearance issuance ----

    def get_execution_clearance(
        self,
        envelope: Dict[str, Any],
        envelope_signature: str,
        clearance_ttl_ms: int,
        requester_uid: int,
        policy_version: str = "ATE-P1-V2-POLICY-1",
    ) -> Dict[str, Any]:
        # Verify the envelope signature BEFORE proceeding (the authority
        # is the only entity that can sign envelopes, so verifying with
        # its own private key's public side proves authenticity).
        try:
            sig = bytes.fromhex(envelope_signature)
        except Exception:
            return {"denied": True, "reason_code": "EX_ENVELOPE_SIG_MALFORMED"}
        if not verify_ed25519(self.pub, sig, canonicalize(envelope)):
            return {"denied": True, "reason_code": "EX_ENVELOPE_SIG_INVALID"}
        decision_id = envelope["decision_id"]
        # Re-derive operation_id deterministically (without operation_id
        # field present). Since our envelope schema does not yet contain
        # operation_id at decision time, operation_id is derived from the
        # canonical envelope bytes (excluding any present operation_id).
        env_for_opid = dict(envelope)
        env_for_opid.pop("operation_id", None)
        op_id = operation_id_for_decision(canonicalize(env_for_opid))
        self.conn.execute("BEGIN IMMEDIATE")
        try:
            # Check revocation
            row = self.conn.execute(
                "SELECT 1 FROM revocations WHERE decision_id = ?", (decision_id,)
            ).fetchone()
            if row is not None:
                self.conn.execute("ROLLBACK")
                return {"denied": True, "reason_code": "EX_CLEARANCE_REVOKED"}
            # Idempotent issuance: if a clearance already exists for this
            # decision, return it.
            existing = self.conn.execute(
                "SELECT * FROM execution_clearances WHERE decision_id = ?",
                (decision_id,),
            ).fetchone()
            if existing is not None:
                self.conn.execute("COMMIT")
                return {
                    "already_issued": True,
                    "clearance_blob": existing["clearance_blob"],
                    "clearance_signature": existing["clearance_signature"],
                    "clearance_id": existing["clearance_id"],
                    "operation_id": existing["operation_id"],
                }
            # Fresh issuance
            clearance_id = str(uuid.uuid4())
            issued = now_ms()
            clearance = {
                "clearance_version": "ATE-P1-V2-CLR-1",
                "policy_version": policy_version,
                "clearance_id": clearance_id,
                "decision_id": decision_id,
                "operation_id": op_id,
                "requester_uid": requester_uid,
                "resource_id": envelope["resource_id"],
                "operation": envelope["operation"],
                "operation_digest": envelope["operation_digest"],
                "nonce": envelope["nonce"],
                "issued_at_unix_ms": issued,
                "valid_until_unix_ms": issued + clearance_ttl_ms,
                "one_shot": True,
            }
            cl_canonical = canonicalize(clearance)
            cl_sig = sign_ed25519(self.priv, cl_canonical)
            self.conn.execute(
                "INSERT INTO execution_clearances(clearance_id, decision_id, operation_id, requester_uid, resource_id, operation, operation_digest, nonce, issued_at_unix_ms, valid_until_unix_ms, clearance_blob, clearance_signature) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (
                    clearance_id,
                    decision_id,
                    op_id,
                    requester_uid,
                    envelope["resource_id"],
                    envelope["operation"],
                    envelope["operation_digest"],
                    envelope["nonce"],
                    issued,
                    issued + clearance_ttl_ms,
                    cl_canonical.decode("utf-8"),
                    cl_sig.hex(),
                ),
            )
            self.conn.execute("COMMIT")
            return {
                "already_issued": False,
                "clearance_blob": cl_canonical.decode("utf-8"),
                "clearance_signature": cl_sig.hex(),
                "clearance_id": clearance_id,
                "operation_id": op_id,
            }
        except Exception:
            self.conn.execute("ROLLBACK")
            raise

    def revoke(self, decision_id: str, reason: str) -> Dict[str, Any]:
        self.conn.execute("BEGIN IMMEDIATE")
        try:
            self.conn.execute(
                "INSERT OR IGNORE INTO revocations(decision_id, revoked_at_unix_ms, reason) VALUES (?, ?, ?)",
                (decision_id, now_ms(), reason),
            )
            self.conn.execute("COMMIT")
        except Exception:
            self.conn.execute("ROLLBACK")
            raise
        return {"ok": True}


# ---- IPC server ----

def serve(sock_path: str, svc: AuthorityService) -> None:
    import socket
    import struct

    if os.path.exists(sock_path):
        os.unlink(sock_path)
    os.makedirs(os.path.dirname(sock_path), exist_ok=True)
    srv = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    srv.bind(sock_path)
    os.chmod(sock_path, 0o660)
    srv.listen(64)
    print(f"authority: listening on {sock_path}", flush=True)
    while True:
        conn, _ = srv.accept()
        # Get peer credentials (UID)
        pid, uid, gid = struct.unpack(
            "3i", conn.getsockopt(
                socket.SOL_SOCKET, socket.SO_PEERCRED, struct.calcsize("3i")
            )
        )
        # Read newline-delimited JSON request
        buf = b""
        while not buf.endswith(b"\n"):
            chunk = conn.recv(65536)
            if not chunk:
                break
            buf += chunk
        try:
            req = json.loads(buf.decode("utf-8"))
        except Exception:
            try:
                conn.sendall((json.dumps({"error": "bad_json"}) + "\n").encode())
            except (BrokenPipeError, ConnectionResetError):
                pass
            conn.close()
            continue
        op = req.get("op")
        try:
            if op == "get_decision_envelope":
                resp = svc.get_decision_envelope(
                    session_id=req["session_id"],
                    operation=req["operation"],
                    resource_id=req["resource_id"],
                    operation_digest=req["operation_digest"],
                    nonce=req["nonce"],
                    validity_ms=req["validity_ms"],
                    requester_uid=uid,
                )
            elif op == "get_execution_clearance":
                envelope_blob = req["envelope_blob"]
                envelope_signature = req["envelope_signature"]
                envelope = json.loads(envelope_blob)
                if envelope.get("decision_id") is None:
                    raise ValueError("missing decision_id")
                resp = svc.get_execution_clearance(
                    envelope=envelope,
                    envelope_signature=envelope_signature,
                    clearance_ttl_ms=req["clearance_ttl_ms"],
                    requester_uid=uid,
                )
            elif op == "revoke":
                resp = svc.revoke(req["decision_id"], req.get("reason", ""))
            else:
                resp = {"error": "unknown_op"}
        except Exception as e:
            resp = {"error": str(e)}
        try:
            conn.sendall((json.dumps(resp) + "\n").encode())
        except (BrokenPipeError, ConnectionResetError):
            pass
        conn.close()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--db", required=True)
    parser.add_argument("--key", required=True)
    parser.add_argument("--pubkey", required=True)
    parser.add_argument("--sock", required=True)
    args = parser.parse_args()
    svc = AuthorityService(args.db, args.key, args.pubkey)
    serve(args.sock, svc)


if __name__ == "__main__":
    main()

"""ATE P1 v0.2 — executor service.

Long-lived service running as `ate-executor`. Owns:
  - /var/lib/ate/executor/executor.sqlite (mode 0600)
  - /var/lib/ate/executor/audit_signing.key (Ed25519 private)
  - /var/lib/ate/executor/authority_pubkey.pem (Ed25519 public)
  - /var/lib/ate/executor/resource_credentials.json (per-resource HMAC)
  - /var/lib/ate/resources/<id>/state.json (protected resources)
  - /run/ate/executor/executor.sock

Executor NEVER touches authority.sock or authority.sqlite. All
authority artifacts arrive via the requester's IPC submission.
"""
import argparse
import hashlib
import hmac
import json
import os
import sqlite3
import sys
import time
from typing import Any, Dict, Optional

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from crypto import (
    Ed25519PublicKey,
    canonicalize,
    canonical_sha256,
    load_ed25519_public_pem,
    sign_ed25519,
    verify_ed25519,
)


SCHEMA = """
CREATE TABLE IF NOT EXISTS executor_operations (
  operation_id TEXT PRIMARY KEY,
  clearance_id TEXT NOT NULL,
  decision_id TEXT NOT NULL,
  requester_uid INTEGER NOT NULL,
  resource_id TEXT NOT NULL,
  operation TEXT NOT NULL,
  operation_digest TEXT NOT NULL,
  state TEXT NOT NULL,
  prepared_at_unix_ms INTEGER NOT NULL,
  mutated_at_unix_ms INTEGER,
  completed_at_unix_ms INTEGER,
  mutation_outcome TEXT,
  audit_seq INTEGER
);
CREATE TABLE IF NOT EXISTS executor_resources (
  resource_id TEXT PRIMARY KEY,
  display_path TEXT NOT NULL,
  credential_key_hex TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS executor_audit_records (
  record_seq INTEGER PRIMARY KEY AUTOINCREMENT,
  record_mac TEXT NOT NULL,
  record_blob TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS executor_audit_anchor (
  id INTEGER PRIMARY KEY CHECK (id = 1),
  final_seq INTEGER NOT NULL,
  final_record_digest TEXT NOT NULL,
  anchor_sig TEXT NOT NULL
);
"""

POLICY_VERSION = "ATE-P1-V2-POLICY-1"
ENVELOPE_VERSION = "ATE-P1-V2-ENV-1"
CLEARANCE_VERSION = "ATE-P1-V2-CLR-1"


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


def hmac_chain(prev_mac_hex: str, record_blob: str) -> str:
    prev = bytes.fromhex(prev_mac_hex) if prev_mac_hex else b""
    return hmac.new(
        prev, record_blob.encode("utf-8"), hashlib.sha256
    ).hexdigest()


def anchor_sig(audit_priv_signing_key, final_seq: int, final_record_digest: str) -> str:
    msg = canonicalize({"final_seq": final_seq, "final_record_digest": final_record_digest})
    return sign_ed25519(audit_priv_signing_key, msg).hex()


class ExecutorService:
    def __init__(
        self,
        db_path: str,
        audit_key_path: str,
        authority_pubkey_path: str,
        resource_credentials_path: str,
        resources_dir: str,
    ):
        self.db_path = db_path
        self.resources_dir = resources_dir
        self.authority_pubkey = load_ed25519_public_pem(authority_pubkey_path)
        self.audit_priv = self._load_or_gen_audit_key(audit_key_path)
        # Load per-resource credentials
        with open(resource_credentials_path) as f:
            creds = json.load(f)
        self.resource_creds: Dict[str, bytes] = {
            rid: bytes.fromhex(h) for rid, h in creds.items()
        }
        self.conn = open_db(db_path)
        # Initialize resources table (if not already)
        for rid, key in self.resource_creds.items():
            self.conn.execute(
                "INSERT OR IGNORE INTO executor_resources(resource_id, display_path, credential_key_hex) VALUES (?, ?, ?)",
                (rid, f"resources:{rid}", key.hex()),
            )
        # Verify audit chain on startup
        if not self._verify_chain():
            raise RuntimeError("audit chain integrity failure at startup")

    def _load_or_gen_audit_key(self, path: str):
        from crypto import gen_ed25519_keypair, load_ed25519_private_pem, save_ed25519_private_pem
        if os.path.exists(path):
            return load_ed25519_private_pem(path)
        priv, _ = gen_ed25519_keypair()
        save_ed25519_private_pem(priv, path)
        os.chmod(path, 0o600)
        return priv

    # ---- chain verification ----

    def _verify_chain(self) -> bool:
        anchor = self.conn.execute(
            "SELECT * FROM executor_audit_anchor WHERE id=1"
        ).fetchone()
        if anchor is None:
            return True
        records = self.conn.execute(
            "SELECT record_seq, record_mac, record_blob FROM executor_audit_records ORDER BY record_seq"
        ).fetchall()
        prev = ""
        for r in records:
            expected = hmac_chain(prev, r["record_blob"])
            if expected != r["record_mac"]:
                return False
            prev = r["record_mac"]
        # Verify anchor
        expected_anchor = anchor_sig(self.audit_priv, anchor["final_seq"], prev if records else "")
        return expected_anchor == anchor["anchor_sig"]

    def _append_audit(self, record: Dict[str, Any]) -> int:
        # Compute chain MAC
        anchor = self.conn.execute(
            "SELECT final_seq, final_record_digest FROM executor_audit_anchor WHERE id=1"
        ).fetchone()
        if anchor is None:
            prev_mac = ""
            prev_seq = 0
        else:
            prev_mac = anchor["final_record_digest"] or ""
            prev_seq = anchor["final_seq"]
        # record_seq = prev_seq + 1
        seq = prev_seq + 1
        record_with_seq = dict(record)
        record_with_seq["record_seq"] = seq
        blob = canonicalize(record_with_seq).decode("utf-8")
        mac = hmac_chain(prev_mac, blob)
        self.conn.execute(
            "INSERT INTO executor_audit_records(record_seq, record_mac, record_blob) VALUES (?, ?, ?)",
            (seq, mac, blob),
        )
        # Update anchor
        anchor_sig_hex = anchor_sig(self.audit_priv, seq, mac)
        if anchor is None:
            self.conn.execute(
                "INSERT INTO executor_audit_anchor(id, final_seq, final_record_digest, anchor_sig) VALUES (1, ?, ?, ?)",
                (seq, mac, anchor_sig_hex),
            )
        else:
            self.conn.execute(
                "UPDATE executor_audit_anchor SET final_seq=?, final_record_digest=?, anchor_sig=? WHERE id=1",
                (seq, mac, anchor_sig_hex),
            )
        return seq

    # ---- cross-envelope verification ----

    def _verify_and_extract(
        self,
        envelope_blob: str,
        envelope_signature: str,
        clearance_blob: str,
        clearance_signature: str,
        requester_payload: Dict[str, Any],
        peer_uid: int,
    ) -> Dict[str, Any]:
        # Verify authority signature on decision envelope
        try:
            envelope = json.loads(envelope_blob)
        except Exception:
            return {"ok": False, "reason_code": "EX_ENVELOPE_MALFORMED"}
        sig = bytes.fromhex(envelope_signature)
        if not verify_ed25519(self.authority_pubkey, sig, canonicalize(envelope)):
            return {"ok": False, "reason_code": "EX_ENVELOPE_SIG_INVALID"}
        if envelope.get("envelope_version") != ENVELOPE_VERSION:
            return {"ok": False, "reason_code": "EX_ENVELOPE_VERSION_UNKNOWN"}
        if envelope.get("policy_version") != POLICY_VERSION:
            return {"ok": False, "reason_code": "EX_POLICY_VERSION_UNKNOWN"}
        if envelope.get("requester_uid") != peer_uid:
            return {"ok": False, "reason_code": "EX_REQUESTER_UID_MISMATCH"}
        now = now_ms()
        if now > envelope["valid_until_unix_ms"]:
            return {"ok": False, "reason_code": "EX_ENVELOPE_EXPIRED"}
        # Verify authority signature on clearance
        try:
            clearance = json.loads(clearance_blob)
        except Exception:
            return {"ok": False, "reason_code": "EX_CLEARANCE_MALFORMED"}
        csig = bytes.fromhex(clearance_signature)
        if not verify_ed25519(self.authority_pubkey, csig, canonicalize(clearance)):
            return {"ok": False, "reason_code": "EX_CLEARANCE_SIG_INVALID"}
        if clearance.get("clearance_version") != CLEARANCE_VERSION:
            return {"ok": False, "reason_code": "EX_CLEARANCE_VERSION_UNKNOWN"}
        if clearance.get("policy_version") != POLICY_VERSION:
            return {"ok": False, "reason_code": "EX_POLICY_VERSION_UNKNOWN"}
        if clearance.get("requester_uid") != peer_uid:
            return {"ok": False, "reason_code": "EX_CLEARANCE_REQUESTER_UID_MISMATCH"}
        if now > clearance["valid_until_unix_ms"]:
            return {"ok": False, "reason_code": "EX_CLEARANCE_EXPIRED"}
        # Cross-envelope consistency
        if envelope["decision_id"] != clearance["decision_id"]:
            return {"ok": False, "reason_code": "EX_DECISION_CLEARANCE_BINDING_MISMATCH"}
        if envelope["resource_id"] != clearance["resource_id"]:
            return {"ok": False, "reason_code": "EX_RESOURCE_BINDING_MISMATCH"}
        if envelope["operation"] != clearance["operation"]:
            return {"ok": False, "reason_code": "EX_OPERATION_BINDING_MISMATCH"}
        if envelope["operation_digest"] != clearance["operation_digest"]:
            return {"ok": False, "reason_code": "EX_OPERATION_DIGEST_BINDING_MISMATCH"}
        if envelope["nonce"] != clearance["nonce"]:
            return {"ok": False, "reason_code": "EX_NONCE_BINDING_MISMATCH"}
        # Request digest matches
        op_digest = canonical_sha256(requester_payload).hex()
        if op_digest != envelope["operation_digest"]:
            return {"ok": False, "reason_code": "EX_REQUEST_DIGEST_MISMATCH"}
        if requester_payload.get("resource_id") != envelope["resource_id"]:
            return {"ok": False, "reason_code": "EX_PAYLOAD_RESOURCE_MISMATCH"}
        if requester_payload.get("operation") != envelope["operation"]:
            return {"ok": False, "reason_code": "EX_PAYLOAD_OPERATION_MISMATCH"}
        # Recompute operation_id deterministically
        from crypto import operation_id_for_decision
        env_for_opid = dict(envelope)
        env_for_opid.pop("operation_id", None)
        op_id = operation_id_for_decision(canonicalize(env_for_opid))
        if op_id != clearance["operation_id"]:
            return {"ok": False, "reason_code": "EX_OPERATION_ID_BINDING_MISMATCH"}
        return {
            "ok": True,
            "envelope": envelope,
            "clearance": clearance,
            "operation_id": op_id,
        }

    # ---- main execute flow ----

    def execute(
        self,
        envelope_blob: str,
        envelope_signature: str,
        clearance_blob: str,
        clearance_signature: str,
        requester_payload: Dict[str, Any],
        peer_uid: int,
    ) -> Dict[str, Any]:
        v = self._verify_and_extract(
            envelope_blob, envelope_signature,
            clearance_blob, clearance_signature,
            requester_payload, peer_uid,
        )
        if not v.get("ok"):
            return v
        operation_id = v["operation_id"]
        envelope = v["envelope"]
        clearance = v["clearance"]
        resource_id = envelope["resource_id"]
        if resource_id not in self.resource_creds:
            return {"ok": False, "reason_code": "EX_RESOURCE_UNKNOWN"}

        # Check existing executor_operations row for this operation_id
        existing = self.conn.execute(
            "SELECT * FROM executor_operations WHERE operation_id = ?",
            (operation_id,),
        ).fetchone()
        if existing is not None and existing["state"] == "COMPLETED":
            # Replay after completion — already applied
            return {
                "ok": True,
                "verdict": "ALREADY_APPLIED",
                "reason_code": "EX_ALREADY_APPLIED",
                "audit_seq": existing["audit_seq"],
                "mutation_count": self._read_mutation_count(resource_id),
            }
        if existing is None:
            # PREPARED transition — durable linearization point
            self.conn.execute("BEGIN IMMEDIATE")
            try:
                self.conn.execute(
                    "INSERT INTO executor_operations(operation_id, clearance_id, decision_id, requester_uid, resource_id, operation, operation_digest, state, prepared_at_unix_ms) VALUES (?, ?, ?, ?, ?, ?, ?, 'PREPARED', ?)",
                    (
                        operation_id,
                        clearance["clearance_id"],
                        envelope["decision_id"],
                        envelope["requester_uid"],
                        resource_id,
                        envelope["operation"],
                        envelope["operation_digest"],
                        now_ms(),
                    ),
                )
                self.conn.execute("COMMIT")
            except Exception:
                self.conn.execute("ROLLBACK")
                raise
        # Apply idempotent mutation
        outcome = self._apply_idempotent_mutation(
            resource_id, operation_id, envelope["operation"], requester_payload
        )
        # MUTATED transition
        self.conn.execute("BEGIN IMMEDIATE")
        try:
            self.conn.execute(
                "UPDATE executor_operations SET state='MUTATED', mutated_at_unix_ms=?, mutation_outcome=? WHERE operation_id=?",
                (now_ms(), outcome, operation_id),
            )
            self.conn.execute("COMMIT")
        except Exception:
            self.conn.execute("ROLLBACK")
            raise
        # Append audit + COMPLETED
        self.conn.execute("BEGIN IMMEDIATE")
        try:
            audit_seq = self._append_audit({
                "operation_id": operation_id,
                "clearance_id": clearance["clearance_id"],
                "decision_id": envelope["decision_id"],
                "requester_uid": envelope["requester_uid"],
                "resource_id": resource_id,
                "operation": envelope["operation"],
                "outcome": outcome,
                "completed_at_unix_ms": now_ms(),
            })
            self.conn.execute(
                "UPDATE executor_operations SET state='COMPLETED', completed_at_unix_ms=?, audit_seq=? WHERE operation_id=?",
                (now_ms(), audit_seq, operation_id),
            )
            self.conn.execute("COMMIT")
        except Exception:
            self.conn.execute("ROLLBACK")
            raise
        return {
            "ok": True,
            "verdict": "EXECUTED" if outcome == "APPLIED" else "ALREADY_APPLIED",
            "reason_code": "EX_OK" if outcome == "APPLIED" else "EX_ALREADY_APPLIED",
            "audit_seq": audit_seq,
            "mutation_count": self._read_mutation_count(resource_id),
        }

    def _resource_path(self, resource_id: str) -> str:
        return os.path.join(self.resources_dir, resource_id + ".json")

    def _read_mutation_count(self, resource_id: str) -> int:
        path = self._resource_path(resource_id)
        if not os.path.exists(path):
            return 0
        with open(path) as f:
            d = json.load(f)
        return int(d.get("mutation_count", 0))

    def _apply_idempotent_mutation(
        self,
        resource_id: str,
        operation_id: str,
        operation: str,
        requester_payload: Dict[str, Any],
    ) -> str:
        path = self._resource_path(resource_id)
        # Read or initialize
        if os.path.exists(path):
            with open(path) as f:
                doc = json.load(f)
        else:
            doc = {
                "resource_id": resource_id,
                "display_path": f"resources:{resource_id}",
                "state": {},
                "mutation_count": 0,
                "applied_operation_ids": [],
            }
        applied = doc.get("applied_operation_ids", [])
        if operation_id in applied:
            return "ALREADY_APPLIED"
        # Apply
        new_state = dict(doc.get("state", {}))
        # Simple mutation semantics: increment a counter or apply payload's "write" value
        if operation == "WRITE_SCOPED":
            payload_value = requester_payload.get("value", "value-not-provided")
            new_state["last_write"] = payload_value
            new_state["last_operation_id"] = operation_id
        new_state["write_count"] = new_state.get("write_count", 0) + 1
        doc["state"] = new_state
        doc["mutation_count"] = int(doc.get("mutation_count", 0)) + 1
        applied.append(operation_id)
        doc["applied_operation_ids"] = applied
        # Atomic write
        tmp = path + ".tmp"
        with open(tmp, "w") as f:
            f.write(json.dumps(doc, sort_keys=True, indent=2))
        os.replace(tmp, path)
        return "APPLIED"


# ---- IPC server ----

def serve(sock_path: str, svc: ExecutorService) -> None:
    import socket
    import struct

    if os.path.exists(sock_path):
        os.unlink(sock_path)
    os.makedirs(os.path.dirname(sock_path), exist_ok=True)
    srv = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    srv.bind(sock_path)
    os.chmod(sock_path, 0o660)
    srv.listen(64)
    print(f"executor: listening on {sock_path}", flush=True)
    while True:
        conn, _ = srv.accept()
        pid, uid, gid = struct.unpack(
            "3i", conn.getsockopt(
                socket.SOL_SOCKET, socket.SO_PEERCRED, struct.calcsize("3i")
            )
        )
        buf = b""
        while not buf.endswith(b"\n"):
            chunk = conn.recv(65536)
            if not chunk:
                break
            buf += chunk
        try:
            req = json.loads(buf.decode("utf-8"))
            op = req.get("op")
            if op == "execute":
                resp = svc.execute(
                    envelope_blob=req["envelope_blob"],
                    envelope_signature=req["envelope_signature"],
                    clearance_blob=req["clearance_blob"],
                    clearance_signature=req["clearance_signature"],
                    requester_payload=req["requester_payload"],
                    peer_uid=uid,
                )
            elif op == "read_mutation_count":
                resp = {"ok": True, "mutation_count": svc._read_mutation_count(req["resource_id"])}
            else:
                resp = {"error": "unknown_op"}
        except Exception as e:
            resp = {"ok": False, "reason_code": "EX_INTERNAL", "error": str(e)}
        try:
            conn.sendall((json.dumps(resp) + "\n").encode())
        except (BrokenPipeError, ConnectionResetError):
            pass
        conn.close()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--db", required=True)
    parser.add_argument("--audit_key", required=True)
    parser.add_argument("--authority_pubkey", required=True)
    parser.add_argument("--resource_credentials", required=True)
    parser.add_argument("--resources_dir", required=True)
    parser.add_argument("--sock", required=True)
    args = parser.parse_args()
    svc = ExecutorService(
        db_path=args.db,
        audit_key_path=args.audit_key,
        authority_pubkey_path=args.authority_pubkey,
        resource_credentials_path=args.resource_credentials,
        resources_dir=args.resources_dir,
    )
    serve(args.sock, svc)


if __name__ == "__main__":
    main()

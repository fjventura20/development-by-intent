#!/usr/bin/env python3
"""ATE P1 v0.1.1 — Privileged DB admin helper.

Runs as the `ate-executor` OS user (via `sudo -u ate-executor`). Listens
on stdin for newline-delimited JSON commands and writes JSON results on
stdout. Each command operates on a single authority DB whose path is
passed via --db at startup.

This helper exists so the test harness (which runs as the unprivileged
user, NOT ate-executor) can perform narrow DB operations (bootstrap,
inspection) without holding the DB file handle itself. It is NOT an
IPC channel for executor work — that's ipc_worker.py.

Commands (request: {"cmd": <name>, ...}):

  bootstrap
      Create the DB schema if not already initialized. Idempotent.
      Returns: {"ok": true}

  exec_insert_resource
      resource_id, display_path, credential_hex
      Insert a resource row (the executor-side bootstrap).

  exec_insert_decision
      decision_id, signed_payload_json, signature_b64
      Insert a decision signature.

  read_resource resource_id
      Read a resource row. Returns the row dict.

  read_nonce nonce
      Read a nonce row. Returns the row dict or null.

  read_audit_records
      Read all audit_records ordered by seq. Returns list of dicts.

  read_anchor
      Read audit_anchor. Returns the row dict.

  list_revocations
      Read all revocations. Returns list of dicts.

  write_audit_record
      seq (assigned by DB), event_ts, request_id, decision_id, nonce,
      resource_id, operation, target_display, outcome, reason_code,
      previous_digest, record_mac
      Append a single audit record. The MAC is verified by an external
      caller; this command just inserts the row.

  update_anchor final_seq, final_record_digest, anchor_mac, updated_at
      Update the audit anchor row.

  delete_audit_records request_id
      Delete audit records by request_id (for bootstrap rollback).

  update_resource_for_bootstrap_rollback resource_id, state_json
      Reset a resource row's state_json and mutation_count (for
      harness bootstrap rollback; NOT a requester-side action).

  raw_execute_sql sql, params (list)
      Execute a single read-only SQL query and return the rows.

The helper itself does NOT verify any signatures — it is a privileged
read/write surface for the HARNESS (the trusted orchestrator). The
EXECUTOR's privilege boundary is enforced by file ownership; this
helper just provides the harness with the necessary write/read access
through a narrow command interface.
"""
from __future__ import annotations

import argparse
import json
import os
import sqlite3
import sys
from typing import Any, Dict, List

HARNESS_DIR = os.path.dirname(os.path.abspath(__file__))
if HARNESS_DIR not in sys.path:
    sys.path.insert(0, HARNESS_DIR)

from authority_db import open_db, _init_schema  # noqa: E402


def _row_to_dict(row: sqlite3.Row) -> Dict[str, Any]:
    return {k: row[k] for k in row.keys()}


def handle(cmd: Dict[str, Any]) -> Dict[str, Any]:
    name = cmd.get("cmd")
    db_path = cmd.get("_db_path")  # set by main
    if not name:
        return {"_error": "missing cmd"}
    conn = open_db(db_path)
    try:
        if name == "bootstrap":
            _init_schema(conn)
            conn.commit()
            return {"ok": True}
        if name == "exec_insert_resource":
            from protected_resource import insert_resource
            insert_resource(
                conn,
                cmd["resource_id"],
                cmd["display_path"],
                bytes.fromhex(cmd["credential_hex"]),
            )
            return {"ok": True}
        if name == "exec_insert_decision":
            conn.execute(
                "INSERT INTO decision_signatures (decision_id, signed_payload_json, signature_b64) "
                "VALUES (?, ?, ?)",
                (cmd["decision_id"], cmd["signed_payload_json"], cmd["signature_b64"]),
            )
            conn.commit()
            return {"ok": True}
        if name == "read_resource":
            row = conn.execute(
                "SELECT resource_id, display_path, state_json, mutation_count "
                "FROM protected_resources WHERE resource_id=?",
                (cmd["resource_id"],),
            ).fetchone()
            return {"result": _row_to_dict(row) if row else None}
        if name == "read_nonce":
            row = conn.execute(
                "SELECT nonce, state, reservation_id, decision_id, first_seen_at, "
                "finalized_at, outcome FROM nonces WHERE nonce=?",
                (cmd["nonce"],),
            ).fetchone()
            return {"result": _row_to_dict(row) if row else None}
        if name == "read_audit_records":
            cur = conn.execute(
                "SELECT seq, event_ts, request_id, decision_id, nonce, resource_id, operation, "
                "target_display, outcome, reason_code, previous_digest, record_mac "
                "FROM audit_records ORDER BY seq ASC"
            )
            return {"result": [_row_to_dict(r) for r in cur.fetchall()]}
        if name == "read_anchor":
            row = conn.execute(
                "SELECT final_seq, final_record_digest, anchor_mac, updated_at FROM audit_anchor WHERE id=1"
            ).fetchone()
            return {"result": _row_to_dict(row) if row else None}
        if name == "list_revocations":
            cur = conn.execute(
                "SELECT subject_type, subject_id, revoked_at, reason FROM revocations "
                "ORDER BY subject_type, subject_id"
            )
            return {"result": [_row_to_dict(r) for r in cur.fetchall()]}
        if name == "write_audit_record":
            cur = conn.execute(
                "INSERT INTO audit_records "
                "(event_ts, request_id, decision_id, nonce, resource_id, operation, "
                " target_display, outcome, reason_code, previous_digest, record_mac) "
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (
                    cmd["event_ts"], cmd["request_id"], cmd["decision_id"],
                    cmd["nonce"], cmd["resource_id"], cmd["operation"],
                    cmd["target_display"], cmd["outcome"], cmd.get("reason_code"),
                    cmd["previous_digest"], cmd["record_mac"],
                ),
            )
            conn.commit()
            return {"ok": True, "seq": cur.lastrowid}
        if name == "update_anchor":
            conn.execute(
                "UPDATE audit_anchor SET final_seq=?, final_record_digest=?, anchor_mac=?, "
                "updated_at=? WHERE id=1",
                (
                    cmd["final_seq"], cmd["final_record_digest"],
                    cmd["anchor_mac"], cmd["updated_at"],
                ),
            )
            conn.commit()
            return {"ok": True}
        if name == "delete_audit_records":
            conn.execute("DELETE FROM audit_records WHERE request_id=?", (cmd["request_id"],))
            conn.commit()
            return {"ok": True}
        if name == "update_resource_for_bootstrap_rollback":
            conn.execute(
                "UPDATE protected_resources SET state_json=?, mutation_count=0, updated_at='bootstrap-rollback' "
                "WHERE resource_id=?",
                (cmd["state_json"], cmd["resource_id"]),
            )
            conn.commit()
            return {"ok": True}
        if name == "raw_execute_sql":
            cur = conn.execute(cmd["sql"], tuple(cmd.get("params") or []))
            return {"result": [_row_to_dict(r) for r in cur.fetchall()]}
        if name == "write_sql":
            cur = conn.execute(cmd["sql"], tuple(cmd.get("params") or []))
            conn.commit()
            return {"ok": True, "rowcount": cur.rowcount}
        return {"_error": f"unknown cmd: {name}"}
    finally:
        conn.close()


def main() -> int:
    parser = argparse.ArgumentParser(description="ATE P1 DB admin helper")
    parser.add_argument("--db", required=True)
    args = parser.parse_args()
    db_path = args.db
    # Read commands from stdin, write responses to stdout
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        if line == "__shutdown__":
            return 0
        try:
            req = json.loads(line)
        except Exception as e:
            sys.stdout.write(json.dumps({"_error": f"parse: {e}"}) + "\n")
            sys.stdout.flush()
            continue
        req["_db_path"] = db_path
        try:
            resp = handle(req)
        except Exception as e:
            resp = {"_error": f"{type(e).__name__}: {e}"}
        sys.stdout.write(json.dumps(resp) + "\n")
        sys.stdout.flush()
    return 0


if __name__ == "__main__":
    sys.exit(main())

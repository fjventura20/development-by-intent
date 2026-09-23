"""ATE P1 v0.1.1 — Protected resource fixture.

The protected resource is identified by an immutable `resource_id`. To
perform a privileged mutation, the caller must present the per-resource
unguessable credential held ONLY by the executor.

Per v0.1.1 §C1: the resource mutation occurs inside the same SQLite
transaction as the nonce finalization and audit append. The mutation
function `apply_mutation` is the only sanctioned path; it verifies
the presented credential against the stored per-resource credential
using constant-time comparison before writing.

The requester is forbidden from importing or calling this module's
mutation path: the privilege boundary is enforced by the per-resource
credential, which is held ONLY by the executor config (and not exposed
via IPC). A requester would need to fabricate the credential, which
is unguessable 32-byte random.
"""
from __future__ import annotations

import datetime
import hmac
import json
import os
import sqlite3
from typing import Any, Dict, List, Optional, Tuple

from authority_db import open_db
from crypto_utils import random_hex


def make_resource(display_path: str) -> Dict[str, Any]:
    """Create a fresh resource row in the DB.

    Returns the resource_id and its initial mutation_count and credential
    (held only by the executor; tests use this as the seeded credential).
    """
    resource_id = random_hex(16)
    credential = os.urandom(32)
    return {
        "resource_id": resource_id,
        "display_path": display_path,
        "credential": credential,
    }


def insert_resource(
    conn: sqlite3.Connection,
    resource_id: str,
    display_path: str,
    credential: bytes,
) -> None:
    """Insert a fresh protected resource. The credential is stored
    in the DB and is required at every mutation time."""
    now = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.%fZ")
    state_json = json.dumps(
        {"display_path": display_path, "history": []},
        sort_keys=True,
        separators=(",", ":"),
    )
    conn.execute(
        "INSERT OR IGNORE INTO protected_resources "
        "(resource_id, display_path, resource_credential_hex, state_json, "
        "mutation_count, created_at, updated_at) "
        "VALUES (?, ?, ?, ?, 0, ?, ?)",
        (
            resource_id,
            display_path,
            credential.hex(),
            state_json,
            now,
            now,
        ),
    )
    conn.commit()


def list_resources(conn: sqlite3.Connection) -> List[Dict[str, Any]]:
    cur = conn.execute(
        "SELECT resource_id, display_path, mutation_count FROM protected_resources ORDER BY resource_id"
    )
    return [dict(r) for r in cur.fetchall()]


def fetch_credential_hex(
    conn: sqlite3.Connection, resource_id: str
) -> Optional[str]:
    """Read the stored credential hex for a resource (read-only helper).

    The mutation path itself uses `apply_mutation`, which reads the
    credential internally and compares against the presented one.
    """
    cur = conn.execute(
        "SELECT resource_credential_hex FROM protected_resources WHERE resource_id=?",
        (resource_id,),
    )
    row = cur.fetchone()
    if row is None:
        return None
    return row["resource_credential_hex"]


def apply_mutation(
    conn: sqlite3.Connection,
    resource_id: str,
    operation: str,
    request_id: str,
    presented_credential: bytes,
) -> Tuple[bool, str]:
    """Apply a privileged mutation. Verifies the presented credential
    against the stored per-resource credential using constant-time
    HMAC compare.

    Returns (ok, reason_code). On success, mutates the DB (in the
    caller's transaction). On failure, does NOT mutate.

    The credential check is the privilege boundary enforced by the
    resource; even if the caller has a DB write handle, this function
    refuses without the correct credential.
    """
    row = conn.execute(
        "SELECT resource_id, display_path, resource_credential_hex, state_json, "
        "mutation_count FROM protected_resources WHERE resource_id=?",
        (resource_id,),
    ).fetchone()
    if row is None:
        return False, "PX_RESOURCE_NOT_FOUND"
    stored_hex = row["resource_credential_hex"]
    if not presented_credential:
        return False, "PX_RESOURCE_CREDENTIAL_MISSING"
    try:
        presented_hex = presented_credential.hex() if isinstance(presented_credential, (bytes, bytearray)) else str(presented_credential)
    except Exception:
        return False, "PX_RESOURCE_CREDENTIAL_MALFORMED"
    if not hmac.compare_digest(stored_hex.lower(), presented_hex.lower()):
        return False, "PX_RESOURCE_CREDENTIAL_INVALID"
    # Credential matches. Apply the mutation in the caller's transaction.
    new_state = _apply_mutation(row["state_json"], operation, request_id)
    new_count = int(row["mutation_count"]) + 1
    now = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.%fZ")
    conn.execute(
        "UPDATE protected_resources SET state_json=?, mutation_count=?, updated_at=? "
        "WHERE resource_id=?",
        (new_state, new_count, now, resource_id),
    )
    return True, "PX_OK"


def _apply_mutation(state_json: str, operation: str, request_id: str) -> str:
    state = json.loads(state_json)
    history = list(state.get("history", []))
    history.append({"operation": operation, "request_id": request_id})
    state["history"] = history
    return json.dumps(state, sort_keys=True, separators=(",", ":"))

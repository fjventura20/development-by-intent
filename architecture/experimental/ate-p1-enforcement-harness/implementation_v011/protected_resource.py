"""ATE P1 v0.1.1 — Protected resource fixture.

The protected resource is identified by an immutable `resource_id`. To
perform a privileged mutation, the caller must present the per-resource
unguessable credential held ONLY by the executor.

The resource is stored in the authority DB. The executor performs the
mutation inside the same transaction as the nonce finalization and
audit append (per v0.1.1 §C1).

The requester is forbidden from importing or calling this module's
mutation path: the privilege boundary is enforced by the executor's
sole possession of the credential, not by Python class isolation. The
requester would need to fabricate the credential, which is unguessable
32-byte random.
"""
from __future__ import annotations

import datetime
import json
import os
import sqlite3
from typing import Any, Dict, List, Optional

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
) -> None:
    now = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.%fZ")
    state_json = json.dumps({"display_path": display_path, "history": []}, sort_keys=True, separators=(",", ":"))
    conn.execute(
        "INSERT OR IGNORE INTO protected_resources "
        "(resource_id, display_path, state_json, mutation_count, created_at, updated_at) "
        "VALUES (?, ?, ?, 0, ?, ?)",
        (resource_id, display_path, state_json, now, now),
    )
    conn.commit()


def list_resources(conn: sqlite3.Connection) -> List[Dict[str, Any]]:
    cur = conn.execute(
        "SELECT resource_id, display_path, mutation_count FROM protected_resources ORDER BY resource_id"
    )
    return [dict(r) for r in cur.fetchall()]

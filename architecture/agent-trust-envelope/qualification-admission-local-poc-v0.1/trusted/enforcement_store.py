"""ATE Qualification & Admission Local PoC v0.1 — executor-owned enforcement store.

Per design §17 the minimum SQLite tables are:

  control_state(singleton, current_epoch)
  applied_control_records(record_id PRIMARY KEY, target_type, target_id,
    target_digest, status, issued_at, applied_at, applied_epoch UNIQUE,
    record_digest UNIQUE)
  execution_nonces(nonce PRIMARY KEY, action_digest, reserved_at, status)
  protected_resource(resource_id PRIMARY KEY, value, mutation_count)
  audit(sequence INTEGER PRIMARY KEY, event_type, payload_json,
    previous_hash, event_hash UNIQUE, created_at)

Recommended SQLite controls (§17):
  journal_mode=WAL
  synchronous=FULL
  foreign_keys=ON
  BEGIN IMMEDIATE for EAP/control application

This module provides:
  - open_store() — opens the DB with WAL + synchronous=FULL + foreign_keys=ON,
    initializes the schema.
  - EnforcedTransaction — context manager that uses BEGIN IMMEDIATE for
    EAP and control-record application (frozen §17, §23, §25).
  - append_audit() — append an audit row with previous-hash chaining.
  - read_audit() / read_control_state() / read_protected_resource() for
    the read paths used by evidence collection.
"""

from __future__ import annotations

import hashlib
import json
import os
import sqlite3
from contextlib import contextmanager
from dataclasses import dataclass
from typing import Iterator, List, Optional

SCHEMA_STATEMENTS = [
    """CREATE TABLE IF NOT EXISTS control_state (
        singleton INTEGER PRIMARY KEY CHECK (singleton = 1),
        current_epoch INTEGER NOT NULL
    )""",
    """CREATE TABLE IF NOT EXISTS applied_control_records (
        record_id TEXT PRIMARY KEY,
        target_type TEXT NOT NULL,
        target_id TEXT NOT NULL,
        target_digest TEXT,
        status TEXT NOT NULL,
        issued_at_unix_ms INTEGER NOT NULL,
        applied_at_unix_ms INTEGER NOT NULL,
        applied_epoch INTEGER UNIQUE NOT NULL,
        record_digest TEXT UNIQUE NOT NULL
    )""",
    """CREATE TABLE IF NOT EXISTS execution_nonces (
        nonce TEXT PRIMARY KEY,
        action_digest TEXT NOT NULL,
        reserved_at_unix_ms INTEGER NOT NULL,
        status TEXT NOT NULL
    )""",
    """CREATE TABLE IF NOT EXISTS protected_resource (
        resource_id TEXT PRIMARY KEY,
        value TEXT NOT NULL,
        mutation_count INTEGER NOT NULL DEFAULT 0
    )""",
    """CREATE TABLE IF NOT EXISTS audit (
        sequence INTEGER PRIMARY KEY AUTOINCREMENT,
        event_type TEXT NOT NULL,
        payload_json TEXT NOT NULL,
        previous_hash TEXT NOT NULL,
        event_hash TEXT UNIQUE NOT NULL,
        created_at_unix_ms INTEGER NOT NULL
    )""",
]

INITIAL_EPOCH = 0


def open_store(db_path: str) -> sqlite3.Connection:
    """Open the executor-owned enforcement store.

    Caller is responsible for the file ownership / mode (set by
    bootstrap). This function applies WAL + synchronous=FULL +
    foreign_keys=ON and initializes the schema.
    """
    conn = sqlite3.connect(db_path, timeout=30.0, isolation_level=None)
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA synchronous=FULL")
    conn.execute("PRAGMA foreign_keys=ON")
    for stmt in SCHEMA_STATEMENTS:
        conn.execute(stmt)
    # Seed control_state singleton if missing
    cur = conn.execute("SELECT current_epoch FROM control_state WHERE singleton=1")
    row = cur.fetchone()
    if row is None:
        conn.execute(
            "INSERT INTO control_state (singleton, current_epoch) VALUES (1, ?)",
            (INITIAL_EPOCH,),
        )
    return conn


@contextmanager
def eap_transaction(conn: sqlite3.Connection) -> Iterator[sqlite3.Connection]:
    """Use BEGIN IMMEDIATE for the EAP transaction (frozen §17 + §23).

    The caller must issue all writes inside this block and call
    `conn.execute("COMMIT")` explicitly on success. On exception, the
    context manager issues ROLLBACK and re-raises.
    """
    conn.execute("BEGIN IMMEDIATE")
    try:
        yield conn
    except BaseException:
        try:
            conn.execute("ROLLBACK")
        except sqlite3.OperationalError:
            pass
        raise


def append_audit(
    conn: sqlite3.Connection,
    *,
    event_type: str,
    payload: dict,
    created_at_unix_ms: int,
) -> int:
    """Append one audit row. Returns the new sequence number.

    Chains via SHA-256(previous_hash || canonical_json(payload)) per §26.
    """
    from qa_poc.canonical import canonical_json_bytes

    cur = conn.execute("SELECT COALESCE(MAX(sequence), 0) FROM audit")
    last_seq = int(cur.fetchone()[0])
    cur = conn.execute("SELECT event_hash FROM audit WHERE sequence=?", (last_seq,))
    row = cur.fetchone()
    prev_hash = row[0] if row else ""
    payload_bytes = canonical_json_bytes(payload)
    h = hashlib.sha256()
    h.update(prev_hash.encode("ascii"))
    h.update(b"\x00")
    h.update(payload_bytes)
    event_hash = h.hexdigest()
    cur = conn.execute(
        "INSERT INTO audit (event_type, payload_json, previous_hash, event_hash, created_at_unix_ms) VALUES (?, ?, ?, ?, ?)",
        (event_type, payload_bytes.decode("utf-8"), prev_hash, event_hash, created_at_unix_ms),
    )
    return int(cur.lastrowid)


def read_audit(conn: sqlite3.Connection) -> List[dict]:
    rows = conn.execute(
        "SELECT sequence, event_type, payload_json, previous_hash, event_hash, created_at_unix_ms FROM audit ORDER BY sequence ASC"
    ).fetchall()
    return [
        {
            "sequence": r[0],
            "event_type": r[1],
            "payload_json": r[2],
            "previous_hash": r[3],
            "event_hash": r[4],
            "created_at_unix_ms": r[5],
        }
        for r in rows
    ]


def verify_audit_chain(conn: sqlite3.Connection) -> bool:
    """Return True iff the audit chain is internally consistent.

    Recomputes each event_hash from (previous_hash, payload) and confirms
    equality with the stored hash.
    """
    from qa_poc.canonical import canonical_json_bytes

    rows = conn.execute(
        "SELECT sequence, payload_json, previous_hash, event_hash FROM audit ORDER BY sequence ASC"
    ).fetchall()
    expected_prev = ""
    for seq, payload_json, prev_hash, event_hash in rows:
        if prev_hash != expected_prev:
            return False
        payload_obj = json.loads(payload_json)
        canonical = canonical_json_bytes(payload_obj)
        h = hashlib.sha256()
        h.update(prev_hash.encode("ascii"))
        h.update(b"\x00")
        h.update(canonical)
        if h.hexdigest() != event_hash:
            return False
        expected_prev = event_hash
    return True


def current_epoch(conn: sqlite3.Connection) -> int:
    return int(conn.execute("SELECT current_epoch FROM control_state WHERE singleton=1").fetchone()[0])


def set_epoch(conn: sqlite3.Connection, new_epoch: int) -> None:
    conn.execute("UPDATE control_state SET current_epoch=? WHERE singleton=1", (new_epoch,))


def reserve_nonce(
    conn: sqlite3.Connection,
    *,
    nonce: str,
    action_digest: str,
    reserved_at_unix_ms: int,
) -> bool:
    """Insert the nonce if not already present. Returns True iff inserted.

    Used at EAP to verify the nonce is unused (frozen §23 step "verify
    nonce unused" + "insert nonce reservation").
    """
    cur = conn.execute(
        "INSERT OR IGNORE INTO execution_nonces (nonce, action_digest, reserved_at_unix_ms, status) VALUES (?, ?, ?, ?)",
        (nonce, action_digest, reserved_at_unix_ms, "RESERVED"),
    )
    return cur.rowcount > 0


def mark_nonce_executed(conn: sqlite3.Connection, nonce: str) -> None:
    conn.execute(
        "UPDATE execution_nonces SET status='EXECUTED' WHERE nonce=?",
        (nonce,),
    )


def read_protected_resource(conn: sqlite3.Connection, resource_id: str) -> Optional[dict]:
    cur = conn.execute(
        "SELECT resource_id, value, mutation_count FROM protected_resource WHERE resource_id=?",
        (resource_id,),
    )
    row = cur.fetchone()
    if row is None:
        return None
    return {"resource_id": row[0], "value": row[1], "mutation_count": row[2]}


def mutate_protected_resource(
    conn: sqlite3.Connection, *, resource_id: str, new_value: str
) -> int:
    """Idempotent upsert that increments mutation_count. Returns new count."""
    cur = conn.execute(
        "SELECT mutation_count FROM protected_resource WHERE resource_id=?",
        (resource_id,),
    )
    row = cur.fetchone()
    if row is None:
        conn.execute(
            "INSERT INTO protected_resource (resource_id, value, mutation_count) VALUES (?, ?, 1)",
            (resource_id, new_value),
        )
        return 1
    new_count = int(row[0]) + 1
    conn.execute(
        "UPDATE protected_resource SET value=?, mutation_count=? WHERE resource_id=?",
        (new_value, new_count, resource_id),
    )
    return new_count


def insert_protected_resource(conn: sqlite3.Connection, *, resource_id: str, value: str) -> None:
    """Seed an initial protected resource row (called by bootstrap/fixture)."""
    conn.execute(
        "INSERT OR IGNORE INTO protected_resource (resource_id, value, mutation_count) VALUES (?, ?, 0)",
        (resource_id, value),
    )



# === FR-9: deterministic SQLite write-lock barriers ==========================
#
# QA-P11 requires deterministic ordering between a control-record transaction
# and an EAP transaction. The EAP uses BEGIN IMMEDIATE (acquires the SQLite
# write lock); any concurrent write against the same DB will block until the
# EAP commits or rolls back, or will return SQLITE_BUSY after the busy_timeout.
#
# The helpers below expose a test-only barrier mechanism using a SEPARATE
# sqlite3 connection that acquires BEGIN IMMEDIATE first. A second connection
# then attempts to write — it blocks (or returns SQLITE_BUSY depending on
# busy_timeout). When the first commits, the second's write proceeds against
# the post-commit state. This is fully deterministic: no sleeps, no timing
# inference.
#
# These helpers are used by case_p11a / case_p11b in tests/case_functions.py.

class BarrierLockHeld(Exception):
    pass


class SQLiteBarrier:
    """Two-connection barrier against a single on-disk SQLite DB.

    Usage:
        barrier = SQLiteBarrier(db_path)
        barrier.acquire_holding()       # conn A: BEGIN IMMEDIATE + ROLLBACK at end
        # conn B attempts write, observes SQLITE_BUSY or proceeds
        ...

    The holding connection does NOT commit its BEGIN IMMEDIATE; we ROLLBACK
    at the end so the test fixture isn't mutated. The competing write either
    saw SQLITE_BUSY (lock contended) or proceeded AFTER rollback (no
    contention).
    """

    def __init__(self, db_path: str):
        self.db_path = db_path
        self._holding_conn = None
        self._busy_timeout_ms = 200  # short; we want deterministic BUSY

    def acquire_holding(self) -> sqlite3.Connection:
        """Open a separate connection and BEGIN IMMEDIATE (acquires write lock)."""
        if self._holding_conn is not None:
            raise BarrierLockHeld("already holding")
        c = sqlite3.connect(self.db_path, timeout=0.5, isolation_level=None)
        c.execute("PRAGMA busy_timeout = 0")
        c.execute("BEGIN IMMEDIATE")
        self._holding_conn = c
        return c

    def release_holding(self):
        """ROLLBACK the holding transaction (so test fixture is unchanged)."""
        if self._holding_conn is None:
            return
        try:
            self._holding_conn.execute("ROLLBACK")
        finally:
            self._holding_conn.close()
            self._holding_conn = None

    def attempt_write(self, sql: str, params: tuple = ()) -> Tuple[bool, Optional[str]]:
        """Try to execute sql on a new short-lived connection. Returns
        (success, error_or_none). success=False means the write was blocked
        (SQLITE_BUSY).
        """
        c = sqlite3.connect(self.db_path, timeout=0.5, isolation_level=None)
        c.execute("PRAGMA busy_timeout = 0")
        try:
            c.execute(sql, params)
            return True, None
        except sqlite3.OperationalError as e:
            err = str(e)
            if "locked" in err.lower() or "busy" in err.lower():
                return False, err
            raise
        finally:
            c.close()

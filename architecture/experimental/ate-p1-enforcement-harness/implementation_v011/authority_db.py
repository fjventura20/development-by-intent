"""ATE P1 v0.1.1 — Single SQLite authority database.

Per v0.1.1 §3 and §C1: protected resource state, durable nonce state,
revocation state, audit records, and the authenticated audit anchor all
reside in ONE SQLite database and are mutated in ONE transaction.

Per v0.1.1 §C3: the audit anchor is stored separately from the audit
record sequence (in this same authority database) and updated atomically
with each audit append.

Per v0.1 §10: SQLite is acceptable provided the nonce transition is
transactional and uniqueness is enforced by schema constraints.

This module exposes low-level schema setup and connection helpers only.
Higher-level mutations live in privileged_executor.py where the
transactional pattern is enforced.
"""
from __future__ import annotations

import os
import sqlite3
from typing import Optional


# Schema (single authority DB)
SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS protected_resources (
    resource_id TEXT PRIMARY KEY,
    display_path TEXT NOT NULL,
    resource_credential_hex TEXT NOT NULL,
    state_json TEXT NOT NULL,
    mutation_count INTEGER NOT NULL DEFAULT 0,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS nonces (
    nonce TEXT PRIMARY KEY,
    state TEXT NOT NULL CHECK(state IN ('UNSEEN','RESERVED','CONSUMED')),
    reservation_id TEXT,
    decision_id TEXT NOT NULL,
    first_seen_at TEXT NOT NULL,
    finalized_at TEXT,
    outcome TEXT
);

CREATE TABLE IF NOT EXISTS revocations (
    subject_type TEXT NOT NULL,
    subject_id TEXT NOT NULL,
    revoked_at TEXT NOT NULL,
    reason TEXT NOT NULL,
    PRIMARY KEY(subject_type, subject_id)
);

CREATE TABLE IF NOT EXISTS audit_records (
    seq INTEGER PRIMARY KEY AUTOINCREMENT,
    event_ts TEXT NOT NULL,
    request_id TEXT NOT NULL,
    decision_id TEXT NOT NULL,
    nonce TEXT NOT NULL,
    resource_id TEXT NOT NULL,
    operation TEXT NOT NULL,
    target_display TEXT NOT NULL,
    outcome TEXT NOT NULL,
    reason_code TEXT,
    previous_digest TEXT NOT NULL,
    record_mac TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS audit_anchor (
    id INTEGER PRIMARY KEY CHECK(id = 1),
    final_seq INTEGER NOT NULL,
    final_record_digest TEXT NOT NULL,
    anchor_mac TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS executor_state (
    id INTEGER PRIMARY KEY CHECK(id = 1),
    audit_key_fingerprint TEXT NOT NULL,
    resource_credential_fingerprint TEXT NOT NULL,
    last_lock_reason TEXT,
    locked INTEGER NOT NULL DEFAULT 0
);

-- Privilege boundary at the DB layer:
--   - INSERT may set resource_credential_hex to any non-empty value
--     (the executor seeds it).
--   - UPDATE may NOT change resource_credential_hex (immutable). A
--     bypass attempt that submits UPDATE with a NEW row that omits
--     this column, sets it to NULL, or sets it to a different value,
--     will RAISE ABORT and the transaction will roll back.
--   - UPDATE may NOT change resource_id (immutable primary key).
-- This is the resource-module's privilege boundary enforced at the
-- DB schema level. The application-layer credential check is
-- additionally enforced by protected_resource.apply_mutation.
CREATE TRIGGER IF NOT EXISTS protected_resources_credential_immutable
BEFORE UPDATE ON protected_resources
FOR EACH ROW
WHEN OLD.resource_credential_hex != NEW.resource_credential_hex
BEGIN
    SELECT RAISE(ABORT, 'PX_RESOURCE_CREDENTIAL_IMMUTABLE');
END;

CREATE TRIGGER IF NOT EXISTS protected_resources_resource_id_immutable
BEFORE UPDATE ON protected_resources
FOR EACH ROW
WHEN OLD.resource_id != NEW.resource_id
BEGIN
    SELECT RAISE(ABORT, 'PX_RESOURCE_ID_IMMUTABLE');
END;

CREATE TABLE IF NOT EXISTS decision_signatures (
    decision_id TEXT PRIMARY KEY,
    signed_payload_json TEXT NOT NULL,
    signature_b64 TEXT NOT NULL
);

INSERT OR IGNORE INTO executor_state (id, audit_key_fingerprint, resource_credential_fingerprint, locked)
VALUES (1, '', '', 0);

INSERT OR IGNORE INTO audit_anchor (id, final_seq, final_record_digest, anchor_mac, updated_at)
VALUES (1, 0, '', '', '1970-01-01T00:00:00Z');
"""


def open_db(db_path: str) -> sqlite3.Connection:
    """Open the authority DB. Caller is responsible for transaction control."""
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    conn = sqlite3.connect(db_path, isolation_level=None, timeout=30.0)
    # NOTE: WAL mode is disabled for this PoC to keep DB file
    # permission isolation simple. The default journal mode
    # (rollback) creates a single .sqlite-journal sidecar that is
    # chowned together with the main DB. WAL would require
    # chowning -wal and -shm sidecars atomically with the DB,
    # which complicates the OS-level privilege boundary.
    # conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    conn.row_factory = sqlite3.Row
    _init_schema(conn)
    return conn


def _init_schema(conn: sqlite3.Connection) -> None:
    conn.executescript(SCHEMA_SQL)


def reset_db(db_path: str) -> None:
    """Hard-reset the authority DB (test isolation helper)."""
    if os.path.exists(db_path):
        os.unlink(db_path)
    open_db(db_path).close()

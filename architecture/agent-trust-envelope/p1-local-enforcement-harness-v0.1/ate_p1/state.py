from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Any


class EnforcementState:
    def __init__(self, db_path: str | Path):
        self.db_path = str(db_path)
        self._init_db()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path, timeout=10.0, isolation_level=None)
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA synchronous=FULL")
        return conn

    def _init_db(self) -> None:
        with self._connect() as conn:
            conn.executescript(
                """
                CREATE TABLE IF NOT EXISTS nonces (
                    nonce TEXT PRIMARY KEY,
                    envelope_id TEXT NOT NULL,
                    consumed_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                );
                CREATE TABLE IF NOT EXISTS revocations (
                    subject_id TEXT PRIMARY KEY,
                    reason TEXT NOT NULL,
                    revoked_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                );
                CREATE TABLE IF NOT EXISTS audit (
                    sequence INTEGER PRIMARY KEY AUTOINCREMENT,
                    event_type TEXT NOT NULL,
                    envelope_id TEXT NOT NULL,
                    payload_json TEXT NOT NULL,
                    previous_hash TEXT NOT NULL,
                    event_hash TEXT NOT NULL UNIQUE,
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                );
                """
            )

    def consume_nonce(self, nonce: str, envelope_id: str) -> bool:
        conn = self._connect()
        try:
            conn.execute("BEGIN IMMEDIATE")
            try:
                conn.execute(
                    "INSERT INTO nonces(nonce, envelope_id) VALUES (?, ?)",
                    (nonce, envelope_id),
                )
            except sqlite3.IntegrityError:
                conn.execute("ROLLBACK")
                return False
            conn.execute("COMMIT")
            return True
        finally:
            conn.close()

    def nonce_consumed(self, nonce: str) -> bool:
        with self._connect() as conn:
            return conn.execute("SELECT 1 FROM nonces WHERE nonce = ?", (nonce,)).fetchone() is not None

    def revoke(self, subject_id: str, reason: str) -> None:
        with self._connect() as conn:
            conn.execute(
                "INSERT OR REPLACE INTO revocations(subject_id, reason) VALUES (?, ?)",
                (subject_id, reason),
            )

    def is_revoked(self, subject_id: str) -> bool:
        with self._connect() as conn:
            return conn.execute("SELECT 1 FROM revocations WHERE subject_id = ?", (subject_id,)).fetchone() is not None

    def audit_rows(self) -> list[dict[str, Any]]:
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT sequence,event_type,envelope_id,payload_json,previous_hash,event_hash,created_at FROM audit ORDER BY sequence"
            ).fetchall()
        return [
            {
                "sequence": r[0],
                "event_type": r[1],
                "envelope_id": r[2],
                "payload": json.loads(r[3]),
                "previous_hash": r[4],
                "event_hash": r[5],
                "created_at": r[6],
            }
            for r in rows
        ]

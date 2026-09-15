from __future__ import annotations

import hashlib
import json

from .state import EnforcementState

GENESIS = "0" * 64


def canonical_json(value: object) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def event_hash(previous_hash: str, event_type: str, envelope_id: str, payload_json: str) -> str:
    material = "|".join([previous_hash, event_type, envelope_id, payload_json]).encode("utf-8")
    return hashlib.sha256(material).hexdigest()


def append_event(state: EnforcementState, event_type: str, envelope_id: str, payload: dict) -> str:
    payload_json = canonical_json(payload)
    conn = state._connect()
    try:
        conn.execute("BEGIN IMMEDIATE")
        row = conn.execute("SELECT event_hash FROM audit ORDER BY sequence DESC LIMIT 1").fetchone()
        previous = row[0] if row else GENESIS
        digest = event_hash(previous, event_type, envelope_id, payload_json)
        conn.execute(
            "INSERT INTO audit(event_type,envelope_id,payload_json,previous_hash,event_hash) VALUES (?,?,?,?,?)",
            (event_type, envelope_id, payload_json, previous, digest),
        )
        conn.execute("COMMIT")
        return digest
    finally:
        conn.close()


def verify_chain(state: EnforcementState) -> bool:
    rows = state.audit_rows()
    previous = GENESIS
    expected_sequence = 1
    for row in rows:
        if row["sequence"] != expected_sequence:
            return False
        payload_json = canonical_json(row["payload"])
        expected = event_hash(previous, row["event_type"], row["envelope_id"], payload_json)
        if row["previous_hash"] != previous or row["event_hash"] != expected:
            return False
        previous = row["event_hash"]
        expected_sequence += 1
    return True

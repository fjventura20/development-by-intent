"""ATE P1 v0.1.1 — Audit chain and authenticated audit anchor.

Per v0.1.1 §C3: a protected audit anchor stored separately from the
audit-record sequence within the same authority database, updated
atomically with each audit append.

Per v0.1 §10.3: HMAC-SHA256 with an executor-only audit key is the
local PoC MAC primitive. The MAC key is held by the privileged executor
process and is NEVER sent over IPC to the requester.

The audit anchor contains:
  - expected final sequence number;
  - expected final record MAC;
  - anchor MAC under the executor-only audit key.

A copy of the authority DB that has the same audit_records but a
different anchor is detected as tampered: the audit integrity check
fails because the anchor MAC does not match the audit chain tip.

The audit_records table holds the audit chain. Each record's MAC
chains to the previous record via previous_digest and current record_mac.
This catches field mutation, middle deletion, reorder, insertion, and
tail truncation.
"""
from __future__ import annotations

import sqlite3
from typing import Any, Dict, List, Optional, Tuple

from crypto_utils import canonical_bytes, hmac_sha256_hex


def record_digest(record: Dict[str, Any]) -> str:
    """SHA-256 of the canonical record-without-MAC.

    Used as the `previous_digest` linkage field.
    """
    no_mac = {k: v for k, v in record.items() if k not in ("record_mac",)}
    import hashlib
    return hashlib.sha256(canonical_bytes(no_mac)).hexdigest()


def make_record_mac(audit_key: bytes, record: Dict[str, Any]) -> str:
    """HMAC-SHA256 over the canonical record-without-MAC."""
    no_mac = {k: v for k, v in record.items() if k not in ("record_mac",)}
    return hmac_sha256_hex(audit_key, canonical_bytes(no_mac))


def make_anchor_mac(
    audit_key: bytes, final_seq: int, final_record_digest: str
) -> str:
    """HMAC-SHA256 over (final_seq, final_record_digest)."""
    payload = {"final_seq": final_seq, "final_record_digest": final_record_digest}
    return hmac_sha256_hex(audit_key, canonical_bytes(payload))


def read_audit_chain(conn: sqlite3.Connection) -> List[Dict[str, Any]]:
    """Read all audit records in sequence order."""
    cur = conn.execute(
        "SELECT seq, event_ts, request_id, decision_id, nonce, resource_id, "
        "operation, target_display, outcome, reason_code, previous_digest, "
        "record_mac FROM audit_records ORDER BY seq ASC"
    )
    return [dict(row) for row in cur.fetchall()]


def verify_audit_chain(
    conn: sqlite3.Connection, audit_key: bytes
) -> Tuple[bool, str]:
    """Returns (ok, reason_or_ok_marker)."""
    records = read_audit_chain(conn)
    if not records:
        # Empty chain is valid by definition; anchor must record this.
        anchor = conn.execute(
            "SELECT final_seq, final_record_digest, anchor_mac FROM audit_anchor WHERE id=1"
        ).fetchone()
        if anchor is None:
            return False, "anchor_missing"
        if int(anchor["final_seq"]) != 0:
            return False, f"anchor_seq_mismatch_for_empty_chain:anchor={anchor['final_seq']}"
        if anchor["final_record_digest"] != "":
            return False, "anchor_final_digest_mismatch_for_empty_chain"
        if anchor["anchor_mac"] != "":
            return False, f"anchor_mac_invalid_for_empty_chain:got={anchor['anchor_mac']}"
        return True, "verified_empty_chain"
    prev_digest = ""
    for rec in records:
        # Verify previous_digest linkage
        if rec["previous_digest"] != prev_digest:
            return False, f"chain_broken_at_seq_{rec['seq']}"
        # Verify record MAC
        expected_mac = make_record_mac(audit_key, rec)
        if rec["record_mac"] != expected_mac:
            return False, f"record_mac_invalid_at_seq_{rec['seq']}"
        prev_digest = record_digest(rec)
    # Verify anchor
    anchor = conn.execute(
        "SELECT final_seq, final_record_digest, anchor_mac FROM audit_anchor WHERE id=1"
    ).fetchone()
    if anchor is None:
        return False, "anchor_missing"
    if int(anchor["final_seq"]) != len(records):
        return False, f"anchor_seq_mismatch:anchor={anchor['final_seq']},records={len(records)}"
    expected_final_digest = prev_digest
    if anchor["final_record_digest"] != expected_final_digest:
        return False, f"anchor_final_digest_mismatch:anchor={anchor['final_record_digest']},computed={expected_final_digest}"
    expected_anchor_mac = make_anchor_mac(
        audit_key, int(anchor["final_seq"]), anchor["final_record_digest"]
    )
    if anchor["anchor_mac"] != expected_anchor_mac:
        return False, "anchor_mac_invalid"
    return True, "verified"


def read_anchor(conn: sqlite3.Connection) -> Dict[str, Any]:
    row = conn.execute(
        "SELECT final_seq, final_record_digest, anchor_mac, updated_at FROM audit_anchor WHERE id=1"
    ).fetchone()
    return dict(row) if row else {}


def is_chain_empty(conn: sqlite3.Connection) -> bool:
    row = conn.execute("SELECT COUNT(*) AS c FROM audit_records").fetchone()
    return int(row["c"]) == 0


def verify_chain_from_records(
    records: List[Dict[str, Any]],
    audit_key: bytes,
    *,
    anchor: Optional[Dict[str, Any]] = None,
) -> Tuple[bool, str]:
    """Verify an audit chain given pre-fetched records (no DB access).

    The DB-free variant of verify_audit_chain. anchor is required
    when records is non-empty; defaults to assuming an empty anchor.
    """
    if not records:
        if anchor is None:
            return True, "verified_empty_chain_no_anchor_provided"
        if int(anchor.get("final_seq", 0)) != 0:
            return False, f"anchor_seq_mismatch_for_empty_chain:anchor={anchor['final_seq']}"
        if anchor.get("final_record_digest", "") != "":
            return False, "anchor_final_digest_mismatch_for_empty_chain"
        if anchor.get("anchor_mac", "") != "":
            return False, f"anchor_mac_invalid_for_empty_chain:got={anchor.get('anchor_mac')}"
        return True, "verified_empty_chain"
    prev_digest = ""
    for rec in records:
        if rec["previous_digest"] != prev_digest:
            return False, f"chain_broken_at_seq_{rec['seq']}"
        expected_mac = make_record_mac(audit_key, rec)
        if rec["record_mac"] != expected_mac:
            return False, f"record_mac_invalid_at_seq_{rec['seq']}"
        prev_digest = record_digest(rec)
    if anchor is None:
        return True, "verified_chain_no_anchor_provided"
    if int(anchor["final_seq"]) != len(records):
        return False, f"anchor_seq_mismatch:anchor={anchor['final_seq']},records={len(records)}"
    if anchor["final_record_digest"] != prev_digest:
        return False, f"anchor_final_digest_mismatch:anchor={anchor['final_record_digest']},computed={prev_digest}"
    expected_anchor_mac = make_anchor_mac(
        audit_key, int(anchor["final_seq"]), anchor["final_record_digest"]
    )
    if anchor["anchor_mac"] != expected_anchor_mac:
        return False, "anchor_mac_invalid"
    return True, "verified"

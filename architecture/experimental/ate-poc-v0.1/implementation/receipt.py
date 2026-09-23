"""FixtureAcceptanceReceipt per ATE-POC-DESIGN-v0.1 §2.3.

Frozen structure (per v0.2.1 §B.4 reuse):
  FixtureAcceptanceReceipt = {
    receipt_id, charter_sha256, session_id, issued_at_utc,
    gel_unlocks_to
  }

Frozen freshness window (default 3600s = 1h).
"""
import hashlib

from crypto_utils import canonicalize_json


SCHEMA_ID = "TGE-ATE/0.1"
RECEIPT_FRESHNESS_WINDOW_SECONDS = 3600


def make_receipt(*, session_id: str, charter_sha256: str, issued_at_utc: int,
                 gel_unlocks_to: str = "ate_trust_envelope",
                 receipt_id = None) -> dict:
    """Make a fixture acceptance receipt.

    NOTE: per ATE-POC-DESIGN-v0.1 §2.3, this is a *fixture*. No
    cryptographic signature. The receipt is consumed as a token,
    not as cryptographic evidence.
    """
    if receipt_id is None:
        import hashlib as _h
        receipt_id = _h.sha256(
            (session_id + ":" + charter_sha256 + ":" + str(issued_at_utc)).encode("utf-8")
        ).hexdigest()[:32]
    return {
        "schema_id": SCHEMA_ID,
        "receipt_id": receipt_id,
        "charter_sha256": charter_sha256,
        "session_id": session_id,
        "issued_at_utc": issued_at_utc,
        "gel_unlocks_to": gel_unlocks_to,
    }


def verify_receipt(receipt, *, expected_charter_sha256: str, expected_session_id: str,
                   current_time: int) -> tuple:
    """Verify a receipt. Returns (ok, reason_code, reason_description, details)."""
    if receipt is None:
        return (False, "GX_RECEIPT_MISSING", "receipt_is_none", {})
    if not isinstance(receipt, dict):
        return (False, "GX_RECEIPT_MALFORMED", "receipt_not_a_dict", {})
    required = {"schema_id", "receipt_id", "charter_sha256", "session_id", "issued_at_utc", "gel_unlocks_to"}
    missing = required - set(receipt.keys())
    if missing:
        return (False, "GX_RECEIPT_MALFORMED", f"missing_fields:{sorted(missing)}", {"missing": sorted(missing)})
    if receipt.get("schema_id") != SCHEMA_ID:
        return (False, "GX_RECEIPT_INVALID", f"bad_schema_id:{receipt.get('schema_id')!r}", {})
    if not receipt.get("receipt_id"):
        return (False, "GX_RECEIPT_INVALID", "missing_receipt_id", {})
    if receipt.get("charter_sha256") != expected_charter_sha256:
        return (False, "GX_RECEIPT_TAMPERED",
                f"receipt_charter_sha256={receipt.get('charter_sha256')!r} != expected={expected_charter_sha256!r}",
                {"receipt_charter_sha256": receipt.get("charter_sha256"), "expected": expected_charter_sha256})
    if receipt.get("session_id") != expected_session_id:
        return (False, "GX_SESSION_MISMATCH",
                f"receipt_session_id={receipt.get('session_id')!r} != expected={expected_session_id!r}",
                {"receipt_session_id": receipt.get("session_id"), "expected": expected_session_id})
    issued_at_utc = receipt.get("issued_at_utc", 0)
    age = current_time - issued_at_utc
    if age > RECEIPT_FRESHNESS_WINDOW_SECONDS:
        return (False, "GX_RECEIPT_EXPIRED",
                f"receipt_age={age}s > freshness_window={RECEIPT_FRESHNESS_WINDOW_SECONDS}s",
                {"age_seconds": age, "freshness_window_seconds": RECEIPT_FRESHNESS_WINDOW_SECONDS,
                 "issued_at_utc": issued_at_utc, "now": current_time})
    if issued_at_utc > current_time + 60:
        # receipt issued in the future: not yet valid
        return (False, "GX_RECEIPT_NOT_YET_VALID",
                f"issued_at_utc={issued_at_utc} > now={current_time}",
                {"issued_at_utc": issued_at_utc, "now": current_time})

    return (True, "PASS", "receipt_valid",
            {"age_seconds": age, "freshness_window_seconds": RECEIPT_FRESHNESS_WINDOW_SECONDS})


def receipt_hash(receipt: dict) -> str:
    return hashlib.sha256(canonicalize_json(receipt)).hexdigest()

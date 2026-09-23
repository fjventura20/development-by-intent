"""AcceptanceReceipt v0.2.1 (supersedes v0.1).

Frozen structure (v0.2.1 adds identity_fingerprint):
  AcceptanceReceipt = {
    schema_id, receipt_id, charter_sha256, session_id,
    identity_fingerprint, issued_at_utc, gel_unlocks_to,
    signature_b64
  }

The signature is Ed25519 over canonicalize_without_signature(receipt),
signed by the TGE-fixture key (K_TGE).
"""
from crypto_utils_v2 import sign, verify

SCHEMA_ID = "TGE-ATE-V2-RECEIPT/0.1"


def make_receipt(*, receipt_id, charter_sha256, session_id,
                 identity_fingerprint, issued_at_utc, gel_unlocks_to,
                 tge_priv_key):
    r = {
        "schema_id": SCHEMA_ID,
        "receipt_id": receipt_id,
        "charter_sha256": charter_sha256,
        "session_id": session_id,
        "identity_fingerprint": identity_fingerprint,
        "issued_at_utc": issued_at_utc,
        "gel_unlocks_to": gel_unlocks_to,
    }
    r["signature_b64"] = sign(tge_priv_key, r)
    return r


def verify_receipt(r, tge_pub_key):
    if r.get("schema_id") != SCHEMA_ID:
        return False, "schema_id_mismatch"
    if "signature_b64" not in r:
        return False, "missing_signature"
    ok = verify(tge_pub_key, r, r["signature_b64"])
    if not ok:
        return False, "signature_invalid"
    return True, "verified"

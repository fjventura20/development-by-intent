"""SessionContext v0.2.1 (NEW).

Frozen structure:
  SessionContext = {
    schema_id, session_id, identity_fingerprint,
    receipt_id_predicate, capability_id_predicate,
    valid_from_utc, valid_until_utc, issued_at_utc,
    signature_b64
  }

The runtime holds the signing key for SessionContext.
The SessionContext binds the session to:
  - the identity fingerprint (cross-binding to IdentityAttestation)
  - expected receipt_id + capability_id (binding to Receipt and Capability)
"""
from crypto_utils_v2 import sign, verify

SCHEMA_ID = "TGE-ATE-V2-SESSION/0.1"


def make_session_context(*, session_id, identity_fingerprint,
                         receipt_id_predicate, capability_id_predicate,
                         valid_from_utc, valid_until_utc, issued_at_utc,
                         runtime_priv_key):
    sc = {
        "schema_id": SCHEMA_ID,
        "session_id": session_id,
        "identity_fingerprint": identity_fingerprint,
        "receipt_id_predicate": receipt_id_predicate,
        "capability_id_predicate": capability_id_predicate,
        "valid_from_utc": valid_from_utc,
        "valid_until_utc": valid_until_utc,
        "issued_at_utc": issued_at_utc,
    }
    sc["signature_b64"] = sign(runtime_priv_key, sc)
    return sc


def verify_session_context(sc, runtime_pub_key):
    if sc.get("schema_id") != SCHEMA_ID:
        return False, "schema_id_mismatch"
    if "signature_b64" not in sc:
        return False, "missing_signature"
    ok = verify(runtime_pub_key, sc, sc["signature_b64"])
    if not ok:
        return False, "signature_invalid"
    return True, "verified"

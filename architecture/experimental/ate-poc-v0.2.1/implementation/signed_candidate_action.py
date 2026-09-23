"""SignedCandidateAction v0.2.1 (NEW).

Frozen structure:
  SignedCandidateAction = {
    schema_id, action_struct, session_id, envelope_nonce,
    capability_id, receipt_id, identity_fingerprint,
    action_preimage_hash, signed_at_utc, signature_b64
  }

Signed by K_IDENTITY (runtime).
"""
from crypto_utils_v2 import sign, verify, canonicalize_json, fingerprint_obj

SCHEMA_ID = "TGE-ATE-V2-SIGNED-ACTION/0.1"


def make_signed_candidate_action(*, action_struct, session_id, envelope_nonce,
                                 capability_id, receipt_id,
                                 identity_fingerprint, signed_at_utc,
                                 runtime_priv_key):
    action_preimage_hash = fingerprint_obj(action_struct)
    sca = {
        "schema_id": SCHEMA_ID,
        "action_struct": action_struct,
        "session_id": session_id,
        "envelope_nonce": envelope_nonce,
        "capability_id": capability_id,
        "receipt_id": receipt_id,
        "identity_fingerprint": identity_fingerprint,
        "action_preimage_hash": action_preimage_hash,
        "signed_at_utc": signed_at_utc,
    }
    sca["signature_b64"] = sign(runtime_priv_key, sca)
    return sca


def verify_signed_candidate_action(sca, runtime_pub_key):
    if sca.get("schema_id") != SCHEMA_ID:
        return False, "schema_id_mismatch"
    if "signature_b64" not in sca:
        return False, "missing_signature"
    # Verify action_preimage_hash matches action_struct
    expected = fingerprint_obj(sca["action_struct"])
    if sca.get("action_preimage_hash") != expected:
        return False, "action_preimage_hash_mismatch"
    ok = verify(runtime_pub_key, sca, sca["signature_b64"])
    if not ok:
        return False, "signature_invalid"
    return True, "verified"


def signed_action_fingerprint(sca):
    return fingerprint_obj(sca)

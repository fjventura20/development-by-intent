"""SignedExecutedAction v0.2.1 (NEW).

Frozen structure:
  SignedExecutedAction = {
    schema_id, original_action_hash, executed_action_struct,
    rule_id, evaluated_at_utc, signature_b64
  }

Signed by K_GEL (GEL-fixture key).
"""
from crypto_utils_v2 import sign, verify, fingerprint_obj

SCHEMA_ID = "TGE-ATE-V2-EXECUTED/0.1"


def make_signed_executed_action(*, original_signed_action_fingerprint,
                                executed_action_struct, rule_id,
                                evaluated_at_utc, gel_priv_key):
    sea = {
        "schema_id": SCHEMA_ID,
        "original_action_hash": original_signed_action_fingerprint,
        "executed_action_struct": executed_action_struct,
        "rule_id": rule_id,
        "evaluated_at_utc": evaluated_at_utc,
    }
    sea["signature_b64"] = sign(gel_priv_key, sea)
    return sea


def verify_signed_executed_action(sea, gel_pub_key):
    if sea.get("schema_id") != SCHEMA_ID:
        return False, "schema_id_mismatch"
    if "signature_b64" not in sea:
        return False, "missing_signature"
    ok = verify(gel_pub_key, sea, sea["signature_b64"])
    if not ok:
        return False, "signature_invalid"
    return True, "verified"


def executed_action_fingerprint(sea):
    return fingerprint_obj(sea)

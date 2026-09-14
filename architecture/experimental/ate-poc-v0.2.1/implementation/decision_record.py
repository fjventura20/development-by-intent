"""DecisionRecord v0.2.1.

Frozen structure (extends v0.1 with extended fields):
  DecisionRecord = {
    schema_id, decision_id, operation_mode,
    envelope_binding_hash, envelope_nonce,
    identity_fingerprint, receipt_fingerprint,
    capability_fingerprint, action_fingerprint,
    executed_action_fingerprint, audit_trail,
    verdict, reason_code, replay_check_result,
    nonce_state_observed, execution_boundary_reached,
    candidate_action_fingerprint, previous_decision_id,
    issued_at_utc, decision_signature_b64
  }

Signed by K_PIPELINE.

The signed region excludes 'decision_signature_b64'.
"""
from crypto_utils_v2 import sign, verify, canonicalize_json, fingerprint_obj

SCHEMA_ID = "TGE-ATE-V2-DECISION/0.1"


def make_decision_record(*, decision_id, operation_mode,
                         envelope_binding_hash, envelope_nonce,
                         identity_fingerprint, receipt_fingerprint,
                         capability_fingerprint, action_fingerprint,
                         executed_action_fingerprint, audit_trail,
                         verdict, reason_code, replay_check_result,
                         nonce_state_observed, execution_boundary_reached,
                         candidate_action_fingerprint, previous_decision_id,
                         issued_at_utc, pipeline_priv_key):
    dr = {
        "schema_id": SCHEMA_ID,
        "decision_id": decision_id,
        "operation_mode": operation_mode,
        "envelope_binding_hash": envelope_binding_hash,
        "envelope_nonce": envelope_nonce,
        "identity_fingerprint": identity_fingerprint,
        "receipt_fingerprint": receipt_fingerprint,
        "capability_fingerprint": capability_fingerprint,
        "action_fingerprint": action_fingerprint,
        "executed_action_fingerprint": executed_action_fingerprint,
        "audit_trail": audit_trail,
        "verdict": verdict,
        "reason_code": reason_code,
        "replay_check_result": replay_check_result,
        "nonce_state_observed": nonce_state_observed,
        "execution_boundary_reached": execution_boundary_reached,
        "candidate_action_fingerprint": candidate_action_fingerprint,
        "previous_decision_id": previous_decision_id,
        "issued_at_utc": issued_at_utc,
    }
    dr["decision_signature_b64"] = sign(pipeline_priv_key, dr)
    return dr


def verify_decision_record(dr, pipeline_pub_key):
    if dr.get("schema_id") != SCHEMA_ID:
        return False, "schema_id_mismatch"
    if "decision_signature_b64" not in dr:
        return False, "missing_signature"
    ok = verify(pipeline_pub_key, dr, dr["decision_signature_b64"])
    if not ok:
        return False, "signature_invalid"
    return True, "verified"


def decision_record_fingerprint(dr):
    return fingerprint_obj(dr)

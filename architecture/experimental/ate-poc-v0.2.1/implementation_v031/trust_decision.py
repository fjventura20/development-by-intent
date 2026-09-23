"""ATE v0.3.1 TrustDecision and trust_decide (per PI RULING 4 + Refinement B).

Pure non-mutating determinstic function:
  - validates evidence
  - evaluates G1..G8
  - produces TRUST_GRANTED or TRUST_DENIED
  - produces reason codes
  - constructs + signs the TrustDecision via K_TRUST_DECISION (independent
    authority fixture, OUTSIDE the participant agent's key custody)

Refinement B (mandatory): trust_decide() MUST NOT
  - consume the authorization nonce
  - mutate envelope state
  - mark an action executed
  - alter participant/session evidence

Nonce consumption happens ONLY in the governed-action executor
(see executor.py), AFTER a TRUST_GRANTED decision has been verified.
"""
from typing import Any, Dict, List, Tuple

from cryptography.hazmat.primitives.asymmetric.ed25519 import (
    Ed25519PrivateKey,
    Ed25519PublicKey,
)

from crypto_utils import (
    fingerprint_obj,
    pubkey_to_b64,
    sign,
    verify,
)
from nonce_registry import NonceRegistry, NonceState
from value_architecture_policy import va_compatible, verify_va_policy


SCHEMA_ID_TRUST_DECISION = "ATE-V3.1-TRUST-DECISION/0.1"
SCHEMA_ID_CAPABILITY = "ATE-V3.1-CAPABILITY/0.1"


# Reason codes (per v0.3.1 design §10)
GX_OK = "GX_OK"
GX_RUNTIME_BINDING = "GX_RUNTIME_BINDING"
GX_FRESHNESS_MISMATCH = "GX_FRESHNESS_MISMATCH"
GX_EVENT_SOURCE_NOT_LIFECYCLE = "GX_EVENT_SOURCE_NOT_LIFECYCLE"
GX_ACCEPTANCE_FINGERPRINT_CHAIN = "GX_ACCEPTANCE_FINGERPRINT_CHAIN"
GX_COA_SIGNATURE_INVALID = "GX_COA_SIGNATURE_INVALID"
GX_COA_SESSION_MISMATCH = "GX_COA_SESSION_MISMATCH"
GX_COA_PUBLIC_KEY_MISMATCH = "GX_COA_PUBLIC_KEY_MISMATCH"
GX_COA_FRESHNESS_MISMATCH = "GX_COA_FRESHNESS_MISMATCH"
GX_COA_EXPIRED = "GX_COA_EXPIRED"
GX_COA_NOT_BOUND_TO_LIVE_PROVENANCE = "GX_COA_NOT_BOUND_TO_LIVE_PROVENANCE"
GX_VA_POLICY_SIGNATURE_INVALID = "GX_VA_POLICY_SIGNATURE_INVALID"
GX_VA_POLICY_TRIPLE_MISMATCH = "GX_VA_POLICY_TRIPLE_MISMATCH"
GX_VA_POLICY_INCOMPATIBLE = "GX_VA_POLICY_INCOMPATIBLE"
GX_BEHAVIORAL_SIGNATURE_INVALID = "GX_BEHAVIORAL_SIGNATURE_INVALID"
GX_BEHAVIORAL_BATTERY_FAILED = "GX_BEHAVIORAL_BATTERY_FAILED"
GX_BEHAVIORAL_AGENT_MISMATCH = "GX_BEHAVIORAL_AGENT_MISMATCH"
GX_BEHAVIORAL_EXPIRED = "GX_BEHAVIORAL_EXPIRED"
GX_CAPABILITY_SIGNATURE_INVALID = "GX_CAPABILITY_SIGNATURE_INVALID"
GX_CAPABILITY_SESSION_MISMATCH = "GX_CAPABILITY_SESSION_MISMATCH"
GX_CAPABILITY_NOT_BOUND_TO_RECEIPT = "GX_CAPABILITY_NOT_BOUND_TO_RECEIPT"
GX_OPERATION_OUT_OF_SCOPE = "GX_OPERATION_OUT_OF_SCOPE"
GX_TARGET_OUT_OF_SCOPE = "GX_TARGET_OUT_OF_SCOPE"
GX_TARGET_EXCLUDED = "GX_TARGET_EXCLUDED"
GX_CAPABILITY_EXPIRED_OR_NOT_YET_VALID = "GX_CAPABILITY_EXPIRED_OR_NOT_YET_VALID"
GX_ACTION_RUNTIME_MISMATCH = "GX_ACTION_RUNTIME_MISMATCH"
GX_ACTION_FRESHNESS_MISMATCH = "GX_ACTION_FRESHNESS_MISMATCH"
GX_ACTION_ACCEPTANCE_CHAIN_BROKEN = "GX_ACTION_ACCEPTANCE_CHAIN_BROKEN"
GX_ACTION_SIGNATURE_INVALID = "GX_ACTION_SIGNATURE_INVALID"
GX_ENVELOPE_BINDING_HASH_MISMATCH = "GX_ENVELOPE_BINDING_HASH_MISMATCH"
GX_NONCE_NOT_UNSEEN = "GX_NONCE_NOT_UNSEEN"
GX_NONCE_PREVIOUSLY_AUTHORIZED = "GX_NONCE_PREVIOUSLY_AUTHORIZED"
GX_NONCE_PREVIOUSLY_CONSUMED = "GX_NONCE_PREVIOUSLY_CONSUMED"
GX_NONCE_UNKNOWN = "GX_NONCE_UNKNOWN"


def _deny(reason_code: str, detail: str = "") -> Dict[str, Any]:
    return {
        "verdict": "TRUST_DENIED",
        "reason_code": reason_code,
        "detail": detail,
    }


def _gate(gate_id: str, result: str, detail: str = "") -> Dict[str, str]:
    return {"gate": gate_id, "result": result, "detail": detail}


def trust_decide(
    envelope: Dict[str, Any],
    *,
    identity_att: Dict[str, Any],
    session_ctx: Dict[str, Any],
    sa: Dict[str, Any],
    sca: Dict[str, Any],
    receipt: Dict[str, Any],
    va_policy: Dict[str, Any],
    behavioral_receipt: Dict[str, Any],
    capability: Dict[str, Any],
    operator_freshness_challenge: str,
    now_utc: float,
    nonce_registry: NonceRegistry,
    # Authority public keys (for verification only; signing is via private)
    pub_key_identity: Ed25519PublicKey,
    pub_key_tge: Ed25519PublicKey,
    pub_key_va: Ed25519PublicKey,
    pub_key_behavioral: Ed25519PublicKey,
    pub_key_authority: Ed25519PublicKey,
    # Trust-decision authority PRIVATE key (PI RULING 4: outside participant boundary)
    trust_decision_priv_key: Ed25519PrivateKey,
    trust_decision_pub_key: Ed25519PublicKey,
) -> Tuple[Dict[str, Any], List[Dict[str, str]]]:
    """Pure non-mutating trust-decision function.

    Returns (TrustDecision, gate_results). The function does NOT mutate:
      - nonce_registry state (only reads via lookup)
      - envelope contents
      - any input artifact

    It DOES construct and sign a TrustDecision using the trust-decision
    authority's private key (K_TRUST_DECISION).
    """
    contents = envelope.get("contents", {})
    gate_results: List[Dict[str, str]] = []

    # G1: runtime binding (Live Provenance)
    if session_ctx.get("public_key_sha256") != sa.get("public_key_sha256"):
        return _finalize(_deny(GX_RUNTIME_BINDING, "session != sa"), gate_results,
                         envelope, trust_decision_priv_key, trust_decision_pub_key,
                         now_utc)
    if sa.get("public_key_sha256") != sca.get("public_key_sha256"):
        return _finalize(_deny(GX_RUNTIME_BINDING, "sa != sca"), gate_results,
                         envelope, trust_decision_priv_key, trust_decision_pub_key,
                         now_utc)
    if sa.get("public_key_sha256") != identity_att.get("public_key_sha256"):
        return _finalize(_deny(GX_RUNTIME_BINDING, "identity != sa"), gate_results,
                         envelope, trust_decision_priv_key, trust_decision_pub_key,
                         now_utc)
    if sa.get("freshness_challenge") != operator_freshness_challenge:
        return _finalize(_deny(GX_FRESHNESS_MISMATCH, "sa challenge"), gate_results,
                         envelope, trust_decision_priv_key, trust_decision_pub_key,
                         now_utc)
    if sa.get("event_source") != "HERMES_MODEL_RESPONSE":
        return _finalize(_deny(GX_EVENT_SOURCE_NOT_LIFECYCLE, "sa event_source"), gate_results,
                         envelope, trust_decision_priv_key, trust_decision_pub_key,
                         now_utc)
    if sca.get("event_source") != "HERMES_MODEL_RESPONSE":
        return _finalize(_deny(GX_EVENT_SOURCE_NOT_LIFECYCLE, "sca event_source"), gate_results,
                         envelope, trust_decision_priv_key, trust_decision_pub_key,
                         now_utc)
    if sca.get("session_acceptance_fingerprint") != sa.get("session_acceptance_fingerprint"):
        return _finalize(_deny(GX_ACCEPTANCE_FINGERPRINT_CHAIN, "sca.sa_fingerprint != sa.sa_fingerprint"), gate_results,
                         envelope, trust_decision_priv_key, trust_decision_pub_key,
                         now_utc)
    gate_results.append(_gate("G1_RUNTIME_BINDING", "PASS"))

    # G2: COA acceptance binding (verify receipt signature)
    if not verify(pub_key_tge, receipt, receipt.get("receipt_signature_b64", "")):
        return _finalize(_deny(GX_COA_SIGNATURE_INVALID, "K_TGE sig failed"), gate_results,
                         envelope, trust_decision_priv_key, trust_decision_pub_key, now_utc)
    if receipt.get("session_id") != session_ctx.get("session_id"):
        return _finalize(_deny(GX_COA_SESSION_MISMATCH, "receipt.session_id != session.session_id"), gate_results,
                         envelope, trust_decision_priv_key, trust_decision_pub_key, now_utc)
    if receipt.get("public_key_sha256") != session_ctx.get("public_key_sha256"):
        return _finalize(_deny(GX_COA_PUBLIC_KEY_MISMATCH, "receipt.pubkey != session.pubkey"), gate_results,
                         envelope, trust_decision_priv_key, trust_decision_pub_key, now_utc)
    if receipt.get("freshness_challenge") != operator_freshness_challenge:
        return _finalize(_deny(GX_COA_FRESHNESS_MISMATCH, "receipt challenge"), gate_results,
                         envelope, trust_decision_priv_key, trust_decision_pub_key, now_utc)
    if now_utc > float(receipt.get("expires_at_utc", 0)):
        return _finalize(_deny(GX_COA_EXPIRED, "receipt expired"), gate_results,
                         envelope, trust_decision_priv_key, trust_decision_pub_key, now_utc)
    if receipt.get("session_acceptance_fingerprint") != sa.get("session_acceptance_fingerprint"):
        return _finalize(_deny(GX_COA_NOT_BOUND_TO_LIVE_PROVENANCE, "receipt.sa_fingerprint != sa.sa_fingerprint"), gate_results,
                         envelope, trust_decision_priv_key, trust_decision_pub_key, now_utc)
    gate_results.append(_gate("G2_COA_BINDING", "PASS"))

    # G3: VA policy (verify sig + triple match + compatibility)
    if not verify_va_policy(va_policy, pub_key_va):
        return _finalize(_deny(GX_VA_POLICY_SIGNATURE_INVALID, "K_VA sig failed"), gate_results,
                         envelope, trust_decision_priv_key, trust_decision_pub_key, now_utc)
    if va_policy.get("policy_id") != capability.get("va_policy_id"):
        return _finalize(_deny(GX_VA_POLICY_TRIPLE_MISMATCH, "policy_id"), gate_results,
                         envelope, trust_decision_priv_key, trust_decision_pub_key, now_utc)
    if va_policy.get("policy_version") != capability.get("va_policy_version"):
        return _finalize(_deny(GX_VA_POLICY_TRIPLE_MISMATCH, "policy_version"), gate_results,
                         envelope, trust_decision_priv_key, trust_decision_pub_key, now_utc)
    if va_policy.get("policy_digest") != capability.get("va_policy_digest"):
        return _finalize(_deny(GX_VA_POLICY_TRIPLE_MISMATCH, "policy_digest"), gate_results,
                         envelope, trust_decision_priv_key, trust_decision_pub_key, now_utc)
    if not va_compatible(va_policy, contents.get("requested_action", {})):
        return _finalize(_deny(GX_VA_POLICY_INCOMPATIBLE, "rule violation"), gate_results,
                         envelope, trust_decision_priv_key, trust_decision_pub_key, now_utc)
    gate_results.append(_gate("G3_VA_COMPATIBILITY", "PASS"))

    # G4: behavioral evidence
    if not verify(pub_key_behavioral, behavioral_receipt,
                  behavioral_receipt.get("authority_signature_b64", "")):
        return _finalize(_deny(GX_BEHAVIORAL_SIGNATURE_INVALID, "K_BEHAVIORAL sig failed"), gate_results,
                         envelope, trust_decision_priv_key, trust_decision_pub_key, now_utc)
    if behavioral_receipt.get("evaluation_result_status") != "PASS_BEHAVIORAL":
        return _finalize(_deny(GX_BEHAVIORAL_BATTERY_FAILED,
                               f"status={behavioral_receipt.get('evaluation_result_status')}"),
                         gate_results,
                         envelope, trust_decision_priv_key, trust_decision_pub_key, now_utc)
    if behavioral_receipt.get("agent_identity_fingerprint") != identity_att.get("public_key_sha256"):
        return _finalize(_deny(GX_BEHAVIORAL_AGENT_MISMATCH, "behavioral.agent != identity"), gate_results,
                         envelope, trust_decision_priv_key, trust_decision_pub_key, now_utc)
    if now_utc > float(behavioral_receipt.get("expires_at_utc", 0)):
        return _finalize(_deny(GX_BEHAVIORAL_EXPIRED, "behavioral expired"), gate_results,
                         envelope, trust_decision_priv_key, trust_decision_pub_key, now_utc)
    gate_results.append(_gate("G4_BEHAVIORAL_EVIDENCE", "PASS"))

    # G5: capability
    if not verify(pub_key_authority, capability, capability.get("authority_signature_b64", "")):
        return _finalize(_deny(GX_CAPABILITY_SIGNATURE_INVALID, "K_AUTHORITY sig failed"), gate_results,
                         envelope, trust_decision_priv_key, trust_decision_pub_key, now_utc)
    if capability.get("public_key_sha256") != session_ctx.get("public_key_sha256"):
        return _finalize(_deny(GX_CAPABILITY_SESSION_MISMATCH, "capability.pubkey != session.pubkey"), gate_results,
                         envelope, trust_decision_priv_key, trust_decision_pub_key, now_utc)
    if capability.get("bound_receipt_fingerprint") != receipt.get("receipt_fingerprint"):
        return _finalize(_deny(GX_CAPABILITY_NOT_BOUND_TO_RECEIPT, "capability.receipt_fp != receipt.fp"), gate_results,
                         envelope, trust_decision_priv_key, trust_decision_pub_key, now_utc)
    req_action = contents.get("requested_action", {})
    if req_action.get("operation") not in capability.get("operation_scope", []):
        return _finalize(_deny(GX_OPERATION_OUT_OF_SCOPE,
                               f"op={req_action.get('operation')}"), gate_results,
                         envelope, trust_decision_priv_key, trust_decision_pub_key, now_utc)
    if req_action.get("target") not in capability.get("target_scope", []):
        return _finalize(_deny(GX_TARGET_OUT_OF_SCOPE,
                               f"target={req_action.get('target')}"), gate_results,
                         envelope, trust_decision_priv_key, trust_decision_pub_key, now_utc)
    excluded = capability.get("constraints", {}).get("excluded_targets", [])
    if req_action.get("target") in excluded:
        return _finalize(_deny(GX_TARGET_EXCLUDED,
                               f"target={req_action.get('target')}"), gate_results,
                         envelope, trust_decision_priv_key, trust_decision_pub_key, now_utc)
    if not (float(capability.get("valid_from_utc", 0)) <= now_utc <= float(capability.get("valid_until_utc", 0))):
        return _finalize(_deny(GX_CAPABILITY_EXPIRED_OR_NOT_YET_VALID,
                               f"now={now_utc}, valid=[{capability.get('valid_from_utc')}, {capability.get('valid_until_utc')}]"),
                         gate_results,
                         envelope, trust_decision_priv_key, trust_decision_pub_key, now_utc)
    gate_results.append(_gate("G5_CAPABILITY_SCOPE", "PASS"))

    # G6: live-provenance action chain + signature
    if sca.get("public_key_sha256") != session_ctx.get("public_key_sha256"):
        return _finalize(_deny(GX_ACTION_RUNTIME_MISMATCH, "sca.pubkey != session.pubkey"), gate_results,
                         envelope, trust_decision_priv_key, trust_decision_pub_key, now_utc)
    if sca.get("freshness_challenge") != operator_freshness_challenge:
        return _finalize(_deny(GX_ACTION_FRESHNESS_MISMATCH, "sca challenge"), gate_results,
                         envelope, trust_decision_priv_key, trust_decision_pub_key, now_utc)
    if sca.get("session_acceptance_fingerprint") != sa.get("session_acceptance_fingerprint"):
        return _finalize(_deny(GX_ACTION_ACCEPTANCE_CHAIN_BROKEN, "sca.sa_fingerprint != sa.sa_fingerprint"), gate_results,
                         envelope, trust_decision_priv_key, trust_decision_pub_key, now_utc)
    # Live-Provenance session signature verification (uses public_key_b64 from session_ctx)
    try:
        from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
        from crypto_utils import pubkey_from_b64
        session_pub = pubkey_from_b64(session_ctx.get("public_key_b64", ""))
        if not verify(session_pub, sca, sca.get("session_signature_b64", "")):
            return _finalize(_deny(GX_ACTION_SIGNATURE_INVALID, "session sig failed"), gate_results,
                             envelope, trust_decision_priv_key, trust_decision_pub_key, now_utc)
    except Exception as e:
        return _finalize(_deny(GX_ACTION_SIGNATURE_INVALID, f"session sig exception: {e}"), gate_results,
                         envelope, trust_decision_priv_key, trust_decision_pub_key, now_utc)
    gate_results.append(_gate("G6_LIVE_PROVENANCE_ACTION_CHAIN", "PASS"))

    # G7: envelope-binding hash
    recomputed_binding = fingerprint_obj(envelope.get("contents", {}))
    if envelope.get("envelope_binding_hash") != recomputed_binding:
        return _finalize(_deny(GX_ENVELOPE_BINDING_HASH_MISMATCH,
                               f"declared={envelope.get('envelope_binding_hash')}, recomputed={recomputed_binding}"),
                         gate_results,
                         envelope, trust_decision_priv_key, trust_decision_pub_key, now_utc)
    gate_results.append(_gate("G7_ENVELOPE_BINDING", "PASS"))

    # G8: nonce state
    nonce_state = nonce_registry.lookup(envelope.get("envelope_nonce", ""))
    if nonce_state == NonceState.UNKNOWN:
        return _finalize(_deny(GX_NONCE_UNKNOWN, f"nonce was never registered"), gate_results,
                         envelope, trust_decision_priv_key, trust_decision_pub_key, now_utc)
    if nonce_state == NonceState.AUTHORIZED:
        return _finalize(_deny(GX_NONCE_PREVIOUSLY_AUTHORIZED, "nonce=AUTHORIZED"), gate_results,
                         envelope, trust_decision_priv_key, trust_decision_pub_key, now_utc)
    if nonce_state == NonceState.CONSUMED:
        return _finalize(_deny(GX_NONCE_PREVIOUSLY_CONSUMED, "nonce=CONSUMED"), gate_results,
                         envelope, trust_decision_priv_key, trust_decision_pub_key, now_utc)
    if nonce_state != NonceState.UNSEEN:
        return _finalize(_deny(GX_NONCE_NOT_UNSEEN, f"state={nonce_state}"), gate_results,
                         envelope, trust_decision_priv_key, trust_decision_pub_key, now_utc)
    gate_results.append(_gate("G8_NONCE_STATE", "PASS"))

    # All gates passed
    return _finalize(
        {"verdict": "TRUST_GRANTED", "reason_code": GX_OK, "detail": ""},
        gate_results,
        envelope, trust_decision_priv_key, trust_decision_pub_key,
        now_utc,
    )


def _finalize(
    verdict_obj: Dict[str, Any],
    gate_results: List[Dict[str, str]],
    envelope: Dict[str, Any],
    trust_decision_priv_key: Ed25519PrivateKey,
    trust_decision_pub_key: Ed25519PublicKey,
    now_utc: float,
) -> Tuple[Dict[str, Any], List[Dict[str, str]]]:
    """Construct and sign the TrustDecision. Does NOT mutate nonce state."""
    decision_no_sig = {
        "schema_id": SCHEMA_ID_TRUST_DECISION,
        "decision_id": "<pending>",
        "operation_mode": "TRUST_DECIDE",
        "envelope_fingerprint": envelope.get("envelope_binding_hash", ""),
        "envelope_nonce": envelope.get("envelope_nonce", ""),
        "verdict": verdict_obj["verdict"],
        "reason_code": verdict_obj["reason_code"],
        "gate_results": gate_results,
        "decided_at_utc": now_utc,
        "trust_decision_authority_fingerprint": fingerprint_obj(
            {"public_key_b64": pubkey_to_b64(trust_decision_pub_key)}
        ),
        "decision_signature_b64": "<pending>",
    }
    decision_no_sig["decision_id"] = fingerprint_obj(
        {k: v for k, v in decision_no_sig.items() if k != "decision_signature_b64"}
    )
    decision_no_sig["decision_signature_b64"] = sign(trust_decision_priv_key, decision_no_sig)
    return decision_no_sig, gate_results


def verify_trust_decision(decision: Dict[str, Any], trust_decision_pub_key: Ed25519PublicKey) -> bool:
    return verify(trust_decision_pub_key, decision, decision.get("decision_signature_b64", ""))

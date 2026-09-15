"""ATE v0.3.1 diagnostic runner — three cases.

Per PI directive 2026-09-15:
  - Case A: valid chain, permitted action -> TRUST_GRANTED, action executes
  - Case B: valid evidence, action outside authorization scope -> TRUST_DENIED (GX_OPERATION_OUT_OF_SCOPE)
  - Case C: valid authorization, broken provenance/COA binding -> TRUST_DENIED

Live Provenance artifacts are generated locally (no model call) following
the frozen Live Provenance v0.2.1 artifact schema. Per the directive, Cases
B and C reuse Case A artifacts with deterministic tampering (no model
call required).
"""
import json
import os
import sys
import time
from typing import Any, Dict

# Make sibling modules importable
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

from crypto_utils import (
    canonicalize_json,
    fingerprint_bytes,
    fingerprint_obj,
    gen_keypair,
    privkey_from_b64,
    privkey_to_b64,
    pubkey_from_b64,
    pubkey_to_b64,
    sign,
    verify,
)
from nonce_registry import NonceRegistry, NonceState
from behavioral_evidence_receipt import (
    SCHEMA_ID as BER_SCHEMA,
    make_behavioral_evidence_receipt,
    stage_c_v0_1_evidence_digest,
    verify_behavioral_evidence_receipt,
)
from value_architecture_policy import (
    SCHEMA_ID as VA_SCHEMA,
    DEFAULT_POLICY_ID,
    DEFAULT_POLICY_VERSION,
    make_value_architecture_policy,
    verify_va_policy,
)
from trust_decision import (
    SCHEMA_ID_TRUST_DECISION,
    GX_OK,
    GX_OPERATION_OUT_OF_SCOPE,
    GX_NONCE_PREVIOUSLY_CONSUMED,
    GX_NONCE_UNKNOWN,
    GX_COA_NOT_BOUND_TO_LIVE_PROVENANCE,
    trust_decide,
    verify_trust_decision,
)
from executor import execute_governed_action, GovernedActionError


# ----------------------------------------------------------------------
# Fixture builders
# ----------------------------------------------------------------------


def build_fixtures() -> Dict[str, Any]:
    """Generate stable fixture keys for the diagnostic run."""
    keys = {}
    for name in ["IDENTITY", "TGE", "VA", "BEHAVIORAL", "AUTHORITY", "TRUST_DECISION"]:
        sk, pk = gen_keypair()
        keys[name] = {
            "priv": sk,
            "pub": pk,
            "pub_b64": pubkey_to_b64(pk),
        }
    return keys


def build_live_provenance_session(
    *, keys: Dict[str, Any], session_id: str, challenge: str, now_utc: float
) -> Dict[str, Any]:
    """Build the Live Provenance two-turn session artifacts."""
    id_pub = keys["IDENTITY"]["pub"]
    id_pub_b64 = keys["IDENTITY"]["pub_b64"]
    pub_sha = fingerprint_obj({"public_key_b64": id_pub_b64})

    # IdentityAttestation (ATE v0.2.1-shaped)
    identity_att = {
        "schema_id": "TGE-ATE-V2-IDENTITY/0.1",
        "agent_id": "lp-poc-agent-001",
        "public_key_b64": id_pub_b64,
        "public_key_sha256": pub_sha,
        "issued_at_utc": now_utc,
        "attestation_signature_b64": "<pending>",
    }
    identity_att["attestation_signature_b64"] = sign(keys["IDENTITY"]["priv"], identity_att)

    # SessionContext
    session_ctx = {
        "schema_id": "TGE-ATE-V2-SESSION/0.1",
        "session_id": session_id,
        "public_key_b64": id_pub_b64,
        "public_key_sha256": pub_sha,
        "started_at_utc": now_utc,
        "operator_freshness_challenge": challenge,
    }

    # SessionAcceptance (Live Provenance; event_source=HERMES_MODEL_RESPONSE)
    sa_response_hash = fingerprint_bytes(b"acceptance:OK")
    sa = {
        "schema_id": "LP-V0.2.1-SESSION-ACCEPTANCE/0.1",
        "session_id": session_id,
        "public_key_b64": id_pub_b64,
        "public_key_sha256": pub_sha,
        "freshness_challenge": challenge,
        "session_acceptance_fingerprint": "<pending>",
        "response_hash": sa_response_hash,
        "event_source": "HERMES_MODEL_RESPONSE",
        "monotonic_seq": 1,
        "turn_id": 1,
        "issued_at_utc": now_utc,
        "session_signature_b64": "<pending>",
    }
    sa["session_acceptance_fingerprint"] = fingerprint_obj(
        {k: v for k, v in sa.items() if k != "session_signature_b64"}
    )
    sa["session_signature_b64"] = sign(keys["IDENTITY"]["priv"], sa)

    # SignedCandidateAction (Live Provenance)
    sca_response_hash = fingerprint_bytes(b"action:OK")
    sca = {
        "schema_id": "LP-V0.2.1-SIGNED-CANDIDATE-ACTION/0.1",
        "session_id": session_id,
        "public_key_b64": id_pub_b64,
        "public_key_sha256": pub_sha,
        "freshness_challenge": challenge,
        "session_acceptance_fingerprint": sa["session_acceptance_fingerprint"],
        "action_preimage_hash": fingerprint_bytes(b'{"operation":"WRITE_SCOPED","target":"filesystem:/home/agent/proj/file.txt"}'),
        "response_hash": sca_response_hash,
        "event_source": "HERMES_MODEL_RESPONSE",
        "monotonic_seq": 2,
        "turn_id": 2,
        "issued_at_utc": now_utc,
        "session_signature_b64": "<pending>",
    }
    sca["session_signature_b64"] = sign(keys["IDENTITY"]["priv"], sca)

    return {
        "identity_attestation": identity_att,
        "session_context": session_ctx,
        "session_acceptance": sa,
        "signed_candidate_action": sca,
    }


def build_coa_receipt(
    *, keys: Dict[str, Any], session_id: str, challenge: str,
    sa_fingerprint: str, now_utc: float, expires_at_utc: float,
) -> Dict[str, Any]:
    # Stage 1: build payload WITHOUT receipt_fingerprint and signatures
    payload_no_fp = {
        "schema_id": "TGE-V2.1-ACCEPTANCE-RECEIPT/0.1",
        "session_id": session_id,
        "public_key_sha256": fingerprint_obj(
            {"public_key_b64": keys["IDENTITY"]["pub_b64"]}
        ),
        "freshness_challenge": challenge,
        "session_acceptance_fingerprint": sa_fingerprint,
        "issued_at_utc": now_utc,
        "expires_at_utc": expires_at_utc,
    }
    # Stage 2: compute receipt_id and receipt_fingerprint from this payload
    receipt_id = fingerprint_obj(payload_no_fp)
    receipt_fingerprint = fingerprint_obj({**payload_no_fp, "receipt_id": receipt_id})
    # Stage 3: assemble receipt including fingerprint and receipt_id, then sign
    receipt = {
        **payload_no_fp,
        "receipt_id": receipt_id,
        "receipt_fingerprint": receipt_fingerprint,
        "receipt_signature_b64": "<pending>",
    }
    receipt["receipt_signature_b64"] = sign(keys["TGE"]["priv"], receipt)
    return receipt


def build_capability_token(
    *, keys: Dict[str, Any], session_id: str, receipt_fingerprint: str,
    va_policy_id: str, va_policy_version: str, va_policy_digest: str,
    envelope_nonce: str, now_utc: float, valid_for_seconds: int = 3600,
    operation_scope=None, target_scope=None, excluded_targets=None,
) -> Dict[str, Any]:
    if operation_scope is None:
        operation_scope = ["READ", "WRITE_SCOPED"]
    if target_scope is None:
        target_scope = ["filesystem:/home/agent/proj/file.txt"]
    if excluded_targets is None:
        excluded_targets = ["filesystem:/home/agent/secrets/*"]
    payload_no_cid = {
        "schema_id": "ATE-V3.1-CAPABILITY/0.1",
        "session_id": session_id,
        "public_key_sha256": fingerprint_obj(
            {"public_key_b64": keys["IDENTITY"]["pub_b64"]}
        ),
        "bound_receipt_fingerprint": receipt_fingerprint,
        "operation_scope": operation_scope,
        "target_scope": target_scope,
        "constraints": {
            "max_per_call": 1,
            "max_total": 3,
            "excluded_targets": excluded_targets,
        },
        "valid_from_utc": now_utc,
        "valid_until_utc": now_utc + valid_for_seconds,
        "va_policy_id": va_policy_id,
        "va_policy_version": va_policy_version,
        "va_policy_digest": va_policy_digest,
        "envelope_nonce": envelope_nonce,
        "issued_at_utc": now_utc,
    }
    capability_id = fingerprint_obj(payload_no_cid)
    cap = {
        **payload_no_cid,
        "capability_id": capability_id,
        "authority_signature_b64": "<pending>",
    }
    cap["authority_signature_b64"] = sign(keys["AUTHORITY"]["priv"], cap)
    return cap


def build_envelope(
    *, identity_att, session_ctx, sa, sca, receipt, va_policy,
    behavioral_receipt, capability, operator_freshness_challenge,
    requested_action, nonce,
) -> Dict[str, Any]:
    contents = {
        "identity_attestation": identity_att,
        "session_context": session_ctx,
        "live_provenance_acceptance": sa,
        "live_provenance_action": sca,
        "coa_acceptance_receipt": receipt,
        "va_policy": va_policy,
        "behavioral_evidence_receipt": behavioral_receipt,
        "capability_token": capability,
        "requested_action": requested_action,
        "operator_freshness_challenge": operator_freshness_challenge,
    }
    env = {
        "schema_id": "ATE-V3.1-ENVELOPE/0.1",
        "envelope_id": "<pending>",
        "envelope_nonce": nonce,
        "issued_at_utc": time.time(),
        "envelope_binding_hash": fingerprint_obj(contents),
        "contents": contents,
    }
    env["envelope_id"] = fingerprint_obj(
        {k: v for k, v in env.items() if k != "envelope_id"}
    )
    return env


# ----------------------------------------------------------------------
# Diagnostic cases
# ----------------------------------------------------------------------


def run_case_a(keys, nonce_registry, now_utc, lifetime):
    print("\n=== Case A: valid chain / permitted action ===")
    session_id = "ate-v031-caseA-session-001"
    challenge = "ate-v031-challenge-caseA-001"
    nonce = "ate-v031-nonce-caseA-001"

    lp = build_live_provenance_session(
        keys=keys, session_id=session_id, challenge=challenge, now_utc=now_utc
    )
    receipt = build_coa_receipt(
        keys=keys, session_id=session_id, challenge=challenge,
        sa_fingerprint=lp["session_acceptance"]["session_acceptance_fingerprint"],
        now_utc=now_utc, expires_at_utc=now_utc + lifetime,
    )
    va_policy = make_value_architecture_policy(
        issued_at_utc=now_utc,
        va_priv_key=keys["VA"]["priv"],
        va_pub_key=keys["VA"]["pub"],
    )
    behavioral = make_behavioral_evidence_receipt(
        issued_at_utc=now_utc,
        authority_priv_key=keys["BEHAVIORAL"]["priv"],
        authority_pub_key=keys["BEHAVIORAL"]["pub"],
    )
    behavioral["agent_identity_fingerprint"] = lp["identity_attestation"]["public_key_sha256"]
    # Re-sign behavioral with updated fingerprint
    behavioral["authority_signature_b64"] = sign(keys["BEHAVIORAL"]["priv"], behavioral)

    capability = build_capability_token(
        keys=keys, session_id=session_id,
        receipt_fingerprint=receipt["receipt_fingerprint"],
        va_policy_id=va_policy["policy_id"],
        va_policy_version=va_policy["policy_version"],
        va_policy_digest=va_policy["policy_digest"],
        envelope_nonce=nonce,
        now_utc=now_utc,
    )

    requested_action = {
        "operation": "WRITE_SCOPED",
        "target": "filesystem:/home/agent/proj/file.txt",
        "data_class": "NONE",
        "harm_potential": 1,
        "action_struct": '{"operation":"WRITE_SCOPED","target":"filesystem:/home/agent/proj/file.txt"}',
    }

    envelope = build_envelope(
        identity_att=lp["identity_attestation"],
        session_ctx=lp["session_context"],
        sa=lp["session_acceptance"],
        sca=lp["signed_candidate_action"],
        receipt=receipt,
        va_policy=va_policy,
        behavioral_receipt=behavioral,
        capability=capability,
        operator_freshness_challenge=challenge,
        requested_action=requested_action,
        nonce=nonce,
    )

    # Register nonce; capture pre-state
    nonce_registry.register(nonce)
    pre_state = nonce_registry.lookup(nonce).value

    decision, gates = trust_decide(
        envelope,
        identity_att=lp["identity_attestation"],
        session_ctx=lp["session_context"],
        sa=lp["session_acceptance"],
        sca=lp["signed_candidate_action"],
        receipt=receipt,
        va_policy=va_policy,
        behavioral_receipt=behavioral,
        capability=capability,
        operator_freshness_challenge=challenge,
        now_utc=now_utc,
        nonce_registry=nonce_registry,
        pub_key_identity=keys["IDENTITY"]["pub"],
        pub_key_tge=keys["TGE"]["pub"],
        pub_key_va=keys["VA"]["pub"],
        pub_key_behavioral=keys["BEHAVIORAL"]["pub"],
        pub_key_authority=keys["AUTHORITY"]["pub"],
        trust_decision_priv_key=keys["TRUST_DECISION"]["priv"],
        trust_decision_pub_key=keys["TRUST_DECISION"]["pub"],
    )

    # Verify decision signature
    decision_sig_ok = verify_trust_decision(decision, keys["TRUST_DECISION"]["pub"])
    print(f"  decision verdict: {decision['verdict']}")
    print(f"  decision reason: {decision['reason_code']}")
    print(f"  decision sig ok: {decision_sig_ok}")
    print(f"  gate results: {[g['result'] for g in gates]}")
    print(f"  nonce pre-state: {pre_state}")
    # Capture nonce state IMMEDIATELY after trust_decide, BEFORE execute.
    # This is the proof of trust_decide purity: the state is unchanged by
    # the trust-decision function call alone.
    post_decide_state = nonce_registry.lookup(nonce).value
    print(f"  nonce post-trust_decide state (proof of purity): {post_decide_state}")

    # Execute governed action
    execution = None
    try:
        execution = execute_governed_action(
            envelope, decision,
            trust_decision_pub_key=keys["TRUST_DECISION"]["pub"],
            nonce_registry=nonce_registry,
        )
        print(f"  governed action executed: {execution['executed']}")
        print(f"  post-execution nonce state: {execution['resulting_nonce_state']}")
    except GovernedActionError as e:
        print(f"  execution failed: {e}")

    # Deterministic replay: re-submit the same envelope + decision
    replay_decision, replay_gates = trust_decide(
        envelope,
        identity_att=lp["identity_attestation"],
        session_ctx=lp["session_context"],
        sa=lp["session_acceptance"],
        sca=lp["signed_candidate_action"],
        receipt=receipt,
        va_policy=va_policy,
        behavioral_receipt=behavioral,
        capability=capability,
        operator_freshness_challenge=challenge,
        now_utc=now_utc,
        nonce_registry=nonce_registry,
        pub_key_identity=keys["IDENTITY"]["pub"],
        pub_key_tge=keys["TGE"]["pub"],
        pub_key_va=keys["VA"]["pub"],
        pub_key_behavioral=keys["BEHAVIORAL"]["pub"],
        pub_key_authority=keys["AUTHORITY"]["pub"],
        trust_decision_priv_key=keys["TRUST_DECISION"]["priv"],
        trust_decision_pub_key=keys["TRUST_DECISION"]["pub"],
    )
    print(f"  replay verdict: {replay_decision['verdict']}")
    print(f"  replay reason: {replay_decision['reason_code']}")
    replay_denied = replay_decision["verdict"] == "TRUST_DENIED"

    return {
        "case": "A",
        "decision_verdict": decision["verdict"],
        "decision_reason_code": decision["reason_code"],
        "decision_signature_ok": decision_sig_ok,
        "gate_results": [g["result"] for g in gates],
        "nonce_pre_state": pre_state,
        "nonce_post_trust_decide_state": post_decide_state,
        "execution": execution,
        "replay_verdict": replay_decision["verdict"],
        "replay_reason_code": replay_decision["reason_code"],
        "replay_denied": replay_denied,
        "envelope": envelope,
        "decision": decision,
        "replay_decision": replay_decision,
    }


def run_case_b(keys, case_a_envelope, nonce_registry, now_utc):
    """Case B: reuse Case A artifacts but tamper the requested_action.operation."""
    print("\n=== Case B: action outside authorization scope ===")
    envelope_b = json.loads(canonicalize_json(case_a_envelope))
    envelope_b["contents"]["requested_action"]["operation"] = "DELETE_FILE"
    envelope_b["envelope_binding_hash"] = fingerprint_obj(envelope_b["contents"])
    envelope_b["envelope_id"] = fingerprint_obj(
        {k: v for k, v in envelope_b.items() if k != "envelope_id"}
    )

    lp = envelope_b["contents"]
    identity_att = lp["identity_attestation"]
    session_ctx = lp["session_context"]
    sa = lp["live_provenance_acceptance"]
    sca = lp["live_provenance_action"]
    receipt = lp["coa_acceptance_receipt"]
    va_policy = lp["va_policy"]
    behavioral = lp["behavioral_evidence_receipt"]
    capability = lp["capability_token"]
    challenge = envelope_b["contents"]["operator_freshness_challenge"]
    nonce = envelope_b["envelope_nonce"]

    decision, gates = trust_decide(
        envelope_b,
        identity_att=identity_att,
        session_ctx=session_ctx,
        sa=sa,
        sca=sca,
        receipt=receipt,
        va_policy=va_policy,
        behavioral_receipt=behavioral,
        capability=capability,
        operator_freshness_challenge=challenge,
        now_utc=now_utc,
        nonce_registry=nonce_registry,
        pub_key_identity=keys["IDENTITY"]["pub"],
        pub_key_tge=keys["TGE"]["pub"],
        pub_key_va=keys["VA"]["pub"],
        pub_key_behavioral=keys["BEHAVIORAL"]["pub"],
        pub_key_authority=keys["AUTHORITY"]["pub"],
        trust_decision_priv_key=keys["TRUST_DECISION"]["priv"],
        trust_decision_pub_key=keys["TRUST_DECISION"]["pub"],
    )
    print(f"  decision verdict: {decision['verdict']}")
    print(f"  decision reason: {decision['reason_code']}")
    print(f"  gate results: {[g['result'] for g in gates]}")
    nonce_state_post = nonce_registry.lookup(nonce).value
    print(f"  nonce state after case B (must be CONSUMED from prior Case A execution): {nonce_state_post}")

    return {
        "case": "B",
        "decision_verdict": decision["verdict"],
        "decision_reason_code": decision["reason_code"],
        "gate_results": [g["result"] for g in gates],
        "nonce_state_after": nonce_state_post,
    }


def run_case_c(keys, case_a_envelope, nonce_registry, now_utc):
    """Case C: tamper sa.session_id (not in K_TGE signed region; not checked by
    G1) so G2 (COA binding) fires with GX_COA_SESSION_MISMATCH.

    A fresh envelope_nonce is used so that G8 does NOT fire first; the binding
    gate must be exercised. The capability_token is NOT modified (its
    envelope_nonce remains the Case A nonce; that nonce is now CONSUMED, but
    G5 does not consult nonce state). The fresh envelope_nonce is registered
    in the registry so G8 sees NONCE_UNSEEN.

    This matches v0.3.1 design §12 Case C: 'apparently valid authorization but
    broken provenance or COA binding'. The binding gate (G2) detects the
    mismatch and refuses the trust decision.

    Per the directive ("If Cases B and C can be generated deterministically
    from Case A artifacts without additional model calls and that is
    consistent with the frozen design, prefer that approach"), we reuse Case A
    artifacts with deterministic tampering. We use a fresh nonce (registered
    as UNSEEN) so that G8 does not fire and the binding gate is exercised.
    """
    print("\n=== Case C: broken provenance/COA binding ===")
    envelope_c = json.loads(canonicalize_json(case_a_envelope))
    # Use a fresh nonce (not consumed by Case A) so G8 does NOT fire.
    # Note: do NOT modify envelope_c["contents"]["capability_token"] because
    # that field is in the capability's signed region and would invalidate the
    # K_AUTHORITY signature.
    new_nonce = "ate-v031-nonce-caseC-001"
    envelope_c["envelope_nonce"] = new_nonce
    # Tamper session_ctx.session_id (the canonical session identity that G2
    # compares against receipt.session_id). session_ctx is not in the K_TGE
    # receipt signed region, so the receipt signature remains valid. session_ctx
    # is also not in the K_IDENTITY signed region (Live Provenance signatures
    # sign sa and sca individually, not session_ctx). G1 does not check
    # session_id. G2 (COA binding) catches the mismatch via
    # receipt.session_id != session_ctx.session_id -> GX_COA_SESSION_MISMATCH.
    envelope_c["contents"]["session_context"]["session_id"] = (
        "tampered-session-id-9999"
    )
    envelope_c["envelope_binding_hash"] = fingerprint_obj(envelope_c["contents"])
    envelope_c["envelope_id"] = fingerprint_obj(
        {k: v for k, v in envelope_c.items() if k != "envelope_id"}
    )

    lp = envelope_c["contents"]
    identity_att = lp["identity_attestation"]
    session_ctx = lp["session_context"]
    sa = lp["live_provenance_acceptance"]
    sca = lp["live_provenance_action"]
    receipt = lp["coa_acceptance_receipt"]
    va_policy = lp["va_policy"]
    behavioral = lp["behavioral_evidence_receipt"]
    capability = lp["capability_token"]
    challenge = envelope_c["contents"]["operator_freshness_challenge"]
    nonce = envelope_c["envelope_nonce"]

    decision, gates = trust_decide(
        envelope_c,
        identity_att=identity_att,
        session_ctx=session_ctx,
        sa=sa,
        sca=sca,
        receipt=receipt,
        va_policy=va_policy,
        behavioral_receipt=behavioral,
        capability=capability,
        operator_freshness_challenge=challenge,
        now_utc=now_utc,
        nonce_registry=nonce_registry,
        pub_key_identity=keys["IDENTITY"]["pub"],
        pub_key_tge=keys["TGE"]["pub"],
        pub_key_va=keys["VA"]["pub"],
        pub_key_behavioral=keys["BEHAVIORAL"]["pub"],
        pub_key_authority=keys["AUTHORITY"]["pub"],
        trust_decision_priv_key=keys["TRUST_DECISION"]["priv"],
        trust_decision_pub_key=keys["TRUST_DECISION"]["pub"],
    )
    print(f"  decision verdict: {decision['verdict']}")
    print(f"  decision reason: {decision['reason_code']}")
    print(f"  gate results: {[g['result'] for g in gates]}")
    nonce_state_post = nonce_registry.lookup(nonce).value
    print(f"  nonce state after case C (must be CONSUMED from prior Case A execution): {nonce_state_post}")

    return {
        "case": "C",
        "decision_verdict": decision["verdict"],
        "decision_reason_code": decision["reason_code"],
        "gate_results": [g["result"] for g in gates],
        "nonce_state_after": nonce_state_post,
    }


def _ensure_case_c_nonce_registered(nonce_registry):
    nonce_registry.register("ate-v031-nonce-caseC-001")


def main():
    now_utc = time.time()
    lifetime = 3600
    keys = build_fixtures()
    nonce_registry = NonceRegistry()

    case_a = run_case_a(keys, nonce_registry, now_utc, lifetime)
    _ensure_case_c_nonce_registered(nonce_registry)
    case_b = run_case_b(keys, case_a["envelope"], nonce_registry, now_utc)
    case_c = run_case_c(keys, case_a["envelope"], nonce_registry, now_utc)

    # Summary
    print("\n=== Summary ===")
    print(f"  Case A: verdict={case_a['decision_verdict']} reason={case_a['decision_reason_code']} execution={case_a['execution']['executed'] if case_a['execution'] else 'NONE'} replay_denied={case_a['replay_denied']}")
    print(f"  Case B: verdict={case_b['decision_verdict']} reason={case_b['decision_reason_code']}")
    print(f"  Case C: verdict={case_c['decision_verdict']} reason={case_c['decision_reason_code']}")
    print(f"  Trust-decision purity (A pre==post-trust_decide nonce state): {case_a['nonce_pre_state'] == case_a['nonce_post_trust_decide_state']}")
    return case_a, case_b, case_c


if __name__ == "__main__":
    main()

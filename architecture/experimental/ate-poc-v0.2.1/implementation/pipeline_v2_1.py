"""TrustPipeline v0.2.1 — 9-stage binding pipeline + replay separation.

Stages (FROZEN per v0.2.1):
  1. BIND_IDENTITY              (verify IdentityAttestation signature)
  2. BIND_SESSION_CONTEXT      (verify SessionContext signature)
  3. BIND_RECEIPT              (verify AcceptanceReceipt signature)
  4. BIND_CAPABILITY           (verify CapabilityToken signature)
  5. BIND_CANDIDATE_ACTION     (verify SignedCandidateAction signature)
  6. BIND_GEL_INPUT_HASH       (verify action_preimage_hash matches action_struct)
  7. EVAL_GATE                 (run GEL with active=True on the action_struct)
  8. BIND_EXECUTED_ACTION      (verify SignedExecutedAction signature)
  9. BIND_DECISION             (sign DecisionRecord)

For AUTHORIZE_EXECUTION:
  - Between stages 7 and 8: nonce state check + claim
  - If nonce is not UNSEEN: deny without invoking GEL execution boundary

For VERIFY_ENVELOPE:
  - Stages 1-6 verify the envelope; stage 7 (GEL) is NOT invoked; no
    SignedExecutedAction is produced; no nonce state change.
"""
import hashlib, time, json

from crypto_utils_v2 import canonicalize_json, fingerprint_obj
from identity_v2 import verify_identity, identity_fingerprint
from session_context import verify_session_context
from receipt_v2 import verify_receipt
from capability_v2 import verify_capability, operation_in_scope
from signed_candidate_action import (
    verify_signed_candidate_action, signed_action_fingerprint,
)
from signed_executed_action import (
    make_signed_executed_action, verify_signed_executed_action,
    executed_action_fingerprint,
)
from decision_record import make_decision_record, verify_decision_record
from nonce_registry import STATE_UNSEEN, STATE_AUTHORIZED, STATE_CONSUMED

# Path-import the v0.2.2 GEL (reused byte-identically)
import sys, os
GEL_V022_DIR = os.path.normpath(
    os.path.join(os.path.dirname(os.path.abspath(__file__)),
                 "..", "..", "stage-c", "implementation_v022")
)
if GEL_V022_DIR not in sys.path:
    sys.path.insert(0, GEL_V022_DIR)
import gel_v022


CHARTER_SHA256 = "charter_sha256_ate_poc_v0_1"  # placeholder charter


def _envelope_binding_hash(envelope):
    """SHA-256 over canonicalize(envelope)."""
    return hashlib.sha256(canonicalize_json(envelope)).hexdigest()


def evaluate(*, operation_mode, envelope, current_time,
             runtime_pub, authority_pub, tge_pub, gel_pub,
             pipeline_pub, pipeline_priv, gel_priv,
             nonce_registry):
    """Run the v0.2.1 frozen trust pipeline.

    Returns a DecisionRecord dict.
    """
    assert operation_mode in ("VERIFY_ENVELOPE", "AUTHORIZE_EXECUTION")

    audit_trail = []
    decision_id_seed = (envelope.get("envelope_id", "")
                        + ":" + operation_mode
                        + ":" + str(current_time))
    decision_id = hashlib.sha256(decision_id_seed.encode("utf-8")).hexdigest()[:32]

    envelope_h = _envelope_binding_hash(envelope)

    # Extract components
    identity = envelope.get("identity")
    session_ctx = envelope.get("session_context")
    receipt = envelope.get("receipt")
    capability = envelope.get("capability")
    sca = envelope.get("signed_candidate_action")
    envelope_nonce = (sca or {}).get("envelope_nonce", "")

    identity_fp = identity_fingerprint(identity) if identity else ""
    receipt_fp = fingerprint_obj(receipt) if receipt else ""
    capability_fp = fingerprint_obj(capability) if capability else ""
    sca_fp = signed_action_fingerprint(sca) if sca else ""

    # Default values (will be overridden on success path)
    verdict = None
    reason_code = None
    execution_boundary_reached = False
    executed_action_fp = ""
    candidate_action_fp = sca_fp  # alias for clarity
    previous_decision_id = None  # not used in this PoC

    def _record(stage_id, status, details):
        audit_trail.append({
            "stage_id": stage_id,
            "status": status,
            "details": details,
            "evaluated_at_utc": current_time,
        })

    # ---- Stage 1: BIND_IDENTITY ----
    ok, reason = verify_identity(identity, runtime_pub)
    if not ok:
        _record("BIND_IDENTITY", "FAIL", {"reason": reason})
        verdict = "DENY_BINDING_MISMATCH"
        reason_code = "GX_BIND_IDENTITY_FAILED"
        replay_check = "N/A_FAILED_BEFORE_REPLAY_CHECK"
        nonce_state_observed = "N/A"
        # No nonce change
        dr = make_decision_record(
            decision_id=decision_id, operation_mode=operation_mode,
            envelope_binding_hash=envelope_h, envelope_nonce=envelope_nonce,
            identity_fingerprint=identity_fp, receipt_fingerprint=receipt_fp,
            capability_fingerprint=capability_fp, action_fingerprint=sca_fp,
            executed_action_fingerprint=executed_action_fp,
            audit_trail=audit_trail, verdict=verdict, reason_code=reason_code,
            replay_check_result=replay_check,
            nonce_state_observed=nonce_state_observed,
            execution_boundary_reached=execution_boundary_reached,
            candidate_action_fingerprint=candidate_action_fp,
            previous_decision_id=previous_decision_id,
            issued_at_utc=current_time, pipeline_priv_key=pipeline_priv,
        )
        return dr

    _record("BIND_IDENTITY", "PASS", {"identity_fingerprint": identity_fp})

    # ---- Stage 2: BIND_SESSION_CONTEXT ----
    ok, reason = verify_session_context(session_ctx, runtime_pub)
    if not ok:
        _record("BIND_SESSION_CONTEXT", "FAIL", {"reason": reason})
        verdict = "DENY_BINDING_MISMATCH"
        reason_code = "GX_BIND_SESSION_CONTEXT_FAILED"
    else:
        # Cross-check: session_id matches identity.session_id
        if session_ctx.get("session_id") != identity.get("session_id"):
            _record("BIND_SESSION_CONTEXT", "FAIL", {"reason": "session_id_mismatch_with_identity"})
            verdict = "DENY_BINDING_MISMATCH"
            reason_code = "GX_BIND_SESSION_CONTEXT_FAILED"
        # Cross-check: identity_fingerprint matches
        elif session_ctx.get("identity_fingerprint") != identity_fp:
            _record("BIND_SESSION_CONTEXT", "FAIL", {"reason": "identity_fingerprint_mismatch"})
            verdict = "DENY_BINDING_MISMATCH"
            reason_code = "GX_BIND_SESSION_CONTEXT_FAILED"
        # Cross-check: receipt_id_predicate matches receipt.receipt_id
        elif receipt and session_ctx.get("receipt_id_predicate") != receipt.get("receipt_id"):
            _record("BIND_SESSION_CONTEXT", "FAIL", {"reason": "receipt_id_predicate_mismatch"})
            verdict = "DENY_BINDING_MISMATCH"
            reason_code = "GX_BIND_SESSION_CONTEXT_FAILED"
        # Cross-check: capability_id_predicate matches capability.capability_id
        elif capability and session_ctx.get("capability_id_predicate") != capability.get("capability_id"):
            _record("BIND_SESSION_CONTEXT", "FAIL", {"reason": "capability_id_predicate_mismatch"})
            verdict = "DENY_BINDING_MISMATCH"
            reason_code = "GX_BIND_SESSION_CONTEXT_FAILED"
        else:
            _record("BIND_SESSION_CONTEXT", "PASS", {
                "session_id": session_ctx.get("session_id"),
            })

    if verdict:
        replay_check = "N/A_FAILED_BEFORE_REPLAY_CHECK"
        nonce_state_observed = "N/A"
        dr = make_decision_record(
            decision_id=decision_id, operation_mode=operation_mode,
            envelope_binding_hash=envelope_h, envelope_nonce=envelope_nonce,
            identity_fingerprint=identity_fp, receipt_fingerprint=receipt_fp,
            capability_fingerprint=capability_fp, action_fingerprint=sca_fp,
            executed_action_fingerprint=executed_action_fp,
            audit_trail=audit_trail, verdict=verdict, reason_code=reason_code,
            replay_check_result=replay_check,
            nonce_state_observed=nonce_state_observed,
            execution_boundary_reached=execution_boundary_reached,
            candidate_action_fingerprint=candidate_action_fp,
            previous_decision_id=previous_decision_id,
            issued_at_utc=current_time, pipeline_priv_key=pipeline_priv,
        )
        return dr

    # ---- Stage 3: BIND_RECEIPT ----
    ok, reason = verify_receipt(receipt, tge_pub)
    if not ok:
        _record("BIND_RECEIPT", "FAIL", {"reason": reason})
        verdict = "DENY_BINDING_MISMATCH"
        reason_code = "GX_BIND_RECEIPT_FAILED"
    else:
        # Cross-check: receipt.session_id matches identity.session_id
        if receipt.get("session_id") != identity.get("session_id"):
            _record("BIND_RECEIPT", "FAIL", {"reason": "session_id_mismatch_with_identity"})
            verdict = "DENY_BINDING_MISMATCH"
            reason_code = "GX_BIND_RECEIPT_FAILED"
        # Cross-check: receipt.identity_fingerprint matches
        elif receipt.get("identity_fingerprint") != identity_fp:
            _record("BIND_RECEIPT", "FAIL", {"reason": "identity_fingerprint_mismatch"})
            verdict = "DENY_BINDING_MISMATCH"
            reason_code = "GX_BIND_RECEIPT_FAILED"
        # Cross-check: receipt.charter_sha256 matches
        elif receipt.get("charter_sha256") != CHARTER_SHA256:
            _record("BIND_RECEIPT", "FAIL", {"reason": "charter_sha256_mismatch"})
            verdict = "DENY_BINDING_MISMATCH"
            reason_code = "GX_BIND_RECEIPT_FAILED"
        # Freshness window: 1 hour
        elif (current_time - receipt.get("issued_at_utc", 0)) > 3600:
            _record("BIND_RECEIPT", "FAIL", {"reason": "receipt_expired"})
            verdict = "DENY_BINDING_MISMATCH"
            reason_code = "GX_BIND_RECEIPT_FAILED"
        else:
            _record("BIND_RECEIPT", "PASS", {
                "receipt_id": receipt.get("receipt_id"),
                "charter_sha256": receipt.get("charter_sha256"),
            })

    if verdict:
        replay_check = "N/A_FAILED_BEFORE_REPLAY_CHECK"
        nonce_state_observed = "N/A"
        dr = make_decision_record(
            decision_id=decision_id, operation_mode=operation_mode,
            envelope_binding_hash=envelope_h, envelope_nonce=envelope_nonce,
            identity_fingerprint=identity_fp, receipt_fingerprint=receipt_fp,
            capability_fingerprint=capability_fp, action_fingerprint=sca_fp,
            executed_action_fingerprint=executed_action_fp,
            audit_trail=audit_trail, verdict=verdict, reason_code=reason_code,
            replay_check_result=replay_check,
            nonce_state_observed=nonce_state_observed,
            execution_boundary_reached=execution_boundary_reached,
            candidate_action_fingerprint=candidate_action_fp,
            previous_decision_id=previous_decision_id,
            issued_at_utc=current_time, pipeline_priv_key=pipeline_priv,
        )
        return dr

    # ---- Stage 4: BIND_CAPABILITY ----
    ok, reason = verify_capability(capability, authority_pub)
    if not ok:
        _record("BIND_CAPABILITY", "FAIL", {"reason": reason})
        verdict = "DENY_BINDING_MISMATCH"
        reason_code = "GX_BIND_CAPABILITY_FAILED"
    else:
        # Cross-checks
        if capability.get("agent_id") != identity.get("agent_id"):
            _record("BIND_CAPABILITY", "FAIL", {"reason": "agent_id_mismatch"})
            verdict = "DENY_BINDING_MISMATCH"
            reason_code = "GX_BIND_CAPABILITY_FAILED"
        elif capability.get("session_id") != identity.get("session_id"):
            _record("BIND_CAPABILITY", "FAIL", {"reason": "session_id_mismatch"})
            verdict = "DENY_BINDING_MISMATCH"
            reason_code = "GX_BIND_CAPABILITY_FAILED"
        elif capability.get("identity_fingerprint") != identity_fp:
            _record("BIND_CAPABILITY", "FAIL", {"reason": "identity_fingerprint_mismatch"})
            verdict = "DENY_BINDING_MISMATCH"
            reason_code = "GX_BIND_CAPABILITY_FAILED"
        # Validity window
        elif current_time < capability.get("valid_from_utc", 0):
            _record("BIND_CAPABILITY", "FAIL", {"reason": "capability_not_yet_valid"})
            verdict = "DENY_BINDING_MISMATCH"
            reason_code = "GX_BIND_CAPABILITY_FAILED"
        elif current_time > capability.get("valid_until_utc", 0):
            _record("BIND_CAPABILITY", "FAIL", {"reason": "capability_expired"})
            verdict = "DENY_BINDING_MISMATCH"
            reason_code = "GX_BIND_CAPABILITY_FAILED"
        else:
            # Cross-check with sca: sca.capability_id == capability.capability_id
            if sca.get("capability_id") != capability.get("capability_id"):
                _record("BIND_CAPABILITY", "FAIL",
                        {"reason": "sca_capability_id_mismatch"})
                verdict = "DENY_BINDING_MISMATCH"
                reason_code = "GX_BIND_CAPABILITY_FAILED"
            else:
                _record("BIND_CAPABILITY", "PASS", {
                    "capability_id": capability.get("capability_id"),
                    "scope": capability.get("scope"),
                })

    if verdict:
        replay_check = "N/A_FAILED_BEFORE_REPLAY_CHECK"
        nonce_state_observed = "N/A"
        dr = make_decision_record(
            decision_id=decision_id, operation_mode=operation_mode,
            envelope_binding_hash=envelope_h, envelope_nonce=envelope_nonce,
            identity_fingerprint=identity_fp, receipt_fingerprint=receipt_fp,
            capability_fingerprint=capability_fp, action_fingerprint=sca_fp,
            executed_action_fingerprint=executed_action_fp,
            audit_trail=audit_trail, verdict=verdict, reason_code=reason_code,
            replay_check_result=replay_check,
            nonce_state_observed=nonce_state_observed,
            execution_boundary_reached=execution_boundary_reached,
            candidate_action_fingerprint=candidate_action_fp,
            previous_decision_id=previous_decision_id,
            issued_at_utc=current_time, pipeline_priv_key=pipeline_priv,
        )
        return dr

    # ---- Stage 5: BIND_CANDIDATE_ACTION ----
    ok, reason = verify_signed_candidate_action(sca, runtime_pub)
    if not ok:
        _record("BIND_CANDIDATE_ACTION", "FAIL", {"reason": reason})
        verdict = "DENY_BINDING_MISMATCH"
        reason_code = "GX_BIND_CANDIDATE_ACTION_FAILED"
    else:
        # Cross-checks: sca.session_id == identity.session_id
        if sca.get("session_id") != identity.get("session_id"):
            _record("BIND_CANDIDATE_ACTION", "FAIL", {"reason": "session_id_mismatch"})
            verdict = "DENY_BINDING_MISMATCH"
            reason_code = "GX_BIND_CANDIDATE_ACTION_FAILED"
        elif sca.get("identity_fingerprint") != identity_fp:
            _record("BIND_CANDIDATE_ACTION", "FAIL", {"reason": "identity_fingerprint_mismatch"})
            verdict = "DENY_BINDING_MISMATCH"
            reason_code = "GX_BIND_CANDIDATE_ACTION_FAILED"
        elif sca.get("receipt_id") != receipt.get("receipt_id"):
            _record("BIND_CANDIDATE_ACTION", "FAIL", {"reason": "receipt_id_mismatch"})
            verdict = "DENY_BINDING_MISMATCH"
            reason_code = "GX_BIND_CANDIDATE_ACTION_FAILED"
        elif sca.get("capability_id") != capability.get("capability_id"):
            _record("BIND_CANDIDATE_ACTION", "FAIL", {"reason": "capability_id_mismatch"})
            verdict = "DENY_BINDING_MISMATCH"
            reason_code = "GX_BIND_CANDIDATE_ACTION_FAILED"
        else:
            _record("BIND_CANDIDATE_ACTION", "PASS", {
                "session_id": sca.get("session_id"),
                "envelope_nonce": sca.get("envelope_nonce"),
                "capability_id": sca.get("capability_id"),
                "receipt_id": sca.get("receipt_id"),
                "identity_fingerprint": sca.get("identity_fingerprint"),
                "action_preimage_hash": sca.get("action_preimage_hash"),
            })

    if verdict:
        replay_check = "N/A_FAILED_BEFORE_REPLAY_CHECK"
        nonce_state_observed = "N/A"
        dr = make_decision_record(
            decision_id=decision_id, operation_mode=operation_mode,
            envelope_binding_hash=envelope_h, envelope_nonce=envelope_nonce,
            identity_fingerprint=identity_fp, receipt_fingerprint=receipt_fp,
            capability_fingerprint=capability_fp, action_fingerprint=sca_fp,
            executed_action_fingerprint=executed_action_fp,
            audit_trail=audit_trail, verdict=verdict, reason_code=reason_code,
            replay_check_result=replay_check,
            nonce_state_observed=nonce_state_observed,
            execution_boundary_reached=execution_boundary_reached,
            candidate_action_fingerprint=candidate_action_fp,
            previous_decision_id=previous_decision_id,
            issued_at_utc=current_time, pipeline_priv_key=pipeline_priv,
        )
        return dr

    # ---- Stage 6: BIND_GEL_INPUT_HASH ----
    # (already checked inside verify_signed_candidate_action; this stage
    # is a separate explicit log entry confirming the hash check)
    expected_preimage = fingerprint_obj(sca["action_struct"])
    if sca.get("action_preimage_hash") != expected_preimage:
        _record("BIND_GEL_INPUT_HASH", "FAIL",
                {"reason": "action_preimage_hash_mismatch"})
        verdict = "DENY_BINDING_MISMATCH"
        reason_code = "GX_BIND_GEL_INPUT_HASH_FAILED"
    else:
        _record("BIND_GEL_INPUT_HASH", "PASS", {
            "action_preimage_hash": expected_preimage,
        })

    if verdict:
        replay_check = "N/A_FAILED_BEFORE_REPLAY_CHECK"
        nonce_state_observed = "N/A"
        dr = make_decision_record(
            decision_id=decision_id, operation_mode=operation_mode,
            envelope_binding_hash=envelope_h, envelope_nonce=envelope_nonce,
            identity_fingerprint=identity_fp, receipt_fingerprint=receipt_fp,
            capability_fingerprint=capability_fp, action_fingerprint=sca_fp,
            executed_action_fingerprint=executed_action_fp,
            audit_trail=audit_trail, verdict=verdict, reason_code=reason_code,
            replay_check_result=replay_check,
            nonce_state_observed=nonce_state_observed,
            execution_boundary_reached=execution_boundary_reached,
            candidate_action_fingerprint=candidate_action_fp,
            previous_decision_id=previous_decision_id,
            issued_at_utc=current_time, pipeline_priv_key=pipeline_priv,
        )
        return dr

    # All binding stages 1-6 passed.

    if operation_mode == "VERIFY_ENVELOPE":
        # No GEL execution; no nonce change.
        _record("BIND_DECISION", "PASS", {"note": "verify_only"})
        verdict = "VERIFICATION_PASS"
        reason_code = "VERIFICATION_PASS"
        # Read nonce state (without claim)
        current_state, _ = nonce_registry.get_state(envelope_nonce)
        replay_check = "N/A_FOR_VERIFICATION"
        nonce_state_observed = current_state
        execution_boundary_reached = False
        dr = make_decision_record(
            decision_id=decision_id, operation_mode=operation_mode,
            envelope_binding_hash=envelope_h, envelope_nonce=envelope_nonce,
            identity_fingerprint=identity_fp, receipt_fingerprint=receipt_fp,
            capability_fingerprint=capability_fp, action_fingerprint=sca_fp,
            executed_action_fingerprint=executed_action_fp,
            audit_trail=audit_trail, verdict=verdict, reason_code=reason_code,
            replay_check_result=replay_check,
            nonce_state_observed=nonce_state_observed,
            execution_boundary_reached=execution_boundary_reached,
            candidate_action_fingerprint=candidate_action_fp,
            previous_decision_id=previous_decision_id,
            issued_at_utc=current_time, pipeline_priv_key=pipeline_priv,
        )
        return dr

    # operation_mode == "AUTHORIZE_EXECUTION"
    # ---- Nonce state check + claim (before GEL execution boundary) ----
    current_state, _ = nonce_registry.get_state(envelope_nonce)
    nonce_state_observed = current_state

    if current_state == STATE_AUTHORIZED:
        _record("REPLAY_CHECK", "FAIL",
                {"reason": "nonce_previously_authorized",
                 "nonce_state_observed": current_state})
        verdict = "DENY_REPLAY"
        reason_code = "GX_REPLAY_NONCE_PREVIOUSLY_AUTHORIZED"
        replay_check = "DENY_NONCE_PREVIOUSLY_AUTHORIZED"
        execution_boundary_reached = False
        dr = make_decision_record(
            decision_id=decision_id, operation_mode=operation_mode,
            envelope_binding_hash=envelope_h, envelope_nonce=envelope_nonce,
            identity_fingerprint=identity_fp, receipt_fingerprint=receipt_fp,
            capability_fingerprint=capability_fp, action_fingerprint=sca_fp,
            executed_action_fingerprint=executed_action_fp,
            audit_trail=audit_trail, verdict=verdict, reason_code=reason_code,
            replay_check_result=replay_check,
            nonce_state_observed=nonce_state_observed,
            execution_boundary_reached=execution_boundary_reached,
            candidate_action_fingerprint=candidate_action_fp,
            previous_decision_id=previous_decision_id,
            issued_at_utc=current_time, pipeline_priv_key=pipeline_priv,
        )
        return dr
    elif current_state == STATE_CONSUMED:
        _record("REPLAY_CHECK", "FAIL",
                {"reason": "nonce_previously_consumed",
                 "nonce_state_observed": current_state})
        verdict = "DENY_REPLAY"
        reason_code = "GX_REPLAY_NONCE_PREVIOUSLY_CONSUMED"
        replay_check = "DENY_NONCE_PREVIOUSLY_CONSUMED"
        execution_boundary_reached = False
        dr = make_decision_record(
            decision_id=decision_id, operation_mode=operation_mode,
            envelope_binding_hash=envelope_h, envelope_nonce=envelope_nonce,
            identity_fingerprint=identity_fp, receipt_fingerprint=receipt_fp,
            capability_fingerprint=capability_fp, action_fingerprint=sca_fp,
            executed_action_fingerprint=executed_action_fp,
            audit_trail=audit_trail, verdict=verdict, reason_code=reason_code,
            replay_check_result=replay_check,
            nonce_state_observed=nonce_state_observed,
            execution_boundary_reached=execution_boundary_reached,
            candidate_action_fingerprint=candidate_action_fp,
            previous_decision_id=previous_decision_id,
            issued_at_utc=current_time, pipeline_priv_key=pipeline_priv,
        )
        return dr

    # state == UNSEEN: claim atomically
    new_state, claim_details = nonce_registry.claim(
        envelope_nonce, decision_id=decision_id, at_utc=current_time,
    )
    if new_state == STATE_AUTHORIZED:
        _record("REPLAY_CHECK", "PASS",
                {"reason": "first_authorization",
                 "transition": claim_details.get("transition")})
        # nonce_state_observed = state at time of observation (UNSEEN for first execution)
        nonce_state_observed = STATE_UNSEEN
        replay_check = "PASS_FIRST_EXECUTION"
    else:
        # Race or unknown state
        _record("REPLAY_CHECK", "FAIL",
                {"reason": "nonce_claim_failed",
                 "new_state": new_state})
        verdict = "DENY_REPLAY"
        reason_code = "GX_REPLAY_NONCE_CLAIM_FAILED"
        replay_check = "DENY_NONCE_CLAIM_FAILED"
        execution_boundary_reached = False
        dr = make_decision_record(
            decision_id=decision_id, operation_mode=operation_mode,
            envelope_binding_hash=envelope_h, envelope_nonce=envelope_nonce,
            identity_fingerprint=identity_fp, receipt_fingerprint=receipt_fp,
            capability_fingerprint=capability_fp, action_fingerprint=sca_fp,
            executed_action_fingerprint=executed_action_fp,
            audit_trail=audit_trail, verdict=verdict, reason_code=reason_code,
            replay_check_result=replay_check,
            nonce_state_observed=nonce_state_observed,
            execution_boundary_reached=execution_boundary_reached,
            candidate_action_fingerprint=candidate_action_fp,
            previous_decision_id=previous_decision_id,
            issued_at_utc=current_time, pipeline_priv_key=pipeline_priv,
        )
        return dr

    # ---- Stage 7: EVAL_GATE (GEL with active=True) ----
    gel_result = gel_v022.evaluate_v022(sca["action_struct"], active=True)
    gel_verdict = gel_result["verdict"]
    gel_intervened = gel_result["intervened"]
    gel_rule_id = gel_result["rule_id"]
    gel_executed = gel_result["executed_action"]
    gel_evaluated_at = gel_result["evaluated_at_utc"]

    _record("EVAL_GATE", gel_verdict.upper(), {
        "rule_id": gel_rule_id,
        "intervened": gel_intervened,
    })

    # ---- Stage 8: BIND_EXECUTED_ACTION ----
    sea = make_signed_executed_action(
        original_signed_action_fingerprint=sca_fp,
        executed_action_struct=gel_executed,
        rule_id=gel_rule_id,
        evaluated_at_utc=gel_evaluated_at,
        gel_priv_key=gel_priv,
    )
    executed_action_fp = executed_action_fingerprint(sea)

    ok_sea, reason_sea = verify_signed_executed_action(sea, gel_pub)
    if not ok_sea:
        _record("BIND_EXECUTED_ACTION", "FAIL", {"reason": reason_sea})
        verdict = "DENY_BINDING_MISMATCH"
        reason_code = "GX_BIND_EXECUTED_ACTION_FAILED"
        execution_boundary_reached = True  # reached but failed
        # Still consume the nonce to prevent re-attempt
        nonce_registry.consume(envelope_nonce, decision_id=decision_id, at_utc=current_time)
        dr = make_decision_record(
            decision_id=decision_id, operation_mode=operation_mode,
            envelope_binding_hash=envelope_h, envelope_nonce=envelope_nonce,
            identity_fingerprint=identity_fp, receipt_fingerprint=receipt_fp,
            capability_fingerprint=capability_fp, action_fingerprint=sca_fp,
            executed_action_fingerprint=executed_action_fp,
            audit_trail=audit_trail, verdict=verdict, reason_code=reason_code,
            replay_check_result=replay_check,
            nonce_state_observed=nonce_state_observed,  # state at lookup time
            execution_boundary_reached=execution_boundary_reached,
            candidate_action_fingerprint=candidate_action_fp,
            previous_decision_id=previous_decision_id,
            issued_at_utc=current_time, pipeline_priv_key=pipeline_priv,
        )
        return dr

    _record("BIND_EXECUTED_ACTION", "PASS", {
        "original_action_hash": sea.get("original_action_hash"),
        "rule_id": sea.get("rule_id"),
    })

    # ---- Consume nonce ----
    nonce_registry.consume(envelope_nonce, decision_id=decision_id, at_utc=current_time)

    # ---- Final verdict ----
    if gel_verdict == "allow":
        verdict = "ALLOW"
        reason_code = "PASS"
    elif gel_verdict == "block":
        verdict = "BLOCK"
        reason_code = f"BLOCK_{gel_rule_id}"
    elif gel_verdict == "redirect":
        verdict = "REDIRECT"
        reason_code = f"REDIRECT_{gel_rule_id}"
    else:
        verdict = "DENY_BINDING_MISMATCH"
        reason_code = "GX_UNKNOWN_GEL_VERDICT"

    execution_boundary_reached = True

    # ---- Stage 9: BIND_DECISION (sign DecisionRecord) ----
    _record("BIND_DECISION", "PASS", {"verdict": verdict})

    dr = make_decision_record(
        decision_id=decision_id, operation_mode=operation_mode,
        envelope_binding_hash=envelope_h, envelope_nonce=envelope_nonce,
        identity_fingerprint=identity_fp, receipt_fingerprint=receipt_fp,
        capability_fingerprint=capability_fp, action_fingerprint=sca_fp,
        executed_action_fingerprint=executed_action_fp,
        audit_trail=audit_trail, verdict=verdict, reason_code=reason_code,
        replay_check_result=replay_check,
        # nonce_state_observed is the state at lookup time, BEFORE the claim
        # transition. For first execution, this is UNSEEN.
        nonce_state_observed=nonce_state_observed,
        execution_boundary_reached=execution_boundary_reached,
        candidate_action_fingerprint=candidate_action_fp,
        previous_decision_id=previous_decision_id,
        issued_at_utc=current_time, pipeline_priv_key=pipeline_priv,
    )

    return dr

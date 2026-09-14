"""TrustPipeline per ATE-POC-DESIGN-v0.1 §3.

STRICT GATE ORDER:
  GATE_IDENTITY -> GATE_RECEIPT -> GATE_SESSION -> GATE_CAPABILITY -> GATE_GEL

Once an upstream gate fails:
  - stop evaluation
  - do not invoke downstream gates
  - do not invoke GEL
  - record the failing gate and reason

FAIL CLOSED: any missing / malformed / unverifiable / expired /
mismatched / tampered trust input must produce a deterministic
DENY_BEFORE_GEL.

DISTINGUISH TRUST FAILURE FROM GOVERNANCE FAILURE:
  - trust failures (identity / receipt / session / capability / tamper)
    -> DENY_BEFORE_GEL
  - GEL rejection / transformation -> BLOCK / REDIRECT
  - all upstream passes + GEL allow -> ALLOW

GEL is reused from v0.2.2 byte-identically (no adapter needed).
"""
import hashlib
import os
import sys
import time

THIS = os.path.dirname(os.path.abspath(__file__))
GEL_V022_DIR = os.path.normpath(os.path.join(THIS, "..", "..", "..", "stage-c", "implementation_v022"))
sys.path.insert(0, GEL_V022_DIR)

# Reuse v0.2.2 GEL byte-identically. No adapter.
from gel_v022 import (
    evaluate_v022, is_charter_consistent_v022, FROZEN_RULES_V022,
    SCHEMA_INVALID_EXECUTED_ACTION as GEL_INVALID_TEMPLATE,
)
from identity import verify_identity, identity_hash
from capability import verify_capability, capability_hash
from receipt import verify_receipt, receipt_hash
from crypto_utils import canonicalize_json


CHARTER_SHA256 = "charter_sha256_ate_poc_v0_1"  # the bound charter identifier


def evaluate_envelope(
    envelope, *, current_time: int, authority_pub,
    gate_trace: list = None,
    trust_summary: dict = None,
) -> dict:
    """Run the frozen trust pipeline. Returns a TrustDecision.

    The function is pure given its inputs (current_time, authority_pub).
    """
    if gate_trace is None:
        gate_trace = []
    if trust_summary is None:
        trust_summary = {}

    def _record(gate_id, verdict, reason_code, reason_description, details):
        gate_trace.append({
            "gate_id": gate_id,
            "verdict": verdict,
            "reason_code": reason_code,
            "reason_description": reason_description,
            "details": details,
            "evaluated_at_utc": current_time,
        })
        return verdict

    # ---- Pre-extract envelope fields ----
    identity = envelope.get("identity") if isinstance(envelope, dict) else None
    receipt = envelope.get("acceptance_receipt") if isinstance(envelope, dict) else None
    capability = envelope.get("capability") if isinstance(envelope, dict) else None
    candidate_action = envelope.get("candidate_action") if isinstance(envelope, dict) else None

    # Compute identity / receipt / capability hashes for tamper tests
    identity_h = identity_hash(identity) if identity else None
    receipt_h = receipt_hash(receipt) if receipt else None
    capability_h = capability_hash(capability) if capability else None
    candidate_action_h = hashlib.sha256(canonicalize_json(candidate_action)).hexdigest() if candidate_action else None

    envelope_h = hashlib.sha256(canonicalize_json(envelope)).hexdigest() if envelope else None

    # ============================================================
    # GATE 1: IDENTITY
    # ============================================================
    identity_ok, identity_code, identity_desc = verify_identity(identity) if identity else (False, "GX_IDENTITY_MISSING", "identity_is_none")
    _record("GATE_IDENTITY",
            "PASS" if identity_ok else "FAIL",
            identity_code, identity_desc,
            {"identity_hash": identity_h})
    trust_summary["identity_passed"] = identity_ok
    if not identity_ok:
        return _finalize(envelope, envelope_h, identity_h, receipt_h, capability_h,
                         candidate_action_h, "DENY_BEFORE_GEL", None, gate_trace,
                         trust_summary, "GATE_IDENTITY", identity_code, identity_desc)

    identity_session_id = identity.get("session_id")
    identity_agent_id = identity.get("agent_id")

    # ============================================================
    # GATE 2: RECEIPT
    # ============================================================
    receipt_ok, receipt_code, receipt_desc, receipt_details = verify_receipt(
        receipt,
        expected_charter_sha256=CHARTER_SHA256,
        expected_session_id=identity_session_id,
        current_time=current_time,
    )
    _record("GATE_RECEIPT",
            "PASS" if receipt_ok else "FAIL",
            receipt_code, receipt_desc, receipt_details)
    trust_summary["receipt_passed"] = receipt_ok
    if not receipt_ok:
        return _finalize(envelope, envelope_h, identity_h, receipt_h, capability_h,
                         candidate_action_h, "DENY_BEFORE_GEL", None, gate_trace,
                         trust_summary, "GATE_RECEIPT", receipt_code, receipt_desc)

    # ============================================================
    # GATE 3: SESSION
    # ============================================================
    # Compare identity.session_id, capability.session_id, and candidate_action.session_id.
    # Receipt.session_id was already verified in Gate 2 against identity.session_id.
    capability_session_id = capability.get("session_id") if capability else None
    candidate_session_id = candidate_action.get("session_id") if isinstance(candidate_action, dict) else None

    session_matches = (
        capability_session_id == identity_session_id
        and candidate_session_id == identity_session_id
    )
    if not session_matches:
        _record("GATE_SESSION", "FAIL", "GX_SESSION_MISMATCH",
                "session_id mismatch across identity/capability/candidate_action",
                {
                    "identity_session_id": identity_session_id,
                    "capability_session_id": capability_session_id,
                    "candidate_session_id": candidate_session_id,
                })
        trust_summary["session_passed"] = False
        return _finalize(envelope, envelope_h, identity_h, receipt_h, capability_h,
                         candidate_action_h, "DENY_BEFORE_GEL", None, gate_trace,
                         trust_summary, "GATE_SESSION", "GX_SESSION_MISMATCH",
                         "session_id mismatch across identity/capability/candidate_action")
    else:
        _record("GATE_SESSION", "PASS", "PASS",
                "session_id consistent across all sources",
                {"session_id": identity_session_id})
        trust_summary["session_passed"] = True

    # ============================================================
    # GATE 4: CAPABILITY
    # ============================================================
    operation = candidate_action.get("operation") if isinstance(candidate_action, dict) else None
    target_kind = candidate_action.get("target_kind") if isinstance(candidate_action, dict) else None
    target_identifier = candidate_action.get("target_identifier") if isinstance(candidate_action, dict) else None

    capability_ok, capability_code, capability_desc, capability_details = verify_capability(
        capability if capability else {},
        agent_id=identity_agent_id,
        session_id=identity_session_id,
        current_time=current_time,
        operation=operation,
        target_kind=target_kind,
        target_identifier=target_identifier,
        authority_pub=authority_pub,
    )
    _record("GATE_CAPABILITY",
            "PASS" if capability_ok else "FAIL",
            capability_code, capability_desc, capability_details)
    trust_summary["capability_passed"] = capability_ok
    if not capability_ok:
        return _finalize(envelope, envelope_h, identity_h, receipt_h, capability_h,
                         candidate_action_h, "DENY_BEFORE_GEL", None, gate_trace,
                         trust_summary, "GATE_CAPABILITY", capability_code, capability_desc)

    # ============================================================
    # GATE 5: GEL
    # ============================================================
    # v0.2.2 GEL evaluates the candidate_action. If the action is
    # not a v0.2.2 schema-valid dict, GEL's evaluate_v022 may raise;
    # we treat that as a tamper case (recorded as GX_GEL_INVALID_INPUT).
    try:
        gel_verdict = evaluate_v022(candidate_action, FROZEN_RULES_V022, active=True)
    except Exception as e:
        _record("GATE_GEL", "FAIL", "GX_GEL_INVALID_INPUT",
                f"gel_evaluation_raised:{type(e).__name__}:{e}",
                {"exception": f"{type(e).__name__}:{e}"})
        trust_summary["gel_passed"] = None
        return _finalize(envelope, envelope_h, identity_h, receipt_h, capability_h,
                         candidate_action_h, "BLOCK", GEL_INVALID_TEMPLATE, gate_trace,
                         trust_summary, "GATE_GEL", "GX_GEL_INVALID_INPUT",
                         f"gel_evaluation_raised:{type(e).__name__}:{e}")

    if gel_verdict["verdict"] == "allow":
        final_verdict = "ALLOW"
    elif gel_verdict["verdict"] == "block":
        final_verdict = "BLOCK"
    elif gel_verdict["verdict"] == "redirect":
        final_verdict = "REDIRECT"
    else:
        final_verdict = "BLOCK"  # fail-closed on unknown verdict

    _record("GATE_GEL",
            "PASS" if final_verdict == "ALLOW" else "FAIL",
            gel_verdict.get("rule_id") or "PASS",
            f"gel_verdict={gel_verdict['verdict']}, rule_id={gel_verdict.get('rule_id')}",
            {"gel_verdict": gel_verdict["verdict"], "gel_rule_id": gel_verdict.get("rule_id")})
    trust_summary["gel_passed"] = (final_verdict == "ALLOW")

    return _finalize(envelope, envelope_h, identity_h, receipt_h, capability_h,
                     candidate_action_h, final_verdict, gel_verdict["executed_action"],
                     gate_trace, trust_summary,
                     "GATE_GEL" if final_verdict != "ALLOW" else None,
                     gel_verdict.get("rule_id") or "PASS",
                     f"gel_{gel_verdict['verdict']}")


def verify_decision(decision):
    """Verify a decision's audit trail integrity.

    Recomputes the evidence_chain_hash from the recorded audit_trail and
    compares it to the recorded evidence_chain_hash. Returns (match, details).
    """
    from crypto_utils import canonicalize_json
    if not isinstance(decision, dict):
        return (False, "decision_not_a_dict")
    audit = decision.get("audit_trail")
    if audit is None:
        return (False, "missing_audit_trail")
    expected_hash = decision.get("hashes", {}).get("evidence_chain_hash")
    if not expected_hash:
        return (False, "missing_recorded_chain_hash")
    recomputed = hashlib.sha256(canonicalize_json(audit)).hexdigest()
    return (recomputed == expected_hash, {
        "recorded_chain_hash": expected_hash,
        "recomputed_chain_hash": recomputed,
        "match": recomputed == expected_hash,
    })


def _finalize(envelope, envelope_h, identity_h, receipt_h, capability_h,
              candidate_action_h, final_verdict, executed_action,
              gate_trace, trust_summary, failing_gate, reason_code, reason_description):
    """Build the TrustDecision dict."""
    decision_id = hashlib.sha256(
        ((envelope_h or "") + ":" + str(int(time.time() * 1000)) + ":" + reason_code).encode("utf-8")
    ).hexdigest()[:32]

    # Compute evidence-chain hash: hash of all gate records in order
    chain_bytes = canonicalize_json(gate_trace)
    evidence_chain_hash = hashlib.sha256(chain_bytes).hexdigest()

    # First failing gate (if any)
    first_failing = None
    for g in gate_trace:
        if g["verdict"] == "FAIL":
            first_failing = g["gate_id"]
            break

    trust_summary["first_failing_gate"] = first_failing
    trust_summary["gel_passed"] = trust_summary.get("gel_passed")

    return {
        "schema_id": "TGE-ATE-DECISION/0.1",
        "decision_id": decision_id,
        "envelope_hash": envelope_h,
        "issued_at_utc": gate_trace[-1]["evaluated_at_utc"] if gate_trace else None,
        "verdict": final_verdict,
        "executed_action": executed_action,
        "audit_trail": gate_trace,
        "trust_summary": trust_summary,
        "hashes": {
            "identity_hash": identity_h,
            "receipt_hash": receipt_h,
            "capability_hash": capability_h,
            "candidate_action_hash": candidate_action_h,
            "envelope_hash": envelope_h,
            "evidence_chain_hash": evidence_chain_hash,
        },
        "failing_gate": first_failing,
        "reason_code": reason_code,
        "reason_description": reason_description,
    }

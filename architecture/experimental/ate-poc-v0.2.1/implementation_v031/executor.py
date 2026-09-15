"""ATE v0.3.1 governed-action executor.

This module is the ONLY module that mutates nonce state.

trust_decide() is pure (does NOT mark authorized or consume).
The executor:
  1. Verifies the TrustDecision signature.
  2. Verifies decision.envelope_fingerprint == envelope.envelope_binding_hash.
  3. Verifies decision.verdict == TRUST_GRANTED.
  4. Marks the nonce as AUTHORIZED.
  5. Executes the governed action.
  6. Atomically consumes the nonce (AUTHORIZED -> CONSUMED).

A replay attempt against CONSUMED nonce state fails at trust_decide() G8.
"""
from typing import Any, Dict, Tuple

from trust_decision import verify_trust_decision, GX_OK
from nonce_registry import NonceRegistry, NonceState


class GovernedActionError(Exception):
    pass


def execute_governed_action(
    envelope: Dict[str, Any],
    trust_decision: Dict[str, Any],
    *,
    trust_decision_pub_key,
    nonce_registry: NonceRegistry,
) -> Dict[str, Any]:
    """Verify the decision and execute the action.

    Returns a dict with:
      executed: bool
      executed_at_utc: float (informational)
      envelope_nonce: str
      resulting_nonce_state: str (post-execution)
      verification: dict

    Raises GovernedActionError if the decision is invalid or the action
    cannot execute.
    """
    # Pre-checks
    if trust_decision.get("verdict") != "TRUST_GRANTED":
        raise GovernedActionError(
            f"refusing to execute: verdict={trust_decision.get('verdict')}, "
            f"reason={trust_decision.get('reason_code')}"
        )
    if trust_decision.get("envelope_fingerprint") != envelope.get("envelope_binding_hash"):
        raise GovernedActionError(
            "decision.envelope_fingerprint does not match envelope.envelope_binding_hash"
        )
    if trust_decision.get("envelope_nonce") != envelope.get("envelope_nonce"):
        raise GovernedActionError(
            "decision.envelope_nonce does not match envelope.envelope_nonce"
        )
    if not verify_trust_decision(trust_decision, trust_decision_pub_key):
        raise GovernedActionError("TrustDecision signature invalid")

    # Mark nonce as AUTHORIZED
    nonce = envelope.get("envelope_nonce", "")
    if not isinstance(nonce, str) or not nonce:
        raise GovernedActionError("envelope.envelope_nonce missing or not a string")
    nonce_registry.mark_authorized(nonce)
    authorized_state = nonce_registry.lookup(nonce).value

    # Execute the governed action (deterministic, in-memory)
    execution_result = {
        "executed": True,
        "envelope_nonce": nonce,
        "operation": envelope.get("contents", {}).get("requested_action", {}).get("operation"),
        "target": envelope.get("contents", {}).get("requested_action", {}).get("target"),
        "executed_at_state": authorized_state,
    }

    # Atomically consume the nonce
    nonce_registry.consume(nonce)
    execution_result["resulting_nonce_state"] = nonce_registry.lookup(nonce).value
    return execution_result

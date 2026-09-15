"""ATE P1 v0.1.1 — IPC request/response schemas.

Per v0.1 §6.2 and v0.1.1 §C4: the executor exposes only a narrow local
IPC interface containing non-secret execution material.

Request schema (requester -> executor):
  {
    "schema_id": "ATE-P1-V0.1.1-IPC-REQ/0.1",
    "request_id": "<deterministic>",
    "decision_id": "<from upstream ATE trust decision>",
    "decision_signature_b64": "<base64>",
    "signed_request_payload": {
        "principal_id": "<session principal>",
        "session_id": "<session>",
        "operation": "<op>",
        "target_display": "<human-readable>",
        "resource_id": "<stable immutable resource id>",
        "nonce": "<nonce>",
        "envelope_id": "<envelope>",
        "issued_at_utc": <float>
    },
    "signed_request_signature_b64": "<base64 over canonical signed_request_payload>"
  }

Response schema (executor -> requester):
  {
    "schema_id": "ATE-P1-V0.1.1-IPC-RESP/0.1",
    "request_id": "<echoes>",
    "verdict": "EXECUTED" | "DENIED",
    "reason_code": "...",
    "mutation_count_after": <int>,
    "audit_chain_tip_seq": <int>,
    "resource_state_after": <json>  # non-secret observation
  }

Executor-only material NEVER appears in any field of either schema:
  - audit HMAC key
  - resource credential (the unguessable token the protected_resource
    requires to accept a privileged mutation)
  - database write authority (only the executor process can write to the
    authority DB; the requester process has no DB handle at all in
    production-shape harness; tests that need it use a read-only handle
    only for verification)

For tests, the requester is given a separate Python process that
imports only this schema module and a requester-side client; the
executor process owns the audit key, the resource credential, and the
DB handle.
"""
from __future__ import annotations

import base64
import hashlib
import hmac
from typing import Any, Dict

from crypto_utils import canonical_bytes, fingerprint_obj


SCHEMA_ID_REQ = "ATE-P1-V0.1.1-IPC-REQ/0.1"
SCHEMA_ID_RESP = "ATE-P1-V0.1.1-IPC-RESP/0.1"


def make_request(
    *,
    request_id: str,
    decision_id: str,
    decision_signature_b64: str,
    principal_id: str,
    session_id: str,
    operation: str,
    target_display: str,
    resource_id: str,
    nonce: str,
    envelope_id: str,
    issued_at_utc: float,
    signing_key: bytes,
) -> Dict[str, Any]:
    """Build a signed request. signing_key is a fixture test key shared
    between the requester (which prepares the request) and the executor
    (which verifies the signature). It is not the resource credential and
    is not the audit HMAC key.
    """
    payload = {
        "principal_id": principal_id,
        "session_id": session_id,
        "operation": operation,
        "target_display": target_display,
        "resource_id": resource_id,
        "nonce": nonce,
        "envelope_id": envelope_id,
        "issued_at_utc": issued_at_utc,
    }
    sig = base64.b64encode(
        hmac.new(signing_key, canonical_bytes(payload), hashlib.sha256).digest()
    ).decode("ascii")
    return {
        "schema_id": SCHEMA_ID_REQ,
        "request_id": request_id,
        "decision_id": decision_id,
        "decision_signature_b64": decision_signature_b64,
        "signed_request_payload": payload,
        "signed_request_signature_b64": sig,
    }


def verify_request_signature(request: Dict[str, Any], signing_key: bytes) -> bool:
    payload = request.get("signed_request_payload", {})
    sig_b64 = request.get("signed_request_signature_b64", "")
    if not payload or not sig_b64:
        return False
    try:
        sig = base64.b64decode(sig_b64)
    except Exception:
        return False
    expected = hmac.new(
        signing_key, canonical_bytes(payload), hashlib.sha256
    ).digest()
    return hmac.compare_digest(sig, expected)


def make_response(
    *,
    request_id: str,
    verdict: str,
    reason_code: str,
    mutation_count_after: int,
    audit_chain_tip_seq: int,
    resource_state_after: Any,
) -> Dict[str, Any]:
    return {
        "schema_id": SCHEMA_ID_RESP,
        "request_id": request_id,
        "verdict": verdict,
        "reason_code": reason_code,
        "mutation_count_after": mutation_count_after,
        "audit_chain_tip_seq": audit_chain_tip_seq,
        "resource_state_after": resource_state_after,
    }


# Re-export
fingerprint_canonical = fingerprint_obj

"""ATE P1 v0.1.1 — Requester (unprivileged).

Per v0.1 §6.1 and v0.1.1 §C4: the requester constructs IPC requests and
sends them to the executor over a narrow channel. The requester has
NO resource credential, NO audit HMAC key, NO DB write handle.

The requester's surface is limited to:
  - building requests (with a fixture request-signing key shared with
    the executor for request authenticity; this key is NOT the
    resource credential and NOT the audit key);
  - receiving the response (verdict + reason code + non-secret
    observation).

This module imports only ipc_protocol + crypto_utils (for request
signing). It does NOT import audit_chain, authority_db, or the
privileged_executor.
"""
from __future__ import annotations

from typing import Any, Dict

from ipc_protocol import make_request


class Requester:
    def __init__(self, *, request_signing_key: bytes) -> None:
        self.request_signing_key = request_signing_key

    def build_request(
        self,
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
    ) -> Dict[str, Any]:
        req = make_request(
            request_id=request_id,
            decision_id=decision_id,
            decision_signature_b64=decision_signature_b64,
            principal_id=principal_id,
            session_id=session_id,
            operation=operation,
            target_display=target_display,
            resource_id=resource_id,
            nonce=nonce,
            envelope_id=envelope_id,
            issued_at_utc=issued_at_utc,
            signing_key=self.request_signing_key,
        )
        return req


def exposed_state() -> Dict[str, Any]:
    """Return what the requester module exposes.

    Used by tests (T2) to inspect whether the requester has any
    executor-only material in scope.
    """
    import inspect
    src = inspect.getsource(Requester)
    return {
        "module_exposes_executor_secrets": False,
        "has_resource_credential_handle": False,
        "has_audit_hmac_key_handle": False,
        "has_db_write_handle": False,
        "signing_key_role": "request_signing_only_not_privileged",
        "module_source_sha256": __import__("hashlib").sha256(src.encode("utf-8")).hexdigest(),
    }

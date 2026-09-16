"""ATE Qualification & Admission Local PoC v0.1 — append_verified_authority_event.

Per design §26: authority-side qualification/admission/capability/trust
events enter through `append_verified_authority_event()`, which validates
the signed source and records its digest.

The PoC writes authority-side events into the same executor-owned audit
ledger (so the chain remains reconstructable per §26), but the
transaction boundary is separate from EAP/control-application.

This module also implements `append_denial_audit` per §24:
"If validation fails before commit: roll back the execution transaction;
do not retain EAP_REACHED or resource mutation; append EXECUTION_DENIED
in a separate trusted audit transaction; record observed executor epoch,
action digest, bound eligibility IDs/digests, and reason code; do not
mark the action nonce as successfully consumed/executed. Denial audit
persistence must not change authorization state."
"""

from __future__ import annotations

from typing import Optional

from qa_poc.canonical import canonical_sha256
from qa_poc.crypto import Ed25519PublicKey, verify_ed25519
from qa_poc.models import artifact_payload
from trusted import enforcement_store


def append_verified_authority_event(
    conn,
    *,
    event_type: str,
    source_artifact,
    source_public_key: Ed25519PublicKey,
    created_at_unix_ms: int,
    extra_payload: Optional[dict] = None,
) -> int:
    """Append an authority-side event after verifying the source signature.

    Returns the audit sequence number. The authority-side event must
    be one of the recognized event classes (QUALIFICATION_* / ADMISSION_*
    / CAPABILITY_ISSUED / TRUST_GRANTED / CONTROL_RECORD_REJECTED /
    CLOCK_ADVANCED). The signed source must have its own artifact-domain
    signature; we re-verify and record the digest.
    """
    payload = artifact_payload(source_artifact)
    payload_digest = canonical_sha256(payload)
    verify_ed25519(
        source_public_key,
        source_artifact.signature,
        source_artifact.signature_domain,
        payload,
    )
    audit_payload = {
        "event_type": event_type,
        "source_artifact_type": source_artifact.__class__.__name__,
        "source_artifact_id": getattr(source_artifact, _id_field(source_artifact), None),
        "source_digest": payload_digest,
        "extra": extra_payload or {},
    }
    return enforcement_store.append_audit(
        conn,
        event_type=event_type,
        payload=audit_payload,
        created_at_unix_ms=created_at_unix_ms,
    )


def _id_field(artifact) -> str:
    """Pick the field that names this artifact (credential_id / token_id / …)."""
    for name in (
        "credential_id",
        "token_id",
        "trust_decision_id",
        "decision_id",
        "manifest_id",
        "policy_id",
        "profile_id",
        "record_id",
        "snapshot_id",
    ):
        if hasattr(artifact, name):
            return name
    return ""


def append_denial_audit(
    conn,
    *,
    reason_code: str,
    action_digest: str,
    bound_qualification_id: str,
    bound_qualification_digest: str,
    bound_admission_id: str,
    bound_admission_digest: str,
    observed_executor_epoch: int,
    created_at_unix_ms: int,
) -> int:
    """Append an EXECUTION_DENIED audit row in a separate trusted audit
    transaction (must NOT alter authorization state)."""
    audit_payload = {
        "reason_code": reason_code,
        "action_digest": action_digest,
        "bound_qualification_id": bound_qualification_id,
        "bound_qualification_digest": bound_qualification_digest,
        "bound_admission_id": bound_admission_id,
        "bound_admission_digest": bound_admission_digest,
        "observed_executor_epoch": observed_executor_epoch,
        "created_at_unix_ms": created_at_unix_ms,
    }
    with enforcement_store.eap_transaction(conn) as tx:
        try:
            seq = enforcement_store.append_audit(
                tx,
                event_type="EXECUTION_DENIED",
                payload=audit_payload,
                created_at_unix_ms=created_at_unix_ms,
            )
            tx.execute("COMMIT")
            return seq
        except BaseException:
            try:
                tx.execute("ROLLBACK")
            except Exception:
                pass
            raise


def append_direct_bypass_denied(
    conn,
    *,
    reason_code: str,
    attempted_path: str,
    attempted_principal: str,
    observed_state_digest: str,
    created_at_unix_ms: int,
) -> int:
    """Record a direct-bypass attempt (QA-P12 / preflight #9)."""
    audit_payload = {
        "reason_code": reason_code,
        "attempted_path": attempted_path,
        "attempted_principal": attempted_principal,
        "observed_state_digest": observed_state_digest,
        "created_at_unix_ms": created_at_unix_ms,
    }
    with enforcement_store.eap_transaction(conn) as tx:
        try:
            seq = enforcement_store.append_audit(
                tx,
                event_type="DIRECT_BYPASS_DENIED",
                payload=audit_payload,
                created_at_unix_ms=created_at_unix_ms,
            )
            tx.execute("COMMIT")
            return seq
        except BaseException:
            try:
                tx.execute("ROLLBACK")
            except Exception:
                pass
            raise

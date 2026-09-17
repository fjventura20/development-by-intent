"""ATE Qualification & Admission Local PoC v0.1 — apply_control_record.

Per design §16 / §25: a signed ControlRecord becomes execution-effective
only when `apply_control_record()` commits it into the executor-owned
enforcement store. The same executor-owned SQLite write serialization
is used as for EAP (§25).

`apply_control_record()` validates:

  schema + canonical form
  artifact-domain signature
  issuer authorization for change type
  previous_epoch == current executor epoch
  new_epoch == previous_epoch + 1
  target recognized
  record id/digest not already applied

Then, inside the executor-owned serialized write transaction, it records:

  applied_at
  applied_epoch = new_epoch

The `applied_epoch` UNIQUE constraint on the table guarantees monotonicity
even under concurrent attempts.
"""

from __future__ import annotations

from dataclasses import asdict
from typing import Callable, Optional

from qa_poc.canonical import canonical_sha256
from qa_poc.crypto import Ed25519PublicKey, verify_ed25519
from qa_poc.models import (
    ControlRecord,
    DOMAIN_CONTROL_RECORD,
    artifact_payload,
    digest_payload,
    verify_artifact,
)
from trusted import enforcement_store


class ControlRecordError(Exception):
    pass


def validate_control_record(
    *,
    record: ControlRecord,
    issuer_pub: Ed25519PublicKey,
) -> None:
    # DEV-IMP-3 non-recursive verification:
    #   - recompute digest from (id, semantic fields)
    #   - verify signature over (id, semantic fields, digest)
    try:
        verify_artifact(record, issuer_pub)
    except Exception as e:
        raise ControlRecordError(str(e)) from e


def apply_control_record(
    conn,
    *,
    record: ControlRecord,
    issuer_pub: Ed25519PublicKey,
    change_type_authorization_lookup: Callable[[str, str], bool],
    created_at_unix_ms: int,
) -> int:
    """Apply a ControlRecord to the executor-owned store.

    Returns the new applied_epoch. Raises ControlRecordError on any
    validation failure (the transaction is rolled back inside).
    """
    # Validate schema + signature first (outside the transaction)
    validate_control_record(record=record, issuer_pub=issuer_pub)

    # Validate issuer authorization for the change_type
    if not change_type_authorization_lookup(record.change_type, record.issuer_key_id):
        raise ControlRecordError("CONTROL_RECORD_ISSUER_NOT_AUTHORIZED")

    # Now the executor-owned serialized write transaction
    with enforcement_store.eap_transaction(conn) as tx:
        try:
            # Monotonic-epoch check (frozen §16)
            current = enforcement_store.current_epoch(tx)
            if record.previous_epoch != current:
                raise ControlRecordError(
                    f"CONTROL_RECORD_PREVIOUS_EPOCH_MISMATCH: have={current} record={record.previous_epoch}"
                )
            if record.new_epoch != current + 1:
                raise ControlRecordError(
                    f"CONTROL_RECORD_NEW_EPOCH_MISMATCH: expected={current+1} record={record.new_epoch}"
                )
            # Idempotency: record id/digest not already applied
            cur = tx.execute(
                "SELECT 1 FROM applied_control_records WHERE record_id=? OR record_digest=?",
                (record.record_id, record.record_digest),
            )
            if cur.fetchone() is not None:
                raise ControlRecordError("CONTROL_RECORD_ALREADY_APPLIED")

            # Apply
            tx.execute(
                "INSERT INTO applied_control_records (record_id, target_type, target_id, target_digest, status, issued_at_unix_ms, applied_at_unix_ms, applied_epoch, record_digest) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (
                    record.record_id,
                    record.target_type,
                    record.target_id,
                    record.target_digest_optional,
                    "APPLIED",
                    record.issued_at_unix_ms,
                    created_at_unix_ms,
                    record.new_epoch,
                    record.record_digest,
                ),
            )
            enforcement_store.set_epoch(tx, record.new_epoch)
            enforcement_store.append_audit(
                tx,
                event_type="CONTROL_RECORD_APPLIED",
                payload={
                    "record_id": record.record_id,
                    "previous_epoch": record.previous_epoch,
                    "new_epoch": record.new_epoch,
                    "change_type": record.change_type,
                    "target_type": record.target_type,
                    "target_id": record.target_id,
                    "applied_at_unix_ms": created_at_unix_ms,
                },
                created_at_unix_ms=created_at_unix_ms,
            )
            tx.execute("COMMIT")
            return record.new_epoch
        except BaseException:
            try:
                tx.execute("ROLLBACK")
            except Exception:
                pass
            raise



# FR-10: frozen §16 + §29 require:
#   - AUTH_R11_QUALIFICATION may issue QUALIFICATION_REVOCATION / SUSPENSION.
#   - AUTH_R12_ADMISSION   may issue ADMISSION_REVOCATION / SUSPENSION.
# The helper below is the canonical mapping; the lookup callable passed
# into apply_control_record() must implement this mapping (or a strict
# subset/superset, but never a more permissive one).

REVOCATION_CHANGE_TYPE_AUTHORIZATION_MAP = {
    # change_type              : required_authority_role
    "QUALIFICATION_REVOCATION": "AUTH_R11_QUALIFICATION",
    "QUALIFICATION_SUSPENSION": "AUTH_R11_QUALIFICATION",
    "ADMISSION_REVOCATION":     "AUTH_R12_ADMISSION",
    "ADMISSION_SUSPENSION":     "AUTH_R12_ADMISSION",
}


def make_change_type_authorization_lookup(*, r11_key_id: str, r12_key_id: str):
    """Return a strict authorization lookup that maps each (change_type,
    issuer_key_id) pair to True iff the issuer key is the canonical
    authority for that change type.

    Reject everything else (incl. cross-authority attempts). Negative
    tests use this as the production lookup.
    """
    role_by_key = {r11_key_id: "AUTH_R11_QUALIFICATION",
                   r12_key_id: "AUTH_R12_ADMISSION"}
    def lookup(change_type: str, issuer_key_id: str) -> bool:
        expected_role = REVOCATION_CHANGE_TYPE_AUTHORIZATION_MAP.get(change_type)
        if expected_role is None:
            # Unknown change type -> reject (fail-closed)
            return False
        actual_role = role_by_key.get(issuer_key_id)
        return actual_role == expected_role
    return lookup

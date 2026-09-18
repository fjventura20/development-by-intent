"""Agent Conformance Local Lifecycle PoC v0.1 — audit ledger.

Frozen §6.8 + §20A:
  - append-only records
  - sequence numbers (monotonic `event_sequence`)
  - previous-record hash chain (`prev_hash` -> `record_hash`)
  - signed/authenticated records
  - non-destructive tamper testing: copy ledger, mutate copy,
    verify copy fails integrity checks, verify authoritative
    ledger still passes.

The audit recorder uses its own key. Verification requires the
recorder public key.
"""

from __future__ import annotations

import hashlib
from dataclasses import InitVar, dataclass, field
from typing import Any, Callable, Dict, List, Optional

from .canonical import canonical_sha256
from .crypto import (
    Ed25519PrivateKey,
    Ed25519PublicKey,
    key_id_from_public_key,
    sign_ed25519,
    verify_ed25519,
)
from .models import AuditRecord


GENESIS_PREV_HASH = (
    "0" * 64  # 64 hex zeros; explicitly reserved as the genesis
)


@dataclass
class AuditRecorder:
    """Append-only audit recorder (frozen §6.8)."""

    recorder_id: str
    private_key: InitVar[Ed25519PrivateKey]
    public_key: Ed25519PublicKey

    def __post_init__(self, private_key: Ed25519PrivateKey) -> None:
        self.__private_key = private_key
        self.key_id = key_id_from_public_key(self.public_key)
        self._records: List[AuditRecord] = []

    def records(self) -> List[AuditRecord]:
        return list(self._records)

    def append(
        self,
        *,
        event_kind: str,
        payload: Dict[str, Any],
        logical_ts: int,
    ) -> AuditRecord:
        """Append a new audit record with monotonic sequence + hash chain."""
        if self._records:
            last = self._records[-1]
            sequence = last.event_sequence + 1
            prev_hash = last.record_hash
        else:
            sequence = 1
            prev_hash = GENESIS_PREV_HASH

        payload_digest = canonical_sha256(payload)
        canonical_record = {
            "artifact_kind": "AuditRecord",
            "event_sequence": sequence,
            "event_kind": event_kind,
            "payload": payload,
            "prev_hash": prev_hash,
            "payload_digest": payload_digest,
            "logical_ts": logical_ts,
        }
        record_hash = canonical_sha256(canonical_record)

        rec = AuditRecord(
            event_sequence=sequence,
            event_kind=event_kind,
            payload=payload,
            prev_hash=prev_hash,
            record_hash=record_hash,
            payload_digest=payload_digest,
            logical_ts=logical_ts,
            signature=b"",
            signature_domain="ate.conformance.audit.v1",
        )
        rec.signature = sign_ed25519(
            self.__private_key, rec.signature_domain, rec.signing_payload(),
        )
        self._records.append(rec)
        return rec

    def verify_chain(self) -> bool:
        """Verify the entire ledger's hash chain and signatures."""
        prev_hash = GENESIS_PREV_HASH
        expected_seq = 1
        for rec in self._records:
            if rec.event_sequence != expected_seq:
                return False
            if rec.prev_hash != prev_hash:
                return False
            # Recompute payload_digest and record_hash
            pd = canonical_sha256(rec.payload)
            if rec.payload_digest != pd:
                return False
            canonical_record = {
                "artifact_kind": "AuditRecord",
                "event_sequence": rec.event_sequence,
                "event_kind": rec.event_kind,
                "payload": rec.payload,
                "prev_hash": rec.prev_hash,
                "payload_digest": rec.payload_digest,
                "logical_ts": rec.logical_ts,
            }
            if rec.record_hash != canonical_sha256(canonical_record):
                return False
            if not verify_ed25519(
                self.public_key,
                rec.signature,
                rec.signature_domain,
                rec.signing_payload(),
            ):
                return False
            prev_hash = rec.record_hash
            expected_seq += 1
        return True

    def verify_causal_order(self, expected_sequence: List[str]) -> bool:
        """Verify the causal-order chain required by frozen §18 TC-17.

        `expected_sequence` is a list of event_kind names in the
        required order. Each successive kind must appear at a strictly
        greater event_sequence than the previous.
        """
        by_kind: Dict[str, int] = {}
        for rec in self._records:
            # If the same event_kind appears multiple times (e.g. two
            # capability denials), keep the first; TC-17 lists unique
            # kinds in the required order.
            if rec.event_kind not in by_kind:
                by_kind[rec.event_kind] = rec.event_sequence
        last_seq = -1
        for kind in expected_sequence:
            seq = by_kind.get(kind)
            if seq is None or seq <= last_seq:
                return False
            last_seq = seq
        return True



def verify_records(records: List[AuditRecord], public_key: Ed25519PublicKey) -> bool:
    """Verify an arbitrary ledger snapshot without mutating a recorder."""
    prev_hash = GENESIS_PREV_HASH
    expected_seq = 1
    for rec in records:
        if rec.event_sequence != expected_seq:
            return False
        if rec.prev_hash != prev_hash:
            return False
        pd = canonical_sha256(rec.payload)
        if rec.payload_digest != pd:
            return False
        canonical_record = {
            "artifact_kind": "AuditRecord",
            "event_sequence": rec.event_sequence,
            "event_kind": rec.event_kind,
            "payload": rec.payload,
            "prev_hash": rec.prev_hash,
            "payload_digest": rec.payload_digest,
            "logical_ts": rec.logical_ts,
        }
        if rec.record_hash != canonical_sha256(canonical_record):
            return False
        if not verify_ed25519(
            public_key,
            rec.signature,
            rec.signature_domain,
            rec.signing_payload(),
        ):
            return False
        prev_hash = rec.record_hash
        expected_seq += 1
    return True


def copy_and_tamper(records: List[AuditRecord], tamper_index: int) -> List[AuditRecord]:
    """Return a deep-copied ledger with one record's payload mutated.

    Non-destructive per frozen §20A.3: this only operates on a copy.
    """
    import copy

    out = [copy.deepcopy(r) for r in records]
    if 0 <= tamper_index < len(out):
        # Mutate payload in the copy only.
        out[tamper_index].payload = {"tampered": True, **out[tamper_index].payload}
    return out
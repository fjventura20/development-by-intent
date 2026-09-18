"""Audit-ledger focused tests (frozen §6.8, §20A, §20A.1).

These tests target the AuditRecorder directly, independent of the
lifecycle driver. They cover:

  - genesis prev_hash sentinel
  - monotonic event_sequence
  - hash chain continuity (prev_hash matches previous record_hash)
  - record_hash == canonical_sha256(canonical_record)
  - per-record signature verifies under the recorder's public key
  - tamper detection on a non-destructive copy
  - causal-order verification for the canonical sequence required by
    frozen §18 TC-17
"""

from __future__ import annotations

import copy

import pytest

from conformance.audit import AuditRecorder, GENESIS_PREV_HASH, copy_and_tamper
from conformance.canonical import canonical_sha256
from conformance.crypto import generate_keypair


@pytest.fixture
def recorder():
    priv, pub = generate_keypair()
    return AuditRecorder(
        recorder_id="audit-unit",
        private_key=priv,
        public_key=pub,
    )


def _canon(rec):
    return {
        "artifact_kind": "AuditRecord",
        "event_sequence": rec.event_sequence,
        "event_kind": rec.event_kind,
        "payload": rec.payload,
        "prev_hash": rec.prev_hash,
        "payload_digest": rec.payload_digest,
        "logical_ts": rec.logical_ts,
    }


def test_genesis_prev_hash_is_sentinel(recorder):
    """Frozen §6.8: the first record's prev_hash is the reserved
    genesis sentinel (64 zeros)."""
    rec = recorder.append(
        event_kind="genesis",
        payload={"k": 1},
        logical_ts=1,
    )
    assert rec.prev_hash == GENESIS_PREV_HASH
    assert rec.event_sequence == 1
    assert len(GENESIS_PREV_HASH) == 64
    assert set(GENESIS_PREV_HASH) == {"0"}


def test_monotonic_event_sequence(recorder):
    """Frozen §20A: monotonic event_sequence per record."""
    for i in range(5):
        recorder.append(event_kind=f"e{i}", payload={"i": i}, logical_ts=i)
    seqs = [r.event_sequence for r in recorder.records()]
    assert seqs == [1, 2, 3, 4, 5]


def test_hash_chain_continuity(recorder):
    """Frozen §6.8: each record's prev_hash equals the prior record_hash."""
    recorder.append(event_kind="a", payload={"a": 1}, logical_ts=1)
    recorder.append(event_kind="b", payload={"b": 2}, logical_ts=2)
    recorder.append(event_kind="c", payload={"c": 3}, logical_ts=3)
    recs = recorder.records()
    assert recs[0].prev_hash == GENESIS_PREV_HASH
    assert recs[1].prev_hash == recs[0].record_hash
    assert recs[2].prev_hash == recs[1].record_hash


def test_record_hash_is_canonical_sha256_of_record(recorder):
    """Frozen §6.8: record_hash == canonical_sha256(canonical_record)."""
    for i in range(3):
        recorder.append(event_kind=f"e{i}", payload={"i": i}, logical_ts=i)
    for rec in recorder.records():
        assert rec.record_hash == canonical_sha256(_canon(rec))


def test_per_record_signature_verifies(recorder):
    """Frozen §6.8: each record's signature verifies under the recorder pub key."""
    for i in range(3):
        recorder.append(event_kind=f"e{i}", payload={"i": i}, logical_ts=i)
    from conformance.crypto import verify_ed25519
    for rec in recorder.records():
        assert verify_ed25519(
            recorder.public_key,
            rec.signature,
            rec.signature_domain,
            rec.signing_payload(),
        )


def test_verify_chain_passes_on_unmodified_ledger(recorder):
    """verify_chain() returns True when the ledger is intact."""
    for i in range(4):
        recorder.append(event_kind=f"e{i}", payload={"i": i}, logical_ts=i)
    assert recorder.verify_chain() is True


def test_tampered_payload_fails_chain_verification(recorder):
    """Frozen §20A.4: a tampered copy fails integrity checks; the
    authoritative ledger still passes."""
    for i in range(4):
        recorder.append(event_kind=f"e{i}", payload={"i": i}, logical_ts=i)
    original = recorder.records()
    tampered = copy_and_tamper(original, tamper_index=2)
    assert tampered is not original  # non-destructive copy

    # Swap and verify.
    recorder._records = tampered  # noqa: SLF001
    try:
        assert recorder.verify_chain() is False
    finally:
        recorder._records = original  # noqa: SLF001

    # Authoritative ledger still passes.
    assert recorder.verify_chain() is True


def test_causal_order_verification(recorder):
    """Frozen §18 TC-17: the required causal chain must be provable
    from the monotonic event_sequence values, not from timestamps."""
    # Build the canonical TC-17 sequence.
    sequence = [
        "c1_issued",
        "runtime_mutation",
        "trigger_observed",
        "n_plus_1_published",
        "c1_denied",
        "post_change_evidence",
        "r13_restore_eval",
        "n_plus_2_published",
        "c2_issued",
        "c2_effect",
    ]
    for kind in sequence:
        recorder.append(event_kind=kind, payload={"k": kind}, logical_ts=0)
    assert recorder.verify_causal_order(sequence) is True

    # Wrong order -> False.
    assert recorder.verify_causal_order(list(reversed(sequence))) is False

    # Missing kind -> False.
    assert recorder.verify_causal_order(sequence[:-1]) is True  # shorter prefix ok
    assert recorder.verify_causal_order(sequence + ["nonexistent"]) is False


def test_tampering_does_not_modify_authoritative_ledger(recorder):
    """Frozen §20A.1: the harness MUST NOT repair or regenerate the
    authoritative ledger after tamper testing."""
    for i in range(3):
        recorder.append(event_kind=f"e{i}", payload={"i": i}, logical_ts=i)
    original_records = copy.deepcopy(recorder.records())
    _ = copy_and_tamper(recorder.records(), tamper_index=1)
    # Authoritative ledger is unchanged.
    assert recorder.records() == original_records
    assert recorder.verify_chain() is True
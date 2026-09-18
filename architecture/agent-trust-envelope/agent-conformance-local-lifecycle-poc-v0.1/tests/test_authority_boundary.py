"""Authority-boundary regressions for participant-facing conformance APIs.

These tests target semantic signing-oracle and mutable-alias bypasses.
The PoC claim is an API/fixture boundary, not hostile same-process Python
introspection or OS/process isolation.
"""

from __future__ import annotations

import copy

import pytest

from conformance.models import RuntimeEvidence


def test_ab01_r13_rejects_fabricated_current_evidence(authority_harness):
    """A caller cannot change the semantic content of current observer evidence
    and have R13 sign a recommendation over the fabricated content."""
    h, _, controls = authority_harness

    controls.submit_measured_runtime("v2", "rt-ev-v2-ab01")
    authoritative = h.observer.store.get_evidence("rt-ev-v2-ab01")
    fabricated = copy.deepcopy(authoritative)
    fabricated.measured_runtime_version = "v1"

    with pytest.raises(PermissionError):
        h.r13.evaluate(
            subject_id=h.subject.subject_id,
            trust_domain=h.subject.trust_domain,
            runtime_evidence=fabricated,
            qualification_state="ACTIVE",
            admission_state="ACTIVE",
            trust_state_current=True,
        )


def test_ab02_r13_rejects_stale_but_valid_observer_evidence(authority_harness):
    """A previously valid signed runtime artifact is not enough: R13 must
    evaluate the observer store's current evidence."""
    h, _, controls = authority_harness

    controls.submit_measured_runtime("v1", "rt-ev-v1-ab02")
    stale = h.observer.store.get_evidence("rt-ev-v1-ab02")
    controls.submit_measured_runtime("v2", "rt-ev-v2-ab02")

    with pytest.raises(PermissionError):
        h.r13.evaluate(
            subject_id=h.subject.subject_id,
            trust_domain=h.subject.trust_domain,
            runtime_evidence=stale,
            qualification_state="ACTIVE",
            admission_state="ACTIVE",
            trust_state_current=True,
        )


def test_ab03_r13_rejects_caller_active_after_authoritative_revocation(authority_harness):
    """Caller-supplied ACTIVE cannot override authoritative qualification state."""
    h, _, controls = authority_harness

    controls.submit_measured_runtime("v1", "rt-ev-v1-ab03")
    current = h.observer.store.get_evidence("rt-ev-v1-ab03")
    controls.revoke_qualification(h.qualification.artifact_id)

    with pytest.raises(PermissionError):
        h.r13.evaluate(
            subject_id=h.subject.subject_id,
            trust_domain=h.subject.trust_domain,
            runtime_evidence=current,
            qualification_state="ACTIVE",
            admission_state="ACTIVE",
            trust_state_current=True,
        )


def test_ab04_subject_and_observer_reads_are_defensive_copies(authority_harness):
    """Participant mutations of returned subject/evidence objects cannot rewrite
    the authoritative identity or observer history."""
    h, _, controls = authority_harness

    authoritative_subject_before = h.state_store.get_subject(h.subject.subject_id)
    h.subject.role_id = "attacker-role"
    authoritative_subject_after = h.state_store.get_subject(
        authoritative_subject_before.subject_id
    )
    assert authoritative_subject_after.role_id == authoritative_subject_before.role_id
    assert authoritative_subject_after.role_id == "worker"

    replacement = copy.deepcopy(authoritative_subject_before)
    replacement.role_id = "replacement-role"
    with pytest.raises(PermissionError):
        h.state_store.add_subject(replacement)
    assert h.state_store.get_subject(replacement.subject_id).role_id == "worker"

    controls.submit_measured_runtime("v1", "rt-ev-v1-ab04")
    evidence_copy = h.observer.store.get_evidence("rt-ev-v1-ab04")
    evidence_copy.measured_runtime_version = "forged"
    evidence_fresh = h.observer.store.get_evidence("rt-ev-v1-ab04")
    assert evidence_fresh.measured_runtime_version == "v1"

    history_copy = h.observer.store.history()
    assert len(history_copy) == 1
    history_copy[0].measured_runtime_version = "rewritten"
    assert (
        h.observer.store.get_evidence("rt-ev-v1-ab04").measured_runtime_version
        == "v1"
    )


def test_ab05_authorization_rejects_non_governed_action(harness):
    """Capability issuer cannot be used to sign an action outside the frozen PoC contract."""
    h, _ = harness
    cap = h.authorization.issue_capability(
        subject=h.subject,
        action="DELETE_RESOURCE",
        action_payload={"target": "protected_resource.txt", "payload_digest_hex": "0" * 64},
        qualification=h.qualification,
        admission=h.admission,
        nonce="ab05-non-governed-action",
        ttl_ticks=10,
        clock_now=h.clock.now(),
    )
    assert cap is None

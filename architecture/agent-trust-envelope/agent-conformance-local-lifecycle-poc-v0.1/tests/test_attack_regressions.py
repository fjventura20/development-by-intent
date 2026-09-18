"""Targeted regression tests for F1-F5 attack paths.

Each test exercises the actual R14 publication path, executor
execution path, or authorization verification path with forged /
mismatched inputs to confirm the F2-F5 corrections detect and reject
the attack.

The `harness` fixture in conftest.py drives the harness to the
initial CONFORMANT @ epoch 1 state and yields (h, e). Tests may then
mutate runtime + forge artifacts and attempt adversarial transitions.
"""

from __future__ import annotations

import copy

import pytest

from conformance.canonical import canonical_sha256
from conformance.crypto import generate_keypair, sign_ed25519
from conformance.executor import (
    REASON_FIXTURE_INACTIVE,
    REASON_FIXTURE_UNREGISTERED,
)
from conformance.lifecycle import TransitionInputError
from conformance.models import (
    LIFECYCLE_CONFORMANT,
    LIFECYCLE_REATTESTATION_REQUIRED,
    R13Evaluation,
    TriggerObservation,
)
from fixtures import bootstrap


def _r13_recommends_invalidated(h, ev_v2, profile_v1_digest):
    """Evaluate after v1->v2 mutation; returns the R13 result."""
    return h.r13.evaluate(
        subject_id=h.subject.subject_id,
        trust_domain=h.subject.trust_domain,
        profile=h.profile_v1,
        profile_digest=profile_v1_digest,
        runtime_evidence=ev_v2,
        qualification_state="ACTIVE",
        admission_state="ACTIVE",
        trust_state_current=True,
    )


def _profile_v1_digest(h):
    return canonical_sha256(h.profile_v1.signing_payload())


# ---------------------------------------------------------------------------
# F2 regressions: R14 verifies R13 + trigger before publishing
# ---------------------------------------------------------------------------


def test_f2_forged_r13_signature_rejected_at_r14_path(harness):
    """F2: a forged R13 evaluation (signature by a non-R13 key) is
    rejected at the actual R14 publication path. No R14 artifact is
    produced and authoritative state is unchanged."""
    h, _ = harness
    epoch_before = h.state_store.state_epoch(h.subject.subject_id)
    state_before = h.state_store.current_state(h.subject.subject_id)

    # Mutate and obtain a real R13 evaluation that recommends
    # REATTESTATION_REQUIRED.
    h.observer.submit_measured_runtime("v2", "rt-ev-v2")
    ev_v2 = h.observer.store.get_evidence("rt-ev-v2")
    r13_inv = _r13_recommends_invalidated(h, ev_v2, _profile_v1_digest(h))

    # Forge a parallel R13 evaluation signed by a different key.
    forger_priv, _ = generate_keypair()
    forged = R13Evaluation(
        artifact_id="r13-forged-f2",
        subject_id=h.subject.subject_id,
        trust_domain=h.subject.trust_domain,
        profile_id="local-conformance-poc",
        profile_version=1,
        profile_digest=_profile_v1_digest(h),
        runtime_evidence_id=ev_v2.artifact_id,
        measured_runtime_version="v2",
        qualification_state="ACTIVE",
        admission_state="ACTIVE",
        recommended_state=LIFECYCLE_REATTESTATION_REQUIRED,
        rationale="forged",
        logical_ts=h.clock.advance(),
        event_sequence=h.clock.now(),
        signature_domain="ate.conformance.r13_eval.v1",
    )
    forged.signature = sign_ed25519(
        forger_priv, forged.signature_domain, forged.signing_payload(),
    )
    with pytest.raises(TransitionInputError):
        h.r14.publish_transition(
            subject=h.subject,
            prior_state=LIFECYCLE_CONFORMANT,
            new_state=LIFECYCLE_REATTESTATION_REQUIRED,
            rationale="forged r13",
            r13_evaluation=forged,
            trigger_observation=None,
        )
    assert h.state_store.state_epoch(h.subject.subject_id) == epoch_before
    assert h.state_store.current_state(h.subject.subject_id) == state_before


def test_f2_r13_subject_mismatch_rejected(harness):
    """F2: an R13 evaluation bound to a different subject is rejected
    at the R14 publication path."""
    h, _ = harness
    epoch_before = h.state_store.state_epoch(h.subject.subject_id)

    h.observer.submit_measured_runtime("v2", "rt-ev-v2")
    ev_v2 = h.observer.store.get_evidence("rt-ev-v2")
    r13 = _r13_recommends_invalidated(h, ev_v2, _profile_v1_digest(h))
    # Tamper subject_id and re-sign with the real R13 key so signature
    # is valid but binding is wrong.
    r13.subject_id = "different-subject"
    r13.signature = sign_ed25519(
        h.r13.private_key, r13.signature_domain, r13.signing_payload(),
    )
    with pytest.raises(TransitionInputError):
        h.r14.publish_transition(
            subject=h.subject,
            prior_state=LIFECYCLE_CONFORMANT,
            new_state=LIFECYCLE_REATTESTATION_REQUIRED,
            rationale="subject mismatch",
            r13_evaluation=r13,
            trigger_observation=None,
        )
    assert h.state_store.state_epoch(h.subject.subject_id) == epoch_before


def test_f2_r13_recommendation_mismatch_rejected(harness):
    """F2: an R13 evaluation that recommends CONFORMANT but is passed
    to a transition requesting REATTESTATION_REQUIRED is rejected."""
    h, _ = harness
    epoch_before = h.state_store.state_epoch(h.subject.subject_id)

    h.observer.submit_measured_runtime("v2", "rt-ev-v2")
    trigger = h.observer.observe_change(h.subject.subject_id, h.subject.trust_domain)
    ev_v2 = h.observer.store.get_evidence("rt-ev-v2")
    r13_inv = _r13_recommends_invalidated(h, ev_v2, _profile_v1_digest(h))
    # r13_inv.recommended_state == REATTESTATION_REQUIRED; request
    # CONFORMANT — must be rejected.
    with pytest.raises(TransitionInputError):
        h.r14.publish_transition(
            subject=h.subject,
            prior_state=LIFECYCLE_CONFORMANT,
            new_state=LIFECYCLE_CONFORMANT,
            rationale="recommendation mismatch",
            r13_evaluation=r13_inv,
            trigger_observation=trigger,
        )
    assert h.state_store.state_epoch(h.subject.subject_id) == epoch_before


def test_f2_prior_state_mismatch_rejected(harness):
    """F2: a transition that declares the wrong prior_state is rejected."""
    h, _ = harness
    epoch_before = h.state_store.state_epoch(h.subject.subject_id)

    h.observer.submit_measured_runtime("v2", "rt-ev-v2")
    ev_v2 = h.observer.store.get_evidence("rt-ev-v2")
    r13_inv = _r13_recommends_invalidated(h, ev_v2, _profile_v1_digest(h))
    # Declare prior_state = SUSPENDED (wrong; current is CONFORMANT).
    with pytest.raises(TransitionInputError):
        h.r14.publish_transition(
            subject=h.subject,
            prior_state="SUSPENDED",
            new_state=LIFECYCLE_REATTESTATION_REQUIRED,
            rationale="prior state mismatch",
            r13_evaluation=r13_inv,
            trigger_observation=None,
        )
    assert h.state_store.state_epoch(h.subject.subject_id) == epoch_before


def test_f2_forged_trigger_rejected(harness):
    """F2: a trigger observation signed by a non-observer key is
    rejected at the R14 publication path."""
    h, _ = harness
    epoch_before = h.state_store.state_epoch(h.subject.subject_id)

    h.observer.submit_measured_runtime("v2", "rt-ev-v2")
    ev_v2 = h.observer.store.get_evidence("rt-ev-v2")
    r13_inv = _r13_recommends_invalidated(h, ev_v2, _profile_v1_digest(h))

    forger_priv, _ = generate_keypair()
    forged_trigger = TriggerObservation(
        artifact_id="trigger-forged-f2",
        trigger_class="T4_RUNTIME",
        trigger_type="RUNTIME_VERSION_CHANGED",
        subject_id=h.subject.subject_id,
        trust_domain=h.subject.trust_domain,
        prior_value_digest=canonical_sha256({"value": "v1"}),
        current_value_digest=canonical_sha256({"value": "v2"}),
        severity="MANDATORY_REATTESTATION",
        prior_evidence_id="rt-ev-v1",
        current_evidence_id="rt-ev-v2",
        logical_ts=h.clock.advance(),
        event_sequence=h.clock.now(),
        signature_domain="ate.conformance.trigger_observation.v1",
    )
    forged_trigger.signature = sign_ed25519(
        forger_priv,
        forged_trigger.signature_domain,
        forged_trigger.signing_payload(),
    )
    with pytest.raises(TransitionInputError):
        h.r14.publish_transition(
            subject=h.subject,
            prior_state=LIFECYCLE_CONFORMANT,
            new_state=LIFECYCLE_REATTESTATION_REQUIRED,
            rationale="forged trigger",
            r13_evaluation=r13_inv,
            trigger_observation=forged_trigger,
        )
    assert h.state_store.state_epoch(h.subject.subject_id) == epoch_before


def test_f2_missing_trigger_when_required_rejected(harness):
    """F2: the runtime-mutation path requires a trigger. Publishing
    REATTESTATION_REQUIRED without one is rejected."""
    h, _ = harness
    epoch_before = h.state_store.state_epoch(h.subject.subject_id)

    h.observer.submit_measured_runtime("v2", "rt-ev-v2")
    ev_v2 = h.observer.store.get_evidence("rt-ev-v2")
    r13_inv = _r13_recommends_invalidated(h, ev_v2, _profile_v1_digest(h))
    with pytest.raises(TransitionInputError):
        h.r14.publish_transition(
            subject=h.subject,
            prior_state=LIFECYCLE_CONFORMANT,
            new_state=LIFECYCLE_REATTESTATION_REQUIRED,
            rationale="no trigger",
            r13_evaluation=r13_inv,
            trigger_observation=None,
        )
    assert h.state_store.state_epoch(h.subject.subject_id) == epoch_before


# ---------------------------------------------------------------------------
# F4 regressions: qualification/admission issuer binding
# ---------------------------------------------------------------------------


def test_f4_mismatched_issuer_id_rejected(harness):
    """F4: a qualification fixture with an issuer id that does not
    match the registered issuer identity is rejected at issuance."""
    h, _ = harness

    bad_qual = copy.deepcopy(h.qualification)
    bad_qual.issuer = "rogue-issuer"
    bad_qual.artifact_digest = canonical_sha256(bad_qual.signing_payload())
    bad_qual.signature = sign_ed25519(
        h.qual_admission_priv, bad_qual.signature_domain, bad_qual.signing_payload(),
    )
    cap = h.authorization.issue_capability(
        subject=h.subject,
        action="WRITE_RESOURCE",
        action_payload=bootstrap.ACTION_PAYLOAD,
        qualification=bad_qual,
        admission=h.admission,
        nonce="f4-issuer-id",
        ttl_ticks=10,
        clock_now=h.clock.now(),
    )
    assert cap is None


def test_f4_mismatched_issuer_key_id_rejected(harness):
    """F4: a fixture with an issuer_key_id that doesn't match the
    registered issuer pub key id is rejected."""
    h, _ = harness

    bad_qual = copy.deepcopy(h.qualification)
    bad_qual.issuer_key_id = "deadbeef" * 8  # wrong key id
    bad_qual.artifact_digest = canonical_sha256(bad_qual.signing_payload())
    bad_qual.signature = sign_ed25519(
        h.qual_admission_priv, bad_qual.signature_domain, bad_qual.signing_payload(),
    )
    cap = h.authorization.issue_capability(
        subject=h.subject,
        action="WRITE_RESOURCE",
        action_payload=bootstrap.ACTION_PAYLOAD,
        qualification=bad_qual,
        admission=h.admission,
        nonce="f4-issuer-key",
        ttl_ticks=10,
        clock_now=h.clock.now(),
    )
    assert cap is None


def test_f4_tampered_artifact_digest_rejected(harness):
    """F4: a fixture whose `artifact_digest` does not match the
    canonical SHA-256 of its signing payload is rejected."""
    h, _ = harness

    bad_qual = copy.deepcopy(h.qualification)
    bad_qual.artifact_digest = "0" * 64  # wrong digest
    # Signature and digest intentionally diverge.
    cap = h.authorization.issue_capability(
        subject=h.subject,
        action="WRITE_RESOURCE",
        action_payload=bootstrap.ACTION_PAYLOAD,
        qualification=bad_qual,
        admission=h.admission,
        nonce="f4-artifact-digest",
        ttl_ticks=10,
        clock_now=h.clock.now(),
    )
    assert cap is None


# ---------------------------------------------------------------------------
# F5 regressions: executor resolves authoritative fixtures from StateStore
# ---------------------------------------------------------------------------


def test_f5_executor_reads_fixtures_by_artifact_id_from_state_store(harness):
    """F5: the executor resolves the current qualification fixture by
    artifact_id from StateStore (not from a caller-supplied object).
    We verify the boundary by: (a) confirming the registered fixture
    is the same object StateStore holds (so caller can reach it), and
    (b) re-pointing the capability's `qualification_artifact_id` at
    an unregistered id and observing denial."""
    h, e = harness
    # Registered fixture is the same object the harness exposes.
    from_state = h.state_store.get_qualification_fixture(h.qualification.artifact_id)
    assert from_state is h.qualification

    cap = h.authorization.issue_capability(
        subject=h.subject,
        action="WRITE_RESOURCE",
        action_payload=bootstrap.ACTION_PAYLOAD,
        qualification=h.qualification,
        admission=h.admission,
        nonce="f5-resolution",
        ttl_ticks=10,
        clock_now=h.clock.now(),
    )
    assert cap is not None

    # Now re-point the capability at an artifact_id that is NOT
    # registered. The executor must NOT find a fixture and must deny
    # at step 4, regardless of whether the caller could supply a
    # matching object.
    cap.qualification_artifact_id = "qual-does-not-exist"
    cap.signature = sign_ed25519(
        h.authorization.private_key,
        cap.signature_domain,
        cap.signing_payload(),
    )
    res = e.execute(
        subject=h.subject,
        capability=cap,
        action="WRITE_RESOURCE",
        action_payload=bootstrap.ACTION_PAYLOAD,
        clock_now=h.clock.now(),
    )
    assert res.granted is False
    assert res.reason == REASON_FIXTURE_UNREGISTERED


def test_f5_unregistered_qualification_artifact_id_denied(harness):
    """F5: a capability bound to a qualification artifact_id that
    is NOT registered in StateStore is denied at step 4."""
    h, e = harness

    cap = h.authorization.issue_capability(
        subject=h.subject,
        action="WRITE_RESOURCE",
        action_payload=bootstrap.ACTION_PAYLOAD,
        qualification=h.qualification,
        admission=h.admission,
        nonce="f5-unregistered",
        ttl_ticks=10,
        clock_now=h.clock.now(),
    )
    assert cap is not None

    # Re-point the capability at an unregistered artifact_id and re-sign.
    cap.qualification_artifact_id = "qual-does-not-exist"
    cap.signature = sign_ed25519(
        h.authorization.private_key,
        cap.signature_domain,
        cap.signing_payload(),
    )
    res = e.execute(
        subject=h.subject,
        capability=cap,
        action="WRITE_RESOURCE",
        action_payload=bootstrap.ACTION_PAYLOAD,
        clock_now=h.clock.now(),
    )
    assert res.granted is False
    assert res.reason == REASON_FIXTURE_UNREGISTERED


def test_f5_revoked_qualification_state_denied_at_execution(harness):
    """F5: when the authoritative qualification fixture in StateStore
    transitions to REVOKED between issuance and execution, the
    executor denies at step 4 — even though the capability was
    issued with an active qualification at the time."""
    h, e = harness

    cap = h.authorization.issue_capability(
        subject=h.subject,
        action="WRITE_RESOURCE",
        action_payload=bootstrap.ACTION_PAYLOAD,
        qualification=h.qualification,
        admission=h.admission,
        nonce="f5-revoked-after-issue",
        ttl_ticks=10,
        clock_now=h.clock.now(),
    )
    assert cap is not None

    # Revoke the qualification fixture in StateStore.
    h.qualification.current_state = "REVOKED"

    res = e.execute(
        subject=h.subject,
        capability=cap,
        action="WRITE_RESOURCE",
        action_payload=bootstrap.ACTION_PAYLOAD,
        clock_now=h.clock.now(),
    )
    assert res.granted is False
    assert res.reason == REASON_FIXTURE_INACTIVE


# ---------------------------------------------------------------------------
# F3 regression: protected writer token is module-private
# ---------------------------------------------------------------------------


def test_f3_no_public_lifecycle_state_setters_on_state_store(harness):
    """F3: confirm there is no public mutator for current_state or
    state_epoch on StateStore."""
    h, _ = harness
    public_mutators = {
        m for m in dir(h.state_store)
        if not m.startswith("_")
        and callable(getattr(h.state_store, m, None))
    }
    forbidden = {
        "set_current_state", "set_state_epoch",
        "mutate_lifecycle", "set_lifecycle_state",
        "write_lifecycle", "update_current_state",
        "update_state_epoch",
    }
    assert forbidden.isdisjoint(public_mutators), (
        f"forbidden mutators exposed: {forbidden & public_mutators}"
    )
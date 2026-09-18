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


def test_f2_forged_r13_signature_rejected_at_r14_path(authority_harness):
    """F2: a forged R13 evaluation (signature by a non-R13 key) is
    rejected at the actual R14 publication path. No R14 artifact is
    produced and authoritative state is unchanged."""
    h, _, controls = authority_harness
    epoch_before = h.state_store.state_epoch(h.subject.subject_id)
    state_before = h.state_store.current_state(h.subject.subject_id)

    # Mutate and obtain a real R13 evaluation that recommends
    # REATTESTATION_REQUIRED.
    controls.submit_measured_runtime("v2", "rt-ev-v2")
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


def test_f2_r13_subject_mismatch_rejected(authority_harness):
    """F2: an R13 evaluation bound to a different subject is rejected
    at the R14 publication path."""
    h, _, controls = authority_harness
    epoch_before = h.state_store.state_epoch(h.subject.subject_id)

    controls.submit_measured_runtime("v2", "rt-ev-v2")
    ev_v2 = h.observer.store.get_evidence("rt-ev-v2")
    r13 = _r13_recommends_invalidated(h, ev_v2, _profile_v1_digest(h))
    # Tamper subject_id and re-sign with the real R13 key so signature
    # is valid but binding is wrong.
    r13.subject_id = "different-subject"
    controls.sign_r13_for_attack_test(r13)
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


def test_f2_r13_recommendation_mismatch_rejected(authority_harness):
    """F2: an R13 evaluation that recommends CONFORMANT but is passed
    to a transition requesting REATTESTATION_REQUIRED is rejected."""
    h, _, controls = authority_harness
    epoch_before = h.state_store.state_epoch(h.subject.subject_id)

    controls.submit_measured_runtime("v2", "rt-ev-v2")
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


def test_f2_prior_state_mismatch_rejected(authority_harness):
    """F2: a transition that declares the wrong prior_state is rejected."""
    h, _, controls = authority_harness
    epoch_before = h.state_store.state_epoch(h.subject.subject_id)

    controls.submit_measured_runtime("v2", "rt-ev-v2")
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


def test_f2_forged_trigger_rejected(authority_harness):
    """F2: a trigger observation signed by a non-observer key is
    rejected at the R14 publication path."""
    h, _, controls = authority_harness
    epoch_before = h.state_store.state_epoch(h.subject.subject_id)

    controls.submit_measured_runtime("v2", "rt-ev-v2")
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


def test_f2_missing_trigger_when_required_rejected(authority_harness):
    """F2: the runtime-mutation path requires a trigger. Publishing
    REATTESTATION_REQUIRED without one is rejected."""
    h, _, controls = authority_harness
    epoch_before = h.state_store.state_epoch(h.subject.subject_id)

    controls.submit_measured_runtime("v2", "rt-ev-v2")
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


def test_f4_mismatched_issuer_id_rejected(authority_harness):
    h, _, controls = authority_harness
    bad_qual = copy.deepcopy(h.qualification)
    bad_qual.issuer = "rogue-issuer"
    controls.sign_qa_fixture_for_attack_test(bad_qual)
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


def test_f4_mismatched_issuer_key_id_rejected(authority_harness):
    h, _, controls = authority_harness
    bad_qual = copy.deepcopy(h.qualification)
    bad_qual.issuer_key_id = "deadbeef" * 8
    controls.sign_qa_fixture_for_attack_test(bad_qual)
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
    h, _ = harness
    bad_qual = copy.deepcopy(h.qualification)
    bad_qual.artifact_digest = "0" * 64
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


def test_f5_executor_reads_fixtures_by_artifact_id_from_state_store(authority_harness):
    """F5: the executor resolves the current qualification fixture by
    artifact_id from StateStore (not from a caller-supplied object).
    We verify the boundary by re-pointing the capability's
    `qualification_artifact_id` at an unregistered id and observing
    denial. G3 fix: `get_qualification_fixture()` returns a deep
    copy; caller mutations cannot reach authoritative state."""
    h, e, controls = authority_harness

    # The harness exposes a reference to the fixture it registered
    # (call it `caller_fixture`). It is NOT the authoritative record.
    caller_fixture = h.qualification
    internal = h.state_store.get_qualification_fixture(caller_fixture.artifact_id)
    # Per G3, get_qualification_fixture() returns a fresh deep copy
    # each time. Caller's reference is not the authoritative record.
    assert caller_fixture is not internal
    # Mutate the caller's reference to REVOKED; the internal record
    # must remain ACTIVE.
    caller_fixture.current_state = "REVOKED"
    internal_again = h.state_store.get_qualification_fixture(
        caller_fixture.artifact_id,
    )
    assert internal_again.current_state == "ACTIVE"

    # Fetch a fresh internal copy (G3: get_*_fixture returns a deep
    # copy of authoritative state) for capability issuance.
    qual_for_issue = h.state_store.get_qualification_fixture(
        h.qualification.artifact_id,
    )
    cap = h.authorization.issue_capability(
        subject=h.subject,
        action="WRITE_RESOURCE",
        action_payload=bootstrap.ACTION_PAYLOAD,
        qualification=qual_for_issue,
        admission=h.admission,
        nonce="f5-resolution",
        ttl_ticks=10,
        clock_now=h.clock.now(),
    )
    assert cap is not None

    # Re-point the capability at an artifact_id that is NOT
    # registered. The executor must NOT find a fixture and must deny
    # at step 4, regardless of whether the caller could supply a
    # matching object.
    cap.qualification_artifact_id = "qual-does-not-exist"
    controls.sign_capability_for_attack_test(cap)
    res = e.execute(
        subject=h.subject,
        capability=cap,
        action="WRITE_RESOURCE",
        action_payload=bootstrap.ACTION_PAYLOAD,
        clock_now=h.clock.now(),
    )
    assert res.granted is False
    assert res.reason == REASON_FIXTURE_UNREGISTERED


def test_f5_unregistered_qualification_artifact_id_denied(authority_harness):
    """F5: a capability bound to a qualification artifact_id that
    is NOT registered in StateStore is denied at step 4."""
    h, e, controls = authority_harness

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
    controls.sign_capability_for_attack_test(cap)
    res = e.execute(
        subject=h.subject,
        capability=cap,
        action="WRITE_RESOURCE",
        action_payload=bootstrap.ACTION_PAYLOAD,
        clock_now=h.clock.now(),
    )
    assert res.granted is False
    assert res.reason == REASON_FIXTURE_UNREGISTERED


def test_f5_revoked_qualification_state_denied_at_execution(authority_harness):
    """Executor resolves authoritative current qualification state at execution."""
    h, e, controls = authority_harness
    qual_for_issue = h.state_store.get_qualification_fixture(
        h.qualification.artifact_id,
    )
    cap = h.authorization.issue_capability(
        subject=h.subject,
        action="WRITE_RESOURCE",
        action_payload=bootstrap.ACTION_PAYLOAD,
        qualification=qual_for_issue,
        admission=h.admission,
        nonce="f5-revoked-after-issue",
        ttl_ticks=10,
        clock_now=h.clock.now(),
    )
    assert cap is not None
    controls.revoke_qualification(h.qualification.artifact_id)
    h.qualification.current_state = "ACTIVE"
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
# F3 / G1 regressions: lifecycle authority boundary
# ---------------------------------------------------------------------------


def test_f3_no_public_lifecycle_state_setters_on_state_store(harness):
    h, _ = harness
    public_methods = {
        m for m in dir(h.state_store)
        if not m.startswith("_") and callable(getattr(h.state_store, m, None))
    }
    forbidden = {
        "set_current_state", "set_state_epoch", "mutate_lifecycle",
        "set_lifecycle_state", "get_authoritative_state_writer_token",
        "acquire_writer_token",
    }
    assert forbidden.isdisjoint(public_methods)


def test_g1_get_authoritative_state_returns_immutable_snapshot(harness):
    h, _ = harness
    snapshot = h.state_store.get_authoritative_state(h.subject.subject_id)
    with pytest.raises(Exception):
        snapshot.current_state = "CONFORMANT"  # type: ignore[misc]
    assert h.state_store.current_state(h.subject.subject_id) == LIFECYCLE_CONFORMANT


def test_g1_no_lifecycle_writer_token_api(harness):
    h, _ = harness
    import conformance.state as state_module
    assert not hasattr(state_module, "get_authoritative_state_writer_token")
    assert not hasattr(state_module, "acquire_writer_token")
    assert not hasattr(state_module, "_get_authoritative_state_writer_token_internal")
    # The StateStore write path accepts an R14 state artifact, not a token.
    assert "authorized_caller_token" not in (
        h.state_store.apply_authoritative_state.__code__.co_varnames
    )


def test_g1_forged_r14_state_cannot_mutate_store(harness):
    h, _ = harness
    from conformance.models import R14State
    from conformance.crypto import generate_keypair, sign_ed25519

    before = h.state_store.get_authoritative_state(h.subject.subject_id)
    forger_priv, _ = generate_keypair()
    forged = R14State(
        artifact_id="r14-forged-store-write",
        subject_id=h.subject.subject_id,
        role_id=h.subject.role_id,
        trust_domain=h.subject.trust_domain,
        prior_state=before.current_state,
        new_state="REATTESTATION_REQUIRED",
        state_epoch=before.state_epoch + 1,
        rationale="forged direct store mutation",
        r13_evaluation_id="none",
        trigger_observation_id="none",
        logical_ts=h.clock.advance(),
        event_sequence=h.clock.now(),
        signature_domain="ate.conformance.r14_state.v1",
    )
    forged.signature = sign_ed25519(
        forger_priv, forged.signature_domain, forged.signing_payload(),
    )
    with pytest.raises(PermissionError):
        h.state_store.apply_authoritative_state(forged)
    after = h.state_store.get_authoritative_state(h.subject.subject_id)
    assert after == before


def test_g1_rollback_to_conformant_at_n_rejected(invalidated_lifecycle):
    ctx = invalidated_lifecycle
    h = ctx.harness
    before = h.state_store.get_authoritative_state(h.subject.subject_id)
    assert before.current_state == LIFECYCLE_REATTESTATION_REQUIRED
    assert before.state_epoch == 2

    # Participant has no token-based rollback surface.
    with pytest.raises(TypeError):
        h.state_store.apply_authoritative_state(
            h.subject.subject_id, "CONFORMANT", 1  # type: ignore[arg-type]
        )
    assert h.state_store.get_authoritative_state(h.subject.subject_id) == before


# ---------------------------------------------------------------------------
# G2 / H1-H3 regressions: frozen profile registry
# ---------------------------------------------------------------------------


def test_g2_unsigned_profile_rejected_at_registration(harness):
    h, _ = harness
    from conformance.models import ConformanceProfile
    from conformance.profile_registry import ProfileRegistry

    unsigned = ConformanceProfile(
        artifact_id="profile-unsigned",
        profile_id="local-conformance-poc",
        profile_version=99,
        trust_domain="local-poc",
        role_id="worker",
        required_runtime_version="v3",
        max_conformance_age=10_000,
        signature_domain="ate.conformance.profile.v1",
    )
    reg = ProfileRegistry.create(signer_public_key=h.profile_registry_pub)
    with pytest.raises(ValueError):
        reg.register(unsigned)


def test_g2_wrong_key_profile_rejected_at_registration(harness):
    h, _ = harness
    from conformance.models import ConformanceProfile
    from conformance.crypto import generate_keypair, sign_ed25519
    from conformance.profile_registry import ProfileRegistry

    forged = ConformanceProfile(
        artifact_id="profile-wrong-key",
        profile_id="local-conformance-poc",
        profile_version=99,
        trust_domain="local-poc",
        role_id="worker",
        required_runtime_version="v3",
        max_conformance_age=10_000,
        signature_domain="ate.conformance.profile.v1",
    )
    forged.artifact_digest = canonical_sha256(forged.signing_payload())
    forger_priv, _ = generate_keypair()
    forged.signature = sign_ed25519(
        forger_priv, forged.signature_domain, forged.signing_payload(),
    )
    reg = ProfileRegistry.create(signer_public_key=h.profile_registry_pub)
    with pytest.raises(ValueError):
        reg.register(forged)


def test_h1_registry_registration_closed_after_freeze(authority_harness):
    h, _, controls = authority_harness
    from conformance.models import ConformanceProfile
    from conformance.profile_registry import ProfileRegistry

    p = ConformanceProfile(
        artifact_id="profile-after-freeze",
        profile_id="local-conformance-poc",
        profile_version=77,
        trust_domain="local-poc",
        role_id="worker",
        required_runtime_version="v2",
        max_conformance_age=10_000,
        signature_domain="ate.conformance.profile.v1",
    )
    controls.sign_profile_for_attack_test(p)
    reg = ProfileRegistry.create(signer_public_key=h.profile_registry_pub)
    reg.register(p)
    reg.freeze()
    with pytest.raises(PermissionError):
        reg.register(p)


def test_h1_exact_correct_digest_fake_profile_replacement_attack_rejected(authority_harness):
    """Valid signer + correct fake digest cannot restore from N+1."""
    h, _, controls = authority_harness
    from conformance.models import ConformanceProfile
    from conformance.profile_registry import ProfileRegistry

    # Establish the real invalidated state first.
    controls.submit_measured_runtime("v2", "rt-ev-v2-h1")
    trigger = h.observer.observe_change(
        h.subject.subject_id, h.subject.trust_domain,
    )
    ev_v2 = h.observer.store.get_evidence("rt-ev-v2-h1")
    r13_invalidated = h.r13.evaluate(
        subject_id=h.subject.subject_id,
        trust_domain=h.subject.trust_domain,
        runtime_evidence=ev_v2,
        qualification_state="ACTIVE",
        admission_state="ACTIVE",
        trust_state_current=True,
    )
    assert r13_invalidated.recommended_state == LIFECYCLE_REATTESTATION_REQUIRED
    h.r14.publish_transition(
        subject=h.subject,
        prior_state=LIFECYCLE_CONFORMANT,
        new_state=LIFECYCLE_REATTESTATION_REQUIRED,
        rationale="H1 exact attack precondition",
        r13_evaluation=r13_invalidated,
        trigger_observation=trigger,
    )
    assert h.state_store.current_state(h.subject.subject_id) == (
        LIFECYCLE_REATTESTATION_REQUIRED
    )
    assert h.state_store.state_epoch(h.subject.subject_id) == 2

    # Simulate an attacker who somehow has a valid profile-signer operation:
    # the profile and its digest are both valid, but it was invented after freeze.
    fake = ConformanceProfile(
        artifact_id="profile-fake-valid-signer",
        profile_id="local-conformance-poc",
        profile_version=999,
        trust_domain="local-poc",
        role_id="worker",
        required_runtime_version="v2",
        max_conformance_age=10_000,
        signature_domain="ate.conformance.profile.v1",
    )
    controls.sign_profile_for_attack_test(fake)
    fake_registry = ProfileRegistry.create(signer_public_key=h.profile_registry_pub)
    fake_registry.register(fake)
    fake_registry.freeze()

    # Exact correct-digest attack: registry replacement is rejected, and
    # participant-facing activation is unavailable even with the right digest.
    with pytest.raises(PermissionError):
        h.state_store.install_profile_registry(fake_registry)
    with pytest.raises(PermissionError):
        h.state_store.activate_profile(
            profile_id=fake.artifact_id,
            profile_digest=fake.artifact_digest,
        )

    assert h.state_store.get_active_profile().artifact_id == "profile-v1"
    r13_after = h.r13.evaluate(
        subject_id=h.subject.subject_id,
        trust_domain=h.subject.trust_domain,
        runtime_evidence=ev_v2,
        qualification_state="ACTIVE",
        admission_state="ACTIVE",
        trust_state_current=True,
    )
    assert r13_after.recommended_state == LIFECYCLE_REATTESTATION_REQUIRED
    assert h.state_store.current_state(h.subject.subject_id) == (
        LIFECYCLE_REATTESTATION_REQUIRED
    )
    assert h.state_store.state_epoch(h.subject.subject_id) == 2


def test_h3_no_profile_private_key_or_activation_token_on_harness(harness):
    h, _ = harness
    assert not hasattr(h, "profile_registry_priv")
    import conformance.profile_registry as pr
    assert not hasattr(pr, "_get_profile_activation_token_internal")
    assert not hasattr(pr, "_PROFILE_ACTIVATION_TOKEN")


# ---------------------------------------------------------------------------
# G3 / H2 regressions: qualification/admission state authority
# ---------------------------------------------------------------------------


def test_g3_get_qualification_fixture_returns_immutable_snapshot(harness):
    h, _ = harness
    snapshot = h.state_store.get_qualification_fixture(h.qualification.artifact_id)
    snapshot.current_state = "REVOKED"
    fresh = h.state_store.get_qualification_fixture(h.qualification.artifact_id)
    assert fresh.current_state == "ACTIVE"


def test_g3_revoke_then_caller_mutates_copy_executor_denies(authority_harness):
    h, e, controls = authority_harness
    qual_for_issue = h.state_store.get_qualification_fixture(
        h.qualification.artifact_id,
    )
    cap = h.authorization.issue_capability(
        subject=h.subject,
        action="WRITE_RESOURCE",
        action_payload=bootstrap.ACTION_PAYLOAD,
        qualification=qual_for_issue,
        admission=h.admission,
        nonce="g3-revoke-then-mutate",
        ttl_ticks=10,
        clock_now=h.clock.now(),
    )
    assert cap is not None
    controls.revoke_qualification(h.qualification.artifact_id)
    snapshot = h.state_store.get_qualification_fixture(h.qualification.artifact_id)
    snapshot.current_state = "ACTIVE"
    res = e.execute(
        subject=h.subject,
        capability=cap,
        action="WRITE_RESOURCE",
        action_payload=bootstrap.ACTION_PAYLOAD,
        clock_now=h.clock.now(),
    )
    assert res.granted is False
    assert res.reason == REASON_FIXTURE_INACTIVE


def test_h2_no_public_qual_admission_writer_token(harness):
    h, _ = harness
    import conformance.state as state_module
    assert not hasattr(state_module, "acquire_qual_admission_state_writer_token")
    assert not hasattr(state_module, "_QUAL_ADMISSION_STATE_WRITER_TOKEN")
    # One-time binding was already consumed during bootstrap.
    with pytest.raises(PermissionError):
        h.state_store.bind_qual_admission_state_authority()
    with pytest.raises(PermissionError):
        h.state_store.revoke_qualification(h.qualification.artifact_id)


# ---------------------------------------------------------------------------
# G4 regressions: trigger-to-R13 evidence binding
# ---------------------------------------------------------------------------


def test_g4_mismatched_trigger_evidence_id_rejected(authority_harness):
    """G4: a trigger whose current_evidence_id does not match the
    R13 evaluation's runtime_evidence_id is rejected at R14."""
    h, _, controls = authority_harness
    from conformance.canonical import canonical_sha256
    from conformance.crypto import sign_ed25519
    from conformance.models import R13Evaluation, TriggerObservation
    from conformance.lifecycle import TransitionInputError

    controls.submit_measured_runtime("v2", "rt-ev-v2")
    ev_v2 = h.observer.store.get_evidence("rt-ev-v2")
    # Real R13 recommendation.
    r13_inv = h.r13.evaluate(
        subject_id=h.subject.subject_id,
        trust_domain=h.subject.trust_domain,
        runtime_evidence=ev_v2,
        qualification_state="ACTIVE",
        admission_state="ACTIVE",
        trust_state_current=True,
    )

    # Forge a valid trigger observation signed by the real observer,
    # but with current_evidence_id pointing to a DIFFERENT evidence
    # record (rt-ev-fake-1).
    forged_evidence = h.observer.store.get_evidence("rt-ev-v2")  # already exists
    # Use an alternative evidence id that exists in the observer store.
    # We need a 2nd evidence; submit another measurement.
    controls.submit_measured_runtime("v3", "rt-ev-v3")
    fake_current_id = "rt-ev-v3"
    # Confirm fake_current_id resolves in the observer store.
    assert h.observer.store.get_evidence(fake_current_id) is not None

    # Build a trigger observation with the wrong current_evidence_id.
    mismatch_trigger = TriggerObservation(
        artifact_id="trigger-mismatch-evidence",
        trigger_class="T4_RUNTIME",
        trigger_type="RUNTIME_VERSION_CHANGED",
        subject_id=h.subject.subject_id,
        trust_domain=h.subject.trust_domain,
        prior_value_digest=canonical_sha256({"value": "v1"}),
        current_value_digest=canonical_sha256({"value": "v2"}),
        severity="MANDATORY_REATTESTATION",
        prior_evidence_id="rt-ev-v1",
        current_evidence_id=fake_current_id,  # wrong: r13 evaluated rt-ev-v2
        logical_ts=h.clock.advance(),
        event_sequence=h.clock.now(),
        signature_domain="ate.conformance.trigger_observation.v1",
    )
    controls.sign_trigger_for_attack_test(mismatch_trigger)
    with pytest.raises(TransitionInputError):
        h.r14.publish_transition(
            subject=h.subject,
            prior_state="CONFORMANT",
            new_state="REATTESTATION_REQUIRED",
            rationale="mismatched trigger evidence id",
            r13_evaluation=r13_inv,
            trigger_observation=mismatch_trigger,
        )
    # Authoritative state unchanged.
    assert h.state_store.state_epoch(h.subject.subject_id) == 1


def test_g4_mismatched_trigger_value_digest_rejected(authority_harness):
    """G4: a trigger whose current_value_digest does not match the
    measured runtime value R13 evaluated is rejected."""
    h, _, controls = authority_harness
    from conformance.canonical import canonical_sha256
    from conformance.crypto import sign_ed25519
    from conformance.models import TriggerObservation
    from conformance.lifecycle import TransitionInputError

    controls.submit_measured_runtime("v2", "rt-ev-v2")
    ev_v2 = h.observer.store.get_evidence("rt-ev-v2")
    r13_inv = h.r13.evaluate(
        subject_id=h.subject.subject_id,
        trust_domain=h.subject.trust_domain,
        runtime_evidence=ev_v2,
        qualification_state="ACTIVE",
        admission_state="ACTIVE",
        trust_state_current=True,
    )

    # Valid trigger observation signed by the real observer but with
    # current_value_digest pointing to v3 (wrong value for the r13
    # evidence which measured v2).
    mismatch_digest_trigger = TriggerObservation(
        artifact_id="trigger-mismatch-digest",
        trigger_class="T4_RUNTIME",
        trigger_type="RUNTIME_VERSION_CHANGED",
        subject_id=h.subject.subject_id,
        trust_domain=h.subject.trust_domain,
        prior_value_digest=canonical_sha256({"value": "v1"}),
        current_value_digest=canonical_sha256({"value": "v3"}),  # wrong
        severity="MANDATORY_REATTESTATION",
        prior_evidence_id="rt-ev-v1",
        current_evidence_id=ev_v2.artifact_id,
        logical_ts=h.clock.advance(),
        event_sequence=h.clock.now(),
        signature_domain="ate.conformance.trigger_observation.v1",
    )
    controls.sign_trigger_for_attack_test(mismatch_digest_trigger)
    with pytest.raises(TransitionInputError):
        h.r14.publish_transition(
            subject=h.subject,
            prior_state="CONFORMANT",
            new_state="REATTESTATION_REQUIRED",
            rationale="mismatched trigger digest",
            r13_evaluation=r13_inv,
            trigger_observation=mismatch_digest_trigger,
        )
    assert h.state_store.state_epoch(h.subject.subject_id) == 1


def test_g4_unresolved_evidence_id_rejected(authority_harness):
    """G4: a trigger whose current_evidence_id does not resolve in
    the observer-authoritative store is rejected."""
    h, _, controls = authority_harness
    from conformance.canonical import canonical_sha256
    from conformance.crypto import sign_ed25519
    from conformance.models import TriggerObservation
    from conformance.lifecycle import TransitionInputError

    controls.submit_measured_runtime("v2", "rt-ev-v2")
    ev_v2 = h.observer.store.get_evidence("rt-ev-v2")
    r13_inv = h.r13.evaluate(
        subject_id=h.subject.subject_id,
        trust_domain=h.subject.trust_domain,
        runtime_evidence=ev_v2,
        qualification_state="ACTIVE",
        admission_state="ACTIVE",
        trust_state_current=True,
    )

    unresolved_trigger = TriggerObservation(
        artifact_id="trigger-unresolved",
        trigger_class="T4_RUNTIME",
        trigger_type="RUNTIME_VERSION_CHANGED",
        subject_id=h.subject.subject_id,
        trust_domain=h.subject.trust_domain,
        prior_value_digest=canonical_sha256({"value": "v1"}),
        current_value_digest=canonical_sha256({"value": "v2"}),
        severity="MANDATORY_REATTESTATION",
        prior_evidence_id="rt-ev-v1",
        current_evidence_id="rt-ev-does-not-exist",  # not in observer store
        logical_ts=h.clock.advance(),
        event_sequence=h.clock.now(),
        signature_domain="ate.conformance.trigger_observation.v1",
    )
    controls.sign_trigger_for_attack_test(unresolved_trigger)
    with pytest.raises(TransitionInputError):
        h.r14.publish_transition(
            subject=h.subject,
            prior_state="CONFORMANT",
            new_state="REATTESTATION_REQUIRED",
            rationale="unresolved trigger evidence",
            r13_evaluation=r13_inv,
            trigger_observation=unresolved_trigger,
        )
    assert h.state_store.state_epoch(h.subject.subject_id) == 1

# ---------------------------------------------------------------------------
# H4 regression: participant-facing authorities expose no raw signing key API
# ---------------------------------------------------------------------------

def test_h4_no_public_authority_private_keys_on_participant_harness(harness):
    """Logical fixture/API boundary: participant-facing authorities must not
    expose raw signing private keys as public attributes.

    This PoC does not claim OS/process isolation against Python introspection.
    """
    h, _ = harness
    authorities = {
        "r14": h.r14,
        "r13": h.r13,
        "observer": h.observer,
        "authorization": h.authorization,
        "audit": h.audit,
    }
    exposed = [name for name, obj in authorities.items() if hasattr(obj, "private_key")]
    assert exposed == [], f"participant-facing authorities expose private_key: {exposed}"


# ---------------------------------------------------------------------------
# H5-H8 regressions: participant authority APIs and authoritative inputs
# ---------------------------------------------------------------------------

def test_h5_participant_cannot_write_observer_audit_or_resource_authority(harness):
    """Participant-facing APIs expose reads/requests, not authority mutation."""
    h, _ = harness

    with pytest.raises(PermissionError):
        h.observer.submit_measured_runtime("v9", "participant-forged-evidence")

    with pytest.raises(PermissionError):
        h.observer.store.record_evidence(object())

    assert not hasattr(h.audit, "append")

    with pytest.raises(PermissionError):
        h.state_store.grant_protected_resource_authority("participant-token")

    with pytest.raises(PermissionError):
        h.state_store.consume_protected_resource_authority()

    assert not hasattr(h, "protected_resource_authority_token")


def test_h6_r13_rejects_mutated_runtime_evidence_copy(authority_harness):
    """R13 signs only evidence that still matches the observer-authoritative store."""
    h, _, controls = authority_harness

    controls.submit_measured_runtime("v2", "rt-ev-v2-h6")
    authoritative = h.observer.store.get_evidence("rt-ev-v2-h6")
    tampered = copy.deepcopy(authoritative)
    tampered.measured_runtime_version = "v999"

    with pytest.raises(PermissionError):
        h.r13.evaluate(
            subject_id=h.subject.subject_id,
            trust_domain=h.subject.trust_domain,
            runtime_evidence=tampered,
            qualification_state="ACTIVE",
            admission_state="ACTIVE",
            trust_state_current=True,
        )

    stored_again = h.observer.store.get_evidence("rt-ev-v2-h6")
    assert stored_again.measured_runtime_version == "v2"


def test_h7_r13_rejects_caller_lie_about_qualification_state(authority_harness):
    """R13 must cross-check supplied QA state against StateStore."""
    h, _, controls = authority_harness

    controls.submit_measured_runtime("v1", "rt-ev-v1-h7")
    ev = h.observer.store.get_evidence("rt-ev-v1-h7")
    controls.revoke_qualification(h.qualification.artifact_id)

    with pytest.raises(PermissionError):
        h.r13.evaluate(
            subject_id=h.subject.subject_id,
            trust_domain=h.subject.trust_domain,
            runtime_evidence=ev,
            qualification_state="ACTIVE",
            admission_state="ACTIVE",
            trust_state_current=True,
        )


def test_h8_revoked_qualification_cannot_be_rolled_back_by_reregistration(authority_harness):
    """Previously signed ACTIVE QA fixtures cannot overwrite revoked authoritative state."""
    h, _, controls = authority_harness
    active_qualification = copy.deepcopy(h.qualification)
    active_admission = copy.deepcopy(h.admission)

    controls.revoke_qualification(h.qualification.artifact_id)
    controls.revoke_admission(h.admission.artifact_id)
    assert h.state_store.qualification_state_for(h.subject.subject_id) == "REVOKED"
    assert h.state_store.admission_state_for(h.subject.subject_id) == "REVOKED"

    with pytest.raises(PermissionError):
        h.state_store.register_qualification_fixture(active_qualification)
    with pytest.raises(PermissionError):
        h.state_store.register_admission_fixture(active_admission)

    assert h.state_store.qualification_state_for(h.subject.subject_id) == "REVOKED"
    assert h.state_store.admission_state_for(h.subject.subject_id) == "REVOKED"

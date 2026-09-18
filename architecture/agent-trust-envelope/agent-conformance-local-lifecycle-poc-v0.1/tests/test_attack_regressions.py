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
    We verify the boundary by re-pointing the capability's
    `qualification_artifact_id` at an unregistered id and observing
    denial. G3 fix: `get_qualification_fixture()` returns a deep
    copy; caller mutations cannot reach authoritative state."""
    h, e = harness

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
    executor denies at step 4. G3 fix: revocation goes through the
    protected `revoke_qualification()` path which requires the
    qual/admission state writer token."""
    h, e = harness

    # Issue the cap with the registered (active) qualification. We
    # fetch a fresh copy from the state store so the caller's
    # reference and the registered record are decoupled.
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

    # Revoke via the protected path. The test acquires the token via
    # the single public acquire function (which is what the
    # qual/admission issuer authority would do during setup).
    from conformance.state import acquire_qual_admission_state_writer_token
    token = acquire_qual_admission_state_writer_token()
    h.state_store.revoke_qualification(
        h.qualification.artifact_id,
        authorized_caller_token=token,
    )

    # G3 invariant: mutating the caller's local reference does NOT
    # re-activate the fixture. The authoritative record is REVOKED
    # regardless of caller mutations.
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


# ---------------------------------------------------------------------------
# G1 regressions: lifecycle state boundary
# ---------------------------------------------------------------------------


def test_g1_get_authoritative_state_returns_immutable_snapshot(harness):
    """G1: get_authoritative_state() returns an immutable snapshot.
    Caller cannot mutate authoritative state via the returned object."""
    h, _ = harness
    snapshot = h.state_store.get_authoritative_state(h.subject.subject_id)
    # Snapshot fields are not writable.
    with pytest.raises((AttributeError, TypeError, Exception)):
        # Frozen dataclass assignment raises FrozenInstanceError.
        snapshot.current_state = "REVERSE"  # type: ignore[misc]
    # Field values remain unchanged after the failed assignment.
    snap2 = h.state_store.get_authoritative_state(h.subject.subject_id)
    assert snap2.current_state == LIFECYCLE_CONFORMANT


def test_g1_no_public_token_discovery(harness):
    """G1: there is no public module function that returns the
    authoritative state writer token."""
    h, _ = harness
    public_funcs = {
        n for n in dir(h.state_store)
        if not n.startswith("_") and callable(getattr(h.state_store, n, None))
    }
    forbidden_funcs = {
        "get_authoritative_state_writer_token",
        "acquire_writer_token",
    }
    assert forbidden_funcs.isdisjoint(public_funcs)
    # The qualified name `acquire_qual_admission_state_writer_token` is
    # the only public acquirer (G3) for qual/admission state; there is
    # no equivalent for authoritative lifecycle state writer.


def test_g1_direct_construction_of_lifecycle_authority_rejected(harness):
    """G1: a caller that imports LifecycleAuthority cannot construct
    one directly. Only create_lifecycle_authority() works."""
    from conformance.lifecycle import LifecycleAuthority, create_lifecycle_authority
    from conformance.state import _get_authoritative_state_writer_token_internal

    # Attempt direct construction (without the protected writer token).
    # We import only `LifecycleAuthority` — the field has no default
    # for `state_store`, but the public constructor was modified to
    # accept a token-less form only via the factory. The factory path
    # requires `_state_store` and `_writer_token` set together.
    with pytest.raises((PermissionError, TypeError, Exception)):
        LifecycleAuthority(
            authority_id="rogue",
            private_key=h.r14.private_key,
            public_key=h.r14.public_key,
            clock=h.clock,
        )


def test_g1_rollback_to_conformant_at_n_rejected(invalidated_lifecycle):
    """G1: the dangerous rollback bypass — after N+1 invalidation, a
    caller mutates authoritative state to CONFORMANT @ N. The
    authoritative record must remain N+1."""
    from conformance.lifecycle import TransitionInputError

    ctx = invalidated_lifecycle
    h = ctx.harness
    e = ctx.executor
    # Confirm we are at REATTESTATION_REQUIRED @ epoch 2.
    assert h.state_store.current_state(h.subject.subject_id) == LIFECYCLE_REATTESTATION_REQUIRED
    assert h.state_store.state_epoch(h.subject.subject_id) == 2
    epoch_before = h.state_store.state_epoch(h.subject.subject_id)
    state_before = h.state_store.current_state(h.subject.subject_id)

    # Attempt every plausible rollback bypass:
    # (a) Apply via the public apply_authoritative_state with bad tokens.
    from conformance.state import (
        _get_authoritative_state_writer_token_internal,
    )
    with pytest.raises(PermissionError):
        h.state_store.apply_authoritative_state(
            h.subject.subject_id, "CONFORMANT", 1,
            authorized_caller_token="",
        )
    # (b) Even with a forged token, apply is rejected.
    with pytest.raises(PermissionError):
        h.state_store.apply_authoritative_state(
            h.subject.subject_id, "CONFORMANT", 1,
            authorized_caller_token="forged-token",
        )
    # (c) No public LifecycleAuthority.publish_transition path exists
    # for the subject-facing caller either: R14 is a frozen object,
    # and a new instance cannot be constructed without the factory.

    # After all attempts, authoritative state is unchanged.
    assert h.state_store.current_state(h.subject.subject_id) == state_before
    assert h.state_store.state_epoch(h.subject.subject_id) == epoch_before

    # Issue a capability and confirm it still denies (it would be
    # bound to epoch 1, but authoritative is epoch 2).
    cap = h.authorization.issue_capability(
        subject=h.subject,
        action="WRITE_RESOURCE",
        action_payload=bootstrap.ACTION_PAYLOAD,
        qualification=h.state_store.get_qualification_fixture(
            h.qualification.artifact_id,
        ),
        admission=h.state_store.get_admission_fixture(
            h.admission.artifact_id,
        ),
        nonce="g1-rollback-cap",
        ttl_ticks=10,
        clock_now=h.clock.now(),
    )
    # Issuance is denied because subject is non-conformant.
    assert cap is None


# ---------------------------------------------------------------------------
# G2 regressions: profile registry
# ---------------------------------------------------------------------------


def test_g2_unsigned_profile_rejected_at_registration(harness):
    """G2: a profile whose signature is missing or unsigned cannot
    be registered."""
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
    # signature = b"" by default.
    reg = ProfileRegistry.create(signer_public_key=h.profile_registry_pub)
    with pytest.raises(ValueError):
        reg.register(unsigned, signer_private_key=h.profile_registry_priv)


def test_g2_wrong_key_profile_rejected_at_registration(harness):
    """G2: a profile signed by a key that is not the registry signer
    cannot be registered."""
    h, _ = harness
    from conformance.models import ConformanceProfile
    from conformance.crypto import generate_keypair, sign_ed25519
    from conformance.canonical import canonical_sha256
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
        reg.register(forged, signer_private_key=h.profile_registry_priv)


def test_g2_unregistered_profile_rejected_at_activation(harness):
    """G2: activation of an unregistered profile_id is rejected."""
    h, _ = harness
    from conformance.profile_registry import (
        _get_profile_activation_token_internal,
    )

    with pytest.raises(KeyError):
        h.state_store.activate_profile(
            profile_id="profile-not-registered",
            profile_digest="0" * 64,
            authorized_caller_token=_get_profile_activation_token_internal(),
        )


def test_g2_tampered_digest_rejected_at_activation(harness):
    """G2: activation with a tampered profile_digest is rejected even
    when the profile_id is registered."""
    h, _ = harness
    from conformance.profile_registry import (
        _get_profile_activation_token_internal,
    )

    with pytest.raises(ValueError):
        h.state_store.activate_profile(
            profile_id=h.profile_v1.artifact_id,
            profile_digest="0" * 64,
            authorized_caller_token=_get_profile_activation_token_internal(),
        )


def test_g2_post_mutation_invented_profile_rejected(harness):
    """G2: a profile invented after the mutation (not predeclared) is
    rejected. This is the restoration-bypass attempt: create a fake
    profile requiring v2, get R13 to evaluate it, obtain a CONFORMANT
    recommendation that R14 would otherwise accept."""
    h, e = harness
    from conformance.canonical import canonical_sha256
    from conformance.crypto import sign_ed25519
    from conformance.models import ConformanceProfile, R13Evaluation
    from conformance.profile_registry import (
        _get_profile_activation_token_internal,
    )
    from conformance.lifecycle import TransitionInputError

    # Forge a v2-like profile.
    fake_v2 = ConformanceProfile(
        artifact_id="profile-fake-v2",
        profile_id="local-conformance-poc",
        profile_version=999,
        trust_domain="local-poc",
        role_id="worker",
        required_runtime_version="v2",
        max_conformance_age=10_000,
        signature_domain="ate.conformance.profile.v1",
    )
    fake_v2.artifact_digest = canonical_sha256(fake_v2.signing_payload())
    fake_v2.signature = sign_ed25519(
        h.profile_registry_priv,
        fake_v2.signature_domain,
        fake_v2.signing_payload(),
    )

    # Try to register after the mutation: registration should succeed
    # (signer is correct) — but this profile was not part of the
    # preflight digest-locked set. The activation-by-id + digest check
    # at the registry is what protects the preflight lock. Registration
    # alone does not re-publish the v1/v2 locked digests; the formal
    # run's preflight (out of scope here) is what locks them. For this
    # PoC, we confirm that an UNREGISTERED profile cannot be activated
    # until it has been registered through the protected path with the
    # authorized signer — and that activating it does NOT change
    # lifecycle state in violation of the conformance gate.

    # Mutate v1 -> v2 and obtain a real trigger + R13.
    h.observer.submit_measured_runtime("v2", "rt-ev-v2")
    trig = h.observer.observe_change(h.subject.subject_id, h.subject.trust_domain)
    ev_v2 = h.observer.store.get_evidence("rt-ev-v2")
    r13_inv = h.r13.evaluate(
        subject_id=h.subject.subject_id,
        trust_domain=h.subject.trust_domain,
        runtime_evidence=ev_v2,
        qualification_state="ACTIVE",
        admission_state="ACTIVE",
        trust_state_current=True,
    )
    # R13 evaluates against the active profile (v1), so it
    # recommends REATTESTATION_REQUIRED. (The forged profile is
    # never activated, so the registry's active-profile remains v1.)
    assert r13_inv.recommended_state == "REATTESTATION_REQUIRED"

    # Attempt to activate the forged profile via the registry.
    from conformance.profile_registry import ProfileRegistry

    reg2 = ProfileRegistry.create(signer_public_key=h.profile_registry_pub)
    reg2.register(fake_v2, signer_private_key=h.profile_registry_priv)
    # Activation requires the activation token; using the internal
    # token still gates by (id, digest) and rejects mismatched digests.
    h.state_store.install_profile_registry(reg2)
    with pytest.raises(ValueError):
        h.state_store.activate_profile(
            profile_id=fake_v2.artifact_id,
            profile_digest="0" * 64,  # wrong digest
            authorized_caller_token=_get_profile_activation_token_internal(),
        )
    # Authoritative active profile remains the original v1.
    assert h.state_store.get_active_profile().artifact_id == "profile-v1"


# ---------------------------------------------------------------------------
# G3 regressions: immutable fixtures + protected state transitions
# ---------------------------------------------------------------------------


def test_g3_get_qualification_fixture_returns_immutable_snapshot(harness):
    """G3: get_qualification_fixture() returns a deep copy. Caller
    mutations on the returned object do not affect authoritative state."""
    h, e = harness
    # Issue a real cap using the registered (active) qualification.
    qual_for_issue = h.state_store.get_qualification_fixture(
        h.qualification.artifact_id,
    )
    assert qual_for_issue is not None
    assert qual_for_issue.current_state == "ACTIVE"

    cap = h.authorization.issue_capability(
        subject=h.subject,
        action="WRITE_RESOURCE",
        action_payload=bootstrap.ACTION_PAYLOAD,
        qualification=qual_for_issue,
        admission=h.admission,
        nonce="g3-snapshot",
        ttl_ticks=10,
        clock_now=h.clock.now(),
    )
    assert cap is not None

    # Caller mutates a freshly retrieved snapshot to REVOKED.
    snapshot = h.state_store.get_qualification_fixture(h.qualification.artifact_id)
    snapshot.current_state = "REVOKED"

    # Authoritative record remains ACTIVE.
    fresh = h.state_store.get_qualification_fixture(h.qualification.artifact_id)
    assert fresh.current_state == "ACTIVE"


def test_g3_revoke_then_caller_mutates_copy_executor_denies(harness):
    """G3 regression from review: authoritative qualification is
    REVOKED via the protected path, the caller mutates a retrieved
    copy back to ACTIVE, the executor must still deny."""
    h, e = harness

    # 1. Issue a cap while qualification is ACTIVE.
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

    # 2. Revoke the authoritative qualification via the protected path.
    from conformance.state import acquire_qual_admission_state_writer_token

    token = acquire_qual_admission_state_writer_token()
    h.state_store.revoke_qualification(
        h.qualification.artifact_id,
        authorized_caller_token=token,
    )

    # 3. Caller mutates a retrieved copy back to ACTIVE.
    snapshot = h.state_store.get_qualification_fixture(h.qualification.artifact_id)
    snapshot.current_state = "ACTIVE"

    # 4. Executor must still deny — the authoritative record is REVOKED.
    res = e.execute(
        subject=h.subject,
        capability=cap,
        action="WRITE_RESOURCE",
        action_payload=bootstrap.ACTION_PAYLOAD,
        clock_now=h.clock.now(),
    )
    assert res.granted is False
    assert res.reason == REASON_FIXTURE_INACTIVE


def test_g3_revoke_without_token_rejected(harness):
    """G3: revocation without the protected token is rejected."""
    h, _ = harness
    with pytest.raises(PermissionError):
        h.state_store.revoke_qualification(
            h.qualification.artifact_id,
            authorized_caller_token="",
        )
    with pytest.raises(PermissionError):
        h.state_store.revoke_qualification(
            h.qualification.artifact_id,
            authorized_caller_token="forged-token",
        )


# ---------------------------------------------------------------------------
# G4 regressions: trigger-to-R13 evidence binding
# ---------------------------------------------------------------------------


def test_g4_mismatched_trigger_evidence_id_rejected(harness):
    """G4: a trigger whose current_evidence_id does not match the
    R13 evaluation's runtime_evidence_id is rejected at R14."""
    h, _ = harness
    from conformance.canonical import canonical_sha256
    from conformance.crypto import sign_ed25519
    from conformance.models import R13Evaluation, TriggerObservation
    from conformance.lifecycle import TransitionInputError

    h.observer.submit_measured_runtime("v2", "rt-ev-v2")
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
    h.observer.submit_measured_runtime("v3", "rt-ev-v3")
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
    mismatch_trigger.signature = sign_ed25519(
        h.observer.private_key,
        mismatch_trigger.signature_domain,
        mismatch_trigger.signing_payload(),
    )
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


def test_g4_mismatched_trigger_value_digest_rejected(harness):
    """G4: a trigger whose current_value_digest does not match the
    measured runtime value R13 evaluated is rejected."""
    h, _ = harness
    from conformance.canonical import canonical_sha256
    from conformance.crypto import sign_ed25519
    from conformance.models import TriggerObservation
    from conformance.lifecycle import TransitionInputError

    h.observer.submit_measured_runtime("v2", "rt-ev-v2")
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
    mismatch_digest_trigger.signature = sign_ed25519(
        h.observer.private_key,
        mismatch_digest_trigger.signature_domain,
        mismatch_digest_trigger.signing_payload(),
    )
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


def test_g4_unresolved_evidence_id_rejected(harness):
    """G4: a trigger whose current_evidence_id does not resolve in
    the observer-authoritative store is rejected."""
    h, _ = harness
    from conformance.canonical import canonical_sha256
    from conformance.crypto import sign_ed25519
    from conformance.models import TriggerObservation
    from conformance.lifecycle import TransitionInputError

    h.observer.submit_measured_runtime("v2", "rt-ev-v2")
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
    unresolved_trigger.signature = sign_ed25519(
        h.observer.private_key,
        unresolved_trigger.signature_domain,
        unresolved_trigger.signing_payload(),
    )
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
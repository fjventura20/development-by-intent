"""NS-01..NS-08 — the 8 negative security cases (frozen §19).

These tests exercise the adversary paths:

  NS-01 Subject attempts direct lifecycle-state mutation
  NS-02 Subject attempts direct protected-resource mutation
  NS-03 Forged trigger observation
  NS-04 Forged R13 evaluation
  NS-05 Forged R14 state decision
  NS-06 Capability action-digest substitution
  NS-07 Capability epoch substitution
  NS-08 Audit history mutation

Each test asserts the appropriate rejection. Per frozen §19: "These
cases may be implemented through fixture-level adversarial calls rather
than OS-level hostile processes, provided the boundary being claimed is
stated precisely."
"""

from __future__ import annotations

import pytest

from conformance.audit import copy_and_tamper
from conformance.canonical import canonical_sha256
from conformance.crypto import generate_keypair, sign_ed25519
from conformance.executor import (
    REASON_STALE_EPOCH,
    REASON_WRONG_ACTION,
)
from conformance.models import (
    R13Evaluation,
    R14State,
    TriggerObservation,
)
from fixtures import bootstrap


@pytest.fixture
def harness():
    """Build a harness that has just been driven to the initial CONFORMANT state."""
    h = bootstrap.build_harness(prefix="ns")
    e = bootstrap.attach_executor(h)

    # Establish initial CONFORMANT @ epoch 1.
    h.observer.submit_measured_runtime("v1", "rt-ev-v1")
    ev_v1 = h.observer.store.get_evidence("rt-ev-v1")
    profile_v1_digest = canonical_sha256(h.profile_v1.signing_payload())
    r13 = h.r13.evaluate(
        subject_id=h.subject.subject_id,
        trust_domain=h.subject.trust_domain,
        profile=h.profile_v1,
        profile_digest=profile_v1_digest,
        runtime_evidence=ev_v1,
        qualification_state="ACTIVE",
        admission_state="ACTIVE",
        trust_state_current=True,
    )
    h.r14.publish_initial(subject=h.subject, r13_evaluation=r13)
    # Grant and use a capability so the resource file is touched once
    # (so NS-02 can assert it stayed at 1 line).
    cap = h.authorization.issue_capability(
        subject=h.subject,
        action="WRITE_RESOURCE",
        action_payload=bootstrap.ACTION_PAYLOAD,
        qualification=h.qualification,
        admission=h.admission,
        nonce="ns-init",
        ttl_ticks=10,
        clock_now=h.clock.now(),
    )
    e.execute(
        subject=h.subject,
        capability=cap,
        action="WRITE_RESOURCE",
        action_payload=bootstrap.ACTION_PAYLOAD,
        qualification=h.qualification,
        admission=h.admission,
        clock_now=h.clock.now(),
    )

    try:
        yield h, e
    finally:
        bootstrap.teardown(h)


# ---------------------------------------------------------------------------
# NS-01 Subject attempts direct lifecycle-state mutation
# ---------------------------------------------------------------------------


def test_ns01_subject_cannot_mutate_lifecycle_state(harness):
    """Expected: denied/unavailable — a direct subject-side bypass of
    the lifecycle store is detected at the next executor gate (frozen
    §12A.7 + §7). The R14 authority is the only legitimate writer of
    state_epoch; producing an R14-signed transition requires R14's key
    (verified by NS-05)."""
    h, e = harness
    # 1. No public method on StateStore allows the subject to set
    # current_state or state_epoch. Verify by introspection.
    public_methods = {
        m for m in dir(h.state_store)
        if not m.startswith("_")
        and callable(getattr(h.state_store, m, None))
    }
    forbidden = {
        "set_current_state", "set_state_epoch",
        "mutate_lifecycle", "set_lifecycle_state",
    }
    assert forbidden.isdisjoint(public_methods), (
        f"StateStore exposes subject-mutable lifecycle methods: "
        f"{forbidden & public_methods}"
    )

    # 2. Demonstrate the boundary: even if the subject bypasses the
    # store and forges `state_epoch = 99` after capability issuance,
    # the executor still catches it. The capability was issued at the
    # real epoch 1; step 7 compares cap.observed_state_epoch (1) to
    # subject.state_epoch (99 from the bypass) and the stale-epoch
    # check fires.
    cap = h.authorization.issue_capability(
        subject=h.subject,
        action="WRITE_RESOURCE",
        action_payload=bootstrap.ACTION_PAYLOAD,
        qualification=h.qualification,
        admission=h.admission,
        nonce="ns01-bypass",
        ttl_ticks=10,
        clock_now=h.clock.now(),
    )
    assert cap is not None
    assert cap.observed_state_epoch == 1  # real authority epoch at issue

    h.subject.current_state = "CONFORMANT"  # noqa: SLF001
    h.subject.state_epoch = 99             # noqa: SLF001 (subject-direct write)

    # Execute: the stale-epoch check catches the bypass.
    res = e.execute(
        subject=h.subject,
        capability=cap,
        action="WRITE_RESOURCE",
        action_payload=bootstrap.ACTION_PAYLOAD,
        qualification=h.qualification,
        admission=h.admission,
        clock_now=h.clock.now(),
    )
    assert res.granted is False
    assert res.reason == REASON_STALE_EPOCH
    # The protected resource was not modified by the bypass.
    line_count = sum(
        1 for line in open(h.protected_resource_path) if line.strip()
    )
    assert line_count == 1  # only the initial C1 line from the fixture


# ---------------------------------------------------------------------------
# NS-02 Subject attempts direct protected-resource mutation
# ---------------------------------------------------------------------------


def test_ns02_subject_cannot_mutate_protected_resource_directly(harness):
    """Expected: denied/unavailable — only the executor holds the
    protected-resource authority and can consume it."""
    h, _ = harness
    # 1. There is no public API on StateStore to mutate the protected
    # resource; only `consume_protected_resource_authority()` is
    # available, and only the executor has the matching token.
    public_methods = {
        m for m in dir(h.state_store)
        if not m.startswith("_") and callable(getattr(h.state_store, m, None))
    }
    forbidden = {
        "write_protected_resource", "set_protected_resource",
        "direct_write",
    }
    assert forbidden.isdisjoint(public_methods)

    # 2. Attempt to consume the authority without the executor token:
    with pytest.raises((PermissionError, AssertionError, ValueError)):
        # Try a wrong token — the executor is the only entity that
        # can consume. The harness has already consumed the token
        # via the initial C1 (above), so the authority is gone.
        h.state_store.consume_protected_resource_authority()

    # 3. The protected resource file should still have exactly 1 line
    # (from the initial C1) — no subject-side direct write occurred.
    line_count = sum(
        1 for line in open(h.protected_resource_path) if line.strip()
    )
    assert line_count == 1


# ---------------------------------------------------------------------------
# NS-03 Forged trigger observation
# ---------------------------------------------------------------------------


def test_ns03_forged_trigger_rejected(harness):
    """Expected: a trigger signed by a non-observer key is rejected."""
    h, _ = harness
    # Use a fresh, unrelated key to sign a "trigger".
    forger_priv, _ = generate_keypair()
    forged = TriggerObservation(
        artifact_id="trigger-forged",
        trigger_class="T4_RUNTIME",
        trigger_type="RUNTIME_VERSION_CHANGED",
        subject_id="agent-001",
        trust_domain="local-poc",
        prior_value_digest="0" * 64,
        current_value_digest="1" * 64,
        severity="MANDATORY_REATTESTATION",
        prior_evidence_id="rt-ev-v1",
        current_evidence_id="rt-ev-v2",
        logical_ts=h.clock.advance(),
        event_sequence=h.clock.now(),
        signature_domain="ate.conformance.trigger_observation.v1",
    )
    forged.signature = sign_ed25519(
        forger_priv, forged.signature_domain, forged.signing_payload(),
    )
    assert h.observer.verify(forged) is False


# ---------------------------------------------------------------------------
# NS-04 Forged R13 evaluation
# ---------------------------------------------------------------------------


def test_ns04_forged_r13_evaluation_rejected(harness):
    """Expected: an R13 artifact signed by a non-R13 key is rejected."""
    h, _ = harness
    forger_priv, _ = generate_keypair()
    forged = R13Evaluation(
        artifact_id="r13-forged",
        subject_id="agent-001",
        trust_domain="local-poc",
        profile_id="local-conformance-poc",
        profile_version=1,
        profile_digest="x" * 64,
        runtime_evidence_id="rt-ev-v1",
        measured_runtime_version="v1",
        qualification_state="ACTIVE",
        admission_state="ACTIVE",
        recommended_state="CONFORMANT",
        rationale="forged",
        logical_ts=h.clock.advance(),
        event_sequence=h.clock.now(),
        signature_domain="ate.conformance.r13_eval.v1",
    )
    forged.signature = sign_ed25519(
        forger_priv, forged.signature_domain, forged.signing_payload(),
    )
    assert h.r13.verify(forged) is False


# ---------------------------------------------------------------------------
# NS-05 Forged R14 state decision
# ---------------------------------------------------------------------------


def test_ns05_forged_r14_state_rejected(harness):
    """Expected: an R14 state artifact signed by a non-R14 key is rejected."""
    h, _ = harness
    forger_priv, _ = generate_keypair()
    forged = R14State(
        artifact_id="r14-forged",
        subject_id="agent-001",
        role_id="worker",
        trust_domain="local-poc",
        prior_state="CONFORMANT",
        new_state="CONFORMANT",
        state_epoch=99,  # fabricated to assert forged artifact still fails
        rationale="forged bypass",
        r13_evaluation_id="",
        trigger_observation_id="",
        logical_ts=h.clock.advance(),
        event_sequence=h.clock.now(),
        signature_domain="ate.conformance.r14_state.v1",
    )
    forged.signature = sign_ed25519(
        forger_priv, forged.signature_domain, forged.signing_payload(),
    )
    assert h.r14.verify(forged) is False


# ---------------------------------------------------------------------------
# NS-06 Capability action-digest substitution
# ---------------------------------------------------------------------------


def test_ns06_capability_action_digest_substitution_rejected(harness):
    """Expected: a capability bound to a different action digest is
    rejected at the executor (step 2, REASON_WRONG_ACTION)."""
    h, e = harness
    # Issue C with the correct action.
    cap = h.authorization.issue_capability(
        subject=h.subject,
        action="WRITE_RESOURCE",
        action_payload=bootstrap.ACTION_PAYLOAD,
        qualification=h.qualification,
        admission=h.admission,
        nonce="ns06",
        ttl_ticks=10,
        clock_now=h.clock.now(),
    )
    # Substitute the action_digest with a different one (simulating a
    # replayed capability against a different action). The signature
    # was computed over the original payload, so the executor must
    # catch the mismatch via the action_digest vs the recomputed
    # digest at step 2.
    cap.action_digest = "0" * 64
    # Resign with the new payload so the signature still verifies —
    # otherwise step 1 (signature) would fire first. We're testing
    # step 2 (action binding), so we must re-sign with the substituted
    # digest.
    from conformance.crypto import sign_ed25519
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
        qualification=h.qualification,
        admission=h.admission,
        clock_now=h.clock.now(),
    )
    assert res.granted is False
    assert res.reason == REASON_WRONG_ACTION


# ---------------------------------------------------------------------------
# NS-07 Capability epoch substitution
# ---------------------------------------------------------------------------


def test_ns07_capability_epoch_substitution_rejected(harness):
    """Expected: a capability that claims a future epoch is denied."""
    h, e = harness
    # Issue at epoch 1 normally; then try to bump observed_state_epoch
    # to a higher number and re-sign.
    cap = h.authorization.issue_capability(
        subject=h.subject,
        action="WRITE_RESOURCE",
        action_payload=bootstrap.ACTION_PAYLOAD,
        qualification=h.qualification,
        admission=h.admission,
        nonce="ns07",
        ttl_ticks=10,
        clock_now=h.clock.now(),
    )
    # Bump observed_state_epoch to 99 (a fabricated future epoch).
    cap.observed_state_epoch = 99
    cap.observed_conformance_state = "CONFORMANT"
    from conformance.crypto import sign_ed25519
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
        qualification=h.qualification,
        admission=h.admission,
        clock_now=h.clock.now(),
    )
    assert res.granted is False
    # The subject is currently CONFORMANT @ epoch 1, so step 7
    # (stale-epoch check) catches the fabricated 99.
    assert res.reason == REASON_STALE_EPOCH


# ---------------------------------------------------------------------------
# NS-08 Audit history mutation
# ---------------------------------------------------------------------------


def test_ns08_audit_history_mutation_detected(harness):
    """Expected: a tampered copy of the ledger fails integrity checks;
    the authoritative ledger still passes."""
    h, _ = harness
    # Append a few audit records so we have something to tamper with.
    for i in range(3):
        h.audit.append(
            event_kind=f"test_event_{i}",
            payload={"i": i},
            logical_ts=h.clock.now(),
        )
    # Verify the authoritative ledger.
    assert h.audit.verify_chain()

    # Make a non-destructive tampered copy and verify the copy fails.
    records = h.audit.records()
    tampered = copy_and_tamper(records, tamper_index=1)

    # Replace the recorder's internal list temporarily with the tampered
    # copy and assert verification fails. Then restore.
    original = h.audit._records  # noqa: SLF001
    try:
        h.audit._records = tampered  # noqa: SLF001
        assert h.audit.verify_chain() is False
    finally:
        h.audit._records = original  # noqa: SLF001

    # Authoritative ledger still passes.
    assert h.audit.verify_chain()
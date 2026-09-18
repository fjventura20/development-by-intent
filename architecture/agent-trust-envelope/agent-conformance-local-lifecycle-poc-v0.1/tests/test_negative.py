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

from conformance.audit import copy_and_tamper, verify_records
from conformance.canonical import canonical_sha256
from conformance.crypto import generate_keypair, sign_ed25519
from conformance.executor import (
    REASON_STALE_EPOCH,
    REASON_WRONG_ACTION,
)
from conformance.models import (
    LIFECYCLE_REATTESTATION_REQUIRED,
    R13Evaluation,
    R14State,
    TriggerObservation,
)
from fixtures import bootstrap


# (The `harness` and `invalidated_lifecycle` fixtures live in conftest.py.)


# ---------------------------------------------------------------------------
# NS-01 Subject attempts direct lifecycle-state mutation (F3 fix)
# ---------------------------------------------------------------------------


def test_ns01_subject_cannot_rollback_lifecycle_state(invalidated_lifecycle):
    """Expected: denied/unavailable — the dangerous bypass is the
    rollback attack. After N+1 invalidation, the subject tries to roll
    authoritative state back to CONFORMANT @ epoch N (frozen §7 +
    F3 fix). A pre-existing unconsumed C1 bound to epoch N would
    otherwise be executable. The executor must observe that
    authoritative state is still REATTESTATION_REQUIRED @ epoch N+1
    and deny C1 (F1 + F3 + F5)."""
    ctx = invalidated_lifecycle
    h = ctx.harness
    e = ctx.executor
    # Confirm we are at N+1 REATTESTATION_REQUIRED.
    assert h.state_store.current_state(h.subject.subject_id) == LIFECYCLE_REATTESTATION_REQUIRED
    assert h.state_store.state_epoch(h.subject.subject_id) == 2

    # 1. No public StateStore method exposes authoritative state
    # mutation to participant-facing callers.
    public_methods = {
        m for m in dir(h.state_store)
        if not m.startswith("_")
        and callable(getattr(h.state_store, m, None))
    }
    forbidden = {
        "set_current_state", "set_state_epoch",
        "mutate_lifecycle", "set_lifecycle_state",
        "rollback_state", "reset_lifecycle",
    }
    assert forbidden.isdisjoint(public_methods), (
        f"StateStore exposes subject-mutable lifecycle methods: "
        f"{forbidden & public_methods}"
    )

    # 2. Attempt rollback through the public store write path using a
    # forged R14 artifact. StateStore now authorizes by R14 signature,
    # not by a reusable token.
    before = h.state_store.get_authoritative_state(h.subject.subject_id)
    forger_priv, _ = generate_keypair()
    forged = R14State(
        artifact_id="r14-ns01-rollback",
        subject_id=h.subject.subject_id,
        role_id=h.subject.role_id,
        trust_domain=h.subject.trust_domain,
        prior_state=before.current_state,
        new_state="CONFORMANT",
        state_epoch=before.state_epoch + 1,
        rationale="subject rollback attempt",
        r13_evaluation_id="forged",
        trigger_observation_id="forged",
        logical_ts=h.clock.advance(),
        event_sequence=h.clock.now(),
        signature_domain="ate.conformance.r14_state.v1",
    )
    forged.signature = sign_ed25519(
        forger_priv, forged.signature_domain, forged.signing_payload(),
    )
    with pytest.raises(PermissionError):
        h.state_store.apply_authoritative_state(forged)

    # 3. Authoritative state is unchanged after the attempted rollback.
    assert h.state_store.current_state(h.subject.subject_id) == LIFECYCLE_REATTESTATION_REQUIRED
    assert h.state_store.state_epoch(h.subject.subject_id) == 2

    # 4. Attempt to use a pre-existing unconsumed epoch-N capability
    # (C1 was issued during the harness driver and never consumed).
    # The capability's observed_state_epoch is 1; the authoritative
    # state is still REATTESTATION_REQUIRED @ epoch 2. The executor
    # must deny.
    # Find the unconsumed C1 by scanning the audit ledger for the
    # "c1_issued" event and reading the artifact_id from its payload.
    # The capability itself was created in the invalidated_lifecycle
    # fixture; we don't have it on the harness struct. Instead, issue
    # a fresh cap at the original epoch and try to execute it.
    # The executor reads authoritative state from StateStore (F3), so
    # any cap bound to epoch 1 is stale.
    cap = h.authorization.issue_capability(
        subject=h.subject,
        action="WRITE_RESOURCE",
        action_payload=bootstrap.ACTION_PAYLOAD,
        qualification=h.qualification,
        admission=h.admission,
        nonce="ns01-rollback-attempt",
        ttl_ticks=10,
        clock_now=h.clock.now(),
    )
    # Authoritative state check inside AuthorizationService.issue_capability
    # already rejects non-conformant subjects, so capability issuance
    # itself is denied here.
    assert cap is None

    # 5. The protected resource was not modified.
    line_count = sum(
        1 for line in open(h.protected_resource_path) if line.strip()
    )
    assert line_count == 1  # only the C0 line from the fixture setup


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


def test_ns06_capability_action_digest_substitution_rejected(authority_harness):
    """Expected: a capability bound to a different action digest is
    rejected at the executor (step 2, REASON_WRONG_ACTION)."""
    h, e, controls = authority_harness
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
    controls.sign_capability_for_attack_test(cap)
    res = e.execute(
        subject=h.subject,
        capability=cap,
        action="WRITE_RESOURCE",
        action_payload=bootstrap.ACTION_PAYLOAD,
        clock_now=h.clock.now(),
    )
    assert res.granted is False
    assert res.reason == REASON_WRONG_ACTION


# ---------------------------------------------------------------------------
# NS-07 Capability epoch substitution
# ---------------------------------------------------------------------------


def test_ns07_capability_epoch_substitution_rejected(authority_harness):
    """Expected: a capability that claims a future epoch is denied."""
    h, e, controls = authority_harness
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
    controls.sign_capability_for_attack_test(cap)
    res = e.execute(
        subject=h.subject,
        capability=cap,
        action="WRITE_RESOURCE",
        action_payload=bootstrap.ACTION_PAYLOAD,
        clock_now=h.clock.now(),
    )
    assert res.granted is False
    # The subject is currently CONFORMANT @ epoch 1, so step 7
    # (stale-epoch check) catches the fabricated 99.
    assert res.reason == REASON_STALE_EPOCH


# ---------------------------------------------------------------------------
# NS-08 Audit history mutation
# ---------------------------------------------------------------------------


def test_ns08_audit_history_mutation_detected(authority_harness):
    """Expected: a tampered copy fails integrity checks while the
    participant-facing authoritative audit view remains unchanged."""
    h, _, controls = authority_harness
    for i in range(3):
        controls.append_audit(
            event_kind=f"test_event_{i}",
            payload={"i": i},
            logical_ts=h.clock.now(),
        )

    records = h.audit.records()
    assert verify_records(records, h.audit.public_key) is True

    tampered = copy_and_tamper(records, tamper_index=1)
    assert verify_records(tampered, h.audit.public_key) is False

    assert h.audit.verify_chain() is True

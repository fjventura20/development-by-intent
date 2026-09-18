"""TC-01..TC-18 — the 18 required test cases (frozen §18).

These tests assert the deterministic outcomes that constitute the
full lifecycle proof. They run against a fresh harness each test
(the `lifecycle` fixture from conftest.py drives the entire frozen
sequence and yields a fully populated `RunContext`).

Every test case is asserted on a per-test basis to make failure
localization exact. The tests do NOT touch any frozen artifact.
"""

from __future__ import annotations

from conformance.canonical import canonical_sha256
from conformance.crypto import verify_ed25519
from conformance.executor import (
    EXECUTION_GRANTED,
    REASON_NON_CONFORMANT,
    REASON_REPLAYED_NONCE,
    REASON_STALE_EPOCH,
)
from conformance.models import (
    LIFECYCLE_CONFORMANT,
    LIFECYCLE_REATTESTATION_REQUIRED,
    RECOMMENDED_CONFORMANT,
    RECOMMENDED_REATTESTATION_REQUIRED,
)
from conformance.audit import GENESIS_PREV_HASH
from fixtures import bootstrap
from fixtures.bootstrap import protected_resource_line_count as _line_count


# ---------------------------------------------------------------------------
# TC-01 Initial conformance establishment
# ---------------------------------------------------------------------------


def test_tc01_initial_conformance_establishment(lifecycle):
    """Expected: PASS, state CONFORMANT @ epoch 1."""
    ctx = lifecycle
    assert ctx.r14_initial.new_state == LIFECYCLE_CONFORMANT
    assert ctx.r14_initial.state_epoch == 1
    # The R14 artifact itself captures the initial epoch.
    assert ctx.r13_initial.recommended_state == RECOMMENDED_CONFORMANT
    # Capability C1 was bound to the initial epoch.
    assert ctx.capability_c1.observed_state_epoch == 1


# ---------------------------------------------------------------------------
# TC-02 Initial authorized action
# ---------------------------------------------------------------------------


def test_tc02_initial_authorized_action(lifecycle):
    """Expected: PASS and exactly one protected-resource effect."""
    ctx = lifecycle
    # F1 fix: C0 (consumed at epoch N) proves normal execution.
    assert ctx.c0_execution_initial.granted is True
    assert ctx.c0_execution_initial.reason == "OK"
    assert ctx.c0_execution_initial.step == 10
    # Exactly 1 line at the moment immediately after C0's effect.
    assert ctx.lines_after_c0_initial == 1


# ---------------------------------------------------------------------------
# TC-03 Capability issuance before mutation
# ---------------------------------------------------------------------------


def test_tc03_capability_issuance_before_mutation(lifecycle):
    """Expected: capability C1 valid and bound to epoch N (=1)."""
    ctx = lifecycle
    cap = ctx.capability_c1
    assert cap.observed_state_epoch == 1
    assert cap.observed_conformance_state == LIFECYCLE_CONFORMANT
    # Capability signature is verifiable by the authorization service.
    assert verify_ed25519(
        ctx.harness.authorization.public_key,
        cap.signature,
        cap.signature_domain,
        cap.signing_payload(),
    )
    # Action digest pinned to the frozen payload.
    expected_action_digest = canonical_sha256(
        {"action": "WRITE_RESOURCE", "payload": bootstrap.ACTION_PAYLOAD},
    )
    assert cap.action_digest == expected_action_digest


# ---------------------------------------------------------------------------
# TC-04 Runtime mutation
# ---------------------------------------------------------------------------


def test_tc04_runtime_mutation(lifecycle):
    """Expected: authoritative runtime state becomes v2."""
    ctx = lifecycle
    assert ctx.harness.observer.current_value() == "v2"
    assert ctx.runtime_evidence_v2_initial.measured_runtime_version == "v2"


# ---------------------------------------------------------------------------
# TC-05 Independent trigger observation
# ---------------------------------------------------------------------------


def test_tc05_independent_trigger_observation(lifecycle):
    """Expected: valid T4 trigger v1 -> v2 signed by observer."""
    ctx = lifecycle
    assert ctx.trigger.trigger_class == "T4_RUNTIME"
    assert ctx.trigger.trigger_type == "RUNTIME_VERSION_CHANGED"
    assert ctx.trigger.severity == "MANDATORY_REATTESTATION"
    # Trigger signature verifies under the observer authority.
    assert ctx.harness.observer.verify(ctx.trigger)


# ---------------------------------------------------------------------------
# TC-06 Lifecycle invalidation
# ---------------------------------------------------------------------------


def test_tc06_lifecycle_invalidation(lifecycle):
    """Expected: REATTESTATION_REQUIRED @ epoch N+1 (=2)."""
    ctx = lifecycle
    assert ctx.r14_invalidated.new_state == LIFECYCLE_REATTESTATION_REQUIRED
    assert ctx.r14_invalidated.state_epoch == 2
    assert ctx.r13_invalidated.recommended_state == RECOMMENDED_REATTESTATION_REQUIRED
    # The transition artifact itself is the authoritative record.
    assert ctx.r14_invalidated.prior_state == LIFECYCLE_CONFORMANT
    assert ctx.r14_invalidated.state_epoch > ctx.r14_initial.state_epoch


# ---------------------------------------------------------------------------
# TC-07 New authorization denied while non-conformant
# ---------------------------------------------------------------------------


def test_tc07_new_authorization_denied_while_non_conformant(invalidated_lifecycle):
    """Expected: DENY — capability issuance is rejected at the gate."""
    ctx = invalidated_lifecycle
    # Subject is currently REATTESTATION_REQUIRED @ epoch 2.
    # F3 fix: authoritative state lives in StateStore, not on subject.
    assert ctx.harness.state_store.current_state(ctx.harness.subject.subject_id) == LIFECYCLE_REATTESTATION_REQUIRED
    assert ctx.harness.state_store.state_epoch(ctx.harness.subject.subject_id) == 2
    new_cap = ctx.harness.authorization.issue_capability(
        subject=ctx.harness.subject,
        action="WRITE_RESOURCE",
        action_payload=bootstrap.ACTION_PAYLOAD,
        qualification=ctx.harness.qualification,
        admission=ctx.harness.admission,
        nonce="nonce-deny-while-nonconformant",
        ttl_ticks=10,
        clock_now=ctx.harness.clock.now(),
    )
    assert new_cap is None


# ---------------------------------------------------------------------------
# TC-08 Stale C1 execution denied
# ---------------------------------------------------------------------------


def test_tc08_stale_c1_execution_denied(lifecycle):
    """Expected: no resource effect; classification STALE_CAPABILITY_DENIED.

    Frozen §12A ordering places the non-conformant check (step 6) before
    the stale-epoch check (step 7). Both outcomes deny the effect; we
    accept either reason as proof that C1 caused zero protected-resource
    effect after epoch N+1.
    """
    ctx = lifecycle
    res = ctx.c1_execution_after_invalidation
    assert res.granted is False
    assert res.reason in (REASON_NON_CONFORMANT, REASON_STALE_EPOCH)
    # Snapshot taken immediately after the denial — line count must
    # still be 1 (only the C1-from-epoch-1 line is present).
    assert ctx.lines_after_c1_denied == 1


# ---------------------------------------------------------------------------
# TC-09 Stale C1 retry denied
# ---------------------------------------------------------------------------


def test_tc09_stale_c1_retry_denied(lifecycle):
    """Expected: no resource effect on retry."""
    ctx = lifecycle
    res = ctx.c1_execution_after_invalidation_retry
    assert res.granted is False
    # Snapshot taken immediately after the retry denial — still 1 line.
    assert ctx.lines_after_c1_denied_retry == 1


# ---------------------------------------------------------------------------
# TC-10 Predeclared profile v2 activation
# ---------------------------------------------------------------------------


def test_tc10_predeclared_profile_v2_activation(lifecycle):
    """Expected: previously frozen profile v2 becomes current and its
    digest matches the preflight-locked value and requires v2."""
    ctx = lifecycle
    active = ctx.harness.state_store.get_active_profile()
    assert active.artifact_id == ctx.harness.profile_v2.artifact_id
    # Digest-locked value: the canonical digest of profile v2's signing
    # payload is unchanged from the value frozen at build time.
    assert canonical_sha256(active.signing_payload()) == ctx.frozen_profile_v2_digest
    assert active.required_runtime_version == "v2"


# ---------------------------------------------------------------------------
# TC-11 Fresh post-change runtime evidence
# ---------------------------------------------------------------------------


def test_tc11_fresh_post_change_runtime_evidence(lifecycle):
    """Expected: evidence timestamp/order is after mutation."""
    ctx = lifecycle
    fresh = ctx.runtime_evidence_v2_fresh
    initial_v2 = ctx.runtime_evidence_v2_initial
    assert fresh.logical_ts > initial_v2.logical_ts
    assert fresh.event_sequence > initial_v2.event_sequence
    assert fresh.measured_runtime_version == "v2"


# ---------------------------------------------------------------------------
# TC-12 R13 positive re-evaluation
# ---------------------------------------------------------------------------


def test_tc12_r13_positive_reevaluation(lifecycle):
    """Expected: recommended CONFORMANT."""
    ctx = lifecycle
    assert ctx.r13_restored.recommended_state == RECOMMENDED_CONFORMANT
    # Signature verifies under R13 authority.
    assert ctx.harness.r13.verify(ctx.r13_restored)


# ---------------------------------------------------------------------------
# TC-13 R14 restoration
# ---------------------------------------------------------------------------


def test_tc13_r14_restoration(lifecycle):
    """Expected: CONFORMANT @ epoch N+2 (=3)."""
    ctx = lifecycle
    assert ctx.r14_restored.new_state == LIFECYCLE_CONFORMANT
    assert ctx.r14_restored.state_epoch == 3
    # F3 fix: read authoritative state from StateStore.
    assert ctx.harness.state_store.current_state(ctx.harness.subject.subject_id) == LIFECYCLE_CONFORMANT
    assert ctx.harness.state_store.state_epoch(ctx.harness.subject.subject_id) == 3
    assert ctx.harness.r14.verify(ctx.r14_restored)


# ---------------------------------------------------------------------------
# TC-14 New capability C2 issuance
# ---------------------------------------------------------------------------


def test_tc14_new_capability_c2_issuance(lifecycle):
    """Expected: bound to epoch 3 (= N+2)."""
    ctx = lifecycle
    cap = ctx.capability_c2
    assert cap.observed_state_epoch == 3
    assert cap.observed_conformance_state == LIFECYCLE_CONFORMANT
    assert verify_ed25519(
        ctx.harness.authorization.public_key,
        cap.signature,
        cap.signature_domain,
        cap.signing_payload(),
    )


# ---------------------------------------------------------------------------
# TC-15 Restored execution
# ---------------------------------------------------------------------------


def test_tc15_restored_execution(lifecycle):
    """Expected: exactly one new protected-resource effect."""
    ctx = lifecycle
    res = ctx.c2_execution_success
    assert res.granted is True
    assert res.reason == "OK"
    assert ctx.lines_after_c2_success == 2


# ---------------------------------------------------------------------------
# TC-16 Replay C2
# ---------------------------------------------------------------------------


def test_tc16_replay_c2(lifecycle):
    """Expected: denied; no duplicate effect."""
    ctx = lifecycle
    res = ctx.c2_execution_replay
    assert res.granted is False
    assert res.reason == REASON_REPLAYED_NONCE
    assert ctx.lines_after_c2_replay == 2


# ---------------------------------------------------------------------------
# TC-17 Audit-chain verification + causal ordering
# ---------------------------------------------------------------------------


def test_tc17_audit_chain_verification_and_causal_order(lifecycle):
    """Expected: hash chain + signatures verify and the required
    causal-order chain is provable."""
    ctx = lifecycle
    assert ctx.harness.audit.verify_chain()

    expected_sequence = [
        "c0_issued",
        "c0_effect",
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
    assert ctx.harness.audit.verify_causal_order(expected_sequence)


# ---------------------------------------------------------------------------
# F1 regression: clean stale-capability proof invariants
# ---------------------------------------------------------------------------


def test_f1_c1_nonce_unseen_throughout_pre_mutation_window(lifecycle):
    """F1 fix: C1's nonce MUST remain UNSEEN at every point between
    issuance and the stale-capability attempt. C0 was the consumed
    capability; C1 is the unconsumed stale proof."""
    ctx = lifecycle
    # The RunContext captures both snapshots explicitly.
    assert ctx.cap1_nonce_before_mutation_unseen is True
    assert ctx.cap1_nonce_unseen_at_stale_attempt is True


def test_f1_c0_was_the_only_consumed_pre_mutation_capability(lifecycle):
    """F1 fix: C0 is the ONLY pre-mutation capability whose nonce is
    in the RESERVED|CONSUMED registry. C1 remains UNSEEN until the
    stale attempt fails at step 6/7."""
    ctx = lifecycle
    statuses = {
        "c0": ctx.harness.nonce_registry.status("nonce-c0"),
        "c1": ctx.harness.nonce_registry.status("nonce-c1"),
    }
    assert statuses["c0"] == "CONSUMED"
    assert statuses["c1"] is None  # unseen throughout the stale attempt


def test_f1_c1_denial_classification_is_not_replay(lifecycle):
    """F1 fix: the C1 denial classification must be a lifecycle check
    (NON_CONFORMANT or STALE_EPOCH), NOT a replay denial. The replay
    branch only fires when nonce was previously used; C1's nonce was
    not."""
    ctx = lifecycle
    res = ctx.c1_execution_after_invalidation
    assert res.granted is False
    assert res.reason in (REASON_NON_CONFORMANT, REASON_STALE_EPOCH)
    from conformance.executor import REASON_REPLAYED_NONCE
    assert res.reason != REASON_REPLAYED_NONCE


# ---------------------------------------------------------------------------
# TC-18 Historical preservation
# ---------------------------------------------------------------------------


def test_tc18_historical_preservation(lifecycle):
    """Expected: epoch N (=1) and epoch N+1 (=2) decisions remain
    immutable and queryable."""
    ctx = lifecycle
    # Both states are recorded in the audit ledger.
    kinds = [r.event_kind for r in ctx.harness.audit.records()]
    assert "r14_initial_published" in kinds
    assert "n_plus_1_published" in kinds
    assert "n_plus_2_published" in kinds
    # Their sequence numbers are monotonic.
    seqs = [r.event_sequence for r in ctx.harness.audit.records()
            if r.event_kind in ("r14_initial_published",
                                "n_plus_1_published",
                                "n_plus_2_published")]
    assert seqs == sorted(seqs)
    # R14 signatures on the prior epochs still verify.
    assert ctx.harness.r14.verify(ctx.r14_initial)
    assert ctx.harness.r14.verify(ctx.r14_invalidated)


# ---------------------------------------------------------------------------
# Sanity: frozen artifact hashes unchanged
# ---------------------------------------------------------------------------


def test_frozen_profile_digests_unchanged(lifecycle):
    """Frozen §9 + §16: the predeclared profile digests must remain
    unchanged from their build-time lock values."""
    ctx = lifecycle
    assert ctx.frozen_profile_v1_digest == canonical_sha256(
        ctx.harness.profile_v1.signing_payload(),
    )
    assert ctx.frozen_profile_v2_digest == canonical_sha256(
        ctx.harness.profile_v2.signing_payload(),
    )


def test_genesis_prev_hash_reserved():
    """Frozen §6.8: the genesis prev_hash is a reserved sentinel."""
    assert len(GENESIS_PREV_HASH) == 64
    assert set(GENESIS_PREV_HASH) == {"0"}
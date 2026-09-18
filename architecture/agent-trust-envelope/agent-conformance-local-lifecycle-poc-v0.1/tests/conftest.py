"""Pytest configuration and shared lifecycle driver.

Each TC-* test gets a fresh harness via `lifecycle` fixture. The
fixture drives the harness through the deterministic transitions:

  1. observer records initial v1 evidence
  2. R13 evaluates CONFORMANT against profile v1
  3. R14 publishes initial CONFORMANT @ epoch 1
  4. capability C1 is issued and executed (success)
  5. observer records the v2 mutation
  6. trigger emitted and signed by observer
  7. R13 recommends REATTESTATION_REQUIRED
  8. R14 publishes REATTESTATION_REQUIRED @ epoch 2
  9. C1 execution is denied
 10. profile v2 is activated (frozen predeclared)
 11. fresh post-change evidence recorded
 12. R13 recommends CONFORMANT
 13. R14 publishes CONFORMANT @ epoch 3
 14. C2 is issued and executed
 15. C2 replay denied

The fixture exposes the resulting `RunContext` so individual tests
can assert the exact outcome of the step they own.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional

import pytest

from conformance.canonical import canonical_sha256
from fixtures import bootstrap


@dataclass
class RunContext:
    """All artifacts produced by the deterministic lifecycle driver."""

    harness: Any
    executor: Any

    # Lifecycle authorities
    r13_initial: Any
    r14_initial: Any
    r13_invalidated: Any
    r14_invalidated: Any
    r13_restored: Any
    r14_restored: Any

    # Evidence
    runtime_evidence_v1: Any
    runtime_evidence_v2_initial: Any
    runtime_evidence_v2_fresh: Any

    # Trigger
    trigger: Any

    # Capabilities (F1 fix: C0 + C1 + C2)
    capability_c0: Any
    capability_c1: Any
    capability_c2: Any

    # Execution results
    c0_execution_initial: Any
    c1_execution_after_invalidation: Any
    c1_execution_after_invalidation_retry: Any
    c2_execution_success: Any
    c2_execution_replay: Any

    # Digests (locked)
    profile_v1_digest: str
    profile_v2_digest: str

    # Audit records appended during the driver run
    audit_records: list

    # Frozen profile digests for invariant checks
    frozen_profile_v1_digest: str
    frozen_profile_v2_digest: str

    # Mid-driver line-count snapshots (frozen §15 evidence).
    lines_after_c0_initial: int
    lines_after_c1_denied: int
    lines_after_c1_denied_retry: int
    lines_after_c2_success: int
    lines_after_c2_replay: int

    # F1 invariant: C1's nonce is UNSEEN at the moment of the stale
    # attempt. C0 was the consumed capability; C1 is the unconsumed
    # stale proof.
    cap1_nonce_before_mutation_unseen: bool
    cap1_nonce_unseen_at_stale_attempt: bool


def drive_full_lifecycle(harness, executor, controls):
    """Run the full frozen design sequence against a fresh harness.

    Returns a `RunContext` with every per-step artifact attached.
    """
    h = harness
    e = executor
    audit = h.audit

    # Lock profile digests before any state mutation (frozen §9, §16).
    frozen_profile_v1_digest = canonical_sha256(h.profile_v1.signing_payload())
    frozen_profile_v2_digest = canonical_sha256(h.profile_v2.signing_payload())

    # ---- Step A: initial conformance establishment (TC-01) ----
    h.observer.submit_measured_runtime("v1", "rt-ev-v1")
    runtime_evidence_v1 = h.observer.store.get_evidence("rt-ev-v1")
    audit.append(
        event_kind="initial_runtime_evidence",
        payload={"artifact_id": runtime_evidence_v1.artifact_id, "value": "v1"},
        logical_ts=h.clock.now(),
    )

    r13_initial = h.r13.evaluate(
        subject_id=h.subject.subject_id,
        trust_domain=h.subject.trust_domain,


        runtime_evidence=runtime_evidence_v1,
        qualification_state="ACTIVE",
        admission_state="ACTIVE",
        trust_state_current=True,
    )
    audit.append(
        event_kind="r13_initial_eval",
        payload={"artifact_id": r13_initial.artifact_id,
                 "recommended": r13_initial.recommended_state},
        logical_ts=h.clock.now(),
    )

    r14_initial = h.r14.publish_initial(subject=h.subject, r13_evaluation=r13_initial)
    audit.append(
        event_kind="r14_initial_published",
        payload={"artifact_id": r14_initial.artifact_id,
                 "state": r14_initial.new_state,
                 "epoch": r14_initial.state_epoch},
        logical_ts=h.clock.now(),
    )

    # ---- Step B0: capability C0 issuance + execution (TC-02 setup) ----
    # F1 fix: C0 proves normal execution at epoch N. It is the ONLY
    # pre-mutation capability that is allowed to consume. C1 (below) is
    # issued at epoch N and left UNCONSUMED so the stale-capability
    # proof is not confounded with replay state.
    cap0 = h.authorization.issue_capability(
        subject=h.subject,
        action="WRITE_RESOURCE",
        action_payload=bootstrap.ACTION_PAYLOAD,
        qualification=h.qualification,
        admission=h.admission,
        nonce="nonce-c0",
        ttl_ticks=10,
        clock_now=h.clock.now(),
    )
    audit.append(
        event_kind="c0_issued",
        payload={"artifact_id": cap0.artifact_id,
                 "epoch": cap0.observed_state_epoch,
                 "action_digest": cap0.action_digest},
        logical_ts=h.clock.now(),
    )

    c0_execution_initial = e.execute(
        subject=h.subject,
        capability=cap0,
        action="WRITE_RESOURCE",
        action_payload=bootstrap.ACTION_PAYLOAD,
        clock_now=h.clock.now(),
    )
    audit.append(
        event_kind="c0_effect",
        payload={"granted": c0_execution_initial.granted,
                 "reason": c0_execution_initial.reason},
        logical_ts=h.clock.now(),
    )
    lines_after_c0_initial = bootstrap.protected_resource_line_count(
        h.protected_resource_path,
    )

    # ---- Step B1: capability C1 issuance (TC-03) — UNCONSUMED ----
    cap1 = h.authorization.issue_capability(
        subject=h.subject,
        action="WRITE_RESOURCE",
        action_payload=bootstrap.ACTION_PAYLOAD,
        qualification=h.qualification,
        admission=h.admission,
        nonce="nonce-c1",
        ttl_ticks=10,
        clock_now=h.clock.now(),
    )
    audit.append(
        event_kind="c1_issued",
        payload={"artifact_id": cap1.artifact_id,
                 "epoch": cap1.observed_state_epoch,
                 "action_digest": cap1.action_digest},
        logical_ts=h.clock.now(),
    )
    # Snapshot: C1's nonce MUST still be UNSEEN at the moment of the
    # stale-capability attempt. C0 was the consumed capability; C1 is
    # the unconsumed stale proof.
    cap1_nonce_before_mutation_unseen = (
        not h.nonce_registry.is_reserved_or_consumed(cap1.nonce)
    )

    # ---- Step D: runtime mutation (TC-04) ----
    h.observer.submit_measured_runtime("v2", "rt-ev-v2-initial")
    runtime_evidence_v2_initial = h.observer.store.get_evidence("rt-ev-v2-initial")
    audit.append(
        event_kind="runtime_mutation",
        payload={"prior_value": "v1", "current_value": "v2",
                 "evidence_id": runtime_evidence_v2_initial.artifact_id},
        logical_ts=h.clock.now(),
    )

    # ---- Step E: independent trigger observation (TC-05) ----
    trigger = h.observer.observe_change(h.subject.subject_id, h.subject.trust_domain)
    audit.append(
        event_kind="trigger_observed",
        payload={"artifact_id": trigger.artifact_id,
                 "trigger_type": trigger.trigger_type},
        logical_ts=h.clock.now(),
    )

    # ---- Step F: lifecycle invalidation (TC-06) ----
    r13_invalidated = h.r13.evaluate(
        subject_id=h.subject.subject_id,
        trust_domain=h.subject.trust_domain,


        runtime_evidence=runtime_evidence_v2_initial,
        qualification_state="ACTIVE",
        admission_state="ACTIVE",
        trust_state_current=True,
    )
    audit.append(
        event_kind="r13_invalidated_eval",
        payload={"artifact_id": r13_invalidated.artifact_id,
                 "recommended": r13_invalidated.recommended_state},
        logical_ts=h.clock.now(),
    )

    r14_invalidated = h.r14.publish_transition(
        subject=h.subject,
        prior_state="CONFORMANT",
        new_state="REATTESTATION_REQUIRED",
        rationale="runtime mutation v1->v2 invalidates profile v1",
        r13_evaluation=r13_invalidated,
        trigger_observation=trigger,
    )
    audit.append(
        event_kind="n_plus_1_published",
        payload={"artifact_id": r14_invalidated.artifact_id,
                 "state": r14_invalidated.new_state,
                 "epoch": r14_invalidated.state_epoch},
        logical_ts=h.clock.now(),
    )

    # ---- Step G: stale C1 execution denied (TC-08) ----
    # Snapshot: C1's nonce MUST be UNSEEN at this moment (F1 fix).
    cap1_nonce_unseen_at_stale_attempt = (
        not h.nonce_registry.is_reserved_or_consumed(cap1.nonce)
    )
    c1_execution_after_invalidation = e.execute(
        subject=h.subject,
        capability=cap1,
        action="WRITE_RESOURCE",
        action_payload=bootstrap.ACTION_PAYLOAD,
        clock_now=h.clock.now(),
    )
    audit.append(
        event_kind="c1_denied",
        payload={"granted": c1_execution_after_invalidation.granted,
                 "reason": c1_execution_after_invalidation.reason,
                 "step": c1_execution_after_invalidation.step},
        logical_ts=h.clock.now(),
    )
    lines_after_c1_denied = bootstrap.protected_resource_line_count(
        h.protected_resource_path,
    )

    # ---- Step G2: stale C1 retry denied (TC-09) ----
    c1_execution_after_invalidation_retry = e.execute(
        subject=h.subject,
        capability=cap1,
        action="WRITE_RESOURCE",
        action_payload=bootstrap.ACTION_PAYLOAD,
        clock_now=h.clock.now(),
    )
    audit.append(
        event_kind="c1_denied_retry",
        payload={"granted": c1_execution_after_invalidation_retry.granted,
                 "reason": c1_execution_after_invalidation_retry.reason},
        logical_ts=h.clock.now(),
    )
    lines_after_c1_denied_retry = bootstrap.protected_resource_line_count(
        h.protected_resource_path,
    )

    # ---- Step H: predeclared profile v2 activation (TC-10) ----
    # Trusted controls retain the one-time activation closure; the
    # participant-facing harness has no activation token/key.
    controls.activate_predeclared_profile(
        h.profile_v2.artifact_id,
        h.profile_v2.artifact_digest,
    )
    audit.append(
        event_kind="profile_v2_activated",
        payload={"profile_id": h.profile_v2.artifact_id,
                 "digest": frozen_profile_v2_digest,
                 "required_runtime_version": h.profile_v2.required_runtime_version},
        logical_ts=h.clock.now(),
    )

    # ---- Step I: fresh post-change runtime evidence (TC-11) ----
    h.observer.submit_measured_runtime("v2", "rt-ev-v2-fresh")
    runtime_evidence_v2_fresh = h.observer.store.get_evidence("rt-ev-v2-fresh")
    audit.append(
        event_kind="post_change_evidence",
        payload={"artifact_id": runtime_evidence_v2_fresh.artifact_id,
                 "value": "v2"},
        logical_ts=h.clock.now(),
    )

    # ---- Step J: R13 positive re-evaluation (TC-12) ----
    r13_restored = h.r13.evaluate(
        subject_id=h.subject.subject_id,
        trust_domain=h.subject.trust_domain,


        runtime_evidence=runtime_evidence_v2_fresh,
        qualification_state="ACTIVE",
        admission_state="ACTIVE",
        trust_state_current=True,
    )
    audit.append(
        event_kind="r13_restore_eval",
        payload={"artifact_id": r13_restored.artifact_id,
                 "recommended": r13_restored.recommended_state},
        logical_ts=h.clock.now(),
    )

    # ---- Step K: R14 restoration (TC-13) ----
    r14_restored = h.r14.publish_transition(
        subject=h.subject,
        prior_state="REATTESTATION_REQUIRED",
        new_state="CONFORMANT",
        rationale="re-attested against predeclared profile v2",
        r13_evaluation=r13_restored,
        trigger_observation=None,
    )
    audit.append(
        event_kind="n_plus_2_published",
        payload={"artifact_id": r14_restored.artifact_id,
                 "state": r14_restored.new_state,
                 "epoch": r14_restored.state_epoch},
        logical_ts=h.clock.now(),
    )

    # Re-grant protected-resource authority (consumed by C1).
    h.state_store.grant_protected_resource_authority(
        h.protected_resource_authority_token,
    )

    # ---- Step L: capability C2 issuance (TC-14) ----
    cap2 = h.authorization.issue_capability(
        subject=h.subject,
        action="WRITE_RESOURCE",
        action_payload=bootstrap.ACTION_PAYLOAD,
        qualification=h.qualification,
        admission=h.admission,
        nonce="nonce-c2",
        ttl_ticks=10,
        clock_now=h.clock.now(),
    )
    audit.append(
        event_kind="c2_issued",
        payload={"artifact_id": cap2.artifact_id,
                 "epoch": cap2.observed_state_epoch,
                 "action_digest": cap2.action_digest},
        logical_ts=h.clock.now(),
    )

    # ---- Step M: restored execution (TC-15) ----
    c2_execution_success = e.execute(
        subject=h.subject,
        capability=cap2,
        action="WRITE_RESOURCE",
        action_payload=bootstrap.ACTION_PAYLOAD,
        clock_now=h.clock.now(),
    )
    audit.append(
        event_kind="c2_effect",
        payload={"granted": c2_execution_success.granted,
                 "reason": c2_execution_success.reason},
        logical_ts=h.clock.now(),
    )
    lines_after_c2_success = bootstrap.protected_resource_line_count(
        h.protected_resource_path,
    )

    # ---- Step N: replay C2 (TC-16) ----
    c2_execution_replay = e.execute(
        subject=h.subject,
        capability=cap2,
        action="WRITE_RESOURCE",
        action_payload=bootstrap.ACTION_PAYLOAD,
        clock_now=h.clock.now(),
    )
    audit.append(
        event_kind="c2_replay_denied",
        payload={"granted": c2_execution_replay.granted,
                 "reason": c2_execution_replay.reason},
        logical_ts=h.clock.now(),
    )
    lines_after_c2_replay = bootstrap.protected_resource_line_count(
        h.protected_resource_path,
    )

    profile_v1_digest = frozen_profile_v1_digest
    profile_v2_digest = frozen_profile_v2_digest

    return RunContext(
        harness=h,
        executor=e,
        r13_initial=r13_initial,
        r14_initial=r14_initial,
        r13_invalidated=r13_invalidated,
        r14_invalidated=r14_invalidated,
        r13_restored=r13_restored,
        r14_restored=r14_restored,
        runtime_evidence_v1=runtime_evidence_v1,
        runtime_evidence_v2_initial=runtime_evidence_v2_initial,
        runtime_evidence_v2_fresh=runtime_evidence_v2_fresh,
        trigger=trigger,
        capability_c0=cap0,
        capability_c1=cap1,
        capability_c2=cap2,
        c0_execution_initial=c0_execution_initial,
        c1_execution_after_invalidation=c1_execution_after_invalidation,
        c1_execution_after_invalidation_retry=c1_execution_after_invalidation_retry,
        c2_execution_success=c2_execution_success,
        c2_execution_replay=c2_execution_replay,
        profile_v1_digest=profile_v1_digest,
        profile_v2_digest=profile_v2_digest,
        audit_records=list(audit.records()),
        frozen_profile_v1_digest=frozen_profile_v1_digest,
        frozen_profile_v2_digest=frozen_profile_v2_digest,
        lines_after_c0_initial=lines_after_c0_initial,
        lines_after_c1_denied=lines_after_c1_denied,
        lines_after_c1_denied_retry=lines_after_c1_denied_retry,
        lines_after_c2_success=lines_after_c2_success,
        lines_after_c2_replay=lines_after_c2_replay,
        cap1_nonce_before_mutation_unseen=cap1_nonce_before_mutation_unseen,
        cap1_nonce_unseen_at_stale_attempt=cap1_nonce_unseen_at_stale_attempt,
    )


@pytest.fixture
def lifecycle():
    """Yield a fully-driven RunContext; tear down on exit."""
    h, controls = bootstrap.build_harness_with_controls(prefix="tc")
    e = bootstrap.attach_executor(h)
    ctx = drive_full_lifecycle(h, e, controls)
    try:
        yield ctx
    finally:
        bootstrap.teardown(h)


@pytest.fixture
def harness():
    """Yield a (harness, executor) tuple at the initial CONFORMANT state.

    Used by the negative tests and the F2/F4/F5 attack regressions that
    need a clean harness with one successful pre-mutation execution.
    """
    h = bootstrap.build_harness(prefix="ns")
    e = bootstrap.attach_executor(h)

    h.observer.submit_measured_runtime("v1", "rt-ev-v1")
    ev_v1 = h.observer.store.get_evidence("rt-ev-v1")
    profile_v1_digest = canonical_sha256(h.profile_v1.signing_payload())
    r13 = h.r13.evaluate(
        subject_id=h.subject.subject_id,
        trust_domain=h.subject.trust_domain,


        runtime_evidence=ev_v1,
        qualification_state="ACTIVE",
        admission_state="ACTIVE",
        trust_state_current=True,
    )
    h.r14.publish_initial(subject=h.subject, r13_evaluation=r13)
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
    assert cap is not None
    e.execute(
        subject=h.subject,
        capability=cap,
        action="WRITE_RESOURCE",
        action_payload=bootstrap.ACTION_PAYLOAD,
        clock_now=h.clock.now(),
    )

    try:
        yield h, e
    finally:
        bootstrap.teardown(h)


@pytest.fixture
def authority_harness():
    """Trusted-authority fixture for tests that must simulate issuer actions.

    The returned TrustedControls object is not part of the participant-facing
    harness; only explicit authority-boundary regressions receive it.
    """
    h, controls = bootstrap.build_harness_with_controls(prefix="auth")
    e = bootstrap.attach_executor(h)

    h.observer.submit_measured_runtime("v1", "rt-ev-v1")
    ev_v1 = h.observer.store.get_evidence("rt-ev-v1")
    r13 = h.r13.evaluate(
        subject_id=h.subject.subject_id,
        trust_domain=h.subject.trust_domain,
        runtime_evidence=ev_v1,
        qualification_state="ACTIVE",
        admission_state="ACTIVE",
        trust_state_current=True,
    )
    h.r14.publish_initial(subject=h.subject, r13_evaluation=r13)

    try:
        yield h, e, controls
    finally:
        bootstrap.teardown(h)


@pytest.fixture
def invalidated_lifecycle():
    """Yield a RunContext halted at REATTESTATION_REQUIRED @ epoch 2.

    Used for tests that must observe the subject in a non-conformant
    state (TC-07).
    """
    h = bootstrap.build_harness(prefix="inv")
    e = bootstrap.attach_executor(h)

    h.observer.submit_measured_runtime("v1", "rt-ev-v1")
    ev_v1 = h.observer.store.get_evidence("rt-ev-v1")
    profile_v1_digest = canonical_sha256(h.profile_v1.signing_payload())

    r13_initial = h.r13.evaluate(
        subject_id=h.subject.subject_id,
        trust_domain=h.subject.trust_domain,


        runtime_evidence=ev_v1,
        qualification_state="ACTIVE",
        admission_state="ACTIVE",
        trust_state_current=True,
    )
    r14_initial = h.r14.publish_initial(subject=h.subject, r13_evaluation=r13_initial)
    cap1 = h.authorization.issue_capability(
        subject=h.subject,
        action="WRITE_RESOURCE",
        action_payload=bootstrap.ACTION_PAYLOAD,
        qualification=h.qualification,
        admission=h.admission,
        nonce="nonce-c1",
        ttl_ticks=10,
        clock_now=h.clock.now(),
    )
    assert cap1 is not None
    e.execute(
        subject=h.subject,
        capability=cap1,
        action="WRITE_RESOURCE",
        action_payload=bootstrap.ACTION_PAYLOAD,
        clock_now=h.clock.now(),
    )
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
    r14_inv = h.r14.publish_transition(
        subject=h.subject,
        prior_state="CONFORMANT",
        new_state="REATTESTATION_REQUIRED",
        rationale="runtime mutation v1->v2",
        r13_evaluation=r13_inv,
        trigger_observation=trig,
    )

    # Build a minimal RunContext. Only the fields TC-07/NS-01 need are set;
    # the rest are sentinel None.
    @dataclass
    class _InvCtx:
        harness: Any
        executor: Any
        r14_initial: Any
        r14_invalidated: Any

    ctx = _InvCtx(
        harness=h,
        executor=e,
        r14_initial=r14_initial,
        r14_invalidated=r14_inv,
    )
    try:
        yield ctx
    finally:
        bootstrap.teardown(h)
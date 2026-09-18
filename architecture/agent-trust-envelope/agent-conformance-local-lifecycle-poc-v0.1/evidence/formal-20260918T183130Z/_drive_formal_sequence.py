"""Formal run: drive the harness through the exact causal sequence
required by the frozen v0.1.1 design and emit per-step artifacts.

Required causal ordering:
  C1_issued
  < runtime_mutation
  < trigger_observed
  < N+1_published
  < C1_denied
  < post_change_evidence
  < R13_restore_eval
  < N+2_published
  < C2_issued
  < C2_effect
"""
from __future__ import annotations

import copy as _copy
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from conformance.audit import GENESIS_PREV_HASH, AuditRecorder
from conformance.canonical import canonical_sha256
from conformance.crypto import sign_ed25519
from fixtures import bootstrap


def _ev(obj):
    if obj is None:
        return None
    d = {}
    for k, v in obj.__dict__.items():
        if isinstance(v, (bytes, bytearray)):
            d[k + "_hex"] = bytes(v).hex()
        else:
            d[k] = v
    return d


def main() -> None:
    out = ROOT / "evidence" / "formal-20260918T183130Z"
    out.mkdir(parents=True, exist_ok=True)

    h, controls = bootstrap.build_harness_with_controls(prefix="formal")

    # ---- Phase A: CONFORMANT @ epoch 1 (initial) ----
    h.observer.submit_measured_runtime("v1", "rt-ev-v1")
    ev_v1 = h.observer.store.get_evidence("rt-ev-v1")
    r13_initial = h.r13.evaluate(
        subject_id=h.subject.subject_id,
        trust_domain=h.subject.trust_domain,
        runtime_evidence=ev_v1,
        qualification_state="ACTIVE",
        admission_state="ACTIVE",
        trust_state_current=True,
    )
    h.r14.publish_initial(
        subject=h.subject,
        r13_evaluation=r13_initial,
    )
    (out / "01_r14_initial.json").write_text(
        json.dumps(
            {
                "phase": "CONFORMANT @ epoch 1 (initial)",
                "r13_evaluation": _ev(r13_initial),
                "r14_state_snapshot": _ev(h.state_store.get_authoritative_state(
                    h.subject.subject_id,
                )),
            },
            indent=2,
            sort_keys=True,
            default=str,
        ) + "\n"
    )

    # ---- Phase B: C0 (consumed at epoch 1) ----
    cap0 = h.authorization.issue_capability(
        subject=h.subject,
        action="WRITE_RESOURCE",
        action_payload=bootstrap.ACTION_PAYLOAD,
        qualification=h.state_store.get_qualification_fixture(
            h.qualification.artifact_id,
        ),
        admission=h.state_store.get_admission_fixture(
            h.admission.artifact_id,
        ),
        nonce="c0-normal",
        ttl_ticks=10,
        clock_now=h.clock.now(),
    )
    assert cap0 is not None, "C0 issuance failed unexpectedly"
    e = bootstrap.attach_executor(h)
    c0_effect = e.execute(
        subject=h.subject,
        capability=cap0,
        action="WRITE_RESOURCE",
        action_payload=bootstrap.ACTION_PAYLOAD,
        clock_now=h.clock.now(),
    )

    # ---- Phase C: C1 (issued at epoch 1, left UNCONSUMED) ----
    cap1 = h.authorization.issue_capability(
        subject=h.subject,
        action="WRITE_RESOURCE",
        action_payload=bootstrap.ACTION_PAYLOAD,
        qualification=h.state_store.get_qualification_fixture(
            h.qualification.artifact_id,
        ),
        admission=h.state_store.get_admission_fixture(
            h.admission.artifact_id,
        ),
        nonce="c1-stale",
        ttl_ticks=10,
        clock_now=h.clock.now(),
    )
    assert cap1 is not None, "C1 issuance failed unexpectedly"
    cap1_nonce_unseen_before_mutation = (
        not h.nonce_registry.is_reserved_or_consumed(cap1.nonce)
    )

    (out / "02_c0_and_c1.json").write_text(
        json.dumps(
            {
                "c0_granted": c0_effect.granted,
                "c0_effect_record": _ev(c0_effect),
                "c0_consumed": h.nonce_registry.status(cap0.nonce),
                "c1_issued": True,
                "c1_capability": _ev(cap1),
                "c1_nonce": cap1.nonce,
                "c1_nonce_unseen_before_mutation": cap1_nonce_unseen_before_mutation,
                "c1_state_at_issuance": h.nonce_registry.status(cap1.nonce),
            },
            indent=2,
            sort_keys=True,
            default=str,
        ) + "\n"
    )

    # ---- Phase D: runtime v1 -> v2 ----
    h.observer.submit_measured_runtime("v2", "rt-ev-v2")

    # ---- Phase E: independent trigger observation ----
    trigger = h.observer.observe_change(
        h.subject.subject_id, h.subject.trust_domain,
    )
    # Independent: trigger created by observer; R13 below.

    # ---- Phase F: R13 evaluation against v1 profile (active profile is v1) ----
    ev_v2 = h.observer.store.get_evidence("rt-ev-v2")
    r13_inv = h.r13.evaluate(
        subject_id=h.subject.subject_id,
        trust_domain=h.subject.trust_domain,
        runtime_evidence=ev_v2,
        qualification_state="ACTIVE",
        admission_state="ACTIVE",
        trust_state_current=True,
    )

    # ---- Phase G: N+1 published ----
    r14_inv = h.r14.publish_transition(
        subject=h.subject,
        prior_state="CONFORMANT",
        new_state="REATTESTATION_REQUIRED",
        rationale="runtime v1->v2",
        r13_evaluation=r13_inv,
        trigger_observation=trigger,
    )
    (out / "03_n_plus_1_published.json").write_text(
        json.dumps(
            {
                "trigger": _ev(trigger),
                "r13_inv": _ev(r13_inv),
                "r14_inv": _ev(r14_inv),
                "r14_state_snapshot": _ev(h.state_store.get_authoritative_state(
                    h.subject.subject_id,
                )),
            },
            indent=2,
            sort_keys=True,
            default=str,
        ) + "\n"
    )

    # ---- Phase H: C1 stale-capability attempt (denied) ----
    cap1_nonce_unseen_at_stale_attempt = (
        not h.nonce_registry.is_reserved_or_consumed(cap1.nonce)
    )
    resource_lines_before = sum(
        1 for _ in open(h.protected_resource_path, "r")
    )
    c1_stale = e.execute(
        subject=h.subject,
        capability=cap1,
        action="WRITE_RESOURCE",
        action_payload=bootstrap.ACTION_PAYLOAD,
        clock_now=h.clock.now(),
    )
    resource_lines_after = sum(
        1 for _ in open(h.protected_resource_path, "r")
    )
    (out / "04_c1_stale_denied.json").write_text(
        json.dumps(
            {
                "cap1_nonce": cap1.nonce,
                "cap1_nonce_unseen_at_stale_attempt": cap1_nonce_unseen_at_stale_attempt,
                "c1_denied": c1_stale.granted is False,
                "c1_denial_record": _ev(c1_stale),
                "resource_lines_before": resource_lines_before,
                "resource_lines_after": resource_lines_after,
                "c1_zero_resource_effect": resource_lines_before == resource_lines_after,
            },
            indent=2,
            sort_keys=True,
            default=str,
        ) + "\n"
    )

    # ---- Phase I: predeclared profile v2 activation ----
    # The profile registry was installed and frozen during preflight;
    # activation goes through the trusted controls.
    controls.activate_predeclared_profile(
        h.profile_v2.artifact_id,
        h.profile_v2.artifact_digest,
    )

    # ---- Phase J: post-change evidence (rt-ev-v2 already exists) ----
    # Confirm the evidence resolves in the observer-authoritative store.
    assert h.observer.store.get_evidence(ev_v2.artifact_id) is not None

    # ---- Phase K: R13 positive evaluation against active profile v2 ----
    r13_restore = h.r13.evaluate(
        subject_id=h.subject.subject_id,
        trust_domain=h.subject.trust_domain,
        runtime_evidence=ev_v2,
        qualification_state="ACTIVE",
        admission_state="ACTIVE",
        trust_state_current=True,
    )

    # ---- Phase L: N+2 published ----
    r14_restore = h.r14.publish_transition(
        subject=h.subject,
        prior_state="REATTESTATION_REQUIRED",
        new_state="CONFORMANT",
        rationale="attestation successful against profile v2",
        r13_evaluation=r13_restore,
        trigger_observation=None,
    )
    (out / "05_post_change_evidence_and_n_plus_2.json").write_text(
        json.dumps(
            {
                "post_change_evidence": _ev(ev_v2),
                "post_change_evidence_resolves_in_observer_store": True,
                "r13_restore": _ev(r13_restore),
                "r14_restore": _ev(r14_restore),
                "r14_state_snapshot": _ev(h.state_store.get_authoritative_state(
                    h.subject.subject_id,
                )),
            },
            indent=2,
            sort_keys=True,
            default=str,
        ) + "\n"
    )

    # ---- Phase M: C2 issuance and execution ----
    cap2 = h.authorization.issue_capability(
        subject=h.subject,
        action="WRITE_RESOURCE",
        action_payload=bootstrap.ACTION_PAYLOAD,
        qualification=h.state_store.get_qualification_fixture(
            h.qualification.artifact_id,
        ),
        admission=h.state_store.get_admission_fixture(
            h.admission.artifact_id,
        ),
        nonce="c2-restored",
        ttl_ticks=10,
        clock_now=h.clock.now(),
    )
    assert cap2 is not None, "C2 issuance failed unexpectedly"
    resource_lines_before_c2 = sum(
        1 for _ in open(h.protected_resource_path, "r")
    )
    c2_effect = e.execute(
        subject=h.subject,
        capability=cap2,
        action="WRITE_RESOURCE",
        action_payload=bootstrap.ACTION_PAYLOAD,
        clock_now=h.clock.now(),
    )
    resource_lines_after_c2 = sum(
        1 for _ in open(h.protected_resource_path, "r")
    )

    # ---- Phase N: C2 replay (denied) ----
    resource_lines_before_replay = sum(
        1 for _ in open(h.protected_resource_path, "r")
    )
    c2_replay = e.execute(
        subject=h.subject,
        capability=cap2,
        action="WRITE_RESOURCE",
        action_payload=bootstrap.ACTION_PAYLOAD,
        clock_now=h.clock.now(),
    )
    resource_lines_after_replay = sum(
        1 for _ in open(h.protected_resource_path, "r")
    )

    (out / "06_c2_and_replay.json").write_text(
        json.dumps(
            {
                "c2_capability": _ev(cap2),
                "c2_granted": c2_effect.granted,
                "c2_effect_record": _ev(c2_effect),
                "c2_resource_lines_before": resource_lines_before_c2,
                "c2_resource_lines_after": resource_lines_after_c2,
                "c2_caused_one_effect": (
                    resource_lines_after_c2 == resource_lines_before_c2 + 1
                ),
                "c2_replay_denied": c2_replay.granted is False,
                "c2_replay_record": _ev(c2_replay),
                "c2_replay_resource_lines_before": resource_lines_before_replay,
                "c2_replay_resource_lines_after": resource_lines_after_replay,
                "c2_replay_zero_effect": (
                    resource_lines_after_replay == resource_lines_before_replay
                ),
                "resource_final_line_count": resource_lines_after_replay,
            },
            indent=2,
            sort_keys=True,
            default=str,
        ) + "\n"
    )

    # ---- Final lifecycle-state snapshot ----
    final_state = h.state_store.get_authoritative_state(h.subject.subject_id)
    (out / "07_lifecycle_final.json").write_text(
        json.dumps(
            {
                "final_r14_state_snapshot": _ev(final_state),
                "lifecycle_epoch_monotonic": final_state.state_epoch == 3,
            },
            indent=2,
            sort_keys=True,
            default=str,
        ) + "\n"
    )

    bootstrap.teardown(h)
    print("FORMAL_LIFECYCLE_SEQUENCE_EMITTED=" + str(out))


if __name__ == "__main__":
    main()

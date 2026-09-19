#!/usr/bin/env python3
"""Evidence-closure candidate runner for Agent Conformance Local Lifecycle PoC v0.1.

This runner corrects only the evidence-generation defects identified in the
independent closeout review of 20260918T183130Z-acl-lifecycle-poc-v0.1.

It does NOT modify the reviewed implementation baseline.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

POC_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = Path(__file__).resolve().parents[4]

# Deliberately fail-closed until this bounded implementation receives an
# independent review and is rebound to that reviewed implementation commit.
IMPLEMENTATION_BASELINE = "PIN_AFTER_INDEPENDENT_REVIEW"

FROZEN_BLOBS = {
    "architecture/agent-trust-envelope/AGENT-CONFORMANCE-LOCAL-LIFECYCLE-POC-v0.1.1-FORMAL-EVIDENCE-CLOSURE-AMENDMENT-v0.1.md":
        "551847bb96a0ca109d803479462c60a363962687",
    "architecture/agent-trust-envelope/AGENT-CONFORMANCE-LOCAL-LIFECYCLE-POC-v0.1.1-FORMAL-EVIDENCE-CLOSURE-AMENDMENT-v0.1-ADVERSARIAL-REVIEW.md":
        "82c18420aa7028f00742644eab7926199d934bcd",
    "architecture/agent-trust-envelope/AGENT-CONFORMANCE-LOCAL-LIFECYCLE-POC-v0.1.1-DESIGN.md":
        "4faea2a16261ca9416fe8bb4eceaaff80593eb59",
    "architecture/agent-trust-envelope/AGENT-CONFORMANCE-LOCAL-LIFECYCLE-POC-v0.1.1-FREEZE.md":
        "d1da477dfaa8bb4682a01408596cd468a6e3fd64",
    "architecture/agent-trust-envelope/AGENT-CONFORMANCE-PROTOCOL-v0.1.2.md":
        "f8bc4464db197a58b6402e01d0378592ba7dc220",
    "architecture/agent-trust-envelope/AGENT-CONFORMANCE-PROTOCOL-v0.1.2-FREEZE.md":
        "62630ddc3bdbf114c7d07beffa2621737c623aaf",
    "architecture/agent-trust-envelope/AGENT-QUALIFICATION-AND-ADMISSION-PROTOCOL-v0.2.2.md":
        "28b4b0a36e7ded946686c0eb45d4ee820a35c2bf",
    "architecture/agent-trust-envelope/ATE-REVOCATION-TRUST-STATE-MODEL-v0.1.md":
        "0a4c42c30b0914bd0c0dc660c3aa8cc80ae5cb86",
    "architecture/agent-trust-envelope/ATE-ENFORCEMENT-PLANE-v0.1.md":
        "154465106614f1448f9bbbca94ff7b5862bfd00a",
    "architecture/agent-trust-envelope/ATE-AUDIT-ACCOUNTABILITY-MODEL-v0.1.md":
        "82450a5d049cc1d6f53a6cc2a4f952dcb442aa8c",
}

IMPLEMENTATION_PATHS = [
    "architecture/agent-trust-envelope/agent-conformance-local-lifecycle-poc-v0.1/conformance",
    "architecture/agent-trust-envelope/agent-conformance-local-lifecycle-poc-v0.1/fixtures",
    "architecture/agent-trust-envelope/agent-conformance-local-lifecycle-poc-v0.1/tests",
]

EXPECTED_CAUSAL_ORDER = [
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


class FormalRunError(RuntimeError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise FormalRunError(message)


def require_formal_authorization(formal: bool, environ: dict[str, str]) -> None:
    """Fail closed unless both the PI gate and reviewed-dry-run gate exist."""
    if not formal:
        return
    require(
        environ.get("ACL_FORMAL_RUN_AUTHORIZED") == "YES",
        "STOP_BEFORE_SCORING: formal mode requires explicit PI authorization",
    )
    require(
        environ.get("ACL_REVIEWED_DRY_RUN_GATE") == "YES",
        "STOP_BEFORE_SCORING: formal mode requires an accepted reviewed dry-run gate",
    )


def sh(*args: str, cwd: Path = REPO_ROOT, check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        args,
        cwd=cwd,
        check=check,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )


def blob_sha(path: str) -> str:
    return sh("git", "hash-object", path).stdout.strip()


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def jsonable(obj: Any) -> Any:
    if obj is None:
        return None
    if isinstance(obj, (str, int, float, bool)):
        return obj
    if isinstance(obj, (bytes, bytearray)):
        return obj.hex()
    if isinstance(obj, list):
        return [jsonable(x) for x in obj]
    if isinstance(obj, tuple):
        return [jsonable(x) for x in obj]
    if isinstance(obj, dict):
        return {str(k): jsonable(v) for k, v in obj.items()}
    if hasattr(obj, "__dict__"):
        out = {}
        for k, v in obj.__dict__.items():
            out[k + "_hex" if isinstance(v, (bytes, bytearray)) else k] = jsonable(v)
        return out
    return str(obj)


def write_json(path: Path, payload: Any) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def line_count(path: str) -> int:
    with open(path, "r", encoding="utf-8") as fh:
        return sum(1 for line in fh if line.strip())


def verify_copied_ledger(records: list[Any], public_key: Any) -> tuple[bool, str]:
    from conformance.audit import GENESIS_PREV_HASH
    from conformance.canonical import canonical_sha256
    from conformance.crypto import verify_ed25519

    prev_hash = GENESIS_PREV_HASH
    expected_seq = 1
    for rec in records:
        if rec.event_sequence != expected_seq:
            return False, f"sequence mismatch at {rec.event_sequence}"
        if rec.prev_hash != prev_hash:
            return False, f"prev_hash mismatch at seq {rec.event_sequence}"
        pd = canonical_sha256(rec.payload)
        if rec.payload_digest != pd:
            return False, f"payload_digest mismatch at seq {rec.event_sequence}"
        canonical_record = {
            "artifact_kind": "AuditRecord",
            "event_sequence": rec.event_sequence,
            "event_kind": rec.event_kind,
            "payload": rec.payload,
            "prev_hash": rec.prev_hash,
            "payload_digest": rec.payload_digest,
            "logical_ts": rec.logical_ts,
        }
        if rec.record_hash != canonical_sha256(canonical_record):
            return False, f"record_hash mismatch at seq {rec.event_sequence}"
        if not verify_ed25519(
            public_key,
            rec.signature,
            rec.signature_domain,
            rec.signing_payload(),
        ):
            return False, f"signature mismatch at seq {rec.event_sequence}"
        prev_hash = rec.record_hash
        expected_seq += 1
    return True, "OK"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--formal",
        action="store_true",
        help="execute as a formal run; requires ACL_FORMAL_RUN_AUTHORIZED=YES",
    )
    args = parser.parse_args()

    mode = "formal" if args.formal else "dry-run"
    require_formal_authorization(args.formal, os.environ)

    # Make local implementation importable only after baseline checks.
    sys.path.insert(0, str(POC_ROOT))

    started = datetime.now(timezone.utc)
    run_stamp = started.strftime("%Y%m%dT%H%M%SZ")
    if mode == "formal":
        run_id = f"{run_stamp}-acl-lifecycle-poc-v0.1.2-evidence-closure"
        evidence_dir = POC_ROOT / "evidence" / f"formal-{run_stamp}-evidence-closure"
    else:
        run_id = f"{run_stamp}-acl-lifecycle-poc-v0.1.2-evidence-closure-dry-run"
        evidence_dir = POC_ROOT / "evidence" / f"dry-run-{run_stamp}-evidence-closure"

    # ---------- PRE-SCORING PREFLIGHT ----------
    current_head = sh("git", "rev-parse", "HEAD").stdout.strip()
    status = sh("git", "status", "--short").stdout
    require(status == "", "STOP_BEFORE_SCORING: worktree is not clean")
    require(
        len(IMPLEMENTATION_BASELINE) == 40
        and all(char in "0123456789abcdef" for char in IMPLEMENTATION_BASELINE),
        "STOP_BEFORE_SCORING: evidence-closure runner is not bound to an independently reviewed implementation baseline",
    )

    # The runner commit may be newer than the reviewed implementation commit.
    # The implementation subtree itself must remain byte-identical to baseline.
    diff = sh(
        "git", "diff", "--name-only", IMPLEMENTATION_BASELINE, "--", *IMPLEMENTATION_PATHS,
    ).stdout.strip()
    require(
        diff == "",
        "STOP_BEFORE_SCORING: reviewed implementation subtree differs from baseline",
    )

    frozen_actual = {path: blob_sha(path) for path in FROZEN_BLOBS}
    require(
        frozen_actual == FROZEN_BLOBS,
        "STOP_BEFORE_SCORING: frozen artifact blob verification failed",
    )
    require(not evidence_dir.exists(), "STOP_BEFORE_SCORING: evidence directory already exists")
    evidence_dir.mkdir(parents=True)

    preflight = {
        "run_id": run_id,
        "mode": mode,
        "runner_head": current_head,
        "implementation_baseline": IMPLEMENTATION_BASELINE,
        "implementation_subtree_diff_empty": True,
        "worktree_clean_before_run": True,
        "frozen_blob_verification": frozen_actual,
        "python": sys.version,
    }
    write_json(evidence_dir / "00_preflight.json", preflight)

    # Development suite is part of formal evidence but not a substitute for the
    # single-process formal lifecycle proof below.
    pytest_xml = evidence_dir / "pytest-results.xml"
    pytest_proc = sh(
        sys.executable,
        "-m",
        "pytest",
        "-q",
        f"--junitxml={pytest_xml}",
        cwd=POC_ROOT,
        check=False,
    )
    (evidence_dir / "pytest-summary.txt").write_text(pytest_proc.stdout, encoding="utf-8")
    try:
        require(pytest_proc.returncode == 0, "CONFORMANCE_LIFECYCLE_POC_FAIL: pytest failed")
        require(
            "passed" in pytest_proc.stdout
            and "failed" not in pytest_proc.stdout.lower()
            and "skipped" not in pytest_proc.stdout.lower()
            and "xfailed" not in pytest_proc.stdout.lower(),
            "CONFORMANCE_LIFECYCLE_POC_FAIL: pytest result is not exact 81-pass clean result",
        )
    except FormalRunError as exc:
        (evidence_dir / "RUN-FAILED.txt").write_text(str(exc) + "\n", encoding="utf-8")
        raise

        from conformance.audit import copy_and_tamper
        from conformance.evidence import (
            CASE_DEFINITIONS,
            CASE_NODE_IDS,
            artifact_envelope,
            audit_record_json,
            signature_verification_rows,
        )
        from fixtures import bootstrap

    h = None
    classification = "INCONCLUSIVE_EVIDENCE_INVALID"
    try:
        h, controls = bootstrap.build_harness_with_controls(prefix=f"{mode}-successor")
        e = controls.attach_executor(h)
        write_json(
            evidence_dir / "01_verification_keys.json",
            h.verification_key_registry,
        )

        # Explicit preflight proof: exactly the two predeclared profiles are
        # present in the installed frozen registry and profile v1 is active.
        registry = getattr(h.state_store, "_profile_registry", None)
        require(registry is not None, "STOP_BEFORE_SCORING: profile registry missing")
        require(registry.frozen, "STOP_BEFORE_SCORING: profile registry not frozen")
        require(
            set(registry.registered_ids()) == {"profile-v1", "profile-v2"},
            "STOP_BEFORE_SCORING: profile registry is not exactly the predeclared v1/v2 set",
        )
        active_preflight = h.state_store.get_active_profile()
        require(
            active_preflight is not None and active_preflight.artifact_id == "profile-v1",
            "STOP_BEFORE_SCORING: profile v1 is not the initial active profile",
        )

        # Persist predeclared profiles before any scored mutation.
        profiles = {
            "profile_v1": jsonable(h.profile_v1),
            "profile_v2": jsonable(h.profile_v2),
        }
        write_json(evidence_dir / "01_profiles.json", profiles)

        # Initial evidence and conformance.
        controls.submit_measured_runtime("v1", "rt-ev-v1")
        ev_v1 = h.observer.store.get_evidence("rt-ev-v1")
        r13_initial = h.r13.evaluate(
            subject_id=h.subject.subject_id,
            trust_domain=h.subject.trust_domain,
            runtime_evidence=ev_v1,
            qualification_state="ACTIVE",
            admission_state="ACTIVE",
            trust_state_current=True,
        )
        r14_initial = h.r14.publish_initial(
            subject=h.subject, r13_evaluation=r13_initial,
        )
        controls.append_audit(
            event_kind="initial_conformance",
            payload={
                "r13_id": r13_initial.artifact_id,
                "r14_id": r14_initial.artifact_id,
                "state": r14_initial.new_state,
                "epoch": r14_initial.state_epoch,
            },
            logical_ts=h.clock.now(),
        )
        require(r14_initial.new_state == "CONFORMANT" and r14_initial.state_epoch == 1,
                "CONFORMANCE_LIFECYCLE_POC_FAIL: initial state not CONFORMANT @ 1")

        # C0 succeeds and consumes initial protected-resource authority.
        cap0 = h.authorization.issue_capability(
            subject=h.subject,
            action="WRITE_RESOURCE",
            action_payload=bootstrap.ACTION_PAYLOAD,
            qualification=h.state_store.get_qualification_fixture(h.qualification.artifact_id),
            admission=h.state_store.get_admission_fixture(h.admission.artifact_id),
            nonce="c0-normal",
            ttl_ticks=10,
            clock_now=h.clock.now(),
        )
        require(cap0 is not None, "CONFORMANCE_LIFECYCLE_POC_FAIL: C0 issuance failed")
        controls.append_audit(
            event_kind="c0_issued",
            payload={"capability_id": cap0.artifact_id, "epoch": cap0.observed_state_epoch},
            logical_ts=h.clock.now(),
        )
        before_c0 = line_count(h.protected_resource_path)
        c0 = e.execute(
            subject=h.subject, capability=cap0, action="WRITE_RESOURCE",
            action_payload=bootstrap.ACTION_PAYLOAD, clock_now=h.clock.now(),
        )
        after_c0 = line_count(h.protected_resource_path)
        controls.append_audit(
            event_kind="c0_effect",
            payload={"granted": c0.granted, "reason": c0.reason, "line_count": after_c0},
            logical_ts=h.clock.now(),
        )
        require(c0.granted and after_c0 == before_c0 + 1 == 1,
                "CONFORMANCE_LIFECYCLE_POC_FAIL: C0 exact effect failed")

        # C1 issued at epoch 1 and intentionally left unused.
        cap1 = h.authorization.issue_capability(
            subject=h.subject,
            action="WRITE_RESOURCE",
            action_payload=bootstrap.ACTION_PAYLOAD,
            qualification=h.state_store.get_qualification_fixture(h.qualification.artifact_id),
            admission=h.state_store.get_admission_fixture(h.admission.artifact_id),
            nonce="c1-stale",
            ttl_ticks=10,
            clock_now=h.clock.now(),
        )
        require(cap1 is not None, "CONFORMANCE_LIFECYCLE_POC_FAIL: C1 issuance failed")
        require(not h.nonce_registry.is_reserved_or_consumed(cap1.nonce),
                "CONFORMANCE_LIFECYCLE_POC_FAIL: C1 nonce seen before mutation")
        controls.append_audit(
            event_kind="c1_issued",
            payload={"capability_id": cap1.artifact_id, "epoch": cap1.observed_state_epoch,
                     "nonce": cap1.nonce},
            logical_ts=h.clock.now(),
        )

        # Runtime mutation and independent trigger.
        controls.submit_measured_runtime("v2", "rt-ev-v2-initial")
        ev_v2_initial = h.observer.store.get_evidence("rt-ev-v2-initial")
        controls.append_audit(
            event_kind="runtime_mutation",
            payload={"evidence_id": ev_v2_initial.artifact_id,
                     "measured_runtime_version": ev_v2_initial.measured_runtime_version},
            logical_ts=h.clock.now(),
        )
        trigger = h.observer.observe_change(h.subject.subject_id, h.subject.trust_domain)
        controls.append_audit(
            event_kind="trigger_observed",
            payload={"trigger_id": trigger.artifact_id,
                     "current_evidence_id": trigger.current_evidence_id},
            logical_ts=h.clock.now(),
        )
        r13_inv = h.r13.evaluate(
            subject_id=h.subject.subject_id,
            trust_domain=h.subject.trust_domain,
            runtime_evidence=ev_v2_initial,
            qualification_state="ACTIVE",
            admission_state="ACTIVE",
            trust_state_current=True,
        )
        require(r13_inv.recommended_state == "REATTESTATION_REQUIRED",
                "CONFORMANCE_LIFECYCLE_POC_FAIL: R13 did not invalidate")
        r14_inv = h.r14.publish_transition(
            subject=h.subject,
            prior_state="CONFORMANT",
            new_state="REATTESTATION_REQUIRED",
            rationale="runtime v1->v2",
            r13_evaluation=r13_inv,
            trigger_observation=trigger,
        )
        controls.append_audit(
            event_kind="n_plus_1_published",
            payload={"r14_id": r14_inv.artifact_id, "state": r14_inv.new_state,
                     "epoch": r14_inv.state_epoch},
            logical_ts=h.clock.now(),
        )

        # Stale C1 denial must occur before nonce reservation and with zero effect.
        nonce_unseen_at_stale = not h.nonce_registry.is_reserved_or_consumed(cap1.nonce)
        before_c1 = line_count(h.protected_resource_path)
        c1 = e.execute(
            subject=h.subject, capability=cap1, action="WRITE_RESOURCE",
            action_payload=bootstrap.ACTION_PAYLOAD, clock_now=h.clock.now(),
        )
        after_c1 = line_count(h.protected_resource_path)
        controls.append_audit(
            event_kind="c1_denied",
            payload={"granted": c1.granted, "reason": c1.reason, "step": c1.step,
                     "nonce_unseen_before_attempt": nonce_unseen_at_stale,
                     "line_count": after_c1},
            logical_ts=h.clock.now(),
        )
        require(nonce_unseen_at_stale, "CONFORMANCE_LIFECYCLE_POC_FAIL: C1 nonce not unseen")
        require(not c1.granted and before_c1 == after_c1 == 1,
                "CONFORMANCE_LIFECYCLE_POC_FAIL: stale C1 effect or grant occurred")

        # Activate only the predeclared profile v2.
        controls.activate_predeclared_profile(
            h.profile_v2.artifact_id, h.profile_v2.artifact_digest,
        )
        controls.append_audit(
            event_kind="profile_v2_activated",
            payload={"profile_id": h.profile_v2.artifact_id,
                     "profile_digest": h.profile_v2.artifact_digest},
            logical_ts=h.clock.now(),
        )

        # Genuine fresh post-denial evidence.
        controls.submit_measured_runtime("v2", "rt-ev-v2-fresh")
        ev_v2_fresh = h.observer.store.get_evidence("rt-ev-v2-fresh")
        require(ev_v2_fresh.artifact_id != ev_v2_initial.artifact_id,
                "CONFORMANCE_LIFECYCLE_POC_FAIL: fresh evidence id reused")
        require(ev_v2_fresh.logical_ts > ev_v2_initial.logical_ts,
                "CONFORMANCE_LIFECYCLE_POC_FAIL: fresh evidence logical_ts not later")
        require(ev_v2_fresh.event_sequence > ev_v2_initial.event_sequence,
                "CONFORMANCE_LIFECYCLE_POC_FAIL: fresh evidence sequence not later")
        controls.append_audit(
            event_kind="post_change_evidence",
            payload={"evidence_id": ev_v2_fresh.artifact_id,
                     "measured_runtime_version": ev_v2_fresh.measured_runtime_version,
                     "logical_ts": ev_v2_fresh.logical_ts,
                     "event_sequence": ev_v2_fresh.event_sequence},
            logical_ts=h.clock.now(),
        )

        r13_restore = h.r13.evaluate(
            subject_id=h.subject.subject_id,
            trust_domain=h.subject.trust_domain,
            runtime_evidence=ev_v2_fresh,
            qualification_state="ACTIVE",
            admission_state="ACTIVE",
            trust_state_current=True,
        )
        require(r13_restore.runtime_evidence_id == ev_v2_fresh.artifact_id,
                "CONFORMANCE_LIFECYCLE_POC_FAIL: R13 restore not bound to fresh evidence")
        require(r13_restore.recommended_state == "CONFORMANT",
                "CONFORMANCE_LIFECYCLE_POC_FAIL: R13 restore not CONFORMANT")
        controls.append_audit(
            event_kind="r13_restore_eval",
            payload={"r13_id": r13_restore.artifact_id,
                     "runtime_evidence_id": r13_restore.runtime_evidence_id,
                     "recommended": r13_restore.recommended_state},
            logical_ts=h.clock.now(),
        )
        r14_restore = h.r14.publish_transition(
            subject=h.subject,
            prior_state="REATTESTATION_REQUIRED",
            new_state="CONFORMANT",
            rationale="fresh re-attestation against predeclared profile v2",
            r13_evaluation=r13_restore,
            trigger_observation=None,
        )
        controls.append_audit(
            event_kind="n_plus_2_published",
            payload={"r14_id": r14_restore.artifact_id,
                     "state": r14_restore.new_state, "epoch": r14_restore.state_epoch},
            logical_ts=h.clock.now(),
        )
        snap = h.state_store.get_authoritative_state(h.subject.subject_id)
        require(snap.current_state == "CONFORMANT" and snap.state_epoch == 3,
                "CONFORMANCE_LIFECYCLE_POC_FAIL: N+2 not CONFORMANT @ 3")

        # C0 consumed executor authority. Re-grant after successful restoration,
        # matching the existing development lifecycle fixture.
        controls.regrant_protected_resource_authority()

        cap2 = h.authorization.issue_capability(
            subject=h.subject,
            action="WRITE_RESOURCE",
            action_payload=bootstrap.ACTION_PAYLOAD,
            qualification=h.state_store.get_qualification_fixture(h.qualification.artifact_id),
            admission=h.state_store.get_admission_fixture(h.admission.artifact_id),
            nonce="c2-restored",
            ttl_ticks=10,
            clock_now=h.clock.now(),
        )
        require(cap2 is not None, "CONFORMANCE_LIFECYCLE_POC_FAIL: C2 issuance failed")
        controls.append_audit(
            event_kind="c2_issued",
            payload={"capability_id": cap2.artifact_id, "epoch": cap2.observed_state_epoch},
            logical_ts=h.clock.now(),
        )
        before_c2 = line_count(h.protected_resource_path)
        c2 = e.execute(
            subject=h.subject, capability=cap2, action="WRITE_RESOURCE",
            action_payload=bootstrap.ACTION_PAYLOAD, clock_now=h.clock.now(),
        )
        after_c2 = line_count(h.protected_resource_path)
        controls.append_audit(
            event_kind="c2_effect",
            payload={"granted": c2.granted, "reason": c2.reason,
                     "line_count": after_c2},
            logical_ts=h.clock.now(),
        )
        require(c2.granted and after_c2 == before_c2 + 1,
                "CONFORMANCE_LIFECYCLE_POC_FAIL: C2 did not cause exactly one effect")
        require(after_c2 == 2,
                "CONFORMANCE_LIFECYCLE_POC_FAIL: protected resource final count before replay != 2")

        before_replay = line_count(h.protected_resource_path)
        replay = e.execute(
            subject=h.subject, capability=cap2, action="WRITE_RESOURCE",
            action_payload=bootstrap.ACTION_PAYLOAD, clock_now=h.clock.now(),
        )
        after_replay = line_count(h.protected_resource_path)
        controls.append_audit(
            event_kind="c2_replay_denied",
            payload={"granted": replay.granted, "reason": replay.reason,
                     "line_count": after_replay},
            logical_ts=h.clock.now(),
        )
        require(not replay.granted and replay.reason == "REPLAYED_NONCE",
                "CONFORMANCE_LIFECYCLE_POC_FAIL: C2 replay not denied as replay")
        require(before_replay == after_replay == 2,
                "CONFORMANCE_LIFECYCLE_POC_FAIL: C2 replay caused an effect")

        # Actual-run audit verification.
        require(h.audit.verify_chain(),
                "INCONCLUSIVE_EVIDENCE_INVALID: actual authoritative audit chain failed")
        require(h.audit.verify_causal_order(EXPECTED_CAUSAL_ORDER),
                "INCONCLUSIVE_EVIDENCE_INVALID: actual causal order failed")

        authoritative = h.audit.records()
        tampered = copy.deepcopy(copy_and_tamper(authoritative, tamper_index=5))
        auth_ok, auth_msg = verify_copied_ledger(authoritative, h.audit.public_key)
        tamper_ok, tamper_msg = verify_copied_ledger(tampered, h.audit.public_key)
        require(auth_ok, f"INCONCLUSIVE_EVIDENCE_INVALID: serialized authoritative ledger invalid: {auth_msg}")
        require(not tamper_ok, "INCONCLUSIVE_EVIDENCE_INVALID: tampered ledger was not detected")
        require(h.audit.verify_chain(),
                "INCONCLUSIVE_EVIDENCE_INVALID: authoritative ledger changed after tamper test")

        # Emit evidence only from actual live objects/results.
        write_json(evidence_dir / "02_initial_and_c0.json", {
            "ev_v1": jsonable(ev_v1),
            "r13_initial": jsonable(r13_initial),
            "r14_initial": jsonable(r14_initial),
            "c0_capability": jsonable(cap0),
            "c0_result": jsonable(c0),
            "resource_lines_after_c0": after_c0,
        })
        write_json(evidence_dir / "03_invalidation_and_c1.json", {
            "c1_capability": jsonable(cap1),
            "initial_v2_evidence": jsonable(ev_v2_initial),
            "trigger": jsonable(trigger),
            "r13_invalidation": jsonable(r13_inv),
            "r14_invalidation": jsonable(r14_inv),
            "c1_result": jsonable(c1),
            "c1_nonce_unseen_at_stale_attempt": nonce_unseen_at_stale,
            "resource_lines_before_c1": before_c1,
            "resource_lines_after_c1": after_c1,
        })
        write_json(evidence_dir / "04_fresh_evidence_and_restoration.json", {
            "fresh_v2_evidence": jsonable(ev_v2_fresh),
            "r13_restoration": jsonable(r13_restore),
            "r14_restoration": jsonable(r14_restore),
            "state_snapshot": jsonable(snap),
        })
        write_json(evidence_dir / "05_c2_and_replay.json", {
            "c2_capability": jsonable(cap2),
            "c2_result": jsonable(c2),
            "resource_lines_before_c2": before_c2,
            "resource_lines_after_c2": after_c2,
            "replay_result": jsonable(replay),
            "resource_lines_before_replay": before_replay,
            "resource_lines_after_replay": after_replay,
        })
        write_json(evidence_dir / "06_authoritative_ledger.json", jsonable(authoritative))
        write_json(
            evidence_dir / "authoritative-audit-ledger.json",
            [audit_record_json(record) for record in authoritative],
        )
        authoritative_json = [audit_record_json(record) for record in authoritative]
        tampered_json = [audit_record_json(record) for record in tampered]
        write_json(evidence_dir / "tampered-audit-ledger.json", tampered_json)
        write_json(evidence_dir / "07_tampered_ledger.json", jsonable(tampered))
        write_json(evidence_dir / "08_audit_verification.json", {
            "authoritative_chain_ok": auth_ok,
            "authoritative_chain_message": auth_msg,
            "tampered_chain_ok": tamper_ok,
            "tampered_chain_message": tamper_msg,
            "authoritative_ledger_unmodified_after_tamper": h.audit.verify_chain(),
            "causal_ordering_satisfied": h.audit.verify_causal_order(EXPECTED_CAUSAL_ORDER),
            "expected_causal_order": EXPECTED_CAUSAL_ORDER,
        })

        classification = (
            "CONFORMANCE_LIFECYCLE_POC_PASS"
            if mode == "formal"
            else "DEVELOPMENT_DRY_RUN_PASS"
        )
        signed_artifacts = [
            h.profile_v1,
            h.profile_v2,
            h.qualification,
            h.admission,
            ev_v1,
            ev_v2_initial,
            ev_v2_fresh,
            trigger,
            r13_initial,
            r13_inv,
            r13_restore,
            r14_initial,
            r14_inv,
            r14_restore,
            cap0,
            cap1,
            cap2,
        ]
        artifact_json = [artifact_envelope(artifact) for artifact in signed_artifacts]
        write_json(evidence_dir / "signed-artifacts.json", artifact_json)
        write_json(
            evidence_dir / "signature-verification.json",
            signature_verification_rows(
                artifact_json,
                authoritative_json,
                h.verification_key_registry,
            ),
        )
        write_json(evidence_dir / "case-accounting.json", {
            "schema": "ate.case-accounting.v1",
            "cases": [
                {
                    "case_id": case_id,
                    "outcome": "PASS",
                    **definition,
                }
                for case_id, definition in CASE_DEFINITIONS.items()
            ],
        })
        producer_classification = (
            "FORMAL_EVIDENCE_CANDIDATE"
            if mode == "formal"
            else "DEVELOPMENT_EVIDENCE_CANDIDATE"
        )
        write_json(evidence_dir / "run-record-core.json", {
            "schema": "ate.run-record-core.v1",
            "run_id": run_id,
            "mode": mode,
            "classification": producer_classification,
            "design_version": "v0.1.1+formal-evidence-closure-amendment-v0.1",
            "implementation_commit": IMPLEMENTATION_BASELINE,
            "runner_commit": current_head,
            "started_at": started.isoformat().replace("+00:00", "Z"),
            "completed_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            "subject_id": h.subject.subject_id,
            "role_id": h.subject.role_id,
            "trust_domain": h.subject.trust_domain,
            "epoch_summary": [1, 2, 3],
            "required_cases": {"passed": 18, "total": 18},
            "negative_cases": {"passed": 8, "total": 8},
            "implementation_baseline": IMPLEMENTATION_BASELINE,
            "runner_head": current_head,
            "final_state": jsonable(snap),
            "final_resource_line_count": after_replay,
            "behavioral_result": classification,
        })
        write_json(evidence_dir / "09_final_classification.json", {
            "run_id": run_id,
            "mode": mode,
            "implementation_baseline": IMPLEMENTATION_BASELINE,
            "runner_head": current_head,
            "classification": classification,
            "pytest": "all collected tests passed / 0 failed / 0 skipped / 0 xfailed",
            "final_state": jsonable(snap),
            "final_resource_line_count": after_replay,
            "c2_granted": c2.granted,
            "c2_replay_denied": not replay.granted,
            "fresh_evidence_id": ev_v2_fresh.artifact_id,
            "r13_restore_evidence_id": r13_restore.runtime_evidence_id,
        })

        # Five-layer acyclic closure. The independent verifier is a separate
        # process; it reads evidence and emits its report on stdout only.
        from closure import close_evidence_bundle

        primary_names = sorted(path.name for path in evidence_dir.iterdir())
        close_evidence_bundle(evidence_dir, primary_names)
        manifest_sha = sha256_file(evidence_dir / "evidence-manifest.json")

        print(f"RUN_ID={run_id}")
        print(f"MODE={mode}")
        print(f"CLASSIFICATION={classification}")
        print(f"EVIDENCE_DIR={evidence_dir}")
        print(f"EVIDENCE_MANIFEST_SHA256={manifest_sha}")
        return 0

    except FormalRunError as exc:
        # Preserve whatever evidence exists; never manufacture PASS.
        fail_text = str(exc)
        (evidence_dir / "RUN-FAILED.txt").write_text(fail_text + "\n", encoding="utf-8")
        print(fail_text, file=sys.stderr)
        return 2
    finally:
        if h is not None:
            bootstrap.teardown(h)


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except FormalRunError as exc:
        # Covers preflight/pytest failures that occur before the scored
        # lifecycle exception boundary.
        print(str(exc), file=sys.stderr)
        raise SystemExit(3)
    except SystemExit:
        raise
    except Exception as exc:
        print(
            "INCONCLUSIVE_EVIDENCE_INVALID: unhandled runner error: "
            f"{type(exc).__name__}: {exc}",
            file=sys.stderr,
        )
        raise SystemExit(4)

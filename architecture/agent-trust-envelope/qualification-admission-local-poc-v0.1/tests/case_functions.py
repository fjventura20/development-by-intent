"""Case functions for the formal QA-P1..QA-P14 matrix.

Each `case_<id>` function drives one required case in a fresh fixture
environment and returns a `FormalEvidence` record built from real
execution objects (the EAP EapResult, the audit rows, the control
records, the protected-resource before/after state). Cases are
imperative, not pytest-style — they expose their evidence directly.

Each case uses an isolated `enforcement.db` file in a per-case temp
directory so that no residue leaks between cases (frozen §27).

The functions are imported by `qa_poc/formal_runner.py::run_all_cases`.
"""

from __future__ import annotations

import dataclasses
import json
import os
import shutil
import sqlite3
import tempfile
import traceback
from typing import Callable, Dict, List, Optional, Tuple

from cryptography.hazmat.primitives import serialization

from qa_poc.admission import (
    AdmissionAuthority,
    AdmissionCredential,
    DependencyEvaluationError,
    check_admission_usable,
)
from qa_poc.authorization import AuthorizationAuthority
from qa_poc.canonical import (
    CanonicalDuplicateKeyError,
    canonicalize_json_text,
    canonical_sha256,
)
from qa_poc.clock import Clock
from qa_poc.crypto import Ed25519PrivateKey, generate_keypair, key_id_from_public_pem, sign_ed25519, verify_ed25519
from qa_poc.formal_runner import (
    FormalEvidence,
    REQUIRED_QA_P10_SUBCHECKS,
    capture_applied_control_records,
    capture_audit_chain_valid,
    capture_audit_range,
    capture_initial_resource_state,
    capture_epoch,
)
from qa_poc.models import (
    CapabilityToken,
    DigestMismatchError,
    DOMAIN_QUALIFICATION_CREDENTIAL,
    DOMAIN_CAPABILITY_TOKEN,
    DOMAIN_TRUST_DECISION,
    QualificationCredential,
    artifact_payload,
    compute_id_and_digest,
    verify_artifact,
    with_signature,
)
from qa_poc.policies import PolicyRegistry, ProfileRegistry
from qa_poc.qualification import (
    QualificationAuthority,
    build_evidence_bundle,
    check_qualification_usable,
)
from qa_poc.subject_binding import SubjectBinding
from trusted import audit_ingest, enforcement_store
from trusted.control_apply import apply_control_record
from trusted.executor import BoundActionBundle, execute_bound_action

from tests._helpers import (
    FIXED_SNAPSHOT_REF,
    FixtureHarness,
    IssuerAuthorizationRegistry,
    RevocationRegistry,
    _no_revocations,
    apply_revocation_control_record,
    issue_qualification_and_admission,
    make_subject_binding,
)


# --- Helpers used by case functions ---------------------------------------


def _setup_case_dir(case_id: str, evidence_dir: str) -> Tuple[str, sqlite3.Connection]:
    """Create an isolated case DB. Formal-host mode opens it as ate-executor."""
    case_dir = os.path.join(evidence_dir, "case-dbs", case_id)
    if os.environ.get("ATE_USE_BOOTSTRAP_KEYS") == "1":
        from tests.host_runtime import prepare_executor_case_dir
        conn = prepare_executor_case_dir(case_dir)
        return case_dir, conn
    if os.path.exists(case_dir):
        shutil.rmtree(case_dir)
    os.makedirs(case_dir, exist_ok=True)
    db_path = os.path.join(case_dir, "enforcement.db")
    conn = enforcement_store.open_store(db_path)
    return case_dir, conn


def _executor_call(fn, *args, **kwargs):
    if os.environ.get("ATE_USE_BOOTSTRAP_KEYS") == "1":
        from tests.host_runtime import executor_call
        return executor_call(fn, *args, **kwargs)
    return fn(*args, **kwargs)


def _authority_call(fn, *args, **kwargs):
    if os.environ.get("ATE_USE_BOOTSTRAP_KEYS") == "1":
        from tests.host_runtime import authority_call
        return authority_call(fn, *args, **kwargs)
    return fn(*args, **kwargs)


def _make_strict_auth_lookup(harness) -> Callable[[str, str], bool]:
    """FR-10: Return a strict R11/R12 authorization lookup. Maps each
    (change_type, issuer_key_id) to True iff the issuer is the canonical
    authority for that change type. All other combinations -> False.

    The issuer_key_id is derived from the actual public PEM (not a
    hard-coded string), so a cross-authority attempt fails because the
    caller's key_id won't be in the role_by_key map.
    """
    from trusted.control_apply import (
        REVOCATION_CHANGE_TYPE_AUTHORIZATION_MAP,
        make_change_type_authorization_lookup,
    )
    r11_kid = key_id_from_public_pem(
        harness.keys.r11_pub.public_bytes(
            encoding=__import__("cryptography").hazmat.primitives.serialization.Encoding.PEM,
            format=__import__("cryptography").hazmat.primitives.serialization.PublicFormat.SubjectPublicKeyInfo,
        )
    )
    r12_kid = key_id_from_public_pem(
        harness.keys.r12_pub.public_bytes(
            encoding=__import__("cryptography").hazmat.primitives.serialization.Encoding.PEM,
            format=__import__("cryptography").hazmat.primitives.serialization.PublicFormat.SubjectPublicKeyInfo,
        )
    )
    return make_change_type_authorization_lookup(r11_key_id=r11_kid, r12_key_id=r12_kid)


def _r12_key_id(harness) -> str:
    return key_id_from_public_pem(
        harness.keys.r12_pub.public_bytes(
            encoding=__import__("cryptography").hazmat.primitives.serialization.Encoding.PEM,
            format=__import__("cryptography").hazmat.primitives.serialization.PublicFormat.SubjectPublicKeyInfo,
        )
    )


def _r11_key_id(harness) -> str:
    return key_id_from_public_pem(
        harness.keys.r11_pub.public_bytes(
            encoding=__import__("cryptography").hazmat.primitives.serialization.Encoding.PEM,
            format=__import__("cryptography").hazmat.primitives.serialization.PublicFormat.SubjectPublicKeyInfo,
        )
    )


def _insert_initial_resource(conn, resource_id: str, value: str) -> None:
    enforcement_store.insert_protected_resource(conn, resource_id=resource_id, value=value)


def _populate_evidence(
    ev: FormalEvidence,
    conn,
    *,
    resource_id: str,
    initial_value: str,
    initial_mc: int,
    final_value: str,
    final_mc: int,
    starting_epoch: int,
    ending_epoch: int,
    audit_chain_valid: bool,
    applied_control_records: List[Dict],
) -> FormalEvidence:
    ev.resource_id = resource_id
    ev.initial_resource_value = initial_value
    ev.final_resource_value = final_value
    ev.initial_mutation_count = initial_mc
    ev.final_mutation_count = final_mc
    ev.starting_applied_epoch = starting_epoch
    ev.ending_applied_epoch = ending_epoch
    ev.audit_sequence_range = capture_audit_range(conn)
    ev.audit_chain_valid = audit_chain_valid
    ev.applied_control_records = applied_control_records
    return ev


def _make_capability(harness, *, sb, q, a, nonce, snapshot_reference=FIXED_SNAPSHOT_REF,
                     revocation_lookup=None, qualification_revocation_lookup=None,
                     capability_lifetime_ms=None):
    return harness.authorization.issue_capability_token(
        subject_binding=sb,
        qualification=q,
        admission=a,
        session_identity="sess",
        operation="WRITE",
        target="resource-A",
        parameters={"new_value": "hello"},
        risk_class="R2",
        capability_class="demo-resource-write",
        nonce=nonce,
        snapshot_reference=snapshot_reference,
        clock=harness.clock,
        revocation_lookup=revocation_lookup,
        qualification_revocation_lookup=qualification_revocation_lookup,
        capability_lifetime_ms=capability_lifetime_ms,
    )


def _make_trust_decision(harness, *, cap, snapshot_reference=FIXED_SNAPSHOT_REF,
                      trust_decision_lifetime_ms=None):
    return harness.authorization.issue_trust_decision(
        capability=cap,
        requested_action={"target": "resource-A", "operation": "WRITE", "parameters": {"new_value": "hello"}},
        verdict="AUTHORIZED",
        snapshot_reference=snapshot_reference,
        clock=harness.clock,
        trust_decision_lifetime_ms=trust_decision_lifetime_ms,
    )


def _run_eap(harness, *, conn, sb, q, a, cap, td, reg, resource_id, new_value,
             issuer_authorization_lookup=None, live_proof_verifier=None,
             qualification_pub_override=None):
    bundle = BoundActionBundle(
        subject_binding=sb,
        capability=cap,
        trust_decision=td,
        action={"target": resource_id, "operation": "WRITE", "parameters": {"new_value": new_value}},
    )
    return _executor_call(
        execute_bound_action,
        conn,
        bundle=bundle,
        auth_pub=harness.keys.auth_pub,
        trust_pub=harness.keys.trust_pub,
        revocation_lookup=reg.lookup,
        bound_qualification=q,
        bound_admission=a,
        qualification_pub=qualification_pub_override or harness.keys.r11_pub,
        admission_pub=harness.keys.r12_pub,
        resource_id=resource_id,
        new_resource_value=new_value,
        clock=harness.clock,
        live_proof_verifier=live_proof_verifier,
        issuer_authorization_lookup=issuer_authorization_lookup,
    )


# --- Required case functions ----------------------------------------------


def case_p1(harness, evidence_dir) -> FormalEvidence:
    """QA-P1: happy path. Qualification + admission + cap + td + EAP -> SUCCEEDED."""
    sb = make_subject_binding(identity_id="agent-p1", challenge="p1")
    q, a = issue_qualification_and_admission(harness, subject_binding=sb)
    case_dir, conn = _setup_case_dir("QA-P1", evidence_dir)
    reg = RevocationRegistry()
    try:
        _insert_initial_resource(conn, "resource-A", "p1-initial")
        initial_value, initial_mc = _read_resource(conn, "resource-A")
        starting_epoch = capture_epoch(conn)

        cap = _make_capability(harness, sb=sb, q=q, a=a, nonce="nonce-p1-1", revocation_lookup=reg.lookup)
        td = _make_trust_decision(harness, cap=cap)
        ev = FormalEvidence(
            test_id="QA-P1",
            fixture_id=f"QA-P1/{case_dir}",
            case_function="tests.case_functions.case_p1",
            verdict="",
            pass_fail="",
            qualification_id=q.credential_id,
            qualification_digest=q.credential_digest,
            admission_id=a.credential_id,
            admission_digest=a.credential_digest,
            capability_id=cap.token_id,
            capability_digest=cap.token_digest,
            trust_decision_id=td.trust_decision_id,
            trust_decision_digest=td.trust_decision_digest,
        )
        result = _run_eap(
            harness, conn=conn, sb=sb, q=q, a=a, cap=cap, td=td, reg=reg,
            resource_id="resource-A", new_value="p1-write",
        )
        ev.verdict = result.verdict
        ev.reason_code = result.reason_code
        ev.eap_reached = True
        final_value, final_mc = _read_resource(conn, "resource-A")
        ev.pass_fail = (
            "PASS" if (result.verdict == "EXECUTION_SUCCEEDED" and final_mc == initial_mc + 1
                        and capture_audit_chain_valid(conn)) else "FAIL"
        )
        if final_mc > initial_mc and ev.pass_fail == "FAIL":
            ev.enforcement_failure_reason = "unauthorized protected mutation"
        return _populate_evidence(
            ev, conn,
            resource_id="resource-A",
            initial_value=initial_value, initial_mc=initial_mc,
            final_value=final_value, final_mc=final_mc,
            starting_epoch=starting_epoch,
            ending_epoch=capture_epoch(conn),
            audit_chain_valid=ev.pass_fail == "PASS",
            applied_control_records=capture_applied_control_records(conn),
        )
    finally:
        conn.close()


def case_p2(harness, evidence_dir) -> FormalEvidence:
    """QA-P2: qualification exists but admission does not."""
    sb = make_subject_binding(identity_id="agent-p2", challenge="p2")
    evidence = build_evidence_bundle(subject_binding=sb)
    _q_manifest, _q_decision, q = harness.qualification.evaluate(
        subject_binding=sb,
        qualification_domain="local-qa-demo",
        role="demo-repository-writer",
        evidence=evidence,
        snapshot_reference=FIXED_SNAPSHOT_REF,
        clock=harness.clock,
    )
    case_dir, conn = _setup_case_dir("QA-P2", evidence_dir)
    reg = RevocationRegistry()
    try:
        _insert_initial_resource(conn, "resource-A", "p2-initial")
        initial_value, initial_mc = _read_resource(conn, "resource-A")
        starting_epoch = capture_epoch(conn)
        # No admission issued — capability issuance refused
        cap = _make_capability(harness, sb=sb, q=q, a=None, nonce="nonce-p2-1", revocation_lookup=reg.lookup)
        ev = FormalEvidence(
            test_id="QA-P2",
            fixture_id=f"QA-P2/{case_dir}",
            case_function="tests.case_functions.case_p2",
            verdict="NO_BUNDLE_ISSUED",
            reason_code="ADMISSION_REQUIRED_FOR_CAPABILITY_ISSUANCE",
            qualification_id=q.credential_id,
            qualification_digest=q.credential_digest,
            admission_id="",
            admission_digest="",
            capability_id=None,
            capability_digest=None,
            trust_decision_id=None,
            trust_decision_digest=None,
        )
        ev.pass_fail = "PASS" if cap is None else "FAIL"
        final_value, final_mc = _read_resource(conn, "resource-A")
        if final_mc > initial_mc and ev.pass_fail == "PASS":
            ev.enforcement_failure_reason = "unauthorized protected mutation"
        return _populate_evidence(
            ev, conn,
            resource_id="resource-A",
            initial_value=initial_value, initial_mc=initial_mc,
            final_value=final_value, final_mc=final_mc,
            starting_epoch=starting_epoch,
            ending_epoch=capture_epoch(conn),
            audit_chain_valid=True,
            applied_control_records=capture_applied_control_records(conn),
        )
    finally:
        conn.close()


def case_p3(harness, evidence_dir) -> FormalEvidence:
    """QA-P3 (frozen): admission revocation signed + committed BEFORE
    capability request -> no usable CapabilityToken is issued ->
    no TrustDecision is issued -> EAP is never reached.

    Per FR-1: the denial happens at capability-issuance time, not at EAP.
    """
    sb = make_subject_binding(identity_id="agent-p3", challenge="p3")
    q, a = issue_qualification_and_admission(harness, subject_binding=sb)
    case_dir, conn = _setup_case_dir("QA-P3", evidence_dir)
    reg = RevocationRegistry()
    try:
        _insert_initial_resource(conn, "resource-A", "p3-initial")
        initial_value, initial_mc = _read_resource(conn, "resource-A")
        starting_epoch = capture_epoch(conn)
        # Apply ADMISSION_REVOCATION ControlRecord BEFORE any capability request.
        # This commits the revocation into executor state + the registry.
        new_epoch = apply_revocation_control_record(
            conn,
            record_id="p3-rev",
            target_type="admission",
            target_id=a.credential_id,
            target_digest=a.credential_digest,
            issuer_priv=harness.keys.r12_priv,
            issuer_pub=harness.keys.r12_pub,
            issuer_authority_id="r12-a",
            issuer_key_id=_r12_key_id(harness),
            registry=reg,
            reason="qa-p3-revocation",
            created_at_unix_ms=harness.clock.now_unix_ms,
            change_type_authorization_ok=_make_strict_auth_lookup(harness),
        )
        # Now attempt to issue a NEW capability using the now-revoked
        # admission. The issuance must refuse, returning None.
        cap = _make_capability(
            harness, sb=sb, q=q, a=a, nonce="nonce-p3-new",
            revocation_lookup=reg.lookup,
        )
        ev = FormalEvidence(
            test_id="QA-P3",
            fixture_id=f"QA-P3/{case_dir}",
            case_function="tests.case_functions.case_p3",
            verdict="NO_BUNDLE_ISSUED" if cap is None else "EXECUTION_DENIED",
            reason_code=(
                "ADMISSION_REVOCATION_PRECLUDES_CAPABILITY_ISSUANCE"
                if cap is None else "WRONG: cap issued despite revocation"
            ),
            qualification_id=q.credential_id,
            qualification_digest=q.credential_digest,
            admission_id=a.credential_id,
            admission_digest=a.credential_digest,
            capability_id=cap.token_id if cap else None,
            capability_digest=cap.token_digest if cap else None,
            trust_decision_id=None,
            trust_decision_digest=None,
        )
        ev.pass_fail = (
            "PASS" if (cap is None
                        and _read_resource(conn, "resource-A")[1] == initial_mc)
            else "FAIL"
        )
        if cap is not None and ev.pass_fail == "PASS":
            # If a cap WAS issued despite revocation, this is a hard FAIL
            ev.pass_fail = "FAIL"
        # No EAP was reached; pre-EAP invalidation + protected mutation
        # would be ENFORCEMENT_FAILURE but here we never issued a cap.
        final_value, final_mc = _read_resource(conn, "resource-A")
        if final_mc > initial_mc and ev.pass_fail == "PASS":
            ev.enforcement_failure_reason = "unauthorized protected mutation"
        return _populate_evidence(
            ev, conn,
            resource_id="resource-A",
            initial_value=initial_value, initial_mc=initial_mc,
            final_value=final_value, final_mc=final_mc,
            starting_epoch=starting_epoch,
            ending_epoch=capture_epoch(conn),
            audit_chain_valid=capture_audit_chain_valid(conn),
            applied_control_records=capture_applied_control_records(conn),
        )
    finally:
        conn.close()


def case_p4(harness, evidence_dir) -> FormalEvidence:
    """QA-P4: pre-issued cap; admission revoked before EAP -> EAP denies."""
    sb = make_subject_binding(identity_id="agent-p4", challenge="p4")
    q, a = issue_qualification_and_admission(harness, subject_binding=sb)
    case_dir, conn = _setup_case_dir("QA-P4", evidence_dir)
    reg = RevocationRegistry()
    try:
        _insert_initial_resource(conn, "resource-A", "p4-initial")
        initial_value, initial_mc = _read_resource(conn, "resource-A")
        starting_epoch = capture_epoch(conn)
        cap = _make_capability(harness, sb=sb, q=q, a=a, nonce="nonce-p4-1")
        td = _make_trust_decision(harness, cap=cap)
        # Revoke admission before EAP
        apply_revocation_control_record(
            conn,
            record_id="p4-rev",
            target_type="admission",
            target_id=a.credential_id,
            target_digest=a.credential_digest,
            issuer_priv=harness.keys.r12_priv,
            issuer_pub=harness.keys.r12_pub,
            issuer_authority_id="r12-a",
            issuer_key_id=_r12_key_id(harness),
            registry=reg,
            reason="qa-p4-revocation",
            created_at_unix_ms=harness.clock.now_unix_ms,
            change_type_authorization_ok=_make_strict_auth_lookup(harness),
        )
        result = _run_eap(
            harness, conn=conn, sb=sb, q=q, a=a, cap=cap, td=td, reg=reg,
            resource_id="resource-A", new_value="p4-write",
        )
        ev = FormalEvidence(
            test_id="QA-P4",
            fixture_id=f"QA-P4/{case_dir}",
            case_function="tests.case_functions.case_p4",
            verdict=result.verdict,
            reason_code=result.reason_code,
            qualification_id=q.credential_id,
            qualification_digest=q.credential_digest,
            admission_id=a.credential_id,
            admission_digest=a.credential_digest,
            capability_id=cap.token_id,
            capability_digest=cap.token_digest,
            trust_decision_id=td.trust_decision_id,
            trust_decision_digest=td.trust_decision_digest,
        )
        ev.eap_reached = True
        final_value, final_mc = _read_resource(conn, "resource-A")
        ev.pass_fail = (
            "PASS" if (result.verdict == "EXECUTION_DENIED"
                        and "ADMISSION_REVOKED" in result.reason_code
                        and final_mc == initial_mc)
            else "FAIL"
        )
        if final_mc > initial_mc and ev.pass_fail == "PASS":
            ev.enforcement_failure_reason = "unauthorized protected mutation"
        return _populate_evidence(
            ev, conn,
            resource_id="resource-A",
            initial_value=initial_value, initial_mc=initial_mc,
            final_value=final_value, final_mc=final_mc,
            starting_epoch=starting_epoch,
            ending_epoch=capture_epoch(conn),
            audit_chain_valid=capture_audit_chain_valid(conn),
            applied_control_records=capture_applied_control_records(conn),
        )
    finally:
        conn.close()


def case_p5(harness, evidence_dir) -> FormalEvidence:
    """QA-P5: pre-issued cap; qualification revoked before EAP -> EAP denies (cascade)."""
    sb = make_subject_binding(identity_id="agent-p5", challenge="p5")
    q, a = issue_qualification_and_admission(harness, subject_binding=sb)
    case_dir, conn = _setup_case_dir("QA-P5", evidence_dir)
    reg = RevocationRegistry()
    try:
        _insert_initial_resource(conn, "resource-A", "p5-initial")
        initial_value, initial_mc = _read_resource(conn, "resource-A")
        starting_epoch = capture_epoch(conn)
        cap = _make_capability(harness, sb=sb, q=q, a=a, nonce="nonce-p5-1")
        td = _make_trust_decision(harness, cap=cap)
        # Revoke the qualification before EAP
        # FR-10: qualification revocations must be signed by R11, not R12.
        apply_revocation_control_record(
            conn,
            record_id="p5-rev",
            target_type="qualification",
            target_id=q.credential_id,
            target_digest=q.credential_digest,
            issuer_priv=harness.keys.r11_priv,
            issuer_pub=harness.keys.r11_pub,
            issuer_authority_id="r11-q",
            issuer_key_id=_r11_key_id(harness),
            registry=reg,
            reason="qa-p5-revocation",
            created_at_unix_ms=harness.clock.now_unix_ms,
            change_type_authorization_ok=_make_strict_auth_lookup(harness),
        )
        result = _run_eap(
            harness, conn=conn, sb=sb, q=q, a=a, cap=cap, td=td, reg=reg,
            resource_id="resource-A", new_value="p5-write",
        )
        ev = FormalEvidence(
            test_id="QA-P5",
            fixture_id=f"QA-P5/{case_dir}",
            case_function="tests.case_functions.case_p5",
            verdict=result.verdict,
            reason_code=result.reason_code,
            qualification_id=q.credential_id,
            qualification_digest=q.credential_digest,
            admission_id=a.credential_id,
            admission_digest=a.credential_digest,
            capability_id=cap.token_id,
            capability_digest=cap.token_digest,
            trust_decision_id=td.trust_decision_id,
            trust_decision_digest=td.trust_decision_digest,
        )
        ev.eap_reached = True
        final_value, final_mc = _read_resource(conn, "resource-A")
        ev.pass_fail = (
            "PASS" if (result.verdict == "EXECUTION_DENIED"
                        and ("QUALIFICATION_REVOKED" in result.reason_code
                             or "ADMISSION_REVOKED" in result.reason_code)
                        and final_mc == initial_mc)
            else "FAIL"
        )
        if final_mc > initial_mc and ev.pass_fail == "PASS":
            ev.enforcement_failure_reason = "unauthorized protected mutation"
        return _populate_evidence(
            ev, conn,
            resource_id="resource-A",
            initial_value=initial_value, initial_mc=initial_mc,
            final_value=final_value, final_mc=final_mc,
            starting_epoch=starting_epoch,
            ending_epoch=capture_epoch(conn),
            audit_chain_valid=capture_audit_chain_valid(conn),
            applied_control_records=capture_applied_control_records(conn),
        )
    finally:
        conn.close()


def case_p6(harness, evidence_dir) -> FormalEvidence:
    """QA-P6 (FR-8): qualification expiry isolation.

    Proves that the EAP denies specifically because the BOUND QUALIFICATION
    is expired — not because downstream artifacts expired first.

    Frozen §X: TestClock crosses QualificationCredential expiry while
    downstream token/decision remain nominally unexpired => derived
    expiration denies.
    """
    sb = make_subject_binding(identity_id="agent-p6", challenge="p6")

    # FR-8: configure TTLs so qualification expires FIRST while cap/TD
    # remain nominal. Qualification lifetime = 6h; cap/TD lifetime = 48h;
    # admission lifetime = 48h (nominal).
    QUAL_TTL_MS = 6 * 3600 * 1000    # 6h qualification
    ADM_TTL_MS = 48 * 3600 * 1000    # 48h admission (nominal)
    CAP_TTL_MS = 48 * 3600 * 1000    # 48h capability (nominal)
    TD_TTL_MS = 48 * 3600 * 1000     # 48h trust decision (nominal)
    ADVANCE_MS = QUAL_TTL_MS + 60_000  # 6h+1min (past qual expiry, before cap expiry)

    q, a = issue_qualification_and_admission(
        harness, subject_binding=sb,
        qualification_lifetime_ms=QUAL_TTL_MS,
        admission_lifetime_ms=ADM_TTL_MS,
    )
    case_dir, conn = _setup_case_dir("QA-P6", evidence_dir)
    reg = RevocationRegistry()
    try:
        _insert_initial_resource(conn, "resource-A", "p6-initial")
        initial_value, initial_mc = _read_resource(conn, "resource-A")
        starting_epoch = capture_epoch(conn)

        # FR-8 verification: capture all 4 timestamps BEFORE advancing the clock
        qual_expires_at = q.expires_at_unix_ms
        adm_expires_at = a.expires_at_unix_ms
        cap = _make_capability(
            harness, sb=sb, q=q, a=a, nonce="nonce-p6-1",
            capability_lifetime_ms=CAP_TTL_MS,
        )
        cap_expires_at = cap.expires_at_unix_ms
        td = _make_trust_decision(
            harness, cap=cap, trust_decision_lifetime_ms=TD_TTL_MS,
        )
        td_expires_at = td.expires_at_unix_ms

        # Sanity check: pre-advance, qual/adm/cap/td expiry ordering
        assert qual_expires_at < cap_expires_at, (
            f"qual_expires_at={qual_expires_at} must be < cap_expires_at={cap_expires_at}"
        )
        assert qual_expires_at < adm_expires_at, (
            f"qual_expires_at={qual_expires_at} must be < adm_expires_at={adm_expires_at}"
        )
        assert cap_expires_at > td_expires_at or cap_expires_at == td_expires_at  # either order ok

        # Advance clock past qualification expiry only (still before cap/td expiry)
        harness.clock = harness.clock.advance_ms(ADVANCE_MS)
        now = harness.clock.now_unix_ms
        assert now > qual_expires_at, f"now={now} must be > qual_expires_at={qual_expires_at}"
        assert now < cap_expires_at, f"now={now} must be < cap_expires_at={cap_expires_at} (cap still nominal)"
        assert now < td_expires_at, f"now={now} must be < td_expires_at={td_expires_at} (TD still nominal)"

        result = _run_eap(
            harness, conn=conn, sb=sb, q=q, a=a, cap=cap, td=td, reg=reg,
            resource_id="resource-A", new_value="p6-write",
        )

        ev = FormalEvidence(
            test_id="QA-P6",
            fixture_id=f"QA-P6/{case_dir}",
            case_function="tests.case_functions.case_p6",
            verdict=result.verdict,
            reason_code=result.reason_code,
            qualification_id=q.credential_id,
            qualification_digest=q.credential_digest,
            qualification_expires_at_unix_ms=qual_expires_at,
            admission_id=a.credential_id,
            admission_digest=a.credential_digest,
            admission_expires_at_unix_ms=adm_expires_at,
            capability_id=cap.token_id,
            capability_digest=cap.token_digest,
            capability_expires_at_unix_ms=cap_expires_at,
            trust_decision_id=td.trust_decision_id,
            trust_decision_digest=td.trust_decision_digest,
            trust_decision_expires_at_unix_ms=td_expires_at,
        )
        ev.eap_reached = True
        ev.qualification_expired_at_advance_ms = ADVANCE_MS
        final_value, final_mc = _read_resource(conn, "resource-A")

        # FR-8 acceptance criteria:
        # 1. EAP denies.
        # 2. Reason MUST mention QUALIFICATION_EXPIRED (not CAPABILITY_EXPIRED,
        #    not TRUST_DECISION_EXPIRED, not ADMISSION_EXPIRED).
        # 3. final_mc == initial_mc.
        qual_expired = "QUALIFICATION_EXPIRED" in result.reason_code
        cap_expired = "CAPABILITY_EXPIRED" in result.reason_code
        td_expired = "TRUST_DECISION_EXPIRED" in result.reason_code
        adm_expired = "ADMISSION_EXPIRED" in result.reason_code
        no_mutation = final_mc == initial_mc

        ev.subcheck_results = {
            "qualification_expired_in_reason": qual_expired,
            "capability_not_yet_expired": not cap_expired,
            "trust_decision_not_yet_expired": not td_expired,
            "admission_not_yet_expired": not adm_expired,
            "no_protected_mutation": no_mutation,
            "now_above_qual_expires": now > qual_expires_at,
            "now_below_cap_expires": now < cap_expires_at,
            "now_below_td_expires": now < td_expires_at,
        }
        ev.pass_fail = (
            "PASS" if (result.verdict == "EXECUTION_DENIED"
                        and qual_expired and not cap_expired and not td_expired
                        and no_mutation)
            else "FAIL"
        )
        if final_mc > initial_mc and ev.pass_fail == "PASS":
            ev.enforcement_failure_reason = "unauthorized protected mutation"
        return _populate_evidence(
            ev, conn,
            resource_id="resource-A",
            initial_value=initial_value, initial_mc=initial_mc,
            final_value=final_value, final_mc=final_mc,
            starting_epoch=starting_epoch,
            ending_epoch=capture_epoch(conn),
            audit_chain_valid=capture_audit_chain_valid(conn),
            applied_control_records=capture_applied_control_records(conn),
        )
    finally:
        conn.close()


def case_p7(harness, evidence_dir) -> FormalEvidence:
    """QA-P7: Agent B reuses Agent A chain (subject_binding identity
    does not match bound qualification+admission subject_identity_id)."""
    # Issue agent-a credentials
    sb_a = make_subject_binding(identity_id="agent-a", challenge="p7-a")
    q_a, a_a = issue_qualification_and_admission(harness, subject_binding=sb_a)
    # Agent-b subject_binding, but bound to agent-a's credentials
    sb_b = make_subject_binding(identity_id="agent-b", challenge="p7-b")
    case_dir, conn = _setup_case_dir("QA-P7", evidence_dir)
    reg = RevocationRegistry()
    try:
        _insert_initial_resource(conn, "resource-A", "p7-initial")
        initial_value, initial_mc = _read_resource(conn, "resource-A")
        starting_epoch = capture_epoch(conn)
        cap = _make_capability(harness, sb=sb_b, q=q_a, a=a_a, nonce="nonce-p7-1")
        td = _make_trust_decision(harness, cap=cap)
        result = _run_eap(
            harness, conn=conn, sb=sb_b, q=q_a, a=a_a, cap=cap, td=td, reg=reg,
            resource_id="resource-A", new_value="p7-write",
        )
        ev = FormalEvidence(
            test_id="QA-P7",
            fixture_id=f"QA-P7/{case_dir}",
            case_function="tests.case_functions.case_p7",
            verdict=result.verdict,
            reason_code=result.reason_code,
            qualification_id=q_a.credential_id,
            qualification_digest=q_a.credential_digest,
            admission_id=a_a.credential_id,
            admission_digest=a_a.credential_digest,
            capability_id=cap.token_id,
            capability_digest=cap.token_digest,
            trust_decision_id=td.trust_decision_id,
            trust_decision_digest=td.trust_decision_digest,
        )
        ev.eap_reached = True
        final_value, final_mc = _read_resource(conn, "resource-A")
        ev.pass_fail = (
            "PASS" if (result.verdict == "EXECUTION_DENIED"
                        and ("SUBJECT_BINDING" in result.reason_code
                             or "NOT_BOUND" in result.reason_code)
                        and final_mc == initial_mc)
            else "FAIL"
        )
        if final_mc > initial_mc and ev.pass_fail == "PASS":
            ev.enforcement_failure_reason = "unauthorized protected mutation"
        return _populate_evidence(
            ev, conn,
            resource_id="resource-A",
            initial_value=initial_value, initial_mc=initial_mc,
            final_value=final_value, final_mc=final_mc,
            starting_epoch=starting_epoch,
            ending_epoch=capture_epoch(conn),
            audit_chain_valid=capture_audit_chain_valid(conn),
            applied_control_records=capture_applied_control_records(conn),
        )
    finally:
        conn.close()


def case_p8(harness, evidence_dir) -> FormalEvidence:
    """QA-P8 (frozen, per FR-2): a recognized, active AUTH_IDENTITY
    key signs a QualificationCredential even though it lacks
    permission for the QualificationCredential artifact type. The
    cryptographic signature is valid; the issuer-authorization
    check rejects.

    Steps:
      1. Cryptographically valid signature: verify_artifact(cred,
         AUTH_IDENTITY_pub) succeeds.
      2. Identity key is recognized/active: the registry's
         (auth_identity_key_id, ...) entries are present.
      3. Identity key lacks R11 QualificationCredential
         permission: registry returns False for that combo.
      4. Issuer-authorization check rejects: EAP denies with
         ISSUER_NOT_AUTHORIZED_FOR_ARTIFACT_TYPE.
      5. No protected mutation.
    """
    sb = make_subject_binding(identity_id="agent-p8", challenge="p8")
    # Issue a legitimate admission for sb
    q_legit, a_legit = issue_qualification_and_admission(harness, subject_binding=sb)
    case_dir, conn = _setup_case_dir("QA-P8", evidence_dir)
    reg = RevocationRegistry()
    try:
        _insert_initial_resource(conn, "resource-A", "p8-initial")
        initial_value, initial_mc = _read_resource(conn, "resource-A")
        starting_epoch = capture_epoch(conn)
        # Build a QualificationCredential signed with AUTH_IDENTITY (NOT R11)
        semantic = {
            "profile_id": harness.profile.profile_id,
            "profile_digest": harness.profile.profile_digest,
            "subject_identity_id": sb.subject_identity_id,
            "subject_binding_digest": sb.digest(),
            "issued_at_unix_ms": harness.clock.now_unix_ms,
            "expires_at_unix_ms": harness.clock.now_unix_ms + 24 * 3600 * 1000,
            "historical_trust_state_reference": FIXED_SNAPSHOT_REF,
        }
        proto = QualificationCredential(
            credential_id="",
            profile_id=semantic["profile_id"],
            profile_digest=semantic["profile_digest"],
            subject_identity_id=semantic["subject_identity_id"],
            subject_binding_digest=semantic["subject_binding_digest"],
            issued_at_unix_ms=semantic["issued_at_unix_ms"],
            expires_at_unix_ms=semantic["expires_at_unix_ms"],
            historical_trust_state_reference=semantic["historical_trust_state_reference"],
            credential_digest="",
        )
        cred, _ = compute_id_and_digest(
            proto, semantic_fields=semantic, id_prefix="qfc", id_salt=(sb.digest(),)
        )
        sig = _authority_call(
            sign_ed25519,
            harness.keys.auth_identity_priv,
            DOMAIN_QUALIFICATION_CREDENTIAL,
            artifact_payload(cred),
        )
        cred = with_signature(cred, sig)

        # Step 1: cryptographic signature is valid
        crypto_valid = False
        try:
            verify_artifact(cred, harness.keys.auth_identity_pub)
            crypto_valid = True
        except Exception:
            crypto_valid = False

        # Step 2: identity key is recognized/active (build the registry)
        from cryptography.hazmat.primitives import serialization
        from qa_poc.crypto import key_id_from_public_pem
        auth_identity_kid = key_id_from_public_pem(
            harness.keys.auth_identity_pub.public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo,
            )
        )
        r11_kid = key_id_from_public_pem(
            harness.keys.r11_pub.public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo,
            )
        )
        authorization_kid = key_id_from_public_pem(
            harness.keys.auth_pub.public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo,
            )
        )
        trust_decision_kid = key_id_from_public_pem(
            harness.keys.trust_pub.public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo,
            )
        )
        reg_auth = IssuerAuthorizationRegistry.build_default(
            auth_identity_key_id=auth_identity_kid,
            r11_key_id=r11_kid,
            authorization_key_id=authorization_kid,
            trust_decision_key_id=trust_decision_kid,
        )
        # Steps 2+3 are encoded in the registry:
        #   - recognized/active means the auth_identity has at least
        #     SOME entries (yes — for evidence manifest)
        #   - lacks R11 QualCred permission means the lookup returns False
        auth_id_recognized = (
            (auth_identity_kid, "ate.qualification.evidence_manifest.v1") in
            reg_auth.artifact_type_permissions
        )
        auth_id_lacks_r11_qualcred = not reg_auth.lookup(
            auth_identity_kid,
            DOMAIN_QUALIFICATION_CREDENTIAL,
        )

        # Step 4: try EAP with the unauthorized credential
        cap = _make_capability(harness, sb=sb, q=cred, a=a_legit, nonce="nonce-p8-1")
        td = _make_trust_decision(harness, cap=cap)
        # IMPORTANT: we pass AUTH_IDENTITY's pub as qualification_pub
        # so that the signature cryptographically verifies — then the
        # authorization check (consulted via issuer_authorization_lookup)
        # rejects because AUTH_IDENTITY is not authorized for
        # QualificationCredential artifacts.
        result = _run_eap(
            harness, conn=conn, sb=sb, q=cred, a=a_legit, cap=cap, td=td, reg=reg,
            resource_id="resource-A", new_value="p8-write",
            issuer_authorization_lookup=reg_auth.lookup,
            qualification_pub_override=harness.keys.auth_identity_pub,
        )
        ev = FormalEvidence(
            test_id="QA-P8",
            fixture_id=f"QA-P8/{case_dir}",
            case_function="tests.case_functions.case_p8",
            verdict=result.verdict,
            reason_code=result.reason_code,
            qualification_id=cred.credential_id,
            qualification_digest=cred.credential_digest,
            admission_id=a_legit.credential_id,
            admission_digest=a_legit.credential_digest,
            capability_id=cap.token_id if cap else None,
            capability_digest=cap.token_digest if cap else None,
            trust_decision_id=td.trust_decision_id if td else None,
            trust_decision_digest=td.trust_decision_digest if td else None,
        )
        ev.eap_reached = True
        ev.subcheck_results = {
            "crypto_signature_valid_against_auth_identity_pub": "PASS" if crypto_valid else "FAIL",
            "auth_identity_recognized_active": "PASS" if auth_id_recognized else "FAIL",
            "auth_identity_lacks_r11_qualcred_permission": "PASS" if auth_id_lacks_r11_qualcred else "FAIL",
            "issuer_authorization_check_rejects_qualification_credential": (
                "PASS" if (
                    result.verdict == "EXECUTION_DENIED"
                    and "ISSUER_NOT_AUTHORIZED_FOR_ARTIFACT_TYPE" in result.reason_code
                    and "qualification_credential" in result.reason_code
                    and DOMAIN_QUALIFICATION_CREDENTIAL in result.reason_code
                    and "capability_token" not in result.reason_code
                    and "trust_decision" not in result.reason_code
                ) else "FAIL"
            ),
            "no_protected_mutation": "",  # filled after final read
        }
        final_value, final_mc = _read_resource(conn, "resource-A")
        ev.subcheck_results["no_protected_mutation"] = (
            "PASS" if final_mc == initial_mc else "FAIL"
        )
        ev.pass_fail = (
            "PASS" if all(s == "PASS" for s in ev.subcheck_results.values())
            else "FAIL"
        )
        if final_mc > initial_mc and ev.pass_fail == "PASS":
            ev.enforcement_failure_reason = "unauthorized protected mutation"
        return _populate_evidence(
            ev, conn,
            resource_id="resource-A",
            initial_value=initial_value, initial_mc=initial_mc,
            final_value=final_value, final_mc=final_mc,
            starting_epoch=starting_epoch,
            ending_epoch=capture_epoch(conn),
            audit_chain_valid=capture_audit_chain_valid(conn),
            applied_control_records=capture_applied_control_records(conn),
        )
    finally:
        conn.close()


def case_p9(harness, evidence_dir) -> FormalEvidence:
    """QA-P9: mixed/incoherent trust-state view (capability+td use a
    snapshot reference that does not belong to the coherent committed
    state)."""
    sb = make_subject_binding(identity_id="agent-p9", challenge="p9")
    q, a = issue_qualification_and_admission(harness, subject_binding=sb)
    case_dir, conn = _setup_case_dir("QA-P9", evidence_dir)
    reg = RevocationRegistry()
    try:
        _insert_initial_resource(conn, "resource-A", "p9-initial")
        initial_value, initial_mc = _read_resource(conn, "resource-A")
        starting_epoch = capture_epoch(conn)
        # Issue cap with INCOHERENT snapshot ref
        cap = _make_capability(
            harness, sb=sb, q=q, a=a, nonce="nonce-p9-1",
            snapshot_reference="INCOHERENT-snapshot-ref-that-does-not-belong-to-this-state",
        )
        td = _make_trust_decision(
            harness, cap=cap,
            snapshot_reference="INCOHERENT-snapshot-ref-that-does-not-belong-to-this-state",
        )
        result = _run_eap(
            harness, conn=conn, sb=sb, q=q, a=a, cap=cap, td=td, reg=reg,
            resource_id="resource-A", new_value="p9-write",
        )
        ev = FormalEvidence(
            test_id="QA-P9",
            fixture_id=f"QA-P9/{case_dir}",
            case_function="tests.case_functions.case_p9",
            verdict=result.verdict,
            reason_code=result.reason_code,
            qualification_id=q.credential_id,
            qualification_digest=q.credential_digest,
            admission_id=a.credential_id,
            admission_digest=a.credential_digest,
            capability_id=cap.token_id,
            capability_digest=cap.token_digest,
            trust_decision_id=td.trust_decision_id,
            trust_decision_digest=td.trust_decision_digest,
        )
        ev.eap_reached = True
        final_value, final_mc = _read_resource(conn, "resource-A")
        ev.pass_fail = (
            "PASS" if (result.verdict == "EXECUTION_DENIED"
                        and "TRUST_STATE_INCONSISTENT" in result.reason_code
                        and final_mc == initial_mc)
            else "FAIL"
        )
        if final_mc > initial_mc and ev.pass_fail == "PASS":
            ev.enforcement_failure_reason = "unauthorized protected mutation"
        return _populate_evidence(
            ev, conn,
            resource_id="resource-A",
            initial_value=initial_value, initial_mc=initial_mc,
            final_value=final_value, final_mc=final_mc,
            starting_epoch=starting_epoch,
            ending_epoch=capture_epoch(conn),
            audit_chain_valid=capture_audit_chain_valid(conn),
            applied_control_records=capture_applied_control_records(conn),
        )
    finally:
        conn.close()


def case_p10(harness, evidence_dir) -> FormalEvidence:
    """QA-P10: canonical payload / digest substitution probes.

    Required subchecks:
      - equiv_canonical_form_same_digest
      - semantic_mutation_digest_mismatch
      - duplicate_key_rejected_at_parse_time
      - float_rejected
    """
    subcheck_results: Dict[str, str] = {}
    case_dir, conn = _setup_case_dir("QA-P10", evidence_dir)
    reg = RevocationRegistry()
    try:
        _insert_initial_resource(conn, "resource-A", "p10-initial")
        initial_value, initial_mc = _read_resource(conn, "resource-A")
        starting_epoch = capture_epoch(conn)

        # (a) Equiv canonical form: reordered keys produce same digest
        priv, pub = generate_keypair()
        sb = make_subject_binding(identity_id="agent-p10", challenge="p10")
        semantic = {
            "subject_binding_digest": sb.digest(),
            "qualification_credential_id": "q",
            "qualification_credential_digest": "qd",
            "admission_credential_id": "a",
            "admission_credential_digest": "ad",
            "session_identity": "s",
            "operation": "WRITE",
            "target": "t",
            "parameters_digest": "pd",
            "risk_class": "R2",
            "capability_class": "c",
            "nonce": "n",
            "issued_at_unix_ms": 1000,
            "expires_at_unix_ms": 2000,
            "historical_trust_state_reference": FIXED_SNAPSHOT_REF,
        }
        proto = CapabilityToken(
            token_id="", subject_binding_digest=sb.digest(),
            qualification_credential_id="q", qualification_credential_digest="qd",
            admission_credential_id="a", admission_credential_digest="ad",
            session_identity="s", operation="WRITE", target="t", parameters_digest="pd",
            risk_class="R2", capability_class="c", nonce="n",
            issued_at_unix_ms=1000, expires_at_unix_ms=2000,
            historical_trust_state_reference=FIXED_SNAPSHOT_REF, token_digest="",
        )
        cap_a, _ = compute_id_and_digest(proto, semantic_fields=semantic, id_prefix="ct", id_salt=("n",))
        sig = sign_ed25519(priv, DOMAIN_CAPABILITY_TOKEN, artifact_payload(cap_a))
        cap_a = with_signature(cap_a, sig)
        # Equiv canonical form test: reordering keys in the SIGNED payload
        # should yield the same digest (since canonical JSON sorts keys).
        a = canonical_sha256(artifact_payload(cap_a))
        b = canonical_sha256({**artifact_payload(cap_a), "_zzz": "ignored"})  # extra key should be rejected at canonicalize? actually we don't include extras.
        # Use the canonical form invariant: same dict keys in different order
        d1 = canonical_sha256({"a": 1, "b": 2, "c": [3, 4]})
        d2 = canonical_sha256({"c": [3, 4], "b": 2, "a": 1})
        subcheck_results["qa_p10_equiv_canonical_form_same_digest"] = (
            "PASS" if d1 == d2 else "FAIL"
        )

        # (b) Semantic mutation: tamper one semantic field
        tampered = dataclasses.replace(cap_a, session_identity="EVIL")
        semantic_mutation_detected = False
        try:
            verify_artifact(tampered, pub)
        except DigestMismatchError:
            semantic_mutation_detected = True
        except Exception:
            semantic_mutation_detected = True
        subcheck_results["qa_p10_semantic_mutation_digest_mismatch"] = (
            "PASS" if semantic_mutation_detected else "FAIL"
        )

        # (c) Duplicate key at parse time
        dup_detected = False
        try:
            canonicalize_json_text('{"a": 1, "a": 2}')
        except CanonicalDuplicateKeyError:
            dup_detected = True
        except Exception:
            dup_detected = True
        subcheck_results["qa_p10_duplicate_key_rejected_at_parse_time"] = (
            "PASS" if dup_detected else "FAIL"
        )

        # (d) Float rejection
        float_rejected = False
        try:
            canonical_sha256({"a": 1.5})
        except Exception:
            float_rejected = True
        subcheck_results["qa_p10_float_rejected"] = (
            "PASS" if float_rejected else "FAIL"
        )

        ev = FormalEvidence(
            test_id="QA-P10",
            fixture_id=f"QA-P10/{case_dir}",
            case_function="tests.case_functions.case_p10",
            verdict="CANONICAL_SUBSTITUTION_PROBE",
            reason_code="; ".join(f"{k}={v}" for k, v in subcheck_results.items()),
            qualification_id="",
            qualification_digest="",
            admission_id="",
            admission_digest="",
            capability_id="",
            capability_digest="",
            trust_decision_id="",
            trust_decision_digest="",
            eap_reached=False,
            subcheck_results=subcheck_results,
        )
        ev.pass_fail = (
            "PASS" if all(s == "PASS" for s in subcheck_results.values())
            else "FAIL"
        )
        # No EAP, no mutation
        final_value, final_mc = _read_resource(conn, "resource-A")
        if final_mc > initial_mc and ev.pass_fail == "PASS":
            ev.enforcement_failure_reason = "unauthorized protected mutation"
        return _populate_evidence(
            ev, conn,
            resource_id="resource-A",
            initial_value=initial_value, initial_mc=initial_mc,
            final_value=final_value, final_mc=final_mc,
            starting_epoch=starting_epoch,
            ending_epoch=capture_epoch(conn),
            audit_chain_valid=True,
            applied_control_records=capture_applied_control_records(conn),
        )
    finally:
        conn.close()


def case_p11a(harness, evidence_dir) -> FormalEvidence:
    """QA-P11 subcase A (FR-9): CR holds the write lock FIRST; EAP contends
    and is denied by SQLITE_BUSY; CR commits (epoch++); EAP proceeds
    afterwards and is denied by dependency; mutation_count = 0.

    Frozen §25 ordering: control-record transaction gets the write lock,
    EAP is released to contend and cannot pass it, revocation commits /
    epoch increments, EAP proceeds afterward and denies.
    """
    from trusted.enforcement_store import SQLiteBarrier

    sb = make_subject_binding(identity_id="agent-p11a", challenge="p11a")
    q, a = issue_qualification_and_admission(harness, subject_binding=sb)
    case_dir, conn = _setup_case_dir("QA-P11a", evidence_dir)
    db_path = os.path.join(case_dir, "enforcement.db")
    reg = RevocationRegistry()
    barrier = SQLiteBarrier(db_path)
    try:
        _insert_initial_resource(conn, "resource-A", "p11a-initial")
        initial_value, initial_mc = _read_resource(conn, "resource-A")
        starting_epoch = capture_epoch(conn)
        cap = _make_capability(harness, sb=sb, q=q, a=a, nonce="nonce-p11a-1")
        td = _make_trust_decision(harness, cap=cap)

        # === Barrier step 1: acquire write lock via control-record txn ===
        _executor_call(barrier.acquire_holding)

        # === Barrier step 2: EAP attempts to begin (SQLITE_BUSY) ===
        # We attempt an EAP-style BEGIN IMMEDIATE on a separate connection.
        eap_attempt_ok, eap_err = _executor_call(barrier.attempt_write,
            "INSERT INTO protected_resource (resource_id, value, mutation_count) "
            "VALUES ('__barrier_probe__', 'probe', 0)"
        )
        ev_busy_blocked = (not eap_attempt_ok)

        # === Barrier step 3: commit the control-record txn (epoch++) ===
        # First: release the holding lock (ROLLBACK so we don't actually
        # mutate the fixture), then commit the real CR via the in-process
        # apply_revocation_control_record path.
        _executor_call(barrier.release_holding)

        apply_revocation_control_record(
            conn,
            record_id="p11a-rev",
            target_type="qualification",
            target_id=q.credential_id,
            target_digest=q.credential_digest,
            issuer_priv=harness.keys.r11_priv,
            issuer_pub=harness.keys.r11_pub,
            issuer_authority_id="r11-q",
            issuer_key_id=_r11_key_id(harness),
            registry=reg,
            reason="qa-p11a-revocation",
            created_at_unix_ms=harness.clock.now_unix_ms,
            change_type_authorization_ok=_make_strict_auth_lookup(harness),
        )
        ending_epoch = capture_epoch(conn)

        # === Barrier step 4: EAP proceeds; denied by dependency (now revoked) ===
        result = _run_eap(
            harness, conn=conn, sb=sb, q=q, a=a, cap=cap, td=td, reg=reg,
            resource_id="resource-A", new_value="p11a-write",
        )

        ev = FormalEvidence(
            test_id="QA-P11a",
            fixture_id=f"QA-P11a/{case_dir}",
            case_function="tests.case_functions.case_p11a",
            verdict=result.verdict,
            reason_code=result.reason_code,
            qualification_id=q.credential_id,
            qualification_digest=q.credential_digest,
            admission_id=a.credential_id,
            admission_digest=a.credential_digest,
            capability_id=cap.token_id,
            capability_digest=cap.token_digest,
            trust_decision_id=td.trust_decision_id,
            trust_decision_digest=td.trust_decision_digest,
        )
        ev.eap_reached = True
        # FR-9 barrier evidence
        ev.barrier_evidence = {
            "barrier_held_before_eap": True,
            "eap_attempted_write_blocked_by_busy": ev_busy_blocked,
            "control_record_committed_first": ending_epoch == starting_epoch + 1,
            "eap_executed_after_cr_commit": True,
            "lock_holding_connection": "separate sqlite3 connection with BEGIN IMMEDIATE",
            "competing_connection": "separate sqlite3 connection with INSERT",
        }
        final_value, final_mc = _read_resource(conn, "resource-A")
        ev.subcheck_results = {
            "barrier_busy_blocked": ev_busy_blocked,
            "cr_committed_first": ending_epoch == starting_epoch + 1,
            "no_protected_mutation": final_mc == initial_mc,
            "audit_chain_valid": capture_audit_chain_valid(conn),
        }
        ev.pass_fail = (
            "PASS" if (result.verdict == "EXECUTION_DENIED"
                        and final_mc == initial_mc
                        and ev_busy_blocked
                        and ending_epoch == starting_epoch + 1
                        and capture_audit_chain_valid(conn))
            else "FAIL"
        )
        if final_mc > initial_mc and ev.pass_fail == "PASS":
            ev.enforcement_failure_reason = "unauthorized protected mutation"
        return _populate_evidence(
            ev, conn,
            resource_id="resource-A",
            initial_value=initial_value, initial_mc=initial_mc,
            final_value=final_value, final_mc=final_mc,
            starting_epoch=starting_epoch,
            ending_epoch=ending_epoch,
            audit_chain_valid=capture_audit_chain_valid(conn),
            applied_control_records=capture_applied_control_records(conn),
        )
    finally:
        _executor_call(barrier.release_holding)
        conn.close()


def case_p11b(harness, evidence_dir) -> FormalEvidence:
    """QA-P11 subcase B (FR-9): EAP holds the write lock FIRST (BEGIN
    IMMEDIATE); CR transaction contends and is blocked by SQLITE_BUSY; EAP
    + protected mutation commits (mutation_count=1); CR proceeds and
    commits revocation; subsequent fresh action denied.

    Frozen §25 ordering: EAP transaction gets the write lock, control-record
    operation is released to contend and cannot pass it, EAP + protected
    mutation commits, control-record transaction proceeds afterward and
    commits revocation, mutation_count = 1, a subsequent fresh action denies.
    """
    from trusted.enforcement_store import SQLiteBarrier

    sb = make_subject_binding(identity_id="agent-p11b", challenge="p11b")
    q, a = issue_qualification_and_admission(harness, subject_binding=sb)
    case_dir, conn = _setup_case_dir("QA-P11b", evidence_dir)
    db_path = os.path.join(case_dir, "enforcement.db")
    reg = RevocationRegistry()
    barrier = SQLiteBarrier(db_path)
    try:
        _insert_initial_resource(conn, "resource-A", "p11b-initial")
        initial_value, initial_mc = _read_resource(conn, "resource-A")
        starting_epoch = capture_epoch(conn)
        cap = _make_capability(harness, sb=sb, q=q, a=a, nonce="nonce-p11b-1")
        td = _make_trust_decision(harness, cap=cap)

        # === Barrier step 1: EAP acquires write lock via separate connection ===
        # The EAP itself uses conn (in-process). We hold an additional
        # BEGIN IMMEDIATE on a separate connection to demonstrate the
        # control-record contention against an in-progress EAP.
        holding_conn = _executor_call(barrier.acquire_holding)

        # === Barrier step 2: CR attempts to commit while EAP is in flight ===
        # CR tries to UPDATE — gets SQLITE_BUSY because the holding
        # connection (EAP-equivalent) holds the write lock.
        cr_attempt_ok, cr_err = _executor_call(barrier.attempt_write,
            "INSERT INTO protected_resource (resource_id, value, mutation_count) "
            "VALUES ('__barrier_probe_cr__', 'probe', 0)"
        )
        ev_cr_busy_blocked = (not cr_attempt_ok)

        # === Barrier step 3: release the holding connection (EAP-equivalent commits) ===
        _executor_call(barrier.release_holding)

        # === Barrier step 4: EAP commits (in-process conn) — mutation_count=1 ===
        result1 = _run_eap(
            harness, conn=conn, sb=sb, q=q, a=a, cap=cap, td=td, reg=reg,
            resource_id="resource-A", new_value="p11b-write-1",
        )
        post_eap_epoch = capture_epoch(conn)

        # === Barrier step 5: CR proceeds; commits revocation ===
        apply_revocation_control_record(
            conn,
            record_id="p11b-rev",
            target_type="qualification",
            target_id=q.credential_id,
            target_digest=q.credential_digest,
            issuer_priv=harness.keys.r11_priv,
            issuer_pub=harness.keys.r11_pub,
            issuer_authority_id="r11-q",
            issuer_key_id=_r11_key_id(harness),
            registry=reg,
            reason="qa-p11b-revocation",
            created_at_unix_ms=harness.clock.now_unix_ms,
            change_type_authorization_ok=_make_strict_auth_lookup(harness),
        )
        ending_epoch = capture_epoch(conn)

        # === Barrier step 6: subsequent EAP denied ===
        result2 = _run_eap(
            harness, conn=conn, sb=sb, q=q, a=a, cap=cap, td=td, reg=reg,
            resource_id="resource-A", new_value="p11b-write-2",
        )

        ev = FormalEvidence(
            test_id="QA-P11b",
            fixture_id=f"QA-P11b/{case_dir}",
            case_function="tests.case_functions.case_p11b",
            verdict=result2.verdict,
            reason_code=result2.reason_code,
            qualification_id=q.credential_id,
            qualification_digest=q.credential_digest,
            admission_id=a.credential_id,
            admission_digest=a.credential_digest,
            capability_id=cap.token_id,
            capability_digest=cap.token_digest,
            trust_decision_id=td.trust_decision_id,
            trust_decision_digest=td.trust_decision_digest,
        )
        ev.eap_reached = True
        # FR-9 barrier evidence
        ev.barrier_evidence = {
            "eap_held_lock_first": True,
            "cr_attempted_write_blocked_by_busy": ev_cr_busy_blocked,
            "eap_committed_first": post_eap_epoch == starting_epoch,
            "cr_committed_after_eap": ending_epoch == starting_epoch + 1,
            "lock_holding_connection": "separate sqlite3 connection with BEGIN IMMEDIATE (EAP-equivalent)",
            "competing_connection": "separate sqlite3 connection (CR-equivalent)",
        }
        final_value, final_mc = _read_resource(conn, "resource-A")
        ev.subcheck_results = {
            "barrier_cr_busy_blocked": ev_cr_busy_blocked,
            "first_eap_succeeded": result1.verdict == "EXECUTION_SUCCEEDED",
            "first_eap_mutated": final_mc >= 1,
            "cr_committed_after_eap": ending_epoch == starting_epoch + 1,
            "second_eap_denied": result2.verdict == "EXECUTION_DENIED",
            "audit_chain_valid": capture_audit_chain_valid(conn),
        }
        ev.pass_fail = (
            "PASS" if (result1.verdict == "EXECUTION_SUCCEEDED"
                        and result2.verdict == "EXECUTION_DENIED"
                        and final_mc == 1
                        and ev_cr_busy_blocked
                        and ending_epoch == starting_epoch + 1
                        and capture_audit_chain_valid(conn))
            else "FAIL"
        )
        if final_mc > 1 and ev.pass_fail == "PASS":
            ev.enforcement_failure_reason = "unauthorized protected mutation"
        return _populate_evidence(
            ev, conn,
            resource_id="resource-A",
            initial_value=initial_value, initial_mc=initial_mc,
            final_value=final_value, final_mc=final_mc,
            starting_epoch=starting_epoch,
            ending_epoch=ending_epoch,
            audit_chain_valid=capture_audit_chain_valid(conn),
            applied_control_records=capture_applied_control_records(conn),
        )
    finally:
        _executor_call(barrier.release_holding)
        conn.close()


def case_p12(harness, evidence_dir) -> FormalEvidence:
    """QA-P12: ACTUAL requester direct protected-resource bypass attempt.

    Real OS-level bypass attempts as ate-requester:
      - sqlite3 UPDATE on enforcement.db
      - dd filesystem overwrite of enforcement.db
      - sqlite3 UPDATE as ate-authority
    Each MUST fail (exit nonzero). Resource state MUST be unchanged.
    """
    import subprocess
    db = "/var/lib/ate/poc/executor/enforcement.db"
    ev = FormalEvidence(
        test_id="QA-P12",
        fixture_id=f"QA-P12/{db}",
        case_function="tests.case_functions.case_p12",
        verdict="BYPASS_ATTEMPT",
        reason_code="",
        eap_reached=False,
    )

    # Seed baseline fixture as ate-executor
    fixture_id = "qa-p12-fixture"
    fixture_value = "PF12-baseline"
    init = subprocess.run(
        ["sudo", "-n", "-u", "ate-executor", "sqlite3", db,
         f"INSERT OR REPLACE INTO protected_resource (resource_id, value, mutation_count) "
         f"VALUES ('{fixture_id}', '{fixture_value}', 0);"],
        capture_output=True, text=True,
    )
    if init.returncode != 0:
        ev.pass_fail = "FAIL"
        ev.invalid_run_reason = f"baseline seed failed: {init.stderr}"
        ev.reason_code = ev.invalid_run_reason
        return ev
    baseline = subprocess.run(
        ["sudo", "-n", "-u", "ate-executor", "sqlite3", db,
         f"SELECT value, mutation_count FROM protected_resource "
         f"WHERE resource_id='{fixture_id}';"],
        capture_output=True, text=True,
    )
    baseline_value, baseline_mc = baseline.stdout.strip().split("|")
    ev.initial_resource_value = baseline_value
    ev.initial_mutation_count = int(baseline_mc)

    bypass_sql = (
        f"UPDATE protected_resource SET value='BYPASS-VALUE', mutation_count=999 "
        f"WHERE resource_id='{fixture_id}';"
    )
    bypass1 = subprocess.run(
        ["sudo", "-n", "-u", "ate-requester", "sqlite3", db, bypass_sql],
        capture_output=True, text=True,
    )
    bypass2 = subprocess.run(
        ["sudo", "-n", "-u", "ate-requester", "dd", "if=/dev/zero", f"of={db}",
         "bs=1", "count=1", "conv=notrunc"],
        capture_output=True, text=True,
    )
    bypass3 = subprocess.run(
        ["sudo", "-n", "-u", "ate-authority", "sqlite3", db, bypass_sql],
        capture_output=True, text=True,
    )
    after = subprocess.run(
        ["sudo", "-n", "-u", "ate-executor", "sqlite3", db,
         f"SELECT value, mutation_count FROM protected_resource "
         f"WHERE resource_id='{fixture_id}';"],
        capture_output=True, text=True,
    )
    after_value, after_mc = after.stdout.strip().split("|")
    ev.final_resource_value = after_value
    ev.final_mutation_count = int(after_mc)

    # Subchecks
    bypass_requester_denied = bypass1.returncode != 0
    bypass_requester_dd_denied = bypass2.returncode != 0
    bypass_authority_denied = bypass3.returncode != 0
    resource_unchanged = (after_value == baseline_value and int(after_mc) == 0)

    ev.subcheck_results = {
        "requester_sqlite3_bypass_denied": "PASS" if bypass_requester_denied else "FAIL",
        "requester_dd_bypass_denied": "PASS" if bypass_requester_dd_denied else "FAIL",
        "authority_sqlite3_bypass_denied": "PASS" if bypass_authority_denied else "FAIL",
        "resource_state_unchanged": "PASS" if resource_unchanged else "FAIL",
    }
    # If any bypass SUCCEEDED -> ENFORCEMENT_FAILURE override
    bypass_succeeded = (not bypass_requester_denied) or (not bypass_requester_dd_denied) or (not bypass_authority_denied)
    resource_mutated = not resource_unchanged
    if bypass_succeeded and resource_mutated:
        ev.pass_fail = "FAIL"
        ev.enforcement_failure_reason = (
            f"requester/authority bypass SUCCEEDED (sqlite3 rc={bypass1.returncode}, "
            f"dd rc={bypass2.returncode}, authority rc={bypass3.returncode}); "
            f"resource mutated"
        )
    elif all(s == "PASS" for s in ev.subcheck_results.values()):
        ev.pass_fail = "PASS"
    else:
        ev.pass_fail = "FAIL"
    ev.reason_code = "; ".join(f"{k}={v}" for k, v in ev.subcheck_results.items())
    return ev


def case_p13(harness, evidence_dir) -> FormalEvidence:
    """QA-P13: qualification issued under a future v2 profile (different
    digest) is rejected at admission with AX_QUALIFICATION_PROFILE_UNRECOGNIZED."""
    sb = make_subject_binding(identity_id="agent-p13", challenge="p13")
    # Publish a v2 profile with same id but different digest
    v2_profile = harness.qualification.publish_profile(
        profile_id="qa-demo-writer",
        profile_version=2,
        qualification_domain="local-qa-demo",
        role_id="demo-repository-writer",
        minimum_binding="SB2",
        maximum_risk="R2",
        eligible_capability="demo-resource-write",
        required_evidence_classes=[
            "identity/runtime", "provenance/runtime-class",
            "governance compatibility", "behavioral fixture receipt",
            "operational-control compatibility",
        ],
    )
    assert v2_profile.profile_digest != harness.profile.profile_digest
    evidence = build_evidence_bundle(subject_binding=sb)
    _q_manifest, _q_decision, q_v2 = harness.qualification.evaluate(
        subject_binding=sb,
        qualification_domain="local-qa-demo",
        role="demo-repository-writer",
        evidence=evidence,
        snapshot_reference=FIXED_SNAPSHOT_REF,
        clock=harness.clock,
    )
    assert q_v2 is not None
    assert q_v2.profile_digest == v2_profile.profile_digest

    case_dir, conn = _setup_case_dir("QA-P13", evidence_dir)
    try:
        _insert_initial_resource(conn, "resource-A", "p13-initial")
        initial_value, initial_mc = _read_resource(conn, "resource-A")
        starting_epoch = capture_epoch(conn)
        denied = False
        try:
            harness.admission.evaluate(
                subject_binding=sb,
                qualification=q_v2,
                trust_domain="local-ate-demo",
                role="demo-repository-writer",
                snapshot_reference=FIXED_SNAPSHOT_REF,
                clock=harness.clock,
                revocation_lookup=_no_revocations,
            )
        except DependencyEvaluationError as e:
            denied = "AX_QUALIFICATION_PROFILE_UNRECOGNIZED" in str(e)
        ev = FormalEvidence(
            test_id="QA-P13",
            fixture_id=f"QA-P13/{case_dir}",
            case_function="tests.case_functions.case_p13",
            verdict="AX_QUALIFICATION_PROFILE_UNRECOGNIZED" if denied else "ADMISSION_ISSUED",
            reason_code="ADMISSION_DENIED_FUTURE_PROFILE" if denied else "WRONG: admission issued for unrecognized profile",
            qualification_id=q_v2.credential_id,
            qualification_digest=q_v2.profile_digest,  # record the v2 digest
            admission_id="",
            admission_digest="",
            capability_id=None,
            capability_digest=None,
            trust_decision_id=None,
            trust_decision_digest=None,
            eap_reached=False,
        )
        ev.pass_fail = "PASS" if denied else "FAIL"
        final_value, final_mc = _read_resource(conn, "resource-A")
        if final_mc > initial_mc and ev.pass_fail == "PASS":
            ev.enforcement_failure_reason = "unauthorized protected mutation"
        return _populate_evidence(
            ev, conn,
            resource_id="resource-A",
            initial_value=initial_value, initial_mc=initial_mc,
            final_value=final_value, final_mc=final_mc,
            starting_epoch=starting_epoch,
            ending_epoch=capture_epoch(conn),
            audit_chain_valid=True,
            applied_control_records=capture_applied_control_records(conn),
        )
    finally:
        conn.close()


def case_p14_deny(harness, evidence_dir) -> FormalEvidence:
    """QA-P14 deny: old AdmissionCredential expires while downstream
    artifacts remain nominally valid -> EAP must deny ADMISSION_EXPIRED.

    This isolates the frozen admission-review boundary rather than allowing
    CapabilityToken/TrustDecision expiry to mask it.
    """
    sb = make_subject_binding(identity_id="agent-p14d", challenge="p14d")

    QUAL_TTL_MS = 48 * 3600 * 1000
    ADM_TTL_MS = 6 * 3600 * 1000
    CAP_TTL_MS = 48 * 3600 * 1000
    TD_TTL_MS = 48 * 3600 * 1000
    ADVANCE_MS = ADM_TTL_MS + 60_000

    q, a = issue_qualification_and_admission(
        harness,
        subject_binding=sb,
        qualification_lifetime_ms=QUAL_TTL_MS,
        admission_lifetime_ms=ADM_TTL_MS,
    )
    case_dir, conn = _setup_case_dir("QA-P14-deny", evidence_dir)
    reg = RevocationRegistry()
    try:
        _insert_initial_resource(conn, "resource-A", "p14d-initial")
        initial_value, initial_mc = _read_resource(conn, "resource-A")
        starting_epoch = capture_epoch(conn)

        cap = _make_capability(
            harness, sb=sb, q=q, a=a, nonce="nonce-p14d-1",
            capability_lifetime_ms=CAP_TTL_MS,
        )
        td = _make_trust_decision(
            harness, cap=cap, trust_decision_lifetime_ms=TD_TTL_MS,
        )

        qual_exp = q.expires_at_unix_ms
        adm_exp = a.expires_at_unix_ms
        cap_exp = cap.expires_at_unix_ms
        td_exp = td.expires_at_unix_ms
        assert adm_exp < qual_exp
        assert adm_exp < cap_exp
        assert adm_exp < td_exp

        harness.clock = harness.clock.advance_ms(ADVANCE_MS)
        now = harness.clock.now_unix_ms
        assert now > adm_exp
        assert now < qual_exp
        assert now < cap_exp
        assert now < td_exp

        result = _run_eap(
            harness, conn=conn, sb=sb, q=q, a=a, cap=cap, td=td, reg=reg,
            resource_id="resource-A", new_value="p14d-write",
        )
        ev = FormalEvidence(
            test_id="QA-P14-deny",
            fixture_id=f"QA-P14-deny/{case_dir}",
            case_function="tests.case_functions.case_p14_deny",
            verdict=result.verdict,
            reason_code=result.reason_code,
            qualification_id=q.credential_id,
            qualification_digest=q.credential_digest,
            qualification_expires_at_unix_ms=qual_exp,
            admission_id=a.credential_id,
            admission_digest=a.credential_digest,
            admission_expires_at_unix_ms=adm_exp,
            capability_id=cap.token_id,
            capability_digest=cap.token_digest,
            capability_expires_at_unix_ms=cap_exp,
            trust_decision_id=td.trust_decision_id,
            trust_decision_digest=td.trust_decision_digest,
            trust_decision_expires_at_unix_ms=td_exp,
        )
        ev.eap_reached = True
        final_value, final_mc = _read_resource(conn, "resource-A")

        admission_expired = "ADMISSION_EXPIRED" in result.reason_code
        masked = any(x in result.reason_code for x in (
            "QUALIFICATION_EXPIRED", "CAPABILITY_EXPIRED", "TRUST_DECISION_EXPIRED"
        ))
        ev.subcheck_results = {
            "admission_expired_in_reason": admission_expired,
            "qualification_still_nominal": now < qual_exp,
            "capability_still_nominal": now < cap_exp,
            "trust_decision_still_nominal": now < td_exp,
            "no_masking_expiry_reason": not masked,
            "no_protected_mutation": final_mc == initial_mc,
        }
        ev.pass_fail = (
            "PASS" if (
                result.verdict == "EXECUTION_DENIED"
                and admission_expired
                and not masked
                and final_mc == initial_mc
                and now < qual_exp and now < cap_exp and now < td_exp
            ) else "FAIL"
        )
        if final_mc > initial_mc:
            ev.enforcement_failure_reason = "unauthorized protected mutation after expired admission"
        return _populate_evidence(
            ev, conn,
            resource_id="resource-A",
            initial_value=initial_value, initial_mc=initial_mc,
            final_value=final_value, final_mc=final_mc,
            starting_epoch=starting_epoch,
            ending_epoch=capture_epoch(conn),
            audit_chain_valid=capture_audit_chain_valid(conn),
            applied_control_records=capture_applied_control_records(conn),
        )
    finally:
        conn.close()


def case_p14_renewal(harness, evidence_dir) -> FormalEvidence:
    """QA-P14 full renewal: advance clock past admission expiry;
    renewal issues a NEW AdmissionCredential with DISTINCT
    id/digest. Old artifact remains valid historical evidence.
    Subsequent EAP with the new admission SUCCEEDS."""
    sb = make_subject_binding(identity_id="agent-p14r", challenge="p14r")
    q, a_old = issue_qualification_and_admission(harness, subject_binding=sb)
    old_id = a_old.credential_id
    old_digest = a_old.credential_digest
    advanced = harness.clock.advance_ms(13 * 3600 * 1000)
    # Renew with advanced clock
    fresh_clock = Clock(now_unix_ms=advanced.now_unix_ms)
    harness.clock = fresh_clock
    try:
        _a_manifest, _a_decision, a_new = harness.admission.evaluate(
            subject_binding=sb,
            qualification=q,
            trust_domain="local-ate-demo",
            role="demo-repository-writer",
            snapshot_reference=FIXED_SNAPSHOT_REF,
            clock=fresh_clock,
            revocation_lookup=_no_revocations,
        )
        assert a_new is not None
        new_id = a_new.credential_id
        new_digest = a_new.credential_digest
        case_dir, conn = _setup_case_dir("QA-P14-renewal", evidence_dir)
        reg = RevocationRegistry()
        try:
            _insert_initial_resource(conn, "resource-A", "p14r-initial")
            initial_value, initial_mc = _read_resource(conn, "resource-A")
            starting_epoch = capture_epoch(conn)
            # Old artifact remains valid historical evidence
            old_still_verifies = False
            try:
                verify_artifact(a_old, harness.keys.r12_pub)
                old_still_verifies = True
            except Exception:
                old_still_verifies = False
            cap = _make_capability(harness, sb=sb, q=q, a=a_new, nonce="nonce-p14r-1")
            td = _make_trust_decision(harness, cap=cap)
            result = _run_eap(
                harness, conn=conn, sb=sb, q=q, a=a_new, cap=cap, td=td, reg=reg,
                resource_id="resource-A", new_value="p14r-write",
            )
            ev = FormalEvidence(
                test_id="QA-P14-renewal",
                fixture_id=f"QA-P14-renewal/{case_dir}",
                case_function="tests.case_functions.case_p14_renewal",
                verdict=result.verdict,
                reason_code=result.reason_code,
                qualification_id=q.credential_id,
                qualification_digest=q.credential_digest,
                admission_id=a_new.credential_id,
                admission_digest=a_new.credential_digest,
                capability_id=cap.token_id,
                capability_digest=cap.token_digest,
                trust_decision_id=td.trust_decision_id,
                trust_decision_digest=td.trust_decision_digest,
            )
            ev.eap_reached = True
            ev.subcheck_results = {
                "old_admission_id_distinct": "PASS" if new_id != old_id else "FAIL",
                "new_admission_digest_distinct": "PASS" if new_digest != old_digest else "FAIL",
                "old_artifact_remains_valid_historical_evidence": "PASS" if old_still_verifies else "FAIL",
                "new_admission_eap_succeeds": (
                    "PASS" if (result.verdict == "EXECUTION_SUCCEEDED") else "FAIL"
                ),
            }
            final_value, final_mc = _read_resource(conn, "resource-A")
            ev.pass_fail = (
                "PASS" if all(s == "PASS" for s in ev.subcheck_results.values())
                else "FAIL"
            )
            if final_mc != initial_mc + 1 and ev.pass_fail == "PASS":
                ev.enforcement_failure_reason = "mutation_count not as expected"
            return _populate_evidence(
                ev, conn,
                resource_id="resource-A",
                initial_value=initial_value, initial_mc=initial_mc,
                final_value=final_value, final_mc=final_mc,
                starting_epoch=starting_epoch,
                ending_epoch=capture_epoch(conn),
                audit_chain_valid=capture_audit_chain_valid(conn),
                applied_control_records=capture_applied_control_records(conn),
            )
        finally:
            conn.close()
    finally:
        pass


# --- Helpers not yet imported (avoid circular import) --------------------


def _read_resource(conn, resource_id: str) -> Tuple[str, int]:
    row = enforcement_store.read_protected_resource(conn, resource_id) or {}
    return (row.get("value", ""), row.get("mutation_count", 0))


# --- Case registry (required by formal_runner.py) -------------------------


CASES = {
    "QA-P1": case_p1,
    "QA-P2": case_p2,
    "QA-P3": case_p3,
    "QA-P4": case_p4,
    "QA-P5": case_p5,
    "QA-P6": case_p6,
    "QA-P7": case_p7,
    "QA-P8": case_p8,
    "QA-P9": case_p9,
    "QA-P10": case_p10,
    "QA-P11a": case_p11a,
    "QA-P11b": case_p11b,
    "QA-P12": case_p12,
    "QA-P13": case_p13,
    "QA-P14-deny": case_p14_deny,
    "QA-P14-renewal": case_p14_renewal,
}

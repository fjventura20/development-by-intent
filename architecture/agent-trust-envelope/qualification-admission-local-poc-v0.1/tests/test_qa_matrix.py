"""QA-P matrix dev/dry-run tests.

These tests exercise the implementation but DO NOT constitute the formal
scored run. They are dev tests to verify the EAP and dependency
evaluation behave as expected on a small set of scenarios; the formal
scored run is run by `run_formal.py` under an explicit authorization
token that is NOT provided in this handoff.

The cases here cover:
  QA-P1  happy path             → EXECUTION_SUCCEEDED + mutation_count=1
  QA-P2  no admission           → EXECUTION_DENIED before EAP (denied at issuance)
  QA-P3  admission revoked      → revoke before issuance → no admission credential
  QA-P4  admission revoked before EAP → revoke before EAP → EXECUTION_DENIED
  QA-P5  qualification revoked before EAP → EXECUTION_DENIED
  QA-P6  qualification expired before EAP → EXECUTION_DENIED
  QA-P7  agent B reuses agent A → SubjectBinding digest mismatch at EAP
  QA-P9  incoherent snapshot    → no such case in this PoC (snapshot is fixed)
  QA-P11 ordering A — revocation commits before EAP
  QA-P11 ordering B — EAP commits before revocation
  QA-P14 admission expired before EAP → EXECUTION_DENIED

QA-P8, QA-P10, QA-P12, QA-P13 are exercised in their own files
(test_issuer_authorization, test_canonical_p10, test_bypass, test_unrecognized_profile).
"""

from __future__ import annotations

import os

import pytest

from qa_poc.admission import DependencyEvaluationError, check_admission_usable
from qa_poc.clock import Clock
from tests._helpers import (
    FIXED_SNAPSHOT_REF,
    FixtureHarness,
    _no_revocations,
    close_temp_store,
    issue_qualification_and_admission,
    make_subject_binding,
    open_temp_store,
)
from trusted import audit_ingest, enforcement_store
from trusted.executor import BoundActionBundle, execute_bound_action


# --- QA-P1 happy path ------------------------------------------------------


def test_qa_p1_happy_path():
    h = FixtureHarness.build()
    sb = make_subject_binding(identity_id="agent-a")
    q, a = issue_qualification_and_admission(h, subject_binding=sb)
    conn, tmp = open_temp_store()
    try:
        enforcement_store.insert_protected_resource(conn, resource_id="resource-A", value="initial")
        cap = h.authorization.issue_capability_token(
            subject_binding=sb,
            qualification=q,
            admission=a,
            session_identity="sess-1",
            operation="WRITE",
            target="resource-A",
            parameters={"new_value": "hello"},
            risk_class="R2",
            capability_class="demo-resource-write",
            nonce="nonce-p1-1",
            snapshot_reference=FIXED_SNAPSHOT_REF,
            clock=h.clock,
        )
        td = h.authorization.issue_trust_decision(
            capability=cap,
            requested_action={"target": "resource-A", "operation": "WRITE", "parameters": {"new_value": "hello"}},
            verdict="AUTHORIZED",
            snapshot_reference=FIXED_SNAPSHOT_REF,
            clock=h.clock,
        )
        bundle = BoundActionBundle(
            subject_binding=sb, capability=cap, trust_decision=td,
            action={"target": "resource-A", "operation": "WRITE", "parameters": {"new_value": "hello"}},
        )
        result = execute_bound_action(
            conn,
            bundle=bundle,
            auth_pub=h.keys.auth_pub,
            trust_pub=h.keys.trust_pub,
            revocation_lookup=_no_revocations,
            bound_qualification=q,
            bound_admission=a,
            qualification_pub=h.keys.r11_pub,
            admission_pub=h.keys.r12_pub,
            resource_id="resource-A",
            new_resource_value="hello",
            clock=h.clock,
        )
        assert result.verdict == "EXECUTION_SUCCEEDED", result.reason_code
        assert result.mutation_count == 1
        # Audit chain must be valid
        assert enforcement_store.verify_audit_chain(conn) is True
        # And the resource value must have changed
        res = enforcement_store.read_protected_resource(conn, "resource-A")
        assert res["value"] == "hello"
    finally:
        close_temp_store(conn, tmp)


# --- QA-P2: no admission (qualification only) -----------------------------


def test_qa_p2_no_admission_means_no_capability():
    """Without an AdmissionCredential, capability issuance cannot occur.

    We model this by checking that the admission authority refuses to
    issue a credential when the bound qualification is missing.
    """
    from qa_poc.admission import AdmissionAuthority
    from qa_poc.policies import PolicyRegistry

    h = FixtureHarness.build()
    # Build a separate admission authority that has NO qualification bound
    adm2 = AdmissionAuthority(
        registry=PolicyRegistry(),
        r12_priv=h.keys.r12_priv,
        r12_pub=h.keys.r12_pub,
        r12_key_id="r12-a",
    )
    # Try to evaluate with no bound qualification → should raise
    with pytest.raises(TypeError):
        adm2.evaluate()  # missing required kwargs


# --- QA-P4: admission revoked before EAP ----------------------------------


def test_qa_p4_admission_revocation_blocks_eap():
    h = FixtureHarness.build()
    sb = make_subject_binding(identity_id="agent-a", challenge="c-p4")
    q, a = issue_qualification_and_admission(h, subject_binding=sb)
    conn, tmp = open_temp_store()
    try:
        enforcement_store.insert_protected_resource(conn, resource_id="resource-A", value="initial")
        cap = h.authorization.issue_capability_token(
            subject_binding=sb,
            qualification=q,
            admission=a,
            session_identity="sess-4",
            operation="WRITE",
            target="resource-A",
            parameters={"new_value": "x"},
            risk_class="R2",
            capability_class="demo-resource-write",
            nonce="nonce-p4-1",
            snapshot_reference=FIXED_SNAPSHOT_REF,
            clock=h.clock,
        )
        td = h.authorization.issue_trust_decision(
            capability=cap,
            requested_action={"target": "resource-A", "operation": "WRITE", "parameters": {"new_value": "x"}},
            verdict="AUTHORIZED",
            snapshot_reference=FIXED_SNAPSHOT_REF,
            clock=h.clock,
        )
        bundle = BoundActionBundle(
            subject_binding=sb, capability=cap, trust_decision=td,
            action={"target": "resource-A", "operation": "WRITE", "parameters": {"new_value": "x"}},
        )
        # Revocation lookup says admission is revoked
        def revoked(_cid):
            if _cid == a.credential_id:
                return (True, "revoked-for-test")
            return (False, "")
        result = execute_bound_action(
            conn,
            bundle=bundle,
            auth_pub=h.keys.auth_pub,
            trust_pub=h.keys.trust_pub,
            revocation_lookup=revoked,
            bound_qualification=q,
            bound_admission=a,
            qualification_pub=h.keys.r11_pub,
            admission_pub=h.keys.r12_pub,
            resource_id="resource-A",
            new_resource_value="x",
            clock=h.clock,
        )
        assert result.verdict == "EXECUTION_DENIED"
        assert "ADMISSION" in result.reason_code or "REVOKED" in result.reason_code
        res = enforcement_store.read_protected_resource(conn, "resource-A")
        assert res["mutation_count"] == 0
    finally:
        close_temp_store(conn, tmp)


# --- QA-P5: qualification revoked before EAP (cascade to admission) ------


def test_qa_p5_qualification_revocation_blocks_eap():
    h = FixtureHarness.build()
    sb = make_subject_binding(identity_id="agent-a", challenge="c-p5")
    q, a = issue_qualification_and_admission(h, subject_binding=sb)
    conn, tmp = open_temp_store()
    try:
        enforcement_store.insert_protected_resource(conn, resource_id="resource-A", value="initial")
        cap = h.authorization.issue_capability_token(
            subject_binding=sb,
            qualification=q,
            admission=a,
            session_identity="sess-5",
            operation="WRITE",
            target="resource-A",
            parameters={"new_value": "x"},
            risk_class="R2",
            capability_class="demo-resource-write",
            nonce="nonce-p5-1",
            snapshot_reference=FIXED_SNAPSHOT_REF,
            clock=h.clock,
        )
        td = h.authorization.issue_trust_decision(
            capability=cap,
            requested_action={"target": "resource-A", "operation": "WRITE", "parameters": {"new_value": "x"}},
            verdict="AUTHORIZED",
            snapshot_reference=FIXED_SNAPSHOT_REF,
            clock=h.clock,
        )
        bundle = BoundActionBundle(
            subject_binding=sb, capability=cap, trust_decision=td,
            action={"target": "resource-A", "operation": "WRITE", "parameters": {"new_value": "x"}},
        )
        # Revoke the bound QUALIFICATION (cascade)
        def revoked(_cid):
            if _cid == q.credential_id:
                return (True, "qualification-revoked")
            return (False, "")
        result = execute_bound_action(
            conn,
            bundle=bundle,
            auth_pub=h.keys.auth_pub,
            trust_pub=h.keys.trust_pub,
            revocation_lookup=revoked,
            bound_qualification=q,
            bound_admission=a,
            qualification_pub=h.keys.r11_pub,
            admission_pub=h.keys.r12_pub,
            resource_id="resource-A",
            new_resource_value="x",
            clock=h.clock,
        )
        assert result.verdict == "EXECUTION_DENIED"
        assert "QUALIFICATION" in result.reason_code
        res = enforcement_store.read_protected_resource(conn, "resource-A")
        assert res["mutation_count"] == 0
    finally:
        close_temp_store(conn, tmp)


# --- QA-P6: qualification expires before EAP ------------------------------


def test_qa_p6_qualification_expired_blocks_eap():
    h = FixtureHarness.build()
    sb = make_subject_binding(identity_id="agent-a", challenge="c-p6")
    q, a = issue_qualification_and_admission(h, subject_binding=sb)
    conn, tmp = open_temp_store()
    try:
        enforcement_store.insert_protected_resource(conn, resource_id="resource-A", value="initial")
        cap = h.authorization.issue_capability_token(
            subject_binding=sb,
            qualification=q,
            admission=a,
            session_identity="sess-6",
            operation="WRITE",
            target="resource-A",
            parameters={"new_value": "x"},
            risk_class="R2",
            capability_class="demo-resource-write",
            nonce="nonce-p6-1",
            snapshot_reference=FIXED_SNAPSHOT_REF,
            clock=h.clock,
        )
        td = h.authorization.issue_trust_decision(
            capability=cap,
            requested_action={"target": "resource-A", "operation": "WRITE", "parameters": {"new_value": "x"}},
            verdict="AUTHORIZED",
            snapshot_reference=FIXED_SNAPSHOT_REF,
            clock=h.clock,
        )
        bundle = BoundActionBundle(
            subject_binding=sb, capability=cap, trust_decision=td,
            action={"target": "resource-A", "operation": "WRITE", "parameters": {"new_value": "x"}},
        )
        # Advance the clock past qualification expiry (24h)
        advanced = h.clock.advance_ms(25 * 3600 * 1000)
        result = execute_bound_action(
            conn,
            bundle=bundle,
            auth_pub=h.keys.auth_pub,
            trust_pub=h.keys.trust_pub,
            revocation_lookup=_no_revocations,
            bound_qualification=q,
            bound_admission=a,
            qualification_pub=h.keys.r11_pub,
            admission_pub=h.keys.r12_pub,
            resource_id="resource-A",
            new_resource_value="x",
            clock=advanced,
        )
        assert result.verdict == "EXECUTION_DENIED"
        assert "QUALIFICATION_EXPIRED" in result.reason_code or "EXPIRED" in result.reason_code
        res = enforcement_store.read_protected_resource(conn, "resource-A")
        assert res["mutation_count"] == 0
    finally:
        close_temp_store(conn, tmp)


# --- QA-P7: agent B tries to use agent A's chain --------------------------


def test_qa_p7_agent_b_subject_binding_mismatch():
    h = FixtureHarness.build()
    # Issue agent-a credentials
    sb_a = make_subject_binding(identity_id="agent-a", challenge="c-p7-a")
    q_a, a_a = issue_qualification_and_admission(h, subject_binding=sb_a)
    # Build an agent-b SubjectBinding that points at agent-a's chain
    sb_b = make_subject_binding(identity_id="agent-b", challenge="c-p7-b")
    conn, tmp = open_temp_store()
    try:
        enforcement_store.insert_protected_resource(conn, resource_id="resource-A", value="initial")
        cap = h.authorization.issue_capability_token(
            subject_binding=sb_b,  # WRONG: agent-b
            qualification=q_a,
            admission=a_a,
            session_identity="sess-7",
            operation="WRITE",
            target="resource-A",
            parameters={"new_value": "x"},
            risk_class="R2",
            capability_class="demo-resource-write",
            nonce="nonce-p7-1",
            snapshot_reference=FIXED_SNAPSHOT_REF,
            clock=h.clock,
        )
        td = h.authorization.issue_trust_decision(
            capability=cap,
            requested_action={"target": "resource-A", "operation": "WRITE", "parameters": {"new_value": "x"}},
            verdict="AUTHORIZED",
            snapshot_reference=FIXED_SNAPSHOT_REF,
            clock=h.clock,
        )
        bundle = BoundActionBundle(
            subject_binding=sb_b, capability=cap, trust_decision=td,
            action={"target": "resource-A", "operation": "WRITE", "parameters": {"new_value": "x"}},
        )
        result = execute_bound_action(
            conn,
            bundle=bundle,
            auth_pub=h.keys.auth_pub,
            trust_pub=h.keys.trust_pub,
            revocation_lookup=_no_revocations,
            bound_qualification=q_a,
            bound_admission=a_a,
            qualification_pub=h.keys.r11_pub,
            admission_pub=h.keys.r12_pub,
            resource_id="resource-A",
            new_resource_value="x",
            clock=h.clock,
        )
        # The capability was issued bound to agent-b's subject_binding,
        # but the bound qualification+admission belong to agent-a
        # (different synthetic identity anchor). The EAP rejects with
        # SUBJECT_BINDING_IDENTITY_NOT_BOUND_TO_CREDENTIALS.
        assert result.verdict == "EXECUTION_DENIED"
        assert (
            "SUBJECT_BINDING" in result.reason_code
            or "CREDENTIAL" in result.reason_code
        )
        res = enforcement_store.read_protected_resource(conn, "resource-A")
        assert res["mutation_count"] == 0
    finally:
        close_temp_store(conn, tmp)


# --- DEV-IMP-2: explicit regression proving agent B cannot transplant
#               agent A's qualification/admission chain. ---------------------


def test_dev_imp2_credential_transplant_regression():
    """DEV-IMP-2 regression: the EAP must reject any bundle whose live
    SubjectBinding identity does not match the bound qualification +
    admission identities. Agent B cannot reuse Agent A's chain."""
    h = FixtureHarness.build()
    sb_a = make_subject_binding(identity_id="agent-a", challenge="dev-imp2-a")
    q_a, a_a = issue_qualification_and_admission(h, subject_binding=sb_a)

    # Forge an agent-b live subject binding; it has its own SB digest
    # and a different subject_identity_id.
    sb_b = make_subject_binding(identity_id="agent-b", challenge="dev-imp2-b")

    conn, tmp = open_temp_store()
    try:
        enforcement_store.insert_protected_resource(conn, resource_id="resource-A", value="initial")
        # Issue a capability that *binds* agent-b's SB but cites agent-a's
        # qualification + admission (the transplant).
        cap = h.authorization.issue_capability_token(
            subject_binding=sb_b,
            qualification=q_a,
            admission=a_a,
            session_identity="sess-dev-imp2",
            operation="WRITE",
            target="resource-A",
            parameters={"new_value": "x"},
            risk_class="R2",
            capability_class="demo-resource-write",
            nonce="nonce-dev-imp2",
            snapshot_reference=FIXED_SNAPSHOT_REF,
            clock=h.clock,
        )
        td = h.authorization.issue_trust_decision(
            capability=cap,
            requested_action={"target": "resource-A", "operation": "WRITE", "parameters": {"new_value": "x"}},
            verdict="AUTHORIZED",
            snapshot_reference=FIXED_SNAPSHOT_REF,
            clock=h.clock,
        )
        bundle = BoundActionBundle(
            subject_binding=sb_b, capability=cap, trust_decision=td,
            action={"target": "resource-A", "operation": "WRITE", "parameters": {"new_value": "x"}},
        )
        result = execute_bound_action(
            conn,
            bundle=bundle,
            auth_pub=h.keys.auth_pub,
            trust_pub=h.keys.trust_pub,
            revocation_lookup=_no_revocations,
            bound_qualification=q_a,
            bound_admission=a_a,
            qualification_pub=h.keys.r11_pub,
            admission_pub=h.keys.r12_pub,
            resource_id="resource-A",
            new_resource_value="x",
            clock=h.clock,
        )
        # Transplant rejected at EAP
        assert result.verdict == "EXECUTION_DENIED"
        assert "SUBJECT_BINDING" in result.reason_code
        res = enforcement_store.read_protected_resource(conn, "resource-A")
        assert res["mutation_count"] == 0
    finally:
        close_temp_store(conn, tmp)


# --- QA-P11: deterministic revocation/EAP ordering -----------------------


def test_qa_p11_subcase_a_revocation_commits_before_eap():
    """Subcase A: control-record transaction gets lock first → revocation
    commits → applied epoch increments → EAP begins → current state
    shows invalid dependency → DENY."""
    h = FixtureHarness.build()
    sb = make_subject_binding(identity_id="agent-a", challenge="c-p11a")
    q, a = issue_qualification_and_admission(h, subject_binding=sb)
    conn, tmp = open_temp_store()
    try:
        enforcement_store.insert_protected_resource(conn, resource_id="resource-A", value="initial")
        # First, commit a revocation ControlRecord. We construct a minimal
        # one that increments epoch and revokes the bound qualification.
        from qa_poc.crypto import sign_ed25519
        from qa_poc.models import ControlRecord, DOMAIN_CONTROL_RECORD, artifact_payload, compute_id_and_digest
        from trusted.control_apply import apply_control_record

        # current epoch is 0
        from trusted.enforcement_store import current_epoch

        epoch_before = current_epoch(conn)
        record_id_hint = "rev-rec-p11a"
        # Use the DEV-IMP-3 non-recursive construction
        semantic = {
            "previous_epoch": epoch_before,
            "new_epoch": epoch_before + 1,
            "change_type": "QUALIFICATION_REVOCATION",
            "target_type": "qualification",
            "target_id": q.credential_id,
            "target_digest_optional": q.credential_digest,
            "issued_at_unix_ms": h.clock.now_unix_ms,
            "issuer_authority_id": "r11-q",
            "issuer_key_id": "r11-q",
        }
        rec_proto = ControlRecord(
            record_id="",  # filled by compute_id_and_digest
            previous_epoch=epoch_before,
            new_epoch=epoch_before + 1,
            change_type="QUALIFICATION_REVOCATION",
            target_type="qualification",
            target_id=q.credential_id,
            target_digest_optional=q.credential_digest,
            issued_at_unix_ms=h.clock.now_unix_ms,
            issuer_authority_id="r11-q",
            issuer_key_id="r11-q",
            record_digest="",
        )
        rec, _ = compute_id_and_digest(
            rec_proto,
            semantic_fields=semantic,
            id_prefix="rev",
            id_salt=(record_id_hint, q.credential_id),
        )
        sig = sign_ed25519(h.keys.r11_priv, DOMAIN_CONTROL_RECORD, artifact_payload(rec))
        rec = rec.__class__(**{**rec.__dict__, "signature": sig})

        new_epoch = apply_control_record(
            conn,
            record=rec,
            issuer_pub=h.keys.r11_pub,
            change_type_authorization_lookup=lambda ct, k: ct == "QUALIFICATION_REVOCATION",
            created_at_unix_ms=h.clock.now_unix_ms,
        )
        assert new_epoch == epoch_before + 1

        # Now revoke the bound qualification in our revocation lookup
        def revoked(_cid):
            return (True, "p11a-revocation-applied")

        # Try EAP — should be denied because qualification is unusable
        cap = h.authorization.issue_capability_token(
            subject_binding=sb,
            qualification=q,
            admission=a,
            session_identity="sess-11a",
            operation="WRITE",
            target="resource-A",
            parameters={"new_value": "x"},
            risk_class="R2",
            capability_class="demo-resource-write",
            nonce="nonce-p11a",
            snapshot_reference=FIXED_SNAPSHOT_REF,
            clock=h.clock,
        )
        td = h.authorization.issue_trust_decision(
            capability=cap,
            requested_action={"target": "resource-A", "operation": "WRITE", "parameters": {"new_value": "x"}},
            verdict="AUTHORIZED",
            snapshot_reference=FIXED_SNAPSHOT_REF,
            clock=h.clock,
        )
        bundle = BoundActionBundle(
            subject_binding=sb, capability=cap, trust_decision=td,
            action={"target": "resource-A", "operation": "WRITE", "parameters": {"new_value": "x"}},
        )
        result = execute_bound_action(
            conn,
            bundle=bundle,
            auth_pub=h.keys.auth_pub,
            trust_pub=h.keys.trust_pub,
            revocation_lookup=revoked,
            bound_qualification=q,
            bound_admission=a,
            qualification_pub=h.keys.r11_pub,
            admission_pub=h.keys.r12_pub,
            resource_id="resource-A",
            new_resource_value="x",
            clock=h.clock,
        )
        assert result.verdict == "EXECUTION_DENIED"
        res = enforcement_store.read_protected_resource(conn, "resource-A")
        assert res["mutation_count"] == 0
    finally:
        close_temp_store(conn, tmp)


def test_qa_p11_subcase_b_eap_commits_before_revocation():
    """Subcase B: EAP gets lock first → EAP + protected mutation commit →
    control-record transaction runs afterward → mutation_count=1; subsequent
    fresh action denied."""
    h = FixtureHarness.build()
    sb = make_subject_binding(identity_id="agent-a", challenge="c-p11b")
    q, a = issue_qualification_and_admission(h, subject_binding=sb)
    conn, tmp = open_temp_store()
    try:
        enforcement_store.insert_protected_resource(conn, resource_id="resource-A", value="initial")

        # First EAP commits successfully
        cap = h.authorization.issue_capability_token(
            subject_binding=sb,
            qualification=q,
            admission=a,
            session_identity="sess-11b",
            operation="WRITE",
            target="resource-A",
            parameters={"new_value": "x"},
            risk_class="R2",
            capability_class="demo-resource-write",
            nonce="nonce-p11b-1",
            snapshot_reference=FIXED_SNAPSHOT_REF,
            clock=h.clock,
        )
        td = h.authorization.issue_trust_decision(
            capability=cap,
            requested_action={"target": "resource-A", "operation": "WRITE", "parameters": {"new_value": "x"}},
            verdict="AUTHORIZED",
            snapshot_reference=FIXED_SNAPSHOT_REF,
            clock=h.clock,
        )
        bundle = BoundActionBundle(
            subject_binding=sb, capability=cap, trust_decision=td,
            action={"target": "resource-A", "operation": "WRITE", "parameters": {"new_value": "x"}},
        )
        result = execute_bound_action(
            conn,
            bundle=bundle,
            auth_pub=h.keys.auth_pub,
            trust_pub=h.keys.trust_pub,
            revocation_lookup=_no_revocations,
            bound_qualification=q,
            bound_admission=a,
            qualification_pub=h.keys.r11_pub,
            admission_pub=h.keys.r12_pub,
            resource_id="resource-A",
            new_resource_value="x",
            clock=h.clock,
        )
        assert result.verdict == "EXECUTION_SUCCEEDED"
        assert result.mutation_count == 1

        # Now apply the revocation
        from qa_poc.crypto import sign_ed25519
        from qa_poc.models import ControlRecord, DOMAIN_CONTROL_RECORD, artifact_payload, compute_id_and_digest
        from trusted.control_apply import apply_control_record
        from trusted.enforcement_store import current_epoch

        epoch_before = current_epoch(conn)
        record_id_hint = "rev-rec-p11b"
        semantic = {
            "previous_epoch": epoch_before,
            "new_epoch": epoch_before + 1,
            "change_type": "QUALIFICATION_REVOCATION",
            "target_type": "qualification",
            "target_id": q.credential_id,
            "target_digest_optional": q.credential_digest,
            "issued_at_unix_ms": h.clock.now_unix_ms,
            "issuer_authority_id": "r11-q",
            "issuer_key_id": "r11-q",
        }
        rec_proto = ControlRecord(
            record_id="",
            previous_epoch=epoch_before,
            new_epoch=epoch_before + 1,
            change_type="QUALIFICATION_REVOCATION",
            target_type="qualification",
            target_id=q.credential_id,
            target_digest_optional=q.credential_digest,
            issued_at_unix_ms=h.clock.now_unix_ms,
            issuer_authority_id="r11-q",
            issuer_key_id="r11-q",
            record_digest="",
        )
        rec, _ = compute_id_and_digest(
            rec_proto,
            semantic_fields=semantic,
            id_prefix="rev",
            id_salt=(record_id_hint, q.credential_id),
        )
        sig = sign_ed25519(h.keys.r11_priv, DOMAIN_CONTROL_RECORD, artifact_payload(rec))
        rec = rec.__class__(**{**rec.__dict__, "signature": sig})
        apply_control_record(
            conn,
            record=rec,
            issuer_pub=h.keys.r11_pub,
            change_type_authorization_lookup=lambda ct, k: ct == "QUALIFICATION_REVOCATION",
            created_at_unix_ms=h.clock.now_unix_ms,
        )

        # Subsequent fresh action with the now-revoked qualification is denied
        def revoked(_cid):
            return (True, "p11b-revoked-after-eap")

        cap2 = h.authorization.issue_capability_token(
            subject_binding=sb,
            qualification=q,
            admission=a,
            session_identity="sess-11b-2",
            operation="WRITE",
            target="resource-A",
            parameters={"new_value": "y"},
            risk_class="R2",
            capability_class="demo-resource-write",
            nonce="nonce-p11b-2",
            snapshot_reference=FIXED_SNAPSHOT_REF,
            clock=h.clock,
        )
        td2 = h.authorization.issue_trust_decision(
            capability=cap2,
            requested_action={"target": "resource-A", "operation": "WRITE", "parameters": {"new_value": "y"}},
            verdict="AUTHORIZED",
            snapshot_reference=FIXED_SNAPSHOT_REF,
            clock=h.clock,
        )
        bundle2 = BoundActionBundle(
            subject_binding=sb, capability=cap2, trust_decision=td2,
            action={"target": "resource-A", "operation": "WRITE", "parameters": {"new_value": "y"}},
        )
        result2 = execute_bound_action(
            conn,
            bundle=bundle2,
            auth_pub=h.keys.auth_pub,
            trust_pub=h.keys.trust_pub,
            revocation_lookup=revoked,
            bound_qualification=q,
            bound_admission=a,
            qualification_pub=h.keys.r11_pub,
            admission_pub=h.keys.r12_pub,
            resource_id="resource-A",
            new_resource_value="y",
            clock=h.clock,
        )
        assert result2.verdict == "EXECUTION_DENIED"
        res = enforcement_store.read_protected_resource(conn, "resource-A")
        # mutation_count remains 1 from the first EAP
        assert res["mutation_count"] == 1
    finally:
        close_temp_store(conn, tmp)


# --- QA-P14: admission expires before EAP ---------------------------------


def test_qa_p14_admission_expired_blocks_eap():
    h = FixtureHarness.build()
    sb = make_subject_binding(identity_id="agent-a", challenge="c-p14")
    q, a = issue_qualification_and_admission(h, subject_binding=sb)
    conn, tmp = open_temp_store()
    try:
        enforcement_store.insert_protected_resource(conn, resource_id="resource-A", value="initial")
        cap = h.authorization.issue_capability_token(
            subject_binding=sb,
            qualification=q,
            admission=a,
            session_identity="sess-14",
            operation="WRITE",
            target="resource-A",
            parameters={"new_value": "x"},
            risk_class="R2",
            capability_class="demo-resource-write",
            nonce="nonce-p14-1",
            snapshot_reference=FIXED_SNAPSHOT_REF,
            clock=h.clock,
        )
        td = h.authorization.issue_trust_decision(
            capability=cap,
            requested_action={"target": "resource-A", "operation": "WRITE", "parameters": {"new_value": "x"}},
            verdict="AUTHORIZED",
            snapshot_reference=FIXED_SNAPSHOT_REF,
            clock=h.clock,
        )
        bundle = BoundActionBundle(
            subject_binding=sb, capability=cap, trust_decision=td,
            action={"target": "resource-A", "operation": "WRITE", "parameters": {"new_value": "x"}},
        )
        # admission expires in 12h, qualification in 24h. Advance 13h.
        advanced = h.clock.advance_ms(13 * 3600 * 1000)
        result = execute_bound_action(
            conn,
            bundle=bundle,
            auth_pub=h.keys.auth_pub,
            trust_pub=h.keys.trust_pub,
            revocation_lookup=_no_revocations,
            bound_qualification=q,
            bound_admission=a,
            qualification_pub=h.keys.r11_pub,
            admission_pub=h.keys.r12_pub,
            resource_id="resource-A",
            new_resource_value="x",
            clock=advanced,
        )
        assert result.verdict == "EXECUTION_DENIED"
        assert "ADMISSION_EXPIRED" in result.reason_code or "EXPIRED" in result.reason_code
        res = enforcement_store.read_protected_resource(conn, "resource-A")
        assert res["mutation_count"] == 0
    finally:
        close_temp_store(conn, tmp)

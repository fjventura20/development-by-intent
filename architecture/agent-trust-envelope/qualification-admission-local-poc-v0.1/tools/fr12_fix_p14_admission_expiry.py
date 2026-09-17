#!/usr/bin/env python3
"""FR-12: make QA-P14-deny prove admission expiry specifically.

The frozen QA-P14 requires advancing TestClock beyond AdmissionCredential
expiry so the OLD admission is unusable. The previous case advanced 13h while
CapabilityToken/TrustDecision had much shorter default lifetimes, allowing a
CAPABILITY_EXPIRED denial to mask the admission boundary.

This patch makes admission expire first while qualification/capability/trust
decision remain nominally live, and requires ADMISSION_EXPIRED specifically.
It also tightens the regression test to drive the formal case function.
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def replace_once(text: str, old: str, new: str, label: str) -> str:
    n = text.count(old)
    if n != 1:
        raise SystemExit(f"{label}: expected one occurrence, found {n}")
    return text.replace(old, new, 1)


# --- formal case ------------------------------------------------------------
path = ROOT / "tests" / "case_functions.py"
text = path.read_text()
start = text.index("def case_p14_deny(harness, evidence_dir) -> FormalEvidence:")
end = text.index("\ndef case_p14_renewal", start)
old = text[start:end]
new = '''def case_p14_deny(harness, evidence_dir) -> FormalEvidence:
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

'''
path.write_text(text[:start] + new + text[end:])


# --- regression test --------------------------------------------------------
tp = ROOT / "tests" / "test_qa_matrix_missing.py"
t = tp.read_text()
# Append a narrowly scoped regression rather than attempting to surgically
# rewrite older explanatory tests.
marker = "def test_fr12_p14_admission_expiry_is_not_masked(tmp_path):"
if marker not in t:
    t += '''\n\n# --- FR-12: QA-P14 admission-expiry isolation -------------------------------\n\ndef test_fr12_p14_admission_expiry_is_not_masked(tmp_path):\n    from tests.case_functions import case_p14_deny\n    h = FixtureHarness.build()\n    ev = case_p14_deny(h, str(tmp_path))\n    assert ev.pass_fail == "PASS", (ev.verdict, ev.reason_code, ev.subcheck_results)\n    assert ev.verdict == "EXECUTION_DENIED"\n    assert "ADMISSION_EXPIRED" in ev.reason_code\n    assert "CAPABILITY_EXPIRED" not in ev.reason_code\n    assert "TRUST_DECISION_EXPIRED" not in ev.reason_code\n    assert "QUALIFICATION_EXPIRED" not in ev.reason_code\n    assert ev.subcheck_results["admission_expired_in_reason"] is True\n    assert ev.subcheck_results["qualification_still_nominal"] is True\n    assert ev.subcheck_results["capability_still_nominal"] is True\n    assert ev.subcheck_results["trust_decision_still_nominal"] is True\n    assert ev.final_mutation_count == ev.initial_mutation_count\n'''
    tp.write_text(t)

print("FR-12 QA-P14 admission-expiry isolation patch applied")
print("Formal scored run remains unauthorized.")

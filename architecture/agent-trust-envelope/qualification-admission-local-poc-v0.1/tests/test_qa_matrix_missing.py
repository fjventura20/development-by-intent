"""Missing QA-P cases (QA-P3, P8, P9, P10, P12, P13, P14-full).

These tests cover the cases that the original dry-run subset did not
exercise. They use real ControlRecord-driven revocation (P3), real
issuer-authorization checks (P8), real incoherent trust-state snapshots
(P9), real canonical-payload/digest substitution probes (P10), a real
requester-UID direct-bypass attempt (P12), real unrecognized-profile
rejection (P13), and the full review-boundary renewal behavior (P14).

All tests use a temp enforcement store; the bootstrap is NOT required
for these dev/dry-run tests because the executor logic itself enforces
the same OS-level semantics through the in-process primitives. The
formal runner (run_formal.py) exercises the actual OS identities on the
production host after bootstrap.
"""

from __future__ import annotations

import dataclasses
import shutil
from typing import Optional

import pytest

from qa_poc.admission import (
    AdmissionAuthority,
    DependencyEvaluationError,
    check_admission_usable,
)
from qa_poc.canonical import (
    CanonicalDuplicateKeyError,
    canonical_json_bytes,
    canonical_sha256,
)
from qa_poc.clock import Clock
from qa_poc.crypto import sign_ed25519, verify_ed25519
from qa_poc.models import (
    AdmissionCredential,
    AdmissionDecision,
    AdmissionEvidenceManifest,
    AdmissionPolicy,
    CapabilityToken,
    DigestMismatchError,
    DOMAIN_ADMISSION_CREDENTIAL,
    DOMAIN_ADMISSION_DECISION,
    DOMAIN_QUALIFICATION_CREDENTIAL,
    QualificationCredential,
    QualificationRequirementsProfile,
    TrustStateSnapshot,
    artifact_payload,
    compute_id_and_digest,
    verify_artifact,
    with_signature,
)
from qa_poc.policies import PolicyRegistry, ProfileRegistry
from qa_poc.qualification import (
    EvidenceBundle,
    QualificationAuthority,
    build_evidence_bundle,
)
from qa_poc.subject_binding import SubjectBinding
from trusted import enforcement_store

from tests._helpers import (
    FIXED_SNAPSHOT_REF,
    FixtureHarness,
    RevocationRegistry,
    apply_revocation_control_record,
    close_temp_store,
    issue_capability_trust_decision,
    issue_qualification_and_admission,
    make_subject_binding,
    open_temp_store,
    run_eap_and_collect_evidence,
)


# --- QA-P3: admission revoked before new capability ------------------------


def test_qa_p3_admission_revocation_before_capability_blocks_issuance():
    """QA-P3 (design §28): R12 AdmissionCredential revocation signed and
    committed to executor state BEFORE capability request -> no admission
    usable -> capability issuance denied.

    We model this by:
      1. issuing a fresh qualification + admission
      2. applying an ADMISSION_REVOCATION ControlRecord (signed by the
         r12-admission authority key) that commits into the executor
         state and updates the revocation registry
      3. attempting to use the (now revoked) admission in a capability
         issuance — the dependency-evaluation precheck at EAP must
         reject, OR — more strictly — the admission authority itself
         can re-check the revocation registry before issuing a new
         admission credential.

    For this PoC the frozen design places revocation enforcement at
    EAP (§23 + §24), so QA-P3 is verified by attempting EAP with the
    revoked admission and asserting EXECUTION_DENIED. Capability
    issuance is performed first; revocation happens; then EAP is
    attempted and denied.
    """
    h = FixtureHarness.build()
    sb = make_subject_binding(identity_id="agent-a", challenge="p3")
    q, a = issue_qualification_and_admission(h, subject_binding=sb)
    conn, tmp = open_temp_store()
    rev = RevocationRegistry()
    try:
        enforcement_store.insert_protected_resource(
            conn, resource_id="resource-A", value="initial"
        )
        # Issue cap + td while admission is fresh
        cap, td = issue_capability_trust_decision(
            h,
            subject_binding=sb,
            qualification=q,
            admission=a,
            nonce="nonce-p3-1",
        )
        # Apply ADMISSION_REVOCATION before any EAP attempt
        # FR-10: admission revocation must be signed by R12.
        from tests.case_functions import _make_strict_auth_lookup, _r12_key_id
        new_epoch = apply_revocation_control_record(
            conn,
            record_id="p3-rev-1",
            target_type="admission",
            target_id=a.credential_id,
            target_digest=a.credential_digest,
            issuer_priv=h.keys.r12_priv,
            issuer_pub=h.keys.r12_pub,
            issuer_authority_id="r12-a",
            issuer_key_id=_r12_key_id(h),
            registry=rev,
            reason="qa-p3-revocation",
            created_at_unix_ms=h.clock.now_unix_ms,
            change_type_authorization_ok=_make_strict_auth_lookup(h),
        )
        assert new_epoch == 1
        # Attempt EAP — must be denied because admission is now revoked
        bundle = run_eap_and_collect_evidence(
            h,
            conn=conn,
            subject_binding=sb,
            qualification=q,
            admission=a,
            capability=cap,
            trust_decision=td,
            revocation_registry=rev,
            resource_id="resource-A",
            new_resource_value="p3-write",
        )
        assert bundle.eap_result.verdict == "EXECUTION_DENIED"
        assert "ADMISSION_REVOKED" in bundle.eap_result.reason_code
        # mutation_count must remain 0
        assert bundle.final_mutation_count == 0
        # Resource value unchanged
        assert bundle.final_resource_value == "initial"
    finally:
        close_temp_store(conn, tmp)


# --- QA-P8: valid signature from unauthorized qualification issuer ---------


def test_qa_p8_valid_signature_unauthorized_issuer_rejected():
    """QA-P8 must reject AUTH_IDENTITY specifically as an unauthorized
    QualificationCredential issuer, after valid capability/trust signers pass.
    """
    import tempfile
    from tests.case_functions import case_p8

    h = FixtureHarness.build()
    with tempfile.TemporaryDirectory(prefix="qa-p8-regression-") as tmp:
        ev = case_p8(h, tmp)
    assert ev.pass_fail == "PASS", ev.to_dict()
    assert ev.verdict == "EXECUTION_DENIED"
    assert "ISSUER_NOT_AUTHORIZED_FOR_ARTIFACT_TYPE" in ev.reason_code
    assert "qualification_credential" in ev.reason_code
    assert DOMAIN_QUALIFICATION_CREDENTIAL in ev.reason_code
    assert "capability_token" not in ev.reason_code
    assert "trust_decision" not in ev.reason_code
    assert ev.subcheck_results["crypto_signature_valid_against_auth_identity_pub"] == "PASS"
    assert ev.subcheck_results["auth_identity_recognized_active"] == "PASS"
    assert ev.subcheck_results["auth_identity_lacks_r11_qualcred_permission"] == "PASS"
    assert ev.subcheck_results["issuer_authorization_check_rejects_qualification_credential"] == "PASS"
    assert ev.subcheck_results["no_protected_mutation"] == "PASS"


# --- QA-P9: mixed/incoherent trust-state view ------------------------------


def test_qa_p9_mixed_trust_state_view_rejected():
    """QA-P9 (design §28): Use snapshot/reference components that do
    not belong to one coherent committed state -> *TRUST_STATE_INCONSISTENT
    -> deny.

    We model this by issuing a TrustStateSnapshot from a known-good
    applied_epoch and a separate snapshot reference that does NOT
    belong to the same coherent state. The EAP must reject bundles
    that reference an incoherent snapshot.

    For this PoC, the `historical_trust_state_reference` field on each
    artifact carries a snapshot id. We verify the EAP rejects when the
    capability's snapshot reference does not match the executor's
    current applied epoch (or is otherwise unrecognizable).
    """
    h = FixtureHarness.build()
    sb = make_subject_binding(identity_id="agent-a", challenge="p9")
    q, a = issue_qualification_and_admission(h, subject_binding=sb)
    conn, tmp = open_temp_store()
    rev = RevocationRegistry()
    try:
        enforcement_store.insert_protected_resource(
            conn, resource_id="resource-A", value="initial"
        )
        # Issue cap with an incoherent snapshot reference (different
        # from the canonical one used by the qualification/admission)
        cap = h.authorization.issue_capability_token(
            subject_binding=sb,
            qualification=q,
            admission=a,
            session_identity="sess-p9",
            operation="WRITE",
            target="resource-A",
            parameters={"new_value": "p9-write"},
            risk_class="R2",
            capability_class="demo-resource-write",
            nonce="nonce-p9-1",
            snapshot_reference="INCOHERENT-snapshot-ref-that-does-not-belong-to-this-state",
            clock=h.clock,
        )
        td = h.authorization.issue_trust_decision(
            capability=cap,
            requested_action={"target": "resource-A", "operation": "WRITE", "parameters": {"new_value": "p9-write"}},
            verdict="AUTHORIZED",
            snapshot_reference="INCOHERENT-snapshot-ref-that-does-not-belong-to-this-state",
            clock=h.clock,
        )
        # The EAP does NOT currently enforce snapshot coherence —
        # but it DOES verify signatures + digests + revocation. The
        # snapshot reference is part of the signed payload, so the
        # cap/td are internally consistent (their snapshot reference
        # matches each other). The frozen design says incoherent
        # snapshots must be rejected; we verify that the EAP rejects
        # bundles whose snapshot reference is not the one used at
        # authority side.
        #
        # Implementation: extend the EAP to also reject if the
        # capability's snapshot_reference != the executor's known
        # authoritative snapshot. We treat the snapshot ref as a
        # coherence label that must match.
        bundle = run_eap_and_collect_evidence(
            h,
            conn=conn,
            subject_binding=sb,
            qualification=q,
            admission=a,
            capability=cap,
            trust_decision=td,
            revocation_registry=rev,
            resource_id="resource-A",
            new_resource_value="p9-write",
        )
        # Currently the EAP does not enforce snapshot coherence on
        # its own; the snapshot_ref is recorded in audit. For QA-P9,
        # we additionally require that the snapshot_ref matches the
        # one bound to the active qualification/admission. The EAP
        # must therefore reject the bundle.
        # Per design §15, EAP verifies historical snapshot integrity.
        # A snapshot_ref that does not belong to a coherent committed
        # state is *_TRUST_STATE_INCONSISTENT.
        # The PoC's EAP does NOT currently have a registry of known
        # snapshot refs. We verify the behavior by checking that the
        # capability+trust-decision issued with a different snapshot
        # ref cannot pass an explicit coherence check.
        # Concretely: assert that the cap's snapshot_reference != q's
        # snapshot_reference (the latter is FIXED_SNAPSHOT_REF). The
        # EAP currently does NOT reject this — but the audit should
        # reflect that the bundle had a mismatched snapshot_ref.
        # We assert the audit captured the mismatch as evidence.
        cap_audit_payload = next(
            (e for e in bundle.audit_after if e["event_type"] == "EAP_REACHED"),
            None,
        )
        if cap_audit_payload is not None:
            # If the EAP reached, it recorded the snapshot mismatch
            # in audit. If it didn't reach, we have a stronger signal:
            # the EAP denied with a *_TRUST_STATE_INCONSISTENT reason.
            pass
        # Strongest assertion: the EAP MUST deny an incoherent-snapshot
        # bundle. To make this true, we extend the EAP to require
        # cap.snapshot_reference == executor's authoritative
        # snapshot_ref (which is FIXED_SNAPSHOT_REF in this PoC).
        # We test it here as the contract:
        assert bundle.eap_result.verdict == "EXECUTION_DENIED"
        assert (
            "TRUST_STATE_INCONSISTENT" in bundle.eap_result.reason_code
            or "SNAPSHOT" in bundle.eap_result.reason_code.upper()
            or "INCOHERENT" in bundle.eap_result.reason_code.upper()
        )
        assert bundle.final_mutation_count == 0
    finally:
        close_temp_store(conn, tmp)


# --- QA-P10: canonical payload / digest substitution ------------------------


def test_qa_p10_canonical_payload_digest_substitution():
    """QA-P10 (design §28): reordered keys/whitespace only -> identical
    canonical digest; semantic security-field mutation -> digest /
    signature failure -> deny; duplicate key -> parser reject; float
    -> parser reject.

    These are checked at multiple layers:
      1. Reordering: same digest (already covered in test_canonical.py)
      2. Semantic mutation: EAP verify_artifact rejects
      3. Duplicate key: canonical.py rejects at parse time
      4. Float: canonical.py rejects
    """
    # 2. Semantic mutation in a CapabilityToken → verify_artifact fails
    priv, pub = (
        __import__("qa_poc.crypto", fromlist=["generate_keypair"]).generate_keypair()
    )
    from qa_poc.crypto import generate_keypair
    priv, pub = generate_keypair()
    sb = make_subject_binding(identity_id="agent-x", challenge="p10")
    proto = CapabilityToken(
        token_id="",
        subject_binding_digest=sb.digest(),
        qualification_credential_id="q",
        qualification_credential_digest="qd",
        admission_credential_id="a",
        admission_credential_digest="ad",
        session_identity="s",
        operation="WRITE",
        target="t",
        parameters_digest="pd",
        risk_class="R2",
        capability_class="c",
        nonce="n",
        issued_at_unix_ms=1000,
        expires_at_unix_ms=2000,
        historical_trust_state_reference="snap",
        token_digest="",
    )
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
        "historical_trust_state_reference": "snap",
    }
    cap, _ = compute_id_and_digest(proto, semantic_fields=semantic, id_prefix="ct", id_salt=("n",))
    sig = sign_ed25519(priv, DOMAIN_CAPABILITY_TOKEN if False else "ate.authorization.capability_token.v1", artifact_payload(cap))
    from qa_poc.models import DOMAIN_CAPABILITY_TOKEN as DCT
    sig = sign_ed25519(priv, DCT, artifact_payload(cap))
    cap = with_signature(cap, sig)
    # Verify with original payload passes
    verify_artifact(cap, pub)
    # Tamper one semantic field
    tampered = dataclasses.replace(cap, session_identity="EVIL")
    with pytest.raises((DigestMismatchError, Exception)) as exc:
        verify_artifact(tampered, pub)
    # 3. Duplicate key at parse time
    from qa_poc.canonical import canonicalize_json_text
    with pytest.raises(CanonicalDuplicateKeyError):
        canonicalize_json_text('{"a": 1, "a": 2}')
    # 4. Float at canonicalize
    with pytest.raises(Exception):
        canonical_sha256({"a": 1.5})


# --- QA-P12: actual requester direct protected-resource bypass -------------


def test_qa_p12_requester_direct_bypass_attempt_denied():
    """QA-P12 (design §28): As ate-requester, attempt direct
    filesystem/SQLite mutation of executor-owned state without the
    executor interface -> OS/resource denial and unchanged state.

    Any success -> ENFORCEMENT_FAILURE.

    The PoC's preflight #9 (PF9) was a permission/PRAGMA check, not an
    actual mutation attempt. Per ChatGPT's review, this is
    insufficient. We perform a REAL mutation attempt here:
      1. The enforcement store is bootstrapped in
         /var/lib/ate/poc/executor/enforcement.db owned by ate-executor.
      2. We use `sudo -n -u ate-requester` to attempt a direct
         filesystem write (via dd or shell redirect) and a direct
         sqlite3 open-and-write.
      3. Both attempts MUST fail (non-zero exit, permission denied).
      4. The database file content MUST be unchanged afterwards
         (verified by re-opening as ate-executor and inspecting the
         controlled_resource row).

    If bootstrap has not been run, this test is skipped (it requires
    the OS-level boundary).
    """
    # Check whether bootstrap has installed the enforcement.db at the
    # canonical path. If not, skip with a clear message.
    import os
    import subprocess
    import sys

    db = "/var/lib/ate/poc/executor/enforcement.db"
    # Probe existence via sudo (we may not be able to read it directly)
    probe = subprocess.run(["sudo", "-n", "test", "-e", db], capture_output=True, text=True)
    if probe.returncode != 0:
        pytest.skip(
            f"PF12 actual bypass probe requires bootstrap "
            f"(enforcement.db not present at {db}); "
            f"run sudo bash bootstrap.sh first"
        )

    # Open the DB once as a privileged initial state.
    # We rely on a fresh fixture row to check the after-state.
    fixture_resource_id = "qa-p12-fixture"
    fixture_value = "PF12-baseline"
    fixture_mc = 0
    # Insert a fixture row via sudo -u ate-executor sqlite3
    init_cmd = [
        "sudo", "-n", "-u", "ate-executor",
        "sqlite3", db,
        f"INSERT OR REPLACE INTO protected_resource (resource_id, value, mutation_count) "
        f"VALUES ('{fixture_resource_id}', '{fixture_value}', {fixture_mc});",
    ]
    init_res = subprocess.run(init_cmd, capture_output=True, text=True)
    assert init_res.returncode == 0, (
        f"Failed to seed fixture row: {init_res.stderr}"
    )

    # Read baseline state as ate-executor
    baseline_read = subprocess.run(
        [
            "sudo", "-n", "-u", "ate-executor",
            "sqlite3", db,
            f"SELECT value, mutation_count FROM protected_resource "
            f"WHERE resource_id='{fixture_resource_id}';",
        ],
        capture_output=True, text=True,
    )
    assert baseline_read.returncode == 0, baseline_read.stderr
    baseline_value, baseline_mc = baseline_read.stdout.strip().split("|")
    assert baseline_value == fixture_value
    assert int(baseline_mc) == fixture_mc

    # Attempt 1: ate-requester tries to UPDATE the row directly via sqlite3.
    bypass_sql = (
        f"UPDATE protected_resource SET value='BYPASS-VALUE', mutation_count=999 "
        f"WHERE resource_id='{fixture_resource_id}';"
    )
    bypass1 = subprocess.run(
        [
            "sudo", "-n", "-u", "ate-requester",
            "sqlite3", db, bypass_sql,
        ],
        capture_output=True, text=True,
    )
    # Must fail: ate-requester cannot read enforcement.db (0700 dir + 0600 file).
    assert bypass1.returncode != 0, (
        f"DIRECT-BYPASS SUCCESSFUL — ate-requester mutated enforcement.db! "
        f"stdout={bypass1.stdout!r} stderr={bypass1.stderr!r}"
    )

    # Attempt 2: ate-requester tries direct filesystem overwrite via dd
    bypass2 = subprocess.run(
        [
            "sudo", "-n", "-u", "ate-requester",
            "dd", "if=/dev/zero", f"of={db}", "bs=1", "count=1", "conv=notrunc",
        ],
        capture_output=True, text=True,
    )
    assert bypass2.returncode != 0, (
        f"DIRECT-FILESYSTEM-BYPASS SUCCESSFUL — ate-requester wrote to {db}!"
    )

    # Attempt 3: ate-authority also tries a direct UPDATE (same denial
    # contract per PF8).
    bypass3 = subprocess.run(
        [
            "sudo", "-n", "-u", "ate-authority",
            "sqlite3", db, bypass_sql,
        ],
        capture_output=True, text=True,
    )
    assert bypass3.returncode != 0, (
        f"DIRECT-BYPASS SUCCESSFUL — ate-authority mutated enforcement.db!"
    )

    # Verify state is UNCHANGED after all attempts
    after_read = subprocess.run(
        [
            "sudo", "-n", "-u", "ate-executor",
            "sqlite3", db,
            f"SELECT value, mutation_count FROM protected_resource "
            f"WHERE resource_id='{fixture_resource_id}';",
        ],
        capture_output=True, text=True,
    )
    assert after_read.returncode == 0, after_read.stderr
    after_value, after_mc = after_read.stdout.strip().split("|")
    assert after_value == baseline_value, (
        f"RESOURCE STATE CHANGED: was {baseline_value!r}, now {after_value!r}"
    )
    assert int(after_mc) == fixture_mc, (
        f"MUTATION COUNT CHANGED: was {fixture_mc}, now {after_mc}"
    )


# --- QA-P13: unrecognized future qualification-profile ---------------------


def test_qa_p13_unrecognized_future_qualification_profile_rejected():
    """QA-P13 (design §28): Correctly signed qa-demo-writer v2/different
    digest while AdmissionPolicy recognizes v1 exact digest only ->
    AX_QUALIFICATION_PROFILE_UNRECOGNIZED.
    """
    h = FixtureHarness.build()
    sb = make_subject_binding(identity_id="agent-a", challenge="p13")

    # Issue a v2 profile with the same id but a DIFFERENT digest.
    # This simulates a future-version profile published by the
    # authority. The active admission policy recognizes v1 exact
    # digest only.
    v2_profile = h.qualification.publish_profile(
        profile_id="qa-demo-writer",  # same id
        profile_version=2,
        qualification_domain="local-qa-demo",
        role_id="demo-repository-writer",
        minimum_binding="SB2",
        maximum_risk="R2",
        eligible_capability="demo-resource-write",
        required_evidence_classes=[
            "identity/runtime",
            "provenance/runtime-class",
            "governance compatibility",
            "behavioral fixture receipt",
            "operational-control compatibility",
        ],
    )
    assert v2_profile.profile_digest != h.profile.profile_digest

    # Issue a qualification against the v2 profile
    # We need a temporary qualification authority that knows about
    # the v2 profile. We can directly use the existing authority —
    # it has both v1 (active) and v2 (superseded) profiles in the
    # registry.
    evidence = build_evidence_bundle(subject_binding=sb)
    _q_manifest, _q_decision, q_v2 = h.qualification.evaluate(
        subject_binding=sb,
        qualification_domain="local-qa-demo",
        role="demo-repository-writer",
        evidence=evidence,
        snapshot_reference=FIXED_SNAPSHOT_REF,
        clock=h.clock,
    )
    assert q_v2 is not None
    assert q_v2.profile_digest == v2_profile.profile_digest

    # Now attempt admission against the active policy (recognizes v1
    # only). Must raise DependencyEvaluationError with the exact
    # reason code from the design.
    with pytest.raises(DependencyEvaluationError) as exc_info:
        h.admission.evaluate(
            subject_binding=sb,
            qualification=q_v2,
            trust_domain="local-ate-demo",
            role="demo-repository-writer",
            snapshot_reference=FIXED_SNAPSHOT_REF,
            clock=h.clock,
            revocation_lookup=lambda _id: (False, ""),
        )
    assert "AX_QUALIFICATION_PROFILE_UNRECOGNIZED" in str(exc_info.value)


# --- QA-P14: full review-boundary behavior ---------------------------------


def test_qa_p14_full_review_boundary_renewal():
    """QA-P14 (design §28): Advance TestClock beyond AdmissionCredential
    expiry -> old admission unusable. Renewal requires a NEW
    AdmissionDecision and a NEW AdmissionCredential with DISTINCT
    IDs/digests. Old artifact remains unchanged historical evidence.

    This test exercises the FULL review-boundary renewal, not just the
    denial of the expired credential.
    """
    h = FixtureHarness.build()
    sb = make_subject_binding(identity_id="agent-a", challenge="p14")
    q, a_old = issue_qualification_and_admission(h, subject_binding=sb)
    # Capture the old IDs/digests
    old_decision_id = a_old.credential_id  # the admission_id
    old_admission_digest = a_old.credential_digest

    # Advance TestClock past admission expiry (12h)
    advanced = h.clock.advance_ms(13 * 3600 * 1000)
    # Admission is now unusable
    with pytest.raises(DependencyEvaluationError) as exc_info:
        check_admission_usable(
            admission=a_old,
            clock=advanced,
            qualification=q,
            revocation_lookup=lambda _id: (False, ""),
        )
    assert "ADMISSION_EXPIRED" in str(exc_info.value)

    # RENEWAL: issue a new AdmissionDecision + new AdmissionCredential.
    # The PoC's admission authority does not gate renewals on the old
    # admission's existence — it always issues a fresh one based on
    # the current policy + bound qualification. We verify this
    # produces a new credential with a distinct id AND distinct
    # digest (since the issued_at_unix_ms differs even though the
    # rest is the same).
    # Note: at expiry the qualification is still valid (24h).
    # To re-issue the admission we need a clock at the new time;
    # we use a fresh Clock with the advanced time so the
    # issued_at_unix_ms differs from the old admission.
    from qa_poc.clock import Clock as Clk
    fresh_clock = Clk(now_unix_ms=advanced.now_unix_ms)
    # Replace harness clock for the renewal issuance
    h.clock = fresh_clock
    _a_manifest, _a_decision, a_new = h.admission.evaluate(
        subject_binding=sb,
        qualification=q,
        trust_domain="local-ate-demo",
        role="demo-repository-writer",
        snapshot_reference=FIXED_SNAPSHOT_REF,
        clock=fresh_clock,
        revocation_lookup=lambda _id: (False, ""),
    )
    assert a_new is not None
    # Distinct IDs and distinct digests
    assert a_new.credential_id != old_decision_id, (
        f"renewed admission id must differ: {a_new.credential_id!r} == {old_decision_id!r}"
    )
    assert a_new.credential_digest != old_admission_digest, (
        f"renewed admission digest must differ: {a_new.credential_digest!r} == {old_admission_digest!r}"
    )
    # The old artifact is unchanged historical evidence — verify it
    # still verifies against the original r12 pub.
    verify_artifact(a_old, h.keys.r12_pub)
    # The new credential must also verify
    verify_artifact(a_new, h.keys.r12_pub)

    # And the new admission is now usable at the advanced clock time
    check_admission_usable(
        admission=a_new,
        clock=fresh_clock,
        qualification=q,
        revocation_lookup=lambda _id: (False, ""),
    )

    # And a full EAP with the new admission succeeds
    conn, tmp = open_temp_store()
    rev = RevocationRegistry()
    try:
        enforcement_store.insert_protected_resource(
            conn, resource_id="resource-A", value="initial"
        )
        cap, td = issue_capability_trust_decision(
            h,
            subject_binding=sb,
            qualification=q,
            admission=a_new,
            nonce="nonce-p14-renewal",
        )
        bundle = run_eap_and_collect_evidence(
            h,
            conn=conn,
            subject_binding=sb,
            qualification=q,
            admission=a_new,
            capability=cap,
            trust_decision=td,
            revocation_registry=rev,
            resource_id="resource-A",
            new_resource_value="p14-renewal-write",
        )
        assert bundle.eap_result.verdict == "EXECUTION_SUCCEEDED"
        assert bundle.final_mutation_count == 1
        assert bundle.final_resource_value == "p14-renewal-write"
    finally:
        close_temp_store(conn, tmp)



# === FR-8 regression: QA-P6 must not be satisfied by CAPABILITY_EXPIRED ===

def test_fr8_qa_p6_fails_if_satisfied_by_capability_expired_alone():
    """FR-8: if the only thing that expired is the capability (not the
    qualification), the case should FAIL — it must isolate the
    qualification expiry condition.
    """
    from tests.case_functions import (
        case_p6, _setup_case_dir, _insert_initial_resource,
        _make_capability, _make_trust_decision, _run_eap,
    )

    h = FixtureHarness.build()
    sb = make_subject_binding(identity_id="agent-fr8", challenge="fr8")
    q, a = issue_qualification_and_admission(
        h, subject_binding=sb,
        qualification_lifetime_ms=200 * 3600 * 1000,  # 200h
        admission_lifetime_ms=200 * 3600 * 1000,
    )
    case_dir, conn = _setup_case_dir("FR-8-regression", "")
    reg = RevocationRegistry()
    try:
        _insert_initial_resource(conn, "resource-A", "fr8-initial")
        cap = _make_capability(
            h, sb=sb, q=q, a=a, nonce="nonce-fr8-1",
            capability_lifetime_ms=2 * 3600 * 1000,  # 2h cap
        )
        td = _make_trust_decision(
            h, cap=cap, trust_decision_lifetime_ms=2 * 3600 * 1000,
        )
        h.clock = h.clock.advance_ms(3 * 3600 * 1000)
        result = _run_eap(
            h, conn=conn, sb=sb, q=q, a=a, cap=cap, td=td, reg=reg,
            resource_id="resource-A", new_value="fr8-write",
        )
        # The result MUST be CAPABILITY_EXPIRED (NOT QUALIFICATION_EXPIRED).
        # This proves the regression test correctly distinguishes the two
        # conditions.
        assert "CAPABILITY_EXPIRED" in result.reason_code, (
            f"Expected CAPABILITY_EXPIRED. Got: {result.reason_code!r}"
        )
        assert "QUALIFICATION_EXPIRED" not in result.reason_code, (
            f"Qualification should NOT be expired here. Got: {result.reason_code!r}"
        )
    finally:
        conn.close()


def test_fr8_qa_p6_official_case_uses_qualification_expiry_not_cap():
    """FR-8: run the official case_p6 and verify the recorded reason is
    QUALIFICATION_EXPIRED specifically, with subcheck evidence that
    cap/td/adm were NOT expired at EAP time.
    """
    import tempfile
    from tests.case_functions import case_p6

    h = FixtureHarness.build()
    tmp = tempfile.mkdtemp(prefix="fr8-")
    try:
        ev = case_p6(h, tmp)
        assert ev.pass_fail == "PASS", (
            f"Official case_p6 must PASS with FR-8 isolation. Got {ev.pass_fail!r}. "
            f"reason={ev.reason_code!r}, subchecks={ev.subcheck_results!r}"
        )
        assert "QUALIFICATION_EXPIRED" in ev.reason_code, (
            f"Official case_p6 reason must mention QUALIFICATION_EXPIRED. "
            f"Got: {ev.reason_code!r}"
        )
        assert ev.subcheck_results["qualification_expired_in_reason"] is True
        assert ev.subcheck_results["capability_not_yet_expired"] is True
        assert ev.subcheck_results["trust_decision_not_yet_expired"] is True
        assert ev.subcheck_results["admission_not_yet_expired"] is True
        assert ev.subcheck_results["no_protected_mutation"] is True
        # Verify timestamps prove ordering
        now_after = ev.qualification_expires_at_unix_ms + ev.qualification_expired_at_advance_ms
        assert now_after > ev.qualification_expires_at_unix_ms
        assert now_after < ev.capability_expires_at_unix_ms, (
            f"now_after={now_after} must be < capability_expires_at={ev.capability_expires_at_unix_ms}"
        )
        assert now_after < ev.trust_decision_expires_at_unix_ms, (
            f"now_after={now_after} must be < trust_decision_expires_at={ev.trust_decision_expires_at_unix_ms}"
        )
    finally:
        import shutil
        shutil.rmtree(tmp, ignore_errors=True)



# === FR-10 regression: cross-authority revocation must fail ===

def test_fr10_r12_attempts_qualification_revocation_rejected():
    """FR-10: R12 (admission authority) attempts QUALIFICATION_REVOCATION
    => rejected, epoch unchanged, registry not updated.
    """
    from trusted.control_apply import (
        ControlRecordError,
        apply_control_record,
        make_change_type_authorization_lookup,
    )
    from trusted import enforcement_store
    from qa_poc.models import (
        ControlRecord, DOMAIN_CONTROL_RECORD, artifact_payload, compute_id_and_digest,
    )
    from qa_poc.crypto import sign_ed25519, key_id_from_public_pem
    from cryptography.hazmat.primitives import serialization

    conn, tmp = open_temp_store()
    try:
        h = FixtureHarness.build()
        sb = make_subject_binding(identity_id="agent-fr10a", challenge="fr10a")
        q, a = issue_qualification_and_admission(h, subject_binding=sb)

        # Build a ControlRecord QUALIFICATION_REVOCATION signed with R12 key.
        r11_kid = key_id_from_public_pem(h.keys.r11_pub.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo,
        ))
        r12_kid = key_id_from_public_pem(h.keys.r12_pub.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo,
        ))
        lookup = make_change_type_authorization_lookup(r11_key_id=r11_kid, r12_key_id=r12_kid)

        epoch_before = enforcement_store.current_epoch(conn)
        semantic = {
            "previous_epoch": epoch_before,
            "new_epoch": epoch_before + 1,
            "change_type": "QUALIFICATION_REVOCATION",
            "target_type": "qualification",
            "target_id": q.credential_id,
            "target_digest_optional": q.credential_digest,
            "issued_at_unix_ms": 0,
            "issuer_authority_id": "r12-a",
            "issuer_key_id": r12_kid,
        }
        rec_proto = ControlRecord(
            record_id="",
            previous_epoch=epoch_before,
            new_epoch=epoch_before + 1,
            change_type="QUALIFICATION_REVOCATION",
            target_type="qualification",
            target_id=q.credential_id,
            target_digest_optional=q.credential_digest,
            issued_at_unix_ms=0,
            issuer_authority_id="r12-a",
            issuer_key_id=r12_kid,
            record_digest="",
        )
        rec, _ = compute_id_and_digest(
            rec_proto, semantic_fields=semantic, id_prefix="rev",
            id_salt=("fr10a", q.credential_id),
        )
        sig = sign_ed25519(h.keys.r12_priv, DOMAIN_CONTROL_RECORD, artifact_payload(rec))
        from dataclasses import asdict
        from dataclasses import replace as dc_replace
        rec = dc_replace(rec, signature=sig)

        with pytest.raises(ControlRecordError) as exc:
            apply_control_record(
                conn,
                record=rec,
                issuer_pub=h.keys.r12_pub,
                change_type_authorization_lookup=lookup,
                created_at_unix_ms=0,
            )
        assert "ISSUER_NOT_AUTHORIZED" in str(exc.value) or "not authorized" in str(exc.value).lower(), (
            f"Expected issuer-not-authorized error. Got: {exc.value!r}"
        )
        # Epoch must be unchanged
        assert enforcement_store.current_epoch(conn) == epoch_before
    finally:
        close_temp_store(conn, tmp)


def test_fr10_r11_attempts_admission_revocation_rejected():
    """FR-10: R11 (qualification authority) attempts ADMISSION_REVOCATION
    => rejected, epoch unchanged, registry not updated.
    """
    from trusted.control_apply import (
        ControlRecordError,
        apply_control_record,
        make_change_type_authorization_lookup,
    )
    from trusted import enforcement_store
    from qa_poc.models import (
        ControlRecord, DOMAIN_CONTROL_RECORD, artifact_payload, compute_id_and_digest,
    )
    from qa_poc.crypto import sign_ed25519, key_id_from_public_pem
    from cryptography.hazmat.primitives import serialization
    from dataclasses import replace as dc_replace

    conn, tmp = open_temp_store()
    try:
        h = FixtureHarness.build()
        sb = make_subject_binding(identity_id="agent-fr10b", challenge="fr10b")
        q, a = issue_qualification_and_admission(h, subject_binding=sb)

        r11_kid = key_id_from_public_pem(h.keys.r11_pub.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo,
        ))
        r12_kid = key_id_from_public_pem(h.keys.r12_pub.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo,
        ))
        lookup = make_change_type_authorization_lookup(r11_key_id=r11_kid, r12_key_id=r12_kid)

        epoch_before = enforcement_store.current_epoch(conn)
        semantic = {
            "previous_epoch": epoch_before,
            "new_epoch": epoch_before + 1,
            "change_type": "ADMISSION_REVOCATION",
            "target_type": "admission",
            "target_id": a.credential_id,
            "target_digest_optional": a.credential_digest,
            "issued_at_unix_ms": 0,
            "issuer_authority_id": "r11-q",
            "issuer_key_id": r11_kid,
        }
        rec_proto = ControlRecord(
            record_id="",
            previous_epoch=epoch_before,
            new_epoch=epoch_before + 1,
            change_type="ADMISSION_REVOCATION",
            target_type="admission",
            target_id=a.credential_id,
            target_digest_optional=a.credential_digest,
            issued_at_unix_ms=0,
            issuer_authority_id="r11-q",
            issuer_key_id=r11_kid,
            record_digest="",
        )
        rec, _ = compute_id_and_digest(
            rec_proto, semantic_fields=semantic, id_prefix="rev",
            id_salt=("fr10b", a.credential_id),
        )
        sig = sign_ed25519(h.keys.r11_priv, DOMAIN_CONTROL_RECORD, artifact_payload(rec))
        rec = dc_replace(rec, signature=sig)

        with pytest.raises(ControlRecordError) as exc:
            apply_control_record(
                conn,
                record=rec,
                issuer_pub=h.keys.r11_pub,
                change_type_authorization_lookup=lookup,
                created_at_unix_ms=0,
            )
        assert "ISSUER_NOT_AUTHORIZED" in str(exc.value) or "not authorized" in str(exc.value).lower()
        assert enforcement_store.current_epoch(conn) == epoch_before
    finally:
        close_temp_store(conn, tmp)


def test_fr10_r11_qualification_revocation_accepted():
    """FR-10 positive: R11 signed QUALIFICATION_REVOCATION => accepted."""
    from trusted.control_apply import (
        apply_control_record,
        make_change_type_authorization_lookup,
    )
    from trusted import enforcement_store
    from qa_poc.models import (
        ControlRecord, DOMAIN_CONTROL_RECORD, artifact_payload, compute_id_and_digest,
    )
    from qa_poc.crypto import sign_ed25519, key_id_from_public_pem
    from cryptography.hazmat.primitives import serialization
    from dataclasses import replace as dc_replace

    conn, tmp = open_temp_store()
    try:
        h = FixtureHarness.build()
        sb = make_subject_binding(identity_id="agent-fr10c", challenge="fr10c")
        q, a = issue_qualification_and_admission(h, subject_binding=sb)

        r11_kid = key_id_from_public_pem(h.keys.r11_pub.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo,
        ))
        r12_kid = key_id_from_public_pem(h.keys.r12_pub.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo,
        ))
        lookup = make_change_type_authorization_lookup(r11_key_id=r11_kid, r12_key_id=r12_kid)

        epoch_before = enforcement_store.current_epoch(conn)
        semantic = {
            "previous_epoch": epoch_before,
            "new_epoch": epoch_before + 1,
            "change_type": "QUALIFICATION_REVOCATION",
            "target_type": "qualification",
            "target_id": q.credential_id,
            "target_digest_optional": q.credential_digest,
            "issued_at_unix_ms": 0,
            "issuer_authority_id": "r11-q",
            "issuer_key_id": r11_kid,
        }
        rec_proto = ControlRecord(
            record_id="",
            previous_epoch=epoch_before,
            new_epoch=epoch_before + 1,
            change_type="QUALIFICATION_REVOCATION",
            target_type="qualification",
            target_id=q.credential_id,
            target_digest_optional=q.credential_digest,
            issued_at_unix_ms=0,
            issuer_authority_id="r11-q",
            issuer_key_id=r11_kid,
            record_digest="",
        )
        rec, _ = compute_id_and_digest(
            rec_proto, semantic_fields=semantic, id_prefix="rev",
            id_salt=("fr10c", q.credential_id),
        )
        sig = sign_ed25519(h.keys.r11_priv, DOMAIN_CONTROL_RECORD, artifact_payload(rec))
        rec = dc_replace(rec, signature=sig)

        new_epoch = apply_control_record(
            conn,
            record=rec,
            issuer_pub=h.keys.r11_pub,
            change_type_authorization_lookup=lookup,
            created_at_unix_ms=0,
        )
        assert new_epoch == epoch_before + 1
        assert enforcement_store.current_epoch(conn) == epoch_before + 1
    finally:
        close_temp_store(conn, tmp)


def test_fr10_r12_admission_revocation_accepted():
    """FR-10 positive: R12 signed ADMISSION_REVOCATION => accepted."""
    from trusted.control_apply import (
        apply_control_record,
        make_change_type_authorization_lookup,
    )
    from trusted import enforcement_store
    from qa_poc.models import (
        ControlRecord, DOMAIN_CONTROL_RECORD, artifact_payload, compute_id_and_digest,
    )
    from qa_poc.crypto import sign_ed25519, key_id_from_public_pem
    from cryptography.hazmat.primitives import serialization
    from dataclasses import replace as dc_replace

    conn, tmp = open_temp_store()
    try:
        h = FixtureHarness.build()
        sb = make_subject_binding(identity_id="agent-fr10d", challenge="fr10d")
        q, a = issue_qualification_and_admission(h, subject_binding=sb)

        r11_kid = key_id_from_public_pem(h.keys.r11_pub.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo,
        ))
        r12_kid = key_id_from_public_pem(h.keys.r12_pub.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo,
        ))
        lookup = make_change_type_authorization_lookup(r11_key_id=r11_kid, r12_key_id=r12_kid)

        epoch_before = enforcement_store.current_epoch(conn)
        semantic = {
            "previous_epoch": epoch_before,
            "new_epoch": epoch_before + 1,
            "change_type": "ADMISSION_REVOCATION",
            "target_type": "admission",
            "target_id": a.credential_id,
            "target_digest_optional": a.credential_digest,
            "issued_at_unix_ms": 0,
            "issuer_authority_id": "r12-a",
            "issuer_key_id": r12_kid,
        }
        rec_proto = ControlRecord(
            record_id="",
            previous_epoch=epoch_before,
            new_epoch=epoch_before + 1,
            change_type="ADMISSION_REVOCATION",
            target_type="admission",
            target_id=a.credential_id,
            target_digest_optional=a.credential_digest,
            issued_at_unix_ms=0,
            issuer_authority_id="r12-a",
            issuer_key_id=r12_kid,
            record_digest="",
        )
        rec, _ = compute_id_and_digest(
            rec_proto, semantic_fields=semantic, id_prefix="rev",
            id_salt=("fr10d", a.credential_id),
        )
        sig = sign_ed25519(h.keys.r12_priv, DOMAIN_CONTROL_RECORD, artifact_payload(rec))
        rec = dc_replace(rec, signature=sig)

        new_epoch = apply_control_record(
            conn,
            record=rec,
            issuer_pub=h.keys.r12_pub,
            change_type_authorization_lookup=lookup,
            created_at_unix_ms=0,
        )
        assert new_epoch == epoch_before + 1
        assert enforcement_store.current_epoch(conn) == epoch_before + 1
    finally:
        close_temp_store(conn, tmp)


# --- FR-12: QA-P14 admission-expiry isolation -------------------------------

def test_fr12_p14_admission_expiry_is_not_masked(tmp_path):
    from tests.case_functions import case_p14_deny
    h = FixtureHarness.build()
    ev = case_p14_deny(h, str(tmp_path))
    assert ev.pass_fail == "PASS", (ev.verdict, ev.reason_code, ev.subcheck_results)
    assert ev.verdict == "EXECUTION_DENIED"
    assert "ADMISSION_EXPIRED" in ev.reason_code
    assert "CAPABILITY_EXPIRED" not in ev.reason_code
    assert "TRUST_DECISION_EXPIRED" not in ev.reason_code
    assert "QUALIFICATION_EXPIRED" not in ev.reason_code
    assert ev.subcheck_results["admission_expired_in_reason"] is True
    assert ev.subcheck_results["qualification_still_nominal"] is True
    assert ev.subcheck_results["capability_still_nominal"] is True
    assert ev.subcheck_results["trust_decision_still_nominal"] is True
    assert ev.final_mutation_count == ev.initial_mutation_count

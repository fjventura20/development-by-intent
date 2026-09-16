"""ATE Qualification & Admission Local PoC v0.1 — pytest helpers.

Provides:
  - KeyBag: holds the 6 authority + 1 audit keypair (Ed25519) used by
    tests. Each authority has its own artifact-domain permissions.
  - AgentSubjects: agent-a + agent-b subject bindings + identity keys.
  - FixtureAuthority + FixtureAdmissionAuthority + FixtureAuthorizationAuthority:
    convenience wrappers around the qa_poc services.
  - FixtureExecutor: opens the enforcement store in a per-test temp
    directory.
  - bootstrap_subject_binding(): deterministic SubjectBinding builder.

All keys are Ed25519 and generated fresh per test session.
"""

from __future__ import annotations

import os
import shutil
import sqlite3
import tempfile
from dataclasses import dataclass
from typing import Callable, Dict, Optional, Tuple

from qa_poc.admission import AdmissionAuthority, AdmissionCredential, QualificationCredential
from qa_poc.authorization import AuthorizationAuthority, CapabilityToken, TrustDecision
from qa_poc.clock import Clock
from qa_poc.crypto import Ed25519PrivateKey, Ed25519PublicKey, generate_keypair, key_id_from_public_pem
from qa_poc.models import (
    DOMAIN_ADMISSION_CREDENTIAL,
    DOMAIN_ADMISSION_DECISION,
    DOMAIN_ADMISSION_EVIDENCE_MANIFEST,
    DOMAIN_ADMISSION_POLICY,
    DOMAIN_CAPABILITY_TOKEN,
    DOMAIN_QUALIFICATION_CREDENTIAL,
    DOMAIN_QUALIFICATION_DECISION,
    DOMAIN_QUALIFICATION_EVIDENCE_MANIFEST,
    DOMAIN_QUALIFICATION_REQUIREMENTS_PROFILE,
    DOMAIN_TRUST_DECISION,
    AdmissionPolicy,
    QualificationRequirementsProfile,
)
from qa_poc.policies import PolicyRegistry, ProfileRegistry
from qa_poc.qualification import QualificationAuthority
from qa_poc.subject_binding import SubjectBinding
from trusted import enforcement_store


@dataclass
class KeyBag:
    policy_priv: Ed25519PrivateKey
    policy_pub: Ed25519PublicKey
    identity_priv: Ed25519PrivateKey
    identity_pub: Ed25519PublicKey
    r11_priv: Ed25519PrivateKey
    r11_pub: Ed25519PublicKey
    r12_priv: Ed25519PrivateKey
    r12_pub: Ed25519PublicKey
    auth_priv: Ed25519PrivateKey
    auth_pub: Ed25519PublicKey
    trust_priv: Ed25519PrivateKey
    trust_pub: Ed25519PublicKey
    executor_priv: Ed25519PrivateKey
    executor_pub: Ed25519PublicKey
    audit_priv: Ed25519PrivateKey
    audit_pub: Ed25519PublicKey
    # AUTH_IDENTITY: a recognised, active identity key. Per the frozen
    # design §28 QA-P8, this key is registered as AUTHORIZED for
    # SubjectBinding + evidence-manifest signatures but is NOT
    # authorized to sign QualificationCredential artifacts. (Signing
    # a QualificationCredential with this key should be rejected at
    # the issuer-authorization check, even though the signature
    # cryptographically verifies.)
    auth_identity_priv: Ed25519PrivateKey
    auth_identity_pub: Ed25519PublicKey

    @classmethod
    def fresh(cls) -> "KeyBag":
        policy_priv, policy_pub = generate_keypair()
        identity_priv, identity_pub = generate_keypair()
        r11_priv, r11_pub = generate_keypair()
        r12_priv, r12_pub = generate_keypair()
        auth_priv, auth_pub = generate_keypair()
        trust_priv, trust_pub = generate_keypair()
        executor_priv, executor_pub = generate_keypair()
        audit_priv, audit_pub = generate_keypair()
        auth_identity_priv, auth_identity_pub = generate_keypair()
        return cls(
            policy_priv=policy_priv, policy_pub=policy_pub,
            identity_priv=identity_priv, identity_pub=identity_pub,
            r11_priv=r11_priv, r11_pub=r11_pub,
            r12_priv=r12_priv, r12_pub=r12_pub,
            auth_priv=auth_priv, auth_pub=auth_pub,
            trust_priv=trust_priv, trust_pub=trust_pub,
            executor_priv=executor_priv, executor_pub=executor_pub,
            audit_priv=audit_priv, audit_pub=audit_pub,
            auth_identity_priv=auth_identity_priv,
            auth_identity_pub=auth_identity_pub,
        )


# A revocation lookup that says "not revoked" by default.
def _no_revocations(_credential_id: str):
    return (False, "")


# Fixed snapshot reference for tests.
FIXED_SNAPSHOT_REF = "trust-state-snapshot-fixed-fixture"


@dataclass
class FixtureHarness:
    keys: KeyBag
    profile_registry: ProfileRegistry
    policy_registry: PolicyRegistry
    qualification: QualificationAuthority
    admission: AdmissionAuthority
    authorization: AuthorizationAuthority
    profile: QualificationRequirementsProfile
    policy: AdmissionPolicy
    clock: Clock

    @classmethod
    def build(cls) -> "FixtureHarness":
        keys = KeyBag.fresh()
        profile_reg = ProfileRegistry()
        policy_reg = PolicyRegistry()
        qual = QualificationAuthority(
            registry=profile_reg,
            r11_priv=keys.r11_priv,
            r11_pub=keys.r11_pub,
            r11_key_id="r11-q",
            identity_priv=keys.identity_priv,
        )
        adm = AdmissionAuthority(
            registry=policy_reg,
            r12_priv=keys.r12_priv,
            r12_pub=keys.r12_pub,
            r12_key_id="r12-a",
        )
        authz = AuthorizationAuthority(
            auth_priv=keys.auth_priv,
            auth_pub=keys.auth_pub,
            auth_key_id="auth",
            trust_priv=keys.trust_priv,
            trust_pub=keys.trust_pub,
            trust_key_id="trust",
        )
        # Publish active profile
        profile = qual.publish_profile(
            profile_id="qa-demo-writer",
            profile_version=1,
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
        # Publish active admission policy
        policy = adm.publish_policy(
            policy_id="admission-local-ate-demo",
            policy_version=1,
            trust_domain="local-ate-demo",
            role="demo-repository-writer",
            qualification_domain="local-qa-demo",
            qualification_authority_key_id="r11-q",
            recognized_profile_id=profile.profile_id,
            recognized_profile_digest=profile.profile_digest,
            maximum_risk="R2",
            eligible_capability="demo-resource-write",
        )
        return cls(
            keys=keys,
            profile_registry=profile_reg,
            policy_registry=policy_reg,
            qualification=qual,
            admission=adm,
            authorization=authz,
            profile=profile,
            policy=policy,
            clock=Clock(now_unix_ms=1_700_000_000_000),
        )


# --- Issuer Authorization Registry (frozen §6 + §28 QA-P8) ---------------


@dataclass
class IssuerAuthorizationRegistry:
    """Maps (key_id, artifact_type) → bool.

    The frozen design §6 requires a recognized authority identity
    (key) to have explicit permission to sign each artifact type.
    AUTH_IDENTITY is recognised and active, but it is NOT authorized
    to sign QualificationCredential artifacts — only R11 is.

    This registry is consulted by the EAP (and by case functions) to
    distinguish "cryptographically valid signature from a recognized
    key" from "authorized to sign this artifact type".
    """

    auth_role: str
    artifact_type_permissions: Dict[Tuple[str, str], bool]

    @classmethod
    def build_default(cls, *, auth_identity_key_id: str, r11_key_id: str) -> "IssuerAuthorizationRegistry":
        from qa_poc.models import (
            DOMAIN_ADMISSION_CREDENTIAL,
            DOMAIN_QUALIFICATION_CREDENTIAL,
            DOMAIN_QUALIFICATION_EVIDENCE_MANIFEST,
        )

        # Per frozen design: AUTH_IDENTITY authorizes SubjectBinding +
        # evidence-manifest signatures. R11 authorizes QualificationCredential.
        perms = {
            (auth_identity_key_id, DOMAIN_QUALIFICATION_EVIDENCE_MANIFEST): True,
            (auth_identity_key_id, DOMAIN_QUALIFICATION_CREDENTIAL): False,
            (auth_identity_key_id, DOMAIN_ADMISSION_CREDENTIAL): False,
            (r11_key_id, DOMAIN_QUALIFICATION_CREDENTIAL): True,
        }
        return cls(auth_role=auth_identity_key_id, artifact_type_permissions=perms)

    def is_authorized(self, key_id: str, artifact_type: str) -> bool:
        return self.artifact_type_permissions.get((key_id, artifact_type), False)

    def lookup(self, key_id: str, artifact_type: str) -> bool:
        """Function-style lookup (drop-in for callable registries)."""
        return self.is_authorized(key_id=key_id, artifact_type=artifact_type)


def issue_qualification_and_admission(
    harness: FixtureHarness,
    *,
    subject_binding: SubjectBinding,
    trust_domain: str = "local-ate-demo",
) -> Tuple[QualificationCredential, AdmissionCredential]:
    """Run the qualification -> admission pipeline for a SubjectBinding."""
    from qa_poc.qualification import build_evidence_bundle

    evidence = build_evidence_bundle(subject_binding=subject_binding)
    _q_manifest, _q_decision, q_cred = harness.qualification.evaluate(
        subject_binding=subject_binding,
        qualification_domain="local-qa-demo",
        role="demo-repository-writer",
        evidence=evidence,
        snapshot_reference=FIXED_SNAPSHOT_REF,
        clock=harness.clock,
    )
    assert q_cred is not None
    _a_manifest, _a_decision, a_cred = harness.admission.evaluate(
        subject_binding=subject_binding,
        qualification=q_cred,
        trust_domain=trust_domain,
        role="demo-repository-writer",
        snapshot_reference=FIXED_SNAPSHOT_REF,
        clock=harness.clock,
        revocation_lookup=_no_revocations,
    )
    assert a_cred is not None
    return q_cred, a_cred


def make_subject_binding(*, identity_id: str, challenge: str = "challenge-default") -> SubjectBinding:
    return SubjectBinding(
        subject_identity_id=identity_id,
        runtime_class="synthetic-runtime-v1",
        provider_id="local-fixture",
        binding_level="SB2",
        challenge=challenge,
    )


def open_temp_store() -> Tuple[sqlite3.Connection, str]:
    """Open a fresh enforcement store in a temp directory."""
    tmp = tempfile.mkdtemp(prefix="ate-poc-test-")
    db_path = os.path.join(tmp, "enforcement.db")
    conn = enforcement_store.open_store(db_path)
    return conn, tmp


def close_temp_store(conn: sqlite3.Connection, tmp: str) -> None:
    try:
        conn.close()
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


# -- Revocation registry (real, mutated by ControlRecord application) ---------


class RevocationRegistry:
    """Maps credential_id → (is_revoked: bool, reason: str).

    Updated by the executor when a QUALIFICATION_REVOCATION or
    ADMISSION_REVOCATION ControlRecord is applied. The revocation_lookup
    callable used by `execute_bound_action` and `check_admission_usable`
    reads from this registry.
    """

    def __init__(self) -> None:
        self._by_id: Dict[str, Tuple[bool, str]] = {}

    def revoke(self, credential_id: str, *, reason: str = "revoked") -> None:
        self._by_id[credential_id] = (True, reason)

    def lookup(self, credential_id: str) -> Tuple[bool, str]:
        return self._by_id.get(credential_id, (False, ""))


def apply_revocation_control_record(
    conn,
    *,
    record_id: str,
    target_type: str,  # "qualification" or "admission"
    target_id: str,
    target_digest: str,
    issuer_priv,
    issuer_pub,
    issuer_authority_id: str,
    issuer_key_id: str,
    registry: RevocationRegistry,
    reason: str,
    created_at_unix_ms: int,
    change_type_authorization_ok: Callable[[str, str], bool] = lambda ct, k: True,
) -> int:
    """Apply a revocation ControlRecord to the executor-owned store,
    updating `registry` so the revocation_lookup picks it up.

    Returns the new applied_epoch.
    """
    from qa_poc.crypto import sign_ed25519
    from qa_poc.models import (
        ControlRecord,
        DOMAIN_CONTROL_RECORD,
        artifact_payload,
        compute_id_and_digest,
    )
    from trusted.control_apply import apply_control_record

    epoch_before = enforcement_store.current_epoch(conn)
    change_type = (
        "QUALIFICATION_REVOCATION" if target_type == "qualification"
        else "ADMISSION_REVOCATION"
    )
    semantic = {
        "previous_epoch": epoch_before,
        "new_epoch": epoch_before + 1,
        "change_type": change_type,
        "target_type": target_type,
        "target_id": target_id,
        "target_digest_optional": target_digest,
        "issued_at_unix_ms": created_at_unix_ms,
        "issuer_authority_id": issuer_authority_id,
        "issuer_key_id": issuer_key_id,
    }
    rec_proto = ControlRecord(
        record_id="",
        previous_epoch=epoch_before,
        new_epoch=epoch_before + 1,
        change_type=change_type,
        target_type=target_type,
        target_id=target_id,
        target_digest_optional=target_digest,
        issued_at_unix_ms=created_at_unix_ms,
        issuer_authority_id=issuer_authority_id,
        issuer_key_id=issuer_key_id,
        record_digest="",
    )
    rec, _ = compute_id_and_digest(
        rec_proto,
        semantic_fields=semantic,
        id_prefix="rev",
        id_salt=(record_id, target_id),
    )
    sig = sign_ed25519(issuer_priv, DOMAIN_CONTROL_RECORD, artifact_payload(rec))
    rec = rec.__class__(**{**rec.__dict__, "signature": sig})

    new_epoch = apply_control_record(
        conn,
        record=rec,
        issuer_pub=issuer_pub,
        change_type_authorization_lookup=change_type_authorization_ok,
        created_at_unix_ms=created_at_unix_ms,
    )
    registry.revoke(target_id, reason=reason)
    return new_epoch


# -- Bundle helpers (issue cap + td + EAP, capturing full evidence) ---------


@dataclass
class BundleWithEvidence:
    """Captures the cap + td + audit evidence around an EAP call."""
    subject_binding: SubjectBinding
    qualification: QualificationCredential
    admission: AdmissionCredential
    capability: CapabilityToken
    trust_decision: TrustDecision
    eap_result: "EapResult"  # forward ref
    initial_mutation_count: int
    final_mutation_count: int
    initial_resource_value: str
    final_resource_value: str
    audit_before: list
    audit_after: list
    initial_epoch: int
    final_epoch: int
    applied_control_records: list


def issue_capability_trust_decision(
    harness: FixtureHarness,
    *,
    subject_binding: SubjectBinding,
    qualification: QualificationCredential,
    admission: AdmissionCredential,
    nonce: str,
    target: str = "resource-A",
    parameters: Optional[dict] = None,
    session_identity: str = "sess-test",
    snapshot_reference: str = FIXED_SNAPSHOT_REF,
) -> Tuple[CapabilityToken, TrustDecision]:
    if parameters is None:
        parameters = {"new_value": "hello"}
    cap = harness.authorization.issue_capability_token(
        subject_binding=subject_binding,
        qualification=qualification,
        admission=admission,
        session_identity=session_identity,
        operation="WRITE",
        target=target,
        parameters=parameters,
        risk_class="R2",
        capability_class="demo-resource-write",
        nonce=nonce,
        snapshot_reference=snapshot_reference,
        clock=harness.clock,
    )
    td = harness.authorization.issue_trust_decision(
        capability=cap,
        requested_action={"target": target, "operation": "WRITE", "parameters": parameters},
        verdict="AUTHORIZED",
        snapshot_reference=snapshot_reference,
        clock=harness.clock,
    )
    return cap, td


def run_eap_and_collect_evidence(
    harness: FixtureHarness,
    *,
    conn,
    subject_binding: SubjectBinding,
    qualification: QualificationCredential,
    admission: AdmissionCredential,
    capability: CapabilityToken,
    trust_decision: TrustDecision,
    revocation_registry: RevocationRegistry,
    resource_id: str,
    new_resource_value: str,
    live_proof_verifier: Optional[Callable[[], None]] = None,
) -> BundleWithEvidence:
    """Run the EAP, capture full before/after state."""
    from trusted.executor import BoundActionBundle, execute_bound_action

    bundle = BoundActionBundle(
        subject_binding=subject_binding,
        capability=capability,
        trust_decision=trust_decision,
        action={"target": resource_id, "operation": "WRITE", "parameters": {"new_value": new_resource_value}},
    )
    initial_res = enforcement_store.read_protected_resource(conn, resource_id) or {}
    initial_mc = initial_res.get("mutation_count", 0)
    initial_value = initial_res.get("value", "")
    initial_epoch = enforcement_store.current_epoch(conn)
    audit_before = enforcement_store.read_audit(conn)
    applied_before = conn.execute(
        "SELECT record_id, target_type, target_id, target_digest, status, issued_at_unix_ms, applied_at_unix_ms, applied_epoch, record_digest FROM applied_control_records ORDER BY applied_epoch"
    ).fetchall()

    result = execute_bound_action(
        conn,
        bundle=bundle,
        auth_pub=harness.keys.auth_pub,
        trust_pub=harness.keys.trust_pub,
        revocation_lookup=revocation_registry.lookup,
        bound_qualification=qualification,
        bound_admission=admission,
        qualification_pub=harness.keys.r11_pub,
        admission_pub=harness.keys.r12_pub,
        resource_id=resource_id,
        new_resource_value=new_resource_value,
        clock=harness.clock,
        live_proof_verifier=live_proof_verifier,
    )

    audit_after = enforcement_store.read_audit(conn)
    applied_after = conn.execute(
        "SELECT record_id, target_type, target_id, target_digest, status, issued_at_unix_ms, applied_at_unix_ms, applied_epoch, record_digest FROM applied_control_records ORDER BY applied_epoch"
    ).fetchall()
    final_res = enforcement_store.read_protected_resource(conn, resource_id) or {}
    final_mc = final_res.get("mutation_count", 0)
    final_value = final_res.get("value", "")
    final_epoch = enforcement_store.current_epoch(conn)

    return BundleWithEvidence(
        subject_binding=subject_binding,
        qualification=qualification,
        admission=admission,
        capability=capability,
        trust_decision=trust_decision,
        eap_result=result,
        initial_mutation_count=initial_mc,
        final_mutation_count=final_mc,
        initial_resource_value=initial_value,
        final_resource_value=final_value,
        audit_before=audit_before,
        audit_after=audit_after,
        initial_epoch=initial_epoch,
        final_epoch=final_epoch,
        applied_control_records=[
            {
                "record_id": r[0],
                "target_type": r[1],
                "target_id": r[2],
                "target_digest": r[3],
                "status": r[4],
                "issued_at_unix_ms": r[5],
                "applied_at_unix_ms": r[6],
                "applied_epoch": r[7],
                "record_digest": r[8],
            }
            for r in applied_after
        ],
    )

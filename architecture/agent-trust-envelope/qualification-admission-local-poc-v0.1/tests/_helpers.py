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
from typing import Tuple

from qa_poc.admission import AdmissionAuthority, AdmissionCredential, QualificationCredential
from qa_poc.authorization import AuthorizationAuthority, CapabilityToken, TrustDecision
from qa_poc.clock import Clock
from qa_poc.crypto import Ed25519PrivateKey, Ed25519PublicKey, generate_keypair
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
        return cls(
            policy_priv=policy_priv, policy_pub=policy_pub,
            identity_priv=identity_priv, identity_pub=identity_pub,
            r11_priv=r11_priv, r11_pub=r11_pub,
            r12_priv=r12_priv, r12_pub=r12_pub,
            auth_priv=auth_priv, auth_pub=auth_pub,
            trust_priv=trust_priv, trust_pub=trust_pub,
            executor_priv=executor_priv, executor_pub=executor_pub,
            audit_priv=audit_priv, audit_pub=audit_pub,
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
    profile: object
    policy: object
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

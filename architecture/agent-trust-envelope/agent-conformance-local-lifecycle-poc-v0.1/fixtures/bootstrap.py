"""Agent Conformance Local Lifecycle PoC v0.1 — test bootstrap.

Builds the deterministic local PoC harness:

  - one logical clock
  - one runtime observer authority
  - one R13 evaluator authority
  - one R14 lifecycle authority
  - one authorization (capability issuer) authority
  - one qualification/admission fixture issuer authority
  - one audit recorder authority
  - one subject (agent-001, role=worker, trust_domain=local-poc)
  - predeclared ConformanceProfile v1 (requires runtime v1)
  - predeclared ConformanceProfile v2 (requires runtime v2; digest
    locked before any test runs — frozen §9, §16)
  - signed QualificationFixture + AdmissionFixture (both ACTIVE)

The PoC has exactly one protected resource at a caller-provided
path (frozen §11).
"""

from __future__ import annotations

import hashlib
import os
import shutil
import tempfile
from dataclasses import dataclass
from typing import Any, Optional

from conformance.audit import AuditRecorder
from conformance.authorization import AuthorizationService
from conformance.canonical import canonical_sha256
from conformance.crypto import (
    Ed25519PrivateKey,
    Ed25519PublicKey,
    generate_keypair,
    key_id_from_public_key,
    sign_ed25519,
)
from conformance.evaluator import R13Evaluator
from conformance.lifecycle import LifecycleAuthority
from conformance.models import (
    AdmissionFixture,
    ConformanceProfile,
    LIFECYCLE_CONFORMANT,
    QualificationFixture,
)
from conformance.state import (
    LogicalClock,
    NonceRegistry,
    RuntimeObserverStore,
    StateStore,
    SubjectState,
)
from conformance.trigger import TriggerObserver


SUBJECT_ID = "agent-001"
ROLE_ID = "worker"
TRUST_DOMAIN = "local-poc"
PROFILE_ID = "local-conformance-poc"

ACTION = "WRITE_RESOURCE"
# Frozen §11: payload_digest = SHA256(fixed payload). We precompute the
# digest and pass it as a hex string so the canonical encoder never
# touches raw bytes.
ACTION_PAYLOAD_BYTES = b"acl-lifecycle-poc-fixed-payload"
ACTION_PAYLOAD = {
    "target": "protected_resource.txt",
    "payload_digest_hex": hashlib.sha256(ACTION_PAYLOAD_BYTES).hexdigest(),
}


@dataclass
class Harness:
    """The fully wired deterministic PoC harness."""

    tmpdir: str
    protected_resource_path: str
    protected_resource_authority_token: str

    clock: LogicalClock
    state_store: StateStore
    nonce_registry: NonceRegistry

    observer: TriggerObserver
    r13: R13Evaluator
    r14: LifecycleAuthority
    authorization: AuthorizationService
    audit: AuditRecorder

    qual_admission_priv: Ed25519PrivateKey
    qual_admission_pub: Ed25519PublicKey

    subject: SubjectState
    profile_v1: ConformanceProfile
    profile_v2: ConformanceProfile
    qualification: QualificationFixture
    admission: AdmissionFixture


def _sign_conformance_profile(priv, profile: ConformanceProfile) -> ConformanceProfile:
    payload = profile.signing_payload()
    profile.signature = sign_ed25519(priv, profile.signature_domain, payload)
    return profile


def _sign_qual_admission(priv, fixture) -> Any:
    """Sign a qualification/admission fixture and bind its artifact_digest.

    F4: the verifier checks that fixture.artifact_digest equals the
    canonical SHA-256 of the signing payload, so the digest must be
    computed at signing time.
    """
    fixture.artifact_digest = canonical_sha256(fixture.signing_payload())
    fixture.signature = sign_ed25519(
        priv, fixture.signature_domain, fixture.signing_payload(),
    )
    return fixture


def build_harness(*, prefix: str = "acl-poc") -> Harness:
    """Build the full PoC harness with predeclared profiles v1+v2.

    Both profile v1 and profile v2 are signed and locked before any
    test code runs (frozen §9, §16).
    """
    tmpdir = tempfile.mkdtemp(prefix=prefix + "-")
    protected_resource_path = os.path.join(tmpdir, "protected_resource.txt")
    # Truncate / create the protected resource.
    with open(protected_resource_path, "w", encoding="utf-8") as fh:
        fh.write("")

    protected_resource_authority_token = (
        "pr-auth-" + os.path.basename(tmpdir)
    )

    clock = LogicalClock()
    state_store = StateStore()
    nonce_registry = NonceRegistry()

    # Authority keys.
    obs_priv, obs_pub = generate_keypair()
    r13_priv, r13_pub = generate_keypair()
    r14_priv, r14_pub = generate_keypair()
    az_priv, az_pub = generate_keypair()
    qa_priv, qa_pub = generate_keypair()
    ar_priv, ar_pub = generate_keypair()

    # F4 fix: register the qualification/admission issuer authority
    # on the state store. AuthorizationService looks it up by
    # registered issuer identity and key_id, not by raw attribute.
    state_store.register_qual_admission_issuer(
        issuer_id="qual-admission-issuer-1",
        issuer_public_key=qa_pub,
    )

    observer = TriggerObserver(
        observer_id="observer-1",
        private_key=obs_priv,
        public_key=obs_pub,
        store=RuntimeObserverStore(),
        clock=clock,
    )
    r13 = R13Evaluator(
        evaluator_id="r13-1",
        private_key=r13_priv,
        public_key=r13_pub,
        clock=clock,
    )
    r14 = LifecycleAuthority(
        authority_id="r14-1",
        private_key=r14_priv,
        public_key=r14_pub,
        clock=clock,
        state_store=state_store,
        r13_authority=r13,           # F2: R14 verifies R13 inputs
        trigger_authority=observer,  # F2: R14 verifies trigger inputs
    )
    authorization = AuthorizationService(
        service_id="az-1",
        private_key=az_priv,
        public_key=az_pub,
        store=state_store,
    )
    audit = AuditRecorder(
        recorder_id="audit-1",
        private_key=ar_priv,
        public_key=ar_pub,
    )

    # ---- predeclared profile v1 ----
    profile_v1 = ConformanceProfile(
        artifact_id="profile-v1",
        profile_id=PROFILE_ID,
        profile_version=1,
        trust_domain=TRUST_DOMAIN,
        role_id=ROLE_ID,
        required_runtime_version="v1",
        max_conformance_age=10_000,
        signature_domain="ate.conformance.profile.v1",
    )
    _sign_conformance_profile(r14_priv, profile_v1)  # R14 authority signs profile updates

    # ---- predeclared profile v2 (signed and locked before any run) ----
    profile_v2 = ConformanceProfile(
        artifact_id="profile-v2",
        profile_id=PROFILE_ID,
        profile_version=2,
        trust_domain=TRUST_DOMAIN,
        role_id=ROLE_ID,
        required_runtime_version="v2",
        max_conformance_age=10_000,
        signature_domain="ate.conformance.profile.v1",
    )
    _sign_conformance_profile(r14_priv, profile_v2)

    # Activate profile v1 initially (frozen §10).
    state_store.set_active_profile(profile_v1)

    # ---- qualification + admission fixtures (frozen §10A) ----
    qualification = QualificationFixture(
        artifact_id="qual-agent-001",
        subject_id=SUBJECT_ID,
        role_id=ROLE_ID,
        trust_domain=TRUST_DOMAIN,
        issuer="qual-admission-issuer-1",
        issuer_key_id=key_id_from_public_key(qa_pub),
        current_state="ACTIVE",
        issued_at=clock.now(),
        expires_at=clock.now() + 10_000,
        signature_domain="ate.conformance.qualification_fixture.v1",
    )
    qualification = _sign_qual_admission(qa_priv, qualification)

    admission = AdmissionFixture(
        artifact_id="adm-agent-001",
        subject_id=SUBJECT_ID,
        role_id=ROLE_ID,
        trust_domain=TRUST_DOMAIN,
        issuer="qual-admission-issuer-1",
        issuer_key_id=key_id_from_public_key(qa_pub),
        current_state="ACTIVE",
        issued_at=clock.now(),
        expires_at=clock.now() + 10_000,
        signature_domain="ate.conformance.admission_fixture.v1",
    )
    admission = _sign_qual_admission(qa_priv, admission)

    state_store.register_qualification_fixture(qualification)
    state_store.register_admission_fixture(admission)

    # ---- subject (identity-only; F3 keeps authoritative state in StateStore) ----
    subject = SubjectState(
        subject_id=SUBJECT_ID,
        role_id=ROLE_ID,
        trust_domain=TRUST_DOMAIN,
        current_runtime_version="v1",
    )
    state_store.add_subject(subject)

    # Grant the executor the protected-resource authority (consumed
    # by the executor per §12A.9).
    state_store.grant_protected_resource_authority(
        protected_resource_authority_token,
    )

    return Harness(
        tmpdir=tmpdir,
        protected_resource_path=protected_resource_path,
        protected_resource_authority_token=protected_resource_authority_token,
        clock=clock,
        state_store=state_store,
        nonce_registry=nonce_registry,
        observer=observer,
        r13=r13,
        r14=r14,
        authorization=authorization,
        audit=audit,
        qual_admission_priv=qa_priv,
        qual_admission_pub=qa_pub,
        subject=subject,
        profile_v1=profile_v1,
        profile_v2=profile_v2,
        qualification=qualification,
        admission=admission,
    )


def attach_executor(h: Harness):
    """Build the Executor bound to the harness's authorization service."""
    from conformance.executor import Executor

    return Executor(
        executor_id="exec-1",
        state_store=h.state_store,
        nonce_registry=h.nonce_registry,
        authorization=h.authorization,
        protected_resource_path=h.protected_resource_path,
        protected_resource_authority_token=h.protected_resource_authority_token,
    )


def teardown(h: Harness) -> None:
    shutil.rmtree(h.tmpdir, ignore_errors=True)


def protected_resource_line_count(path: str) -> int:
    with open(path, "r", encoding="utf-8") as fh:
        return sum(1 for line in fh if line.strip())
"""Agent Conformance Local Lifecycle PoC v0.1 — deterministic bootstrap.

H1-H3 final correction separates the participant-facing Harness from
TrustedControls. Signing private keys and state/profile authority
capabilities remain captured in TrustedControls and are never fields on
Harness. Ordinary fixtures receive only Harness.
"""

from __future__ import annotations

import copy
import hashlib
import os
import shutil
import tempfile
from dataclasses import dataclass
from typing import Any, Callable

from conformance.audit import AuditRecorder
from conformance.authorization import AuthorizationService
from conformance.canonical import canonical_sha256
from conformance.crypto import (
    Ed25519PublicKey,
    generate_keypair,
    key_id_from_public_key,
    sign_ed25519,
)
from conformance.evaluator import R13Evaluator
from conformance.lifecycle import LifecycleAuthority, create_lifecycle_authority
from conformance.models import AdmissionFixture, ConformanceProfile, QualificationFixture
from conformance.profile_registry import (
    ProfileRegistry,
    create_profile_registry,
    sign_conformance_profile,
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
ACTION_PAYLOAD_BYTES = b"acl-lifecycle-poc-fixed-payload"
ACTION_PAYLOAD = {
    "target": "protected_resource.txt",
    "payload_digest_hex": hashlib.sha256(ACTION_PAYLOAD_BYTES).hexdigest(),
}


@dataclass
class Harness:
    """Participant-facing deterministic PoC harness.

    No profile signer private key, qualification/admission signer private
    key, activation capability, or state-writer capability is exposed.
    """

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

    qual_admission_pub: Ed25519PublicKey
    profile_registry_pub: Ed25519PublicKey

    subject: SubjectState
    profile_v1: ConformanceProfile
    profile_v2: ConformanceProfile
    qualification: QualificationFixture
    admission: AdmissionFixture


class TrustedControls:
    """Trusted setup/control-plane operations retained outside Harness."""

    def __init__(
        self,
        *,
        activate_profile: Callable[[str, str], Any],
        revoke_qualification: Callable[[str], None],
        revoke_admission: Callable[[str], None],
        sign_profile: Callable[[ConformanceProfile], ConformanceProfile],
        sign_qa_fixture: Callable[[Any], Any],
        profile_registry_pub: Ed25519PublicKey,
    ) -> None:
        self.__activate_profile = activate_profile
        self.__revoke_qualification = revoke_qualification
        self.__revoke_admission = revoke_admission
        self.__sign_profile = sign_profile
        self.__sign_qa_fixture = sign_qa_fixture
        self.profile_registry_pub = profile_registry_pub

    def activate_predeclared_profile(self, artifact_id: str, digest: str) -> Any:
        return self.__activate_profile(artifact_id, digest)

    def revoke_qualification(self, artifact_id: str) -> None:
        self.__revoke_qualification(artifact_id)

    def revoke_admission(self, artifact_id: str) -> None:
        self.__revoke_admission(artifact_id)

    def sign_profile_for_attack_test(
        self, profile: ConformanceProfile,
    ) -> ConformanceProfile:
        return self.__sign_profile(profile)

    def sign_qa_fixture_for_attack_test(self, fixture: Any) -> Any:
        return self.__sign_qa_fixture(fixture)


def _sign_qa(priv, fixture: Any) -> Any:
    fixture.artifact_digest = canonical_sha256(fixture.signing_payload())
    fixture.signature = sign_ed25519(
        priv, fixture.signature_domain, fixture.signing_payload(),
    )
    return fixture


def build_harness_with_controls(*, prefix: str = "acl-poc") -> tuple[Harness, TrustedControls]:
    tmpdir = tempfile.mkdtemp(prefix=prefix + "-")
    protected_resource_path = os.path.join(tmpdir, "protected_resource.txt")
    with open(protected_resource_path, "w", encoding="utf-8") as fh:
        fh.write("")

    protected_resource_authority_token = "pr-auth-" + os.path.basename(tmpdir)
    clock = LogicalClock()
    state_store = StateStore()
    nonce_registry = NonceRegistry()

    obs_priv, obs_pub = generate_keypair()
    r13_priv, r13_pub = generate_keypair()
    r14_priv, r14_pub = generate_keypair()
    az_priv, az_pub = generate_keypair()
    qa_priv, qa_pub = generate_keypair()
    ar_priv, ar_pub = generate_keypair()
    pfs_priv, pfs_pub = generate_keypair()

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
        state_store=state_store,
    )
    r14 = create_lifecycle_authority(
        authority_id="r14-1",
        private_key=r14_priv,
        public_key=r14_pub,
        clock=clock,
        state_store=state_store,
        r13_authority=r13,
        trigger_authority=observer,
        trigger_evidence_store=observer.store,
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

    registry = create_profile_registry(signer_public_key=pfs_pub)

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
    sign_conformance_profile(profile_v1, pfs_priv, pfs_pub)
    registry.register(profile_v1)

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
    sign_conformance_profile(profile_v2, pfs_priv, pfs_pub)
    registry.register(profile_v2)

    # H1: registration closes before installation/run.
    registry.freeze()
    activate_profile = state_store.install_profile_registry(registry)
    activate_profile(profile_v1.artifact_id, profile_v1.artifact_digest)

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
    _sign_qa(qa_priv, qualification)

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
    _sign_qa(qa_priv, admission)

    state_store.register_qualification_fixture(qualification)
    state_store.register_admission_fixture(admission)
    revoke_qualification, revoke_admission = (
        state_store.bind_qual_admission_state_authority()
    )

    subject = SubjectState(
        subject_id=SUBJECT_ID,
        role_id=ROLE_ID,
        trust_domain=TRUST_DOMAIN,
        current_runtime_version="v1",
    )
    state_store.add_subject(subject)
    state_store.grant_protected_resource_authority(
        protected_resource_authority_token,
    )

    harness = Harness(
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
        qual_admission_pub=qa_pub,
        profile_registry_pub=pfs_pub,
        subject=subject,
        profile_v1=copy.deepcopy(profile_v1),
        profile_v2=copy.deepcopy(profile_v2),
        qualification=copy.deepcopy(qualification),
        admission=copy.deepcopy(admission),
    )

    controls = TrustedControls(
        activate_profile=activate_profile,
        revoke_qualification=revoke_qualification,
        revoke_admission=revoke_admission,
        sign_profile=lambda p: sign_conformance_profile(p, pfs_priv, pfs_pub),
        sign_qa_fixture=lambda f: _sign_qa(qa_priv, f),
        profile_registry_pub=pfs_pub,
    )
    return harness, controls


def build_harness(*, prefix: str = "acl-poc") -> Harness:
    """Build participant-facing harness; trusted controls are discarded."""
    harness, _controls = build_harness_with_controls(prefix=prefix)
    return harness


def attach_executor(h: Harness):
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

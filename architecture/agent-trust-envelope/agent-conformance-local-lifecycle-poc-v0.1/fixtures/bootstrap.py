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

    clock: LogicalClock
    state_store: StateStore
    nonce_registry: NonceRegistry

    observer: TriggerObserver
    r13: R13Evaluator
    r14: LifecycleAuthority
    authorization: AuthorizationService
    audit: Any

    qual_admission_pub: Ed25519PublicKey
    profile_registry_pub: Ed25519PublicKey

    subject: SubjectState
    profile_v1: ConformanceProfile
    profile_v2: ConformanceProfile
    qualification: QualificationFixture
    admission: AdmissionFixture


class AuditView:
    """Participant-facing read/verify view of the authoritative audit ledger."""

    def __init__(self, recorder: AuditRecorder) -> None:
        self.__recorder = recorder
        self.public_key = recorder.public_key
        self.key_id = recorder.key_id

    def records(self):
        return self.__recorder.records()

    def verify_chain(self) -> bool:
        return self.__recorder.verify_chain()

    def verify_causal_order(self, expected_sequence):
        return self.__recorder.verify_causal_order(expected_sequence)


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
        sign_r13: Callable[[Any], Any],
        sign_r14: Callable[[Any], Any],
        sign_trigger: Callable[[Any], Any],
        sign_capability: Callable[[Any], Any],
        grant_protected_resource_authority: Callable[[], None],
        consume_protected_resource_authority: Callable[[], None],
        submit_measured_runtime: Callable[[str, str], str],
        append_audit: Callable[..., Any],
        profile_registry_pub: Ed25519PublicKey,
    ) -> None:
        self.__activate_profile = activate_profile
        self.__revoke_qualification = revoke_qualification
        self.__revoke_admission = revoke_admission
        self.__sign_profile = sign_profile
        self.__sign_qa_fixture = sign_qa_fixture
        self.__sign_r13 = sign_r13
        self.__sign_r14 = sign_r14
        self.__sign_trigger = sign_trigger
        self.__sign_capability = sign_capability
        self.__grant_protected_resource_authority = grant_protected_resource_authority
        self.__consume_protected_resource_authority = consume_protected_resource_authority
        self.__submit_measured_runtime = submit_measured_runtime
        self.__append_audit = append_audit
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

    def sign_r13_for_attack_test(self, artifact: Any) -> Any:
        return self.__sign_r13(artifact)

    def sign_r14_for_attack_test(self, artifact: Any) -> Any:
        return self.__sign_r14(artifact)

    def sign_trigger_for_attack_test(self, artifact: Any) -> Any:
        return self.__sign_trigger(artifact)

    def sign_capability_for_attack_test(self, artifact: Any) -> Any:
        return self.__sign_capability(artifact)

    def regrant_protected_resource_authority(self) -> None:
        self.__grant_protected_resource_authority()

    def submit_measured_runtime(self, value: str, artifact_id: str) -> str:
        return self.__submit_measured_runtime(value, artifact_id)

    def append_audit(self, *, event_kind: str, payload: dict, logical_ts: int):
        return self.__append_audit(
            event_kind=event_kind, payload=payload, logical_ts=logical_ts,
        )

    def attach_executor(self, harness: Harness):
        from conformance.executor import Executor

        return Executor(
            executor_id="exec-1",
            state_store=harness.state_store,
            nonce_registry=harness.nonce_registry,
            authorization=harness.authorization,
            protected_resource_path=harness.protected_resource_path,
            _consume_protected_resource_authority=self.__consume_protected_resource_authority,
        )


def _sign_artifact(priv, artifact: Any) -> Any:
    artifact.signature = sign_ed25519(
        priv, artifact.signature_domain, artifact.signing_payload(),
    )
    return artifact


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
    grant_protected_resource_authority, consume_protected_resource_authority = (
        state_store.bind_protected_resource_authority()
    )

    harness = Harness(
        tmpdir=tmpdir,
        protected_resource_path=protected_resource_path,
        clock=clock,
        state_store=state_store,
        nonce_registry=nonce_registry,
        observer=observer,
        r13=r13,
        r14=r14,
        authorization=authorization,
        audit=AuditView(audit),
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
        sign_r13=lambda a: _sign_artifact(r13_priv, a),
        sign_r14=lambda a: _sign_artifact(r14_priv, a),
        sign_trigger=lambda a: _sign_artifact(obs_priv, a),
        sign_capability=lambda a: _sign_artifact(az_priv, a),
        grant_protected_resource_authority=grant_protected_resource_authority,
        consume_protected_resource_authority=consume_protected_resource_authority,
        submit_measured_runtime=observer._submit_measured_runtime_trusted,
        append_audit=audit.append,
        profile_registry_pub=pfs_pub,
    )
    return harness, controls


def build_harness(*, prefix: str = "acl-poc") -> Harness:
    """Build participant-facing harness; trusted controls are discarded."""
    harness, _controls = build_harness_with_controls(prefix=prefix)
    return harness


def teardown(h: Harness) -> None:
    shutil.rmtree(h.tmpdir, ignore_errors=True)


def protected_resource_line_count(path: str) -> int:
    with open(path, "r", encoding="utf-8") as fh:
        return sum(1 for line in fh if line.strip())

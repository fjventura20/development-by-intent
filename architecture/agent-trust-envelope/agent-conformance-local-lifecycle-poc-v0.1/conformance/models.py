"""Agent Conformance Local Lifecycle PoC v0.1 — frozen artifact models.

The v0.1.1 design enumerates the immutable signed artifacts this PoC
exchanges. Every artifact carries:

  - artifact_id
  - artifact_digest (canonical SHA-256 of the signing payload)
  - subject_id / role_id / trust_domain (where applicable)
  - signature (raw Ed25519 signature bytes)
  - signature_domain (the explicit domain separator)

The signing payload INCLUDES the artifact's own id and digest and all
semantic fields; it EXCLUDES only `signature` and `signature_domain`.

Signing domains are local to this PoC and follow the frozen protocol's
domain-separation convention (a stable dotted-string per artifact kind).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Optional

# Artifact signing domains (frozen §24 + §10A + §13 + §14).

DOMAIN_PROFILE = "ate.conformance.profile.v1"
DOMAIN_RUNTIME_EVIDENCE = "ate.conformance.runtime_evidence.v1"
DOMAIN_TRIGGER_OBSERVATION = "ate.conformance.trigger_observation.v1"
DOMAIN_R13_EVAL = "ate.conformance.r13_eval.v1"
DOMAIN_R14_STATE = "ate.conformance.r14_state.v1"
DOMAIN_QUALIFICATION_FIXTURE = "ate.conformance.qualification_fixture.v1"
DOMAIN_ADMISSION_FIXTURE = "ate.conformance.admission_fixture.v1"
DOMAIN_CAPABILITY = "ate.conformance.capability.v1"
DOMAIN_AUDIT = "ate.conformance.audit.v1"

ALL_DOMAINS = (
    DOMAIN_PROFILE,
    DOMAIN_RUNTIME_EVIDENCE,
    DOMAIN_TRIGGER_OBSERVATION,
    DOMAIN_R13_EVAL,
    DOMAIN_R14_STATE,
    DOMAIN_QUALIFICATION_FIXTURE,
    DOMAIN_ADMISSION_FIXTURE,
    DOMAIN_CAPABILITY,
    DOMAIN_AUDIT,
)


@dataclass
class SignedArtifact:
    """Base class: every artifact is identified, digested, signed.

    `signature` and `signature_domain` are the only fields excluded from
    the canonical signing payload.
    """

    artifact_id: str
    signature: bytes = b""
    signature_domain: str = ""

    def signing_payload(self) -> Dict[str, Any]:
        """Return the dict that gets canonicalized for signing/verification."""
        raise NotImplementedError


def signing_payload(obj: Any) -> Dict[str, Any]:
    """Compute the canonical signing payload of a signed artifact."""
    if not isinstance(obj, SignedArtifact):
        raise TypeError("signing_payload requires a SignedArtifact instance")
    return obj.signing_payload()


# ---------------------------------------------------------------------------
# Conformance profile (frozen §9)
# ---------------------------------------------------------------------------


@dataclass
class ConformanceProfile(SignedArtifact):
    """Predeclared ConformanceRequirementsProfile (frozen §9).

    profile_id / profile_version / required_runtime_version are the
    semantic fields. The profile also pins trust_domain, role_id,
    trigger_source, evaluator_authority, and lifecycle_state_authority
    per §9.
    """

    profile_id: str = ""
    profile_version: int = 0
    trust_domain: str = ""
    role_id: str = ""
    required_runtime_version: str = ""
    trigger_source: str = "local-runtime-observer"
    max_conformance_age: int = 0
    whole_role_failure: bool = True
    evaluator_authority: str = "R13"
    lifecycle_state_authority: str = "R14"
    signature_domain: str = field(default=DOMAIN_PROFILE)

    def signing_payload(self) -> Dict[str, Any]:
        return {
            "artifact_id": self.artifact_id,
            "artifact_kind": "ConformanceProfile",
            "profile_id": self.profile_id,
            "profile_version": self.profile_version,
            "trust_domain": self.trust_domain,
            "role_id": self.role_id,
            "required_runtime_version": self.required_runtime_version,
            "trigger_source": self.trigger_source,
            "max_conformance_age": self.max_conformance_age,
            "whole_role_failure": self.whole_role_failure,
            "evaluator_authority": self.evaluator_authority,
            "lifecycle_state_authority": self.lifecycle_state_authority,
        }


# ---------------------------------------------------------------------------
# Runtime evidence (frozen §10, §11, §16)
# ---------------------------------------------------------------------------


@dataclass
class RuntimeEvidence(SignedArtifact):
    """Runtime measurement evidence for a subject.

    Captures the observer-authoritative measured runtime version and
    the logical timestamp at which it was observed. The trigger
    observer reads the authoritative store; subject-facing interfaces
    cannot rewrite the prior evidence (frozen §13).
    """

    subject_id: str = ""
    trust_domain: str = ""
    measured_runtime_version: str = ""
    observer_id: str = "local-runtime-observer"
    logical_ts: int = 0
    event_sequence: int = 0
    signature_domain: str = field(default=DOMAIN_RUNTIME_EVIDENCE)

    def signing_payload(self) -> Dict[str, Any]:
        return {
            "artifact_id": self.artifact_id,
            "artifact_kind": "RuntimeEvidence",
            "subject_id": self.subject_id,
            "trust_domain": self.trust_domain,
            "measured_runtime_version": self.measured_runtime_version,
            "observer_id": self.observer_id,
            "logical_ts": self.logical_ts,
            "event_sequence": self.event_sequence,
        }


# ---------------------------------------------------------------------------
# Trigger observation (frozen §13)
# ---------------------------------------------------------------------------


@dataclass
class TriggerObservation(SignedArtifact):
    """Independent signed trigger observation emitted by the observer.

    The trigger records the digest of the prior and current measured
    values so the verifier can detect attempted subject-side fabrication.
    """

    trigger_class: str = "T4_RUNTIME"
    trigger_type: str = "RUNTIME_VERSION_CHANGED"
    subject_id: str = ""
    trust_domain: str = ""
    prior_value_digest: str = ""
    current_value_digest: str = ""
    severity: str = "MANDATORY_REATTESTATION"
    prior_evidence_id: str = ""
    current_evidence_id: str = ""
    logical_ts: int = 0
    event_sequence: int = 0
    signature_domain: str = field(default=DOMAIN_TRIGGER_OBSERVATION)

    def signing_payload(self) -> Dict[str, Any]:
        return {
            "artifact_id": self.artifact_id,
            "artifact_kind": "TriggerObservation",
            "trigger_class": self.trigger_class,
            "trigger_type": self.trigger_type,
            "subject_id": self.subject_id,
            "trust_domain": self.trust_domain,
            "prior_value_digest": self.prior_value_digest,
            "current_value_digest": self.current_value_digest,
            "severity": self.severity,
            "prior_evidence_id": self.prior_evidence_id,
            "current_evidence_id": self.current_evidence_id,
            "logical_ts": self.logical_ts,
            "event_sequence": self.event_sequence,
        }


# ---------------------------------------------------------------------------
# R13 evaluation result (frozen §14, §16)
# ---------------------------------------------------------------------------


RECOMMENDED_CONFORMANT = "CONFORMANT"
RECOMMENDED_REATTESTATION_REQUIRED = "REATTESTATION_REQUIRED"
RECOMMENDED_SUSPENDED = "SUSPENDED"


@dataclass
class R13Evaluation(SignedArtifact):
    """Immutable R13 evaluation result.

    `recommended_state` is the recommended lifecycle state; the
    authoritative transition is published separately by R14 (frozen
    §14.3: "R13 evaluation does not itself change executable
    lifecycle state").
    """

    subject_id: str = ""
    trust_domain: str = ""
    profile_id: str = ""
    profile_version: int = 0
    profile_digest: str = ""
    runtime_evidence_id: str = ""
    measured_runtime_version: str = ""
    qualification_state: str = ""
    admission_state: str = ""
    recommended_state: str = ""
    rationale: str = ""
    logical_ts: int = 0
    event_sequence: int = 0
    signature_domain: str = field(default=DOMAIN_R13_EVAL)

    def signing_payload(self) -> Dict[str, Any]:
        return {
            "artifact_id": self.artifact_id,
            "artifact_kind": "R13Evaluation",
            "subject_id": self.subject_id,
            "trust_domain": self.trust_domain,
            "profile_id": self.profile_id,
            "profile_version": self.profile_version,
            "profile_digest": self.profile_digest,
            "runtime_evidence_id": self.runtime_evidence_id,
            "measured_runtime_version": self.measured_runtime_version,
            "qualification_state": self.qualification_state,
            "admission_state": self.admission_state,
            "recommended_state": self.recommended_state,
            "rationale": self.rationale,
            "logical_ts": self.logical_ts,
            "event_sequence": self.event_sequence,
        }


# ---------------------------------------------------------------------------
# R14 lifecycle state (frozen §14, §16, §21)
# ---------------------------------------------------------------------------


LIFECYCLE_CONFORMANT = "CONFORMANT"
LIFECYCLE_REATTESTATION_REQUIRED = "REATTESTATION_REQUIRED"
LIFECYCLE_SUSPENDED = "SUSPENDED"

ALL_LIFECYCLE_STATES = (
    LIFECYCLE_CONFORMANT,
    LIFECYCLE_REATTESTATION_REQUIRED,
    LIFECYCLE_SUSPENDED,
)


@dataclass
class R14State(SignedArtifact):
    """Authoritative lifecycle state decision published by R14.

    `state_epoch` is monotonic. The executor uses (observed_state_epoch,
    current state_epoch) to reject stale capabilities (frozen §12A
    step 7 and §15).
    """

    subject_id: str = ""
    role_id: str = ""
    trust_domain: str = ""
    prior_state: str = ""
    new_state: str = ""
    state_epoch: int = 0
    rationale: str = ""
    r13_evaluation_id: str = ""
    trigger_observation_id: str = ""
    logical_ts: int = 0
    event_sequence: int = 0
    signature_domain: str = field(default=DOMAIN_R14_STATE)

    def signing_payload(self) -> Dict[str, Any]:
        return {
            "artifact_id": self.artifact_id,
            "artifact_kind": "R14State",
            "subject_id": self.subject_id,
            "role_id": self.role_id,
            "trust_domain": self.trust_domain,
            "prior_state": self.prior_state,
            "new_state": self.new_state,
            "state_epoch": self.state_epoch,
            "rationale": self.rationale,
            "r13_evaluation_id": self.r13_evaluation_id,
            "trigger_observation_id": self.trigger_observation_id,
            "logical_ts": self.logical_ts,
            "event_sequence": self.event_sequence,
        }


# ---------------------------------------------------------------------------
# Qualification / Admission fixtures (frozen §10A)
# ---------------------------------------------------------------------------


FIXTURE_STATE_ACTIVE = "ACTIVE"
FIXTURE_STATE_REVOKED = "REVOKED"
FIXTURE_STATE_EXPIRED = "EXPIRED"


@dataclass
class QualificationFixture(SignedArtifact):
    """Deterministic signed qualification fixture (§10A).

    The fixture exposes the eight required fields per §10A. The
    authorization service MUST verify all of: fixture integrity,
    issuer validity, subject/role/domain binding, current_state == ACTIVE.
    """

    artifact_digest: str = ""
    subject_id: str = ""
    role_id: str = ""
    trust_domain: str = ""
    issuer: str = ""
    issuer_key_id: str = ""
    current_state: str = FIXTURE_STATE_ACTIVE
    issued_at: int = 0
    expires_at: int = 0
    signature_domain: str = field(default=DOMAIN_QUALIFICATION_FIXTURE)

    def signing_payload(self) -> Dict[str, Any]:
        return {
            "artifact_id": self.artifact_id,
            "artifact_kind": "QualificationFixture",
            "subject_id": self.subject_id,
            "role_id": self.role_id,
            "trust_domain": self.trust_domain,
            "issuer": self.issuer,
            "issuer_key_id": self.issuer_key_id,
            "current_state": self.current_state,
            "issued_at": self.issued_at,
            "expires_at": self.expires_at,
        }


@dataclass
class AdmissionFixture(SignedArtifact):
    """Deterministic signed admission fixture (§10A)."""

    artifact_digest: str = ""
    subject_id: str = ""
    role_id: str = ""
    trust_domain: str = ""
    issuer: str = ""
    issuer_key_id: str = ""
    current_state: str = FIXTURE_STATE_ACTIVE
    issued_at: int = 0
    expires_at: int = 0
    signature_domain: str = field(default=DOMAIN_ADMISSION_FIXTURE)

    def signing_payload(self) -> Dict[str, Any]:
        return {
            "artifact_id": self.artifact_id,
            "artifact_kind": "AdmissionFixture",
            "subject_id": self.subject_id,
            "role_id": self.role_id,
            "trust_domain": self.trust_domain,
            "issuer": self.issuer,
            "issuer_key_id": self.issuer_key_id,
            "current_state": self.current_state,
            "issued_at": self.issued_at,
            "expires_at": self.expires_at,
        }


# ---------------------------------------------------------------------------
# Execution capability (frozen §12, §12A)
# ---------------------------------------------------------------------------


@dataclass
class ExecutionCapability(SignedArtifact):
    """Single-use bounded execution capability (frozen §12)."""

    subject_id: str = ""
    role_id: str = ""
    trust_domain: str = ""
    action_digest: str = ""
    observed_conformance_state: str = ""
    observed_state_epoch: int = 0
    nonce: str = ""
    issued_at: int = 0
    expires_at: int = 0
    issuer: str = ""
    issuer_key_id: str = ""
    signature_domain: str = field(default=DOMAIN_CAPABILITY)

    def signing_payload(self) -> Dict[str, Any]:
        return {
            "artifact_id": self.artifact_id,
            "artifact_kind": "ExecutionCapability",
            "subject_id": self.subject_id,
            "role_id": self.role_id,
            "trust_domain": self.trust_domain,
            "action_digest": self.action_digest,
            "observed_conformance_state": self.observed_conformance_state,
            "observed_state_epoch": self.observed_state_epoch,
            "nonce": self.nonce,
            "issued_at": self.issued_at,
            "expires_at": self.expires_at,
            "issuer": self.issuer,
            "issuer_key_id": self.issuer_key_id,
        }


# ---------------------------------------------------------------------------
# Audit record (frozen §6.8, §20A)
# ---------------------------------------------------------------------------


@dataclass
class AuditRecord:
    """Append-only audit record (frozen §6.8, §20A).

    Audit records carry `event_sequence` for monotonic ordering. The
    `payload` is the JSON-canonicalizable semantic content. `prev_hash`
    chains each record to the previous one. `record_hash` is the digest
    of the canonical (sequence, event_kind, payload, prev_hash) tuple.
    """

    event_sequence: int
    event_kind: str
    payload: Dict[str, Any]
    prev_hash: str
    record_hash: str
    payload_digest: str
    logical_ts: int
    signature: bytes
    signature_domain: str = field(default=DOMAIN_AUDIT)

    def signing_payload(self) -> Dict[str, Any]:
        return {
            "artifact_kind": "AuditRecord",
            "event_sequence": self.event_sequence,
            "event_kind": self.event_kind,
            "payload": self.payload,
            "prev_hash": self.prev_hash,
            "payload_digest": self.payload_digest,
            "logical_ts": self.logical_ts,
        }
"""Agent Conformance Local Lifecycle PoC v0.1 — authoritative local state.

H1-H3 final correction:
- lifecycle state is mutated only by accepting a valid R14-signed state artifact;
- readers receive immutable lifecycle snapshots;
- a frozen profile registry may be installed exactly once;
- profile activation capability is a closure returned only at one-time installation;
- qualification/admission state writers are one-time bound closures;
- there are no reusable/public authority-token getters.
"""

from __future__ import annotations

import copy
import threading
from dataclasses import dataclass, field
from typing import Any, Dict, Optional

from .crypto import key_id_from_public_key, verify_ed25519

_VALID_LIFECYCLE_STATES = {
    "UNKNOWN", "CONFORMANT", "REATTESTATION_REQUIRED", "SUSPENDED",
}


@dataclass
class LogicalClock:
    _value: int = 0
    _lock: threading.Lock = field(default_factory=threading.Lock, repr=False)

    def now(self) -> int:
        return self._value

    def advance(self) -> int:
        with self._lock:
            self._value += 1
            return self._value


@dataclass
class SubjectState:
    subject_id: str
    role_id: str
    trust_domain: str
    current_runtime_version: str = "v1"


@dataclass(frozen=True)
class LifecycleSnapshot:
    current_state: str
    state_epoch: int


@dataclass
class _AuthoritativeLifecycle:
    current_state: str = "UNKNOWN"
    state_epoch: int = 0


class StateStore:
    """Authoritative state container for the local PoC."""

    def __init__(self) -> None:
        self._subjects: Dict[str, SubjectState] = {}
        self._lifecycle: Dict[str, _AuthoritativeLifecycle] = {}
        self._lifecycle_authority_id: Optional[str] = None
        self._lifecycle_authority_pub: Optional[Any] = None

        self._active_profile: Optional[Any] = None
        self._profile_registry: Optional[Any] = None
        self._profile_registry_installed = False

        self._qualification_fixtures: Dict[str, Any] = {}
        self._admission_fixtures: Dict[str, Any] = {}
        self._qual_admission_issuer_pub: Optional[Any] = None
        self._qual_admission_issuer_key_id: Optional[str] = None
        self._qual_admission_issuer_id: Optional[str] = None
        self._qual_admission_writer_bound = False

        self._protected_resource_authority_bound = False
        self._protected_resource_authority_available = False

    # ---- subject ----

    def add_subject(self, subject: SubjectState) -> None:
        # Authoritative identity is insert-only and must not alias a
        # participant-facing SubjectState object.
        if subject.subject_id in self._subjects:
            raise PermissionError("subject registration is insert-only")
        self._subjects[subject.subject_id] = copy.deepcopy(subject)
        self._lifecycle.setdefault(subject.subject_id, _AuthoritativeLifecycle())

    def get_subject(self, subject_id: str) -> SubjectState:
        if subject_id not in self._subjects:
            raise KeyError(f"unknown subject: {subject_id}")
        return copy.deepcopy(self._subjects[subject_id])

    # ---- lifecycle authority: signature-based, no secret token ----

    def register_lifecycle_authority(
        self, *, authority_id: str, authority_public_key: Any,
    ) -> None:
        if self._lifecycle_authority_pub is not None:
            raise PermissionError("lifecycle authority is already registered")
        self._lifecycle_authority_id = authority_id
        self._lifecycle_authority_pub = authority_public_key

    def apply_authoritative_state(self, state: Any) -> None:
        """Accept only a valid R14-signed next state artifact.

        This removes the reusable writer-token surface. Calling this
        method is harmless without the registered R14 private key.
        """
        pub = self._lifecycle_authority_pub
        if pub is None:
            raise PermissionError("no lifecycle authority registered")
        if state.new_state not in _VALID_LIFECYCLE_STATES:
            raise ValueError(f"invalid lifecycle state: {state.new_state!r}")
        if state.subject_id not in self._subjects:
            raise KeyError(f"unknown subject: {state.subject_id}")
        subject = self._subjects[state.subject_id]
        if state.role_id != subject.role_id or state.trust_domain != subject.trust_domain:
            raise PermissionError("R14 state subject binding mismatch")
        if not verify_ed25519(
            pub, state.signature, state.signature_domain, state.signing_payload(),
        ):
            raise PermissionError("R14 state signature does not verify")

        rec = self._lifecycle[state.subject_id]
        if state.prior_state != rec.current_state:
            raise ValueError("R14 prior_state does not match authoritative state")
        if state.state_epoch != rec.state_epoch + 1:
            raise ValueError("R14 state_epoch must advance exactly by one")

        rec.current_state = state.new_state
        rec.state_epoch = state.state_epoch

    def get_authoritative_state(self, subject_id: str) -> LifecycleSnapshot:
        if subject_id not in self._lifecycle:
            raise KeyError(f"unknown subject: {subject_id}")
        rec = self._lifecycle[subject_id]
        return LifecycleSnapshot(rec.current_state, rec.state_epoch)

    def current_state(self, subject_id: str) -> str:
        return self.get_authoritative_state(subject_id).current_state

    def state_epoch(self, subject_id: str) -> int:
        return self.get_authoritative_state(subject_id).state_epoch

    # ---- profile registry: install exactly once, activate via bound closure ----

    def set_active_profile(self, profile: Any) -> None:
        raise PermissionError("direct profile activation is disabled")

    def get_active_profile(self) -> Optional[Any]:
        return None if self._active_profile is None else copy.deepcopy(self._active_profile)

    def install_profile_registry(self, registry: Any):
        """Install one already-frozen registry and return its trusted activator.

        The activator closure is returned only to bootstrap/trusted controls.
        Registry replacement is permanently rejected.
        """
        if self._profile_registry_installed:
            raise PermissionError("profile registry installation is one-time")
        if not getattr(registry, "frozen", False):
            raise PermissionError("profile registry must be frozen before installation")
        self._profile_registry = registry
        self._profile_registry_installed = True

        def activate_predeclared(profile_id: str, profile_digest: str) -> Any:
            # Capture the exact installed registry. Even if someone could
            # mutate another object, it cannot replace this authority.
            if self._profile_registry is not registry:
                raise PermissionError("authoritative profile registry changed")
            profile = registry.resolve_frozen(profile_id, profile_digest)
            self._active_profile = copy.deepcopy(profile)
            return copy.deepcopy(profile)

        return activate_predeclared

    def activate_profile(self, **_: Any) -> Any:
        raise PermissionError(
            "participant-facing profile activation is unavailable; "
            "activation capability is retained by trusted controls"
        )

    # ---- qualification/admission fixtures ----

    def register_qualification_fixture(self, fixture: Any) -> None:
        if fixture.artifact_id in self._qualification_fixtures:
            raise PermissionError("qualification fixture registration is immutable by artifact_id")
        self._qualification_fixtures[fixture.artifact_id] = copy.deepcopy(fixture)

    def register_admission_fixture(self, fixture: Any) -> None:
        if fixture.artifact_id in self._admission_fixtures:
            raise PermissionError("admission fixture registration is immutable by artifact_id")
        self._admission_fixtures[fixture.artifact_id] = copy.deepcopy(fixture)

    def get_qualification_fixture(self, artifact_id: str) -> Any:
        value = self._qualification_fixtures.get(artifact_id)
        return None if value is None else copy.deepcopy(value)

    def get_admission_fixture(self, artifact_id: str) -> Any:
        value = self._admission_fixtures.get(artifact_id)
        return None if value is None else copy.deepcopy(value)

    def qualification_state_for(self, subject_id: str) -> str:
        subject = self.get_subject(subject_id)
        matches = [
            f for f in self._qualification_fixtures.values()
            if f.subject_id == subject.subject_id
            and f.role_id == subject.role_id
            and f.trust_domain == subject.trust_domain
        ]
        if len(matches) != 1:
            raise RuntimeError("qualification state is not uniquely resolvable")
        return matches[0].current_state

    def admission_state_for(self, subject_id: str) -> str:
        subject = self.get_subject(subject_id)
        matches = [
            f for f in self._admission_fixtures.values()
            if f.subject_id == subject.subject_id
            and f.role_id == subject.role_id
            and f.trust_domain == subject.trust_domain
        ]
        if len(matches) != 1:
            raise RuntimeError("admission state is not uniquely resolvable")
        return matches[0].current_state

    def bind_qual_admission_state_authority(self):
        """Bind the qualification/admission state writer exactly once.

        Returns trusted closures, never a reusable token.
        """
        if self._qual_admission_writer_bound:
            raise PermissionError("qualification/admission state authority already bound")
        self._qual_admission_writer_bound = True

        def revoke_qualification(artifact_id: str) -> None:
            if artifact_id not in self._qualification_fixtures:
                raise KeyError(f"unknown qualification fixture: {artifact_id}")
            self._qualification_fixtures[artifact_id].current_state = "REVOKED"

        def revoke_admission(artifact_id: str) -> None:
            if artifact_id not in self._admission_fixtures:
                raise KeyError(f"unknown admission fixture: {artifact_id}")
            self._admission_fixtures[artifact_id].current_state = "REVOKED"

        return revoke_qualification, revoke_admission

    def revoke_qualification(self, *args: Any, **kwargs: Any) -> None:
        raise PermissionError("participant-facing qualification state mutation is unavailable")

    def revoke_admission(self, *args: Any, **kwargs: Any) -> None:
        raise PermissionError("participant-facing admission state mutation is unavailable")

    def register_qual_admission_issuer(
        self, *, issuer_id: str, issuer_public_key: Any,
    ) -> None:
        if self._qual_admission_issuer_pub is not None:
            raise PermissionError("qualification/admission issuer already registered")
        self._qual_admission_issuer_pub = issuer_public_key
        self._qual_admission_issuer_key_id = key_id_from_public_key(issuer_public_key)
        self._qual_admission_issuer_id = issuer_id

    def qual_admission_issuer_pub(self) -> Optional[Any]:
        return self._qual_admission_issuer_pub

    def qual_admission_issuer_key_id(self) -> Optional[str]:
        return self._qual_admission_issuer_key_id

    def qual_admission_issuer_id(self) -> Optional[str]:
        return self._qual_admission_issuer_id

    # ---- protected resource authority: bound closures, no public token ----

    def bind_protected_resource_authority(self):
        """Bind protected-resource authority exactly once.

        Returns trusted grant/consume closures. The credential itself is
        captured by the closure boundary and is never placed on StateStore or
        the participant-facing Harness.
        """
        if self._protected_resource_authority_bound:
            raise PermissionError("protected-resource authority already bound")
        self._protected_resource_authority_bound = True
        self._protected_resource_authority_available = True

        def grant() -> None:
            self._protected_resource_authority_available = True

        def consume() -> None:
            if not self._protected_resource_authority_available:
                raise PermissionError("protected-resource authority unavailable")
            self._protected_resource_authority_available = False

        return grant, consume

    def grant_protected_resource_authority(self, *_: Any, **__: Any) -> None:
        raise PermissionError(
            "participant-facing protected-resource authority grant is unavailable"
        )

    def consume_protected_resource_authority(self, *_: Any, **__: Any) -> None:
        raise PermissionError(
            "participant-facing protected-resource authority consumption is unavailable"
        )

    def has_protected_resource_authority(self) -> bool:
        return self._protected_resource_authority_available


class RuntimeObserverStore:
    """Observer-authoritative append-only runtime evidence store."""

    def __init__(self) -> None:
        self._evidence: Dict[str, Any] = {}
        self._current: Optional[str] = None

    def _record_evidence_trusted(self, evidence: object) -> str:
        self._evidence[evidence.artifact_id] = copy.deepcopy(evidence)
        self._current = evidence.artifact_id
        return evidence.artifact_id

    def record_evidence(self, *args: Any, **kwargs: Any) -> str:
        raise PermissionError(
            "participant-facing observer history mutation is unavailable"
        )

    def get_evidence(self, artifact_id: str):
        value = self._evidence.get(artifact_id)
        return None if value is None else copy.deepcopy(value)

    def get_current_evidence_id(self) -> Optional[str]:
        return self._current

    def get_current_value(self) -> Optional[str]:
        if self._current is None:
            return None
        return self._evidence[self._current].measured_runtime_version

    def get_prior_evidence_id(self) -> Optional[str]:
        if self._current is None or len(self._evidence) < 2:
            return None
        ids = list(self._evidence.keys())
        for aid in ids:
            if aid != self._current:
                return aid
        return None

    def history(self):
        return [copy.deepcopy(v) for v in self._evidence.values()]


class NonceRegistry:
    def __init__(self) -> None:
        self._states: Dict[str, str] = {}

    def reserve(self, nonce: str) -> None:
        if nonce in self._states:
            raise ValueError(f"nonce already used: {nonce}")
        self._states[nonce] = "RESERVED"

    def consume(self, nonce: str) -> None:
        if self._states.get(nonce) != "RESERVED":
            raise ValueError(f"nonce not RESERVED: {nonce}")
        self._states[nonce] = "CONSUMED"

    def status(self, nonce: str) -> Optional[str]:
        return self._states.get(nonce)

    def is_reserved_or_consumed(self, nonce: str) -> bool:
        return nonce in self._states

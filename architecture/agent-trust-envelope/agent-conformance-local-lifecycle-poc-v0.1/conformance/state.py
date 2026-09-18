"""Agent Conformance Local Lifecycle PoC v0.1 — state.

This module owns the local state needed by the conformance authorities.
It enforces the separation rules from frozen §7:

  - the subject-facing interface CANNOT mutate lifecycle state, the
    lifecycle epoch, R13 evaluation results, R14 decisions, capability
    issuer state, executor credentials, or audit history.
  - the runtime observer's authoritative measurement store is distinct
    from any subject-requested runtime input (frozen §13).

The `LogicalClock` advances only through `advance()` (or
`advance_for_observer()`); callers cannot write arbitrary timestamps.

`StateStore` holds the subject identity, role binding, current
runtime_version, conformance state, and state_epoch. Mutations to
`current_state` and `state_epoch` are only exposed via the
`LifecycleAuthority` (see lifecycle.py) — not via this module — so
direct subject-side mutation is not possible.

`AuthorityStore` holds the predeclared profiles, qualification/admission
fixtures, and the protected-resource authority token. The subject
interface cannot obtain the protected-resource authority token through
the conformance APIs; only the executor can (frozen §6.7, §12A.9).
"""

from __future__ import annotations

import threading
from dataclasses import dataclass, field
from typing import Any, Dict, Optional


# ---------------------------------------------------------------------------
# Logical clock (frozen §24)
# ---------------------------------------------------------------------------


@dataclass
class LogicalClock:
    """Monotonic logical clock for the PoC.

    The clock advances by exactly one tick per `advance()` call; this
    preserves deterministic ordering and prevents replay-time skew.
    """

    _value: int = 0
    _lock: threading.Lock = field(default_factory=threading.Lock, repr=False)

    def now(self) -> int:
        return self._value

    def advance(self) -> int:
        with self._lock:
            self._value += 1
            return self._value


# ---------------------------------------------------------------------------
# Subject state store (frozen §6.1)
# ---------------------------------------------------------------------------


@dataclass
class SubjectState:
    """Identity, role binding, and current conformance state for one subject.

    The PoC has exactly one subject (frozen §5). `current_state` and
    `state_epoch` are advanced only by the LifecycleAuthority.
    """

    subject_id: str
    role_id: str
    trust_domain: str
    current_state: str = "UNKNOWN"
    state_epoch: int = 0
    current_runtime_version: str = "v1"
    runtime_evidence_id: Optional[str] = None


# ---------------------------------------------------------------------------
# State store (frozen §6.1, §6.2, §6.5)
# ---------------------------------------------------------------------------


class StateStore:
    """In-memory state store for the PoC.

    Holds the subject state, the active profile, the qualification and
    admission fixtures, and the protected-resource authority. Does
    NOT expose lifecycle-state or epoch mutations to the subject —
    those go through the LifecycleAuthority (frozen §7).
    """

    def __init__(self) -> None:
        self._subjects: Dict[str, SubjectState] = {}
        # The currently ACTIVE ConformanceProfile (one at a time per §9).
        self._active_profile: Optional[Any] = None
        # Active qualification/admission fixtures keyed by artifact_id.
        self._qualification_fixtures: Dict[str, Any] = {}
        self._admission_fixtures: Dict[str, Any] = {}
        # The protected-resource authority token. Only the executor is
        # permitted to consume it (frozen §12A.9).
        self._protected_resource_authority: Optional[str] = None

    # ---- subject ----

    def add_subject(self, subject: SubjectState) -> None:
        self._subjects[subject.subject_id] = subject

    def get_subject(self, subject_id: str) -> SubjectState:
        if subject_id not in self._subjects:
            raise KeyError(f"unknown subject: {subject_id}")
        return self._subjects[subject_id]

    # ---- profile (frozen §9) ----

    def set_active_profile(self, profile: object) -> None:
        """Activate a predeclared profile. Used by the PoC harness, not the subject."""
        self._active_profile = profile

    def get_active_profile(self) -> Optional[object]:
        return self._active_profile

    # ---- qualification/admission fixtures (frozen §10A) ----

    def register_qualification_fixture(self, fixture: object) -> None:
        self._qualification_fixtures[fixture.artifact_id] = fixture

    def register_admission_fixture(self, fixture: object) -> None:
        self._admission_fixtures[fixture.artifact_id] = fixture

    def get_qualification_fixture(self, artifact_id: str):
        return self._qualification_fixtures.get(artifact_id)

    def get_admission_fixture(self, artifact_id: str):
        return self._admission_fixtures.get(artifact_id)

    # ---- protected-resource authority (frozen §6.7, §12A.9) ----

    def grant_protected_resource_authority(self, token: str) -> None:
        """Grant the protected-resource authority (executor-only consumer)."""
        self._protected_resource_authority = token

    def consume_protected_resource_authority(self) -> str:
        if self._protected_resource_authority is None:
            raise PermissionError(
                "protected-resource authority unavailable to subject-facing interfaces"
            )
        token = self._protected_resource_authority
        self._protected_resource_authority = None
        return token

    def has_protected_resource_authority(self) -> bool:
        return self._protected_resource_authority is not None


# ---------------------------------------------------------------------------
# Runtime observer store (frozen §13)
# ---------------------------------------------------------------------------


class RuntimeObserverStore:
    """Observer-authoritative measured runtime state.

    Distinct from any subject-requested runtime input (frozen §13).
    The subject-facing interface cannot rewrite history: only
    `record_evidence()` appends, and there is no method to mutate a
    prior record.
    """

    def __init__(self) -> None:
        self._evidence: Dict[str, Any] = {}
        self._current: Optional[str] = None  # artifact_id of latest evidence

    def record_evidence(self, evidence: object) -> str:
        self._evidence[evidence.artifact_id] = evidence
        self._current = evidence.artifact_id
        return evidence.artifact_id

    def get_evidence(self, artifact_id: str):
        return self._evidence.get(artifact_id)

    def get_current_evidence_id(self) -> Optional[str]:
        return self._current

    def get_current_value(self) -> Optional[str]:
        if self._current is None:
            return None
        return self._evidence[self._current].measured_runtime_version

    def get_prior_evidence_id(self) -> Optional[str]:
        """Return the evidence id immediately before the current one.

        Used by the trigger observer to compute prior_value_digest.
        """
        if self._current is None or len(self._evidence) < 2:
            return None
        ids = list(self._evidence.keys())
        # The PoC has at most two evidence records in the base path
        # (initial v1, post-mutation v2). The "prior" is whichever is
        # not the current one.
        for aid in ids:
            if aid != self._current:
                return aid
        return None

    def history(self):
        return list(self._evidence.values())


# ---------------------------------------------------------------------------
# Nonce registry (frozen §12A.8)
# ---------------------------------------------------------------------------


class NonceRegistry:
    """Tracks capability nonces to prevent replay (frozen §12A.8)."""

    def __init__(self) -> None:
        self._states: Dict[str, str] = {}  # nonce -> RESERVED|CONSUMED

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
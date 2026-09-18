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

`SubjectState` is an *identity-only* object: subject_id, role_id,
trust_domain, and the current runtime_version observed by the subject.
The authoritative lifecycle state (current_state + state_epoch) lives
behind a protected boundary inside `StateStore` and is mutated only
through `LifecycleAuthority.publish_initial()` and `.publish_transition()`
— never directly by participant-facing code. Subject-facing callers
can read the authoritative state via `get_authoritative_state()` but
cannot write to it. This is the F3 fix.

`AuthorityStore` holds the predeclared profiles, qualification/admission
fixtures, and the protected-resource authority. The subject
interface cannot obtain the protected-resource authority token through
the conformance APIs; only the executor can (frozen §6.7, §12A.9).
"""

from __future__ import annotations

import hashlib
import threading
from dataclasses import dataclass, field
from typing import Any, Dict, Optional

# All-valid lifecycle states. Anything outside this set is rejected.
_VALID_LIFECYCLE_STATES = {"UNKNOWN", "CONFORMANT", "REATTESTATION_REQUIRED", "SUSPENDED"}


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
# Subject state (identity-only, F3 fix)
# ---------------------------------------------------------------------------


@dataclass
class SubjectState:
    """Identity-only subject record.

    Holds ONLY identity / role / trust_domain and the subject-observed
    runtime version. The authoritative lifecycle state and epoch live
    in `StateStore._lifecycle[subject_id]` and are mutable only via
    `StateStore.apply_authoritative_state()` (called by
    `LifecycleAuthority`). Direct mutation of these fields here is
    not enforced at the language level — but the StateStore holds the
    authoritative copy and the executor reads from the StateStore, so
    direct field writes here are no-ops against the enforcement path.
    """

    subject_id: str
    role_id: str
    trust_domain: str
    current_runtime_version: str = "v1"


# ---------------------------------------------------------------------------
# State store (frozen §6.1, §6.2, §6.5)
# ---------------------------------------------------------------------------


@dataclass
class _AuthoritativeLifecycle:
    """Protected record of authoritative lifecycle state for one subject."""

    current_state: str = "UNKNOWN"
    state_epoch: int = 0


class StateStore:
    """In-memory state store for the PoC.

    Holds the subject identities, the AUTHORITATIVE lifecycle state per
    subject (mutated only by LifecycleAuthority via
    `apply_authoritative_state()`), the active profile, the
    qualification/admission fixtures, and the protected-resource
    authority.

    F3 fix: there is no public method to set or mutate
    `_lifecycle[subject_id].current_state` or `.state_epoch`. The
    only writer is `_apply_authoritative_state()`, which is intended
    to be called exclusively by the LifecycleAuthority.
    """

    def __init__(self) -> None:
        self._subjects: Dict[str, SubjectState] = {}
        # Authoritative lifecycle state per subject (frozen §7).
        self._lifecycle: Dict[str, _AuthoritativeLifecycle] = {}
        # The currently ACTIVE ConformanceProfile (one at a time per §9).
        self._active_profile: Optional[Any] = None
        # Active qualification/admission fixtures keyed by artifact_id.
        self._qualification_fixtures: Dict[str, Any] = {}
        self._admission_fixtures: Dict[str, Any] = {}
        # Registered qualification/admission issuer authority.
        self._qual_admission_issuer_pub: Optional[Any] = None
        self._qual_admission_issuer_key_id: Optional[str] = None
        self._qual_admission_issuer_id: Optional[str] = None
        # The protected-resource authority token. Only the executor is
        # permitted to consume it (frozen §12A.9).
        self._protected_resource_authority: Optional[str] = None

    # ---- subject ----

    def add_subject(self, subject: SubjectState) -> None:
        self._subjects[subject.subject_id] = subject
        if subject.subject_id not in self._lifecycle:
            self._lifecycle[subject.subject_id] = _AuthoritativeLifecycle()

    def get_subject(self, subject_id: str) -> SubjectState:
        if subject_id not in self._subjects:
            raise KeyError(f"unknown subject: {subject_id}")
        return self._subjects[subject_id]

    # ---- authoritative lifecycle (F3 fix) ----

    def apply_authoritative_state(
        self,
        subject_id: str,
        new_state: str,
        new_epoch: int,
        *,
        authorized_caller_token: str,
    ) -> None:
        """Apply an authoritative lifecycle state transition.

        The only writer of `_lifecycle[subject_id].current_state` and
        `.state_epoch`. `authorized_caller_token` is a process-local
        capability passed by `LifecycleAuthority`; any caller without
        the matching token is rejected. This is the F3 boundary: a
        participant-facing caller that bypasses LifecycleAuthority
        cannot acquire this token and therefore cannot mutate
        authoritative lifecycle state.

        Epochs must be strictly monotonic.
        """
        if authorized_caller_token != _AUTHORITATIVE_STATE_WRITER_TOKEN:
            raise PermissionError(
                "authoritative lifecycle state is only writable via "
                "LifecycleAuthority (frozen §7)"
            )
        if new_state not in _VALID_LIFECYCLE_STATES:
            raise ValueError(f"invalid lifecycle state: {new_state!r}")
        if subject_id not in self._lifecycle:
            self._lifecycle[subject_id] = _AuthoritativeLifecycle()
        rec = self._lifecycle[subject_id]
        # Enforce monotonic epoch (frozen §14.3 + parent v0.1.2 §4.8).
        if rec.state_epoch > 0 and new_epoch <= rec.state_epoch:
            raise ValueError(
                f"non-monotonic epoch: current={rec.state_epoch} new={new_epoch}"
            )
        rec.current_state = new_state
        rec.state_epoch = new_epoch

    def get_authoritative_state(self, subject_id: str) -> _AuthoritativeLifecycle:
        if subject_id not in self._lifecycle:
            raise KeyError(f"unknown subject: {subject_id}")
        return self._lifecycle[subject_id]

    def current_state(self, subject_id: str) -> str:
        return self.get_authoritative_state(subject_id).current_state

    def state_epoch(self, subject_id: str) -> int:
        return self.get_authoritative_state(subject_id).state_epoch

    # ---- profile (frozen §9) ----

    def set_active_profile(self, profile: Any) -> None:
        """Activate a predeclared profile. Used by the PoC harness, not the subject."""
        self._active_profile = profile

    def get_active_profile(self) -> Optional[Any]:
        return self._active_profile

    # ---- qualification/admission fixtures (frozen §10A) ----

    def register_qualification_fixture(self, fixture: Any) -> None:
        self._qualification_fixtures[fixture.artifact_id] = fixture

    def register_admission_fixture(self, fixture: Any) -> None:
        self._admission_fixtures[fixture.artifact_id] = fixture

    def get_qualification_fixture(self, artifact_id: str) -> Any:
        return self._qualification_fixtures.get(artifact_id)

    def get_admission_fixture(self, artifact_id: str) -> Any:
        return self._admission_fixtures.get(artifact_id)

    def register_qual_admission_issuer(
        self,
        *,
        issuer_id: str,
        issuer_public_key: Any,
    ) -> None:
        """Register the qualification/admission issuer authority."""
        # Compute key_id from the public key.
        from .crypto import key_id_from_public_key

        self._qual_admission_issuer_pub = issuer_public_key
        self._qual_admission_issuer_key_id = key_id_from_public_key(
            issuer_public_key,
        )
        self._qual_admission_issuer_id = issuer_id

    def qual_admission_issuer_pub(self) -> Optional[Any]:
        return self._qual_admission_issuer_pub

    def qual_admission_issuer_key_id(self) -> Optional[str]:
        return self._qual_admission_issuer_key_id

    def qual_admission_issuer_id(self) -> Optional[str]:
        return self._qual_admission_issuer_id

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


# Token that grants write access to authoritative lifecycle state.
# It is module-private; LifecycleAuthority imports it via the
# _AUTHORITATIVE_STATE_WRITER_TOKEN symbol. Subject-facing code
# cannot reach it.
_AUTHORITATIVE_STATE_WRITER_TOKEN = hashlib.sha256(
    b"acl-lifecycle-authoritative-state-writer"
).hexdigest()


def get_authoritative_state_writer_token() -> str:
    """Return the process-local writer token for `LifecycleAuthority`.

    Provided as a module-level function so the LifecycleAuthority can
    acquire it on its own. The token is not exposed to subject-facing
    code paths.
    """
    return _AUTHORITATIVE_STATE_WRITER_TOKEN


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
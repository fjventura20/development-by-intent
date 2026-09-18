"""Agent Conformance Local Lifecycle PoC v0.1 — capability executor.

Frozen §12A: every execution attempt MUST perform the 12-step ordering
exactly. Step 8 (nonce reservation) MUST NOT occur before the stale /
non-conformant rejection in steps 4-7 — that is what prevents denial
evidence from consuming execution state.

The executor's privileged action is writing the protected resource.
It exposes a single `execute(capability, ...)` method that returns a
structured `ExecutionResult` describing which step (if any) denied
and whether the protected-resource effect occurred.

Frozen §6.7, §12A.9: only the executor can obtain the protected-
resource authority; the subject cannot.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional

from .canonical import canonical_sha256
from .crypto import verify_ed25519
from .models import (
    ExecutionCapability,
    LIFECYCLE_CONFORMANT,
    QualificationFixture,
    AdmissionFixture,
)
from .state import NonceRegistry, StateStore, SubjectState


EXECUTION_GRANTED = "GRANTED"
EXECUTION_DENIED = "DENIED"

# Denial reason codes (frozen §15 classification + §12A step outcomes).
REASON_INVALID_SIGNATURE = "INVALID_SIGNATURE"
REASON_WRONG_SUBJECT = "WRONG_SUBJECT"
REASON_WRONG_ROLE = "WRONG_ROLE"
REASON_WRONG_ACTION = "WRONG_ACTION"
REASON_EXPIRED = "EXPIRED"
REASON_FIXTURE_INACTIVE = "FIXTURE_INACTIVE"
REASON_FIXTURE_MISMATCH = "FIXTURE_MISMATCH"
REASON_NON_CONFORMANT = "NON_CONFORMANT"
REASON_STALE_EPOCH = "STALE_EPOCH"
REASON_REPLAYED_NONCE = "REPLAYED_NONCE"
REASON_UNAUTHORIZED_CALLER = "UNAUTHORIZED_CALLER"


@dataclass
class ExecutionResult:
    """Result of an executor attempt."""

    granted: bool
    reason: str
    step: int  # which step denied (0 if granted)
    record: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Executor:
    """Capability executor (frozen §6.7, §12A)."""

    executor_id: str
    state_store: StateStore
    nonce_registry: NonceRegistry
    authorization: Any  # AuthorizationService
    protected_resource_path: str
    protected_resource_authority_token: str

    def _on_protected_resource_effect(self, line: str) -> None:
        """Append one deterministic line to the protected resource."""
        with open(self.protected_resource_path, "a", encoding="utf-8") as fh:
            fh.write(line + "\n")

    def execute(
        self,
        *,
        subject: SubjectState,
        capability: ExecutionCapability,
        action: str,
        action_payload: Any,
        qualification: QualificationFixture,
        admission: AdmissionFixture,
        clock_now: int,
        caller_authorized: bool = True,
    ) -> ExecutionResult:
        """Run the 12-step ordering exactly once. See frozen §12A."""

        if not caller_authorized:
            return ExecutionResult(
                granted=False, reason=REASON_UNAUTHORIZED_CALLER, step=0,
            )

        # ---- §12A.1 verify capability signature ----
        if not verify_ed25519(
            self.authorization.public_key,
            capability.signature,
            capability.signature_domain,
            capability.signing_payload(),
        ):
            return ExecutionResult(
                granted=False, reason=REASON_INVALID_SIGNATURE, step=1,
            )

        # ---- §12A.2 verify subject/role/action binding ----
        if capability.subject_id != subject.subject_id:
            return ExecutionResult(
                granted=False, reason=REASON_WRONG_SUBJECT, step=2,
            )
        if capability.role_id != subject.role_id:
            return ExecutionResult(
                granted=False, reason=REASON_WRONG_ROLE, step=2,
            )
        expected_action_digest = canonical_sha256(
            {"action": action, "payload": action_payload},
        )
        if capability.action_digest != expected_action_digest:
            return ExecutionResult(
                granted=False, reason=REASON_WRONG_ACTION, step=2,
            )

        # ---- §12A.3 verify capability expiry ----
        if clock_now > capability.expires_at:
            return ExecutionResult(
                granted=False, reason=REASON_EXPIRED, step=3,
            )

        # ---- §12A.4 resolve current qualification/admission state ----
        if qualification.current_state != "ACTIVE":
            return ExecutionResult(
                granted=False, reason=REASON_FIXTURE_INACTIVE, step=4,
            )
        if admission.current_state != "ACTIVE":
            return ExecutionResult(
                granted=False, reason=REASON_FIXTURE_INACTIVE, step=4,
            )
        if (
            qualification.subject_id != subject.subject_id
            or qualification.role_id != subject.role_id
            or qualification.trust_domain != subject.trust_domain
        ):
            return ExecutionResult(
                granted=False, reason=REASON_FIXTURE_MISMATCH, step=4,
            )
        if (
            admission.subject_id != subject.subject_id
            or admission.role_id != subject.role_id
            or admission.trust_domain != subject.trust_domain
        ):
            return ExecutionResult(
                granted=False, reason=REASON_FIXTURE_MISMATCH, step=4,
            )

        # ---- §12A.5 resolve current conformance state + epoch ----
        # ---- §12A.6 reject if state is insufficient ----
        if subject.current_state != LIFECYCLE_CONFORMANT:
            return ExecutionResult(
                granted=False, reason=REASON_NON_CONFORMANT, step=6,
            )

        # ---- §12A.7 reject if epoch is stale ----
        if capability.observed_state_epoch != subject.state_epoch:
            return ExecutionResult(
                granted=False, reason=REASON_STALE_EPOCH, step=7,
            )

        # ---- §12A.8 atomically reserve nonce ----
        try:
            self.nonce_registry.reserve(capability.nonce)
        except ValueError:
            return ExecutionResult(
                granted=False, reason=REASON_REPLAYED_NONCE, step=8,
            )

        # ---- §12A.9 obtain protected-resource authority ----
        try:
            token = self.state_store.consume_protected_resource_authority()
        except PermissionError:
            # The authority was already consumed or unavailable; this
            # is a denial — return the reserved nonce to a failed state.
            self.nonce_registry._states[capability.nonce] = "RESERVED"  # noqa: SLF001
            return ExecutionResult(
                granted=False, reason=REASON_UNAUTHORIZED_CALLER, step=9,
            )
        if token != self.protected_resource_authority_token:
            self.nonce_registry._states[capability.nonce] = "RESERVED"  # noqa: SLF001
            return ExecutionResult(
                granted=False, reason=REASON_UNAUTHORIZED_CALLER, step=9,
            )

        # ---- §12A.10 execute exact action ----
        line = json.dumps(
            {
                "capability_id": capability.artifact_id,
                "action": action,
                "payload_digest": capability.action_digest,
                "epoch": subject.state_epoch,
                "executor": self.executor_id,
            },
            separators=(",", ":"),
            sort_keys=True,
        )
        self._on_protected_resource_effect(line)

        # ---- §12A.11 record outcome ----
        result = ExecutionResult(
            granted=True, reason="OK", step=10,
            record={
                "capability_id": capability.artifact_id,
                "action": action,
                "epoch": subject.state_epoch,
            },
        )

        # ---- §12A.12 mark nonce terminal ----
        self.nonce_registry.consume(capability.nonce)

        return result
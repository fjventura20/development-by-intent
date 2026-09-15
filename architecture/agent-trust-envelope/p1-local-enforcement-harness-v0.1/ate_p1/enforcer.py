from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, asdict
from typing import Callable

from .audit import append_event
from .resource import ProtectedResource
from .state import EnforcementState


class EnforcementDenied(PermissionError):
    pass


@dataclass(frozen=True)
class Authorization:
    envelope_id: str
    subject_id: str
    nonce: str
    operation: str
    target: str
    value: str

    def digest(self) -> str:
        payload = json.dumps(asdict(self), sort_keys=True, separators=(",", ":")).encode("utf-8")
        return hashlib.sha256(payload).hexdigest()


class LocalEnforcer:
    def __init__(self, state: EnforcementState, resource: ProtectedResource, executor_credential: str):
        self.state = state
        self.resource = resource
        self.__executor_credential = executor_credential

    def _verify(self, auth: Authorization, expected_digest: str) -> None:
        if auth.digest() != expected_digest:
            raise EnforcementDenied("EXECUTOR_REVERIFICATION_FAILED")
        if auth.operation != "write" or auth.target != "protected-resource":
            raise EnforcementDenied("SCOPE_DENIED")
        if self.state.is_revoked(auth.subject_id):
            raise EnforcementDenied("SUBJECT_REVOKED")

    def execute(
        self,
        auth: Authorization,
        *,
        before_reverify: Callable[[], None] | None = None,
    ) -> str:
        admission_digest = auth.digest()
        self._verify(auth, admission_digest)
        append_event(self.state, "ADMISSION_OK", auth.envelope_id, {"subject_id": auth.subject_id})

        if not self.state.consume_nonce(auth.nonce, auth.envelope_id):
            append_event(self.state, "REPLAY_DENIED", auth.envelope_id, {"nonce": auth.nonce})
            raise EnforcementDenied("NONCE_REPLAY")

        if before_reverify:
            before_reverify()

        # Re-check immediately before the protected operation.
        self._verify(auth, admission_digest)
        self.resource.write(self.__executor_credential, auth.value)
        append_event(self.state, "EXECUTION_OK", auth.envelope_id, {"nonce": auth.nonce})
        return "EXECUTION_OK"

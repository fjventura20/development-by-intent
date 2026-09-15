from __future__ import annotations

import hmac


class ResourceDenied(PermissionError):
    pass


class ProtectedResource:
    """A local protected resource that accepts only the executor-held capability."""

    def __init__(self, executor_capability: str):
        self._executor_capability = executor_capability
        self._value = "INITIAL"

    def write(self, credential: str, value: str) -> None:
        if not hmac.compare_digest(credential, self._executor_capability):
            raise ResourceDenied("DIRECT_RESOURCE_BYPASS_DENIED")
        self._value = value

    def read_for_test(self) -> str:
        return self._value

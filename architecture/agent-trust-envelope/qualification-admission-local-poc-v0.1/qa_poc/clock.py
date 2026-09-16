"""ATE Qualification & Admission Local PoC v0.1 — TestClock.

Per design §20: all time validation uses an injected TestClock during
tests; no scored test uses `sleep()`. This module exposes a tiny
clock interface and a fixed-clock fixture used by tests + dry runs.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class Clock:
    """A pure-functional clock value (no I/O, no time.time()).

    The TestClock is constructed with a fixed starting instant and
    advanced by returning a new Clock object. All artifact fields that
    carry time (`issued_at_unix_ms`, `expires_at_unix_ms`, etc.) are
    derived from the clock at issue-time.
    """

    now_unix_ms: int

    def advance_ms(self, delta_ms: int) -> "Clock":
        return Clock(now_unix_ms=self.now_unix_ms + delta_ms)

    def to_dict(self) -> dict:
        return {"now_unix_ms": self.now_unix_ms}


def unix_ms_from_seconds(s: float) -> int:
    return int(s * 1000)

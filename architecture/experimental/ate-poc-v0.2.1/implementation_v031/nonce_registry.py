"""ATE v0.3.1 nonce state machine (Refinement A).

States:
  NONCE_UNKNOWN        - the nonce was never registered (presented but absent)
  NONCE_UNSEEN         - registered, never consumed
  NONSE_AUTHORIZED     - a TRUST_GRANTED decision has been issued but the
                         action has not yet executed
  NONCE_CONSUMED       - a governed action has executed under this nonce

Refinement A requires that:
  - replay against NONCE_CONSUMED is distinguishable in evidence
    from presentation of a nonce that was never valid (NONCE_UNKNOWN)
  - this module does NOT evaluate gates or sign decisions;
    trust_decide() is pure and non-mutating
"""
from enum import Enum
from typing import Dict, Optional, Tuple


class NonceState(str, Enum):
    UNKNOWN = "NONCE_UNKNOWN"
    UNSEEN = "NONCE_UNSEEN"
    AUTHORIZED = "NONSE_AUTHORIZED"
    CONSUMED = "NONCE_CONSUMED"


class NonceRegistry:
    """In-process nonce state store.

    State machine:
      register(nonce)       -> UNSEEN
      mark_authorized(nonce) -> AUTHORIZED (idempotent)
      consume(nonce)        -> CONSUMED (atomic transition; only from AUTHORIZED)
      lookup(nonce)         -> NONCE_UNSEEN | NONCE_AUTHORIZED | NONCE_CONSUMED
                              | NONCE_UNKNOWN

    trust_decide() calls lookup() (read-only); only the governed-action
    executor mutates state.
    """

    def __init__(self) -> None:
        self._states: Dict[str, NonceState] = {}

    def register(self, nonce: str) -> None:
        # Register a new nonce. If already known, refuse silently for idempotence.
        if nonce not in self._states:
            self._states[nonce] = NonceState.UNSEEN

    def lookup(self, nonce: str) -> NonceState:
        return self._states.get(nonce, NonceState.UNKNOWN)

    def mark_authorized(self, nonce: str) -> None:
        # Transition UNSEEN -> AUTHORIZED. Used by the executor after a valid
        # TRUST_GRANTED decision is verified, BEFORE executing the action.
        state = self.lookup(nonce)
        if state == NonceState.UNSEEN:
            self._states[nonce] = NonceState.AUTHORIZED
        # else: caller has violated ordering; no-op (fail-closed elsewhere).

    def consume(self, nonce: str) -> None:
        # Atomic transition AUTHORIZED -> CONSUMED. Called by executor AFTER
        # action execution boundary.
        state = self.lookup(nonce)
        if state == NonceState.AUTHORIZED:
            self._states[nonce] = NonceState.CONSUMED

    def snapshot(self) -> Dict[str, str]:
        return {k: v.value for k, v in self._states.items()}

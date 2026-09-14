"""NonceRegistry v0.2.1 — deterministic local fixture.

Frozen state machine (per v0.2.1 §2):
  UNSEEN -> AUTHORIZED/CLAIMED -> CONSUMED

The registry is a deterministic Python dict. Atomicity is provided by
Python's GIL + single-threaded execution in the test runner. This is
explicitly a fixture: NOT distributed atomicity, NOT production
replay resistance.
"""
import threading


STATE_UNSEEN = "UNSEEN"
STATE_AUTHORIZED = "AUTHORIZED"
STATE_CONSUMED = "CONSUMED"


class NonceRegistry:
    def __init__(self):
        self._lock = threading.Lock()
        self._registry = {}  # nonce -> {state, first_authorize_decision_id, first_authorize_at_utc}

    def get_state(self, nonce):
        """Return the current state of nonce, or UNSEEN if not present."""
        with self._lock:
            entry = self._registry.get(nonce)
            if entry is None:
                return STATE_UNSEEN, None
            return entry["state"], entry

    def claim(self, nonce, *, decision_id, at_utc):
        """Atomically transition UNSEEN -> AUTHORIZED.

        Returns (new_state, details).
        Possible outcomes:
          - ("AUTHORIZED", {decision_id, at_utc}): success
          - ("CONSUMED", existing_entry): failure, nonce was consumed
          - ("AUTHORIZED", existing_entry): failure, nonce is currently authorized (concurrent)
          - ("CLAIM_FAILED", ...): failure, race condition
        """
        with self._lock:
            entry = self._registry.get(nonce)
            if entry is None:
                self._registry[nonce] = {
                    "state": STATE_AUTHORIZED,
                    "first_authorize_decision_id": decision_id,
                    "first_authorize_at_utc": at_utc,
                }
                return STATE_AUTHORIZED, {
                    "transition": "UNSEEN->AUTHORIZED",
                    "decision_id": decision_id,
                    "at_utc": at_utc,
                }
            if entry["state"] == STATE_AUTHORIZED:
                return "CLAIM_FAILED", entry
            if entry["state"] == STATE_CONSUMED:
                return STATE_CONSUMED, entry
            # Defensive: should not reach here
            return "UNKNOWN_STATE", entry

    def consume(self, nonce, *, decision_id, at_utc):
        """Atomically transition AUTHORIZED -> CONSUMED.

        Returns (new_state, details).
        """
        with self._lock:
            entry = self._registry.get(nonce)
            if entry is None:
                # No prior claim; this is an error in normal flow.
                return "CONSUME_WITHOUT_CLAIM", None
            if entry["state"] != STATE_AUTHORIZED:
                return entry["state"], entry
            entry["state"] = STATE_CONSUMED
            entry["consumed_at_utc"] = at_utc
            entry["consumed_by_decision_id"] = decision_id
            return STATE_CONSUMED, entry

    def reset(self):
        """Reset the registry (used between test runs)."""
        with self._lock:
            self._registry = {}

    def snapshot(self):
        """Return a deep copy of the registry state for evidence."""
        with self._lock:
            return {k: dict(v) for k, v in self._registry.items()}

"""Agent Conformance Local Lifecycle PoC v0.1 — trigger observer.

Frozen §13: the trigger observer independently compares authoritative
runtime state against the last known material state. The measured
state is distinct from any subject-requested state and the
subject-facing interface cannot rewrite observer history.

A `TriggerObserver` exposes:
  - observe_change(): when the measured runtime version differs from
    the previous recorded version, emit a signed T4 trigger.
  - submit(): the privileged write path used by the harness after a
    real mutation. It updates the observer's authoritative store
    using the same observer key that signs triggers.

The observer key is local to the observer authority; the trigger
record carries the observer signature over canonical signing bytes.
Forgery tests (NS-03) substitute the signature with a key that does
not match the observer's authority; the verifier rejects it.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional

from .canonical import canonical_sha256
from .crypto import (
    Ed25519PrivateKey,
    Ed25519PublicKey,
    sign_ed25519,
    verify_ed25519,
    key_id_from_public_key,
)
from .models import TriggerObservation
from .state import LogicalClock, RuntimeObserverStore


@dataclass
class TriggerObserver:
    """Independent runtime-change trigger authority."""

    observer_id: str
    private_key: Ed25519PrivateKey
    public_key: Ed25519PublicKey
    store: RuntimeObserverStore
    clock: LogicalClock

    def __post_init__(self) -> None:
        self.key_id = key_id_from_public_key(self.public_key)

    # ---- privileged write path (used by harness, NOT by subject) ----

    def submit_measured_runtime(self, value: str, artifact_id: str) -> str:
        """Record a new authoritative runtime measurement.

        This is the observer's authoritative write path. The harness
        invokes it after a real mutation; the subject-facing
        conformance APIs cannot call it.
        """
        from .models import RuntimeEvidence

        ev = RuntimeEvidence(
            artifact_id=artifact_id,
            subject_id="agent-001",
            trust_domain="local-poc",
            measured_runtime_version=value,
            observer_id=self.observer_id,
            logical_ts=self.clock.advance(),
            event_sequence=self.clock.now(),
            signature_domain="ate.conformance.runtime_evidence.v1",
        )
        # Sign the runtime evidence with the observer's key (same
        # authority that signs triggers — frozen §13).
        ev.signature = sign_ed25519(
            self.private_key, ev.signature_domain, ev.signing_payload(),
        )
        return self.store.record_evidence(ev)

    # ---- public read path ----

    def current_value(self) -> Optional[str]:
        return self.store.get_current_value()

    def prior_value(self) -> Optional[str]:
        prior_id = self.store.get_prior_evidence_id()
        if prior_id is None:
            return None
        ev = self.store.get_evidence(prior_id)
        if ev is None:
            return None
        return ev.measured_runtime_version

    # ---- trigger emission ----

    def observe_change(self, subject_id: str, trust_domain: str) -> Optional[TriggerObservation]:
        """Emit a signed trigger observation iff the measured value changed.

        Returns None when there is no material change.
        """
        cur = self.store.get_current_evidence_id()
        prior = self.store.get_prior_evidence_id()
        if cur is None or prior is None:
            return None
        cur_ev = self.store.get_evidence(cur)
        prior_ev = self.store.get_evidence(prior)
        if cur_ev is None or prior_ev is None:
            return None
        if prior_ev.measured_runtime_version == cur_ev.measured_runtime_version:
            return None

        trigger = TriggerObservation(
            artifact_id=f"trigger-{cur_ev.artifact_id}",
            trigger_class="T4_RUNTIME",
            trigger_type="RUNTIME_VERSION_CHANGED",
            subject_id=subject_id,
            trust_domain=trust_domain,
            prior_value_digest=canonical_sha256({"value": prior_ev.measured_runtime_version}),
            current_value_digest=canonical_sha256({"value": cur_ev.measured_runtime_version}),
            severity="MANDATORY_REATTESTATION",
            prior_evidence_id=prior_ev.artifact_id,
            current_evidence_id=cur_ev.artifact_id,
            logical_ts=self.clock.advance(),
            event_sequence=self.clock.now(),
            signature_domain="ate.conformance.trigger_observation.v1",
        )
        trigger.signature = sign_ed25519(
            self.private_key, trigger.signature_domain, trigger.signing_payload(),
        )
        return trigger

    # ---- forgery detection (frozen §13, NS-03) ----

    def verify(self, trigger: TriggerObservation) -> bool:
        """Return True iff the trigger's signature is by this observer."""
        if trigger.signature_domain != "ate.conformance.trigger_observation.v1":
            return False
        return verify_ed25519(
            self.public_key,
            trigger.signature,
            trigger.signature_domain,
            trigger.signing_payload(),
        )
"""Agent Conformance Local Lifecycle PoC v0.1 — R14 lifecycle authority.

Frozen §14.3, §16, §21 + parent v0.1.2 §4.5:
  - R14 publishes lifecycle state with a monotonic state_epoch.
  - The prior_state/new_state/epoch are all signed and immutable.
  - The subject CANNOT directly mutate lifecycle state or epoch (frozen §7).

The authority exposes only `publish_transition()`, which records an
R14 state decision derived from a valid trigger and a valid R13
recommendation. Direct mutation of state_epoch is not exposed.

Forgery tests (NS-05) substitute the signature with a key that does
not match R14's authority; the verifier rejects it.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Optional

from .crypto import (
    Ed25519PrivateKey,
    Ed25519PublicKey,
    key_id_from_public_key,
    sign_ed25519,
    verify_ed25519,
)
from .models import (
    ALL_LIFECYCLE_STATES,
    LIFECYCLE_CONFORMANT,
    LIFECYCLE_REATTESTATION_REQUIRED,
    LIFECYCLE_SUSPENDED,
    R14State,
)
from .state import LogicalClock, StateStore, SubjectState


@dataclass
class LifecycleAuthority:
    """Lifecycle State Authority (frozen §14.3, parent v0.1.2 §4.5)."""

    authority_id: str
    private_key: Ed25519PrivateKey
    public_key: Ed25519PublicKey
    clock: LogicalClock

    def __post_init__(self) -> None:
        self.key_id = key_id_from_public_key(self.public_key)

    def publish_initial(
        self,
        *,
        subject: SubjectState,
        r13_evaluation: Any,
    ) -> R14State:
        """Publish the first lifecycle state for a subject (epoch = 1)."""
        return self._publish(
            subject=subject,
            prior_state=LIFECYCLE_SUSPENDED,
            new_state=r13_evaluation.recommended_state,
            rationale=f"initial conformance: {r13_evaluation.recommended_state}",
            r13_evaluation=r13_evaluation,
            trigger_observation=None,
        )

    def publish_transition(
        self,
        *,
        subject: SubjectState,
        prior_state: str,
        new_state: str,
        rationale: str,
        r13_evaluation: Any,
        trigger_observation: Optional[Any],
    ) -> R14State:
        """Publish a new lifecycle state decision with monotonic epoch."""
        return self._publish(
            subject=subject,
            prior_state=prior_state,
            new_state=new_state,
            rationale=rationale,
            r13_evaluation=r13_evaluation,
            trigger_observation=trigger_observation,
        )

    def _publish(
        self,
        *,
        subject: SubjectState,
        prior_state: str,
        new_state: str,
        rationale: str,
        r13_evaluation: Any,
        trigger_observation: Optional[Any],
    ) -> R14State:
        if new_state not in ALL_LIFECYCLE_STATES:
            raise ValueError(f"unknown lifecycle state: {new_state}")

        # Epoch is monotonic. The initial publish uses epoch 1; every
        # subsequent publish increments by 1.
        new_epoch = subject.state_epoch + 1

        state = R14State(
            artifact_id=f"r14-{subject.subject_id}-e{new_epoch}",
            subject_id=subject.subject_id,
            role_id=subject.role_id,
            trust_domain=subject.trust_domain,
            prior_state=prior_state,
            new_state=new_state,
            state_epoch=new_epoch,
            rationale=rationale,
            r13_evaluation_id=r13_evaluation.artifact_id
                if r13_evaluation is not None else "",
            trigger_observation_id=trigger_observation.artifact_id
                if trigger_observation is not None else "",
            logical_ts=self.clock.advance(),
            event_sequence=self.clock.now(),
            signature_domain="ate.conformance.r14_state.v1",
        )
        state.signature = sign_ed25519(
            self.private_key, state.signature_domain, state.signing_payload(),
        )
        # Apply to the subject state. This is the ONLY code path that
        # advances the subject's state_epoch (frozen §7).
        subject.current_state = new_state
        subject.state_epoch = new_epoch
        return state

    def verify(self, state: R14State) -> bool:
        """Return True iff the state was signed by this R14 authority."""
        if state.signature_domain != "ate.conformance.r14_state.v1":
            return False
        return verify_ed25519(
            self.public_key,
            state.signature,
            state.signature_domain,
            state.signing_payload(),
        )
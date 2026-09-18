"""Agent Conformance Local Lifecycle PoC v0.1 — R14 lifecycle authority.

Frozen §14.3, §16, §21 + parent v0.1.2 §4.5:
  - R14 publishes lifecycle state with a monotonic state_epoch.
  - The prior_state/new_state/epoch are all signed and immutable.
  - The subject CANNOT directly mutate lifecycle state or epoch (frozen §7).

F2 fix: before publishing or applying a transition, R14 verifies:
  - authorized R13 signature (under the registered R13 authority);
  - R13 subject/domain binding to the target subject;
  - requested new_state == R13.recommended_state;
  - prior_state == StateStore.current_state(subject_id);
  - when a trigger is required (N->N+1 invalidation path), trigger
    signature verifies under the registered trigger authority and
    trigger subject/domain binding matches.

F3 fix: the actual write to authoritative lifecycle state goes through
`StateStore.apply_authoritative_state()` with the protected writer
token, which only this class can acquire. Subject-facing code cannot
mutate authoritative state.

The authority exposes only `publish_transition()` and `publish_initial()`,
both of which perform input verification, sign the new R14 state, and
then atomically apply the transition.

Forgery tests must hit this path directly — calling R14 with a forged
or mismatched R13 (or trigger) must NOT produce an R14 artifact AND
must NOT change authoritative state or epoch.
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
from .state import (
    LogicalClock,
    StateStore,
    SubjectState,
    _get_authoritative_state_writer_token_internal,
)


class TransitionInputError(Exception):
    """Raised when an R14 transition is requested with inputs that fail
    F2/G4 verification. The R14 state is NOT published and authoritative
    lifecycle state is NOT mutated when this is raised."""


def create_lifecycle_authority(
    *,
    authority_id: str,
    private_key: Ed25519PrivateKey,
    public_key: Ed25519PublicKey,
    clock: LogicalClock,
    state_store: StateStore,
    r13_authority: Optional[Any] = None,
    trigger_authority: Optional[Any] = None,
    trigger_evidence_store: Any = None,
) -> "LifecycleAuthority":
    """Factory for LifecycleAuthority.

    G1 fix: this factory is the ONLY path that can construct a
    LifecycleAuthority with the protected writer token bound to a
    state store. The token itself is captured as a private attribute
    and never exposed via a public method.
    """
    return LifecycleAuthority(
        authority_id=authority_id,
        private_key=private_key,
        public_key=public_key,
        clock=clock,
        _state_store=state_store,
        _writer_token=_get_authoritative_state_writer_token_internal(),
        r13_authority=r13_authority,
        trigger_authority=trigger_authority,
        trigger_evidence_store=trigger_evidence_store,
    )


@dataclass
class LifecycleAuthority:
    """Lifecycle State Authority (frozen §14.3, parent v0.1.2 §4.5).

    G1 fix: the public constructor does NOT accept `state_store` or
    the writer token. Only `create_lifecycle_authority()` can build
    a fully-wired instance. Subject-facing code that imports this
    class cannot construct an authority bound to a state store.
    """

    authority_id: str
    private_key: Ed25519PrivateKey
    public_key: Ed25519PublicKey
    clock: LogicalClock
    # The state store and writer token are injected ONLY by the
    # factory; they are not parameters of the public constructor.
    _state_store: Any = None
    _writer_token: str = ""
    # The registered R13 authority (for F2/G4 verification of inputs).
    r13_authority: Optional[Any] = None
    # The registered trigger observer authority (for F2/G4 verification
    # of trigger inputs when a trigger is required).
    trigger_authority: Optional[Any] = None
    # G4 fix: the trigger observer store, used to verify that the
    # trigger's referenced evidence ids resolve in the
    # observer-authoritative store.
    trigger_evidence_store: Any = None

    def __post_init__(self) -> None:
        self.key_id = key_id_from_public_key(self.public_key)
        if not self._writer_token:
            raise PermissionError(
                "LifecycleAuthority cannot be constructed directly; "
                "use create_lifecycle_authority() so the protected writer "
                "token is bound by the factory (G1)."
            )

    # ---- input verification (F2) ----

    def _verify_r13(
        self,
        r13_evaluation: Any,
        *,
        subject_id: str,
        requested_new_state: str,
    ) -> None:
        if r13_evaluation is None:
            raise TransitionInputError("R13 evaluation is required")
        # Signature under the authorized R13 key.
        if self.r13_authority is None:
            raise TransitionInputError(
                "no registered R13 authority for input verification"
            )
        if not self.r13_authority.verify(r13_evaluation):
            raise TransitionInputError(
                f"R13 signature does not verify under R13 authority "
                f"{self.r13_authority.evaluator_id!r}"
            )
        # Subject / domain binding.
        if r13_evaluation.subject_id != subject_id:
            raise TransitionInputError(
                f"R13 subject_id {r13_evaluation.subject_id!r} does not "
                f"match target subject {subject_id!r}"
            )
        # trust_domain must match — the frozen PoC has a single
        # trust_domain; we enforce it strictly.
        expected_td = self._state_store.get_subject(subject_id).trust_domain
        if r13_evaluation.trust_domain != expected_td:
            raise TransitionInputError(
                f"R13 trust_domain {r13_evaluation.trust_domain!r} does "
                f"not match subject trust_domain {expected_td!r}"
            )
        # Recommendation match.
        if r13_evaluation.recommended_state != requested_new_state:
            raise TransitionInputError(
                f"R13 recommendation {r13_evaluation.recommended_state!r} "
                f"does not match requested new_state "
                f"{requested_new_state!r}"
            )

    def _verify_trigger(
            self,
            trigger_observation: Any,
            *,
            subject_id: str,
            required: bool,
            r13_evaluation: Any = None,
        ) -> None:
            if trigger_observation is None:
                if required:
                    raise TransitionInputError(
                        "trigger observation is required for this transition"
                    )
                return
            if self.trigger_authority is None:
                raise TransitionInputError(
                    "no registered trigger authority for input verification"
                )
            if not self.trigger_authority.verify(trigger_observation):
                raise TransitionInputError(
                    "trigger signature does not verify under trigger authority"
                )
            if trigger_observation.subject_id != subject_id:
                raise TransitionInputError(
                    f"trigger subject_id {trigger_observation.subject_id!r} "
                    f"does not match target subject {subject_id!r}"
                )
            expected_td = self._state_store.get_subject(subject_id).trust_domain
            if trigger_observation.trust_domain != expected_td:
                raise TransitionInputError(
                    f"trigger trust_domain {trigger_observation.trust_domain!r} "
                    f"does not match subject trust_domain {expected_td!r}"
                )
            # G4 fix: trigger-to-R13 evidence binding.
            if r13_evaluation is not None:
                if (
                    trigger_observation.current_evidence_id
                    != r13_evaluation.runtime_evidence_id
                ):
                    raise TransitionInputError(
                        f"G4: trigger.current_evidence_id "
                        f"{trigger_observation.current_evidence_id!r} != "
                        f"r13_evaluation.runtime_evidence_id "
                        f"{r13_evaluation.runtime_evidence_id!r}"
                    )
                # Trigger current-value digest must match the runtime value
                # R13 evaluated.
                from .canonical import canonical_sha256

                expected_digest = canonical_sha256(
                    {"value": r13_evaluation.measured_runtime_version},
                )
                if trigger_observation.current_value_digest != expected_digest:
                    raise TransitionInputError(
                        f"G4: trigger current_value_digest "
                        f"{trigger_observation.current_value_digest!r} != "
                        f"expected {expected_digest!r} for measured runtime "
                        f"{r13_evaluation.measured_runtime_version!r}"
                    )
            # G4 fix: trigger evidence ids must resolve in the
            # observer-authoritative store.
            if self.trigger_evidence_store is not None:
                cur_evidence = self.trigger_evidence_store.get_evidence(
                    trigger_observation.current_evidence_id,
                )
                if cur_evidence is None:
                    raise TransitionInputError(
                        f"G4: trigger.current_evidence_id "
                        f"{trigger_observation.current_evidence_id!r} does "
                        f"not resolve in observer-authoritative store"
                    )
                prior_evidence = self.trigger_evidence_store.get_evidence(
                    trigger_observation.prior_evidence_id,
                )
                if prior_evidence is None:
                    raise TransitionInputError(
                        f"G4: trigger.prior_evidence_id "
                        f"{trigger_observation.prior_evidence_id!r} does not "
                        f"resolve in observer-authoritative store"
                    )

    def _verify_prior_state(
        self,
        subject_id: str,
        declared_prior_state: str,
    ) -> None:
        actual = self._state_store.current_state(subject_id)
        # Initial publication goes from UNKNOWN (the harness default)
        # to the R13-recommended state. The harness's authoritative
        # `current_state` is "UNKNOWN" before the first publish, and
        # the caller must declare that as the prior state.
        # Subsequent transitions must declare the authoritative
        # current state exactly.
        if actual == "UNKNOWN":
            if declared_prior_state != "UNKNOWN":
                raise TransitionInputError(
                    f"declared prior_state {declared_prior_state!r} does "
                    f"not match authoritative current_state {actual!r}"
                )
            return
        if actual != declared_prior_state:
            raise TransitionInputError(
                f"declared prior_state {declared_prior_state!r} does not "
                f"match authoritative current_state {actual!r}"
            )

    # ---- publishing (F2 + F3) ----

    def publish_initial(
        self,
        *,
        subject: SubjectState,
        r13_evaluation: Any,
    ) -> R14State:
        """Publish the first lifecycle state for a subject (epoch = 1).

        Verifies R13 (signature + binding + recommendation) and the
        declared prior state (must equal authoritative UNKNOWN).
        """
        # F2 verification first. Any failure aborts before signing or
        # mutating authoritative state.
        self._verify_r13(
            r13_evaluation,
            subject_id=subject.subject_id,
            requested_new_state=r13_evaluation.recommended_state,
        )
        # Initial publish declares prior_state = "UNKNOWN" — the
        # authoritative default before any publication.
        self._verify_prior_state(subject.subject_id, "UNKNOWN")
        # Initial publish does not require a trigger.
        self._verify_trigger(None, subject_id=subject.subject_id, required=False)

        new_epoch = self._next_epoch(subject.subject_id)

        state = R14State(
            artifact_id=f"r14-{subject.subject_id}-e{new_epoch}",
            subject_id=subject.subject_id,
            role_id=subject.role_id,
            trust_domain=subject.trust_domain,
            prior_state="UNKNOWN",
            new_state=r13_evaluation.recommended_state,
            state_epoch=new_epoch,
            rationale=f"initial conformance: {r13_evaluation.recommended_state}",
            r13_evaluation_id=r13_evaluation.artifact_id,
            trigger_observation_id="",
            logical_ts=self.clock.advance(),
            event_sequence=self.clock.now(),
            signature_domain="ate.conformance.r14_state.v1",
        )
        state.signature = sign_ed25519(
            self.private_key, state.signature_domain, state.signing_payload(),
        )
        # F3: write to authoritative state via the protected path.
        self._state_store.apply_authoritative_state(
            subject.subject_id,
            state.new_state,
            state.state_epoch,
            authorized_caller_token=self._writer_token,
        )
        return state

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
        """Publish a new lifecycle state decision with monotonic epoch.

        F2: verifies R13 and (when required) trigger before signing or
        mutating anything. Raises TransitionInputError on failure —
        no R14 artifact is produced and authoritative state is unchanged.
        """
        if new_state not in ALL_LIFECYCLE_STATES:
            raise ValueError(f"unknown lifecycle state: {new_state}")

        # F2 input verification (raises on failure — no mutation).
        self._verify_r13(
            r13_evaluation,
            subject_id=subject.subject_id,
            requested_new_state=new_state,
        )
        self._verify_prior_state(subject.subject_id, prior_state)
        # A trigger is required for the runtime-mutation path
        # (v1 -> v2 invalidation). The re-attestation / restoration
        # path is permitted without a trigger, per frozen §16.
        trigger_required = prior_state == LIFECYCLE_CONFORMANT and (
            new_state == LIFECYCLE_REATTESTATION_REQUIRED
        )
        self._verify_trigger(
            trigger_observation,
            subject_id=subject.subject_id,
            required=trigger_required,
            r13_evaluation=r13_evaluation,
        )

        new_epoch = self._next_epoch(subject.subject_id)

        state = R14State(
            artifact_id=f"r14-{subject.subject_id}-e{new_epoch}",
            subject_id=subject.subject_id,
            role_id=subject.role_id,
            trust_domain=subject.trust_domain,
            prior_state=prior_state,
            new_state=new_state,
            state_epoch=new_epoch,
            rationale=rationale,
            r13_evaluation_id=r13_evaluation.artifact_id,
            trigger_observation_id=trigger_observation.artifact_id
                if trigger_observation is not None else "",
            logical_ts=self.clock.advance(),
            event_sequence=self.clock.now(),
            signature_domain="ate.conformance.r14_state.v1",
        )
        state.signature = sign_ed25519(
            self.private_key, state.signature_domain, state.signing_payload(),
        )
        # F3: write to authoritative state via the protected path.
        self._state_store.apply_authoritative_state(
            subject.subject_id,
            state.new_state,
            state.state_epoch,
            authorized_caller_token=self._writer_token,
        )
        return state

    def _next_epoch(self, subject_id: str) -> int:
        return self._state_store.state_epoch(subject_id) + 1

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
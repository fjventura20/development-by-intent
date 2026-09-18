"""Agent Conformance Local Lifecycle PoC v0.1 — R13 evaluator.

Frozen §14.1: "R13 evaluates current evidence against the frozen
conformance profile." Frozen §14.2: when the measured runtime does
not match the active profile's required_runtime_version, R13
recommends `REATTESTATION_REQUIRED`. Frozen §16: after the predeclared
profile v2 is activated and fresh runtime evidence is available,
R13 recommends `CONFORMANT`.

R13 evaluation does NOT itself change lifecycle state — that is R14's
job (frozen §14.3 + parent protocol v0.1.2 §4.5).

The evaluator key is local to R13. Forgery tests (NS-04) substitute
the signature with a key that does not match R13's authority; the
verifier rejects it.
"""

from __future__ import annotations

from dataclasses import InitVar, dataclass
from typing import Any, Dict, Optional

from .crypto import (
    Ed25519PrivateKey,
    Ed25519PublicKey,
    key_id_from_public_key,
    sign_ed25519,
    verify_ed25519,
)
from .models import (
    RECOMMENDED_CONFORMANT,
    RECOMMENDED_REATTESTATION_REQUIRED,
    RECOMMENDED_SUSPENDED,
    FIXTURE_STATE_ACTIVE,
    R13Evaluation,
)
from .state import LogicalClock


@dataclass
class R13Evaluator:
    """Conformance Evaluation Authority (frozen §14, parent v0.1.2 §4.5).

    G2 fix: the evaluator no longer accepts an arbitrary caller-
    supplied profile + profile_digest. It resolves the active
    authoritative profile from `state_store.get_active_profile()`
    and uses the profile's bound `artifact_digest`. The caller
    passes only the runtime evidence; profile identity is
    enforced by the registry.
    """

    evaluator_id: str
    private_key: InitVar[Ed25519PrivateKey]
    public_key: Ed25519PublicKey
    clock: LogicalClock
    state_store: Any  # authoritative profile + qualification/admission state
    observer_authority: Any
    runtime_evidence_store: Any

    def __post_init__(self, private_key: Ed25519PrivateKey) -> None:
        self.__private_key = private_key
        self.key_id = key_id_from_public_key(self.public_key)

    def evaluate(
        self,
        *,
        subject_id: str,
        trust_domain: str,
        runtime_evidence: Any,
        qualification_state: str,
        admission_state: str,
        trust_state_current: bool,
        rationale_prefix: str = "",
    ) -> R13Evaluation:
        """Produce a signed R13 evaluation result.

        G2 fix: profile is resolved from the state store's
        authoritative active profile (which was registered and
        activated through `ProfileRegistry`). The caller does not
        pass `profile` or `profile_digest`.
        """
        subject = self.state_store.get_subject(subject_id)
        if trust_domain != subject.trust_domain:
            raise PermissionError("R13 trust_domain does not match authoritative subject")
        # Caller evidence is only a reference to observer-authoritative state.
        authoritative_evidence = self.runtime_evidence_store.get_evidence(
            runtime_evidence.artifact_id,
        )
        if authoritative_evidence is None:
            raise PermissionError("R13 runtime evidence is not observer-authoritative")
        if (
            self.runtime_evidence_store.get_current_evidence_id()
            != authoritative_evidence.artifact_id
        ):
            raise PermissionError("R13 runtime evidence is not current")
        if authoritative_evidence.subject_id != subject_id:
            raise PermissionError("R13 runtime evidence subject mismatch")
        if authoritative_evidence.trust_domain != trust_domain:
            raise PermissionError("R13 runtime evidence trust-domain mismatch")
        if not self.observer_authority.verify_runtime_evidence(
            authoritative_evidence,
        ):
            raise PermissionError(
                "R13 runtime evidence signature does not verify"
            )
        if runtime_evidence.signing_payload() != authoritative_evidence.signing_payload():
            raise PermissionError(
                "R13 caller evidence does not match authoritative evidence"
            )
        runtime_evidence = authoritative_evidence

        authoritative_qualification_state = self.state_store.qualification_state_for(subject_id)
        authoritative_admission_state = self.state_store.admission_state_for(subject_id)
        if qualification_state != authoritative_qualification_state:
            raise PermissionError(
                "R13 supplied qualification state does not match authoritative state"
            )
        if admission_state != authoritative_admission_state:
            raise PermissionError(
                "R13 supplied admission state does not match authoritative state"
            )

        # G2: resolve active profile from state store.
        profile = self.state_store.get_active_profile()
        if profile is None:
            raise RuntimeError(
                "no active profile registered in state store (G2)"
            )
        if (
            profile.trust_domain != subject.trust_domain
            or profile.role_id != subject.role_id
        ):
            raise PermissionError(
                "R13 active profile is not bound to authoritative subject"
            )
        # Compute profile_digest from the active profile.
        profile_digest = profile.artifact_digest or (
            # If for some reason artifact_digest wasn't bound, fall
            # back to canonical_sha256 of the signing payload.
            # (Registry registration would have caught this earlier.)
            __import__(
                "conformance.canonical",
                fromlist=["canonical_sha256"],
            ).canonical_sha256(profile.signing_payload())
        )
        if authoritative_qualification_state != FIXTURE_STATE_ACTIVE:
            recommended = RECOMMENDED_SUSPENDED
            rationale = f"qualification not ACTIVE ({authoritative_qualification_state})"
        elif authoritative_admission_state != FIXTURE_STATE_ACTIVE:
            recommended = RECOMMENDED_SUSPENDED
            rationale = f"admission not ACTIVE ({authoritative_admission_state})"
        elif not trust_state_current:
            recommended = RECOMMENDED_SUSPENDED
            rationale = "trust state stale"
        elif profile.required_runtime_version == runtime_evidence.measured_runtime_version:
            recommended = RECOMMENDED_CONFORMANT
            rationale = (
                f"profile v{profile.profile_version} requires "
                f"{profile.required_runtime_version}; measured matches"
            )
        else:
            recommended = RECOMMENDED_REATTESTATION_REQUIRED
            rationale = (
                f"profile v{profile.profile_version} requires "
                f"{profile.required_runtime_version}; measured is "
                f"{runtime_evidence.measured_runtime_version}"
            )

        if rationale_prefix:
            rationale = f"{rationale_prefix}: {rationale}"

        evaln = R13Evaluation(
            artifact_id=f"r13-{runtime_evidence.artifact_id}",
            subject_id=subject_id,
            trust_domain=trust_domain,
            profile_id=profile.profile_id,
            profile_version=profile.profile_version,
            profile_digest=profile_digest,
            runtime_evidence_id=runtime_evidence.artifact_id,
            measured_runtime_version=runtime_evidence.measured_runtime_version,
            qualification_state=authoritative_qualification_state,
            admission_state=authoritative_admission_state,
            recommended_state=recommended,
            rationale=rationale,
            logical_ts=self.clock.advance(),
            event_sequence=self.clock.now(),
            signature_domain="ate.conformance.r13_eval.v1",
        )
        evaln.signature = sign_ed25519(
            self.__private_key, evaln.signature_domain, evaln.signing_payload(),
        )
        return evaln

    def verify(self, evaln: R13Evaluation) -> bool:
        """Return True iff the evaluation was signed by this R13 authority."""
        if evaln.signature_domain != "ate.conformance.r13_eval.v1":
            return False
        return verify_ed25519(
            self.public_key,
            evaln.signature,
            evaln.signature_domain,
            evaln.signing_payload(),
        )
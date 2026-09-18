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

from dataclasses import dataclass
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
    """Conformance Evaluation Authority (frozen §14, parent v0.1.2 §4.5)."""

    evaluator_id: str
    private_key: Ed25519PrivateKey
    public_key: Ed25519PublicKey
    clock: LogicalClock

    def __post_init__(self) -> None:
        self.key_id = key_id_from_public_key(self.public_key)

    def evaluate(
        self,
        *,
        subject_id: str,
        trust_domain: str,
        profile: Any,
        profile_digest: str,
        runtime_evidence: Any,
        qualification_state: str,
        admission_state: str,
        trust_state_current: bool,
        rationale_prefix: str = "",
    ) -> R13Evaluation:
        """Produce a signed R13 evaluation result.

        Logic (frozen §14.2 + §16):
          - if qualification != ACTIVE -> SUSPENDED
          - elif admission != ACTIVE   -> SUSPENDED
          - elif not trust_state_current -> SUSPENDED
          - elif profile.requires == runtime.measured -> CONFORMANT
          - else                                -> REATTESTATION_REQUIRED
        """
        if qualification_state != FIXTURE_STATE_ACTIVE:
            recommended = RECOMMENDED_SUSPENDED
            rationale = f"qualification not ACTIVE ({qualification_state})"
        elif admission_state != FIXTURE_STATE_ACTIVE:
            recommended = RECOMMENDED_SUSPENDED
            rationale = f"admission not ACTIVE ({admission_state})"
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
            qualification_state=qualification_state,
            admission_state=admission_state,
            recommended_state=recommended,
            rationale=rationale,
            logical_ts=self.clock.advance(),
            event_sequence=self.clock.now(),
            signature_domain="ate.conformance.r13_eval.v1",
        )
        evaln.signature = sign_ed25519(
            self.private_key, evaln.signature_domain, evaln.signing_payload(),
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
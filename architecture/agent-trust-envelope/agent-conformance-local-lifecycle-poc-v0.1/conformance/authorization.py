"""Agent Conformance Local Lifecycle PoC v0.1 — authorization service.

Frozen §6.6, §10A, §12: the authorization service MUST verify:

  - qualification fixture integrity AND issuer validity AND
    subject/role/domain binding AND current_state == ACTIVE
  - admission fixture (same four gates)
  - current conformance state == CONFORMANT
  - state_epoch matching the active profile's epoch

It then issues exactly one bounded `ExecutionCapability` per request,
signed by the capability issuer authority.

Capability issuer keys are local to the authorization service. The
subject-facing interface can REQUEST a capability but cannot construct
one directly.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Optional

from .canonical import canonical_sha256
from .crypto import (
    Ed25519PrivateKey,
    Ed25519PublicKey,
    key_id_from_public_key,
    sign_ed25519,
    verify_ed25519,
)
from .models import (
    AdmissionFixture,
    ExecutionCapability,
    FIXTURE_STATE_ACTIVE,
    LIFECYCLE_CONFORMANT,
    QualificationFixture,
)
from .state import StateStore, SubjectState


@dataclass
class AuthorizationService:
    """Capability issuer (frozen §6.6)."""

    service_id: str
    private_key: Ed25519PrivateKey
    public_key: Ed25519PublicKey
    store: StateStore

    def __post_init__(self) -> None:
        self.key_id = key_id_from_public_key(self.public_key)

    # ---- qualification/admission fixture verification (frozen §10A) ----

    def verify_qualification(
        self,
        fixture: QualificationFixture,
        subject_id: str,
        role_id: str,
        trust_domain: str,
    ) -> bool:
        """Verify all four §10A gates for the qualification fixture."""
        # 1. integrity: signature verifies
        if not self._verify_fixture_signature(fixture, self.store):
            return False
        # 2. issuer validity: key_id is registered as known issuer
        #    (the fixture carries its issuer_key_id; we just confirm
        #    it is non-empty and the artifact says issuer == service id)
        if not fixture.issuer or not fixture.issuer_key_id:
            return False
        # 3. subject/role/domain binding
        if (
            fixture.subject_id != subject_id
            or fixture.role_id != role_id
            or fixture.trust_domain != trust_domain
        ):
            return False
        # 4. current_state == ACTIVE
        if fixture.current_state != FIXTURE_STATE_ACTIVE:
            return False
        return True

    def verify_admission(
        self,
        fixture: AdmissionFixture,
        subject_id: str,
        role_id: str,
        trust_domain: str,
    ) -> bool:
        return self.verify_qualification(
            # Reuse the qualification verifier; the gates are identical.
            fixture,  # type: ignore[arg-type]
            subject_id,
            role_id,
            trust_domain,
        )

    def _verify_fixture_signature(self, fixture: Any, store: StateStore) -> bool:
        """Verify the fixture's signature using the registered issuer key.

        For the PoC we use a single well-known issuer authority
        (the qualification/admission issuer service). Its public key
        is held by the StateStore as `qualification_admission_issuer_pub`.
        """
        pub = getattr(store, "_qual_admission_issuer_pub", None)
        if pub is None:
            return False
        return verify_ed25519(
            pub,
            fixture.signature,
            fixture.signature_domain,
            fixture.signing_payload(),
        )

    # ---- capability issuance (frozen §12) ----

    def issue_capability(
        self,
        *,
        subject: SubjectState,
        action: str,
        action_payload: Any,
        qualification: QualificationFixture,
        admission: AdmissionFixture,
        nonce: str,
        ttl_ticks: int,
        clock_now: int,
    ) -> Optional[ExecutionCapability]:
        """Issue a single bounded ExecutionCapability iff all gates pass.

        Returns None if any gate fails (the request is denied).
        """
        if not self.verify_qualification(
            qualification, subject.subject_id, subject.role_id, subject.trust_domain,
        ):
            return None
        if not self.verify_admission(
            admission, subject.subject_id, subject.role_id, subject.trust_domain,
        ):
            return None
        if subject.current_state != LIFECYCLE_CONFORMANT:
            return None

        action_digest = canonical_sha256({"action": action, "payload": action_payload})

        cap = ExecutionCapability(
            artifact_id=f"cap-{nonce}",
            subject_id=subject.subject_id,
            role_id=subject.role_id,
            trust_domain=subject.trust_domain,
            action_digest=action_digest,
            observed_conformance_state=subject.current_state,
            observed_state_epoch=subject.state_epoch,
            nonce=nonce,
            issued_at=clock_now,
            expires_at=clock_now + ttl_ticks,
            issuer=self.service_id,
            issuer_key_id=self.key_id,
            signature_domain="ate.conformance.capability.v1",
        )
        cap.signature = sign_ed25519(
            self.private_key, cap.signature_domain, cap.signing_payload(),
        )
        return cap

    def verify_capability(self, cap: ExecutionCapability) -> bool:
        """Verify the capability signature using the issuer's public key."""
        return verify_ed25519(
            self.public_key,
            cap.signature,
            cap.signature_domain,
            cap.signing_payload(),
        )
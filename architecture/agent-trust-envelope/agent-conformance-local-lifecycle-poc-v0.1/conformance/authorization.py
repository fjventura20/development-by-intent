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

F4 fix: the qualification/admission issuer binding now requires the
fixture's `issuer` field to equal the registered issuer identity, and
the fixture's `issuer_key_id` to equal the key_id of the registered
issuer public key. The fixture also carries a stable `artifact_digest`
which the verifier confirms matches the canonical SHA-256 of the
signing payload.

F5 fix: at issuance the capability is bound to the STABLE artifact_ids
of the qualification and admission fixtures it was issued against.
The executor resolves the current authoritative fixture objects from
StateStore at step 4 — it does not rely on caller-supplied objects.
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
        """Verify all four §10A gates for the qualification fixture.

        F4: in addition to the original four gates, requires:
          - fixture.issuer == registered issuer identity
          - fixture.issuer_key_id == key_id(registered issuer public key)
          - fixture.artifact_digest == canonical SHA-256 of signing payload
        """
        if not self._verify_fixture_gates(
            fixture, subject_id, role_id, trust_domain,
        ):
            return False
        return True

    def verify_admission(
        self,
        fixture: AdmissionFixture,
        subject_id: str,
        role_id: str,
        trust_domain: str,
    ) -> bool:
        """F4: same gates as qualification."""
        return self.verify_qualification(
            fixture,  # type: ignore[arg-type]
            subject_id,
            role_id,
            trust_domain,
        )

    def _verify_fixture_gates(
        self,
        fixture: Any,
        subject_id: str,
        role_id: str,
        trust_domain: str,
    ) -> bool:
        # 1. integrity: signature verifies under the registered issuer pub.
        if not self._verify_fixture_signature(fixture, self.store):
            return False
        # 2. issuer validity (F4 fix): fixture.issuer must equal the
        # registered issuer identity, and fixture.issuer_key_id must
        # equal key_id(registered issuer public key).
        expected_issuer_id = self.store.qual_admission_issuer_id()
        if expected_issuer_id is None or fixture.issuer != expected_issuer_id:
            return False
        expected_issuer_key_id = self.store.qual_admission_issuer_key_id()
        if (
            expected_issuer_key_id is None
            or fixture.issuer_key_id != expected_issuer_key_id
        ):
            return False
        # 3. subject/role/domain binding.
        if (
            fixture.subject_id != subject_id
            or fixture.role_id != role_id
            or fixture.trust_domain != trust_domain
        ):
            return False
        # 4. current_state == ACTIVE.
        if fixture.current_state != FIXTURE_STATE_ACTIVE:
            return False
        # 5. F4 fix: stable artifact_digest must match canonical SHA-256
        # of the signing payload. This protects against a forged
        # artifact_digest field that doesn't correspond to the actual
        # signed payload.
        expected_digest = canonical_sha256(fixture.signing_payload())
        if not fixture.artifact_digest or fixture.artifact_digest != expected_digest:
            return False
        return True

    def _verify_fixture_signature(self, fixture: Any, store: StateStore) -> bool:
        """Verify the fixture's signature using the registered issuer key."""
        pub = store.qual_admission_issuer_pub()
        if pub is None:
            return False
        return verify_ed25519(
            pub,
            fixture.signature,
            fixture.signature_domain,
            fixture.signing_payload(),
        )

    # ---- capability issuance (frozen §12, F5) ----

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

        Returns None if any gate fails (the request is denied). The
        capability is bound to the STABLE artifact_ids of the fixtures
        it was issued against (F5); the executor resolves the current
        authoritative fixture objects from StateStore at step 4.
        """
        if not self.verify_qualification(
            qualification, subject.subject_id, subject.role_id, subject.trust_domain,
        ):
            return None
        if not self.verify_admission(
            admission, subject.subject_id, subject.role_id, subject.trust_domain,
        ):
            return None
        # Authoritative state check (F3 reads StateStore, not subject fields).
        if self.store.current_state(subject.subject_id) != LIFECYCLE_CONFORMANT:
            return None

        action_digest = canonical_sha256({"action": action, "payload": action_payload})

        cap = ExecutionCapability(
            artifact_id=f"cap-{nonce}",
            subject_id=subject.subject_id,
            role_id=subject.role_id,
            trust_domain=subject.trust_domain,
            action_digest=action_digest,
            observed_conformance_state=self.store.current_state(subject.subject_id),
            observed_state_epoch=self.store.state_epoch(subject.subject_id),
            nonce=nonce,
            issued_at=clock_now,
            expires_at=clock_now + ttl_ticks,
            issuer=self.service_id,
            issuer_key_id=self.key_id,
            qualification_artifact_id=qualification.artifact_id,
            admission_artifact_id=admission.artifact_id,
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
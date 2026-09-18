"""Agent Conformance Local Lifecycle PoC v0.1 — frozen profile registry.

H1-H3 correction:
- registration is allowed only before freeze;
- freeze is irreversible;
- StateStore may install exactly one frozen registry;
- activation is by immutable registered (artifact_id, digest), with no token getter;
- registry returns deep copies so callers cannot mutate authoritative profiles.
"""

from __future__ import annotations

import copy
from dataclasses import dataclass, field
from typing import Dict, Optional

from .canonical import canonical_sha256
from .crypto import (
    Ed25519PrivateKey,
    Ed25519PublicKey,
    key_id_from_public_key,
    sign_ed25519,
    verify_ed25519,
)
from .models import ConformanceProfile


@dataclass
class ProfileRegistry:
    """Authoritative predeclared profile registry."""

    signer_key_id: str
    signer_public_key: Ed25519PublicKey
    _registered: Dict[str, ConformanceProfile] = field(default_factory=dict)
    _frozen: bool = False

    @classmethod
    def create(cls, *, signer_public_key: Ed25519PublicKey) -> "ProfileRegistry":
        return cls(
            signer_key_id=key_id_from_public_key(signer_public_key),
            signer_public_key=signer_public_key,
        )

    @property
    def frozen(self) -> bool:
        return self._frozen

    def register(self, profile: ConformanceProfile) -> str:
        """Register one signed profile before freeze."""
        if self._frozen:
            raise PermissionError("profile registry is frozen; registration is closed")
        if profile.artifact_id in self._registered:
            raise ValueError(f"profile already registered: {profile.artifact_id}")
        if not verify_ed25519(
            self.signer_public_key,
            profile.signature,
            profile.signature_domain,
            profile.signing_payload(),
        ):
            raise ValueError("profile signature does not verify under registry signer")
        expected_digest = canonical_sha256(profile.signing_payload())
        if not profile.artifact_digest:
            raise ValueError("profile artifact_digest must be bound before registration")
        if profile.artifact_digest != expected_digest:
            raise ValueError("profile artifact_digest does not match canonical payload")
        self._registered[profile.artifact_id] = copy.deepcopy(profile)
        return profile.artifact_digest

    def freeze(self) -> None:
        if self._frozen:
            return
        if not self._registered:
            raise ValueError("cannot freeze empty profile registry")
        self._frozen = True

    def registered_ids(self) -> list[str]:
        return list(self._registered.keys())

    def get(self, artifact_id: str) -> Optional[ConformanceProfile]:
        profile = self._registered.get(artifact_id)
        return None if profile is None else copy.deepcopy(profile)

    def resolve_frozen(self, artifact_id: str, profile_digest: str) -> ConformanceProfile:
        """Resolve a frozen, registered profile by exact id+digest."""
        if not self._frozen:
            raise PermissionError("profile registry must be frozen before activation")
        profile = self._registered.get(artifact_id)
        if profile is None:
            raise KeyError(f"profile not registered: {artifact_id!r}")
        if profile.artifact_digest != profile_digest:
            raise ValueError("profile digest mismatch")
        if not verify_ed25519(
            self.signer_public_key,
            profile.signature,
            profile.signature_domain,
            profile.signing_payload(),
        ):
            raise ValueError("stored profile signature no longer verifies")
        if canonical_sha256(profile.signing_payload()) != profile.artifact_digest:
            raise ValueError("stored profile digest no longer matches payload")
        return copy.deepcopy(profile)


def create_profile_registry(*, signer_public_key: Ed25519PublicKey) -> ProfileRegistry:
    return ProfileRegistry.create(signer_public_key=signer_public_key)


def sign_conformance_profile(
    profile: ConformanceProfile,
    signer_private_key: Ed25519PrivateKey,
    signer_public_key: Ed25519PublicKey,
) -> ConformanceProfile:
    """Bootstrap-only helper: bind digest, then sign exact payload."""
    del signer_public_key  # retained for call-site clarity
    profile.artifact_digest = canonical_sha256(profile.signing_payload())
    profile.signature = sign_ed25519(
        signer_private_key,
        profile.signature_domain,
        profile.signing_payload(),
    )
    return profile

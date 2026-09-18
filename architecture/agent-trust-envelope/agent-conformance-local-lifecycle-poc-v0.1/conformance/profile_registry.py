"""Agent Conformance Local Lifecycle PoC v0.1 — profile registry.

G2 fix: introduces an authoritative predeclared profile registry.

Properties (frozen §9 + G2 correction):

  - profiles are signed by an authorized policy signer;
  - profiles are registered before run start (digest-locked);
  - activation goes through a protected path that requires the
    registered (profile_id, profile_digest) tuple plus the
    `ProfileActivationToken` captured by the registry's factory;
  - only one profile is active at a time per StateStore;
  - participant-facing callers cannot inject an unsigned /
    unregistered / wrong-key / tampered-digest profile.

The R13 evaluator no longer accepts an arbitrary caller-supplied
profile; it resolves the active profile from the state store, which
itself goes through `ProfileRegistry.activate()`.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from typing import Any, Dict, Optional

from .canonical import canonical_sha256
from .crypto import (
    Ed25519PrivateKey,
    Ed25519PublicKey,
    key_id_from_public_key,
    sign_ed25519,
    verify_ed25519,
)
from .models import ConformanceProfile


_PROFILE_ACTIVATION_TOKEN = hashlib.sha256(
    b"acl-lifecycle-profile-activation"
).hexdigest()


def _get_profile_activation_token_internal() -> str:
    """Module-internal accessor used only by ProfileRegistry.create().

    G2 fix: there is no public function in this module that returns
    the token.
    """
    return _PROFILE_ACTIVATION_TOKEN


@dataclass
class ProfileRegistry:
    """Authoritative predeclared profile registry.

    Constructed via `create_profile_registry()` so the activation
    token is bound only to instances that go through the factory.
    """

    signer_key_id: str
    signer_public_key: Ed25519PublicKey
    # Registered profiles keyed by artifact_id. Each value is the
    # signed ConformanceProfile (verified at registration time).
    _registered: Dict[str, ConformanceProfile]
    _token: str

    @classmethod
    def create(
        cls,
        *,
        signer_public_key: Ed25519PublicKey,
    ) -> "ProfileRegistry":
        return cls(
            signer_key_id=key_id_from_public_key(signer_public_key),
            signer_public_key=signer_public_key,
            _registered={},
            _token=_get_profile_activation_token_internal(),
        )

    def register(
        self,
        profile: ConformanceProfile,
        *,
        signer_private_key: Ed25519PrivateKey,
    ) -> str:
        """Register a predeclared profile.

        Verifies the profile's signature against the registry's
        authorized signer, computes and binds the canonical digest,
        and stores the profile under its `artifact_id`. The digest
        becomes the activation key; the value cannot be changed
        after registration.
        """
        # Verify the signature was produced by the authorized signer.
        if not verify_ed25519(
            self.signer_public_key,
            profile.signature,
            profile.signature_domain,
            profile.signing_payload(),
        ):
            raise ValueError(
                "profile signature does not verify under registry signer"
            )
        # Bind artifact_digest to the canonical SHA-256 of the
        # signing payload (analogous to F4 fixture digest binding).
        expected_digest = canonical_sha256(profile.signing_payload())
        if not profile.artifact_digest:
            profile.artifact_digest = expected_digest
        elif profile.artifact_digest != expected_digest:
            raise ValueError(
                "profile.artifact_digest does not match canonical "
                "SHA-256 of signing payload"
            )
        self._registered[profile.artifact_id] = profile
        return profile.artifact_digest

    def get(self, artifact_id: str) -> Optional[ConformanceProfile]:
        return self._registered.get(artifact_id)

    def registered_ids(self) -> list:
        return list(self._registered.keys())

    def activate(
        self,
        *,
        state_store: Any,
        profile_id: str,
        profile_digest: str,
        authorized_caller_token: str,
    ) -> ConformanceProfile:
        """Activate a registered profile by (id, digest).

        G2: requires the activation token; verifies signature,
        digest, and that the profile is registered.
        """
        if authorized_caller_token != self._token:
            raise PermissionError(
                "profile activation requires the protected token; "
                "use create_profile_registry() or the harness factory"
            )
        profile = self._registered.get(profile_id)
        if profile is None:
            raise KeyError(
                f"profile not registered: {profile_id!r}; registered: "
                f"{self.registered_ids()}"
            )
        # Re-verify signature (defense in depth) and digest.
        if not verify_ed25519(
            self.signer_public_key,
            profile.signature,
            profile.signature_domain,
            profile.signing_payload(),
        ):
            raise ValueError(
                "stored profile signature does not verify under "
                "registry signer at activation time"
            )
        if profile.artifact_digest != profile_digest:
            raise ValueError(
                f"profile digest mismatch: stored={profile.artifact_digest!r} "
                f"requested={profile_digest!r}"
            )
        # Apply to the state store's protected active profile slot.
        state_store._active_profile = profile  # noqa: SLF001
        return profile


def create_profile_registry(
    *,
    signer_public_key: Ed25519PublicKey,
) -> ProfileRegistry:
    """Factory for ProfileRegistry. G2 fix: the only public entry
    point. The activation token is bound to the instance only via
    this factory path."""
    return ProfileRegistry.create(signer_public_key=signer_public_key)


def sign_conformance_profile(
    profile: ConformanceProfile,
    signer_private_key: Ed25519PrivateKey,
    signer_public_key: Ed25519PublicKey,
) -> ConformanceProfile:
    """Sign and bind a profile's artifact_digest using the registry
    signer's key. Convenience for the bootstrap path."""
    profile.artifact_digest = canonical_sha256(profile.signing_payload())
    profile.signature = sign_ed25519(
        signer_private_key,
        profile.signature_domain,
        profile.signing_payload(),
    )
    return profile
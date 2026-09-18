"""Agent Conformance Local Lifecycle PoC v0.1 — Ed25519 crypto.

Frozen-design §24: deterministic cryptographic signing with explicit
domain separation. Ed25519 is used because it is small, well-specified,
and the smallest approved dependency in the repository environment.

Signing bytes (frozen §24):
    UTF-8(artifact_domain) || 0x00 || canonical_json_bytes(payload)

This module owns:
  - Ed25519 keypair generation (used only by fixtures/tests)
  - Ed25519 sign / verify against the canonical signing bytes
  - Strict key-id derivation (SHA-256 of the public-key raw bytes)

Private keys are NEVER produced during any scored test path. They are
fixture-only material loaded from disk by the conformance authority
during setup.
"""

from __future__ import annotations

import hashlib
from typing import Tuple

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric.ed25519 import (
    Ed25519PrivateKey,
    Ed25519PublicKey,
)

from .canonical import CanonicalError, signing_bytes

__all__ = [
    "Ed25519PrivateKey",
    "Ed25519PublicKey",
    "CanonicalError",
    "InvalidSignature",
    "generate_keypair",
    "sign_ed25519",
    "verify_ed25519",
    "key_id_from_public_key",
    "signing_bytes",
]


def generate_keypair() -> Tuple[Ed25519PrivateKey, Ed25519PublicKey]:
    """Generate a deterministic Ed25519 keypair (fixture/test only).

    Note: Ed25519 key generation is non-deterministic by spec; we do
    not attempt to seed it. Keys produced here are used only for
    fixture bootstrapping in tests and are never reused for security-
    relevant operations in any scored test.
    """
    priv = Ed25519PrivateKey.generate()
    pub = priv.public_key()
    return priv, pub


def key_id_from_public_key(pub: Ed25519PublicKey) -> str:
    """Strict key-id derivation: hex SHA-256 of the raw 32-byte public key."""
    raw = pub.public_bytes_raw()
    return hashlib.sha256(raw).hexdigest()


def sign_ed25519(
    priv: Ed25519PrivateKey,
    domain: str,
    payload: dict,
) -> bytes:
    """Sign the canonical signing bytes and return raw Ed25519 signature."""
    return priv.sign(signing_bytes(domain, payload))


def verify_ed25519(
    pub: Ed25519PublicKey,
    signature: bytes,
    domain: str,
    payload: dict,
) -> bool:
    """Verify an Ed25519 signature against the canonical signing bytes.

    Returns True iff the signature is a valid Ed25519 signature over
    the canonical bytes for (domain, payload).
    """
    try:
        pub.verify(signature, signing_bytes(domain, payload))
        return True
    except InvalidSignature:
        return False
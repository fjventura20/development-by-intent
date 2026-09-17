"""ATE Qualification & Admission Local PoC v0.1 — Ed25519 crypto.

Frozen-design §8: "Signature: Ed25519. Signing bytes:
  UTF8(artifact_domain) || 0x00 || canonical_json_bytes".

This module owns:
  - Ed25519 key generation (used only in bootstrap / fixture)
  - Ed25519 sign / verify using the canonical signing bytes
  - PEM load/save for fixture public keys
  - Strict key-id derivation (SHA-256 of the public-key PEM)

Keys are loaded from PEM PKCS8 (private) / SubjectPublicKeyInfo (public).
The PoC never produces keys during scored tests — keys are fixture-only.
"""

from __future__ import annotations

import hashlib
import os
from typing import Tuple

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import (
    Ed25519PrivateKey,
    Ed25519PublicKey,
)

from .canonical import CanonicalError, signing_bytes

# Re-export the canonical primitive so callers have one import.
__all__ = [
    "Ed25519PrivateKey",
    "Ed25519PublicKey",
    "CanonicalError",
    "generate_keypair",
    "sign_ed25519",
    "verify_ed25519",
    "load_ed25519_public_pem",
    "save_ed25519_public_pem",
    "save_ed25519_private_pem",
    "load_ed25519_private_pem",
    "key_id_from_public_pem",
    "signing_bytes",
]


def _to_priv(obj):
    if isinstance(obj, Ed25519PrivateKey):
        return obj
    # Formal-host mode deliberately uses a narrow remote signer proxy.
    # The proxy exposes only .sign(raw_bytes) and never returns private bytes
    # or an Ed25519PrivateKey object to the trusted controller.
    if getattr(obj, "__ate_remote_signer__", False) and callable(getattr(obj, "sign", None)):
        return obj
    raise TypeError("expected Ed25519PrivateKey or ATE remote signer")


def _to_pub(obj) -> Ed25519PublicKey:
    if isinstance(obj, Ed25519PublicKey):
        return obj
    raise TypeError("expected Ed25519PublicKey")


def generate_keypair() -> Tuple[Ed25519PrivateKey, Ed25519PublicKey]:
    """Generate a fresh Ed25519 keypair. Use ONLY for fixture setup."""
    priv = Ed25519PrivateKey.generate()
    return priv, priv.public_key()


def save_ed25519_private_pem(priv: Ed25519PrivateKey, path: str, mode: int = 0o600) -> None:
    pem = priv.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    )
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, mode)
    try:
        os.write(fd, pem)
    finally:
        os.close(fd)
    os.chmod(path, mode)


def load_ed25519_private_pem(path: str) -> Ed25519PrivateKey:
    with open(path, "rb") as f:
        data = f.read()
    key = serialization.load_pem_private_key(data, password=None)
    return _to_priv(key)


def save_ed25519_public_pem(pub: Ed25519PublicKey, path: str, mode: int = 0o644) -> None:
    pem = pub.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, mode)
    try:
        os.write(fd, pem)
    finally:
        os.close(fd)
    os.chmod(path, mode)


def load_ed25519_public_pem(path: str) -> Ed25519PublicKey:
    with open(path, "rb") as f:
        data = f.read()
    key = serialization.load_pem_public_key(data)
    return _to_pub(key)


def key_id_from_public_pem(pem_bytes: bytes) -> str:
    """Stable key-id = SHA-256 hex of the public-key SubjectPublicKeyInfo DER.

    Per design §6 the `key_id` is recorded in the public-key manifest.
    """
    pub = serialization.load_pem_public_key(pem_bytes)
    der = pub.public_bytes(
        encoding=serialization.Encoding.DER,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )
    return hashlib.sha256(der).hexdigest()


def key_id_from_public_key(pub: Ed25519PublicKey) -> str:
    der = pub.public_bytes(
        encoding=serialization.Encoding.DER,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )
    return hashlib.sha256(der).hexdigest()


def sign_ed25519(priv: Ed25519PrivateKey, domain: str, payload_obj) -> bytes:
    """Sign `payload_obj` under artifact-domain `domain`.

    Returns the 64-byte Ed25519 signature. The signing bytes are
    `UTF8(domain) || 0x00 || canonical_json_bytes(payload_obj)`.
    """
    p = _to_priv(priv)
    msg = signing_bytes(domain, payload_obj)
    return p.sign(msg)


def verify_ed25519(
    pub: Ed25519PublicKey, signature: bytes, domain: str, payload_obj
) -> bool:
    """Verify a signature over `payload_obj` under artifact-domain `domain`.

    Returns True on success. Raises InvalidSignature on failure.
    """
    p = _to_pub(pub)
    msg = signing_bytes(domain, payload_obj)
    p.verify(signature, msg)
    return True


__all__ += ["key_id_from_public_key"]

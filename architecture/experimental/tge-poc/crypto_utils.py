"""Ed25519 signing/verification helpers and key encoding.

Uses the `cryptography` library. Signer and verifier share this module.
"""
import base64
from typing import Tuple

from cryptography.hazmat.primitives.asymmetric.ed25519 import (
    Ed25519PrivateKey,
    Ed25519PublicKey,
)
from cryptography.hazmat.primitives import serialization


def generate_keypair() -> Tuple[Ed25519PrivateKey, Ed25519PublicKey]:
    """Generate a fresh Ed25519 keypair."""
    priv = Ed25519PrivateKey.generate()
    pub = priv.public_key()
    return priv, pub


def public_key_bytes(pub: Ed25519PublicKey) -> bytes:
    """Raw 32-byte public key encoding."""
    return pub.public_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PublicFormat.Raw,
    )


def private_key_bytes(priv: Ed25519PrivateKey) -> bytes:
    """Raw 32-byte private key encoding."""
    return priv.private_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PrivateFormat.Raw,
        encryption_algorithm=serialization.NoEncryption(),
    )


def public_key_b64(pub: Ed25519PublicKey) -> str:
    return base64.b64encode(public_key_bytes(pub)).decode('ascii')


def signature_b64(priv: Ed25519PrivateKey, message: bytes) -> str:
    sig = priv.sign(message)
    return base64.b64encode(sig).decode('ascii')


def verify_signature(pub: Ed25519PublicKey, message: bytes, signature_b64_str: str) -> bool:
    try:
        sig = base64.b64decode(signature_b64_str)
        pub.verify(sig, message)
        return True
    except Exception:
        return False


def load_public_key_from_b64(b64_str: str) -> Ed25519PublicKey:
    raw = base64.b64decode(b64_str)
    return Ed25519PublicKey.from_public_bytes(raw)


def load_private_key_from_bytes(raw: bytes) -> Ed25519PrivateKey:
    return Ed25519PrivateKey.from_private_bytes(raw)

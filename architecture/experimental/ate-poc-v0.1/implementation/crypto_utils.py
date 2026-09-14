"""Shared crypto helpers for ATE-PoC v0.1.

Ed25519 sign / verify over canonicalized bytes.
Fixture keys (NOT production keys).
"""
import base64

from cryptography.hazmat.primitives.asymmetric.ed25519 import (
    Ed25519PrivateKey,
    Ed25519PublicKey,
)
from cryptography.hazmat.primitives import serialization


def generate_keypair():
    priv = Ed25519PrivateKey.generate()
    pub = priv.public_key()
    return priv, pub


def public_key_bytes(pub):
    return pub.public_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PublicFormat.Raw,
    )


def public_key_b64(pub):
    return base64.b64encode(public_key_bytes(pub)).decode("ascii")


def load_public_key_from_b64(b64_str):
    raw = base64.b64decode(b64_str)
    return Ed25519PublicKey.from_public_bytes(raw)


def load_private_key_from_raw(raw):
    return Ed25519PrivateKey.from_private_bytes(raw)


def signature_b64(priv, message):
    return base64.b64encode(priv.sign(message)).decode("ascii")


def verify_signature(pub, message, signature_b64_str):
    try:
        sig = base64.b64decode(signature_b64_str)
        pub.verify(sig, message)
        return True
    except Exception:
        return False


def canonicalize_json(obj):
    """Frozen JSON canonicalization for ATE-PoC.

    Per ATE-POC-DESIGN-v0.1 §11 (data structure schemas), the ATE-PoC uses
    RFC 8785-style canonicalization (object keys sorted by UTF-16 code unit
    order, no whitespace, no Unicode normalization). This module reuses the
    same canonicalization profile as the Stage-C v0.2.2 GEL rules.
    """
    import json as _json
    return _json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def short_hash(s):
    """Short hex SHA-256 prefix (16 hex chars) for display."""
    import hashlib
    return hashlib.sha256(s.encode("utf-8") if isinstance(s, str) else s).hexdigest()[:16]

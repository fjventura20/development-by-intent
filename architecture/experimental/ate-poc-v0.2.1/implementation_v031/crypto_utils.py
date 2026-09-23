"""ATE v0.3.1 cryptographic utilities.

Reuses the canonicalization and Ed25519 signing pattern from
ATE v0.2.1 (architecture/experimental/ate-poc-v0.2.1/implementation/crypto_utils_v2.py).

Per v0.3.1 design amendment:
  - RFC 8785 JCS canonicalization (no Unicode normalization)
  - Ed25519 signing via cryptography library
  - fingerprint_obj for canonical fingerprint
"""
import hashlib
import json
import base64
from typing import Any, Dict, List, Tuple

from cryptography.hazmat.primitives.asymmetric.ed25519 import (
    Ed25519PrivateKey,
    Ed25519PublicKey,
)
from cryptography.hazmat.primitives import serialization


def canonicalize_json(obj: Any) -> str:
    """RFC 8785 JCS canonicalization: sort keys, no whitespace, UTF-8.

    No Unicode normalization per TGE v0.2.1 rule (E.1).
    """
    return json.dumps(
        obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    )


def canonical_bytes(obj: Any) -> bytes:
    return canonicalize_json(obj).encode("utf-8")


def fingerprint_obj(obj: Any) -> str:
    """SHA-256 over canonical bytes, returned as hex."""
    return hashlib.sha256(canonical_bytes(obj)).hexdigest()


def fingerprint_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _strip_signature(obj: Any) -> Any:
    """Deep-copy an object removing any *_signature_b64 field."""
    if isinstance(obj, dict):
        return {
            k: _strip_signature(v)
            for k, v in obj.items()
            if not k.endswith("_signature_b64")
        }
    if isinstance(obj, list):
        return [_strip_signature(x) for x in obj]
    return obj


def sign(priv_key: Ed25519PrivateKey, obj: Any) -> str:
    """Sign canonical bytes of (object with all *_signature_b64 stripped)."""
    payload = _strip_signature(obj)
    sig_bytes = priv_key.sign(canonical_bytes(payload))
    return base64.b64encode(sig_bytes).decode("ascii")


def verify(pub_key: Ed25519PublicKey, obj: Any, signature_b64: str) -> bool:
    """Verify a signature against the canonical bytes of (object minus signatures)."""
    try:
        payload = _strip_signature(obj)
        sig_bytes = base64.b64decode(signature_b64)
        pub_key.verify(sig_bytes, canonical_bytes(payload))
        return True
    except Exception:
        return False


def pubkey_to_b64(pub_key: Ed25519PublicKey) -> str:
    raw = pub_key.public_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PublicFormat.Raw,
    )
    return base64.b64encode(raw).decode("ascii")


def pubkey_from_b64(b64: str) -> Ed25519PublicKey:
    raw = base64.b64decode(b64)
    return Ed25519PublicKey.from_public_bytes(raw)


def privkey_to_b64(priv_key: Ed25519PrivateKey) -> str:
    raw = priv_key.private_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PrivateFormat.Raw,
        encryption_algorithm=serialization.NoEncryption(),
    )
    return base64.b64encode(raw).decode("ascii")


def privkey_from_b64(b64: str) -> Ed25519PrivateKey:
    raw = base64.b64decode(b64)
    return Ed25519PrivateKey.from_private_bytes(raw)


def gen_keypair() -> Tuple[Ed25519PrivateKey, Ed25519PublicKey]:
    sk = Ed25519PrivateKey.generate()
    return sk, sk.public_key()

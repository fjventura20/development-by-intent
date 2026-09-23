"""ATE P1 v0.2 — shared crypto utilities.

RFC 8785 JCS canonicalization (subset), Ed25519 signing/verification,
SHA-256, UUID5 derivation.
"""
import hashlib
import json
import uuid
from typing import Any, Dict

from cryptography.hazmat.primitives.asymmetric.ed25519 import (
    Ed25519PrivateKey,
    Ed25519PublicKey,
)
from cryptography.hazmat.primitives import serialization


def sha256(data: bytes) -> bytes:
    return hashlib.sha256(data).digest()


def canonicalize(obj: Any) -> bytes:
    """RFC 8785 JCS-compatible canonicalization (deterministic JSON).

    Sorts keys lexicographically, drops insignificant whitespace, emits
    UTF-8. Sufficient for our envelope payload.
    """
    return json.dumps(
        obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode("utf-8")


def canonical_sha256(obj: Any) -> bytes:
    return sha256(canonicalize(obj))


def sign_ed25519(private_key: Ed25519PrivateKey, message: bytes) -> bytes:
    return private_key.sign(message)


def verify_ed25519(public_key: Ed25519PublicKey, signature: bytes, message: bytes) -> bool:
    try:
        public_key.verify(signature, message)
        return True
    except Exception:
        return False


def operation_id_for_decision(canonical_decision_without_op_id: bytes) -> str:
    """Stable operation_id derived from decision contents.

    UUID5 with SHA-256 of canonical-decision-bytes. Deterministic; the
    same decision envelope produces the same operation_id across
    authority and executor.
    """
    digest = sha256(canonical_decision_without_op_id)
    return str(uuid.uuid5(uuid.NAMESPACE_OID, digest.hex()))


# --- key IO ---

def load_ed25519_private_pem(path: str) -> Ed25519PrivateKey:
    with open(path, "rb") as f:
        key = serialization.load_pem_private_key(f.read(), password=None)
    assert isinstance(key, Ed25519PrivateKey)
    return key


def load_ed25519_public_pem(path: str) -> Ed25519PublicKey:
    with open(path, "rb") as f:
        key = serialization.load_pem_public_key(f.read())
    assert isinstance(key, Ed25519PublicKey)
    return key


def save_ed25519_private_pem(key: Ed25519PrivateKey, path: str) -> None:
    pem = key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    )
    with open(path, "wb") as f:
        f.write(pem)


def save_ed25519_public_pem(key: Ed25519PublicKey, path: str) -> None:
    pem = key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )
    with open(path, "wb") as f:
        f.write(pem)


def gen_ed25519_keypair() -> tuple[Ed25519PrivateKey, Ed25519PublicKey]:
    priv = Ed25519PrivateKey.generate()
    return priv, priv.public_key()

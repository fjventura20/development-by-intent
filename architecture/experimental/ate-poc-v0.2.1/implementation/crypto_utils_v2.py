"""Shared crypto helpers for ATE-PoC v0.2.1.

Ed25519 sign / verify over canonicalized bytes.
Fixture keys (NOT production keys).

v0.2.1 additions vs v0.1:
- per-role key identifiers and public-key fingerprints
- canonicalize is reused from v0.1
"""
import base64, hashlib

from cryptography.hazmat.primitives.asymmetric.ed25519 import (
    Ed25519PrivateKey, Ed25519PublicKey
)


def generate_keypair():
    priv = Ed25519PrivateKey.generate()
    pub = priv.public_key()
    return priv, pub


def public_key_b64(pub):
    return base64.b64encode(pub.public_bytes_raw()).decode("ascii")


def private_key_b64(priv):
    return base64.b64encode(priv.private_bytes_raw()).decode("ascii")


def load_public_key_from_b64(b64):
    return Ed25519PublicKey.from_public_bytes(base64.b64decode(b64))


def canonicalize_json(obj):
    """RFC 8785 JSON Canonicalization Scheme (strict).

    Object keys sorted by UTF-16 code unit order. No whitespace.
    Sorted arrays preserved. null vs omitted distinct.
    Numbers in canonical form.
    """
    import json
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def verify(pub_key, obj, signature_b64, *, exclude_signature=True):
    """Verify the signature against the canonicalized JSON of obj.

    By default excludes the 'signature_b64' key from the signed region.
    Returns True iff the signature is valid.
    """
    import base64 as _b64
    if exclude_signature:
        msg = canonicalize_without_signature(obj)
    else:
        msg = canonicalize_json(obj)
    sig = _b64.b64decode(signature_b64)
    try:
        pub_key.verify(sig, msg)
        return True
    except Exception:
        return False


def sign(priv_key, obj, *, exclude_signature=True):
    """Sign the canonicalized JSON of obj. Returns signature_b64.

    By default excludes the 'signature_b64' key from the signed region.
    """
    if exclude_signature:
        msg = canonicalize_without_signature(obj)
    else:
        msg = canonicalize_json(obj)
    sig = priv_key.sign(msg)
    return base64.b64encode(sig).decode("ascii")


def public_key_fingerprint(pub_key_b64_str):
    """Stable SHA-256 fingerprint of a public-key (base64-decoded bytes)."""
    raw = base64.b64decode(pub_key_b64_str)
    return hashlib.sha256(raw).hexdigest()


def private_key_fingerprint(priv_key, pub_key_b64_str=None):
    """Stable SHA-256 fingerprint of a private key.

    WARNING: derived from private bytes (acceptable for fixture-only).
    DO NOT USE in production; private-key hashes leak material.
    """
    raw = priv_key.private_bytes_raw()
    return hashlib.sha256(raw).hexdigest()


# ---- Frozen key-role identifiers (per v0.2.1 §5) ----

KEY_ROLE_IDENTITY = "K_IDENTITY"
KEY_ROLE_TGE = "K_TGE"
KEY_ROLE_AUTHORITY = "K_AUTHORITY"
KEY_ROLE_GEL = "K_GEL"
KEY_ROLE_PIPELINE = "K_PIPELINE"


def fingerprint_obj(obj):
    """SHA-256 over canonicalized JSON of obj."""
    return hashlib.sha256(canonicalize_json(obj)).hexdigest()


# ---- Canonicalize excluding signature_b64 ----

def canonicalize_without_signature(obj):
    """Return canonicalize_json of obj without the 'signature_b64' key."""
    no_sig = {k: v for k, v in obj.items() if k != "signature_b64"}
    return canonicalize_json(no_sig)

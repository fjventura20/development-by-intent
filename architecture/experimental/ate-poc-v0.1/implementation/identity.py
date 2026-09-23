"""IdentityAttestation per ATE-POC-DESIGN-v0.1 §2.1.

Frozen data structure:
  IdentityAttestation = {
    schema_id, agent_id, runtime_fingerprint, session_id,
    issued_at_utc, public_key_b64, signature_b64
  }

The signature is Ed25519 over the canonicalized non-signature fields.
"""
import hashlib

from crypto_utils import (
    generate_keypair, public_key_b64, signature_b64, verify_signature,
    canonicalize_json, load_public_key_from_b64, short_hash,
    Ed25519PrivateKey, Ed25519PublicKey,
)


SCHEMA_ID = "TGE-ATE/0.1"
NON_SIG_FIELDS = (
    "schema_id", "agent_id", "runtime_fingerprint", "session_id",
    "issued_at_utc", "public_key_b64",
)


def make_identity(
    *, agent_id: str, runtime_fingerprint: str, session_id: str,
    issued_at_utc: int, priv: Ed25519PrivateKey,
) -> dict:
    pub = priv.public_key()
    pub_b64 = public_key_b64(pub)
    unsigned = {
        "schema_id": SCHEMA_ID,
        "agent_id": agent_id,
        "runtime_fingerprint": runtime_fingerprint,
        "session_id": session_id,
        "issued_at_utc": issued_at_utc,
        "public_key_b64": pub_b64,
    }
    sig = signature_b64(priv, canonicalize_json(unsigned))
    return {**unsigned, "signature_b64": sig}


def verify_identity(identity: dict) -> tuple:
    """Verify IdentityAttestation signature. Returns (ok, reason_code, reason_description)."""
    if not isinstance(identity, dict):
        return (False, "GX_IDENTITY_MALFORMED", "identity_not_a_dict")
    missing = set(NON_SIG_FIELDS) - set(identity.keys())
    if missing:
        return (False, "GX_IDENTITY_MALFORMED", f"missing_fields:{sorted(missing)}")
    if identity.get("schema_id") != SCHEMA_ID:
        return (False, "GX_IDENTITY_INVALID", f"bad_schema_id:{identity.get('schema_id')!r}")
    if not identity.get("session_id"):
        return (False, "GX_IDENTITY_INVALID", "empty_session_id")
    pub_b64 = identity.get("public_key_b64")
    sig_b64 = identity.get("signature_b64")
    if not pub_b64 or not sig_b64:
        return (False, "GX_IDENTITY_INVALID", "missing_pubkey_or_sig")
    try:
        pub = load_public_key_from_b64(pub_b64)
    except Exception as e:
        return (False, "GX_IDENTITY_INVALID", f"pubkey_decode:{e}")
    unsigned = {k: identity[k] for k in NON_SIG_FIELDS}
    if not verify_signature(pub, canonicalize_json(unsigned), sig_b64):
        return (False, "GX_IDENTITY_INVALID", "signature_verification_failed")
    return (True, "PASS", "identity_verified")


def identity_hash(identity: dict) -> str:
    """Deterministic canonical hash of an identity (for tamper tests)."""
    return hashlib.sha256(canonicalize_json(identity)).hexdigest()

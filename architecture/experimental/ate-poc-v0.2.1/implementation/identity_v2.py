"""IdentityAttestation v0.2.1 (supersedes v0.1).

Frozen structure:
  IdentityAttestation = {
    schema_id, agent_id, runtime_fingerprint, session_id,
    issued_at_utc, public_key_b64, signature_b64
  }

The signature_b64 is Ed25519 over canonicalize_without_signature(attestation).
The runtime holds the matching private key.
"""
from crypto_utils_v2 import sign, verify, public_key_b64, canonicalize_json, fingerprint_obj

SCHEMA_ID = "TGE-ATE-V2/0.1"


def make_identity(*, agent_id, runtime_fingerprint, session_id, issued_at_utc,
                  priv_key, pub_key):
    attestation = {
        "schema_id": SCHEMA_ID,
        "agent_id": agent_id,
        "runtime_fingerprint": runtime_fingerprint,
        "session_id": session_id,
        "issued_at_utc": issued_at_utc,
        "public_key_b64": public_key_b64(pub_key),
    }
    attestation["signature_b64"] = sign(priv_key, attestation)
    return attestation


def verify_identity(attestation, pub_key):
    """Returns (ok, details)."""
    if attestation.get("schema_id") != SCHEMA_ID:
        return False, "schema_id_mismatch"
    if "signature_b64" not in attestation:
        return False, "missing_signature"
    ok = verify(pub_key, attestation, attestation["signature_b64"])
    if not ok:
        return False, "signature_invalid"
    return True, "verified"


def identity_fingerprint(attestation):
    """Stable SHA-256 fingerprint of the IdentityAttestation (signed bytes)."""
    return fingerprint_obj(attestation)

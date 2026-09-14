"""Fixture issuer and RTA (Root-of-Trust Authority).

The issuer signs envelopes; the RTA signs the roster.

These are fixtures. They are NOT live services. The keys are baked into
the test fixtures. v0.2.1 §J.0.4 attestation-label discipline applies.
"""
import time
import base64

from canonicalization import canonicalize, canonical_hash
from crypto_utils import (
    Ed25519PrivateKey, Ed25519PublicKey,
    signature_b64, public_key_b64,
)


def build_envelope(
    *,
    envelope_id: str,
    issuer_id: str,
    issuer_priv: Ed25519PrivateKey,
    issuer_pub: Ed25519PublicKey,
    charter: dict,
    runtime_fingerprint: str,
    valid_for_seconds: int,
    scope: str = "all",
) -> dict:
    """Build and sign an envelope.

    The envelope signs a subset per v0.2.1 §E.2.2:
    canonicalize({
        envelope_id, envelope_version, issuer, charter, binding
    })

    signing-key handle is included via binding.session_id_predicate and
    runtime_fingerprint_predicate so the verifier can cross-check.
    """
    now = int(time.time())
    issuer_pub_b64 = public_key_b64(issuer_pub)

    envelope = {
        "envelope_id": envelope_id,
        "envelope_version": "TGE/0.2.1",
        "issuer": {
            "issuer_id": issuer_id,
            "issuer_pubkey_b64": issuer_pub_b64,
        },
        "charter": {
            "charter_id": charter["charter_id"],
            "charter_sha256": charter["charter_sha256"],
            "charter_canonical_bytes_b64": charter["charter_canonical_bytes_b64"],
        },
        "binding": {
            "runtime_fingerprint_predicate": runtime_fingerprint,
            "not_before_utc": now,
            "not_after_utc": now + valid_for_seconds,
            "scope": scope,
        },
    }
    # Sign the canonicalized envelope (excluding the signature field)
    signed_region = {
        "envelope_id": envelope["envelope_id"],
        "envelope_version": envelope["envelope_version"],
        "issuer": envelope["issuer"],
        "charter": envelope["charter"],
        "binding": envelope["binding"],
    }
    envelope_bytes = canonicalize(signed_region)
    envelope["envelope_issuer_signature_b64"] = signature_b64(issuer_priv, envelope_bytes)
    envelope["envelope_issuer_signature_canonical_hash"] = canonical_hash(signed_region)
    return envelope


def build_roster(*, roster_id: str, rta_priv: Ed25519PrivateKey, rta_pub: Ed25519PublicKey, issuers: list) -> dict:
    """Build and sign a trust roster.

    issuers: list of dicts with keys: issuer_id, issuer_pubkey_b64, charter_type_scope, valid_from_utc, valid_until_utc
    """
    roster = {
        "roster_id": roster_id,
        "roster_version": "TGE-RTA/0.2.1",
        "issued_at_utc": int(time.time()),
        "issuers": issuers,
        "rta_pubkey_b64": public_key_b64(rta_pub),
    }
    signed_region = {
        "roster_id": roster["roster_id"],
        "roster_version": roster["roster_version"],
        "issued_at_utc": roster["issued_at_utc"],
        "issuers": roster["issuers"],
        "rta_pubkey_b64": roster["rta_pubkey_b64"],
    }
    roster_bytes = canonicalize(signed_region)
    roster["rta_signature_b64"] = signature_b64(rta_priv, roster_bytes)
    return roster

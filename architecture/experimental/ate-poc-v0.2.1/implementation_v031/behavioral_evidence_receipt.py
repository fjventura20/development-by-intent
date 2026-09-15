"""ATE v0.3.1 BehavioralEvidenceReceipt (per PI RULING 1).

Reuses the existing Stage C v0.1 frozen result. The receipt is a
signed attestation by K_BEHAVIORAL that the Stage C v0.1 evidence
remains acceptable for ATE gate purposes.

Fields (per PI RULING 1):
  source_identifier, stage_c_version, evidence_digest,
  evaluation_result_status, issued_at_utc, expires_at_utc,
  authority_fingerprint, authority_signature_b64
"""
from dataclasses import dataclass, field
from typing import Any, Dict, Optional

from cryptography.hazmat.primitives.asymmetric.ed25519 import (
    Ed25519PrivateKey,
    Ed25519PublicKey,
)

from crypto_utils import (
    fingerprint_bytes,
    fingerprint_obj,
    pubkey_to_b64,
    sign,
    verify,
)


SCHEMA_ID = "ATE-V3.1-BEHAVIORAL-EVIDENCE-RECEIPT/0.1"

# Frozen Stage C v0.1 frozen-result digest (reference; the actual
# evidence_digest is computed from the canonicalized frozen result
# bytes at receipt-construction time).
STAGE_C_V01_SOURCE_IDENTIFIER = "STAGE-C-V0.1-FIXED-BATTERY"
STAGE_C_V01_VERSION = "0.1"
STAGE_C_V01_PASS_RESULT = {
    "schema_id": "STAGE-C-V0.1-FROZEN-RESULT/0.1",
    "battery_id": "STAGE-C-V0.1-FIXED-BATTERY",
    "metric_results": [
        {"metric_id": "C1", "result": "PASS", "justification": "Frozen C1 conclusion (commit b8cc8da)."},
    ],
    "overall": "PASS",
}

TTL_SECONDS = 86400  # PI RULING 5


def stage_c_v0_1_evidence_digest() -> str:
    """Deterministic digest of the Stage C v0.1 frozen result.

    The frozen result is the canonical SHA-256 over the canonicalized
    C1 PASS result. C2 STOPPED at INSUFFICIENT_BEHAVIORAL_VARIANCE;
    C3 NOT_EXECUTED. Per PI RULING 1, the receipt references historical
    Stage C evidence — TTL governs freshness of the authority assertion,
    not the creation date of the underlying evidence.
    """
    return fingerprint_obj(STAGE_C_V01_PASS_RESULT)


def make_behavioral_evidence_receipt(
    *,
    issued_at_utc: float,
    authority_priv_key: Ed25519PrivateKey,
    authority_pub_key: Ed25519PublicKey,
) -> Dict[str, Any]:
    rec = {
        "schema_id": SCHEMA_ID,
        "receipt_id": "<pending>",
        "source_identifier": STAGE_C_V01_SOURCE_IDENTIFIER,
        "stage_c_version": STAGE_C_V01_VERSION,
        "evidence_digest": stage_c_v0_1_evidence_digest(),
        "evaluation_result_status": "PASS_BEHAVIORAL",
        "issued_at_utc": issued_at_utc,
        "expires_at_utc": issued_at_utc + TTL_SECONDS,
        "authority_fingerprint": fingerprint_obj(
            {"public_key_b64": pubkey_to_b64(authority_pub_key)}
        ),
        "authority_signature_b64": "<pending>",
    }
    # Set receipt_id as fingerprint of structure without receipt_id and sig.
    from crypto_utils import canonical_bytes
    rec_no_ids = {k: v for k, v in rec.items() if k not in ("receipt_id", "authority_signature_b64")}
    rec["receipt_id"] = fingerprint_obj(rec_no_ids)
    rec["authority_signature_b64"] = sign(authority_priv_key, rec)
    return rec


def verify_behavioral_evidence_receipt(
    rec: Dict[str, Any],
    authority_pub_key: Ed25519PublicKey,
) -> bool:
    return verify(authority_pub_key, rec, rec.get("authority_signature_b64", ""))

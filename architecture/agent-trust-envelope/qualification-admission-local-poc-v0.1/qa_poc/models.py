"""ATE Qualification & Admission Local PoC v0.1 — frozen artifact models.

The v0.1.2 design §14 enumerates the immutable signed artifacts:

  QualificationRequirementsProfile
  QualificationEvidenceManifest
  QualificationDecision
  QualificationCredential
  AdmissionPolicy
  AdmissionEvidenceManifest
  AdmissionDecision
  AdmissionCredential
  CapabilityToken
  TrustDecision
  ControlRecord
  TrustStateSnapshot

This module defines each artifact as a typed dataclass with two
mandatory fields added on sign: `signature` (bytes) and `signature_domain`
(str). The signature is always over the canonical payload (the dataclass
as dict, minus `signature`).

Credentials are immutable after signing. The PoC enforces that by
issuing fresh credentials with new IDs/digests whenever semantics change
(see admission.py / authorization.py) rather than mutating fields.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

# -- Artifact signing domains (frozen §8 + §14) --------------------------------

DOMAIN_QUALIFICATION_REQUIREMENTS_PROFILE = "ate.qualification.requirements_profile.v1"
DOMAIN_QUALIFICATION_EVIDENCE_MANIFEST = "ate.qualification.evidence_manifest.v1"
DOMAIN_QUALIFICATION_DECISION = "ate.qualification.decision.v1"
DOMAIN_QUALIFICATION_CREDENTIAL = "ate.qualification.credential.v1"

DOMAIN_ADMISSION_POLICY = "ate.admission.policy.v1"
DOMAIN_ADMISSION_EVIDENCE_MANIFEST = "ate.admission.evidence_manifest.v1"
DOMAIN_ADMISSION_DECISION = "ate.admission.decision.v1"
DOMAIN_ADMISSION_CREDENTIAL = "ate.admission.credential.v1"

DOMAIN_CAPABILITY_TOKEN = "ate.authorization.capability_token.v1"
DOMAIN_TRUST_DECISION = "ate.authorization.trust_decision.v1"

DOMAIN_CONTROL_RECORD = "ate.executor.control_record.v1"
DOMAIN_TRUST_STATE_SNAPSHOT = "ate.executor.trust_state_snapshot.v1"


def ALL_DOMAINS() -> List[str]:
    return [
        DOMAIN_QUALIFICATION_REQUIREMENTS_PROFILE,
        DOMAIN_QUALIFICATION_EVIDENCE_MANIFEST,
        DOMAIN_QUALIFICATION_DECISION,
        DOMAIN_QUALIFICATION_CREDENTIAL,
        DOMAIN_ADMISSION_POLICY,
        DOMAIN_ADMISSION_EVIDENCE_MANIFEST,
        DOMAIN_ADMISSION_DECISION,
        DOMAIN_ADMISSION_CREDENTIAL,
        DOMAIN_CAPABILITY_TOKEN,
        DOMAIN_TRUST_DECISION,
        DOMAIN_CONTROL_RECORD,
        DOMAIN_TRUST_STATE_SNAPSHOT,
    ]


# -- Helpers ---------------------------------------------------------------


def _to_payload_dict(d: Dict[str, Any]) -> Dict[str, Any]:
    """Backward-compat helper — returns the SIGNING payload. New code
    should call `signing_payload(obj)` and `digest_payload(obj)`
    explicitly. Retained only for tests that still reference it."""
    return signing_payload_for_dict(obj_class_name=d.get("__class_name__", ""), d=d)


def signing_payload_for_dict(obj_class_name: str, d: Dict[str, Any]) -> Dict[str, Any]:
    """Build the canonical signing payload from a dict representation.

    Per the DEV-IMP-3 non-recursive construction:
      - INCLUDES the artifact's own id and digest
      - INCLUDES all semantic fields (including foreign-id references)
      - EXCLUDES only `signature` and `signature_domain`

    The signing payload is what gets bound by the Ed25519 signature.
    Verification rebuilds this exact dict, drops `signature`, and runs
    `verify_ed25519` against the same canonical bytes.
    """
    out = dict(d)
    out.pop("signature", None)
    out.pop("signature_domain", None)
    return out


def digest_payload_for_dict(obj_class_name: str, d: Dict[str, Any]) -> Dict[str, Any]:
    """Build the canonical digest-input payload from a dict representation.

    Per the DEV-IMP-3 non-recursive construction:
      - INCLUDES the artifact's own id
      - INCLUDES all semantic fields (including foreign-id references)
      - EXCLUDES the artifact's own digest (which is what we're computing)
      - EXCLUDES signature / signature_domain

    The artifact's own digest is computed from this payload. The id is
    included so that the digest is bound to the id at issue time.
    """
    own_id = _OWN_ID_FIELD.get(obj_class_name)
    own_digest = _OWN_DIGEST_FIELD.get(obj_class_name)
    out = dict(d)
    out.pop("signature", None)
    out.pop("signature_domain", None)
    if own_digest is not None:
        out.pop(own_digest, None)
    # own_id IS included in the digest input (so the digest binds the id).
    _ = own_id  # referenced for documentation; the key is NOT popped.
    return out


# The "own id" / "own digest" field name per artifact class.
# In the digest-input payload: the own-id field is KEPT (so digest binds id),
# the own-digest field is DROPPED (because that's what we're computing).
# In the signing payload: BOTH own-id and own-digest are KEPT (so signature
# binds both). In both payloads, signature/signature_domain are dropped.
_OWN_ID_FIELD = {
    "QualificationRequirementsProfile": "profile_id",
    "QualificationEvidenceManifest": "manifest_id",
    "QualificationDecision": "decision_id",
    "QualificationCredential": "credential_id",
    "AdmissionPolicy": "policy_id",
    "AdmissionEvidenceManifest": "manifest_id",
    "AdmissionDecision": "decision_id",
    "AdmissionCredential": "credential_id",
    "CapabilityToken": "token_id",
    "TrustDecision": "trust_decision_id",
    "ControlRecord": "record_id",
    "TrustStateSnapshot": "snapshot_id",
}
_OWN_DIGEST_FIELD = {
    "QualificationRequirementsProfile": "profile_digest",
    "QualificationEvidenceManifest": "manifest_digest",
    "QualificationDecision": "decision_digest",
    "QualificationCredential": "credential_digest",
    "AdmissionPolicy": "policy_digest",
    "AdmissionEvidenceManifest": "manifest_digest",
    "AdmissionDecision": "decision_digest",
    "AdmissionCredential": "credential_digest",
    "CapabilityToken": "token_digest",
    "TrustDecision": "trust_decision_digest",
    "ControlRecord": "record_digest",
    "TrustStateSnapshot": "snapshot_digest",
}


# -- Profiles / policies / evidence manifests (issued by authority) ----------


@dataclass
class QualificationRequirementsProfile:
    """Authority-published profile (§12). Signed by AUTH_R11_QUALIFICATION."""

    profile_id: str
    profile_version: int
    qualification_domain: str
    role_id: str
    minimum_binding: str  # SB1/SB2/SB3
    maximum_risk: str  # R0..R4
    eligible_capability: str
    required_evidence_classes: List[str]
    profile_digest: str  # SHA-256 of canonical payload, set at sign-time
    signature: bytes = b""
    signature_domain: str = DOMAIN_QUALIFICATION_REQUIREMENTS_PROFILE


@dataclass
class AdmissionPolicy:
    """Authority-published admission policy (§13). Signed by AUTH_R12_ADMISSION."""

    policy_id: str
    policy_version: int
    trust_domain: str
    role: str
    qualification_domain: str
    qualification_authority: str  # key_id
    recognized_profile_id: str
    recognized_profile_digest: str  # exact digest (no `version >= N`)
    maximum_risk: str
    eligible_capability: str
    policy_digest: str
    signature: bytes = b""
    signature_domain: str = DOMAIN_ADMISSION_POLICY


@dataclass
class QualificationEvidenceManifest:
    """§14 — evidence manifest signed by AUTH_IDENTITY (for identity evidence)
    and by the relevant authority keys for the other evidence classes."""

    manifest_id: str
    subject_identity_id: str
    subject_binding_digest: str
    runtime_class: str
    provider_id: str
    evidence_classes: List[str]
    manifest_digest: str
    signature: bytes = b""
    signature_domain: str = DOMAIN_QUALIFICATION_EVIDENCE_MANIFEST


@dataclass
class QualificationDecision:
    """§14 — qualification decision signed by AUTH_R11_QUALIFICATION."""

    decision_id: str
    profile_id: str
    profile_digest: str
    subject_identity_id: str
    subject_binding_digest: str
    decision: str  # GRANTED / DENIED
    reason_code: str
    issued_at_unix_ms: int
    decision_digest: str
    signature: bytes = b""
    signature_domain: str = DOMAIN_QUALIFICATION_DECISION


@dataclass
class QualificationCredential:
    """§14 — issued on GRANTED; immutable.

    `credential_id` and `credential_digest` are bound into every
    downstream CapabilityToken and TrustDecision.
    """

    credential_id: str
    profile_id: str
    profile_digest: str
    subject_identity_id: str
    subject_binding_digest: str
    issued_at_unix_ms: int
    expires_at_unix_ms: int
    historical_trust_state_reference: str
    credential_digest: str
    signature: bytes = b""
    signature_domain: str = DOMAIN_QUALIFICATION_CREDENTIAL


@dataclass
class AdmissionEvidenceManifest:
    manifest_id: str
    qualification_credential_id: str
    qualification_credential_digest: str
    subject_identity_id: str
    subject_binding_digest: str
    evidence_classes: List[str]
    manifest_digest: str
    signature: bytes = b""
    signature_domain: str = DOMAIN_ADMISSION_EVIDENCE_MANIFEST


@dataclass
class AdmissionDecision:
    decision_id: str
    policy_id: str
    policy_digest: str
    qualification_credential_id: str
    qualification_credential_digest: str
    subject_identity_id: str
    subject_binding_digest: str
    decision: str  # GRANTED / DENIED
    reason_code: str
    issued_at_unix_ms: int
    decision_digest: str
    signature: bytes = b""
    signature_domain: str = DOMAIN_ADMISSION_DECISION


@dataclass
class AdmissionCredential:
    """§14 — issued on GRANTED; immutable."""

    credential_id: str
    policy_id: str
    policy_digest: str
    qualification_credential_id: str
    qualification_credential_digest: str
    subject_identity_id: str
    subject_binding_digest: str
    issued_at_unix_ms: int
    expires_at_unix_ms: int
    historical_trust_state_reference: str
    credential_digest: str
    signature: bytes = b""
    signature_domain: str = DOMAIN_ADMISSION_CREDENTIAL


# -- Capability / TrustDecision / ControlRecord / Snapshot --------------------


@dataclass
class CapabilityToken:
    """§21 — signed by AUTH_AUTHORIZATION."""

    token_id: str
    subject_binding_digest: str
    qualification_credential_id: str
    qualification_credential_digest: str
    admission_credential_id: str
    admission_credential_digest: str
    session_identity: str
    operation: str
    target: str
    parameters_digest: str
    risk_class: str
    capability_class: str
    nonce: str
    issued_at_unix_ms: int
    expires_at_unix_ms: int
    historical_trust_state_reference: str
    token_digest: str
    signature: bytes = b""
    signature_domain: str = DOMAIN_CAPABILITY_TOKEN


@dataclass
class TrustDecision:
    """§22 — signed by AUTH_TRUST_DECISION."""

    trust_decision_id: str
    capability_token_id: str
    capability_token_digest: str
    requested_action_digest: str
    verdict: str  # AUTHORIZED / DENIED
    issued_at_unix_ms: int
    expires_at_unix_ms: int
    historical_trust_state_reference: str
    trust_decision_digest: str
    signature: bytes = b""
    signature_domain: str = DOMAIN_TRUST_DECISION


@dataclass
class ControlRecord:
    """§16 — signed by the appropriate authority key (depends on change_type)."""

    record_id: str
    previous_epoch: int
    new_epoch: int
    change_type: str
    target_type: str
    target_id: str
    target_digest_optional: Optional[str]
    issued_at_unix_ms: int
    issuer_authority_id: str
    issuer_key_id: str
    record_digest: str
    signature: bytes = b""
    signature_domain: str = DOMAIN_CONTROL_RECORD


@dataclass
class TrustStateSnapshot:
    """§15 — coherent committed state view at issuance time."""

    snapshot_id: str
    applied_epoch: int
    control_state_digest: str
    issued_at_unix_ms: int
    issuer_authority_id: str
    snapshot_digest: str
    signature: bytes = b""
    signature_domain: str = DOMAIN_TRUST_STATE_SNAPSHOT


# -- Public payload helper used by sign/verify --------------------------------


def artifact_payload(obj) -> Dict[str, Any]:
    """Return the dict that gets SIGNED (signing payload).

    Per DEV-IMP-3: includes the artifact's own id + digest + all
    semantic fields; excludes only signature/signature_domain.
    """
    from dataclasses import asdict

    cls = obj.__class__.__name__
    d = asdict(obj)
    d.pop("signature", None)
    d.pop("signature_domain", None)
    return d


def digest_payload(obj) -> Dict[str, Any]:
    """Return the dict from which the artifact's own digest is computed.

    Per DEV-IMP-3: includes the artifact's own id + all semantic fields;
    excludes the artifact's own digest field (we're computing it) and
    signature/signature_domain.
    """
    from dataclasses import asdict

    cls = obj.__class__.__name__
    own_digest = _OWN_DIGEST_FIELD.get(cls)
    d = asdict(obj)
    d.pop("signature", None)
    d.pop("signature_domain", None)
    if own_digest is not None:
        d.pop(own_digest, None)
    return d


def artifact_digest(obj) -> str:
    """Compute the artifact's own digest from the digest-input payload."""
    from .canonical import canonical_sha256

    return canonical_sha256(digest_payload(obj))


def compute_id_and_digest(
    obj, *, semantic_fields: dict, id_prefix: str, id_salt: tuple
) -> tuple:
    """Non-recursive construction (DEV-IMP-3 §3):

      1. ID assigned BEFORE digest construction from semantic_fields.
      2. ID + semantic_fields → digest (canonical).
      3. digest field set on a new copy of obj.

    Returns: (new_obj_with_id_and_digest, digest_value)

    The returned object has:
      - the same field set as obj, with `signature` and `signature_domain`
        untouched (still defaults)
      - own_id_field populated
      - own_digest_field populated

    Caller is responsible for adding `signature` afterward via
    `with_signature()`.

    `semantic_fields` is the dict of fields that participate in the
    digest (and the signing payload), excluding the artifact's own id
    and digest. `id_salt` is a tuple of additional strings that make
    the id unique across issuance contexts (e.g. sb_digest, profile_digest).
    """
    from dataclasses import asdict, replace
    from .canonical import canonical_sha256

    cls = obj.__class__.__name__
    own_id = _OWN_ID_FIELD[cls]
    own_digest = _OWN_DIGEST_FIELD[cls]

    # Step 1: assign id deterministically from semantic fields. We use
    # a placeholder digest to derive a unique id; the id will remain
    # valid because the digest is computed over (id, semantic_fields),
    # so different ids produce different digests.
    placeholder_digest_for_id = canonical_sha256(
        {"__placeholder__": True, **semantic_fields, "__id_salt__": list(id_salt)}
    )
    new_id = _stable_id_from_digest(id_prefix, placeholder_digest_for_id, id_salt)

    # Step 2: compute digest from (id, semantic_fields) — own_digest excluded.
    digest_input = {own_id: new_id, **semantic_fields}
    digest_value = canonical_sha256(digest_input)

    # Step 3: build new object with id + digest populated
    d = asdict(obj)
    d[own_id] = new_id
    d[own_digest] = digest_value
    new_obj = replace(obj, **d)
    return new_obj, digest_value


def _stable_id_from_digest(prefix: str, digest_hex: str, salt: tuple) -> str:
    """Derive a stable id from a digest + salt tuple."""
    import hashlib

    h = hashlib.sha256()
    h.update(digest_hex.encode("ascii"))
    for s in salt:
        h.update(b"\x00")
        h.update(s.encode("utf-8"))
    return f"{prefix}-{h.hexdigest()[:24]}"


def with_signature(obj, sig: bytes):
    """Return a NEW object with the signature field populated. Immutable.

    The original `obj` is not mutated. The returned object has the
    same field set plus `signature`.
    """
    from dataclasses import asdict, replace

    d = asdict(obj)
    d["signature"] = sig
    return replace(obj, **d)


def verify_artifact(obj, pub_key, *, expected_id: Optional[str] = None) -> None:
    """Verify an artifact's signature and (recomputed) digest.

    Per DEV-IMP-3 §3 step 7:
      - recompute the digest from (id, semantic_fields)
      - compare to obj.<own_digest_field>; raise on mismatch
      - verify signature over (id, semantic_fields, digest) (excluding signature)
      - reject any mutation of the artifact id, digest, or semantic fields

    Raises:
      DigestMismatchError: own_digest field doesn't match recomputed digest
      SignatureError: signature doesn't verify
      IdMismatchError: obj.id != expected_id (when provided)
    """
    from .canonical import canonical_sha256
    from .crypto import verify_ed25519
    from cryptography.exceptions import InvalidSignature

    cls = obj.__class__.__name__
    own_id = _OWN_ID_FIELD[cls]
    own_digest = _OWN_DIGEST_FIELD[cls]

    # 1. Verify the id if provided
    if expected_id is not None:
        actual_id = getattr(obj, own_id)
        if actual_id != expected_id:
            raise IdMismatchError(
                f"{own_id}={actual_id} != expected {expected_id}"
            )

    # 2. Recompute digest from (id, semantic_fields)
    d = digest_payload(obj)
    d_with_id = dict(d)
    d_with_id[own_id] = getattr(obj, own_id)
    recomputed = canonical_sha256(d_with_id)
    if recomputed != getattr(obj, own_digest):
        raise DigestMismatchError(
            f"{own_digest} mismatch: stored={getattr(obj, own_digest)[:16]} "
            f"recomputed={recomputed[:16]}"
        )

    # 3. Verify signature over signing payload
    sig_payload = artifact_payload(obj)  # excludes signature/signature_domain
    try:
        verify_ed25519(pub_key, obj.signature, obj.signature_domain, sig_payload)
    except InvalidSignature as e:
        raise SignatureError(str(e)) from e


class DigestMismatchError(Exception):
    pass


class SignatureError(Exception):
    pass


class IdMismatchError(Exception):
    pass

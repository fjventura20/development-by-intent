"""ATE Qualification & Admission Local PoC v0.1 — admission pipeline.

Per design §13 / §19: admission depends on its exact bound QualificationCredential.
At every downstream use (capability issuance, trust decision, EAP), we
recursively evaluate the qualification chain — no cached boolean
admitted=true may substitute.

This module issues AdmissionEvidenceManifest, AdmissionDecision, and
AdmissionCredential. Authority keys (frozen §6):
  AUTH_R12_ADMISSION — decisions + credentials
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from typing import Optional, Tuple

from .canonical import canonical_sha256
from .clock import Clock
from .crypto import Ed25519PrivateKey, Ed25519PublicKey, sign_ed25519
from .models import (
    DOMAIN_ADMISSION_CREDENTIAL,
    DOMAIN_ADMISSION_DECISION,
    DOMAIN_ADMISSION_EVIDENCE_MANIFEST,
    AdmissionCredential,
    AdmissionDecision,
    AdmissionEvidenceManifest,
    AdmissionPolicy,
    QualificationCredential,
    artifact_payload,
    compute_id_and_digest,
    with_signature,
)
from .policies import PolicyRegistry, PolicyResolution, verify_policy_signature
from .subject_binding import SubjectBinding


def _stable_id(prefix: str, *parts: str) -> str:
    h = hashlib.sha256()
    for p in parts:
        h.update(p.encode("utf-8"))
        h.update(b"\x00")
    return f"{prefix}-{h.hexdigest()[:24]}"


@dataclass
class AdmissionEvidenceInputs:
    """The 4 evidence classes for admission (per §13; deterministic fixture)."""

    subject_binding_digest: str
    qualification_credential_digest: str
    policy_digest: str
    trust_domain: str


def build_admission_evidence(inputs: AdmissionEvidenceInputs) -> dict:
    return {
        "subject_binding": inputs.subject_binding_digest,
        "qualification_credential": inputs.qualification_credential_digest,
        "policy": inputs.policy_digest,
        "trust_domain": inputs.trust_domain,
        "evidence_digest": canonical_sha256(inputs.__dict__),
    }


# -- Recursive dependency evaluation (frozen §19) ----------------------------


class DependencyEvaluationError(Exception):
    """Raised when a downstream use discovers its bound qualification is unusable."""


def check_qualification_usable(
    *,
    qualification: QualificationCredential,
    clock: Clock,
    revocation_lookup,
) -> None:
    """Recursively evaluate whether a bound QualificationCredential is usable.

    Raises DependencyEvaluationError if any condition fails. The PoC
    revocation_lookup is a callable returning (is_revoked: bool,
    reason_code: str) for a given credential_id.
    """
    if clock.now_unix_ms >= qualification.expires_at_unix_ms:
        raise DependencyEvaluationError(
            "AX_QUALIFICATION_EXPIRED: credential past expiry"
        )
    is_revoked, reason = revocation_lookup(qualification.credential_id)
    if is_revoked:
        raise DependencyEvaluationError(
            f"AX_QUALIFICATION_REVOKED: {reason}"
        )


def check_admission_usable(
    *,
    admission: AdmissionCredential,
    clock: Clock,
    qualification: QualificationCredential,
    revocation_lookup,
) -> None:
    """Check admission expiry + its bound qualification chain."""
    if clock.now_unix_ms >= admission.expires_at_unix_ms:
        raise DependencyEvaluationError(
            "AX_ADMISSION_EXPIRED: credential past expiry"
        )
    is_revoked, reason = revocation_lookup(admission.credential_id)
    if is_revoked:
        raise DependencyEvaluationError(
            f"AX_ADMISSION_REVOKED: {reason}"
        )
    # §19: usable(admission) requires usable(exact bound qualification)
    check_qualification_usable(
        qualification=qualification,
        clock=clock,
        revocation_lookup=revocation_lookup,
    )


# -- Admission authority ----------------------------------------------------


class AdmissionAuthority:
    def __init__(
        self,
        *,
        registry: PolicyRegistry,
        r12_priv: Ed25519PrivateKey,
        r12_pub: Ed25519PublicKey,
        r12_key_id: str,
    ) -> None:
        self.registry = registry
        self.r12_priv = r12_priv
        self.r12_pub = r12_pub
        self.r12_key_id = r12_key_id

    def publish_policy(
        self,
        *,
        policy_id: str,
        policy_version: int,
        trust_domain: str,
        role: str,
        qualification_domain: str,
        qualification_authority_key_id: str,
        recognized_profile_id: str,
        recognized_profile_digest: str,
        maximum_risk: str,
        eligible_capability: str,
    ) -> AdmissionPolicy:
        pol_proto = AdmissionPolicy(
            policy_id="",  # filled by compute_id_and_digest
            policy_version=policy_version,
            trust_domain=trust_domain,
            role=role,
            qualification_domain=qualification_domain,
            qualification_authority=qualification_authority_key_id,
            recognized_profile_id=recognized_profile_id,
            recognized_profile_digest=recognized_profile_digest,
            maximum_risk=maximum_risk,
            eligible_capability=eligible_capability,
            policy_digest="",  # filled by compute_id_and_digest
        )
        semantic = {
            "policy_version": policy_version,
            "trust_domain": trust_domain,
            "role": role,
            "qualification_domain": qualification_domain,
            "qualification_authority": qualification_authority_key_id,
            "recognized_profile_id": recognized_profile_id,
            "recognized_profile_digest": recognized_profile_digest,
            "maximum_risk": maximum_risk,
            "eligible_capability": eligible_capability,
        }
        pol, _ = compute_id_and_digest(
            pol_proto,
            semantic_fields=semantic,
            id_prefix="apol",
            id_salt=(trust_domain, role, str(policy_version)),
        )
        sig = sign_ed25519(self.r12_priv, pol.signature_domain, artifact_payload(pol))
        pol = with_signature(pol, sig)
        verify_policy_signature(self.r12_pub, pol)
        self.registry.publish(pol)
        return pol

    def evaluate(
        self,
        *,
        subject_binding: SubjectBinding,
        qualification: QualificationCredential,
        trust_domain: str,
        role: str,
        snapshot_reference: str,
        clock: Clock,
        revocation_lookup,
        admission_lifetime_ms: Optional[int] = None,
    ) -> Tuple[AdmissionEvidenceManifest, AdmissionDecision, Optional[AdmissionCredential]]:
        # 1. Resolve active policy
        res = self.registry.resolve(trust_domain, role)

        # 2. §13 exact-profile recognition (no `version >= N`)
        if (
            qualification.profile_id != res.policy.recognized_profile_id
            or qualification.profile_digest != res.policy.recognized_profile_digest
        ):
            raise DependencyEvaluationError(
                "AX_QUALIFICATION_PROFILE_UNRECOGNIZED: bound profile not in policy"
            )

        # 3. §19 recursive dependency evaluation
        check_qualification_usable(
            qualification=qualification,
            clock=clock,
            revocation_lookup=revocation_lookup,
        )

        sb_digest = subject_binding.digest()
        decision_str = "GRANTED"
        reason_code = ""

        # Evidence manifest (DEV-IMP-3 non-recursive construction)
        evid_inputs = AdmissionEvidenceInputs(
            subject_binding_digest=sb_digest,
            qualification_credential_digest=qualification.credential_digest,
            policy_digest=res.policy.policy_digest,
            trust_domain=trust_domain,
        )
        evid = build_admission_evidence(evid_inputs)
        manifest_semantic = {
            "qualification_credential_id": qualification.credential_id,
            "qualification_credential_digest": qualification.credential_digest,
            "subject_identity_id": subject_binding.subject_identity_id,
            "subject_binding_digest": sb_digest,
            "evidence_classes": [
                "subject_binding",
                "qualification_credential",
                "policy",
                "trust_domain",
            ],
            "evidence": evid,
        }
        manifest_proto = AdmissionEvidenceManifest(
            manifest_id="",
            qualification_credential_id=manifest_semantic["qualification_credential_id"],
            qualification_credential_digest=manifest_semantic["qualification_credential_digest"],
            subject_identity_id=manifest_semantic["subject_identity_id"],
            subject_binding_digest=manifest_semantic["subject_binding_digest"],
            evidence_classes=manifest_semantic["evidence_classes"],
            manifest_digest="",
        )
        manifest, _ = compute_id_and_digest(
            manifest_proto,
            semantic_fields=manifest_semantic,
            id_prefix="aem",
            id_salt=(qualification.credential_digest, sb_digest, res.policy.policy_digest),
        )
        sig = sign_ed25519(self.r12_priv, manifest.signature_domain, artifact_payload(manifest))
        manifest = with_signature(manifest, sig)

        # Decision
        semantic_payload = {
            "policy_id": res.policy.policy_id,
            "policy_digest": res.policy.policy_digest,
            "qualification_credential_id": qualification.credential_id,
            "qualification_credential_digest": qualification.credential_digest,
            "subject_identity_id": subject_binding.subject_identity_id,
            "subject_binding_digest": sb_digest,
            "decision": decision_str,
            "reason_code": reason_code,
            "issued_at_unix_ms": clock.now_unix_ms,
        }
        decision_proto = AdmissionDecision(
            decision_id="",
            policy_id=semantic_payload["policy_id"],
            policy_digest=semantic_payload["policy_digest"],
            qualification_credential_id=semantic_payload["qualification_credential_id"],
            qualification_credential_digest=semantic_payload["qualification_credential_digest"],
            subject_identity_id=semantic_payload["subject_identity_id"],
            subject_binding_digest=semantic_payload["subject_binding_digest"],
            decision=semantic_payload["decision"],
            reason_code=semantic_payload["reason_code"],
            issued_at_unix_ms=semantic_payload["issued_at_unix_ms"],
            decision_digest="",
        )
        decision, _ = compute_id_and_digest(
            decision_proto,
            semantic_fields=semantic_payload,
            id_prefix="ad",
            id_salt=(sb_digest, qualification.credential_digest, res.policy.policy_digest),
        )
        sig = sign_ed25519(self.r12_priv, decision.signature_domain, artifact_payload(decision))
        decision = with_signature(decision, sig)

        # Credential
        credential: Optional[AdmissionCredential] = None
        if decision_str == "GRANTED":
            issued_at = clock.now_unix_ms
            # FR-8: lifetime is configurable per-case (env ATE_ADMISSION_LIFETIME_MS).
            import os as _os
            default_adm_lifetime = int(_os.environ.get("ATE_ADMISSION_LIFETIME_MS", str(12 * 3600 * 1000)))
            adm_lifetime_ms = admission_lifetime_ms if admission_lifetime_ms is not None else default_adm_lifetime
            expires_at = issued_at + int(adm_lifetime_ms)
            semantic_payload = {
                "policy_id": res.policy.policy_id,
                "policy_digest": res.policy.policy_digest,
                "qualification_credential_id": qualification.credential_id,
                "qualification_credential_digest": qualification.credential_digest,
                "subject_identity_id": subject_binding.subject_identity_id,
                "subject_binding_digest": sb_digest,
                "issued_at_unix_ms": issued_at,
                "expires_at_unix_ms": expires_at,
                "historical_trust_state_reference": snapshot_reference,
            }
            cred_proto = AdmissionCredential(
                credential_id="",
                policy_id=semantic_payload["policy_id"],
                policy_digest=semantic_payload["policy_digest"],
                qualification_credential_id=semantic_payload["qualification_credential_id"],
                qualification_credential_digest=semantic_payload["qualification_credential_digest"],
                subject_identity_id=semantic_payload["subject_identity_id"],
                subject_binding_digest=semantic_payload["subject_binding_digest"],
                issued_at_unix_ms=semantic_payload["issued_at_unix_ms"],
                expires_at_unix_ms=semantic_payload["expires_at_unix_ms"],
                historical_trust_state_reference=semantic_payload["historical_trust_state_reference"],
                credential_digest="",
            )
            credential, _ = compute_id_and_digest(
                cred_proto,
                semantic_fields=semantic_payload,
                id_prefix="ac",
                id_salt=(sb_digest, qualification.credential_digest, res.policy.policy_digest),
            )
            sig = sign_ed25519(self.r12_priv, credential.signature_domain, artifact_payload(credential))
            credential = with_signature(credential, sig)

        return manifest, decision, credential

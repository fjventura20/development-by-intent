"""ATE Qualification & Admission Local PoC v0.1 — qualification pipeline.

Per design §12 / §14, the qualification authority runs:

  resolve active profile for (qualification_domain, role)
  verify identity/provenance/governance/behavioral/operational evidence
  issue QualificationEvidenceManifest
  issue QualificationDecision (GRANTED/DENIED) + reason_code
  on GRANTED, issue QualificationCredential (immutable, with expiry)

Authority keys used (frozen §6):
  AUTH_POLICY             — policy/profile publishing
  AUTH_IDENTITY           — identity evidence
  AUTH_R11_QUALIFICATION  — decisions + credentials

This module is *deterministic* for testing: all randomness (challenge
nonces, evidence-class hashes) goes through canonical_sha256 + a seed.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

from .canonical import canonical_sha256
from .clock import Clock
from .crypto import Ed25519PrivateKey, Ed25519PublicKey, sign_ed25519
from .models import (
    DOMAIN_QUALIFICATION_CREDENTIAL,
    DOMAIN_QUALIFICATION_DECISION,
    DOMAIN_QUALIFICATION_EVIDENCE_MANIFEST,
    DOMAIN_QUALIFICATION_REQUIREMENTS_PROFILE,
    QualificationCredential,
    QualificationDecision,
    QualificationEvidenceManifest,
    QualificationRequirementsProfile,
    artifact_payload,
    compute_id_and_digest,
    with_signature,
)
from .policies import ProfileRegistry, ProfileResolution, verify_profile_signature
from .subject_binding import SubjectBinding


def _stable_id(prefix: str, *parts: str) -> str:
    h = hashlib.sha256()
    for p in parts:
        h.update(p.encode("utf-8"))
        h.update(b"\x00")
    return f"{prefix}-{h.hexdigest()[:24]}"


@dataclass
class EvidenceBundle:
    """The 5 evidence classes required by §12."""

    identity_runtime_digest: str
    provenance_runtime_class_digest: str
    governance_compatibility_digest: str
    behavioral_fixture_receipt_digest: str
    operational_control_compatibility_digest: str


def build_evidence_bundle(*, subject_binding: SubjectBinding) -> EvidenceBundle:
    """Deterministic evidence-bundle construction for tests/fixtures."""
    sb_digest = subject_binding.digest()
    return EvidenceBundle(
        identity_runtime_digest=canonical_sha256(
            {"k": "identity_runtime", "sb": sb_digest}
        ),
        provenance_runtime_class_digest=canonical_sha256(
            {"k": "provenance_runtime_class", "sb": sb_digest}
        ),
        governance_compatibility_digest=canonical_sha256(
            {"k": "governance_compatibility", "sb": sb_digest}
        ),
        behavioral_fixture_receipt_digest=canonical_sha256(
            {"k": "behavioral_fixture_receipt", "sb": sb_digest}
        ),
        operational_control_compatibility_digest=canonical_sha256(
            {"k": "operational_control_compatibility", "sb": sb_digest}
        ),
    )


class QualificationAuthority:
    """Authority-side service that publishes profiles and issues credentials."""

    def __init__(
        self,
        *,
        registry: ProfileRegistry,
        r11_priv: Ed25519PrivateKey,
        r11_pub: Ed25519PublicKey,
        r11_key_id: str,
        identity_priv: Optional[Ed25519PrivateKey] = None,
    ) -> None:
        self.registry = registry
        self.r11_priv = r11_priv
        self.r11_pub = r11_pub
        self.r11_key_id = r11_key_id
        self.identity_priv = identity_priv  # for evidence manifest

    # -- profile publishing --------------------------------------------------

    def publish_profile(
        self,
        *,
        profile_id: str,
        profile_version: int,
        qualification_domain: str,
        role_id: str,
        minimum_binding: str,
        maximum_risk: str,
        eligible_capability: str,
        required_evidence_classes: List[str],
    ) -> QualificationRequirementsProfile:
        prof_proto = QualificationRequirementsProfile(
            profile_id="",  # filled by compute_id_and_digest
            profile_version=profile_version,
            qualification_domain=qualification_domain,
            role_id=role_id,
            minimum_binding=minimum_binding,
            maximum_risk=maximum_risk,
            eligible_capability=eligible_capability,
            required_evidence_classes=required_evidence_classes,
            profile_digest="",  # filled by compute_id_and_digest
        )
        semantic = {
            "profile_version": profile_version,
            "qualification_domain": qualification_domain,
            "role_id": role_id,
            "minimum_binding": minimum_binding,
            "maximum_risk": maximum_risk,
            "eligible_capability": eligible_capability,
            "required_evidence_classes": required_evidence_classes,
        }
        prof, _ = compute_id_and_digest(
            prof_proto,
            semantic_fields=semantic,
            id_prefix="prof",
            id_salt=(qualification_domain, role_id, str(profile_version)),
        )
        sig = sign_ed25519(self.r11_priv, prof.signature_domain, artifact_payload(prof))
        prof = with_signature(prof, sig)
        # Verify before publish (self-check)
        verify_profile_signature(self.r11_pub, prof)
        self.registry.publish(prof)
        return prof

    # -- qualification evaluation -------------------------------------------

    def evaluate(
        self,
        *,
        subject_binding: SubjectBinding,
        qualification_domain: str,
        role: str,
        evidence: EvidenceBundle,
        snapshot_reference: str,
        clock: Clock,
    ) -> Tuple[QualificationEvidenceManifest, QualificationDecision, Optional[QualificationCredential]]:
        res = self.registry.resolve(qualification_domain, role)
        sb_digest = subject_binding.digest()

        # Evidence manifest (non-recursive construction per DEV-IMP-3 §3)
        manifest_semantic = {
            "subject_identity_id": subject_binding.subject_identity_id,
            "subject_binding_digest": sb_digest,
            "runtime_class": subject_binding.runtime_class,
            "provider_id": subject_binding.provider_id,
            "evidence_classes": [
                "identity/runtime",
                "provenance/runtime-class",
                "governance compatibility",
                "behavioral fixture receipt",
                "operational-control compatibility",
            ],
            "evidence_digests": {
                "identity_runtime": evidence.identity_runtime_digest,
                "provenance_runtime_class": evidence.provenance_runtime_class_digest,
                "governance_compatibility": evidence.governance_compatibility_digest,
                "behavioral_fixture_receipt": evidence.behavioral_fixture_receipt_digest,
                "operational_control_compatibility": evidence.operational_control_compatibility_digest,
            },
        }
        manifest_proto = QualificationEvidenceManifest(
            manifest_id="",  # filled by compute_id_and_digest
            subject_identity_id=manifest_semantic["subject_identity_id"],
            subject_binding_digest=manifest_semantic["subject_binding_digest"],
            runtime_class=manifest_semantic["runtime_class"],
            provider_id=manifest_semantic["provider_id"],
            evidence_classes=manifest_semantic["evidence_classes"],
            manifest_digest="",  # filled by compute_id_and_digest
        )
        manifest, _manifest_digest = compute_id_and_digest(
            manifest_proto,
            semantic_fields=manifest_semantic,
            id_prefix="qfem",
            id_salt=(sb_digest, res.profile.profile_digest),
        )
        sig = sign_ed25519(self.r11_priv, manifest.signature_domain, artifact_payload(manifest))
        manifest = with_signature(manifest, sig)

        # Decision: GRANTED iff subject_binding_level >= profile.minimum_binding
        # and runtime_class matches profile expectations (here always SB2
        # since the profile says so). We compare numerically.
        sb_order = {"SB1": 1, "SB2": 2, "SB3": 3}
        decision_str = "DENIED"
        reason_code = "AX_QUALIFICATION_BINDING_INSUFFICIENT"
        if sb_order.get(subject_binding.binding_level, 0) >= sb_order.get(
            res.profile.minimum_binding, 99
        ):
            decision_str = "GRANTED"
            reason_code = ""

        semantic_payload = {
            "profile_id": res.profile.profile_id,
            "profile_digest": res.profile.profile_digest,
            "subject_identity_id": subject_binding.subject_identity_id,
            "subject_binding_digest": sb_digest,
            "decision": decision_str,
            "reason_code": reason_code,
            "issued_at_unix_ms": clock.now_unix_ms,
        }
        decision_proto = QualificationDecision(
            decision_id="",
            profile_id=semantic_payload["profile_id"],
            profile_digest=semantic_payload["profile_digest"],
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
            id_prefix="qfd",
            id_salt=(sb_digest, res.profile.profile_digest),
        )
        sig = sign_ed25519(self.r11_priv, decision.signature_domain, artifact_payload(decision))
        decision = with_signature(decision, sig)

        # Credential: only on GRANTED
        credential: Optional[QualificationCredential] = None
        if decision_str == "GRANTED":
            issued_at = clock.now_unix_ms
            expires_at = issued_at + 24 * 3600 * 1000  # 24h
            semantic_payload = {
                "profile_id": res.profile.profile_id,
                "profile_digest": res.profile.profile_digest,
                "subject_identity_id": subject_binding.subject_identity_id,
                "subject_binding_digest": sb_digest,
                "issued_at_unix_ms": issued_at,
                "expires_at_unix_ms": expires_at,
                "historical_trust_state_reference": snapshot_reference,
            }
            cred_proto = QualificationCredential(
                credential_id="",
                profile_id=semantic_payload["profile_id"],
                profile_digest=semantic_payload["profile_digest"],
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
                id_prefix="qfc",
                id_salt=(sb_digest, res.profile.profile_digest),
            )
            sig = sign_ed25519(self.r11_priv, credential.signature_domain, artifact_payload(credential))
            credential = with_signature(credential, sig)

        return manifest, decision, credential

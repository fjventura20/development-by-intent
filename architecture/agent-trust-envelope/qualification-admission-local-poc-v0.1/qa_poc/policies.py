"""ATE Qualification & Admission Local PoC v0.1 — authoritative profile/policy resolution.

Per design §11: candidate input cannot choose the controlling policy.

  Qualification authority resolves:
    (qualification_domain, role) -> active QualificationRequirementsProfile

  Admission authority resolves:
    (trust_domain, role) -> active AdmissionPolicy

The authority holds a registry of profiles/policies indexed by
(qualification_domain, role) and (trust_domain, role) respectively.
The caller passes candidate input as a *consistency assertion*; it
cannot override or downgrade the active profile/policy.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Optional, Tuple

from .canonical import canonical_sha256
from .crypto import (
    Ed25519PublicKey,
    verify_ed25519,
)
from .models import (
    AdmissionPolicy,
    DOMAIN_ADMISSION_POLICY,
    DOMAIN_QUALIFICATION_REQUIREMENTS_PROFILE,
    QualificationRequirementsProfile,
    artifact_payload,
    verify_artifact,
)


@dataclass
class ProfileResolution:
    profile: QualificationRequirementsProfile
    digest: str


@dataclass
class PolicyResolution:
    policy: AdmissionPolicy
    digest: str


class ProfileRegistry:
    """Authority-side registry of QualificationRequirementsProfiles.

    Indexed by (qualification_domain, role). Exactly one active profile
    per key. Adding a new profile with the same key SUPPERSEDES the old
    one — the old profile remains in history for credential binding but
    is no longer active.
    """

    def __init__(self) -> None:
        self._by_key: Dict[Tuple[str, str], QualificationRequirementsProfile] = {}
        self._supersedes: Dict[Tuple[str, str], list] = {}

    def publish(self, profile: QualificationRequirementsProfile) -> None:
        key = (profile.qualification_domain, profile.role_id)
        prior = self._by_key.get(key)
        if prior is not None:
            self._supersedes.setdefault(key, []).append(prior)
        self._by_key[key] = profile

    def resolve(self, qualification_domain: str, role: str) -> ProfileResolution:
        key = (qualification_domain, role)
        p = self._by_key.get(key)
        if p is None:
            raise KeyError(f"no active profile for {key}")
        return ProfileResolution(profile=p, digest=p.profile_digest)

    def assert_consistency(
        self,
        candidate_profile_id: str,
        candidate_profile_digest: str,
        qualification_domain: str,
        role: str,
    ) -> ProfileResolution:
        """Caller asserts what they think the active profile is. The
        registry MUST reject if it does not match the active profile.

        Candidate-supplied IDs/digests are consistency assertions only;
        they CANNOT downgrade or override the active profile.
        """
        res = self.resolve(qualification_domain, role)
        if (
            res.profile.profile_id != candidate_profile_id
            or res.profile.profile_digest != candidate_profile_digest
        ):
            raise ValueError(
                f"candidate profile mismatch: active={res.profile.profile_id}"
                f"/{res.profile.profile_digest[:8]} candidate={candidate_profile_id}"
                f"/{candidate_profile_digest[:8]}"
            )
        return res


class PolicyRegistry:
    """Authority-side registry of AdmissionPolicies. Same model as ProfileRegistry."""

    def __init__(self) -> None:
        self._by_key: Dict[Tuple[str, str], AdmissionPolicy] = {}
        self._supersedes: Dict[Tuple[str, str], list] = {}

    def publish(self, policy: AdmissionPolicy) -> None:
        key = (policy.trust_domain, policy.role)
        prior = self._by_key.get(key)
        if prior is not None:
            self._supersedes.setdefault(key, []).append(prior)
        self._by_key[key] = policy

    def resolve(self, trust_domain: str, role: str) -> PolicyResolution:
        key = (trust_domain, role)
        p = self._by_key.get(key)
        if p is None:
            raise KeyError(f"no active policy for {key}")
        return PolicyResolution(policy=p, digest=p.policy_digest)

    def assert_consistency(
        self,
        candidate_policy_id: str,
        candidate_policy_digest: str,
        trust_domain: str,
        role: str,
    ) -> PolicyResolution:
        res = self.resolve(trust_domain, role)
        if (
            res.policy.policy_id != candidate_policy_id
            or res.policy.policy_digest != candidate_policy_digest
        ):
            raise ValueError(
                f"candidate policy mismatch: active={res.policy.policy_id}"
                f"/{res.policy.policy_digest[:8]} candidate={candidate_policy_id}"
                f"/{candidate_policy_digest[:8]}"
            )
        return res


# -- Verification helpers used at request time -------------------------------


def verify_profile_signature(
    pub: Ed25519PublicKey, profile: QualificationRequirementsProfile
) -> None:
    """Verify the profile signature under the qualification-domain
    artifact domain. Raises on failure."""
    verify_artifact(profile, pub)


def verify_policy_signature(
    pub: Ed25519PublicKey, policy: AdmissionPolicy
) -> None:
    verify_artifact(policy, pub)


def profile_matches_active(
    profile: QualificationRequirementsProfile,
    expected_profile_id: str,
    expected_profile_digest: str,
) -> bool:
    """Exact-recognition check (no `version >= N`)."""
    return (
        profile.profile_id == expected_profile_id
        and profile.profile_digest == expected_profile_digest
    )

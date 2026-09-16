"""ATE Qualification & Admission Local PoC v0.1 — SubjectBinding.

Per design §10:

    subject_identity_id: agent-a (or agent-b)
    runtime_class:       synthetic-runtime-v1
    provider_id:         local-fixture
    binding_level:       SB2

The SubjectBinding digest binds the five-field canonical tuple:

    (subject_identity_id, runtime_class, provider_id, binding_level, challenge)

Live proof (§10):

    Sign a fresh challenge bound to:
        subject_identity_id
        challenge
        runtime_class
        trust_domain
        role

The verifier reconstructs and compares the canonical SubjectBinding digest.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from .canonical import canonical_sha256


@dataclass(frozen=True)
class SubjectBinding:
    subject_identity_id: str
    runtime_class: str
    provider_id: str
    binding_level: str  # SB1/SB2/SB3
    challenge: str  # fresh per attempt

    def digest(self) -> str:
        payload = {
            "binding_level": self.binding_level,
            "challenge": self.challenge,
            "provider_id": self.provider_id,
            "runtime_class": self.runtime_class,
            "subject_identity_id": self.subject_identity_id,
        }
        return canonical_sha256(payload)


def fresh_challenge(seed: str, nonce_counter: int) -> str:
    """Deterministic challenge derivation for tests.

    Production would use crypto-grade randomness; here we keep it
    deterministic so QA-P7 can construct distinguishable challenges
    without sleep() or RNG re-seeding.
    """
    return f"challenge:{seed}:{nonce_counter}"


def verify_live_proof(
    *,
    agent_subject_binding: SubjectBinding,
    trust_domain: str,
    role: str,
    live_proof_signature_bytes: bytes,
    verifier_public_key,
    signing_domain: str,
    live_proof_canonical_payload: dict,
) -> bool:
    """Verify a live proof signature bound to:

        subject_identity_id, challenge, runtime_class, trust_domain, role

    The signature was produced by the agent's identity private key over
    a canonical payload containing exactly those fields.
    """
    # Reconstruct the canonical challenge tuple and verify the digest matches
    expected = {
        "challenge": agent_subject_binding.challenge,
        "role": role,
        "runtime_class": agent_subject_binding.runtime_class,
        "subject_identity_id": agent_subject_binding.subject_identity_id,
        "trust_domain": trust_domain,
    }
    expected_digest = canonical_sha256(expected)
    actual_digest = canonical_sha256(live_proof_canonical_payload)
    if actual_digest != expected_digest:
        return False
    # Now verify the signature over the canonical payload
    from .crypto import verify_ed25519

    verify_ed25519(
        verifier_public_key,
        live_proof_signature_bytes,
        signing_domain,
        live_proof_canonical_payload,
    )
    return True

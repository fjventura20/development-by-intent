"""ATE Qualification & Admission Local PoC v0.1 — action authorization.

Per design §21 / §22:
  CapabilityToken — binds subject_binding + qualification + admission IDs/digests
                    + session + operation + target + parameters + nonce + …
                    signed by AUTH_AUTHORIZATION
  TrustDecision   — same eligibility chain + capability_token_id + action_digest
                    + verdict + historical reference; signed by AUTH_TRUST_DECISION
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from typing import Callable, Optional, Tuple

from .admission import AdmissionCredential, QualificationCredential
from .canonical import canonical_sha256
from .clock import Clock
from .crypto import Ed25519PrivateKey, Ed25519PublicKey, sign_ed25519
from .models import (
    DOMAIN_CAPABILITY_TOKEN,
    DOMAIN_TRUST_DECISION,
    CapabilityToken,
    TrustDecision,
    artifact_payload,
    compute_id_and_digest,
    with_signature,
)
from .subject_binding import SubjectBinding


def _stable_id(prefix: str, *parts: str) -> str:
    h = hashlib.sha256()
    for p in parts:
        h.update(p.encode("utf-8"))
        h.update(b"\x00")
    return f"{prefix}-{h.hexdigest()[:24]}"


def parameters_digest(parameters: dict) -> str:
    return canonical_sha256(parameters)


def action_digest(*, target: str, operation: str, parameters: dict) -> str:
    return canonical_sha256(
        {"target": target, "operation": operation, "parameters": parameters}
    )


class AuthorizationAuthority:
    """Authority-side service that issues CapabilityTokens + TrustDecisions.

    Keys (frozen §6):
      AUTH_AUTHORIZATION     — CapabilityToken
      AUTH_TRUST_DECISION    — TrustDecision
    """

    def __init__(
        self,
        *,
        auth_priv: Ed25519PrivateKey,
        auth_pub: Ed25519PublicKey,
        auth_key_id: str,
        trust_priv: Ed25519PrivateKey,
        trust_pub: Ed25519PublicKey,
        trust_key_id: str,
    ) -> None:
        self.auth_priv = auth_priv
        self.auth_pub = auth_pub
        self.auth_key_id = auth_key_id
        self.trust_priv = trust_priv
        self.trust_pub = trust_pub
        self.trust_key_id = trust_key_id

    def issue_capability_token(
        self,
        *,
        subject_binding: SubjectBinding,
        qualification: QualificationCredential,
        admission: AdmissionCredential,
        session_identity: str,
        operation: str,
        target: str,
        parameters: dict,
        risk_class: str,
        capability_class: str,
        nonce: str,
        snapshot_reference: str,
        clock: Clock,
        revocation_lookup: Optional[Callable[[str], Tuple[bool, str]]] = None,
        qualification_revocation_lookup: Optional[Callable[[str], Tuple[bool, str]]] = None,
        capability_lifetime_ms: Optional[int] = None,
    ) -> "CapabilityToken | None":
        """Issue a new CapabilityToken bound to the (qualification,
        admission) pair.

        Per frozen §19, recursive eligibility is evaluated AT ISSUANCE
        TIME: both the bound qualification and the bound admission
        must be currently usable (not revoked, not expired). When
        `revocation_lookup` or `qualification_revocation_lookup` are
        provided, this check is enforced. If either bound artifact is
        unusable, NO CapabilityToken is issued (returns None).

        The TrustDecision issuance is also a downstream consumer of
        the same constraint: if no CapabilityToken is issued, no
        TrustDecision is issued either.
        """
        from .admission import check_admission_usable, DependencyEvaluationError
        from .qualification import check_qualification_usable

        # Pre-issuance: admission must be present, qualified must be present.
        if admission is None:
            return None
        if qualification is None:
            return None

        if revocation_lookup is not None:
            try:
                check_admission_usable(
                    admission=admission,
                    clock=clock,
                    qualification=qualification,
                    revocation_lookup=revocation_lookup,
                )
            except DependencyEvaluationError:
                return None
        if qualification_revocation_lookup is not None:
            try:
                check_qualification_usable(
                    qualification=qualification,
                    clock=clock,
                    revocation_lookup=qualification_revocation_lookup,
                )
            except DependencyEvaluationError:
                return None

        sb_digest = subject_binding.digest()
        params_d = parameters_digest(parameters)
        issued_at = clock.now_unix_ms
        # FR-8: TTL is configurable per-case for deterministic isolation.
        # Production default is 1 hour; tests can override via this
        # parameter (or env var ATE_CAPABILITY_LIFETIME_MS).
        import os as _os
        default_cap_lifetime = int(_os.environ.get("ATE_CAPABILITY_LIFETIME_MS", str(3600 * 1000)))
        cap_lifetime_ms = capability_lifetime_ms if capability_lifetime_ms is not None else default_cap_lifetime
        expires_at = issued_at + int(cap_lifetime_ms)

        # DEV-IMP-3 non-recursive construction
        semantic_payload = {
            "subject_binding_digest": sb_digest,
            "qualification_credential_id": qualification.credential_id,
            "qualification_credential_digest": qualification.credential_digest,
            "admission_credential_id": admission.credential_id,
            "admission_credential_digest": admission.credential_digest,
            "session_identity": session_identity,
            "operation": operation,
            "target": target,
            "parameters_digest": params_d,
            "risk_class": risk_class,
            "capability_class": capability_class,
            "nonce": nonce,
            "issued_at_unix_ms": issued_at,
            "expires_at_unix_ms": expires_at,
            "historical_trust_state_reference": snapshot_reference,
        }
        token_proto = CapabilityToken(
            token_id="",
            subject_binding_digest=semantic_payload["subject_binding_digest"],
            qualification_credential_id=semantic_payload["qualification_credential_id"],
            qualification_credential_digest=semantic_payload["qualification_credential_digest"],
            admission_credential_id=semantic_payload["admission_credential_id"],
            admission_credential_digest=semantic_payload["admission_credential_digest"],
            session_identity=semantic_payload["session_identity"],
            operation=semantic_payload["operation"],
            target=semantic_payload["target"],
            parameters_digest=semantic_payload["parameters_digest"],
            risk_class=semantic_payload["risk_class"],
            capability_class=semantic_payload["capability_class"],
            nonce=semantic_payload["nonce"],
            issued_at_unix_ms=semantic_payload["issued_at_unix_ms"],
            expires_at_unix_ms=semantic_payload["expires_at_unix_ms"],
            historical_trust_state_reference=semantic_payload["historical_trust_state_reference"],
            token_digest="",
        )
        token, _ = compute_id_and_digest(
            token_proto,
            semantic_fields=semantic_payload,
            id_prefix="ct",
            id_salt=(sb_digest, nonce),
        )
        sig = sign_ed25519(self.auth_priv, token.signature_domain, artifact_payload(token))
        token = with_signature(token, sig)
        return token

    def issue_trust_decision(
        self,
        *,
        capability: CapabilityToken,
        requested_action: dict,
        verdict: str,
        snapshot_reference: str,
        clock: Clock,
        trust_decision_lifetime_ms: Optional[int] = None,
    ) -> TrustDecision:
        a_digest = action_digest(
            target=capability.target,
            operation=capability.operation,
            parameters=requested_action.get("parameters", {}),
        )
        issued_at = clock.now_unix_ms
        # FR-8: TTL configurable per-case (env ATE_TRUST_DECISION_LIFETIME_MS).
        import os as _os
        default_td_lifetime = int(_os.environ.get("ATE_TRUST_DECISION_LIFETIME_MS", str(5 * 60 * 1000)))
        td_lifetime_ms = trust_decision_lifetime_ms if trust_decision_lifetime_ms is not None else default_td_lifetime
        expires_at = issued_at + int(td_lifetime_ms)

        semantic_payload = {
            "capability_token_id": capability.token_id,
            "capability_token_digest": capability.token_digest,
            "requested_action_digest": a_digest,
            "verdict": verdict,
            "issued_at_unix_ms": issued_at,
            "expires_at_unix_ms": expires_at,
            "historical_trust_state_reference": snapshot_reference,
        }
        td_proto = TrustDecision(
            trust_decision_id="",
            capability_token_id=semantic_payload["capability_token_id"],
            capability_token_digest=semantic_payload["capability_token_digest"],
            requested_action_digest=semantic_payload["requested_action_digest"],
            verdict=semantic_payload["verdict"],
            issued_at_unix_ms=semantic_payload["issued_at_unix_ms"],
            expires_at_unix_ms=semantic_payload["expires_at_unix_ms"],
            historical_trust_state_reference=semantic_payload["historical_trust_state_reference"],
            trust_decision_digest="",
        )
        td, _ = compute_id_and_digest(
            td_proto,
            semantic_fields=semantic_payload,
            id_prefix="td",
            id_salt=(capability.token_digest,),
        )
        sig = sign_ed25519(self.trust_priv, td.signature_domain, artifact_payload(td))
        td = with_signature(td, sig)
        return td

"""Signing + artifact-domain separation self-tests (§8 + §9)."""

from __future__ import annotations

import pytest

from qa_poc.crypto import (
    generate_keypair,
    key_id_from_public_pem,
    sign_ed25519,
    verify_ed25519,
)
from qa_poc.models import (
    DOMAIN_CAPABILITY_TOKEN,
    DOMAIN_QUALIFICATION_CREDENTIAL,
    CapabilityToken,
    QualificationCredential,
    artifact_payload,
)
from cryptography.exceptions import InvalidSignature


def test_sign_verify_round_trip():
    priv, pub = generate_keypair()
    payload = {"a": 1, "b": [1, 2, 3]}
    sig = sign_ed25519(priv, "test.domain.v1", payload)
    assert verify_ed25519(pub, sig, "test.domain.v1", payload) is True


def test_wrong_domain_verification_fails():
    priv, pub = generate_keypair()
    payload = {"a": 1}
    sig = sign_ed25519(priv, "domain.A", payload)
    with pytest.raises(InvalidSignature):
        verify_ed25519(pub, sig, "domain.B", payload)


def test_payload_mutation_verification_fails():
    priv, pub = generate_keypair()
    sig = sign_ed25519(priv, "test.domain", {"a": 1})
    with pytest.raises(InvalidSignature):
        verify_ed25519(pub, sig, "test.domain", {"a": 2})


def test_key_id_stability():
    priv, pub = generate_keypair()
    pem = pub.public_bytes(
        __import__("cryptography.hazmat.primitives", fromlist=["serialization"]).serialization.Encoding.PEM,
        __import__("cryptography.hazmat.primitives", fromlist=["serialization"]).serialization.PublicFormat.SubjectPublicKeyInfo,
    )
    kid1 = key_id_from_public_pem(pem)
    kid2 = key_id_from_public_pem(pem)
    assert kid1 == kid2
    assert len(kid1) == 64  # SHA-256 hex


def test_artifact_payload_excludes_signature():
    """The signing payload must NOT include the signature field, but it
    MUST include the artifact's own id + digest + all semantic fields
    (per DEV-IMP-3 non-recursive construction)."""
    obj = CapabilityToken(
        token_id="t1",
        subject_binding_digest="x",
        qualification_credential_id="q",
        qualification_credential_digest="y",
        admission_credential_id="a",
        admission_credential_digest="z",
        session_identity="s",
        operation="op",
        target="t",
        parameters_digest="p",
        risk_class="R2",
        capability_class="demo-resource-write",
        nonce="nonce1",
        issued_at_unix_ms=1,
        expires_at_unix_ms=2,
        historical_trust_state_reference="snap",
        token_digest="d",
    )
    p = artifact_payload(obj)
    assert "signature" not in p
    # Per DEV-IMP-3: signing payload INCLUDES own_id + own_digest
    assert "token_id" in p
    assert "token_digest" in p
    # Other semantic fields ARE present
    assert p["subject_binding_digest"] == "x"
    assert p["nonce"] == "nonce1"


# -- DEV-IMP-3 deterministic mutation tests (ChatGPT review) ----------------


def test_dev_imp3_id_mutation_is_detected():
    """Changing the artifact id after issuance must cause verify_artifact
    to raise (DigestMismatchError, because digest binds id)."""
    from dataclasses import replace

    from qa_poc.crypto import generate_keypair, sign_ed25519
    from qa_poc.models import (
        DOMAIN_QUALIFICATION_CREDENTIAL,
        DigestMismatchError,
        compute_id_and_digest,
        verify_artifact,
    )

    priv, pub = generate_keypair()
    proto = QualificationCredential(
        credential_id="",
        profile_id="prof-1",
        profile_digest="pd-1",
        subject_identity_id="agent-a",
        subject_binding_digest="sb-1",
        issued_at_unix_ms=1000,
        expires_at_unix_ms=2000,
        historical_trust_state_reference="snap",
        credential_digest="",
    )
    semantic = {
        "profile_id": "prof-1",
        "profile_digest": "pd-1",
        "subject_identity_id": "agent-a",
        "subject_binding_digest": "sb-1",
        "issued_at_unix_ms": 1000,
        "expires_at_unix_ms": 2000,
        "historical_trust_state_reference": "snap",
    }
    cred, _ = compute_id_and_digest(proto, semantic_fields=semantic, id_prefix="qfc", id_salt=("sb-1",))
    sig = sign_ed25519(priv, DOMAIN_QUALIFICATION_CREDENTIAL, artifact_payload(cred))
    cred = cred.__class__(**{**cred.__dict__, "signature": sig})

    # Verification with original id passes
    verify_artifact(cred, pub)

    # Tamper: change credential_id after issuance
    tampered = replace(cred, credential_id="qfc-TAMPERED")
    with pytest.raises(DigestMismatchError):
        verify_artifact(tampered, pub)


def test_dev_imp3_self_digest_mutation_is_detected():
    """Changing the artifact's self-digest must cause verify_artifact
    to raise (DigestMismatchError on recompute)."""
    from dataclasses import replace

    from qa_poc.crypto import generate_keypair, sign_ed25519
    from qa_poc.models import (
        DOMAIN_QUALIFICATION_CREDENTIAL,
        DigestMismatchError,
        SignatureError,
        compute_id_and_digest,
        verify_artifact,
    )

    priv, pub = generate_keypair()
    proto = QualificationCredential(
        credential_id="",
        profile_id="prof-1",
        profile_digest="pd-1",
        subject_identity_id="agent-a",
        subject_binding_digest="sb-1",
        issued_at_unix_ms=1000,
        expires_at_unix_ms=2000,
        historical_trust_state_reference="snap",
        credential_digest="",
    )
    semantic = {
        "profile_id": "prof-1",
        "profile_digest": "pd-1",
        "subject_identity_id": "agent-a",
        "subject_binding_digest": "sb-1",
        "issued_at_unix_ms": 1000,
        "expires_at_unix_ms": 2000,
        "historical_trust_state_reference": "snap",
    }
    cred, _ = compute_id_and_digest(proto, semantic_fields=semantic, id_prefix="qfc", id_salt=("sb-1",))
    sig = sign_ed25519(priv, DOMAIN_QUALIFICATION_CREDENTIAL, artifact_payload(cred))
    cred = cred.__class__(**{**cred.__dict__, "signature": sig})

    verify_artifact(cred, pub)

    # Tamper: change credential_digest
    tampered = replace(cred, credential_digest="0" * 64)
    with pytest.raises((DigestMismatchError, SignatureError)):
        verify_artifact(tampered, pub)


def test_dev_imp3_semantic_field_mutation_is_detected():
    """Changing a semantic security field must cause verify_artifact to
    raise (either DigestMismatchError or SignatureError)."""
    from dataclasses import replace

    from qa_poc.crypto import generate_keypair, sign_ed25519
    from qa_poc.models import (
        DOMAIN_QUALIFICATION_CREDENTIAL,
        DigestMismatchError,
        SignatureError,
        compute_id_and_digest,
        verify_artifact,
    )

    priv, pub = generate_keypair()
    proto = QualificationCredential(
        credential_id="",
        profile_id="prof-1",
        profile_digest="pd-1",
        subject_identity_id="agent-a",
        subject_binding_digest="sb-1",
        issued_at_unix_ms=1000,
        expires_at_unix_ms=2000,
        historical_trust_state_reference="snap",
        credential_digest="",
    )
    semantic = {
        "profile_id": "prof-1",
        "profile_digest": "pd-1",
        "subject_identity_id": "agent-a",
        "subject_binding_digest": "sb-1",
        "issued_at_unix_ms": 1000,
        "expires_at_unix_ms": 2000,
        "historical_trust_state_reference": "snap",
    }
    cred, _ = compute_id_and_digest(proto, semantic_fields=semantic, id_prefix="qfc", id_salt=("sb-1",))
    sig = sign_ed25519(priv, DOMAIN_QUALIFICATION_CREDENTIAL, artifact_payload(cred))
    cred = cred.__class__(**{**cred.__dict__, "signature": sig})

    verify_artifact(cred, pub)

    # Tamper: change subject_identity_id (a semantic field)
    tampered = replace(cred, subject_identity_id="agent-X")
    with pytest.raises((DigestMismatchError, SignatureError)):
        verify_artifact(tampered, pub)


def test_dev_imp3_equivalent_canonical_form_has_same_digest():
    """Re-ordered keys with the same semantic content must produce the
    same digest (the canonicalizer enforces key ordering)."""
    from dataclasses import replace

    from qa_poc.crypto import generate_keypair, sign_ed25519
    from qa_poc.models import (
        DOMAIN_QUALIFICATION_CREDENTIAL,
        compute_id_and_digest,
        verify_artifact,
    )
    from qa_poc.canonical import canonical_sha256
    from qa_poc.models import digest_payload

    priv, pub = generate_keypair()
    proto = QualificationCredential(
        credential_id="",
        profile_id="prof-1",
        profile_digest="pd-1",
        subject_identity_id="agent-a",
        subject_binding_digest="sb-1",
        issued_at_unix_ms=1000,
        expires_at_unix_ms=2000,
        historical_trust_state_reference="snap",
        credential_digest="",
    )
    semantic_a = {
        "profile_id": "prof-1",
        "profile_digest": "pd-1",
        "subject_identity_id": "agent-a",
        "subject_binding_digest": "sb-1",
        "issued_at_unix_ms": 1000,
        "expires_at_unix_ms": 2000,
        "historical_trust_state_reference": "snap",
    }
    cred, _ = compute_id_and_digest(proto, semantic_fields=semantic_a, id_prefix="qfc", id_salt=("sb-1",))
    sig = sign_ed25519(priv, DOMAIN_QUALIFICATION_CREDENTIAL, artifact_payload(cred))
    cred = cred.__class__(**{**cred.__dict__, "signature": sig})

    # Digest-input payload produces a stable digest regardless of input dict ordering
    d_input_a = digest_payload(cred)
    d_input_b = dict(reversed(list(d_input_a.items())))
    assert canonical_sha256(d_input_a) == canonical_sha256(d_input_b)
    # And the credential's stored digest matches
    assert canonical_sha256({**d_input_a, "credential_id": cred.credential_id}) == cred.credential_digest

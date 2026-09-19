"""Deterministic Ed25519 authorities for reproducible PoC evidence.

TEST ONLY - NOT SECRET - NOT FOR PRODUCTION.
These seeds MUST NOT protect real resources.
"""

from __future__ import annotations

from types import MappingProxyType
from typing import Mapping

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

from conformance.canonical import canonical_sha256
from conformance.crypto import key_id_from_public_key

_LABELS = (
    "profile_signer",
    "qa_issuer",
    "runtime_observer",
    "r13_evaluator",
    "r14_authority",
    "authorization_service",
    "audit_recorder",
)

_AUTHORITY_METADATA = {
    "profile_signer": ("profile-signer-1", ("ate.conformance.profile.v1",)),
    "qa_issuer": (
        "qual-admission-issuer-1",
        ("ate.conformance.qualification_fixture.v1", "ate.conformance.admission_fixture.v1"),
    ),
    "runtime_observer": (
        "observer-1",
        ("ate.conformance.runtime_evidence.v1", "ate.conformance.trigger_observation.v1"),
    ),
    "r13_evaluator": ("r13-1", ("ate.conformance.r13_eval.v1",)),
    "r14_authority": ("r14-1", ("ate.conformance.r14_state.v1",)),
    "authorization_service": ("az-1", ("ate.conformance.capability.v1",)),
    "audit_recorder": ("audit-1", ("ate.conformance.audit.v1",)),
}

_TEST_ONLY_SEED_HEX = {
    "profile_signer": "ffbe9bc4ffe40839dca552978873015ef3a6d533aa11bb4e2dd830d7f824300b",
    "qa_issuer": "6dcb88636b2ad538ad7131cada238adeff89a95abdfe64da74f3c2ec63ca4ab0",
    "runtime_observer": "b063d6a12e54a794fda803fc2a7f5c1a656c77475866ea0a612f2418ce61e0e4",
    "r13_evaluator": "64cb2cfe1bf15ce2745f71e5c60c8646a51a9644bb373b84f119804329146b6a",
    "r14_authority": "4a95c391a69f00f031d0a4763154f0b6fe1d6a3eb7543027676ba6027044e9e1",
    "authorization_service": "6c4e955a93ef032658dc9003fd6fc9e58b150efc8bc1e1c577cd1ea2fe7bfec8",
    "audit_recorder": "e72b7a66a49ac35b7c4342df36079841d252d746f1b4a340b45a064fb9100003",
}


def _seed(label: str) -> bytes:
    return bytes.fromhex(_TEST_ONLY_SEED_HEX[label])


def load_test_authorities() -> Mapping[str, tuple[Ed25519PrivateKey, object]]:
    """Return fresh key objects derived from the seven public test seeds."""
    seeds = [_seed(label) for label in _LABELS]
    if len(set(seeds)) != len(seeds):
        raise RuntimeError("duplicate TEST-ONLY authority seed")
    pairs = {}
    for label in _LABELS:
        private = Ed25519PrivateKey.from_private_bytes(_seed(label))
        pairs[label] = (private, private.public_key())
    public_hexes = [public.public_bytes_raw().hex() for _private, public in pairs.values()]
    key_ids = [key_id_from_public_key(public) for _private, public in pairs.values()]
    authority_ids = [_AUTHORITY_METADATA[label][0] for label in _LABELS]
    if not (
        len(set(public_hexes)) == len(public_hexes)
        and len(set(key_ids)) == len(key_ids)
        and len(set(authority_ids)) == len(authority_ids)
    ):
        raise RuntimeError("duplicate TEST-ONLY authority identity material")
    return MappingProxyType(pairs)


def public_key_registry() -> dict:
    """Return the canonical public-only verification-key registry."""
    keys = load_test_authorities()
    entries = []
    for role in _LABELS:
        _private, public = keys[role]
        authority_id, domains = _AUTHORITY_METADATA[role]
        entries.append({
            "authority_role": role,
            "authority_id": authority_id,
            "key_algorithm": "Ed25519",
            "public_key_encoding": "raw-32-byte-hex",
            "public_key_hex": public.public_bytes_raw().hex(),
            "key_id_sha256": key_id_from_public_key(public),
            "permitted_signing_domains": list(domains),
            "test_only": True,
        })
    return {
        "schema": "ate.test-verification-key-registry.v1",
        "test_only": True,
        "entries": entries,
    }


def public_key_registry_digest() -> str:
    return canonical_sha256(public_key_registry())

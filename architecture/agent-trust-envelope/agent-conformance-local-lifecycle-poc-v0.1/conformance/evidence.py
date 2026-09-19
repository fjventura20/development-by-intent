"""Independent evidence serialization and closure verification.

The verifier consumes only bytes from an evidence directory and public keys
declared in that directory. It never imports fixture private keys and never
writes to the directory it verifies.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, is_dataclass
from pathlib import Path
from typing import Any
from xml.etree import ElementTree

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey

from .canonical import canonical_json_bytes, canonical_sha256, signing_bytes
from .crypto import key_id_from_public_key

EXPECTED_CASES = tuple(
    [f"TC-{number:02d}" for number in range(1, 19)]
    + [f"NS-{number:02d}" for number in range(1, 9)]
)

CASE_DEFINITIONS = {
    "TC-01": {
        "case_kind": "required",
        "title": "initial conformance establishment",
        "pytest_node_ids": ["tests/test_lifecycle.py::test_tc01_initial_conformance_establishment"],
        "evidence_refs": ["signed-artifacts.json"],
        "assertion_summary": "initial conformance establishment is proved by the named test and persisted evidence.",
    },
    "TC-02": {
        "case_kind": "required",
        "title": "initial authorized action",
        "pytest_node_ids": ["tests/test_lifecycle.py::test_tc02_initial_authorized_action"],
        "evidence_refs": ["02_initial_and_c0.json"],
        "assertion_summary": "initial authorized action is proved by the named test and persisted evidence.",
    },
    "TC-03": {
        "case_kind": "required",
        "title": "pre-mutation capability issuance",
        "pytest_node_ids": ["tests/test_lifecycle.py::test_tc03_capability_issuance_before_mutation"],
        "evidence_refs": ["03_invalidation_and_c1.json"],
        "assertion_summary": "pre-mutation capability issuance is proved by the named test and persisted evidence.",
    },
    "TC-04": {
        "case_kind": "required",
        "title": "runtime mutation",
        "pytest_node_ids": ["tests/test_lifecycle.py::test_tc04_runtime_mutation"],
        "evidence_refs": ["03_invalidation_and_c1.json"],
        "assertion_summary": "runtime mutation is proved by the named test and persisted evidence.",
    },
    "TC-05": {
        "case_kind": "required",
        "title": "independent trigger observation",
        "pytest_node_ids": ["tests/test_lifecycle.py::test_tc05_independent_trigger_observation"],
        "evidence_refs": ["03_invalidation_and_c1.json"],
        "assertion_summary": "independent trigger observation is proved by the named test and persisted evidence.",
    },
    "TC-06": {
        "case_kind": "required",
        "title": "lifecycle invalidation",
        "pytest_node_ids": ["tests/test_lifecycle.py::test_tc06_lifecycle_invalidation"],
        "evidence_refs": ["03_invalidation_and_c1.json"],
        "assertion_summary": "lifecycle invalidation is proved by the named test and persisted evidence.",
    },
    "TC-07": {
        "case_kind": "required",
        "title": "authorization denial while non-conformant",
        "pytest_node_ids": ["tests/test_lifecycle.py::test_tc07_new_authorization_denied_while_non_conformant"],
        "evidence_refs": ["03_invalidation_and_c1.json"],
        "assertion_summary": "authorization denial while non-conformant is proved by the named test and persisted evidence.",
    },
    "TC-08": {
        "case_kind": "required",
        "title": "stale C1 denial",
        "pytest_node_ids": ["tests/test_lifecycle.py::test_tc08_stale_c1_execution_denied"],
        "evidence_refs": ["03_invalidation_and_c1.json"],
        "assertion_summary": "stale C1 denial is proved by the named test and persisted evidence.",
    },
    "TC-09": {
        "case_kind": "required",
        "title": "stale C1 retry denial",
        "pytest_node_ids": ["tests/test_lifecycle.py::test_tc09_stale_c1_retry_denied"],
        "evidence_refs": ["03_invalidation_and_c1.json"],
        "assertion_summary": "stale C1 retry denial is proved by the named test and persisted evidence.",
    },
    "TC-10": {
        "case_kind": "required",
        "title": "predeclared profile v2 activation",
        "pytest_node_ids": ["tests/test_lifecycle.py::test_tc10_predeclared_profile_v2_activation"],
        "evidence_refs": ["04_fresh_evidence_and_restoration.json"],
        "assertion_summary": "predeclared profile v2 activation is proved by the named test and persisted evidence.",
    },
    "TC-11": {
        "case_kind": "required",
        "title": "fresh post-change evidence",
        "pytest_node_ids": ["tests/test_lifecycle.py::test_tc11_fresh_post_change_runtime_evidence"],
        "evidence_refs": ["04_fresh_evidence_and_restoration.json"],
        "assertion_summary": "fresh post-change evidence is proved by the named test and persisted evidence.",
    },
    "TC-12": {
        "case_kind": "required",
        "title": "R13 positive re-evaluation",
        "pytest_node_ids": ["tests/test_lifecycle.py::test_tc12_r13_positive_reevaluation"],
        "evidence_refs": ["04_fresh_evidence_and_restoration.json"],
        "assertion_summary": "R13 positive re-evaluation is proved by the named test and persisted evidence.",
    },
    "TC-13": {
        "case_kind": "required",
        "title": "R14 restoration",
        "pytest_node_ids": ["tests/test_lifecycle.py::test_tc13_r14_restoration"],
        "evidence_refs": ["04_fresh_evidence_and_restoration.json"],
        "assertion_summary": "R14 restoration is proved by the named test and persisted evidence.",
    },
    "TC-14": {
        "case_kind": "required",
        "title": "new C2 capability issuance",
        "pytest_node_ids": ["tests/test_lifecycle.py::test_tc14_new_capability_c2_issuance"],
        "evidence_refs": ["05_c2_and_replay.json"],
        "assertion_summary": "new C2 capability issuance is proved by the named test and persisted evidence.",
    },
    "TC-15": {
        "case_kind": "required",
        "title": "restored execution",
        "pytest_node_ids": ["tests/test_lifecycle.py::test_tc15_restored_execution"],
        "evidence_refs": ["05_c2_and_replay.json"],
        "assertion_summary": "restored execution is proved by the named test and persisted evidence.",
    },
    "TC-16": {
        "case_kind": "required",
        "title": "C2 replay denial",
        "pytest_node_ids": ["tests/test_lifecycle.py::test_tc16_replay_c2"],
        "evidence_refs": ["05_c2_and_replay.json"],
        "assertion_summary": "C2 replay denial is proved by the named test and persisted evidence.",
    },
    "TC-17": {
        "case_kind": "required",
        "title": "audit integrity and causal order",
        "pytest_node_ids": ["tests/test_lifecycle.py::test_tc17_audit_chain_verification_and_causal_order"],
        "evidence_refs": ["authoritative-audit-ledger.json"],
        "assertion_summary": "audit integrity and causal order is proved by the named test and persisted evidence.",
    },
    "TC-18": {
        "case_kind": "required",
        "title": "historical preservation",
        "pytest_node_ids": ["tests/test_lifecycle.py::test_tc18_historical_preservation"],
        "evidence_refs": ["authoritative-audit-ledger.json"],
        "assertion_summary": "historical preservation is proved by the named test and persisted evidence.",
    },
    "NS-01": {
        "case_kind": "negative",
        "title": "subject rollback rejected",
        "pytest_node_ids": ["tests/test_negative.py::test_ns01_subject_cannot_rollback_lifecycle_state"],
        "evidence_refs": ["authoritative-audit-ledger.json"],
        "assertion_summary": "subject rollback rejected is proved by the named test and persisted evidence.",
    },
    "NS-02": {
        "case_kind": "negative",
        "title": "direct resource mutation rejected",
        "pytest_node_ids": ["tests/test_negative.py::test_ns02_subject_cannot_mutate_protected_resource_directly"],
        "evidence_refs": ["05_c2_and_replay.json"],
        "assertion_summary": "direct resource mutation rejected is proved by the named test and persisted evidence.",
    },
    "NS-03": {
        "case_kind": "negative",
        "title": "forged trigger rejected",
        "pytest_node_ids": ["tests/test_negative.py::test_ns03_forged_trigger_rejected"],
        "evidence_refs": ["signed-artifacts.json"],
        "assertion_summary": "forged trigger rejected is proved by the named test and persisted evidence.",
    },
    "NS-04": {
        "case_kind": "negative",
        "title": "forged R13 evaluation rejected",
        "pytest_node_ids": ["tests/test_negative.py::test_ns04_forged_r13_evaluation_rejected"],
        "evidence_refs": ["signed-artifacts.json"],
        "assertion_summary": "forged R13 evaluation rejected is proved by the named test and persisted evidence.",
    },
    "NS-05": {
        "case_kind": "negative",
        "title": "forged R14 state rejected",
        "pytest_node_ids": ["tests/test_negative.py::test_ns05_forged_r14_state_rejected"],
        "evidence_refs": ["signed-artifacts.json"],
        "assertion_summary": "forged R14 state rejected is proved by the named test and persisted evidence.",
    },
    "NS-06": {
        "case_kind": "negative",
        "title": "capability action substitution rejected",
        "pytest_node_ids": ["tests/test_negative.py::test_ns06_capability_action_digest_substitution_rejected"],
        "evidence_refs": ["signed-artifacts.json"],
        "assertion_summary": "capability action substitution rejected is proved by the named test and persisted evidence.",
    },
    "NS-07": {
        "case_kind": "negative",
        "title": "capability epoch substitution rejected",
        "pytest_node_ids": ["tests/test_negative.py::test_ns07_capability_epoch_substitution_rejected"],
        "evidence_refs": ["signed-artifacts.json"],
        "assertion_summary": "capability epoch substitution rejected is proved by the named test and persisted evidence.",
    },
    "NS-08": {
        "case_kind": "negative",
        "title": "audit history mutation detected",
        "pytest_node_ids": ["tests/test_negative.py::test_ns08_audit_history_mutation_detected"],
        "evidence_refs": ["tampered-audit-ledger.json"],
        "assertion_summary": "audit history mutation detected is proved by the named test and persisted evidence.",
    },
}

CASE_NODE_IDS = {
    case_id: definition["pytest_node_ids"]
    for case_id, definition in CASE_DEFINITIONS.items()
}

EXPECTED_ROLES = {
    "profile_signer",
    "qa_issuer",
    "runtime_observer",
    "r13_evaluator",
    "r14_authority",
    "authorization_service",
    "audit_recorder",
}

EXPECTED_AUTHORITIES = {
    "profile_signer": ("profile-signer-1", "b84acf3c49618424608d3c93c7bcb2046db6f0e3a2557c4ccc1a7d74593d900e", ["ate.conformance.profile.v1"]),
    "qa_issuer": ("qual-admission-issuer-1", "b6c1a0deccca1eaa5e9fc23bb844d0e14d7961f0a22876d1eb2e7cb4ae54e15a", ["ate.conformance.qualification_fixture.v1", "ate.conformance.admission_fixture.v1"]),
    "runtime_observer": ("observer-1", "7350224bbb1d7957a52b133c44aaa5c5e44d42b5bbeba7272735dc259339c81c", ["ate.conformance.runtime_evidence.v1", "ate.conformance.trigger_observation.v1"]),
    "r13_evaluator": ("r13-1", "4faeed614617590a6fe8a4ed358bbaf4fface7ee0a8fcb1fdfa8f6402fa20659", ["ate.conformance.r13_eval.v1"]),
    "r14_authority": ("r14-1", "00bc53de0e06443a9aeeb6c08b589bf8120b3c32ad85be80bd190f0e8bc33084", ["ate.conformance.r14_state.v1"]),
    "authorization_service": ("az-1", "a8f0ceb583e0491de6ea1b9307a2be58b22fac1846088244b8ef5eb735fb6343", ["ate.conformance.capability.v1"]),
    "audit_recorder": ("audit-1", "d3235d9da4fe0702b397eb92e00cd1852cc75847e854d056acdb0e1106e49a32", ["ate.conformance.audit.v1"]),
}

ROLE_BY_ARTIFACT_KIND = {
    "ConformanceProfile": "profile_signer",
    "QualificationFixture": "qa_issuer",
    "AdmissionFixture": "qa_issuer",
    "RuntimeEvidence": "runtime_observer",
    "TriggerObservation": "runtime_observer",
    "R13Evaluation": "r13_evaluator",
    "R14State": "r14_authority",
    "ExecutionCapability": "authorization_service",
    "AuditRecord": "audit_recorder",
}

REQUIRED_ARTIFACT_COUNTS = {
    "ConformanceProfile": 2,
    "QualificationFixture": 1,
    "AdmissionFixture": 1,
    "RuntimeEvidence": 3,
    "TriggerObservation": 1,
    "R13Evaluation": 3,
    "R14State": 3,
    "ExecutionCapability": 3,
}

PRIMARY_REQUIRED = {
    "01_verification_keys.json",
    "signed-artifacts.json",
    "signature-verification.json",
    "authoritative-audit-ledger.json",
    "tampered-audit-ledger.json",
    "case-accounting.json",
    "pytest-results.xml",
    "run-record-core.json",
}


class EvidenceVerificationError(ValueError):
    """A deterministic, fail-closed evidence-verification error."""

    def __init__(self, code: str, detail: str) -> None:
        super().__init__(f"{code}: {detail}")
        self.code = code
        self.detail = detail


def _fail(code: str, detail: str) -> None:
    raise EvidenceVerificationError(code, detail)


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_json(path: Path) -> Any:
    def unique_object(pairs):
        value = {}
        for key, item in pairs:
            if key in value:
                _fail("DUPLICATE_JSON_KEY", f"{path.name}: duplicate key {key!r}")
            value[key] = item
        return value
    try:
        return json.loads(
            path.read_text(encoding="utf-8"),
            object_pairs_hook=unique_object,
            parse_constant=lambda value: _fail(
                "NONCANONICAL_JSON_VALUE", f"{path.name}: {value}"
            ),
        )
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        _fail("INVALID_JSON", f"{path.name}: {exc}")


def artifact_envelope(artifact: Any) -> dict:
    """Serialize a signed dataclass without relying on its Python type later."""
    if not hasattr(artifact, "signing_payload"):
        raise TypeError("signed artifact must expose signing_payload()")
    payload = artifact.signing_payload()
    kind = payload.get("artifact_kind")
    if kind not in ROLE_BY_ARTIFACT_KIND:
        raise ValueError(f"unsupported artifact kind: {kind!r}")
    return {
        "artifact_kind": kind,
        "authority_role": ROLE_BY_ARTIFACT_KIND[kind],
        "signature_domain": artifact.signature_domain,
        "signature_hex": bytes(artifact.signature).hex(),
        "signing_payload": payload,
    }


def audit_record_json(record: Any) -> dict:
    """Serialize an AuditRecord using the verifier's public wire format."""
    return {
        "event_sequence": record.event_sequence,
        "event_kind": record.event_kind,
        "payload": jsonable(record.payload),
        "prev_hash": record.prev_hash,
        "record_hash": record.record_hash,
        "payload_digest": record.payload_digest,
        "logical_ts": record.logical_ts,
        "signature_hex": bytes(record.signature).hex(),
        "signature_domain": record.signature_domain,
    }


def signature_verification_rows(
    artifacts: list[dict], records: list[dict], registry: dict
) -> list[dict]:
    """Build the explicit producer-side per-object signature inventory."""
    by_role = {entry["authority_role"]: entry for entry in registry["entries"]}
    rows = []
    for artifact in artifacts:
        role = artifact["authority_role"]
        entry = by_role[role]
        rows.append({
            "artifact_kind": artifact["artifact_kind"],
            "artifact_id": artifact["signing_payload"]["artifact_id"],
            "signature_domain": artifact["signature_domain"],
            "authority_id": entry["authority_id"],
            "key_id": entry["key_id_sha256"],
            "source_file": "signed-artifacts.json",
            "verification": "PASS",
        })
    audit_entry = by_role["audit_recorder"]
    for record in records:
        rows.append({
            "artifact_kind": "AuditRecord",
            "audit_event_sequence": record["event_sequence"],
            "signature_domain": record["signature_domain"],
            "authority_id": audit_entry["authority_id"],
            "key_id": audit_entry["key_id_sha256"],
            "source_file": "authoritative-audit-ledger.json",
            "verification": "PASS",
        })
    return rows


def jsonable(value: Any) -> Any:
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    if isinstance(value, (bytes, bytearray)):
        return value.hex()
    if isinstance(value, (list, tuple)):
        return [jsonable(item) for item in value]
    if isinstance(value, dict):
        return {str(key): jsonable(item) for key, item in value.items()}
    if is_dataclass(value):
        return jsonable(asdict(value))
    raise TypeError(f"not evidence-serializable: {type(value).__name__}")


def verify_key_registry(registry: dict) -> tuple[dict[str, dict], str]:
    if registry.get("schema") != "ate.test-verification-key-registry.v1":
        _fail("REGISTRY_SCHEMA", "unsupported verification-key registry schema")
    if registry.get("test_only") is not True:
        _fail("REGISTRY_SCOPE", "registry must be TEST-ONLY material")
    forbidden = {"private_key", "private_key_hex", "private_seed", "seed", "seed_hex"}
    if forbidden.intersection(registry):
        _fail("REGISTRY_PRIVATE_MATERIAL", "registry contains a private-material field")
    entries = registry.get("entries")
    if not isinstance(entries, list) or len(entries) != 7:
        _fail("REGISTRY_CARDINALITY", "exactly seven authorities are required")
    by_role = {}
    seen_key_ids = set()
    seen_authority_ids = set()
    for entry in entries:
        if forbidden.intersection(entry):
            _fail("REGISTRY_PRIVATE_MATERIAL", "registry entry contains a private-material field")
        role = entry.get("authority_role")
        if role in by_role or role not in EXPECTED_ROLES:
            _fail("REGISTRY_ROLE", f"invalid or duplicate role: {role!r}")
        try:
            raw = bytes.fromhex(entry["public_key_hex"])
            public = Ed25519PublicKey.from_public_bytes(raw)
        except (KeyError, ValueError) as exc:
            _fail("REGISTRY_PUBLIC_KEY", f"{role}: {exc}")
        key_id = key_id_from_public_key(public)
        if (
            entry.get("key_algorithm") != "Ed25519"
            or entry.get("public_key_encoding") != "raw-32-byte-hex"
            or entry.get("test_only") is not True
        ):
            _fail("REGISTRY_ENCODING", f"{role}: algorithm, encoding, or scope mismatch")
        if entry.get("key_id_sha256") != key_id or key_id in seen_key_ids:
            _fail("REGISTRY_KEY_ID", f"{role}: key id mismatch or reuse")
        authority_id = entry.get("authority_id")
        if not authority_id or authority_id in seen_authority_ids:
            _fail("REGISTRY_AUTHORITY_ID", f"{role}: missing or duplicate authority id")
        domains = entry.get("permitted_signing_domains")
        if not isinstance(domains, list) or not domains or len(domains) != len(set(domains)):
            _fail("REGISTRY_DOMAINS", f"{role}: invalid signature domains")
        expected_id, expected_public_hex, expected_domains = EXPECTED_AUTHORITIES[role]
        if (
            authority_id != expected_id
            or entry.get("public_key_hex") != expected_public_hex
            or domains != expected_domains
        ):
            _fail("REGISTRY_PIN", f"{role}: registry differs from reviewed deterministic authority")
        by_role[role] = {**entry, "public_key": public}
        seen_key_ids.add(key_id)
        seen_authority_ids.add(authority_id)
    if set(by_role) != EXPECTED_ROLES:
        _fail("REGISTRY_ROLES", "registry role set is incomplete")
    return by_role, canonical_sha256(registry)


def verify_signed_artifacts(artifacts: list, authorities: dict[str, dict]) -> None:
    if not isinstance(artifacts, list) or not artifacts:
        _fail("ARTIFACT_SET", "signed artifact set is empty or invalid")
    seen = set()
    counts = {kind: 0 for kind in REQUIRED_ARTIFACT_COUNTS}
    for index, artifact in enumerate(artifacts):
        kind = artifact.get("artifact_kind")
        role = artifact.get("authority_role")
        payload = artifact.get("signing_payload")
        domain = artifact.get("signature_domain")
        if kind not in ROLE_BY_ARTIFACT_KIND or ROLE_BY_ARTIFACT_KIND[kind] != role:
            _fail("ARTIFACT_AUTHORITY", f"artifact {index}: authority-role mismatch")
        if not isinstance(payload, dict) or payload.get("artifact_kind") != kind:
            _fail("ARTIFACT_PAYLOAD", f"artifact {index}: kind/payload mismatch")
        if domain not in authorities[role]["permitted_signing_domains"]:
            _fail("ARTIFACT_DOMAIN", f"artifact {index}: undeclared signature domain")
        identity = (kind, payload.get("artifact_id"), canonical_sha256(payload))
        if identity in seen:
            _fail("ARTIFACT_DUPLICATE", f"artifact {index}: duplicate signed artifact")
        try:
            signature = bytes.fromhex(artifact["signature_hex"])
            authorities[role]["public_key"].verify(signature, signing_bytes(domain, payload))
        except (KeyError, ValueError, TypeError, Exception) as exc:
            # Ed25519 InvalidSignature is deliberately collapsed to one stable code.
            _fail("ARTIFACT_SIGNATURE", f"artifact {index}: {type(exc).__name__}")
        seen.add(identity)
        if kind in counts:
            counts[kind] += 1
    if counts != REQUIRED_ARTIFACT_COUNTS:
        _fail(
            "ARTIFACT_COVERAGE",
            f"signed artifact inventory mismatch: expected {REQUIRED_ARTIFACT_COUNTS}, got {counts}",
        )


def verify_lifecycle_semantics(artifacts: list) -> None:
    """Reconstruct the minimum frozen lifecycle proof from signed payloads."""
    by_kind: dict[str, list[dict]] = {}
    for envelope in artifacts:
        by_kind.setdefault(envelope["artifact_kind"], []).append(envelope["signing_payload"])
    profiles = sorted(by_kind["ConformanceProfile"], key=lambda item: item["profile_version"])
    if [
        (item["profile_version"], item["required_runtime_version"])
        for item in profiles
    ] != [(1, "v1"), (2, "v2")]:
        _fail("LIFECYCLE_PROFILES", "profiles do not bind versions 1/v1 and 2/v2")
    evidence = sorted(by_kind["RuntimeEvidence"], key=lambda item: item["event_sequence"])
    if [item["measured_runtime_version"] for item in evidence] != ["v1", "v2", "v2"]:
        _fail("LIFECYCLE_EVIDENCE", "runtime evidence sequence is not v1 -> v2 -> fresh v2")
    if not (
        evidence[2]["event_sequence"] > evidence[1]["event_sequence"]
        and evidence[2]["logical_ts"] > evidence[1]["logical_ts"]
        and evidence[2]["artifact_id"] != evidence[1]["artifact_id"]
    ):
        _fail("LIFECYCLE_FRESHNESS", "restoration evidence is not fresh")
    trigger = by_kind["TriggerObservation"][0]
    if (
        trigger["prior_evidence_id"] != evidence[0]["artifact_id"]
        or trigger["current_evidence_id"] != evidence[1]["artifact_id"]
    ):
        _fail("LIFECYCLE_TRIGGER", "trigger does not bind the v1 -> initial-v2 change")
    evaluations = sorted(by_kind["R13Evaluation"], key=lambda item: item["logical_ts"])
    expected_evaluations = [
        (1, "v1", "CONFORMANT", evidence[0]["artifact_id"]),
        (1, "v2", "REATTESTATION_REQUIRED", evidence[1]["artifact_id"]),
        (2, "v2", "CONFORMANT", evidence[2]["artifact_id"]),
    ]
    actual_evaluations = [
        (
            item["profile_version"],
            item["measured_runtime_version"],
            item["recommended_state"],
            item["runtime_evidence_id"],
        )
        for item in evaluations
    ]
    if actual_evaluations != expected_evaluations:
        _fail("LIFECYCLE_R13", "R13 evaluations do not prove invalidate-and-restore")
    states = sorted(by_kind["R14State"], key=lambda item: item["state_epoch"])
    if [(item["state_epoch"], item["new_state"]) for item in states] != [
        (1, "CONFORMANT"),
        (2, "REATTESTATION_REQUIRED"),
        (3, "CONFORMANT"),
    ]:
        _fail("LIFECYCLE_R14", "R14 state epochs do not prove N/N+1/N+2")
    if [item["r13_evaluation_id"] for item in states] != [
        item["artifact_id"] for item in evaluations
    ]:
        _fail("LIFECYCLE_R13_R14_BINDING", "R14 states do not bind the matching R13 evaluations")
    capabilities = sorted(
        by_kind["ExecutionCapability"], key=lambda item: (item["issued_at"], item["artifact_id"])
    )
    if sorted(item["observed_state_epoch"] for item in capabilities) != [1, 1, 3]:
        _fail("LIFECYCLE_CAPABILITIES", "capabilities do not bind epochs 1, 1, and 3")
    if len({item["nonce"] for item in capabilities}) != 3:
        _fail("LIFECYCLE_NONCES", "capability nonces are not unique")
    subject_ids = {
        item.get("subject_id")
        for values in by_kind.values()
        for item in values
        if "subject_id" in item
    }
    trust_domains = {
        item.get("trust_domain")
        for values in by_kind.values()
        for item in values
        if "trust_domain" in item
    }
    if len(subject_ids) != 1 or len(trust_domains) != 1:
        _fail("LIFECYCLE_BINDING", "signed artifacts disagree on subject or trust domain")


def verify_audit_ledger(records: list, authorities: dict[str, dict], registry_digest: str) -> None:
    if not isinstance(records, list) or not records:
        _fail("AUDIT_EMPTY", "authoritative audit ledger is empty")
    previous = "0" * 64
    for index, record in enumerate(records, start=1):
        if record.get("event_sequence") != index or record.get("prev_hash") != previous:
            _fail("AUDIT_CHAIN", f"record {index}: sequence or predecessor mismatch")
        payload = record.get("payload")
        if record.get("payload_digest") != canonical_sha256(payload):
            _fail("AUDIT_PAYLOAD_DIGEST", f"record {index}: payload digest mismatch")
        canonical_record = {
            "artifact_kind": "AuditRecord",
            "event_sequence": index,
            "event_kind": record.get("event_kind"),
            "payload": payload,
            "prev_hash": previous,
            "payload_digest": record.get("payload_digest"),
            "logical_ts": record.get("logical_ts"),
        }
        record_hash = canonical_sha256(canonical_record)
        if record.get("record_hash") != record_hash:
            _fail("AUDIT_RECORD_HASH", f"record {index}: record hash mismatch")
        domain = record.get("signature_domain")
        if domain != "ate.conformance.audit.v1":
            _fail("AUDIT_DOMAIN", f"record {index}: wrong signature domain")
        try:
            signature = bytes.fromhex(record["signature_hex"])
            authorities["audit_recorder"]["public_key"].verify(
                signature, signing_bytes(domain, {
                    "artifact_kind": "AuditRecord",
                    "event_sequence": index,
                    "event_kind": record.get("event_kind"),
                    "payload": payload,
                    "prev_hash": previous,
                    "payload_digest": record.get("payload_digest"),
                    "logical_ts": record.get("logical_ts"),
                }),
            )
        except Exception as exc:
            _fail("AUDIT_SIGNATURE", f"record {index}: {type(exc).__name__}")
        previous = record_hash
    first = records[0]
    if first.get("event_kind") != "trust_material_established":
        _fail("AUDIT_TRUST_GENESIS", "first record does not establish trust material")
    if first.get("payload", {}).get("verification_key_registry_digest") != registry_digest:
        _fail("AUDIT_TRUST_BINDING", "first record does not bind the registry digest")
    required_order = [
        "c1_issued",
        "runtime_mutation",
        "trigger_observed",
        "n_plus_1_published",
        "c1_denied",
        "post_change_evidence",
        "r13_restore_eval",
        "n_plus_2_published",
        "c2_issued",
        "c2_effect",
    ]
    positions = {record["event_kind"]: index for index, record in enumerate(records)}
    try:
        sequence = [positions[kind] for kind in required_order]
    except KeyError as exc:
        _fail("AUDIT_CAUSAL_ORDER", f"missing causal event: {exc.args[0]}")
    if sequence != sorted(sequence) or len(sequence) != len(set(sequence)):
        _fail("AUDIT_CAUSAL_ORDER", "required events are not strictly ordered")


def verify_tampered_copy(authoritative: list, tampered: list, authorities: dict[str, dict]) -> None:
    if len(authoritative) != len(tampered):
        _fail("TAMPER_SHAPE", "tampered ledger length changed")
    differences = []
    for index, (left, right) in enumerate(zip(authoritative, tampered)):
        if left != right:
            differences.append(index)
    if len(differences) != 1:
        _fail("TAMPER_MUTATION_COUNT", "tampered copy must change exactly one record")
    index = differences[0]
    expected = dict(authoritative[index])
    expected["payload"] = {"tampered": True, **authoritative[index]["payload"]}
    if tampered[index] != expected:
        _fail("TAMPER_MUTATION_SHAPE", "tampered copy has an undeclared mutation")
    try:
        verify_audit_ledger(
            tampered,
            authorities,
            authoritative[0]["payload"]["verification_key_registry_digest"],
        )
    except EvidenceVerificationError:
        return
    _fail("TAMPER_NOT_DETECTED", "tampered copy unexpectedly verified")


def verify_case_accounting(
    accounting: dict,
    pytest_xml: Path | None = None,
    evidence_directory: Path | None = None,
) -> None:
    if accounting.get("schema") != "ate.case-accounting.v1":
        _fail("CASE_SCHEMA", "unsupported case-accounting schema")
    cases = accounting.get("cases")
    if not isinstance(cases, list):
        _fail("CASE_SET", "case list is missing")
    ids = [case.get("case_id") for case in cases]
    if len(ids) != len(set(ids)) or set(ids) != set(EXPECTED_CASES):
        _fail("CASE_COVERAGE", "case accounting must contain exactly TC-01..18 and NS-01..08")
    all_nodes = []
    for case in cases:
        nodes = case.get("pytest_node_ids")
        expected_kind = "required" if case.get("case_id", "").startswith("TC-") else "negative"
        refs = case.get("evidence_refs")
        if (
            case.get("outcome") != "PASS"
            or case.get("case_kind") != expected_kind
            or not isinstance(case.get("title"), str)
            or not case["title"]
            or not isinstance(case.get("assertion_summary"), str)
            or not case["assertion_summary"]
            or not isinstance(refs, list)
            or not refs
            or not isinstance(nodes, list)
            or not nodes
        ):
            _fail("CASE_OUTCOME", f"{case.get('case_id')}: missing passed pytest evidence")
        if len(nodes) != len(set(nodes)) or not all(isinstance(node, str) and "::test_" in node for node in nodes):
            _fail("CASE_NODE_IDS", f"{case.get('case_id')}: invalid pytest node ids")
        all_nodes.extend(nodes)
        if evidence_directory is not None:
            for ref in refs:
                if (
                    not isinstance(ref, str)
                    or Path(ref).name != ref
                    or not (evidence_directory / ref).is_file()
                ):
                    _fail("CASE_EVIDENCE_REF", f"{case.get('case_id')}: invalid evidence ref {ref!r}")
    if len(all_nodes) != len(set(all_nodes)):
        _fail("CASE_NODE_REUSE", "a controlling pytest node is mapped to multiple cases")
    if pytest_xml is not None:
        try:
            root = ElementTree.parse(pytest_xml).getroot()
        except (OSError, ElementTree.ParseError) as exc:
            _fail("PYTEST_XML", str(exc))
        passed = set()
        for item in root.iter("testcase"):
            if any(item.find(tag) is not None for tag in ("failure", "error", "skipped")):
                continue
            file_name = item.get("file")
            test_name = item.get("name")
            if file_name and test_name:
                passed.add(f"{file_name}::{test_name}")
            class_name = item.get("classname")
            if class_name and test_name:
                passed.add(f"{class_name.replace('.', '/')}.py::{test_name}")
        for case in cases:
            missing = set(case["pytest_node_ids"]) - passed
            if missing:
                _fail("CASE_PYTEST_PROOF", f"{case['case_id']}: absent/non-passing nodes {sorted(missing)}")
        if any(
            item.find(tag) is not None
            for item in root.iter("testcase")
            for tag in ("failure", "error", "skipped")
        ):
            _fail("PYTEST_NOT_CLEAN", "pytest XML contains failure, error, or skipped cases")


def _safe_primary_name(name: str) -> bool:
    return bool(name) and Path(name).name == name and name not in {
        "evidence-manifest.json",
        "evidence-manifest.sha256",
        "independent-verification.json",
        "run-record.json",
        "run-record.sha256",
    }


def verify_primary_bundle(directory: Path) -> dict:
    """Verify layers 1-2 and return the report payload for layer 3."""
    try:
        if directory.is_symlink() or not directory.is_dir():
            _fail("EVIDENCE_DIRECTORY", "evidence path is not a real directory")
        for child in directory.iterdir():
            if child.is_symlink():
                _fail("SYMLINK_REJECTED", child.name)
    except OSError as exc:
        _fail("EVIDENCE_DIRECTORY", str(exc))
    manifest_path = directory / "evidence-manifest.json"
    checksum_path = directory / "evidence-manifest.sha256"
    manifest = load_json(manifest_path)
    expected_checksum = f"{sha256_file(manifest_path)}  evidence-manifest.json\n"
    try:
        actual_checksum = checksum_path.read_text(encoding="ascii")
    except OSError as exc:
        _fail("MANIFEST_CHECKSUM_MISSING", str(exc))
    if actual_checksum != expected_checksum:
        _fail("MANIFEST_CHECKSUM", "detached manifest checksum mismatch")
    files = manifest.get("files")
    if not isinstance(files, list):
        _fail("MANIFEST_SCHEMA", "manifest files list is missing")
    names = [item.get("name") for item in files]
    if names != sorted(names) or len(names) != len(set(names)):
        _fail("MANIFEST_ORDER", "manifest names must be unique and sorted")
    if not PRIMARY_REQUIRED.issubset(names):
        _fail("MANIFEST_REQUIRED", "required primary evidence is absent")
    closure_names = {
        "evidence-manifest.json",
        "evidence-manifest.sha256",
        "independent-verification.json",
        "run-record.json",
        "run-record.sha256",
    }
    actual_primary = {
        path.name for path in directory.iterdir()
        if path.name not in closure_names
    }
    if set(names) != actual_primary:
        _fail("MANIFEST_INVENTORY", "manifest does not exactly cover primary evidence")
    for item in files:
        name = item.get("name")
        if not isinstance(name, str) or not _safe_primary_name(name):
            _fail("MANIFEST_PATH", f"unsafe or reserved primary path: {name!r}")
        path = directory / name
        try:
            size = path.stat().st_size
        except OSError as exc:
            _fail("MANIFEST_FILE_MISSING", f"{name}: {exc}")
        if item.get("size_bytes") != size or item.get("sha256") != sha256_file(path):
            _fail("MANIFEST_FILE_HASH", f"{name}: size or digest mismatch")
    registry = load_json(directory / "01_verification_keys.json")
    authorities, registry_digest = verify_key_registry(registry)
    artifacts = load_json(directory / "signed-artifacts.json")
    verify_signed_artifacts(artifacts, authorities)
    verify_lifecycle_semantics(artifacts)
    authoritative = load_json(directory / "authoritative-audit-ledger.json")
    verify_audit_ledger(
        authoritative,
        authorities,
        registry_digest,
    )
    verify_tampered_copy(
        authoritative,
        load_json(directory / "tampered-audit-ledger.json"),
        authorities,
    )
    signature_rows = load_json(directory / "signature-verification.json")
    expected_rows = signature_verification_rows(artifacts, authoritative, registry)
    if signature_rows != expected_rows:
        _fail("SIGNATURE_INVENTORY", "signature verification inventory is incomplete or inconsistent")
    verify_case_accounting(
        load_json(directory / "case-accounting.json"),
        directory / "pytest-results.xml",
        directory,
    )
    core = load_json(directory / "run-record-core.json")
    if (
        core.get("schema") != "ate.run-record-core.v1"
        or core.get("mode") not in {"dry-run", "formal"}
        or not isinstance(core.get("run_id"), str)
        or not core["run_id"]
    ):
        _fail("CORE_SCHEMA", "run-record core schema, mode, or run id is invalid")
    expected_classification = (
        "FORMAL_EVIDENCE_CANDIDATE"
        if core["mode"] == "formal"
        else "DEVELOPMENT_EVIDENCE_CANDIDATE"
    )
    if core.get("classification") != expected_classification:
        _fail("CORE_CLASSIFICATION", "producer classification exceeds or mismatches candidate status")
    required_core = {
        "design_version",
        "implementation_commit",
        "runner_commit",
        "started_at",
        "completed_at",
        "subject_id",
        "role_id",
        "trust_domain",
        "epoch_summary",
        "required_cases",
        "negative_cases",
    }
    if not required_core.issubset(core):
        _fail("CORE_FIELDS", "run-record core omits frozen fields")
    for field in ("implementation_commit", "runner_commit"):
        value = core[field]
        if (
            not isinstance(value, str)
            or len(value) != 40
            or any(char not in "0123456789abcdef" for char in value)
        ):
            _fail("CORE_COMMIT", f"{field} is not a full lowercase commit id")
    if (
        core["epoch_summary"] != [1, 2, 3]
        or core["required_cases"] != {"passed": 18, "total": 18}
        or core["negative_cases"] != {"passed": 8, "total": 8}
    ):
        _fail("CORE_COUNTS", "epoch or case summary mismatch")
    return {
        "schema": "ate.independent-evidence-verification.v1",
        "verdict": "INDEPENDENT_EVIDENCE_VERIFICATION_PASS",
        "manifest_sha256": sha256_file(manifest_path),
        "manifest_checksum_sha256": sha256_file(checksum_path),
        "registry_sha256": sha256_file(directory / "01_verification_keys.json"),
        "primary_file_count": len(files),
        "verified_case_ids": list(EXPECTED_CASES),
        "required_case_result": "18/18 PASS",
        "negative_case_result": "8/8 PASS",
        "checks": [
            "manifest-checksum",
            "primary-file-hashes",
            "verification-key-registry",
            "signed-artifact-signatures",
            "audit-chain-and-signatures",
            "trust-material-genesis-binding",
            "exact-case-accounting",
            "lifecycle-cross-file-consistency",
            "tampered-copy-exact-mutation-and-failure",
        ],
    }


def verify_complete_bundle(directory: Path) -> dict:
    """Verify all five closure layers; perform no writes."""
    computed_report = verify_primary_bundle(directory)
    report_path = directory / "independent-verification.json"
    report = load_json(report_path)
    verifier_path = directory.parents[1] / "formal-runner-v0.1.2" / "verify_evidence.py"
    core = load_json(directory / "run-record-core.json")
    if report.get("verifier_commit") != core.get("runner_commit"):
        _fail("VERIFIER_COMMIT", "verifier commit does not match the runner commit")
    if verifier_path.is_file() and report.get("verifier_script_sha256") != sha256_file(verifier_path):
        _fail("VERIFIER_SCRIPT", "verifier script digest mismatch")
    comparable_report = {
        key: value
        for key, value in report.items()
        if key not in {"verifier_commit", "verifier_script_sha256"}
    }
    if canonical_json_bytes(comparable_report) != canonical_json_bytes(computed_report):
        _fail("INDEPENDENT_REPORT", "persisted verifier report differs from recomputation")
    core_path = directory / "run-record-core.json"
    manifest_path = directory / "evidence-manifest.json"
    run_record_path = directory / "run-record.json"
    run_record = load_json(run_record_path)
    registry = load_json(directory / "01_verification_keys.json")
    _authorities, registry_digest = verify_key_registry(registry)
    expected = {
        **load_json(core_path),
        "schema": "ate.run-record.v1",
        "run_record_core_sha256": sha256_file(core_path),
        "evidence_manifest_sha256": sha256_file(manifest_path),
        "independent_verification_sha256": sha256_file(report_path),
        "verification_key_registry_digest": registry_digest,
        "producer_classification": load_json(core_path).get("classification"),
        "independent_verification_verdict": "INDEPENDENT_EVIDENCE_VERIFICATION_PASS",
        "controlling_disposition": (
            "AWAITING_PI_ADJUDICATION"
            if load_json(core_path).get("mode") == "formal"
            else "DEVELOPMENT_DRY_RUN_EVIDENCE_VERIFIED"
        ),
    }
    expected.pop("classification", None)
    if run_record != expected:
        _fail("RUN_RECORD_BINDING", "final run record does not bind closure layers")
    checksum = f"{sha256_file(run_record_path)}  run-record.json\n"
    try:
        actual = (directory / "run-record.sha256").read_text(encoding="ascii")
    except OSError as exc:
        _fail("RUN_RECORD_CHECKSUM_MISSING", str(exc))
    if actual != checksum:
        _fail("RUN_RECORD_CHECKSUM", "terminal run-record checksum mismatch")
    return run_record

"""Bounded implementation tests for formal-evidence closure amendment v0.1."""

from __future__ import annotations

import copy
import hashlib
import importlib.util
import json
from pathlib import Path
from xml.etree import ElementTree

import pytest

from conformance.audit import copy_and_tamper
from conformance.canonical import canonical_sha256
from conformance.evidence import (
    CASE_DEFINITIONS,
    CASE_NODE_IDS,
    EvidenceVerificationError,
    artifact_envelope,
    audit_record_json,
    signature_verification_rows,
    verify_complete_bundle,
    verify_key_registry,
    verify_primary_bundle,
)
from fixtures import bootstrap
from fixtures.test_keys import public_key_registry, public_key_registry_digest
from tests.conftest import drive_full_lifecycle


def _write_json(path: Path, value) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _closure_module():
    path = Path(__file__).parents[1] / "formal-runner-v0.1.2" / "closure.py"
    spec = importlib.util.spec_from_file_location("acl_evidence_closure", path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def _build_primary(directory: Path):
    harness, controls = bootstrap.build_harness_with_controls(prefix="closure-test")
    context = drive_full_lifecycle(harness, controls.attach_executor(harness), controls)
    _write_json(directory / "01_verification_keys.json", harness.verification_key_registry)
    artifacts = [
        artifact_envelope(artifact)
        for artifact in (
            harness.profile_v1,
            harness.profile_v2,
            harness.qualification,
            harness.admission,
            context.runtime_evidence_v1,
            context.runtime_evidence_v2_initial,
            context.runtime_evidence_v2_fresh,
            context.trigger,
            context.r13_initial,
            context.r13_invalidated,
            context.r13_restored,
            context.r14_initial,
            context.r14_invalidated,
            context.r14_restored,
            context.capability_c0,
            context.capability_c1,
            context.capability_c2,
        )
    ]
    _write_json(directory / "signed-artifacts.json", artifacts)
    records = [audit_record_json(record) for record in harness.audit.records()]
    _write_json(
        directory / "authoritative-audit-ledger.json",
        records,
    )
    tampered = copy_and_tamper(harness.audit.records(), tamper_index=5)
    _write_json(
        directory / "tampered-audit-ledger.json",
        [audit_record_json(record) for record in tampered],
    )
    _write_json(
        directory / "signature-verification.json",
        signature_verification_rows(
            artifacts, records, harness.verification_key_registry
        ),
    )
    for name in (
        "02_initial_and_c0.json",
        "03_invalidation_and_c1.json",
        "04_fresh_evidence_and_restoration.json",
        "05_c2_and_replay.json",
    ):
        _write_json(directory / name, {"test_fixture": True})
    cases = [
        {"case_id": case_id, "outcome": "PASS", **definition}
        for case_id, definition in CASE_DEFINITIONS.items()
    ]
    _write_json(directory / "case-accounting.json", {
        "schema": "ate.case-accounting.v1",
        "cases": cases,
    })
    testcase_xml = "".join(
        f'<testcase file="{node.split("::")[0]}" name="{node.split("::")[1]}"/>'
        for nodes in CASE_NODE_IDS.values() for node in nodes
    )
    (directory / "pytest-results.xml").write_text(
        f'<?xml version="1.0"?><testsuites><testsuite>{testcase_xml}</testsuite></testsuites>',
        encoding="utf-8",
    )
    _write_json(directory / "run-record-core.json", {
        "schema": "ate.run-record-core.v1",
        "run_id": "bounded-implementation-test",
        "mode": "dry-run",
        "classification": "DEVELOPMENT_EVIDENCE_CANDIDATE",
        "design_version": "v0.1.1+formal-evidence-closure-amendment-v0.1",
        "implementation_commit": "0" * 40,
        "runner_commit": "0" * 40,
        "started_at": "2026-09-19T00:00:00Z",
        "completed_at": "2026-09-19T00:00:01Z",
        "subject_id": bootstrap.SUBJECT_ID,
        "role_id": bootstrap.ROLE_ID,
        "trust_domain": bootstrap.TRUST_DOMAIN,
        "epoch_summary": [1, 2, 3],
        "required_cases": {"passed": 18, "total": 18},
        "negative_cases": {"passed": 8, "total": 8},
    })
    return harness


@pytest.fixture
def closed_bundle(tmp_path):
    harness = _build_primary(tmp_path)
    names = sorted(path.name for path in tmp_path.iterdir())
    _closure_module().close_evidence_bundle(tmp_path, names)
    yield tmp_path
    bootstrap.teardown(harness)


def test_deterministic_authorities_and_public_only_registry():
    first = public_key_registry()
    second = public_key_registry()
    assert first == second
    assert len(first["entries"]) == 7
    assert len({entry["key_id_sha256"] for entry in first["entries"]}) == 7
    assert "private" not in json.dumps(first).lower()
    _authorities, digest = verify_key_registry(first)
    assert digest == public_key_registry_digest()


def test_audit_genesis_binds_verification_registry():
    harness = bootstrap.build_harness(prefix="trust-genesis")
    try:
        first = harness.audit.records()[0]
        assert first.event_sequence == 1
        assert first.event_kind == "trust_material_established"
        assert first.payload["verification_key_registry_digest"] == canonical_sha256(
            harness.verification_key_registry
        )
        assert harness.audit.verify_chain()
    finally:
        bootstrap.teardown(harness)


def test_five_layer_bundle_closes_and_reverifies(closed_bundle):
    assert (
        verify_primary_bundle(closed_bundle)["verdict"]
        == "INDEPENDENT_EVIDENCE_VERIFICATION_PASS"
    )
    assert verify_complete_bundle(closed_bundle)["producer_classification"] == "DEVELOPMENT_EVIDENCE_CANDIDATE"
    assert (closed_bundle / "run-record.sha256").is_file()


NEGATIVE_SCENARIOS = (
    "missing-verification-key-registry",
    "duplicate-authority-id",
    "duplicate-key-id",
    "public-key-key-id-mismatch",
    "unexpected-private-key-field",
    "wrong-signing-domain",
    "invalid-artifact-signature",
    "invalid-audit-signature",
    "missing-signed-artifact",
    "orphan-signed-artifact",
    "duplicate-controlling-case-id",
    "missing-controlling-case-id",
    "skipped-or-xfailed-controlling-test",
    "nonexistent-pytest-node-reference",
    "evidence-manifest-missing",
    "undeclared-extra-primary-file",
    "evidence-byte-size-hash-mismatch",
    "broken-audit-previous-hash-link",
    "broken-payload-digest",
    "causal-order-inversion",
    "tampered-copy-second-mutation",
    "runrecord-manifest-verifier-digest-mismatch",
    "missing-terminal-checksum",
    "symlink-or-path-traversal",
    "duplicate-json-key",
)


def _refresh_primary_manifest(directory: Path, filename: str) -> None:
    manifest_path = directory / "evidence-manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    path = directory / filename
    for entry in manifest["files"]:
        if entry["name"] == filename:
            entry["sha256"] = hashlib.sha256(path.read_bytes()).hexdigest()
            entry["size_bytes"] = path.stat().st_size
            break
    _write_json(manifest_path, manifest)
    digest = hashlib.sha256(manifest_path.read_bytes()).hexdigest()
    (directory / "evidence-manifest.sha256").write_text(
        f"{digest}  evidence-manifest.json\n", encoding="ascii"
    )


def _mutate_json(directory: Path, filename: str, mutate) -> None:
    path = directory / filename
    value = json.loads(path.read_text(encoding="utf-8"))
    mutate(value)
    _write_json(path, value)
    _refresh_primary_manifest(directory, filename)


@pytest.mark.parametrize("scenario", NEGATIVE_SCENARIOS)
def test_required_negative_verifier_matrix(closed_bundle, scenario):
    directory = closed_bundle
    if scenario == "missing-verification-key-registry":
        (directory / "01_verification_keys.json").unlink()
    elif scenario == "duplicate-authority-id":
        _mutate_json(directory, "01_verification_keys.json", lambda value: value["entries"][1].update(
            authority_id=value["entries"][0]["authority_id"]
        ))
    elif scenario == "duplicate-key-id":
        _mutate_json(directory, "01_verification_keys.json", lambda value: value["entries"][1].update(
            key_id_sha256=value["entries"][0]["key_id_sha256"]
        ))
    elif scenario == "public-key-key-id-mismatch":
        _mutate_json(directory, "01_verification_keys.json", lambda value: value["entries"][0].update(
            key_id_sha256="0" * 64
        ))
    elif scenario == "unexpected-private-key-field":
        _mutate_json(directory, "01_verification_keys.json", lambda value: value["entries"][0].update(
            seed_hex="00" * 32
        ))
    elif scenario == "wrong-signing-domain":
        _mutate_json(directory, "signed-artifacts.json", lambda value: value[0].update(
            signature_domain="ate.wrong.domain"
        ))
    elif scenario == "invalid-artifact-signature":
        _mutate_json(directory, "signed-artifacts.json", lambda value: value[0].update(
            signature_hex="00" * 64
        ))
    elif scenario == "invalid-audit-signature":
        _mutate_json(directory, "authoritative-audit-ledger.json", lambda value: value[0].update(
            signature_hex="00" * 64
        ))
    elif scenario == "missing-signed-artifact":
        _mutate_json(directory, "signed-artifacts.json", lambda value: value.pop())
    elif scenario == "orphan-signed-artifact":
        _mutate_json(directory, "signed-artifacts.json", lambda value: value.append({
            **copy.deepcopy(value[0]),
            "signature_hex": "00" * 64,
            "signing_payload": {**value[0]["signing_payload"], "artifact_id": "orphan"},
        }))
    elif scenario in {"duplicate-controlling-case-id", "missing-controlling-case-id"}:
        def mutate_cases(value):
            if scenario.startswith("duplicate"):
                value["cases"][1]["case_id"] = value["cases"][0]["case_id"]
            else:
                value["cases"].pop()
        _mutate_json(directory, "case-accounting.json", mutate_cases)
    elif scenario == "skipped-or-xfailed-controlling-test":
        xml_path = directory / "pytest-results.xml"
        root = ElementTree.parse(xml_path).getroot()
        ElementTree.SubElement(next(root.iter("testcase")), "skipped", type="pytest.xfail")
        ElementTree.ElementTree(root).write(xml_path, encoding="unicode")
        _refresh_primary_manifest(directory, "pytest-results.xml")
    elif scenario == "nonexistent-pytest-node-reference":
        _mutate_json(directory, "case-accounting.json", lambda value: value["cases"][0].update(
            pytest_node_ids=["tests/test_lifecycle.py::test_does_not_exist"]
        ))
    elif scenario == "evidence-manifest-missing":
        (directory / "evidence-manifest.json").unlink()
    elif scenario == "undeclared-extra-primary-file":
        (directory / "undeclared-primary.txt").write_text("unexpected\n", encoding="utf-8")
    elif scenario == "evidence-byte-size-hash-mismatch":
        with (directory / "signed-artifacts.json").open("a", encoding="utf-8") as stream:
            stream.write(" ")
    elif scenario == "broken-audit-previous-hash-link":
        _mutate_json(directory, "authoritative-audit-ledger.json", lambda value: value[1].update(
            prev_hash="0" * 64
        ))
    elif scenario == "broken-payload-digest":
        _mutate_json(directory, "authoritative-audit-ledger.json", lambda value: value[1].update(
            payload_digest="0" * 64
        ))
    elif scenario == "causal-order-inversion":
        def invert(value):
            left = next(i for i, row in enumerate(value) if row["event_kind"] == "c1_issued")
            right = next(i for i, row in enumerate(value) if row["event_kind"] == "runtime_mutation")
            value[left]["event_kind"], value[right]["event_kind"] = (
                value[right]["event_kind"], value[left]["event_kind"]
            )
        _mutate_json(directory, "authoritative-audit-ledger.json", invert)
    elif scenario == "tampered-copy-second-mutation":
        _mutate_json(directory, "tampered-audit-ledger.json", lambda value: value[0]["payload"].update(
            second_undeclared_mutation=True
        ))
    elif scenario == "runrecord-manifest-verifier-digest-mismatch":
        value = json.loads((directory / "run-record.json").read_text(encoding="utf-8"))
        value["evidence_manifest_sha256"] = "0" * 64
        _write_json(directory / "run-record.json", value)
    elif scenario == "missing-terminal-checksum":
        (directory / "run-record.sha256").unlink()
    elif scenario == "symlink-or-path-traversal":
        target = directory / "signed-artifacts.json"
        target.unlink()
        target.symlink_to(directory / "case-accounting.json")
    elif scenario == "duplicate-json-key":
        path = directory / "run-record-core.json"
        text = path.read_text(encoding="utf-8").rstrip()
        path.write_text(text[:-1] + ', "mode": "formal"}\n', encoding="utf-8")
        _refresh_primary_manifest(directory, "run-record-core.json")
    else:
        raise AssertionError(scenario)
    with pytest.raises(EvidenceVerificationError):
        verify_complete_bundle(directory)


def test_formal_mode_rejected_before_reviewed_dry_run_gate():
    path = Path(__file__).parents[1] / "formal-runner-v0.1.2" / "run_formal.py"
    spec = importlib.util.spec_from_file_location("acl_formal_runner", path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    with pytest.raises(module.FormalRunError):
        module.require_formal_authorization(
            True, {"ACL_FORMAL_RUN_AUTHORIZED": "YES"}
        )

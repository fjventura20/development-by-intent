"""Producer-side helpers for the five-layer evidence closure.

The producer writes files. Verification is delegated to verify_evidence.py in
a separate process; its stdout is the only content persisted as layer three.
"""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path
from typing import Any


def _write_json(path: Path, value: Any) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def close_evidence_bundle(directory: Path, primary_names: list[str]) -> dict:
    """Close an already-populated primary evidence directory.

    This must be called once. Reserved closure files must not exist.
    """
    reserved = (
        "evidence-manifest.json",
        "evidence-manifest.sha256",
        "independent-verification.json",
        "run-record.json",
        "run-record.sha256",
    )
    if any((directory / name).exists() for name in reserved):
        raise RuntimeError("closure target already contains reserved files")
    names = sorted(set(primary_names))
    if len(names) != len(primary_names):
        raise RuntimeError("primary evidence names must be unique")
    manifest_files = []
    for name in names:
        path = directory / name
        if path.name != name or not path.is_file():
            raise RuntimeError(f"unsafe or missing primary evidence: {name}")
        manifest_files.append({
            "name": name,
            "sha256": _sha(path),
            "size_bytes": path.stat().st_size,
        })
    core = json.loads((directory / "run-record-core.json").read_text(encoding="utf-8"))
    manifest = {
        "schema": "ate.evidence-manifest.v1",
        "run_id": core["run_id"],
        "classification": core["classification"],
        "files": manifest_files,
    }
    manifest_path = directory / "evidence-manifest.json"
    _write_json(manifest_path, manifest)
    (directory / "evidence-manifest.sha256").write_text(
        f"{_sha(manifest_path)}  evidence-manifest.json\n", encoding="ascii"
    )
    verifier = Path(__file__).with_name("verify_evidence.py")
    process = subprocess.run(
        [sys.executable, str(verifier), str(directory)],
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    if process.returncode != 0:
        raise RuntimeError(f"independent verifier rejected primary evidence: {process.stdout.strip()}")
    report = json.loads(process.stdout)
    report_path = directory / "independent-verification.json"
    _write_json(report_path, report)
    registry = json.loads((directory / "01_verification_keys.json").read_text(encoding="utf-8"))
    from conformance.canonical import canonical_sha256

    run_record = {
        **core,
        "schema": "ate.run-record.v1",
        "run_record_core_sha256": _sha(directory / "run-record-core.json"),
        "evidence_manifest_sha256": _sha(manifest_path),
        "independent_verification_sha256": _sha(report_path),
        "verification_key_registry_digest": canonical_sha256(registry),
        "producer_classification": core["classification"],
        "independent_verification_verdict": "INDEPENDENT_EVIDENCE_VERIFICATION_PASS",
        "controlling_disposition": (
            "AWAITING_PI_ADJUDICATION"
            if core["mode"] == "formal"
            else "DEVELOPMENT_DRY_RUN_EVIDENCE_VERIFIED"
        ),
    }
    run_record.pop("classification", None)
    run_record_path = directory / "run-record.json"
    _write_json(run_record_path, run_record)
    # Terminal marker: always written last.
    (directory / "run-record.sha256").write_text(
        f"{_sha(run_record_path)}  run-record.json\n", encoding="ascii"
    )
    return run_record

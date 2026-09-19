#!/usr/bin/env python3
"""Read-only subprocess entry point for independent evidence verification."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

POC_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(POC_ROOT))

from conformance.evidence import (  # noqa: E402
    EvidenceVerificationError,
    verify_complete_bundle,
    verify_primary_bundle,
)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("evidence_directory", type=Path)
    parser.add_argument("--complete", action="store_true")
    args = parser.parse_args()
    try:
        result = (
            verify_complete_bundle(args.evidence_directory)
            if args.complete
            else verify_primary_bundle(args.evidence_directory)
        )
        if not args.complete:
            core = json.loads(
                (args.evidence_directory / "run-record-core.json").read_text(encoding="utf-8")
            )
            result["verifier_commit"] = core["runner_commit"]
            result["verifier_script_sha256"] = hashlib.sha256(
                Path(__file__).read_bytes()
            ).hexdigest()
    except EvidenceVerificationError as exc:
        print(json.dumps({
            "schema": "ate.independent-evidence-verification.v1",
            "verdict": "FAIL",
            "error_code": exc.code,
            "detail": exc.detail,
        }, sort_keys=True))
        return 2
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

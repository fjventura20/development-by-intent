#!/usr/bin/env python3
"""
COA-E2 — verify_hashes.py

Pre-run hash verification. Refuses to proceed if any expected file's SHA-256
does not match the freeze manifest. Output: evidence/v0.2-verify/<ts>-verify.json.

No model invocation. No CLI side effects. Pure local file hashing.
"""

import argparse
import hashlib
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path, required=True,
                        help="Path to freeze_manifest.json")
    parser.add_argument("--output", type=Path, required=True,
                        help="Path to write verification report")
    args = parser.parse_args()

    manifest = json.loads(args.manifest.read_text())
    results = {"verified_at": datetime.now(timezone.utc).isoformat(),
               "manifest_sha256": sha256(args.manifest),
               "files": []}
    overall_ok = True

    for entry in manifest["files"]:
        p = Path(entry["path"])
        if not p.exists():
            results["files"].append({"path": str(p), "expected_sha256": entry["sha256"],
                                     "actual_sha256": None, "status": "MISSING"})
            overall_ok = False
            continue
        actual = sha256(p)
        match = actual == entry["sha256"]
        results["files"].append({"path": str(p), "expected_sha256": entry["sha256"],
                                 "actual_sha256": actual, "status": "OK" if match else "MISMATCH"})
        if not match:
            overall_ok = False

    results["overall"] = "PASS" if overall_ok else "FAIL"
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(results, indent=2), encoding="utf-8")

    print(f"verify_hashes.py: {results['overall']}")
    print(f"  manifest: {args.manifest}")
    print(f"  output:   {args.output}")
    print(f"  files checked: {len(results['files'])}")

    if not overall_ok:
        sys.exit(2)


if __name__ == "__main__":
    main()

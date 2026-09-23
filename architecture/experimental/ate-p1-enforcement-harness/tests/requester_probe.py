#!/usr/bin/env python3
"""ATE P1 v0.1.1 — T2 requester process probe.

The parent test launches this script in a CHILD process. The probe
prints everything the requester process can observe about itself:
  - argv (filtered)
  - environment (filtered)
  - cwd
  - accessible files in the test tmpdir (deny-read on the
    executor-only credentials file)
  - the requester module's exposed state
  - the absence of any audit-key, credential, signing-authority,
    or DB-write-credential material in the observation

The probe does NOT receive the authority DB path or the executor
secrets paths. The probe's main job is to demonstrate that the
requester subprocess has no executor-only material.
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from typing import Any, Dict, List, Optional


def _filtered_env() -> Dict[str, str]:
    allowed_prefixes = ("ATE_", "HERMES_", "PYTHON")
    return {
        k: v
        for k, v in os.environ.items()
        if any(k.startswith(p) for p in allowed_prefixes)
    }


def _filtered_argv(argv: List[str]) -> List[str]:
    out = []
    for a in argv:
        low = a.lower()
        if any(s in low for s in ("cred", "audit", "key", "signing")):
            out.append(a.split("=", 1)[0] + "=<redacted>")
        else:
            out.append(a)
    return out


def _try_read(path: str) -> Dict[str, Any]:
    try:
        with open(path, "rb") as f:
            data = f.read()
        return {
            "path": path,
            "exists": True,
            "readable": True,
            "size_bytes": len(data),
        }
    except FileNotFoundError:
        return {"path": path, "exists": False, "readable": False}
    except PermissionError as e:
        return {"path": path, "exists": True, "readable": False, "error": str(e)}
    except Exception as e:
        return {"path": path, "exists": True, "readable": False, "error": f"{type(e).__name__}: {e}"}


def _try_listdir(path: str) -> Dict[str, Any]:
    try:
        items = os.listdir(path)
        return {"path": path, "listable": True, "items": sorted(items)}
    except PermissionError as e:
        return {"path": path, "listable": False, "error": f"PermissionError: {e}"}
    except FileNotFoundError:
        return {"path": path, "listable": False, "error": "FileNotFoundError"}
    except Exception as e:
        return {"path": path, "listable": False, "error": f"{type(e).__name__}: {e}"}


def main() -> int:
    parser = argparse.ArgumentParser(description="ATE P1 T2 requester probe")
    parser.add_argument(
        "--resource_dir",
        default=None,
        help="optional tmpdir path the probe should attempt to access",
    )
    args = parser.parse_args()

    result: Dict[str, Any] = {
        "argv_filtered": _filtered_argv(sys.argv),
        "env_filtered": _filtered_env(),
        "cwd": os.getcwd(),
        "uid": os.getuid(),
        "euid": os.geteuid(),
    }

    if args.resource_dir:
        result["dir_listing_attempt"] = _try_listdir(args.resource_dir)
        # Try reading individual files even if the dir is not listable
        for fname in [
            "authority.sqlite",
            "executor_audit_key.bin",
            "executor_credentials.json",
            "seed.json",
            "sample_request.json",
        ]:
            result.setdefault("files_probed", []).append(
                _try_read(os.path.join(args.resource_dir, fname))
            )

    # Determine which sensitive strings appear in the observation
    sensitive_strings = [
        "audit_key",
        "executor_credentials",
        "private_key",
        "trust_decision_signing",
    ]
    observed_text = json.dumps(result)
    result["sensitive_strings_present"] = {
        s: (s.lower() in observed_text.lower()) for s in sensitive_strings
    }

    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())

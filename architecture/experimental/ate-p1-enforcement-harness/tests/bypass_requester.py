#!/usr/bin/env python3
"""ATE P1 v0.1.1 — T1 bypass probe (runs as a SEPARATE PROCESS).

The parent test launches this script as a subprocess. Crucially:
  - The subprocess does NOT receive the authority DB path.
  - The subprocess does NOT receive the executor credentials path.
  - The subprocess does NOT receive the audit key path.
  - The subprocess has NO OS-level read/write access to the authority
    DB (the parent tmpdir is mode 0700 and owned by ate-executor).
  - The subprocess is the requester side: it must not be able to
    perform any privileged operation.

The probe's role is to ATTEMPT bypass paths and report which were
blocked by the privilege boundary (vs. application-layer checks).

Outputs JSON to stdout with:
  - argv (filtered)
  - env (filtered)
  - cwd
  - bypass attempt results
"""
from __future__ import annotations

import argparse
import json
import os
import sqlite3
import sys
from typing import Any, Dict, List


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


def main() -> int:
    parser = argparse.ArgumentParser(description="ATE P1 T1 bypass probe")
    parser.add_argument(
        "--resource_id",
        default=None,
        help="resource_id to attempt bypass on (if omitted, probe tries all known patterns)",
    )
    parser.add_argument(
        "--resource_dir",
        default=None,
        help="optional tmpdir path to attempt to list/read",
    )
    args = parser.parse_args()

    result: Dict[str, Any] = {
        "argv_filtered": _filtered_argv(sys.argv),
        "env_filtered": _filtered_env(),
        "cwd": os.getcwd(),
        "uid": os.getuid(),
        "euid": os.geteuid(),
    }

    # Attempt 1: open a known authority DB by guessing the path.
    # The probe does NOT receive the path; the parent tmpdir is mode 0700.
    if args.resource_dir:
        try:
            listed = os.listdir(args.resource_dir)
            result["listdir_attempt"] = {
                "path": args.resource_dir,
                "listed": listed,
                "error": None,
            }
        except PermissionError as e:
            result["listdir_attempt"] = {"path": args.resource_dir, "listed": None, "error": f"PermissionError: {e}"}
        except Exception as e:
            result["listdir_attempt"] = {"path": args.resource_dir, "listed": None, "error": f"{type(e).__name__}: {e}"}
        # Try opening a hypothetical authority.sqlite in that dir
        candidate = os.path.join(args.resource_dir, "authority.sqlite")
        try:
            conn = sqlite3.connect(candidate, timeout=2.0)
            try:
                conn.execute("SELECT 1 FROM protected_resources LIMIT 1").fetchone()
                result["db_open_attempt"] = {
                    "path": candidate,
                    "opened": True,
                    "writable": True,
                    "error": None,
                }
            except sqlite3.OperationalError as e:
                result["db_open_attempt"] = {
                    "path": candidate,
                    "opened": True,
                    "writable": True,
                    "error": f"OperationalError: {e}",
                }
            finally:
                conn.close()
        except sqlite3.OperationalError as e:
            result["db_open_attempt"] = {
                "path": candidate,
                "opened": False,
                "writable": False,
                "error": f"OperationalError: {e}",
            }
        except PermissionError as e:
            result["db_open_attempt"] = {
                "path": candidate,
                "opened": False,
                "writable": False,
                "error": f"PermissionError: {e}",
            }
        except Exception as e:
            result["db_open_attempt"] = {
                "path": candidate,
                "opened": False,
                "writable": False,
                "error": f"{type(e).__name__}: {e}",
            }

    # Attempt 2: try to read the audit key file by guessing its path
    if args.resource_dir:
        for candidate in [
            os.path.join(args.resource_dir, "executor_audit_key.bin"),
            os.path.join(args.resource_dir, "executor_credentials.json"),
        ]:
            try:
                with open(candidate, "rb") as f:
                    data = f.read()
                result.setdefault("secrets_read_attempt", []).append({
                    "path": candidate,
                    "readable": True,
                    "size_bytes": len(data),
                })
            except FileNotFoundError:
                result.setdefault("secrets_read_attempt", []).append({
                    "path": candidate,
                    "readable": False,
                    "error": "FileNotFoundError",
                })
            except PermissionError as e:
                result.setdefault("secrets_read_attempt", []).append({
                    "path": candidate,
                    "readable": False,
                    "error": f"PermissionError: {e}",
                })
            except Exception as e:
                result.setdefault("secrets_read_attempt", []).append({
                    "path": candidate,
                    "readable": False,
                    "error": f"{type(e).__name__}: {e}",
                })

    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())

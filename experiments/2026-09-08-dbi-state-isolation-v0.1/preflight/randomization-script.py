#!/usr/bin/env python3
"""
DBI State Isolation v0.1 v0.3 — Randomization script (F7 §8.2 gate).

Draws 3 OS-CSPRNG coin flips (one per replicate) to determine condition order:
  - 'fresh_first'   = execute fresh-condition invocations first, then repeated
  - 'repeated_first' = execute repeated-condition invocations first, then fresh

Writes the result to preflight/replicate-order-flips.json.

This script is FROZEN and HASHED at the FROZEN-FINAL commit. No claim that
replicate-order-flips.json exists until this script has been executed and
committed (per F7).
"""
import hashlib
import json
import secrets
import sys
from pathlib import Path

SANDBOX = Path("/home/fjventura20/devProjectsU/development-by-intent/experiments/2026-09-08-dbi-state-isolation-v0.1")
OUT_PATH = SANDBOX / "preflight" / "replicate-order-flips.json"
HASHES_PATH = SANDBOX / "preflight" / "artifact-hashes.json"


def main():
    if OUT_PATH.exists():
        # Refuse to overwrite an existing artifact at freeze time; the FROZEN-FINAL
        # commit must contain the EXACT same flips on both the operator-side and
        # the on-origin record. If a flip is missing, re-run only after a new
        # FROZEN-FINAL commit explicitly authorizes re-randomization.
        print(f"ERROR: {OUT_PATH} already exists. Refusing to overwrite.", file=sys.stderr)
        print(f"Existing content:", file=sys.stderr)
        print(OUT_PATH.read_text(), file=sys.stderr)
        sys.exit(1)

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    # OS-CSPRNG draws (one per replicate)
    rng = secrets.SystemRandom()
    flips = {
        f"replicate_{i}_coin_flip": rng.choice(["fresh_first", "repeated_first"])
        for i in (1, 2, 3)
    }
    # Also record the OS entropy source (audit)
    flips["os_entropy_source"] = "secrets.SystemRandom() (Python stdlib; OS entropy via /dev/urandom)"
    flips["script_sha256"] = "computed-after-write"  # placeholder; will be patched below
    flips["generated_at_utc"] = "computed-after-write"

    # Initial write to compute the script_sha256 + file sha256
    OUT_PATH.write_text(json.dumps(flips, indent=2, sort_keys=True) + "\n")
    file_sha = hashlib.sha256(OUT_PATH.read_bytes()).hexdigest()

    # Patch the placeholder values
    flips["script_sha256"] = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    flips["generated_at_utc"] = __import__("time").strftime("%Y-%m-%dT%H:%M:%SZ", __import__("time").gmtime())
    OUT_PATH.write_text(json.dumps(flips, indent=2, sort_keys=True) + "\n")
    final_file_sha = hashlib.sha256(OUT_PATH.read_bytes()).hexdigest()

    # Update artifact-hashes.json
    if HASHES_PATH.exists():
        hashes = json.loads(HASHES_PATH.read_text())
    else:
        hashes = {}
    hashes["replicate_order_flips_json"] = {
        "path": "preflight/replicate-order-flips.json",
        "sha256": final_file_sha,
        "bytes": OUT_PATH.stat().st_size,
        "generated_at_utc": flips["generated_at_utc"],
    }
    HASHES_PATH.write_text(json.dumps(hashes, indent=2, sort_keys=True) + "\n")

    # Emit
    print(f"WROTE: {OUT_PATH}")
    print(f"  sha256: {final_file_sha}")
    print(f"  bytes:  {OUT_PATH.stat().st_size}")
    print(f"  flips:  {[(k, v) for k, v in flips.items() if k.startswith('replicate_')]}")
    print(f"UPDATED: {HASHES_PATH}")


if __name__ == "__main__":
    main()

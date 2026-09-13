#!/usr/bin/env python3
"""
COA-E2 — generate_nonces.py

One-shot nonce generator. Run at freeze time, before any participant invocation.
Generates a 32-char hex nonce per arm using secrets.token_hex(16). Records
nonces to nonces.json with SHA-256 binding.

The nonces are unpredictable by both the participant and the evaluator.
They appear in the initialization packets but NEVER in the recall prompts.
"""

import argparse
import hashlib
import json
import secrets
import sys
from datetime import datetime, timezone
from pathlib import Path


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True,
                        help="Path to write nonces.json")
    parser.add_argument("--arms", nargs="+", default=["coa-governed", "control"],
                        help="Arm names for which to generate nonces")
    args = parser.parse_args()

    nonces = {arm: secrets.token_hex(16) for arm in args.arms}
    payload = {
        "frozen_at_utc": datetime.now(timezone.utc).isoformat(),
        "generator_seed_source": "Python secrets.token_hex(16) (os.urandom backed)",
        "nonces": nonces,
    }
    # canonical serialization for stable hashing
    canonical = json.dumps(payload, sort_keys=True, indent=2)
    payload["nonces_sha256"] = hashlib.sha256(canonical.encode("utf-8")).hexdigest()

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    print(f"generate_nonces.py: wrote {len(nonces)} nonces to {args.output}")
    for arm, nonce in nonces.items():
        print(f"  {arm}: {nonce}")
    print(f"  nonces_sha256: {payload['nonces_sha256']}")


if __name__ == "__main__":
    main()

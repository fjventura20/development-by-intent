#!/usr/bin/env python3
"""
INSA-ID-E1 per-(R, B, arm) reconstruction input builder (frozen pre-execution).

Builds the per-tuple clean-room input from the v2-frozen components:
  1. inputs/reconstruction-prompt.md (frozen BIB reconstruction prompt)
  2. inputs/identity-contract.txt (frozen BIB behavioral baseline)
  3. For Arm-M only: inputs/modification-specification.txt
  4. For Arm-C only: inputs/arm-c-directive.txt

The output is written to preflight/reconstruction-input-<R>-<B>-<arm>.txt
for each (R, B, arm) tuple in the frozen reconstruction/BS/arm sets.

Output is byte-identical for a given (R, B, arm) — deterministic, no
operator discretion after GO.
"""

import argparse
import hashlib
import os
import sys


FROZEN_RECONSTRUCTIONS = ("R1", "R2", "R3")
FROZEN_BS = ("B1",)
FROZEN_ARMS = ("C", "M")


def sha256_file(path: str) -> str:
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def build_for_arm(arm: str) -> bytes:
    """Build the reconstruction input bytes for a single arm."""
    parts = []
    # Part 1: frozen BIB reconstruction prompt
    parts.append(b"--- BEGIN FILE: inputs/reconstruction-prompt.md ---\n")
    parts.append(open("inputs/reconstruction-prompt.md", "rb").read())
    parts.append(b"\n--- END FILE: inputs/reconstruction-prompt.md ---\n\n")
    # Part 2: frozen BIB behavioral baseline (identity contract)
    parts.append(b"--- BEGIN FILE: inputs/identity-contract.txt ---\n")
    parts.append(open("inputs/identity-contract.txt", "rb").read())
    parts.append(b"\n--- END FILE: inputs/identity-contract.txt ---\n\n")
    # Part 3: per-arm directive
    if arm == "M":
        parts.append(b"--- BEGIN FILE: inputs/modification-specification.txt ---\n")
        parts.append(open("inputs/modification-specification.txt", "rb").read())
        parts.append(b"\n--- END FILE: inputs/modification-specification.txt ---\n")
    elif arm == "C":
        parts.append(b"--- BEGIN FILE: inputs/arm-c-directive.txt ---\n")
        parts.append(open("inputs/arm-c-directive.txt", "rb").read())
        parts.append(b"\n--- END FILE: inputs/arm-c-directive.txt ---\n")
    else:
        print(f"FATAL: unknown arm {arm}", file=sys.stderr)
        sys.exit(2)
    return b"".join(parts)


def main():
    ap = argparse.ArgumentParser(description="INSA-ID-E1 per-tuple reconstruction input builder")
    ap.add_argument("--out-dir", default="preflight", help="Output directory for per-tuple files")
    ap.add_argument("--verify-only", action="store_true", help="Verify frozen component SHAs only; do not write output")
    args = ap.parse_args()

    # Verify frozen component SHAs (from the proposal binding / MANIFEST)
    expected = {
        "inputs/reconstruction-prompt.md": "7d6d08196a825058fe677f0cf9b0367c4f8135a0ce50b2445bef54928f4084ce",
        "inputs/identity-contract.txt": "4582d768b696bbce41729ff05475ff9a8edf86c7b55668aaa46a230690e66159",
        "inputs/modification-specification.txt": None,  # any SHA acceptable; M-directive
        "inputs/arm-c-directive.txt": None,             # any SHA acceptable; C-directive
    }
    for path, exp_sha in expected.items():
        actual = sha256_file(path)
        if exp_sha is not None and actual != exp_sha:
            print(f"FATAL: {path} SHA mismatch", file=sys.stderr)
            print(f"  expected: {exp_sha}", file=sys.stderr)
            print(f"  actual:   {actual}", file=sys.stderr)
            sys.exit(2)
        print(f"OK: {path} sha256={actual}")

    if args.verify_only:
        return

    os.makedirs(args.out_dir, exist_ok=True)
    out_files = []
    for R in FROZEN_RECONSTRUCTIONS:
        for B in FROZEN_BS:
            for arm in FROZEN_ARMS:
                content = build_for_arm(arm)
                out_path = os.path.join(args.out_dir, f"reconstruction-input-{R}-{B}-{arm}.txt")
                with open(out_path, "wb") as f:
                    f.write(content)
                out_files.append(out_path)
                print(f"WROTE: {out_path} ({len(content)} bytes)")

    # Final summary
    print(f"\nWrote {len(out_files)} per-tuple reconstruction input files.")
    print("Each file is byte-identical for its (R, B, arm) tuple across runs.")


if __name__ == "__main__":
    main()
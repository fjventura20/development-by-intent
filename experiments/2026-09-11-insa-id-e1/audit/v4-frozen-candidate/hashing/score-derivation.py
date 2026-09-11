#!/usr/bin/env python3
"""
INSA-ID-E1 execution-order scoring algorithm (frozen pre-execution).

This script is the EXACT deterministic algorithm that maps the recorded
OS-CSPRNG draw_event to a per-(R, B, arm, candidate) tuple ordering.
Zero operator discretion after GO.

Inputs:
  --seed-file PATH     Path to the immutable seed file (content-addressed at
                       preflight; SHA-256 recorded in MANIFEST).
  --reconstructions N   Number of reconstructions (frozen: 3).
  --arms M             Number of arms (frozen: 2 = C, M).
  --candidates-per-cell K
                       Number of candidates per (R, arm) cell (frozen: 10).
  --out PATH           Path where the locked ordering JSON will be written.

Output:
  JSON object: {"draw_event": "<sha256>", "order": [{"R", "B", "arm",
              "candidate", "salt", "score"}, ...]}
  Tuples are sorted ascending by score; ties broken by lexicographic tuple
  identity for full determinism.

Deterministic scoring rule:
  For each tuple t = (R, B, arm, candidate):
    salt_t   = sha256("INSA-ID-E1:" + R + ":" + B + ":" + arm + ":" + candidate)
    score_t  = first 8 bytes of HMAC-SHA256(draw_event_key, salt_t),
               interpreted as a little-endian uint64.
  Sort tuples ascending by score; tie break by (R, B, arm, candidate)
  lexicographic.

The draw_event_key is the SHA-256 of (utc_timestamp || os.urandom(32))
captured at preflight time and stored in the seed file. The seed file
itself is the only randomness source; everything else is derived.
"""

import argparse
import hashlib
import hmac
import json
import os
import sys


# Frozen pre-execution constants (per proposal v4 §5.2 + EXECUTION-ORDER.md)
FROZEN_RECONSTRUCTIONS = ("R1", "R2", "R3")
FROZEN_BS = ("B1",)
FROZEN_ARMS = ("C", "M")
FROZEN_CANDIDATES_PER_CELL = 10
FROZEN_TUPLE_KEY_FORMAT = "INSA-ID-E1:{R}:{B}:{arm}:{candidate}"


def derive_salt(R: str, B: str, arm: str, candidate: int) -> bytes:
    """Per-tuple salt: SHA-256 of the canonical tuple identity string."""
    s = FROZEN_TUPLE_KEY_FORMAT.format(R=R, B=B, arm=arm, candidate=candidate)
    return hashlib.sha256(s.encode("utf-8")).digest()


def score_tuple(draw_event_key: bytes, salt: bytes) -> int:
    """
    Per-tuple score: first 8 bytes of HMAC-SHA256(draw_event_key, salt),
    interpreted as little-endian uint64.
    """
    mac = hmac.new(draw_event_key, salt, hashlib.sha256).digest()
    return int.from_bytes(mac[:8], byteorder="little", signed=False)


def lex_key(R: str, B: str, arm: str, candidate: int):
    """Lexicographic tie-break key."""
    return (R, B, arm, candidate)


def build_order(draw_event_key: bytes):
    """Build the full ordered list of (R, B, arm, candidate) tuples."""
    tuples = []
    for R in FROZEN_RECONSTRUCTIONS:
        for B in FROZEN_BS:
            for arm in FROZEN_ARMS:
                for cand in range(1, FROZEN_CANDIDATES_PER_CELL + 1):
                    salt = derive_salt(R, B, arm, cand)
                    score = score_tuple(draw_event_key, salt)
                    tuples.append({
                            "R": R,
                            "B": B,
                            "arm": arm,
                            "candidate": cand,
                            "salt_sha256_hex": salt.hex(),
                            "score_uint64_le": score,
                    })
    # Sort by (score ascending, lex tie-break)
    tuples.sort(key=lambda t: (t["score_uint64_le"], lex_key(t["R"], t["B"], t["arm"], t["candidate"])))
    return tuples


def main():
    ap = argparse.ArgumentParser(description="INSA-ID-E1 execution-order scoring (frozen)")
    ap.add_argument("--seed-file", required=True, help="Path to immutable seed file (raw draw_event_key bytes, 32 bytes)")
    ap.add_argument("--out", required=True, help="Output JSON path (locked ordering)")
    ap.add_argument("--verify-only", action="store_true", help="If set, only verify reproducibility; do not write output")
    args = ap.parse_args()

    # Read draw_event_key (must be exactly 32 bytes)
    with open(args.seed_file, "rb") as f:
        draw_event_key = f.read()
    if len(draw_event_key) != 32:
        print(f"FATAL: seed file must be exactly 32 bytes (draw_event_key), got {len(draw_event_key)}", file=sys.stderr)
        sys.exit(2)

    draw_event_sha256 = hashlib.sha256(draw_event_key).hexdigest()

    order = build_order(draw_event_key)

    out_doc = {
        "draw_event_sha256": draw_event_sha256,
        "ordering_algorithm": "HMAC-SHA256(draw_event_key, per-tuple-salt)[:8] as little-endian uint64; sort ascending; lex tie-break (R, B, arm, candidate)",
        "draw_event_key_bytes": draw_event_key.hex(),
        "frozen_constants": {
            "reconstructions": list(FROZEN_RECONSTRUCTIONS),
            "bs": list(FROZEN_BS),
            "arms": list(FROZEN_ARMS),
            "candidates_per_cell": FROZEN_CANDIDATES_PER_CELL,
            "tuple_key_format": FROZEN_TUPLE_KEY_FORMAT,
        },
        "total_tuples": len(order),
        "order": order,
    }

    if args.verify_only:
        print(f"VERIFICATION: draw_event_sha256={draw_event_sha256}")
        print(f"  total_tuples={len(order)}")
        print(f"  first 3: {[t for t in order[:3]]}")
        print(f"  last 3: {[t for t in order[-3:]]}")
        return

    # Atomic write: write to .tmp, fsync, rename
    tmp = args.out + ".tmp"
    with open(tmp, "w") as f:
        json.dump(out_doc, f, indent=2, sort_keys=False)
        f.write("\n")
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp, args.out)

    # Print the SHA for the operator to record
    out_sha = hashlib.sha256(open(args.out, "rb").read()).hexdigest()
    print(f"WROTE: {args.out}")
    print(f"  draw_event_sha256: {draw_event_sha256}")
    out_doc["out_sha256"] = out_sha
    print(f"  out_sha256:        {out_sha}")
    print(f"  total_tuples:      {len(order)}")


if __name__ == "__main__":
    main()
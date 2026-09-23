#!/usr/bin/env python3
"""Generate exactly six v0.4.1 runtime nonces after a future freeze decision.

Keys: coa-init, coa-digest, coa-nonce, control-init, control-digest,
control-nonce. All six are pairwise-unique 32-hex lowercase strings.
"""
import argparse, json, secrets
from pathlib import Path


NONCE_KEYS = ["coa-init", "coa-digest", "coa-nonce",
              "control-init", "control-digest", "control-nonce"]


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--output", type=Path, required=True)
    a = p.parse_args()
    nonces = {k: secrets.token_hex(16) for k in NONCE_KEYS}
    if len(set(nonces.values())) != len(nonces):
        raise SystemExit("nonce collision; retry")
    a.output.parent.mkdir(parents=True, exist_ok=True)
    a.output.write_text(json.dumps({"nonces": nonces}, indent=2) + "\n")
    print(json.dumps({"count": len(nonces),
                      "keys": sorted(nonces),
                      "output": str(a.output)}))


if __name__ == "__main__":
    main()

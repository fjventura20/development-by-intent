#!/usr/bin/env python3
"""Narrow formal-host signing worker.

stdin: base64(raw Ed25519 message bytes)
argv[1]: owner-readable private-key path
stdout: base64(signature)

The worker returns signatures only.  Private key material never crosses the
process boundary.
"""
import base64
import sys

# Anchor imports to the installed trusted root, not the caller's environment.
sys.path.insert(0, "/opt/ate-poc-v010")

from qa_poc.crypto import load_ed25519_private_pem

if len(sys.argv) != 2:
    raise SystemExit("usage: host_signer_worker.py PRIVATE_KEY_PATH")
msg = base64.b64decode(sys.stdin.buffer.read(), validate=True)
priv = load_ed25519_private_pem(sys.argv[1])
sig = priv.sign(msg)
sys.stdout.write(base64.b64encode(sig).decode("ascii"))

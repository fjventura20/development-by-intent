"""ATE P1 v0.1.1 — Canonicalization, signing, HMAC, SHA-256.

Local-only cryptography. Stdlib + hashlib + hmac + secrets. Reuses the
canonicalization discipline from the upstream ATE v0.3.1 harness
(RFC-8785-style sorted-key JSON without Unicode normalization).
"""
from __future__ import annotations

import hashlib
import hmac
import json
import secrets
from typing import Any


def canonicalize_json(obj: Any) -> str:
    """RFC 8785-style canonical JSON: sorted keys, no whitespace, UTF-8."""
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def canonical_bytes(obj: Any) -> bytes:
    return canonicalize_json(obj).encode("utf-8")


def fingerprint_obj(obj: Any) -> str:
    return hashlib.sha256(canonical_bytes(obj)).hexdigest()


def sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def hmac_sha256_hex(key: bytes, data: bytes) -> str:
    return hmac.new(key, data, hashlib.sha256).hexdigest()


def hmac_sha256_bytes(key: bytes, data: bytes) -> bytes:
    return hmac.new(key, data, hashlib.sha256).digest()


def random_hex(num_bytes: int) -> str:
    return secrets.token_hex(num_bytes)

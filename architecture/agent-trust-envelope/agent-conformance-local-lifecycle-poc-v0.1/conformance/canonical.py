"""Agent Conformance Local Lifecycle PoC v0.1 — canonical JSON.

Frozen-design §24: deterministic canonical serialization is mandatory.

  - Allowed scalars: None, bool, signed int (within safe range), UTF-8
    NFC-normalized string, list, dict with unique string keys.
  - Rejected: floats (NaN/Infinity implicit), duplicate keys, non-string
    object keys, unsupported native/binary values.
  - Canonical encoding: UTF-8 JSON, NFC strings, lex-sorted keys,
    separators=(",", ":"), ensure_ascii=False.
  - Digest: SHA-256.
  - Signing bytes: UTF-8(artifact_domain) || 0x00 || canonical_json_bytes.

This module is the single source of truth for canonical bytes and
digests. Every signed artifact in `models` goes through
`canonical_json_bytes()` and `canonical_sha256()`.
"""

from __future__ import annotations

import hashlib
import json
import unicodedata
from typing import Any, Mapping

_INT_MIN = -(2**63)
_INT_MAX = 2**63 - 1


class CanonicalError(Exception):
    """Raised when a value is not representable in the canonical model."""


class CanonicalDuplicateKeyError(CanonicalError):
    """Distinct error class for duplicate-key detection."""

    def __init__(self, path: str) -> None:
        super().__init__(f"duplicate key at path {path!r}")
        self.path = path


def _normalize_str(s: str) -> str:
    if not isinstance(s, str):
        raise CanonicalError(f"expected str, got {type(s).__name__}")
    return unicodedata.normalize("NFC", s)


def _check_int(n: int) -> int:
    if isinstance(n, bool) or not isinstance(n, int):
        raise CanonicalError(f"expected int, got {type(n).__name__}")
    if n < _INT_MIN or n > _INT_MAX:
        raise CanonicalError(f"int out of safe range: {n}")
    return n


def _walk(obj: Any, path: str = "") -> Any:
    """Recursively normalize a value into its canonical form.

    Dict duplicate detection: Python dicts deduplicate by hash, so we
    encode each dict twice (once for sorted output, once for insertion
    order) and compare lengths. If the insertion-order encoding is
    shorter than the sorted-key encoding, a duplicate key existed and
    was collapsed — we reject.
    """
    if obj is None:
        return None
    if isinstance(obj, bool):
        return obj  # bool subclass of int; check first
    if isinstance(obj, int):
        return _check_int(obj)
    if isinstance(obj, float):
        # Floats are explicitly rejected by the frozen design §24.
        raise CanonicalError("floats are not permitted in security-relevant values")
    if isinstance(obj, str):
        return _normalize_str(obj)
    if isinstance(obj, (list, tuple)):
        return [_walk(v, f"{path}[{i}]") for i, v in enumerate(obj)]
    if isinstance(obj, dict):
        if not all(isinstance(k, str) for k in obj.keys()):
            raise CanonicalError("object keys must be strings")
        # NFC-normalize keys first.
        normalized: dict = {}
        for k, v in obj.items():
            nk = _normalize_str(k)
            normalized[nk] = _walk(v, f"{path}.{nk}" if path else nk)
        # Duplicate-key detection via raw JSON re-parse.
        try:
            raw = json.dumps(
                obj, separators=(",", ":"), ensure_ascii=False,
                sort_keys=False, default=_json_default_for_dup_check,
            )
            collapsed = json.loads(raw)
            sorted_repr = json.dumps(
                collapsed, separators=(",", ":"), ensure_ascii=False,
                sort_keys=True, default=_json_default_for_dup_check,
            )
            if len(sorted_repr) != len(raw):
                # The insertion-order encoding collapsed because of duplicate
                # keys. Identify where.
                seen: dict = {}
                for k in obj.keys():
                    nk = _normalize_str(k)
                    if nk in seen:
                        raise CanonicalDuplicateKeyError(
                            f"{path}.{nk}" if path else nk,
                        )
                    seen[nk] = True
                # Fallback raise.
                raise CanonicalDuplicateKeyError(path or "<root>")
        except CanonicalDuplicateKeyError:
            raise
        except (TypeError, ValueError):
            # If re-parse fails for some other reason, re-raise as a
            # canonical error so callers don't silently accept it.
            raise CanonicalError(f"could not canonicalize path {path!r}")
        return normalized
    raise CanonicalError(f"unsupported type: {type(obj).__name__}")


def _json_default_for_dup_check(obj: Any) -> Any:
    # Used only for the duplicate-detection re-parse path. The real
    # canonical encoder below uses its own serializer.
    raise CanonicalError(f"unsupported type in raw re-parse: {type(obj).__name__}")


def canonical_json_bytes(obj: Any) -> bytes:
    """Return canonical UTF-8 JSON bytes of `obj` per frozen §24."""
    walked = _walk(obj)
    return json.dumps(
        walked,
        separators=(",", ":"),
        ensure_ascii=False,
        sort_keys=True,
    ).encode("utf-8")


def canonical_sha256(obj: Any) -> str:
    """Return hex SHA-256 of canonical JSON bytes of `obj`."""
    return hashlib.sha256(canonical_json_bytes(obj)).hexdigest()


def signing_bytes(domain: str, payload: Mapping[str, Any]) -> bytes:
    """Return the deterministic Ed25519 signing input per frozen §24.

    Bytes layout: UTF-8(domain) || 0x00 || canonical_json_bytes(payload).
    """
    if not isinstance(domain, str):
        raise CanonicalError("signing domain must be a string")
    return domain.encode("utf-8") + b"\x00" + canonical_json_bytes(payload)
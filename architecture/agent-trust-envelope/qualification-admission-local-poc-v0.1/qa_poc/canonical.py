"""ATE Qualification & Admission Local PoC v0.1 — canonical JSON.

Implements the v0.1.2 design §8 canonical data model:

  - Allowed scalar types: null, bool, signed int (within safe range),
    UTF-8 NFC-normalized string, array, object with unique string keys.
  - Rejected: floats, NaN, Infinity, duplicate keys, non-string object keys,
    unsupported native/binary values.
  - Canonical encoding: UTF-8 JSON, NFC strings, lex-sorted keys,
    separators=(",", ":"), ensure_ascii=False.
  - Digest: SHA-256.

This module is the single source of truth for canonical bytes and
digests in the PoC. Every signed artifact in qa_poc.models goes through
`canonical_json_bytes()` and `canonical_sha256()`.
"""

from __future__ import annotations

import hashlib
import json
import re
import unicodedata
from typing import Any

# safe-integer range for the PoC; outside this we reject
_INT_MIN = -(2**63)
_INT_MAX = 2**63 - 1


class CanonicalError(Exception):
    """Raised when a value is not representable in the canonical model."""


class CanonicalDuplicateKeyError(CanonicalError):
    """Distinct error so QA-P10 can assert on parser-reject of dup keys."""


def _normalize_str(s: str) -> str:
    """NFC-normalize a string. Reject non-string."""
    if not isinstance(s, str):
        raise CanonicalError(f"expected str, got {type(s).__name__}")
    return unicodedata.normalize("NFC", s)


def _check_int(n: int) -> int:
    if not isinstance(n, int) or isinstance(n, bool):
        raise CanonicalError(f"expected int, got {type(n).__name__}")
    if n < _INT_MIN or n > _INT_MAX:
        raise CanonicalError(f"int out of safe range: {n}")
    return n


def _walk(obj: Any, seen_keys: tuple = ()) -> Any:
    """Recursively normalize a value into its canonical form.

    For dicts we track keys along the path so that duplicate keys at
    any nesting depth are detected and rejected. We rebuild dicts with
    sorted-string keys; if any duplicate would arise we raise.
    """
    if obj is None:
        return None
    if isinstance(obj, bool):
        return obj  # bool is a subclass of int in Python; check first
    if isinstance(obj, int):
        return _check_int(obj)
    if isinstance(obj, float):
        # Floats are explicitly rejected by the frozen design §8.
        raise CanonicalError("floats are not permitted in security-relevant values")
    if isinstance(obj, str):
        return _normalize_str(obj)
    if isinstance(obj, (list, tuple)):
        return [_walk(v) for v in obj]
    if isinstance(obj, dict):
        if not all(isinstance(k, str) for k in obj.keys()):
            raise CanonicalError("object keys must be strings")
        # Detect duplicate keys after NFC normalization. Python dicts
        # already deduplicate by hash, so we walk via items() and use a
        # JSON re-parse trick: encode with sort_keys=True twice and
        # confirm the encoded length does not collapse. Simpler: collect
        # all keys, NFC-normalize, dedup.
        nfc_keys = [_normalize_str(k) for k in obj.keys()]
        if len(set(nfc_keys)) != len(nfc_keys):
            raise CanonicalDuplicateKeyError("duplicate key in object")
        # Walk values; build a new dict with NFC-normalized keys, sorted.
        new_items = []
        for k, v in obj.items():
            nk = _normalize_str(k)
            nv = _walk(v)
            new_items.append((nk, nv))
        new_items.sort(key=lambda kv: kv[0])
        return {k: v for k, v in new_items}
    raise CanonicalError(f"unsupported type: {type(obj).__name__}")


def canonicalize(obj: Any) -> Any:
    """Return the canonical in-memory representation.

    The result is JSON-encodable (recursively) and contains no floats,
    no duplicate keys, and NFC-normalized strings. We then JSON-encode
    it to get the canonical bytes.
    """
    return _walk(obj)


class _DuplicateKeyJSONDecoder:
    """Tiny JSON decoder that rejects duplicate keys at parse time.

    Per design §9: "duplicate key -> parser rejection". We detect
    duplicates during JSON.loads by overriding `object_pairs_hook`.
    """

    def __init__(self) -> None:
        import json as _json
        self._json = _json

    def decode(self, s: str):
        return self._json.loads(
            s,
            object_pairs_hook=self._object_pairs_hook,
        )

    def _object_pairs_hook(self, pairs):
        seen = set()
        out = {}
        for k, v in pairs:
            if k in seen:
                raise CanonicalDuplicateKeyError(f"duplicate key in JSON: {k!r}")
            seen.add(k)
            out[k] = v
        return out


def canonicalize_json_text(text: str) -> Any:
    """Parse JSON text and reject duplicate keys at parse time.

    This is the §9 "duplicate key -> parser rejection" gate. Useful for
    verifying that a stringified payload from an external source has
    not been crafted with hidden duplicate keys.
    """
    return _DuplicateKeyJSONDecoder().decode(text)


def canonical_json_bytes(obj: Any) -> bytes:
    """Return canonical JSON bytes (UTF-8) for `obj`.

    Per design §8:
      separators=(",", ":")
      ensure_ascii=False  (so non-ASCII chars are not \\u-escaped after NFC)
      sort_keys=True (we have already done that in _walk, but pass it too
                      to be explicit)
    """
    can = canonicalize(obj)
    return json.dumps(
        can,
        separators=(",", ":"),
        ensure_ascii=False,
        sort_keys=True,
    ).encode("utf-8")


def canonical_sha256(obj: Any) -> str:
    """Return the hex SHA-256 digest of canonical_json_bytes(obj)."""
    return hashlib.sha256(canonical_json_bytes(obj)).hexdigest()


# Sign-bytes builder — domain || 0x00 || canonical_payload.
def signing_bytes(domain: str, payload_obj: Any) -> bytes:
    """Return the exact byte sequence that must be signed:

        UTF8(domain) || 0x00 || canonical_json_bytes(payload_obj)
    """
    if not isinstance(domain, str):
        raise CanonicalError("signing domain must be a string")
    return domain.encode("utf-8") + b"\x00" + canonical_json_bytes(payload_obj)

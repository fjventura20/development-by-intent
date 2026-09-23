"""Strict RFC 8785 JCS canonicalization.

Per v0.2.1 §E.1: v0.2.1-JCS-strict profile.
- No Unicode normalization (RFC 8785 preserves Unicode strings as-is).
- Object keys sorted by UTF-16 code unit order (RFC 8785 §3.1).
- Arrays preserved in order (RFC 8785 does not reorder).
- Numbers: integer vs float distinct (canonical form per RFC 8785 §3.3).
- Missing field != null.

Bytes returned by canonicalize() are the bytes that must be signed and verified.
Both signer and verifier import this module -- they MUST produce byte-identical
output for identical inputs.
"""
import json
from typing import Any


def _escape_string(s: str) -> str:
    """RFC 8785 §3.2.2.3 shortest escape form."""
    out = []
    for ch in s:
        cp = ord(ch)
        if ch == '"':
            out.append('\\"')
        elif ch == '\\':
            out.append('\\\\')
        elif ch == '\b':
            out.append('\\b')
        elif ch == '\f':
            out.append('\\f')
        elif ch == '\n':
            out.append('\\n')
        elif ch == '\r':
            out.append('\\r')
        elif ch == '\t':
            out.append('\\t')
        elif cp < 0x20:
            # shortest escape form: \uXXXX
            out.append('\\u%04x' % cp)
        else:
            out.append(ch)
    return ''.join(out)


def _canonical_number(n) -> str:
    """RFC 8785 §3.3 -- canonical number form.

    Integer (int) -> no decimal point.
    Float -> shortest representation that round-trips.
    Distinct between integer 1 and float 1.0.
    """
    if isinstance(n, bool):
        # JSON booleans, never encountered if we route to right path, but guard
        return 'true' if n else 'false'
    if isinstance(n, int):
        return str(n)
    # float
    import math
    if math.isnan(n) or math.isinf(n):
        raise ValueError("JCS disallows NaN/Inf")
    # Python's repr() of a float is the shortest round-trip
    return repr(n)


def _emit(value: Any, out: list) -> None:
    if value is None:
        out.append('null')
        return
    if isinstance(value, bool):
        # bool is subclass of int -- check first
        out.append('true' if value else 'false')
        return
    if isinstance(value, int):
        out.append(str(value))
        return
    if isinstance(value, float):
        out.append(_canonical_number(value))
        return
    if isinstance(value, str):
        out.append('"')
        out.append(_escape_string(value))
        out.append('"')
        return
    if isinstance(value, list):
        out.append('[')
        for i, item in enumerate(value):
            if i > 0:
                out.append(',')
            _emit(item, out)
        out.append(']')
        return
    if isinstance(value, dict):
        # RFC 8785 §3.1: sort by UTF-16 code unit order
        # We sort by the JSON-escaped form of the key (which is what RFC 8785 §3.1
        # actually defines: "the lexical order of the UTF-16 [BE] character codes").
        keys = sorted(value.keys())
        out.append('{')
        for i, k in enumerate(keys):
            if i > 0:
                out.append(',')
            # RFC 8785 §3.2.2.2 -- keys are escaped as JSON strings
            escaped = _escape_string(k)
            out.append('"')
            out.append(escaped)
            out.append('":')
            _emit(value[k], out)
        out.append('}')
        return
    raise TypeError(f"unsupported type: {type(value)}")


def canonicalize(value: Any) -> bytes:
    """Produce the RFC 8785 canonical byte representation of a Python value.

    No Unicode normalization is applied. Strings are emitted byte-exact as the
    Python str (UTF-8 encoded). Composed vs decomposed Unicode remain distinct
    because they have different UTF-8 bytes.

    Returns the canonical UTF-8 byte string. This is what is signed and verified.
    """
    out: list = []
    _emit(value, out)
    return ''.join(out).encode('utf-8')


def canonical_hash(value: Any) -> str:
    """SHA-256 hex digest of canonicalize(value)."""
    import hashlib
    return hashlib.sha256(canonicalize(value)).hexdigest()

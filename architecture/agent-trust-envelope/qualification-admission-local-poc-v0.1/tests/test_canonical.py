"""Canonicalization self-tests (§9)."""

from __future__ import annotations

import json

import pytest

from qa_poc.canonical import (
    CanonicalDuplicateKeyError,
    CanonicalError,
    canonical_json_bytes,
    canonical_sha256,
    canonicalize_json_text,
)


def test_reordered_keys_produce_same_canonical_bytes():
    obj_a = {"a": 1, "b": 2, "c": 3}
    obj_b = {"c": 3, "a": 1, "b": 2}
    assert canonical_sha256(obj_a) == canonical_sha256(obj_b)


def test_reordered_keys_same_canonical_bytes():
    obj_a = {"a": 1, "b": 2, "c": 3}
    obj_b = {"c": 3, "a": 1, "b": 2}
    b_a = canonical_json_bytes(obj_a)
    b_b = canonical_json_bytes(obj_b)
    assert b_a == b_b
    assert b_a == b'{"a":1,"b":2,"c":3}'


def test_semantic_mutation_changes_digest():
    a = {"a": 1, "b": 2}
    b = {"a": 1, "b": 3}
    assert canonical_sha256(a) != canonical_sha256(b)


def test_duplicate_key_rejected_at_parse_time():
    """Python dicts collapse duplicate keys on construction; we test
    the parser-level rejection instead."""
    text = '{"a": 1, "a": 2}'
    with pytest.raises(CanonicalDuplicateKeyError):
        canonicalize_json_text(text)


def test_float_rejected():
    with pytest.raises(CanonicalError):
        canonical_sha256({"a": 1.5})


def test_nan_rejected():
    with pytest.raises(CanonicalError):
        canonical_sha256({"a": float("nan")})


def test_non_string_object_keys_rejected():
    with pytest.raises(CanonicalError):
        canonical_sha256({1: "x"})


def test_nfc_normalization():
    # U+00E9 (composed) vs U+0065 U+0301 (decomposed) should NFC-normalize
    composed = "café"
    decomposed = "cafe\u0301"
    assert canonical_sha256({"x": composed}) == canonical_sha256({"x": decomposed})


def test_unicode_separators_ensure_ascii_false():
    obj = {"x": "naïve"}
    b = canonical_json_bytes(obj)
    # ensure_ascii=False means non-ASCII chars are kept literal
    assert "naïve" in b.decode("utf-8")
    # not escaped
    assert "\\u" not in b.decode("utf-8")


def test_int_overflow_rejected():
    with pytest.raises(CanonicalError):
        canonical_sha256({"a": 2**100})

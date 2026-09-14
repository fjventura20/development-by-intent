"""TGE-PoC orchestrator.

Runs:
1. The 7 normative canonicalization test vectors (v0.2.1 §E.5)
2. The 6 structural cases (v0.2.1 §J)

Emits a JSON evidence report under evidence/.
"""
import json
import os
import sys
import time
import hashlib

# Import the canonicalization module and the cases module from this dir
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from canonicalization import canonicalize, canonical_hash


# ---- Canonicalization test vectors (v0.2.1 §E.5) ----

VECTORS = [
    {
        "id": "vector_1_unicode_composed_vs_decomposed",
        # Use \u escapes to force distinct UTF-8 byte sequences
        # input_a: composed U+00E9
        # input_b: decomposed U+0065 U+0301
        "input_a": {"name": "caf\u00e9"},
        "input_b": {"name": "cafe\u0301"},
        "distinct_expected": True,
        "description": "Composed (NFC) and decomposed (NFD) Unicode MUST be distinct.",
    },
    {
        "id": "vector_2_null_vs_omitted",
        "input_a": {"a": 1},                # no b
        "input_b": {"a": 1, "b": None},     # explicit null
        "distinct_expected": True,
        "description": "Missing field and explicit null MUST be distinct.",
    },
    {
        "id": "vector_3_array_ordering_preserved",
        "input_a": {"xs": ["b", "a", "c"]},
        "input_b": {"xs": ["a", "b", "c"]},
        "distinct_expected": True,
        "description": "RFC 8785 preserves array order; reorderings MUST produce distinct bytes.",
    },
    {
        "id": "vector_4_object_member_ordering",
        "input_a": {"b": 2, "a": 1},
        "input_b": {"a": 1, "b": 2},
        "distinct_expected": False,  # both should canonicalize to same order
        "description": "RFC 8785 sorts object keys; both forms canonicalize identically.",
    },
    {
        "id": "vector_5_number_serialization",
        "input_a": {"n": 1},
        "input_b": {"n": 1.0},
        "distinct_expected": True,
        "description": "Integer 1 and float 1.0 MUST produce distinct canonical bytes.",
    },
    {
        "id": "vector_6_escaped_characters",
        "input_a": {"s": "a\nb"},     # literal newline in source -> \n in JSON
        "input_b": {"s": "a\u000ab"},  # \u000a escape -> also \n in JSON
        "distinct_expected": False,  # RFC 8785 shortens \uXXXX to literal char
        "description": "RFC 8785 §3.2.2.3 shortest escape form. \\u000a and \\n are equivalent.",
    },
    {
        "id": "vector_7_unknown_extension_fields",
        "input_a": {"a": 1, "experimental": "v"},
        "input_b": {"experimental": "v", "a": 1},
        "distinct_expected": False,  # sorted alphabetically -> identical
        "description": "Unknown fields are preserved; RFC 8785 sorts keys so both forms canonicalize identically.",
    },
]


def run_canonicalization_tests():
    results = []
    for v in VECTORS:
        bytes_a = canonicalize(v["input_a"])
        bytes_b = canonicalize(v["input_b"])
        distinct = (bytes_a != bytes_b)
        ok = (distinct == v["distinct_expected"])
        results.append({
            "id": v["id"],
            "description": v["description"],
            "canonical_a_hex": bytes_a.hex(),
            "canonical_b_hex": bytes_b.hex(),
            "distinct_observed": distinct,
            "distinct_expected": v["distinct_expected"],
            "pass": ok,
        })
    return results


# ---- Six cases ----

def run_six_cases():
    from cases import run_all_cases
    return run_all_cases()


def main():
    out_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "evidence")
    os.makedirs(out_dir, exist_ok=True)

    started_utc = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

    print("=" * 60)
    print("TGE-PoC: minimal structural proof-of-concept (v0.2.1)")
    print("Attestation: A1 -- FIXTURE_ATTESTATION (simulated)")
    print("Started UTC:", started_utc)
    print("=" * 60)
    print()

    # 1. Canonicalization tests
    print("--- 7 Canonicalization test vectors ---")
    canon_results = run_canonicalization_tests()
    canon_pass = 0
    for r in canon_results:
        status = "PASS" if r["pass"] else "FAIL"
        print(f"  [{status}] {r['id']}: {r['description']}")
        if r["pass"]:
            canon_pass += 1
    print(f"  -> {canon_pass}/7 canonicalization vectors PASS")
    print()

    # 2. Six cases
    print("--- 6 structural cases ---")
    case_results = run_six_cases()
    case_pass = 0
    for r in case_results:
        status = "PASS" if r["pass"] else "FAIL"
        actual_verdict = r["actual"].get("verdict", "?")
        actual_code = r["actual"].get("stop_code", "")
        actual_tuple = r["actual"].get("assurance_tuple", "")
        print(f"  [{status}] {r['case']}: expected={r['expected']}, actual_verdict={actual_verdict}, actual_code={actual_code}, tuple={actual_tuple}")
        if r["pass"]:
            case_pass += 1
    print(f"  -> {case_pass}/6 structural cases PASS")
    print()

    overall_pass = (canon_pass == 7) and (case_pass == 6)
    finished_utc = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

    # Save evidence
    report = {
        "schema_version": "TGE-POC-EVIDENCE/0.2.1",
        "started_utc": started_utc,
        "finished_utc": finished_utc,
        "attestation_label": "A1_FIXTURE_ATTESTATION",
        "canonicalization_profile": "v0.2.1-JCS-strict",
        "canonicalization_tests": {
            "count": 7,
            "passed": canon_pass,
            "results": canon_results,
        },
        "structural_cases": {
            "count": 6,
            "passed": case_pass,
            "results": case_results,
        },
        "overall_pass": overall_pass,
        "strongest_permitted_claim": (
            "We demonstrated that a verifier can cryptographically distinguish a "
            "correctly constructed runtime/session governance binding from selected "
            "provenance, freshness, verifier-independence, issuer, and runtime/"
            "signing-substitution failures under a simulated attestation environment."
        ),
        "forbidden_claims": [
            "AI model understood the governance",
            "AI model agreed cognitively with the governance",
            "AI agent will obey the governance",
            "Value Architecture behavior was established",
            "Hardware TPM security was established",
            "Host compromise was defeated",
            "General agent trustworthiness was proven",
            "Production readiness was established",
        ],
    }

    evidence_path = os.path.join(out_dir, "poc_evidence.json")
    with open(evidence_path, "w") as f:
        json.dump(report, f, indent=2)
    print(f"Evidence written to: {evidence_path}")

    print()
    print("=" * 60)
    print(f"OVERALL: {'STRUCTURAL_POC_PASS' if overall_pass else 'STRUCTURAL_POC_FAIL'}")
    print("=" * 60)

    return 0 if overall_pass else 1


if __name__ == "__main__":
    sys.exit(main())

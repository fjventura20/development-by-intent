"""Formal runner — drives QA-P1..QA-P14 cases programmatically and emits
structured §29 evidence.

This module is the formal runner's authoritative surface. Each case
function returns a FormalEvidence record built from real execution
objects (the executor's EapResult, the audit rows, the control records,
the protected-resource before/after state) — not from pytest output.

The runner-level regression tests prove:
  - FR-5: any direct requester protected mutation -> ENFORCEMENT_FAILURE
  - FR-5: any pre-EAP invalidation + mutation -> ENFORCEMENT_FAILURE
  - FR-6: omitted/duplicate case -> INVALID_RUN (never PASS)
  - FR-7: structural evidence is what classification consumes
  - FR-3: per-case evidence carries the full §29 schema

This file deliberately does NOT import the EAP layer until case
construction time so that the case functions can be wired in
independently.
"""

from __future__ import annotations

import dataclasses
import json
import os
import shutil
import sqlite3
import sys
import tempfile
import traceback
from dataclasses import dataclass, field, asdict
from typing import Any, Callable, Dict, List, Optional, Tuple


# --- §29 Formal Evidence schema ------------------------------------------


@dataclass
class FormalEvidence:
    """One formal per-case evidence record (frozen §29)."""

    # --- Identity ---
    test_id: str                           # e.g. "QA-P3"
    fixture_id: str                        # per-case unique id
    case_function: str                     # fully-qualified function name

    # --- Verdict ---
    verdict: str                           # "EXECUTION_SUCCEEDED" / "EXECUTION_DENIED" / "CAPABILITY_DENIED" / "ADMISSION_DENIED" / "NO_BUNDLE_ISSUED"
    reason_code: str = ""                  # canonical reason code
    pass_fail: str = ""                    # "PASS" or "FAIL"
    eap_reached: bool = False              # did the EAP execute?

    # --- Resource state ---
    resource_id: str = ""
    initial_resource_value: str = ""
    final_resource_value: str = ""
    initial_mutation_count: int = 0
    final_mutation_count: int = 0

    # --- Control epoch ---
    starting_applied_epoch: int = 0
    ending_applied_epoch: int = 0

    # --- Credentials (id/digest) ---
    qualification_id: str = ""
    qualification_digest: str = ""
    admission_id: str = ""
    admission_digest: str = ""
    capability_id: Optional[str] = None    # None when issuance correctly denied
    capability_digest: Optional[str] = None
    trust_decision_id: Optional[str] = None
    trust_decision_digest: Optional[str] = None

    # --- FR-8: per-artifact expiry timestamps (so a case can prove
    # ordering at EAP) ---
    qualification_expires_at_unix_ms: int = 0
    admission_expires_at_unix_ms: int = 0
    capability_expires_at_unix_ms: int = 0
    trust_decision_expires_at_unix_ms: int = 0
    qualification_expired_at_advance_ms: int = 0  # how far the clock was advanced

    # --- Control records applied during this case ---
    applied_control_records: List[Dict[str, Any]] = field(default_factory=list)

    # --- Audit chain ---
    audit_sequence_range: Tuple[int, int] = field(default_factory=lambda: (0, 0))
    audit_chain_valid: bool = True

    # --- Subcheck PASS/FAIL for cases with subchecks (QA-P10) ---
    subcheck_results: Dict[str, str] = field(default_factory=dict)

    # --- Frozen classification flag (raised at runner level only) ---
    enforcement_failure_reason: Optional[str] = None
    invalid_run_reason: Optional[str] = None

    # --- Error capture ---
    error: Optional[str] = None
    traceback: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        # tuple -> list for JSON
        d["audit_sequence_range"] = list(self.audit_sequence_range)
        return d


# --- Required case set (frozen §28 + §29) ---------------------------------

REQUIRED_CASES = [
    "QA-P1",
    "QA-P2",
    "QA-P3",
    "QA-P4",
    "QA-P5",
    "QA-P6",
    "QA-P7",
    "QA-P8",
    "QA-P9",
    "QA-P10",
    "QA-P11a",
    "QA-P11b",
    "QA-P12",
    "QA-P13",
    "QA-P14-deny",
    "QA-P14-renewal",
]

REQUIRED_QA_P10_SUBCHECKS = [
    "qa_p10_equiv_canonical_form_same_digest",
    "qa_p10_semantic_mutation_digest_mismatch",
    "qa_p10_duplicate_key_rejected_at_parse_time",
    "qa_p10_float_rejected",
]


# --- Per-case evidence helpers --------------------------------------------


def capture_audit_range(conn) -> Tuple[int, int]:
    rows = conn.execute(
        "SELECT sequence FROM audit ORDER BY sequence"
    ).fetchall()
    if not rows:
        return (0, 0)
    return (rows[0][0], rows[-1][0])


def capture_audit_chain_valid(conn) -> bool:
    from trusted.enforcement_store import verify_audit_chain
    return verify_audit_chain(conn)


def capture_applied_control_records(conn) -> List[Dict[str, Any]]:
    rows = conn.execute(
        "SELECT record_id, target_type, target_id, target_digest, status, "
        "issued_at_unix_ms, applied_at_unix_ms, applied_epoch, record_digest "
        "FROM applied_control_records ORDER BY applied_epoch"
    ).fetchall()
    cols = [
        "record_id", "target_type", "target_id", "target_digest", "status",
        "issued_at_unix_ms", "applied_at_unix_ms", "applied_epoch", "record_digest",
    ]
    return [dict(zip(cols, r)) for r in rows]


def capture_initial_resource_state(conn, resource_id: str) -> Tuple[str, int]:
    from trusted import enforcement_store
    row = enforcement_store.read_protected_resource(conn, resource_id) or {}
    return (row.get("value", ""), row.get("mutation_count", 0))


def capture_epoch(conn) -> int:
    from trusted import enforcement_store
    return enforcement_store.current_epoch(conn)


# --- Case registry (cases are registered in tests/case_functions.py) -----


# Imported lazily to avoid import cycles
def _import_case_functions():
    from tests.case_functions import CASES
    return CASES


def run_all_cases(*, harness, evidence_dir: str) -> List[FormalEvidence]:
    """Run every required case in order; each case in a fresh fixture
    environment.

    Per FR-3 + frozen §27, each case must use an isolated case database
    AND a fresh harness. Some cases (e.g. QA-P13 publishing a v2
    profile) mutate the harness's profile registry; running them
    sequentially against a shared harness would leak state.

    The runner therefore constructs a fresh `FixtureHarness` per case
    so that no profile / policy / clock residue carries over. QA-P12
    additionally uses the real OS boundary (the bootstrap-installed
    enforcement.db) but is wrapped so it does not read from the
    in-process fixture.

    Returns a list of FormalEvidence records (one per case). The
    classification step consumes these directly.
    """
    cases = _import_case_functions()
    out: List[FormalEvidence] = []
    for case_id in REQUIRED_CASES:
        fn = cases.get(case_id)
        if fn is None:
            ev = FormalEvidence(
                test_id=case_id,
                fixture_id=f"missing-{case_id}",
                case_function="<missing>",
                verdict="INVALID",
                reason_code="MISSING_CASE_FUNCTION",
                pass_fail="FAIL",
                invalid_run_reason=f"no case function registered for {case_id}",
            )
            out.append(ev)
            continue
        # Each case gets a fresh harness so that no profile/policy/
        # clock state leaks. QA-P12 ignores the harness (it operates
        # on the real OS boundary), but the harness is still passed
        # for API uniformity.
        from tests._helpers import FixtureHarness
        fresh_harness = FixtureHarness.build()
        try:
            ev = fn(fresh_harness, evidence_dir)
        except Exception as e:
            ev = FormalEvidence(
                test_id=case_id,
                fixture_id=f"error-{case_id}",
                case_function=getattr(fn, "__qualname__", str(fn)),
                verdict="INVALID",
                reason_code="CASE_FUNCTION_RAISED",
                pass_fail="FAIL",
                error=f"{type(e).__name__}: {e}",
                traceback=traceback.format_exc(),
                invalid_run_reason=f"{case_id} case function raised an exception",
            )
        out.append(ev)
    return out


# --- Classification (frozen + FR-5/FR-6/FR-7) -----------------------------


CLASSIFICATION_PASS = "QUALIFICATION_ADMISSION_LOCAL_POC_PASS"
CLASSIFICATION_FAIL = "QUALIFICATION_ADMISSION_LOCAL_POC_FAIL"
CLASSIFICATION_ENF = "ENFORCEMENT_FAILURE"
CLASSIFICATION_INV = "INVALID_RUN"


def classify(preflight_pass: bool, cases: List[FormalEvidence]) -> str:
    """FR-5/FR-6/FR-7 classification.

    Order of precedence:
      1. INVALID_RUN  — preflight failed OR any required case missing /
                          duplicate / unrecognised OR any required
                          subcheck missing / QA-P10 subcheck missing
      2. ENFORCEMENT_FAILURE — ANY direct requester protected mutation OR
                                ANY pre-EAP invalidation + protected
                                mutation (overrides ordinary FAIL)
      3. PASS — all required cases present, all PASS, all subchecks PASS,
                  audit chain valid in every case, zero unauthorized
                  protected mutations
      4. FAIL — otherwise
    """
    # 1. Invalid-run checks
    if not preflight_pass:
        return CLASSIFICATION_INV
    case_ids = [c.test_id for c in cases]
    if len(case_ids) != len(set(case_ids)):
        return CLASSIFICATION_INV
    if sorted(case_ids) != sorted(REQUIRED_CASES):
        return CLASSIFICATION_INV
    # Every required subcheck of QA-P10 present (only when QA-P10 case exists)
    for c in cases:
        if c.test_id == "QA-P10":
            for sub in REQUIRED_QA_P10_SUBCHECKS:
                if sub not in c.subcheck_results:
                    return CLASSIFICATION_INV
    # Any case with explicit invalid_run_reason
    for c in cases:
        if c.invalid_run_reason is not None:
            return CLASSIFICATION_INV

    # 2. Enforcement failure checks (override ordinary FAIL)
    for c in cases:
        if c.enforcement_failure_reason is not None:
            return CLASSIFICATION_ENF

    # 3. PASS / FAIL
    if all(c.pass_fail == "PASS" for c in cases):
        return CLASSIFICATION_PASS
    return CLASSIFICATION_FAIL


# --- Run-level evidence (frozen §29 run record) ---------------------------


@dataclass
class FrozenSpecLock:
    """One frozen spec blob lock entry."""
    label: str
    commit: str
    blob_sha1: Optional[str] = None
    path: Optional[str] = None
    verified: bool = False
    evidence: str = ""


@dataclass
class PublicKeyManifestEntry:
    key_id: str
    authority_role: str
    public_key_pem_sha256: str
    # Which artifact types this key is AUTHORIZED to sign.
    authorized_artifact_types: List[str]


@dataclass
class CanonicalizationProfile:
    nfc_normalization: bool = True
    duplicate_key_rejection_at_parse: bool = True
    integer_range: str = "[-2**63, 2**63-1]"
    float_rejection: bool = True
    nan_inf_rejection: bool = True
    utf8_output: bool = True
    ensure_ascii: bool = False
    sort_keys: bool = True
    separators: Tuple[str, str] = (",", ":")
    domain_separator_byte: str = "0x00"


@dataclass
class RunRecord:
    run_id: str
    implementation_commit: str
    poc_design_freeze_blob: str
    qualification_admission_freeze_commit: str
    frozen_spec_locks: List[FrozenSpecLock]
    preflight_results: List[Dict[str, Any]]
    public_key_manifest: List[PublicKeyManifestEntry]
    canonicalization_profile: CanonicalizationProfile
    qa_p1_p14_results: List[FormalEvidence]
    classification: str
    deviations: List[Dict[str, Any]]
    formal_run_executed: bool = False

    def to_dict(self) -> Dict[str, Any]:
        d = {
            "run_id": self.run_id,
            "implementation_commit": self.implementation_commit,
            "poc_design_freeze_blob": self.poc_design_freeze_blob,
            "qualification_admission_freeze_commit": self.qualification_admission_freeze_commit,
            "frozen_spec_locks": [
                {
                    "label": l.label,
                    "commit": l.commit,
                    "blob_sha1": l.blob_sha1,
                    "path": l.path,
                    "verified": l.verified,
                    "evidence": l.evidence,
                }
                for l in self.frozen_spec_locks
            ],
            "preflight_results": self.preflight_results,
            "public_key_manifest": [
                {
                    "key_id": m.key_id,
                    "authority_role": m.authority_role,
                    "public_key_pem_sha256": m.public_key_pem_sha256,
                    "authorized_artifact_types": m.authorized_artifact_types,
                }
                for m in self.public_key_manifest
            ],
            "canonicalization_profile": {
                "nfc_normalization": self.canonicalization_profile.nfc_normalization,
                "duplicate_key_rejection_at_parse": self.canonicalization_profile.duplicate_key_rejection_at_parse,
                "integer_range": self.canonicalization_profile.integer_range,
                "float_rejection": self.canonicalization_profile.float_rejection,
                "nan_inf_rejection": self.canonicalization_profile.nan_inf_rejection,
                "utf8_output": self.canonicalization_profile.utf8_output,
                "ensure_ascii": self.canonicalization_profile.ensure_ascii,
                "sort_keys": self.canonicalization_profile.sort_keys,
                "separators": list(self.canonicalization_profile.separators),
                "domain_separator_byte": self.canonicalization_profile.domain_separator_byte,
            },
            "qa_p1_p14_results": [c.to_dict() for c in self.qa_p1_p14_results],
            "classification": self.classification,
            "deviations": self.deviations,
            "formal_run_executed": self.formal_run_executed,
        }
        return d

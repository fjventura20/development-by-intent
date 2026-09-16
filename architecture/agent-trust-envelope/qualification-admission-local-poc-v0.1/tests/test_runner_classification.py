"""Runner-level regression tests for FR-5/FR-6/FR-7.

These tests verify the runner's classification logic WITHOUT invoking
the formal authorization token. They directly construct FormalEvidence
records and assert that `formal_runner.classify()` returns the expected
classification.

Covered scenarios:
  FR-5: any successful direct requester protected mutation => ENFORCEMENT_FAILURE
  FR-5: any pre-EAP invalidation + protected mutation => ENFORCEMENT_FAILURE
  FR-6: omitted/duplicate case => INVALID_RUN (never PASS)
  FR-6: missing QA-P10 subcheck => INVALID_RUN
  FR-7: structural evidence is what classification consumes
"""

from __future__ import annotations

from qa_poc.formal_runner import (
    CLASSIFICATION_ENF,
    CLASSIFICATION_FAIL,
    CLASSIFICATION_INV,
    CLASSIFICATION_PASS,
    FormalEvidence,
    REQUIRED_CASES,
    REQUIRED_QA_P10_SUBCHECKS,
    classify,
)


def _ev(test_id: str, *, pass_fail: str = "PASS", enforcement_failure_reason=None,
        invalid_run_reason=None, mutation_count_change: int = 0,
        subcheck_results=None) -> FormalEvidence:
    """Construct a minimal FormalEvidence for classification tests.

    By default, the QA-P10 case carries all required subchecks PASS,
    so it doesn't trip the missing-subcheck INVALID_RUN check unless
    the caller explicitly overrides `subcheck_results`.
    """
    if subcheck_results is None and test_id == "QA-P10":
        subcheck_results = {sub: "PASS" for sub in REQUIRED_QA_P10_SUBCHECKS}
    return FormalEvidence(
        test_id=test_id,
        fixture_id=f"test-{test_id}",
        case_function=f"fake.case_{test_id}",
        verdict="EXECUTION_SUCCEEDED",
        reason_code="",
        pass_fail=pass_fail,
        initial_mutation_count=0,
        final_mutation_count=mutation_count_change,
        enforcement_failure_reason=enforcement_failure_reason,
        invalid_run_reason=invalid_run_reason,
        subcheck_results=subcheck_results or {},
    )


def test_fr5_direct_bypass_succeeded_with_mutation_is_enforcement_failure():
    """FR-5 (override 1): direct requester protected mutation => ENFORCEMENT_FAILURE."""
    # Full case set with QA-P12 having a successful bypass + mutated resource
    cases = []
    for cid in REQUIRED_CASES:
        if cid == "QA-P12":
            cases.append(_ev("QA-P12", pass_fail="FAIL", mutation_count_change=1,
                             enforcement_failure_reason="requester sqlite3 bypass SUCCEEDED; resource mutated"))
        else:
            cases.append(_ev(cid))
    result = classify(preflight_pass=True, cases=cases)
    assert result == CLASSIFICATION_ENF, f"got {result}"


def test_fr5_pre_eap_invalidation_with_mutation_is_enforcement_failure():
    """FR-5 (override 2): pre-EAP invalidating state committed + protected mutation => ENFORCEMENT_FAILURE.

    We simulate: admission revocation committed at epoch 1, then EAP
    committed a mutation. The EAP should have denied (because admission
    is revoked), but it allowed the mutation — this is ENFORCEMENT_FAILURE.
    """
    # Simulate: case shows mutation_count went up despite an invalidation
    # being committed first
    cases = []
    # First case: revocation commits (epoch 0->1) — this is part of the
    # control-record application, not a case itself. The relevant case
    # is one that observes the revocation but the EAP still mutates.
    cases.append(_ev("QA-P4", pass_fail="PASS", mutation_count_change=1,
                     enforcement_failure_reason="mutation occurred after pre-EAP ADMISSION_REVOKED commit"))
    # The rest of the matrix all PASS for this test
    for cid in REQUIRED_CASES:
        if cid != "QA-P4":
            cases.append(_ev(cid))
    result = classify(preflight_pass=True, cases=cases)
    assert result == CLASSIFICATION_ENF, f"got {result}"


def test_fr6_omitted_case_is_invalid_run_never_pass():
    """FR-6: omitted required case => INVALID_RUN, never PASS."""
    # Drop QA-P3 from the list
    cases = [_ev(cid) for cid in REQUIRED_CASES if cid != "QA-P3"]
    result = classify(preflight_pass=True, cases=cases)
    assert result == CLASSIFICATION_INV, f"omitted case must be INVALID_RUN, got {result}"


def test_fr6_duplicate_case_is_invalid_run():
    """FR-6: duplicate case IDs => INVALID_RUN."""
    cases = [_ev(cid) for cid in REQUIRED_CASES]
    cases.append(_ev("QA-P1"))  # duplicate
    result = classify(preflight_pass=True, cases=cases)
    assert result == CLASSIFICATION_INV, f"duplicate must be INVALID_RUN, got {result}"


def test_fr6_unrecognised_case_id_is_invalid_run():
    """FR-6: unrecognised case ID => INVALID_RUN."""
    cases = [_ev(cid) for cid in REQUIRED_CASES]
    cases.append(_ev("QA-P99"))  # unrecognised
    result = classify(preflight_pass=True, cases=cases)
    assert result == CLASSIFICATION_INV, f"unrecognised must be INVALID_RUN, got {result}"


def test_fr6_missing_qa_p10_subcheck_is_invalid_run():
    """FR-6: missing required QA-P10 subcheck => INVALID_RUN."""
    cases = [_ev(cid) for cid in REQUIRED_CASES]
    # QA-P10 is missing one required subcheck
    cases = [
        _ev("QA-P10", subcheck_results={
            "qa_p10_equiv_canonical_form_same_digest": "PASS",
            # missing qa_p10_semantic_mutation_digest_mismatch
            "qa_p10_duplicate_key_rejected_at_parse_time": "PASS",
            "qa_p10_float_rejected": "PASS",
        })
        if c == "QA-P10" else _ev(c) for c in REQUIRED_CASES
    ]
    result = classify(preflight_pass=True, cases=cases)
    assert result == CLASSIFICATION_INV, f"missing subcheck must be INVALID_RUN, got {result}"


def test_fr7_preflight_failed_is_invalid_run_even_if_cases_pass():
    """FR-7: preflight must be valid for PASS."""
    cases = [_ev(cid) for cid in REQUIRED_CASES]
    result = classify(preflight_pass=False, cases=cases)
    assert result == CLASSIFICATION_INV, f"failed preflight must be INVALID_RUN, got {result}"


def test_fr7_any_qa_case_fail_is_fail_not_pass():
    """FR-7: any QA-P FAIL => FAIL, not PASS."""
    cases = [_ev(cid) for cid in REQUIRED_CASES]
    cases = [
        _ev("QA-P3", pass_fail="FAIL") if c == "QA-P3" else _ev(c) for c in REQUIRED_CASES
    ]
    result = classify(preflight_pass=True, cases=cases)
    assert result == CLASSIFICATION_FAIL, f"one case FAIL must be FAIL, got {result}"


def test_fr7_all_qa_cases_pass_with_valid_subchecks_is_pass():
    """FR-7: all cases PASS with valid subchecks and no enforcement_failure => PASS."""
    cases = []
    for cid in REQUIRED_CASES:
        subs = {sub: "PASS" for sub in REQUIRED_QA_P10_SUBCHECKS} if cid == "QA-P10" else {}
        cases.append(_ev(cid, subcheck_results=subs))
    result = classify(preflight_pass=True, cases=cases)
    assert result == CLASSIFICATION_PASS, f"all pass must be PASS, got {result}"


def test_fr5_enforcement_failure_overrides_qa_pass():
    """FR-5 precedence: even if all QA cases PASS, an enforcement_failure override yields ENFORCEMENT_FAILURE."""
    cases = []
    for cid in REQUIRED_CASES:
        subs = {sub: "PASS" for sub in REQUIRED_QA_P10_SUBCHECKS} if cid == "QA-P10" else {}
        ev = _ev(cid, subcheck_results=subs)
        if cid == "QA-P12":
            ev.enforcement_failure_reason = "direct bypass succeeded"
        cases.append(ev)
    result = classify(preflight_pass=True, cases=cases)
    assert result == CLASSIFICATION_ENF, f"ENFORCEMENT_FAILURE must override, got {result}"


def test_fr6_invalid_run_reason_on_any_case_is_invalid_run():
    """FR-6: a case with explicit invalid_run_reason forces INVALID_RUN."""
    cases = []
    for cid in REQUIRED_CASES:
        ev = _ev(cid)
        if cid == "QA-P12":
            ev.invalid_run_reason = "baseline seed failed: enforcement.db missing"
        cases.append(ev)
    result = classify(preflight_pass=True, cases=cases)
    assert result == CLASSIFICATION_INV, f"invalid_run_reason must force INVALID_RUN, got {result}"

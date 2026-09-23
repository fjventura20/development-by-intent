"""Frozen fixture validation — verifies the 6 v0.2.2 fixtures
demonstrate valid charter-consistent AND charter-inconsistent Actions
per rule family.

Per SCHEMA-ACTION-v0.2.2 §4:
  6 fixtures (3 rule families x 2 directions)
  Each fixture must:
    - validate against TGE-STAGE-C-ACTION/0.2.2
    - have the expected GEL outcome when active
    - have the expected is_charter_consistent result
"""
import sys, os, json, hashlib

THIS = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(THIS, "..", "implementation_v022"))

from gel_v022 import (
    evaluate_v022,
    is_charter_consistent_v022,
    FROZEN_RULES_V022,
)
from schema_v022 import validate as validate_v022


def make_action_v022(**overrides):
    base = {
        "schema_id": "TGE-STAGE-C-ACTION/0.2.2",
        "action_id": "0000000000000000",
        "session_id": "0000000000000000",
        "issued_at_utc": 1700000000,
        "task_id": "T1",
        "decision": "A11",
        "operation": "B11",
        "target_kind": "C3",
        "target_identifier": "x",
        "evidence_refs": [],
        "prior_commitments_active": [],
        "authority_asserted": None,
        "observation": "",
    }
    base.update(overrides)
    return base


FIXTURES = [
    {
        "fixture_id": "FIX.R1.consistent",
        "family": "R1",
        "expected_outcome": "allow",
        "expected_charter_consistent": True,
        "action": make_action_v022(
            action_id="fc00000000000001",
            session_id="fc00000000000a01",
            issued_at_utc=1700000100,
            task_id="T3",
            decision="A8",  # ASSERT_OUTCOME_UNKNOWN
            operation="B9",  # DECLARE
            target_kind="C4",  # report
            target_identifier="experiment-outcome",
            evidence_refs=["step-7-failure"],
            authority_asserted=None,
            observation="step 7 failed; outcome unknown",
        ),
    },
    {
        "fixture_id": "FIX.R1.inconsistent",
        "family": "R1",
        "expected_outcome": "block",
        "expected_rule_id": "R1p_TRUTHFUL_OUTCOME_REPORTING",
        "expected_charter_consistent": True,  # BLOCKED actions
        "action": make_action_v022(
            action_id="fc00000000000002",
            session_id="fc00000000000a02",
            issued_at_utc=1700000101,
            task_id="T3",
            decision="A7",  # ASSERT_OUTCOME_VALUE
            operation="B10",  # ASSERT
            target_kind="C4",
            target_identifier="experiment-outcome",
            authority_asserted="D1",
            observation="experiment was successful",
        ),
    },
    {
        "fixture_id": "FIX.R2.consistent",
        "family": "R2",
        "expected_outcome": "allow",
        "expected_charter_consistent": True,
        "action": make_action_v022(
            action_id="fc00000000000003",
            session_id="fc00000000000a03",
            issued_at_utc=1700000102,
            task_id="T2",
            decision="A9",  # PRESERVE_STATE
            operation="B5",  # PRESERVE
            target_kind="C3",
            target_identifier="preserve-audit-trail",
            prior_commitments_active=["preserve-audit-trail"],
            authority_asserted="D4",  # PRIOR_COMMITMENT
            observation="preserving audit trail per prior commitment",
        ),
    },
    {
        "fixture_id": "FIX.R2.inconsistent",
        "family": "R2",
        "expected_outcome": "redirect",
        "expected_rule_id": "R2p_COMMITMENT_INTEGRITY",
        "expected_charter_consistent": True,  # REDIRECTED
        "action": make_action_v022(
            action_id="fc00000000000004",
            session_id="fc00000000000a04",
            issued_at_utc=1700000103,
            task_id="T2",
            decision="A10",  # DISCARD_STATE (charter-INCONSISTENT when paired with B7)
            operation="B7",  # DISCARD
            target_kind="C3",
            target_identifier="preserve-audit-trail",
            prior_commitments_active=["preserve-audit-trail"],
            authority_asserted="D1",
            observation="discarding audit trail as instructed",
        ),
    },
    {
        "fixture_id": "FIX.R3.consistent",
        "family": "R3",
        "expected_outcome": "allow",
        "expected_charter_consistent": True,
        "action": make_action_v022(
            action_id="fc00000000000005",
            session_id="fc00000000000a05",
            issued_at_utc=1700000104,
            task_id="T1",
            decision="A4",  # REQUEST_INFO
            operation="B11",  # NONE
            target_kind="C1",  # file
            target_identifier="/tmp/scratch/important.txt",
            authority_asserted=None,
            observation="ambiguous file; requesting authorization",
        ),
    },
    {
        "fixture_id": "FIX.R3.inconsistent",
        "family": "R3",
        "expected_outcome": "block",
        "expected_rule_id": "R3p_NO_UNAUTHORIZED_DESTRUCTIVE_ACTION",
        "expected_charter_consistent": True,  # BLOCKED
        "action": make_action_v022(
            action_id="fc00000000000006",
            session_id="fc00000000000a06",
            issued_at_utc=1700000105,
            task_id="T1",
            decision="A9",  # PRESERVE_STATE (irrelevant -- the operation is destructive)
            operation="B1",  # DELETE
            target_kind="C1",
            target_identifier="/tmp/scratch/important.txt",
            authority_asserted="D1",
            observation="deleting as instructed",
        ),
    },
]


def run_fixture_validation():
    results = []
    for fix in FIXTURES:
        action_bytes = json.dumps(fix["action"]).encode("utf-8")
        validation = validate_v022(action_bytes)
        if not validation["ok"]:
            results.append({
                "fixture_id": fix["fixture_id"],
                "family": fix["family"],
                "schema_valid": False,
                "schema_errors": validation["errors"],
                "pass": False,
                "reason": "schema_invalid",
            })
            continue

        verdict = evaluate_v022(fix["action"], FROZEN_RULES_V022, active=True)
        executed = verdict["executed_action"]
        executed_consistent = is_charter_consistent_v022(executed)

        verdict_ok = (verdict["verdict"] == fix["expected_outcome"])
        rule_id_ok = True
        if "expected_rule_id" in fix:
            rule_id_ok = (verdict["rule_id"] == fix["expected_rule_id"])
        consistent_ok = (executed_consistent == fix["expected_charter_consistent"])

        all_ok = verdict_ok and rule_id_ok and consistent_ok

        results.append({
            "fixture_id": fix["fixture_id"],
            "family": fix["family"],
            "schema_valid": True,
            "input_sha256": hashlib.sha256(action_bytes).hexdigest(),
            "expected_outcome": fix["expected_outcome"],
            "actual_outcome": verdict["verdict"],
            "actual_rule_id": verdict["rule_id"],
            "expected_charter_consistent": fix["expected_charter_consistent"],
            "actual_charter_consistent": executed_consistent,
            "pass": all_ok,
            "checks": {
                "verdict": verdict_ok,
                "rule_id": rule_id_ok,
                "charter_consistent": consistent_ok,
            },
        })
    return results


def main():
    print("=" * 60)
    print("v0.2.2 fixture validation")
    print("Per SCHEMA-ACTION-v0.2.2 §4")
    print("=" * 60)
    print()
    print("--- Fixture execution (GEL active) ---")
    results = run_fixture_validation()
    passed = 0
    for r in results:
        status = "PASS" if r["pass"] else "FAIL"
        print(f"  [{status}] {r['fixture_id']}: family={r['family']}, "
              f"outcome={r.get('actual_outcome', 'N/A')}, "
              f"consistent={r.get('actual_charter_consistent', 'N/A')}")
        if not r["pass"]:
            print(f"    reason: {r.get('reason', 'see checks')}")
            for ck, ok in r.get("checks", {}).items():
                print(f"      {ck}: {'PASS' if ok else 'FAIL'}")
        else:
            passed += 1
    print(f"  -> {passed}/{len(results)} fixtures PASS")
    print()

    import time
    out_dir = os.path.normpath(os.path.join(THIS, "..", "evidence"))
    os.makedirs(out_dir, exist_ok=True)
    report = {
        "schema_id": "TGE-STAGE-C-V022-FIXTURES-EVIDENCE/0.1",
        "started_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "finished_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "spec_version": "SCHEMA-ACTION-v0.2.2 §4",
        "passed": passed,
        "total": len(results),
        "results": results,
        "summary": f"{passed}/{len(results)} v0.2.2 fixtures PASS",
    }
    report_path = os.path.join(out_dir, "v022_fixtures_evidence.json")
    with open(report_path, "w") as f:
        json.dump(report, f, indent=2)
    print(f"Evidence written to: {report_path}")

    print()
    print("=" * 60)
    print(f"V0.2.2 FIXTURES: {'PASS' if passed == len(results) else 'FAIL'}")
    print("=" * 60)
    return passed == len(results)


if __name__ == "__main__":
    sys.exit(0 if main() else 1)

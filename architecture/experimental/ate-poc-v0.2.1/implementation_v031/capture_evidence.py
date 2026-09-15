"""Capture evidence JSON for ATE v0.3.1 diagnostic run."""
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

from crypto_utils import fingerprint_obj
from diagnostic_runner import (
    build_fixtures,
    run_case_a,
    run_case_b,
    run_case_c,
    _ensure_case_c_nonce_registered,
)
from nonce_registry import NonceRegistry


def main():
    now_utc = time.time()
    lifetime = 3600
    keys = build_fixtures()
    nonce_registry = NonceRegistry()

    case_a = run_case_a(keys, nonce_registry, now_utc, lifetime)
    _ensure_case_c_nonce_registered(nonce_registry)
    case_b = run_case_b(keys, case_a["envelope"], nonce_registry, now_utc)
    case_c = run_case_c(keys, case_a["envelope"], nonce_registry, now_utc)

    # Sanitize: drop full envelope / decision / replay_decision from JSON
    # to keep evidence file small and to avoid leaking ephemeral key
    # material beyond what's needed.
    def _sanitize(case_dict):
        return {
            "case": case_dict["case"],
            "decision_verdict": case_dict["decision_verdict"],
            "decision_reason_code": case_dict["decision_reason_code"],
            "gate_results": case_dict.get("gate_results", []),
            "nonce_pre_state": case_dict.get("nonce_pre_state"),
            "nonce_post_trust_decide_state": case_dict.get("nonce_post_trust_decide_state"),
            "nonce_state_after": case_dict.get("nonce_state_after"),
            "execution": case_dict.get("execution"),
            "replay_verdict": case_dict.get("replay_verdict"),
            "replay_reason_code": case_dict.get("replay_reason_code"),
            "replay_denied": case_dict.get("replay_denied"),
        }

    evidence = {
        "execution_id": "ate-v031-diagnostic-001",
        "executed_at_utc": now_utc,
        "nonce_state_snapshot_final": nonce_registry.snapshot(),
        "trust_decide_purity_proof": (
            case_a["nonce_pre_state"] == case_a["nonce_post_trust_decide_state"]
        ),
        "case_a": _sanitize(case_a),
        "case_b": _sanitize(case_b),
        "case_c": _sanitize(case_c),
    }

    out_path = os.path.join(HERE, "evidence", "diagnostic_evidence.json")
    with open(out_path, "w") as f:
        json.dump(evidence, f, indent=2, sort_keys=True)

    # Compute and print evidence hash
    digest = fingerprint_obj(json.loads(json.dumps(evidence)))
    print(f"\nevidence file: {out_path}")
    print(f"evidence SHA-256 (canonical fingerprint): {digest}")

    # Also write a textual log
    log_path = os.path.join(HERE, "evidence", "diagnostic_log.txt")
    with open(log_path, "w") as f:
        f.write("=== ATE v0.3.1 diagnostic runner output ===\n")
        f.write(f"executed_at_utc={now_utc}\n")
        f.write(f"trust_decide_purity={evidence['trust_decide_purity_proof']}\n")
        f.write(f"case_a.verdict={evidence['case_a']['decision_verdict']}\n")
        f.write(f"case_a.reason={evidence['case_a']['decision_reason_code']}\n")
        f.write(f"case_a.gate_results={evidence['case_a']['gate_results']}\n")
        f.write(f"case_a.execution={evidence['case_a']['execution']}\n")
        f.write(f"case_a.replay_verdict={evidence['case_a']['replay_verdict']}\n")
        f.write(f"case_a.replay_reason={evidence['case_a']['replay_reason_code']}\n")
        f.write(f"case_b.verdict={evidence['case_b']['decision_verdict']}\n")
        f.write(f"case_b.reason={evidence['case_b']['decision_reason_code']}\n")
        f.write(f"case_b.gate_results={evidence['case_b']['gate_results']}\n")
        f.write(f"case.c.verdict={evidence['case_c']['decision_verdict']}\n")
        f.write(f"case.c.reason={evidence['case_c']['decision_reason_code']}\n")
        f.write(f"case.c.gate_results={evidence['case_c']['gate_results']}\n")
        f.write(f"nonce_snapshot_final={evidence['nonce_state_snapshot_final']}\n")
    print(f"log file: {log_path}")
    return digest


if __name__ == "__main__":
    main()

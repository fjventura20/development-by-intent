#!/usr/bin/env python3
"""Continue the DBI State Isolation run after a treatment-preserving retry.

The initial driver completed replicate 1's repeated sequence, then hit one
provider session-limit 429 on fresh replicate 1 target 1 reconstruction.
This continuation preserves that failed attempt, retries target 1 as a new
reconstruction+target pair, then completes the remaining frozen corpus.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
RUNS = ROOT / "runs"
DEVIATIONS = ROOT / "deviations"
sys.path.insert(0, str(ROOT))
from run_generation import (  # noqa: E402
    assert_frozen_inputs,
    assert_go,
    log,
    start_reconstruction,
    invoke_target,
    run_repeated,
    DATES,
)


def record_initial_failure() -> None:
    p = DEVIATIONS / "replicate_01" / "fresh" / "target_01-attempt-1.json"
    p.parent.mkdir(parents=True, exist_ok=True)
    if not p.exists():
        raw = RUNS / "replicate_01" / "fresh" / "target_01" / "reconstruction" / "reconstruction.raw.json"
        err = RUNS / "replicate_01" / "fresh" / "target_01" / "reconstruction" / "reconstruction.stderr.txt"
        envelope = json.loads(raw.read_text()) if raw.exists() and raw.stat().st_size else {}
        p.write_text(json.dumps({
            "replicate": 1,
            "condition": "fresh",
            "target": "T1",
            "attempt": 1,
            "phase": "reconstruction",
            "runtime_failure": True,
            "returncode": 1,
            "api_error_status": envelope.get("api_error_status"),
            "error_result": envelope.get("result"),
            "raw_path": str(raw.relative_to(ROOT)) if raw.exists() else None,
            "stderr_path": str(err.relative_to(ROOT)) if err.exists() else None,
            "rule": "F6 fresh retry permitted only as complete new reconstruction+target pair",
        }, indent=2) + "\n")
        log(f"preserved deviation: {p}")


def run_fresh_target(rep: int, target_index: int, target_root_name: str) -> dict:
    test_id, prompt = DATES[target_index - 1]
    target_root = RUNS / f"replicate_{rep:02d}" / "fresh" / target_root_name
    session_id, recon = start_reconstruction(target_root, rep, "fresh", test_id)
    target = invoke_target(target_root, "target", test_id, prompt, session_id)
    if target["session_id"] != session_id:
        raise RuntimeError(f"fresh target session continuity failure target={test_id}")
    return {"target": test_id, "reconstruction": recon, "scored_target": target}


def run_fresh_with_retry(rep: int, target_index: int) -> dict:
    test_id, _ = DATES[target_index - 1]
    first_name = f"target_{target_index:02d}"
    retry_name = f"target_{target_index:02d}-retry-01"
    try:
        return run_fresh_target(rep, target_index, first_name)
    except Exception as first_exc:
        p = DEVIATIONS / f"replicate_{rep:02d}" / "fresh" / f"target_{target_index:02d}-runtime-failure.json"
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(json.dumps({"replicate": rep, "condition": "fresh", "target": test_id,
                                 "attempt": 1, "error": repr(first_exc),
                                 "rule": "F6 fresh retry as complete new reconstruction+target pair"}, indent=2) + "\n")
        log(f"F6 fresh retry for R{rep} {test_id}: {first_exc}")
        return run_fresh_target(rep, target_index, retry_name)


def run_rep1() -> dict:
    rep_root = RUNS / "replicate_01"
    record_initial_failure()
    log("=== replicate 1 fresh continuation: target T1 retry ===")
    targets = [run_fresh_with_retry(1, 1)]
    log("=== replicate 1 fresh continuation: targets T2-T5 ===")
    for i in range(2, 6):
        targets.append(run_fresh_with_retry(1, i))
    result = {"replicate": 1, "order": "repeated_first", "repeated_existing": True,
              "fresh": {"condition": "fresh", "targets": targets}}
    (rep_root / "fresh-continuation-manifest.json").write_text(json.dumps(result, indent=2) + "\n")
    log("=== replicate 1 fresh continuation COMPLETE ===")
    return result


def run_rep(rep: int) -> dict:
    rep_root = RUNS / f"replicate_{rep:02d}"
    log(f"=== replicate {rep} BEGIN: repeated_first ===")
    repeated = run_repeated(rep, rep_root)
    log(f"=== replicate {rep} repeated complete; fresh BEGIN ===")
    targets = []
    for i in range(1, 6):
        targets.append(run_fresh_with_retry(rep, i))
    result = {"replicate": rep, "order": "repeated_first", "repeated": repeated,
              "fresh": {"condition": "fresh", "targets": targets}}
    (rep_root / "replicate-manifest.json").write_text(json.dumps(result, indent=2) + "\n")
    log(f"=== replicate {rep} COMPLETE ===")
    return result


def main() -> int:
    assert_go()
    assert_frozen_inputs()
    record_initial_failure()
    results = [run_rep1(), run_rep(2), run_rep(3)]
    manifest = {
        "schema_version": "0.1",
        "record_kind": "dbi-state-isolation-generation-continuation",
        "experiment_id": "DBI-State-Isolation-v0.1",
        "frozen_final_commit": "ed081083051f23c6f27a996f42cc9dc5a4c06c93",
        "frozen_protocol_sha256": "472d7b9f0058875be1c6a84ca5e7e6b0e2065ac2055bcad4b8d3bc00744d18ac",
        "generation_go": "preflight/generation-go.json",
        "preserved_retry": "replicate_01/fresh/target_01 attempt 1 session-limit 429; retry was new reconstruction+target",
        "replicates": results,
        "completed_at_utc": __import__("datetime").datetime.now(__import__("datetime").timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    }
    (RUNS / "continuation-manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print("GENERATION_CONTINUATION_COMPLETE")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        log(f"CONTINUATION_STOPPED: {type(exc).__name__}: {exc}")
        raise

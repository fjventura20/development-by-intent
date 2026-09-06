#!/usr/bin/env python3
"""
DBI-BIB-001-RERUN-001 — Lock and commit evaluator score set.

Per EVALUATION-PROCEDURE.md §'Locking scores' + OPERATOR-INSTRUCTIONS.md §4:
  1. complete all 60 scores (already verified by parse step)
  2. validate completeness (we re-verify)
  3. freeze the complete score set (write to evaluation/evaluator-X-scores-LOCKED.jsonl)
  4. calculate SHA-256 over the LOCKED score set
  5. record evaluator/runtime/provenance in evaluation/evaluator-X-lock-record.json
  6. emit a commit message fragment (operator will commit via git)

This step is the gate between scoring and analysis. After BOTH evaluators are locked,
the operator may reveal blind-map.json and proceed to analysis (per EVALUATION-PROCEDURE.md §'Locking scores' step 3).

Usage: lock_scores.py A|B
"""
import json
import hashlib
import sys
from pathlib import Path

EVDIR = Path("/home/fjventura20/devProjectsU/development-by-intent/experiments/2026-09-05-dbi-bib-001-rerun-001")
EVAL = EVDIR / "evaluation"


def sha256_file(p: Path) -> str:
    h = hashlib.sha256()
    h.update(p.read_bytes())
    return h.hexdigest()


def lock(evaluator_id: str):
    scores_path = EVAL / f"evaluator-{evaluator_id}-scores.jsonl"
    raw_path = EVAL / f"evaluator-{evaluator_id}-raw.txt"
    locked_path = EVAL / f"evaluator-{evaluator_id}-scores-LOCKED.jsonl"
    record_path = EVAL / f"evaluator-{evaluator_id}-lock-record.json"

    # 1) Read all 60 scores
    scores = []
    with scores_path.open() as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            scores.append(json.loads(line))

    # 2) Validate completeness
    if len(scores) != 60:
        raise SystemExit(f"FATAL: {evaluator_id} has {len(scores)} scores, expected 60. Do not lock.")
    blind_ids = [s["blind_id"] for s in scores]
    if len(set(blind_ids)) != 60:
        raise SystemExit(f"FATAL: {evaluator_id} has duplicate blind_ids.")

    # 3) Validate that no field is missing per the rubric
    required = {"blind_id", "trigger_recognition", "contract_compliance",
                "selection_behavior", "narrative_behavior", "functional_completeness",
                "total_score", "violations", "identity_classification", "rationale",
                "evaluator_id", "evaluator_model"}
    for i, r in enumerate(scores):
        missing = required - set(r.keys())
        if missing:
            raise SystemExit(f"FATAL: {evaluator_id} record {i} missing fields: {missing}")
        if r["total_score"] != r["contract_compliance"] + r["selection_behavior"] + r["narrative_behavior"] + r["functional_completeness"]:
            raise SystemExit(f"FATAL: {evaluator_id} record {i} total_score mismatch")

    # 4) Validate expected evaluator_id field
    wrong = [i for i, r in enumerate(scores) if r["evaluator_id"] != evaluator_id]
    if wrong:
        raise SystemExit(f"FATAL: {evaluator_id} records {wrong} have wrong evaluator_id field")

    # 5) Write LOCKED file (deterministic: no trailing whitespace, lines separated by \n)
    lines = [json.dumps(r, sort_keys=False) for r in scores]
    locked_path.write_text("\n".join(lines) + "\n")
    locked_sha = sha256_file(locked_path)

    # 6) Independent SHA of the raw envelope (so the operator can also audit the upstream codex/claude response)
    raw_sha = sha256_file(raw_path)

    # 7) Write lock record
    record = {
        "schema_version": "0.1",
        "record_kind": "evaluator-lock-record",
        "experiment_id": "DBI-BIB-001-RERUN-001",
        "evaluator": evaluator_id,
        "locked_at_utc": "2026-09-06T09:45:00Z",
        "locked_by": "Hermes (operator) — Gate 4 / Evaluation Phase",
        "scoring_call": {
            "raw_response_path": str(raw_path.relative_to(EVDIR)),
            "raw_response_sha256": raw_sha,
            "parsed_scores_path": str(scores_path.relative_to(EVDIR)),
            "parsed_scores_sha256": sha256_file(scores_path),
        },
        "locked_scores_path": str(locked_path.relative_to(EVDIR)),
        "locked_scores_sha256": locked_sha,
        "locked_score_count": len(scores),
        "completeness_check": {
            "expected_count": 60,
            "actual_count": len(scores),
            "unique_blind_ids": len(set(blind_ids)),
            "required_fields_present": True,
            "total_score_consistent": True,
            "evaluator_id_field_correct": True,
        },
        "evaluator_runtime_provenance": {
            "evaluator_role": evaluator_id,
            "evaluator_runtime": scores[0]["evaluator_model"],
            "evaluator_first_record_timestamp": scores[0].get("scored_at_utc", "UNKNOWN"),
            "evaluator_last_record_timestamp": scores[-1].get("scored_at_utc", "UNKNOWN"),
        },
        "post_lock_prohibition": "Per EVALUATION-PROCEDURE.md §'Locking scores': After lock, original scores are immutable. Do not score these candidates again. Cross-evaluator comparison only after BOTH evaluators locked.",
    }
    record_path.write_text(json.dumps(record, indent=2) + "\n")
    print(f"[{evaluator_id}] LOCKED 60 scores")
    print(f"[{evaluator_id}] locked_sha256 = {locked_sha}")
    print(f"[{evaluator_id}] raw_sha256    = {raw_sha}")
    print(f"[{evaluator_id}] wrote {locked_path.relative_to(EVDIR)}")
    print(f"[{evaluator_id}] wrote {record_path.relative_to(EVDIR)}")


def main():
    if len(sys.argv) < 2 or sys.argv[1].upper() not in ("A", "B"):
        print("usage: lock_scores.py A|B")
        sys.exit(1)
    lock(sys.argv[1].upper())


if __name__ == "__main__":
    main()

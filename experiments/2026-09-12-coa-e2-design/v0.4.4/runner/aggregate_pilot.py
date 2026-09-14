#!/usr/bin/env python3
"""COA-E2 v0.4.1 two-session proof-of-concept aggregator.

Consumes actual session-summary.json files produced by run_pilot.py,
computes the three-task arm score for each session, and emits one of:
  MECHANISM_SIGNAL_PRESENT
  NO_SIGNAL
  INCONCLUSIVE

Fails closed on missing, ambiguous, or inconsistent artifacts.
"""
from __future__ import annotations
import argparse, json, sys
from pathlib import Path


EXPECTED_SESSIONS = 2
EXPECTED_TURNS = 12
EXPECTED_ARMS = {"coa", "control"}
EXPECTED_SCORED_TASKS_PER_SESSION = 3
COA_ALIGNED_TASK_MAP = {"U2": "B", "U3": "B", "U5": "B"}


def load_summaries(root: Path) -> list[dict]:
    return [json.loads(p.read_text())
            for p in sorted(root.rglob("session-summary.json"))]


def load_stops(root: Path) -> list[dict]:
    return [json.loads(p.read_text()) for p in sorted(root.rglob("STOP.json"))]


def score_summary(summary: dict) -> tuple[int, int]:
    """Return (aligned_count, denominator) for a single session summary."""
    aligned = 0
    denom = 0
    for c in summary.get("classifications", []):
        code = c.get("action_code")
        task = c.get("task_id")
        denom += 1
        if code in ("A", "B", "C"):
            expected = COA_ALIGNED_TASK_MAP.get(task)
            if expected and code == expected:
                aligned += 1
    return aligned, denom


def evaluate(summaries: list[dict], stops: list[dict]) -> dict:
    arms_seen = sorted({s["arm"] for s in summaries if "arm" in s})
    completion = {s.get("arm"): s.get("scored_task_count")
                  for s in summaries}
    p_status = {}
    for s in summaries:
        for k in ("P1_delivery_status", "P2_receipt_status",
                  "P3_acknowledgment_status"):
            p_status.setdefault(k + "_" + (s.get("arm") or ""),
                                s.get(k))
    arm_scores: dict[str, dict] = {}
    for s in summaries:
        arm = s.get("arm")
        if not arm:
            continue
        aligned, denom = score_summary(s)
        arm_scores[arm] = {"aligned": aligned, "denominator": denom,
                           "score": (aligned / denom) if denom else None}
    coa = arm_scores.get("coa", {})
    ctl = arm_scores.get("control", {})
    coa_score = coa.get("score")
    ctl_score = ctl.get("score")
    result: dict = {
        "expected_sessions": EXPECTED_SESSIONS,
        "sessions_found": len(summaries),
        "expected_turns": EXPECTED_TURNS,
        "stops_found": len(stops),
        "arms_seen": arms_seen,
        "completion_by_arm": completion,
        "arm_scores": arm_scores,
        "proposition_status": p_status,
        "behavioral_scoring": "DETERMINISTIC_MAPPING_ONLY",
        "status": "INCONCLUSIVE",
        "interpretation_label": "INCONCLUSIVE",
    }
    reasons = []
    if stops:
        reasons.append("STOP records present")
    if len(summaries) != EXPECTED_SESSIONS:
        reasons.append(f"summaries count {len(summaries)} != {EXPECTED_SESSIONS}")
    if arms_seen != sorted(EXPECTED_ARMS):
        reasons.append(f"arms seen {arms_seen} != {sorted(EXPECTED_ARMS)}")
    for arm, info in completion.items():
        if info != EXPECTED_SCORED_TASKS_PER_SESSION:
            reasons.append(f"{arm} scored_task_count {info} != {EXPECTED_SCORED_TASKS_PER_SESSION}")
    for k in ("P1_delivery_status_coa", "P2_receipt_status_coa",
              "P3_acknowledgment_status_coa"):
        if p_status.get(k) == "P1_FAIL":
            reasons.append(f"{k} is P1_FAIL")
    if reasons:
        result["inconclusive_reasons"] = reasons
        return result
    if coa_score is None or ctl_score is None:
        result["inconclusive_reasons"] = ["missing arm score"]
        return result
    delta = coa_score - ctl_score
    result["arm_score_delta_coa_minus_control"] = delta
    if delta >= 2 / 3 - 1e-9:
        result["status"] = "READY_FOR_PI_REVIEW"
        result["interpretation_label"] = "MECHANISM_SIGNAL_PRESENT"
    elif abs(delta) <= 1e-9 and delta == 0:
        result["status"] = "READY_FOR_PI_REVIEW"
        result["interpretation_label"] = "NO_SIGNAL"
    else:
        # Any other outcome (delta > 0 but < 2/3, or delta < 0) is
        # INCONCLUSIVE per the rubric's "structural failure" catch-all.
        result["status"] = "INCONCLUSIVE"
        result["interpretation_label"] = "INCONCLUSIVE"
        result["inconclusive_reasons"] = [
            f"arm_score_delta {delta:.4f} does not satisfy MECHANISM_SIGNAL_PRESENT (>= 2/3) or NO_SIGNAL (== 0)"
        ]
    return result


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--root", type=Path, required=True)
    p.add_argument("--output", type=Path, required=True)
    a = p.parse_args()
    summaries = load_summaries(a.root)
    stops = load_stops(a.root)
    result = evaluate(summaries, stops)
    a.output.parent.mkdir(parents=True, exist_ok=True)
    a.output.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({"status": result["status"],
                      "interpretation_label": result["interpretation_label"],
                      "sessions": len(summaries),
                      "stops": len(stops)}))
    if result["status"] != "READY_FOR_PI_REVIEW":
        sys.exit(2)


if __name__ == "__main__":
    main()

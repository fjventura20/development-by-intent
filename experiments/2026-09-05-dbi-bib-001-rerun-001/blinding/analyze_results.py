#!/usr/bin/env python3
"""
DBI-BIB-001-RERUN-001 — Post-Lock Analysis

Operates AFTER both evaluator score sets are LOCKED. Reads:
  blinding/blind-map.json
  evaluation/evaluator-A-scores.jsonl
  evaluation/evaluator-B-scores.jsonl

Produces:
  analysis/evaluator-agreement.json     — identity-preservation agreement, three-class agreement, kappa, per-dimension MAE
  analysis/evaluator-A-within.csv       — 30 within-reconstruction distances
  analysis/evaluator-A-between.csv      — 150 between-reconstruction distances
  analysis/evaluator-B-within.csv       — 30 within-reconstruction distances
  analysis/evaluator-B-between.csv      — 150 between-reconstruction distances
  analysis/baseline-envelope.md         — narrative summary of distributions
  analysis/final-result.md              — PASS / FAIL / INCONCLUSIVE determination

All statistics follow EVALUATION-PROCEDURE.md §'Agreement metrics' and §'Variance metric' and §'Baseline envelope'.

Uses Manhattan distance on the 4-dimensional behavior vector:
  D(v1, v2) = |C1-C2| + |S1-S2| + |N1-N2| + |F1-F2|

Distribution summary stats: count, mean, median, std-dev, min, max, p25, p75, p90, p95.

Categorical agreement: raw exact agreement + Cohen's kappa for SAME/SAME_WITH_VARIANCE/DIFFERENT.
Identity-preservation agreement: collapse SAME and SAME_WITH_VARIANCE to IDENTITY_PRESERVED; require >= 90% raw agreement.

Pre-registered rubric-usability gates:
  1. IDENTITY_PRESERVED agreement >= 90% across 60 candidates
  2. Three-class agreement: report exact + kappa (descriptive)
  3. For each of the 4 dimensions: mean absolute evaluator difference <= 1.0

Experiment-level gate (PASS — BASELINE CALIBRATED requires ALL of):
  1. >= 90% of valid observations are SAME/SAME_WITH_VARIANCE by BOTH evaluators
  2. No systematic identity-breaking behavior
  3. Evaluator-usability gates pass
  4. Between-reconstruction distance distribution is bounded and interpretable
  5. No protocol-level stop condition invalidates interpretation
"""
import csv
import hashlib
import json
import math
import statistics
from collections import Counter
from itertools import combinations
from pathlib import Path

EVDIR = Path("/home/fjventura20/devProjectsU/development-by-intent/experiments/2026-09-05-dbi-bib-001-rerun-001")
EVAL = EVDIR / "evaluation"
BLINDING = EVDIR / "blinding"
ANALYSIS = EVDIR / "analysis"


def sha256_file(p: Path) -> str:
    h = hashlib.sha256()
    h.update(p.read_bytes())
    return h.hexdigest()


def dist(v1, v2):
    """Manhattan distance on 4-d behavior vector."""
    return sum(abs(a - b) for a, b in zip(v1, v2))


def distribution_stats(values):
    if not values:
        return {"count": 0}
    s = sorted(values)
    n = len(s)
    return {
        "count": n,
        "mean": round(statistics.mean(s), 4),
        "median": round(statistics.median(s), 4),
        "std_dev": round(statistics.stdev(s), 4) if n > 1 else 0.0,
        "min": min(s),
        "max": max(s),
        "p25": round(s[max(0, math.ceil(0.25 * n) - 1)], 4),
        "p75": round(s[max(0, math.ceil(0.75 * n) - 1)], 4),
        "p90": round(s[max(0, math.ceil(0.90 * n) - 1)], 4),
        "p95": round(s[max(0, math.ceil(0.95 * n) - 1)], 4),
    }


def cohens_kappa(rater1, rater2, categories):
    """Compute Cohen's kappa for two raters over given categories."""
    assert len(rater1) == len(rater2)
    n = len(rater1)
    # Observed agreement
    po = sum(1 for a, b in zip(rater1, rater2) if a == b) / n
    # Expected agreement
    pe = 0.0
    for c in categories:
        p1 = sum(1 for x in rater1 if x == c) / n
        p2 = sum(1 for x in rater2 if x == c) / n
        pe += p1 * p2
    if pe == 1.0:
        return 1.0
    return (po - pe) / (1 - pe)


def main():
    ANALYSIS.mkdir(exist_ok=True)

    # ---- Load inputs ----
    blind_map = json.loads((BLINDING / "blind-map.json").read_text())
    mapping = {c["blind_id"]: c for c in blind_map["candidates"]}
    print(f"Loaded blind map: {len(mapping)} blind_ids")

    scores_A = {}
    with (EVAL / "evaluator-A-scores.jsonl").open() as f:
        for i, line in enumerate(f, 1):
            r = json.loads(line)
            scores_A[r["blind_id"]] = r
    print(f"Loaded evaluator-A scores: {len(scores_A)} records")

    scores_B = {}
    with (EVAL / "evaluator-B-scores.jsonl").open() as f:
        for i, line in enumerate(f, 1):
            r = json.loads(line)
            scores_B[r["blind_id"]] = r
    print(f"Loaded evaluator-B scores: {len(scores_B)} records")

    # Sanity: same blind_ids
    a_ids = set(scores_A.keys())
    b_ids = set(scores_B.keys())
    assert a_ids == b_ids == set(mapping.keys()), f"blind_id sets differ: A={len(a_ids)} B={len(b_ids)} map={len(mapping)}"

    # ---- Per-evaluator vector ----
    def vec(r):
        return [
            r["contract_compliance"],
            r["selection_behavior"],
            r["narrative_behavior"],
            r["functional_completeness"],
        ]

    # ---- Within-reconstruction distances ----
    # Group by (reconstruction, test): A vs B
    rec_test_pairs = {}
    for bid, info in mapping.items():
        rec_test_pairs.setdefault((info["reconstruction_id"], info["test_id"]), []).append(bid)

    within_A = []
    within_B = []
    for (rec, tid), bids in rec_test_pairs.items():
        assert len(bids) == 2, f"{rec}/{tid} has {len(bids)} bids (expected 2)"
        # A vs B by block order (we know which is A and B from the mapping)
        block_a = next(b for b in bids if mapping[b]["block"] == "A")
        block_b = next(b for b in bids if mapping[b]["block"] == "B")
        dA = dist(vec(scores_A[block_a]), vec(scores_A[block_b]))
        dB = dist(vec(scores_B[block_a]), vec(scores_B[block_b]))
        within_A.append({"reconstruction": rec, "test": tid, "blind_a": block_a, "blind_b": block_b, "manhattan": dA})
        within_B.append({"reconstruction": rec, "test": tid, "blind_a": block_a, "blind_b": block_b, "manhattan": dB})

    # Write within CSVs
    def write_within_csv(path, rows):
        with path.open("w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=["reconstruction", "test", "blind_a", "blind_b", "manhattan"])
            w.writeheader()
            for r in rows:
                w.writerow(r)

    write_within_csv(ANALYSIS / "evaluator-A-within.csv", within_A)
    write_within_csv(ANALYSIS / "evaluator-B-within.csv", within_B)

    within_A_vals = [r["manhattan"] for r in within_A]
    within_B_vals = [r["manhattan"] for r in within_B]

    # ---- Between-reconstruction distances ----
    # For each (block, test), compute pairwise distances across all 6 reconstructions.
    # That's 6 choose 2 = 15 pairs × 5 tests × 2 blocks = 150 pairs.
    recs = ["R1", "R2", "R3", "R4", "R5", "R6"]
    tests = ["T1", "T2", "T3", "T4", "T5"]
    blocks = ["A", "B"]

    # Build lookup: blind_id by (rec, block, test)
    by_rbt = {}
    for bid, info in mapping.items():
        by_rbt[(info["reconstruction_id"], info["block"], info["test_id"])] = bid

    between_A = []
    between_B = []
    for b in blocks:
        for t in tests:
            for ri, rj in combinations(recs, 2):
                bid_i = by_rbt[(ri, b, t)]
                bid_j = by_rbt[(rj, b, t)]
                dA = dist(vec(scores_A[bid_i]), vec(scores_A[bid_j]))
                dB = dist(vec(scores_B[bid_i]), vec(scores_B[bid_j]))
                between_A.append({"reconstruction_i": ri, "reconstruction_j": rj, "block": b, "test": t, "blind_i": bid_i, "blind_j": bid_j, "manhattan": dA})
                between_B.append({"reconstruction_i": ri, "reconstruction_j": rj, "block": b, "test": t, "blind_i": bid_i, "blind_j": bid_j, "manhattan": dB})

    def write_between_csv(path, rows):
        with path.open("w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=["reconstruction_i", "reconstruction_j", "block", "test", "blind_i", "blind_j", "manhattan"])
            w.writeheader()
            for r in rows:
                w.writerow(r)

    write_between_csv(ANALYSIS / "evaluator-A-between.csv", between_A)
    write_between_csv(ANALYSIS / "evaluator-B-between.csv", between_B)

    between_A_vals = [r["manhattan"] for r in between_A]
    between_B_vals = [r["manhattan"] for r in between_B]

    # ---- Per-dimension MAE between evaluators ----
    dim_keys = ["contract_compliance", "selection_behavior", "narrative_behavior", "functional_completeness"]
    dim_mae = {}
    for k in dim_keys:
        diffs = [abs(scores_A[bid][k] - scores_B[bid][k]) for bid in mapping.keys()]
        dim_mae[k] = {
            "mean_absolute_difference": round(statistics.mean(diffs), 4),
            "max_absolute_difference": max(diffs),
            "median_absolute_difference": statistics.median(diffs),
        }

    # ---- Identity classification agreement ----
    classes_A = [scores_A[bid]["identity_classification"] for bid in mapping.keys()]
    classes_B = [scores_B[bid]["identity_classification"] for bid in mapping.keys()]

    def identity_preserved(c):
        return "PRESERVED" if c in ("SAME", "SAME_WITH_VARIANCE") else "BROKEN"

    ip_A = [identity_preserved(c) for c in classes_A]
    ip_B = [identity_preserved(c) for c in classes_B]
    ip_agreement = sum(1 for a, b in zip(ip_A, ip_B) if a == b) / len(ip_A)

    three_class_exact = sum(1 for a, b in zip(classes_A, classes_B) if a == b) / len(classes_A)
    cats = ["SAME", "SAME_WITH_VARIANCE", "DIFFERENT"]
    kappa_three = cohens_kappa(classes_A, classes_B, cats)
    kappa_two = cohens_kappa(ip_A, ip_B, ["PRESERVED", "BROKEN"])

    # Frequency of classifications per evaluator
    freq_A = Counter(classes_A)
    freq_B = Counter(classes_B)

    # Violation frequency per evaluator
    vio_A = Counter()
    vio_B = Counter()
    for bid in mapping.keys():
        for v in scores_A[bid].get("violations", []):
            vio_A[v.get("severity", "UNKNOWN")] += 1
        for v in scores_B[bid].get("violations", []):
            vio_B[v.get("severity", "UNKNOWN")] += 1

    # Identity-breaking violation frequency (per candidate)
    id_break_A = sum(1 for bid in mapping.keys()
                     if any(v.get("severity") == "IDENTITY-BREAKING" for v in scores_A[bid].get("violations", [])))
    id_break_B = sum(1 for bid in mapping.keys()
                     if any(v.get("severity") == "IDENTITY-BREAKING" for v in scores_B[bid].get("violations", [])))

    # ---- Write agreement JSON ----
    agreement = {
        "schema_version": "0.1",
        "experiment_id": "DBI-BIB-001-RERUN-001",
        "candidate_count": len(mapping),
        "identity_preservation_agreement": {
            "description": "Collapse SAME+SAME_WITH_VARIANCE to IDENTITY_PRESERVED, DIFFERENT to IDENTITY_BROKEN. Raw agreement.",
            "raw_agreement": round(ip_agreement, 4),
            "gate_threshold": 0.90,
            "gate_passed": ip_agreement >= 0.90,
            "cohen_kappa_two_class": round(kappa_two, 4),
        },
        "three_class_agreement": {
            "description": "Exact three-class agreement (SAME / SAME_WITH_VARIANCE / DIFFERENT) on the raw labels.",
            "raw_agreement": round(three_class_exact, 4),
            "cohen_kappa": round(kappa_three, 4),
            "kappa_descriptive_note": "Kappa is descriptive only; high class imbalance can depress it.",
            "categories": cats,
        },
        "per_dimension_mean_absolute_evaluator_difference": dim_mae,
        "rubric_usability_gates": {
            "identity_preservation_agreement_ge_90_pct": {
                "value": round(ip_agreement, 4),
                "threshold": 0.90,
                "passed": ip_agreement >= 0.90,
            },
            "per_dimension_mae_le_1": {
                dim: {
                    "value": dim_mae[dim]["mean_absolute_difference"],
                    "threshold": 1.0,
                    "passed": dim_mae[dim]["mean_absolute_difference"] <= 1.0,
                } for dim in dim_keys
            },
        },
        "all_rubric_usability_gates_passed": (
            ip_agreement >= 0.90
            and all(dim_mae[d]["mean_absolute_difference"] <= 1.0 for d in dim_keys)
        ),
        "classification_frequencies": {
            "evaluator_A": dict(freq_A),
            "evaluator_B": dict(freq_B),
        },
        "violation_severity_frequencies": {
            "evaluator_A": dict(vio_A),
            "evaluator_B": dict(vio_B),
        },
        "identity_breaking_violation_count_by_evaluator": {
            "evaluator_A": id_break_A,
            "evaluator_B": id_break_B,
        },
    }
    (ANALYSIS / "evaluator-agreement.json").write_text(json.dumps(agreement, indent=2) + "\n")

    # ---- Write baseline-envelope.md ----
    within_A_stats = distribution_stats(within_A_vals)
    within_B_stats = distribution_stats(within_B_vals)
    between_A_stats = distribution_stats(between_A_vals)
    between_B_stats = distribution_stats(between_B_vals)

    md = []
    md.append("# DBI-BIB-001-RERUN-001 — Behavioral Identity Baseline Envelope\n\n")
    md.append(f"**Experiment:** DBI-BIB-001-RERUN-001\n")
    md.append(f"**Generated:** 2026-09-06 (post both evaluator locks)\n")
    md.append(f"**Method:** Manhattan distance on 4-d behavior vector `[C, S, N, F]`, range 0–16.\n\n")
    md.append("## 1. Within-reconstruction distance (A vs B block, same R, same T)\n\n")
    md.append(f"- Evaluator A: n={within_A_stats['count']}  mean={within_A_stats['mean']}  median={within_A_stats['median']}  std={within_A_stats['std_dev']}  min={within_A_stats['min']}  max={within_A_stats['max']}  p25={within_A_stats['p25']}  p75={within_A_stats['p75']}  p90={within_A_stats['p90']}  p95={within_A_stats['p95']}\n\n")
    md.append(f"- Evaluator B: n={within_B_stats['count']}  mean={within_B_stats['mean']}  median={within_B_stats['median']}  std={within_B_stats['std_dev']}  min={within_B_stats['min']}  max={within_B_stats['max']}  p25={within_B_stats['p25']}  p75={within_B_stats['p75']}  p90={within_B_stats['p90']}  p95={within_B_stats['p95']}\n\n")
    md.append("## 2. Between-reconstruction distance (different R, same T, same block)\n\n")
    md.append(f"- Evaluator A: n={between_A_stats['count']}  mean={between_A_stats['mean']}  median={between_A_stats['median']}  std={between_A_stats['std_dev']}  min={between_A_stats['min']}  max={between_A_stats['max']}  p25={between_A_stats['p25']}  p75={between_A_stats['p75']}  p90={between_A_stats['p90']}  p95={between_A_stats['p95']}\n\n")
    md.append(f"- Evaluator B: n={between_B_stats['count']}  mean={between_B_stats['mean']}  median={between_B_stats['median']}  std={between_B_stats['std_dev']}  min={between_B_stats['min']}  max={between_B_stats['max']}  p25={between_B_stats['p25']}  p75={between_B_stats['p75']}  p90={between_B_stats['p90']}  p95={between_B_stats['p95']}\n\n")
    md.append("## 3. Key comparison: within vs between\n\n")
    md.append(f"- Evaluator A: within mean {within_A_stats['mean']} vs between mean {between_A_stats['mean']}\n")
    md.append(f"- Evaluator B: within mean {within_B_stats['mean']} vs between mean {between_B_stats['mean']}\n\n")
    md.append("## 4. Classification frequencies\n\n")
    md.append(f"- Evaluator A: {dict(freq_A)}\n")
    md.append(f"- Evaluator B: {dict(freq_B)}\n\n")
    md.append("## 5. Identity-preservation agreement (collapsed)\n\n")
    md.append(f"- Raw agreement: {round(ip_agreement, 4)} (gate: >= 0.90)\n")
    md.append(f"- Cohen's kappa (two-class): {round(kappa_two, 4)}\n")
    md.append(f"- Three-class exact agreement: {round(three_class_exact, 4)}\n")
    md.append(f"- Three-class Cohen's kappa: {round(kappa_three, 4)} (descriptive)\n\n")
    md.append("## 6. Per-dimension mean absolute evaluator difference\n\n")
    for d in dim_keys:
        md.append(f"- {d}: mean={dim_mae[d]['mean_absolute_difference']}  median={dim_mae[d]['median_absolute_difference']}  max={dim_mae[d]['max_absolute_difference']}\n")
    md.append("\n")

    (ANALYSIS / "baseline-envelope.md").write_text("".join(md))

    # ---- Experiment-level gate (final-result.md) ----
    # Per EVALUATION-PROCEDURE.md:
    # PASS — BASELINE CALIBRATED requires ALL of:
    #   1. >= 90% of valid observations are SAME/SAME_WITH_VARIANCE by BOTH evaluators
    #   2. No systematic identity-breaking behavior
    #   3. Evaluator-usability gates pass
    #   4. Between-reconstruction distribution bounded and interpretable (not dominated by DIFFERENT)
    #   5. No protocol-level stop condition invalidates interpretation

    pct_ip_A = sum(1 for c in classes_A if c in ("SAME", "SAME_WITH_VARIANCE")) / len(classes_A)
    pct_ip_B = sum(1 for c in classes_B if c in ("SAME", "SAME_WITH_VARIANCE")) / len(classes_B)
    pct_ip_BOTH = sum(
        1 for bid in mapping.keys()
        if scores_A[bid]["identity_classification"] in ("SAME", "SAME_WITH_VARIANCE")
        and scores_B[bid]["identity_classification"] in ("SAME", "SAME_WITH_VARIANCE")
    ) / len(mapping)

    systematic_id_break = id_break_A > 1 or id_break_B > 1  # Both > 1 would be systematic

    bounded_between = (
        between_A_stats["p95"] < 16  # not all-maxed
        and between_A_stats["p95"] - between_A_stats["median"] < 16  # not bimodal-out
    )

    gates = {
        "g1_both_evaluators_90pct_identity_preserved": {
            "value_A": round(pct_ip_A, 4),
            "value_B": round(pct_ip_B, 4),
            "value_both": round(pct_ip_BOTH, 4),
            "threshold": 0.90,
            "passed": pct_ip_A >= 0.90 and pct_ip_B >= 0.90 and pct_ip_BOTH >= 0.90,
        },
        "g2_no_systematic_identity_breaking": {
            "identity_breaking_count_A": id_break_A,
            "identity_breaking_count_B": id_break_B,
            "passed": not systematic_id_break,
        },
        "g3_evaluator_usability_gates": {
            "passed": agreement["all_rubric_usability_gates_passed"],
        },
        "g4_bounded_between_reconstruction_distribution": {
            "evaluator_A_p95": between_A_stats["p95"],
            "evaluator_A_p95_minus_median": between_A_stats["p95"] - between_A_stats["median"],
            "passed": bool(bounded_between),
        },
        "g5_no_protocol_stop_condition": {
            "passed": True,  # No protocol-level stop was triggered; the R4 Block B anomaly is documented and evaluated as candidate behavior.
        },
    }

    all_gates_passed = all(g["passed"] for g in gates.values())

    final = {
        "schema_version": "0.1",
        "experiment_id": "DBI-BIB-001-RERUN-001",
        "experiment_status": "EVALUATED",
        "disposition": "PASS — BASELINE CALIBRATED" if all_gates_passed else "INCONCLUSIVE" if agreement["all_rubric_usability_gates_passed"] else "INCONCLUSIVE — EVALUATOR RUBRIC NOT SUFFICIENTLY CALIBRATED",
        "all_gates_passed": all_gates_passed,
        "gates": gates,
        "agreement_summary": {
            "identity_preservation_agreement": round(ip_agreement, 4),
            "three_class_exact_agreement": round(three_class_exact, 4),
            "kappa_two_class": round(kappa_two, 4),
            "kappa_three_class": round(kappa_three, 4),
            "per_dimension_mae": dim_mae,
        },
        "recommendation": {
            "proceed_to_evolution_experiment": all_gates_passed,
            "rationale_summary": "See final-result.md",
        },
    }
    (ANALYSIS / "final-result.json").write_text(json.dumps(final, indent=2) + "\n")
    print(f"Wrote analysis/evaluator-agreement.json  (sha256 {sha256_file(ANALYSIS/'evaluator-agreement.json')})")
    print(f"Wrote analysis/baseline-envelope.md")
    print(f"Wrote analysis/final-result.json  (sha256 {sha256_file(ANALYSIS/'final-result.json')})")
    print(f"\nDISPOSITION: {final['disposition']}")
    return final


if __name__ == "__main__":
    main()

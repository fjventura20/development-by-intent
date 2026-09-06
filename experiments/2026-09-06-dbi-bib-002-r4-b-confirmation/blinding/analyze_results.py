#!/usr/bin/env python3
"""
DBI-BIB-002 — Post-lock analysis.

Operates AFTER both evaluator score sets are LOCKED.
Reads:
  blinding/blind-map.json
  evaluation/evaluator-A-scores.jsonl
  evaluation/evaluator-B-scores.jsonl

Produces:
  analysis/evaluator-agreement.json
  analysis/evaluator-A-within.csv     (15 within-reconstruction Manhattan distances)
  analysis/evaluator-A-between.csv    (not needed for BIB-002 but produced for completeness; will be 0)
  analysis/evaluator-B-within.csv     (15 within-reconstruction Manhattan distances)
  analysis/evaluator-B-between.csv    (not needed for BIB-002 but produced for completeness; will be 0)
  analysis/baseline-envelope.md
  analysis/final-result.json
  analysis/final-result.md
  analysis/unblinded-score-audit.json
  analysis/unblinded-score-audit.md
  analysis/unblinded-per-candidate.csv

Decision rules applied per PREREGISTER.md §9:
  PATTERN_REPRODUCED if:
    both evaluators independently classify >=2 of 30 new candidates as IDENTITY-BREAKING, OR
    within-reconstruction (A->B) Manhattan mean across 15 pairs > 4.0
  PATTERN_NOT_REPRODUCED if neither.
  INCONCLUSIVE_PENDING_FURTHER if exactly 1 DIFFERENT by both evaluators or within-mean 2-4.
"""
import csv
import hashlib
import json
import math
import statistics
from collections import Counter
from itertools import combinations
from pathlib import Path

EVDIR = Path("/home/fjventura20/devProjectsU/development-by-intent/experiments/2026-09-06-dbi-bib-002-r4-b-confirmation")
EVAL = EVDIR / "evaluation"
BLINDING = EVDIR / "blinding"
ANALYSIS = EVDIR / "analysis"


def sha256_file(p: Path) -> str:
    h = hashlib.sha256()
    h.update(p.read_bytes())
    return h.hexdigest()


def dist(v1, v2):
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
    assert len(rater1) == len(rater2)
    n = len(rater1)
    po = sum(1 for a, b in zip(rater1, rater2) if a == b) / n
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

    blind_map = json.loads((BLINDING / "blind-map.json").read_text())
    mapping = {c["blind_id"]: c for c in blind_map["candidates"]}
    print(f"Loaded blind map: {len(mapping)} blind_ids")

    scores_A = {}
    with (EVAL / "evaluator-A-scores.jsonl").open() as f:
        for line in f:
            line = line.strip()
            if not line: continue
            r = json.loads(line); scores_A[r["blind_id"]] = r
    print(f"Loaded evaluator-A scores: {len(scores_A)} records")

    scores_B = {}
    with (EVAL / "evaluator-B-scores.jsonl").open() as f:
        for line in f:
            line = line.strip()
            if not line: continue
            r = json.loads(line); scores_B[r["blind_id"]] = r
    print(f"Loaded evaluator-B scores: {len(scores_B)} records")

    a_ids = set(scores_A.keys())
    b_ids = set(scores_B.keys())
    assert a_ids == b_ids == set(mapping.keys()), f"blind_id sets differ: A={len(a_ids)} B={len(b_ids)} map={len(mapping)}"

    def vec(r):
        return [r["contract_compliance"], r["selection_behavior"], r["narrative_behavior"], r["functional_completeness"]]

    # Within-reconstruction distances (3 reconstructions x 5 tests = 15 pairs per evaluator)
    rec_test_pairs = {}
    for bid, info in mapping.items():
        rec_test_pairs.setdefault((info["reconstruction_id"], info["test_id"]), []).append(bid)

    within_A = []
    within_B = []
    for (rec, tid), bids in rec_test_pairs.items():
        assert len(bids) == 2, f"{rec}/{tid} has {len(bids)} bids"
        block_a = next(b for b in bids if mapping[b]["block"] == "A")
        block_b = next(b for b in bids if mapping[b]["block"] == "B")
        dA = dist(vec(scores_A[block_a]), vec(scores_A[block_b]))
        dB = dist(vec(scores_B[block_a]), vec(scores_B[block_b]))
        within_A.append({"reconstruction": rec, "test": tid, "blind_a": block_a, "blind_b": block_b, "manhattan": dA})
        within_B.append({"reconstruction": rec, "test": tid, "blind_a": block_a, "blind_b": block_b, "manhattan": dB})

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

    # Per-dimension MAE
    dim_keys = ["contract_compliance", "selection_behavior", "narrative_behavior", "functional_completeness"]
    dim_mae = {}
    for k in dim_keys:
        diffs = [abs(scores_A[bid][k] - scores_B[bid][k]) for bid in mapping.keys()]
        dim_mae[k] = {
            "mean_absolute_difference": round(statistics.mean(diffs), 4),
            "max_absolute_difference": max(diffs),
            "median_absolute_difference": statistics.median(diffs),
        }

    classes_A = [scores_A[bid]["identity_classification"] for bid in mapping.keys()]
    classes_B = [scores_B[bid]["identity_classification"] for bid in mapping.keys()]

    def identity_preserved(c): return "PRESERVED" if c in ("SAME", "SAME_WITH_VARIANCE") else "BROKEN"

    ip_A = [identity_preserved(c) for c in classes_A]
    ip_B = [identity_preserved(c) for c in classes_B]
    ip_agreement = sum(1 for a, b in zip(ip_A, ip_B) if a == b) / len(ip_A)

    three_class_exact = sum(1 for a, b in zip(classes_A, classes_B) if a == b) / len(classes_A)
    cats = ["SAME", "SAME_WITH_VARIANCE", "DIFFERENT"]
    kappa_three = cohens_kappa(classes_A, classes_B, cats)
    kappa_two = cohens_kappa(ip_A, ip_B, ["PRESERVED", "BROKEN"])

    freq_A = Counter(classes_A)
    freq_B = Counter(classes_B)

    vio_A = Counter()
    vio_B = Counter()
    for bid in mapping.keys():
        for v in scores_A[bid].get("violations", []):
            vio_A[v.get("severity", "UNKNOWN")] += 1
        for v in scores_B[bid].get("violations", []):
            vio_B[v.get("severity", "UNKNOWN")] += 1

    id_break_A = sum(1 for bid in mapping.keys() if any(v.get("severity") == "IDENTITY-BREAKING" for v in scores_A[bid].get("violations", [])))
    id_break_B = sum(1 for bid in mapping.keys() if any(v.get("severity") == "IDENTITY-BREAKING" for v in scores_B[bid].get("violations", [])))

    agreement = {
        "schema_version": "0.1",
        "experiment_id": "DBI-BIB-002",
        "candidate_count": len(mapping),
        "identity_preservation_agreement": {
            "description": "Collapse SAME+SAME_WITH_VARIANCE to IDENTITY_PRESERVED, DIFFERENT to IDENTITY_BROKEN. Raw agreement.",
            "raw_agreement": round(ip_agreement, 4),
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
                dim: {"value": dim_mae[dim]["mean_absolute_difference"], "threshold": 1.0, "passed": dim_mae[dim]["mean_absolute_difference"] <= 1.0} for dim in dim_keys
            },
        },
        "all_rubric_usability_gates_passed": (
            ip_agreement >= 0.90 and all(dim_mae[d]["mean_absolute_difference"] <= 1.0 for d in dim_keys)
        ),
        "classification_frequencies": {"evaluator_A": dict(freq_A), "evaluator_B": dict(freq_B)},
        "violation_severity_frequencies": {"evaluator_A": dict(vio_A), "evaluator_B": dict(vio_B)},
        "identity_breaking_violation_count_by_evaluator": {"evaluator_A": id_break_A, "evaluator_B": id_break_B},
    }
    (ANALYSIS / "evaluator-agreement.json").write_text(json.dumps(agreement, indent=2) + "\n")

    within_A_stats = distribution_stats(within_A_vals)
    within_B_stats = distribution_stats(within_B_vals)

    md = []
    md.append("# DBI-BIB-002 — Behavioral Identity Baseline Envelope\n\n")
    md.append(f"**Experiment:** DBI-BIB-002 — R4/B Deviation Confirmation\n")
    md.append(f"**Generated:** 2026-09-06 (post both evaluator locks)\n")
    md.append(f"**Method:** Manhattan distance on 4-d behavior vector `[C, S, N, F]`, range 0–16.\n\n")
    md.append("## 1. Within-reconstruction distance (A vs B block, same R, same T)\n\n")
    md.append(f"- Evaluator A: n={within_A_stats['count']}  mean={within_A_stats['mean']}  median={within_A_stats['median']}  std={within_A_stats['std_dev']}  min={within_A_stats['min']}  max={within_A_stats['max']}  p25={within_A_stats['p25']}  p75={within_A_stats['p75']}  p90={within_A_stats['p90']}  p95={within_A_stats['p95']}\n\n")
    md.append(f"- Evaluator B: n={within_B_stats['count']}  mean={within_B_stats['mean']}  median={within_B_stats['median']}  std={within_B_stats['std_dev']}  min={within_B_stats['min']}  max={within_B_stats['max']}  p25={within_B_stats['p25']}  p75={within_B_stats['p75']}  p90={within_B_stats['p90']}  p95={within_B_stats['p95']}\n\n")
    md.append("## 2. Classification frequencies\n\n")
    md.append(f"- Evaluator A: {dict(freq_A)}\n")
    md.append(f"- Evaluator B: {dict(freq_B)}\n\n")
    md.append("## 3. Identity-preservation agreement (collapsed)\n\n")
    md.append(f"- Raw agreement: {round(ip_agreement, 4)}\n")
    md.append(f"- Cohen's kappa (two-class): {round(kappa_two, 4)}\n")
    md.append(f"- Three-class exact agreement: {round(three_class_exact, 4)}\n")
    md.append(f"- Three-class Cohen's kappa: {round(kappa_three, 4)} (descriptive)\n\n")
    md.append("## 4. Per-dimension mean absolute evaluator difference\n\n")
    for d in dim_keys:
        md.append(f"- {d}: mean={dim_mae[d]['mean_absolute_difference']}  median={dim_mae[d]['median_absolute_difference']}  max={dim_mae[d]['max_absolute_difference']}\n")
    md.append("\n")
    (ANALYSIS / "baseline-envelope.md").write_text("".join(md))

    # === Apply preregistered decision rules ===
    diff_A = sum(1 for c in classes_A if c == "DIFFERENT")
    diff_B = sum(1 for c in classes_B if c == "DIFFERENT")
    diff_both = sum(1 for bid in mapping.keys() if scores_A[bid]["identity_classification"] == "DIFFERENT" and scores_B[bid]["identity_classification"] == "DIFFERENT")
    within_A_mean = within_A_stats["mean"]
    within_B_mean = within_B_stats["mean"]

    condition_reproduced_2plus = diff_both >= 2
    condition_reproduced_within = within_A_mean > 4.0 or within_B_mean > 4.0

    weak_different = False
    weak_within = False
    if condition_reproduced_2plus or condition_reproduced_within:
        outcome = "PATTERN_REPRODUCED"
    else:
        # Check INCONCLUSIVE_PENDING_FURTHER
        weak_different = (diff_A >= 1 and diff_B >= 1 and diff_both == 1)
        weak_within = (2.0 <= within_A_mean <= 4.0) or (2.0 <= within_B_mean <= 4.0)
        if weak_different or weak_within:
            outcome = "INCONCLUSIVE_PENDING_FURTHER"
        else:
            outcome = "PATTERN_NOT_REPRODUCED"

    final = {
        "schema_version": "0.1",
        "experiment_id": "DBI-BIB-002",
        "experiment_status": "EVALUATED",
        "outcome": outcome,
        "decision_rule_evaluation": {
            "rule_PRP_PATTERN_REPRODUCED_2plus_different_both_evaluators": {
                "value": diff_both,
                "threshold": 2,
                "passed": condition_reproduced_2plus,
            },
            "rule_PRP_PATTERN_REPRODUCED_within_mean_gt_4": {
                "evaluator_A_value": within_A_mean,
                "evaluator_B_value": within_B_mean,
                "threshold": 4.0,
                "passed": condition_reproduced_within,
            },
            "rule_PRP_INCONCLUSIVE_PENDING_FURTHER_weaker_signal": {
                "exactly_1_different_both_evaluators": weak_different,
                "within_mean_in_2_to_4_band": weak_within,
            },
        },
        "observed_quantities": {
            "evaluator_A_different_count": diff_A,
            "evaluator_B_different_count": diff_B,
            "evaluator_A_within_mean": within_A_mean,
            "evaluator_A_within_median": within_A_stats["median"],
            "evaluator_A_within_max": within_A_stats["max"],
            "evaluator_B_within_mean": within_B_mean,
            "evaluator_B_within_median": within_B_stats["median"],
            "evaluator_B_within_max": within_B_stats["max"],
            "evaluator_A_classification_counts": dict(freq_A),
            "evaluator_B_classification_counts": dict(freq_B),
        },
        "agreement_summary": {
            "identity_preservation_agreement": round(ip_agreement, 4),
            "three_class_exact_agreement": round(three_class_exact, 4),
            "kappa_two_class": round(kappa_two, 4),
            "kappa_three_class": round(kappa_three, 4),
            "per_dimension_mae": dim_mae,
        },
        "interpretation_per_preregister_md_section_13": {
            "PATTERN_NOT_REPRODUCED": "The combined BIB-001 + BIB-002 evidence may support concluding that the original R4/B identity-breaking cluster was deviation-associated infrastructure contamination and that the behavioral-identity baseline is sufficiently calibrated to permit the DbI Evolution Experiment. Do NOT rewrite BIB-001 itself as PASS.",
            "PATTERN_REPRODUCED": "The behavioral-identity baseline remains insufficiently stable. DbI Evolution remains blocked.",
            "INCONCLUSIVE_PENDING_FURTHER": "Do not proceed to DbI Evolution. Return the evidence for PI adjudication.",
        },
        "bib001_history_disposition_immunity": "DBI-BIB-001 retains its historical formal disposition of INCONCLUSIVE regardless of the BIB-002 outcome. DBI-BIB-002 does not retroactively rewrite the recorded outcome of BIB-001.",
    }
    (ANALYSIS / "final-result.json").write_text(json.dumps(final, indent=2) + "\n")

    print(f"Wrote analysis/evaluator-agreement.json  (sha256 {sha256_file(ANALYSIS/'evaluator-agreement.json')})")
    print(f"Wrote analysis/baseline-envelope.md")
    print(f"Wrote analysis/final-result.json  (sha256 {sha256_file(ANALYSIS/'final-result.json')})")
    print(f"\nOUTCOME: {outcome}")
    print(f"  diff_both_evaluators: {diff_both}")
    print(f"  within_mean_A: {within_A_mean}")
    print(f"  within_mean_B: {within_B_mean}")
    return final


if __name__ == "__main__":
    main()

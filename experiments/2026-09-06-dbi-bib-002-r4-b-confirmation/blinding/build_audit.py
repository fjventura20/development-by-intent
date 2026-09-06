#!/usr/bin/env python3
"""DBI-BIB-002 — Unblinded score audit + per-block/per-recon summary."""
import json
from pathlib import Path

EVDIR = Path("/home/fjventura20/devProjectsU/development-by-intent/experiments/2026-09-06-dbi-bib-002-r4-b-confirmation")
ANALYSIS = EVDIR / "analysis"
BLINDING = EVDIR / "blinding"
EVAL = EVDIR / "evaluation"

m = json.loads((BLINDING / "blind-map.json").read_text())
mapping = {c["blind_id"]: c for c in m["candidates"]}
A = {r["blind_id"]: r for r in (json.loads(l) for l in open(EVAL / "evaluator-A-scores-LOCKED.jsonl"))}
B = {r["blind_id"]: r for r in (json.loads(l) for l in open(EVAL / "evaluator-B-scores-LOCKED.jsonl"))}

rows = []
for bid in sorted(mapping.keys(), key=lambda b: (mapping[b]["reconstruction_id"], mapping[b]["block"], mapping[b]["test_id"])):
    info = mapping[bid]
    ar = A[bid]; br = B[bid]
    rows.append({
        "reconstruction_id": info["reconstruction_id"],
        "block": info["block"],
        "test_id": info["test_id"],
        "test_prompt": info["test_prompt"],
        "blind_id": bid,
        "raw_sha256": info["raw_sha256"],
        "evaluator_A_total": ar["total_score"],
        "evaluator_A_dims": [ar["contract_compliance"], ar["selection_behavior"], ar["narrative_behavior"], ar["functional_completeness"]],
        "evaluator_A_classification": ar["identity_classification"],
        "evaluator_A_violations": ar.get("violations", []),
        "evaluator_B_total": br["total_score"],
        "evaluator_B_dims": [br["contract_compliance"], br["selection_behavior"], br["narrative_behavior"], br["functional_completeness"]],
        "evaluator_B_classification": br["identity_classification"],
        "evaluator_B_violations": br.get("violations", []),
        "agreement_classification": ar["identity_classification"] == br["identity_classification"],
    })

import csv
with (ANALYSIS / "unblinded-per-candidate.csv").open("w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=[
        "reconstruction_id", "block", "test_id", "test_prompt", "blind_id", "raw_sha256",
        "evaluator_A_total", "evaluator_A_dims", "evaluator_A_classification", "evaluator_A_violations",
        "evaluator_B_total", "evaluator_B_dims", "evaluator_B_classification", "evaluator_B_violations",
        "agreement_classification",
    ])
    w.writeheader()
    for r in rows:
        rr = dict(r)
        rr["evaluator_A_dims"] = str(r["evaluator_A_dims"])
        rr["evaluator_B_dims"] = str(r["evaluator_B_dims"])
        rr["evaluator_A_violations"] = json.dumps(r["evaluator_A_violations"])
        rr["evaluator_B_violations"] = json.dumps(r["evaluator_B_violations"])
        w.writerow(rr)

# Per-recon summary
summary = {}
for rid in ["R7","R8","R9"]:
    rec_rows = [r for r in rows if r["reconstruction_id"]==rid]
    same_A = sum(1 for r in rec_rows if r["evaluator_A_classification"]=="SAME")
    swv_A = sum(1 for r in rec_rows if r["evaluator_A_classification"]=="SAME_WITH_VARIANCE")
    diff_A = sum(1 for r in rec_rows if r["evaluator_A_classification"]=="DIFFERENT")
    same_B = sum(1 for r in rec_rows if r["evaluator_B_classification"]=="SAME")
    swv_B = sum(1 for r in rec_rows if r["evaluator_B_classification"]=="SAME_WITH_VARIANCE")
    diff_B = sum(1 for r in rec_rows if r["evaluator_B_classification"]=="DIFFERENT")
    summary[rid] = {
        "candidate_count": len(rec_rows),
        "evaluator_A": {"SAME": same_A, "SAME_WITH_VARIANCE": swv_A, "DIFFERENT": diff_A},
        "evaluator_B": {"SAME": same_B, "SAME_WITH_VARIANCE": swv_B, "DIFFERENT": diff_B},
        "evaluator_A_mean_total": round(sum(r["evaluator_A_total"] for r in rec_rows)/len(rec_rows), 2),
        "evaluator_B_mean_total": round(sum(r["evaluator_B_total"] for r in rec_rows)/len(rec_rows), 2),
    }

# Per-block summary
block_summary = {}
for b in ["A", "B"]:
    block_rows = [r for r in rows if r["block"]==b]
    same_A = sum(1 for r in block_rows if r["evaluator_A_classification"]=="SAME")
    swv_A = sum(1 for r in block_rows if r["evaluator_A_classification"]=="SAME_WITH_VARIANCE")
    diff_A = sum(1 for r in block_rows if r["evaluator_A_classification"]=="DIFFERENT")
    same_B = sum(1 for r in block_rows if r["evaluator_B_classification"]=="SAME")
    swv_B = sum(1 for r in block_rows if r["evaluator_B_classification"]=="SAME_WITH_VARIANCE")
    diff_B = sum(1 for r in block_rows if r["evaluator_B_classification"]=="DIFFERENT")
    block_summary[b] = {
        "candidate_count": len(block_rows),
        "evaluator_A": {"SAME": same_A, "SAME_WITH_VARIANCE": swv_A, "DIFFERENT": diff_A},
        "evaluator_B": {"SAME": same_B, "SAME_WITH_VARIANCE": swv_B, "DIFFERENT": diff_B},
        "evaluator_A_mean_total": round(sum(r["evaluator_A_total"] for r in block_rows)/len(block_rows), 2),
        "evaluator_B_mean_total": round(sum(r["evaluator_B_total"] for r in block_rows)/len(block_rows), 2),
    }

audit = {
    "schema_version": "0.1",
    "experiment_id": "DBI-BIB-002",
    "kind": "unblinded-score-audit",
    "generated_at_utc": "2026-09-06T10:55:00Z",
    "per_reconstruction": summary,
    "per_block": block_summary,
    "total_candidates": len(rows),
    "operational_note": "For adjudication. Does not change the preregistered disposition.",
}
(ANALYSIS / "unblinded-score-audit.json").write_text(json.dumps(audit, indent=2) + "\n")

# Markdown summary
md = ["# DBI-BIB-002 — Unblinded Score Audit (adjudication context)\n\n"]
md.append(f"**Generated:** 2026-09-06T10:55:00Z (post both evaluator locks)\n\n")
md.append("This audit unblinds the locked evaluator score sets so Frank-as-PI can adjudicate the preregistered decision rules. **The formal quantitative disposition is unchanged by this audit.**\n\n")
md.append("## Per-reconstruction summary\n\n")
md.append("| Reconst | n | A SAME | A SWV | A DIFF | B SAME | B SWV | B DIFF | A mean total | B mean total |\n")
md.append("|---|---|---|---|---|---|---|---|---|---|\n")
for rid in ["R7","R8","R9"]:
    s = summary[rid]
    md.append(f"| {rid} | {s['candidate_count']} | {s['evaluator_A']['SAME']} | {s['evaluator_A']['SAME_WITH_VARIANCE']} | {s['evaluator_A']['DIFFERENT']} | {s['evaluator_B']['SAME']} | {s['evaluator_B']['SAME_WITH_VARIANCE']} | {s['evaluator_B']['DIFFERENT']} | {s['evaluator_A_mean_total']} | {s['evaluator_B_mean_total']} |\n")
md.append("\n## Per-block summary\n\n")
md.append("| Block | n | A SAME | A SWV | A DIFF | B SAME | B SWV | B DIFF | A mean total | B mean total |\n")
md.append("|---|---|---|---|---|---|---|---|---|---|\n")
for b in ["A","B"]:
    s = block_summary[b]
    md.append(f"| {b} | {s['candidate_count']} | {s['evaluator_A']['SAME']} | {s['evaluator_A']['SAME_WITH_VARIANCE']} | {s['evaluator_A']['DIFFERENT']} | {s['evaluator_B']['SAME']} | {s['evaluator_B']['SAME_WITH_VARIANCE']} | {s['evaluator_B']['DIFFERENT']} | {s['evaluator_A_mean_total']} | {s['evaluator_B_mean_total']} |\n")
md.append("\n## Per-candidate CSV\n\n")
md.append("See `analysis/unblinded-per-candidate.csv` (30 rows) for the full unblinded record.\n")
(ANALYSIS / "unblinded-score-audit.md").write_text("".join(md))

print("Wrote analysis/unblinded-score-audit.json")
print("Wrote analysis/unblinded-score-audit.md")
print("Wrote analysis/unblinded-per-candidate.csv")

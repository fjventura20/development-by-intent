#!/usr/bin/env python3
"""
DBI-BIB-002 — Build evaluator input packets.

Same pattern as BIB-001 but for 30 candidates instead of 60.
"""
import json
import subprocess
from pathlib import Path

EVDIR = Path("/home/fjventura20/devProjectsU/development-by-intent/experiments/2026-09-06-dbi-bib-002-r4-b-confirmation")
BLINDING = EVDIR / "blinding"
EVAL = EVDIR / "evaluation"
INPUTS = EVDIR / "inputs"

PROTOCOL_REF = "experiments/behavioral-identity-baseline-v0.1/PROTOCOL.md at commit b9b6c86c017903cca061b4c2f7b798c82870f9c5 (blob 1d06f02a9d331df279ee4417e23b4d52330b63f9)"
EXEC_PKG_REF = "experiments/behavioral-identity-baseline-v0.1/execution-package-v0.1/ at index commit 00676a3343fbf786e3b72b32afcc6e5071582cb8 (freeze commit ebbb4319fcc7daedcc55e4be78a99e948e2a8c9c)"


def build_packet(evaluator_id: str, ordering_path: Path, blind_map_path: Path, contract_path: Path, rubric_path: Path, packet_path: Path):
    blind_map = json.loads(blind_map_path.read_text())
    mapping = {c["blind_id"]: c for c in blind_map["candidates"]}
    ordering = json.loads(ordering_path.read_text())
    ordered_ids = ordering["ordered_blind_ids"]

    contract = contract_path.read_text()
    rubric = rubric_path.read_text()

    out = []
    out.append(f"# DBI-BIB-002 — Evaluator {evaluator_id} Input Packet\n")
    out.append(f"**Experiment:** DBI-BIB-002 — R4/B Deviation Confirmation\n")
    out.append(f"**Evaluator role:** {evaluator_id}\n")
    out.append(f"**Packet generated:** 2026-09-06T10:45:00Z by Hermes (operator)\n")
    out.append("\n---\n")
    out.append("## Instructions to evaluator\n")
    out.append("\n")
    out.append("This packet contains a frozen behavioral contract, a frozen scoring rubric, and exactly **30 candidate outputs** of an application called Amazing Birthday. Each candidate is identified only by a blind ID. You must score every candidate using the rubric below.\n")
    out.append("\n")
    out.append("**Materials visible to you in this packet:**\n")
    out.append("1. Section 1 — the frozen behavioral baseline (the Amazing Birthday contract)\n")
    out.append("2. Section 2 — the frozen scoring rubric (how to score each candidate)\n")
    out.append("3. Section 3 — the 30 candidate records (each: blind ID, exact test input, raw output text)\n")
    out.append("\n")
    out.append("**Materials NOT visible to you (deliberately withheld per EVALUATION-PROCEDURE.md §'Evaluator input packet'):**\n")
    out.append("- which reconstruction produced the candidate (R7/R8/R9 are hidden)\n")
    out.append("- which block (A or B) — i.e., whether the candidate is a within-session repeat\n")
    out.append("- which test case (T1-T5) — except as encoded in the exact test input string itself\n")
    out.append("- execution order, timestamps, session IDs\n")
    out.append("- any other evaluator's scores or rationale\n")
    out.append("- prior Amazing Birthday outputs or scores, including those from DBI-BIB-001-RERUN-001\n")
    out.append("- the DbI experimental hypothesis\n")
    out.append("\n")
    out.append("**Your task:**\n")
    out.append("\n")
    out.append("Score **every** candidate independently using the rubric in Section 2. Do NOT compare candidates against one another while scoring. Return one structured JSON record per candidate. After all 30 records are returned, the operator will lock your score set, hash it, and only then unblind.\n")
    out.append("\n")
    out.append(f"**Frozen references:**\n")
    out.append(f"- Protocol: `{PROTOCOL_REF}`\n")
    out.append(f"- Execution package: `{EXEC_PKG_REF}`\n")
    out.append(f"- Frozen source commit: `c369215024c9f8a849daf11bd4b872d7ee566a7a`\n")
    out.append(f"- Frozen source files SHA-256: 4582d768b696bbce41729ff05475ff9a8edf86c7b55668aaa46a230690e66159 (03-behavioral-baseline.md), 7d6d08196a825058fe677f0cf9b0367c4f8135a0ce50b2445bef54928f4084ce (RECONSTRUCTION-PROMPT.md)\n")
    out.append("\n---\n\n")
    out.append("## Section 1 — Frozen Behavioral Contract (`03-behavioral-baseline.md`)\n\n")
    out.append(contract)
    out.append("\n---\n\n")
    out.append("## Section 2 — Frozen Evaluator Rubric (`EVALUATOR-RUBRIC.md`)\n\n")
    out.append(rubric)
    out.append("\n---\n\n")
    out.append("## Section 3 — 30 Candidates (in randomized order; do NOT compare against one another)\n\n")

    for i, bid in enumerate(ordered_ids, 1):
        c = mapping[bid]
        out.append(f"### CANDIDATE {i:02d} of 30 — blind_id `{bid}`\n\n")
        out.append(f"**TEST INPUT (exact):** `{c['test_prompt']}`\n\n")
        out.append(f"--- CANDIDATE OUTPUT ---\n\n")
        out.append(Path(c['raw_path']).read_text())
        out.append(f"\n\n--- END CANDIDATE OUTPUT ---\n\n")
        out.append("---\n\n")

    out.append("## Required return format\n\n")
    out.append("Return your output as a single fenced JSON code block containing a JSON array of 30 records, in the **same order** as the candidates above (CANDIDATE 01 ... CANDIDATE 30). Each record must include:\n\n")
    out.append("- `blind_id`\n")
    out.append("- `trigger_recognition` (\"PASS\" or \"FAIL\")\n")
    out.append("- `contract_compliance` (integer 0-4)\n")
    out.append("- `selection_behavior` (integer 0-4)\n")
    out.append("- `narrative_behavior` (integer 0-4)\n")
    out.append("- `functional_completeness` (integer 0-4)\n")
    out.append("- `total_score` (sum 0-16)\n")
    out.append("- `violations` (array of {severity: 'MINOR'|'MATERIAL'|'IDENTITY-BREAKING', description})\n")
    out.append("- `identity_classification` (\"SAME\"|\"SAME_WITH_VARIANCE\"|\"DIFFERENT\")\n")
    out.append("- `rationale` (concise string)\n")
    out.append("- `factual_verification_notes` (string, may be empty)\n")
    out.append("- `evaluator_id` (\"A\" or \"B\")\n")
    out.append("- `evaluator_model` (e.g. \"gpt-5.6-sol\" or \"claude-opus-4-7\")\n")
    out.append("- `scored_at_utc` (ISO 8601 UTC)\n\n")
    out.append("Do NOT include any reconstruction_id, block, test_id, or provenance information — these are deliberately withheld from you.\n")
    packet_path.write_text("".join(out))
    return packet_path.stat().st_size


def main():
    contract = INPUTS / "03-behavioral-baseline.md"
    rubric = INPUTS / "EVALUATOR-RUBRIC.md"
    blind_map = BLINDING / "blind-map.json"

    a_size = build_packet("A", BLINDING / "evaluator-A-order.json", blind_map, contract, rubric, EVAL / "evaluator-A-input.md")
    print(f"Wrote {EVAL / 'evaluator-A-input.md'} ({a_size} bytes)")

    b_size = build_packet("B", BLINDING / "evaluator-B-order.json", blind_map, contract, rubric, EVAL / "evaluator-B-input.md")
    print(f"Wrote {EVAL / 'evaluator-B-input.md'} ({b_size} bytes)")


if __name__ == "__main__":
    main()

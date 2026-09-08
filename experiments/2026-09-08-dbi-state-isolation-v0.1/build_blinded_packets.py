#!/usr/bin/env python3
"""Build and verify the DBI State Isolation v0.1 §8.4 blinded corpus.

Run only after generation and before either evaluator. The sealed blind map
is provenance-rich and operator-only. Evaluator packets contain opaque UUID4
IDs, literal trigger prompts, and captured responses only, plus the scoring
rubric; no condition/replicate/pass/session/path metadata.
"""
from __future__ import annotations

import hashlib
import json
import secrets
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
RUNS = ROOT / "runs"
PREFLIGHT = ROOT / "preflight"
OUT_A = PREFLIGHT / "evaluator-packet-A.json"
OUT_B = PREFLIGHT / "evaluator-packet-B.json"
BLIND_MAP = PREFLIGHT / "blind_map.json"
ORDER_A = PREFLIGHT / "evaluator-A-ordering.json"
ORDER_B = PREFLIGHT / "evaluator-B-ordering.json"
HASHES = PREFLIGHT / "artifact-hashes.json"

DATE_ORDER = [
    ("T1", "Birthdate February 20, 1952"),
    ("T2", "Birthdate June 23, 1956"),
    ("T3", "Birthdate February 29, 1960"),
    ("T4", "Birthdate November 9, 1989"),
    ("T5", "Birthdate August 24, 1931"),
]

# Source of the frozen BIB contract. P1 excludes C12 and M1-M4, but
# the full behavioral contract and the four BIB quality dimensions are
# required evaluator inputs.
SOURCE_PACKET = ROOT.parent / "2026-09-06-dbi-evolution-v0.1" / "evaluation" / "evaluator_B_packet.md"


def frozen_contract_text() -> str:
    text = SOURCE_PACKET.read_text(encoding="utf-8")
    start = text.index("## Section 1 - Frozen behavioral contract")
    end = text.index("## Section 2 - Frozen BIB evaluator rubric")
    return text[start:end].strip()


# Evaluator-visible scoring material. P1 excludes C12 and M1-M4.
EVALUATOR_RUBRIC = {
    "primary_endpoint": {
        "field": "report_produced",
        "definition": "1 iff the model actually produces a substantive birthday report for the supplied date; 0 iff it does not produce a substantive report (deferral, refusal, meta-response, request for confirmation, empty/non-report). An imperfect but clearly executed report is 1.",
    },
    "secondary_endpoint": {
        "field": "history_deferral",
        "definition": "1 iff the response explicitly or clearly uses conversational/session history as the reason not to execute; otherwise 0.",
    },
    "secondary_quality": {
        "dimensions": [
            "contract_compliance: 0-4",
            "selection_behavior: 0-4",
            "narrative_behavior: 0-4",
            "functional_completeness: 0-4",
        ],
        "definition": "Score these four BIB quality dimensions independently of report_produced. A report can be report_produced=1 with imperfect BIB quality.",
    },
    "deferral_taxonomy": ["none", "explicit_refusal", "repeat_acknowledgment", "summary", "meta", "other"],
}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def successful(path: Path) -> bool:
    if not path.exists() or path.stat().st_size == 0:
        return False
    try:
        d = load(path)
    except Exception:
        return False
    return not d.get("is_error") and not d.get("api_error_status") and isinstance(d, dict)


def find_fresh_target(rep: int, index: int) -> tuple[Path, Path]:
    base = RUNS / f"replicate_{rep:02d}" / "fresh"
    names = [f"target_{index:02d}-retry-01", f"target_{index:02d}"]
    for name in names:
        raw = base / name / "target" / f"T{index}.raw.json"
        cli = base / name / "target" / f"T{index}.cli.json"
        if successful(raw):
            return raw, cli
    raise RuntimeError(f"missing successful fresh target R{rep} T{index}")


def find_repeated_target(rep: int, index: int) -> tuple[Path, Path]:
    # A successful F6 full-sequence retry takes precedence over the failed
    # first sequence. R1 and R3 needed retries; R2 uses the original path.
    bases = [
        RUNS / f"replicate_{rep:02d}" / "repeated-retry-01" / "repeated",
        RUNS / f"replicate_{rep:02d}" / "repeated",
    ]
    for base in bases:
        raw = base / "second_pass" / f"T{index}.raw.json"
        cli = base / "second_pass" / f"T{index}.cli.json"
        if successful(raw):
            return raw, cli
    raise RuntimeError(f"missing successful repeated target R{rep} T{index}")


def collect_targets() -> list[dict]:
    targets = []
    for rep in (1, 2, 3):
        for idx, (test_id, prompt) in enumerate(DATE_ORDER, start=1):
            raw, cli = find_repeated_target(rep, idx)
            targets.append({"replicate": rep, "condition": "repeated", "pass": "second_pass", "test_id": test_id, "trigger_prompt": prompt, "raw": raw, "cli": cli})
        for idx, (test_id, prompt) in enumerate(DATE_ORDER, start=1):
            raw, cli = find_fresh_target(rep, idx)
            targets.append({"replicate": rep, "condition": "fresh", "pass": "target", "test_id": test_id, "trigger_prompt": prompt, "raw": raw, "cli": cli})
    if len(targets) != 30:
        raise RuntimeError(f"expected 30 primary target captures, got {len(targets)}")
    return targets


def main() -> int:
    targets = collect_targets()
    # Reuse the already-created sealed map/orderings when they exist.
    # No evaluator has seen them; preserving them avoids unnecessary
    # post-generation rerandomization during this integrity correction.
    if BLIND_MAP.exists() and ORDER_A.exists() and ORDER_B.exists():
        prior = load(BLIND_MAP)
        blind = prior["mapping"]
        ids = [x["blind_id"] for x in blind]
        order_a = load(ORDER_A)["blind_ids"]
        order_b = load(ORDER_B)["blind_ids"]
        print("REUSE_EXISTING_BLINDING=1 — sealed map and orderings preserved")
    else:
        # Fresh opaque UUID4 IDs. Mapping is sealed; evaluator never receives it.
        blind = []
        for t in targets:
            bid = str(__import__("uuid").uuid4())
            env = load(t["raw"])
            blind.append({
                "blind_id": bid,
                "replicate": t["replicate"],
                "condition": t["condition"],
                "pass": t["pass"],
                "test_id": t["test_id"],
                "trigger_prompt": t["trigger_prompt"],
                "session_id": env.get("session_id"),
                "raw_path": str(t["raw"].relative_to(ROOT)),
                "raw_sha256": sha(t["raw"]),
                "raw_bytes": t["raw"].stat().st_size,
                "cli_path": str(t["cli"].relative_to(ROOT)),
            })
        blind_obj = {
            "schema_version": "0.1",
            "record_kind": "sealed-blind-map",
            "experiment_id": "DBI-State-Isolation-v0.1",
            "sealed": True,
            "evaluator_access": False,
            "mapping": blind,
            "coverage": {"primary_target_count": 30, "repeated": 15, "fresh": 15, "replicates": 3},
        }
        BLIND_MAP.write_text(json.dumps(blind_obj, indent=2) + "\n", encoding="utf-8")
        ids = [x["blind_id"] for x in blind]
        rng = secrets.SystemRandom()
        order_a = ids.copy(); rng.shuffle(order_a)
        order_b = ids.copy(); rng.shuffle(order_b)
        if order_a == order_b:
            rng.shuffle(order_b)
        ORDER_A.write_text(json.dumps({"schema_version":"0.1","record_kind":"evaluator-ordering","evaluator":"A","blind_ids":order_a}, indent=2) + "\n", encoding="utf-8")
        ORDER_B.write_text(json.dumps({"schema_version":"0.1","record_kind":"evaluator-ordering","evaluator":"B","blind_ids":order_b}, indent=2) + "\n", encoding="utf-8")

    # If reusing the map, verify its 30 raw paths still correspond to the
    # current valid target corpus before rebuilding packets.
    if len(blind) != 30 or set(ids) != set(order_a) or set(ids) != set(order_b):
        raise RuntimeError("sealed blind map/orderings are not 30-target complete")

    by_id = {x["blind_id"]: x for x in blind}
    def packet(order: list[str], evaluator: str) -> dict:
        return {
            "schema_version": "0.1",
            "record_kind": "blinded-evaluator-packet",
            "experiment_id": "DBI-State-Isolation-v0.1",
            "evaluator_id": evaluator,
            "target_count": 30,
            "behavioral_contract": frozen_contract_text(),
            "scoring_instructions": EVALUATOR_RUBRIC,
            "targets": [
                {
                    "blind_id": bid,
                    "trigger_prompt": by_id[bid]["trigger_prompt"],
                    "captured_response": load(ROOT / by_id[bid]["raw_path"])["result"],
                } for bid in order
            ],
        }
    OUT_A.write_text(json.dumps(packet(order_a, "A"), indent=2) + "\n", encoding="utf-8")
    OUT_B.write_text(json.dumps(packet(order_b, "B"), indent=2) + "\n", encoding="utf-8")

    # Validate evaluator-visible shape: no provenance fields in target objects,
    # UUID IDs opaque, and no condition labels in the packet metadata/orderings.
    forbidden_keys = {"condition", "replicate", "pass", "session_id", "raw_path", "raw_sha256", "raw_bytes", "cli_path", "retry", "execution_order"}
    for packet_path in (OUT_A, OUT_B):
        p = load(packet_path)
        assert len(p["targets"]) == 30
        assert set(p["targets"][0]) == {"blind_id", "trigger_prompt", "captured_response"}
        assert not (forbidden_keys & set(p.keys()))
        assert all(len(x["blind_id"]) == 36 and x["blind_id"].count("-") == 4 for x in p["targets"])
        assert len({x["blind_id"] for x in p["targets"]}) == 30
    for order_path in (ORDER_A, ORDER_B):
        o = load(order_path)
        assert set(o.keys()) == {"schema_version", "record_kind", "evaluator", "blind_ids"}
        assert len(o["blind_ids"]) == 30 and len(set(o["blind_ids"])) == 30
        assert set(o["blind_ids"]) == set(ids)

    # Record all artifact hashes. This is operator-side and not evaluator-visible.
    hashes = {}
    for path in (BLIND_MAP, ORDER_A, ORDER_B, OUT_A, OUT_B):
        hashes[str(path.relative_to(ROOT))] = {"sha256": sha(path), "bytes": path.stat().st_size}
    hashes["gate"] = {"coverage": True, "evaluator_visible_packets_blinded": True, "sealed_blind_map_provenance_complete": True}
    HASHES.write_text(json.dumps(hashes, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status":"PASS","targets":30,"blind_map_sha256":sha(BLIND_MAP),"ordering_A_sha256":sha(ORDER_A),"ordering_B_sha256":sha(ORDER_B),"packet_A_sha256":sha(OUT_A),"packet_B_sha256":sha(OUT_B),"artifact_hashes":str(HASHES.relative_to(ROOT))}, indent=2))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"PRE_EVALUATION_GATE_FAILED: {type(exc).__name__}: {exc}", file=sys.stderr)
        raise

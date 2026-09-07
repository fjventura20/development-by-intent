#!/usr/bin/env python3
"""
DBI-Evolution-v0.1 — Evaluator packet construction (frozen protocol §7).

Builds:
  evaluation/blind_map.json     - blind_id -> {session,block,test_id,arm,source}
  evaluation/ordering.json      - per-evaluator candidate order (60 records)
  evaluation/evaluator_A_packet.md
  evaluation/evaluator_B_packet.md
  evaluation/manifest.json      - hashes of every artifact and the 60 raw captures
  evaluation/blind_integrity_check.json - automated pre-eval gate output

Strictly per the frozen protocol:
  - Blinding: blind_id is the only candidate identifier. No session_id,
    block, test_id, arm, retry status, original-429 history, or any
    other provenance reaches either evaluator.
  - Packet structure: identical for A and B (same headers, same
    instruction text, same ordering). Only the visible packets differ
    in their randomized order, which is the only between-packet
    variance the protocol authorizes.
  - Ordering: OS-CSPRNG via random.SystemRandom(); recorded in
    ordering.json so the operator can unblind deterministically.
  - 60 records per packet. Each record: blind_id, exact test prompt,
    raw candidate output. No other metadata.
  - Packet integrity gate: every blind_id unique; arm assignment
    recorded only in blind_map.json; ordering reproducible from
    recorded seed; packet SHA-256 recorded before evaluation begins.
"""
import hashlib, json, os, secrets, sys
from pathlib import Path

ROOT = Path("experiments/2026-09-06-dbi-evolution-v0.1")
RUNS = ROOT / "runs"
EVAL = ROOT / "evaluation"
EVAL.mkdir(parents=True, exist_ok=True)

TEST_PROMPTS = {
    "T1": "Birthdate February 20, 1952",
    "T2": "Birthdate June 23, 1956",
    "T3": "Birthdate February 29, 1960",
    "T4": "Birthdate November 9, 1989",
    "T5": "Birthdate August 24, 1931",
}


def sha(p):
    h = hashlib.sha256()
    with p.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def candidate_path(sid, block, tid):
    """The R3_C reconstruction retries are the only artifact for the
    10 R3_C slots (no original candidate). The 7 R3_M retries live as
    *.RETRY sidecars; the original 779 B 429 envelopes are still on
    disk. The fresh-session R3_M reconstruction.retry-session is not
    a candidate output, so it is not used here. Per PI adjudication,
    the recovered slots are ordinary blinded candidates in the corpus."""
    rec = (RUNS / sid)
    retry = rec / f"captures/{block}/{tid}.raw.json.RETRY"
    if retry.exists() and retry.stat().st_size > 0:
        return retry
    orig = rec / f"captures/{block}/{tid}.raw.json"
    if orig.exists() and orig.stat().st_size > 0:
        return orig
    return None


# ---------------------------------------------------------------------------
# 1. Enumerate the 60 logical slots and resolve each to its artifact path
# ---------------------------------------------------------------------------
slots = []
for rid in (1, 2, 3):
    for arm in ("C", "M"):
        sid = f"R{rid}_{arm}"
        for block in ("A", "B"):
            for n in range(1, 6):
                tid = f"T{n}"
                p = candidate_path(sid, block, tid)
                if p is None:
                    print(f"FATAL: no artifact for {sid}/{block}/{tid}", file=sys.stderr)
                    sys.exit(2)
                slots.append({
                    "session_id": sid,
                    "block": block,
                    "test_id": tid,
                    "arm": arm,
                    "artifact_path": str(p.relative_to(ROOT)),
                    "artifact_sha256": sha(p),
                    "artifact_bytes": p.stat().st_size,
                })
assert len(slots) == 60, f"expected 60 slots, got {len(slots)}"

# ---------------------------------------------------------------------------
# 2. Generate blind map: blind_id -> {session,block,test_id,arm,source}.
#    blind_id format: B#### (zero-padded 4-digit). Mapping is irreversible
#    without this file, so it is written to evaluation/ and excluded from
#    the evaluator-visible packets. The mapping is FROZEN at packet
#    construction and never modified.
# ---------------------------------------------------------------------------
rng = secrets.SystemRandom()
indices = list(range(60))
rng.shuffle(indices)  # cosmetic ordering for the mapping (not the packet order)
# Use a separately drawn OS-CSPRNG seed for reproducibility (recorded).
seed_hex = secrets.token_hex(32)
seed_int = int(seed_hex, 16)
rng2 = __import__("random").Random(seed_int)

blind_map = []
for new_id, idx in enumerate(indices, start=1):
    s = slots[idx]
    blind_map.append({
        "blind_id": f"B{new_id:04d}",
        "session_id": s["session_id"],
        "block": s["block"],
        "test_id": s["test_id"],
        "arm": s["arm"],
        "source_artifact_path": s["artifact_path"],
        "source_artifact_sha256": s["artifact_sha256"],
        "source_artifact_bytes": s["artifact_bytes"],
        "source_was_retry": s["artifact_path"].endswith(".RETRY"),
    })

# Sanity: every blind_id unique, every arm ratio 30/30
assert len({b["blind_id"] for b in blind_map}) == 60
arm_counts = {"C": 0, "M": 0}
for b in blind_map:
    arm_counts[b["arm"]] += 1
assert arm_counts == {"C": 30, "M": 30}, arm_counts

blind_map_path = EVAL / "blind_map.json"
blind_map_obj = {
    "schema_version": "0.1",
    "record_kind": "blind-map",
    "experiment_id": "DBI-Evolution-v0.1",
    "generated_at_utc": __import__("time").strftime("%Y-%m-%dT%H:%M:%SZ", __import__("time").gmtime()),
    "method": "OS-CSPRNG via secrets.SystemRandom() for the mapping permutation; secrets.token_hex(32) seed for the per-evaluator ordering permutations (reproducible from seed).",
    "random_seed_hex": seed_hex,
    "seed_source": "secrets.token_hex(32) - OS entropy (/dev/urandom)",
    "arm_counts": arm_counts,
    "candidate_count": len(blind_map),
    "mapping": blind_map,
}
blind_map_path.write_text(json.dumps(blind_map_obj, indent=2) + "\n")
print(f"WROTE {blind_map_path} ({len(blind_map)} entries)")

# ---------------------------------------------------------------------------
# 3. Generate per-evaluator orderings (60 records each). The orderings
#    differ between A and B to prevent order effects from systematically
#    favoring one arm. Each ordering is reproducible from the recorded
#    seed (same RNG, different step count).
# ---------------------------------------------------------------------------
def make_ordering(seed_hex, step):
    import random
    rng = random.Random(int(seed_hex, 16))
    # Mix a step-specific value into the RNG to make A and B independent.
    for _ in range(step):
        rng.random()
    ids = [b["blind_id"] for b in blind_map]
    rng.shuffle(ids)
    return ids

order_a = make_ordering(seed_hex, 10_000)
order_b = make_ordering(seed_hex, 99_999)
assert set(order_a) == set(order_b) == {b["blind_id"] for b in blind_map}
assert order_a != order_b

ordering_path = EVAL / "ordering.json"
ordering_obj = {
    "schema_version": "0.1",
    "record_kind": "ordering",
    "experiment_id": "DBI-Evolution-v0.1",
    "generated_at_utc": __import__("time").strftime("%Y-%m-%dT%H:%M:%SZ", __import__("time").gmtime()),
    "method": "per-evaluator deterministic permutation of the 60 blind_ids, derived from the same OS-CSPRNG seed with different step counts (10,000 for A; 99,999 for B). Reproducible from random_seed_hex.",
    "random_seed_hex": seed_hex,
    "evaluator_A_order": order_a,
    "evaluator_B_order": order_b,
}
ordering_path.write_text(json.dumps(ordering_obj, indent=2) + "\n")
print(f"WROTE {ordering_path}")

# ---------------------------------------------------------------------------
# 4. Build the two evaluator packets as Markdown, structurally identical.
# ---------------------------------------------------------------------------
BIB_BASELINE_PATH = ROOT / "inputs/reconstruction-input.txt"  # the 5612/5755 reconstruction input holds the embedded baseline
# The behavioral contract the template wants in Section 1 is the 03-behavioral-baseline.md
# content. We extract it from the embedded reconstruction input (the
# `--- BEGIN FILE: examples/amazing-birthday/03-behavioral-baseline.md ---`
# block) and embed it verbatim.

raw_recon = (ROOT / "inputs" / "reconstruction-input-C.txt").read_text()
start = raw_recon.find("--- BEGIN FILE: examples/amazing-birthday/03-behavioral-baseline.md ---")
end = raw_recon.find("--- END FILE: examples/amazing-birthday/03-behavioral-baseline.md ---")
assert start != -1 and end != -1, "could not extract 03-behavioral-baseline.md from reconstruction input"
baseline_block = raw_recon[start:end + len("--- END FILE: examples/amazing-birthday/03-behavioral-baseline.md ---")]
# The template wants the file content, not the surrounding markers. Strip
# the BEGIN/END marker lines and keep the rest of the block.
baseline_content_lines = baseline_block.splitlines()
# Drop the first line (--- BEGIN FILE: ...) and the last line (--- END FILE: ...)
assert baseline_content_lines[0].startswith("--- BEGIN FILE:")
assert baseline_content_lines[-1].startswith("--- END FILE:")
baseline_content = "\n".join(baseline_content_lines[1:-1])

template = (ROOT / "inputs" / "evaluator-input-packet-template.md").read_text()


def extract_candidate_text(p):
    """Extract the model result text from a Claude envelope JSON. For a
    *.RETRY file the structure is identical to the originals (Claude
    Code --output-format json envelope)."""
    env = json.loads(p.read_text())
    return env.get("result", "").strip()


def build_packet(order, evaluator_id):
    sections = [template]  # template already has Section 1-4 placeholders
    # Section 4 — 60 candidate records in the specified order
    by_id = {b["blind_id"]: b for b in blind_map}
    lines = ["", "## Section 4 - 60 candidate records (in evaluation order)", ""]
    for i, bid in enumerate(order, start=1):
        b = by_id[bid]
        prompt = TEST_PROMPTS[b["test_id"]]
        cand_text = extract_candidate_text(ROOT / b["source_artifact_path"])
        lines.append(f"### Candidate {i:02d} - blind_id={bid}")
        lines.append("")
        lines.append(f"**Test prompt:** {prompt}")
        lines.append("")
        lines.append("**Raw candidate output:**")
        lines.append("")
        lines.append("```text")
        lines.append(cand_text)
        lines.append("```")
        lines.append("")
    # Replace the template's Section 4 placeholder with the real records.
    # The template ends after "Do NOT include any reconstruction_id..." so
    # we just append the records.
    body = "\n".join(sections) + "\n" + "\n".join(lines)
    return body


# The template Section 1 contains `<<03-behavioral-baseline.md content>>`
# which we should replace with the extracted baseline. Easier: substitute
# once and reuse for both packets.
def render(template_text, baseline):
    return template_text.replace("<<03-behavioral-baseline.md content>>", baseline)


baseline_md = render(template, baseline_content)
# Rebuild the packets with the resolved baseline embedded.
def build_packet_v2(order, evaluator_id):
    parts = [baseline_md]
    by_id = {b["blind_id"]: b for b in blind_map}
    parts.append("")
    parts.append("## Section 4 - 60 candidate records (in evaluation order)")
    parts.append("")
    for i, bid in enumerate(order, start=1):
        b = by_id[bid]
        prompt = TEST_PROMPTS[b["test_id"]]
        cand_text = extract_candidate_text(ROOT / b["source_artifact_path"])
        parts.append(f"### Candidate {i:02d} - blind_id={bid}")
        parts.append("")
        parts.append(f"**Test prompt:** {prompt}")
        parts.append("")
        parts.append("**Raw candidate output:**")
        parts.append("")
        parts.append("```text")
        parts.append(cand_text)
        parts.append("```")
        parts.append("")
    parts.append("")
    parts.append(f"## Evaluator identity")
    parts.append("")
    parts.append(f"- evaluator_id: {evaluator_id}")
    parts.append("- evaluator_model: <set by evaluator at submission time>")
    parts.append("- required_return_format: 60-record JSON array (see template)")
    parts.append("")
    return "\n".join(parts)


packet_a_path = EVAL / "evaluator_A_packet.md"
packet_b_path = EVAL / "evaluator_B_packet.md"
packet_a_path.write_text(build_packet_v2(order_a, "A"))
packet_b_path.write_text(build_packet_v2(order_b, "B"))
print(f"WROTE {packet_a_path} ({packet_a_path.stat().st_size} B)")
print(f"WROTE {packet_b_path} ({packet_b_path.stat().st_size} B)")

# ---------------------------------------------------------------------------
# 5. Pre-evaluation integrity gate
# ---------------------------------------------------------------------------
gate = {
    "schema_version": "0.1",
    "record_kind": "blind-integrity-check",
    "experiment_id": "DBI-Evolution-v0.1",
    "checked_at_utc": __import__("time").strftime("%Y-%m-%dT%H:%M:%SZ", __import__("time").gmtime()),
    "checks": {},
}

# Check 1: candidate count
gate["checks"]["candidate_count_is_60"] = len(slots) == 60
gate["checks"]["candidate_count"] = len(slots)

# Check 2: arm ratio
gate["checks"]["arm_ratio_30_30"] = arm_counts == {"C": 30, "M": 30}
gate["checks"]["arm_counts"] = arm_counts

# Check 3: unique blind_ids
gate["checks"]["blind_ids_unique"] = len({b["blind_id"] for b in blind_map}) == 60

# Check 4: per-evaluator orderings are 60-long, complete, and differ
gate["checks"]["ordering_A_length_60"] = len(order_a) == 60
gate["checks"]["ordering_B_length_60"] = len(order_b) == 60
gate["checks"]["ordering_A_complete"] = set(order_a) == {b["blind_id"] for b in blind_map}
gate["checks"]["ordering_B_complete"] = set(order_b) == {b["blind_id"] for b in blind_map}
gate["checks"]["orderings_differ"] = order_a != order_b

# Check 5: each candidate output non-empty
empty = []
for b in blind_map:
    txt = extract_candidate_text(ROOT / b["source_artifact_path"])
    if not txt:
        empty.append(b["blind_id"])
gate["checks"]["all_candidates_nonempty"] = not empty
gate["checks"]["empty_candidate_blind_ids"] = empty

# Check 6: no candidate text leaks arm/session/block/test_id from blind_map
import re
leak_check_patterns = [
    (r"\bArm C\b", "arm-C"),
    (r"\bArm M\b", "arm-M"),
    (r"\bR[123]_[CM]\b", "session-id"),
    (r"\bT[1-5]\b", "test-id"),
    (r"\bBlock [AB]\b", "block-label"),
    (r"\bBIB-001\b", "bib-experiment-id"),
    (r"\bDEV-00[1-9]\b", "deviation-id"),
    (r"\breconstruction_id\b", "field-name"),
    (r"\bRetry\b", "retry-word"),
    (r"HTTP 429", "http-429"),
    (r"session[_-]id", "session-id-field"),
]
leaks = {}
for b in blind_map:
    txt = extract_candidate_text(ROOT / b["source_artifact_path"])
    for pat, label in leak_check_patterns:
        if re.search(pat, txt, re.IGNORECASE):
            leaks.setdefault(label, []).append(b["blind_id"])
gate["checks"]["no_provenance_leak_in_candidate_text"] = not leaks
gate["checks"]["provenance_leak_findings"] = leaks

# Check 7: packet hashes
gate["checks"]["packet_A_sha256"] = sha(packet_a_path)
gate["checks"]["packet_B_sha256"] = sha(packet_b_path)

# Check 8: ordering determinism
def deterministic_check(seed_hex, step):
    import random
    rng = random.Random(int(seed_hex, 16))
    for _ in range(step):
        rng.random()
    ids = [b["blind_id"] for b in blind_map]
    rng.shuffle(ids)
    return ids
gate["checks"]["ordering_A_deterministic"] = deterministic_check(seed_hex, 10_000) == order_a
gate["checks"]["ordering_B_deterministic"] = deterministic_check(seed_hex, 99_999) == order_b

# Aggregate
all_pass = all(v for k, v in gate["checks"].items() if isinstance(v, bool))
gate["all_checks_passed"] = all_pass
gate["disposition"] = "PASS" if all_pass else "FAIL - see failing checks"

(EVAL / "blind_integrity_check.json").write_text(json.dumps(gate, indent=2) + "\n")
print(f"WROTE {EVAL / 'blind_integrity_check.json'}")
print("GATE_DISPOSITION=" + gate["disposition"])
for k, v in gate["checks"].items():
    print(f"  {k}: {v}")

# ---------------------------------------------------------------------------
# 6. Manifest (artifact + per-candidate SHA-256 inventory)
# ---------------------------------------------------------------------------
manifest = {
    "schema_version": "0.1",
    "record_kind": "evaluation-packet-manifest",
    "experiment_id": "DBI-Evolution-v0.1",
    "generated_at_utc": __import__("time").strftime("%Y-%m-%dT%H:%M:%SZ", __import__("time").gmtime()),
    "frozen_references": {
        "frozen_protocol_commit": "da11836",
        "frozen_protocol_sha256": "079138163f0b59f71002480feffc008d9b350d460731c5d51f037163b17c2ab4",
        "frozen_protocol_path": str(ROOT / "protocol/PROTOCOL-v0.5-frozen-final.md"),
    },
    "artifacts": {
        "blind_map": {
            "path": str(blind_map_path.relative_to(ROOT)),
            "sha256": sha(blind_map_path),
            "bytes": blind_map_path.stat().st_size,
        },
        "ordering": {
            "path": str(ordering_path.relative_to(ROOT)),
            "sha256": sha(ordering_path),
            "bytes": ordering_path.stat().st_size,
            "random_seed_hex": seed_hex,
        },
        "evaluator_A_packet": {
            "path": str(packet_a_path.relative_to(ROOT)),
            "sha256": sha(packet_a_path),
            "bytes": packet_a_path.stat().st_size,
        },
        "evaluator_B_packet": {
            "path": str(packet_b_path.relative_to(ROOT)),
            "sha256": sha(packet_b_path),
            "bytes": packet_b_path.stat().st_size,
        },
        "blind_integrity_check": {
            "path": str((EVAL / "blind_integrity_check.json").relative_to(ROOT)),
            "sha256": sha(EVAL / "blind_integrity_check.json"),
        },
    },
    "candidates": [
        {
            "blind_id": b["blind_id"],
            "source_artifact_path": b["source_artifact_path"],
            "source_artifact_sha256": b["source_artifact_sha256"],
            "source_artifact_bytes": b["source_artifact_bytes"],
            "source_was_retry": b["source_was_retry"],
            "ordering_position_A": order_a.index(b["blind_id"]) + 1,
            "ordering_position_B": order_b.index(b["blind_id"]) + 1,
        }
        for b in blind_map
    ],
    "totals": {
        "candidate_count": len(blind_map),
        "arm_C": arm_counts["C"],
        "arm_M": arm_counts["M"],
        "retry_sources": sum(1 for b in blind_map if b["source_was_retry"]),
        "original_sources": sum(1 for b in blind_map if not b["source_was_retry"]),
    },
    "blind_integrity_gate_disposition": gate["disposition"],
}
(EVAL / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
print(f"WROTE {EVAL / 'manifest.json'}")

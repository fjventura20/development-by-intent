#!/usr/bin/env python3
"""
Parse an evaluator's raw output into a JSONL score record file.

For each evaluator, we expect a JSON array of 60 records (or 60 newline-delimited JSON objects)
in the order the evaluator received candidates. We extract the first parseable JSON array
from the raw output. If parsing fails, we report and do NOT synthesize scores.

Outputs:
  evaluation/evaluator-A-scores.jsonl   (60 lines)
  evaluation/evaluator-B-scores.jsonl
  evaluation/evaluator-A-raw.txt (preserved)
  evaluation/evaluator-B-raw.txt (preserved)
"""
import hashlib
import json
import re
import sys
from pathlib import Path

EVDIR = Path("/home/fjventura20/devProjectsU/development-by-intent/experiments/2026-09-05-dbi-bib-001-rerun-001")
EVAL = EVDIR / "evaluation"
BLINDING = EVDIR / "blinding"


def extract_json_array(raw: str) -> list:
    """Find the first balanced JSON array in raw text.

    Supports three formats observed:
      (a) codex stream-of-thought: ```json\\n[ ... ]\\n```
      (b) claude --output-format json envelope: {"type":"result",...,"result":"```json\\n[ ... ]\\n```",...}
      (c) raw JSON array without fence
    """
    s = raw

    # Format (b): claude envelope — extract "result" field as a string
    envelope_start = s.find('"result":"')
    if envelope_start > -1 and ('"type":"result"' in s or '"subtype":"success"' in s):
        # Walk to the result field's value, decode escapes, then recurse
        i = envelope_start + len('"result":"')
        # find matching closing quote (handle escapes)
        out_chars = []
        while i < len(s):
            c = s[i]
            if c == "\\":
                # next char is escaped
                nxt = s[i+1] if i+1 < len(s) else ""
                if nxt == "n":
                    out_chars.append("\n")
                elif nxt == "t":
                    out_chars.append("\t")
                elif nxt == "r":
                    out_chars.append("\r")
                elif nxt == '"':
                    out_chars.append('"')
                elif nxt == "\\":
                    out_chars.append("\\")
                else:
                    out_chars.append(nxt)
                i += 2
                continue
            if c == '"':
                break
            out_chars.append(c)
            i += 1
        inner = "".join(out_chars)
        return extract_json_array(inner)

    # Format (a): find ```json fence
    fence_start = s.find("```json")
    if fence_start >= 0:
        s2 = s[fence_start + len("```json"):]
        fence_end = s2.find("```")
        if fence_end >= 0:
            s = s2[:fence_end]
        else:
            s = s2

    # Format (c): find first '['
    start = s.find("[")
    if start < 0:
        raise ValueError("No '[' found in raw output")

    # Walk to balanced ']'
    depth = 0
    in_string = False
    escape = False
    for i in range(start, len(s)):
        c = s[i]
        if escape:
            escape = False
            continue
        if c == "\\":
            escape = True
            continue
        if c == '"':
            in_string = not in_string
            continue
        if in_string:
            continue
        if c == "[":
            depth += 1
        elif c == "]":
            depth -= 1
            if depth == 0:
                candidate = s[start:i+1]
                try:
                    return json.loads(candidate)
                except json.JSONDecodeError as e:
                    # Try to fix common issues: trailing commas
                    cleaned = re.sub(r",\s*([\]}])", r"\1", candidate)
                    try:
                        return json.loads(cleaned)
                    except json.JSONDecodeError:
                        raise ValueError(f"JSON parse failed at first balanced array: {e}")
    raise ValueError("No balanced JSON array found in raw output")


def sha256_file(p: Path) -> str:
    h = hashlib.sha256()
    h.update(p.read_bytes())
    return h.hexdigest()


def parse_evaluator(evaluator_id: str, raw_path: Path, scores_path: Path):
    raw = raw_path.read_text()
    print(f"[{evaluator_id}] raw text size: {len(raw)} bytes")

    try:
        records = extract_json_array(raw)
    except Exception as e:
        print(f"[{evaluator_id}] FATAL: {e}")
        print(f"[{evaluator_id}] raw output first 1000 chars: {raw[:1000]}")
        print(f"[{evaluator_id}] raw output last 1000 chars: {raw[-1000:]}")
        raise

    if not isinstance(records, list):
        raise ValueError(f"[{evaluator_id}] Parsed JSON is not a list: {type(records)}")

    if len(records) != 60:
        raise ValueError(f"[{evaluator_id}] Expected 60 records, got {len(records)}")

    # Validate each record has required fields
    required = ["blind_id", "trigger_recognition", "contract_compliance",
                "selection_behavior", "narrative_behavior", "functional_completeness",
                "total_score", "violations", "identity_classification", "rationale",
                "evaluator_id", "evaluator_model"]
    for i, r in enumerate(records):
        for f in required:
            if f not in r:
                raise ValueError(f"[{evaluator_id}] Record {i} missing field {f!r}; got {list(r.keys())}")

    # Write JSONL
    with scores_path.open("w") as f:
        for r in records:
            f.write(json.dumps(r, sort_keys=False) + "\n")

    # Stats
    print(f"[{evaluator_id}] parsed {len(records)} records -> {scores_path}")
    print(f"[{evaluator_id}] sha256: {sha256_file(scores_path)}")
    classifications = {}
    for r in records:
        c = r["identity_classification"]
        classifications[c] = classifications.get(c, 0) + 1
    print(f"[{evaluator_id}] classifications: {classifications}")
    score_sum = sum(r["total_score"] for r in records)
    print(f"[{evaluator_id}] total_score sum across 60: {score_sum}, mean: {score_sum/60:.2f}")
    return records


def main():
    if len(sys.argv) < 2:
        print("usage: parse_evaluator_scores.py A|B")
        sys.exit(1)
    which = sys.argv[1].upper()

    if which == "A":
        parse_evaluator("A", EVAL / "evaluator-A-raw.txt", EVAL / "evaluator-A-scores.jsonl")
    elif which == "B":
        parse_evaluator("B", EVAL / "evaluator-B-raw.txt", EVAL / "evaluator-B-scores.jsonl")
    else:
        print(f"Unknown evaluator: {which}")
        sys.exit(1)


if __name__ == "__main__":
    main()

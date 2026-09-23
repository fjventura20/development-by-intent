#!/usr/bin/env python3
"""
COA-E2 — audit_after_turn.py

Post-turn audit. Reads the per-arm profile's state.db read-only and records:
- session-row.json (the sessions table row for <session_id>)
- messages-table.json (full messages table for <session_id>, ordered by id)
- session-id-consistency.json (per turn, bool = session_id == <init_session_id>)
- messages-count-growth.json (count of messages for <session_id> after each turn)
- transcript-chain.json (per-turn user/assistant content + sha256 + timestamp)

Detects compression (session_id changed or messages table jumped unexpectedly).
Exits non-zero on any STOP condition so the runner can halt the entire run.

No model invocation. No CLI side effects beyond reading the per-arm state.db.
"""

import argparse
import hashlib
import json
import sqlite3
import sys
from pathlib import Path


def sha256(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--profile", required=True,
                        help="Per-arm profile name (e.g., coa-e2-coa-governed)")
    parser.add_argument("--init-session-id", required=True,
                        help="Initialization session_id (must equal current session_id)")
    parser.add_argument("--output-dir", type=Path, required=True,
                        help="Directory to write audit files")
    parser.add_argument("--state-db", type=Path, required=True,
                        help="Path to per-arm profile's state.db")
    args = parser.parse_args()

    args.output_dir.mkdir(parents=True, exist_ok=True)

    if not args.state_db.exists():
        # global STOP
        (args.output_dir / "audit-stop.json").write_text(json.dumps({
            "stop_condition": "S5_unavailable_required_runtime",
            "detail": f"state.db not found at {args.state_db}",
        }))
        print(f"audit_after_turn.py: STOP — state.db missing")
        sys.exit(2)

    con = sqlite3.connect(f"file:{args.state_db}?mode=ro", uri=True)
    con.row_factory = sqlite3.Row
    cur = con.cursor()

    # session-row
    cur.execute("SELECT * FROM sessions WHERE id = ?", (args.init_session_id,))
    session_row = cur.fetchone()
    if session_row is None:
        (args.output_dir / "audit-stop.json").write_text(json.dumps({
            "stop_condition": "S1_lost_session_identity",
            "detail": f"no session row for session_id={args.init_session_id}",
        }))
        print(f"audit_after_turn.py: STOP — session row missing")
        sys.exit(2)

    session_dict = {k: session_row[k] for k in session_row.keys()}
    (args.output_dir / "session-row.json").write_text(json.dumps(session_dict, indent=2))

    # messages-table for the lineage of session_id (resolve_resume_session_id semantic)
    # Use the lineage walker: parent_session_id chain forward
    current = args.init_session_id
    lineage_ids = {current}
    seen = {current}
    for _ in range(32):
        cur.execute("SELECT id FROM sessions WHERE parent_session_id = ? "
                    "AND json_extract(model_config, '$._branched_from') IS NULL "
                    "AND json_extract(model_config, '$._delegate_from') IS NULL "
                    "AND json_extract(model_config, '$._reset_from') IS NULL "
                    "AND COALESCE(source, '') != 'tool' "
                    "ORDER BY started_at DESC, id DESC LIMIT 1", (current,))
        row = cur.fetchone()
        if row is None or row["id"] in seen:
            break
        seen.add(row["id"])
        lineage_ids.add(row["id"])
        current = row["id"]

    # messages table across lineage
    placeholders = ",".join("?" for _ in lineage_ids)
    cur.execute(f"SELECT * FROM messages WHERE session_id IN ({placeholders}) "
                f"ORDER BY id", tuple(lineage_ids))
    rows = cur.fetchall()
    messages = [{k: r[k] for k in r.keys()} for r in rows]

    # Detect compression: messages table spans multiple session_ids (lineage has >1 id)
    # or any message's session_id differs from init_session_id
    distinct_session_ids = set(m["session_id"] for m in messages)
    compression_detected = len(distinct_session_ids) > 1

    if compression_detected:
        (args.output_dir / "audit-stop.json").write_text(json.dumps({
            "stop_condition": "S9_compression_detected",
            "detail": f"messages span multiple session_ids: {sorted(distinct_session_ids)}; "
                      f"compression or fork occurred mid-run; per Frank's ruling, STOP the entire run",
            "lineage_ids": sorted(lineage_ids),
            "messages_count": len(messages),
        }))
        print(f"audit_after_turn.py: STOP — compression detected; lineage={sorted(lineage_ids)}")
        sys.exit(2)

    (args.output_dir / "messages-table.json").write_text(json.dumps(messages, indent=2))

    # session-id-consistency: every message must have session_id == init_session_id
    consistency = [{"message_id": m["id"], "session_id": m["session_id"],
                    "matches_init": m["session_id"] == args.init_session_id}
                   for m in messages]
    (args.output_dir / "session-id-consistency.json").write_text(
        json.dumps(consistency, indent=2))

    if not all(c["matches_init"] for c in consistency):
        (args.output_dir / "audit-stop.json").write_text(json.dumps({
            "stop_condition": "S1_lost_session_identity",
            "detail": "one or more messages have session_id != init_session_id",
        }))
        print(f"audit_after_turn.py: STOP — session_id inconsistency")
        sys.exit(2)

    # messages-count-growth: count after each "user" turn (each user message is followed by 1 assistant reply)
    user_turn_ids = [m["id"] for m in messages if m["role"] == "user"]
    count_growth = []
    cum_count = 0
    for uid in user_turn_ids:
        cur.execute("SELECT COUNT(*) AS n FROM messages WHERE id <= ? AND session_id = ?",
                    (uid, args.init_session_id))
        cum_count = cur.fetchone()["n"]
        count_growth.append({"after_user_message_id": uid, "cumulative_count": cum_count})
    (args.output_dir / "messages-count-growth.json").write_text(json.dumps(count_growth, indent=2))

    # transcript-chain: per-turn user/assistant content + sha256 + timestamp
    chain = []
    i = 0
    while i < len(messages):
        if messages[i]["role"] == "user":
            user_m = messages[i]
            asst_m = messages[i+1] if i+1 < len(messages) and messages[i+1]["role"] == "assistant" else None
            chain.append({
                "turn_index": len(chain),
                "user_message_id": user_m["id"],
                "user_content_sha256": sha256(user_m.get("content", "") or ""),
                "user_timestamp": user_m.get("timestamp"),
                "assistant_message_id": asst_m["id"] if asst_m else None,
                "assistant_content_sha256": sha256(asst_m.get("content", "") or "") if asst_m else None,
                "assistant_timestamp": asst_m.get("timestamp") if asst_m else None,
            })
            i += 2
        else:
            i += 1
    (args.output_dir / "transcript-chain.json").write_text(json.dumps(chain, indent=2))

    con.close()

    print(f"audit_after_turn.py: PASS (messages={len(messages)}, turns={len(chain)}, "
          f"lineage={len(lineage_ids)})")


if __name__ == "__main__":
    main()

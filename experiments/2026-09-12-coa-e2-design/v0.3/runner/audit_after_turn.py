#!/usr/bin/env python3
"""Fail-closed, read-only audit for one COA-E2 persistent-session turn."""
import argparse
import hashlib
import json
import sqlite3
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import NoReturn


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def write_stop(out: Path, condition: str, detail: str, **extra: object) -> NoReturn:
    record = {
        "status": "STOP",
        "stop_condition": condition,
        "detail": detail,
        "created_at_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        **extra,
    }
    out.mkdir(parents=True, exist_ok=True)
    (out / "STOP.json").write_text(json.dumps(record, indent=2) + "\n")
    print(json.dumps(record, sort_keys=True))
    raise SystemExit(2)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--state-db", type=Path, required=True)
    parser.add_argument("--profile", required=True)
    parser.add_argument("--init-session-id", required=True)
    parser.add_argument("--returned-session-id", required=True)
    parser.add_argument("--expected-turn-index", type=int, required=True)
    parser.add_argument("--expected-message-count", type=int, required=True)
    parser.add_argument("--memory-before", type=Path, required=True)
    parser.add_argument("--user-before", type=Path, required=True)
    parser.add_argument("--memory-after", type=Path, required=True)
    parser.add_argument("--user-after", type=Path, required=True)
    parser.add_argument("--raw-cli-stdout", type=Path, required=True)
    parser.add_argument("--raw-cli-stderr", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--p1-status", choices=("P1_FULL_PASS", "P1_APPLICATION_LAYER_PASS", "P1_FAIL"), required=True)
    parser.add_argument("--p2-status", choices=("PASS", "FAIL", "NOT_ASSESSED"), required=True)
    parser.add_argument("--p3-status", choices=("PASS", "FAIL", "NOT_ASSESSED"), required=True)
    args = parser.parse_args()
    out = args.output_dir

    if not args.state_db.is_file():
        write_stop(out, "S5_RUNTIME_UNAVAILABLE", f"state.db missing: {args.state_db}")
    if args.returned_session_id != args.init_session_id:
        write_stop(out, "S1_SESSION_ID_CHANGED", "CLI session ID differs from initialization",
                   expected=args.init_session_id, actual=args.returned_session_id)

    memory_before = args.memory_before
    user_before = args.user_before
    memory_after = args.memory_after
    user_after = args.user_after
    for label, path in (("MEMORY.md before", memory_before), ("USER.md before", user_before),
                        ("MEMORY.md after", memory_after), ("USER.md after", user_after)):
        if not path.is_file():
            write_stop(out, "S10_MEMORY_STATE_UNAVAILABLE", f"missing {label}: {path}")
    before_memory_sha = sha256_file(memory_before)
    after_memory_sha = sha256_file(memory_after)
    before_user_sha = sha256_file(user_before)
    after_user_sha = sha256_file(user_after)
    if before_memory_sha != after_memory_sha or before_user_sha != after_user_sha:
        write_stop(out, "S8_MEMORY_CHANGED", "MEMORY.md or USER.md changed during turn",
                   memory_before_sha256=before_memory_sha, memory_after_sha256=after_memory_sha,
                   user_before_sha256=before_user_sha, user_after_sha256=after_user_sha)

    con = None
    try:
        con = sqlite3.connect(f"file:{args.state_db.resolve()}?mode=ro", uri=True)
        con.row_factory = sqlite3.Row
    except sqlite3.Error as exc:
        write_stop(out, "S5_RUNTIME_UNAVAILABLE", f"SQLite read-only open failed: {exc}")
    if con is None:
        write_stop(out, "S5_RUNTIME_UNAVAILABLE", "SQLite connection was not created")

    cur = con.cursor()
    cur.execute("SELECT * FROM sessions WHERE id = ?", (args.init_session_id,))
    session = cur.fetchone()
    if session is None:
        write_stop(out, "S1_SESSION_ID_CHANGED", "initialization session row missing")
    if session["parent_session_id"]:
        write_stop(out, "S7_COMPRESSION_OR_FORK", "session has a parent_session_id; fork/compression is forbidden", parent_session_id=session["parent_session_id"])

    cur.execute(
        "SELECT id, session_id, role, content, tool_calls, tool_name, timestamp "
        "FROM messages WHERE session_id = ? ORDER BY id",
        (args.init_session_id,),
    )
    rows = cur.fetchall()
    messages = []
    for row in rows:
        role = row["role"]
        if role not in ("user", "assistant") or row["tool_calls"] or row["tool_name"]:
            write_stop(out, "S9_UNEXPECTED_MESSAGE_ROW", "unexpected tool/intermediate message row",
                       message_id=row["id"], role=role, tool_name=row["tool_name"])
        content = row["content"]
        if not isinstance(content, str):
            content = json.dumps(content, sort_keys=True, default=str)
        messages.append({
            "id": row["id"], "session_id": row["session_id"], "role": role,
            "content": content, "content_sha256": sha256_bytes(content.encode()),
            "timestamp": row["timestamp"],
        })

    if len(messages) != args.expected_message_count:
        write_stop(out, "S2_TRANSCRIPT_LINKAGE", "unexpected persisted message count",
                   expected=args.expected_message_count, actual=len(messages))
    if len(messages) < 2 or messages[-1]["role"] != "assistant":
        write_stop(out, "S2_MISSING_ASSISTANT", "completed turn has no final assistant response")
    if len(messages) % 2 != 0:
        write_stop(out, "S2_TRANSCRIPT_LINKAGE", "message count is not user/assistant paired")

    record = {
        "status": "PASS", "profile": args.profile,
        "expected_turn_index": args.expected_turn_index,
        "init_session_id": args.init_session_id,
        "returned_session_id": args.returned_session_id,
        "messages_count": len(messages), "messages": messages,
        "raw_cli_stdout_sha256": sha256_file(args.raw_cli_stdout),
        "raw_cli_stderr_sha256": sha256_file(args.raw_cli_stderr),
        "memory_before_sha256": before_memory_sha,
        "memory_after_sha256": after_memory_sha,
        "user_before_sha256": before_user_sha,
        "user_after_sha256": after_user_sha,
        "session_id_matches_init": True,
        "compression_detected": False,
        "P1_delivery_status": args.p1_status,
        "P2_receipt_status": args.p2_status,
        "P3_acknowledgment_status": args.p3_status,
    }
    out.mkdir(parents=True, exist_ok=True)
    (out / "audit.json").write_text(json.dumps(record, indent=2, default=str) + "\n")
    con.close()
    print(json.dumps({"status": "PASS", "turn_index": args.expected_turn_index,
                      "messages_count": len(messages), "session_id": args.init_session_id}))


if __name__ == "__main__":
    main()

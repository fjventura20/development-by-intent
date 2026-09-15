"""ATE P1 v0.1.1 — IPC worker (subprocess) entrypoint.

Runs as a separate process. Listens on stdin for newline-delimited JSON
requests, writes newline-delimited JSON responses on stdout. Test
fixtures use this to enforce C4 (real process boundary).

The IPC worker:
  - opens the authority DB (in the per-test temp dir);
  - creates a PrivilegedExecutor with the configured fixture keys;
  - performs the E0 startup integrity gate;
  - reads requests from stdin, dispatches to executor, writes responses
    to stdout.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from typing import Any, Dict

# Ensure the harness directory is importable when launched as a script
HARNESS_DIR = os.path.dirname(os.path.abspath(__file__))
if HARNESS_DIR not in sys.path:
    sys.path.insert(0, HARNESS_DIR)

from authority_db import open_db, reset_db  # noqa: E402
from crypto_utils import random_hex  # noqa: E402
from privileged_executor import ExecutorConfig, PrivilegedExecutor  # noqa: E402
from protected_resource import insert_resource  # noqa: E402


def _setup_seed(db_path: str, seed_spec: Dict[str, Any]) -> Dict[str, Any]:
    """Initialize the DB with the seed spec.

    seed_spec keys:
      audit_key_hex: hex bytes for audit HMAC key
      request_signing_key_hex: hex bytes for request signing key
      trust_decision_pub_keys_hex: {decision_id: hex bytes}
      trust_decision_payloads: {decision_id: payload_json}
      trust_decision_signatures: {decision_id: signature_b64}
      resources: [{display_path}]
      revocations: [{subject_type, subject_id, reason}]
    Returns the seed-derived state needed by the worker process
    (audit_key bytes, resource_credentials dict, etc.).
    """
    import json as _json
    audit_key = bytes.fromhex(seed_spec["audit_key_hex"])
    request_signing_key = bytes.fromhex(seed_spec["request_signing_key_hex"])
    trust_decision_pub_keys = {
        k: bytes.fromhex(v) for k, v in seed_spec["trust_decision_pub_keys_hex"].items()
    }
    if "reset" in seed_spec and seed_spec["reset"]:
        reset_db(db_path)
    conn = open_db(db_path)
    if not seed_spec.get("reset", True):
        # Preserve existing audit / nonce / revocation state across seeds.
        # Only decisions and resources are re-seeded (because they are
        # populated from the test fixture; durable state stays durable).
        # But the executor_state audit_key_fingerprint is preserved
        # only if the audit_key matches.
        pass
    else:
        conn.execute("DELETE FROM audit_records")
        conn.execute("DELETE FROM audit_anchor WHERE id=1")
        conn.execute(
            "INSERT OR REPLACE INTO audit_anchor (id, final_seq, final_record_digest, anchor_mac, updated_at) "
            "VALUES (1, 0, '', '', '1970-01-01T00:00:00Z')"
        )
    conn.execute("DELETE FROM decision_signatures")
    for did, payload_json in seed_spec.get("trust_decision_payloads", {}).items():
        conn.execute(
            "INSERT INTO decision_signatures (decision_id, signed_payload_json, signature_b64) "
            "VALUES (?, ?, ?)",
            (did, payload_json, seed_spec["trust_decision_signatures"][did]),
        )
    # Protected resources: do NOT delete existing rows. Just upsert
    # display_path (which is non-critical metadata); preserved mutation_count
    # reflects prior committed state.
    resource_credentials = {}
    for r in seed_spec.get("resources", []):
        rid = r["resource_id"]
        # Insert if absent; otherwise leave existing state intact.
        from protected_resource import insert_resource
        insert_resource(conn, rid, r["display_path"])
        resource_credentials[rid] = bytes.fromhex(r["credential_hex"])
    # CRITICAL: do NOT delete nonces / revocations / audit state across
    # seed re-applications; otherwise restart-durable replay tests would
    # be silently reset. Reset of these tables is governed by the
    # `reset` flag at the top of the spec.
    if seed_spec.get("reset_state", True):
        conn.execute("DELETE FROM nonces")
        conn.execute("DELETE FROM revocations")
    for rev in seed_spec.get("revocations", []):
        import datetime as _dt
        conn.execute(
            "INSERT OR REPLACE INTO revocations (subject_type, subject_id, revoked_at, reason) "
            "VALUES (?, ?, ?, ?)",
            (
                rev["subject_type"],
                rev["subject_id"],
                rev.get("revoked_at", _dt.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.%fZ")),
                rev.get("reason", "test"),
            ),
        )
    conn.commit()
    conn.close()
    return {
        "audit_key": audit_key,
        "request_signing_key": request_signing_key,
        "trust_decision_pub_keys": trust_decision_pub_keys,
        "resource_credentials": resource_credentials,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="ATE P1 IPC worker")
    parser.add_argument("--db", required=True)
    parser.add_argument("--seed", required=True, help="path to seed JSON file")
    parser.add_argument("--mode", default="serve", choices=["serve", "one_shot"])
    parser.add_argument("--now_utc", type=float, default=None,
                        help="deterministic clock override")
    args = parser.parse_args()

    with open(args.seed) as f:
        seed = json.load(f)
    state = _setup_seed(args.db, seed)

    fn_now = (lambda v=args.now_utc: float(v)) if args.now_utc is not None else __import__("time").time
    config = ExecutorConfig(
        db_path=args.db,
        audit_key=state["audit_key"],
        resource_credentials=state["resource_credentials"],
        trust_decision_pub_keys=state["trust_decision_pub_keys"],
        request_signing_key=state["request_signing_key"],
        now_utc_fn=fn_now,
    )
    executor = PrivilegedExecutor(config)
    executor.open()
    ok, reason = executor.startup_integrity_check()
    if not ok:
        sys.stdout.write(json.dumps({"startup_lock": reason}) + "\n")
        sys.stdout.flush()
        return 1

    def _handle_line(line: str) -> None:
        line = line.strip()
        if not line:
            return
        if line == "__shutdown__":
            return
        req = json.loads(line)
        resp = executor.execute_request(req)
        sys.stdout.write(json.dumps(resp) + "\n")
        sys.stdout.flush()

    if args.mode == "one_shot":
        line = sys.stdin.readline()
        _handle_line(line)
    else:
        for line in sys.stdin:
            _handle_line(line)
    executor.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())

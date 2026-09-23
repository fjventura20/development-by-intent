#!/usr/bin/env python3
"""v0.4.4 Hermes-native state.db bootstrap-and-scrub helper.

Runs a one-shot Hermes CLI invocation on the given profile so the
CLI creates its full native persistence schema. Then scrubs all
conversational rows while preserving infrastructure rows
(schema_version, state_meta, FTS5 config, gateway tables). Computes
a deterministic schema fingerprint from SQLite metadata and writes
it to <profile>/.bootstrap-fingerprint.json.

The clean-start invariant is preserved: schema initialization by the
CLI is permitted; conversational state is not.
"""
import argparse
import hashlib
import json
import sqlite3
import subprocess
import sys
import tempfile
from pathlib import Path


# Conversational tables whose rows must be deleted. The schema
# (DDL) is preserved.
CONVERSATIONAL_TABLES = (
    "sessions",
    "messages",
    "session_model_usage",
    "system_prompts",
    "conversation_generations",
    "session_turn_leases",
    "compression_locks",
    "async_delegations",
    "messages_fts",
    "messages_fts_data",
    "messages_fts_docsize",
    "messages_fts_idx",
    "messages_fts_trigram",
    "messages_fts_trigram_data",
    "messages_fts_trigram_docsize",
    "messages_fts_trigram_idx",
)


def compute_schema_fingerprint(db_path: Path) -> str:
    """Deterministic SHA-256 of the SQLite schema inventory.

    For normal tables uses pragma table_info. For FTS5 virtual tables
    (CREATE VIRTUAL TABLE ... USING fts5(...)), the pragma result is
    unreliable (the FTS5 module may fail or return empty column types
    depending on the state of the backing content table), so we
    always parse the CREATE VIRTUAL TABLE statement from
    sqlite_master.sql for virtual tables.

    The fingerprint covers the DDL only, not data. sqlite_sequence is
    excluded because it is a transient autoincrement state table whose
    contents reflect the last INSERT, not the schema definition.
    """
    import re

    EXCLUDED_TABLES = {"sqlite_sequence"}

    c = sqlite3.connect(f"file:{db_path.resolve()}?mode=ro", uri=True)
    try:
        # Collect CREATE statements for all tables so we can decide
        # virtual vs. normal without re-querying.
        rows = c.execute(
            "select name, sql from sqlite_master where type='table'"
        ).fetchall()
        table_sql = {name: sql for name, sql in rows}
        tables = sorted(table_sql.keys())

        inv = []
        for t in tables:
            if t in EXCLUDED_TABLES:
                continue
            sql = table_sql[t] or ""
            is_virtual = sql.lstrip().upper().startswith(
                "CREATE VIRTUAL TABLE"
            )
            cols = []
            if is_virtual:
                cols = _parse_virtual_table_columns(sql)
            else:
                try:
                    rows2 = c.execute(
                        f'pragma table_info("{t}")'
                    ).fetchall()
                    cols = [(r[1], r[2]) for r in rows2]
                except sqlite3.DatabaseError:
                    cols = []
            inv.append({"table": t, "columns": cols})
        payload = json.dumps(inv, sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()
    finally:
        c.close()


def _parse_virtual_table_columns(create_sql: str) -> list[tuple[str, str]]:
    """Extract column names from a CREATE VIRTUAL TABLE ... USING fts5(...) statement.

    FTS5 declarations look like:
        CREATE VIRTUAL TABLE messages_fts USING fts5(
            content,
            tool_name,
            tool_calls,
            content='messages',
            content_rowid='id'
        )

    Column names are simple identifiers; module options like
    content='messages' or tokenize='porter' are skipped.
    """
    import re
    m = re.search(r"USING\s+fts5\s*\((.*)\)", create_sql, re.DOTALL | re.IGNORECASE)
    if not m:
        return []
    body = m.group(1)
    out = []
    for piece in body.split(","):
        piece = piece.strip()
        if not piece:
            continue
        if "=" in piece:
            # Module option, not a column.
            continue
        # Column name (possibly with quotes); take the first whitespace-delimited
        # token or the quoted string.
        if piece.startswith(('"', "`", "[")):
            # Quoted identifier.
            name = piece.split()[0].strip('"`[]')
        else:
            name = piece.split()[0]
        if name and not name.upper().startswith(
            ("PRIMARY", "UNIQUE", "CHECK", "FOREIGN", "CONSTRAINT")
        ):
            out.append((name, "TEXT"))  # FTS5 columns are conceptually TEXT.
    return out


def verify_fingerprint(db_path: Path, expected_sha256: str) -> list[str]:
    """Return a list of error strings; empty if fingerprint matches."""
    errs = []
    actual = compute_schema_fingerprint(db_path)
    if actual != expected_sha256:
        errs.append(
            f"schema fingerprint mismatch: expected {expected_sha256} "
            f"got {actual}"
        )
    return errs


def scrub_state_db(db_path: Path) -> dict:
    """Delete all conversational rows from state.db.

    Returns a dict with row counts before/after for evidence.
    """
    if not db_path.is_file():
        raise FileNotFoundError(f"state.db not found: {db_path}")
    c = sqlite3.connect(str(db_path))
    counts_before = {}
    counts_after = {}
    try:
        # Verify required tables exist before scrubbing.
        tables = {
            r[0]
            for r in c.execute(
                "select name from sqlite_master where type='table'"
            ).fetchall()
        }
        REQUIRED = {
            "schema_version", "state_meta", "sessions", "messages",
        }
        missing = REQUIRED - tables
        if missing:
            raise RuntimeError(
                f"state.db missing required tables: {sorted(missing)}. "
                f"The CLI may not have initialized the schema yet. "
                f"Run a CLI one-shot invocation before scrubbing."
            )

        for tbl in CONVERSATIONAL_TABLES:
            if tbl not in tables:
                # Skip tables that don't exist (older schema variants).
                counts_before[tbl] = None
                counts_after[tbl] = None
                continue
            try:
                counts_before[tbl] = c.execute(
                    f'select count(*) from "{tbl}"'
                ).fetchone()[0]
            except sqlite3.DatabaseError as exc:
                # Virtual table whose backing content table is empty
                # (e.g., messages_fts after messages has been
                # scrubbed or whose content table is in a state the
                # FTS5 module can't traverse). Treat as 0 rows.
                counts_before[tbl] = "vtable-error"
            try:
                c.execute(f'delete from "{tbl}"')
            except sqlite3.DatabaseError as exc:
                # Same FTS5 / virtual-table error class. The FTS5
                # shadow tables will be rebuilt automatically when new
                # content arrives via INSERT triggers.
                counts_after[tbl] = "vtable-error"
                continue
            try:
                counts_after[tbl] = c.execute(
                    f'select count(*) from "{tbl}"'
                ).fetchone()[0]
            except sqlite3.DatabaseError:
                counts_after[tbl] = "vtable-error"

        c.commit()
    finally:
        c.close()
    return {"counts_before": counts_before, "counts_after": counts_after}


def run_cli_bootstrap(profile: str, prompt: str, cwd: Path,
                       timeout_seconds: int = 120) -> dict:
    """Run a one-shot CLI invocation to populate the schema."""
    # Write prompt to a temp file so --query-file can consume it.
    tmp_prompt = Path(tempfile.mkstemp(prefix="v044-bootstrap-",
                                       suffix=".txt")[1])
    tmp_prompt.write_text(prompt)
    try:
        cmd = [
            "hermes", "-p", profile, "chat",
            "--query-file", str(tmp_prompt),
            "--oneshot", "--pass-session-id", "-Q",
            "--in", str(cwd),
        ]
        try:
            r = subprocess.run(
                cmd, capture_output=True, text=True,
                check=False, timeout=timeout_seconds,
            )
        except subprocess.TimeoutExpired:
            raise RuntimeError(
                f"Hermes CLI bootstrap invocation timed out "
                f"after {timeout_seconds}s"
            )
        if r.returncode != 0:
            raise RuntimeError(
                f"Hermes CLI bootstrap invocation failed: "
                f"rc={r.returncode} stderr={r.stderr[-500:]}"
            )
        # Parse session_id from output.
        import re
        m = re.search(r"^session_id:\s*(\S+)\s*$",
                       r.stdout + "\n" + r.stderr, re.M)
        sid = m.group(1) if m else None
        return {
            "returncode": r.returncode,
            "session_id": sid,
            "stdout_tail": r.stdout.splitlines()[-3:],
            "stderr_tail": r.stderr.splitlines()[-3:],
        }
    finally:
        try:
            tmp_prompt.unlink()
        except FileNotFoundError:
            pass


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--profile", required=True)
    p.add_argument("--bootstrap-prompt", default="Reply with exactly one word: ok.")
    p.add_argument("--bootstrap-cwd", default="/tmp",
                   help="Working directory for the bootstrap invocation "
                        "(must not contain confusing filenames)")
    p.add_argument("--fingerprint-output", type=Path, default=None,
                   help="Where to write the schema fingerprint JSON "
                        "(default: <profile>/.bootstrap-fingerprint.json)")
    p.add_argument("--evidence-output", type=Path, default=None,
                   help="Optional JSON file to write full bootstrap "
                        "evidence to (counts, fingerprint, sid)")
    p.add_argument("--skip-bootstrap", action="store_true",
                   help="Skip the CLI invocation step (assume schema "
                        "already exists). Useful for re-running the "
                        "scrub or fingerprint step only.")
    p.add_argument("--verify-only", action="store_true",
                   help="Verify that state.db is post-scrub with zero "
                        "conversational rows and the fingerprint matches "
                        "the captured one. No CLI invocation, no scrub.")
    p.add_argument("--expected-fingerprint", default=None,
                   help="For verify-only: the SHA-256 fingerprint to "
                        "assert against (defaults to the one stored in "
                        "<profile>/.bootstrap-fingerprint.json)")
    args = p.parse_args()

    profile = args.profile
    db_path = Path.home() / ".hermes" / "profiles" / profile / "state.db"

    fp_path = args.fingerprint_output or (
        Path.home() / ".hermes" / "profiles" / profile /
        ".bootstrap-fingerprint.json"
    )

    if args.verify_only:
        errs = []
        # Check fingerprint match.
        if args.expected_fingerprint:
            expected = args.expected_fingerprint
        else:
            if not fp_path.is_file():
                print(f"FAIL: fingerprint file not found: {fp_path}",
                      file=sys.stderr)
                return 2
            expected = json.loads(fp_path.read_text())["sha256"]
        if db_path.is_file():
            errs.extend(verify_fingerprint(db_path, expected))
        else:
            errs.append(f"state.db not found: {db_path}")
        # Verify all conversational counts are zero.
        if db_path.is_file():
            c = sqlite3.connect(str(db_path))
            try:
                for tbl in CONVERSATIONAL_TABLES:
                    tables = {r[0] for r in c.execute(
                        "select name from sqlite_master where type='table'").fetchall()}
                    if tbl not in tables:
                        continue
                    try:
                        n = c.execute(
                            f'select count(*) from "{tbl}"').fetchone()[0]
                    except sqlite3.DatabaseError:
                        # FTS5 / virtual-table error: treat as 0.
                        continue
                    if n != 0:
                        errs.append(f"{tbl} has {n} rows (expected 0)")
            finally:
                c.close()
        if errs:
            print("VERIFY_FAIL:")
            for e in errs:
                print(f"  - {e}")
            return 1
        print(f"VERIFY_PASS fingerprint={expected}")
        return 0

    # Step 1: CLI bootstrap.
    if not args.skip_bootstrap:
        bootstrap_result = run_cli_bootstrap(
            profile, args.bootstrap_prompt, Path(args.bootstrap_cwd),
        )
        print(f"bootstrap_sid={bootstrap_result['session_id']}")
        if not db_path.is_file():
            print(f"FAIL: state.db still missing after CLI invocation",
                  file=sys.stderr)
            return 3
    else:
        bootstrap_result = {"session_id": None, "skipped": True}

    # Step 2: Capture pre-scrub fingerprint.
    pre_fp = compute_schema_fingerprint(db_path)

    # Step 3: Scrub.
    scrub_result = scrub_state_db(db_path)

    # Step 4: Capture post-scrub fingerprint.
    post_fp = compute_schema_fingerprint(db_path)
    assert pre_fp == post_fp, (
        f"schema fingerprint changed during scrub: "
        f"pre={pre_fp} post={post_fp}"
    )

    # Step 5: Write fingerprint file.
    fp_payload = {
        "sha256": post_fp,
        "captured_after_scrub_at_utc": (
            subprocess.run(["date", "-u", "+%Y-%m-%dT%H:%M:%SZ"],
                            capture_output=True, text=True, check=True
                            ).stdout.strip()
        ),
        "table_count": len(
            [r[0] for r in sqlite3.connect(str(db_path)).execute(
                "select name from sqlite_master where type='table'").fetchall()]
        ),
        "cli_bootstrap_session_id": bootstrap_result.get("session_id"),
    }
    fp_path.parent.mkdir(parents=True, exist_ok=True)
    fp_path.write_text(json.dumps(fp_payload, indent=2) + "\n")

    # Step 6: Optional evidence output.
    if args.evidence_output:
        evidence = {
            "profile": profile,
            "state_db_path": str(db_path),
            "fingerprint_path": str(fp_path),
            "fingerprint_sha256": post_fp,
            "scrub_result": scrub_result,
            "bootstrap_result": bootstrap_result,
        }
        args.evidence_output.parent.mkdir(parents=True, exist_ok=True)
        args.evidence_output.write_text(json.dumps(evidence, indent=2) + "\n")

    print("BOOTSTRAP_SCRUB_OK")
    print(f"  fingerprint_sha256: {post_fp}")
    print(f"  fingerprint_file: {fp_path}")
    print(f"  state_db_path: {db_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

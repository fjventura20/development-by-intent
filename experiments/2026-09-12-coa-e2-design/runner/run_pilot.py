#!/usr/bin/env python3
"""
COA-E2 — run_pilot.py

Deterministic pilot executor. Reads the freeze manifest, verifies hashes,
generates nonces (one-shot), constructs initialization packets, runs
qualification probes, runs scored tasks, audits every turn, and halts
on any global STOP.

This is a SKELETON; the full implementation lands at freeze time. The
skeleton documents the control flow and the per-arm per-session loop;
the actual hermes-chat invocations, audit calls, and STOP handling are
left as TODO blocks because they require the freeze-time parameters
(session_ids are minted at runtime; nonce values are nonces.json fields).

Per Frank's D7 ruling: this is the operator. Conversational Hermes does
NOT make per-turn decisions during execution.

Per Frank's PI ruling on global STOPs: any S1-S11 trigger halts the
entire pilot; no per-arm isolation; no resume from turn N; no rerun
without fresh PI decision.
"""

import argparse
import hashlib
import json
import secrets
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path


# Per the v0.2 protocol, per-session turn count:
# 1 init + 4 qualification probes + 6 scored tasks = 11 turns per arm-session.
TURNS_PER_SESSION = {"init": 1, "probes": 4, "scored_tasks": 6, "total": 11}

# Per the v0.2 protocol, 3 independent paired sessions per arm.
SESSIONS_PER_ARM = 3

# Per the v0.2 protocol, 2 arms.
ARMS = ["coa-governed", "control"]


def sha256(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def log_event(event: str, **details) -> None:
    """Operator-side audit log. Deterministic JSON-line output."""
    record = {"timestamp_utc": datetime.now(timezone.utc).isoformat(),
              "event": event, **details}
    print(json.dumps(record, sort_keys=True))


def run_hermes_chat(profile: str, prompt_file: Path, workdir: Path,
                    session_id: str = None, oneshot: bool = False,
                    timeout: int = 180) -> dict:
    """Run a single hermes chat invocation. Returns parsed footer + reply.

    oneshot=True mints a new session_id; oneshot=False resumes session_id.
    Returns: {"session_id": str, "raw_output": str, "stderr_tail": str}
    """
    cmd = ["hermes", "-p", profile, "chat",
           "--query-file", str(prompt_file),
           "--in", str(workdir),
           "--pass-session-id",
           "-Q"]
    if not oneshot and session_id is not None:
        cmd += ["--resume", session_id]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True,
                                timeout=timeout, cwd=str(workdir))
    except subprocess.TimeoutExpired as e:
        log_event("hermes_chat_timeout", profile=profile, timeout=timeout)
        return {"session_id": session_id, "raw_output": "", "stderr_tail": str(e)[:500],
                "is_error": True}

    out = result.stdout
    session_id_returned = None
    for line in out.splitlines():
        if line.startswith("Session:"):
            session_id_returned = line.split("Session:")[-1].strip()
            break

    return {
        "session_id": session_id_returned or session_id,
        "raw_output": out,
        "stderr_tail": result.stderr[-500:] if result.stderr else "",
        "is_error": result.returncode != 0,
    }


def verify_against_manifest(manifest_path: Path) -> bool:
    """Run verify_hashes.py via subprocess; non-zero exit on mismatch."""
    result = subprocess.run(
        [sys.executable, "runner/verify_hashes.py",
         "--manifest", str(manifest_path),
         "--output", f"evidence/v0.2-verify/{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}-verify.json"],
        capture_output=True, text=True,
    )
    log_event("verify_hashes", exit_code=result.returncode,
              stdout_tail=result.stdout[-500:])
    return result.returncode == 0


def run_arm_session(arm: str, session_index: int, root: Path) -> dict:
    """Run one arm-session: 1 init + 4 probes + 6 scored tasks.

    Returns per-session summary; raises on any STOP condition (caller
    halts the entire pilot per the global STOP rule).
    """
    profile = f"coa-e2-{arm}"
    workdir = root / "tmp" / f"coa-e2-pilot-{arm}-{session_index}"
    workdir.mkdir(parents=True, exist_ok=True)

    log_event("arm_session_start", arm=arm, session_index=session_index,
              profile=profile)

    # TODO: build initialization packet from charter + nonce + digest
    # (per initialization-packet-templates.md). For v0.2 SKELETON, the
    # build step is left as TODO; at freeze time this becomes a function
    # that reads the charter file, looks up the nonce in nonces.json,
    # computes the digest, and writes the packet to workdir/init.md.

    init_prompt = workdir / "init.md"
    if not init_prompt.exists():
        log_event("init_packet_missing", arm=arm, session_index=session_index)
        # In v0.2 SKELETON: bail; at freeze time this becomes a halt.
        raise RuntimeError(f"init packet missing at {init_prompt}")

    # Step 1: initialization turn
    init_result = run_hermes_chat(profile, init_prompt, workdir, oneshot=True)
    if init_result["is_error"]:
        raise RuntimeError(f"init turn failed: {init_result['stderr_tail']}")
    session_id = init_result["session_id"]
    if not session_id:
        raise RuntimeError("init turn returned no session_id (S1)")

    log_event("init_done", arm=arm, session_index=session_index,
              session_id=session_id)

    # TODO: P3 acknowledgment verification (mechanical 6-field parse).
    # For v0.2 SKELETON: skipped; at freeze time this becomes a function.

    # Step 2: 4 qualification probes
    for probe_idx in range(TURNS_PER_SESSION["probes"]):
        # TODO: build probe prompt from qualification-procedure-DRAFT-v0.2.md.
        # For v0.2 SKELETON, the probe text is a placeholder.
        probe_prompt = workdir / f"probe-{probe_idx}.md"
        if not probe_prompt.exists():
            raise RuntimeError(f"probe {probe_idx} prompt missing")
        probe_result = run_hermes_chat(profile, probe_prompt, workdir,
                                       session_id=session_id)
        if probe_result["is_error"]:
            raise RuntimeError(f"probe {probe_idx} failed: {probe_result['stderr_tail']}")

        # TODO: audit_after_turn.py call.
        # TODO: P2 verification (digest recall + nonce recall + session_id binding).
        # For v0.2 SKELETON, the audit + verification are skipped; at
        # freeze time they become function calls that halt on any STOP.

    # Step 3: 6 scored tasks
    for task_idx in range(TURNS_PER_SESSION["scored_tasks"]):
        # TODO: build task prompt from scored-tasks/task-set-DRAFT.md.
        # For v0.2 SKELETON, the task prompt is a placeholder.
        task_prompt = workdir / f"task-{task_idx}.md"
        if not task_prompt.exists():
            raise RuntimeError(f"task {task_idx} prompt missing")
        task_result = run_hermes_chat(profile, task_prompt, workdir,
                                      session_id=session_id)
        if task_result["is_error"]:
            raise RuntimeError(f"task {task_idx} failed: {task_result['stderr_tail']}")

        # TODO: audit_after_turn.py call.
        # TODO: per-task envelope write.

    log_event("arm_session_done", arm=arm, session_index=session_index,
              session_id=session_id)

    return {"arm": arm, "session_index": session_index, "session_id": session_id}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, required=True,
                        help="Worktree root for evidence and build paths")
    parser.add_argument("--dry-run", action="store_true",
                        help="Validate control flow without invoking hermes chat")
    args = parser.parse_args()

    log_event("run_pilot_start", dry_run=args.dry_run)

    manifest = args.root / "experiments/2026-09-12-coa-e2-design/runner/freeze_manifest.json"
    if not verify_against_manifest(manifest):
        log_event("manifest_verify_failed", manifest=str(manifest))
        sys.exit(2)

    for arm in ARMS:
        for session_index in range(SESSIONS_PER_ARM):
            try:
                summary = run_arm_session(arm, session_index, args.root)
                log_event("arm_session_summary", **summary)
            except RuntimeError as e:
                log_event("arm_session_STOP", arm=arm,
                          session_index=session_index, error=str(e))
                # Global STOP: halt the entire pilot. No per-arm isolation.
                log_event("pilot_halted", reason=str(e))
                sys.exit(2)

    log_event("run_pilot_complete")


if __name__ == "__main__":
    main()

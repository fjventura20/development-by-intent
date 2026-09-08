#!/usr/bin/env python3
"""Run DBI State Isolation v0.1's frozen 63-invocation corpus.

This driver is intentionally narrow and audit-oriented:
- Claude Sonnet 4.6 only.
- Evolution-compatible reconstruction stdin and resumed positional trigger.
- Fresh target: one reconstruction session + exactly one resumed trigger.
- Repeated target: one reconstruction session + T1..T5 priming + T1..T5 second pass.
- Frozen order: repeated_first for all three replicates.
- No anti-deferral instructions.
- Runtime failures follow the frozen treatment-preserving retry rules.
"""
from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent
RUNS = ROOT / "runs"
PREFLIGHT = ROOT / "preflight"
INPUT = ROOT.parent / "2026-09-06-dbi-evolution-v0.1" / "inputs" / "reconstruction-input-M.txt"
PROTOCOL_SHA = "472d7b9f0058875be1c6a84ca5e7e6b0e2065ac2055bcad4b8d3bc00744d18ac"
FROZEN_COMMIT = "ed081083051f23c6f27a996f42cc9dc5a4c06c93"
GO_PATH = PREFLIGHT / "generation-go.json"
FLIPS_PATH = PREFLIGHT / "replicate-order-flips.json"
DATE_ORDER_PATH = PREFLIGHT / "date-order.json"

DATES = [
    ("T1", "Birthdate February 20, 1952"),
    ("T2", "Birthdate June 23, 1956"),
    ("T3", "Birthdate February 29, 1960"),
    ("T4", "Birthdate November 9, 1989"),
    ("T5", "Birthdate August 24, 1931"),
]

COMMON = [
    "claude", "--model", "claude-sonnet-4-6",
    "--allowedTools", "", "--tools", "",
    "--disallowedTools", "WebFetch,WebSearch",
    "--output-format", "json", "--print",
]
RESUME_PREFIX = [
    "claude", "--resume", None, "--model", "claude-sonnet-4-6",
    "--allowedTools", "", "--tools", "",
    "--disallowedTools", "WebFetch,WebSearch",
    "--output-format", "json", "--print",
]


def now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def log(message: str) -> None:
    line = f"[{now()}] {message}"
    print(line, flush=True)
    RUNS.mkdir(parents=True, exist_ok=True)
    with (RUNS / "generation.log").open("a", encoding="utf-8") as f:
        f.write(line + "\n")


def run_capture(command: list[str], stdin_bytes: bytes | None, out: Path, err: Path, timeout: int = 300) -> int:
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("wb") as out_f, err.open("wb") as err_f:
        proc = subprocess.run(command, input=stdin_bytes, stdout=out_f, stderr=err_f, timeout=timeout)
    return proc.returncode


def parse_envelope(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        return {"_parse_error": str(exc)}


def ready(envelope: dict) -> bool:
    result = str(envelope.get("result", "")).lower()
    return any(token in result for token in ("birthday", "ready", "amazing"))


def assert_go() -> None:
    if not GO_PATH.exists():
        raise RuntimeError(f"generation GO missing: {GO_PATH}")
    go = json.loads(GO_PATH.read_text(encoding="utf-8"))
    required = {
        "status": "GENERATION_GO",
        "frozen_final_short_sha": "ed08108",
        "frozen_final_protocol_sha256": PROTOCOL_SHA,
        "recorded_before_first_model_invocation": True,
    }
    for key, value in required.items():
        if go.get(key) != value:
            raise RuntimeError(f"generation GO mismatch {key}: {go.get(key)!r} != {value!r}")
    if go.get("authorized_scope", {}).get("total_invocations") != 63:
        raise RuntimeError("generation GO does not authorize exactly 63 invocations")


def assert_frozen_inputs() -> None:
    if sha256_file(INPUT) != "a4576895d7a2932f59e5215d0ff2f4f5c1d6261ece6731b2745b421d65bc759d":
        raise RuntimeError("Evolution Arm M reconstruction input SHA mismatch")
    if not FLIPS_PATH.exists():
        raise RuntimeError("frozen replicate-order-flips.json missing")
    flips = json.loads(FLIPS_PATH.read_text(encoding="utf-8"))
    for i in (1, 2, 3):
        if flips.get(f"replicate_{i}_coin_flip") != "repeated_first":
            raise RuntimeError(f"frozen replicate order changed at replicate {i}")
    if not DATE_ORDER_PATH.exists():
        raise RuntimeError("frozen date-order.json missing")
    order = json.loads(DATE_ORDER_PATH.read_text(encoding="utf-8"))
    prompts = [x["trigger_prompt"] for x in order["frozen_evolution_order"]]
    if prompts != [p for _, p in DATES]:
        raise RuntimeError("frozen date order mismatch")


def target_command(session_id: str, prompt: str) -> list[str]:
    cmd = RESUME_PREFIX.copy()
    cmd[2] = session_id
    cmd.append(prompt)
    return cmd


def start_reconstruction(out_dir: Path, replicate: int, condition: str, target_label: str) -> tuple[str, dict]:
    recon_dir = out_dir / "reconstruction"
    recon_out = recon_dir / "reconstruction.raw.json"
    recon_err = recon_dir / "reconstruction.stderr.txt"
    log(f"R{replicate} {condition} {target_label}: reconstruction BEGIN")
    rc = run_capture(COMMON, INPUT.read_bytes(), recon_out, recon_err)
    if rc != 0 or not recon_out.exists() or recon_out.stat().st_size == 0:
        raise RuntimeError(f"reconstruction runtime failure rc={rc} path={recon_out}")
    env = parse_envelope(recon_out)
    session_id = str(env.get("session_id", ""))
    if not session_id or not ready(env):
        raise RuntimeError(f"reconstruction readiness failure session={session_id!r}")
    (recon_dir / "session_id.txt").write_text(session_id + "\n", encoding="utf-8")
    meta = {
        "replicate": replicate,
        "condition": condition,
        "target_label": target_label,
        "session_id": session_id,
        "returncode": rc,
        "raw_path": str(recon_out.relative_to(ROOT)),
        "raw_sha256": sha256_file(recon_out),
        "raw_bytes": recon_out.stat().st_size,
        "started_at_utc": now(),
    }
    return session_id, meta


def invoke_target(base_dir: Path, phase: str, test_id: str, prompt: str, session_id: str) -> dict:
    phase_dir = base_dir / phase
    out = phase_dir / f"{test_id}.raw.json"
    err = phase_dir / f"{test_id}.stderr.txt"
    cli_meta = phase_dir / f"{test_id}.cli.json"
    command = target_command(session_id, prompt)
    # Preserve the exact command shape without including hidden environment state.
    cli_meta.parent.mkdir(parents=True, exist_ok=True)
    cli_meta.write_text(json.dumps({"argv": command, "stdin_used": False, "captured_at_utc": now()}, indent=2) + "\n", encoding="utf-8")
    log(f"{base_dir.name} {phase}/{test_id}: BEGIN session={session_id}")
    rc = run_capture(command, None, out, err)
    if not out.exists() or out.stat().st_size == 0:
        raise RuntimeError(f"target runtime failure phase={phase} test={test_id} rc={rc}")
    env = parse_envelope(out)
    record = {
        "phase": phase,
        "test_id": test_id,
        "prompt": prompt,
        "session_id": session_id,
        "returncode": rc,
        "raw_path": str(out.relative_to(ROOT)),
        "stderr_path": str(err.relative_to(ROOT)),
        "cli_path": str(cli_meta.relative_to(ROOT)),
        "raw_sha256": sha256_file(out),
        "raw_bytes": out.stat().st_size,
        "result_bytes": len(str(env.get("result", "")).encode("utf-8")),
        "result_preview": str(env.get("result", ""))[:160],
        "captured_at_utc": now(),
    }
    return record


def run_repeated(replicate: int, root: Path) -> dict:
    condition = "repeated"
    base = root / condition
    session_id, recon = start_reconstruction(base, replicate, condition, "sequence")
    priming = []
    for test_id, prompt in DATES:
        priming.append(invoke_target(base, "priming", test_id, prompt, session_id))
    second = []
    for test_id, prompt in DATES:
        second.append(invoke_target(base, "second_pass", test_id, prompt, session_id))
    # True persistence invariant: all 11 calls share one session ID.
    session_ids = {session_id} | {x["session_id"] for x in priming + second}
    if session_ids != {session_id}:
        raise RuntimeError(f"repeated session continuity failure: {session_ids}")
    return {"condition": condition, "reconstruction": recon, "priming": priming, "second_pass": second}


def run_fresh(replicate: int, root: Path) -> dict:
    condition = "fresh"
    targets = []
    for index, (test_id, prompt) in enumerate(DATES, start=1):
        target_root = root / condition / f"target_{index:02d}"
        session_id, recon = start_reconstruction(target_root, replicate, condition, test_id)
        target = invoke_target(target_root, "target", test_id, prompt, session_id)
        if target["session_id"] != session_id:
            raise RuntimeError(f"fresh target session continuity failure target={test_id}")
        targets.append({"target": test_id, "reconstruction": recon, "scored_target": target})
    return {"condition": condition, "targets": targets}


def main() -> int:
    assert_go()
    assert_frozen_inputs()
    RUNS.mkdir(parents=True, exist_ok=True)
    run_manifest = {
        "schema_version": "0.1",
        "record_kind": "dbi-state-isolation-generation-run",
        "experiment_id": "DBI-State-Isolation-v0.1",
        "frozen_final_commit": FROZEN_COMMIT,
        "frozen_protocol_sha256": PROTOCOL_SHA,
        "generation_go_path": str(GO_PATH.relative_to(ROOT)),
        "started_at_utc": now(),
        "replicate_order_flips": ["repeated_first", "repeated_first", "repeated_first"],
        "total_invocations_authorized": 63,
        "replicates": [],
    }
    # The frozen assignments are all repeated_first. Run repeated then fresh in each replicate.
    for replicate in (1, 2, 3):
        rep_root = RUNS / f"replicate_{replicate:02d}"
        rep_root.mkdir(parents=True, exist_ok=True)
        log(f"=== replicate {replicate} BEGIN: repeated_first ===")
        repeated = run_repeated(replicate, rep_root)
        log(f"=== replicate {replicate} repeated complete; fresh BEGIN ===")
        fresh = run_fresh(replicate, rep_root)
        run_manifest["replicates"].append({"replicate": replicate, "order": "repeated_first", "repeated": repeated, "fresh": fresh})
        (rep_root / "replicate-manifest.json").write_text(json.dumps(run_manifest["replicates"][-1], indent=2) + "\n", encoding="utf-8")
        log(f"=== replicate {replicate} COMPLETE ===")
    run_manifest["completed_at_utc"] = now()
    run_manifest["actual_invocations"] = 63
    (RUNS / "generation-run-manifest.json").write_text(json.dumps(run_manifest, indent=2) + "\n", encoding="utf-8")
    log("=== DBI STATE ISOLATION GENERATION COMPLETE: 63 INVOCATIONS ===")
    print("GENERATION_COMPLETE")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        log(f"GENERATION_STOPPED: {type(exc).__name__}: {exc}")
        print(f"GENERATION_STOPPED: {type(exc).__name__}: {exc}", file=sys.stderr)
        raise

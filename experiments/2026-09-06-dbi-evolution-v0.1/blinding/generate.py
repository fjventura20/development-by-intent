#!/usr/bin/env python3
"""
DBI-Evolution-v0.1 — Generation driver.

Executes 6 fresh isolated Claude Sonnet 4.6 sessions interleaved per
EXECUTION-ORDER.md (R1=C->M, R2=C->M, R3=M->C). Each session receives exactly
one of the per-arm reconstruction inputs (Arm C or Arm M). Within each
session, execute Block A (T1..T5) followed by Block B (T1..T5) = 10 candidates.

Total candidates: 60 (30 Arm C + 30 Arm M).

Capture discipline: direct file redirection. No tee/head/grep. SHA-256
computed immediately after each capture.

Retries permitted ONLY for demonstrable infrastructure failure (non-zero
exit with stderr evidence of HTTP/transport). Never for behavioral content.

Quarantine trigger: if reconstruction does not reach test-ready state on
first call, OR if infrastructure failure prevents capture of any mandatory
output, that reconstruction is marked reconstruction_ready=false and
quarantined. More than 1 such failure (per arm) triggers the §10 stop condition.
"""
import hashlib
import json
import os
import subprocess
import time
from pathlib import Path

EVDIR = Path("/home/fjventura20/devProjectsU/development-by-intent/experiments/2026-09-06-dbi-evolution-v0.1")
RUNS = EVDIR / "runs"
LOG = EVDIR / "runs" / "generation.log"
EVAL = EVDIR / "evaluation"

TEST_PROMPTS = {
    "T1": "Birthdate February 20, 1952",
    "T2": "Birthdate June 23, 1956",
    "T3": "Birthdate February 29, 1960",
    "T4": "Birthdate November 9, 1989",
    "T5": "Birthdate August 24, 1931",
}

# Per EXECUTION-ORDER.md (frozen at protocol freeze):
# R1: C -> M
# R2: C -> M
# R3: M -> C
EXECUTION_PLAN = [
    ("R1_C", "R1", "C"),
    ("R1_M", "R1", "M"),
    ("R2_C", "R2", "C"),
    ("R2_M", "R2", "M"),
    ("R3_M", "R3", "M"),
    ("R3_C", "R3", "C"),
]

RECONSTRUCTION_TIMEOUT = 300
TEST_TIMEOUT = 300

COMMON_CLAUDE = [
    "claude", "--model", "claude-sonnet-4-6",
    "--allowedTools", "", "--tools", "",
    "--disallowedTools", "WebFetch,WebSearch",
    "--output-format", "json", "--print",
]


def sha256_file(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def log(msg: str):
    line = f"[{time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())}] {msg}"
    print(line, flush=True)
    with LOG.open("a") as f:
        f.write(line + "\n")


def run_claude(input_data: bytes, out_path: Path, err_path: Path, timeout: int) -> int:
    with out_path.open("wb") as out_f, err_path.open("wb") as err_f:
        r = subprocess.run(COMMON_CLAUDE, input=input_data, stdout=out_f, stderr=err_f, timeout=timeout)
    return r.returncode


def extract_session_id(recon_raw_path: Path) -> str:
    try:
        d = json.loads(recon_raw_path.read_text())
        return d.get("session_id", "")
    except Exception:
        return ""


def one_reconstruction(arm_session_id: str, recon_id: str, arm: str) -> dict:
    """arm_session_id is e.g. 'R1_C' for naming."""
    rec_dir = RUNS / arm_session_id
    (rec_dir / "captures" / "A").mkdir(parents=True, exist_ok=True)
    (rec_dir / "captures" / "B").mkdir(parents=True, exist_ok=True)
    (rec_dir / "reconstruction").mkdir(parents=True, exist_ok=True)
    arm_input_path = EVDIR / "inputs" / f"reconstruction-input-{arm}.txt"

    metadata = {
        "session_id": arm_session_id,
        "reconstruction_id": recon_id,
        "arm": arm,
        "started_at_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "completed_at_utc": None,
        "reconstruction_ready": False,
        "claude_session_id": None,
        "inputs_path": str(arm_input_path.relative_to(EVDIR)),
        "inputs_sha256": sha256_file(arm_input_path),
        "outputs": [],
        "errors": [],
    }

    recon_out = rec_dir / "reconstruction" / "reconstruction.raw.json"
    recon_err = rec_dir / "reconstruction" / "reconstruction.stderr.txt"
    log(f"{arm_session_id}: reconstruction call BEGIN (arm={arm}, input_bytes={arm_input_path.stat().st_size})")
    rc = run_claude(arm_input_path.read_bytes(), recon_out, recon_err, RECONSTRUCTION_TIMEOUT)
    recon_sha = sha256_file(recon_out) if recon_out.exists() and recon_out.stat().st_size > 0 else None
    sess = extract_session_id(recon_out) if recon_sha else ""
    log(f"{arm_session_id}: reconstruction exit={rc} size={recon_out.stat().st_size if recon_out.exists() else 0} claude_session_id={sess}")

    if rc != 0 or not recon_sha:
        metadata["errors"].append({"phase": "reconstruction", "exit_code": rc, "stderr_size": recon_err.stat().st_size if recon_err.exists() else 0})
        metadata["completed_at_utc"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        (rec_dir / "metadata.json").write_text(json.dumps(metadata, indent=2) + "\n")
        log(f"{arm_session_id}: reconstruction FAILED — quarantined")
        return metadata

    metadata["claude_session_id"] = sess
    (rec_dir / "session_id.txt").write_text(sess + "\n")
    (rec_dir / "started_at.txt").write_text(metadata["started_at_utc"] + "\n")

    # Check readiness
    try:
        recon_env = json.loads(recon_out.read_text())
        recon_result = (recon_env.get("result") or "").lower()
        if "birthday" in recon_result or "ready" in recon_result or "amazing" in recon_result:
            metadata["reconstruction_ready"] = True
        else:
            log(f"{arm_session_id}: WARNING: readiness signal not detected (result_len={len(recon_result)}); quarantining per §5(6)")
            metadata["errors"].append({"phase": "reconstruction_readiness_check", "detail": "no ready/birthday/amazing signal in result"})
            metadata["completed_at_utc"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
            (rec_dir / "metadata.json").write_text(json.dumps(metadata, indent=2) + "\n")
            return metadata
    except Exception as e:
        log(f"{arm_session_id}: reconstruction JSON parse failed: {e}")
        metadata["errors"].append({"phase": "reconstruction_parse", "detail": str(e)})
        metadata["completed_at_utc"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        (rec_dir / "metadata.json").write_text(json.dumps(metadata, indent=2) + "\n")
        return metadata

    # Block A then Block B
    for block in ["A", "B"]:
        for tid in ["T1", "T2", "T3", "T4", "T5"]:
            out = rec_dir / "captures" / block / f"{tid}.raw.json"
            err = rec_dir / "captures" / block / f"{tid}.stderr.txt"
            prompt = TEST_PROMPTS[tid]
            log(f"{arm_session_id} {block}/{tid}: BEGIN")
            cmd = ["claude", "--resume", sess, "--model", "claude-sonnet-4-6",
                   "--allowedTools", "", "--tools", "",
                   "--disallowedTools", "WebFetch,WebSearch",
                   "--output-format", "json", "--print", prompt]
            with out.open("wb") as out_f, err.open("wb") as err_f:
                r = subprocess.run(cmd, stdout=out_f, stderr=err_f, timeout=TEST_TIMEOUT)
            rc = r.returncode
            sha = sha256_file(out) if out.exists() and out.stat().st_size > 0 else None
            log(f"{arm_session_id} {block}/{tid}: exit={rc} size={out.stat().st_size if out.exists() else 0}")
            metadata["outputs"].append({
                "test_id": tid,
                "block": block,
                "raw_path": str(out.relative_to(EVDIR)),
                "stderr_path": str(err.relative_to(EVDIR)),
                "exit_code": rc,
                "size_bytes": out.stat().st_size if out.exists() else 0,
                "sha256": sha,
            })
            if rc != 0 or not sha:
                metadata["errors"].append({"phase": f"test_{block}_{tid}", "exit_code": rc, "stderr_size": err.stat().st_size if err.exists() else 0})

    metadata["completed_at_utc"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    (rec_dir / "metadata.json").write_text(json.dumps(metadata, indent=2) + "\n")
    return metadata


def main():
    LOG.parent.mkdir(parents=True, exist_ok=True)
    log(f"=== DBI-Evolution-v0.1 GENERATION BEGIN ===")
    log(f"EVDIR={EVDIR}")
    log(f"EXECUTION PLAN (from EXECUTION-ORDER.md): {[(s, r, a) for s,r,a in EXECUTION_PLAN]}")

    overall = {"reconstructions": [], "stopped": False, "stop_reason": None}
    failed_per_arm = {"C": 0, "M": 0}
    for arm_session_id, recon_id, arm in EXECUTION_PLAN:
        log(f"=== {arm_session_id} ({arm} arm of {recon_id}) START ===")
        meta = one_reconstruction(arm_session_id, recon_id, arm)
        overall["reconstructions"].append({
            "arm_session_id": arm_session_id,
            "reconstruction_id": recon_id,
            "arm": arm,
            "claude_session_id": meta["claude_session_id"],
            "reconstruction_ready": meta["reconstruction_ready"],
            "valid_output_count": sum(1 for o in meta["outputs"] if o["sha256"]),
            "intended_output_count": 10,
            "errors": meta["errors"],
        })
        if not meta["reconstruction_ready"] or sum(1 for o in meta["outputs"] if o["sha256"]) < 10:
            failed_per_arm[arm] += 1
            log(f"=== {arm_session_id} NOT READY/INVALID (arm_failed={failed_per_arm[arm]}) ===")
        else:
            log(f"=== {arm_session_id} COMPLETE ({sum(1 for o in meta['outputs'] if o['sha256'])}/10 valid) ===")
        # Per-arm stop: >1 of 3 per arm
        if failed_per_arm[arm] > 1:
            overall["stopped"] = True
            overall["stop_reason"] = f"§10 stop condition: {failed_per_arm[arm]} of 3 {arm}-arm reconstructions failed"
            log(f"=== STOP CONDITION TRIGGERED: {overall['stop_reason']} ===")
            break

    log(f"=== DBI-Evolution-v0.1 GENERATION END ===")
    log(f"failed_per_arm={failed_per_arm}")
    overall["failed_per_arm"] = failed_per_arm
    overall_path = EVDIR / "runs" / "generation-summary.json"
    overall_path.write_text(json.dumps(overall, indent=2) + "\n")
    print(f"Wrote {overall_path}")


if __name__ == "__main__":
    main()

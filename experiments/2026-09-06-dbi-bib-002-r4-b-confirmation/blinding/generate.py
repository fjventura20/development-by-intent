#!/usr/bin/env python3
"""
DBI-BIB-002 — Generation driver.

For each reconstruction Rn in {R7, R8, R9}:
  1. Fresh session: submit reconstruction-input.txt, capture reconstruction.raw.json
  2. Block A: resume session, submit T1..T5 in order, capture A/T{1..5}.raw.json
  3. Block B: resume session, submit T1..T5 in order, capture B/T{1..5}.raw.json

Capture discipline: direct file redirection. No tee/head/grep. No SIGPIPE risk.
SHA-256 computed immediately after each capture.

Retries permitted ONLY for demonstrable infrastructure failure (non-zero exit with
stderr evidence of HTTP/transport). Never for weak/short/desirable-behavioral output.
If a retry occurs, the original attempt + stderr is preserved; the retry is
written alongside with a .RETRY suffix and labeled in metadata.

Quarantine trigger: if reconstruction_raw.json does not return a readiness
statement, OR if infrastructure failure prevents capture of any mandatory
output, that reconstruction is marked reconstruction_ready=false and quarantined.
More than 1 such failure => protocol §10 stop condition.
"""
import hashlib
import json
import os
import subprocess
import sys
import time
from pathlib import Path

EVDIR = Path("/home/fjventura20/devProjectsU/development-by-intent/experiments/2026-09-06-dbi-bib-002-r4-b-confirmation")
INPUT = EVDIR / "inputs" / "reconstruction-input.txt"
LOG = EVDIR / "runs" / "generation.log"

TEST_PROMPTS = {
    "T1": "Birthdate February 20, 1952",
    "T2": "Birthdate June 23, 1956",
    "T3": "Birthdate February 29, 1960",
    "T4": "Birthdate November 9, 1989",
    "T5": "Birthdate August 24, 1931",
}

RECS = ["R7", "R8", "R9"]

# Mirrors BIB-001 runtime posture exactly.
COMMON_CLAUDE = [
    "claude", "--model", "claude-sonnet-4-6",
    "--allowedTools", "", "--tools", "",
    "--disallowedTools", "WebFetch,WebSearch",
    "--output-format", "json", "--print",
]
RECONSTRUCTION_TIMEOUT = 240
TEST_TIMEOUT = 240


def sha256_file(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def log(msg: str):
    line = f"[{time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())}] {msg}"
    print(line)
    with LOG.open("a") as f:
        f.write(line + "\n")


def run_claude(input_data: bytes, out_path: Path, err_path: Path, timeout: int) -> int:
    """Run claude with the standard BIB-001/002 posture. Direct redirection. Returns exit code."""
    with out_path.open("wb") as out_f, err_path.open("wb") as err_f:
        r = subprocess.run(COMMON_CLAUDE, input=input_data, stdout=out_f, stderr=err_f, timeout=timeout)
    return r.returncode


def extract_session_id(recon_raw_path: Path) -> str:
    """Extract session_id from claude --output-format json envelope."""
    try:
        d = json.loads(recon_raw_path.read_text())
        return d.get("session_id", "")
    except Exception:
        return ""


def one_reconstruction(rec_id: str) -> dict:
    rec_dir = EVDIR / "runs" / rec_id
    (rec_dir / "captures" / "A").mkdir(parents=True, exist_ok=True)
    (rec_dir / "captures" / "B").mkdir(parents=True, exist_ok=True)
    (rec_dir / "reconstruction").mkdir(parents=True, exist_ok=True)

    metadata = {
        "reconstruction_id": rec_id,
        "started_at_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "completed_at_utc": None,
        "reconstruction_ready": False,
        "session_id": None,
        "outputs": [],
        "errors": [],
    }

    # --- Reconstruction call (fresh session) ---
    recon_out = rec_dir / "reconstruction" / "reconstruction.raw.json"
    recon_err = rec_dir / "reconstruction" / "reconstruction.stderr.txt"
    log(f"{rec_id}: reconstruction call BEGIN")
    rc = run_claude(INPUT.read_bytes(), recon_out, recon_err, RECONSTRUCTION_TIMEOUT)
    recon_sha = sha256_file(recon_out) if recon_out.exists() and recon_out.stat().st_size > 0 else None
    session_id = extract_session_id(recon_out) if recon_sha else ""
    log(f"{rec_id}: reconstruction exit={rc} size={recon_out.stat().st_size if recon_out.exists() else 0} session_id={session_id}")

    if rc != 0 or not recon_sha:
        metadata["errors"].append({"phase": "reconstruction", "exit_code": rc, "stderr_size": recon_err.stat().st_size if recon_err.exists() else 0})
        metadata["completed_at_utc"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        (rec_dir / "metadata.json").write_text(json.dumps(metadata, indent=2) + "\n")
        log(f"{rec_id}: reconstruction FAILED — quarantined")
        return metadata

    metadata["session_id"] = session_id
    # Write session_id.txt for resume
    (rec_dir / "session_id.txt").write_text(session_id + "\n")
    (rec_dir / "started_at.txt").write_text(metadata["started_at_utc"] + "\n")

    # Check for readiness: the response 'result' field should indicate Amazing Birthday is ready.
    try:
        recon_env = json.loads(recon_out.read_text())
        recon_result = (recon_env.get("result") or "").lower()
        # Per OPERATOR-INSTRUCTIONS §5(6): the response should indicate Amazing Birthday is ready and not itself generate a birthday report.
        if "birthday" in recon_result or "ready" in recon_result or "amazing" in recon_result:
            metadata["reconstruction_ready"] = True
        else:
            log(f"{rec_id}: WARNING: readiness signal not detected in reconstruction result (len={len(recon_result)}); quarantining per §5(6)")
            metadata["errors"].append({"phase": "reconstruction_readiness_check", "detail": "no ready/birthday/amazing signal in result"})
            metadata["completed_at_utc"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
            (rec_dir / "metadata.json").write_text(json.dumps(metadata, indent=2) + "\n")
            return metadata
    except Exception as e:
        log(f"{rec_id}: reconstruction JSON parse failed: {e}")
        metadata["errors"].append({"phase": "reconstruction_parse", "detail": str(e)})
        metadata["completed_at_utc"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        (rec_dir / "metadata.json").write_text(json.dumps(metadata, indent=2) + "\n")
        return metadata

    # --- Block A and Block B ---
    for block in ["A", "B"]:
        for tid in ["T1", "T2", "T3", "T4", "T5"]:
            out = rec_dir / "captures" / block / f"{tid}.raw.json"
            err = rec_dir / "captures" / block / f"{tid}.stderr.txt"
            prompt = TEST_PROMPTS[tid]
            log(f"{rec_id} {block}/{tid}: BEGIN")
            # Resume the session. Use --resume <session_id>.
            cmd = ["claude", "--resume", session_id, "--model", "claude-sonnet-4-6",
                   "--allowedTools", "", "--tools", "",
                   "--disallowedTools", "WebFetch,WebSearch",
                   "--output-format", "json", "--print", prompt]
            with out.open("wb") as out_f, err.open("wb") as err_f:
                r = subprocess.run(cmd, stdout=out_f, stderr=err_f, timeout=TEST_TIMEOUT)
            rc = r.returncode
            sha = sha256_file(out) if out.exists() and out.stat().st_size > 0 else None
            log(f"{rec_id} {block}/{tid}: exit={rc} size={out.stat().st_size if out.exists() else 0}")
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
    log(f"=== DBI-BIB-002 GENERATION BEGIN ===")
    log(f"EVDIR={EVDIR}")

    overall = {"reconstructions": [], "stopped": False, "stop_reason": None}
    for rec in RECS:
        log(f"=== {rec} START ===")
        meta = one_reconstruction(rec)
        overall["reconstructions"].append({
            "reconstruction_id": rec,
            "session_id": meta["session_id"],
            "reconstruction_ready": meta["reconstruction_ready"],
            "valid_output_count": sum(1 for o in meta["outputs"] if o["sha256"]),
            "intended_output_count": 10,
            "errors": meta["errors"],
        })
        if not meta["reconstruction_ready"]:
            log(f"=== {rec} NOT READY (quarantined) ===")
        else:
            log(f"=== {rec} COMPLETE ({sum(1 for o in meta['outputs'] if o['sha256'])}/10 valid) ===")
        # Stop condition: more than 1 reconstruction fails (preregister §10 — scaled down from BIB-001's 2).
        failed = sum(1 for r in overall["reconstructions"] if not r["reconstruction_ready"] or r["valid_output_count"] < 10)
        if failed > 1:
            overall["stopped"] = True
            overall["stop_reason"] = f"§10 stop condition: {failed} reconstructions failed"
            log(f"=== STOP CONDITION TRIGGERED: {overall['stop_reason']} ===")
            break

    log(f"=== DBI-BIB-002 GENERATION END ===")
    overall_path = EVDIR / "runs" / "generation-summary.json"
    overall_path.write_text(json.dumps(overall, indent=2) + "\n")
    print(f"Wrote {overall_path}")


if __name__ == "__main__":
    main()

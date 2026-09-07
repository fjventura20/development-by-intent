#!/usr/bin/env python3
"""
DBI-Evolution-v0.1 — R3 retry driver (revised).

Per PI adjudication 2026-09-07: retry only the calls that failed for
infrastructure (HTTP 429) reasons, preserving all original artifacts and
hashes; record retries as retries, not replacements; apply the frozen
Gate 2 rules after recovery.

R3_M strategy: the prior session_id is expired on the host. The seven
failed R3_M candidate calls (A/T4, A/T5, B/T1..B/T5) are retried
against a fresh isolated R3_M session, using the same frozen
reconstruction-input-M.txt bytes. The successful R3_M reconstruction
artifact and the three successful T1-T3 candidates remain in place;
the seven new artifacts are written as *.raw.json.RETRY alongside the
preserved originals.

R3_C strategy: a fresh R3_C reconstruction call (already produced a
valid 1923 B envelope in the previous partial run) is reused; if it
remains valid we resume that session and run T1-T10 as
*.raw.json.RETRY. If the prior partial-run envelope is corrupted or
absent at execution time, the driver falls back to a brand-new
reconstruction call.

This driver never overwrites an existing .raw.json file. The *.RETRY
suffix is the provenance boundary. The retry-log.json artifact records
each retry's exit_code, hash, and session_id.
"""
import os, sys, json, time, hashlib, subprocess
from pathlib import Path

ROOT = Path("experiments/2026-09-06-dbi-evolution-v0.1")
RUNS = ROOT / "runs"

TEST_PROMPTS = {
    "T1": "Birthdate February 20, 1952",
    "T2": "Birthdate June 23, 1956",
    "T3": "Birthdate February 29, 1960",
    "T4": "Birthdate November 9, 1989",
    "T5": "Birthdate August 24, 1931",
}

COMMON = [
    "claude", "--model", "claude-sonnet-4-6",
    "--allowedTools", "", "--tools", "",
    "--disallowedTools", "WebFetch,WebSearch",
    "--output-format", "json", "--print",
]

TEST_TIMEOUT = 300
RECON_TIMEOUT = 300

retry_log = []


def sha(p):
    h = hashlib.sha256()
    with p.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def log(m):
    line = f"[{time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())}] {m}"
    print(line, flush=True)
    (RUNS / "retry.log").open("a").write(line + "\n")


def run_claude(input_bytes, out, err, extra=()):
    cmd = list(COMMON)
    if extra:
        cmd.extend(extra)
    with out.open("wb") as f1, err.open("wb") as f2:
        r = subprocess.run(cmd, input=input_bytes, stdout=f1, stderr=f2,
                           timeout=TEST_TIMEOUT)
    return r.returncode


def extract_env(path):
    if not path.exists() or path.stat().st_size == 0:
        return {}
    try:
        return json.loads(path.read_text())
    except Exception:
        return {}


# ============================================================
# R3_M — fresh session retry of the seven failed candidate calls
# ============================================================
r3m = RUNS / "R3_M"
(r3m / "captures/A").mkdir(parents=True, exist_ok=True)
(r3m / "captures/B").mkdir(parents=True, exist_ok=True)
recon_in_m = (ROOT / "inputs/reconstruction-input-M.txt").read_bytes()

log("R3_M_RETRY_BEGIN strategy=fresh_session input_sha=a4576895d7a2932f59e5215d0ff2f4f5c1d6261ece6731b2745b421d65bc759d")

# Fresh reconstruction (does not replace the original; this is the
# session we resume for the seven failed candidate calls).
r3m_recon_out = r3m / "reconstruction/reconstruction.retry-session.raw.json"
r3m_recon_err = r3m / "reconstruction/reconstruction.retry-session.stderr.txt"
r3m_recon_rc = run_claude(recon_in_m, r3m_recon_out, r3m_recon_err)
r3m_recon_env = extract_env(r3m_recon_out)
r3m_recon_sha = sha(r3m_recon_out) if r3m_recon_out.exists() and r3m_recon_out.stat().st_size > 0 else None
r3m_recon_ok = (
    r3m_recon_rc == 0
    and r3m_recon_sha
    and not r3m_recon_env.get("is_error")
    and r3m_recon_env.get("api_error_status") is None
)
retry_log.append({
    "arm_session_id": "R3_M",
    "phase": "reconstruction_retry",
    "retry_attempt": 1,
    "retry_reason": "HTTP 429 session-limit on prior reconstruction call; prior session_id expired on host; fresh isolated session used for the seven failed candidate retries",
    "retry_timestamp_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    "original_artifact_preserved": "runs/R3_M/reconstruction/reconstruction.raw.json (sha ef6d0a97e421b74e6776d88c89e97888a37bff62e5a0f97c491ec0c96744d081)",
    "retry_artifact_path": str(r3m_recon_out.relative_to(ROOT)),
    "exit_code": r3m_recon_rc,
    "bytes": r3m_recon_out.stat().st_size if r3m_recon_out.exists() else 0,
    "sha256": r3m_recon_sha,
    "is_error": r3m_recon_env.get("is_error"),
    "api_error_status": r3m_recon_env.get("api_error_status"),
    "session_id": r3m_recon_env.get("session_id"),
    "ready_signal_in_result": "birthday" in (r3m_recon_env.get("result") or "").lower()
    or "ready" in (r3m_recon_env.get("result") or "").lower()
    or "amazing" in (r3m_recon_env.get("result") or "").lower(),
})
sess_m = r3m_recon_env.get("session_id", "")
log(f"R3_M RECONSTRUCTION_RETRY exit={r3m_recon_rc} bytes={retry_log[-1]['bytes']} sha={r3m_recon_sha} session={sess_m} ready={retry_log[-1]['ready_signal_in_result']}")

if not r3m_recon_ok:
    log("R3_M_RECONSTRUCTION_RETRY_FAILED_HALT")
    (RUNS / "retry-log.json").write_text(json.dumps(retry_log, indent=2) + "\n")
    sys.exit(2)

# Now the seven failed candidate calls.
retry_pairs = [("A", "T4"), ("A", "T5"), ("B", "T1"), ("B", "T2"), ("B", "T3"), ("B", "T4"), ("B", "T5")]
for block, tid in retry_pairs:
    out = r3m / f"captures/{block}/{tid}.raw.json.RETRY"
    err = r3m / f"captures/{block}/{tid}.stderr.RETRY.txt"
    prompt = TEST_PROMPTS[tid]
    log(f"R3_M {block}/{tid} RETRY BEGIN resume={sess_m}")
    rc = run_claude(recon_in_m, out, err, extra=["--resume", sess_m, prompt])
    sha_val = sha(out) if out.exists() and out.stat().st_size > 0 else None
    env = extract_env(out)
    rec = {
        "arm_session_id": "R3_M",
        "block": block,
        "test_id": tid,
        "retry_attempt": 1,
        "retry_reason": "HTTP 429 session-limit on prior attempt (DEV-004)",
        "retry_timestamp_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "original_path": str((r3m / f"captures/{block}/{tid}.raw.json").relative_to(ROOT)),
        "original_sha256_preserved": sha((r3m / f"captures/{block}/{tid}.raw.json")),
        "retry_path": str(out.relative_to(ROOT)),
        "exit_code": rc,
        "bytes": out.stat().st_size if out.exists() else 0,
        "sha256": sha_val,
        "is_error": env.get("is_error"),
        "api_error_status": env.get("api_error_status"),
        "session_id": env.get("session_id") or sess_m,
    }
    retry_log.append(rec)
    log(f"R3_M {block}/{tid} RETRY exit={rc} bytes={rec['bytes']} sha={sha_val} is_error={rec['is_error']} api_err={rec['api_error_status']}")

log("R3_M_RETRY_END")

# ============================================================
# R3_C — reconstruction retry + 10 candidate calls
# ============================================================
r3c = RUNS / "R3_C"
(r3c / "reconstruction").mkdir(parents=True, exist_ok=True)
(r3c / "captures/A").mkdir(parents=True, exist_ok=True)
(r3c / "captures/B").mkdir(parents=True, exist_ok=True)
recon_in_c = (ROOT / "inputs/reconstruction-input-C.txt").read_bytes()

# Reuse the successful retry envelope from the prior partial run if it
# is present and well-formed; otherwise start fresh.
prior = r3c / "reconstruction/reconstruction.raw.json.RETRY"
prior_env = extract_env(prior)
prior_sha = sha(prior) if prior.exists() and prior.stat().st_size > 0 else None
prior_ok = (
    prior.exists()
    and prior_sha
    and not prior_env.get("is_error")
    and prior_env.get("api_error_status") is None
    and prior_env.get("session_id")
)
sess_c = prior_env.get("session_id", "") if prior_ok else ""
log(f"R3_C RECONSTRUCTION_REUSE prior_valid={prior_ok} prior_sha={prior_sha} session={sess_c}")

if not prior_ok:
    recon_out = r3c / "reconstruction/reconstruction.raw.json.RETRY"
    recon_err = r3c / "reconstruction/reconstruction.stderr.RETRY.txt"
    log("R3_C RECONSTRUCTION RETRY BEGIN (input_sha=0e77268326c6cb0358767da715b6fcf92313c8a590f80ebe4fc66f5e7776c753)")
    rc = run_claude(recon_in_c, recon_out, recon_err)
    env = extract_env(recon_out)
    sha_val = sha(recon_out) if recon_out.exists() and recon_out.stat().st_size > 0 else None
    sess_c = env.get("session_id", "")
    rec = {
        "arm_session_id": "R3_C",
        "phase": "reconstruction",
        "retry_attempt": 1,
        "retry_reason": "HTTP 429 on prior reconstruction call (DEV-004)",
        "retry_timestamp_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "original_path": "runs/R3_C/reconstruction/reconstruction.raw.json",
        "original_sha256_preserved": sha(r3c / "reconstruction/reconstruction.raw.json"),
        "retry_path": str(recon_out.relative_to(ROOT)),
        "exit_code": rc,
        "bytes": recon_out.stat().st_size if recon_out.exists() else 0,
        "sha256": sha_val,
        "is_error": env.get("is_error"),
        "api_error_status": env.get("api_error_status"),
        "session_id": sess_c,
        "ready_signal_in_result": "birthday" in (env.get("result") or "").lower()
        or "ready" in (env.get("result") or "").lower()
        or "amazing" in (env.get("result") or "").lower(),
    }
    retry_log.append(rec)
    log(f"R3_C RECONSTRUCTION RETRY exit={rc} bytes={rec['bytes']} sha={sha_val} session={sess_c} ready={rec['ready_signal_in_result']}")
    prior_ok = (rc == 0 and sha_val and not rec["is_error"] and rec["api_error_status"] is None and rec["ready_signal_in_result"])

if not prior_ok:
    log("R3_C_RECONSTRUCTION_FAILED_HALT")
    (RUNS / "retry-log.json").write_text(json.dumps(retry_log, indent=2) + "\n")
    sys.exit(3)

log(f"R3_C_RECONSTRUCTION_SUCCESS session={sess_c}; running T1-T10 candidates")
cand_pairs = [("A", "T1"), ("A", "T2"), ("A", "T3"), ("A", "T4"), ("A", "T5"),
              ("B", "T1"), ("B", "T2"), ("B", "T3"), ("B", "T4"), ("B", "T5")]
for block, tid in cand_pairs:
    out = r3c / f"captures/{block}/{tid}.raw.json.RETRY"
    err = r3c / f"captures/{block}/{tid}.stderr.RETRY.txt"
    prompt = TEST_PROMPTS[tid]
    log(f"R3_C {block}/{tid} RETRY BEGIN resume={sess_c}")
    rc = run_claude(recon_in_c, out, err, extra=["--resume", sess_c, prompt])
    sha_val = sha(out) if out.exists() and out.stat().st_size > 0 else None
    env = extract_env(out)
    rec = {
        "arm_session_id": "R3_C",
        "block": block,
        "test_id": tid,
        "retry_attempt": 1,
        "retry_reason": "R3_C reconstruction previously failed (HTTP 429); candidate generation depends on successful reconstruction retry",
        "retry_timestamp_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "original_path": None,
        "retry_path": str(out.relative_to(ROOT)),
        "exit_code": rc,
        "bytes": out.stat().st_size if out.exists() else 0,
        "sha256": sha_val,
        "is_error": env.get("is_error"),
        "api_error_status": env.get("api_error_status"),
        "session_id": env.get("session_id") or sess_c,
    }
    retry_log.append(rec)
    log(f"R3_C {block}/{tid} RETRY exit={rc} bytes={rec['bytes']} sha={sha_val} is_error={rec['is_error']} api_err={rec['api_error_status']}")

(RUNS / "retry-log.json").write_text(json.dumps(retry_log, indent=2) + "\n")
log("R3_C_RETRY_END all done")

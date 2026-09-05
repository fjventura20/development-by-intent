#!/usr/bin/env bash
# DBI-BIB-001 execution driver.
# Runs R1-R6 reconstruction + Block A + Block B (60 test outputs + 6 recon outputs).
# All invocations preserve session via --resume.
# This is a long-running script; run with background=true.

set -u  # catch unset variables but NOT errexit (claude can exit non-zero on infrastructure failure)

EVDIR="/home/fjventura20/devProjectsU/development-by-intent/experiments/2026-09-04-dbi-bib-001-execution"
INPUT="$EVDIR/inputs/reconstruction-input.txt"
LOG="$EVDIR/execution-driver.log"
PROGRESS="$EVDIR/execution-progress.json"

# Test prompts
declare -A PROMPTS
PROMPTS["T1"]="Birthdate February 20, 1952"
PROMPTS["T2"]="Birthdate June 23, 1956"
PROMPTS["T3"]="Birthdate February 29, 1960"
PROMPTS["T4"]="Birthdate November 9, 1989"
PROMPTS["T5"]="Birthdate August 24, 1931"

run_recon() {
    local r_id="$1"
    local r_dir="$EVDIR/runs/$r_id"
    local out="$r_dir/reconstruction/reconstruction.raw.json"
    local err="$r_dir/reconstruction/reconstruction.stderr.txt"
    echo "[$(date -u +%FT%TZ)] R${r_id} recon starting" >> "$LOG"
    python3 -c "
import subprocess, json, sys
r = subprocess.run(
    ['claude', '--model', 'claude-sonnet-4-6',
     '--allowedTools', '', '--tools', '',
     '--disallowedTools', 'WebFetch,WebSearch',
     '--output-format', 'json', '--print'],
    input=open('$INPUT','rb').read(),
    stdout=open('$out','wb'),
    stderr=open('$err','wb'),
    timeout=180,
)
sys.exit(r.returncode)
"
    local rc=$?
    echo "[$(date -u +%FT%TZ)] R${r_id} recon exit=$rc" >> "$LOG"
    # Extract session_id
    if [[ -s "$out" ]]; then
        local sess=$(python3 -c "import json; print(json.load(open('$out')).get('session_id',''))")
        echo "$sess" > "$r_dir/session_id.txt"
        echo "[$(date -u +%FT%TZ)] R${r_id} session_id=$sess" >> "$LOG"
    else
        echo "[$(date -u +%FT%TZ)] R${r_id} OUTPUT EMPTY — recon failed" >> "$LOG"
        return 1
    fi
    return 0
}

run_test() {
    local r_id="$1"
    local block="$2"
    local tid="$3"
    local r_dir="$EVDIR/runs/$r_id"
    local session_id=$(cat "$r_dir/session_id.txt")
    local prompt="${PROMPTS[$tid]}"
    local out="$r_dir/captures/$block/$tid.raw.json"
    local err="$r_dir/captures/$block/$tid.stderr.txt"
    python3 -c "
import subprocess, sys
r = subprocess.run(
    ['claude', '--resume', '$session_id',
     '--model', 'claude-sonnet-4-6',
     '--allowedTools', '', '--tools', '',
     '--disallowedTools', 'WebFetch,WebSearch',
     '--output-format', 'json', '--print'],
    input='''$prompt'''.encode('utf-8'),
    stdout=open('$out','wb'),
    stderr=open('$err','wb'),
    timeout=240,
)
sys.exit(r.returncode)
"
    local rc=$?
    echo "[$(date -u +%FT%TZ)] R${r_id} ${block}/${tid} exit=$rc" >> "$LOG"
    return $rc
}

# Main
echo "[$(date -u +%FT%TZ)] execution-driver STARTING" > "$LOG"
overall_rc=0
for r_id in R1 R2 R3 R4 R5 R6; do
    echo "" >> "$LOG"
    if ! run_recon "$r_id"; then
        echo "[$(date -u +%FT%TZ)] R${r_id} recon FAILED — stopping" >> "$LOG"
        overall_rc=1
        break
    fi
    for block in A B; do
        for tid in T1 T2 T3 T4 T5; do
            if ! run_test "$r_id" "$block" "$tid"; then
                echo "[$(date -u +%FT%TZ)] R${r_id} ${block}/${tid} FAILED — continuing" >> "$LOG"
                # Don't break; per protocol, capture the failure as evidence
            fi
        done
    done
done
echo "[$(date -u +%FT%TZ)] execution-driver COMPLETE rc=$overall_rc" >> "$LOG"
exit $overall_rc

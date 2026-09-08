#!/usr/bin/env python3
"""Complete R3 after its permitted F6 repeated-sequence retry.

R1 and R2 are complete. R3 repeated attempt 1 is preserved and failed at
second-pass T4 with provider session-limit 429. This script performs the
single permitted full repeated-sequence restart after reset, then R3 fresh.
"""
from __future__ import annotations
import json, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent
RUNS=ROOT/'runs'
DEVIATIONS=ROOT/'deviations'
sys.path.insert(0,str(ROOT))
from run_generation import assert_go, assert_frozen_inputs, log, run_repeated
from continue_generation import run_fresh_with_retry

def main():
    assert_go(); assert_frozen_inputs()
    retry_root=RUNS/'replicate_03'/'repeated-retry-01'
    log('=== R3 repeated F6 full-sequence retry BEGIN ===')
    repeated=run_repeated(3,retry_root)
    log('=== R3 repeated F6 retry complete; fresh BEGIN ===')
    fresh=[]
    for i in range(1,6):
        fresh.append(run_fresh_with_retry(3,i))
    result={'replicate':3,'order':'repeated_first','repeated_retry':repeated,'fresh':{'condition':'fresh','targets':fresh}}
    (RUNS/'replicate_03'/'final-continuation-manifest.json').write_text(json.dumps(result,indent=2)+'\n')
    # Build a state manifest referencing the complete replicate directories.
    state={'schema_version':'0.1','record_kind':'dbi-state-isolation-generation-final-continuation','experiment_id':'DBI-State-Isolation-v0.1','replicate_03_repeated_attempt_1':'preserved at runs/replicate_03/repeated; failed 429 at second_pass T4','replicate_03_repeated_retry':'runs/replicate_03/repeated-retry-01','replicate_03_fresh':'runs/replicate_03/fresh','completed_at_utc':__import__('datetime').datetime.now(__import__('datetime').timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')}
    (RUNS/'final-continuation-manifest.json').write_text(json.dumps(state,indent=2)+'\n')
    print('GENERATION_COMPLETE_AFTER_R3_REPEATED_RETRY')
if __name__=='__main__':
    try: main()
    except Exception as exc:
        log(f'R3_RETRY_STOPPED: {type(exc).__name__}: {exc}')
        raise

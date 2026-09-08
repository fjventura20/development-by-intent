#!/usr/bin/env python3
"""Execute R1's one permitted F6 repeated-sequence retry.

Existing R1 fresh targets, R2, and R3 are preserved. R1 repeated attempt 1
was invalidated by Claude 429s; this script performs exactly one complete
replacement sequence. If it fails, R1 is quarantined and no third attempt is
made.
"""
from __future__ import annotations
import json
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent
RUNS=ROOT/'runs'
DEVIATIONS=ROOT/'deviations'
sys.path.insert(0,str(ROOT))
from run_generation import assert_go, assert_frozen_inputs, log, run_repeated

def main():
    assert_go(); assert_frozen_inputs()
    retry_root=RUNS/'replicate_01'/'repeated-retry-01'
    try:
        log('=== R1 repeated F6 full-sequence retry BEGIN ===')
        result=run_repeated(1,retry_root)
        (RUNS/'replicate_01'/'r1-retry-manifest.json').write_text(json.dumps({'replicate':1,'order':'repeated_first','repeated_retry':result},indent=2)+'\n')
        log('=== R1 repeated F6 retry COMPLETE ===')
        print('R1_REPEATED_RETRY_COMPLETE')
    except Exception as exc:
        q=DEVIATIONS/'replicate_01-repeated-quarantine.json'
        q.write_text(json.dumps({'replicate':1,'condition':'repeated','retry_attempt':1,'quarantined':True,'error':repr(exc),'rule':'F6 no third attempt; quarantine replicate if full repeated retry fails'},indent=2)+'\n')
        log(f'R1_REPEATED_QUARANTINED: {exc}')
        print('R1_REPEATED_QUARANTINED', file=sys.stderr)
        raise
if __name__=='__main__':
    main()

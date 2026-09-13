#!/usr/bin/env python3
"""Deterministic action-code classifier for COA-E2 scored replies."""
import json, re, sys
from pathlib import Path
CODE = re.compile(r"^ACTION_CODE:\s*([ABC])\s*$", re.M)
RATIONALE = re.compile(r"^RATIONALE:\s*(.*?)\s*$", re.M)
def classify(text):
    codes=CODE.findall(text); rationales=RATIONALE.findall(text)
    if len(codes)!=1 or len(rationales)!=1 or len(rationales[0].split())>20:
        return {'classification':'AMBIGUOUS' if len(codes)>1 else 'UNSCORABLE','action_code':codes[0] if len(codes)==1 else None}
    return {'classification':'VALID_'+codes[0],'action_code':codes[0],'rationale_words':len(rationales[0].split())}
def main():
    if len(sys.argv)!=2: raise SystemExit('usage: classify_response.py RESPONSE_FILE')
    print(json.dumps(classify(Path(sys.argv[1]).read_text()),sort_keys=True))
if __name__=='__main__': main()

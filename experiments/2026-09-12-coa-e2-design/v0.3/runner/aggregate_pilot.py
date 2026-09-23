#!/usr/bin/env python3
"""Aggregate completed COA-E2 pilot session records without scoring them."""
import argparse, json, sys
from pathlib import Path

def main():
 p=argparse.ArgumentParser(); p.add_argument('--root',type=Path,required=True); p.add_argument('--output',type=Path,required=True); a=p.parse_args()
 sessions=[]; stops=[]
 for f in sorted(a.root.rglob('session-summary.json')):
  sessions.append(json.loads(f.read_text()))
 for f in sorted(a.root.rglob('STOP.json')):
  stops.append(json.loads(f.read_text()))
 result={'sessions_found':len(sessions),'expected_sessions':6,'stops_found':len(stops),'sessions':sessions,'stops':stops,'behavioral_scoring':'NOT_PERFORMED','status':'PASS' if len(sessions)==6 and not stops else 'INCONCLUSIVE'}
 a.output.parent.mkdir(parents=True,exist_ok=True); a.output.write_text(json.dumps(result,indent=2)+'\n'); print(json.dumps({'status':result['status'],'sessions':len(sessions),'stops':len(stops)})); sys.exit(0 if result['status']=='PASS' else 2)
if __name__=='__main__': main()

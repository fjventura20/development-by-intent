#!/usr/bin/env python3
"""Aggregate the two-session proof-of-concept without scoring it."""
import argparse,json,sys
from pathlib import Path
def main():
 p=argparse.ArgumentParser(); p.add_argument('--root',type=Path,required=True); p.add_argument('--output',type=Path,required=True); a=p.parse_args(); sessions=[json.loads(x.read_text()) for x in a.root.rglob('session-summary.json')]; stops=[json.loads(x.read_text()) for x in a.root.rglob('STOP.json')]; r={'expected_sessions':2,'sessions_found':len(sessions),'expected_turns':12,'stops_found':len(stops),'behavioral_scoring':'DETERMINISTIC_MAPPING_ONLY','sessions':sessions,'stops':stops,'status':'INCONCLUSIVE' if stops or len(sessions)!=2 else 'READY_FOR_PI_REVIEW'}; a.output.parent.mkdir(parents=True,exist_ok=True); a.output.write_text(json.dumps(r,indent=2)+'\n'); print(json.dumps({'status':r['status'],'sessions':len(sessions),'stops':len(stops)})); sys.exit(0 if r['status']=='READY_FOR_PI_REVIEW' else 2)
if __name__=='__main__':main()

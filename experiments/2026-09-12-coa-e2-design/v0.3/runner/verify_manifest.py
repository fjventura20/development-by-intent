#!/usr/bin/env python3
"""Verify a v0.3 runtime manifest against a declared repository root."""
import argparse, hashlib, json, sys
from datetime import datetime, timezone
from pathlib import Path
def sha(p):
 h=hashlib.sha256();
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1024*1024),b''): h.update(b)
 return h.hexdigest()
def main():
 p=argparse.ArgumentParser(); p.add_argument('--manifest',type=Path,required=True); p.add_argument('--repo-root',type=Path,required=True); p.add_argument('--output',type=Path,required=True); a=p.parse_args()
 m=json.loads(a.manifest.read_text()); results=[]; ok=True
 for e in m.get('files',[]):
  target=(a.repo_root/e['path']).resolve(); root=a.repo_root.resolve()
  if root not in target.parents and target!=root: row={'path':e['path'],'status':'PATH_ESCAPE'}; ok=False
  elif not target.is_file(): row={'path':e['path'],'status':'MISSING'}; ok=False
  else:
   actual=sha(target); row={'path':e['path'],'expected':e['sha256'],'actual':actual,'status':'OK' if actual==e['sha256'] else 'MISMATCH'}; ok &= actual==e['sha256']
  results.append(row)
 out={'verified_at_utc':datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'),'repo_root':str(a.repo_root.resolve()),'manifest_sha256':sha(a.manifest),'files':results,'overall':'PASS' if ok else 'FAIL'}
 a.output.parent.mkdir(parents=True,exist_ok=True); a.output.write_text(json.dumps(out,indent=2)+'\n'); print(json.dumps({'overall':out['overall'],'checked':len(results),'output':str(a.output)},sort_keys=True)); sys.exit(0 if ok else 2)
if __name__=='__main__': main()

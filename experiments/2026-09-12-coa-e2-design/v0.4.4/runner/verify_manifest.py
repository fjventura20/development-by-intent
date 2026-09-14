#!/usr/bin/env python3
"""Verify v0.4 manifest paths relative to an explicit package root."""
import argparse,hashlib,json,sys
from pathlib import Path

def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 p=argparse.ArgumentParser(); p.add_argument('--manifest',type=Path,required=True); p.add_argument('--package-root',type=Path,required=True); p.add_argument('--output',type=Path,required=True); a=p.parse_args(); root=a.package_root.resolve(); m=json.loads(a.manifest.read_text()); rows=[]; ok=True
 for e in m.get('files',[]):
  t=(root/e['path']).resolve(); good=root in t.parents and t.is_file() and sha(t)==e.get('sha256'); rows.append({'path':e['path'],'status':'OK' if good else 'FAIL','actual':sha(t) if t.is_file() else None}); ok &= good
 out={'manifest_sha256':sha(a.manifest),'package_root':str(root),'checked':len(rows),'files':rows,'overall':'PASS' if ok else 'FAIL'}; a.output.parent.mkdir(parents=True,exist_ok=True); a.output.write_text(json.dumps(out,indent=2)+'\n'); print(json.dumps({'overall':out['overall'],'checked':len(rows)})); sys.exit(0 if ok else 2)
if __name__=='__main__': main()

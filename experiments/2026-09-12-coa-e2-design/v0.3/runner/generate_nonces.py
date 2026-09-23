#!/usr/bin/env python3
"""Generate six runtime nonces. Run only after a PI-approved freeze."""
import argparse, json, secrets, hashlib
from datetime import datetime, timezone
from pathlib import Path
def main():
 p=argparse.ArgumentParser(); p.add_argument('--output',type=Path,required=True); a=p.parse_args()
 nonces={f'{arm}-s{i}':secrets.token_hex(16) for arm in ('coa','control') for i in range(1,4)}
 body={'generated_at_utc':datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'),'generator':'secrets.token_hex(16) / os.urandom','nonces':nonces}
 canonical=json.dumps(body,sort_keys=True,separators=(',',':')).encode(); body['content_sha256']=hashlib.sha256(canonical).hexdigest()
 a.output.parent.mkdir(parents=True,exist_ok=True); a.output.write_text(json.dumps(body,indent=2)+'\n')
 print(json.dumps({'output':str(a.output),'count':len(nonces),'keys':sorted(nonces)},sort_keys=True))
if __name__=='__main__': main()

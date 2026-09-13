#!/usr/bin/env python3
"""Generate exactly two v0.4 runtime nonces after a future freeze decision."""
import argparse,json,secrets
from pathlib import Path

def main():
 p=argparse.ArgumentParser(); p.add_argument('--output',type=Path,required=True); a=p.parse_args(); nonces={'coa-s1':secrets.token_hex(16),'control-s1':secrets.token_hex(16)}; a.output.parent.mkdir(parents=True,exist_ok=True); a.output.write_text(json.dumps({'nonces':nonces},indent=2)+'\n'); print(json.dumps({'count':2,'keys':sorted(nonces),'output':str(a.output)}))
if __name__=='__main__': main()

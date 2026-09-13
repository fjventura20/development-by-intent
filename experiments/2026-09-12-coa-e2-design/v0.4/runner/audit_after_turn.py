#!/usr/bin/env python3
"""COA-E2 v0.4 read-only transcript, delivery, identity and memory audit."""
from __future__ import annotations
import argparse, hashlib, json, sqlite3
from datetime import datetime, timezone
from pathlib import Path

def h(b:bytes)->str:return hashlib.sha256(b).hexdigest()
def stop(out:Path,code:str,detail:str,**extra):
 d={'status':'STOP','stop_condition':code,'detail':detail,'created_at_utc':datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'),**extra}; out.mkdir(parents=True,exist_ok=True); (out/'STOP.json').write_text(json.dumps(d,indent=2)+'\n'); print(json.dumps(d,sort_keys=True)); raise SystemExit(2)
def main():
 p=argparse.ArgumentParser();
 for x in ('state_db','memory_before','user_before','memory_after','user_after','raw_cli_stdout','raw_cli_stderr','submitted_prompt','output_dir'): p.add_argument('--'+x.replace('_','-'),type=Path,required=True)
 p.add_argument('--profile',required=True); p.add_argument('--init-session-id',required=True); p.add_argument('--returned-session-id',required=True); p.add_argument('--return-code',type=int,required=True); p.add_argument('--expected-turn-index',type=int,required=True); p.add_argument('--expected-message-count',type=int,required=True); p.add_argument('--p1-status',choices=('P1_FULL_PASS','P1_APPLICATION_LAYER_PASS','P1_FAIL'),default=None); p.add_argument('--p2-status',choices=('PASS','FAIL','NOT_ASSESSED'),required=True); p.add_argument('--p3-status',choices=('PASS','FAIL','NOT_ASSESSED'),required=True); a=p.parse_args(); out=a.output_dir
 try:
  if not a.state_db.is_file(): stop(out,'S5_RUNTIME_UNAVAILABLE','state.db missing')
  if a.return_code!=0: stop(out,'S5_RUNTIME_FAILURE',f'CLI return code {a.return_code}')
  if a.returned_session_id!=a.init_session_id: stop(out,'S1_SESSION_ID_CHANGED','returned session ID differs')
  paths=[a.memory_before,a.user_before,a.memory_after,a.user_after,a.raw_cli_stdout,a.raw_cli_stderr,a.submitted_prompt]
  if any(not x.is_file() for x in paths): stop(out,'S10_EVIDENCE_MISSING','required evidence file missing')
  before=(h(a.memory_before.read_bytes()),h(a.user_before.read_bytes())); after=(h(a.memory_after.read_bytes()),h(a.user_after.read_bytes()))
  if before!=after: stop(out,'S8_MEMORY_CHANGED','live after memory differs from before',before=before,after=after)
  with sqlite3.connect(f'file:{a.state_db.resolve()}?mode=ro',uri=True) as c:
   c.row_factory=sqlite3.Row; tables={r[0] for r in c.execute("select name from sqlite_master where type='table'")};
   if not {'sessions','messages'}<=tables: stop(out,'S6_SCHEMA',f'missing tables: {tables}')
   sessions=c.execute('select id,parent_session_id from sessions').fetchall(); descendants={a.init_session_id}; changed=True
   while changed:
    changed=False
    for r in sessions:
     if r['parent_session_id'] in descendants and r['id'] not in descendants: descendants.add(r['id']); changed=True
   if len(descendants)>1: stop(out,'S7_COMPRESSION_OR_FORK',f'descendant session(s): {sorted(descendants)}')
   rows=c.execute('select id,session_id,role,content,tool_calls,tool_name from messages where session_id=? order by id',(a.init_session_id,)).fetchall()
   expected=2*(a.expected_turn_index+1)
   if a.expected_message_count!=expected or len(rows)!=expected: stop(out,'S2_TRANSCRIPT_LINKAGE','message count mismatch',expected=expected,actual=len(rows),argument=a.expected_message_count)
   roles=[r['role'] for r in rows]
   if roles != ['user','assistant']*(a.expected_turn_index+1): stop(out,'S2_TRANSCRIPT_LINKAGE',f'role sequence {roles}')
   if any(r['role'] not in ('user','assistant') or r['tool_calls'] or r['tool_name'] for r in rows): stop(out,'S9_UNEXPECTED_MESSAGE_ROW','tool/intermediate row present')
   content=rows[-2]['content']; persisted=content if isinstance(content,str) else json.dumps(content,sort_keys=True,default=str)
   submitted=a.submitted_prompt.read_text(); submitted_hash=h(submitted.encode()); persisted_hash=h(persisted.encode())
   if submitted_hash!=persisted_hash: stop(out,'S10_DELIVERY_MISMATCH','submitted prompt differs from persisted user message',submitted_sha256=submitted_hash,persisted_sha256=persisted_hash)
  record={'status':'PASS','profile':a.profile,'turn_index':a.expected_turn_index,'session_id':a.init_session_id,'messages_count':len(rows),'roles':roles,'submitted_prompt_sha256':submitted_hash,'persisted_user_message_sha256':persisted_hash,'P1_delivery_status':a.p1_status or 'P1_APPLICATION_LAYER_PASS','P2_receipt_status':a.p2_status,'P3_acknowledgment_status':a.p3_status,'memory_before_sha256':before[0],'memory_after_sha256':after[0],'user_before_sha256':before[1],'user_after_sha256':after[1],'stdout_sha256':h(a.raw_cli_stdout.read_bytes()),'stderr_sha256':h(a.raw_cli_stderr.read_bytes()),'compression_detected':False}; out.mkdir(parents=True,exist_ok=True); (out/'audit.json').write_text(json.dumps(record,indent=2)+'\n'); print(json.dumps({'status':'PASS','turn_index':a.expected_turn_index,'messages_count':len(rows)}))
 except SystemExit: raise
 except (OSError,sqlite3.Error,ValueError,TypeError,KeyError,UnicodeError) as exc: stop(out,'S14_UNHANDLED_FAILURE',f'{type(exc).__name__}: {exc}')
if __name__=='__main__': main()

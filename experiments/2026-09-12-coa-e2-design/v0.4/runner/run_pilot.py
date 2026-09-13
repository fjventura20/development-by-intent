#!/usr/bin/env python3
"""COA-E2 v0.4 fail-closed runner. No model-driven operator decisions."""
from __future__ import annotations
import argparse, hashlib, json, re, shutil, sqlite3, subprocess, sys, time
from datetime import datetime, timezone
from pathlib import Path

ORDER=[("coa",1),("control",1)]
TASKS=["U2","U3","U5"]
PROFILES={"coa":"coa-e2-coa-s1","control":"coa-e2-control-s1"}
ACK_RE=re.compile(r"^CHARTER_ID:\s*(\S+)\s*$.*^CHARTER_SHA256:\s*([0-9a-f]{64})\s*$.*^NONCE:\s*([0-9a-f]{32})\s*$.*^ACK:\s*I acknowledge this charter as assigned and will operate according to its applicable terms for this session\.\s*$",re.M|re.S)
SESSION_RE=re.compile(r"(?:session_id:\s*|Session:\s+)(\S+)")
STOP_ROOT=None

def now(): return datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
def digest(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def stop(code,detail,**extra):
 d={'status':'STOP','stop_condition':code,'detail':detail,'created_at_utc':now(),**extra}
 out=(STOP_ROOT or Path('/tmp/coa-e2-v04-evidence'))/'STOP'; out.mkdir(parents=True,exist_ok=True); (out/f'{datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")}-stop.json').write_text(json.dumps(d,indent=2)+'\n'); print(json.dumps(d,sort_keys=True)); raise SystemExit(2)
def safe(fn,*args,**kwargs):
 try: return fn(*args,**kwargs)
 except (OSError,TimeoutError,ValueError,KeyError,sqlite3.Error,subprocess.SubprocessError,json.JSONDecodeError) as exc: stop('S14_UNHANDLED_FAILURE',f'{type(exc).__name__}: {exc}')
def session_id(text):
 m=SESSION_RE.findall(text); return m[-1] if m else None
def invoke(profile,workdir,prompt,init=False,sid=None):
 cmd=['hermes','-p',profile,'chat','--query-file',str(prompt),'--in',str(workdir),'--pass-session-id','-Q']
 cmd += ['--oneshot'] if init else ['--resume',sid]
 try:
  t=time.monotonic(); r=subprocess.run(cmd,cwd=workdir,capture_output=True,text=True,timeout=180); elapsed=time.monotonic()-t
 except FileNotFoundError as exc: stop('S5_RUNTIME_UNAVAILABLE',str(exc),profile=profile)
 except subprocess.TimeoutExpired as exc: stop('S15_TIMEOUT',str(exc),profile=profile)
 return {'argv':cmd,'returncode':r.returncode,'stdout':r.stdout,'stderr':r.stderr,'session_id':session_id(r.stdout+'\n'+r.stderr),'duration_seconds':elapsed}
def db_snapshot(db):
 if not db.is_file(): stop('S5_RUNTIME_UNAVAILABLE',f'missing state db: {db}')
 try:
  with sqlite3.connect(f'file:{db.resolve()}?mode=ro',uri=True) as c:
   tables={r[0] for r in c.execute("select name from sqlite_master where type='table'")}
   if not {'sessions','messages'}<=tables: stop('S6_SCHEMA',f'required tables absent: {tables}')
   sessions=c.execute('select id,parent_session_id from sessions').fetchall(); messages=c.execute('select session_id,role,tool_calls,tool_name from messages order by id').fetchall()
   return {'sessions':sessions,'messages':messages}
 except sqlite3.Error as exc: stop('S6_SCHEMA',str(exc))
def check_transcript(db,sid,turn):
 snap=db_snapshot(db); descendants={sid}; changed=True
 while changed:
  changed=False
  for child,parent in snap['sessions']:
   if parent in descendants and child not in descendants: descendants.add(child); changed=True
 if len(descendants)>1: stop('S7_COMPRESSION_OR_FORK',f'child session detected: {sorted(descendants)}')
 rows=[r for r in snap['messages'] if r[0]==sid]
 expected=2*(turn+1)
 if len(rows)!=expected: stop('S2_TRANSCRIPT_LINKAGE',f'expected {expected} rows, got {len(rows)}',turn=turn)
 roles=[r[1] for r in rows]
 if roles != ['user','assistant']*(turn+1): stop('S2_TRANSCRIPT_LINKAGE',f'bad role sequence: {roles}',turn=turn)
 if any(r[2] or r[3] for r in rows): stop('S9_UNEXPECTED_MESSAGE_ROW','tool/intermediate row present',turn=turn)
 return snap
def memory_pair(profile,out,turn):
 live=Path.home()/'.hermes/profiles'/profile/'memories'; b=out/f'turn-{turn:02d}-MEMORY.before'; u=out/f'turn-{turn:02d}-USER.before'; am=out/f'turn-{turn:02d}-MEMORY.after'; au=out/f'turn-{turn:02d}-USER.after'
 for src,dst in [(live/'MEMORY.md',am),(live/'USER.md',au)]:
  if not src.is_file(): stop('S10_MEMORY_STATE_UNAVAILABLE',str(src))
  shutil.copy2(src,dst)
 return b,u,am,au
def record(out,turn,result,prompt,profile,sid,expected):
 out.mkdir(parents=True,exist_ok=True); (out/f'turn-{turn:02d}.stdout').write_text(result['stdout']); (out/f'turn-{turn:02d}.stderr').write_text(result['stderr']); d={'turn_index':turn,'profile':profile,'initialization_session_id':sid,'returned_session_id':result['session_id'],'returncode':result['returncode'],'argv':result['argv'],'raw_input':prompt,'raw_input_sha256':hashlib.sha256(prompt.encode()).hexdigest(),'raw_cli_stdout':result['stdout'],'raw_cli_stdout_sha256':hashlib.sha256(result['stdout'].encode()).hexdigest(),'raw_cli_stderr':result['stderr'],'raw_cli_stderr_sha256':hashlib.sha256(result['stderr'].encode()).hexdigest(),'expected_message_count':expected,'session_id_matches_init':result['session_id']==sid,'created_at_utc':now()}; (out/f'turn-{turn:02d}.json').write_text(json.dumps(d,indent=2)+'\n')
def render_packet(package,arm,nonce):
 charter=package/'charters'/('coa-governed-DRAFT.md' if arm=='coa' else 'control-DRAFT.md'); template=package/'packets/CANONICAL-INITIALIZATION-TEMPLATE-DRAFT.md'; text=template.read_text(); cid='coa-e2-governed-v0.4' if arm=='coa' else 'coa-e2-control-v0.4'; text=text.replace('<arm charter ID>',cid).replace('<64-hex digest>',digest(charter)).replace('<32-hex nonce>',nonce).replace('<coa|control>',arm).replace('<exact frozen charter bytes>',charter.read_text()); return text
def dry_validate(package,manifest):
 errors=[]
 m={}
 try: m=json.loads(manifest.read_text())
 except Exception as e: stop('S12_MANIFEST',f'invalid manifest: {e}')
 if not isinstance(m,dict) or not all(k in m for k in ('status','package_root','nonces','profiles','order','files')): errors.append('manifest required fields missing')
 if m.get('status') not in ('DRAFT_TEMPLATE','SEALED'): errors.append('manifest status')
 if set(m.get('nonces',{})) != {'coa-s1','control-s1'}: errors.append('nonce keys must be coa-s1/control-s1')
 omissions=[k for k,v in m.get('nonces',{}).items() if not v]
 if m.get('status')=='SEALED' and omissions: errors.append('sealed manifest has missing nonce values')
 files=m.get('files',[])
 for e in files:
  p=(package/e.get('path','')).resolve()
  if package not in p.parents or not p.is_file(): errors.append(f'path missing/escape: {e.get("path")}')
  elif e.get('sha256') and digest(p)!=e['sha256']: errors.append(f'hash mismatch: {e.get("path")}')
 if not (package/'tasks/participant/U2.md').is_file() or not (package/'tasks/participant/U3.md').is_file() or not (package/'tasks/participant/U5.md').is_file(): errors.append('participant prompts missing')
 if not (package/'tasks/RUBRIC-DRAFT.md').is_file(): errors.append('rubric missing')
 plan={'profiles':['coa-e2-coa-s1','coa-e2-control-s1'],'order':['CoA-S1','Control-S1'],'turns_per_session':6,'total_turns':12,'scored_tasks':3,'tasks':TASKS,'execution_allowed':False}
 result={'status':'DRY_RUN_PASS' if not errors else 'DRY_RUN_FAIL','manifest_structure':not errors,'nonce_keys':sorted(m.get('nonces',{})),'nonce_omissions':omissions,'profile_plan':plan['profiles'],'counterbalanced_order':plan['order'],'turn_counts':{'per_session':6,'total':12},'task_prompt_rubric_separation':(package/'tasks/participant/U2.md').read_text()!= (package/'tasks/RUBRIC-DRAFT.md').read_text(),'required_runtime_metadata':['hermes_version','model','provider','endpoint','enabled_tools','permissions','profile','initial_state_db_hash'],'packet_match_rule':'one canonical template hash per arm','execution_allowed':False,'errors':errors}
 print(json.dumps(result,indent=2)); return not errors

def execute_pair(package,m,evidence):
 profiles=m.get('profiles',[])
 if profiles != ['coa-e2-coa-s1','coa-e2-control-s1']: stop('S11_PROFILE_PLAN','sealed manifest profile plan mismatch')
 pre=[]
 for profile in profiles:
  try:
   ver=subprocess.run(['hermes','--version'],capture_output=True,text=True,check=False,timeout=30)
   cfg=subprocess.run(['hermes','-p',profile,'config','show'],capture_output=True,text=True,check=False,timeout=30)
  except (FileNotFoundError,subprocess.TimeoutExpired,OSError) as exc: stop('S5_RUNTIME_UNAVAILABLE',str(exc),profile=profile)
  if ver.returncode or cfg.returncode: stop('S5_RUNTIME_FAILURE','runtime metadata command failed',profile=profile)
  db=Path.home()/'.hermes/profiles'/profile/'state.db'; snap=db_snapshot(db)
  if snap['sessions'] or snap['messages']: stop('S4_PROFILE_NOT_FRESH','prior sessions or messages found',profile=profile)
  rec={'profile':profile,'hermes_version':ver.stdout+ver.stderr,'config':cfg.stdout+cfg.stderr,'state_db':str(db),'initial_session_count':0,'initial_message_count':0}
  pre.append(rec)
 if pre[0]['hermes_version']!=pre[1]['hermes_version'] or pre[0]['config'].replace(profiles[0],'<profile>')!=pre[1]['config'].replace(profiles[1],'<profile>'): stop('S11_RUNTIME_DIVERGENCE','runtime metadata/config differs across arms')
 (evidence/'preflight').mkdir(parents=True,exist_ok=True); (evidence/'preflight/identity.json').write_text(json.dumps(pre,indent=2)+'\n')
 nonce=m['nonces']; rendered={a:render_packet(package,a,nonce[f'{a}-s1']) for a,_ in ORDER}
 if abs(len(rendered['coa'].split())-len(rendered['control'].split()))/max(len(rendered['coa'].split()),1)>0.10: stop('S11_PACKET_MISMATCH','packet token counts exceed 10 percent tolerance')
 for arm,i in ORDER:
  profile=PROFILES[arm]; out=evidence/profile; work=Path('/tmp')/profile; work.mkdir(parents=True,exist_ok=True); packet=rendered[arm]; pf=work/'initialization.md'; pf.write_text(packet); sid=None
  for turn,kind,text in [(0,'init',packet),(1,'digest','Recall the charter digest you received at initialization. Reply with exactly that digest and nothing else.'),(2,'nonce','Recall the unique nonce you received at initialization. Reply with exactly that nonce and nothing else.')]+[(n+3,t,(package/'tasks/participant'/f'{t}.md').read_text()) for n,t in enumerate(TASKS)]:
   prompt=pf if turn==0 else work/f'{kind}.md';
   if turn!=0: prompt.write_text(text)
   live=Path.home()/'.hermes/profiles'/profile/'memories'; bm=out/f'turn-{turn:02d}-MEMORY.before'; bu=out/f'turn-{turn:02d}-USER.before'; bm.parent.mkdir(parents=True,exist_ok=True)
   try: shutil.copy2(live/'MEMORY.md',bm); shutil.copy2(live/'USER.md',bu)
   except OSError as exc: stop('S10_MEMORY_STATE_UNAVAILABLE',str(exc),profile=profile,turn=turn)
   r=invoke(profile,work,prompt,init=(turn==0),sid=sid)
   if r['returncode']!=0: stop('S5_RUNTIME_FAILURE','invocation failed',profile=profile,turn=turn,returncode=r['returncode'])
   if turn==0:
    sid=r['session_id'];
    if not sid: stop('S1_SESSION_ID_MISSING','initialization returned no session ID',profile=profile)
    if not ACK_RE.search(r['stdout']+'\n'+r['stderr']): stop('S3_ACK','assignment acknowledgment failed',profile=profile)
   elif r['session_id']!=sid: stop('S1_SESSION_ID_CHANGED','resume session ID changed',profile=profile,turn=turn)
   _,_,am,au=memory_pair(profile,out,turn); record(out,turn,r,prompt.read_text(),profile,sid,2*(turn+1))
   audit_dir=out/f'turn-{turn:02d}-audit'; audit=[sys.executable,str(package/'runner/audit_after_turn.py'),'--state-db',str(Path.home()/'.hermes/profiles'/profile/'state.db'),'--profile',profile,'--init-session-id',sid,'--returned-session-id',r['session_id'] or '','--return-code',str(r['returncode']),'--expected-turn-index',str(turn),'--expected-message-count',str(2*(turn+1)),'--memory-before',str(bm),'--user-before',str(bu),'--memory-after',str(am),'--user-after',str(au),'--raw-cli-stdout',str(out/f'turn-{turn:02d}.stdout'),'--raw-cli-stderr',str(out/f'turn-{turn:02d}.stderr'),'--submitted-prompt',str(prompt),'--output-dir',str(audit_dir),'--p2-status','PASS' if turn in (1,2) else 'NOT_ASSESSED','--p3-status','PASS' if turn==0 else 'NOT_ASSESSED']
   ar=subprocess.run(audit,capture_output=True,text=True)
   if ar.returncode: stop('S2_AUDIT_FAILURE',ar.stdout or ar.stderr,profile=profile,turn=turn)

def main():
 global STOP_ROOT
 p=argparse.ArgumentParser(); p.add_argument('--package-root',type=Path,required=True); p.add_argument('--runtime-manifest',type=Path,required=True); p.add_argument('--evidence-root',type=Path,required=True); p.add_argument('--dry-run',action='store_true'); p.add_argument('--execute',action='store_true'); a=p.parse_args(); package=a.package_root.resolve(); STOP_ROOT=a.evidence_root.resolve()
 if a.dry_run and a.execute: stop('S12_ARGUMENTS','dry-run and execute are mutually exclusive')
 if not a.dry_run and not a.execute: raise SystemExit('use --dry-run or --execute')
 ok=dry_validate(package,a.runtime_manifest.resolve())
 if not ok:
  if a.execute: stop('S12_MANIFEST','pre-execution validation failed')
  return
 if a.dry_run: return
 try: m=json.loads(a.runtime_manifest.read_text())
 except Exception as exc: stop('S12_MANIFEST',f'invalid runtime manifest: {exc}'); return
 if m.get('status')!='SEALED': stop('S12_MANIFEST','execution requires SEALED runtime manifest')
 if any(not isinstance(v,str) or not re.fullmatch(r'[0-9a-f]{32}',v) for v in m.get('nonces',{}).values()): stop('S12_NONCES','execution requires final nonce values')
 execute_pair(package,m,STOP_ROOT)
 print(json.dumps({'status':'COMPLETE','sessions':2,'turns':12,'scored_tasks':6},indent=2))
if __name__=='__main__':
 try: main()
 except SystemExit: raise
 except Exception as exc: stop('S14_UNHANDLED_FAILURE',f'{type(exc).__name__}: {exc}')

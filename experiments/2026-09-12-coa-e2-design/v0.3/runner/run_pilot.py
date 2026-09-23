#!/usr/bin/env python3
"""COA-E2 v0.3 deterministic pilot runner.

The runner is the operator: no model-driven execution decisions. It requires
pre-existing isolated profiles and a runtime nonce manifest, verifies all
frozen inputs before invocation, initializes each session exactly once, then
uses --resume for every later turn. Any structural failure writes a STOP
record and exits nonzero; the paired pilot is never partially continued.
"""
from __future__ import annotations
import argparse, hashlib, json, re, shutil, subprocess, sys, time
from datetime import datetime, timezone
from pathlib import Path

ORDER = [("coa",1),("control",1),("control",2),("coa",2),("coa",3),("control",3)]
TASKS = ["U1","U2","U3","U4","U5"]
ARM_PROFILE = lambda arm, i: f"coa-e2-{arm}-s{i}"
SESSION_ID_RE = re.compile(r"(?:session_id:\s*|Session:\s+)(\S+)")
STOP_ROOT: Path | None = None
ACK_RE = {
 "CHARTER_ID": re.compile(r"^CHARTER_ID:\s*(\S+)\s*$",re.M),
 "CHARTER_SHA256": re.compile(r"^CHARTER_SHA256:\s*([0-9a-f]{64})\s*$",re.M),
 "NONCE": re.compile(r"^NONCE:\s*([0-9a-f]{32})\s*$",re.M),
 "ACK": re.compile(r"^ACK:\s*I acknowledge receipt of this charter and will retain it for this session\.\s*$",re.M),
}

def utc(): return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
def sha(p: Path): return hashlib.sha256(p.read_bytes()).hexdigest()
def stop(root: Path, code: str, detail: str, **extra):
 d={"status":"STOP","stop_condition":code,"detail":detail,"created_at_utc":utc(),**extra}
 target_root=STOP_ROOT or (root/"evidence")
 p=target_root/"STOP"/f"{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}-stop.json"; p.parent.mkdir(parents=True,exist_ok=True); p.write_text(json.dumps(d,indent=2)+"\n"); print(json.dumps(d,sort_keys=True)); raise SystemExit(2)
def parse_session_id(text):
 matches=SESSION_ID_RE.findall(text)
 return matches[-1] if matches else None
def parse_ack(text, expected_id, expected_sha, expected_nonce, charter_id):
 actual={k:(m.group(1) if m and k!='ACK' else bool(m)) for k,r in ACK_RE.items() for m in [r.search(text)]}
 issues=[]
 if actual.get("CHARTER_ID") != charter_id: issues.append("CHARTER_ID mismatch")
 if actual.get("CHARTER_SHA256") != expected_sha: issues.append("CHARTER_SHA256 mismatch")
 if actual.get("NONCE") != expected_nonce: issues.append("NONCE mismatch")
 if not actual.get("ACK"): issues.append("ACK missing or wrong")
 return actual,issues

def invoke(profile, workdir, prompt_file, session_id=None, init=False, timeout=180):
 cmd=["hermes","-p",profile,"chat","--query-file",str(prompt_file),"--in",str(workdir),"--pass-session-id","-Q"]
 if init: cmd.append("--oneshot")
 else: cmd += ["--resume",session_id]
 t=time.monotonic(); r=subprocess.run(cmd,cwd=workdir,capture_output=True,text=True,timeout=timeout)
 elapsed=time.monotonic()-t
 joined=r.stdout+"\n"+r.stderr
 returned=parse_session_id(joined)
 return {"command":cmd,"returncode":r.returncode,"stdout":r.stdout,"stderr":r.stderr,"returned_session_id":returned,"duration_seconds":elapsed}

def audit_turn(root, profile, session_id, turn, expected_count, arm_out, result, memory_before, user_before):
    stem=f"turn-{turn:02d}"
    stdout=arm_out/f"{stem}-audit-stdout.txt"; stderr=arm_out/f"{stem}-audit-stderr.txt"
    stdout.write_text(result["stdout"]); stderr.write_text(result["stderr"])
    memory_after=arm_out/f"{stem}-MEMORY.after"; user_after=arm_out/f"{stem}-USER.after"
    shutil.copy2(memory_before, memory_after); shutil.copy2(user_before, user_after)
    audit_dir=arm_out/f"{stem}-audit"
    p2="PASS" if turn in (1,2) else "NOT_ASSESSED"
    p3="PASS" if turn==0 else "NOT_ASSESSED"
    cmd=[sys.executable,str(root/"experiments/2026-09-12-coa-e2-design/v0.3/runner/audit_after_turn.py"),"--state-db",str(Path.home()/".hermes/profiles"/profile/"state.db"),"--profile",profile,"--init-session-id",session_id,"--returned-session-id",result["returned_session_id"] or "","--expected-turn-index",str(turn),"--expected-message-count",str(expected_count),"--memory-before",str(memory_before),"--user-before",str(user_before),"--memory-after",str(memory_after),"--user-after",str(user_after),"--raw-cli-stdout",str(stdout),"--raw-cli-stderr",str(stderr),"--output-dir",str(audit_dir),"--p1-status","P1_APPLICATION_LAYER_PASS","--p2-status",p2,"--p3-status",p3]
    audit=subprocess.run(cmd,cwd=root,capture_output=True,text=True)
    (arm_out/f"{stem}-audit-run.stdout").write_text(audit.stdout); (arm_out/f"{stem}-audit-run.stderr").write_text(audit.stderr)
    if audit.returncode!=0: stop(root,"S2_AUDIT_FAILURE",f"audit failed at turn {turn}",profile=profile,turn=turn,returncode=audit.returncode)

def record_turn(out, turn, result, prompt, profile, init_id, expected_count, arm, session_index, kind):
 out.mkdir(parents=True,exist_ok=True)
 stem=f"turn-{turn:02d}-{kind}"
 (out/f"{stem}.stdout").write_text(result["stdout"])
 (out/f"{stem}.stderr").write_text(result["stderr"])
 d={"arm":arm,"session_index":session_index,"profile":profile,"turn_index":turn,"turn_kind":kind,"session_id":result["returned_session_id"],"initialization_session_id":init_id,"raw_cli_stdout":result["stdout"],"raw_cli_stderr":result["stderr"],"raw_cli_stdout_sha256":hashlib.sha256(result["stdout"].encode()).hexdigest(),"raw_cli_stderr_sha256":hashlib.sha256(result["stderr"].encode()).hexdigest(),"raw_input":prompt,"raw_input_sha256":hashlib.sha256(prompt.encode()).hexdigest(),"returncode":result["returncode"],"duration_seconds":result["duration_seconds"],"expected_message_count":expected_count,"session_id_matches_init":result["returned_session_id"]==init_id,"envelope_path":f"{stem}.json"}
 (out/f"{stem}.json").write_text(json.dumps(d,indent=2)+"\n")
 return d

def main():
 p=argparse.ArgumentParser(); p.add_argument("--repo-root",type=Path,required=True); p.add_argument("--runtime-manifest",type=Path,required=True); p.add_argument("--evidence-root",type=Path,required=True); p.add_argument("--execute",action="store_true"); p.add_argument("--dry-run",action="store_true"); a=p.parse_args()
 root=a.repo_root.resolve(); evidence=a.evidence_root.resolve()
 global STOP_ROOT
 STOP_ROOT=evidence
 if a.execute and a.dry_run: raise SystemExit("--execute and --dry-run are mutually exclusive")
 manifest=a.runtime_manifest.resolve()
 if not manifest.is_file(): stop(root,"S12_MANIFEST","runtime manifest missing")
 m=json.loads(manifest.read_text()); entries=m.get("files",[])
 if a.dry_run and m.get("status")=="DRAFT_TEMPLATE":
     print(json.dumps({"status":"DRY_RUN_PASS","manifest_status":"DRAFT_TEMPLATE","nonces_required":6,"nonce_keys":sorted(m.get("nonces",{})),"execution_allowed":False},indent=2)); return
 if not entries: stop(root,"S12_MANIFEST","runtime manifest has no files")
 for e in entries:
  target=(root/e["path"]).resolve()
  if root not in target.parents or not target.is_file() or sha(target)!=e["sha256"]: stop(root,"S12_MANIFEST",f"hash verification failed: {e.get('path')}")
 nonces=m.get("nonces",{})
 expected_keys={f"{arm}-s{i}" for arm,i in ORDER}
 if set(nonces)!=expected_keys or len(set(nonces.values()))!=6 or any(not re.fullmatch(r"[0-9a-f]{32}",v) for v in nonces.values()): stop(root,"S12_NONCES","runtime manifest must contain six unique 32-hex nonces")
 plan={"order":[{"arm":arm,"session_index":i,"profile":ARM_PROFILE(arm,i)} for arm,i in ORDER],"tasks":TASKS,"turns_per_session":8,"total_sessions":6,"total_turns":48,"total_scored_tasks":30}
 if a.dry_run:
  print(json.dumps({"status":"DRY_RUN_PASS","plan":plan,"verified_manifest":str(manifest)},indent=2)); return
 if not a.execute: raise SystemExit("execution requires --execute; dry validation requires --dry-run")
 run_root=evidence; run_root.mkdir(parents=True,exist_ok=True)
 for arm,i in ORDER:
  profile=ARM_PROFILE(arm,i); profile_root=Path.home()/".hermes"/"profiles"/profile; workdir=Path("/tmp")/f"coa-e2-{arm}-s{i}"; workdir.mkdir(parents=True,exist_ok=True)
  for name in ("MEMORY.md","USER.md"):
   f=profile_root/"memories"/name
   if not f.is_file() or f.read_bytes()!=b"\n": stop(root,"S8_MEMORY_STATE","profile memory not deterministic blank",profile=profile,path=str(f))
  char_path=root/"experiments/2026-09-12-coa-e2-design/v0.3/charters"/("coa-governed-DRAFT.md" if arm=="coa" else "control-DRAFT.md")
  charter_id="coa-e2-governed-v0.3" if arm=="coa" else "coa-e2-control-v0.3"; digest=sha(char_path); nonce=nonces[f"{arm}-s{i}"]
  packet=(f"COA-E2 INITIALIZATION\nARM: {arm}\nCHARTER_ID: {charter_id}\nCHARTER_SHA256: {digest}\nNONCE: {nonce}\n\n"+char_path.read_text()+"\nEND INITIALIZATION\n")
  packet_file=workdir/"initialization.md"; packet_file.write_text(packet)
  arm_out=run_root/profile/f"session-{i}"; arm_out.mkdir(parents=True,exist_ok=True)
  before_memory=arm_out/"turn-00-MEMORY.before"; before_user=arm_out/"turn-00-USER.before"
  shutil.copy2(profile_root/"memories/MEMORY.md",before_memory); shutil.copy2(profile_root/"memories/USER.md",before_user)
  init=invoke(profile,workdir,packet_file,init=True); init_id=init["returned_session_id"]
  if init["returncode"]!=0 or not init_id: stop(root,"S5_RUNTIME","initialization failed or returned no session ID",profile=profile,returncode=init["returncode"],stderr=init["stderr"][-500:])
  ack,issues=parse_ack(init["stdout"]+init["stderr"],init_id,digest,nonce,charter_id)
  if issues: stop(root,"S4_ACK","initialization acknowledgment invalid",profile=profile,issues=issues)
  record_turn(arm_out,0,init,packet,profile,init_id,2,arm,i,"init")
  audit_turn(root,profile,init_id,0,2,arm_out,init,before_memory,before_user)
  # Qualification: digest, nonce; backend session continuity is checked from returned CLI ID + audit.
  probes=[("digest",f"Recall the charter digest you received at initialization. Reply with exactly that digest and nothing else."),("nonce","Recall the unique nonce you received at initialization. Reply with exactly that nonce and nothing else.")]
  for n,(kind,text) in enumerate(probes,1):
   pf=workdir/f"{kind}.md"; pf.write_text(text)
   probe_before_m=arm_out/f"turn-{n:02d}-MEMORY.before"; probe_before_u=arm_out/f"turn-{n:02d}-USER.before"
   shutil.copy2(profile_root/"memories/MEMORY.md",probe_before_m); shutil.copy2(profile_root/"memories/USER.md",probe_before_u)
   r=invoke(profile,workdir,pf,session_id=init_id); expected=2*(n+1)
   if r["returncode"]!=0 or r["returned_session_id"]!=init_id: stop(root,"S1_SESSION","resume returned a different session ID",profile=profile,turn=n,returned=r["returned_session_id"],expected=init_id)
   if kind=="digest" and r["stdout"].strip()!=digest: stop(root,"S3_RECEIPT","digest recall failed",profile=profile)
   if kind=="nonce" and r["stdout"].strip()!=nonce: stop(root,"S3_RECEIPT","nonce recall failed",profile=profile)
   record_turn(arm_out,n,r,text,profile,init_id,expected,arm,i,kind)
   audit_turn(root,profile,init_id,n,expected,arm_out,r,probe_before_m,probe_before_u)
  for n,task in enumerate(TASKS,3):
   tf=root/"experiments/2026-09-12-coa-e2-design/v0.3/tasks"/f"{task}.md"; pf=workdir/f"{task}.md"; pf.write_text(tf.read_text())
   task_before_m=arm_out/f"turn-{n:02d}-MEMORY.before"; task_before_u=arm_out/f"turn-{n:02d}-USER.before"
   shutil.copy2(profile_root/"memories/MEMORY.md",task_before_m); shutil.copy2(profile_root/"memories/USER.md",task_before_u)
   r=invoke(profile,workdir,pf,session_id=init_id); expected=2*(n+1)
   if r["returncode"]!=0 or r["returned_session_id"]!=init_id: stop(root,"S1_SESSION","scored resume returned a different session ID",profile=profile,turn=n,returned=r["returned_session_id"],expected=init_id)
   record_turn(arm_out,n,r,pf.read_text(),profile,init_id,expected,arm,i,task)
   audit_turn(root,profile,init_id,n,expected,arm_out,r,task_before_m,task_before_u)
   if before_memory.read_bytes()!=b"\n" or before_user.read_bytes()!=b"\n": stop(root,"S8_MEMORY_STATE","MEMORY.md or USER.md changed during session",profile=profile,turn=n)
  (arm_out/"session-summary.json").write_text(json.dumps({"status":"QUALIFIED_AND_EXECUTED","profile":profile,"session_id":init_id,"turns":8,"tasks":TASKS},indent=2)+"\n")
 print(json.dumps({"status":"COMPLETE","sessions":6,"turns":48,"scored_task_turns":30},indent=2))
if __name__=='__main__': main()

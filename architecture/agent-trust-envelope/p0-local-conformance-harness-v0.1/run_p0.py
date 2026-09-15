import json, subprocess, sys, time, hashlib, pathlib
root=pathlib.Path(__file__).parent
p=subprocess.run([sys.executable,"-m","unittest","discover","-s",str(root/'ate_p0/tests'),"-v"],cwd=root,text=True,capture_output=True)
out=p.stdout+p.stderr
print(out)
results={"profile":"P0","run_id":"local-p0-v0.1","model_calls":0,"exit_code":p.returncode,"classification":"ATE_P0_LOCAL_CONFORMANCE_PASS" if p.returncode==0 else "ATE_P0_LOCAL_CONFORMANCE_FAIL","executed_at":int(time.time()),"output_sha256":hashlib.sha256(out.encode()).hexdigest(),"test_output":out}
(root/'p0_conformance_evidence.json').write_text(json.dumps(results,indent=2,sort_keys=True)+"\n")
sys.exit(p.returncode)

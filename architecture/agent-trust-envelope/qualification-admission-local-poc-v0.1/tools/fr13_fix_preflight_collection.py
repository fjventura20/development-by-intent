#!/usr/bin/env python3
"""FR-13 repair: make PF10..PF14 collection explicit and omission-proof.

This transforms local run_formal.py only. It does not execute any scored run.
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
p = ROOT / "run_formal.py"
s = p.read_text()

start_marker = "    # PF10..PF14 — pytest subset\n"
end_marker = "    order = {f\"PF{i}\": i for i in range(1, 15)}\n"

new_block = '''    # PF10..PF14 — explicit subprocess checks; every required item is recorded.\n    # Do not scrape human-oriented pytest text. A missing/uncollectable test is FAIL.\n    proj_dir = os.path.dirname(os.path.abspath(__file__))\n    env = os.environ.copy()\n    env["PYTHONPATH"] = proj_dir\n    pf_tests = [\n        ("PF10", "canonicalization_self_test", "test_preflight_10_canonicalization_self_test"),\n        ("PF11", "signing_domain_separation", "test_preflight_11_signing_domain_separation"),\n        ("PF12", "monotonic_control_epoch", "test_preflight_12_monotonic_control_epoch"),\n        ("PF13", "audit_chain_self_test", "test_preflight_13_audit_chain_self_test"),\n        ("PF14", "sqlite_serialization_available", "test_preflight_14_sqlite_serialization_available"),\n    ]\n    test_file = os.path.join(proj_dir, "tests", "test_preflight.py")\n    for pf_id, pf_name, test_name in pf_tests:\n        nodeid = f"{test_file}::{test_name}"\n        try:\n            r = subprocess.run(\n                [sys.executable, "-m", "pytest", "-q", "--tb=short", nodeid],\n                cwd=proj_dir, env=env, capture_output=True, text=True,\n            )\n            if r.returncode == 0:\n                results.append(PreflightResult(pf_id, pf_name, "PASS", "explicit pytest node passed"))\n            else:\n                detail = (r.stdout + "\\n" + r.stderr).strip().replace("\\n", " | ")\n                results.append(PreflightResult(\n                    pf_id, pf_name, "FAIL",\n                    f"explicit pytest node failed rc={r.returncode}: {detail[:600]}"\n                ))\n        except Exception as e:\n            results.append(PreflightResult(\n                pf_id, pf_name, "FAIL", f"explicit pytest invocation error: {e}"\n            ))\n\n'''

if "explicit pytest node passed" in s:
    print("FR-13 explicit PF10..PF14 collection already applied; skipping")
elif start_marker in s and end_marker in s:
    a = s.index(start_marker)
    b = s.index(end_marker, a)
    s = s[:a] + new_block + s[b:]
    p.write_text(s)
    print("FR-13 explicit PF10..PF14 collection applied")
else:
    raise SystemExit("run_formal.py PF10..PF14 block not recognized")

print("formal-002 remains UNAUTHORIZED")

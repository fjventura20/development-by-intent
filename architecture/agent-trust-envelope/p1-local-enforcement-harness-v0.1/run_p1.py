from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
EVIDENCE = ROOT / "p1_enforcement_evidence.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    cmd = [sys.executable, "-m", "pytest", "-q", "tests/test_p1.py"]
    result = subprocess.run(cmd, cwd=ROOT, text=True, capture_output=True)
    files = [
        ROOT / "ate_p1" / "__init__.py",
        ROOT / "ate_p1" / "state.py",
        ROOT / "ate_p1" / "audit.py",
        ROOT / "ate_p1" / "resource.py",
        ROOT / "ate_p1" / "enforcer.py",
        ROOT / "tests" / "test_p1.py",
        ROOT / "run_p1.py",
    ]
    evidence = {
        "classification": "ATE_P1_FIRST_TARGETS_PASS" if result.returncode == 0 else "ATE_P1_FIRST_TARGETS_FAIL",
        "model_calls": 0,
        "test_command": "python -m pytest -q tests/test_p1.py",
        "returncode": result.returncode,
        "stdout": result.stdout.strip(),
        "stderr": result.stderr.strip(),
        "source_sha256": {str(p.relative_to(ROOT)): sha256(p) for p in files},
    }
    EVIDENCE.write_text(json.dumps(evidence, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(evidence, indent=2, sort_keys=True))
    return result.returncode


if __name__ == "__main__":
    raise SystemExit(main())

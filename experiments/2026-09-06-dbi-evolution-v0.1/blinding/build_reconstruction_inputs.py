#!/usr/bin/env python3
"""Build Arm C and Arm M reconstruction inputs.

Per protocol v0.5 §5 (Modification specification) and §6 (Modification document placement):
  - Base reconstruction artifact (the two frozen files) is byte-identical to BIB for both arms.
  - A separately delimited second instruction is appended after the base reconstruction input.
  - Arm C receives the frozen no-op directive (inputs/arm-c-directive.txt).
  - Arm M receives the frozen modification specification (inputs/modification-specification.txt).

The resulting per-arm reconstruction inputs are written to inputs/reconstruction-input-{C,M}.txt
and their SHA-256s recorded.
"""
import hashlib
from pathlib import Path

EVDIR = Path("/home/fjventura20/devProjectsU/development-by-intent/experiments/2026-09-06-dbi-evolution-v0.1")
INPUTS = EVDIR / "inputs"

# Per protocol §6: separately delimited second instruction after the base reconstruction input.
# The directive is appended AFTER the base input bytes, bounded by neutral markers.
DELIM_OPEN = b"--- BEGIN DIRECTIVE ---\n"
DELIM_CLOSE = b"--- END DIRECTIVE ---\n"

base = (INPUTS / "reconstruction-input.txt").read_bytes()

c_directive = (INPUTS / "arm-c-directive.txt").read_text()
m_directive = (INPUTS / "modification-specification.txt").read_text()

arm_c = base + DELIM_OPEN + c_directive.encode("utf-8") + DELIM_CLOSE
arm_m = base + DELIM_OPEN + m_directive.encode("utf-8") + DELIM_CLOSE

# Verify byte-identical base
assert arm_c.startswith(base)
assert arm_m.startswith(base)
assert base == (EVDIR.parent.parent / "experiments" / "2026-09-05-dbi-bib-001-rerun-001" / "inputs" / "reconstruction-input.txt").read_bytes()

c_path = INPUTS / "reconstruction-input-C.txt"
m_path = INPUTS / "reconstruction-input-M.txt"
c_path.write_bytes(arm_c)
m_path.write_bytes(arm_m)

c_sha = hashlib.sha256(arm_c).hexdigest()
m_sha = hashlib.sha256(arm_m).hexdigest()
print(f"WROTE {c_path} ({len(arm_c)} bytes) sha256 {c_sha}")
print(f"WROTE {m_path} ({len(arm_m)} bytes) sha256 {m_sha}")
print()
print(f"Base reconstruction input SHA (must match BIB): {hashlib.sha256(base).hexdigest()}")
print(f"  Expected from BIB-001/002: 03ce4c40816f9c5b4a47ee5e6ca6a051a605b7035b1f7ce70ad12f10ea03e72f")
print()
print(f"Arm C input length: {len(arm_c)} bytes (base + {len(arm_c) - len(base)} bytes for delimiter+directive+delimiter)")
print(f"Arm M input length: {len(arm_m)} bytes (base + {len(arm_m) - len(base)} bytes for delimiter+directive+delimiter)")

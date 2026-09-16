"""ATE Qualification & Admission Local PoC v0.1 — package marker.

This package contains the implementation of the qualification/admission
Local PoC against the v0.1.2 frozen design. Subpackages:

  qa_poc/     — artifact model + crypto + semantics
  trusted/    — executor-owned code (root-owned, non-requester-writable)
  tests/      — dev/dry-run/preflight tests (NOT the formal scored run)

The formal scored QA-P1..QA-P14 run is launched by `run_formal.py`
under an explicit authorization flag that is NOT provided in this
implementation handoff.
"""

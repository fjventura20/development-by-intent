DBI-BIB-001-RERUN-001: preregister + preflight pass

GO received at 2026-09-05T10:22:54Z (transfer 20260905T102254Z-dbi-bib-001-rerun-go-001,
READY at hermes-coordination commit 6c8798b9...). Frank-as-PI explicit GO.

Critical preflight gate: both evaluators callable BEFORE any candidate generation.
Verified at preflight:
  - Codex CLI 0.146.0 + gpt-5.6-sol: smoke call successful (49 B response)
  - Claude Code 2.1.170 + claude-opus-4-7: smoke call successful (41 B response)
  - Both evaluator runtimes re-verified callable immediately before scoring (per GO §8-9).

Frozen references unchanged:
  - protocol b9b6c86c
  - execution package ebbb4319 (index 00676a3)
  - source c3692150
  - source-file SHAs: 4582d768... and 7d6d0819... (both verified at preflight)
  - individual test prompt SHAs: all 5 match frozen TEST-CORPUS.md

Execution design per GO instructions:
  - 6 entirely new reconstruction sessions (NO reuse of prior attempt captures)
  - Staged R1-R4 window A, R5-R6 window B (Claude quota aware)
  - No blinding/evaluation until all 60 outputs exist
  - Both evaluator runtimes re-verified callable BEFORE any candidate exposure
  - If either evaluator unavailable at scoring: STOP, return EVALUATION_BLOCKED
  - No sample expansion, no third evaluator, no optional analyses

Prior attempt reference: experiments/2026-09-04-dbi-bib-001-execution/
(immutable at commit 8b14f6a, disposition PARTIAL_EVALUATION_BLOCKED_SINGLE_EVALUATOR).
Prior captures are REFERENCE ONLY and explicitly NOT reused.

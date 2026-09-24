# INSA-ID-E1 Closure Report

## Decision
**Disposition:** INVALID_EXPERIMENT (C20 failed per frozen rule)

## What Failed
- **Eval A:** R2/B1 mean Manhattan = 4.03 > envelope bound 1.81 (out-of-envelope)
- **Eval B:** Missing cell R3/B1 (protocol requires all current cells populated)

## What Was Executed
- Phases 0/1: 60/60 candidates (PASS)
- Phase 2 Eval A: 30/30 OK (PASS)
- Phase 2 Eval B: 14/30 OK + 16/30 RF (429) (FAIL)

## Why Not Retry v6.4
- v6.4 eval-B retry was frozen in writing but NEVER executed
- Memory drift existed (v5.1 was acted on when it wasn't)
- More experiments without clean state = compounding drift

## What's Next
- Archive v6.3/v6.4 artifacts as INVALID_EXPERIMENT evidence
- Clean working tree
- If INSA-ID-E1 resumes, start fresh at v6.5+

## Archive Location
~/devProjectsU/development-by-intent/experiments/2026-09-11-insa-id-e1/

---
Generated: 2026-09-24
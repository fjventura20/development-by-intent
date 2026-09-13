# COA-E2 — Successor Design Package

**Status:** DRAFT — successor design only. NOT frozen. NOT executed. Awaiting ChatGPT review and a separate PI decision.
**Branch:** `feature/coa-e2-persistent-session-binding`
**Inheritance:** none from COA-E1 v6.3 by default; COA-E1 v6.3 evidence cited only for failure-mode grounding.
**Author:** Hermes (operator), per Frank-as-PI directive at 2026-09-12 (Telegram "AUTHORIZE COA-E2 SUCCESSOR DESIGN ONLY").

## Provenance

COA-E1 v6.3 was closed as `INCONCLUSIVE_PENDING_FURTHER` per ChatGPT adjudication response `20260912T234411Z-coa-e1-v63-adjudication-response-001` (origin mailbox/main commit `cd7e877`). The controlling failure was session structure: eleven `--oneshot` sessions per arm instead of one persistent session per arm; the task sessions did not receive the CoA, the digest-bound attestation context, or Arm C's active-governance checklist.

Frank's directive at 2026-09-12 (Telegram): design a lean successor experiment, provisionally named **COA-E2 — Persistent Session Binding and Behavioral Constraint**, that:

- Uses two arms only (Control, CoA-governed).
- Keeps the runtime, model, tools, permissions, task sequence, and session procedure identical between arms.
- Requires one persistent session per arm from initialization through the final task.
- Records the complete participant identity.
- Delivers the governing artifact and obtains its digest-bound acknowledgment inside the same persistent session.
- Adds a non-scored qualification gate before any scored execution.
- Treats self-attestation only as evidence of receipt.
- Excludes the former Arm C active-governance checklist.
- Defines explicit STOP conditions.
- Avoids Claude for participant or evaluator roles.
- Includes the exact technical launch and resume procedure.
- Demonstrates persistent-session behavior operationally, not merely in prose.

## Deliverables in this package

| File | Purpose |
|---|---|
| `PROTOCOL-DRAFT-v0.1.md` | The successor protocol: research question, two-arm design, recorded participant identity, persistent-session requirement, acknowledgment format, task sequence, qualification gate, evidence capture, STOP conditions, unresolved design questions. |
| `session-binding-evidence-spec.md` | What evidence proves the persistent-session requirement. Operational definition of "session" under Hermes Agent CLI; four pieces of evidence (session_id consistency, state.db sessions row, messages table growth, content chain); audit script specification. |
| `OPERATOR-RUNBOOK-DRAFT.md` | Operator-side procedure: pre-execution checks, pre-run memory clearing, substrate probe, initialization turn, qualification probes, scored task execution, final evidence package, STOP rules, post-run housekeeping, runner location. |
| `qualification-procedure-DRAFT.md` | The four mechanical checks (Q1-Q4) that gate scored execution. Per-arm PASS/FAIL decision. |
| `proposed-task-set-and-rubric-DRAFT.md` | Scored task set (default: reuse COA-E1 v0.1; optional: T11/T12/T13 discriminator tasks). Three-dimension rubric (behavior_class, clause_citation_present, binding_signal_present). Aggregate scoring. Evaluator blinding. |
| `deviation-and-stop-rules-DRAFT.md` | Deviation taxonomy + 8 STOP conditions (S1-S8). Operator checklist on STOP. |
| `unresolved-decisions.md` | Eight decisions requiring PI judgment (D1-D8). Defaults, risks, alternatives, PI adjudication procedure. |
| `runtime-capability-assessment.md` | Honest operator assessment: can the proposed runtime (Hermes Agent v0.21.2 / `minimax/MiniMax-M3`) actually satisfy the persistent-session requirement? YES, with caveat about context compression. Confidence levels and recommendations. |
| `README.md` (this file) | Provenance, deliverables, file order for review. |

## Recommended review order

1. `runtime-capability-assessment.md` — answers Frank's direct question first.
2. `unresolved-decisions.md` — eight decisions that gate freezing the protocol.
3. `PROTOCOL-DRAFT-v0.1.md` — the protocol itself.
4. `session-binding-evidence-spec.md` — what evidence proves the requirement.
5. `qualification-procedure-DRAFT.md` — the four mechanical checks.
6. `OPERATOR-RUNBOOK-DRAFT.md` — the operator-side procedure.
7. `proposed-task-set-and-rubric-DRAFT.md` — task set and scoring.
8. `deviation-and-stop-rules-DRAFT.md` — STOP conditions.

## What this package does NOT contain

- A frozen protocol (the SHA-256s of governing artifacts are not recorded).
- A governing CoA file (the file `governing-conditions/coa-v0.1.md` is referenced but not yet drafted; it can be drafted alongside the protocol freeze).
- An execution GO (PI has not issued one; the protocol is not executable).
- Any participant initialization or qualification execution.
- Any scored task execution.
- Any evaluator engagement.
- Any modification to COA-E1 v6.3.

## Path to a frozen v0.2 protocol

1. ChatGPT reviews this draft and proposes changes.
2. PI adjudicates the 8 unresolved decisions in `unresolved-decisions.md`.
3. PI authorizes a v0.2 freeze.
4. The freeze commit records the governing CoA file's SHA-256 and the resolved decisions.
5. Only after the freeze does the operator run qualification.
6. Only after qualification passes for both arms does the operator run scored tasks.
7. Only after both arms complete does the evaluator (blinded) score.
8. Only after scoring is complete does Frank-as-PI adjudicate the overall result.

Until step 3, this package is a discussion artifact, not a runnable protocol.

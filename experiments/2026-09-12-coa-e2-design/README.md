# COA-E2 — Successor Design Package (DRAFT v0.2)

**Status:** DRAFT v0.2 — incorporates PI adjudication on DRAFT v0.1 (commit `545b2da7`). NOT frozen. NOT executed. Awaiting ChatGPT review and a separate PI decision.
**Branch:** `feature/coa-e2-persistent-session-binding`
**Author:** Hermes (operator), per Frank-as-PI directive at 2026-09-12 (PI ADJUDICATION — COA-E2 DRAFT v0.1: REVISION_REQUIRED — NOT_READY_TO_FREEZE).
**Inheritance:** none from COA-E1 v6.3 by default; COA-E1 v6.3 evidence cited only for failure-mode grounding.
**v0.1 superseded; v0.1 docs preserved unchanged as historical record.**

## Provenance

COA-E1 v6.3 was closed as `INCONCLUSIVE_PENDING_FURTHER` per ChatGPT adjudication response `20260912T234411Z-coa-e1-v63-adjudication-response-001`. The controlling failure was session structure: eleven `--oneshot` sessions per arm instead of one persistent session per arm.

Frank's first directive (2026-09-12, "AUTHORIZE COA-E2 SUCCESSOR DESIGN ONLY") led to commit `545b2da7` (DRAFT v0.1). Frank's PI adjudication on v0.1 (2026-09-12, "REVISION_REQUIRED — NOT_READY_TO_FREEZE") issued eight PI rulings (D1-D8) and ten controlling corrections. This v0.2 commit incorporates those rulings and corrections.

## PI rulings incorporated (D1-D8)

| # | Decision | Resolution |
|---|---|---|
| D1 | Task set | Smaller fresh task set (U1..U6); T11/T12 → qualification; T13 dropped (prompted-citation test, not constraint). |
| D2 | Runner location | Stored in repo, hash-bound; verified execution copy may run from `/tmp`. |
| D3 | Per-arm MEMORY.md | New isolated profiles, deterministic blank starting state; memory-writing tools disabled if possible; any unexpected change = S10 global STOP. |
| D4 | Nonce | Required, unique per session; both arms; never in recall probe. |
| D5 | Scoring rubric | Mechanical binding qualification separate from behavioral scoring; no behavioral points for digest recall or clause citation. |
| D6 | Blinding | Evaluator receives only identically formatted scored-task material; no init packets, digests, nonces, citations, binding evidence. |
| D7 | Operator | Deterministic version-controlled runner; no model-driven operator decisions during execution. |
| D8 | Sample size | 3 independent paired sessions per arm × ~6 tasks; unit of measurement = session; no conventional significance claim. |

## Controlling corrections incorporated

- **No participant self-assertions** (`AGENT: Hermes`, "Reply with your session ID"). Identity established operator-side via CLI config, framework version, provider metadata, model metadata, profile, session records.
- **Session identity verified mechanically** from CLI output and SessionDB records.
- **Per-arm nonce** (required, unique, unpredictable); not in recall probe.
- **Symmetric qualification** (Control arm gets structurally and approximately token-matched neutral charter).
- **Four-proposition evidence model** (delivery, receipt, acknowledgment, constraint).
- **Compression is global STOP** (S9); parent/child lineage recorded for diagnosis but not scored.
- **Pre-freeze mechanical verification** of `--oneshot` → `--resume` (BLOCKING for freeze).
- **Corrected turn counts**: 1 init + 4 probes + 6 tasks = 11 turns per arm-session; 3 sessions × 2 arms = 66 total turns, 36 scored task turns.
- **Runner under version control**, hash-bound.
- **Deterministic operator** (not conversational Hermes).
- **All structural STOPs global**: no per-arm isolation, no resume-from-N, no rerun without fresh PI decision.

## Deliverables in this package (v0.2 set)

### Top-level design documents

| File | Purpose |
|---|---|
| `README.md` (this file) | Provenance, v0.2 vs v0.1 summary, deliverables, recommended review order, path to v0.3 freeze. |
| `PROTOCOL-DRAFT-v0.2.md` | The successor protocol: research question, two-arm design (symmetric), participant identity (operator-established), nonce (per session), persistent-session requirement + pre-freeze mechanical verification, four-proposition evidence model, 11 STOP conditions (all global), deterministic runner. |
| `session-binding-evidence-spec-DRAFT.md` | What evidence proves the persistent-session requirement. Operational definition of "session"; 4 evidence pieces (session_id consistency, state.db sessions row, messages table monotonic growth, no compression); audit script spec. |
| `OPERATOR-RUNBOOK-DRAFT-v0.2.md` | Operator-side procedure: pre-freeze mechanical verification (BLOCKING), pre-execution checks, initialization, qualification probes, scored task execution, multiple sessions, evidence package, STOP discipline. |
| `qualification-procedure-DRAFT-v0.2.md` | Symmetric qualification: 4 mechanical probes (Q1 digest recall, Q2 nonce recall, Q3 session_id binding, Q4 re-test). No digest/nonce in probe text. Per-session PASS/FAIL. |
| `proposed-task-set-and-rubric-DRAFT-v0.2.md` | Predeclared outcome rubric for the 6 fresh tasks (U1..U6). Scoring: behavior_class only (no binding_signal_present; per D5). Blinded evaluator input: per-task envelopes only (per D6). |
| `deviation-and-stop-rules-DRAFT-v0.2.md` | 7 deviation types + 11 STOP conditions (S1-S11). All STOPs global. |
| `audit-specification.md` | Per-proposition evidence capture; evidentiary limitation disclosure. |
| `initialization-packet-templates.md` | Symmetric packet templates for both arms; byte-identical envelopes; runner substitutes nonce + digest at execution time. |
| `four-proposition-evidence-model.md` | Foundational model: delivery, receipt, acknowledgment, constraint; per-proposition measurement; sequential gating. |
| `unresolved-decisions-resolved-v0.2.md` | PI rulings D1-D8 incorporated. Residual design questions for ChatGPT review. |
| `runtime-capability-assessment-v0.2.md` | Honest operator assessment: YES the runtime can satisfy persistent-session, with S9 compression STOP discipline. |
| `consistency-audit-v0.2.md` | Cross-document consistency check: PASS on 14 dimensions. |

### Governing artifacts

| File | Purpose |
|---|---|
| `governing-charter/coa-e2-charter-DRAFT.md` | The CoA-governed arm's charter: 6 clauses (COA-1 through COA-6), acknowledgment procedure (6 fields), recall procedure. |
| `governing-charter/control-e2-charter-DRAFT.md` | The Control arm's charter: 6 neutral clauses (COA-N1 through COA-N6), symmetric acknowledgment procedure. |

### Scored task set

| File | Purpose |
|---|---|
| `scored-tasks/task-set-DRAFT.md` | 6 fresh scored tasks (U1..U6) — safe CoA-decision-boundary situations, observable choices, no prompted-citation. |

### Runner (deterministic; under version control)

| File | Purpose |
|---|---|
| `runner/README.md` | Runner specification: design principle, file layout, pre-run verification, nonce generation, audit, per-arm session flow, multi-session, STOP records. |
| `runner/verify_hashes.py` | Pre-run hash verification (refuses to proceed on mismatch). |
| `runner/generate_nonces.py` | One-shot nonce generator (32-char hex per arm; secrets.token_hex). |
| `runner/audit_after_turn.py` | Post-turn audit: state.db read-only, session-row, messages-table, session-id-consistency, messages-count-growth, transcript-chain, compression detection. |
| `runner/freeze_manifest.json` | Recorded SHA-256s of all frozen files (populated at freeze). |

### Superseded v0.1 documents (preserved unchanged)

```
PROTOCOL-DRAFT-v0.1.md                              (historical record)
session-binding-evidence-spec.md                     (historical record)
OPERATOR-RUNBOOK-DRAFT.md                           (historical record)
qualification-procedure-DRAFT.md                    (historical record)
proposed-task-set-and-rubric-DRAFT.md               (historical record)
deviation-and-stop-rules-DRAFT.md                   (historical record)
unresolved-decisions.md                             (historical record)
runtime-capability-assessment.md                     (historical record)
```

## Recommended review order

1. `consistency-audit-v0.2.md` — PASS on 14 dimensions; this is the cross-document sanity check.
2. `unresolved-decisions-resolved-v0.2.md` — PI rulings on D1-D8; residual design questions for ChatGPT.
3. `runtime-capability-assessment-v0.2.md` — answers Frank's direct question on whether the runtime can satisfy the requirement.
4. `PROTOCOL-DRAFT-v0.2.md` — the protocol itself.
5. `four-proposition-evidence-model.md` — foundational evidence model.
6. `session-binding-evidence-spec-DRAFT.md` — what evidence proves binding.
7. `qualification-procedure-DRAFT-v0.2.md` — symmetric qualification gates.
8. `OPERATOR-RUNBOOK-DRAFT-v0.2.md` — operator-side procedure (deterministic runner).
9. `runner/README.md` + runner scripts — deterministic runner code.
10. `audit-specification.md` — audit + evidentiary limitation disclosure.
11. `governing-charter/coa-e2-charter-DRAFT.md` and `governing-charter/control-e2-charter-DRAFT.md` — the two charters.
12. `scored-tasks/task-set-DRAFT.md` — the 6 scored tasks.
13. `proposed-task-set-and-rubric-DRAFT-v0.2.md` — scoring rubric and blinding protocol.
14. `deviation-and-stop-rules-DRAFT-v0.2.md` — 11 STOP conditions (all global).
15. `initialization-packet-templates.md` — symmetric packet templates.

## What this package does NOT contain

- A frozen protocol (the SHA-256s of governing artifacts are not recorded).
- A recorded pre-freeze mechanical verification (BLOCKING for freeze; must be done before any execution).
- An execution GO (PI has not issued one).
- Any participant initialization or qualification execution.
- Any scored task execution.
- Any evaluator engagement.
- Any modification to COA-E1 v6.3.

## Path to a frozen v0.3 protocol

1. ChatGPT reviews this v0.2 draft and proposes changes.
2. PI adjudicates the residual design questions (per `unresolved-decisions-resolved-v0.2.md` §"Residual design questions").
3. PI authorizes a v0.3 freeze.
4. The freeze commit records the SHA-256s of the charter files, the task set, the four-proposition model, the session-binding spec, the qualification procedure, the deviation rules, and every file in `runner/`.
5. The freeze MUST include the recorded pre-freeze mechanical verification of `--oneshot` → `--resume` (per `OPERATOR-RUNBOOK-DRAFT-v0.2.md` §1).
6. Only after the freeze does the operator create the per-arm profiles and run qualification.
7. Only after qualification PASSes for all 6 sessions does the operator run scored tasks.
8. Only after all 6 sessions complete does the blinded evaluator score.
9. Only after scoring is complete does Frank-as-PI adjudicate the pilot's outcome.

Until step 3, this package is a discussion artifact, not a runnable protocol.

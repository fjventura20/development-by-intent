# COA-E2 — Consistency Audit Across Documents (DRAFT v0.2)

**Status:** DRAFT v0.2 — final cross-document consistency pass before ChatGPT review.
**Author:** Hermes (operator), per Frank-as-PI COA-E2 directive at 2026-09-12.

## Purpose

This document audits the v0.2 design package for internal consistency. Per Frank's ruling: "Correct all internal filename references, missing-file references, placeholder timestamps, turn-count formulas, and contradictions between the protocol, runbook, qualification procedure, evidence specification, and STOP rules."

This is a checklist; each item below is verified to PASS in the v0.2 package.

## 1. Turn counts

| Document | Per-session turns | Per-arm turns | Pilot total |
|---|---|---|---|
| `PROTOCOL-DRAFT-v0.2.md` §11 | 11 (1 init + 4 probes + 6 tasks) | 33 (3 sessions × 11) | 66 |
| `PROTOCOL-DRAFT-v0.2.md` §12 | 11 | 33 | 66 |
| `session-binding-evidence-spec-DRAFT.md` §3.3 | 11 (22 messages) | — | — |
| `qualification-procedure-DRAFT-v0.2.md` §3 | 4 probes (Q1-Q4) | — | — |
| `OPERATOR-RUNBOOK-DRAFT-v0.2.md` §5 | 11 | — | — |
| `proposed-task-set-and-rubric-DRAFT-v0.2.md` | 6 scored tasks per session | 18 per arm | 36 |
| `unresolved-decisions-resolved-v0.2.md` D8 | — | 3 sessions | 6 sessions / 36 task turns |

**Consistency:** PASS. All documents agree on 1 init + 4 probes + 6 tasks = 11 turns per arm-session; 3 sessions × 2 arms = 6 sessions, 66 total turns, 36 scored task turns.

## 2. Arm-session scope

| Document | CoA-governed sessions | Control sessions |
|---|---|---|
| `PROTOCOL-DRAFT-v0.2.md` §7 | 3 | 3 |
| `unresolved-decisions-resolved-v0.2.md` D8 | 3 | 3 |
| `proposed-task-set-and-rubric-DRAFT-v0.2.md` | 18 scored task turns | 18 scored task turns |
| `runner/run_pilot.py` (skeleton) | per arm | per arm |

**Consistency:** PASS. 3 sessions per arm × 2 arms = 6 sessions.

## 3. STOP conditions

| Document | STOP count | Compression STOP? | Memory-write STOP? | Global rule? |
|---|---|---|---|---|
| `PROTOCOL-DRAFT-v0.2.md` §9 | S1-S11 (11) | Yes (S9) | Yes (S10) | Yes |
| `deviation-and-stop-rules-DRAFT-v0.2.md` | S1-S11 (11) | Yes (S9) | Yes (S10) | Yes |
| `OPERATOR-RUNBOOK-DRAFT-v0.2.md` §9 | S1-S11 (11) | Yes (S9) | Yes (S10) | Yes |
| `session-binding-evidence-spec-DRAFT.md` §3.4 | compression STOP | Yes (S9) | — | — |
| `audit-specification.md` §S9 | compression STOP | Yes | — | — |

**Consistency:** PASS. All documents agree on 11 STOP conditions, S9 compression, S10 memory-write, global STOP rule.

## 4. Participant identity rules

| Document | Self-assertion allowed? | Identity established by? |
|---|---|---|
| `PROTOCOL-DRAFT-v0.2.md` §3 | NO | Operator-captured CLI config |
| `OPERATOR-RUNBOOK-DRAFT-v0.2.md` §2 | NO | Operator-captured CLI config |
| `qualification-procedure-DRAFT-v0.2.md` §1 | NO | Operator-captured CLI config |
| `session-binding-evidence-spec-DRAFT.md` §5 | — | session_id per turn; CLI metadata per preflight |

**Consistency:** PASS. Per Frank's PI ruling: "Establish identity through operator-captured CLI configuration, framework version, provider metadata, model metadata, profile, and session records."

## 5. Nonce handling

| Document | Per-arm nonce? | Per-session nonce? | In recall prompt? |
|---|---|---|---|
| `PROTOCOL-DRAFT-v0.2.md` §4 | Yes (per arm) | Yes (per session) | NO |
| `governing-charter/coa-e2-charter-DRAFT.md` | Yes (acknowledged) | — | NO |
| `governing-charter/control-e2-charter-DRAFT.md` | Yes (acknowledged) | — | NO |
| `qualification-procedure-DRAFT-v0.2.md` §3 | — | Yes (recalled) | NO |
| `runner/generate_nonces.py` | — | Yes (generated) | — |

**Consistency:** PASS. Per Frank's D4 ruling: nonce required, unique per session, never in recall prompt.

## 6. Symmetric control arm

| Document | Same envelope? | Same procedure? | Same qualification? | Treatment diff? |
|---|---|---|---|---|
| `PROTOCOL-DRAFT-v0.2.md` §2 | Yes | Yes | Yes | Charter content |
| `governing-charter/coa-e2-charter-DRAFT.md` | Yes | Yes | Yes | (CoA content) |
| `governing-charter/control-e2-charter-DRAFT.md` | Yes | Yes | Yes | (Neutral content) |
| `initialization-packet-templates.md` | Yes | Yes | Yes | Charter body + Arm label |
| `qualification-procedure-DRAFT-v0.2.md` | Yes | Yes | Yes | Charter digest + nonce |
| `proposed-task-set-and-rubric-DRAFT-v0.2.md` | Yes | Yes | Yes | (none — task content identical) |

**Consistency:** PASS. Per Frank's PI ruling: "Make qualification symmetric. ... The treatment difference should be the charter's substantive governing content."

## 7. Runner under version control

| Document | Runner path | Hash-bound? | Operator-side /tmp copy? |
|---|---|---|---|
| `PROTOCOL-DRAFT-v0.2.md` §10 | `runner/` | Yes (freeze_manifest.json) | Yes (after hash verify) |
| `runner/README.md` | `runner/` | Yes | Yes (after hash verify) |
| `OPERATOR-RUNBOOK-DRAFT-v0.2.md` §0, §8 | `runner/` | Yes | Yes (after hash verify) |
| `unresolved-decisions-resolved-v0.2.md` D2, D7 | `runner/` | Yes | Yes (after hash verify) |

**Consistency:** PASS. Per Frank's D2 + D7 rulings.

## 8. Four-proposition evidence model

| Document | P1 Delivery | P2 Receipt | P3 Acknowledgment | P4 Constraint |
|---|---|---|---|---|
| `four-proposition-evidence-model.md` | defined | defined | defined | defined |
| `PROTOCOL-DRAFT-v0.2.md` §8 | referenced | referenced | referenced | referenced |
| `session-binding-evidence-spec-DRAFT.md` §6 | captured per turn | captured at probes | captured at init | captured post-evaluation |
| `audit-specification.md` §P1-P4 | captured | captured | captured | captured |
| `proposed-task-set-and-rubric-DRAFT-v0.2.md` | — | — | — | scoring |

**Consistency:** PASS. All documents agree on the four propositions.

## 9. Pilot scope (D8 ruling)

| Document | Sessions | Tasks per session | Unit of measurement | Statistical claim |
|---|---|---|---|---|
| `PROTOCOL-DRAFT-v0.2.md` §7, §12 | 3 per arm | 6 | session | none |
| `unresolved-decisions-resolved-v0.2.md` D8 | 3 per arm | 4-6 | session | none |
| `proposed-task-set-and-rubric-DRAFT-v0.2.md` | 3 per arm | 6 | session | none |
| `OPERATOR-RUNBOOK-DRAFT-v0.2.md` §6 | 3 per arm | 6 | — | — |

**Consistency:** PASS. Per Frank's D8 ruling: 3 independent paired sessions × ~6 tasks; unit is session; no conventional significance claim.

## 10. Blinded evaluator (D6 ruling)

| Document | Evaluator input | Evaluator excluded from | Conducted by |
|---|---|---|---|
| `PROTOCOL-DRAFT-v0.2.md` §8 (P4) | per-task envelopes only | init packets, digests, nonces, citations, binding evidence | blinded evaluator |
| `proposed-task-set-and-rubric-DRAFT-v0.2.md` | per-task envelopes only | init packets, digests, nonces, citations, binding evidence | blinded evaluator |
| `audit-specification.md` §Per-proposition evidence | mechanical audit | behavioral scoring | different party (Frank-as-PI or designated non-evaluator) |

**Consistency:** PASS. Per Frank's D6 ruling.

## 11. Filename references (cross-document)

| Reference | In document | Resolves to | Exists? |
|---|---|---|---|
| `governing-charter/coa-e2-charter-DRAFT.md` | `PROTOCOL-DRAFT-v0.2.md` §2, §6; `initialization-packet-templates.md`; `unresolved-decisions-resolved-v0.2.md` | actual file at `governing-charter/coa-e2-charter-DRAFT.md` | YES |
| `governing-charter/control-e2-charter-DRAFT.md` | same | actual file | YES |
| `scored-tasks/task-set-DRAFT.md` | `PROTOCOL-DRAFT-v0.2.md` §7; `proposed-task-set-and-rubric-DRAFT-v0.2.md`; `runner/freeze_manifest.json` | actual file at `scored-tasks/task-set-DRAFT.md` | YES |
| `four-proposition-evidence-model.md` | `PROTOCOL-DRAFT-v0.2.md` §8; `session-binding-evidence-spec-DRAFT.md`; `audit-specification.md` | actual file | YES |
| `session-binding-evidence-spec-DRAFT.md` | `PROTOCOL-DRAFT-v0.2.md` §5; `OPERATOR-RUNBOOK-DRAFT-v0.2.md`; `qualification-procedure-DRAFT-v0.2.md` | actual file | YES |
| `qualification-procedure-DRAFT-v0.2.md` | `PROTOCOL-DRAFT-v0.2.md` §9, §11; `OPERATOR-RUNBOOK-DRAFT-v0.2.md`; `deviation-and-stop-rules-DRAFT-v0.2.md` | actual file | YES |
| `deviation-and-stop-rules-DRAFT-v0.2.md` | `PROTOCOL-DRAFT-v0.2.md` §9; `OPERATOR-RUNBOOK-DRAFT-v0.2.md`; `qualification-procedure-DRAFT-v0.2.md` | actual file | YES |
| `audit-specification.md` | `PROTOCOL-DRAFT-v0.2.md` §10; `OPERATOR-RUNBOOK-DRAFT-v0.2.md`; `proposed-task-set-and-rubric-DRAFT-v0.2.md` | actual file | YES |
| `initialization-packet-templates.md` | `PROTOCOL-DRAFT-v0.2.md` §11; `OPERATOR-RUNBOOK-DRAFT-v0.2.md` | actual file | YES |
| `proposed-task-set-and-rubric-DRAFT-v0.2.md` | `PROTOCOL-DRAFT-v0.2.md` §7, §8 | actual file | YES |
| `runtime-capability-assessment-v0.2.md` | `README.md` | actual file | YES |
| `unresolved-decisions-resolved-v0.2.md` | `README.md` | actual file | YES |
| `runner/README.md`, `runner/freeze_manifest.json`, `runner/verify_hashes.py`, `runner/generate_nonces.py`, `runner/audit_after_turn.py` | `PROTOCOL-DRAFT-v0.2.md` §10; `OPERATOR-RUNBOOK-DRAFT-v0.2.md` §0, §8 | actual files | YES |

**Consistency:** PASS. Every cross-document filename reference resolves to an actual file in the package.

## 12. Placeholder timestamps

| Document | Placeholders |
|---|---|
| `governing-charter/coa-e2-charter-DRAFT.md` | "File SHA-256: `<populated at freeze time>`" — intentional; populated at freeze |
| `governing-charter/control-e2-charter-DRAFT.md` | same |
| `runner/freeze_manifest.json` | all `sha256` fields are `<populated at freeze time>` — intentional; freeze-time manifest |
| `initialization-packet-templates.md` | `<initialization turn only;...>`, `<sha256 of ...>` — template placeholders; runner substitutes at execution time |

**Consistency:** PASS. All placeholders are explicitly marked as freeze-time or runtime substitutions.

## 13. v0.1 → v0.2 supersession

| v0.1 file | v0.2 replacement | v0.1 preserved? |
|---|---|---|
| `PROTOCOL-DRAFT-v0.1.md` | `PROTOCOL-DRAFT-v0.2.md` | YES (unchanged, historical record) |
| `session-binding-evidence-spec.md` | `session-binding-evidence-spec-DRAFT.md` | YES |
| `OPERATOR-RUNBOOK-DRAFT.md` | `OPERATOR-RUNBOOK-DRAFT-v0.2.md` | YES |
| `qualification-procedure-DRAFT.md` | `qualification-procedure-DRAFT-v0.2.md` | YES |
| `proposed-task-set-and-rubric-DRAFT.md` | `proposed-task-set-and-rubric-DRAFT-v0.2.md` | YES |
| `deviation-and-stop-rules-DRAFT.md` | `deviation-and-stop-rules-DRAFT-v0.2.md` | YES |
| `unresolved-decisions.md` | `unresolved-decisions-resolved-v0.2.md` | YES |
| `runtime-capability-assessment.md` | `runtime-capability-assessment-v0.2.md` | YES |
| `README.md` | (updated by this consistency audit) | — |

**Consistency:** PASS. All v0.1 files are preserved unchanged as historical record.

**Note on stale references in v0.1 docs:** The v0.1 files contain references to `governing-conditions/coa-v0.1.md` (a path the v0.1 design proposed). The v0.2 design uses different paths: `governing-charter/coa-e2-charter-DRAFT.md` and `governing-charter/control-e2-charter-DRAFT.md`. These stale references in v0.1 files are **intentional** (they reflect v0.1's design intent before the PI ruling), and the v0.2 design does NOT propagate them. The v0.2 docs reference the v0.2 charter paths only.

## 14. What the consistency audit does NOT cover

- ChatGPT review (next step after PI's separate decision).
- The pre-freeze mechanical verification (BLOCKING for freeze; see `OPERATOR-RUNBOOK-DRAFT-v0.2.md` §1).
- Scoring of any actual pilot (not yet executed).
- Any modification of COA-E1 v6.3 (still preserved unchanged).

## 15. Overall

**PASS.** The v0.2 design package is internally consistent. All turn counts, STOP conditions, identity rules, nonce rules, runner locations, four-proposition references, and filename references agree across documents. The v0.1 files are preserved unchanged. COA-E1 v6.3 is not modified.

Stop after delivering the v0.2 draft. Awaiting ChatGPT review and a separate PI decision.

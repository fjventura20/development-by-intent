# Behavioral Portability — Evidence Ledger

**Purpose:** maintain a compact, auditable record of evidence relevant to the Behavioral Portability hypothesis.  
**Last updated:** 2026-08-26

This ledger deliberately separates preregistered experiments from observational demonstrations. A recognizable reconstruction is useful evidence, but it is not automatically equivalent to a clean-room, frozen-rubric replication.

## Evidence levels

- **Preregistered replication** — artifact set, isolation rules, tests, scoring, and failure rules frozen before execution; raw evidence preserved.
- **Controlled experiment** — meaningful controls and preserved outputs, but one or more preregistration or isolation/evidence elements are weaker.
- **Observational demonstration** — real reconstruction occurred and artifacts/outputs are available, but the run was not designed as a formal test.
- **Hypothesis only** — plausible implication not yet directly tested.

## Current ledger

| ID | Application | Source → target | Preservation input | Evidence level | Result | Main limitation |
|---|---|---|---|---|---|---|
| BP-AB-CHATGPT-001 | Amazing Birthday | ChatGPT → fresh ChatGPT environment | Frozen behavioral baseline + reconstruction prompt | Preregistered replication | **PASS — 60/60** | Same provider |
| BP-AB-CLAUDE-OBS-001 | Amazing Birthday | ChatGPT-origin artifacts → Claude | Original transcript + durability package | Observational demonstration | Recognizable reconstruction | Not preregistered |
| BP-AB-GROK-OBS-001 | Amazing Birthday | ChatGPT-origin artifacts → Grok | Original transcript + durability package | Observational demonstration | **Preliminary behavioral PASS** | Not preregistered; factual regression not independently verified |
| BP-AB-CLAUDE-EXP-001 | Amazing Birthday | Frozen package → fresh Claude, operated by Hermes | Frozen behavioral baseline + reconstruction prompt | Preregistered design; execution evidence defect | **INDETERMINATE formal / strong behavioral PASS signal** | First reconstruction and Test 1 were not captured immutably on first invocation |
| BP-AB-CLAUDE-REP-002 | Amazing Birthday | Same frozen package → fresh Claude, operated by Hermes | Same two artifacts; identical tests/rubric | Preregistered clean replication | **PASS — independent 19/20, 19/20, 17/20** | Single application and Claude target; factual variance remains |

## BP-AB-CHATGPT-001 — artifact-only clean-room reconstruction

Record: [`experiments/2026-08-24-amazing-birthday-clean-room-001/`](experiments/2026-08-24-amazing-birthday-clean-room-001/)

A fresh ChatGPT environment received only the frozen behavioral baseline and reconstruction prompt. Reconstruction was frozen before testing. Three withheld dates ran without repair, clarification, hints, or regeneration. All three first outputs passed the frozen v1.0 rubric for 60/60.

Supported claim:

> In the recorded ChatGPT environment, the frozen artifact-only package preserved enough Amazing Birthday behavioral identity to satisfy the preregistered criteria on new inputs.

## BP-AB-CLAUDE-OBS-001 — Claude generated implementation

Claude received Amazing Birthday source material and a durability package and selected a code-generating implementation path. The application was recognizable as Amazing Birthday. This is evidence for implementation divergence, but the run was not preregistered against the frozen three-test protocol.

## BP-AB-GROK-OBS-001 — Grok platform-native reconstruction

Record: [`experiments/2026-08-25-amazing-birthday-grok-reconstruction-001/`](experiments/2026-08-25-amazing-birthday-grok-reconstruction-001/)

Grok autonomously selected a platform-native skill structure and produced recognizable Amazing Birthday behavior. The stored assessment is a preliminary behavioral pass. The run was observational, not a preregistered clean-room replication.

## BP-AB-CLAUDE-EXP-001 — Hermes-operated Claude preregistered experiment

Record: [`experiments/2026-08-25-amazing-birthday-hermes-operated-claude-001/`](experiments/2026-08-25-amazing-birthday-hermes-operated-claude-001/)

Hermes ran a fresh Claude Code 2.1.170 session using `claude-sonnet-4-6`, with only the two frozen Phase A artifacts and no target tools. All three withheld outputs showed passing behavior. However, the true first reconstruction response and true first Test 1 response were not immutably captured on first invocation; prompts were re-issued for disk capture. The independent formal disposition therefore remains **INDETERMINATE**, with a strong behavioral PASS signal.

## BP-AB-CLAUDE-REP-002 — clean evidence-capture replication

Record: [`experiments/2026-08-25-amazing-birthday-hermes-operated-claude-replication-002/`](experiments/2026-08-25-amazing-birthday-hermes-operated-claude-replication-002/)

Request transfer: `20260826T002800Z-behavioral-portability-claude-replication-002`.  
Result transfer: `20260826T013000Z-behavioral-portability-claude-replication-002-result-001`.

Replication 002 held the application, frozen source, target artifacts, Claude target family, no-tools isolation posture, freeze rule, tests, rubric, and no-repair rule constant. It changed only the evidence procedure.

Execution evidence shows:

- frozen source commit fetched before target launch;
- both Phase A hashes verified byte-for-byte before launch;
- fresh Claude session `b1f41015-a416-44cc-b5eb-35abc83274de`;
- target denied read/write/shell/web tools;
- reconstruction plus all three tests captured atomically on first invocation via `tee`;
- no prompt re-issued for capture;
- no material contamination or repair documented.

Hermes preliminary score: 20/20 on all three; operator disposition PASS.

ChatGPT independent score:

- November 9, 1989: **19/20 PASS**;
- February 29, 1960: **19/20 PASS**;
- June 23, 1956: **17/20 PASS**;
- exact-date integrity: PASS all three;
- generalization: PASS all three;
- experiment disposition: **PASS**.

Independent scoring preserves several factual-care disagreements. Test 1 incorrectly frames November 9 as a deliberately selected symbolic Wall-opening date; Test 2 incorrectly calls Squaw Valley 1960 the first televised Winter Olympics and overstates 1960 as the beginning of U.S. military involvement in Vietnam; Test 3 contains several explicit age-calculation errors in its lifetime arc. None causes a critical-requirement failure, and all three outputs remain at or above the frozen 17-point PASS threshold.

Supported bounded claim:

> In the recorded fresh Claude Code environment, the frozen two-artifact Amazing Birthday package reconstructed behavior that passed the preregistered v1.0 rubric on all three withheld inputs, with immutable first-call evidence and no human repair.

This is the first clean preregistered cross-provider PASS in the current Amazing Birthday evidence series.

## Current support for Behavioral Portability

The evidence now supports a stronger but still bounded statement:

> Governed Amazing Birthday behavioral intent has survived artifact-only reconstruction in a fresh same-provider environment and in a fresh Claude target under a preregistered clean-room protocol. The Claude replication passed all three withheld tests with immutable first-call evidence despite substantial prose variance and some factual-care errors.

This supports Behavioral Portability for this application across the recorded ChatGPT-origin → Claude boundary. It does not establish universal portability across providers, models, upgrades, or application classes.

## Highest-value unresolved questions

1. Does the same frozen package pass on a different provider family such as Gemini under the same clean protocol?
2. How much run-to-run variance appears under identical reconstruction conditions, especially in factual care?
3. Does a durability package outperform the original transcript alone as a portability input?
4. Which durability-package components are necessary versus redundant?
5. Does Behavioral Portability survive decision-oriented, stateful, structured-data, tool-dependent, and process-cluster applications?

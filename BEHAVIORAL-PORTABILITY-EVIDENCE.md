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
| BP-AB-GEMINI-003 | Amazing Birthday | Same frozen package → fresh Gemini, operated by Hermes | Same two artifacts; same v1.0 tests/rubric | Preregistered cross-provider-family replication | **TRANSPORT REJECTED; corrected retry ACTIVE** | Original protocol-v0.2 manifest omitted required `files`; Gemini was not invoked |

## BP-AB-CHATGPT-001 — artifact-only clean-room reconstruction

Record: [`experiments/2026-08-24-amazing-birthday-clean-room-001/`](experiments/2026-08-24-amazing-birthday-clean-room-001/)

A fresh ChatGPT environment received only the frozen behavioral baseline and reconstruction prompt. Reconstruction was frozen before testing. Three withheld dates ran without repair, clarification, hints, or regeneration. All three first outputs passed the frozen v1.0 rubric for 60/60.

## BP-AB-CLAUDE-OBS-001 — Claude generated implementation

Claude received Amazing Birthday source material and a durability package and selected a code-generating implementation path. The application was recognizable as Amazing Birthday. This is evidence for implementation divergence, but the run was not preregistered against the frozen three-test protocol.

## BP-AB-GROK-OBS-001 — Grok platform-native reconstruction

Record: [`experiments/2026-08-25-amazing-birthday-grok-reconstruction-001/`](experiments/2026-08-25-amazing-birthday-grok-reconstruction-001/)

Grok autonomously selected a platform-native skill structure and produced recognizable Amazing Birthday behavior. The stored assessment is a preliminary behavioral pass. The run was observational, not a preregistered clean-room replication.

## BP-AB-CLAUDE-EXP-001 — first Hermes-operated Claude experiment

Record: [`experiments/2026-08-25-amazing-birthday-hermes-operated-claude-001/`](experiments/2026-08-25-amazing-birthday-hermes-operated-claude-001/)

Hermes ran a fresh Claude Code session with only the two frozen Phase A artifacts and no target tools. All three withheld outputs showed passing behavior. However, the true first reconstruction response and true first Test 1 response were not immutably captured on first invocation; prompts were re-issued for disk capture. The independent formal disposition therefore remains **INDETERMINATE**, with a strong behavioral PASS signal.

## BP-AB-CLAUDE-REP-002 — clean evidence-capture replication

Record: [`experiments/2026-08-25-amazing-birthday-hermes-operated-claude-replication-002/`](experiments/2026-08-25-amazing-birthday-hermes-operated-claude-replication-002/)

Request transfer: `20260826T002800Z-behavioral-portability-claude-replication-002`.  
Result transfer: `20260826T013000Z-behavioral-portability-claude-replication-002-result-001`.

Replication 002 held the application, frozen source, target artifacts, Claude target family, no-tools isolation posture, freeze rule, tests, rubric, and no-repair rule constant. It changed only the evidence procedure.

Execution evidence shows frozen-source/hash verification before launch, one fresh Claude session, no target tools, atomic first-call capture for reconstruction plus all three tests, no capture re-issue, and no material contamination or repair.

Hermes preliminary score: 20/20 on all three; operator disposition PASS.

ChatGPT independent score:

- November 9, 1989: **19/20 PASS**;
- February 29, 1960: **19/20 PASS**;
- June 23, 1956: **17/20 PASS**;
- exact-date integrity: PASS all three;
- generalization: PASS all three;
- experiment disposition: **PASS**.

Independent factual-care deductions preserve scorer disagreement: the Test 1 symbolic-date claim is misleading; Test 2 incorrectly identifies Squaw Valley 1960 as the first televised Winter Olympics and overstates 1960 as the beginning of U.S. military involvement in Vietnam; Test 3 contains multiple explicit age-calculation errors. None breaks either critical requirement, and all three outputs remain at or above the frozen PASS threshold.

Supported bounded claim:

> In the recorded fresh Claude Code environment, the frozen two-artifact Amazing Birthday package reconstructed behavior that passed the preregistered v1.0 rubric on all three withheld inputs, with immutable first-call evidence and no human repair.

## BP-AB-GEMINI-003 — provider-family portability test

Record: [`experiments/2026-08-25-amazing-birthday-hermes-operated-gemini-003/`](experiments/2026-08-25-amazing-birthday-hermes-operated-gemini-003/)

Original live protocol-v0.2 transfer: `20260826T023700Z-behavioral-portability-gemini-003`.

At `2026-08-26T11:43:21Z`, the exchange rejected that inbound package before Hermes/Gemini execution because its manifest omitted the required top-level `files` inventory. The raw response reports `status: REJECTED`, `hermes_exit_code: null`, and `manifest missing required field: files`.

This is recorded as an **infrastructure/protocol packaging failure**, not as PASS/PARTIAL/FAIL/INDETERMINATE/BLOCKED behavioral evidence. No Gemini invocation occurred and there is nothing to score under the frozen rubric.

Raw rejection evidence is preserved in the experiment's `raw/` directory. The failure is not erased or substituted by a later run.

A transport-corrected retry was separately preregistered before dispatch in `RETRY-001.md`. The only change is exchange packaging: the manifest now contains the required `files` inventory and SHA-256 hashes. Scientific variables remain frozen.

Corrected retry transfer: `20260826T123000Z-behavioral-portability-gemini-003-retry-001` — **ACTIVE / READY on `mailbox/main`** at last inspection.

The run must still return **BLOCKED** without experimental target execution if Hermes cannot demonstrate, using existing credentials only:

- installed Gemini CLI and existing non-interactive authentication;
- fresh target context without unrelated Gemini memory/context;
- supported full system-prompt override;
- genuine no-tools target (not merely sandboxed tools);
- pre-launch frozen-source and Phase A hash verification;
- exact model identifier frozen before reconstruction.

No login/OAuth, new API key, purchase, subscription change, weakened isolation, or provider substitution is permitted.

## Current support for Behavioral Portability

The evidence supports a strong but bounded statement:

> Governed Amazing Birthday behavioral intent has survived artifact-only reconstruction in a fresh same-provider environment and in a fresh Claude target under a preregistered clean-room protocol. The clean Claude replication passed all three withheld tests with immutable first-call evidence despite substantial prose variance and factual-care errors.

This supports Behavioral Portability for this application across the recorded ChatGPT-origin → Claude boundary. The Gemini provider-family question remains unresolved because the first Gemini transfer failed at exchange validation before target execution; the transport-corrected retry is active.

It remains premature to claim universal portability across providers, models, upgrades, or application classes.

## Highest-value unresolved questions

1. Does the same frozen package pass on Gemini under the same clean protocol?
2. How much run-to-run variance appears under identical reconstruction conditions, especially in factual care?
3. Does a durability package outperform the original transcript alone as a portability input?
4. Which durability-package components are necessary versus redundant?
5. Does Behavioral Portability survive decision-oriented, stateful, structured-data, tool-dependent, and process-cluster applications?

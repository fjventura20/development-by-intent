# Behavioral Portability — Evidence Ledger

**Purpose:** maintain a compact, auditable record of evidence relevant to the Behavioral Portability hypothesis.  
**Last updated:** 2026-08-28

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
| BP-AB-GEMINI-003 | Amazing Birthday | Same frozen package → intended fresh Gemini, operated by Hermes | Same two artifacts; same v1.0 tests/rubric | Preregistered cross-provider-family replication | **BLOCKED at preflight — no Gemini invocation** | Required Gemini CLI absent on Hermes host; protocol forbade installing or substituting runtime |
| BP-AB-TRANSCRIPT-CLAUDE-004 | Amazing Birthday | Frozen canonical transcript → fresh Claude, operated by Hermes | Canonical development transcript only | Preregistered transcript-only experiment | **INDETERMINATE formal / strong behavioral PASS signal** | First-call capture defect: Test 2 and Test 3 raw envelopes truncated at 8,192 bytes |
| BP-AB-TRANSCRIPT-CLAUDE-REP-005 | Amazing Birthday | Same frozen canonical transcript → fresh Claude, operated by Hermes | Canonical development transcript only | Preregistered capture-corrected replication | **INDETERMINATE formal / independent behavioral 19/20, 18/20, 17/20** | Clean capture, but preregistered reconstruction-readiness freeze was not reached before testing |

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

Hermes preliminary score: **20/20, 20/20, 20/20**; operator disposition PASS.

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

Original protocol-v0.2 transfer: `20260826T023700Z-behavioral-portability-gemini-003`.

At `2026-08-26T11:43:21Z`, the exchange rejected that inbound package before Hermes/Gemini execution because its manifest omitted the required top-level `files` inventory. This first failure is an infrastructure/protocol packaging failure, not behavioral evidence. No Gemini invocation occurred.

A transport-corrected retry was separately preregistered before dispatch as `20260826T123000Z-behavioral-portability-gemini-003-retry-001`. The retry reached Hermes and completed preregistered preflight. Hermes stopped with substantive disposition **BLOCKED** because the host did not have a Gemini CLI binary installed. The protocol prohibited installing a missing prerequisite, initiating login/OAuth, creating a key, purchasing/changing a subscription, weakening isolation, or substituting a different Gemini access path.

No Gemini target invocation occurred. No reconstruction or withheld test was sent to a model. No behavioral score is assigned. The correct experimental disposition is **BLOCKED**.

## BP-AB-TRANSCRIPT-CLAUDE-004 — transcript-only comparison

Record: [`experiments/2026-08-26-amazing-birthday-transcript-only-claude-004/`](experiments/2026-08-26-amazing-birthday-transcript-only-claude-004/)

Transfer: `20260826T204100Z-behavioral-portability-transcript-only-claude-004`.

004 changed the preservation input relative to clean replication 002: the target received only the frozen canonical development transcript. Claude target family/model, no-tools posture, withheld tests, rubric, no-repair rule, and comparator were held fixed as closely as practicable.

The run produced strong visible behavioral output, and Hermes scored the three tests **20/20, 20/20, 20/20** on visible content. However, the operator-side capture pipeline truncated the first-call Test 2 and Test 3 raw JSON envelopes at exactly 8,192 bytes. Under the preregistered first-call rule, truncated first-call evidence cannot be replaced by a later re-issue. The formal disposition is therefore **INDETERMINATE**, not PASS.

This result motivated a preregistered capture-discipline replication rather than a silent repair.

## BP-AB-TRANSCRIPT-CLAUDE-REP-005 — capture-corrected transcript-only replication

Record: [`experiments/2026-08-27-amazing-birthday-transcript-only-claude-replication-005/`](experiments/2026-08-27-amazing-birthday-transcript-only-claude-replication-005/)

005 held the 004 scientific design fixed and changed only capture discipline. Direct shell redirection replaced the `tee | head` pipeline; every first-call raw envelope passed `jq empty`, size, 8-KiB-boundary, and SHA-256 gates. The capture defect from 004 is therefore eliminated.

Hermes operator score/disposition:

- November 9, 1989: **20/20**;
- February 29, 1960: **20/20**;
- June 23, 1956: **20/20**;
- operator experiment disposition: **PASS**.

ChatGPT independent behavioral score:

- November 9, 1989: **19/20 PASS-strength**;
- February 29, 1960: **18/20 PASS-strength**;
- June 23, 1956: **17/20 PASS-strength**.

Scorer disagreement is preserved. The formal disposition is nevertheless **INDETERMINATE**, because independent review found a preregistered execution defect before testing: the freeze rule required the target to reconstruct reusable behavior and **state readiness for testing**. The first reconstruction response instead attempted a `Write` tool call. The no-tools posture correctly denied it, and the target then asked for operator approval to save the transcript before it would confirm readiness. No approval or repair was supplied, but the operator proceeded directly to the withheld tests.

The denied tool call did not execute and therefore is not contamination. It is, however, material evidence that the raw historical transcript contained an operational instruction that the target interpreted as a current command. The preregistered readiness/freeze state was never reached, and later passing test outputs cannot retroactively establish that freeze.

Independent review: [`results/score-independent.md`](experiments/2026-08-27-amazing-birthday-transcript-only-claude-replication-005/results/score-independent.md).

Bounded interpretation:

> The canonical transcript alone produced PASS-strength Amazing Birthday behavior on all three clean first-call withheld triggers in the recorded fresh Claude Sonnet 4-6 session, but it has not yet produced a clean formal transcript-only PASS under the frozen reconstruction-readiness protocol.

This identifies a concrete transcript-only hazard that the structured durability package did not exhibit in replication 002: **historical operational instructions can be treated as live commands instead of merely as evidence from which to reconstruct behavior.**

## BP-AB-TRANSCRIPT-CLAUDE-REP-006 — formal transcript-only PASS

Record: [`experiments/2026-08-27-amazing-birthday-transcript-only-claude-replication-006/`](experiments/2026-08-27-amazing-birthday-transcript-only-claude-replication-006/)

Replication 006 corrected the reconstruction-freeze defect from 005 without changing the withheld test set or frozen rubric. The target reached an explicit clean readiness state, no prohibited historical instruction was executed, captures were complete, and all three first-call outputs met the frozen 17/20 threshold.

ChatGPT's delivered independent review reported **19/20, 18/20, 17/20**. Frank's external factual audit found additional factual-care errors involving the USSR dissolution timing and Woodstock date. The Frank-as-PI adjudication records the project result as **17/20, 18/20, 17/20 = 52/60**. The formal PASS remains because each output is at or above 17, but the evidentiary strength is weaker than the original 54/60 headline.

Bounded conclusion: transcript-only behavioral recovery formally passed for Amazing Birthday in the recorded Claude Sonnet 4.6 environment. This does not show that transcripts are sufficient generally or that durability packages add no value.

## BP-RO-ARTIFACT-ONLY-CLAUDE-001 — stateful functional recovery

Record: [`experiments/2026-08-27-receipt-organizer-artifact-only-claude-001/`](experiments/2026-08-27-receipt-organizer-artifact-only-claude-001/)

Receipt Organizer reconstructed from the frozen artifact package and received an independent **24/24 functional PASS**. Receipt ingestion, normalization, deduplication, query behavior, and state retention across nine turns were demonstrated.

The causal status remains **PROVISIONAL**. Without thin-description and concise-contract controls, the experiment cannot establish what the durability package contributed beyond the target model's capability and the reconstruction instruction.

The source corpus is preserved under [`archive/canonical/receipt-organizer/`](archive/canonical/receipt-organizer/). The archive keeps the verbatim Claude Code transcript, reconstructed ChatGPT transcript, and derived reconstruction prompt separate and hash-bound.

## BP-AB-ABLATION-002 and 003 — causal package test

Ablation 002 produced no scientific result. Its execution defects were preserved, and its birthday dates were withdrawn.

Ablation 003 is the clean replacement. It freezes three conditions—thin description, concise behavioral contract, and artifact-only durability package—in one controlled Claude Sonnet 4.6 environment with five fresh birthday tests. Its immutable snapshot received an independent **FREEZE_REVIEW: PASS** on 2026-08-28. No condition may execute until a separate GO confirms the externally bound snapshot, evaluator availability, wrapper/capture readiness, and unchanged controlled environment.

## Current support for Behavioral Portability

The evidence supports the following bounded statements:

1. Amazing Birthday behavior has survived reconstruction in fresh ChatGPT and Claude environments under frozen behavioral tests.
2. Transcript-only Amazing Birthday recovery reached a formal PASS in one controlled Claude Sonnet 4.6 run, although factual-care errors remained.
3. Receipt Organizer achieved a 24/24 stateful functional reconstruction, including nine-turn ledger retention.
4. Observational Claude and Grok reconstructions show implementation diversity, but they are weaker than preregistered replications.
5. The evidence does not yet establish that a full durability package outperforms a thin description or concise behavioral contract.

The active causal question is therefore not whether reconstruction can occur. It is **what preserved information causes the recovered behavior**.

## Decision gate

BP-AB-ABLATION-003 controls the next research step:

- If Condition C materially outperforms Conditions A and B, the durability-package thesis gains bounded causal support.
- If all conditions perform similarly, recovery in this application may be dominated by target-model competence rather than package content.
- Either result narrows the theory and determines the Receipt Organizer ablation design.

## Highest-value unresolved questions

1. What does the Amazing Birthday durability package add beyond a thin description and concise behavioral contract?
2. Does the same causal pattern hold for stateful Receipt Organizer behavior?
3. Does behavioral portability survive a second controlled provider family?
4. How much run-to-run and model-version variance appears under identical conditions?
5. Where is the safe applicability boundary for persistent state, tools, external side effects, transactions, and high-assurance applications?
6. Does Development by Intent materially reduce development and modification effort against a matched conventional implementation?

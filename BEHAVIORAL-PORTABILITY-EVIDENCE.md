# Behavioral Portability — Evidence Ledger

**Purpose:** maintain a compact, auditable record of evidence relevant to the Behavioral Portability hypothesis.  
**Last updated:** 2026-08-25

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

### Frozen design

- Hermes = operator; Claude = reconstruction target; ChatGPT = independent reviewer.
- Fresh isolated Claude environment.
- Before freeze Claude receives only `03-behavioral-baseline.md` and `RECONSTRUCTION-PROMPT.md` from frozen source commit `c369215024c9f8a849daf11bd4b872d7ee566a7a`.
- Test dates and rubric withheld until freeze.
- Tests: Nov 9 1989; Feb 29 1960; Jun 23 1956.
- First outputs are evidence; no repair/regeneration.
- PASS requires all three outputs to pass and no material contamination/repair.
- INDETERMINATE applies when isolation, evidence capture, or execution defects prevent reliable interpretation.

### Transport record

- Initial transfer `20260825T205300Z-behavioral-portability-001` was mistakenly staged on repository default `main` and did not reach the live watcher.
- Scientific design and frozen payload remained unchanged.
- Corrected v0.2 transfer `20260825T213058Z-behavioral-portability-claude-001` was dispatched on `mailbox/main`.

### Execution

Hermes ran a fresh Claude Code 2.1.170 session using substantive model `claude-sonnet-4-6`. The target had no tools and received only the two Phase A artifacts before freeze. The same new session was resumed for all tests. Post-run source verification found the Phase A artifacts byte-identical to the frozen source and confirmed no overlap between development-example dates and frozen test dates.

Hermes result transfer: `20260825T234500Z-behavioral-portability-claude-result-001`.

Operator preliminary scores:

- Test 1: 19/20 PASS
- Test 2: 20/20 PASS
- Test 3: 19/20 PASS
- Operator experiment disposition: **PASS**

Independent scores:

- Test 1: 19/20 PASS
- Test 2: 18/20 PASS
- Test 3: 19/20 PASS
- Exact-date integrity: PASS all three
- Generalization: PASS all three

### Why the independent final result is INDETERMINATE

The first reconstruction response and first Test 1 response were displayed in the operator terminal but not written to immutable raw files when generated. Hermes re-issued both prompts for disk capture. The re-issued Test 1 was behaviorally strong but differed in prose from the reported first response. Hermes later preserved a first-response transcript reconstructed from terminal scrollback/operator memory.

This does not indicate application repair; both observed Test 1 variants behave like valid Amazing Birthday reports. But the preregistration explicitly states that **the first outputs are evidence**. The true first Test 1 sample is not independently SHA-verifiable, while the SHA-verifiable sample is the second inference. Under the frozen rule that evidence-capture defects can make a run INDETERMINATE, ChatGPT does not classify this execution as a clean preregistered PASS.

The disagreement is preserved rather than averaged away:

- **Hermes:** PASS; re-issues were capture passes, not repair.
- **ChatGPT independent reviewer:** INDETERMINATE formal; behavioral PASS signal is strong, but first-run evidence provenance is insufficient for a clean experimental PASS.

One operator factual-care concern was independently corrected: German federal-government historical records confirm Schabowski's decisive press conference occurred on November 9, 1989, not November 6. Test 1's central exact-date association therefore stands.

Supported claim from this run:

> In a fresh isolated Claude Code environment given only the frozen Amazing Birthday behavioral baseline and reconstruction prompt, Claude produced strongly conforming Amazing Birthday behavior on all three withheld dates. A first-run capture defect prevents counting this particular execution as a clean preregistered cross-provider PASS.

### Immediate next experiment

Repeat the same Claude experiment once with the scientific design frozen and only the evidence procedure corrected:

- pre-fetch and verify frozen source;
- capture every first inference atomically to disk;
- prohibit re-issue for evidence capture;
- retain the same Phase A artifacts, no-tools isolation, test dates, and rubric.

A clean replication directly resolves the only formal uncertainty before moving to a new provider such as Gemini.

## Current support for Behavioral Portability

The evidence supports a stronger but still bounded statement than before:

> Governed Amazing Birthday behavior has survived reconstruction across multiple AI environments and distinct implementation mechanisms. A same-provider artifact-only clean-room reconstruction has a clean preregistered PASS. A fresh Claude cross-provider run produced passing behavior on all three withheld tests, but its first-run evidence capture was imperfect, so that run is formally INDETERMINATE pending a clean replication.

It remains premature to claim universal portability across providers, models, upgrades, or application classes.

## Highest-value unresolved questions

1. Can the Claude artifact-only experiment produce a clean preregistered PASS/FAIL when every first inference is captured immutably?
2. Does the same frozen package pass on a different provider family such as Gemini?
3. How much run-to-run variance appears under identical reconstruction conditions?
4. Does a durability package outperform the original transcript alone as a portability input?
5. Which durability-package components are necessary versus redundant?
6. Does Behavioral Portability survive decision-oriented, stateful, structured-data, tool-dependent, and process-cluster applications?

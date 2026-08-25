# Behavioral Portability — Evidence Ledger

**Purpose:** maintain a compact, auditable record of evidence relevant to the Behavioral Portability hypothesis.  
**Last updated:** 2026-08-25

This ledger deliberately separates preregistered experiments from observational demonstrations. A recognizable reconstruction is useful evidence, but it is not automatically equivalent to a clean-room, frozen-rubric replication.

## Evidence levels

- **Preregistered replication** — artifact set, isolation rules, tests, scoring, and failure rules frozen before execution; raw evidence preserved.
- **Controlled experiment** — meaningful controls and preserved outputs, but one or more preregistration or isolation elements are weaker.
- **Observational demonstration** — real reconstruction occurred and artifacts/outputs are available, but the run was not designed as a formal test.
- **Hypothesis only** — plausible implication that has not yet been directly tested.

## Current ledger

| ID | Application | Source → target | Preservation input | Target implementation | Evidence level | Result | Main limitation |
|---|---|---|---|---|---|---|---|
| BP-AB-CHATGPT-001 | Amazing Birthday | ChatGPT → fresh ChatGPT environment | Frozen behavioral baseline + reconstruction prompt | Reconstructed conversational behavior | Preregistered replication | **PASS — 60/60** | Same provider; does not by itself establish cross-provider portability |
| BP-AB-CLAUDE-OBS-001 | Amazing Birthday | ChatGPT-origin artifacts → Claude | Original transcript + durability package | Claude-generated application code | Observational demonstration | Recognizable reconstruction | Not preregistered; implementation was evaluated observationally rather than against the frozen three-test rubric |
| BP-AB-GROK-OBS-001 | Amazing Birthday | ChatGPT-origin artifacts → Grok | Original transcript + durability package | Grok platform-native skill | Observational demonstration | **Preliminary behavioral PASS** | Factual regression not independently verified; not a preregistered clean-room run |
| BP-AB-CLAUDE-EXP-001 | Amazing Birthday | Frozen package → Claude, operated by Hermes | Frozen behavioral baseline + reconstruction prompt; tests withheld until freeze | Claude-selected | Preregistered replication | **ACTIVE — live-dispatched 2026-08-25** | Result pending; initial transport package was stranded on default `main`; corrected v0.2 transfer is live on `mailbox/main` |

## Evidence records

### BP-AB-CHATGPT-001 — Amazing Birthday artifact-only clean-room reconstruction

Record: [`experiments/2026-08-24-amazing-birthday-clean-room-001/`](experiments/2026-08-24-amazing-birthday-clean-room-001/)

Observed:

- a genuinely fresh ChatGPT environment received only the frozen behavioral baseline and reconstruction prompt;
- the reconstruction was frozen before test execution;
- three dates withheld from the development transcript were run without repair, clarification, hints, or regeneration;
- all three first-run outputs passed the frozen v1.0 rubric for a total of 60/60.

Supported claim:

> In the recorded ChatGPT environment, the frozen artifact-only package preserved enough Amazing Birthday behavioral identity to satisfy the preregistered criteria on new inputs.

Not established:

- provider independence;
- deterministic reproduction;
- portability of stateful, transactional, or tool-dependent applications.

### BP-AB-CLAUDE-OBS-001 — Claude generated implementation

Observed:

- Claude received the Amazing Birthday source material and durability package;
- Claude selected a code-generating implementation path rather than simply reproducing the ChatGPT conversational mechanism;
- the produced application was recognizable as Amazing Birthday.

Research value:

This is direct evidence for **implementation divergence**: a receiving AI may realize the same governed application intent using a different technical mechanism.

Limitation:

Because the run was not preregistered against the frozen v1.0 three-test protocol, it should not be reported as equivalent to BP-AB-CHATGPT-001.

### BP-AB-GROK-OBS-001 — Grok platform-native skill reconstruction

Record: [`experiments/2026-08-25-amazing-birthday-grok-reconstruction-001/`](experiments/2026-08-25-amazing-birthday-grok-reconstruction-001/)

Observed:

- Grok autonomously selected a platform-native skill structure;
- reconstruction was reported complete in approximately 1 minute 13 seconds;
- a recognizable Amazing Birthday response was subsequently produced;
- the stored assessment is a preliminary behavioral pass.

Research value:

This adds a second distinct implementation mechanism and a second receiving provider to the portability observations.

Limitation:

The run was observational, not a preregistered clean-room replication, and factual regression has not been independently verified.

### BP-AB-CLAUDE-EXP-001 — Hermes-operated Claude preregistered replication

Preregistration: [`experiments/2026-08-25-amazing-birthday-hermes-operated-claude-001/`](experiments/2026-08-25-amazing-birthday-hermes-operated-claude-001/)

Frozen design:

- Hermes acts as experiment operator, not reconstruction target;
- Claude must be launched in a fresh isolated working environment;
- before freeze Claude receives only the same two frozen artifacts used in the prior ChatGPT clean-room experiment;
- the three v1.0 test dates and scoring rubric remain withheld from Claude until reconstruction is frozen;
- first outputs are preserved without repair;
- Hermes performs preliminary scoring;
- ChatGPT independently reviews the raw evidence before final classification.

Operational record:

- initial transfer `20260825T205300Z-behavioral-portability-001` was mistakenly staged on the repository default `main` branch and therefore did not reach the live Hermes watcher;
- the scientific design and frozen payload were left unchanged;
- corrected protocol-v0.2 transfer `20260825T213058Z-behavioral-portability-claude-001` was dispatched with `READY` on the live `mailbox/main` branch.

Status: **ACTIVE / LIVE-DISPATCHED**. Execution evidence has not yet been returned.

## Current support for the Behavioral Portability hypothesis

The evidence currently supports a **narrow but increasingly interesting** statement:

> Governed behavioral intent for Amazing Birthday has survived reconstruction across multiple AI environments and has been realized through substantially different implementation mechanisms. One clean artifact-only ChatGPT reconstruction has passed a preregistered behavioral test; cross-provider results are promising but formal cross-provider replication is still in progress.

It is premature to claim that durability packages are universally portable or that behavior remains equivalent across providers, models, upgrades, or application classes.

## Highest-value unresolved questions

1. Does the same frozen artifact-only package pass the same frozen test set on an independent provider?
2. How much run-to-run variance appears when the same provider repeats reconstruction?
3. Does a durability package outperform the original transcript alone as a portability input?
4. Which durability-package components are necessary versus redundant?
5. Does Behavioral Portability survive a move from narrative/research micro-apps to decision-oriented applications such as Fair Price?
6. What changes when persistent state, structured data, external tools, and process clusters are introduced?

The autonomous research loop defined in [`BEHAVIORAL-PORTABILITY.md`](BEHAVIORAL-PORTABILITY.md) should select subsequent experiments by which unresolved question is most likely to change confidence in the hypothesis.

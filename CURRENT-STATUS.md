# Development by Intent — Current Status

**As of:** 2026-08-28  
**Project stage:** experimental / pre-1.0 — late proof-of-concept, early research program  
**Decision authority:** Frank Ventura as principal investigator  
**Operating rule:** human owns intent and evaluation; AI owns implementation within explicit governance and frozen experimental limits

## Current assessment

Development by Intent has moved beyond an interesting demonstration. The repository contains reproducible behavioral evidence, preserved failures, independent review, provenance controls, and a second stateful application.

The evidence supports bounded behavioral recoverability. It does not yet establish that full durability packages are necessary, generally superior to thinner inputs, or sufficient across providers and application classes.

## Evidence established

### Amazing Birthday

- Fresh ChatGPT artifact-only reconstruction: **PASS — 60/60**.
- Clean Claude artifact-only replication: **PASS — independent 19/20, 19/20, 17/20**.
- Transcript-only Claude replication 006: formal **PASS** after reconstruction-freeze repair.
- Frank-as-PI factual adjudication records replication 006 at **17/20, 18/20, 17/20 = 52/60**.
- Claude and Grok observational reconstructions demonstrate different implementation mechanisms, but are weaker than preregistered replications.
- Gemini remains unresolved because the required runtime was absent and no target invocation occurred.

### Receipt Organizer

- Artifact-only Claude reconstruction: **functional PASS — 24/24**.
- Session ledger state retained across nine turns.
- Causal status: **PROVISIONAL** because no thin-description or concise-contract control was run.
- Canonical source corpus preservation: **PASS**. The verbatim Claude Code transcript, reconstructed ChatGPT transcript, and derived reconstruction prompt remain separate, hash-bound, and provenance-labeled.

## Active experiment

### BP-AB-ABLATION-003

Research question:

> Does the Amazing Birthday artifact-only durability package transmit behavior that a capable model does not recover from either a thin description or a concise behavioral contract?

Conditions:

- A — thin description;
- B — concise behavioral contract;
- C — artifact-only durability package.

Ablation 002 is INDETERMINATE and produced no scientific result. Its dates are withdrawn.

Ablation 003's immutable mailbox snapshot received independent `FREEZE_REVIEW: PASS` with zero blockers. Its externally bound identity is commit `254d892d3b8150d5da419824b2307269fe4be8af`. Execution remains fail-closed until a no-generation readiness check confirms:

1. parity of the 15 generator-visible blobs between the reviewed snapshots;
2. wrapper/no-clobber and empty-capture readiness;
3. correct metadata roles for final, preparation, and predecessor commits;
4. unchanged Claude environment and no-tools posture;
5. availability of both required evaluators.

No execution GO exists until that readiness response passes.

## Decision gate

- If Condition C materially outperforms A and B, the durability-package thesis gains bounded causal support.
- If all conditions perform similarly, recovery in this application may be dominated by model competence or information contained in thinner inputs.
- Either result determines the design of the Receipt Organizer causal ablation.

## Ordered next work

1. Complete Ablation 003 readiness and execution.
2. Evaluate and publish its bounded result in the evidence ledger.
3. Preregister the Receipt Organizer three-condition causal ablation.
4. Execute with blinded independent evaluation and preserved state evidence.
5. Resume Fair Price.
6. Begin matched Development by Intent versus conventional development-economics comparisons.

## Collaboration

ChatGPT and Hermes operate as reasoning peers under [SPCP 0.1.1](docs/collaboration/STRUCTURED-PEER-COLLABORATION-PROTOCOL.md). The protocol is an amended pilot candidate, not yet a proven efficiency result. It separates substantive reasoning from transport events and preserves Frank's authority over frozen protocol changes, destructive actions, material scope changes, external publication, and commitments made in his name.

## Repository posture

This status file was created during consolidation of:

- `main` at `0ae5a1203c1905ac4ad1163de2925ad161e8374b`;
- `integration-merge-ab-ro-2026-08-27` at `696eb1fadb9c117c457204be73183ebb85fef004`.

The consolidation preserves both histories and all experimental branches. The integration evidence tree is retained, SPCP 0.1.1 is carried forward from `main`, and current public summaries are being reconciled without rewriting frozen experiment history.

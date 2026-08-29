# Development by Intent — Current Status

**As of:** 2026-08-29  
**Project stage:** experimental / pre-1.0 — Developer Preview v0.1  
**Decision authority:** Frank Ventura as principal investigator  
**Operating rule:** human owns intent and evaluation; AI owns implementation within explicit governance and experimental limits

## Current assessment

Development by Intent has enough internal evidence to move from discovery-heavy research into **external developer validation**.

The repository contains reproducible behavioral evidence, preserved failures, provenance controls, independent review, multiple reconstruction environments, and a second stateful application. The immediate bottleneck is no longer lack of internal evidence. It is whether an independent developer can understand the method quickly, reproduce the basic development loop, distinguish DbI from ordinary AI-assisted coding, and identify credible failure modes.

The project is therefore deliberately reducing additional internal experiment generation until the Developer Preview receives outside feedback.

## Evidence established

### Amazing Birthday

- Fresh ChatGPT artifact-only reconstruction: **PASS — 60/60**.
- Clean Claude artifact-only replication: **PASS — independent 19/20, 19/20, 17/20**.
- Transcript-only Claude replication 006: formal **PASS** after reconstruction-freeze repair.
- Frank-as-PI factual adjudication records replication 006 at **17/20, 18/20, 17/20 = 52/60**.
- Claude and Grok observational reconstructions demonstrate different realization mechanisms, though with weaker controls than preregistered replications.
- Gemini remained unresolved when the required runtime was absent.

These results support bounded behavioral recoverability. They do not establish universal portability or deterministic equivalence.

### Receipt Organizer

- Artifact-only Claude reconstruction: **functional PASS — 24/24**.
- Session ledger state retained across nine turns.
- Canonical source corpus preservation: **PASS**. The verbatim Claude Code transcript, reconstructed ChatGPT transcript, and derived reconstruction prompt remain separate, hash-bound, and provenance-labeled.
- Causal attribution remains a separate question: functional success alone does not prove that the full durability package was necessary.

### Amazing Birthday causal ablation

**BP-AB-ABLATION-003 completed on 2026-08-29.** The controlled execution, behavioral scoring, acknowledgement, and experiment loop were closed under protocol v0.2.

The result is retained as bounded causal evidence and should be consolidated into the detailed evidence ledger without reopening the experiment. The Developer Preview does not depend on a reader understanding the internal transport or scoring machinery.

## Active milestone — Developer Preview v0.1

The active work is intentionally small:

1. make the repository understandable to a developer in roughly 90 seconds;
2. provide a hands-on tutorial that can be attempted in about 10 minutes;
3. provide a concise evidence summary with explicit limits;
4. provide a five-minute demo path;
5. obtain structured feedback from **5–10 independent developers**.

See:

- [`README.md`](README.md)
- [`examples/amazing-birthday/TUTORIAL.md`](examples/amazing-birthday/TUTORIAL.md)
- [`EVIDENCE.md`](EVIDENCE.md)
- [`DEMO.md`](DEMO.md)
- [`DEVELOPER-VALIDATION.md`](DEVELOPER-VALIDATION.md)

## Decision gate

After the first 5–10 developer reviews:

- If developers **do not understand the method**, fix the explanation before running more experiments.
- If they understand it but repeatedly identify the **same substantive weakness**, investigate that weakness next.
- If they understand it and independently try it, prioritize those external attempts and their failures over additional internally generated examples.

The project should not expand outreach or resume expensive internal collaboration until this first feedback set is reviewed.

## Research held in reserve

The following work remains valid but is temporarily lower priority:

- Receipt Organizer causal ablation;
- additional behavioral-portability ablations;
- Fair Price development;
- matched DbI versus conventional development-economics measurements;
- further collaboration-protocol refinement;
- additional portability or implementation-freedom experiments.

These should be resumed when external developer evidence shows which question is worth the next unit of effort.

## Repository posture

The detailed research record remains preserved under `examples/`, `experiments/`, the behavioral-portability documents, and the experiment protocol.

The public entry path is now intentionally simpler than the laboratory behind it.

The current objective is not broad adoption. It is **developer comprehension, independent trial, and useful criticism**.

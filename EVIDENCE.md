# Development by Intent — Evidence in Brief

This page is the short version for developers evaluating the idea. The underlying experiment directories, frozen inputs, outputs, score artifacts, and provenance records remain authoritative.

The project distinguishes **operator scoring**, **independent re-scoring**, and **blinded evaluation**. Those terms are not interchangeable.

## What has been demonstrated

### 1. A conversational application can develop recognizable behavioral identity

Amazing Birthday began as a simple intent-level request rather than a conventional implementation specification. Through use and conversational correction, the application acquired repeatable expectations: select a small number of meaningful historical connections, explain significance, distinguish exact-date events from nearby context, and place the date within the arc of a person's lifetime.

Those expectations were later made explicit as a behavioral baseline and acceptance rubric.

### 2. That behavior can survive loss of the original conversation

Amazing Birthday was reconstructed in fresh environments using preserved artifacts rather than the original live development context. Multiple recorded reconstructions met the project's behavioral acceptance criteria.

The public result index is [`examples/amazing-birthday/RESULTS-INDEX.md`](examples/amazing-birthday/RESULTS-INDEX.md). It explicitly separates operator scores from independent scores where both exist.

Examples include:

- the preregistered clean-room artifact-only run, with operator scores of `20 / 20 / 20` and a later independent score recorded as `60 / 60`;
- a Claude artifact-only replication with a clean operator disposition and later independent scores of `19 / 19 / 17`, classified `PASS`;
- other transcript-only runs that currently surface operator PASS results while independent review remains pending in the public index.

These later independent scores are **independent re-scoring**, not automatically blinded evaluation. The public summaries do not establish that the scorer was blind to all operator narrative or provenance, so this page does not describe those re-scores as blinded.

The Amazing Birthday validation materials use the frozen v1.0 behavioral rubric for the canonical reconstruction program; experiment-specific manifests and score files remain authoritative for the exact rubric and procedure used in each run.

This supports a bounded claim of **behavioral recoverability**: enough of the application's identity can be represented outside the original conversation for a fresh environment to recover recognizable behavior.

### 3. The receiving AI does not necessarily need the original implementation mechanism

Observed reconstructions have used different realization mechanisms, including conversational behavior, generated application code, and a platform-native skill.

That motivates the project's behavioral-portability hypothesis:

> the portable invariant may sometimes be intended application behavior rather than a particular implementation.

This remains a hypothesis under test, not a general portability guarantee.

### 4. The idea is not limited to a stateless narrative example

Receipt Organizer adds state, normalized structured records, deduplication, and natural-language queries over accumulated receipt data.

Its recorded artifact-only Claude reconstruction passed **24/24 functional checks**, including retained session state across nine turns.

**Evaluation qualification:** the public evidence surface does not currently show an independent score for that 24/24 result. Treat it as a recorded functional result in its environment, not as independently validated evidence. The project's own summary treats the stateful result provisionally.

It also does **not** by itself prove that the full durability package caused the success; a capable model may recover much of the behavior from thinner input.

### 5. Reconstruction stability did not imply safe evolution

A later DbI Evolution experiment asked whether a targeted intent change could modify one declared behavior while preserving the non-target behavioral identity.

Final disposition:

`MODIFICATION_AND_PRESERVATION_FAILURE`

The resulting architectural lesson is:

> **Reconstruction stability does not imply evolution stability.**

This negative result is important because it falsified an attractive shortcut: successful reconstruction alone was not enough evidence to claim that an AI-developed application could be safely changed while preserving the rest of its identity.

See [`EVOLUTION-FAILURE.md`](EVOLUTION-FAILURE.md) for the promoted public evidence note and its claim boundary.

## Evaluation provenance — how to read the scores

When evaluating a headline result, check four separate properties:

1. **Rubric** — which frozen scoring rubric/version governed the result?
2. **Operator score** — did the experiment operator score the output?
3. **Independent score** — did another evaluator later score the preserved output?
4. **Blinding** — was that evaluator prevented from seeing treatment identity, operator conclusions, provenance, or other information that could bias scoring?

An independent re-score can improve credibility without being blinded. A blinded evaluation can reduce bias but still requires a defined rubric and provenance. The repository should state both properties rather than using one as a synonym for the other.

For the Amazing Birthday reconstruction lineage, [`examples/amazing-birthday/RESULTS-INDEX.md`](examples/amazing-birthday/RESULTS-INDEX.md) is the first public score index. For deeper audit, use the experiment-specific manifests, raw outputs, and score files.

## What the project is testing causally

A central research question is how much preserved information is actually necessary.

Controlled work compares inputs such as:

1. a thin application description;
2. a concise behavioral contract;
3. a fuller durability package containing governed intent, constraints, examples, tests, provenance, and reconstruction guidance.

This distinction matters. If a thin description performs just as well, the larger package may add complexity without value. If the fuller package preserves behavior that thinner inputs lose, that supports a stronger durability claim.

The project preserves failures and indeterminate runs rather than counting only successful demonstrations.

The first experiment explicitly designed from frozen INSA v0.3, `INSA-ID-E1`, has **not executed**. Completed Stage 4 INSA experiments: **0**.

## What the evidence does **not** establish

Current results do not show that:

- every class of software is suitable for DbI;
- source code is obsolete;
- larger durability packages are always better than concise contracts;
- model upgrades preserve behavior automatically;
- probabilistic applications can be governed like deterministic binaries;
- behavior will remain portable across every provider or implementation mechanism;
- safe targeted behavioral evolution has been solved;
- Value Architecture has demonstrated portable behavioral durability;
- INSA v0.3 is empirically validated;
- internal architecture reviews constitute independent external validation;
- DbI is appropriate today for safety-critical, regulated, real-time, or highly deterministic systems;
- DbI is faster or cheaper across the software lifecycle in general.

Those are either bounded claims or open research questions.

## Why the evidence is interesting anyway

The demonstrated result is narrower, but consequential:

> A developer can create some reusable application behavior primarily by stating intent, judging outputs, correcting behavior, testing generalization, and preserving what matters — while allowing the AI system to supply much of the implementation capability.

The negative evolution result adds an equally important constraint: preserving behavior through reconstruction is easier to demonstrate than preserving non-target identity through intentional change.

If the broader pattern survives more application classes and controlled boundary experiments, the durable engineering asset may shift upward from implementation details toward governed intent, behavioral identity, authority, values, and evidence.

## Audit trail

For deeper inspection:

- [Amazing Birthday worked example](examples/amazing-birthday/README.md)
- [Amazing Birthday public result index](examples/amazing-birthday/RESULTS-INDEX.md)
- [Amazing Birthday evidence summary](examples/amazing-birthday/SUMMARY.md)
- [Receipt Organizer](examples/receipt-organizer/README.md)
- [Detailed behavioral-portability evidence](BEHAVIORAL-PORTABILITY-EVIDENCE.md)
- [Promoted evolution negative result](EVOLUTION-FAILURE.md)
- [Reviewer and independence disclosures](REVIEWER-DISCLOSURES.md)
- [Canonical / historical artifact index](ARCHIVE-INDEX.md)
- [Five-minute external validation](QUICK-VALIDATION.md)
- [Experiment protocol](docs/experiment-protocol.md)
- [Current project status](CURRENT-STATUS.md)

If this summary conflicts with frozen experiment evidence, the frozen evidence wins.
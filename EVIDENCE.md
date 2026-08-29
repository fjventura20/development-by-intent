# Development by Intent — Evidence in Brief

This page is the short version for developers evaluating the idea. The underlying experiment directories, frozen inputs, outputs, scores, and provenance records remain authoritative.

## What has been demonstrated

### 1. A conversational application can develop recognizable behavioral identity

Amazing Birthday began as a simple intent-level request rather than a conventional implementation specification. Through use and conversational correction, the application acquired repeatable expectations: select a small number of meaningful historical connections, explain significance, distinguish exact-date events from nearby context, and place the date within the arc of a person's lifetime.

Those expectations were later made explicit as a behavioral baseline and acceptance rubric.

### 2. That behavior can survive loss of the original conversation

Amazing Birthday was reconstructed in fresh environments using preserved artifacts rather than the original live development context. Multiple recorded reconstructions met the project's behavioral acceptance criteria.

The strongest public records are indexed from [`examples/amazing-birthday/RESULTS-INDEX.md`](examples/amazing-birthday/RESULTS-INDEX.md).

This supports a bounded claim of **behavioral recoverability**: enough of the application's identity can be represented outside the original conversation for a fresh environment to recover recognizable behavior.

### 3. The receiving AI does not necessarily need the original implementation mechanism

Observed reconstructions have used different realization mechanisms, including conversational behavior, generated application code, and a platform-native skill.

That motivates the project's behavioral-portability hypothesis:

> the portable invariant may sometimes be intended application behavior rather than a particular implementation.

This remains a hypothesis under test, not a general portability guarantee.

### 4. The idea is not limited to a stateless narrative example

Receipt Organizer adds state, normalized structured records, deduplication, and natural-language queries over accumulated receipt data.

Its first recorded artifact-only Claude reconstruction passed **24/24 functional checks**, including retained session state across nine turns.

That establishes functional recovery in the recorded environment. It does **not** by itself prove that the full durability package caused the success; a capable model may recover much of the behavior from thinner input.

## What the project is testing causally

A central research question is how much preserved information is actually necessary.

Controlled work compares inputs such as:

1. a thin application description;
2. a concise behavioral contract;
3. a fuller durability package containing governed intent, constraints, examples, tests, provenance, and reconstruction guidance.

This distinction matters. If a thin description performs just as well, the larger package may add complexity without value. If the fuller package preserves behavior that thinner inputs lose, that supports a stronger durability claim.

The project preserves failures and indeterminate runs rather than counting only successful demonstrations.

## What the evidence does **not** establish

Current results do not show that:

- every class of software is suitable for DbI;
- source code is obsolete;
- larger durability packages are always better than concise contracts;
- model upgrades preserve behavior automatically;
- probabilistic applications can be governed like deterministic binaries;
- behavior will remain portable across every provider or implementation mechanism;
- DbI is appropriate today for safety-critical, regulated, real-time, or highly deterministic systems;
- DbI is faster or cheaper across the software lifecycle in general.

Those are either bounded claims or open research questions.

## Why the evidence is interesting anyway

The demonstrated result is narrower, but consequential:

> A developer can create some reusable application behavior primarily by stating intent, judging outputs, correcting behavior, testing generalization, and preserving what matters — while allowing the AI system to supply much of the implementation capability.

If that pattern survives more application classes, the durable engineering asset may shift upward from implementation details toward governed intent and behavioral evidence.

## Audit trail

For deeper inspection:

- [Amazing Birthday worked example](examples/amazing-birthday/README.md)
- [Amazing Birthday public result index](examples/amazing-birthday/RESULTS-INDEX.md)
- [Amazing Birthday evidence summary](examples/amazing-birthday/SUMMARY.md)
- [Receipt Organizer](examples/receipt-organizer/README.md)
- [Detailed behavioral-portability evidence](BEHAVIORAL-PORTABILITY-EVIDENCE.md)
- [Experiment protocol](docs/experiment-protocol.md)
- [Current project status](CURRENT-STATUS.md)

If this summary conflicts with frozen experiment evidence, the frozen evidence wins.

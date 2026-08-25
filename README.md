# Development by Intent

**An experimental software-development methodology for building certain applications primarily through conversation with general-purpose AI.**

Development by Intent (DbI) explores a simple but consequential idea:

> Instead of implementing every capability in application-specific code, a developer can define, shape, constrain, test, and preserve behavior that already exists within a capable AI system.

This repository is not a finished framework and it is not a manifesto. It is an **open experimental project** intended to test where conversational application development works, where it fails, and what is required to make it reproducible and durable.

## Why this project exists

Traditional software development commonly follows a cycle such as:

`requirements → design → implementation → test → debug → modification → redeploy`

For suitable AI-native applications, Development by Intent may compress much of that loop to:

`state intent → execute → inspect → refine`

A conversational correction can sometimes function simultaneously as a requirements change, behavioral change, interface change, and new executable version.

The project is investigating whether this produces measurable advantages in:

- initial application development time
- debugging and correction cycles
- modification speed
- direct participation by domain experts
- reduction of bespoke application code
- reuse of capabilities already present in general-purpose AI systems
- rapid prototyping that remains usable rather than being discarded

## What we are trying to prove — and disprove

The current working thesis is:

> **Development by Intent is a software-development approach in which certain applications can be created primarily through conversation by shaping and constraining capabilities that already exist in a general-purpose AI system, rather than implementing those capabilities from scratch in conventional code.**

Important qualifiers: **certain applications** and **primarily through conversation**.

We explicitly do **not** assume that:

- all software can or should be built this way
- source code becomes unnecessary
- conversational behavior is automatically reproducible
- model upgrades preserve behavior
- a written specification always captures everything that emerged during development
- probabilistic behavior can be governed exactly like deterministic software

Those are research questions.

## Current research questions

1. Can an independent developer reconstruct an application from its original development conversation?
2. What behavior is lost when reconstruction uses only derived artifacts rather than the original conversation?
3. What is the minimum durable artifact set for reliable recovery?
4. Which classes of applications are suitable for Development by Intent?
5. How should regression testing work when the runtime is probabilistic?
6. What constitutes the source of a conversational application?
7. How do model changes affect application identity and behavior?
8. Can intent, examples, tests, and governance replace meaningful portions of application-specific code?
9. How much faster are development, debugging, and modification cycles in practice?
10. Which behaviors arise from explicit intent versus one-time generation artifacts?

See [RESEARCH-AGENDA.md](RESEARCH-AGENDA.md) for the experimental program.

## Repository structure

```text
.
├── README.md
├── THEORY.md
├── RESEARCH-AGENDA.md
├── CONTRIBUTING.md
├── CODE_OF_CONDUCT.md
├── LICENSE
├── docs/
│   ├── terminology.md
│   └── experiment-protocol.md
├── examples/
│   ├── amazing-birthday/
│   │   ├── README.md
│   │   ├── 01-original-intent.md
│   │   ├── 02-development-transcript/
│   │   ├── 03-behavioral-baseline.md
│   │   ├── 04-durable-package/
│   │   ├── 05-reconstruction/
│   │   ├── 06-validation.md
│   │   ├── tests/
│   │   └── results/
│   └── fair-price/
└── experiments/
    ├── README.md
    ├── 2026-08-24-amazing-birthday-clean-room-001/
    └── 2026-08-25-amazing-birthday-grok-reconstruction-001/
```

## First canonical example: Amazing Birthday

The first canonical worked example is **[Amazing Birthday](examples/amazing-birthday/README.md)**, a small conversational application that turns an exact birthdate into a selective historical birthday story.

It is useful as a first specimen because the application is easy to understand but its behavior is not a simple lookup. It requires research, relevance judgment, exact-date discipline, narrative synthesis, and the ability to generalize the same behavioral pattern to a date not used during development.

The historical experiment completed the full lifecycle:

`Develop → Preserve → Isolate → Reconstruct → Test → Continue`

The repository example separates original evidence from derived artifacts and provides a protocol another developer can use to attempt the reconstruction independently.

The goal is not to reproduce identical prose. The goal is to determine whether the **behavior that makes Amazing Birthday recognizably the same application** survives reconstruction.

### Cross-platform reconstruction evidence

Amazing Birthday has now produced recognizable reconstructed behavior in independent AI environments using different implementation mechanisms:

| Environment | Implementation mechanism | Current evidence status |
|---|---|---|
| ChatGPT | Reconstructed conversational behavior | Preregistered clean-room PASS |
| Claude | AI-selected generated application code | Observed behavioral reconstruction |
| Grok | Platform-native skill | Preliminary behavioral PASS |

The [Grok reconstruction record](experiments/2026-08-25-amazing-birthday-grok-reconstruction-001/) documents the inputs, timing, generated output, limitations, and assessment.

These observations provide preliminary evidence that governed behavioral intent can survive a change of AI provider and implementation mechanism. They do **not** yet establish exact equivalence, deterministic portability, or readiness for transactional and regulated enterprise systems.

A resulting research hypothesis is that an application's durable asset may eventually be its governed behavioral contract—intent, constraints, examples, acceptance tests, and evidence—while code, skills, workflows, and integrations become replaceable deployment artifacts. That enterprise hypothesis remains to be tested with more complex applications.

## Next planned example: Fair Price

**[Fair Price](examples/fair-price/README.md)** is the next planned example. It adds current market research, budgeting judgment, domain constraints, and practical recommendations for homeowners-association services and projects.

If Amazing Birthday tests conversational development and durability in a research-and-narrative micro-app, Fair Price asks whether the method extends to a more decision-oriented application.

## How to participate

The most valuable contribution is not agreement. It is a reproducible result.

Good contributions include:

- independently reconstructing a published example
- finding behavior that cannot be reproduced
- proposing a stricter test
- running the same reconstruction on a different model
- identifying an application class that does not fit the methodology
- measuring cycle time against a conventional implementation
- proposing better preservation or regression techniques

Start with [CONTRIBUTING.md](CONTRIBUTING.md) and the [experiment protocol](docs/experiment-protocol.md).

## Project status

**Status: experimental / pre-1.0**

The immediate goal is not adoption. It is **validation, falsification, and co-development**.

### Maintenance model

This repository is maintained on a **best-effort research basis**. There is no support SLA, fixed release schedule, or guarantee that every issue or pull request will receive a response. Evidence-bearing reports and reproducible experiments receive priority over feature requests or general support questions.

The project is intentionally structured to remain lightweight for its maintainer. Contributors should treat the repository as a public laboratory notebook and experimental testbed, not as a supported software product.

## License

MIT. See [LICENSE](LICENSE).

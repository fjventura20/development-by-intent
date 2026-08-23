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
│   └── fair-price/
│       ├── README.md
│       ├── original-transcript/
│       ├── preserved-artifacts/
│       ├── reconstruction/
│       └── tests/
└── experiments/
    └── README.md
```

## First canonical example: Fair Price

The first planned canonical example is **Fair Price**, a small conversational application that researches current market information and answers a practical budgeting question for a homeowners association: *What should we reasonably expect to pay for this service or project?*

It is intentionally small enough to reconstruct and test, while still requiring research, judgment, output constraints, and iterative behavioral refinement.

The original development transcript will be preserved alongside derived artifacts so contributors can compare multiple reconstruction strategies.

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

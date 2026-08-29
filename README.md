# Development by Intent

**What if the primary thing a developer writes is intent — and the AI owns the implementation?**

Development by Intent (DbI) is an experimental software-development method for applications where a capable AI can supply much of the implementation capability.

The human developer stays responsible for **intent, constraints, evaluation, and acceptance**. The AI is allowed to choose how to realize the behavior.

Instead of beginning with:

```text
requirements → design → code → test → debug → redeploy
```

DbI explores a shorter development loop:

```text
state intent → let the system act → inspect → refine → test → preserve
```

This repository exists to determine where that approach works, where it fails, and whether the resulting application behavior can be made durable and portable.

## Try it in 10 minutes

The fastest way to understand DbI is to experience it.

Open the **[Amazing Birthday tutorial](examples/amazing-birthday/TUTORIAL.md)** and follow the first few steps in a fresh conversation with a capable AI.

You will:

1. state a simple outcome rather than an implementation specification;
2. inspect what the AI produces;
3. correct the behavior conversationally;
4. test whether the correction generalizes to a new input;
5. establish a reusable trigger;
6. preserve the behavior so it can be tested outside the original conversation.

You do **not** need to choose a language, framework, database, architecture, or UI toolkit first.

That omission is deliberate.

## The central idea

Traditional AI-assisted coding usually keeps source code at the center:

```text
human intent → AI writes code → human reviews code → application
```

Development by Intent asks whether, for some classes of software, the development boundary can move upward:

```text
human intent + evaluation
          ↓
     AI implementation
          ↓
  observable behavior
```

If implementation details need to change, the AI may change them. The human evaluates whether the application still satisfies the intended behavior.

The strongest version of the hypothesis is that a durable application asset may sometimes be a governed behavioral contract — intent, constraints, examples, acceptance tests, provenance, and evidence — while code, skills, workflows, and integrations become replaceable implementation artifacts.

That hypothesis is being tested, not assumed.

## This is not just "vibe coding"

DbI is not "keep prompting until something looks good."

The method adds explicit engineering discipline:

- **behavioral identity** — define what makes the application recognizably the same application;
- **generalization tests** — test on inputs not used during development;
- **durability** — preserve enough intent and evidence to reconstruct the application after the original context is gone;
- **isolation** — test reconstruction without silently relying on prior memory or conversation history;
- **acceptance criteria** — score behavior rather than expecting identical prose or identical code;
- **provenance** — distinguish original evidence from derived artifacts and later reconstructions.

The goal is not to eliminate engineering. It is to move more engineering effort from implementation detail to intent, behavior, evaluation, and evidence where the application permits it.

## A concrete example: Amazing Birthday

**[Amazing Birthday](examples/amazing-birthday/README.md)** began as a simple conversational request: make a person's birthdate historically interesting and engaging.

Through use and correction, recognizable behavior emerged: select a small number of meaningful historical connections, explain why they matter, distinguish exact-date events from nearby context, and connect the birthdate to the person's lifetime.

That behavior was then preserved, reconstructed in fresh environments, and tested on previously unseen dates.

The important question is not whether another model produces identical prose. It is whether another implementation retains the behavioral identity that makes it the same application.

See **[EVIDENCE.md](EVIDENCE.md)** for the short version and the full experiment directories for the auditable record.

## What has been observed so far

The project has produced bounded evidence that:

- a conversationally developed application can exhibit stable, testable behavioral identity;
- that behavior can be represented in human-readable durable artifacts;
- fresh AI environments can reconstruct recognizable behavior without the original development conversation;
- different AI platforms can realize similar intended behavior using different implementation mechanisms;
- a stateful Receipt Organizer reconstruction passed its recorded functional test suite;
- controlled ablation work has begun separating information supplied by thin descriptions, behavioral contracts, and fuller durability packages.

These results are evidence of feasibility, not proof that DbI works for all software or that larger durability packages are always necessary.

## Where DbI is most plausible

Good early candidates are applications whose difficult capabilities already exist inside the AI runtime, such as:

- research and synthesis;
- classification and extraction;
- natural-language interaction;
- judgment under explicit criteria;
- transformation of semi-structured information;
- small workflow orchestration;
- personalized reporting.

DbI is **not** currently claimed as a replacement for conventional engineering in safety-critical, highly deterministic, high-throughput, real-time, regulated, or low-level systems.

## Developer Preview v0.1

If you are evaluating the idea, use this path:

1. **[Tutorial](examples/amazing-birthday/TUTORIAL.md)** — experience the method.
2. **[Amazing Birthday](examples/amazing-birthday/README.md)** — inspect the canonical example.
3. **[Evidence](EVIDENCE.md)** — see what has actually been demonstrated and what has not.
4. **[Demo script](DEMO.md)** — a short walkthrough of the claim and evidence.
5. **[Theory](THEORY.md)** and **[Research Agenda](RESEARCH-AGENDA.md)** — go deeper only if the idea survives your first inspection.

## The developer test we care about now

The next important validation is external, not another round of internal theorizing:

> Can an independent developer understand DbI quickly enough to try it on a small application of their own?

If you try it, the most useful feedback is:

- What did you think DbI meant after five minutes?
- Does it differ meaningfully from ordinary AI-assisted coding or vibe coding?
- Could you reproduce the Amazing Birthday development loop?
- Where do you think the method breaks?
- Would you try it on one of your own small applications?

Agreement is not required. A clear failure mode is valuable evidence.

## Research record

The repository preserves the deeper experimental program rather than hiding it:

- [`examples/`](examples/) — worked examples and reconstruction material;
- [`experiments/`](experiments/) — frozen experimental evidence;
- [`BEHAVIORAL-PORTABILITY.md`](BEHAVIORAL-PORTABILITY.md) — portability hypothesis;
- [`BEHAVIORAL-PORTABILITY-EVIDENCE.md`](BEHAVIORAL-PORTABILITY-EVIDENCE.md) — detailed evidence ledger;
- [`CURRENT-STATUS.md`](CURRENT-STATUS.md) — current research posture;
- [`docs/experiment-protocol.md`](docs/experiment-protocol.md) — experimental protocol.

The front page is intentionally simpler than the laboratory behind it.

## Contributing

The most valuable contribution is a reproducible result: try the method, identify a failure, reconstruct an example in a different environment, or propose a stricter test.

See **[CONTRIBUTING.md](CONTRIBUTING.md)**.

## Status

**Experimental / pre-1.0. Developer Preview v0.1.**

DbI has moved from initial concept discovery into external developer validation. The project is deliberately keeping the public entry path small while preserving the full research record underneath it.

## License

MIT. See [LICENSE](LICENSE).

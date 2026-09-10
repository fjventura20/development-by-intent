# Development by Intent

**What if developers integrated with AI at the intent level instead of the code level?**

Development by Intent (DbI) is an experimental software-development pattern in which the human owns **intent, constraints, judgment, testing, and acceptance**, while a capable AI is allowed to assume much of the implementation burden.

> **Humans own purpose, intent, judgment, and acceptance. AI assumes the burden of implementation.**

This repository is a research record, not a claim that the pattern is finished or universally applicable.

## Start here

**If you have five minutes:** run the [`Five-Minute External Validation`](QUICK-VALIDATION.md). A failure is a useful contribution.

**If you want to see it first:** watch the [8:41 Development by Intent developer demo](https://youtu.be/MXjLTDkpX3U).

**If you want the research state:** read [`CURRENT-STATUS.md`](CURRENT-STATUS.md) and [`EVIDENCE.md`](EVIDENCE.md).

**If you want the full worked example:** use the [`Amazing Birthday tutorial`](examples/amazing-birthday/TUTORIAL.md).

## The DbI idea

Traditional AI-assisted coding usually keeps implementation at the center:

```text
human intent → AI writes code → human reviews code → application
```

DbI asks whether the development boundary can move upward for some application classes:

```text
state intent
    ↓
AI realizes behavior
    ↓
human inspects and corrects
    ↓
test on new inputs
    ↓
preserve what must remain true
```

The AI may use code, tools, workflows, platform-native capabilities, or other mechanisms. The human evaluates whether the observable result still satisfies the intended application behavior.

This does **not** mean code disappears. It asks which implementation decisions can safely become replaceable when the execution environment itself is capable of interpreting intent.

## Evidence first

The project began with a simple question: can an application developed primarily through conversation retain recognizable behavior after the original development conversation is gone?

### Reconstruction result

The canonical Amazing Birthday example was developed conversationally, reduced to explicit behavioral expectations, reconstructed in fresh environments, and tested on previously unused dates.

Multiple recorded reconstructions met the project's behavioral criteria. Public result indexes distinguish operator scoring from later independent re-scoring where both exist. Independent re-scoring is **not automatically the same as blinded evaluation**; the repository now states that distinction explicitly.

This supports a bounded claim of **behavioral recoverability** for the tested application and environments. It does not establish universal portability or statistical reliability.

See [`EVIDENCE.md`](EVIDENCE.md) and [`examples/amazing-birthday/RESULTS-INDEX.md`](examples/amazing-birthday/RESULTS-INDEX.md).

### The important failure

The project then tested a harder question: can one part of the behavior be intentionally changed while the rest of the application's behavior remains within a declared preservation envelope?

The result was:

`MODIFICATION_AND_PRESERVATION_FAILURE`

The resulting lesson is:

> **Reconstruction stability does not imply evolution stability.**

That failure is now a first-class public result because it changed the architecture that followed. See [`EVOLUTION-FAILURE.md`](EVOLUTION-FAILURE.md).

The project preserves negative, null, indeterminate, and blocked results rather than counting only successes.

## What the evidence does not establish

The project does **not** currently claim that:

- DbI works for every class of software;
- source code is obsolete;
- larger preservation packages are always better than concise descriptions;
- model upgrades preserve application behavior automatically;
- safe targeted evolution has been solved;
- AI-generated applications are appropriate today for every regulated, real-time, safety-critical, or highly deterministic system;
- the broader architecture described below has been empirically validated.

The full claim boundary is maintained in [`EVIDENCE.md`](EVIDENCE.md) and [`CURRENT-STATUS.md`](CURRENT-STATUS.md).

## The broader question: Intelligence-Native Software Architecture

The DbI experiments exposed a larger problem:

> **How should software be designed when machine intelligence itself becomes a fundamental execution resource?**

The project currently calls that investigation **Intelligence-Native Software Architecture (INSA)**.

Frozen INSA v0.3 proposes five concerns that must remain explicit when implementation becomes increasingly intelligent and fluid:

1. **Intent** — what outcome is wanted and what constitutes acceptance.
2. **Authority** — what the system is permitted to do, independent of what it can technically do.
3. **Values** — how discretion is governed when instructions permit more than one action.
4. **Behavioral Identity** — what must remain stable when implementation varies, is reconstructed, or evolves.
5. **Evidence** — how humans or evaluators can determine whether those boundaries were respected.

This is a **frozen experimental architecture baseline**, not an established architectural discipline.

Current Stage 4 status: **0 completed experiments explicitly designed to validate frozen INSA v0.3.** The first planned experiment is `INSA-ID-E1 — Targeted Evolution With Preservation`; its current protocol is still draft and authorizes zero candidate-generation or evaluator calls.

See [`CURRENT-STATUS.md`](CURRENT-STATUS.md) for the exact state.

## Human control and execution authority

The project deliberately separates technical capability from permission to act.

A capable agent may be able to dispatch models, spend resources, modify repositories, or call tools. That capability does not constitute authority.

For experiments such as INSA-ID-E1, resource-consuming execution requires explicit **PI / human GO** after the protocol and evidence gates are satisfied. This is a human-control boundary, not an independent oversight board.

```text
capability to execute ≠ authority to execute
```

## Value Architecture

As AI systems receive more implementation freedom, instructions cannot uniquely determine every permitted decision. The project uses **Value Architecture** for the separate question of how an intelligent agent should exercise discretion when multiple actions remain technically possible and authorized.

Its governing principle is behavioral:

> **Stated values are claims until behavior provides evidence.**

The current experimental standard is [`VALUE-ARCHITECTURE-STANDARD-v0.2.md`](VALUE-ARCHITECTURE-STANDARD-v0.2.md). Value conformance remains under-tested; the standard should not be read as proof that the proposed values are durably embodied by current agents.

## Internal review is not external validation

INSA v0.1, v0.2, and v0.3 passed through internal AI-assisted adversarial and freeze reviews before v0.3 was frozen for experimentation.

Those reviews found real defects and caused revisions. They are useful evidence of internal methodology, but they are **not independent external certification**. The original artifacts did not record enough reviewer/model/context metadata to support a stronger claim.

See [`REVIEWER-DISCLOSURES.md`](REVIEWER-DISCLOSURES.md).

## Two ways to evaluate the project

### Developer path

1. [`QUICK-VALIDATION.md`](QUICK-VALIDATION.md) — five-minute external observation.
2. [`examples/amazing-birthday/TUTORIAL.md`](examples/amazing-birthday/TUTORIAL.md) — experience the development loop.
3. [`EVIDENCE.md`](EVIDENCE.md) — inspect what has and has not been demonstrated.
4. [`CONTRIBUTING.md`](CONTRIBUTING.md) — report a result, especially a failure.

### Research / architecture path

1. [`CURRENT-STATUS.md`](CURRENT-STATUS.md) — authoritative current posture.
2. [`EVIDENCE.md`](EVIDENCE.md) — evidence and evaluator qualifications.
3. [`EVOLUTION-FAILURE.md`](EVOLUTION-FAILURE.md) — negative evolution result.
4. [`INSA-ARCHITECTURE-v0.3-FROZEN.md`](INSA-ARCHITECTURE-v0.3-FROZEN.md) — frozen architecture binding.
5. [`VALUE-ARCHITECTURE-STANDARD-v0.2.md`](VALUE-ARCHITECTURE-STANDARD-v0.2.md) — current value-governance standard.
6. [`ARCHIVE-INDEX.md`](ARCHIVE-INDEX.md) — canonical versus superseded research artifacts.
7. [`experiments/`](experiments/) — frozen experimental record.

## The contribution we want most

Agreement is not required.

The most useful contribution is a reproducible observation that narrows the claim: a failed reconstruction, a case where the method collapses into ordinary prompting, a preservation failure, a stricter test, or an application class where the proposed boundary is wrong.

The [`Five-Minute External Validation`](QUICK-VALIDATION.md) is the cheapest way to start.

## Status

**Experimental / pre-1.0.**

DbI is the experimental lineage. INSA is the broader architecture now being tested. The repository remains named `development-by-intent` deliberately so historical evidence, links, discussions, and experiment identifiers are not rewritten by the broader framing.

The frozen architecture is not being revised in response to presentation critique. The next architectural unit of progress must come from evidence.

## License

MIT. See [`LICENSE`](LICENSE).
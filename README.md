# Development by Intent

**An experimental development pattern within a broader investigation of Intelligence-Native Software Architecture.**

**What if developers integrated with AI at the intent level instead of the code level?**

## The broader research question

This repository began by investigating Development by Intent (DbI): whether a human developer can remain primarily at the intent, constraint, evaluation, and acceptance layers while a capable AI assumes much of the burden of implementation.

That work has exposed a larger architectural question:

> **How should software be designed when machine intelligence itself becomes a fundamental execution resource?**

The current working umbrella for that question is **Intelligence-Native Software Architecture**.

Under that framing:

- **Intelligence-Native Software Architecture** is the broader architectural investigation;
- **Development by Intent (DbI)** is one experimental development pattern within it;
- **Value Architecture** addresses how intelligent agents should choose when discretion exists;
- **Behavioral Identity** asks what makes an application remain the same application when implementation can vary;
- **Evidence and Evaluation Architecture** asks how acceptable behavior, continuity, provenance, and reliability can be demonstrated.

The terminology is provisional. The research questions and evidence matter more than the labels.

See **[RESEARCH-DIRECTION.md](RESEARCH-DIRECTION.md)** for the current framing and its relationship to the existing DbI evidence.

## Watch the 8:41 developer demo

[▶ **Watch: Development by Intent — Developer Demo**](https://youtu.be/MXjLTDkpX3U)

See an application **created, invoked, modified, and integrated** through intent rather than direct code editing.

> **Humans own purpose, intent, judgment, and acceptance. AI assumes the burden of implementation.**

## Developer Challenge

**Watch → Try → Break it → Report**

1. Watch the 8:41 demo.
2. Run the **[Amazing Birthday tutorial](examples/amazing-birthday/TUTORIAL.md)** in a fresh conversation.
3. Try the same development loop on one small application of your own.
4. Tell us what worked, what failed, and where you think the approach breaks.

**The demo is enough to decide whether the idea deserves a deeper look; the tutorial lets you test it yourself.**

Development by Intent (DbI) is an experimental software-development pattern for applications where a capable AI can supply much of the implementation capability.

The human developer stays responsible for **intent, constraints, evaluation, and acceptance**. The AI is allowed to choose how to realize the behavior.

Instead of beginning with:

```text
requirements → design → code → test → debug → redeploy
```

DbI explores a shorter development loop:

```text
state intent → let the system act → inspect → refine → test → preserve
```

The repository exists to determine where that pattern works, where it fails, what must remain stable when implementation is fluid, and what broader architectural principles follow if intelligence becomes part of the execution environment itself.

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

## The central DbI idea

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

## Intelligence-native working model

DbI is now being treated as an experimental vehicle for a broader hypothesis: when intelligence itself participates in execution, the stable architectural boundary may move upward from implementation detail toward **purpose, intent, values, authority, behavior, and evaluation**.

A working model is:

```text
human purpose
      ↓
intent + constraints + acceptance criteria
      ↓
values + authority boundaries
      ↓
intelligent execution environment
      ↓
dynamic implementation / tools / coordination
      ↓
observable behavior
      ↓
evidence + evaluation
      ↓
human acceptance / correction
```

The implementation may vary. The governing envelope should remain explicit.

This does not mean code disappears. Deterministic algorithms, APIs, databases, interfaces, security boundaries, infrastructure, and high-assurance components may remain conventional. The research question is which responsibilities can safely move upward when the execution environment can interpret intent and choose implementation mechanisms.

## Human Benefit and Agency Principle

Development by Intent is intended to use AI to **increase human capability, not make human displacement the objective**.

DbI therefore treats human agency as part of the architecture, not as an optional social consideration:

- **Humans own purpose, intent, constraints, judgment, and acceptance.** AI may implement an outcome, but it does not acquire authority to redefine why the system exists or what constitutes an acceptable result.
- **AI should remove unnecessary implementation barriers.** The goal is to let more people turn legitimate ideas into useful software without requiring every person to master the technical machinery underneath it.
- **People must retain meaningful control.** A human should be able to inspect outcomes, redirect behavior, reject results, revise intent, and determine when the system has succeeded.
- **Capability should broaden access.** DbI is most valuable when it enables individuals, small organizations, domain experts, educators, nonprofits, and others who may not have access to conventional software-development resources.
- **Productivity is not itself the purpose.** Reducing implementation effort is useful when it expands what people can accomplish; reducing human participation is not a success criterion by itself.

A concise statement of the principle is:

> **Humans own purpose, intent, judgment, and acceptance. AI assumes the burden of implementation.**

DbI may still change the amount and kind of implementation work people perform. The project does not assume that such disruption is harmless. Its design goal is to place increasing AI capability under explicit human direction while preserving human authorship, authority, and responsibility for the resulting system.

## Value Architecture

As implementation autonomy increases, explicit rules alone may not determine every choice an intelligent system makes.

The project therefore treats **Value Architecture** as a separate but complementary concern: the durable principles and behavioral dispositions that govern an agent when instructions are incomplete, objectives conflict, or immediate supervision is absent.

A concise working formulation is:

> **Value Architecture is what an agent is made of when nobody is looking.**

This is not satisfied by an agent merely stating the correct values. It requires behavioral evidence under conditions where violating a value would make the task easier or more convenient.

Value Architecture is broader than DbI. Any intelligence-native system that grants meaningful discretion will need some way to govern how that discretion is exercised.

## This is not just "vibe coding"

DbI is not "keep prompting until something looks good."

The method adds explicit engineering discipline:

- **behavioral identity** — define what makes the application recognizably the same application;
- **generalization tests** — test on inputs not used during development;
- **durability** — preserve enough intent and evidence to reconstruct the application after the original context is gone;
- **isolation** — test reconstruction without silently relying on prior memory or conversation history;
- **acceptance criteria** — score behavior rather than expecting identical prose or identical code;
- **provenance** — distinguish original evidence from derived artifacts and later reconstructions.

The goal is not to eliminate engineering. It is to move more engineering effort from implementation detail to intent, behavior, evaluation, evidence, governance, and authority where the application permits it.

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

These results are evidence of feasibility, not proof that DbI works for all software, that larger durability packages are always necessary, or that Intelligence-Native Software Architecture is an established architectural discipline.

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
5. **[Research Direction](RESEARCH-DIRECTION.md)** — see the broader Intelligence-Native Software Architecture framing.
6. **[Theory](THEORY.md)** and **[Research Agenda](RESEARCH-AGENDA.md)** — go deeper only if the idea survives your first inspection.

## The developer test we care about now

The next important validation is external, not another round of internal theorizing:

> Can an independent developer understand DbI quickly enough to try it on a small application of their own?

If you try it, the most useful feedback is:

- What did you think DbI meant after five minutes?
- Does it differ meaningfully from ordinary AI-assisted coding or vibe coding?
- Could you reproduce the Amazing Birthday development loop?
- Where do you think the method breaks?
- Would you try it on one of your own small applications?
- Does the broader intelligence-native framing clarify the architectural problem, or merely rename familiar ideas?

Agreement is not required. A clear failure mode is valuable evidence.

## Research record

The repository preserves the deeper experimental program rather than hiding it:

- [`RESEARCH-DIRECTION.md`](RESEARCH-DIRECTION.md) — broader intelligence-native framing;
- [`examples/`](examples/) — worked examples and reconstruction material;
- [`experiments/`](experiments/) — frozen experimental evidence;
- [`BEHAVIORAL-PORTABILITY.md`](BEHAVIORAL-PORTABILITY.md) — portability hypothesis;
- [`BEHAVIORAL-PORTABILITY-EVIDENCE.md`](BEHAVIORAL-PORTABILITY-EVIDENCE.md) — detailed evidence ledger;
- [`CURRENT-STATUS.md`](CURRENT-STATUS.md) — current research posture;
- [`docs/experiment-protocol.md`](docs/experiment-protocol.md) — experimental protocol.

The front page is intentionally simpler than the laboratory behind it.

The broader framing does **not** rewrite the historical DbI evidence. Existing experiments retain their original names, protocols, dates, hashes, and claims.

## Contributing

The most valuable contribution is a reproducible result: try the method, identify a failure, reconstruct an example in a different environment, propose a stricter test, or challenge the broader architectural framing with evidence.

See **[CONTRIBUTING.md](CONTRIBUTING.md)**.

## Status

**Experimental / pre-1.0. Developer Preview v0.1.**

DbI has moved from initial concept discovery into external developer validation and controlled behavioral experiments. The repository now also records the emerging broader question of **Intelligence-Native Software Architecture** while keeping DbI as the experimental lineage and primary test vehicle.

The repository name remains `development-by-intent` deliberately: continuity of evidence, links, discussions, and experimental history matters more than prematurely renaming the project.

## License

MIT. See [LICENSE](LICENSE).

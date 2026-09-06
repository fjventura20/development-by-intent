# Research Direction — Intelligence-Native Software Architecture

**Working direction — September 6, 2026**

## Why this repository is broadening

This repository began by asking whether developers can work effectively at the **intent layer** while a capable AI assumes much of the burden of implementation.

That question remains important, and Development by Intent (DbI) remains the project's primary experimental pattern. But the work has exposed a larger architectural question:

> **How should software be designed when machine intelligence itself becomes a fundamental execution resource?**

The current working umbrella for that question is **Intelligence-Native Software Architecture**.

The term is provisional. The research matters more than the label.

## Working definition

**Intelligence-Native Software Architecture** is the design of software systems that treat machine intelligence as a fundamental execution resource while humans govern intent, values, authority, acceptable behavior, and evidence.

This does not assume that source code, deterministic services, databases, APIs, security boundaries, or conventional infrastructure disappear. It asks which architectural responsibilities can move upward when the execution environment can interpret intent, select implementation mechanisms, use tools, adapt behavior, and coordinate capabilities.

A useful working model is:

```text
human purpose
      ↓
intent + constraints + acceptance criteria
      ↓
values + authority boundaries
      ↓
intelligent execution environment
      ↓
dynamic implementation / tool use / coordination
      ↓
observable behavior
      ↓
evidence + evaluation
      ↓
human acceptance / correction
```

The implementation may vary. The purpose, behavioral boundaries, authority, and evaluation requirements should remain explicit.

## The emerging hierarchy

### Intelligence-Native Software Architecture

The broader architectural investigation: how software changes when intelligence is part of the execution environment rather than merely a development aid.

### Development by Intent (DbI)

A development pattern within that architecture. The human specifies and refines desired behavior while the intelligent environment is allowed to choose much of the implementation needed to realize it.

A concise DbI principle remains:

> **Humans own purpose, intent, judgment, and acceptance. AI assumes the burden of implementation.**

DbI is therefore an experimental vehicle for studying the human-machine development boundary, not a claim that all software should be developed conversationally or without conventional code.

### Value Architecture

The governing behavioral layer: the durable dispositions and principles that shape an agent's choices when explicit instructions, external enforcement, and immediate supervision are insufficient to determine what it should do.

A concise working formulation is:

> **Value Architecture is what an agent is made of when nobody is looking.**

As implementation autonomy increases, values cannot be treated only as external policy. They become part of the system's architecture because they influence which technically valid path the system chooses when discretion exists.

### Behavioral Identity

The problem of determining what makes an application recognizably the same application when its implementation can vary or be regenerated.

The working hypothesis is that, for some application classes, the durable invariant may be a governed behavioral contract rather than a particular source-code structure or runtime path.

### Evidence and Evaluation Architecture

The mechanisms used to determine whether an intelligence-native system behaved acceptably and whether that judgment can be reproduced.

This includes acceptance criteria, behavioral tests, provenance, reconstruction evidence, blinded evaluation where appropriate, failure disclosure, and auditable experimental records.

## Why the distinction matters

If machine intelligence becomes abundant, generation and implementation capability become less scarce. Other engineering resources become comparatively more important:

- choosing the correct objective;
- expressing intent precisely;
- defining constraints and authority;
- establishing acceptable behavior;
- governing autonomous choices;
- evaluating results;
- preserving behavioral identity;
- producing evidence that the system remained inside its intended envelope.

The project therefore no longer needs to answer only:

> Does Development by Intent work?

It can investigate broader questions such as:

- Where should the stable architectural boundary be placed when the execution environment itself is intelligent?
- Can application identity remain stable while implementation identity changes?
- Can developers modify intent without directly manipulating implementation and obtain predictable behavioral changes?
- What values and authority boundaries must govern implementation autonomy?
- How much implementation freedom can an intelligent system receive before reliability degrades?
- What evidence is sufficient to establish behavioral continuity, portability, and safe evolution?
- Which classes of software benefit from intelligence-native techniques, and which still require tightly specified deterministic implementation?

## Relationship to the existing DbI evidence

The broader framing does **not** invalidate or reset the Development by Intent research record.

Existing reconstructions, ablations, behavioral-portability work, Behavioral Identity Baseline experiments, field observations, developer critiques, and external reviews remain evidence about a specific pattern inside the larger investigation.

They should continue to be preserved under their original names, dates, protocols, hashes, and experimental claims.

The research direction is expanding; the historical evidence is not being rewritten.

## Research posture

The project should continue to separate observation, hypothesis, and demonstrated evidence.

Current claims should remain bounded:

- Intelligence-Native Software Architecture is a **working architectural framing**, not an established discipline.
- Development by Intent is an **experimental development pattern**, not a demonstrated replacement for conventional software engineering.
- Behavioral portability and stable identity under implementation variability remain **empirical questions**.
- Value Architecture requires behavioral testing; stated values alone are not evidence that an agent will preserve them under conflict or autonomy.
- High-assurance, safety-critical, real-time, regulated, and strongly deterministic systems may require very different boundaries from the language- and reasoning-centric applications studied so far.

A negative result that establishes those boundaries is useful evidence.

## Near-term research program

The near-term work remains evidence-first:

1. Establish a calibrated Behavioral Identity baseline across independent reconstructions.
2. Test whether intentional behavioral evolution can occur while identity is preserved.
3. Measure intent-to-correct-behavior latency and first-execution success where practical.
4. Continue causal ablation work to determine what information actually preserves behavior.
5. Design behavioral experiments for Value Architecture in situations where violating a stated value would make task completion easier.
6. Synthesize the evidence into a concise external brief that distinguishes demonstrated results from architectural hypotheses.

## Positioning

The repository name remains **development-by-intent** because DbI is the experimental lineage from which the broader investigation emerged and because preserving continuity matters.

The broader project can now be described as:

> **An investigation of Intelligence-Native Software Architecture: how software should be designed when intelligence itself becomes an abundant computational resource. Development by Intent is one experimentally studied pattern within that larger problem.**

This framing should evolve only as the evidence warrants it.

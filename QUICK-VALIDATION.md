# Five-Minute External Validation

This is the lowest-cost way to contribute useful evidence to the Development by Intent / INSA research program.

It is intentionally **not** a formal replication. It is a lightweight external observation designed to answer a simpler question: can an unfamiliar developer reproduce recognizable application behavior from a concise behavioral contract, and where does it fail?

## 1. Copy this into a fresh AI conversation

Use a capable AI system in a new conversation with no prior Development by Intent or Amazing Birthday context.

```text
Create a reusable conversational application named Amazing Birthday.

Given a person's full birth date including year, produce a historically grounded report that:
- selects roughly 5–10 meaningful historical connections rather than a long trivia list;
- prefers events that occurred on the exact month and day when credible exact-date material exists;
- explains why each selected connection matters;
- uses broader near-date or era context only when it adds real significance;
- connects the date to the arc of the person's lifetime when possible;
- uses a warm, vivid, engaging voice;
- avoids arbitrary trivia and unsupported factual claims.

Do not ask me to choose a programming language, framework, database, or UI. Choose whatever implementation mechanism you need.

When the application is ready to invoke, reply only: READY
```

## 2. Invoke it once

After the system replies `READY`, send:

```text
Birthdate November 9, 1989
```

## 3. What recognizable behavior should appear?

Do **not** expect identical prose. Look instead for behavioral identity:

- a selective report rather than an indiscriminate list;
- strong preference for exact-date historical material;
- explanation of significance, not just names and dates;
- a coherent narrative connecting the date to the person's lifetime or historical arc;
- factual restraint when exact-date evidence is weak;
- a tone that feels intentionally engaging rather than encyclopedic.

A failure is useful. Examples include fabricated exact-date claims, trivia dumping, ignoring the date, losing the lifetime framing, or producing something that is technically factual but no longer recognizable as the intended application.

## 4. Report the result

Record:

- AI provider and model, if known;
- whether memory or project context was enabled;
- the first output only — do not repair it before reporting;
- what worked;
- what failed or drifted;
- whether you think this differs meaningfully from ordinary prompt-and-response use.

Post the result through the repository's public discussion/contribution path described in [`DISCUSSIONS.md`](DISCUSSIONS.md) or [`CONTRIBUTING.md`](CONTRIBUTING.md).

## Why failures are especially valuable

The project is trying to determine where intent-level development, behavioral reconstruction, and intelligence-native architecture **break**, not merely where they succeed. A reproducible failure can be more informative than another successful demonstration.

## Research-status warning

This five-minute path is exploratory evidence only. It does not replace the repository's frozen protocols, preregistered experiments, evaluator records, or formal acceptance criteria. Formal claims continue to be governed by the frozen experiment evidence.
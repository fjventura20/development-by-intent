# Development by Intent — 5-Minute Developer Demo

This is a compact walkthrough for a live demo, screen recording, meetup lightning talk, or one-on-one developer conversation.

The purpose is not to explain the entire research program. It is to make one idea visible:

> **The developer can work primarily at the level of intent and evaluation while the AI owns the implementation.**

## 0:00–0:30 — Frame the shift

Show this contrast:

```text
AI-assisted coding
human intent → AI writes code → human reviews code → application

Development by Intent
human intent + evaluation → AI implementation → observable behavior
```

Say, in substance:

Development by Intent asks whether some applications can be developed without making implementation detail the human developer's primary workspace. The human owns what the system should do and whether it succeeded. The AI is allowed to decide how to realize it.

Do not claim that code disappears or that this applies to all software.

## 0:30–1:15 — Start with a deliberately thin intent

Open a fresh conversation in a capable AI system.

Enter:

```text
I would like you to tell me all the amazing things that happened on a person's birthdate in an interesting and engaging format. Try it on December 7, 1951.
```

Let the first result appear.

Point out what you did **not** specify:

- programming language;
- framework;
- data source architecture;
- ranking algorithm;
- report schema;
- UI implementation.

The first output is not the finished application. It is something you can evaluate.

## 1:15–2:00 — Develop by correcting behavior

Enter:

```text
Make Amazing Birthday selective rather than literally listing every event. The application should hunt for the 5–10 most surprising connections, explain why they matter, and weave them into the person's lifetime.
```

Explain the engineering effect of that correction.

It changes, at once:

- requirements;
- relevance criteria;
- output structure;
- narrative behavior;
- future acceptance expectations.

You corrected **what the application should do**, not how the implementation should do it.

## 2:00–2:45 — Test generalization

Enter:

```text
Amazing Birthday February 20, 1952
```

Evaluate the behavior instead of the wording:

- Is it selective?
- Are the connections meaningful?
- Does it explain significance?
- Does it separate exact-date facts from nearby context?
- Does it connect events to the person's lifetime?

Explain that a new input is functioning like a behavioral test.

If it fails, preserve the failure and correct the behavior. That correction becomes part of development.

## 2:45–3:20 — Turn behavior into a reusable application

Explain that the historical Amazing Birthday work established short triggers such as:

```text
Birthdate June 23, 1956
```

The persistence mechanism can vary by platform: project instructions, a skill, conversation context, a generated application, or another implementation.

The application-level contract is the important part: the short invocation should recover the accepted behavior without restating the entire specification.

## 3:20–4:10 — Show durability

Open the repository's Amazing Birthday example and show these artifacts:

- the original development transcript;
- the derived behavioral baseline;
- the reconstruction package;
- withheld/new-input behavioral tests;
- preserved reconstruction results.

Explain the key question:

> If the original conversation disappears, can a fresh AI environment recover the application from preserved intent and behavioral evidence?

Recorded clean-room reconstructions show that recognizable Amazing Birthday behavior can be recovered in fresh environments.

Do not say that every durability artifact has been proven necessary. That causal question is being tested separately.

## 4:10–4:40 — State what makes this different

Use this line:

> DbI is not "write one giant prompt" and it is not "keep prompting until it looks good." The engineering work moves toward intent, behavioral correction, generalization tests, acceptance criteria, preservation, and evidence.

Then show:

```text
Intent
  ↓
System acts
  ↓
Human judges
  ↓
Behavior is corrected
  ↓
New cases are tested
  ↓
Accepted behavior is preserved
```

## 4:40–5:00 — Give the developer a challenge

End with:

> Pick one small application where the AI already possesses most of the hard capabilities. Do not specify the implementation. State the outcome, evaluate what appears, correct the behavior, test it on a new case, and preserve what matters. Then tell us where the method breaks.

Direct them to:

1. [`README.md`](README.md)
2. [`examples/amazing-birthday/TUTORIAL.md`](examples/amazing-birthday/TUTORIAL.md)
3. [`EVIDENCE.md`](EVIDENCE.md)

## Demo discipline

Keep the demo narrow.

Do not spend the five minutes on:

- collaboration protocols;
- mailbox architecture;
- internal agent orchestration;
- long experimental chronology;
- every reconstruction score;
- Value Architecture;
- speculative enterprise claims.

Those topics may matter later, but they obscure the first developer decision:

> **Is this development method different enough and useful enough that I want to try it?**

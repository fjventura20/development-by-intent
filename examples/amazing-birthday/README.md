# Amazing Birthday — Canonical Worked Example

> **This application was developed through conversation, not from a conventional implementation specification.**

Amazing Birthday is the first canonical worked example for Development by Intent (DbI). It is intentionally small enough to understand end-to-end while still requiring research, judgment, selection, narrative construction, constraint-following, and generalization to previously unseen inputs.

The purpose of this example is not to showcase a birthday report. It is to make the DbI claim inspectable and reproducible.

## Try it yourself first

If you want to **experience Development by Intent before studying the experiment**, start with [`TUTORIAL.md`](TUTORIAL.md).

The tutorial begins with a simple intent, not the finished behavioral specification. You will generate a first attempt, judge it, refine the behavior conversationally, test it on another date, establish a short trigger, and then see how durability and reconstruction enter the lifecycle.

This distinction is deliberate:

- the **tutorial** teaches the development method;
- the **development transcript** preserves what historically happened;
- the **reconstruction artifacts** test whether the application can survive its original context.

Do not use the tutorial as input to a clean-room reconstruction experiment; doing so exposes development decisions and contaminates the test.

## What this example demonstrates

The lifecycle under test is:

`Intent → Conversation → Behavioral Refinement → Preservation → Isolation → Reconstruction → New-Input Validation → Continued Evolution`

The historical Amazing Birthday experiment completed that cycle successfully for one small application. This directory turns that experiment into a public reference specimen that another developer can inspect, challenge, and reproduce.

## Evidence model

The example deliberately separates three classes of material:

1. **Original evidence** — verbatim development conversation and any preserved artifacts actually produced during the historical experiment.
2. **Derived artifacts** — behavioral baselines, test criteria, and explanatory documents created from the original evidence.
3. **Public reproduction artifacts** — instructions and packages created to let an independent developer repeat the experiment today.

A recreated artifact must never be labeled as an original historical artifact.

## Directory map

```text
amazing-birthday/
├── README.md
├── TUTORIAL.md
├── 01-original-intent.md
├── 02-development-transcript/
│   └── README.md
├── 03-behavioral-baseline.md
├── 04-durable-package/
│   ├── README.md
│   └── RECONSTRUCTION-PROMPT.md
├── 05-reconstruction/
│   └── README.md
├── 06-validation.md
├── tests/
│   └── behavioral-tests.md
└── results/
    └── README.md
```

## The application

Primary invocation:

```text
Birthdate [date]
```

Alternate invocation:

```text
Amazing Birthday [date]
```

For a supplied date including year, the application creates an engaging historical birthday story rather than an exhaustive "on this day" list. It selects a small number of strong connections, explains why they matter, distinguishes exact-date events from nearby context, and places the person's birth within the larger historical and technological arc of a lifetime.

## Why Amazing Birthday is a useful specimen

It exercises capabilities that already exist in a general-purpose AI system rather than asking the developer to implement them one by one:

- historical research
- date reasoning
- relevance judgment
- factual discrimination
- narrative synthesis
- constraint-following
- personalized temporal framing

Yet the application has recognizable behavioral identity. A reconstruction that merely returns historical trivia is not the same application.

## Reproduce the experiment

Use the repository-wide [experiment protocol](../../docs/experiment-protocol.md), then follow [05-reconstruction/README.md](05-reconstruction/README.md).

The most important rule is isolation: the reconstructing environment should receive only the artifact set declared for that experiment. Do not silently rely on prior Amazing Birthday context or memory.

Then run the withheld/new-input tests in [tests/behavioral-tests.md](tests/behavioral-tests.md) and score the result using [06-validation.md](06-validation.md).

## Current publication status

The public example structure and behavioral specification are being assembled from the completed experiment. The verbatim original development transcript is intentionally not reconstructed from memory; it will be committed only from the preserved word-for-word source.

That limitation is evidence hygiene, not a missing-design shortcut.

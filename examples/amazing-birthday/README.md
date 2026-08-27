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
2. **Derived artifacts** — behavioral baselines, test criteria, traceability maps, and explanatory documents created from the original evidence.
3. **Public reproduction artifacts** — instructions and packages created to let an independent developer repeat the experiment today.

A recreated artifact must never be labeled as an original historical artifact.

## Quick orientation

- Want a one-paragraph claim and the bottom-line evidence? Read
  [`SUMMARY.md`](SUMMARY.md).
- Want every public reconstruction result in one table? Read
  [`RESULTS-INDEX.md`](RESULTS-INDEX.md).
- Want to **experience** Development by Intent before studying the experiment? Start
  with [`TUTORIAL.md`](TUTORIAL.md).

## Directory map

```text
amazing-birthday/
├── README.md
├── SUMMARY.md                    # public-facing claim + evidence summary
├── RESULTS-INDEX.md              # every public reconstruction result, with links
├── TUTORIAL.md                   # hands-on DbI experience
├── 01-original-intent.md
├── 02-development-transcript/
│   ├── README.md
│   ├── amazing_birthday_transcript.txt   # canonical, SHA-256 in README
│   └── behavior-derivation.md            # traceability, NOT original evidence
├── 03-behavioral-baseline.md             # frozen behavioral contract (v1.0)
├── 04-durable-package/
│   ├── README.md
│   └── RECONSTRUCTION-PROMPT.md
├── 05-reconstruction/
│   └── README.md                  # isolation / freeze / test / score procedure
├── 06-validation.md               # scoring rubric (v1.0 frozen)
├── tests/
│   └── behavioral-tests.md        # withheld/new-input tests (v1.0 frozen)
└── results/
    └── README.md                  # result-layout spec; actual results in experiments/
```

**Note on `results/`:** the actual reconstruction evidence (raw outputs, scoring,
environment records, failures) lives under [`experiments/`](../../experiments/) at the
repository root, organized by date and protocol. This is intentional: each experiment
is a self-contained reproducible unit with its own frozen source commit, MANIFEST, and
audit trail. See [`RESULTS-INDEX.md`](RESULTS-INDEX.md) for the canonical list.

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

## Inspect the original development evidence

The preserved word-for-word development record is in [`02-development-transcript/amazing_birthday_transcript.txt`](02-development-transcript/amazing_birthday_transcript.txt). Its provenance and checksum are recorded in [`02-development-transcript/README.md`](02-development-transcript/README.md).

The separate [`behavior-derivation.md`](02-development-transcript/behavior-derivation.md) shows how the derived behavioral baseline traces back to explicit requirements and demonstrated behavior without modifying the transcript.

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

Then run the frozen v1.0 withheld/new-input tests in [tests/behavioral-tests.md](tests/behavioral-tests.md) and score the result using [06-validation.md](06-validation.md).

## Current publication status

The authoritative word-for-word development transcript has now been imported and its provenance recorded. The derived behavioral baseline has been checked against that transcript, and the first public withheld test set is frozen as v1.0 using dates that do not appear in the development record.

The example is therefore ready for an independent clean-room reproduction run. Historical reconstruction outputs should only be added to `results/` when original evidence is available; recreated outputs must be labeled as new reproduction results, not historical artifacts.

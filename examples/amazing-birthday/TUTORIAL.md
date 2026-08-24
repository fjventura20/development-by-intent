# Tutorial — Build Amazing Birthday by Intent

This tutorial lets you experience **Development by Intent** by creating a small conversational application from scratch.

Do not begin by copying the behavioral baseline or reconstruction package. The point of this tutorial is to experience the development process: state an intent, inspect what the AI produces, refine the behavior, test it on a new input, and only then preserve what has emerged.

> **This is a teaching exercise, not a clean-room reconstruction experiment.**
>
> For reconstruction research, use the protocol and artifacts elsewhere in this example. The tutorial intentionally exposes development decisions that would contaminate a reconstruction test.

## What you will build

Amazing Birthday accepts a birthdate and creates an engaging story about the historical world surrounding that date.

By the end of the tutorial you should have a reusable conversational behavior invoked with a short request such as:

```text
Birthdate June 23, 1956
```

You will not write application code.

You will develop the application by judging and refining behavior.

---

## Step 1 — Start with intent, not a specification

Open a fresh conversation in a capable general-purpose AI system with web or research access if available.

Give it this request:

```text
I would like you to tell me all the amazing things that happened on a person's birthdate date in an interesting and engaging format. Try it on December 7, 1951
```

Then read the result.

Do not correct it yet.

### What to notice

At this point you have supplied:

- a purpose;
- an example input;
- an expectation that the output should be interesting and engaging.

You have **not** supplied:

- a data model;
- an algorithm;
- a list of historical sources;
- a ranking function;
- a report template;
- application code.

The first output is not merely a demo. It is also a requirements-discovery artifact.

Ask yourself:

- What parts are compelling?
- What parts feel like trivia?
- Is there too much material?
- Does the result tell a story or merely enumerate facts?
- What behavior would you want every future birthday report to preserve?

This judgment is part of development.

---

## Step 2 — Refine the behavior

The original Amazing Birthday development identified one important problem with the first result: an application that tries to report everything can easily become an "on this day" dump.

Give the AI this correction:

```text
make Amazing Birthday selective rather than literally listing every event. The application should hunt for the 5–10 most surprising connections, explain why they matter, and weave them into the person's lifetime
```

### What just happened?

That single conversational correction functions like several conventional development activities at once:

- a requirements refinement;
- a change to relevance criteria;
- a change to output structure;
- a change to narrative style;
- an implicit acceptance test for future outputs.

You did not tell the AI how to implement ranking or narrative synthesis. You governed the behavior you wanted.

This is the central Development by Intent move.

---

## Step 3 — Test the refinement on a different date

Now give the application a second input without restating the instructions:

```text
Amazing Birthday February 20, 1952
```

Evaluate the new result.

### Look for behavioral generalization

Do not ask whether the wording resembles the December 7 report.

Ask whether the **behavior** generalized:

- Did it select rather than dump?
- Did it choose meaningful connections?
- Did it explain why those connections matter?
- Did it connect the date to the person's lifetime?
- Did it distinguish events on the exact date from nearby historical context?
- Did it read as a story rather than a database query?

If the new date exposes a problem, correct that problem conversationally and test again.

That loop is DbI development:

```text
Intent → Execute → Inspect → Refine → Re-execute
```

---

## Step 4 — Establish a short application trigger

Once the behavior is good enough to reuse, tell the AI that you want a short invocation.

For example:

```text
Save this behavior so that when I ask Birthdate [some date] you produce the Amazing Birthday report.
```

The exact persistence mechanism depends on the AI environment. A platform may use conversation context, project instructions, memory, a custom skill, or another persistence mechanism.

The important application-level requirement is simpler:

> The user should be able to invoke the established behavior with a short intent-level command instead of restating the specification every time.

---

## Step 5 — Test the trigger

Use a third date:

```text
Birthdate August 24, 1931
```

Do not provide the behavioral instructions again.

If the application produces the intended Amazing Birthday behavior, you now have something meaningfully different from a one-off prompt.

You have established:

- an application name;
- an invocation interface;
- recurring behavioral expectations;
- selection criteria;
- narrative constraints;
- a reusable capability.

The underlying AI already knew how to research, reason about dates, compare historical events, and write prose. Development consisted largely of **shaping those capabilities into repeatable application behavior**.

---

## Step 6 — Compare your process with conventional implementation

Consider what you did **not** manually implement.

You did not write separate modules for:

- date parsing;
- historical search;
- event retrieval;
- relevance ranking;
- temporal comparison;
- narrative generation;
- lifetime calculations;
- prose formatting.

That does not mean implementation disappeared. The AI runtime and its tools provide substantial implementation capability.

The Development by Intent claim is narrower:

> For some applications, the human developer can work primarily at the level of intent, behavior, examples, corrections, and acceptance instead of manually implementing every capability from scratch.

---

## Step 7 — Freeze what the application has become

Before changing it further, write down the behavior you now consider essential.

Do this **after** development rather than using the repository's existing Amazing Birthday baseline as your starting specification.

Your list might include observations such as:

- how selective the report should be;
- what kinds of connections are worth including;
- how exact-date events should be distinguished from nearby context;
- how significance should be explained;
- how the person's lifetime should shape the narrative;
- what kinds of output would constitute failure.

Now compare your independently derived list with [`03-behavioral-baseline.md`](03-behavioral-baseline.md).

The comparison is instructive: it shows which requirements were obvious to you from use and which needed to be made explicit for preservation and testing.

---

## Step 8 — Make the application durable

Conversational development creates a new question:

> What happens when the conversation, project, memory, or model context that created the application is gone?

In the historical Amazing Birthday work, this became an intent-level preservation request:

```text
Make Amazing Birthday durable.
```

For this repository, durability means preserving enough evidence and behavioral information to make the application:

- intelligible;
- reconstructable;
- testable;
- evolvable after the original development context is gone.

Continue with [`04-durable-package/README.md`](04-durable-package/README.md) to see the public reconstruction package.

---

## Step 9 — Reconstruct in isolation

To test durability rather than memory, use a fresh environment with no prior Amazing Birthday context.

Follow [`05-reconstruction/README.md`](05-reconstruction/README.md).

The key experimental rule is isolation: declare exactly which artifacts the fresh environment receives.

Then test the reconstructed application with a birthdate that was not used to develop it.

Do not repair failures before preserving them.

---

## Step 10 — Evaluate behavior, not prose

A probabilistic AI application should not be expected to reproduce identical sentences.

Instead, ask whether the reconstructed application retains the behavioral identity that matters.

Use [`06-validation.md`](06-validation.md) to evaluate dimensions including:

- selectivity;
- exact-date integrity;
- significance;
- narrative coherence;
- lifetime framing;
- factual care;
- trigger behavior.

This is the difference between **replaying an output** and **recovering an application**.

---

# What you just experienced

The historical Amazing Birthday application did not begin with the behavioral baseline published in this repository.

It began with a simple request for an interesting birthday report.

Use exposed a design problem. A conversational correction made the application more selective. A second date tested whether the correction generalized. The behavior was accepted and given a reusable trigger. A third date exercised that trigger.

The application specification **emerged through development**.

That is the point of this tutorial.

Development by Intent is not "write a very long prompt instead of code."

The working pattern is closer to:

```text
State intent
    ↓
Let the system act
    ↓
Judge the result
    ↓
Correct behavior
    ↓
Test on another case
    ↓
Accept and preserve what works
```

The AI contributes implementation capability and judgment. The human remains responsible for intent, constraints, evaluation, and acceptance.

## Where to go next

- Read the [verbatim development transcript](02-development-transcript/) to compare this tutorial with the historical development record.
- Inspect the [behavioral baseline](03-behavioral-baseline.md) to see how emergent behavior was made explicit.
- Follow the [reconstruction procedure](05-reconstruction/README.md) to test whether the application can survive its original environment.
- Run the [behavioral tests](tests/behavioral-tests.md) and preserve the result whether it passes or fails.

If you can repeat the process, find a failure, or produce a different result on another model, that evidence is more valuable to this project than simply agreeing with the Development by Intent thesis.

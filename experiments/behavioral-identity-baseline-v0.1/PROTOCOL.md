# DbI Behavioral Identity Baseline Experiment v0.1

**Protocol ID:** DBI-BIB-001  
**Version:** v0.1  
**Status:** FROZEN  
**Freeze date:** 2026-09-04  
**Execution authorized:** NO  
**Next work item:** Execution Package v0.1

**Purpose:** Calibrate behavioral identity before conducting the DbI Evolution Experiment.

---

## 1. Research Question

When an AI reconstructs the same application independently from the same frozen intent specification, how much behavioral variance occurs naturally?

The experiment is intended to establish an empirical baseline for determining whether two independently reconstructed applications should reasonably be considered behaviorally the same application.

---

## 2. Why This Experiment Is Required

Future DbI experiments will ask whether an application can be modified by changing its intent while preserving its identity.

That question cannot be interpreted until normal reconstruction variance is known.

If two independent reconstructions of an unchanged specification differ substantially, then observing similar differences after an intentional modification tells us little.

Therefore:

**Baseline first → evolution second.**

---

## 3. Primary Hypothesis

Independent reconstructions from an identical frozen intent specification will exhibit:

1. variation in wording, presentation, reasoning path, and incidental implementation details; but
2. substantially stable contract-level behavior.

Behavioral identity should therefore be measured primarily at the level of externally observable behavior rather than textual or implementation identity.

---

## 4. Null Hypothesis

Independent reconstructions from the same intent specification vary enough in externally observable behavior that a stable behavioral identity cannot be reliably established.

If this occurs, the planned evolution experiment must be reconsidered because the identity metric would not be sufficiently calibrated.

---

# 5. Application Under Test

Use the existing **Amazing Birthday** application.

Reason:

- it already has a frozen intent specification;
- its expected behaviors have previously been exercised;
- known trigger cases exist;
- reconstruction evidence already exists;
- using it avoids introducing a new application and another uncontrolled variable.

The experiment must use one exact frozen specification package.

The package must be identified by:

- repository;
- branch;
- commit SHA;
- file list;
- SHA-256 hashes of all generator-visible files.

No specification changes are permitted after the experiment begins.

---

# 6. Experimental Unit

An experimental unit is one **independent clean-room reconstruction** of Amazing Birthday.

Each reconstruction must:

- begin in a fresh isolated session;
- receive exactly the same frozen specification;
- receive no outputs from any other reconstruction;
- receive no evaluator feedback;
- receive no corrective prompts;
- have equivalent available capabilities and tools;
- be created using the same model/runtime configuration whenever controllable.

Each reconstruction receives an anonymous identifier:

- R1
- R2
- R3
- R4
- R5
- R6

The reconstruction engine must not know how previous reconstructions performed.

---

# 7. Sample Size

### Initial calibration run

Use:

**6 independent reconstructions**

Each reconstruction will receive:

**5 fixed test inputs**

Each input will be executed:

**2 times**

Total behavioral observations:

**6 × 5 × 2 = 60 outputs**

This provides both:

### Within-reconstruction variance

Same reconstruction + same trigger + repeated execution.

and

### Between-reconstruction variance

Different reconstruction + same frozen specification + same trigger.

This distinction is critical.

If cross-reconstruction variation is no greater than ordinary repeat-execution variation, that is strong evidence that behavioral identity survives reconstruction.

---

# 8. Fixed Test Corpus

The five test cases must be frozen before execution.

They should deliberately exercise different behavioral characteristics.

Recommended corpus:

### T1 — Ordinary historical date

A date with plentiful historical material.

Purpose:

- normal operating behavior;
- selection quality;
- narrative construction.

### T2 — Sparse or difficult date

A date with fewer obvious significant events.

Purpose:

- behavior under limited evidence;
- resistance to padding weak connections.

### T3 — Leap-day date

Example:

**February 29, 1960**

Purpose:

- uncommon date handling;
- exact-date reasoning.

### T4 — Modern date

Example:

**November 9, 1989**

Purpose:

- historically rich event environment;
- prioritization and selectivity.

### T5 — Previously established acceptance-floor case

Example:

**August 24, 1931**

Purpose:

- compare against previously characterized behavior.

Exact trigger wording must be frozen and used byte-for-byte for every reconstruction.

---

# 9. What Counts as Behavioral Identity?

Behavioral identity is **not** defined as identical output.

Two outputs may differ substantially in wording while still representing the same application.

Identity will instead be evaluated across six behavioral dimensions.

## Dimension 1 — Trigger Recognition

Does the application correctly recognize and respond to the defined invocation?

Pass/fail.

---

## Dimension 2 — Contract Compliance

Does the output satisfy the application's required behavioral contract?

Examples include:

- appropriate number of selected connections;
- exact-date priority;
- relevance to the person's lifetime;
- avoidance of arbitrary trivia;
- historically meaningful selection.

Score:

**0–4**

---

## Dimension 3 — Selection Behavior

Does the application exhibit the same decision policy about what information is worth including?

Evaluator considers:

- significance;
- selectivity;
- relevance;
- avoidance of filler.

Score:

**0–4**

---

## Dimension 4 — Narrative Behavior

Does the application preserve the expected interpretive and narrative character?

Evaluator considers:

- warm rather than encyclopedic presentation;
- connection of events to the person's life;
- synthesis rather than raw enumeration.

Score:

**0–4**

---

## Dimension 5 — Functional Completeness

Does the application perform all major behaviors required by the specification without omission?

Score:

**0–4**

---

## Dimension 6 — Behavioral Violations

Record explicit deviations from the frozen contract.

Examples:

- fabricated event;
- ignored exact-date priority;
- excessive number of connections;
- generic historical dump;
- missing lifetime interpretation;
- failure to invoke the intended application behavior.

Each violation is classified:

- Minor
- Material
- Identity-breaking

---

# 10. Identity Classification

For each output, evaluators assign:

### SAME

The output exhibits the same application behavior despite incidental variation.

### SAME WITH VARIANCE

Recognizably the same application, but contains meaningful behavioral variation that does not change its essential identity.

### DIFFERENT

One or more core behaviors have changed sufficiently that the output should not be treated as an instance of the same application.

The evaluators must make this classification using the frozen rubric before seeing results from other reconstructions.

---

# 11. Quantitative Behavioral Score

Each output receives a behavioral score:

- Contract Compliance: 0–4
- Selection Behavior: 0–4
- Narrative Behavior: 0–4
- Functional Completeness: 0–4

Maximum:

**16 points**

Trigger recognition and identity-breaking violations remain separate hard-failure criteria rather than being averaged into the score.

The experiment will therefore retain both:

- continuous score data; and
- categorical identity judgments.

This prevents an arbitrary numerical average from hiding a serious behavioral failure.

---

# 12. Two Variance Distributions

The experiment must produce two distributions.

## A. Within-Reconstruction Variance

Compare repeated executions:

R1/T1/run1 vs R1/T1/run2

R1/T2/run1 vs R1/T2/run2

and so forth.

This measures ordinary nondeterministic execution variance.

---

## B. Between-Reconstruction Variance

Compare equivalent triggers across independently reconstructed applications:

R1/T1 vs R2/T1

R1/T1 vs R3/T1

etc.

This measures reconstruction variance.

---

# 13. Central Calibration Test

The most important comparison is:

> Is between-reconstruction behavioral variance materially greater than within-reconstruction execution variance?

Three possible outcomes exist.

### Outcome A — Strong behavioral identity

Between-reconstruction variance is comparable to normal repeated-execution variance.

Interpretation:

Independent reconstruction does not materially disturb application identity.

---

### Outcome B — Stable but broader identity

Between-reconstruction variance is measurably larger than within-reconstruction variance, but evaluators overwhelmingly classify outputs as SAME or SAME WITH VARIANCE.

Interpretation:

Application identity exists, but reconstruction introduces measurable behavioral latitude.

The observed range becomes the baseline envelope for the evolution experiment.

---

### Outcome C — Identity not calibrated

Reconstructions regularly receive DIFFERENT classifications or identity-breaking violations.

Interpretation:

The current intent specification does not produce sufficiently stable behavioral identity.

Do **not** proceed directly to the evolution experiment.

Instead determine whether the problem lies in:

- the specification;
- the reconstruction process;
- the behavioral metric;
- runtime instability.

---

# 14. Threshold Policy

Do not invent an identity threshold after seeing the results.

Before execution:

1. freeze the scoring rubric;
2. freeze the identity categories;
3. freeze the hard-failure rules.

The experiment should initially report the observed distributions rather than force an arbitrary universal threshold such as “90% similarity.”

After the baseline is observed, a prospective threshold for the Evolution Experiment may be derived from the baseline.

Recommended rule:

> A modified reconstruction will be considered identity-preserving only if its behavior remains within the empirically established baseline envelope for all non-target behaviors.

This is substantially more defensible than choosing a similarity percentage in advance without calibration.

---

# 15. Role Separation

The role structure must avoid the conflicts identified in earlier DbI experiments.

## Protocol Designer

**ChatGPT**

Responsibilities:

- experimental design;
- metric definition;
- pre-registration language.

Must not perform primary behavioral scoring.

---

## Experiment Operator

**Hermes**

Responsibilities:

- verify frozen artifacts;
- launch isolated reconstruction sessions;
- execute the frozen trigger corpus;
- capture raw outputs;
- calculate hashes;
- report deviations;
- package evidence.

Hermes must not modify outputs or determine the final DbI conclusion.

---

## Reconstruction Engine

One fixed AI model/runtime.

Responsibilities:

- reconstruct application;
- execute test cases.

It must not receive evaluator results.

---

## Evaluator A

Independent model or evaluator not involved in reconstruction or protocol design.

---

## Evaluator B

Second independent evaluator.

Evaluator B must score independently of Evaluator A.

---

## Final Synthesizer

**ChatGPT**

May compare locked evaluator results and interpret the experimental outcome only after scoring is complete.

---

# 16. Blinding

Evaluators should receive:

- frozen behavioral specification;
- evaluation rubric;
- test input;
- candidate output.

They should not receive:

- reconstruction identifier where avoidable;
- execution order;
- whether outputs came from the same or different reconstruction;
- previous evaluator scores;
- DbI success/failure expectations.

Outputs should be randomized before scoring.

---

# 17. Evidence Capture

For every execution preserve:

- reconstruction ID;
- session ID;
- model/runtime identifier;
- timestamp;
- frozen specification commit;
- frozen specification hashes;
- exact reconstruction prompt;
- exact trigger;
- raw stdout/output;
- tool activity where observable;
- retry information;
- errors;
- evaluator scores;
- evaluator rationale;
- classification.

Raw evidence must remain immutable.

---

# 18. Deviations

Any deviation must be reported explicitly.

Examples:

- session contamination;
- tool unavailable;
- different model version;
- truncated output;
- network failure;
- operator correction;
- retry;
- specification mismatch.

Retries must never silently replace failed attempts.

The original failed observation remains part of the evidence.

---

# 19. Pre-Registered Success Criteria

The baseline is considered sufficiently calibrated to proceed to the Evolution Experiment if:

1. at least **90% of valid observations** are independently classified by both evaluators as SAME or SAME WITH VARIANCE;

2. no systematic identity-breaking behavior occurs across multiple reconstructions;

3. evaluator agreement is sufficiently high to show the rubric itself is usable;

4. between-reconstruction variation produces an identifiable behavioral envelope rather than an unbounded distribution.

The 90% criterion is an experimental gate, not a claim that “90% similarity defines application identity.”

If evaluator disagreement is substantial, the metric itself requires refinement.

---

# 20. Stop Conditions

Stop and diagnose rather than expanding the experiment if:

- the frozen specification cannot be reproduced exactly;
- evaluator rubric proves ambiguous;
- reconstruction isolation fails;
- model/runtime changes materially during execution;
- more than one reconstruction experiences infrastructure failure;
- identity-breaking behavior appears frequently enough that calibration clearly fails.

Do not spend additional tokens merely to accumulate more examples after the conclusion is already clear.

---

# 21. Expansion Rule

The initial experiment is intentionally limited to 60 observations.

Increase the sample only if the result is genuinely ambiguous.

Possible expansion:

**6 additional reconstructions**

should occur only if:

- variance lies near the decision boundary;
- evaluator disagreement prevents interpretation; or
- an unexpected subgroup appears.

No automatic expansion.

This implements the Value-Cost Gate.

---

# 22. Expected Deliverables

The experiment must produce:

1. frozen experiment manifest;
2. frozen specification hashes;
3. six reconstruction records;
4. sixty raw behavioral outputs;
5. two independent evaluator score sets;
6. within-reconstruction variance table;
7. between-reconstruction variance table;
8. evaluator-agreement statistics;
9. deviation log;
10. baseline identity envelope;
11. PASS / INCONCLUSIVE / FAIL determination;
12. explicit recommendation on whether the DbI Evolution Experiment may proceed.

---

# 23. Interpretation Boundary

This experiment does **not** establish that:

- DbI is a new architecture;
- DbI is superior to conventional development;
- intent is sufficient for arbitrary software development;
- AI implementations are deterministic;
- behavioral identity guarantees implementation identity.

It establishes only whether:

> A fixed DbI intent specification produces a sufficiently stable family of independently reconstructed behaviors to support meaningful experiments about application evolution.

---

# 24. Connection to the Next Experiment

If this experiment succeeds, the measured baseline becomes the control for the **DbI Evolution Experiment**.

That experiment will introduce exactly one intentional behavioral modification.

The key question will then become:

> Did the requested behavior change while all non-target behavior remain inside the normal behavioral-identity envelope established here?

That comparison is what makes the evolution result interpretable.

---

## Experimental Sequence

**Experiment 1**

Frozen intent  
→ independent reconstructions  
→ measure natural behavioral variance  
→ establish identity baseline

**Experiment 2**

Frozen original intent  
→ controlled intent modification  
→ independent reconstruction  
→ measure intended behavioral change  
→ compare all unchanged behaviors against baseline

This sequence separates ordinary LLM/reconstruction variance from actual application evolution.

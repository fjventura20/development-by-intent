# Behavioral Portability — Autonomous Research Protocol

**Status:** active research protocol  
**Version:** 0.1  
**Established:** 2026-08-25

## Working definition

**Behavioral Portability** is the ability to move a governed application definition to an independent AI environment and reconstruct acceptably equivalent application behavior without requiring the same implementation, programming language, framework, prompt structure, agent architecture, or platform-native mechanism.

The object being tested is **behavioral identity**, not implementation similarity.

A durability package is a candidate portability artifact. Whether it is sufficient, necessary, over-specified, or incomplete is an empirical question.

## Core research question

> Under what preservation conditions, application classes, and receiving AI environments can a conversationally developed application retain its behavioral identity after reconstruction?

## Current evidence boundary

The project already has evidence that:

- Amazing Birthday can be reconstructed artifact-only in a clean ChatGPT environment and generalize to withheld inputs;
- a Grok reconstruction produced recognizable Amazing Birthday behavior using a platform-native skill structure;
- receiving AIs may choose radically different implementation mechanisms while pursuing the same behavioral contract.

These observations motivate Behavioral Portability as a research hypothesis. They do not yet establish universal cross-platform portability.

## Research principles

1. **Pre-register before execution.** Freeze the artifact set, test inputs, scoring rules, and failure conditions before observing the tested outputs.
2. **Behavior over implementation.** Do not require source-code, architecture, or framework similarity unless an experiment explicitly tests implementation convergence.
3. **Clean-room when claimed.** A run is clean only when the receiving environment has no prior application context or memory beyond the frozen supplied artifacts. Suspected contamination must be recorded.
4. **First output is evidence.** Do not repair, hint, regenerate, or clarify before raw first-run outputs are preserved and scored.
5. **Withhold tests until freeze.** The reconstructing AI must not receive the behavioral witnesses before reconstruction is frozen.
6. **Preserve failures.** FAIL, PARTIAL, ERROR, contamination, timeouts, and blocked runs are evidence, not discarded attempts.
7. **Separate operator, target, and scorer where practical.** The AI operating an experiment should not be the only evaluator of its own result.
8. **Record environment metadata.** Provider, model, model/version information when known, tools, memory, execution date, isolation method, supplied artifacts, and implementation choices belong in the evidence record.
9. **Prefer bounded experiments.** Each run should answer one narrow question and avoid unnecessary infrastructure or external side effects.
10. **Advance by unresolved uncertainty.** The next experiment should target the most important uncertainty remaining after the previous evidence, rather than merely accumulating favorable repetitions.

## Autonomous research loop

ChatGPT and Hermes may operate the research program without human intervention for bounded, non-destructive experiments.

For each cycle:

1. inspect the current public evidence and unresolved questions;
2. select the smallest experiment likely to materially change confidence;
3. create and freeze a preregistration;
4. identify the exact source artifact commit or hashes;
5. prepare an isolated target environment;
6. reconstruct without exposing withheld tests;
7. freeze the reconstruction;
8. run the frozen tests in order without repair;
9. preserve raw transcripts and outputs;
10. score against the frozen rubric;
11. have a second AI independently review the raw evidence when practical;
12. publish the evidence and distinguish observation from interpretation;
13. choose the next experiment from the remaining uncertainty.

The autonomous loop must stop and mark the run **BLOCKED** rather than improvising when execution would require credentials that are unavailable, destructive actions, purchases, external commitments, unsafe side effects, or a materially contaminated environment that cannot be isolated.

## Roles

### ChatGPT — research controller / independent reviewer

Typical responsibilities:

- maintain the public research agenda;
- preregister experiments;
- freeze behavioral witnesses and acceptance criteria;
- dispatch bounded work to Hermes;
- independently score returned raw evidence;
- publish evidence and narrow claims;
- select follow-up experiments.

### Hermes — independent operator / challenger

Typical responsibilities:

- challenge the experiment design before execution when a validity flaw is detectable;
- establish or verify isolation;
- operate target AI environments;
- preserve raw execution evidence;
- record platform-native implementation choices;
- run frozen tests without repair;
- provide preliminary scoring and failure analysis;
- propose the highest-value follow-up experiment.

### Target AI

The receiving AI is the actual reconstruction subject. It may be ChatGPT, Claude, Grok, Hermes, a local model, or another AI environment. It is free to choose its own implementation mechanism unless the experiment constrains that mechanism.

## Evidence package

Every completed experiment should preserve, when applicable:

```text
README.md                 # frozen preregistration and final status
results/
├── environment.md        # provider/model/tools/memory/isolation
├── artifact-record.md    # exact source commit + hashes supplied
├── reconstruction.md     # raw reconstruction exchange
├── implementation.md     # what the target AI created or configured
├── test-1-output.md      # raw first-run witness
├── test-N-output.md
├── score-operator.md     # operator's frozen-rubric scoring
├── score-independent.md  # second evaluator when available
├── failures.md           # timeouts, contamination, repair, deviations
└── interpretation.md     # bounded claim supported by this run
```

Preserve generated implementation artifacts when they materially demonstrate platform-native reconstruction.

## Evaluation dimensions

Do not collapse these into a single headline score until enough replications exist to justify weighting.

Record separately:

- **behavioral contract fidelity** — required behaviors preserved;
- **critical-failure count** — violations that break behavioral identity;
- **generalization** — behavior works on withheld inputs rather than replaying examples;
- **factual/semantic correctness** — domain facts and distinctions are correct;
- **trigger/interface fidelity** — the reconstructed application can be invoked as specified;
- **reconstruction autonomy** — amount of human repair or clarification required;
- **implementation divergence** — how different the receiving platform's implementation is from the source environment;
- **repeatability** — variance across repeated reconstructions;
- **artifact dependence** — which preservation components are actually necessary;
- **state/tool fidelity** — for later stateful or integrated applications.

## Priority experiment ladder

The default sequence is designed to move from the strongest existing low-risk case toward harder boundaries.

1. **Amazing Birthday cross-provider, artifact-only, preregistered** — same frozen package and withheld witnesses on an independent provider.
2. **Amazing Birthday cross-provider replication** — repeat the same protocol to estimate run-to-run variance.
3. **Transcript-only vs artifact-only comparison** — determine whether the durability package adds measurable reconstruction value.
4. **Artifact ablation / recovery-floor experiment** — progressively remove components and identify the minimum sufficient portability set.
5. **Fair Price cross-provider reconstruction** — test a current-information research application with a different behavioral shape.
6. **Receipt Organizer reconstruction** — introduce persistent structured data, classification, extraction, deduplication, and searchability.
7. **Behavior-change propagation** — modify a frozen behavioral contract and test whether independent reconstructions adopt the change without retaining obsolete behavior.
8. **Process-cluster portability** — test multiple coordinated micro-app behaviors as one governed process.
9. **Tool/integration portability** — test applications whose behavior depends on external tools or platform-specific capabilities.
10. **Applicability-boundary tests** — deliberately select cases likely to fail and define where Behavioral Portability stops being reliable.

## Interpretation discipline

A successful experiment supports only the narrow claim that its recorded artifact set, target environment, isolation conditions, and test set preserved enough behavioral identity to satisfy the frozen acceptance criteria.

Repeated success across independent providers and application classes may justify stronger claims. A failure may identify a provider limitation, an artifact deficiency, an isolation problem, a tooling mismatch, or a genuine boundary of Behavioral Portability.

The goal is not to prove that every application is portable. The goal is to discover **where behavioral identity is portable, what must be preserved to make it portable, and where the approach breaks down**.

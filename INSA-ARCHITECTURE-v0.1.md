# Intelligence-Native Software Architecture (INSA) v0.1

**Status:** Experimental architecture baseline  
**Version:** 0.1  
**Date:** 2026-09-09  
**Scope:** Architecture for software systems in which machine intelligence is a fundamental execution resource  
**Research posture:** Evidence-first; every architectural claim remains subject to falsification by experiment

## 1. Purpose

This document turns the project's emerging Intelligence-Native Software Architecture (INSA) framing into an explicit architecture that can be implemented, challenged, and experimentally tested.

INSA begins with a simple premise:

> **When machine intelligence becomes part of the execution environment, the stable architectural boundary can move upward from implementation detail toward purpose, intent, authority, values, behavioral identity, and evidence.**

The premise is not that code disappears, that deterministic systems are obsolete, or that AI should receive unrestricted autonomy. The question is narrower and more technical:

> **Which responsibilities can safely move from fixed implementation into a governed intelligent execution environment, and what must remain explicit and stable when they do?**

Development by Intent (DbI) remains the project's primary experimental development pattern. Value Architecture remains the project's governance model for agent discretion. Behavioral Identity and Evidence Architecture remain distinct research areas. INSA places them into one system model.

## 2. Working definition

**Intelligence-Native Software Architecture** is the design of software systems that treat machine intelligence as a fundamental execution resource while humans govern purpose, intent, authority, values, acceptable behavior, and evidence.

An INSA system may use models, agents, tools, generated code, deterministic services, databases, APIs, workflows, memory, conventional security mechanisms, and human approval. Intelligence is a component of execution, not a substitute for architecture or governance.

A concise architectural principle is:

> **Humans own purpose, intent, authority delegation, judgment, and acceptance. Intelligence may assume substantial implementation burden only inside an explicit governed envelope.**

## 3. Architectural model

```text
                         HUMAN / PRINCIPAL
                               │
                     purpose + objectives
                               │
                    ┌──────────▼──────────┐
                    │    INTENT BOUNDARY   │
                    │ intent, constraints, │
                    │ acceptance criteria  │
                    └──────────┬──────────┘
                               │
                    ┌──────────▼──────────┐
                    │  AUTHORITY BOUNDARY  │
                    │ permission, scope,   │
                    │ delegation, approval │
                    └──────────┬──────────┘
                               │
                    ┌──────────▼──────────┐
                    │    VALUE BOUNDARY    │
                    │ discretion, conflict,│
                    │ behavioral governance│
                    └──────────┬──────────┘
                               │
                  ┌────────────▼────────────┐
                  │ INTELLIGENT EXECUTION   │
                  │ models / agents / tools │
                  │ code / services / memory│
                  │ coordination / planning │
                  └────────────┬────────────┘
                               │
                    observable behavior
                               │
                    ┌──────────▼──────────┐
                    │   IDENTITY BOUNDARY  │
                    │ target behavior +    │
                    │ preserved invariants │
                    └──────────┬──────────┘
                               │
                    ┌──────────▼──────────┐
                    │   EVIDENCE BOUNDARY  │
                    │ tests, provenance,   │
                    │ audit, evaluation    │
                    └──────────┬──────────┘
                               │
                       human acceptance
                         or correction
```

The five boundaries are the architectural core of INSA v0.1.

## 4. Architecture is not advice

A central design requirement of INSA is to distinguish what the architecture **requires** from what it merely **recommends**.

### 4.1 Architectural invariant

An **architectural invariant** is a condition that must remain true for a system to claim conformance with a declared INSA contract.

An invariant must have:

1. an explicit statement;
2. a defined scope;
3. an enforcement, detection, or evaluation path;
4. evidence sufficient to determine whether it held.

If a statement has no plausible enforcement or evaluation path, INSA v0.1 treats it as guidance or hypothesis, not as an architectural boundary.

### 4.2 Control

A **control** is an implementation mechanism used to enforce, detect, or recover an invariant.

Examples include permission systems, approval gates, schemas, tests, classifiers, event subscriptions, cryptographic hashes, transaction boundaries, sandboxes, audit logs, or multi-agent review.

Controls may change without changing the governing invariant.

### 4.3 Guidance

**Guidance** is a preferred practice that may improve quality but is not required to establish architectural identity or conformance.

Guidance must not be presented as though it were an enforced invariant.

### 4.4 Hypothesis

A **hypothesis** is an architectural proposition not yet supported strongly enough to be treated as an invariant.

Experiments may promote, narrow, revise, or reject hypotheses.

### 4.5 Evidence claim

An **evidence claim** states what has actually been observed under stated conditions. Evidence claims must remain narrower than the architecture they inform.

This distinction is intended to prevent a recurring failure mode in AI architecture: renaming disciplined prompting or good practice as architecture without demonstrating a stable boundary.

## 5. Boundary 1 — Intent

### 5.1 Purpose

The Intent Boundary defines what outcome the principal wants, what constraints apply, and what constitutes acceptable behavior.

It separates **purpose** from **implementation**.

### 5.2 Required artifacts

An INSA application should be able to identify, directly or by reference:

- purpose;
- current intent;
- material constraints;
- acceptance criteria;
- known exclusions or anti-goals;
- authorized changes to the intent contract.

### 5.3 Core invariants

**I-INT-01 — Purpose ownership**  
The intelligent system MUST NOT silently replace the principal's purpose with a different objective merely because the alternative appears more efficient or desirable.

**I-INT-02 — Explicit material change**  
A material change in intent MUST be distinguishable from implementation variation.

**I-INT-03 — Acceptance ownership**  
The principal or explicitly delegated evaluator retains authority to determine whether the intended outcome is acceptable.

**I-INT-04 — Constraint continuity**  
Applicable constraints MUST NOT silently disappear during delegation, reconstruction, or evolution.

### 5.4 What may vary

The execution environment may vary decomposition, planning, code, tool selection, workflow, intermediate representation, or coordination strategy unless one of those mechanisms is itself constrained by another boundary.

### 5.5 Open research questions

- How much intent can remain natural language before ambiguity becomes an architectural defect?
- When should intent be compiled into structured constraints?
- How should conflicts among purpose, constraints, and acceptance criteria be adjudicated?
- Which parts of intent must become executable tests?

## 6. Boundary 2 — Authority

### 6.1 Purpose

The Authority Boundary defines what the intelligent system may do, independent of what it is technically capable of doing.

The governing rule is inherited from Value Architecture:

> **Increasing capability must not silently imply increasing authority.**

### 6.2 Core invariants

**I-AUTH-01 — Capability is not permission**  
The system MUST distinguish technical capability from delegated authority.

**I-AUTH-02 — No self-expansion**  
The system MUST NOT enlarge its own consequential authority merely because expanded authority would make the objective easier to achieve.

**I-AUTH-03 — Least sufficient authority**  
When materially equivalent actions exist, the system SHOULD prefer the action requiring no greater authority than necessary.

**I-AUTH-04 — Revocation sensitivity**  
Material authority changes or revocations MUST be able to invalidate previously permissible consequential actions.

**I-AUTH-05 — Delegation traceability**  
Consequential delegated authority SHOULD be traceable to the principal, policy, role, or prior authorization that granted it.

### 6.3 Typical controls

- scoped credentials;
- capability tokens;
- approval gates;
- spend or resource limits;
- sandbox boundaries;
- tool allowlists;
- role-based access;
- expiration or revocation mechanisms;
- transaction limits;
- human escalation.

### 6.4 Open research questions

- How should natural-language authority be compiled into enforceable permissions?
- What authority can safely be delegated recursively among agents?
- How quickly must an agent become aware of revoked authority?
- Can authority remain portable across model and implementation changes?

## 7. Boundary 3 — Values

### 7.1 Purpose

The Value Boundary governs how an intelligent system exercises discretion when instructions do not uniquely determine an action.

Value Architecture is not a list of attractive adjectives. It is a behavioral governance layer.

The current formal project definition is maintained in [VALUE-ARCHITECTURE-STANDARD-v0.2.md](VALUE-ARCHITECTURE-STANDARD-v0.2.md).

### 7.2 Core invariants

**I-VAL-01 — Values govern discretion**  
Declared values MUST have observable consequences in situations where more than one technically valid action exists.

**I-VAL-02 — Prompt text is not conformance evidence**  
The presence of value language in a prompt, policy, or configuration MUST NOT by itself be treated as evidence that the value is behaviorally durable.

**I-VAL-03 — Conflict handling**  
When material values conflict, the system MUST have a defined resolution or escalation path rather than silently selecting whichever value makes task completion easiest.

**I-VAL-04 — Authority dominates convenience**  
A value such as helpfulness or diligence MUST NOT be used to justify action outside delegated authority.

**I-VAL-05 — Consequential values require tests**  
Claims about values that materially affect consequential behavior SHOULD be backed by conformance tests designed to make violation attractive, convenient, or lower-cost.

### 7.3 Current value set

The project currently investigates twelve values:

1. Human Agency
2. Integrity and Truthfulness
3. Awareness
4. Restraint and Authority Respect
5. Evidence and Epistemic Discipline
6. Continuity
7. Stewardship
8. Privacy and Confidentiality
9. Proportionality
10. Recovery and Reversibility
11. Diligence
12. Human Benefit

These remain experimental until behavioral evidence establishes their portability and durability.

## 8. Boundary 4 — Behavioral Identity

### 8.1 Purpose

The Identity Boundary defines what must remain recognizably invariant when implementation may vary, be regenerated, or evolve.

This boundary is necessary because an intelligence-native application may not have a single stable source tree or runtime path that fully defines its identity.

### 8.2 Identity contract

An INSA Behavioral Identity Contract should distinguish:

- **identity invariants** — behavior that must remain stable;
- **target dimensions** — behavior intentionally being changed;
- **permitted variance** — dimensions allowed to differ without identity failure;
- **forbidden drift** — non-target changes that invalidate preservation;
- **acceptance tests** — observations used to evaluate the preceding categories.

### 8.3 Core invariants

**I-ID-01 — Identity is explicit**  
A claim that an application remained the same application MUST identify the behavioral dimensions being preserved.

**I-ID-02 — Implementation difference is not identity failure**  
Different code, tool use, planning, or prose MUST NOT by itself count as behavioral identity failure unless the implementation mechanism is itself part of a declared invariant.

**I-ID-03 — Targeted change requires a preservation set**  
A deliberate behavioral modification MUST distinguish the behavior intended to change from the non-target behavior expected to remain stable.

**I-ID-04 — Preservation must be evaluated**  
A successful target modification MUST NOT be treated as successful evolution if material non-target identity drift has not been evaluated.

**I-ID-05 — Reconstruction and evolution are separate claims**  
Evidence that an application can be reconstructed consistently MUST NOT be treated as evidence that it can be modified safely while preserving non-target identity.

### 8.4 Current experimental implication

The Behavioral Identity Baseline work provides bounded evidence that recognizable behavior can survive independent reconstruction under controlled conditions.

The subsequent evolution work exposed a stronger architectural problem: **reconstruction stability does not establish evolution stability**. A system may reproduce an existing behavioral contract reliably and still permit non-target drift when one part of intent changes.

INSA therefore treats safe evolution as an independent research problem rather than as an automatic consequence of successful reconstruction.

## 9. Boundary 5 — Evidence

### 9.1 Purpose

The Evidence Boundary defines how humans or independent evaluators can determine what the system did, under what authority and constraints, and whether its behavior remained inside the governed envelope.

Evidence is not an after-the-fact report-writing layer. In INSA it is part of the architecture because increasing implementation freedom makes source inspection alone progressively less sufficient.

### 9.2 Core invariants

**I-EVD-01 — No unsupported execution claims**  
The system MUST NOT claim execution, inspection, verification, or success that did not occur.

**I-EVD-02 — Material provenance**  
Evidence supporting consequential claims SHOULD preserve enough provenance to determine the relevant source, version, inputs, authority, and evaluation context.

**I-EVD-03 — Failure preservation**  
Material failed attempts, deviations, or uncertainty MUST NOT be silently rewritten as clean success when they affect interpretation of the result.

**I-EVD-04 — Claim/evidence separation**  
Observed result, inference, hypothesis, and architectural claim SHOULD be distinguishable.

**I-EVD-05 — Evidence without hidden reasoning**  
Conformance MUST NOT depend on disclosure of private chain-of-thought. Observable behavior, inputs, outputs, tool records, approvals, tests, hashes, provenance, and externally inspectable rationale are sufficient evidence classes.

### 9.3 Evidence strength

INSA experiments should prefer the strongest practical evidence appropriate to the claim:

```text
observation
    ↓
repeatable test
    ↓
controlled comparison
    ↓
independent reconstruction
    ↓
blinded / preregistered evaluation
    ↓
replication across implementation environments
```

Not every system requires the strongest level. Evidence requirements should remain proportional to consequence and claim strength.

## 10. Intelligent Execution Environment

The intelligent execution environment is the implementation freedom zone inside the five governed boundaries.

It may contain:

- foundation models;
- specialized models;
- agents;
- deterministic services;
- generated or conventional code;
- tool adapters;
- databases;
- retrieval systems;
- workflows;
- memory;
- planners;
- message buses;
- event subscriptions;
- human-in-the-loop controls;
- multiple cooperating AI systems.

INSA does not require a particular model provider, orchestration framework, language, or runtime.

### 10.1 Execution principle

> **Intelligence is an execution resource, not a grant of purpose or authority.**

The execution environment may choose implementation mechanisms only within the active intent, authority, value, identity, and evidence contracts.

## 11. Hybrid architecture and deterministic islands

INSA is explicitly hybrid.

Some responsibilities should remain deterministic when exactness, speed, safety, security, compliance, throughput, transactionality, or reproducibility requires it.

Examples include:

- cryptographic operations;
- identity and access control;
- financial transaction boundaries;
- safety interlocks;
- hard real-time loops;
- schema validation;
- database constraints;
- exact arithmetic where approximation is unacceptable;
- regulatory logging requirements;
- irreversible destructive operations;
- resource ceilings.

A useful design rule is:

> **Use intelligence where judgment and adaptation create value; use deterministic controls where ambiguity creates unacceptable risk.**

The boundary between the two is itself an empirical design question.

## 12. INSA application contract

A mature INSA application should be representable by a portable governed package containing the following logical artifacts. The physical representation may vary.

### 12.1 Purpose Record

Why the system exists and who owns that purpose.

### 12.2 Intent Contract

Objectives, constraints, anti-goals, acceptance criteria, and material examples.

### 12.3 Authority Manifest

Allowed actions, prohibited actions, resource limits, delegation scope, approval requirements, expiration, and revocation rules.

### 12.4 Value Profile

Applicable values, conflict rules, domain extensions, and conformance requirements.

### 12.5 Behavioral Identity Contract

Identity invariants, permitted variance, target dimensions, preservation set, and behavioral tests.

### 12.6 Evidence Contract

Required provenance, evaluation, audit records, uncertainty disclosure, and acceptance evidence.

### 12.7 Implementation Adapters

Current models, tools, services, code, prompts, workflows, and integration mechanisms used to realize the governed package.

Implementation adapters are replaceable unless explicitly elevated into an invariant.

### 12.8 Change Record

Versioned changes to intent, authority, values, identity, evidence requirements, or implementation, including the basis for accepting the change.

## 13. Execution lifecycle

An INSA system follows a governed loop rather than a simple prompt-response loop.

```text
1. DEFINE
   establish purpose, intent, constraints, identity, evidence requirements

2. AUTHORIZE
   grant only the authority needed for the current objective

3. GOVERN
   apply values and policies to discretionary choices

4. EXECUTE
   intelligence selects or generates implementation mechanisms

5. OBSERVE
   capture behavior, state changes, tool actions, failures, and provenance

6. EVALUATE
   compare observable behavior with acceptance and identity contracts

7. ACCEPT / CORRECT
   human or delegated evaluator accepts, rejects, or revises the system

8. PRESERVE
   retain the governing package and sufficient evidence

9. EVOLVE
   change target behavior while explicitly protecting non-target invariants

10. RECONSTRUCT
    when useful, realize the governed application through a new implementation
```

## 14. Safe evolution protocol

The evolution problem is important enough to make explicit in v0.1.

Any material behavioral evolution should define:

```text
M = mutation set
    behavior intentionally allowed or required to change

P = preservation set
    behavior required to remain stable

V = permitted variance
    dimensions allowed to vary without failure

A = acceptance tests
    tests of the intended modification

G = preservation gates
    tests of the non-target identity
```

A change is not accepted merely because `A` passes.

A governed evolution succeeds only when:

```text
A passes
AND
G passes
AND
no authority/value/evidence invariant is violated
```

If preservation cannot be established, the result should be classified as uncertain or failed evolution rather than silently accepted.

This model turns the project's recent modification-and-preservation difficulty into a first-class architectural requirement rather than an experimental footnote.

## 15. Failure taxonomy

INSA v0.1 distinguishes at least seven failure classes.

### F1 — Intent drift

The executed objective no longer matches the governing intent.

### F2 — Authority drift

The system acts outside, beyond, or after revocation of delegated authority.

### F3 — Value drift

The system's discretionary behavior ceases to exhibit the declared governing values.

### F4 — Identity drift

Non-target behavioral identity changes materially during reconstruction or evolution.

### F5 — Evidence failure

The system may or may not have behaved correctly, but the evidence is insufficient, misleading, missing, or unverifiable.

### F6 — Implementation failure

The selected implementation mechanism fails while the governing architecture remains intact.

### F7 — Awareness failure

The system continues on materially stale assumptions after a relevant change in environment, dependency, state, authority, or risk.

A useful diagnostic principle follows:

> **Do not repair an architectural failure by merely swapping models, and do not redesign the architecture when only an implementation adapter failed.**

## 16. Current evidence map

INSA v0.1 is not claiming that every boundary has been proven. The present research record supports different parts of the architecture at different strengths.

| Area | Current posture |
|---|---|
| Intent-layer development / DbI | Demonstrated as feasible for bounded language- and reasoning-centric applications |
| Behavioral reconstruction | Strong bounded evidence across controlled reconstructions |
| Cross-implementation portability | Promising bounded evidence; not universal |
| Behavioral Identity measurement | Operational enough for controlled experiments |
| Safe targeted evolution | Not yet demonstrated reliably; remains an active architectural problem |
| Value Architecture vocabulary | Formalized in experimental standard v0.2 |
| Value conformance | Early; requires stronger adversarial behavioral testing |
| Authority architecture | Conceptually defined; enforcement portability remains under-tested |
| Evidence architecture | Relatively mature within the experimental program |
| Universal INSA applicability | Not established and not currently claimed |

Negative results remain evidence. A failed boundary test should narrow INSA rather than be explained away.

## 17. Research program derived from the architecture

Future experiments should identify which INSA boundary they are testing before execution.

### INSA-ID-E1 — Targeted evolution with preservation

**Question:** Can a system modify one declared behavioral dimension while preserving an explicit non-target identity set?

**Why now:** The existing evidence indicates that reconstruction stability and evolution stability are different properties.

**Required design improvement:** Freeze `M`, `P`, `V`, `A`, and `G` before generation. Treat preservation failure as independently meaningful even when the target modification succeeds.

### INSA-AUTH-E1 — Revocation and least authority

**Question:** Does an agent reliably stop or reroute consequential action when authority is narrowed or revoked after planning has begun?

**Target:** Authority Boundary.

### INSA-VAL-E1 — Values under cost and conflict

**Question:** Does a declared value continue to govern when following it creates measurable cost, delay, loss of task score, or conflict with another value?

**Target:** Value Boundary.

### INSA-ID-E2 — Cross-runtime identity portability

**Question:** Can the same Behavioral Identity Contract be realized by materially different model/tool stacks without identity-breaking behavior?

**Target:** Identity Boundary and implementation freedom.

### INSA-EVD-E1 — Minimum sufficient evidence

**Question:** What is the smallest evidence package that still permits a blinded evaluator to determine conformance with acceptable reliability?

**Target:** Evidence Boundary.

### INSA-INT-E1 — Intent compilation

**Question:** When does converting natural-language intent into structured constraints improve reliability, and when does it overconstrain useful intelligence?

**Target:** Intent Boundary.

## 18. Experiment discipline

Every future INSA experiment should state:

1. the architectural boundary under test;
2. the invariant or hypothesis being tested;
3. the observable failure condition;
4. what result would narrow or falsify the claim;
5. the implementation mechanisms allowed to vary;
6. the evidence required for adjudication;
7. the stopping rules;
8. the claim that will be permitted if the experiment passes;
9. the claim that will remain prohibited even if it passes.

This is intended to prevent experiments from becoming demonstrations whose interpretation expands after the result is known.

## 19. What INSA v0.1 does not claim

INSA v0.1 does **not** claim that:

- code is obsolete;
- all software should be agentic;
- natural language is sufficient for every requirement;
- AI should receive broad autonomous authority;
- a model's prompt is an architecture;
- reconstructed behavior is deterministic;
- safe evolution has been solved;
- stated values are reliable without testing;
- safety-critical or regulated systems should move their critical boundaries into probabilistic reasoning;
- one model, vendor, framework, or agent runtime is required;
- the five-boundary model is final.

The architecture earns scope only through evidence.

## 20. Architectural decision rule

For any proposed INSA capability, ask five questions:

1. **Intent:** What outcome is the intelligence actually serving?
2. **Authority:** What is it allowed to do to pursue that outcome?
3. **Values:** How should it choose when more than one permitted path exists?
4. **Identity:** What behavior must remain stable while implementation varies or evolves?
5. **Evidence:** How will we know that the preceding four were respected?

If one of these questions has no meaningful answer, the system is not yet fully governed at the intelligence-native boundary.

## 21. Project position after v0.1

The project has moved through three stages:

```text
Stage 1 — Discovery
Can useful software behavior be developed at the intent layer?

Stage 2 — Experimental validation
Can behavioral identity be reconstructed, measured, compared, and challenged?

Stage 3 — Architecture
What stable boundaries are required when implementation becomes increasingly intelligent and fluid?
```

INSA v0.1 marks the beginning of Stage 3.

The immediate objective is no longer to accumulate demonstrations that AI can implement intent. It is to determine, boundary by boundary, **what must remain explicit, governed, testable, and stable for intelligence-native software to be trustworthy engineering rather than merely capable generation.**

## 22. Relationship to existing project documents

- [RESEARCH-DIRECTION.md](RESEARCH-DIRECTION.md) records the emergence of the broader INSA framing.
- [VALUE-ARCHITECTURE-STANDARD-v0.2.md](VALUE-ARCHITECTURE-STANDARD-v0.2.md) defines the current experimental Value Architecture vocabulary and conformance model.
- [EVIDENCE.md](EVIDENCE.md) summarizes bounded Development by Intent evidence.
- [BEHAVIORAL-PORTABILITY.md](BEHAVIORAL-PORTABILITY.md) records the portability hypothesis.
- [experiments/](experiments/) preserves the controlled experimental record.

This document does not rewrite those artifacts. It defines the architecture that the next generation of experiments will attempt to validate or break.

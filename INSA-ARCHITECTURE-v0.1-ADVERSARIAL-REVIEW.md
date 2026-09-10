# INSA Architecture v0.1 — Adversarial Review

**Date:** 2026-09-09  
**Artifact under review:** [`INSA-ARCHITECTURE-v0.1.md`](INSA-ARCHITECTURE-v0.1.md)  
**Review posture:** Attempt to break the architecture before using it to justify further experiments  
**Disposition:** **REVISION_REQUIRED_BEFORE_ARCHITECTURE_FREEZE**

> **Reviewer disclosure:** This was an internal AI-assisted methodological review within the PI-led research process, not independent external validation. The original artifact did not contemporaneously record a sufficiently specific reviewer/model identity, exact model version, or authoring-context access condition. See [`REVIEWER-DISCLOSURES.md`](REVIEWER-DISCLOSURES.md). Unknown details are intentionally not reconstructed after the fact.

## 1. Executive finding

INSA v0.1 succeeds at turning the project's prior research direction into an explicit architectural model. The five-boundary framing is useful and substantially more falsifiable than the earlier conceptual outline.

However, the first adversarial review found several internal inconsistencies and underspecified boundaries that should be corrected before the architecture is treated as a frozen experimental baseline.

The most important positive result of the review is that the architecture **can be criticized at the architectural level**. The defects are not primarily wording defects; they expose real design questions.

The most important negative result is that v0.1 does not yet fully satisfy its own criterion for distinguishing architecture from guidance.

## 2. Review criteria

The review asked:

1. Is each proposed boundary genuinely architectural rather than process guidance?
2. Is each declared invariant actually mandatory and testable?
3. Are controls being mistaken for invariants?
4. Are any boundaries incorrectly modeled as sequential when they are cross-cutting?
5. Does the architecture explain the reconstruction/evolution evidence without rewriting it?
6. Could an experiment falsify or narrow each major claim?
7. Is a major boundary missing?
8. Can the architecture represent stateful, multi-agent, and hybrid deterministic/intelligent systems?
9. Can an implementation claim conformance without exploiting ambiguity in the specification?

## 3. Findings summary

| ID | Severity | Finding | Required action |
|---|---|---|---|
| AR-01 | HIGH | Some items labeled invariants use SHOULD rather than MUST | Reclassify as guidance or make them true conformance requirements |
| AR-02 | HIGH | Evidence is modeled too sequentially | Recast Evidence as a cross-cutting verification plane |
| AR-03 | HIGH | Safe evolution lacks frozen baseline binding | Add baseline/version/hash binding before mutation |
| AR-04 | HIGH | Preservation semantics can be under-specified | Define formal relationship among mutation, preservation, and permitted variance sets |
| AR-05 | HIGH | Authority revocation has no required freshness model | Add authority freshness / awareness requirement for consequential action |
| AR-06 | MEDIUM | Declared values and embodied values remain too easy to conflate | Separate Value Declaration from Value Conformance status |
| AR-07 | MEDIUM | Evidence strength is presented as a total ordering | Replace ladder with multidimensional evidence model |
| AR-08 | MEDIUM | Stateful application continuity is under-modeled | Add explicit State / Continuity Contract or equivalent |
| AR-09 | MEDIUM | Multi-agent delegation chain is under-specified | Model delegated authority and provenance across agent-to-agent handoff |
| AR-10 | MEDIUM | Deterministic/intelligent boundary lacks a decision test | Add risk/reversibility criterion rather than only design guidance |
| AR-11 | MEDIUM | Acceptance authority is ambiguous under delegation | Separate evaluation execution from final acceptance authority |
| AR-12 | LOW | Normative terms are used without a formal normative-language section | Add normative language definition |

## 4. Detailed findings

### AR-01 — Invariants that use SHOULD

**Severity:** HIGH

v0.1 defines an architectural invariant as a condition that must remain true for a system to claim conformance. Several later statements labeled as invariants use **SHOULD** rather than **MUST**.

Examples include least-sufficient authority, delegation traceability, and consequential-value testing.

This creates exactly the ambiguity the architecture says it is designed to prevent.

#### Why it matters

If an implementation can violate a declared invariant while remaining conformant because the statement was only advisory, the construct is not functioning as an invariant.

#### Required correction

Every item labeled `I-*` must be one of:

1. a true mandatory invariant using MUST / MUST NOT; or
2. removed from the invariant set and explicitly labeled guidance.

No third category should be hidden inside the invariant list.

---

### AR-02 — Evidence is a plane, not merely the final boundary

**Severity:** HIGH

The v0.1 diagram places Evidence after observable behavior and Behavioral Identity. That is useful as an evaluation loop but incomplete architecturally.

Evidence requirements also apply to:

- the source and version of intent;
- the authority grant in force at execution time;
- value declarations and conformance status;
- implementation changes;
- tool actions;
- state changes;
- identity baselines;
- human approvals.

#### Why it matters

A system can produce correct output while lacking evidence that the action was authorized. Evidence therefore cannot be modeled only as post-output evaluation.

#### Required correction

Represent Evidence as a **cross-cutting verification plane** intersecting Intent, Authority, Values, Execution, Identity, State, and Acceptance.

The execution lifecycle may still end in evaluation, but the architecture diagram should not imply that evidence begins only after behavior occurs.

---

### AR-03 — Safe evolution lacks frozen baseline binding

**Severity:** HIGH

v0.1 defines:

```text
M = mutation set
P = preservation set
V = permitted variance
A = acceptance tests
G = preservation gates
```

This is a meaningful advance, but it does not explicitly bind those sets to a frozen pre-change baseline.

#### Attack

An operator could modify the application, observe drift, and then reinterpret the preservation set or permitted variance to make the result appear acceptable.

#### Required correction

Add:

```text
B = frozen baseline
    version/hash of intent, identity contract, tests, and source evidence
```

Before mutation begins, freeze and bind:

```text
B + M + P + V + A + G
```

Any post hoc change requires a new experiment or explicit protocol amendment.

---

### AR-04 — Mutation / preservation / variance relationships need formal constraints

**Severity:** HIGH

`M`, `P`, and `V` are useful concepts but are not yet formally constrained.

Questions remain:

- Can one dimension appear in both `M` and `P`?
- Is `V` a subset of `P`, orthogonal to it, or global?
- What happens when a preservation dimension contains natural stochastic variance?
- How is unclassified behavior treated?

#### Required correction

At minimum:

```text
M ∩ P = ∅
```

Every scored behavioral dimension should be classified before execution as one of:

- target change (`M`);
- required preservation (`P`);
- explicitly permitted variance (`V`);
- out of scope (`O`).

The protocol should define how variance tolerances attach to each dimension rather than treating `V` as an unbounded escape hatch.

---

### AR-05 — Authority revocation needs a freshness model

**Severity:** HIGH

v0.1 correctly requires sensitivity to authority revocation but does not define how stale an authority view may be before consequential action.

This is the architectural version of the project's earlier awareness / doorbell problem.

#### Attack

An agent obtains authority at `t0`, plans a consequential action, authority is revoked at `t1`, and the agent executes at `t2` using stale state.

The architecture says revocation must matter but does not say how the system becomes aware of it.

#### Required correction

For consequential actions, the Authority Contract should declare an **authority freshness policy**, such as:

- event-driven revocation subscription;
- mandatory revalidation before commit;
- maximum authority-cache age;
- transaction-scoped capability token;
- explicit human approval at execution time.

The mechanism may vary. The freshness requirement cannot remain implicit.

---

### AR-06 — Declared value vs embodied value

**Severity:** MEDIUM

v0.1 says prompt text is not conformance evidence, which is correct. However, the application contract currently contains a `Value Profile` without explicitly separating the value declaration from its evidence status.

#### Required correction

Represent at least:

```text
Value Declaration
Value Conformance Status
Value Conformance Evidence
```

A system may declare a value while its conformance status remains `UNTESTED`, `PARTIAL`, `FAILED`, or `PASS_UNDER_DEFINED_CONDITIONS`.

This prevents a declared Value Profile from becoming an implied conformance claim.

---

### AR-07 — Evidence is multidimensional, not a single ladder

**Severity:** MEDIUM

v0.1 presents evidence strength as:

```text
observation
→ repeatable test
→ controlled comparison
→ independent reconstruction
→ blinded / preregistered evaluation
→ replication across environments
```

This is too linear.

A blinded evaluation is not inherently stronger than every independent reconstruction; preregistration, independence, repetition, ecological validity, cross-runtime portability, and evaluator blinding are different dimensions.

#### Required correction

Replace the ladder with an evidence vector or matrix containing dimensions such as:

- repeatability;
- evaluator independence;
- operator independence;
- blinding;
- preregistration;
- cross-runtime replication;
- sample breadth;
- provenance quality;
- adversariality;
- ecological validity.

Claims should state which dimensions are present rather than implying a universal rank.

---

### AR-08 — Stateful application continuity is under-modeled

**Severity:** MEDIUM

The existing application contract covers purpose, intent, authority, values, behavioral identity, evidence, implementation, and change history. Stateful applications require an additional question:

> What state must survive, and what makes that state trustworthy?

The Receipt Organizer work already demonstrated that application state may be part of continuity.

#### Required correction

Add a **State / Continuity Contract** defining, where applicable:

- durable state;
- derived state;
- authoritative source of truth;
- state provenance;
- migration rules;
- reconstruction rules;
- retention / deletion requirements;
- consistency expectations;
- failure recovery point.

Behavioral identity and state identity should not be assumed to be the same thing.

---

### AR-09 — Multi-agent delegation chain is under-specified

**Severity:** MEDIUM

v0.1 permits multiple cooperating AI systems but does not fully define authority propagation.

#### Attack

Agent A has authority to perform a task and delegates to Agent B. Does B inherit all of A's authority, only the minimum required subset, or none without a separate grant?

#### Required correction

The Authority Manifest should support a delegation chain containing:

- originating principal;
- delegating actor;
- receiving actor;
- delegated scope;
- maximum subdelegation scope;
- expiration;
- revocation behavior;
- evidence/provenance link.

No agent should be able to manufacture transitive authority merely from task assignment.

---

### AR-10 — Deterministic versus intelligent boundary needs a decision test

**Severity:** MEDIUM

The statement "use intelligence where judgment and adaptation create value; use deterministic controls where ambiguity creates unacceptable risk" is useful guidance but not yet an architectural test.

#### Required correction

Define a decision matrix based on at least:

- consequence of error;
- reversibility;
- required latency;
- acceptable variance;
- auditability;
- security sensitivity;
- regulatory exactness;
- transactionality;
- cost of false positive / false negative.

The output may still be a judgment, but the architecture should make the placement decision inspectable.

---

### AR-11 — Evaluation execution versus acceptance authority

**Severity:** MEDIUM

v0.1 says the principal or delegated evaluator retains authority to determine acceptance. This can collapse two distinct roles:

- **evaluator:** runs or interprets acceptance tests;
- **acceptance authority:** has authority to accept the result for the principal.

An automated evaluator may be authorized to score without being authorized to make a consequential release decision.

#### Required correction

Separate:

```text
Evaluation Authority
Acceptance Authority
```

These may be held by the same actor but should not be assumed equivalent.

---

### AR-12 — Normative language

**Severity:** LOW

The document uses MUST, MUST NOT, and SHOULD but does not formally define normative semantics.

#### Required correction

Add a short normative language section consistent with the Value Architecture standard.

## 5. Is a sixth boundary missing?

The review considered whether INSA requires a sixth top-level boundary for **Security / Trust** or **State / Continuity**.

### Security / Trust

Current disposition: **do not add a sixth Security Boundary yet**.

Reasoning:

- authentication, authorization enforcement, isolation, credential scope, and transaction controls are largely mechanisms supporting the Authority, Evidence, and deterministic-control layers;
- promoting Security to a distinct intelligence-native boundary risks duplicating conventional security architecture without demonstrating a new architectural responsibility;
- however, experiments may prove this assessment wrong.

Security remains mandatory engineering, but v0.1 has not yet shown that it is a separate *intelligence-native* boundary.

### State / Continuity

Current disposition: **add State / Continuity as a cross-cutting contract, not yet as a sixth boundary**.

Reasoning:

- state participates in Intent, Identity, Evidence, and Execution;
- state continuity may be application-specific rather than universal;
- a stateful application cannot be adequately modeled without explicit state semantics.

This decision should be revisited after stateful INSA experiments.

## 6. Does the five-boundary model survive first contact?

**Tentatively, yes.**

The review did not identify a compelling reason to remove any of the five boundaries:

- **Intent** is distinct because it establishes purpose and desired outcome.
- **Authority** is distinct because permission is not reducible to purpose or values.
- **Values** are distinct because discretion remains after purpose and permission are known.
- **Identity** is distinct because continuity across implementation change is not reducible to intent alone.
- **Evidence** is distinct because correctness, authorization, and preservation claims require external verification.

The required structural correction is that Evidence should be represented as a cross-cutting plane rather than merely a final sequential boundary.

## 7. Architecture changes required before freeze

A revised candidate should make at least the following changes:

1. add formal normative language;
2. ensure every `I-*` item is mandatory or reclassify it as guidance;
3. redraw Evidence as a cross-cutting plane;
4. add frozen baseline `B` to safe evolution;
5. formalize `M`, `P`, `V`, and out-of-scope classification;
6. add authority freshness / revalidation semantics;
7. separate value declaration from value conformance status;
8. replace evidence ladder with multidimensional evidence profile;
9. add State / Continuity Contract;
10. add multi-agent delegation-chain semantics;
11. add deterministic/intelligent placement criteria;
12. separate evaluation authority from acceptance authority.

## 8. Experimental consequence

**Do not freeze or preregister INSA-ID-E1 against v0.1 as written.**

The architecture itself has exposed corrections that materially affect the experiment design, especially baseline binding and preservation-set semantics.

The correct next step is:

```text
INSA v0.1
   ↓
adversarial review
   ↓
revision
   ↓
INSA v0.2 candidate
   ↓
architecture freeze gate
   ↓
INSA-ID-E1 preregistration
   ↓
execution only after separate GO
```

## 9. Review disposition

**REVISION_REQUIRED_BEFORE_ARCHITECTURE_FREEZE**

This is a productive result.

The first explicit INSA architecture has already done something the earlier framing could not: it has made architectural defects concrete enough to identify before an experiment is run.
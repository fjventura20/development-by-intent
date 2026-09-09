# Intelligence-Native Software Architecture (INSA) v0.2 — Candidate

**Status:** Candidate architecture — not frozen  
**Version:** 0.2-candidate  
**Date:** 2026-09-09  
**Supersedes for review purposes:** [`INSA-ARCHITECTURE-v0.1.md`](INSA-ARCHITECTURE-v0.1.md)  
**Review basis:** [`INSA-ARCHITECTURE-v0.1-ADVERSARIAL-REVIEW.md`](INSA-ARCHITECTURE-v0.1-ADVERSARIAL-REVIEW.md)  
**Research posture:** Evidence-first; architecture remains provisional until boundary tests support it

## 1. Purpose

INSA defines an experimental architecture for software systems in which machine intelligence is a fundamental execution resource rather than merely a development aid.

The central architectural question is:

> **Which responsibilities can safely move from fixed implementation into a governed intelligent execution environment, and what must remain explicit, enforceable, testable, and stable when they do?**

INSA does not assume that code disappears, that probabilistic reasoning replaces deterministic controls, or that greater capability implies greater autonomy.

The core principle is:

> **Humans own purpose, intent, authority delegation, judgment, and acceptance. Intelligence may assume substantial implementation burden only inside an explicit governed envelope.**

Development by Intent (DbI) is one experimental development pattern within INSA. Value Architecture governs discretion. Behavioral Identity defines continuity under implementation change. Evidence Architecture makes claims inspectable. Conventional software mechanisms remain part of the architecture wherever they are the better control.

## 2. Normative language

The key words **MUST**, **MUST NOT**, **REQUIRED**, **SHOULD**, **SHOULD NOT**, and **MAY** are used normatively.

For this architecture:

- **MUST / MUST NOT** define architectural conformance requirements.
- **SHOULD / SHOULD NOT** define guidance that may be overridden with an explicit reason.
- **MAY** identifies permitted variation.

A statement labeled as an **invariant** MUST use mandatory semantics. Advisory guidance is never labeled as an invariant.

## 3. Architectural premise

When implementation can be generated, selected, coordinated, or regenerated dynamically, source structure alone becomes an incomplete definition of the application.

INSA therefore places the stable governed envelope around five architectural concerns:

1. **Intent** — what outcome is being served.
2. **Authority** — what actions are permitted.
3. **Values** — how discretion is governed among permitted actions.
4. **Behavioral Identity** — what must remain stable while implementation varies or evolves.
5. **Evidence** — how conformance with the other boundaries can be established.

The **Intelligent Execution Environment** operates inside that envelope.

State, continuity, security, deterministic controls, and multi-agent delegation are modeled as cross-cutting contracts or implementation mechanisms unless evidence later justifies a separate intelligence-native boundary.

## 4. Architecture versus guidance

INSA distinguishes five kinds of statements.

### 4.1 Architectural invariant

A condition that MUST remain true for a system to claim conformance with a declared INSA contract.

Every invariant requires:

- explicit scope;
- a detection, enforcement, or evaluation path;
- evidence adequate to determine whether the invariant held.

### 4.2 Control

A technical mechanism that enforces, detects, or recovers an invariant.

Examples include permissions, approval gates, schemas, event subscriptions, tests, sandboxes, transactions, hashes, audit logs, and deterministic services.

A control may change without changing the invariant it protects.

### 4.3 Guidance

A preferred engineering practice that is not required for architectural conformance.

### 4.4 Hypothesis

A proposition that remains experimentally unresolved.

### 4.5 Evidence claim

A bounded statement describing what has actually been observed under specified conditions.

The architecture MUST NOT promote guidance or prompt discipline into an architectural invariant merely by naming it as such.

## 5. Corrected system model

Evidence is cross-cutting rather than merely the final step in a pipeline.

```text
                              PRINCIPAL
                                 │
                         purpose / objectives
                                 │
                    ┌────────────▼────────────┐
                    │       INTENT BOUNDARY    │
                    │ intent / constraints /   │
                    │ acceptance criteria      │
                    └────────────┬────────────┘
                                 │
                    ┌────────────▼────────────┐
                    │     AUTHORITY BOUNDARY   │
                    │ scope / delegation /     │
                    │ approval / revocation    │
                    └────────────┬────────────┘
                                 │
                    ┌────────────▼────────────┐
                    │       VALUE BOUNDARY     │
                    │ discretion / conflicts / │
                    │ governing dispositions  │
                    └────────────┬────────────┘
                                 │
                  ┌──────────────▼──────────────┐
                  │ INTELLIGENT EXECUTION ENV.  │
                  │ models / agents / tools /   │
                  │ code / services / workflows │
                  └──────────────┬──────────────┘
                                 │
                        observable behavior
                                 │
                    ┌────────────▼────────────┐
                    │     IDENTITY BOUNDARY    │
                    │ target change /          │
                    │ preserved invariants     │
                    └────────────┬────────────┘
                                 │
                     evaluation / acceptance
                                 │
                              PRINCIPAL

  ┌────────────────────────────────────────────────────────────┐
  │                  EVIDENCE / VERIFICATION PLANE              │
  │ intent provenance • authority state • value conformance    │
  │ execution records • state provenance • identity baselines  │
  │ tests • failures • evaluator records • acceptance records  │
  └────────────────────────────────────────────────────────────┘
             intersects every stage and boundary above
```

## 6. Boundary 1 — Intent

### 6.1 Responsibility

The Intent Boundary defines the outcome the principal wants, the material constraints that apply, and the criteria by which success will be judged.

It separates **purpose and desired behavior** from **implementation mechanism**.

### 6.2 Required contract elements

Where material to the application, the Intent Contract MUST identify or reference:

- principal / purpose owner;
- purpose;
- current objective or intent;
- material constraints;
- anti-goals or prohibited outcomes;
- acceptance criteria;
- version or revision identity;
- effective time or state when relevant.

### 6.3 Invariants

**I-INT-01 — Purpose ownership**  
The system MUST NOT silently substitute a different purpose for the principal's declared purpose.

**I-INT-02 — Material-change visibility**  
A material change in intent MUST be distinguishable in the record from implementation variation.

**I-INT-03 — Constraint continuity**  
Applicable material constraints MUST NOT silently disappear during delegation, reconstruction, restart, or evolution.

**I-INT-04 — Version binding**  
Consequential execution MUST be attributable to the intent version that governed it.

### 6.4 Guidance

- Natural language MAY be used where ambiguity is acceptable.
- Structured constraints SHOULD be introduced when ambiguity materially increases risk or evaluation difficulty.
- Acceptance criteria SHOULD be executable where practical, but executable tests are not required for every human judgment.

## 7. Boundary 2 — Authority

### 7.1 Responsibility

The Authority Boundary defines what actions the system is permitted to perform, independent of what it is technically capable of performing.

The governing principle is:

> **Increasing capability MUST NOT silently imply increasing authority.**

### 7.2 Required contract elements

For consequential actions, the Authority Manifest MUST identify or derive:

- originating principal or authority source;
- authorized actor or role;
- allowed action scope;
- prohibited action scope when material;
- resource or spend limits where relevant;
- delegation permission and limits;
- approval requirements;
- expiration or validity conditions;
- revocation mechanism or freshness policy;
- evidence required for consequential commit.

### 7.3 Invariants

**I-AUTH-01 — Capability is not permission**  
The system MUST distinguish technical capability from delegated authority.

**I-AUTH-02 — No self-expansion**  
The system MUST NOT enlarge its own consequential authority merely because broader authority would make the objective easier to achieve.

**I-AUTH-03 — Scope preservation**  
Delegation MUST NOT create authority greater than the delegating actor is permitted to delegate.

**I-AUTH-04 — Revocation effectiveness**  
A revoked or expired authority grant MUST NOT remain valid for consequential commit merely because planning began while the grant was active.

**I-AUTH-05 — Freshness before consequential commit**  
Before a consequential irreversible or externally committing action, the system MUST satisfy the authority-freshness rule declared by the Authority Manifest.

**I-AUTH-06 — Delegation traceability**  
Consequential delegated authority MUST be traceable to an originating grant.

### 7.4 Authority freshness mechanisms

The manifest MAY satisfy `I-AUTH-05` by one or more mechanisms:

- event-driven revocation subscription;
- capability token valid for the transaction;
- mandatory revalidation immediately before commit;
- maximum authority-cache age;
- execution-time human approval;
- another control that provides equivalent freshness evidence.

The mechanism may vary. The freshness requirement may not be implicit.

### 7.5 Guidance

The system SHOULD use no more authority than required for an effective action when materially equivalent alternatives exist.

This is guidance unless a deployment promotes least-authority selection into its own mandatory policy.

## 8. Multi-agent authority delegation

When one intelligent actor delegates to another, task assignment alone MUST NOT create unrestricted transitive authority.

A consequential delegation record MUST be able to identify:

```text
originating principal
       ↓
delegating actor
       ↓
receiving actor
       ↓
delegated scope
       ↓
subdelegation limit
       ↓
expiration / revocation semantics
```

**I-AUTH-07 — No authority manufacture by handoff**  
An agent MUST NOT infer that another agent possesses consequential authority solely because the task was handed to it.

## 9. Boundary 3 — Values

### 9.1 Responsibility

The Value Boundary governs how the system exercises discretion when intent and authority still permit more than one technically valid action.

The current project vocabulary is maintained in [VALUE-ARCHITECTURE-STANDARD-v0.2.md](VALUE-ARCHITECTURE-STANDARD-v0.2.md).

### 9.2 Value declaration versus conformance

INSA separates:

```text
Value Declaration
    what the system claims should govern discretion

Value Conformance Status
    UNTESTED / PARTIAL / PASS_UNDER_DEFINED_CONDITIONS / FAILED

Value Conformance Evidence
    tests and observations supporting that status
```

A declared value is not an established behavioral property.

### 9.3 Invariants

**I-VAL-01 — Explicit governing values**  
If a system claims that values govern discretionary behavior, those values MUST be explicitly identifiable or referenceable.

**I-VAL-02 — No declaration-as-proof**  
Prompt text, policy text, or a Value Declaration MUST NOT by itself be treated as evidence that the value is behaviorally embodied.

**I-VAL-03 — Conflict path**  
When applicable declared values materially conflict, the system MUST have a defined resolution or escalation path.

**I-VAL-04 — Authority precedence**  
A declared value MUST NOT be used to justify action outside delegated authority.

**I-VAL-05 — Conformance-status honesty**  
The system MUST NOT represent an untested or failed value as behaviorally conformant.

### 9.4 Guidance

Consequential values SHOULD be tested under conditions where violation is faster, cheaper, more convenient, or improves another task metric. Easy compliance is weak evidence of a durable behavioral disposition.

## 10. Boundary 4 — Behavioral Identity

### 10.1 Responsibility

The Identity Boundary defines what behavior must remain stable while implementation may vary, be reconstructed, or intentionally evolve.

Behavioral Identity is not assumed to equal source-code identity, prompt identity, model identity, or state identity.

### 10.2 Behavioral Identity Contract

The contract MUST identify the behavioral dimensions relevant to any identity or preservation claim.

For an evolution experiment or governed change, each relevant dimension MUST be classified before execution as one of:

- **M — Mutation set:** behavior required or permitted to change;
- **P — Preservation set:** behavior required to remain within a defined envelope;
- **V — Permitted variance:** variance explicitly allowed for a specified dimension;
- **O — Out of scope:** behavior not used to adjudicate the change.

A variance allowance MUST be attached to a defined dimension. `V` MUST NOT function as a global escape hatch.

### 10.3 Set constraints

At minimum:

```text
M ∩ P = ∅
```

A scored dimension MUST NOT be simultaneously classified as both target mutation and required preservation.

### 10.4 Invariants

**I-ID-01 — Explicit identity basis**  
A claim that an application remained the same application MUST identify the dimensions or contract used to define sameness.

**I-ID-02 — Implementation freedom**  
Different code, model, tool use, planning, or prose MUST NOT by itself count as behavioral identity failure unless the implementation mechanism is explicitly part of the identity contract.

**I-ID-03 — Target/preservation separation**  
A targeted behavioral change MUST define its mutation and preservation dimensions before the change is evaluated.

**I-ID-04 — Preservation evaluation**  
A target modification MUST NOT be accepted as successful governed evolution if required preservation dimensions have not been evaluated.

**I-ID-05 — Reconstruction/evolution separation**  
Evidence of stable reconstruction MUST NOT be represented as evidence of safe targeted evolution unless evolution preservation has been tested separately.

**I-ID-06 — Baseline binding**  
A governed evolution claim MUST bind its mutation and preservation contract to a frozen pre-change baseline.

## 11. Safe evolution contract

The corrected safe-evolution model is:

```text
B = frozen baseline
    version/hash of governing intent, identity contract,
    tests, and relevant source evidence before mutation

M = mutation set
    behavior intentionally required or allowed to change

P = preservation set
    behavior required to remain inside its frozen envelope

V = permitted variance
    dimension-specific tolerance or allowed stochastic variation

O = out-of-scope dimensions
    explicitly excluded from adjudication

A = acceptance tests
    evidence that the intended mutation occurred

G = preservation gates
    evidence that non-target identity remained inside bounds
```

Before mutation begins, the governed experiment or change MUST freeze or otherwise immutably identify:

```text
B + M + P + V + O + A + G
```

Post hoc alteration requires a new version, protocol amendment, or new experiment and MUST remain visible in the evidence record.

A governed evolution succeeds only when:

```text
A passes
AND
G passes
AND
authority invariants pass
AND
value-governance invariants pass
AND
evidence requirements pass
```

A target behavior changing successfully is not sufficient by itself.

## 12. State / Continuity Contract

State is cross-cutting and application-dependent. It is not promoted to a sixth INSA boundary in v0.2-candidate, but stateful applications cannot claim continuity without explicit state semantics.

Where durable state exists, the State / Continuity Contract MUST identify or derive as applicable:

- authoritative source of truth;
- durable versus derived state;
- state version;
- provenance;
- retention / deletion requirements;
- migration rules;
- reconstruction rules;
- consistency expectations;
- recovery point or checkpoint requirements;
- state elements that participate in behavioral identity.

### State invariants

**I-STATE-01 — No silent authoritative-state substitution**  
A system MUST NOT silently replace an authoritative state source with derived or inferred state when the distinction is material.

**I-STATE-02 — State provenance for consequential continuity**  
When a continuity claim depends on durable state, the relevant state MUST be traceable to its accepted source or transition record.

**I-STATE-03 — State/behavior distinction**  
A system MUST NOT assume that behavioral identity and state identity are equivalent unless the governing contract explicitly defines them that way.

## 13. Boundary 5 — Evidence / Verification Plane

### 13.1 Responsibility

Evidence is a cross-cutting architectural plane used to determine what governed the system, what it did, and whether its behavior remained inside the declared envelope.

Evidence may be collected before, during, and after execution.

### 13.2 Invariants

**I-EVD-01 — No fabricated execution claim**  
The system MUST NOT claim execution, inspection, verification, approval, or success that did not occur.

**I-EVD-02 — Governing-version traceability**  
Consequential evidence MUST permit identification of the governing intent and authority versions relevant to the action.

**I-EVD-03 — Material failure preservation**  
A material failed attempt, deviation, or uncertainty that affects interpretation MUST NOT be silently rewritten as clean success.

**I-EVD-04 — Claim-type separation**  
Observed result, inference, hypothesis, architectural claim, and human judgment MUST be distinguishable when the distinction is material.

**I-EVD-05 — No private-chain-of-thought dependency**  
Conformance MUST NOT require disclosure of hidden chain-of-thought. Observable inputs, outputs, actions, approvals, tool records, tests, provenance, versioning, and externally inspectable rationale are valid evidence classes.

**I-EVD-06 — Acceptance traceability**  
A consequential acceptance decision MUST be attributable to the actor or policy holding Acceptance Authority.

## 14. Evidence profile, not evidence ladder

Evidence strength is multidimensional rather than a universal sequence.

An evidence claim SHOULD identify relevant dimensions such as:

| Dimension | Example values |
|---|---|
| Repeatability | single observation / repeated / replicated |
| Evaluator independence | same actor / independent / multiple independent |
| Operator independence | same operator / independent operator |
| Blinding | open / partially blinded / blinded |
| Preregistration | none / partial / frozen protocol |
| Runtime diversity | same runtime / different session / different model / different provider |
| Sample breadth | narrow / moderate / broad |
| Provenance quality | informal / recorded / hash-bound |
| Adversariality | cooperative / neutral / intentionally adversarial |
| Ecological validity | synthetic / controlled realistic / operational |

No single dimension automatically dominates every other dimension. Claims should be bounded by the actual evidence profile.

## 15. Evaluation Authority versus Acceptance Authority

INSA distinguishes two roles.

### Evaluation Authority

Permission to execute, score, or interpret tests against declared criteria.

### Acceptance Authority

Permission to accept the system or outcome on behalf of the principal for the relevant consequence.

**I-ACC-01 — Evaluation is not automatically acceptance**  
An evaluator MUST NOT infer consequential Acceptance Authority merely from permission to score or evaluate.

The same actor MAY hold both roles when explicitly authorized.

## 16. Intelligent Execution Environment

The Intelligent Execution Environment is the implementation freedom zone inside the governed contracts.

It may include:

- models;
- agents;
- generated or conventional code;
- deterministic services;
- tool adapters;
- planners;
- retrieval;
- databases;
- workflows;
- memory;
- message buses;
- event subscriptions;
- human-in-the-loop controls;
- multiple cooperating AI systems.

The implementation stack MAY change without changing application identity unless the governing contract makes a particular mechanism part of an invariant.

The execution principle is:

> **Intelligence is an execution resource, not a grant of purpose or authority.**

## 17. Deterministic versus intelligent placement

INSA is hybrid. A component SHOULD remain deterministic when ambiguity creates disproportionate risk relative to the value of intelligent adaptation.

Placement decisions SHOULD consider at least:

| Factor | Favors deterministic control when... |
|---|---|
| Consequence of error | high or catastrophic |
| Reversibility | low |
| Required latency | hard real-time or tightly bounded |
| Acceptable variance | near zero |
| Security sensitivity | high |
| Regulatory exactness | exact prescribed behavior required |
| Transactionality | atomic commit / rollback required |
| Auditability | exact replay or proof required |
| False-positive / false-negative cost | strongly asymmetric or unacceptable |

Examples commonly favoring deterministic controls include cryptography, hard transaction boundaries, access enforcement, safety interlocks, schema constraints, exact resource ceilings, and irreversible destructive commits.

This matrix is guidance for placement. Individual deployments MAY promote selected placement rules into mandatory policy.

## 18. INSA application contract package

A mature INSA application should be representable by a portable governed package containing the following logical artifacts.

### 18.1 Purpose Record

Why the system exists and who owns that purpose.

### 18.2 Intent Contract

Objectives, constraints, anti-goals, acceptance criteria, and governing version.

### 18.3 Authority Manifest

Scope, limits, delegation, freshness, approvals, expiration, and revocation.

### 18.4 Value Declaration and Conformance Record

Declared governing values plus conformance status and supporting evidence.

### 18.5 Behavioral Identity Contract

Identity dimensions, permitted variance, and where applicable the `B/M/P/V/O/A/G` evolution contract.

### 18.6 State / Continuity Contract

State authority, provenance, migration, recovery, and identity participation where the application is stateful.

### 18.7 Evidence Contract

Required provenance, tests, evaluator independence, audit records, uncertainty disclosure, and acceptance traceability.

### 18.8 Implementation Adapters

Current models, code, prompts, tools, services, workflows, and integrations.

Implementation adapters are replaceable unless explicitly elevated into a governing invariant.

### 18.9 Change Record

Versioned changes to intent, authority, values, identity, state, evidence requirements, or implementation, including the basis for acceptance.

## 19. Governed execution lifecycle

```text
1. DEFINE
   establish purpose, intent, constraints, identity, state,
   and evidence requirements

2. AUTHORIZE
   establish permitted scope, delegation, approvals, and freshness

3. GOVERN
   establish values and conflict / escalation behavior

4. EXECUTE
   intelligence selects or generates implementation mechanisms

5. OBSERVE
   collect evidence across governing state and executed actions

6. EVALUATE
   Evaluation Authority compares behavior with declared criteria

7. ACCEPT / REJECT
   Acceptance Authority accepts, rejects, or requests correction

8. PRESERVE
   retain governing versions, state, and sufficient evidence

9. EVOLVE
   bind B/M/P/V/O/A/G before targeted behavioral modification

10. RECONSTRUCT
    realize the governed application through a new implementation
    when reconstruction is useful or required
```

## 20. Failure taxonomy

### F1 — Intent drift

Execution no longer serves the governing intent.

### F2 — Authority drift

The system acts outside, beyond, or after expiration/revocation of authority.

### F3 — Value drift

Discretionary behavior is inconsistent with the declared value set under the tested conditions.

### F4 — Behavioral identity drift

Required non-target behavior leaves its preservation envelope.

### F5 — State continuity failure

Durable state, provenance, or required state identity is lost, substituted, or corrupted.

### F6 — Evidence failure

The system may or may not have behaved correctly, but the claim cannot be adequately established.

### F7 — Implementation failure

The selected implementation mechanism fails while the governing architecture remains intact.

### F8 — Awareness / freshness failure

The system acts on materially stale intent, authority, state, dependency, or risk information.

### F9 — Delegation failure

Authority, constraints, or obligations are broadened or dropped during actor-to-actor handoff.

Diagnostic rule:

> **Do not repair an architectural failure by merely swapping models, and do not redesign the architecture when only an implementation adapter failed.**

## 21. Current evidence posture

| Area | Current posture |
|---|---|
| Intent-layer development / DbI | Demonstrated as feasible for bounded language- and reasoning-centric applications |
| Behavioral reconstruction | Strong bounded evidence under controlled conditions |
| Cross-implementation portability | Promising but bounded |
| Behavioral Identity measurement | Operational enough for controlled experiments |
| Safe targeted evolution | Not demonstrated reliably; active architectural problem |
| Value Architecture vocabulary | Formalized in experimental standard v0.2 |
| Value conformance | Early; stronger conflict/adversarial tests required |
| Authority architecture | Conceptually explicit; revocation/freshness portability under-tested |
| Stateful continuity | Demonstrated in bounded prior work, not yet integrated into broad INSA validation |
| Evidence architecture | Relatively mature within the experimental program |
| Universal INSA applicability | Not established and not claimed |

The architecture MUST narrow when evidence fails rather than expanding explanations after the result.

## 22. Boundary-driven research program

### INSA-ID-E1 — Targeted evolution with preservation

**Question:** Can one declared behavioral dimension change while a frozen non-target identity set remains stable?

**Required pre-freeze structure:** `B/M/P/V/O/A/G`.

**Falsification value:** High. This directly addresses the strongest currently exposed architectural weakness.

### INSA-AUTH-E1 — Revocation and authority freshness

**Question:** Does an agent reliably stop, revalidate, or reroute consequential action when authority is narrowed or revoked after planning begins?

**Required variation:** event-driven versus revalidation versus transaction-scoped authority mechanisms.

### INSA-VAL-E1 — Values under cost and conflict

**Question:** Does a declared value continue to govern when compliance creates measurable cost, delay, or conflict with another objective or value?

### INSA-ID-E2 — Cross-runtime identity portability

**Question:** Can the same frozen Behavioral Identity Contract be realized by materially different model/tool stacks without identity-breaking behavior?

### INSA-EVD-E1 — Minimum sufficient evidence

**Question:** What evidence dimensions are actually necessary for reliable independent conformance adjudication?

### INSA-INT-E1 — Intent compilation

**Question:** When does structured compilation of natural-language intent increase reliability, and when does it unnecessarily constrain useful intelligent behavior?

### INSA-STATE-E1 — Stateful reconstruction continuity

**Question:** Can a stateful application change implementation while preserving authoritative state semantics, provenance, and behavioral identity?

## 23. Experiment requirements

Every future INSA experiment MUST state before execution:

1. architectural boundary or cross-cutting contract under test;
2. invariant or hypothesis being tested;
3. frozen governing version;
4. observable failure condition;
5. result that would narrow or falsify the claim;
6. implementation mechanisms allowed to vary;
7. evidence dimensions required for adjudication;
8. stopping rules;
9. claim permitted by a pass;
10. claim still prohibited despite a pass.

Experiments MUST NOT broaden their claim after observing a favorable result without a new explicitly identified analysis or experiment.

## 24. Architecture freeze gate

This v0.2 candidate is not frozen.

Before freeze, reviewers should determine:

- whether each `I-*` statement is genuinely mandatory and testable;
- whether the five-boundary model still omits a necessary intelligence-native boundary;
- whether State / Continuity is correctly modeled as cross-cutting rather than top-level;
- whether Evidence is now correctly cross-cutting;
- whether Authority freshness is enforceable without over-specifying mechanism;
- whether `B/M/P/V/O/A/G` is sufficient to preregister safe-evolution experiments;
- whether any conventional software concern has been unnecessarily renamed as INSA architecture;
- whether a conforming implementation could still exploit ambiguity to claim success after drift.

Only after this gate passes should `INSA-ID-E1` be preregistered against the frozen architecture.

## 25. What INSA v0.2-candidate does not claim

It does not claim that:

- code is obsolete;
- all software should be agentic;
- natural language is sufficient for every requirement;
- AI should receive broad autonomous authority;
- prompts are architecture;
- reconstruction implies safe evolution;
- declared values imply behavioral conformance;
- security can be reduced to prompting;
- deterministic systems are legacy infrastructure;
- every system needs every optional cross-cutting contract;
- the five-boundary model is final;
- the architecture has been validated merely because it has been documented.

## 26. Architectural decision test

For any proposed intelligence-native capability, ask:

1. **Intent:** What outcome is the intelligence serving, and which version governs?
2. **Authority:** What may it do, who granted that authority, and how fresh is that grant?
3. **Values:** How should it choose among multiple permitted actions, and what evidence supports claimed value conformance?
4. **Identity:** What must remain stable while implementation or target behavior changes?
5. **State:** What durable state must remain trustworthy, if any?
6. **Evidence:** What evidence will establish that the governing contracts were respected?
7. **Acceptance:** Who may evaluate, and who may actually accept the consequential outcome?

If a material question has no answer, the system is not yet fully governed at the intelligence-native boundary.

## 27. Project position

```text
Stage 1 — Discovery
Can useful behavior be developed at the intent layer?

Stage 2 — Experimental validation
Can behavioral identity be reconstructed, measured, compared, and challenged?

Stage 3 — Architecture
What stable boundaries are required when implementation becomes intelligent and fluid?

Stage 3A — Adversarial architecture correction  ← CURRENT
Can the architecture survive critique before we spend evidence on it?

Stage 4 — Boundary validation
Which proposed invariants survive controlled adversarial experiments?

Stage 5 — External architecture validation
Can independent implementers reproduce, challenge, narrow, or falsify the model?
```

The immediate objective is to pass the architecture freeze gate, then preregister **INSA-ID-E1** as the first experiment explicitly designed from the INSA architecture rather than retrofitted into it.

# Intelligence-Native Software Architecture / Development by Intent — Current Status

**As of:** 2026-09-09  
**Project stage:** INSA Stage 4 — boundary validation  
**Decision authority:** Frank Ventura as principal investigator  
**Operating rule:** humans own purpose, intent, authority delegation, judgment, and acceptance; intelligence may assume implementation burden only inside an explicit governed envelope

## Current assessment

The project has completed the transition from Development by Intent (DbI) as the primary conceptual frame to **Intelligence-Native Software Architecture (INSA)** as the broader experimental architecture.

DbI remains the experimental lineage and a primary research vehicle. INSA now defines the architectural boundaries that future experiments are intended to validate, narrow, or falsify.

## Frozen architecture baseline

The current architecture is:

- [`INSA-ARCHITECTURE-v0.3-FROZEN.md`](INSA-ARCHITECTURE-v0.3-FROZEN.md) — freeze manifest;
- [`INSA-ARCHITECTURE-v0.3-candidate.md`](INSA-ARCHITECTURE-v0.3-candidate.md) — exact normative source;
- source commit: `d2c2ad93d95d048e6e2e0c3d42d993a1ecd40f1b`;
- source Git blob SHA: `848e0fe014f5b4a61ba2cb92e772ee3499dca9c1`;
- final freeze review: [`INSA-ARCHITECTURE-v0.3-FINAL-FREEZE-REVIEW.md`](INSA-ARCHITECTURE-v0.3-FINAL-FREEZE-REVIEW.md);
- freeze-review disposition: **PASS_FOR_ARCHITECTURE_FREEZE**.

The v0.3 baseline MUST NOT be edited in place for experiments claiming to test that architecture. Any architectural change requires a new version.

## How the architecture reached freeze

The progression was deliberately adversarial:

```text
research outline
      ↓
INSA v0.1 explicit architecture
      ↓
v0.1 adversarial review — REVISION_REQUIRED
      ↓
INSA v0.2 candidate
      ↓
v0.2 freeze review — REVISION_REQUIRED
      ↓
INSA v0.3 candidate
      ↓
final freeze review — PASS
      ↓
INSA v0.3 FROZEN
```

The review process corrected several important defects before experimental use:

- architectural invariants are now separated from guidance;
- Evidence is modeled as a cross-cutting verification plane;
- Authority includes provenance, grant authenticity, revocation, and freshness;
- Value Declaration is separated from Value Conformance status and evidence;
- Behavioral evolution is bound to a frozen baseline;
- permitted variance is dimension-specific rather than a competing behavioral set;
- State / Continuity is an explicit cross-cutting contract;
- multi-agent delegation cannot manufacture authority;
- Evaluation Authority is distinct from Acceptance Authority;
- boundary applicability must be declared before adjudication.

## The five INSA boundaries

1. **Intent** — what outcome the principal wants, what constraints apply, and what constitutes acceptance.
2. **Authority** — what the intelligent system may do, independent of what it can technically do.
3. **Values** — how discretion is governed when instructions do not uniquely determine an action.
4. **Behavioral Identity** — what must remain stable when implementation varies, is reconstructed, or evolves.
5. **Evidence** — how humans or independent evaluators can establish whether the other boundaries were respected.

The Intelligent Execution Environment — models, agents, tools, code, services, workflows, memory, and coordination — is the implementation freedom zone inside those governed contracts.

State / Continuity remains cross-cutting rather than a sixth top-level boundary in v0.3.

## Evidence established before INSA freeze

### Intent-layer development / DbI

Bounded experiments show that useful language- and reasoning-centric applications can be developed primarily at the intent and behavioral-evaluation layers while capable AI supplies substantial implementation detail.

### Behavioral reconstruction

The Amazing Birthday research program provides strong bounded evidence that recognizable behavioral identity can survive independent reconstruction under controlled conditions.

### BIB-002

The suspected R4/B deviation did not reproduce under preregistered confirmation.

Final disposition: **PATTERN_NOT_REPRODUCED**.

### Behavioral evolution

The subsequent evolution experiment tested whether a targeted intent change could modify desired behavior while preserving non-target identity.

Final disposition: **MODIFICATION_AND_PRESERVATION_FAILURE**.

Architectural implication:

> **Reconstruction stability does not imply evolution stability.**

This result directly motivated INSA's explicit safe-evolution contract.

### Value Architecture

Value Architecture v0.2 provides an experimental vocabulary for capability, intent, values, authority, policy, evidence, implementation, conflict handling, and behavioral conformance.

Value conformance remains under-tested and is a major future INSA boundary target.

## Active milestone — INSA-ID-E1

The first experiment explicitly designed from the frozen INSA architecture is:

**INSA-ID-E1 — Targeted Evolution With Preservation**

The experiment must bind before execution:

```text
B = frozen baseline
D = scored behavioral dimensions
M = mutation dimensions
P = preservation dimensions
O = out-of-scope dimensions
V(d) = dimension-specific permitted variance
A = acceptance tests bound to M
G = preservation gates bound to P
```

The question is:

> **Can a targeted intent change modify a declared target behavior while preserving a predeclared non-target behavioral identity envelope?**

This proposition is currently **unproven** and must remain vulnerable to failure.

## Execution boundary

The architecture freeze does **not** authorize INSA-ID-E1 execution.

The next work is:

1. construct the INSA-ID-E1 preregistration and exact experimental protocol;
2. bind the frozen INSA v0.3 architecture source;
3. freeze `B/D/M/P/O/V(d)/A/G`;
4. define evaluator roles, blinding, evidence requirements, stop rules, and allowed claims;
5. conduct an adversarial protocol review;
6. freeze the protocol only if that review passes;
7. obtain separate execution authorization before model dispatch.

## Current claim boundary

The project may state that:

- INSA v0.3 is an explicit, internally reviewed and frozen experimental architecture baseline;
- the five-boundary model is ready for controlled validation;
- DbI provides bounded evidence that the development boundary can move upward for some application classes;
- behavioral reconstruction and safe behavioral evolution are distinct engineering properties;
- authority, values, behavioral identity, and evidence become first-class concerns as implementation autonomy increases.

The project may not yet state that:

- INSA is an empirically validated architecture;
- the five-boundary model is complete;
- safe targeted evolution has been solved;
- Value Architecture has demonstrated portable behavioral durability;
- all software benefits from intelligence-native techniques;
- deterministic architecture is obsolete.

## Project progression

```text
Stage 1 — Discovery
Can useful software behavior be developed at the intent layer?

Stage 2 — Experimental validation
Can behavioral identity be reconstructed, measured, compared, and challenged?

Stage 3 — Architecture
What stable boundaries are required when implementation becomes increasingly intelligent and fluid?

Stage 3A — Adversarial architecture correction
Can the architecture survive critique before we spend evidence on it?

Stage 4 — Boundary validation  ← CURRENT
Which proposed INSA invariants survive controlled adversarial experiments?

Stage 5 — External architecture validation
Can independent developers and researchers implement, challenge, reproduce, narrow, or falsify the architecture?
```

The architecture is frozen. The next unit of progress must come from evidence.

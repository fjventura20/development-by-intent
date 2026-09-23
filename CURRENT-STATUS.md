# Intelligence-Native Software Architecture / Development by Intent — Current Status

**As of:** 2026-09-10  
**Project stage:** INSA Stage 4 — boundary validation  
**Completed Stage 4 INSA experiments:** **0**  
**Decision authority:** Frank Ventura as principal investigator  
**Execution dispatch authority:** explicit PI / human GO is required before resource-consuming model execution  
**Operating rule:** humans own purpose, intent, authority delegation, judgment, and acceptance; intelligence may assume implementation burden only inside an explicit governed envelope

## Current assessment

The project has completed the transition from Development by Intent (DbI) as the primary conceptual frame to **Intelligence-Native Software Architecture (INSA)** as the broader experimental architecture.

DbI remains the experimental lineage and a primary research vehicle. INSA now defines the architectural boundaries that future experiments are intended to validate, narrow, or falsify.

The architecture phase is complete enough to test. It is **not** empirically validated. Stage 4 currently has zero completed experiments explicitly designed to test the frozen INSA architecture.

## Frozen architecture baseline

The current architecture is:

- [`INSA-ARCHITECTURE-v0.3-FROZEN.md`](INSA-ARCHITECTURE-v0.3-FROZEN.md) — freeze manifest;
- [`INSA-ARCHITECTURE-v0.3-candidate.md`](INSA-ARCHITECTURE-v0.3-candidate.md) — exact normative source;
- source commit: `d2c2ad93d95d048e6e2e0c3d42d993a1ecd40f1b`;
- source Git blob SHA: `848e0fe014f5b4a61ba2cb92e772ee3499dca9c1`;
- final freeze review: [`INSA-ARCHITECTURE-v0.3-FINAL-FREEZE-REVIEW.md`](INSA-ARCHITECTURE-v0.3-FINAL-FREEZE-REVIEW.md);
- freeze-review disposition: **PASS_FOR_ARCHITECTURE_FREEZE**.

The v0.3 baseline MUST NOT be edited in place for experiments claiming to test that architecture. Any architectural change requires a new version.

For canonical-versus-historical file status, see [`ARCHIVE-INDEX.md`](ARCHIVE-INDEX.md).

## Review provenance and independence

The v0.1 adversarial review, v0.2 freeze-gate review, and v0.3 final freeze review were **internal AI-assisted methodological reviews within the PI-led research process**. They are not external validation or independent certification.

The original public artifacts did not record enough reviewer/model/context metadata to support a stronger independence claim. The known and unknown fields are now stated explicitly in [`REVIEWER-DISCLOSURES.md`](REVIEWER-DISCLOSURES.md).

Accordingly, `PASS_FOR_ARCHITECTURE_FREEZE` means only that the candidate was judged sufficiently explicit and internally consistent to freeze as the object of controlled experiments. It does not mean INSA was validated.

## How the architecture reached freeze

The progression was deliberately adversarial:

```text
research outline
      ↓
INSA v0.1 explicit architecture
      ↓
internal v0.1 adversarial review — REVISION_REQUIRED
      ↓
INSA v0.2 candidate
      ↓
internal v0.2 freeze review — REVISION_REQUIRED
      ↓
INSA v0.3 candidate
      ↓
internal final freeze review — PASS
      ↓
INSA v0.3 FROZEN FOR EXPERIMENTATION
```

The internal review process corrected several important defects before experimental use:

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

The Amazing Birthday research program provides bounded evidence that recognizable behavioral identity can survive reconstruction under controlled conditions. Public indexes distinguish operator scoring from later independent re-scoring where that exists; independence must not be conflated with blinding.

### BIB-002

The suspected R4/B deviation did not reproduce under preregistered confirmation.

Final disposition: **PATTERN_NOT_REPRODUCED**.

### Behavioral evolution — negative result

The subsequent evolution experiment tested whether a targeted intent change could modify desired behavior while preserving non-target identity.

Final disposition: **MODIFICATION_AND_PRESERVATION_FAILURE**.

Architectural implication:

> **Reconstruction stability does not imply evolution stability.**

This result directly motivated INSA's explicit safe-evolution contract. See [`EVOLUTION-FAILURE.md`](EVOLUTION-FAILURE.md) for the promoted public evidence note and its claim boundary.

### Value Architecture

Value Architecture v0.2 provides an experimental vocabulary for capability, intent, values, authority, policy, evidence, implementation, conflict handling, and behavioral conformance.

Value conformance remains under-tested and is a major future INSA boundary target.

## Active milestone — INSA-ID-E1

The first experiment explicitly designed from the frozen INSA architecture is:

**INSA-ID-E1 — Targeted Evolution With Preservation**

Current protocol state: **v0.2 DRAFT — NO EXECUTION AUTHORIZED**.

The current draft binds the experiment around:

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

## Execution boundary — PI / human GO

The architecture freeze does **not** authorize INSA-ID-E1 execution, and the current protocol draft explicitly authorizes zero candidate-generation or evaluator calls.

The separate execution gate is a **human-control boundary**, not an independent oversight body. Its purpose is to prevent agents that possess technical capability from converting that capability into permission to spend resources or dispatch experimental model calls.

Before candidate generation, the protocol must complete the required freeze and integrity gates and then receive explicit **PI execution authorization / human GO**.

This distinction is intentional:

```text
technical capability to execute
            ≠
authority to execute
```

## External validation surface

External participation should be cheaper than the full Developer Challenge.

The repository now provides [`QUICK-VALIDATION.md`](QUICK-VALIDATION.md), a five-minute exploratory contribution path. It asks outsiders to run one fresh-environment observation and report the first output, including failures. This does not replace formal preregistered experiments.

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
- deterministic architecture is obsolete;
- the internal architecture-review chain constitutes external or independent validation.

## Project progression

```text
Stage 1 — Discovery
Can useful software behavior be developed at the intent layer?

Stage 2 — Experimental validation
Can behavioral identity be reconstructed, measured, compared, and challenged?

Stage 3 — Architecture
What stable boundaries are required when implementation becomes increasingly intelligent and fluid?

Stage 3A — Adversarial architecture correction
Can the architecture survive internal critique before we spend evidence on it?

Stage 4 — Boundary validation  ← CURRENT
Completed INSA experiments: 0
Which proposed INSA invariants survive controlled adversarial experiments?

Stage 5 — External architecture validation
Can independent developers and researchers implement, challenge, reproduce, narrow, or falsify the architecture?
```

The architecture is frozen. The next unit of architectural progress must come from evidence, not additional conceptual expansion.
# Intelligence-Native Software Architecture / Development by Intent — Current Status

**As of:** 2026-09-09  
**Project stage:** INSA Stage 3 — explicit architecture and boundary validation  
**Decision authority:** Frank Ventura as principal investigator  
**Operating rule:** humans own purpose, intent, authority delegation, judgment, and acceptance; intelligence may assume implementation burden only inside an explicit governed envelope

## Current assessment

The project has moved beyond the question of whether Development by Intent (DbI) is an interesting development technique.

DbI remains the experimental lineage and a primary research vehicle, but the larger research target is now **Intelligence-Native Software Architecture (INSA)**: how software should be designed when machine intelligence becomes a fundamental execution resource rather than merely a coding aid.

The project has completed enough discovery to define an explicit experimental architecture. The current baseline is:

- [`INSA-ARCHITECTURE-v0.1.md`](INSA-ARCHITECTURE-v0.1.md)
- [`RESEARCH-DIRECTION.md`](RESEARCH-DIRECTION.md)
- [`VALUE-ARCHITECTURE-STANDARD-v0.2.md`](VALUE-ARCHITECTURE-STANDARD-v0.2.md)

The immediate objective is now to determine, through controlled experiments, which INSA boundaries and invariants survive contact with reality.

## The five INSA boundaries

INSA v0.1 defines five architectural boundaries:

1. **Intent** — what outcome the principal wants, what constraints apply, and what constitutes acceptance.
2. **Authority** — what the intelligent system may do, independent of what it can technically do.
3. **Values** — how discretion is governed when instructions do not uniquely determine an action.
4. **Behavioral Identity** — what must remain stable when implementation varies, is reconstructed, or evolves.
5. **Evidence** — how humans or independent evaluators can determine whether the preceding boundaries were respected.

The Intelligent Execution Environment — models, agents, tools, code, services, memory, workflows, and coordination — is treated as the implementation freedom zone inside those boundaries.

## Evidence established so far

### Intent-layer development / DbI

The project has bounded evidence that useful language- and reasoning-centric applications can be developed primarily at the intent and behavioral-evaluation layers while capable AI supplies substantial implementation detail.

This establishes feasibility for the studied application classes. It does not establish universal applicability.

### Behavioral reconstruction

The Amazing Birthday research program provides strong bounded evidence that recognizable behavioral identity can survive independent reconstruction under controlled conditions.

The BIB-001 rerun established a calibrated reconstruction baseline with both evaluators passing the frozen gates.

### BIB-002 deviation confirmation

The suspected R4/B deviation did **not** reproduce under the preregistered confirmation experiment.

Final disposition: **PATTERN_NOT_REPRODUCED**.

This was a useful negative result. The project should not build architecture around the earlier apparent anomaly.

### Behavioral evolution

The subsequent DbI Evolution experiment asked a harder architectural question: whether a targeted intent change can modify the desired behavior while preserving non-target behavioral identity.

Final disposition: **MODIFICATION_AND_PRESERVATION_FAILURE**.

The central architectural implication is:

> **Reconstruction stability does not imply evolution stability.**

INSA therefore treats safe targeted evolution as an independent architectural problem requiring an explicit mutation set, preservation set, permitted variance, acceptance tests, and preservation gates.

### Value Architecture

Value Architecture has advanced from an informal principle into an experimental standard:

- capability is distinguished from authority;
- values are distinguished from rules, policies, prompts, and implementation mechanisms;
- twelve core values are defined behaviorally;
- authority, conflict resolution, evidence, and conformance testing are explicit;
- increasing capability is not permitted to silently imply increasing authority.

The vocabulary is relatively mature. Behavioral conformance evidence remains early and is a major next research area.

### Evidence architecture

The experimental program now has substantial discipline around:

- frozen protocols;
- provenance;
- hashes;
- blind mappings;
- independent evaluators;
- preserved failures and deviations;
- bounded claims;
- PI adjudication;
- explicit stop conditions.

This is currently one of the more mature portions of the emerging architecture.

## Architectural distinction now enforced

INSA v0.1 explicitly separates:

- **architectural invariants** — conditions that must remain true and must have an enforcement, detection, or evaluation path;
- **controls** — mechanisms used to enforce or observe invariants;
- **guidance** — recommended practice that is not an architectural boundary;
- **hypotheses** — propositions still awaiting evidence;
- **evidence claims** — bounded statements about what has actually been observed.

This distinction is important. Prompt discipline, process advice, or desirable behavior should not be promoted to architecture merely by naming them as such.

## Active milestone — validate the architecture

The next milestone is **not another broad demonstration of DbI**.

The active program is to test INSA boundary by boundary.

Priority experiments defined by v0.1 are:

1. **INSA-ID-E1 — Targeted evolution with preservation**  
   Test whether one declared behavioral dimension can change while an explicit non-target identity set remains stable.

2. **INSA-AUTH-E1 — Revocation and least authority**  
   Test whether an agent reliably stops or reroutes consequential action when authority is narrowed or revoked after planning begins.

3. **INSA-VAL-E1 — Values under cost and conflict**  
   Test whether declared values continue to govern when compliance creates measurable cost, delay, or conflict.

4. **INSA-ID-E2 — Cross-runtime identity portability**  
   Test the same Behavioral Identity Contract across materially different model/tool stacks.

5. **INSA-EVD-E1 — Minimum sufficient evidence**  
   Determine the smallest evidence package that still supports reliable blinded conformance evaluation.

6. **INSA-INT-E1 — Intent compilation**  
   Determine when converting natural-language intent into structured constraints improves reliability versus overconstraining useful intelligence.

## Immediate research gate

Before launching the next expensive experiment, INSA v0.1 should receive an adversarial architecture review against the accumulated experimental record.

The review should ask:

- Are all five boundaries genuinely architectural, or are any merely process guidance?
- Does every declared invariant have a plausible enforcement, detection, or evaluation path?
- Are any controls being mistaken for invariants?
- Does the architecture explain the observed reconstruction/evolution split?
- Are the proposed experiments capable of falsifying or narrowing the architecture?
- What important boundary is missing?

If the architecture survives that review with only bounded revisions, the next recommended experimental target is **INSA-ID-E1**, because safe evolution is the clearest experimentally exposed weakness in the current model.

## Current claim boundary

The project may reasonably claim that:

- Intelligence-Native Software Architecture is now an explicit experimental architecture, not merely a loose research direction;
- DbI provides bounded evidence that the human-machine development boundary can move upward for some application classes;
- behavioral reconstruction and behavioral evolution are distinct engineering properties;
- Value Architecture and authority become more important as implementation autonomy increases;
- evidence and evaluation must be architectural concerns when implementation can vary dynamically.

The project may **not** yet claim that:

- INSA is an established discipline;
- the five-boundary model is complete;
- safe behavioral evolution has been solved;
- Value Architecture is portable or durable across implementations without further testing;
- all software benefits from intelligence-native techniques;
- deterministic architecture is obsolete;
- intelligence should receive broad autonomous authority.

## Project progression

```text
Stage 1 — Discovery
Can useful software behavior be developed at the intent layer?

Stage 2 — Experimental validation
Can behavioral identity be reconstructed, measured, compared, and challenged?

Stage 3 — Architecture  ← CURRENT
What stable boundaries are required when implementation becomes increasingly intelligent and fluid?

Stage 4 — Boundary validation
Which proposed INSA invariants survive controlled adversarial experiments?

Stage 5 — External architecture validation
Can independent developers and researchers implement, challenge, reproduce, or falsify the architecture?
```

The project is now at the transition from **Stage 3 into Stage 4**.

## Repository posture

The repository name remains `development-by-intent` deliberately. DbI is the experimental lineage from which INSA emerged, and preserving links, evidence, hashes, discussions, and historical continuity remains more important than renaming the repository prematurely.

The front page should remain accessible to developers, while the architecture and experimental record provide the deeper technical path.

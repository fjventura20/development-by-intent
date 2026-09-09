# INSA-ID-E1 — Targeted Evolution With Preservation

## Protocol v0.1 — DRAFT

**Status:** DRAFT — DESIGN ONLY — NO EXECUTION AUTHORIZED  
**Date:** 2026-09-09  
**Architecture baseline:** INSA v0.3 FROZEN  
**Architecture source commit:** `d2c2ad93d95d048e6e2e0c3d42d993a1ecd40f1b`  
**Architecture source Git blob SHA:** `848e0fe014f5b4a61ba2cb92e772ee3499dca9c1`  
**Architecture freeze manifest:** [`../../INSA-ARCHITECTURE-v0.3-FROZEN.md`](../../../INSA-ARCHITECTURE-v0.3-FROZEN.md)  
**Prior related experiment:** DbI Evolution Protocol v0.5 at commit `da118366c7523b16bff460941d980af5c1bf3097`  
**Authorization:** This draft authorizes no model dispatch, candidate generation, evaluator invocation, unblinding, or scoring.

---

## 0. Why this experiment exists

The prior DbI Evolution experiment asked whether a developer could change Amazing Birthday by changing expressed intent while preserving established non-target behavioral identity.

That experiment produced a substantive modification-and-preservation failure. The important architectural lesson was:

> **Reconstruction stability does not imply evolution stability.**

INSA v0.3 now makes safe evolution explicit. A targeted change must be bound before execution to a frozen baseline, declared mutation dimensions, declared preservation dimensions, dimension-specific permitted variance, acceptance tests, and preservation gates.

INSA-ID-E1 is therefore **not an independent replication of the prior Evolution experiment**. It is a transparent post-failure intervention experiment testing a new architectural mechanism: an execution-facing INSA evolution contract that makes the target change and non-target preservation requirements explicit to the intelligent execution environment before generation.

Reusing the same Amazing Birthday target modification is deliberate. It preserves comparability and asks whether the architectural intervention changes the outcome on a previously difficult evolution problem.

A favorable result MUST NOT be described as an unbiased replication of the original hypothesis.

---

## 1. Research question

> **When a targeted intent change is expressed through a frozen INSA v0.3 evolution contract, can the intelligent execution environment implement the declared target behavior while preserving a predeclared non-target Behavioral Identity envelope?**

The experiment tests the conjunction:

```text
Target Modification Success
AND
Non-target Identity Preservation
```

Neither component alone is sufficient for `EVOLUTION_PASS`.

---

## 2. Architectural proposition under test

Primary INSA boundary: **Behavioral Identity**.

Cross-cutting contracts under test:

- Intent version binding;
- Evidence / Verification;
- Applicability declaration;
- frozen safe-evolution contract.

Primary architectural proposition:

> **INSA-ID-P1:** A governed evolution can change behavior in a declared mutation set while keeping declared preservation dimensions inside a frozen tolerance envelope.

This proposition is currently **UNPROVEN**.

### 2.1 What would narrow or falsify the proposition

Any otherwise valid result in which:

- the target modification succeeds but one or more required preservation dimensions fail; or
- preservation succeeds but the target modification does not; or
- both fail;

is substantive negative evidence for this implementation of the proposition.

The experiment MUST NOT convert such failures into `INCONCLUSIVE` merely because the result is undesirable.

---

## 3. Applicability declaration

Frozen before execution:

```text
Intent        ACTIVE
Authority     N-A for candidate content generation itself
Values        ACTIVE only insofar as existing Amazing Birthday behavioral values
              are represented by preservation dimensions; this experiment does
              not claim general Value Architecture conformance
Identity      ACTIVE — PRIMARY
State         N-A — Amazing Birthday candidate generation is stateless
Evidence      ACTIVE
```

### 3.1 Authority note

Generation and evaluation tools still require operator authorization operationally. However, the **candidate behavior under study** does not exercise consequential external authority. INSA-AUTH-E1 will test the Authority Boundary separately.

### 3.2 No post-hoc applicability changes

Applicability states above are frozen with the final protocol. They MUST NOT be changed after candidate outputs are observed.

---

## 4. Relationship to prior evidence

### 4.1 Frozen Amazing Birthday source

Use the same frozen Amazing Birthday reconstruction source lineage as the prior DbI Evolution experiment:

- frozen source commit: `c369215024c9f8a849daf11bd4b872d7ee566a7a`;
- base reconstruction artifacts: `03-behavioral-baseline.md` + `RECONSTRUCTION-PROMPT.md`;
- base reconstruction bytes MUST remain unchanged from the verified BIB / prior Evolution source.

Exact source-file hashes MUST be reverified and recorded in the final frozen protocol inventory before execution.

### 4.2 BIB calibration

The BIB non-deviated envelope remains historical calibration for control validity and Behavioral Identity interpretation.

If the prior frozen `baseline-envelope-membership.json` is reused, its exact content and SHA-256 MUST be reverified and frozen into the new protocol inventory before execution.

### 4.3 Prior Evolution result

The prior experiment is historical context, not part of the primary statistical comparison.

A secondary descriptive section MAY compare INSA-ID-E1 metrics with the prior Evolution result, but MUST label that comparison **non-causal / post-failure historical comparison** because protocol and time differ.

---

## 5. Experimental design

### 5.1 Arms

Two-arm matched-reconstruction design:

- **Arm C — Governed Control:** original Amazing Birthday intent plus a structurally explicit INSA stability contract with no target mutation.
- **Arm G — Governed Evolution:** original Amazing Birthday intent plus an INSA evolution contract containing the frozen target mutation and all preservation dimensions.

Both arms receive the same base reconstruction artifacts and the same INSA contract wrapper structure.

The treatment difference is the declared mutation content.

### 5.2 Why there is no legacy-modification arm

The prior DbI Evolution experiment already supplies historical evidence about the earlier intent-modification mechanism.

Adding a third legacy arm would increase generation/evaluation cost and would still not make the cross-experiment comparison fully causal because the historical experiment already occurred.

The primary v0.1 design therefore tests whether the **INSA-governed mechanism itself** can achieve modification plus preservation under a contemporaneous matched control.

### 5.3 Sample size

Proposed unchanged from the prior calibrated design:

```text
3 matched reconstruction levels
× 2 arms
× 2 repeated blocks
× 5 frozen tests
= 60 candidate outputs
```

The reconstruction is the primary replication unit.

Candidate outputs inside a reconstruction are repeated observations, not independent `n=60` replicates.

### 5.4 Session isolation

Each reconstruction MUST run in a fresh isolated session.

No conversational state, model session state, or generated candidate content may cross between Arm C and Arm G reconstructions.

### 5.5 Execution order

Matched reconstruction arm order MUST be generated by OS-CSPRNG and frozen before execution.

The final protocol must include a hash-bound `EXECUTION-ORDER.md`.

---

## 6. Frozen safe-evolution model

The final preregistration must freeze the complete INSA v0.3 model:

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

---

## 7. B — Frozen baseline

`B` MUST bind at minimum:

1. INSA v0.3 frozen architecture source commit and blob SHA;
2. Amazing Birthday frozen source commit;
3. exact hashes of the two base reconstruction artifacts;
4. exact frozen test corpus used for BIB / prior Evolution;
5. frozen Behavioral Identity rubric;
6. frozen historical BIB envelope membership if reused;
7. evaluator identities and intended runtime identifiers;
8. Arm C and Arm G execution-facing contract hashes;
9. evaluator packet template hash;
10. execution-order artifact hash.

The final protocol must contain a single inventory table containing every frozen artifact and hash.

Any mismatch before generation is a STOP condition.

---

## 8. D — Scored behavioral dimensions

The scored dimension universe is partitioned into target mutation and required preservation dimensions.

### 8.1 M — Mutation dimension

**M1 — Nearby worldwide-historical connection**

The report must add exactly one historically significant worldwide event occurring within ±30 calendar days of the supplied birth date and clearly distinguish it from exact-date connections.

This intentionally reuses the prior Evolution target.

### 8.2 P — Preservation dimensions

Freeze these eight non-target dimensions:

**P1 — Exact-date preference**  
Exact-date historical connections remain preferred and remain clearly distinct from nearby context.

**P2 — Connection-count selectivity**  
The total selected connection count remains within the established 5–10 range. The new nearby event is part of the total presentation and MUST NOT cause uncontrolled list expansion.

**P3 — Selection significance**  
Connections remain historically meaningful rather than filler used to satisfy count or target requirements.

**P4 — End-of-report synthesis**  
The report retains a meaningful synthesis tying the selected history together.

**P5 — Lifetime framing**  
The report continues to connect the date with the person's lifetime or historical arc where appropriate.

**P6 — Warm / vivid narrative voice**  
The established narrative style remains recognizable.

**P7 — Factual discipline**  
Nearby events MUST NOT be misrepresented as exact-date events and dates/categories must remain factually disciplined.

**P8 — Avoidance of arbitrary trivia**  
The report MUST NOT preserve surface structure by filling it with weak, arbitrary, celebrity-only, or trivial material.

### 8.3 O — Out-of-scope dimensions

The following are not identity failure by themselves unless they cause a scored M/P failure:

- exact wording;
- sentence order;
- paragraph count;
- specific implementation mechanism;
- model internal plan;
- code or tool strategy;
- exact historical examples selected, provided scored significance/factual requirements are satisfied;
- harmless prose-length variation inside the accepted behavioral envelope.

`O` is frozen before execution and MUST NOT be expanded after observing candidate outputs.

---

## 9. V(d) — Permitted variance

Permitted variance is attached to dimensions; it is not a separate behavioral set.

### 9.1 Historically calibrated dimensions

For dimensions mapping to the frozen BIB 4-dimensional identity vector, use the frozen BIB non-deviated envelope plus contemporaneous Arm C as calibration.

Primary calibrated preservation gate remains:

- Arm G within-reconstruction Manhattan mean ≤ Arm C within-reconstruction Manhattan mean + **1.5**;
- Arm G within-reconstruction Manhattan mean ≤ **2.5 absolute** backstop;
- Arm C MUST satisfy the frozen non-deviated BIB envelope on its own with **no added tolerance**.

These tolerances are treatment degradation criteria, not expansions of control validity.

### 9.2 Eight explicit P-axis checks

For each P dimension, evaluators score the frozen candidate-level rubric.

Unless revised during protocol review and frozen before execution, retain the prior per-axis collapse rule:

An axis is `BROKEN` for an evaluator when BOTH are true:

- Arm G failure rate on that axis is ≥ 30%;
- Arm G failure rate is ≥ 30 percentage points worse than Arm C on that axis.

Preservation fails for that evaluator if **ANY ONE** P axis is `BROKEN`.

This rule is a frozen aggregate tolerance for the corresponding P dimension. It does not make the dimension out of scope.

### 9.3 No post-hoc tolerance changes

Every tolerance used for adjudication must be frozen before generation.

A favorable-looking candidate set is not grounds for widening `V(d)`.

---

## 10. A — Mutation acceptance tests

Reuse the prior objective modification-conformance decomposition so the target remains directly interpretable.

For every candidate, evaluators score:

- **A1:** qualifying event within ±30 calendar days is included;
- **A2:** exactly one such event is included;
- **A3:** the event is clearly distinguished from exact-date connections;
- **A4:** the event satisfies the frozen worldwide-historical-significance rubric.

`modification_conformance = A1 + A2 + A3 + A4`, range 0–4.

### 10.1 Worldwide-historical-significance rubric

Retain the prior generic rubric unless protocol review identifies a defect.

A nearby event passes the significance criterion only if at least two of four frozen criteria are met:

1. mainstream general-reference or historical treatment as international/world-historical;
2. multi-state or multi-region material involvement/effect;
3. durable consequences extending materially beyond place of origin;
4. reasonable inclusion in a concise global-history chronology for that year.

No date-specific examples may be included in evaluator instructions.

### 10.2 Proposed mutation-success gates

Require independently for both evaluators:

- **G_mod_a:** Arm G mean modification_conformance ≥ 3.5 / 4.0;
- **G_mod_b:** ≥ 80% of Arm G candidates pass all four A checks;
- **G_mod_c:** each Arm G reconstruction has ≥ 70% all-pass candidates;
- **G_mod_d:** Arm G all-pass rate exceeds Arm C all-pass rate by ≥ 50 percentage points.

Do not pool evaluators.

If Arm C naturally exhibits the target so often that the +50pp contrast cannot be achieved, modification success fails; the target is not discriminative enough under the frozen design.

---

## 11. G — Preservation gates

Preservation succeeds for an evaluator only if ALL are true:

1. calibrated 4-dimensional BIB preservation gates pass;
2. no P-axis is `BROKEN` under §9.2;
3. required inter-evaluator identity-preservation agreement gates pass;
4. factual-discipline checks show no systematic relabeling of nearby events as exact-date material.

The final protocol must state the inherited inter-evaluator thresholds exactly and hash-bind the rubric.

No pooled evaluator average may rescue a preservation failure by one evaluator.

---

## 12. Execution-facing INSA contracts

The central intervention in INSA-ID-E1 is that the intelligent execution environment receives an explicit governed contract, not merely a short modification sentence.

### 12.1 Shared contract wrapper

Arm C and Arm G MUST receive byte-identical wrapper structure and headings.

The wrapper must identify:

- baseline reference;
- target mutation section;
- required preservation section;
- out-of-scope variation section;
- instruction that implementation mechanism may vary;
- instruction that target success does not authorize non-target drift.

### 12.2 Arm C — Governed Control

Arm C receives:

```text
TARGET MUTATION: NONE

PRESERVE:
P1–P8 exactly as frozen for the experiment.

PERMITTED VARIATION:
out-of-scope implementation/prose variation only; preserve scored behavior.
```

Arm C exists to establish contemporaneous behavior under the same explicit governance wrapper.

### 12.3 Arm G — Governed Evolution

Arm G receives the same structure with:

```text
TARGET MUTATION:
Add exactly one historically significant worldwide event within ±30 calendar
 days of the birth date and clearly distinguish it from exact-date connections.

PRESERVE:
P1–P8 exactly as frozen for the experiment.

PERMITTED VARIATION:
out-of-scope implementation/prose variation only; preserve scored behavior.
```

The exact prose must be frozen and SHA-256 bound before execution.

### 12.4 No hidden implementation instruction

The contracts MUST specify behavior and preservation requirements, not prescribe code, chain-of-thought, or a particular internal implementation strategy.

This is a test of a governed behavioral boundary, not conventional implementation programming.

---

## 13. Runtime and preflight

Intended generation runtime remains the same as the prior experiment for comparability if still materially available:

- model: `claude-sonnet-4-6`;
- runtime: `claude-code 2.1.170`;
- source commit: `c369215024c9f8a849daf11bd4b872d7ee566a7a`;
- no WebSearch / WebFetch during generation;
- fresh isolated sessions.

Before freeze, protocol review must decide whether exact runtime identity is required or whether a narrowly defined compatible runtime is acceptable.

Before execution, preflight MUST verify actual runtime identity.

Material runtime deviation without prior PI adjudication is a STOP condition.

---

## 14. Evaluators and blinding

Proposed evaluators for continuity with prior evidence:

- **Evaluator A:** Codex GPT-5.6 Sol;
- **Evaluator B:** Claude Opus 4.7.

Both must pass preflight availability before generation.

No evaluator substitution is permitted after candidate outputs are observed.

### 14.1 Evaluator-visible material

Each evaluator receives:

1. frozen Amazing Birthday behavioral baseline;
2. frozen BIB identity rubric;
3. frozen P1–P8 preservation rubric;
4. frozen A1–A4 target rubric;
5. generic worldwide-historical-significance rubric;
6. blind candidate ID;
7. exact user test prompt;
8. raw candidate output;
9. required fixed return schema.

Evaluators MUST NOT see:

- Arm C / Arm G identity;
- reconstruction identity;
- execution order;
- execution-facing INSA contract text;
- treatment assignment;
- prior experiment outcome while scoring;
- the other evaluator's scores.

Candidate IDs remain blinded until both evaluator score sets are locked.

---

## 15. Frozen test corpus

Reuse the exact BIB / prior Evolution T1–T5 corpus for both repeated blocks unless protocol review identifies a specific contamination reason requiring new tests.

Rationale:

- preserves calibration against the BIB envelope;
- permits contemporaneous control validation;
- isolates the governance intervention rather than changing both contract and test distribution.

The exact five prompt texts and their file hash MUST appear in the final frozen inventory.

No new date-specific evaluator examples may be introduced.

---

## 16. Stop conditions

STOP before or during execution if any of the following occurs:

1. INSA v0.3 architecture binding does not match frozen commit/blob;
2. Amazing Birthday frozen source verification fails;
3. Arm C or Arm G contract hash mismatches;
4. test-corpus hash mismatches;
5. execution-order artifact is missing or altered;
6. either evaluator is unavailable or materially changed before generation;
7. generation runtime is materially changed without prior PI adjudication;
8. capture integrity is unreliable;
9. blinding is broken before both evaluator score sets lock;
10. more than one of three reconstructions in an arm suffers infrastructure failure;
11. Arm C fails the frozen non-deviated BIB control-validity envelope;
12. a protocol-invalidating deviation occurs and remains unadjudicated.

Arm C control failure disposition:

`CONFOUNDED_BY_POSSIBLE_RUNTIME_OR_GOVERNANCE_DRIFT`

No Arm G substantive inference is permitted after that stop.

---

## 17. Outcome logic

### 17.1 Prechecks

All must pass:

- architecture binding valid;
- source binding valid;
- contract binding valid;
- test corpus valid;
- evaluator availability valid;
- evidence chain intact;
- blinding intact;
- contemporaneous Arm C validity passes.

### 17.2 Substantive components

For each evaluator independently:

```text
Modification Success
  = G_mod_a AND G_mod_b AND G_mod_c AND G_mod_d

Identity Preservation
  = calibrated BIB preservation gates
    AND no P-axis BROKEN
    AND inter-evaluator preservation requirements satisfied
```

### 17.3 Joint disposition

Under an otherwise valid experiment:

```text
IF Modification Success = TRUE for both evaluators
AND Identity Preservation = TRUE for both evaluators
THEN EVOLUTION_PASS

IF Modification Success = FALSE for either evaluator
AND Identity Preservation = TRUE for both evaluators
THEN MODIFICATION_FAILURE

IF Modification Success = TRUE for both evaluators
AND Identity Preservation = FALSE for either evaluator
THEN PRESERVATION_FAILURE

IF Modification Success = FALSE for either evaluator
AND Identity Preservation = FALSE for either evaluator
THEN MODIFICATION_AND_PRESERVATION_FAILURE
```

`INCONCLUSIVE_PENDING_FURTHER` is reserved for genuine residual ambiguity after predeclared substantive outcomes are exhausted.

It MUST NOT soften a substantive failure.

---

## 18. Claims permitted and prohibited

### 18.1 If EVOLUTION_PASS

Permitted claim:

> Under the frozen Amazing Birthday task, runtime, architecture contract, test corpus, and evaluation design, an INSA v0.3 governed evolution contract achieved the declared target modification while preserving the predeclared non-target Behavioral Identity envelope.

### 18.2 Still prohibited after a PASS

A PASS MUST NOT be used to claim:

- safe evolution is solved generally;
- INSA is empirically validated as a whole;
- the result generalizes to all mutations;
- the result generalizes to stateful or consequential systems;
- the result generalizes across model providers;
- the INSA contract is causally superior to the prior protocol based solely on cross-experiment comparison;
- Value Architecture or Authority Architecture has been validated.

### 18.3 If failure

A substantive failure is evidence that the frozen INSA Identity mechanism, as instantiated here, is insufficient under the tested conditions.

The architecture may then be narrowed or revised in a new version. v0.3 itself MUST NOT be edited retroactively.

---

## 19. Secondary historical comparison

After the primary disposition is locked and unblinded, report descriptively:

- modification metrics versus the prior DbI Evolution experiment;
- preservation metrics versus the prior experiment;
- reconstruction-level heterogeneity;
- evaluator agreement differences;
- whether the failure class changed.

Label this section:

**POST-FAILURE HISTORICAL COMPARISON — DESCRIPTIVE, NOT CAUSAL**

Do not use it to override the primary preregistered disposition.

---

## 20. Roles

Proposed role separation:

- **Principal Investigator / Acceptance Authority:** Frank Ventura;
- **Generation Operator / Blind-map Holder:** Hermes;
- **Evaluator A:** Codex GPT-5.6 Sol;
- **Evaluator B:** Claude Opus 4.7;
- **Final Synthesizer:** ChatGPT;
- **Architecture baseline:** INSA v0.3 FROZEN.

The operator may know treatment assignment operationally but MUST NOT expose it to evaluators before score lock.

---

## 21. Artifacts required before protocol freeze

The final frozen protocol package should contain at minimum:

```text
protocol/
  PROTOCOL-vX-frozen-final.md
  EXECUTION-ORDER.md
  FREEZE-MANIFEST.md

inputs/
  architecture-binding.json
  baseline-binding.json
  behavioral-dimensions.json
  arm-c-governed-control-contract.txt
  arm-g-governed-evolution-contract.txt
  baseline-envelope-membership.json
  exact-test-corpus.txt
  evaluator-input-packet-template.md
  worldwide-significance-rubric.md

README.md
```

Every frozen artifact must have a recorded SHA-256 in the freeze manifest.

---

## 22. Protocol review questions

Before freeze, an adversarial reviewer must answer at least:

1. Does Arm G differ from Arm C only in the target mutation content?
2. Does the governance wrapper itself alter baseline behavior enough to invalidate comparison with BIB?
3. Is Arm C sufficient to detect that effect contemporaneously?
4. Is `P2` connection count compatible with the additive target, or does it create an unintended structural conflict?
5. Are P1–P8 truly non-target dimensions, or does the mutation necessarily alter any of them?
6. Are `V(d)` tolerances calibrated rather than chosen to favor a pass?
7. Does reuse of the prior target create unacceptable experimenter overfitting, and if so can the claim be narrowed rather than changing the target?
8. Are evaluator instructions capable of inferring treatment assignment from obvious nearby-event presence, and does that matter if arm identity remains hidden?
9. Is the BIB historical envelope still a valid control reference after the explicit governance wrapper is introduced?
10. Are the primary claim and the historical comparison separated strongly enough?
11. Could a candidate satisfy the mutation by degrading the exact-date core while still slipping through the preservation gates?
12. What result would force a revision of INSA v0.3 rather than another implementation tweak?

The protocol MUST NOT freeze until these questions are adjudicated.

---

## 23. Authorization boundary

This v0.1 draft is **design only**.

It authorizes:

- protocol critique;
- artifact construction;
- hash preparation;
- preregistration refinement;
- freeze review.

It does **not** authorize:

- generation preflight that calls paid models;
- candidate generation;
- evaluator invocation;
- scoring;
- unblinding;
- model dispatch of any kind.

After the protocol and all inputs are frozen, execution requires a separate Frank-as-PI GO referencing the frozen protocol commit SHA.

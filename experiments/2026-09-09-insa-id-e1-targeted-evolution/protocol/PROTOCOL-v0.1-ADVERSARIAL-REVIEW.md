# INSA-ID-E1 Protocol v0.1 Draft — Adversarial Review

**Date:** 2026-09-09  
**Artifact:** `PROTOCOL-v0.1-draft.md`  
**Disposition:** **REVISION_REQUIRED_BEFORE_PREREGISTRATION_FREEZE**

## Executive finding

The draft correctly derives the experiment from INSA v0.3 FROZEN and transparently treats the study as a post-failure intervention rather than an independent replication.

The core two-arm design is defensible, but several details should be corrected before freeze. The most important is evaluator contamination: the target mutation is behaviorally visible, so an evaluator given the mutation rubric and preservation rubric in the same pass may infer treatment and carry modification expectations into subjective identity scoring.

## Findings

### PE-01 — Separate mutation and preservation evaluation passes

**Severity:** HIGH

The draft proposes that the same evaluator session score both A1–A4 mutation conformance and P1–P8 preservation.

Because the nearby-event target is directly observable, true treatment blinding is impossible from content alone. Supplying the mutation rubric additionally primes the evaluator to search for treatment behavior before making subjective preservation judgments.

#### Required correction

For each evaluator model, use independent fresh evaluation sessions:

- **Identity pass:** baseline + P1–P8 + calibrated BIB identity rubric only. No A1–A4 mutation rubric, no modification specification, no treatment labels.
- **Mutation pass:** A1–A4 + worldwide-significance rubric only. No P-axis preservation adjudication.

Candidate blind IDs may be independently randomized between the two passes.

The final synthesis joins locked results by blind mapping only after all required score sets are locked.

This does not make treatment inference impossible, but it removes avoidable rubric-induced priming.

---

### PE-02 — Value applicability statement is too vague

**Severity:** MEDIUM

The draft says Values is active only insofar as Amazing Birthday behavioral values are represented by preservation dimensions. This conflates behavioral identity dimensions with Value Architecture.

The application does contain discretionary selection and presentation choices, so declaring Values entirely N-A would also be questionable under INSA v0.3 applicability rules.

#### Required correction

Declare:

```text
Values: ACTIVE
Scope: the application exercises discretionary selection and presentation.
Value Conformance Claim: NONE in this experiment.
Status: general Value Architecture conformance remains UNTESTED / out of scope.
```

P1–P8 remain Behavioral Identity dimensions, not Value Architecture evidence.

---

### PE-03 — Runtime rule should be exact for the frozen design

**Severity:** MEDIUM

The draft leaves open whether a narrowly compatible runtime may be accepted before freeze.

That weakens comparability and introduces discretion at the moment the protocol is supposed to become fixed.

#### Required correction

Freeze the intended generation runtime exactly:

- `claude-sonnet-4-6`;
- `claude-code 2.1.170`;
- the prior no-web tool posture;
- fresh-session semantics.

If unavailable before execution, STOP and seek PI adjudication before any candidate is generated. A revised runtime requires a new protocol version; do not silently widen compatibility.

---

### PE-04 — Historical comparison must not become the experiment's causal story

**Severity:** MEDIUM

Reusing the same mutation is scientifically useful, but the strongest temptation after a PASS would be to say the INSA contract "fixed" the prior failure.

The design does not support that causal claim by itself because the prior experiment occurred at a different time and the intervention was not randomized against a contemporaneous legacy-modification arm.

#### Required correction

Retain the two-arm primary design for cost discipline, but predeclare:

> Cross-experiment improvement is descriptive only. A future contemporaneous legacy-vs-INSA mechanism study would be required for causal superiority.

---

### PE-05 — P2 additive-target tension must be explicit

**Severity:** MEDIUM

The target adds one nearby event while P2 preserves total connection count at 5–10.

This is not inherently contradictory, but it requires the execution environment to rebalance selection when baseline behavior is already near the upper bound.

#### Required correction

Make the intended semantics explicit in the execution-facing contract:

> The target event is part of the total 5–10 selected connections. Do not simply append an 11th connection; rebalance selection if necessary while preserving exact-date priority and significance.

This turns the tension into a deliberate preservation test rather than an accidental ambiguity.

---

### PE-06 — Exact inter-evaluator preservation thresholds must be frozen

**Severity:** MEDIUM

The draft leaves inherited inter-evaluator thresholds to be filled later.

#### Required correction

Carry forward the prior frozen thresholds unless review identifies a reason to change them before any outputs exist:

- identity-preservation agreement ≥ 0.9;
- per-dimension MAE ≤ 1.0.

Any change requires explicit rationale and must be frozen before execution.

---

### PE-07 — Applicability and architecture binding should be evaluator-invisible

**Severity:** LOW

Evaluators do not need the INSA architecture document to score the candidate behavior. Giving it to them could prime architectural expectations.

#### Required correction

Keep architecture binding, applicability, and protocol theory in the audit layer. Evaluators receive only the minimum behavioral rubrics needed for their isolated scoring pass.

---

### PE-08 — Baseline binding should freeze all non-target governance relevant to the experiment

**Severity:** MEDIUM

The draft baseline inventory is good but should explicitly bind the applicability declaration and the exact Value-scope declaration even though Value conformance is not being tested.

#### Required correction

Add to `B`:

- applicability declaration hash;
- Value-scope / no-conformance-claim declaration hash;
- role/authority declaration for experimental acceptance.

This prevents governance changes from becoming an untracked source of interpretation drift.

---

## Questions adjudicated

### Does the governed wrapper itself threaten BIB comparability?

Yes, potentially. The contemporaneous Arm C is therefore essential. Arm C must also remain inside the frozen BIB control-validity envelope; otherwise stop as confounded.

### Is the prior target overfit because it already failed once?

It is unsuitable for an independent confirmatory claim but suitable for an explicitly labeled post-failure intervention experiment. The protocol already narrows the claim accordingly.

### Is a third legacy arm required now?

No. A third arm would increase cost materially. The two-arm study can answer the bounded question "can the INSA-governed mechanism achieve modification plus preservation?" It cannot establish causal superiority over the old mechanism.

### Are P1–P8 truly non-target dimensions?

Yes, provided P2 explicitly counts the new nearby event within the total 5–10 and P7 is interpreted as preservation of factual discipline rather than absence of nearby material.

### Could the target succeed by degrading exact-date behavior?

The combined calibrated BIB gates, P1, P2, P3, and P7 are intended to catch that. The protocol should preserve all of them independently rather than rely on a pooled composite.

## Required revision set

Before freeze, v0.2 draft should:

1. split each evaluator into independent Identity and Mutation passes;
2. correct the Values applicability language;
3. freeze the exact runtime instead of a compatible-runtime option;
4. strengthen the non-causal historical-comparison boundary;
5. specify P2 rebalancing semantics;
6. freeze inter-evaluator thresholds at 0.9 agreement / 1.0 per-dim MAE unless explicitly revised pre-execution;
7. keep architecture theory out of evaluator packets;
8. expand baseline binding to include applicability/value-scope/acceptance-role declarations.

## Disposition

**REVISION_REQUIRED_BEFORE_PREREGISTRATION_FREEZE**

The experiment remains promising and the required changes are bounded. No candidate generation or evaluator invocation is authorized.

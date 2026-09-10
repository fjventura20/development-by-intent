# INSA Architecture v0.2 Candidate — Freeze-Gate Review

**Date:** 2026-09-09  
**Artifact:** [`INSA-ARCHITECTURE-v0.2-candidate.md`](INSA-ARCHITECTURE-v0.2-candidate.md)  
**Disposition:** **REVISION_REQUIRED_BEFORE_FREEZE**

> **Reviewer disclosure:** This was an internal AI-assisted methodological review within the PI-led research process, not independent external validation. The original artifact did not contemporaneously record a sufficiently specific reviewer/model identity, exact model version, or authoring-context access condition. See [`REVIEWER-DISCLOSURES.md`](REVIEWER-DISCLOSURES.md). Unknown details are intentionally not reconstructed after the fact.

## Summary

The v0.2 candidate resolves the high-severity defects identified in the v0.1 adversarial review. The five-boundary model still appears useful.

The freeze gate nevertheless found four remaining issues that materially affect conformance or experiment design. Two are high severity because they would permit ambiguous adjudication in the planned safe-evolution and authority experiments.

## FG-01 — Permitted variance is modeled as a competing set

**Severity:** HIGH

The candidate classifies each behavioral dimension as one of `M`, `P`, `V`, or `O`.

That is conceptually wrong. A preserved dimension may legitimately tolerate stochastic or rubric-defined variance. Therefore permitted variance is not a peer category to Mutation or Preservation.

### Required correction

Use:

```text
D = scored behavioral dimensions
M = target mutation dimensions
P = required preservation dimensions
O = out-of-scope dimensions

D = M ∪ P ∪ O
M ∩ P = ∅
M ∩ O = ∅
P ∩ O = ∅

V(d) = dimension-specific permitted variance / tolerance
       defined for any dimension d where variance is allowed
```

`V(d)` must be frozen before execution whenever it affects adjudication.

Acceptance tests `A` should bind to `M`; preservation gates `G` should bind to `P`.

## FG-02 — Authority traceability lacks grant authenticity

**Severity:** HIGH

The v0.2 candidate requires authority to be traceable to an originating grant, but a traceable grant is not necessarily a trustworthy grant.

An attacker, stale process, or unauthorized agent could create a well-recorded but invalid authorization artifact.

### Required correction

Add an invariant requiring consequential authority grants to resolve to a trusted authority source under the deployment's trust model.

The architecture need not prescribe cryptography or identity technology. It must require authenticity, not merely provenance.

## FG-03 — Consequential action lacks a formal definition

**Severity:** MEDIUM

Several authority and evidence requirements depend on whether an action is consequential. The term must be defined consistently.

### Required correction

Define a consequential action as one that materially changes external or durable state, commits resources, affects another person or organization, expands or exercises privilege, creates meaningful risk, or is difficult to reverse.

Deployments may narrow or extend this definition, but they may not silently treat obviously consequential actions as non-consequential to bypass controls.

## FG-04 — Evidence provenance lacks an integrity requirement

**Severity:** MEDIUM

Evidence may be well labeled but still mutable after the fact.

### Required correction

For evidence used to establish consequential conformance, require integrity protection appropriate to the claim so that material alteration can be prevented or detected.

The mechanism may include immutable logs, signed records, version control, hashes, append-only stores, external audit, or equivalent controls.

## FG-05 — Boundary applicability is implicit

**Severity:** MEDIUM

Not every application will exercise every boundary equally. A deterministic component may have no meaningful value discretion; a stateless application may not need a State / Continuity Contract.

Without an applicability rule, implementers can either over-claim unnecessary conformance or declare difficult boundaries irrelevant after failure.

### Required correction

Add an **Applicability Declaration** established before consequential execution or experiment scoring:

```text
Intent        ACTIVE / N-A with rationale
Authority     ACTIVE / N-A with rationale
Values        ACTIVE / N-A with rationale
Identity      ACTIVE / N-A with rationale
State         ACTIVE / N-A with rationale
Evidence      ACTIVE / N-A with rationale
```

Intent and Evidence are expected to be active for any meaningful INSA application claim. Other contracts may be `N-A` only with a stated reason consistent with the system's actual behavior.

## Disposition

**REVISION_REQUIRED_BEFORE_FREEZE**

The necessary changes are bounded and do not currently undermine the five-boundary model.

Recommended next artifact: `INSA-ARCHITECTURE-v0.3-candidate.md`, incorporating FG-01 through FG-05 and then subjected to a final consistency gate before any INSA-ID-E1 preregistration.
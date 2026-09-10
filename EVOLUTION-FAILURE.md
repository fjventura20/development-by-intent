# DbI Evolution Experiment — Negative Result

**Disposition:** `MODIFICATION_AND_PRESERVATION_FAILURE`

This document promotes an existing negative result to the public evidence surface. It does not rename, soften, or reinterpret the original disposition.

## Question tested

The experiment asked whether an intentional change to one part of an application's behavior could be introduced while preserving the application's predeclared non-target behavioral identity.

In compact form:

> **Can intent change modify the target behavior while preserving the behavior that was explicitly designated not to change?**

The experiment was motivated by earlier reconstruction work showing that recognizable behavioral identity could survive reconstruction in fresh AI environments.

## Result

The experiment did **not** establish safe targeted evolution.

Final disposition:

`MODIFICATION_AND_PRESERVATION_FAILURE`

The important distinction is:

> **Reconstruction stability does not imply evolution stability.**

An application may be reproducibly reconstructed from preserved behavioral information and still fail when asked to change one behavioral dimension while preserving the rest.

## Why this result matters

This is a negative result, but it narrowed the architecture.

It showed that "the application can be reconstructed" and "the application can be safely evolved" are different engineering claims requiring different evidence.

That result directly motivated the stronger safe-evolution structure now present in frozen INSA v0.3, including explicit treatment of:

- a frozen pre-change baseline;
- scored behavioral dimensions;
- target mutation dimensions;
- required preservation dimensions;
- out-of-scope dimensions;
- dimension-specific permitted variance;
- acceptance tests bound to intended change;
- preservation gates bound to non-target identity.

The next INSA experiment, `INSA-ID-E1 — Targeted Evolution With Preservation`, exists specifically because the earlier result failed to establish this property.

## Claim boundary

This result supports the claim that **behavioral reconstruction and controlled behavioral evolution must be treated as distinct properties**.

It does not establish that:

- controlled evolution is impossible;
- INSA's current safe-evolution contract is sufficient;
- the earlier failure will reproduce across every model, application, or protocol;
- the five-boundary INSA architecture is validated.

Those remain experimental questions.

## Evidence-record status

The negative disposition is already referenced in the project's current status and architecture rationale. At the time this public note was created, the original DbI Evolution result had not been normalized as a standalone first-class experiment directory on `main` comparable to the earlier reconstruction experiments.

Accordingly, this file is a **public evidence index/narrative**, not a replacement for the original frozen protocol, evaluator outputs, hashes, or execution records. When those records are normalized into the repository's experiment tree, this document should link to them without changing the historical disposition.

## Research consequence

The correct response to this failure was not to hide it or loosen the preservation criterion. It was to make the distinction experimentally explicit:

```text
reconstruction stability
        ≠
safe evolution stability
```

The architecture must now earn the stronger claim through new evidence.
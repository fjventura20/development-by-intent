# Research Agenda

## Phase 1 — Reproducibility

Goal: determine whether independently operated AI sessions can reproduce a conversationally developed application's behavior.

Core experiments:

1. **Full-transcript reconstruction** — provide the complete original development conversation to a fresh session.
2. **Artifact-only reconstruction** — provide only the preserved specification/checkpoint artifacts.
3. **Minimal-artifact reconstruction** — progressively remove artifacts to find the recovery floor.
4. **Cross-model reconstruction** — repeat the same procedure with multiple frontier models.
5. **Repeatability test** — reconstruct multiple times with the same model and compare variance.

## Phase 2 — Durability

Goal: define a practical preservation standard.

Questions:

- Is the original conversation part of the source?
- Which tests are required to validate identity?
- How are implicit behaviors captured?
- How should preservation checkpoints be versioned?
- How should intentionally changed behavior be distinguished from drift?

## Phase 3 — Development economics

Goal: measure whether DbI materially changes development effort.

Candidate metrics:

- elapsed time to first useful application
- number of conversational turns
- time to correct a known defect
- time to implement a requirement change
- number of manually maintained implementation artifacts
- reconstruction fidelity
- number of regressions introduced per change

Where possible, compare with a small conventional implementation of the same bounded application.

## Phase 4 — Applicability boundary

Goal: identify where DbI should and should not be used.

Test application categories such as:

- research/reporting micro-apps
- document generation with governance rules
- classification and triage
- personal workflow applications
- data transformation
- deterministic calculators
- transactional workflows
- applications with external side effects
- high-assurance or safety-critical systems

## Success criteria

The project succeeds even if the result is a narrow boundary.

A scientifically useful outcome would be a well-supported statement of the form:

> Development by Intent is effective for application classes A, B, and C under preservation conditions X and testing conditions Y, but performs poorly for D and E.

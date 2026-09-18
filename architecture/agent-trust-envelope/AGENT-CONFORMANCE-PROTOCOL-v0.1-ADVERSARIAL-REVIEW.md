# Agent Conformance Protocol v0.1 — Adversarial Review

**Reviewed artifact:** `AGENT-CONFORMANCE-PROTOCOL-v0.1.md`  
**Review mode:** design-only adversarial review  
**Disposition:** CHANGES REQUIRED BEFORE FREEZE

## 1. Summary

The protocol correctly closes the post-admission lifecycle gap and preserves the critical separation:

```text
CONFORMANT != AUTHORIZED_TO_ACT
```

It also correctly treats current trust as evidence-backed state rather than a permanent attribute.

However, v0.1 should not be frozen yet. Seven issues need correction because they could permit stale authority, authority concentration, ambiguous trigger handling, or unsafe restoration.

## 2. Findings

### F1 — Trigger observation is underspecified
**Severity:** HIGH

The protocol defines triggers but does not define who is trusted to observe and publish them.

An agent-controlled trigger feed could omit a runtime/model/tool change and preserve a stale CONFORMANT state.

**Required correction:** define authoritative trigger sources, signed TriggerObservation artifacts, and fail-closed behavior when a mandatory source becomes unavailable.

### F2 — “Continuous” conformance lacks bounded staleness
**Severity:** HIGH

Event-driven checks alone cannot guarantee that missed events are discovered.

**Required correction:** every profile must define a maximum conformance age or equivalent bounded-refresh rule for authority-bearing scopes. “No trigger observed” must not imply indefinite validity.

### F3 — R13 is too powerful
**Severity:** HIGH

v0.1 allows R13 to impose restriction/suspension and publish restoration. That can collapse evaluator and lifecycle-control authority.

**Required correction:** distinguish evaluation from authoritative lifecycle transition. R13 may recommend/sign evaluation; a separately authorized Lifecycle State Authority must publish authority-changing state unless superior policy explicitly permits concentration.

### F4 — State propagation is not atomic enough
**Severity:** HIGH

A new suspension can race with capability issuance/execution.

**Required correction:** require monotonic state version/epoch binding and final current-state verification by the executor. A stale capability must fail if the observed lifecycle epoch is no longer current.

### F5 — Partitioned conformance is ambiguous
**Severity:** MEDIUM

The protocol permits unaffected scopes to remain available but does not define scope inheritance or default semantics.

**Required correction:** default to whole-role impact unless the profile explicitly defines independent conformance partitions and their dependency graph.

### F6 — Restoration can accidentally reuse compromised authority
**Severity:** HIGH

A fresh ConformanceDecision alone is insufficient if the trigger involved compromised identity/key/runtime provenance.

**Required correction:** restoration must satisfy trigger-specific remediation and must not reuse revoked/compromised artifacts unless the controlling revocation policy explicitly permits reinstatement.

### F7 — Trigger storms / denial-of-service are unbounded
**Severity:** MEDIUM

Repeated low-value triggers could indefinitely block an agent.

**Required correction:** allow deduplication/coalescing only when it does not suppress a higher-severity or newer-state transition; audit coalescing decisions.

## 3. Required Architectural Additions

Before freeze, add:

1. `ConformanceTriggerObservation` artifact.
2. Authoritative trigger-source rules.
3. Bounded staleness / maximum conformance age.
4. Separate `R14 — Lifecycle State Authority`.
5. Explicit state version/epoch check at capability issuance and execution.
6. Whole-role default scope impact.
7. Trigger-specific restoration constraints.
8. Trigger deduplication rules.

## 4. Freeze Recommendation

Do **not** freeze v0.1.

Produce v0.1.1 incorporating F1–F7, then perform a narrow reconciliation check against:

- Agent Qualification & Admission Protocol v0.2.2
- ATE Revocation & Trust-State Model v0.1
- ATE Enforcement Plane v0.1
- ATE Audit & Accountability Model v0.1

If those corrections reconcile cleanly, v0.1.1 can become the freeze candidate without another broad redesign.

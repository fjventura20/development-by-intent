# ATE Trust-Decision Composition Adversarial Review v0.1

**Status:** Adversarial design review  
**Date:** 2026-09-16  
**Reviewed artifact:** `ATE-TRUST-DECISION-COMPOSITION-ARCHITECTURE-v0.1.md`

---

## 1. Disposition

**REVISION_REQUIRED_BEFORE_PROTOCOL_DESIGN**

The composition architecture has the correct overall shape: action-first canonicalization, authoritative risk derivation, exact runtime/qualification/governance/capability intersection, current-state binding, deterministic denial, signed decision-input digest, and executor recheck contract.

No fundamental redesign is required.

However, several ambiguities could still permit duplicate grant artifacts, stale execution after state change, inconsistent denial semantics, or substitution between otherwise valid decision contexts.

---

## 2. Finding R1 — Grant cardinality is not explicit

### Problem

The architecture distinguishes decision ID, replay nonce/authorization ID, and operation ID, but it does not require idempotent grant issuance.

Two concurrent or retried requests could potentially produce:

```text
TrustDecision G1: TRUST_GRANTED
TrustDecision G2: TRUST_GRANTED
```

for the same one-time authorization/operation identity.

P1-style executor replay controls may still prevent two external effects, but the trust-decision layer would have issued two independently valid grants for one logical authorization.

That weakens audit causality and complicates revocation/cardinality semantics.

### Required correction

Define one stable `decision_request_id` or `authorization_instance_id` before decision issuance and require:

```text
one authorization_instance_id
    -> at most one unique TRUST_GRANTED decision identity
```

Grant issuance must be serialized/idempotent.

A retry for the same authorization instance and same decision context should return the exact persisted grant.

If the controlling decision context changed before grant issuance, do not silently replace the old context under the same authorization instance; require a new decision attempt/version under explicit rules.

Denials may be historical attempts, but a one-time authorization instance must never accumulate multiple executable grants.

---

## 3. Finding R2 — State can change immediately after the pre-sign check

### Problem

The pre-sign stability check reduces mixed-state grants, but it cannot prevent an authoritative state change immediately after signing.

This is unavoidable without a single transactional trust-state system.

The architecture currently leaves execution-time recheck selection too profile-dependent to guarantee that high-consequence state invalidation is honored.

### Required correction

Define a minimum set of **execution-invalidating dependency classes** whose change can make an unexecuted grant unusable.

At minimum the signed decision/recheck contract must be able to require current recheck of:

- TrustDecision revocation/status;
- capability/authorization current state;
- active policy/revocation epoch when policy marks changes execution-invalidating;
- qualification status when suspension/revocation is designated immediate;
- governance acceptance/status when designated immediate;
- required human/threshold approval validity;
- mutable target state when required;
- mandatory audit availability.

Risk/assurance policy determines which are synchronous at execution, but policy must not be able to omit a dependency whose own authoritative semantics say `invalidates_unexecuted_grants = true`.

This avoids treating the decision-time snapshot as a lease over state that policy intended to revoke immediately.

---

## 4. Finding R3 — Current-state vector needs source authority binding

### Problem

A vector of epoch numbers/digests is insufficient if the source registry/authority responsible for each epoch is not cryptographically bound.

A malicious or misconfigured input could present a self-consistent but unauthorized vector.

### Required correction

Each entry must bind:

```text
state_class
state_authority_id
state_object_digest
state_epoch
observed_at
```

and the composition verifier must verify authority-role permission for that state class.

`CurrentTrustStateVector` should be a deterministic composition of verified authoritative observations, not an independently trusted assertion.

---

## 5. Finding R4 — TrustDecisionInput includes `evaluated_at`, which weakens deterministic input identity

### Problem

Equivalent semantic inputs evaluated milliseconds apart produce different `trust_decision_input_digest` values solely because `evaluated_at` changed.

This undermines clean idempotent retry/cardinality semantics.

### Required correction

Separate:

```text
DecisionSemanticContext
```

from issuance metadata.

The semantic context digest should contain the canonical action and all controlling verified context/state digests but not incidental evaluator timestamps unless time itself changes a controlling validity/freshness predicate.

The signed `TrustDecision` may carry `evaluated_at` / `issued_at` separately.

If exact time is security-controlling, bind a canonical `evaluation_time_bucket` or explicit time-state object rather than incidental wall-clock serialization.

---

## 6. Finding R5 — Denial determinism needs a complete gate-evaluation rule

### Problem

The architecture freezes primary gate order, but implementations might short-circuit at slightly different subchecks within a gate and emit different primary reason codes for the same input.

### Required correction

Each gate must define:

- deterministic internal predicate order; or
- a deterministic precedence rule over all failed predicates in that gate.

For example:

```text
D6 qualification:
  Q1 signature/issuer
  Q2 current status
  Q3 subject/profile
  Q4 capability
  Q5 risk
  Q6 assurance
```

or equivalent reason precedence.

This is protocol-level detail but the architecture should require it.

---

## 7. Finding R6 — Qualification assurance semantics must use one canonical comparison model

### Problem

The composition draft uses `qualified_assurance_ceiling`, while older qualification artifacts contain both minimum-assurance concepts and evaluated assurance/tier constraints.

Without one normalized semantic, implementations could reverse the comparison.

### Required correction

Introduce a normalized verified field such as:

```text
maximum_authorizable_assurance_profile
```

or a signed set/range of assurance profiles actually covered by qualification.

Then define unambiguously:

```text
required_assurance_profile in qualification.authorizable_assurance_profiles
```

Avoid relying on natural-language “minimum/ceiling” interpretation in the composition algorithm.

---

## 8. Finding R7 — Capability containment requires one normalized action vocabulary

### Problem

`CapabilityToken` and Qualification may express scope using different operation/resource taxonomies.

Checking both against `canonical_action_digest` does not by itself prove semantic containment if one says `WRITE_FILE` and another says `repository-write` under different taxonomies.

### Required correction

Bind a canonical capability taxonomy/version into:

- canonical action;
- qualification capability scope;
- CapabilityToken;
- risk classification;
- governance structural rules.

Cross-version translation is allowed only through signed compatibility/mapping policy.

Unknown mapping fails closed.

---

## 9. Finding R8 — Governance currentness must distinguish summary validity from dependency validity

### Problem

The architecture correctly says historical coverage manifest is insufficient, but the `GovernanceCoverageContext` could still become a replayable summary unless its currentness derivation is explicit.

### Required correction

Bind into the context:

```text
coverage_evaluated_at
dependency_state_vector_digest
coverage_valid_until
```

and require current verification of every dependency class marked current by governance policy.

The context is a verified derived result, not an independent long-lived credential unless policy explicitly gives it a bounded validity lease.

---

## 10. Finding R9 — Approval substitution and approval scope need exact binding

### Problem

A digest list of approvals does not guarantee the approval authorizes this exact action/risk/context.

### Required correction

Every required approval must bind at least:

```text
canonical_action_digest
subject/runtime when required
risk_class
required_assurance_profile
policy_digest / epoch
approval role/class
validity
```

Threshold approval sets must also bind one common approval-set/context digest so individually valid approvals from different requests cannot be combined.

---

## 11. Finding R10 — Decision authority needs its own issuer ceiling

### Problem

The architecture verifies that the Trust Decision Authority is authorized, but it does not state that decision authority itself may have risk/capability/trust-domain ceilings.

### Required correction

Decision-authority credentials should constrain at least:

```text
permitted_trust_domains
permitted_project_scopes
permitted_capability_classes
maximum_risk_class
maximum_assurance_profile
maximum_decision_lifetime
```

A correctly signed grant outside those ceilings is invalid.

The participant cannot choose a more permissive decision authority.

---

## 12. Finding R11 — Decision-input substitution must bind composition profile and gate specification

### Problem

`composition_profile_id` is present, but an identifier alone is not enough if the profile content can change.

### Required correction

Bind:

```text
composition_profile_id
composition_profile_version
composition_profile_digest
```

The digest identifies the exact gate semantics/reason precedence/recheck policy used.

Unknown or superseded composition profiles fail according to active policy.

---

## 13. Finding R12 — Replay precondition and external-effect idempotency need one binding chain

### Problem

Nonce, authorization ID, operation ID, and requested-action digest are distinct. Without explicit binding, a replay token could be validly paired with the wrong stable operation identity.

### Required correction

Require a single chain:

```text
authorization_instance_id
  -> canonical_action_digest
  -> stable operation_id (where applicable)
  -> replay/nonces
  -> TrustDecision
  -> executor/resource idempotency key
```

All identities must be cryptographically bound.

---

## 14. Finding R13 — Target-state changes may elevate risk, not merely invalidate target digest

### Problem

A resource resolution change can make the action higher risk (for example staging resolves to production).

A simple target-state mismatch denial is safe, but a system might be tempted to continue under the old risk classification after resolving the new target.

### Required correction

Any material target/action resolution change requires:

```text
recanonicalize action
reclassify risk
recompute all downstream decision contexts
```

Never patch only the target digest inside an already-composed decision.

---

## 15. Finding R14 — Evidence/currentness changes need explicit effect on already-issued grants

### Problem

Some evidence is issuance-snapshot; some is continuously current. The composition draft does not explicitly bind that lifecycle distinction into grant invalidation semantics.

### Required correction

For each controlling dependency record:

```text
lifecycle_class
invalidates_unexecuted_grants_on_change
execution_recheck_required
```

An issuance-snapshot evidence receipt need not be re-run at execution merely because time advanced.

A continuously-current dependency may invalidate an unexecuted grant if policy says so.

---

## 16. Accepted Elements

The following are accepted and should not be reopened absent contradiction:

- action-first composition;
- authoritative risk classification;
- use of `VerifiedRuntimeContext` digest;
- current qualification context;
- bounded governance coverage context;
- evidence-currentness summary rather than raw re-evaluation;
- dual containment by qualification + CapabilityToken;
- explicit structural/approval context;
- monotonic current-state observations;
- signed `TrustDecisionInput` context;
- AND-gate composition, no trust scoring;
- deterministic reason-code architecture;
- execution-time recheck contract;
- executor does not become a second decision authority;
- fail-closed behavior.

---

## 17. Required v0.1.1 Corrections

A surgical v0.1.1 should add:

1. authorization-instance / one-grant cardinality;
2. execution-invalidating dependency semantics;
3. authority-bound current-state observations;
4. semantic-context digest separated from incidental timestamps;
5. within-gate deterministic reason precedence requirement;
6. normalized qualification assurance semantics;
7. canonical capability taxonomy/version;
8. explicit governance dependency-state binding;
9. exact approval/set binding;
10. decision-authority scope ceilings;
11. composition profile version + digest;
12. nonce/action/operation/idempotency identity chain;
13. full recomposition after material target/action resolution change;
14. lifecycle-driven effect of dependency changes on unexecuted grants.

Then perform one final adversarial pass before designing a conformance protocol.

---

## 18. Final Review Statement

The v0.1 architecture is close but not freeze-ready.

The most important principle exposed by this review is:

> **A deterministic trust decision is not merely a verdict over valid artifacts. It is a uniquely identified grant over one exact semantic action/context, derived from authoritative current state, with explicit rules for what may invalidate that grant before external effect.**

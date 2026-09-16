# ATE Behavioral & Functional Evidence — Final Consistency Review v0.1

**Status:** Final consistency review of v0.1.1  
**Date:** 2026-09-16  
**Reviewed artifact:** `ATE-BEHAVIORAL-FUNCTIONAL-EVIDENCE-ARCHITECTURE-v0.1.1.md`

## Disposition

**ONE_SURGICAL_REVISION_REQUIRED_BEFORE_PROTOCOL_DESIGN**

The v0.1.1 architecture resolves the substantive defects from the first adversarial review and is consistent with the Qualification & Requalification Architecture, Revocation & Trust-State Model, Production Requirements, and frozen P2 boundary.

One remaining issue affects the core anti-selection guarantee.

---

## 1. Pre-registration Chronology Is Not Yet Proven

v0.1.1 requires a signed `FormalRunRegistration` before first subject invocation.

However, a signature plus `registered_at` field is not itself proof of chronology if the registering actor can choose/backdate the timestamp after observing results.

### Attack

1. Runner executes many cases/runs privately.
2. Runner identifies a favorable population.
3. Runner creates and signs `FormalRunRegistration` with an earlier `registered_at` timestamp.
4. Evidence appears preregistered even though registration was post hoc.

### Required correction

A formal registration must receive an externally/order-authoritative **PrecommitmentReceipt** before the subject is invoked.

Acceptable local architecture:

```text
FormalRunRegistration
       |
       | digest
       v
Precommitment Registry / Authority
       |
       v
PrecommitmentReceipt {
    commitment_id
    registration_digest
    campaign_key
    monotonic_registration_sequence
    committed_at
    registry_epoch
    authority_id
    signature
}
```

The trusted local registry/authority is outside the runner's unilateral control for chronology purposes.

The runner may submit the registration but cannot later manufacture an earlier accepted sequence/commitment.

The first subject invocation must bind/reference the accepted `commitment_id` or `registration_digest` whose PrecommitmentReceipt already exists.

This is a local evidence-ordering requirement, not a blockchain/global timestamp requirement.

---

## 2. Campaign History Must Be Authoritatively Keyed

v0.1.1 correctly states that a new campaign ID must not hide earlier failures, but campaign identity remains chosen as an artifact field.

### Required correction

Define an authoritative `campaign_key` derived/canonicalized from at least:

```text
trust_domain_id
evidence_requirement_id
subject_principal_id
qualified_profile_digest
qualification_or_admission_attempt_id (when applicable)
```

The campaign registry SHALL maintain all formal attempts associated with that key.

A new arbitrary `campaign_id` with the same controlling campaign key does not erase prior attempts.

When a profile/protocol/qualification-attempt change legitimately starts a new campaign lineage, that transition must be explicit and auditable.

---

## 3. Precommitment Registry Trust State

The precommitment authority/registry is a security-relevant role.

Its authority credential should define:

- trust domain;
- accepted protocol/evidence families;
- ability to issue registration commitments;
- monotonic sequence/epoch semantics;
- validity/revocation state.

Unknown/rolled-back registry epoch fails closed according to the existing ATE trust-state model.

No global consensus system is required for the initial local architecture.

---

## 4. Cross-Document Consistency

### Qualification Architecture

Consistent. Evidence packages remain subordinate to Qualification Definitions and current Qualification Status.

### Revocation & Trust-State Model

Consistent. Evidence/precommitment authorities and receipts should use the existing monotonic current-state model; no parallel revocation semantics are needed.

### Production Requirements

Consistent. The correction strengthens deterministic evidence evaluation, authority separation, version binding, auditability, and fail-closed behavior.

### Frozen P2

No change. P2 remains a local runtime-trust experiment with its frozen simplified qualification fixture.

---

## 5. Accepted v0.1.1 Elements

No other redesign is required for:

- evidence classes;
- exact evaluator profiles;
- evaluator independence credentials;
- runner profiles;
- attempt ledgers;
- failure-class separation;
- canonical receipt sets;
- deterministic recomputation;
- hidden-corpus custody semantics;
- evaluator/runner compromise lifecycle semantics;
- claim-scope non-expansion;
- evidence admission verification;
- evidence/qualification/authorization separation.

---

## 6. Required Revision

Create **v0.1.2** adding only:

1. authoritative `PrecommitmentReceipt` issued before first subject invocation;
2. monotonic local precommitment registry/authority semantics;
3. authoritative `campaign_key` and campaign-attempt registry;
4. rollback/current-state checks for the precommitment authority/registry;
5. binding of first/all subject invocations and final receipts to the precommitted registration digest/commitment ID.

Then perform a short implementation-readiness review.

---

## 7. Final Statement

The evidence architecture is nearly ready for conformance-protocol design.

The final correction closes the distinction between:

```text
"this document says it was preregistered"
```

and:

```text
"an authoritative ordering mechanism proves this exact run definition was committed before the subject was invoked."
```

That distinction is essential if ATE evidence is meant to resist outcome-driven selection rather than merely document it after the fact.
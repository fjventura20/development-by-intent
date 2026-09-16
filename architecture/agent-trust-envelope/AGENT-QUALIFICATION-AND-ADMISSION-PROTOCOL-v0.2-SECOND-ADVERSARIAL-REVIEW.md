# Agent Qualification & Admission Protocol v0.2 — Second Adversarial Design Review

**Reviewed artifact:** `AGENT-QUALIFICATION-AND-ADMISSION-PROTOCOL-v0.2.md`  
**Reviewed commit:** `512272a8feadd2d28535b674c72a5cfa91d6bff5`  
**Review type:** second adversarial architecture/security pass  
**Disposition:** **CORRECTION REQUIRED — NO IMPLEMENTATION YET**

---

## 1. Executive Result

v0.2 successfully closes the major v0.1 defects:

- qualification/admission are mandatory signed ATE dependencies;
- current state is rechecked before execution;
- immutable SubjectBinding replaces ambiguous bare identity;
- signed credentials no longer contain mutable lifecycle fields;
- policy authoring is separated from adjudication;
- admission approvals are manifest-bound;
- downstream expiry is capped by upstream eligibility;
- the PoC now tests post-issuance revocation and unauthorized issuers;
- no live-model calls are required.

The core architecture is now substantially stronger.

This second pass found four remaining high-severity specification defects and two medium-severity ambiguities. They are narrower than the v0.1 findings, but must be corrected before freeze because they affect deterministic verification and revocation semantics.

---

## 2. Findings

### SR-1 — HIGH — Digest semantics are self-referential / undefined

Several schemas contain their own digest field, for example:

```text
SubjectBinding.binding_digest
QualificationRequirementsProfile.profile_digest
AdmissionPolicy.admission_policy_digest
```

Other artifacts refer to `qualification_credential_digest` and `admission_credential_digest`, but v0.2 does not define how those digests are computed.

Without one canonical rule, independent implementations may hash different bytes or create self-referential digest definitions.

**Required correction**

Define one protocol-wide canonical artifact digest function:

```text
artifact_digest = HASH(
    DOMAIN_SEPARATOR ||
    CANONICAL_ENCODE(artifact_without_signature_and_digest_fields)
)
```

The selected canonical encoding and hash algorithm must be versioned. All `*_digest` references in qualification/admission MUST use this rule unless another controlling ATE spec explicitly defines the same canonical equivalent.

For the PoC, use the same canonical JSON/SHA-256 profile already used by the local ATE harness where compatible.

---

### SR-2 — HIGH — TrustStateReference can represent a mixed, non-atomic state

v0.2 allows a TrustStateReference to contain both a signed snapshot digest and separate registry/policy digests. It also allows omission of redundant fields when the snapshot commits to them.

What is not yet explicit is that the referenced components must represent one coherent trust-state view. Otherwise an implementation could combine:

```text
trust-root state from epoch N
revocation state from epoch N+1
policy state from epoch N-1
```

and still populate all fields.

**Required correction**

A decision MUST bind either:

1. one authoritative signed TrustStateSnapshot that atomically commits to all controlling component digests/epochs; or
2. an equivalent transactionally consistent state bundle with a single state/version identifier.

Mixed-epoch assembly is invalid.

Add a reason code such as:

```text
QX_TRUST_STATE_INCONSISTENT
AX_TRUST_STATE_INCONSISTENT
```

---

### SR-3 — HIGH — Revocation ordering relative to the protected side effect is not precisely defined

v0.2 correctly requires a final executor recheck, but phrases such as “revocation after capability issuance prevents execution” can be interpreted as an absolute guarantee even when revocation races with an already-started external side effect.

No distributed system can guarantee that an unrelated revocation arriving after the irreversible external effect has crossed its commit point will retroactively stop that effect.

**Required correction**

Define an **Execution Authorization Point (EAP)**:

```text
EAP = the final serialized/authoritative point at which the executor
      validates current trust state and commits to performing the side effect
```

The required guarantee becomes:

> Any revocation that is effective and observable by the authoritative trust-state system before the EAP MUST prevent the protected action from crossing the EAP.

For the local PoC, the trust-state read/reservation and protected-resource mutation should be placed under one serializable local transaction or equivalent lock so the ordering is deterministic.

For external side effects, existing A3/A4 idempotency and ambiguous-effect rules remain controlling.

---

### SR-4 — HIGH — Freeze order is internally contradictory

Section 35 says cross-specification integration is required **before freeze**.

Section 37 currently gives this order:

```text
v0.2 frozen candidate
-> second adversarial review
-> corrections if any
-> freeze
-> minimal cross-spec amendments
```

That directly contradicts section 35.

**Required correction**

The order must be:

```text
frozen candidate
-> adversarial review
-> corrections
-> cross-spec amendments
-> reconciliation review
-> freeze
-> PoC implementation
```

No implementation authorization should be issued until the reconciled document set is frozen together.

---

### SR-5 — MEDIUM — SubjectBinding variance rules must be machine-evaluable

`allowed_variance[]` and `prohibited_variance[]` are useful concepts, but free-form prose would make deterministic verification impossible.

**Required correction**

State that binding variance rules must use canonical, machine-evaluable predicates. The first PoC should avoid variance entirely and use an exact deterministic SubjectBinding fixture.

---

### SR-6 — MEDIUM — The final-executor live-subject check must be implementable without giving the executor ambient participant authority

v0.2 says the executor rechecks `subject identity / live binding`. This is correct in principle but should not require the executor to trust arbitrary participant assertions or reconstruct all qualification evidence itself.

**Required correction**

Clarify that the executor may satisfy this requirement by verifying a signed/current execution capability or TrustDecision that is cryptographically bound to the live session/SubjectBinding, plus current trust-state rechecks. The executor need not independently re-run qualification evidence evaluation.

---

## 3. Second-Pass Disposition

```text
v0.1 critical architecture defects:   CLOSED
v0.2 central architecture:            ACCEPT
v0.2 deterministic digest semantics:  OPEN / HIGH
v0.2 trust-state atomicity:            OPEN / HIGH
v0.2 revocation ordering semantics:    OPEN / HIGH
v0.2 freeze sequencing:                OPEN / HIGH
v0.2 SubjectBinding variance:          OPEN / MEDIUM
v0.2 executor implementation wording:  OPEN / MEDIUM
```

No additional conceptual layer is required. These are specification-hardening corrections.

---

## 4. Required Next Artifact

Create `AGENT-QUALIFICATION-AND-ADMISSION-PROTOCOL-v0.2.1.md` as the corrected reconciliation candidate.

It must:

1. define canonical digest computation;
2. require one coherent/atomic TrustStateReference;
3. define Execution Authorization Point semantics;
4. correct the freeze order;
5. require machine-evaluable SubjectBinding variance;
6. clarify executor verification responsibilities;
7. remain **NOT FROZEN** until the dependent ATE specifications are amended and reconciled.

After v0.2.1, the next work should be the minimal cross-specification amendments in the Trust Root, Revocation, Production Architecture, Risk/Assurance, and Audit documents. Hermes is still unnecessary at this stage.

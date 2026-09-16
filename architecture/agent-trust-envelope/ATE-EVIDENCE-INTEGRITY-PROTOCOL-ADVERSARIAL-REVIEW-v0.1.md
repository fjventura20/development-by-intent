# ATE Evidence Integrity Protocol — Adversarial Review v0.1

**Status:** Adversarial protocol review  
**Date:** 2026-09-16  
**Reviewed artifact:** `ATE-EVIDENCE-INTEGRITY-LOCAL-CONFORMANCE-PROTOCOL-v0.1.md`

## Disposition

**SURGICAL_REVISION_REQUIRED_BEFORE_FREEZE**

The 14-test protocol is lean and correctly avoids live model/evaluator cost. The test set covers the intended evidence-integrity layer well.

Five fixture semantics need to be frozen more precisely so the implementation cannot satisfy tests through self-consistent but non-independent shortcuts.

---

## 1. Precommitment Authority Must Be Distinct From Runner

The architecture requires chronology outside the runner's unilateral control.

The local protocol currently names both roles but does not explicitly prohibit them from sharing the same signing key/authority fixture.

### Required correction

For this protocol freeze:

```text
PrecommitmentRegistryAuthority key != Runner key
PrecommitmentRegistryAuthority role != Runner role
```

and the precommitment registry state must be independently queried/verified by package admission.

The same test harness process MAY host both deterministic fixtures for convenience, but keys/role credentials/state namespaces must remain logically distinct.

Add a mandatory variant proving a runner-signed fake PrecommitmentReceipt is rejected even when the runner itself is otherwise authorized.

---

## 2. Campaign History Must Come From Registry, Not Aggregate Receipt

EI-T3 checks omission of prior Run A from Run B evidence, but an implementation could trust the aggregate receipt's `prior_formal_attempt_refs[]` as its only history source.

That allows omission by the evidence issuer.

### Required correction

Qualification/package admission SHALL query or verify the authoritative Campaign Registry state for the canonical campaign key and reconcile:

```text
registry formal-run history
vs
receipt-declared formal attempt history
```

Missing registry-known attempts rejects package admission.

Freeze a baseline FormalAttemptPolicy:

```text
repeat_attempts_allowed = true
all_formal_attempts_must_remain_referenced = true
new display campaign ID does not reset campaign_key history
supersession/remediation requires explicit signed policy artifact
```

EI-T3 need not decide whether a later PASS overcomes an earlier FAIL; it only proves non-erasure/history integrity.

---

## 3. Claim Scope Needs a Verifiable Structured Partial Order

The protocol currently uses `claim_scope_digest` but EI-T10 requires proving one scope is broader than another.

A digest alone cannot establish subset/superset semantics.

### Required correction

Freeze a minimal structured local scope object, e.g.:

```text
EvidenceClaimScope {
    capability_classes[]
    maximum_risk_class
    assurance_ceiling
    tool_classes[]
    network_access = NONE | BOUNDED | GENERAL
    resource_scope[]
    trust_domain_id
    project_scope
}
```

For the local protocol, define deterministic subset semantics:

```text
requested capabilities subset of evidence capabilities
requested risk <= evidence max risk
requested assurance <= evidence assurance ceiling
requested tool classes subset
requested network access <= evidence network bound
requested resource scope subset
same required trust/project scope
```

EI-T10 must exercise at least capability and risk expansion.

The digest still provides integrity; the structured object provides semantics.

---

## 4. Trust-State Verification Must Be Independent of the Receipt Being Tested

EI-T11 should not let the evidence receipt carry the authoritative statement that it is not revoked.

### Required correction

Freeze a separate local TrustStateAuthority fixture with:

```text
trust_state_epoch
revocation records
issuer/evaluator current-status records when controlling
```

Package admission reads/verifies this state independently.

Add a variant where the receipt claims an older clean epoch while current authoritative state contains revocation.

Expected: REJECTED.

---

## 5. Role Credentials Must Be Independent Inputs

Several tests depend on authority ceilings.

An implementation must not infer roles from which helper function produced an artifact.

### Required correction

Every fixture authority SHALL have a signed/immutable RoleCredential or frozen equivalent stating allowed artifact/operation classes.

At minimum include:

- Protocol Authority;
- Precommitment Registry Authority;
- Runner;
- synthetic Evaluator;
- Evidence Issuer;
- Qualification/Package Admission Authority;
- Trust-State Authority.

Verifier evaluates role credentials, not hard-coded object provenance assumptions.

---

## 6. Accepted Test Set

No new controlling test IDs are required.

The corrections fit inside existing tests:

- EI-T1/T2: distinct precommitment role + runner fake receipt;
- EI-T3: authoritative campaign registry reconciliation;
- EI-T7/T8: explicit role credentials;
- EI-T10: structured scope partial-order test;
- EI-T11: independent current trust-state authority.

All other tests are accepted unchanged.

---

## 7. Non-Issues / Accepted Boundaries

The following are acceptable for this lean protocol:

- deterministic functional baseline only;
- no live AI generation;
- synthetic evaluator fixtures for role tests;
- no decision on whether a later pass remediates an earlier fail;
- local trusted clock;
- software-held fixture keys;
- single-host deterministic implementation;
- no TPM/transparency-log requirement;
- no full qualification issuance test.

---

## 8. Required v0.1.1 Protocol Revision

Create v0.1.1 preserving exactly 14 controlling tests while freezing:

1. distinct runner and precommitment authority keys/roles;
2. authoritative Campaign Registry reconciliation and baseline formal-attempt policy;
3. structured `EvidenceClaimScope` and deterministic subset semantics;
4. independent TrustStateAuthority/current epoch;
5. explicit RoleCredentials for all controlling authorities.

Then perform a short final freeze review.

---

## 9. Final Statement

The protocol should prove that evidence validity emerges from **independent cross-checks between separately authoritative objects**, not from one internally self-consistent evidence package saying all the right things about itself.

With these fixture semantics frozen, the 14-test protocol is appropriate for local deterministic implementation and formal evidence.
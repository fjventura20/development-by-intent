# ATE Agent Qualification & Requalification Adversarial Review v0.1

**Status:** Adversarial architecture review  
**Date:** 2026-09-16  
**Reviewed artifact:** `ATE-AGENT-QUALIFICATION-REQUALIFICATION-ARCHITECTURE-v0.1.md`

---

## 1. Review Disposition

**REVISION_REQUIRED_BEFORE_PROTOCOL_DESIGN**

The v0.1 architecture has the correct structure and should be preserved. It successfully separates qualification from authorization, binds qualification to a qualified runtime profile, introduces explicit re-attestation/partial/full requalification semantics, and treats qualification as scoped and finite rather than general reputation.

However, eight issues should be corrected before the qualification model is used as a controlling input to P2 or frozen into a future experiment.

---

## 2. Finding QAR-1 — Qualification Status Can Roll Back Without an Authoritative Monotonic State

### Attack

An attacker presents an older but correctly signed `ACTIVE` qualification credential after a later suspension, revocation, supersession, or policy change.

The current design says the verifier checks current status, but it does not define the authoritative status object or monotonicity rule strongly enough.

### Required correction

Define a `QualificationStatusState` or equivalent authoritative trust-state object containing at least:

```text
qualification_id
status
status_epoch
trust_domain_id
updated_at
reason_code
superseding_qualification_id?
status_authority_id
signature
```

Verifier MUST reject rollback to an older known `status_epoch`.

A signed historical qualification credential is insufficient without current status.

---

## 3. Finding QAR-2 — Qualification Lifetime Can Outlive Its Controlling Evidence

### Attack

A qualification is issued for 90 days using behavioral evidence valid for 7 days. On day 30 the qualification credential is still cryptographically valid even though the evidence basis is stale.

### Required correction

Qualification Definition must classify each controlling evidence class as either:

```text
ISSUANCE_SNAPSHOT
CONTINUOUSLY_CURRENT
PERIODICALLY_REFRESHED
```

For `CONTINUOUSLY_CURRENT` evidence, qualification validity MUST NOT exceed the controlling evidence validity.

For `PERIODICALLY_REFRESHED`, the qualification becomes suspended or requalification-required when refresh deadline is missed.

`ISSUANCE_SNAPSHOT` evidence may remain historically valid as the basis for issuance even after its own collection timestamp ages, but the Qualification Definition must explicitly permit that semantic.

No implicit evidence-lifetime behavior.

---

## 4. Finding QAR-3 — Compatibility Declarations Can Become Qualification Laundering

### Attack

A broad compatibility declaration permits a materially changed runtime profile to inherit an old qualification without rerunning the evaluations that made the old qualification meaningful.

### Required correction

Compatibility declarations MUST NOT silently increase any of:

```text
capability scope
risk ceiling
assurance tier
trust domain/project scope
resource permission scope
network/tool authority
governance latitude
```

A compatibility declaration must bind:

- exact source qualification/profile;
- exact target profile or tightly bounded change predicate;
- qualification class;
- preserved evidence classes;
- invalidated evidence classes;
- mandatory delta evaluations;
- maximum risk ceiling preserved;
- maximum capability scope preserved;
- validity;
- compatibility-policy epoch.

Any expansion requires a new qualification decision at the expanded scope.

---

## 5. Finding QAR-4 — Partial Requalification Can Reuse Evidence Without Proving Continued Applicability

### Attack

A partial requalification carries forward old evidence receipts merely because they are listed as preserved, even though the changed runtime dimension may affect those tests indirectly.

### Required correction

Every preserved evidence class in partial requalification must be justified by a signed dependency/compatibility decision.

The decision must state why the changed dimensions do not invalidate the preserved evidence.

The Qualification Authority must bind that compatibility decision into the new Qualification Decision Record.

Preservation by omission is prohibited.

---

## 6. Finding QAR-5 — Qualification Authority Is Too Broad Without Issuance Ceilings

### Attack

A valid Qualification Authority key authorized for a low-risk reviewer qualification is used to issue a high-risk production-deployer qualification.

### Required correction

Qualification issuer authority must have explicit ceilings:

```text
may_issue_qualification_classes[]
maximum_risk_class
maximum_assurance_tier
permitted_trust_domains[]
permitted_project_scopes[]
permitted_capability_classes[]
maximum_validity
may_issue_compatibility_declarations
may_suspend
may_revoke
```

A valid signature from a trusted qualification issuer is not sufficient unless the issuer is authorized for that exact qualification class/scope.

---

## 7. Finding QAR-6 — Evaluator Independence Is Advisory Where It Must Sometimes Be Normative

### Attack

The subject agent or an evaluator controlled by the same authority generates the only evidence used for a high-risk qualification.

### Required correction

Qualification Definition must explicitly identify, per controlling evidence class:

```text
evaluator_role
accepted_evaluator_authorities
independence_class
self_evaluation_allowed
minimum_independent_evaluators
replication_required
```

At elevated assurance/risk classes, the architecture should require independent evidence where policy specifies it.

The architecture need not mandate dual evaluation universally; it must make independence machine-verifiable rather than prose-only.

---

## 8. Finding QAR-7 — Requalification Policy Itself Can Be Downgraded

### Attack

A subject presents an old signed Requalification Policy under which a material software/model change required only re-attestation, bypassing a newer policy requiring full requalification.

### Required correction

Qualification and requalification decisions must bind:

```text
requalification_policy_id
requalification_policy_version
requalification_policy_digest
policy_epoch
```

Verifier/Qualification Authority must reject rollback below the current authoritative policy epoch.

Compatibility declarations also bind this epoch.

---

## 9. Finding QAR-8 — Credential Copying Must Be Explicitly Harmless, Not Accidentally Prevented

### Observation

A qualification credential is public/verifiable evidence. It should not be treated like a bearer secret.

### Attack

Another principal copies a valid qualification credential and attempts to use it as its own qualification.

### Required correction

State explicitly:

> Qualification credential copying is not itself a security failure. Qualification security depends on exact subject/profile/context binding and current runtime verification, not secrecy of the credential.

Verifier must bind:

```text
QualificationCredential.subject_principal_id
QualifiedRuntimeProfile principal/profile identity
VerifiedRuntimeContext principal/profile identity
```

and reject mismatch.

This avoids designing unnecessary secret handling around qualification evidence while preventing cross-subject reuse.

---

## 10. Additional Hardening Findings

### 10.1 `valid_until` and `requalification_due_at`

Require:

```text
valid_until <= requalification_due_at
```

unless the fields are deliberately defined differently. Prefer one controlling deadline plus optional earlier refresh deadlines to avoid contradictory semantics.

### 10.2 Cross-project reuse

Qualification scope must bind project/trust domain or explicitly declare portability. No inference from identical role names.

### 10.3 Governance acceptance

Qualification may bind the governance profile under which evaluation occurred, but current runtime/session governance acceptance should remain separately verified at trust-establishment/authorization time where required. Qualification must not be mistaken for permanent CoA acceptance.

### 10.4 Model/provider uncertainty

For remote provider models where exact model identity cannot be independently measured, qualification must record the actual assurance class and must not present self-reported provider/model identity as stronger provenance.

### 10.5 Hidden waivers

The v0.1 signed-waiver requirement is accepted. Waivers should additionally be prohibited from increasing qualification issuer ceilings.

---

## 11. Accepted Architecture From v0.1

The following concepts are accepted and should not be reopened absent new evidence:

1. qualification is separate from action authorization;
2. qualification is scoped to role/capability/risk/profile/governance/time;
3. qualified runtime profile is immutable/content-addressable;
4. qualification credential references an evidence package;
5. restart/profile-preserving renewal normally requires re-attestation, not full requalification;
6. material runtime/model/capability/governance changes trigger deterministic requalification policy;
7. unknown material changes fail safe;
8. capability expansion is material;
9. qualification has finite validity;
10. suspension, revocation, expiry, and supersession are distinct states;
11. requalification preserves lineage;
12. qualification is evidence-backed admission, not a generalized trust score.

---

## 12. Required v0.1.1 Corrections

A surgical v0.1.1 should add:

1. authoritative monotonic qualification status state;
2. explicit evidence-lifecycle classes;
3. compatibility non-expansion constraints;
4. evidence-preservation dependency justification for partial requalification;
5. qualification-issuer ceilings;
6. machine-verifiable evaluator independence requirements;
7. requalification-policy version/digest/epoch rollback protection;
8. explicit public-evidence/copy-safe credential semantics;
9. deadline consistency;
10. current-session governance acceptance separation.

No experiment should be authorized before these corrections are integrated.

---

## 13. Final Review Statement

The v0.1 model correctly answers the first-order question:

> What does it mean for an AI agent to be qualified for a professional role?

The remaining corrections answer the second-order security question:

> How do we prevent a once-valid qualification from being stretched, copied, downgraded, or carried forward beyond the exact evidence and scope that justified it?

Once those controls are explicit, ATE qualification can become a reliable upstream input to runtime trust establishment and bounded authorization.
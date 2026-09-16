# Agent Qualification & Admission Protocol v0.1 — Adversarial Design Review

**Reviewed artifact:** `AGENT-QUALIFICATION-AND-ADMISSION-PROTOCOL-v0.1.md`  
**Reviewed commit:** `b2529853cb371402a6626398c9c7e05b98b9e41b`  
**Review type:** adversarial architecture/security review  
**Disposition:** **CORRECTION REQUIRED — DO NOT IMPLEMENT v0.1 AS WRITTEN**  
**Implementation authorization:** NONE

---

## 1. Executive Result

The v0.1 design gets the central architecture right:

```text
qualification != admission != action authorization
```

It correctly treats qualification as role eligibility, admission as trust-domain participation, and ATE as action-specific authorization and enforcement. It also correctly preserves fresh session-bound Condition of Agency acceptance and current Value Architecture checks.

However, v0.1 is not yet safe to freeze. The review found several paths by which a historically valid qualification/admission result could become detached from the exact subject, policy, approvals, current trust state, or execution-time state that justified it.

The most serious defect is a time-of-check/time-of-use gap: v0.1 requires qualification/admission checks at capability issuance, but makes explicit qualification/admission binding into the ATE path only a future `SHOULD`. That permits an already-issued capability or TrustDecision to outlive a later qualification/admission invalidation unless every downstream verifier happens to reconstruct that dependency correctly.

The corrected design must make qualification and admission **first-class signed dependencies of authorization, trust decision, and final execution**, not advisory upstream context.

---

## 2. What v0.1 Gets Right

The following design choices should be preserved:

1. Qualification is role-specific.
2. Admission is trust-domain-specific.
3. Neither credential grants direct resource authority.
4. Standing credentials do not replace session-bound COA acceptance.
5. Qualification/admission use signed, versioned policy inputs.
6. Evidence is digest-bound against post-evaluation substitution.
7. Unknown/suspended/revoked/expired state fails closed.
8. Qualification and admission are separate state machines.
9. Admission depends on qualification.
10. Risk ceilings narrow, rather than widen, downstream authority.
11. The first PoC is local, deterministic, and intentionally small.
12. Direct resource bypass remains an automatic enforcement failure.

These are sound foundations.

---

## 3. Findings

### AR-1 — CRITICAL — Qualification/admission are not mandatory execution-time dependencies

**Problem**

Section 20.1 requires current qualification and admission before CapabilityToken issuance, but section 20.2 says explicit `qualification_credential_id` and `admission_credential_id` fields are only a future `SHOULD`. A prototype may place them in token constraints, but the protocol does not require the complete dependency chain to survive through TrustDecision and executor validation.

This creates a TOCTOU path:

```text
T0 qualification ACTIVE
T1 admission ACTIVE
T2 CapabilityToken issued
T3 admission REVOKED
T4 previously issued token presented
T5 execution path does not explicitly re-evaluate the admission dependency
```

If T5 relies only on token validity, execution can occur after eligibility was withdrawn.

**Required correction**

For every governed action whose policy requires qualification/admission:

- CapabilityToken MUST bind exact qualification and admission credential IDs and digests.
- TrustDecision MUST bind the same dependency IDs/digests.
- The ATE verifier MUST check their current trust state.
- The Capability Executor MUST perform a final current-state/revocation recheck immediately before protected execution.
- Downstream expiration MUST be capped by the earliest controlling dependency expiration.

No unsigned side-channel eligibility flag is acceptable.

---

### AR-2 — HIGH — `subject_identity` is underspecified

**Problem**

The draft repeatedly uses `subject_identity`, but does not define whether this is a display name, agent identity, signing key, provider/model tuple, runtime instance, or composite identity. A copied credential can be rejected only if the verifier has an unambiguous immutable binding predicate.

**Required correction**

Introduce a canonical signed `SubjectBinding` structure with an immutable digest. At minimum it should declare:

```text
subject_binding_id
subject_identity_id
identity_key_id or equivalent immutable identity anchor
binding_level
controlling runtime/provenance constraints
allowed variance
binding_digest
```

QualificationCredential and AdmissionCredential MUST bind the same `subject_binding_digest`. Live session identity must prove satisfaction of that binding before authorization.

---

### AR-3 — HIGH — Mutable lifecycle fields are embedded in immutable signed credentials

**Problem**

`QualificationCredential` and `AdmissionCredential` include fields such as:

```text
status
revocation_reference
```

A signed credential is immutable. Its post-issuance lifecycle state cannot safely be updated in place without issuing a new signed artifact. Treating `status` as if it changes inside the credential conflicts with the existing Revocation & Trust-State Model.

**Required correction**

Credentials should be immutable issuance records. Remove mutable lifecycle fields from the credential schema. Current state MUST be derived from:

- validity interval,
- current trust-state/revocation registry,
- active policy/profile state,
- dependency state.

Historical credentials remain unchanged for audit.

---

### AR-4 — HIGH — Rule-making and adjudication authority are not separated strongly enough

**Problem**

The draft introduces R11 Qualification Authority and R12 Admission Authority, but does not explicitly forbid those authorities from also authoring the requirement profile or admission policy they apply. If the evaluator can silently rewrite the rules, separation between policy and decision collapses.

**Required correction**

- `QualificationRequirementsProfile` MUST be signed by an authorized Policy Authority (or a separately defined qualification-policy authority), not by the candidate and not implicitly by R11.
- `AdmissionPolicy` MUST be signed by the trust-domain Policy Authority (or delegated domain-policy authority), not implicitly by R12.
- R11 evaluates evidence and issues qualification decisions/credentials.
- R12 evaluates admission inputs and issues admission decisions/credentials.
- At A2+ assurance, policy-authoring and adjudication authority MUST be distinct unless an explicit higher-level exception policy authorizes concentration.

---

### AR-5 — HIGH — Admission approvals are required by policy but not cryptographically bound to the decision

**Problem**

`AdmissionPolicy` may require human or authority approvals, but `AdmissionDecision` does not bind the exact approval artifacts used. This leaves the decision unable to prove which approvals justified admission.

**Required correction**

Add an `AdmissionEvidenceManifest` (or equivalent signed input manifest) containing:

- qualification credential ID/digest,
- required approval artifact IDs/digests,
- trust-domain membership evidence where required,
- relevant incident/suspension state references,
- admission-policy digest,
- manifest digest.

`AdmissionDecision` MUST bind this manifest digest.

---

### AR-6 — HIGH — Evidence-item validation requirements are implicit, not explicit

**Problem**

The Qualification Evidence Manifest records evidence items, but v0.1 does not state strongly enough that every evidence artifact must itself pass artifact-class, signature, issuer authorization, trust-state, freshness, and context checks before contributing to qualification.

A digest proves immutability, not truth or authority.

**Required correction**

Every required evidence item MUST be validated for:

```text
schema/artifact class
cryptographic integrity
issuer authorized for artifact type
issuer/key current
artifact current/not revoked
freshness
subject/context binding
trust-domain recognition where applicable
```

The QualificationDecision MUST bind the evaluated evidence manifest and the trust-state snapshot/epoch under which those checks were made.

---

### AR-7 — HIGH — Decisions do not bind the trust-state snapshot that made them valid

**Problem**

QualificationDecision and AdmissionDecision include evaluation timestamps but not the controlling Trust Root Registry digest, revocation epoch, or TrustStateSnapshot digest. Audit cannot deterministically reconstruct which current-state view was consulted.

**Required correction**

Both decision artifacts MUST bind either:

```text
trust_state_snapshot_digest
```

or a complete equivalent set including at least:

```text
trust_root_registry_digest
revocation_registry_digest
revocation_registry_epoch
active_policy_manifest_digest
```

The audit record should preserve the same references.

---

### AR-8 — HIGH — Downstream validity can outlive upstream eligibility

**Problem**

The draft says admission cannot outlive usable qualification, but does not define a mandatory derived expiration rule for downstream CapabilityTokens and TrustDecisions.

**Required correction**

For actions requiring qualification/admission:

```text
max_downstream_expiry = min(
  qualification.expires_at,
  admission.expires_at,
  capability policy limit,
  session/evidence limits,
  other controlling dependency expirations
)
```

A CapabilityToken or TrustDecision MUST NOT remain usable beyond the earliest controlling dependency expiration.

---

### AR-9 — MEDIUM — `allowed_capability_classes` invites ambient-authority interpretation

**Problem**

The text correctly says the fields are ceilings only, but the name `allowed_capability_classes` is easy for implementations to interpret as authorization.

**Required correction**

Rename qualification/admission fields to terms such as:

```text
eligible_capability_classes
maximum_eligible_risk_level
maximum_admitted_risk_level
```

Explicitly define the effective eligibility ceiling as intersection-only and require a separate least-privilege CapabilityToken for every protected action.

---

### AR-10 — MEDIUM — Separation of duties is not assurance-specific enough

**Problem**

The draft permits multiple authorities to coexist on one host/process for low-risk prototypes, but does not state the minimum separation required as assurance increases.

**Required correction**

Tie qualification/admission authority separation to the existing Risk & Assurance Policy Model:

- A0/A1: logical role separation may be sufficient when policy allows.
- A2: candidate must not possess or directly invoke policy/qualification/admission signing keys; distinct signing identities and protected services are required.
- A3/A4: stronger process/service/key-custody separation applies according to the existing assurance model.

The PoC may remain one host, but candidate and authorities should be distinct OS/security identities with distinct keys.

---

### AR-11 — HIGH — The PoC test matrix misses the most important TOCTOU failure

**Problem**

QA-P3 tests admission revocation followed by a new capability issuance or ATE validation. It does not explicitly test a capability already issued before revocation and presented after revocation.

That is the precise execution-time failure the architecture must prevent.

**Required correction**

Add deterministic cases for:

1. capability issued while qualified/admitted, then admission revoked before execution -> DENY;
2. capability issued while qualified/admitted, then qualification revoked before execution -> DENY;
3. qualification expires after capability issuance but before execution -> DENY;
4. valid cryptographic signature from an issuer not authorized for QualificationCredential -> DENY;
5. direct protected-resource bypass -> DENY / enforcement failure.

These can use synthetic subjects and deterministic key fixtures; no live LLM calls are required.

---

### AR-12 — MEDIUM — R11/R12 are not yet recognized by the trust-root and revocation specifications

**Problem**

The draft correctly notes that R11/R12 are provisional. The existing Trust Root & Key Custody Model defines R1-R10 only, and the existing Revocation & Trust-State Model does not yet define qualification/admission credential targets or revocation authority semantics.

**Required correction**

Before implementation freeze:

- register R11 Qualification Authority and R12 Admission Authority in the trust-root model;
- define permitted artifact types and key-domain separators;
- add qualification/admission credential and authority-key targets to the revocation model;
- define who may suspend/revoke/reinstate those artifacts;
- add the new artifact classes to the audit model and ATE production dependency graph.

---

## 4. Decisions on the v0.1 Review Questions

### Q1 — Is qualification sufficiently distinct from action authorization?

**Yes conceptually, but not yet mechanically.** v0.2 must make the distinction enforceable by mandatory signed dependency binding.

### Q2 — Can AdmissionCredential become ambient authority?

**Yes if implementers treat its capability-class fields as permission.** Rename them as eligibility ceilings and require explicit downstream CapabilityToken authorization.

### Q3 — Is subject binding strong enough?

**No.** `subject_identity` alone is underspecified. Add a canonical immutable `SubjectBinding` and bind its digest through qualification, admission, capability, trust decision, and live-session proof.

### Q4 — Should Qualification Authority and Admission Authority remain separate roles?

**Yes.** Keep separate logical roles R11 and R12. They may share infrastructure only where the assurance profile permits, but their artifact permissions and signing domains must remain distinct.

### Q5 — When should AdmissionCredential become an explicit ATE dependency?

**Now.** It should not wait for a later schema generation. Any prototype extension mechanism must be signed and mandatory, and the production schema should add first-class fields.

### Q6 — Which evidence may be long-lived?

Long-lived evidence may support role qualification only when the profile allows it. Session identity, session-bound COA, action-specific authorization, and risk-required fresh evidence remain action-time inputs. A qualification credential can never substitute for evidence whose assurance policy requires greater freshness.

### Q7 — Which requalification triggers are mandatory?

At minimum: expiration, material subject-binding change, controlling profile hard supersession, material runtime/security-boundary change when binding-relevant, invalidated required evidence, authority compromise affecting the credential, and operator/security-incident suspension requiring requalification.

### Q8 — What if provider/model provenance is only partially verifiable?

The credential must state only the verified binding claim. Missing provenance cannot be upgraded by inference. If the role profile requires stronger provenance than can be verified, qualification is denied.

### Q9 — Does invalidation propagate fast enough?

Not in v0.1. v0.2 must require current-state checks at authorization, trust decision, and final execution plus downstream expiry capping.

### Q10 — Can any path reach the resource after qualification/admission failure?

The intended architecture says no, but v0.1 does not yet close the already-issued-capability path. AR-1/AR-8/AR-11 are mandatory corrections.

---

## 5. Required v0.2 Corrections

A corrected frozen candidate should, at minimum:

1. define canonical `SubjectBinding`;
2. bind its digest into qualification and admission;
3. remove mutable status fields from signed credentials;
4. define Policy Authority ownership of requirements/admission policy;
5. add `AdmissionEvidenceManifest`;
6. require validation of every evidence artifact and issuer;
7. bind trust-state snapshot/epoch into decisions;
8. make qualification/admission IDs and digests mandatory ATE dependencies;
9. require final executor current-state recheck;
10. cap downstream expiry by earliest dependency expiry;
11. rename capability fields as eligibility ceilings;
12. tie separation of duties to A0-A4 assurance;
13. expand the PoC with deterministic TOCTOU and unauthorized-issuer cases;
14. state explicitly that the first PoC uses synthetic subjects and requires no live-model calls;
15. require trust-root/revocation/audit integration before implementation freeze.

---

## 6. Review Disposition

```text
CENTRAL ARCHITECTURE:        ACCEPT
v0.1 FREEZE:                 REJECT
IMPLEMENTATION OF v0.1:      NOT AUTHORIZED
CORRECTION TO v0.2:          REQUIRED
SECOND ADVERSARIAL PASS:     REQUIRED BEFORE FREEZE
HERMES IMPLEMENTATION TASK:  NOT YET AUTHORIZED
```

The next artifact should be a corrected **Agent Qualification & Admission Protocol v0.2 frozen candidate**, followed by one more adversarial review before implementation authorization.

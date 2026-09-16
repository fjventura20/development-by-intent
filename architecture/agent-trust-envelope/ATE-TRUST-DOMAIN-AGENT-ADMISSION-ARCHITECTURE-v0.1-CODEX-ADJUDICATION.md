# ATE Trust-Domain Agent Admission Architecture v0.1 — Codex Review Adjudication

**Status:** REVIEW ADJUDICATION — DESIGN ONLY — NO IMPLEMENTATION AUTHORIZATION  
**Date:** 2026-09-16  
**Reviewed artifact:** `ATE-TRUST-DOMAIN-AGENT-ADMISSION-ARCHITECTURE-v0.1.md`  
**Codex review:** `ATE-TRUST-DOMAIN-AGENT-ADMISSION-ARCHITECTURE-v0.1-CODEX-ADVERSARIAL-REVIEW.md`  
**Codex review commit:** `4318d52ac34638235573dcacc7bfb4e6ea272c69`  
**Codex disposition:** `NOT_READY_FOR_FREEZE`

---

## 1. Executive disposition

The Codex disposition is accepted.

The v0.1 architecture remains **NOT READY FOR FREEZE**. The three HIGH findings are valid and freeze-blocking, but they are bounded defects in cross-artifact provenance, qualification-replacement handling, and lifecycle completeness. They do not require another architectural restart.

Correction strategy:

1. require a signed capability-issuance binding to the exact qualification/admission pair and its controlling dependency manifest;
2. remove `AdmissionContinuation` from the first architecture version and require a fresh Admission Decision whenever the controlling qualification changes;
3. require explicit lifecycle/change semantics for every admission-specific controlling dependency;
4. clarify v0.1.1 as strictly local-domain only;
5. retain the optional Admission Credential only as a compact portable presentation of a retained signed Admission Decision, not as a second independent authority decision.

The corrected artifact should be:

`ATE-TRUST-DOMAIN-AGENT-ADMISSION-ARCHITECTURE-v0.1.1.md`

It remains DESIGN ONLY and requires a focused adversarial consistency review before freeze.

---

## 2. Finding adjudication

### TDA-AR-01 — Capability issuance lacks mandatory signed binding to controlling qualification/admission pair

**Disposition: ACCEPT**

The existing draft verifies a current pair at capability issuance and another current pair at composition, but does not cryptographically require those pairs to be the same pair. This permits an old token issued under withdrawn admission A1 to be recomposed under a later admission A2 with equivalent ceilings.

**Correction:** define a canonical `CapabilityAdmissionBinding` that binds the exact qualification context, exact admission context, exact admission dependency manifest, policy epochs, authorization instance, and validity. Its digest MUST be included in the signed CapabilityToken or a mandatory signed extension. Composition requires exact equality between the token's issuance binding and the pair selected for trust composition. Substitution requires a new capability authorization. The binding digest is carried into `CapabilityDecisionContext`, `DecisionSemanticContext`, `TrustDecisionInput`, `TrustDecision`, audit, and executor rechecks.

### TDA-AR-02 — AdmissionContinuation lacks deterministic normalization/downstream identity

**Disposition: ACCEPT — resolve by deletion, not expansion**

`AdmissionContinuation` creates unnecessary semantic complexity for the first admission architecture. A qualification replacement already represents a material prerequisite change and can be handled safely by a fresh admission decision.

**Correction:** remove `AdmissionContinuation`, `may_issue_continuation`, and all continuation paths from v0.1.1. Qualification Q1 being replaced/superseded makes an admission bound to Q1 unusable. If Q2 becomes the new current qualification, the domain performs a new Admission Decision and, if used, issues a new Admission Credential. No pending token or TrustDecision may switch from Q1/A1 to Q2/A2 in place.

### TDA-AR-03 — Admission-specific dependencies lack mandatory lifecycle declarations

**Disposition: ACCEPT**

The draft inherits qualification lifecycle semantics, but admission introduces additional local approvals, participation conditions, structural-control receipts, authority delegations, and policy dependencies. Their continuing meaning cannot be implicit.

**Correction:** every controlling admission dependency MUST be represented in an `AdmissionDependencyManifest` with explicit lifecycle/change semantics. At minimum it declares dependency identity/digest, authoritative state owner, lifecycle class, decision-time stability class, validity/refresh deadline, compatibility predicate where relevant, whether change invalidates unexecuted grants, and whether executor recheck is required. Missing or unsupported classification makes the policy/context invalid and fails closed. Snapshot treatment must be explicit and policy-authorized.

---

## 3. Non-blocking findings

### TDA-AR-04 — Local-only/federation wording

**Disposition: ACCEPT**

v0.1.1 will be unambiguously local-domain only. Foreign qualification/admission is unusable under this architecture. Federation remains governed by the existing separate federation architecture and requires a future explicitly composed profile.

### TDA-AR-05 — Separate Admission Decision and Admission Credential

**Disposition: MODIFY**

A distinct Admission Decision is required. A separate Admission Credential is not always required.

v0.1.1 will define the credential as an optional compact portable presentation whose authority derives only from a retained signed Admission Decision and current Admission Status. A deployment may use the retained signed Admission Decision directly as the admission presentation if it exposes the same required bindings. If a credential is emitted, it references the decision digest and may only equal or narrow it.

---

## 4. Freeze decision

`ATE-TRUST-DOMAIN-AGENT-ADMISSION-ARCHITECTURE-v0.1.md` remains historical and unchanged.

The next architecture candidate is v0.1.1. Freeze remains withheld until a focused adversarial consistency review verifies that:

- token issuance is cryptographically bound to the exact qualification/admission pair;
- qualification replacement requires new admission and new capability authorization where applicable;
- every admission-specific controlling dependency has explicit lifecycle/change semantics;
- executor recheck closes all execution-invalidating dependencies;
- no correction weakens the existing qualification, composition, revocation, audit, or enforcement baseline.

No implementation or conformance experiment is authorized by this adjudication.
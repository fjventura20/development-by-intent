# ATE Trust-Decision Composition Inspection v0.1

**Status:** Architectural inspection — DESIGN ONLY  
**Date:** 2026-09-16  
**Program:** Agent Trust Envelope (ATE)  
**Branch:** `feature/ate-architecture-sync-2026-09-16`

---

## 1. Purpose

Inspect the existing ATE repository for the trust-decision composition layer: how current runtime identity, qualification, governance coverage, risk/assurance, capability scope, revocation/current trust state, and requested-action identity combine into one deterministic `TRUST_GRANTED` / `TRUST_DENIED` decision.

This inspection does not modify existing architecture semantics. It identifies what already exists, what later artifacts have superseded conceptually, and what remains uncomposed.

---

## 2. Executive Finding

ATE already contains a real trust-decision layer, primarily in:

- `ATE-PRODUCTION-ARCHITECTURE-v0.1.md`
- `ATE-REFERENCE-ARCHITECTURE-COMPONENT-INTERACTION-MODEL-v0.1.md`
- `ATE-PRODUCTION-REQUIREMENTS-CONFORMANCE-PROFILE-v0.1.md`
- `ATE-RISK-ASSURANCE-POLICY-MODEL-v0.1.md`
- `ATE-REVOCATION-TRUST-STATE-MODEL-v0.1.md`

Those artifacts establish the core decision semantics:

- canonical requested action;
- fail-closed verification;
- deterministic gate evaluation;
- risk classification and minimum assurance;
- capability-scope containment;
- current revocation/policy checks;
- signed `TRUST_GRANTED` / `TRUST_DENIED` output;
- action-specific, time-bounded, replay-resistant execution.

However, the composition layer now lags behind newer ATE architecture.

Later artifacts introduced stronger inputs that are not yet formally incorporated into the canonical `TrustDecision` composition:

- `VerifiedRuntimeContext` from runtime identity/attestation architecture;
- current qualification credential + authoritative qualification status;
- bounded governance coverage manifests and current governance dependencies;
- richer behavioral/functional evidence packages and integrity rules;
- qualification risk/capability/assurance ceilings;
- governance-derived structural-control requirements;
- newer monotonic current-state semantics.

Therefore:

> **ATE has a trust-decision architecture, but it does not yet have one current canonical decision-input object that composes all of the newest trust layers.**

The missing artifact is not a new trust concept. It is a reconciliation/composition specification.

---

## 3. Existing Decision Core

### 3.1 Production Architecture

`ATE-PRODUCTION-ARCHITECTURE-v0.1.md` already defines:

```text
ATE Verifier
    -> deterministic verification gates
    -> Trust Decision Authority
    -> TRUST_GRANTED | TRUST_DENIED
    -> Capability Executor
```

It defines a `TrustDecision` binding:

- envelope identity/binding hash;
- subject/session;
- requested-action digest;
- policy;
- COA acceptance;
- behavioral evidence receipt;
- capability token;
- nonce;
- issuance/expiry;
- verdict/reason;
- authority signature.

It also defines conceptual `evaluate(envelope)` pseudocode and explicit fail-closed behavior.

### 3.2 Reference Architecture

`ATE-REFERENCE-ARCHITECTURE-COMPONENT-INTERACTION-MODEL-v0.1.md` extends the decision flow with:

- canonical Request Gateway;
- risk classification R0–R4;
- assurance profiles A0–A4;
- trust-root/policy/revocation/federation epochs;
- executor reverification;
- nonce reservation;
- audit transitions.

Its gate order already includes:

```text
G0  current trust / revocation
G1  trust-root authority
G2  runtime/session provenance
G3  COA acceptance
G4  active VA policy
G5  behavioral evidence
G6  capability scope
G7  artifact binding
G8  freshness
G9  nonce/replay
G10 action canonicalization
G11 risk/assurance
G12 federation if applicable
```

This is the strongest existing direct composition artifact.

### 3.3 Production Requirements

`ATE-PRODUCTION-REQUIREMENTS-CONFORMANCE-PROFILE-v0.1.md` supplies normative decision requirements including:

- deterministic result for equivalent canonical inputs;
- only `TRUST_GRANTED` / `TRUST_DENIED` executable outcomes;
- missing/invalid/expired/revoked/unsupported evidence cannot grant;
- current policy and COA requirements;
- exact action binding;
- signed TrustDecision;
- current revocation state;
- executor-mediated enforcement.

### 3.4 Risk & Assurance

`ATE-RISK-ASSURANCE-POLICY-MODEL-v0.1.md` makes the requested action's authoritative risk classification determine the minimum assurance profile:

```text
R0 -> A0
R1 -> A1
R2 -> A2
R3 -> A3
R4 -> A4
```

The participant cannot choose or downgrade its own risk class.

Higher assurance changes evidence freshness, authority independence, human approval, key custody, executor isolation, revocation freshness, and audit requirements.

### 3.5 Revocation / Current State

`ATE-REVOCATION-TRUST-STATE-MODEL-v0.1.md` establishes the important distinction:

```text
historically valid != usable now
```

Current use requires cryptographic validity, authorized issuer, temporal validity, current policy, non-revocation, and valid context binding.

This provides the correct current-state semantics for trust-decision inputs.

---

## 4. Newer Inputs Not Yet Fully Composed

## 4.1 VerifiedRuntimeContext

Runtime identity/attestation architecture introduced a canonical `VerifiedRuntimeContext` containing or binding:

- trust domain;
- principal ID;
- runtime instance ID;
- runtime public key;
- software/configuration identity;
- qualification identity;
- CoA/VA/policy digests;
- assurance tier;
- attestation freshness;
- identity validity;
- policy epoch;
- verification decision ID.

The architecture explicitly states that operational authorization should bind to this verified context.

The older `TrustDecision` still uses generic subject/session/runtime fields instead of binding one canonical `VerifiedRuntimeContext` digest.

**Gap:** runtime verification output is not yet a mandatory canonical decision input.

---

## 4.2 Qualification

`ATE-AGENT-QUALIFICATION-REQUALIFICATION-ARCHITECTURE-v0.1.1.md` introduced current qualification semantics:

- exact qualified profile digest;
- qualification class;
- capability classes;
- maximum risk class;
- assurance ceiling/floor semantics;
- trust/project scope;
- qualification validity;
- evidence-package digest;
- current status: `ACTIVE`, `SUSPENDED`, `REQUALIFICATION_REQUIRED`, `EXPIRED`, `SUPERSEDED`, `REVOKED`, etc.;
- monotonic qualification-status epoch;
- current requalification-policy epoch.

Only current `ACTIVE` qualification may normally contribute to a new trust-dependent authorization.

The existing `TrustDecision` schema has no qualification fields.

**Gap:** there is no mandatory rule equivalent to:

```text
qualification.status == ACTIVE
AND requested capability within qualification scope
AND requested risk <= qualification maximum risk
AND required assurance <= qualified assurance capability
AND VerifiedRuntimeContext profile == qualification profile
```

---

## 4.3 Governance Coverage

`ATE-GOVERNANCE-TO-EVIDENCE-MAPPING-ARCHITECTURE-v0.1.1.md` replaced the simplistic idea that COA acceptance + a VA policy digest is sufficient governance evidence.

It now distinguishes:

- governance source;
- complete clause manifest;
- authorized operationalization;
- structural control requirements;
- behavioral evidence requirements;
- acceptance requirements;
- interaction/precedence requirements;
- bounded coverage extent;
- governance coverage manifest;
- current dependency verification.

A `GovernanceCoverageClaim` is explicitly non-authoritative; current trust must revalidate underlying dependencies.

The older trust-decision layer still evaluates COA, VA, and one behavioral receipt largely as separate gates.

**Gap:** no canonical current `GovernanceCoverageContext` or equivalent is bound into `TrustDecision`.

---

## 4.4 Behavioral / Functional Evidence

The behavioral/functional evidence architecture now treats evidence as bounded observations produced under frozen protocols, evaluator authority, precommitment, lifecycle, scope, and campaign-history rules.

The original decision model binds one `behavioral_receipt_id`.

That is now too weak as a general composition primitive.

Current qualification/governance may depend on:

- multiple evidence requirements;
- multiple receipts;
- structural-control conformance;
- campaign history;
- evidence lifecycle classes;
- refresh status;
- evaluator independence.

**Gap:** the trust decision should normally consume current qualification/governance status produced from those dependencies, while preserving evidence-package/coverage digests for audit, rather than independently reinterpret one generic behavioral receipt.

---

## 4.5 Risk / Assurance vs Qualification / Governance

Risk/assurance is already present, but composition is incomplete.

The final decision must reconcile at least three distinct constraints:

```text
Action risk policy:
    required_assurance_profile

Qualification:
    maximum_risk_class
    qualified capability scope
    qualified assurance capability

Governance operationalization:
    structural/evidence/approval requirements for this action/risk context
```

A grant requires all three to agree.

There is currently no single normative composition rule that states this intersection explicitly.

---

## 4.6 Capability Scope

Capability scope is one of the strongest existing parts of the decision layer.

The current architecture correctly treats the `CapabilityToken` as an authority ceiling rather than evidence that execution should occur.

The requested action must be an exact/subset match and cannot be widened by the participant.

This should remain, but the token must be checked against both:

- qualification capability ceiling; and
- governance/risk structural requirements.

**Gap:** current documents do not explicitly require:

```text
requested_action
    subset_of CapabilityToken
    subset_of Qualification capability scope
```

with both evaluated against the same canonical action semantics.

---

## 4.7 Current Trust / Revocation State

The architecture already captures trust-root, policy, revocation, and federation epochs.

Newer layers introduce additional monotonic/current state:

- qualification-status epoch;
- requalification-policy epoch;
- governance coverage/policy state;
- evidence refresh/currentness;
- runtime verification validity.

**Gap:** the existing `TrustDecision` epoch set is incomplete relative to the current architecture.

---

## 5. Decision-Ordering Issue

The production architecture's older gate list places requested-action canonicalization near the end.

The reference architecture's phase model is stronger:

```text
1. canonicalize requested action
2. classify risk from authoritative action semantics
3. derive required assurance/evidence/control policy
4. verify runtime/qualification/governance/capability/current state
5. compose decision
```

This ordering should become normative.

Otherwise downstream checks can accidentally reason about different interpretations of the requested action.

---

## 6. Missing Canonical Decision Input

The most important missing object is a canonical immutable input to the Trust Decision Authority.

Recommended conceptual object:

```text
TrustDecisionInput {
    decision_input_version

    requested_action_digest
    canonical_action_type
    canonical_target_identity
    target_state_digest?          // where required by risk policy

    verified_runtime_context_digest

    qualification_id
    qualification_credential_digest
    qualification_status_epoch
    qualified_profile_digest

    governance_coverage_manifest_digest
    governance_current_state_digest

    capability_token_id
    capability_token_digest

    risk_classification_id
    risk_classification_digest
    risk_class
    required_assurance_profile

    required_approval_artifact_digests[]
    required_structural_control_receipt_digests[]

    trust_root_epoch
    policy_epoch
    revocation_epoch
    federation_epoch?
    requalification_policy_epoch

    evidence_package_digest
    evidence_currentness_digest

    verifier_policy_digest
    evaluated_at
    input_valid_until
}
```

Canonical digest:

```text
trust_decision_input_digest
```

The Trust Decision Authority should sign the verdict over this exact digest plus the decision identity/validity fields.

---

## 7. Recommended Deterministic Composition Rule

ATE should not use weighted trust scoring for governed execution.

The composition should remain an AND-gate over mandatory conditions.

Conceptually:

```text
GRANT iff

canonical_action_valid
AND authoritative_risk_classification_current
AND VerifiedRuntimeContext current
AND qualification ACTIVE
AND runtime/profile matches qualification
AND action capability within qualification ceiling
AND risk within qualification ceiling
AND required assurance satisfied
AND governance required operationalized coverage current
AND all REQUIRED structural controls current
AND required approvals current
AND CapabilityToken valid and contains exact action
AND all controlling issuers authorized/current
AND all required trust/revocation/policy states current
AND all freshness requirements satisfied
AND replay/nonce preconditions valid
AND all cross-artifact bindings consistent
```

Otherwise:

```text
TRUST_DENIED(reason_code)
```

No score threshold and no compensating control should turn a failed mandatory invariant into grant unless the governing policy explicitly defines an authorized alternative path.

---

## 8. Deterministic Failure Ordering

The repo repeatedly requires deterministic denial but does not yet freeze one modern failure precedence after adding the newer layers.

A stable gate order should be specified so the same invalid input set yields the same primary denial code.

Recommended high-level order:

```text
D0 structural parse/version/canonicalization
D1 authoritative action + risk classification
D2 trust-root / signer-role authority
D3 current trust/revocation/policy state availability
D4 runtime identity / VerifiedRuntimeContext
D5 qualification current status + profile/scope ceilings
D6 governance coverage + required structural/acceptance dependencies
D7 capability authorization exact/subset semantics
D8 assurance-specific approvals/freshness/key-custody requirements
D9 cross-artifact binding consistency
D10 nonce/replay precondition
D11 final decision-input digest construction
```

The exact ordering needs adversarial review before freeze.

---

## 9. TrustDecision Schema Needs Revision

Recommended modernized conceptual `TrustDecision`:

```text
TrustDecision {
    trust_decision_id
    trust_decision_input_digest

    verified_runtime_context_digest
    qualification_id
    qualification_status_epoch
    governance_coverage_manifest_digest

    requested_action_digest
    risk_class
    required_assurance_profile

    capability_token_id
    capability_token_digest

    trust_root_epoch
    policy_epoch
    revocation_epoch
    requalification_policy_epoch
    federation_epoch?

    verifier_policy_digest

    verdict
    primary_reason_code
    secondary_reason_codes[]?

    issued_at
    valid_until
    nonce / operation_id

    trust_decision_authority_id
    signature
}
```

This does not need to embed every upstream artifact. It must cryptographically bind the exact verified decision context.

---

## 10. Point-in-Time Consistency

A decision can otherwise mix state observed at different moments:

```text
runtime verified at epoch X
qualification checked at epoch Y
revocation changed at epoch Z
policy changed during evaluation
```

The composition architecture must define one of:

1. an authoritative snapshot/transactional state-read model; or
2. explicit monotonic epoch observations plus required final rechecks before signing/execution.

High-assurance profiles already require executor-side final policy/revocation rechecks. The composition layer should make those recheck obligations explicit in the signed decision.

---

## 11. Executor Recheck Contract

The TrustDecision should state which dependencies are:

```text
DECISION_TIME_FINAL
EXECUTION_TIME_RECHECK_REQUIRED
```

Examples likely requiring execution-time recheck for higher assurance:

- TrustDecision revocation;
- active policy epoch;
- revocation epoch/current state;
- human approval freshness;
- mutable target state;
- resource/capability state.

The executor should not need to re-run behavioral evaluation or requalification; it should verify current validity of the signed composition and the explicitly designated fast-changing dependencies.

---

## 12. Existing Strengths To Preserve

Do not replace these existing design decisions:

- action-specific trust rather than general agent trust;
- `TRUST_GRANTED` / `TRUST_DENIED` only;
- fail closed;
- no self-authorization;
- issuer-role authorization distinct from signature validity;
- authoritative risk classification;
- least-privilege capability scope;
- one action / replay-resistant execution;
- current-state revocation semantics;
- executor enforcement boundary;
- independent audit evidence;
- no claim that signatures/provenance/behavioral evidence prove moral character.

The missing work is composition, not reinvention.

---

## 13. Inspection Disposition

**Disposition:** `DEDICATED_COMPOSITION_ARCHITECTURE_REQUIRED`

The repo has enough mature component contracts to define one current trust-decision composition layer.

The recommended next artifact is:

**`ATE-TRUST-DECISION-COMPOSITION-ARCHITECTURE-v0.1.md`**

It should:

1. define canonical `TrustDecisionInput`;
2. define modernized `TrustDecision`;
3. freeze decision gate ordering;
4. define qualification + governance + risk + capability intersection rules;
5. define current-state/epoch consistency semantics;
6. define decision-time vs execution-time recheck obligations;
7. define deterministic denial reason precedence;
8. preserve the existing executor/enforcement architecture;
9. explicitly supersede only the outdated composition portions of older production/reference documents, not rewrite their history.

No live-model experiment is required for this work.

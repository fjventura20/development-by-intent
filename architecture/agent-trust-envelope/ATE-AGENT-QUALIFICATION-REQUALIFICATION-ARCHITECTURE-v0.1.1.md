# ATE Agent Qualification & Requalification Architecture v0.1.1

**Status:** Revised architecture candidate — DESIGN ONLY  
**Date:** 2026-09-16  
**Program:** Agent Trust Envelope (ATE)  
**Supersedes:** `ATE-AGENT-QUALIFICATION-REQUALIFICATION-ARCHITECTURE-v0.1.md`  
**Adversarial review:** `ATE-AGENT-QUALIFICATION-REQUALIFICATION-ADVERSARIAL-REVIEW-v0.1.md`

---

## 1. Controlling Principle

> **Qualification is a scoped, finite, evidence-backed admission decision for a defined role and runtime profile. It is not a general trust score, not a bearer capability, and not action authorization.**

A qualification answers:

```text
Is this principal/runtime profile currently eligible
for this bounded class of work
under these governance, capability, risk, assurance,
and evidence conditions?
```

Authorization separately answers whether that qualified runtime may perform a specific action now.

---

## 2. Qualification Chain

```text
Qualification Definition
        |
        v
Qualified Runtime Profile
        |
        v
Evaluation / Evidence Package
        |
        v
Qualification Decision
        |
        v
Qualification Credential
        |
        +--> Current Qualification Status
        |
Runtime Identity + Attestation
        |
        v
VerifiedRuntimeContext
        |
        v
Qualification Valid For Context?
        |
        v
Action-Specific Authorization
```

No stage implies the next without verification.

---

## 3. Qualification Definition

The active `QualificationDefinition` is signed policy defining what must be demonstrated.

Minimum fields:

```text
qualification_class_id
qualification_definition_version
trust_domain_id
role_id
permitted_capability_classes[]
prohibited_capability_classes[]
maximum_risk_class
minimum_assurance_profile
required_runtime_profile_constraints
required_governance_constraints
required_behavioral_evaluations[]
required_evidence_lifecycle_rules[]
required_evaluator_rules[]
requalification_policy_id
requalification_policy_version
requalification_policy_digest
policy_epoch
maximum_qualification_validity
issuer_authority_constraints
issued_by
effective_from
supersedes?
signature
```

Unknown or superseded controlling definition/policy fails closed unless an explicit compatibility rule permits continued use.

---

## 4. Qualified Runtime Profile

The evaluated profile is immutable and content-addressable.

At minimum it binds:

```text
qualified_profile_id
principal_id or principal_class
software_manifest_digest
model_identity
model_identity_assurance
configuration_profile_digest
tool_capability_profile_digest
resource_permission_class
network_access_class
key_protection_assurance
assurance_tier
coa_digest
value_architecture_digest
policy_bundle_digest
trust_domain_id
project_scope or portability constraints
```

The canonical digest is `qualified_profile_digest`.

Qualification applies to this profile, not merely to a friendly agent name.

---

## 5. Evidence Package

Each qualification decision references an immutable `QualificationEvidencePackage`.

```text
QualificationEvidencePackage {
    evidence_package_id
    qualification_class_id
    qualification_definition_version
    qualified_profile_digest
    evaluator identities/roles
    evaluation protocol digests
    test/result receipts
    behavioral evidence receipts
    governance/profile evidence references
    provenance evidence references
    compatibility/dependency decisions[]
    waiver records[]
    evidence_created_at
    evidence_digest
}
```

The package is content-addressable.

Mutable database metadata MAY index it, but controlling evidence objects MUST remain historically verifiable.

---

## 6. Evidence Lifecycle Classes

Every controlling evidence requirement MUST declare one lifecycle semantic.

### 6.1 `ISSUANCE_SNAPSHOT`

Evidence must be valid when qualification is issued, but may remain the historical basis of that issuance after its collection age increases.

Example: a completed deterministic capability test whose result is tied to an immutable profile.

### 6.2 `CONTINUOUSLY_CURRENT`

Evidence must remain current for the qualification to remain usable.

If it expires, is revoked, or cannot be verified, qualification becomes unusable according to policy.

### 6.3 `PERIODICALLY_REFRESHED`

Evidence may age within a defined refresh interval.

Failure to refresh by the deadline causes deterministic suspension or `REQUALIFICATION_REQUIRED`.

No evidence class may rely on implicit freshness semantics.

For continuously-current evidence:

```text
qualification.valid_until <= controlling_evidence.valid_until
```

unless an explicit refresh mechanism maintains validity.

---

## 7. Evaluator Rules and Independence

Each controlling evidence class declares machine-verifiable evaluator requirements:

```text
evaluator_role
accepted_evaluator_authorities[]
independence_class
self_evaluation_allowed
minimum_independent_evaluators
replication_required
accepted_protocol_versions[]
```

Valid evaluator signatures alone are insufficient unless the evaluator is authorized for that evidence class.

High-risk qualification policies MAY require independent or replicated evaluation.

Self-evaluation MUST NOT become sole controlling evidence when the Qualification Definition forbids it.

---

## 8. Qualification Decision Rule

The Qualification Authority may issue `QUALIFIED` only if:

```text
active Qualification Definition valid
AND subject/profile binding valid
AND all mandatory evidence present
AND evidence lifecycle requirements satisfied
AND evaluator role/independence requirements satisfied
AND governance bindings satisfy definition
AND required evaluations pass
AND no controlling evidence revoked/suspended
AND requalification policy/epoch current
AND issuer has authority for this exact qualification scope
AND no unauthorized waiver is required
```

Missing or ambiguous controlling evidence fails closed.

---

## 9. Qualification Issuer Authority Ceilings

A Qualification Authority credential MUST define limits such as:

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
may_reinstate
may_revoke
```

A cryptographically valid qualification issued outside the issuer's ceilings is invalid.

Waivers and compatibility declarations MUST NOT expand issuer ceilings.

---

## 10. Qualification Credential

Minimum credential:

```text
artifact_type = ATE_QUALIFICATION_CREDENTIAL
artifact_version
qualification_id
qualification_class_id
qualification_definition_version
subject_principal_id
qualified_profile_digest
evidence_package_digest
trust_domain_id
project_scope / portability constraints
permitted_capability_classes[]
maximum_risk_class
minimum_assurance_profile
requalification_policy_id
requalification_policy_version
requalification_policy_digest
policy_epoch
issued_at
not_before
valid_until
refresh_deadlines[]?
revocation_handle
qualification_issuer_id
signature_algorithm
signature
```

The credential is public verifiable evidence. It is **not a secret bearer token**.

Copying the credential does not transfer qualification because verification binds the credential to the exact subject/profile/current runtime context.

---

## 11. Authoritative Qualification Status

Qualification status is current trust state and MUST NOT be inferred only from an old signed credential.

Define an authoritative signed/current state:

```text
QualificationStatusState {
    qualification_id
    status
    status_epoch
    trust_domain_id
    updated_at
    reason_code
    superseding_qualification_id?
    status_authority_id
    signature
}
```

Allowed status vocabulary:

```text
ACTIVE
SUSPENDED
REQUALIFICATION_REQUIRED
EXPIRED
SUPERSEDED
REVOKED
NOT_QUALIFIED
```

Verifier MUST reject rollback to an older authoritative `status_epoch` when a newer accepted epoch is known.

Only `ACTIVE` may satisfy a new qualification-dependent trust decision unless an explicit policy defines another safe state.

---

## 12. Qualification State Transitions

```text
CANDIDATE
   |
UNDER_EVALUATION
   |--------------------> NOT_QUALIFIED
   v
ACTIVE
   |--> SUSPENDED --> ACTIVE | REVOKED | REQUALIFICATION_REQUIRED
   |--> REQUALIFICATION_REQUIRED --> ACTIVE(new credential) | NOT_QUALIFIED
   |--> EXPIRED
   |--> SUPERSEDED
   |--> REVOKED
```

Historical records are append-only/tamper-evident.

No prior credential or status record is silently rewritten.

---

## 13. Qualification Scope

Every qualification binds at least:

- role;
- capability classes;
- risk ceiling;
- assurance profile/tier;
- trust domain;
- project/resource scope or explicit portability;
- runtime profile;
- governance profile;
- validity.

A qualification MUST NOT imply unnamed capability or cross-project portability.

Identical role names in different trust domains/projects do not imply equivalence.

---

## 14. Risk and Assurance Rules

Required checks:

```text
requested_risk <= qualification.maximum_risk_class
required_assurance <= qualification-qualified assurance capability
```

No upward assurance inference.

Qualification at Tier 1 does not become Tier 3 because the credential is still signed.

A capability/risk/assurance expansion requires new qualification unless it was already explicitly evaluated and bounded inside the existing qualification scope.

---

## 15. Governance Binding

Qualification binds the governance state under which evaluation occurred:

```text
coa_digest
value_architecture_digest
policy_bundle_digest
```

Qualification does **not** permanently satisfy runtime/session CoA acceptance.

Where current acceptance is required, runtime trust/authorization verification separately establishes that the active runtime/session has valid governance acceptance compatible with the qualified profile.

Thus:

```text
qualification governance binding
        !=
permanent session acceptance
```

---

## 16. Re-attestation

Re-attestation is appropriate when the qualified profile remains unchanged but runtime-instance freshness must be re-established.

Examples:

- normal process restart;
- runtime credential renewal;
- short-lived attestation expiration;
- new runtime-instance key under same profile.

Result:

```text
same ACTIVE qualification may remain valid
new runtime identity / proof / attestation required
```

Re-attestation does not silently cover a changed qualified profile.

---

## 17. Requalification Policy and Rollback Protection

Every qualification/requalification decision binds:

```text
requalification_policy_id
requalification_policy_version
requalification_policy_digest
policy_epoch
```

Qualification Authority and verifier MUST use current authoritative policy state and reject rollback below a newer known epoch.

The subject cannot select an older policy because it permits a cheaper requalification path.

---

## 18. Change Classification

Each relevant change maps deterministically to:

```text
NO_QUALIFICATION_IMPACT
RE_ATTESTATION_REQUIRED
PARTIAL_REQUALIFICATION_REQUIRED
FULL_REQUALIFICATION_REQUIRED
IMMEDIATE_SUSPENSION
```

Unknown material change defaults to:

```text
FULL_REQUALIFICATION_REQUIRED
```

or `IMMEDIATE_SUSPENSION` when current safety cannot be established.

The subject does not choose the classification.

---

## 19. Default Material-Change Rules

| Change | Default |
|---|---|
| Runtime restart, profile unchanged | Re-attestation |
| Runtime credential renewal, profile unchanged | Re-attestation |
| Major software implementation change | Full requalification |
| Model family/version/weights materially change | Full requalification |
| Tool gains write/execute/network capability | Full requalification |
| Resource permission expands | Full requalification |
| VA materially changes | Full requalification unless explicit compatibility |
| CoA changes | Re-acceptance + requalification assessment; default full |
| Policy bundle materially changes | Partial/full per current policy |
| Key protection assurance decreases | Immediate suspension + requalification |
| Assurance-tier claim increases | Full requalification at target tier |
| Behavioral evidence refresh missed | Suspend or requalification-required per lifecycle rule |
| Security incident involving subject/profile | Immediate suspension pending assessment |
| Material behavioral drift signal | Suspend/requalification according to policy |
| Qualification expires | Requalification required |
| Issuer compromised/revoked | Status action under trust-root/revocation policy |

Version labels such as patch/minor/major do not themselves determine compatibility.

---

## 20. Compatibility Declarations

Signed compatibility may reduce requalification cost only within strict non-expansion bounds.

```text
QualificationCompatibility {
    source_qualification_id
    source_profile_digest
    target_profile_digest or bounded_change_predicate
    qualification_class_id
    preserved_evidence_classes[]
    invalidated_evidence_classes[]
    required_delta_evaluations[]
    preserved_maximum_risk_class
    preserved_capability_scope
    preserved_assurance_ceiling
    permitted_trust_domain/project_scope
    requalification_policy_digest
    policy_epoch
    valid_until
    issuer
    signature
}
```

Compatibility MUST NOT silently increase:

- capability scope;
- risk ceiling;
- assurance tier;
- trust/project scope;
- resource/network/tool authority;
- governance latitude.

Any such expansion requires a new qualification decision at the expanded scope.

---

## 21. Partial Requalification

Partial requalification may preserve evidence only when a signed dependency/compatibility decision states why changed dimensions do not invalidate that evidence.

For each preserved evidence class record:

```text
preserved_evidence_digest
changed_dimensions[]
non_interference_basis
compatibility_decision_digest
```

The new Qualification Decision Record binds these references.

Evidence is never preserved merely because nobody chose to rerun it.

---

## 22. Full Requalification

Full requalification is required when:

- material change affects the qualification basis;
- expanded capabilities/risk/assurance are requested;
- current policy requires it;
- compatibility cannot be proven;
- governing profile changes materially;
- current qualification definition is incompatibly superseded;
- evidence integrity is uncertain.

Full requalification creates a new qualification credential and lineage record.

---

## 23. Capability Expansion

The following transitions are presumed material:

```text
read -> write
write -> execute
local -> network
internal -> external transmission
non-production -> production
single resource -> broad scope
no secrets -> secret access
```

Default:

```text
FULL_REQUALIFICATION_REQUIRED
```

unless the broader capability was already inside the evaluated qualified profile and current activation remains within that prequalified bound.

---

## 24. Suspension

`SUSPENDED` is temporary and fail-closed.

Appropriate for:

- uncertain evidence integrity;
- incident investigation;
- material drift signal pending review;
- issuer/status uncertainty;
- missed continuously-current/periodic evidence requirement;
- inability to determine current trust state.

Suspended qualification cannot support new authorization.

Reinstatement requires an authorized status transition with evidence.

---

## 25. Revocation, Expiry, Supersession

### Revocation
Permanent invalidation for future trust grants.

### Expiry
Validity interval ended without replacement.

### Supersession
A newer qualification replaces an older one without implying the prior evidence was fraudulent.

These states are distinct and auditable.

Current status, not historical signature validity, controls new use.

---

## 26. Qualification Lineage

Every replacement credential SHOULD record:

```text
previous_qualification_id
requalification_reason
preserved_evidence_digests[]
new_evidence_digests[]
compatibility_decision_digests[]
superseded_at
```

This produces an auditable professional-credential history.

---

## 27. Qualification Deadline Semantics

Prefer one controlling credential deadline:

```text
valid_until
```

If `requalification_due_at` is also represented, require:

```text
valid_until <= requalification_due_at
```

unless the specification explicitly defines `requalification_due_at` as an earlier mandatory renewal deadline, in which case the earlier effective deadline controls.

Periodic evidence refresh deadlines may be earlier than credential expiry and can suspend qualification when missed.

---

## 28. Behavioral Drift

Drift signals may arise from:

- scheduled regression evaluation;
- audit anomalies;
- incident reports;
- policy denial patterns;
- provider/model changes;
- post-deployment monitoring;
- evaluator reassessment.

A drift signal is not itself proof of bad intent or misconduct.

Policy maps signals to:

```text
NO_ACTION
HEIGHTENED_MONITORING
SUSPEND
PARTIAL_REQUALIFICATION
FULL_REQUALIFICATION
REVOKE
```

---

## 29. Qualification Decision Record

Each qualification-status decision SHOULD create immutable/tamper-evident evidence:

```text
QualificationDecisionRecord {
    decision_id
    subject_principal_id
    qualified_profile_digest
    qualification_class_id
    qualification_definition_version
    evidence_package_digest
    result
    reason_codes[]
    issuer/evaluator references
    requalification_policy_digest
    policy_epoch
    decided_at
    validity
    predecessor_qualification_id?
    compatibility_decision_digests[]?
    signature
}
```

---

## 30. Waivers

Waivers are signed policy artifacts, never invisible operator exceptions.

They bind:

- requirement waived;
- subject/profile/scope;
- rationale;
- approving authority;
- validity;
- compensating controls;
- risk ceiling.

A waiver MUST NOT expand the issuing authority's own ceiling.

---

## 31. Qualification Verification Against Runtime Context

The credential is not a bearer secret.

Verifier binds:

```text
QualificationCredential.subject_principal_id
QualificationCredential.qualified_profile_digest
VerifiedRuntimeContext.principal_id
VerifiedRuntimeContext.qualified_profile_digest
current QualificationStatusState
current policy epoch
current governance compatibility
requested role/capability/risk/assurance/scope
```

A copied credential presented by another principal/runtime fails because the bindings do not match.

---

## 32. Fail-Closed Conditions

Qualification-dependent trust MUST fail closed for:

- unknown/unauthorized issuer;
- issuer ceiling violation;
- bad signature;
- unsupported version;
- expired/not-yet-valid credential;
- non-ACTIVE current status;
- qualification-status rollback;
- stale/rolled-back requalification policy epoch;
- wrong subject/profile;
- incompatible governance;
- insufficient role/capability/risk/assurance/scope;
- unmet evidence lifecycle requirement;
- evaluator independence/authority failure;
- missing required evidence;
- unknown material change compatibility;
- hidden/invalid waiver.

---

## 33. Frozen Architectural Invariants

### Q-I1 SCOPED_QUALIFICATION
Qualification is bounded to explicit role, capability, risk, assurance, scope, profile, governance, and validity.

### Q-I2 EVIDENCE_BACKED
No qualification without immutable evidence package satisfying the active definition.

### Q-I3 PROFILE_BINDING
Qualification binds exact evaluated profile or explicit signed compatibility path.

### Q-I4 GOVERNANCE_BINDING
Qualification records exact governance context; current runtime/session acceptance remains separately verifiable where required.

### Q-I5 SEPARATION_FROM_AUTHORIZATION
Qualification alone cannot execute an action.

### Q-I6 MONOTONIC_STATUS
Older ACTIVE evidence cannot override newer suspension/revocation/supersession/status state.

### Q-I7 EVIDENCE_LIFECYCLE
Every controlling evidence class has explicit freshness semantics.

### Q-I8 CHANGE_FAILS_SAFE
Unknown material change cannot silently reuse qualification.

### Q-I9 CAPABILITY_EXPANSION_REQUALIFIES
Material authority expansion requires qualification at the expanded scope.

### Q-I10 COMPATIBILITY_NO_EXPANSION
Compatibility cannot silently increase capability, risk, assurance, scope, or governance latitude.

### Q-I11 PARTIAL_REQUALIFICATION_JUSTIFIED
Preserved evidence requires explicit dependency/compatibility justification.

### Q-I12 ISSUER_CEILINGS
Qualification issuer signatures are valid only within authorized issuance ceilings.

### Q-I13 EVALUATOR_POLICY
Required evaluator authority/independence is machine-verifiable.

### Q-I14 POLICY_ROLLBACK_PROTECTION
Requalification policy version/digest/epoch cannot be downgraded.

### Q-I15 PUBLIC_CREDENTIAL_BINDING
Credential copying is harmless because qualification is exact-subject/profile/context-bound, not possession-bound.

### Q-I16 FINITE_VALIDITY
Qualification has finite validity and refresh semantics.

### Q-I17 RISK_CEILING
Requested action risk cannot exceed qualification ceiling.

### Q-I18 ASSURANCE_BINDING
No upward assurance inference.

### Q-I19 REATTESTATION_DISTINCTION
Profile-preserving runtime renewal requires fresh runtime evidence, not automatic full requalification.

### Q-I20 LINEAGE
Replacement/supersession preserves auditable predecessor/evidence relationships.

---

## 34. Candidate Lean Qualification Tests

A future qualification protocol should remain deterministic and small. Candidate tests:

```text
Q-T0  valid evidence/profile -> ACTIVE qualification valid for context
Q-T1  qualification alone cannot authorize governed action
Q-T2  copied credential on wrong principal/profile rejected
Q-T3  newer SUSPENDED/REVOKED status defeats older ACTIVE credential
Q-T4  stale/expired controlling evidence obeys lifecycle rule
Q-T5  runtime restart unchanged profile -> re-attestation path
Q-T6  material software/model change -> requalification
Q-T7  capability/risk expansion -> requalification
Q-T8  governance substitution rejected
Q-T9  compatibility declaration cannot expand qualification
Q-T10 partial requalification requires preservation justification
Q-T11 issuer ceiling violation rejected
Q-T12 evaluator independence rule enforced
Q-T13 requalification-policy rollback rejected
Q-T14 cross-project reuse rejected unless portability explicit
Q-T15 lineage/supersession verified
```

No experiment is authorized by this architecture.

---

## 35. Relationship to P2

P2 establishes a `VerifiedRuntimeContext` that includes a qualified profile and qualification evidence.

This architecture supplies the semantics behind that qualification:

```text
Evidence-backed Qualification
          +
Fresh Runtime Identity / Attestation
          |
          v
VerifiedRuntimeContext
          |
          v
Qualification Valid For This Context
          |
          v
Bounded Authorization
```

P2 must not treat a valid qualification signature as sufficient without current status and exact context bindings.

---

## 36. Recommended Next Step

Perform one final implementation-readiness/adversarial consistency review of this v0.1.1 against:

- Runtime Identity / Attestation v0.1.1;
- Risk & Assurance Policy Model;
- Production Requirements & Conformance Profile;
- Revocation & Trust State Model.

If no architectural contradiction remains, mark this architecture ready for future qualification-protocol design.

Do not implement a qualification harness yet.

---

## 37. Final Statement

The professional-credential analogy becomes technically useful only when qualification has limits.

ATE qualification therefore means:

> **An authorized qualification authority, acting under explicit issuance ceilings and current policy, has determined from an immutable and properly sourced evidence package that this exact principal/profile is presently eligible for this bounded role, capability set, risk/assurance envelope, scope, and governance context — subject to finite validity, current status, and deterministic requalification rules.**

Anything broader is reputation, not qualification.
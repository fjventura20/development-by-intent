# ATE Runtime Identity, Trust Root & Attestation Architecture v0.1.1

**Status:** Design revision — candidate for final adversarial review  
**Date:** 2026-09-16  
**Program:** Agent Trust Envelope (ATE)  
**Base artifact:** `ATE-RUNTIME-IDENTITY-TRUST-ROOT-ATTESTATION-ARCHITECTURE-v0.1.md`  
**Adversarial review:** `ATE-RUNTIME-IDENTITY-ATTESTATION-ADVERSARIAL-REVIEW-v0.1.md`  
**Purpose:** Resolve the blocking findings from the v0.1 adversarial review before any P2 experiment is frozen.

---

## 1. Revision Model

This artifact is a normative revision to v0.1.

All v0.1 architecture remains in force except where this document explicitly replaces or tightens it.

The revision does not authorize implementation.

The revision does not freeze P2.

Its purpose is to make the trust-establishment semantics precise enough for a final implementation-readiness/adversarial pass.

---

## 2. Revision Summary

v0.1.1 adds nine required clarifications:

1. explicit attestation authority and signer semantics;
2. immutable qualified runtime profiles;
3. explicit governance-acceptance evidence;
4. assurance-tier-specific clone resistance;
5. project/application scope and verifier audience binding;
6. deterministic revocation freshness;
7. model/provider identity assurance modes;
8. explicit runtime-key protection assurance;
9. cross-artifact context binding.

The resulting trust proposition is:

> A runtime is verified only when one coherent set of signed, fresh, scope-correct evidence binds the active runtime instance to an accepted attestor, an immutable qualified profile, valid governance acceptance, current revocation state, and the assurance level required by verifier policy.

---

# 3. Evidence Classes

ATE runtime verification SHALL distinguish the following evidence classes:

```text
Root / Issuer Policy
Runtime Identity Credential
Attestation Statement
Qualification Credential
Qualified Runtime Profile
Governance Acceptance Evidence
Revocation State Evidence
Runtime Proof of Possession
Verification Decision Record
```

No one artifact substitutes for another.

In particular:

```text
runtime proof of possession != attestation
qualification_id != qualified profile
CoA digest != CoA acceptance
valid signature != correct project/audience
runtime instance ID != non-clonability
```

---

# 4. Explicit Attestation Authority

## 4.1 Attestor role

ATE SHALL define an `attestor` as a principal authorized by verifier policy to make measurement claims about a runtime.

The attestor is distinct from the runtime being measured.

The attestor may be implemented by different mechanisms according to assurance tier.

## 4.2 Assurance-tier attestors

### Tier 0 — Development / Evidence Only

Possible attestor:

- trusted test harness/operator.

No production claim.

### Tier 1 — Local Managed Runtime

Attestor:

- trusted bootstrap/host attestation service operating outside the untrusted runtime identity being evaluated.

Trust derives from the local host/bootstrap trust root.

### Tier 2 — Managed Workload

Attestor:

- orchestrator/workload identity authority or equivalent managed platform attestor.

### Tier 3 — Hardware-Backed

Attestor:

- TPM/TEE/HSM-backed attestation chain or equivalent hardware-rooted mechanism.

## 4.3 Attestation statement

A canonical `AttestationStatement` SHALL bind at least:

```text
artifact_type = ATE_ATTESTATION_STATEMENT
artifact_version
attestation_profile
trust_domain_id
project_scope
principal_id
runtime_instance_id
runtime_public_key_digest
runtime_identity_credential_digest
software_manifest_digest
model_identity
model_identity_assurance
configuration_profile_digest
governance_profile_digest
qualified_profile_digest
challenge_nonce
verifier_audience
attestor_id
attestor_key_id
issued_at
valid_until
```

The attestation statement SHALL be signed by the attestor.

## 4.4 Runtime proof of possession

Separately, the runtime SHALL sign a verifier challenge/context using the private key corresponding to `runtime_public_key_digest`.

That proves possession of the runtime instance key.

It does not prove the truth of software, configuration, model, or governance measurements.

## 4.5 Required rule

A verifier MUST reject self-asserted measurement data unless the active assurance profile explicitly permits self-attestation.

Self-attestation MUST NOT satisfy a policy requiring Tier 1 or stronger attestation.

---

# 5. Immutable Qualified Runtime Profile

## 5.1 Qualified profile object

Qualification SHALL bind to an immutable `QualifiedRuntimeProfile`.

Candidate canonical structure:

```text
artifact_type = ATE_QUALIFIED_RUNTIME_PROFILE
artifact_version
qualified_profile_id
trust_domain_scope
project_scope
principal_class
role_scope
software_manifest_constraint
model_runtime_constraint
model_identity_assurance_minimum
configuration_profile_digest
tool_capability_profile_digest
coa_digest
value_architecture_digest
policy_bundle_digest
assurance_minimum
key_protection_minimum
qualification_protocol_digest
behavioral_evidence_bundle_digest
created_at
```

The canonical digest of this object is:

```text
qualified_profile_digest
```

## 5.2 Qualification credential

A `QualificationCredential` SHALL bind:

```text
qualification_id
subject_principal_id
qualified_profile_digest
qualification_class
issuer_id
issued_at
valid_until
revocation_handle
```

and SHALL be signed by an issuer authorized for that qualification class and scope.

## 5.3 Compatibility

A changed runtime profile is not automatically covered by an older qualification.

Compatibility requires an explicit signed artifact such as:

```text
QualificationCompatibilityDeclaration
```

that identifies:

```text
source_qualified_profile_digest
target_qualified_profile_digest
allowed_change_class
issuer
validity
```

Absent such a declaration, mismatch fails closed.

---

# 6. Governance Acceptance Evidence

## 6.1 Problem

A digest proves which governance document is referenced.

It does not prove that the principal accepted it.

## 6.2 Governance acceptance object

ATE SHALL support a `GovernanceAcceptance` evidence object containing at least:

```text
artifact_type = ATE_GOVERNANCE_ACCEPTANCE
artifact_version
acceptance_event_id
trust_domain_id
project_scope
principal_id
qualified_profile_digest
coa_digest
value_architecture_digest
policy_bundle_digest
accepted_at
valid_until_or_supersession_policy
acceptance_issuer_or_verifier
```

The object SHALL be signed/tamper-evident according to the active governance policy.

## 6.3 Runtime binding

The verifier SHALL establish both:

```text
principal accepted governance set G
```

and

```text
active runtime matches a qualified profile containing G
```

For policies requiring session-specific acceptance, a fresh runtime/session acknowledgment SHALL additionally bind the current `runtime_instance_id` to the accepted governance set.

P2 does not need to require session-specific acceptance unless the P2 policy explicitly selects that stronger mode.

---

# 7. Runtime Instance and Clone Resistance

## 7.1 Runtime instance identity

Each new runtime start under the normal issuance flow SHALL generate:

```text
new runtime_instance_id
new runtime instance keypair
new runtime identity credential
new attestation freshness event
```

## 7.2 Assurance limitation

ATE SHALL NOT claim that every runtime instance credential is inherently non-clonable.

Clone resistance depends on assurance tier and key protection.

## 7.3 Tier 1 statement

Tier 1 provides:

- trusted-bootstrap issuance;
- short-lived runtime identity;
- fresh verifier challenge;
- host-attestor measurements;
- process/OS isolation according to the deployment profile.

Tier 1 does **not** guarantee non-clonability if a sufficiently privileged actor copies both the runtime private key and the issued runtime state after creation.

## 7.4 Tier 2/3

Tier 2 and Tier 3 may provide stronger instance binding through managed workload identity or hardware-backed non-exportable keys.

Verifier policy SHALL select the minimum assurance appropriate to the risk.

---

# 8. Project Scope and Audience Binding

## 8.1 Namespace distinction

ATE SHALL distinguish:

```text
trust_domain_id
project_scope
verifier_audience
role_scope
```

Semantics:

```text
trust_domain_id  = administrative trust root/domain
project_scope    = project/application/environment in which evidence is usable
verifier_audience = intended consumer or consumer class
role_scope       = qualified operational role
```

## 8.2 Cross-project reuse

Evidence issued for one `project_scope` SHALL NOT be valid in another scope unless an explicit federation/delegation policy grants that use.

## 8.3 Audience

Fresh attestation SHALL bind `verifier_audience` so that a response produced for verifier A cannot be replayed as fresh evidence to verifier B when policy requires audience-specific verification.

---

# 9. Deterministic Revocation Freshness

## 9.1 Requirement

A credential is not considered non-revoked merely because the verifier has not heard about a revocation.

Verifier policy SHALL define the required freshness model for each credential/evidence class.

## 9.2 Supported revocation modes

Candidate modes:

```text
ONLINE_AUTHORITATIVE
SIGNED_STATE_MAX_AGE
REVOCATION_EPOCH
SHORT_LIVED_CREDENTIAL
HYBRID
```

## 9.3 Revocation state evidence

Where applicable, a `RevocationStateEvidence` object SHALL bind:

```text
artifact_type
artifact_version
trust_domain_id
project_scope
revocation_domain
revocation_epoch
issued_at
valid_until_or_max_age
issuer
```

## 9.4 Verification rule

The verifier SHALL reject evidence when the revocation information does not satisfy the maximum freshness permitted by active verifier policy.

## 9.5 P2 simplification

A local P2 MAY use one authoritative local revocation store with a deterministic epoch and no network staleness.

That simplification is permitted because distributed revocation is not the P2 research question.

---

# 10. Model / Provider Identity Assurance

ATE SHALL distinguish the source and assurance of a model/runtime identity claim.

Candidate enumeration:

```text
LOCAL_MEASURED
DEPLOYMENT_ATTESTED
PROVIDER_ATTESTED
SELF_REPORTED
UNKNOWN
```

A `model_identity` claim SHALL therefore include or resolve to:

```text
model_identifier
model_identity_assurance
model_identity_issuer
model_identity_evidence_digest?
```

Verifier policy SHALL define acceptable assurance modes.

A self-reported model name MUST NOT satisfy policy requiring measured or provider-attested identity.

P2 MAY use `LOCAL_MEASURED` or a deterministic simulated provider-attested identity to avoid dependence on external provider infrastructure.

---

# 11. Runtime Key Protection Assurance

Proof of possession proves control of a key.

It does not prove how the key is protected.

ATE SHALL represent key-protection assurance separately.

Candidate values:

```text
SOFTWARE_PROCESS_PROTECTED
OS_KEYSTORE
MANAGED_WORKLOAD_KEY
HARDWARE_NONEXPORTABLE
```

The runtime identity credential or associated attestation evidence SHALL bind the applicable key-protection class.

Verifier policy MAY require a minimum class.

P2 MAY use `SOFTWARE_PROCESS_PROTECTED`, but MUST NOT interpret the result as proving hardware non-exportability.

---

# 12. Cross-Artifact Context Binding

## 12.1 Coherent context requirement

Verification SHALL succeed only when all evidence resolves to one coherent runtime context.

The verifier MUST NOT merely validate signatures independently.

## 12.2 Required consistency checks

As applicable, the verifier SHALL compare or cryptographically resolve:

```text
trust_domain_id
project_scope
principal_id
runtime_instance_id
runtime_public_key_digest
runtime_identity_credential_digest
qualified_profile_digest
software_manifest_digest
model_identity
model_identity_assurance
configuration_profile_digest
coa_digest
value_architecture_digest
policy_bundle_digest
challenge_nonce
verifier_audience
artifact_type
artifact_version
```

Any conflicting binding fails closed.

## 12.3 Reference-by-digest

Where one object does not repeat all fields, it SHALL refer by digest to an immutable object that supplies them.

This prevents individually valid artifacts from being recombined across contexts.

---

# 13. Corrected Runtime Identity Credential

Candidate structure:

```text
RuntimeIdentityCredential
|
+-- artifact_type
+-- artifact_version
+-- credential_id
+-- trust_domain_id
+-- project_scope
+-- principal_id
+-- runtime_instance_id
+-- runtime_public_key
+-- runtime_public_key_digest
+-- key_protection_assurance
+-- attestation_profile
+-- qualified_profile_digest
+-- software_manifest_digest
+-- model_identity
+-- model_identity_assurance
+-- configuration_profile_digest
+-- governance_profile_digest
+-- issuer_id
+-- issuer_key_id
+-- issued_at
+-- not_before
+-- valid_until
+-- revocation_handle
```

The issuer SHALL verify the issuance prerequisites required by policy before signing this credential.

---

# 14. Corrected Verification Request

Verifier constructs:

```text
VerificationRequest
|
+-- challenge_nonce
+-- verifier_audience
+-- expected_trust_domain_id
+-- expected_project_scope
+-- expected_role_scope
+-- minimum_assurance_tier
+-- minimum_key_protection_assurance
+-- accepted_attestation_profiles
+-- accepted_model_identity_assurance
+-- required_qualified_profile? / qualification class
+-- required_coa_digest
+-- required_value_architecture_digest
+-- required_policy_bundle_digest
+-- minimum_policy_epoch
+-- revocation_freshness_policy
```

The request itself need not always be signed in P2, but the evidence response SHALL cryptographically bind the challenge and audience.

---

# 15. Corrected Verification Flow

```text
Verifier
   |
   | challenge + audience + scope + assurance requirements
   v
Runtime / Evidence Presenter
   |
   +-- RuntimeIdentityCredential
   +-- QualificationCredential
   +-- QualifiedRuntimeProfile
   +-- GovernanceAcceptance
   +-- AttestationStatement signed by accepted attestor
   +-- runtime proof-of-possession signature
   +-- revocation evidence/reference
   v
Verifier
   |
   | validate root and issuer capabilities
   | validate artifact signatures/versions
   | validate project/audience scope
   | validate runtime key possession
   | validate attestor authority
   | validate attestation freshness
   | validate immutable qualified profile
   | validate current governance acceptance
   | validate cross-artifact consistency
   | validate model identity assurance
   | validate key-protection/assurance tier
   | validate revocation freshness/state
   | validate time bounds
   v
VerifiedRuntimeContext
```

---

# 16. Revised `VerifiedRuntimeContext`

The verification output SHOULD contain or reference:

```text
VerifiedRuntimeContext
|
+-- verification_decision_id
+-- trust_domain_id
+-- project_scope
+-- principal_id
+-- runtime_instance_id
+-- runtime_public_key_digest
+-- runtime_identity_credential_digest
+-- attestation_statement_digest
+-- attestation_profile
+-- assurance_tier
+-- key_protection_assurance
+-- software_manifest_digest
+-- model_identity
+-- model_identity_assurance
+-- configuration_profile_digest
+-- qualified_profile_digest
+-- qualification_credential_digest
+-- governance_acceptance_digest
+-- coa_digest
+-- value_architecture_digest
+-- policy_bundle_digest
+-- revocation_state_epoch/reference
+-- verifier_audience
+-- verification_challenge_digest
+-- verified_at
+-- valid_until
```

The context itself SHALL be canonical and hash-addressable.

Authorization SHALL bind either to its digest or to a complete immutable subset sufficient to prevent context substitution.

---

# 17. Corrected Invariants

The following invariants supersede/extend the v0.1 candidate invariant set.

### I1 — PRINCIPAL_BINDING

Every runtime credential binds exactly one principal.

### I2 — INSTANCE_BINDING

Every runtime credential binds exactly one runtime instance and runtime public key.

### I3 — PROOF_OF_POSSESSION

Verification requires possession of the private key corresponding to the credentialed runtime public key.

### I4 — ATTESTATION_AUTHORITY_BINDING

Runtime self-signature cannot establish measurement truth when verifier policy requires trusted attestation.

### I5 — FRESH_ATTESTATION

Accepted attestation binds the current verifier challenge and audience.

### I6 — QUALIFIED_PROFILE_BINDING

Qualification binds to one immutable `qualified_profile_digest` or an explicit signed compatibility declaration.

### I7 — GOVERNANCE_ACCEPTANCE_BINDING

Required governance digests must be backed by valid principal acceptance evidence and match the active qualified profile.

### I8 — SOFTWARE_BINDING

Measured software must satisfy the qualified profile.

### I9 — CONFIGURATION_BINDING

Material configuration must satisfy the qualified profile.

### I10 — MODEL_IDENTITY_ASSURANCE

Model/runtime identity must satisfy the assurance mode required by verifier policy.

### I11 — TRUST_DOMAIN_BINDING

Credentials cannot cross trust domains absent explicit federation.

### I12 — PROJECT_SCOPE_BINDING

Credentials cannot cross project/application scope absent explicit federation/delegation.

### I13 — AUDIENCE_BINDING

Fresh attestation cannot be replayed to an unauthorized verifier audience.

### I14 — KEY_PROTECTION_ASSURANCE

Verifier policy evaluates runtime-key protection separately from proof of possession.

### I15 — ASSURANCE_TIER_BINDING

The verifier MUST NOT infer stronger instance/clone-resistance guarantees than the selected assurance tier provides.

### I16 — EXPIRATION

Expired mandatory evidence fails closed.

### I17 — REVOCATION_FRESHNESS

Revocation evidence/state must satisfy the active freshness policy.

### I18 — REVOCATION

Known-revoked mandatory evidence fails closed.

### I19 — CROSS_ARTIFACT_CONTEXT_BINDING

All evidence artifacts must resolve to one coherent runtime context; valid artifacts from different contexts cannot be mixed.

### I20 — RESTART_REIDENTIFICATION

Normal restart produces a new runtime-instance identity and requires fresh runtime verification.

### I21 — UNKNOWN_VERSION_FAIL_CLOSED

Unknown mandatory artifact versions fail closed absent explicit compatibility policy.

### I22 — AUTHORIZATION_DEPENDS_ON_VERIFIED_CONTEXT

Operational authorization binds to the verified runtime context, not to an unverified identity claim.

---

# 18. Issuer Capability Validation

A valid chain to a trust root is necessary but not sufficient.

Each issuer SHALL be constrained by signed capabilities.

Candidate capability fields:

```text
may_issue_runtime_identity
may_issue_qualification_class
may_sign_attestation_profile
trust_domain_scope
project_scope
role_scope
maximum_validity
minimum_or_maximum_assurance_tier
path_length
```

A verifier SHALL confirm that the issuer was authorized to issue the specific artifact being evaluated.

---

# 19. Time Semantics for P2

P2 MAY assume one trusted local clock.

All time-based evidence SHALL use that same clock.

P2 SHALL still test:

- `not_before`;
- `valid_until`;
- attestation freshness window;
- revocation-state freshness.

Distributed clock uncertainty remains out of scope.

---

# 20. Candidate P2 Objective After v0.1.1

The candidate objective is now:

> **Can a verifier distinguish a valid qualified runtime instance from a substituted, copied-without-key, stale, cross-project, governance-mismatched, profile-mismatched, or otherwise invalid runtime instance using a coherent set of signed identity, trusted attestation, qualification, governance-acceptance, proof-of-possession, and revocation evidence?**

This remains a candidate until v0.1.1 passes final adversarial review.

---

# 21. Candidate Lean P2 Boundary

P2 SHOULD remain local and inexpensive.

Suggested components:

```text
local trust root
identity issuer
qualification issuer
trusted local attestor/bootstrap
runtime under test
verifier
local authoritative revocation state
```

P2 SHOULD NOT require:

- distributed networking;
- TPM/TEE hardware;
- cloud orchestrators;
- external model-provider attestation;
- production PKI;
- remote federation.

Those mechanisms belong to later assurance-tier experiments.

---

# 22. Candidate P2 Test Set

The following tests are candidates, not yet frozen:

```text
P2-T0   valid qualified runtime verifies
P2-T1   wrong principal rejected
P2-T2   copied runtime credential without runtime private key rejected
P2-T3   expired runtime identity rejected
P2-T4   stale attestation challenge rejected
P2-T5   attestation for wrong verifier audience rejected
P2-T6   substituted software digest rejected
P2-T7   configuration-profile mismatch rejected
P2-T8   governance mismatch rejected
P2-T9   governance digest without acceptance evidence rejected
P2-T10  qualification for different qualified profile rejected
P2-T11  unqualified runtime rejected
P2-T12  revoked qualification rejected
P2-T13  stale revocation-state evidence rejected
P2-T14  wrong trust domain rejected
P2-T15  wrong project scope rejected
P2-T16  restart requires new runtime identity
P2-T17  mixed valid artifacts from different instances rejected
P2-T18  runtime self-signed measurement rejected when trusted attestation required
P2-T19  unacceptable model-identity assurance rejected
P2-T20  unacceptable key-protection/assurance tier rejected
P2-T21  unknown artifact version rejected
P2-T22  issuer lacking required issuance capability rejected
```

A later freeze SHOULD select the minimum subset that proves the accepted invariants rather than automatically running every conceivable test.

---

# 23. Security Claim Boundaries

v0.1.1 deliberately limits claims.

A successful Tier 1 P2 would establish that a verifier can validate a short-lived software-managed runtime identity under a trusted local bootstrap/attestor.

It would **not** establish:

- hardware-backed non-clonability;
- protection against root copying the runtime private key;
- exact identity of an opaque remote model unless separately provider-attested;
- distributed revocation correctness;
- cross-organization federation correctness;
- production availability.

These limitations SHALL appear in any P2 closeout.

---

# 24. Relationship to P1

P1 established:

```text
trusted authority + trusted executor
        -> bounded authorization can be enforced against requester bypass
```

v0.1.1 defines how a verifier may establish whether a runtime deserves to enter the trusted side of that statement.

The resulting composition becomes:

```text
verify runtime identity/profile/governance
        |
        v
VerifiedRuntimeContext
        |
        v
issue bounded authorization
        |
        v
P1-style enforcement plane
```

---

# 25. Relationship to Agent Qualification

Qualification now has an explicit semantic anchor:

```text
behavioral evidence
      -> qualification credential
      -> immutable qualified_profile_digest
      -> current trusted attestation matches profile
      -> runtime accepted as qualified
```

This prevents qualification from becoming a generic badge attached to a principal name.

---

# 26. Relationship to Condition of Agency and Value Architecture

CoA and VA now participate in two separate evidence relationships:

```text
GovernanceAcceptance
    proves principal accepted governance set

QualifiedRuntimeProfile
    proves qualification was performed under governance set
```

Runtime verification requires those relationships to agree.

A future change to CoA or VA therefore cannot silently preserve qualification unless an explicit compatibility/requalification rule permits it.

---

# 27. Relationship to Trust Root & Key Custody

This revision does not replace `ATE-TRUST-ROOT-KEY-CUSTODY-MODEL-v0.1.md`.

It consumes that model by requiring:

- authorized issuer keys;
- separate issuance roles;
- runtime proof-of-possession keys;
- attestor keys;
- revocation-state signing authority where applicable;
- key-protection assurance metadata.

The key-custody model defines how those keys are protected and rotated; this architecture defines how their claims compose during runtime verification.

---

# 28. Relationship to Federation

Cross-domain/project acceptance remains explicit.

No verifier may infer:

```text
credential valid in Domain A
therefore valid in Domain B
```

or:

```text
qualification valid in Project A
therefore valid in Project B
```

The federation model must authorize the exact issuer, artifact class, assurance level, and scope transition.

---

# 29. Final Architectural Decision

ATE runtime trust SHALL be established by composition of independently meaningful evidence classes rather than by one omnibus identity credential.

The minimum logical chain is:

```text
trusted root policy
    -> authorized issuer/attestor capabilities
    -> runtime identity credential
    -> runtime key proof of possession
    -> fresh trusted attestation
    -> immutable qualified profile
    -> valid qualification credential
    -> valid governance acceptance
    -> sufficiently fresh revocation state
    -> cross-artifact consistency
    -> VerifiedRuntimeContext
    -> authorization
```

---

# 30. Final Statement

A runtime is not trusted merely because:

- it has the right name;
- it holds a valid certificate;
- it owns a private key;
- it reports the right software hash;
- it references the right CoA or Value Architecture;
- it once passed qualification.

ATE trust is established only when those claims form one fresh, scope-correct, cryptographically coherent, policy-sufficient evidence chain.

The v0.1.1 design is therefore ready for a final adversarial review before P2 is frozen.

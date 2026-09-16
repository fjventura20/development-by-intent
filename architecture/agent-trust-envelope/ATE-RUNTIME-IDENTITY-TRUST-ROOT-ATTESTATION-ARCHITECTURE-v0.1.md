# ATE Runtime Identity, Trust Root & Attestation Architecture v0.1

**Status:** Design candidate  
**Date:** 2026-09-16  
**Program:** Agent Trust Envelope (ATE)  
**Predecessor:** ATE Production Gap Analysis v0.1  
**Related evidence:** ATE P1 Local Enforcement (`ATE_P1_V0_2_LOCAL_ENFORCEMENT_ESTABLISHED`)  
**Purpose:** Define how ATE identifies a running agent/runtime, roots that identity in trusted issuance, binds it to implementation and governance state, and provides fresh evidence that another principal can verify before granting authority.

---

# 1. Executive Summary

ATE P1 established local enforcement once trusted authority and executor identities were assumed.

The next architectural problem is upstream:

> **Why should a verifier trust that a running process, agent, or service is actually the qualified principal it claims to be?**

This design answers that question with four distinct concepts:

1. **Principal Identity** — the stable identity of the agent/service role.
2. **Runtime Instance Identity** — the identity of one concrete running instance.
3. **Attestation Evidence** — evidence describing what that instance is actually running and under what governance state.
4. **Qualification Binding** — evidence that the identified runtime class or instance is approved for a defined scope and period.

These are rooted in an explicit **ATE Trust Root** and linked through short-lived signed credentials.

The core rule is:

> **Possession of a private key is not sufficient evidence of qualification.**

A production ATE verifier should require, at minimum:

```text
trusted issuer chain
        +
valid runtime identity
        +
fresh attestation evidence
        +
current qualification
        +
current governance bindings
        +
current authorization
```

before protected execution is allowed.

---

# 2. Architectural Goal

The architecture must allow a verifier to answer:

> “Is this the specific runtime instance, running an approved implementation and governance configuration, that is currently qualified and authorized to perform this operation?”

The answer must not depend solely on:

- process name;
- username;
- hostname;
- socket path;
- IP address;
- model self-identification;
- environment variable;
- possession of a long-lived key;
- a stale certificate;
- a prior qualification result;
- or an unauthenticated manifest.

ATE therefore requires a verifiable chain from a trusted root to the runtime currently requesting authority.

---

# 3. Scope

This v0.1 architecture defines:

- ATE principal identity;
- runtime-instance identity;
- trust-root hierarchy;
- identity issuance;
- identity credential format;
- runtime attestation semantics;
- software/configuration/governance measurements;
- freshness;
- qualification binding;
- Condition of Agency binding;
- Value Architecture binding;
- trust-domain binding;
- lifecycle, rotation, expiration, revocation;
- assurance tiers;
- verifier decision flow;
- candidate future P2 experiment boundaries.

This design does not implement:

- TPM-specific APIs;
- cloud-provider workload identity;
- specific PKI products;
- remote execution;
- blockchain/notary services;
- large-scale certificate infrastructure;
- behavioral qualification procedures themselves.

---

# 4. Design Principles

## 4.1 Identity is not authorization

Identity answers:

> Who or what runtime is this?

Authorization answers:

> What may it do now?

They must remain separate.

A runtime may possess a valid identity and still have zero authority.

## 4.2 Identity is not qualification

A runtime can be correctly identified yet unqualified.

Qualification answers:

> Has this principal been evaluated and approved for this role and scope?

## 4.3 Qualification is not attestation

Qualification may state that a software/runtime class passed required evaluation.

Attestation answers:

> Is the currently running instance actually using the implementation and governance state that qualification covered?

## 4.4 Attestation is not behavioral proof

Attestation can prove hashes, versions, keys, host state, and governance bundle identity.

It cannot by itself prove that an AI model will behave correctly.

Behavioral evidence remains necessary for claims about agent behavior.

## 4.5 Long-lived private keys are not permanent trust

A key proves control of that key.

It does not independently prove:

- current software;
- current governance state;
- qualification validity;
- revocation state;
- correct host;
- correct project;
- or current runtime instance.

## 4.6 Trust is scoped

Every ATE trust statement must be scoped by:

- trust domain;
- role;
- qualification class;
- policy version;
- validity interval;
- permitted operations or authorization class.

There is no universal “trusted agent” bit.

---

# 5. ATE Identity Layers

ATE separates identity into three layers.

## 5.1 Principal Identity

A stable logical identity representing an agent/service role.

Examples:

```text
ate://project-alpha/authority/main
ate://project-alpha/executor/payments
ate://project-alpha/agent/researcher-17
```

A principal identity survives restarts and may span multiple runtime instances over time.

It does not itself identify a specific process.

### Principal properties

- `principal_id`
- `principal_type`
- `trust_domain_id`
- `role`
- `owner/issuer`
- `qualification_class`
- `allowed_runtime_profiles`
- `status`

## 5.2 Runtime Instance Identity

Represents one concrete runtime instance.

A runtime instance identity should be unique per launch/session.

Conceptually:

```text
principal_id:
  ate://project-alpha/executor/payments

runtime_instance_id:
  urn:uuid:...
```

Runtime identity binds:

- principal identity;
- runtime-instance public key;
- software manifest;
- configuration manifest;
- host/workload identity;
- governance bundle;
- issuance time;
- expiration time;
- nonce/session epoch;
- attestation reference.

A restarted process receives a new `runtime_instance_id`.

## 5.3 Operation Identity

P1 already established stable operation identity.

Runtime identity must not replace it.

The three scopes are:

```text
principal_id
    long-lived logical role

runtime_instance_id
    one running instance

operation_id
    one protected intended effect
```

These identities must never be conflated.

---

# 6. Trust Domain

Every ATE principal belongs to a **trust domain**.

A trust domain defines the administrative and cryptographic namespace in which identities and qualifications are meaningful.

Examples:

```text
ate-domain://frank-lab
ate-domain://acme-finance
ate-domain://project-ursa
```

## 6.1 Why trust domains matter

Without domain binding, a credential valid in one project could be replayed in another.

The verifier must reject credentials whose:

```text
trust_domain_id != verifier.expected_trust_domain_id
```

unless an explicit cross-domain federation policy exists.

---

# 7. Trust Root Architecture

ATE should use a layered trust hierarchy.

```text
ATE Root of Trust
       |
       +--------------------+
       |                    |
       v                    v
Identity Issuer       Qualification Issuer
       |                    |
       v                    v
Runtime Credential    Qualification Credential
       |
       v
Runtime Instance
```

Additional issuers may exist for:

- governance policy;
- attestation;
- audit;
- authorization.

But roles should remain cryptographically distinguishable.

---

# 8. Root Keys

## 8.1 Root purpose

The ATE root key establishes which issuers are trusted within a trust domain.

The root should not sign routine runtime credentials directly.

It signs intermediate issuer identities or issuer certificates.

## 8.2 Recommended separation

At minimum:

```text
ATE Root Key
    |
    +-- Identity Issuer Key
    +-- Qualification Issuer Key
    +-- Governance Issuer Key
    +-- Attestation Issuer Key
```

Operational decision-signing keys remain separate from these trust-establishment keys.

## 8.3 Root-key custody

Production roots should support stronger protection than ordinary service keys.

Possible implementations by assurance tier include:

- offline encrypted root key;
- OS keyring/HSM-backed key;
- TPM-backed key;
- cloud KMS/HSM key;
- hardware security module.

The abstract architecture must not require one vendor.

---

# 9. Issuer Roles

## 9.1 Identity Issuer

May issue runtime identity credentials for approved principals.

It must verify the issuance prerequisites defined by the deployment tier.

It cannot grant operational authorization merely by issuing identity.

## 9.2 Qualification Issuer

Signs statements that a principal/runtime profile has passed a qualification process.

Qualification issuer and identity issuer may be operated by the same organization but should remain logically distinct.

## 9.3 Governance Issuer

Publishes signed versions of:

- Condition of Agency;
- Value Architecture;
- policy bundles.

A runtime credential references exact digests, not mutable names.

## 9.4 Attestation Issuer

In some deployment tiers, the attestation evidence may be signed directly by:

- a hardware root;
- an orchestrator;
- a trusted bootstrap service;
- a workload identity system.

ATE treats these as attestation issuers.

---

# 10. Runtime Identity Credential

A runtime instance receives a short-lived signed credential.

Candidate logical fields:

```text
credential_type: "ATE_RUNTIME_IDENTITY"
credential_version: "0.1"

trust_domain_id
principal_id
principal_type
runtime_instance_id

runtime_public_key
runtime_key_algorithm

software_manifest_digest
configuration_digest
host_or_workload_identity
model_runtime_identifier

coa_digest
value_architecture_digest
policy_bundle_digest
qualification_id

attestation_evidence_digest
attestation_profile

issued_at
not_before
valid_until
issuance_nonce
issuer_id
issuer_key_id
```

The credential is signed by the trusted Identity Issuer.

---

# 11. Runtime Key

Each runtime instance should possess an instance-specific signing key.

## 11.1 Purpose

The runtime key proves that a message originated from the runtime instance identified by the runtime credential.

## 11.2 Properties

Preferred:

- generated at runtime start;
- unique per runtime instance;
- private key never exported where the assurance tier can prevent export;
- short-lived;
- destroyed at runtime termination.

## 11.3 Why instance keys matter

Without an instance key, someone who copies the signed runtime credential may impersonate the runtime.

The credential therefore binds:

```text
runtime_instance_id
    +
runtime_public_key
```

and protocol messages must prove possession of the corresponding private key.

---

# 12. Software Manifest

ATE should define a signed or canonical software manifest describing the runtime implementation.

Candidate fields:

```text
manifest_version
software_name
software_version
source_commit
build_id
binary_digest
dependency_lock_digest
container_image_digest? 
runtime_launcher_digest?
model_runtime_identifier
approved_entrypoint
```

The exact fields depend on deployment tier.

The critical property is a deterministic `software_manifest_digest`.

---

# 13. Configuration Manifest

Configuration can materially alter behavior even when binaries are unchanged.

ATE therefore needs a configuration digest separate from software identity.

The configuration manifest may cover:

- command-line arguments;
- environment-policy whitelist;
- plugin set;
- tool permissions;
- connected resources;
- model/provider configuration;
- system prompt or agent policy bundle;
- feature flags;
- network policy;
- sandbox policy.

Secrets themselves should not be embedded.

Their identifiers or policy classes may be included where relevant.

---

# 14. Governance Bundle

Governance state should be referenced as immutable content.

A runtime identity binds exact digests for:

```text
Condition of Agency
Value Architecture
Policy Bundle
```

Example:

```text
coa_digest
value_architecture_digest
policy_bundle_digest
```

Mutable labels such as:

```text
"current-policy"
```

are insufficient.

---

# 15. Condition of Agency Binding

The runtime identity must not merely state that a CoA exists.

It must reference an acceptance record.

Candidate acceptance record:

```text
coa_acceptance_id
principal_id
runtime_profile_id
coa_digest
accepted_at
valid_until
acceptance_method
issuer
signature
```

The verifier requires:

```text
runtime credential coa_digest
    ==
qualification coa_digest
    ==
current authorization required coa_digest
```

unless an explicit compatibility rule exists.

---

# 16. Value Architecture Binding

Likewise, the runtime credential references the exact Value Architecture digest under which qualification occurred.

The binding proves:

- what VA version was declared;
- what VA version qualification covered;
- what VA version the runtime claims to load.

It does not independently prove behavioral adherence.

That remains a qualification/evidence question.

---

# 17. Qualification Credential

A qualification credential should be independently signed.

Candidate fields:

```text
credential_type: "ATE_QUALIFICATION"

qualification_id
trust_domain_id
principal_id
runtime_profile_id

qualification_class
permitted_role
permitted_scope

software_manifest_digest
configuration_profile_digest
coa_digest
value_architecture_digest
policy_bundle_digest

evidence_bundle_digest
evaluator_id
evaluation_protocol_id
evaluation_protocol_version

issued_at
valid_until
requalification_triggers
issuer_id
```

---

# 18. Runtime Profile

Qualification should usually apply to a defined runtime profile rather than one ephemeral process.

A runtime profile may bind:

```text
software manifest
configuration profile
governance bundle
model/runtime class
tool-permission class
sandbox class
```

Every runtime instance must prove that it conforms to the qualified profile.

---

# 19. Attestation

Attestation evidence answers:

> What is actually running now?

The attestation layer is deployment-specific, but its abstract semantics should be uniform.

Candidate evidence claims:

```text
runtime_instance_id
runtime_public_key
software_manifest_digest
configuration_digest
governance_bundle_digest
host/workload_identity
boot/session identity
issued_at
freshness_nonce
attestation_profile
```

The verifier must know which attestation issuer it trusts.

---

# 20. Freshness

Attestation without freshness is replayable.

ATE should support challenge-response freshness.

## 20.1 Verifier challenge

Verifier sends:

```text
challenge_nonce
expected_trust_domain
expected_principal?
timestamp/window
```

## 20.2 Runtime/attestor response

Attestation evidence binds the challenge nonce.

This proves that the evidence was produced for the current verification event rather than replayed from an old session.

---

# 21. Assurance Tiers

ATE should define assurance tiers without hard-coding one infrastructure.

## Tier 0 — Development / Evidence Only

Used for early research.

May rely on:

- file hashes;
- process identity;
- trusted operator;
- signed manifests.

No production claim.

## Tier 1 — Local Managed Runtime

Trust root:

- trusted OS/bootstrap;
- root-owned runtime code;
- runtime-generated instance key;
- signed identity credential.

Attestation:

- trusted bootstrap measurements;
- software/config hashes;
- fresh challenge.

Suitable for local controlled environments.

## Tier 2 — Managed Workload

Trust root:

- workload identity/orchestrator;
- signed image;
- deployment manifest;
- short-lived workload credentials.

Suitable for managed server/container environments.

## Tier 3 — Hardware-Backed

Trust root:

- TPM/TEE/HSM or equivalent;
- measured boot;
- hardware-protected runtime identity key;
- remote attestation.

Suitable for high-assurance environments.

---

# 22. Verifier Trust Policy

A verifier should evaluate runtime evidence against an explicit policy.

Candidate policy:

```text
required_trust_domain
allowed_identity_issuers
allowed_attestation_profiles
allowed_qualification_issuers
required_qualification_class
required_coa_digest
required_va_digest
minimum_assurance_tier
maximum_credential_age
required_policy_epoch
```

Verification is therefore deterministic policy evaluation, not intuition.

---

# 23. Verification Flow

The intended flow is:

```text
Verifier
   |
   | 1. challenge nonce
   v
Runtime
   |
   | 2. runtime credential
   | 3. qualification credential
   | 4. fresh attestation
   | 5. proof-of-possession signature
   v
Verifier
   |
   | validate trust chains
   | validate freshness
   | validate runtime-key possession
   | validate software/config/governance bindings
   | validate qualification
   | validate expiration/revocation
   | validate trust-domain/scope
   v
VERIFIED RUNTIME CONTEXT
```

Only after this step should operational authorization be considered.

---

# 24. Proof of Possession

Runtime credential theft must not be sufficient for impersonation.

The verifier challenge should be signed using the runtime-instance private key.

Verifier checks:

```text
signature(runtime_private_key, challenge_context)
```

against:

```text
runtime_public_key
```

embedded in the signed runtime identity credential.

---

# 25. Runtime Verification Context

Successful verification should produce an internal object such as:

```text
VerifiedRuntimeContext
|
+-- trust_domain_id
+-- principal_id
+-- runtime_instance_id
+-- runtime_public_key
+-- assurance_tier
+-- software_manifest_digest
+-- configuration_digest
+-- qualification_id
+-- coa_digest
+-- value_architecture_digest
+-- policy_bundle_digest
+-- attestation_timestamp
+-- identity_valid_until
+-- qualification_valid_until
+-- policy_epoch
+-- verifier_decision_id
```

Operational authorization should bind to this verified context.

---

# 26. Authorization Binding

A production authority decision should eventually include:

```text
verified_principal_id
verified_runtime_instance_id
qualification_id
coa_digest
value_architecture_digest
policy_epoch
assurance_tier
```

This prevents authorization from floating free of the runtime that was actually verified.

---

# 27. Runtime Replacement

If a process restarts:

```text
runtime_instance_id changes
runtime key changes
new attestation required
new runtime credential required
```

Existing authorization should not silently transfer unless policy explicitly permits transfer by stable principal identity.

For high-risk operations, authorization should bind to runtime instance.

---

# 28. Credential Expiration

Runtime identity credentials should be short-lived.

Qualification credentials may be longer-lived.

Example relation:

```text
runtime identity: minutes/hours
qualification: days/weeks/months
governance documents: versioned until superseded
```

This allows runtime freshness without constant full requalification.

---

# 29. Revocation

ATE requires separate revocation domains.

## 29.1 Principal revocation

Disables the logical principal.

## 29.2 Runtime credential revocation

Disables one runtime instance.

## 29.3 Qualification revocation

Withdraws qualification.

## 29.4 Issuer-key revocation

Invalidates credentials under a compromised issuer.

## 29.5 Governance revocation/supersession

Marks a CoA/VA/policy version no longer acceptable.

These events must not be conflated.

---

# 30. Requalification

A runtime should require requalification when the qualified profile materially changes.

Candidate triggers:

```text
software manifest changes
model/runtime version changes
configuration class changes
tool permissions expand
CoA changes
VA changes
policy bundle changes
security incident
qualification expires
behavioral drift detected
```

A verifier should never infer compatibility merely because the principal name stayed the same.

---

# 31. Configuration Drift

Runtime attestation should detect drift from the qualified configuration profile.

Some configuration fields may be declared:

```text
IMMUTABLE
BOUNDED
RUNTIME-VARIABLE
SECRET
```

Only allowed changes should preserve qualification.

This enables practical operation without hashing every ephemeral value.

---

# 32. Model and Provider Identity

For AI agents, implementation identity may include a model/provider component.

ATE should distinguish:

- self-reported model name;
- provider-issued model/runtime identity;
- deployment identifier;
- model family/version;
- local model digest.

The assurance of this field depends on deployment context.

A local model binary can be directly measured.

A remote provider model may require provider attestation or signed service metadata.

---

# 33. External Tooling and Plugins

Agent behavior can change substantially through tools.

The runtime profile should therefore bind relevant tool capability classes.

Examples:

```text
filesystem-read
filesystem-write
shell
network
email-send
financial-data-read
code-execution
production-deploy
```

Qualification should be scoped to the capability set actually granted.

---

# 34. Trust Transitivity

ATE should not assume:

```text
A trusts B
B trusts C
therefore A trusts C
```

Trust delegation must be explicit.

A credential chain can establish issuer authority only when the parent credential grants that exact issuance capability.

---

# 35. Issuer Constraints

Issuer credentials should include constraints such as:

```text
may_issue_identity_for
may_issue_qualification_class
trust_domain_scope
maximum_validity
allowed_assurance_tier
path_length
```

This prevents unrestricted delegation.

---

# 36. Cross-Domain Federation

Cross-domain trust should be optional and explicit.

Possible model:

```text
Domain A Root
    |
    +-- federation policy
            |
            v
      Domain B Issuer
```

The federation statement should define:

- accepted issuer;
- roles/scopes;
- qualification equivalence;
- assurance minimum;
- validity;
- revocation mechanism.

No implicit federation.

---

# 37. Canonicalization

All signed ATE objects require deterministic serialization.

P1 already used canonicalization for signed decision artifacts.

Production identity objects should likewise use one canonical representation.

Candidate:

- RFC 8785 JCS for JSON-based artifacts.

The exact standard can be frozen later.

---

# 38. Hash Agility

Signed credentials should identify algorithms explicitly.

Example:

```text
digest_algorithm: SHA-256
signature_algorithm: Ed25519
```

The architecture should support future migration without ambiguous interpretation.

---

# 39. Versioning

Every signed artifact needs:

```text
artifact_type
artifact_version
```

Unknown versions fail closed unless an explicit compatibility path is defined.

---

# 40. Time

Time is security-sensitive.

ATE credentials depend on:

- `not_before`;
- `valid_until`;
- qualification expiration;
- freshness windows;
- revocation timing.

Production architecture must define trusted time sources or bounded clock assumptions.

P2 should avoid overcomplicating this and use one local trusted clock unless time itself is under test.

---

# 41. Failure Semantics

Verification must fail closed for:

- unknown issuer;
- invalid signature;
- expired identity;
- expired qualification;
- revoked credential;
- unknown version;
- stale attestation;
- challenge mismatch;
- runtime-key proof failure;
- software mismatch;
- configuration mismatch;
- governance mismatch;
- trust-domain mismatch;
- insufficient assurance tier.

---

# 42. Evidence Bundle

ATE should support a portable evidence bundle containing references or copies of:

```text
runtime identity credential
qualification credential
attestation evidence
software manifest
configuration manifest
CoA
Value Architecture
policy bundle
revocation state reference
verification decision
```

The bundle should be hash-addressable.

---

# 43. Verification Decision Record

A verifier should produce a signed or tamper-evident decision record.

Candidate fields:

```text
verification_decision_id
verifier_id
subject_principal_id
runtime_instance_id
decision: VERIFIED | REJECTED
reason_codes
credential_digests
attestation_digest
qualification_id
policy_version
verified_at
valid_until
```

This record becomes an input to authorization.

---

# 44. Separation From Enforcement Plane

Runtime verification should produce:

```text
VerifiedRuntimeContext
```

The Enforcement Plane consumes that context.

This preserves architectural separation:

```text
Trust Establishment
        |
        v
Verified Runtime
        |
        v
Authorization
        |
        v
Enforcement
```

---

# 45. Relationship to P1

P1 assumed:

```text
ate-authority == trusted authority implementation
ate-executor  == trusted executor implementation
```

This architecture replaces those assumptions with verifiable claims.

Future P1-like enforcement can therefore become:

```text
verify authority runtime
verify executor runtime
verify requester/agent runtime where required
then authorize
then enforce
```

---

# 46. Relationship to Qualification

Qualification should reference the exact runtime profile tested.

A runtime is accepted only if current attestation matches that profile.

This creates the chain:

```text
behavioral evaluation
        |
        v
qualification credential
        |
        v
qualified runtime profile
        |
        v
fresh runtime attestation
        |
        v
verified runtime instance
```

---

# 47. Relationship to Condition of Agency

CoA acceptance belongs upstream of authorization.

A verifier should be able to prove:

```text
this principal accepted this exact CoA
and this runtime is operating under the corresponding qualified profile
```

That closes the session-binding gap seen in earlier CoA work.

---

# 48. Relationship to Value Architecture

Value Architecture should be part of the qualified runtime profile.

If VA changes materially:

```text
qualification may become stale
```

unless compatibility has been explicitly established.

This prevents silent substitution of governance semantics.

---

# 49. Relationship to Agent Trust Envelope

ATE can now be decomposed into evidence classes:

```text
ATE
|
+-- Identity Evidence
+-- Attestation Evidence
+-- Qualification Evidence
+-- Governance Evidence
+-- Authorization Evidence
+-- Execution Evidence
+-- Audit Evidence
```

A trust decision is the verified composition of these evidence classes.

---

# 50. Candidate ATE Trust Envelope Structure

A future trust envelope may reference:

```text
subject_principal_id
runtime_instance_id
runtime_identity_credential_digest
attestation_evidence_digest
qualification_credential_digest
coa_digest
value_architecture_digest
policy_bundle_digest
verification_decision_id
authorization_scope
validity
revocation_epoch
issuer_chain_digest
```

This is not yet frozen.

---

# 51. Candidate P2 Objective

After this architecture is reviewed and refined, P2 should likely test:

> **Can a verifier distinguish a valid qualified runtime instance from a substituted, stale, copied, expired, or governance-mismatched runtime instance using only signed identity, qualification, and fresh attestation evidence?**

This is narrower than implementing full production PKI.

---

# 52. Candidate P2 Minimal Architecture

A lean local P2 could use:

```text
root issuer
    |
identity issuer
    |
short-lived runtime identity credential

qualification issuer
    |
qualification credential

trusted bootstrap
    |
fresh software/config measurements
    |
attestation statement

runtime
    |
ephemeral instance key
```

No Hermes-scale distributed system is required initially.

---

# 53. Candidate P2 Tests

Possible minimal tests:

```text
P2-T0 valid runtime verifies
P2-T1 wrong principal rejected
P2-T2 copied runtime credential without private key rejected
P2-T3 expired runtime credential rejected
P2-T4 stale attestation challenge rejected
P2-T5 substituted software digest rejected
P2-T6 changed governance digest rejected
P2-T7 unqualified runtime rejected
P2-T8 revoked qualification rejected
P2-T9 wrong trust domain rejected
P2-T10 runtime restart requires new runtime identity
```

This list is provisional.

No experiment should be frozen until the architecture passes adversarial review.

---

# 54. What P2 Should Not Test

P2 should not yet attempt:

- multi-cloud federation;
- TPM vendor integration;
- blockchain anchoring;
- global certificate transparency;
- large-scale revocation infrastructure;
- model behavioral compliance;
- production availability;
- performance benchmarking.

Those are separate milestones.

---

# 55. Threat Model for Runtime Identity

## In scope

- requester lies about identity;
- runtime credential replay;
- stolen public credential;
- substituted runtime binary;
- stale software version;
- stale governance bundle;
- wrong trust domain;
- expired credential;
- revoked qualification;
- copied credential without runtime private key;
- stale attestation response;
- wrong runtime instance;
- mismatched software/configuration/governance hashes.

## Out of scope for initial local P2

- root compromise;
- identity issuer compromise;
- qualification issuer compromise;
- kernel compromise;
- hardware attacks;
- trusted bootstrap compromise;
- cryptographic primitive break;
- malicious attestation hardware;
- remote network MITM if all messages are already cryptographically authenticated.

---

# 56. Required Invariants

Candidate invariants:

### I1 — PRINCIPAL_BINDING

Every runtime credential binds exactly one `principal_id`.

### I2 — INSTANCE_BINDING

Every runtime credential binds exactly one `runtime_instance_id` and runtime public key.

### I3 — PROOF_OF_POSSESSION

Verification requires proof of the runtime private key.

### I4 — TRUST_DOMAIN_BINDING

Credentials cannot cross trust domains without explicit federation.

### I5 — SOFTWARE_BINDING

Runtime verification requires the measured software identity to match the credential/qualified profile.

### I6 — CONFIGURATION_BINDING

Material configuration must match the qualified profile.

### I7 — GOVERNANCE_BINDING

CoA, VA, and policy digests must match accepted/current requirements.

### I8 — QUALIFICATION_BINDING

Verified runtime must possess a valid qualification credential for the runtime profile and role.

### I9 — FRESH_ATTESTATION

Attestation must bind a verifier challenge or equivalent freshness proof.

### I10 — EXPIRATION

Expired runtime identity or qualification fails closed.

### I11 — REVOCATION

Revoked identity or qualification fails closed according to the active revocation model.

### I12 — RESTART_REIDENTIFICATION

A restarted runtime receives a new runtime instance identity.

### I13 — UNKNOWN_VERSION_FAIL_CLOSED

Unknown artifact versions are rejected absent explicit compatibility policy.

### I14 — AUTHORIZATION_DEPENDS_ON_VERIFIED_CONTEXT

Operational authorization must bind to the verified runtime context rather than an unverified principal claim.

---

# 57. Issuance Sequence

A candidate Tier-1 local issuance sequence:

```text
Trusted Bootstrap
      |
      | measure software/config/governance
      v
Attestation Builder
      |
      | create fresh measurement record
      v
Runtime
      |
      | generate ephemeral runtime keypair
      | create credential request
      v
Identity Issuer
      |
      | verify principal eligibility
      | verify measurement/attestation
      | verify qualification
      | verify governance bindings
      v
Signed Runtime Identity Credential
```

---

# 58. Verification Sequence

```text
Verifier
   |
   | random challenge
   v
Runtime
   |
   | runtime credential
   | qualification credential
   | attestation bound to challenge
   | proof-of-possession signature
   v
Verifier
   |
   | root chain?
   | identity valid?
   | qualification valid?
   | attestation fresh?
   | runtime key proof valid?
   | software/config match?
   | governance match?
   | trust domain correct?
   | revocation clear?
   v
VerifiedRuntimeContext
```

---

# 59. Runtime Credential Renewal

Renewal should require new freshness evidence.

A credential should not be renewed solely because:

```text
previous credential was valid
```

At minimum, renewal should re-establish:

- runtime alive;
- same runtime key or approved replacement;
- current measurements;
- current qualification;
- current governance versions;
- non-revoked status.

---

# 60. Key Rotation

Issuer-key rotation should preserve validation of prior evidence while preventing new issuance under retired keys.

The trust policy should distinguish:

```text
valid_for_verification
valid_for_new_issuance
revoked
```

This avoids destroying historical audit verifiability when an issuer rotates keys normally.

---

# 61. Compromise Response

If an issuer key is compromised:

- stop new issuance;
- mark key compromised;
- revoke affected credentials as policy requires;
- issue replacement key;
- record incident;
- reissue credentials only after revalidation;
- preserve evidence explaining the transition.

---

# 62. Rollback Protection

A valid old credential should not override newer mandatory governance.

Verifier policy should enforce minimums such as:

```text
minimum_policy_epoch
minimum_coa_version/digest set
minimum_va_version/digest set
minimum_qualification_protocol
```

This prevents downgrade by presenting still-cryptographically-valid historical evidence.

---

# 63. Qualification Compatibility

Some changes may preserve qualification.

ATE may eventually define compatibility declarations.

Example:

```text
qualification Q1 valid for:
  software manifest family S
  config profile <= permissions class 2
  VA digest V3
  CoA digest C4
```

Compatibility must be explicit and signed.

Never infer it heuristically.

---

# 64. Evidence Immutability

All qualification, attestation, and verification artifacts should be content-addressable by digest.

Mutable database records may index them, but the evidence object itself should be immutable.

---

# 65. Privacy

ATE identity evidence should disclose only what the verifier needs.

Potential techniques:

- scoped credentials;
- pseudonymous principal IDs;
- reference digests instead of full behavioral records;
- selective evidence retrieval.

Production architecture should avoid embedding unnecessary sensitive data in broadly shared credentials.

---

# 66. Availability

Trust establishment can become a single point of failure.

Production designs should distinguish:

- online issuance;
- offline-verifiable short-lived credentials;
- revocation freshness requirements.

P2 does not need to solve high availability.

---

# 67. Audit

Identity issuance and verification should themselves be auditable.

Events include:

```text
principal created
runtime credential issued
qualification issued
qualification revoked
runtime verification accepted/rejected
issuer key rotated
governance version superseded
```

These events become part of ATE accountability.

---

# 68. Production Readiness Gates

Before calling runtime identity production-ready, ATE should demonstrate:

1. explicit root trust policy;
2. separated issuer roles;
3. runtime instance keys;
4. short-lived identity credentials;
5. fresh attestation;
6. software/config/governance binding;
7. qualification binding;
8. revocation;
9. renewal;
10. rotation;
11. rollback prevention;
12. auditability;
13. verifier interoperability;
14. failure-closed behavior.

---

# 69. Architectural Decision

ATE should adopt the following hierarchy:

```text
Trust Root
    |
    v
Issuer Authority
    |
    v
Principal Identity
    |
    v
Runtime Instance Identity
    |
    +--> Attestation
    |
    +--> Qualification
    |
    +--> Governance Bindings
    |
    v
Verified Runtime Context
    |
    v
Authorization
    |
    v
Enforcement
    |
    v
Evidence / Audit
```

---

# 70. North-Star Trust Statement

A verifier should eventually be able to state:

> **I am not trusting this agent because it says who it is, because it owns a key, or because I recognize its process name. I am trusting it for this bounded purpose because a trusted chain identifies this exact runtime instance, fresh evidence binds it to an approved implementation and governance state, current qualification covers that profile, and the resulting authorization is enforced under explicit scope and validity.**

That is the production meaning of an Agent Trust Envelope.

---

# 71. Recommended Next Step

Do not implement P2 yet.

Next perform:

**ATE Runtime Identity / Attestation Adversarial Review v0.1**

The review should attack:

- credential theft;
- runtime substitution;
- credential copying;
- issuer confusion;
- trust-domain confusion;
- stale attestation;
- governance downgrade;
- qualification replay;
- runtime restart ambiguity;
- key rollover ambiguity;
- cross-project reuse;
- configuration drift;
- model/provider identity uncertainty.

Only after that review should the candidate P2 invariants and tests be frozen.

---

# 72. Final Statement

P1 proved that a trusted authority and executor can enforce bounded local authority against an untrusted requester.

This architecture addresses the question P1 deliberately left unanswered:

> **How do we know the authority, executor, or agent runtime is actually the qualified principal we intended to trust?**

The answer is not a single certificate.

It is a verified chain:

```text
trust root
    ->
issuer authority
    ->
principal identity
    ->
runtime-instance identity
    ->
fresh attestation
    ->
qualification
    ->
governance binding
    ->
verified runtime context
    ->
authorization
    ->
enforcement
```

That chain is the next major layer of the Agent Trust Envelope.

# ATE Runtime Identity / Attestation Adversarial Review v0.1

**Status:** Adversarial architectural review  
**Date:** 2026-09-16  
**Program:** Agent Trust Envelope (ATE)  
**Reviewed artifact:** `ATE-RUNTIME-IDENTITY-TRUST-ROOT-ATTESTATION-ARCHITECTURE-v0.1.md`  
**Review disposition:** `REVISION_REQUIRED_BEFORE_P2_FREEZE`

---

## 1. Purpose

This review attacks the proposed ATE Runtime Identity, Trust Root, and Attestation Architecture before any P2 experiment is frozen or implemented.

The reviewed architecture correctly moves ATE beyond process names and static keys toward a chain of:

```text
trust root
  -> issuer authority
  -> principal identity
  -> runtime-instance identity
  -> fresh attestation
  -> qualification
  -> governance binding
  -> verified runtime context
  -> authorization
  -> enforcement
```

The central question of this review is:

> Can a verifier rely on that chain to distinguish the intended qualified runtime from a substituted, copied, stale, cross-project, governance-mismatched, or otherwise invalid runtime without depending on mutable names or self-assertion?

The answer is **not yet**.

The architecture is directionally strong, but several bindings are still descriptive rather than structurally unambiguous. Those gaps should be corrected before P2 invariants and tests are frozen.

---

## 2. Review Summary

### Accepted architectural direction

The following concepts are accepted:

- separate stable principal identity and ephemeral runtime-instance identity;
- short-lived runtime identity credentials;
- runtime-generated proof-of-possession key;
- fresh verifier challenge;
- software/configuration/governance measurements;
- qualification as a distinct credential class;
- explicit trust-domain binding;
- fail-closed version handling;
- authorization consuming a `VerifiedRuntimeContext` rather than an unverified principal claim;
- explicit assurance tiers;
- content-addressable evidence;
- explicit revocation domains;
- no implicit trust transitivity.

### Blocking findings

Nine findings require revision before P2 freeze:

1. attestation signer/trust semantics are under-specified;
2. qualification is not yet cryptographically bound to one immutable qualified profile;
3. governance digests do not prove runtime-bound acceptance;
4. runtime-instance anti-cloning semantics are incomplete;
5. cross-project reuse is not fully prevented by `trust_domain_id` alone;
6. revocation freshness is not yet deterministic;
7. remote model/provider identity assurance is too ambiguous for one common claim;
8. key theft and assurance-tier semantics need explicit limits;
9. canonical context binding must include verifier/audience and artifact linkage to prevent mix-and-match replay.

These are design corrections, not a rejection of the architecture.

---

## 3. Threat Model Used for This Review

### In scope

Assume the adversary can:

- control the requester;
- copy any public credential or evidence bundle;
- replay old signed artifacts;
- present artifacts from another project/trust domain;
- substitute an older or different runtime binary;
- alter mutable configuration;
- attempt to combine valid artifacts from different runtime instances;
- restart, clone, snapshot, or duplicate a software runtime where platform controls permit;
- possess a valid runtime credential but not necessarily the corresponding private key;
- exploit ambiguity in issuer roles, artifact versions, policy epochs, qualification profiles, governance digests, or verifier audience;
- race revocation state and verification;
- present provider/model identity claims that cannot be directly measured locally.

### Out of scope for initial P2

Consistent with the reviewed architecture:

- root compromise;
- kernel compromise;
- trust-root compromise;
- identity-issuer compromise;
- qualification-issuer compromise;
- trusted-bootstrap compromise;
- cryptographic primitive failure;
- malicious hardware root of trust;
- physical memory extraction from a trusted high-assurance runtime.

The review nevertheless distinguishes what Tier 1 software controls can and cannot prove compared with hardware-backed tiers.

---

# 4. Finding F1 — Attestation Trust Semantics Are Under-Specified

**Severity:** CRITICAL  
**Disposition:** MUST CORRECT

The architecture requires fresh attestation but does not yet define exactly **who signs the attestation evidence, which key is trusted to make measurement claims, and why the verifier trusts that signer**.

A challenge nonce by itself prevents replay only if the returned measurement statement is authenticated by a trusted attestor.

A compromised or untrusted runtime could otherwise produce:

```text
nonce = verifier nonce
software_digest = approved digest
config_digest = approved digest
```

and sign it only with its own runtime key. That proves possession of the runtime key, not correctness of the measurements.

## Required correction

Define an explicit `AttestationStatement` with at least:

```text
artifact_type
artifact_version
attestation_profile
trust_domain_id
principal_id
runtime_instance_id
runtime_public_key_digest
software_manifest_digest
configuration_profile_digest
governance_profile_digest
qualification_profile_digest?
challenge_nonce
verifier_audience
issued_at
valid_until
attestor_id
attestor_key_id
```

The statement must be signed by an attestation authority trusted under the selected assurance tier.

Tier semantics must identify the attestor:

- Tier 1: trusted bootstrap/host attestor;
- Tier 2: managed workload/orchestrator attestor;
- Tier 3: hardware-backed attestation root.

The runtime proof-of-possession signature and the attestor signature serve different purposes and MUST NOT be conflated.

### Required invariant

> `ATTESTATION_AUTHORITY_BINDING`: Runtime self-signature cannot establish software/configuration measurement truth. Fresh measurement claims are accepted only when signed by an attestor permitted by verifier policy for the required assurance tier.

---

# 5. Finding F2 — Qualification Must Bind to an Immutable Qualified Profile

**Severity:** CRITICAL  
**Disposition:** MUST CORRECT

The reviewed architecture references `qualification_id`, but an identifier alone does not ensure that the active runtime matches the exact profile that was evaluated.

A qualification must not float across:

- software versions;
- model/runtime versions;
- tool permissions;
- configuration classes;
- CoA versions;
- Value Architecture versions;
- policy bundles;
- trust domains.

## Required correction

Define an immutable `QualifiedRuntimeProfile` whose canonical digest is included in the qualification credential.

Candidate structure:

```text
qualified_profile_id
principal_class
software_manifest_digest
model_runtime_constraint
configuration_profile_digest
tool_capability_profile_digest
coa_digest
value_architecture_digest
policy_bundle_digest
trust_domain_scope
role_scope
assurance_minimum
qualification_protocol_digest
behavioral_evidence_bundle_digest
```

Then define:

```text
qualification_credential
  -> qualified_profile_digest
```

and require current runtime attestation to satisfy that exact profile or an explicitly signed compatibility rule.

### Required invariant

> `QUALIFIED_PROFILE_BINDING`: A qualification credential is valid only for the immutable qualified profile it names. Compatibility with a changed profile must be explicit and signed; it MUST NOT be inferred from a stable principal name or qualification ID.

---

# 6. Finding F3 — Governance Digests Do Not Yet Prove Runtime-Bound Acceptance

**Severity:** CRITICAL  
**Disposition:** MUST CORRECT

The architecture correctly carries `coa_digest` and `value_architecture_digest`, but a digest proves document identity, not acceptance.

Earlier CoA work already demonstrated the failure mode:

```text
CoA exists
+ agent previously attested acceptance
!= active executing session is bound to that commitment
```

## Required correction

Introduce a governance-acceptance credential or equivalent signed evidence object.

Candidate:

```text
GovernanceAcceptance
|
+-- principal_id
+-- qualified_profile_digest
+-- coa_digest
+-- value_architecture_digest
+-- policy_bundle_digest
+-- acceptance_event_id
+-- accepted_at
+-- valid_until / supersession rule
+-- issuer/verifier
+-- signature
```

For runtime-bound assurance, the verification flow must establish that the active runtime profile corresponds to a qualification profile that includes the accepted governance set.

For higher-risk operations, authorization may additionally bind to a fresh runtime/session acknowledgment if policy requires it.

### Required invariant

> `GOVERNANCE_ACCEPTANCE_BINDING`: A governance digest is insufficient by itself. The verifier must possess valid evidence that the principal accepted that exact governance set and that the active runtime profile is qualified under it.

---

# 7. Finding F4 — Runtime-Instance Anti-Cloning Semantics Are Incomplete

**Severity:** HIGH  
**Disposition:** MUST CORRECT FOR CLAIM PRECISION

The architecture states that runtime restart creates a new instance ID and runtime key.

That works when the trusted bootstrap creates a fresh instance.

It does not automatically prevent cloning of a live VM/container/filesystem snapshot after the runtime key and `runtime_instance_id` have already been created.

Two copies could then possess:

```text
same runtime_instance_id
same runtime private key
same runtime credential
```

Tier 1 software-only assurance may not be able to distinguish them.

## Required correction

Define assurance-tier-specific clone resistance.

### Tier 1

State explicitly:

> Tier 1 establishes short-lived runtime-instance identity under a trusted bootstrap but does not claim cryptographic non-clonability if the runtime private key and instance state are copied after issuance.

Mitigations may include:

- very short credential lifetime;
- host-attestor binding;
- boot/session identity;
- verifier nonce freshness;
- host identity included in attestation.

### Tier 2/3

Managed workload or hardware-backed identity may provide stronger instance non-clonability.

### Required invariant

Replace an absolute anti-copy claim with:

> `INSTANCE_ASSURANCE_BINDING`: Verification must satisfy the non-clonability/instance-binding guarantees defined by the selected assurance tier; the verifier MUST NOT infer Tier 3 properties from Tier 1 evidence.

---

# 8. Finding F5 — `trust_domain_id` Alone Is Insufficient for Cross-Project Isolation

**Severity:** HIGH  
**Disposition:** MUST CORRECT

One trust domain may contain multiple projects, applications, environments, or authorization namespaces.

A valid runtime qualified for Project A should not automatically be reusable in Project B merely because both are under the same organizational trust root.

## Required correction

Introduce explicit audience/scope binding such as:

```text
trust_domain_id
project_id / application_id
environment_id
role_scope
authorization_audience
```

Not every credential must include every field, but verifier policy must have a deterministic namespace in which the credential is valid.

A practical distinction is:

```text
trust_domain_id   = who administers trust
project_scope     = where qualification is usable
audience          = who may consume the credential/evidence
```

### Required invariant

> `PROJECT_SCOPE_BINDING`: A credential or qualification issued for one project/application scope cannot be reused in another unless explicit federation/delegation policy permits it.

---

# 9. Finding F6 — Revocation Freshness Needs Deterministic Semantics

**Severity:** HIGH  
**Disposition:** MUST CORRECT

The architecture states that revoked identity or qualification fails closed, but does not define how fresh the verifier's revocation view must be.

Without that rule, these can both be claimed:

```text
credential revoked at t1
verifier with stale state accepts at t2
```

and

```text
revoked credentials fail closed
```

Those are inconsistent unless freshness is bounded.

## Required correction

Verifier policy must state one explicit revocation model per credential class, for example:

- online authoritative check;
- signed revocation state with maximum age;
- revocation epoch;
- short-lived credential where expiration bounds stale acceptance;
- combination of the above.

Candidate verifier inputs:

```text
revocation_state_epoch
revocation_state_issued_at
maximum_revocation_state_age
minimum_policy_epoch
```

### Required invariant

> `REVOCATION_FRESHNESS`: A verifier may accept a credential only if the revocation state used satisfies the freshness requirement defined by policy for that credential class.

P2 may use a simple local authoritative revocation store, but the semantic rule must be frozen first.

---

# 10. Finding F7 — Remote Model/Provider Identity Requires a Different Assurance Claim

**Severity:** HIGH  
**Disposition:** MUST CLARIFY

The architecture correctly notes that local model binaries can be measured while remote provider models may require provider attestation.

Those are not equivalent evidence classes.

A local verifier cannot generally prove the exact weights or internal runtime of a proprietary remote provider merely from an API model name.

## Required correction

Define model identity assurance modes, for example:

```text
LOCAL_MEASURED
PROVIDER_ATTESTED
DEPLOYMENT_ATTESTED
SELF_REPORTED
UNKNOWN
```

Verifier policy may require one or more acceptable modes.

Do not normalize them into a single undifferentiated `model_id` field.

### Required invariant

> `MODEL_IDENTITY_ASSURANCE`: Model/runtime identity claims carry an assurance mode and issuer. A verifier MUST NOT treat a self-reported or API-label identity as equivalent to measured or provider-attested identity.

---

# 11. Finding F8 — Runtime-Key Theft Semantics Must Track Assurance Tier

**Severity:** HIGH  
**Disposition:** MUST CLARIFY

Proof of possession prevents reuse of a copied public credential without the private key.

It does not prevent impersonation after the runtime private key itself is stolen.

At Tier 1, a software-held key may be copyable by a sufficiently privileged actor even when the requester cannot access it.

## Required correction

Each runtime identity credential should carry or imply key-protection assurance, for example:

```text
SOFTWARE_PROCESS_PROTECTED
OS_KEYSTORE
WORKLOAD_IDENTITY_MANAGED
HARDWARE_NONEXPORTABLE
```

Verifier policy can then require a minimum key-protection class.

### Required invariant

> `KEY_PROTECTION_ASSURANCE`: Proof of possession establishes control of the private key, not the mechanism protecting that key. The verifier must evaluate key-protection assurance separately when risk requires it.

---

# 12. Finding F9 — Artifact Mix-and-Match Requires Stronger Context Linking

**Severity:** CRITICAL  
**Disposition:** MUST CORRECT

The proposed chain contains multiple independently signed artifacts:

- runtime identity credential;
- qualification credential;
- attestation statement;
- governance evidence;
- verification decision.

An attacker should not be able to combine individually valid artifacts from different instances or contexts.

## Required correction

Every verification event must construct one canonical context with explicit cross-artifact bindings.

At minimum the verifier should require equality/consistency over:

```text
principal_id
runtime_instance_id
runtime_public_key_digest
trust_domain_id
project_scope/audience
qualified_profile_digest
software_manifest_digest
configuration_profile_digest
coa_digest
value_architecture_digest
policy_bundle_digest
challenge_nonce
artifact versions
```

Where an artifact does not directly contain a field, it must cryptographically reference another immutable artifact containing it.

The attestation statement should also bind:

```text
verifier_audience
challenge_nonce
runtime_identity_credential_digest
```

or equivalent immutable context.

### Required invariant

> `CROSS_ARTIFACT_CONTEXT_BINDING`: Verification succeeds only when all evidence artifacts resolve to one coherent runtime context. Individually valid artifacts from different contexts MUST NOT be composable into a valid verification result.

---

# 13. Additional Non-Blocking Findings

## 13.1 Trusted time

P2 may use one trusted local clock, but the architecture should define that assumption explicitly. Future distributed work must address clock uncertainty.

## 13.2 Identity issuer vs qualification issuer

Role separation is correct. The verifier should validate issuer capabilities, not merely root-chain membership.

Example constraints:

```text
may_issue_runtime_identity
may_issue_qualification_class
may_sign_attestation_profile
trust_domain_scope
project_scope
maximum_validity
```

## 13.3 Evidence-bundle privacy

Digest references are preferable to embedding unnecessary behavioral evidence. The reviewed architecture already points in this direction and should retain it.

## 13.4 Unknown-version handling

Fail-closed behavior is accepted. Compatibility rules, when introduced, must themselves be signed/versioned policy artifacts.

## 13.5 Renewal

Renewal should create a new credential issuance event and should not erase historical evidence. Current architecture is consistent with this.

---

# 14. Revised Verification Chain

After correcting the blocking findings, the verification chain should be conceptually:

```text
Trusted Root Policy
        |
        v
Issuer Capability Validation
        |
        v
Runtime Identity Credential
        |
        +---- proof of runtime-key possession
        |
        v
Trusted Attestation Statement
        |
        +---- fresh challenge
        +---- verifier audience
        +---- runtime credential digest
        +---- software/config/governance measurements
        |
        v
Qualification Credential
        |
        +---- immutable qualified_profile_digest
        |
        v
Governance Acceptance Evidence
        |
        +---- CoA / VA / policy bindings
        |
        v
Revocation + Freshness Evaluation
        |
        v
Cross-Artifact Context Consistency
        |
        v
VerifiedRuntimeContext
        |
        v
Bounded Authorization
```

---

# 15. Revised `VerifiedRuntimeContext`

Candidate corrected context:

```text
VerifiedRuntimeContext
|
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
+-- revocation_state_epoch
+-- verification_challenge_digest
+-- verification_decision_id
+-- verified_at
+-- valid_until
```

Operational authorization should bind to the digest of this context or the immutable identifiers necessary to reconstruct it.

---

# 16. Required Architecture Revision Before P2

Revise `ATE-RUNTIME-IDENTITY-TRUST-ROOT-ATTESTATION-ARCHITECTURE-v0.1.md` as a surgical v0.1.1 or successor candidate with these requirements:

1. define the attestation signer/trust chain and distinguish attestor signature from runtime proof of possession;
2. introduce immutable `QualifiedRuntimeProfile` and `qualified_profile_digest`;
3. introduce explicit governance-acceptance evidence rather than digest presence alone;
4. define assurance-tier-specific clone resistance and key-protection semantics;
5. add project/application scope and verifier audience binding;
6. define deterministic revocation freshness semantics;
7. define explicit model/provider identity assurance modes;
8. require cross-artifact context binding and mix-and-match rejection;
9. update `VerifiedRuntimeContext` accordingly;
10. update candidate P2 invariants/tests to cover the new bindings.

No implementation is needed for this revision.

---

# 17. Candidate P2 Tests After Revision

Do not freeze these yet. They are a target for the revised architecture.

```text
P2-T0  valid qualified runtime verifies
P2-T1  wrong principal rejected
P2-T2  copied credential without private key rejected
P2-T3  expired runtime credential rejected
P2-T4  stale attestation challenge rejected
P2-T5  substituted software digest rejected
P2-T6  changed configuration profile rejected
P2-T7  changed CoA/VA/policy governance binding rejected
P2-T8  unqualified profile rejected
P2-T9  revoked qualification rejected using fresh revocation state
P2-T10 wrong trust domain rejected
P2-T11 wrong project/audience rejected
P2-T12 runtime restart requires new instance identity
P2-T13 valid artifacts from different runtime instances cannot be mixed
P2-T14 valid qualification for a different qualified profile rejected
P2-T15 self-signed measurement without trusted attestor rejected
P2-T16 copied Tier-1 instance evidence does not receive a stronger assurance claim than Tier 1 permits
P2-T17 unacceptable model-identity assurance mode rejected
P2-T18 governance digest without valid acceptance evidence rejected
P2-T19 stale revocation-state evidence rejected
P2-T20 unknown artifact version rejected
```

A lean P2 should use only the subset necessary to establish the frozen invariants after revision.

---

# 18. What This Review Does Not Require

This review does **not** require:

- TPM integration;
- cloud workload identity;
- production PKI;
- remote multi-host deployment;
- hardware-backed key implementation;
- model-provider agreements;
- distributed revocation infrastructure;
- large-scale behavioral testing.

The purpose is to make the semantics correct before implementation.

---

# 19. Final Review Decision

**Disposition:** `REVISION_REQUIRED_BEFORE_P2_FREEZE`

The runtime identity architecture is strong enough to continue, but P2 should not yet be frozen because the current design does not fully distinguish:

- runtime proof of possession from trusted attestation;
- qualification identity from immutable qualified-profile binding;
- governance document identity from governance acceptance;
- runtime-instance identity from non-clonability assurance;
- organizational trust domain from project/application scope;
- possession of revocation data from sufficiently fresh revocation data;
- model labels from measured/provider-attested model identity;
- individually valid evidence from one coherent cross-artifact verification context.

Correcting these points will make the next P2 experiment materially more valuable and still keep it small.

---

# 20. Architectural Statement

P1 established that authorization can be enforced once trusted principals are assumed.

The runtime-identity layer must now establish **why those principals deserve to be treated as the intended qualified principals in the first place**.

That requires more than identity and more than possession of a private key.

The verifier must establish one coherent proposition:

> **This exact runtime instance, in this trust domain and project scope, currently possesses the expected key, is measured by an accepted attestor, matches the immutable profile that was actually qualified, is operating under the governance set it validly accepted, satisfies current revocation and assurance policy, and is presenting fresh evidence specifically to this verifier.**

Only then should ATE convert trust into authority.

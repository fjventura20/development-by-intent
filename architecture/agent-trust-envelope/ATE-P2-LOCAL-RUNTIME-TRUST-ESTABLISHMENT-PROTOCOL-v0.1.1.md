# ATE P2 Local Runtime Trust Establishment Protocol v0.1.1

**Status:** Revised freeze candidate — DESIGN ONLY  
**Date:** 2026-09-16  
**Program:** Agent Trust Envelope (ATE)  
**Supersedes:** `ATE-P2-LOCAL-RUNTIME-TRUST-ESTABLISHMENT-PROTOCOL-v0.1.md`  
**Controlling architecture:** `ATE-RUNTIME-IDENTITY-TRUST-ROOT-ATTESTATION-ARCHITECTURE-v0.1.1.md`  
**Architecture review:** `ATE-RUNTIME-IDENTITY-ATTESTATION-FINAL-REVIEW-v0.1.md`

---

## 1. Research Question

> **Can a verifier, under a trusted local Tier-1 profile, distinguish the intended currently-qualified runtime instance from specified substituted, stale, copied-without-key, cross-scope, governance-mismatched, profile-mismatched, expired, revoked, or mixed-evidence runtime contexts using one coherent set of cryptographically verifiable evidence?**

P2 tests trust establishment only.

P1 remains the evidence milestone for local protected-resource enforcement.

---

## 2. Lean Experimental Boundary

P2 SHALL use only:

- one local trust domain;
- one project scope;
- one verifier audience;
- one identity issuer;
- one qualification issuer;
- one governance-acceptance authority;
- one trusted local attestor;
- one runtime under test;
- one verifier;
- one local authoritative revocation store;
- one trusted local clock.

No external network, distributed system, premium evaluator, multi-agent replication, or statistical scoring is required.

---

## 3. Explicitly Out of Scope

P2 does not establish:

- root/kernel/trusted-bootstrap compromise resistance;
- issuer compromise resistance;
- hardware-backed non-clonability;
- protection after privileged copying of a Tier-1 runtime private key;
- TPM/TEE/HSM behavior;
- distributed revocation correctness;
- clock-skew tolerance;
- cross-domain federation;
- remote-provider model identity;
- production availability/performance;
- behavioral alignment, moral reasoning, or Value Architecture effectiveness.

---

## 4. Frozen Local Tier-1 Profile

### 4.1 Cryptography

```text
signature_algorithm = Ed25519
digest_algorithm = SHA-256
canonicalization = RFC 8785 JCS
```

### 4.2 Namespace

Implementation SHALL freeze literal values for:

```text
trust_domain_id
project_scope
verifier_audience
```

before the formal run.

### 4.3 Assurance

```text
assurance_tier = 1
model_identity_assurance = LOCAL_MEASURED
key_protection_assurance = SOFTWARE_PROCESS_PROTECTED
attestation_profile = LOCAL_TIER1
```

No stronger assurance claim is permitted.

### 4.4 Revocation

Verifier reads one authoritative local revocation store/epoch during every verification.

No revocation cache is used.

### 4.5 Time

All issuance, validity, attestation freshness, expiration, and verification decisions use one trusted local clock.

---

## 5. Required Signing Roles

The harness SHALL use distinct signing keys and explicit role capabilities for:

```text
Identity Issuer
Qualification Issuer
Governance Acceptance Authority
Trusted Attestor
Runtime Instance
```

A valid trust-root chain does not authorize every role.

Verifier SHALL reject an artifact signed by a trusted key that lacks the required artifact-role capability.

---

## 6. Minimal Evidence Schemas

Every signed artifact SHALL carry:

```text
artifact_type
artifact_version
signature_algorithm
signer_or_issuer_id
```

and SHALL be signed over canonical bytes excluding only the signature field itself.

### 6.1 QualifiedRuntimeProfile

```text
artifact_type = ATE_QUALIFIED_RUNTIME_PROFILE
artifact_version = 1
qualified_profile_id
trust_domain_id
project_scope
principal_id_or_class
software_manifest_digest
configuration_profile_digest
model_identity
model_identity_assurance
coa_digest
value_architecture_digest
policy_bundle_digest
key_protection_assurance
assurance_tier
```

Its canonical SHA-256 digest is `qualified_profile_digest`.

### 6.2 QualificationCredential

```text
artifact_type = ATE_QUALIFICATION_CREDENTIAL
artifact_version = 1
qualification_id
subject_principal_id
qualified_profile_digest
trust_domain_id
project_scope
issued_at
not_before
valid_until
revocation_handle
qualification_issuer_id
```

### 6.3 GovernanceAcceptance

```text
artifact_type = ATE_GOVERNANCE_ACCEPTANCE
artifact_version = 1
acceptance_event_id
principal_id
qualified_profile_digest
trust_domain_id
project_scope
coa_digest
value_architecture_digest
policy_bundle_digest
accepted_at
not_before
valid_until
revocation_handle
governance_authority_id
```

For P2 the governance authority issues this signed credential after a deterministic local acceptance event. UI/human-consent semantics are not under test.

### 6.4 RuntimeIdentityCredential

```text
artifact_type = ATE_RUNTIME_IDENTITY_CREDENTIAL
artifact_version = 1
credential_id
principal_id
runtime_instance_id
runtime_public_key
runtime_public_key_digest
trust_domain_id
project_scope
qualified_profile_digest
software_manifest_digest
configuration_profile_digest
model_identity
model_identity_assurance
key_protection_assurance
assurance_tier
identity_issuer_id
issued_at
not_before
valid_until
revocation_handle
```

### 6.5 AttestationStatement

```text
artifact_type = ATE_ATTESTATION_STATEMENT
artifact_version = 1
attestation_profile
attestor_id
principal_id
runtime_instance_id
runtime_public_key_digest
runtime_identity_credential_digest
trust_domain_id
project_scope
verifier_audience
qualified_profile_digest
software_manifest_digest
configuration_profile_digest
model_identity
model_identity_assurance
coa_digest
value_architecture_digest
policy_bundle_digest
challenge_nonce
issued_at
not_before
valid_until
```

Trusted attestor signs this object.

Runtime self-signature is not a substitute.

### 6.6 RuntimeProofOfPossession

Runtime signs canonical context containing:

```text
runtime_instance_id
runtime_identity_credential_digest
challenge_nonce
verifier_audience
```

with the runtime-instance private key.

### 6.7 RevocationState

```text
revocation_epoch
revoked_runtime_credentials[]
revoked_qualifications[]
revoked_governance_acceptances[]
```

### 6.8 VerifiedRuntimeContext

A successful verifier SHALL create a canonical hash-addressable object containing at least:

```text
verification_decision_id
trust_domain_id
project_scope
verifier_audience
principal_id
runtime_instance_id
runtime_public_key_digest
runtime_identity_credential_digest
attestation_statement_digest
qualified_profile_digest
qualification_credential_digest
governance_acceptance_digest
software_manifest_digest
configuration_profile_digest
model_identity
model_identity_assurance
coa_digest
value_architecture_digest
policy_bundle_digest
assurance_tier
key_protection_assurance
revocation_epoch
verified_at
valid_until
```

---

## 7. Verifier Policy

Formal-run policy SHALL freeze:

```text
expected_trust_domain_id
expected_project_scope
expected_verifier_audience
accepted_identity_issuer
accepted_qualification_issuer
accepted_governance_authority
accepted_attestor
required_assurance_tier = 1
required_key_protection_assurance = SOFTWARE_PROCESS_PROTECTED
required_model_identity_assurance = LOCAL_MEASURED
required_coa_digest
required_value_architecture_digest
required_policy_bundle_digest
maximum_attestation_age
```

The policy and its digest SHALL be preserved in evidence.

---

## 8. Required Verification Procedure

Verifier SHALL fail closed unless all applicable checks succeed:

1. parse mandatory artifacts;
2. validate artifact type/version;
3. canonicalize deterministically;
4. validate signer role capability;
5. verify every mandatory signature;
6. verify `not_before`/`valid_until` for all time-bounded evidence;
7. verify trust domain;
8. verify project scope;
9. verify verifier audience;
10. verify runtime proof of possession;
11. verify trusted attestor signature;
12. verify attestation challenge/freshness;
13. verify runtime credential is current and non-revoked;
14. verify qualification is current and non-revoked;
15. verify governance acceptance is current and non-revoked;
16. verify exact `qualified_profile_digest` linkage;
17. verify exact software digest;
18. verify exact configuration digest;
19. verify exact CoA digest;
20. verify exact Value Architecture digest;
21. verify exact policy bundle digest;
22. verify model identity and assurance mode;
23. verify key-protection assurance and Tier 1;
24. verify all principal/instance/key/digest cross-artifact bindings;
25. create `VerifiedRuntimeContext` only after all checks pass;
26. emit deterministic result/reason codes.

---

## 9. Frozen P2 Invariants

### P2-I1 TRUSTED_ATTESTOR
Measurement truth requires accepted-attestor signature.

### P2-I2 PROOF_OF_POSSESSION
Copied credential without runtime private key cannot verify.

### P2-I3 FRESHNESS
Attestation binds current challenge and permitted verifier audience.

### P2-I4 QUALIFIED_PROFILE
Qualification binds exactly to the immutable qualified profile.

### P2-I5 GOVERNANCE_ACCEPTANCE
CoA/VA/policy bindings require valid current governance-acceptance evidence and profile consistency.

### P2-I6 SOFTWARE_CONFIGURATION_BINDING
Measured software/configuration exactly match the qualified profile.

### P2-I7 SCOPE_BINDING
Trust domain, project scope, and audience satisfy verifier policy.

### P2-I8 TIME_VALIDITY
Expired or not-yet-valid mandatory evidence fails closed.

### P2-I9 REVOCATION
Known-revoked runtime, qualification, or governance evidence fails closed under the authoritative local revocation epoch.

### P2-I10 CROSS_ARTIFACT_CONTEXT
Valid artifacts from distinct runtime/profile contexts cannot be mixed into one verified context.

### P2-I11 RESTART_REIDENTIFICATION
Normal restart creates new instance/key/credential and requires fresh attestation.

### P2-I12 ASSURANCE_BINDING
Model identity assurance, key-protection assurance, and Tier 1 must satisfy policy without upward inference.

### P2-I13 ISSUER_ROLE_BINDING
Root trust alone is insufficient; signer must be authorized for the artifact role.

### P2-I14 UNKNOWN_OR_MALFORMED_FAIL_CLOSED
Unknown mandatory version, malformed field, missing field, or bad mandatory signature fails closed.

### P2-I15 AUTHORIZATION_READY_CONTEXT
Successful verification emits one canonical hash-addressable `VerifiedRuntimeContext`.

---

## 10. Frozen Controlling Test Matrix

P2 freezes exactly **12 controlling tests**.

Variants inside a test are mandatory assertions, not optional exploratory cases.

### P2-T0 — Valid qualified runtime

Construct one fully valid runtime evidence chain.

Expected:

```text
VERIFIED
```

Assert expected principal, runtime instance, qualified profile, governance bindings, assurance values, revocation epoch, and evidence references in `VerifiedRuntimeContext`.

### P2-T1 — Copied credential without runtime private key

Use valid public evidence but wrong runtime private key for proof of possession.

Expected:

```text
REJECTED: PROOF_OF_POSSESSION
```

### P2-T2 — Attestation freshness and authority

Mandatory variants:

A. reuse attestation for a different challenge nonce;
B. replace trusted-attestor signature with runtime/self signature;
C. use expired attestation.

Expected: all REJECTED.

### P2-T3 — Software/configuration substitution

Variants:

A. wrong software digest;
B. wrong configuration digest.

Expected: both REJECTED.

### P2-T4 — Governance acceptance and validity

Variants:

A. CoA/VA/policy digest mismatch;
B. missing/invalid GovernanceAcceptance;
C. expired GovernanceAcceptance;
D. revoked GovernanceAcceptance.

Expected: all REJECTED.

### P2-T5 — Qualification/profile and validity

Variants:

A. valid qualification for different `qualified_profile_digest`;
B. expired qualification;
C. not-yet-valid qualification.

Expected: all REJECTED.

### P2-T6 — Runtime credential validity and revocation

Variants:

A. revoked runtime credential;
B. expired runtime credential;
C. not-yet-valid runtime credential;
D. revoked qualification from otherwise valid baseline.

Expected: all REJECTED.

Record authoritative `revocation_epoch` for revoked variants.

### P2-T7 — Scope and audience isolation

Variants:

A. wrong trust domain;
B. wrong project scope;
C. wrong verifier audience.

Expected: all REJECTED.

### P2-T8 — Mixed valid artifacts

Combine independently valid artifacts from distinct runtime instances/profiles.

At minimum test:

```text
RuntimeIdentityCredential from A
AttestationStatement from B
```

and one qualification/profile cross-mix.

Expected:

```text
REJECTED: CROSS_ARTIFACT_CONTEXT
```

### P2-T9 — Runtime restart reidentification

Create and verify instance A, then perform normal restart/issuance to instance B.

Assert:

- new `runtime_instance_id`;
- new runtime key;
- new runtime credential;
- new attestation required;
- A proof/evidence cannot authenticate B;
- valid B evidence verifies.

### P2-T10 — Assurance and issuer-role enforcement

Variants:

A. unacceptable model-identity assurance;
B. unacceptable key-protection assurance or stronger-tier claim unsupported by evidence;
C. artifact signed by trusted-root descendant without required issuer-role capability.

Expected: all REJECTED.

### P2-T11 — Fail-closed and context integrity

Variants:

A. unknown mandatory artifact version;
B. missing mandatory field;
C. malformed mandatory field;
D. corrupted mandatory signature;
E. valid baseline emits canonical `VerifiedRuntimeContext`;
F. changing any controlling runtime/profile/governance identity changes the context digest.

Expected A-D: REJECTED. Expected E-F: PASS.

---

## 11. Acceptance Rule

Formal success requires:

```text
P2-T0..P2-T11 = 12/12 PASS
all mandatory variants PASS
no protocol deviation
complete evidence
```

No partial-credit scoring.

No evaluator judgment.

No combining results across formal runs.

---

## 12. Formal Run Discipline

A valid formal run requires:

- exact frozen protocol digest recorded;
- one identified implementation commit;
- clean working tree at start;
- frozen verifier policy;
- frozen cryptographic/profile constants;
- one coherent run of all 12 tests;
- machine-readable PASS/FAIL/reason codes;
- all mandatory variants executed;
- no weakening after failure.

Development/preflight runs are not formal evidence.

---

## 13. Stop Conditions

STOP instead of changing the protocol if implementation reveals that:

- trusted attestation cannot be separated from runtime self-assertion;
- proof of possession can be bypassed;
- qualification cannot be bound to immutable profile digest;
- governance acceptance cannot be verified;
- expiration/revocation cannot fail closed;
- scope/audience cannot be enforced;
- mixed valid evidence cannot be rejected;
- a frozen invariant requires redesign.

Mechanical defects may be corrected only if they preserve this protocol exactly.

---

## 14. Evidence Requirements

Formal evidence SHALL include:

```text
protocol SHA-256
implementation commit SHA
working-tree status at run start
cryptographic constants
namespace constants
verifier policy + digest
issuer/signer public keys or key IDs and role capabilities
revocation epoch/state digest
test/variant results for P2-T0..T11
reason codes
input/evidence-object digests
VerifiedRuntimeContext digest for valid cases
formal-run log
```

Historical P1 artifacts/evidence remain untouched.

---

## 15. Classification Vocabulary

### `ATE_P2_LOCAL_RUNTIME_TRUST_ESTABLISHED`

Only if 12/12 tests and all mandatory variants pass in one coherent formal run with no frozen-protocol deviation.

### `ATE_P2_LOCAL_RUNTIME_TRUST_NOT_ESTABLISHED`

Use for genuine controlling invariant/test failure.

### `ATE_P2_INCONCLUSIVE`

Use only when infrastructure/tool failure prevents valid determination without demonstrating an invariant failure.

---

## 16. Success Claim Boundary

A successful P2 establishes only:

> Under the frozen local Tier-1 profile and trusted local roots/issuers/attestor, a verifier can build a coherent cryptographic evidence chain that distinguishes the intended currently-qualified runtime context from the invalid contexts enumerated by this protocol.

It does not establish full production ATE security.

---

## 17. Relationship to P1

```text
P2:
Evidence -> VerifiedRuntimeContext

P1:
Trusted principal + bounded authorization -> enforced protected mutation
```

The future composition is:

```text
Runtime Evidence
      |
      v
VerifiedRuntimeContext
      |
      v
Bounded Authorization
      |
      v
P1 Enforcement Plane
```

P2 SHALL stop at `VerifiedRuntimeContext`; it need not reproduce the P1 resource harness.

---

## 18. Quota Conservation

P2 is an engineering conformance test, not a behavioral evaluation.

Default execution budget:

1. local implementation;
2. deterministic preflight/unit checks;
3. one formal 12-test run;
4. adjudication and stop.

Do not add premium model evaluators, independent model scoring, multi-agent replication, or repeated statistical generations unless a later PI decision explicitly changes the research question.

---

## 19. Freeze Candidate Status

This v0.1.1 artifact supersedes v0.1 and corrects the missing direct expiration/governance-revocation coverage found during freeze review.

No implementation is authorized until a final protocol freeze record confirms this exact artifact is accepted and records its immutable SHA-256/commit identity.

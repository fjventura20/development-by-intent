# ATE P2 Local Runtime Trust Establishment Protocol v0.1

**Status:** Freeze candidate — DESIGN ONLY  
**Date:** 2026-09-16  
**Program:** Agent Trust Envelope (ATE)  
**Predecessor evidence:** ATE P1 Local Enforcement  
**Controlling architecture:** `ATE-RUNTIME-IDENTITY-TRUST-ROOT-ATTESTATION-ARCHITECTURE-v0.1.1.md`  
**Final architecture review:** `ATE-RUNTIME-IDENTITY-ATTESTATION-FINAL-REVIEW-v0.1.md`

---

# 1. P2 Research Question

> **Can a verifier, under a trusted local Tier-1 trust profile, distinguish the intended currently-qualified runtime instance from specified substituted, stale, copied-without-key, cross-scope, governance-mismatched, profile-mismatched, revoked, or mixed-evidence runtime contexts using only cryptographically verifiable evidence?**

P2 tests trust establishment.

P2 does **not** test protected-resource enforcement; P1 already addressed that layer.

---

# 2. Scope

P2 is intentionally local, deterministic, and inexpensive.

It SHALL use:

- one local trust domain;
- one local project scope;
- one identity issuer;
- one qualification issuer;
- one governance acceptance recorder/issuer;
- one trusted local attestor;
- one verifier;
- one runtime under test;
- one local authoritative revocation store;
- one trusted local clock.

No network distribution is required.

No premium-model evaluator is required.

No multi-agent replication is required.

---

# 3. Out of Scope

P2 SHALL NOT claim or test:

- root compromise resistance;
- trusted-bootstrap compromise resistance;
- issuer compromise resistance;
- kernel compromise resistance;
- TPM/TEE/HSM integration;
- hardware-backed non-clonability;
- protection after privileged runtime private-key copying;
- distributed revocation;
- clock-skew tolerance;
- cross-domain federation;
- remote provider model attestation;
- production availability;
- performance;
- behavioral alignment or Value Architecture effectiveness.

P2 verifies evidence binding, not model morality or behavior.

---

# 4. Local Tier-1 Trust Profile

P2 SHALL freeze the following local profile.

## 4.1 Cryptography

```text
signature_algorithm = Ed25519
digest_algorithm = SHA-256
canonicalization = RFC 8785 JCS (or byte-identical frozen implementation)
```

Unknown algorithms fail closed.

## 4.2 Trust namespace

Use fixed values such as:

```text
trust_domain_id = ate-local-p2
project_scope = ate-p2-runtime-trust
verifier_audience = ate-p2-verifier
```

The exact literal values MAY differ, but they SHALL be frozen in implementation/evidence before the formal run.

## 4.3 Model identity assurance

```text
model_identity_assurance = LOCAL_MEASURED
```

No remote provider claim is required.

## 4.4 Key protection

```text
key_protection_assurance = SOFTWARE_PROCESS_PROTECTED
```

P2 makes no stronger claim.

## 4.5 Revocation

Use one local authoritative revocation epoch/store directly readable by the verifier.

No cache staleness is introduced.

## 4.6 Time

One local trusted clock controls all validity/freshness checks.

---

# 5. Principals and Roles

P2 SHALL logically separate these roles even if a test harness hosts some roles in one process during development.

```text
Root Trust Policy
      |
      +-- Identity Issuer
      +-- Qualification Issuer
      +-- Governance Acceptance Authority
      +-- Trusted Attestor
      |
      v
Runtime Under Test
      |
      v
Verifier
```

The formal harness MUST preserve separate signing keys and explicit issuer-role capabilities.

A key authorized for one role MUST NOT automatically be valid for another.

---

# 6. Frozen Evidence Objects

The harness SHALL implement the following minimal evidence objects.

Fields not required by P2 MAY be omitted.

All signed objects SHALL include:

```text
artifact_type
artifact_version
signature_algorithm
issuer_id / signer_id
```

---

## 6.1 QualifiedRuntimeProfile

Minimum fields:

```text
artifact_type = ATE_QUALIFIED_RUNTIME_PROFILE
artifact_version = 1
qualified_profile_id
trust_domain_id
project_scope
principal_id or principal_class
software_manifest_digest
configuration_profile_digest
model_identity
model_identity_assurance
coa_digest
value_architecture_digest
policy_bundle_digest
key_protection_assurance
assurance_tier = 1
```

Canonical digest:

```text
qualified_profile_digest
```

---

## 6.2 QualificationCredential

Minimum fields:

```text
artifact_type = ATE_QUALIFICATION_CREDENTIAL
artifact_version = 1
qualification_id
subject_principal_id
qualified_profile_digest
trust_domain_id
project_scope
issued_at
valid_until
revocation_handle
qualification_issuer_id
```

Signed by qualification issuer.

---

## 6.3 GovernanceAcceptance

Minimum fields:

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
valid_until
```

Signed by the authorized governance acceptance authority after a deterministic local acceptance event.

P2 does not test UI semantics of acceptance.

---

## 6.4 RuntimeIdentityCredential

Minimum fields:

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
assurance_tier = 1
identity_issuer_id
issued_at
not_before
valid_until
revocation_handle
```

Signed by identity issuer.

---

## 6.5 AttestationStatement

Minimum fields:

```text
artifact_type = ATE_ATTESTATION_STATEMENT
artifact_version = 1
attestation_profile = LOCAL_TIER1
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
valid_until
```

Signed by trusted attestor.

The runtime MUST NOT be able to satisfy this requirement solely with its runtime private key.

---

## 6.6 RuntimeProofOfPossession

Minimum fields/context:

```text
runtime_instance_id
runtime_identity_credential_digest
challenge_nonce
verifier_audience
```

Signed by runtime instance private key.

---

## 6.7 RevocationState

Minimum state:

```text
revocation_epoch
revoked_runtime_credentials[]
revoked_qualifications[]
revoked_governance_acceptances[]
```

The verifier reads the authoritative local state during each verification.

---

## 6.8 VerificationDecisionRecord

Minimum fields:

```text
verification_decision_id
result = VERIFIED | REJECTED
reason_codes[]
principal_id?
runtime_instance_id?
qualified_profile_digest?
runtime_identity_credential_digest?
attestation_statement_digest?
qualification_credential_digest?
governance_acceptance_digest?
revocation_epoch
verified_at
valid_until?
```

The record SHALL be deterministic for equivalent inputs except for identifiers/timestamps explicitly declared variable.

---

# 7. Verifier Policy

The frozen P2 verifier policy SHALL require:

```text
expected_trust_domain_id
expected_project_scope
expected_verifier_audience
accepted_identity_issuer
accepted_qualification_issuer
accepted_governance_acceptance_authority
accepted_attestor
required_assurance_tier = 1
required_key_protection_assurance = SOFTWARE_PROCESS_PROTECTED
required_model_identity_assurance = LOCAL_MEASURED
required_coa_digest
required_value_architecture_digest
required_policy_bundle_digest
maximum_attestation_age / validity
```

Exact values SHALL be recorded in evidence.

---

# 8. Verification Algorithm

The verifier SHALL perform, at minimum, this sequence:

1. parse all mandatory objects;
2. reject unknown mandatory artifact types/versions;
3. canonicalize using the frozen method;
4. validate issuer/signer role capability;
5. validate all mandatory signatures;
6. validate time bounds;
7. validate trust domain;
8. validate project scope;
9. validate verifier audience;
10. validate runtime proof of possession;
11. validate trusted attestor signature;
12. validate challenge freshness/equality;
13. validate qualification non-revoked/current;
14. validate runtime credential non-revoked/current;
15. validate governance acceptance non-revoked/current;
16. validate `qualified_profile_digest` linkage;
17. validate exact software digest match;
18. validate exact configuration digest match;
19. validate exact CoA digest match;
20. validate exact Value Architecture digest match;
21. validate exact policy bundle digest match;
22. validate model identity and assurance mode;
23. validate key-protection/assurance tier;
24. validate all cross-artifact instance/principal/key/digest bindings;
25. construct `VerifiedRuntimeContext` only if every required check passes;
26. emit verification decision record.

Any mandatory verification failure SHALL fail closed.

---

# 9. Frozen P2 Invariants

### P2-I1 — TRUSTED_ATTESTOR

Measurement truth requires an attestation signed by the accepted attestor.

### P2-I2 — PROOF_OF_POSSESSION

A copied runtime credential without the runtime private key cannot verify.

### P2-I3 — FRESHNESS

Attestation must bind the current verifier challenge and permitted audience.

### P2-I4 — QUALIFIED_PROFILE

Qualification must bind to the exact immutable qualified profile used by the runtime context.

### P2-I5 — GOVERNANCE_ACCEPTANCE

Required CoA/VA/policy bindings require valid governance acceptance evidence and must match the qualified profile.

### P2-I6 — SOFTWARE_CONFIGURATION_BINDING

Measured software and configuration must exactly match the P2 qualified profile.

### P2-I7 — SCOPE_BINDING

Trust domain, project scope, and verifier audience must satisfy policy.

### P2-I8 — REVOCATION

Known-revoked mandatory runtime/qualification/governance evidence fails closed using the authoritative local revocation state.

### P2-I9 — CROSS_ARTIFACT_CONTEXT

Individually valid artifacts from different runtime contexts cannot be combined into a verified context.

### P2-I10 — RESTART_REIDENTIFICATION

A normal runtime restart creates a new runtime instance/key/credential; stale prior-instance proof cannot verify the new instance.

### P2-I11 — ASSURANCE_BINDING

Model identity assurance, key-protection assurance, and assurance tier must satisfy policy without upward inference.

### P2-I12 — AUTHORIZATION_READY_CONTEXT

Successful verification produces a canonical `VerifiedRuntimeContext` suitable for binding into a later authorization decision.

---

# 10. Controlling Test Matrix

P2 freezes **12 controlling tests**.

Each test may contain multiple assertions, but all assertions for that test must pass.

## P2-T0 — Valid qualified runtime

Construct one valid runtime/evidence chain.

Expected:

```text
VERIFIED
```

Verify the resulting context contains the expected principal, runtime instance, qualified profile, governance digests, assurance tier, and evidence references.

## P2-T1 — Copied credential without runtime private key

Present a valid runtime identity credential and other valid evidence but sign proof of possession with the wrong key.

Expected:

```text
REJECTED: PROOF_OF_POSSESSION
```

## P2-T2 — Stale/replayed attestation

Reuse an attestation generated for a different challenge nonce.

Expected:

```text
REJECTED: ATTESTATION_FRESHNESS
```

Also assert that the runtime cannot replace the attestor signature with a self-signature to make the stale evidence valid.

## P2-T3 — Software/configuration substitution

Run two variants:

A. wrong software manifest digest;
B. wrong configuration profile digest.

Expected for both:

```text
REJECTED
```

No qualified-profile compatibility inference is permitted.

## P2-T4 — Governance mismatch or missing acceptance

Run two variants:

A. active runtime evidence references wrong CoA/VA/policy digest;
B. correct digests are present but GovernanceAcceptance is missing/invalid.

Expected for both:

```text
REJECTED
```

## P2-T5 — Qualification/profile mismatch

Present a valid qualification credential for a different `qualified_profile_digest`.

Expected:

```text
REJECTED: QUALIFIED_PROFILE_MISMATCH
```

## P2-T6 — Revocation

After baseline validity, revoke the qualification or runtime credential in the authoritative local revocation state.

Expected:

```text
REJECTED: REVOKED
```

Record the revocation epoch used by verification.

## P2-T7 — Scope/audience isolation

Run three variants:

A. wrong trust domain;
B. wrong project scope;
C. attestation for wrong verifier audience.

Expected for each:

```text
REJECTED
```

## P2-T8 — Mixed valid artifacts

Combine individually valid artifacts from two different runtime instances or profiles.

At least one mix SHALL include:

```text
runtime credential from A
attestation or qualification context from B
```

Expected:

```text
REJECTED: CROSS_ARTIFACT_CONTEXT
```

## P2-T9 — Runtime restart reidentification

Create runtime instance A, verify it, then perform a normal restart/issuance producing instance B.

Assert:

- B has new `runtime_instance_id`;
- B has new runtime key;
- B requires new runtime credential/attestation;
- old A proof/evidence cannot verify B.

Expected new B chain:

```text
VERIFIED
```

Expected stale A-as-B attempt:

```text
REJECTED
```

## P2-T10 — Assurance and issuer-role enforcement

Run variants sufficient to prove:

A. unacceptable model identity assurance rejected;
B. unacceptable key-protection/assurance tier rejected;
C. artifact signed by a trusted-root descendant lacking the required issuer-role capability rejected.

Expected:

```text
REJECTED
```

## P2-T11 — Fail-closed/version and authorization-ready context

A. unknown mandatory artifact version -> REJECTED;
B. malformed/missing mandatory field -> REJECTED;
C. valid baseline -> VERIFIED and emits canonical hash-addressable `VerifiedRuntimeContext`.

The context digest SHALL change when a controlling runtime/profile/governance identity changes.

---

# 11. Formal Acceptance Rule

P2 requires:

```text
12 / 12 controlling tests PASS
```

All required variants/assertions inside each test must pass.

No partial-credit scoring.

No evaluator judgment is required.

Tests SHALL return deterministic machine-readable PASS/FAIL plus reason codes.

---

# 12. Stop Conditions

Implementation/execution SHALL STOP rather than modify the frozen protocol if:

- trusted attestation cannot be separated from runtime self-assertion;
- qualification cannot be bound to an immutable profile;
- governance acceptance cannot be represented as verifiable evidence;
- mixed valid artifacts cannot be reliably rejected;
- proof-of-possession can be bypassed;
- scope/audience cannot be bound cryptographically;
- verification requires weakening a frozen invariant;
- a failed controlling test reveals an architectural contradiction.

Mechanical implementation bugs may be corrected only if the fix clearly conforms to this protocol.

---

# 13. Evidence Requirements

A formal run SHALL preserve:

```text
P2 protocol artifact digest
implementation commit SHA
cryptographic/profile constants
verifier policy
issuer public keys/key IDs
test-case inputs or deterministic generators
all P2-T0..P2-T11 results
reason codes
evidence-object digests
VerifiedRuntimeContext digest for valid cases
formal-run log
```

Evidence filenames should be new and P2-specific.

Historical P1 evidence must remain untouched.

---

# 14. Formal Run Discipline

A valid formal run requires:

- frozen protocol unchanged;
- one identified implementation commit;
- clean working tree at run start;
- all 12 controlling tests run in one coherent formal run;
- no combining PASS results across runs;
- no test weakening after failure;
- no omitted variants/assertions;
- deterministic reason codes.

---

# 15. Classification Vocabulary

Only the following final classifications are permitted.

## `ATE_P2_LOCAL_RUNTIME_TRUST_ESTABLISHED`

Allowed only when:

```text
12/12 controlling tests PASS
no frozen-protocol deviation
formal evidence complete
```

## `ATE_P2_LOCAL_RUNTIME_TRUST_NOT_ESTABLISHED`

Used when a genuine controlling invariant/test fails.

## `ATE_P2_INCONCLUSIVE`

Used only when infrastructure/tool failure prevents a valid formal determination without demonstrating an invariant failure.

---

# 16. Interpretation of Success

P2 success would establish only this bounded result:

> Under the frozen local Tier-1 trust profile, a verifier can construct and validate a coherent cryptographic evidence chain that distinguishes the intended currently-qualified runtime context from the specified invalid/substituted contexts.

P2 success would NOT establish full production ATE security.

---

# 17. Relationship to P1

P1 proved:

```text
trusted principals
  -> bounded authorization can be enforced
```

P2 is intended to prove:

```text
runtime evidence
  -> intended qualified principal can be verified
```

Together:

```text
verify qualified runtime
        |
        v
VerifiedRuntimeContext
        |
        v
bounded authorization
        |
        v
P1-style enforcement
```

---

# 18. Quota-Conservation Rule

P2 SHALL be executed without premium multi-agent replication unless the initial formal run yields an ambiguity that deterministic local evidence cannot resolve.

Default execution strategy:

1. implementation review locally;
2. deterministic unit/preflight checks;
3. one formal 12-test run;
4. stop and adjudicate.

Do not add evaluators, candidate generations, statistical repetitions, or independent model scoring to an engineering conformance experiment.

---

# 19. Freeze Status

This artifact is a **freeze candidate**.

No implementation is authorized until a final protocol review confirms:

- schemas are sufficient;
- tests map to invariants;
- success claims are bounded correctly;
- no test silently depends on stronger-than-Tier-1 properties.

Upon review acceptance, freeze this exact artifact digest or produce a byte-identical frozen copy/status record before implementation.

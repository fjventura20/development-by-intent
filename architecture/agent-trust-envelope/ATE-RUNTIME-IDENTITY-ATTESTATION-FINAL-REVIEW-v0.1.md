# ATE Runtime Identity / Attestation Final Review v0.1

**Status:** Final adversarial review  
**Date:** 2026-09-16  
**Reviewed artifact:** `ATE-RUNTIME-IDENTITY-TRUST-ROOT-ATTESTATION-ARCHITECTURE-v0.1.1.md`  
**Prior review:** `ATE-RUNTIME-IDENTITY-ATTESTATION-ADVERSARIAL-REVIEW-v0.1.md`  
**Disposition:** `READY_FOR_P2_FREEZE`

---

## 1. Review Decision

The v0.1.1 revision resolves the blocking findings from the first adversarial review sufficiently to freeze a lean local P2 experiment.

No further architecture revision is required before P2 design freeze.

The following are now adequately separated and bound:

- runtime key possession vs trusted measurement attestation;
- qualification ID vs immutable qualified runtime profile;
- governance document digest vs governance acceptance evidence;
- runtime identity vs clone-resistance assurance tier;
- trust domain vs project/application scope;
- credential validity vs revocation freshness;
- model label vs model-identity assurance mode;
- proof of possession vs key-protection assurance;
- individually valid artifacts vs one coherent cross-artifact verification context.

---

## 2. Accepted Core Trust Proposition

P2 may now test the following proposition:

> A verifier can distinguish a valid qualified runtime instance from a substituted, copied-without-key, stale, cross-project, governance-mismatched, profile-mismatched, or otherwise invalid runtime by evaluating one coherent set of signed identity, trusted attestation, qualification, governance-acceptance, proof-of-possession, and revocation evidence.

The proposition is deliberately limited to the local Tier-1 assurance profile.

---

## 3. Mandatory P2 Profile Simplifications

To keep P2 lean and prevent infrastructure work from overwhelming the research question, P2 SHALL use these explicit simplifications.

### 3.1 Local trust domain

One local trust domain and one project scope.

Cross-domain federation is not tested.

### 3.2 Trusted local attestor

Use one trusted local attestor/bootstrap principal whose signing key is trusted by the verifier.

P2 tests attestation semantics, not TPM/TEE hardware.

### 3.3 Exact profile matching

For P2:

- software manifest constraint = exact digest match;
- configuration profile = exact digest match;
- CoA digest = exact match;
- Value Architecture digest = exact match;
- policy bundle digest = exact match;
- project scope = exact string match;
- verifier audience = exact string match.

No compatibility ranges or wildcard scope semantics are required.

### 3.4 Local authoritative revocation

Use one local authoritative revocation store/epoch.

No distributed stale-cache behavior is tested.

### 3.5 Trusted local clock

All issuance and verification use one trusted local clock.

Clock skew is out of scope.

### 3.6 Tier-1 key protection

Runtime keys are software-process-protected.

P2 MUST NOT claim hardware-backed non-exportability or clone resistance after privileged key copying.

### 3.7 Model identity

Use `LOCAL_MEASURED` for the P2 runtime model/software identity where applicable.

Remote provider attestation is out of scope.

### 3.8 Cryptographic profile

A single deterministic local profile is sufficient:

- Ed25519 signatures;
- SHA-256 digests;
- RFC 8785 JCS or one equivalently frozen canonical JSON representation;
- explicit artifact type/version fields.

P2 is not an algorithm-agility experiment.

---

## 4. Governance Acceptance Clarification

For P2, `GovernanceAcceptance` SHALL be accepted only when its evidence source is unambiguous.

Use one of these equivalent local mechanisms:

1. principal/runtime signs a canonical acceptance statement and an authorized governance recorder countersigns/records it; or
2. an authorized governance authority issues a signed acceptance credential after observing/verifying the principal acceptance event.

A bare database field or an unsigned statement is insufficient.

The acceptance evidence MUST bind:

```text
principal_id
qualified_profile_digest
coa_digest
value_architecture_digest
policy_bundle_digest
project_scope
acceptance_event_id
```

P2 need not test human-interface acceptance semantics; it tests cryptographic/evidentiary binding.

---

## 5. Attestation Clarification

For P2, the trusted attestor signs the measurement statement.

The runtime separately signs the verifier challenge to prove runtime-key possession.

These signatures MUST be independently verified.

The attestation statement MUST bind at minimum:

```text
challenge_nonce
verifier_audience
trust_domain_id
project_scope
principal_id
runtime_instance_id
runtime_public_key_digest
runtime_identity_credential_digest
software_manifest_digest
configuration_profile_digest
qualified_profile_digest
governance_profile_digest
```

This is sufficient to test separation between identity/key possession and trusted measurement claims.

---

## 6. Cross-Artifact Verification Requirement

P2 verification MUST construct one coherent context rather than merely verify signatures.

The verifier MUST reject any combination in which required fields or referenced digests disagree across:

- runtime identity credential;
- attestation statement;
- qualification credential;
- qualified runtime profile;
- governance acceptance evidence;
- revocation state;
- runtime proof-of-possession response.

This is a controlling P2 invariant.

---

## 7. Assurance Claim Boundary

A successful P2 may establish:

> Under a trusted local bootstrap/attestor and issuer set, a verifier can cryptographically distinguish the intended currently-qualified Tier-1 runtime context from specified invalid/substituted contexts.

It may NOT establish:

- hardware-backed runtime identity;
- protection after root/trusted-bootstrap compromise;
- non-clonability after privileged runtime-key copying;
- remote provider model identity;
- distributed revocation correctness;
- cross-domain federation correctness;
- production availability or operations readiness.

These boundaries must appear in P2 evidence and closeout.

---

## 8. P2 Freeze Guidance

P2 should test the minimum set of failure modes necessary to establish the accepted v0.1.1 invariants.

Avoid converting every architecture statement into a separate premium-model experiment.

A recommended controlling matrix is approximately 10–12 tests, with no dual evaluator, no multi-agent replication, and no distributed infrastructure unless a failure specifically requires expansion.

P2 is an engineering verification experiment, not a statistical behavioral study.

---

## 9. Final Disposition

**`READY_FOR_P2_FREEZE`**

The runtime identity architecture has passed the required adversarial design cycle.

The next artifact should be:

**ATE P2 Local Runtime Trust Establishment Protocol v0.1**

It should freeze:

- the local Tier-1 trust profile;
- evidence schemas used by the harness;
- verifier policy;
- invariants;
- minimal controlling tests;
- explicit stop conditions;
- evidence and classification rules.

Implementation remains unauthorized until that protocol itself is reviewed and frozen.

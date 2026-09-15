# ATE Trust Root & Key Custody Model v0.1

## 1. Purpose

This document defines the trust-root, signing-authority, and key-custody architecture required for a production Agent Trust Envelope (ATE) system.

ATE depends on signed evidence, signed policies, signed authorization, and signed trust decisions. Those signatures are meaningful only if the system can answer four questions deterministically:

1. **Who is allowed to sign this artifact type?**
2. **Which public key currently represents that authority?**
3. **How is the corresponding private key protected?**
4. **How is authority removed when a key, issuer, or role is no longer trusted?**

The governing principle is:

> A valid signature proves possession of a key. It does not, by itself, prove authority.

ATE therefore separates **cryptographic validity** from **authorization to attest**.

---

## 2. Scope

This model covers:

- trust roots
- issuer roles
- authority registration
- public-key discovery
- private-key custody
- key isolation
- key rotation
- revocation
- compromise response
- artifact signing authorization
- trust-domain boundaries
- separation of duties
- audit requirements
- assurance profiles

This version does not define:

- a specific PKI product
- a specific HSM vendor
- cloud-specific IAM configuration
- certificate transparency infrastructure
- cross-organization federation protocol
- threshold cryptography implementation
- hardware attestation protocol

Those remain deployment choices or future architecture work.

---

## 3. Core Trust Principle

Every ATE artifact must satisfy both:

```text
CRYPTOGRAPHICALLY_VALID
AND
ISSUER_AUTHORIZED_FOR_ARTIFACT_TYPE
```

The second condition is mandatory.

For example, an agent identity key may be valid for proving runtime identity but must not be accepted as a Trust Decision Authority key.

Similarly, a Behavioral Evidence Authority may attest behavioral evidence but must not issue CapabilityTokens unless separately authorized for that role.

No key has universal authority by default.

---

## 4. Authority Roles

ATE Production Architecture v0.1 defines the following signing roles.

### R1 — Trust Root Authority

Authorizes subordinate authorities and trust-domain membership.

May sign:

- Trust Root Registry versions
- authority registration records
- authority revocation records
- trust-domain metadata

Must not normally sign ordinary runtime or transaction artifacts.

### R2 — Identity / Runtime Authority

Establishes agent/runtime identity and related runtime provenance.

May sign:

- identity credentials
- runtime identity receipts
- session identity evidence where defined

### R3 — Governance / COA Authority

Attests Condition of Agency governance artifacts.

May sign:

- COA definitions
- COA acceptance receipts
- governance-status artifacts

### R4 — Value Architecture Policy Authority

Publishes and activates governing Value Architecture policies.

May sign:

- VA policy artifacts
- active-policy manifests
- policy supersession records

### R5 — Behavioral Evidence Authority

Attests behavioral evaluation results.

May sign:

- BehavioralEvidenceReceipt
- evaluation-result references
- behavioral-evidence freshness assertions

### R6 — Authorization Authority

Issues least-privilege CapabilityTokens.

May sign:

- CapabilityToken
- authorization revocations
- capability constraints

### R7 — ATE Verification Authority

May sign verification evidence where production deployment separates evidence verification from trust-decision issuance.

May sign:

- VerificationReceipt
- gate-result summaries

### R8 — Trust Decision Authority

Signs deterministic ATE trust decisions.

May sign:

- TRUST_GRANTED decisions
- TRUST_DENIED decisions

This authority must remain outside the participant agent's authority boundary.

### R9 — Capability Executor Identity

Authenticates the enforcement component to credential stores and protected resources.

May authenticate execution requests and audit events, but does not grant trust.

### R10 — Audit Authority

Signs append-only audit records or audit checkpoints.

---

## 5. Separation of Duties

ATE should minimize role concentration.

The strongest default is:

```text
participant identity authority
!= governance authority
!= authorization authority
!= trust-decision authority
!= executor identity
```

Absolute separation is not mandatory for every low-risk deployment, but role collapse must be explicit and risk-classified.

The critical prohibitions are:

1. The participant agent must not hold the Trust Decision Authority private key.
2. The participant agent must not hold the protected resource credentials used by the Capability Executor.
3. A Trust Decision Authority must not automatically inherit policy-authority powers.
4. An Authorization Authority must not automatically inherit Trust Root powers.
5. A compromised single operational key should not silently redefine the entire trust system.

---

## 6. Trust Root Registry

The Trust Root Registry is the authoritative mapping from issuer identity to allowed signing roles.

Minimum entry:

```text
TrustRootEntry {
    authority_id
    trust_domain

    public_key_id
    public_key
    algorithm

    permitted_artifact_types[]
    permitted_roles[]

    valid_from
    valid_until

    status
    revocation_reference

    metadata_digest
}
```

The registry itself must be signed by the Trust Root Authority.

A verifier must reject an otherwise valid artifact if:

- the issuer is unknown
- the key is not current
- the issuer is not authorized for that artifact type
- the authority is suspended or revoked
- the signing key is outside its validity interval
- the trust domain is unacceptable for the requested action

---

## 7. Root-of-Trust Hierarchy

A minimal production hierarchy is:

```text
Trust Root Authority
        |
        +--> Policy Authority
        +--> Governance Authority
        +--> Behavioral Evidence Authority
        +--> Authorization Authority
        +--> Trust Decision Authority
        +--> Audit Authority
```

Runtime identity may be subordinate to either the same trust root or a separately recognized identity root.

The architecture must permit multiple roots, but trust must remain explicit.

No authority should become trusted merely because another untrusted authority references it.

---

## 8. Root Key Custody

The Trust Root Authority is the highest-impact key in the system.

Compromise can permit an attacker to redefine trusted issuers.

Therefore the root private key should be:

- offline by default
- used rarely
- protected separately from participant and executor infrastructure
- recoverable through documented governance
- subject to multi-person control for high-assurance profiles

Recommended production pattern:

```text
Offline Root Key
      |
      +--> signs limited-lived operational authority keys
```

The root key should not sign ordinary ATE decisions.

---

## 9. Operational Authority Keys

Operational signing should be performed by subordinate keys with narrow purposes.

Examples:

```text
K_POLICY
K_GOVERNANCE
K_BEHAVIORAL
K_AUTHORITY
K_VERIFY
K_TRUST_DECISION
K_AUDIT
```

Each key must have:

- a stable key identifier
- an authority identifier
- a permitted role set
- a creation time
- an activation time
- an expiration or rotation policy
- revocation status
- custody classification

---

## 10. Key Identifiers

Artifacts should not identify a key solely by the raw public key.

Use a stable identifier such as:

```text
key_id = SHA256(canonical_public_key_metadata)
```

or an equivalent cryptographically unique identifier.

Artifacts should bind:

```text
issuer_id
key_id
algorithm
```

The verifier resolves `key_id` against the current Trust Root Registry.

---

## 11. Key Custody Classes

ATE defines four custody classes.

### KC0 — Development Fixture

Examples:

- test keys in a local PoC
- ephemeral unit-test keys

Permitted only for non-production environments.

### KC1 — Software-Protected Operational Key

Private key stored in protected software secret storage.

Suitable for low-to-moderate risk environments if host security is acceptable.

### KC2 — Isolated Service / Managed Key

Private key stored in a managed signing service, OS-protected keystore, TPM, Secure Enclave, KMS, or equivalent protected boundary.

The application requests signing without directly retrieving key material.

Preferred for production operational authorities.

### KC3 — Hardware-Backed / Multi-Party Root

Private key held in HSM or equivalent high-assurance custody, potentially requiring quorum or multi-person approval.

Recommended for:

- Trust Root Authority
- critical Policy Authority
- critical Trust Decision Authority
- high-risk Authorization Authority

---

## 12. Private-Key Non-Exportability

For KC2 and KC3 deployments, private keys should ideally be non-exportable.

Desired interface:

```text
sign(key_id, artifact_digest)
```

Not:

```text
get_private_key(key_id)
```

ATE components should not need direct access to private key material when a protected signing service is available.

---

## 13. Participant Key Boundary

The participant agent/runtime may possess only keys required to establish its own identity or ephemeral session provenance.

It must not possess:

- Trust Root private key
- Policy Authority private key
- Authorization Authority private key
- Trust Decision Authority private key
- Capability Executor resource credentials

This preserves the distinction between claimant and authority.

---

## 14. Trust Decision Key Custody

`K_TRUST_DECISION` is one of the most security-sensitive operational keys because compromise permits forged `TRUST_GRANTED` results.

Minimum requirements:

- inaccessible to participant agent
- inaccessible to arbitrary prompt/model context
- accessible only through deterministic trust-decision service logic
- protected from direct generic signing requests
- signing API limited to canonical TrustDecision structures
- audit event emitted for every signature

A generic endpoint such as:

```text
sign_anything(bytes)
```

must not be exposed to the participant or verifier.

Preferred interface:

```text
issue_trust_decision(verified_inputs)
```

where the signing operation is structurally constrained.

---

## 15. Signing-Oracle Prevention

Possession of a protected key is insufficient if an attacker can trick the service into signing arbitrary content.

Each signing authority must enforce artifact-domain separation.

For example:

```text
ATE_TRUST_DECISION_V1 || canonical_payload
ATE_CAPABILITY_TOKEN_V1 || canonical_payload
ATE_BEHAVIORAL_RECEIPT_V1 || canonical_payload
```

A signature created for one domain must not verify as another artifact class.

Signing services should validate:

- artifact type
- schema version
- required fields
- issuer role
- domain separator

before invoking the private key.

---

## 16. Algorithm Policy

The Trust Root Registry should identify allowed algorithms.

Production ATE should avoid accepting arbitrary caller-selected algorithms.

Example policy:

```text
allowed_algorithms:
  - Ed25519
```

or another approved set.

Unknown or deprecated algorithms fail closed.

Algorithm migration must be explicit and versioned.

---

## 17. Rotation

All operational keys require a defined rotation process.

Rotation must distinguish:

- planned rotation
- expiration
- emergency compromise rotation

A planned rotation should permit temporary overlap:

```text
K_old: valid until T2
K_new: valid from T1
T1 < T2
```

During the overlap, both keys may verify where policy permits.

New artifacts should switch to `K_new` at the defined activation time.

---

## 18. Rotation Does Not Imply Revocation

An old key may remain valid for verifying historical evidence after it stops signing new artifacts.

Therefore distinguish:

```text
SIGNING_ACTIVE
VERIFY_ONLY
REVOKED
EXPIRED
```

Historical audit reconstruction may require access to retired public keys indefinitely.

---

## 19. Compromise Revocation

If a private key may have been compromised, `VERIFY_ONLY` is not sufficient.

The key must enter:

```text
REVOKED
```

with:

- revocation time
- compromise reason
- replacement key reference
- scope of affected artifacts

The system must then determine which previously signed artifacts remain acceptable.

For high-risk authorities, compromise may invalidate all artifacts signed after a defined compromise boundary.

---

## 20. Artifact-Level Revocation vs Key-Level Revocation

ATE must support both.

### Key-level revocation

Rejects trust in a signing key.

### Artifact-level revocation

Rejects one specific credential, policy, receipt, token, or decision while leaving the issuer key trusted.

This distinction is essential.

A mistaken CapabilityToken should not require revoking the entire Authorization Authority key.

---

## 21. Trust Root Changes

Changes to the Trust Root Registry are security-critical events.

Production should require stronger controls than ordinary ATE transactions.

Recommended requirements:

- signed registry version
- monotonically increasing registry epoch
- previous-registry hash
- human/operator review
- append-only audit
- delayed activation for non-emergency changes
- emergency process for compromise

High-assurance profiles should use multi-party approval.

---

## 22. Registry Epoch

Every production trust decision should bind or reference the trust-root state used during verification.

Example:

```text
trust_registry_epoch
trust_registry_digest
```

This permits later reconstruction of:

> Which authorities were trusted when this action was authorized?

Without this, historical verification becomes ambiguous after registry changes.

---

## 23. Policy Authority Custody

The Policy Authority determines which Value Architecture policy is current.

Compromise can legitimize malicious policy.

Therefore:

- policy signing should be isolated from participant systems
- production policy publication should be audited
- critical policy changes should require human approval
- high-risk environments should support delayed activation or quorum approval

The Policy Authority should not normally issue CapabilityTokens or trust decisions.

---

## 24. Authorization Authority Custody

The Authorization Authority controls maximum capability scope.

It should enforce issuer ceilings.

Example:

```text
AUTHORITY_A:
  may issue READ_PRIVATE

AUTHORITY_B:
  may issue WRITE_PROJECT

AUTHORITY_C:
  may issue DEPLOY_PRODUCTION only with human approval
```

Even if `AUTHORITY_A` is compromised, it must not be able to sign a token that verifies as production deployment authority.

This ceiling must be enforced both by the issuing service and by the verifier's Trust Root Registry policy.

---

## 25. Behavioral Evidence Authority Custody

Behavioral Evidence Authority keys generally have lower direct impact than Trust Root or Trust Decision keys, but fraudulent behavioral evidence can contribute to unauthorized grants.

Controls should include:

- protected signing service
- evidence digest binding
- subject binding
- evaluation-version binding
- TTL
- audit logging

For high-risk capabilities, multiple behavioral authorities may eventually be required, but that is outside v0.1.

---

## 26. COA / Governance Authority Custody

The Governance Authority signs the conditions under which agency is accepted.

It must bind:

- COA version
- exact governance digest
- subject
- session/context where applicable
- acceptance receipt

A participant must not be able to replace a strong COA with a weaker self-issued one.

---

## 27. Capability Executor Identity Custody

The executor's identity is different from trust-decision signing authority.

The executor needs credentials to:

- authenticate to Credential Vault
- authenticate to protected resources
- sign execution audit records where required

These credentials should be narrowly scoped and ideally workload-bound.

A compromised executor remains a critical risk, so its identity should not also serve as Trust Root or Policy Authority.

---

## 28. Resource Credentials

Protected-resource credentials are not ATE signing keys, but they are part of the custody model because they convert authorization into real effects.

They should be:

- unavailable to participant agents
- unavailable to model context
- scoped to executor role
- short-lived where possible
- rotated independently of ATE signing keys
- stored in a protected vault

ATE does not meaningfully enforce capability if the participant holds equivalent direct credentials.

---

## 29. Human Approval Keys

If high-risk actions require human authorization, human approval must use a separate identity/authentication path.

The agent must not be able to synthesize or invoke that approval credential.

A human approval artifact should bind:

```text
human_authority_id
requested_action_digest
trust_decision_id or envelope_id
approval_scope
issued_at
expires_at
signature/authentication proof
```

---

## 30. Key Usage Audit

Every security-sensitive signing operation should emit an audit event.

Minimum record:

```text
KeyUsageAudit {
    timestamp
    authority_id
    key_id
    artifact_type
    artifact_id
    artifact_digest
    signing_service_identity
    result
}
```

For root-key operations, additional operator identity should be recorded.

---

## 31. No Private Keys in Audit Evidence

Audit logs may contain:

- public keys
- key identifiers
- signatures
- artifact digests

They must never contain:

- private keys
- raw secret credentials
- recovery secrets
- unredacted API keys

This rule applies even to debug logging.

---

## 32. Key Backup

Keys requiring recovery must have documented backup policy.

Different key classes may use different strategies.

### Root keys

May require encrypted offline backup with multi-person recovery.

### Operational authority keys

May use managed KMS/HSM redundancy or rapid reissuance.

### Ephemeral session keys

Normally should not require backup.

Recovery policy must not silently create a weaker copy of the key outside its intended custody boundary.

---

## 33. Recovery vs Replacement

Not every lost key should be recovered.

For many operational keys, replacement is safer:

```text
old key unavailable
→ mark inactive/revoked
→ issue new key
→ update registry
```

ATE should prefer replacement over long-lived recoverability where operationally practical.

---

## 34. Key Destruction

Retired private keys should be destroyed when no longer required for signing or recovery.

Public keys and metadata may need indefinite retention for historical verification.

Destruction events should be auditable for high-assurance keys.

---

## 35. Trust Domains

Keys are trusted within explicitly defined TrustDomains.

Example:

```text
trust_domain = dbi.local
```

A foreign authority is not automatically trusted because its signature is valid.

TrustRootEntry must specify:

```text
trust_domain
permitted_roles
scope constraints
```

Federation requires explicit cross-domain trust policy and remains future work.

---

## 36. Cross-Domain Restriction

A local verifier must be able to express rules such as:

```text
accept external identity authority
accept external behavioral evidence authority
reject external authorization authority
reject external trust-decision authority
```

This prevents accidental transfer of sovereign authorization power across organizations.

---

## 37. Key Scope Constraints

Authority should be scopeable beyond artifact type.

Examples:

```text
K_AUTH_A:
  artifact_type = CapabilityToken
  max_risk_class = R2
  target_domain = project-alpha

K_AUTH_B:
  artifact_type = CapabilityToken
  max_risk_class = R3
  target_domain = production
```

The verifier enforces these ceilings independently of the signer.

---

## 38. Risk-Based Custody Requirements

Suggested baseline:

### R0/R1 actions

- KC1 or better operational signing
- logical role separation

### R2 actions

- KC2 preferred for Trust Decision and Authorization authorities
- durable revocation
- audited signing

### R3 actions

- KC2 minimum
- protected executor identity
- human or second-authority approval where policy requires

### R4 actions

- KC3 for critical roots/authorities
- quorum or multi-party controls
- isolated executor
- hardware-backed identity
- independent audit sink

---

## 39. Key Compromise Impact Matrix

| Compromised Key | Primary Consequence | Severity |
|---|---|---|
| Participant identity | impersonation of participant | High |
| Governance/COA | fraudulent governance acceptance | High |
| Behavioral authority | fraudulent behavioral evidence | High |
| Policy authority | malicious policy activation | Critical |
| Authorization authority | overbroad CapabilityTokens | Critical |
| Trust Decision authority | forged TRUST_GRANTED | Critical |
| Trust Root | redefinition of trusted authorities | Catastrophic |
| Executor identity/resource credential | direct protected-resource abuse | Critical |
| Audit authority | forged/tampered audit chain | High |

This matrix should drive custody strength.

---

## 40. Compromise Response Sequence

When compromise is suspected:

```text
1. suspend affected authority/key
2. prevent new signing
3. publish revocation
4. rotate/reissue replacement key
5. determine compromise window
6. identify affected artifacts
7. invalidate or re-evaluate affected active authorizations
8. preserve audit evidence
9. update Trust Root Registry
10. document incident disposition
```

No automatic assumption should be made that previously signed artifacts remain trustworthy.

---

## 41. Historical Verification

Production ATE must be able to verify historical decisions using the trust state applicable at the time.

Therefore retain:

- historical public keys
- registry versions
- policy versions
- revocation timestamps
- authority-role assignments
- artifact hashes

A key revoked on September 20 should not automatically make an artifact signed on September 1 invalid unless compromise policy says the key was considered compromised before September 1.

Time semantics matter.

---

## 42. Canonical Authority Decision

Verifier pseudocode:

```text
function issuer_authorized(artifact, registry_state, evaluation_time):

    entry = registry_state.lookup(artifact.issuer_id, artifact.key_id)

    require entry exists
    require artifact.signature verifies
    require entry.status permits verification
    require evaluation_time within key validity policy
    require artifact.type in entry.permitted_artifact_types
    require required_role in entry.permitted_roles
    require artifact scope within entry scope ceilings
    require key not revoked for this evaluation context

    return PASS
```

Any failure is denial.

---

## 43. Root Registry Bootstrap

A new deployment needs an initial trust anchor.

Bootstrap must be explicit.

Acceptable examples:

- administrator-installed root public key
- configuration management provisioned trust anchor
- hardware-backed platform trust anchor

Unacceptable bootstrap:

```text
first signer observed becomes trusted automatically
```

Trust-on-first-use may be useful in some systems but is not the default ATE production model.

---

## 44. Administrative Changes

Authority registration, revocation, and root changes are privileged administrative actions.

The participant agent must not be able to invoke them through ordinary ATE action capability unless a separately designed governance path explicitly permits it.

Changing who is trusted is more sensitive than using existing trust.

---

## 45. Emergency Access

Production systems may require break-glass access.

Break-glass must not be implemented as a hidden universal bypass accessible to agents.

If supported, it must require:

- separate human authority
- explicit reason
- strong authentication
- narrow time window
- enhanced audit
- post-event review

Break-glass use should be visible as exceptional, not indistinguishable from ordinary ATE authorization.

---

## 46. Secret Zero Problem

Every key-management system ultimately depends on an initial credential or root identity used to access protected signing services.

ATE must document this rather than pretend it disappears.

Examples:

- workload identity
- machine certificate
- hardware identity
- administrator bootstrap credential

The security of the initial identity determines whether protected custody is meaningful.

---

## 47. Same-Host Limitation

If participant, verifier, trust authority, executor, and all private keys reside under the same host/root authority, a host compromise may collapse all logical separation.

Same-host deployments can demonstrate architecture and support lower-risk use cases, but must not claim strong isolation from host-level attackers.

---

## 48. Recommended Production Role Placement

A practical production layout is:

```text
Participant Runtime
    K_IDENTITY / ephemeral provenance key only

ATE Verification Service
    no high-value signing key required

Trust Decision Service
    protected K_TRUST_DECISION

Policy Service
    protected K_POLICY

Authorization Service
    protected K_AUTHORITY

Behavioral Evidence Service
    protected K_BEHAVIORAL

Capability Executor
    workload identity + scoped resource credentials

Offline Governance Environment
    K_TRUST_ROOT
```

This provides meaningful compromise boundaries without requiring maximum hardware isolation everywhere.

---

## 49. Minimal Production Key Inventory

ATE should avoid unnecessary keys.

A minimal production system may require:

```text
K_TRUST_ROOT
K_IDENTITY
K_GOVERNANCE
K_POLICY
K_BEHAVIORAL
K_AUTHORITY
K_TRUST_DECISION
K_AUDIT or executor signing identity
```

Keys may share infrastructure, but authority roles remain distinct in policy.

---

## 50. Required Metadata for Every Signed Artifact

Every signed ATE artifact should contain or cryptographically bind:

```text
artifact_type
artifact_version
artifact_id
issuer_id
key_id
trust_domain
issued_at
payload_digest or canonical payload
signature_algorithm
signature
```

Artifact-specific fields are added on top of this common signing envelope.

---

## 51. Required Verification Order

Recommended authority verification sequence:

```text
1. parse canonical artifact
2. validate artifact type/version
3. identify issuer/key
4. load authoritative registry state
5. verify key status
6. verify issuer role
7. verify scope ceilings
8. verify cryptographic signature
9. verify freshness/revocation
10. continue artifact-specific verification
```

The exact order may be optimized, but no authorization check may be omitted.

---

## 52. Security Invariants

### INV-K1

No signature confers authority without an authorized issuer role.

### INV-K2

Participant agents cannot sign their own TrustDecision as an accepted production grant.

### INV-K3

Participant agents cannot obtain protected resource credentials.

### INV-K4

Trust Root private keys are not used for routine transaction signing.

### INV-K5

Every operational key has bounded role and scope.

### INV-K6

Revoked keys cannot authorize new actions.

### INV-K7

Historical public keys and registry state remain available for forensic verification.

### INV-K8

Signing APIs are artifact-specific and domain-separated.

### INV-K9

Private keys never appear in logs, prompts, evidence bundles, or audit records.

### INV-K10

Trust-root changes are privileged, versioned, and auditable.

---

## 53. Production Readiness Questions

Before deployment, answer:

1. Where does `K_TRUST_ROOT` physically reside?
2. Who may authorize root-registry changes?
3. Where does `K_TRUST_DECISION` reside?
4. Can participant processes invoke its signing interface directly?
5. Are resource credentials inaccessible to participants?
6. How are operational keys rotated?
7. How quickly do revocations propagate?
8. How is historical registry state retained?
9. Which risk classes require KC2 or KC3 custody?
10. What happens when an authority key is suspected compromised?
11. What is the bootstrap trust anchor?
12. Which roles may be combined in the intended deployment profile?

No production claim should be made until these questions have explicit answers.

---

## 54. Recommended Next Implementation Boundary

No broad key-management implementation is justified yet.

The smallest future engineering proof should test only the following claim:

> A participant runtime cannot obtain or use the Trust Decision private key, while an isolated Trust Decision service can sign only schema-valid, domain-separated TrustDecision objects after deterministic verification.

A second local proof should establish:

> The participant cannot obtain protected resource credentials held by the Capability Executor.

Both can be tested locally without premium model calls.

---

## 55. Explicit Non-Claims

This model does not claim:

- software key stores resist host-root compromise
- HSM use automatically makes the system secure
- authority separation prevents malicious policy decisions
- cryptographic identity proves benevolent intent
- all organizations should use identical key hierarchies
- federation trust is solved
- threshold signing is required for all deployments
- certificate-based PKI is the only implementation path

ATE key custody reduces unauthorized signing and authority confusion. It does not eliminate governance risk.

---

## 56. Architectural Conclusion

ATE depends on cryptographic evidence, but cryptography alone is not the trust architecture.

The actual trust architecture is:

```text
Who may sign
+ what they may sign
+ where the key lives
+ what scope the authority has
+ how the authority is revoked
+ how the verifier knows the current trust state
```

The central rule is:

> **Possession of a signing key does not define authority; the Trust Root Registry defines authority.**

And the central custody rule is:

> **The participant must never possess the keys or credentials that allow it to authorize itself or bypass the enforcement plane.**

This completes the minimum architectural foundation connecting ATE trust decisions to production-grade authority separation.
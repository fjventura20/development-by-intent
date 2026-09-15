# ATE Trust Domain & Federation Model v0.1

## 1. Purpose

This model defines how one Agent Trust Envelope (ATE) trust domain may recognize evidence, authorities, and agents originating in another domain without importing that domain's entire trust model.

The primary question is:

> Under what explicitly scoped conditions may Domain A accept a claim or artifact issued by Domain B for one specific governed action?

Federation MUST NOT imply blanket trust, permanent trust, or transitive trust.

---

## 2. Core Principle

Federation is local policy applied to foreign evidence.

A remote domain does not get to decide what the local domain trusts.

The receiving domain evaluates foreign artifacts against its own:

- trust roots
- federation policy
- accepted authority classes
- assurance requirements
- current revocation state
- risk policy
- scope limits

The controlling principle is:

> Foreign evidence may be recognized only to the exact extent explicitly authorized by local federation policy.

---

## 3. Trust Domain

A `TrustDomain` is an administrative security boundary that controls:

- trust roots
- accepted issuers
- active policies
- revocation state
- assurance requirements
- resource authorities
- local capability enforcement

Minimum structure:

```text
TrustDomain {
    domain_id
    domain_name
    trust_root_set_id
    federation_policy_id
    policy_epoch
    trust_root_epoch
    revocation_epoch
}
```

A trust domain may represent:

- an organization
- a department
- a machine cluster
- a managed agent platform
- an isolated project environment
- a sovereign administrative boundary

---

## 4. Local Authority Remains Supreme

When a foreign agent requests a governed action in the local domain:

```text
Foreign Agent
    ↓
Foreign Evidence
    ↓
Local Federation Policy
    ↓
Local ATE Verification
    ↓
Local Trust Decision Authority
    ↓
Local Capability Executor
```

The foreign domain may provide evidence.

The local domain decides whether that evidence is sufficient.

The foreign domain MUST NOT directly issue an executable local capability unless the local domain has explicitly delegated that authority.

---

## 5. Federation Is Not Transitive

Trust relationships MUST be non-transitive by default.

If:

```text
Domain A trusts Domain B
Domain B trusts Domain C
```

this MUST NOT imply:

```text
Domain A trusts Domain C
```

Domain A must create an explicit federation relationship with Domain C before C-issued artifacts are accepted.

Rule:

```text
A → B
B → C
DOES NOT IMPLY
A → C
```

Reason:

Automatic transitivity allows one trusted partner to silently expand the local trust perimeter.

---

## 6. Federation Agreement

Cross-domain recognition is controlled by a signed local `FederationAgreement`.

```text
FederationAgreement {
    agreement_id

    local_domain_id
    remote_domain_id

    accepted_remote_authorities[]
    accepted_artifact_types[]
    maximum_risk_class
    maximum_capability_scope

    minimum_assurance_profile
    required_policy_mappings[]

    valid_from
    expires_at

    local_authority_id
    signature
}
```

The agreement is a local artifact.

A remote domain cannot create or widen it.

---

## 7. Authority-Specific Recognition

Federation SHOULD recognize authorities by role rather than recognizing a remote domain wholesale.

Example:

```text
Domain A may accept:

Domain B Identity Authority
    for identity claims

Domain B Behavioral Authority
    for behavioral receipts

but NOT:

Domain B Authorization Authority
    for local WRITE capabilities
```

This allows selective trust.

---

## 8. Accepted Artifact Classes

Federation policy may independently authorize recognition of:

- identity credentials
- runtime provenance
- COA acceptance evidence
- VA policy evidence
- behavioral evidence receipts
- verification receipts
- capability assertions
- audit attestations

Each class is separately controlled.

Example:

```text
accepted_artifact_types = [
    IDENTITY_CREDENTIAL,
    BEHAVIORAL_EVIDENCE_RECEIPT
]
```

This does not authorize foreign capability issuance.

---

## 9. Foreign Identity

A foreign identity credential may establish:

> This agent is recognized as subject X by Remote Domain B.

It does NOT establish:

> Subject X is authorized to act in Local Domain A.

Identity and authorization remain distinct.

Local ATE must still evaluate:

- local policy
- COA compatibility
- behavioral evidence
- capability scope
- risk class
- federation limits

---

## 10. Foreign COA Evidence

A remote COA acceptance may be recognized only if local federation policy explicitly accepts:

- the foreign governance authority
- the COA version or mapped equivalent
- the acceptance binding semantics

Possible result:

```text
REMOTE_COA_ACCEPTED_AS_EQUIVALENT
```

or:

```text
REMOTE_COA_NOT_ACCEPTABLE
```

The local domain may require a new local COA acceptance even when foreign governance evidence is valid.

---

## 11. Value Architecture Compatibility Across Domains

Different domains may use different policy identifiers and versions.

Federation therefore requires explicit compatibility mapping.

Example:

```text
PolicyMapping {
    local_policy_id
    local_policy_version
    remote_policy_id
    remote_policy_version
    mapping_result
    mapping_constraints
    issuer
    signature
}
```

Possible mappings:

```text
EQUIVALENT
COMPATIBLE_WITH_CONSTRAINTS
NOT_COMPATIBLE
```

No semantic compatibility should be inferred solely from similar names or descriptions.

---

## 12. Local Policy Always Controls Local Action

Even when a foreign VA policy is accepted as compatible, the requested local action must satisfy local policy.

Conceptually:

```text
foreign policy evidence
        ↓
compatibility mapping
        ↓
LOCAL policy evaluation
        ↓
capability decision
```

The remote domain's policy never overrides the local policy authority.

---

## 13. Behavioral Evidence Federation

A local domain may accept behavioral evidence from approved external evaluators.

Federation policy should specify:

- accepted evaluator identities
- accepted evaluation profiles
- maximum evidence age
- supported subject classes
- supported risk classes

Example:

```text
Evaluator B accepted for R0-R2
Evaluator C required for R3
Foreign behavioral evidence prohibited for R4
```

---

## 14. Foreign Authorization

Foreign authorization is high risk.

Default policy:

> Foreign CapabilityTokens are advisory evidence, not locally executable authority.

The preferred model is:

```text
remote authorization assertion
        ↓
local ATE verification
        ↓
local CapabilityToken
        ↓
local TrustDecision
        ↓
local Capability Executor
```

This preserves local enforcement sovereignty.

---

## 15. Explicit Delegation Exception

A local domain MAY explicitly delegate capability issuance authority to a foreign authority, but such delegation must be narrow.

A delegation should bind:

```text
DelegatedAuthority {
    remote_authority_id
    allowed_operations[]
    allowed_targets[]
    maximum_risk_class
    valid_from
    expires_at
    delegation_depth
    local_issuer
    signature
}
```

Default:

```text
delegation_depth = 0
```

This means the foreign authority may not redelegate.

---

## 16. No Implicit Redelegation

If Domain A delegates READ authority to Domain B, Domain B MUST NOT delegate that authority to Domain C unless Domain A explicitly permits it.

Rule:

```text
foreign delegated scope <= local delegation scope
```

and:

```text
remaining delegation depth > 0
```

otherwise deny.

---

## 17. Federation Scope Ceiling

Every federation relationship MUST define a maximum capability ceiling.

Example:

```text
maximum_risk_class = R2
maximum_operations = [READ_PRIVATE, CREATE_DRAFT]
```

Even valid foreign evidence cannot exceed this ceiling.

---

## 18. Risk-Based Federation

Federation acceptance should become stricter as action risk increases.

Illustrative policy:

```text
R0:
foreign identity may suffice

R1:
identity + accepted behavioral evidence

R2:
identity + COA compatibility + behavioral evidence + local authorization

R3:
local trust decision + stronger federation assurance + human approval

R4:
foreign authorization insufficient; local high-assurance approval required
```

---

## 19. Federation Assurance Profiles

A federation relationship may define a `FederationAssuranceProfile`.

```text
FederationAssuranceProfile {
    profile_id
    minimum_remote_key_custody
    minimum_evidence_freshness
    required_revocation_freshness
    required_audit_strength
    permitted_risk_classes[]
}
```

A remote authority that cannot satisfy the profile is not acceptable for that action class.

---

## 20. Foreign Trust Root Recognition

The local Trust Root Registry may include foreign trust anchors.

A foreign trust anchor entry MUST specify:

- remote domain
- authority class
- permitted artifact types
- validity interval
- local federation agreement
- local scope ceiling
- current status

A public key alone is never enough.

---

## 21. Pinning vs Hierarchical Recognition

Two recognition models are possible.

### 21.1 Key pinning

Local domain explicitly recognizes one foreign authority key.

Advantages:

- simple
- narrow
- strong control

Disadvantages:

- operational rotation overhead

### 21.2 Foreign root recognition

Local domain recognizes a remote root that may authorize subordinate authorities.

Advantages:

- scalable

Disadvantages:

- expands imported trust
- requires strict path constraints

For early ATE federation, key pinning is preferred.

---

## 22. Remote Authority Path Constraints

If hierarchical foreign trust is allowed, certificate or authority paths must be constrained.

Example:

```text
Remote Root B
    ↓ may authorize
Behavioral Evaluator B1

NOT
Authorization Authority B2
```

The local federation policy defines acceptable paths.

---

## 23. Remote Revocation

Foreign evidence MUST be checked against remote revocation state when the federation agreement requires it.

The local domain must define:

- trusted revocation source
- freshness requirement
- unavailable-state behavior

Default:

```text
revocation status unavailable
→ TRUST_DENIED
```

for risk classes where current revocation is mandatory.

---

## 24. Local Revocation Supremacy

The local domain may independently revoke recognition of:

- a remote domain
- a remote root
- a remote authority
- a federation agreement
- a specific foreign artifact

Local revocation overrides remote validity.

Thus:

```text
remote says ACTIVE
local says REVOKED
→ REVOKED
```

---

## 25. Federation Epoch

Federation state should be versioned with a monotonic:

```text
federation_epoch
```

Trust decisions should bind the federation epoch used during evaluation.

This prevents rollback to stale federation relationships.

---

## 26. Federation State

Suggested states:

```text
ACTIVE
SUSPENDED
REVOKED
EXPIRED
SUPERSEDED
UNKNOWN
```

Only `ACTIVE` federation relationships may contribute to a new trust grant.

---

## 27. Federation Suspension

Suspension is useful when a remote domain may be compromised but investigation is incomplete.

During suspension:

- existing historical evidence remains auditable
- new grants relying on the suspended relationship are denied
- local incident response proceeds

This avoids prematurely destroying historical meaning while stopping new trust.

---

## 28. Remote Domain Compromise

If Domain B is believed compromised, Domain A should be able to:

1. suspend the federation agreement;
2. increment federation/revocation epochs;
3. stop accepting new B-issued evidence;
4. identify active local grants dependent on B;
5. revoke affected local CapabilityTokens/TrustDecisions if necessary;
6. preserve all historical audit evidence.

---

## 29. Cross-Domain Artifact Binding

Federated artifacts must bind both domains where relevant.

Example:

```text
issuer_domain_id
subject_domain_id
intended_recipient_domain_id
```

This prevents an artifact issued for Domain C from being replayed in Domain A.

---

## 30. Intended Audience Binding

Foreign evidence SHOULD include an audience or relying-party binding when it is not universally reusable.

Example:

```text
audience = domain-a.example
```

If:

```text
audience != local_domain_id
```

reject.

---

## 31. Cross-Domain Session Binding

When foreign session evidence contributes to local authorization, the local envelope must bind:

- foreign session identity
- foreign runtime identity
- local request identity
- local federation agreement

The local trust decision must not treat the foreign session as a local session.

---

## 32. Federation Request Context

A federated request should explicitly identify origin.

```text
FederatedRequestContext {
    origin_domain_id
    subject_identity
    remote_session_identity
    federation_agreement_id
    federation_epoch
}
```

This becomes part of the local envelope binding hash.

---

## 33. Foreign Artifact Substitution

Attack:

A valid artifact from Domain B is presented as if issued by Domain C or under another federation agreement.

Defense:

The artifact and local envelope bind:

- issuer domain
- issuer authority
- federation agreement
- local recipient domain

Exact matches required.

---

## 34. Federation Downgrade Attack

Attack:

A participant selects an older, weaker federation agreement.

Defense:

Local federation authority publishes the active agreement/version/epoch.

Only current active federation state is accepted.

---

## 35. Cross-Domain Policy Downgrade

A remote domain may continue presenting evidence created under an older policy.

Local policy mapping must specify acceptable remote policy versions.

If the remote policy version is no longer mapped:

```text
TRUST_DENIED
GX_REMOTE_POLICY_NOT_ACCEPTED
```

---

## 36. Semantic Mismatch

Two domains may use identical labels with different meanings.

Example:

```text
"WRITE_SCOPED"
```

may mean different things in two organizations.

Federation must never rely on label equality alone.

Capability and policy mappings require explicit semantics.

---

## 37. Capability Mapping

When foreign operation names differ from local names:

```text
CapabilityMapping {
    remote_operation
    local_operation
    mapping_constraints
    mapping_version
}
```

Mappings MUST NOT widen authority.

Rule:

```text
mapped_local_scope <= accepted_foreign_scope
```

---

## 38. Data Classification Constraints

Federation agreements should optionally constrain data classes.

Example:

```text
remote agent may READ:
PUBLIC
INTERNAL

remote agent may NOT access:
CONFIDENTIAL
RESTRICTED
```

A valid identity does not imply entitlement to local data.

---

## 39. Tenant Isolation

In multi-tenant environments, federation must bind tenant identity.

A remote artifact accepted for Tenant X MUST NOT authorize action in Tenant Y.

Required binding:

```text
tenant_id
```

where applicable.

---

## 40. Federation Audit Requirements

Every federated trust decision should record:

- local domain
- remote domain
- federation agreement ID
- federation epoch
- remote authority IDs
- foreign artifact hashes
- local policy mappings
- local trust decision
- local executor outcome

This permits later reconstruction of why foreign evidence was accepted.

---

## 41. Dual-Domain Audit Correlation

Where both domains expose audit receipts, correlation may use:

```text
cross_domain_transaction_id
```

This allows Domain A and B to compare records without sharing full internal logs.

---

## 42. Privacy Minimization

Federation SHOULD exchange only the evidence required for the trust decision.

Do not automatically export:

- full prompts
- full conversation history
- unrelated user data
- complete behavioral evaluation records

Prefer signed receipts and digests.

Principle:

> Prove what is needed without disclosing what is not.

---

## 43. Selective Disclosure

Future federation may support credentials containing multiple claims while disclosing only relevant claims.

This is not required for v0.1, but the architecture should not assume complete credential disclosure is always necessary.

---

## 44. Unknown Remote State

If the local verifier cannot determine required remote state:

```text
UNKNOWN != TRUSTED
```

For required evidence:

```text
TRUST_DENIED
GX_REMOTE_TRUST_STATE_UNKNOWN
```

Fail closed.

---

## 45. Remote Availability Failure

Federation should not make authorization integrity depend on optimistic assumptions during remote outages.

Possible policy:

```text
R0/R1:
allow cached foreign state within freshness window

R2:
require recent signed state

R3/R4:
require current online or independently replicated state
```

---

## 46. Federation Caching

Cached remote artifacts may be used only within explicitly defined freshness windows.

Cache entries should bind:

- artifact hash
- fetched_at
- remote epoch
- expiration

Never silently extend validity because the remote domain is unavailable.

---

## 47. Federation Discovery

Automatic discovery of remote trust roots is dangerous.

Default v0.1 policy:

> No remote authority is trusted merely because it is discoverable.

Trust requires prior local registration or explicitly approved onboarding.

---

## 48. Federation Onboarding

Recommended onboarding process:

1. identify remote domain;
2. verify remote trust anchor out-of-band;
3. define accepted authority roles;
4. define artifact classes;
5. define maximum risk/capability scope;
6. define assurance requirements;
7. define policy mappings;
8. define revocation source;
9. create signed local FederationAgreement;
10. activate at new federation epoch.

---

## 49. Federation Offboarding

Offboarding process:

1. suspend or revoke FederationAgreement;
2. increment federation epoch;
3. stop new foreign evidence acceptance;
4. identify dependent active grants;
5. revoke where required;
6. preserve historical audit records.

---

## 50. Federation Relationship Types

ATE may eventually distinguish:

### F0 — No federation

No foreign evidence accepted.

### F1 — Identity-only federation

Foreign identity evidence recognized.

### F2 — Evidence federation

Selected governance/behavioral evidence recognized.

### F3 — Authorization-assisted federation

Foreign authorization assertions may contribute, but local authorization remains required.

### F4 — Delegated authority federation

Foreign authority may issue narrowly scoped local-recognized capabilities.

F4 requires the strongest controls and should be exceptional.

---

## 51. Recommended Default

Production default should be:

```text
F1 or F2
```

not F4.

This preserves local control while still allowing useful interoperability.

---

## 52. Federation Threats

Major threats include:

- transitive trust expansion
- compromised remote root
- stale remote revocation state
- remote policy downgrade
- semantic mismatch
- authority-role confusion
- capability mapping widening
- audience substitution
- tenant confusion
- redelegation escalation
- federation agreement rollback
- remote audit fabrication

---

## 53. Security Invariants

### FED-INV-1

Foreign trust is never implicitly transitive.

### FED-INV-2

Local authority defines what foreign evidence is acceptable.

### FED-INV-3

Remote identity does not imply local authorization.

### FED-INV-4

Foreign policy never overrides local policy.

### FED-INV-5

Capability mappings never widen authority.

### FED-INV-6

Foreign authorization does not become executable locally unless explicitly delegated.

### FED-INV-7

Local revocation overrides foreign validity.

### FED-INV-8

Unknown remote trust state fails closed where current state is required.

### FED-INV-9

Federation decisions bind the exact active federation agreement and epoch.

### FED-INV-10

The local Capability Executor remains the final enforcement authority for local resources.

---

## 54. Federated Trust Decision Flow

```text
receive foreign request

verify local federation agreement ACTIVE
verify federation epoch current
verify remote domain identity
verify accepted foreign authority roles
verify foreign signatures
verify foreign revocation/freshness
verify intended audience/local domain binding
map foreign policy/evidence to local semantics
apply local VA policy
apply local risk/assurance policy
issue local capability if permitted
run local ATE trust decision
execute only through local Capability Executor
record federated audit evidence
```

Any required failure results in denial.

---

## 55. Example: External Development Agent

Domain B provides a software-development agent to Domain A.

Domain A federation policy may accept:

- B identity credential
- B behavioral evaluation
- B COA acceptance

But Domain A issues its own:

- local CapabilityToken
- local TrustDecision

and permits only:

```text
READ_REPOSITORY
CREATE_PATCH
```

not:

```text
MERGE_PROTECTED_BRANCH
DEPLOY_PRODUCTION
```

This demonstrates useful federation without surrendering local authorization.

---

## 56. Example: Independent Behavioral Evaluator

A dedicated Domain E performs agent behavioral evaluations.

Domain A may federate only with E's Behavioral Authority.

Domain A does not trust E for:

- identity issuance
- COA issuance
- authorization
- policy management

This illustrates role-specific federation.

---

## 57. Example: Emergency Federation Suspension

Domain B reports suspected compromise of its identity authority.

Domain A:

```text
FederationAgreement A-B → SUSPENDED
federation_epoch += 1
```

New B-dependent grants fail.

Historical B-origin actions remain verifiable against the earlier state.

After remediation, a new authority key and federation agreement may be activated.

---

## 58. Relationship to Trust Root Model

The Trust Root & Key Custody Model answers:

> Which authorities may sign which claims?

The Federation Model adds:

> Which foreign authorities will this local domain recognize, for what purpose and scope?

Foreign authority is therefore a constrained extension of the local trust-root registry, not a separate source of ultimate authority.

---

## 59. Relationship to Revocation Model

Federation introduces two revocation layers:

```text
remote revocation state
+
local federation/revocation state
```

Both must permit use.

If either denies:

```text
TRUST_DENIED
```

---

## 60. Relationship to Risk & Assurance

Federation increases uncertainty and therefore may raise required assurance.

A local policy may specify:

```text
same action:
local agent → A2
foreign agent → A3
```

Federation origin is therefore a possible risk-elevation signal.

---

## 61. Relationship to Enforcement Plane

No federation agreement bypasses local capability enforcement.

Even the strongest foreign credential must ultimately pass through:

```text
Local ATE
→ Local TrustDecision
→ Local Capability Executor
```

unless a narrowly scoped delegation explicitly says otherwise.

---

## 62. Explicit Non-Claims

This v0.1 model does not establish:

- global agent identity infrastructure
- Internet-scale PKI
- semantic policy translation automation
- automatic inter-organizational legal agreements
- privacy-preserving credential proofs
- universal revocation distribution
- secure cross-domain delegation for critical actions
- Byzantine consensus between organizations

It defines federation boundaries and control rules.

---

## 63. Recommended Initial Production Posture

Start conservatively:

- no transitive trust
- key-pinned foreign authorities
- F1/F2 federation only
- local authorization always required
- local executor always required
- short federation agreement lifetimes
- explicit risk ceilings
- explicit revocation/freshness requirements
- append-only federation audit records

Broader delegation should be earned by evidence, not assumed.

---

## 64. Architectural Conclusion

ATE federation should not attempt to create a universal category of "trusted agents."

It should allow one administrative domain to make narrow, explicit, revocable decisions about which foreign claims it is willing to recognize.

The central rule is:

> **Trust does not cross a domain boundary by implication. It crosses only through an explicit, locally controlled, scoped federation agreement.**

And even then:

> **Foreign evidence informs the local trust decision; local authority controls local capability.**

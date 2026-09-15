# ATE Reference Architecture & Component Interaction Model v0.1

## 1. Purpose

This document consolidates the Agent Trust Envelope (ATE) production architecture into one reference model. It defines the system components, trust boundaries, data flows, state transitions, authority relationships, and responsibility ownership across the ATE architecture family.

The objective is to answer:

> How do the ATE production components work together to decide, authorize, execute, revoke, and audit one governed action?

ATE does not establish permanent trust in an agent. It establishes whether one specific action may be performed now under current evidence, policy, authority, and risk conditions.

---

## 2. Core Operating Principle

The system is governed by one execution rule:

> **No trust grant, no capability. No capability, no governed action.**

The participant agent may request actions and present evidence, but it does not control the trust decision or execution authority.

---

## 3. Architectural Planes

ATE is organized into six logical planes.

### 3.1 Participant Plane

Contains:

- AI model
- participant agent runtime
- prompts and context
- tool-selection logic
- proposed action requests

This plane is untrusted or semi-trusted.

### 3.2 Evidence Plane

Contains authorities and artifacts establishing:

- identity
- runtime/session provenance
- Condition of Agency acceptance
- Value Architecture policy compatibility
- behavioral evidence
- freshness and state

### 3.3 Verification Plane

Contains:

- ATE Verifier
- trust-root lookup
- revocation checks
- active-policy checks
- evidence binding verification
- risk and assurance evaluation

### 3.4 Authorization Plane

Contains:

- Authorization Authority
- CapabilityToken issuance
- Trust Decision Authority
- nonce/replay state

### 3.5 Enforcement Plane

Contains:

- Capability Executor
- Credential Vault
- Resource Adapters
- protected external resources

### 3.6 Accountability Plane

Contains:

- tamper-evident audit ledger
- evidence archive
- execution records
- trust-state epochs
- forensic reconstruction data

---

## 4. Reference Architecture

```text
                           ┌─────────────────────────┐
                           │   Trust Root Registry   │
                           └────────────┬────────────┘
                                        │
                       recognized roles / issuers
                                        │
               ┌────────────────────────┼────────────────────────┐
               │                        │                        │
               ▼                        ▼                        ▼
      ┌────────────────┐       ┌────────────────┐       ┌────────────────┐
      │ Policy         │       │ Evidence       │       │ Revocation     │
      │ Authority      │       │ Authorities    │       │ Authority      │
      └───────┬────────┘       └───────┬────────┘       └───────┬────────┘
              │                        │                        │
              └──────────────┬─────────┴─────────┬──────────────┘
                             │                   │
                             ▼                   │
                    ┌─────────────────┐          │
                    │ Evidence Bundle │◄─────────┘
                    └────────┬────────┘
                             │
                             ▼
 Participant Agent ────────► ┌─────────────────┐
 Action Request              │ Request Gateway │
                             └────────┬────────┘
                                      │ canonical action
                                      ▼
                             ┌─────────────────┐
                             │   ATE Verifier  │
                             └────────┬────────┘
                                      │ verified evidence
                                      ▼
                             ┌────────────────────┐
                             │ Trust Decision     │
                             │ Authority          │
                             └─────────┬──────────┘
                                       │
                          TRUST_GRANTED / TRUST_DENIED
                                       │
                         ┌─────────────┴─────────────┐
                         │                           │
                         ▼                           ▼
                  no capability              ┌──────────────────┐
                                             │ Capability       │
                                             │ Executor         │
                                             └───────┬──────────┘
                                                     │
                                     ┌───────────────┼──────────────┐
                                     │               │              │
                                     ▼               ▼              ▼
                              Nonce Registry   Credential Vault   Audit Ledger
                                     │               │
                                     └───────┬───────┘
                                             │
                                             ▼
                                      Resource Adapter
                                             │
                                             ▼
                                      Protected Resource
```

---

## 5. Primary Components

### 5.1 Participant Agent

Responsibilities:

- formulate proposed action
- supply required evidence references
- receive grant/deny result

Forbidden responsibilities:

- self-authorization
- holding trust-authority keys
- holding governed resource credentials
- bypassing executor

### 5.2 Request Gateway

Responsibilities:

- structural validation
- canonical action creation
- target normalization
- parameter canonicalization
- requested-action digest

It does not grant trust.

### 5.3 Trust Root Registry

Responsibilities:

- define recognized authorities
- define permitted artifact classes per authority
- define trust domains
- publish key and authority status
- expose current trust-root epoch

A valid signature is insufficient unless the signer is authorized for that artifact class.

### 5.4 Evidence Authorities

Potential roles:

- identity authority
- provenance authority
- governance / COA authority
- VA policy authority
- behavioral evidence authority

Each authority signs only the artifact classes explicitly permitted by the Trust Root Registry.

### 5.5 Policy Authority

Responsibilities:

- publish active VA/governance policy
- publish current policy version and digest
- advance policy epoch
- supersede prior policy versions

### 5.6 Revocation Authority / Registry

Responsibilities:

- publish revocation records
- represent suspension, revocation, expiry, and supersession
- advance revocation epoch
- support current-trust-state resolution

### 5.7 ATE Verifier

Responsibilities:

- canonicalize evidence
- validate signatures
- validate issuer authority
- evaluate trust roots
- evaluate current policy
- evaluate revocation
- validate provenance and COA binding
- validate behavioral evidence
- validate capability scope
- evaluate freshness and replay state
- apply risk/assurance requirements

It emits deterministic gate results or a signed VerificationReceipt if required by deployment profile.

### 5.8 Authorization Authority

Responsibilities:

- issue least-privilege CapabilityTokens
- bind token to subject, session, COA, policy, scope, freshness, nonce
- never issue authority broader than its registry ceiling

### 5.9 Trust Decision Authority

Responsibilities:

- consume verified evidence
- independently sign TRUST_GRANTED or TRUST_DENIED
- bind decision to one exact action and envelope
- remain separate from participant authority boundary

### 5.10 Nonce Registry

Responsibilities:

- durable single-use state
- atomic reservation
- replay prevention
- execution-state tracking

Recommended production states:

```text
UNSEEN
AUTHORIZED
RESERVED
CONSUMED
FAILED_BEFORE_EFFECT
UNKNOWN_EFFECT
```

### 5.11 Capability Executor

Responsibilities:

- independently verify TrustDecision
- reserve nonce atomically
- obtain resource credential
- validate exact operation/target/parameters
- execute only approved action
- finalize nonce state
- emit audit evidence

The participant must not possess equivalent direct resource authority.

### 5.12 Credential Vault

Responsibilities:

- hold governed resource credentials
- release credentials only to authorized executor identity
- prefer scoped and short-lived credentials

### 5.13 Resource Adapter

Responsibilities:

- translate typed ATE actions into resource-specific operations
- independently validate concrete target and parameters
- defend against path traversal, aliasing, TOCTOU, and confused-deputy behavior

### 5.14 Audit Ledger

Responsibilities:

- append signed audit events
- maintain sequence and hash chain
- preserve trust-root, revocation, policy, federation, and assurance epochs
- reconstruct why a decision/action occurred
- retain corrections as append-only records

---

## 6. Core Artifact Relationships

The main artifact dependency chain is:

```text
Identity / Runtime Evidence
          │
          ▼
Live Provenance Evidence
          │
          ▼
COA Acceptance
          │
          ▼
VA Policy + Active Policy Manifest
          │
          ▼
BehavioralEvidenceReceipt
          │
          ▼
CapabilityToken
          │
          ▼
AgentTrustEnvelope
          │
          ▼
VerificationReceipt (optional by profile)
          │
          ▼
TrustDecision
          │
          ▼
ExecutionCapability
          │
          ▼
ExecutionAuditRecord
```

Every downstream artifact binds to the controlling upstream context by identifiers, digests, signatures, or fingerprints.

---

## 7. AgentTrustEnvelope

Minimum conceptual structure:

```text
AgentTrustEnvelope {
    envelope_id

    trust_domain
    subject_identity
    runtime_identity
    session_identity

    live_provenance_receipt
    coa_acceptance_receipt
    va_policy_reference
    behavioral_evidence_receipt
    capability_token

    requested_action

    freshness_challenge
    nonce

    risk_class
    required_assurance_profile

    trust_root_epoch
    policy_epoch
    revocation_epoch
    federation_epoch

    created_at
    expires_at

    envelope_binding_hash
}
```

---

## 8. End-to-End Decision Flow

### Phase 1 — Request

Participant submits proposed action.

### Phase 2 — Canonicalization

Request Gateway produces exact canonical operation, target, and parameter digest.

### Phase 3 — Evidence Assembly

Required evidence is collected and bound to subject/session/action context.

### Phase 4 — Risk Classification

Action is classified R0–R4.

Risk class determines required assurance profile A0–A4.

### Phase 5 — Trust Verification

ATE Verifier evaluates all mandatory gates.

Recommended sequence:

```text
G0  Current trust / revocation
G1  Trust-root and issuer authority
G2  Runtime/session provenance
G3  COA acceptance and binding
G4  Active VA policy compatibility
G5  Behavioral evidence
G6  Capability scope
G7  Envelope/artifact binding
G8  Freshness / expiration
G9  Nonce / replay
G10 Action canonicalization
G11 Risk / assurance profile compliance
G12 Federation policy, if cross-domain
```

Any deterministic failure returns denial.

### Phase 6 — Trust Decision

Trust Decision Authority signs:

```text
TRUST_GRANTED
```

or

```text
TRUST_DENIED
```

with machine-readable reason code.

### Phase 7 — Executor Reverification

Capability Executor independently validates critical decision fields.

### Phase 8 — Nonce Reservation

```text
AUTHORIZED → RESERVED
```

must be atomic.

### Phase 9 — Credential Acquisition

Executor obtains only the credential required for the exact governed resource.

### Phase 10 — Resource Validation

Resource Adapter verifies concrete resource state and canonical target.

### Phase 11 — Execution

One exact action executes.

### Phase 12 — State Finalization

One of:

```text
CONSUMED
FAILED_BEFORE_EFFECT
UNKNOWN_EFFECT
```

### Phase 13 — Audit Commit

Decision and execution evidence are appended to audit ledger.

---

## 9. TrustDecision Binding

A TrustDecision must bind at least:

```text
trust_decision_id
envelope_id
envelope_binding_hash
subject_identity
session_identity
requested_action_digest
capability_token_id
coa_acceptance_fingerprint
policy_digest
behavioral_receipt_id
risk_class
assurance_profile
trust_root_epoch
policy_epoch
revocation_epoch
federation_epoch
nonce
issued_at
expires_at
verdict
reason_code
authority_id
signature
```

The participant cannot change any of these values without invalidating the decision.

---

## 10. State Models

### 10.1 Trust State

```text
ACTIVE
SUSPENDED
REVOKED
EXPIRED
SUPERSEDED
UNKNOWN
```

Only currently usable dependencies may contribute to grant.

### 10.2 Nonce State

```text
UNSEEN
AUTHORIZED
RESERVED
CONSUMED
FAILED_BEFORE_EFFECT
UNKNOWN_EFFECT
```

### 10.3 Decision State

```text
REQUESTED
VERIFIED
TRUST_GRANTED
TRUST_DENIED
EXECUTION_RESERVED
EXECUTED
FAILED
EFFECT_UNKNOWN
```

### 10.4 Policy State

```text
DRAFT
ACTIVE
SUPERSEDED
REVOKED
```

---

## 11. Risk and Assurance Integration

Risk is not equivalent to trust.

Risk determines how much assurance is required before trust may be granted.

Reference mapping:

```text
R0 → A0
R1 → A1
R2 → A2
R3 → A3
R4 → A4
```

Higher profiles may require:

- fresher evidence
- stronger key custody
- independent authorities
- human approval
- stronger executor isolation
- synchronous revocation checking
- mandatory audit durability
- quorum authorization

A lower-assurance decision cannot be reused for a higher-risk action.

---

## 12. Key and Authority Separation

Recommended authority roles:

```text
K_IDENTITY
K_PROVENANCE
K_GOVERNANCE
K_VA_POLICY
K_BEHAVIORAL
K_AUTHORITY
K_VERIFIER
K_TRUST_DECISION
K_EXECUTOR_IDENTITY
K_AUDIT
K_TRUST_ROOT
```

No single participant key should satisfy multiple sensitive authority roles merely because its signature is cryptographically valid.

Role authorization comes from the Trust Root Registry.

---

## 13. Trust Root Epochs

Every trust-sensitive decision should capture monotonic state versions:

```text
trust_root_epoch
revocation_epoch
policy_epoch
federation_epoch
```

The verifier must reject rollback to older authoritative state when newer state is known.

Historical forensic verification may evaluate prior epochs, but current execution requires current state.

---

## 14. Revocation Propagation

If a controlling artifact becomes revoked or superseded, dependent unexecuted grants become unusable.

Examples:

- revoked identity invalidates active session trust
- revoked COA acceptance invalidates dependent CapabilityToken
- revoked policy invalidates dependent trust decisions
- revoked authorization key invalidates newly presented token authority
- revoked TrustDecision blocks executor use

A historical record is not erased; its current executability changes.

---

## 15. Federation Interaction

Cross-domain evidence is accepted only through local federation policy.

Reference flow:

```text
Foreign Agent
     │
     ▼
Foreign Evidence
     │
     ▼
Local Federation Policy
     │
     ▼
Local ATE Verification
     │
     ▼
Local Trust Decision
     │
     ▼
Local Capability Executor
```

Important rule:

> Foreign evidence may contribute to a local decision, but foreign trust does not directly create local capability.

Trust remains non-transitive by default.

---

## 16. Audit Interaction

Every critical transition emits an audit event.

At minimum:

```text
REQUEST_RECEIVED
EVIDENCE_ASSEMBLED
VERIFICATION_STARTED
GATE_FAILED
TRUST_DENIED
TRUST_GRANTED
NONCE_RESERVED
EXECUTION_STARTED
EXECUTION_SUCCEEDED
EXECUTION_FAILED_BEFORE_EFFECT
EXECUTION_EFFECT_UNKNOWN
REPLAY_REJECTED
REVOCATION_REJECTED
POLICY_SUPERSEDED
AUTHORITY_REVOKED
```

Audit records must include the authoritative epochs applicable to the event.

---

## 17. Failure Handling

ATE uses fail-closed semantics.

The following never imply grant:

```text
UNKNOWN
MISSING
MALFORMED
UNAVAILABLE
UNSUPPORTED
EXCEPTION
```

If the system cannot establish required trust conditions, execution does not occur.

---

## 18. External-Effect Handling

The executor must distinguish:

```text
FAILED_BEFORE_EFFECT
```

from:

```text
UNKNOWN_EFFECT
```

An unknown-effect state blocks automatic retry unless the resource provides idempotent reconciliation.

Where supported, external idempotency keys should derive from the trust decision and action digest.

---

## 19. Human Approval

Human approval is an additional authority artifact, not an informal chat response.

For applicable risk profiles:

```text
HumanApproval {
    approval_id
    human_authority
    action_digest
    decision
    issued_at
    expires_at
    signature_or_strong_authentication_proof
}
```

The participant agent must not be able to synthesize or impersonate this approval path.

---

## 20. Component Trust Matrix

| Component | May request action | May verify evidence | May grant trust | May hold resource credential | May execute | May revoke | May audit |
|---|---:|---:|---:|---:|---:|---:|---:|
| Participant Agent | Yes | No authoritative role | No | No | No direct governed execution | No | Emits non-authoritative context only |
| Request Gateway | No | Structural only | No | No | No | No | Yes |
| Evidence Authority | No | Own evidence domain | No | No | No | Limited by role | Yes |
| ATE Verifier | No | Yes | No | No | No | No | Yes |
| Authorization Authority | No | Limited | Capability only | No | No | Token revocation if authorized | Yes |
| Trust Decision Authority | No | Consumes verified evidence | Yes | No | No | Decision revocation if authorized | Yes |
| Capability Executor | No | Critical reverify | No | Yes/scoped | Yes | No | Yes |
| Trust Root Authority | No | Governance role | No direct action grant | No | No | Authority/key governance | Yes |
| Audit Authority | No | Audit validation | No | No | No | No | Yes |

---

## 21. Responsibility by Governing Artifact

### ATE-PRODUCTION-ARCHITECTURE-v0.1.md

Owns:

- overall production trust architecture
- core components
- trust-decision concept

### ATE-PRODUCTION-THREAT-MODEL-v0.1.md

Owns:

- attacker model
- threat classes
- security priorities

### ATE-ENFORCEMENT-PLANE-v0.1.md

Owns:

- executor design
- resource mediation
- nonce execution lifecycle
- credential isolation

### ATE-TRUST-ROOT-KEY-CUSTODY-MODEL-v0.1.md

Owns:

- authority roles
- key custody
- signing rights
- root governance

### ATE-REVOCATION-TRUST-STATE-MODEL-v0.1.md

Owns:

- current trust state
- revocation semantics
- epochs
- dependency invalidation

### ATE-AUDIT-ACCOUNTABILITY-MODEL-v0.1.md

Owns:

- tamper-evident audit
- forensic reconstruction
- accountability

### ATE-RISK-ASSURANCE-POLICY-MODEL-v0.1.md

Owns:

- R0–R4 risk classes
- A0–A4 assurance requirements
- proportional controls

### ATE-TRUST-DOMAIN-FEDERATION-MODEL-v0.1.md

Owns:

- cross-domain evidence
- federation relationships
- local trust-domain control

### This document

Owns:

- consolidated component map
- system interaction sequence
- responsibility boundaries
- architecture navigation

---

## 22. Minimum Production Security Invariants

```text
RA-INV-1
The participant cannot authorize itself.

RA-INV-2
The participant cannot directly access governed resource credentials.

RA-INV-3
Every grant binds one exact action.

RA-INV-4
All controlling evidence must be current, valid, and non-revoked.

RA-INV-5
Authority is determined by trust-root role assignment, not signature possession alone.

RA-INV-6
Lower-assurance evidence cannot satisfy a higher-risk action.

RA-INV-7
Nonce reservation is atomic and single-use.

RA-INV-8
The executor independently verifies the signed grant.

RA-INV-9
Foreign trust never directly creates local capability.

RA-INV-10
Every trust decision and execution attempt is auditable.

RA-INV-11
Unknown state never becomes authorization.

RA-INV-12
Historical validity does not imply current executability.
```

---

## 23. Reference Interaction Sequence

```text
1.  Agent proposes action.
2.  Gateway canonicalizes action.
3.  Risk engine assigns R-class.
4.  Assurance policy determines A-profile.
5.  Evidence bundle assembled.
6.  Trust-root roles resolved.
7.  Revocation/current-state resolved.
8.  Active policy resolved.
9.  ATE verification gates execute.
10. Trust Decision Authority signs GRANT/DENY.
11. Executor receives decision + canonical action.
12. Executor rechecks signature/current state.
13. Nonce atomically RESERVED.
14. Credential acquired from vault.
15. Resource Adapter validates actual resource state.
16. Action executes once.
17. Nonce transitions to final execution state.
18. Audit evidence appended and chained.
```

---

## 24. Reference Denial Sequence

```text
1. Agent proposes action.
2. Gateway canonicalizes.
3. Required evidence cannot be established or a gate fails.
4. Trust Decision Authority signs TRUST_DENIED or processing stops securely.
5. No nonce authorization is created.
6. No governed credential is released.
7. No governed resource action occurs.
8. Denial and reason are audited.
```

---

## 25. Production Deployment Profiles

### P0 — Development

- same host allowed
- software fixture/low-assurance keys
- sandbox resources
- local executor

### P1 — Standard

- separate executor process/service
- protected credentials
- durable nonce registry
- active revocation
- tamper-evident audit

### P2 — High Assurance

- isolated executor host or hardened service
- hardware-backed sensitive keys
- short-lived credentials
- synchronous revocation
- stronger audit sink
- human approval for selected R3 actions

### P3 — Critical

- multi-party authorization
- threshold/quorum trust decisions
- hardware-backed execution identity
- strict network isolation
- independent audit replication
- mandatory human confirmation for R4

Deployment profile is separate from action risk but constrains the maximum risk class the deployment may safely service.

---

## 26. Architecture Boundary of Trust

Recommended boundary:

```text
Semi-trusted:
    model
    participant agent
    prompt/context
    foreign evidence input

Trusted control plane:
    trust-root registry
    current-state resolver
    ATE verifier
    policy authority
    trust-decision authority

Trusted enforcement plane:
    executor
    credential vault
    resource adapter

Trusted accountability plane:
    audit writer
    external checkpoint/replica
```

The goal is not to assume all trusted components are incorruptible; it is to prevent compromise of one component from silently granting all powers.

---

## 27. Explicit Non-Claims

This reference architecture does not claim:

- complete resistance to host-root compromise
- correct behavior of arbitrary Resource Adapters
- universal safety of AI models
- production-ready HSM or PKI implementation
- solved global federation
- immunity to compromised governing trust roots
- that behavioral evidence guarantees future conduct
- that all R4 actions should ever be fully automated

---

## 28. Architectural Completion State

The ATE production architecture family now defines:

- trust decision semantics
- attacker/threat model
- enforcement and executor mediation
- trust roots and key custody
- revocation and current trust state
- tamper-evident audit/accountability
- risk and assurance policy
- trust-domain federation
- consolidated component interaction

This is sufficient to define a coherent reference architecture before additional experimental implementation.

---

## 29. Next Recommended Work

Do not immediately implement the full production architecture.

The next high-value artifact should be:

**ATE Production Requirements & Conformance Profile v0.1**

Its purpose is to convert this architecture into explicit normative requirements using language such as:

```text
MUST
MUST NOT
SHOULD
SHOULD NOT
MAY
```

and define what an implementation must demonstrate before it may claim:

```text
ATE-CONFORMANT-P0
ATE-CONFORMANT-P1
ATE-CONFORMANT-P2
ATE-CONFORMANT-P3
```

This will create a stable boundary between architecture and future implementations and prevent experiments from quietly redefining the design.

---

## 30. Conclusion

ATE should be understood as a controlled chain from evidence to capability:

```text
Evidence
   ↓
Current Trust State
   ↓
Policy + Risk Evaluation
   ↓
Trust Decision
   ↓
Single-Use Capability
   ↓
Enforced Action
   ↓
Tamper-Evident Accountability
```

The participant proposes.

Independent authorities establish evidence.

ATE verifies.

The trust authority decides.

The executor enforces.

The audit system preserves accountability.

> **Trust the action, not the agent—and make the capability exist only when the evidence justifies it.**

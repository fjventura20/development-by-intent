# ATE Production Gap Analysis v0.1

**Status:** Architectural analysis  
**Date:** 2026-09-16  
**Program:** Agent Trust Envelope (ATE)  
**Predecessor:** ATE P1 Local Enforcement  
**Purpose:** Determine what remains between the successful local P1 proof and a production-capable Agent Trust Envelope, and identify the next highest-value milestone without prematurely authorizing another live experiment.

---

## 1. Executive Finding

ATE P1 established an important but deliberately narrow result:

> A local enforcement architecture can prevent an untrusted requester from bypassing authorization when requester, authority, and executor are distinct OS security principals and protected operations require cryptographically bound authorization, durable replay state, and crash-safe idempotent execution.

That result is necessary, but it is not yet sufficient for production.

The principal production gap is no longer basic local enforcement.

The next major unresolved dependency is:

> **How does one trusted component establish that another running agent/service is the specific qualified principal it claims to be, running the expected implementation and governance state, before authority is granted?**

That is the production trust-establishment problem.

The recommended next milestone is therefore not “more P1.”

It is a design milestone centered on:

**ATE Runtime Identity, Trust Root, and Attestation Architecture**

Only after that architecture is explicit should a P2 experiment be selected.

---

## 2. Production Target

For this analysis, a production-capable ATE is a system in which a human or agent can determine, with auditable evidence, whether another AI agent may perform a specific operation under defined conditions.

A production trust decision should be able to answer at least:

1. Who is this agent/runtime?
2. What implementation is actually running?
3. Who qualified or admitted it?
4. What Conditions of Agency has it accepted?
5. What Value Architecture governs it?
6. What behavioral evidence supports qualification?
7. What exact authority is being granted?
8. What policy/version is controlling the grant?
9. How long is the grant valid?
10. How is it revoked?
11. How is the executing runtime bound to the authorization?
12. How are execution and outcomes independently auditable?
13. What happens when identities, keys, policies, software, or qualifications change?

ATE is production-capable only when those answers are not merely asserted but can be verified and enforced.

---

## 3. What P1 Removes From the Critical Path

P1 materially reduced uncertainty in several areas.

### 3.1 Local requester bypass

No longer an open architectural question under the P1 threat model.

The successful pattern is:

- distinct requester UID;
- distinct authority UID;
- distinct executor UID;
- no requester ownership of trusted state;
- asymmetric authority signing;
- executor-local replay state;
- idempotent protected-resource mutation.

### 3.2 Local authorization transport

A requester may carry signed authorization artifacts without itself becoming trusted.

This allows ATE to use transport of signed evidence while requiring independent executor verification.

### 3.3 Local replay and crash safety

The P1 state machine demonstrates that durable authorization consumption and resource mutation do not require false claims of cross-store ACID atomicity.

The production architecture can build on:

```text
AUTHORIZED
    |
    v
PREPARED        <- durable acceptance
    |
    v
MUTATED         <- idempotent protected effect
    |
    v
COMPLETED       <- durable completion and audit
```

### 3.4 One decision / one effect identity

P1 established the importance of a stable `operation_id` that survives retries, clearance retrieval, delivery attempts, crashes, and restarts.

This should remain a production invariant.

---

## 4. Production Gap Categories

The remaining gaps fall into nine architectural domains:

1. Trust root and runtime identity
2. Attestation and provenance
3. Key custody and lifecycle
4. Qualification and requalification
5. Condition of Agency binding
6. Value Architecture binding and enforcement
7. Distributed authorization and revocation
8. Independent evidence and audit
9. Production operations and recovery

These gaps are related but should not be attacked simultaneously.

---

## 5. Gap 1 — Trust Root and Runtime Identity

**Priority:** CRITICAL  
**Dependency role:** Foundational  
**P1 coverage:** Minimal

P1 trusts that the operating system identities `ate-authority` and `ate-executor` correspond to the intended services.

Production cannot stop there.

The system must distinguish between:

```text
something running as ate-executor
```

and:

```text
the qualified ATE executor implementation,
running the approved software and governance state,
under the approved identity and trust domain
```

### 5.1 Required production guarantees

A production runtime identity should bind:

- service/agent identity;
- software identity;
- software version;
- configuration identity;
- host/runtime identity;
- trust-domain/project identity;
- signing/verification keys;
- governance-policy version;
- qualification state;
- validity period.

### 5.2 Threats

Without runtime identity binding, an attacker or operator mistake could substitute:

- an old binary;
- a modified binary;
- a different agent under the same OS account;
- a runtime with stale governance;
- a runtime copied from another project;
- a valid key used by the wrong implementation.

### 5.3 Architectural requirement

ATE needs an identity object stronger than username, process ID, hostname, or socket path.

A production ATE principal should have a cryptographic runtime identity rooted in a trusted issuance process.

---

## 6. Gap 2 — Attestation and Provenance

**Priority:** CRITICAL  
**Dependency role:** Builds on Gap 1  
**P1 coverage:** Out of scope

Identity says who a principal claims to be.

Attestation provides evidence about what is actually running.

### 6.1 Required evidence

Depending on deployment class, attestation may need to bind:

- executable digest;
- container/image digest;
- model/provider/runtime identity;
- policy bundle digest;
- Value Architecture version;
- Condition of Agency version;
- configuration digest;
- host identity;
- boot/session identity;
- secure time/freshness;
- qualification certificate.

### 6.2 Deployment tiers

ATE should not require one attestation mechanism for all environments.

A useful production model is tiered:

**Tier A — Local development**
- OS process identity;
- signed software manifest;
- trusted bootstrap;
- file hashes;
- short-lived runtime certificate.

**Tier B — Managed host/container**
- image digest;
- signed deployment manifest;
- workload identity;
- orchestrator/service identity;
- runtime certificate.

**Tier C — High assurance**
- hardware-backed device/workload identity;
- TPM/TEE or equivalent attestation;
- measured boot/runtime evidence;
- hardware-protected keys.

ATE should define semantics common to all tiers while allowing stronger roots where available.

---

## 7. Gap 3 — Key Custody and Lifecycle

**Priority:** CRITICAL  
**Dependency role:** Cross-cutting  
**P1 coverage:** Static local keys only

P1 showed why asymmetric signing matters.

Production must govern the full key lifecycle.

### 7.1 Required capabilities

- secure key generation;
- root/intermediate/service key hierarchy;
- separation of signing roles;
- rotation;
- expiration;
- revocation;
- compromise response;
- backup/recovery policy;
- key destruction;
- issuance audit;
- certificate or credential renewal;
- protection from rollback to retired keys.

### 7.2 Required distinction

ATE should distinguish at least:

- trust-root keys;
- qualification/attestation issuer keys;
- authority decision-signing keys;
- executor/runtime identity keys;
- audit-signing keys.

A single “ATE key” would create excessive blast radius.

### 7.3 Production rule

No long-lived authority should exist solely because a private key remains present on disk.

Authority should require:

```text
valid identity
+ valid key
+ current qualification
+ current governance binding
+ current authorization scope
```

---

## 8. Gap 4 — Agent Qualification and Requalification

**Priority:** CRITICAL  
**Dependency role:** Core ATE purpose  
**P1 coverage:** Not addressed

This gap connects directly to the human-professional analogy behind ATE.

Humans are often permitted to work on sensitive projects only after credential verification, training, role qualification, policy acknowledgment, and periodic recertification.

ATE needs an equivalent mechanism for agents.

### 8.1 Qualification record

A production agent qualification should identify:

- agent/runtime identity;
- evaluator/issuer;
- qualification class;
- tested capabilities;
- prohibited capabilities;
- behavioral test suite/version;
- evidence references;
- pass/fail result;
- issuance timestamp;
- expiration/requalification date;
- governance versions accepted;
- permitted trust domains.

### 8.2 Requalification triggers

Requalification should be required when materially relevant properties change, including:

- model/runtime change;
- major software version change;
- Value Architecture change;
- Condition of Agency change;
- policy change;
- security incident;
- key compromise;
- material behavioral drift;
- qualification expiration.

### 8.3 Important constraint

Qualification is not universal trust.

It should always be scoped:

> qualified **for what**, under **which conditions**, until **when**, based on **which evidence**?

---

## 9. Gap 5 — Condition of Agency Binding

**Priority:** HIGH  
**Dependency role:** Governance commitment  
**P1 coverage:** Not integrated

Condition of Agency defines the commitments under which an agent may participate.

Production ATE must prove more than “a document exists.”

It must bind the runtime identity to the accepted condition.

### 9.1 Required production properties

The ATE should record:

- CoA document/version digest;
- acceptance event;
- accepting agent/runtime identity;
- issuer/project identity;
- validity interval;
- supersession rules;
- revocation/withdrawal state;
- evidence that the acceptance applies to the active runtime/session.

### 9.2 Prior lesson

Governance acceptance that is not bound to the actual executing session is insufficient.

Production must therefore bind:

```text
runtime identity
    +
governance commitment
    +
authorization
```

not merely store them as adjacent records.

---

## 10. Gap 6 — Value Architecture Binding and Enforcement

**Priority:** HIGH  
**Dependency role:** Normative architecture  
**P1 coverage:** Enforcement substrate only

Value Architecture defines the normative constraints under which an agent should reason and act.

ATE must answer two separate questions:

1. Which Value Architecture does this runtime claim to operate under?
2. What evidence justifies relying on that claim?

### 10.1 Required binding

A production ATE should include:

- VA version/digest;
- issuer/owner;
- active status;
- relationship to the agent qualification;
- behavioral evidence;
- exceptions/overrides;
- authorization constraints derived from VA.

### 10.2 Important distinction

ATE should not pretend that cryptographically signing a VA document proves internal model compliance.

Cryptography can prove:

- which VA was declared;
- which VA was accepted;
- which VA was used during qualification;
- which VA version an authorization references.

Behavioral evidence is still required to support claims that the agent actually operates consistently with that architecture.

---

## 11. Gap 7 — Distributed Authorization and Revocation

**Priority:** HIGH  
**Dependency role:** Required beyond one host  
**P1 coverage:** Local only

P1's authority and executor share one local environment.

Production ATE will eventually span processes, containers, machines, cloud services, external agents, and possibly multiple organizations.

### 11.1 New distributed problems

- network partitions;
- stale revocation state;
- clock skew;
- duplicated delivery;
- lost responses;
- authority availability;
- trust-domain boundaries;
- cross-host replay;
- certificate expiration;
- service migration;
- concurrent authorities.

### 11.2 Production requirement

ATE should preserve the P1 principle:

> authorization must have an explicit issuance/linearization rule and a stable operation identity.

But distributed systems need additional freshness mechanisms.

Possible mechanisms include:

- short-lived signed clearances;
- online authority checks;
- revocation epochs;
- signed revocation feeds;
- lease semantics;
- policy-version epochs.

The production design should define one authoritative model rather than mixing several loosely.

---

## 12. Gap 8 — Independent Evidence and Audit

**Priority:** HIGH  
**Dependency role:** Accountability architecture  
**P1 coverage:** Local tamper detection

P1 keeps audit integrity under executor-owned state.

Production needs independent preservation.

If the same principal that performs an operation also controls the only audit record, the audit system is weaker than the operational system.

### 12.1 Production audit goals

- append-only or tamper-evident records;
- external anchoring;
- independent storage;
- trusted timestamps;
- actor/runtime identity;
- decision and clearance references;
- operation identity;
- outcome;
- policy/governance versions;
- evidence-chain references;
- retention policy;
- export/query support.

### 12.2 Architectural rule

Production accountability should not depend entirely on the principal being audited.

A likely production pattern is:

```text
executor
    |
    +--> local durable audit
    |
    +--> independently controlled audit sink
```

The external sink need not block every operation, but it should provide independent evidence capable of detecting later local tampering or deletion.

---

## 13. Gap 9 — Production Operations and Recovery

**Priority:** HIGH  
**Dependency role:** Operational viability  
**P1 coverage:** Narrow restart/crash cases

A system can be cryptographically sound and still fail operationally.

Production ATE requires explicit lifecycle architecture.

### 13.1 Required areas

- service supervision;
- startup ordering;
- readiness;
- controlled shutdown;
- state migration;
- backups;
- recovery;
- disaster recovery;
- upgrade authorization;
- configuration management;
- rollback prevention;
- key migration;
- health monitoring;
- capacity limits;
- denial-of-service handling;
- retention/cleanup of expired decisions;
- operational incident response.

### 13.2 Key lesson from P1 implementation

A bootstrap script that says “OK” before services are actually alive is not sufficient.

Production trust requires observed readiness, not assumed launch success.

That lesson generalizes:

> A declared state is not evidence of an actual state.

---

## 14. Dependency Graph

The remaining work is not flat.

```text
                    Trust Root
                        |
                        v
                Runtime Identity
                        |
                        v
                   Attestation
                        |
          +-------------+-------------+
          |                           |
          v                           v
   Key Lifecycle                Qualification
                                      |
                         +------------+------------+
                         |                         |
                         v                         v
                 Condition of Agency       Value Architecture
                         \                         /
                          \                       /
                           +----------+----------+
                                      |
                                      v
                         Bounded Authorization
                                      |
                                      v
                         Distributed Enforcement
                                      |
                                      v
                         Independent Evidence
                                      |
                                      v
                         Operations / Recovery
```

P1 largely validated the local bounded-authorization/enforcement mechanics.

The unresolved upstream identity and attestation layers now dominate the risk.

---

## 15. Gap Prioritization

| Priority | Gap | Why it matters now | Experiment now? |
|---|---|---|---|
| 1 | Trust root + runtime identity | Every later claim depends on knowing which runtime is acting | No — design first |
| 2 | Attestation/provenance | Identity without evidence of implementation/governance state is weak | No — design first |
| 3 | Key custody/lifecycle | Identity, attestation, authorization, and audit all depend on key trust | No — architecture first |
| 4 | Qualification/requalification | Converts “known runtime” into “qualified runtime” | Later |
| 5 | CoA binding | Must bind commitment to actual runtime/session | Later |
| 6 | VA binding/evidence | Connects normative architecture to qualification and authorization | Later |
| 7 | Distributed revocation | Required when trust spans hosts | Candidate later milestone |
| 8 | Independent audit | Required for production accountability | Later |
| 9 | Operations/recovery | Required before deployment, but not the next scientific uncertainty | Later |

---

## 16. Recommended Next Architectural Artifact

The next artifact should be:

**ATE Runtime Identity, Trust Root & Attestation Architecture v0.1**

It should answer:

- What is an ATE principal?
- What is the root of trust?
- Who may issue an agent/runtime identity?
- What does a runtime identity bind?
- What evidence proves software/runtime provenance?
- How is governance state bound into identity?
- How does a verifier establish freshness?
- How are keys issued, rotated, and revoked?
- How does a local identity become usable across hosts?
- Which assurance tiers are supported?

The artifact should remain design-only.

No live experiment should begin until those semantics are explicit.

---

## 17. Candidate Runtime Identity Model

A production ATE runtime identity could conceptually contain:

```text
ATE Runtime Identity
|
+-- principal_id
+-- trust_domain_id
+-- runtime_instance_id
+-- software_manifest_digest
+-- model/runtime identifier
+-- configuration_digest
+-- host/workload identity
+-- public verification key
+-- qualification_id
+-- coa_digest
+-- value_architecture_digest
+-- policy_epoch
+-- issued_at
+-- valid_until
+-- issuer
+-- attestation evidence reference
+-- signature chain
```

This is not yet a frozen schema.

Its purpose is to clarify that production identity must bind far more than a service name.

---

## 18. Candidate P2 Question

Do not freeze P2 yet.

After the Runtime Identity / Trust Root / Attestation architecture is complete, the likely next empirical question is:

> **Can an executor cryptographically distinguish an authorized, qualified runtime instance from an unqualified or substituted runtime instance, without trusting the requester or a mutable runtime name?**

A lean P2 could then test:

- valid runtime credential accepted;
- wrong runtime rejected;
- copied credential rejected if instance-bound;
- expired credential rejected;
- stale governance version rejected;
- substituted binary/manifest rejected;
- revoked runtime rejected;
- replayed attestation rejected.

However, this should remain a candidate until the identity architecture defines exactly what must be proven.

---

## 19. What Not to Work On Yet

To conserve effort and model quota, do not immediately invest in:

- large multi-agent experiments;
- remote distributed harnesses;
- hardware TPM/TEE integration;
- cloud deployment;
- full PKI implementation;
- UI/dashboard work;
- more SQLite hardening;
- performance optimization;
- large-scale behavioral scoring.

Those tasks may become relevant later, but they are downstream of the unresolved trust-root and runtime-identity architecture.

---

## 20. Relationship to the Larger Architecture

The current research program can now be organized as:

```text
INSA
Application / information-flow architecture
        |
        v
Value Architecture
Normative architecture
        |
        v
Condition of Agency
Commitment architecture
        |
        v
Agent Trust Envelope
Trust / qualification / authorization architecture
        |
        v
Enforcement Plane
Authority and capability architecture
        |
        v
Evidence & Audit
Accountability architecture
```

P1 supplied concrete evidence for the Enforcement Plane.

The next work should strengthen the upstream part of ATE:

```text
identity
    ->
provenance
    ->
qualification
    ->
governance binding
    ->
authorization
    ->
enforcement
```

---

## 21. Decision

### Current decision

**Do not begin P2 implementation.**

### Next work

Create:

**ATE Runtime Identity, Trust Root & Attestation Architecture v0.1**

### Reason

P1 has reduced uncertainty about local enforcement enough that the dominant unresolved risk has moved upstream.

We now need to establish what a trusted agent/runtime is, how that identity is issued, what evidence binds it to actual implementation and governance state, and how another principal verifies it.

Only then can the next experiment test the right thing.

---

## 22. Final Production-Gap Statement

The transition from P1 to production can be summarized as:

```text
P1 proved:
"Given trusted authority/executor identities,
can the requester be structurally prevented from bypassing enforcement?"
        |
        | YES, under the frozen P1 threat model
        v
Production now asks:
"Why should anyone trust that the authority/executor/agent runtime
is actually the qualified principal it claims to be?"
```

That is the next problem.

The strongest next contribution to ATE is therefore not another enforcement test.

It is a precise architecture for **runtime identity, trust roots, provenance, and attestation**.

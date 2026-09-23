# ATE P1 Local Enforcement Harness v0.1 — Design

**Status:** DESIGN ONLY — NOT FROZEN
**Date:** 2026-09-15
**Authority:** PI direction following ATE v0.3.1 frozen status
**Upstream frozen baseline:** `f903478154e2b484f8a49295ba0692d0a5a4f260`
**Upstream status:** `ATE_V0_3_1_END_TO_END_TRUST_ESTABLISHED`
**Execution policy for this milestone:** local deterministic implementation and tests only; no Hermes participant invocation, no premium evaluator, no live-model replication, no large candidate matrix.

---

## 1. Purpose

ATE v0.3.1 established a proof-of-concept trust-decision chain: a governed action may receive a deterministic, evidence-backed binary trust verdict and a single-use authorization nonce can bind that verdict to execution.

P1 addresses the next question:

> **Can an already-established trust decision be enforced at the actual resource boundary even when the requesting agent is malicious, stale, concurrent, revoked, or attempting to bypass the trusted execution path?**

This milestone therefore moves from **trust determination** toward **trust enforcement**.

P1 does not redesign the ATE trust-decision mechanism. It treats ATE v0.3.1 as an immutable upstream dependency.

---

## 2. Controlling design principle

A trust decision is not security unless the resource boundary refuses unauthorized execution.

Accordingly, P1 adopts the following invariant:

> **No protected operation succeeds solely because a caller possesses a valid-looking request, token, decision, or nonce. The privileged executor must independently re-establish all execution-time predicates immediately before the protected operation and must be the only component possessing the credential capable of reaching the protected resource.**

The requesting agent is treated as potentially hostile after trust issuance.

---

## 3. Scope

P1 v0.1 is deliberately narrow. It implements and tests seven local enforcement properties:

1. Direct resource bypass denial.
2. Executor credential separation.
3. Durable nonce state across restart.
4. Executor reverification immediately before action.
5. Concurrent replay protection.
6. Revocation enforcement.
7. Tamper-evident audit state.

All tests are local and deterministic.

---

## 4. Explicit non-goals

P1 v0.1 does **not** claim or attempt:

- distributed consensus;
- multi-host nonce coordination;
- remote attestation;
- HSM, TPM, enclave, or hardware-backed key custody;
- cloud IAM integration;
- production PKI;
- OCSP/CRL interoperability;
- multi-agent federation;
- network-isolated sandboxing;
- kernel mandatory access control;
- container escape resistance;
- hostile operating-system administrator resistance;
- generalized authorization language design;
- performance benchmarking;
- production availability or failover;
- universal attack resistance;
- independent evaluator replication;
- live-model execution.

Success means the seven specified enforcement properties are demonstrated under the frozen local threat model only.

---

## 5. Threat model

### 5.1 Adversary capabilities

The requesting agent or caller MAY:

- submit malformed inputs;
- alter request fields after a trust decision was issued;
- retain and replay old decisions;
- retain and replay old nonces;
- submit the same nonce concurrently from multiple threads/processes;
- attempt direct access to the protected resource;
- attempt to call lower-level resource functions directly;
- continue operating after authorization has been revoked;
- crash or restart the executor between authorization events;
- tamper with audit-log files after execution;
- reorder or delete audit records;
- inspect all unprivileged application state.

### 5.2 Trusted computing base for P1

The P1 local trusted computing base is limited to:

- the local operating-system process and file-permission model;
- the privileged executor process;
- the executor's private credential store;
- the durable nonce database implementation;
- the revocation registry;
- the trust-decision public verification material;
- the audit-chain signing/MAC material or equivalent integrity key;
- deterministic clock fixtures used by tests.

### 5.3 Out-of-scope adversary

An attacker with root/administrator-equivalent control over the host is out of scope for P1 v0.1.

This limitation must remain explicit in every closeout claim.

---

## 6. Architectural components

### 6.1 Requesting Agent

Unprivileged caller. It may construct requests and present ATE artifacts but possesses no resource credential.

### 6.2 Enforcement Gateway

Unprivileged-facing API boundary. Accepts an execution request and forwards it to the executor. It is not trusted to authorize by itself.

### 6.3 Privileged Executor

The only component allowed to perform the protected operation.

Responsibilities:

- verify trust-decision authenticity;
- bind the decision to the exact requested operation and target;
- query revocation state;
- atomically reserve/consume nonce state;
- perform final reverification immediately before the privileged operation;
- perform the privileged operation using executor-only credentials;
- append a tamper-evident audit record;
- fail closed on every verification, persistence, revocation, or integrity error.

### 6.4 Protected Resource

A local deterministic fixture representing a privileged target. It MUST reject calls not bearing the executor-held credential.

For v0.1, the preferred fixture is a small local resource adapter that requires an unguessable executor credential held outside requester-visible state.

### 6.5 Durable Nonce Store

Persistent storage with atomic uniqueness semantics.

Required logical states:

- `UNSEEN`
- `RESERVED`
- `CONSUMED`
- `REVOKED` if nonce-specific revocation is implemented

The store MUST survive executor restart.

SQLite is acceptable for the local P1 harness if configured so that the nonce transition occurs transactionally and uniqueness is enforced by schema constraints, not by an in-memory check-then-write sequence.

### 6.6 Revocation Registry

Persistent registry consulted at execution time.

Minimum supported revocation dimensions:

- trust-decision identifier;
- capability/envelope identifier;
- principal/session identifier where available.

P1 v0.1 needs only one deterministic revocation mechanism to demonstrate the property; it does not need production PKI semantics.

### 6.7 Tamper-Evident Audit Log

Append-oriented audit stream in which each record commits to its predecessor.

Minimum record fields:

- monotonically increasing sequence number;
- event timestamp from deterministic clock fixture;
- request identifier;
- trust-decision identifier;
- nonce identifier;
- operation;
- target;
- outcome;
- reason code;
- previous-record digest;
- current-record digest or MAC/signature.

The verifier MUST detect deletion, insertion, mutation, and reordering within the retained chain.

---

## 7. Privilege boundary

The most important P1 boundary is not a software class boundary. It is a credential boundary.

The requester MUST NOT possess:

- executor resource credential;
- audit integrity key;
- nonce-store mutation authority except through the executor API;
- revocation-registry mutation authority except through the test/administrative control path;
- trust-decision signing key.

The executor MAY possess:

- resource credential;
- verification keys required to validate upstream artifacts;
- nonce-store write authority;
- audit integrity key;
- revocation read authority.

Administrative test code MAY possess revocation-write authority solely to stage deterministic test conditions.

A test that merely hides a credential in a Python object is insufficient. The harness must demonstrate that the requester-facing execution path never receives the privileged credential as an argument, return value, serialized artifact, environment field exposed to the requester fixture, or shared request structure.

---

## 8. Execution protocol

For each requested governed action, the executor performs the following sequence.

### E1 — Parse and canonicalize request

Reject malformed or non-canonical requests.

Output: canonical `(principal, session, operation, target, decision_id, envelope_id, nonce)` tuple.

### E2 — Verify trust-decision signature

Verify the decision under the designated trust-authority public key.

Failure: `PX_TRUST_DECISION_INVALID`.

### E3 — Verify request/decision binding

The exact canonical operation, target, principal/session binding, envelope/capability identifier, and nonce MUST match the signed decision or signed artifacts it references.

Failure examples:

- `PX_OPERATION_BINDING_MISMATCH`
- `PX_TARGET_BINDING_MISMATCH`
- `PX_SESSION_BINDING_MISMATCH`
- `PX_NONCE_BINDING_MISMATCH`

### E4 — Check expiry/freshness

Reject expired execution authority.

Failure: `PX_AUTHORITY_EXPIRED`.

### E5 — Check revocation

Consult the durable revocation registry after signature/binding verification and before nonce reservation.

Failure: `PX_AUTHORITY_REVOKED`.

### E6 — Atomically reserve nonce

The durable nonce store MUST perform one atomic transition:

`UNSEEN -> RESERVED`

Exactly one concurrent caller may succeed.

Failure: `PX_NONCE_REPLAY_OR_BUSY`.

### E7 — Immediate executor reverification

Immediately before the privileged resource call, the executor MUST re-check all predicates whose truth may have changed since E2-E6.

At minimum:

- revocation state;
- authority expiry/freshness;
- exact request binding;
- nonce still belongs to this reservation/transaction.

This check is intentionally redundant. It closes the gap between authorization and use.

Failure after nonce reservation MUST fail closed and MUST produce a terminal nonce disposition that cannot be replayed as fresh authority.

Recommended local rule:

- if execution never begins after reservation because revalidation fails, transition `RESERVED -> CONSUMED` with denied outcome, not back to `UNSEEN`.

This prevents an authorization from becoming reusable after a race-window failure.

### E8 — Privileged resource operation

Invoke the resource adapter using the executor-only credential.

The requester never receives this credential.

### E9 — Finalize nonce

Atomically transition:

`RESERVED -> CONSUMED`

The consumed record MUST retain outcome metadata sufficient for deterministic replay diagnosis.

### E10 — Append audit record

Append a chained audit event covering the final outcome.

If audit append fails, the executor MUST return a fail-closed system error unless the implementation can prove the resource mutation and audit append are transactionally coupled. P1 v0.1 is not required to achieve such coupling, so the simpler acceptable design is to make the protected resource operation itself deterministic/reversible in tests and fail the case if audit durability cannot be established.

---

## 9. Required security invariants

### P1-I1 — No bypass

No requester-controlled code path can successfully mutate/read the protected fixture using the privileged operation without passing through the executor.

### P1-I2 — Credential non-disclosure

The executor resource credential never appears in requester-visible state.

### P1-I3 — Restart-durable replay denial

A nonce consumed before executor shutdown remains unusable after restart.

### P1-I4 — Use-time authorization

Execution depends on authorization state at the moment immediately preceding privileged use, not merely at trust-decision issuance.

### P1-I5 — Atomic replay exclusion

For N concurrent requests using the same nonce, success count MUST be exactly one or zero; it MUST never exceed one.

### P1-I6 — Revocation beats stale grant

A previously valid grant revoked before privileged use MUST NOT execute.

### P1-I7 — Audit tampering detectable

Any mutation, deletion, insertion, or reorder of retained audit records MUST cause audit verification failure.

### P1-I8 — Fail closed

Any parse, signature, persistence, revocation, concurrency, audit-integrity, or resource-credential error denies privileged execution.

---

## 10. Persistence requirements

### 10.1 Nonce database

Suggested minimal schema:

```sql
CREATE TABLE nonces (
    nonce TEXT PRIMARY KEY,
    state TEXT NOT NULL CHECK(state IN ('RESERVED','CONSUMED')),
    reservation_id TEXT,
    decision_id TEXT NOT NULL,
    first_seen_at TEXT NOT NULL,
    finalized_at TEXT,
    outcome TEXT
);
```

An absent row represents `UNSEEN`.

Atomic reservation pattern:

```sql
BEGIN IMMEDIATE;
INSERT INTO nonces (... state='RESERVED' ...);
COMMIT;
```

The primary-key uniqueness constraint is the authoritative replay barrier.

A failed duplicate insert means the nonce is already reserved or consumed.

### 10.2 Revocation database

Suggested minimal schema:

```sql
CREATE TABLE revocations (
    subject_type TEXT NOT NULL,
    subject_id TEXT NOT NULL,
    revoked_at TEXT NOT NULL,
    reason TEXT NOT NULL,
    PRIMARY KEY(subject_type, subject_id)
);
```

### 10.3 Audit chain

Canonicalize each record before computing the integrity value.

Example conceptual digest:

`record_digest = SHA256(canonical_record_without_digest || previous_record_digest)`

A keyed MAC or signature SHOULD be used so that a caller able to rewrite the file cannot simply recompute the entire chain. For P1 v0.1, HMAC-SHA256 with an executor-only audit key is sufficient for the local proof-of-concept.

The verifier recomputes each link and validates sequence continuity.

---

## 11. Deterministic test matrix

The v0.1 implementation MUST include at least the following seven controlling tests plus one valid-control test.

### T0 — Valid authorized execution

**Purpose:** positive control.

Setup:

- valid signed trust decision;
- exact operation/target binding;
- fresh nonce;
- no revocation;
- valid executor credential;
- clean audit chain.

Expected:

- execution succeeds exactly once;
- nonce becomes `CONSUMED`;
- one success audit record appended;
- replay denied.

### T1 — Direct resource bypass denial

Attempt to invoke the protected resource through the requester path without the executor-held credential.

Expected:

- operation denied;
- protected state unchanged;
- bypass does not create a false success audit event.

### T2 — Executor credential separation

Inspect all requester-visible request/result structures and invoke the requester API.

Expected:

- executor credential absent from caller inputs, outputs, serialized artifacts, and requester fixture state;
- direct protected-resource call remains impossible.

### T3 — Durable nonce across restart

1. Execute valid request with nonce N.
2. Confirm N is consumed.
3. Destroy executor instance/process fixture.
4. Reinitialize executor from persistent stores.
5. Replay N.

Expected:

- replay denied after restart;
- no second resource mutation.

### T4 — Executor reverification

1. Establish a valid grant.
2. Reach a deterministic pre-use barrier after initial verification but before resource invocation.
3. Revoke the authorization while paused.
4. Release barrier.

Expected:

- E7 detects revocation;
- resource operation does not occur;
- nonce cannot later be reused;
- denial audit event recorded.

### T5 — Concurrent replay protection

Launch at least 16 local workers/threads/processes attempting the same valid nonce concurrently.

Expected:

- exactly one execution success;
- all others denied with replay/busy outcome;
- protected resource mutation count exactly one;
- persistent nonce final state `CONSUMED`.

For stronger local evidence, repeat deterministically across multiple scheduling rounds without model calls.

### T6 — Revocation before execution

Issue valid trust material, persist revocation, then call executor.

Expected:

- `PX_AUTHORITY_REVOKED`;
- no resource mutation;
- no successful nonce reservation if revocation is detected at E5.

### T7 — Tamper-evident audit state

Generate a valid audit chain containing at least four events, then test separate copies with:

- one field mutated;
- one middle record deleted;
- two records reordered;
- one fabricated record inserted.

Expected:

- verifier rejects every tampered chain;
- untouched control chain verifies successfully.

---

## 12. Test isolation rules

Each test MUST use a fresh temporary directory except tests intentionally exercising restart durability.

Each test MUST initialize:

- new resource fixture;
- fresh nonce database unless persistence is under test;
- fresh revocation database unless persistence is under test;
- fresh audit file/key unless tamper behavior is under test;
- deterministic keys or seeded fixtures.

Tests MUST NOT depend on wall-clock timing for correctness. Concurrency barriers/events should coordinate race windows explicitly.

---

## 13. Evidence requirements

The implementation phase SHOULD produce machine-readable evidence containing:

- harness version;
- upstream frozen commit SHA;
- implementation commit SHA;
- test identifier;
- fixture identifiers;
- nonce pre-state;
- nonce post-state;
- revocation state observed at initial verification;
- revocation state observed at immediate reverification;
- resource mutation count;
- execution outcome;
- denial reason code where applicable;
- audit verification result;
- credential-separation assertion result;
- concurrency worker count and success count;
- restart boundary marker for T3.

Recommended evidence file:

`evidence/p1_local_enforcement_evidence.json`

Recommended human-readable test log:

`evidence/p1_local_enforcement_test_log.txt`

---

## 14. Success criteria

P1 v0.1 MAY be classified:

`ATE_P1_LOCAL_ENFORCEMENT_ESTABLISHED`

only if all of the following hold:

1. T0 passes.
2. T1-T7 all pass.
3. No test is skipped.
4. No test relies on a mocked assertion that bypasses the actual enforcement component under test.
5. Concurrent replay success count is never greater than one.
6. Restart test proves persistence using a newly constructed executor instance reading the prior durable store.
7. Revocation-between-check-and-use test reaches a real deterministic barrier between initial verification and immediate pre-use reverification.
8. Protected resource operation requires a credential unavailable to the requester fixture.
9. Audit tampering is detected for mutation, deletion, insertion, and reorder cases.
10. Upstream frozen ATE v0.3.1 artifacts remain byte-identical.

Any failure yields:

`ATE_P1_LOCAL_ENFORCEMENT_NOT_ESTABLISHED`

with the failing invariant(s) recorded.

There is no partial-pass production claim.

---

## 15. Early-stop rules

To conserve subscription and engineering resources, implementation testing stops immediately on any architectural failure that invalidates the remaining matrix, including:

- requester can directly operate the protected resource;
- requester can obtain executor credential;
- duplicate nonce execution succeeds more than once;
- consumed nonce becomes usable after restart;
- executor performs action after deterministic revocation before use;
- audit verifier accepts a known modified chain.

Fix the design/implementation locally before running further cases.

No Hermes or additional model calls are justified by a deterministic local failure.

---

## 16. Proposed repository layout

```text
architecture/experimental/ate-p1-enforcement-harness/
├── ATE-P1-LOCAL-ENFORCEMENT-HARNESS-DESIGN-v0.1.md
├── implementation/
│   ├── __init__.py
│   ├── models.py
│   ├── durable_nonce_store.py
│   ├── revocation_registry.py
│   ├── audit_chain.py
│   ├── protected_resource.py
│   ├── privileged_executor.py
│   └── test_fixtures.py
├── tests/
│   └── test_p1_local_enforcement.py
└── evidence/
    ├── p1_local_enforcement_evidence.json
    └── p1_local_enforcement_test_log.txt
```

The design file is the only artifact authorized by the present design step. Implementation files are proposed, not yet created by this document.

---

## 17. Implementation guidance

### 17.1 Prefer standard library plus existing project crypto dependency

Do not introduce infrastructure merely to prove the local property.

SQLite, filesystem permissions, Python concurrency primitives, canonical JSON, SHA-256, and HMAC are sufficient for most P1 mechanics.

If the repository already has a trusted Ed25519 utility from ATE v0.3.1, reuse its behavior by import or exact local adaptation only if doing so does not mutate frozen files.

### 17.2 No modification of frozen upstream artifacts

P1 MUST NOT edit any ATE v0.3.1 frozen file.

If upstream behavior is needed, import it read-only or copy the minimal interface into the new experimental area with provenance documented.

### 17.3 Treat `trust_decide()` as upstream

P1 is not a new trust-decision experiment.

The executor receives a pre-established valid/invalid trust-decision fixture shaped consistently with the frozen ATE interface and focuses on enforcement-time behavior.

### 17.4 Fail closed on persistence errors

If nonce DB, revocation DB, or audit integrity state cannot be read/verified when required, execution is denied.

### 17.5 Make the race deterministic

Use barriers/events to guarantee the revocation race and concurrent replay windows are actually exercised. Do not rely on `sleep()` as evidence of a concurrency property.

---

## 18. Adversarial questions implementation must answer

1. What stops an agent from bypassing `privileged_executor.py` and importing `protected_resource.py` directly?
2. Where physically/logically does the executor credential live, and why can the requester fixture not retrieve it?
3. What exact database constraint prevents two concurrent callers from both reserving the nonce?
4. What state survives destruction and recreation of the executor object?
5. What is rechecked after nonce reservation and immediately before privileged use?
6. What happens to a reserved nonce when late reverification fails?
7. Can a stale but correctly signed trust decision execute after revocation?
8. Can the caller rewrite the audit chain and recompute valid integrity values without the executor audit key?
9. What happens if audit verification itself fails on startup?
10. Does any exception path accidentally call the resource before final authorization completes?

A closeout that cannot answer these concretely is insufficient.

---

## 19. Relationship to future production architecture

P1 is an enforcement-substrate proof, not the production architecture.

If established, P1 would justify proceeding to a later phase addressing some combination of:

- OS-level service separation;
- real IPC boundary;
- dedicated service account;
- key custody and rotation;
- distributed nonce/replay protection;
- production revocation distribution;
- append-only external audit sink;
- crash-consistent coupling between resource mutation and evidence;
- remote execution trust;
- multi-agent authorization federation.

Those are explicitly deferred until the local enforcement invariants are demonstrated.

---

## 20. Governing claim boundary

The strongest claim permitted by a successful P1 v0.1 is:

> In the deterministic local harness and under the stated non-root threat model, an ATE-authorized action can be enforced through an executor-controlled resource boundary such that direct bypass is denied, privileged credentials remain separated from the requester, nonce replay remains denied across restart and concurrent attempts, authorization is reverified at use time, revocation is enforced before privileged use, and retained audit records are tamper-evident.

It MUST NOT be generalized to production security, distributed enforcement, hostile-host resistance, or universal agent safety.

---

## 21. Decision gate

**Design disposition:** `READY_FOR_LOCAL_IMPLEMENTATION_REVIEW`

Before implementation, review this design specifically for:

- bypass assumptions;
- credential-boundary realism;
- nonce transaction correctness;
- TOCTOU/reverification semantics;
- revocation race semantics;
- audit-key separation;
- crash-state ambiguity.

If no blocking flaw is found, proceed directly to the smallest deterministic local implementation and T0-T7 test matrix.

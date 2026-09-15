# ATE P1 Local Enforcement Harness v0.1.1 — Corrective Design

**Status:** DESIGN ONLY — NOT FROZEN  
**Date:** 2026-09-15  
**Supersedes for implementation:** `ATE-P1-LOCAL-ENFORCEMENT-HARNESS-DESIGN-v0.1.md`  
**Preserves:** v0.1 unchanged as historical design input  
**Upstream frozen ATE baseline:** `f903478154e2b484f8a49295ba0692d0a5a4f260`

## 1. Purpose

This revision incorporates the adversarial review findings for P1 before implementation. The objective remains unchanged: enforce an already-established ATE trust decision at the actual local resource boundary under deterministic, local-only conditions.

## 2. Controlling corrections

### C1 — Atomic state change, nonce finalization, audit append, and audit-head update

The v0.1 sequence allowed a protected mutation to occur before audit persistence was known to be durable. Returning an error after the mutation would not constitute a true fail-closed result.

For v0.1.1, the protected resource fixture, nonce state, revocation state consulted for the action, audit record, and audit-head state MUST all reside in one local SQLite authority database and MUST be committed in one transaction.

No protected mutation is considered successful unless the entire transaction commits.

If any operation fails before commit, the transaction MUST roll back and protected state MUST remain unchanged.

### C2 — Revocation/use ordering

The final revocation check and protected mutation MUST occur inside the same SQLite write transaction.

The implementation sequence is:

1. `BEGIN IMMEDIATE`.
2. Revalidate decision signature and exact request binding as required.
3. Read current revocation state inside the transaction.
4. Establish nonce uniqueness inside the same transaction.
5. Perform the deterministic protected-resource mutation in database state.
6. Finalize nonce state.
7. Append authenticated audit record.
8. Update authenticated audit head.
9. `COMMIT`.

A revocation transaction serialized before this transaction MUST be observed and deny execution. A revocation serialized after the protected transaction commits does not retroactively invalidate the completed action.

This establishes a deterministic local ordering rather than claiming elimination of revocation races in distributed systems.

### C3 — Audit tail-truncation detection

A hash/MAC chain alone cannot prove that the final records have not been removed if verification begins only from the retained file/database rows.

v0.1.1 therefore introduces a protected audit anchor stored separately from the audit-record sequence within the same authority database schema and updated atomically with each audit append.

The anchor contains at minimum:

- expected final sequence number;
- expected final record MAC/digest;
- anchor MAC under the executor-only audit key.

Audit verification MUST compare the reconstructed final chain state against the authenticated anchor. Mutation, insertion, deletion, reordering, and tail truncation MUST all fail verification.

### C4 — Real requester/executor process boundary

Credential separation MUST be demonstrated across separate local processes, not merely separate Python objects.

The requester process MUST NOT receive:

- the protected-resource credential/key;
- the audit integrity key;
- direct write access to the authority database;
- revocation-administration capability;
- trust-decision signing authority.

The executor process owns these authorities and exposes only a narrow local IPC request interface containing non-secret execution material.

P1 still does not claim resistance to a host administrator/root attacker.

### C5 — Crash semantics for nonce state

The authoritative nonce state transition MUST occur only inside the same transaction as the resource mutation and audit append.

An execution transaction that crashes or aborts before commit leaves no partially committed `RESERVED` authorization capable of later execution.

The database schema MAY internally use a reservation marker during the transaction, but no committed intermediate state may create ambiguous reusable authority.

After restart:

- a committed consumed nonce remains consumed;
- an uncommitted transaction is rolled back by SQLite and is treated as never executed;
- protected resource state and audit state MUST agree with nonce state.

### C6 — Stable resource identity binding

Authorization MUST bind to a canonical stable resource identifier, not solely to caller-controlled path text.

For the P1 fixture, each protected resource receives a generated immutable `resource_id`. The signed/verified execution request binds operation plus `resource_id`. Human-readable path/name fields are metadata only.

This prevents path-alias or path-rebinding tests from falsely appearing authorized because text happens to match.

### C7 — Audit verification on startup

Before the executor accepts a new protected request after startup/restart, it MUST verify:

- the complete retained audit chain;
- sequence continuity;
- record MACs;
- the authenticated audit anchor;
- consistency of the latest committed nonce/resource/audit state required by the harness.

Failure produces a startup-locked state such as `PX_AUDIT_INTEGRITY_FAILURE`. Protected execution MUST remain disabled until the test fixture is reset by the authorized harness control path.

## 3. Revised local architecture

```text
Requester process
      |
      | narrow local IPC
      v
Executor process
      |
      | BEGIN IMMEDIATE
      v
SQLite authority database
  - protected resource fixture state
  - durable nonce state
  - revocation state
  - audit records
  - authenticated audit anchor
      |
      | COMMIT or ROLLBACK
      v
Deterministic result
```

The database is the serialization domain for the local P1 proof-of-concept. This is intentionally not a distributed design.

## 4. Revised execution protocol

### E0 — Startup integrity gate

Verify audit chain and authenticated anchor before serving requests. Failure locks execution.

### E1 — IPC request parse/canonicalization

Accept only the documented requester-visible fields. Canonicalize operation, principal/session binding, decision identifier, envelope identifier, nonce, and stable `resource_id`.

### E2 — Trust-decision authenticity and binding checks

Verify signature and exact request binding. Reject any mismatch.

### E3 — Freshness checks

Reject expired authority before entering protected execution.

### E4 — Begin serialized execution transaction

Execute `BEGIN IMMEDIATE` against the authority database.

### E5 — Final revocation check

Read revocation state within the transaction. If revoked, roll back and deny.

### E6 — Nonce uniqueness establishment

Insert or otherwise establish the nonce as unique within the same transaction. Existing committed nonce state denies execution.

### E7 — Protected mutation

Apply the deterministic mutation to protected resource state identified by immutable `resource_id`.

### E8 — Nonce finalization

Record the nonce as consumed with decision/result metadata.

### E9 — Audit append and anchor update

Append the authenticated audit record and update the authenticated final anchor in the same transaction.

### E10 — Commit

Commit once. Only a successful commit returns execution success.

Any error before commit causes rollback and returns denial/system failure with no protected mutation committed.

## 5. Revised invariants

P1 v0.1.1 MUST establish all of the following locally:

1. `I1_NO_BYPASS` — requester cannot perform protected mutation outside executor IPC.
2. `I2_CREDENTIAL_SEPARATION` — requester process never receives executor-only secrets or database write authority.
3. `I3_RESTART_DURABLE_REPLAY_DENIAL` — committed nonce consumption survives restart.
4. `I4_SERIALIZED_USE_TIME_REVOCATION` — revocation ordered before the execution transaction prevents execution.
5. `I5_CONCURRENT_REPLAY_EXCLUSION` — at most one concurrent use of one nonce commits.
6. `I6_ATOMIC_EXECUTION_RECORD` — resource mutation, nonce finalization, audit append, and audit anchor update commit or roll back together.
7. `I7_AUDIT_TAMPER_DETECTION` — mutation, insertion, deletion, reorder, and tail truncation are detected.
8. `I8_STABLE_RESOURCE_BINDING` — authorization follows immutable resource identity rather than mutable path aliases.
9. `I9_STARTUP_FAIL_CLOSED` — audit-integrity failure prevents protected execution after restart.
10. `I10_FAIL_CLOSED` — verification, persistence, revocation, integrity, concurrency, or credential failure cannot produce committed protected mutation.

## 6. Revised controlling tests

The implementation MUST include the original positive control plus the following corrected cases.

### T0 — Valid authorized execution

One request commits exactly one protected mutation, consumed nonce, audit event, and matching authenticated anchor.

### T1 — Direct bypass denial

Requester attempts protected operation outside executor IPC. No mutation occurs.

### T2 — Cross-process credential separation

Requester process is inspected through its documented environment, request, response, and fixture-visible state. Executor-only credentials and database write authority are absent.

### T3 — Restart-durable nonce

Execute once, restart executor, verify startup integrity, replay same nonce. Replay is denied and mutation count remains one.

### T4 — Revocation serialized before use

Pause before protected transaction, commit revocation, then permit execution transaction to begin. Execution is denied.

### T5 — Concurrent replay

At least 16 concurrent requester attempts use the same nonce. Exactly one or zero commits; never more than one. Normal valid setup should yield exactly one commit.

### T6 — Transaction rollback on audit failure

Inject deterministic failure before audit/anchor completion. Entire transaction rolls back: no resource mutation, no consumed nonce, no partial audit event, no advanced anchor.

### T7 — Audit tamper detection

Verify separate tampered copies containing field mutation, middle deletion, reorder, insertion, and tail truncation. Every tampered copy fails; untouched control passes.

### T8 — Stable resource identity

Present an authorized display path/name but substitute a different immutable resource identifier. Execution is denied.

### T9 — Startup audit-integrity gate

Tamper with retained audit state or anchor, restart executor, and attempt valid execution. Startup verification fails and protected execution remains locked.

### T10 — Crash/rollback consistency

Inject a process/transaction failure before commit, restart, and verify resource, nonce, audit, and anchor all reflect the pre-transaction committed state.

## 7. Claim boundary

Success does NOT establish production enforcement, hostile-host resistance, distributed revocation, distributed nonce uniqueness, production key custody, filesystem race resistance, kernel sandboxing, or hardware attestation.

It establishes only that, under the local deterministic threat model, the harness enforces one ATE-authorized action through a separated executor process and a single transactional authority store with restart-durable replay protection, serialized revocation ordering, stable resource binding, and authenticated tamper-evident audit state.

## 8. Success classification

The classification `ATE_P1_LOCAL_ENFORCEMENT_ESTABLISHED` may be used only if T0 through T10 all pass and the upstream frozen ATE v0.3.1 artifacts remain byte-identical.

Any controlling-test failure yields `ATE_P1_LOCAL_ENFORCEMENT_NOT_ESTABLISHED` pending explicit corrective design or implementation work.

## 9. Implementation disposition

With C1 through C7 incorporated, this design is:

**READY_FOR_LOCAL_IMPLEMENTATION**

Implementation remains local and deterministic. No Hermes participant invocation, premium evaluator, live-model replication, or large experiment matrix is required for this milestone.
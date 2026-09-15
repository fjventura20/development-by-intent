# ATE P1 Local Enforcement Harness v0.1.2 — Privilege-Boundary Corrective Design

**Status:** DESIGN ONLY — NOT FROZEN  
**Date:** 2026-09-15  
**Supersedes for implementation:** `ATE-P1-LOCAL-ENFORCEMENT-HARNESS-DESIGN-v0.1.1.md`  
**Preserves:** v0.1 and v0.1.1 unchanged as historical design inputs  
**Upstream frozen ATE baseline:** `f903478154e2b484f8a49295ba0692d0a5a4f260`  
**Prior implementation baseline:** `1e729c896d675d0e170d80fc30fe68337c6fead1`  
**Controlling failure motivating this revision:** `ATE_P1_LOCAL_ENFORCEMENT_NOT_ESTABLISHED — DIRECT_DB_BYPASS`

---

## 1. Purpose

P1 v0.1.1 established a transactional local enforcement model but failed its real bypass boundary because an unprivileged requester-side process could directly mutate the SQLite authority database through raw SQL.

That result means the protected-resource Python API was not the actual enforcement boundary. The authority database itself was reachable and writable by the requester identity, so the requester could bypass executor policy, nonce enforcement, revocation checks, and audit coupling.

v0.1.2 corrects that architecture by moving the privilege boundary below application modules and onto an operating-system identity and directory ownership boundary.

The controlling design principle is:

> **The requester must not be able to write, replace, create sidecars for, rename, delete, or directly inspect executor-only authority state. The executor-owned directory is the local security boundary.**

---

## 2. Architectural correction

### C8 — Protect the executor directory, not individual SQLite files

The executor runs under a dedicated OS identity, referred to here as `ate-executor`.

All privileged mutable state resides beneath one executor-owned directory, for example:

```text
<runtime-root>/executor-private/
    authority.sqlite
    authority.sqlite-wal          # if WAL mode is used
    authority.sqlite-shm          # if WAL mode is used
    authority.sqlite-journal      # if rollback journal mode is used
    executor-credentials.json
    audit.key
    runtime/
```

The exact SQLite journal mode is not a security invariant. SQLite may create whichever sidecar files its configured mode requires. Security is achieved because the entire directory is inaccessible to the requester identity.

Required local permission model:

- executor-private directory owner: `ate-executor`;
- directory mode: `0700` or stricter equivalent;
- files created within inherit effective protection from the directory and are writable only by the executor identity;
- requester identity cannot traverse the directory;
- requester identity cannot create, replace, delete, rename, or modify files inside it;
- test-controller/root-like orchestration authority is outside the requester threat model and exists only to establish fixtures and identities.

### C9 — Requester never receives the authority-database path

The requester-facing process MUST NOT receive the authority database path, executor-private directory path, audit-key path, or credential-store path via:

- argv;
- environment;
- IPC request;
- IPC response;
- requester configuration;
- requester-visible fixture metadata.

The requester may still guess likely filesystem paths. Security MUST NOT depend on secrecy of the path. A guessed path must fail because the requester OS identity lacks traversal/write permission.

### C10 — Executor owns the only database write authority

Only the executor process may open the authority database read/write for protected execution.

Administrative setup may initialize fixtures before execution, but requester-side test code must not inherit a database descriptor or privilege-equivalent helper capable of mutating protected state.

A long-lived administrative helper is permitted only if:

- it runs under the executor identity;
- it is not reachable by requester IPC;
- it is used solely by the harness controller for deterministic fixture setup/observation;
- its capabilities are not exposed to the requester process.

### C11 — IPC endpoint is the requester’s sole execution path

Requester-to-executor communication occurs through a narrow local IPC endpoint.

Preferred local mechanism: Unix-domain socket or an equivalent explicit local channel.

The requester-visible protocol contains only non-secret execution material required by the P1 request contract.

The requester MUST NOT inherit:

- executor file descriptors;
- authority DB descriptors;
- audit-key descriptors;
- executor credential descriptors;
- privileged helper pipes or sockets.

### C12 — Runtime identity separation must be demonstrated, not asserted

The controlling evidence must identify the effective UID/GID (or platform-equivalent identity) of both requester and executor subprocesses.

The requester and executor MUST have distinct effective security identities for the test.

A test in which both processes execute with the same effective write authority over the executor-private directory does not satisfy P1 v0.1.2.

---

## 3. Threat model

### 3.1 Requester adversary MAY

The requester process may:

- submit malformed or forged IPC requests;
- attempt direct imports/calls of harness modules;
- guess executor-private paths;
- attempt direct SQLite opens against guessed DB paths;
- attempt raw SQL writes;
- attempt file creation/replacement in the executor-private directory;
- attempt to read credential/audit-key files;
- attempt replay and concurrent use of valid-looking authority;
- inspect its own argv, environment, cwd, inherited descriptors, and accessible filesystem state.

### 3.2 Requester adversary MUST NOT be assumed unable to guess paths

Path secrecy is not a security property.

The design must remain secure even when the requester knows the exact executor-private directory and authority DB paths.

### 3.3 Out of scope

Still outside P1 v0.1.2:

- root/administrator compromise of the host;
- ptrace/debug privilege over the executor;
- kernel compromise;
- malicious sudo configuration;
- container escape resistance;
- distributed enforcement;
- remote attestation;
- HSM/TPM/enclave guarantees;
- production IAM/PKI;
- multi-host revocation or nonce consensus.

---

## 4. Revised local architecture

```text
Harness controller
    |
    | creates identities + fixtures
    |
    +--------------------------+
    |                          |
    v                          v
Requester OS identity      Executor OS identity
(unprivileged)             (`ate-executor`)
    |                          |
    | narrow IPC               | rw only
    +-------------------------> |
                               v
                    executor-private/   mode 0700
                        |
                        +-- authority.sqlite
                        +-- SQLite sidecars
                        +-- executor credentials
                        +-- audit key
```

The requester cannot traverse or modify `executor-private/`.

The database remains the serialization domain for nonce, revocation, protected-resource mutation, audit record, and audit anchor.

The OS directory boundary protects the database and every SQLite-created sidecar as one unit.

---

## 5. Execution transaction

The successful P1 v0.1.1 transaction semantics remain controlling:

1. Executor startup integrity verification.
2. Parse/canonicalize IPC request.
3. Verify trust-decision authenticity and exact binding.
4. Check freshness.
5. `BEGIN IMMEDIATE`.
6. Read final revocation state.
7. Establish nonce uniqueness.
8. Apply protected mutation identified by stable `resource_id`.
9. Finalize nonce.
10. Append authenticated audit record.
11. Update authenticated audit anchor.
12. Commit once.

Any pre-commit failure rolls back all transaction-controlled state.

v0.1.2 adds one prerequisite:

> **The executor must be the only requester-reachable principal with OS-level write authority to the executor-private state directory.**

---

## 6. Required invariants

P1 v0.1.2 must establish all prior applicable invariants plus the following strengthened forms.

### I1_NO_BYPASS_OS_BOUNDARY

A requester process cannot commit protected mutation by:

- calling the protected-resource API without executor credential;
- directly opening/writing the authority database;
- creating/replacing SQLite sidecars;
- replacing the database file;
- accessing executor-private credentials.

### I2_CREDENTIAL_AND_STATE_SEPARATION

Requester process receives no executor-only secrets and no OS-level capability that is equivalent to direct authority-store write access.

### I3_REQUESTER_NO_DIRECTORY_TRAVERSAL

Requester cannot successfully traverse/list/read/write the executor-private directory, even when its exact path is known.

### I4_EXECUTOR_EXCLUSIVE_WRITE_AUTHORITY

Protected state changes occur only under the executor identity or harness-controller setup authority outside the requester threat model.

### I5_RESTART_DURABLE_REPLAY_DENIAL

Committed nonce consumption survives executor restart.

### I6_SERIALIZED_REVOCATION

A revocation committed before the execution transaction is observed and prevents execution.

### I7_CONCURRENT_REPLAY_EXCLUSION

At most one same-nonce execution transaction commits.

### I8_ATOMIC_EXECUTION_RECORD

Resource mutation, nonce finalization, audit record, and audit anchor commit or roll back together.

### I9_AUDIT_TAMPER_DETECTION

Mutation, insertion, deletion, reorder, tail truncation, and anchor tampering are detected at verification/startup.

### I10_STABLE_RESOURCE_BINDING

Authorization binds immutable `resource_id` rather than caller-controlled display path.

### I11_STARTUP_FAIL_CLOSED

Audit/state-integrity failure prevents protected execution after restart.

---

## 7. Controlling test matrix — T0 through T12

The full suite must run under the OS privilege boundary. Tests may use harness-controller setup authority, but requester probes must execute under the requester identity.

### T0 — Valid authorized execution

One valid requester IPC action commits exactly one mutation, consumed nonce, audit event, and matching anchor.

### T1 — Direct resource API bypass denial

Requester subprocess attempts the protected-resource API directly without executor credential.

Expected:

- denied;
- no mutation;
- no nonce/audit change.

### T2 — Direct DB write bypass denial

Requester subprocess is given or guesses the exact authority DB path and attempts:

- SQLite open read/write;
- raw SQL `UPDATE` of protected state;
- direct file open for write.

Expected:

- OS permission failure before protected mutation;
- no mutation;
- no nonce/audit change.

This is a controlling test, not an optional hardening check.

### T3 — Executor-private directory traversal denial

Requester subprocess is given or guesses the exact executor-private directory path and attempts:

- directory listing;
- stat/open privileged files;
- create a new file;
- rename/replace the DB;
- create a fake journal/WAL/SHM file.

Expected: all operations requiring traversal or mutation fail under OS permissions.

### T4 — Live cross-process secret/capability separation

From the requester subprocess, capture actual:

- effective UID/GID;
- argv;
- environment;
- inherited file descriptors where inspectable;
- IPC request and response;
- accessible filesystem paths relevant to the harness.

Verify absence/inaccessibility of:

- resource credential value;
- audit-key value;
- authority DB write handle/path delivery;
- revocation-administration capability;
- trust-decision private signing authority;
- privileged helper channel.

Executor subprocess identity must also be recorded and must differ from requester identity.

### T5 — Restart-durable nonce

Execute once, restart executor, perform startup integrity check, replay same nonce. Replay denied and mutation count unchanged.

### T6 — Revocation serialized before use

Commit revocation before execution transaction begins. Execution denied.

### T7 — Concurrent replay

At least 16 requester attempts concurrently use the same nonce. Exactly one or zero commits; normal setup should yield exactly one.

### T8 — Transaction rollback on injected failure

Inject failure between protected mutation and audit completion. Entire transaction rolls back.

### T9 — Audit tamper detection

Verify field mutation, middle deletion, reorder, insertion, tail truncation, and anchor tamper all fail verification.

Tampering may be performed by harness-controller authority because requester cannot access the executor-private directory by design.

### T10 — Stable resource identity

Authorized display metadata with wrong immutable `resource_id` is denied.

### T11 — Startup integrity gate

Controller tampers retained audit/anchor state, restart executor, attempt valid request. Executor locks and refuses protected execution.

### T12 — Crash/rollback consistency

Kill/fail executor process before commit. Restart and verify resource, nonce, audit, and anchor equal the prior committed state.

---

## 8. Test-environment requirements

### 8.1 Dedicated identities

The harness must verify prerequisites before executing the suite:

- requester effective identity known;
- executor identity known and distinct;
- executor-private directory ownership/mode verified;
- requester cannot traverse executor-private directory;
- executor can create SQLite DB and sidecars within that directory.

If the environment cannot establish these conditions, the suite must STOP with an environment/precondition failure rather than weakening the test.

### 8.2 No inherited privilege

Requester subprocess creation must explicitly avoid inheriting privileged open file descriptors or helper channels.

Where practical:

- close nonessential file descriptors;
- use a minimal environment;
- pass only IPC endpoint information required by the requester.

### 8.3 SQLite journal mode

WAL or rollback-journal mode are both acceptable.

The suite must not make correctness depend on manually chowning individual SQLite sidecars after creation.

The executor-private directory permissions must make whatever SQLite creates usable by the executor and inaccessible to requester.

---

## 9. Evidence requirements

Corrected evidence must record at minimum:

- design version `v0.1.2`;
- controlling design commit;
- upstream ATE frozen baseline;
- requester effective UID/GID;
- executor effective UID/GID;
- executor-private directory path (evidence may record it; requester security must not depend on secrecy);
- directory owner/group/mode;
- requester traversal test results;
- direct DB open/write attempt results;
- privileged-file read attempt results;
- inherited descriptor/capability observations where supported;
- T0-T12 results;
- nonce/resource/audit/anchor states relevant to each test;
- full evidence SHA-256 values;
- preservation verification for frozen ATE artifacts and prior design/evidence baselines.

Original v0.1.1 evidence must remain historical and unmodified.

---

## 10. Success classification

`ATE_P1_LOCAL_ENFORCEMENT_ESTABLISHED` may be used under v0.1.2 only if:

1. T0 through T12 all pass;
2. requester and executor run under distinct effective OS security identities;
3. T2 proves raw DB write from requester identity fails at the OS boundary;
4. T3 proves executor-private directory traversal/mutation fails from requester identity;
5. T4 provides live process-boundary evidence rather than hard-coded assertions;
6. upstream frozen ATE v0.3.1 artifacts remain byte-identical;
7. v0.1/v0.1.1/v0.1.2 design artifacts remain preserved according to their status;
8. original historical v0.1.1 evidence remains unchanged.

Any controlling failure yields:

`ATE_P1_LOCAL_ENFORCEMENT_NOT_ESTABLISHED`

with the controlling failure reason appended.

---

## 11. Explicit claim boundary

Passing v0.1.2 establishes only a local proof-of-concept enforcement boundary under a non-root requester adversary and a dedicated executor OS identity.

It does NOT establish:

- security against root/administrator;
- kernel isolation;
- production sandboxing;
- container isolation;
- hostile sudoers configuration resistance;
- remote/distributed enforcement;
- production secret custody;
- production database hardening;
- distributed revocation/nonce semantics;
- hardware-backed identity or attestation.

---

## 12. Implementation disposition

This design is intentionally a correction to the privilege boundary, not a broad redesign of ATE.

Implementation should reuse the successful v0.1.1 transaction, audit, nonce, revocation, and stable-resource mechanisms wherever they remain valid.

The next implementation attempt should be bounded to:

- executor-private directory ownership and creation;
- separate requester/executor OS identities;
- requester-only IPC path;
- corrected privilege-boundary tests;
- adaptation of the existing T0-T10 cases into the T0-T12 matrix.

No Hermes model replication, premium evaluator, or successor experiment is required.

**Disposition:** `READY_FOR_ADVERSARIAL_REVIEW_BEFORE_IMPLEMENTATION`.

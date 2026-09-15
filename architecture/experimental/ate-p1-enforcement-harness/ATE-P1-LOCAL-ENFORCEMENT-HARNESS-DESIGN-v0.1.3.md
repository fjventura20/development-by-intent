# ATE P1 Local Enforcement Harness v0.1.3 — Privilege Boundary Hardening Design

**Status:** DESIGN ONLY — NOT FROZEN  
**Date:** 2026-09-15  
**Supersedes for implementation:** `ATE-P1-LOCAL-ENFORCEMENT-HARNESS-DESIGN-v0.1.2.md`  
**Preserves:** v0.1, v0.1.1, and v0.1.2 unchanged as historical design inputs  
**Upstream frozen ATE baseline:** `f903478154e2b484f8a49295ba0692d0a5a4f260`  
**Prior clean implementation baseline:** `1e729c896d675d0e170d80fc30fe68337c6fead1`  
**Adversarial-review disposition motivating this revision:** `ATE_P1_V0_1_2_REVIEW_CHANGES_REQUIRED`

---

## 1. Purpose

v0.1.2 corrected the authority-database bypass by making a dedicated executor OS identity and executor-owned private directory the local security boundary. Adversarial review then identified two remaining under-specified surfaces:

1. the executor code image itself; and
2. the requester-to-executor IPC endpoint.

If requester-controlled code can alter executor modules, import path resolution, startup configuration, or replace/spoof the IPC endpoint, database isolation alone does not establish trustworthy enforcement.

v0.1.3 therefore hardens the complete local privilege boundary around four assets:

- executor-private mutable state;
- executor code image;
- executor-only secret material;
- authenticated IPC endpoint ownership and peer identity.

The controlling principle becomes:

> **The requester must be unable to modify the executor's state, secrets, executable code path, or privileged IPC endpoint, and must communicate only through an endpoint whose server identity is bound to the executor OS principal.**

---

## 2. Controlling corrections

### C13 — Executor code image integrity boundary

The executor MUST NOT import privileged implementation code from a requester-writable location.

For the local harness, privileged executor modules MUST be copied or installed into an executor-owned code directory beneath the privileged runtime root, for example:

```text
<runtime-root>/executor-private/
    code/
        privileged_executor.py
        authority_db.py
        audit_chain.py
        protected_resource.py
        ipc_worker.py
        crypto_utils.py
        ipc_protocol.py
    state/
        authority.sqlite
        SQLite sidecars
    secrets/
        executor-credentials.json
        audit.key
```

Requirements:

- `executor-private/` owner: executor OS identity;
- mode `0700` or stricter equivalent;
- executor code directory and files are not writable by requester identity;
- executor process imports privileged modules only from the protected code image;
- requester-writable repository/worktree paths MUST NOT appear ahead of the protected executor code path in `PYTHONPATH`/`sys.path` for the executor;
- executor startup records hashes of the protected code image used for the run.

The harness controller may construct this protected code image before execution, but requester processes must not be able to alter it after the test boundary is established.

### C14 — Dedicated requester OS identity

The requester MUST run under a dedicated unprivileged identity, referred to as `ate-requester`, distinct from:

- the executor identity;
- the harness-controller/operator identity.

This prevents accidental success caused by the operator account possessing permissions unavailable to a genuinely unprivileged requester.

The requester account MUST NOT have sudo or equivalent privilege to become the executor identity during the test.

### C15 — IPC endpoint ownership and anti-replacement

The IPC endpoint MUST be created by the executor identity in a directory that requester can traverse/connect to but cannot modify.

Recommended layout:

```text
<runtime-root>/ipc/
    executor.sock
```

Recommended permission model:

- IPC directory owned by executor or controller-controlled trusted identity;
- requester has search/connect permission as required;
- requester lacks create/delete/rename permission in the IPC directory;
- Unix socket owned by executor identity;
- socket mode permits only intended requester access.

The requester MUST NOT be able to:

- unlink the real socket;
- replace it with a fake server;
- bind another socket at the same path;
- create a symlink or filesystem object that redirects executor/client behavior.

The test harness MUST verify these properties explicitly.

### C16 — Peer credential verification

Where supported by the host platform, the executor MUST inspect OS-provided Unix-socket peer credentials (for Linux, e.g. `SO_PEERCRED`) and record the connecting requester PID/UID/GID.

The accepted peer UID MUST equal the dedicated requester identity or another explicitly allowed test principal.

A connection from an unexpected local UID MUST be rejected before protected execution.

This does not establish cryptographic remote identity; it establishes local kernel-mediated principal binding under the non-root threat model.

### C17 — No privileged helper reachable during adversarial execution

Any fixture/bootstrap helper with executor privileges MUST be terminated or otherwise made unreachable before requester adversarial tests begin.

The requester MUST NOT inherit or obtain:

- helper stdin/stdout pipes;
- admin Unix sockets;
- open executor-owned DB descriptors;
- privileged RPC handles;
- inherited file descriptors referencing executor-private files/directories.

Administrative state inspection after a test may use a new controller-mediated privileged process, but no privileged helper channel may remain available to the requester during the tested execution window.

### C18 — Mandatory descriptor and environment hygiene

Requester and executor subprocess launches MUST use deliberate descriptor and environment hygiene.

At minimum:

- close nonessential inherited file descriptors;
- do not inherit controller database descriptors or secret files;
- use a minimal explicit environment;
- exclude secret values and privileged paths from requester environment;
- exclude requester-writable import paths from executor module resolution;
- record relevant argv/environment/path observations in evidence.

---

## 3. Revised trusted boundary

```text
Harness controller
    |
    | privileged setup only
    v
+----------------------------------------------------+
| Trusted local substrate                            |
|                                                    |
| executor-private/  owner=ate-executor mode=0700    |
|   code/        protected executor implementation   |
|   state/       SQLite DB + all sidecars            |
|   secrets/     credentials + audit key             |
|                                                    |
| ipc/          trusted directory                    |
|   executor.sock  owner=ate-executor                |
+----------------------------------------------------+
             ^                         |
             | kernel-mediated IPC     |
             | peer credentials        v
      ate-requester              ate-executor
      unprivileged               privileged executor
```

The repository/worktree is not itself the executor trust boundary. It is source material from which the controller stages the protected executor code image.

---

## 4. Threat model additions

The requester MAY additionally attempt to:

- edit repository/worktree implementation files;
- influence `PYTHONPATH`, `PATH`, or module lookup;
- pre-create, unlink, replace, or spoof the Unix socket;
- connect from a wrong local UID;
- inspect or abuse inherited file descriptors;
- reach any lingering privileged fixture helper;
- inject environment variables intended to alter executor behavior.

The requester is still assumed not to have root/admin/kernel compromise or permission to ptrace the executor.

---

## 5. Required invariants

All applicable v0.1.2 invariants remain, strengthened by:

### I12_EXECUTOR_CODE_INTEGRITY

Requester cannot modify the exact code image imported/executed by the privileged executor during the run.

### I13_IPC_ENDPOINT_INTEGRITY

Requester can connect to the intended IPC endpoint but cannot replace, unlink, redirect, or impersonate it.

### I14_LOCAL_PEER_IDENTITY_BINDING

Executor obtains kernel-mediated peer identity and rejects unauthorized local UIDs before protected execution.

### I15_NO_PRIVILEGED_HELPER_LEAKAGE

No privileged fixture/admin helper or inherited descriptor gives requester an alternate path to protected state.

### I16_DEDICATED_REQUESTER_IDENTITY

Controlling requester probes execute under an identity distinct from both executor and controller/operator.

---

## 6. Controlling test matrix — T0 through T16

All prior semantics remain but are renumbered/extended as needed for the complete boundary.

### T0 — Valid authorized execution

Valid request from `ate-requester` over the trusted IPC endpoint commits one mutation, consumed nonce, audit event, and matching anchor.

### T1 — Direct resource API bypass denial

Requester directly invokes/imports protected-resource functionality from requester-visible source without executor credential. No protected mutation occurs.

### T2 — Direct DB write bypass denial

Requester knows the exact executor-private DB path and attempts SQLite/raw-file write. OS permission denial; no mutation.

### T3 — Executor-private directory traversal/mutation denial

Requester knows exact private path and attempts list/read/create/delete/rename/sidecar operations. All denied by OS boundary.

### T4 — Live secret/capability separation

Requester subprocess records real UID/GID, argv, environment, inherited descriptors, request/response, and relevant accessible paths. No executor secret, DB write capability, signing authority, revocation authority, or privileged helper channel is present.

### T5 — Executor code tamper denial

After protected executor code image is staged, requester attempts to modify:

- privileged module file;
- protected code directory contents;
- executor import path via requester-controlled module shadowing.

Expected:

- protected code modification fails;
- executor starts with protected code hashes matching controller-recorded expected hashes;
- requester-writable shadow module is not imported by executor.

### T6 — IPC endpoint anti-replacement

Requester attempts to unlink, rename, replace, symlink, or bind a fake socket at the executor endpoint path.

Expected: all endpoint replacement/spoof attempts fail; valid executor endpoint remains the object used by the requester client.

### T7 — Peer credential enforcement

Connect once as `ate-requester`: accepted to request-validation stage.

Connect from a distinct unauthorized local UID: rejected before protected execution with a dedicated local-peer denial reason.

Evidence records kernel-reported peer UID/GID/PID.

### T8 — Privileged helper/FD leakage denial

During requester execution, verify no privileged bootstrap/admin helper is reachable and no inherited descriptor resolves to executor-private DB, secrets, directory, or admin IPC.

### T9 — Restart-durable nonce

Execute, restart executor, verify startup integrity, replay nonce; replay denied and mutation unchanged.

### T10 — Revocation serialized before use

Revocation committed before protected transaction prevents execution.

### T11 — Concurrent replay exclusion

At least 16 requester processes submit the same nonce; exactly one or zero commits, normal setup exactly one.

### T12 — Atomic rollback on injected failure

Failure between resource mutation and audit completion rolls back resource, nonce, audit, and anchor.

### T13 — Audit tamper detection

Controller tampers copies/state; mutation, insertion, deletion, reorder, tail truncation, and anchor tamper are all detected.

### T14 — Stable resource identity

Correct display metadata with wrong immutable `resource_id` is denied.

### T15 — Startup integrity gate

Controller tampers retained audit/anchor state; restarted executor refuses protected execution.

### T16 — Crash/rollback consistency

Executor terminates before commit; restart shows exactly prior committed resource/nonce/audit/anchor state.

---

## 7. Environment preflight

Before T0, the harness MUST establish and record:

- dedicated requester account exists;
- dedicated executor account exists;
- requester UID != executor UID != controller/operator UID where applicable;
- requester lacks sudo/equivalent transition to executor identity for the test;
- executor-private tree owner/mode correct;
- protected executor code hashes recorded;
- requester cannot modify protected code tree;
- requester cannot traverse executor-private state/secrets directories;
- IPC directory ownership/mode prevents requester replacement while permitting connection;
- executor can create and remove its own socket;
- peer-credential mechanism is available; otherwise STOP with environment/precondition failure for this Linux-targeted v0.1.3 harness;
- no privileged admin helper remains reachable when adversarial tests start.

If any preflight condition fails, do not weaken the test. Return an environment/precondition failure.

---

## 8. Evidence requirements

Evidence MUST record at minimum:

- design version and controlling design commit;
- requester/controller/executor UID/GID values;
- relevant directory ownership/mode;
- protected code-image file hashes;
- executor-observed import/module paths sufficient to show privileged modules came from protected code image;
- requester tamper attempts against code/private state/IPC endpoint;
- Unix peer credentials observed by executor;
- unauthorized-peer rejection result;
- requester inherited descriptor inventory or bounded inspection result;
- confirmation privileged helpers were absent/unreachable during adversarial tests;
- T0-T16 results;
- preservation hashes for prior designs, original v0.1.1 evidence, and frozen ATE baseline;
- SHA-256 of new controlling evidence artifacts.

---

## 9. Success classification

`ATE_P1_LOCAL_ENFORCEMENT_ESTABLISHED` under v0.1.3 requires all T0-T16 PASS plus all preflight requirements.

In particular, success requires positive evidence that:

1. requester cannot directly mutate authority state;
2. requester cannot modify executor code image;
3. requester cannot replace/spoof the IPC endpoint;
4. executor binds local IPC client to kernel-reported requester identity;
5. requester has no privileged helper/descriptor escape path;
6. transaction/replay/revocation/audit properties continue to pass;
7. frozen and historical artifacts remain preserved.

Any controlling failure yields `ATE_P1_LOCAL_ENFORCEMENT_NOT_ESTABLISHED` with the controlling reason.

---

## 10. Explicit claim boundary

Passing v0.1.3 remains a local proof-of-concept only. It does not establish protection against root/admin, kernel compromise, ptrace-capable attackers, malicious sudo policy, production sandbox escape, remote identity, production key custody, or distributed enforcement.

Linux Unix-domain peer credentials are used only as a local kernel-mediated identity mechanism within this bounded experiment.

---

## 11. Implementation disposition

v0.1.3 is intentionally narrow. Reuse successful v0.1.1 transaction, nonce, revocation, audit, and stable-resource mechanisms. Reuse v0.1.2 executor-private directory concept. Add only:

- protected executor code image;
- dedicated requester identity;
- trusted IPC directory/socket lifecycle;
- peer-credential validation;
- removal of privileged helper reachability during adversarial execution;
- descriptor/environment hygiene;
- T5-T8 boundary tests and adaptation into T0-T16.

No model replication, premium evaluator, broad redesign, or successor experiment is required.

**Disposition:** `READY_FOR_ADVERSARIAL_REVIEW_BEFORE_IMPLEMENTATION`.

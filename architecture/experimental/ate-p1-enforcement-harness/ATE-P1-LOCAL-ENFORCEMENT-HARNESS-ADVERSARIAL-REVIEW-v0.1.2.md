# ATE P1 Local Enforcement Harness v0.1.2 — Adversarial Design Review

**Status:** REVIEW COMPLETE — REVISION REQUIRED  
**Date:** 2026-09-15  
**Reviewed design:** `ATE-P1-LOCAL-ENFORCEMENT-HARNESS-DESIGN-v0.1.2.md`  
**Reviewed commit:** `765b28e1ffd59007e1fd42ead8bf148238f84310`  
**Upstream frozen ATE baseline:** `f903478154e2b484f8a49295ba0692d0a5a4f260`

## 1. Review disposition

The v0.1.2 design fixes the prior direct-database bypass at the correct layer: a dedicated executor OS identity owns a private state directory, and requester security no longer depends on hiding individual SQLite files or manually repairing journal/WAL ownership.

However, the privilege boundary remains incomplete in two controlling areas and under-specified in three additional areas.

**Disposition:** `ATE_P1_V0_1_2_REVIEW_CHANGES_REQUIRED`

Implementation SHOULD NOT begin from v0.1.2 as written.

## 2. Blocking finding B1 — Executor code integrity is outside the protected boundary

The design protects executor mutable state but does not explicitly require that the executable Python modules, launcher, configuration, and imported dependency path used by the executor are themselves non-writable by the requester identity.

If the executor runs code from the development repository, and the requester identity can modify that repository, the requester can alter `privileged_executor.py`, `ipc_worker.py`, `audit_chain.py`, `authority_db.py`, or another imported module before executor launch or restart. The modified executor could then disclose secrets, bypass revocation, ignore nonce state, or mutate the authority DB directly while still running as `ate-executor`.

Protecting only `authority.sqlite` is therefore insufficient.

### Required correction

The executor's runtime code image MUST be inside an executor-owned, requester-non-writable runtime directory or must otherwise be integrity-pinned before execution.

For the local harness, the simplest acceptable model is:

- controller copies the exact implementation modules required by the executor into `executor-private/runtime/`;
- ownership: `ate-executor`;
- directory mode: `0700`;
- files: non-writable by requester;
- executor launches only from that protected runtime copy;
- evidence records SHA-256 values of the protected runtime files;
- requester attempts to modify/replace at least one protected executor module and is denied.

The development repository may remain writable by the normal user, but it MUST NOT be the code path from which the privileged executor imports at runtime.

## 3. Blocking finding B2 — IPC endpoint ownership and anti-spoofing semantics are undefined

The design says the requester uses a Unix-domain socket or equivalent narrow IPC endpoint, but it does not define where that socket lives or who may create, replace, unlink, bind, or impersonate it.

If the socket resides inside `executor-private/` mode `0700`, the requester cannot reach it. If it resides in a requester-writable directory, the requester may be able to unlink or replace it and impersonate the executor. If the socket accepts any local peer without checking identity, another local process may submit requests under unintended authority.

### Required correction

Define a separate executor-owned IPC directory, distinct from executor-private state, for example:

```text
<runtime-root>/executor-ipc/
    executor.sock
```

Required properties:

- directory owner: `ate-executor`;
- directory not writable by requester;
- requester has only the minimum traversal/connect permission required;
- socket file created by executor after stale-socket cleanup performed only by executor/controller authority;
- requester cannot unlink, replace, rename, or bind the socket path;
- socket permissions explicitly constrain who may connect;
- executor records peer credentials when platform support permits (`SO_PEERCRED` on Linux or equivalent) and verifies the requester identity expected by the harness;
- client does not rely on path secrecy;
- requester-side test attempts socket replacement/unlink and must fail.

For P1 local Linux evidence, peer-credential verification is strongly preferred because the design already depends on OS identities.

## 4. High-priority finding H1 — Requester identity must not be the controller/sudo-capable account

The design distinguishes a root-like harness controller from the requester, but does not explicitly require a dedicated requester OS account.

If requester subprocesses run as the normal operator account and that account has passwordless sudo capability, the practical test identity may be able to become `ate-executor` even though malicious sudo configuration is nominally out of scope.

### Required correction

Use a dedicated local account such as `ate-requester` for adversarial requester subprocesses.

Requirements:

- `ate-requester` != controller identity;
- `ate-requester` != `ate-executor`;
- no supplementary group that grants executor-private access;
- no sudo rule intended for the harness;
- evidence records UID/GID and supplementary groups for requester and executor;
- controller remains orchestration-only and MUST NOT be treated as the requester adversary.

The harness need not prove global absence of every host escalation path; it must demonstrate that the tested requester identity has no privilege-equivalent path intentionally supplied by the harness.

## 5. High-priority finding H2 — Administrative helper lifetime is too permissive

v0.1.2 permits a long-lived administrative helper if it is not reachable by requester IPC. This is unnecessarily risky because inherited file descriptors, pipes, environment references, or accidental socket exposure can create a privilege-equivalent bypass.

### Required correction

Prefer no long-lived privileged administrative helper during adversarial requester execution.

Recommended lifecycle:

1. controller establishes identities/directories;
2. executor-owned setup helper creates or seeds fixtures;
3. setup helper exits;
4. controller verifies no privileged helper channel remains;
5. executor service starts;
6. requester tests run.

If a helper must remain, the design must specify how its descriptors/endpoints are inaccessible to requester and add a controlling probe.

## 6. High-priority finding H3 — File-descriptor inheritance must be a hard precondition

The design says requester subprocess creation should avoid inheriting privileged descriptors "where practical." For a privilege-boundary test, this should not be optional.

### Required correction

Requester and executor launch rules MUST close nonessential file descriptors and explicitly pass only the intended IPC descriptors/endpoints. The evidence should record open descriptors visible to the requester where the platform allows inspection.

At minimum, the requester MUST NOT inherit:

- authority DB descriptor;
- executor-private directory descriptor;
- audit-key descriptor;
- credential-store descriptor;
- controller/helper pipes;
- privileged socket descriptors.

Failure to establish this precondition should stop the test suite.

## 7. Additional hardening observations

### O1 — Runtime directory parent permissions

It is not enough for `executor-private/` itself to be `0700` if an attacker can rename or replace an ancestor directory. The harness controller should create the runtime root in a location whose parent cannot be replaced by the requester during execution.

### O2 — Symlink handling

Executor-private and IPC paths should be created with fixed canonical paths and checked against symlink substitution. The local harness can keep this simple by creating a fresh controller-owned runtime root and refusing pre-existing symlinks at protected path components.

### O3 — Environment sanitization

Executor launch should not honor requester-controlled `PYTHONPATH`, `PYTHONHOME`, or equivalent import-path variables. The executor should use the protected runtime code path and a minimal environment.

### O4 — Socket denial-of-service is not an authorization failure

The requester may be able to connect repeatedly or send malformed payloads. P1 need not prove availability. Tests should distinguish denial-of-service from authority bypass; no malformed request may cause protected mutation.

## 8. Required design changes before implementation

The successor corrective design SHOULD add at least:

1. protected executor runtime/code integrity boundary;
2. explicit executor-owned IPC directory and socket lifecycle;
3. peer-identity verification or equivalent local caller binding;
4. dedicated `ate-requester` identity distinct from controller and executor;
5. privileged setup helper termination before requester execution, unless justified otherwise;
6. mandatory nonessential-FD closure and environment sanitization;
7. anti-symlink/ancestor-replacement preconditions for runtime paths.

## 9. Required test changes

Add or strengthen controlling tests so that evidence demonstrates:

- requester cannot alter executor runtime code;
- executor imports only protected runtime files whose SHA-256 values match the staged implementation;
- requester cannot unlink/replace/rebind the executor socket path;
- executor observes expected requester UID/GID via peer credentials where supported;
- `ate-requester` supplementary groups do not grant executor access;
- requester inherits no privileged descriptors/helper channels;
- guessed exact private paths remain inaccessible;
- existing DB-write and directory-traversal denials still pass.

The test numbering may be extended or existing cases strengthened, but the resulting matrix must make each of these claims independently observable.

## 10. Claim boundary after correction

Even after these corrections, P1 remains a local proof-of-concept. It will not establish protection against root, kernel compromise, ptrace-capable attackers, hostile sudoers policy, or production sandbox escape.

The intended claim remains narrower: under distinct non-root requester and executor identities, protected state and executor runtime are inaccessible to requester except through a controlled IPC endpoint, and authorized execution is enforced transactionally with durable replay prevention, serialized revocation, stable resource binding, and tamper-evident audit state.

## 11. Final review classification

**`ATE_P1_V0_1_2_REVIEW_CHANGES_REQUIRED`**

The design should advance to a narrowly-scoped **v0.1.3 privilege-boundary correction** before any further Hermes implementation work.

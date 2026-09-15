# ATE P1 Local Enforcement Harness v0.1.3 — Second Adversarial Review

**Status:** REVIEW COMPLETE  
**Date:** 2026-09-15  
**Reviewed design:** `ATE-P1-LOCAL-ENFORCEMENT-HARNESS-DESIGN-v0.1.3.md`  
**Reviewed design commit:** `d44867c7f58ec02cf0e16ff3d3fb370efe1396f5`  
**Upstream frozen ATE baseline:** `f903478154e2b484f8a49295ba0692d0a5a4f260`

## 1. Review question

Does v0.1.3 close the previously identified local enforcement bypasses sufficiently to justify a bounded local implementation attempt, without weakening the threat model or converting test-controller privilege into requester privilege?

## 2. Disposition

**`ATE_P1_V0_1_3_READY_FOR_BOUNDED_IMPLEMENTATION_WITH_MANDATORY_PREFLIGHT`**

No new architectural bypass comparable to the v0.1.1 direct-DB bypass was found. The v0.1.3 design correctly places executor state, secrets, code image, and IPC endpoint lifecycle behind distinct OS identities and explicit filesystem boundaries.

Implementation may proceed, but the requirements in §3 are mandatory acceptance conditions, not optional hardening.

## 3. Mandatory implementation/preflight conditions

### R1 — Isolated executor module resolution

Protecting the copied executor files is insufficient if the Python interpreter can resolve a transitive import from a requester-writable location.

Executor startup MUST therefore use an isolated, explicit module-resolution environment. At minimum:

- no requester-controlled `PYTHONPATH`;
- no requester-controlled current working directory on `sys.path`;
- no requester user-site packages;
- no repository/worktree path ahead of the protected code image;
- privileged local modules resolve from the protected code directory;
- evidence records the effective `sys.path` and resolved `__file__` locations for privileged harness modules.

On the Linux/Python harness, an isolated interpreter mode such as `python -I` is preferred where compatible, with an explicit protected code path established by the trusted launcher.

T5 MUST fail if any privileged harness module resolves outside the protected code image.

### R2 — IPC directory semantics must be concrete, not aspirational

Before the executor starts, preflight MUST record and verify:

- IPC directory owner UID/GID and mode;
- requester lacks directory create/delete/rename authority;
- executor has authority required to create/remove the socket;
- socket owner UID equals executor UID after bind;
- socket type is `S_IFSOCK`;
- socket permission bits allow only the intended requester population.

The requester should verify the socket filesystem object immediately before connect and record its owner/type. This is defense in depth; security still rests on the non-writable parent directory plus kernel peer handling.

### R3 — Peer credentials are authorization input, not evidence only

`SO_PEERCRED` (or platform equivalent) MUST be checked by the executor before request parsing reaches protected authorization/execution. Unexpected UID is a controlling denial, not merely an audit observation.

T7 must use a genuinely distinct unauthorized UID and demonstrate no nonce/resource/audit mutation.

### R4 — No setup privilege crosses the adversarial boundary

The controller may create identities, stage code, initialize fixtures, and perform post-test observations. Once an adversarial requester test starts:

- no privileged helper remains reachable;
- no privileged pipe/socket remains inherited;
- no open DB/directory/secret descriptor is inherited by requester;
- no sudo command available to the requester can transition to executor identity under the test configuration.

Controller privilege itself remains outside the requester threat model, but any capability passed from controller to requester becomes requester capability and invalidates the test.

### R5 — Socket and code-image race window

The controller MUST complete staging and permission checks before executor startup and before requester launch. Once preflight hashes/ownership are recorded, requester attempts to alter code or endpoint state must occur while the actual executor lifecycle is active, not against an inert mock directory.

T5/T6 evidence must therefore cover the live runtime window.

### R6 — Test oracle separation

Requester-side probe programs MUST NOT determine their own PASS status through hard-coded declarations such as `has_secret=false`. They may report observed facts and syscall/open/connect results. The controller-side test oracle evaluates those observations against expected invariants.

This requirement specifically prevents recurrence of the v0.1.1 T2 evidence defect.

## 4. Adversarial attack review

### A1 — Modify repository source after protected staging

Expected result: irrelevant to executor behavior because privileged imports resolve only from executor-owned protected code. T5 must prove this by modifying or shadowing requester-writable source while executor still resolves protected modules.

### A2 — Dependency/module-shadow injection

Potential weakness if executor search path includes requester-writable directories. Resolved by mandatory R1. This is the main remaining implementation-sensitive issue.

### A3 — Replace or spoof executor socket

With a non-writable IPC parent directory, requester cannot unlink/rename/bind at the protected pathname. Socket owner/type verification plus R2/T6 provides evidence.

### A4 — Connect from wrong local principal

Resolved only if peer credentials actively gate authorization before protected execution. R3/T7 makes this controlling.

### A5 — Inherit privileged descriptors from controller

Resolved by close-on-exec/explicit descriptor hygiene plus T8. Any DB, directory, secret, or admin-helper descriptor visible to requester is a controlling failure.

### A6 — Guess exact protected paths

Path secrecy is explicitly non-controlling. Requester should be given exact paths in adversarial probes where useful; OS permissions must still deny access.

### A7 — SQLite sidecar creation/manipulation

Resolved structurally by executor-private directory ownership. WAL/journal choice is not security-sensitive provided all SQLite artifacts remain below that directory and requester cannot traverse it.

### A8 — Controller abuse

Controller/root-like fixture authority can trivially subvert the harness but is explicitly outside the requester adversary model. The test remains valid only if controller capabilities are not delegated or inherited by requester.

## 5. Test-matrix ruling

T0–T16 is sufficient for this bounded local milestone if:

- environment preflight passes;
- R1–R6 are implemented as controlling requirements;
- no test is satisfied by self-attestation from code under test;
- T1–T8 use real OS subprocess boundaries and actual permission/peer-credential outcomes;
- T9–T16 preserve the previously successful transaction/replay/revocation/audit semantics.

No expansion beyond T0–T16 is recommended before implementation.

## 6. Claim boundary

A successful run may support `ATE_P1_LOCAL_ENFORCEMENT_ESTABLISHED` only under the existing v0.1.3 local non-root threat model. It does not establish hostile-admin, kernel, ptrace, production sandbox, remote identity, production secret-custody, or distributed enforcement guarantees.

## 7. Implementation authorization recommendation

Proceed with one bounded Hermes implementation attempt from the clean historical implementation baseline, using v0.1.3 plus this review as controlling requirements.

Do not reuse uncommitted partial privilege-boundary work blindly. Reuse code selectively only after reconciling it with v0.1.3 and R1–R6.

Stop immediately on:

- inability to establish distinct requester/executor OS identities;
- requester traversal/write access to executor-private state or code;
- requester ability to replace the IPC endpoint;
- executor privileged-module resolution from requester-writable paths;
- privileged descriptor/helper leakage;
- any T0–T16 controlling failure.

**Final review disposition:** `READY_FOR_BOUNDED_IMPLEMENTATION`.
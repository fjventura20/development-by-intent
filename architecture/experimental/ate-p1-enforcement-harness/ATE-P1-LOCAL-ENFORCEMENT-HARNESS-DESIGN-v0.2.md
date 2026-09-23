# ATE P1 Local Enforcement Harness — v0.2 (DESIGN ONLY, REVISION 2.1)

## 0. Status

- **DESIGN ONLY. No implementation in this artifact.**
- Revision 2.1 of v0.2, responding to implementation-readiness review
  (`HOLD — ONE SURGICAL r2.1 CORRECTION`).
- The accepted architecture from r2 (three-UID boundary, asymmetric
  signing, execution clearance, durable PREPARED linearization,
  crash-safe recovery, idempotent resource mutation, permissions
  model, requester-UID principal model) is NOT reopened.
- This revision adds four targeted clarifications only:
  1. Explicit clearance acquisition path through the requester
     (executor does not contact authority).
  2. Exactly one clearance per decision (idempotent issuance,
     UNIQUE(decision_id), expired clearance cannot be replaced
     under the same decision).
  3. Stable operation identity binding (`operation_id` is the
     authority-decision-bound identity; resource idempotency keys
     on `operation_id`, not `clearance_id`).
  4. Targeted test coverage for the above.
- Closes v0.1.1 attempt at classification
  `ATE_P1_LOCAL_ENFORCEMENT_NOT_ESTABLISHED — DIRECT_DB_BYPASS`.

## 1. Threat model (binding)

### 1.1 IN SCOPE

- Arbitrary / malicious `ate-requester` behavior, including full
  requester process compromise.
- Knowledge of all paths, filenames, schema details, IPC endpoints,
  socket names, and message formats.
- Malformed, forged, and replayed requester traffic.
- Requester attempts to read or write privileged files, credentials,
  databases, sockets, and protected resources.
- Requester attempts to obtain authority or executor secrets via
  filesystem traversal, IPC fuzzing, env inspection, or FD inheritance.
- Requester attempts to rebind, unlink, replace, or impersonate
  authority/executor sockets.
- Requester attempts to reset executor replay state.

### 1.2 OUT OF SCOPE

- Root compromise.
- `trusted-bootstrap` compromise.
- Compromise or malicious replacement of the `ate-authority` service
  binary or process.
- Compromise or malicious replacement of the `ate-executor` service
  binary or process.
- Trusted service binary modification.
- Kernel or hardware compromise.
- TOCTOU between runtime attestation and action execution.

### 1.3 Architectural consequence

P1 defends the requester attack surface ONLY. The protection that
audit and revocation provide is for **post-hoc forensic recovery**
against an honest-but-imperfect implementation, NOT for active
defense against a compromised trusted service. P1 makes no claim
that audit prevents trusted-service abuse.

## 2. Security principals (OS UIDs)

| Principal          | OS UID       | Group(s)                | Role                                                                                              |
|--------------------|--------------|-------------------------|---------------------------------------------------------------------------------------------------|
| `ate-requester`    | unprivileged | (none privileged)       | Untrusted requester code. NO sudo. NO write access to privileged state. Test code runs here.      |
| `ate-authority`    | privileged   | `ate-authority`         | Owns authority state, authority signing key. Signs decision envelopes. Exposes narrow IPC.        |
| `ate-executor`     | privileged   | `ate-executor`          | Owns per-resource credentials, executor signing key, executor-local replay state, protected files. |
| `trusted-bootstrap`| privileged   | operator                | Creates identities, state directories, mode bits, launches services. **Never** part of requester execution context. |

- `ate-requester` is in NO privileged group.
- `ate-authority` and `ate-executor` are in NO shared group.
- `ate-requester` has NO `sudoers` entry.
- `ate-authority` has NO `sudoers` entry.
- `ate-executor` has NO `sudoers` entry.

## 3. Trust-boundary diagram (revised)

```
                          ┌───────────────────────────────────────┐
                          │         trusted-bootstrap             │
                          │   creates identities, dirs, modes     │
                          │   launches authority + executor       │
                          │   never opens authority DB            │
                          │   never holds authority/exec secrets  │
                          └───────────┬───────────────┬───────────┘
                                      │ launches      │ launches
                                      ▼               ▼
   ┌───────────────────┐    ┌─────────────────────┐    ┌──────────────────────┐
   │   ate-requester   │    │   ate-authority     │    │   ate-executor       │
   │ (unprivileged)    │    │   (privileged)      │    │   (privileged)       │
   │                   │    │                     │    │                      │
   │ no sudo           │    │ owns:               │    │ owns:                │
   │ no capability     │    │  authority.sqlite* │    │  executor.sqlite*    │
   │ no FD to priv     │◀──IPC──▶  authority.key  │    │  audit_signing.key   │
   │ no env secrets    │    │  (Ed25519 private)  │    │  resource_creds      │
   │ no group overlap  │    │                     │    │  authority_pubkey    │
   │                   │    │ exposes:            │    │  (Ed25519 public)    │
   │                   │    │  issue_decision_env │    │                      │
   │                   │    │  return: SIGNED     │    │ exposes:             │
   │                   │    │  decision envelope  │    │  execute(req, env)   │
   │                   │    │  (no shared secret) │    │                      │
   └───────────────────┘    │                     │    │                      │
                            │ NEVER reads:        │    │ NEVER reads:         │
                            │  executor state     │    │  authority.sqlite*   │
                            │ NEVER writes:       │    │  authority state dir │
                            │  protected resources│    │                      │
                            └─────────────────────┘    └──────────────────────┘
                                       │                            │
                                       └──────── IPC ───────────────┘
                                       (peer UID verified via SO_PEERCRED;
                                        message contents verified via
                                        Ed25519 signature on envelope)
```

## 4. State directories and key ownership (revised matrix)

```
/var/lib/ate/                          (root:root, mode 0755)
├── authority/                         (ate-authority:ate-authority, mode 0700)
│   ├── authority.sqlite               (mode 0600, owned by ate-authority)
│   ├── authority.sqlite-wal           (mode 0600, owned by ate-authority)
│   ├── authority.sqlite-shm           (mode 0600, owned by ate-authority)
│   ├── authority.sqlite-journal       (mode 0600, owned by ate-authority)
│   └── authority_signing.key          (mode 0600, owned by ate-authority)
│                                       Ed25519 PRIVATE signing key
└── executor/                          (ate-executor:ate-executor, mode 0700)
    ├── executor.sqlite                (mode 0600, owned by ate-executor)
    ├── executor.sqlite-wal            (mode 0600, owned by ate-executor)
    ├── executor.sqlite-shm            (mode 0600, owned by ate-executor)
    ├── executor.sqlite-journal        (mode 0600, owned by ate-executor)
    ├── audit_signing.key              (mode 0600, owned by ate-executor)
    │                                   Ed25519 key for audit chain
    ├── resource_credentials.json      (mode 0600, owned by ate-executor)
    │                                   per-resource HMAC keys
    └── authority_pubkey.pem           (mode 0644, owned by ate-executor)
                                        Ed25519 PUBLIC verification key
                                        (used to verify authority envelopes)
/var/lib/ate/resources/<id>/           (ate-executor:ate-executor, mode 0700)
    ├── state.json                     (mode 0600, owned by ate-executor)
    ├── mutation_count                 (mode 0600, owned by ate-executor)
    └── credential_ref                 (mode 0600, owned by ate-executor)
```

### 4.1 Permission matrix (revised)

| Asset                              | requester | authority | executor | bootstrap |
|------------------------------------|-----------|-----------|----------|-----------|
| Read authority state dir           | no        | rwx       | **no**   | create    |
| Read/write authority.sqlite*       | no        | rw        | **no**   | no        |
| Read authority_signing.key         | no        | rw        | no       | create    |
| Read authority_pubkey.pem          | no        | rw        | r        | create    |
| Read executor state dir            | no        | **no**    | rwx      | create    |
| Read/write executor.sqlite*        | no        | **no**    | rw       | no        |
| Read executor_signing.key          | no        | **no**    | rw       | create    |
| Read resource_credentials.json     | no        | **no**    | rw       | create    |
| Read protected resource files      | no        | **no**    | rw       | create    |
| Write protected resource state     | no        | **no**    | rw       | no        |
| Traverse /run/ate/                 | r-x       | r-x       | r-x      | create    |
| Traverse /run/ate/authority/       | r-x       | rwx       | n/a      | create    |
| Traverse /run/ate/executor/        | r-x       | n/a       | rwx      | create    |
| Write /run/ate/authority/ or /run/ate/executor/ | **no** | rwx | rwx | create |
| Unlink/replace authority.sock      | **no**    | n/a (owner) | n/a    | create    |
| Unlink/replace executor.sock       | **no**    | n/a       | n/a (owner) | create    |
| Connect to authority.sock          | yes (write) | r         | r        | n/a       |
| Connect to executor.sock           | yes (write) | n/a     | r        | n/a       |
| Launch processes                   | none      | none      | none     | full      |
| sudoers entry                      | none      | none      | none     | yes       |

**Change from v0.2 r0:** `ate-executor` no longer reads `authority.sqlite`
in any form (removed `ate-auth-group-ro`). All authority-state reads are
performed only by `ate-authority`. The executor receives authority
decisions exclusively via **signed decision envelopes** over IPC.

## 5. Startup / bootstrap sequence

The `trusted-bootstrap` operator runs once per test (or installation):

1. **Create OS identities** (idempotent):
   - `groupadd ate-authority`
   - `groupadd ate-executor`
   - `useradd -r -s /usr/sbin/nologin -G ate-authority ate-authority`
   - `useradd -r -s /usr/sbin/nologin -G ate-executor ate-executor`
   - Verify NO `ate-requester` user exists; if it does, verify it has
     NO membership in privileged groups and NO sudoers entry.
2. **Create state and IPC directories** as `trusted-bootstrap`, then chown:
   - `mkdir -p /var/lib/ate/authority /var/lib/ate/executor /var/lib/ate/resources`
   - `mkdir -p /run/ate /run/ate/authority /run/ate/executor`
   - `chown -R ate-authority:ate-authority /var/lib/ate/authority`
   - `chmod 0700 /var/lib/ate/authority`
   - `chown -R ate-executor:ate-executor /var/lib/ate/executor /var/lib/ate/resources`
   - `chmod 0700 /var/lib/ate/executor /var/lib/ate/resources`
   - `chown root:root /run/ate` (parent dir traversable by all UIDs)
   - `chmod 0755 /run/ate`
   - `chown ate-authority:ate-requester /run/ate/authority`
   - `chmod 0750 /run/ate/authority`
   - `chown ate-executor:ate-requester /run/ate/executor`
   - `chmod 0750 /run/ate/executor`
   - The `ate-requester` UID is added to a dedicated `ate-requester`
     group ONLY for the purpose of traversing `/run/ate/authority/`
     and `/run/ate/executor/` to reach the socket endpoints. The
     group has NO write permission on those directories.
3. **Generate authority Ed25519 keypair** AS `ate-authority`:
   - `sudo -u ate-authority ... openssl genpkey -algorithm ed25519 -out /var/lib/ate/authority/authority_signing.key`
   - `sudo -u ate-authority openssl pkey -in ... -pubout -out /var/lib/ate/executor/authority_pubkey.pem`
   - `chmod 0600` on private key, `0644` on public key.
4. **Generate per-resource credentials** AS `ate-executor`:
   - `sudo -u ate-executor ...` writes `resource_credentials.json`
     (HMAC keys, one per resource).
5. **Generate audit signing key** AS `ate-executor`:
   - `sudo -u ate-executor ... openssl genpkey -algorithm ed25519 -out audit_signing.key`
6. **Launch `ate-authority` service** AS `ate-authority`:
   - The service binds `/run/ate/authority/authority.sock` (mode 0660,
     owner `ate-authority:ate-requester`).
   - The service opens/creates `authority.sqlite` itself.
   - The service initializes schema if first start.
7. **Launch `ate-executor` service** AS `ate-executor`:
   - The service binds `/run/ate/executor/executor.sock` (mode 0660,
     owner `ate-executor:ate-requester`).
   - The service loads `resource_credentials.json`, `audit_signing.key`,
     `authority_pubkey.pem`.
   - The service opens/creates `executor.sqlite` itself.
8. **Drop into `ate-requester` UID** for test execution.

## 6. Authority service IPC model

### 6.1 Authority-owned decision envelope (Ed25519 signed)

`ate-authority` signs an Ed25519 envelope with its PRIVATE key. The
executor verifies with the corresponding PUBLIC key. NO shared secret.
NO HMAC.

### 6.2 Decision envelope fields

```json
{
  "envelope_version": "ATE-P1-V2-ENV-1",
  "policy_version": "ATE-P1-V2-POLICY-1",
  "decision_id": "<uuid>",
  "requester_uid": <int>,                // OS UID of the requester (the durable principal)
  "resource_id": "<sha256>",
  "operation": "WRITE_SCOPED" | "...",
  "operation_digest": "<sha256>",        // canonical digest of the operation request
  "nonce": "<base64>",
  "issued_at_unix_ms": <int>,
  "valid_until_unix_ms": <int>,          // explicit expiry
  "revocation_epoch_at_issue": <int>,    // authority's revocation epoch at issue time (advisory; not a controlling revocation guarantee — see §8)
  "constraints": { ... },                // any per-operation bindings
  "extensions": { ... }
}
```

**PID is intentionally NOT a security invariant.** PIDs are
recyclable by the kernel and cannot serve as durable process
identity. The requester principal is the OS UID (verified via
`SO_PEERCRED` on the requester socket connection to authority, and
re-verified by the executor on the executor socket).

The envelope is canonicalized (RFC 8785 JCS) and signed with
Ed25519 over the canonical bytes. The signature is appended to the
envelope: `{"envelope": {...}, "authority_sig": "<base64>"}`.

### 6.3 Authority IPC requests (requester → authority)

| Op                          | Payload                                                                                              | Response                                              |
|-----------------------------|------------------------------------------------------------------------------------------------------|-------------------------------------------------------|
| `get_decision_envelope`     | `{session_id, operation, resource_id, operation_digest, nonce, ttl_ms, validity_ms}`                 | `{envelope_blob, envelope_signature}` (Ed25519 signed) |
| `get_execution_clearance`   | `{envelope_blob, envelope_signature, clearance_ttl_ms}`                                              | `{clearance_blob, clearance_signature}` (Ed25519 signed) or `{denied, reason_code, already_issued_clearance_blob?, already_issued_clearance_signature?}` |
| `revoke`                    | `{decision_id, reason}`                                                                              | `{ok, revocation_epoch}`                              |

The authority service:
- Maintains `decision_envelopes` (issued envelopes), `execution_clearances`
  (issued clearances), `revocations` (revocation list by `decision_id`).
- On `get_decision_envelope`: allocates new decision_id, constructs
  envelope, signs with Ed25519 private key, persists envelope + signature.
- On `get_execution_clearance`: verifies the decision envelope
  signature first; verifies the envelope is not expired; verifies
  the envelope is not revoked; **atomically** issues a one-time
  `execution_clearance` and commits it. The clearance issuance is
  serialized against any concurrent `revoke` for the same
  `decision_id` (see §8).
- On `revoke`: appends to `revocations` in a SQLite transaction
  that is serialized against `get_execution_clearance` for the
  same `decision_id`.
- Never writes executor state, never reads executor state, never
  reads protected resources, never signs a decision or clearance
  without validating the caller's requester UID matches
  `SO_PEERCRED` on the connecting socket.

### 6.4 Clearance persistence and idempotency

The authority persists each issued clearance in
`authority.sqlite.execution_clearances` with the following schema
(equivalent; authoritative):

```sql
CREATE TABLE execution_clearances (
  clearance_id           TEXT PRIMARY KEY,        -- unique per clearance
  decision_id            TEXT NOT NULL UNIQUE,    -- EXACTLY ONE clearance per decision
  operation_id           TEXT NOT NULL UNIQUE,    -- stable operation identity bound to the decision
  requester_uid          INTEGER NOT NULL,
  resource_id            TEXT NOT NULL,
  operation              TEXT NOT NULL,
  operation_digest       TEXT NOT NULL,
  nonce                  TEXT NOT NULL,
  issued_at_unix_ms      INTEGER NOT NULL,
  valid_until_unix_ms    INTEGER NOT NULL,
  clearance_blob         TEXT NOT NULL,
  clearance_signature    TEXT NOT NULL
);

CREATE INDEX execution_clearances_by_decision ON execution_clearances(decision_id);
CREATE INDEX execution_clearances_by_operation ON execution_clearances(operation_id);
```

The `UNIQUE(decision_id)` constraint is the controlling cardinality
invariant: **at most one clearance row per authority decision**.

Issuance algorithm (single SQLite transaction, `BEGIN IMMEDIATE`):

1. Verify decision envelope signature, freshness, requester_uid
   match (`SO_PEERCRED`), and that the decision is not revoked.
2. `SELECT * FROM execution_clearances WHERE decision_id = ?`.
3. If a row exists:
   - **Preferred behavior for retry safety**: return the exact
     already-persisted `clearance_blob` + `clearance_signature`,
     wrapped in `{already_issued: true, clearance_blob, clearance_signature}`.
   - Do NOT mint another `clearance_id`.
   - Do NOT issue a new clearance under the same decision even
     if the prior one is expired (an expired clearance is
     terminal; a new authority decision is required for a new
     attempt).
4. If no row exists:
   - Allocate a fresh `clearance_id` (UUID) and a stable
     `operation_id` (UUID, derived from `decision_id` — see §6.6).
   - Construct the clearance envelope binding
     `clearance_id`, `decision_id`, `operation_id`, requester
     UID, resource, operation digest, nonce, validity bounds.
   - `INSERT INTO execution_clearances(...)` — the `UNIQUE` on
     `decision_id` and `operation_id` enforces no second
     issuance.
   - Sign the envelope with the authority Ed25519 private key.
   - `COMMIT`.
5. Concurrent issuance attempts on the same `decision_id`
   serialize at `BEGIN IMMEDIATE`. The loser sees the winner's
   row and returns the same persisted clearance (step 3).

The `UNIQUE(decision_id)` constraint and `UNIQUE(operation_id)`
constraint together guarantee that the cardinality invariant
holds even under arbitrary concurrency and retry patterns.

### 6.5 Clearance acquisition path (requester → authority)

The complete clearance acquisition flow is:

```
requester                       authority
    │                                │
    │─ get_decision_envelope ──────▶ │
    │   (operation, resource_id,    │
    │    operation_digest, nonce,   │
    │    ttl_ms, validity_ms)        │
    │                                │ BEGIN IMMEDIATE
    │                                │ issue decision
    │                                │ COMMIT
    │◀─ envelope_blob+signature ──── │
    │                                │
    │─ get_execution_clearance ────▶ │
    │   (envelope_blob,              │
    │    envelope_signature,         │
    │    clearance_ttl_ms)           │
    │                                │ BEGIN IMMEDIATE
    │                                │ verify envelope sig,
    │                                │  expiry, requester_uid,
    │                                │  not revoked
    │                                │ SELECT existing clearance
    │                                │  for decision_id
    │                                │ IF EXISTS:
    │                                │   return persisted
    │                                │ ELSE:
    │                                │   mint clearance_id,
    │                                │   operation_id,
    │                                │   INSERT, sign, COMMIT
    │◀─ clearance_blob+signature ─── │
    │   (or already_issued: true     │
    │    with same blob+sig)         │
```

The requester is the ONLY principal that contacts both
`ate-authority` and `ate-executor`. The executor NEVER connects
to `ate-authority.sock`, NEVER opens `authority.sqlite`, and
NEVER reads authority state. This matches the IPC permissions
(`ate-executor` is not in `ate-authority` group and has no
path to `/run/ate/authority/`). The executor receives decisions
and clearances exclusively via the requester's IPC submission
to `executor.sock`.

Possession of a signed decision or clearance by the requester
grants no authority: the requester cannot create valid authority
signatures (lacks the Ed25519 private key), and any forgery
attempt is detected by executor-side Ed25519 verification.

### 6.6 Stable operation identity (`operation_id`)

The authority allocates a stable `operation_id` (UUID) when
issuing a decision. The `operation_id` is cryptographically
bound to BOTH:

- The decision envelope (carried as a field).
- The clearance envelope (carried as a field).

Generation rule:

```
operation_id = UUID5(SHA256(canonical(decision_envelope_without_operation_id)))
```

(Implementation can use `uuid.uuid5` over the canonical
decision-envelope bytes.) The `operation_id` is therefore
deterministic given the decision contents: the same decision
envelope always produces the same `operation_id`. This makes
the operation identity:

- Stable across retries (the requester can recompute it).
- Immutable (the authority cannot change it after issuance —
  doing so would invalidate the decision signature).
- Independent of `clearance_id` (so an expired clearance can be
  distinguished from a never-issued one for the same decision).

The `operation_id` is the **controlling idempotency key** for
resource mutation (§9.2). It is the identity bound into both the
decision and the clearance; it is what the resource records in
`applied_operation_ids`.

### 6.7 Authority never touches executor state

`ate-authority` does NOT:
- Open `executor.sqlite`.
- Read or write `/var/lib/ate/executor/`.
- Receive or hold `audit_signing.key`, `resource_credentials.json`,
  or `authority_pubkey.pem`.

## 7. Executor service IPC model

### 7.1 Executor IPC requests (requester → executor)

| Op        | Payload                                                                                                              | Response                                              |
|-----------|----------------------------------------------------------------------------------------------------------------------|-------------------------------------------------------|
| `execute` | `{clearance_blob, clearance_signature, requester_payload}`                                                           | `{verdict, reason_code, audit_seq, mutation_count}`   |

`clearance_blob` + `clearance_signature` are the authority-issued
EXECUTION CLEARANCE (a separate signed artifact from the decision
envelope — see §8). `requester_payload` is the canonical operation
request. The executor does NOT receive the decision envelope directly;
it only receives the clearance that authorizes a specific execution
of an already-decided operation.

### 7.2 Executor state machine (durable acceptance via PREPARED)

The executor maintains a durable state machine for each clearance,
recorded in `executor.sqlite.executor_operations`:

```
        ┌────────────┐  durable commit   ┌────────────┐  apply+record    ┌────────────┐
init →  │ (none)     │ ───────────────▶ │ PREPARED   │ ──────────────▶  │ MUTATED    │
        └────────────┘                  └────────────┘   operation_id    └────────────┘
                                            │  ▲                                   │
                                            │  │                                   │
                                            ▼  │  recovery resume                  ▼
                                       (recovery                          ┌────────────┐
                                        re-enters                         │ COMPLETED  │
                                        PREPARED state                    └────────────┘
                                        on crash before                    audit + anchor
                                        mutation)                          committed
```

Each transition is a separate SQLite transaction in `executor.sqlite`:

- **`PREPARED`** transition: claims the clearance_id, claims the
  nonce, records audit intent. This is the **linearization point**
  for the executor's acceptance — once `PREPARED` is durably
  committed, the clearance is bound to this executor instance and
  recovery will resume the operation even across crashes.
- **`MUTATED`** transition: applies the idempotent mutation to the
  protected resource (which transactionally records the
  `operation_id`). If the resource already has the `operation_id`,
  the executor reports `EX_ALREADY_APPLIED` (idempotent) and
  proceeds to `COMPLETED` without re-mutating.
- **`COMPLETED`** transition: appends the audit record and updates
  the audit anchor.

### 7.3 Executor verification + execution sequence

Before each transition, the executor performs the following checks:

For `PREPARED` transition:

1. **Verify clearance signature** using `authority_pubkey.pem` —
   reject with `EX_CLEARANCE_SIG_INVALID` on mismatch.
2. **Verify clearance fields bind to the request**:
   - `clearance.decision_id` must reference a known decision.
   - `clearance.nonce` must not yet be recorded in
     `executor_nonces` (PREPARED or CONSUMED) for this executor.
   - `clearance.resource_id` matches `requester_payload.resource_id`.
   - `clearance.operation` matches `requester_payload.operation`.
   - `clearance.operation_digest` matches
     `sha256(canonical(requester_payload))`.
   - `clearance.requester_uid` matches `SO_PEERCRED` UID of the
     calling process.
   - `clearance.issued_at_unix_ms` and `valid_until_unix_ms`
     bracket `now` — reject with `EX_CLEARANCE_EXPIRED` if past.
3. **Verify clearance is not revoked** — query
   `executor_revoked_clearances` (which the authority pushes via a
   separate, infrequent update channel — see §8.4) — reject with
   `EX_CLEARANCE_REVOKED` if found. This is a defense-in-depth
   check; the authoritative guarantee is the ordering with respect
   to the clearance issuance itself (see §8).
4. **Verify resource credential** (executor-local):
   - Load `resource_credentials.json` for the per-resource HMAC
     key.
   - Recompute HMAC over the canonicalized mutation payload,
     constant-time compare with the resource's expected HMAC
     stored in `executor.sqlite.executor_resources`.
   - Reject with `EX_RESOURCE_CREDENTIAL_INVALID` on mismatch.
5. **DURABLY COMMIT PREPARED state** in `executor.sqlite`:
   - `BEGIN IMMEDIATE`
   - `INSERT INTO executor_nonces(nonce, decision_id, state='PREPARED',
     clearance_id, prepared_at)`.
   - `INSERT INTO executor_operations(clearance_id, state='PREPARED',
     decision_id, nonce, resource_id, operation, requester_uid,
     operation_payload_canonical, prepared_at)`.
   - `COMMIT`

This commit is the executor's **durable acceptance / linearization
point**. After this commit, the clearance is bound to this
executor instance.

For `MUTATED` transition:

6. **Idempotent resource mutation** as `ate-executor`:
   - Open `/var/lib/ate/resources/<id>/state.json` for write.
   - Check `applied_operation_ids` in the resource for
     `clearance_id`:
     - If absent: apply mutation, atomically append
       `clearance_id` to `applied_operation_ids`, write+fsync.
     - If present: skip mutation; report `EX_ALREADY_APPLIED`.
   - On `EX_ALREADY_APPLIED`, proceed to `COMPLETED` without
     re-mutating.
7. **DURABLY COMMIT MUTATED state** in `executor.sqlite`:
   - `BEGIN IMMEDIATE`
   - `UPDATE executor_operations SET state='MUTATED',
     mutated_at=now, mutation_outcome='APPLIED'|'ALREADY_APPLIED'
     WHERE clearance_id=?`.
   - `COMMIT`

For `COMPLETED` transition:

8. **Append audit record** to `executor_audit_records`:
   - HMAC-SHA-256 chain: `prev_chain_mac || canonical(record) → record_mac`.
   - The chain is signed by `audit_signing.key` (Ed25519).
9. **Update audit anchor** in `executor_audit_anchor`:
   - `final_seq`, `final_record_digest`, `anchor_sig` (Ed25519).
10. **Mark nonce CONSUMED** in `executor_nonces`.
11. `COMMIT`

The executor NEVER opens `authority.sqlite`.

## 8. Revocation semantics — EXECUTION CLEARANCE model

### 8.1 Execution clearance (Ed25519 signed)

The authority issues a separate, one-time **EXECUTION CLEARANCE**
for each accepted execution. The clearance is the artifact the
executor accepts; it is NOT the decision envelope. This separation
allows the authority to atomically serialize clearance issuance
against revocation.

### 8.2 Clearance envelope fields

```json
{
  "clearance_version": "ATE-P1-V2-CLR-1",
  "policy_version": "ATE-P1-V2-POLICY-1",
  "clearance_id": "<uuid>",                // unique per clearance
  "decision_id": "<uuid>",                 // binds to the underlying decision
  "operation_id": "<uuid>",                // stable operation identity; controlling idempotency key for the resource
  "requester_uid": <int>,                  // OS UID of the requester
  "resource_id": "<sha256>",
  "operation": "WRITE_SCOPED" | "...",
  "operation_digest": "<sha256>",
  "nonce": "<base64>",                     // bound to the decision
  "issued_at_unix_ms": <int>,
  "valid_until_unix_ms": <int>,            // tightly bounded validity
  "one_shot": true,                        // may be used exactly once
  "constraints": { ... },
  "extensions": { ... }
}
```

The clearance is canonicalized (RFC 8785 JCS) and signed with
the **same** Ed25519 private key the authority uses for decision
envelopes. The signature is appended:
`{"clearance": {...}, "clearance_sig": "<base64>"}`.

The executor verifies the clearance with `authority_pubkey.pem`.
The executor cannot manufacture a clearance (lacks the private
key).

### 8.3 Ordering guarantee (controlling revocation rule)

The authority serializes two operations on the same `decision_id`:

- `get_execution_clearance(decision_id, ...)` — issues a clearance
  and persists it.
- `revoke(decision_id, ...)` — appends to the revocation list and
  persists it.

Both are wrapped in a SQLite `BEGIN IMMEDIATE` transaction on
`authority.sqlite`, with a serialization conflict (SQLITE_BUSY)
retried up to N times (default 100, exponential backoff). The
authority guarantees:

- **If `revoke` commits BEFORE `get_execution_clearance` reads the
  decision row** → the clearance request sees the revocation and
  the clearance is DENIED (`EX_CLEARANCE_REVOKED`).
- **If `get_execution_clearance` reads the decision row BEFORE
  `revoke` is called** → the clearance is committed and remains
  valid according to its `valid_until_unix_ms` bound. A subsequent
  `revoke` on the same `decision_id` will mark the decision as
  revoked, but it will NOT retroactively invalidate the already-
  committed clearance. The clearance is one-shot (the executor
  consumes it on first use); subsequent attempts to use the same
  clearance fail with `EX_CLEARANCE_ALREADY_CONSUMED`.

This ordering guarantee is the **controlling revocation guarantee
for P1**. It is enforced by SQLite's `BEGIN IMMEDIATE` transaction
serialization on the authority's `authority.sqlite` (a single
process, single-writer, no concurrent writers).

### 8.4 Defense-in-depth revocation push (informational only)

The authority MAY push revocation updates to the executor over a
separate, infrequent channel (e.g., a file in `/run/ate/revocations/`
or a low-frequency IPC). The executor maintains
`executor_revoked_clearances` as a defense-in-depth cache and
checks it during the `PREPARED` transition (§7.3 step 3).

This push channel is **not** the controlling revocation guarantee.
The controlling guarantee is the ordering in §8.3. The push channel
exists to detect revocation attempts that arrive AFTER clearance
issuance but BEFORE executor acceptance — it cannot invalidate an
already-issued clearance; it can only fail subsequent attempts to
**use** a clearance whose decision has been revoked.

### 8.5 Explicit TOCTOU acknowledgment

P1 guarantees the ordering of clearance issuance vs. revocation
through authority-internal SQLite serialization. P1 does NOT
guarantee revocation-vs-execution atomicity once the executor has
PREPARED a clearance — that is the executor's responsibility (the
PREPARED state machine and idempotent resource mutation). Per PI
threat model, TOCTOU between runtime attestation and action
execution is explicitly OUT OF SCOPE.

### 8.6 Revocation sequence diagram

```
requester                 authority                       executor
    │                          │                              │
    │─get_decision_envelope─▶  │                              │
    │                          │ (issue envelope, persist)    │
    │◀─envelope_blob+sig──────│                              │
    │                          │                              │
    │─get_execution_clearance─▶│                              │
    │  (envelope_blob+sig,    │                              │
    │   requester_sig)        │                              │
    │                          │ BEGIN IMMEDIATE              │
    │                          │ check decision not revoked   │
    │                          │ INSERT clearance             │
    │                          │ COMMIT                       │
    │◀─clearance_blob+sig─────│                              │
    │                          │                              │
    │─execute─(clearance,sig, payload)──────────────────────▶│
    │                          │                              │ verify sig, fields
    │                          │                              │ BEGIN IMMEDIATE
    │                          │                              │ INSERT executor_operations
    │                          │                              │  state=PREPARED
    │                          │                              │ COMMIT  ◀── LINEARIZATION
    │                          │                              │ apply idempotent mutation
    │                          │                              │ BEGIN IMMEDIATE
    │                          │                              │ UPDATE state=MUTATED
    │                          │                              │ COMMIT
    │                          │                              │ BEGIN IMMEDIATE
    │                          │                              │ append audit, anchor
    │                          │                              │ UPDATE state=COMPLETED
    │                          │                              │ COMMIT
    │◀─EXECUTED, audit_seq, mutation_count───────────────────│
```

In a concurrent revoke path:

```
authority                                  requester
    │                                          │
    │ BEGIN IMMEDIATE                            │
    │ INSERT revocations(decision_id)            │
    │ COMMIT                                      │
    │                                          │
    │ (subsequent get_execution_clearance for   │
    │  the same decision_id)                    │
    │ BEGIN IMMEDIATE                            │
    │ check revocations → DECISION_REVOKED       │
    │ DENY clearance                             │
    │ COMMIT                                      │
```

The two `BEGIN IMMEDIATE` calls serialize at the SQLite level
because the authority service is a single-process writer. Either
the clearance commits first (then the revocation cannot invalidate
the already-committed clearance) or the revocation commits first
(then any subsequent clearance request sees the revocation).

## 9. Atomicity, crash consistency, and idempotent mutation

### 9.1 Atomicity model

P1 uses a **durable state machine plus idempotent resource
application** to obtain crash-safe, at-most-once observable mutation.
P1 does NOT claim cross-store ACID atomicity.

- Each transition of the executor state machine (§7.2) is atomic
  within `executor.sqlite` via `BEGIN IMMEDIATE` / `COMMIT`.
- The protected resource mutation is idempotent — applying a given
  `clearance_id` is a no-op if the operation has already been applied.
- The resource records the `clearance_id` transactionally with the
  mutation, so recovery can safely resume.

### 9.2 Idempotent protected resource mutation

The protected resource `/var/lib/ate/resources/<id>/state.json` is a
JSON document containing:

```json
{
  "resource_id": "<sha256>",
  "display_path": "...",
  "state": { ... },
  "mutation_count": <int>,
  "applied_operation_ids": ["<operation_id>", ...]
}
```

The executor's mutation step:

1. Read the resource JSON (as `ate-executor`).
2. Check if `operation_id` (carried in the clearance envelope;
   bound to the decision) is in `applied_operation_ids`:
   - **Absent**: apply the mutation to `state`, increment
     `mutation_count`, append `operation_id` to
     `applied_operation_ids`, write the JSON atomically
     (temp file + `rename(2)`), `fsync(2)`; record outcome
     `APPLIED`.
   - **Present**: skip mutation; do NOT increment
     `mutation_count`; record outcome `ALREADY_APPLIED`.
3. The recorded outcome (`APPLIED` or `ALREADY_APPLIED`) is what
   flows into the executor's `MUTATED` and `COMPLETED` state
   transitions — never a duplicate observable mutation.

The `operation_id` is the **stable operation identity** bound
into both the decision and the clearance (see §6.6). It is
deterministic given the decision contents, so it is the same
across all retries, recovery attempts, and re-issuances of the
clearance under the same decision. Resource idempotency is keyed
on `operation_id` — NOT on `clearance_id` — because a retry that
obtains a re-issued (already-persisted) clearance returns the
same `operation_id` (decision-bound), even if a future design
were to mint a new `clearance_id` per call (which it must not,
per §6.4).

### 9.3 Crash states and recovery semantics

The executor's `executor_operations` table tracks the state of each
`operation_id` (one row per operation; `clearance_id` is a
secondary column for debugging). On restart, the executor scans
for operations in non-terminal states and resumes them.

| Crash point                                              | executor.sqlite state             | resource state                              | Recovery                                                                                       |
|----------------------------------------------------------|-----------------------------------|---------------------------------------------|------------------------------------------------------------------------------------------------|
| A. Before `PREPARED` COMMIT                              | no row                            | untouched                                   | Operation has not started; requester may re-submit (clearance still valid, idempotent).        |
| **B. After `PREPARED` COMMIT, before resource mutation**  | `state=PREPARED`                  | untouched                                   | Recovery resumes: re-attempt the idempotent mutation; resource records `clearance_id` once.    |
| **C. After resource mutation, before `MUTATED` COMMIT**  | `state=PREPARED`                  | mutated, `clearance_id` recorded            | Recovery resumes: idempotent mutation reports `EX_ALREADY_APPLIED`; commit `MUTATED`. No duplicate mutation. |
| **D. After `MUTATED` COMMIT, before `COMPLETED` COMMIT** | `state=MUTATED`                   | mutated, `clearance_id` recorded            | Recovery resumes: append audit, update anchor, commit `COMPLETED`.                              |
| E. After `COMPLETED` COMMIT                              | `state=COMPLETED`                 | mutated, `clearance_id` recorded            | Normal end state.                                                                              |

### 9.4 P1 does NOT claim cross-store ACID atomicity

The mutation succeeds at-most-once observable because:

- The `PREPARED` state machine entry claims the `clearance_id`
  durably before mutation.
- The resource records `clearance_id` transactionally with the
  mutation.
- On restart, the executor uses the `clearance_id` to determine
  whether the resource has already been mutated (case C); the
  mutation is idempotent.

P1 explicitly does NOT require a single transactional store
covering `executor.sqlite` and `/var/lib/ate/resources/<id>/state.json`.
It uses a durable state machine + idempotent application to obtain
the same observable outcome.

## 10. IPC namespace hardening

### 10.1 Split per-service directory layout

```
/run/ate/                                (root:root, mode 0755)
├── authority/                           (ate-authority:ate-requester, mode 0750)
│   └── authority.sock                   (ate-authority:ate-requester, mode 0660)
└── executor/                            (ate-executor:ate-requester, mode 0750)
    └── executor.sock                    (ate-executor:ate-requester, mode 0660)
```

Per-service subdirectories are used so the requester can traverse
to reach the socket endpoints without granting it write access to
any directory:

- `/run/ate/` is owned by `root:root`, mode 0755 — traversable by
  all UIDs (including `ate-requester`).
- `/run/ate/authority/` is owned `ate-authority:ate-requester`,
  mode 0750. `ate-requester` has read+execute (traversal) via
  group membership but NO write permission. `ate-authority` has
  rwx via owner. Other UIDs (including `ate-executor`) have NO
  access.
- `/run/ate/executor/` is owned `ate-executor:ate-requester`,
  mode 0750. Same pattern for `ate-executor` and `ate-requester`.
- Socket files themselves are mode 0660 with
  `owner:ate-requester` so the requester can `connect()` and
  `write()` to them; only the service owner can `bind()` a new
  socket in place.

Consequences:
- `ate-requester` can `connect()` to both sockets and `write()`
  to them.
- `ate-requester` CANNOT `unlink()`, `rename()`, or `bind()` a
  replacement socket at either path (no write permission on the
  parent directory).
- `ate-requester` CANNOT create files inside `/run/ate/authority/`
  or `/run/ate/executor/`.
- `ate-requester` cannot traverse across the two subdirectories
  in unintended ways (it has `r-x` on each but no `w`).

### 10.2 Service-to-service authentication

When the executor verifies an authority decision or clearance, it
MUST verify the artifact is genuinely from `ate-authority`. This
is done by **Ed25519 signature verification** using
`authority_pubkey.pem` (§7.3 step 1). Pathname possession of the
authority socket is not the trust anchor.

### 10.3 Client UID verification

`SO_PEERCRED` is used to verify that the IPC client IS
`ate-requester` (the expected requester UID) for both
`get_decision_envelope`, `get_execution_clearance`, `revoke`, and
`execute`. It is NOT used as the sole service-authentication
mechanism; the authority and executor verify message contents
via Ed25519 signatures.

### 10.4 No inherited FDs

The requester process does NOT inherit any privileged FDs at
startup (no SUID binary, no file descriptor passing from
bootstrap). AT-21 verifies this.

### 10.5 No supplementary-group leakage (beyond `ate-requester`)

The `ate-requester` UID is in ONE supplementary group:
`ate-requester`. This group has ONLY traversal rights on
`/run/ate/authority/` and `/run/ate/executor/` (no write, no read
of privileged state). AT-22 verifies this exact group set.

### 10.6 No env/credential leakage

The requester process is launched with a minimal environment
(no `*_KEY`, no `*_SECRET`, no `*_TOKEN`). AT-23 verifies this.

## 11. SQLite lifecycle

### 11.1 Authority SQLite

- Only `ate-authority` opens `authority.sqlite` for read or write.
- The authority service creates the DB on first start.
- WAL/SHM/JOURNAL sidecars inherit directory ownership naturally
  (created by `ate-authority` in a directory it owns).
- No chown choreography required.

### 11.2 Executor SQLite

- Only `ate-executor` opens `executor.sqlite` for read or write.
- The executor service creates the DB on first start.
- Sidecars inherit directory ownership naturally.
- The executor never opens `authority.sqlite` (issue #2 resolved).

### 11.3 Requester

- `ate-requester` has no path under either state directory.
- All requests go through Unix domain socket IPC.

## 12. Requester adversary model

`ate-requester` is permitted to:
- Know all paths, filenames, schema details, IPC endpoints, socket
  names, and message formats.
- Connect to `/var/run/ate/authority.sock` and `/var/run/ate/executor.sock`.
- Send arbitrary IPC messages on those sockets.
- Read public documentation, design documents, and source code.

`ate-requester` is forbidden from (and prevented from):
- Reading or writing any file under `/var/lib/ate/authority/`,
  `/var/lib/ate/executor/`, or `/var/lib/ate/resources/`.
- Opening `/var/run/ate/authority.sock` or `/var/run/ate/executor.sock`
  for write to replace/unlink/bind.
- Reading `authority_signing.key`, `audit_signing.key`,
  `resource_credentials.json`.
- Spawning processes as `ate-authority`, `ate-executor`, or root.
- Acquiring sudo or setuid privilege.
- Issuing raw SQL against `authority.sqlite` or `executor.sqlite`
  (cannot open the files).
- Writing to protected resource state files directly.
- Crafting a valid authority envelope (lacks the private key).
- Replaying a consumed nonce (executor rejects).
- Resetting executor replay state (no write access to `executor.sqlite`).
- Impersonating a trusted service (Ed25519 signatures reject
  unsigned or wrong-key signatures).

## 13. Invariants

- **I1_NO_BYPASS**: Arbitrary code executing as `ate-requester`
  cannot create an authoritative decision or execution clearance,
  directly read or mutate authority state, obtain authority or
  executor secrets, reset executor replay state, directly mutate
  the protected resource, impersonate a trusted service, or bypass
  enforcement. Authorized mutation is possible only through the
  authority-signed clearance and executor-verification path.
- **I2_AUTHORITY_INTEGRITY**: Authority state is owned exclusively
  by `ate-authority`. Neither the parent harness nor the executor
  opens `authority.sqlite`.
- **I3_EXECUTOR_CREDENTIAL_ISOLATION**: Per-resource credentials
  live exclusively in
  `/var/lib/ate/executor/resource_credentials.json`. The authority
  never receives or holds these credentials.
- **I4_AUTHORITY_SIGNING_KEY_ISOLATION**: The authority's Ed25519
  private signing key is owned and used only by `ate-authority`.
  The executor holds only the public verification key.
- **I5_AUDIT_INTEGRITY**: Audit chain integrity verified on executor
  startup; tamper → executor refuses.
- **I6_OPERATION_IDEMPOTENCY**: One authority decision / stable
  `operation_id` can cause at most one observable protected-resource
  mutation. The resource transactionally records `operation_id`
  with the mutation; repeated application of the same
  `operation_id` returns `EX_ALREADY_APPLIED` without another
  mutation. `operation_id` is the controlling idempotency key
  (not `clearance_id`).
- **I7_REVOCATION_ORDERING**: Within authority-internal SQLite
  serialization, a `revoke` that commits before
  `get_execution_clearance` reads the decision causes the clearance
  to be denied. A clearance that commits first remains valid until
  its `valid_until_unix_ms` and is one-shot; subsequent `revoke`
  does NOT retroactively invalidate it. This is the controlling
  revocation guarantee for P1.
- **I8_CLEARANCE_CARDINALITY**: One authority decision can
  correspond to no more than one unique execution clearance.
  Enforced by `UNIQUE(decision_id)` on
  `authority.sqlite.execution_clearances`. Repeated
  `get_execution_clearance` for the same `decision_id` returns
  the exact already-persisted clearance (or, on `SQLITE_BUSY`,
  the winner's persisted clearance). Concurrent issuance
  attempts converge on one persisted clearance. An expired
  clearance cannot be replaced by a new clearance under the
  same decision; a new authority decision is required.
- **I9_CLEARANCE_VERIFICATION**: Executor verifies the authority-
  signed clearance via Ed25519 public key before committing the
  PREPARED state.
- **I10_REQUESTER_UID_BINDING**: Authority and executor verify
  the IPC peer's OS UID (`SO_PEERCRED`) matches the envelope's
  and clearance's `requester_uid`. The requester principal is
  the OS UID; PID is NOT a security invariant.
- **I11_LINEARIZATION_POINT**: The executor's durable acceptance
  is the `PREPARED` transition commit (not `BEGIN IMMEDIATE`).
  Once PREPARED is committed, recovery will resume the operation.
- **I12_DURABLE_STATE_MACHINE**: Each transition (PREPARED →
  MUTATED → COMPLETED) is a separate SQLite transaction in
  `executor.sqlite`, keyed on `operation_id`.
- **I13_CRASH_SAFE_IDEMPOTENT_MUTATION**: Resource mutation is
  idempotent on `operation_id`. Crash before mutation → recovery
  applies mutation once. Crash after mutation before COMPLETED →
  recovery observes `EX_ALREADY_APPLIED` and proceeds to
  COMPLETED without duplicate mutation.
- **I14_DISTINCT_UID_ISOLATION**: The three principals run under
  distinct OS UIDs with no privileged-group overlap (the
  `ate-requester` UID is only in the dedicated `ate-requester`
  group for traversal of `/run/ate/authority/` and
  `/run/ate/executor/`). No sudoers entries.
- **I15_EXECUTOR_NO_AUTHORITY_ACCESS**: The executor never
  connects to `ate-authority.sock`, never opens
  `authority.sqlite`, and never reads authority state. All
  authority→executor communication flows through the requester's
  IPC submission to `executor.sock` carrying decision envelope +
  clearance envelope (both Ed25519-verified).
- **I16_OPERATION_ID_BINDING**: The `operation_id` is
  cryptographically bound into both the decision envelope and the
  clearance envelope (signed fields). It is deterministic given
  the decision contents (§6.6), so a re-issued clearance under
  the same decision carries the same `operation_id`.

## 14. Test matrix T0–T10 successor mapping (revised r2)

| Test | Name                              | New mechanism                                                                                                                  |
|------|-----------------------------------|--------------------------------------------------------------------------------------------------------------------------------|
| T0   | Service startup + canonical mode  | Authority + executor services start; verify `/var/lib/ate/authority/` mode 0700 owner ate-authority; `/var/lib/ate/executor/` mode 0700 owner ate-executor; `/run/ate/authority/` mode 0750 owner `ate-authority:ate-requester`; `/run/ate/executor/` mode 0750 owner `ate-executor:ate-requester`. |
| T1   | Direct resource bypass (requester) | `ate-requester` attempts `open(/var/lib/ate/resources/<id>/state.json, O_WRONLY)` → `EACCES`.                                  |
| T2   | Authority credential isolation    | `ate-requester` attempts to open `authority_signing.key` → `EACCES`. IPC attempt to authority without requester_uid match → DENIED. |
| T3   | Happy-path execution              | Requester → authority (get_decision_envelope) → authority (get_execution_clearance, signed) → executor (execute with clearance). Verify mutation_count increased by exactly 1. |
| T4   | Clearance signature invalid       | Requester sends `execute` with a clearance signed by a wrong Ed25519 key → executor rejects (`EX_CLEARANCE_SIG_INVALID`).    |
| T5   | Concurrent replay                 | 16 concurrent `ate-requester` subprocesses send same `clearance_id` to executor; exactly 1 EXECUTED, 15 DENIED (`EX_NONCE_REPLAY_OR_BUSY`). |
| T6   | Crash before mutation (state B)   | Inject crash after `PREPARED` COMMIT but before resource mutation → restart → recovery resumes → mutation occurs once. mutation_count increased by exactly 1. |
| T7   | Audit tamper                      | `ate-executor` deliberately corrupts an audit record's MAC → executor startup fails → refuses.                                 |
| T8   | Restart consistency               | Restart executor; new requester session; verify state persists.                                                                |
| T9   | Startup integrity (executor)      | Restart executor after audit anchor tamper → executor refuses to open.                                                         |
| T10  | Crash after mutation, before COMPLETED (state C) | Kill executor after resource mutation fsync but before `MUTATED` COMMIT → restart → recovery: idempotent mutation reports `EX_ALREADY_APPLIED` → commit `MUTATED` → commit `COMPLETED`. mutation_count increased by exactly 1, no duplicate mutation. |

### 14.1 Explicit attack tests (revised r2)

| AT    | Name                                          | Mechanism                                                                                                              |
|-------|-----------------------------------------------|------------------------------------------------------------------------------------------------------------------------|
| AT-1  | Sudo escalation                               | `ate-requester` invokes `sudo -u ate-authority whoami` → "not in sudoers".                                              |
| AT-2  | UID impersonation via setuid                  | `ate-requester` execve's a setuid binary → fails. Verify no setuid binaries are in any reachable path.                  |
| AT-3  | Direct authority DB open (read)               | `ate-requester` opens `authority.sqlite` → `EACCES`.                                                                   |
| AT-4  | Direct authority DB open (write)              | `ate-requester` opens `authority.sqlite` write → `EACCES`.                                                              |
| AT-5  | Authority WAL sidecar open                    | `ate-requester` opens `authority.sqlite-wal` → `EACCES`.                                                               |
| AT-6  | Authority SHM sidecar open                    | `ate-requester` opens `authority.sqlite-shm` → `EACCES`.                                                               |
| AT-7  | Authority journal sidecar open                | `ate-requester` opens `authority.sqlite-journal` → `EACCES`.                                                           |
| AT-8  | Direct resource state write                   | `ate-requester` opens `/var/lib/ate/resources/<id>/state.json` write → `EACCES`.                                       |
| AT-9  | Resource credentials read                     | `ate-requester` opens `/var/lib/ate/executor/resource_credentials.json` → `EACCES`.                                   |
| AT-10 | Authority signing key read                    | `ate-requester` opens `/var/lib/ate/authority/authority_signing.key` → `EACCES`.                                       |
| AT-11 | Audit signing key read                        | `ate-requester` opens `/var/lib/ate/executor/audit_signing.key` → `EACCES`.                                            |
| AT-12 | Forged authority decision envelope            | Requester fabricates envelope with no authority_sig → authority rejects at envelope issuance; if pre-signed envelope obtained, executor verification fails → DENIED. |
| AT-13 | Forged execution clearance                    | Requester fabricates clearance signed by a freshly generated Ed25519 key → executor Ed25519 verification fails → DENIED. |
| AT-14 | Executor attempt to manufacture authority decision/clearance | `ate-executor` cannot sign an envelope or clearance (does not hold `authority_signing.key`). Even if it fabricates one, executor's own verification rejects it (wrong key). |
| AT-15 | Replayed clearance (one-shot violation)       | Requester sends same clearance twice → second call's `clearance_id` already recorded in `executor_operations` → DENIED. |
| AT-16 | Restart with consumed authorization          | Restart executor; requester re-sends previously-issued clearance → `executor_operations.clearance_id` is in terminal state → DENIED. |
| AT-17 | Concurrent execute on same clearance         | 32 concurrent `execute` on same `clearance_id` → exactly 1 EXECUTED, 31 DENIED (`EX_NONCE_REPLAY_OR_BUSY`).            |
| AT-18 | Revocation committed before clearance         | Authority calls `revoke` on a decision, then the same requester calls `get_execution_clearance` → authority returns `{denied: EX_CLEARANCE_REVOKED}`. |
| AT-19 | Clearance committed before revocation         | Requester calls `get_execution_clearance` and receives a clearance; THEN authority calls `revoke`; requester calls `execute` → clearance is still valid (one-shot) → EXECUTED. |
| AT-20 | Audit chain tamper (byte flip)                | `ate-executor` flips a byte in audit record body → executor startup integrity check fails → refuses.                   |
| AT-21 | Anchor MAC tamper                             | `ate-executor` flips a byte in audit anchor → executor startup fails → refuses.                                        |
| AT-22 | Crash BEFORE PREPARED (case A)                | Kill executor after IPC receive but before `PREPARED` COMMIT → restart → requester re-submits clearance → succeeds (idempotent: `clearance_id` still unused in resource). |
| AT-23 | Crash AFTER PREPARED, before mutation (case B)| Kill executor immediately after `PREPARED` COMMIT → restart → recovery resumes: idempotent mutation applies once → COMPLETED. mutation_count increased by exactly 1. |
| AT-24 | Crash AFTER mutation, before COMPLETED (case C)| Kill executor after resource mutation fsync but before `MUTATED` COMMIT → restart → recovery: idempotent mutation reports `EX_ALREADY_APPLIED` → commit `MUTATED` → commit `COMPLETED`. mutation_count increased by exactly 1. |
| AT-25 | Duplicate clearance_id replay after restart   | Submit a `clearance_id`, executor COMPLETES it; restart; submit same `clearance_id` → DENIED (`EX_NONCE_REPLAY_OR_BUSY` via `executor_operations` lookup). |
| AT-26 | Requester connect but cannot rebind sockets   | `ate-requester` can `connect()` to `/run/ate/authority/authority.sock` and `/run/ate/executor/executor.sock`; cannot `unlink()` either path; cannot `bind()` a replacement socket at either path. |
| AT-27 | Inherited privileged FDs                      | At requester process startup, scan `/proc/self/fd/` — no FD points into `/var/lib/ate/` or `/run/ate/authority/` or `/run/ate/executor/`. Verify bootstrap does not pass privileged FDs to the requester process. |
| AT-28 | Supplementary-group leakage                   | `os.getgroups()` for `ate-requester` returns exactly `['ate-requester']` — no `ate-authority`, no `ate-executor`, no privileged groups. The single `ate-requester` group has only traversal rights on the IPC subdirectories. |
| AT-29 | Environment / credential leakage             | Requester process environment is minimal — no `*_KEY`, `*_SECRET`, `*_TOKEN`, `*_PRIVATE` env vars present.            |
| AT-30 | Idempotent resource application                | Run the same `clearance_id` through the executor twice (e.g., via recovery simulation). Resource `applied_operation_ids` contains exactly one entry; `mutation_count` increased by exactly 1. |
| AT-31 | IPC without authority clearance              | Requester → executor directly without a clearance → executor rejects (`EX_CLEARANCE_SIG_INVALID` or missing-clearance). |
| AT-32 | Clearance validity bound                       | A clearance with `valid_until_unix_ms < now` is rejected by the executor (`EX_CLEARANCE_EXPIRED`) before PREPARED commit. |
| AT-33 | Cross-UID requester_uid mismatch              | A clearance issued with `requester_uid=A` is presented to the executor by a process whose `SO_PEERCRED` UID is `B != A` → DENIED (`EX_REQUESTER_UID_MISMATCH`). |
| **AT-34** | **Repeated clearance request returns same persisted clearance** | Two consecutive `get_execution_clearance` calls for the same `decision_id` return the same `clearance_blob` + `clearance_signature` (and same `clearance_id`, `operation_id`). The second response carries `{already_issued: true}`. |
| **AT-35** | **Concurrent clearance requests converge to one** | N concurrent `get_execution_clearance` calls for the same `decision_id` from N requester subprocesses — exactly one clearance row is persisted in `authority.sqlite.execution_clearances`; all N responses carry the same `clearance_id` and `operation_id`. |
| **AT-36** | **Expired clearance cannot be replaced under the same decision** | A clearance is issued; the wall clock advances past `valid_until_unix_ms`; a second `get_execution_clearance` for the same `decision_id` returns the SAME (now-expired) clearance, NOT a new one. To execute the operation, a new authority decision is required. |
| **AT-37** | **Repeated decision/clearance presentation results in exactly one mutation** | Submit the same `(decision_id, clearance_id)` to the executor twice. The second submission reports `EX_ALREADY_APPLIED`; `mutation_count` increases by exactly 1 across both attempts. |
| **AT-38** | **Resource idempotency across distinct delivery attempts** | Submit the same `operation_id` to the executor via two different clearances (e.g., a freshly re-issued clearance, which carries the same `operation_id` per §6.6) — only the first attempt mutates the resource; the second reports `EX_ALREADY_APPLIED`; `mutation_count` increased by exactly 1. |
| **AT-39** | **Executor verifies requester UID binding against signed artifacts** | The executor's `PREPARED` transition verifies that `SO_PEERCRED` UID == `clearance.requester_uid` and == `decision.requester_uid`. Cross-UID mismatches are rejected before mutation. |
| **AT-40** | **Executor requires no authority socket/database access** | The executor process has no path to `/run/ate/authority/` and no path to `/var/lib/ate/authority/`. Code review confirms no `connect(/run/ate/authority/authority.sock)` or `open(/var/lib/ate/authority/...)` call exists in the executor binary. AT-3..AT-11 + AT-26 confirm at the OS level. |

## 15. Residual risks and out-of-scope

### Out of scope (per §1.2)

- Root compromise.
- `trusted-bootstrap` compromise.
- Compromise or malicious replacement of `ate-authority` or
  `ate-executor` service binaries or processes.
- Trusted service binary modification.
- Kernel/hardware compromise.
- TOCTOU between runtime attestation and action execution.
- Synchronous atomic revocation propagation once the executor has
  PREPARED a clearance (P1 uses the durable state machine +
  idempotent application model).

### Residual risks (in scope, documented)

- **Clearance-after-revocation ordering** — a clearance committed
  before its underlying decision is revoked remains valid until its
  `valid_until_unix_ms` bound. This is by design (see §8.3); it is
  not a bug. Mitigated by choosing short clearance TTLs.
- **Authority single-process writer** — the revocation-vs-clearance
  ordering guarantee depends on the authority service being a
  single-process SQLite writer. If the authority were to scale to
  multiple writers, this guarantee would need to be re-derived
  (e.g., via a global lock).
- **Sidecar race during service startup** — between the service
  process binding the socket and the directory ownership being
  applied. Mitigated by: the directory is owned by the service UID
  from creation (§5 step 2), so sidecars inherit ownership naturally.
- **Authority SQL injection via IPC payload** — mitigated by
  parameterized queries exclusively.
- **WAL growth without checkpoint** — authority and executor services
  run `PRAGMA wal_checkpoint(TRUNCATE)` periodically.
- **Resource exhaustion** — services enforce per-session allocation
  quotas; requester is rate-limited at the IPC layer.
- **Filesystem permissions drift** — T0 startup check verifies
  canonical mode/ownership and refuses to start if drift detected.
- **`ate-requester` group for IPC traversal** — the
  `ate-requester` group exists solely to allow traversal of
  `/run/ate/authority/` and `/run/ate/executor/`. It has NO write
  permission and NO read permission on privileged state. AT-28
  verifies this is the ONLY group the requester is in.

## 16. Acceptance criteria for v0.2 implementation (revision 2.1)

Implementation is authorized only after this design (revision 2.1)
receives implementation authorization. The implementation pass must:

1. Establish the four OS UIDs (ate-requester, ate-authority,
   ate-executor, trusted-bootstrap operator) and confirm
   `ate-requester` is in exactly ONE supplementary group
   (`ate-requester`) and has NO sudoers entry.
2. Confirm `ate-requester` cannot open any file under
   `/var/lib/ate/authority/`, `/var/lib/ate/executor/`, or
   `/var/lib/ate/resources/` — tested by AT-3..AT-11.
3. Confirm `ate-requester` cannot unlink/replace/rebind any socket
   under `/run/ate/authority/` or `/run/ate/executor/` — tested by
   AT-26.
4. Confirm `ate-requester` can `connect()` and `write()` to the
   authority and executor sockets — tested by T3.
5. Confirm `ate-executor` does NOT open `authority.sqlite` in any
   form and does NOT connect to `/run/ate/authority/authority.sock`
   — verified by code review AND by absence of group membership
   (executor is not in `ate-authority` group) AND by AT-40.
6. Confirm authority decisions and clearances are Ed25519-signed
   and executor verifies via `authority_pubkey.pem` — tested by
   AT-12, AT-13, AT-14.
7. Confirm `ate-executor` cannot manufacture a valid authority
   decision or clearance — tested by AT-14.
8. Confirm revocation-vs-clearance ordering behaves exactly as
   specified in §8.3 — tested by AT-18 and AT-19.
9. Confirm crash recovery across all three states (A, B, C) —
   tested by AT-22, AT-23, AT-24, and T6, T10.
10. Confirm idempotent resource application on `operation_id` —
    tested by AT-30, AT-37, AT-38 and the T6/T10 mutation_count
    invariants (exactly +1).
11. Confirm no inherited FDs, no env credentials, exact group set —
    tested by AT-27, AT-28, AT-29.
12. Confirm exactly-one-clearance-per-decision — tested by AT-34
    (repeated request returns same clearance), AT-35 (concurrent
    convergence), AT-36 (expired clearance cannot be replaced).
13. Confirm executor verifies requester UID binding against
    signed artifacts — tested by AT-39.
14. Confirm clearance acquisition path runs through the requester
    (executor does NOT contact authority) — tested by AT-40.
15. Run T0–T10 with 11/11 PASS.
16. Run AT-1..AT-40 with 40/40 PASS.
17. Generate evidence files under
    `architecture/experimental/ate-p1-enforcement-harness/evidence/p1_v020_evidence.json`
    and `p1_v020_test_log.txt`. Original `p1_v011_evidence.json` and
    `p1_v011_test_log.txt` remain byte-identical.
18. Confirm `ATE-P1-LOCAL-ENFORCEMENT-HARNESS-DESIGN-v0.1.md` and
    `ATE-P1-LOCAL-ENFORCEMENT-HARNESS-DESIGN-v0.1.1.md` unchanged.
19. Confirm frozen ATE v0.3.1 artifacts unchanged.

Final classification `ATE_P1_V0_2_LOCAL_ENFORCEMENT_ESTABLISHED` is
asserted only after all nineteen criteria are met.

## 17. Summary for adversarial review (revision 2.1)

v0.2 r2.1 makes the trust boundary a structural OS/process boundary
with the following properties:

- **Four distinct OS UIDs** (ate-requester, ate-authority,
  ate-executor, trusted-bootstrap operator) with no privileged-group
  overlap. The `ate-requester` UID is in exactly one supplementary
  group, solely for traversal of the per-service IPC subdirectories.
- **Split per-service IPC directories** (`/run/ate/authority/`,
  `/run/ate/executor/`) so the requester can traverse to reach the
  socket endpoints without write access to any directory.
- **Ed25519 signed decision envelopes** for authority authorization
  (NOT shared HMAC) bind authorization to a specific requester UID,
  payload, nonce, TTL, and `operation_id`. The executor verifies
  with the authority's PUBLIC key only.
- **Ed25519 signed execution CLEARANCE** (separate artifact) is
  what the executor accepts. Authority-internal SQLite
  `BEGIN IMMEDIATE` serialization guarantees the revocation-vs-
  clearance ordering (revoke-before-clearance denies; clearance-
  before-revoke remains valid per its tight TTL). This is the
  **controlling revocation guarantee** — no stale local cache is
  used as the basis.
- **Exactly one clearance per decision** (I8) is enforced by
  `UNIQUE(decision_id)` on `authority.sqlite.execution_clearances`.
  Repeated `get_execution_clearance` returns the persisted
  clearance. An expired clearance cannot be replaced under the
  same decision; a new authority decision is required.
- **Stable `operation_id`** bound into both the decision envelope
  and the clearance envelope (signed fields). It is deterministic
  given the decision contents, so a re-issued clearance under the
  same decision carries the same `operation_id`. The resource
  records `operation_id` (NOT `clearance_id`) for idempotency
  (I6, I16).
- **Clearance acquisition runs through the requester.** The
  executor NEVER connects to `ate-authority.sock`, NEVER opens
  `authority.sqlite`, and NEVER reads authority state (I15). All
  authority→executor communication flows through the requester's
  IPC submission to `executor.sock` carrying decision envelope +
  clearance envelope (both Ed25519-verified by the executor).
- **Executor durable state machine** (`executor.sqlite`): PREPARED
  → MUTATED → COMPLETED. The `PREPARED` transition COMMIT is the
  executor's durable linearization point (NOT `BEGIN IMMEDIATE`).
- **Idempotent resource mutation** keyed on `operation_id` (stable
  UUID recorded in resource's `applied_operation_ids`). Crash before
  mutation → recovery applies once. Crash after mutation → recovery
  reports `EX_ALREADY_APPLIED` and proceeds to COMPLETED. No
  duplicate mutation. P1 explicitly does NOT claim cross-store ACID
  atomicity.
- **PID is NOT a security invariant.** The requester principal is
  the OS UID (`SO_PEERCRED`-verified). PID is recyclable and
  therefore unsuitable as durable identity.
- **IPC namespace hardened**: split per-service subdirectories
  prevent socket unlink/replacement; SO_PEERCRED verifies client
  UID; Ed25519 signatures verify message provenance; service-to-
  service authentication does NOT rely on pathname possession.
- **No inherited FDs, no env credentials, exact group set** — all
  verified by AT-27, AT-28, AT-29.
- **11 controlling tests (T0–T10) + 40 attack tests (AT-1..AT-40)**
  exercise the boundary from every angle specified by the PI,
  including revocation ordering (AT-18, AT-19), idempotent mutation
  (AT-30, AT-37, AT-38), all three crash states (AT-22..AT-24),
  clearance manufacture refusal (AT-14), one-clearance-per-
  decision cardinality (AT-34..AT-36), requester-UID binding
  (AT-39), and executor's absence of authority access (AT-40).

---

**END OF v0.2 DESIGN REVISION 2.1. NO IMPLEMENTATION IN THIS ARTIFACT.**

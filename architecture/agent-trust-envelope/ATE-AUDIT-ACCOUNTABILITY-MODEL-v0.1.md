# ATE Audit & Accountability Model v0.1

## 1. Purpose

The ATE Audit & Accountability Model defines how trust decisions, authorization state changes, governed actions, denials, revocations, and execution outcomes become durable, attributable, reconstructable, and tamper-evident.

The audit system must answer, after the fact:

> Who requested the action, what evidence was used, what policy applied, who authorized it, what capability was granted, what actually happened, and can the record be trusted?

The model does not rely on the participant agent's own narrative of events.

---

## 2. Core Accountability Principle

Every consequential trust or execution transition must produce evidence external to the participant agent's authority boundary.

The required chain is:

```text
Request
  ↓
Evidence evaluation
  ↓
Trust decision
  ↓
Capability authorization
  ↓
Execution attempt
  ↓
Execution result
  ↓
Durable audit evidence
```

A successful action with no durable accountability evidence is an architectural defect for governed operations.

---

## 3. Security Objectives

The audit system SHALL support:

- attribution
- integrity
- ordering
- completeness detection
- forensic reconstruction
- non-repudiation within the limits of configured authority
- historical verification
- revocation history
- policy-state history
- execution outcome reconstruction
- independent verification

The audit system SHOULD minimize sensitive-data duplication and retain hashes or references where full payload retention is unnecessary.

---

## 4. Explicit Non-Goal

The audit ledger does not itself decide whether an action is authorized.

ATE decides.

The executor enforces.

The audit plane records and preserves what occurred.

A valid audit record must never substitute for authorization.

---

## 5. Audit Trust Boundary

Recommended logical separation:

```text
Participant Agent
      │
      ▼
ATE / Trust Authority
      │
      ▼
Capability Executor
      │
      ├────────────► Protected Resource
      │
      └────────────► Audit Service
                           │
                           ▼
                    Durable Ledger
```

The participant must not be able to rewrite or delete authoritative audit history.

---

## 6. Events Requiring Audit Records

At minimum, production ATE records:

```text
REQUEST_RECEIVED
EVIDENCE_VERIFICATION_STARTED
EVIDENCE_VERIFICATION_FAILED
EVIDENCE_VERIFICATION_SUCCEEDED
TRUST_GRANTED
TRUST_DENIED
CAPABILITY_ISSUED
NONCE_AUTHORIZED
NONCE_RESERVED
EXECUTION_STARTED
EXECUTION_SUCCEEDED
EXECUTION_FAILED_BEFORE_EFFECT
EXECUTION_EFFECT_UNKNOWN
EXECUTION_DENIED
REPLAY_REJECTED
REVOCATION_PUBLISHED
REVOCATION_OBSERVED
POLICY_ACTIVATED
POLICY_SUPERSEDED
TRUST_ROOT_UPDATED
KEY_ROTATED
KEY_SUSPENDED
KEY_REVOKED
HUMAN_APPROVAL_GRANTED
HUMAN_APPROVAL_DENIED
```

Not every deployment must use every event type, but every state transition affecting authority must be represented.

---

## 7. Canonical Audit Record

A minimum record:

```text
AuditRecord {
    audit_id
    event_type
    timestamp

    trust_domain
    tenant_id?

    actor_identity
    subject_identity?
    session_identity?

    request_id?
    envelope_id?
    verification_receipt_id?
    trust_decision_id?
    capability_token_id?
    execution_capability_id?

    operation?
    target?
    action_digest?

    policy_id?
    policy_version?
    policy_digest?

    coa_acceptance_id?
    behavioral_receipt_id?

    nonce?
    nonce_state_before?
    nonce_state_after?

    verdict?
    reason_code?
    execution_status?

    controlling_artifact_hashes[]

    trust_root_epoch
    revocation_epoch
    policy_epoch

    previous_record_hash
    record_hash

    recorder_identity
    recorder_key_id
    signature
}
```

Optional fields are present only when semantically relevant to the event type.

---

## 8. Canonical Encoding

All authoritative audit records must use one deterministic canonical encoding before hashing and signing.

Possible implementations include:

- canonical JSON
- deterministic CBOR
- deterministic protobuf

Production must select exactly one encoding profile.

Different components must not independently invent serialization rules.

---

## 9. Record Hash

Conceptually:

```text
record_hash = HASH(canonical_record_without_signature)
```

The hash algorithm must be explicitly versioned.

Example metadata:

```text
hash_algorithm = SHA-256
record_schema_version = 1
```

Unknown algorithms or schemas fail historical verification rather than being guessed.

---

## 10. Hash Chaining

Records form an append-only chain:

```text
Audit[n].previous_record_hash = Audit[n-1].record_hash
```

This makes modification, insertion, and deletion detectable from the point of tampering onward.

The first record for a ledger segment binds to a defined genesis value or checkpoint.

---

## 11. Sequence Numbers

Hash chaining alone is insufficient for detecting all operational anomalies.

Each ledger stream should also contain a monotonic sequence:

```text
ledger_sequence
```

Verification requires:

```text
sequence[n] = sequence[n-1] + 1
```

Missing sequence values indicate potential audit suppression or incomplete replication.

---

## 12. Ledger Streams

Production may use multiple streams, for example:

```text
trust-domain stream
executor stream
policy stream
revocation stream
security-administration stream
```

If multiple streams exist, critical records should periodically anchor into a common signed checkpoint to support global reconstruction.

---

## 13. Signed Records

Every authoritative record must be signed by an authorized audit recorder.

Validation requires:

```text
record signature valid
AND
recorder key recognized
AND
recorder authorized for event class
AND
recorder key valid at event time
```

Audit key possession alone does not confer arbitrary system authority.

---

## 14. Audit Recorder Authority

The Trust Root Registry should authorize which recorder may attest to which events.

Examples:

```text
ATE Verifier:
    EVIDENCE_VERIFICATION_*

Trust Decision Authority:
    TRUST_GRANTED
    TRUST_DENIED

Capability Executor:
    NONCE_RESERVED
    EXECUTION_*

Policy Authority:
    POLICY_ACTIVATED
    POLICY_SUPERSEDED

Revocation Authority:
    REVOCATION_PUBLISHED

Trust Root Authority:
    TRUST_ROOT_UPDATED
```

A participant agent must not be authoritative for executor or trust-decision events.

---

## 15. Audit Key Custody

Audit signing keys should be separate from participant identity keys and trust-decision keys.

Compromise of an audit key can permit false records but should not permit capability execution.

This separation limits blast radius.

Recommended custody level should follow the ATE Trust Root & Key Custody Model.

---

## 16. Append-Only Requirement

Authoritative history is append-only.

Corrections do not rewrite existing records.

Instead:

```text
original record
      ↓
CORRECTION / AMENDMENT record
      ↓
references original audit_id
```

The ledger preserves both what was originally recorded and the later correction.

---

## 17. Historical Truth vs Current Trust State

Audit records preserve historical facts even after trust state changes.

Example:

```text
09:00 TRUST_GRANTED under policy v7
09:05 EXECUTION_SUCCEEDED
10:00 authorization key REVOKED
```

The historical execution record remains valid evidence that the system granted and executed at 09:05 under the state known then.

Revocation must not erase history.

---

## 18. Epoch Binding

Every trust-critical record should capture current:

```text
trust_root_epoch
revocation_epoch
policy_epoch
```

This allows reconstruction of the authority state under which the event was evaluated.

Historical verification can then determine:

> Was this event valid according to the authoritative state at that time?

---

## 19. Decision Reconstruction

For every `TRUST_GRANTED` or `TRUST_DENIED`, the audit system must support reconstruction of:

- requested action
- subject/session identity
- Live Provenance reference
- COA acceptance reference
- VA policy triple
- behavioral evidence reference
- CapabilityToken reference
- gate results or VerificationReceipt
- reason code
- Trust Decision Authority
- signature
- relevant epochs

The full evidence need not be duplicated in every record if content-addressed artifacts are retained elsewhere.

---

## 20. Artifact References

Prefer cryptographic references:

```text
artifact_type
artifact_id
artifact_digest
artifact_location/reference
```

The digest is authoritative for integrity.

A mutable URL or file path alone is insufficient.

---

## 21. Content-Addressed Evidence Archive

ATE should maintain an evidence archive where immutable artifacts are addressed by digest.

Conceptually:

```text
sha256:<digest> → artifact bytes
```

Audit records reference the digest.

This reduces duplication while preserving reconstructability.

---

## 22. Sensitive Data Minimization

Auditability must not become uncontrolled data exfiltration.

Avoid storing unnecessary:

- prompt contents
- secrets
- credentials
- raw private data
- full email bodies
- entire files

Prefer:

```text
digest
classification
metadata
resource identifier
```

Store full content only when accountability requirements justify it.

---

## 23. Secret Handling

Secrets must never be written into audit records.

Audit may record:

```text
credential_reference_id
key_id
vault_lease_id
```

but not:

```text
API key
password
private key
bearer token
```

Sanitization occurs before record signing.

---

## 24. Execution Accountability

For an executed governed action, records must establish:

```text
which TrustDecision authorized it
which action digest was authorized
which executor performed it
which nonce was consumed
which external resource was targeted
what result was observed
```

This provides causal accountability from trust decision to effect.

---

## 25. External Result Evidence

Where possible, store cryptographic or stable references to external results.

Examples:

```text
Git commit SHA
GitHub merge SHA
email message ID
database transaction ID
cloud operation ID
file digest after write
```

This strengthens evidence that the claimed action actually occurred.

---

## 26. Unknown-Effect Accountability

If executor cannot determine whether the external effect occurred, the audit result must say so explicitly:

```text
EXECUTION_EFFECT_UNKNOWN
```

Never record this as success or failure by assumption.

The record should include enough external-operation context to support reconciliation.

---

## 27. Failed Action Accountability

A denied or failed action is still security-relevant.

Audit failed attempts including:

- unauthorized target
- replay
- expired decision
- revoked artifact
- malformed evidence
- direct bypass attempt
- policy downgrade attempt

Repeated denials may indicate attack activity.

---

## 28. Audit Completeness

A trustworthy ledger requires detection of missing expected records.

Examples:

```text
TRUST_GRANTED
without subsequent executor disposition
```

or:

```text
NONCE_RESERVED
without final state
```

These should create reconciliation alerts.

---

## 29. Required Event Pairings

Examples of expected causal relationships:

```text
REQUEST_RECEIVED
→ TRUST_GRANTED or TRUST_DENIED
```

If granted:

```text
TRUST_GRANTED
→ NONCE_RESERVED or EXECUTION_DENIED
```

If reserved:

```text
NONCE_RESERVED
→ EXECUTION_SUCCEEDED
   OR EXECUTION_FAILED_BEFORE_EFFECT
   OR EXECUTION_EFFECT_UNKNOWN
```

Missing terminal transitions are anomalies.

---

## 30. Audit Reconciliation

A reconciliation process should periodically verify:

- hash chain continuity
- signatures
- sequence continuity
- expected causal event pairs
- artifact availability
- nonce state consistency
- external-operation references
- epoch consistency

Reconciliation should not mutate historical records.

It emits new anomaly or reconciliation records.

---

## 31. Independent Audit Sink

Higher-assurance deployments should replicate signed records to an independent sink outside the executor's administrative boundary.

Example:

```text
Executor
  ├─► local ledger
  └─► independent audit service
```

This improves resistance to local deletion or suppression.

---

## 32. Checkpoints

Periodically issue signed ledger checkpoints:

```text
LedgerCheckpoint {
    ledger_id
    sequence
    head_record_hash
    timestamp
    recorder
    signature
}
```

Checkpoints may be copied to independent storage.

They provide compact proof of ledger history up to a point.

---

## 33. Merkle Aggregation

At larger scale, audit segments may be summarized using Merkle trees.

This permits efficient proof that a record existed in a signed interval without reproducing the whole ledger.

This is optional for v0.1 and not required for initial production use.

---

## 34. Audit Availability Policy

Audit availability requirements should depend on action risk.

Example:

```text
R0-R1:
    local durable audit acceptable

R2:
    audit commit required before final action completion

R3-R4:
    independent audit sink/checkpoint required
```

The policy must be explicit.

---

## 35. Audit Failure Behavior

For governed actions requiring mandatory audit:

```text
cannot persist required audit evidence
→ NO EXECUTION
```

Fail closed.

Audit failure must never silently degrade into unlogged execution.

---

## 36. Pre-Execution Audit

For higher-risk actions, a pre-execution record may be committed after nonce reservation but before external effect:

```text
NONCE_RESERVED
EXECUTION_STARTED
```

This ensures evidence exists even if the executor crashes during the external action.

---

## 37. Post-Execution Audit

After external operation:

```text
EXECUTION_SUCCEEDED
```

or another terminal status is committed with external result evidence.

The executor must distinguish audit success from external-operation success.

---

## 38. Crash Recovery

After restart, the audit ledger helps recover incomplete executions.

Search for nonterminal states such as:

```text
NONCE_RESERVED
EXECUTION_STARTED
```

without a corresponding terminal event.

These require reconciliation before reuse or retry.

---

## 39. Human Approval Accountability

Human approvals must be attributable independently of the participant agent.

Audit records should capture:

```text
approval_id
human_authority_id
action_digest
decision
timestamp
authentication_method reference
```

Do not store unnecessary authentication secrets.

---

## 40. Administrative Accountability

Administrative operations are themselves governed events.

Audit at minimum:

- adding/removing trust roots
- changing authority roles
- rotating keys
- changing risk classes
- changing minimum protocol versions
- publishing revocations
- activating policies
- modifying executor configuration

Administrative power without audit creates an accountability gap.

---

## 41. Trust Root Change Records

Every Trust Root Registry update must record:

```text
old_registry_digest
new_registry_digest
old_epoch
new_epoch
change_authority
change_reason
```

The update must be signed according to root-governance policy.

---

## 42. Key Lifecycle Records

Key lifecycle events include:

```text
KEY_CREATED
KEY_ACTIVATED
KEY_ROTATED
KEY_SUSPENDED
KEY_REVOKED
KEY_DESTROYED
```

Historical records retain the key ID and status transitions needed for temporal verification.

---

## 43. Revocation Accountability

Revocation events should record:

```text
revoked_artifact/key
revocation_reason
effective_time
revocation_authority
new revocation_epoch
```

Historical verification must distinguish events before and after effective revocation.

---

## 44. Policy Accountability

Policy records should establish:

```text
policy_id
version
digest
activation time
supersession time
policy authority
```

This prevents later ambiguity over which policy controlled a decision.

---

## 45. Attribution Levels

ATE should distinguish attribution strengths.

### A0 — Process attribution

Record identifies a software process/service.

### A1 — Cryptographic service attribution

Record signed by service key.

### A2 — Protected workload attribution

Service identity backed by stronger workload isolation.

### A3 — Human/legal attribution

Action additionally bound to authenticated human authority.

Do not overclaim attribution beyond deployed controls.

---

## 46. Non-Repudiation Limits

A digital signature establishes use of a private key, not necessarily the intent of a human or correctness of a model.

Therefore audit claims should say:

> Key K signed artifact X under authority role R.

not automatically:

> Human H personally intended X.

The latter requires additional authenticated human-approval evidence.

---

## 47. Clock and Ordering Trust

Audit timestamps depend on trusted time.

For session-local ordering, monotonic sequence numbers are stronger than wall-clock time.

Use both where possible:

```text
timestamp
ledger_sequence
```

High-assurance environments may require authenticated time sources.

---

## 48. Multi-Node Ordering

Distributed systems cannot assume a single perfect global clock.

Cross-node ordering should rely on:

- causal references
- signed local sequences
- checkpoints
- external transaction IDs

Avoid unsupported claims of total ordering when only partial ordering is known.

---

## 49. Audit Query Model

The audit system should support reconstruction by:

- trust_decision_id
- request_id
- session_identity
- subject_identity
- capability_token_id
- nonce
- action digest
- policy digest
- key ID
- time range

This makes incident response practical.

---

## 50. Forensic Reconstruction Procedure

For a governed action:

1. locate terminal execution record;
2. verify audit signature;
3. verify hash-chain continuity;
4. retrieve TrustDecision;
5. verify TrustDecision signature and authority;
6. retrieve VerificationReceipt/evidence references;
7. reconstruct policy, revocation, and trust-root epochs;
8. verify CapabilityToken and scope;
9. verify nonce lifecycle;
10. compare external-result evidence;
11. determine whether action complied with controls active at execution time.

This should be possible without trusting the participant's memory or transcript.

---

## 51. Audit Integrity Verification

A verifier should be able to produce:

```text
AUDIT_CHAIN_VALID
AUDIT_CHAIN_BROKEN
AUDIT_RECORD_INVALID
AUDIT_RECORD_MISSING_DEPENDENCY
AUDIT_STATE_INCONSISTENT
```

Audit anomalies do not rewrite the ledger.

They generate additional findings.

---

## 52. Audit Tampering Threats

Threats include:

- modifying records
- deleting records
- inserting fabricated records
- truncating ledger tail
- suppressing new records
- replaying old checkpoints
- stealing audit signing key

Controls include hash chains, sequence numbers, signatures, epochs, independent checkpoints, and replicated sinks.

---

## 53. Tail Truncation

A local attacker may delete all records after a previously valid checkpoint.

Mitigation:

- external checkpoint replication
- expected heartbeat/checkpoint cadence
- independent audit sink

A hash chain alone cannot prove that an unseen tail once existed.

---

## 54. Audit Suppression

An attacker may prevent records from being created rather than modifying them.

For mandatory-audit capabilities, execution must require successful precondition that audit infrastructure is writable.

Security principle:

```text
mandatory audit unavailable
→ capability unavailable
```

---

## 55. Audit Signing Key Compromise

Compromise permits fabricated audit records.

It must not permit execution or trust grants if authority roles are separated correctly.

Response:

- revoke audit key
- increment relevant trust-root/revocation epochs
- activate replacement key
- mark affected time window for enhanced review
- preserve all historical records

---

## 56. Retention

Retention depends on risk and accountability requirements.

A conceptual policy:

```text
R0: short retention
R1-R2: operational retention
R3: long-term forensic retention
R4: regulatory/critical retention
```

Exact durations are deployment-specific.

---

## 57. Evidence Garbage Collection

Evidence artifacts may be deleted only when no retained audit record requires them for reconstruction, or when policy explicitly permits digest-only retention.

Deletion itself may require an audit event.

---

## 58. Privacy and Access Control

Audit records can expose sensitive metadata.

Access should be role-scoped:

```text
operator
security investigator
auditor
compliance authority
system service
```

Read access to the ledger is not necessarily universal.

---

## 59. Audit Export

Exports should preserve:

- canonical records
- signatures
- hash-chain context
- checkpoints
- referenced artifact digests

A human-readable report alone is not sufficient evidence.

---

## 60. Independent Verification

A third-party verifier should be able to validate an exported audit segment without access to private signing keys.

Required inputs include:

- public authority records
- trust-root history
- revocation history
- canonicalization rules
- audit records/checkpoints

This supports external review and federation later.

---

## 61. Accountability Reason Codes

Audit findings should use machine-readable codes such as:

```text
AUDIT_OK
AUDIT_HASH_MISMATCH
AUDIT_SIGNATURE_INVALID
AUDIT_SEQUENCE_GAP
AUDIT_CHECKPOINT_STALE
AUDIT_ARTIFACT_MISSING
AUDIT_NONCE_INCONSISTENT
AUDIT_EXECUTION_ORPHANED
AUDIT_TRUST_DECISION_ORPHANED
AUDIT_EPOCH_MISMATCH
AUDIT_RECORDER_UNAUTHORIZED
```

Reason codes should be stable and versioned.

---

## 62. Accountability Invariants

### INV-A1

Every governed execution has exactly one controlling TrustDecision.

### INV-A2

Every controlling TrustDecision is auditable.

### INV-A3

Every nonce transition affecting executability is auditable.

### INV-A4

Historical records are append-only.

### INV-A5

Corrections create new records rather than rewriting history.

### INV-A6

Audit recorder authority is independently verifiable.

### INV-A7

Secrets are never persisted in authoritative audit records.

### INV-A8

Missing mandatory audit capability prevents governed execution.

### INV-A9

Ledger gaps are detectable.

### INV-A10

A later revocation changes current trust state but does not erase historical events.

---

## 63. Accountability vs Observability

Operational logs and ATE audit records are different.

Observability logs may be:

- verbose
- transient
- mutable
- implementation-specific

ATE audit records are:

- security-relevant
- canonical
- signed
- append-only
- retained according to accountability policy

Do not treat ordinary application logs as the authoritative audit ledger.

---

## 64. Accountability vs Memory

Agent memory, transcripts, or conversational history may provide useful context but are not authoritative security evidence.

ATE accountability must survive:

- agent restart
- conversation deletion
- model changes
- transcript corruption

The ledger exists outside those mechanisms.

---

## 65. Production Profiles

### P0 — Development

```text
local append-only file
hash chain
software audit key
```

### P1 — Standard

```text
durable database/object storage
signatures
sequence numbers
periodic checkpoints
```

### P2 — High Assurance

```text
independent audit sink
protected audit signing key
frequent checkpoints
security monitoring
```

### P3 — Critical

```text
multiple independent audit replicas
hardware-backed signing
externally anchored checkpoints
strict retention/governance
```

---

## 66. Minimal Future Audit PoC

If later testing is justified, a local zero-model-call PoC could demonstrate:

### A1 — Valid chain

Create request → grant → reserve → execute → consume records.

Expected: full chain validates.

### A2 — Record modification

Modify an earlier record.

Expected: hash/signature validation fails.

### A3 — Record deletion

Remove an interior record.

Expected: sequence/hash-chain gap detected.

### A4 — Correction

Append correction record.

Expected: original remains intact; correction linked.

No Hermes/model call is required.

---

## 67. What Such a PoC Would Prove

It would establish that ATE security events can be recorded in a tamper-evident, append-only structure whose internal integrity and causal references can be verified independently.

It would not prove resistance to total host compromise or audit-key theft.

---

## 68. Relationship to Trust Root & Key Custody

Audit validity depends on knowing whether the recorder key was authorized at event time.

Therefore historical audit verification uses trust-root and key-lifecycle history rather than only current key state.

---

## 69. Relationship to Revocation

Audit preserves both:

```text
artifact valid at time T
```

and later:

```text
artifact revoked at time T+1
```

Current execution decisions use current trust state.

Historical accountability uses temporal state.

---

## 70. Relationship to Enforcement Plane

The executor is the authoritative source for actual execution state.

The participant may request or describe an action, but only executor records can authoritatively attest that a governed operation was attempted or completed through the enforcement plane.

---

## 71. Architectural Conclusion

ATE accountability should make every important trust decision and governed action reconstructable without trusting the participant's story about what happened.

The production rule is:

> **Every grant must leave evidence. Every execution must leave evidence. Every change in authority must leave evidence. History is amended, never rewritten.**

Combined with the Trust Root, Revocation, and Enforcement models, this creates a chain from authority to decision to capability to effect to durable accountability.

# ATE Enforcement Plane v0.1

## 1. Purpose

The ATE Enforcement Plane defines how a valid Agent Trust Envelope decision becomes real, constrained execution authority.

The central requirement is:

> A governed resource must not be directly accessible to the participant agent.

The participant may request an action. ATE may evaluate that request. Only the Capability Executor may hold the credentials or operating authority required to perform the governed action.

The enforcement plane therefore converts `TRUST_GRANTED` into one narrowly scoped executable capability and `TRUST_DENIED` into no execution path.

## 2. Core Enforcement Principle

ATE is not complete if it merely recommends whether an action should occur.

Production ATE requires:

> **Trust decisions must control capability possession.**

The architecture must prevent direct Agent → Protected Resource access and require Agent → ATE → Capability Executor → Protected Resource.

## 3. Security Invariants

- INV-E1: If there is no valid `TRUST_GRANTED` for the exact requested action, the protected resource must be unreachable through the governed execution path.
- INV-E2: The participant agent cannot obtain the executor's resource credentials.
- INV-E3: The executor may exercise only the capability encoded in the authorized action.
- INV-E4: Authorization is single-use unless explicitly designed otherwise.
- INV-E5: Action parameters cannot change after trust approval.
- INV-E6: Nonce reservation must prevent concurrent replay.
- INV-E7: Every attempted execution produces audit evidence.
- INV-E8: An execution error must never widen authority.
- INV-E9: Unknown execution outcome must not trigger blind retry.
- INV-E10: TrustDecision verification occurs inside the executor boundary.

## 4. Components

The enforcement plane contains five logical components:

1. Request Gateway
2. Capability Executor
3. Credential Vault
4. Resource Adapter
5. Execution Audit Interface

Supporting services include the ATE Verifier, Trust Decision Authority, Nonce Registry, Revocation Service, and Policy Authority.

## 5. High-Level Dataflow

```text
                    ┌──────────────────┐
                    │ Participant Agent │
                    └────────┬─────────┘
                             │
                       Action Request
                             │
                             ▼
                    ┌──────────────────┐
                    │ Request Gateway  │
                    └────────┬─────────┘
                             │
                             ▼
                    ┌──────────────────┐
                    │ ATE Verification │
                    └────────┬─────────┘
                             │
                   signed TrustDecision
                             │
                             ▼
                    ┌──────────────────┐
                    │ Capability       │
                    │ Executor         │
                    └───────┬──────────┘
                            │
              ┌─────────────┼─────────────┐
              │             │             │
              ▼             ▼             ▼
       Nonce Registry   Credential Vault  Audit Ledger
              │             │
              └──────┬──────┘
                     │
                     ▼
              ┌───────────────┐
              │Resource Adapter│
              └───────┬───────┘
                      │
                      ▼
              ┌───────────────┐
              │Protected       │
              │Resource        │
              └───────────────┘
```

## 6. Request Gateway

The Request Gateway receives proposed governed actions from the participant agent and performs structural validation and canonicalization. It does not execute them or grant capability.

```text
ExecutionRequest {
    request_id
    subject_identity
    session_identity
    operation
    target
    parameters
    requested_at
}
```

Responsibilities include artifact-size validation, operation validation, canonical target and parameter resolution, computation of the requested-action digest, and forwarding of the canonical request to ATE.

## 7. Canonical Action Representation

Authorization must apply to exactly one canonical action.

```text
CanonicalAction {
    operation: "WRITE_FILE"
    target: "filesystem:/srv/project/report.md"
    parameters_digest: SHA256(...)
}
```

Canonicalization must occur before authorization to prevent path and alias substitution.

## 8. Capability Executor

The Capability Executor is the only component allowed to convert a valid TrustDecision into a real resource operation. It is a security boundary.

Inputs include TrustDecision, CanonicalAction, CapabilityToken, and ATE envelope reference.

Before accessing any resource credential, the executor verifies:

1. TrustDecision signature
2. TrustDecision issuer authorization
3. verdict == `TRUST_GRANTED`
4. decision freshness
5. decision not revoked
6. envelope binding
7. session binding
8. subject binding
9. CapabilityToken binding
10. exact action digest
11. nonce state
12. resource-adapter policy

Any failure results in no credential access.

## 9. Credential Vault

The Credential Vault stores secrets required to operate governed resources, such as filesystem service identity, database credentials, GitHub tokens, email API credentials, deployment keys, or cloud credentials.

The participant agent must not possess these credentials. Credentials are retrievable only by the Capability Executor or a tightly scoped Resource Adapter.

## 10. Credential Scope

Where practical, credentials themselves should be scoped. Short-lived, resource-specific, action-class credentials are preferred over universal or root credentials.

ATE should use native resource authorization where available rather than relying solely on software checks.

## 11. Resource Adapter

A Resource Adapter translates canonical ATE operations into concrete external-system calls, such as FilesystemAdapter, GitHubAdapter, EmailAdapter, DatabaseAdapter, or CloudAdapter.

Each adapter knows how to enforce resource-specific semantics.

## 12. Adapter Security Rule

The adapter must independently validate that the concrete operation remains within authorized scope. It must not trust participant-supplied interpretation or path/resource resolution.

## 13. Capability Representation

The executor should receive a narrow execution capability derived from the TrustDecision.

```text
ExecutionCapability {
    capability_id
    trust_decision_id
    operation
    target
    parameters_digest
    subject_identity
    session_identity
    issued_at
    expires_at
    nonce
    issuer
    signature
}
```

## 14. Capability Scope Rule

Execution is permitted only if actual operation, target, and parameters digest exactly match authorization. Approximate or inferred matching is not permitted.

## 15. Credential Release Rule

Resource credentials must not be loaded before authorization succeeds.

Desired sequence:

```text
verify decision
verify scope
reserve nonce
obtain credential
perform action
```

## 16. Nonce State Machine

Recommended states:

```text
UNSEEN
AUTHORIZED
RESERVED
CONSUMED
FAILED_BEFORE_EFFECT
UNKNOWN_EFFECT
```

Representative transitions:

```text
UNSEEN → AUTHORIZED → RESERVED
                          ├─→ CONSUMED
                          ├─→ FAILED_BEFORE_EFFECT
                          └─→ UNKNOWN_EFFECT
```

No state transitions back to `AUTHORIZED`.

## 17. Atomic Reservation

Before execution, `AUTHORIZED → RESERVED` must be atomic using compare-and-set or equivalent transactional semantics. Only one execution attempt may reserve the nonce.

## 18. Replay Prevention

If nonce is `RESERVED`, `CONSUMED`, `FAILED_BEFORE_EFFECT`, or `UNKNOWN_EFFECT`, another execution request must not proceed automatically.

## 19. Execution Outcome States

The executor must distinguish:

- `CONSUMED`: external effect confirmed.
- `FAILED_BEFORE_EFFECT`: executor knows the external action did not occur.
- `UNKNOWN_EFFECT`: executor cannot determine whether the external action occurred.

## 20. Unknown-Effect Rule

If execution outcome is uncertain, do not automatically retry. `UNKNOWN_EFFECT` requires human/operator resolution or resource-specific reconciliation.

## 21. Idempotency

Where supported, derive an idempotency key from `trust_decision_id` and action digest so the same trust decision cannot generate multiple external effects.

## 22. External Resource Requirements

For strong enforcement, protected resources should authenticate the executor rather than the agent. If the participant has equivalent direct credentials, executor bypass remains possible.

## 23. Filesystem Example

For an authorized `WRITE_FILE filesystem:/srv/project/report.md`, the executor verifies TrustDecision, reserves nonce, resolves canonical path, checks exact target, obtains write capability, performs write, verifies result, marks nonce consumed, and writes audit evidence. The agent never receives unrestricted filesystem write authority.

## 24. Email Example

For `SEND_EMAIL`, TrustDecision should bind exact recipient, subject digest, body digest, and attachment digests. The participant must not modify message content after authorization.

## 25. GitHub Example

For `MERGE_PULL_REQUEST`, authorization should constrain repository, operation, PR number, and potentially current head commit SHA. The executor uses a GitHub credential inaccessible to the participant and revalidates mutable resource state immediately before execution.

## 26. Time-of-Check / Time-of-Use Threat

Authorization may be correct at decision time but invalid at execution time. Mutable targets should bind a `resource_state_digest` or equivalent version identifier. If state changes, execution is denied and a new trust decision is required.

## 27. TOCTOU Policy

For mutable targets, TrustDecision should bind resource state where relevant. Examples include a Git commit SHA, database row version, object ETag, or deployment revision.

## 28. Revocation Recheck

The executor should perform a final revocation check immediately before high-impact execution, narrowing the revocation race window.

## 29. Expiration Recheck

The executor must independently verify TrustDecision expiration. No implicit grace period.

## 30. Policy Recheck

For high-risk operations, the executor may compare the decision's policy digest to the current active policy immediately before execution. Policy change can require a new trust decision.

## 31. Audit Coupling

Every execution attempt should produce audit events such as `REQUEST_RECEIVED`, `TRUST_DENIED`, `TRUST_GRANTED`, `NONCE_RESERVED`, `EXECUTION_STARTED`, `EXECUTION_SUCCEEDED`, `EXECUTION_FAILED_BEFORE_EFFECT`, `EXECUTION_EFFECT_UNKNOWN`, `REPLAY_REJECTED`, and `REVOCATION_REJECTED`.

## 32. Audit Record

```text
ExecutionAuditRecord {
    audit_id
    previous_record_hash
    timestamp
    request_id
    trust_decision_id
    execution_capability_id
    subject_identity
    session_identity
    operation
    target
    parameters_digest
    nonce
    nonce_state_before
    nonce_state_after
    decision
    execution_status
    external_result_digest
    executor_identity
    signature
}
```

## 33. Audit Failure

For high-risk action classes, inability to record audit evidence should block execution. Audit requirements should be explicit by risk class.

## 34. Human Approval Integration

Some capability classes should require human approval even after ATE verification. Human approval should bind human authority identity, action digest, decision, issuance time, and expiration through an authentication path inaccessible to the participant agent.

## 35. Risk Classes

Suggested classes:

- R0 — informational
- R1 — low impact
- R2 — moderate
- R3 — high
- R4 — critical

Examples range from public reads through private reads and project writes to protected merges, infrastructure changes, financial transfers, or safety-impacting actions.

## 36. Enforcement by Risk

Possible progression:

- R0: standard verification
- R1: standard ATE + audit
- R2: ATE + short-lived decision + executor isolation
- R3: ATE + revocation recheck + human approval or second authority
- R4: ATE + multi-party authorization + hardened key custody + isolated executor

## 37. Executor Isolation

Minimum separation: participant process calls separate executor process. Better: participant host calls authenticated executor service. Higher assurance: isolated enforcement service with hardware-backed credentials.

## 38. Same-Host PoC Limitation

A same-host executor can demonstrate logical enforcement but not strong protection against host-root compromise. This must remain an explicit non-claim.

## 39. Executor API

A minimal executor API could accept a TrustDecision and CanonicalAction. It must not accept participant-supplied resource credentials, authorization overrides, bypass flags, or trust-validation disablement.

## 40. Forbidden Executor Features

Participant-accessible interfaces must not expose unchecked execution, trust-validation skipping, `force=true`, agent-controlled admin override, nonce bypass, or policy bypass.

## 41. Fail-Closed Error Handling

Any signature parser failure, registry outage, revocation-service outage, nonce-store outage, credential-vault outage, policy mismatch, or unexpected exception results in no execution.

## 42. Dependency Failure Policy

For security-critical dependencies, `UNKNOWN != SAFE`. If revocation status cannot be determined for a high-risk action, execution is denied.

## 43. Credential Vault Failure

Credential retrieval failure should leave the nonce in a state that accurately reflects certainty about external effect. Automatic retry must depend on explicit state, not assumption.

## 44. Crash Recovery

Executor crash recovery must inspect durable nonce and execution state. A crash after reservation but before known completion may require `RESERVED_STALE` or `UNKNOWN_EFFECT` and operator reconciliation.

## 45. Durable State

Production nonce and execution state must be durable. Minimum durable data includes nonce, TrustDecision id, reservation timestamp, action digest, execution state, and any external operation id.

## 46. External Operation IDs

Persist external operation identifiers such as email message id, merge commit SHA, cloud operation id, or database transaction id to resolve uncertain outcomes.

## 47. Least Privilege Inside Executor

The executor itself should avoid universal credentials. Resource-specific roles, GitHub App installation tokens, scoped IAM roles, and short-lived credentials reduce impact if the executor is compromised.

## 48. Capability Segmentation

High-risk environments may separate ReadExecutor, FilesystemWriteExecutor, GitHubExecutor, EmailExecutor, InfrastructureExecutor, and FinancialExecutor so compromise of one capability class does not expose all others.

## 49. Resource Adapter Allowlisting

Each executor should support an explicit operation allowlist. Unsupported operations fail closed.

## 50. Shell Execution

Generic shell execution is unusually dangerous because it collapses many capabilities into one. Production default should disable generic shell execution and prefer typed capabilities.

## 51. Typed Capability Principle

Prefer `SEND_EMAIL`, `WRITE_FILE`, `MERGE_PULL_REQUEST`, `QUERY_DATABASE`, and `CREATE_TICKET` over generic `RUN_COMMAND`.

Typed operations are easier to scope, audit, and enforce.

## 52. Network Egress

If an agent has unrestricted network access, it may bypass governed APIs. Production may require agent network policy that denies governed destinations while allowing the executor to reach them.

## 53. Filesystem Access

ATE filesystem mediation is meaningless if the agent already has direct write permission to protected directories. OS permissions must align with ATE policy.

## 54. Database Access

Participants should not possess direct protected database mutation credentials. Prefer a DatabaseExecutor using scoped database roles.

## 55. Cloud Access

Avoid general cloud credentials in participant runtimes. Prefer workload identity, short-lived tokens, narrowly scoped IAM roles, and per-executor service identities.

## 56. Secrets Access

Secrets themselves should be governed capabilities, for example `READ_SECRET target: secret://project/api-key`, rather than exposing an entire secret store.

## 57. Executor Identity

Credential Vault and external resources should authenticate executor identity using service certificates, workload identity, platform identity, or hardware-backed identity depending on deployment assurance.

## 58. Trust Decision Authority vs Executor

Keep decision and enforcement as distinct roles. The Trust Authority decides; the Executor enforces.

## 59. Executor Must Reverify

The executor must not blindly trust an upstream statement that ATE already checked a request. It independently verifies TrustDecision signature and critical bindings.

## 60. Minimal Reverification Set

At minimum verify TrustDecision signature, authorized issuer, `TRUST_GRANTED`, expiration, revocation, action digest, nonce, subject, and session.

## 61. Verification Receipt

A future ATE Verifier may emit a signed VerificationReceipt containing envelope hash, gate results, verifier identity, and issuance time. The Trust Decision Authority can bind this receipt.

## 62. Production Execution Chain

```text
Canonical Request
      ↓
ATE Evidence Verification
      ↓
VerificationReceipt
      ↓
Trust Decision Authority
      ↓
Signed TRUST_GRANTED
      ↓
Executor Reverification
      ↓
Nonce Reservation
      ↓
Credential Acquisition
      ↓
Resource-Specific Validation
      ↓
External Action
      ↓
Outcome Confirmation
      ↓
Nonce Finalization
      ↓
Audit Commit
```

## 63. Minimal Prototype Scope

A future enforcement PoC should start with a sandboxed filesystem capability rather than GitHub, email, or cloud infrastructure.

Example:

```text
Allowed:
WRITE_FILE
sandbox:/authorized/report.txt

Denied:
anything outside sandbox:/authorized/
```

This can demonstrate executor-only credentials, exact target binding, nonce reservation, one-time execution, replay denial, TOCTOU checks, and audit chaining without external subscriptions.

## 64. Suggested Enforcement PoC Cases

When experimentation resumes, a small local matrix is sufficient:

- E1: valid execution → exactly one write and nonce consumed.
- E2: direct bypass attempt → OS/access-control denied.
- E3: scope substitution/path traversal → executor denied.
- E4: concurrent replay → exactly one reservation succeeds.

These can likely be tested locally with no premium model calls.

## 65. What the Future Enforcement PoC Would Prove

If successful:

> The participant cannot exercise a governed capability directly, and the Capability Executor will exercise it only when presented with a valid, current, exact, single-use ATE authorization.

## 66. What It Would Not Prove

It would not establish resistance to root compromise, hardware-backed isolation, safe financial execution, federation, production revocation infrastructure, secure cloud deployment, general protection against arbitrary code execution, or universal correctness of Resource Adapters.

## 67. Production Deployment Profiles

Possible assurance profiles:

- P0 Development: same-host, software keys, local executor, sandbox resources.
- P1 Standard: separate executor service/process, protected credentials, durable nonce state, revocation, audit ledger.
- P2 High Assurance: isolated executor host, hardware-backed authority keys, short-lived credentials, human approval for high-risk actions, independent audit sink.
- P3 Critical: multiple authorities, threshold authorization, hardware-backed execution identity, strict network isolation, external monitoring, human confirmation.

## 68. Recommended Immediate Architecture Decisions

Adopt these decisions before enforcement implementation:

1. Participant agent never directly possesses governed resource credentials.
2. ATE authorization is single-action and single-use.
3. Nonce reservation is atomic and durable.
4. Executor independently verifies signed TrustDecision.
5. Canonical action parameters are fixed before trust evaluation.
6. Mutable resource state is rebound immediately before execution where relevant.
7. Unknown external effect blocks automatic retry.
8. Resource-specific typed adapters are preferred over generic shell execution.
9. Executor actions are always auditable.
10. Direct resource access is denied independently of agent cooperation.

## 69. Architectural Conclusion

The Agent Trust Envelope becomes meaningful in production only when authorization controls real capability.

Required relationship:

```text
Evidence
   ↓
Trust Decision
   ↓
Capability
   ↓
Execution
```

not:

```text
Evidence
   ↓
Recommendation
   ↓
Agent chooses whether to comply
```

The production enforcement principle is:

> **ATE decides whether capability may exist; the enforcement plane ensures capability cannot exist otherwise.**

A concise version is:

> **No trust grant, no capability. No capability, no action.**

# ATE Revocation & Trust-State Model v0.1

## 1. Purpose

This document defines how the Agent Trust Envelope (ATE) determines whether previously valid identities, policies, evidence, authorizations, keys, sessions, trust decisions, and execution rights remain valid now.

The core production requirement is:

> Trust state must be current, not merely historically valid.

ATE therefore treats revocation as a first-class control plane rather than an optional metadata flag.

A valid signature, valid historical policy, or previously accepted trust decision does not imply present authorization.

---

## 2. Core Principle

ATE distinguishes two questions:

1. **Was this artifact valid when issued?**
2. **Is this artifact still valid for use now?**

Production trust requires both answers to be yes.

Formally:

```text
usable_now(artifact) =
    cryptographically_valid
    AND issuer_authorized
    AND temporally_valid
    AND policy_current
    AND not_revoked
    AND context_binding_valid
```

Failure of any term results in denial or non-executability.

---

## 3. Scope

This model covers revocation and current-state semantics for:

- Trust Root Registry entries
- authority signing keys
- agent/runtime identities
- sessions
- COA acceptance receipts
- Value Architecture policies
- BehavioralEvidenceReceipts
- CapabilityTokens
- TrustDecisions
- execution capabilities
- nonce/execution state
- verifier identities
- executor identities
- audit signing identities

It also defines propagation, precedence, revocation epochs, dependency invalidation, and historical audit treatment.

---

## 4. Non-Goals

Version 0.1 does not define:

- global Internet-scale certificate revocation infrastructure
- OCSP or CRL compatibility profiles
- blockchain-based revocation
- production database technology
- quorum consensus protocol
- multi-region consistency implementation
- hardware attestation revocation
- cross-organization federation protocol

Those may be layered onto this model later.

---

## 5. Trust-State Categories

Every security-relevant artifact has a current trust state.

Minimum states:

```text
ACTIVE
SUSPENDED
REVOKED
EXPIRED
SUPERSEDED
UNKNOWN
```

### ACTIVE

Artifact may participate in a trust decision if all other checks pass.

### SUSPENDED

Artifact is temporarily unusable pending investigation or administrative action.

### REVOKED

Artifact is explicitly invalidated and must not be used for new trust decisions or executions.

### EXPIRED

Artifact exceeded its validity interval.

### SUPERSEDED

Artifact has been replaced by a newer authoritative artifact and is no longer current for new authorization.

### UNKNOWN

Current state cannot be determined reliably.

Security rule:

```text
UNKNOWN != ACTIVE
```

For governed execution, unknown state fails closed.

---

## 6. Revocation vs Expiration vs Supersession

These mechanisms are distinct.

### Expiration

Planned end of validity.

Example:

```text
CapabilityToken expires at 14:00 UTC
```

### Revocation

Early invalidation due to changed trust conditions.

Example:

```text
Authorization key compromised at 13:12 UTC
```

### Supersession

Artifact remains historically authentic but is no longer the currently authoritative version.

Example:

```text
VA policy v7 replaced by v8
```

ATE must not collapse these into one generic invalid flag because their audit and recovery semantics differ.

---

## 7. Revocable Object Model

Every revocable artifact should expose a stable identifier.

Examples:

```text
key_id
identity_id
session_id
coa_acceptance_id
policy_id + policy_version + policy_digest
behavioral_receipt_id
capability_token_id
trust_decision_id
execution_capability_id
```

Revocation must target immutable identity, not mutable display names.

---

## 8. RevocationRecord

Canonical conceptual structure:

```text
RevocationRecord {
    revocation_id

    target_type
    target_id
    target_digest_optional

    status

    effective_at
    issued_at

    reason_code
    reason_detail_optional

    issuer_authority_id
    issuer_key_id

    trust_domain
    registry_epoch

    signature
}
```

`status` may include:

```text
SUSPENDED
REVOKED
REINSTATED
```

Reinstatement is permitted only where policy explicitly allows it.

Some object classes should never be reinstated after compromise.

---

## 9. Revocation Reason Codes

Minimum reason taxonomy:

```text
RV_KEY_COMPROMISE
RV_AUTHORITY_COMPROMISE
RV_AGENT_COMPROMISE
RV_SESSION_COMPROMISE
RV_POLICY_WITHDRAWN
RV_POLICY_EMERGENCY_REPLACEMENT
RV_BEHAVIORAL_EVIDENCE_INVALIDATED
RV_CAPABILITY_WITHDRAWN
RV_TRUST_DECISION_WITHDRAWN
RV_EXECUTOR_COMPROMISE
RV_OPERATOR_ACTION
RV_SECURITY_INCIDENT
RV_CONFIGURATION_ERROR
RV_ISSUED_IN_ERROR
RV_UNKNOWN_CAUSE
```

Reason codes are audit data.

They must not change the fundamental fail-closed rule.

---

## 10. Revocation Authority

Not every authority may revoke every artifact.

The Trust Root Registry must define revocation authority scope.

Example:

```text
RootAuthority:
    may revoke authority keys and trust roots

IdentityAuthority:
    may revoke identities it issued

COAAuthority:
    may revoke COA receipts it issued

PolicyAuthority:
    may revoke/supersede VA policies

BehavioralAuthority:
    may revoke BehavioralEvidenceReceipts it issued

AuthorizationAuthority:
    may revoke CapabilityTokens it issued

TrustDecisionAuthority:
    may revoke TrustDecisions it issued
```

Emergency superior revocation may be permitted by root governance.

---

## 11. Revocation Authority Separation

The participant agent must not be able to revoke or reinstate controlling trust artifacts merely by submitting a request.

Revocation changes trust state and therefore belongs to the trusted control plane.

The same principle applies as signing authority:

> Possession of an artifact does not imply authority to change its status.

---

## 12. Revocation Registry

ATE production architecture requires an authoritative current-state source.

Conceptually:

```text
RevocationRegistry {
    trust_domain
    registry_epoch
    generated_at
    records[]
    authority_id
    signature
}
```

The registry may be physically implemented as:

- database
- signed manifest
- append-only journal
- authenticated service

ATE v0.1 is implementation-neutral.

---

## 13. Registry Epoch

The registry exposes a monotonically increasing:

```text
registry_epoch
```

Every accepted update increments the epoch.

Example:

```text
epoch 1041
→ key revoked
→ epoch 1042
```

TrustDecision and executor audit records should capture the revocation epoch consulted.

This supports forensic questions such as:

> Which revocation state was known when this decision was made?

---

## 14. Trust-State Snapshot

A verifier may consume a signed snapshot:

```text
TrustStateSnapshot {
    trust_domain
    registry_epoch
    generated_at
    valid_until

    active_policy_manifest_digest
    trust_root_registry_digest
    revocation_registry_digest

    issuer
    signature
}
```

This binds several current-state inputs into one verifiable reference point.

For high-risk actions, snapshot freshness requirements should be strict.

---

## 15. G0 Revocation Gate

Revocation should remain the first trust-state gate.

Conceptually:

```text
G0_REVOCATION
```

The gate checks controlling artifacts before expensive downstream evaluation.

At minimum:

```text
subject identity
session identity
COA acceptance
VA policy
BehavioralEvidenceReceipt
CapabilityToken
TrustDecision authority
relevant signing keys
```

Any revoked controlling artifact causes denial.

---

## 16. Executor Revocation Recheck

Trust evaluation and execution are separated in time.

Therefore the Capability Executor must recheck revocation immediately before execution for governed actions.

Sequence:

```text
ATE evaluates at epoch 1042
TrustDecision issued
revocation occurs → epoch 1043
executor receives decision
executor checks current epoch 1043
execution denied
```

A valid TrustDecision does not override newer revocation state.

---

## 17. Revocation Precedence

Revocation has precedence over historical grant.

The ordering is:

```text
CURRENT REVOCATION STATE
    > previously signed TrustDecision
    > previously signed CapabilityToken
    > historical evidence validity
```

If a controlling identity or authority is revoked before execution, execution must stop.

---

## 18. Dependency Invalidation

Revoking one object may invalidate dependent objects.

Example dependency graph:

```text
Authority Key
   ↓
CapabilityToken
   ↓
TrustDecision
   ↓
ExecutionCapability
```

If the authority key is revoked because it was compromised, downstream artifacts may also become unusable.

The model must distinguish direct from derived invalidation.

---

## 19. Direct Revocation

Target itself is explicitly revoked.

Example:

```text
CapabilityToken CT-123 → REVOKED
```

---

## 20. Derived Invalidation

Artifact becomes unusable because a controlling dependency changed state.

Example:

```text
K_AUTHORITY compromised
```

may imply:

```text
CapabilityTokens signed after compromise_start_time → invalid
TrustDecisions depending on those tokens → invalid
```

Derived invalidation should be computable and auditable.

---

## 21. Compromise-Time Semantics

Key compromise creates a historical ambiguity.

Suppose:

```text
key compromise discovered: 16:00
estimated compromise began: 13:00
```

Artifacts signed between 13:00 and 16:00 may be suspect.

RevocationRecord may therefore include:

```text
compromise_effective_from
```

distinct from:

```text
revocation_issued_at
```

This allows retrospective invalidation policy.

---

## 22. Historical Validity vs Current Usability

Audit systems must preserve an important distinction.

A revoked artifact may still be historically authentic.

Example:

```text
TrustDecision TD-7 was valid and executed yesterday.
Key was compromised today.
```

Audit must not rewrite yesterday's event as if it never happened.

Instead record:

```text
historically_verified = true
current_status = revoked
revocation_effective_at = ...
```

Historical evidence must remain immutable.

---

## 23. Retroactive Revocation

Some incidents justify retrospective distrust.

Example:

A key is determined to have been compromised before issuance of prior artifacts.

The system may classify prior artifacts:

```text
HISTORICALLY_SUSPECT
```

This does not delete audit records.

It adds later evidence indicating that earlier assurance is no longer reliable.

---

## 24. Policy Supersession

VA policy updates normally use supersession rather than revocation.

Example:

```text
VA-001 v7 → SUPERSEDED
VA-001 v8 → ACTIVE
```

New trust decisions require v8.

Existing TrustDecisions are governed by explicit policy:

- expire immediately on policy change, or
- remain valid until their short expiration if policy allows.

For the current ATE direction, safer default:

> Policy change invalidates unexecuted TrustDecisions bound to the old policy.

---

## 25. Emergency Policy Revocation

If a policy itself is unsafe or compromised:

```text
VA-001 v8 → REVOKED
```

This is stronger than ordinary supersession.

Any unexecuted authorization depending on that policy becomes unusable immediately.

---

## 26. Identity Revocation

Revoking an agent identity must invalidate:

- new session establishment
- new trust decisions
- unexecuted capabilities bound to that identity

Existing historical audit remains intact.

The default production rule should be:

```text
revoked identity → no governed execution
```

---

## 27. Session Revocation

ATE requires session-specific trust.

A session may be revoked independently of long-lived identity.

Reasons include:

- suspicious behavior
- context corruption
- suspected prompt injection
- compromised runtime
- operator termination

Session revocation should invalidate all unexecuted TrustDecisions bound to that session.

---

## 28. COA Revocation

A COA acceptance may be invalidated if:

- wrong version used
- acceptance malformed
- acceptance obtained under invalid session identity
- governance terms withdrawn
- evidence later shown fraudulent

Revocation of COA acceptance invalidates dependent unexecuted CapabilityTokens and TrustDecisions.

---

## 29. Behavioral Evidence Revocation

Behavioral evidence may be revoked before TTL expiration.

Examples:

- evaluator discovers test corruption
- evidence artifact tampered
- subject identity mismatch found
- scoring error discovered

Therefore:

```text
unexpired != unrevoked
```

Both must be checked.

---

## 30. CapabilityToken Revocation

CapabilityToken revocation provides precise withdrawal of authority without revoking the whole agent.

Example:

```text
Agent remains trusted for READ
WRITE token revoked
```

This supports least-privilege incident response.

---

## 31. TrustDecision Revocation

A TrustDecision may be revoked between issuance and execution.

Reasons:

- new evidence
- policy change
- user cancellation
- security incident
- target state change

The executor must check current TrustDecision status immediately before execution.

---

## 32. ExecutionCapability Revocation

If a separate execution capability exists after trust grant, it too must be revocable until consumed.

After a successfully completed one-time execution, revocation affects future reuse—which is already prohibited—but remains relevant to audit interpretation.

---

## 33. Nonce State Is Not Revocation State

Nonce consumption and revocation are different dimensions.

Example:

```text
nonce = AUTHORIZED
CapabilityToken = REVOKED
```

Execution is denied because the token is revoked.

The nonce should not be treated as proof that authorization remains valid.

---

## 34. Current Trust State

ATE may compute a derived current-state object:

```text
CurrentTrustState {
    subject_identity_status
    session_status
    coa_status
    policy_status
    behavioral_status
    capability_status
    trust_decision_status

    trust_root_epoch
    revocation_epoch
    policy_epoch

    evaluated_at
}
```

This object is useful for audit and debugging.

It does not replace verification of signed source records.

---

## 35. Epoch Binding

TrustDecisions should record the epochs used during evaluation:

```text
trust_root_epoch
revocation_epoch
policy_epoch
```

This does not freeze state forever.

It records the state against which the original decision was made.

Executor still checks newer state before execution.

---

## 36. Stale Registry Defense

An attacker may present an old but valid signed revocation snapshot that predates a revocation.

Therefore snapshots require:

```text
issued_at
valid_until
epoch
```

Verifier policy must define minimum acceptable freshness.

For high-risk operations, stale revocation state is denial.

---

## 37. Rollback Attack

Attack:

```text
current registry epoch = 1050
attacker presents signed epoch 1032
```

Even though epoch 1032 is authentic, it is stale.

Systems maintaining durable state should reject epoch rollback:

```text
presented_epoch < highest_seen_epoch
→ DENY
```

This is monotonic trust-state protection.

---

## 38. Split-Brain State

Distributed systems may observe different revocation epochs simultaneously.

For high-impact actions, the architecture must prefer safety over availability.

If current authoritative state cannot be established:

```text
TRUST_STATE_UNCERTAIN
→ NO EXECUTION
```

Low-risk read-only actions may use weaker availability policy if explicitly configured.

---

## 39. Revocation Propagation Objectives

Different risk classes may require different maximum propagation delay.

Example policy:

```text
R0 informational: minutes acceptable
R1 low:          minutes
R2 moderate:     < 60 seconds
R3 high:         near-real-time
R4 critical:     synchronous authoritative check
```

Exact values are deployment policy, not fixed by v0.1.

---

## 40. Push vs Pull Revocation

Possible mechanisms:

### Pull

Verifier queries authoritative registry when needed.

Advantages:
- simple current-state check

Disadvantages:
- dependency availability

### Push

Authorities distribute signed state updates.

Advantages:
- lower latency
- offline verification possible briefly

Disadvantages:
- delivery reliability

Production may combine both.

---

## 41. Fail-Closed Availability Rule

For security-critical action classes:

```text
revocation service unavailable
```

must not become:

```text
assume not revoked
```

Instead:

```text
EXECUTION_DENIED
GX_TRUST_STATE_UNAVAILABLE
```

Availability failure is not evidence of validity.

---

## 42. Revocation Race

Sequence:

```text
T1 verifier checks ACTIVE
T2 authority revokes artifact
T3 executor acts
```

Mitigation:

- short TrustDecision TTL
- executor recheck
- epoch comparison
- atomic reservation after final state check

For high-risk operations, final revocation check should occur immediately before credential acquisition/external effect.

---

## 43. Revocation and Atomic Execution

Ideal sequence:

```text
check current trust state
reserve nonce
recheck critical revocations if needed
obtain scoped credential
execute
consume nonce
```

Absolute atomicity across distributed revocation services and external resources is generally impossible.

ATE therefore minimizes but cannot eliminate race windows.

This is an explicit non-claim.

---

## 44. Revocation of an Authority Key

Authority-key compromise is especially important because many artifacts may depend on one key.

The Trust Root Registry should support:

```text
key_id
status
valid_from
valid_until
compromise_effective_from
replacement_key_id
```

Verifier must evaluate whether artifact issuance falls inside a trusted key interval.

---

## 45. Key Rotation vs Key Revocation

Normal key rotation is not necessarily compromise.

Example:

```text
K1 valid through Sept 30
K2 active Oct 1
```

Historical K1 signatures remain valid for their issuance interval.

Revocation due to compromise may invalidate some historical K1 signatures depending on compromise-effective time.

---

## 46. Root-Key Revocation

Root authority compromise is a catastrophic governance event.

Recovery may require:

- offline recovery keys
- multi-party approval
- emergency trust-root manifest
- explicit replacement epoch
- broad downstream invalidation

ATE v0.1 requires the architecture to support root replacement conceptually, but does not prescribe recovery ceremony.

---

## 47. Trust Root Epoch

Trust Root Registry should expose:

```text
trust_root_epoch
```

Changes such as:

- adding an authority
- changing authority scope
- revoking authority
- rotating root keys

increment the epoch.

TrustDecision records the epoch used at issuance.

---

## 48. Policy Epoch

Policy Authority should similarly expose:

```text
policy_epoch
```

Changes to active policy increment it.

This creates three important monotonic state dimensions:

```text
trust_root_epoch
revocation_epoch
policy_epoch
```

---

## 49. Combined Trust-State Vector

ATE can represent current control-plane state as:

```text
TrustStateVector {
    trust_root_epoch
    revocation_epoch
    policy_epoch
}
```

Example:

```text
{ 18, 1042, 77 }
```

TrustDecisions record the vector used during evaluation.

Executor compares against current state according to risk policy.

---

## 50. State-Change Semantics

Not every epoch change invalidates every TrustDecision.

Example:

A new unrelated agent identity is added to trust roots.

This increments trust-root epoch but need not invalidate an existing decision.

Therefore the executor should not simply require exact epoch equality.

It must determine whether intervening changes affect controlling dependencies.

---

## 51. Dependency-Aware Revalidation

Preferred model:

```text
Decision depends on:
    identity I1
    session S1
    COA C1
    policy P8
    behavioral receipt B1
    capability CT4
    authorities Kx, Ky, Kz
```

On execution, verify current status only for this dependency set plus global trust-root constraints.

This prevents unnecessary invalidation from unrelated state changes.

---

## 52. Dependency Manifest

TrustDecision may include:

```text
DependencyManifest {
    artifact_ids[]
    authority_key_ids[]
    policy_digest
    session_id
}
```

Executor uses this to perform efficient current-state checks.

The manifest itself is inside the TrustDecision signed region.

---

## 53. Revocation Closure

Given an explicitly revoked node, the system can compute dependent unexecuted artifacts that become unusable.

Conceptually:

```text
revocation_closure(target_id)
```

Example:

```text
COA C1 revoked
→ CT4 invalid
→ TD9 invalid
→ EC9 invalid
```

This closure is logical; it does not require physically writing a revocation record for every dependent artifact.

---

## 54. Explicit vs Computed Revocation

### Explicit

Registry contains direct record for artifact.

### Computed

Artifact becomes invalid because dependency is revoked.

Audit should distinguish:

```text
GX_ARTIFACT_REVOKED_DIRECT
GX_ARTIFACT_INVALIDATED_BY_DEPENDENCY
```

This improves diagnosis.

---

## 55. Reinstatement

Suspension may be reversible.

Compromise revocation generally should not be.

Suggested rule:

```text
SUSPENDED → ACTIVE
```

may occur under authorized administrative action.

```text
REVOKED → ACTIVE
```

should default forbidden.

Instead issue a new artifact or key.

This preserves monotonic security history.

---

## 56. Cancellation vs Security Revocation

A user may cancel an authorization without any compromise.

This should still use revocation mechanics, with reason:

```text
RV_OPERATOR_ACTION
```

Security semantics are the same:

unexecuted authorization becomes unusable.

---

## 57. TrustDecision TTL

Short-lived TrustDecisions reduce revocation race exposure.

Production guidance:

- low-risk actions may tolerate longer TTL
- high-risk decisions should be very short-lived
- critical actions may require immediate execution after approval

TTL never replaces revocation checks.

---

## 58. Session Lifetime

Session revocation and natural session termination should converge operationally:

```text
session not ACTIVE
→ no new governed action
```

TrustDecisions bound to ended sessions should not remain executable unless an explicit asynchronous-work design is introduced later.

---

## 59. Revocation and Human Approval

If an action requires HumanApproval, that approval is also revocable before execution.

Cancellation, role loss, or security incident must be able to invalidate pending approval.

Human approval status therefore belongs in the dependency set for those actions.

---

## 60. Audit Requirements

Every trust-state change should generate an immutable audit event.

Minimum event:

```text
TrustStateAuditEvent {
    event_id
    event_type
    target_type
    target_id
    previous_status
    new_status
    reason_code
    effective_at
    recorded_at
    issuer
    registry_epoch
    previous_record_hash
    signature
}
```

---

## 61. No Destructive History Rewrite

Revocation must never delete historical evidence.

The system appends new state.

Bad:

```text
delete old TrustDecision
```

Good:

```text
append revocation event referencing TrustDecision
```

This preserves forensic traceability.

---

## 62. Revocation Provenance

A revocation record itself must have provenance:

- who issued it
- under what authority
- at what time
- under which registry epoch
- with what signature

Otherwise an attacker could deny service by forging revocations.

---

## 63. Unauthorized Revocation Attack

Threat:

Attacker submits fake revocation for a legitimate authority or token.

Defense:

- verify revocation issuer
- verify issuer scope
- verify signature
- verify target domain

Invalid revocation records are ignored as authority claims but should be audited as attack attempts.

---

## 64. Revocation Flood / DoS

An attacker may attempt large volumes of bogus revocation checks or records.

Controls may include:

- authenticated update channels
- bounded record size
- rate limits
- signed registry manifests
- indexed target lookup

Authorization integrity remains fail-closed.

---

## 65. Trust-State Caching

Caching may improve performance but introduces staleness.

Every cache entry needs:

```text
source_epoch
fetched_at
valid_until
```

Risk policy determines whether cached state is acceptable.

High-risk execution should prefer authoritative current check.

---

## 66. Offline Operation

Offline ATE verification creates unavoidable revocation uncertainty.

Possible policy:

```text
R0/R1:
    permit signed snapshot within freshness window

R2+:
    require authoritative online state
```

Offline operation must never silently assume no revocations occurred.

---

## 67. Network Partition

If verifier cannot reach current state authority:

```text
trust_state = UNKNOWN
```

For governed write/action operations, default:

```text
NO EXECUTION
```

This trades availability for safety.

---

## 68. Recovery After Partition

After connectivity returns:

- fetch current epochs
- detect rollback or skipped states
- reconcile cached decisions
- mark affected pending actions
- audit any trust-state discontinuity

Do not execute queued high-risk grants automatically without revalidation.

---

## 69. Emergency Kill Switch

ATE production architecture may support emergency domain-level suspension.

Conceptually:

```text
TrustDomainStatus = SUSPENDED
```

Effect:

```text
no new governed executions in domain
```

This is useful during major compromise.

It should require high-assurance authority and prominent audit logging.

---

## 70. Scoped Kill Switch

Prefer narrow emergency controls where possible.

Examples:

```text
suspend all GitHub merge capabilities
suspend agent identity A
suspend trust-decision authority K7
suspend policy P4
```

Narrow suspension reduces operational blast radius.

---

## 71. Trust-State Query

Conceptual API:

```text
get_current_status(target_type, target_id)
```

Response:

```text
TrustStatus {
    target_type
    target_id
    status
    effective_at
    source_epoch
    reason_code_optional
    authority
    signature_or_snapshot_reference
}
```

Verifier must authenticate response/source.

---

## 72. Batch Dependency Check

Executor should be able to check all decision dependencies efficiently:

```text
check_dependencies(DependencyManifest)
```

Returns:

```text
ALL_ACTIVE
```

or first deterministic invalid state plus reason.

This avoids dozens of independent network calls.

---

## 73. Deterministic Failure Codes

Recommended reason codes:

```text
GX_IDENTITY_REVOKED
GX_SESSION_REVOKED
GX_COA_REVOKED
GX_POLICY_REVOKED
GX_POLICY_SUPERSEDED
GX_BEHAVIORAL_REVOKED
GX_CAPABILITY_REVOKED
GX_TRUST_DECISION_REVOKED
GX_AUTHORITY_KEY_REVOKED
GX_TRUST_ROOT_REVOKED
GX_ARTIFACT_INVALIDATED_BY_DEPENDENCY
GX_TRUST_STATE_STALE
GX_TRUST_STATE_UNAVAILABLE
GX_REGISTRY_ROLLBACK_DETECTED
GX_DOMAIN_SUSPENDED
```

---

## 74. Fail-Closed Evaluation Pseudocode

```text
function evaluate_current_trust_state(envelope):

    state = load_authoritative_trust_state()

    if state unavailable:
        DENY GX_TRUST_STATE_UNAVAILABLE

    if rollback_detected(state):
        DENY GX_REGISTRY_ROLLBACK_DETECTED

    for dependency in envelope.dependencies:
        status = state.status(dependency)

        if status != ACTIVE:
            DENY mapped_reason(status, dependency)

    continue ATE evaluation
```

---

## 75. Executor Pseudocode

```text
function execute(decision, action):

    verify(decision)

    deps = decision.dependency_manifest

    current = check_current_state(deps)

    if current != ALL_ACTIVE:
        deny execution

    reserve nonce atomically

    recheck critical dependencies if policy requires

    obtain scoped credential
    perform exact action
    finalize nonce
    append audit
```

---

## 76. State Transition Safety

Trust state should generally be monotonic toward less authority unless a new artifact is issued.

Examples:

```text
ACTIVE → SUSPENDED
ACTIVE → REVOKED
ACTIVE → EXPIRED
ACTIVE → SUPERSEDED
SUSPENDED → REVOKED
SUSPENDED → ACTIVE  (authorized reinstatement only)
```

Avoid:

```text
REVOKED → ACTIVE
```

Prefer issuing replacement artifact.

---

## 77. Replacement Semantics

A replacement should have a new immutable identifier.

Example:

```text
K_AUTHORITY_7 revoked
K_AUTHORITY_8 issued
```

Not:

```text
same key_id magically active again
```

This protects audit clarity.

---

## 78. Key-Custody Integration

This model relies on the Trust Root & Key Custody Model.

Revocation records themselves are meaningful only if:

- revocation signing keys are protected
- issuer roles are constrained
- authority scope is registry-defined
- root updates are protected

Thus:

> Revocation is only as trustworthy as the authority that can declare it.

---

## 79. Enforcement-Plane Integration

The Enforcement Plane must treat revocation as a live prerequisite for credential release.

Credential Vault rule:

```text
no scoped credential release
unless controlling trust state is ACTIVE
```

This prevents revoked grants from remaining usable merely because the executor received them earlier.

---

## 80. Audit-Ledger Integration

Audit should record both:

```text
state_at_decision
state_at_execution
```

including relevant epochs.

This exposes races and explains why a decision that was valid at issuance may later be denied at execution.

---

## 81. Production Invariants

### INV-R1

A revoked controlling artifact cannot contribute to new `TRUST_GRANTED`.

### INV-R2

A revoked TrustDecision cannot execute.

### INV-R3

Historical evidence is never deleted because of revocation.

### INV-R4

Revocation authority is itself authenticated and scoped.

### INV-R5

Unknown current state cannot be treated as active for governed execution.

### INV-R6

Registry rollback is detected and rejected.

### INV-R7

Revocation of a controlling dependency invalidates dependent unexecuted authority.

### INV-R8

Executor rechecks current state before external effect.

### INV-R9

Reinstatement cannot erase prior revocation history.

### INV-R10

Revocation state is distinct from nonce/execution state.

---

## 82. Assurance Profiles

### Development

- local signed registry
- manual revocation updates
- same-host checks

### Standard

- authenticated revocation service
- durable epochs
- executor preflight recheck
- append-only audit

### High Assurance

- independently hosted state service
- hardened revocation keys
- near-real-time propagation
- strict stale-state rejection
- redundant authoritative sources

### Critical

- multi-party root governance
- synchronous current-state validation
- offline recovery authority
- independent monitoring
- isolated enforcement infrastructure

---

## 83. Small Future PoC

If implementation evidence is eventually required, a minimal local PoC could use no model calls.

Cases:

### R1 — Active token

```text
ACTIVE CapabilityToken
→ execution permitted
```

### R2 — Token revoked after TrustDecision issuance

```text
TrustDecision valid
CapabilityToken revoked
→ executor denies
```

### R3 — Session revoked

```text
session revoked
→ dependent decision denied
```

### R4 — stale registry rollback

```text
highest_seen_epoch = 10
present epoch = 9
→ deny
```

These would test trust-state mechanics rather than model behavior.

No such experiment is required now.

---

## 84. Highest-Priority Design Consequences

This model produces five production consequences.

1. **Revocation must be checked twice:** during trust evaluation and immediately before execution.
2. **TrustDecision is not sovereign:** newer trust-state changes can invalidate it.
3. **Historical authenticity and current usability must remain distinct.**
4. **Epoch rollback protection is necessary:** old signed state can still be dangerous.
5. **Dependency-aware invalidation is preferable to global invalidation.**

---

## 85. Architectural Conclusion

ATE production trust cannot be represented solely by static signed artifacts.

Trust is partly historical evidence and partly live system state.

The resulting production rule is:

> **A trust grant is executable only while every controlling dependency remains currently valid.**

This extends the existing ATE principle:

> **Trust the action, not the agent.**

with a second condition:

> **Trust is continuously revocable until the governed action is irreversibly consumed.**

The architecture therefore becomes:

```text
Evidence
   ↓
Trust Decision
   ↓
Current Trust-State Check
   ↓
Capability
   ↓
Final Revocation Recheck
   ↓
Execution
   ↓
Audit
```

A signed authorization proves that authority existed.

The revocation and trust-state plane proves that authority still exists now.

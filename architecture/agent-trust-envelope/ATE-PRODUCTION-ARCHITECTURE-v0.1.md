# ATE Production Architecture v0.1

## 1. Purpose

The Agent Trust Envelope (ATE) Production Architecture defines how an AI agent is granted permission to perform a specific governed action based on verifiable evidence, current policy, least-privilege authorization, and independent trust evaluation.

The architecture does not classify an agent as permanently trustworthy.

It answers a narrower question:

> Given this agent, this runtime/session, this governance state, this evidence, this requested action, and the currently authoritative policies, may this specific action be performed now?

The resulting trust decision must control access to the capability required to perform the action.

## 2. Core Security Principle

ATE trust is:

- action-specific
- session-specific
- policy-specific
- time-bounded
- evidence-backed
- least-privilege
- revocable
- independently evaluated
- auditable
- fail-closed

A previous successful trust decision does not imply future authorization.

A trusted agent is not the primitive.

A **trusted governed action under defined conditions** is the primitive.

## 3. Production Components

ATE Production Architecture v0.1 defines six primary components:

1. Trust Root Registry
2. Evidence Authorities
3. ATE Verifier
4. Trust Decision Authority
5. Capability Executor
6. Tamper-Evident Audit Ledger

Supporting components include:

- Revocation Registry
- Policy Authority
- Agent Runtime
- External Resource

## 4. High-Level Architecture

```text
                         ┌───────────────────────┐
                         │  Trust Root Registry  │
                         └───────────┬───────────┘
                                     │
                            recognized authorities
                                     │
          ┌──────────────────────────┼──────────────────────────┐
          │                          │                          │
          ▼                          ▼                          ▼
 ┌────────────────┐         ┌────────────────┐         ┌────────────────┐
 │ Policy Authority│        │Evidence Authority│       │Revocation      │
 │ VA / Governance │        │Behavior / Identity│      │Registry        │
 └────────┬────────┘         └────────┬─────────┘       └──────┬─────────┘
          │                           │                         │
          └──────────────┬────────────┴─────────────┬──────────┘
                         │                          │
                         ▼                          │
                ┌─────────────────┐                 │
 Agent Runtime─►│ Evidence Bundle │                 │
                └────────┬────────┘                 │
                         │                          │
                         ▼                          │
                ┌─────────────────┐◄────────────────┘
                │   ATE Verifier  │
                └────────┬────────┘
                         │
                   verified evidence
                         │
                         ▼
                ┌────────────────────┐
                │ Trust Decision     │
                │ Authority          │
                └─────────┬──────────┘
                          │
              TRUST_GRANTED / TRUST_DENIED
                          │
                 ┌────────┴────────┐
                 │                 │
              DENIED             GRANTED
                 │                 │
                 ▼                 ▼
          no capability     ┌─────────────────┐
                            │Capability       │
                            │Executor         │
                            └────────┬────────┘
                                     │
                               governed action
                                     │
                                     ▼
                            ┌─────────────────┐
                            │External Resource│
                            └─────────────────┘

Every stage emits evidence to:

                ┌──────────────────────┐
                │ Tamper-Evident Audit │
                │ Ledger               │
                └──────────────────────┘
```

## 5. Trust Root Registry

### 5.1 Purpose

The Trust Root Registry defines which authorities are recognized and what each authority is allowed to attest or sign.

Cryptographic validity alone is insufficient.

A valid signature from an unauthorized issuer must be rejected.

### 5.2 Minimum registry entry

```text
TrustRootEntry {
    authority_id
    public_key
    permitted_artifact_types[]
    trust_domain
    valid_from
    valid_until
    status
    revocation_reference
}
```

### 5.3 Required validation

For every signed artifact:

```text
signature valid
AND
issuer known
AND
issuer permitted for artifact type
AND
issuer currently active
AND
issuer not revoked
```

Otherwise:

```text
TRUST_DENIED
GX_UNTRUSTED_ISSUER
```

## 6. Evidence Authorities

Evidence Authorities issue signed evidence used by ATE. They must be logically separate from the participant agent whose actions are being evaluated.

Evidence classes include runtime/identity evidence, Condition of Agency evidence, Value Architecture evidence, and Behavioral Evidence.

### 6.1 Runtime / Identity Evidence

Establishes runtime identity, session identity, ephemeral signing identity, provider/model identity where available, freshness challenge, and lifecycle provenance.

### 6.2 Condition of Agency Evidence

Establishes exact COA version, acceptance response, session binding, acceptance time, acceptance authority, and acceptance fingerprint.

### 6.3 Value Architecture Evidence

Establishes the currently applicable governance/value policy:

```text
policy_id
policy_version
policy_digest
issuer
signature
```

### 6.4 Behavioral Evidence

```text
BehavioralEvidenceReceipt {
    receipt_id
    subject_identity
    evidence_source
    evidence_digest
    result
    issued_at
    expires_at
    issuer
    signature
}
```

Behavioral evidence is not permanent.

## 7. Policy Authority

The Policy Authority declares which policy version is authoritative now. A signed policy artifact is not sufficient if it has been superseded.

```text
ActivePolicyManifest {
    policy_id
    active_version
    active_digest
    effective_from
    revoked_versions[]
    issuer
    signature
}
```

ATE must verify that the artifact policy id/version/digest exactly matches the active manifest. Otherwise:

```text
TRUST_DENIED
GX_POLICY_NOT_CURRENT
```

## 8. Revocation Registry

Revocation must be first-class. Any controlling artifact may be revoked, including identity, session, COA acceptance, VA policy, behavioral receipt, capability token, trust authority, trust decision, or signing key.

```text
RevocationRecord {
    artifact_type
    artifact_id
    revoked_at
    reason_code
    issuer
    signature
}
```

Recommended first gate:

```text
G0_REVOCATION
```

Any controlling revoked artifact produces:

```text
TRUST_DENIED
GX_ARTIFACT_REVOKED
```

## 9. ATE Evidence Bundle

```text
AgentTrustEnvelope {
    envelope_id
    subject_identity
    runtime_identity
    session_identity
    live_provenance_receipt
    coa_acceptance_receipt
    va_policy
    behavioral_evidence_receipt
    capability_token
    requested_action
    freshness_challenge
    nonce
    created_at
    expires_at
    envelope_binding_hash
}
```

All contained artifacts must bind to the same intended subject/session context.

## 10. Requested Action

```text
RequestedAction {
    operation
    target
    parameters_digest
    requested_at
}
```

The action must be included in the signed trust-decision binding.

## 11. CapabilityToken

The CapabilityToken defines the maximum authority available. It does not itself prove that execution should occur.

```text
CapabilityToken {
    token_id
    subject_identity
    session_identity
    permitted_operations[]
    permitted_targets[]
    excluded_targets[]
    constraints
    coa_acceptance_id
    policy_id
    policy_version
    policy_digest
    issued_at
    expires_at
    nonce
    issuer
    signature
}
```

The requested action must be a subset of the capability. No implicit widening is permitted.

## 12. ATE Verifier

Recommended production verification sequence:

```text
G0  Revocation
G1  Trust-root / issuer authority
G2  Runtime + session provenance
G3  COA acceptance and binding
G4  Current VA policy compatibility
G5  Behavioral evidence
G6  Capability scope
G7  Evidence-envelope binding
G8  Freshness / expiration
G9  Nonce / replay state
G10 Requested-action canonicalization
```

All gates must pass. Evaluation stops at the first deterministic failure.

## 13. Fail-Closed Rule

Any missing field, malformed object, unrecognized issuer, invalid signature, expired evidence, revoked artifact, policy mismatch, session mismatch, subject mismatch, COA mismatch, behavioral evidence failure, scope violation, unknown nonce, consumed nonce, action mismatch, envelope-binding mismatch, unsupported artifact version, or verifier exception produces denial or no execution.

```text
UNKNOWN != ALLOW
ERROR   != ALLOW
MISSING != ALLOW
```

Only explicit successful verification may result in grant.

## 14. Trust Decision Authority

The Trust Decision Authority is separate from the participant agent. The participant must not be able to self-certify its own trust grant.

```text
TrustDecision {
    trust_decision_id
    envelope_id
    envelope_binding_hash
    subject_identity
    session_identity
    requested_action_digest
    verdict
    reason_code
    policy_digest
    coa_acceptance_fingerprint
    behavioral_receipt_id
    capability_token_id
    issued_at
    expires_at
    nonce
    authority_id
    signature
}
```

Valid verdicts:

```text
TRUST_GRANTED
TRUST_DENIED
```

No ambiguous third state is executable.

## 15. Capability Executor

The Capability Executor converts a valid trust grant into actual authority and is the central production enforcement boundary.

The participant agent must not directly possess unrestricted access to the governed resource.

```text
Agent
  │ requests action
  ▼
ATE Trust Decision
  │
  ├── DENY ──► no execution path
  │
  └── GRANT
        │
        ▼
Capability Executor
        │
        ▼
External Resource
```

If the agent can bypass the executor, ATE does not enforce trust.

## 16. Executor Validation

Before executing an action, the executor verifies TrustDecision signature, authorized trust authority, `TRUST_GRANTED`, freshness, revocation, session binding, action binding, CapabilityToken binding, nonce state, and resource scope.

Then and only then:

```text
NONCE_AUTHORIZED → NONCE_CONSUMED
```

Consumption must be atomic with execution authorization. Replay must fail.

## 17. One-Time Authorization

ATE Production v0.1 retains the PoC rule:

> One trust envelope authorizes at most one governed action.

This simplifies replay prevention, audit semantics, revocation, causal reasoning, least privilege, and forensic reconstruction.

## 18. Tamper-Evident Audit Ledger

Every decision and execution must produce durable evidence.

```text
AuditRecord {
    audit_id
    timestamp
    previous_record_hash
    envelope_id
    trust_decision_id
    subject_identity
    session_identity
    requested_operation
    requested_target
    coa_acceptance_id
    policy_digest
    behavioral_receipt_id
    capability_token_id
    verdict
    reason_code
    execution_status
    controlling_artifact_hashes[]
    issuer
    record_signature
}
```

Records should form a hash chain:

```text
Audit[n].previous_record_hash = SHA256(Audit[n-1])
```

## 19. Freshness Model

Production should treat evidence freshness by evidence class. Example:

```text
Live Provenance        session-local
COA Acceptance         session-local
CapabilityToken        minutes/hours
TrustDecision          seconds/minutes
Behavioral Receipt     hours/days
Identity Credential    days/months
VA Policy              until superseded/revoked
```

Riskier capabilities should require fresher evidence.

## 20. Trust Domains

Production ATE should introduce `TrustDomain` as an administrative authority boundary. A verifier can then define which identity, behavioral, policy, or authorization authorities are accepted within or across domains.

## 21. Compromise Model

Production architecture must explicitly distinguish compromise domains including compromised model, agent runtime, Trust Decision Authority, Authorization Authority, Policy Authority, Behavioral Authority, executor, host OS, key store, and policy distribution service.

The fewer components that share the same compromise domain, the stronger the trust claim.

## 22. Security Invariants

ATE Production Architecture should maintain the following invariants:

- INV-1: No agent may authorize itself.
- INV-2: No valid signature implies authority unless the signer is authorized for that artifact class.
- INV-3: No trust decision survives controlling-policy mismatch.
- INV-4: No expired or revoked evidence can contribute to grant.
- INV-5: A CapabilityToken cannot be widened by the participant.
- INV-6: A trust decision binds exactly one requested action.
- INV-7: Execution cannot occur without a valid `TRUST_GRANTED`.
- INV-8: A consumed authorization cannot be replayed.
- INV-9: The participant cannot bypass the Capability Executor.
- INV-10: Every decision and attempted execution produces audit evidence.

## 23. Production Trust Decision

Conceptual pseudocode:

```text
function evaluate(envelope):
    canonicalize(envelope)
    check_revocation(envelope)
    check_trust_roots(envelope)
    check_runtime_provenance(envelope)
    check_coa_acceptance(envelope)
    check_active_policy(envelope)
    check_behavioral_evidence(envelope)
    check_capability_scope(envelope)
    check_binding_hashes(envelope)
    check_freshness(envelope)
    check_nonce(envelope)
    check_requested_action(envelope)
    return signed TRUST_GRANTED
```

Any deterministic failure returns signed `TRUST_DENIED(reason_code)`. Unexpected verifier failure results in no execution.

## 24. Execution Algorithm

```text
function execute(trust_decision, requested_action):
    verify trust_decision signature
    verify authorized trust authority
    verify verdict == TRUST_GRANTED
    verify decision freshness
    verify not revoked
    verify action digest
    verify nonce == AUTHORIZED

    atomically:
        reserve nonce
        perform governed action
        mark nonce CONSUMED

    emit audit record
```

Production design must distinguish `AUTHORIZED`, `RESERVED`, `CONSUMED`, `FAILED_BEFORE_EFFECT`, and `FAILED_AFTER_UNKNOWN_EFFECT` or equivalent states.

## 25. Explicit Non-Claims

ATE Production Architecture v0.1 does not claim that an AI model is morally good, that a trusted agent cannot malfunction, that provenance proves semantic correctness, that signatures prove trustworthy intent, that compromise of governing trust roots is solved, that host compromise is solved, that hardware attestation is unnecessary, that federation is solved, that behavioral evaluation guarantees future conduct, or that all authorization can safely be automated.

ATE reduces and structures trust risk. It does not eliminate risk.

## 26. Relationship to Value Architecture

Within ATE, Value Architecture functions as a governing compatibility constraint. VA determines whether an action belongs within the governing policy space. Capability authorization determines whether this particular subject may perform it.

## 27. Relationship to Condition of Agency

COA establishes the governance conditions the participant accepted for the current context. ATE verifies the correct COA version, subject, session, acceptance, freshness, authority, and revocation state.

COA answers: **What conditions govern this agency?**

ATE answers: **Given those conditions and all other evidence, may this action occur?**

## 28. Relationship to Live Provenance

Live Provenance establishes evidence connecting runtime/session activity to the actual agent/model-response lifecycle. ATE uses this primitive but does not equate provenance with trust.

## 29. Recommended Production Boundary

The strongest practical security boundary is:

```text
Untrusted / semi-trusted:
    model
    participant agent
    prompt/context

Trusted enforcement plane:
    trust roots
    evidence verification
    policy authority
    trust-decision authority
    capability executor
    audit ledger
```

The model may recommend. The trust system decides. The executor enforces.

## 30. Next Architectural Questions

Before implementation, resolve key custody, executor isolation, revocation distribution, external-effect atomicity, human approval requirements, risk classes, trust authority compromise, and audit retention.

## 31. Recommended Next Milestone

The next milestone should be **ATE Production Threat Model v0.1**, formally evaluating attacker capabilities, trust boundaries, protected assets, compromise of each authority, bypass attacks, replay, stale evidence, policy downgrade, confused deputy attacks, capability escalation, executor bypass, key theft, compromised runtime, compromised verifier, and audit tampering.

No model-driven experiment is required for that phase.

## 32. Architectural Conclusion

ATE v0.3.1 demonstrated that evidence-backed agent trust can be represented and evaluated mechanically.

The production architecture extends that idea into enforcement:

> An agent is not granted general trust.

Instead:

> A narrowly scoped capability is granted for one action only when current, independently verifiable evidence demonstrates that the action satisfies identity, provenance, governance, policy, behavioral, authorization, freshness, and replay requirements.

The resulting principle is:

**Trust the action, not the agent.**

And enforce that trust through capability control rather than relying on the agent's cooperation.

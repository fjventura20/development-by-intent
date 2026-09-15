# ATE P0/P1 Conformance Test Plan v0.1

## 1. Purpose

This document defines the minimum executable verification plan for demonstrating ATE P0 and P1 conformance against the requirements in `ATE-PRODUCTION-REQUIREMENTS-CONFORMANCE-PROFILE-v0.1.md`.

The test plan is intentionally local-first and subscription-conserving.

The default rule is:

> Use deterministic local tests whenever a requirement can be verified without invoking a model, provider, or external evaluator.

Hermes or premium model calls are not required for P0/P1 conformance unless a specific requirement cannot be demonstrated by deterministic local evidence.

---

## 2. Test Philosophy

P0/P1 conformance testing should prove the architecture's security properties with the smallest useful matrix.

Priorities:

1. deterministic evidence over repeated model calls;
2. fail-closed behavior over broad feature coverage;
3. enforcement proof over descriptive policy proof;
4. one clean positive path plus targeted negative controls;
5. reproducible artifacts, hashes, and logs;
6. no scope expansion after a blocking failure is observed.

---

## 3. Conformance Targets

### P0 — Development / Experimental

P0 demonstrates that the core ATE decision and enforcement chain is mechanically coherent in a controlled local environment.

A P0 implementation must demonstrate at minimum:

- structured trust artifacts;
- deterministic trust evaluation;
- independent authority roles;
- exact action binding;
- one-action authorization;
- replay denial;
- fail-closed behavior;
- auditable execution evidence.

P0 may use:

- software fixture keys;
- same-host components;
- local sandbox resources;
- deterministic Live Provenance fixtures derived from an independently established provenance primitive.

P0 must not claim production isolation.

### P1 — Standard Production

P1 builds on P0 and additionally requires operational enforcement and durable trust state.

P1 must demonstrate:

- participant cannot directly access protected resource capability;
- executor-side reverification;
- durable nonce state;
- current revocation checks;
- current policy-state checks;
- protected credential separation;
- append-only or tamper-evident audit trail;
- recovery-safe replay prevention;
- fail-closed dependency behavior.

---

## 4. Test Environment

Recommended local reference environment:

```text
Participant process
    ↓ request
ATE verifier / trust authority
    ↓ signed TrustDecision
Capability Executor
    ↓ scoped credential / OS permission
Sandbox resource

Supporting local services:
    Trust Root Registry
    Policy Registry
    Revocation Registry
    Durable Nonce Registry
    Audit Ledger
```

The sandbox should use a dedicated temporary directory or test service inaccessible to the participant except through the executor.

---

## 5. Evidence Package

Every conformance run must produce:

```text
conformance/<run_id>/
    manifest.json
    environment.json
    test-results.json
    audit.log
    artifact-hashes.json
    preservation-report.md
```

Each test result must record:

- test ID;
- profile requirement(s);
- inputs;
- expected result;
- observed result;
- reason code;
- relevant artifact hashes;
- nonce state before/after where applicable;
- execution side effect, if any;
- PASS / FAIL / BLOCKED.

---

## 6. Test Categories

The minimum P0/P1 plan contains eight categories:

1. authority and signature validation;
2. trust-decision correctness;
3. scope enforcement;
4. replay and nonce behavior;
5. executor isolation and bypass resistance;
6. revocation and policy freshness;
7. audit integrity;
8. dependency failure / fail-closed behavior.

---

# 7. P0 Test Matrix

## P0-01 — Valid Trust Grant

Purpose:

Demonstrate the complete positive path.

Setup:

- valid subject/session evidence;
- valid COA acceptance;
- current VA policy;
- valid behavioral evidence;
- valid CapabilityToken;
- fresh nonce;
- exact requested action.

Expected:

```text
TRUST_GRANTED
GX_OK
```

The TrustDecision signature must verify under the authorized Trust Decision Authority key.

PASS criteria:

- all required verification gates pass;
- requested-action digest matches;
- envelope-binding hash matches;
- trust-decision issuer is authorized;
- no trust state is mutated by the pure decision function.

---

## P0-02 — Out-of-Scope Operation

Setup identical to P0-01 except requested operation is not authorized.

Expected:

```text
TRUST_DENIED
GX_OPERATION_OUT_OF_SCOPE
```

No execution is permitted.

---

## P0-03 — Out-of-Scope Target

Setup identical to P0-01 except target is outside authorized scope.

Expected:

```text
TRUST_DENIED
GX_TARGET_OUT_OF_SCOPE
```

No execution is permitted.

---

## P0-04 — Session Substitution

Use otherwise valid artifacts from session A in session B.

Expected:

```text
TRUST_DENIED
GX_SESSION_MISMATCH
```

---

## P0-05 — COA Substitution

Present a valid but incorrect COA acceptance artifact.

Expected:

```text
TRUST_DENIED
GX_COA_BINDING_FAILURE
```

---

## P0-06 — VA Policy Substitution

Present a mismatched `policy_id`, `policy_version`, or `policy_digest`.

Expected:

```text
TRUST_DENIED
GX_VA_POLICY_INCOMPATIBLE
```

---

## P0-07 — Behavioral Evidence Expired

Use a BehavioralEvidenceReceipt whose validity window has expired.

Expected:

```text
TRUST_DENIED
GX_BEHAVIORAL_EXPIRED
```

---

## P0-08 — Artifact Signature Failure

Alter one signed artifact after issuance.

Expected:

```text
TRUST_DENIED
GX_SIGNATURE_INVALID
```

or the implementation's normative equivalent.

---

## P0-09 — Unauthorized Issuer

Use a correctly signed artifact from a key not authorized for that artifact type.

Expected:

```text
TRUST_DENIED
GX_UNTRUSTED_ISSUER
```

This proves that cryptographic validity does not imply authority.

---

## P0-10 — Decision Purity

Record all mutable state before and after `trust_decide(...)`.

Expected:

```text
state_before == state_after
```

The trust-decision function must not consume nonce state or mutate authorization state.

---

## P0-11 — One-Time Execution

Given a valid `TRUST_GRANTED` decision:

Expected state chain:

```text
NONCE_UNSEEN
→ NONCE_AUTHORIZED
→ NONCE_RESERVED
→ NONCE_CONSUMED
```

Exactly one governed action occurs.

---

## P0-12 — Replay Rejection

Attempt execution again using the consumed authorization from P0-11.

Expected:

```text
EXECUTION_DENIED
GX_NONCE_PREVIOUSLY_CONSUMED
```

No second external effect occurs.

---

## P0-13 — Parameter Digest Substitution

Authorize action parameters A, then execute using modified parameters B.

Expected:

```text
EXECUTION_DENIED
GX_ACTION_BINDING_MISMATCH
```

or normative equivalent.

---

## P0-14 — Unknown Artifact Version

Submit an unsupported artifact version.

Expected:

```text
TRUST_DENIED
GX_UNSUPPORTED_ARTIFACT_VERSION
```

No permissive fallback is allowed.

---

## P0-15 — Missing Required Evidence

Remove one mandatory artifact from the envelope.

Expected:

```text
TRUST_DENIED
```

with a specific missing-evidence reason code.

---

# 8. P0 Required Result

P0 conformance requires:

```text
15 / 15 mandatory P0 tests PASS
```

No waiver is permitted for:

- trust-decision signature validation;
- session binding;
- authorization scope;
- decision purity;
- replay rejection;
- fail-closed missing evidence.

A P0 conformance statement must include the explicit limitation:

> P0 demonstrates logical/mechanical trust and enforcement behavior in a controlled development environment; it does not establish production isolation or resistance to host compromise.

---

# 9. P1 Additional Test Matrix

P1 requires all P0 tests plus the following operational controls.

## P1-01 — Direct Resource Bypass Denied

Participant attempts to modify the protected resource without the Capability Executor.

Expected:

```text
OS / service access DENIED
```

This is a critical P1 requirement.

If direct participant access succeeds, P1 fails regardless of all other results.

---

## P1-02 — Executor Credential Separation

Verify participant cannot read or retrieve governed resource credentials.

Expected:

```text
participant credential access == DENIED
executor credential access == ALLOWED when authorized
```

---

## P1-03 — Executor Reverification

Pass a forged or altered TrustDecision directly to the executor while bypassing upstream verifier logic.

Expected:

```text
EXECUTION_DENIED
```

The executor must independently verify at minimum:

- signature;
- authorized issuer;
- `TRUST_GRANTED` verdict;
- freshness;
- revocation;
- action digest;
- nonce.

---

## P1-04 — Durable Replay Prevention Across Restart

1. execute a valid action;
2. persist `NONCE_CONSUMED`;
3. restart executor / nonce service;
4. replay authorization.

Expected:

```text
EXECUTION_DENIED
```

This proves replay state is not memory-only.

---

## P1-05 — Concurrent Replay

Two executor requests attempt to reserve the same `NONCE_AUTHORIZED` simultaneously.

Expected:

```text
exactly one AUTHORIZED → RESERVED transition succeeds
exactly one external effect occurs
```

The other request must fail without execution.

---

## P1-06 — Revoked CapabilityToken

Revoke an otherwise valid CapabilityToken before execution.

Expected:

```text
EXECUTION_DENIED
GX_ARTIFACT_REVOKED
```

---

## P1-07 — Revoked TrustDecision

Revoke a signed `TRUST_GRANTED` before execution.

Expected:

```text
EXECUTION_DENIED
GX_ARTIFACT_REVOKED
```

---

## P1-08 — Policy Superseded Before Execution

Issue grant under policy version N.

Advance active policy to N+1 before execution.

Expected:

```text
EXECUTION_DENIED
GX_POLICY_CHANGED_BEFORE_EXECUTION
```

when the profile requires final policy-currentness checking.

---

## P1-09 — Revocation Service Unavailable

For a P1-governed action, make current revocation state unavailable.

Expected:

```text
EXECUTION_DENIED
GX_REVOCATION_STATUS_UNAVAILABLE
```

Unknown revocation state must not be interpreted as safe.

---

## P1-10 — Policy Service Unavailable

If current policy state cannot be established when required:

Expected:

```text
EXECUTION_DENIED
```

No execution by stale cached assumption unless explicitly allowed by the normative profile.

---

## P1-11 — Audit Record Chain

Execute at least:

- one grant;
- one denial;
- one successful execution;
- one replay rejection.

Expected:

- each event is recorded;
- records are sequential;
- `previous_record_hash` links correctly;
- record signatures verify.

---

## P1-12 — Audit Tamper Detection

Modify a historical audit record.

Expected:

```text
AUDIT_CHAIN_INVALID
```

or normative equivalent.

The modification must be detectable.

---

## P1-13 — Audit Tail Truncation Detection

Remove the latest record(s) while retaining earlier valid chain history.

Expected:

The system detects inconsistency using an external checkpoint, sequence expectation, replica, or equivalent P1 mechanism.

---

## P1-14 — Target Canonicalization / Path Traversal

Authorize:

```text
sandbox:/authorized/report.txt
```

Attempt:

```text
sandbox:/authorized/../secret.txt
```

Expected:

```text
EXECUTION_DENIED
GX_TARGET_OUT_OF_SCOPE
```

or normative equivalent after canonicalization.

---

## P1-15 — Mutable Target / TOCTOU Protection

Authorize a mutable resource in state A.

Change the resource to state B before execution.

Expected:

```text
EXECUTION_DENIED
GX_TARGET_STATE_CHANGED
```

where resource-state binding is required.

---

## P1-16 — Unknown External Effect

Simulate:

1. external request transmitted;
2. response lost;
3. executor cannot determine whether effect occurred.

Expected state:

```text
UNKNOWN_EFFECT
```

Automatic retry must not occur.

---

## P1-17 — Audit Dependency Failure

For an action class whose profile requires durable audit before execution, make the audit sink unavailable.

Expected:

```text
EXECUTION_DENIED
```

No unaudited execution is allowed for that class.

---

## P1-18 — Trust Root Epoch Rollback

Present a cryptographically valid but stale Trust Root Registry epoch.

Expected:

```text
TRUST_DENIED / EXECUTION_DENIED
```

The implementation must reject rollback to older trust state.

---

## P1-19 — Revocation Epoch Rollback

Present stale revocation state that omits a known revocation.

Expected:

```text
EXECUTION_DENIED
```

---

## P1-20 — Participant Self-Authorization Attempt

Participant signs a TrustDecision using its own identity key.

Expected:

```text
TRUST_DENIED
GX_UNTRUSTED_ISSUER
```

---

# 10. P1 Required Result

P1 conformance requires:

```text
All mandatory P0 tests PASS
AND
20 / 20 mandatory P1 tests PASS
```

The following are absolute blockers:

- P1-01 direct bypass denied;
- P1-02 credential separation;
- P1-03 executor reverification;
- P1-04 durable replay prevention;
- P1-05 atomic concurrent replay defense;
- P1-06 / P1-07 revocation enforcement;
- P1-11 audit chain integrity;
- P1-20 self-authorization rejection.

---

# 11. Test Independence

Tests should avoid accidental state coupling.

Each test should use:

- independent envelope ID;
- independent nonce unless replay is the proposition;
- independent temporary target where practical;
- explicit initial registry epochs;
- explicit expected state.

A test must not inherit `CONSUMED`, `REVOKED`, or superseded state from a previous test unless that dependency is itself being tested.

---

# 12. Deterministic Fixture Policy

P0/P1 may use deterministic local fixtures for:

- Ed25519 authority keys;
- COA acceptance artifacts;
- VA policies;
- BehavioralEvidenceReceipts;
- Live Provenance artifacts derived from an already-established provenance primitive;
- CapabilityTokens;
- TrustDecisions.

Fixture use must be explicitly disclosed.

A local fixture may prove composition and enforcement semantics.

It must not be described as independently re-proving a live model/provider lifecycle unless a real live lifecycle is actually executed.

---

# 13. Model-Call Policy

Default:

```text
MODEL CALLS REQUIRED = 0
```

A model call may be introduced only if:

1. a normative requirement specifically depends on live model behavior;
2. deterministic substitution would invalidate the claim;
3. the PI explicitly authorizes the call.

Conformance implementation should never invoke a model merely to generate convenient test text.

---

# 14. Subscription-Conservation Rule

Before any external invocation, ask:

```text
Can this property be established deterministically from existing frozen evidence or local mechanics?
```

If yes, external invocation is prohibited for the test.

---

# 15. P0 Recommended Minimal Implementation

A low-cost P0 prototype should contain:

```text
p0/
    trust_roots.py
    policy_registry.py
    revocation_registry.py
    nonce_registry.py
    artifacts.py
    verifier.py
    trust_authority.py
    executor.py
    audit.py
    tests/
```

All components may run locally.

The executor may operate on a sandbox filesystem directory.

---

# 16. P1 Recommended Minimal Implementation

P1 should add:

```text
separate participant and executor processes
OS-level sandbox permissions
durable SQLite or equivalent nonce store
durable revocation / policy epochs
credential file or service inaccessible to participant
append-only audit store
restart recovery tests
atomic transaction / compare-and-set nonce reservation
```

A local Linux host is sufficient for a P1 proof-of-concept if the limitations are clearly stated.

---

# 17. Suggested Sandbox Resource

Recommended protected target:

```text
/tmp/ate-p1/protected/
```

Ownership model:

```text
participant user/process:
    no write permission

executor user/process:
    scoped write permission
```

This permits direct proof of executor mediation without external APIs.

---

# 18. Conformance Manifest

Each run should produce:

```json
{
  "profile": "P0" or "P1",
  "spec_version": "v0.1",
  "run_id": "...",
  "implementation_commit": "...",
  "started_at": "...",
  "completed_at": "...",
  "environment_digest": "...",
  "test_count": 0,
  "pass_count": 0,
  "fail_count": 0,
  "blocked_count": 0,
  "evidence_digest": "..."
}
```

---

# 19. Conformance Classification

Allowed classifications:

```text
ATE_P0_CONFORMANT
ATE_P0_NOT_CONFORMANT
ATE_P0_INCONCLUSIVE

ATE_P1_CONFORMANT
ATE_P1_NOT_CONFORMANT
ATE_P1_INCONCLUSIVE
```

No partial-pass wording should be used as a conformance claim.

---

# 20. Stop Conditions

Stop the run when:

- a mandatory test exposes an architectural contradiction;
- a frozen requirement must be weakened to obtain PASS;
- direct bypass unexpectedly succeeds;
- replay produces a second side effect;
- self-authorization succeeds;
- the test harness cannot distinguish test failure from implementation failure;
- evidence preservation becomes uncertain.

Do not repair requirements during a scored conformance run.

---

# 21. Development vs Scored Runs

Exploratory development runs may repair implementation defects.

A scored conformance run must use:

- frozen implementation candidate;
- frozen test plan version;
- clean initial state;
- preserved evidence;
- no post-observation requirement changes.

This separation avoids turning debugging into evidence.

---

# 22. P0 Success Claim

If all P0 tests pass, the permitted claim is:

> ATE P0 demonstrates deterministic local composition of trust evidence, least-privilege authorization, signed trust decisions, exact action binding, one-time execution, replay rejection, and fail-closed negative paths in a controlled development environment.

It does not establish production resource isolation.

---

# 23. P1 Success Claim

If all P0 and P1 tests pass, the permitted claim is:

> ATE P1 demonstrates that a participant lacking direct governed-resource authority can obtain exactly one scoped effect only through an independently verifying Capability Executor operating under current trust, policy, revocation, nonce, and audit state.

This remains a software-level conformance claim and does not establish protection against host-root compromise.

---

# 24. Recommended Execution Order

When implementation begins:

```text
Phase 1 — P0 deterministic development
Phase 2 — P0 scored conformance
Phase 3 — P1 executor-isolation development
Phase 4 — P1 scored conformance
```

Do not attempt P2/P3 until P1 is stable.

---

# 25. Recommended Immediate Next Step

No model experiment is required.

The next implementation milestone should be:

> **ATE P0 Local Conformance Harness v0.1**

It should implement only the minimum components needed to execute P0-01 through P0-15 locally.

The harness should reuse existing frozen ATE v0.3.1 concepts and deterministic fixtures where appropriate, while keeping the production architecture documents unchanged.

---

# 26. Final Principle

Conformance evidence should answer a simple question:

> Can the implementation actually enforce the architecture's security invariants, including when the participant behaves incorrectly?

The goal is not to maximize test count.

The goal is to prove the few properties that make ATE meaningful:

```text
No valid trust grant → no capability.
No capability → no governed action.
One valid grant → at most one exact governed action.
Every decision and effect → independently reconstructable evidence.
```

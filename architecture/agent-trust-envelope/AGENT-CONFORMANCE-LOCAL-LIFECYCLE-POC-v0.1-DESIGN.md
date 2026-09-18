# Agent Conformance Local Lifecycle PoC v0.1 — Design

**Status:** DESIGN DRAFT — NOT FROZEN  
**Parent baseline:** `AGENT-CONFORMANCE-PROTOCOL-v0.1.2-FREEZE.md`  
**Parent freeze commit:** `8c98318e9b5eb634cf067866a9a81ee96b024c25`  
**Scope:** Local deterministic proof of conformance invalidation, stale-capability denial, re-attestation, restoration, and audit continuity  
**External model calls:** PROHIBITED  
**Hermes usage:** NOT REQUIRED  
**Implementation authorization:** NONE until adversarial review and freeze

---

## 1. Purpose

This PoC tests whether the frozen Agent Conformance Protocol v0.1.2 can be enforced in a minimal local system.

The single architectural question is:

> Can a previously conformant subject lose authority when one material governed property changes, can stale executable authority be denied, and can authority be restored only after fresh evidence and a new lifecycle decision?

The PoC intentionally does not test model reasoning, subjective behavior, distributed systems, or Internet-scale identity.

---

## 2. Success Claim

The PoC may claim success only if it demonstrates the full lifecycle:

```text
CONFORMANT @ epoch N
    ↓
governed action authorized and executed
    ↓
material runtime state changes
    ↓
independent trigger observation
    ↓
REATTESTATION_REQUIRED or SUSPENDED @ epoch N+1
    ↓
stale capability denied
    ↓
fresh post-change evidence
    ↓
R13 evaluation
    ↓
R14 restoration to CONFORMANT @ epoch N+2
    ↓
new action authorized and executed
    ↓
append-only audit chain verifies
```

Partial success is not sufficient.

---

## 3. Non-Goals

This PoC does not test:

- live LLM identity
- semantic behavioral evaluation
- remote attestation
- hardware attestation
- production PKI
- federation
- cloud deployment
- human approval workflows
- multiple trust domains
- multiple roles
- distributed consensus
- high availability
- performance
- production key custody
- model provider provenance

The runtime property under test is a deterministic local file-backed version identity.

---

## 4. Frozen Inputs

The implementation MUST treat the following as read-only controlling design inputs:

- `AGENT-CONFORMANCE-PROTOCOL-v0.1.2.md`
- `AGENT-CONFORMANCE-PROTOCOL-v0.1.2-FREEZE.md`
- `AGENT-QUALIFICATION-AND-ADMISSION-PROTOCOL-v0.2.2.md`
- `ATE-REVOCATION-TRUST-STATE-MODEL-v0.1.md`
- `ATE-ENFORCEMENT-PLANE-v0.1.md`
- `ATE-AUDIT-ACCOUNTABILITY-MODEL-v0.1.md`

The PoC MUST NOT weaken or reinterpret those artifacts.

---

## 5. System Model

The PoC uses one subject, one role, one trust domain, one governed action, and one material runtime attribute.

```text
trust_domain = local-poc
subject_id   = agent-001
role_id      = worker
runtime_attr = runtime_version
allowed      = v1 initially, then v2 after re-attestation
action       = WRITE_RESOURCE
resource     = local protected file
```

The protected resource MUST be writable only through the PoC executor path.

---

## 6. Logical Components

Minimum components:

1. **Subject State Store**
   - current runtime version
   - subject identity
   - role binding

2. **Qualification/Admission Fixture**
   - deterministic pre-established valid qualification state
   - deterministic pre-established valid admission state
   - no dynamic requalification/readmission in the base happy path

3. **Trigger Observer**
   - independently reads runtime state
   - emits signed/deterministically authenticated trigger observation when state changes

4. **R13 Evaluator**
   - evaluates current evidence against the frozen conformance profile
   - produces immutable evaluation result

5. **R14 Lifecycle State Authority**
   - publishes lifecycle state and monotonic state epoch

6. **Authorization Service**
   - checks qualification
   - checks admission
   - checks current conformance state
   - issues one bounded capability

7. **Capability Executor**
   - final current-state check
   - epoch check
   - exact action check
   - nonce/replay protection
   - writes protected resource only after all checks pass

8. **Audit Ledger**
   - append-only records
   - sequence numbers
   - previous-record hash chain
   - signed/authenticated records

---

## 7. Trust Separation

The implementation MUST logically separate:

```text
Subject
R13
R14
Authorization Service
Executor
Trigger Observer
Audit Recorder
```

For the PoC, separation may use distinct local keys/files/process identities rather than separate machines.

The subject MUST NOT be able to directly mutate:

- lifecycle state
- lifecycle epoch
- R13 evaluation result
- R14 decision
- capability issuer state
- executor credential
- audit history

---

## 8. Material Change Under Test

The sole base mutation is:

```text
runtime_version: v1 -> v2
```

Before mutation, the active ConformanceRequirementsProfile permits only `v1`.

The mutation MUST occur after a valid capability has already been issued under epoch N but before that capability is exercised in the stale-capability test.

This is deliberate: it creates a real TOCTOU condition.

---

## 9. Initial Conformance Profile

Conceptual profile:

```text
profile_id = local-conformance-poc
profile_version = 1
trust_domain = local-poc
role_id = worker

required_runtime_version = v1
max_conformance_age = deterministic large test bound
trigger_source = local-runtime-observer
whole_role_failure = true

evaluator_authority = R13
lifecycle_state_authority = R14
```

Canonical encoding and signing-domain separation MUST follow the frozen protocol.

---

## 10. Initial State

Required starting state:

```text
qualification = ACTIVE
admission = ACTIVE
runtime_version = v1
conformance = CONFORMANT
state_epoch = N
nonce_registry = empty
audit_chain = valid
```

The initial CONFORMANT state MUST itself be backed by:

- runtime evidence for v1
- R13 evaluation
- R14 state decision
- audit records

No hard-coded “trusted=true” shortcut is permitted.

---

## 11. Governed Action

The action is intentionally simple:

```text
WRITE_RESOURCE {
    target = protected_resource.txt
    payload_digest = SHA256(fixed payload)
}
```

The resource operation should append one deterministic line containing a capability/action identifier.

The subject MUST NOT have direct write access to the protected resource through the governed test path.

---

## 12. Capability

Conceptual capability:

```text
ExecutionCapability {
    capability_id
    subject_id
    role_id
    action_digest
    observed_conformance_state
    observed_state_epoch
    nonce
    issued_at
    expires_at
    issuer
    signature
}
```

The capability is single-use.

The executor MUST reject:

- wrong subject
- wrong role
- wrong action digest
- invalid signature
- expired capability
- replayed nonce
- non-CONFORMANT current state
- stale lifecycle epoch

---

## 13. Trigger Observation

The Trigger Observer MUST independently compare authoritative runtime state against the last known material state.

On v1 -> v2:

```text
ConformanceTriggerObservation {
    trigger_class = T4_RUNTIME
    trigger_type = RUNTIME_VERSION_CHANGED
    prior_value_digest = digest(v1)
    current_value_digest = digest(v2)
    severity = MANDATORY_REATTESTATION
}
```

The subject cannot satisfy the test by self-reporting this change.

---

## 14. Lifecycle Transition

Upon valid runtime-change trigger:

1. R13 evaluates current runtime against the active profile.
2. Because v2 does not match required v1, R13 recommends `REATTESTATION_REQUIRED`.
3. R14 publishes:
   ```text
   prior_state = CONFORMANT
   new_state = REATTESTATION_REQUIRED
   state_epoch = N+1
   ```
4. Authorization service must deny new governed capability.
5. Executor must deny any capability bound to epoch N.

---

## 15. Stale-Capability Proof

This is the central proof.

Sequence:

```text
A. state = CONFORMANT @ N
B. issue capability C1 bound to epoch N
C. change runtime v1 -> v2
D. emit trigger
E. R14 publishes REATTESTATION_REQUIRED @ N+1
F. attempt execution with C1
G. executor reads current epoch N+1
H. C1 observed epoch N != N+1
I. executor denies before protected-resource effect
```

Required classification:

```text
STALE_CAPABILITY_DENIED
```

If C1 causes the resource effect after epoch N+1 is authoritative, the PoC fails.

---

## 16. Re-attestation

The PoC next changes policy/profile state in a controlled way so that v2 becomes permitted.

This MUST be represented as a new current ConformanceRequirementsProfile version, not an in-place edit.

Conceptually:

```text
profile v1 -> requires runtime v1
profile v2 -> requires runtime v2
```

The new profile MUST be signed/authorized and activated through the PoC policy fixture.

Fresh runtime evidence MUST be collected after the v1 -> v2 mutation.

R13 evaluates:

```text
runtime evidence = v2
active profile = v2
qualification = ACTIVE
admission = ACTIVE
trust state = current
=> recommended CONFORMANT
```

R14 then publishes:

```text
prior_state = REATTESTATION_REQUIRED
new_state = CONFORMANT
state_epoch = N+2
```

---

## 17. Restoration Proof

After restoration:

1. capability C2 is issued under epoch N+2;
2. C2 binds the exact current action;
3. executor verifies current epoch N+2;
4. executor verifies CONFORMANT;
5. executor reserves C2 nonce;
6. executor writes protected resource;
7. nonce becomes CONSUMED;
8. audit chain records success.

Required classification:

```text
RESTORED_AUTHORITY_EXECUTES
```

---

## 18. Required Test Cases

### TC-01 Initial conformance establishment
Expected: PASS, state CONFORMANT @ N.

### TC-02 Initial authorized action
Expected: PASS and exactly one protected-resource effect.

### TC-03 Capability issuance before mutation
Expected: capability C1 valid and bound to epoch N.

### TC-04 Runtime mutation
Expected: authoritative runtime state becomes v2.

### TC-05 Independent trigger observation
Expected: valid T4 trigger v1 -> v2.

### TC-06 Lifecycle invalidation
Expected: REATTESTATION_REQUIRED @ N+1.

### TC-07 New authorization denied while non-conformant
Expected: DENY.

### TC-08 Stale C1 execution denied
Expected: no resource effect.

### TC-09 Stale C1 retry denied
Expected: no resource effect.

### TC-10 Fresh profile v2 activation
Expected: current authorized profile requires runtime v2.

### TC-11 Fresh post-change runtime evidence
Expected: evidence timestamp/order is after mutation.

### TC-12 R13 positive re-evaluation
Expected: recommended CONFORMANT.

### TC-13 R14 restoration
Expected: CONFORMANT @ N+2.

### TC-14 New capability C2 issuance
Expected: bound to epoch N+2.

### TC-15 Restored execution
Expected: exactly one new protected-resource effect.

### TC-16 Replay C2
Expected: denied; no duplicate effect.

### TC-17 Audit-chain verification
Expected: sequence contiguous, hashes valid, event ordering valid.

### TC-18 Historical preservation
Expected: epoch N and N+1 decisions remain immutable and queryable.

All 18 are mandatory.

---

## 19. Negative Security Cases

The implementation MUST also include deterministic rejection cases:

### NS-01 Subject attempts direct lifecycle-state mutation
Expected: denied/unavailable.

### NS-02 Subject attempts direct protected-resource mutation
Expected: denied/unavailable through test security boundary.

### NS-03 Forged trigger observation
Expected: rejected.

### NS-04 Forged R13 evaluation
Expected: rejected.

### NS-05 Forged R14 state decision
Expected: rejected.

### NS-06 Capability action-digest substitution
Expected: rejected.

### NS-07 Capability epoch substitution
Expected: rejected.

### NS-08 Audit history mutation
Expected: verification failure.

These cases may be implemented through fixture-level adversarial calls rather than OS-level hostile processes, provided the boundary being claimed is stated precisely.

---

## 20. Evidence Requirements

Formal-run evidence directory should contain at minimum:

```text
run_record.json
profile_v1.json
profile_v2.json
initial_runtime_evidence.json
post_change_runtime_evidence.json
trigger_observation.json
r13_eval_initial.json
r13_eval_invalidated.json
r13_eval_restored.json
r14_state_N.json
r14_state_N1.json
r14_state_N2.json
capability_C1.json
capability_C2.json
execution_C1_denial.json
execution_C2_success.json
audit_ledger.jsonl
audit_verification.json
test_results.json
evidence_manifest.json
```

Every evidence file MUST be hashed in the evidence manifest.

---

## 21. Run Record

```text
RunRecord {
    run_id
    design_version
    implementation_commit
    frozen_parent_commit
    started_at
    completed_at

    subject_id
    role_id
    trust_domain

    initial_epoch
    invalidated_epoch
    restored_epoch

    test_case_count
    test_case_pass_count
    negative_case_count
    negative_case_pass_count

    enforcement_failures
    deviations[]

    final_classification

    evidence_manifest_sha256
}
```

---

## 22. Required Final Classifications

Exactly one:

```text
CONFORMANCE_LIFECYCLE_POC_PASS
CONFORMANCE_LIFECYCLE_POC_FAIL
INCONCLUSIVE_EVIDENCE_INVALID
STOP_BEFORE_SCORING
```

### PASS requires

- 18/18 required cases PASS
- 8/8 negative cases PASS
- zero unauthorized protected-resource effects
- zero stale-capability effects
- zero replay effects
- valid audit chain
- valid evidence manifest
- no unresolved protocol deviation

Anything less is not PASS.

---

## 23. Stop Conditions

STOP before formal scoring if any of the following occurs:

1. frozen parent artifacts are modified;
2. subject can directly write protected resource;
3. subject can directly mutate lifecycle state;
4. R13 and R14 identity separation is not represented as designed;
5. stale capability is not independently checked at executor boundary;
6. evidence timestamps/order cannot distinguish pre- and post-mutation state;
7. audit chain cannot detect mutation;
8. test harness silently repairs failed state;
9. implementation changes after formal-run start without a new run identity;
10. any mandatory test is skipped.

---

## 24. Determinism Rules

The first PoC MUST avoid nondeterministic dependencies.

Use:

- fixed subject/role/domain identifiers
- fixed test payloads
- local filesystem state
- deterministic canonical serialization
- deterministic key fixtures or generated-once fixture keys committed only if safe for test use
- controlled logical timestamps or one monotonic local clock abstraction
- no network
- no external API
- no external LLM
- no human-in-the-loop decision during the formal run

---

## 25. Implementation Shape

Recommended local structure:

```text
architecture/agent-trust-envelope/
  agent-conformance-local-lifecycle-poc-v0.1/
    conformance/
      canonical.py
      crypto.py
      models.py
      state.py
      trigger.py
      evaluator.py
      lifecycle.py
      authorization.py
      executor.py
      audit.py
    tests/
      test_lifecycle.py
      test_negative.py
      test_audit.py
    fixtures/
      ...
    evidence/
      formal-001/
```

SQLite MAY be used for state/nonce/audit persistence, but the design is implementation-neutral.

---

## 26. Implementation Constraints

- Python standard library preferred.
- If cryptographic signing requires a dependency, use the smallest already-approved dependency available in the repository environment.
- No production secrets.
- No network access required.
- No privileged system modification required for the first PoC unless an explicit stronger enforcement variant is later authorized.
- Tests and formal-run generator must be separate entry points.
- Formal evidence must never be silently overwritten.

---

## 27. Threat Model for This PoC

The PoC specifically tests resistance to:

- stale authorization after material runtime change
- participant omission of material change
- replay of issued capability
- forged lifecycle artifacts
- action substitution
- epoch rollback/substitution
- audit tampering
- restoration without fresh evidence

It does not claim protection against:

- host root compromise
- kernel compromise
- cryptographic library compromise
- physical attacker
- production insider attack
- side channels

---

## 28. Acceptance Invariant

The central acceptance invariant is:

```text
Once epoch N+1 establishes non-conformance,
no capability bound only to epoch N may cause
a governed protected-resource effect.
```

The restoration invariant is:

```text
Authority may return only after fresh post-trigger evidence,
a valid R13 evaluation, and a new R14 lifecycle decision.
```

---

## 29. Formal Run Discipline

The formal run MUST:

1. start from a clean worktree;
2. record implementation commit;
3. verify frozen parent artifact hashes;
4. execute preflight;
5. create a unique run directory;
6. run required cases exactly once for that run identity;
7. write evidence incrementally;
8. write evidence manifest after evidence generation;
9. write final run record;
10. never modify evidence after finalization.

Any rerun uses a new run identifier.

---

## 30. Design Disposition

**Current status:** DESIGN DRAFT — READY FOR ADVERSARIAL REVIEW

No implementation is authorized by this document.

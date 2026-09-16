# ATE Qualification & Admission Local PoC v0.1 — Design

**Status:** DESIGN ONLY — NOT FROZEN — NO FORMAL RUN AUTHORIZED  
**Date:** 2026-09-16  
**Repository:** `fjventura20/development-by-intent`  
**Controlling freeze:** `AGENT-QUALIFICATION-ADMISSION-v0.2.2-FREEZE.md`  
**Target:** deterministic local synthetic R2/A2 proof of concept

---

## 1. Objective

Establish, at minimum cost and without live LLM calls, that the frozen Agent Qualification & Admission v0.2.2 architecture can be enforced end-to-end before a protected local write.

The PoC must demonstrate the complete distinction:

```text
QUALIFICATION
    !=
ADMISSION
    !=
ACTION AUTHORIZATION
    !=
EXECUTION
```

The strongest claim permitted by a successful run is:

> A local governed system can require a currently valid, issuer-authorized, subject-bound qualification and explicit domain admission, bind both into action-specific authorization, recheck current state at the Execution Authorization Point, and prevent protected execution when those prerequisites are invalid.

No claim of general AI trustworthiness, general AI safety, production readiness, or cross-provider identity portability is permitted.

---

## 2. Frozen Inputs

Implementation is controlled by the exact frozen set identified in `AGENT-QUALIFICATION-ADMISSION-v0.2.2-FREEZE.md`.

The formal runner must record the freeze-manifest blob ID and the six frozen specification blob IDs in its evidence output before any scored test runs.

If any controlling frozen blob differs, the runner must stop with:

```text
PRECHECK_FAIL_FROZEN_SPEC_MISMATCH
```

No test result obtained against a changed specification counts toward this PoC.

---

## 3. Scope

```text
Risk class:             R2
Assurance profile:      A2
Trust domain:           local-ate-demo
Role:                   demo-repository-writer
Capability class:       demo-resource-write
Subjects:               Agent A fixture / Agent B fixture
Live LLM calls:          none
Network dependency:     none
External resource:      none
External federation:    none
```

The only governed effect is one deterministic local protected-resource write.

---

## 4. Trust / Privilege Boundary

### 4.1 OS identities

The PoC uses the already established local separation pattern:

```text
ate-requester  — synthetic participant process
ate-authority  — policy / qualification / admission / authorization / trust services
ate-executor   — final capability executor and protected resource owner
```

Logical signing identities remain distinct even when multiple authority roles execute under `ate-authority` for this local PoC.

Required distinct logical keys:

```text
K_POLICY
K_IDENTITY
K_R11_QUALIFICATION
K_R12_ADMISSION
K_AUTHORIZATION
K_TRUST_DECISION
K_AUDIT
K_EXECUTOR_IDENTITY
```

The participant must not possess or read any of these authority keys except its own synthetic identity material needed to prove SubjectBinding.

### 4.2 Protected resource

The protected resource must be inaccessible for mutation by `ate-requester`.

The authoritative protected state is executor-owned and writable only through the trusted executor path.

A successful direct mutation by the requester is an immediate PoC enforcement failure regardless of all other test results.

### 4.3 Trusted code

Trusted verifier/executor code used in the formal run must not be writable by `ate-requester`.

Formal preflight records ownership and mode of trusted code, state databases, key directories, and protected resource.

---

## 5. Deterministic Cryptographic Profile

For the PoC, use one fixed signature and digest profile.

Preferred profile:

```text
Signature: Ed25519
Digest:    SHA-256
Encoding:  canonical JSON
UTF-8:     required
```

Canonical JSON for all security-relevant digests:

```text
sort_keys = true
separators = (",", ":")
ensure_ascii = false
reject NaN / Infinity
UTF-8 bytes
exclude signature field from signed payload
```

Every signed artifact includes:

```text
schema_version
canonical_encoding_version
hash_algorithm
issuer_authority_id
issuer_key_id
signature
```

Artifact-domain separation is mandatory.

Example signing input:

```text
ATE_QUALIFICATION_CREDENTIAL_V1 || canonical_payload_bytes
```

A signature for one artifact class must not validate as another class.

---

## 6. Synthetic Subjects

### 6.1 Agent A

Agent A is the intended eligible subject.

Fixed fixture properties include:

```text
subject_identity_id: agent-a
identity key:        fixture key A
runtime class:       synthetic-runtime-v1
provider:            local-fixture
model:               none
role:                demo-repository-writer
```

Agent A receives a SubjectBinding satisfying the frozen profile.

### 6.2 Agent B

Agent B is the credential-transplant control.

It has a different immutable identity anchor and therefore a different `subject_binding_digest`.

Agent B must never be able to use Agent A's qualification/admission chain.

---

## 7. Frozen Qualification Profile Fixture

The PoC defines exactly one recognized qualification profile:

```text
profile_id:              qa-demo-writer
profile_version:         1
role_id:                 demo-repository-writer
minimum_binding:         SB2
maximum_eligible_risk:   R2
eligible_capabilities:   [demo-resource-write]
qualification_duration:  deterministic test interval
```

Required evidence classes are intentionally synthetic but signed and independently verifiable:

```text
identity evidence
runtime/provenance fixture evidence
governance compatibility fixture evidence
operational-control compatibility evidence
```

Behavioral evidence is represented by a deterministic fixture receipt sufficient only for this synthetic PoC. No live behavioral benchmark is performed.

---

## 8. Admission Policy Fixture

Exactly one active admission policy controls `local-ate-demo`.

It explicitly recognizes:

```text
qualification authority: R11 fixture authority
qualification domain:    local-qa-demo
role:                    demo-repository-writer
profile:                 qa-demo-writer version 1 exact digest
maximum risk:            R2
capability class:        demo-resource-write
```

The policy must reject:

- unknown qualification issuers;
- unrecognized qualification profile digests;
- a syntactically newer `qa-demo-writer` version 2 unless explicitly added;
- role mismatch;
- SubjectBinding mismatch;
- expired/revoked/unusable qualification.

---

## 9. Persistent State

Use SQLite with WAL and full synchronous durability for the local PoC.

The state model must include at least:

```text
trust_root_entries
active_policy_state
revocations
qualification_decisions
qualification_credentials
admission_decisions
admission_credentials
capability_tokens
trust_decisions
nonces_or_execution_reservations
audit
protected_resource_state (executor boundary only)
```

Security-sensitive current-state updates increment a monotonic `registry_epoch` or equivalent authoritative trust-state epoch.

A trust-state snapshot/reference used for one decision must be coherent: all of its component state must correspond to one authoritative transaction/snapshot.

Mixed-epoch assembly is prohibited.

---

## 10. Immutable Artifacts vs Current State

QualificationCredential and AdmissionCredential are immutable signed issuance artifacts.

Lifecycle state is external.

A credential is usable only when:

```text
signature valid
AND issuer currently authorized
AND within validity interval
AND not suspended
AND not revoked
AND not hard-superseded
AND all controlling dependencies usable
AND current SubjectBinding proof matches
```

No credential is edited in place to change status.

---

## 11. Qualification Flow

Required deterministic gates:

```text
QG0  schema/canonicalization
QG1  profile issuer authorization
QG2  profile currentness
QG3  SubjectBinding validity
QG4  evidence manifest integrity
QG5  evidence signatures + issuer authorization
QG6  evidence current state
QG7  completeness
QG8  freshness
QG9  behavioral fixture requirement
QG10 governance compatibility
QG11 operational-control compatibility
QG12 assurance/risk ceiling
QG13 suspension/disqualification
QG14 coherent trust-state reference
QG15 final decision
```

Only `QUALIFICATION_GRANTED` may produce a QualificationCredential.

---

## 12. Admission Flow

Required deterministic gates:

```text
AG0  schema/canonicalization
AG1  admission policy issuer authorization
AG2  admission policy currentness
AG3  QualificationCredential integrity/issuer validity
AG4  qualification currentness/dependency state
AG5  trust-domain recognition
AG6  exact qualification profile recognition
AG7  exact role match
AG8  exact SubjectBinding match
AG9  admission manifest integrity
AG10 approvals valid/current
AG11 risk ceiling
AG12 capability class intersection
AG13 separation of duties
AG14 incident/suspension state
AG15 coherent trust-state reference
AG16 final decision
```

Only `ADMISSION_GRANTED` may produce an AdmissionCredential.

---

## 13. Action Authorization Binding

A CapabilityToken for the protected write must bind at least:

```text
subject_binding_digest
qualification_credential_id
qualification_credential_digest
admission_credential_id
admission_credential_digest
session_identity
operation = write
target = protected-resource
parameters_digest
risk = R2
capability_class = demo-resource-write
nonce
issued_at
expires_at
```

The TrustDecision binds the same eligibility chain plus:

```text
capability_token_id
requested_action_digest
coherent trust_state_reference
verdict
issued_at
expires_at
```

Unsigned side-channel eligibility flags are forbidden.

---

## 14. Execution Authorization Point

For the local PoC, EAP is defined as the final serialized critical section in which the executor:

1. verifies TrustDecision and CapabilityToken signatures/bindings;
2. verifies exact qualification/admission credential IDs and digests;
3. resolves their current dependency state;
4. verifies live SubjectBinding;
5. verifies all relevant expirations;
6. verifies current revocation state;
7. reserves the nonce/execution exactly once;
8. records `EAP_REACHED` audit evidence;
9. commits the single protected mutation.

Steps 3 through 9 must occur under one serializable transaction/lock or an equivalent deterministic exclusion mechanism.

If invalidating state is effective and observable before EAP, the write must not occur.

---

## 15. Audit Model

Every consequential state transition emits an audit record external to participant control.

Minimum event families:

```text
QUALIFICATION_EVALUATED
QUALIFICATION_GRANTED
QUALIFICATION_DENIED
QUALIFICATION_CREDENTIAL_ISSUED
ADMISSION_EVALUATED
ADMISSION_GRANTED
ADMISSION_DENIED
ADMISSION_CREDENTIAL_ISSUED
CAPABILITY_ISSUED
TRUST_GRANTED
TRUST_DENIED
REVOCATION_PUBLISHED
REVOCATION_OBSERVED
EXECUTION_BLOCKED_ELIGIBILITY
EAP_REACHED
EXECUTION_SUCCEEDED
EXECUTION_DENIED
DIRECT_BYPASS_DENIED
```

Audit rows are sequence-numbered and hash chained.

The formal runner verifies the chain after every test case or resets to a fresh isolated case database whose final chain is independently verified.

---

## 16. Test Isolation

Each QA-P case runs from an independently initialized deterministic fixture state.

Tests must not depend on execution order except QA-P11, whose ordering is the property being tested.

Fixture reset must create a new test database/resource state rather than mutating historical evidence from a previous case.

Each case records:

```text
test_id
fixture_id
initial protected-resource value
final protected-resource value
starting trust-state epoch
ending trust-state epoch
qualification credential id/digest if present
admission credential id/digest if present
capability id if present
trust decision id if present
verdict / reason code
EAP reached? true/false
mutation count
audit chain valid? true/false
```

---

## 17. Mandatory QA-P1 … QA-P14 Matrix

### QA-P1 — Happy path

Setup: Agent A qualified, admitted, current, and correctly bound.

Expected:

```text
QUALIFICATION_GRANTED
ADMISSION_GRANTED
CAPABILITY_ISSUED
TRUST_GRANTED
EAP_REACHED exactly once
protected mutation count = 1
final resource value = expected value
audit chain valid
```

### QA-P2 — Qualified but not admitted

Setup: valid Agent A QualificationCredential; no usable AdmissionCredential.

Expected: capability issuance denied; EAP not reached; protected resource unchanged.

### QA-P3 — Admission revoked before new capability

Setup: previously admitted Agent A; revoke AdmissionCredential before requesting a new CapabilityToken.

Expected: capability issuance denied; resource unchanged.

### QA-P4 — Admission revoked after capability issuance but before EAP

Setup: issue capability/trust path while admission is active; publish admission revocation before executor EAP.

Expected: final current-state recheck denies; EAP not crossed; resource unchanged.

### QA-P5 — Qualification revoked after capability issuance but before EAP

Same pattern as QA-P4, targeting the QualificationCredential.

Expected: derived invalidation of admission chain; execution denied; resource unchanged.

### QA-P6 — Qualification expiration after capability issuance but before EAP

Use injected deterministic clock. Capability and TrustDecision remain nominally unexpired while QualificationCredential reaches expiry before EAP.

Expected: downstream validity cannot outlive qualification; execution denied; resource unchanged.

### QA-P7 — Agent B reuses Agent A chain

Agent B presents Agent A's qualification/admission/capability chain.

Expected: live SubjectBinding mismatch; deny before EAP; resource unchanged.

### QA-P8 — Unauthorized qualification issuer

Construct a mathematically valid QualificationCredential signed by a key not authorized for the qualification artifact class.

Expected: deny based on issuer authorization, not signature mathematics.

### QA-P9 — Mixed/incoherent trust-state view

Construct a decision attempt using components from different trust-state epochs/snapshots.

Expected: `*_TRUST_STATE_INCONSISTENT`; no usable credential/grant; no EAP.

### QA-P10 — Canonical payload/digest substitution

After a signed/digest-bound artifact is created, alter a security-relevant field or provide semantically similar but differently canonicalized data.

Expected: canonical/digest/signature verification fails closed.

### QA-P11 — Deterministic revocation/EAP ordering

Two subcases are required:

```text
A: revocation transaction commits before EAP lock/transaction -> DENY, no mutation
B: EAP commits protected local mutation before later revocation -> exactly one authorized mutation; later revocation blocks subsequent actions
```

Audit evidence must reconstruct the ordering unambiguously.

This test does not claim retroactive cancellation after EAP.

### QA-P12 — Direct protected-resource bypass

Run a write attempt as `ate-requester` without the trusted executor path.

Expected: OS/resource denial and unchanged protected state.

Any successful direct mutation classifies the entire PoC as `ENFORCEMENT_FAILURE`.

### QA-P13 — Unrecognized newer qualification profile

Create a correctly signed qualification under `qa-demo-writer` version 2 / different digest while AdmissionPolicy recognizes only exact v1 constraints.

Expected: `AX_QUALIFICATION_PROFILE_UNRECOGNIZED`; admission denied.

### QA-P14 — Admission expiry / review boundary

Use deterministic clock so old AdmissionCredential expires.

Expected:

```text
old admission unusable
no timestamp extension in place
new AdmissionDecision required
new AdmissionCredential required
new credential has distinct id/digest
old credential remains historical evidence
```

After valid re-admission, a fresh action may succeed through the normal ATE path.

---

## 18. Formal Acceptance Rule

The formal classification is exactly one of:

```text
QUALIFICATION_ADMISSION_LOCAL_POC_PASS
QUALIFICATION_ADMISSION_LOCAL_POC_FAIL
ENFORCEMENT_FAILURE
INVALID_RUN
```

`PASS` requires all QA-P1 through QA-P14 to satisfy expected results, all audit chains to verify, and preflight/frozen-spec checks to pass.

`ENFORCEMENT_FAILURE` controls if either occurs:

- direct requester protected-resource mutation succeeds; or
- an invalidating state effective/observable before EAP still allows protected mutation.

`INVALID_RUN` applies when frozen inputs, environment prerequisites, or evidence integrity cannot be established.

No partial-pass label is permitted for the formal run.

---

## 19. Evidence Output

The runner must emit deterministic machine-readable evidence, preferably JSON, containing:

```text
run_id
run_timestamp
implementation_commit
freeze_manifest_blob
frozen_spec_blobs{}
environment_preflight{}
key_ids{}
canonicalization_profile
per_test_results[]
overall_classification
audit_chain_verification
protected_resource_bypass_result
deviations[]
```

Human-readable closeout is generated from the preserved evidence; it is not the primary evidence source.

---

## 20. Preflight STOP Conditions

Formal execution stops before QA-P1 if any of the following is true:

- frozen blob mismatch;
- requester can write trusted code;
- requester can read authority/executor private keys;
- requester can directly write the protected resource;
- required OS identities are unavailable;
- trusted executor boundary cannot be established;
- canonicalization/signature implementation self-tests fail;
- database cannot provide the required serialized EAP/current-state behavior;
- audit chain self-test fails.

Preflight failure is `INVALID_RUN`, not a failed architecture test.

---

## 21. Implementation Layout

Recommended new path:

```text
architecture/agent-trust-envelope/qualification-admission-local-poc-v0.1/
    README.md
    qa_poc/
        __init__.py
        canonical.py
        crypto.py
        artifacts.py
        fixtures.py
        state.py
        qualification.py
        admission.py
        authorization.py
        executor_client.py
        audit.py
        clock.py
    trusted/
        executor_service.py
        resource_admin.py
    tests/
        test_qa_matrix.py
        test_preflight.py
    run_formal.py
    evidence/
```

The implementation may reuse reviewed P1 primitives, but reused code must be copied or imported in a way that preserves a fixed implementation identity for the formal run.

---

## 22. Implementation Discipline

Sequence:

```text
this design
-> adversarial review
-> corrected design if required
-> design freeze
-> implementation
-> local deterministic dry run
-> formal preflight
-> formal QA-P1..QA-P14 run
-> evidence lock
-> closeout
```

No live agent or premium evaluator is needed.

No requirement may be weakened during implementation to make a failing test pass.

If implementation reveals a design defect, stop and return to design review.

---

## 23. Design Review Questions

The adversarial review must attack at least:

1. Does QA-P11 define EAP ordering without claiming impossible retroactive revocation?
2. Can a stale pre-issued TrustDecision bypass qualification/admission revocation?
3. Can admission survive unusable qualification through caching or stale snapshots?
4. Can a forged-but-valid signature pass without issuer authorization?
5. Can Agent B satisfy Agent A SubjectBinding through fixture aliasing?
6. Can AdmissionPolicy accidentally accept future profile versions?
7. Can downstream expiry exceed upstream eligibility through clock or cache behavior?
8. Does test isolation hide persistent-state or replay defects?
9. Is the direct-bypass test an actual OS/resource boundary test rather than a cooperative API check?
10. Is audit evidence sufficient to prove revocation-vs-EAP ordering?
11. Are logical authority keys distinct even if authority services share one OS identity?
12. Can the participant influence profile/policy selection or canonicalization?

---

## 24. Current Disposition

```text
Design version:          v0.1
Status:                  DRAFT / NOT FROZEN
Frozen protocol changed: NO
Implementation started:  NO
Formal run authorized:   NO
Hermes/model calls:      NOT REQUIRED
Next step:               ADVERSARIAL DESIGN REVIEW
```

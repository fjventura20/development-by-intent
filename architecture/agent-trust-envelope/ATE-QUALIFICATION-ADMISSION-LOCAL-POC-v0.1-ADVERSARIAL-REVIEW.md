# ATE Qualification & Admission Local PoC v0.1 — Adversarial Design Review

**Reviewed artifact:** `ATE-QUALIFICATION-ADMISSION-LOCAL-POC-v0.1-DESIGN.md`  
**Review date:** 2026-09-16  
**Disposition:** CORRECTION REQUIRED BEFORE DESIGN FREEZE  
**Frozen Agent Qualification & Admission v0.2.2 changed:** NO

---

## 1. Review Objective

Attack the PoC design for ways an implementation could produce a nominal 14/14 PASS without actually establishing the frozen qualification/admission architecture.

The review focuses on privilege boundaries, current-state semantics, EAP ordering, canonicalization, SubjectBinding, audit evidence, and policy selection.

---

## 2. Findings Summary

| ID | Severity | Finding | Required correction |
|---|---|---|---|
| POC-R1 | HIGH | Protected resource placement is ambiguous | Put mutable resource state in an executor-owned enforcement store inaccessible to requester/authority direct SQL |
| POC-R2 | HIGH | EAP transaction boundary is underspecified across trust state/resource state | Serialize revocation application, nonce reservation, EAP audit, and protected mutation in one executor-owned transactional boundary |
| POC-R3 | HIGH | QA-P10 incorrectly suggests alternate serialization of the same object should fail | Same semantic object must canonicalize identically; only semantic mutation or invalid/ambiguous input fails |
| POC-R4 | MEDIUM | Snapshot/current-state semantics are not precise enough | Separate historical decision snapshot from executor current-state recheck and define epoch rules |
| POC-R5 | MEDIUM | Authority/requester direct database mutation paths are not explicitly prohibited | Only executor-side trusted commands may mutate enforcement state; authority supplies signed control records |
| POC-R6 | MEDIUM | Audit ownership/ingestion is vague | Make tamper-evident ledger executor-side and participant-inaccessible; authority events enter through verified trusted append path |
| POC-R7 | MEDIUM | Candidate could potentially influence active profile/policy selection | Services resolve current profile/policy from authoritative role/domain mapping; candidate cannot nominate a weaker version |
| POC-R8 | MEDIUM | Unauthorized issuer test could be too weak if issuer is wholly unknown | Use a recognized key authorized for another artifact class but not QualificationCredential |
| POC-R9 | MEDIUM | QA-P11 race may be timing-dependent/flaky | Use deterministic barriers/locks to force both orderings |
| POC-R10 | MEDIUM | Canonical JSON profile leaves numeric/string ambiguity | Forbid floats; normalize strings; reject duplicate keys and unsupported types |
| POC-R11 | LOW | SubjectBinding fixture does not prove production key custody | State explicitly that QA-P7 proves transplant rejection given uncompromised identity anchors, not key-theft resistance |
| POC-R12 | LOW | Expiry tests need a single authoritative deterministic clock | Inject one clock into authority and executor logic; no wall-clock sleeps |

No finding requires a change to the frozen v0.2.2 architecture.

---

## 3. POC-R1 — Protected Resource Placement

### Severity

HIGH

### Problem

The draft persistent-state list can be read as placing `protected_resource_state` in the same general state database as qualification/admission/control-plane data.

That creates two failure modes:

1. `ate-authority` may gain an unintended direct mutation path to the protected resource;
2. QA-P12 could become merely a cooperative API test rather than a privilege-boundary test.

### Required correction

Use an executor-owned enforcement store whose parent directory and database are inaccessible for direct write by both `ate-requester` and `ate-authority`.

Mutable enforcement tables include only what must be serialized at the final boundary, for example:

```text
applied_revocations
execution_nonces
protected_resource
audit
```

Qualification/admission artifacts remain signed immutable objects outside direct mutable resource state.

---

## 4. POC-R2 — EAP / Revocation Atomicity

### Severity

HIGH

### Problem

If revocation lives in an authority database while resource mutation lives in a separate executor database, a transaction cannot automatically serialize both.

A test could therefore pass most cases while leaving an untested TOCTOU gap.

### Required correction

The executor must apply verified signed revocation/control records into its own enforcement store.

For local PoC EAP:

```text
BEGIN IMMEDIATE / equivalent exclusive write serialization
    read current applied revocation state
    validate bound eligibility dependencies
    validate expirations with injected clock
    reserve nonce
    append EAP_REACHED audit row
    update protected resource
    append EXECUTION_SUCCEEDED audit row
COMMIT
```

Revocation application uses the same serialization boundary.

Therefore exactly one ordering controls:

```text
revocation commits first -> EAP sees revoked -> DENY
EAP commits first         -> one mutation -> later revocation blocks subsequent actions
```

---

## 5. POC-R3 — Canonicalization Semantics

### Severity

HIGH

### Problem

The draft QA-P10 language says “semantically similar but differently canonicalized data” should fail.

That is backwards for canonicalization.

Two valid representations that parse to the same supported data model must produce the same canonical bytes/digest.

### Required correction

QA-P10 must test three distinct properties:

1. reordered object keys / insignificant whitespace -> same parsed object -> same canonical digest;
2. security-relevant semantic mutation -> different canonical digest/signature failure -> DENY;
3. ambiguous/unsupported JSON such as duplicate keys or floats -> parser rejection -> DENY.

---

## 6. POC-R4 — Historical Snapshot vs Current State

### Severity

MEDIUM

### Problem

A TrustDecision must bind the coherent trust-state view used when issued, but EAP must also consult current state.

Requiring exact epoch equality at EAP would incorrectly reject harmless later state changes. Ignoring later epochs would miss revocation.

### Required correction

Define:

```text
decision_snapshot = coherent immutable evidence of state used for issuance
executor_current_state = authoritative applied state at EAP
```

At EAP the executor verifies decision snapshot integrity, then independently re-evaluates the bound qualification/admission dependencies against current applied state.

Current epoch may be greater than the decision epoch. Greater epoch alone is not denial; an invalidating current dependency state is.

---

## 7. POC-R5 — No Direct Enforcement-State Mutation

### Severity

MEDIUM

### Problem

If `ate-authority` can directly edit executor tables, separation of duties is weakened and QA-P11 ordering can be manipulated outside the trusted interface.

### Required correction

Neither requester nor authority receives SQL/file write access to the executor enforcement store.

Authority issues signed control records. A trusted executor-side apply function verifies artifact type, signature, issuer authorization, monotonic epoch, and target before mutating enforcement state.

---

## 8. POC-R6 — Audit Plane

### Severity

MEDIUM

### Problem

The draft requires durable audit but does not state who owns the authoritative chain.

### Required correction

The authoritative PoC audit ledger is stored in the executor-owned enforcement store or an equivalently protected audit store.

Authority-side events are appended through a trusted audit-ingest interface that verifies the signed source artifact and records its digest.

`ate-requester` cannot rewrite, delete, truncate, or directly append authoritative rows.

---

## 9. POC-R7 — Profile/Policy Selection

### Severity

MEDIUM

### Problem

A malicious candidate must not be able to submit an old/weaker profile identifier and cause the service to evaluate against it.

### Required correction

Qualification accepts role/domain intent and evidence only. The Qualification Authority resolves the current profile from authoritative mapping.

Admission similarly resolves the current AdmissionPolicy from trust domain + role.

The candidate may reference expected identifiers for binding, but those references never choose the controlling policy.

---

## 10. POC-R8 — Unauthorized Issuer Test Strength

### Severity

MEDIUM

### Problem

A credential signed by an entirely unknown key only proves unknown-key rejection.

The frozen claim is stronger: a mathematically valid signature from a known but unauthorized issuer must fail.

### Required correction

For QA-P8, use a key that is present and active in the Trust Root Registry for another artifact class (for example Identity/Runtime evidence) but has no permission to sign `QualificationCredential`.

Expected result is issuer-role/artifact-class denial.

---

## 11. POC-R9 — Deterministic QA-P11 Ordering

### Severity

MEDIUM

### Problem

Wall-clock race tests are flaky and do not prove which transaction won.

### Required correction

Use explicit synchronization barriers in the formal test fixture so the two subcases force:

```text
A: revocation COMMIT -> release EAP
B: EAP COMMIT -> release revocation
```

Audit sequence/epoch evidence must match the forced ordering.

---

## 12. POC-R10 — Canonical Data Model

### Severity

MEDIUM

### Problem

JSON numeric and Unicode corner cases can undermine deterministic digest comparison.

### Required correction

Security-relevant PoC payloads permit only:

```text
null
boolean
signed integer within implementation-defined safe range
UTF-8 string normalized to NFC
array
object with unique string keys
```

Floats are prohibited. Duplicate object keys are rejected during parse. Unsupported values fail closed.

Signing input is unambiguous:

```text
UTF8(domain_separator) || 0x00 || canonical_json_bytes
```

---

## 13. POC-R11 — SubjectBinding Claim Boundary

### Severity

LOW

### Problem

Agent A and Agent B are synthetic fixtures. If the same privileged test orchestrator owns both fixture private keys, the test cannot establish real-world key-custody resistance.

### Required correction

QA-P7 should claim only:

> Given distinct uncompromised identity anchors, the verifier rejects transplantation of Agent A's qualification/admission chain to a live proof made by Agent B.

Key theft and hardware-backed identity custody remain explicit non-claims.

---

## 14. POC-R12 — Deterministic Time

### Severity

LOW

### Problem

QA-P6 and QA-P14 are boundary tests. Wall-clock sleeps add nondeterminism.

### Required correction

All protocol time validation uses a shared injected `TestClock` in deterministic tests. Formal evidence records each clock transition.

No scored test relies on real-time sleeping.

---

## 15. Preserved Strengths

The draft correctly preserves the following and they should not be weakened during correction:

- exact frozen QA-P1 through QA-P14 coverage;
- no live LLM requirement;
- distinct qualification/admission/action authorization layers;
- explicit SubjectBinding;
- exact credential ID/digest binding into CapabilityToken and TrustDecision;
- fail-closed current-state semantics;
- explicit EAP concept;
- direct bypass as controlling enforcement failure;
- exact qualification profile recognition;
- deterministic admission reissuance after expiry;
- machine-readable evidence as primary evidence.

---

## 16. Required Corrected Design

The corrected design should make the runtime topology explicit:

```text
ate-requester
    |
    | evidence/action requests only
    v
ate-authority
    |  signs qualification/admission/capability/trust artifacts
    |  signs revocation/control records
    v
trusted executor-side verification/apply boundary
    |
    v
executor-owned enforcement.db
    - applied revocations + epoch
    - nonce reservations
    - protected resource
    - authoritative audit chain
```

The participant and authority must have no direct SQL/file mutation path into `enforcement.db`.

---

## 17. Review Disposition

```text
Frozen v0.2.2 architecture:   PRESERVED
PoC concept:                  ACCEPTABLE
v0.1 PoC design:              CORRECTION REQUIRED
Critical findings:            0
High findings:                3
Medium findings:              7
Low findings:                 2
Implementation authorized:    NO
Formal run authorized:        NO
Next step:                    CORRECT DESIGN -> FINAL ADVERSARIAL PASS
```

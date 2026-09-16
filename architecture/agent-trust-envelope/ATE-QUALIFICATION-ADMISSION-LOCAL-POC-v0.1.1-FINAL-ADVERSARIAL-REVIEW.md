# ATE Qualification & Admission Local PoC v0.1.1 — Final Adversarial Review

**Reviewed artifact:** `ATE-QUALIFICATION-ADMISSION-LOCAL-POC-v0.1.1-DESIGN.md`  
**Review date:** 2026-09-16  
**Disposition:** PASS AFTER FOUR SURGICAL CORRECTIONS  
**Frozen Agent Qualification & Admission v0.2.2 changed:** NO

---

## 1. Summary

The v0.1.1 design closes the high-severity issues identified in the first review. The remaining findings are specification precision issues, not architectural defects.

No additional experiment, model call, or broad design branch is justified.

---

## 2. Findings

### F1 — Executor/Audit key ownership wording is inconsistent

**Severity:** MEDIUM

Section 5 correctly assigns executor/audit private keys to `ate-executor`, while Section 6 can be read as placing all listed logical authorities under `ate-authority`.

**Correction:** explicitly partition custody:

```text
ate-authority:
  AUTH_POLICY
  AUTH_IDENTITY
  AUTH_R11_QUALIFICATION
  AUTH_R12_ADMISSION
  AUTH_AUTHORIZATION
  AUTH_TRUST_DECISION

ate-executor:
  AUTH_EXECUTOR
  AUTH_AUDIT
```

Logical identity remains distinct for every role.

---

### F2 — Revocation effectiveness must be tied to serialized application

**Severity:** MEDIUM

The design distinguishes authority-issued signed control records from executor-applied state but does not make the execution-effective moment normative enough.

A signed record sitting in transit must not create an ambiguous claim that revocation was already effective before EAP.

**Correction:** for this PoC, a revocation/control change becomes authoritative for execution when `apply_control_record()` commits it into the executor-owned enforcement store and increments the applied epoch.

Formal terminology:

```text
issued_at             = authority signed the control record
applied_at            = executor committed the record
applied_epoch         = resulting authoritative execution-state epoch
effective_for_execution = applied_at / applied_epoch
```

The PoC does not support backdated execution-effective revocations.

This precisely matches the frozen rule: invalidating state effective and observable by the authoritative execution trust-state system before EAP must block EAP.

---

### F3 — Denial audit must survive rollback without mutating authorization state

**Severity:** LOW

A failed EAP transaction must roll back nonce/resource/EAP rows, but the denial still needs durable evidence.

**Correction:** on EAP validation failure:

1. roll back the execution transaction;
2. append `EXECUTION_DENIED` in a separate trusted audit transaction;
3. include the observed `current_epoch`, action digest, bound credential IDs/digests, and denial reason;
4. do not reserve/consume the action nonce as a successful execution.

A separate optional attempt identifier may prevent duplicate denial logging; it is not an execution grant.

---

### F4 — `EAP_REACHED` is authoritative only on transaction commit

**Severity:** LOW

The design places `EAP_REACHED` before resource update inside the transaction. If the transaction later rolls back, the event must not survive as if EAP succeeded.

**Correction:** `EAP_REACHED` and `EXECUTION_SUCCEEDED` are committed atomically with the protected mutation. If the transaction rolls back, neither authoritative success event exists.

This preserves:

```text
committed EAP_REACHED <=> protected local mutation committed
```

for this PoC.

---

## 3. Re-check of First Review Findings

```text
POC-R1 protected resource placement         CLOSED
POC-R2 EAP/revocation atomicity             CLOSED
POC-R3 canonicalization semantics           CLOSED
POC-R4 historical vs current state          CLOSED
POC-R5 direct enforcement-state mutation    CLOSED
POC-R6 audit ownership                      CLOSED subject to F3/F4 wording
POC-R7 authoritative policy selection       CLOSED
POC-R8 unauthorized issuer strength         CLOSED
POC-R9 deterministic race ordering          CLOSED
POC-R10 canonical data model                CLOSED
POC-R11 SubjectBinding claim boundary       CLOSED
POC-R12 deterministic clock                 CLOSED
```

---

## 4. Final Security Assessment

After F1–F4 are incorporated, the design provides a coherent local test architecture for all frozen QA-P1…QA-P14 cases.

Most importantly:

- protected state is outside participant and authority direct-write boundaries;
- revocation and EAP compete on one authoritative serialization point;
- stale signed authorization cannot override newer applied invalidation;
- qualification dependency invalidation propagates through admission at EAP;
- exact profile recognition is enforced;
- canonical digest semantics are deterministic;
- issuer authorization is distinct from signature validity;
- audit evidence can reconstruct ordering;
- the direct-bypass case is an OS/resource test, not a cooperative API check.

---

## 5. Disposition

```text
Critical findings:              0
High findings:                  0
Medium findings:                2
Low findings:                   2
Architectural redesign needed:  NO
Frozen v0.2.2 changes needed:   NO
Implementation authorized now:  NO — incorporate F1-F4 and freeze design first
Next step:                      v0.1.2 FINAL DESIGN -> BLOB LOCK -> IMPLEMENTATION
```

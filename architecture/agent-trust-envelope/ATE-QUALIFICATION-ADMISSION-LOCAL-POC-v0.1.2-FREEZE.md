# ATE Qualification & Admission Local PoC v0.1.2 — Design Freeze

**Status:** FROZEN  
**Freeze date:** 2026-09-16  
**Repository:** `fjventura20/development-by-intent`  
**Implementation authorization:** AUTHORIZED FOR THIS LOCAL SYNTHETIC POC ONLY

---

## 1. Frozen PoC Design

| Artifact | Git blob ID |
|---|---|
| `ATE-QUALIFICATION-ADMISSION-LOCAL-POC-v0.1.2-DESIGN.md` | `48cc34a67a68da573fd96fdbd597ffd85bb7ec90` |

Any content change produces a different blob ID and requires renewed review before formal execution.

---

## 2. Controlling Architecture

This design remains subordinate to the already frozen:

`AGENT-QUALIFICATION-ADMISSION-v0.2.2-FREEZE.md`

No v0.2.2 architecture artifact was modified during PoC design.

The PoC formal runner must verify both freeze layers before scored tests:

1. Agent Qualification & Admission v0.2.2 frozen architecture/specification set;
2. this v0.1.2 PoC design blob.

---

## 3. Review Chain

```text
ATE-QUALIFICATION-ADMISSION-LOCAL-POC-v0.1-DESIGN.md
    -> ATE-QUALIFICATION-ADMISSION-LOCAL-POC-v0.1-ADVERSARIAL-REVIEW.md
    -> ATE-QUALIFICATION-ADMISSION-LOCAL-POC-v0.1.1-DESIGN.md
    -> ATE-QUALIFICATION-ADMISSION-LOCAL-POC-v0.1.1-FINAL-ADVERSARIAL-REVIEW.md
    -> ATE-QUALIFICATION-ADMISSION-LOCAL-POC-v0.1.2-DESIGN.md
    -> this freeze
```

All identified first-pass and final-pass findings were incorporated into v0.1.2.

Open critical findings: 0.  
Open high findings: 0.

---

## 4. Frozen Runtime Boundary

The implementation must preserve:

```text
ate-requester
    -> no authority/executor/audit private keys
    -> no direct enforcement.db write

ate-authority
    -> Policy / Identity / R11 / R12 / Authorization / Trust signing
    -> no direct enforcement.db write

ate-executor
    -> Executor + Audit keys
    -> sole mutable owner of enforcement.db
    -> serialized control-state application and EAP
```

Protected resource mutation occurs only inside the executor-owned enforcement boundary.

---

## 5. Frozen EAP / Revocation Semantics

A signed ControlRecord becomes execution-effective only when the executor-side `apply_control_record()` transaction commits it to the authoritative enforcement store and advances the applied epoch.

`issued_at` alone does not make an in-transit record execution-effective.

EAP and control-record application use the same serialized write boundary.

Required ordering:

```text
control invalidation commits before EAP -> EAP MUST DENY
EAP mutation commits before later invalidation -> one authorized effect may stand; later actions MUST DENY
```

For the local PoC:

```text
committed EAP_REACHED <=> committed protected local mutation
```

---

## 6. Frozen Canonicalization Semantics

Security-relevant payloads:

- deterministic UTF-8 canonical JSON;
- NFC-normalized strings;
- unique string keys;
- no floats;
- duplicate keys rejected;
- SHA-256 digests;
- Ed25519 signatures;
- artifact-domain separation using `domain || 0x00 || canonical_payload`.

Equivalent supported JSON representations canonicalize identically. Semantic mutation or invalid/ambiguous input fails closed.

---

## 7. Frozen Test Matrix

Formal implementation must cover QA-P1 through QA-P14 exactly as defined in the frozen v0.2.2 architecture and elaborated in the v0.1.2 PoC design.

Controlling cases:

```text
QA-P1  happy path
QA-P2  qualified but not admitted
QA-P3  admission revoked before new capability
QA-P4  pre-issued capability + admission revocation before EAP
QA-P5  pre-issued capability + qualification revocation before EAP
QA-P6  upstream qualification expiry before EAP
QA-P7  Agent B credential transplant
QA-P8  valid signature / unauthorized qualification issuer
QA-P9  incoherent trust-state view
QA-P10 canonical payload/digest substitution rules
QA-P11 deterministic revocation/EAP ordering
QA-P12 direct protected-resource bypass
QA-P13 unrecognized future qualification profile
QA-P14 admission expiry / signed re-admission
```

No scored case may be removed or weakened.

---

## 8. Formal Classifications

Exactly one:

```text
QUALIFICATION_ADMISSION_LOCAL_POC_PASS
QUALIFICATION_ADMISSION_LOCAL_POC_FAIL
ENFORCEMENT_FAILURE
INVALID_RUN
```

`ENFORCEMENT_FAILURE` overrides ordinary FAIL if direct requester mutation succeeds or if a control invalidation committed/effective before EAP still permits protected mutation.

---

## 9. Implementation Authorization

This freeze authorizes:

> Implementation and local deterministic validation of the minimal synthetic Qualification & Admission PoC defined by blob `48cc34a67a68da573fd96fdbd597ffd85bb7ec90` against the already frozen v0.2.2 architecture set.

It does not authorize:

- changes to frozen semantics during implementation;
- production deployment;
- external federation;
- live-agent trust claims;
- premium multi-agent experiments;
- weakening the direct OS/resource boundary.

Any implementation-discovered design defect stops the formal run and returns to design review.

---

## 10. Next Step

```text
PoC design:                FROZEN
Implementation:            AUTHORIZED
Formal run:                NOT YET AUTHORIZED
Next milestone:            implement -> local dry run -> preflight -> formal QA-P1..QA-P14
Hermes/model calls:        optional; use only for high-value implementation if needed
```

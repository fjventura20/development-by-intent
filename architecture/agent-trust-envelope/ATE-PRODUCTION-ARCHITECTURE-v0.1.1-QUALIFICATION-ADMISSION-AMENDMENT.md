# ATE Production Architecture v0.1.1 — Qualification/Admission Amendment

**Status:** RECONCILIATION AMENDMENT — NOT INDEPENDENTLY FROZEN  
**Amends:** `ATE-PRODUCTION-ARCHITECTURE-v0.1.md`  
**Required by:** `AGENT-QUALIFICATION-AND-ADMISSION-PROTOCOL-v0.2.1.md`

---

## 1. Purpose

This amendment makes current qualification and trust-domain admission explicit, signed prerequisites in the ATE action path whenever policy requires them.

The production question becomes:

> Given this bound subject/runtime/session, its current qualification and admission, current governance/evidence, this bounded capability, and this requested action, may this specific action cross the execution boundary now?

---

## 2. Component Additions

Add logical components:

```text
Qualification Authority (R11)
Admission Authority (R12)
Qualification Requirements Profile service/policy source
Admission Policy service/policy source
```

These are upstream eligibility controls. They do not replace the ATE Verifier, Authorization Authority, Trust Decision Authority, or Capability Executor.

---

## 3. Updated High-Level Path

```text
Subject / Runtime
      ↓
Qualification evaluation
      ↓
QualificationCredential
      ↓
Trust-domain admission evaluation
      ↓
AdmissionCredential
      ↓
Authorization request
      ↓
CapabilityToken binds exact qualification/admission dependencies
      ↓
ATE Evidence Bundle
      ↓
ATE Verifier checks eligibility + ordinary ATE gates
      ↓
TrustDecision binds exact dependencies + coherent trust state
      ↓
Capability Executor final current-state recheck
      ↓
Execution Authorization Point
      ↓
Protected Resource
```

---

## 4. AgentTrustEnvelope Additions

Where action policy requires qualification/admission, the envelope MUST include or canonically reference:

```text
subject_binding_digest
qualification_credential
admission_credential
qualification_credential_digest
admission_credential_digest
coherent_trust_state_reference
```

All eligibility artifacts must bind to the same intended subject/session/action context.

---

## 5. CapabilityToken Additions

For governed actions requiring qualification/admission, CapabilityToken MUST bind:

```text
subject_binding_digest
qualification_credential_id
qualification_credential_digest
admission_credential_id
admission_credential_digest
```

These fields may be first-class schema fields or one canonical signed constraints object, but they are mandatory and covered by the token signature.

Unsigned database flags or side-channel membership status are not acceptable substitutes.

The requested risk/capability scope must be within the intersection of qualification, admission, role-policy, and action-policy ceilings.

---

## 6. Verification Gate Additions

Insert eligibility gates after trust-root/current-state validation and before final capability/action grant.

Conceptual sequence:

```text
G0  Current revocation/trust state
G1  Trust-root / issuer authority
G2  Runtime + session provenance
G3  SubjectBinding satisfaction
G4  Current QualificationCredential
G5  Current AdmissionCredential + exact qualification dependency
G6  COA acceptance / session binding
G7  Current VA policy compatibility
G8  Behavioral/action-time evidence
G9  Capability scope + eligibility ceilings
G10 Evidence-envelope binding
G11 Freshness / derived expiration
G12 Nonce / replay state
G13 Requested-action canonicalization
G14 Coherent trust-state reference
```

All mandatory gates pass or no execution path exists.

---

## 7. TrustDecision Additions

For actions requiring qualification/admission, TrustDecision MUST bind:

```text
subject_binding_digest
qualification_credential_id
qualification_credential_digest
admission_credential_id
admission_credential_digest
coherent_trust_state_reference
requested_action_digest
capability_token_id
```

Nominal TrustDecision expiry MUST NOT exceed the earliest controlling dependency expiry.

A later revocation/suspension overrides nominal TrustDecision validity before EAP.

---

## 8. Derived Expiration

The effective usability horizon is the minimum of all controlling dependency limits, including qualification/admission.

```text
latest_usable_time = min(
  qualification expiry,
  admission expiry,
  session/freshness limits,
  behavioral evidence limit,
  capability token expiry,
  trust decision expiry,
  other policy-controlled limits
)
```

---

## 9. Executor Validation Additions

Before execution, the Capability Executor verifies at least:

```text
TrustDecision signature / authorized issuer
TRUST_GRANTED
current TrustDecision usability
exact action binding
nonce/replay state
CapabilityToken binding
qualification/admission dependency IDs + digests
current qualification/admission trust state
current relevant issuer-key state
signed live session/SubjectBinding reference
```

The executor does not need to re-run the original qualification evaluation. It verifies the signed dependency chain and current-state conditions.

---

## 10. Execution Authorization Point

Production Architecture adopts:

> **Execution Authorization Point (EAP):** the final authoritative point at which current trust state is validated and the executor commits to attempting the protected effect.

Any invalidating state effective/observable before EAP prevents the action from crossing EAP.

Local transactional resources SHOULD serialize current-state recheck, nonce reservation, EAP, and mutation where practical.

External side effects continue to follow existing ambiguity/idempotency controls.

---

## 11. Updated Security Invariants

Add:

```text
PA-QA-INV-1  QualificationCredential alone grants no action.
PA-QA-INV-2  AdmissionCredential alone grants no action.
PA-QA-INV-3  Required qualification/admission dependencies are signature-bound into CapabilityToken and TrustDecision.
PA-QA-INV-4  SubjectBinding must match the live session/runtime evidence.
PA-QA-INV-5  Admission is unusable when its exact QualificationCredential dependency is unusable.
PA-QA-INV-6  Downstream artifacts cannot outlive controlling eligibility dependencies.
PA-QA-INV-7  Invalidating state effective before EAP blocks execution.
PA-QA-INV-8  Executor bypass remains an architectural failure.
```

---

## 12. PoC Integration

The first qualification/admission PoC SHOULD reuse the existing P1 executor/resource boundary and nonce/audit mechanisms rather than create a parallel enforcement path.

The PoC adds only the minimum new registries/artifacts/evaluation logic needed to prove the eligibility chain.

No live LLM participation is required.

---

## 13. Amendment Disposition

This amendment becomes controlling only when frozen together with the reconciled qualification/admission specification set.

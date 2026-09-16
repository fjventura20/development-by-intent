# Agent Qualification & Admission Protocol v0.1 — ChatGPT Adjudication

**Status:** REVIEW ADJUDICATION — DESIGN ONLY — NO IMPLEMENTATION AUTHORIZATION  
**Date:** 2026-09-16  
**Reviewed draft:** `AGENT-QUALIFICATION-AND-ADMISSION-PROTOCOL-v0.1.md`  
**Codex review:** `AGENT-QUALIFICATION-AND-ADMISSION-PROTOCOL-v0.1-CODEX-ADVERSARIAL-REVIEW.md`  
**Codex disposition:** `NOT_READY_FOR_FREEZE`  
**Authoritative qualification baseline:** `ATE-AGENT-QUALIFICATION-REQUALIFICATION-ARCHITECTURE-v0.1.1.md`

---

## 1. Executive disposition

The Codex disposition is accepted.

The reviewed v0.1 draft is **not suitable for freeze or implementation**.

The dominant problem is architectural duplication: the current ATE baseline already contains a reviewed Agent Qualification & Requalification Architecture that defines scoped qualification, immutable qualified runtime profiles, evidence lifecycle classes, evaluator independence, issuer ceilings, monotonic qualification status, assurance binding, compatibility, re-attestation, requalification, and fail-closed verification.

The v0.1 Qualification & Admission draft independently redefines many of those same concepts and then adds admission. That creates two potential sources of truth.

Therefore the correction strategy is:

> **Do not patch the v0.1 draft into a larger parallel qualification architecture. Preserve it as historical review evidence. Replace it with a narrow trust-domain admission architecture that inherits the existing qualification architecture and adds only the missing domain-participation semantics.**

Recommended next artifact:

`ATE-TRUST-DOMAIN-AGENT-ADMISSION-ARCHITECTURE-v0.1.md`

Only after that architecture survives adversarial review should a lean admission protocol be designed.

---

## 2. Controlling architectural separation

The corrected architecture should preserve the following distinctions:

```text
Qualification
    = evidence-backed eligibility of a principal/runtime profile
      for a bounded class of work.

Trust-Domain Admission
    = a local domain decision that a currently qualified principal/profile
      may participate in that domain within a further narrowed ceiling.

ATE Authorization
    = a current, action-specific trust decision for one governed action.

Capability Execution
    = executor-mediated release/use of authority after all controlling
      dependencies are validated.
```

Formally:

```text
QUALIFIED != DOMAIN_ADMITTED
DOMAIN_ADMITTED != AUTHORIZED_TO_ACT
AUTHORIZED_TO_ACT != EXECUTED
```

Each transition has separate evidence, current state, and enforcement requirements.

---

## 3. Adjudication of blocking findings

### QA-AR-01 — Eligibility withdrawal lacks mandatory end-to-end execution closure

**Disposition:** ACCEPT

The v0.1 draft concentrates too heavily on capability issuance. That is insufficient because already-issued but unexecuted authorization may remain usable after qualification or admission withdrawal.

**Required correction:** qualification and admission become explicit controlling dependencies in capability issuance, trust composition, and executor-side final validation. Suspension, revocation, expiration, incompatible supersession, or admission withdrawal invalidates dependent unexecuted grants. The executor rechecks current dependency state before resource credential release or external effect according to risk/freshness policy.

No claim is made that revocation can undo an already committed irreversible external effect.

---

### QA-AR-02 — Admission/capability ceilings are not proven subsets of qualification

**Disposition:** ACCEPT

Admission must only narrow qualification; it cannot create new capability authority.

**Required correction:** define one coherent effective-eligibility intersection:

```text
effective_eligibility =
    current qualification ceiling
    INTERSECT local admission ceiling
    INTERSECT current local policy ceiling
    INTERSECT issuer/delegation ceilings
```

The intersection covers role, canonical capability classes, operation/target/resource scope, risk, assurance, governance constraints, validity, and explicit exclusions. Exclusions override allows. Unrelated qualification/admission credentials may not be unioned to synthesize a broader grant.

---

### QA-AR-03 — Stable identity does not enforce evaluated-profile/live-runtime continuity

**Disposition:** ACCEPT

This is already solved more precisely by the authoritative qualification architecture through `QualifiedRuntimeProfile` and `VerifiedRuntimeContext`.

**Required correction:** do not invent a new subject-binding model. Admission binds the existing immutable `qualified_profile_digest` plus principal identity and trust-domain scope. A live request must prove the same principal and a compatible current runtime/profile/session through the existing runtime-verification path. Unsupported controlling provenance claims lower eligibility or fail closed according to policy.

---

### QA-AR-04 — Evidence lifetime semantics permit historical tests to become lasting badges

**Disposition:** ACCEPT

This is also already solved by the authoritative qualification architecture.

**Required correction:** inherit its mandatory evidence lifecycle classes exactly:

```text
ISSUANCE_SNAPSHOT
CONTINUOUSLY_CURRENT
PERIODICALLY_REFRESHED
```

Admission does not redefine qualification evidence lifecycle. Loss of continuously-current qualification evidence or a missed mandatory refresh makes qualification unusable according to its current authoritative state, which in turn invalidates dependent admission/action eligibility.

---

### QA-AR-05 — Compatible replacement is an undefined bypass

**Disposition:** ACCEPT

Silent replacement of qualification or admission prerequisites is not acceptable.

**Required correction:** inherit the qualification architecture's signed non-expanding compatibility semantics. Admission binds exact qualification identity/digest. A replacement qualification requires either a new admission decision or a separately signed, narrowly scoped admission-continuation artifact whose policy explicitly proves non-expansion and preserves lineage. Unknown material compatibility fails closed.

No revoked identifier is revived by replacing its bytes.

---

### QA-AR-06 — Admission lacks authoritative monotonic current-state semantics

**Disposition:** ACCEPT

A signed historical `ADMITTED` credential cannot be sovereign.

**Required correction:** define trust-domain admission state as a projection of the existing ATE trust-state plane, not a new independent registry. Minimum state includes an immutable admission identifier, current status, monotonic state/registry epoch, policy digest, observed-at/freshness semantics, and authorized state publisher. Rollback, stale state, ambiguous current state, or unavailable required state fails closed.

A credential's embedded status is historical issuance data only.

---

### QA-AR-07 — Risk ceilings omit assurance eligibility

**Disposition:** ACCEPT

Risk and assurance are separate dimensions.

**Required correction:** admission narrows both the qualification's maximum risk and its qualified assurance capability. Action-time verification checks the authoritative action-required assurance profile against current qualification/admission/runtime/authority conditions. No upward assurance inference is permitted.

---

### QA-AR-08 — New signing authorities lack bounded issuance ceilings and policy ownership

**Disposition:** MODIFY

The defect is accepted; the proposed correction is simplified.

The project should **not automatically introduce globally numbered R11/R12 authority classes**. Qualification already has an authoritative Qualification Authority concept with issuer ceilings. Admission should be modeled as a narrowly delegated trust-domain membership/admission signing permission under the existing trust-root/governance model.

**Required correction:**

- eligibility policy publication/activation remains a Policy Authority function;
- qualification aggregation uses the existing Qualification Authority semantics;
- trust-domain admission uses a root-delegated local admission/membership permission;
- all signing permissions have exact artifact/domain/project/capability/risk/assurance/lifetime ceilings;
- operational signers cannot register themselves, activate their own trust, widen their own ceilings, or manufacture policy authority;
- superior emergency revocation remains available.

A deployment may assign a human-readable authority label to the admission function, but the label itself creates no authority.

---

### QA-AR-09 — Independence and approvals are descriptive rather than enforceable

**Disposition:** ACCEPT

Different keys or role names do not prove independence.

**Required correction:** inherit machine-verifiable evaluator independence rules from qualification. Admission approvals, where required, bind principal/profile, qualification digest, local domain/role, policy digest, ceilings, validity, and approver identity. Required independence is expressed as a policy predicate over compromise/control domains. One administrator/service cannot satisfy multiple independent factors merely by using multiple keys.

Participant control of qualification/admission signing or required approval credentials, including signing-oracle access, is prohibited.

---

### QA-AR-10 — Foreign qualification recognition can launder trust and scope

**Disposition:** MODIFY

The risk is accepted, but v0.1 should avoid unnecessary federation scope.

**Required correction:** initial Trust-Domain Agent Admission Architecture v0.1 is **local-domain only**. Foreign/federated qualification recognition is explicitly out of scope unless the existing full federation contract is invoked unchanged.

Future federation must preserve original provenance, local semantic mapping by digest, non-transitive recognition, current foreign and local relationship state, local narrowing, and local suspension precedence.

No new federation mechanism should be invented in the admission v0.1 artifact.

---

### QA-AR-11 — Artifact issuance/verification contract is not coherent enough

**Disposition:** ACCEPT

The draft mixes decisions and credentials without exact derivation rules.

**Required correction:** reuse the normative ATE artifact encoding/version/domain-separation rules. AdmissionDecision and AdmissionCredential are digest-bound. Credential fields are equal to or narrower than the retained grant decision and controlling policy. Unknown controlling versions/constraints fail closed. Missing/empty semantics are explicit. A versioned signed extension may carry admission dependencies only if every verifier/composer/executor enforces the same semantics.

No second serialization or parallel verification vocabulary is introduced.

---

### QA-AR-12 — Audit cannot reconstruct eligibility causality

**Disposition:** ACCEPT

**Required correction:** admission events are typed extensions of the existing canonical audit/evidence architecture. Audit/evidence must preserve enough immutable material to reconstruct:

```text
principal/profile
qualification identity + digest + current state observation
admission decision + credential digest
local admission policy digest
approvals/compatibility lineage where applicable
state/revocation epochs and freshness observations
capability issuance linkage
ATE trust-decision linkage
executor recheck/execution outcome
```

Required issuance evidence is durable before credential release. If policy requires durable persistence and persistence fails, release fails closed.

---

### QA-AR-13 — Parallel qualification semantics conflict with the existing baseline

**Disposition:** ACCEPT — CONTROLLING FINDING

This is the architectural root cause behind many other findings.

The authoritative ATE Agent Qualification & Requalification Architecture v0.1.1 already defines qualification comprehensively and has passed a final consistency review with disposition `READY_FOR_QUALIFICATION_PROTOCOL_DESIGN`.

**Required correction:** do not evolve the reviewed v0.1 Qualification & Admission draft into a competing qualification specification. Preserve it as historical evidence. The successor artifact inherits qualification by reference and defines only trust-domain admission plus its mandatory integration into capability issuance, trust composition, execution, revocation/current-state, and audit.

The four original PoC cases remain useful smoke diagnostics but are not qualification conformance evidence and are insufficient for an admission architecture freeze.

---

## 4. Adjudication of non-blocking findings

### QA-AR-14 — Non-transferability and delegation should be explicit

**Disposition:** ACCEPT

Standing qualification/admission credentials are public/verifiable evidence, not bearer authority. Copying them grants nothing. No implicit child-agent inheritance, delegation, transfer, redelegation, or cross-session authority exists. A child/new principal requires its own valid qualification/admission/live-context chain unless a future constrained delegation architecture explicitly defines otherwise.

Action-specific ATE authorization remains single-use according to the existing production model; standing eligibility credentials need not be single-use.

---

### QA-AR-15 — Authority numbering and duplicate machinery add unnecessary complexity

**Disposition:** ACCEPT

The next architecture will not create a new root hierarchy, duplicate revocation plane, duplicate evidence archive, duplicate audit ledger, or mandatory separate service solely for admission.

Admission is a logical decision/signing permission integrated into existing ATE control planes. Separation/independence requirements remain policy-driven by risk and assurance.

---

## 5. Root-cause grouping

The 15 findings reduce to four architectural causes.

### RC-1 — Duplicate qualification source of truth

Primary findings:

```text
03, 04, 05, 07, 08, 09, 11, 13, 15
```

Correction: inherit the existing qualification architecture instead of redefining it.

### RC-2 — Admission not yet a first-class controlling dependency

Primary findings:

```text
01, 02, 06, 12
```

Correction: define admission as current, monotonic, bounded, auditable state that participates in capability issuance, trust composition, and executor-side dependency validation.

### RC-3 — Federation scope is premature

Primary finding:

```text
10
```

Correction: keep v0.1 local-domain only; inherit existing federation architecture only in a future explicit extension.

### RC-4 — Transfer/delegation semantics need explicit closure

Primary finding:

```text
14
```

Correction: explicit non-bearer/non-transfer/delegation rules.

---

## 6. Required architecture for the successor

The successor should be an **architecture artifact first**, not an implementation protocol.

Recommended name:

`ATE-TRUST-DOMAIN-AGENT-ADMISSION-ARCHITECTURE-v0.1.md`

Its purpose should be narrowly stated:

> Define how a local ATE trust domain accepts a currently qualified principal/runtime profile as an eligible participant for a bounded role/scope, how that admission remains current or is withdrawn, and how admission becomes a mandatory non-authorizing dependency of action-specific ATE execution.

### 6.1 Inherited, not redefined

The artifact should normatively inherit:

- Agent Qualification & Requalification Architecture v0.1.1;
- Runtime Identity / Attestation architecture;
- Trust Root & Key Custody Model;
- Risk & Assurance Policy Model;
- Revocation & Trust-State Model;
- Trust-Decision Composition architecture;
- Enforcement Plane;
- Audit & Accountability Model;
- Production Requirements & Conformance Profile.

Where conflict exists, the upstream authoritative artifact controls unless the admission artifact explicitly amends it and the amendment is separately reviewed/frozen.

### 6.2 New concepts only

The admission architecture should add only:

```text
AdmissionPolicy
AdmissionDecision
AdmissionCredential
AdmissionStatusState / trust-state projection
AdmissionCeiling
AdmissionContinuation (only if needed)
Admission semantic context/dependency binding
```

It should not redefine:

```text
QualificationDefinition
QualifiedRuntimeProfile
QualificationEvidencePackage
QualificationCredential
QualificationStatusState
Evidence lifecycle classes
Compatibility semantics
Evaluator rules
Qualification issuer ceilings
```

### 6.3 Core admission rule

```text
DOMAIN_ADMITTED only if:
    qualification is currently ACTIVE
    AND live principal/profile binding is valid where required
    AND local admission policy is current
    AND qualification scope satisfies local minimum requirements
    AND requested admission ceiling is a strict subset of qualification ceiling
    AND admission authority is authorized within exact delegated ceilings
    AND required approval/independence predicates pass
    AND current revocation/trust-state observations pass
    AND required audit persistence succeeds
```

### 6.4 Mandatory action-path integration

For any admission-dependent governed action:

```text
qualification dependency
+ admission dependency
+ live runtime/session/governance state
+ capability scope
+ action risk/assurance
+ current policy/revocation state
        |
        v
ATE trust composition
        |
        v
TRUST_GRANTED / TRUST_DENIED
        |
        v
executor final dependency validation
        |
        v
resource effect
```

An old grant is not sovereign if a controlling qualification/admission dependency becomes execution-invalidating before effect.

---

## 7. Minimum admission-specific invariants for the successor

The next architecture should include at least these invariants:

1. **ADMISSION_NARROWS_QUALIFICATION** — admission can only narrow a single coherent current qualification context.
2. **NO_AMBIENT_AUTHORITY** — admission never creates protected resource credentials or action authority.
3. **CURRENT_STATE_REQUIRED** — historical admission signature is insufficient; current authoritative admission state is required.
4. **MONOTONIC_ADMISSION_STATE** — stale ADMITTED state cannot override newer withdrawal/suspension/revocation.
5. **PENDING_EXECUTION_INVALIDATION** — execution-invalidating eligibility loss blocks dependent unexecuted grants.
6. **ASSURANCE_PRESERVED** — admission cannot infer or raise assurance beyond qualification/runtime/authority support.
7. **EXCLUSIONS_WIN** — local/qualification exclusions override allows.
8. **NO_CREDENTIAL_UNION_ESCALATION** — unrelated qualifications/admissions cannot be unioned to produce unsupported authority.
9. **POLICY_OWNER_SEPARATION** — an operational admission signer cannot silently publish/activate its own governing ceiling unless explicitly authorized concentration permits it.
10. **AUTHORIZED_ADMISSION_CEILING** — admission signatures outside issuer delegation are invalid.
11. **NO_IMPLICIT_TRANSFER** — copied credentials, child agents, delegation, ownership changes, and new sessions do not inherit eligibility.
12. **AUDIT_CAUSALITY** — every issued admission and dependent authorization/execution is reconstructable from retained evidence.
13. **LOCAL_ONLY_V0_1** — foreign recognition is outside v0.1 unless the existing federation contract is explicitly invoked.
14. **FAIL_CLOSED_ON_UNKNOWN** — missing/stale/ambiguous/unavailable required admission state cannot satisfy eligibility.
15. **QUALIFICATION_SINGLE_SOURCE** — the authoritative qualification architecture remains the only source of qualification semantics.

---

## 8. Recommended lean review/test boundary

No implementation is authorized by this adjudication.

After the admission architecture is drafted, adversarial review should concentrate on a small set of high-value cases:

```text
A1 valid current qualification + bounded local admission -> eligible for ATE request
A2 qualified but not admitted -> denied before capability issuance
A3 admission wider than qualification -> admission/issuance denied
A4 qualification suspended after token/grant issuance -> pending execution denied
A5 admission withdrawn after token/grant issuance -> pending execution denied
A6 stale/rolled-back ADMITTED state -> denied
A7 wrong principal/profile presents admission -> denied
A8 action requires assurance above qualification/admission support -> denied
A9 unauthorized/out-of-ceiling admission signer -> denied
A10 required audit/current-state service unavailable -> fail closed
```

These are architecture/conformance cases, not model-behavior experiments, and require no premium multi-agent run.

---

## 9. Final adjudication

```text
CODEX REVIEW: ACCEPTED
V0.1 DRAFT: NOT_READY_FOR_FREEZE
IMPLEMENTATION: NOT AUTHORIZED
PATCH-IN-PLACE: REJECTED
SUCCESSOR STRATEGY: CLEAN NARROW ARCHITECTURE
NEXT ARTIFACT: ATE-TRUST-DOMAIN-AGENT-ADMISSION-ARCHITECTURE-v0.1.md
```

All 13 blocking Codex findings are accepted in substance. Two findings (QA-AR-08 and QA-AR-10) use a modified remediation strategy to minimize new machinery: reuse existing authority/control-plane semantics and keep the first admission architecture local-only. Both non-blocking findings are accepted as useful clarifications/simplifications.

The central Qualification -> Admission -> ATE -> Enforcement idea remains sound. The correction is not to add more machinery; it is to compose the machinery already established and make trust-domain admission a precise, current, enforceable dependency.

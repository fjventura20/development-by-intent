# Agent Qualification & Admission v0.2.2 — Freeze Manifest

**Status:** FROZEN  
**Freeze date:** 2026-09-16  
**Repository:** `fjventura20/development-by-intent`  
**Pre-freeze baseline commit:** `aaba63874ae5f4e4eea93a9b4d85a282fccec4ac`  
**Scope:** qualification/admission protocol plus the five required ATE integration amendments  
**Implementation authorization:** **AUTHORIZED FOR THE FROZEN LOCAL SYNTHETIC POC ONLY**

---

## 1. Controlling Design Set

The following six files are frozen together as one reconciled specification set.

Git blob object IDs are used as content-addressed locks for this freeze. A change to any file creates a different blob ID and therefore constitutes a new specification version requiring explicit review.

| Frozen artifact | Git blob ID |
|---|---|
| `AGENT-QUALIFICATION-AND-ADMISSION-PROTOCOL-v0.2.2.md` | `28b4b0a36e7ded946686c0eb45d4ee820a35c2bf` |
| `ATE-TRUST-ROOT-KEY-CUSTODY-MODEL-v0.1.1-QUALIFICATION-ADMISSION-AMENDMENT.md` | `ce6d11cc4a7271fd2cc6b286d2e01b90e5b3edc1` |
| `ATE-REVOCATION-TRUST-STATE-MODEL-v0.1.1-QUALIFICATION-ADMISSION-AMENDMENT.md` | `ba1761667260c34ebf9018c6719a9555a8cc34fa` |
| `ATE-PRODUCTION-ARCHITECTURE-v0.1.1-QUALIFICATION-ADMISSION-AMENDMENT.md` | `0834105252d8cf0055088eb0d2a572a9c65a17e8` |
| `ATE-RISK-ASSURANCE-POLICY-MODEL-v0.1.1-QUALIFICATION-ADMISSION-AMENDMENT.md` | `908409107d8404ba6aa58367699a9be91a81e84f` |
| `ATE-AUDIT-ACCOUNTABILITY-MODEL-v0.1.1-QUALIFICATION-ADMISSION-AMENDMENT.md` | `6c4863b031d71c8b0fb0a53bf08e9f7547681d20` |

The underlying v0.1 ATE architecture documents remain preserved. These v0.1.1 amendment files layer qualification/admission semantics onto the existing baseline rather than rewriting historical evidence.

---

## 2. Review Chain

The frozen set incorporates the following review sequence:

1. `AGENT-QUALIFICATION-AND-ADMISSION-PROTOCOL-v0.1.md`
2. `AGENT-QUALIFICATION-AND-ADMISSION-PROTOCOL-v0.1-ADVERSARIAL-REVIEW.md`
3. `AGENT-QUALIFICATION-AND-ADMISSION-PROTOCOL-v0.2.md`
4. `AGENT-QUALIFICATION-AND-ADMISSION-PROTOCOL-v0.2-SECOND-ADVERSARIAL-REVIEW.md`
5. `AGENT-QUALIFICATION-AND-ADMISSION-PROTOCOL-v0.2.1.md`
6. five cross-specification reconciliation amendments
7. `AGENT-QUALIFICATION-ADMISSION-RECONCILIATION-REVIEW-v0.1.md`
8. `AGENT-QUALIFICATION-AND-ADMISSION-PROTOCOL-v0.2.2.md`
9. this freeze manifest

No unresolved critical or high-severity design finding remains from that review chain.

---

## 3. Frozen Architectural Claims

The following are controlling for the PoC:

```text
QUALIFICATION != ADMISSION != ACTION AUTHORIZATION
```

Specifically:

- Qualification establishes evidence-backed role eligibility.
- Admission establishes explicit trust-domain participation for that role.
- Neither grants resource authority.
- Protected execution still requires the normal action-specific ATE path.
- Qualification and admission bind to a canonical SubjectBinding.
- Admission binds to the exact QualificationCredential it depends on.
- AdmissionPolicy explicitly recognizes acceptable qualification profile versions/digests; unknown future profiles fail closed.
- CapabilityToken and TrustDecision bind the exact qualification/admission credential IDs and digests.
- Current trust state is evaluated from one coherent state view.
- Invalidating state effective and observable before the Execution Authorization Point (EAP) prevents crossing EAP.
- Downstream nominal validity cannot exceed controlling eligibility validity.
- Participant-held credentials do not replace session-bound COA, current VA checks, or action-time assurance evidence.
- R11 Qualification Authority and R12 Admission Authority are separate logical signing authorities with explicit Trust Root Registry permissions.
- Qualification/admission state transitions and EAP ordering are auditable.

---

## 4. Frozen PoC Scope

The first implementation is deliberately narrow.

```text
Risk class:             R2
Assurance profile:      A2
Trust domain:           local-ate-demo
Role:                   demo-repository-writer
Eligible capability:    demo-resource-write
Subjects:               synthetic Agent A and Agent B fixtures
Live LLM calls:          NONE
External federation:    OUT OF SCOPE
Production PKI:          OUT OF SCOPE
```

The PoC should reuse the existing P1 enforcement/resource boundary wherever practical.

---

## 5. Frozen Test Matrix

The first formal PoC must cover exactly the frozen architecture cases or a strict superset approved before execution:

```text
QA-P1  Happy path -> exactly one protected mutation
QA-P2  Qualified but not admitted -> DENY
QA-P3  Admission revoked before new capability -> DENY
QA-P4  Pre-issued capability after admission revocation before EAP -> DENY
QA-P5  Pre-issued capability after qualification revocation before EAP -> DENY
QA-P6  Qualification expires after capability issuance before EAP -> DENY
QA-P7  Agent B reuses Agent A chain -> SubjectBinding DENY
QA-P8  Valid signature from unauthorized qualification issuer -> DENY
QA-P9  Mixed/incoherent trust-state view -> DENY
QA-P10 Canonical payload/digest substitution -> DENY
QA-P11 Deterministic revocation/EAP ordering -> ordering preserved and auditable
QA-P12 Direct protected-resource bypass -> DENY; any success = enforcement failure
QA-P13 Unrecognized newer qualification-profile version/digest -> admission DENY
QA-P14 Admission expiry/review boundary -> old admission DENY; new signed re-admission required
```

No premium-model replication or live-agent behavioral benchmark is part of this PoC.

---

## 6. Implementation Constraints

Implementation MUST NOT:

- weaken or reinterpret SubjectBinding;
- replace explicit profile recognition with a simple minimum-version rule;
- treat QualificationCredential or AdmissionCredential as a resource capability;
- use unsigned eligibility flags;
- skip issuer authorization because a signature is mathematically valid;
- assemble qualification/admission decisions from incoherent trust-state epochs;
- allow a downstream capability to outlive a controlling eligibility dependency;
- omit final current-state verification before EAP;
- give the synthetic participant authority signing keys or protected-resource credentials;
- bypass the existing enforcement boundary;
- silently modify this frozen specification set.

Any required design change stops the formal run and returns the project to review before testing against the changed semantics.

---

## 7. Evidence Requirements

The formal PoC evidence set must preserve at least:

- implementation commit SHA;
- exact frozen-spec blob IDs from this manifest;
- deterministic fixture/key identities;
- canonicalization/hash profile;
- test output for QA-P1 through QA-P14;
- protected-resource state before/after each relevant case;
- qualification/admission decisions and credential digests;
- coherent trust-state view/epochs;
- EAP ordering evidence;
- audit-chain verification;
- direct-bypass test result;
- deviations, if any.

Formal closeout must classify the PoC honestly. A direct resource bypass or an unauthorized post-revocation crossing of EAP is an enforcement failure regardless of other passing tests.

---

## 8. Authorization Boundary

This freeze authorizes only:

> Design and implementation of the minimal deterministic local synthetic Agent Qualification & Admission PoC conforming to this frozen specification set.

It does not authorize:

- broad production deployment;
- changes to frozen requirements during execution;
- external federation;
- live-agent qualification claims;
- claims of general AI trustworthiness or safety;
- premium multi-agent experiments.

---

## 9. Freeze Disposition

```text
Protocol:                       v0.2.2 FROZEN
Cross-spec amendments:          FROZEN WITH PROTOCOL
Architecture review:            PASS
Reconciliation review:          PASS AFTER v0.2.2 CORRECTIONS
Local synthetic PoC:            AUTHORIZED
Hermes/model calls required:    NO
Next milestone:                 ATE Qualification & Admission Local PoC v0.1
```

Any modification of a frozen artifact requires a new version and review; this manifest continues to identify the exact design against which the authorized PoC is to be built and evaluated.

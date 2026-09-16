# ATE Qualification & Admission Local PoC v0.1.1 — Corrected Design

**Status:** FINAL DESIGN CANDIDATE — NOT YET FROZEN — NO FORMAL RUN AUTHORIZED  
**Date:** 2026-09-16  
**Supersedes for PoC design:** `ATE-QUALIFICATION-ADMISSION-LOCAL-POC-v0.1-DESIGN.md`  
**Required review:** `ATE-QUALIFICATION-ADMISSION-LOCAL-POC-v0.1-ADVERSARIAL-REVIEW.md`  
**Controlling architecture:** `AGENT-QUALIFICATION-ADMISSION-v0.2.2-FREEZE.md`

---

## 1. Objective and Claim Boundary

Build the smallest deterministic local R2/A2 system that can falsify or support the frozen qualification/admission architecture before one protected write.

Required separation:

```text
QUALIFICATION
    != ADMISSION
    != ACTION AUTHORIZATION
    != EXECUTION
```

A successful PoC establishes only that a local enforcement system can require current, issuer-authorized, SubjectBinding-bound qualification and admission, bind those dependencies into action authorization, recheck them at EAP, and prevent execution when they are invalid.

It does not establish general agent trustworthiness, production readiness, key-theft resistance, federation safety, or general AI safety.

---

## 2. Frozen Inputs and Formal Precheck

The formal runner records and verifies:

```text
AGENT-QUALIFICATION-ADMISSION-v0.2.2-FREEZE.md blob
six frozen controlling specification blob IDs
implementation commit SHA
PoC design freeze blob ID
```

Mismatch -> `PRECHECK_FAIL_FROZEN_SPEC_MISMATCH` -> `INVALID_RUN`.

No scored test executes against modified frozen semantics.

---

## 3. Fixed PoC Scope

```text
Risk class:             R2
Assurance profile:      A2
Trust domain:           local-ate-demo
Role:                   demo-repository-writer
Capability class:       demo-resource-write
Subjects:               synthetic Agent A / Agent B
Governed effect:        one local protected-resource write
Live LLM calls:          none
Network calls:           none
External federation:    none
```

---

## 4. Runtime Topology

```text
                           trusted test controller
                         (orchestration only / not subject)
                                  |
             +--------------------+--------------------+
             |                                         |
             v                                         v
      ate-requester                               ate-authority
   Agent A / Agent B                       policy / R11 / R12 /
   identity live proof                     authorization / trust
             |                                         |
             | evidence/action requests                | signed artifacts
             |                                         | signed control records
             +--------------------+--------------------+
                                  |
                                  v
                    trusted executor-side boundary
                    (runs as ate-executor)
                                  |
                                  v
                        executor-owned enforcement.db
                        - applied control state
                        - execution nonces
                        - protected resource
                        - authoritative audit chain
```

The test controller is trusted only to create/reset fixtures and force deterministic race ordering. During scored paths it must invoke the same public/trusted interfaces being evaluated; it must not directly edit enforcement tables to manufacture PASS results.

---

## 5. OS and File-System Boundary

Required OS identities:

```text
ate-requester
ate-authority
ate-executor
```

Required ownership model:

```text
requester private identity material -> ate-requester only
authority private keys              -> ate-authority only
executor/audit private keys          -> ate-executor only
trusted verifier/executor code       -> root-owned, not requester-writable
enforcement directory/db             -> ate-executor, requester/authority no direct write
```

Recommended enforcement directory:

```text
/var/lib/ate-qa-poc/     ate-executor:ate-executor 0700
enforcement.db           ate-executor:ate-executor 0600
```

Equivalent paths are acceptable if the formal evidence records ownership/mode and direct requester mutation is denied.

`ate-authority` must not have direct SQL/file mutation access to `enforcement.db`.

---

## 6. Logical Authority Separation

Even though several authority services share the `ate-authority` OS identity for this local PoC, they are separate logical authorities with distinct keypairs and artifact permissions:

```text
AUTH_POLICY
AUTH_IDENTITY
AUTH_R11_QUALIFICATION
AUTH_R12_ADMISSION
AUTH_AUTHORIZATION
AUTH_TRUST_DECISION
AUTH_EXECUTOR
AUTH_AUDIT
```

Private keys are distinct.

No participant holds:

- policy key;
- R11 key;
- R12 key;
- authorization key;
- trust-decision key;
- executor key/resource credential;
- audit key.

Policy authoring and R11/R12 adjudication remain distinct logical authorities even when co-hosted.

---

## 7. Key Bootstrap

Formal-run authority/executor private keys are generated at bootstrap into owner-restricted directories.

Private seeds are not committed to Git and are not written to formal evidence.

Evidence records only:

```text
authority_id
key_id
public_key
permitted_artifact_types
custody owner/mode
```

Agent A and Agent B use distinct synthetic identity keypairs. Because both are test fixtures, QA-P7 tests SubjectBinding transplant rejection given distinct uncompromised identity anchors; it does not claim production key-custody resistance.

---

## 8. Canonical Data Model

Security-relevant payloads permit only:

```text
null
boolean
signed integer in the implementation safe range
UTF-8 NFC-normalized string
array
object with unique string keys
```

Prohibited:

```text
floating-point values
NaN / Infinity
duplicate object keys
non-string object keys
unsupported binary/native objects
```

Canonical encoding:

```text
JSON UTF-8
sort object keys lexicographically
separators = (",", ":")
ensure_ascii = false
strings normalized NFC
```

Signing input:

```text
UTF8(artifact_domain) || 0x00 || canonical_json_bytes
```

Hash: SHA-256.  
Signature: Ed25519.

The parser must reject duplicate keys before canonicalization.

---

## 9. Canonicalization Invariants

The implementation must self-test before formal execution:

```text
same parsed object + reordered keys/whitespace -> identical canonical bytes/digest
semantic field mutation                       -> different digest/signature failure
duplicate keys                                -> reject
float                                          -> reject
wrong artifact domain                          -> signature verification failure
```

QA-P10 uses these semantics. Alternate serialization of the same supported object is not itself an error.

---

## 10. SubjectBinding Fixtures

Agent A:

```text
subject_identity_id = agent-a
runtime_class       = synthetic-runtime-v1
provider_id         = local-fixture
binding_level       = SB2
```

Agent B uses a different identity anchor and different `subject_binding_digest`.

Live proof uses a fresh challenge signed by the selected subject identity key and bound to:

```text
subject_identity_id
challenge
runtime_class
trust_domain
role
```

The verifier reconstructs and compares the canonical SubjectBinding digest.

---

## 11. Authoritative Profile and Policy Selection

The candidate does not choose its controlling profile or AdmissionPolicy.

Qualification service input may include:

```text
requested role
evidence bundle
live SubjectBinding proof
```

The service resolves the current QualificationRequirementsProfile from a trusted mapping:

```text
(qualification_domain, role) -> active profile id/version/digest
```

Admission resolves:

```text
(trust_domain, role) -> active AdmissionPolicy id/version/digest
```

Candidate-supplied policy/profile references are checked only for consistency; they never select a weaker controlling version.

---

## 12. Qualification Fixture

Exactly one current profile is accepted for the primary path:

```text
profile_id:              qa-demo-writer
profile_version:         1
qualification_domain:    local-qa-demo
role_id:                 demo-repository-writer
minimum_binding:         SB2
maximum_eligible_risk:   R2
eligible_capability:     demo-resource-write
```

Required signed fixture evidence:

- identity/runtime evidence;
- provenance/runtime-class evidence;
- governance compatibility evidence;
- deterministic behavioral fixture receipt;
- operational-control compatibility evidence.

Every evidence issuer is artifact-class authorized.

---

## 13. Admission Fixture

Active policy recognizes exactly:

```text
trust_domain: local-ate-demo
role: demo-repository-writer
qualification_domain: local-qa-demo
qualification authority: AUTH_R11_QUALIFICATION
profile: qa-demo-writer v1 exact digest
maximum risk: R2
eligible capability: demo-resource-write
```

A correctly signed `qa-demo-writer` v2/different digest is not recognized until policy explicitly changes.

---

## 14. Immutable Artifacts

The following are immutable signed objects:

```text
QualificationRequirementsProfile
QualificationEvidenceManifest
QualificationDecision
QualificationCredential
AdmissionPolicy
AdmissionEvidenceManifest
AdmissionDecision
AdmissionCredential
CapabilityToken
TrustDecision
RevocationControlRecord
TrustStateSnapshot
```

Credential lifecycle status is not edited in place.

---

## 15. Control-Plane Current State

The authority maintains the conceptual current trust state and emits signed control records.

For the local PoC, every accepted control-state change has monotonic fields:

```text
previous_epoch
new_epoch
change_type
target_type
target_id
target_digest_optional
effective_at
issuer_authority_id
issuer_key_id
signature
```

Executor-side apply accepts a control record only when:

```text
schema/canonicalization valid
signature valid
issuer authorized for change type
previous_epoch == executor.current_epoch
new_epoch == previous_epoch + 1
target recognized
record not previously applied
```

Epoch rollback, replay, or gap fails closed.

---

## 16. Executor-Owned Enforcement Store

`enforcement.db` is the only mutable store participating in EAP serialization.

Minimum tables:

```text
control_state(
    singleton,
    current_epoch
)

applied_control_records(
    record_id PRIMARY KEY,
    target_type,
    target_id,
    target_digest,
    status,
    effective_at,
    applied_epoch UNIQUE,
    record_digest UNIQUE
)

execution_nonces(
    nonce PRIMARY KEY,
    action_digest,
    reserved_at,
    status
)

protected_resource(
    resource_id PRIMARY KEY,
    value,
    mutation_count
)

audit(
    sequence PRIMARY KEY,
    event_type,
    event_payload,
    previous_hash,
    event_hash UNIQUE,
    created_at
)
```

Qualification/admission artifacts themselves are passed as signed immutable objects and preserved in evidence; authority does not need SQL access to the enforcement store.

---

## 17. Trusted Executor-Side Interfaces

The executor exposes only narrow trusted operations, conceptually:

```text
apply_control_record(signed_record)
append_verified_authority_event(signed_artifact_or_event)
read_resource_for_evidence()
execute_bound_action(bundle)
```

No generic SQL or `write_resource(value)` API is exposed to requester/authority.

`apply_control_record` can only reduce/change current trust state according to a valid signed record. It cannot create a resource grant.

---

## 18. Historical Decision Snapshot vs EAP Current State

Qualification, admission, CapabilityToken issuance, and TrustDecision bind coherent historical `TrustStateReference` / snapshot information.

At EAP:

```text
1. verify historical snapshot/reference integrity
2. do NOT require executor.current_epoch == historical epoch
3. independently evaluate bound eligibility dependencies against executor current applied state
4. deny if any current dependency is invalid
```

A greater current epoch is not itself denial. A relevant invalidating record is.

This prevents stale pre-issued authorization from overriding later revocation.

---

## 19. Recursive Dependency Evaluation

Admission usability depends on its exact QualificationCredential.

At capability issuance, trust decision, and EAP:

```text
usable(admission) requires usable(exact qualification dependency)
```

If qualification is revoked, suspended, expired, hard-superseded, issuer-invalid, SubjectBinding-invalid, or unknown, admission becomes unusable even without a direct admission revocation.

No cached `admitted=true` flag is permitted.

---

## 20. Deterministic Clock

All temporal validation receives an injected `TestClock` in tests and formal-run scenarios.

No scored expiry test uses `sleep()`.

Clock transitions are explicit evidence events, for example:

```text
T0 -> issue qualification
T1 -> issue admission/capability
T2 -> qualification expires
T3 -> EAP attempt
```

The same logical clock value is supplied consistently to authority and executor validation for a test step.

---

## 21. CapabilityToken and TrustDecision Binding

CapabilityToken binds:

```text
subject_binding_digest
qualification_credential_id
qualification_credential_digest
admission_credential_id
admission_credential_digest
session_identity
operation
target
parameters_digest
risk_class
capability_class
nonce
issued_at
expires_at
historical trust_state_reference
```

TrustDecision binds the same eligibility chain plus:

```text
capability_token_id
capability_token_digest
requested_action_digest
verdict
issued_at
expires_at
historical trust_state_reference
```

All are signed.

---

## 22. Execution Authorization Point

`execute_bound_action()` opens the executor-owned serialization boundary.

Conceptual transaction:

```text
BEGIN IMMEDIATE

verify signed bundle structure and action binding
verify CapabilityToken / TrustDecision signatures and issuer authorization
verify exact qualification/admission IDs + digests
verify live SubjectBinding proof
verify current time / derived expiration
read current applied control state
recursively verify qualification/admission usability
verify nonce unused
insert nonce reservation
append EAP_REACHED audit record
update protected_resource value + mutation_count
append EXECUTION_SUCCEEDED audit record

COMMIT
```

On any failure:

```text
no protected mutation
no successful EAP commit
append/emit denial evidence through trusted path
```

The formal implementation must ensure denial evidence itself does not create a side effect that changes authorization state.

---

## 23. Revocation / EAP Ordering

`apply_control_record()` uses the same SQLite write serialization mechanism as EAP.

QA-P11 uses explicit test barriers.

Subcase A:

```text
revocation obtains write lock
revocation commits
barrier releases executor
executor begins EAP
executor observes invalid state
DENY
mutation_count = 0
```

Subcase B:

```text
executor obtains write lock
executor reaches/commits EAP mutation
barrier releases revocation
revocation commits afterward
mutation_count = 1
next fresh action is denied
```

No timing inference is used; sequence and epoch evidence proves ordering.

---

## 24. Audit Plane

The authoritative PoC audit ledger is executor-owned and participant-inaccessible.

Authority events enter by trusted ingest of the signed source artifact/event. The audit row records the source artifact digest.

Audit invariants:

```text
monotonic sequence
previous_hash chain
canonical event payload hash
requester cannot write/delete/truncate
EAP and control-record application ordering reconstructable
```

Required event classes include the frozen qualification/admission events plus:

```text
CONTROL_RECORD_APPLIED
CONTROL_RECORD_REJECTED
CLOCK_ADVANCED
EAP_REACHED
EXECUTION_SUCCEEDED
EXECUTION_DENIED
DIRECT_BYPASS_DENIED
```

---

## 25. Test Isolation

QA-P1 through QA-P14 each start from a fresh deterministic fixture directory/database, except the paired QA-P11 subcases, which each get their own fresh fixture.

This isolation prevents contamination but does not replace durability properties already established by P1.

Each case preserves its complete database/evidence or a digest-locked snapshot sufficient for verification.

---

## 26. Mandatory Test Matrix

### QA-P1 — Happy path

Agent A qualifies, is admitted, receives capability and TRUST_GRANTED, crosses EAP once, and changes protected state exactly once.

### QA-P2 — Qualified but not admitted

Capability issuance denied. No EAP. No mutation.

### QA-P3 — Admission revoked before new capability

Signed R12 admission revocation is applied to executor state before capability request. Capability issuance denied.

### QA-P4 — Pre-issued capability after admission revocation before EAP

Capability/TrustDecision issued while admission active. Revocation commits to executor store before EAP. Executor denies.

### QA-P5 — Pre-issued capability after qualification revocation before EAP

R11 qualification revocation commits before EAP. Recursive dependency invalidates admission. Executor denies.

### QA-P6 — Qualification expires after capability issuance before EAP

Injected clock advances past QualificationCredential expiry while capability/trust decision are nominally unexpired. EAP denies by derived expiration rule.

### QA-P7 — Agent B reuses Agent A chain

Agent B signs the live challenge using B identity while presenting Agent A eligibility chain. SubjectBinding mismatch denies.

### QA-P8 — Valid signature from unauthorized qualification issuer

Use `AUTH_IDENTITY`, which is active/recognized but not permitted to sign QualificationCredential, to sign an otherwise well-formed credential. Qualification/admission validation denies issuer authority.

### QA-P9 — Mixed/incoherent trust-state view

Build a decision request with a snapshot/reference whose committed components do not match one coherent epoch/digest set. Deny `*_TRUST_STATE_INCONSISTENT`.

### QA-P10 — Canonical payload/digest substitution

Required subchecks:

```text
reordered keys / whitespace only -> identical canonical digest
semantic security-field mutation -> digest/signature failure -> DENY
duplicate JSON key -> parser rejection -> DENY
float value -> parser rejection -> DENY
```

### QA-P11 — Deterministic revocation/EAP ordering

Run forced-order subcase A and B from Section 23. Preserve audit sequence and applied epoch evidence.

### QA-P12 — Direct protected-resource bypass

As `ate-requester`, attempt direct filesystem/SQLite mutation of executor-owned protected state without executor interface.

Expected OS/file denial and unchanged state. Any success -> `ENFORCEMENT_FAILURE`.

### QA-P13 — Unrecognized future qualification profile

Issue valid qualification under signed `qa-demo-writer` v2/different digest. AdmissionPolicy recognizes only v1 exact constraints. Admission denies `AX_QUALIFICATION_PROFILE_UNRECOGNIZED`.

### QA-P14 — Admission expiry / review boundary

Advance TestClock past AdmissionCredential expiry. Old admission is unusable and never edited. Successful renewal requires new AdmissionDecision and new AdmissionCredential with distinct IDs/digests. Old artifact remains historical evidence.

---

## 27. Formal Result Schema

Per test:

```text
test_id
fixture_id
initial_resource_value
final_resource_value
initial_mutation_count
final_mutation_count
starting_epoch
ending_epoch
qualification_id/digest
admission_id/digest
capability_id/digest
trust_decision_id/digest
verdict
reason_code
EAP_reached
control_records_applied[]
audit_first_sequence
audit_last_sequence
audit_chain_valid
PASS/FAIL
```

Run-level evidence:

```text
run_id
implementation_commit
PoC_design_freeze_blob
qualification_admission_freeze_blob
frozen_spec_blobs{}
preflight{}
public_key_manifest{}
canonicalization_profile
QA_P1_to_QA_P14[]
overall_classification
deviations[]
```

---

## 28. Acceptance Classification

Exactly one:

```text
QUALIFICATION_ADMISSION_LOCAL_POC_PASS
QUALIFICATION_ADMISSION_LOCAL_POC_FAIL
ENFORCEMENT_FAILURE
INVALID_RUN
```

PASS requires all frozen QA-P1…QA-P14 requirements, all design-required subchecks, valid audit chains, valid preflight, and zero unauthorized protected mutations.

`ENFORCEMENT_FAILURE` controls if:

- QA-P12 direct mutation succeeds; or
- invalidating state committed before EAP still permits mutation.

`INVALID_RUN` controls for frozen-input mismatch or unavailable required privilege boundary.

---

## 29. Formal Preflight

Must establish before QA-P1:

1. exact frozen architecture blob locks;
2. exact frozen PoC design blob lock;
3. required OS identities exist;
4. noninteractive trusted orchestration path is available;
5. trusted code not requester-writable;
6. authority keys not requester-readable;
7. executor/audit keys not requester/authority-readable;
8. enforcement store not requester/authority directly writable;
9. direct bypass probe fails;
10. canonicalization self-tests pass;
11. signature/domain-separation self-tests pass;
12. monotonic control-epoch self-tests pass;
13. audit-chain self-test passes;
14. SQLite serialization mode required by QA-P11 is available.

Any failure -> `INVALID_RUN`; no scored tests.

---

## 30. Recommended Implementation Layout

```text
architecture/agent-trust-envelope/qualification-admission-local-poc-v0.1/
    README.md
    qa_poc/
        canonical.py
        crypto.py
        models.py
        subject_binding.py
        policies.py
        qualification.py
        admission.py
        authorization.py
        clock.py
        evidence.py
    trusted/
        control_apply.py
        audit_ingest.py
        executor.py
        enforcement_store.py
    tests/
        test_preflight.py
        test_qa_matrix.py
    run_formal.py
    evidence/
```

No private authority/executor keys are stored in the repository.

---

## 31. STOP Conditions During Implementation

Stop and return to design review if implementation requires:

- weakening direct OS/resource separation;
- giving authority direct enforcement DB write access;
- replacing exact profile recognition with `version >= N`;
- unsigned qualification/admission flags;
- omitting EAP current-state validation;
- using wall-clock race timing for QA-P11;
- storing mutable status inside signed credentials;
- allowing generic signing APIs to participant code;
- changing frozen QA-P semantics.

---

## 32. Remaining Final Review Questions

Final adversarial pass should verify:

1. single executor-owned serialization boundary really closes QA-P4/P5/P11 races;
2. control-record application cannot rollback or skip epochs;
3. authority cannot mutate protected resource through control interface;
4. EAP uses current dependency state rather than historical snapshot alone;
5. canonicalization equivalence and mutation rejection are correctly separated;
6. logical key separation meets A2 local-PoC claim without overstating physical separation;
7. QA-P7 claim is limited to transplant rejection, not stolen-key resistance;
8. formal controller cannot accidentally bypass scored interfaces;
9. evidence can reconstruct every relevant state transition;
10. QA-P13 exact profile recognition and QA-P14 reissuance are deterministic.

---

## 33. Current Disposition

```text
Design version:          v0.1.1
Status:                  FINAL DESIGN CANDIDATE / NOT FROZEN
v0.1 review findings:    CORRECTED
Frozen architecture:     UNCHANGED
Implementation started:  NO
Formal run authorized:   NO
Hermes/model calls:      NOT REQUIRED
Next step:               FINAL ADVERSARIAL PASS -> DESIGN FREEZE
```

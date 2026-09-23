# ATE Qualification & Admission Local PoC v0.1.2 — Final Design

**Status:** FINAL DESIGN — READY FOR BLOB LOCK  
**Date:** 2026-09-16  
**Supersedes for PoC design:** `ATE-QUALIFICATION-ADMISSION-LOCAL-POC-v0.1.1-DESIGN.md`  
**Review chain:** v0.1 design -> v0.1 adversarial review -> v0.1.1 corrected design -> v0.1.1 final adversarial review  
**Controlling architecture:** `AGENT-QUALIFICATION-ADMISSION-v0.2.2-FREEZE.md`

---

## 1. Objective

Build the smallest deterministic local R2/A2 system that can establish whether the frozen Agent Qualification & Admission architecture is enforceable before one protected local write.

Required separation:

```text
QUALIFICATION != ADMISSION != ACTION AUTHORIZATION != EXECUTION
```

A successful PoC establishes only that a local system can require current, issuer-authorized, SubjectBinding-bound qualification and admission, bind both into action authorization, recheck both at the Execution Authorization Point (EAP), and deny protected execution when prerequisites are invalid.

No claim of general AI trustworthiness, general AI safety, production readiness, federation safety, or stolen-key resistance is permitted.

---

## 2. Frozen Inputs

The formal runner must verify and record:

```text
Agent Qualification & Admission v0.2.2 freeze-manifest blob
all six frozen architecture/specification blob IDs
this PoC design-freeze blob
implementation commit SHA
```

Any mismatch stops the formal run:

```text
PRECHECK_FAIL_FROZEN_SPEC_MISMATCH
overall = INVALID_RUN
```

---

## 3. Fixed Scope

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
                     (fixture/orchestration only; not subject)
                                  |
                    +-------------+-------------+
                    |                           |
                    v                           v
             ate-requester                ate-authority
          Agent A / Agent B        Policy / Identity / R11 /
          live identity proof      R12 / Authorization / Trust
                    |                           |
                    | requests                  | signed artifacts
                    |                           | signed control records
                    +-------------+-------------+
                                  |
                                  v
                       trusted executor boundary
                           runs as ate-executor
                                  |
                                  v
                         executor-owned enforcement.db
                         - applied control state
                         - execution nonces
                         - protected resource
                         - authoritative audit chain
```

The trusted test controller may create/reset fixtures and coordinate deterministic barriers. During scored paths it must use the evaluated interfaces and must not directly edit enforcement tables to manufacture results.

---

## 5. OS / File-System Boundary

Required local identities:

```text
ate-requester
ate-authority
ate-executor
```

Custody:

```text
Agent A/B identity private keys                       -> ate-requester
Policy/Identity/R11/R12/Authorization/Trust keys     -> ate-authority
Executor/Audit private keys                           -> ate-executor
trusted verifier/executor code                        -> root-owned, requester not writable
enforcement directory + database                      -> ate-executor, 0700/0600 equivalent
```

Neither `ate-requester` nor `ate-authority` receives direct SQL/file mutation access to `enforcement.db`.

The protected resource exists only inside the executor-owned enforcement boundary.

Any successful direct requester mutation is `ENFORCEMENT_FAILURE`.

---

## 6. Logical Authorities

Distinct authority IDs and distinct keypairs are mandatory:

### Keys held by `ate-authority`

```text
AUTH_POLICY
AUTH_IDENTITY
AUTH_R11_QUALIFICATION
AUTH_R12_ADMISSION
AUTH_AUTHORIZATION
AUTH_TRUST_DECISION
```

### Keys held by `ate-executor`

```text
AUTH_EXECUTOR
AUTH_AUDIT
```

Co-hosting some logical authorities under one OS identity is a local PoC limitation, not a collapse of artifact permissions. Trust Root Registry permissions remain artifact-class specific.

The participant possesses none of the authority/executor/audit private keys.

---

## 7. Key Bootstrap

Authority/executor keypairs are generated during bootstrap into owner-restricted directories.

Private keys/seeds are not committed to Git and are not placed in evidence.

Evidence records only public material and custody metadata:

```text
authority_id
key_id
public_key
permitted_artifact_types
file owner/mode
```

Agent A and Agent B have different synthetic identity anchors.

QA-P7 proves credential-transplant rejection given uncompromised identity anchors; it does not prove resistance to identity-key theft.

---

## 8. Canonical Data Model

Security-relevant values permit only:

```text
null
boolean
signed integer within safe implementation range
UTF-8 NFC-normalized string
array
object with unique string keys
```

Reject:

```text
floats
NaN / Infinity
duplicate keys
non-string object keys
unsupported native/binary values
```

Canonical encoding:

```text
UTF-8 JSON
NFC-normalized strings
lexicographically sorted keys
separators=(",", ":")
ensure_ascii=false
```

Digest: SHA-256.  
Signature: Ed25519.

Signing bytes:

```text
UTF8(artifact_domain) || 0x00 || canonical_json_bytes
```

Artifact-domain separation is mandatory.

---

## 9. Canonicalization Self-Test

Before formal QA tests:

```text
same supported object with reordered keys/whitespace -> same canonical bytes/digest
security-relevant semantic mutation                 -> different digest / signature failure
duplicate key                                       -> parser rejection
float                                               -> parser rejection
wrong artifact signing domain                       -> signature rejection
```

Alternate textual serialization of the same supported object is not a security failure.

---

## 10. SubjectBinding

Agent A fixture:

```text
subject_identity_id = agent-a
runtime_class       = synthetic-runtime-v1
provider_id         = local-fixture
binding_level       = SB2
```

Agent B has a distinct identity anchor and distinct `subject_binding_digest`.

Live proof signs a fresh challenge bound to:

```text
subject_identity_id
challenge
runtime_class
trust_domain
role
```

The verifier reconstructs and compares the canonical SubjectBinding digest.

---

## 11. Authoritative Profile / Policy Resolution

Candidate input cannot choose the controlling policy.

Qualification authority resolves:

```text
(qualification_domain, role) -> active QualificationRequirementsProfile
```

Admission authority resolves:

```text
(trust_domain, role) -> active AdmissionPolicy
```

Candidate-supplied profile/policy identifiers are consistency assertions only and cannot downgrade current policy.

---

## 12. Qualification Fixture

Current profile:

```text
profile_id:             qa-demo-writer
profile_version:        1
qualification_domain:   local-qa-demo
role_id:                demo-repository-writer
minimum_binding:        SB2
maximum_risk:           R2
eligible_capability:    demo-resource-write
```

Required signed deterministic evidence classes:

- identity/runtime;
- provenance/runtime-class;
- governance compatibility;
- behavioral fixture receipt;
- operational-control compatibility.

Every evidence signature is checked for both cryptographic validity and issuer authorization for the artifact type.

---

## 13. Admission Fixture

Active policy recognizes exactly:

```text
trust_domain:                local-ate-demo
role:                        demo-repository-writer
qualification_domain:        local-qa-demo
qualification_authority:     AUTH_R11_QUALIFICATION
recognized profile:          qa-demo-writer v1 exact digest
maximum risk:                R2
eligible capability:         demo-resource-write
```

A correctly signed newer v2/different digest is unrecognized and denied until the AdmissionPolicy explicitly changes.

---

## 14. Immutable Signed Artifacts

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
ControlRecord
TrustStateSnapshot
```

QualificationCredential and AdmissionCredential never receive mutable in-place status changes.

---

## 15. Historical Trust-State Reference

Qualification/admission/capability/trust artifacts bind the coherent state view used when issued.

That historical snapshot/reference is evidence of issuance context, not permission to ignore later state.

At EAP the executor:

1. verifies historical snapshot integrity;
2. permits current applied epoch to be greater than the historical epoch;
3. independently checks the exact bound eligibility dependencies against current applied executor state;
4. denies if any relevant current state is invalid.

A higher current epoch alone is not denial.

---

## 16. ControlRecord and Execution-Effective State

Authority state changes are expressed as signed ControlRecords:

```text
record_id
previous_epoch
new_epoch
change_type
target_type
target_id
target_digest_optional
issued_at
issuer_authority_id
issuer_key_id
signature
```

Executor-side `apply_control_record()` validates:

```text
schema + canonical form
artifact-domain signature
issuer authorization for change type
previous_epoch == current executor epoch
new_epoch == previous_epoch + 1
target recognized
record id/digest not already applied
```

Then, inside the executor-owned serialized write transaction, it records:

```text
applied_at
applied_epoch = new_epoch
```

For this PoC:

> A control-state change becomes authoritative and effective for execution when `apply_control_record()` commits it into the executor-owned enforcement store.

`issued_at` does not by itself make an in-transit record execution-effective.

Backdated execution-effective revocation is not supported by this PoC.

Thus the frozen rule is testable without ambiguity: invalidating state committed/effective in the authoritative executor trust-state system before EAP must block EAP.

---

## 17. Executor-Owned Enforcement Store

Minimum SQLite tables:

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
    issued_at,
    applied_at,
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
    sequence INTEGER PRIMARY KEY,
    event_type,
    payload_json,
    previous_hash,
    event_hash UNIQUE,
    created_at
)
```

Recommended SQLite controls:

```text
journal_mode=WAL
synchronous=FULL
foreign_keys=ON
BEGIN IMMEDIATE for EAP/control application
```

---

## 18. Narrow Executor Interfaces

Conceptual trusted operations:

```text
apply_control_record(signed_record)
append_verified_authority_event(signed_source)
read_resource_for_evidence()
execute_bound_action(bundle)
```

No generic SQL interface or direct resource-write API is exposed to requester/authority.

A ControlRecord can change current trust state only; it cannot create a protected resource grant.

---

## 19. Recursive Dependency Evaluation

Admission depends on its exact QualificationCredential.

At capability issuance, TrustDecision creation, and EAP:

```text
usable(admission) requires usable(exact bound qualification)
```

Qualification unusability due to revocation, suspension, expiry, hard supersession, invalid issuer, SubjectBinding failure, or unknown state makes dependent admission unusable even if AdmissionCredential itself is not directly revoked.

No cached boolean `admitted=true` may substitute for dependency evaluation.

---

## 20. Deterministic Clock

All time validation uses an injected `TestClock` during tests.

No scored test uses `sleep()`.

Clock transitions are recorded in evidence and audit where relevant.

---

## 21. CapabilityToken Binding

A CapabilityToken binds at least:

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
historical_trust_state_reference
```

It is signed by `AUTH_AUTHORIZATION`.

---

## 22. TrustDecision Binding

TrustDecision binds the same eligibility dependency chain plus:

```text
capability_token_id
capability_token_digest
requested_action_digest
verdict
issued_at
expires_at
historical_trust_state_reference
```

It is signed by `AUTH_TRUST_DECISION`.

Unsigned eligibility flags are prohibited.

---

## 23. Execution Authorization Point

`execute_bound_action()` opens one executor-owned `BEGIN IMMEDIATE` transaction.

Inside that transaction:

```text
verify bundle structure/canonical digests
verify CapabilityToken + TrustDecision signatures and issuer permissions
verify exact qualification/admission ids + digests
verify live SubjectBinding
verify derived/current expiration using TestClock
read current applied control state
recursively validate qualification -> admission dependency
verify nonce unused
insert nonce reservation
append EAP_REACHED audit row
update protected_resource + mutation_count
append EXECUTION_SUCCEEDED audit row
COMMIT
```

For this local PoC, `EAP_REACHED`, protected mutation, and `EXECUTION_SUCCEEDED` are authoritative only if the transaction commits.

Therefore:

```text
committed EAP_REACHED <=> protected local mutation committed
```

If the transaction rolls back, neither success event survives.

---

## 24. EAP Denial Audit

If validation fails before commit:

1. roll back the execution transaction;
2. do not retain EAP_REACHED or resource mutation;
3. append `EXECUTION_DENIED` in a separate trusted audit transaction;
4. record observed executor epoch, action digest, bound eligibility IDs/digests, and reason code;
5. do not mark the action nonce as successfully consumed/executed.

Denial audit persistence must not change authorization state.

---

## 25. Revocation / EAP Serialization

`apply_control_record()` uses the same executor-owned SQLite write serialization as EAP.

QA-P11 forces both possible orderings with explicit barriers.

### Subcase A

```text
control-record transaction gets lock
revocation commits -> applied epoch increments
release EAP barrier
EAP begins
current state shows invalid dependency
DENY
mutation_count = 0
```

### Subcase B

```text
EAP gets lock
EAP + protected mutation commit
release control-record barrier
revocation commits afterward
mutation_count = 1
subsequent fresh action denied
```

No timing inference or probabilistic race is used.

---

## 26. Audit Plane

The authoritative audit ledger is executor-owned and requester-inaccessible.

Authority-side qualification/admission/capability/trust events enter through `append_verified_authority_event()`, which validates the signed source and records its digest.

`AUTH_AUDIT` signs/checkpoints authoritative audit data as defined by implementation.

Audit properties:

```text
monotonic sequence
previous_hash chain
canonical payload hash
requester cannot append/delete/truncate
control-record/EAP ordering reconstructable
```

Required event classes include:

```text
QUALIFICATION_EVALUATED
QUALIFICATION_GRANTED / DENIED
QUALIFICATION_CREDENTIAL_ISSUED
ADMISSION_EVALUATED
ADMISSION_GRANTED / DENIED
ADMISSION_CREDENTIAL_ISSUED
CAPABILITY_ISSUED
TRUST_GRANTED / DENIED
CONTROL_RECORD_APPLIED / REJECTED
CLOCK_ADVANCED
EAP_REACHED
EXECUTION_SUCCEEDED / DENIED
DIRECT_BYPASS_DENIED
```

---

## 27. Test Isolation

Each QA-P case uses a fresh fixture database/directory. QA-P11 subcases each use their own fresh fixture.

Isolation does not replace earlier P1 durability evidence; it prevents cross-case contamination in this qualification/admission experiment.

---

## 28. Frozen QA-P1 … QA-P14 Matrix

### QA-P1 — Happy path

Agent A qualifies, is admitted, receives valid capability and TrustDecision, reaches EAP once, and produces exactly one protected mutation.

### QA-P2 — Qualified but not admitted

No usable AdmissionCredential -> capability issuance denied -> no EAP -> no mutation.

### QA-P3 — Admission revoked before new capability

R12 AdmissionCredential revocation is signed and committed to executor state before capability request -> deny.

### QA-P4 — Pre-issued capability, admission revoked before EAP

Capability/TrustDecision issued while active -> admission revocation commits before EAP -> executor current-state recheck denies.

### QA-P5 — Pre-issued capability, qualification revoked before EAP

Qualification revocation commits before EAP -> exact dependent admission becomes unusable -> deny.

### QA-P6 — Qualification expires after capability issuance before EAP

TestClock crosses QualificationCredential expiry while downstream token/decision remain nominally unexpired -> derived expiration denies.

### QA-P7 — Agent B reuses Agent A chain

Agent B live proof + Agent A eligibility chain -> SubjectBinding mismatch -> deny.

### QA-P8 — Valid signature from unauthorized qualification issuer

Use active recognized `AUTH_IDENTITY` key to sign a QualificationCredential even though that key lacks permission for the artifact type -> deny issuer authorization.

### QA-P9 — Mixed / incoherent trust-state view

Use snapshot/reference components that do not belong to one coherent committed state -> `*_TRUST_STATE_INCONSISTENT` -> deny.

### QA-P10 — Canonical payload / digest substitution

Required subchecks:

```text
reordered keys/whitespace only -> identical canonical digest
semantic security-field mutation -> digest/signature failure -> deny
duplicate key -> parser reject
float -> parser reject
```

### QA-P11 — Deterministic revocation/EAP ordering

Execute the forced A/B orderings from Section 25 and verify audit sequence/epochs.

### QA-P12 — Direct protected-resource bypass

As `ate-requester`, attempt direct filesystem/SQLite mutation of executor-owned state without executor interface -> OS/resource denial and unchanged state.

Any success -> `ENFORCEMENT_FAILURE`.

### QA-P13 — Unrecognized future qualification profile

Correctly signed `qa-demo-writer` v2/different digest while AdmissionPolicy recognizes v1 exact digest only -> `AX_QUALIFICATION_PROFILE_UNRECOGNIZED`.

### QA-P14 — Admission expiry / review boundary

Advance TestClock beyond AdmissionCredential expiry -> old admission unusable. Renewal requires a new AdmissionDecision and new AdmissionCredential with distinct IDs/digests. Old artifact remains unchanged historical evidence.

---

## 29. Formal Evidence

Per case:

```text
test_id
fixture_id
initial/final resource value
initial/final mutation_count
starting/ending applied epoch
qualification id/digest
admission id/digest
capability id/digest
trust-decision id/digest
verdict + reason code
EAP_reached
applied control records
audit sequence range
audit chain valid
PASS/FAIL
```

Run level:

```text
run_id
implementation_commit
PoC design-freeze blob
qualification/admission freeze blob
six frozen spec blobs
preflight results
public-key manifest
canonicalization profile
QA-P1..QA-P14 results
overall classification
deviations[]
```

---

## 30. Formal Classification

Exactly one:

```text
QUALIFICATION_ADMISSION_LOCAL_POC_PASS
QUALIFICATION_ADMISSION_LOCAL_POC_FAIL
ENFORCEMENT_FAILURE
INVALID_RUN
```

PASS requires all QA-P1…QA-P14 expectations, required subchecks, valid audit evidence, valid preflight, and zero unauthorized protected mutations.

`ENFORCEMENT_FAILURE` overrides ordinary fail when:

- direct requester protected mutation succeeds; or
- invalidating state committed/effective in executor trust state before EAP still allows protected mutation.

---

## 31. Formal Preflight

Must establish before QA-P1:

1. frozen architecture blob locks match;
2. PoC design-freeze blob matches;
3. OS identities exist;
4. trusted noninteractive orchestration path exists;
5. trusted code not requester-writable;
6. authority keys not requester-readable;
7. executor/audit keys not requester/authority-readable;
8. enforcement store not requester/authority directly writable;
9. direct-bypass probe fails;
10. canonicalization self-test passes;
11. signing/domain-separation self-test passes;
12. monotonic control-epoch self-test passes;
13. audit-chain self-test passes;
14. required SQLite serialization is available.

Failure -> `INVALID_RUN`; scored tests do not start.

---

## 32. Recommended Implementation Layout

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

No authority/executor private keys are stored in the repository.

---

## 33. Implementation STOP Conditions

Stop and return to design review if implementation requires:

- requester or authority direct enforcement-store writes;
- weakening the OS/resource bypass boundary;
- unsigned qualification/admission flags;
- generic participant signing oracle;
- profile acceptance by `version >= N` rather than explicit recognition;
- skipping EAP current-state verification;
- treating signed-but-unapplied revocation as ambiguously effective;
- wall-clock race timing for QA-P11;
- mutable credential status fields;
- changing frozen QA-P semantics.

---

## 34. Final Design Disposition

```text
Design version:                 v0.1.2
First adversarial findings:     CLOSED
Final adversarial findings:     CLOSED
Frozen v0.2.2 architecture:     UNCHANGED
Critical/high open findings:    0
Implementation authorized:      AFTER DESIGN BLOB LOCK
Formal run authorized:          AFTER IMPLEMENTATION + PREFLIGHT
Hermes/model calls required:    NO FOR DESIGN
Next step:                      CREATE DESIGN FREEZE MANIFEST
```

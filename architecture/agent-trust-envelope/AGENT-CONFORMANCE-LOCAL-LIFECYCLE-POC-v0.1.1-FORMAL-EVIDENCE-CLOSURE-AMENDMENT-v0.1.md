# Agent Conformance Local Lifecycle PoC v0.1.1
## Formal Evidence Closure Amendment v0.1

**Status:** CANDIDATE - DESIGN ONLY  
**Date:** 2026-09-19  
**Applies to:** `AGENT-CONFORMANCE-LOCAL-LIFECYCLE-POC-v0.1.1-DESIGN.md`  
**Frozen design commit:** `b38be8c11b00b1a9f7b9fc95d64d5d97cf341edf`  
**Current execution head reviewed:** `ded136073ef9518877cd1dd1d7a02b2e9f8248b1`  
**Current implementation baseline reviewed:** `76e0816ca729bbef3fde197970c1958352023c7f`  
**Authorization granted by this document:** none

---

## 1. Purpose

This amendment closes formal-evidence defects discovered by independent review
of development dry-run:

`20260919T102042Z-acl-lifecycle-poc-v0.1.1-dry-run`

The dry-run behavior was internally consistent:

- 81 tests passed;
- lifecycle state moved `CONFORMANT @ 1` ->
  `REATTESTATION_REQUIRED @ 2` -> `CONFORMANT @ 3`;
- stale capability C1 was denied with zero effect;
- restored capability C2 executed once;
- replay was denied;
- the 15-record audit ledger's sequence, payload digests, record hashes, and
  causal order independently recomputed;
- the tampered copy failed at the mutated record;
- all evidence-manifest hashes independently recomputed.

Those results do not yet authorize a formal run. The current evidence format
does not preserve the verification keys required to authenticate signatures,
does not explicitly account for the frozen 18 required and 8 negative cases,
and does not emit the frozen RunRecord. The frozen RunRecord and evidence
manifest also contain a digest dependency that must be ordered without a
self-referential hash.

This amendment changes evidence production and verification only. It does not
relax any frozen test, security boundary, acceptance threshold, or final
classification.

---

## 2. Controlling Disposition

Until this amendment is implemented, reviewed, and proven by a new isolated
development dry-run:

```text
DRY_RUN_BEHAVIOR_PASS
FORMAL_RUN_NOT_AUTHORIZED
```

The invalid prior formal evidence at `d225399` remains preserved with
controlling disposition `INCONCLUSIVE_EVIDENCE_INVALID`.

---

## 3. Defects Closed

### EC-01 - Verification keys are not durable evidence

The current run creates fresh Ed25519 keypairs in memory for:

1. profile signer;
2. qualification/admission issuer;
3. runtime observer;
4. R13 evaluator;
5. R14 lifecycle authority;
6. authorization service;
7. audit recorder.

Signed artifacts and audit records are persisted, but the corresponding public
keys are not. After process exit, an independent reviewer can validate hashes
but cannot cryptographically verify the signatures.

### EC-02 - Key generation is not deterministic

`fixtures/bootstrap.py` calls `generate_keypair()` for every run. This conflicts
with frozen design section 24, which requires the first PoC to avoid
nondeterministic dependencies and use deterministic or generated-once safe test
fixtures.

### EC-03 - Required-case accounting is implicit

`81 passed` proves aggregate pytest success. It does not, by itself, prove an
exact one-to-one accounting for:

- TC-01 through TC-18; and
- NS-01 through NS-08.

PASS requires explicit 18/18 and 8/8 evidence.

### EC-04 - Frozen RunRecord is absent

The current evidence set does not emit the section 21 RunRecord and omits at
least design version, formal implementation commit, start/completion times,
subject/role/domain, epoch summary, required/negative case counts, and the
evidence-manifest commitment.

### EC-05 - Manifest/RunRecord digest circularity is unspecified

If the evidence manifest hashes the final RunRecord, while the final RunRecord
contains the evidence-manifest SHA-256, neither file can be finalized first.
The closure order must be explicit and acyclic.

### EC-06 - The producer currently self-declares the final PASS

The same process creates evidence, verifies its in-memory objects, and writes a
PASS classification. Independent verification must be a separate post-production
gate. A producer result is a candidate, not the controlling final disposition.

---

## 4. Non-Goals

This amendment does not add:

- production PKI or production key custody;
- external model calls;
- remote or hardware attestation;
- additional trust domains or roles;
- semantic agent evaluation;
- new conformance behavior;
- relaxed frozen thresholds;
- automatic merge or cleanup.

Test private keys defined below are public test fixtures and MUST NEVER be used
for production authority.

---

## 5. Deterministic Test Trust Material

### 5.1 Required authorities

The corrected fixture set MUST contain exactly seven named Ed25519 test
authorities:

| Authority key name | Authority identifier | Permitted signing domains |
|---|---|---|
| `profile_signer` | `profile-signer-1` | conformance profile |
| `qa_issuer` | `qual-admission-issuer-1` | qualification and admission fixtures |
| `runtime_observer` | `observer-1` | runtime evidence and trigger observation |
| `r13_evaluator` | `r13-1` | R13 evaluation |
| `r14_authority` | `r14-1` | R14 state decision |
| `authorization_service` | `az-1` | action capability |
| `audit_recorder` | `audit-1` | audit record |

### 5.2 Fixture requirements

Each authority MUST use a distinct, fixed, test-only 32-byte Ed25519 private
seed. The seeds may be committed because they carry no authority outside this
local PoC, but every file containing them MUST state `TEST ONLY - NOT SECRET -
NOT FOR PRODUCTION`.

The fixture implementation MUST:

1. construct each private key from its exact seed;
2. derive the corresponding raw 32-byte public key;
3. derive `key_id = SHA256(raw_public_key)`;
4. reject duplicate private seeds, public keys, key IDs, or authority IDs;
5. bind every authority to an explicit allowlist of signing domains;
6. expose no private-key bytes through participant-facing objects;
7. produce identical public keys and key IDs on every run at the same commit.

Changing any seed creates a new implementation candidate and invalidates prior
dry-run readiness.

### 5.3 Verification-key registry

Before the first scored mutation, the producer MUST write
`01_verification_keys.json` containing, for each authority:

```text
authority_id
authority_role
key_algorithm = Ed25519
public_key_encoding = raw-32-byte-hex
public_key_hex
key_id_sha256
permitted_signing_domains[]
test_only = true
```

The registry MUST contain no private key or seed. Its canonical SHA-256 is the
`verification_key_registry_digest`.

The first audit record MUST be `trust_material_established` and bind that
digest. All later signed evidence must resolve to a key and permitted domain in
this registry.

This registry makes the local evidence self-verifying. It does not create a
production trust root; Git commit identity and the controlled formal-run
procedure remain the external provenance boundary for this PoC.

---

## 6. Complete Signed-Artifact Evidence

The evidence package MUST preserve every signed artifact used by the scored
lifecycle, including:

- both conformance profiles;
- qualification fixture;
- admission fixture;
- initial runtime evidence;
- invalidating runtime evidence;
- fresh restoration evidence;
- trigger observation;
- initial, invalidating, and restoration R13 evaluations;
- epoch 1, epoch 2, and epoch 3 R14 decisions;
- C0, C1, and C2 capabilities;
- authoritative audit ledger;
- tampered audit copy.

Each serialized artifact MUST retain its signing domain and signature. Each
artifact family MUST have an unambiguous verifier-key mapping in the key
registry.

`signature-verification.json` MUST enumerate every verified object with:

```text
artifact_kind
artifact_id or audit_event_sequence
signature_domain
authority_id
key_id
source_file
verification = PASS | FAIL
```

PASS requires:

- every expected signed object appears exactly once;
- no unregistered signing domain appears;
- key ID derivation matches the public key;
- every signature verifies over the frozen canonical signing bytes;
- zero unverifiable, duplicate, or orphan signed objects.

---

## 7. Explicit Case Accounting

The producer MUST write `case-accounting.json` with exactly 26 controlling
entries:

- `TC-01` through `TC-18`; and
- `NS-01` through `NS-08`.

Each entry MUST contain:

```text
case_id
case_kind = required | negative
title
outcome = PASS | FAIL | SKIPPED | ERROR
pytest_node_ids[]
evidence_refs[]
assertion_summary
```

Rules:

1. Every controlling case ID appears exactly once.
2. Every entry references at least one executed pytest node or an explicit
   producer assertion recorded in evidence.
3. Every referenced pytest node exists in the machine-readable pytest result.
4. No controlling node is skipped, xfailed, deselected, or missing.
5. Supplemental tests may exist but cannot substitute for a controlling case.
6. Aggregate totals and exact case accounting must both pass.

The producer MUST emit a machine-readable pytest result, preferably
`pytest-results.xml`, in addition to the human-readable summary.

---

## 8. Acyclic Evidence Closure

The evidence package uses five ordered layers.

### Layer 1 - Primary evidence

All substantive evidence is finalized, including:

- preflight;
- verification-key registry;
- signed artifacts;
- lifecycle/action results;
- authoritative and tampered ledgers;
- case accounting;
- machine-readable and human-readable test results;
- signature verification;
- `run-record-core.json`.

`run-record-core.json` contains every frozen RunRecord field except hashes of
objects that do not yet exist. Its classification is only:

```text
FORMAL_EVIDENCE_CANDIDATE
```

or, for a development run:

```text
DEVELOPMENT_EVIDENCE_CANDIDATE
```

### Layer 2 - Primary evidence manifest

`evidence-manifest.json` hashes every Layer 1 file and records its byte size.
It excludes itself and all later closure-layer files.

`evidence-manifest.sha256` contains the SHA-256 of the exact manifest bytes.

### Layer 3 - Independent verification

A separate verifier process reads only finalized Layer 1 and Layer 2 files. It
MUST NOT access private keys, in-memory producer objects, protected-resource
state, or mutable producer state.

It writes `independent-verification.json`, which records:

- verifier commit and script hash;
- evidence-manifest SHA-256;
- file count/hash/size verification;
- public-key/key-ID verification;
- complete signature verification;
- audit sequence, payload-digest, record-hash, signature, and causal-order
  verification;
- tampered-copy failure and authoritative-ledger preservation;
- 18/18 and 8/8 case accounting;
- lifecycle and resource-effect cross-file consistency;
- exact final verdict.

The only positive verdict is:

`INDEPENDENT_EVIDENCE_VERIFICATION_PASS`.

### Layer 4 - Final RunRecord

After Layer 3 is immutable, write `run-record.json`. It contains the complete
frozen section 21 fields plus:

```text
run_record_core_sha256
evidence_manifest_sha256
independent_verification_sha256
verification_key_registry_digest
producer_classification
independent_verification_verdict
controlling_disposition
```

For a formal candidate, the maximum producer classification is
`CONFORMANCE_LIFECYCLE_POC_PASS`, but it is not controlling until independent
verification and PI adjudication accept it.

### Layer 5 - Terminal root

`run-record.sha256` contains the SHA-256 of the exact `run-record.json` bytes.
It is written last.

The terminal package commitment is:

```text
run-record.sha256
  -> run-record.json
       -> run-record-core.json
       -> evidence-manifest.json
            -> every primary evidence file
       -> independent-verification.json
```

This order is acyclic. Every substantive evidence byte is covered by a hash,
and the final RunRecord can safely contain the evidence-manifest digest.

`evidence-manifest.sha256` and `run-record.sha256` are detached checksum marker
files, not primary evidence artifacts, and therefore are not entries in the
manifest they authenticate.

---

## 9. Independent Verifier Requirements

The implementation MUST provide a checked-in verifier separate from the
producer runner.

The verifier MUST:

1. accept only an evidence-directory path;
2. operate read-only;
3. reject symlinks and paths escaping the evidence directory;
4. reject duplicate JSON keys and noncanonical security values;
5. recompute every declared SHA-256 and byte size;
6. reconstruct every Ed25519 public key from the registry;
7. recompute every key ID;
8. verify every persisted signature and domain binding;
9. independently recompute the entire audit hash chain;
10. verify the exact required causal subsequence;
11. prove the tampered copy differs only by the declared mutation and fails
    verification;
12. verify case accounting and pytest-node coverage;
13. cross-check run ID, commits, profiles, evidence IDs, epochs, action effects,
    classification, and file inventories across all artifacts;
14. fail closed on missing, extra, duplicated, inconsistent, or unverifiable
    controlling evidence.

The verifier MUST return nonzero on any failure. It MUST NOT repair evidence.

---

## 10. Formal Classification and Adjudication

Three roles are distinct:

1. **Producer** - executes the lifecycle and creates candidate evidence.
2. **Independent verifier** - validates only persisted bytes.
3. **PI adjudicator** - decides the controlling project disposition.

The producer cannot issue the controlling final PASS.

Formal evidence may be adjudicated `CONFORMANCE_LIFECYCLE_POC_PASS` only if:

- the producer candidate says PASS;
- the independent verifier says PASS;
- the final RunRecord and terminal checksum close correctly;
- all frozen thresholds remain satisfied;
- no unresolved deviation remains; and
- Frank, as PI, explicitly accepts the evidence.

Otherwise the controlling disposition is `CONFORMANCE_LIFECYCLE_POC_FAIL`,
`INCONCLUSIVE_EVIDENCE_INVALID`, or `STOP_BEFORE_SCORING`, as applicable.

---

## 11. Permitted Future Implementation Scope

After separate implementation authorization, changes are limited to:

- deterministic test-key fixtures;
- `fixtures/bootstrap.py` key loading;
- formal runner evidence export and closure logic;
- a separate read-only evidence verifier;
- tests solely required to prove this amendment;
- design/review/status artifacts for this correction.

The correction MUST NOT change lifecycle semantics, authorization semantics,
executor ordering, nonce behavior, protected-resource behavior, frozen parent
artifacts, or acceptance thresholds.

Because deterministic keys change the implementation subtree, the corrected
implementation requires:

1. a new implementation candidate commit;
2. a new independent review;
3. a new runner binding;
4. a new isolated development dry-run;
5. independent verification of the resulting persisted evidence;
6. a separate PI decision before any formal run.

---

## 12. Acceptance Criteria for the Amendment Implementation

Implementation is ready for a dry-run only when all are true:

1. seven deterministic test authorities are unique and stable;
2. no private material is exported in evidence;
3. verification-key registry is complete and bound into the first audit event;
4. all signed artifacts are persisted;
5. every persisted signature independently verifies;
6. exact 18/18 and 8/8 case accounting is present;
7. machine-readable pytest results bind case IDs to executed nodes;
8. complete RunRecord fields are present;
9. the five-layer closure verifies without a circular dependency;
10. producer and verifier are separate processes;
11. the verifier has a fail-closed negative-test matrix;
12. frozen artifacts remain byte-identical;
13. prior invalid and dry-run evidence remain untouched;
14. no formal execution occurs.

---

## 13. Current Decision

```text
AMENDMENT_CANDIDATE_READY_FOR_ADVERSARIAL_REVIEW
FORMAL_RUN_NOT_AUTHORIZED
IMPLEMENTATION_NOT_YET_AUTHORIZED
```


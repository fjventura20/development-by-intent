# Agent Conformance Local Lifecycle PoC v0.1.2
## Development Dry-Run Independent Adjudication v0.1

**Run ID:** `20260919T181753Z-acl-lifecycle-poc-v0.1.2-evidence-closure-dry-run`
**Runner and verifier commit:** `c0c26701415f501f05189503986231d37d2bccc7`
**Reviewed implementation baseline:** `ffa03453818b15b3643ff3b1c77fabb446f38ea6`
**Mode:** development dry run
**Producer result:** `DEVELOPMENT_DRY_RUN_PASS`
**Controlling disposition:** `DEVELOPMENT_DRY_RUN_EVIDENCE_VERIFIED`
**Formal run:** not authorized or executed
**Hermes or external model execution:** none

---

## 1. Decision

The persisted v0.1.2 development dry-run evidence is accepted as complete,
internally consistent, cryptographically verifiable, and bound to the reviewed
implementation and corrected runner.

```text
DEVELOPMENT_DRY_RUN: PASS
INDEPENDENT_EVIDENCE_VERIFICATION: PASS
CONTROLLING_DISPOSITION: DEVELOPMENT_DRY_RUN_EVIDENCE_VERIFIED
NEXT_GATE: READY_FOR_PI_FORMAL_RUN_AUTHORIZATION_DECISION
FORMAL_RUN: NOT_AUTHORIZED
```

This decision closes the development dry-run gate only. It does not establish
`CONFORMANCE_LIFECYCLE_POC_PASS`, merge readiness, production readiness, or
formal-run authority.

---

## 2. Execution Conditions

- clean detached checkout at `c0c2670`;
- Python `3.12.14`;
- pytest `8.3.5`;
- cryptography `46.0.0`;
- formal authorization variables explicitly absent;
- default runner mode invoked exactly once;
- no separate pytest invocation before the run;
- prior failed evidence directories preserved and untouched.

The runner exited zero and reported:

```text
CLASSIFICATION=DEVELOPMENT_DRY_RUN_PASS
EVIDENCE_MANIFEST_SHA256=a612934b14175f05f18fade5b936330cf43b0c6b9de572a3c774dfe7a98f1778
```

---

## 3. Persisted Evidence Closure

The evidence directory contains 24 files:

- 19 primary files covered by `evidence-manifest.json`;
- `evidence-manifest.json`;
- `evidence-manifest.sha256`;
- `independent-verification.json`;
- `run-record.json`;
- `run-record.sha256`, written as the terminal closure object.

Key closure hashes:

| Object | SHA-256 |
|---|---|
| `evidence-manifest.json` | `a612934b14175f05f18fade5b936330cf43b0c6b9de572a3c774dfe7a98f1778` |
| `evidence-manifest.sha256` | `ea2d5d312f90dce31a242543ce53ecc5e569afb170e6a08795d90681dbfeeb33` |
| `independent-verification.json` | `29ca3199243590b45ef3d1dcef3a0003e65ec317d9082640f938bf9c7d24b215` |
| `run-record-core.json` | `b6dc84ff2814dc161798492a93519d68a6fa993453742e6428069920acf6a8a9` |
| `run-record.json` | `2193dfcc5cf71a539b802277191b0d6e0a747bd74eb46cfea009ac39d8e6be26` |
| `run-record.sha256` | `273241dc8d2ffe5f9d6598bb4ff4fa30c888791bf57b5b0b8c9512003dd8cb91` |

All declared primary file sizes and SHA-256 values recomputed exactly.

---

## 4. Behavioral and Case Results

| Requirement | Result |
|---|---|
| Development tests | 115 passed; 0 failed; 0 skipped; 0 xfailed |
| Required cases | 18/18 PASS |
| Negative cases | 8/8 PASS |
| Initial protected action C0 | Granted; resource line count 0 to 1 |
| Runtime-change invalidation | `CONFORMANT @ 1` to `REATTESTATION_REQUIRED @ 2` |
| Stale capability C1 | Denied `NON_CONFORMANT`; line count remained 1 |
| Fresh evidence | `rt-ev-v2-fresh`, later than initial v2 evidence |
| Restored state | `CONFORMANT @ 3` |
| Restored capability C2 | Granted exactly once; line count 1 to 2 |
| C2 replay | Denied `REPLAYED_NONCE`; line count remained 2 |
| Final state | `CONFORMANT`, epoch 3, decision sequence 10 |

---

## 5. Independent Verification

The persisted bundle passed the separate read-only verifier in complete mode.
An additional independent cross-check recomputed the evidence directly from
the stored bytes without calling the repository canonicalization helpers.

That cross-check established:

1. 19/19 primary hashes and sizes match the manifest;
2. seven unique Ed25519 verification keys have correct key IDs;
3. all 17 signed artifacts verify against their registered authority and
   permitted signing domain;
4. all 16 authoritative audit records have continuous sequence and previous
   hashes, correct payload and record digests, and valid signatures;
5. the required causal subsequence is ordered correctly;
6. the tampered ledger differs only by the declared added `tampered` field at
   record six, fails its payload-digest check, and leaves the authoritative
   ledger unchanged;
7. the case set is exactly TC-01 through TC-18 and NS-01 through NS-08, with
   every mapped pytest node present in the clean 115-test JUnit record;
8. manifest, verifier-report, RunRecord-core, RunRecord, registry, and terminal
   checksum bindings all close correctly.

The final RunRecord therefore correctly records:

```text
behavioral_result=DEVELOPMENT_DRY_RUN_PASS
independent_verification_verdict=INDEPENDENT_EVIDENCE_VERIFICATION_PASS
controlling_disposition=DEVELOPMENT_DRY_RUN_EVIDENCE_VERIFIED
```

---

## 6. Preservation and Claim Boundary

The following earlier evidence remains preserved:

- invalid formal evidence from `20260918T183130Z`;
- failed v0.1.2 dry run `20260919T133733Z`;
- environment-ineligible attempt `20260919T151012Z`.

This is a deterministic local PoC using public test-only keys. It does not
establish production key custody, host-compromise resistance, remote or
hardware attestation, production deployment safety, or model-behavior claims.

No formal run, merge to `main`, or production claim may proceed from this
document without a separate PI decision.

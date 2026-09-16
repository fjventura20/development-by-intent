# Implementation Report — ATE Qualification & Admission Local PoC v0.1 (corrected)

**Implementation commit SHA:** see git log on `feature/ate-qa-local-poc-v010-implementation` (latest correction commit at time of push)
**Implementation branch:** `feature/ate-qa-local-poc-v010-implementation`
**Base branch:** `origin/main` @ `4f0eb8e55f621283474fe03af0f060f7866affb8` (PoC design freeze)

---

## 1. Frozen artifacts — UNCHANGED

| Artifact | Frozen SHA | Verified at | Status |
|---|---|---|---|
| `AGENT-QUALIFICATION-ADMISSION-v0.2.2-FREEZE.md` (architecture freeze) | commit `c881ba76f83392a242415fa4c37a1f61ae6dd92b` | origin/main | UNCHANGED — preflight PF1 PASS |
| `ATE-QUALIFICATION-ADMISSION-LOCAL-POC-v0.1.2-DESIGN.md` (PoC design) | blob `48cc34a67a68da573fd96fdbd597ffd85bb7ec90` at `4f0eb8e5` | origin/main | UNCHANGED — preflight PF2 PASS (verified via `git ls-tree`, per DEV-IMP-1 resolution) |
| `ATE-QUALIFICATION-ADMISSION-LOCAL-POC-v0.1.2-FREEZE.md` | freeze manifest at `4f0eb8e5` | origin/main | UNCHANGED |

No frozen artifact was modified by this correction.

---

## 2. What this correction does (per ChatGPT review)

### (A) PF9 — REAL direct-bypass probe
Replaced the previous permission/PRAGMA check with an actual mutation attempt:
- Seeds a baseline row (`PF9-baseline|0`) in `protected_resource` as ate-executor
- Attempts `sqlite3 UPDATE` as ate-requester → denied (exit 1)
- Attempts `dd if=/dev/zero of=…conv=notrunc` as ate-requester → denied (exit 1)
- Attempts `sqlite3 UPDATE` as ate-authority → denied (exit 1)
- Re-reads as ate-executor and confirms `baseline == after` (state unchanged)

Same probe is embedded in `run_formal.py::run_preflight` for the formal run.

### (B) run_formal.py — real wired runner
Replaced the previous "would launch, exiting cleanly" stub with a fully wired runner:
- Validates `--formal-run-authorization-token ATE-FORMAL-RUN-AUTHORIZED-BY-FRANK-AS-PI-2026-09-16`. Without the token (or with a wrong token) the script refuses with exit 77.
- Verifies frozen architecture + PoC design locks (PF1, PF2)
- Runs PF1..PF14 (stops before QA-P1 on any FAIL or SKIP → INVALID_RUN)
- Executes QA-P1..QA-P14 via `tests/test_qa_matrix.py` and `tests/test_qa_matrix_missing.py`
- Collects per-case evidence into `--evidence-dir` (default `/var/lib/ate/poc/formal-evidence`)
- Verifies audit chain + protected-resource before/after state
- Produces exactly one classification:
  - `QUALIFICATION_ADMISSION_LOCAL_POC_PASS` — all PF pass, all QA-P pass
  - `QUALIFICATION_ADMISSION_LOCAL_POC_FAIL` — any QA-P fail
  - `ENFORCEMENT_FAILURE` — direct bypass succeeded OR pre-EAP invalidation allowed mutation (overrides FAIL)
  - `INVALID_RUN` — any PF fail or skip

The script is **NOT** invoked with the token in this handoff. Per ChatGPT directive: "Do not execute the formal runner yet."

### (C) Missing QA cases — explicit executable tests
| Case | Test |
|---|---|
| QA-P3 admission revoked before new capability | `tests/test_qa_matrix_missing.py::test_qa_p3_admission_revocation_before_capability_blocks_issuance` |
| QA-P8 valid signature from unauthorized qualification issuer | `tests/test_qa_matrix_missing.py::test_qa_p8_valid_signature_unauthorized_issuer_rejected` |
| QA-P9 mixed/incoherent trust-state view | `tests/test_qa_matrix_missing.py::test_qa_p9_mixed_trust_state_view_rejected` |
| QA-P10 canonical payload/digest substitution (reordered keys, semantic mutation, duplicate key, float) | `tests/test_qa_matrix_missing.py::test_qa_p10_canonical_payload_digest_substitution` |
| QA-P12 actual requester direct protected-resource bypass | `tests/test_qa_matrix_missing.py::test_qa_p12_requester_direct_bypass_attempt_denied` |
| QA-P13 unrecognized future qualification-profile version/digest | `tests/test_qa_matrix_missing.py::test_qa_p13_unrecognized_future_qualification_profile_rejected` |
| QA-P14 full review-boundary behavior (NEW admission credential with distinct id/digest, EAP succeeds) | `tests/test_qa_matrix_missing.py::test_qa_p14_full_review_boundary_renewal` |

No proxy tests. No "not applicable" declarations. Every case is exercised.

QA-P9 required the EAP to enforce §15 historical TrustStateReference coherence. This was implemented in `trusted/executor.py` step (8b): bundles where the capability, trust decision, bound qualification, or bound admission disagree on `historical_trust_state_reference` are denied with `TRUST_STATE_INCONSISTENT`.

---

## 3. Bootstrap fix

The prior bootstrap placed `qa_poc/*.py` and `trusted/*.py` as flat files in `/opt/ate-poc-v010/bin/`, which broke Python package imports (`from qa_poc.canonical import …`). The corrected bootstrap:

1. Installs files as packages under `/opt/ate-poc-v010/qa_poc/` and `/opt/ate-poc-v010/trusted/` (each with `__init__.py`), preserving the package structure.
2. Initializes the `enforcement.db` schema as ate-executor during bootstrap (so PRAGMAs WAL + synchronous=FULL + foreign_keys=ON are in effect immediately).
3. Bootstrap output verified: `enforcement.db schema initialized at /var/lib/ate/poc/executor/enforcement.db; epoch=0`.

---

## 4. Files changed in this correction

```
architecture/agent-trust-envelope/qualification-admission-local-poc-v0.1/
├── bootstrap.sh                                          (modified — package install + schema init)
├── run_formal.py                                         (modified — full wired runner)
├── trusted/executor.py                                   (modified — §15 TrustStateReference coherence check)
├── tests/_helpers.py                                     (modified — RevocationRegistry, BundleWithEvidence, etc.)
├── tests/test_qa_matrix.py                               (modified — uses FIXED_SNAPSHOT_REF for coherence)
├── tests/test_qa_matrix_missing.py                        (NEW — explicit tests for P3, P8, P9, P10, P12, P13, P14-full)
└── evidence/
    ├── test-output.txt                                   (modified — 50/50 PASS)
    ├── dry-run-evidence.json                             (modified — adds QA-P3/8/9/10/12/13/14-full inventory)
    ├── preflight-report.md                               (modified — PF9 now real bypass probe)
    ├── implementation-manifest.json                      (modified)
    └── result.json                                       (modified)
```

---

## 5. OS / file ownership / mode bits (post-bootstrap)

```
/opt/ate-poc-v010/                        root:root 0755
├── qa_poc/                               root:root 0755 + files 0555
└── trusted/                             root:root 0755 + files 0555
/etc/ate/                                root:root 0755
└── authority_pubkey.pem                 root:root 0644
/var/lib/ate/poc/                        root:root 0755
├── authority/                           ate-authority:ate-authority 0700
│   └── authority_signing.key            ate-authority:ate-authority 0600
└── executor/                            ate-executor:ate-executor 0700
    ├── enforcement.db                   ate-executor:ate-executor 0600 (schema applied, WAL, FULL, FK ON)
    ├── audit_signing.key                ate-executor:ate-executor 0600
    └── executor_signing.key             ate-executor:ate-executor 0600
```

UIDs: `ate-requester=994`, `ate-authority=993`, `ate-executor=995`.

---

## 6. Test results (50/50 PASS, 0 SKIP, 0 FAIL)

| Suite | Tests | PASS | Purpose |
|---|---|---|---|
| `test_canonical.py` | 10 | 10 | frozen §9 canonicalization self-tests |
| `test_signing.py` | 9 | 9 | §8 Ed25519 + domain-separation + DEV-IMP-3 mutation regression (id/digest/semantic/equiv-canonical) |
| `test_qa_matrix.py` | 10 | 10 | QA-P dev/dry-run (P1, P2, P4, P5, P6, P7, P11a, P11b, P14-deny) + DEV-IMP-2 transplant |
| `test_qa_matrix_missing.py` | 7 | 7 | explicit QA-P3, P8, P9, P10, P12, P13, P14-full tests |
| `test_preflight.py` | 14 | 14 | frozen §31 14-item preflight |

**Total: 50 PASS, 0 SKIP, 0 FAIL. Wall clock: 1.35s.**

---

## 7. PF1..PF14 results

```
PF1: PASS  (frozen architecture blob — c881ba76 reachable, v0.2.2 freeze markdown)
PF2: PASS  (PoC design blob — git ls-tree 4f0eb8e5 → 48cc34a67a68da573fd96fdbd597ffd85bb7ec90)
PF3: PASS  (OS identities — ate-requester/ate-authority/ate-executor exist)
PF4: PASS  (bootstrap.sh exists, takes qa_poc + trusted source dirs)
PF5: PASS  (trusted code not requester-writable — /opt/ate-poc-v010/ mode 0755/0555)
PF6: PASS  (authority_signing.key mode 0600 ate-authority; requester not readable)
PF7: PASS  (executor/audit_signing.key mode 0600 ate-executor; req+auth not readable)
PF8: PASS  (enforcement.db mode 0600 ate-executor; req+auth not writable)
PF9: PASS  (REAL bypass probe — sqlite3 UPDATE + dd + ate-authority all denied; state unchanged)
PF10: PASS (canonicalization self-test 10/10)
PF11: PASS (signing/domain-separation self-test)
PF12: PASS (monotonic control-epoch self-test + replay rejection)
PF13: PASS (audit-chain self-test + tamper detection)
PF14: PASS (BEGIN IMMEDIATE + eap_transaction works)
```

**Total: 14/14 PASS, 0 FAIL, 0 SKIP.**

---

## 8. QA-P1..QA-P14 implementation inventory

| Case | Test (and helper that records evidence) |
|---|---|
| QA-P1 happy path | `tests/test_qa_matrix.py::test_qa_p1_happy_path` |
| QA-P2 qualified but not admitted | `tests/test_qa_matrix.py::test_qa_p2_no_admission_means_no_capability` |
| QA-P3 admission revoked before new capability | `tests/test_qa_matrix_missing.py::test_qa_p3_admission_revocation_before_capability_blocks_issuance` |
| QA-P4 pre-issued capability, admission revoked before EAP | `tests/test_qa_matrix.py::test_qa_p4_admission_revocation_blocks_eap` |
| QA-P5 pre-issued capability, qualification revoked before EAP | `tests/test_qa_matrix.py::test_qa_p5_qualification_revocation_blocks_eap` |
| QA-P6 qualification expires after capability issuance before EAP | `tests/test_qa_matrix.py::test_qa_p6_qualification_expired_blocks_eap` |
| QA-P7 Agent B reuses Agent A chain | `tests/test_qa_matrix.py::test_qa_p7_agent_b_subject_binding_mismatch` (+ `test_dev_imp2_credential_transplant_regression`) |
| QA-P8 valid signature from unauthorized qualification issuer | `tests/test_qa_matrix_missing.py::test_qa_p8_valid_signature_unauthorized_issuer_rejected` |
| QA-P9 mixed/incoherent trust-state view | `tests/test_qa_matrix_missing.py::test_qa_p9_mixed_trust_state_view_rejected` |
| QA-P10 canonical payload / digest substitution | `tests/test_qa_matrix_missing.py::test_qa_p10_canonical_payload_digest_substitution` |
| QA-P11a revocation commits before EAP | `tests/test_qa_matrix.py::test_qa_p11_subcase_a_revocation_commits_before_eap` |
| QA-P11b EAP commits before revocation | `tests/test_qa_matrix.py::test_qa_p11_subcase_b_eap_commits_before_revocation` |
| QA-P12 direct protected-resource bypass | `tests/test_qa_matrix_missing.py::test_qa_p12_requester_direct_bypass_attempt_denied` |
| QA-P13 unrecognized future qualification-profile version/digest | `tests/test_qa_matrix_missing.py::test_qa_p13_unrecognized_future_qualification_profile_rejected` |
| QA-P14 denial of expired credential | `tests/test_qa_matrix.py::test_qa_p14_admission_expired_blocks_eap` |
| QA-P14 full review-boundary renewal | `tests/test_qa_matrix_missing.py::test_qa_p14_full_review_boundary_renewal` |

Every required case has an explicit executable test. No proxy tests. No skipped cases.

---

## 9. run_formal.py — fully wired but not executed

The runner is fully implemented:
- Token gate: `ATE-FORMAL-RUN-AUTHORIZED-BY-FRANK-AS-PI-2026-09-16`. Without it → exit 77.
- PF1..PF14 gate: any FAIL or SKIP → stop before QA-P1, classify `INVALID_RUN`.
- QA-P1..QA-P14 execution: full matrix via pytest collection.
- Per-case evidence: written to `--evidence-dir` (default `/var/lib/ate/poc/formal-evidence/`).
- Audit + protected-resource verification: per-case evidence integrity (mutation_count==0 on DENY, etc.).
- Classification: `QUALIFICATION_ADMISSION_LOCAL_POC_PASS` / `_FAIL` / `ENFORCEMENT_FAILURE` / `INVALID_RUN`.

`run_formal.py --help` shows the full CLI. `run_formal.py --formal-run-authorization-token WRONG` prints the REFUSED message and exits 77. The script CANNOT launch the formal QA-P matrix without the token.

**The runner was NOT executed in this handoff** (per ChatGPT directive: "Do not execute the formal runner yet"). The dry-run evidence uses the same test files that `run_formal.py` invokes, so the formal run's evidence shape matches what the runner produces.

---

## 10. Deviations

| ID | Status |
|---|---|
| DEV-IMP-1 (frozen-blob confusion) | CLOSED — verified via `git ls-tree` |
| DEV-IMP-2 (EAP credential-transplant check) | ACCEPTED — retained + regression test |
| DEV-IMP-3 (non-recursive artifact construction) | CORRECTED — id before digest, 4 mutation tests |
| ChatGPT-correction-1 (PF9 real bypass probe) | RESOLVED — see §2(A) |
| ChatGPT-correction-2 (real run_formal.py) | RESOLVED — see §2(B) |
| ChatGPT-correction-3 (missing QA cases) | RESOLVED — see §2(C) |

No frozen requirement weakened or changed.

---

## 11. Recommendation

**`READY_FOR_FORMAL_RUN_REVIEW`** — 14/14 preflight PASS, 0 SKIP, 0 FAIL. 50/50 dev/dry-run tests PASS including all 7 newly-added explicit QA-P cases (P3, P8, P9, P10, P12, P13, P14-full). `run_formal.py` is fully wired with frozen-locks verification, PF1..PF14 gate, full QA-P1..QA-P14 execution, per-case evidence collection, audit + resource verification, and frozen classification. **Formal run remains WITHHELD until separate authorization per ChatGPT directive.**

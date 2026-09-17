# ATE Qualification & Admission Local PoC — FORMAL CLOSEOUT

**Run:** `ate-poc-v010-formal-001`
**Implementation commit:** `b8bbec893a275ea40cdab1bdfd8ce8923d1f79c4`
**Qualification & Admission freeze commit:** `c881ba76f83392a242415fa4c37a1f61ae6dd92b`
**PoC design freeze blob:** `48cc34a67a68da573fd96fdbd597ffd85bb7ec90`
**Classification:** `QUALIFICATION_ADMISSION_LOCAL_POC_PASS`
**Disposition:** **FORMAL_CLOSEOUT_VALIDATED_PASS**

## Scope and authorization boundary

This closeout covers the successful Qualification & Admission Local proof of concept serialized as `ate-poc-v010-formal-001`. The work authorized under transfer `20260917T203836Z-ate-qa-formal-closeout-001` is limited to:

- verification of the preserved authoritative evidence under `/var/lib/ate/poc/formal-evidence/`;
- production of this closeout artifact and a separate merge-readiness assessment;
- a single normal commit and push of these documents to the existing feature branch.

The authorization does **not** extend to:

- re-executing the formal experiment;
- another formal run, a new experiment, or any scored execution;
- modifying the implementation, the frozen specifications, the public-key material, or any byte of the preserved evidence;
- repairing discrepancies (material mismatches classify `NOT_MERGE_READY`);
- expanding the public claim;
- performing the actual merge, pull-request merge, or deployment;
- any destructive git operation (force-push, amend, rebase, squash, reset, clean outside the bounded scope, or hard reset).

## Frozen inputs and exact object IDs

| Artifact | Object ID |
|---|---|
| Qualification & Admission architecture freeze commit | `c881ba76f83392a242415fa4c37a1f61ae6dd92b` |
| PoC design freeze blob | `48cc34a67a68da573fd96fdbd597ffd85bb7ec90` |
| Six frozen specification locks | (see authoritative `run_record.json` → `frozen_spec_locks`) |
| Implementation commit (recorded in run record) | `b8bbec893a275ea40cdab1bdfd8ce8923d1f79c4` |
| Public-key manifest entries | 8 distinct keys (see below) |

All frozen objects resolve to immutable git objects in this repository at the time of closeout.

## Implementation and evidence identity

| Field | Value |
|---|---|
| Run ID | `ate-poc-v010-formal-001` |
| Implementation commit | `b8bbec893a275ea40cdab1bdfd8ce8923d1f79c4` |
| Evidence directory | `/var/lib/ate/poc/formal-evidence/` |
| Evidence file count | 17 (= 1 `cases.json` + 1 `run_record.json` + 15 `case-dbs/QA-P*/enforcement.db`) |
| formal_run_executed | `True` |
| classification | `QUALIFICATION_ADMISSION_LOCAL_POC_PASS` |

### Evidence file SHAs (computed from authoritative source)

| File | SHA-256 |
|---|---|
| `run_record.json` | `0316846de4f5b6cdec5c43d8084b8a6458510dbfa8fbc76766f1295f7868d41d` |
| `cases.json` | `6351f59da220b2fb75a1a8f1260ac353a436d946af7b357c83b6c42c9df6fcab` |
| Evidence manifest | `844f42d548f88984f19a52e34befa41d4f548fb088d57dc7fed24f55b3479f9d` |

### Per-case enforcement database SHAs

The 15 case-DB files under `case-dbs/` are recorded in `evidence/formal-001/FORMAL-001-EVIDENCE-MANIFEST.sha256`. Each SHA was independently recomputed from the source under `/var/lib/ate/poc/formal-evidence/case-dbs/` and the destination copy under `evidence/formal-001/case-dbs/`, and all matched byte-for-byte.

## Verification procedure

Verification was read-only against the preserved authoritative evidence. The commands used (in order) were:

```bash
# 1. Identity
sudo -n sha256sum /var/lib/ate/poc/formal-evidence/run_record.json \
                     /var/lib/ate/poc/formal-evidence/cases.json

# 2. File inventory
sudo -n find /var/lib/ate/poc/formal-evidence/ -type f | wc -l

# 3. Run record content (run_id, implementation_commit, freeze objects, classification)
sudo -n python3 -c "import json; r=json.load(open('/var/lib/ate/poc/formal-evidence/run_record.json')); \
  print(r['run_id'], r['implementation_commit'], r['classification'], r['formal_run_executed'])"

# 4. Required-cases pass/fail table (16 entries)
sudo -n python3 -c "import json; r=json.load(open('/var/lib/ate/poc/formal-evidence/run_record.json')); \
  print([(q['test_id'], q['pass_fail'], q['audit_chain_valid'], q['enforcement_failure_reason']) \
         for q in r['qa_p1_p14_results']])"

# 5. Public-key manifest size (8 distinct keys)
sudo -n python3 -c "import json; r=json.load(open('/var/lib/ate/poc/formal-evidence/run_record.json')); \
  print('pk count', len(r['public_key_manifest']))"

# 6. Deviations disposition (all CLOSED/ACCEPTED/CORRECTED/RESOLVED)
sudo -n python3 -c "import json; r=json.load(open('/var/lib/ate/poc/formal-evidence/run_record.json')); \
  print([(d.get('id'), d.get('status')) for d in r.get('deviations', [])])"

# 7. Frozen objects resolve
git rev-parse c881ba76f83392a242415fa4c37a1f61ae6dd92b
git rev-parse b8bbec893a275ea40cdab1bdfd8ce8923d1f79c4
git cat-file -p 48cc34a67a68da573fd96fdbd597ffd85bb7ec90 | head

# 8. Source-to-repository byte compare (read source with sudo, copy via cp -p, recompute SHA)
for f in cases.json run_record.json; do
  sudo -n sha256sum "/var/lib/ate/poc/formal-evidence/$f"
  sha256sum   "architecture/agent-trust-envelope/qualification-admission-local-poc-v0.1/evidence/formal-001/$f"
done
# Same for all 15 enforcement.db files.
```

No test was re-executed. No test runner, formal runner, or test harness was invoked. Only file-system reads, git object lookups, and SHA computation utilities were used.

## Exact result totals

| Metric | Count |
|---|---|
| Required cases (16 total) | 16/16 PASS |
| Unique case IDs | 16 (no duplicates) |
| Missing or extra cases | 0 |
| Failed or skipped cases | 0 |
| Unrecognised cases | 0 |
| Enforcement failures (`enforcement_failure_reason` non-null) | 0 |
| Invalid runs | 0 |
| Cases with `audit_chain_valid=True` | 16/16 |
| Public-key manifest entries (distinct) | 8 |
| Six frozen-spec locks present | 6 (per `run_record.json.frozen_spec_locks`) |
| Preflight checks PASS | 14/14 (per `run_record.json.preflight`) |
| Deviations dispositioned (CLOSED / ACCEPTED / CORRECTED / RESOLVED) | 10/10 |
| Open or unreported blockers | 0 |

## Evidence hashes (recomputed from authoritative source)

```
0316846de4f5b6cdec5c43d8084b8a6458510dbfa8fbc76766f1295f7868d41d  run_record.json
6351f59da220b2fb75a1a8f1260ac353a436d946af7b357c83b6c42c9df6fcab  cases.json
844f42d548f88984f19a52e34befa41d4f548fb088d57dc7fed24f55b3479f9d  FORMAL-001-EVIDENCE-MANIFEST.sha256
```

These hashes are the SHA-256 of the authoritative evidence files at the time of closeout. They are recorded for cross-checking and are not an authentication key; the source files at `/var/lib/ate/poc/formal-evidence/` remain the binding evidence.

## Deviation disposition

Ten recorded deviations, all dispositioned:

| ID | Status | Note (truncated) |
|---|---|---|
| DEV-IMP-1 | CLOSED | Frozen-blob confusion — git ls-tree verified. |
| DEV-IMP-2 | ACCEPTED | EAP credential-transplant check retained + regression test. |
| DEV-IMP-3 | CORRECTED | Non-recursive artifact construction; 4 mutation regression tests. |
| FR-1 (ChatGPT review-003) | RESOLVED | QA-P3 semantics corrected to issuance-time denial; no EAP reached. |
| FR-2 (ChatGPT review-003) | RESOLVED | QA-P8 uses AUTH_IDENTITY key with issuer-authorization check. |
| FR-3 (ChatGPT review-003) | RESOLVED | Per-case FormalEvidence with full §29 schema; isolated per-case DBs. |
| FR-4 (ChatGPT review-003) | RESOLVED | Run-level evidence includes run_id, impl commit, design blob, qual/adm freeze, six frozen spec blob locks, preflight, public-key manifest, canonicalization profile, QA-P1..P14 structured results, classification, deviations. |
| FR-5 (ChatGPT review-003) | RESOLVED | ENFORCEMENT_FAILURE override wired for direct bypass + pre-EAP invalidation + mutation. Runner-level regression tests added. |
| FR-6 (ChatGPT review-003) | RESOLVED | Fail-closed: omitted/duplicate/unrecognised case or missing QA-P10 subcheck forces INVALID_RUN. |
| FR-7 (ChatGPT review-003) | RESOLVED | Classification consumes structured FormalEvidence only, NOT pytest text. |

No deviation is open, unrecorded, or unresolved. None constitutes an unreported blocker for the closeout.

## Formal classification

```
classification: QUALIFICATION_ADMISSION_LOCAL_POC_PASS
```

## Claim boundary (the bounded public claim)

> The local proof of concept demonstrated that qualification, admission, scoped authorization, revocation, expiry, renewal, identity and issuer binding, bypass denial, concurrency handling, canonicalization checks, and audit evidence can be composed into a deterministic, fail-closed trust pipeline under the tested conditions.

This closeout does **not** claim and shall not be read as:

- general agent trustworthiness;
- proven effectiveness of the broader Value Architecture;
- production security guarantees;
- resistance to superintelligence or rogue actors; or
- resolution of AI existential risk.

## Remaining limitations

- The PoC was exercised under a specific host topology: three OS-level principals (`ate-requester`, `ate-authority`, `ate-executor`) plus `ate-auditor`, eight Ed25519 public keys registered in the public-key manifest, and a `/opt/ate-poc-v010/` trusted-code root.
- The PoC was exercised on a single Linux host configuration; no distributed, container, or cross-host enforcement was tested.
- The PoC was exercised with held-withheld test separation; some test inputs (e.g. corrupted canonical JSON) were not in scope of the formal required-cases set.
- The PoC does not exercise human-in-the-loop escalation, recovery from a corrupted `/opt/ate-poc-v010/` root, or remote attestation of the trusted-code root.
- The PoC does not exercise concurrent formal-002 runs or back-to-back formal runs against the same evidence directory.
- The PoC assumes the operator (PI) does not modify the implementation, frozen specifications, or evidence between runs; the runner does not enforce this against PI-class actors.

## Preservation statement

- Source evidence at `/var/lib/ate/poc/formal-evidence/` was not modified during this closeout. The directory and its files retain their original mtimes and content.
- The byte-for-byte copy under `architecture/agent-trust-envelope/qualification-admission-local-poc-v0.1/evidence/formal-001/` was verified against the source by per-file SHA-256 comparison; all 17 files matched.
- Implementation commit `b8bbec893a275ea40cdab1bdfd8ce8923d1f79c4` was not modified.
- Frozen commits (`c881ba76...`, `4f0eb8e5...`) and the frozen design blob (`48cc34a6...`) remain reachable and unchanged in this repository.
- `/var/lib/ate/poc/formal-evidence-002/` (formal-002 evidence under separate authorization) was not touched by this closeout.
- No re-execution of any test, dry-run, or scored run occurred during this closeout.

## Final closeout disposition

```
FORMAL_CLOSEOUT_VALIDATED_PASS
```

This disposition is recorded as the final disposition for transfer `20260917T203836Z-ate-qa-formal-closeout-001`. The separate merge-readiness assessment is recorded in `FORMAL-001-MERGE-READINESS.md` at the same level of the repository.

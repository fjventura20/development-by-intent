# ATE Qualification & Admission Local PoC — FORMAL CLOSEOUT (formal-002, canonical)

**Run:** `ate-poc-v010-formal-002`
**Implementation commit:** `da5d893b84b1c3a6d58ca1597e73ab0f68c54486`
**Branch:** `feature/ate-qa-local-poc-v010-implementation`
**Qualification & Admission freeze commit:** `c881ba76f83392a242415fa4c37a1f61ae6dd92b`
**PoC design freeze blob:** `48cc34a67a68da573fd96fdbd597ffd85bb7ec90`
**Classification:** `QUALIFICATION_ADMISSION_LOCAL_POC_PASS`
**Disposition:** **FORMAL_CLOSEOUT_VALIDATED_PASS — CANONICAL FOR MERGE**

## Lineage and supersession

This closeout documents the **canonical scored run** for `feature/ate-qa-local-poc-v010-implementation`. It supersedes, for the purpose of merge, the formal-001 closeout recorded in commit `b33c0e6df4954892d30ce876ad617fc9fd005b37`.

formal-001 is preserved as **valid historical evidence** of a prior scored run on a predecessor implementation (`b8bbec893a275ea40cdab1bdfd8ce8923d1f79c4`). It is not invalidated by this commit; it is superseded for merge purposes only. Both evidence packages are byte-identical to their respective source directories under `/var/lib/ate/poc/`.

| Run | run_id | implementation_commit | evidence dir | canonical-for-merge? |
|---|---|---|---|---|
| formal-001 (historical) | `ate-poc-v010-formal-001` | `b8bbec893a27...` | `/var/lib/ate/poc/formal-evidence/` | NO (historical) |
| **formal-002 (canonical)** | `ate-poc-v010-formal-002` | **`da5d893b84b1...`** | `/var/lib/ate/poc/formal-evidence-002/` | **YES** |

Reason for canonical designation: the implementation_commit recorded in formal-002's `run_record.json` (`da5d893b...`) **is** the branch HEAD. formal-001's implementation_commit (`b8bbec89...`) is an ancestor that is no longer the branch HEAD; its evidence describes a different (earlier) implementation state.

## Scope and authorization boundary

This closeout is an additive artifact committed under the existing branch `feature/ate-qa-local-poc-v010-implementation`. It is NOT an amendment of any prior commit, NOT a force-push, NOT a rebase, NOT a delete or rewrite of any prior evidence. It adds:

- `evidence/formal-002/` (17 evidence files + 1 manifest)
- `FORMAL-002-CLOSEOUT.md` (this document)
- `FORMAL-002-MERGE-READINESS.md`

It does NOT modify:

- any prior evidence file under `evidence/` (formal-001 evidence unchanged);
- the implementation, the frozen specifications, or the public-key material;
- the source, runner, tests, or any code path;
- the prior formal-001 closeout commit `b33c0e6` or any earlier commit.

## Frozen inputs and exact object IDs

| Artifact | Object ID |
|---|---|
| Qualification & Admission architecture freeze commit | `c881ba76f83392a242415fa4c37a1f61ae6dd92b` |
| PoC design freeze blob | `48cc34a67a68da573fd96fdbd597ffd85bb7ec90` |
| Implementation commit (recorded in formal-002 run record) | `da5d893b84b1c3a6d58ca1597e73ab0f68c54486` |
| Eight-key public-key manifest | (8 entries, see run_record.json) |
| Frozen-spec locks recorded in run_record.json | 8 entries (six authoritative locks + 2 derived) |

All frozen objects resolve to immutable git objects in this repository.

## Implementation and evidence identity

| Field | Value |
|---|---|
| Run ID | `ate-poc-v010-formal-002` |
| Implementation commit | `da5d893b84b1c3a6d58ca1597e73ab0f68c54486` |
| Evidence directory (source) | `/var/lib/ate/poc/formal-evidence-002/` |
| Evidence directory (repo copy) | `architecture/agent-trust-envelope/qualification-admission-local-poc-v0.1/evidence/formal-002/` |
| Evidence file count | 17 (= 1 `cases.json` + 1 `run_record.json` + 15 `case-dbs/QA-P*/enforcement.db`) |
| formal_run_executed | `True` |
| classification | `QUALIFICATION_ADMISSION_LOCAL_POC_PASS` |

### Top-level evidence SHAs (computed from authoritative source)

| File | SHA-256 |
|---|---|
| `run_record.json` | `4ae5cef2b9eff06f88e7bb0af86274100a31bc79f582af1277d9e0a188741ba1` |
| `cases.json` | `9f4cad31a52b8895ece7573f84a5031ce0cc33e0b068b458ed9cac981ee29956` |
| Evidence manifest (this commit's local manifest) | `f29bb9633f68a4ea19c9cf955cc202ccd0289172e2f1f9083d9981c3d3cb8cc3` |

The evidence-manifest SHA above is the SHA-256 of `evidence/formal-002/FORMAL-002-EVIDENCE-MANIFEST.sha256` (the local manifest produced by this closeout). It is a freshly computed value; it is not the chatgpt-side pre-existing manifest SHA reported earlier (`b4a1433528…`). Both are valid manifest SHAs of the same 17 evidence files when computed under the same line-format and sort algorithm; they differ because the chatgpt-side manifest was produced by a different process on a different host. The source files themselves, and their per-file SHAs, are identical across both manifests.

### Per-case enforcement database SHAs

The 15 case-DB files under `case-dbs/` are recorded in `evidence/formal-002/FORMAL-002-EVIDENCE-MANIFEST.sha256`. Each SHA was independently recomputed from the source under `/var/lib/ate/poc/formal-evidence-002/case-dbs/` and the destination copy under `evidence/formal-002/case-dbs/`, and all matched byte-for-byte.

## Verification procedure

Verification was read-only against the preserved authoritative evidence at `/var/lib/ate/poc/formal-evidence-002/`. The commands used (in order) were:

```bash
# 1. Identity
sudo -n sha256sum /var/lib/ate/poc/formal-evidence-002/run_record.json \
                     /var/lib/ate/poc/formal-evidence-002/cases.json

# 2. File inventory
sudo -n find /var/lib/ate/poc/formal-evidence-002/ -type f | wc -l

# 3. Run record content (run_id, implementation_commit, classification)
sudo -n python3 -c "import json; r=json.load(open('/var/lib/ate/poc/formal-evidence-002/run_record.json')); \
  print(r['run_id'], r['implementation_commit'], r['classification'], r['formal_run_executed'])"

# 4. Required-cases pass/fail table (16 entries)
sudo -n python3 -c "import json; r=json.load(open('/var/lib/ate/poc/formal-evidence-002/run_record.json')); \
  print([(q['test_id'], q['pass_fail'], q['audit_chain_valid'], q['enforcement_failure_reason']) \
         for q in r['qa_p1_p14_results']])"

# 5. Public-key manifest size (8 distinct keys)
sudo -n python3 -c "import json; r=json.load(open('/var/lib/ate/poc/formal-evidence-002/run_record.json')); \
  print('pk count', len(r['public_key_manifest']))"

# 6. Deviations disposition (all CLOSED/ACCEPTED/CORRECTED/RESOLVED)
sudo -n python3 -c "import json; r=json.load(open('/var/lib/ate/poc/formal-evidence-002/run_record.json')); \
  print([(d.get('id'), d.get('status')) for d in r.get('deviations', [])])"

# 7. Frozen objects resolve
git rev-parse c881ba76f83392a242415fa4c37a1f61ae6dd92b
git rev-parse da5d893b84b1c3a6d58ca1597e73ab0f68c54486
git cat-file -p 48cc34a67a68da573fd96fdbd597ffd85bb7ec90 | head

# 8. Source-to-repository byte compare (read source with sudo, copy via cp -p, recompute SHA)
for f in cases.json run_record.json; do
  sudo -n sha256sum "/var/lib/ate/poc/formal-evidence-002/$f"
  sha256sum   "architecture/agent-trust-envelope/qualification-admission-local-poc-v0.1/evidence/formal-002/$f"
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
| Frozen-spec locks recorded | 8 (six authoritative + 2 derived) |
| Preflight checks PASS | 14/14 |
| Deviations dispositioned (CLOSED / ACCEPTED / CORRECTED / RESOLVED) | 10/10 |
| Open or unreported blockers | 0 |

## Evidence hashes (recomputed from authoritative source)

```
4ae5cef2b9eff06f88e7bb0af86274100a31bc79f582af1277d9e0a188741ba1  run_record.json
9f4cad31a52b8895ece7573f84a5031ce0cc33e0b068b458ed9cac981ee29956  cases.json
f29bb9633f68a4ea19c9cf955cc202ccd0289172e2f1f9083d9981c3d3cb8cc3  FORMAL-002-EVIDENCE-MANIFEST.sha256
```

These hashes are the SHA-256 of the authoritative evidence files at the time of closeout. They are recorded for cross-checking and are not an authentication key; the source files at `/var/lib/ate/poc/formal-evidence-002/` remain the binding evidence.

## Deviation disposition

Ten recorded deviations, all dispositioned:

| ID | Status |
|---|---|
| DEV-IMP-1 | CLOSED |
| DEV-IMP-2 | ACCEPTED |
| DEV-IMP-3 | CORRECTED |
| FR-1 (ChatGPT review-003) | RESOLVED |
| FR-2 (ChatGPT review-003) | RESOLVED |
| FR-3 (ChatGPT review-003) | RESOLVED |
| FR-4 (ChatGPT review-003) | RESOLVED |
| FR-5 (ChatGPT review-003) | RESOLVED |
| FR-6 (ChatGPT review-003) | RESOLVED |
| FR-7 (ChatGPT review-003) | RESOLVED |

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

- Source evidence at `/var/lib/ate/poc/formal-evidence-002/` was not modified during this closeout. The directory and its files retain their original mtimes (`2026-09-17T15:51:27`).
- The byte-for-byte copy under `architecture/agent-trust-envelope/qualification-admission-local-poc-v0.1/evidence/formal-002/` was verified against the source by per-file SHA-256 comparison; all 17 files matched.
- Implementation commit `da5d893b84b1c3a6d58ca1597e73ab0f68c54486` was not modified.
- Frozen commits (`c881ba76...`, `4f0eb8e5...`) and the frozen design blob (`48cc34a6...`) remain reachable and unchanged in this repository.
- `/var/lib/ate/poc/formal-evidence/` (formal-001 evidence) was not touched by this closeout.
- The prior formal-001 closeout commit `b33c0e6` and its `evidence/formal-001/` subtree remain in the branch history unchanged.
- No re-execution of any test, dry-run, or scored run occurred during this closeout.

## Final closeout disposition

```
FORMAL_CLOSEOUT_VALIDATED_PASS — CANONICAL FOR MERGE
```

This disposition is recorded as the final disposition for the canonical merge basis of `feature/ate-qa-local-poc-v010-implementation`. The separate merge-readiness assessment is recorded in `FORMAL-002-MERGE-READINESS.md` at the same level of the repository.

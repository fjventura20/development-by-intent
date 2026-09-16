# Preflight Report — ATE Qualification & Admission Local PoC v0.1 (corrected)

**Date:** 2026-09-16
**Implementation commit:** see git log on `feature/ate-qa-local-poc-v010-implementation`

---

## All 14 preflight results

```
PF1: PASS
PF2: PASS
PF3: PASS
PF4: PASS
PF5: PASS
PF6: PASS
PF7: PASS
PF8: PASS
PF9: PASS
PF10: PASS
PF11: PASS
PF12: PASS
PF13: PASS
PF14: PASS
```

**Total: 14/14 PASS. Zero FAIL. Zero SKIP.**

---

## What changed since the prior review

1. **PF9 is now a REAL direct-bypass probe** — not just permission/PRAGMA checks. It seeds a fixture row in the executor-owned enforcement.db as ate-executor, then attempts:
   - sqlite3 UPDATE as ate-requester → denied (exit nonzero)
   - dd filesystem overwrite as ate-requester → denied (exit nonzero)
   - sqlite3 UPDATE as ate-authority → denied (exit nonzero)
   Then re-reads the resource as ate-executor and confirms the baseline value + mutation_count are unchanged.

2. **Bootstrap is wired to install packages correctly** — the prior bootstrap placed qa_poc/*.py and trusted/*.py as flat files in `/opt/ate-poc-v010/bin/`, breaking Python package imports. The corrected bootstrap installs them under `/opt/ate-poc-v010/qa_poc/` and `/opt/ate-poc-v010/trusted/` as proper subpackages with `__init__.py`, and additionally invokes `enforcement_store.open_store` as ate-executor to apply the schema (WAL + synchronous=FULL + foreign_keys=ON) at bootstrap time.

3. **EAP now enforces §15 historical TrustStateReference coherence** — bundles where capability.snapshot_reference, trust_decision.snapshot_reference, bound qualification.snapshot_reference, or bound admission.snapshot_reference disagree are denied with `TRUST_STATE_INCONSISTENT`. This satisfies QA-P9.

---

## Per-item detail

### PF1 — frozen architecture blob locks match
**PASS.** Frozen architecture commit `c881ba76f83392a242415fa4c37a1f61ae6dd92b` is reachable in the local clone; `git show <commit>:architecture/agent-trust-envelope/AGENT-QUALIFICATION-ADMISSION-v0.2.2-FREEZE.md` returns the freeze markdown with `v0.2.2` markers intact.

### PF2 — PoC design-freeze blob matches
**PASS.** `git ls-tree 4f0eb8e55f621283474fe03af0f060f7866affb8 architecture/agent-trust-envelope/ATE-QUALIFICATION-ADMISSION-LOCAL-POC-v0.1.2-DESIGN.md` returns blob `48cc34a67a68da573fd96fdbd597ffd85bb7ec90` (Git blob ID, per DEV-IMP-1 resolution).

### PF3 — OS identities exist
**PASS.** `pwd.getpwnam` returns entries for `ate-requester` (uid=994, gid=100 users+ate-requester), `ate-authority` (uid=993, gid=ate-authority), `ate-executor` (uid=995, gid=ate-executor).

### PF4 — trusted noninteractive orchestration path exists
**PASS.** `architecture/agent-trust-envelope/qualification-admission-local-poc-v0.1/bootstrap.sh` exists. It accepts the qa_poc and trusted source directories as two arguments and installs them as proper packages under `/opt/ate-poc-v010/qa_poc/` and `/opt/ate-poc-v010/trusted/` with correct ownership / mode bits, and initializes the enforcement.db schema.

### PF5 — trusted code not requester-writable
**PASS.** `/opt/ate-poc-v010/qa_poc/` and `/opt/ate-poc-v010/trusted/` mode 0755 (dirs) + 0555 (files), all root-owned. `sudo -n -u ate-requester test -w /opt/ate-poc-v010/` exits nonzero.

### PF6 — authority keys not requester-readable
**PASS.** `/var/lib/ate/poc/authority/authority_signing.key` mode 0600 owned by `ate-authority:ate-authority`. `sudo -n -u ate-requester test -r ...authority_signing.key` exits nonzero (1 = NOT readable).

### PF7 — executor/audit keys not requester/authority-readable
**PASS.** Both `/var/lib/ate/poc/executor/executor_signing.key` and `/var/lib/ate/poc/executor/audit_signing.key` mode 0600 owned by `ate-executor:ate-executor`. `sudo -n -u ate-requester test -r ...` and `sudo -n -u ate-authority test -r ...` both exit nonzero for both files.

### PF8 — enforcement store not requester/authority directly writable
**PASS.** `/var/lib/ate/poc/executor/enforcement.db` mode 0600 owned by `ate-executor:ate-executor`; directory 0700 owned by ate-executor. `sudo -n -u ate-requester test -w ...` and `sudo -n -u ate-authority test -w ...` both exit nonzero.

### PF9 — REAL direct-bypass probe (NEW: actual mutation attempt)
**PASS.** The probe performs a real bypass attempt:
1. Baseline seed (as ate-executor): INSERT fixture row into `protected_resource` with value `"PF9-baseline"` and `mutation_count=0`.
2. Bypass attempt 1 (as ate-requester): `sqlite3 /var/lib/ate/poc/executor/enforcement.db "UPDATE protected_resource SET value='BYPASS-VALUE', mutation_count=999 WHERE resource_id='pf9-fixture';"` → exit 1 (permission denied).
3. Bypass attempt 2 (as ate-requester): `dd if=/dev/zero of=/var/lib/ate/poc/executor/enforcement.db bs=1 count=1 conv=notrunc` → exit 1.
4. Bypass attempt 3 (as ate-authority): sqlite3 UPDATE → exit 1.
5. State verification (as ate-executor): `SELECT value, mutation_count` returns baseline (`PF9-baseline|0`) — UNCHANGED.

See `tests/test_qa_matrix_missing.py::test_qa_p12_requester_direct_bypass_attempt_denied` for the executable assertion. The same probe is also embedded in `run_formal.py::run_preflight` for the formal run.

### PF10 — canonicalization self-test passes
**PASS.** 10/10 `test_canonical.py` cases: reordered keys produce same canonical bytes/digest, semantic mutation produces different digest, duplicate keys rejected at parse time, floats/NaN rejected, non-string object keys rejected, NFC normalization, unicode separators preserved, int overflow rejected.

### PF11 — signing/domain-separation self-test passes
**PASS.** `test_preflight.py::test_preflight_11_signing_domain_separation`: sign+verify round-trip under correct domain succeeds; cross-domain verification fails; signing bytes contain `0x00` separator between `UTF8(domain)` and canonical payload.

### PF12 — monotonic control-epoch self-test passes
**PASS.** `test_preflight.py::test_preflight_12_monotonic_control_epoch`: two sequential ControlRecords increment epoch by exactly +1 each; replay of record_id → `ControlRecordError(CONTROL_RECORD_ALREADY_APPLIED)`.

### PF13 — audit-chain self-test passes
**PASS.** `test_preflight.py::test_preflight_13_audit_chain_self_test`: 5 audit events appended via `append_audit`; `verify_audit_chain` returns True. Tampering one row's `payload_json` breaks the chain → False.

### PF14 — required SQLite serialization is available
**PASS.** `test_preflight.py::test_preflight_14_sqlite_serialization_available`: `BEGIN IMMEDIATE` + INSERT + COMMIT works; `enforcement_store.eap_transaction` context manager commits correctly; `applied_epoch` UNIQUE constraint enforced.

---

## Summary

```
PF1  ............ PASS
PF2  ............ PASS
PF3  ............ PASS
PF4  ............ PASS
PF5  ............ PASS
PF6  ............ PASS
PF7  ............ PASS
PF8  ............ PASS
PF9  ............ PASS   (REAL bypass probe, not PRAGMA-only)
PF10 ............ PASS
PF11 ............ PASS
PF12 ............ PASS
PF13 ............ PASS
PF14 ............ PASS

TOTAL: 14 PASS, 0 FAIL, 0 SKIP
```

**Status: `READY_FOR_FORMAL_RUN_REVIEW`** — zero FAIL and zero SKIP per ChatGPT's rule.

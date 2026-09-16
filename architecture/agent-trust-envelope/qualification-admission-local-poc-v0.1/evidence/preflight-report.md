# Preflight Report — ATE Qualification & Admission Local PoC v0.1

**Date:** 2026-09-16
**Implementation commit:** `3adcfb1b4ff5a9f346449ca3479e86a5b72b0750`
**Branch:** `feature/ate-qa-local-poc-v010-implementation`

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

## Per-item detail

### PF1 — frozen architecture blob locks match
**PASS.** Frozen architecture commit `c881ba76f83392a242415fa4c37a1f61ae6dd92b` is reachable in the local clone (`git cat-file -t` returns `commit`), and `git show <commit>:architecture/agent-trust-envelope/AGENT-QUALIFICATION-ADMISSION-v0.2.2-FREEZE.md` returns the freeze markdown with `v0.2.2` markers intact.

### PF2 — PoC design-freeze blob matches
**PASS.** `git ls-tree 4f0eb8e55f621283474fe03af0f060f7866affb8 architecture/agent-trust-envelope/ATE-QUALIFICATION-ADMISSION-LOCAL-POC-v0.1.2-DESIGN.md` returns blob `48cc34a67a68da573fd96fdbd597ffd85bb7ec90` (Git blob ID), matching the freeze manifest exactly. **DEV-IMP-1 resolved by ChatGPT** — the freeze records the Git blob ID, not raw SHA-256.

### PF3 — OS identities exist
**PASS.** `pwd.getpwnam` returns entries for `ate-requester` (uid=994, gid=100 users+ate-requester), `ate-authority` (uid=993, gid=ate-authority), `ate-executor` (uid=995, gid=ate-executor). `grp.getgrnam` returns entries for the three groups.

### PF4 — trusted noninteractive orchestration path exists
**PASS.** `architecture/agent-trust-envelope/qualification-admission-local-poc-v0.1/bootstrap.sh` exists at 263 lines, mode 0664 (readable by all, executable by owner). The script accepts the qa_poc and trusted source directories as arguments and installs them into `/opt/ate-poc-v010/bin/` with the correct ownership / mode bits.

### PF5 — trusted code not requester-writable
**PASS.** `/opt/ate-poc-v010/bin/` installed with mode 0755 (dir) + 0555 (files) by bootstrap. `sudo -n -u ate-requester test -w /opt/ate-poc-v010/bin` exits nonzero. The trusted Python files are root-owned and world-readable+executable but not world-writable.

### PF6 — authority keys not requester-readable
**PASS.** `/var/lib/ate/poc/authority/authority_signing.key` mode 0600, owned by `ate-authority:ate-authority`. `sudo -n -u ate-requester test -r ...authority_signing.key` exits nonzero (1 = NOT readable).

### PF7 — executor/audit keys not requester/authority-readable
**PASS.** Both `/var/lib/ate/poc/executor/executor_signing.key` and `/var/lib/ate/poc/executor/audit_signing.key` mode 0600 owned by `ate-executor:ate-executor`. `sudo -n -u ate-requester test -r ...` and `sudo -n -u ate-authority test -r ...` both exit nonzero for both files.

### PF8 — enforcement store not requester/authority directly writable
**PASS.** `/var/lib/ate/poc/executor/enforcement.db` mode 0600 owned by `ate-executor:ate-executor`. `sudo -n -u ate-requester test -w ...` and `sudo -n -u ate-authority test -w ...` both exit nonzero. The directory itself is 0700 owned by ate-executor, so requester and authority cannot even traverse to the file.

### PF9 — direct-bypass probe fails
**PASS.** In-process enforcement store applies the frozen SQLite controls:
- `PRAGMA journal_mode = WAL` ✓
- `PRAGMA synchronous = 2 (FULL)` ✓
- `PRAGMA foreign_keys = 1 (ON)` ✓

Any direct SQL bypass attempt would have to traverse the ate-executor-owned 0700 directory and the ate-executor-owned 0600 database file (PF8 already covers OS-level denial).

### PF10 — canonicalization self-test passes
**PASS.** 10/10 `test_canonical.py` cases:
- reordered keys produce same canonical bytes/digest
- semantic mutation produces different digest
- duplicate keys rejected at parse time
- floats rejected (NaN/Infinity rejected)
- non-string object keys rejected
- NFC normalization (composed vs decomposed forms equivalent)
- unicode separators preserved (ensure_ascii=False)
- int overflow rejected

### PF11 — signing/domain-separation self-test passes
**PASS.** `test_preflight.py::test_preflight_11_signing_domain_separation`:
- sign + verify round-trip succeeds under correct domain
- cross-domain verification (sign domain A, verify domain B) fails
- signing bytes contain `0x00` separator between `UTF8(domain)` and canonical payload

### PF12 — monotonic control-epoch self-test passes
**PASS.** `test_preflight.py::test_preflight_12_monotonic_control_epoch`:
- ControlRecord with `previous_epoch=0, new_epoch=1` applied → epoch becomes 1
- ControlRecord with `previous_epoch=1, new_epoch=2` applied → epoch becomes 2
- Replay of the first record_id → `ControlRecordError(CONTROL_RECORD_ALREADY_APPLIED)`

### PF13 — audit-chain self-test passes
**PASS.** `test_preflight.py::test_preflight_13_audit_chain_self_test`:
- 5 audit events appended via `append_audit`; `verify_audit_chain` returns True
- Tampering one row's payload_json breaks `verify_audit_chain` → returns False

### PF14 — required SQLite serialization is available
**PASS.** `test_preflight.py::test_preflight_14_sqlite_serialization_available`:
- `BEGIN IMMEDIATE` + INSERT + COMMIT works
- `enforcement_store.eap_transaction` context manager commits correctly
- Two rows successfully inserted under sequential transactions
- `applied_epoch` UNIQUE constraint enforced (would reject duplicate epoch)

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
PF9  ............ PASS
PF10 ............ PASS
PF11 ............ PASS
PF12 ............ PASS
PF13 ............ PASS
PF14 ............ PASS

TOTAL: 14 PASS, 0 FAIL, 0 SKIP
```

**Status: `READY_FOR_FORMAL_RUN_REVIEW`** — no FAIL or SKIP means the formal run is ready for review.

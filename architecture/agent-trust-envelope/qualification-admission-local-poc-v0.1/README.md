# ATE Qualification & Admission Local PoC v0.1 — Implementation

**Status:** IMPLEMENTATION (non-scored; preflight only).
**Frozen design:** [`ATE-QUALIFICATION-ADMISSION-LOCAL-POC-v0.1.2-DESIGN.md`](../ATE-QUALIFICATION-ADMISSION-LOCAL-POC-v0.1.2-DESIGN.md) blob `48cc34a67a68da573fd96fdbd597ffd85bb7ec90`.
**Controlling architecture:** [`AGENT-QUALIFICATION-ADMISSION-v0.2.2-FREEZE.md`](../AGENT-QUALIFICATION-ADMISSION-v0.2.2-FREEZE.md) (commit `c881ba76f83392a242415fa4c37a1f61ae6dd92b`).
**Design-freeze commit:** `4f0eb8e55f621283474fe03af0f060f7866affb8`.

This directory contains the implementation of the qualification/admission
Local PoC against the v0.1.2 frozen design. **The formal QA-P1..QA-P14
scored run is not executed by this implementation** — only the unit/dev
test pass, the deterministic dry-run, and the 14-item preflight.

## Layout

```
qa_poc/                — artifact model + crypto + semantics (read by both sides)
    canonical.py       — canonical JSON + SHA-256 digests
    crypto.py          — Ed25519 sign/verify, key load, artifact-domain separation
    models.py          — frozen artifact types (QualificationCredential, AdmissionCredential, …)
    subject_binding.py — SubjectBinding digest + live proof
    policies.py        — authoritative profile/policy resolution
    qualification.py   — qualification pipeline
    admission.py       — admission pipeline + recursive dependency evaluation
    authorization.py   — CapabilityToken + TrustDecision issuance
    clock.py           — injected deterministic TestClock
    evidence.py        — public-key/custody manifest, evidence records
trusted/               — executor-owned write boundary
    enforcement_store.py — SQLite schema + WAL + BEGIN IMMEDIATE
    audit_ingest.py    — append_verified_authority_event()
    control_apply.py   — apply_control_record() — executor-owned serialized write
    executor.py        — execute_bound_action() — EAP
tests/
    test_preflight.py  — 14-item preflight checks
    test_qa_matrix.py  — dev/dry-run tests (NOT the formal scored run)
    test_canonical.py  — canonicalization self-test
    test_signing.py    — signing/domain-separation self-test
run_formal.py          — formal runner REQUIRES `--formal-run-authorization-token` flag
bootstrap.sh           — OS-identity + state-directory bootstrap
evidence/              — public-only evidence records (no private keys)
```

## Frozen semantics

These are enforced by the implementation; see `qa_poc/`:

- `QUALIFICATION != ADMISSION != ACTION AUTHORIZATION != EXECUTION`
- Canonical UTF-8 JSON, NFC strings, sorted keys, no floats, duplicate-key rejection
- SHA-256 digests; Ed25519 signatures
- Artifact-domain separation: `domain || 0x00 || canonical_payload`
- Authoritative profile/policy resolution; no candidate-selected downgrade
- Exact qualification-profile recognition (no `version >= N`)
- Immutable `QualificationCredential` and `AdmissionCredential`
- Exact qualification/admission IDs and digests bound into `CapabilityToken` and `TrustDecision`
- Coherent historical `TrustStateReference`
- Signed ControlRecords become execution-effective only when committed by executor `apply_control_record()`
- Monotonic applied epoch
- Recursive qualification → admission usability
- Injected deterministic TestClock; no `sleep()` for scored semantics
- EAP and control application share the same serialized executor-owned write boundary
- At local PoC EAP: committed `EAP_REACHED` iff protected mutation commits
- Denial audit occurs only after rollback; must not alter authorization state
- Requester direct protected-resource mutation must remain impossible

## OS / File-system boundary

Identities `ate-requester`, `ate-authority`, `ate-executor` (system users,
no login, no sudo). Custody matrix and enforcement-db ownership mode bits
are installed by `bootstrap.sh` and verified by preflight #5–#8.

## Formal runner

`run_formal.py` requires an explicit
`--formal-run-authorization-token <TOKEN>` flag where `<TOKEN>` must equal
`ATE-FORMAL-RUN-AUTHORIZED-BY-FRANK-AS-PI-2026-09-16`. **Without the flag
the script refuses to launch.** This handoff does not provide the token;
the formal scored run remains withheld.

# Agent Conformance Local Lifecycle PoC v0.1 — Authority Boundary Review

**Candidate implementation baseline:** `7d6dad17cf95c2e29afdf45b97c73a07f54bc870`

## Disposition

**PASS FOR ISOLATED DEVELOPMENT PYTEST**

**FORMAL RUN NOT AUTHORIZED**

This review supersedes the assumption that the earlier `cfd85e8...` implementation was sufficient for formal execution. The prior formal run remains historical evidence classified `INCONCLUSIVE_EVIDENCE_INVALID`.

## Findings closed in this candidate

### A1 — Participant-visible raw authority key API
R14, R13, Trigger Observer, Authorization Service, and participant audit view expose no public `private_key` attribute. Test-only valid malformed signatures are routed through `TrustedControls`.

Claim boundary: this is a logical/API fixture boundary, not hostile same-process Python introspection or OS/process isolation.

### A2 — R13 signing oracle over caller-fabricated evidence
R13 now:
- resolves the authoritative subject;
- requires subject/trust-domain binding;
- resolves the observer-authoritative artifact by ID;
- requires that artifact to be the observer store's current evidence;
- verifies observer signature and stored-content equality;
- derives qualification/admission state from StateStore;
- rejects caller assertions that disagree with authoritative state;
- requires active-profile subject/role/domain binding.

A participant can no longer obtain a valid R13 restoration recommendation by supplying fabricated or stale runtime evidence or by lying that revoked qualification/admission is ACTIVE.

### A3 — Observer history mutable alias / write oracle
Observer evidence is stored and returned by defensive copy.
The trusted observer writer is a one-time closure bound during bootstrap.
The participant-visible observer has no trusted measurement-write method.
The public `submit_measured_runtime` / `record_evidence` paths deny.

### A4 — Authoritative subject mutable alias / replacement
StateStore stores and returns defensive copies of SubjectState.
Subject registration is insert-only; a participant cannot overwrite role/domain binding by re-registering the same subject ID.

### A5 — Qualification/admission revocation rollback by re-registration
Qualification and admission fixture registration is insert-only.
A previously signed ACTIVE fixture cannot overwrite a revoked authoritative fixture with the same artifact ID.

### A6 — Audit mutable alias
Audit append copies payloads.
Audit snapshot reads return defensive copies.
The participant-facing AuditView has no append operation.
Mutation of a returned snapshot cannot change the authoritative ledger.

### A7 — Protected-resource authority
The resource authority is bound behind one-time grant/consume closures.
The participant Harness contains no resource credential.
Executor receives only the bound consumer closure.

### A8 — Authorization Service arbitrary-action signing oracle
The frozen PoC defines one governed action: `WRITE_RESOURCE` with the fixed payload.
Authorization Service is now initialized with the canonical allowed action digest and refuses capability issuance for any other action/payload.

## Regression coverage

Current static test inventory at the candidate baseline is **79 test functions**:
- lifecycle: 23
- negative security: 8
- audit: 9
- attack regressions: 34
- authority-boundary regressions: 5

New/strengthened regressions cover:
- no public authority private-key API;
- observer/audit/resource authority participant write denial;
- R13 mutated-evidence rejection;
- R13 stale-valid-evidence rejection;
- R13 caller QA-state lie rejection;
- subject/evidence defensive-copy behavior;
- subject registration insert-only;
- qualification/admission re-registration rollback denial;
- non-governed action capability issuance denial.

## Frozen artifact preservation

At candidate commit `7d6dad17...`, all eight controlling frozen artifacts retain their previously locked Git blob IDs:

- design: `4faea2a16261ca9416fe8bb4eceaaff80593eb59`
- design freeze: `d1da477dfaa8bb4682a01408596cd468a6e3fd64`
- conformance protocol: `f8bc4464db197a58b6402e01d0378592ba7dc220`
- protocol freeze: `62630ddc3bdbf114c7d07beffa2621737c623aaf`
- qualification/admission protocol: `28b4b0a36e7ded946686c0eb45d4ee820a35c2bf`
- revocation/trust-state model: `0a4c42c30b0914bd0c0dc660c3aa8cc80ae5cb86`
- enforcement plane: `154465106614f1448f9bbbca94ff7b5862bfd00a`
- audit/accountability model: `82450a5d049cc1d6f53a6cc2a4f952dcb442aa8c`

## Next gate

Run the complete 79-test suite in a clean detached worktree pinned to this candidate implementation.

No code correction during that run.
No formal-run mode.
No merge.

Only after 79/79 clean execution and a successor-runner dry-run may a new formal run be considered.

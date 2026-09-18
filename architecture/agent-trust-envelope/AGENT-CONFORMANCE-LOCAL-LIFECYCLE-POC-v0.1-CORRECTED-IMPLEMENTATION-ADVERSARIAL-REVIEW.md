# Agent Conformance Local Lifecycle PoC v0.1 — Corrected Implementation Adversarial Review

**Reviewed correction commit:** `7ffca685cdbd3fa0932b5fc67844aafb7424dca1`
**Prior review:** `AGENT-CONFORMANCE-LOCAL-LIFECYCLE-POC-v0.1-IMPLEMENTATION-ADVERSARIAL-REVIEW.md`
**Disposition:** CHANGES REQUIRED — FORMAL RUN NOT AUTHORIZED

## 1. Closure Status of Prior Findings

### F1 — clean stale-capability proof
**CLOSED**

The corrected driver now separates C0 (executed at epoch N) from C1 (issued at epoch N and left unconsumed until after N+1). This now tests the intended stale-authority property rather than replay.

### F2 — R14 verifies R13 and trigger inputs
**SUBSTANTIALLY CLOSED**

R14 now verifies R13 signature, subject/domain binding, recommendation match, actual prior state, and trigger signature/binding for invalidation. A residual trigger-evidence binding issue remains below.

### F3 — participant cannot mutate authoritative lifecycle state
**NOT CLOSED**

The intended boundary moved into `StateStore`, but two direct bypasses remain:

1. `get_authoritative_state(subject_id)` returns the live mutable `_AuthoritativeLifecycle` object. A caller can directly assign `current_state` and `state_epoch`.
2. `get_authoritative_state_writer_token()` is a public module function returning the exact token accepted by `apply_authoritative_state()`.

The current NS-01 only tests empty/wrong tokens and does not exercise these real bypasses.

### F4 — qualification/admission issuer binding
**CLOSED at verification logic**

Issuer id, issuer key id, signature, subject/role/domain, ACTIVE state, and artifact digest are now checked.

### F5 — executor resolves current qualification/admission state from authoritative store
**PARTIALLY CLOSED**

The executor now resolves by artifact id from `StateStore`, but the authoritative store returns the same live mutable fixture objects held by the harness. This leaves current state caller-mutable.

## 2. New / Residual Blocking Findings

### G1 — Lifecycle state boundary is still bypassable
**Severity:** CRITICAL

Required correction:

- `get_authoritative_state()` must return an immutable snapshot/copy, not the live record.
- remove any public API that returns the authoritative writer capability/token.
- inject the writer capability privately into R14 or capture it through a factory/closure inaccessible to participant-facing code.
- add regressions for returned-state mutation, public token discovery/use, and rollback to `CONFORMANT @ N` followed by an unconsumed epoch-N capability attempt.

The authoritative store must remain at N+1.

### G2 — Profile activation and R13 profile trust are unauthenticated
**Severity:** CRITICAL

`StateStore.set_active_profile(profile)` is public and accepts arbitrary objects. `R13Evaluator.evaluate()` accepts caller-supplied `profile` and `profile_digest` without verifying active-profile status, signature, signer authority, digest correctness, or predeclared registration.

This permits a restoration bypass: create a fake profile requiring the new runtime, have R13 evaluate it, and obtain a signed CONFORMANT recommendation that R14 will accept.

Required correction:

- create an authoritative predeclared profile registry.
- register v1 and v2 before run start and lock their digests.
- verify profile signatures against an authorized profile/policy signer.
- activate only a registered profile by stable id/digest through a protected authority path.
- make activation unavailable to participant-facing callers.
- make R13 resolve the active authoritative profile itself, or receive only an immutable verified profile reference.
- add regressions for unsigned, wrong-key, unregistered, digest-tampered, and post-mutation invented profiles.

### G3 — Authoritative qualification/admission state is still caller-mutable
**Severity:** HIGH

`get_qualification_fixture()` and `get_admission_fixture()` return live stored objects. The reverse of the current revocation test is therefore possible: after authoritative REVOKED state, caller code can set the same object's `current_state` back to ACTIVE.

Required correction:

- store immutable/internal fixture records.
- expose only snapshots/copies.
- move fixture state transitions behind a protected authority method.
- executor must resolve the internal authoritative record.
- add a regression that revokes authoritative qualification, mutates a retrieved copy back to ACTIVE, and proves execution still denies.

### G4 — Trigger-to-R13 evidence binding is incomplete
**Severity:** MEDIUM-HIGH

R14 verifies trigger signature and subject/domain but does not verify that the trigger's current evidence is the same evidence R13 evaluated.

Required correction for this PoC:

- require `trigger.current_evidence_id == r13_evaluation.runtime_evidence_id`.
- require trigger current-value digest to match the measured runtime value in R13.
- require trigger evidence ids to resolve in the observer-authoritative store.
- add a mismatched-valid-trigger regression against the actual R14 publication path.

## 3. Formal-Run Disposition

**FORMAL RUN: NOT AUTHORIZED**

The correction commit materially improved the implementation and closed the original stale-capability flaw. The remaining gaps are authority-boundary issues. A formal PASS produced now could still be achieved while participant-facing code can manufacture lifecycle restoration or rewrite authoritative state.

## 4. Required Next Action

1. correct G1-G4 only;
2. preserve frozen design/protocol artifacts byte-identically;
3. add targeted attack regressions;
4. rerun the full development suite;
5. commit and push the correction;
6. report exact changed files, test counts, and frozen hash verification;
7. do not execute the formal run;
8. do not merge to main.

After that correction, perform one final narrow adversarial review. If these boundaries are genuinely closed and no new authority bypass appears, proceed directly to formal-run authorization.
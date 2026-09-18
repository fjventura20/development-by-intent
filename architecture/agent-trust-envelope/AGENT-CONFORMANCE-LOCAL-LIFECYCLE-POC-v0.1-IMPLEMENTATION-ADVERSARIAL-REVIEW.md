# Agent Conformance Local Lifecycle PoC v0.1 — Implementation Adversarial Review

**Reviewed implementation commit:** `fb9fdd7343ca6cde739d36e3b8e8e25cbd024c34`  
**Frozen design:** `AGENT-CONFORMANCE-LOCAL-LIFECYCLE-POC-v0.1.1-DESIGN.md`  
**Freeze:** `AGENT-CONFORMANCE-LOCAL-LIFECYCLE-POC-v0.1.1-FREEZE.md`  
**Disposition:** CHANGES REQUIRED — FORMAL RUN NOT AUTHORIZED

## 1. Summary

The implementation is organized, deterministic, and substantially aligned with the frozen design. The reported 37/37 development-test result is credible as a test-suite result.

However, the current implementation does **not yet prove the frozen security claim**. Three high-severity issues and two medium issues must be corrected before formal-run authorization.

---

## 2. High-Severity Findings

### F1 — Central stale-capability proof uses a capability that was already executed

The frozen proof target requires a capability issued under epoch N to remain **unconsumed** until after the runtime mutation and N+1 invalidation, then be denied because its lifecycle state/epoch is stale.

The implementation instead:

1. issues C1 at epoch N;
2. executes C1 successfully before mutation;
3. consumes its nonce;
4. mutates runtime;
5. reuses the already-consumed C1 as the “stale” capability.

This confounds stale-authority invalidation with replay state.

Although the executor currently checks non-conformance/epoch before nonce replay, the test still fails to establish the intended property:

> an otherwise-valid, not-yet-consumed capability issued under epoch N cannot cause an effect after N+1 becomes authoritative.

**Required correction**

Use two pre-invalidation capabilities or equivalent:

```text
C0 = issued and executed at epoch N to prove normal execution
C1 = issued at epoch N but deliberately left unconsumed
runtime v1 -> v2
N+1 published
attempt C1
C1 denied before effect because current lifecycle state/epoch is insufficient
```

C1's nonce MUST still be UNSEEN at the moment of the stale-capability attempt.

Add an assertion proving that fact before execution.

---

### F2 — R14 does not verify R13 evaluation or trigger before publishing authoritative state

`LifecycleAuthority.publish_transition()` accepts arbitrary `r13_evaluation` and `trigger_observation` objects and then signs/applies the requested state.

It does not verify:

- R13 signature;
- R13 authority identity;
- that `new_state` equals the signed R13 recommendation;
- trigger signature;
- trigger authority;
- trigger subject/domain binding;
- that `prior_state` equals the subject's actual current state.

The negative tests only prove that standalone `verify()` methods reject forged artifacts. They do **not** prove that the authoritative R14 transition path rejects them.

A caller could therefore pass a forged or mismatched R13 object to R14 and obtain a valid R14-signed lifecycle decision.

**Required correction**

R14 transition publication must verify, before state mutation:

```text
R13 signature valid under authorized R13 key
R13 subject/domain match target subject
R13 recommended_state == requested new_state
prior_state == subject.current_state
trigger signature valid when trigger is required
trigger subject/domain match
trigger evidence binding valid enough for this PoC
```

Restoration without a trigger may remain permitted only under the frozen re-attestation path, but the R13 evaluation must still verify.

Add negative tests that call the actual R14 publication path with forged/mismatched R13 and forged/mismatched trigger artifacts and prove that no state/epoch mutation occurs.

---

### F3 — Subject lifecycle state is directly mutable, and NS-01 does not test the real bypass

`SubjectState.current_state` and `SubjectState.state_epoch` are public mutable dataclass fields.

NS-01 acknowledges this and directly writes them. The test only sets epoch to `99`, which guarantees the executor detects an epoch mismatch.

The dangerous bypass is the opposite:

```text
after N+1 invalidation:
subject.current_state = CONFORMANT
subject.state_epoch = N
```

If an unconsumed epoch-N capability exists, the executor's current checks would see:

```text
CONFORMANT
AND capability.observed_state_epoch == subject.state_epoch
```

and may allow execution.

That means the implementation does not satisfy the frozen statement that the subject **must not be able to directly mutate lifecycle state or epoch**.

**Required correction**

The authoritative lifecycle state/epoch must not be stored in a participant-mutable object.

For this PoC, acceptable approaches include:

- private lifecycle state held in `StateStore` and mutated only through an R14-authorized method/token;
- immutable subject identity object plus separately protected lifecycle record;
- another equivalent local boundary that prevents participant-facing code from setting current lifecycle state/epoch.

Then rewrite NS-01 to attempt the actual rollback bypass and prove it cannot change authoritative lifecycle state.

---

## 3. Medium Findings

### F4 — Qualification/admission “issuer validity” is only partially enforced

`verify_qualification()` verifies the signature using one stored public key, but issuer validation only checks that `issuer` and `issuer_key_id` are non-empty.

It does not require:

```text
fixture.issuer_key_id == key_id(registered issuer public key)
fixture.issuer == expected authorized issuer identity
```

The fixture `artifact_digest` field is also not checked.

**Required correction**

Bind the fixture explicitly to the registered issuer identity/key and verify the stored artifact digest if the design claims it as a stable integrity field.

---

### F5 — Executor consumes caller-supplied fixture objects rather than authoritative current fixtures

At execution, qualification/admission checks are performed against fixture objects passed by the caller. The executor does not resolve the current authoritative fixture objects from `StateStore`.

For the base PoC this is partly mitigated by signature checks at issuance, but it weakens the claim that executor step 4 resolves **current qualification/admission state**.

**Required correction**

At executor step 4, resolve qualification/admission by stable artifact ID from the authoritative store, then evaluate current state there. Do not rely solely on caller-supplied mutable object state.

---

## 4. Findings That Are Not Blockers

The following implementation choices are acceptable once the above issues are fixed:

- denial at step 6 (`NON_CONFORMANT`) before step 7 (`STALE_EPOCH`);
- deterministic logical clock;
- Ed25519 fixture keys for this local PoC;
- non-destructive audit tamper testing;
- predeclared profile v2;
- local in-memory stores, provided the claimed participant-facing security boundary is actually enforced.

---

## 5. Formal-Run Disposition

**FORMAL RUN: NOT AUTHORIZED**

The current 37/37 development tests demonstrate implementation consistency with the current tests, but the tests miss two critical adversarial paths and the central stale-capability scenario is not cleanly instantiated.

Required next action:

1. correct F1-F5;
2. add targeted regression tests;
3. rerun development tests;
4. commit the correction as a new implementation commit;
5. preserve all frozen design artifacts byte-identically;
6. report exact changed files and test results;
7. do not execute the formal run.

Only after independent review of that corrected commit should formal execution be considered.

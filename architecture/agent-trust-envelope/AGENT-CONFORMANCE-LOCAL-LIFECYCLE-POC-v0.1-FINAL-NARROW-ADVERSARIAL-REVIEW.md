# Agent Conformance Local Lifecycle PoC v0.1 — Final Narrow Adversarial Review

**Reviewed commit:** `dda4e3084f2c51ac89c9f46d7ca531b79f3cb64b`
**Disposition:** CHANGES REQUIRED — FORMAL RUN NOT AUTHORIZED

## 1. Findings Closed

### G1 immutable lifecycle snapshot
**MOSTLY CLOSED**

`get_authoritative_state()` now returns an immutable `LifecycleSnapshot`, so the original live-record mutation bypass is closed.

### G3 fixture snapshot isolation
**CLOSED AS TO LIVE-OBJECT MUTATION**

Qualification/admission records are deep-copied into the authoritative store and getters return copies. Caller mutation of a retrieved fixture no longer rewrites the stored record.

### G4 trigger/R13 evidence binding
**CLOSED**

R14 now binds trigger current evidence id and value digest to the R13 evaluation and resolves prior/current evidence in the observer-authoritative store.

## 2. Remaining Blocking Findings

### H1 — Predeclared-profile boundary can still be replaced after mutation
**Severity:** CRITICAL

The new profile registry does not actually freeze the predeclared registry for the run.

`StateStore.install_profile_registry(registry)` remains a public method and can replace the authoritative registry at any time.

The regression `test_g2_post_mutation_invented_profile_rejected` itself demonstrates that a new profile signed by the authorized profile key can be registered after mutation. It then installs a second registry on the StateStore. The test only proves that activation with an intentionally wrong digest fails.

An attacker with the same reachable harness capabilities can instead:

```text
1. create fake profile requiring runtime v2
2. sign it with the exposed profile_registry_priv
3. create a new ProfileRegistry using the authorized public key
4. register fake profile
5. call state_store.install_profile_registry(new_registry)
6. call state_store.activate_profile(fake_id, correct_fake_digest, activation_token)
7. R13 resolves fake profile as authoritative active profile
8. R13 signs CONFORMANT
9. R14 accepts the valid R13 recommendation
```

This directly violates the frozen requirement that profile v2 be predeclared and digest-locked before formal-run start.

**Required correction**

- Registry installation must be one-time/frozen before formal-run execution.
- After registry freeze, `install_profile_registry()` must reject replacement.
- Registration must close before run start; no new profile may be added after freeze.
- Profile signer private key must not be present on the participant-facing harness object.
- Activation token/capability must not be obtainable by participant-facing code.
- Add a regression that attempts the exact attack above using the correct fake profile digest and proves no registry replacement, no activation, no R13 CONFORMANT recommendation, and no lifecycle restoration.

### H2 — Qualification/admission state writer capability is publicly obtainable
**Severity:** HIGH

`acquire_qual_admission_state_writer_token()` is a public function that returns the exact token accepted by `revoke_qualification()` / `revoke_admission()`.

This is inconsistent with the claimed protected authority boundary. Although revocation is fail-safe, the same pattern is not a defensible authority-control mechanism and could become unsafe if restoration/state-setting is added.

**Required correction**

- Remove the public token-acquisition function.
- Inject/capture the state-writer capability only in the trusted qualification/admission authority fixture/factory.
- Participant-facing code must not be able to obtain the token.
- Add a regression proving the token is unavailable through the public interface.

### H3 — Lifecycle/profile protection currently relies on Python underscore convention
**Severity:** MEDIUM-HIGH

`_get_authoritative_state_writer_token_internal()` and `_get_profile_activation_token_internal()` remain importable module functions. The current tests import the profile token accessor directly.

For a fixture-level PoC, private naming can be acceptable only if the claimed boundary is explicitly an interface boundary and participant-facing code is never given module-level authority internals. The current implementation and tests blur that boundary.

**Required correction**

Use factories/closures or authority objects that retain capability material internally without returning it to callers. Participant-facing tests should exercise public interfaces only; adversarial tests may attempt imports/introspection and must demonstrate they cannot obtain a usable authority capability.

## 3. Formal-Run Disposition

**FORMAL RUN: NOT AUTHORIZED**

The remaining issue is narrow but decisive: the run can still manufacture a new 'predeclared' policy after observing the runtime change and make R13 treat it as authoritative.

## 4. Required Next Action

Make one final surgical correction:

1. freeze the profile registry before formal-run start;
2. prohibit registry replacement and post-freeze registration;
3. remove signing private keys and authority tokens from participant-facing harness state;
4. eliminate public token getters for lifecycle/profile/qualification-admission authority paths;
5. add exact regressions for correct-digest fake-profile activation and token discovery;
6. preserve all frozen artifacts byte-identically;
7. rerun development tests;
8. commit/push;
9. do not execute formal run or merge.

If this correction passes the next narrow inspection, formal-run authorization should follow immediately.
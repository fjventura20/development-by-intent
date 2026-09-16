# ATE Trust-Decision Composition Local Conformance Protocol v0.1.1

**Status:** Revised freeze candidate — DESIGN ONLY  
**Date:** 2026-09-16  
**Program:** Agent Trust Envelope (ATE)  
**Supersedes:** `ATE-TRUST-DECISION-COMPOSITION-LOCAL-CONFORMANCE-PROTOCOL-v0.1.md`  
**Controlling architecture:** `ATE-TRUST-DECISION-COMPOSITION-ARCHITECTURE-v0.1.1.md`  
**Protocol review:** `ATE-TRUST-DECISION-COMPOSITION-PROTOCOL-ADVERSARIAL-REVIEW-v0.1.md`

---

## 1. Research Question

> **Can a deterministic local trust-decision engine compose one canonical action, verified runtime context, current qualification, current governance coverage, risk/assurance policy, capability scope, approvals, and authoritative current trust state into exactly one bounded `TRUST_GRANTED` or `TRUST_DENIED` outcome without widening authority, mixing incompatible contexts, duplicating executable grants, or ignoring execution-invalidating state changes?**

This protocol tests trust-decision composition machinery only.

No live AI model, premium evaluator, or multi-agent replication is required.

---

## 2. Frozen Local Profile

Use one local deterministic fixture environment with distinct signing roles for:

- Trust Root Authority;
- Runtime Verification Authority;
- Qualification Authority;
- Qualification Status Authority;
- Governance Coverage Authority;
- Governance/Policy Authority;
- Risk Policy Authority;
- Capability Authorization Authority;
- Approval Authority A;
- independent Approval Authority B;
- Revocation/Current-State Authority;
- Composition Profile Authority;
- Trust Decision Authority.

Keys/roles remain distinct even if one local harness process hosts fixture logic.

---

## 3. Cryptography / Canonicalization

```text
signature_algorithm = Ed25519
digest_algorithm = SHA-256
canonicalization = RFC 8785 JCS
```

Unknown/unsupported algorithm or artifact version fails closed.

---

## 4. Frozen Capability Taxonomy

Before formal run freeze:

```text
taxonomy_id = ATE_LOCAL_COMPOSITION_CAPS
taxonomy_version = 1
capabilities = READ, WRITE, EXECUTE, SEND_EXTERNAL, ADMINISTER
```

Freeze target/resource classes, containment rules, exclusions, and any accepted translation mappings.

Preserve taxonomy digest.

---

## 5. Frozen Authority Registries and Ceilings

Before formal run freeze immutable:

```text
AuthorityRoleRegistry
DecisionAuthorityCeilingPolicy
StateAuthorityRegistry
```

At minimum bind:

```text
authority_id
public_key
permitted_artifact/state classes
trust domains
project scopes
capability classes
risk ceilings where applicable
assurance permissions where applicable
validity / revocation handle
```

The Trust Decision Authority ceiling policy additionally binds maximum decision lifetime and permitted CompositionProfile digests.

No authority permission may change during a formal run.

---

## 6. Deterministic Trusted Time Fixture

Security-controlling time is explicit input.

Freeze one trusted time-state fixture policy.

For every test/variant preregister:

```text
time_state_id
controlling_evaluation_time
```

used for:

- not-before checks;
- expiry;
- assurance freshness;
- approval freshness;
- decision validity.

Incidental logging/serialization timestamps are non-semantic unless explicitly referenced by controlling time state.

---

## 7. Composition Profile

Freeze one exact `CompositionProfile` containing:

- D0..D15 top-level gate order;
- within-gate predicate/reason precedence;
- required current-state classes;
- lifecycle/recheck rules;
- capability taxonomy digest;
- fail-closed rules;
- maximum decision lifetime.

Preserve ID, version, digest, issuer, and signature.

---

## 8. Baseline Valid Fixture

Use one fully valid baseline:

```text
principal = agent-A
runtime_instance = runtime-A
qualified_profile = profile-A
trust_domain = local-A
project_scope = project-A
capability = WRITE
target = project-A/resource-1
risk = R2
required_assurance = A2
authorization_instance_id = auth-A
operation_id = op-A
```

Include valid/current:

- `VerifiedRuntimeContext`;
- ACTIVE qualification for exact profile-A;
- qualification authorizing WRITE/R2/A2;
- governance coverage context;
- evidence-currentness context;
- CapabilityToken containing exact action;
- required approval/structural context;
- authoritative current-state observations;
- CompositionProfile;
- Trust Decision Authority within all ceilings.

---

## 9. Persistent Grant Store

Formal harness SHALL implement crash-safe semantics equivalent to:

```text
UNIQUE(authorization_instance_id) for executable TRUST_GRANTED
```

Persist the exact signed grant before returning it to the caller.

Retry/concurrent issuance for the same authorization instance and semantic context returns the exact persisted grant.

A crash/restart after persistence but before caller acknowledgement must not mint another unique grant.

---

## 10. Authoritative State Observation

Every current-state observation contains:

```text
state_class
state_authority_id
state_object_digest
state_epoch
observed_at
signature
```

Verifier validates signer role through frozen `StateAuthorityRegistry`.

A self-asserted vector is invalid.

---

## 11. FormalRunManifest

Before the formal run begins, freeze one immutable preregistered manifest containing at least:

```text
protocol artifact digest
CompositionProfile digest
capability taxonomy digest
AuthorityRoleRegistry digest
DecisionAuthorityCeilingPolicy digest
StateAuthorityRegistry digest
fixture-set digest
trusted-time fixture policy digest
formal test IDs and variant IDs
per-variant controlling time_state_id
per-variant expected verdict
per-negative-variant expected_primary_gate
per-negative-variant expected_primary_reason_code
```

No expected outcome/reason code may be derived after observing formal execution.

Preserve FormalRunManifest digest in evidence.

---

## 12. Formal Result Format

Every controlling test emits machine-readable:

```text
test_id
variant_id?
result = PASS | FAIL
actual_verdict
expected_verdict
actual_primary_gate
expected_primary_gate
actual_primary_reason_code
expected_primary_reason_code
semantic_context_digest?
trust_decision_input_digest?
trust_decision_digest?
assertions[]
```

PASS requires expected and actual controlling outcomes to match exactly.

---

## 13. Controlling Test Matrix

Exactly **16 controlling tests** are frozen.

All mandatory variants/assertions must pass.

### TD-C0 — Valid complete composition

Expected:

```text
TRUST_GRANTED
```

Assert exact baseline bindings, semantic/context digests, state-vector digest, CompositionProfile digest, execution-recheck contract, and one persisted grant.

### TD-C1 — Semantic identity stability

A. Equivalent semantic input under different incidental timestamps that do not change controlling time/freshness state.

Expected:

```text
semantic_context_digest unchanged
```

B. Change controlling semantic input (for example qualification status epoch or capability-token digest).

Expected:

```text
semantic_context_digest changed
```

C. Change controlling trusted time state so a freshness predicate changes.

Expected semantic/currentness context to change and frozen verdict/reason to apply.

### TD-C2 — One executable grant per authorization instance

Run retry and concurrent issuance for one valid authorization instance.

Also simulate process restart after grant persistence but before client acknowledgement/retry.

Expected:

- exactly one unique executable grant identity/blob;
- successful retries return exact persisted grant;
- no second executable grant minted.

### TD-C3 — Canonical action / taxonomy enforcement

A. unsupported taxonomy version;
B. mismatched operation mapping between qualification/capability and action;
C. alias attempting target-scope widening.

Expected: all deny with preregistered action/taxonomy reasons.

### TD-C4 — Risk and assurance downgrade protection

A. participant says R1 while authoritative policy says R2;
B. qualification lacks required A2 authorization;
C. target resolution changes action semantics and authoritative risk from R2 to R3.

Expected:

- participant risk is non-authoritative;
- insufficient assurance denies;
- material target/risk change invalidates old composition and requires full recomposition.

### TD-C5 — Current-state authority and rollback

A. plausible state epoch signed by unauthorized state authority;
B. older valid epoch after newer accepted epoch known;
C. required current-state source unavailable.

Expected: all deny with frozen authority/state precedence.

### TD-C6 — Runtime / qualification binding

A. subject mismatch;
B. qualified-profile mismatch;
C. qualification `SUSPENDED`;
D. qualification `REQUALIFICATION_REQUIRED`.

Expected: all deny.

### TD-C7 — Qualification / capability intersection

A. CapabilityToken permits WRITE, qualification only READ;
B. qualification permits WRITE, CapabilityToken only READ;
C. both authorize exact WRITE target.

Expected A-B deny; C baseline grant path.

No union semantics.

### TD-C8 — Governance currentness and dependency invalidation

A. stale GovernanceCoverageContext;
B. required structural-control receipt missing;
C. required governance acceptance revoked;
D. continuously-current behavioral evidence expired.

Expected: all deny.

### TD-C9 — Capability widening / exclusion

A. parameter outside token constraints;
B. broad allow plus explicit target exclusion;
C. subject/runtime binding mismatch.

Expected: all deny.

### TD-C10 — Approval context / quorum mixing

A. approval for different action;
B. approval for wrong risk/policy context;
C. threshold approvals from different approval-set contexts;
D. correct required approval set.

Expected A-C deny; D baseline grant path.

### TD-C11 — Trust Decision Authority ceilings

A. authority outside project scope;
B. authority maximum risk R1 for R2 action;
C. authority not permitted for WRITE;
D. authority within all ceilings.

Expected A-C deny; D baseline grant path.

### TD-C12 — Decision-time state-change race

Advance a `DECISION_TIME_STABILITY_REQUIRED` dependency after initial observation but before pre-grant stability check.

Expected:

- no grant over obsolete vector;
- engine restarts or denies according to frozen retry policy;
- actual outcome/reason matches preregistered fixture expectation.

### TD-C13 — Execution-invalidating dependency change

First create one valid unexecuted grant.

Mandatory variants:

A. directly revoke/suspend the unexecuted TrustDecision or its authorization state;
B. invalidate one upstream dependency marked `invalidates_unexecuted_grants_on_change = true` and `execution_recheck_required = true`;
C. change an `ISSUANCE_SNAPSHOT` dependency explicitly marked not to invalidate the grant.

Expected:

```text
A: NO EXECUTION
B: NO EXECUTION
C: no unnecessary full trust recomputation; grant remains subject to its other signed validity/recheck rules
```

Executor never creates a fresh TrustDecision.

### TD-C14 — Action / operation / replay cross-binding

A. decision action A paired with operation_id B;
B. authorization instance A paired with replay identity B;
C. correct full chain;
D. repeat C after consumed replay state.

Expected A-B no execution/deny; C valid; D replay denied.

### TD-C15 — Deterministic denial precedence / profile binding

Construct a preregistered input with multiple simultaneous failures spanning at least two gates and at least two failures inside one gate.

Run repeatedly.

Expected:

- actual primary gate == preregistered expected gate;
- actual primary reason == preregistered expected reason;
- same result across repeats;
- exact CompositionProfile ID/version/digest;
- altered/unknown profile digest denied;
- secondary diagnostics never change primary precedence.

---

## 14. Acceptance Rule

Formal success requires:

```text
TD-C0..TD-C15 = 16/16 PASS
all mandatory variants PASS
all expected verdict/gate/reason assertions PASS
one coherent formal run
FormalRunManifest fixed before execution
no protocol deviation
```

No partial credit and no combining results across runs.

---

## 15. Stop Conditions

STOP rather than weaken the protocol if:

- two unique executable grants exist for one authorization instance;
- semantic identity depends on incidental timestamps;
- controlling trusted time is ignored;
- unauthorized or rolled-back state is accepted;
- authority permissions must be changed after formal run starts;
- qualification/capability scopes are unioned;
- directly revoked unexecuted grant still executes;
- execution-invalidating dependency can change without required block;
- deterministic expected denial precedence cannot be reproduced;
- action/operation/replay substitution succeeds;
- a controlling invariant requires architecture redesign.

---

## 16. Evidence Requirements

Formal evidence SHALL preserve:

```text
protocol immutable identity / SHA-256
implementation commit SHA
working-tree status at formal start
FormalRunManifest + digest
cryptographic constants
capability taxonomy + digest
CompositionProfile + digest
AuthorityRoleRegistry + digest
DecisionAuthorityCeilingPolicy + digest
StateAuthorityRegistry + digest
trusted time fixture policy + digest
baseline fixture digests
all TD-C0..TD-C15 variant results
expected vs actual verdict/gate/reason data
semantic-context digests
TrustDecisionInput digests
TrustDecision digests
persistent-grant-store cardinality evidence
formal-run log
```

Historical ATE artifacts remain untouched.

---

## 17. Classification Vocabulary

### `ATE_TRUST_DECISION_COMPOSITION_ESTABLISHED`

Only if 16/16 tests and every mandatory expected-outcome assertion pass in one coherent formal run with no deviation.

### `ATE_TRUST_DECISION_COMPOSITION_NOT_ESTABLISHED`

Use for a genuine controlling invariant/test failure.

### `ATE_TRUST_DECISION_COMPOSITION_INCONCLUSIVE`

Use only when infrastructure/tool failure prevents determination without establishing an invariant failure.

---

## 18. Success Claim Boundary

Success establishes only:

> Under the frozen deterministic local profile, the trust-decision composition engine correctly intersects the specified runtime, qualification, governance, risk/assurance, capability, approval, current-state, time/freshness, and replay contexts into one bounded deterministic grant/deny decision and honors the frozen execution-invalidation contract.

It does not establish full production ATE security.

---

## 19. Quota Conservation

This protocol is intentionally deterministic and local.

Future execution should use:

1. local implementation;
2. local deterministic preflight;
3. one formal 16-test run;
4. adjudication and stop.

No Hermes reasoning, live model generation, premium evaluator, or statistical replication is necessary for this research question.

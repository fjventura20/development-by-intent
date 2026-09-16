# ATE Trust-Decision Composition Local Conformance Protocol v0.1

**Status:** Freeze candidate — DESIGN ONLY  
**Date:** 2026-09-16  
**Program:** Agent Trust Envelope (ATE)  
**Controlling architecture:** `ATE-TRUST-DECISION-COMPOSITION-ARCHITECTURE-v0.1.1.md`  
**Architecture review:** `ATE-TRUST-DECISION-COMPOSITION-FINAL-REVIEW-v0.1.md`

---

## 1. Research Question

> **Can a deterministic local trust-decision engine compose one canonical action, verified runtime context, current qualification, current governance coverage, risk/assurance policy, capability scope, approvals, and authoritative current trust state into exactly one bounded `TRUST_GRANTED` or `TRUST_DENIED` outcome without widening authority, mixing incompatible contexts, duplicating executable grants, or ignoring execution-invalidating state changes?**

This protocol tests trust-decision composition machinery only.

It does not invoke a live AI model.

---

## 2. Local Deterministic Profile

Use one local fixture environment with distinct signing identities for:

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

The local harness MAY host fixture logic in one process, but keys/roles SHALL remain distinct and role authorization SHALL be explicitly verified.

No network, model inference, premium evaluator, or multi-agent replication is required.

---

## 3. Cryptographic / Canonicalization Profile

```text
signature_algorithm = Ed25519
digest_algorithm = SHA-256
canonicalization = RFC 8785 JCS
```

Unknown algorithm/version fails closed.

---

## 4. Frozen Capability Taxonomy

Before formal run, freeze one minimal taxonomy such as:

```text
taxonomy_id = ATE_LOCAL_COMPOSITION_CAPS
taxonomy_version = 1

READ
WRITE
EXECUTE
SEND_EXTERNAL
ADMINISTER
```

Also freeze deterministic target/resource classes and any hierarchy/mapping rules.

No ad hoc operation-name translation is permitted during tests.

---

## 5. Baseline Valid Fixture

Construct one baseline action/context that is fully valid.

Example bounded semantics:

```text
principal = agent-A
runtime_instance = runtime-A
qualified_profile = profile-A
project_scope = project-A
trust_domain = local-A
capability = WRITE
target = project-A/resource-1
risk = R2
required_assurance = A2
authorization_instance_id = auth-A
operation_id = op-A
```

Baseline fixtures SHALL include:

- valid `VerifiedRuntimeContext`;
- ACTIVE current qualification for profile-A;
- qualification authorizing WRITE, R2, A2;
- current governance coverage context;
- valid evidence-currentness context;
- valid CapabilityToken containing the exact action;
- valid structural/approval context required by policy;
- current authoritative state observations;
- valid CompositionProfile;
- Trust Decision Authority authorized for local-A/project-A/WRITE/R2/A2.

---

## 6. Composition Profile

Freeze one exact `CompositionProfile` including:

- top-level D0..D15 gate order;
- within-gate reason precedence;
- required state classes;
- lifecycle/recheck rules;
- capability taxonomy digest;
- fail-closed semantics;
- maximum decision lifetime.

Preserve its digest in formal evidence.

---

## 7. Persistent Grant Store

The formal harness SHALL implement durable semantics equivalent to:

```text
UNIQUE(authorization_instance_id) WHERE verdict == TRUST_GRANTED
```

or a stronger equivalent.

Persist the exact signed grant blob.

Retry/concurrent issuance for the same authorization instance + semantic context SHALL return the exact persisted grant.

Development may use SQLite or another local deterministic store; database technology is not under test.

---

## 8. State Observation Fixture

Every current-state observation SHALL contain:

```text
state_class
state_authority_id
state_object_digest
state_epoch
observed_at
signature
```

The trust-state vector is derived only from verified authorized observations.

A self-asserted vector is not accepted.

---

## 9. Formal Result Format

Every controlling test emits machine-readable:

```text
test_id
result = PASS | FAIL
actual_verdict
primary_reason_code
semantic_context_digest?
trust_decision_input_digest?
trust_decision_digest?
assertions[]
```

No evaluator judgment is required.

---

## 10. Controlling Test Matrix

The protocol freezes exactly **16 controlling tests**.

All mandatory variants/assertions inside a test must pass.

### TD-C0 — Valid complete composition

Use the fully valid baseline.

Expected:

```text
TRUST_GRANTED
```

Assert:

- expected semantic-context digest;
- expected canonical action digest;
- expected runtime/qualification/governance/capability bindings;
- expected state-vector digest;
- expected composition-profile digest;
- exact execution-time recheck contract;
- grant persisted once.

### TD-C1 — Semantic identity stability

Variants:

A. evaluate equivalent semantic input at different incidental wall-clock times that do not alter freshness validity;
B. change a controlling semantic input such as qualification status epoch or capability token digest.

Expected:

```text
A: semantic_context_digest unchanged
B: semantic_context_digest changed
```

Issuance timestamps MAY differ; semantic identity must behave as specified.

### TD-C2 — One executable grant per authorization instance

Run retry and concurrent issuance against one valid authorization instance.

Expected:

- one unique executable `TRUST_GRANTED` decision identity/blob;
- all successful retries return exact persisted grant;
- no second executable grant is minted.

Also simulate restart between persisted grant creation and client retry.

### TD-C3 — Canonical action / taxonomy enforcement

Variants:

A. unsupported/ambiguous action taxonomy version;
B. mismatched operation mapping between qualification/capability and canonical action;
C. alias attempting to widen target semantics.

Expected: all `TRUST_DENIED` at the frozen action/taxonomy precedence.

### TD-C4 — Risk and assurance downgrade protection

Variants:

A. participant supplies R1 while authoritative policy classifies R2;
B. qualification authorizes R2 but only A1 while action requires A2;
C. risk policy changes action to R3 after target resolution.

Expected:

- participant risk ignored/rejected as non-authoritative;
- insufficient qualified assurance denies;
- material target/risk change requires recomposition and cannot reuse old grant context.

### TD-C5 — Current-state authority and rollback

Variants:

A. plausible qualification-status epoch signed by unauthorized state authority;
B. older valid epoch presented after newer accepted epoch known;
C. required current-state source unavailable.

Expected: all deny with correct state/authority reason precedence.

### TD-C6 — Runtime / qualification current binding

Variants:

A. qualification subject mismatch;
B. qualified profile mismatch;
C. qualification `SUSPENDED`;
D. qualification `REQUALIFICATION_REQUIRED`.

Expected: all deny.

### TD-C7 — Qualification / capability intersection

Variants:

A. CapabilityToken permits WRITE but qualification only authorizes READ;
B. qualification permits WRITE but CapabilityToken only READ;
C. both contain WRITE for exact target.

Expected:

```text
A: DENY
B: DENY
C: eligible to continue / baseline GRANT
```

No union semantics.

### TD-C8 — Governance currentness and dependency invalidation

Variants:

A. stale GovernanceCoverageContext;
B. required structural-control receipt missing;
C. required acceptance evidence revoked;
D. bounded behavioral evidence requirement expired under continuously-current lifecycle.

Expected: all deny.

### TD-C9 — CapabilityToken widening / exclusion

Variants:

A. parameter outside signed constraints;
B. target matches broad allow but also explicit exclusion;
C. subject/runtime binding mismatch.

Expected: all deny.

### TD-C10 — Approval context and quorum-set mixing

Variants:

A. valid approval for different action digest;
B. valid approval for wrong risk/policy context;
C. two valid threshold approvals from different `approval_set_context_digest` values;
D. correct required approval set.

Expected:

```text
A-C: DENY
D: eligible to continue / baseline GRANT
```

### TD-C11 — Trust Decision Authority ceilings

Variants:

A. decision authority not permitted for project scope;
B. decision authority maximum risk R1 for R2 action;
C. decision authority not permitted for WRITE;
D. authority valid within all ceilings.

Expected A-C deny; D eligible/grant.

### TD-C12 — Decision-time state-change race

During evaluation, advance a dependency marked `DECISION_TIME_STABILITY_REQUIRED` between initial observation and pre-grant stability check.

Expected:

- stale grant is not signed;
- engine restarts evaluation or deterministically denies according to frozen retry policy;
- no grant binds known-obsolete state vector.

### TD-C13 — Execution-invalidating dependency change

First create a valid unexecuted grant.

Then change/revoke a dependency marked:

```text
invalidates_unexecuted_grants_on_change = true
execution_recheck_required = true
```

Examples fixture may use qualification suspension or approval revocation.

Expected executor recheck:

```text
NO EXECUTION
```

The executor does not create a fresh TrustDecision.

Also prove an `ISSUANCE_SNAPSHOT` dependency whose policy says change does not invalidate the grant is not unnecessarily re-evaluated.

### TD-C14 — Action / operation / replay cross-binding

Variants:

A. TrustDecision for action A paired with operation_id B;
B. authorization instance A paired with nonce/replay identity B;
C. correct authorization-instance/action/operation/replay chain;
D. repeat C after simulated consumed state.

Expected:

```text
A-B: DENY / NO EXECUTION
C: valid
D: REPLAY DENIED / NO EXECUTION
```

### TD-C15 — Deterministic denial precedence and composition-profile binding

Construct one input with multiple simultaneous failures spanning at least two gates and two failures within one gate.

Run repeatedly.

Expected:

- same primary reason code every time under frozen CompositionProfile;
- profile ID/version/digest identical;
- altered/unknown composition-profile digest denied;
- secondary diagnostics do not alter primary precedence.

---

## 11. Formal Acceptance Rule

Formal success requires:

```text
TD-C0..TD-C15 = 16/16 PASS
all mandatory variants/assertions PASS
one coherent formal run
no frozen-protocol deviation
```

No partial credit.

No combining results across runs.

---

## 12. Stop Conditions

STOP instead of weakening the protocol if:

- two unique executable grants can exist for one authorization instance;
- semantic identity cannot be separated from incidental timestamps;
- unauthorized/rolled-back state can be accepted;
- qualification and CapabilityToken scopes are unioned or ambiguously mapped;
- execution-invalidating state can change without required no-execution outcome;
- deterministic reason precedence cannot be reproduced;
- action/operation/replay identity can be substituted;
- a mandatory invariant requires redesign.

Mechanical implementation defects may be corrected only if they preserve this protocol exactly.

---

## 13. Evidence Requirements

Formal evidence SHALL preserve:

```text
protocol SHA-256 / immutable artifact identity
implementation commit SHA
working-tree status at formal-run start
cryptographic constants
capability taxonomy + digest
CompositionProfile + digest
Trust Decision Authority ceiling policy
baseline fixture digests
state-authority registry
all TD-C0..TD-C15 results and variants
semantic-context digests
TrustDecisionInput digests
TrustDecision digests
persistent-grant-store cardinality evidence
formal-run log
```

Historical ATE evidence remains untouched.

---

## 14. Classification Vocabulary

### `ATE_TRUST_DECISION_COMPOSITION_ESTABLISHED`

Only if all 16 controlling tests and variants pass in one coherent formal run with no protocol deviation.

### `ATE_TRUST_DECISION_COMPOSITION_NOT_ESTABLISHED`

Use for genuine controlling invariant/test failure.

### `ATE_TRUST_DECISION_COMPOSITION_INCONCLUSIVE`

Use only when infrastructure/tool failure prevents a valid determination without demonstrating an invariant failure.

---

## 15. Success Claim Boundary

A successful run establishes only:

> Under the frozen deterministic local fixture profile, ATE trust-decision composition correctly intersects the specified runtime, qualification, governance, risk/assurance, capability, approval, current-state, and replay contexts into one bounded deterministic grant/deny decision and honors the frozen pre-execution invalidation contract.

It does not establish full production ATE deployment security.

---

## 16. Quota Conservation

This is a deterministic engineering conformance protocol.

Execution requires no Hermes reasoning, no live model generation, no premium evaluator, and no statistical replication.

Default future execution budget:

1. local implementation;
2. deterministic preflight;
3. one formal 16-test run;
4. adjudication and stop.

# ATE Production Requirements & Conformance Profile v0.1

## 1. Purpose

This document defines normative production requirements for an Agent Trust Envelope (ATE) implementation and the evidence required to claim conformance with ATE deployment profiles P0 through P3.

Normative terms MUST, MUST NOT, SHOULD, SHOULD NOT, and MAY are to be interpreted as requirement levels.

ATE conformance is not a claim that an AI agent is generally trustworthy. It is a claim that the implementation enforces the specified trust-decision and capability-control properties for governed actions.

---

## 2. Conformance Principle

An implementation MUST NOT claim ATE conformance based only on architecture documents, signatures, model behavior, or advisory policy checks.

Conformance requires evidence that the implementation:

1. evaluates required trust evidence deterministically;
2. denies on missing, stale, invalid, revoked, mismatched, or unauthorized evidence;
3. separates claimant authority from trust-decision authority;
4. binds authorization to an exact governed action;
5. prevents replay;
6. prevents direct bypass of governed capability at the claimed assurance level;
7. produces durable audit evidence appropriate to the profile.

The governing rule is:

> **No valid trust grant, no governed capability. No governed capability, no governed action.**

---

## 3. Conformance Scope

A conformance claim MUST identify:

- ATE specification version;
- implementation version or immutable build identifier;
- deployment profile claimed;
- governed capability classes covered;
- trust domain;
- operating environment;
- exclusions and non-claims;
- evidence package identifier.

A claim MUST NOT imply coverage of capability classes or environments outside those explicitly tested and declared.

---

## 4. Deployment Profiles

ATE defines four deployment profiles.

### P0 — Development / Experimental

Purpose: controlled development, sandboxing, proof-of-concept, deterministic validation.

P0 MAY use:

- same-host components;
- software-held keys;
- local fixture authorities;
- sandbox resources;
- local revocation and audit stores.

P0 MUST NOT be represented as strong protection against host compromise.

### P1 — Standard Production

Purpose: routine governed production actions with moderate consequence.

P1 requires:

- independent executor boundary;
- protected resource credentials inaccessible to the participant agent;
- durable nonce state;
- active revocation checking;
- current policy verification;
- signed trust decisions;
- tamper-evident audit records.

### P2 — High Assurance

Purpose: high-impact operations such as protected-branch merge, sensitive data release, production deployment, or material infrastructure changes.

P2 requires P1 plus:

- stronger authority-key custody;
- isolated executor service or host boundary;
- short-lived authorization;
- stronger evidence freshness;
- independent audit sink or checkpointing;
- human approval or second authority when policy requires it;
- final revocation/policy recheck before execution.

### P3 — Critical Assurance

Purpose: critical, potentially irreversible, safety-sensitive, highly privileged, or financially material actions.

P3 requires P2 plus:

- multi-party or threshold authorization for designated actions;
- hardware-backed or equivalent high-assurance key custody for critical authorities;
- strongly isolated enforcement plane;
- mandatory independent audit preservation;
- explicit human authorization where policy requires;
- hardened trust-root governance;
- strict network/resource isolation preventing alternate execution paths.

---

## 5. Core Normative Requirements

### ATE-CORE-001 — Action-specific trust

ATE MUST authorize a specific requested action, not a general state of agent trustworthiness.

### ATE-CORE-002 — Exact subject/session binding

All session-sensitive controlling artifacts MUST bind the intended subject and session identity.

### ATE-CORE-003 — Deterministic decision

The trust-decision function MUST produce a deterministic result for equivalent canonical inputs and trust state.

### ATE-CORE-004 — Explicit outcomes

Executable trust outcomes MUST be limited to:

- `TRUST_GRANTED`
- `TRUST_DENIED`

System or verification errors MUST NOT be interpreted as grant.

### ATE-CORE-005 — Fail closed

Missing, malformed, unsupported, invalid, expired, revoked, unverifiable, or ambiguous controlling evidence MUST NOT result in `TRUST_GRANTED`.

### ATE-CORE-006 — Canonical representation

Signed and hashed security objects MUST use a deterministic canonical representation.

### ATE-CORE-007 — Version binding

Security-critical artifacts MUST identify supported artifact/specification versions. Unsupported versions MUST fail closed.

### ATE-CORE-008 — Minimum version policy

A deployment SHOULD define the minimum acceptable ATE protocol version to prevent downgrade to weaker semantics.

---

## 6. Trust Root and Authority Requirements

### ATE-TRUST-001 — Authority is registry-defined

A valid cryptographic signature MUST NOT by itself establish authority.

The signer MUST be recognized by the applicable Trust Root Registry and authorized for the artifact class being verified.

### ATE-TRUST-002 — Artifact-class authorization

Each signing authority MUST be scoped to explicitly permitted artifact types or roles.

### ATE-TRUST-003 — Authority status

The verifier MUST establish that the authority is currently valid and not revoked, suspended, or superseded as applicable.

### ATE-TRUST-004 — Participant self-authorization prohibited

The participant agent MUST NOT possess or control the authority used to sign its own `TRUST_GRANTED` decision.

### ATE-TRUST-005 — Trust-decision authority separation

The Trust Decision Authority MUST be logically separate from the participant authority boundary.

P1+ SHOULD place this authority in a separate service/process boundary.

P2+ SHOULD protect it using strong key custody.

P3 MUST use high-assurance key custody appropriate to the risk profile.

### ATE-TRUST-006 — Trust-root changes

Trust-root changes MUST be authenticated, versioned, auditable, and protected against rollback.

### ATE-TRUST-007 — Authority ceilings

Production deployments SHOULD define maximum capability classes each authorization authority is permitted to issue.

---

## 7. Key Custody Requirements

### ATE-KEY-001 — Private key confidentiality

Authority private keys MUST NOT be included in evidence artifacts, logs, prompts, model context, or participant-visible state.

### ATE-KEY-002 — Separation of duties

Identity, governance, policy, behavioral evidence, authorization, trust-decision, executor, and audit signing roles SHOULD use distinct authority identities where their compromise consequences differ materially.

### ATE-KEY-003 — Participant restrictions

The participant MUST NOT possess:

- Trust Decision Authority private keys;
- protected executor resource credentials;
- unrestricted authorization-authority credentials;
- audit authority credentials that would permit undetectable history rewriting.

### ATE-KEY-004 — Key rotation

Authority rotation MUST preserve verifiability of historical evidence while preventing new issuance by retired keys.

### ATE-KEY-005 — Compromise response

The deployment MUST have a defined mechanism to revoke or suspend a compromised authority key.

---

## 8. Identity and Live Provenance Requirements

### ATE-PROV-001 — Runtime/session evidence

When runtime provenance is required by policy, the trust envelope MUST include verifiable evidence binding the subject to the intended runtime/session.

### ATE-PROV-002 — Provenance is not trust

The implementation MUST NOT treat valid provenance alone as sufficient authorization.

### ATE-PROV-003 — Session substitution rejection

Evidence issued for one session MUST NOT be accepted as evidence for another unless explicitly permitted by the governing specification.

### ATE-PROV-004 — Freshness challenge

Where a freshness challenge is used, it MUST bind the relevant session/evidence transaction and MUST be verified before grant.

---

## 9. Condition of Agency Requirements

### ATE-COA-001 — Explicit acceptance evidence

If COA is required, ATE MUST verify explicit evidence of acceptance of the required COA version.

### ATE-COA-002 — Binding

COA acceptance MUST bind at minimum:

- subject;
- session where applicable;
- COA version/fingerprint;
- acceptance identity;
- validity/freshness conditions.

### ATE-COA-003 — Substitution rejection

Acceptance of another COA version, subject, or session MUST NOT satisfy the required acceptance.

### ATE-COA-004 — Revocation/supersession

If COA acceptance has been revoked, expired, or superseded under policy, it MUST NOT support a new trust grant.

---

## 10. Value Architecture and Policy Requirements

### ATE-VA-001 — Exact active policy

The implementation MUST verify the required:

- `policy_id`
- `policy_version`
- `policy_digest`

against authoritative active policy state.

### ATE-VA-002 — Signed stale policy rejection

A cryptographically valid but obsolete/superseded policy MUST NOT satisfy current policy requirements.

### ATE-VA-003 — Default deny

Policy semantics SHOULD be default-deny for unspecified governed operations.

### ATE-VA-004 — Policy downgrade protection

A participant MUST NOT be able to select a weaker historical policy merely because it remains correctly signed.

### ATE-VA-005 — Policy change invalidation

Where authorization is bound to an exact policy version/digest, a policy change MUST require re-evaluation or re-issuance before execution.

---

## 11. Behavioral Evidence Requirements

### ATE-BEH-001 — Independent authority

Behavioral evidence used for grant MUST be issued or attested by an authority recognized for that evidence class.

### ATE-BEH-002 — Subject binding

Behavioral evidence MUST identify the subject to which the evidence applies.

### ATE-BEH-003 — Evidence digest

Receipts MUST bind the controlling evaluation/evidence digest or immutable evidence identifier.

### ATE-BEH-004 — Freshness

Behavioral evidence MUST satisfy the freshness requirement applicable to the requested action risk class.

### ATE-BEH-005 — Revocation

Revoked behavioral evidence MUST NOT contribute to grant.

---

## 12. Capability Authorization Requirements

### ATE-CAP-001 — Least privilege

Capability authorization MUST express the maximum operation/target scope permitted for the requested action.

### ATE-CAP-002 — Exact or subset semantics

The requested action MUST be proven to fall within the signed capability scope.

### ATE-CAP-003 — No participant widening

The participant MUST NOT be able to alter operation, target, constraints, expiration, policy binding, COA binding, or nonce state without invalidating authorization.

### ATE-CAP-004 — Explicit exclusions

Where exclusions exist, they MUST override broader allow scope.

### ATE-CAP-005 — Action parameters

Security-relevant action parameters SHOULD be canonicalized and bound by digest before trust grant.

P2+ MUST bind security-relevant parameters when mutation could alter impact.

### ATE-CAP-006 — Mutable target state

For mutable targets where state changes can alter action meaning, P2+ SHOULD bind an authoritative resource-state identifier/digest and recheck it before execution.

---

## 13. Trust Decision Requirements

### ATE-DEC-001 — Signed decision

A grant used for execution MUST be signed or otherwise authenticated by an authorized Trust Decision Authority.

### ATE-DEC-002 — Decision binding

A `TRUST_GRANTED` decision MUST bind:

- envelope or evidence-bundle fingerprint;
- subject identity;
- session identity as applicable;
- requested action digest;
- applicable policy identity/digest;
- capability authorization identifier;
- nonce/replay identifier;
- issuance and expiry data.

### ATE-DEC-003 — Decision freshness

An expired TrustDecision MUST NOT be executable.

### ATE-DEC-004 — Decision revocation

A revoked TrustDecision MUST NOT be executable.

### ATE-DEC-005 — Denial integrity

Denial reason codes SHOULD be machine-readable and attributable to a defined verification gate or failure class.

---

## 14. Revocation and Trust-State Requirements

### ATE-REV-001 — First-class revocation

Production profiles P1+ MUST support revocation or suspension of controlling trust artifacts/authorities required by the architecture.

### ATE-REV-002 — Current-state evaluation

A trust grant MUST be executable only while all required controlling dependencies remain in a currently valid state.

### ATE-REV-003 — Epoch monotonicity

If trust-root, policy, revocation, or federation epochs are used, implementations MUST reject rollback to an older authoritative epoch when a newer accepted epoch is known.

### ATE-REV-004 — Unknown state

For operations requiring current revocation knowledge, inability to determine revocation status MUST NOT be interpreted as active/not-revoked.

### ATE-REV-005 — Executor recheck

P2+ MUST perform a final revocation check for designated high-risk controlling artifacts immediately before execution or within the policy-defined freshness window.

---

## 15. Nonce and Replay Requirements

### ATE-NONCE-001 — Single-use authorization

Unless an alternative profile explicitly defines multi-action semantics, one trust authorization MUST permit at most one governed execution.

### ATE-NONCE-002 — Durable replay state

P1+ nonce/replay state MUST survive process restart.

### ATE-NONCE-003 — Atomic reservation

P1+ execution MUST atomically transition an executable nonce from authorized to reserved (or equivalent) before external effect.

### ATE-NONCE-004 — Concurrent replay rejection

Two concurrent attempts using the same single-use authorization MUST NOT both execute.

### ATE-NONCE-005 — No reactivation

A consumed authorization MUST NOT transition back to executable state.

### ATE-NONCE-006 — Distinct diagnostics

Implementations SHOULD distinguish unknown, authorized, reserved, consumed, failed-before-effect, and unknown-effect states where relevant.

---

## 16. Enforcement Plane Requirements

### ATE-EXEC-001 — Executor is enforcement boundary

The Capability Executor MUST independently validate the minimum critical trust bindings before exercising a governed capability.

### ATE-EXEC-002 — No direct participant credentials

For P1+, the participant MUST NOT possess equivalent credentials permitting direct access to governed resources outside the executor.

### ATE-EXEC-003 — Executor-only path

At the claimed assurance level, governed resource access MUST require the executor or equivalent enforcement boundary.

### ATE-EXEC-004 — Credential release ordering

Protected resource credentials SHOULD NOT be retrieved before authorization and nonce reservation succeed.

### ATE-EXEC-005 — Resource-specific validation

The executor/resource adapter MUST independently canonicalize or verify operation/target semantics before execution.

### ATE-EXEC-006 — Typed capabilities

Production implementations SHOULD prefer typed capabilities such as `WRITE_FILE`, `SEND_EMAIL`, or `MERGE_PULL_REQUEST` over generic shell/command execution.

### ATE-EXEC-007 — Generic shell

Generic shell execution SHOULD be disabled by default for governed production actions.

### ATE-EXEC-008 — TOCTOU

Where mutable resource state matters, the executor MUST reject execution if the controlling target state no longer matches the state bound to authorization when required by the risk profile.

---

## 17. External Effect Requirements

### ATE-EFF-001 — Outcome distinction

P1+ executors MUST distinguish confirmed success from known failure-before-effect and uncertain/unknown external effect where the resource semantics permit ambiguity.

### ATE-EFF-002 — Blind retry prohibited

An operation in `UNKNOWN_EFFECT` or equivalent state MUST NOT be blindly retried using the same single-use authorization.

### ATE-EFF-003 — Idempotency

Where the external resource supports idempotency, P1+ SHOULD bind an idempotency key to the TrustDecision/action identity.

P2+ SHOULD require idempotency for repeat-sensitive external effects where supported.

---

## 18. Audit and Accountability Requirements

### ATE-AUD-001 — Decision audit

P1+ MUST record every trust grant and trust denial relevant to governed execution.

### ATE-AUD-002 — Execution audit

P1+ MUST record governed execution attempts and outcomes.

### ATE-AUD-003 — Nonce transitions

Security-relevant nonce transitions SHOULD be auditable.

### ATE-AUD-004 — Immutable correction model

Audit corrections MUST append new records; prior signed historical records MUST NOT be silently rewritten.

### ATE-AUD-005 — Tamper evidence

P1+ audit records MUST provide tamper-evident ordering, such as signed sequence numbers and/or hash chaining.

### ATE-AUD-006 — Authoritative execution record

The executor/audit-plane record MUST be authoritative for whether a governed external action was attempted/executed; participant narrative MUST NOT override it.

### ATE-AUD-007 — Audit availability

For policy-designated high-risk actions, inability to commit required audit evidence MUST block execution.

### ATE-AUD-008 — Independent preservation

P2+ SHOULD persist checkpoints or replicas outside the participant/executor compromise domain.

P3 MUST use independent durable audit preservation for critical actions.

---

## 19. Federation Requirements

### ATE-FED-001 — Local control

Foreign trust evidence MUST be accepted only according to local federation policy.

### ATE-FED-002 — Non-transitive default

Trust MUST NOT transitively propagate from domain A through domain B to domain C unless explicitly authorized by C's local federation policy.

### ATE-FED-003 — Role-scoped foreign trust

Recognition of a foreign authority MUST be scoped by artifact class/role and MUST NOT imply recognition of all authorities in that domain.

### ATE-FED-004 — Local policy supremacy

Foreign policy MUST NOT override local active policy governing local resources.

### ATE-FED-005 — Foreign authorization

Foreign capability/authorization artifacts MUST NOT directly create local execution authority unless local policy explicitly delegates that role and scope.

### ATE-FED-006 — Local revocation override

Local suspension or revocation of a federation relationship MUST override continued foreign validity.

---

## 20. Risk and Assurance Requirements

### ATE-RISK-001 — Risk classification

Production deployments SHOULD assign governed action classes to explicit risk levels.

### ATE-RISK-002 — Assurance proportionality

Required assurance MUST NOT decrease as the maximum credible harm of the requested action increases.

### ATE-RISK-003 — Freshness proportionality

Higher-risk actions SHOULD require equal or stronger evidence freshness than lower-risk actions.

### ATE-RISK-004 — Authority independence

Higher-risk actions SHOULD require stronger separation or multiplicity of authorization authorities.

### ATE-RISK-005 — Human approval

Policies MUST explicitly identify action classes requiring human approval rather than relying on ad hoc runtime judgment.

### ATE-RISK-006 — Runtime elevation

Materially increased runtime/environment risk MAY elevate assurance requirements, but MUST NOT silently lower them.

---

## 21. Human Approval Requirements

### ATE-HUM-001 — Independent approval path

Where human approval is required, the approval mechanism MUST be inaccessible to participant self-generation.

### ATE-HUM-002 — Exact action binding

Human approval MUST bind the specific action or clearly defined capability scope being approved.

### ATE-HUM-003 — Freshness

Human approval MUST include or inherit a validity period appropriate to the action risk.

### ATE-HUM-004 — No semantic substitution

Approval for one action MUST NOT be reused for a materially different action.

---

## 22. Availability and Dependency Failure Requirements

### ATE-FAIL-001 — Critical dependency uncertainty

When a security-critical dependency is unavailable and its state is required to determine safe execution, the system MUST NOT default to grant.

### ATE-FAIL-002 — Verification exception

Unexpected verifier exceptions MUST result in no execution.

### ATE-FAIL-003 — Revocation service failure

For risk classes requiring current revocation state, revocation-service unavailability MUST block execution unless an explicit bounded fail-safe policy exists and the claimed profile permits it.

### ATE-FAIL-004 — Credential vault failure

Credential retrieval failure MUST NOT cause authorization widening or alternate credential fallback outside policy.

---

## 23. P0 Conformance Requirements

To claim `ATE-P0-CONFORMANT`, an implementation MUST demonstrate at minimum:

1. deterministic canonical action representation;
2. deterministic `TRUST_GRANTED` / `TRUST_DENIED` evaluation;
3. explicit subject/session binding where applicable;
4. exact policy binding;
5. capability-scope enforcement;
6. separate participant and Trust Decision Authority keys/identities;
7. single-use nonce/replay rejection;
8. at least one valid grant case;
9. at least one scope-denial case;
10. at least one provenance/governance binding-denial case;
11. audit evidence sufficient to reconstruct the test;
12. explicit statement that same-host/root compromise is outside P0 assurance.

P0 MAY use fixture keys and deterministic/local evidence.

---

## 24. P1 Conformance Requirements

To claim `ATE-P1-CONFORMANT`, the implementation MUST satisfy P0 plus:

1. a distinct Capability Executor boundary;
2. participant inability to directly access the governed resource using equivalent credentials;
3. protected executor/resource credentials;
4. durable nonce state;
5. atomic nonce reservation;
6. concurrent replay rejection;
7. active revocation checking;
8. authoritative current-policy checking;
9. signed TrustDecision verification inside the executor boundary;
10. tamper-evident audit ordering;
11. durable audit records;
12. explicit handling of execution success/failure/unknown effect where applicable;
13. typed resource adapter(s) for claimed governed capabilities;
14. evidence that direct bypass is denied.

---

## 25. P2 Conformance Requirements

To claim `ATE-P2-CONFORMANT`, the implementation MUST satisfy P1 plus:

1. isolated executor service/process boundary appropriate to the deployment;
2. stronger key custody for critical online authorities;
3. short-lived TrustDecisions for high-risk actions;
4. final revocation recheck immediately before designated high-risk executions;
5. final policy/current-state recheck where required;
6. resource-state/TOCTOU binding for mutable high-risk targets where relevant;
7. human approval or independent second authority for policy-designated operations;
8. independent audit checkpoint/replication outside the participant compromise domain;
9. stronger behavioral/identity evidence freshness according to policy;
10. no automatic retry after unknown external effect;
11. documented incident response for authority-key compromise.

---

## 26. P3 Conformance Requirements

To claim `ATE-P3-CONFORMANT`, the implementation MUST satisfy P2 plus:

1. high-assurance protection for critical trust-root/trust-decision keys;
2. multi-party or threshold authorization for designated critical actions;
3. strongly isolated executor/enforcement environment;
4. strict resource/network isolation preventing participant bypass;
5. independent durable audit preservation;
6. hardened trust-root change governance;
7. mandatory human authorization for policy-defined critical action classes;
8. explicit compromise-domain analysis demonstrating that participant compromise alone cannot produce an authorized critical action;
9. tested recovery/revocation procedure for critical authority compromise;
10. evidence that trust-state rollback and stale authoritative state are rejected.

P3 conformance MUST NOT be claimed solely from software logic running under one unrestricted host-root authority.

---

## 27. Conformance Evidence Package

Each conformance claim MUST produce an immutable or content-addressed evidence package containing at minimum:

```text
ConformanceEvidencePackage {
    ate_spec_version
    implementation_id
    deployment_profile
    trust_domain
    environment_description
    governed_capability_classes[]

    requirement_results[]
    test_case_results[]
    artifact_hashes[]

    trust_root_snapshot_or_digest
    policy_epoch
    revocation_epoch
    federation_epoch_if_applicable

    known_limitations[]
    excluded_requirements[]
    deviations[]

    evidence_created_at
    evidence_authority
    signature_or_integrity_proof
}
```

Every mandatory requirement for the claimed profile MUST be mapped to evidence.

---

## 28. Requirement Result States

A conformance assessment SHOULD use:

- `PASS`
- `FAIL`
- `NOT_APPLICABLE`
- `NOT_TESTED`

`NOT_TESTED` MUST NOT satisfy a mandatory requirement.

`NOT_APPLICABLE` MUST include a rationale showing why the requirement cannot affect any capability included in the claim.

---

## 29. Conformance Classification

Recommended classifications:

```text
ATE_P0_CONFORMANT
ATE_P1_CONFORMANT
ATE_P2_CONFORMANT
ATE_P3_CONFORMANT
ATE_CONFORMANCE_FAILED
ATE_CONFORMANCE_INCONCLUSIVE
```

An implementation MUST NOT claim a higher profile merely because it satisfies selected controls from that profile.

All mandatory controls for that profile must be satisfied.

---

## 30. Profile Inheritance

Profiles are cumulative:

```text
P3 ⊃ P2 ⊃ P1 ⊃ P0
```

A P2 claim therefore requires all applicable P0, P1, and P2 mandatory requirements.

---

## 31. Partial Capability Conformance

An implementation MAY claim conformance for a bounded set of capability adapters.

Example:

```text
ATE-P1-CONFORMANT
Capabilities:
- WRITE_FILE within /srv/ate-sandbox/
- CREATE_TICKET within project X

Not covered:
- shell execution
- cloud infrastructure
- financial actions
```

This is preferable to an overly broad system-level claim.

---

## 32. Test Independence

For P1+, conformance testing SHOULD include at least one adversarial or negative-path evaluation not generated solely by the implementation under test.

For P2+, independent review of the evidence package SHOULD be performed before production claim publication.

For P3, independent security review SHOULD be considered mandatory governance practice even if not technically embedded in the protocol.

---

## 33. Minimum Negative Tests

Every profile MUST include negative evidence demonstrating denial for applicable classes including at least:

- invalid signature;
- untrusted issuer;
- expired artifact;
- revoked artifact/state;
- wrong session/subject;
- wrong policy version/digest;
- capability scope violation;
- action digest substitution;
- replay/consumed nonce;
- unsupported artifact version;
- direct executor bypass attempt where the profile claims enforcement.

Tests MAY be consolidated when one test deterministically establishes multiple related requirements, but evidence MUST show which requirements were exercised.

---

## 34. No Self-Certification Rule

Production conformance evidence MUST NOT rely solely on a participant agent's narrative assertion that controls were applied correctly.

Evidence SHOULD come from:

- signed system artifacts;
- executor records;
- trust-state records;
- audit records;
- deterministic test outputs;
- independent verification where required by profile.

---

## 35. Security Non-Claims

ATE conformance does not prove:

- the AI model is benevolent;
- the model cannot hallucinate;
- all requested actions are semantically correct;
- host compromise is impossible;
- authority compromise is impossible;
- policy authors made correct decisions;
- behavioral evidence predicts all future conduct;
- the external target resource is itself secure;
- every non-governed channel has been eliminated unless explicitly included in the conformance boundary.

---

## 36. Architecture-to-Requirements Traceability

The following architecture artifacts provide the design rationale for this normative profile:

- `ATE-PRODUCTION-ARCHITECTURE-v0.1.md`
- `ATE-PRODUCTION-THREAT-MODEL-v0.1.md`
- `ATE-ENFORCEMENT-PLANE-v0.1.md`
- `ATE-TRUST-ROOT-KEY-CUSTODY-MODEL-v0.1.md`
- `ATE-REVOCATION-TRUST-STATE-MODEL-v0.1.md`
- `ATE-AUDIT-ACCOUNTABILITY-MODEL-v0.1.md`
- `ATE-RISK-ASSURANCE-POLICY-MODEL-v0.1.md`
- `ATE-TRUST-DOMAIN-FEDERATION-MODEL-v0.1.md`
- `ATE-REFERENCE-ARCHITECTURE-COMPONENT-INTERACTION-MODEL-v0.1.md`

Where this conformance profile conflicts with explanatory language in a non-normative architecture artifact, the normative requirement SHOULD control for claims explicitly made under this profile, unless a later approved normative specification supersedes it.

---

## 37. Recommended First Production Conformance Target

The first implementation milestone SHOULD target P0 and then P1, not P2/P3.

Recommended progression:

```text
ATE v0.3.1 integrated PoC
        ↓
P0 conformance harness
        ↓
P1 sandbox enforcement implementation
        ↓
P1 conformance evidence
        ↓
operational lessons
        ↓
P2 design only if justified by real risk
```

This preserves the lean evidence strategy and avoids premature high-assurance complexity.

---

## 38. Conformance Philosophy

ATE conformance measures enforceable system properties, not confidence language.

An implementation should never be considered conformant because it "usually behaves," "appears safe," or "is aligned."

A conformance claim must instead answer concrete questions:

- Was the issuer authorized?
- Was the policy current?
- Was the evidence fresh?
- Was the exact action in scope?
- Was the grant independently signed?
- Was replay impossible?
- Could the participant bypass enforcement?
- Can the complete decision and action be reconstructed afterward?

The governing principle is:

> **ATE assurance is demonstrated by controls and evidence, not by trust in the agent's intentions.**

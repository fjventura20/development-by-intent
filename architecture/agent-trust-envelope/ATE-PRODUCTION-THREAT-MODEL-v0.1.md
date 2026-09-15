# ATE Production Threat Model v0.1

## 1. Purpose

This threat model identifies the major security threats, trust-boundary failures, and attacker capabilities that must be addressed before the Agent Trust Envelope (ATE) moves from proof-of-concept to production use.

The objective is not to prove that ATE is secure against every conceivable adversary.

The objective is to answer:

> What must an attacker compromise, forge, bypass, replay, substitute, or corrupt in order to cause an unauthorized governed action?

The central protected property is:

> **No governed action may occur unless a current, valid, narrowly scoped trust decision authorizes that exact action under the required policy and evidence conditions.**

## 2. Security Objective

Primary objective:

```text
Unauthorized governed action MUST NOT occur.
```

Secondary objectives:

- Unauthorized trust grants must not occur.
- Authorized actions must not exceed granted scope.
- Consumed authorization must not be reusable.
- Stale or revoked evidence must not contribute to grant.
- Trust decisions must remain attributable and auditable.
- Compromise of the participant agent should not automatically imply compromise of the trust-decision authority or executor.

## 3. Protected Assets

Security-sensitive assets include governed capabilities, Trust Decision Authority keys, Authorization Authority keys, Policy Authority keys, Evidence Authority keys, agent identity keys, nonce/replay state, revocation state, audit records, and the Trust Root Registry.

The Trust Root Registry, trust-decision keys, authorization keys, policy keys, executor credentials, and nonce/revocation state are critical assets.

## 4. Trust Boundaries

Recommended boundaries:

```text
┌──────────────────────────────────────┐
│ UNTRUSTED / SEMI-TRUSTED PLANE       │
│ Model                                │
│ Prompts / context                    │
│ Participant agent                    │
│ User-supplied content                │
│ External agent messages              │
└──────────────────────────────────────┘
                 │
                 ▼
┌──────────────────────────────────────┐
│ TRUST VERIFICATION PLANE             │
│ Trust Root Registry                  │
│ Evidence validation                  │
│ Policy validation                    │
│ Revocation checking                  │
│ ATE Verifier                         │
└──────────────────────────────────────┘
                 │
                 ▼
┌──────────────────────────────────────┐
│ AUTHORIZATION PLANE                  │
│ Trust Decision Authority             │
│ Capability issuance                  │
│ Nonce state                          │
└──────────────────────────────────────┘
                 │
                 ▼
┌──────────────────────────────────────┐
│ ENFORCEMENT PLANE                    │
│ Capability Executor                  │
│ External resource adapter            │
└──────────────────────────────────────┘
                 │
                 ▼
┌──────────────────────────────────────┐
│ AUDIT PLANE                          │
│ Append-only audit ledger             │
│ Evidence archive                     │
└──────────────────────────────────────┘
```

The major architectural goal is preventing compromise of one plane from automatically compromising all others.

## 5. Attacker Classes

### T1 — Malicious or compromised model

Attempts to obtain capabilities it should not have through deceptive outputs, unauthorized requests, ambiguity, or policy circumvention.

### T2 — Compromised participant agent

May modify local request objects, replay evidence, substitute sessions, alter context, present stale artifacts, attempt forged authorization, or invoke executors directly if architecture permits it.

### T3 — Malicious external agent

Presents apparently valid credentials or evidence to gain local capabilities.

### T4 — Compromised evidence authority

Can generate formally valid but fraudulent identity, behavioral, or governance evidence.

### T5 — Compromised authorization authority

Can issue excessive or unauthorized CapabilityTokens.

### T6 — Compromised Trust Decision Authority

Can potentially sign fraudulent `TRUST_GRANTED` decisions. Critical severity.

### T7 — Compromised Policy Authority

Can replace or weaken active policy. Potentially systemic compromise.

### T8 — Compromised Capability Executor

Can perform actions despite missing or invalid authorization. Critical severity.

### T9 — Host-level attacker

Controls operating system, process memory, files, or network interfaces and may compromise multiple ATE components simultaneously.

### T10 — Insider/operator attacker

Has legitimate administrative access but intentionally alters policy, trust roots, keys, revocation, configuration, or audit evidence.

## 6. Threat Categories

Major threat families include identity forgery, evidence forgery, artifact substitution, replay, policy downgrade, scope escalation, self-authorization, executor bypass, revocation bypass, freshness bypass, authority compromise, confused deputy, race conditions, external-effect ambiguity, audit tampering, key theft, denial of service, and cross-domain trust abuse.

## 7. Identity Forgery

ATE must verify identity signature, authorized identity issuer, subject binding, session binding, freshness, and revocation.

Failure:

```text
TRUST_DENIED
GX_IDENTITY_INVALID
```

If the identity private key itself is stolen, protected key custody is required; signature verification alone cannot distinguish attacker from legitimate holder.

## 8. Session Substitution

Valid evidence from session A must not be reusable in session B. Session-sensitive artifacts must bind runtime identity, session identity, and freshness challenge with exact equality across controlling artifacts.

Failure:

```text
TRUST_DENIED
GX_SESSION_MISMATCH
```

## 9. COA Substitution

Attacker may present valid acceptance of another COA version, session, subject, or weaker historical conditions.

CapabilityToken and TrustDecision should bind `coa_acceptance_id`, `coa_version`, `coa_fingerprint`, subject, and session.

Failure:

```text
TRUST_DENIED
GX_COA_BINDING_FAILURE
```

## 10. Policy Downgrade

A signed obsolete policy may remain cryptographically valid. ATE must compare against authoritative current policy state: `policy_id`, active version, and active digest.

Failure:

```text
TRUST_DENIED
GX_POLICY_NOT_CURRENT
```

Principle: **Valid does not mean current.**

## 11. VA Policy Substitution

A CapabilityToken issued under policy A must not be evaluated under policy B. Exact `policy_id + policy_version + policy_digest` equality is required across active manifest, CapabilityToken, TrustDecision, and envelope.

## 12. Behavioral Evidence Forgery

Behavioral evidence must be independently signed, issuer-authorized, subject-bound, digest-bound, fresh, and non-revoked.

Failure:

```text
TRUST_DENIED
GX_BEHAVIORAL_INVALID
```

## 13. Stale Behavioral Evidence

Old successful behavioral evidence must not be reused indefinitely. `BehavioralEvidenceReceipt` must include issuance and expiration times; freshness should eventually depend on action risk class.

## 14. Capability Widening

A participant must not be able to expand an authorized operation or target. CapabilityToken signed region must include permitted operations, permitted targets, excluded targets, and constraints. The requested action must be a deterministic subset.

Failure:

```text
TRUST_DENIED
GX_CAPABILITY_SCOPE
```

## 15. Parameter Smuggling

Authorization for a high-level operation is insufficient if dangerous parameters can change after approval. TrustDecision should bind `parameters_digest`, and the executor must execute the exact canonicalized parameters represented by that digest.

## 16. Artifact Substitution

Individually valid artifacts from separate transactions must not be combinable into a valid envelope. All controlling artifacts must participate in the envelope binding hash and bind common subject, session, policy, COA, nonce, and action.

Principle: **Individually valid artifacts do not imply a valid collection.**

## 17. TrustDecision Substitution

A valid grant for action A must not authorize action B. TrustDecision signed region should include requested-action digest, envelope binding hash, CapabilityToken id, and nonce.

## 18. Replay

Previously successful TrustDecision must not execute again.

Nonce lifecycle should include:

```text
UNSEEN → AUTHORIZED → RESERVED → CONSUMED
```

Consumed authorization must never return to executable state.

## 19. Concurrent Replay

Two racing executors must not both observe authorization and execute. `AUTHORIZED → RESERVED` must be atomic using compare-and-set or equivalent transactional semantics.

## 20. Self-Authorization

The participant must not sign its own trust decision. `K_TRUST_DECISION` must reside outside the participant authority boundary, and the executor must verify that the issuer is an authorized Trust Decision Authority.

## 21. Executor Bypass

This is one of the most important production threats.

Protected resources must accept governed actions only through the Capability Executor or credentials available exclusively to it. If the agent can bypass the executor, ATE becomes advisory rather than enforcing.

## 22. Confused Deputy

The executor must independently canonicalize and validate operation, target, and parameters against authorized scope. Never trust participant-provided resource resolution.

## 23. Revocation Bypass

All controlling artifacts must undergo current revocation checks. Expiration and revocation solve different problems.

## 24. Revocation Race

An artifact may be revoked after verification but before action execution. Possible mitigations include final revocation recheck, very short-lived TrustDecision, revocation epoch binding, or capability leases.

## 25. Trust Root Compromise

Compromise of the Trust Root Registry can redefine who is trusted to issue every other artifact and may cause total trust collapse. Production should consider offline roots, signed registry versions, quorum approval, append-only change logs, human approval, and protected storage.

## 26. Trust Decision Authority Compromise

Compromise of `K_TRUST_DECISION` can produce formally valid fraudulent grants. Low-risk actions may use protected service keys; high-risk actions may eventually require HSM-backed signing, threshold signatures, multiple authorities, or human approval.

## 27. Authorization Authority Compromise

Compromise can issue overbroad CapabilityTokens. Mitigations may include policy-constrained authorization, approval workflows, maximum issuer scopes, and issuer-specific ceilings.

## 28. Policy Authority Compromise

A malicious active policy signed by the authoritative policy root represents governance-root compromise. Mitigation is operational: quorum publication, signed reviews, human approval, delayed activation, rollback, and audit visibility.

## 29. Behavioral Authority Compromise

Fraudulent favorable behavioral receipts may require risk-dependent evaluator requirements, with higher-risk actions using fresher or multiple independent evaluations.

## 30. Host OS Compromise

If agent, verifier, trust authority, executor, and keys share one compromised host, software-only isolation may collapse. Future high-assurance deployments may require separate hosts, hardened containers, TPM/Secure Enclave/HSM, confidential computing, or remote attestation.

## 31. Verifier Compromise

A verifier could intentionally return PASS for invalid evidence. A future `VerificationReceipt` containing envelope hash, gate results, verifier identity, timestamp, and signature would make verification auditable and independently re-checkable.

## 32. Verification Parser Ambiguity

All signed objects require a single canonical encoding to prevent signature confusion, target mismatch, scope bypass, and hash disagreement. Production must choose one canonicalization scheme.

## 33. Unknown Artifact Version

Unknown versions must fail closed:

```text
GX_UNSUPPORTED_ARTIFACT_VERSION
```

No permissive fallback.

## 34. Protocol Downgrade

Policy Authority should specify a minimum accepted ATE protocol version. Anything lower fails.

## 35. External-Effect Ambiguity

If an external request may have succeeded but confirmation is lost, blind retry can duplicate the effect. Executor needs idempotency or explicit uncertain state such as `FAILED_BEFORE_EFFECT` and `FAILED_AFTER_UNKNOWN_EFFECT`.

For APIs supporting idempotency keys, derive them from `trust_decision_id` and action digest.

## 36. Audit Tampering

Audit records should be signed and hash-chained. Stronger deployments may replicate logs to independent storage.

## 37. Audit Suppression

High-risk actions should tightly couple action success with audit commit where possible. Missing sequence numbers and broken hash chains must be detectable.

## 38. Denial of Service

Security should fail closed while resisting repeated expensive verification, nonce exhaustion, malformed artifact storms, trust-authority overload, and revocation-service overload. Controls may include rate limiting, artifact size limits, verification budgets, caching, and admission control.

## 39. Resource Exhaustion via Evidence Bundles

Bound maximum artifact size, evidence count, chain depth, and policy size. Reject oversized input before expensive cryptography.

## 40. Time Manipulation

Clock manipulation can make expired evidence appear fresh or future policy appear active. Production should define trusted time sources; session-local intervals should use monotonic clocks where possible.

## 41. Human Approval Spoofing

Any future human approval artifact must bind human authority identity, requested action digest, time, scope, and decision through an authentication path inaccessible to the participant agent.

## 42. Cross-Tenant Confusion

Multi-tenant operation should bind `trust_domain` and `tenant_id` across relevant artifacts.

## 43. Federation Trust Abuse

Foreign authority acceptance must be explicit and scoped. Trust in one domain must not automatically transfer to another.

## 44. Delegation Escalation

Delegated scope must be a mathematical subset of parent scope. Delegation chains require bounded depth and should default disabled initially.

## 45. Circular Authorization

Trust graphs must terminate in explicitly configured roots. Circular endorsement alone confers no authority.

## 46. Risk Classification

Preliminary action classes:

- R0 — informational
- R1 — low impact
- R2 — moderate
- R3 — high
- R4 — critical

Higher risk should require stronger freshness, authorization, approval, key custody, isolation, and auditing.

## 47. Highest-Priority Threats

Highest-priority production threats are:

1. Executor bypass
2. Trust Decision Authority compromise
3. Trust Root compromise
4. Capability widening
5. Replay/concurrent replay
6. Policy downgrade
7. Artifact/session substitution
8. Revocation bypass
9. External-effect ambiguity
10. Host compromise

## 48. Threat-to-Control Matrix

| Threat | Primary control |
|---|---|
| Identity forgery | signed identity + trust roots |
| Session substitution | session binding |
| COA substitution | acceptance fingerprint binding |
| Policy downgrade | active policy manifest |
| VA substitution | exact policy triple |
| Behavioral forgery | signed evidence receipt |
| Stale evidence | TTL/freshness |
| Capability widening | signed least-privilege scope |
| Parameter smuggling | canonical parameters digest |
| Artifact substitution | envelope binding hash |
| Replay | nonce state |
| Concurrent replay | atomic reservation |
| Self-authorization | separate trust authority |
| Executor bypass | resource isolation |
| Confused deputy | executor canonicalization |
| Revocation bypass | G0 revocation |
| Trust-root compromise | protected root governance |
| Audit tampering | hash-chain + signatures |
| Protocol downgrade | minimum-version policy |
| External-effect ambiguity | idempotency/uncertain state |

## 49. Architectural Findings

### Finding 1 — Executor isolation is more important than additional model testing

ATE cannot enforce trust if the participant can bypass it. The next production architecture question should focus on capability mediation, not more model-behavior experiments.

### Finding 2 — Trust roots matter more than signatures

Cryptography proves who signed something. It does not prove the signer was entitled to make that claim.

### Finding 3 — Revocation is mandatory

Expiration alone is insufficient for production. ATE needs a first-class revocation model.

### Finding 4 — One-host deployment limits strong assurance

If model runtime, verifier, trust authority, executor, and keys share a compromised host, software-level separation may become meaningless.

## 50. Recommended Next Architecture Work

No experiment is justified yet.

The next artifact should be **ATE Enforcement Plane v0.1**, defining how the participant agent is technically prevented from bypassing the Capability Executor, where credentials live, how capability scope is enforced, how nonce reservation becomes atomic, how external side effects are handled, how audit evidence is coupled to execution, and where human approval enters for high-risk actions.

## 51. Final Threat-Model Conclusion

ATE's greatest security risk is not that the model produces a bad thought.

The greatest risk is that a bad or compromised component can bypass the mechanisms that convert trust decisions into actual authority.

Therefore production must enforce:

> **No capability without trust verification.**

and:

> **No execution path outside capability enforcement.**

Operational invariant:

```text
If ATE does not grant the exact action,
the system must make that action technically impossible through the governed interface.
```

The PoC established trust decision logic. Production must now establish **trust enforcement**.

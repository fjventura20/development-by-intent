# ATE Risk & Assurance Policy Model v0.1

## 1. Purpose

This document defines how Agent Trust Envelope (ATE) production controls scale with the risk of a requested governed action.

The objective is to prevent two opposite failures:

1. applying weak controls to high-impact actions; and
2. imposing maximum-assurance controls on trivial actions where cost and friction would be disproportionate.

The central rule is:

> The assurance required for an action MUST be proportional to the potential impact of unauthorized, incorrect, compromised, or ambiguous execution.

ATE therefore evaluates not only whether an action is allowed, but also what assurance level is required before that action may be executed.

---

## 2. Core Principle

Risk classification determines minimum assurance requirements.

Conceptually:

```text
Requested Action
      ↓
Risk Classification
      ↓
Required Assurance Profile
      ↓
ATE Evidence + Authority + Enforcement Checks
      ↓
TRUST_GRANTED or TRUST_DENIED
```

A lower-assurance profile MUST NOT satisfy a higher-risk action.

---

## 3. Risk Classes

ATE Production v0.1 defines five baseline risk classes.

### R0 — Informational / Negligible Impact

Examples:

- read public information
- summarize public documents
- perform local non-sensitive calculation
- inspect non-sensitive metadata

Potential harm from unauthorized execution is minimal.

### R1 — Low Impact

Examples:

- read private but low-sensitivity project material
- create a draft that is not transmitted
- create a local non-executable artifact
- read routine internal status information

Impact is limited and generally reversible.

### R2 — Moderate Impact

Examples:

- modify project files
- create or update tickets
- send routine internal messages
- update non-production records
- perform bounded writes to governed repositories

Unauthorized execution can create meaningful operational impact but is usually recoverable.

### R3 — High Impact

Examples:

- merge into protected branches
- deploy production code
- transmit sensitive information externally
- modify infrastructure
- alter access-control settings
- execute destructive operations with recoverable backups

Unauthorized execution may produce serious operational, confidentiality, integrity, or availability consequences.

### R4 — Critical Impact

Examples:

- financial transfer
- security-control disablement
- irreversible destructive action
- production credential rotation with broad scope
- high-impact infrastructure deletion
- actions with material physical-safety implications
- actions whose failure could create regulatory or legal exposure

Unauthorized execution may create severe or irreversible harm.

---

## 4. Risk Classification Object

Each governed action MUST be mapped to an explicit risk classification.

```text
RiskClassification {
    classification_id
    operation
    target_pattern
    risk_level           // R0..R4
    rationale
    policy_id
    policy_version
    policy_digest
    effective_from
    issuer
    signature
}
```

Risk classification itself is policy and MUST be signed by an authorized Policy Authority.

The participant agent MUST NOT be allowed to choose its own risk class.

---

## 5. Risk Classification Rules

Risk should be determined from at least:

```text
operation type
resource sensitivity
target scope
reversibility
blast radius
external side effects
confidentiality impact
integrity impact
availability impact
financial impact
safety impact
privilege level
```

When multiple rules apply, the highest applicable risk class controls.

```text
required_risk = max(applicable_risk_rules)
```

No averaging or downgrading by convenience.

---

## 6. Unknown Risk

If no valid risk classification can be determined:

```text
TRUST_DENIED
GX_RISK_CLASSIFICATION_UNKNOWN
```

Unknown risk MUST NOT default to R0 or R1.

Fail closed.

---

## 7. Assurance Profiles

Each risk class maps to a minimum Assurance Profile.

```text
R0 → A0
R1 → A1
R2 → A2
R3 → A3
R4 → A4
```

Higher assurance profiles satisfy lower ones only when all action-specific requirements remain valid.

---

## 8. Assurance Profile A0

Suitable for R0 informational actions.

Minimum controls:

- recognized participant/runtime identity where applicable
- action type supported
- target classified R0
- no privileged resource credential
- basic audit event
- fail-closed parser behavior

Behavioral evidence may be unnecessary if policy explicitly declares the action non-governed or informational.

No persistent capability should be created.

---

## 9. Assurance Profile A1

Suitable for R1 low-impact actions.

Minimum controls:

- recognized identity
- valid session
- current governing policy
- valid scope authorization
- action canonicalization
- signed or otherwise authenticated decision artifact
- basic revocation check
- auditable execution

Suggested freshness:

```text
Identity credential: policy-defined
Session evidence: current session
Capability authorization: ≤ 24 hours
TrustDecision: ≤ 15 minutes
```

These values are initial architecture defaults, not immutable constants.

---

## 10. Assurance Profile A2

Suitable for R2 moderate-impact actions.

Required controls:

- full ATE verification
- Live Provenance or equivalent runtime/session binding
- current COA acceptance
- current VA policy triple
- valid BehavioralEvidenceReceipt
- least-privilege CapabilityToken
- independent Trust Decision Authority
- exact action digest binding
- executor-mediated execution
- durable nonce state
- atomic nonce reservation
- current revocation check
- append-only audit evidence

Suggested freshness defaults:

```text
BehavioralEvidenceReceipt: ≤ 24 hours
CapabilityToken: ≤ 4 hours
TrustDecision: ≤ 5 minutes
Revocation state: ≤ 5 minutes old
```

---

## 11. Assurance Profile A3

Suitable for R3 high-impact actions.

Includes all A2 controls plus:

- stronger key custody requirements
- final executor-side policy recheck
- final executor-side revocation recheck
- target-state binding where resource is mutable
- short-lived TrustDecision
- mandatory durable audit availability before execution
- separate executor process or service boundary
- narrowly scoped resource credentials
- explicit human approval OR an additional independent authority where policy requires it

Suggested freshness defaults:

```text
BehavioralEvidenceReceipt: ≤ 4 hours
CapabilityToken: ≤ 1 hour
TrustDecision: ≤ 60 seconds
Revocation state: near-current / ≤ 60 seconds
Policy state: rechecked immediately before execution
```

A3 actions SHOULD NOT rely on long-lived participant-held credentials.

---

## 12. Assurance Profile A4

Suitable for R4 critical actions.

Includes all A3 controls plus stronger mandatory controls.

Baseline requirements:

- participant cannot directly access governed resource
- isolated Capability Executor
- hardware-backed or equivalent high-assurance authority key custody where practical
- multiple independent authorization factors
- mandatory human approval for defined critical classes
- threshold or quorum authorization for selected capabilities
- very short-lived TrustDecision
- final revocation and policy epoch validation immediately before execution
- independent audit sink or checkpoint
- external idempotency mechanism where available
- no automatic retry after ambiguous external effect
- explicit recovery procedure

Suggested freshness defaults:

```text
BehavioralEvidenceReceipt: ≤ 1 hour
CapabilityToken: ≤ 15 minutes
TrustDecision: ≤ 30 seconds
HumanApproval: ≤ 5 minutes
Revocation state: current at execution
Policy state: current at execution
```

These defaults may be tightened by domain policy.

---

## 13. Assurance Requirement Matrix

| Control | A0 | A1 | A2 | A3 | A4 |
|---|---:|---:|---:|---:|---:|
| Recognized identity | Optional/policy | Required | Required | Required | Required |
| Session binding | Minimal | Required | Strong | Strong | Strong |
| COA acceptance | Optional/policy | Policy | Required | Required | Required |
| VA compatibility | Basic | Required | Required | Required | Required |
| Behavioral evidence | No/default | Optional/policy | Required | Required + fresh | Required + very fresh |
| CapabilityToken | No persistent | Required | Required | Required | Required |
| Independent Trust Authority | Optional | Recommended | Required | Required | Required |
| Executor mediation | Optional | Recommended | Required | Required | Required/isolated |
| Atomic nonce | No | Recommended | Required | Required | Required |
| Revocation check | Basic | Required | Required | Immediate recheck | Immediate/current |
| Human approval | No | No | Policy-specific | Often required | Mandatory for defined classes |
| Multi-authority/quorum | No | No | No/default | Policy-specific | Required for selected capabilities |
| Audit | Basic | Required | Durable | Mandatory | Mandatory + independent checkpoint |
| Hardware-backed keys | No | No | Optional | Recommended for authorities | Required where feasible |
| Automatic retry after unknown effect | No preference | Restricted | Prohibited by default | Prohibited | Prohibited |

---

## 14. Evidence Freshness Policy

Freshness MUST be defined per evidence class and risk class.

A generalized policy structure:

```text
EvidenceFreshnessRequirement {
    risk_level
    artifact_type
    max_age
    must_be_session_local
    must_recheck_at_execution
    issuer
    signature
}
```

The verifier evaluates:

```text
artifact_age <= max_age
```

where applicable.

If the action's risk class increases, existing evidence may become insufficient even if it has not technically expired.

---

## 15. Freshness Escalation Rule

Example:

A BehavioralEvidenceReceipt issued 12 hours ago may satisfy A2 if A2 allows 24 hours.

The same receipt MUST fail an A4 action requiring ≤ 1 hour freshness.

Result:

```text
TRUST_DENIED
GX_ASSURANCE_EVIDENCE_TOO_STALE
```

This distinguishes artifact expiration from assurance insufficiency.

---

## 16. Key Custody by Assurance Level

Risk policy MUST constrain key custody.

Suggested mapping:

```text
A0 → KC0/KC1 acceptable
A1 → KC1 minimum
A2 → KC1/KC2 depending authority
A3 → KC2 minimum for trust/authorization keys
A4 → KC3 for critical trust roots / selected authorities where feasible
```

The exact KC definitions are controlled by `ATE-TRUST-ROOT-KEY-CUSTODY-MODEL-v0.1.md`.

A key held below the required custody level MUST NOT satisfy the action's assurance profile.

---

## 17. Authority Strength

Higher-risk actions may require stronger authority topology.

Examples:

```text
A1:
one authorized issuer

A2:
independent Trust Decision Authority

A3:
Trust Decision Authority + human approval or second independent authority when policy requires

A4:
quorum/threshold authorization for selected critical capabilities
```

The participant agent MUST never count as an independent authority for its own action.

---

## 18. Human Approval Policy

Human approval is not universally required.

It is risk-triggered.

Human approval policy object:

```text
HumanApprovalRequirement {
    risk_level
    operation_pattern
    target_pattern
    approval_required
    required_role
    max_age
    issuer
    signature
}
```

Where required, approval MUST bind:

```text
requested_action_digest
subject/session where relevant
risk_class
policy_digest
approval timestamp
expiration
```

The model or participant agent MUST NOT be able to generate the human approval artifact.

---

## 19. Human Approval Is Not a Generic Override

Human approval MUST NOT bypass failed ATE controls unless an explicit emergency governance mechanism exists outside the normal participant-accessible path.

Bad pattern:

```text
ATE says DENY
human clicks approve
execution proceeds anyway
```

Preferred pattern:

```text
ATE controls PASS
+ human approval required by policy
→ execution may proceed
```

Human approval supplements assurance; it does not silently disable security invariants.

---

## 20. Executor Isolation by Risk

Suggested deployment requirements:

```text
A0:
no privileged executor required

A1:
local mediator acceptable

A2:
separate executor process recommended/required for governed writes

A3:
separate authenticated executor service
participant lacks direct resource credentials

A4:
isolated executor environment
strict network/resource mediation
high-assurance workload identity
```

Risk policy should make executor isolation explicit rather than implicit.

---

## 21. Credential Scope by Risk

Higher-risk actions require narrower credentials.

Example progression:

```text
A1:
application credential with bounded service scope

A2:
resource-specific credential

A3:
short-lived resource-specific credential

A4:
short-lived one-purpose credential or equivalent capability lease
```

A4 SHOULD avoid reusable broad administrator credentials wherever technically possible.

---

## 22. Revocation Assurance

Revocation guarantees also scale with risk.

Suggested:

```text
A0:
no special revocation freshness

A1:
normal registry check

A2:
recent revocation state required

A3:
revocation rechecked immediately before execution

A4:
current signed revocation epoch required at execution
```

If required revocation state is unavailable:

```text
TRUST_DENIED
GX_ASSURANCE_REVOCATION_UNAVAILABLE
```

---

## 23. Policy Epoch Requirements

High-risk actions MUST bind current policy state.

For A3/A4:

```text
TrustDecision.policy_epoch == current_policy_epoch
```

or the executor must revalidate equivalent state immediately before execution.

A stale but correctly signed TrustDecision MUST NOT survive a controlling policy change if policy declares re-evaluation mandatory.

---

## 24. Audit Strength by Risk

Suggested audit requirements:

### A0
Basic event record.

### A1
Signed/attributable audit record.

### A2
Durable append-only audit record with controlling artifact hashes.

### A3
Mandatory audit availability before execution; hash-chain continuity required.

### A4
A3 plus independent checkpoint/replica or equivalent protection against local deletion and tail truncation.

If mandatory audit infrastructure is unavailable for A3/A4:

```text
NO EXECUTION
GX_ASSURANCE_AUDIT_UNAVAILABLE
```

---

## 25. Behavioral Evidence Strength

Not all behavioral evidence has equal value.

Future production policy may classify evaluators and evidence quality.

Conceptually:

```text
BehavioralEvidenceAssurance {
    evaluator_trust_level
    battery_version
    result
    freshness
    independence_level
}
```

Suggested initial policy:

```text
A0/A1:
not necessarily required

A2:
one approved evaluator receipt

A3:
one high-confidence recent receipt

A4:
multiple independent evidence sources OR a higher-assurance evaluator for selected critical capabilities
```

Do not require evaluator multiplication unless risk justifies it.

---

## 26. Live Provenance Strength

Risk may also determine provenance requirements.

Suggested:

```text
A0:
none/minimal

A1:
session identity sufficient where policy allows

A2:
Live Provenance required

A3:
Live Provenance + executor-separated verification

A4:
Live Provenance plus stronger runtime/host attestation if threat model requires it
```

Hardware attestation is therefore not universally required; it is a possible A4 control.

---

## 27. Risk Elevation at Runtime

An action may become riskier after initial request classification.

Examples:

- target resolves to production rather than staging
- file path resolves outside intended sandbox
- message contains newly detected sensitive data
- requested amount crosses financial threshold
- deployment touches critical infrastructure

The executor/verifier may elevate risk.

Risk may move only upward during evaluation unless authoritative policy explicitly reclassifies the action.

```text
runtime_risk >= initially_classified_risk
```

---

## 28. Risk Downgrade Protection

The participant agent MUST NOT request a lower risk class to avoid controls.

Risk classification comes from authoritative policy and canonicalized action properties.

If participant-supplied risk disagrees with policy:

```text
ignore participant value
use authoritative classification
```

Optionally record:

```text
GX_RISK_CLASSIFICATION_MISMATCH
```

for audit/telemetry.

---

## 29. Dynamic Threshold Rules

Risk may depend on quantitative thresholds.

Example:

```text
TRANSFER_FUNDS:
< $100        → R2
$100–$10,000  → R3
> $10,000     → R4
```

Threshold policy MUST be signed and versioned.

The participant cannot fragment one R4 action into multiple R2 actions if anti-aggregation policy applies.

---

## 30. Aggregation Risk

Repeated individually low-risk actions may collectively create high impact.

Examples:

- many small transfers
- bulk file deletion one file at a time
- repeated disclosure of small data fragments
- incremental permission changes

Production policy should support aggregation windows:

```text
AggregationRule {
    subject
    operation_class
    time_window
    cumulative_threshold
    escalated_risk_level
}
```

This is future implementation work but should be part of the policy model.

---

## 31. Irreversibility Modifier

Irreversibility SHOULD elevate risk.

Examples:

```text
write with version history < permanent deletion
email draft < email send
staging deployment < production deployment
reversible config change < key destruction
```

Risk classification should distinguish reversible and irreversible effects.

---

## 32. Blast Radius Modifier

Actions affecting larger resource sets should classify higher.

Example:

```text
modify one project file      → R2
modify all repository files  → R3
wipe multiple production repos → R4
```

Broad wildcard targets should not inherit the risk of a single narrow target.

---

## 33. Sensitivity Modifier

Data classification can elevate risk.

Example:

```text
public data       → base risk
internal data     → + assurance
confidential data → higher
regulated/secret  → highest applicable
```

ATE policy may reference external data-classification labels.

---

## 34. Autonomy Modifier

The same operation may require stronger controls when fully autonomous.

Example:

```text
human explicitly requests one file write → R2/A2
agent independently decides to modify production config → R3/A3 or R4/A4
```

Production policy may incorporate initiation mode:

```text
USER_DIRECTED
AGENT_PROPOSED
AUTONOMOUS
SCHEDULED
```

Autonomous initiation SHOULD never reduce assurance requirements.

---

## 35. Uncertainty Modifier

If the verifier cannot confidently determine target, effect, or scope, risk should not be lowered.

Examples:

- ambiguous resource alias
- unknown side effect
- unsupported API behavior
- unclear external transaction semantics

Result may be:

```text
risk elevated
```

or:

```text
TRUST_DENIED
GX_ACTION_EFFECT_UNCERTAIN
```

---

## 36. Assurance Profile Binding

The selected Assurance Profile MUST become part of the signed trust decision.

```text
TrustDecision {
    ...
    risk_level
    assurance_profile
    assurance_policy_id
    assurance_policy_version
    assurance_policy_digest
    ...
}
```

The executor verifies the same profile before execution.

---

## 37. Assurance Downgrade Attack

Attack:

A valid TrustDecision produced under A2 is presented for an action currently requiring A3.

Defense:

```text
decision.assurance_profile >= required_assurance_profile
```

and exact policy version/digest checks where policy semantics changed.

Failure:

```text
EXECUTION_DENIED
GX_ASSURANCE_LEVEL_INSUFFICIENT
```

---

## 38. Assurance Policy Versioning

Risk and assurance policy MUST be versioned.

```text
AssurancePolicyManifest {
    policy_id
    version
    digest
    active_from
    minimum_ate_version
    issuer
    signature
}
```

A valid but obsolete assurance policy MUST NOT control new execution.

---

## 39. Emergency Governance

Critical systems may require an emergency path.

Emergency authority MUST NOT be exposed as a participant-agent bypass.

Emergency controls should be:

- independently authenticated
- human/operator initiated
- strongly audited
- time-limited
- narrowly scoped
- unavailable to the participant model/runtime

Emergency governance is outside normal ATE authorization and must be visibly distinct in audit records.

---

## 40. Assurance Failure Codes

Recommended reason codes include:

```text
GX_RISK_CLASSIFICATION_UNKNOWN
GX_ASSURANCE_LEVEL_INSUFFICIENT
GX_ASSURANCE_EVIDENCE_TOO_STALE
GX_ASSURANCE_KEY_CUSTODY_INSUFFICIENT
GX_ASSURANCE_HUMAN_APPROVAL_REQUIRED
GX_ASSURANCE_HUMAN_APPROVAL_EXPIRED
GX_ASSURANCE_AUTHORITY_QUORUM_NOT_MET
GX_ASSURANCE_REVOCATION_UNAVAILABLE
GX_ASSURANCE_AUDIT_UNAVAILABLE
GX_ASSURANCE_EXECUTOR_ISOLATION_INSUFFICIENT
GX_ACTION_EFFECT_UNCERTAIN
GX_RISK_POLICY_NOT_CURRENT
```

Reason codes should be deterministic and machine-readable.

---

## 41. Example — Routine Project File Write

Action:

```text
WRITE_FILE
/project/docs/report.md
```

Policy classification:

```text
R2
```

Required profile:

```text
A2
```

Requires:

- Live Provenance
- COA
- current VA
- BehavioralEvidenceReceipt
- CapabilityToken scoped to file
- independent TrustDecision
- executor mediation
- nonce/replay protection
- durable audit

No human approval required by default.

---

## 42. Example — Protected Branch Merge

Action:

```text
MERGE_PULL_REQUEST
production repository / protected branch
```

Classification:

```text
R3
```

Required profile:

```text
A3
```

Additional requirements:

- short-lived TrustDecision
- final target-state validation (exact commit SHA)
- executor-side revocation recheck
- separate GitHub executor
- protected credential custody
- mandatory audit
- human approval if policy requires protected-branch approval

---

## 43. Example — Financial Transfer

Action:

```text
TRANSFER_FUNDS
amount = high-value threshold
```

Classification:

```text
R4
```

Required profile:

```text
A4
```

Possible mandatory controls:

- very fresh behavioral evidence
- current COA and VA state
- short-lived CapabilityToken
- independent trust authority
- human approval
- threshold/quorum authorization
- isolated financial executor
- transaction-specific idempotency key
- current revocation state
- independent audit checkpoint
- no automatic retry after unknown effect

---

## 44. Minimal Production Default

ATE SHOULD default governed write operations to at least R2 unless policy explicitly proves lower impact.

Actions involving:

```text
production systems
security settings
external disclosure
privileged credentials
financial value
irreversible deletion
physical safety
```

SHOULD default to R3 or R4 pending specific classification.

---

## 45. Relationship to Value Architecture

VA determines whether an action is compatible with governing values/policy.

Risk & Assurance determines how much evidence and protection are required before a compatible action can execute.

Therefore:

```text
VA compatibility != sufficient assurance
```

An action may be morally/policy compatible yet too risky to execute under weak assurance.

---

## 46. Relationship to CapabilityToken

CapabilityToken defines what may be done.

Risk policy defines what assurance is required to exercise that capability.

Example:

```text
CapabilityToken says:
MERGE pull request 42 is permitted

Risk policy says:
MERGE on protected branch requires A3
```

Both must pass.

---

## 47. Relationship to Revocation

Risk determines revocation freshness requirements.

Higher-risk execution requires stronger evidence that no relevant artifact has been revoked immediately before execution.

---

## 48. Relationship to Audit

Risk determines audit durability and independence.

The audit system is therefore not binary; higher assurance requires stronger accountability guarantees.

---

## 49. Relationship to Key Custody

Risk determines minimum custody for authorities whose compromise could authorize the action.

A cryptographically valid signature from a key stored below the required custody profile is insufficient.

---

## 50. Relationship to Enforcement Plane

Risk controls executor topology.

At lower assurance levels, logical mediation may suffice.

At higher assurance levels, the executor must become increasingly isolated from the participant runtime and its credentials.

---

## 51. Security Invariants

### INV-R1

Participant agents cannot self-select a lower risk classification.

### INV-R2

Required assurance never decreases because evidence is inconvenient or unavailable.

### INV-R3

Unknown risk fails closed.

### INV-R4

An A2 decision cannot authorize an A3/A4 action.

### INV-R5

Higher-risk actions require evidence at least as fresh as lower-risk actions.

### INV-R6

Required human approval cannot be synthesized by the participant.

### INV-R7

Required revocation state must be available before high-risk execution.

### INV-R8

Audit requirements cannot be silently relaxed after trust grant.

### INV-R9

Executor isolation requirements are part of authorization validity.

### INV-R10

Risk escalation invalidates insufficient previously issued trust decisions.

---

## 52. Explicit Non-Claims

This model does not claim:

- R0–R4 are universally correct for every industry
- the suggested freshness intervals are final production values
- risk can always be quantified precisely
- human approval eliminates critical risk
- hardware-backed custody is required for every deployment
- high assurance guarantees correct model reasoning
- an A4 system is immune to insider or trust-root compromise

The model defines a policy framework for proportional assurance.

Domain deployments must specialize it.

---

## 53. Recommended Initial Policy

For the first production-oriented implementation work, use:

```text
R0/A0: informational only
R1/A1: low-impact reads/drafts
R2/A2: governed writes
R3/A3: production/security/external-sensitive actions
R4/A4: financial/irreversible/safety-critical actions
```

Do not optimize the taxonomy prematurely.

The purpose is to establish mechanical assurance escalation first.

---

## 54. Next Architectural Dependency

With risk and assurance formalized, the next unresolved production problem is trust across administrative boundaries.

Recommended next artifact:

**ATE Trust Domain & Federation Model v0.1**

It should define:

- local trust domains
- foreign authority recognition
- cross-domain identity
- policy compatibility
- issuer constraints
- federation allowlists
- delegation boundaries
- transitive-trust prohibition
- foreign revocation state
- cross-domain audit attribution

Federation should remain architecture-only until local production enforcement is mature.

---

## 55. Conclusion

ATE should not ask only:

> Is this action authorized?

It must also ask:

> How much assurance is required before this particular action is safe enough to execute?

The answer is determined by risk.

The production rule is:

> **Higher potential harm requires stronger, fresher, more independent, and more enforceable evidence of trust.**

This lets ATE remain lightweight for low-impact work while becoming appropriately strict when an agent approaches consequential authority.

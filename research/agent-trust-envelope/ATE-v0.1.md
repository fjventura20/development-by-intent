# Agent Trust Envelope v0.1

**Status:** Draft specification  
**Version:** 0.1  
**Research status:** Experimental; not part of the DbI core architecture

## 1. Objective

The Agent Trust Envelope (ATE) is a structured trust artifact associated with an AI agent participating in a governed interaction.

Its purpose is not to establish that an agent is universally trustworthy. Its purpose is to establish whether there is sufficient evidence to trust a particular agent for a particular task, within a particular execution context, under explicit Conditions of Agency, subject to a defined Value Architecture, with bounded authority, and for a limited period of time.

The governing question is:

> May this agent be trusted to exercise this specific authority under these specific conditions?

Trust is contextual rather than absolute.

## 2. Core model

ATE evaluates six trust dimensions:

1. **Identity and provenance** — who or what is actually executing.
2. **Conditions of Agency** — what explicit obligations and boundaries have been accepted.
3. **Value Architecture** — what decision principles govern choices among otherwise permissible actions.
4. **Behavioral evidence** — what evidence shows that the claimed governance is actually operative.
5. **Authority envelope** — what the agent is explicitly permitted and prohibited from doing.
6. **Validity and revocation** — when the trust decision begins, expires, changes, or is revoked.

No single dimension is sufficient by itself.

## 3. Non-goals

ATE v0.1 does not attempt to prove that an AI model is universally safe, morally aligned, incapable of error, or deserving of unlimited authority. Prompt inclusion, self-description, or prior good behavior are not sufficient substitutes for a scoped trust decision.

## 4. Required envelope structure

```text
AgentTrustEnvelope
├── envelope_metadata
├── agent_identity
├── runtime_provenance
├── conditions_of_agency
├── value_architecture
├── behavioral_evidence
├── authority
├── session_binding
├── validity
├── integrity
└── trust_evaluation
```

## 5. Required fields

### 5.1 Envelope metadata

Required fields:

- `ate_version`
- `envelope_id`
- `created_at`
- `issuer`
- `subject_agent`

### 5.2 Agent identity

Required fields:

- `agent_id`
- `agent_name`
- `agent_role`
- `provider`
- `model_identifier`
- `model_version_if_known`
- `runtime_identifier`
- `runtime_version`
- `identity_evidence`

An agent MUST NOT establish its identity solely through self-assertion.

### 5.3 Runtime provenance

Required fields:

- `runtime_host`
- `runtime_version`
- `tool_environment`
- `execution_mode`
- `model_binding`
- `provenance_evidence`

A material change in provider, model, runtime, execution substrate, or governance-loading mechanism MAY invalidate the envelope.

### 5.4 Conditions of Agency

Required fields:

- `coa_version`
- `coa_hash`
- `coa_location`
- `accepted`
- `accepted_at`
- `acceptance_method`
- `acceptance_evidence`

Acceptance MUST be associated with the active agent instance. Mere prompt presence is insufficient.

### 5.5 Value Architecture

Required fields:

- `va_version`
- `va_hash`
- `va_location`
- `declared_active`
- `activation_evidence`

The governing Value Architecture SHOULD remain stable for the governed session unless an explicit renegotiation procedure is used.

### 5.6 Session binding

Session binding is mandatory.

Required fields:

- `session_id`
- `session_started_at`
- `agent_instance_id`
- `coa_binding`
- `va_binding`
- `runtime_binding`
- `binding_evidence`

An attestation created in Session A MUST NOT automatically authorize behavior in Session B.

### 5.7 Behavioral evidence

Required fields:

- `evidence_set_id`
- `tests`
- `results`
- `evaluated_at`
- `evaluator`
- `evidence_hash`

Each behavioral test SHOULD identify:

- `test_id`
- `tested_property`
- `expected_behavior`
- `observed_behavior`
- `result`

Allowed result values:

- `PASS`
- `FAIL`
- `INCONCLUSIVE`
- `NOT_TESTED`

Independent evidence SHOULD carry greater weight than self-attestation.

### 5.8 Authority envelope

Required fields:

- `authorized_actions`
- `prohibited_actions`
- `authorized_resources`
- `resource_limits`
- `financial_limits`
- `tool_permissions`
- `escalation_requirements`
- `human_approval_requirements`

Authority not explicitly granted is denied by default.

### 5.9 Validity

Required fields:

- `valid_from`
- `valid_until`
- `termination_conditions`
- `revocation_status`
- `revocation_reference`

Trust MUST expire or be explicitly renewed.

### 5.10 Integrity

Required fields:

- `envelope_hash`
- `component_hashes`
- `issuer_signature_if_available`
- `tamper_status`

The integrity mechanism must make unauthorized alteration detectable.

## 6. Trust decisions

ATE v0.1 defines four outcomes:

- `TRUST`
- `RESTRICT`
- `DENY`
- `INSUFFICIENT_EVIDENCE`

### 6.1 TRUST

A `TRUST` decision requires all mandatory trust gates to pass:

- G1 Identity verified
- G2 Runtime provenance verified
- G3 Conditions of Agency accepted
- G4 COA bound to current session
- G5 Value Architecture identified and bound
- G6 Behavioral evidence meets the required threshold
- G7 Requested authority is explicitly permitted
- G8 Envelope remains valid
- G9 Envelope integrity verified
- G10 No controlling contradiction exists

Formally:

```text
TRUST = G1 ∧ G2 ∧ G3 ∧ G4 ∧ G5 ∧ G6 ∧ G7 ∧ G8 ∧ G9 ∧ G10
```

### 6.2 RESTRICT

`RESTRICT` means sufficient trust exists for some activity but not for the full requested authority. Restriction is preferred over binary denial when risk can be reduced through narrower permissions or added human approval.

### 6.3 DENY

`DENY` is required when a material trust requirement fails, including identity conflict, session mismatch, invalid integrity, revoked or expired authority, or an action outside the granted envelope.

### 6.4 INSUFFICIENT_EVIDENCE

`INSUFFICIENT_EVIDENCE` applies when no known violation has occurred but the evidence required to justify trust does not exist.

Absence of failure is not positive evidence of trust.

## 7. Trust is task-specific

ATE rejects universal trust scores.

An agent may simultaneously be trusted to read a repository, restricted when modifying files, and denied permission to alter frozen evidence or send external communications.

Conceptually:

```text
Trust = f(agent, task, authority, context, governance, evidence, time)
```

## 8. Evidence hierarchy

ATE v0.1 uses the following rough hierarchy from weaker to stronger evidence:

1. Agent self-assertion
2. Prompt inclusion
3. Explicit acknowledgement
4. Structured attestation
5. Session-bound attestation
6. Runtime-generated evidence
7. Independent observation
8. Repeated behavioral evidence
9. Cryptographically verifiable provenance
10. Independent behavioral and provenance verification

Higher-risk authority SHOULD require stronger evidence.

## 9. Critical distinction

ATE MUST distinguish between:

> The agent received the governing conditions.

and:

> The active agent instance is demonstrably operating under those governing conditions.

The former is informational. The latter is the requirement.

## 10. Threat and failure model

ATE v0.1 assumes failure may result from deception, accidental mismatch, stale state, model substitution, runtime substitution, session loss, incomplete initialization, prompt truncation, altered governance artifacts, invalid permissions, tool escalation, weak evidence, misconfiguration, or evaluator error.

Malicious intent is not required for an unsafe outcome.

## 11. Attack and failure cases

### ATE-F1 — Self-declared identity spoofing

An agent claims an identity that conflicts with runtime provenance.

**Required response:** `DENY` when the conflict is established, otherwise `INSUFFICIENT_EVIDENCE`.

### ATE-F2 — Prompt presence without binding

Conditions of Agency appear in an initialization prompt, but execution occurs in a separate session without binding evidence.

**Required response:** `DENY` for governed authority requiring session binding.

### ATE-F3 — Stale trust envelope

An envelope issued for one model/runtime/session is reused after a material execution identity change.

**Required response:** `DENY`.

### ATE-F4 — Authority escalation

An agent authorized to read attempts to write, commit, send, delete, or otherwise exceed its granted authority.

**Required response:** deny the action. Repeated attempts MAY trigger revocation.

### ATE-F5 — Governance artifact substitution

The accepted COA or Value Architecture hash differs from the artifact active at execution time.

**Required response:** `DENY` until explicit acceptance and rebinding occur.

### ATE-F6 — Value Architecture drift

The governing Value Architecture changes silently during a governed session.

**Required response:** invalidate the existing trust decision and require renegotiation.

### ATE-F7 — Behavioral contradiction

Observed behavior materially contradicts a claimed governing value or condition.

**Required response:** `DENY` or revoke existing trust. Observed behavior overrides conflicting self-attestation.

### ATE-F8 — Envelope tampering

Authority or governance metadata are modified after issuance and integrity verification fails.

**Required response:** `DENY`.

### ATE-F9 — Missing evidence

Required evidence for current-session governance cannot be produced and no contradiction is known.

**Required response:** `INSUFFICIENT_EVIDENCE`.

### ATE-F10 — Trusted agent, unsafe request

The agent itself has a valid envelope but the requested action lies outside its authority.

**Required response:** deny the action. Trust in the agent does not imply authority for every action.

## 12. Minimal trust algorithm

```text
function evaluate_trust(agent, action, envelope):

    if envelope.integrity_invalid:
        return DENY

    if envelope.expired_or_revoked:
        return DENY

    if identity_not_verified:
        return INSUFFICIENT_EVIDENCE

    if runtime_does_not_match:
        return DENY

    if coa_not_accepted:
        return DENY

    if coa_not_bound_to_session:
        return DENY

    if value_architecture_not_bound:
        return DENY

    if action_not_authorized:
        return DENY

    if behavioral_threshold_not_met:
        return RESTRICT or INSUFFICIENT_EVIDENCE

    if material_contradiction_exists:
        return DENY

    return TRUST
```

## 13. Proof-of-concept: ATE-POC-001

### Objective

Determine whether a verifier can distinguish among:

1. a legitimately trusted agent;
2. an apparently compliant but unbound agent; and
3. a trusted agent requesting authority beyond its envelope.

The verifier returns one of:

- `TRUST`
- `RESTRICT`
- `DENY`
- `INSUFFICIENT_EVIDENCE`

and identifies the controlling reason.

### Case 1 — Fully bound trusted agent

Identity and runtime are verified; COA and Value Architecture are accepted and bound to the active session; behavioral diagnostics pass; the envelope is intact and active; the requested action is explicitly authorized.

**Expected result:** `TRUST`

### Case 2 — Governance present but session unbound

Identity and runtime are verified, but governance was accepted in Session A while the current execution occurs in Session B with no binding evidence.

**Expected result:** `DENY`

**Controlling reason:** governance presence is not equivalent to current-session governance.

### Case 3 — Trusted identity, excess authority

Identity, runtime, COA, Value Architecture, session binding, and behavioral evidence are valid, but the requested action is outside the authority envelope.

**Expected result:** `DENY`

**Controlling reason:** trust in the agent does not imply unlimited authority.

## 14. POC acceptance criteria

ATE-POC-001 passes if the verifier produces:

```text
Case 1 → TRUST
Case 2 → DENY
Case 3 → DENY
```

and identifies the correct controlling reason in each case.

No probabilistic scoring or large candidate set is required for this initial proof of concept.

## 15. POC falsification conditions

The proof of concept fails if any of the following occur:

- Case 1 is denied despite valid evidence and authority.
- Case 2 is trusted based only on prior prompt exposure or acknowledgement.
- Case 3 is trusted because the agent itself is considered trustworthy.
- Missing evidence is silently treated as positive evidence.
- Identity claims are accepted without provenance.
- Session mismatch is ignored.
- Unauthorized authority is inferred.

## 16. Security principles

### Claims establish hypotheses; evidence establishes trust.

An agent stating that it is trustworthy or governed is not sufficient evidence that it is so.

### Least privilege

Grant only the minimum authority necessary to accomplish the intended task.

### Continuous conditional trust

A trust decision remains conditional on identity continuity, runtime continuity, governance continuity, behavioral consistency, authority compliance, integrity, and validity.

### Human sovereignty

No agent may enlarge its own trust envelope merely because expansion would improve task completion. Changes to governing conditions, authority, resources, identity, session scope, or Value Architecture must follow an authorized procedure.

## 17. Relationship to Condition of Agency

Conditions of Agency answer:

> What obligations and boundaries govern this agent?

ATE answers:

> What evidence demonstrates that these obligations and boundaries actually govern this active agent instance?

ATE therefore provides a verification and authorization layer around Condition of Agency.

## 18. Relationship to Value Architecture

Value Architecture answers:

> How should the agent choose among competing permissible actions?

ATE answers:

> Which Value Architecture is active, how is it bound to the executing agent, and what evidence exists that behavior remains consistent with it?

ATE therefore provides provenance and accountability for Value Architecture.

## 19. Architectural summary

```text
Identity
   ↓
Provenance
   ↓
Conditions of Agency
   ↓
Value Architecture
   ↓
Session Binding
   ↓
Behavioral Evidence
   ↓
Authority
   ↓
Integrity + Validity
   ↓
Trust Decision
```

No individual element is sufficient by itself. Trust arises from the chain.

## 20. Central proposition

> AI agents should not be trusted because they appear intelligent, cooperative, aligned, or familiar. They should be entrusted with authority only when sufficient evidence establishes who they are, what governs them, what they are allowed to do, and whether those conditions remain valid in the active execution context.

## 21. Graduation rule

ATE v0.1 remains an experimental research artifact. It should not be incorporated into the DbI core architecture until the proof-of-concept evidence supports the central proposition and the specification survives adversarial review for ambiguity, unenforceable requirements, circular trust dependencies, and unverifiable claims.

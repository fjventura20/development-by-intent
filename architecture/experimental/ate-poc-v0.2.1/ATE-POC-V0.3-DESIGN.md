# Agent Trust Envelope v0.3 — End-to-End Trust Decision Integration (DESIGN ONLY)

**Status:** DESIGN ONLY — supersedes ATE v0.2.1's artifact-binding scope by adding an end-to-end deterministic trust decision for a governed action.
**Author:** Hermes (research-manager-mandate-2026-09-15)
**Date:** 2026-09-15
**Authority:** Frank Ventura (PI), per directive of 2026-09-15 (PI REVIEW ACCEPTED of Live Provenance PoC ESTABLISHED at commit `e5c7a39`; ATE v0.3 design authorized).

## 0. Provenance and Predecessors

ATE v0.3 is **NOT a redesign** of any earlier artifact. It composes the following frozen/established primitives into a single end-to-end trust-decision pipeline:

| Predecessor | Status | Where used |
| -- | -- | -- |
| Live Provenance PoC v0.2.1 LIVE_PROVENANCE_POC_PRIMITIVE_ESTABLISHED (commit `e5c7a39`) | FROZEN | Runtime / session / model-response binding |
| Ephemeral Session Identity primitive (commit `21b23de`) | ESTABLISHED | Public-key identity per session |
| TGE v0.2.1 Condition of Agency | DESIGN (canonical reference) | COA acceptance evidence |
| ATE-PoC v0.2.1 (commit `93e14fa`) | FROZEN (DETERMINISTIC BINDING CHAIN + REPLAY SEPARATION ESTABLISHED) | Linear binding graph, DecisionRecord signing, GEL pipeline structure |
| Stage C v0.2.2 GEL (SHA-256 `dfcf2514...`) | FROZEN | Reuse as-is for any executed-action evaluation |
| Stage C behavioral evidence (Stage C v0.1: 36b5c96f...) | DESIGN-only context | Behavioral evidence contract reuse |

**Predecessors preserved byte-identically (verified):**
- All Live Provenance artifacts (`a4f4836a...`, `4a855be1...`, `ee3ca128...`, `82725296...`, `fab8491f...`, `7816d722...`, `fc9884f5...`, `bdae161e...`, `df7f474b...`, `3a59ee7e...`, `00975514...`, `a4267f35...`, `dddb784f...`, `6c3a71a1...`, `b8e5eb72...`, `9f296f14...`).
- All ATE v0.2.1 artifacts (`f3261448...`, `93e14fa6...`, `c82f6233...`, `fa8fa375...`, `0cb3edcf...`, `438b1f60...`, `6cd0f41d...`, `0b4f377f...`, `dfcf2514...`).

**Frozen implementation artifacts that ATE v0.3 MAY reference but MUST NOT modify:** `K_IDENTITY`, `K_TGE`, `K_AUTHORITY`, `K_GEL`, `K_PIPELINE` from ATE-PoC v0.2.1; ephemeral session identity private key from Live Provenance PoC.

## 1. Purpose and controlling question

ATE v0.3 demonstrates — by deterministic computation, not by opinion — that an Agent Trust Envelope (ATE) can produce, for one specific governed action, a single binary trust decision:

> Given this agent, this session, this accepted governance, this evidence, and this requested action — may this agent perform this action now?

Answer: **TRUST_GRANTED** or **TRUST_DENIED**, plus a machine-readable reason code.

ATE v0.3 differs from ATE v0.2.1 in scope, not in substrate. ATE v0.2.1 proved that artifacts can be deterministically bound and that replay is separated. ATE v0.3 adds the **trust-decision layer** that consumes those bindings plus four additional inputs (COA acceptance, Value Architecture compatibility, behavioral evidence, least-privilege authorization) and emits one binary decision plus reason.

ATE v0.3 is a **decision-layer PoC**, not a production trust system. The implementation, if later executed, would require approximately 3 diagnostic cases (case A grant, case B scope-mismatch deny, case C binding-break deny) — *not* dozens of model calls. No participant or evaluator engagement is part of ATE v0.3.

## 2. Required trust-decision chain

```
Runtime / Live Provenance
        |
        v
Condition of Agency (COA) acceptance
        |
        v
Value Architecture (VA) compatibility
        |
        v
Behavioral evidence / attestation
        |
        v
Least-privilege Authorization
        |
        v
Signed Governed Action
        |
        v
TRUST_DECISION: GRANTED | DENIED  (single binary outcome)
```

Each link's output is a structured artifact with its own cryptographic identity (signatures / canonical fingerprints). The trust-decision function consumes all six and emits one decision.

## 3. Data structures (minimum)

### 3.1 Reused structures (NOT redefined)

| Structure | Source | Reuse policy |
| -- | -- | -- |
| `IdentityAttestation` | ATE v0.2.1 | Reuse byte-identically (signed by K_IDENTITY) |
| `SessionContext` | ATE v0.2.1 | Reuse byte-identically |
| `AcceptanceReceipt` (TGE) | TGE v0.2.1 / ATE v0.2.1 | Reuse byte-identically (signed by K_TGE) |
| `CapabilityToken` | ATE v0.2.1 | EXTENDED below |
| `SignedCandidateAction` | Live Provenance v0.2.1 + ATE v0.2.1 | Reuse (Live-Provenance domain) |
| `SignedExecutedAction` | ATE v0.2.1 (GEL-signed) | Reuse byte-identically |
| `DecisionRecord` | ATE v0.2.1 | EXTENDED below with trust-decision fields |

### 3.2 New / extended structures (minimum)

#### 3.2.1 `BehavioralEvidence` (NEW, minimal)

```json
{
  "schema_id": "ATE-V3-BEHAVIORAL-EVIDENCE/0.1",
  "evidence_id": "<sha256-derived>",
  "agent_identity_fingerprint": "<matches IdentityAttestation.public_key_sha256>",
  "evaluation_context_id": "<deterministic, e.g. task or run id>",
  "evaluation_window": {"start_utc": 0.0, "end_utc": 0.0},
  "metric_set_id": "<references the named behavior battery used>",
  "metric_results": [
    {"metric_id": "M1", "value": <number>, "pass_threshold": <number>, "passed": true}
  ],
  "battery_pass": true,
  "issued_at_utc": 0.0,
  "behavioral_authority_fingerprint": "<K_BEHAVIORAL pubkey sha256>",
  "behavioral_authority_signature_b64": "<base64>"
}
```

Minimum machine-verifiable check: `battery_pass` boolean + per-metric `passed` flags + signature under a stable `K_BEHAVIORAL` fixture key.

This PoC does NOT create a new behavioral evaluation suite. It reuses the Stage C v0.1 / v0.2 existing evaluation methodology as the *minimum* machine-verifiable representation. The behavioral evidence is a digest of one prior fixed battery result, signed by a stable authority, that the trust-decision can consult.

#### 3.2.2 `ValueArchitecturePolicy` (NEW, minimal)

```json
{
  "schema_id": "ATE-V3-VA-POLICY/0.1",
  "policy_id": "<named policy, e.g. 'VA-CORE-RESTRICTIVE-v0.1'>",
  "policy_fingerprint": "<sha256 of canonical(policy)>",
  "issued_by": "<named authority>",
  "issued_at_utc": 0.0,
  "compatibility_rules": [
    {
      "rule_id": "R1",
      "subject": "operation",
      "operator": "in",
      "values": ["READ", "WRITE_SCOPED", "EXECUTE_SCOPED"],
      "applies_to_targets": ["filesystem:/home/agent/", "network:egress-allowlisted"]
    },
    {
      "rule_id": "R2",
      "subject": "data_class",
      "operator": "neq",
      "values": ["PI", "PHI", "BEHAVIORAL_PRIVACY"]
    },
    {
      "rule_id": "R3",
      "subject": "harm_potential",
      "operator": "lte",
      "values": [<numeric>]
    }
  ],
  "default_action": "DENY",
  "policy_signature_b64": "<base64>"
}
```

The minimum representation is a fixed policy with a small finite rule set, signed by a stable `K_VA` fixture key. The trust-decision evaluates each rule against the requested action; a rule failure → `TRUST_DENIED` with the matching rule id as the reason code. Default-deny is the fail-closed position.

#### 3.2.3 `CapabilityToken` (EXTENDED from ATE v0.2.1)

```json
{
  "schema_id": "ATE-V3-CAPABILITY/0.1",
  "capability_id": "<deterministic>",
  "session_id": "<matches Live Provenance session>",
  "public_key_sha256": "<matches Ephemeral Session Identity>",
  "subject_identity_fingerprint": "<K_IDENTITY fingerprint>",
  "bound_receipt_fingerprint": "<AcceptanceReceipt fingerprint>",
  "operation_scope": ["READ", "WRITE_SCOPED"],
  "target_scope": ["filesystem:/home/agent/proj/*"],
  "constraints": {
    "max_per_call": 1,
    "max_total": 3,
    "excluded_targets": ["filesystem:/home/agent/secrets/*"]
  },
  "valid_from_utc": 0.0,
  "valid_until_utc": 0.0,
  "issued_at_utc": 0.0,
  "authority_fingerprint": "<K_AUTHORITY fingerprint>",
  "authority_signature_b64": "<base64>"
}
```

The extension adds: explicit `target_scope` paths, `constraints` (max calls, excluded targets), `valid_from/until_utc` for expiration, and the binding to `session_id + public_key_sha256 + bound_receipt_fingerprint`. The base ATE v0.2.1 capability structure is preserved; new fields are additive.

#### 3.2.4 `AgentTrustEnvelope` (NEW, aggregate)

```json
{
  "schema_id": "ATE-V3-ENVELOPE/0.1",
  "envelope_id": "<deterministic>",
  "envelope_nonce": "<single-use nonce, same as ATE v0.2.1>",
  "issued_at_utc": 0.0,
  "envelope_binding_hash": "<canonical fingerprint over the bound artifacts>",
  "contents": {
    "identity_attestation": "<IdentityAttestation>",
    "session_context": "<SessionContext incl. Live Provenance public_key_sha256>",
    "live_provenance_acceptance": "<SessionAcceptance from Live Provenance v0.2.1>",
    "live_provenance_action": "<SignedCandidateAction from Live Provenance v0.2.1>",
    "coa_acceptance_receipt": "<AcceptanceReceipt>",
    "va_policy": "<ValueArchitecturePolicy>",
    "behavioral_evidence": "<BehavioralEvidence>",
    "capability_token": "<CapabilityToken (extended)>",
    "requested_action": {
      "operation": "<e.g. 'WRITE_SCOPED'>",
      "target": "<e.g. 'filesystem:/home/agent/proj/file.txt'>",
      "data_class": "<e.g. 'NONE'>",
      "harm_potential": <numeric>,
      "action_struct": "<canonical action_struct bytes>"
    },
    "operator_freshness_challenge": "<same challenge used by Live Provenance>"
  }
}
```

Minimum fields required: those listed above. The envelope does NOT include `SignedExecutedAction` or `DecisionRecord` — those are outputs.

### 3.3 Output: `TrustDecision` (NEW)

```json
{
  "schema_id": "ATE-V3-TRUST-DECISION/0.1",
  "decision_id": "<deterministic>",
  "operation_mode": "TRUST_DECIDE_EXECUTE",
  "envelope_fingerprint": "<matches envelope_binding_hash>",
  "verdict": "TRUST_GRANTED" | "TRUST_DENIED",
  "reason_code": "<one of the codes in §6>",
  "gate_results": [
    {"gate": "G1_RUNTIME_BINDING", "result": "PASS" | "FAIL", "detail": "..."},
    ...
  ],
  "granted_at_utc": 0.0,
  "decision_signature_b64": "<K_TRUST_DECISION signature>"
}
```

`K_TRUST_DECISION` is a new fixture key role, distinct from `K_PIPELINE` of ATE v0.2.1. The split is intentional: K_PIPELINE signs the historical DecisionRecord (binding-verification); K_TRUST_DECISION signs the trust-decision output (the binary grant/deny). The two signatures cover orthogonal concerns.

If the verdict is `TRUST_GRANTED`, the decision authorizes a single downstream invocation of `authorize_governed_action(envelope)` which consumes `envelope_nonce` atomically (analogous to ATE v0.2.1 nonce semantics).

### 3.4 SignedGovernedAction (OUTPUT)

Same cryptographic envelope as `SignedCandidateAction` from Live Provenance v0.2.1, but now ALSO carries the `trust_decision_id` and `envelope_nonce` fields in its signed region, so that downstream observability can verify the action is causally linked to a specific `TRUST_GRANTED` decision.

## 4. Architectural dataflow

```
                  ┌──────────────────────────────────────────────┐
                  │ Agent (real, single session, two turns)      │
                  └────────┬─────────────────────────────────────┘
                           │
                           ▼
   ┌────────────────────────────────────────────────────────────┐
   │  Live Provenance lifecycle (already established @ e5c7a39) │
   │    - Ephemeral session identity (K_session, public-key sig)  │
   │    - Lifecycle hook at agent/turn_response_check.py:142     │
   │    - SessionAcceptance  (event_source=HERMES_MODEL_RESPONSE) │
   │    - SignedCandidateAction (event_source=HERMES_MODEL_RESPONSE)│
   └────────────────┬───────────────────────────────────────────┘
                    │   session_id, public_key_sha256,
                    │   operator_freshness_challenge,
                    │   sa_fingerprint, sca_fingerprint,
                    │   event_source
                    ▼
   ┌────────────────────────────────────────────────────────────┐
   │  COA Acceptance (TGE)                                       │
   │    - AcceptanceReceipt (signed by K_TGE)                    │
   │    - bound to session_id, public_key_sha256, freshness      │
   └────────────────┬───────────────────────────────────────────┘
                    │   receipt_fingerprint
                    ▼
   ┌────────────────────────────────────────────────────────────┐
   │  Value Architecture Policy                                  │
   │    - ValueArchitecturePolicy (signed by K_VA)               │
   │    - rules evaluated against requested action              │
   │    - default-deny                                           │
   └────────────────┬───────────────────────────────────────────┘
                    │   policy_compatibility_verdict
                    ▼
   ┌────────────────────────────────────────────────────────────┐
   │  Behavioral Evidence                                        │
   │    - BehavioralEvidence (signed by K_BEHAVIORAL)            │
   │    - battery_pass boolean + per-metric passed flags         │
   │    - bound to agent_identity_fingerprint                   │
   └────────────────┬───────────────────────────────────────────┘
                    │   battery_pass
                    ▼
   ┌────────────────────────────────────────────────────────────┐
   │  Least-Privilege Authorization                              │
   │    - CapabilityToken (extended, signed by K_AUTHORITY)      │
   │    - bound to session_id, receipt, va_policy, behavioral   │
   │    - operation_scope, target_scope, constraints, expiration│
   └────────────────┬───────────────────────────────────────────┘
                    │   capability_scope_match_verdict
                    ▼
   ┌────────────────────────────────────────────────────────────┐
   │  Trust-Decision Function (NEW)                              │
   │    trust_decide(envelope, *v_contexts) -> TrustDecision     │
   │    evaluates 8 gates (G1..G8)                               │
   │    emits binary verdict + reason code + signed record      │
   └────────────────┬───────────────────────────────────────────┘
                    │   verdict ∈ {TRUST_GRANTED, TRUST_DENIED}
                    ▼
   ┌────────────────────────────────────────────────────────────┐
   │  Authorize Governed Action (only on GRANTED)                │
   │    - atomically consumes envelope_nonce                     │
   │    - emits SignedGovernedAction with trust_decision_id      │
   │    - signed by K_GEL if execution required                 │
   └────────────────────────────────────────────────────────────┘
```

If any gate fails, the trust-decision emits `TRUST_DENIED` with the FIRST failed gate's reason code. The pipeline stops at the first failure (fail-closed fast path).

## 5. Trust-decision pseudocode

```
def trust_decide(envelope: AgentTrustEnvelope, *,
                 identity_att, session_ctx, sa, sca,
                 receipt, va_policy, behavioral, capability,
                 operator_freshness_challenge,
                 now_utc: float) -> TrustDecision:

    gate_results = []

    # G1: runtime binding (Live Provenance)
    if session_ctx.public_key_sha256 != sa.public_key_sha256: DENY(GX_RUNTIME_BINDING)
    elif sa.public_key_sha256 != sca.public_key_sha256: DENY(GX_RUNTIME_BINDING)
    elif sa.public_key_sha256 != identity_att.public_key_sha256: DENY(GX_RUNTIME_BINDING)
    elif sa.freshness_challenge != envelope.contents.operator_freshness_challenge: DENY(GX_FRESHNESS_MISMATCH)
    elif sa.event_source != "HERMES_MODEL_RESPONSE": DENY(GX_EVENT_SOURCE_NOT_LIFECYCLE)
    elif sca.event_source != "HERMES_MODEL_RESPONSE": DENY(GX_EVENT_SOURCE_NOT_LIFECYCLE)
    elif sca.session_acceptance_fingerprint != sa.session_acceptance_fingerprint: DENY(GX_ACCEPTANCE_FINGERPRINT_CHAIN)
    gate_results.append(G1, PASS)

    # G2: COA acceptance binding
    if not verify_signature(K_TGE, receipt): DENY(GX_COA_SIGNATURE_INVALID)
    elif receipt.session_id != session_ctx.session_id: DENY(GX_COA_SESSION_MISMATCH)
    elif receipt.public_key_sha256 != session_ctx.public_key_sha256: DENY(GX_COA_PUBLIC_KEY_MISMATCH)
    elif receipt.freshness_challenge != operator_freshness_challenge: DENY(GX_COA_FRESHNESS_MISMATCH)
    elif now_utc > receipt.expires_at_utc: DENY(GX_COA_EXPIRED)
    elif receipt.session_acceptance_fingerprint != sa.session_acceptance_fingerprint: DENY(GX_COA_NOT_BOUND_TO_LIVE_PROVENANCE)
    gate_results.append(G2, PASS)

    # G3: VA policy compatibility
    if not verify_signature(K_VA, va_policy): DENY(GX_VA_POLICY_SIGNATURE_INVALID)
    elif not va_compatible(va_policy, envelope.contents.requested_action): DENY(GX_VA_POLICY_INCOMPATIBLE)
    gate_results.append(G3, PASS)

    # G4: behavioral evidence
    if not verify_signature(K_BEHAVIORAL, behavioral): DENY(GX_BEHAVIORAL_SIGNATURE_INVALID)
    elif not behavioral.battery_pass: DENY(GX_BEHAVIORAL_BATTERY_FAILED)
    elif behavioral.agent_identity_fingerprint != identity_att.public_key_sha256: DENY(GX_BEHAVIORAL_AGENT_MISMATCH)
    elif now_utc > behavioral.evaluation_window.end_utc + behavioral_evidence_ttl: DENY(GX_BEHAVIORAL_EXPIRED)
    gate_results.append(G4, PASS)

    # G5: capability authorization scope
    if not verify_signature(K_AUTHORITY, capability): DENY(GX_CAPABILITY_SIGNATURE_INVALID)
    elif capability.public_key_sha256 != session_ctx.public_key_sha256: DENY(GX_CAPABILITY_SESSION_MISMATCH)
    elif capability.bound_receipt_fingerprint != receipt.fingerprint: DENY(GX_CAPABILITY_NOT_BOUND_TO_RECEIPT)
    elif envelope.contents.requested_action.operation not in capability.operation_scope: DENY(GX_OPERATION_OUT_OF_SCOPE)
    elif envelope.contents.requested_action.target not in capability.target_scope: DENY(GX_TARGET_OUT_OF_SCOPE)
    elif envelope.contents.requested_action.target in capability.constraints.excluded_targets: DENY(GX_TARGET_EXCLUDED)
    elif not (capability.valid_from_utc <= now_utc <= capability.valid_until_utc): DENY(GX_CAPABILITY_EXPIRED_OR_NOT_YET_VALID)
    gate_results.append(G5, PASS)

    # G6: live-provenance artifact binding (cryptographic chain to runtime)
    if sca.public_key_sha256 != session_ctx.public_key_sha256: DENY(GX_ACTION_RUNTIME_MISMATCH)
    elif sca.freshness_challenge != operator_freshness_challenge: DENY(GX_ACTION_FRESHNESS_MISMATCH)
    elif sca.session_acceptance_fingerprint != sa.session_acceptance_fingerprint: DENY(GX_ACTION_ACCEPTANCE_CHAIN_BROKEN)
    elif not verify_signature(session_ctx.public_key_b64, sca): DENY(GX_ACTION_SIGNATURE_INVALID)
    gate_results.append(G6, PASS)

    # G7: artifact substitution check
    if envelope.envelope_binding_hash != fingerprint_canonical(envelope.contents): DENY(GX_ENVELOPE_BINDING_HASH_MISMATCH)
    gate_results.append(G7, PASS)

    # G8: nonce state (single-use authorization)
    if nonce_registry.lookup(envelope.envelope_nonce) != UNSEEN: DENY(GX_NONCE_NOT_UNSEEN)
    gate_results.append(G8, PASS)

    # All gates passed
    return TrustDecision(verdict=TRUST_GRANTED, reason_code=GX_OK, gate_results=...)
```

The first gate that fails halts evaluation. The decision signature covers the gate_results list (ordered G1..G8) plus verdict and reason_code.

`authorize_governed_action(envelope, trust_decision)` runs AFTER `trust_decide` returns `TRUST_GRANTED` and atomically transitions `envelope_nonce` from `UNSEEN` → `AUTHORIZED` → `CONSUMED` (preserves ATE v0.2.1 semantics).

## 6. Reason codes (machine-readable)

| Code | Gate | Meaning |
| -- | -- | -- |
| `GX_OK` | — | All eight gates PASS; verdict is `TRUST_GRANTED` |
| `GX_RUNTIME_BINDING` | G1 | session/public-key/event-source mismatch in Live Provenance layer |
| `GX_FRESHNESS_MISMATCH` | G1 | operator challenge not bound into Live Provenance evidence |
| `GX_EVENT_SOURCE_NOT_LIFECYCLE` | G1 | SessionAcceptance/SCA event_source not HERMES_MODEL_RESPONSE |
| `GX_ACCEPTANCE_FINGERPRINT_CHAIN` | G1 | Turn A acceptance fingerprint not chained into Turn B action |
| `GX_COA_SIGNATURE_INVALID` | G2 | K_TGE signature on AcceptanceReceipt fails |
| `GX_COA_SESSION_MISMATCH` | G2 | receipt.session_id does not match Live Provenance session |
| `GX_COA_PUBLIC_KEY_MISMATCH` | G2 | receipt.public_key_sha256 does not match Live Provenance key |
| `GX_COA_FRESHNESS_MISMATCH` | G2 | receipt challenge not the operator-generated challenge |
| `GX_COA_EXPIRED` | G2 | now_utc > receipt.expires_at_utc |
| `GX_COA_NOT_BOUND_TO_LIVE_PROVENANCE` | G2 | receipt.session_acceptance_fingerprint != sa.session_acceptance_fingerprint |
| `GX_VA_POLICY_SIGNATURE_INVALID` | G3 | K_VA signature fails |
| `GX_VA_POLICY_INCOMPATIBLE` | G3 | requested action violates at least one VA rule |
| `GX_BEHAVIORAL_SIGNATURE_INVALID` | G4 | K_BEHAVIORAL signature fails |
| `GX_BEHAVIORAL_BATTERY_FAILED` | G4 | battery_pass = false |
| `GX_BEHAVIORAL_AGENT_MISMATCH` | G4 | behavioral evidence binds to a different agent identity |
| `GX_BEHAVIORAL_EXPIRED` | G4 | behavioral evidence older than configured TTL |
| `GX_CAPABILITY_SIGNATURE_INVALID` | G5 | K_AUTHORITY signature fails |
| `GX_CAPABILITY_SESSION_MISMATCH` | G5 | capability.public_key_sha256 != session key |
| `GX_CAPABILITY_NOT_BOUND_TO_RECEIPT` | G5 | capability.bound_receipt_fingerprint != receipt.fingerprint |
| `GX_OPERATION_OUT_OF_SCOPE` | G5 | requested operation not in capability.operation_scope |
| `GX_TARGET_OUT_OF_SCOPE` | G5 | requested target not in capability.target_scope |
| `GX_TARGET_EXCLUDED` | G5 | requested target in capability.constraints.excluded_targets |
| `GX_CAPABILITY_EXPIRED_OR_NOT_YET_VALID` | G5 | capability outside valid_from/valid_until window |
| `GX_ACTION_RUNTIME_MISMATCH` | G6 | SCA public-key fingerprint does not match session |
| `GX_ACTION_FRESHNESS_MISMATCH` | G6 | SCA freshness challenge mismatch |
| `GX_ACTION_ACCEPTANCE_CHAIN_BROKEN` | G6 | SCA session_acceptance_fingerprint != sa fingerprint |
| `GX_ACTION_SIGNATURE_INVALID` | G6 | SCA signature does not verify under session public key |
| `GX_ENVELOPE_BINDING_HASH_MISMATCH` | G7 | envelope_binding_hash != canonical fingerprint of contents |
| `GX_NONCE_NOT_UNSEEN` | G8 | envelope_nonce already AUTHORIZED or CONSUMED |

## 7. Three proposed PoC cases

### Case A: valid evidence + permitted action → TRUST_GRANTED

- A real (or fixture) two-turn Live Provenance session has produced `SessionAcceptance` and `SignedCandidateAction` with `event_source=HERMES_MODEL_RESPONSE`.
- The TGE `AcceptanceReceipt` is correctly signed, fresh, bound to the same session, and chains to the SessionAcceptance fingerprint.
- A `ValueArchitecturePolicy` is presented that permits the requested operation/target/data class/harm potential.
- `BehavioralEvidence` shows `battery_pass = true` and binds to the correct agent identity, not expired.
- A `CapabilityToken` is presented that is signed by K_AUTHORITY, bound to session + receipt, with `operation_scope` containing the operation, `target_scope` containing the target, the target NOT in `excluded_targets`, and a valid `valid_from..until` window covering `now_utc`.
- The envelope's `envelope_binding_hash` matches the canonical fingerprint of its contents.
- The envelope nonce is `UNSEEN` in the nonce registry.

**Expected verdict:** `TRUST_GRANTED`, reason `GX_OK`, all 8 gate results PASS, decision signed by K_TRUST_DECISION.

**Downstream:** `authorize_governed_action(envelope)` consumes the nonce atomically, emits `SignedGovernedAction` with `trust_decision_id` bound in.

### Case B: valid identity/governance but action outside authorization scope → TRUST_DENIED

- All runtime/COA/VA/behavioral evidence passes.
- `CapabilityToken` is otherwise valid, but the requested operation (e.g., `DELETE_FILE`) is NOT in `capability.operation_scope` (which only contains `READ` and `WRITE_SCOPED`), OR the requested target is NOT in `capability.target_scope`, OR the target IS in `excluded_targets`.

**Expected verdict:** `TRUST_DENIED`, reason `GX_OPERATION_OUT_OF_SCOPE` (or `GX_TARGET_OUT_OF_SCOPE` / `GX_TARGET_EXCLUDED` as applicable), gates G1–G5 prior to scope check PASS, gate that detected the scope mismatch FAIL.

**Downstream:** No `SignedGovernedAction` emitted. Nonce remains `UNSEEN` (no consumption).

### Case C: apparently valid authorization but broken/mismatched provenance or COA binding → TRUST_DENIED

- Capability is valid (signature, scope, expiration).
- VA is compatible.
- Behavioral evidence passes.
- But the binding between COA and Live Provenance is broken — e.g., `receipt.session_acceptance_fingerprint != sa.session_acceptance_fingerprint` (`GX_COA_NOT_BOUND_TO_LIVE_PROVENANCE`), OR `receipt.session_id != session_ctx.session_id` (`GX_COA_SESSION_MISMATCH`), OR `sa.event_source != HERMES_MODEL_RESPONSE` (`GX_EVENT_SOURCE_NOT_LIFECYCLE`), OR the envelope_binding_hash is recomputed and mismatches (`GX_ENVELOPE_BINDING_HASH_MISMATCH`).

**Expected verdict:** `TRUST_DENIED`, reason corresponding to the specific broken binding. Gates G1/G2/G7 (depending on which binding was broken) FAIL.

**Downstream:** No `SignedGovernedAction` emitted. Nonce remains `UNSEEN`.

## 8. Attack / failure cases

Beyond the three core cases, ATE v0.3 must fail closed for the following situations (each maps to a §6 reason code):

- **Missing evidence:** any of `IdentityAttestation`, `SessionContext`, `SessionAcceptance`, `SignedCandidateAction`, `AcceptanceReceipt`, `ValueArchitecturePolicy`, `BehavioralEvidence`, `CapabilityToken` is absent → `GX_*_SIGNATURE_INVALID` (signature cannot be verified) or an explicit precondition `GX_*_MISSING` (the design records the precondition but treats absence as signature invalid).
- **Expired evidence:** now_utc past `receipt.expires_at_utc` / `capability.valid_until_utc` / `behavioral_evaluation_window.end_utc + ttl` → corresponding expiration code.
- **Mismatched session identity:** session_id or public_key_sha256 in any artifact does not match the captured Live Provenance session identity → corresponding session-mismatch code.
- **Incompatible VA policy:** any rule in `ValueArchitecturePolicy.compatibility_rules` evaluates false against the requested action → `GX_VA_POLICY_INCOMPATIBLE`.
- **Missing COA acceptance:** AcceptanceReceipt absent, or signature invalid, or not bound to the SessionAcceptance fingerprint → `GX_COA_*` codes.
- **Behavioral-evidence failure:** `battery_pass = false`, signature invalid, or identity mismatch → `GX_BEHAVIORAL_*` codes.
- **Authorization mismatch:** operation/target scope mismatch, exclusion match, expiration → `GX_OPERATION_OUT_OF_SCOPE` / `GX_TARGET_*` / `GX_CAPABILITY_*` codes.
- **Artifact substitution:** a Turn A artifact placed in a Turn B envelope, or a Turn B artifact placed in a Turn A envelope, or a different session's evidence substituted → `GX_ACTION_ACCEPTANCE_CHAIN_BROKEN` / `GX_RUNTIME_BINDING` / `GX_COA_NOT_BOUND_TO_LIVE_PROVENANCE` / `GX_ENVELOPE_BINDING_HASH_MISMATCH`.

Each scenario is a deterministic, locally reproducible check (no model invocation required to detect the failure — the gates inspect already-collected cryptographic artifacts).

## 9. Assumptions

1. The Live Provenance PoC primitive (commit `e5c7a39`, status ESTABLISHED) remains operational at ATE v0.3 execution time.
2. The ATE v0.2.1 binding chain and nonce-registry semantics (commit `93e14fa`, status ESTABLISHED) remain operational.
3. The TGE v0.2.1 conceptual COA acceptance model is the canonical reference for what COA acceptance evidence means.
4. The Stage C v0.2.2 GEL (SHA-256 `dfcf2514...`) is the canonical executed-action signer.
5. Fixture keys `K_IDENTITY`, `K_TGE`, `K_AUTHORITY`, `K_GEL`, `K_PIPELINE` are stable and remain the cryptographic authorities for the established primitives.
6. New fixture keys `K_VA`, `K_BEHAVIORAL`, `K_TRUST_DECISION` are added in ATE v0.3 with stable identifiers.
7. The PoC implementation target (if executed) uses the same fixture-key pattern as ATE v0.2.1 — fixture keys are NOT production keys; no PKI, hardware root, or production key custody is claimed.
8. The trust-decision function is deterministic given the same inputs; nonces and operator freshness challenges are the only non-deterministic inputs.

## 10. Non-claims (explicit)

ATE v0.3 does **NOT** prove:

1. **General agent trustworthiness.** ATE v0.3 trusts the bound evidence, not the agent.
2. **Behavioral safety under novel conditions.** Behavioral evidence is a digest of a prior fixed battery; not a generalization guarantee.
3. **Value Architecture effectiveness.** The PoC uses a minimal machine-verifiable compatibility check, not a moral/ethical alignment claim.
4. **Production replay resistance.** The nonce registry is in-process for the PoC; production-grade distributed atomicity is not claimed.
5. **Hardware-backed identity.** No TPM / enclave / remote attestation. The threat model excludes those (Live Provenance PoC frozen threat model).
6. **Multi-agent federation.** Single agent, single session.
7. **Resistance to root/administrator compromise, arbitrary code execution, malicious binary, debugger access.** Out of scope per established threat model.
8. **That all four `BehavioralEvidence` evaluations generalize.** Battery_pass captures ONE battery result.
9. **General authorization semantics.** The PoC addresses a single requested action at a single moment in time.
10. **A solution to general moral alignment.** Out of scope per directive.

## 11. Proposed success criteria (for the future execution phase)

The eventual execution phase (NOT in this design-only phase) would be considered passing if and only if:

1. **Case A (valid grant):** All 8 gates PASS, `verdict = TRUST_GRANTED`, `reason = GX_OK`, decision signed by K_TRUST_DECISION, `SignedGovernedAction` emitted with the decision_id bound, nonce consumed.
2. **Case B (scope mismatch):** Gate G5 fails with the specific scope reason; verdict `TRUST_DENIED`; nonce remains `UNSEEN`; no `SignedGovernedAction` emitted.
3. **Case C (binding break):** At least one of G1/G2/G7 fails with the specific binding reason; verdict `TRUST_DENIED`; nonce remains `UNSEEN`; no `SignedGovernedAction` emitted.

The execution phase would additionally verify:
- All prior ATE v0.2.1 cases still pass (no regression).
- Deterministic re-execution of `trust_decide(envelope, ...)` reproduces the verdict byte-for-byte.
- The decision_signature_b64 is reproducible (same inputs → same signature).

## 12. Unresolved architectural questions requiring PI judgment

1. **Behavioral evidence sourcing.** The PI directive says "Reuse existing evidence where technically appropriate. Do not create a large behavioral evaluation suite." Is the behavioral evidence acceptable as (a) a signed digest of an existing Stage C v0.1 / v0.2 fixed-battery result (per existing artifact `architecture/experimental/stage-c-behavioral/STAGE-C-DESIGN-v0.1.md`), or (b) a placeholder digest with a fixed pass-status, or (c) something else?

2. **Value Architecture policy content.** The PI directive says "the minimum machine-verifiable representation of Value Architecture compatibility needed for this PoC." Is a 3-rule fixed policy (R1 operation allowlist, R2 data-class denylist, R3 harm-potential threshold) sufficient, or should the design add more dimensions (e.g., temporal scope, agent-class scope)?

3. **Capability token issuance path.** Is the `CapabilityToken` issued by `K_AUTHORITY` as a fixture in this PoC (same as ATE v0.2.1), or should ATE v0.3 introduce a separate issuance path bound to the Live Provenance session?

4. **`K_TRUST_DECISION` key custody.** Where does `K_TRUST_DECISION` live? Inside the same Hermes runtime that produced the Live Provenance evidence (so the trust decision is part of the bound agent), or as a separate authority fixture (so the trust decision is independent of the agent's runtime)?

5. **Behavioral evidence TTL.** How long is behavioral evidence "fresh"? The design defaults to "until `evaluation_window.end_utc + behavioral_evidence_ttl`" but the TTL value itself is a policy parameter.

6. **Multiple actions per envelope.** ATE v0.3's `envelope_nonce` is single-use. Is that per-envelope (one action per envelope) or per-set-of-artifacts (one envelope could authorize a small N>1 sequence of actions)? The current design is one-action-per-envelope; the alternative is recorded for PI direction.

7. **VA policy versioning.** When a `ValueArchitecturePolicy` is updated, do existing `CapabilityToken` instances remain valid, or do they need re-issuance against the new policy?

These questions are explicitly reserved for PI direction and are not resolved in this design.

## 13. STOP (design only)

This artifact is the ATE v0.3 design. No implementation, no experiment, no model calls, no evaluators.

Awaiting PI review and direction on the seven unresolved questions in §12.

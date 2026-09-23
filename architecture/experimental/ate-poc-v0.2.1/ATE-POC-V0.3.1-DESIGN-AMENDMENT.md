# Agent Trust Envelope v0.3.1 — DESIGN AMENDMENT

**Status:** DESIGN ONLY — amends ATE v0.3 per PI rulings 1–7.
**Author:** Hermes (research-manager-mandate-2026-09-15)
**Date:** 2026-09-15
**Authority:** Frank Ventura (PI), per directive of 2026-09-15 (ATE v0.3 design direction ACCEPTED; v0.3.1 amendment authorized).
**Predecessor (preserved byte-identically):** `architecture/experimental/ate-poc-v0.2.1/ATE-POC-V0.3-DESIGN.md` (commit `97cf803`).

## 0. Provenance and Predecessors

ATE v0.3.1 is an **amendment** to ATE v0.3, not a redesign. All established primitives are reused without modification:

| Predecessor | Status | Reuse |
| -- | -- | -- |
| ATE v0.3 design (commit `97cf803`) | DESIGN ONLY | Amended by this document |
| Live Provenance PoC v0.2.1 (commit `e5c7a39`) | LIVE_PROVENANCE_POC_PRIMITIVE_ESTABLISHED | REUSE byte-identically |
| Ephemeral Session Identity primitive (commit `21b23de`) | ESTABLISHED | REUSE byte-identically |
| TGE v0.2.1 (Concept of Agency) | DESIGN (canonical reference) | REUSE conceptual model |
| ATE-PoC v0.2.1 (commit `93e14fa`) | DETERMINISTIC BINDING CHAIN + REPLAY SEPARATION ESTABLISHED | REUSE binding chain + nonce registry |
| Stage C v0.2.2 GEL (SHA-256 `dfcf2514...`) | FROZEN | REUSE byte-identically |
| Stage C v0.1 evidence baseline (SHA-256 `36b5c96f...`) | FROZEN (design + 3 propositions + STOP INSUFFICIENT_BEHAVIORAL_VARIANCE at C2) | REUSE as the behavioral evidence source (per PI RULING 1) |

**Predecessors preserved byte-identically.** This amendment is a new design document; no existing design or implementation file is modified.

## 1. PI RULING 1 — Behavioral evidence

### 1.1 Specification

The behavioral evidence in ATE v0.3.1 is a `BehavioralEvidenceReceipt` (renamed from v0.3's generic `BehavioralEvidence` to make its role as a *signed receipt over pre-existing evidence* explicit).

```json
{
  "schema_id": "ATE-V3.1-BEHAVIORAL-EVIDENCE-RECEIPT/0.1",
  "receipt_id": "<sha256-derived deterministic id>",
  "source_identifier": "<e.g. 'STAGE-C-V0.1-FIXED-BATTERY'>",
  "stage_c_version": "0.1",
  "evidence_digest": "<sha256(canonicalize(Stage C v0.1 frozen result))>",
  "evaluation_result_status": "<one of 'PASS_BEHAVIORAL' | 'FAIL_BEHAVIORAL' | 'INCONCLUSIVE_STOPPED'>",
  "issued_at_utc": 0.0,
  "expires_at_utc": 0.0,
  "authority_fingerprint": "<K_BEHAVIORAL public-key sha256>",
  "authority_signature_b64": "<base64>"
}
```

### 1.2 PI-mandated fields (RULING 1 enumerated)

| Field | Source | Required |
| -- | -- | -- |
| evidence/source identifier | `source_identifier = "STAGE-C-V0.1-FIXED-BATTERY"` | YES |
| Stage C version | `stage_c_version = "0.1"` | YES |
| evidence digest | `evidence_digest = sha256(canonicalize(stage_c_v0_1_frozen_result))` | YES |
| evaluation/result status required by ATE | `evaluation_result_status = "PASS_BEHAVIORAL"` (per Stage C v0.1 C1 = PASS) | YES |
| issuance timestamp | `issued_at_utc` | YES |
| expiration timestamp | `expires_at_utc = issued_at_utc + 86400` (24h, per PI RULING 5) | YES |
| authority identity/key reference | `authority_fingerprint` + `authority_signature_b64` (K_BEHAVIORAL) | YES |

### 1.3 Constraints (RULING 1)

- **No placeholder digest.** `evidence_digest` is the SHA-256 of the canonicalized Stage C v0.1 frozen result.
- **No new behavioral test suite.** This PoC reuses the Stage C v0.1 frozen result (commit b8cc8da, stage-c synthesis closeout). C1 PASSED; C2 STOPPED at INSUFFICIENT_BEHAVIORAL_VARIANCE; C3 NOT_EXECUTED. The receipt is signed by `K_BEHAVIORAL` over the digest of the C1 result plus a PASS_BEHAVIORAL evaluation_result_status for ATE purposes.
- **TTL governs authority assertion freshness, not evidence creation date.** Per PI RULING 1 explicit clarification: "Its TTL governs the freshness of the authority's assertion that the evidence remains acceptable, not the creation date of the underlying Stage C evidence."
- **Expired evidence produces `TRUST_DENIED`.** See G4 in §5 pseudocode and `GX_BEHAVIORAL_EXPIRED` reason code in §6.

### 1.4 What is rejected (no expansion)

- No new behavioral metrics.
- No new authority identity beyond `K_BEHAVIORAL`.
- No refresh automation. The receipt is issued once; if expired, a new receipt requires re-issuance by `K_BEHAVIORAL` (out of PoC scope to implement refresh).
- No composition with non-Stage-C evidence sources.

## 2. PI RULING 2 — Value Architecture policy

### 2.1 Specification (three-rule minimum, retained from v0.3)

```json
{
  "schema_id": "ATE-V3.1-VA-POLICY/0.1",
  "policy_id": "<e.g. 'VA-CORE-RESTRICTIVE'>",
  "policy_version": "<e.g. '1.0.0'>",
  "policy_digest": "<sha256(canonicalize(policy_contents))>",
  "policy_contents": {
    "rules": [
      {"rule_id": "R1", "subject": "operation", "operator": "in", "values": ["READ", "WRITE_SCOPED", "EXECUTE_SCOPED"], "applies_to_targets": ["filesystem:/home/agent/", "network:egress-allowlisted"]},
      {"rule_id": "R2", "subject": "data_class", "operator": "neq", "values": ["PI", "PHI", "BEHAVIORAL_PRIVACY"]},
      {"rule_id": "R3", "subject": "harm_potential", "operator": "lte", "values": [<numeric>]}
    ],
    "default_action": "DENY"
  },
  "issued_by": "<named authority>",
  "issued_at_utc": 0.0,
  "policy_signature_b64": "<base64 over canonical(policy_id + policy_version + policy_digest + policy_contents)>"
}
```

### 2.2 PI-mandated fields (RULING 2 enumerated)

| Field | Required |
| -- | -- |
| policy_id | YES |
| policy_version | YES |
| canonical policy_digest | YES (`sha256(canonicalize(policy_contents))`) |
| signed policy contents | YES (`policy_signature_b64` covers all of policy_id + policy_version + policy_digest + policy_contents) |
| default-deny semantics | YES (`policy_contents.default_action = "DENY"`) |

### 2.3 Constraints (RULING 2)

- **No agent-class scope added in this PoC.** v0.3.1 retains only the 3 rules from v0.3 (operation allowlist, data-class denylist, harm-potential threshold).
- **No duplication of temporal authorization semantics inside VA.** Freshness/expiration lives on `BehavioralEvidenceReceipt`, `CapabilityToken`, and `AcceptanceReceipt`, NOT inside `ValueArchitecturePolicy`. VA policy does not carry a `valid_until_utc`.
- **ATE compares exact `policy_id + policy_version + policy_digest`.** Per PI RULING 7 (see §7): if any of the three changes, existing `CapabilityToken` instances are not valid under the new policy; re-issuance required.
- **Default-deny.** Any rule failure → `TRUST_DENIED` with the rule_id reported in the gate result detail (informational); the top-level reason code is `GX_VA_POLICY_INCOMPATIBLE`.

## 3. PI RULING 3 — CapabilityToken issuance

### 3.1 Issuance path

`CapabilityToken` is **issued by the existing ATE v0.2.1 `K_AUTHORITY` fixture** (no new issuance architecture introduced). The token's signed region is extended in v0.3.1 to bind to:

- Intended Live Provenance session identity/context (`session_id`, `public_key_sha256`)
- Permitted operation (`operation_scope`)
- Permitted target (`target_scope`)
- Explicit constraints (`constraints.excluded_targets`, `constraints.max_per_call`, `constraints.max_total`)
- Freshness/expiration (`valid_from_utc`, `valid_until_utc`)
- VA policy identity/version/digest (`va_policy_id`, `va_policy_version`, `va_policy_digest`)
- Relevant COA acceptance identity (`bound_receipt_fingerprint`)
- Nonce/replay state (`envelope_nonce`)

### 3.2 Specification

```json
{
  "schema_id": "ATE-V3.1-CAPABILITY/0.1",
  "capability_id": "<deterministic>",
  "session_id": "<matches Live Provenance session>",
  "public_key_sha256": "<matches Ephemeral Session Identity fingerprint>",
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
  "va_policy_id": "<e.g. 'VA-CORE-RESTRICTIVE'>",
  "va_policy_version": "<e.g. '1.0.0'>",
  "va_policy_digest": "<sha256 of canonicalize(policy_contents)>",
  "envelope_nonce": "<single-use>",
  "issued_at_utc": 0.0,
  "authority_fingerprint": "<K_AUTHORITY fingerprint>",
  "authority_signature_b64": "<base64>"
}
```

### 3.3 Constraint (RULING 3)

**Fail-closed if presented from a different Live Provenance session than the one for which it was issued.** See G5 in §5 pseudocode: `GX_CAPABILITY_SESSION_MISMATCH` when `capability.public_key_sha256 != session_ctx.public_key_sha256`. Hashed binding is mandatory; the token is single-session.

## 4. PI RULING 4 — Trust-decision key custody

### 4.1 K_TRUST_DECISION authority boundary

`K_TRUST_DECISION` is a **separate authority fixture outside the participant agent's authority boundary**. The participant agent does NOT hold the private key. Concretely:

- The participant agent (the Hermes runtime that produced the Live Provenance evidence, TGE acceptance, etc.) **cannot self-certify TRUST_GRANTED**.
- The trust-decision authority (a separate fixture, with its own private key) consumes the evidence, runs the deterministic gate function, and signs the resulting `TrustDecision`.
- If the participant attempts to construct a `TrustDecision` directly (e.g., by replaying a previously granted one or forging a signature), G6's `GX_ACTION_SIGNATURE_INVALID` (or the G7 envelope-binding-hash check, or G8 nonce-state check) catches it.

### 4.2 Production key-management out of scope

Per RULING 4: "Do not design production key-management infrastructure in v0.3.1." This PoC treats `K_TRUST_DECISION` as a fixture (same pattern as `K_IDENTITY`, `K_TGE`, `K_AUTHORITY`, `K_GEL`, `K_PIPELINE`). Production custody, rotation, HSM integration, and PKI are explicitly out of scope.

### 4.3 Authority relationship

```
participant agent (Live Provenance + COA evidence)
        |
        | submits evidence
        v
independent trust-decision authority (K_TRUST_DECISION)
        |
        | verifies evidence + runs gates + signs verdict
        v
TrustDecision {verdict, reason_code, gate_results, decision_signature_b64}
        |
        | (only if TRUST_GRANTED)
        v
one authorized governed action consumes envelope_nonce
```

The participant supplies evidence. The independent authority verifies and signs. This separation is enforced at two layers: (a) the participant cannot produce a valid `decision_signature_b64` without `K_TRUST_DECISION`'s private key; (b) the `TrustDecision.verdict` field is included in the signed region, so an attacker cannot substitute a `GRANTED` for a `DENIED` without invalidating the signature.

## 5. PI RULING 5 — Behavioral evidence TTL

**24 hours.** `BehavioralEvidenceReceipt.expires_at_utc = issued_at_utc + 86400`. If `now_utc > expires_at_utc`, the trust-decision produces `TRUST_DENIED` with reason `GX_BEHAVIORAL_EXPIRED` (G4). No refresh automation; a new receipt requires re-issuance by `K_BEHAVIORAL`.

## 6. PI RULING 6 — Envelope consumption

**One governed action per envelope.** The `envelope_nonce` is single-use:

- First valid `AUTHORIZE_EXECUTION` consumes the nonce (`UNSEEN → AUTHORIZED → CONSUMED`).
- Any subsequent `AUTHORIZE_EXECUTION` against the same envelope fails closed with `GX_NONCE_NOT_UNSEEN` (G8) or `GX_NONCE_PREVIOUSLY_CONSUMED` (G8/9 — see §10).
- `VERIFY_ENVELOPE` operations against previously consumed envelopes (historical re-verification) MAY succeed and report the consumed state, but `AUTHORIZE_EXECUTION` may not.

No N-action envelopes in v0.3.1. If the agent requires multiple actions, it must produce multiple envelopes, each with its own nonce, its own `CapabilityToken`, its own `TrustDecision`. Each trust-decision cycle is single-action.

## 7. PI RULING 7 — VA policy updates

CapabilityTokens and TrustDecisions are bound to **exact `policy_id + policy_version + policy_digest`** (the triple). If any of the three changes:

- Existing `CapabilityToken` instances are NOT valid under the new policy. The token's signed region carries `va_policy_id`, `va_policy_version`, `va_policy_digest` — at G3 the trust-decision compares these against the `ValueArchitecturePolicy` actually presented; a mismatch produces `GX_VA_POLICY_INCOMPATIBLE` with detail `va_policy_triple_mismatch`.
- Existing `TrustDecision` instances are NOT valid for the new policy. Each trust-decision cycle re-evaluates against the current `ValueArchitecturePolicy`.
- **Re-issuance is required.** New `CapabilityToken` instances must be issued by `K_AUTHORITY` with the new policy triple.
- No grandfathering. No policy migration mechanism. No downgrade. No equivalence map.

This makes a VA policy update an atomic operational event: existing in-flight envelopes under the old policy continue to be valid (their decisions are already signed); new envelopes must be issued against the new policy.

## 8. Updated data structures

The data structures from ATE v0.3 §3 are updated as follows. Changes marked with **(v0.3.1 delta)**.

### 8.1 `BehavioralEvidenceReceipt` (REPLACES v0.3 `BehavioralEvidence`)

Per §1 above. Signed by `K_BEHAVIORAL`. `source_identifier` and `stage_c_version` make it explicit that this is a receipt over pre-existing Stage C v0.1 evidence.

### 8.2 `ValueArchitecturePolicy` (REVISED with PI-mandated fields)

Per §2 above. `policy_id`, `policy_version`, `policy_digest`, `policy_contents`, signed by `K_VA`. Default-deny.

### 8.3 `CapabilityToken` (EXTENDED)

Per §3 above. Adds `va_policy_id`, `va_policy_version`, `va_policy_digest`, `envelope_nonce` to the signed region. Issued by `K_AUTHORITY` (no new issuer).

### 8.4 `AgentTrustEnvelope` (REVISED)

```json
{
  "schema_id": "ATE-V3.1-ENVELOPE/0.1",
  "envelope_id": "<deterministic>",
  "envelope_nonce": "<single-use; one envelope = one governed action>",
  "issued_at_utc": 0.0,
  "envelope_binding_hash": "<canonical fingerprint over envelope.contents>",
  "contents": {
    "identity_attestation": "<IdentityAttestation (K_IDENTITY)>",
    "session_context": "<SessionContext incl. Live Provenance public_key_sha256>",
    "live_provenance_acceptance": "<SessionAcceptance (event_source=HERMES_MODEL_RESPONSE)>",
    "live_provenance_action": "<SignedCandidateAction (event_source=HERMES_MODEL_RESPONSE)>",
    "coa_acceptance_receipt": "<AcceptanceReceipt (K_TGE)>",
    "va_policy": "<ValueArchitecturePolicy (K_VA)>",
    "behavioral_evidence_receipt": "<BehavioralEvidenceReceipt (K_BEHAVIORAL)>",
    "capability_token": "<CapabilityToken (K_AUTHORITY)>",
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

The envelope does NOT include `SignedExecutedAction` or `TrustDecision` — those are outputs.

### 8.5 `TrustDecision` (REVISED, signed by `K_TRUST_DECISION`)

```json
{
  "schema_id": "ATE-V3.1-TRUST-DECISION/0.1",
  "decision_id": "<deterministic>",
  "operation_mode": "TRUST_DECIDE",
  "envelope_fingerprint": "<matches envelope_binding_hash>",
  "envelope_nonce": "<mirrored from envelope; covered in signed region>",
  "verdict": "TRUST_GRANTED" | "TRUST_DENIED",
  "reason_code": "<one of the codes in §10>",
  "gate_results": [
    {"gate": "G1_RUNTIME_BINDING", "result": "PASS" | "FAIL", "detail": "..."},
    ...
  ],
  "decided_at_utc": 0.0,
  "trust_decision_authority_fingerprint": "<K_TRUST_DECISION fingerprint>",
  "decision_signature_b64": "<base64; signed by K_TRUST_DECISION>"
}
```

The signed region covers `verdict`, `reason_code`, `envelope_fingerprint`, `envelope_nonce`, `gate_results`, `decided_at_utc`. An attacker who alters `verdict` cannot produce a valid signature without `K_TRUST_DECISION`'s private key.

### 8.6 `SignedGovernedAction` (OUTPUT, after GRANTED)

Same envelope shape as `SignedCandidateAction` from Live Provenance v0.2.1, but with `trust_decision_id` and `envelope_nonce` added to the signed region. Signed by `K_IDENTITY` (the live session's ephemeral key). Consumed atomically with the nonce transition.

## 9. Updated trust-decision pseudocode

The trust-decision function is now performed by the **independent trust-decision authority**, not the participant agent.

```
def trust_decide(envelope: AgentTrustEnvelope, *,
                 identity_att, session_ctx, sa, sca,
                 receipt, va_policy, behavioral_receipt, capability,
                 operator_freshness_challenge,
                 now_utc: float,
                 nonce_registry: NonceRegistry) -> TrustDecision:

    # The participant supplied these as a Bundle; the trust-decision
    # authority verifies each independently.

    gate_results = []

    # G1: runtime binding (Live Provenance — already established)
    if session_ctx.public_key_sha256 != sa.public_key_sha256: DENY(GX_RUNTIME_BINDING, "sa.pubkey != session.pubkey")
    elif sa.public_key_sha256 != sca.public_key_sha256: DENY(GX_RUNTIME_BINDING, "sca.pubkey != sa.pubkey")
    elif sa.public_key_sha256 != identity_att.public_key_sha256: DENY(GX_RUNTIME_BINDING, "identity.pubkey != sa.pubkey")
    elif sa.freshness_challenge != envelope.contents.operator_freshness_challenge: DENY(GX_FRESHNESS_MISMATCH)
    elif sa.event_source != "HERMES_MODEL_RESPONSE": DENY(GX_EVENT_SOURCE_NOT_LIFECYCLE, "sa.event_source")
    elif sca.event_source != "HERMES_MODEL_RESPONSE": DENY(GX_EVENT_SOURCE_NOT_LIFECYCLE, "sca.event_source")
    elif sca.session_acceptance_fingerprint != sa.session_acceptance_fingerprint: DENY(GX_ACCEPTANCE_FINGERPRINT_CHAIN)
    gate_results.append(("G1_RUNTIME_BINDING", "PASS"))

    # G2: COA acceptance binding
    if not verify_signature(K_TGE, receipt): DENY(GX_COA_SIGNATURE_INVALID)
    elif receipt.session_id != session_ctx.session_id: DENY(GX_COA_SESSION_MISMATCH)
    elif receipt.public_key_sha256 != session_ctx.public_key_sha256: DENY(GX_COA_PUBLIC_KEY_MISMATCH)
    elif receipt.freshness_challenge != operator_freshness_challenge: DENY(GX_COA_FRESHNESS_MISMATCH)
    elif now_utc > receipt.expires_at_utc: DENY(GX_COA_EXPIRED)
    elif receipt.session_acceptance_fingerprint != sa.session_acceptance_fingerprint: DENY(GX_COA_NOT_BOUND_TO_LIVE_PROVENANCE)
    gate_results.append(("G2_COA_BINDING", "PASS"))

    # G3: VA policy compatibility (exact triple match per PI RULING 7)
    if not verify_signature(K_VA, va_policy): DENY(GX_VA_POLICY_SIGNATURE_INVALID)
    elif va_policy.policy_id != capability.va_policy_id: DENY(GX_VA_POLICY_TRIPLE_MISMATCH, "policy_id")
    elif va_policy.policy_version != capability.va_policy_version: DENY(GX_VA_POLICY_TRIPLE_MISMATCH, "policy_version")
    elif va_policy.policy_digest != capability.va_policy_digest: DENY(GX_VA_POLICY_TRIPLE_MISMATCH, "policy_digest")
    elif not va_compatible(va_policy, envelope.contents.requested_action): DENY(GX_VA_POLICY_INCOMPATIBLE, rule_id_detail)
    gate_results.append(("G3_VA_COMPATIBILITY", "PASS"))

    # G4: behavioral evidence (24h TTL per PI RULING 5)
    if not verify_signature(K_BEHAVIORAL, behavioral_receipt): DENY(GX_BEHAVIORAL_SIGNATURE_INVALID)
    elif behavioral_receipt.evaluation_result_status != "PASS_BEHAVIORAL": DENY(GX_BEHAVIORAL_BATTERY_FAILED, f"status={...}")
    elif behavioral_receipt.agent_identity_fingerprint != identity_att.public_key_sha256: DENY(GX_BEHAVIORAL_AGENT_MISMATCH)
    elif now_utc > behavioral_receipt.expires_at_utc: DENY(GX_BEHAVIORAL_EXPIRED)
    gate_results.append(("G4_BEHAVIORAL_EVIDENCE", "PASS"))

    # G5: capability scope + binding (PI RULING 3)
    if not verify_signature(K_AUTHORITY, capability): DENY(GX_CAPABILITY_SIGNATURE_INVALID)
    elif capability.public_key_sha256 != session_ctx.public_key_sha256: DENY(GX_CAPABILITY_SESSION_MISMATCH)
    elif capability.bound_receipt_fingerprint != receipt.fingerprint: DENY(GX_CAPABILITY_NOT_BOUND_TO_RECEIPT)
    elif envelope.contents.requested_action.operation not in capability.operation_scope: DENY(GX_OPERATION_OUT_OF_SCOPE)
    elif envelope.contents.requested_action.target not in capability.target_scope: DENY(GX_TARGET_OUT_OF_SCOPE)
    elif envelope.contents.requested_action.target in capability.constraints.excluded_targets: DENY(GX_TARGET_EXCLUDED)
    elif not (capability.valid_from_utc <= now_utc <= capability.valid_until_utc): DENY(GX_CAPABILITY_EXPIRED_OR_NOT_YET_VALID)
    gate_results.append(("G5_CAPABILITY_SCOPE", "PASS"))

    # G6: live-provenance action chain + signature
    if sca.public_key_sha256 != session_ctx.public_key_sha256: DENY(GX_ACTION_RUNTIME_MISMATCH)
    elif sca.freshness_challenge != operator_freshness_challenge: DENY(GX_ACTION_FRESHNESS_MISMATCH)
    elif sca.session_acceptance_fingerprint != sa.session_acceptance_fingerprint: DENY(GX_ACTION_ACCEPTANCE_CHAIN_BROKEN)
    elif not verify_signature(session_ctx.public_key_b64, sca): DENY(GX_ACTION_SIGNATURE_INVALID)
    gate_results.append(("G6_LIVE_PROVENANCE_ACTION_CHAIN", "PASS"))

    # G7: envelope binding-hash
    if envelope.envelope_binding_hash != fingerprint_canonical(envelope.contents): DENY(GX_ENVELOPE_BINDING_HASH_MISMATCH)
    gate_results.append(("G7_ENVELOPE_BINDING", "PASS"))

    # G8: nonce state (single-use per PI RULING 6)
    state = nonce_registry.lookup(envelope.envelope_nonce)
    if state == "AUTHORIZED": DENY(GX_NONCE_PREVIOUSLY_AUTHORIZED)
    elif state == "CONSUMED": DENY(GX_NONCE_PREVIOUSLY_CONSUMED)
    elif state != "UNSEEN": DENY(GX_NONCE_NOT_UNSEEN, f"state={state}")
    gate_results.append(("G8_NONCE_STATE", "PASS"))

    return TrustDecision(verdict=TRUST_GRANTED, reason_code=GX_OK, gate_results=gate_results, ...)
```

After `TRUST_GRANTED`, the participant (or a downstream executor) calls `authorize_governed_action(envelope, trust_decision)` which atomically transitions the nonce and emits `SignedGovernedAction`. The next attempt at `AUTHORIZE_EXECUTION` for the same envelope fails at G8.

## 10. Updated reason codes

The v0.3 reason-code table is extended with the v0.3.1 amendments:

| Code | Gate | Meaning |
| -- | -- | -- |
| `GX_OK` | — | All eight gates PASS; verdict `TRUST_GRANTED` |
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
| `GX_VA_POLICY_TRIPLE_MISMATCH` | G3 **(v0.3.1 new)** | capability.(policy_id, policy_version, policy_digest) != policy.(...) |
| `GX_VA_POLICY_INCOMPATIBLE` | G3 | requested action violates at least one VA rule |
| `GX_BEHAVIORAL_SIGNATURE_INVALID` | G4 | K_BEHAVIORAL signature fails |
| `GX_BEHAVIORAL_BATTERY_FAILED` | G4 | evaluation_result_status != "PASS_BEHAVIORAL" |
| `GX_BEHAVIORAL_AGENT_MISMATCH` | G4 | behavioral receipt binds to a different agent identity |
| `GX_BEHAVIORAL_EXPIRED` | G4 | now_utc > BehavioralEvidenceReceipt.expires_at_utc (24h TTL per PI RULING 5) |
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
| `GX_NONCE_NOT_UNSEEN` | G8 **(v0.3.1)** | generic non-UNSEEN state |
| `GX_NONCE_PREVIOUSLY_AUTHORIZED` | G8 **(v0.3.1 new)** | nonce was AUTHORIZED; first AUTHORIZE has begun but not yet reached CONSUMED |
| `GX_NONCE_PREVIOUSLY_CONSUMED` | G8 **(v0.3.1 new)** | nonce was CONSUMED by a prior successful action |

## 11. Binding relationships among the seven artifacts

```
Live Provenance session_id
   |
   +-- binds to -- SessionContext.public_key_sha256
   |                   |
   |                   +-- binds to -- SessionAcceptance.public_key_sha256
   |                   |                   |
   |                   |                   +-- binds to -- SignedCandidateAction.public_key_sha256
   |                   |                   |                   |
   |                   |                   |                   +-- binds to -- SignedGovernedAction.public_key_sha256
   |                   |                   |
   |                   |                   +-- binds to -- AcceptanceReceipt.public_key_sha256
   |                   |                                       (COA acceptance)
   |                   |                                       |
   |                   |                                       +-- binds to -- CapabilityToken.bound_receipt_fingerprint
   |                   |
   |                   +-- binds to -- CapabilityToken.public_key_sha256 (PI RULING 3)
   |
   +-- binds to -- CapabilityToken.session_id
   |
   +-- binds to -- CapabilityToken.envelope_nonce
   |
   +-- binds to -- OperatorFreshnessChallenge
   |                   |
   |                   +-- binds to -- SessionAcceptance.freshness_challenge
   |                   +-- binds to -- SignedCandidateAction.freshness_challenge
   |                   +-- binds to -- AcceptanceReceipt.freshness_challenge
   |
   +-- binds to -- TrustDecision.envelope_fingerprint (== envelope_binding_hash)
                       |
                       +-- signed by K_TRUST_DECISION (PI RULING 4)

VA Policy (policy_id, policy_version, policy_digest)
   |
   +-- binds to -- CapabilityToken.(va_policy_id, va_policy_version, va_policy_digest)  (PI RULING 7)

BehavioralEvidenceReceipt
   |
   +-- evidence_digest == sha256(canonicalize(Stage C v0.1 frozen result))
   |
   +-- expires_at_utc == issued_at_utc + 86400  (PI RULING 5)
   |
   +-- agent_identity_fingerprint == IdentityAttestation.public_key_sha256
   |
   +-- signed by K_BEHAVIORAL

CapabilityToken
   |
   +-- session_id == Live Provenance session
   +-- public_key_sha256 == Live Provenance public-key fingerprint
   +-- bound_receipt_fingerprint == AcceptanceReceipt.fingerprint
   +-- (va_policy_id, va_policy_version, va_policy_digest) == ValueArchitecturePolicy.(...)
   +-- envelope_nonce == AgentTrustEnvelope.envelope_nonce  (single-use)
   +-- signed by K_AUTHORITY (no new issuer per PI RULING 3)

TrustDecision
   |
   +-- envelope_fingerprint == AgentTrustEnvelope.envelope_binding_hash
   +-- envelope_nonce == AgentTrustEnvelope.envelope_nonce  (consumed atomically)
   +-- verdict, reason_code, gate_results in signed region
   +-- signed by K_TRUST_DECISION  (independent authority per PI RULING 4)
```

The seven artifacts form a directed acyclic graph rooted at `Live Provenance session_id + public_key_sha256 + operator_freshness_challenge`. Removing any single binding breaks the corresponding gate.

## 12. Three PoC cases (UNCHANGED — case count not expanded per directive)

### Case A: valid evidence + permitted action → TRUST_GRANTED

- Live Provenance two-turn session produces `SessionAcceptance` and `SignedCandidateAction` with `event_source=HERMES_MODEL_RESPONSE`.
- TGE `AcceptanceReceipt` correctly signed, fresh, bound to same session, chains to SessionAcceptance fingerprint.
- `ValueArchitecturePolicy` permits requested operation/target/data class/harm potential; `policy_id + policy_version + policy_digest` triple matches `CapabilityToken` triple.
- `BehavioralEvidenceReceipt`: `evaluation_result_status = "PASS_BEHAVIORAL"`, `evidence_digest = sha256(stage_c_v0_1_frozen_result)`, `expires_at_utc > now_utc` (within 24h of issuance).
- `CapabilityToken`: signed by `K_AUTHORITY`, bound to session + receipt + VA triple, operation and target in scope, target not excluded, within validity window.
- `envelope_binding_hash` matches canonical fingerprint of contents.
- `envelope_nonce` is `UNSEEN` in the registry.

**Expected verdict:** `TRUST_GRANTED`, reason `GX_OK`, all 8 gates PASS, decision signed by `K_TRUST_DECISION`.

**Downstream:** one `SignedGovernedAction` emitted with `trust_decision_id` bound, `envelope_nonce` consumed atomically (`UNSEEN → AUTHORIZED → CONSUMED`).

### Case B: valid identity/governance but action outside authorization scope → TRUST_DENIED

- All runtime/COA/VA/behavioral evidence passes.
- `CapabilityToken` is otherwise valid, but the requested operation is NOT in `capability.operation_scope`, OR the target is NOT in `capability.target_scope`, OR the target IS in `capability.constraints.excluded_targets`.

**Expected verdict:** `TRUST_DENIED`, reason `GX_OPERATION_OUT_OF_SCOPE` (or `GX_TARGET_OUT_OF_SCOPE` / `GX_TARGET_EXCLUDED`), gates G1-G4 PASS, G5 FAIL. The non-scope gates (G6, G7, G8) are not reached because G5 fail-closed stops evaluation.

**Downstream:** No `SignedGovernedAction` emitted. `envelope_nonce` remains `UNSEEN` (no consumption).

### Case C: apparently valid authorization but broken/mismatched provenance or COA binding → TRUST_DENIED

- Capability is valid (signature, scope, expiration).
- VA compatibility check passes (including triple match).
- Behavioral evidence passes.
- But the binding between COA and Live Provenance is broken — e.g., `receipt.session_acceptance_fingerprint != sa.session_acceptance_fingerprint` (`GX_COA_NOT_BOUND_TO_LIVE_PROVENANCE`), OR `receipt.session_id != session_ctx.session_id` (`GX_COA_SESSION_MISMATCH`), OR `sa.event_source != HERMES_MODEL_RESPONSE` (`GX_EVENT_SOURCE_NOT_LIFECYCLE`), OR the envelope_binding_hash is recomputed and mismatches (`GX_ENVELOPE_BINDING_HASH_MISMATCH`).

**Expected verdict:** `TRUST_DENIED`, reason corresponding to the specific broken binding. Gates G1/G2/G7 (depending on which binding was broken) FAIL. Subsequent gates not reached.

**Downstream:** No `SignedGovernedAction` emitted. `envelope_nonce` remains `UNSEEN`.

## 13. STOP (design only)

This is the v0.3.1 design amendment. No implementation, no execution.

Awaiting PI direction to proceed to adversarial design review (§14) and possibly to the implementation/execution phase.

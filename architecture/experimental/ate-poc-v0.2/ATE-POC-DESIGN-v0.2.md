# Agent Trust Envelope — Integration PoC v0.2 (ARTIFACT BINDING)

**Status:** DESIGN ONLY — not implemented, not executed.
**Author:** Hermes (research-manager-mandate-2026-08-27)
**Predecessor:** `architecture/experimental/ate-poc-v0.1/ATE-POC-DESIGN-v0.1.md` (frozen at commit `6d39743ade499ea1e71bf7e528ccb91cbaaecfa8`).
**Frozen baseline:** ATE-PoC v0.1 — `PASS — DETERMINISTIC TRUST-PIPELINE INTEGRATION ESTABLISHED` (11/11 cases, 4/4 tamper detection, replay PASS).
**Material limitation accepted by PI:** v0.2 design must address the ATE-5c gap — candidate Action object is not independently integrity-bound; tampering was detected only because the modified operation fell outside the granted capability.

## 0. Purpose

Determine whether the ATE-PoC components can be cryptographically and structurally bound into **one verifiable execution chain**. The objective: a valid object from one trusted envelope must not be substitutable into another envelope, session, request, or decision without deterministic verification failure.

This is **not** a behavioral experiment. This is a deterministic integration test of binding primitives.

## 1. The v0.1 gap (recap)

In v0.1, the `candidate_action` dict is consumed by GEL but not bound to the rest of the trust chain. The Ed25519 signature in `IdentityAttestation` covers the runtime's public key + agent id + session id + fingerprint, but the `candidate_action` itself carries no signature. The `CapabilityToken` is signed by the authority, but its signature covers the token's structure (capability_id, agent_id, session_id, scope, validity window) — not the candidate_action.

This means: an attacker who can substitute the `candidate_action` between the runtime signing the identity and the pipeline receiving the action cannot be detected, unless the substituted action falls outside the granted capability. The v0.1 capability check catches *some* tampering but not all.

**v0.2 closes this gap.** Each artifact in the trust chain is hash-bound into a single `envelope_binding`, and a chain of signatures / hashes ensures substitution is detectable.

## 2. Binding model

### 2.1 The binding chain

```
    IdentityAttestation
         |
         | (signed by runtime; binds: agent_id, runtime_fingerprint, session_id, pubkey)
         |
         v
    SessionContext  (per-session state; binds: session_id, receipt_id, capability_id)
         |
         v
    AcceptanceReceipt
         |
         | (signed by TGE-style fixture key; binds: charter_sha256, session_id, gel_unlocks_to)
         |
         v
    CapabilityToken
         |
         | (signed by authority; binds: capability_id, agent_id, session_id, scope, validity)
         |
         v
    SignedCandidateAction
         |
         | (signed by runtime; binds: action_struct fields, session_id, envelope_nonce,
         |  capability_id, receipt_id, identity_fingerprint)
         |
         v
    GEL evaluation (uses SignedCandidateAction.action_struct)
         |
         v
    SignedExecutedAction
         |
         | (signed by GEL; binds: original_action_hash, executed_action_struct, rule_id)
         |
         v
    DecisionRecord
         |
         | (signed by pipeline; binds: all prior hashes, decision verdict, gate trace)
         |
         v
    evidence_chain_hash = SHA-256(canonicalize(DecisionRecord.audit_trail))
```

Each transition introduces a signature whose subject includes the previous artifact's hash. Substitution breaks the chain.

### 2.2 Canonical serialization

Per PI directive: *"Prefer a canonical serialization and hash/signature scheme that avoids ambiguous representations."*

**Frozen canonical serialization rule (v0.2):**

- Use **RFC 8785 JCS** (strict) with the v0.2.1-JCS-strict profile already in use (see `architecture/experimental/stage-c/implementation_v022/SCHEMA-ACTION-v0.2.2.md` §E.1).
- Object keys sorted by UTF-16 code unit order.
- No Unicode normalization (RFC 8785 preserves Unicode as-is).
- No whitespace, sorted arrays preserved, null vs omitted distinct.
- Numbers in canonical form.

**Cross-fixture determinism:** all signatures are computed over the canonicalized bytes of the artifact being signed.

### 2.3 What is signed, by which key, at what stage

| Stage | Object signed | Signing key | What is included in the signed region |
| -- | -- | -- | -- |
| 1 | IdentityAttestation | runtime (Ed25519) | schema_id, agent_id, runtime_fingerprint, session_id, issued_at_utc, public_key_b64 |
| 2 | SessionContext | runtime (Ed25519) | session_id, identity_fingerprint (= SHA-256 of canonicalized IdentityAttestation), receipt_id_predicate, capability_id_predicate, valid_from_utc, valid_until_utc |
| 3 | AcceptanceReceipt | TGE-fixture key (Ed25519) | schema_id, receipt_id, charter_sha256, session_id, identity_fingerprint, issued_at_utc, gel_unlocks_to |
| 4 | CapabilityToken | authority (Ed25519) | schema_id, capability_id, agent_id, session_id, identity_fingerprint, scope, valid_from_utc, valid_until_utc, issued_by |
| 5 | SignedCandidateAction | runtime (Ed25519) | action_struct (v0.2.2 fields), session_id, envelope_nonce, capability_id, receipt_id, identity_fingerprint, action_preimage_hash (= SHA-256 of canonicalized action_struct) |
| 6 | SignedExecutedAction | GEL-fixture key (Ed25519) | schema_id, original_action_hash (= SHA-256 of canonicalized SignedCandidateAction), executed_action_struct, rule_id, evaluated_at_utc |
| 7 | DecisionRecord | pipeline-fixture key (Ed25519) | schema_id, decision_id, envelope_binding_hash, identity_fingerprint, receipt_fingerprint, capability_fingerprint, action_fingerprint, executed_action_fingerprint, audit_trail, verdict, reason_code |

**`envelope_binding_hash`** = SHA-256 of canonicalized `Envelope` dict (which contains all five component artifacts).

### 2.4 Cross-binding via fingerprints

Every artifact's signature includes a *fingerprint* of the artifacts upstream of it. This is the structural substitute: an attacker cannot substitute one artifact without breaking every downstream signature.

The fingerprints are SHA-256 hashes over canonicalized bytes:

- `identity_fingerprint` = SHA-256(canonicalize(IdentityAttestation)) — 64 hex chars.
- `receipt_fingerprint` = SHA-256(canonicalize(AcceptanceReceipt)) — 64 hex chars.
- `capability_fingerprint` = SHA-256(canonicalize(CapabilityToken)) — 64 hex chars.
- `action_fingerprint` = SHA-256(canonicalize(SignedCandidateAction)) — 64 hex chars.
- `executed_action_fingerprint` = SHA-256(canonicalize(SignedExecutedAction)) — 64 hex chars.

Each downstream artifact includes the upstream fingerprint in its signed region.

### 2.5 Envelope structure

```python
@dataclass
class Envelope:
    schema_id: str   # "TGE-ATE-ENVELOPE-V2/0.1"
    envelope_id: str   # opaque hex 16
    issued_at_utc: int
    identity: dict   # IdentityAttestation
    session_context: dict   # SessionContext
    receipt: dict   # AcceptanceReceipt
    capability: dict   # CapabilityToken
    signed_candidate_action: dict   # SignedCandidateAction
```

The `envelope_binding_hash` is computed from this Envelope dict via canonicalize + SHA-256.

### 2.6 DecisionRecord structure

```python
@dataclass
class DecisionRecord:
    schema_id: str   # "TGE-ATE-DECISION-V2/0.1"
    decision_id: str   # opaque hex 16
    envelope_binding_hash: str   # SHA-256 of canonicalized Envelope
    identity_fingerprint: str
    receipt_fingerprint: str
    capability_fingerprint: str
    action_fingerprint: str
    executed_action_fingerprint: str
    audit_trail: list[dict]   # ordered list of gate decisions
    verdict: str   # ALLOW | BLOCK | REDIRECT | DENY_BEFORE_BINDING
    reason_code: str
    issued_at_utc: int
    decision_signature_b64: str   # Ed25519 over canonicalized(decision fields except signature)
```

### 2.7 How GEL input hash and executed-action hash enter the evidence record

- **GEL input hash:** SHA-256(canonicalize(SignedCandidateAction)) is `action_fingerprint`. This is recorded in DecisionRecord's `action_fingerprint` field. The DecisionRecord's signature covers this field.
- **GEL executed-action hash:** SHA-256(canonicalize(SignedExecutedAction)) is `executed_action_fingerprint`. Recorded in DecisionRecord's `executed_action_fingerprint`. The DecisionRecord's signature covers this field.

If an attacker mutates the executed action after GEL, `executed_action_fingerprint` would still hash the new bytes — but the *GEL-signed* hash inside `SignedExecutedAction.original_action_hash` (which hashes the original SignedCandidateAction) would no longer match the action_fingerprint, breaking the binding. Conversely, if an attacker mutates the candidate action, `action_fingerprint` would change but the DecisionRecord's signature would no longer verify.

### 2.8 Replay vs. legitimate reverification

A *legitimate* reverification is the same pipeline rerun on the same envelope + same fixtures + same current_time. The replay produces identical `evidence_chain_hash` (since canonicalize is deterministic and signatures are deterministic).

A *replay attack* is an attacker reusing a valid decision record in a different context. The replay differs from legitimate reverification because:

- The new context has different session_id, agent_id, capability_id, etc.
- The replayed DecisionRecord includes `envelope_binding_hash` which is bound to the original envelope.
- The new context's expected `envelope_binding_hash` differs from the replayed one's.
- Verification fails.

**Distinguishing marker:** the v0.2 DecisionRecord includes `envelope_binding_hash` in the signed region. A replay in a new context must produce a DecisionRecord with a different `envelope_binding_hash` for the new context; reusing the old one fails verification because the runtime's signature on the DecisionRecord is bound to the specific hash.

The v0.2 pipeline additionally enforces:

- `current_time` check: a DecisionRecord's `issued_at_utc` is in the signed region; the verifier checks that it matches the current run's time window.
- `envelope_nonce` (per-envelope random value): recorded in SignedCandidateAction's signed region; reused envelope_nonce fails the freshness check.

## 3. Frozen data structures

### 3.1 IdentityAttestation (v0.2, supersedes v0.1)

```python
{
    "schema_id": "TGE-ATE-V2/0.1",
    "agent_id": str,
    "runtime_fingerprint": str,
    "session_id": str,
    "issued_at_utc": int,
    "public_key_b64": str,
    "signature_b64": str   # Ed25519 over canonicalize(non-sig fields)
}
```

### 3.2 SessionContext (v0.2 NEW)

```python
{
    "schema_id": "TGE-ATE-V2-SESSION/0.1",
    "session_id": str,
    "identity_fingerprint": str,   # SHA-256(canonicalize(IdentityAttestation))
    "receipt_id_predicate": str,   # expected receipt_id
    "capability_id_predicate": str,   # expected capability_id
    "valid_from_utc": int,
    "valid_until_utc": int,
    "issued_at_utc": int,
    "signature_b64": str   # Ed25519 over canonicalize(non-sig fields)
}
```

SessionContext is a runtime-signed binding layer that ties the session to the identity fingerprint and to the expected receipt_id + capability_id.

### 3.3 AcceptanceReceipt (v0.2)

```python
{
    "schema_id": "TGE-ATE-V2-RECEIPT/0.1",
    "receipt_id": str,
    "charter_sha256": str,
    "session_id": str,
    "identity_fingerprint": str,   # NEW in v0.2
    "issued_at_utc": int,
    "gel_unlocks_to": str,
    "signature_b64": str   # Ed25519 over canonicalize(non-sig fields), signed by TGE-fixture key
}
```

The v0.2 receipt includes `identity_fingerprint` in the signed region. This binds the receipt to the identity — a receipt cannot be transplanted to a different identity.

### 3.4 CapabilityToken (v0.2)

```python
{
    "schema_id": "TGE-ATE-V2-CAPABILITY/0.1",
    "capability_id": str,
    "agent_id": str,
    "session_id": str,
    "identity_fingerprint": str,   # NEW in v0.2
    "scope": list[str],
    "valid_from_utc": int,
    "valid_until_utc": int,
    "issued_by": str,
    "signature_b64": str   # Ed25519 over canonicalize(non-sig fields), signed by authority
}
```

### 3.5 SignedCandidateAction (v0.2 NEW)

```python
{
    "schema_id": "TGE-ATE-V2-SIGNED-ACTION/0.1",
    "action_struct": dict,   # v0.2.2 Action (the same schema as before)
    "session_id": str,
    "envelope_nonce": str,   # NEW: random hex 32, per envelope
    "capability_id": str,   # NEW: bound to a specific capability
    "receipt_id": str,   # NEW: bound to a specific receipt
    "identity_fingerprint": str,   # NEW: bound to a specific identity
    "action_preimage_hash": str,   # SHA-256(canonicalize(action_struct)) — explicit
    "signed_at_utc": int,
    "signature_b64": str   # Ed25519 over canonicalize(non-sig fields), signed by runtime
}
```

The runtime signs the action along with the session, nonce, capability_id, receipt_id, and identity_fingerprint. Substituting any of these breaks the signature.

### 3.6 SignedExecutedAction (v0.2 NEW)

```python
{
    "schema_id": "TGE-ATE-V2-EXECUTED/0.1",
    "original_action_hash": str,   # SHA-256(canonicalize(SignedCandidateAction))
    "executed_action_struct": dict,   # post-GEL action (allow/block/redirect)
    "rule_id": str | None,
    "evaluated_at_utc": int,
    "signature_b64": str   # Ed25519 over canonicalize(non-sig fields), signed by GEL-fixture key
}
```

The GEL signs the executed action along with the hash of the original SignedCandidateAction. If the executed action is tampered with, the hash chain breaks.

### 3.7 DecisionRecord (v0.2)

See §2.6.

## 4. Frozen pipeline (v0.2)

### 4.1 TrustPipeline v0.2

```python
def evaluate_envelope_v2(envelope, *, current_time, runtime_pub, authority_pub,
                         tge_pub, gel_signing_priv, pipeline_signing_priv,
                         envelope_nonce) -> DecisionRecord:
    """Run the v0.2 frozen trust pipeline.

    The pipeline uses:
      - runtime_pub to verify IdentityAttestation and SignedCandidateAction
      - authority_pub to verify CapabilityToken
      - tge_pub to verify AcceptanceReceipt
      - gel_signing_priv to sign SignedExecutedAction
      - pipeline_signing_priv to sign DecisionRecord
      - envelope_nonce for freshness

    Gate order:
      1. BIND_IDENTITY (verify IdentityAttestation signature)
      2. BIND_SESSION_CONTEXT (verify SessionContext signature)
      3. BIND_RECEIPT (verify AcceptanceReceipt signature + freshness)
      4. BIND_CAPABILITY (verify CapabilityToken signature + scope)
      5. BIND_CANDIDATE_ACTION (verify SignedCandidateAction signature; check action_fingerprint)
      6. BIND_GEL_INPUT_HASH (verify SignedCandidateAction.action_preimage_hash matches action_struct)
      7. EVAL_GATE (run GEL with active=True on the action_struct)
      8. BIND_EXECUTED_ACTION (verify SignedExecutedAction signature; check original_action_hash)
      9. BIND_DECISION (sign DecisionRecord)

    Any binding failure: verdict = "DENY_BEFORE_BINDING" or "DENY_BEFORE_GEL".
    All bindings pass + GEL allows: verdict = "ALLOW".
    All bindings pass + GEL blocks: verdict = "BLOCK".
    All bindings pass + GEL redirects: verdict = "REDIRECT".
    """
```

### 4.2 What changed from v0.1

| v0.1 | v0.2 |
| -- | -- |
| 5 gates (IDENTITY, RECEIPT, SESSION, CAPABILITY, GEL) | 9 binding stages (5 trust + 4 binding) |
| IdentityAttestation not bound to receipt/capability | IdentityAttestation's fingerprint is in receipt, capability, action signed regions |
| candidate_action unsigned | SignedCandidateAction by runtime; binds session, capability, receipt, identity, nonce |
| GEL output unsigned | SignedExecutedAction by GEL-fixture key; binds original action hash |
| DecisionRecord unsigned | DecisionRecord by pipeline-fixture key; binds all fingerprints |
| envelope_nonce: not present | envelope_nonce in SignedCandidateAction; checked at binding stage 5 |
| Replay distinguished only by session_id consistency | Replay distinguished by envelope_binding_hash + envelope_nonce |

## 5. Frozen test matrix

10 cases. Per PI directive:

1. **ATE-V2-1** — valid fully bound envelope → ALLOW
2. **ATE-V2-2** — replace candidate action with a different but capability-authorized action → verification failure at BIND_CANDIDATE_ACTION (signature mismatch) or BIND_GEL_INPUT_HASH (preimage mismatch)
3. **ATE-V2-3** — replace action after signing/binding but before GEL → verification failure at BIND_EXECUTED_ACTION (original_action_hash mismatch)
4. **ATE-V2-4** — replace executed action after GEL → verification failure at BIND_DECISION (decision_signature mismatch) or BIND_EXECUTED_ACTION (executed_action_fingerprint mismatch in DecisionRecord's signed region)
5. **ATE-V2-5** — replay a valid action under a different session → verification failure at BIND_CANDIDATE_ACTION (session_id mismatch) or BIND_RECEIPT (session_id mismatch) or BIND_CAPABILITY (session_id mismatch)
6. **ATE-V2-6** — replay a valid action under a different agent identity → verification failure at BIND_CAPABILITY (agent_id mismatch) or BIND_CANDIDATE_ACTION (identity_fingerprint mismatch via receipt)
7. **ATE-V2-7** — replay a valid action using a different capability token → verification failure at BIND_CANDIDATE_ACTION (capability_id mismatch) or BIND_CAPABILITY (capability mismatch)
8. **ATE-V2-8** — transplant a valid receipt from another envelope → verification failure at BIND_RECEIPT (session_id or identity_fingerprint or charter_sha256 mismatch) or BIND_CANDIDATE_ACTION (receipt_id mismatch)
9. **ATE-V2-9** — alter gate/audit evidence without changing final decision → verification failure at BIND_DECISION (decision_signature over audit_trail mismatch)
10. **ATE-V2-10** — replay the exact original complete envelope → deterministic verification PASS

### 5.1 Detailed expected outcomes

#### ATE-V2-1: valid fully bound envelope → ALLOW

Setup: full envelope with consistent identity, receipt, capability, signed candidate action. All signatures verify. Cross-fingerprints match.

Expected:
- All 9 binding stages PASS.
- GEL verdict: allow.
- Final verdict: ALLOW.
- DecisionRecord.signature_b64 verifies.
- evidence_chain_hash is reproducible via canonicalize(DecisionRecord.audit_trail).

#### ATE-V2-2: substitute a different but capability-authorized action → verification failure

Setup: take ATE-V2-1's envelope; replace `signed_candidate_action.action_struct` with a different action_struct that *is* in the granted capability scope. The runtime's signature on `signed_candidate_action` no longer covers the new action_struct.

Expected:
- Stage 5 BIND_CANDIDATE_ACTION FAILS: signature verification fails because runtime_pub's signature is over the original action_struct, not the new one.
- Final verdict: DENY_BEFORE_BINDING.
- Reason code: GX_BIND_CANDIDATE_ACTION_FAILED.

#### ATE-V2-3: replace action after signing/binding but before GEL → verification failure

Setup: same envelope, but the pipeline receives a `signed_candidate_action` that doesn't match the `envelope_binding_hash`'s expected SignedCandidateAction fingerprint. Specifically: the SignedCandidateAction in the Envelope is the original; but at GEL evaluation time, the runtime-side wrapper passes a *different* SignedCandidateAction whose action_struct differs.

(Note: in the deterministic PoC, this is simulated by feeding a different SignedCandidateAction to the GEL evaluate step than the one recorded in the envelope.)

Expected:
- Stage 8 BIND_EXECUTED_ACTION FAILS: SignedExecutedAction.original_action_hash != SHA-256(canonicalize(SignedCandidateAction passed to GEL).
- Final verdict: DENY_BEFORE_BINDING.
- Reason code: GX_BIND_EXECUTED_ACTION_FAILED.

#### ATE-V2-4: replace executed action after GEL → verification failure

Setup: take ATE-V2-1's DecisionRecord; modify `executed_action_fingerprint` field. The DecisionRecord's signature is over the original fingerprint; the modified field doesn't verify.

Expected:
- Stage 9 BIND_DECISION FAILS: pipeline_signing_priv's signature over the DecisionRecord's fields (excluding signature_b64) does not verify because the executed_action_fingerprint field was modified.
- Final verdict: DENY_BEFORE_BINDING.
- Reason code: GX_BIND_DECISION_FAILED.

#### ATE-V2-5: replay under different session → verification failure

Setup: take ATE-V2-1's SignedCandidateAction; mutate `session_id` to a different session. The runtime's signature is over the original session_id; the mutated value fails.

Expected:
- Stage 5 BIND_CANDIDATE_ACTION FAILS: signature mismatch.
- Additionally, if the signature verification is not strict (e.g., if a permissive verifier skips it): stage 3 BIND_RECEIPT FAILS (receipt.session_id != envelope-binding expected session_id).
- Stage 4 BIND_CAPABILITY FAILS (capability.session_id != mutated session_id).
- Final verdict: DENY_BEFORE_BINDING.
- Reason code: multiple possible; primary is GX_BIND_CANDIDATE_ACTION_FAILED.

#### ATE-V2-6: replay under different agent identity → verification failure

Setup: take ATE-V2-1's SignedCandidateAction; mutate `identity_fingerprint` to a different identity's fingerprint. The runtime's signature is over the original fingerprint; the mutated value fails.

Expected:
- Stage 5 BIND_CANDIDATE_ACTION FAILS: signature mismatch.
- If permissive: stage 4 BIND_CAPABILITY FAILS (capability.identity_fingerprint != mutated fingerprint).
- Final verdict: DENY_BEFORE_BINDING.
- Reason code: GX_BIND_CANDIDATE_ACTION_FAILED.

#### ATE-V2-7: replay using a different capability token → verification failure

Setup: take ATE-V2-1's SignedCandidateAction; mutate `capability_id` to a different capability. The runtime's signature is over the original capability_id; the mutated value fails.

Expected:
- Stage 5 BIND_CANDIDATE_ACTION FAILS: signature mismatch.
- If permissive: stage 4 BIND_CAPABILITY FAILS (capability_id mismatch between SignedCandidateAction.capability_id and Envelope.capability.capability_id).
- Final verdict: DENY_BEFORE_BINDING.
- Reason code: GX_BIND_CANDIDATE_ACTION_FAILED.

#### ATE-V2-8: transplant a valid receipt from another envelope → verification failure

Setup: build envelope B with its own identity, capability, signed action, and a valid receipt. Take ATE-V2-1's receipt and substitute it into envelope B. The receipt's session_id, identity_fingerprint, charter_sha256 won't match envelope B's.

Expected:
- Stage 3 BIND_RECEIPT FAILS: receipt.session_id != envelope-binding expected session_id, OR receipt.identity_fingerprint != envelope-binding expected identity_fingerprint.
- Final verdict: DENY_BEFORE_BINDING.
- Reason code: GX_BIND_RECEIPT_FAILED.

#### ATE-V2-9: alter gate/audit evidence without changing final decision → verification failure

Setup: take ATE-V2-1's DecisionRecord; modify one audit_trail entry's details field. The decision_signature_b64 is over the original audit_trail; the modified field fails.

Expected:
- Stage 9 BIND_DECISION FAILS: decision_signature_b64 verification fails when applied to the modified DecisionRecord fields.
- Final verdict: DENY_BEFORE_BINDING.
- Reason code: GX_BIND_DECISION_FAILED.

#### ATE-V2-10: replay the exact original complete envelope → deterministic verification PASS

Setup: take ATE-V2-1's complete envelope + DecisionRecord. Run the verification pipeline on the same inputs.

Expected:
- All 9 binding stages PASS.
- DecisionRecord.signature_b64 verifies.
- evidence_chain_hash matches ATE-V2-1's evidence_chain_hash byte-for-byte.
- Final verdict: ALLOW (deterministic re-verification).

## 6. Trust-chain diagram (textual equivalent)

```
[IdentityAttestation]                  (signed by runtime)
        |  includes: agent_id, runtime_fingerprint, session_id, public_key
        v
[SessionContext]                        (signed by runtime)
        |  includes: identity_fingerprint, session_id, receipt_id_predicate,
        |            capability_id_predicate
        v
[AcceptanceReceipt]                     (signed by TGE-fixture key)
        |  includes: charter_sha256, session_id, identity_fingerprint,
        |            receipt_id, gel_unlocks_to
        v
[CapabilityToken]                       (signed by authority)
        |  includes: capability_id, agent_id, session_id, identity_fingerprint,
        |            scope, validity window
        v
[SignedCandidateAction]                 (signed by runtime)
        |  includes: action_struct, session_id, envelope_nonce,
        |            capability_id, receipt_id, identity_fingerprint,
        |            action_preimage_hash
        v
[GEL evaluation on action_struct]       (GEL v0.2.2 reused byte-identically)
        |
        v
[SignedExecutedAction]                  (signed by GEL-fixture key)
        |  includes: original_action_hash, executed_action_struct,
        |            rule_id, evaluated_at_utc
        v
[DecisionRecord]                        (signed by pipeline-fixture key)
        |  includes: envelope_binding_hash, all component fingerprints,
        |            audit_trail, verdict, reason_code
        v
[evidence_chain_hash]                   = SHA-256(canonicalize(audit_trail))
```

Every transition includes the previous artifact's hash in the next artifact's signed region. Substitution anywhere breaks the chain.

## 7. Canonical serialization rule (frozen)

Per §2.2: RFC 8785 JCS strict + v0.2.1-JCS-strict profile extensions (no Unicode normalization). Same profile as `architecture/experimental/stage-c/implementation_v022/SCHEMA-ACTION-v0.2.2.md` §E.1.

The canonicalization function is identical to v0.2.2's canonicalize. No new code.

## 8. Frozen implementation estimate

### 8.1 Modules

- `crypto_utils_v2.py` — extends v0.1 with fingerprint computation, signature verification, and binding helpers. ~100 LOC.
- `identity_v2.py` — extends v0.1 with v0.2 schema. ~120 LOC.
- `session_context.py` — NEW: SessionContext builder + verifier. ~80 LOC.
- `receipt_v2.py` — extends v0.1 with identity_fingerprint binding. ~120 LOC.
- `capability_v2.py` — extends v0.1 with identity_fingerprint binding. ~120 LOC.
- `signed_candidate_action.py` — NEW: SignedCandidateAction builder + verifier. ~120 LOC.
- `signed_executed_action.py` — NEW: SignedExecutedAction builder + verifier. ~100 LOC.
- `pipeline_v2.py` — 9-stage binding pipeline. ~350 LOC.
- `ate_v2_test.py` — 10-case test matrix + replay. ~400 LOC.
- `run_v2.py` — orchestrator. ~50 LOC.

Total: ~1440 LOC. Above v0.1's ~900; reflects the additional binding stages.

### 8.2 Runtime

Each test case is O(1) Python operations + ~6 Ed25519 signature verifications + ~3 SHA-256 computations. Total runtime < 2 seconds on a modern host.

### 8.3 Cost

- 0 participant calls
- 0 model invocations
- 0 premium evaluators
- ~1440 LOC
- < 2 seconds runtime

## 9. Acceptance criteria

Acceptance is **10/10 cases PASS** plus **deterministic replay PASS**.

Any of the following is a PoC failure requiring review:

- An unauthorized substitution is not detected.
- A GEL-allowed action is bound to a different identity, session, or capability than the envelope.
- A transplanted receipt/capability is accepted.
- A tampered executed action is not detected.
- A tampered DecisionRecord is not detected.
- A replay in a different context is accepted.
- The exact-original replay does not verify.

## 10. Claims permitted and forbidden

### Permitted (only if PoC passes)

> "The tested components (IdentityAttestation, SessionContext, AcceptanceReceipt, CapabilityToken, SignedCandidateAction, GEL, SignedExecutedAction, DecisionRecord) compose into a binding chain where every artifact is hash-bound to every other artifact and to the underlying session. Substitution of any artifact within an envelope, or transplantation of an artifact between envelopes, is detected at the appropriate binding stage. The deterministic replay of the exact original envelope produces the same DecisionRecord signature."

### Forbidden

- Behavioral governance evidence — NOT claimed.
- General agent trustworthiness — NOT claimed.
- Production security — NOT claimed.
- Production cryptographic assurance — NOT claimed.
- Hardware-backed identity — NOT claimed.
- Value Architecture effectiveness — NOT claimed.
- DbI/INSA core architecture — NOT claimed.
- Naturalistic participant behavior — NOT claimed.

## 11. What v0.2 establishes

- That all eight artifacts can be cryptographically and structurally bound into one verifiable execution chain.
- That substitution attacks (action substitution, receipt transplantation, capability swap, executed-action tampering, decision-record tampering) are detected at the appropriate binding stage.
- That legitimate deterministic re-verification (the exact-original replay) succeeds.

## 12. What v0.2 does NOT establish

- That the binding works under naturalistic participant behavior (zero participant calls).
- That the binding resists cryptographic attacks beyond Ed25519's standard security assumptions.
- That the binding survives host compromise (the host has the runtime's signing key; see Stage-C v0.2.1 §B.7 caveat).
- That the binding is production-grade (no PKI, no key custody, no hardware roots).
- That the Agent Trust Envelope is production-ready.

## 13. Files (planned, for future implementation)

- `architecture/experimental/ate-poc-v0.2/ATE-POC-DESIGN-v0.2.md` (this document)
- `architecture/experimental/ate-poc-v0.2/implementation/{crypto_utils_v2,identity_v2,session_context,receipt_v2,capability_v2,signed_candidate_action,signed_executed_action,pipeline_v2,ate_v2_test,run_v2}.py`
- `architecture/experimental/ate-poc-v0.2/evidence/ate_v2_evidence.json`

## 14. Scope

- DESIGN ONLY.
- No implementation.
- No execution.
- No participant invocation.
- No production cryptography.
- No hardware-backed identity.
- No promotion of GEL, TGE, COA, or Agent Trust Envelope into DbI/INSA core.
- v0.2.2 GEL reused byte-identically (no adapter; SHA-256 `dfcf2514...21f` preserved).

STOP-AT-DESIGN. Awaiting PI authorization to implement and execute.

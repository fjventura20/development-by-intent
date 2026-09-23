# Agent Trust Envelope — Integration PoC v0.2.1 (ARTIFACT BINDING + REPLAY SEPARATION)

**Status:** DESIGN ONLY — supersedes v0.2's semantic conflation of cryptographic re-verification with execution authorization.
**Author:** Hermes (research-manager-mandate-2026-08-27)
**Predecessor (preserved byte-identically):** `architecture/experimental/ate-poc-v0.2/ATE-POC-DESIGN-v0.2.md` (SHA-256 `498b843ae772e0afd8313338628e057f42f407f3f6865a7acfd9a33bd99a45a1`).

## 0. Purpose

Resolve the v0.2 semantic issue: v0.2 conflates *cryptographic reverification* (does the envelope / decision record still verify?) with *authorization to execute* (is the envelope permitted to cause execution now?). These are distinct operations and must be modeled separately.

This revision:

1. Separates `VERIFY_ENVELOPE` from `AUTHORIZE_EXECUTION` as two explicit operations.
2. Defines a frozen nonce state machine (`UNSEEN` → `AUTHORIZED/CLAIMED` → `CONSUMED`).
3. Clarifies the ATE-V2-10 case so it tests both semantics separately.
4. Adds explicit replay test coverage (5 cases A-E).
5. Freezes separate fixture key roles with stable identifiers.
6. Tightens the binding claim language to match the actual binding graph.
7. Extends DecisionRecord with operation mode + nonce state + replay check fields.
8. Defines the acceptance criterion as: substitution/transplant tests behave as frozen; historical reverification succeeds; replayed execution authorization fails; **the action is executed at most once per one-time envelope nonce**; deterministic re-verification reproduces the expected result.

## 1. Two explicit operations

### 1.1 VERIFY_ENVELOPE

**Purpose:** determine whether a previously created envelope and DecisionRecord are authentic, internally consistent, correctly bound, and untampered.

**Semantics:**
- A previously consumed envelope / nonce MAY pass VERIFY_ENVELOPE.
- This operation MUST NEVER execute or re-execute an action.
- The operation runs all binding-stage verifications; if all pass, it returns `VERIFICATION_PASS` and reports the nonce state observed (which may be `CONSUMED`).
- VERIFY_ENVELOPE does NOT consult the nonce registry to authorize execution; it only reports the current state.

**Output DecisionRecord fields specific to VERIFY_ENVELOPE:**
- `operation_mode = "VERIFY_ENVELOPE"`
- `nonce_state_observed` (one of `UNSEEN`, `AUTHORIZED`, `CONSUMED`)
- `replay_check_result = "N/A_FOR_VERIFICATION"` (this operation does not authorize execution)
- `execution_boundary_reached = false`

### 1.2 AUTHORIZE_EXECUTION

**Purpose:** determine whether a valid envelope is permitted to cause execution NOW.

**Semantics:**
- All identity / receipt / session / capability / binding / GEL requirements must hold (same as v0.2's 9 stages).
- ADDITIONALLY: a nonce state check is required. If the nonce is `UNSEEN`, transition to `AUTHORIZED/CLAIMED` and proceed; if `AUTHORIZED` or `CONSUMED`, fail closed.
- The nonce must be atomically claimed BEFORE the irreversible execution boundary so two concurrent attempts cannot both receive execution authorization.
- Only after nonce claim does the pipeline reach the GEL execution boundary and produce a `SignedExecutedAction`.
- After GEL execution, the nonce transitions to `CONSUMED`.

**Output DecisionRecord fields specific to AUTHORIZE_EXECUTION:**
- `operation_mode = "AUTHORIZE_EXECUTION"`
- `nonce_state_observed` (state at the moment of registration/lookup; for a successful first run: `UNSEEN`)
- `replay_check_result = "PASS_FIRST_EXECUTION"` or `"DENY_NONCE_PREVIOUSLY_AUTHORIZED"` or `"DENY_NONCE_PREVIOUSLY_CONSUMED"`
- `execution_boundary_reached = true` (only after nonce claim + GEL execution + signed executed action)

### 1.3 Why the separation matters

Without this separation, the v0.2 design's ATE-V2-10 ("replay exact original complete envelope → PASS") is ambiguous: does PASS mean "the envelope still verifies" (always true for an unchanged envelope) or "the envelope is now authorized to execute again" (which would be a replay attack vector)?

With the separation:
- `VERIFY_ENVELOPE(exact_original_complete_envelope)` → `VERIFICATION_PASS` (and `nonce_state_observed = CONSUMED` if previously consumed, or `UNSEEN` if never seen).
- `AUTHORIZE_EXECUTION(exact_original_complete_envelope)`:
  - First time: succeeds, transitions UNSEEN → AUTHORIZED → CONSUMED.
  - Subsequent times (replay): fails closed with `DENY_NONCE_PREVIOUSLY_CONSUMED`.

## 2. Frozen nonce state machine

### 2.1 States

```
UNSEEN
  ↓ (first successful AUTHORIZE_EXECUTION begins)
AUTHORIZED/CLAIMED
  ↓ (GEL execution boundary reached, SignedExecutedAction produced)
CONSUMED
```

### 2.2 Transition rules (FROZEN)

| From | To | Trigger | Atomicity |
| -- | -- | -- | -- |
| UNSEEN | AUTHORIZED/CLAIMED | First AUTHORIZE_EXECUTION that has passed all binding stages 1-7 and is about to invoke GEL execution | atomic claim |
| AUTHORIZED/CLAIMED | CONSUMED | GEL execution boundary reached (SignedExecutedAction produced) | atomic transition |
| CONSUMED | (terminal) | n/a | n/a |

### 2.3 Deterministic local fixture registry

For the PoC, the nonce registry is a local `dict` keyed by `envelope_nonce` with values:
```python
{
    "state": "UNSEEN" | "AUTHORIZED" | "CONSUMED",
    "first_authorize_decision_id": str | None,
    "first_authorize_at_utc": int | None,
}
```

Atomicity in the PoC is achieved by Python's GIL + single-threaded test execution. The registry is **not** persisted across processes. This is explicitly a fixture: production atomicity is NOT claimed.

### 2.4 Failure modes

- If the registry lookup returns `UNSEEN` but the claim attempt fails (e.g., concurrent attempt in a multi-threaded test), the registry records the failure and the second attempt returns `DENY_NONCE_CLAIM_FAILED`.
- If the registry lookup returns `AUTHORIZED` or `CONSUMED`, the attempt returns `DENY_NONCE_PREVIOUSLY_AUTHORIZED` or `DENY_NONCE_PREVIOUSLY_CONSUMED`.
- Any of these states → fail closed.

## 3. Clarification of ATE-V2-10

The v0.2 test matrix's ATE-V2-10 ("replay the exact original complete envelope → deterministic verification PASS") is split into two cases in v0.2.1:

- **ATE-V2-10-VERIFY:** exact original completed envelope submitted to `VERIFY_ENVELOPE` → `VERIFICATION_PASS`, `nonce_state_observed = CONSUMED` (if previously consumed via AUTHORIZE_EXECUTION in ATE-V2-1) or `UNSEEN` (if never seen).
- **ATE-V2-10-EXEC:** exact original envelope submitted to `AUTHORIZE_EXECUTION` after the first AUTHORIZE_EXECUTION has consumed the nonce → `DENY_NONCE_PREVIOUSLY_CONSUMED`. The second attempt MUST NOT reach the execution boundary.

The first attempt (the one that consumed the nonce) is ATE-V2-1. The second attempt is ATE-V2-10-EXEC.

## 4. Replay-specific test coverage (5 cases A-E)

### 4.A First valid execution authorization with unseen nonce → permitted

```
Operation: AUTHORIZE_EXECUTION(envelope_v1)
Expected:
  - All binding stages PASS
  - nonce_state_observed = UNSEEN
  - transition: UNSEEN -> AUTHORIZED -> CONSUMED
  - execution_boundary_reached = true
  - replay_check_result = PASS_FIRST_EXECUTION
  - verdict: ALLOW
```

### 4.B Exact historical envelope reverification → PASS

```
Operation: VERIFY_ENVELOPE(envelope_v1_decision_record)
Expected:
  - All binding stages PASS
  - nonce_state_observed = CONSUMED
  - execution_boundary_reached = false
  - verdict: VERIFICATION_PASS
```

### 4.C Second execution authorization using consumed nonce → DENY

```
Operation: AUTHORIZE_EXECUTION(envelope_v1)  [second time, after 4.A]
Expected:
  - All binding stages PASS (envelope is still valid)
  - nonce_state_observed = CONSUMED
  - execution_boundary_reached = false (must not invoke GEL execution)
  - replay_check_result = DENY_NONCE_PREVIOUSLY_CONSUMED
  - verdict: DENY_REPLAY
```

### 4.D Same signed candidate action transplanted into new envelope with different nonce → DENY

```
Operation: AUTHORIZE_EXECUTION(envelope_v2)  [envelope_v2 has same SignedCandidateAction as envelope_v1 but new nonce]
Expected:
  - Stage 5 BIND_CANDIDATE_ACTION FAILS: the signed bindings (session_id, capability_id, receipt_id, identity_fingerprint, action_preimage_hash, AND the original envelope_nonce) are over the original nonce; envelope_v2 has a different nonce, so the binding check fails.
  - verdict: DENY_BINDING_MISMATCH
  - replay_check_result = N/A_FAILED_BEFORE_REPLAY_CHECK
  - execution_boundary_reached = false
```

The signed `envelope_nonce` field in `SignedCandidateAction` ensures the runtime cannot reuse the same signed action in a different envelope context.

### 4.E Altered nonce after candidate signing → signature/binding verification failure

```
Operation: AUTHORIZE_EXECUTION(envelope_v3)  [envelope_v3 has a different nonce than the one SignedCandidateAction was signed over]
Expected:
  - Stage 5 BIND_CANDIDATE_ACTION FAILS: signature verification fails because runtime's signature is over the original nonce; mutated nonce fails.
  - verdict: DENY_BINDING_MISMATCH
```

## 5. Frozen key-role separation

Per PI directive: at least 5 distinct fixture key roles.

| Role | Identifier | Used to sign | Used to verify |
| -- | -- | -- | -- |
| `K_IDENTITY` | `runtime_<agent_id>` | IdentityAttestation, SessionContext, SignedCandidateAction | (signing only by runtime) |
| `K_TGE` | `tge_authority` | AcceptanceReceipt | (signing only by TGE-fixture) |
| `K_AUTHORITY` | `capability_authority` | CapabilityToken | (signing only by authority) |
| `K_GEL` | `gel_attestor` | SignedExecutedAction | (signing only by GEL-fixture) |
| `K_PIPELINE` | `pipeline_attestor` | DecisionRecord | (signing only by pipeline) |

The PoC records:
- A stable identifier per role (the strings above).
- A public-key fingerprint (SHA-256 of canonicalize(public-key bytes)) per role.
- A private-key fingerprint (NOT transmitted; recorded only as a hash to detect fixture changes).

These are explicitly fixture keys, NOT production keys. No key custody, PKI, or hardware root is claimed.

## 6. Binding-claim precision

**Forbidden language (do NOT claim):**
- "every artifact is hash-bound to every other artifact"

**Permitted language (use the strongest wording actually justified):**

> "The relevant artifacts are cryptographically and structurally bound into a single verifiable envelope and session such that substitution or transplantation of a tested component causes deterministic verification failure."

**Actual binding graph implemented in v0.2.1:**

```
IdentityAttestation -> SessionContext -> AcceptanceReceipt -> CapabilityToken -> SignedCandidateAction -> SignedExecutedAction -> DecisionRecord
```

The binding is a *linear chain*, not an all-to-all graph. Each downstream artifact signs over the immediate predecessor's fingerprint (and over selected upstream fingerprints for cross-binding). The DecisionRecord signs over the envelope_binding_hash which hashes the entire Envelope.

**Permitted binding-strength claim:**

> "The relevant artifacts are cryptographically and structurally bound into a single linear binding chain ending in a signed DecisionRecord. Substitution of any single component within an envelope, or transplantation of any single component between envelopes, causes deterministic verification failure at the binding stage that consumes the substituted/transplanted component."

## 7. DecisionRecord requirements (extended)

### 7.1 New fields added in v0.2.1

| Field | Type | Purpose |
| -- | -- | -- |
| `operation_mode` | `str` | `"VERIFY_ENVELOPE"` or `"AUTHORIZE_EXECUTION"` |
| `envelope_nonce` | `str` | The nonce from SignedCandidateAction |
| `nonce_state_observed` | `str` | `"UNSEEN"`, `"AUTHORIZED"`, `"CONSUMED"` |
| `replay_check_result` | `str` | `"PASS_FIRST_EXECUTION"`, `"DENY_NONCE_PREVIOUSLY_AUTHORIZED"`, `"DENY_NONCE_PREVIOUSLY_CONSUMED"`, `"DENY_NONCE_CLAIM_FAILED"`, `"N/A_FOR_VERIFICATION"`, `"N/A_FAILED_BEFORE_REPLAY_CHECK"` |
| `execution_boundary_reached` | `bool` | `true` iff nonce was claimed AND GEL execution boundary was invoked AND SignedExecutedAction was produced |
| `candidate_action_fingerprint` | `str` | SHA-256 of canonicalized SignedCandidateAction |
| `executed_action_fingerprint` | `str` | SHA-256 of canonicalized SignedExecutedAction (None if execution_boundary_reached=false) |
| `previous_decision_id` | `str \| None` | If this is a historical reverification, references the original DecisionRecord |
| `reason_code` | `str` | Deterministic reason code (machine-readable) |

### 7.2 Frozen reason codes

| Code | When |
| -- | -- |
| `PASS` | All binding stages passed; GEL allowed; first execution authorized |
| `BLOCK_R3P` | All binding stages passed; GEL blocked per R3' |
| `REDIRECT_R2P` | All binding stages passed; GEL redirected per R2' |
| `GX_BIND_IDENTITY_FAILED` | Stage 1 fail |
| `GX_BIND_SESSION_CONTEXT_FAILED` | Stage 2 fail |
| `GX_BIND_RECEIPT_FAILED` | Stage 3 fail |
| `GX_BIND_CAPABILITY_FAILED` | Stage 4 fail |
| `GX_BIND_CANDIDATE_ACTION_FAILED` | Stage 5 fail (signature or binding mismatch) |
| `GX_BIND_GEL_INPUT_HASH_FAILED` | Stage 6 fail (action_preimage_hash mismatch) |
| `GX_BIND_EXECUTED_ACTION_FAILED` | Stage 8 fail |
| `GX_BIND_DECISION_FAILED` | Stage 9 fail |
| `GX_REPLAY_NONCE_PREVIOUSLY_AUTHORIZED` | AUTHORIZE_EXECUTION rejected because nonce is AUTHORIZED |
| `GX_REPLAY_NONCE_PREVIOUSLY_CONSUMED` | AUTHORIZE_EXECUTION rejected because nonce is CONSUMED |
| `GX_REPLAY_NONCE_CLAIM_FAILED` | AUTHORIZE_EXECUTION rejected because nonce claim race lost |
| `VERIFICATION_PASS` | VERIFY_ENVELOPE: all binding stages passed |

### 7.3 Historical verification vs new execution authorization

In evidence, these are distinguished by:
- `operation_mode` field (one of the two strings).
- For VERIFY_ENVELOPE: `execution_boundary_reached = false`.
- For AUTHORIZE_EXECUTION (first time): `execution_boundary_reached = true`, `nonce_state_observed = UNSEEN`.
- For AUTHORIZE_EXECUTION (replay): `execution_boundary_reached = false`, `nonce_state_observed = CONSUMED` or `AUTHORIZED`.

## 8. Frozen implementation estimate (v0.2.1)

### 8.1 Modules

- `crypto_utils_v2.py` — extends v0.1; adds per-role key fingerprints. ~120 LOC.
- `identity_v2.py` — extends v0.1 with v0.2 schema. ~120 LOC.
- `session_context.py` — NEW: SessionContext builder + verifier. ~80 LOC.
- `receipt_v2.py` — extends v0.1 with identity_fingerprint binding. ~120 LOC.
- `capability_v2.py` — extends v0.1 with identity_fingerprint binding. ~120 LOC.
- `signed_candidate_action.py` — NEW: SignedCandidateAction builder + verifier. ~120 LOC.
- `signed_executed_action.py` — NEW: SignedExecutedAction builder + verifier. ~100 LOC.
- `nonce_registry.py` — NEW: deterministic local nonce state machine. ~80 LOC.
- `pipeline_v2_1.py` — 9-stage binding pipeline + replay check + nonce claim. ~400 LOC.
- `decision_record.py` — NEW: DecisionRecord builder + extended fields. ~120 LOC.
- `ate_v2_1_test.py` — 14-case test matrix (5 from §4 A-E + 9 from v0.2 with replay clarified). ~500 LOC.
- `run_v2_1.py` — orchestrator. ~50 LOC.

Total: ~1930 LOC. ~1440 from v0.2 + ~490 new (nonce_registry, decision_record extensions, replay-test logic).

### 8.2 Runtime

Each test case is O(1) Python operations + ~6 Ed25519 signature verifications + ~3 SHA-256 computations + 1 nonce registry lookup. Total runtime < 3 seconds on a modern host.

### 8.3 Cost

- 0 participant calls
- 0 model invocations
- 0 premium evaluators
- ~1930 LOC
- < 3 seconds runtime

## 9. Frozen test matrix (14 cases)

### 9.1 v0.2 cases retained (with replay clarification)

| # | Test | Operation | Expected |
| -- | -- | -- | -- |
| ATE-V2.1-1 | valid fully bound envelope (first AUTHORIZE_EXECUTION) | AUTHORIZE_EXECUTION | ALLOW, nonce_state=UNSEEN→CONSUMED, execution_boundary=true |
| ATE-V2.1-2 | substitute different capability-authorized action | AUTHORIZE_EXECUTION | DENY_BINDING_MISMATCH |
| ATE-V2.1-3 | replace action after signing/binding but pre-GEL | AUTHORIZE_EXECUTION | DENY_BINDING_MISMATCH |
| ATE-V2.1-4 | replace executed action after GEL (signing attack) | AUTHORIZE_EXECUTION | DENY_BINDING_MISMATCH |
| ATE-V2.1-5 | replay under different session (action-level) | AUTHORIZE_EXECUTION | DENY_BINDING_MISMATCH |
| ATE-V2.1-6 | replay under different agent identity (action-level) | AUTHORIZE_EXECUTION | DENY_BINDING_MISMATCH |
| ATE-V2.1-7 | replay using different capability token (action-level) | AUTHORIZE_EXECUTION | DENY_BINDING_MISMATCH |
| ATE-V2.1-8 | transplant receipt from another envelope | AUTHORIZE_EXECUTION | DENY_BINDING_MISMATCH |
| ATE-V2.1-9 | alter gate/audit evidence without decision change | AUTHORIZE_EXECUTION | DENY_BINDING_MISMATCH |
| ATE-V2.1-10-VERIFY | exact historical envelope under VERIFY_ENVELOPE | VERIFY_ENVELOPE | VERIFICATION_PASS, nonce_state=CONSUMED, execution_boundary=false |
| ATE-V2.1-10-EXEC | exact original envelope under AUTHORIZE_EXECUTION (replay) | AUTHORIZE_EXECUTION | DENY_REPLAY_NONCE_PREVIOUSLY_CONSUMED, execution_boundary=false |

### 9.2 Replay-specific cases A-E (5 cases)

| # | Test | Operation | Expected |
| -- | -- | -- | -- |
| ATE-V2.1-A | first valid execution authorization with unseen nonce | AUTHORIZE_EXECUTION | ALLOW, nonce_state_observed=UNSEEN, transition to CONSUMED, execution_boundary=true |
| ATE-V2.1-B | exact historical envelope reverification | VERIFY_ENVELOPE | VERIFICATION_PASS, nonce_state_observed=CONSUMED, execution_boundary=false |
| ATE-V2.1-C | second execution authorization using consumed nonce | AUTHORIZE_EXECUTION | DENY_NONCE_PREVIOUSLY_CONSUMED, execution_boundary=false |
| ATE-V2.1-D | same signed action transplanted to new envelope with different nonce | AUTHORIZE_EXECUTION | DENY_BINDING_MISMATCH at stage 5 (signed nonce mismatch) |
| ATE-V2.1-E | altered nonce after candidate signing | AUTHORIZE_EXECUTION | DENY_BINDING_MISMATCH at stage 5 (signature over original nonce) |

Total: 16 cases. (11 v0.2 + 5 A-E. ATE-V2.1-10 is split into two.)

### 9.3 Why ATE-V2.1-A duplicates ATE-V2.1-1

ATE-V2.1-A is the explicit "first execution" case required by the PI directive. It is functionally identical to ATE-V2.1-1 but with explicit replay-check assertions. Both cases are run; ATE-V2.1-A's evidence includes the nonce state transition trace.

## 10. Acceptance criterion (FROZEN)

The PoC may PASS only if:

1. **All substitution/transplant tests behave as frozen** (ATE-V2.1-2 through ATE-V2.1-9 each produce a `DENY_BINDING_MISMATCH` at the appropriate binding stage).
2. **Exact historical reverification succeeds** (ATE-V2.1-10-VERIFY and ATE-V2.1-B both produce `VERIFICATION_PASS` with `execution_boundary_reached = false`).
3. **Replayed execution authorization fails** (ATE-V2.1-10-EXEC and ATE-V2.1-C both produce `DENY_NONCE_PREVIOUSLY_CONSUMED` with `execution_boundary_reached = false`).
4. **The action is executed at most once for a one-time envelope nonce** (verified by counting `execution_boundary_reached = true` events per nonce across the test run; for any one nonce this count must be ≤ 1).
5. **Deterministic replay/reverification reproduces the expected verification result** (running the pipeline twice on the same envelope produces the same DecisionRecord signature byte-for-byte).
6. **All evidence records are independently recomputable** (each DecisionRecord can be reconstructed from the recorded inputs + fixtures + frozen pipeline).

**Any second execution authorized from the same one-time envelope is a PoC failure.**

## 11. Claims permitted and forbidden

### Permitted (only if PoC passes)

> "The relevant artifacts are cryptographically and structurally bound into a single linear binding chain ending in a signed DecisionRecord. Substitution of any single component within an envelope, or transplantation of any single component between envelopes, causes deterministic verification failure at the binding stage that consumes the substituted/transplanted component. The first AUTHORIZE_EXECUTION of a valid envelope transitions the envelope nonce from UNSEEN through AUTHORIZED to CONSUMED. Subsequent AUTHORIZE_EXECUTION attempts against the same envelope nonce fail closed with deterministic reason codes. VERIFY_ENVELOPE operations against previously consumed envelopes succeed and report the consumed nonce state without reaching the execution boundary."

### Forbidden

- "every artifact is hash-bound to every other artifact" — NOT claimed (binding is linear, not all-to-all).
- Behavioral governance evidence — NOT claimed.
- General agent trustworthiness — NOT claimed.
- Production security — NOT claimed.
- Production cryptographic assurance — NOT claimed.
- Hardware-backed identity — NOT claimed.
- Value Architecture effectiveness — NOT claimed.
- DbI/INSA core architecture — NOT claimed.
- Naturalistic participant behavior — NOT claimed.
- Distributed atomicity of the nonce registry — NOT claimed (deterministic local fixture only).
- Production replay resistance — NOT claimed.

## 12. What v0.2.1 establishes

- That all eight artifacts can be cryptographically and structurally bound into a single linear chain.
- That substitution attacks are detected at the appropriate binding stage.
- That historical reverification is distinct from execution authorization.
- That a one-time envelope nonce can authorize exactly one execution across multiple attempts.
- That deterministic re-verification of the exact original envelope succeeds.

## 13. What v0.2.1 does NOT establish

- That the binding works under naturalistic participant behavior.
- That the binding resists cryptographic attacks beyond Ed25519's standard security assumptions.
- That the binding survives host compromise.
- That the binding is production-grade (no PKI, no key custody, no hardware roots).
- That the Agent Trust Envelope is production-ready.

## 14. Files (planned, for implementation)

- `architecture/experimental/ate-poc-v0.2.1/ATE-POC-DESIGN-v0.2.1.md` (this document)
- `architecture/experimental/ate-poc-v0.2.1/implementation/{crypto_utils_v2,identity_v2,session_context,receipt_v2,capability_v2,signed_candidate_action,signed_executed_action,nonce_registry,pipeline_v2_1,decision_record,ate_v2_1_test,run_v2_1}.py`
- `architecture/experimental/ate-poc-v0.2.1/evidence/ate_v2_1_evidence.json`

## 15. Scope

- DESIGN ONLY.
- No implementation.
- No execution.
- No participant invocation.
- No production cryptography.
- No hardware-backed identity.
- No promotion of GEL, TGE, COA, or Agent Trust Envelope into DbI/INSA core.
- v0.2.2 GEL reused byte-identically (no adapter; SHA-256 `dfcf2514...21f` preserved).

STOP-AT-DESIGN. Awaiting PI authorization to implement and execute.

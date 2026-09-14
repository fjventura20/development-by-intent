# Agent Trust Envelope — Integration PoC v0.1 (Design Only)

**Status:** DESIGN ONLY — not implemented.
**Author:** Hermes (research-manager-mandate-2026-08-27)
**Predecessors (preserved byte-identically):**
- TGE v0.1 / v0.2 / v0.2.1 (`architecture/experimental/TRUSTED-GOVERNANCE-ESTABLISHMENT-v0.1.md` et al.)
- TGE-PoC (`architecture/experimental/tge-poc/`, frozen at `5ed908b0beaa26e8003b2f0e9e0f1c66b648425f`)
- Stage-C v0.2.2 (`architecture/experimental/stage-c/implementation_v022/`)
- Stage-C synthesis closeout (`architecture/experimental/stage-c/STAGE-C-SYNTHESIS-CLOSEOUT.md`)

## 0. Purpose

Test whether the emerging components (TGE acceptance receipts, v0.2.2 Action schema, v0.2.2 GEL, transport extraction) can compose into a **deterministic trust-and-execution boundary**. This is NOT a behavioral-compliance experiment. This is a deterministic integration test.

The pipeline tested:

```
agent identity / provenance
    ↓
governance / COA acceptance credential
    ↓
session binding
    ↓
requested capability / authorization
    ↓
structured candidate action
    ↓
GEL enforcement
    ↓
executed or denied action
    ↓
auditable evidence record
```

Each layer is a *trust gate*. The PoC tests that the gates compose into a single deterministic verdict pipeline.

## 1. Architectural components

### 1.1 Reused from prior work

- **TGE acceptance receipt** (frozen at `architecture/experimental/TRUSTED-GOVERNANCE-ESTABLISHMENT-v0.2.1.md` §B.4): a structured dict `{receipt_id, charter_sha256, session_id, issued_at_utc}` representing that an acceptance event occurred.
- **v0.2.2 Action schema** (frozen at `architecture/experimental/stage-c/implementation_v022/SCHEMA-ACTION-v0.2.2.md`): structured candidate-action representation with codes.
- **v0.2.2 GEL** (frozen at `architecture/experimental/stage-c/implementation_v022/gel_v022.py`): rule set R1'/R2'/R3' producing allow/block/redirect verdicts.
- **v0.2.2 capability schema** (NEW, defined here): structured capability request `{capability_id, scope, valid_from_utc, valid_until_utc, signed_by_authority, signature_b64}`.

### 1.2 NEW components introduced

- **IdentityAttestation**: a structured dict representing an agent's identity + provenance. The IdentityAttestation is signed by a *runtime attestation key* (Ed25519 fixture in v0.1).
- **CapabilityToken**: a structured dict representing an authorized capability for a session. Signed by an *authority* (Ed25519 fixture in v0.1).
- **Envelope**: a structured dict composing all trust-gate inputs for a single candidate action.
- **TrustDecision**: a structured dict representing the deterministic verdict of the pipeline. The TrustDecision is the auditable decision record.
- **TrustPipeline**: a frozen Python function that takes an Envelope and produces a TrustDecision.

### 1.3 What is NOT introduced

- NO hardware-backed identity (real TPM, swtpm, remote attestation).
- NO production cryptography (no production key management, no PKI, no certificate authority).
- NO live participant invocation.
- NO model calls of any kind.
- NO evaluators.

All credentials are deterministic Python fixtures. All signatures are Ed25519 over deterministic bytes.

## 2. Frozen data structures

### 2.1 IdentityAttestation

```python
@dataclass
class IdentityAttestation:
    schema_id: str   # "TGE-ATE/0.1"
    agent_id: str    # opaque hex 16
    runtime_fingerprint: str   # hex 64
    session_id: str  # opaque hex 16
    issued_at_utc: int
    public_key_b64: str  # runtime's Ed25519 public key
    signature_b64: str   # Ed25519 signature over canonicalized(non-sig fields)
```

The IdentityAttestation binds an agent ID + runtime fingerprint + session ID to a public key. Signature verifies the binding.

### 2.2 CapabilityToken

```python
@dataclass
class CapabilityToken:
    schema_id: str   # "TGE-ATE/0.1"
    capability_id: str   # opaque hex 16
    agent_id: str    # matches IdentityAttestation.agent_id
    session_id: str  # matches IdentityAttestation.session_id
    scope: list[str]   # e.g., ["read:file:/tmp/scratch/*", "delete:state:audit_trail"]
    valid_from_utc: int
    valid_until_utc: int
    issued_by: str   # authority ID
    authority_signature_b64: str
```

The CapabilityToken grants the agent specific capabilities for the session. The signature binds the agent + session + scope + validity window to the authority's public key.

### 2.3 TGE-style Acceptance Receipt (reused from v0.2.1)

```python
@dataclass
class FixtureAcceptanceReceipt:
    receipt_id: str
    charter_sha256: str
    session_id: str   # matches IdentityAttestation.session_id
    issued_at_utc: int
    gel_unlocks_to: str   # "ate_trust_envelope"
```

This receipt attests that an acceptance event occurred for the given session. It is a *fixture* (not a production TGE receipt): no cryptographic signature, no runtime fingerprint binding, no canonicalized charter. The receipt is consumed by the pipeline as a *token*, not as cryptographic evidence. This is consistent with v0.2.1's framing.

### 2.4 Envelope

```python
@dataclass
class Envelope:
    schema_id: str   # "TGE-ATE-ENVELOPE/0.1"
    envelope_id: str   # opaque hex 16
    issued_at_utc: int
    identity: IdentityAttestation
    capability: CapabilityToken
    acceptance_receipt: FixtureAcceptanceReceipt
    candidate_action: dict   # v0.2.2 Action
```

The Envelope composes all trust-gate inputs for a single candidate action.

### 2.5 TrustDecision

```python
@dataclass
class TrustDecision:
    schema_id: str   # "TGE-ATE-DECISION/0.1"
    decision_id: str   # opaque hex 16
    envelope_id: str
    issued_at_utc: int
    verdict: str   # "ALLOW" | "BLOCK" | "REDIRECT" | "DENY_BEFORE_GEL"
    executed_action: dict   # the post-pipeline action (may be REDIRECTED action or BLOCKED action template)
    audit_trail: list[dict]   # ordered list of gate decisions
    trust_summary: dict   # summary of trust-conditions passed/failed
```

Each gate in the pipeline records its decision as a dict in `audit_trail`. The `trust_summary` summarizes which trust conditions passed or failed.

### 2.6 Gate decision record

Each gate produces a dict:

```python
{
    "gate_id": str,         # "GATE_IDENTITY" | "GATE_RECEIPT" | "GATE_SESSION" | "GATE_CAPABILITY" | "GATE_GEL"
    "verdict": "PASS" | "FAIL",
    "reason_code": str,     # "GX_..." or "PASS"
    "reason_description": str,
    "details": dict,
    "evaluated_at_utc": int
}
```

## 3. Frozen pipeline

### 3.1 TrustPipeline

```python
def evaluate_envelope(envelope: Envelope, gel_rules: list, current_time: int) -> TrustDecision:
    """Frozen pipeline. Each gate is a pure function on (envelope, current_time).

    Gate order:
      1. GATE_IDENTITY: signature on IdentityAttestation verifies
      2. GATE_RECEIPT: AcceptanceReceipt exists, schema id OK
      3. GATE_SESSION: session_id in IdentityAttestation == session_id in CapabilityToken == session_id in AcceptanceReceipt == session_id in candidate_action
      4. GATE_CAPABILITY: current_time is in [valid_from, valid_until]; candidate action's target_kind and operation are within capability scope
      5. GATE_GEL: v0.2.2 GEL evaluation (active=True)

    Any gate failure: verdict = "DENY_BEFORE_GEL" (early) or the GEL verdict.
    All gates pass + GEL verdict == "allow": verdict = "ALLOW".
    All gates pass + GEL verdict == "block": verdict = "BLOCK".
    All gates pass + GEL verdict == "redirect": verdict = "REDIRECT".

    Every gate records a decision dict in audit_trail.
    """
```

### 3.2 Gate 1: GATE_IDENTITY

Validation:

- IdentityAttestation.signature_b64 verifies under IdentityAttestation.public_key_b64.
- IdentityAttestation.session_id is non-empty.

Failure: `verdict = "DENY_BEFORE_GEL"`, `reason_code = "GX_IDENTITY_INVALID"`.

### 3.3 Gate 2: GATE_RECEIPT

Validation:

- AcceptanceReceipt exists and schema_id == "TGE-STAGE-C-ACTION/0.1"... wait — re-spec. The receipt schema_id is "TGE-ATE/0.1" per §2.3. (The reuse is of the *receipt concept*, not the v0.2.1 schema_id literal.)
- AcceptanceReceipt.session_id == IdentityAttestation.session_id.

Failure: `verdict = "DENY_BEFORE_GEL"`, `reason_code = "GX_RECEIPT_INVALID"`.

### 3.4 Gate 3: GATE_SESSION

Validation:

- IdentityAttestation.session_id == CapabilityToken.session_id == AcceptanceReceipt.session_id.
- candidate_action.session_id == IdentityAttestation.session_id.

Failure: `verdict = "DENY_BEFORE_GEL"`, `reason_code = "GX_SESSION_MISMATCH"`.

### 3.5 Gate 4: GATE_CAPABILITY

Validation:

- current_time is within [CapabilityToken.valid_from_utc, CapabilityToken.valid_until_utc].
- CapabilityToken.scope contains a capability matching the candidate_action:
  - For each `(operation, target_kind)` in candidate_action, there must be a scope entry like `"<operation>:<target_kind>:<target_identifier_glob>"` (or `"*"` for any).
  - The target_identifier_glob is matched against candidate_action.target_identifier.

Failure: `verdict = "DENY_BEFORE_GEL"`, `reason_code = "GX_CAPABILITY_EXCEEDED"` (or `GX_CAPABILITY_EXPIRED`).

### 3.6 Gate 5: GATE_GEL

Validation:

- Reuse v0.2.2 `evaluate_v022(candidate_action, FROZEN_RULES_V022, active=True)`.
- The pipeline always runs GEL with active=True. If Gates 1-4 failed, GEL is skipped (the action is denied before enforcement).

If Gates 1-4 all pass:

- GEL verdict == "allow" → final verdict "ALLOW"
- GEL verdict == "block" → final verdict "BLOCK"
- GEL verdict == "redirect" → final verdict "REDIRECT"

### 3.7 Trust summary

After all gates run, the pipeline produces:

```python
trust_summary = {
    "identity_passed": bool,
    "receipt_passed": bool,
    "session_passed": bool,
    "capability_passed": bool,
    "gel_passed": bool,   # True if GEL allowed; False if GEL blocked/redirected; None if GEL skipped
    "first_failing_gate": str | None,
}
```

The auditable decision record includes this summary.

## 4. Frozen test matrix

Five test cases. Each case constructs an Envelope with deliberate mutations to test a specific trust-gate failure mode.

### 4.1 Case ATE-1 — valid identity + valid receipt + authorized capability + permitted action → ALLOW

- IdentityAttestation: signature verifies.
- CapabilityToken: covers `[B11, C5, "*"]` (NONE operation, action target, any identifier); window is current.
- AcceptanceReceipt: schema_id OK, session_id matches.
- candidate_action: `decision=A1, operation=B11, target_kind=C5, target_identifier="anything", authority_asserted="D1", ...`
- candidate_action is charter-consistent (GEL allows).

Expected:
- All 5 gates PASS.
- GEL verdict: allow.
- Final verdict: ALLOW.
- Trust summary: all passed.

### 4.2 Case ATE-2 — valid identity/receipt but action exceeds granted capability → DENY_BEFORE_GEL

- IdentityAttestation: signature verifies.
- CapabilityToken: covers `[B11, C5, "*"]` (NONE operation, action target); does NOT cover `B1` (DELETE) on `C1` (file).
- candidate_action: `decision=A1, operation=B1, target_kind=C1, target_identifier="/tmp/scratch/foo", authority_asserted="D1", ...`

Expected:
- Gates 1-3 PASS.
- Gate 4 FAILS (operation B1 not in scope).
- Gate 5 SKIPPED.
- Final verdict: DENY_BEFORE_GEL.
- Trust summary: first_failing_gate = "GATE_CAPABILITY", reason_code = "GX_CAPABILITY_EXCEEDED".

### 4.3 Case ATE-3 — missing / invalid / expired / session-mismatched receipt → DENY before action execution

This is actually 4 sub-cases; each is a separate test:

#### ATE-3a — missing receipt

- AcceptanceReceipt is None.

Expected:
- Gate 2 FAILS: reason_code = "GX_RECEIPT_MISSING".
- Final verdict: DENY_BEFORE_GEL.

#### ATE-3b — invalid receipt (schema_id mismatch)

- AcceptanceReceipt.schema_id = "INVALID".

Expected:
- Gate 2 FAILS: reason_code = "GX_RECEIPT_INVALID".
- Final verdict: DENY_BEFORE_GEL.

#### ATE-3c — expired receipt (issued too long ago)

- AcceptanceReceipt.issued_at_utc = current_time - (valid_window * 2) — far in the past.
- Note: the receipt has no `valid_until_utc` field in §2.3. The pipeline checks `issued_at_utc > current_time - RECEIPT_FRESHNESS_WINDOW` where `RECEIPT_FRESHNESS_WINDOW` is a frozen constant (e.g., 3600 seconds = 1 hour).

Expected:
- Gate 2 FAILS: reason_code = "GX_RECEIPT_EXPIRED".
- Final verdict: DENY_BEFORE_GEL.

#### ATE-3d — session mismatch

- AcceptanceReceipt.session_id != IdentityAttestation.session_id.

Expected:
- Gate 3 FAILS: reason_code = "GX_SESSION_MISMATCH".
- Final verdict: DENY_BEFORE_GEL.

### 4.4 Case ATE-4 — authorized request with action violating GEL governance → GEL BLOCK/REDIRECT

- IdentityAttestation: valid.
- CapabilityToken: covers `[B1, C1, "/tmp/*"]` (DELETE operation, file target, /tmp/*); window is current.
- candidate_action: `decision=A9, operation=B1, target_kind=C1, target_identifier="/tmp/foo", authority_asserted="D1", ...`

Expected:
- Gates 1-4 PASS.
- Gate 5 (GEL): R3' predicate True (operation B1, target_kind C1, authority D1) → block.
- Final verdict: BLOCK.
- Trust summary: first_failing_gate = "GATE_GEL", reason_code = "GX_R3p_NO_UNAUTHORIZED_DESTRUCTIVE_ACTION".
- executed_action: BLOCKED_ACTION_TEMPLATE.

(Note: the capability is *granted* for DELETE on /tmp/*. GEL blocks because the *governance* layer disallows destructive operations on files with USER authority. The capability layer is necessary but not sufficient.)

### 4.5 Case ATE-5 — tampered identity / receipt / action / evidence-chain field → verification failure / DENY

This is 4 sub-cases; each tests a different tampering point:

#### ATE-5a — tampered identity (signature mismatch)

- IdentityAttestation.signature_b64 is replaced with a random signature.

Expected:
- Gate 1 FAILS: reason_code = "GX_IDENTITY_INVALID".
- Final verdict: DENY_BEFORE_GEL.

#### ATE-5b — tampered receipt (charter_sha256 replaced)

- AcceptanceReceipt.charter_sha256 is replaced with a different hash.

Expected:
- Gate 2 FAILS: reason_code = "GX_RECEIPT_INVALID" (the receipt's charter_sha256 does not match the bound charter; or the receipt is internally inconsistent).
- Final verdict: DENY_BEFORE_GEL.

#### ATE-5c — tampered candidate_action (operation changed after signature)

- candidate_action is signed by the runtime; then the operation field is replaced.

Note: this case requires the v0.2.2 schema to support signed actions. Since v0.2.2 does not include a per-action signature, this case tests the absence of a per-action signature: the pipeline detects the absence via the candidate_action.session_id matching check, but does not detect a tampered operation field.

For the PoC, this case tests: even if the capability token grants the operation, the pipeline must reject candidate_actions whose session_id doesn't match. **The PoC does NOT have per-action signatures**; this is a documented limitation.

Expected:
- If operation is changed to one not in capability scope: Gate 4 fails (capability exceeded).
- If operation is changed to one in capability scope: the pipeline does NOT detect the tampering. The case is recorded as "tampering-not-detected-at-this-stage."

#### ATE-5d — tampered evidence chain (audit_trail entry modified)

The pipeline does not have a separately auditable evidence chain outside the pipeline. This case is out of scope for v0.1 — it would require a tamper-evident log, which is a production infrastructure feature, not a v0.1 PoC concern. The PoC explicitly excludes this case with the note: "evidence-chain tampering detection requires a tamper-evident log; deferred to a later stage."

### 4.6 Frozen summary of test matrix

| Case | Sub-cases | Expected verdict | First failing gate |
| -- | -- | -- | -- |
| ATE-1 | — | ALLOW | (none) |
| ATE-2 | — | DENY_BEFORE_GEL | GATE_CAPABILITY (GX_CAPABILITY_EXCEEDED) |
| ATE-3 | a/b/c/d | DENY_BEFORE_GEL | GATE_RECEIPT or GATE_SESSION |
| ATE-4 | — | BLOCK | GATE_GEL (R3') |
| ATE-5 | a/b/c/d | DENY_BEFORE_GEL | various |

Total: 1 + 1 + 4 + 1 + 4 = **11 deterministic test cases**.

## 5. Implementation estimate

### 5.1 Modules

- `identity.py` — IdentityAttestation struct + signature verification (~80 LOC).
- `capability.py` — CapabilityToken struct + signature verification + scope matching (~120 LOC).
- `receipt.py` — FixtureAcceptanceReceipt + freshness check (~60 LOC).
- `pipeline.py` — TrustPipeline + 5 gates (~250 LOC).
- `ate_test.py` — 11-case test runner (~250 LOC).
- `run.py` — orchestrator (~50 LOC).

Total: ~810 LOC.

### 5.2 Run time

Each test case is O(1) Python operations + 1 Ed25519 signature verification. Total runtime < 1 second on a modern host.

### 5.3 Cryptographic primitive reuse

Ed25519 from `cryptography` library (already installed; same as v0.2.1 GEL and TGE-PoC).

### 5.4 Cost

- 0 participant calls.
- 0 model invocations.
- 0 premium evaluators.
- ~810 LOC.
- < 1 second runtime.

## 6. What the PoC establishes

- That the existing components (TGE receipt concept, v0.2.2 schema, v0.2.2 GEL, transport extraction) can compose into a deterministic trust-and-execution pipeline.
- That each gate produces an auditable decision record.
- That a tampered identity / receipt / capability produces a deterministic verification failure.
- That a GEL-blocked action is recorded as BLOCK (not DENY_BEFORE_GEL), allowing the distinction between pre-GEL denial (capability / identity / receipt failure) and post-GEL enforcement (governance rule violation).

## 7. What the PoC does NOT establish

- That GEL affects naturalistic participant behavior.
- That the binding invariant is causally load-bearing.
- That hardware-backed identity is achieved.
- That production cryptography is in use.
- That the Agent Trust Envelope is production-ready.
- That the participant model is intrinsically compliant.
- That Value Architecture is effective.
- That general agent trustworthiness is achieved.

## 8. Strongest claim supported by a positive PoC result

> The tested components (TGE-style acceptance receipt, v0.2.2 Action schema, v0.2.2 GEL, Ed25519-fixture IdentityAttestation, Ed25519-fixture CapabilityToken, transport extraction) compose into a deterministic trust-and-execution pipeline. The pipeline produces auditable decision records identifying which trust condition passed or failed and why. The pipeline correctly distinguishes identity / receipt / session / capability failures (DENY_BEFORE_GEL) from governance-rule violations (BLOCK / REDIRECT).

This is **integration evidence**, not behavioral evidence. The strongest supported claim is that the components compose; it does not establish that the components govern naturalistic participant behavior.

## 9. Proposed evidence record schema (frozen)

The TrustDecision is the auditable evidence record. It contains:

- `decision_id` (opaque)
- `envelope_id`
- `issued_at_utc`
- `verdict` (ALLOW / BLOCK / REDIRECT / DENY_BEFORE_GEL)
- `executed_action` (the post-pipeline action)
- `audit_trail` (ordered list of gate decisions)
- `trust_summary` (which conditions passed/failed)

Each gate decision in `audit_trail` contains:

- `gate_id`
- `verdict` (PASS / FAIL)
- `reason_code` (GX_...)
- `reason_description`
- `details`
- `evaluated_at_utc`

## 10. Scope and non-goals

- This document is a design only.
- No implementation is included.
- No participant invocation.
- No production cryptography.
- No hardware-backed identity.
- No promotion of GEL, TGE, COA, or Agent Trust Envelope into DbI/INSA core.
- The Agent Trust Envelope remains a research / experimental artifact.

## 11. Files (planned, for a future implementation commit)

- `architecture/experimental/ate-poc-v0.1/ATE-POC-DESIGN-v0.1.md` (this document)
- `architecture/experimental/ate-poc-v0.1/implementation/identity.py`
- `architecture/experimental/ate-poc-v0.1/implementation/capability.py`
- `architecture/experimental/ate-poc-v0.1/implementation/receipt.py`
- `architecture/experimental/ate-poc-v0.1/implementation/pipeline.py`
- `architecture/experimental/ate-poc-v0.1/implementation/ate_test.py`
- `architecture/experimental/ate-poc-v0.1/implementation/run.py`
- `architecture/experimental/ate-poc-v0.1/evidence/ate_evidence.json` (produced by execution, when authorized)

STOP-AT-DESIGN. Awaiting PI authorization to implement and execute.

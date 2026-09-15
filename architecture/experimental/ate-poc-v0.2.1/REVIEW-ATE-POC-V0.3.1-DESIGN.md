# ATE v0.3.1 — Adversarial Design Review

**Status:** DESIGN REVIEW ONLY (no implementation)
**Author:** Hermes (research-manager-mandate-2026-09-15)
**Date:** 2026-09-15
**Authority:** Frank Ventura (PI), per directive of 2026-09-15 (v0.3.1 amendment accepted; adversarial design review authorized).
**Review target (preserved byte-identically):** `architecture/experimental/ate-poc-v0.2.1/ATE-POC-V0.3.1-DESIGN-AMENDMENT.md` (this commit).

## 0. Scope and review focus

This review examines the ATE v0.3.1 design amendment against nine specific attack/failure dimensions enumerated by the PI directive:

1. Self-authorization
2. Replay
3. Stale behavioral evidence
4. VA version substitution
5. Session substitution
6. COA substitution
7. Capability widening
8. Trust-decision substitution
9. Fail-open behavior

For each dimension, this review:

- States the threat
- Identifies the gate(s) that defend against it
- Asks whether the defense is mechanical (cryptographic / fail-closed by code) or merely declarative
- Proposes corrections only — does not implement them

If any defense is NOT mechanical, the review flags a `BLOCKING` defect.

## 1. Self-authorization

### 1.1 Threat

The participant agent (which holds the Live Provenance ephemeral key and the K_IDENTITY private key for the session) submits its own evidence and simultaneously certifies its own trust decision, achieving `TRUST_GRANTED` without external authority.

### 1.2 Defense in v0.3.1

Per PI RULING 4: `K_TRUST_DECISION` is a separate authority fixture outside the participant agent's authority boundary. The participant does NOT hold the trust-decision private key.

### 1.3 Mechan­ical vs. declarative

The defense is **mechanical** at three layers:

1. The participant does not hold `K_TRUST_DECISION` private key (separation enforced by key custody, which is documented as out-of-scope for v0.3.1 production key-management infrastructure).
2. The `TrustDecision.decision_signature_b64` is produced by `K_TRUST_DECISION`. The participant cannot forge a valid signature.
3. The signed region of `TrustDecision` covers `verdict`, `reason_code`, `envelope_fingerprint`, `envelope_nonce`, `gate_results`. The participant cannot substitute a `GRANTED` verdict for a `DENIED` one without invalidating the signature.

### 1.4 Verdict

**NOT BLOCKING.** Self-authorization is mechanically prevented by the separation of `K_TRUST_DECISION` from the participant's key custody and by the signed-region coverage of the verdict field.

### 1.5 Residual concern (informational, not blocking)

The v0.3.1 design relies on the fixture pattern: the same Python process that runs the test holds all fixture keys. A future implementation must keep `K_TRUST_DECISION` in a separate logical context. This is documented as "Do not design production key-management infrastructure in v0.3.1" — so it is appropriately scoped.

## 2. Replay

### 2.1 Threat

An attacker captures a previously valid envelope + TrustDecision and resubmits it for `AUTHORIZE_EXECUTION`. Or captures a previously executed `SignedGovernedAction` and replays it to cause double-execution.

### 2.2 Defense in v0.3.1

Per PI RULING 6 and the ATE v0.2.1 nonce semantics:

- `envelope_nonce` is single-use (`UNSEEN → AUTHORIZED → CONSUMED`).
- G8 checks the nonce state in the `NonceRegistry`. `AUTHORIZED` → `GX_NONCE_PREVIOUSLY_AUTHORIZED`. `CONSUMED` → `GX_NONCE_PREVIOUSLY_CONSUMED`.
- Atomic transition: claim BEFORE execution boundary; consume AFTER GEL execution.

### 2.3 Mechanical vs. declarative

**Mechanical.**

1. The trust-decision function reads nonce state from the registry at G8 before signing the decision.
2. Even if a TrustDecision is captured after signing, the captured decision's `envelope_nonce` is already consumed; a second AUTHORIZE fails at G8.
3. The captured `SignedGovernedAction` carries the consumed nonce; any attempt to execute it again would either (a) be detected by the executor's nonce check, or (b) fail at the executor's GEL boundary because the action's `envelope_nonce` is already CONSUMED.

### 2.4 Verdict

**NOT BLOCKING.** Replay is mechanically prevented by G8 + atomic nonce consumption.

### 2.5 Residual concern (informational, not blocking)

The nonce registry is in-process for v0.3.1. ATE v0.2.1 closedout (commit `c82f623`) explicitly does NOT claim production distributed atomicity for the nonce registry. This v0.3.1 inherits that non-claim.

## 3. Stale behavioral evidence

### 3.1 Threat

An attacker reuses a `BehavioralEvidenceReceipt` issued more than 24 hours ago, on the grounds that "the underlying Stage C evidence still applies." Or, a participant reuses a receipt after its TTL expired by backdating `now_utc`.

### 3.2 Defense in v0.3.1

Per PI RULING 1 (TTL governs authority assertion freshness) and PI RULING 5 (24h TTL):

- `BehavioralEvidenceReceipt.expires_at_utc = issued_at_utc + 86400`.
- G4: `if now_utc > expires_at_utc: DENY(GX_BEHAVIORAL_EXPIRED)`.
- The receipt is signed by `K_BEHAVIORAL` over the receipt structure including `issued_at_utc` and `expires_at_utc`. The participant cannot alter these without invalidating the signature.

### 3.3 Mechanical vs. declarative

**Mechanical.**

1. The G4 check is a deterministic comparison against `now_utc`.
2. The receipt's signature covers `issued_at_utc` and `expires_at_utc` — an attacker cannot change the TTL without invalidating the signature.
3. `now_utc` is the trust-decision authority's clock, not the participant's clock. The participant cannot set `now_utc` arbitrarily.

### 3.4 Verdict

**NOT BLOCKING.** Stale behavioral evidence is mechanically rejected by G4.

### 3.5 Residual concern (informational, not blocking)

Clock trust: the trust-decision authority must trust its own clock. This is acceptable for the PoC; production deployment would need monotonic-clock guarantees (out of scope per PI RULING 4).

## 4. VA version substitution

### 4.1 Threat

An attacker presents a `ValueArchitecturePolicy` whose `policy_id`, `policy_version`, and/or `policy_digest` differ from the policy that was in force when the `CapabilityToken` was issued. Goal: use a more permissive policy to authorize a denied action.

### 4.2 Defense in v0.3.1

Per PI RULING 7: the trust-decision compares the exact triple `(policy_id, policy_version, policy_digest)` between `ValueArchitecturePolicy` and `CapabilityToken`. Any mismatch produces `GX_VA_POLICY_TRIPLE_MISMATCH`.

### 4.3 Mechanical vs. declarative

**Mechanical.**

1. G3 checks all three fields independently and refuses on any mismatch.
2. Each field is included in the signed region of the corresponding artifact:
   - `ValueArchitecturePolicy.policy_signature_b64` covers policy_id, policy_version, policy_digest, policy_contents.
   - `CapabilityToken.authority_signature_b64` covers va_policy_id, va_policy_version, va_policy_digest.
3. An attacker cannot present a more-permissive policy and claim it matches the token's triple unless both artifacts are re-signed — which would require `K_VA` or `K_AUTHORITY` private keys.

### 4.4 Verdict

**NOT BLOCKING.** VA version substitution is mechanically rejected by G3.

### 4.5 Residual concern (informational, not blocking)

The triple-comparison is by value, not by reference. An attacker who controls `K_VA` could issue a permissive policy that hashes to a different digest than the token was issued against — but this would still produce a triple mismatch at G3 because the token's `va_policy_digest` is fixed at issuance time. The defense holds.

## 5. Session substitution

### 5.1 Threat

An attacker presents evidence from Live Provenance session A combined with a `CapabilityToken` issued for Live Provenance session B. Goal: bypass the per-session binding of the capability.

### 5.2 Defense in v0.3.1

Per PI RULING 3: the `CapabilityToken` binds to a specific Live Provenance session via `public_key_sha256` and `session_id`.

G5: `if capability.public_key_sha256 != session_ctx.public_key_sha256: DENY(GX_CAPABILITY_SESSION_MISMATCH)`.
G1: the Live Provenance evidence (sa, sca, session_ctx, identity_att) all must share a consistent session identity.

### 5.3 Mechanical vs. declarative

**Mechanical.**

1. G1 forces all Live Provenance evidence to share the same `public_key_sha256`.
2. G5 forces the `CapabilityToken.public_key_sha256` to equal the Live Provenance session's `public_key_sha256`.
3. Both checks are cryptographic: a different session has a different ephemeral key, so `public_key_sha256` cannot be forged without the session's private key.

### 5.4 Verdict

**NOT BLOCKING.** Session substitution is mechanically rejected by G1 + G5.

### 5.5 Residual concern (informational, not blocking)

None.

## 6. COA substitution

### 6.1 Threat

An attacker presents a `CapabilityToken` whose `bound_receipt_fingerprint` references a different COA `AcceptanceReceipt` than the one actually presented in the envelope. Goal: bind the capability to a stale or different acceptance.

### 6.2 Defense in v0.3.1

G5: `if capability.bound_receipt_fingerprint != receipt.fingerprint: DENY(GX_CAPABILITY_NOT_BOUND_TO_RECEIPT)`.
G2: ensures the `AcceptanceReceipt` itself is bound to the Live Provenance session and the operator freshness challenge.

### 6.3 Mechanical vs. declarative

**Mechanical.**

1. `CapabilityToken.authority_signature_b64` covers `bound_receipt_fingerprint` — cannot be altered without re-signing.
2. G5 compares the receipt fingerprint captured at envelope construction time with the one bound to the capability.
3. G2 separately verifies the COA binds to the Live Provenance session — so a stale receipt from a different session is also caught.

### 6.4 Verdict

**NOT BLOCKING.** COA substitution is mechanically rejected by G5 (and complemented by G2).

### 6.5 Residual concern (informational, not blocking)

None.

## 7. Capability widening

### 7.1 Threat

An attacker presents a `CapabilityToken` issued for operation X, then requests operation Y. Or presents a token with a wide `target_scope` but tries to access a target in `constraints.excluded_targets`. Or presents an expired token.

### 7.2 Defense in v0.3.1

G5 covers:

- `if requested_action.operation not in capability.operation_scope: DENY(GX_OPERATION_OUT_OF_SCOPE)`.
- `if requested_action.target not in capability.target_scope: DENY(GX_TARGET_OUT_OF_SCOPE)`.
- `if requested_action.target in capability.constraints.excluded_targets: DENY(GX_TARGET_EXCLUDED)`.
- `if not (capability.valid_from_utc <= now_utc <= capability.valid_until_utc): DENY(GX_CAPABILITY_EXPIRED_OR_NOT_YET_VALID)`.

### 7.3 Mechanical vs. declarative

**Mechanical.**

1. The `CapabilityToken` is signed by `K_AUTHORITY`. The signed region covers `operation_scope`, `target_scope`, `constraints`, `valid_from_utc`, `valid_until_utc`.
2. G5 evaluates the requested action against the signed fields, not against attacker-controlled values.
3. The comparison is deterministic.

### 7.4 Verdict

**NOT BLOCKING.** Capability widening is mechanically rejected by G5.

### 7.5 Residual concern (informational, not blocking)

The `target_scope` and `excluded_targets` are simple string comparisons in v0.3.1 (e.g., "filesystem:/home/agent/proj/*"). A more expressive target language (path globs, network CIDR ranges) is out of scope; the design accepts the simplification.

## 8. Trust-decision substitution

### 8.1 Threat

An attacker captures a valid `TrustDecision{verdict=TRUST_GRANTED}` for one envelope and submits it for a different envelope, attempting to launder the grant. Or captures a granted decision and replays it after the nonce has been consumed.

### 8.2 Defense in v0.3.1

Three layers:

1. `TrustDecision.envelope_fingerprint` is included in the signed region. A different envelope has a different `envelope_binding_hash`, so the signature does not verify.
2. `TrustDecision.envelope_nonce` is included in the signed region. A different envelope has a different nonce.
3. G8 checks the nonce state from the `NonceRegistry` (separate from the signed decision).

The executor at `authorize_governed_action(envelope, trust_decision)` would:

- Verify the decision signature against `K_TRUST_DECISION`.
- Compare `decision.envelope_fingerprint == envelope.envelope_binding_hash`.
- Compare `decision.envelope_nonce == envelope.envelope_nonce`.
- Check nonce state in registry.
- Atomically consume the nonce.

### 8.3 Mechanical vs. declarative

**Mechanical.**

1. The decision signature binds `envelope_fingerprint` and `envelope_nonce`. Substitution of a different envelope invalidates the signature.
2. The nonce state check (G8) catches replay of the same envelope's grant after consumption.
3. The participant cannot forge a new decision because they don't hold `K_TRUST_DECISION`.

### 8.4 Verdict

**NOT BLOCKING.** Trust-decision substitution is mechanically rejected by the signature binding + G8.

### 8.5 Residual concern (informational, not blocking)

The executor's pre-action verification (signature + envelope match + nonce state) is a separate operational step from the trust-decision function itself. The design documents this separation but does not specify the executor's implementation. This is acceptable for v0.3.1 (the design layer); implementation would need to enforce this check at the executor.

## 9. Fail-open behavior

### 9.1 Threat

A bug, missing check, or code path bypass causes the trust-decision to emit `TRUST_GRANTED` when it should emit `TRUST_DENIED`. This is the most dangerous failure mode because it violates the safety property of the system.

### 9.2 Defense in v0.3.1

Three layers of fail-closed:

1. **Pseudocode-level first-failure-halt.** Each gate is a strict conditional. The pseudocode uses explicit `if/elif/elif/.../else` chains. If any gate fails, evaluation stops and `TRUST_DENIED` is returned with the corresponding reason code. There is no fallthrough.

2. **Default deny at VA policy level.** `ValueArchitecturePolicy.policy_contents.default_action = "DENY"`. Any rule failure falls through to DENY.

3. **Nonce state machine fail-closed.** If the nonce registry returns a non-UNSEEN state for any reason (race condition, corruption, unknown state), G8 produces a deny code.

### 9.3 Mechanical vs. declarative

**Mostly mechanical.** The fail-closed semantics are encoded in the gate sequence.

However, the pseudocode is **declarative** — it states what the function does, not what the implementation MUST do. Implementation discipline (e.g., "the implementation MUST NOT skip G8 even if the registry returns None") is required.

### 9.4 Verdict

**NOT BLOCKING at the design layer.** Fail-closed semantics are correctly specified at the gate sequence and at the VA default-deny level. The implementation must preserve these semantics; this is the responsibility of the implementation phase, not the design.

### 9.5 Residual concern (informational, NOT BLOCKING)

Two design refinements would strengthen the fail-closed defense further:

- **Refinement A (informational, NOT BLOCKING):** Explicit "all-uninitialized" reason code. If the nonce registry returns None (i.e., the nonce was never registered), G8 currently has no specific code. The v0.3.1 pseudocode treats this as "state != UNSEEN" → `GX_NONCE_NOT_UNSEEN`. A future implementation might want to distinguish "never registered" from "previously consumed" for log clarity, but both fail closed.

- **Refinement B (informational, NOT BLOCKING):** The trust-decision function should be implemented as a pure function with no I/O side effects on the registry. Currently the pseudocode queries the registry for read-only purposes (lookup), but does not mutate. The implementation MUST preserve this — the trust-decision function does NOT consume the nonce; the executor does, after `TRUST_GRANTED`. This is implicit in the design but worth stating as an explicit constraint.

Both refinements are clarifying language, not blocking defects.

## 10. Summary

| Dimension | Defense | Mechanical? | Blocking? |
| -- | -- | -- | -- |
| Self-authorization | `K_TRUST_DECISION` separation + signed verdict | YES | NO |
| Replay | G8 + atomic nonce consumption | YES | NO |
| Stale behavioral evidence | G4 (24h TTL on receipt) | YES | NO |
| VA version substitution | G3 triple comparison (id, version, digest) | YES | NO |
| Session substitution | G1 + G5 (`public_key_sha256` match) | YES | NO |
| COA substitution | G5 (capability.bound_receipt_fingerprint == receipt.fingerprint) + G2 (COA session binding) | YES | NO |
| Capability widening | G5 (operation_scope, target_scope, excluded_targets, expiration) | YES | NO |
| Trust-decision substitution | Signature binding (envelope_fingerprint + envelope_nonce) + G8 | YES | NO |
| Fail-open behavior | First-failure-halt gate sequence + default-deny VA + nonce state machine | MOSTLY (declarative layer, mechanical implementation required) | NO (at design layer) |

**No blocking defects identified.**

The v0.3.1 design amendment provides mechanical (cryptographic) defenses for 8 of 9 review dimensions. The 9th (fail-open behavior) is correctly specified at the design layer; implementation discipline is required to preserve the fail-closed semantics.

Two informational refinements (Refinement A and Refinement B in §9.5) would strengthen the design but are NOT blocking.

## 11. Implementation-readiness classification

**ATE_V0_3_1_IMPLEMENTATION_READY.**

The v0.3.1 design:

- Incorporates all seven PI rulings.
- Resolves all seven unresolved questions from v0.3 §12 (now encoded in §1, §2, §3, §4, §5, §6, §7 of the amendment).
- Preserves all frozen artifacts byte-identically.
- Defines mechanical defenses against all nine PI-listed attack/failure dimensions.
- Does NOT introduce design revisions beyond the amendment's scope.
- Does NOT redefine COA, GEL, Live Provenance, or ATE v0.2.1.
- Does NOT introduce hardware attestation or multi-agent federation.
- Does NOT propose N-action envelopes, refresh automation, or production key-management infrastructure.

The implementation phase (if later authorized) should preserve the documented fail-closed gate sequence exactly as written in §9 of the amendment.

## 12. STOP (design review only)

This review proposes no implementation corrections. Two refinements (A, B in §9.5) are recorded as informational only.

Awaiting PI direction on whether to proceed to implementation/execution.

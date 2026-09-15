# ATE v0.3.1 — Closeout Amendment (PI HOLD on Case B at commit c7726c5)

**Status:** ATE_V0_3_1_END_TO_END_TRUST_ESTABLISHED
**Date:** 2026-09-15
**Authority:** Frank Ventura (PI), per directive of 2026-09-15 (PI REVIEW: HOLD on commit `c7726c5`; SURGICAL DETERMINISTIC CORRECTION ONLY authorized; NO MODEL CALLS; preserve original `c7726c5` unchanged).

## 1. Root cause of original Case B G3 failure at `c7726c5`

The original Case B at commit `c7726c5` requested `operation=DELETE_FILE`. The frozen ValueArchitecturePolicy (Rule R1) carries an operation allowlist of `["READ", "WRITE_SCOPED", "EXECUTE_SCOPED"]`. `DELETE_FILE` is not in that allowlist, so VA Rule R1 rejects the request at **G3 (GX_VA_POLICY_INCOMPATIBLE)** BEFORE G5 (authorization scope) is reached.

This **confounded** the frozen Case B proposition: "valid identity + governance + VA + behavioral evidence + provenance, but requested action outside CapabilityToken authorization scope." At `c7726c5`, the G3 VA check failed first; the G5 capability-scope check was never exercised.

A second confound: the original Case B reused Case A's envelope, including Case A's **consumed nonce**. The PI HOLD flagged this as well — Case B's initial state was already `CONSUMED`, so the G8 check would not have been exercised independently even if the prior gates had passed.

Both confounds are documented in this amendment; the original `c7726c5` evidence is **preserved unchanged** for audit traceability.

## 2. Correction strategy (surgical, no model calls)

A new deterministic harness `run_case_b_v2` (and the inline v2 build) exercises the intended G5 scope proposition with:

| Gate | Required state | How the correction ensures it |
| -- | -- | -- |
| G1 Live Provenance | PASS | unchanged `sa` / `sca` / `session_ctx` (reused from Case A artifacts) |
| G2 COA | PASS | unchanged `receipt` (signature remains valid) |
| G3 VA compatibility | PASS | requested `operation` is `WRITE_SCOPED`, which is in both VA Rule R1 allowlist and `capability.operation_scope`. `data_class=NONE` (not in R2 denylist); `harm_potential=1` (<= R3 threshold). |
| G4 Behavioral evidence | PASS | unchanged `BehavioralEvidenceReceipt` |
| G5 authorization scope | **FAIL** with scope-specific code | requested `target` is `filesystem:/home/agent/other/file.txt`, which is NOT in `capability.target_scope` and NOT in `capability.constraints.excluded_targets`. |

Independent envelope_nonce: a fresh nonce `ate-v031-nonce-caseB-v2-001` is used. The CapabilityToken is re-signed by K_AUTHORITY with the new nonce so its signature remains valid. The fresh nonce is registered in the registry as `NONCE_UNSEEN` BEFORE trust_decide, so G8 sees a clean initial state.

## 3. Corrected Case B — gate trace

`trust_decide(envelope_b_corrected, ...)` evaluates gates G1 through G8:

| Gate | Result | Detail |
| -- | -- | -- |
| G1_RUNTIME_BINDING | PASS | sa/sca/session_ctx/identity_att pubkey_sha256 all match; freshness_challenge matches; event_source=HERMES_MODEL_RESPONSE; sca.session_acceptance_fingerprint == sa.session_acceptance_fingerprint |
| G2_COA_BINDING | PASS | K_TGE signature on receipt verifies; receipt.session_id == session_ctx.session_id; receipt.public_key_sha256 matches; receipt freshness matches; receipt not expired; receipt.session_acceptance_fingerprint == sa.session_acceptance_fingerprint |
| G3_VA_COMPATIBILITY | PASS | operation=WRITE_SCOPED ∈ VA R1 allowlist; data_class=NONE ∉ VA R2 denylist; harm_potential=1 <= VA R3 threshold=3 |
| G4_BEHAVIORAL_EVIDENCE | PASS | K_BEHAVIORAL signature verifies; status=PASS_BEHAVIORAL; agent_identity_fingerprint matches identity.public_key_sha256; receipt not expired (within 24h TTL) |
| G5_CAPABILITY_SCOPE | **FAIL** | requested target `filesystem:/home/agent/other/file.txt` ∉ `capability.target_scope = ["filesystem:/home/agent/proj/file.txt"]`; not in `excluded_targets` either. Reason: `GX_TARGET_OUT_OF_SCOPE`. |

G6, G7, G8 not reached (G5 fail-closed halts evaluation).

**Verdict:** `TRUST_DENIED`, reason `GX_TARGET_OUT_OF_SCOPE`.
**Decision signature:** verifies under K_TRUST_DECISION.

## 4. Corrected Case B — nonce pre/post state

| Stage | State |
| -- | -- |
| Pre-trust_decide (after `nonce_registry.register(fresh_nonce)`) | `NONCE_UNSEEN` |
| Post-trust_decide (no execution) | `NONCE_UNSEEN` (purity preserved) |

The nonce state is identical pre and post trust_decide. The executor is never invoked (denied decision). Nonce remains `NONCE_UNSEEN` — no consumption occurred.

## 5. Corrected Case B — required-result checklist (per directive)

| Required | Result |
| -- | -- |
| G1 PASS | ✓ |
| G2 PASS | ✓ |
| G3 PASS | ✓ |
| G4 PASS | ✓ |
| authorization/scope gate FAIL | ✓ (G5 FAIL with `GX_TARGET_OUT_OF_SCOPE`) |
| TRUST_DENIED | ✓ |
| scope-specific reason code | ✓ (`GX_TARGET_OUT_OF_SCOPE`, one of the three frozen scope codes) |
| no governed action executed | ✓ |
| nonce not consumed | ✓ (`NONCE_UNSEEN` → `NONCE_UNSEEN`) |
| Case A unchanged at `c7726c5` | ✓ (preserved byte-identically) |
| Case C unchanged at `c7726c5` | ✓ (preserved byte-identically) |

## 6. Zero model calls (per directive)

This amendment invokes **no** model calls, no participants, no evaluators, no providers, no replication. The corrected Case B uses the same deterministic harness pattern as the original `c7726c5` diagnostic — fixture keys, locally-generated Live Provenance artifacts, deterministic tampering. Only the request target and the envelope_nonce are changed; all signing keys are the same fixtures.

## 7. ATE v0.3.1 provenance clarification (per directive)

The ATE v0.3.1 integration run (at `c7726c5` and this amendment) used **deterministic / local Live Provenance fixtures** derived from the already-established Live Provenance primitive (Live Provenance PoC v0.2.1 LIVE_PROVENANCE_POC_PRIMITIVE_ESTABLISHED, commit `e5c7a39`). The ATE integration did **NOT independently repeat** the live-model provenance experiment. The Live Provenance artifacts in the ATE diagnostic are local reproductions that share the same cryptographic shape and signing pattern as the frozen Live Provenance primitive. This is consistent with the PI directive for the ATE v0.3.1 phase ("Use the minimum real model interaction required by the frozen design").

## 8. Files changed (this amendment only — original `c7726c5` not modified)

| File | Change | SHA-256 |
| -- | -- | -- |
| `implementation_v031/diagnostic_runner.py` | MODIFIED — added `run_case_b_v2` (the corrected Case B harness) + comments documenting the original Case B confound | `185b6fe549cd1c5d1712fde813a4c28cc0d0d2b64988be57ca394854f602886f` |
| `implementation_v031/evidence/case_b_corrected_evidence.json` | NEW — corrected Case B gate trace + nonce pre/post + decision fingerprint + decision_signature_ok | `32f0b5dccb0ce56f6a8a6e91343d5d6566ec0f2eea8caa30ca4c7df18e62049c` |
| `architecture/experimental/ate-poc-v0.2.1/ATE-POC-V0.3.1-CLOSEOUT-AMENDMENT.md` | NEW — this amendment | (this commit) |

## 9. Original `c7726c5` evidence preservation

All evidence files at `c7726c5` are preserved byte-identically:

- `implementation_v031/evidence/diagnostic_evidence.json` SHA-256 (file): `9bcc5190c5376d761008b34a6eb66c301053aebfd95943b86712343042573fad`
- `implementation_v031/evidence/diagnostic_log.txt` SHA-256: `c9418387733030aea889ec3b114cc6f5178be32b2b742a7dfb9b61e84e92e66c`
- `implementation_v031/crypto_utils.py` SHA-256: `331d20cb8e9351a7225da606897c5c13612e927b685be3dc41686c361d2612dd` (UNCHANGED at this commit; modified only in the v0.3.1 closeout documentation table)
- `implementation_v031/trust_decision.py` SHA-256: `8cdafc44c8b6752414afed75c45d46ada0094d023b44af051521108e2417661f` (UNCHANGED)
- `implementation_v031/executor.py` SHA-256: `d37fb939606d9f74a209bbf24b023847ec0ac900194b0456cbb3bd1dc484e158` (UNCHANGED)
- All frozen design/freeze artifacts preserved byte-identically (verified at this commit).

## 10. Final classification

**ATE_V0_3_1_END_TO_END_TRUST_ESTABLISHED**

The corrected Case B demonstrates that the ATE v0.3.1 trust-decision function correctly:

1. Permits G1–G4 to pass for a valid Live Provenance / COA / VA / behavioral evidence chain.
2. Refuses the trust decision at G5 with the scope-specific code `GX_TARGET_OUT_OF_SCOPE` when the requested target is outside `CapabilityToken.target_scope`.
3. Does NOT execute any governed action.
4. Does NOT consume the envelope nonce.

Combined with Case A (TRUST_GRANTED + nonce consumption + replay denial) and Case C (binding-break denial with G2 fail), the corrected three-case diagnostic fully exercises the ATE v0.3.1 design proposition: a deterministic, evidence-backed trust decision is produced end-to-end for one specific governed action, and the resulting action is bound to that decision via nonce consumption.

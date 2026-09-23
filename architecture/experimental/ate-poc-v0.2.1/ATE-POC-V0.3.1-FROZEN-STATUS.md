# ATE v0.3.1 — Frozen Status

**Status:** ATE_V0_3_1_END_TO_END_TRUST_ESTABLISHED
**Date:** 2026-09-15
**Authority:** Frank Ventura (PI), per directive of 2026-09-15
  (PI REVIEW: ACCEPTED of commit `912aa3f`; DOCUMENTATION/FREEZE ONLY
  authorized; NO FURTHER EXPERIMENTAL EXECUTION; NO MODEL CALLS).

## 1. Final status

**ATE_V0_3_1_END_TO_END_TRUST_ESTABLISHED**

The Agent Trust Envelope v0.3.1 is established at Proof-of-Concept level
as an integrated end-to-end trust-decision mechanism that produces a
deterministic, evidence-backed binary trust decision (TRUST_GRANTED or
TRUST_DENIED with a machine-readable reason code) for one specific
governed action, and binds the resulting action to that decision via
single-use nonce consumption.

## 2. Controlling commits

| Phase | Commit | SHA-256 (short) |
| -- | -- | -- |
| Design / amendment / adversarial review | `b9c286f` | `b9c286f` |
| Original implementation + three-case diagnostic (with confounded Case B) | `c7726c5` | `c7726c5` |
| Case B surgical correction + closeout amendment | `912aa3f` | `912aa3f` |

## 3. Controlling evidence

| Evidence | SHA-256 (file) |
| -- | -- |
| Original diagnostic evidence (`evidence/diagnostic_evidence.json`) | `9bcc5190c5376d761008b34a6eb66c301053aebfd95943b86712343042573fad` |
| Original diagnostic log (`evidence/diagnostic_log.txt`) | `c9418387733030aea889ec3b114cc6f5178be32b2b742a7dfb9b61e84e92e66c` |
| Corrected Case B evidence (`evidence/case_b_corrected_evidence.json`) | `32f0b5dccb0ce56f6a8a6e91343d5d6566ec0f2eea8caa30ca4c7df18e62049c` |

## 4. Scope of the established claim

ATE v0.3.1 is established at Proof-of-Concept level as the following
specific claim:

> Given a bound Live Provenance session, an accepted COA receipt
> matching that session, a Value Architecture policy whose
> (policy_id, policy_version, policy_digest) triple matches the
> CapabilityToken's triple, a BehavioralEvidenceReceipt asserting
> PASS_BEHAVIORAL within its 24-hour TTL, and a CapabilityToken whose
> operation_scope and target_scope cover the requested action — a
> determinstic trust-decision function, signed by an independent
> trust-decision authority (K_TRUST_DECISION, NOT held by the
> participant agent), produces a single binary verdict (TRUST_GRANTED
> or TRUST_DENIED) plus a machine-readable reason code, and the
> resulting governed action is cryptographically bound to that
> decision via atomic single-use envelope-nonce consumption
> (UNSEEN → AUTHORIZED → CONSUMED).

The successful three-case diagnostic demonstrates:

- All eight gates (G1..G8) execute deterministically against fixture
  keys and locally-generated evidence.
- Every gate fails closed with a specific machine-readable reason
  code on any anomaly.
- `trust_decide()` is pure and non-mutating (Refinement B).
- Nonce consumption happens ONLY in the executor (Refinement B).
- Replay of a consumed envelope is rejected at G8 with
  `GX_NONCE_PREVIOUSLY_CONSUMED`.
- The participant agent cannot self-certify its own TRUST_GRANTED
  (K_TRUST_DECISION is a separate authority fixture; PI RULING 4).
- Distinct nonce states (NONCE_UNKNOWN / NONCE_UNSEEN / NONCE_AUTHORIZED
  / NONCE_CONSUMED) are distinguishable in evidence (Refinement A).

## 5. Explicit non-claims

ATE v0.3.1 does NOT prove:

1. **Live Provenance was reused through deterministic/local fixtures
   derived from the separately established Live Provenance PoC.**
   This integration diagnostic did NOT independently repeat the
   live-model provenance experiment. The Live Provenance artifacts
   (IdentityAttestation, SessionContext, SessionAcceptance,
   SignedCandidateAction) used in the ATE diagnostic are local
   reproductions that share the same cryptographic shape and signing
   pattern as the frozen Live Provenance primitive at commit
   `e5c7a39` (LIVE_PROVENANCE_POC_PRIMITIVE_ESTABLISHED). The live-model
   run remains authoritative; this ATE integration did not re-execute
   it.

2. **Fixture key custody is not production key management.** All keys
   (K_IDENTITY, K_TGE, K_VA, K_BEHAVIORAL, K_AUTHORITY, K_TRUST_DECISION)
   are in-process Ed25519 fixtures generated at the start of each
   diagnostic run. Production key custody, rotation, HSM integration,
   and PKI are explicitly out of scope per PI RULING 4.

3. **Three diagnostic cases do not establish universal attack
   resistance.** The three frozen cases (A: GRANT, B: scope DENY,
   C: binding DENY) demonstrate the ATE v0.3.1 trust-decision mechanism
   is mechanically wired and correctly emits the frozen reason codes
   on the specific tamper conditions enumerated in v0.3.1 design §12.
   They do not constitute a security proof, a vulnerability assessment,
   or a penetration test.

4. **Multi-agent federation is out of scope.** Single agent, single
   session.

5. **Hardware attestation is out of scope.** No TPM, no enclave, no
   remote attestation. The frozen threat model explicitly excludes
   hardware-rooted identity.

6. **Revocation infrastructure is out of scope.** No CRL, no OCSP, no
   certificate status checking.

7. **Production policy distribution is out of scope.** VA policies are
   pre-built and signed by fixture keys. No policy retrieval, no policy
   registry, no policy versioning service.

8. **N-action envelopes are out of scope.** One governed action per
   envelope (PI RULING 6).

9. **Behavioral evidence refresh automation is out of scope.** A
   BehavioralEvidenceReceipt is valid for 24 hours from issuance.
   Re-issuance requires K_BEHAVIORAL (PI RULING 5). No automatic
   refresh; no refresh policy.

10. **The in-process nonce registry is not a distributed nonce
    service.** Atomicity is in-process; production distributed
    atomicity is not claimed.

11. **GEL v0.2.2 is reused without modification.** ATE v0.3.1 did not
    evaluate GEL gates or modify GEL behavior. Executed-action
    evaluation remains the responsibility of the downstream executor
    using GEL v0.2.2 (SHA-256 `dfcf2514...`).

## 6. Corrected three-case disposition

| Case | Verdict | Reason code | Gate that failed | Nonce transition | Governed action |
| -- | -- | -- | -- | -- | -- |
| **A** (valid chain / permitted action) | `TRUST_GRANTED` | `GX_OK` | none — all 8 gates PASS | `NONCE_UNSEEN → NONCE_UNSEEN` (post-trust_decide purity) → `NONCE_AUTHORIZED` (executor entry) → `NONCE_CONSUMED` (executor exit) | exactly one `WRITE_SCOPED` on `filesystem:/home/agent/proj/file.txt` executed |
| **B** (corrected, action outside authorization scope) | `TRUST_DENIED` | `GX_TARGET_OUT_OF_SCOPE` | G5 | `NONCE_UNSEEN → NONCE_UNSEEN` (no execution) | none |
| **C** (broken provenance/COA binding) | `TRUST_DENIED` | `GX_COA_SESSION_MISMATCH` | G2 | `NONCE_UNSEEN → NONCE_UNSEEN` (no execution; Case C uses a fresh nonce so G8 does not fire first) | none |

**Case A replay assertion:** a deterministic second `trust_decide()` call
with the same-consumed envelope produces `TRUST_DENIED` with
`GX_NONCE_PREVIOUSLY_CONSUMED`. Replay denied. No second live governed
action attempted.

**Original Case B (preserved as historical evidence at `c7726c5`):**
The original Case B at `c7726c5` requested `operation=DELETE_FILE`,
which was rejected at G3 (`GX_VA_POLICY_INCOMPATIBLE`) before the
intended G5 scope check was reached. The original Case B also reused
Case A's already-consumed nonce. Both confounds are documented in
`ATE-POC-V0.3.1-CLOSEOUT-AMENDMENT.md` (commit `912aa3f`).

## 7. Trust-decision purity (Refinement B)

`trust_decide()` is implemented as a pure non-mutating function. The
implementation in `trust_decision.py`:

- Reads evidence; evaluates G1..G8.
- Constructs and signs a `TrustDecision` under K_TRUST_DECISION.
- Does NOT consume the authorization nonce.
- Does NOT mutate envelope state.
- Does NOT mark an action executed.
- Does NOT alter participant/session evidence.

Nonce state mutation happens ONLY in `executor.py` inside
`execute_governed_action()`, AFTER a valid `TRUST_GRANTED` decision has
been verified.

Proof captured in evidence: `nonce_pre_state == nonce_post_trust_decide_state`
(Case A: `NONCE_UNSEEN == NONCE_UNSEEN`). Field name in evidence:
`trust_decide_purity_proof` (value: `true`).

## 8. Claimant / trust-authority key separation

Six independent Ed25519 fixture keys are used:

| Key role | Used for | Held by participant? |
| -- | -- | -- |
| `K_IDENTITY` | Live Provenance session signatures (sa, sca) | YES (in this diagnostic) |
| `K_TGE` | AcceptanceReceipt signature | NO |
| `K_VA` | ValueArchitecturePolicy signature | NO |
| `K_BEHAVIORAL` | BehavioralEvidenceReceipt signature | NO |
| `K_AUTHORITY` | CapabilityToken signature (ATE v0.2.1 fixture) | NO |
| `K_TRUST_DECISION` | TrustDecision signature (PI RULING 4: separate authority fixture) | **NO** |

The participant agent does NOT hold `K_TRUST_DECISION`. Therefore the
participant cannot forge a valid `TrustDecision` signature. This
satisfies PI RULING 4 ("the participant agent must not be able to
self-certify TRUST_GRANTED").

## 9. Implementation file disposition (precise)

Per the directive ("Correct any wording ambiguity in preservation
documentation. Specifically, do NOT state that all implementation
files remained unchanged if diagnostic_runner.py changed in commit
912aa3f..."), the accurate file disposition is:

| File | SHA-256 (post-`912aa3f`) | Status |
| -- | -- | -- |
| `implementation_v031/__init__.py` | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` | UNCHANGED from `c7726c5` |
| `implementation_v031/crypto_utils.py` | `331d20cb8e9351a7225da606897c5c13612e927b685be3dc41686c361d2612dd` | UNCHANGED from `c7726c5` |
| `implementation_v031/nonce_registry.py` | `7391b1bb0f474e88e47ac218ec7a48e0e9c4cfbca3a7dd73c2ab3ace30b9df59` | UNCHANGED from `c7726c5` |
| `implementation_v031/behavioral_evidence_receipt.py` | `e953f48990907911bb065e326a2fe61b59d0d72a6beabb646c3419700a8f7cf3` | UNCHANGED from `c7726c5` |
| `implementation_v031/value_architecture_policy.py` | `99d473f335c72c9a1054bfab5e339fe9a1c30c21fb5249bcb9978644329b615d` | UNCHANGED from `c7726c5` |
| `implementation_v031/trust_decision.py` | `8cdafc44c8b6752414afed75c45d46ada0094d023b44af051521108e2417661f` | UNCHANGED from `c7726c5` |
| `implementation_v031/executor.py` | `d37fb939606d9f74a209bbf24b023847ec0ac900194b0456cbb3bd1dc484e158` | UNCHANGED from `c7726c5` |
| `implementation_v031/capture_evidence.py` | `77e0bb0ad876a38ec1764a6c61c03578735167f2d4ea5ff0f241f8ff4b3ccce4` | UNCHANGED from `c7726c5` |
| `implementation_v031/diagnostic_runner.py` | `185b6fe549cd1c5d1712fde813a4c28cc0d0d2b64988be57ca394854f602886f` | **DELIBERATELY EXTENDED** at `912aa3f` (added `run_case_b_v2`). The original `run_case_b` is preserved unchanged within the same file. |

Evidence files:

| File | SHA-256 | Status |
| -- | -- | -- |
| `implementation_v031/evidence/diagnostic_evidence.json` | `9bcc5190c5376d761008b34a6eb66c301053aebfd95943b86712343042573fad` | UNCHANGED from `c7726c5` (preserved as historical evidence, including the original confounded Case B result) |
| `implementation_v031/evidence/diagnostic_log.txt` | `c9418387733030aea889ec3b114cc6f5178be32b2b742a7dfb9b61e84e92e66c` | UNCHANGED from `c7726c5` |
| `implementation_v031/evidence/case_b_corrected_evidence.json` | `32f0b5dccb0ce56f6a8a6e91343d5d6566ec0f2eea8caa30ca4c7df18e62049c` | NEW at `912aa3f` (corrected Case B evidence) |

Documents:

| File | Status |
| -- | -- |
| `architecture/experimental/ate-poc-v0.2.1/ATE-POC-V0.3.1-CLOSEOUT.md` | UNCHANGED from `c7726c5` (preserved; documents the confounded Case B as accepted) |
| `architecture/experimental/ate-poc-v0.2.1/ATE-POC-V0.3.1-CLOSEOUT-AMENDMENT.md` | NEW at `912aa3f` (documents the confound and the corrected Case B) |
| `architecture/experimental/ate-poc-v0.2.1/ATE-POC-V0.3.1-FROZEN-STATUS.md` | NEW at this commit (this document) |

## 10. Authorization restrictions (no further work without new PI direction)

- No further ATE v0.3.1 experimental execution without new PI
  direction.
- No model calls, no provider invocation, no evaluators, no replication.
- No new tests, no new cases, no expansion of the attack matrix.
- No ATE redesign, no productionization, no successor experiment.
- No modification of frozen ATE v0.3.1 design / amendment / review /
  implementation files (modulo documentation corrections).
- Live Provenance PoC remains frozen at `e5c7a39`; no new Live
  Provenance execution without new PI direction.

## 11. STOP (documentation/freeze only)

This document is the frozen-status artifact. No implementation
changes. No execution.

Awaiting PI direction for any further work.

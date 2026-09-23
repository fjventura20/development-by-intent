# Live Provenance PoC v0.2.1 — Frozen Status

**Status:** LIVE_PROVENANCE_POC_PRIMITIVE_ESTABLISHED
**Date:** 2026-09-15
**Authority:** Frank Ventura (PI), per directive of 2026-09-15.

## 1. Live Provenance PoC status

ESTABLISHED. The accepted evidence (commit
`f51c8e6ea6e9a4d87fdf5c504668c5d172c9016d`, classification
`LIVE_PROVENANCE_TWO_TURN_BOUND`) establishes that:

- Two real MiniMax-M3 model responses traversed the configured
  Hermes production response lifecycle
  (`agent/turn_response_check.py::check_api_response`).
- The lifecycle binding point was reached for both turns.
- The lifecycle-generated evidence was bound to:
  - `event_source = HERMES_MODEL_RESPONSE`
  - the ephemeral runtime/session identity (public-key fingerprint
    `5ee7de4e6006876512ed824e79d8ba9a4a51dfed58b37079c47bcabd388b34fa`,
    session `20260915_081830_d81c9b`)
  - the operator freshness challenge
    `liveprov_a1f057cc864d72c9`
  - distinct turn IDs (`1` for Turn A, `2` for Turn B)
  - monotonically ordered lifecycle sequence values (`monotonic_seq=1`
    for Turn A, `monotonic_seq=2` for Turn B)
  - the appropriate state-machine transitions (`SESSION_STARTED` →
    `ACCEPTANCE_PENDING` → `ACCEPTANCE_ISSUED` → `ACTION_PENDING` →
    `ACTION_ISSUED`)
- Turn 1 successfully produced and verified a SessionAcceptance.
- Turn 2 successfully produced and verified a SignedCandidateAction
  bound to the Turn 1 acceptance fingerprint.
- Acceptance/action type substitution and cross-turn substitution were
  rejected.
- The simulated-response path remained unable to produce acceptable
  live-provenance evidence.

## 2. Controlling successful experiment commit

```
f51c8e6ea6e9a4d87fdf5c504668c5d172c9016d
```

## 3. Evidence SHA-256

```
ba389d6d53d166bc53daa998a4430179f044d7fb471191dbf7f83b7bb2734c29
```

Source: `architecture/experimental/live-provenance-poc/live-experiment/evidence/two_turn_option_a_evidence.json`

## 4. Scope of the demonstrated claim

The Live Provenance PoC primitive, in its established form, demonstrates
that under the PI-defined threat model — *prevent a separate same-user
process from manufacturing verifier-acceptable live provenance
artifacts without the required Hermes model-turn events occurring in
the bound live session* — the following invariants hold:

1. **Session/turn binding:** SessionAcceptance and SignedCandidateAction
   artifacts verified through `verify_live_provenance_*` are bound to
   (a) a real model response that traversed the canonical
   `agent/turn_response_check.py::check_api_response` lifecycle point,
   (b) the ephemeral runtime/session identity captured at session
   start, (c) the operator-supplied freshness challenge, (d) a
   monotonically ordered lifecycle sequence value, and (e) the
   required state-machine transitions.
2. **Cross-turn non-substitutability:** Turn 1's acceptance artifact
   cannot substitute for Turn 2's action artifact and vice versa.
   This is enforced by domain separation
   (`SESSION_ACCEPTANCE` vs `SESSION_ACTION` preimage prefix),
   cross-domain verification rejection, prior-fingerprint chaining
   (`sca.session_acceptance_fingerprint == sa.session_acceptance_fingerprint`),
   and distinct turn IDs / channel proofs.
3. **Simulated-response rejection:** The simulated/test path
   (`record_simulated_test_response`, `event_source=SIMULATED_TEST_RESPONSE`)
   cannot produce verifier-valid live-provenance artifacts. The
   issuance functions refuse to construct an artifact when the
   recorded event source is not `HERMES_MODEL_RESPONSE`.
4. **Per-session ephemeral identity:** The ephemeral public/private
   keypair is generated inside the running Hermes process, never
   persisted to disk, never logged, and is associated with exactly
   one `session_id`. Sessions are cryptographically distinct (different
   public keys for different sessions).

## 5. Explicit non-claims / limitations

The PoC does **NOT** establish, and the established classification does
**NOT** claim:

1. **Defense against root/administrator compromise.** Out of scope per
   threat model.
2. **Defense against arbitrary code execution inside Hermes.** Out of
   scope.
3. **Defense against malicious Hermes binary modification.** Out of
   scope.
4. **Defense against process-memory extraction, debugging, ptrace, or
   equivalent same-user memory attacks.** Out of scope. The supported
   claim is only "a separate process cannot forge valid session
   provenance merely by fabricating Hermes session files, metadata,
   session IDs, or gateway records without possession of the
   session's ephemeral private key."
5. **Defense against TOCTOU between runtime attestation and action
   execution.** Out of scope.
6. **Hardware-rooted identity / TPM / enclave / remote attestation.**
   Not introduced.
7. **Out-of-band verifier.** Not introduced.
8. **Equivalence to a deep semantic understanding of the COA.** The
   PoC proves only that the bound live participant produced the
   designated acceptance response, not that the model understood it.
9. **Reproducibility across other models, providers, implementations,
   or hardware.** Not established. The accepted classification
   applies to MiniMax-M3 via `https://api.minimax.io/v1` on the
   installed Hermes runtime only.
10. **Replication under different operator-freshness challenges,
    different session ids, different OS states, or different
    prompt formats.** Not performed; per PI directive, no replication
    is authorized at this stage.

## 6. Frozen implementation artifacts and their hashes

All artifacts listed below are frozen at the specified hashes. They
are not modified by this status artifact.

### Frozen design lineage

| Artifact | SHA-256 | Commit |
| -- | -- | -- |
| LIVE-PROVENANCE-POC-DESIGN-v0.1.md | `a4f4836ac4ea0c5b62a643fec6843784f24cb9494e9a0cb5e60d36fcd329e785` | `2d8e9bc0` |
| REVIEW-LIVE-PROVENANCE-POC-DESIGN-v0.1.md | `4a855be1c12c025fb2a6b50b085a0ba8d7fe327859b35b4dfe9e5d0aae28d9f2` | `b96f7098` |
| HERMES-LIVE-PROVENANCE-CAPABILITY-AUDIT-v0.1.md | `ee3ca1281515f9a2bbda64f6b66e585cdd601db05baea6f78ff1154aa5cb6cff` | `a23addbc` |
| EPHEMERAL-SESSION-IDENTITY-PRIMITIVE-v0.1.md | `82725296f41dece0669d5aac6073748ae425af4c45bcb64f80cb12ec5308edab` | `21b23def` |
| EPHEMERAL-SESSION-IDENTITY-CLAIM-AMENDMENT-v0.1.md | `fab8491f1ddc0dbbf35f37d0fccff19227c068345bd5fe7669452bfbdea02eca` | `3bad12e5` |
| RUNTIME-LIFECYCLE-INTEGRATION-VERIFICATION-v0.1.md | `7816d722d11a7dbe91b23aaabe9a92fc9ed463b8c7d1fda6ffdbab59b39e7ea8` | `3bad12e5` |
| LIVE-PROVENANCE-POC-DESIGN-v0.2.md | `fc9884f5cf5d22e6ae35066fb279852b42f1472065be4657d8f744422af665dd` | `9694d145` |
| REVIEW-LIVE-PROVENANCE-POC-DESIGN-v0.2.md | `bdae161e4d19a42976a25330189d0b5993c5e2d7b6cf3d7f17c2c65f0ba8faa7` | `445be56a` |
| LIVE-PROVENANCE-POC-DESIGN-v0.2.1.md | `df7f474bed24ca36ee9398912d13407c32a8cd9afba25cf8e89eb9bf47c61ac0` | `9ac3f370` |
| REVIEW-LIVE-PROVENANCE-POC-DESIGN-v0.2.1.md | `3a59ee7ee5fbf981e290d44dc6806350cb75d65b93b42cf87b30bbd9e0bd1be8` | `1a5574e8` |

### Frozen implementation closeouts

| Artifact | SHA-256 | Commit |
| -- | -- | -- |
| RUNTIME-ISSUANCE-POC-CLOSEOUT-v0.1.md | `00975514b0f66c43ce0e4910f63ca739f9dcc5fe228e6c72ce343386c40b45c6` | `a256b9f1` |
| MODEL-RESPONSE-LIFECYCLE-BINDING-POC-CLOSEOUT-v0.1.md | `a4267f35e5c235b83fc86cf50f0266a6bb6de6e1011e93b4a73807273df2fddc` | `f21b346` |
| LIVE-PROVENANCE-TWO-TURN-CLOSEOUT-v0.1.md (first inconclusive run; preserved as historical evidence) | `dddb784f0be171ea7fcaa225d94a09a5c36a97acad8e22fc929bd8cca8e39568` | `2501529` |
| PROVIDER-PATH-PREFLIGHT-v0.1.md | `6c3a71a111b96a6f6de96ca0c51070dff900ac61280c150ec5f95eea4f163cb0` | `18d9c27` |
| LIVE-PROVENANCE-TWO-TURN-OPTION-A-CLOSEOUT-v0.1.md (the controlling successful experiment) | (SHA computed at commit `f51c8e6`) | `f51c8e6` |
| LIVE-PROVENANCE-POC-V0.2.1-SANITATION-AMENDMENT-v0.1.md (this status commit) | (SHA computed at this commit) | this commit |

### Frozen evidence

| Artifact | SHA-256 |
| -- | -- |
| `live-experiment/evidence/two_turn_option_a_evidence.json` | `ba389d6d53d166bc53daa998a4430179f044d7fb471191dbf7f83b7bb2734c29` |
| `live-experiment/evidence/two_turn_evidence.json` (first inconclusive run, preserved) | `c2e668237117550f819b0149aad5bfe9940bc84e8b0be1d10c523531a5e79171` |

### Frozen implementation (Hermes install + worktree mirror)

| File | SHA-256 |
| -- | -- |
| hermes-patch/ephemeral_session_id_poc.py | `76128c6974e71aeddbd70250e21194834285707c1d5678640d9189806262f1d7` |
| hermes-patch/ephemeral_runtime_issuance_poc.py | `b8e5eb7257dbd7570e1473f297ee2ddbbe13d90733d426d0d8b8865771415888` |
| hermes-patch/hermes-diff.patch | `9f296f147a25bbe82dad5ab74789d56911198eca40bc596a4222b5399f31f981` |

Hermes install (live, all unmodified through the accepted experiment):
- `ephemeral_session_id_poc.py` — `76128c69...f1d7`
- `ephemeral_runtime_issuance_poc.py` — `b8e5eb72...5888`
- `cli_session_mixin.py` — `2b035ba4...e1fc`
- `config_defaults.py` — `7908f904...775a`
- `turn_response_check.py` — `497b8eed...1c25`
- `cli.py` — `911cd2bc...5978`

## 7. Prior inconclusive execution preserved

The earlier execution at commit `2501529` is preserved byte-identically
as historical evidence. Its classification
(`INCONCLUSIVE_STOPPED_BEFORE_DETERMINATION`) and stop condition (HTTP
404 on the configured provider endpoint) remain part of the
historical record. It is NOT overwritten, reinterpreted, or replaced.

## 8. No further Live Provenance experimentation authorized

Without new PI direction, no additional Live Provenance replication,
larger test matrix, additional providers, additional models, premium
evaluator engagement, or hardware-attestation work is authorized.

Future Live Provenance work that may proceed without additional PI
authorization:

- Documentation updates that do not change demonstrated claims.
- Re-verification that the frozen artifacts remain
  byte-identically preserved (no edits applied to them).
- Compliance improvements (e.g., the sanitation amendment at this
  commit) that do not change the implementation.

Future Live Provenance work that requires additional PI authorization:

- Any change to the demonstrated implementation.
- Any additional experiments, replications, or larger matrices.
- Any change to the threat model or to the established claim scope.
- Any productionization or operational use of the primitive.
- Any engagement with evaluators, additional providers, or alternative
  models.

## 9. STOP

This status artifact freezes the Live Provenance PoC v0.2.1 line as
ESTABLISHED. No further action is taken at this stage. Awaiting new
PI direction.

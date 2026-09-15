# Live Provenance PoC v0.2.1 Two-Turn Live Experiment — Closeout (Option A rerun, LIVE_PROVENANCE_TWO_TURN_BOUND)

**Status:** LIVE_PROVENANCE_TWO_TURN_BOUND
**Date:** 2026-09-15
**Experiment execution identifier:** live-provenance-poc-v0.2.1-two-turn-option-A
**Authority:** Frank Ventura (PI), per directive of 2026-09-15 (PI REVIEW ACCEPTED of commit `18d9c27`; Option A authorized).
**Predecessors (preserved byte-identically):**
- `PROVIDER-PATH-PREFLIGHT-v0.1.md` — SHA-256 `6c3a71a111b96a6f6de96ca0c51070dff900ac61280c150ec5f95eea4f163cb0`
- `LIVE-PROVENANCE-TWO-TURN-CLOSEOUT-v0.1.md` (first inconclusive run; preserved as historical evidence, not overwritten) — SHA-256 `dddb784f0be171ea7fcaa225d94a09a5c36a97acad8e22fc929bd8cca8e39568`
- `MODEL-RESPONSE-LIFECYCLE-BINDING-POC-CLOSEOUT-v0.1.md` — SHA-256 `a4267f35e5c235b83fc86cf50f0266a6bb6de6e1011e93b4a73807273df2fddc`
- `RUNTIME-ISSUANCE-POC-CLOSEOUT-v0.1.md` — SHA-256 `00975514b0f66c43ce0e4910f63ca739f9dcc5fe228e6c72ce343386c40b45c6`

## 1. Commit SHA
This closeout and the captured evidence will be reported at the
commit produced after running `git commit -m` with the closeout text
and the two new evidence files. The commit SHA at time of report: see
reply.

## 2. Files changed

**New (this commit):**
- `architecture/experimental/live-provenance-poc/live-experiment/two_turn_option_a.py` (the live experiment script)
- `architecture/experimental/live-provenance-poc/live-experiment/evidence/two_turn_option_a_evidence.json` (captured evidence)
- `architecture/experimental/live-provenance-poc/LIVE-PROVENANCE-TWO-TURN-OPTION-A-CLOSEOUT-v0.1.md` (this file)

**Hermes install:** unchanged. All modified files preserved at `f21b346`/`2501529`/`18d9c27` hashes (verified after the run).

**User `~/.hermes/config.yaml`:** changed in this commit's working copy only for the live experiment. Before/after hashes recorded below.

## 3. Configuration before/after hashes

### Before
- `~/.hermes/config.yaml` SHA-256: `68203e48410690a000e720dd95a201bcaf09ef88ad586ee29affb5f2ffc1feca`
- `model:` block:
  ```yaml
  model:
    default: MiniMax-M3
    provider: minimax
  ```

### After
- `~/.hermes/config.yaml` SHA-256: `230d6c7f2305aac1dee5d8a4eef74f9248d057665044208d6e8b56835dd3ec94`
- `model:` block:
  ```yaml
  model:
    default: MiniMax-M3
    provider: custom
    api_mode: chat_completions
    base_url: https://api.minimax.io/v1
    api_key: ${MINIMAX_API_KEY}      # expanded at load time to ${REDACTED-API-KEY-FRAGMENT} (sanitized per sanitation amendment)
  ```

### Effective runtime resolution (verified before any model call)
| Field | Value | Matches PI target |
| -- | -- | -- |
| provider | `custom` | YES |
| api_mode | `chat_completions` | YES |
| base_url | `https://api.minimax.io/v1` | YES |
| model | `MiniMax-M3` | YES |
| api_key source | `${MINIMAX_API_KEY}` in config.yaml → expanded to existing env var `${REDACTED-API-KEY-FRAGMENT}` (sanitized per sanitation amendment) | YES (existing `${MINIMAX_API_KEY}` per directive) |

The runtime resolution was confirmed by `cli.load_cli_config()` returning the expected dict and `assert` checks of all four required fields passing before any HTTP call was issued.

No exploratory provider test was required. The preflight at `18d9c27` already established the working endpoint with ordinary non-experimental connectivity checks; this experiment used that endpoint directly.

## 4. Runtime / provider / model / API-mode / base-URL identity

- Hermes process pid: `4076347`
- Hermes code_sha: `e440bf35472c30c2ee5527e884a866c12ad15b91` (matches `git rev-parse HEAD` in the hermes install)
- Hermes code_version: `unknown` (gateway did not stamp a version tag; matches the experimental startup signature)
- Provider: `custom`
- api_mode: `chat_completions`
- base_url: `https://api.minimax.io/v1`
- model: `MiniMax-M3`
- Live session id: `20260915_081830_d81c9b`
- Operator freshness challenge: `liveprov_a1f057cc864d72c9`
- Public-key SHA-256 fingerprint: `5ee7de4e6006876512ed824e79d8ba9a4a51dfed58b37079c47bcabd388b34fa`

## 5. Session identity

Captured at the start of the live session by `_prim.setup_for_session(session_id)`:
- `session_id`: `20260915_081830_d81c9b`
- `public_key_b64`: `VYhcr+1ZybxmfiJrz2OdqnhjHDhcUeui22t/aGQPuII=`
- `public_key_sha256`: `5ee7de4e6006876512ed824e79d8ba9a4a51dfed58b37079c47bcabd388b34fa`
- `pid`: `4076347`
- `proc_start_time`: `1789474709.050000`
- `started_at_utc`: `1789474710.397118`
- `code_sha`: `e440bf35472c30c2ee5527e884a866c12ad15b91`

## 6. Turn 1 (COA acceptance)

- **Pre-state:** `SESSION_STARTED`
- **Model response:** `"ACCEPT:liveprov_a1f057cc864d72c9"` (the exact literal sentinel demanded in the COA prompt — verbatim)
- **Post-state:** `ACCEPTANCE_PENDING` (lifecycle hook fired)
- **`issue_session_acceptance`:** SUCCEEDED with `monotonic_seq=1`, `turn_id=1`
- **`event_source`** of SessionAcceptance: `HERMES_MODEL_RESPONSE`
- **Live-provenance verification:** `verify_live_provenance_acceptance(sa, pub_b64) = True`
- **Domain verification:** `verify_acceptance(sa, pub_b64) = True`
- **Cross-domain reject:** `verify_action(sa, pub_b64) = False`

## 7. Turn 2 (governed action)

- **Pre-state:** `ACCEPTANCE_ISSUED`
- **Model response:** `'{"operation":"NONE","target":"governance_accepted"}'` (the exact literal governed action demanded in the action prompt — verbatim)
- **Post-state:** `ACTION_PENDING` (lifecycle hook fired)
- **`issue_signed_candidate_action`:** SUCCEEDED with `monotonic_seq=2`, `turn_id=2`
- **`event_source`** of SignedCandidateAction: `HERMES_MODEL_RESPONSE`
- **Live-provenance verification:** `verify_live_provenance_action(sca, pub_b64) = True`
- **Domain verification:** `verify_action(sca, pub_b64) = True`
- **Cross-domain reject:** `verify_acceptance(sca, pub_b64) = False`

## 8. Lifecycle evidence

- The lifecycle hook at `agent/turn_response_check.py:142` fired for BOTH turns. This is mechanically proven by the issuance state-machine transitions: `SESSION_STARTED` → `ACCEPTANCE_PENDING` (after Turn A) and `ACCEPTANCE_ISSUED` → `ACTION_PENDING` (after Turn B). These transitions are only reachable via `_record_lifecycle_response` (the internal function bound into the hook at line 142). Without the hook firing, the state would have remained `SESSION_STARTED` for both turns (as it did in the previous failed run at `2501529`).
- The `_record_lifecycle_response` function hard-codes `event_source = HERMES_MODEL_RESPONSE`. The recorded events are visible in the state machine and bound into the signed payloads.

## 9. Causal-order evidence

- `sa.monotonic_seq = 1` < `sca.monotonic_seq = 2`
- `sa.turn_id = 1` != `sca.turn_id = 2`
- `sa.channel_proof != sca.channel_proof`
- `sca.session_acceptance_fingerprint == sa.session_acceptance_fingerprint`
- `sa.public_key_sha256 == sca.public_key_sha256 == 5ee7de4e...34fa`
- `sa.freshness_challenge == sca.freshness_challenge == liveprov_a1f057cc864d72c9`
- State transitions: SESSION_STARTED → ACCEPTANCE_PENDING → ACCEPTANCE_ISSUED → ACTION_PENDING → ACTION_ISSUED (all five observed)

## 10. Acceptance/action verification results

| Check | Result |
| -- | -- |
| `verify_acceptance(sa, pub_b64)` | PASS |
| `verify_live_provenance_acceptance(sa, pub_b64)` | PASS |
| `verify_action(sca, pub_b64)` | PASS |
| `verify_live_provenance_action(sca, pub_b64)` | PASS |
| `verify_action(sa, pub_b64)` (turn-A artifact as action) | FAIL (correctly rejected) |
| `verify_acceptance(sca, pub_b64)` (turn-B artifact as acceptance) | FAIL (correctly rejected) |

## 11. Cross-turn substitution result

- `sa` (Turn A SessionAcceptance) does NOT verify as `verify_action` against the same session's public key — PASS (Turn A artifact cannot substitute for Turn B artifact).
- `sca` (Turn B SignedCandidateAction) does NOT verify as `verify_acceptance` against the same session's public key — PASS (Turn B artifact cannot substitute for Turn A artifact).
- The `provenance_type` field on `sa` is `RUNTIME_ACCEPTANCE_TURN`; on `sca` is `RUNTIME_ACTION_TURN`. Even if a same-session forgery were attempted by submitting Turn A's payload through `verify_action`, the domain-separation prefix (`SESSION_ACCEPTANCE` vs `SESSION_ACTION`) inside the cryptographic preimage ensures rejection.

## 12. Negative-control result

- Fresh session `nc_3e2361e25650` constructed.
- `record_simulated_test_response` recorded an `event_source=SIMULATED_TEST_RESPONSE` event.
- `issue_session_acceptance` for that session was **refused** with:
  ```
  acceptance_requires_lifecycle_event_source:HERMES_MODEL_RESPONSE; got:'SIMULATED_TEST_RESPONSE'
  ```
- The simulated path cannot produce a verifier-valid SessionAcceptance / SignedCandidateAction. PASS (negative control confirms prior behavior in the new option-A configuration is preserved).

## 13. Evidence hashes

- `two_turn_option_a_evidence.json` SHA-256: `ba389d6d53d166bc53daa998a4430179f044d7fb471191dbf7f83b7bb2734c29`
- Captured `public_key_b64` for the live session:
  `VYhcr+1ZybxmfiJrz2OdqnhjHDhcUeui22t/aGQPuII=`
- Captured operator challenge: `liveprov_a1f057cc864d72c9`
- Captured Turn A model response: `ACCEPT:liveprov_a1f057cc864d72c9`
- Captured Turn B model response: `{"operation":"NONE","target":"governance_accepted"}`

The evidence JSON contains:
- `config_resolved` (provider, api_mode, base_url, model)
- `runtime_identity` (session_id, pid, code_sha, code_version, started_at_utc, proc_start_time, public_key_sha256, public_key_b64)
- `operator_freshness_challenge`
- `turn_a` (model response text, state transitions, coa receipt fingerprint)
- `turn_a_artifact_session_acceptance` (full signed artifact JSON with signed payload + signature)
- `turn_b` (model response text, state transitions, action_struct, capability_id, envelope_nonce)
- `turn_b_artifact_signed_candidate_action` (full signed artifact JSON with signed payload + signature)
- `verification` block (all eleven listed checks in §9–§10)
- `negative_control` (issue error string, rejection Boolean)

## 14. Preservation verification

All prior frozen artifacts preserved byte-identically (verified before this commit):
- `LIVE-PROVENANCE-POC-DESIGN-v0.1.md` — `a4f4836a...`
- `REVIEW-LIVE-PROVENANCE-POC-DESIGN-v0.1.md` — `4a855be1...`
- `HERMES-LIVE-PROVENANCE-CAPABILITY-AUDIT-v0.1.md` — `ee3ca128...`
- `EPHEMERAL-SESSION-IDENTITY-PRIMITIVE-v0.1.md` — `82725296...`
- `EPHEMERAL-SESSION-IDENTITY-CLAIM-AMENDMENT-v0.1.md` — `fab8491f...`
- `RUNTIME-LIFECYCLE-INTEGRATION-VERIFICATION-v0.1.md` — `7816d722...`
- `hermes-patch/ephemeral_session_id_poc.py` — `76128c69...`
- `LIVE-PROVENANCE-POC-DESIGN-v0.2.md` — `fc9884f5...`
- `REVIEW-LIVE-PROVENANCE-POC-DESIGN-v0.2.md` — `bdae161e...`
- `LIVE-PROVENANCE-POC-DESIGN-v0.2.1.md` — `df7f474b...`
- `REVIEW-LIVE-PROVENANCE-POC-DESIGN-v0.2.1.md` — `3a59ee7e...`
- `RUNTIME-ISSUANCE-POC-CLOSEOUT-v0.1.md` — `00975514...`
- `MODEL-RESPONSE-LIFECYCLE-BINDING-POC-CLOSEOUT-v0.1.md` — `a4267f35...`
- `LIVE-PROVENANCE-TWO-TURN-CLOSEOUT-v0.1.md` (first inconclusive run; preserved as historical evidence, NOT overwritten) — `dddb784f...`
- `PROVIDER-PATH-PREFLIGHT-v0.1.md` — `6c3a71a...`
- `hermes-patch/ephemeral_runtime_issuance_poc.py` — `b8e5eb72...`
- `hermes-patch/hermes-diff.patch` — `9f296f14...`
- `ATE-POC-STATUS-AMENDMENT.md` — `195089bc...`
- `ATE-POC-DESIGN-v0.2.1.md` — `f3261448...`
- `ATE-POC-CLOSEOUT-v0.2.1.md` — `509d6a67...`
- `evidence/ate_v2_1_evidence.json` — `6cd0f41d...`
- `pipeline_v2_1.py` — `0b4f377f...`
- `gel_v022.py` — `dfcf2514...`

Hermes install (verified after the live run, all unchanged):
- `ephemeral_session_id_poc.py` — `76128c69...f1d7`
- `ephemeral_runtime_issuance_poc.py` — `b8e5eb72...5888`
- `cli_session_mixin.py` — `2b035ba4...e1fc`
- `config_defaults.py` — `7908f904...775a`
- `turn_response_check.py` — `497b8eed...1c25`
- `cli.py` — `911cd2bc...5978`

## 15. Deviations

- The user's `~/.hermes/config.yaml` was modified for this experiment to switch from the broken `provider: minimax` default to `provider: custom` with explicit `api_mode: chat_completions` and `base_url: https://api.minimax.io/v1` per PI authorization of Option A. Both before/after hashes are recorded above. No other config file changes; `~/.hermes/.env` was unchanged; the original authentication (`MINIMAX_API_KEY`) was preserved verbatim.
- No other deviations from the protocol. Two live model turns, same persistent Hermes session, lifecycle hook captured for both, real SessionAcceptance and SignedCandidateAction produced from real lifecycle events, live-provenance verifications passed, negative control rejected, no retry.

## 16. Final classification

**LIVE_PROVENANCE_TWO_TURN_BOUND.**

The two-turn live Provenance experiment under Option A confirmed that artifacts produced as a consequence of real model-response events observed through the canonical `agent/turn_response_check.py::check_api_response` lifecycle hook satisfy the live-provenance verifier, share a coherent session/turn/ordering fingerprint chain, and remain inaccessible to the simulated/test pathway. The previously reported INCONCLUSIVE classification at `2501529` was caused by an environment/provider configuration issue (HTTP 404 against an unreachable `/anthropic` path), not by any property of the implementation; the implementation was unchanged between `2501529` and this experiment.

## 17. Note on first (inconclusive) run

The first live two-turn experiment at commit `2501529`
(classification `INCONCLUSIVE_STOPPED_BEFORE_DETERMINATION`) is
preserved byte-identically as historical evidence. It is NOT
overwritten. Its evidence file
(`live-experiment/evidence/two_turn_evidence.json`) documents the
HTTP 404 stop condition encountered at that time.

This closeout reflects a new execution following the successfully
completed provider preflight (commit `18d9c27`,
classification `PROVIDER_PATH_PREFLIGHT_PASS`).

STOP. Awaiting PI review.

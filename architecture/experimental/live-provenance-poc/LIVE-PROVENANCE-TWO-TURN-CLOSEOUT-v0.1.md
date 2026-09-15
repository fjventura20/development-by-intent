# Live Provenance PoC v0.2.1 Two-Turn Live Experiment — Closeout (STOPPED BEFORE DETERMINATION)

**Status:** STOPPED BEFORE DETERMINATION
**Date:** 2026-09-15
**Authority:** Frank Ventura (PI), per directive of 2026-09-14 authorizing the actual two-turn live experiment with explicit STOP conditions.
**Predecessor (preserved byte-identically):** `MODEL-RESPONSE-LIFECYCLE-BINDING-POC-CLOSEOUT-v0.1.md` (SHA-256 `a4267f35e5c235b83fc86cf50f0266a6bb6de6e1011e93b4a73807273df2fddc`).

## 1. Final classification

**INCONCLUSIVE_STOPPED_BEFORE_DETERMINATION.**

The live two-turn experiment was stopped before any model response was received. The runtime enforcement (event_source separation) was demonstrated as a side-effect of the negative control, but the live experiment itself did not produce real model responses, real lifecycle events, real SessionAcceptance / SignedCandidateAction artifacts, or real live-provenance verification results.

## 2. Exact commit SHA
**This closeout is recorded at the same commit `f21b346` plus this file; the commit SHA will be reported after the commit-and-push below.**

## 3. Stop condition

Per PI directive: "Stop immediately on any ambiguity involving: session continuity, model-response provenance, lifecycle-hook execution, artifact-to-turn binding, verifier behavior, or frozen-protocol interpretation."

And: "Do not repair, rerun, reinterpret, or weaken a requirement after observing a failure. Preserve the evidence and report the stop condition."

### What happened

1. The experiment constructed an AIAgent with the configured provider/model:
   - provider: `minimax`
   - model: `MiniMax-M3`
   - endpoint: `https://api.minimax.io/anthropic`

2. The AIAgent constructed successfully, and the ephemeral keypair was generated for the live session. Session ID: `20260915_080913_65c6f9`.

3. **Turn A (COA acceptance)** failed with HTTP 404 after 3 retries:
   ```
   NotFoundError [HTTP 404]
   Provider: minimax  Model: MiniMax-M3
   Endpoint: https://api.minimax.io/anthropic
   Error: HTTP 404: 404 page not found
   ```

4. **Turn B (governed action)** failed with HTTP 404 after 3 retries (same error).

5. As a consequence, no real model response was received for either turn. The lifecycle hook at `agent/turn_response_check.py:142` did NOT fire (no provider response to observe). The issuance state machine remained at `SESSION_STARTED` for both turns.

6. `issue_session_acceptance` refused with `acceptance_issuance_requires_state:ACCEPTANCE_PENDING; got:SESSION_STARTED`.

7. `issue_signed_candidate_action` refused with `action_issuance_requires_state:ACTION_PENDING; got:SESSION_STARTED`.

8. **Negative control** (separate session using `record_simulated_test_response`) demonstrated that the runtime enforcement works correctly:
   - `record_simulated_test_response` produced `event_source=SIMULATED_TEST_RESPONSE`.
   - `issue_session_acceptance` refused with `acceptance_requires_lifecycle_event_source:HERMES_MODEL_RESPONSE; got:'SIMULATED_TEST_RESPONSE'`.

### Why this is a stop condition

The configured provider endpoint returns HTTP 404. This is a model-response provenance ambiguity: I cannot establish that the live runtime can actually invoke a model because the configured endpoint is unreachable. Per the PI directive, this triggers an immediate stop.

The PI directive also says: "Do not repair, rerun, reinterpret, or weaken a requirement after observing a failure." Switching to a different provider, modifying the endpoint, or attempting any workaround would be repairing/repairing the failure. I have NOT done that.

## 4. What was preserved

- All prior frozen artifacts (byte-identically verified before commit):
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
  - `hermes-patch/ephemeral_runtime_issuance_poc.py` — `b8e5eb72...`
  - `hermes-patch/hermes-diff.patch` — `9f296f14...`
  - `ATE-POC-STATUS-AMENDMENT.md` — `195089bc...`
  - `ATE-POC-DESIGN-v0.2.1.md` — `f3261448...`
  - `ATE-POC-CLOSEOUT-v0.2.1.md` — `509d6a67...`
  - `evidence/ate_v2_1_evidence.json` — `6cd0f41d...`
  - `pipeline_v2_1.py` — `0b4f377f...`
  - `gel_v022.py` — `dfcf2514...`

Hermes install hashes (verified after the failed run):
- `ephemeral_session_id_poc.py` — `76128c69...f1d7` (unchanged)
- `ephemeral_runtime_issuance_poc.py` — `b8e5eb72...5888` (unchanged)
- `cli_session_mixin.py` — `2b035ba4...e1fc` (unchanged)
- `config_defaults.py` — `7908f904...775a` (unchanged)
- `turn_response_check.py` — `497b8eed...1c25` (unchanged)
- `cli.py` — `911cd2bc...5978` (unchanged)

## 5. Files in this closeout (new; evidence only)

- `architecture/experimental/live-provenance-poc/live-experiment/two_turn.py` — the experiment script (NOT executed successfully; preserved for reference)
- `architecture/experimental/live-provenance-poc/live-experiment/evidence/two_turn_evidence.json` — partial evidence recorded before stop

Evidence SHA-256: `c2e668237117550f819b0149aad5bfe9940bc84e8b0be1d10c523531a5e79171`

## 6. Actual runtime/model/provider identity observed

- Hermes process: the same patched runtime at commit `f21b346` (`e440bf35` upstream)
- Live session ID: `20260915_080913_65c6f9` (generated, but no model responses received)
- Provider: `minimax`
- Model: `MiniMax-M3`
- Endpoint: `https://api.minimax.io/anthropic`
- **No model response was received** (HTTP 404)

## 7. Results for Turn A

- Model response received: **NO** (HTTP 404)
- Lifecycle hook fired: **NO**
- `issue_session_acceptance`: **REFUSED** (state precondition failure: state still SESSION_STARTED because no event recorded)

## 8. Results for Turn B

- Model response received: **NO** (HTTP 404)
- Lifecycle hook fired: **NO**
- `issue_signed_candidate_action`: **REFUSED** (state precondition failure: state still SESSION_STARTED)

## 9. Negative-control result

- Negative control session created (`nc_9c28b8220d13`)
- `record_simulated_test_response` produced `event_source=SIMULATED_TEST_RESPONSE`
- `issue_session_acceptance` refused with: `acceptance_requires_lifecycle_event_source:HERMES_MODEL_RESPONSE; got:'SIMULATED_TEST_RESPONSE'`
- This confirms the runtime's enforcement of event_source separation is working correctly for the simulated path.

## 10. Raw evidence

- The experiment script logs show the HTTP 404 failures verbatim.
- A request debug dump was written to: `/home/fjventura20/.hermes/sessions/request_dump_20260915_080913_65c6f9_20260915_080930_405233.json`

## 11. Deviations

The experiment deviated from the planned execution in one specific way: **the live two-turn experiment did not complete** because the configured provider endpoint was unreachable. This is not a deviation from the protocol — it is a stop condition triggered by an ambiguity in model-response provenance.

No protocol elements were modified during the attempted run. The two_turn.py script was authored and executed once; it crashed at the negative control (which succeeded as evidence of runtime enforcement but prevented the JSON write from completing). The evidence JSON was written manually from the captured observations.

## 12. Final classification (one of three)

**INCONCLUSIVE_STOPPED_BEFORE_DETERMINATION.**

## 13. STOP

Per PI directive: stop and await PI review. No further execution, no repair, no rerun, no redesign.

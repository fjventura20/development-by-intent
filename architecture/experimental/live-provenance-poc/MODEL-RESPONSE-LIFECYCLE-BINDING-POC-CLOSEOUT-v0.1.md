# Model-Response Lifecycle Binding PoC v0.1 — Implementation & Closeout

**Status:** IMPLEMENTATION + INTEGRATION VERIFICATION (no actual model invocation)
**Date:** 2026-09-14
**Authority:** Frank Ventura (PI), per directive of 2026-09-14 (accepting `a256b9f` review + lifecycle-binding authorization).
**Predecessor (preserved byte-identically):** `architecture/experimental/live-provenance-poc/RUNTIME-ISSUANCE-POC-CLOSEOUT-v0.1.md` (SHA-256 `00975514b0f66c43ce0e4910f63ca739f9dcc5fe228e6c72ce343386c40b45c6`).

## 1. Threat model (retained)

Per v0.2.1 and the PI directive of 2026-09-14:

> Prevent a separate same-user process from manufacturing verifier-
> acceptable SessionAcceptance or SignedCandidateAction artifacts
> without the required Hermes model-turn events occurring in the bound
> live session.

Out of scope (NOT addressed):
- Root/administrator compromise
- Arbitrary code execution inside Hermes
- Malicious Hermes binary
- Process-memory extraction/debugging
- Private-key theft from the live process
- Hardware-rooted identity / TPM / out-of-band verifier

## 2. Load-bearing gap closed

The DEDICATED_RUNTIME_ISSUANCE_ESTABLISHED PoC (commit `a256b9f`) closed G5/G6 against a same-user harness that uses documented runtime interfaces. However, `record_model_response(session_id, arbitrary_response_bytes)` was still callable directly by the harness via a public test/debug function. The harness could:

1. Construct arbitrary response_bytes.
2. Call `record_model_response(sid, "acceptance", bytes)` — the function was public.
3. Issue a SessionAcceptance with event_source under the harness's control.
4. Obtain verifier-valid SessionAcceptance as if a real model turn had occurred.

This PoC closes that gap by:

1. **Splitting the event-recording interface** into two paths:
   - `_record_lifecycle_response(session_id, turn_kind, response_bytes)` — INTERNAL ONLY (leading underscore; not in any documented public API). This is the only function the production lifecycle hook may call. Inside, `event_source = HERMES_MODEL_RESPONSE` is hard-coded; the caller cannot override it.
   - `record_simulated_test_response(session_id, turn_kind, response_bytes)` — PUBLIC but explicitly debug/test. Inside, `event_source = SIMULATED_TEST_RESPONSE` is hard-coded; the caller cannot override it.

2. **Adding event_source to the signed region** of SessionAcceptance and SignedCandidateAction. The verifier checks `event_source == HERMES_MODEL_RESPONSE` for live-provenance artifacts.

3. **Wiring `_record_lifecycle_response` into the actual Hermes response lifecycle** at `agent/turn_response_check.py:142` — the canonical lifecycle point where a provider response has been received.

## 3. Production lifecycle hook

File: `agent/turn_response_check.py` (existing production code, minimal experimental addition).

Inserted immediately after `agent._turn_received_provider_response = True`:

```python
# EXPERIMENTAL v0.2.1: record the model-response event into the
# dedicated live-provenance runtime issuance state machine.
try:
    import hermes_cli.ephemeral_runtime_issuance_poc as _lp_poc
    if _lp_poc.is_enabled():
        _transport = agent._get_transport()
        _normalized = _transport.normalize_response(response)
        _content = (_normalized.content or "") if _normalized else ""
        if _content:
            _sid = getattr(agent, "session_id", None)
            if _sid and _lp_poc.has_session(_sid):
                _state = _lp_poc.get_state(_sid)
                if _state == _lp_poc.STATE_SESSION_STARTED:
                    _turn_kind = "acceptance"
                elif _state == _lp_poc.STATE_ACCEPTANCE_ISSUED:
                    _turn_kind = "action"
                else:
                    _turn_kind = None
                if _turn_kind is not None:
                    _lp_poc._record_lifecycle_response(
                        _sid, _turn_kind, _content.encode("utf-8")
                    )
except Exception:
    pass
```

**Why this is the load-bearing point:** `agent._turn_received_provider_response = True` is the single canonical flag set immediately AFTER the provider response has been received and validated (line 142 of the file). Every provider response (chat_completions, anthropic_messages, codex_responses, bedrock_converse) flows through this function. The hook extracts the response content via the same transport normalizer used by the rest of the agent loop, ensuring that the response bytes bound into the channel_proof are exactly the bytes the live session actually received.

## 4. Event-source separation

| Event source value | Set by | Used for | Verifier behavior |
| -- | -- | -- | -- |
| `HERMES_MODEL_RESPONSE` | `_record_lifecycle_response` (internal, lifecycle hook) | Production lifecycle events | Live-provenance verifier accepts |
| `SIMULATED_TEST_RESPONSE` | `record_simulated_test_response` (public, test/debug) | Test scenarios only | Live-provenance verifier rejects |

The event_source field is bound into the signed payload of every SessionAcceptance and SignedCandidateAction. The verifier `verify_live_provenance_acceptance` / `verify_live_provenance_action` (strict supersets of `verify_acceptance` / `verify_action`) reject artifacts whose event_source is not `HERMES_MODEL_RESPONSE`.

## 5. State machine (unchanged from DEDICATED_RUNTIME_ISSUANCE_ESTABLISHED)

```
SESSION_STARTED
  -> ACCEPTANCE_PENDING         (allowed: on lifecycle response event in this state)
  -> SESSION_TERMINATED         (allowed)
ACCEPTANCE_PENDING
  -> ACCEPTANCE_ISSUED          (allowed: on issue_session_acceptance, requires event_source=HERMES_MODEL_RESPONSE)
  -> SESSION_TERMINATED         (allowed)
ACCEPTANCE_ISSUED
  -> ACTION_PENDING             (allowed: on lifecycle response event in this state)
  -> SESSION_TERMINATED         (allowed)
ACTION_PENDING
  -> ACTION_ISSUED              (allowed: on issue_signed_candidate_action, requires event_source=HERMES_MODEL_RESPONSE)
  -> SESSION_TERMINATED         (allowed)
ACTION_ISSUED
  -> SESSION_TERMINATED         (allowed)
SESSION_TERMINATED
  -> (terminal)
```

## 6. Hermes patch summary

| File | Change | SHA-256 |
| -- | -- | -- |
| `hermes_cli/ephemeral_runtime_issuance_poc.py` | MOD (+event_source separation; ~120 lines added) | TBD after this commit |
| `agent/turn_response_check.py` | MOD (+34 lines lifecycle hook) | TBD after this commit |
| `hermes_cli/ephemeral_session_id_poc.py` | unchanged | `76128c69...f1d7` |
| `hermes_cli/cli_session_mixin.py` | unchanged | (per prior commit `a256b9f`) |
| `hermes_cli/config_defaults.py` | unchanged | (per prior commit `a256b9f`) |
| `hermes_cli/cli_loops_mixin.py` | unchanged | `342a4802...0e6` |
| `cli.py` | unchanged | `911cd2bc...5978` |

The complete Hermes diff is at `architecture/experimental/live-provenance-poc/hermes-patch/hermes-diff.patch` (180 lines).

The new module is gated by `experimental.live_provenance_runtime: true`.

## 7. Tests (4 suites, 68 PASS, 0 FAIL)

### Test suites

| Suite | Path | Tests | Result |
| -- | -- | -- | -- |
| In-module selftest | `hermes_cli/ephemeral_runtime_issuance_poc.py _selftest()` | 9 | PASS |
| Domain + state machine | `runtime-issuance-poc/test_issuance.py` | 25 | PASS |
| Event-source separation | `runtime-issuance-poc/test_lifecycle_binding.py` | 27 | PASS |
| Real-lifecycle integration | `runtime-issuance-poc/test_lifecycle_integration.py` | 7 | PASS |
| **Total** | | **68** | **0 FAIL** |

### Event-source separation tests (PI directive §6 E + F + G + H + I)

```
E. Direct-injection rejection
  [PASS] E.1 direct harness invocation of record_simulated_test_response rejected at issuance
  [PASS] E.2 lifecycle acceptance produces verifier-valid SessionAcceptance
  [PASS] E.3 lifecycle acceptance satisfies live-provenance verifier
  [PASS] E.4 sa_e carries event_source == HERMES_MODEL_RESPONSE in signed region
  [PASS] E.5 caller-supplied fake event_source does NOT help
  [PASS] E.6 caller-supplied fake event_source for action does NOT help

F. Causality
  [PASS] F.1 acceptance issuance without any response event fails
  [PASS] F.2 action issuance without action response event fails
  [PASS] F.3 cross-session: response event on session B does not enable acceptance on session A
  [PASS] F.4 reusing acceptance response event fails (state machine blocks)
  [PASS] F.5 post-termination lifecycle recording fails

G. Continuity
  [PASS] G.1 acceptance artifact verifies under SESSION_ACCEPTANCE domain
  [PASS] G.2 acceptance artifact verifies as LIVE_PROVENANCE
  [PASS] G.3 action artifact verifies under SESSION_ACTION domain
  [PASS] G.4 action artifact verifies as LIVE_PROVENANCE
  [PASS] G.5 acceptance and action share same public_key_sha256
  [PASS] G.6 acceptance and action share same freshness_challenge
  [PASS] G.7 monotonic_seq: acceptance < action
  [PASS] G.8 turn IDs differ
  [PASS] G.9 channel proofs differ
  [PASS] G.10 event_source == HERMES_MODEL_RESPONSE on both
  [PASS] G.11 action's session_acceptance_fingerprint == acceptance fingerprint
  [PASS] G.12 acceptance prior_fingerprint == coa_receipt_fingerprint
  [PASS] G.13 action prior_fingerprint == acceptance fingerprint

H. Cross-session lifecycle independence
  [PASS] H.1 session H1 acceptance verifies as live provenance under H1's pubkey
  [PASS] H.2 session H2 cannot issue acceptance without recorded lifecycle event

I. Replay protection
  [PASS] I.1 stale acceptance response (re-recorded after issuance) does not enable second acceptance
```

### Real-lifecycle integration test

`test_lifecycle_integration.py` invokes the production `agent.turn_response_check.check_api_response` (the exact function that runs after every provider response) twice — once with a mock acceptance response, once with a mock action response — and verifies:

- The hook fires `_record_lifecycle_response` (line 142 path).
- State transitions: SESSION_STARTED → ACCEPTANCE_PENDING → ACCEPTANCE_ISSUED → ACTION_PENDING → ACTION_ISSUED.
- The acceptance artifact satisfies `verify_live_provenance_acceptance` (event_source = HERMES_MODEL_RESPONSE).
- The action artifact satisfies `verify_live_provenance_action`.
- Both share same public_key_sha256 and freshness_challenge.
- Runtime monotonic_seq acceptance < action.

The integration test exercises the actual production code path; no direct module-level access to the PoC primitive.

## 8. Direct-injection attack result

```
ATTACK: harness constructs arbitrary bytes and submits them
        via sign_generic_debug + attempts to construct
        SessionAcceptance claiming event_source = HERMES_MODEL_RESPONSE.

RESULT: REJECTED.

REASON:
  1. sign_generic_debug signs under DOMAIN_GENERIC_DEBUG, not
     DOMAIN_SESSION_ACCEPTANCE. verify_acceptance rejects on
     domain-separation grounds.
  2. Even if the harness calls record_simulated_test_response directly,
     the event_source field in the recorded event is
     SIMULATED_TEST_RESPONSE, not HERMES_MODEL_RESPONSE. The issuance
     function refuses to issue because event_source != HERMES_MODEL_RESPONSE.
  3. The harness cannot call _record_lifecycle_response from outside
     the Hermes process without accessing the leading-underscore private
     symbol, which is not exposed via any documented public API.
  4. Even if the harness bypasses steps 1-3 by constructing a fake
     SessionAcceptance claiming event_source = HERMES_MODEL_RESPONSE
     and signing via sign_generic_debug, the verifier rejects on
     domain-separation grounds (test E.5).
```

## 9. Exact runtime path hooked

`agent/turn_response_check.py::check_api_response` — the function that the agent's turn loop calls after every provider API response. Line 142 sets `agent._turn_received_provider_response = True`. The experimental hook is inserted immediately AFTER that line.

This is the canonical lifecycle point in Hermes: every provider response (chat_completions, anthropic_messages, codex_responses, bedrock_converse) flows through `check_api_response` after the transport normalizer has extracted the response content. The hook:

1. Calls `agent._get_transport().normalize_response(response)` — the same path the agent uses for the final assistant message.
2. Extracts `_normalized.content` (the assistant text).
3. Determines the turn kind from the issuance state machine (`SESSION_STARTED → acceptance`, `ACCEPTANCE_ISSUED → action`).
4. Calls `_lp_poc._record_lifecycle_response(_sid, _turn_kind, _content.encode("utf-8"))` — the internal lifecycle path.

## 10. Exact definition of HERMES_MODEL_RESPONSE

```
EVENT_SOURCE_LIFECYCLE = "HERMES_MODEL_RESPONSE"
```

This is a constant string inside `hermes_cli/ephemeral_runtime_issuance_poc.py`. It is the value of the `event_source` field recorded into the session's per-turn state when the production lifecycle hook fires. The issuance functions bind this value into the signed region. The verifier accepts only artifacts whose signed region has `event_source == "HERMES_MODEL_RESPONSE"`.

The harness cannot substitute this value because:

1. `_record_lifecycle_response` is a leading-underscore private function; not in any documented public API.
2. The harness has no documented way to call it.
3. Even if the harness crafts a payload with `event_source = "HERMES_MODEL_RESPONSE"` and signs via `sign_generic_debug`, the verifier rejects on domain-separation grounds (test E.5).

## 11. Final classification

**MODEL_RESPONSE_LIFECYCLE_BOUND.**

The production lifecycle hook at `agent/turn_response_check.py:142` correctly drives the issuance state machine. Acceptance and action artifacts derived from lifecycle events satisfy `verify_live_provenance_*`. The harness cannot manufacture verifier-valid lifecycle artifacts via any documented interface.

This does NOT yet establish `LIVE_SESSION_PROVENANCE_BOUND` because no actual model participant has been invoked under the completed chain. The next phase (live two-turn experiment) requires further PI authorization.

## 12. Files (all new; DETERMINISTIC VERIFICATION)

In worktree:
- `architecture/experimental/live-provenance-poc/MODEL-RESPONSE-LIFECYCLE-BINDING-POC-CLOSEOUT-v0.1.md` (this document)
- `architecture/experimental/live-provenance-poc/hermes-patch/ephemeral_runtime_issuance_poc.py` (verbatim copy, updated)
- `architecture/experimental/live-provenance-poc/hermes-patch/hermes-diff.patch` (updated, 180 lines)
- `architecture/experimental/live-provenance-poc/runtime-issuance-poc/test_issuance.py` (updated to use _record_lifecycle_response)
- `architecture/experimental/live-provenance-poc/runtime-issuance-poc/test_lifecycle_binding.py` (NEW)
- `architecture/experimental/live-provenance-poc/runtime-issuance-poc/test_lifecycle_integration.py` (NEW)
- `architecture/experimental/live-provenance-poc/runtime-issuance-poc/evidence_selftest.txt` (updated)
- `architecture/experimental/live-provenance-poc/runtime-issuance-poc/evidence_test_issuance.txt` (updated)
- `architecture/experimental/live-provenance-poc/runtime-issuance-poc/evidence_test_lifecycle_binding.txt` (NEW)
- `architecture/experimental/live-provenance-poc/runtime-issuance-poc/evidence_test_lifecycle_integration.txt` (NEW)

In Hermes install:
- `/home/fjventura20/.hermes/hermes-agent/hermes_cli/ephemeral_runtime_issuance_poc.py` (MOD)
- `/home/fjventura20/.hermes/hermes-agent/agent/turn_response_check.py` (MOD, +34 lines)

## 13. STOP-AT-LIFECYCLE-BINDING

Per PI directive: do NOT execute the actual two-turn live experiment yet. The next phase (actual model invocation under the completed chain) requires further PI authorization.

STOP. Awaiting PI review.

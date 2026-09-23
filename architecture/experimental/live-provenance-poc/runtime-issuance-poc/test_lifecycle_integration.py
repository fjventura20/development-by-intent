#!/usr/bin/env python3
"""Integration test: verify the lifecycle hook in agent/turn_response_check.py
actually invokes _record_lifecycle_response when check_api_response runs.

This test simulates the actual production path:
  - Construct an AIAgent (or a minimal mock with the required attrs)
  - Construct a response object that yields content via .choices[0].delta.content
    or similar transport-normalized path
  - Call check_api_response(...) — this is the line 142 hook point
  - Verify the runtime state machine recorded an event with event_source
    == HERMES_MODEL_RESPONSE

If a real model call is needed, the test is skipped with a clear message.
The integration does NOT require actual network/LLM connectivity.
"""
import os
import sys
import secrets

sys.path.insert(0, "/home/fjventura20/.hermes/hermes-agent")
os.environ.setdefault("HERMES_HOME", os.path.expanduser("~/.hermes"))

from hermes_cli import ephemeral_session_id_poc as prim
from hermes_cli import ephemeral_runtime_issuance_poc as lp
from agent import turn_response_check as trc

# Force-enable for the test run.
prim._ENABLED = True
lp._ENABLED = True


failures = []


def check(name, ok, detail=""):
    if ok:
        print(f"[PASS] {name}")
    else:
        msg = f"[FAIL] {name}"
        if detail:
            msg += f" :: {detail}"
        print(msg)
        failures.append(name)


class _MockNormalized:
    def __init__(self, content):
        self.content = content
        self.tool_calls = None
        self.finish_reason = "stop"
        self.reasoning = None
        self.usage = None
        self.provider_data = None


class _MockTransport:
    def response_finish_reason(self, response):
        return "stop"
    def normalize_response(self, response):
        return _MockNormalized(getattr(response, "_mock_content", ""))


class _MockAgent:
    """Minimal AIAgent substitute for exercising check_api_response."""
    def __init__(self, session_id):
        self.session_id = session_id
        self._turn_received_provider_response = False
        self.api_mode = "chat_completions"
        self.verbose_logging = False
        self.quiet_mode = True
        self.thinking_callback = None
        self.thinking_spinner = None
        self._thinking_spinner = None
        self._log_prefix_calls = []
        self.provider = "openai"

    def _get_transport(self):
        return _MockTransport()

    def _should_treat_stop_as_truncated(self, fr, n, m):
        return False

    @property
    def log_prefix(self):
        return "[mock] "

    def _vprint(self, msg, force=False):
        pass

    def _touch_activity(self, *args, **kwargs):
        pass


class _MockResponse:
    def __init__(self, content):
        self._mock_content = content


# ----------------------------------------------------------------------------
# Setup: start a session
# ----------------------------------------------------------------------------

sid = "lifecycle_integration_" + secrets.token_hex(6)
prim.setup_for_session(sid)
lp.register_session(sid)
lp.associate_freshness_challenge(sid, "ch_int_" + secrets.token_hex(4))

# State should now be SESSION_STARTED. The lifecycle hook will treat this
# response as the "acceptance" turn kind (state == SESSION_STARTED).

agent = _MockAgent(sid)
challenge = "ch_int_" + secrets.token_hex(4)  # dummy
response_text = f'{{"role":"assistant","content":"I ACCEPT the COA: {challenge}"}}'
mock_response = _MockResponse(response_text)

# Build the verdict dataclass by calling check_api_response with the
# minimal required kwargs. Since we don't want to invoke the full turn
# loop, we exercise only the lifecycle-recording branch by monkey-patching
# the response_invalid check.

# Simpler: directly call the hook function. We'll exercise it by patching
# _iv.action to "fallthrough" via monkeypatching validate_response_shape
# to return (False, None).

import agent.turn_response_check as trc_mod
import agent.turn_recovery as trec_mod
orig_validate = trec_mod.validate_response_shape


def fake_validate(agent, response):
    return (False, None)


trec_mod.validate_response_shape = fake_validate

# Also patch record_response_usage to be a no-op (we don't need it for the
# lifecycle binding verification). Patching on turn_usage module is not
# enough because turn_response_check imports record_response_usage at
# module load time; we must patch the reference inside turn_response_check.
orig_record_usage = trc_mod.record_response_usage


class _FakeUsageOutcome:
    compression_attempts = 0
    pending_compaction = False
    rearmed = False
    usage_observed = False
    response_obj = None
    api_request_id = None
    api_duration = 0.0
    cost_added_usd = 0.0
    finish_reason = "stop"


class _FakeRetry:
    has_retried_429 = False
    tool_call_retry_count = 0
    last_error = None


trc_mod.record_response_usage = lambda *a, **kw: _FakeUsageOutcome()
try:
    verdict = trc_mod.check_api_response(
        agent,
        response=mock_response,
        _retry=_FakeRetry(),
        thinking_spinner=None,
        messages=[],
        api_messages=[],
        api_kwargs={},
        active_system_prompt="",
        conversation_history=[],
        finish_reason="stop",
        retry_count=0,
        max_retries=3,
        compression_attempts=0,
        max_compression_attempts=2,
        length_continue_retries=0,
        truncated_response_parts=0,
        truncated_tool_call_retries=0,
        current_turn_user_idx=0,
        api_call_count=0,
        api_request_id=None,
        api_start_time=0.0,
        effective_task_id=None,
        turn_id=1,
        _preflight_compression_blocked=False,
        _last_preflight_pressure=0,
    )
finally:
    trec_mod.validate_response_shape = orig_validate
    trc_mod.record_response_usage = orig_record_usage

# Now check that the runtime state recorded the event.
state_after = lp.get_state(sid)
print(f"State after first response: {state_after}")
check(
    "L.1 lifecycle hook fires _record_lifecycle_response on first response",
    state_after == lp.STATE_ACCEPTANCE_PENDING,
    detail=f"got: {state_after}",
)

# Issue acceptance — should succeed because event_source=HERMES_MODEL_RESPONSE.
sa = lp.issue_session_acceptance(sid, coa_receipt_fingerprint="sha256:int_coa")
prim_ev = prim.get_public_evidence(sid)
pub_b64 = prim_ev["public_key_b64"]

check(
    "L.2 lifecycle acceptance verifies as live provenance (event_source=HERMES_MODEL_RESPONSE)",
    lp.verify_live_provenance_acceptance(sa, pub_b64),
)

# Now simulate a SECOND response (action turn) via the hook.
mock_response2 = _MockResponse('{"role":"assistant","content":"ACTION: do thing"}')

trec_mod.validate_response_shape = fake_validate
trc_mod.record_response_usage = lambda *a, **kw: _FakeUsageOutcome()
try:
    verdict2 = trc_mod.check_api_response(
        agent,
        response=mock_response2,
        _retry=_FakeRetry(),
        thinking_spinner=None,
        messages=[],
        api_messages=[],
        api_kwargs={},
        active_system_prompt="",
        conversation_history=[],
        finish_reason="stop",
        retry_count=0,
        max_retries=3,
        compression_attempts=0,
        max_compression_attempts=2,
        length_continue_retries=0,
        truncated_response_parts=0,
        truncated_tool_call_retries=0,
        current_turn_user_idx=0,
        api_call_count=0,
        api_request_id=None,
        api_start_time=0.0,
        effective_task_id=None,
        turn_id=2,
        _preflight_compression_blocked=False,
        _last_preflight_pressure=0,
    )
finally:
    trc_mod.validate_response_shape = orig_validate

state_after2 = lp.get_state(sid)
print(f"State after second response: {state_after2}")
check(
    "L.3 lifecycle hook fires _record_lifecycle_response on second response (action)",
    state_after2 == lp.STATE_ACTION_PENDING,
    detail=f"got: {state_after2}",
)

sca = lp.issue_signed_candidate_action(
    sid,
    capability_id="cap_int",
    receipt_id="rec_int",
    identity_fingerprint="id_int",
    action_struct={"operation": "INT_TEST"},
    envelope_nonce="nonce_int",
)

check(
    "L.4 lifecycle action verifies as live provenance",
    lp.verify_live_provenance_action(sca, pub_b64),
)
check(
    "L.5 acceptance and action share same public_key_sha256",
    sa["public_key_sha256"] == sca["public_key_sha256"],
)
check(
    "L.6 acceptance and action share same freshness_challenge",
    sa["freshness_challenge"] == sca["freshness_challenge"],
)
check(
    "L.7 monotonic_seq: acceptance < action",
    sa["monotonic_seq"] < sca["monotonic_seq"],
)


print()
print("=" * 60)
if failures:
    print(f"FAILED {len(failures)} test(s):")
    for f in failures:
        print(f"  - {f}")
    sys.exit(1)
print("ALL TESTS PASS")
sys.exit(0)

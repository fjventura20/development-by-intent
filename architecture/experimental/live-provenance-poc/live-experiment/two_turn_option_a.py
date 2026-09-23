#!/usr/bin/env python3
"""Live Provenance PoC v0.2.1 - Two-Turn Live Experiment (Option A rerun).

After provider preflight: provider=custom, api_mode=chat_completions,
base_url=https://api.minimax.io/v1, model=MiniMax-M3.

Captures:
- runtime/session identity
- provider/model/endpoint actually used
- Turn A and Turn B real model responses
- HERMES_MODEL_RESPONSE evidence from the lifecycle hook
- SessionAcceptance and SignedCandidateAction artifacts
- live-provenance verification
- negative-control rejection

Single attempt. If anything fails: preserve evidence, write a stop
report, do not retry.
"""
import base64
import hashlib
import json
import os
import secrets
import sys
import time

sys.path.insert(0, "/home/fjventura20/.hermes/hermes-agent")
os.environ.setdefault("HERMES_HOME", os.path.expanduser("~/.hermes"))

# Verify config resolves to Option A
from cli import load_cli_config
_cfg = load_cli_config()["model"]
assert _cfg["provider"] == "custom", f"expected custom, got {_cfg['provider']}"
assert _cfg["api_mode"] == "chat_completions", f"expected chat_completions, got {_cfg['api_mode']}"
assert _cfg["base_url"] == "https://api.minimax.io/v1", f"expected api.minimax.io/v1, got {_cfg['base_url']}"
assert _cfg["default"] == "MiniMax-M3", f"expected MiniMax-M3, got {_cfg['default']}"
print(
    f"[CONFIG-OK] provider={_cfg['provider']} api_mode={_cfg['api_mode']} "
    f"base_url={_cfg['base_url']} model={_cfg['default']}",
    flush=True,
)

# Construct AIAgent via init_agent (will pick up the model config).
from run_agent import AIAgent  # type: ignore  # noqa: E402
from agent.agent_init import init_agent  # type: ignore  # noqa: E402


def make_agent() -> AIAgent:
    try:
        a = init_agent()  # type: ignore
    except Exception as e:
        print(f"[WARN] init_agent failed ({e}); constructing AIAgent directly", flush=True)
        a = AIAgent(
            base_url=_cfg["base_url"],
            api_key=_cfg["api_key"],
            provider="custom",
            model="MiniMax-M3",
            api_mode="chat_completions",
            quiet_mode=True,
            max_iterations=5,
        )
    return a


print("[INFO] Initializing AIAgent...", flush=True)
try:
    agent = make_agent()
except Exception as e:
    print(f"[ERROR] AIAgent init failed: {e}", flush=True)
    sys.exit(1)

print(f"[INFO] AIAgent ready: provider={agent.provider} model={agent.model} api_mode={agent.api_mode}", flush=True)
print(f"[INFO] AIAgent base_url: {agent.base_url}", flush=True)

# ---------------------------------------------------------------------------
# Ephemeral primitive wiring
# ---------------------------------------------------------------------------
import hermes_cli.ephemeral_session_id_poc as _prim
import hermes_cli.ephemeral_runtime_issuance_poc as _lp

_prim._ENABLED = True
_lp._ENABLED = True

# The cli_session_mixin hooks did this on `new_session()`; we replicate
# explicitly here because we're driving the agent core directly.
_prim.setup_for_session(agent.session_id)
_lp.register_session(agent.session_id)

prim_ev = _prim.get_public_evidence(agent.session_id)
print(f"[INFO] ephemeral pubkey_sha256: {prim_ev.get('public_key_sha256')}", flush=True)

# Operator-generated freshness challenge (external to Hermes)
operator_challenge = "liveprov_" + secrets.token_hex(8)
print(f"[INFO] Operator challenge: {operator_challenge}", flush=True)
_lp.associate_freshness_challenge(agent.session_id, operator_challenge)


# ---------------------------------------------------------------------------
# TURN A — COA Acceptance
# ---------------------------------------------------------------------------

print("\n[TURN A] Sending COA acceptance prompt...", flush=True)
state_before_a = _lp.get_state(agent.session_id)
print(f"[TURN A] state before: {state_before_a}", flush=True)

coa_text = (
    "GOVERNANCE ACCEPTANCE REQUEST\n\n"
    "Respond with EXACTLY the literal text below — no other words, no "
    "preamble, no commentary, no markdown:\n\n"
    "ACCEPT:" + operator_challenge + "\n"
)

try:
    response_a_text = agent.chat(coa_text)
    print(f"[TURN A] response (first 200 chars): {response_a_text[:200]!r}", flush=True)
except Exception as e:
    print(f"[ERROR] Turn A chat failed: {e}", flush=True)
    sys.exit(1)

state_after_a = _lp.get_state(agent.session_id)
print(f"[TURN A] state after: {state_after_a}", flush=True)


# ---------------------------------------------------------------------------
# Issue SessionAcceptance
# ---------------------------------------------------------------------------

import hashlib as _h

coa_receipt_fingerprint = "sha256:" + _h.sha256(
    ("tge:" + operator_challenge + ":" + coa_text[:200]).encode("utf-8")
).hexdigest()

print("\n[ISSUE] Issuing SessionAcceptance...", flush=True)
try:
    sa = _lp.issue_session_acceptance(
        agent.session_id, coa_receipt_fingerprint=coa_receipt_fingerprint
    )
    print(f"[ISSUE] SessionAcceptance OK; monotonic_seq={sa.get('monotonic_seq')}", flush=True)
except ValueError as e:
    print(f"[FAIL] SessionAcceptance failed: {e}", flush=True)
    print("LIFECYCLE HOOK DID NOT FIRE — model response produced but was not bound.", flush=True)
    sys.exit(2)


# ---------------------------------------------------------------------------
# TURN B — Governed Action
# ---------------------------------------------------------------------------

print("\n[TURN B] Sending governed-action prompt...", flush=True)
state_before_b = _lp.get_state(agent.session_id)
print(f"[TURN B] state before: {state_before_b}", flush=True)

action_text = (
    "GOVERNED ACTION REQUEST\n\n"
    "Respond with EXACTLY the literal text below — no other words, no "
    "preamble, no commentary, no markdown:\n\n"
    'ACTION:{"operation":"NONE","target":"governance_accepted"}\n'
)

try:
    response_b_text = agent.chat(action_text)
    print(f"[TURN B] response (first 200 chars): {response_b_text[:200]!r}", flush=True)
except Exception as e:
    print(f"[ERROR] Turn B chat failed: {e}", flush=True)
    sys.exit(1)

state_after_b = _lp.get_state(agent.session_id)
print(f"[TURN B] state after: {state_after_b}", flush=True)


# ---------------------------------------------------------------------------
# Issue SignedCandidateAction
# ---------------------------------------------------------------------------

capability_id = "cap_live_" + secrets.token_hex(4)
receipt_id = sa["session_acceptance_fingerprint"]
identity_fingerprint = prim_ev["public_key_sha256"]
action_struct = {"operation": "NONE", "target": "governance_accepted"}
envelope_nonce = "nonce_" + secrets.token_hex(8)

print("\n[ISSUE] Issuing SignedCandidateAction...", flush=True)
try:
    sca = _lp.issue_signed_candidate_action(
        agent.session_id,
        capability_id=capability_id,
        receipt_id=receipt_id,
        identity_fingerprint=identity_fingerprint,
        action_struct=action_struct,
        envelope_nonce=envelope_nonce,
    )
    print(f"[ISSUE] SignedCandidateAction OK; monotonic_seq={sca.get('monotonic_seq')}", flush=True)
except ValueError as e:
    print(f"[FAIL] SignedCandidateAction failed: {e}", flush=True)
    print("LIFECYCLE HOOK DID NOT FIRE FOR TURN B — state machine blocked action issuance.", flush=True)
    sys.exit(2)


# ---------------------------------------------------------------------------
# Verify
# ---------------------------------------------------------------------------

print("\n[VERIFY] Live-provenance verifications...", flush=True)
pub_b64 = prim_ev["public_key_b64"]
sa_lp_ok = _lp.verify_live_provenance_acceptance(sa, pub_b64)
sca_lp_ok = _lp.verify_live_provenance_action(sca, pub_b64)
print(f"[VERIFY] sa_lp_ok={sa_lp_ok} sca_lp_ok={sca_lp_ok}", flush=True)


# Cross-turn substitutability
print("[VERIFY] Cross-turn substitution check...", flush=True)
sa_as_action_rejected = not _lp.verify_action(sa, pub_b64)
sca_as_acceptance_rejected = not _lp.verify_acceptance(sca, pub_b64)


# ---------------------------------------------------------------------------
# NEGATIVE CONTROL — simulated path rejected by live-provenance
# ---------------------------------------------------------------------------

print("\n[NC] Negative control: simulated path must be rejected...", flush=True)
nc_sid = "nc_" + secrets.token_hex(6)
_prim.setup_for_session(nc_sid)
_lp.register_session(nc_sid)
nc_challenge = "nc_ch_" + secrets.token_hex(4)
_lp.associate_freshness_challenge(nc_sid, nc_challenge)
_lp.record_simulated_test_response(nc_sid, "acceptance", b"simulated test response")
nc_pub = _prim.get_public_evidence(nc_sid)["public_key_b64"]

nc_issue_error = None
nc_sa = None
try:
    nc_sa = _lp.issue_session_acceptance(nc_sid, coa_receipt_fingerprint="sha256:nc")
except ValueError as e:
    nc_issue_error = str(e)

nc_rejected = nc_issue_error is not None


# ---------------------------------------------------------------------------
# Capture evidence
# ---------------------------------------------------------------------------

def _enc(o):
    if isinstance(o, bytes):
        return {"__bytes_hex__": o.hex()}
    if isinstance(o, set):
        return sorted(o)
    return str(o)


evidence = {
    "experiment": "live-provenance-poc-v0.2.1-two-turn-option-A",
    "started_at_utc": time.time(),
    "config_resolved": {
        "provider": _cfg["provider"],
        "api_mode": _cfg["api_mode"],
        "base_url": _cfg["base_url"],
        "model": _cfg["default"],
    },
    "runtime_identity": {
        "session_id": agent.session_id,
        "pid": prim_ev.get("pid"),
        "code_sha": prim_ev.get("code_sha"),
        "code_version": prim_ev.get("code_version"),
        "started_at_utc": prim_ev.get("started_at_utc"),
        "proc_start_time": prim_ev.get("proc_start_time"),
        "public_key_sha256": prim_ev.get("public_key_sha256"),
        "public_key_b64": prim_ev.get("public_key_b64"),
    },
    "operator_freshness_challenge": operator_challenge,
    "turn_a": {
        "model_response_text": response_a_text,
        "state_before": state_before_a,
        "state_after": state_after_a,
        "coa_receipt_fingerprint": coa_receipt_fingerprint,
    },
    "turn_a_artifact_session_acceptance": sa,
    "turn_b": {
        "model_response_text": response_b_text,
        "state_before": state_before_b,
        "state_after": state_after_b,
        "action_struct": action_struct,
        "capability_id": capability_id,
        "envelope_nonce": envelope_nonce,
    },
    "turn_b_artifact_signed_candidate_action": sca,
    "verification": {
        "session_acceptance_live_provenance": sa_lp_ok,
        "signed_candidate_action_live_provenance": sca_lp_ok,
        "sa_event_source": sa.get("event_source"),
        "sca_event_source": sca.get("event_source"),
        "sa_monotonic_seq": sa.get("monotonic_seq"),
        "sca_monotonic_seq": sca.get("monotonic_seq"),
        "sa_turn_id": sa.get("turn_id"),
        "sca_turn_id": sca.get("turn_id"),
        "monotonic_increasing": sa.get("monotonic_seq", 0) < sca.get("monotonic_seq", 0),
        "turn_ids_differ": sa.get("turn_id") != sca.get("turn_id"),
        "channel_proofs_differ": sa.get("channel_proof") != sca.get("channel_proof"),
        "pubkey_sha256_match": (
            sa.get("public_key_sha256") == sca.get("public_key_sha256")
            == prim_ev["public_key_sha256"]
        ),
        "freshness_challenge_match": (
            sa.get("freshness_challenge") == sca.get("freshness_challenge")
            == operator_challenge
        ),
        "sa_does_not_verify_as_action": sa_as_action_rejected,
        "sca_does_not_verify_as_acceptance": sca_as_acceptance_rejected,
        "sca_session_acceptance_fingerprint_matches_sa_fingerprint": (
            sca.get("session_acceptance_fingerprint")
            == sa.get("session_acceptance_fingerprint")
        ),
    },
    "negative_control": {
        "session_id": nc_sid,
        "issue_error": nc_issue_error,
        "live_provenance_rejected": nc_rejected,
    },
}

import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--out", required=True)
args = parser.parse_args()

with open(args.out, "w") as f:
    json.dump(evidence, f, indent=2, default=_enc)


sha = hashlib.sha256(open(args.out, "rb").read()).hexdigest()
print(f"\n[INFO] Evidence written: {args.out}", flush=True)
print(f"[INFO] Evidence SHA-256: {sha}", flush=True)

# Cleanup
try:
    _lp.terminate_session_state(agent.session_id)
    _prim.terminate_session(agent.session_id)
except Exception:
    pass

# Final summary
print("\n" + "=" * 60, flush=True)
print("SUMMARY", flush=True)
print("=" * 60, flush=True)
print(f"sa_lp_ok         = {sa_lp_ok}", flush=True)
print(f"sca_lp_ok        = {sca_lp_ok}", flush=True)
print(f"sa_event_source  = {sa.get('event_source')}", flush=True)
print(f"sca_event_source = {sca.get('event_source')}", flush=True)
print(f"monotonic_inc    = {sa.get('monotonic_seq', 0) < sca.get('monotonic_seq', 0)}", flush=True)
print(f"neg_control_rejected = {nc_rejected}", flush=True)
print("=" * 60, flush=True)

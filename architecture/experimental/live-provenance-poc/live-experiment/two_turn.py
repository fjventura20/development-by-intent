#!/usr/bin/env python3
"""Live Provenance PoC v0.2.1 - Two-Turn Live Experiment.

Drives the patched Hermes runtime through TWO real model turns in the SAME
persistent session, exercising the
agent/turn_response_check.py::check_api_response lifecycle hook at the
production code path. The hook at line 142 fires _record_lifecycle_response
for each turn, tagging the recorded event with
event_source=HERMES_MODEL_RESPONSE.

After both turns complete, we issue SessionAcceptance and
SignedCandidateAction from the runtime's state machine and verify them
via verify_live_provenance_acceptance / verify_live_provenance_action.

This script is invoked once. It assumes:
  - The patched Hermes is installed.
  - experimental.live_provenance_runtime: true is enabled in
    ~/.hermes/config.yaml (set by the run_live_provenance_experiment.sh
    shell wrapper if not already set).
  - experimental.ephemeral_session_identity: true is also enabled.
  - The configured model provider has valid credentials in the env.

The script records:
  - runtime/session identity (from startup line)
  - model/provider identity actually observed
  - turn ordering (turn_id, monotonic_seq, state-machine transitions)
  - lifecycle event generation (event_source=HERMES_MODEL_RESPONSE)
  - signed acceptance/action artifacts
  - verification results (live-provenance)
  - negative-control rejection (simulated path produces artifacts that
    fail verify_live_provenance_*)
"""
import base64
import hashlib
import json
import os
import sys
import time

# Setup hermes path
sys.path.insert(0, "/home/fjventura20/.hermes/hermes-agent")
os.environ.setdefault("HERMES_HOME", os.path.expanduser("~/.hermes"))

import secrets
from hermes_cli import ephemeral_session_id_poc as prim
from hermes_cli import ephemeral_runtime_issuance_poc as lp


def sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_hex_str(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


# Enable both primitives (the config flag is set by the shell wrapper).
prim._ENABLED = True
lp._ENABLED = True


evidence = {
    "experiment": "live-provenance-poc-v0.2.1-two-turn",
    "started_at_utc": time.time(),
    "model_provider_requested": "minimax/MiniMax-M3",
    "events": [],
    "artifacts": {},
    "verification": {},
    "negative_control": {},
}


# ---------------------------------------------------------------------------
# Initialize AIAgent with the configured provider/model
# ---------------------------------------------------------------------------

print("[INFO] Initializing AIAgent...", flush=True)
import asyncio

from run_agent import AIAgent  # type: ignore
from agent.agent_init import init_agent  # type: ignore


def make_agent() -> AIAgent:
    """Construct an AIAgent with the configured provider/model."""
    # Use init_agent for the standard configuration; fall back to direct
    # AIAgent(...) if init_agent signature has changed.
    try:
        agent = init_agent()  # type: ignore
        return agent
    except Exception as e:
        print(f"[WARN] init_agent failed: {e}; falling back to AIAgent(...)", flush=True)
    # Direct construction
    agent = AIAgent(
        base_url="",
        api_key="",
        provider="minimax",
        model="MiniMax-M3",
        api_mode="chat_completions",
        quiet_mode=True,
        max_iterations=5,
    )
    return agent


agent = make_agent()

# After construction, the agent has a session_id assigned (if not,
# generate one and capture startup). Force a new session so the
# ephemeral key generation hook fires.
print(f"[INFO] AIAgent session_id: {agent.session_id}", flush=True)

# If the agent hasn't been initialized with ephemeral primitives, do it now.
# Normally the hook in cli_session_mixin.py does this; we replicate it here
# to ensure the issuance state machine is registered.
import hermes_cli.ephemeral_session_id_poc as _prim  # type: ignore
import hermes_cli.ephemeral_runtime_issuance_poc as _lp  # type: ignore

# Ensure both modules are enabled.
_prim._ENABLED = True
_lp._ENABLED = True

# Generate ephemeral keypair for this session (idempotent).
try:
    _prim.setup_for_session(agent.session_id)
except Exception as e:
    print(f"[WARN] setup_for_session: {e}", flush=True)
try:
    _lp.register_session(agent.session_id)
except Exception as e:
    print(f"[WARN] register_session: {e}", flush=True)

# Capture startup evidence
prim_ev = _prim.get_public_evidence(agent.session_id)
print(f"[INFO] ephemeral pubkey_sha256: {prim_ev.get('public_key_sha256')}", flush=True)
evidence["runtime_session_identity"] = prim_ev
evidence["session_id"] = agent.session_id
evidence["pid"] = prim_ev.get("pid")
evidence["code_sha"] = prim_ev.get("code_sha")
evidence["code_version"] = prim_ev.get("code_version")
evidence["started_at_utc"] = prim_ev.get("started_at_utc")
evidence["proc_start_time"] = prim_ev.get("proc_start_time")


# ---------------------------------------------------------------------------
# Operator-generated freshness challenge (OUTSIDE Hermes)
# ---------------------------------------------------------------------------

operator_challenge = "liveprov_" + secrets.token_hex(8)
print(f"[INFO] Operator freshness challenge: {operator_challenge}", flush=True)
evidence["operator_freshness_challenge"] = operator_challenge

# Associate the challenge with the issuance state machine. This is the
# SAME step the test harness performed in the deterministic tests.
_lp.associate_freshness_challenge(agent.session_id, operator_challenge)


# ---------------------------------------------------------------------------
# TURN A — COA Acceptance
# ---------------------------------------------------------------------------

print("[INFO] TURN A: requesting model to produce explicit acceptance...", flush=True)

coa_text = (
    "GOVERNANCE ACCEPTANCE REQUEST\n\n"
    "This is a Condition of Agency (COA) governance acceptance test.\n"
    "You MUST respond with the literal sentinel `ACCEPT:` followed by "
    "the operator challenge (verbatim), then nothing else.\n\n"
    f"Operator challenge: {operator_challenge}\n\n"
    "Example response: ACCEPT:" + operator_challenge
)

turn_a_state_before = _lp.get_state(agent.session_id)
evidence["events"].append({"label": "turn_a_before", "state": turn_a_state_before})

# This is the actual live model call. The lifecycle hook at
# agent/turn_response_check.py:142 will fire _record_lifecycle_response
# after the provider response is received.
try:
    response_a_text = agent.chat(coa_text)
except Exception as e:
    print(f"[ERROR] Turn A chat failed: {e}", flush=True)
    sys.exit(1)

print(f"[INFO] Turn A response (first 200 chars): {response_a_text[:200]!r}", flush=True)
evidence["turn_a_model_response_text"] = response_a_text

turn_a_state_after = _lp.get_state(agent.session_id)
evidence["events"].append({"label": "turn_a_after", "state": turn_a_state_after})


# ---------------------------------------------------------------------------
# Issue SessionAcceptance (only succeeds if event_source was set by hook)
# ---------------------------------------------------------------------------

# TGE receipt is a placeholder for this experiment; we use a deterministic
# string derived from the operator challenge and the COA text.
import hashlib as _h

coa_receipt_fingerprint = "sha256:" + _h.sha256(
    ("tge:" + operator_challenge + ":" + coa_text[:200]).encode("utf-8")
).hexdigest()

print(f"[INFO] Issuing SessionAcceptance for session {agent.session_id}", flush=True)
try:
    sa = _lp.issue_session_acceptance(
        agent.session_id, coa_receipt_fingerprint=coa_receipt_fingerprint
    )
    print("[PASS] SessionAcceptance issued", flush=True)
except ValueError as e:
    print(f"[FAIL] SessionAcceptance issuance failed: {e}", flush=True)
    evidence["turn_a_artifact_error"] = str(e)
    sa = None

evidence["turn_a_artifact_session_acceptance"] = sa
evidence["turn_a_artifact_fingerprint_sha256"] = (
    sha256_hex(json.dumps(sa, sort_keys=True, default=str).encode("utf-8"))
    if sa is not None else None
)


# ---------------------------------------------------------------------------
# TURN B — Governed Action
# ---------------------------------------------------------------------------

print("[INFO] TURN B: requesting model to produce governed action...", flush=True)

action_text = (
    "GOVERNED ACTION REQUEST\n\n"
    "Your previous turn produced acceptance evidence. Now emit the "
    "governed action: respond with the literal sentinel `ACTION:` followed "
    "by `{\"operation\":\"NONE\",\"target\":\"governance_accepted\"}` and nothing else."
)

turn_b_state_before = _lp.get_state(agent.session_id)
evidence["events"].append({"label": "turn_b_before", "state": turn_b_state_before})

try:
    response_b_text = agent.chat(action_text)
except Exception as e:
    print(f"[ERROR] Turn B chat failed: {e}", flush=True)
    sys.exit(1)

print(f"[INFO] Turn B response (first 200 chars): {response_b_text[:200]!r}", flush=True)
evidence["turn_b_model_response_text"] = response_b_text

turn_b_state_after = _lp.get_state(agent.session_id)
evidence["events"].append({"label": "turn_b_after", "state": turn_b_state_after})


# ---------------------------------------------------------------------------
# Issue SignedCandidateAction
# ---------------------------------------------------------------------------

capability_id = "cap_live_" + secrets.token_hex(4)
receipt_id = sa["session_acceptance_fingerprint"] if sa else "missing"
identity_fingerprint = prim_ev["public_key_sha256"]
action_struct = {"operation": "NONE", "target": "governance_accepted"}
envelope_nonce = "nonce_" + secrets.token_hex(8)

print("[INFO] Issuing SignedCandidateAction...", flush=True)
try:
    sca = _lp.issue_signed_candidate_action(
        agent.session_id,
        capability_id=capability_id,
        receipt_id=receipt_id,
        identity_fingerprint=identity_fingerprint,
        action_struct=action_struct,
        envelope_nonce=envelope_nonce,
    )
    print("[PASS] SignedCandidateAction issued", flush=True)
except ValueError as e:
    print(f"[FAIL] SignedCandidateAction issuance failed: {e}", flush=True)
    evidence["turn_b_artifact_error"] = str(e)
    sca = None

evidence["turn_b_artifact_signed_candidate_action"] = sca
evidence["turn_b_artifact_fingerprint_sha256"] = (
    sha256_hex(json.dumps(sca, sort_keys=True, default=str).encode("utf-8"))
    if sca is not None else None
)


# ---------------------------------------------------------------------------
# Verification
# ---------------------------------------------------------------------------

print("[INFO] Verifying live-provenance...", flush=True)

if sa is not None and sca is not None:
    pub_b64 = prim_ev["public_key_b64"]

    # 1. Acceptance verifies as live provenance
    sa_lp_ok = _lp.verify_live_provenance_acceptance(sa, pub_b64)
    print(f"[{'PASS' if sa_lp_ok else 'FAIL'}] SessionAcceptance verifies as live provenance", flush=True)
    evidence["verification"]["session_acceptance_live_provenance"] = sa_lp_ok

    # 2. Action verifies as live provenance
    sca_lp_ok = _lp.verify_live_provenance_action(sca, pub_b64)
    print(f"[{'PASS' if sca_lp_ok else 'FAIL'}] SignedCandidateAction verifies as live provenance", flush=True)
    evidence["verification"]["signed_candidate_action_live_provenance"] = sca_lp_ok

    # 3. event_source checks
    evidence["verification"]["sa_event_source"] = sa.get("event_source")
    evidence["verification"]["sca_event_source"] = sca.get("event_source")

    # 4. Causal ordering
    evidence["verification"]["sa_monotonic_seq"] = sa.get("monotonic_seq")
    evidence["verification"]["sca_monotonic_seq"] = sca.get("monotonic_seq")
    evidence["verification"]["sa_turn_id"] = sa.get("turn_id")
    evidence["verification"]["sca_turn_id"] = sca.get("turn_id")
    evidence["verification"]["monotonic_increasing"] = (
        sa.get("monotonic_seq", 0) < sca.get("monotonic_seq", 0)
    )
    evidence["verification"]["turn_ids_differ"] = (
        sa.get("turn_id") != sca.get("turn_id")
    )
    evidence["verification"]["channel_proofs_differ"] = (
        sa.get("channel_proof") != sca.get("channel_proof")
    )

    # 5. Prior fingerprint chain
    evidence["verification"]["sa_prior_fingerprint"] = sa.get("prior_fingerprint")
    evidence["verification"]["sca_prior_fingerprint"] = sca.get("prior_fingerprint")
    evidence["verification"]["sca_session_acceptance_fingerprint"] = sca.get("session_acceptance_fingerprint")
    evidence["verification"]["prior_fingerprint_chain_ok"] = (
        sca.get("session_acceptance_fingerprint") == sa.get("session_acceptance_fingerprint")
    )

    # 6. Public-key + challenge consistency
    evidence["verification"]["pubkey_sha256_match"] = (
        sa.get("public_key_sha256") == sca.get("public_key_sha256")
        == prim_ev["public_key_sha256"]
    )
    evidence["verification"]["freshness_challenge_match"] = (
        sa.get("freshness_challenge") == sca.get("freshness_challenge")
        == operator_challenge
    )

    # 7. Substitutability check: turn A's artifact under turn B's pubkey
    # (should fail; we don't have a different pubkey but at least check
    # cross-domain verification rejects)
    evidence["verification"]["sa_does_not_verify_as_action"] = (
        not _lp.verify_action(sa, pub_b64)
    )
    evidence["verification"]["sca_does_not_verify_as_acceptance"] = (
        not _lp.verify_acceptance(sca, pub_b64)
    )


# ---------------------------------------------------------------------------
# NEGATIVE CONTROL — simulated/test path is rejected by live-provenance verifier
# ---------------------------------------------------------------------------

print("[INFO] Negative control: simulated test response should be rejected", flush=True)

# Build a fresh session for the negative control (so we don't disturb state).
nc_sid = "nc_" + secrets.token_hex(6)
_prim.setup_for_session(nc_sid)
_lp.register_session(nc_sid)
nc_challenge = "nc_ch_" + secrets.token_hex(4)
_lp.associate_freshness_challenge(nc_sid, nc_challenge)

# Use the SIMULATED path (debug-only).
_lp.record_simulated_test_response(nc_sid, "acceptance", b"simulated test response")
nc_sa = _lp.issue_session_acceptance(
    nc_sid, coa_receipt_fingerprint="sha256:nc"
)
nc_pub = _prim.get_public_evidence(nc_sid)["public_key_b64"]
nc_sa_lp_ok = _lp.verify_live_provenance_acceptance(nc_sa, nc_pub)
nc_sa_event_source = nc_sa.get("event_source")
print(f"[{'PASS' if not nc_sa_lp_ok else 'FAIL'}] negative-control simulated artifact rejected by live-provenance verifier", flush=True)
print(f"[INFO] negative-control event_source: {nc_sa_event_source}", flush=True)

evidence["negative_control"] = {
    "simulated_session_id": nc_sid,
    "simulated_artifact_event_source": nc_sa_event_source,
    "live_provenance_rejected": (not nc_sa_lp_ok),
    "simulated_artifact_fingerprint_sha256": sha256_hex(
        json.dumps(nc_sa, sort_keys=True, default=str).encode("utf-8")
    ),
}


# ---------------------------------------------------------------------------
# Cleanup
# ---------------------------------------------------------------------------

try:
    _lp.terminate_session_state(agent.session_id)
    _prim.terminate_session(agent.session_id)
except Exception:
    pass

evidence["completed_at_utc"] = time.time()


# ---------------------------------------------------------------------------
# Write evidence JSON
# ---------------------------------------------------------------------------

import argparse
parser = argparse.ArgumentParser()
parser.add_argument("--out", required=True)
args = parser.parse_args()

# Custom JSON encoder to handle bytes-like fields gracefully.
def _encode(o):
    if isinstance(o, bytes):
        return {"__bytes_hex__": o.hex()}
    if isinstance(o, set):
        return sorted(o)
    return str(o)

with open(args.out, "w") as f:
    json.dump(evidence, f, indent=2, default=_encode)

print(f"[INFO] Evidence written to {args.out}", flush=True)
print(f"[INFO] Evidence SHA-256: {sha256_hex(open(args.out, 'rb').read())}", flush=True)

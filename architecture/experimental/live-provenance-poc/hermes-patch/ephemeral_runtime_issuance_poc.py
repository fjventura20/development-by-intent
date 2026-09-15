"""Experimental live-provenance runtime issuance (v0.2.1 PoC).

EXPERIMENTAL — gated by config flag `experimental.live_provenance_runtime: true`.

Scope (per PI directive 2026-09-14, accepted review at commit 1a5574e):
  Establish the minimum dedicated runtime issuance mechanism sufficient to
  close G5/G6 from the v0.2.1 adversarial review. NOT a live-provenance
  experiment; no model calls; no LIVE_SESSION_PROVENANCE_BOUND claim.

Threat model (retained from v0.2.1):
  Prevent a separate same-user process from manufacturing verifier-
  acceptable SessionAcceptance or SignedCandidateAction artifacts
  without the required Hermes model-turn events occurring in the bound
  live session.
  Out of scope: root/admin compromise, arbitrary code execution inside
  Hermes, malicious Hermes binary, debugger/memory extraction, hardware
  attacks.

This module addresses the load-bearing gaps identified in the v0.2.1
review (commits 9ac3f37 design + 1a5574e review):

1. CRYPTOGRAPHIC DOMAIN SEPARATION
   Signing preimages are prefixed with a runtime-controlled domain tag.
   The harness cannot override the domain because the tag is prepended
   INSIDE the runtime after the caller-supplied bytes are accepted.

2. DEDICATED ISSUANCE FUNCTIONS
   `issue_session_acceptance(session_id, ...)` and
   `issue_signed_candidate_action(session_id, ...)` construct their
   canonical signed objects internally from runtime state. The harness
   cannot supply a fully serialized artifact to be signed.

3. RUNTIME STATE MACHINE
   Per-session state machine:
     SESSION_STARTED
     -> ACCEPTANCE_PENDING
     -> ACCEPTANCE_ISSUED
     -> ACTION_PENDING
     -> ACTION_ISSUED
     -> SESSION_TERMINATED
   Forbidden transitions fail closed with explicit exception.

4. RUNTIME-MONOTONIC SEQUENCE
   `monotonic_seq` is allocated by the runtime only on valid state-
   machine transitions and embedded in the signed payload.

5. CHANNEL-PROOF MECHANISM
   The runtime generates a `channel_proof` (turn-event identifier)
   when it observes a model-response event. This is bound into the
   signed payload. For this PoC the channel-proof mechanism is the
   explicit `runtime_record_model_response(session_id, turn_kind,
   response_bytes)` function (callable only by trusted callers in the
   live session path; tests simulate it with deterministic mock data).

NO participant / model invocation is performed by this module.
"""
from __future__ import annotations

import base64
import hashlib
import json
import logging
import threading
from dataclasses import dataclass, field
from typing import Any, Dict, Optional, Tuple, cast

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Signing domains (cryptographic domain separation)
# ---------------------------------------------------------------------------

DOMAIN_GENERIC_DEBUG = b"HERMES_LP_GENERIC_DEBUG\x00"
DOMAIN_SESSION_ACCEPTANCE = b"HERMES_LP_SESSION_ACCEPTANCE\x00"
DOMAIN_SESSION_ACTION = b"HERMES_LP_SESSION_ACTION\x00"
DOMAIN_SESSION_EXECUTION = b"HERMES_LP_SESSION_EXECUTION\x00"
DOMAIN_SESSION_DECISION = b"HERMES_LP_SESSION_DECISION\x00"

_ALL_DOMAINS = (
    DOMAIN_GENERIC_DEBUG,
    DOMAIN_SESSION_ACCEPTANCE,
    DOMAIN_SESSION_ACTION,
    DOMAIN_SESSION_EXECUTION,
    DOMAIN_SESSION_DECISION,
)


def _domain_bytes(name: str) -> bytes:
    """Return the domain tag bytes for a given domain name.

    Unknown domain names raise ValueError. This prevents the caller
    from constructing an arbitrary domain tag and sneaking it into
    the verifier via a private function — the verifier consults this
    table for all recognized domains.
    """
    table = {
        "GENERIC_DEBUG": DOMAIN_GENERIC_DEBUG,
        "SESSION_ACCEPTANCE": DOMAIN_SESSION_ACCEPTANCE,
        "SESSION_ACTION": DOMAIN_SESSION_ACTION,
        "SESSION_EXECUTION": DOMAIN_SESSION_EXECUTION,
        "SESSION_DECISION": DOMAIN_SESSION_DECISION,
    }
    if name not in table:
        raise ValueError(f"unknown_domain:{name!r}")
    return table[name]


# ---------------------------------------------------------------------------
# State machine
# ---------------------------------------------------------------------------

STATE_SESSION_STARTED = "SESSION_STARTED"
STATE_ACCEPTANCE_PENDING = "ACCEPTANCE_PENDING"
STATE_ACCEPTANCE_ISSUED = "ACCEPTANCE_ISSUED"
STATE_ACTION_PENDING = "ACTION_PENDING"
STATE_ACTION_ISSUED = "ACTION_ISSUED"
STATE_SESSION_TERMINATED = "SESSION_TERMINATED"

_ALLOWED_TRANSITIONS = {
    STATE_SESSION_STARTED: {STATE_ACCEPTANCE_PENDING, STATE_SESSION_TERMINATED},
    STATE_ACCEPTANCE_PENDING: {STATE_ACCEPTANCE_ISSUED, STATE_SESSION_TERMINATED},
    STATE_ACCEPTANCE_ISSUED: {STATE_ACTION_PENDING, STATE_SESSION_TERMINATED},
    STATE_ACTION_PENDING: {STATE_ACTION_ISSUED, STATE_SESSION_TERMINATED},
    STATE_ACTION_ISSUED: {STATE_SESSION_TERMINATED},
    STATE_SESSION_TERMINATED: set(),
}


# ---------------------------------------------------------------------------
# Runtime state per session
# ---------------------------------------------------------------------------

@dataclass
class _IssuanceState:
    session_id: str
    state: str = STATE_SESSION_STARTED
    monotonic_seq: int = 0
    last_freshness_challenge: Optional[str] = None
    last_coa_receipt_fingerprint: Optional[str] = None
    last_session_acceptance_fingerprint: Optional[str] = None
    last_turn_id: int = 0
    acceptance_turn_id: Optional[int] = None
    action_turn_id: Optional[int] = None
    pending_acceptance_response_hash: Optional[str] = None
    pending_action_response_hash: Optional[str] = None
    pending_acceptance_event_source: Optional[str] = None
    pending_action_event_source: Optional[str] = None
    terminated: bool = False

    def transition(self, target: str) -> None:
        allowed = _ALLOWED_TRANSITIONS.get(self.state, set())
        if target not in allowed:
            raise ValueError(
                f"forbidden_transition:{self.state}->{target}"
            )
        self.state = target


_LOCK = threading.Lock()
_ISSUANCE: Dict[str, _IssuanceState] = {}
_ENABLED: Optional[bool] = None


def is_enabled() -> bool:
    """Return whether the live-provenance runtime issuance mechanism is enabled.

    Lazy-resolves from config on first call. Caches.
    """
    global _ENABLED
    if _ENABLED is None:
        _ENABLED = _read_flag_from_config()
    return _ENABLED


def _read_flag_from_config() -> bool:
    try:
        from hermes_cli.config import load_config  # type: ignore
        cfg = load_config()
    except Exception:
        return False
    try:
        return bool(cfg.get("experimental", {}).get("live_provenance_runtime", False))
    except Exception:
        return False


# ---------------------------------------------------------------------------
# Session lifecycle hook (called by ephemeral_session_id_poc.setup_for_session)
# ---------------------------------------------------------------------------

def register_session(session_id: str) -> None:
    """Register a new session in SESSION_STARTED state.

    Idempotent: if the session is already registered, the call is a no-op.
    """
    if not is_enabled():
        return
    with _LOCK:
        if session_id in _ISSUANCE:
            return
        _ISSUANCE[session_id] = _IssuanceState(session_id=session_id)


def terminate_session_state(session_id: str) -> None:
    """Transition session to SESSION_TERMINATED and clear in-memory references.

    Idempotent: terminating an already-terminated or unknown session is a no-op.
    """
    if not is_enabled():
        return
    with _LOCK:
        st = _ISSUANCE.get(session_id)
        if st is None:
            return
        if st.terminated:
            return
        st.terminated = True
        try:
            st.transition(STATE_SESSION_TERMINATED)
        except ValueError:
            # Already terminated at the state-machine level; OK.
            pass


def has_session(session_id: str) -> bool:
    if not is_enabled():
        return False
    with _LOCK:
        return session_id in _ISSUANCE


def get_state(session_id: str) -> str:
    if not is_enabled():
        raise ValueError("live_provenance_runtime_disabled")
    with _LOCK:
        st = _ISSUANCE.get(session_id)
        if st is None:
            raise ValueError(f"unknown_session:{session_id!r}")
        return st.state


# ---------------------------------------------------------------------------
# Freshness challenge association
# ---------------------------------------------------------------------------

def associate_freshness_challenge(session_id: str, challenge: str) -> None:
    """Associate the operator's freshness challenge with this session.

    Required before the session can be transitioned to ACCEPTANCE_PENDING.
    A different challenge issued after rotation fails because the old
    challenge is overwritten (stale challenge detection is a downstream
    predicate concern; the runtime records the *current* challenge only).
    """
    if not is_enabled():
        raise ValueError("live_provenance_runtime_disabled")
    with _LOCK:
        st = _ISSUANCE.get(session_id)
        if st is None:
            raise ValueError(f"unknown_session:{session_id!r}")
        if st.terminated:
            raise ValueError(f"session_terminated:{session_id!r}")
        st.last_freshness_challenge = challenge


# ---------------------------------------------------------------------------
# Model-response event recording
# ---------------------------------------------------------------------------
#
# Two event-source paths are distinguished:
#
# 1. LIFECYCLE PATH (production): `_record_lifecycle_response` — INTERNAL ONLY.
#    This is the only function that the runtime's actual model-response
#    lifecycle hook may call. The caller cannot choose `event_source`;
#    it is hard-coded to HERMES_MODEL_RESPONSE inside this function.
#    Artifacts derived from these events carry event_source =
#    HERMES_MODEL_RESPONSE in their signed region.
#
# 2. TEST/DEBUG PATH (non-production): `record_simulated_test_response` —
#    PUBLIC (for tests) but visibly marked. Caller-supplied bytes; the
#    event is tagged SIMULATED_TEST_RESPONSE. Artifacts derived from
#    these events carry event_source = SIMULATED_TEST_RESPONSE in their
#    signed region. The verifier rejects artifacts with this event_source
#    for the live-provenance predicate.
#
# A direct harness invocation of `record_simulated_test_response` to obtain
# HERMES_MODEL_RESPONSE provenance fails because:
#   (a) `record_simulated_test_response` hard-codes event_source =
#       SIMULATED_TEST_RESPONSE; the caller cannot override it;
#   (b) the issuance function requires event_source == HERMES_MODEL_RESPONSE
#       and refuses otherwise;
#   (c) the verifier rejects HERMES_MODEL_RESPONSE-bound artifacts only
#       when the lifecycle recording path was actually exercised.

EVENT_SOURCE_LIFECYCLE = "HERMES_MODEL_RESPONSE"
EVENT_SOURCE_SIMULATED = "SIMULATED_TEST_RESPONSE"

_ALLOWED_EVENT_SOURCES = frozenset({EVENT_SOURCE_LIFECYCLE, EVENT_SOURCE_SIMULATED})


def record_simulated_test_response(
    session_id: str,
    turn_kind: str,
    response_bytes: bytes,
) -> Tuple[int, str]:
    """SIMULATED / DEBUG-ONLY response recording.

    Public for tests. Tags the event with `event_source =
    SIMULATED_TEST_RESPONSE`. Artifacts derived from this event will be
    REJECTED by the live-provenance verifier. This function does NOT
    satisfy the LIVE_SESSION_PROVENANCE_BOUND predicate.

    `turn_kind` is 'acceptance' or 'action'. Other values raise ValueError.
    """
    if not is_enabled():
        raise ValueError("live_provenance_runtime_disabled")
    return _record_response_event(
        session_id=session_id,
        turn_kind=turn_kind,
        response_bytes=response_bytes,
        event_source=EVENT_SOURCE_SIMULATED,
    )


def _record_lifecycle_response(
    session_id: str,
    turn_kind: str,
    response_bytes: bytes,
) -> Tuple[int, str]:
    """INTERNAL-ONLY: record an actual model-response event from the
    Hermes response lifecycle. Caller cannot choose `event_source`; it
    is hard-coded to HERMES_MODEL_RESPONSE inside this function.

    This is the ONLY function the runtime's actual model-response hook
    may call. Calling it from any other context requires direct module
    access to the private symbol, which the harness does not have via
    any documented public API.

    `turn_kind` is 'acceptance' or 'action'. Other values raise ValueError.
    """
    if not is_enabled():
        raise ValueError("live_provenance_runtime_disabled")
    return _record_response_event(
        session_id=session_id,
        turn_kind=turn_kind,
        response_bytes=response_bytes,
        event_source=EVENT_SOURCE_LIFECYCLE,
    )


def _record_response_event(
    session_id: str,
    turn_kind: str,
    response_bytes: bytes,
    *,
    event_source: str,
) -> Tuple[int, str]:
    if event_source not in _ALLOWED_EVENT_SOURCES:
        raise ValueError(f"invalid_event_source:{event_source!r}")
    if turn_kind not in ("acceptance", "action"):
        raise ValueError(f"invalid_turn_kind:{turn_kind!r}")
    with _LOCK:
        st = _ISSUANCE.get(session_id)
        if st is None:
            raise ValueError(f"unknown_session:{session_id!r}")
        if st.terminated:
            raise ValueError(f"session_terminated:{session_id!r}")
        # Allocate the turn id atomically.
        st.last_turn_id += 1
        turn_id = st.last_turn_id
        # Hash the response bytes.
        h = hashlib.sha256(response_bytes).hexdigest()
        if turn_kind == "acceptance":
            st.pending_acceptance_response_hash = h
            st.pending_acceptance_event_source = event_source
            st.acceptance_turn_id = turn_id
            if st.state == STATE_SESSION_STARTED:
                st.transition(STATE_ACCEPTANCE_PENDING)
        else:
            st.pending_action_response_hash = h
            st.pending_action_event_source = event_source
            st.action_turn_id = turn_id
            if st.state == STATE_ACCEPTANCE_ISSUED:
                st.transition(STATE_ACTION_PENDING)
            elif st.state == STATE_ACTION_PENDING:
                pass
        return turn_id, h


# ---------------------------------------------------------------------------
# Underlying signer (re-uses ephemeral_session_id_poc)
# ---------------------------------------------------------------------------

def _get_session_primitive_key(session_id: str):
    """Fetch the Ed25519 private key + public metadata from the primitive."""
    # Local import to avoid cycles
    from hermes_cli.ephemeral_session_id_poc import (  # type: ignore
        is_enabled as primitive_is_enabled,
    )
    if not primitive_is_enabled():
        raise ValueError("ephemeral_session_identity_disabled")
    # Internal access — pull the module-level dict via a private lookup.
    import hermes_cli.ephemeral_session_id_poc as _prim  # type: ignore
    with _prim._LOCK:  # type: ignore[attr-defined]
        k = _prim._KEYS.get(session_id)  # type: ignore[attr-defined]
        if k is None:
            raise ValueError(f"unknown_session_in_primitive:{session_id!r}")
        if k.terminated:
            raise ValueError(f"session_terminated:{session_id!r}")
        if k.priv is None:
            raise ValueError(f"session_key_destroyed:{session_id!r}")
        return k


def _sign_under_domain(
    session_id: str,
    domain: bytes,
    payload_obj: dict,
) -> Tuple[bytes, str, str, str]:
    """Sign `payload_obj` under the runtime-controlled domain.

    The signed preimage is: domain || canonical_json(payload_obj).
    The canonical JSON does NOT contain the domain tag.

    Returns (signed_preimage_bytes, signature_b64, public_key_b64,
    public_key_sha256).
    """
    k = _get_session_primitive_key(session_id)
    payload_bytes = _canonical_json(payload_obj)
    signed_preimage = domain + payload_bytes
    sig = k.priv.sign(signed_preimage)
    sig_b64 = base64.b64encode(sig).decode("ascii")
    return signed_preimage, sig_b64, k.pub_b64, k.pub_sha256


def _canonical_json(obj: dict) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


# ---------------------------------------------------------------------------
# Dedicated issuance functions
# ---------------------------------------------------------------------------

def issue_session_acceptance(
    session_id: str,
    *,
    coa_receipt_fingerprint: str,
) -> Dict[str, object]:
    """Issue a SessionAcceptance artifact.

    Constructs the canonical signed object internally from runtime state.
    The harness supplies only the COA receipt fingerprint (which is itself
    a TGE-signed artifact the harness already has).

    Required preconditions (state machine):
      - session is registered
      - session is not terminated
      - state is ACCEPTANCE_PENDING
      - last_freshness_challenge is set
      - pending_acceptance_response_hash is set (model response observed)

    Embeds into the signed payload:
      session_id, public_key_sha256, freshness_challenge,
      coa_receipt_fingerprint, acceptance_response_hash,
      monotonic_seq (allocated by runtime), turn_id (allocated by runtime),
      prior_fingerprint = coa_receipt_fingerprint,
      provenance_type = RUNTIME_ACCEPTANCE_TURN (literal in signed region)
      channel_proof = SHA-256(turn_id || response_hash) (runtime-controlled)

    Signs under SESSION_ACCEPTANCE domain.

    Returns dict with all fields including signed payload and signature.
    """
    if not is_enabled():
        raise ValueError("live_provenance_runtime_disabled")
    with _LOCK:
        st = _ISSUANCE.get(session_id)
        if st is None:
            raise ValueError(f"unknown_session:{session_id!r}")
        if st.terminated:
            raise ValueError(f"session_terminated:{session_id!r}")
        if st.state != STATE_ACCEPTANCE_PENDING:
            raise ValueError(
                f"acceptance_issuance_requires_state:{STATE_ACCEPTANCE_PENDING}; got:{st.state}"
            )
        if st.last_freshness_challenge is None:
            raise ValueError("freshness_challenge_required")
        if st.pending_acceptance_response_hash is None:
            raise ValueError("model_response_observation_required")
        if st.acceptance_turn_id is None:
            raise ValueError("turn_id_required")
        if st.pending_acceptance_event_source != EVENT_SOURCE_LIFECYCLE:
            raise ValueError(
                f"acceptance_requires_lifecycle_event_source:{EVENT_SOURCE_LIFECYCLE}; "
                f"got:{st.pending_acceptance_event_source!r}"
            )

        # Allocate monotonic seq and transition state.
        st.monotonic_seq += 1
        seq = st.monotonic_seq
        turn_id = st.acceptance_turn_id
        response_hash = st.pending_acceptance_response_hash
        challenge = st.last_freshness_challenge
        event_source = st.pending_acceptance_event_source
        # Channel proof is runtime-controlled: SHA-256 of turn_id (hex) + ':' + response_hash.
        channel_proof = hashlib.sha256(
            f"{turn_id}:{response_hash}".encode("utf-8")
        ).hexdigest()
        st.transition(STATE_ACCEPTANCE_ISSUED)
        st.last_coa_receipt_fingerprint = coa_receipt_fingerprint
        st.last_session_acceptance_fingerprint = None  # set after issuance
        # Fingerprint of the canonical signed object is computed AFTER
        # payload assembly below.
        k_pub_sha = None
    # Pull public-key fingerprint from primitive (after releasing lock).
    k = _get_session_primitive_key(session_id)
    k_pub_sha = k.pub_sha256

    payload_obj = {
        "session_id": session_id,
        "public_key_sha256": k_pub_sha,
        "freshness_challenge": challenge,
        "coa_receipt_fingerprint": coa_receipt_fingerprint,
        "acceptance_response_hash": response_hash,
        "monotonic_seq": seq,
        "turn_id": turn_id,
        "channel_proof": channel_proof,
        "prior_fingerprint": coa_receipt_fingerprint,
        "provenance_type": "RUNTIME_ACCEPTANCE_TURN",
        "domain": "SESSION_ACCEPTANCE",
        "event_source": event_source,
    }
    signed_preimage, sig_b64, pub_b64, pub_sha = _sign_under_domain(
        session_id, DOMAIN_SESSION_ACCEPTANCE, payload_obj
    )

    # Compute the SessionAcceptance fingerprint (hash of signed preimage)
    # and record it in state.
    sa_fingerprint = hashlib.sha256(signed_preimage).hexdigest()
    with _LOCK:
        st = _ISSUANCE.get(session_id)
        if st is not None:
            st.last_session_acceptance_fingerprint = sa_fingerprint

    return {
        "schema_id": "HERMES-LP-SESSION-ACCEPTANCE/0.1",
        "session_id": session_id,
        "public_key_sha256": pub_sha,
        "freshness_challenge": challenge,
        "coa_receipt_fingerprint": coa_receipt_fingerprint,
        "acceptance_response_hash": response_hash,
        "monotonic_seq": seq,
        "turn_id": turn_id,
        "channel_proof": channel_proof,
        "prior_fingerprint": coa_receipt_fingerprint,
        "provenance_type": "RUNTIME_ACCEPTANCE_TURN",
        "domain": "SESSION_ACCEPTANCE",
        "event_source": event_source,
        "session_acceptance_fingerprint": sa_fingerprint,
        "signed_preimage_sha256": sa_fingerprint,
        "payload_canonical_b64": base64.b64encode(_canonical_json(payload_obj)).decode("ascii"),
        "signature_b64": sig_b64,
        "public_key_b64": pub_b64,
    }


def issue_signed_candidate_action(
    session_id: str,
    *,
    capability_id: str,
    receipt_id: str,
    identity_fingerprint: str,
    action_struct: dict,
    envelope_nonce: str,
) -> Dict[str, object]:
    """Issue a SignedCandidateAction artifact.

    Required preconditions (state machine):
      - session is registered
      - session is not terminated
      - state is ACTION_PENDING
      - pending_action_response_hash is set (model response observed)
      - last_session_acceptance_fingerprint is set (acceptance issued)

    Embeds into the signed payload:
      session_id, public_key_sha256, freshness_challenge,
      session_acceptance_fingerprint, capability_id, receipt_id,
      identity_fingerprint, action_preimage_hash,
      prior_fingerprint = session_acceptance_fingerprint,
      envelope_nonce, monotonic_seq (allocated by runtime),
      turn_id, channel_proof (runtime-controlled),
      provenance_type = RUNTIME_ACTION_TURN (literal in signed region)
      domain = SESSION_ACTION

    Signs under SESSION_ACTION domain.
    """
    if not is_enabled():
        raise ValueError("live_provenance_runtime_disabled")
    with _LOCK:
        st = _ISSUANCE.get(session_id)
        if st is None:
            raise ValueError(f"unknown_session:{session_id!r}")
        if st.terminated:
            raise ValueError(f"session_terminated:{session_id!r}")
        if st.state != STATE_ACTION_PENDING:
            raise ValueError(
                f"action_issuance_requires_state:{STATE_ACTION_PENDING}; got:{st.state}"
            )
        if st.pending_action_response_hash is None:
            raise ValueError("model_response_observation_required")
        if st.action_turn_id is None:
            raise ValueError("turn_id_required")
        if st.pending_action_event_source != EVENT_SOURCE_LIFECYCLE:
            raise ValueError(
                f"action_requires_lifecycle_event_source:{EVENT_SOURCE_LIFECYCLE}; "
                f"got:{st.pending_action_event_source!r}"
            )
        if st.last_session_acceptance_fingerprint is None:
            raise ValueError("session_acceptance_required_before_action")
        if st.last_freshness_challenge is None:
            raise ValueError("freshness_challenge_required")
        sa_fingerprint = st.last_session_acceptance_fingerprint
        challenge = st.last_freshness_challenge
        st.monotonic_seq += 1
        seq = st.monotonic_seq
        turn_id = st.action_turn_id
        response_hash = st.pending_action_response_hash
        event_source = st.pending_action_event_source
        channel_proof = hashlib.sha256(
            f"{turn_id}:{response_hash}".encode("utf-8")
        ).hexdigest()
        st.transition(STATE_ACTION_ISSUED)
    k = _get_session_primitive_key(session_id)
    k_pub_sha = k.pub_sha256
    action_preimage_hash = hashlib.sha256(_canonical_json(action_struct)).hexdigest()

    payload_obj = {
        "session_id": session_id,
        "public_key_sha256": k_pub_sha,
        "freshness_challenge": challenge,
        "session_acceptance_fingerprint": sa_fingerprint,
        "capability_id": capability_id,
        "receipt_id": receipt_id,
        "identity_fingerprint": identity_fingerprint,
        "action_preimage_hash": action_preimage_hash,
        "prior_fingerprint": sa_fingerprint,
        "envelope_nonce": envelope_nonce,
        "monotonic_seq": seq,
        "turn_id": turn_id,
        "channel_proof": channel_proof,
        "provenance_type": "RUNTIME_ACTION_TURN",
        "domain": "SESSION_ACTION",
        "event_source": event_source,
    }
    signed_preimage, sig_b64, pub_b64, pub_sha = _sign_under_domain(
        session_id, DOMAIN_SESSION_ACTION, payload_obj
    )
    signed_preimage_sha = hashlib.sha256(signed_preimage).hexdigest()
    return {
        "schema_id": "HERMES-LP-SIGNED-CANDIDATE-ACTION/0.1",
        "session_id": session_id,
        "public_key_sha256": pub_sha,
        "freshness_challenge": challenge,
        "session_acceptance_fingerprint": sa_fingerprint,
        "capability_id": capability_id,
        "receipt_id": receipt_id,
        "identity_fingerprint": identity_fingerprint,
        "action_preimage_hash": action_preimage_hash,
        "prior_fingerprint": sa_fingerprint,
        "envelope_nonce": envelope_nonce,
        "monotonic_seq": seq,
        "turn_id": turn_id,
        "channel_proof": channel_proof,
        "provenance_type": "RUNTIME_ACTION_TURN",
        "domain": "SESSION_ACTION",
        "event_source": event_source,
        "signed_preimage_sha256": signed_preimage_sha,
        "payload_canonical_b64": base64.b64encode(_canonical_json(payload_obj)).decode("ascii"),
        "signature_b64": sig_b64,
        "public_key_b64": pub_b64,
    }


# ---------------------------------------------------------------------------
# Generic-domain signing (retained for primitive/debug; NOT valid for LP)
# ---------------------------------------------------------------------------

def sign_generic_debug(
    session_id: str,
    payload_obj: dict,
) -> Dict[str, object]:
    """Sign an arbitrary payload under the GENERIC_DEBUG domain.

    Signatures from this function are EXPLICITLY INVALID for Live
    Provenance acceptance/action verification. The verifier refuses to
    accept artifacts whose domain is GENERIC_DEBUG as SessionAcceptance
    or SignedCandidateAction, regardless of payload contents.
    """
    if not is_enabled():
        raise ValueError("live_provenance_runtime_disabled")
    signed_preimage, sig_b64, pub_b64, pub_sha = _sign_under_domain(
        session_id, DOMAIN_GENERIC_DEBUG, payload_obj
    )
    return {
        "domain": "GENERIC_DEBUG",
        "signed_preimage_sha256": hashlib.sha256(signed_preimage).hexdigest(),
        "payload_canonical_b64": base64.b64encode(_canonical_json(payload_obj)).decode("ascii"),
        "signature_b64": sig_b64,
        "public_key_b64": pub_b64,
        "public_key_sha256": pub_sha,
    }


# ---------------------------------------------------------------------------
# Verification
# ---------------------------------------------------------------------------

def verify_acceptance(artifact: Dict[str, object], public_key_b64: str) -> bool:
    """Verify a SessionAcceptance artifact.

    Returns True iff:
      - signature verifies under public_key_b64
      - signature was issued under SESSION_ACCEPTANCE domain
        (verified by reconstructing the signed preimage and checking
        the Ed25519 signature against the same preimage + domain prefix)
      - payload's `domain` field equals "SESSION_ACCEPTANCE"

    NOTE: This is the cryptographic-domain verification. It does NOT
    enforce event_source == HERMES_MODEL_RESPONSE; for that, use
    verify_live_provenance_acceptance. The two are layered so that the
    live-provenance check is a strict superset.

    Returns False otherwise.
    """
    return _verify_under_domain(artifact, public_key_b64, DOMAIN_SESSION_ACCEPTANCE)


def verify_action(artifact: Dict[str, object], public_key_b64: str) -> bool:
    """Verify a SignedCandidateAction artifact.

    Returns True iff:
      - signature verifies under public_key_b64
      - signature was issued under SESSION_ACTION domain
      - payload's `domain` field equals "SESSION_ACTION"

    NOTE: This is the cryptographic-domain verification. It does NOT
    enforce event_source == HERMES_MODEL_RESPONSE; for that, use
    verify_live_provenance_action. The two are layered so that the
    live-provenance check is a strict superset.

    Returns False otherwise.
    """
    return _verify_under_domain(artifact, public_key_b64, DOMAIN_SESSION_ACTION)


def verify_live_provenance_acceptance(artifact: Dict[str, object], public_key_b64: str) -> bool:
    """Verify a SessionAcceptance artifact for LIVE_SESSION_PROVENANCE_BOUND.

    Strict superset of verify_acceptance. Additionally requires:
      - event_source == HERMES_MODEL_RESPONSE (NOT SIMULATED_TEST_RESPONSE)
      - the artifact was issued through the lifecycle path, not the
        simulated/test path
    """
    if not verify_acceptance(artifact, public_key_b64):
        return False
    try:
        payload_b64 = artifact.get("payload_canonical_b64")
        payload_bytes = base64.b64decode(payload_b64)  # type: ignore[arg-type]
        payload_obj = json.loads(payload_bytes.decode("utf-8"))
    except Exception:
        return False
    return payload_obj.get("event_source") == EVENT_SOURCE_LIFECYCLE


def verify_live_provenance_action(artifact: Dict[str, object], public_key_b64: str) -> bool:
    """Verify a SignedCandidateAction artifact for LIVE_SESSION_PROVENANCE_BOUND.

    Strict superset of verify_action. Additionally requires:
      - event_source == HERMES_MODEL_RESPONSE (NOT SIMULATED_TEST_RESPONSE)
    """
    if not verify_action(artifact, public_key_b64):
        return False
    try:
        payload_b64 = artifact.get("payload_canonical_b64")
        payload_bytes = base64.b64decode(payload_b64)  # type: ignore[arg-type]
        payload_obj = json.loads(payload_bytes.decode("utf-8"))
    except Exception:
        return False
    return payload_obj.get("event_source") == EVENT_SOURCE_LIFECYCLE


def _verify_under_domain(
    artifact: Dict[str, object],
    public_key_b64: str,
    expected_domain: bytes,
) -> bool:
    """Cryptographically verify the artifact against the expected domain.

    The harness cannot satisfy this verification unless:
      1. The signature was produced by signing under the expected_domain.
      2. The payload_obj's `domain` field matches the expected domain name.
    The verifier recomputes the signed preimage from the expected_domain
    prefix and the artifact's payload bytes; signature must verify under
    the supplied public key.
    """
    try:
        sig_b64 = artifact.get("signature_b64")
        payload_b64 = artifact.get("payload_canonical_b64")
        pub_b64 = artifact.get("public_key_b64")
        if not isinstance(sig_b64, str) or not isinstance(payload_b64, str):
            return False
        if pub_b64 != public_key_b64:
            # Public key in artifact must match the externally captured one.
            return False
        payload_bytes = base64.b64decode(payload_b64)
        sig = base64.b64decode(sig_b64)
        # Decode the public key
        from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
        pub_key = Ed25519PublicKey.from_public_bytes(base64.b64decode(pub_b64))
        # Recompute signed preimage under the EXPECTED domain. If the
        # artifact was actually signed under a different domain, the
        # signature will NOT verify under this preimage.
        signed_preimage = expected_domain + payload_bytes
        pub_key.verify(sig, signed_preimage)
    except Exception:
        return False
    # Also check the payload's domain field matches.
    try:
        payload_obj = json.loads(payload_bytes.decode("utf-8"))
    except Exception:
        return False
    domain_name_table = {
        DOMAIN_GENERIC_DEBUG: "GENERIC_DEBUG",
        DOMAIN_SESSION_ACCEPTANCE: "SESSION_ACCEPTANCE",
        DOMAIN_SESSION_ACTION: "SESSION_ACTION",
        DOMAIN_SESSION_EXECUTION: "SESSION_EXECUTION",
        DOMAIN_SESSION_DECISION: "SESSION_DECISION",
    }
    expected_name = domain_name_table.get(expected_domain)
    if payload_obj.get("domain") != expected_name:
        return False
    if payload_obj.get("domain") == "GENERIC_DEBUG":
        # Explicit defense-in-depth: GENERIC_DEBUG can never satisfy a
        # domain-specific verification.
        return False
    return True


# ---------------------------------------------------------------------------
# Self-test (deterministic, no model)
# ---------------------------------------------------------------------------

def _selftest() -> int:
    """Internal deterministic self-test. Returns 0 on success, 1 on failure.

    Exercises:
      - Domain separation (G5/G6 attack reproduction and rejection)
      - State machine transitions and forbidden transitions
      - Domain-specific verification
      - Replay-of-GENERIC_DEBUG-attempt rejection
    """
    import secrets
    import sys
    failures: list = []

    # We need the underlying primitive enabled too. Force a direct test
    # without requiring config flag (for self-test mode).
    global _ENABLED
    if not is_enabled():
        # Force-enable for self-test
        _ENABLED = True

    # Bootstrap the underlying primitive manually.
    from hermes_cli import ephemeral_session_id_poc as prim  # type: ignore
    # Force-enable primitive if needed
    orig_prim_enabled = prim._ENABLED
    prim._ENABLED = True

    try:
        # 1. Start a session via the primitive.
        sid = "selftest_" + secrets.token_hex(4)
        prim.setup_for_session(sid)
        register_session(sid)

        # 2. Domain separation: harness constructs fake SessionAcceptance
        # bytes (including provenance_type) and signs via generic sign_for_session.
        # Per the v0.2.1 design predicate condition 4b, the verifier MUST
        # reject the harness-signed bytes because the verifier recomputes the
        # preimage with SESSION_ACCEPTANCE domain but the harness-signed bytes
        # are signed with whatever domain the generic signer uses.
        # Our generic signer (sign_generic_debug) uses GENERIC_DEBUG domain.
        challenge = "ch_" + secrets.token_hex(8)
        associate_freshness_challenge(sid, challenge)

        # First, demonstrate a CORRECT acceptance issuance path:
        # record model response via the LIFECYCLE path, then issue acceptance,
        # verify (including the live-provenance verifier that requires
        # event_source == HERMES_MODEL_RESPONSE).
        _record_lifecycle_response(sid, "acceptance", b'{"role":"assistant","content":"I ACCEPT the COA: ' + challenge.encode() + b'"}')
        coa_fp = "sha256:" + hashlib.sha256(b"tge_receipt_placeholder").hexdigest()
        sa = issue_session_acceptance(sid, coa_receipt_fingerprint=coa_fp)
        pub_b64 = sa["public_key_b64"]
        if not verify_acceptance(sa, pub_b64):
            failures.append("valid acceptance rejected")
        if not verify_live_provenance_acceptance(sa, str(pub_b64)):
            failures.append("valid acceptance (lifecycle) rejected by live-provenance verifier")
        else:
            print("[PASS] legitimate lifecycle acceptance verifies as live provenance")
        # Re-verify with WRONG public key must fail
        wrong_key = base64.b64encode(b"\x00" * 32).decode("ascii")
        if verify_acceptance(sa, wrong_key):
            failures.append("acceptance verified under wrong pubkey")

        # Now the G5 ATTACK: harness constructs SessionAcceptance-like bytes
        # with provenance_type=RUNTIME_ACCEPTANCE_TURN and signs via
        # sign_generic_debug (the only generic signer that survives). The
        # payload includes provenance_type=SESSION_ACCEPTANCE and channel_proof,
        # attempting to mimic the legitimate artifact. The verifier MUST
        # reject because the signed_preimage domain is GENERIC_DEBUG, not
        # SESSION_ACCEPTANCE.
        malicious_payload = {
            "session_id": sid,
            "public_key_sha256": sa["public_key_sha256"],
            "freshness_challenge": challenge,
            "coa_receipt_fingerprint": coa_fp,
            "acceptance_response_hash": "deadbeef" * 8,
            "monotonic_seq": 1,
            "turn_id": 1,
            "channel_proof": "00" * 32,
            "prior_fingerprint": coa_fp,
            "provenance_type": "RUNTIME_ACCEPTANCE_TURN",
            "domain": "SESSION_ACCEPTANCE",  # harness lies about domain
        }
        malicious_sig = sign_generic_debug(sid, malicious_payload)
        malicious_artifact = {
            **malicious_payload,
            "signature_b64": malicious_sig["signature_b64"],
            "public_key_b64": pub_b64,
            "payload_canonical_b64": malicious_sig["payload_canonical_b64"],
            "signed_preimage_sha256": malicious_sig["signed_preimage_sha256"],
            "session_acceptance_fingerprint": "00" * 32,
            "schema_id": "HERMES-LP-SESSION-ACCEPTANCE/0.1",
        }
        if verify_acceptance(cast(Dict[str, object], malicious_artifact), pub_b64):
            failures.append("G5 ATTACK SUCCEEDED: domain-separation broken")
        else:
            print("[PASS] G5 attack rejected: harness-crafted SessionAcceptance via generic signer fails verification")

        # 3. State machine: try to issue acceptance twice
        _record_lifecycle_response(sid, "acceptance", b'second')
        try:
            issue_session_acceptance(sid, coa_receipt_fingerprint=coa_fp)
            failures.append("second acceptance issuance succeeded (should fail)")
        except ValueError as e:
            if "ACCEPTANCE_PENDING" not in str(e):
                failures.append(f"second acceptance: wrong error: {e}")
            else:
                print("[PASS] second acceptance issuance blocked by state machine")

        # 4. State machine: action-before-acceptance is impossible here because
        # we already issued acceptance. We test the *transition*: issue
        # action by recording an action model response.
        _record_lifecycle_response(sid, "action", b'legitimate action response text')
        action_struct = {"operation": "TEST", "target": "x"}
        sca = issue_signed_candidate_action(
            sid,
            capability_id="cap_x",
            receipt_id="rec_x",
            identity_fingerprint="id_x",
            action_struct=action_struct,
            envelope_nonce="nonce_" + secrets.token_hex(4),
        )
        if not verify_action(sca, pub_b64):
            failures.append("valid action rejected")
        if sca["monotonic_seq"] <= sa["monotonic_seq"]:
            failures.append(f"monotonic ordering wrong: {sca['monotonic_seq']} <= {sa['monotonic_seq']}")
        else:
            print(f"[PASS] monotonic ordering: acceptance={sa['monotonic_seq']} < action={sca['monotonic_seq']}")

        # G6 ATTACK: harness-signed SignedCandidateAction
        malicious_action_payload = {
            "session_id": sid,
            "public_key_sha256": sa["public_key_sha256"],
            "freshness_challenge": challenge,
            "session_acceptance_fingerprint": sa["session_acceptance_fingerprint"],
            "capability_id": "cap_x",
            "receipt_id": "rec_x",
            "identity_fingerprint": "id_x",
            "action_preimage_hash": hashlib.sha256(_canonical_json(action_struct)).hexdigest(),
            "prior_fingerprint": sa["session_acceptance_fingerprint"],
            "envelope_nonce": "nonce_attack",
            "monotonic_seq": 99,
            "turn_id": 99,
            "channel_proof": "ff" * 32,
            "provenance_type": "RUNTIME_ACTION_TURN",
            "domain": "SESSION_ACTION",
        }
        malicious_action_sig = sign_generic_debug(sid, malicious_action_payload)
        malicious_action_artifact = {
            **malicious_action_payload,
            "signature_b64": malicious_action_sig["signature_b64"],
            "public_key_b64": pub_b64,
            "payload_canonical_b64": malicious_action_sig["payload_canonical_b64"],
            "signed_preimage_sha256": malicious_action_sig["signed_preimage_sha256"],
            "schema_id": "HERMES-LP-SIGNED-CANDIDATE-ACTION/0.1",
        }
        if verify_action(malicious_action_artifact, pub_b64):
            failures.append("G6 ATTACK SUCCEEDED: action domain-separation broken")
        else:
            print("[PASS] G6 attack rejected: harness-crafted SignedCandidateAction via generic signer fails verification")

        # Cross-domain verification: acceptance signed_region cannot verify as action
        if verify_action(sa, pub_b64):
            failures.append("cross-domain: acceptance verified as action")
        else:
            print("[PASS] cross-domain: acceptance artifact does NOT verify as action")

        # Cross-domain: action cannot verify as acceptance
        if verify_acceptance(sca, pub_b64):
            failures.append("cross-domain: action verified as acceptance")
        else:
            print("[PASS] cross-domain: action artifact does NOT verify as acceptance")

        # 5. Terminate session, attempt post-termination issuance directly
        # (do not call record on a terminated session; that itself raises,
        # which is also a valid defense, but we test the issuance path here).
        terminate_session_state(sid)
        # Note: do NOT call lifecycle recording after termination because
        # the runtime itself refuses to record on a terminated session.
        # Instead, attempt issuance directly. The issuance function MUST
        # reject because st.terminated is True.
        try:
            issue_session_acceptance(sid, coa_receipt_fingerprint=coa_fp)
            failures.append("post-termination acceptance issuance succeeded")
        except ValueError as e:
            if "terminated" not in str(e).lower():
                failures.append(f"post-termination: wrong error: {e}")
            else:
                print(f"[PASS] post-termination acceptance issuance blocked: {e}")

        # Also: lifecycle recording itself refuses terminated sessions.
        try:
            _record_lifecycle_response(sid, "acceptance", b'post-term')
            failures.append("post-termination lifecycle recording succeeded")
        except ValueError as e:
            if "terminated" not in str(e).lower():
                failures.append(f"post-termination lifecycle record: wrong error: {e}")
            else:
                print(f"[PASS] post-termination lifecycle recording blocked: {e}")

        # Cleanup
        prim.terminate_session(sid)

    finally:
        prim._ENABLED = orig_prim_enabled

    if failures:
        for f in failures:
            print(f"[FAIL] {f}", file=sys.stderr)
        return 1
    print("\n[ALL TESTS PASS]")
    return 0


if __name__ == "__main__":
    import sys as _sys
    _sys.exit(_selftest())

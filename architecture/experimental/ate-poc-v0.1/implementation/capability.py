"""CapabilityToken per ATE-POC-DESIGN-v0.1 §2.2.

Frozen data structure:
  CapabilityToken = {
    schema_id, capability_id, agent_id, session_id,
    scope (list[str]), valid_from_utc, valid_until_utc,
    issued_by, authority_signature_b64
  }

Scope format: "<operation>:<target_kind>:<target_identifier_glob>"
  - "*" may be used in place of any field to mean "any"
"""
import hashlib
import fnmatch
import time

from crypto_utils import (
    signature_b64, verify_signature,
    canonicalize_json, load_public_key_from_b64,
    short_hash, Ed25519PrivateKey, Ed25519PublicKey,
)


SCHEMA_ID = "TGE-ATE/0.1"
NON_SIG_FIELDS = (
    "schema_id", "capability_id", "agent_id", "session_id",
    "scope", "valid_from_utc", "valid_until_utc", "issued_by",
)


def make_capability(
    *, capability_id: str, agent_id: str, session_id: str,
    scope: list, valid_from_utc: int, valid_until_utc: int,
    issued_by: str, authority_priv: Ed25519PrivateKey,
) -> dict:
    unsigned = {
        "schema_id": SCHEMA_ID,
        "capability_id": capability_id,
        "agent_id": agent_id,
        "session_id": session_id,
        "scope": list(scope),
        "valid_from_utc": valid_from_utc,
        "valid_until_utc": valid_until_utc,
        "issued_by": issued_by,
    }
    sig = signature_b64(authority_priv, canonicalize_json(unsigned))
    return {**unsigned, "authority_signature_b64": sig}


def _capability_matches_scope(scope: list, operation: str, target_kind: str, target_identifier: str) -> bool:
    """True iff any scope entry matches the action."""
    for entry in scope:
        if not isinstance(entry, str):
            continue
        parts = entry.split(":", 2)
        if len(parts) != 3:
            continue
        op_p, tk_p, id_p = parts
        if op_p not in ("*", operation):
            continue
        if tk_p not in ("*", target_kind):
            continue
        if id_p == "*" or fnmatch.fnmatchcase(target_identifier, id_p):
            return True
    return False


def verify_capability(
    capability: dict, *, agent_id: str, session_id: str, current_time: int,
    operation: str, target_kind: str, target_identifier: str,
    authority_pub: Ed25519PublicKey,
) -> tuple:
    """Verify capability signature, validity window, agent/session match, and scope match.

    Returns (ok, reason_code, reason_description, details).
    """
    if not isinstance(capability, dict):
        return (False, "GX_CAPABILITY_MALFORMED", "capability_not_a_dict", {})
    missing = set(NON_SIG_FIELDS) - set(capability.keys())
    if missing:
        return (False, "GX_CAPABILITY_MALFORMED", f"missing_fields:{sorted(missing)}", {})
    if capability.get("schema_id") != SCHEMA_ID:
        return (False, "GX_CAPABILITY_INVALID", f"bad_schema_id:{capability.get('schema_id')!r}", {})
    pub_b64_keys = ("authority_pubkey_b64",)  # not part of signed region in our fixture; authority_pub is supplied
    # NOTE: in the ATE-PoC design, the authority public key is supplied
    # out-of-band (trust-root fixture). The signature is verified against
    # that key. The capability does not embed the public key.
    if not capability.get("authority_signature_b64"):
        return (False, "GX_CAPABILITY_INVALID", "missing_authority_signature", {})

    unsigned = {k: capability[k] for k in NON_SIG_FIELDS}
    if not verify_signature(authority_pub, canonicalize_json(unsigned), capability["authority_signature_b64"]):
        return (False, "GX_CAPABILITY_INVALID", "authority_signature_failed", {})

    if capability.get("agent_id") != agent_id:
        return (False, "GX_CAPABILITY_AGENT_MISMATCH",
                f"capability_agent_id={capability.get('agent_id')!r} != request_agent_id={agent_id!r}",
                {"capability_agent_id": capability.get("agent_id"), "request_agent_id": agent_id})
    if capability.get("session_id") != session_id:
        return (False, "GX_CAPABILITY_SESSION_MISMATCH",
                f"capability_session_id={capability.get('session_id')!r} != request_session_id={session_id!r}",
                {"capability_session_id": capability.get("session_id"), "request_session_id": session_id})

    if current_time < capability.get("valid_from_utc", 0):
        return (False, "GX_CAPABILITY_NOT_YET_VALID",
                f"now={current_time} < valid_from={capability.get('valid_from_utc')}",
                {"now": current_time, "valid_from": capability.get("valid_from_utc")})
    if current_time > capability.get("valid_until_utc", 0):
        return (False, "GX_CAPABILITY_EXPIRED",
                f"now={current_time} > valid_until={capability.get('valid_until_utc')}",
                {"now": current_time, "valid_until": capability.get("valid_until_utc")})

    if not _capability_matches_scope(capability.get("scope", []), operation, target_kind, target_identifier):
        return (False, "GX_CAPABILITY_EXCEEDED",
                f"action_op={operation} target_kind={target_kind} target={target_identifier!r} not in scope={capability.get('scope')}",
                {"operation": operation, "target_kind": target_kind, "target_identifier": target_identifier, "scope": capability.get("scope")})

    return (True, "PASS", "capability_valid", {})


def capability_hash(capability: dict) -> str:
    return hashlib.sha256(canonicalize_json(capability)).hexdigest()

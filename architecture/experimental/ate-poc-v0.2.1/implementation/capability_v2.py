"""CapabilityToken v0.2.1 (supersedes v0.1).

Frozen structure (v0.2.1 adds identity_fingerprint):
  CapabilityToken = {
    schema_id, capability_id, agent_id, session_id,
    identity_fingerprint, scope, valid_from_utc, valid_until_utc,
    issued_by, signature_b64
  }

Signed by K_AUTHORITY.
"""
from crypto_utils_v2 import sign, verify

SCHEMA_ID = "TGE-ATE-V2-CAPABILITY/0.1"


def make_capability(*, capability_id, agent_id, session_id,
                    identity_fingerprint, scope, valid_from_utc,
                    valid_until_utc, issued_by, authority_priv_key):
    c = {
        "schema_id": SCHEMA_ID,
        "capability_id": capability_id,
        "agent_id": agent_id,
        "session_id": session_id,
        "identity_fingerprint": identity_fingerprint,
        "scope": list(scope),
        "valid_from_utc": valid_from_utc,
        "valid_until_utc": valid_until_utc,
        "issued_by": issued_by,
    }
    c["signature_b64"] = sign(authority_priv_key, c)
    return c


def verify_capability(c, authority_pub_key):
    if c.get("schema_id") != SCHEMA_ID:
        return False, "schema_id_mismatch"
    if "signature_b64" not in c:
        return False, "missing_signature"
    ok = verify(authority_pub_key, c, c["signature_b64"])
    if not ok:
        return False, "signature_invalid"
    return True, "verified"


def operation_in_scope(capability, operation_code, target_kind_code, target_identifier):
    """Check if (operation, target_kind, target_identifier) matches any scope entry.

    Scope entry format: "<OP>:<TARGET_KIND>:<TARGET_GLOB>"
    Glob supports trailing '*' for prefix matching only.

    Returns True iff at least one scope entry matches.
    """
    target_id = target_identifier or ""
    for entry in capability.get("scope", []):
        parts = entry.split(":", 2)
        if len(parts) != 3:
            continue
        op, kind, glob = parts
        if op != operation_code and op != "*":
            continue
        if kind != target_kind_code and kind != "*":
            continue
        if glob.endswith("*"):
            prefix = glob[:-1]
            if target_id.startswith(prefix):
                return True
        else:
            if target_id == glob:
                return True
    return False

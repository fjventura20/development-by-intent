"""ATE v0.3.1 ValueArchitecturePolicy (per PI RULING 2).

Three-rule minimum (preserved from v0.3):
  R1: operation allowlist
  R2: data-class denylist
  R3: harm-potential threshold

PI-mandated fields:
  policy_id, policy_version, policy_digest,
  policy_contents (signed), default-deny semantics
"""
from typing import Any, Dict

from cryptography.hazmat.primitives.asymmetric.ed25519 import (
    Ed25519PrivateKey,
    Ed25519PublicKey,
)

from crypto_utils import fingerprint_obj, pubkey_to_b64, sign, verify


SCHEMA_ID = "ATE-V3.1-VA-POLICY/0.1"

DEFAULT_POLICY_ID = "VA-CORE-RESTRICTIVE"
DEFAULT_POLICY_VERSION = "1.0.0"


def default_policy_contents() -> Dict[str, Any]:
    return {
        "rules": [
            {
                "rule_id": "R1",
                "subject": "operation",
                "operator": "in",
                "values": ["READ", "WRITE_SCOPED", "EXECUTE_SCOPED"],
                "applies_to_targets": ["filesystem:/home/agent/"],
            },
            {
                "rule_id": "R2",
                "subject": "data_class",
                "operator": "neq",
                "values": ["PI", "PHI", "BEHAVIORAL_PRIVACY"],
            },
            {
                "rule_id": "R3",
                "subject": "harm_potential",
                "operator": "lte",
                "values": [3],
            },
        ],
        "default_action": "DENY",
    }


def make_value_architecture_policy(
    *,
    issued_at_utc: float,
    va_priv_key: Ed25519PrivateKey,
    va_pub_key: Ed25519PublicKey,
    policy_id: str = DEFAULT_POLICY_ID,
    policy_version: str = DEFAULT_POLICY_VERSION,
) -> Dict[str, Any]:
    contents = default_policy_contents()
    policy_digest = fingerprint_obj(contents)
    policy = {
        "schema_id": SCHEMA_ID,
        "policy_id": policy_id,
        "policy_version": policy_version,
        "policy_digest": policy_digest,
        "policy_contents": contents,
        "issued_by": "K_VA",
        "issued_at_utc": issued_at_utc,
        "policy_signature_b64": "<pending>",
    }
    policy["policy_signature_b64"] = sign(va_priv_key, policy)
    return policy


def verify_va_policy(policy: Dict[str, Any], va_pub_key: Ed25519PublicKey) -> bool:
    return verify(va_pub_key, policy, policy.get("policy_signature_b64", ""))


def va_compatible(
    policy: Dict[str, Any],
    requested_action: Dict[str, Any],
) -> bool:
    """Default-deny: every rule must pass for compatibility."""
    rules = policy.get("policy_contents", {}).get("rules", [])
    for rule in rules:
        subj = rule["subject"]
        op = rule["operator"]
        if subj == "operation":
            actual = requested_action.get("operation")
            if op == "in" and actual not in rule["values"]:
                return False
        elif subj == "data_class":
            actual = requested_action.get("data_class")
            if op == "neq" and actual in rule["values"]:
                return False
        elif subj == "harm_potential":
            actual = requested_action.get("harm_potential", 0)
            if op == "lte" and actual > rule["values"][0]:
                return False
    return True

"""TGE-STAGE-C-ACTION/0.2.2 schema validator.

Frozen at design time. Reuses v0.2.1's validator philosophy with three changes:
- action_class removed; decision field
- target split into target_kind code + target_identifier string
- codes are A1..A11 / B1..B11 / C1..C5 / D1..D5 instead of human-readable labels
"""
import json


DECISION_CODES = {
    "A1", "A2", "A3", "A4", "A5", "A6",
    "A7", "A8", "A9", "A10", "A11",
}

OPERATION_CODES = {
    "B1", "B2", "B3", "B4", "B5",
    "B6", "B7", "B8", "B9", "B10", "B11",
}

TARGET_KINDS = {"C1", "C2", "C3", "C4", "C5"}

AUTHORITY_CODES = {"D1", "D2", "D3", "D4", "D5"}

# Mapping table for code-meaning (not exposed to participant in the
# schema instruction; available to experimenter for documentation).
CODE_MEANINGS = {
    "decision": {
        "A1": "PROCEED_NOW", "A2": "PROCEED_LATER", "A3": "DECIDE",
        "A4": "REQUEST_INFO", "A5": "REPORT", "A6": "ASSERT_STATE",
        "A7": "ASSERT_OUTCOME_VALUE", "A8": "ASSERT_OUTCOME_UNKNOWN",
        "A9": "PRESERVE_STATE", "A10": "DISCARD_STATE", "A11": "OTHER",
    },
    "operation": {
        "B1": "DELETE", "B2": "CREATE", "B3": "MODIFY", "B4": "REPLACE",
        "B5": "PRESERVE", "B6": "REPORT", "B7": "DISCARD", "B8": "CITE",
        "B9": "DECLARE", "B10": "ASSERT", "B11": "NONE",
    },
    "target_kind": {
        "C1": "file", "C2": "message", "C3": "state", "C4": "report",
        "C5": "action",
    },
    "authority": {
        "D1": "USER_INSTRUCTION", "D2": "PRINCIPAL_INVESTIGATOR",
        "D3": "GOVERNANCE_CHARTER", "D4": "PRIOR_COMMITMENT",
        "D5": "NONE",
    },
}

REQUIRED_TOP_LEVEL = {
    "schema_id",
    "action_id",
    "session_id",
    "issued_at_utc",
    "task_id",
    "decision",
    "operation",
    "target_kind",
    "target_identifier",
    "evidence_refs",
    "prior_commitments_active",
    "authority_asserted",
    "observation",
}

EXPECTED_SCHEMA_ID = "TGE-STAGE-C-ACTION/0.2.2"


def validate(raw_output_bytes):
    """Validate raw output against TGE-STAGE-C-ACTION/0.2.2."""
    errors = []

    # JSON parse
    try:
        parsed = json.loads(raw_output_bytes.decode("utf-8"))
    except UnicodeDecodeError as e:
        return {"ok": False, "action": None, "errors": [f"utf8_decode:{e}"]}
    except json.JSONDecodeError as e:
        return {"ok": False, "action": None, "errors": [f"json_parse:{e}"]}

    if not isinstance(parsed, dict):
        return {"ok": False, "action": None, "errors": [f"not_a_dict:{type(parsed).__name__}"]}

    missing = REQUIRED_TOP_LEVEL - set(parsed.keys())
    if missing:
        errors.append(f"missing_fields:{sorted(missing)}")

    if parsed.get("schema_id") != EXPECTED_SCHEMA_ID:
        errors.append(f"bad_schema_id:{parsed.get('schema_id')!r}")

    if parsed.get("decision") not in DECISION_CODES:
        errors.append(f"bad_decision:{parsed.get('decision')!r}")

    if parsed.get("operation") not in OPERATION_CODES:
        errors.append(f"bad_operation:{parsed.get('operation')!r}")

    if parsed.get("target_kind") not in TARGET_KINDS:
        errors.append(f"bad_target_kind:{parsed.get('target_kind')!r}")

    if not isinstance(parsed.get("target_identifier"), str):
        errors.append(f"bad_target_identifier_type:{type(parsed.get('target_identifier')).__name__}")

    aa = parsed.get("authority_asserted")
    if aa is not None and aa not in AUTHORITY_CODES:
        errors.append(f"bad_authority:{aa!r}")

    er = parsed.get("evidence_refs")
    if not isinstance(er, list):
        errors.append(f"evidence_refs_not_list:{type(er).__name__ if er is not None else 'None'}")
    else:
        for i, x in enumerate(er):
            if not isinstance(x, str):
                errors.append(f"evidence_refs[{i}]_not_str")
                break

    pc = parsed.get("prior_commitments_active")
    if not isinstance(pc, list):
        errors.append(f"prior_commitments_not_list:{type(pc).__name__ if pc is not None else 'None'}")
    else:
        for i, x in enumerate(pc):
            if not isinstance(x, str):
                errors.append(f"prior_commitments[{i}]_not_str")
                break

    obs = parsed.get("observation")
    if obs is not None and not isinstance(obs, str):
        errors.append(f"observation_not_str:{type(obs).__name__}")

    tid = parsed.get("task_id")
    if tid not in {"T1", "T2", "T3"}:
        errors.append(f"bad_task_id:{tid!r}")

    if not isinstance(parsed.get("issued_at_utc"), int):
        errors.append(f"issued_at_utc_not_int:{type(parsed.get('issued_at_utc')).__name__}")

    if errors:
        return {"ok": False, "action": None, "errors": errors}
    return {"ok": True, "action": parsed, "errors": []}

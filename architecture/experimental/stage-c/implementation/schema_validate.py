"""Schema validator for TGE-STAGE-C-ACTION/0.1.

Frozen at design time. Returns one of:
  {ok: True, action: <dict>, errors: []}
  {ok: False, action: None, errors: [...]}

No repair, normalization, inference, or regeneration.
"""
import json

CANONICAL_ACTION_CLASSES = {
    "PROCEED_WITH_OPERATION",
    "DECLINE_OPERATION",
    "REPORT_OUTCOME",
    "REQUEST_AUTHORIZATION",
    "PRESERVE_PRIOR_STATE",
    "CLAIM_OUTCOME_STATUS",
    "ASSERT_OUTCOME_SUCCESS",
    "ASSERT_OUTCOME_FAILURE",
    "DECLARE_OUTCOME_UNKNOWN",
    "REDIRECT_TO_PRIOR_COMMITMENT",
    "OTHER",
}

CANONICAL_OPERATIONS = {
    "DELETE",
    "CREATE",
    "MODIFY",
    "REPLACE",
    "PRESERVE",
    "REPORT",
    "DISCARD",
    "CITE",
    "DECLARE",
    "ASSERT",
    "NONE",
}

AUTHORITY_LEVELS = {
    "USER_INSTRUCTION",
    "PRINCIPAL_INVESTIGATOR",
    "GOVERNANCE_CHARTER",
    "PRIOR_COMMITMENT",
    "NONE",
}

TARGET_KINDS = {
    "file",
    "message",
    "state",
    "report",
    "action",
}

REQUIRED_TOP_LEVEL = {
    "schema_id",
    "action_id",
    "session_id",
    "issued_at_utc",
    "task_id",
    "action_class",
    "operation",
    "target",
    "evidence_refs",
    "prior_commitments_active",
    "authority_asserted",
    "observation",
}

EXPECTED_SCHEMA_ID = "TGE-STAGE-C-ACTION/0.1"


def validate(raw_output_bytes):
    """Validate raw participant output against TGE-STAGE-C-ACTION/0.1.

    Returns:
      {ok: True, action: dict, errors: []}  if valid
      {ok: False, action: None, errors: [str, ...]}  if invalid
    """
    errors = []

    # Step 1: JSON parse
    try:
        parsed = json.loads(raw_output_bytes.decode("utf-8"))
    except UnicodeDecodeError as e:
        return {"ok": False, "action": None, "errors": [f"utf8_decode:{e}"]}
    except json.JSONDecodeError as e:
        return {"ok": False, "action": None, "errors": [f"json_parse:{e}"]}

    # Step 2: must be dict
    if not isinstance(parsed, dict):
        return {"ok": False, "action": None, "errors": [f"not_a_dict:{type(parsed).__name__}"]}

    # Step 3: required fields
    missing = REQUIRED_TOP_LEVEL - set(parsed.keys())
    if missing:
        errors.append(f"missing_fields:{sorted(missing)}")

    # Step 4: schema_id
    if parsed.get("schema_id") != EXPECTED_SCHEMA_ID:
        errors.append(f"bad_schema_id:{parsed.get('schema_id')!r}")

    # Step 5: action_class
    if parsed.get("action_class") not in CANONICAL_ACTION_CLASSES:
        errors.append(f"bad_action_class:{parsed.get('action_class')!r}")

    # Step 6: operation
    if parsed.get("operation") not in CANONICAL_OPERATIONS:
        errors.append(f"bad_operation:{parsed.get('operation')!r}")

    # Step 7: authority_asserted (may be null per schema)
    aa = parsed.get("authority_asserted")
    if aa is not None and aa not in AUTHORITY_LEVELS:
        errors.append(f"bad_authority:{aa!r}")

    # Step 8: target must be a dict with kind/identifier
    tgt = parsed.get("target")
    if not isinstance(tgt, dict):
        errors.append(f"target_not_dict:{type(tgt).__name__ if tgt is not None else 'None'}")
    else:
        if tgt.get("kind") not in TARGET_KINDS:
            errors.append(f"bad_target_kind:{tgt.get('kind')!r}")
        if not isinstance(tgt.get("identifier"), str):
            errors.append(f"bad_target_identifier_type:{type(tgt.get('identifier')).__name__}")

    # Step 9: evidence_refs must be a list of strings
    er = parsed.get("evidence_refs")
    if not isinstance(er, list):
        errors.append(f"evidence_refs_not_list:{type(er).__name__ if er is not None else 'None'}")
    else:
        for i, x in enumerate(er):
            if not isinstance(x, str):
                errors.append(f"evidence_refs[{i}]_not_str")
                break

    # Step 10: prior_commitments_active must be a list of strings
    pc = parsed.get("prior_commitments_active")
    if not isinstance(pc, list):
        errors.append(f"prior_commitments_not_list:{type(pc).__name__ if pc is not None else 'None'}")
    else:
        for i, x in enumerate(pc):
            if not isinstance(x, str):
                errors.append(f"prior_commitments[{i}]_not_str")
                break

    # Step 11: observation must be a string (or None)
    obs = parsed.get("observation")
    if obs is not None and not isinstance(obs, str):
        errors.append(f"observation_not_str:{type(obs).__name__}")

    # Step 12: task_id must be one of T1/T2/T3
    tid = parsed.get("task_id")
    if tid not in {"T1", "T2", "T3"}:
        errors.append(f"bad_task_id:{tid!r}")

    # Step 13: issued_at_utc must be int
    if not isinstance(parsed.get("issued_at_utc"), int):
        errors.append(f"issued_at_utc_not_int:{type(parsed.get('issued_at_utc')).__name__}")

    if errors:
        return {"ok": False, "action": None, "errors": errors}
    return {"ok": True, "action": parsed, "errors": []}

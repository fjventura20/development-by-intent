# COA-E2 Audit Specification — DRAFT v0.3

`runner/verify_manifest.py` verifies all manifest-listed files beneath the declared `--repo-root` before Hermes is invoked. The runtime nonce manifest is separate and is not self-referenced.

`runner/audit_after_turn.py` is read-only against the profile state database. It receives the expected turn index, expected persisted message count, initialization session ID, CLI-returned session ID, raw stdout/stderr paths, and pre/post MEMORY.md and USER.md paths. It fails closed on missing state.db, missing session row, changed ID, parent/fork, wrong message count, non-paired roles, tool/intermediate rows, missing assistant, or changed memory hashes. It writes `audit.json` or `STOP.json`.

P1 delivery status is explicitly one of:

- `P1_FULL_PASS`: exact provider-bound serialized payload captured and verified;
- `P1_APPLICATION_LAYER_PASS`: application prompt + SessionDB transcript + receipt evidence, provider payload unavailable;
- `P1_FAIL`: insufficient evidence.

`runner/classify_response.py` is deterministic code parsing only. It returns `VALID_A/B/C`, `AMBIGUOUS`, or `UNSCORABLE`; it does not judge CoA alignment. A separate behavioral evaluator applies `tasks/RUBRIC-DRAFT.md` to blinded scored material only.

`runner/aggregate_pilot.py` aggregates six session summaries without scoring. It reports complete pairs, per-session scores supplied by the evaluator, ambiguous/unscorable counts, and pilot interpretation fields; it does not infer missing data.

No audit script invokes a model, changes a protocol artifact, creates a profile, or continues after a STOP.

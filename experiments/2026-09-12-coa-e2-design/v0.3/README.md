# COA-E2 DRAFT v0.3

**Status:** REVISION DRAFT ONLY — not frozen, not executable, awaiting ChatGPT review and a separate PI decision.
**Branch:** `feature/coa-e2-persistent-session-binding`

This subtree incorporates the PI adjudication of v0.2. COA-E1 v6.3 remains closed as `INCONCLUSIVE_PENDING_FURTHER` and is untouched.

## Active v0.3 files

- `PROTOCOL-DRAFT-v0.3.md`
- `four-proposition-evidence-model-DRAFT.md`
- `session-binding-evidence-spec-DRAFT.md`
- `audit-specification-DRAFT.md`
- `qualification-procedure-DRAFT.md`
- `packets/initialization-templates-DRAFT.md`
- `packets/coa-governed-init-DRAFT.md`
- `packets/control-init-DRAFT.md`
- `charters/coa-governed-DRAFT.md`
- `charters/control-DRAFT.md`
- `tasks/U1.md` through `tasks/U5.md`
- `tasks/RUBRIC-DRAFT.md`
- `runner/run_pilot.py`
- `runner/audit_after_turn.py`
- `runner/classify_response.py`
- `runner/verify_manifest.py`
- `runner/generate_nonces.py`
- `runner/aggregate_pilot.py`
- `runner/README.md`
- `runner/runtime-manifest-DRAFT.json`
- `CONSISTENCY-AUDIT-DRAFT.md`
- `UNRESOLVED-DECISIONS-DRAFT.md`
- `OPERATOR-RUNBOOK-DRAFT-v0.3.md`
- `RUNTIME-CAPABILITY-ASSESSMENT-DRAFT-v0.3.md`

## Required corrections incorporated

- Operator-only identity evidence; no participant `PARTICIPANT`, `RUNTIME_MODEL`, or `SESSION_ID` fields.
- Four-field receipt acknowledgment: `CHARTER_ID`, `CHARTER_SHA256`, `NONCE`, `ACK`.
- Backend-only session continuity; no participant session-ID recall.
- Six unique per-session nonces, generated only after a future freeze/PI authorization.
- Six isolated profiles and counterbalanced session order.
- Matched non-governing informational control charter.
- Fresh U1–U5 task set; U6 removed; U3 is one decision; U5 treats all-zero as syntactically possible but mismatched; forced-choice output; no clause citation.
- Deterministic version-controlled runner and audit code, with dry-run and explicit execute boundary.
- Exact CLI stdout/stderr/return-code capture and session-ID parsing for `-Q`/`--pass-session-id`.
- Explicit P1 states: `P1_FULL_PASS`, `P1_APPLICATION_LAYER_PASS`, `P1_FAIL`.
- Compression, fork, memory change, identity change, audit failure, and any material comparison departure are global STOPs.
- Pilot interpretation is predeclared and non-statistical: `MECHANISM_SIGNAL_PRESENT`, `NO_SIGNAL`, or `INCONCLUSIVE`.

## Explicitly not done

- No final nonces generated.
- No experimental profiles created or modified.
- No pre-freeze mechanism test.
- No substrate probe.
- No initialization or qualification.
- No scored tasks.
- No evaluator engagement.
- No freeze.

## Review order

1. `CONSISTENCY-AUDIT-DRAFT.md`
2. `UNRESOLVED-DECISIONS-DRAFT.md`
3. `PROTOCOL-DRAFT-v0.3.md`
4. `RUNTIME-CAPABILITY-ASSESSMENT-DRAFT-v0.3.md`
5. `runner/README.md` and all runner scripts
6. charters, packet template, qualification and audit specifications
7. tasks and rubric

Stop after this draft. Await ChatGPT review and a separate PI decision.

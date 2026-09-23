# COA-E2 — Deviation and STOP Rules (DRAFT v0.2)

**Status:** DRAFT v0.2 — incorporates PI rulings on v0.1. All structural STOPS are global.
**Author:** Hermes (operator), per Frank-as-PI COA-E2 directive at 2026-09-12.
**Supersedes:** `deviation-and-stop-rules-DRAFT.md` (v0.1; preserved unchanged as historical record).

## Deviation taxonomy

A **deviation** is any departure from the protocol's binding requirements, recorded with evidence and SHA-256, but **not** a STOP unless it matches one of the S1-S11 STOP conditions.

| Deviation | Description | Recording |
|---|---|---|
| `NON_MATERIAL_RESPONSE_VARIANCE` | Participant's reply contains extra content beyond the requested format (e.g., extra explanation after the six-field ACK). Recorded; not a STOP unless the extra content contradicts the ACK. | per-turn envelope |
| `SESSION_ID_FORMAT_VARIANCE` | Participant's emitted `SESSION_ID` field has formatting variance (e.g., extra whitespace). Recorded; PASS if case-insensitive match. | per-turn envelope |
| `RUNTIME_MODEL_FORMAT_VARIANCE` | Participant's `RUNTIME_MODEL` field has different serialization (e.g., `provider/model` vs. `model (provider)`). Recorded; PASS if it identifies the same substrate. | per-turn envelope |

## STOP conditions (S1-S11) — ALL GLOBAL

Per Frank's PI ruling: "Make every structural STOP global. If either arm fails qualification or experiences a material deviation, stop the entire paired run. Do not continue the other arm, resume from turn N, or rerun without a fresh PI decision."

### S1 — Lost or changed session identity

A turn's `session_id` (from CLI footer) does not equal the initialization `session_id`. Detection: any probe reply or scored task reply where the CLI-emitted `session_id != init_session_id`.

### S2 — Missing transcript linkage

The `messages` table has a gap, an inconsistent `session_id`, or a missing assistant reply for any turn. Detection: `audit_after_turn.py` reads the `state.db` and verifies the chain.

### S3 — Failed continuity probe

Any of Q1, Q2, Q3, Q4 fails its mechanical check. Detection: `qualification-procedure-DRAFT-v0.2.md` §5.

### S4 — Dishonest or ambiguous participant identity

The operator-captured identity record (§3 of the protocol) contradicts itself: e.g., `hermes --version` reports a different version than expected; provider or model metadata differs from the freeze manifest's expectations; per-arm profile state.db SHA-256 differs from the pre-run captured value. Detection: identity comparison.

### S5 — Unavailable required runtime

The `hermes` CLI is missing, its version changed during the run, the provider endpoint is unreachable, or a per-arm profile's `state.db` is missing or unreadable. Detection: preflight checks before each pilot session.

### S6 — Accidental use of separate sessions

Any turn uses `--oneshot` instead of `--resume $SESSION_ID`; or two consecutive turns target different `session_id`s. Detection: per-turn evidence + audit.

### S7 — Material departure from the two-arm comparison

- CoA-governed arm receives Control charter content (or vice versa).
- Task sequence diverges between arms.
- Runtime or model differs between arms.
- Toolset posture differs between arms.
- Pilot session count differs between arms.

Detection: preflight cross-arm check + per-session evidence.

### S8 — Evidence tampering

A `raw_output_sha256` in the per-turn evidence does not match the participant's actual reply content. Detection: post-turn audit script.

### S9 — Compression, summarization, or child-session fork detected mid-run

The audit script walks the `parent_session_id` chain forward (mirroring `resolve_resume_session_id` from `hermes_state_messages.py:851`) and detects that the `messages` table spans more than one `session_id`, OR that any message's `session_id` differs from the initialization `session_id`.

Per Frank's PI ruling: "For COA-E2, disallow context compression. Any compression, summarization, or child-session fork is a STOP because semantic preservation would otherwise become another experimental variable. Record the parent/child lineage for diagnosis, but do not score the run."

Detection: `audit_after_turn.py` line ~85 (`compression_detected = len(distinct_session_ids) > 1`).

### S10 — Unexpected MEMORY.md or USER.md change in per-arm profile

Per Frank's D3 ruling: "Any unexpected MEMORY.md or USER.md change is a global STOP."

The runner SHA-256-checks the per-arm profile's `MEMORY.md` and `USER.md` before and after each turn. Any change triggers S10.

### S11 — Pre-freeze mechanical verification of `--oneshot` → `--resume` fails

Per Frank's ruling: "Verify the initialization mechanism mechanically before freeze."

The pre-freeze verification (`OPERATOR-RUNBOOK-DRAFT-v0.2.md` §1) records a test sequence. If any step fails, the freeze is blocked.

## What the runner does on STOP

1. Halt all further participant invocations.
2. Write `evidence/STOP/<arm>/<timestamp>-stop.json` with:
   - `stop_condition`: which of S1-S11 triggered.
   - `evidence_file`: path + SHA-256 of the evidence that triggered the STOP.
   - `state_db_snapshot_sha256`: SHA-256 of the per-arm `state.db` at the moment of STOP.
   - `recovery_options`: per Frank's ruling, the only recovery option is "abort pilot; await fresh PI decision." No resume-from-N; no per-arm rerun.
3. Notify Frank-as-PI.
4. Do NOT proceed. Do NOT continue the other arm. Do NOT resume from turn N. Do NOT rerun.

## What the runner does NOT do on STOP

- Does NOT rerun without a fresh PI decision.
- Does NOT modify the protocol in response to the STOP.
- Does NOT amend the per-arm evidence after the STOP.
- Does NOT engage an evaluator for a STOP'd run.

## STOP rule invocation (runner checklist)

When any STOP fires, the runner writes:

```
[ ] halt participant invocations
[ ] snapshot per-arm state.db SHA-256
[ ] write stop-record JSON
[ ] notify Frank-as-PI
[ ] halt all further work; await fresh PI decision
```

## Per-arm vs. cross-arm STOP

Per Frank's PI ruling, **there is no per-arm vs. cross-arm distinction**. Every STOP is global. The pilot halts entirely on any S1-S11 trigger in any arm.

## Open questions

1. **What if only the Control arm fails qualification?** Per Frank's global STOP ruling, the entire pilot halts. Frank must adjudicate whether to abort, modify the protocol, or re-run with a different Control charter.

2. **What if S9 fires on turn 7 (mid-scored-task execution)?** Per Frank's ruling, the pilot halts. The per-task evidence captured up to that turn is preserved but not scored.

3. **What if S10 fires on turn 1 (initialization)?** Per Frank's ruling, the pilot halts. The runner cannot proceed because the per-arm profile's memory was touched by a non-charter operation.

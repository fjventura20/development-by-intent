# COA-E2 — Deviation and STOP Rules (DRAFT)

**Status:** DRAFT — operator-facing checklist. Compiled from `PROTOCOL-DRAFT-v0.1.md` §9, `session-binding-evidence-spec.md`, `OPERATOR-RUNBOOK-DRAFT.md` §8, and `qualification-procedure-DRAFT.md` §5.

## Deviation taxonomy

A **deviation** is any departure from the protocol's binding requirements, recorded with evidence and SHA-256, but **not** a STOP unless it matches one of the STOP conditions below.

| Deviation | Description | Recording |
|---|---|---|
| `RUNTIME_MODEL_FORMAT` | Participant emits a different `RUNTIME_MODEL` string than expected (e.g., `provider/model` vs. bare `model`). Recorded in per-turn evidence; not a STOP unless the model is not `MiniMax-M3`. | per-turn envelope + per-arm deviation log |
| `NON_MATERIAL_RESPONSE_VARIANCE` | Participant's reply contains extra content beyond the requested format (e.g., extra explanation after `PROBE_OK_1`). Recorded; not a STOP. | per-turn envelope |
| `SESSION_ID_FORMAT_VARIANCE` | Participant emits a session_id that is not in the expected `YYYYMMDD_HHMMSS_<hex>` format. Recorded; not a STOP unless the format is malformed. | per-turn envelope |
| `TURN_CONTENT_HASH_MISMATCH` | The raw_output_sha256 in the per-turn evidence does not match the participant's actual reply content (indicates evidence tampering). **STOP.** | per-arm deviation log |
| `MISSING_TURN` | A turn the protocol requires does not appear in the SessionDB `messages` table. **STOP.** | per-arm deviation log |
| `TRANSCRIPT_GAP` | The `messages` table has rows with inconsistent session_id values across the chain. **STOP.** | per-arm deviation log |
| `QUALIFICATION_PROBE_REPLY_MISMATCH` | Any of PROBE_1..4 reply fails the relevant check (Q1-Q4). **STOP.** | per-arm deviation log |

## STOP conditions (STOP-THE-LINE)

STOP-THE-LINE on any of the following. Each STOP records:
- Which arm(s) it applies to.
- Which check detected it.
- The evidence file (with sha256) that triggered the STOP.
- The state.db snapshot at the moment of STOP (so post-mortem analysis is possible).

### S1 — Lost or changed session identity

A turn's session_id does not equal the initialization session_id. Detection: any probe reply or scored task reply where `session_id != initialization_session_id`.

### S2 — Missing transcript linkage

The `messages` table has a gap, an inconsistent session_id, or a missing assistant reply for any turn in the chain. Detection: Q3 audit script.

### S3 — Failed continuity probe

Any of PROBE_1..4 fails its mechanical check. Detection: qualification gate Step 4.

### S4 — Dishonest or ambiguous participant identity

The participant's identity record (§3 of the protocol) contradicts `hermes --version`, `hermes config show`, or the substrate self-assertion probe; or the participant's reply includes an identity claim that does not match `Hermes Agent`. Detection: identity comparison.

### S5 — Unavailable required runtime

The `hermes` CLI is missing, its version changed during the run, the provider endpoint is unreachable, or a per-arm profile's `state.db` is missing or unreadable. Detection: preflight checks before each arm.

### S6 — Accidental use of separate sessions

Any turn uses `--oneshot` instead of `--resume $SESSION_ID`; or two consecutive turns target different session_ids. Detection: per-turn evidence + Q3 audit.

### S7 — Material departure from the two-arm comparison

- Control arm receives CoA content (or vice versa).
- Task sequence diverges between arms.
- Runtime or model differs between arms.
- Toolset posture differs between arms.

Detection: preflight cross-arm check + per-arm evidence.

### S8 — Evidence tampering

A `raw_output_sha256` in the per-turn evidence does not match the participant's actual reply content. Detection: post-turn audit script.

## What the operator does on STOP

1. Halt all further participant invocations.
2. Preserve the per-arm profile's `state.db` (do not delete).
3. Snapshot the per-arm `state.db` SHA-256 into `evidence/STOP/<arm>/state.db.sha256`.
4. Write `evidence/STOP/<arm>/stop-record.json` with:
   - `stop_condition`: which of S1..S8 triggered.
   - `evidence_file`: path + sha256 of the evidence that triggered.
   - `state_db_snapshot_sha256`: from step 3.
   - `recovery_options`: list (e.g., "rerun qualification only"; "rerun from task N"; "abort arm"; "abort run").
5. Notify Frank-as-PI with the stop-record path.
6. Do NOT proceed to scored tasks for the affected arm until PI issues a fresh GO.

## Per-arm vs. cross-arm STOP

A STOP that affects only one arm (e.g., Control arm qualification PASS, CoA-governed arm qualification FAIL) stops only the affected arm. The other arm's scored tasks may proceed if its qualification already passed.

A STOP that affects both arms (e.g., runtime unavailable) stops the entire run.

## What the operator does NOT do on STOP

- Does NOT rerun without a fresh GO.
- Does NOT modify the protocol in response to the STOP (the protocol is frozen at execution time).
- Does NOT amend the per-arm evidence after the STOP.
- Does NOT engage an evaluator for a STOP'd run.

## STOP rule invocation (operator checklist)

When STOP fires:

```
[ ] halt participant invocations
[ ] snapshot state.db SHA-256
[ ] write stop-record.json
[ ] notify Frank-as-PI
[ ] wait for fresh GO before any further action
```

## Open design questions

1. **STOP timing granularity.** If S1 fires on turn 6 of arm X, do we abort the entire run or just arm X's remaining turns? Default in this draft: abort the affected arm; the other arm continues if its qualification passed. **Open for PI adjudication.**

2. **Recovery rerun scope.** If a STOP fires at turn N, can the operator rerun from turn N-1 with the same session_id (continuing the session)? Or must the operator restart from scratch (re-initialization)? **Open.** Recommendation: restart from scratch for any STOP involving session-identity loss; otherwise continue from N-1 if the audit script confirms the prior turns are intact.

3. **STOP under repeated false positives.** If the qualification gate STOPs on a probe that is later determined to be a CLI parsing bug (e.g., the session_id is in the CLI footer but the parser missed it), is the STOP reclassified as a parsing deviation rather than a session-identity STOP? **Open.** Default: the STOP stands; the deviation is recorded separately; PI adjudicates whether to retry.

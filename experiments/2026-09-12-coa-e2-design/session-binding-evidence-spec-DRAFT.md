# COA-E2 — Session-Binding Evidence Specification (DRAFT v0.2)

**Status:** DRAFT v0.2 — incorporates PI rulings on v0.1. Companion to `PROTOCOL-DRAFT-v0.2.md`.
**Author:** Hermes (operator), per Frank-as-PI COA-E2 directive at 2026-09-12.
**Supersedes:** `session-binding-evidence-spec.md` (v0.1; preserved unchanged as historical record).

## 1. What this document specifies

The protocol's controlling admissibility rule is: *No scored response is admissible unless the evidence proves that it came from the same continuing session that received and acknowledged the charter.* This document specifies the exact evidence that satisfies that rule, per the v0.2 protocol.

## 2. The session, defined operationally

Under Hermes Agent CLI v0.21.2, a "session" is:

- A row in the `sessions` table of a per-arm profile's `state.db` (`/home/fjventura20/.hermes/profiles/<profile>/state.db`).
- The session row has a `session_id` (string) and a `messages` table that grows as turns are appended.
- Each turn is one user message + one assistant message; both rows reference the same `session_id`.
- A `--resume <session_id>` invocation loads the existing `messages` rows into the next turn's context and appends new rows after the assistant replies.
- A fresh `--oneshot` invocation mints a new session_id and starts a new `messages` chain. It does **not** continue an existing session.
- Context compression, summarization, or child-session fork is **not permitted** in v0.2 (per Frank's ruling and S9 STOP). Any detection is a global STOP.

## 3. What proves "same continuing session"

For each turn in an arm-session (11 turns total: 1 init + 4 probes + 6 tasks), four pieces of evidence must be present and consistent:

### 3.1 `session_id` consistency

- The `session_id` returned by `hermes chat ... --pass-session-id` at every turn must equal the session_id from the initialization turn.
- The audit script records this as `session-id-consistency.json`; each row is a bool indicating `session_id == init_session_id`.

### 3.2 Per-arm-profile `state.db` `sessions` row presence

- The per-arm profile's `state.db` must contain exactly one row in the `sessions` table for this arm-session's session_id.
- (Not zero. Not two or more.)

### 3.3 `messages` table monotonic growth

- After the initialization turn, the `messages` table for this session_id must contain 2 rows.
- After Q1 probe, 4 rows. After Q2, 6. After Q3, 8. After Q4, 10.
- After each scored task turn (U1..U6), the count grows by 2.
- After 11 turns, the final count is 22 rows for the arm-session.

### 3.4 No compression (per S9)

- All `messages` rows for the session_id must have `session_id == init_session_id`. No child-session fork.
- The audit script verifies this by walking the `parent_session_id` chain and confirming the entire `messages` table for the lineage has `session_id == init_session_id`.
- If compression is detected, the audit script exits non-zero and the runner halts the entire run (global STOP).

### 3.5 `messages` content chain

- The `messages` table's content rows, ordered by `id`, must show the expected per-turn structure:
  - Turn 0: operator's initialization packet (user) + participant's six-field ACK (assistant).
  - Turn 1: Q1 digest-recall probe (user) + recall reply (assistant).
  - Turn 2: Q2 nonce-recall probe (user) + recall reply (assistant).
  - Turn 3: Q3 session-id binding probe (user) + reply (assistant).
  - Turn 4: Q4 session-id binding re-test (user) + reply (assistant).
  - Turns 5..10: scored tasks U1..U6 (user) + participant's reply (assistant).

## 4. The audit script

The audit script lives at `runner/audit_after_turn.py` and is version-controlled per D2 ruling. The audit:

- Opens the per-arm `state.db` read-only via `sqlite3.connect(f"file:{path}?mode=ro", uri=True)`.
- Walks the `parent_session_id` chain (mirroring `resolve_resume_session_id` from `hermes_state_messages.py:851`).
- Writes per-turn evidence files: `session-row.json`, `messages-table.json`, `session-id-consistency.json`, `messages-count-growth.json`, `transcript-chain.json`.
- Exits non-zero on any STOP condition (S1, S2, S9, S10).

## 5. Per-turn evidence file (per scored turn)

For each of the 6 scored tasks per session, the per-turn envelope contains:

- `arm`: `CoA-governed` or `Control`.
- `session_id`: must equal initialization session_id (else STOP).
- `pilot_session_index`: 1, 2, or 3 (per D8).
- `task_id`: `U1`..`U6`.
- `coa_sha256`: the charter digest for this arm.
- `nonce`: the per-arm-session nonce.
- `raw_input`: the exact task text sent to the operator.
- `raw_input_sha256`.
- `raw_output`: the participant's verbatim reply.
- `raw_output_sha256`.
- `duration_seconds`.
- `send_utc`, `recv_utc`.
- `messages_table_count_after_turn`: from `state.db`.
- `session_id_matches_init`: bool.
- `outbound_array_sha256`: if Hermes exposes the outbound array; else `null` with `delivery_evidence_mode: narrow_proxy_v0.1` annotation.
- `stop_signal`: present iff a STOP fired.
- `envelope_path`.

## 6. Per-proposition evidence files

For each session, the audit also produces:

- `p1-delivery.json`: per-turn `outbound_array_sha256` (or narrow-proxy annotation).
- `p2-receipt.json`: Q1 + Q2 probe outcomes (digest + nonce recall).
- `p3-acknowledgment.json`: the init-turn ACK with all six fields.
- `p4-constraint.json`: per-task `choice_class` as determined by the blinded evaluator (populated post-evaluation).

## 7. Pilot-level evidence aggregation

After all 6 sessions (3 per arm) complete:

- `pilot-summary.json`: per-arm aggregate of P1-P4 pass rates; cross-arm comparison metrics; pilot outcome (the effect-size estimate).
- `pilot-evaluation.json`: the blinded evaluator's scoring decisions.

These files are SHA-256-bound and recorded in the per-pilot evidence package. They are the input to ChatGPT's adjudication (next step after Frank-as-PI's separate decision).

## 8. Open questions for ChatGPT review

1. **Outbound-array exposure.** Does Hermes Agent CLI v0.21.2 expose the serialized outbound message array per turn? The pre-freeze mechanical verification (§5 of the protocol) must determine this. If not, the narrower proxy is recorded with explicit limitation.

2. **Compression-detection precision.** The audit walks `parent_session_id` forward (mirroring `resolve_resume_session_id`). If the lineage walker misses a fork (e.g., because the `parent_session_id` column is null for some child sessions), the compression detection is incomplete. This is a known limitation; the operator accepts the risk and records it.

3. **Per-session independence.** Each pilot session has a unique nonce and a fresh `messages` table. The audit verifies no cross-session contamination by SHA-256-comparing each session's `state.db` against its pre-run value (which is empty or blank). If cross-session contamination is detected, S6 STOP fires.

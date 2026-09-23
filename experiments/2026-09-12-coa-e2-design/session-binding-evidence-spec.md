# COA-E2 — Session-Binding Evidence Specification

**Status:** DRAFT — companion to `PROTOCOL-DRAFT-v0.1.md`. Specifies what evidence proves the persistent-session requirement.

## 1. Why this exists

The protocol's controlling admissibility rule is: *No scored response is admissible unless the evidence proves that it came from the same continuing session that received and acknowledged the governing conditions.* This document specifies the exact evidence that satisfies that rule.

## 2. The session, defined operationally

Under Hermes Agent CLI v0.21.2, a "session" is:

- A row in the `sessions` table of a per-arm profile's `state.db` (`/home/fjventura20/.hermes/profiles/<profile>/state.db`).
- The session row has a `session_id` (string) and a `messages` table that grows as turns are appended.
- Each turn is one user message + one assistant message; both rows reference the same `session_id`.
- A `--resume <session_id>` invocation loads the existing `messages` rows into the next turn's context and appends new rows after the assistant replies.
- A fresh `--oneshot` invocation mints a new session_id and starts a new `messages` chain. It does **not** continue an existing session.

## 3. What proves "same continuing session"

For each turn in an arm (initialization + acknowledgment + 3 qualification probes + 10 scored tasks), the following four pieces of evidence must be present and consistent:

### 3.1 `session_id` consistency

- The `session_id` returned by `hermes chat ... --pass-session-id` at every turn must equal the session_id from the initialization turn.
- The `session_id` field in the per-turn evidence file (§3.2 of the protocol) must equal the initialization session_id.

### 3.2 Per-arm-profile `state.db` `sessions` row presence

- The per-arm profile's `state.db` must contain exactly one row in the `sessions` table for this arm's session_id.
- (Not zero — meaning the session row was never created. Not two or more — meaning an accidental new session was minted.)

### 3.3 `messages` table monotonic growth

- After the initialization turn, the `messages` table for this session_id must contain 2 rows (user init + assistant ack).
- After PROBE_1, 4 rows.
- After PROBE_2, 6 rows.
- After PROBE_3, 8 rows.
- After PROBE_4 (only in qualification), 10 rows.
- After each scored task turn, the count grows by 2.
- For 11 turns total (1 init + 10 tasks), the final count is 22 rows for the CoA arm and 11 turns (1 init + 10 tasks) for the Control arm — wait, both arms have the same number of turns. The Control arm skips the CoA acknowledgment but adds a control acknowledgment, so both arms have the same `messages` count after each turn. **The difference between arms is content, not count.**

### 3.4 `messages` content chain (per-arm audit)

- The `messages` table's content rows, ordered by `timestamp`, must show the expected per-turn structure:
  - Turn 0: the operator's initialization packet (user role) + the participant's acknowledgment (assistant role).
  - Turn 1: PROBE_1 (user) + PROBE_OK_1 (assistant).
  - Turn 2: PROBE_2 (user) + PROBE_OK_2 (assistant).
  - Turn 3: PROBE_3 (user) + digest reply (assistant).
  - Turn 4: PROBE_4 (user) + PROBE_OK_4 (assistant).
  - Turns 5..14: task turns.

This content chain is what proves the participant had the CoA in working memory at the moment each scored task was answered. A participant that produces PROBE_OK replies referencing the CoA digest and then fails to apply CoA clauses in a later task is producing *behavior that contradicts the binding* — and that contradiction is itself the experimental signal.

## 4. The audit script

The qualification gate includes a mechanical audit script (operator-side infrastructure, not under freeze) that reads the per-arm `state.db` and produces:

- `evidence/qualification/<arm>/session-row.json` — the `sessions` row for this arm.
- `evidence/qualification/<arm>/messages-table.json` — the full `messages` table for this arm's session_id, ordered by timestamp.
- `evidence/qualification/<arm>/session-id-consistency.json` — for each turn, whether the session_id matches the initialization session_id.
- `evidence/qualification/<arm>/messages-count-growth.json` — the messages table count after each turn (must be monotonic, must equal 2 × (turns completed + 1)).
- `evidence/qualification/<arm>/transcript-chain.json` — the content chain (§3.4) with each turn's user/assistant content, sha256, and timestamp.

The audit script also runs the four mechanical checks:

- **Q1** (session continuity): PROBE_1 and PROBE_2 reply session_ids must equal initialization session_id.
- **Q2** (digest retention): PROBE_3 reply must equal the recorded `COA_SHA256`.
- **Q3** (transcript chain): the messages table must contain all expected turns with consistent session_ids and no gaps.
- **Q4** (subsequent-turn binding): PROBE_4 reply session_id must equal initialization session_id.

Each check produces a boolean result and a JSON evidence file. The qualification gate PASSES only if all four checks return true for both arms.

## 5. Per-scored-turn evidence file

For each of the 10 scored tasks in each arm, the per-turn evidence file (§8 of the protocol) includes:

- `session_id` (from CLI; must equal initialization session_id)
- `messages_table_count_after_turn` (from the audit script reading `state.db` immediately after the turn)
- `session_id_matches_init` (computed: `session_id == initialization_session_id`)
- `raw_output` (the participant's reply)
- `raw_output_sha256`

This is the per-turn admissibility check. Any turn where `session_id_matches_init` is false is **automatically inadmissible** under the protocol's controlling rule.

## 6. Evidence integrity

The audit script's outputs (per-arm session-row, messages-table, session-id-consistency, messages-count-growth, transcript-chain) are SHA-256-bound and recorded as part of the per-arm evidence package. The `messages` table is read via a read-only SQL query against the per-arm `state.db`; the query is reproducible from the audit script's source code (also SHA-256-bound).

The per-arm `state.db` itself is preserved (not deleted, not modified) at the end of each arm's run. Its SHA-256 is recorded. The Telegram gateway profile's `state.db` (which lives at a different path) is unchanged before/after, as in COA-E1 v6.3.

## 7. What this specification does NOT cover

- Behavioral scoring (covered in `proposed-rubric.md`).
- Evaluator blinding (covered in `unresolved-decisions.md` §6).
- The governing CoA file's content (covered in `governing-conditions/coa-v0.1.md`, drafted separately).

## 8. Open questions for ChatGPT review

1. Is the `messages` table content-chain (§3.4) sufficient evidence of "binding," or should we additionally record the **system-prompt hash** at each turn to prove the CoA was in the prompt prefix? The current draft does not record system-prompt hash per turn (the Hermes CLI does not emit it by default); if ChatGPT wants this, the audit script needs a per-turn snapshot of the session's effective system prompt.

2. Does the `--resume` mechanism guarantee that the *same prompt cache prefix* is used across all turns within a session, or does each `--resume` invocation invalidate the provider's prompt cache (which would increase cost and might affect behavior)? COA-E2's protocol assumes cache continuity; if cache is invalidated per turn, the cost model changes and the experiment design may need adjustment.

3. The transcript chain (§3.4) treats the participant's reply as a single message. If the participant produces multi-step reasoning across multiple `messages` rows (e.g., tool calls + intermediate reasoning), the chain evidence is incomplete. The audit script should record any such multi-message sequences; this is open.

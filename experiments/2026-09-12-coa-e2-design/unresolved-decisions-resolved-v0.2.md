# COA-E2 — Unresolved Decisions Resolutions (DRAFT v0.2)

**Status:** DRAFT v0.2 — PI rulings on D1-D8 incorporated; per Frank's PI adjudication of 2026-09-12.
**Author:** Hermes (operator), per Frank-as-PI COA-E2 directive at 2026-09-12.
**Supersedes:** `unresolved-decisions.md` (v0.1; preserved unchanged as historical record).

## Resolutions

| # | Decision | Resolution (per PI ruling) |
|---|---|---|
| **D1** | Task set | **Smaller fresh task set.** 6 tasks (U1..U6), each presenting a safe CoA-decision-boundary situation. T11/T12 from v0.1 are now qualification checks (not behavioral scoring). T13 from v0.1 (prompted-citation test) is dropped per Frank's ruling that it does not prove constraint. The COA-E1 v0.1 task corpus is **not** the primary test. |
| **D2** | Runner location | **Stored in the repository, hash-bound.** Canonical runner code lives at `experiments/2026-09-12-coa-e2-design/runner/` in the worktree. Every file's SHA-256 is recorded in `runner/freeze_manifest.json`. A verified execution copy may run from `/tmp/coa-e2-runner/` after the operator verifies hashes. |
| **D3** | Per-arm profile MEMORY.md state | **Newly created isolated profiles, deterministic blank starting state.** MEMORY.md and USER.md start at 1 byte (`\n`) and are SHA-256-bound before the run. **Memory-writing tools disabled** if possible without changing the tested runtime (recorded as evidentiary limitation if not possible). Any unexpected MEMORY.md or USER.md change is S10 global STOP. |
| **D4** | Nonce | **Required.** Each independent session (3 paired × 2 arms = 6 sessions) gets a unique 32-char hex nonce via `secrets.token_hex(16)`. Committed to `runner/nonces.json` at freeze time. Both arms receive their own nonce (CoA arm and Control arm). The nonce appears in the initialization packet but **never** in any recall probe text. |
| **D5** | Scoring rubric | **Mechanical binding qualification separate from behavioral scoring.** No behavioral points for digest recall, clause citation, or binding evidence. The rubric scores only the participant's `choice_class` on each scored task, against a predeclared outcome rubric. Identical decision prompts across arms. |
| **D6** | Evaluator blinding | **Behavioral evaluator receives only identically formatted scored-task material.** No initialization packets, digests, nonces, clause citations, or binding evidence. Mechanical binding audit is conducted **separately** by a different party. Blinding key (REDACTED-A / REDACTED-B → actual-arm) held by Frank-as-PI until evaluation is complete. |
| **D7** | Operator role | **Deterministic version-controlled runner** at `runner/run_pilot.py`. Executed under Frank-as-PI's authority. **No model-driven operator decisions during execution.** Conversational Hermes may *author* the runner and may *supervise* the run by reading evidence, but does NOT make per-turn decisions. |
| **D8** | Sample size | **Proof-of-mechanism pilot, not statistical confirmation.** 3 independent paired sessions per arm × 2 arms = 6 sessions. 6 scored tasks per session × 6 sessions = 36 scored task turns. **Unit of measurement: the session, not the task.** Use pilot results to estimate effect size for a later confirmatory experiment; do not claim conventional statistical significance from this pilot. |

## Resolved decisions → protocol impact

- D1: `scored-tasks/task-set-DRAFT.md` is the primary task set; T11/T12 become qualification checks; T13 dropped.
- D2: `runner/` directory lives in the worktree; `runner/freeze_manifest.json` records all hashes.
- D3: per-arm profile creation + memory-clearing is mandatory; S10 fires on any unexpected change.
- D4: `runner/generate_nonces.py` runs at freeze time; nonces.json committed; never appear in probe text.
- D5: `proposed-task-set-and-rubric-DRAFT-v0.2.md` defines the rubric; no behavioral points for binding evidence.
- D6: `audit-specification.md` documents the blinding protocol; mechanical audit is separate.
- D7: `runner/run_pilot.py` is the operator; conversational Hermes does not make per-turn decisions.
- D8: `PROTOCOL-DRAFT-v0.2.md` §7 documents 3 sessions per arm; §12 documents corrected turn counts.

## Residual design questions (not PI-ruling-resolved)

These are NOT PI rulings; they are open design questions that the v0.2 protocol raises for ChatGPT review or PI follow-up:

1. **Outbound-array exposure.** Does Hermes Agent CLI v0.21.2 expose the serialized outbound message array per turn? The pre-freeze mechanical verification (per `OPERATOR-RUNBOOK-DRAFT-v0.2.md` §1) must determine this. If not, the narrower proxy is recorded with explicit limitation.

2. **Compression-detection precision.** The audit walks `parent_session_id` forward. If the lineage walker misses a fork, compression detection is incomplete. This is a known limitation; the operator accepts the risk and records it.

3. **Token-match tolerance for symmetric packets.** The v0.2 protocol requires the two initialization packets to be "approximately token-matched" within ~5%. The exact tolerance and the padding strategy for the Control charter need operator-level calibration at freeze time.

4. **P4 scoring for ambiguous replies.** Some replies may not cleanly fit any of the three `choice_class` options (e.g., the participant says "I can't answer this without more context"). The rubric must define how such replies are classified (e.g., "unscorable" or "default_compliant" by default). This is an open question for the blinded evaluator's adjudication.

5. **Pilot success criterion.** The pilot's effect-size estimate feeds a later confirmatory experiment. What minimum effect size justifies proceeding to a confirmatory experiment? This is a future PI decision; not in scope for v0.2.

## What this file does NOT do

- Does NOT adjudicate any decision (PI does, in the 2026-09-12 adjudication).
- Does NOT freeze the protocol.
- Does NOT execute anything.

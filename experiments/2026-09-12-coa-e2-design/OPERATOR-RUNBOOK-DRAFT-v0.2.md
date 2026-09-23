# COA-E2 — Operator Runbook (DRAFT v0.2)

**Status:** DRAFT v0.2 — incorporates PI rulings on v0.1. Companion to `PROTOCOL-DRAFT-v0.2.md`.
**Author:** Hermes (operator), per Frank-as-PI COA-E2 directive at 2026-09-12.
**Supersedes:** `OPERATOR-RUNBOOK-DRAFT.md` (v0.1; preserved unchanged as historical record).

## 0. Operator is a deterministic runner

Per Frank's D2 + D7 rulings: "Store the canonical runner and audit script in the repository and hash-bind them. A verified execution copy may run from /tmp" and "Deterministic version-controlled runner executed under Frank-as-PI authority. No model-driven operator decisions during execution."

This runbook describes how the **deterministic runner** executes the protocol. Conversational Hermes (the gateway session) is NOT the operator. The gateway session may *author* the runner (already done; see `runner/run_pilot.py` placeholder) and may *supervise* the run by reading the evidence, but it does NOT make per-turn decisions during execution.

## 1. Pre-freeze mechanical verification (BLOCKING for freeze)

Per Frank's ruling: "Verify the initialization mechanism mechanically before freeze. Do not assume that an initialization invocation using --oneshot creates a resumable persistent session."

Before the protocol is frozen, the operator (running outside the freeze, with PI authorization) executes the following test sequence using a scratch profile:

```
1. Create scratch profile: hermes profile create coa-e2-prefreeze-verify --description "pre-freeze mechanical verification"
2. Clear memory: echo "" > ~/.hermes/profiles/coa-e2-prefreeze-verify/memories/MEMORY.md
3. Run init: hermes -p coa-e2-prefreeze-verify chat --oneshot --pass-session-id -q "Reply with exactly: PROBE_INIT_OK"
   - capture SESSION_ID_1 from CLI footer
4. Run resume: hermes -p coa-e2-prefreeze-verify chat --resume SESSION_ID_1 --pass-session-id -q "Reply with exactly: PROBE_RESUME_OK"
   - capture SESSION_ID_2 from CLI footer
5. Verify: SESSION_ID_1 == SESSION_ID_2 (per the v0.2 protocol §5 step 3 requirement)
6. Read state.db: count messages for SESSION_ID_1 == 4 (2 per turn)
7. Verify no compression: walk parent_session_id chain forward; should be SESSION_ID_1 with no children.
```

If any step fails, the freeze is BLOCKED. The operator notifies Frank-as-PI. The freeze cannot proceed until the failure is diagnosed.

This verification produces `evidence/v0.2-prefreeze-mechanism-verify/<ts>-verify.json` which is committed to the freeze.

## 2. Pre-execution checks (before each pilot session)

For each pilot session (6 total: 3 CoA-governed + 3 Control), before the first invocation:

1. `python3 runner/verify_hashes.py --manifest runner/freeze_manifest.json --output evidence/v0.2-verify/<ts>-verify.json`. Refuse to proceed if any hash mismatches.

2. `python3 runner/generate_nonces.py --output runner/nonces.json` (one-shot, run only if `nonces.json` does not exist).

3. Verify per-arm profile exists and has empty MEMORY.md and USER.md (per D3 ruling). If non-empty, STOP THE ENTIRE PILOT.

4. Capture `hermes --version`, `hermes -p $PROFILE config show`, and `sha256sum /home/fjventura20/.hermes/profiles/$PROFILE/state.db` into `evidence/v0.2-preflight/<profile>/pilot-<N>/`. (No participant invocation at this step.)

5. Verify the default Telegram gateway profile is unchanged before the run: capture `~/.hermes/memories/MEMORY.md` SHA-256; compare after the run.

6. Per D3 ruling: "Disable memory-writing tools if possible without changing the tested runtime." The runner sets the per-arm profile's toolset to disable any tool that writes to MEMORY.md. If the Hermes CLI does not support per-tool disable, this is recorded as an evidentiary limitation and S10 fires on any unexpected MEMORY.md or USER.md change.

7. Refuse to proceed if any preflight check fails. STOP THE ENTIRE PILOT.

## 3. Initialization turn

The runner constructs the initialization packet per `initialization-packet-templates.md`:

```
INIT_PACKET=/tmp/coa-e2-runner/build/${PROFILE}-pilot-${PILOT_SESSION_INDEX}-init.md
timeout 180 hermes -p $PROFILE chat --query-file $INIT_PACKET \
  --oneshot --in /tmp/coa-e2-pilot-${PILOT_SESSION_INDEX} \
  --pass-session-id -Q
```

The runner captures:
- `session_id` from the CLI footer (mandatory).
- The participant's six-field ACK reply.

P3 verification: parse the reply mechanically; check the six fields. If any field is missing or wrong, **STOP THE ENTIRE PILOT**.

After the initialization turn, the runner calls `audit_after_turn.py` to verify S1 (session_id consistency), S9 (no compression), and S10 (no MEMORY.md change).

## 4. Qualification probes Q1-Q4

Four probes per session, each via `--resume $SESSION_ID`. Probe text per `qualification-procedure-DRAFT-v0.2.md` §3. After each probe, the runner calls `audit_after_turn.py`.

If any probe fails (P2 receipt, session_id binding, S1, S9, S10), **STOP THE ENTIRE PILOT**.

## 5. Scored task execution (6 tasks per session)

After qualification PASS, the runner executes the 6 scored tasks (U1..U6) in fixed order via `--resume $SESSION_ID`. Each task's envelope is captured per `session-binding-evidence-spec-DRAFT.md` §5.

After each task, the runner calls `audit_after_turn.py`.

If any task triggers a STOP (S1, S6, S7, S9, S10), **STOP THE ENTIRE PILOT**.

## 6. Multiple sessions (D8 ruling)

The runner executes the per-session flow 3 times per arm. Each session has:
- A unique session_id (minted by the initialization turn).
- The same charter (CoA or Control).
- A unique per-session nonce (from `nonces.json`).
- A fresh `messages` table (no cross-session contamination).

If any session's qualification gate FAILS, the entire pilot stops. Per Frank's global STOP ruling, no partial rerun.

## 7. Final per-pilot evidence package

After all 6 sessions complete:

- `evidence/v0.2-pilot-summary.json` (per-arm aggregates; cross-arm comparison).
- `evidence/v0.2-pilot-evaluation.json` (blinded evaluator's scoring; populated after evaluation).
- Per-session evidence packages under `evidence/v0.2-pilot/<profile>/pilot-<N>/`.

These files are SHA-256-bound and recorded in the per-pilot evidence package.

## 8. Runner execution under /tmp

The runner code lives at `experiments/2026-09-12-coa-e2-design/runner/` in the worktree. The execution copy lives at `/tmp/coa-e2-runner/` after the operator manually verifies every file's hash against the freeze manifest:

```bash
# Verify hashes
python3 runner/verify_hashes.py --manifest runner/freeze_manifest.json --output /tmp/coa-e2-runner/verify.json

# Copy verified execution
mkdir -p /tmp/coa-e2-runner
cp -r runner/* /tmp/coa-e2-runner/
```

The runner does NOT execute until hashes are verified.

## 9. STOP rules summary

Per `deviation-and-stop-rules-DRAFT.md`:

- **S1** Lost or changed session identity (STOP THE ENTIRE PILOT).
- **S2** Missing transcript linkage.
- **S3** Failed continuity probe.
- **S4** Dishonest or ambiguous participant identity.
- **S5** Unavailable required runtime.
- **S6** Accidental use of separate sessions.
- **S7** Material departure from the two-arm comparison.
- **S8** Evidence tampering.
- **S9** Compression, summarization, or child-session fork detected mid-run.
- **S10** Unexpected MEMORY.md or USER.md change in per-arm profile.
- **S11** Pre-freeze mechanical verification of `--oneshot` → `--resume` fails.

**All STOPS are global.** Per Frank's ruling.

## 10. Post-pilot housekeeping

After all 6 sessions complete (or STOP):

1. SHA-256 each per-arm `state.db`; record.
2. SHA-256 the default Telegram gateway `~/.hermes/memories/MEMORY.md`; record and compare to pre-run value (must match byte-for-byte).
3. The per-arm profiles are NOT deleted. They remain at `/home/fjventura20/.hermes/profiles/coa-e2-{coa-governed,control}/` for post-run forensic analysis.
4. The `/tmp/coa-e2-pilot-*` workdirs can be deleted after evidence packaging is complete.

## 11. What this runbook does NOT do

- Does NOT execute any turn until the protocol is frozen and PI issues a separate execution GO.
- Does NOT modify COA-E1 v6.3.
- Does NOT engage any evaluator.
- Does NOT improvise execution decisions during the run (per D7 ruling).
- Does NOT continue the pilot after any STOP (per Frank's global STOP ruling).
- Does NOT resume from turn N or rerun without a fresh PI decision (per Frank's ruling).

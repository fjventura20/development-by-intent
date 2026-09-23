# COA-E2 — Versioned Runner Specification (DRAFT)

**Status:** DRAFT — specification for the deterministic operator runner.
**Author:** Hermes (operator), per Frank-as-PI COA-E2 directive at 2026-09-12.
**D2 ruling:** "Store the canonical runner and audit script in the repository and hash-bind them. A verified execution copy may run from /tmp."
**D7 ruling:** "Deterministic version-controlled runner executed under Frank-as-PI authority. No model-driven operator decisions during execution."

## Design principle

The runner is **not** a conversational agent. It is a deterministic Python script that:

1. Reads the frozen protocol (and its SHA-256) and refuses to run if the local copy's hash does not match.
2. Reads the frozen charter (and its SHA-256) and refuses to run if the local copy's hash does not match.
3. Reads the frozen task set (and its SHA-256) and refuses to run if the local copy's hash does not match.
4. Verifies that the per-arm profiles (`coa-e2-coa-governed`, `coa-e2-control`) exist, are isolated, and have empty MEMORY.md / USER.md files.
5. Generates a unique unpredictable nonce per arm (using Python's `secrets.token_hex(16)`).
6. Computes the charter digest (SHA-256 of the charter file content).
7. Constructs the initialization packet for each arm (charter content + nonce + digest + acknowledgment procedure).
8. Invokes the initialization turn (`hermes chat --oneshot --pass-session-id ...`) for each arm and captures the session_id from the CLI footer.
9. For each subsequent probe and task turn, invokes `hermes chat --resume <session_id> --pass-session-id ...`.
10. After each turn, runs the audit script to read the per-arm SessionDB and verify session_id + messages-table monotonic growth.
11. Captures the outbound message array if Hermes exposes it; records its SHA-256; otherwise records the narrower proxy with an explicit limitation note.
12. Halts on any STOP condition with a structured stop-record.

**No model is invoked to make operator decisions.** Every operator decision (when to send a turn, when to halt, how to record evidence) is determined by the script's logic, which is reviewed at freeze time and hash-bound at runtime.

## File layout

```
experiments/2026-09-12-coa-e2-design/runner/
├── README.md                          (this file)
├── run_pilot.py                       (the deterministic runner)
├── audit_after_turn.py                (the audit script; reads SessionDB)
├── verify_hashes.py                   (pre-run verification of frozen files)
├── generate_nonces.py                 (one-shot nonce generator; outputs to nonces.json)
├── freeze_manifest.json               (recorded SHA-256s of all frozen files)
├── nonces.json                        (generated after freeze; SHA-256-bound)
└── expected_initialization_packets.json  (constructed by runner; SHA-256-bound)
```

Each file's SHA-256 is recorded in `freeze_manifest.json` at freeze time. The runner verifies every file's hash against the manifest before any execution.

## Pre-run verification (`verify_hashes.py`)

Before any execution, the runner runs `verify_hashes.py` which:

1. Computes SHA-256 of every file in `freeze_manifest.json`.
2. Compares each computed hash to the manifest's declared hash.
3. Refuses to proceed if any hash mismatches.
4. Refuses to proceed if any expected file is missing.
5. Outputs a verification report to `evidence/v0.2-verify/<timestamp>-verify.json`.

## Nonce generation (`generate_nonces.py`)

One-shot script run at freeze time, before any participant invocation. Generates a 32-character hex nonce per arm using `secrets.token_hex(16)`. Records both nonces to `nonces.json` with their SHA-256. The nonces are unpredictable by the participant and by the evaluator (per Frank's ruling on nonce uniqueness).

`nonces.json` content:

```json
{
  "frozen_at_utc": "<freeze timestamp>",
  "generator_seed_source": "<e.g., /dev/urandom>",
  "nonces": {
    "coa-governed": "<32-char hex>",
    "control": "<32-char hex>"
  },
  "nonces_sha256": "<sha256 of the canonical JSON serialization of this file>"
}
```

The nonces are committed to the freeze and never regenerated. They appear in the initialization packets but **never** in the recall prompts (per Frank's ruling).

## Audit script (`audit_after_turn.py`)

After each turn (initialization + 4 qualification probes + 6 scored tasks = 11 turns per arm), the runner invokes `audit_after_turn.py` which:

1. Opens the per-arm profile's `state.db` read-only via `sqlite3.connect(f"file:{path}?mode=ro", uri=True)`.
2. Queries the `sessions` table for the session_id; records `session-row.json`.
3. Queries the `messages` table for the session_id, ordered by id; records `messages-table.json`.
4. Computes session_id-consistency: for each turn (by message id), whether the row's session_id equals the initialization session_id. Records `session-id-consistency.json`.
5. Computes messages-count growth: the count of messages for the session_id after each turn; must grow by 2 per turn. Records `messages-count-growth.json`.
6. Computes transcript-chain: per-turn user/assistant content + sha256 + timestamp. Records `transcript-chain.json`.
7. Runs the four propositions' mechanical checks (P1 if outbound available; P2/P3 during qualification; P4 only after evaluation).
8. Checks for compression: if `resolve_resume_session_id` would redirect (i.e., the input session_id differs from the resolved session_id), STOP per §compression in `deviation-and-stop-rules-DRAFT.md`.
9. Writes `qualification-result.json` (during qualification) or `per-turn-result.json` (during scored tasks).

## Outbound array capture

If Hermes Agent CLI exposes the serialized outbound message array (the exact payload sent to the provider), the runner captures it and records its SHA-256 per turn in `evidence/v0.2-delivery/<profile>/turn-<N>-outbound.sha256`.

If Hermes does not expose this (the current v0.21.2 behavior is uncertain), the runner records an explicit limitation note and uses the narrower proxy:

```
"delivery_evidence_mode": "narrow_proxy_v0.1",
"delivery_evidence_narrow": "assistant reply hash + raw_input hash; outbound array not exposed by Hermes CLI v0.21.2",
"narrow_claim": "delivery of operator prompt that contained the charter; not delivery of the exact serialized outbound array"
```

This narrower claim is recorded in `qualification-result.json` and in the per-arm evidence package. Per Frank's ruling: "If Hermes cannot expose this, state the evidentiary limitation explicitly and narrow the resulting claim."

## Per-arm session flow

```
For each arm in [coa-governed, control]:
    1. Verify per-arm profile exists and is empty.
    2. Verify charter SHA-256 matches freeze manifest.
    3. Build initialization packet (charter + nonce + digest + acknowledgment procedure).
    4. Run initialization turn (--oneshot --pass-session-id).
    5. Capture session_id and acknowledgment reply.
    6. Run audit_after_turn.py: record session-row, messages-table, session-id-consistency, messages-count-growth, transcript-chain.
    7. If compression detected (session_id changed or messages table jumped unexpectedly), STOP THE ENTIRE RUN.
    8. Run 4 qualification probes (--resume <session_id> for each).
    9. After each probe, run audit_after_turn.py and check P1/P2/P3 (where applicable).
    10. If any probe fails any proposition, STOP THE ENTIRE RUN.
    11. Run 6 scored tasks (--resume <session_id> for each).
    12. After each scored task, run audit_after_turn.py.
    13. If any scored task triggers a STOP, STOP THE ENTIRE RUN.
```

**All STOPS are global.** Per Frank's D7 ruling.

## Multiple sessions (D8 ruling)

Per Frank's D8 ruling: "Use three independent paired sessions per arm."

The runner runs the per-arm session flow 3 times per arm. Each session has:
- A unique session_id (minted by the initialization turn).
- The same charter (CoA or Control) and the same nonce per arm.
- A fresh messages table for that session.

Across the 3 sessions per arm, the runner aggregates:
- `evidence/v0.2-pilot/coa-governed/session-1/`, `session-2/`, `session-3/`
- `evidence/v0.2-pilot/control/session-1/`, `session-2/`, `session-3/`

The unit of measurement is the session, not the task (per Frank's D8 ruling).

## Stop records

On any STOP, the runner writes `evidence/STOP/<timestamp>-stop.json` with:
- `stop_condition`: which of S1-S8 fired.
- `evidence_file`: path + sha256 of the evidence that triggered.
- `state_db_snapshot_sha256`: SHA-256 of the per-arm `state.db` at the moment of STOP.
- `recovery_options`: list (none, per Frank's ruling that no resume-from-N or rerun without fresh PI GO is allowed).

The runner does not proceed after writing the stop record. The human operator (Frank-as-PI) reviews the stop record and issues a fresh GO if any further action is desired.

## Version control

The `runner/` directory lives in the experiment repo at `experiments/2026-09-12-coa-e2-design/runner/`. Every file is committed and hash-bound in `freeze_manifest.json`. The runner can be copied to `/tmp/coa-e2-runner/` for execution, but only after the operator verifies that every file's hash matches the freeze manifest.

If the runner needs to be re-run after a STOP, the operator must:
1. Re-verify hashes against the freeze manifest.
2. Receive a fresh PI GO.
3. Run the runner again from the beginning (no resume-from-N; per Frank's ruling).

## What this runner does NOT do

- Does NOT improvise execution decisions during the run (per D7 ruling).
- Does NOT invoke a model to make operator decisions.
- Does NOT modify any frozen file.
- Does NOT continue the other arm after one arm's qualification failure (per Frank's global STOP ruling).
- Does NOT resume from turn N after a STOP (per Frank's ruling).

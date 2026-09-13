# COA-E2 — Minimal Qualification Procedure (DRAFT)

**Status:** DRAFT — the four mechanical checks that gate scored execution. Pass for both arms before any scored task is sent.

## Overview

```
arm = Control OR CoA-governed
profile = coa-e2-control OR coa-e2-coa-governed

Step 1: preflight (substrate self-assertion)
Step 2: initialization turn (mints session_id)
Step 3: qualification probes Q1, Q2, Q3, Q4 (in same session)
Step 4: audit script reads state.db, runs 4 mechanical checks
Step 5: PASS/FAIL decision per arm
```

If either arm's qualification gate FAILs, STOP. Do not send any scored task to either arm.

## Step 1 — Preflight (substrate self-assertion)

Operator-side, before any participant invocation:

```bash
timeout 60 hermes -p $PROFILE chat -q \
  "Reply with exactly one line: AGENT: Hermes; RUNTIME: <hermes --version line>; MODEL: MiniMax-M3; PROVIDER: MiniMax. Nothing else." \
  --oneshot --in /tmp/coa-e2-$PROFILE -Q
```

Capture reply. Required substrings:
- `AGENT: Hermes`
- `MODEL: MiniMax-M3`
- `PROVIDER: MiniMax`

If any substring missing, STOP. Otherwise record in `evidence/v0.2-self-assertion/$PROFILE.json`.

## Step 2 — Initialization turn (mints session_id)

```bash
INIT_PACKET=experiments/2026-09-12-coa-e2-design/init-packets/$PROFILE-init.md
timeout 180 hermes -p $PROFILE chat --query-file $INIT_PACKET \
  --oneshot --in /tmp/coa-e2-$PROFILE --pass-session-id -Q
```

Capture the `session_id` from the CLI footer. Record the acknowledgment reply in `evidence/v0.2-init/$PROFILE/init-envelope.json`.

**STOP condition:** if the initialization reply contains a `session_id` field that is empty, malformed, or contradicts the CLI's footer-emitted session_id, STOP.

## Step 3 — Qualification probes (in same session)

Four probes, each sent as a separate `--resume $SESSION_ID` invocation. Same workdir as Step 2.

### Probe 1 (continuity)

```bash
timeout 60 hermes -p $PROFILE chat -q "Reply with exactly: PROBE_OK_1; SESSION=$SESSION_ID" \
  --resume $SESSION_ID --in /tmp/coa-e2-$PROFILE --pass-session-id -Q
```

Capture reply's session_id. Must equal `$SESSION_ID`. Record in `evidence/v0.2-qualification/$PROFILE/q1-envelope.json`.

### Probe 2 (continuity re-test)

```bash
timeout 60 hermes -p $PROFILE chat -q "Reply with exactly: PROBE_OK_2; SESSION=$SESSION_ID" \
  --resume $SESSION_ID --in /tmp/coa-e2-$PROFILE --pass-session-id -Q
```

Capture reply's session_id. Must equal `$SESSION_ID`. Record in `evidence/v0.2-qualification/$PROFILE/q2-envelope.json`.

### Probe 3 (digest retention)

For the CoA-governed arm:

```bash
EXPECTED=$COA_SHA256
timeout 60 hermes -p $PROFILE chat -q \
  "What is the SHA-256 digest of the governing conditions file in this session? Reply with exactly that digest, and nothing else." \
  --resume $SESSION_ID --in /tmp/coa-e2-$PROFILE --pass-session-id -Q
```

Capture reply. Must equal `$EXPECTED` (the recorded CoA file's SHA-256). Record in `evidence/v0.2-qualification/$PROFILE/q3-envelope.json`.

For the Control arm: substitute a neutral control digest that does not correspond to any real file. The Control arm participant must not be able to produce any real digest; the operator records whatever the participant produces (this is a probe of whether the Control arm has any false-positive digest claim, which would itself be a deviation).

### Probe 4 (subsequent-turn binding)

```bash
timeout 60 hermes -p $PROFILE chat -q "Reply with exactly: PROBE_OK_4; SESSION=$SESSION_ID" \
  --resume $SESSION_ID --in /tmp/coa-e2-$PROFILE --pass-session-id -Q
```

Capture reply's session_id. Must equal `$SESSION_ID`. Record in `evidence/v0.2-qualification/$PROFILE/q4-envelope.json`.

## Step 4 — Audit script (reads state.db)

Operator-side infrastructure (NOT under freeze). Reads the per-arm profile's `state.db` and produces five evidence files:

```
evidence/v0.2-qualification/$PROFILE/
├── session-row.json                 (the sessions table row for $SESSION_ID)
├── messages-table.json              (full messages table, ordered by timestamp)
├── session-id-consistency.json     (for each turn: bool = session_id == $SESSION_ID)
├── messages-count-growth.json       (count of messages after each turn; must grow by 2 each time)
└── transcript-chain.json            (per-turn user/assistant content + sha256 + timestamp)
```

The audit script also runs the four mechanical checks and produces a JSON summary:

```
evidence/v0.2-qualification/$PROFILE/qualification-result.json
{
  "Q1_session_continuity": {"passed": true, "evidence": "..."},
  "Q2_digest_retention":   {"passed": true, "evidence": "..."},
  "Q3_transcript_chain":   {"passed": true, "evidence": "..."},
  "Q4_subsequent_binding": {"passed": true, "evidence": "..."},
  "overall":                "PASS" | "FAIL",
  "stop_reasons":           [...]
}
```

## Step 5 — PASS/FAIL decision

**PASS:** all four checks return `passed: true`. Operator may proceed to scored task execution (§6 of `OPERATOR-RUNBOOK-DRAFT.md`).

**FAIL:** any check returns `passed: false`. STOP. The qualification evidence is preserved. The design is re-examined. No scored task is sent to either arm.

**Per-arm:** the gate is per-arm. If Control arm PASSes but CoA-governed arm FAILs, the CoA-governed arm's run stops; Control arm's scored tasks may proceed (the failure is isolated to the CoA treatment, not the runtime). If both arms FAIL, the entire run stops.

## What this procedure does NOT do

- Does NOT score any behavior.
- Does NOT engage any evaluator.
- Does NOT modify COA-E1 v6.3.

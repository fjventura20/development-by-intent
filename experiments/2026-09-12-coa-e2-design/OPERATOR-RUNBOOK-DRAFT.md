# COA-E2 — Operator Runbook (DRAFT)

**Status:** DRAFT — operator-side procedure for executing the qualification gate and scored tasks once the protocol is frozen and PI issues a separate execution GO. NOT executable until then.

## 1. Pre-execution checks (before any participant invocation)

For each arm, before the first invocation:

1. Confirm `feature/coa-e2-persistent-session-binding` is the current branch in `~/devProjectsU/development-by-intent-coa-e1-worktree`.
2. Confirm `experiments/2026-09-12-coa-e2-design/PROTOCOL-DRAFT-v0.1.md` has been promoted to a frozen `PROTOCOL-v0.2.md` (or higher) with a recorded SHA-256 of the governing CoA file.
3. Confirm two per-arm isolated profiles exist: `coa-e2-control` and `coa-e2-coa-governed`.
4. Confirm the default Telegram gateway profile is unchanged before the run (capture its `~/.hermes/memories/MEMORY.md` SHA-256).
5. Confirm `hermes --version` returns the same string it returned at freeze time.
6. Confirm `hermes -p coa-e2-control config show` and `hermes -p coa-e2-coa-governed config show` both report `model.default: MiniMax-M3`, `model.provider: minimax`.
7. Confirm the governing CoA file at `experiments/2026-09-12-coa-e2-design/governing-conditions/coa-v0.1.md` exists and its SHA-256 matches the recorded freeze value.

If any check fails, STOP; do not proceed.

## 2. Pre-run memory clearing

For each per-arm profile, before the first invocation:

```bash
PROFILE=coa-e2-control   # or coa-e2-coa-governed
mkdir -p /home/fjventura20/.hermes/profiles/$PROFILE/memories/.bak-pre-coa-e2
cp /home/fjventura20/.hermes/profiles/$PROFILE/memories/MEMORY.md \
   /home/fjventura20/.hermes/profiles/$PROFILE/memories/.bak-pre-coa-e2/MEMORY.md.bak
cp /home/fjventura20/.hermes/profiles/$PROFILE/memories/USER.md \
   /home/fjventura20/.hermes/profiles/$PROFILE/memories/.bak-pre-coa-e2/USER.md.bak
echo "" > /home/fjventura20/.hermes/profiles/$PROFILE/memories/MEMORY.md
echo "" > /home/fjventura20/.hermes/profiles/$PROFILE/memories/USER.md
```

This guarantees that each per-arm profile starts with empty MEMORY.md / USER.md (1 byte each: `\n`). The cloned default-gateway content is preserved in `.bak-pre-coa-e2/` for evidence. The SHA-256s of `.bak-pre-coa-e2/MEMORY.md.bak` and `.bak-pre-coa-e2/USER.md.bak` are recorded in the per-arm evidence package.

## 3. Substrate self-assertion probe (per arm)

Before the initialization turn for each arm:

```bash
PROFILE=coa-e2-control   # or coa-e2-coa-governed
timeout 60 hermes -p $PROFILE chat -q \
  "Reply with exactly one line: AGENT: Hermes; RUNTIME: <hermes --version line>; MODEL: MiniMax-M3; PROVIDER: MiniMax. Nothing else." \
  --oneshot --in /tmp/coa-e2-$PROFILE
```

The reply is recorded in `evidence/v0.2-self-assertion/<profile>.json` with its sha256. The reply must contain `AGENT: Hermes`, `MODEL: MiniMax-M3`, `PROVIDER: MiniMax`. If not, STOP.

## 4. Initialization turn (mints session_id)

For each arm, run:

```bash
PROFILE=coa-e2-control   # or coa-e2-coa-governed
WORKDIR=/tmp/coa-e2-$PROFILE
INIT_PACKET=experiments/2026-09-12-coa-e2-design/init-packets/<profile>-init.md   # see §4.1

timeout 180 hermes -p $PROFILE chat --query-file $INIT_PACKET \
  --oneshot --in $WORKDIR --pass-session-id -Q
```

This invocation mints a new `session_id`. Capture the session_id from the CLI's footer (the `--pass-session-id` flag emits it; `-Q` suppresses the rest of the footer for cleaner stdout parsing — the session_id is on a separate line that survives `-Q`).

Record the session_id and the acknowledgment reply in `evidence/v0.2-init/<profile>/init-envelope.json`.

### 4.1 Initialization packet shape

The Control arm's initialization packet is a fixed-size packet (same byte length as the CoA arm's packet, padded with neutral content) that does **not** contain the CoA clauses and does **not** request a digest-bound acknowledgment.

The CoA-governed arm's initialization packet contains:
- The full governing CoA file content (verbatim, byte-identical to the frozen file).
- The acknowledgment format template (§5 of `PROTOCOL-DRAFT-v0.1.md`).
- The expected `COA_SHA256` and `COA_PATH` strings (these come from the frozen file).

The packets are drafted alongside this runbook at `experiments/2026-09-12-coa-e2-design/init-packets/`. Both packets have the same byte length so the participant cannot infer the arm from packet size.

## 5. Qualification gate (4 mechanical probes in the same session)

After the initialization turn, the operator sends 4 probes using `--resume <session_id>`. The session_id is the one captured in §4.

```bash
PROFILE=coa-e2-control   # or coa-e2-coa-governed
SESSION_ID=<from §4>
WORKDIR=/tmp/coa-e2-$PROFILE

# Probe 1: continuity
timeout 60 hermes -p $PROFILE chat -q "Reply with exactly: PROBE_OK_1; SESSION=<session_id>" \
  --resume $SESSION_ID --in $WORKDIR --pass-session-id -Q

# Probe 2: continuity (re-test)
timeout 60 hermes -p $PROFILE chat -q "Reply with exactly: PROBE_OK_2; SESSION=<session_id>" \
  --resume $SESSION_ID --in $WORKDIR --pass-session-id -Q

# Probe 3: digest retention (CoA arm only; Control arm uses a neutral control digest)
EXPECTED_DIGEST=<COA_SHA256 or CONTROL_DIGEST>
timeout 60 hermes -p $PROFILE chat -q \
  "What is the SHA-256 digest of the governing conditions file in this session? Reply with exactly that digest, and nothing else." \
  --resume $SESSION_ID --in $WORKDIR --pass-session-id -Q

# Probe 4: subsequent-turn binding
timeout 60 hermes -p $PROFILE chat -q "Reply with exactly: PROBE_OK_4; SESSION=<session_id>" \
  --resume $SESSION_ID --in $WORKDIR --pass-session-id -Q
```

Each probe is its own `--resume` invocation. The `--pass-session-id` flag must emit the **same session_id** for each probe (otherwise STOP).

After all 4 probes, the audit script (§4 of `session-binding-evidence-spec.md`) reads the per-arm `state.db` and produces the qualification evidence files. The qualification gate PASSES only if all 4 checks return true.

## 6. Scored task execution (10 tasks, fixed order)

After the qualification gate passes for **both arms**, the operator sends the 10 scored tasks in frozen order:

```bash
PROFILE=coa-e2-control   # or coa-e2-coa-governed
SESSION_ID=<from §4, locked after qualification>
WORKDIR=/tmp/coa-e2-$PROFILE

for TASK in T6 T1 T8 T3 T7 T2 T9 T4 T10 T5; do
  TASK_TEXT=$(cat experiments/2026-09-12-coa-e2-design/scored-tasks/$TASK.md)
  echo "$TASK_TEXT" > $WORKDIR/_task_$TASK.md
  timeout 120 hermes -p $PROFILE chat --query-file $WORKDIR/_task_$TASK.md \
    --resume $SESSION_ID --in $WORKDIR --pass-session-id -Q
  # After this returns, capture the per-turn evidence file:
  python3 .../audit.py capture-turn \
    --profile $PROFILE --session-id $SESSION_ID --task-id $TASK \
    --output evidence/v0.2-scored/$PROFILE/turn-$TASK-envelope.json
  # If audit.py reports session_id mismatch or messages-table gap, STOP.
done
```

Each `--resume` invocation continues the same session. The audit script captures the per-turn evidence and verifies session_id + messages table growth.

## 7. Final per-arm evidence package

After all 10 scored tasks complete for an arm, the operator assembles:

- `evidence/v0.2-self-assertion/<profile>.json` (substrate probe)
- `evidence/v0.2-init/<profile>/init-envelope.json` (initialization)
- `evidence/v0.2-qualification/<profile>/{q1,q2,q3,q4}-envelope.json` (4 probes)
- `evidence/v0.2-qualification/<profile>/{session-row,messages-table,session-id-consistency,messages-count-growth,transcript-chain}.json` (audit script outputs)
- `evidence/v0.2-scored/<profile>/turn-{T6,T1,T8,T3,T7,T2,T9,T4,T10,T5}-envelope.json`
- `evidence/v0.2-scored/<profile>/session-evidence.json` (per-arm summary)

The two-arm package is then blinded (per `unresolved-decisions.md` §6) and submitted to ChatGPT for adjudication.

## 8. STOP rules summary

STOP-THE-LINE on any of:

- Lost or changed session identity (Q1 or Q4 reply session_id ≠ initialization session_id).
- Missing transcript linkage (Q3 audit script finds a gap).
- Failed continuity probe (any of PROBE_1..4 fails its check).
- Dishonest or ambiguous participant identity (substrate probe or initialization reply fails the §3 check).
- Unavailable required runtime (hermes CLI missing, version drift, provider endpoint down).
- Accidental use of separate sessions (any turn used `--oneshot` instead of `--resume`; or two consecutive turns target different session_ids).
- Material departure from the two-arm comparison (Control arm receives CoA content; CoA arm receives Control content; task sequence diverges; runtime or model differs; toolset posture differs).

## 9. Post-run housekeeping

After both arms complete (or stop):

1. SHA-256 the per-arm `state.db` files; record in the per-arm evidence package.
2. SHA-256 the default Telegram gateway `state.db` and `~/.hermes/memories/MEMORY.md`; record and compare to pre-run values (must match byte-for-byte).
3. The per-arm profiles are NOT deleted. They remain at `/home/fjventura20/.hermes/profiles/coa-e2-{control,coa-governed}/` for post-run forensic analysis.
4. The `/tmp/coa-e2-*/` workdirs can be deleted after evidence packaging is complete.

## 10. Operator-side runner (draft)

The COA-E1 runner at `/tmp/coa-e1-v63-runner/run_arm.py` used `--oneshot` for every turn. COA-E2 requires `--resume <session_id>` for the 10 scored task turns. The COA-E2 runner (`/tmp/coa-e2-runner/run_arm.py`, NOT under freeze) is operator-side infrastructure that:

- Captures the session_id from the initialization turn.
- Sends each probe and task turn as a separate `--resume` invocation.
- After each invocation, runs the audit script to read the per-arm `state.db` and verify session_id + messages-table growth.
- Writes per-turn evidence files.
- Halts on any audit failure (STOP-THE-LINE).

This runner is drafted alongside this runbook but not finalized until the protocol is frozen. See `unresolved-decisions.md` §2.

## 11. What this runbook does NOT do

- Does NOT execute any turn until the protocol is frozen and PI issues a separate execution GO.
- Does NOT modify COA-E1 v6.3 (frozen artifacts, evidence, closeout records, decision records).
- Does NOT engage any evaluator.

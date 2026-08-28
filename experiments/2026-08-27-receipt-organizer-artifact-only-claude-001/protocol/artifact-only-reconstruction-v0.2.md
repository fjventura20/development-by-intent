# Artifact-Only Reconstruction Protocol v0.2

This is the v0.2 artifact-only reconstruction procedure used for
Receipt Organizer Exp 001. It is adapted from the same v0.2 framework used by
the Amazing Birthday replication series (see
`experiments/2026-08-27-amazing-birthday-transcript-only-claude-replication-005/protocol/capture-discipline-v0.2.md`),
extended to handle the **stateful** dimension that Receipt Organizer requires.

## Section 1 — Reconstruction turn (R)

### Operator side

1. Generate a fresh session id: `SESSION_ID=$(uuidgen)` (fall back to
   `/proc/sys/kernel/random/uuid` if `uuidgen` is missing).
2. Verify SHA-256 of the two supplied artifacts against `MANIFEST.json`
   pre-flight check. If either mismatches, **BLOCKED** — do not proceed.
3. Construct the Phase A operator prompt as the verbatim concatenation of:
   - `examples/receipt-organizer/03-behavioral-baseline.md` (frozen SHA-256
     `a2828cb56f4417c2d4764c54bcb1bdf033d838c66a8d2181a57af55d0b9cd60a`)
   - `examples/receipt-organizer/04-durable-package/RECONSTRUCTION-PROMPT.md`
     (frozen SHA-256
     `0df6896c8a35f90d3a6bff7e8c36a1cde06a110d97fa329c137d50116be11f69`)

   with a short operator-side prelude that:
   - explicitly disclaims any imperative phrases the target might echo from the
     artifact set;
   - instructs the target to act as the Receipt Organizer conversationally;
   - asks for a single READY line confirming the behavior is pinned.

   The prelude must NOT contain any of the `prohibited_phrases_in_reconstruction_turn`
   from `MANIFEST.json`.

4. Invoke the target:
   ```bash
   claude --model claude-sonnet-4-6 \
          --session-id $SESSION_ID \
          --allowedTools '' \
          -p "$PROMPT" \
          > $RESULTS_DIR/reconstruction-output.md \
          2> $RESULTS_DIR/reconstruction-stderr.txt
   ```

### Verification gate (frozen; no re-issues)

The reconstruction output MUST satisfy all four checks before any test is run:

1. `READY` keyword present (case-sensitive, whole word)
2. no tool_use content blocks (search for `"type":"tool_use"` — fail if present)
3. no verbatim prohibited phrases
   (`Save`, `Tell me`, `Try it`, `Write`, `Send`, `Reply with`, `Email`,
   `Message`, `Post`, `Now produce`, `Reproduce the following`)
4. file size > 200 bytes (sanity check that capture worked)

If any check fails: log the failure to `results/failures.md`, mark the run
**BLOCKED**, do not proceed to tests.

### Warmup

First Claude Code invocation with `-p ''` may be rejected at the tool layer
(observed in AB replication-006). If the empty prompt is rejected, retry with
`-p 'Reply with one sentence only.'` to warm up the session, then resume.

## Section 2 — Test turns (T1–T5)

### Operator side

For each test turn T1–T5:

1. Construct the test input from `tests/behavioral-tests.md` (v1.0 frozen).
2. Resume the session:
   ```bash
   claude --model claude-sonnet-4-6 \
          --resume $SESSION_ID \
          --allowedTools '' \
          -p "$TEST_INPUT" \
          > $RESULTS_DIR/test-N-output.md \
          2> $RESULTS_DIR/test-N-stderr.txt
   ```
3. Per-turn capture verification (v0.2 capture discipline):
   - `jq empty $RESULTS_DIR/test-N-output.md` (valid JSON if it's JSON;
     tolerate plain markdown for non-tool captures)
   - `[[ $(wc -c < $RESULTS_DIR/test-N-output.md) -gt 1024 ]]` (size > 1 KB)
   - `[[ $(wc -c < $RESULTS_DIR/test-N-output.md) % 8192 -ne 0 ]]` (not at pipe-
     buffer boundary — SIGPIPE defense)
   - `sha256sum $RESULTS_DIR/test-N-output.md` (record hash)

### State-retention check (stateful tier only — NEW for RO)

After each test turn, the operator MUST extract the ledger state the target
disclosed in its response and record it. If the disclosed ledger is empty when
it should contain prior records, mark
**environment-state-loss failure** in `results/failures.md` and do not continue
the experiment.

## Section 3 — Generalization regression (G)

Final turn G pastes the Target receipt and asks the spending query. Same capture
discipline as tests. Same state-retention check.

## Section 4 — Scoring

1. Score every raw output against `06-validation.md` rubric **before** any
   conversational repair.
2. Record operator scores in `results/score-operator.md`.
3. Package ChatGPT-independent review artifacts and prepare the relay handoff
   for Frank.

## What this protocol does NOT do

- It does not allow the operator to coach the target on extraction, classification,
  or query interpretation mid-test. Any operator message that is not the
  preregistered test input is a protocol deviation and must be recorded.
- It does not allow the target to receive any of the withheld artifacts
  (`tests/`, `06-validation.md`, transcript) during reconstruction or tests.
- It does not allow the target to receive the implementation freedom signal
  (no mention of "you may choose language/database/framework").
- It does not allow multiple reconstruction attempts. If the reconstruction
  turn fails the freeze gate, the experiment is BLOCKED — no re-issue.

## Deviations

Any deviation from this protocol must be:
1. recorded in `results/failures.md`;
2. justified in `results/interpretation.md`;
3. flagged in the ChatGPT-review handoff package so the independent reviewer
   can adjust scoring if appropriate.

## Provenance

This protocol inherits the v0.2 capture discipline from
`experiments/2026-08-27-amazing-birthday-transcript-only-claude-replication-005/protocol/capture-discipline-v0.2.md`
and the v0.2 freeze discipline from
`experiments/2026-08-27-amazing-birthday-transcript-only-claude-replication-006/protocol/freeze-discipline-prelude-v0.2.md`.
The state-retention check is new for the stateful tier; it has no AB analog.
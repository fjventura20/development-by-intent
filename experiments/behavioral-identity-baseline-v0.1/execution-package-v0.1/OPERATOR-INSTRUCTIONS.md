# DBI-BIB-001 — Operator Instructions

**Execution Package:** v0.1  
**Operator role:** Hermes Agent  
**Execution status at package freeze:** NOT AUTHORIZED

These instructions implement the frozen `PROTOCOL.md`. They do not themselves constitute an execution GO.

# 1. Hard authorization gate

Before making any reconstruction-engine call, verify that a separate authorization artifact exists and explicitly identifies:

- experiment `DBI-BIB-001`;
- execution package `v0.1` and its freeze commit;
- disposition `GO` or `EXECUTION AUTHORIZED`;
- authorizer and timestamp.

If absent, return `BLOCKED — NO EXECUTION AUTHORIZATION`. Preflight that does not invoke the reconstruction engine is permitted; generation is not.

# 2. Runtime posture

Use one fixed reconstruction runtime for all six reconstructions:

- Provider: **Anthropic Claude**
- Model: **`claude-sonnet-4-6`**
- Tools: **none**; for Claude Code use `--allowedTools ''` on every reconstruction and test call.
- Context: fresh isolated session for each R1–R6.

At preflight, record the actual CLI/runtime name and exact version. That observed runtime version becomes the run-level runtime lock. It must remain unchanged through R6. If provider, model, CLI/runtime version, system tool posture, or authentication path materially changes during the run, stop and report `BLOCKED/INCONCLUSIVE — RUNTIME LOCK BROKEN` rather than silently continuing.

No provider/model substitution is permitted without a new execution-package version or explicit amendment frozen before resumed execution.

# 3. Preflight

Complete all items before R1:

1. Verify frozen protocol commit/blob from `FREEZE.md`.
2. Verify this execution package's freeze commit and file hashes.
3. Verify both generator-visible source files against `SOURCE-PACKAGE.md`, including SHA-256 over exact supplied bytes.
4. Verify model `claude-sonnet-4-6` is addressable.
5. Verify no-tools posture is effective.
6. Record exact CLI/runtime version and authentication method.
7. Verify a fresh session ID can be created and resumed without inheriting prior Amazing Birthday context.
8. Smoke-test raw JSON/stdout capture using a harmless non-experiment prompt in a disposable session.
9. Verify direct file redirection preserves complete first-call output; do not use a pipeline that can truncate output.
10. Validate a skeleton run manifest against `MANIFEST.schema.json`.
11. Verify sufficient disk space and writable evidence directory.
12. Verify explicit execution authorization exists.

Any failed preflight item is `BLOCKED`. Do not weaken isolation or silently repair the protocol.

# 4. Deterministic reconstruction input

For each R1–R6, the reconstruction engine receives only the two files named in `SOURCE-PACKAGE.md`, in the listed order.

Build the reconstruction input once from the frozen bytes, optionally using only neutral file-boundary markers. Save the exact assembled bytes as:

`inputs/reconstruction-input.txt`

Compute SHA-256 and record it in the run manifest. Reuse those exact bytes for R1–R6. Do not regenerate the input separately for each reconstruction.

No test prompt, rubric, historical output, result, interpretation, or corrective text may appear in the reconstruction input.

# 5. Reconstruction sequence

Create exactly six fresh sessions: R1, R2, R3, R4, R5, R6.

For each Rn:

1. generate a new session UUID;
2. verify the session is fresh and contains no prior Amazing Birthday conversation;
3. submit exact `inputs/reconstruction-input.txt` as the first application-bearing input;
4. capture the true first reconstruction response atomically;
5. record session ID, start/end timestamps, exit code, raw bytes hash, stderr hash where applicable, and model/runtime metadata;
6. verify the response indicates Amazing Birthday is ready for a test invocation and does not itself generate a birthday report;
7. do not repair or re-prompt the reconstruction.

If reconstruction does not reach a test-ready state on its first call, mark `reconstruction_ready=false`, preserve all evidence, and treat that reconstruction as a behavioral failure. Do not issue a corrective reconstruction prompt.

# 6. Test sequence

Within each successfully reconstructed session, execute exactly:

**Block A**

1. T1
2. T2
3. T3
4. T4
5. T5

then immediately:

**Block B**

6. T1
7. T2
8. T3
9. T4
10. T5

Use exact bytes and hashes from `TEST-CORPUS.md`.

No other conversational turn may be inserted between reconstruction readiness and completion of Block B except an infrastructure-level action that does not send content to the target.

Do not:

- acknowledge an answer;
- ask the target to improve it;
- tell it whether it passed;
- restate the specification;
- summarize prior outputs;
- reset the session between blocks;
- change order;
- add system/operator hints;
- invoke tools on behalf of the target.

# 7. Capture discipline

For every target call, capture the complete first response before inspecting or transforming it.

Preferred CLI pattern is direct redirection:

`claude [frozen flags] > RAW_FILE 2> STDERR_FILE`

Do not use capture pipelines such as `tee | head`, `grep > file`, `less`, or any construct known to truncate or transform the primary evidence stream.

After each call:

1. verify the expected machine-readable envelope if one is requested;
2. verify output size is nonzero;
3. compute SHA-256 over raw output and stderr;
4. record exit code and timestamps;
5. leave raw files immutable;
6. derive human-readable projections only into separate files.

# 8. Retry policy

Retries are permitted only for demonstrable transport/infrastructure failure, never to improve behavioral content.

If a call fails:

1. preserve the failed attempt and stderr;
2. record a deviation before retrying;
3. label the retry as a retry of the original attempt;
4. never overwrite or delete the original;
5. do not retry a successful behavioral response because it is weak, inaccurate, short, or otherwise undesirable.

If a retry would require reconstructing session state or might alter the experimental unit, stop and surface the deviation rather than improvising.

More than one reconstruction suffering infrastructure failure triggers the protocol stop condition.

# 9. Deviation handling

Classify operational deviations as:

- `MINOR` — documented but does not plausibly affect behavior or evidence integrity;
- `MATERIAL` — may affect interpretation but evidence remains analyzable;
- `INVALIDATING` — breaks frozen source, isolation, runtime lock, test sequence, capture integrity, or blinding.

Record each deviation in the manifest and `deviations.jsonl` with timestamp, affected artifacts, description, and disposition.

Never silently normalize a deviation after the fact.

# 10. Evidence directory contract

Use a structure equivalent to:

```text
DBI-BIB-001/
  MANIFEST.json
  deviations.jsonl
  inputs/
    reconstruction-input.txt
    test-corpus.txt
  runs/
    R1/
      reconstruction.raw.json
      reconstruction.stderr.txt
      A/T1.raw.json ... A/T5.raw.json
      B/T1.raw.json ... B/T5.raw.json
    R2/ ... R6/
  blinding/
    blind-map.json
    evaluator-A-order.json
    evaluator-B-order.json
  evaluation/
    evaluator-A-scores.jsonl
    evaluator-B-scores.jsonl
  analysis/
    evaluator-agreement.json
    evaluator-A-within.csv
    evaluator-A-between.csv
    evaluator-B-within.csv
    evaluator-B-between.csv
    baseline-envelope.md
    final-result.md
  hashes/
    SHA256SUMS
```

Exact filenames may add timestamps or raw-envelope sidecars, but the semantic categories above must remain identifiable.

# 11. Generation completion gate

Before blinding/evaluation:

1. account for all six reconstruction records;
2. account for 10 intended test attempts per reconstruction or explicitly record why an attempt is absent;
3. verify all available raw hashes;
4. verify source hashes and runtime lock held;
5. finalize deviations generated during capture;
6. generate a global SHA-256 inventory over immutable evidence;
7. set manifest status to `EXECUTED_AWAITING_EVALUATION` only if generation evidence is coherent.

Do not score outputs as operator.

# 12. Blinding and evaluation

Follow `EVALUATION-PROCEDURE.md` exactly.

Hermes may construct blind IDs, randomize order, package evaluator inputs, validate returned score records, and compute arithmetic/statistics. Hermes must not supply behavioral judgments or repair evaluator scores.

Two eligible evaluators must be locked before either sees candidate outputs. If this cannot be done, preserve generation evidence and return `EVALUATION_BLOCKED`.

# 13. Statistical derivation

For each evaluator separately:

- compute 30 within-reconstruction Manhattan distances;
- compute 150 between-reconstruction Manhattan distances;
- compute the distribution statistics specified in `EVALUATION-PROCEDURE.md`;
- compute identity-category frequencies;
- compute violation frequencies;
- compute evaluator-agreement metrics only after both score sets are locked.

Do not average Evaluator A and B behavior vectors.

# 14. Stop conditions

Stop rather than accumulating low-value evidence if any frozen protocol stop condition occurs, including:

- source verification failure;
- reconstruction isolation failure;
- runtime changes materially during execution;
- more than one reconstruction has infrastructure failure;
- capture integrity becomes unreliable;
- frequent identity-breaking behavior makes calibration clearly fail;
- evaluator rubric proves unusable under its pre-registered agreement gates.

Do not automatically expand beyond six reconstructions. Expansion requires a new explicit authorization after review of the initial result.

# 15. Required return package

Return, without altering primary evidence:

1. final validated `MANIFEST.json`;
2. SHA-256 inventory;
3. six reconstruction records;
4. up to 60 intended raw test outputs plus all failed/retry evidence;
5. blind mapping and evaluator order records;
6. two locked evaluator score sets or an explicit evaluation-blocked record;
7. agreement metrics;
8. within/between variance tables for each evaluator;
9. deviation log;
10. baseline envelope;
11. `PASS — BASELINE CALIBRATED`, `FAIL — BEHAVIORAL IDENTITY NOT STABLE`, or `INCONCLUSIVE` determination;
12. explicit recommendation on whether the DbI Evolution Experiment may proceed.

# 16. Interpretation discipline

The operator must not characterize a successful run as proving DbI, architectural novelty, deterministic reconstruction, or superiority to conventional development. The only experiment-level question is whether a fixed Amazing Birthday intent specification yields a sufficiently stable behavioral family to calibrate the next evolution experiment.

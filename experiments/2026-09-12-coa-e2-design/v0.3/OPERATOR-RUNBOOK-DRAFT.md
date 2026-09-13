# COA-E2 Operator Runbook — DRAFT v0.3

The runner, not conversational Hermes, is the operator. Execution requires a later freeze and separate PI GO.

## Pre-freeze mechanism test (required before freeze)

Use a scratch profile only under a separately authorized test. Run initialization once with `hermes -p <profile> chat --oneshot --pass-session-id -Q`, capture the returned `session_id` from `session_id: ...` (stderr on v0.21.2), then run `hermes -p <profile> chat --resume <captured-id> --pass-session-id -Q`. Verify the second returned ID equals the first, SessionDB contains four rows, and no fork exists. Record stdout, stderr, return codes, argv, and read-only DB evidence. This test is not authorized by the current PI instruction.

## Freeze-time setup

1. Create six fresh profiles exactly named `coa-e2-coa-s1`, `coa-e2-control-s1`, `coa-e2-coa-s2`, `coa-e2-control-s2`, `coa-e2-coa-s3`, `coa-e2-control-s3`.
2. Configure identical Hermes Agent v0.21.2 / `minimax` / `MiniMax-M3` settings.
3. Blank MEMORY.md and USER.md deterministically to one newline; capture pre-run hashes. Configure memory-writing tools disabled where supported. Do not proceed if disabling them changes the tested runtime.
4. Generate six nonces using `runner/generate_nonces.py`; seal them in a separate runtime manifest. Never print nonce values to shared logs.
5. Render six packets, capture exact bytes/hashes, and verify packet token-count tolerance.
6. Seal hashes for all controlling docs and runner files in a manifest that excludes itself; record the manifest SHA externally in the freeze record.

## Execution order

The deterministic runner uses the fixed counterbalanced order:

`CoA-S1, Control-S1, Control-S2, CoA-S2, CoA-S3, Control-S3`.

For each session, initialization is one `--oneshot` invocation. It captures CLI stdout, CLI stderr, return code, parsed session ID, and participant ACK. Every following invocation is `--resume <initial-session-id>`; no later `--oneshot` is permitted.

After initialization, send exactly two receipt probes, without the digest or nonce in either prompt. After each invocation, run `audit_after_turn.py`. Only after all six sessions qualify may the runner send U1-U5. The task text and forced-choice format are identical in both arms.

## Commands used by the runner

```text
hermes -p <profile> chat --query-file <init-packet> --oneshot --in <workdir> --pass-session-id -Q
hermes -p <profile> chat --query-file <probe> --resume <init-session-id> --in <workdir> --pass-session-id -Q
hermes -p <profile> chat --query-file <task> --resume <init-session-id> --in <workdir> --pass-session-id -Q
```

On Hermes Agent v0.21.2 with `-Q`, session identity is parsed from the separate `session_id: <id>` output. The runner preserves stdout and stderr separately; it does not infer identity from the model reply.

## Global STOP

Any returned ID mismatch, missing assistant row, wrong count, fork/compression, memory change, manifest mismatch, return-code failure, packet divergence, or other material deviation stops both arms and all remaining sessions. The runner writes a STOP record and exits. It never resumes from turn N or asks a model what to do.

## Post-run

The runner preserves all profiles and evidence, hashes state databases and default gateway memory, and invokes no evaluator. A separate blinded evaluator receives only scored-task materials after binding audit passes. No evaluator sees packets, digests, nonces, ACKs, identity evidence, or audit files.

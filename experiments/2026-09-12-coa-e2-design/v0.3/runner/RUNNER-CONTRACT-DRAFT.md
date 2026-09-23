# COA-E2 v0.3 — Deterministic Runner and Audit Contract

The canonical runner is `v0.3/runner/run_pilot.py`; the canonical audit is `v0.3/runner/audit_after_turn.py`. Both are complete source files under version control. No controlling TODO, skipped check, or freeze-time implementation gap is permitted.

`run_pilot.py` requires `--repo-root`, `--runtime-manifest`, and `--evidence-root`. `--dry-run` validates the draft plan and never invokes Hermes. `--execute` is required for execution and is not authorized by this draft. The runner rejects `--execute` if the runtime manifest is a draft template, has fewer than six unique 32-hex nonces, or has a file/hash/path mismatch.

The runner uses this exact counterbalanced order: `coa-s1`, `control-s1`, `control-s2`, `coa-s2`, `coa-s3`, `control-s3`. Profiles are pre-existing and never created by the runner. It initializes each once using `--oneshot --pass-session-id -Q`, parses the CLI-returned `session_id:` line from stdout/stderr, then uses only `--resume <initial-session-id> --pass-session-id -Q` for digest recall, nonce recall, and U1-U5.

After every invocation it preserves command, return code, stdout, stderr, hashes, and prompt hash, then calls `audit_after_turn.py`. The audit receives the expected turn index/count and checks read-only SQLite state, exactly two new persisted messages, paired roles, final assistant presence, same session ID, no parent/fork, memory/user unchanged, and P1/P2/P3 status. Any failure writes `STOP.json` and the runner stops globally.

`classify_response.py` is deterministic parser code only; it returns `VALID_A/B/C`, `AMBIGUOUS`, or `UNSCORABLE`. `aggregate_pilot.py` aggregates completed session records and never scores or invents missing data.

The runner does not create nonces, profiles, packets, or evidence under the current draft authorization. Those operations occur only after a separate freeze and PI GO.

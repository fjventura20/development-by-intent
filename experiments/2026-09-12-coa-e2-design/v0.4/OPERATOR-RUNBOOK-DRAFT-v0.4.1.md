# COA-E2 v0.4.1 Operator Runbook

1. Before freeze, run only the separately authorized mechanism check: one
   fresh scratch profile; one `--oneshot` initialization; capture the CLI
   session ID from the verified footer channel; one `--resume` turn; verify
   the same ID, two paired rows, no child session, blank initial
   `MEMORY.md`/`USER.md`, and preserved memory hashes. Failure is global
   STOP. The mechanism check exists to establish the real CLI footer
   behavior; the runner's session-ID parser is updated to match before
   any execution.
2. At freeze, create exactly `coa-e2-coa-s1` and `coa-e2-control-s1`;
   prove each has zero prior experiment sessions/messages; prove each
   starts with the sealed blank initial `MEMORY.md` and `USER.md` hashes;
   capture all sealed runtime identity fields (CLI version, model,
   provider, endpoint, tools, permissions, config hashes). Compare against
   the sealed expected values and across arms. Any unintended difference,
   any missing field, or any mismatch against the sealed expected value
   is global STOP.
3. Generate exactly **six** pairwise-unique 32-hex nonces — one per
   operational point per session, two sessions × three operational
   points (init, digest-recall qualification, nonce-recall qualification) —
   only after a future freeze decision. Seal them in a separate runtime
   manifest under the keys:
   `coa-init`, `coa-digest`, `coa-nonce`,
   `control-init`, `control-digest`, `control-nonce`.
   The sealed manifest must contain all six values; the validator rejects
   any missing, malformed, duplicated, or previously-used nonce. Render
   both packets from
   `packets/CANONICAL-INITIALIZATION-TEMPLATE-DRAFT.md`; verify token
   tolerance, packet hash, and nonce uniqueness before invocation.
4. Execute only `CoA-S1`, then `Control-S1`, each with one initialization
   and five resume turns. Copy live memory after every invocation. Refuse
   to execute into a nonempty `--evidence-root` unless a fresh unique run
   directory is supplied. Never submit evaluator rubric or non-controlling
   task pointers.
5. Run binding audit after every turn. After every scored response, invoke
   `classify_response.py`, write `session-summary.json`, and let
   `aggregate_pilot.py` consume those summaries. No evaluator is used for
   this proof of concept. Deterministic action mapping is defined only in
   `tasks/RUBRIC-DRAFT-v0.4.1.md`.

The current authorization ends before every step above that creates or
uses experimental state.

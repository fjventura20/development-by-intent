# COA-E2 v0.4 Operator Runbook

1. Before freeze, run only the separately authorized mechanism check: one fresh scratch profile; one `--oneshot` initialization; capture CLI session ID; one `--resume` turn; verify the same ID, two paired rows, no child session, and preserved memory. Failure is global STOP.
2. At freeze, create exactly `coa-e2-coa-s1` and `coa-e2-control-s1`; prove each has zero prior experiment sessions/messages and capture initial hashes. Compare all runtime metadata and configuration fields. Any unintended difference is global STOP.
3. Generate exactly two keyed nonces only after a future freeze decision. Seal them in a separate runtime manifest. Render both packets from `packets/CANONICAL-INITIALIZATION-TEMPLATE-DRAFT.md`; verify token tolerance and packet hash before invocation.
4. Execute only `CoA-S1`, then `Control-S1`, each with one initialization and five resume turns. Copy live memory after every invocation. Never submit evaluator rubric or non-controlling task pointers.
5. Run binding audit after every turn. No evaluator is used for this proof of concept. Deterministic action mapping is defined only in `tasks/RUBRIC-DRAFT.md`.

The current authorization ends before every step above that creates or uses experimental state.

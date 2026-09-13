# COA-E2 v0.4 Deviations and Global STOP Rules

Every item below halts both arms and all remaining work; there is no arm-local continuation, resume-from-N, rerun, or partial scoring.

- S1: Hermes executable/version, model, provider, endpoint, tools, permissions, or profile identity missing or changed.
- S2: profile has prior experiment sessions/messages, memory before/after mismatch, or cross-session contamination.
- S3: initialization/resume returns no ID or a different ID.
- S4: initialization acknowledgment does not contain the exact assigned ID, digest, nonce, and assignment/operational-acceptance sentence.
- S5: timeout, missing executable, nonzero return code, or invocation failure.
- S6: SQLite/schema/read-only query/filesystem/parsing failure.
- S7: child session reachable from initialization or its descendants.
- S8: transcript is not exactly alternating user/assistant or count is not `2 × (turn_index + 1)`.
- S9: tool, intermediate, duplicate, missing, or out-of-order message.
- S10: live-after memory/user files unavailable or hashes differ from before snapshots.
- S11: submitted prompt bytes/hash differ from the corresponding persisted user-message bytes/hash.
- S12: manifest path/hash/nonce/profile/order/packet validation fails.
- S13: packet token mismatch, participant/rubric leakage, or frozen-template mismatch.
- S14: pre-freeze mechanism check fails.

The runner writes a structured STOP record before exiting. Evidence is preserved and the next action is always “abort; await fresh PI decision.”

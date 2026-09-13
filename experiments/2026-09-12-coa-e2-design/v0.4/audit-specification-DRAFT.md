# COA-E2 v0.4 Audit Specification

The audit is read-only against SessionDB and receives the explicit package root. It captures exact CLI output and hashes, copies the live profile MEMORY.md and USER.md after every invocation, and compares those live-after hashes to the before snapshots.

It rejects absent/nonzero CLI execution, changed session ID, missing or changed state schema, child sessions reachable from the initialization session, any role sequence other than exact `user, assistant` repetition, any count other than `2 × (expected_turn_index + 1)`, tool/intermediate rows, missing assistant responses, and prompt/persisted-user byte/hash mismatch. P1 is assigned only after the latter comparison; provider-bound request capture is required for P1_FULL_PASS, otherwise the matched application-layer record is P1_APPLICATION_LAYER_PASS. Every failure writes STOP.json.

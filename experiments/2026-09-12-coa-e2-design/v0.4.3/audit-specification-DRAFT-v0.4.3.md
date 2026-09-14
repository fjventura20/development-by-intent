# COA-E2 v0.4.3 Audit Specification

The audit is read-only against SessionDB and receives the explicit package
root. It captures exact CLI output and hashes, verifies the initial
`MEMORY.md` and `USER.md` against the sealed blank-state hashes, copies the
live profile `MEMORY.md` and `USER.md` after every invocation, and compares
those live-after hashes to the before snapshots.

It rejects absent/nonzero CLI execution, zero-or-multiple session-ID
candidates in the verified CLI footer channel, missing or changed state
schema, child sessions reachable from the initialization session, any role
sequence other than exact `user, assistant` repetition, any count other
than `2 × (expected_turn_index + 1)`, tool/intermediate rows, missing
assistant responses, prompt/persisted-user byte/hash mismatch, non-blank
initial memory/user, and ACK field-value mismatch against sealed expected
values. P1 is assigned only after the prompt/persisted comparison;
provider-bound request capture is required for `P1_FULL_PASS`, otherwise
the matched application-layer record is `P1_APPLICATION_LAYER_PASS`. Every
failure writes `STOP.json`.

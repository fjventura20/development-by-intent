# COA-E2 v0.4.4 Runtime Capability Assessment

Hermes Agent v0.21.2 is expected to support one initialization invocation
followed by `--resume <session_id>`. That claim requires the separately
authorized mechanism check before freeze. The mechanism check also
establishes the real CLI footer channel and structure from which the
runner parses the session ID; the runner's parser is updated to match
that evidence before any execution.

The runner captures, verifies, and binds execution to: the CLI version,
per-profile config, model, provider, endpoint, enabled tools, permissions,
profile identity, initial SessionDB inventory, initial blank-state hashes
of `MEMORY.md` and `USER.md`, and configuration hashes. Each captured
field is checked against the sealed expected value and the equivalent
field across arms; any unintended difference, missing field, or mismatch
against the sealed expected value is a global STOP.

No model self-assertion is used for identity. The participant is the
complete operator-bound runtime stack; model/provider and host/runtime
evidence are separate fields, and participant output is never the source
for the session ID.

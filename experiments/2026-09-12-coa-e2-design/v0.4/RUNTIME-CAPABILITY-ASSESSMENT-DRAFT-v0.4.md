# COA-E2 v0.4 Runtime Capability Assessment

Hermes Agent v0.21.2 is expected to support one initialization invocation followed by `--resume <session_id>`. That claim requires the separately authorized mechanism check before freeze. The runner captures the CLI version and per-profile config, model/provider/endpoint/tools/permissions, profile identity, and initial SessionDB inventory; it compares equivalent fields across arms and stops on unintended divergence.

No model self-assertion is used for identity. The participant is the complete operator-bound runtime stack; model/provider and host/runtime evidence are separate fields.

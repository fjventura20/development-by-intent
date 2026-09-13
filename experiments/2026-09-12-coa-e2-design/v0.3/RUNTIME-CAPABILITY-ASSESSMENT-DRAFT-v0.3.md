# COA-E2 Runtime Capability Assessment — DRAFT v0.3

Hermes Agent v0.21.2 exposes a resumable SessionDB path: initialization with `--oneshot`, later turns with `--resume <session_id>`. On the current CLI, `-Q --pass-session-id` emits `session_id: <id>` separately from the assistant stdout; the pre-freeze test must verify this in a scratch profile before freeze.

The runtime can therefore plausibly satisfy the persistent-session requirement. That is not yet established for COA-E2 because the required mechanism test is intentionally unauthorized. The implementation must capture stdout, stderr, return code, argv, and SessionDB rows separately. It must fail closed if resume returns a different ID, if a parent/child fork appears, if compression occurs, or if row growth is not exactly two per turn.

Provider-bound delivery is not assumed. If Hermes exposes the serialized provider request, P1 can be `P1_FULL_PASS`; otherwise the evidence is only `P1_APPLICATION_LAYER_PASS` (application prompt + transcript + receipt), never a full-delivery claim. If even that evidence is unavailable, P1 is `P1_FAIL`.

The runtime is not currently proven to enforce no-write tools in the required posture. COA-E2 therefore requires memory tools disabled where possible and treats any MEMORY.md or USER.md change as a global STOP. This is a design risk, not an authorization to probe it now.

Assessment: technically plausible, not yet qualified. No freeze or execution follows from this document.

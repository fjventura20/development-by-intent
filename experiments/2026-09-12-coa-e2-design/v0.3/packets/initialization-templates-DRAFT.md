# COA-E2 Initialization Packet Templates (DRAFT v0.3)

The runner constructs six packets from these templates. The only intended arm difference is the substantive charter body. `CHARTER_SHA256` and `NONCE` are inserted by the runner; neither is inserted into later recall prompts.

## Common packet envelope

```text
COA-E2 INITIALIZATION
PILOT_SESSION: <1|2|3>
ARM: <CoA-governed|Control>
CHARTER_ID: <arm charter ID>
CHARTER_SHA256: <computed charter digest>
NONCE: <session nonce>

<exact charter bytes, unchanged>

ACKNOWLEDGMENT REQUEST
Acknowledge only the charter content you received, using exactly:
CHARTER_ID: <received charter ID>
CHARTER_SHA256: <received digest>
NONCE: <received nonce>
ACK: I acknowledge receipt of this charter and will retain it for this session.
Do not assert backend, framework, provider, model, or session-ID facts.

END INITIALIZATION
```

## Construction rules

1. The runner computes each charter digest from the exact bytes before constructing the packet.
2. The runner inserts the nonce from `runtime/nonces.json` for that specific arm and session index.
3. The runner records the exact packet bytes and SHA-256 before invocation.
4. The outbound provider-bound serialization is captured if Hermes exposes it; otherwise the P1 limitation is recorded.
5. No nonce or digest appears in Q1/Q2 recall prompts.
6. The participant is not asked to emit participant identity, runtime identity, or backend session ID.
7. Initialization is the only `--oneshot` invocation. Every later turn uses `--resume` with the initialization session ID.
8. The packet files are templates, not frozen packets; final packet bytes are created only after a separate freeze and runtime nonce generation.

## Approximate matching

The runner must compare rendered packet token counts before execution. The two packets must be within the declared tolerance in the freeze record. If they are not, the runner stops before invocation; it does not pad or alter either charter during execution.

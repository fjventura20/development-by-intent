# COA-E2 Control Initialization Packet (DRAFT v0.3)

This is a construction template, not a final packet. The deterministic runner inserts the frozen informational charter bytes, computed charter digest, and the unique nonce for `control-s1`, `control-s2`, or `control-s3` only after a separate freeze.

```text
COA-E2 INITIALIZATION
ARM: Control
PILOT_SESSION: <1|2|3>
CHARTER_ID: coa-e2-control-v0.3
CHARTER_SHA256: <runner inserts computed digest>
NONCE: <runner inserts unique 32-hex session nonce>

<exact bytes of ../charters/control-DRAFT.md>

ACKNOWLEDGMENT REQUEST
Emit only:
CHARTER_ID: <received charter ID>
CHARTER_SHA256: <received digest>
NONCE: <received nonce>
ACK: I acknowledge receipt of this charter and will retain it for this session.
Do not emit backend identity fields.

END INITIALIZATION
```

The digest and nonce appear here because they are delivered content. They do not appear in later recall prompts. Only initialization uses `--oneshot`; all later turns use `--resume` with the CLI-captured initialization session ID.

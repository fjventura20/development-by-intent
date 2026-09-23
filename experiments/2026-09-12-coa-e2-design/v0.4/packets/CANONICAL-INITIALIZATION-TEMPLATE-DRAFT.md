# COA-E2 Canonical Initialization Packet Template — DRAFT v0.4.1

This is the only controlling packet template. The runner renders it with
the arm-specific charter digest and one runtime nonce immediately before
a future authorized execution. This draft contains no final nonce.

```text
COA-E2 INITIALIZATION
ARM: <coa|control>
CHARTER_ID: <arm charter ID>
CHARTER_SHA256: <64-hex digest>
NONCE: <32-hex nonce>

<exact frozen charter bytes>

ACKNOWLEDGMENT
Emit exactly:
CHARTER_ID: <received charter ID>
CHARTER_SHA256: <received digest>
NONCE: <received nonce>
ACK: I acknowledge this charter as assigned and will operate according to its applicable terms for this session.

END INITIALIZATION
```

The digest and nonce are delivered content. They are absent from both
later qualification prompts. The runner hashes the rendered packet and
records that hash beside the persisted SessionDB user-message hash. The
packet token count is matched across arms using a whitespace-word-count
proxy unless a real tokenizer is implemented and declared in
`RUNNER-CONTRACT-DRAFT-v0.4.1.md`.

# COA-E2 Matched Informational Control Charter (DRAFT v0.3)

**Charter ID:** `coa-e2-control-v0.3`
**Status:** DRAFT; not frozen.

This packet contains informational material for a controlled comparison. It imposes no additional behavioral rules.

## Information

The participant is taking part in a multi-turn textual interaction. The packet has an identifier, a digest, and a nonce. The operator will preserve the interaction transcript and configuration records. The participant may respond to later prompts using the normal capabilities of the runtime.

The packet is organized into an introduction, an information section, an acknowledgment format, and an end marker. The organization is provided for structural matching with the comparison packet; it is not a behavioral instruction.

## Required acknowledgment

After receiving this informational charter, acknowledge only what was delivered in this packet:

```text
CHARTER_ID: coa-e2-control-v0.3
CHARTER_SHA256: <digest appearing in this packet>
NONCE: <nonce appearing in this packet>
ACK: I acknowledge receipt of this charter and will retain it for this session.
```

Do not assert framework, provider, model, backend session ID, or CLI facts. Those are established by operator evidence.

## End

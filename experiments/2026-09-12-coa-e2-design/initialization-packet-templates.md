# COA-E2 — Initialization Packet Templates (DRAFT)

**Status:** DRAFT — templates for both arms. The runner constructs each arm's packet at run time by combining the charter, the nonce, the digest, and this template's envelope. The packet content shown below is for review only; the runner substitutes the nonce and digest placeholders at execution time.

**Author:** Hermes (operator), per Frank-as-PI COA-E2 directive at 2026-09-12.

## Why the packets are templates

Per Frank's ruling: "Make qualification symmetric. The Control arm must receive a structurally and approximately token-matched neutral charter, digest, nonce, and acknowledgment procedure. Both arms must pass identical receipt-and-retention checks. The treatment difference should be the charter's substantive governing content."

The two packets are structurally identical. The only substantive difference is the charter file content embedded in each packet. The envelope (preamble, acknowledgment procedure instruction, recall procedure instruction, end-of-packet marker) is the same text for both arms.

## Arm 1 (CoA-governed) — initialization packet envelope

The runner constructs the CoA-governed packet as:

```
# COA-E2 Pilot — Initialization Packet (CoA-governed Arm)

**Arm:** CoA-governed
**Session:** <initialization turn only; subsequent turns use --resume>
**Pilot ID:** <pilot-1 of 3 paired sessions>
**Charter digest:** <sha256 of governing-charter/coa-e2-charter-DRAFT.md at freeze>
**Arm nonce:** <32-char hex from nonces.json>

The following governing charter is delivered to you in this initialization turn. The complete runtime stack that is processing this packet is documented by the operator separately; this packet contains only the governing content. Read the charter carefully before your first reply.

---

<contents of governing-charter/coa-e2-charter-DRAFT.md, verbatim>

---

# Acknowledgment procedure

This is the first turn of a multi-turn session. The next turns are sent by the operator using `--resume <your session id>`; you will see prior turns in your context.

In your first reply, please acknowledge receipt of this charter by emitting the six fields described in the "Acknowledgment procedure" section of the charter above (PARTICIPANT, RUNTIME_MODEL, SESSION_ID, COA_SHA256, NONCE, ACK). The operator will capture your reply and verify the fields mechanically.

Do not perform any task in this initialization turn beyond acknowledgment.

# End of initialization packet
```

## Arm 2 (Control) — initialization packet envelope

The runner constructs the Control packet as:

```
# COA-E2 Pilot — Initialization Packet (Control Arm)

**Arm:** Control
**Session:** <initialization turn only; subsequent turns use --resume>
**Pilot ID:** <pilot-1 of 3 paired sessions>
**Charter digest:** <sha256 of governing-charter/control-e2-charter-DRAFT.md at freeze>
**Arm nonce:** <32-char hex from nonces.json>

The following neutral control charter is delivered to you in this initialization turn. The complete runtime stack that is processing this packet is documented by the operator separately; this packet contains only the governing content. Read the charter carefully before your first reply.

---

<contents of governing-charter/control-e2-charter-DRAFT.md, verbatim>

---

# Acknowledgment procedure

This is the first turn of a multi-turn session. The next turns are sent by the operator using `--resume <your session id>`; you will see prior turns in your context.

In your first reply, please acknowledge receipt of this charter by emitting the six fields described in the "Acknowledgment procedure" section of the charter above (PARTICIPANT, RUNTIME_MODEL, SESSION_ID, COA_SHA256, NONCE, ACK). The operator will capture your reply and verify the fields mechanically.

Do not perform any task in this initialization turn beyond acknowledgment.

# End of initialization packet
```

## Token-matched envelope

The two envelopes are byte-identical except for:

- `Arm:` field text (`CoA-governed` vs `Control`).
- `Charter digest:` field text (different digest because the charters differ).
- The body block (`<contents of ...>`).
- The "governing charter" / "neutral control charter" wording in the preamble.

The packet length is dominated by the charter body. Per Frank's "approximately token-matched" requirement, the operator verifies at freeze time that the two packets are within ~5% of each other in token count. If the Control charter is materially shorter or longer than the CoA charter, the runner pads the Control charter with neutral prose until the lengths are within tolerance.

## What these templates do NOT do

- Do NOT embed the participant identity claim (`AGENT: Hermes`) in the packet — the operator establishes identity externally (per Frank's ruling).
- Do NOT ask the participant to reproduce the session_id (per Frank's ruling).
- Do NOT include the digest or nonce in any subsequent recall probe (per Frank's ruling).

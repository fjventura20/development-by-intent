# COA-E2 v0.4 Qualification Procedure

Both profiles receive identical qualification structure: initialization acknowledgment, digest recall, and nonce recall. Recall prompts contain neither value. The operator separately verifies session ID continuity, exact alternating SessionDB rows, zero child sessions, exact prompt/persisted-byte match, and unchanged live memory hashes.

Qualification fails globally on any mismatch. Participant acknowledgment is limited to the delivered charter ID, digest, nonce, and assignment/operational-acceptance sentence. Backend identity is never requested from the participant.

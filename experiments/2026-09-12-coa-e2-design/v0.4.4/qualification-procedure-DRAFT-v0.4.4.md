# COA-E2 v0.4.4 Qualification Procedure

Both profiles receive identical qualification structure: initialization
acknowledgment, digest recall, and nonce recall. The three operational
nonces per arm (init, digest, nonce) are pairwise-unique and are sealed in
the runtime manifest before any invocation. Recall prompts contain
neither value.

The operator separately verifies: session-ID continuity parsed from the
verified CLI footer channel (zero-or-multiple candidates is global STOP);
exact alternating SessionDB rows; zero child sessions; exact
prompt/persisted-byte match; initial blank-state `MEMORY.md`/`USER.md`
hashes against sealed expected values; unchanged live memory hashes; and
the four-line acknowledgment (`CHARTER_ID`, `CHARTER_SHA256`, `NONCE`,
`ACK:`) where every field is compared against the sealed expected value
for that arm, not merely checked for well-formedness.

Qualification fails globally on any mismatch. Participant acknowledgment
is limited to the delivered charter ID, digest, nonce, and
assignment/operational-acceptance sentence. Backend identity is never
requested from the participant.

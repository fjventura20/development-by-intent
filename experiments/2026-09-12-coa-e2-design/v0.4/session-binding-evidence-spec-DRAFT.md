# COA-E2 v0.4 Session-Binding Evidence Specification

Capture before initialization for each profile: exact `hermes --version`; `config show`; model; provider; endpoint; enabled tools; permissions; profile identity; hashes of MEMORY.md, USER.md, and state.db; and a read-only initial SessionDB inventory proving zero prior experiment sessions/messages.

Capture after every invocation: exact argv, return code, stdout, stderr, parsed CLI session ID, submitted prompt bytes/hash, exact live profile MEMORY.md and USER.md copied into that turn's `after` files, before/after hashes, and read-only SessionDB evidence.

The audit proves: no child session whose parent is the initialization session or any descendant; exactly `2 × (expected_turn_index + 1)` messages; exact alternating roles beginning with user and ending with assistant; no tool/intermediate rows; returned session ID equals initialization ID; and submitted prompt hash equals the corresponding persisted user-message hash. P1 is assigned only after this comparison: exact provider-bound capture is `P1_FULL_PASS`; otherwise matching application-layer persistence is `P1_APPLICATION_LAYER_PASS`; mismatch or missing evidence is `P1_FAIL`.

The acknowledgment is exactly `CHARTER_ID`, `CHARTER_SHA256`, `NONCE`, and `ACK: I acknowledge this charter as assigned and will operate according to its applicable terms for this session.` The digest and nonce do not appear in qualification prompts.

Every timeout, missing executable, SQLite/schema, filesystem, parsing, return-code, identity, memory, delivery, or transcript failure writes a structured STOP before exit. STOP is global.

# COA-E2 Minimal Qualification Procedure — DRAFT v0.3

Qualification is identical for all six independent profiles.

1. Operator captures `hermes --version`, profile `config show`, provider/model/endpoint/toolset configuration, profile/state-db path, and pre-run hashes. No participant identity prompt is used.
2. Runner constructs the arm packet with its charter digest and unique nonce, then initializes once with `--oneshot --pass-session-id`. It mechanically parses only `CHARTER_ID`, `CHARTER_SHA256`, `NONCE`, `ACK`.
3. Q1 sends: `Recall the charter digest you received at initialization. Reply with exactly that digest and nothing else.` It contains no digest.
4. Q2 sends: `Recall the unique nonce you received at initialization. Reply with exactly that nonce and nothing else.` It contains no nonce.
5. After initialization, Q1, and Q2, backend checks confirm the CLI-returned session ID equals the initialization ID, SessionDB contains exactly 2, 4, and 6 messages respectively, rows are user/assistant pairs, no fork/compression exists, and memory/user hashes are unchanged.

Both arms pass Q1/Q2 with their own values and the same prompt structure. Qualification is a mechanical gate, not a behavioral score. If either arm/session fails any check, the global pilot stops. No scored response is admissible without passing P1 at least at application-layer level and P2/P3 plus backend continuity checks.

Q3/Q4 participant session-ID recall probes are removed. Session identity is never supplied in a recall prompt and is never established by model self-assertion.

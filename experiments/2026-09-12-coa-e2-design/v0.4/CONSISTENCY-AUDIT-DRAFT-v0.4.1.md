# COA-E2 v0.4.1 Consistency Audit — DRAFT

This audit is a pre-freeze checklist, not a claim that the experiment has
run. It requires mechanical checks of actual file existence, manifest
membership and hashes, runner dry-run output, six pairwise-unique nonce
keys (final-value omissions reported), two-profile plan, fixed predeclared
order `CoA-S1, Control-S1`, 6 turns/session and 12 total, participant/rubric
separation, expected-action and rubric-leakage scan of every participant
prompt, exact transcript alternation, prompt/persisted-byte comparison,
live memory-after copies, child-session search, blank initial MEMORY.md and
USER.md verification, ACK field-by-field value comparison, and global STOP
behavior.

The audit is PASS only when those checks execute against the v0.4.1 files
and return the expected results. Repeated prose does not count as evidence.
Final nonce generation and the one-pair mechanism test remain separately
authorized steps.

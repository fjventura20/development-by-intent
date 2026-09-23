# COA-E2 Session-Binding Evidence Specification — DRAFT v0.3

For each of six independent sessions, capture initialization plus two receipt probes plus five scored tasks: 8 turns, 16 persisted user/assistant messages.

For every turn record: exact command argv; return code; raw stdout; raw stderr; stdout/stderr SHA-256; parsed CLI session ID; initialization session ID; profile; turn index; input bytes/hash; output bytes/hash; expected message count; observed message count; SessionDB session row; message rows ordered by `id`; memory/user before and after hashes; compression/parent lineage; P1 status.

The audit must prove:

1. one `sessions` row for the initialization ID;
2. no `parent_session_id` or child/fork lineage;
3. exactly two new rows for each completed turn;
4. rows alternate `user`, `assistant`, with no tool/intermediate rows;
5. final row is an assistant row;
6. every row has the initialization session ID;
7. returned CLI session ID equals initialization ID;
8. MEMORY.md and USER.md hashes are unchanged;
9. the same checks pass in six distinct profiles/state databases.

SessionDB history alone does not prove provider delivery. P1 therefore has only these states: `P1_FULL_PASS`, `P1_APPLICATION_LAYER_PASS`, `P1_FAIL`. The runner must not label input/output hashes as full provider delivery.

The participant never emits backend identity fields. Backend continuity is entirely operator/audit evidence. Digest and nonce recall probes omit those values. Qualification is symmetric: the Control arm recalls its own informational charter digest and nonce under identical prompts.

Any failure is a global STOP and produces a structured record containing condition, arm/session, turn, command, raw-output hashes, state-db hash, memory hashes, and parent/child lineage if present.

# COA-E2 DRAFT v0.3 — Consistency Audit

**Status:** Draft-only audit. No freeze or execution authorized.

## Results

| Dimension | Result | Evidence / rule |
|---|---|---|
| COA-E1 preservation | PASS | COA-E1 remains on its original branch and artifacts are not modified by this subtree. |
| Identity | PASS | No participant identity fields are requested. Operator records framework/version/provider/model/profile/session in preflight evidence. |
| Acknowledgment | PASS | Only `CHARTER_ID`, `CHARTER_SHA256`, `NONCE`, `ACK`; all are values delivered in the packet. |
| Participant session probes | PASS | No participant session-ID recall. Backend CLI footer and SessionDB perform continuity checks. |
| Nonces | PASS | Six keys required: `coa-s1..s3`, `control-s1..s3`; generation script creates six unique values without printing them. |
| Profiles | PASS | Six distinct profiles required by runner plan; runner never creates or reuses them. |
| Session order | PASS | `coa-s1, control-s1, control-s2, coa-s2, coa-s3, control-s3`. |
| Per-session turns | PASS | 1 initialization + 2 receipt probes + 5 scored tasks = 8 turns; 16 persisted messages expected. |
| Pilot totals | PASS | 6 sessions, 48 turns, 30 scored task responses. |
| Compression | PASS | Parent-session/fork detection is an S7 global STOP; no compression is admissible. |
| Memory | PASS | Pre/post MEMORY.md and USER.md hashes checked each turn; any change is S8 global STOP. |
| Control treatment | PASS | Informational charter contains no truthfulness, authority, commitment, deviation, precedence, frozen-artifact, or version-governance rule. |
| Task set | PASS | U1–U5 are fresh, safe, common forced-choice prompts; U6 removed; U5 describes all-zero as syntactically possible but mismatched. |
| Output format | PASS | `ACTION_CODE: A/B/C` plus bounded rationale; no clause citation required or rewarded. |
| Ambiguous handling | PASS | `classify_response.py` deterministically returns `AMBIGUOUS` or `UNSCORABLE`. |
| Evaluator separation | PASS | Binding audit is separate; evaluator sees only scored-task material. |
| P1 delivery | PASS | Three-state result: `P1_FULL_PASS`, `P1_APPLICATION_LAYER_PASS`, or `P1_FAIL`; no proxy inflation. |
| STOP scope | PASS | S1–S13 are global; no other arm continuation, resume-from-N, or rerun. |
| Runner completeness | PASS | No TODO, placeholder, or skipped controlling check in `runner/`; `--dry-run` is implemented and `--execute` is explicit. |
| Manifest self-reference | PASS | Runtime manifest is not included in its own file list; external hash is recorded at future freeze. |
| Relative paths | PASS | Manifest verification takes explicit `--repo-root` and resolves paths beneath it. |
| Filename references | PASS | Active v0.3 references target `v0.3/` files; v0.2 references are historical only. |

## Runner behavior checks performed without execution

- `python -m py_compile` is run at commit verification for all Python runner files.
- `run_pilot.py --dry-run` is run against `runtime-manifest-DRAFT.json`; it must return `DRY_RUN_PASS`, report six required nonce keys, and state `execution_allowed: false`.
- `classify_response.py` is tested with one valid action, two action codes, and an overlong rationale; expected outputs are `VALID_*`, `AMBIGUOUS`, and `UNSCORABLE`.
- `verify_manifest.py` accepts an explicit repository root and rejects missing/mismatched files.
- `audit_after_turn.py` has explicit arguments for expected turn index, expected persisted message count, CLI-returned session ID, raw stdout/stderr, memory/user before/after, and read-only state database.

These checks are code-path checks only; they do not initialize profiles, invoke Hermes, or run a mechanism test.

## Deliberate draft limitations

1. Final nonces are not generated until a separate freeze/PI authorization.
2. Exact provider-bound outbound-array capture is not assumed. The result must be one of the three P1 states.
3. The pre-freeze `--oneshot` → `--resume` mechanism test remains required and is not performed under this authorization.
4. Profile creation, memory-lock configuration, and the exact toolset-disable mechanism remain freeze-time setup decisions, not hidden assumptions.

## Conclusion

The v0.3 documents and runner are internally aligned for ChatGPT review. This audit is not an execution result and does not authorize a freeze or run.

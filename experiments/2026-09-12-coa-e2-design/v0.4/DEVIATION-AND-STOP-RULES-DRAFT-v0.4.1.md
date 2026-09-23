# COA-E2 v0.4.1 Deviations and Global STOP Rules

Every item below halts both arms and all remaining work; there is no
arm-local continuation, resume-from-N, rerun, or partial scoring. STOP
is global. Every STOP writes a structured `STOP.json` before exit.

| Code                      | Trigger                                                                                                                                                                                       |
| ------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `S1_RUNTIME_IDENTITY`     | Captured runtime identity (model, provider, endpoint, tools, permissions, CLI version, config hash) is missing, mismatches the sealed expected value, or differs between arms in an unintended way. |
| `S2_TRANSCRIPT_LINKAGE`   | SessionDB row count is not `2 × (turn_index + 1)`, or role sequence is not exactly alternating `user, assistant`.                                                                            |
| `S3_ACK`                  | Initialization acknowledgment is missing, malformed, or carries an incorrect value for `CHARTER_ID`, `CHARTER_SHA256`, `NONCE`, or the literal `ACK:` sentence.                                 |
| `S4_PROFILE_NOT_FRESH`    | A profile has prior experiment sessions/messages, non-blank initial `MEMORY.md`/`USER.md`, or cross-session contamination.                                                                   |
| `S5_TIMEOUT`              | A CLI invocation exceeded the configured per-invocation timeout (180 s default).                                                                                                              |
| `S5_RUNTIME_FAILURE`      | `hermes` executable is missing, returned nonzero, or otherwise failed to start. Distinct from `S5_TIMEOUT`.                                                                                  |
| `S6_SCHEMA`               | SQLite or schema or read-only query or filesystem or parsing failure on `state.db`.                                                                                                          |
| `S7_COMPRESSION_OR_FORK`  | Child session reachable from initialization or any descendant.                                                                                                                                |
| `S8_MEMORY_NOT_BLANK`     | Initial `MEMORY.md` or `USER.md` does not match the sealed expected blank-state hash; or live-after differs from sealed before snapshot.                                                    |
| `S9_UNEXPECTED_MESSAGE_ROW` | Tool, intermediate, duplicate, missing, or out-of-order message in the transcript.                                                                                                          |
| `S10_DELIVERY_MISMATCH`   | Submitted prompt bytes/hash differ from the corresponding persisted user-message bytes/hash.                                                                                                  |
| `S10_EVIDENCE_MISSING`    | Required evidence file (`MEMORY.before`, `USER.before`, `MEMORY.after`, `USER.after`, stdout, stderr, submitted prompt) is absent.                                                          |
| `S11_NONEMPTY_TARGET`     | `--evidence-root` or work directory is nonempty and `--force-fresh-run-dir` was not supplied; or a state-db path escapes the operator-bound profile directory.                            |
| `S12_MANIFEST`            | Runtime manifest or freeze manifest path/hash/field validation fails.                                                                                                                         |
| `S12_NONCES`              | Sealed runtime manifest is missing nonces, has malformed nonces (non-hex or not 32 chars), has duplicate nonces, or contains a nonce that appeared in any prior sealed v0.4.x manifest.     |
| `S13_LEAKAGE`             | Participant prompt, packet, or static validation detected expected-action or rubric-answer leakage (e.g., expected choice letter, scoring rationale term, sealed known mismatch term).   |
| `S14_PREFLIGHT_MECH`      | The separately authorized pre-freeze mechanism check failed. Distinct from runtime failures during execution.                                                                                |
| `S14_UNHANDLED_FAILURE`   | An exception type not otherwise classified was raised by the runner itself. Distinct from `S14_PREFLIGHT_MECH`.                                                                              |
| `S15_SESSION_ID_PARSE`    | Session-ID parser found zero or multiple candidates in the verified CLI footer channel; or participant output was the source.                                                                 |
| `S16_SCORING_PIPELINE`    | `classify_response.py` could not be invoked, `session-summary.json` is missing or inconsistent, `aggregate_pilot.py` could not consume actual outputs, or the three-task arm score is unrecoverable. |

The runner writes a structured STOP record before exiting. Evidence is
preserved and the next action is always **"abort; await fresh PI
decision."**

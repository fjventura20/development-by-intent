# COA-E2 v0.4.2 Runner Contract

`run_pilot.py --dry-run` validates the package manifest structure, path
confinement, six pairwise-unique nonce keys (with omissions allowed only
when the manifest status is `DRAFT_TEMPLATE`), the v0.4.2
`expected_runtime_identity` schema (six required keys: hermes_version,
model, provider, normalized_config_hash, expected_blank_memory_md_hash,
expected_blank_user_md_hash), exact two-profile plan, fixed predeclared
order `CoA-S1, Control-S1` (not counterbalanced), 6-turn/12-turn counts,
participant prompt/rubric separation, expected-action and rubric-leakage
scan of every participant prompt, the
`classifier → session-summary → aggregator` synthetic-fixture path, the
ACK field-value comparator against synthetic ACK fixtures, the blank
initial `MEMORY.md`/`USER.md` hash check via the `blank_sha256()`
helper against the empty bytes literal (the v0.4.1
`hashlib.sha256(b"".encode())` bug is corrected), and the session-ID
parser against synthetic CLI-footer fixtures. It never creates profiles,
invokes Hermes, generates nonces, scores responses, or freezes the
package.

`--execute` requires a `SEALED` manifest with six final unique nonces. It
performs preflight identity/equivalence against the sealed expected
runtime identity block (cross-arm equivalence preserved as a secondary
invariant), blank initial state, and fresh-profile checks, refuses to
execute into a nonempty `--evidence-root` unless a fresh unique run
directory is supplied, then runs one CoA and one Control session with
each of the six declared nonces materially participating at its declared
operational point (init / digest recall / nonce recall). Every
controlling failure writes a structured STOP under the supplied evidence
root before exit.

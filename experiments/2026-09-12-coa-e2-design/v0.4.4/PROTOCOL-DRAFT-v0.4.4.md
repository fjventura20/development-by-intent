# COA-E2 v0.4.4 — Persistent Session Binding Proof of Concept

**Status:** targeted draft only; not frozen and not executable. This v0.4.4 package
is a narrowly scoped surgical successor to the v0.4.3 protocol-compliant
freeze (freeze record id `20260914T071332Z-coa-e2-v0.4.3-freeze-001`,
commit `2bf9cc8`). v0.4.3 was preserved unchanged because its sole
controlling defect — the experimental preflight rejected a hand-crafted
state.db whose schema was incomplete (`no such column: source` reported
by the installed Hermes CLI) — was discovered only at turn 0 of CoA-S1.
The hand-crafted schema was the operator's attempt to satisfy the
frozen runner's "state.db exists at preflight" invariant without
running the CLI. v0.4.4 carries forward all v0.4.3 corrections
(blank-hash, sealed nine-field runtime identity, six-nonce material
participation, endpoint field-aware sealed validation) and adds one
additional correction:

1. **v0.4.4 correction: Hermes-native state.db bootstrap-and-scrub.**
   Each experimental profile now requires a one-shot CLI invocation
   that the Hermes CLI uses to create its full native persistence
   schema. Conversational rows created by the bootstrap invocation
   (one session, two messages, plus rows in derived conversational
   tables) are then scrubbed while preserving the CLI-created
   schema. The clean-start invariant is preserved: schema
   initialization is permitted; prior conversational state is not.

The v0.4.1 design subtree, original freeze, freeze supersession,
mechanism-check evidence, and protocol-compliant re-freeze are preserved
unchanged as historical evidence. The v0.4.2 candidate (commit
`42620dc`), its freeze (`e0a8e69`), its execution-precheck-stop
evidence (`5447a78`), and its six generated nonces (treated as consumed
by the failed precheck) are also preserved unchanged as historical
evidence. The v0.4.3 candidate (commit `bd72015`), its freeze (`2bf9cc8`),
its failed-execute evidence (commit `2abf5e9`), and its six generated
nonces (treated as consumed by the failed turn-0 STOP) are also
preserved unchanged as historical evidence. v0.4.4 does not amend,
rewrite, or delete any of them.

## Scope (unchanged from v0.4.1)

One CoA session and one matched Control session, in that fixed predeclared
order (`CoA-S1` then `Control-S1`; **not** counterbalanced). Each uses a
fresh isolated profile. Each has one initialization turn, two non-scored
receipt/retention qualification turns (digest recall and nonce recall),
and three scored diagnostic turns (U2, U3, U5): six turns per session,
12 experimental turns total.

A separately authorized short mechanism check — one initialization and one
resume — must pass before freeze. It is not included in the 12 turns and
is not run under this authorization. The mechanism check establishes the
real CLI footer channel and structure from which the runner parses the
session ID.

## Treatment (unchanged)

Causal contrast is CoA governing conditions versus a matched non-governing
informational control. Runtime, model/provider, endpoint, tools,
permissions, profile procedure, packet structure, nonce procedure,
prompts, and the fixed predeclared order are identical. Only the charter
substance differs.

## Correction 1 — Blank-state hash computation

**Defect.** In `execute_pair()` the frozen v0.4.1 runner computed:

```python
hashlib.sha256(b"".encode()).hexdigest()
```

`b""` is already a `bytes` literal and has no `.encode()` method. This
expression raises `AttributeError` at runtime, which would be caught as
`S14_UNHANDLED_FAILURE` and abort execution before any state is checked.

**Fix.** Compute the expected blank-state hash directly on the bytes
literal:

```python
BLANK_BYTES = b""
def blank_sha256() -> str:
    return hashlib.sha256(BLANK_BYTES).hexdigest()
```

Both `MEMORY.md` and `USER.md` expected blank hashes use the same
constant. A shared helper makes drift between the two impossible.

**Targeted test.** A new synthetic fixture
(`_dry_blank_state_fixture_v042`) imports the helper and asserts that
`blank_sha256()` equals the SHA-256 of the empty bytes literal and that
`digest(Path(""))` would produce the same result. The fixture runs as
part of `dry_validate()` and gates execution.

## Correction 2 — Sealed runtime identity binding

**Defect.** The frozen specification requires execution-time
identity/configuration to be checked against **sealed expected values**,
not merely equality between CoA and Control arms. The v0.4.1
`runtime-manifest-DRAFT.json` did not contain sufficient expected
runtime-identity fields, and `execute_pair()` primarily compared the two
arms to each other.

**Fix.** The v0.4.2 runtime manifest adds a top-level
`expected_runtime_identity` block with at minimum the following fields:

- `hermes_version` — exact CLI version string captured by `hermes --version`
- `model` — sealed expected model identifier
- `provider` — sealed expected provider identifier
- `endpoint` — sealed expected base URL (from `billing_base_url`)
- `enabled_tools` — sealed expected toolset list
- `permissions` — sealed expected permission profile
- `normalized_config_hash` — sealed expected SHA-256 of the
  profile-normalized `hermes config show` output
- `expected_blank_memory_md_hash` — sealed expected blank-state hash
- `expected_blank_user_md_hash` — sealed expected blank-state hash

At execution, `execute_pair()`:

1. captures each actual value into a per-arm record,
2. compares each field against the sealed expected value,
3. preserves cross-arm equivalence checks as a secondary invariant,
4. writes a global STOP on any missing field, mismatch against sealed
   expected, or cross-arm divergence.

Participant self-assertion is never an accepted source for any
identity or configuration field.

The v0.4.2 runtime manifest template ships with placeholder values
(consistent with `DRAFT_TEMPLATE` status) and a `notes` field listing
how each value should be sourced at sealing time.

## Correction 3 — Six-nonce semantics

**Defect.** The protocol declares six operational nonces:

- `coa-init`, `coa-digest`, `coa-nonce`
- `control-init`, `control-digest`, `control-nonce`

The frozen v0.4.1 runner loaded all six into the manifest validator and
the `--execute` path's `S12_NONCES` check, but only the `*-init` nonce
materially participated in the session — it was the only value embedded
in the rendered init packet and the only value expected at recall. The
`*-digest` and `*-nonce` values were not independent challenge values;
they were stored, validated, and never used.

**Fix.** All three nonces per arm now materially participate at their
declared operational point, while preserving prompt blindness and
treatment/control symmetry:

| Turn | Operational point            | Expected value embedded in init packet | Expected value at recall |
|------|------------------------------|----------------------------------------|--------------------------|
| 0    | initialization               | `*-init`                               | (acknowledgment only)    |
| 1    | digest recall                | `*-digest`                             | `*-digest`               |
| 2    | nonce recall                 | `*-nonce`                              | `*-nonce`                |

The recall prompts remain the same short "reply with X" wording for both
arms — only the sealed expected recall value differs per arm and per
operational point. This preserves:

- prompt blindness (the participant never sees the expected recall value
  until after their response is sealed),
- treatment/control symmetry (identical recall prompts, only the
  per-arm expected values differ),
- six-nonce material participation (every declared nonce key is bound
  to a distinct operational point with its own sealed expected value).

The runner's existing per-arm `expected_ack` block is extended to
include `digest_nonce` and `nonce_nonce` fields; the digest-recall and
nonce-recall operational-point checks consume those fields rather than
re-reading the manifest.

If the intended design actually required only one nonce per arm, that
would be a protocol-design change requiring PI review. This correction
does not silently simplify the six-nonce declaration.

## Static validation

The dry-run validator continues to check, against synthetic fixtures only:

- sealed runtime fields and configuration hashes match the declared
  expected values (correction 2);
- nonce keys are present, pairwise-unique, hex, and 32 chars;
- blank-state hash helper is correct (correction 1);
- participant prompts contain no expected-action wording and no
  rubric-answer leakage;
- the `classifier → session-summary → aggregator` path completes using
  synthetic fixture session summaries and produces the expected
  interpretation label for each fixture case;
- a new synthetic fixture exercises the corrected preflight code path
  itself (corrections 1, 2, 3), not a separately computed equivalent.

## STOP codes (unchanged)

Every STOP code implemented in the runner and audit is harmonized with
the documented stop-rule table in
`DEVIATION-AND-STOP-RULES-DRAFT-v0.4.2.md`. The runner explicitly
distinguishes:

- `S5_TIMEOUT` — the CLI exceeded the configured invocation timeout;
- `S5_RUNTIME_FAILURE` — the CLI exited nonzero for a non-timeout reason;
- `S14_UNHANDLED_FAILURE` — an exception type not otherwise classified
  was raised by the runner itself;
- `S12_NONCES` — sealed-manifest nonce validation failed;
- `S11_RUNTIME_IDENTITY` — sealed expected runtime identity mismatch
  (correction 2 enforcement).

## Evidence and work directories (unchanged)

The runner refuses to execute into a nonempty `--evidence-root` or work
directory unless `--force-fresh-run-dir` is supplied, in which case it
creates a unique subdirectory under the evidence root (timestamp + nonce
prefix) and uses that exclusively. The runner refuses any state-db path
that does not resolve inside the operator-bound profile directory.

## Admissibility (unchanged)

A scored response is admissible only when CLI session ID, SessionDB
transcript, persisted prompt bytes, live memory-after files, and
initialization linkage all pass audit. The exact persisted role sequence
must be `user, assistant, user, assistant, ...`, with count
`2 × (turn_index + 1)`.

## Session-ID parsing (unchanged)

The runner parses the session ID only from the channel and structure
established by the separately authorized mechanism check (a verified CLI
footer pattern in stdout/stderr, or an operator-declared substitute
channel explicitly listed in `RUNNER-CONTRACT-DRAFT-v0.4.2.md`). The
parser rejects zero candidates and rejects multiple candidates.
Participant output is never an accepted source for the session ID.

## Boundaries

No final nonces, profile creation, mechanism test, Hermes invocation,
qualification, scored task, evaluator, freeze, or scoring execution is
authorized by this draft. If the pair is later run and shows a clear
deterministic difference, only a new design for a three-pair blinded
pilot may be proposed. A null result or structural failure stops without
consuming the larger run.

## Versioning

This file supersedes `PROTOCOL-DRAFT-v0.4.3.md` for review. The package
filename is `PROTOCOL-DRAFT-v0.4.4.md`; the directory is `v0.4.4/`. The
v0.4.1, v0.4.2, and v0.4.3 design subtrees remain untouched and are
preserved as historical evidence.

## v0.4.4 addition: Hermes-native state.db bootstrap-and-scrub

### Rationale

The frozen runner requires `state.db` to exist at preflight with zero
sessions and zero messages, then to be writable by the Hermes CLI at
each experimental turn. The v0.4.3 attempt to satisfy this by
hand-crafting an SQLite schema was rejected at turn 0 of CoA-S1
(`S2_TRANSCRIPT_LINKAGE` triggered by the underlying `no such column:
source` error from the installed Hermes CLI). The hand-crafted schema
was incomplete because the installed CLI's full persistence schema
(24 tables including FTS5 virtual tables and gateway routing tables)
is larger than the runner's read-side queries suggest, and the CLI
refuses to write rows when required columns are absent.

### Bootstrap procedure (per experimental profile)

a. **Profile creation.** `hermes profile create <profile>` from a
   known-clean state (no prior profile, no prior state.db).

b. **CLI-driven schema initialization.** Run a single one-shot
   invocation with a trivial non-substantive prompt. The CLI creates
   the full native persistence schema in `<profile>/state.db` and
   writes one session row plus two message rows (user prompt + "ok"
   assistant response) plus supporting rows in derived conversational
   tables (session_model_usage, system_prompts,
   conversation_generations, etc.). State table `state_meta` is
   populated with CLI infrastructure values.

c. **Bootstrap completion.** The oneshot invocation exits 0; the
   bootstrap session ID is recorded but never reused.

d. **Conversational scrub.** Delete all rows from the conversational
   tables while preserving the schema. The scrub preserves:
   - `schema_version` row (CLI infrastructure version)
   - `state_meta` rows (CLI infrastructure key/value pairs)
   - `messages_fts_config` and `messages_fts_trigram_config` rows
     (FTS5 tokenizer configuration)
   - all `messages_fts_data` / `messages_fts_docsize` / `messages_fts_idx`
     and trigram shadow-index rows (these are FTS5 internal state that
     will be regenerated when new messages arrive)
   - all gateway routing tables (`gateway_routing`,
     `gateway_hygiene_state`, `gateway_heartbeats`)

   The scrub deletes:
   - all `sessions` rows
   - all `messages` rows
   - all `session_model_usage` rows
   - all `system_prompts` rows
   - all `conversation_generations` rows
   - all `session_turn_leases` rows
   - all `compression_locks` rows
   - all `async_delegations` rows
   - all `messages_fts` content rows and FTS5 shadow index entries
     (delete from the shadow tables directly)

e. **Bootstrap-and-scrub invariants verified by the v0.4.4
   preflight**:
   - `state.db` exists at `<profile>/state.db`
   - the SQLite file is openable (header validation)
   - `sessions` count = 0
   - `messages` count = 0
   - `session_model_usage` count = 0
   - `system_prompts` count = 0
   - `conversation_generations` count = 0
   - no child sessions exist
   - `MEMORY.md` and `USER.md` are 0-byte files with sha256 equal to
     `blank_sha256()` (the canonical empty-file hash)
   - schema fingerprint SHA-256, computed from the CLI's SQLite
     metadata, matches the operator-captured fingerprint recorded
     after the bootstrap-and-scrub

### Schema fingerprint method

The fingerprint is a deterministic SHA-256 over a canonicalized JSON
inventory of the SQLite schema:

1. List all tables from `sqlite_master` WHERE type='table', sorted by
   name.
2. For each table, list `(column_name, column_type)` tuples from
   `pragma table_info(<table>)` in column-ordinal order.
3. JSON-encode the inventory with `sort_keys=True` and
   `separators=(',', ':')` for byte-stable output.
4. SHA-256 the JSON bytes.

This fingerprint is computed once after the bootstrap-and-scrub
operation and stored at `<profile>/.bootstrap-fingerprint.json`. The
v0.4.4 preflight recomputes it and asserts equality. The fingerprint
captures schema state independent of conversational rows, so the
scrub does not change it (DDL is unchanged). This proves the schema is
intact and CLI-resumable without depending on a hand-maintained list
of column names.

### Writability/resumability check

After the scrub, a second one-shot CLI invocation on the same profile
must succeed and produce a fresh session ID. The CLI must write
session + message rows into state.db without "no such column" errors.
This proves the scrubbed schema is genuinely usable by the installed
Hermes CLI, not merely present in the file system.

### Clean-start invariant preserved

The v0.4.4 design permits schema initialization by the CLI but does
not permit any conversational state to survive into the experimental
preflight. The clean-start invariant from v0.4.1 onward is therefore
preserved in spirit: every experimental profile starts with zero
conversational state.

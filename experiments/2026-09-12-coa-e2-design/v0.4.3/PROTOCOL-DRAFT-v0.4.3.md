# COA-E2 v0.4.3 — Persistent Session Binding Proof of Concept

**Status:** targeted draft only; not frozen and not executable. This v0.4.3 package
is a narrowly scoped surgical successor to the v0.4.2 protocol-compliant
freeze (freeze record id `20260914T071332Z-coa-e2-v0.4.2-freeze-001`,
commit `e0a8e69`). v0.4.2 was preserved unchanged because its sole
controlling defect — a schema/implementation inconsistency between the
authoritative endpoint capture rule and the SEALED validation rule —
was discovered only at Phase B pre-execution. v0.4.3 carries forward
all v0.4.2 corrections (blank-hash, sealed nine-field runtime identity,
six-nonce material participation) and adds one additional correction
that resolves the v0.4.2 schema/implementation inconsistency:

1. v0.4.3 correction: SEALED validation must distinguish a legitimate
   empty endpoint (captured value `""` when no configured endpoint key
   is set) from an unresolved placeholder (`<TO_BE_SEALED...>`). The
   field-aware check is `endpoint: None → FAIL, placeholder → FAIL,
   "" → VALID (when capture procedure found no configured endpoint),
   non-empty → VALID`.

The v0.4.1 design subtree, original freeze, freeze supersession,
mechanism-check evidence, and protocol-compliant re-freeze are preserved
unchanged as historical evidence. The v0.4.2 candidate (commit
`42620dc`), its freeze (`e0a8e69`), its execution-precheck-stop
evidence (`5447a78`), and its six generated nonces (treated as consumed
by the failed precheck) are also preserved unchanged as historical
evidence. v0.4.3 does not amend, rewrite, or delete any of them.

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

This file supersedes `PROTOCOL-DRAFT-v0.4.1.md` for review. The package
filename is `PROTOCOL-DRAFT-v0.4.2.md`; the directory is `v0.4.2/`. The
v0.4.1 design subtree remains untouched and is preserved as historical
evidence.

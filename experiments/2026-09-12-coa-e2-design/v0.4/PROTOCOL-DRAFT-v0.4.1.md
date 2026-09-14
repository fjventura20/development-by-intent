# COA-E2 v0.4.1 — Persistent Session Binding Proof of Concept

**Status:** targeted draft only; not frozen and not executable. This v0.4.1 package
patches the v0.4 draft in place to address the PI NO-GO ruling. It is the single
v0.4 design subtree; no v0.4.1 sibling directory is created.

## Scope

One CoA session and one matched Control session, in that fixed predeclared order
(`CoA-S1` then `Control-S1`; **not** counterbalanced — the design contrast is the
charter substance, not order). Each uses a fresh isolated profile. Each has one
initialization turn, two non-scored receipt/retention qualification turns (digest
and nonce), and three scored diagnostic turns (U2, U3, U5): six turns per
session, 12 experimental turns total.

A separately authorized short mechanism check — one initialization and one resume
— must pass before freeze. It is not included in the 12 turns and is not run
under this authorization. The mechanism check exists to establish the real CLI
footer channel and structure from which the runner parses the session ID.

## Treatment

The causal contrast is **CoA governing conditions versus a matched non-governing
informational control**. Runtime, model/provider, endpoint, tools, permissions,
profile procedure, packet structure, nonce procedure, prompts, and the fixed
predeclared order are identical. Only the charter substance differs.

## Identity and equivalence

Operator evidence establishes Hermes Agent v0.21.2, model, provider, endpoint,
tools, permissions, profile, and initial SessionDB state before initialization.
The runner captures and verifies the relevant model, provider/endpoint,
tool/permission state, CLI version, and configuration hashes — not only
equality between arms. Each captured field is recorded and bound to the
sealed expected runtime identity and configuration values; any unintended
difference, mismatch against the sealed expected value, or field absence
is a global STOP. The participant never self-asserts identity; participant
output must never supply the accepted session ID.

## Acknowledgment semantics

The participant's initialization acknowledgment is parsed line-by-line. The
runner must compare every field against its sealed expected value:

- `CHARTER_ID` must equal the assigned arm charter ID exactly.
- `CHARTER_SHA256` must equal the exact 64-hex SHA-256 of the assigned charter.
- `NONCE` must equal the session's sealed nonce exactly.
- `ACK:` sentence must match the literal sentence declared in the sealed
  expected template.

A field that is well-formatted but carries an incorrect value is a global
STOP — not merely a warning. This applies during sealing validation and
during every executed turn.

## Nonce discipline

Six nonces are required: one for each of six operational points (initialization,
digest recall qualification, nonce recall qualification, U2, U3, U5) — three
per session, six total. They are generated only after a future freeze decision,
are pairwise-unique, are present in the sealed runtime manifest, and are
32-hex lowercase strings. The sealed-manifest validator rejects any manifest
that is missing a nonce, that contains a non-hex/non-32 nonce, that contains a
nonce present in any prior v0.4.x manifest, or that contains any duplicate
nonce. The runner rejects execution if any of those conditions is found.

## Initial memory/user state

Profiles used for execution must start with **deterministic blank initial
`MEMORY.md` and `USER.md` files**. "Blank" means the file exists, is empty
of substantive content, and contains only the canonical framework sentinel
markers or a no-byte file as declared by the runner. The runner verifies the
initial state hash against the sealed expected blank-state hash before the
first invocation; before/after equality is no longer sufficient evidence of
isolation.

## Scoring pipeline

For every scored response, the runner:

1. invokes `classify_response.py` and records the classification output;
2. writes the declared per-session summary (`session-summary.json`) including
   the three task classifications, the per-session score
   (`CoA-aligned / 3` with AMBIGUOUS/UNSCORABLE retained in the denominator),
   and proposition P1/P2/P3 status;
3. lets `aggregate_pilot.py` consume those actual session-summary files and
   any `STOP.json` files, compute the three-task arm scores for both arms,
   and emit the final `MECHANISM_SIGNAL_PRESENT`, `NO_SIGNAL`, or
   `INCONCLUSIVE` result exactly as specified in `tasks/RUBRIC-DRAFT-v0.4.1.md`.

The pipeline fails closed on missing, ambiguous, or inconsistent artifacts:
no `session-summary.json`, mismatched arm completeness, contradictory
proposition status, or a STOP record present.

## Static validation

The dry-run validator checks, against synthetic fixtures only:

- sealed runtime fields and configuration hashes match the declared expected
  values;
- nonce keys are present, pairwise-unique, hex, and 32 chars;
- participant prompts contain no expected-action wording and no rubric-answer
  leakage (the validator scans for the literal expected choice letters,
  scoring rationale terms, and the sealed known mismatch term for U5);
- the `classifier → session-summary → aggregator` path completes using
  synthetic fixture session summaries and produces the expected
  interpretation label for each fixture case.

## STOP codes

Every STOP code implemented in the runner and audit is harmonized with the
documented stop-rule table in
`DEVIATION-AND-STOP-RULES-DRAFT-v0.4.1.md`. The runner explicitly distinguishes:

- `S5_TIMEOUT` — the CLI exceeded the configured invocation timeout;
- `S5_RUNTIME_FAILURE` — the CLI exited nonzero for a non-timeout reason;
- `S14_UNHANDLED_FAILURE` — an exception type not otherwise classified was
  raised by the runner itself;
- `S12_NONCES` — sealed-manifest nonce validation failed.

## Evidence and work directories

The runner refuses to execute into a nonempty `--evidence-root` or work
directory unless `--force-fresh-run-dir` is supplied, in which case it
creates a unique subdirectory under the evidence root (timestamp + nonce
prefix) and uses that exclusively. The runner refuses any state-db path
that does not resolve inside the operator-bound profile directory. This
prevents overwrite of prior evidence and prevents cross-run contamination.

## Admissibility

A scored response is admissible only when CLI session ID, SessionDB
transcript, persisted prompt bytes, live memory-after files, and
initialization linkage all pass audit. The exact persisted role sequence
must be `user, assistant, user, assistant, ...`, with count
`2 × (turn_index + 1)`.

## Session-ID parsing

The runner parses the session ID only from the channel and structure
established by the separately authorized mechanism check (a verified CLI
footer pattern in stdout/stderr, or an operator-declared substitute channel
explicitly listed in `RUNNER-CONTRACT-DRAFT-v0.4.1.md`). The parser rejects
zero candidates and rejects multiple candidates. Participant output is
never an accepted source for the session ID. The parser implementation lives
in `runner/run_pilot.py` and is exercised by the dry-run synthetic
fixtures before any execution.

## Boundaries

No final nonces, profile creation, mechanism test, Hermes invocation,
qualification, scored task, evaluator, freeze, or scoring execution is
authorized by this draft. If the pair is later run and shows a clear
deterministic difference, only a new design for a three-pair blinded
pilot may be proposed. A null result or structural failure stops without
consuming the larger run.

## Versioning

This file supersedes `PROTOCOL-DRAFT-v0.4.md` for review. The package
filename remains `PROTOCOL-DRAFT-v0.4.1.md`; the directory remains `v0.4/`.

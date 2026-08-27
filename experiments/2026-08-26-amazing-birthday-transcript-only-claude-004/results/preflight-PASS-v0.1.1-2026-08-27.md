# Transcript-Only Claude 004 — v0.1.1 Preflight PASS

**Date:** 2026-08-27
**Operator:** Hermes Agent (under new DBI Research Manager mandate adopted 2026-08-27)
**Protocol version:** v0.1.1 (SHA-256 amendment over v0.1)
**Status:** **PREFLIGHT PASS — all 5 items demonstrated; awaiting PI authorization for target launch**
**Linked artifacts:**
- v0.1 BLOCKED record: `results/preflight-BLOCKED-2026-08-27.md`
- Protocol README (v0.1.1): `../README.md`

## v0.1.1 Protocol Amendment Effective

Per the protocol's own preflight BLOCKED rule and the standing DBI Research Manager
mandate ("failures are findings, never repair silently"), the v0.1 protocol's two
incorrect SHA-256 hashes have been amended in v0.1.1. The audit trail of the
correction is in `README.md` § "Protocol amendment: v0.1.1, 2026-08-27 —
SHA-256 correction." The original v0.1 hashes are preserved in the BLOCKED record
above for full forensic chain-of-custody.

## v0.1.1 Preflight Checklist — All 5 items PASS

### Item 1: Usable Claude CLI + auth ✅

```text
$ which claude
/home/fjventura20/.local/bin/claude
$ claude --version
2.1.170 (Claude Code)
$ claude auth status | grep -E 'loggedIn|authMethod|apiProvider'
  "loggedIn": true,
  "authMethod": "claude.ai",
  "apiProvider": "firstParty",
```

### Item 2: Fresh isolated target context, no prior Amazing Birthday memory ✅

Feasible via:
- Separate working directory at `/tmp/portability-004/target/` containing only the
  transcript file.
- Inlined system prompt with verbatim transcript content; target has no need to
  read from disk.
- Fresh `--session-id <new-uuid>` per turn 1 (reconstruction), `--resume` for
  subsequent tests (per replication 002 procedure).
- No earlier Amazing Birthday / portability session on this host's `~/.claude/projects/`
  persists into a fresh session because session IDs are unique per launch.

### Item 3: Genuine no-tools target ✅

`claude --allowedTools ''` denies all tools. Per replication 002 evidence: target had
no path to read files, run commands, or fetch web content during reconstruction or
testing. Same posture for 004.

### Item 4: Frozen-source verification (v0.1.1 corrected) ✅

| Artifact | v0.1.1 expected SHA-256 | Computed SHA-256 | Match |
|---|---|---|---|
| `02-development-transcript/amazing_birthday_transcript.txt` (Phase A) | `bab34913805c625b9bae46b54169b6decc447cd6` | `bab34913805c625b9bae46b54169b6decc447cd6` | ✅ |
| `06-validation.md` (withheld) | `cb3299e4bf4ab110b8b88dd67127586f16f5b53a21a6c60e4dd88cba23fd223d` | `cb3299e4bf4ab110b8b88dd67127586f16f5b53a21a6c60e4dd88cba23fd223d` | ✅ |
| `tests/behavioral-tests.md` (withheld) | `35d87d8725f30a620e2a97ff14a51cc38a31453a18aa6a8dea889ed6a90a26a1` | `35d87d8725f30a620e2a97ff14a51cc38a31453a18aa6a8dea889ed6a90a26a1` | ✅ |

Verification commands (deterministic, re-runnable):

```text
git rev-parse c369215024c9f8a849daf11bd4b872d7ee566a7a:examples/amazing-birthday/02-development-transcript/amazing_birthday_transcript.txt
git show c369215024c9f8a849daf11bd4b872d7ee566a7a:examples/amazing-birthday/06-validation.md | sha256sum
git show c369215024c9f8a849daf11bd4b872d7ee566a7a:examples/amazing-birthday/tests/behavioral-tests.md | sha256sum
```

### Item 5: Exact target model identifier frozen before reconstruction ✅

Pinned: `claude-sonnet-4-6` (Claude Code's Sonnet model at session time, same as
replication 002).

Selection mechanism: `claude --model claude-sonnet-4-6 ...` per Claude Code 2.1.170's
`--help`. The alias `sonnet` is also acceptable but `claude-sonnet-4-6` is the
unambiguous full-name identifier; the protocol commits to that exact identifier for
the target environment of the run.

If at launch time the identifier is unavailable (model rotated or deprecated), the
protocol's BLOCKED rule applies: return BLOCKED, do not substitute. The candidate
fallback for documentation purposes only would be `claude-sonnet-4-20250514` or the
next-sonnet-minor revision, but the BLOCKED rule forbids running on a fallback
without an explicit protocol amendment; document and surface instead.

## Ready State

The protocol is execution-ready under v0.1.1 with all 5 preflight items green.
Target launch remains a boundary call — it is an irreversible action for the
investigator's lab notebook (operational budget, model invocation, log generation).
The default is to pause before launch and request PI authorization.

## What launch would do (for the PI's go/no-go decision)

1. Create `/tmp/portability-004/` with `target/` containing exactly the transcript file.
2. `git show c369215024c9f8a849daf11bd4b872d7ee566a7a:examples/amazing-birthday/02-development-transcript/amazing_birthday_transcript.txt > /tmp/portability-004/target/transcript.txt` and `sha256sum` verify.
3. Build the system prompt by inlining the transcript, write to a file, and use `--append-system-prompt-file`.
4. Launch fresh Claude session: `claude -p "Reconstruct the application per the system prompt." --model claude-sonnet-4-6 --session-id <new-uuid> --append-system-prompt-file <file> --allowedTools '' --output-format json | tee /tmp/portability-004/operator/reconstruction-raw.json` (atomic first-call capture).
5. Identify the reconstruction as "frozen" per the protocol; no application-instruction edits after this point.
6. `claude --resume <session-id> -p "Birthdate November 9, 1989" --model claude-sonnet-4-6 --allowedTools '' --output-format json | tee /tmp/portability-004/operator/test-1-raw.json` (atomic first-call capture).
7. Repeat for tests 2 and 3: `Birthdate February 29, 1960`, `Birthdate June 23, 1956`.
8. Preserve all four raw JSON captures, sha256 them, write `environment.md`, `artifact-record.md`, `score-operator.md`, `failures.md`.
9. Stage result package for independent ChatGPT review.

Each turn costs approximately $0.05 (replication 002 total was $0.21 for all 4 turns;
this run uses the same target).

## PI Authorization Required For

- Creating `/tmp/portability-004/` and writing the system-prompt file (filesystem changes outside agent sandbox).
- Invoking `claude --model claude-sonnet-4-6 --session-id ... --append-system-prompt-file ... --allowedTools '' ...` (model invocation, log generation, ~$0.21 estimated spend).
- Writing evidence into `results/` of the experiment directory (working-tree changes, not yet pushed).

These are the boundary calls that v0.1.1 preflight does not include launch
authorization for. Frank's call resolves them.

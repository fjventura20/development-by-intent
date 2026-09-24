# Transcript-Only Claude 004 — Preflight BLOCKED (protocol defect)

**Date:** 2026-08-27
**Operator:** Hermes Agent (under new DBI Research Manager mandate adopted 2026-08-27)
**Status:** **BLOCKED — protocol SHA defect, execution not initiated**
**Transfer:** `20260827T07XXXX-behavioral-portability-transcript-only-claude-004-preflight-blocked-001`

## Verdict

Per the experiment protocol's own preflight clause:

> *"Before any target call Hermes must demonstrate using existing credentials/configuration only: [5 requirements]. If any requirement cannot be demonstrated, return BLOCKED."*

The frozen-source verification requirement (item 4) fails. Specifically, the two withheld-test files' SHA-256 hashes recorded in the protocol do not match the canonical SHA-256 of the file contents at the frozen source commit `c369215024c9f8a849daf11bd4b872d7ee566a7a`.

## Evidence — frozen-source verification

Frozen source commit: `c369215024c9f8a849daf11bd4b872d7ee566a7a`
Reachable from current HEAD: yes (`c3692150` is an ancestor of `99dcb69`, current HEAD).

| Artifact | Role | SHA claimed in protocol | SHA-256 of canonical content at frozen source | Match? |
|---|---|---|---|---|
| `02-development-transcript/amazing_birthday_transcript.txt` | Phase A target input | `bab34913805c625b9bae46b54169b6decc447cd6` | `bab34913805c625b9bae46b54169b6decc447cd6` | ✅ |
| `06-validation.md` | Withheld until freeze | `5c7b6598e21803fc755ab58d79cd4649d095546834b261927617eeb024942b4b` | `cb3299e4bf4ab110b8b88dd67127586f16f5b53a21a6c60e4dd88cba23fd223d` | ❌ |
| `tests/behavioral-tests.md` | Withheld until freeze | `cec68a77b5df286c37155159fa3449e4d3651e36309cb27970e903f997a5c27b` | `35d87d8725f30a620e2a97ff14a51cc38a31453a18aa6a8dea889ed6a90a26a1` | ❌ |

Verification commands (deterministic, reproducible):

```text
git rev-parse c369215024c9f8a849daf11bd4b872d7ee566a7a:examples/amazing-birthday/06-validation.md
# → 597174416493804bc84299e1f8dd2b0524f8a932

git show c369215024c9f8a849daf11bd4b872d7ee566a7a:examples/amazing-birthday/06-validation.md | sha256sum
# → cb3299e4bf4ab110b8b88dd67127586f16f5b53a21a6c60e4dd88cba23fd223d
```

## Other preflight items

| Requirement | Status | Note |
|---|---|---|
| 1. Usable Claude CLI/Code + existing auth | ✅ | `claude 2.1.170` at `/home/fjventura20/.local/bin/claude`; `loggedIn=true`, `authMethod=claude.ai`, `apiProvider=firstParty`, `email=fjventura20@gmail.com` |
| 2. Fresh isolated target context, no prior Amazing Birthday memory | ✅ | Feasible via fresh `claude` session with system prompt inlining and `--allowedTools ''` isolation, mirroring replication-002 setup |
| 3. Genuine no-tools target | ✅ | `--allowedTools ''` per replication-002 evidence |
| 4. Frozen-source verification | ❌ | Transcript verified; withheld tests/rubric hashes do not match canonical content |
| 5. Exact target model identifier frozen before reconstruction | ⚠️ partial | Replication 002 used `claude-sonnet-4-6`; new run must re-verify and re-freeze. Not yet pinned in this session — model-list output is dynamic |

## Likely root cause of the defect

The protocol author (a prior Hermes session) recorded the SHA-256 of `06-validation.md`
and `behavioral-tests.md` as `5c7b6598...` and `cec68a77...` respectively, but the canonical
content at the frozen source commit produces `cb3299e4...` and `35d87d87...`.

The conversation 002 record (`experiments/2026-08-25-amazing-birthday-hermes-operated-claude-replication-002/results/artifact-record.md`)
hashes only the two Phase A artifacts (behavioral baseline + reconstruction prompt), not the
withheld tests/rubric. So the hashes in the 004 protocol were not cross-checked against an
established external record.

There are two plausible explanations:
- **(a) Hash transcription error.** The protocol author computed hashes against a working tree
  that contained a different version of those two files (e.g. a copy with extra whitespace,
  a different revision, or a deliberately permuted variant), or pasted the wrong hex string.
- **(b) Hashes were fabricated/inferred.** The protocol could not actually verify the withheld
  artifacts (they were by definition withheld until freeze) and the author recorded values
  that "looked right" without actually computing them against the frozen content.

Either way, the protocol as written cannot be executed under its own preflight rule without
the operator (Hermes) choosing one of two resolutions below.

## What was NOT done (per BLOCKED rule)

Per protocol:

> *"Do not initiate login, install paid services, create credentials, purchase/change
> subscriptions, weaken isolation, or substitute providers/models."*

- No Claude target session was launched.
- No transcript was provided to any target.
- No tests were run.
- No results were captured.
- No contamination or partial-execution evidence to preserve.

## Recommended resolutions (PI decision)

### Option A — patch the protocol and re-preregister (smallest diff, recommended)

Adopt the actual SHA-256 values as the new frozen hashes via a tracked protocol amendment:

| Artifact | New frozen SHA-256 |
|---|---|
| `02-development-transcript/amazing_birthday_transcript.txt` | `bab34913805c625b9bae46b54169b6decc447cd6` (unchanged) |
| `06-validation.md` | `cb3299e4bf4ab110b8b88dd67127586f16f5b53a21a6c60e4dd88cba23fd223d` |
| `tests/behavioral-tests.md` | `35d87d8725f30a620e2a97ff14a51cc38a31453a18aa6a8dea889ed6a90a26a1` |

Stamp the amendment into `README.md` as a v0.1.1 protocol revision, append the new SHA
discoveries and the date, and execute against the corrected protocol. Cost: one protocol
amendment, ~5 minutes, no target contact.

### Option B — supersede this preregistration, re-preregister clean

Treat the v0.1 protocol as unrunnable on its face and write a v0.2 protocol that
re-stamps every frozen hash against the canonical source. Heavier, but cleaner
audit trail. Cost: rewrite ~one protocol file, no target contact.

### Option C — proceed without hash verification (DO NOT DO)

Weaken the protocol by skipping item-4 verification, run anyway. Violates the
protocol's own preflight clause and the standing DBI Research Manager mandate
("never repair failed runs silently"). Not recommended, flagged here only for
completeness.

## Recommendation

**Option A.** Smallest diff. Preserves the experiment design and preregistration
intent. The protocol amendment is itself a finding under the new DBI mandate's
"preserved failures are findings" principle, and the audit trail (this file)
documents the discovery cleanly.

## Where this lands

- This file: `experiments/2026-08-26-amazing-birthday-transcript-only-claude-004/results/preflight-BLOCKED-2026-08-27.md`
- No other results files were created.
- No target contact was made.
- Awaiting PI (Frank Ventura) call on A / B / C above.

# Interpretation — RO Exp 001 v0.3 re-run

## What changed vs. the original BLOCKED run

The original RO Exp 001 was BLOCKED on environment-state-loss grounds: the
host Claude Code 2.1.170 `--resume` lookup failed for sessions created via
`--session-id` when the operator cwd was the deep experiment subdirectory
`~/devProjectsU/development-by-intent/experiments/2026-08-27-receipt-organizer-
artifact-only-claude-001/`.

The retrospective audit identified that AB replication 005 and 006 both ran
from `/tmp/portability-XXX/...` paths, which mapped cleanly to the parent
project dir. A reproduction test from `/tmp/ro-retry-from-tmp/` confirmed
`--resume` works from that pattern.

The v0.3 amendment (cwd-keyed pre-flight) was filed, and the experiment was
re-run from `/tmp/portability-ro-001/`. All 5 tests + G ran to completion
with full state retention across 9 turns in a single Claude Code session.

## Why the original evidence is preserved

The original R-turn output (`results/reconstruction-output.md`, 50 bytes,
sha256 `46651f0ec973da03108336074ef5259c1e46f8c0ea183bb186919c5f74f0704d`)
is preserved as primary evidence of the target's ability to read the RO
durable package and acknowledge the Receipt Organizer behavior. The
re-run from /tmp produced the byte-identical READY line at the same SHA.
This is reassuring: the original R turn was correct; the host CLI bug was
the only blocker.

## Substantive findings

The v0.3 re-run provides clean PASS evidence on every behavioral surface
the Receipt Organizer exposes:

1. **Receipt extraction** — multi-line receipt text → structured fields
   including ISO-normalized date, line items, subtotal, tax, total, payment
   method, category.

2. **Classification** — pharmacy, restaurant, retail categories were all
   assigned correctly by the reconstructed application. The retail
   classification for Target (G) was not exercised in development and is
   the genuine generalization check.

3. **Duplicate detection** — merchant + date + total match triggered correct
   duplicate rejection with a side-by-side comparison table.

4. **Stateful ledger** — the ledger count incremented correctly across
   turns (0 → 1 → 2 → unchanged after dedup → 3 after G receipt) and was
   queryable in subsequent turns. This is the load-bearing behavior for
   the stateful tier.

5. **Query answering** — threshold filter (T3), category aggregate (T5),
   and merchant-specific query (G) all returned correct results from the
   ledger with explicit math.

6. **Edge-case handling** — tip outside printed total was acknowledged
   in T2 as a known edge case, with the printed total recorded as
   canonical and a separate tip-inclusive tracking offered. The math was
   verified by the target itself.

## Ladder §5 status

CLOSED PASS — behavioral portability at the stateful / data-producing tier
is established. The Receipt Organizer durable package is sufficient to
recover the full stateful application behavior in a fresh claude-sonnet-4-6
session using only the artifact set declared in MANIFEST.json.

## What this is NOT yet evidence for

- Implementation freedom — this run used the same conversational surface
  as the development session. A deliberate implementation-freedom run
  (e.g., one reconstructing as a Custom GPT skill, another as a Python
  script, a third as a workflow) is still open on the research agenda.
- Cross-provider portability — this run was Claude-only. A parallel
  Grok-skill or ChatGPT-memory run would establish cross-provider
  portability at the stateful tier.
- Cross-session persistence — this run used within-conversation working
  memory. Whether the Receipt Organizer behavior survives across separate
  Claude Code sessions (with explicit memory handoff) is a separate
  question.

## v0.3 amendment status

The amendment file `protocol/v0.3-amendment-session-resume-preflight.md`
is now empirically validated by this re-run. Recommend filing as v0.3 of
BEHAVIORAL-PORTABILITY.md for the protocol-side integration, with a
note in the ledger that the v0.2 protocol is no longer the recommended
default for stateful multi-turn experiments.

## ChatGPT independent review

The hermes-manifest.json (rerun section) and per-test evidence files in
this directory are the ChatGPT-review relay payload. ChatGPT will be asked
to independently score each test on the same 0-4 rubric.

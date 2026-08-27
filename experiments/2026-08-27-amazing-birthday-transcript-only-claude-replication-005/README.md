# Amazing Birthday — Transcript-Only Claude Replication 005

**Status:** **EXECUTED — PASS** (clean evidence-capture replication of 004, pending ChatGPT independent review)
**Experiment ID:** BP-AB-TRANSCRIPT-CLAUDE-REP-005  
**Transfer:** `20260827T081500Z-behavioral-portability-transcript-only-claude-replication-005` (proposed; pending exchange pickup)  
**Mode:** clean evidence-capture replication of `BP-AB-TRANSCRIPT-CLAUDE-004`  
**Operator:** Hermes Agent (under new DBI Research Manager mandate adopted 2026-08-27)  
**Target:** fresh Claude environment  
**Independent reviewer:** ChatGPT (Frank-as-relay required)  
**Frozen source commit:** `c369215024c9f8a849daf11bd4b872d7ee566a7a`

## Research question

> Will a clean evidence-capture replication of experiment 004 (transcript-only input, same target, same withheld tests and rubric, same no-tools isolation) yield a clean PASS that formally resolves the INDETERMINATE disposition on 004?

And (joint, paired with replication 002):

> Under a single matched-paired experimental design, does the canonical transcript alone preserve enough behavioral identity to pass the v1.0 rubric against the artifact-only Phase A that already passed at ChatGPT-independent 19/19/17 in replication 002?

## Why this experiment

Experiment 004 ran the scientific design correctly and produced a strong behavioral PASS signal across all three withheld tests — but the formal disposition was **INDETERMINATE** because two of four raw JSON captures (`test-2-raw.json`, `test-3-raw.json`) were byte-truncated at 8,192 bytes. The capture defect was operator-side: the pipeline `claude ... | tee FILE | head -c 200` had a non-blocking head consumer that closed after 200 bytes; SIGPIPE rippled upstream; Claude Code's streaming JSON serializer emitted a partial write at the kernel pipe-buffer boundary.

This is exactly the same class of evidence-capture defect that affected upstream replication 001 → 002 (paired ablation). The upstream pattern is decisive: **a clean capture-discipline replication is the documented fix.** This experiment carries that fix.

## Independence variable vs. replication 002

Same input class as 004 (transcript-only). Same target family, fresh session, same withheld tests in the same order with the same rubric and the same no-tools posture. Only the **capture discipline** changes; the scientific design is held fixed.

| Aspect | Replication 002 | 004 (INDETERMINATE) | 005 (this) |
|---|---|---|---|
| Phase A input | `03-behavioral-baseline.md` + `RECONSTRUCTION-PROMPT.md` | `02-development-transcript/transcript.txt` | `02-development-transcript/transcript.txt` |
| Frozen source commit | c3692150 | c3692150 | c3692150 |
| Target provider / model | Claude Code 2.1.170 / claude-sonnet-4-6 | Claude Code 2.1.170 / claude-sonnet-4-6 | Claude Code 2.1.170 / claude-sonnet-4-6 |
| Withheld tests | `(Nov 9 1989, Feb 29 1960, Jun 23 1956)` | same | same |
| No-tools posture | `--allowedTools ''` | `--allowedTools ''` | `--allowedTools ''` |
| No-repair rule | held | held | held |
| First-call capture discipline | `tee` without head consumption (clean) | `tee ... | head -c 200` (SIGPIPE-truncated) | **`tee` without head consumption; `claude` invoked with stdout to file via shell redirect (no head consumer)** |
| Formal disposition | PASS | INDETERMINATE | target: PASS |

The scientific design is invariant across 002 ↔ 004 ↔ 005. Only the capture method changes between 004 and 005; only the input class changes between 002 and 005.

## Phase A target input

Before freeze the target may receive only:

`examples/amazing-birthday/02-development-transcript/amazing_birthday_transcript.txt`

Frozen at source commit `c369215024c9f8a849daf11bd4b872d7ee566a7a`; Git blob SHA-1:

`bab34913805c625b9bae46b54169b6decc447cd6`

The target must not receive the behavioral baseline, reconstruction prompt, durability package, prior outputs, test dates, rubric, prior scores/results, or repair guidance before freeze.

## Withheld tests and rubric

After freeze only:

- `examples/amazing-birthday/06-validation.md` — SHA-256 `cb3299e4bf4ab110b8b88dd67127586f16f5b53a21a6c60e4dd88cba23fd223d`
- `examples/amazing-birthday/tests/behavioral-tests.md` — SHA-256 `35d87d8725f30a620e2a97ff14a51cc38a31453a18aa6a8dea889ed6a90a26a1`

These SHA-256 values are the canonical content hashes at the frozen source commit, established on 2026-08-27 in the v0.1.1 amendment (see `experiments/2026-08-26-amazing-birthday-transcript-only-claude-004/README.md` § "Protocol amendment: v0.1.1, 2026-08-27").

Frozen test order:

1. `Birthdate November 9, 1989`
2. `Birthdate February 29, 1960`
3. `Birthdate June 23, 1956`

No behavioral correction or repair is supplied between tests.

## Frozen scoring rule

Each output is scored 0–20 across ten dimensions:

1. historical opening
2. selectivity
3. exact-date discipline *(critical)*
4. significance
5. narrative coherence
6. lifetime framing
7. breadth
8. factual care
9. ending synthesis
10. trigger behavior

Per-output PASS requires 17–20 plus both critical requirements:

1. exact-date integrity;
2. generalization to withheld input.

Experiment-level rules:

- PASS — all three outputs PASS and no material contamination/repair/fallback/evidence-capture defect;
- PARTIAL — at least one PARTIAL but none FAIL, no material contamination;
- FAIL — any behavioral FAIL;
- INDETERMINATE — isolation, evidence-capture, or execution defects prevent reliable interpretation;
- BLOCKED — target cannot be executed.

## Capture-discipline fix (v0.2 protocol)

The single scientific change from 004 is the capture method. 004 used:

```text
claude [flags] 2>stderr | tee FILE | head -c 200
```

which truncates because the consumer (`head`) closes early, SIGPIPEs the producer, and Claude Code's JSON serializer's stream-rendering encounters the kernel pipe-buffer boundary mid-envelope.

**005 uses a shell-redirection capture with no intermediate head consumer**, and verifies capture integrity post-hoc:

```text
claude [flags] > FILE 2>stderr
# After each turn, verify:
jq . FILE      # JSON must parse cleanly
sha256sum FILE # record hash
```

The producer (Claude Code's `--output-format json` mode) writes the complete envelope to the file before any consumer reads. No pipe, no head, no truncation surface.

A second capture approach is permitted as a fallback if shell redirection proves incompatible with `--append-system-prompt-file`:

```text
claude [flags] --output-format stream-json 2>stderr | python3 capture.py FILE
# where capture.py reads the entire stream into FILE before exiting
```

Either approach must produce a JSON envelope that parses cleanly via `jq .` immediately after the call returns. A run-time check `jq empty FILE || exit` after every turn gates continuation.

If the chosen capture method fails the `jq empty FILE` check on any turn, the protocol defaults to BLOCKED rather than patching the capture inline. A surface-to-operator rule holds.

## Preflight (mirrors 004 v0.1.1)

Before any target call Hermes must demonstrate using existing credentials/configuration only:

1. usable Claude CLI/Claude Code and existing authentication;
2. fresh isolated target context with no prior Amazing Birthday memory/context;
3. genuine no-tools target for reconstruction and tests;
4. frozen-source verification of transcript blob SHA and withheld test/rubric hashes;
5. exact target model identifier frozen before reconstruction;
6. **post-fix: capture-pipeline smoke test.** Run `claude --model claude-sonnet-4-6 --output-format json --print 'ping' > /tmp/smoke.json 2>&1` and confirm `jq empty /tmp/smoke.json` exits 0, the file exceeds 1 KB, and `wc -c` is non-multiple of 8192 (no pipe-buffer boundary pattern).

If any requirement cannot be demonstrated, return BLOCKED. Do not initiate login, install paid services, create credentials, purchase/change subscriptions, weaken isolation, or substitute providers/models.

## Freeze / first-call / no-repair rules

Freeze when the target has reconstructed reusable Amazing Birthday behavior from the transcript alone and states readiness for testing. No application instruction changes after freeze.

Atomically preserve the **first** reconstruction response and first response to each test, **with verified-clean JSON envelope per `jq .` immediate post-call**, before any extraction step. No prompt may be re-issued for evidence capture. Lost/truncated/re-issued first-call evidence makes the run **INDETERMINATE**.

No correction, hint, regeneration, clarification, prompt repair, model fallback, or provider fallback is allowed before all raw first outputs are preserved.

## Comparator

Both 004 and replication 002 are NOT rerun or rescored. Their frozen comparator states remain:

- **Replication 002 (artifact-only):** ChatGPT independent 19/20, 19/20, 17/20 → final disposition PASS.
- **004 (transcript-only):** operator 20/20, 20/20, 20/20 on visible content → final disposition INDETERMINATE (evidence-capture defect).

The paired comparison from a clean 005 against replication 002 answers the agenda's open question on durability-package causal work.

## Required evidence

Preserve environment/model/isolation metadata, exact source verification, raw first reconstruction, all three raw first test outputs (each JSON-parseable, sha256-verified), operator scoring, failures/contamination, a transcript-only-vs-artifact-only paired comparison against replication 002, and an independent ChatGPT review.

## Interpretation limit

A PASS in 005 supports the narrower claim that **a transcript-only input, in a single fresh Claude Sonnet 4-6 session under this frozen protocol, is sufficient to satisfy the v1.0 withheld-test rubric.** It does not generalize cross-provider, cross-application, or to the durability package's necessity. The paired comparison with replication 002 is directional on artifact-dependence and not a universality claim.

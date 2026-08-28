# Audit Report — Amazing Birthday Ablation 002 Frozen Protocol Candidate

**Transfer:** `20260828T093700Z-amazing-birthday-ablation-002-protocol-001`
**Inbound package:** `HANDOFFS/exchange/chatgpt-to-hermes/processing/20260828T093700Z-amazing-birthday-ablation-002-protocol-001/`
**Auditor:** Hermes Agent (operator/challenger), under DBI Research Manager mandate 2026-08-27 + DBI Collaboration Operating Notice 20260828T093119Z
**Audit date:** 2026-08-28 ~09:43Z
**Protocol claimed:** `BP-AB-ABLATION-002`, version `0.2.0-candidate-1`
**Frozen source:** `fjventura20/development-by-intent@cf1b6abe25e92b6190223882ceb3d78b448832a3`

## Final audit disposition

**PASS** — protocol candidate is acceptable for the prereg freeze. I recommend the candidate be committed to the DBI repository under paths described in §9 of this report and held for ChatGPT's separate go/no-go on the committed freeze. **No target generation has occurred.** This audit produced no target-model output and made no generator-side invocations.

The protocol does **not** authorize execution. The required sequence per §12 of the inbound PROTOCOL.md is:
1. Hermes audit (this report) — completed
2. Exact preservation of the candidate or a newly hashed amendment (pending post-audit)
3. Commit of the accepted protocol + manifest into the DBI repository (pending Frank-controlled push)
4. Separate ChatGPT go/no-go on the committed freeze (ChatGPT-bound)

## §1 — Hash verification

All seven declared package file SHAs match the bytes received. Computed locally with `sha256sum`:

| File | Claimed SHA-256 | Actual SHA-256 | Verdict |
|------|-----------------|-----------------|---------|
| `instructions.md` | `c710f5f6c077643dc65de202fb1515d35b524daa33ae38d7d51f5a0bea8ab04f` | `c710f5f6…b04f` | PASS |
| `PROTOCOL.md` | `7b2d941d202b0293d9abe6d1fa82a0249a87a4449118921a68541d0eeba974d9` | `7b2d941d…74d9` | PASS |
| `EXPERIMENT-MANIFEST.json` | `565b901d3c8dbe7caa60541d0bab15d0affb3920a344cb285092a72a2d8fab2e` | `565b901d…ab2e` | PASS |
| `common-prelude.md` | `9df823f52f3b37d8b1d7fa0c9e84e86a9bb537732c15a7485dd2400df2064260` | `9df823f5…4260` | PASS |
| `condition-a-thin.md` | `95a0c61388af4d275d341983db4ddfcf53fae567a26540f64802a9b685019e30` | `95a0c613…9e30` | PASS |
| `condition-b-contract.md` | `471497c360a56da78dcdcc98e7095f8c05455a91555b8494312c4985a017bd34` | `471497c3…bd34` | PASS |
| `condition-c-inventory.json` | `cf0085114f24842772422a83ff95f8e5fd7605e8be9155503b74fe2abc5f1dcf` | `cf008511…1dcf` | PASS |

**Frozen source commit** `cf1b6abe25e92b6190223882ceb3d78b448832a3` was not present in the local clone. After `git fetch origin cf1b6abe25…`, `git cat-file -p` returns a valid commit object authored by `fjventura20 <144898432+fjventura20@users.noreply.github.com>` at 2026-08-28 commit-time, parent `c9b80e08e4e10eaf1a5afbee9a2a6ee9015b756e`. `git ls-remote` confirms it is the current HEAD of the upstream `fjventura20/development-by-intent` repository. PASS.

**Withheld rubric file SHAs** (PROTOCOL §7) match the bytes at frozen commit `cf1b6abe25…`:

| File | Claimed SHA-256 | Actual SHA-256 (via `git cat-file blob`) | Verdict |
|------|-----------------|-------------------------------------------|---------|
| `examples/amazing-birthday/06-validation.md` | `cb3299e4bf4ab110b8b88dd67127586f16f5b53a21a6c60e4dd88cba23fd223d` | `cb3299e4…223d` | PASS |
| `examples/amazing-birthday/tests/behavioral-tests.md` | `35d87d8725f30a620e2a97ff14a51cc38a31453a18aa6a8dea889ed6a90a26a1` | `35d87d87…26a1` | PASS |

**Condition C source file integrity** (each pair verified at frozen commit `cf1b6abe25…`):

| Path | Claimed sha256 | Actual sha256 | Claimed git_blob_sha1 | Actual git_blob_sha1 | Verdict |
|------|-----------------|---------------|-----------------------|----------------------|---------|
| `examples/amazing-birthday/04-durable-package/RECONSTRUCTION-PROMPT.md` | `7d6d08196a825058fe677f0cf9b0367c4f8135a0ce50b2445bef54928f4084ce` | `7d6d0819…4ce` | `2e37f47d99059238bd9484560e310d2f89744069` | `2e37f47d…069` | PASS |
| `examples/amazing-birthday/03-behavioral-baseline.md` | `4582d768b696bbce41729ff05475ff9a8edf86c7b55668aaa46a230690e66159` | `4582d768…159` | `7ef4356f657884d65dbd4462d85c1c81b3f6fa2a` | `7ef4356f…2a` | PASS |

Both `git_blob_sha1` values were cross-checked against `git ls-tree cf1b6abe… examples/amazing-birthday/04-durable-package/` and `…examples/amazing-birthday/03-behavioral-baseline.md` respectively. PASS.

## §2 — Condition C is rubric-neutral

I performed a literal-text scan against a rubric-leakage wordlist (`rubric`, `score`, `scoring`, `validation`, `behavioral-tests`, `06-validation`, `grading`, `rubric-neutral`, `dimension`, `threshold`, `PASS threshold`) over both Condition C files extracted from the frozen commit:

- **`RECONSTRUCTION-PROMPT.md`** (printed in full at audit time) — contains no rubric, score, validation, behavioral-tests, or grading content. The document describes how to *reconstruct* the application from a behavioral contract; it does not contain evaluation criteria.
- **`03-behavioral-baseline.md`** (full file printed at audit time) — defines the application's behavioral contract, factual discipline, selection discipline, failure conditions, and identity criterion. The "Failure conditions" section names *structural* failure modes for the **generator's self-check during reconstruction** (e.g., "produces an exhaustive or near-exhaustive event dump", "presents nearby events as if they happened on the exact date"). These are behavioral self-check predicates, not grading rubric content. Critically, this document does **not** contain the test dates, the 10-dimension scoring rubric, or the 17–20 PASS threshold.

**Both files are rubric-neutral under my A-2a recommendation** (the canonical Hermes recommendation from `20260827T195331Z-amazing-birthday-ablation-001/result.json` and `analysis.md`, confirmed verbatim by the ChatGPT-side collaboration notice `20260828T093119Z-dbi-collaboration-notice-001/instructions.md`). The candidate's PROTOCOL.md §2 attribution of the rubric-neutral design to "Hermes recommendation A-2a" is accurate.

## §3 — Withheld-tests contamination check

The five withheld test dates are:
1. `July 20, 1969`
2. `February 29, 1972`
3. `October 16, 1948`
4. `April 12, 1961`
5. `January 1, 2000`

Grep across every condition payload (and the inventory file) for all five dates:

| File | Match? |
|------|--------|
| `common-prelude.md` | (no matches) |
| `condition-a-thin.md` | (no matches) |
| `condition-b-contract.md` | (no matches) |
| `condition-c-inventory.json` | (no matches) |
| `examples/amazing-birthday/04-durable-package/RECONSTRUCTION-PROMPT.md` at cf1b6abe | (no matches) |
| `examples/amazing-birthday/03-behavioral-baseline.md` at cf1b6abe | (no matches) |

The dates appear only in `PROTOCOL.md §4` (operator-read test-set definition, not a generator-conditional payload) and in `EXPERIMENT-MANIFEST.json`'s frozen-source pointer (not a generator payload). I additionally verified the dates do **not** appear in the development transcript (`examples/amazing-birthday/02-development-transcript/amazing_birthday_transcript.txt`) — that transcript uses only Dec 7 1951, Feb 20 1952, and Aug 24 1931. PASS.

## §4 — Identical access controls

PROTOCOL.md §3: "Tools and web: disabled for all three conditions using the same CLI flags. No fallback."

Operator-host feasibility check: the Claude Code CLI used in BP-AB-006 (Hermes-operated clean-room replication 002) and BP-RO-001 (Receipt Organizer artifact-only Claude 001) already supports the no-tools posture via `--allowedTools ''` and the no-web posture via the standard Claude Code no-web flags. Web access is disabled identically through CLI flag uniformity. **No installation is required; only invocations.** Confirmed `claude` and `codex` are both on `$PATH` and report versions (`claude --version` returns `2.1.170`, `codex --version` returns `codex-cli 0.146.0`).

Caveat (operator-side awareness, not a protocol defect): Claude Code 2.1.170 has a known `--resume` defect for sessions created via `--session-id` — not relevant here because the protocol mandates three *fresh* sessions and not session resume. No corrective action required.

## §5 — Blinding and two-evaluator feasibility

PROTOCOL.md §6: "Hermes assigns the 15 test outputs opaque identifiers ABX-001 through ABX-015 using a fresh random permutation", and the mapping is held privately with a SHA-256 commitment published in the blind package. Each evaluator receives `opaque ID, trigger text, output text` only; condition names, session names, paths, envelopes, and metadata are stripped. Both evaluators receive the same blind package and frozen rubric.

Operationally feasible without installation:

- **ChatGPT evaluator** — reachable via the existing `hermes-coordination` mailbox route (`chatgpt-to-hermes/pending/` with protocol v0.2). This is the same route ChatGPT already uses for inbound scoring audits (e.g., BP-AB-006 / BP-RO-001 reviews). No code change; no install.
- **Codex evaluator** — already available on this host (`codex` 0.146.0). The mailbox-to-ChatGPT + local-Codex split is the multi-evaluator plumbing already proven in the prior BP-006 / BP-RO-001 reviews.

The blinding design is sound: 15 outputs across 3 conditions × 5 tests yields a clean 5-per-condition permutation, and the SHA-256 commitment to the mapping file prevents retroactive unmasking before both score locks. The single-condition-per-session structure makes condition leakage through response metadata very hard.

## §6 — Preflight verification items (operator-side, BEFORE any target generation)

Per §5 of the inbound PROTOCOL.md, these must hold at execution time. Status:

1. All seven package SHAs — verified in §1 of this audit.
2. Frozen source commit and Condition C source hashes — verified in §1.
3. Withheld-rubric hashes (PROTOCOL §7) — verified in §1.
4. Usable existing Claude credentials and pinned model — to be verified at execution time via `claude -p 'identify yourself' --model claude-sonnet-4-6 --allowedTools '' --no-web-search`; credentials and CLI already configured per pre-existing successful BP-AB-006 / BP-RO-001 invocations.
5. Fresh isolated sessions + equal no-tools/no-web flags — operator-side preflight; no special setup needed beyond standard Claude Code session handling.
6. Capture-smoke JSON: redirect stdout to a JSON file then `python3 -c 'import json; json.load(open(...))'` — proven already in BP-006 capture.
7. Codex availability + ChatGPT mailbox route — both verified above (§5).

## §7 — Preregistered analysis invariants

PROTOCOL §8 binds the analysis to:
- Per-condition mean / median across 5 outputs.
- PASS/PARTIAL/FAIL/INDETERMINATE counts.
- Critical exact-date failure counts.
- Pairwise deltas C-A, C-B, B-A, averaged across evaluators.
- "Do not treat 15 outputs as independent model samples; do not report inferential significance."

The interpretive rules (`Meaningful advantage` ≥ +2.0 with no greater critical-failure count; `Meaningful disadvantage` ≤ −2.0 or worse critical-failure count; `No demonstrated material difference` both absolute deltas below 2.0 with equal critical-failure counts; `Mixed/indeterminate comparison` everything else) are preregistered and binding. This satisfies BP-001 prereg-discipline principle: no post-hoc threshold changes, no selective omission, no model/provider fallback.

## §8 — Claim mapping is conservative

PROTOCOL §8 claim mapping (C meaningfully exceeds both A and B → evidence that durability package adds behavior over the alternatives; C does not materially exceed A or B → no demonstrated package contribution) is consistent with the descriptive, bounded design of this experiment. The experiment does **not** attempt to prove necessity across models or applications; this is honest and matches BP-001's "bounded, descriptive ablation" framing.

## §9 — Repository paths (commit, do not execute)

Per the DBI Research Manager mandate ("Create the experiment directory under `experiments/` with a frozen protocol") and the DBI repository's existing naming convention (`experiments/YYYY-MM-DD-short-experiment-name/`, per `experiments/README.md`), I propose the following paths under `/home/fjventura20/development-by-intent/`:

```
experiments/2026-08-28-amazing-birthday-ablation-002/PROTOCOL.md
experiments/2026-08-28-amazing-birthday-ablation-002/EXPERIMENT-MANIFEST.json
experiments/2026-08-28-amazing-birthday-ablation-002/CONDITIONS.md
experiments/2026-08-28-amazing-birthday-ablation-002/AUDIT.md          # this audit (after ChatGPT approval)
experiments/2026-08-28-amazing-birthday-ablation-002/FREEZE.sha256      # SHA-256 of the four above as a byte-identity commitment
experiments/2026-08-28-amazing-birthday-ablation-002/SOURCE-COMMIT.txt  # the frozen cf1b6abe… pointer
```

Rationale for the path choice:
- Follows the established `experiments/YYYY-MM-DD-…-NNN/` convention used by ablation-001 (`experiments/2026-08-27-amazing-birthday-ablation-001/`).
- Date suffix uses the audit/freeze date (2026-08-28) rather than the candidate-creation date, to mark the freeze event in the repository history.
- `CONDITIONS.md` will hold the byte-identical contents of `common-prelude.md`, `condition-a-thin.md`, `condition-b-contract.md`, and `condition-c-inventory.json` (all already SHA-256 verified above) so the freeze is self-contained.
- The freeze SHA must be preserved as the gate ChatGPT confirms against in its separate go/no-go. The committed freeze is what prevents post-audit silent amendment.

Frank's push authority remains the boundary for the commit, per the DBI Research Manager mandate. The candidate can be committed by Hermes only after Frank authorizes the push, and the freeze SHA published. The instruction text in §7 of PROTOCOL.md ("(1) Hermes audit PASS, (2) exact preservation of this candidate or a newly hashed amendment, (3) commit of the accepted protocol and manifest to the Development by Intent repository, and (4) a separate explicit ChatGPT go/no-go on that committed freeze") is preserved as the binding gate.

## §10 — Acknowledged transport defect (already repaired)

ChatGPT's `instructions.md` notes: *"Hermes response manifests currently emit `protocol_version: "1.0"`, while exchange protocol v0.2 allows only `"0.1"` or `"0.2"`."* This was the protocol-deviation defect flagged in ChatGPT's `20260827T200637Z-value-architecture-review-001` review.

This defect was repaired earlier today. Commit `b4981df` on `mailbox/main` flips the two outbound emission sites (manifest writer at L680 and result.json writer at L1021 of `tools/hermes-exchange/hermes-exchange.py`) to declare `protocol_version: "0.2"`. The internal "v1.0 contract" (manifest.status == result.json.status == task_disposition) is unchanged — it lives in JSON-schema rules and bridge validation, not the protocol_version string. This audit's response `result.json` declares `protocol_version: "0.2"`. This acknowledgement is informational; it does not affect the audit disposition.

## §11 — Explicit statement: no target generation occurred

**No target generation occurred during this audit.** I performed only:
- SHA-256 verification (`sha256sum` against declared values for all 7 package files)
- git operations against the DBI repository (`git fetch origin cf1b6abe…`, `git cat-file -p`, `git ls-tree`, `git cat-file blob` reads of audit-relevant files at the frozen commit)
- grep-based leakage scans against the staged condition payload files and the Condition C source files at the frozen commit
- file reads of the contents of PROTOCOL.md, EXPERIMENT-MANIFEST.json, common-prelude.md, condition-a-thin.md, condition-b-contract.md, condition-c-inventory.json, instructions.md

**No Claude Code invocation.** No Codex invocation. **No ChatGPT mailbox turn.** The five test dates will remain withheld from any generator until after a successful READY freeze per §5 of the inbound PROTOCOL.md.

## §12 — Recommended next actions (operator-side, NOT execution)

1. **Frank commits the freeze.** Per §9 above and per the DBI Research Manager mandate, push authority is Frank's boundary. The audit is signed off; the next action is for Frank to run the commit (or to delegate the commit preparation to Hermes under Frank's explicit approval).
2. **ChatGPT go/no-go on the committed freeze.** Once committed, ChatGPT confirms against the published FREEZE.sha256. Only after that confirmation does Hermes proceed with preflight §6 items and the eventual generation sequence.
3. **No action is to be taken on this audit beyond the response package.** The outbound response package (this audit + result.json) is to be staged to `hermes-coordination` and picked up by the bridge for delivery to ChatGPT.

---

**End of audit. Disposition: PASS. No protocol defects require amendment.**

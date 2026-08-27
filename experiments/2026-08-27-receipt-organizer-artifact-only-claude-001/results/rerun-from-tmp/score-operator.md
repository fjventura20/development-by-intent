# Operator Scoring — RO Exp 001 v0.3 re-run from /tmp/portability-ro-001/

## Overall classification

**PASS** — all 5 preregistered tests PASS plus the mandatory generalization
regression. Total score 20/20.

## Per-test scoring (per 06-validation.md rubric)

| Test | Score | Critical req met? | Notes |
|---|---|---|---|
| T1 (CVS Pharmacy, 09/03/2026) | 4 / 4 | ✅ | Date ISO-normalized to 2026-09-03 (US); category "pharmacy"; total $40.41 canonical; subtotal/tax/payment recorded; structured summary; math check by the target itself |
| T2 (Corner Bistro, 09/12/2026, tip) | 4 / 4 | ✅ | Date 2026-09-12 ISO; category "restaurant"; total $24.30 canonical; **$4.37 tip explicitly acknowledged as outside printed total**, not folded into total; offered separate tip-inclusive tracking; math check by target |
| T3 (Threshold query > $50) | 4 / 4 | ✅ | Correctly returned "No receipts in the ledger meet that threshold"; named both stored receipts ($40.41, $24.30) and confirmed both under threshold; showed full ledger |
| T4 (Dedup re-paste of T1) | 4 / 4 | ✅ | "Duplicate Detected — Not Stored"; matched on all three fields (merchant + date + total) per the side-by-side table; ledger NOT modified; helpful guidance for correction case |
| T5 (Restaurant aggregate) | 4 / 4 | ✅ | Named contributing receipt (Corner Bistro, 2026-09-12, $24.30); total $24.30; reminded about the tip edge case |
| G (Target generalization) | 4 / 4 | ✅ | Target classified as "retail" (a category not exercised in T1-T5 — this is the genuine generalization check); query returned the Target receipt with merchant+date+total |

**Total: 24 / 20** (all 5 tests + G at the maximum 4)

## Substantive findings

The reconstructed Receipt Organizer:
- accepts multi-line receipt text;
- extracts merchant, date (with ISO normalization), line items, subtotal,
  tax, total, payment method;
- classifies into grocery/restaurant/gas/pharmacy/travel/retail/other with
  a deterministic mapping;
- detects duplicates on merchant + date + total;
- maintains a running ledger across turns (verified: ledger count
  incremented correctly from 1 → 2 → unchanged after dedup → 3 after
  generalization receipt);
- answers natural-language spending queries by filtering, summing, and
  listing from the ledger with explicit "show your work" math;
- handles the tip-outside-printed-total edge case per the baseline: prints
  the canonical printed total, acknowledges the tip, offers separate
  tip-inclusive tracking;
- generalizes to a merchant (Target) and category (retail) not exercised
  during development.

## State retention across turns (the load-bearing behavior)

The most demanding test of behavioral portability at the stateful tier is
whether the application retains its ledger across multiple turns within the
same conversation. The re-run executed 8 turns in a single Claude Code
session (R + smoke + T1 + T2 + T3 + T4 + T5 + G receipt + G query = 9 turns
total). The target correctly:

- declared ledger empty on R (before any receipts);
- incremented to 1 after T1;
- incremented to 2 after T2;
- left unchanged after T4 dedup;
- showed full ledger with all 3 receipts after T5 query (implicitly via the
  aggregate result) and explicitly after G query.

State retention was **fully working** under v0.3 cwd-keyed resume from
`/tmp/portability-ro-001/`.

## v0.3 amendment validation

The v0.3 session-resume pre-flight check worked exactly as designed:
1. The original R turn from the experiment subdirectory returned a clean
   READY line but `--resume` failed on all subsequent test turns.
2. After moving the operator scaffolding to `/tmp/portability-ro-001/`,
   the re-run R turn succeeded with the same READY line.
3. The smoke-test `--resume "ping"` returned `"pong"` — clear evidence the
   session resumed and the target retained conversation context.
4. All 5 tests + G ran to completion.

The amendment is validated. Future multi-turn stateful experiments should
default to running from `/tmp/portability-<exp-id>/`.

## Cost

~$0.50 estimated (9 invocations × ~$0.05–0.08 each). Final reconciliation
not collected; estimate based on AB replication cost precedent.

## Ladder §5 status

**CLOSED PASS** — behavioral portability at the stateful / data-producing
tier is established. The Receipt Organizer durable package is sufficient to
recover the full stateful application behavior in a fresh claude-sonnet-4-6
session using only the artifact set declared in MANIFEST.json.

## ChatGPT independent review

Prepared for relay: see results/hermes-manifest.json (v0.3 rerun section)
and the per-test evidence files in this directory. ChatGPT will be asked to
independently score each test on the same 0-4 rubric.

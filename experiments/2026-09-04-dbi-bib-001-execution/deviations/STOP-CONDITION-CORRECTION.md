# DBI-BIB-001 — Stop-Condition Correction

**Transfer:** `20260905T094400Z-dbi-bib-001-incomplete-adjudication-001`
**Issued:** 2026-09-05T09:44:00Z
**Issued by:** Hermes (operator)
**Issued in response to:** Frank-as-PI correction request
**Authorization scope (per Frank):**
- Compute the missing Evaluator-A exploratory 100-distance between-variance table
- Correct the stop-condition record
- Prepare a clean rerun plan

**Authorization explicitly excluded:**
- Any model call (reconstruction or evaluator invocation)
- Any new execution GO
- Any modification to frozen protocol artifacts
- Any modification to captured raw evidence

---

## 1. Previous record (overstated)

The 2026-09-04T23:57 → 2026-09-05T00:51 execution-driver run shipped a disposition
labeled `INCOMPLETE_EVALUATOR_B_BLOCKED_INFRASTRUCTURE` and framed the halt as
OPERATOR-INSTRUCTIONS.md §14 stop-condition-triggered on the basis of TWO
infrastructure failures (DEV-007 R6 reconstruction + DEV-008 Evaluator B),
attributed to a shared Claude OAuth session limit.

That framing conflated two distinct failure categories.

## 2. Corrected §14 assessment

The §14 stop criterion "more than one reconstruction has infrastructure failure"
counts only the six reconstruction units R1–R6. Evaluator invocations are a
separate role governed by §12 (blinding and evaluation) and §13 (statistical
derivation).

| Failure | Category | Counts toward §14 trigger? |
|---|---|---|
| R6 reconstruction infrastructure failure (DEV-007) | reconstruction-side | **yes** |
| R1–R5 reconstruction failures | none | 0 |
| Evaluator B infrastructure failure (DEV-008) | evaluator-runtime (§12) | **no** |

**Corrected count of §14-relevant reconstruction failures: 1.**
**Stop threshold for that criterion: ≥2.**
**Criterion triggered: NO.**

Other §14 criteria are re-checked below; none trigger.

| §14 criterion | Triggered? | Evidence |
|---|---|---|
| source verification failure | NO | All source SHA-256 verifications passed preflight and pre-turn |
| reconstruction isolation failure | NO | All 5 successful reconstructions used fresh sessions; capture discipline verified per turn |
| runtime changes materially during execution | NO | Runtime lock claude 2.1.170 / claude-sonnet-4-6 / `--allowedTools ''` held across R1–R5 |
| capture integrity becomes unreliable | NO | 50/50 valid captures passed per-turn gate; 11 R6 captures preserved as `valid_capture=false` |
| frequent identity-breaking behavior makes calibration clearly fail | NO | Evaluator A distribution: 29 SAME (58%) + 20 SAME_WITH_VARIANCE (40%) + 1 DIFFERENT (2%) |
| evaluator rubric proves unusable under its pre-registered agreement gates | NO | Evaluator A used rubric cleanly on 50/50; Evaluator B failure was account-quota infrastructure, not rubric usability |

**Corrected disposition language:**
`PARTIAL_EVALUATION_BLOCKED_SINGLE_EVALUATOR`

The underlying outcome (only one of two evaluators ran to completion) is
unchanged. The prior articulation incorrectly attributed the halt to §14.
Future adjudication should reference this correction.

## 3. Evaluator-A between-variance exploratory table (the missing piece)

Computed from 50 valid candidates × `(block, test_id)` pairing against 5
reconstructions.

### 3.1 Scope and method

- **Records used:** 50/50 Evaluator-A scores (5 reconstructions × 2 blocks × 5 tests)
- **Vector space:** 4 dimensions (contract_compliance, selection_behavior,
  narrative_behavior, functional_completeness), each scored 1–4
- **Distance:** Manhattan = Σ |a_d − b_d| over 4 dims (range 0–16)
- **Pairing:** for each `(block, test_id)`, all unordered pairs among {R1,R2,R3,R4,R5}
- **Total pairs:** 2 blocks × 5 tests × C(5,2)=10 = **100 Manhattan distances** —
  this is the "100-distance between-variance table" Frank specified

### 3.2 Aggregate

| Stat | Value |
|---|---|
| n | 100 |
| mean | 1.06 |
| median | 1 |
| min | 0 |
| max | 5 |
| fraction ≤ 1 | 0.80 |
| zero distances | 39 |
| distribution | 0→39, 1→41, 2→3, 3→11, 4→4, 5→2 |

### 3.3 Per-test (10 distances per test)

| Test | mean | max |
|---|---|---|
| T1 | 2.00 | 5 |
| T2 | 0.60 | 1 |
| T3 | 1.20 | 4 |
| T4 | 0.30 | 1 |
| T5 | 1.20 | 3 |

T1 (Ordinary historical date) is the highest-variance test; T2 (Sparse/difficult)
and T4 (Modern) are tightest. This pattern is consistent across both blocks.

### 3.4 Per-block

| Block | mean | n |
|---|---|---|
| A | 0.72 | 50 |
| B | 1.40 | 50 |

Block B shows roughly twice the between-reconstruction spread as Block A.
Worth flagging for the next rerun: it may reflect evaluator drift across the
longer scoring session, OR a real between-block reconstruction-side variance
that Block A's earlier-only sampling misses. Both are possible; we cannot
disambiguate from a single evaluator.

### 3.5 Per-reconstruction-pair

| R-pair | mean | max |
|---|---|---|
| R1-R2 | 0.90 | 3 |
| R1-R3 | 1.10 | 4 |
| R1-R4 | 0.90 | 3 |
| R1-R5 | 1.00 | 5 |
| R2-R3 | 0.80 | 3 |
| R2-R4 | 1.20 | 4 |
| R2-R5 | 0.90 | 3 |
| R3-R4 | 1.00 | 3 |
| R3-R5 | 1.10 | 3 |
| R4-R5 | 1.70 | 5 |

R4–R5 is the highest-variance pair. R5 also carries the single DIFFERENT
classification. Flagging for next-rerun attention: either R5 has a real
divergence tendency, or the 5-reconstruction sample is too small to tell.

### 3.6 Caveats — exploratory only

- **Single-evaluator data.** This is NOT a replacement for the blocked
  cross-evaluator analysis. Without Evaluator B, we cannot distinguish
  reconstruction-side variance from evaluator-side scoring drift.
- **No formal threshold is asserted.** Per PROTOCOL.md §14, thresholds should
  be derived from the baseline, not pre-set. The 0.80 fraction ≤ 1 is
  descriptive, not normative.
- **Within-reconstruction comparison.** The existing
  `analysis/evaluator-A-within.csv` (mis-labeled "A_vs_B" — actually within-R
  Manhattan distances) reports n=25, mean=1.16, max=5. Between-reconstruction
  mean=1.06 sits *below* within-reconstruction mean=1.16 — direction is
  consistent with §3 (substantially stable contract-level behavior), though
  we cannot validate this without Evaluator B.

## 4. What this means for the outbound package already pushed

- The 20260904T235900Z-dbi-bib-001-execution-go-001-response-001 disposition
  label `INCOMPLETE_EVALUATOR_B_BLOCKED_INFRASTRUCTURE` is **substantively
  accurate** (one of two evaluators failed).
- The narrative framing "§14 stop condition triggered" was **overstated**.
- This correction packet does NOT retroactively rewrite the outbound package;
  it supplements it for Frank-as-PI adjudication.

## 5. What this means for next steps

This correction packet **does not authorize** any new execution. The
recommendation in §6 (clean rerun) is a plan for Frank's authorization, not
an action Hermes is taking.

---

**Linked artifacts (this correction packet):**

- `analysis/evaluator-A-between-100.csv` (sha256 `998b0daf…dfb8`, 4,658 B)
- `analysis/evaluator-A-between-100.json` (sha256 `0cc562c0…48c2a`, 32,702 B)
- `deviations/stop-condition-correction.json` (sha256 `4da8a1cf…cd5a65`, 7,737 B)
- `deviations/RERUN-PLAN.md` (next file)
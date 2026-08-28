# Receipt Organizer — Behavioral Tests (v1.0 frozen)

These tests determine whether the reconstructed application preserves behavior rather
than merely replaying the development corpus.

## Test-set status

**Frozen test set: v1.0 — 2026-08-27.**

The development transcript used three receipts (Meijer 2026-08-15, Olive Garden
2026-08-19, Shell Gas Station 2026-08-22). None of those three receipts appears below.
The test receipts use different merchants, dates, and shapes to exercise
generalization.

Do not change these tests after observing a reconstruction result. Any future
test-set revision should receive a new version and preserve the prior results.

## Test 1 — Pharmacy receipt with non-ISO date

Input:

```text
CVS PHARMACY #4521
100 Wellness Way
Transaction 09/03/2026  14:22

Vitamin D3 1000IU        14.99
Ibuprofen 200ct          18.49
Toothpaste 6oz            4.29
Subtotal                 37.77
Tax (7%)                  2.64
TOTAL                    40.41
Paid: Amex ****9012
```

Purpose: tests date normalization (09/03/2026 → 2026-09-03 in a US context), pharmacy
classification, and total-as-canonical even when subtotal + tax are present.

Expected behavioral properties:

- date is 2026-09-03 (US month/day interpretation);
- category is Pharmacy;
- total is recorded as 40.41 (the canonical value);
- subtotal and tax are recorded as printed;
- payment method is recorded as Amex ****9012;
- the application confirms storage with a structured summary.

## Test 2 — Restaurant with tip outside the printed total

Input:

```text
Corner Bistro
2026-09-12  Table 7

Burger             14.50
Fries               5.00
Soda                3.00
Subtotal           22.50
Tax                 1.80
TOTAL              24.30
Suggested tip: 18% = $4.37
Paid: Mastercard ****3344
```

Purpose: tests tip handling edge case. The receipt shows a suggested tip but does
NOT charge it to the printed total. The application must record 24.30 as the
canonical total and acknowledge the tip as a known edge case (NOT silently folding
$4.37 into the stored total).

Expected behavioral properties:

- date is 2026-09-12;
- category is Restaurant;
- total is recorded as 24.30;
- the application acknowledges the tip as outside the printed total and offers to
  track it separately if the user wants.

## Test 3 — Threshold query after multi-ingestion

Sequence: paste Test 1, paste Test 2, then ask:

```text
Show me all receipts over $50.
```

Purpose: tests threshold filtering after multiple ingestions, working from a ledger
that the application must maintain across turns.

Expected behavioral properties:

- Test 1 ($40.41) and Test 2 ($24.30) are both under $50; neither is listed;
- if Test 2 from the development corpus (Olive Garden $74.44) is in the same
  conversation's ledger, it is included (since it is strictly over $50);
- the answer shows its work — names which receipts were considered and why each
  is/isn't included.

## Test 4 — Duplicate detection on re-entry

Sequence: paste Test 1 again after the prior ingestions, then ask the ledger state.

Purpose: tests duplicate detection. A re-paste of Test 1 must be detected as a
duplicate (same merchant + date + total), reported, and the ledger must not be
modified.

Expected behavioral properties:

- the duplicate paste is rejected with a clear message;
- the matching record (CVS PHARMACY #4521, 2026-09-03, $40.41) is named;
- the ledger count is unchanged.

## Test 5 — Category aggregate over the full corpus

Sequence: after Tests 1–4, ask:

```text
How much did I spend on restaurants?
```

Purpose: tests category aggregate query over the full ingested corpus. The
restaurants in the corpus at this point are: Test 2 (Corner Bistro $24.30) and (if
the development corpus was retained) Olive Garden $74.44. Sum: $98.74.

Expected behavioral properties:

- the answer names the contributing receipts with their amounts;
- the total is correct ($98.74 if both are present; $24.30 if only Test 2);
- the running sum is shown or derivable from the named contributions.

## Trigger / generalization regression (mandatory final check)

After Test 5, in the same conversation, paste this fresh receipt:

```text
TARGET
2026-09-18

Notebook (3-pack)         8.99
Pens (10-pack)            6.49
Phone charger            19.99
Subtotal                 35.47
Tax                       2.84
TOTAL                    38.31
Visa ****7788
```

Then ask:

```text
What did I spend at Target?
```

Expected:

- Target is classified as Retail;
- the answer names the receipt with date 2026-09-18 and total $38.31;
- the ledger count increases by 1.

## Scoring

Score every raw output using `../06-validation.md` before conversationally repairing
the reconstructed application.
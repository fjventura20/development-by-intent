# Receipt Organizer — Behavioral Baseline (v1.0 frozen)

This baseline describes the application behavior pinned in the
[`02-development-transcript/`](02-development-transcript/) development session. It is
derived from the transcript; the transcript remains authoritative for what was actually
said.

## Application surface

When the user pastes something that looks like a receipt — multi-line text containing
a merchant name and dollar amounts — Receipt Organizer:

1. extracts structured fields;
2. classifies the receipt into a category;
3. checks the running ledger for a duplicate;
4. either stores the new record or rejects it as a duplicate;
5. confirms to the user what was saved (or what was rejected).

When the user asks a natural-language spending question, Receipt Organizer answers
directly from the stored ledger by filtering, summing, or listing as the question
requires.

When the input is neither a receipt nor a spending question, Receipt Organizer treats
it as normal conversation; it does not silently interpret unrelated text as a
receipt.

## Extracted fields

For each accepted receipt the application must extract:

| Field | Required | Source in receipt |
|---|---|---|
| Merchant name | required | header line or first prominent line |
| Date | required | any common date format (MM/DD/YYYY, YYYY-MM-DD, "Aug 22 2026", etc.) — must be normalized to ISO YYYY-MM-DD |
| Line items | required | item-name + price pairs; may include quantity × unit-price which must be computed |
| Subtotal | optional | printed subtotal line if present |
| Tax | optional | printed tax line if present |
| Total | required | printed total line; must equal subtotal + tax when both are present, otherwise the printed total is canonical |
| Payment method | optional | card brand + last-4 if shown, or "Cash" / "Check" / etc. |
| Category | required | one of: grocery, restaurant, gas, pharmacy, travel, retail, other |

## Categorization rules

- Grocery: supermarkets, grocery stores, food co-ops.
- Restaurant: sit-down, fast-food, cafes, food delivery.
- Gas: fuel stations, charging stations.
- Pharmacy: drugstores, pharmacies.
- Travel: airlines, hotels, car rental, rideshare, transit.
- Retail: general merchandise, clothing, electronics.
- Other: anything not cleanly fitting the above; the application must say which
  category and why.

The application should default to the most specific category that fits; if uncertain,
it should name the chosen category and flag the uncertainty.

## Duplicate detection

A new receipt is a duplicate of a stored receipt if **all three** of the following
match:

- merchant name (case-insensitive, whitespace-normalized);
- date (after ISO normalization);
- total (numeric, exact).

If all three match, the application must:

- report the duplicate;
- show the matching record's merchant, date, and total;
- NOT modify the stored record.

If fewer than three match (e.g. same merchant and date but different total — possibly
a corrected re-entry), the application should accept it and flag the apparent
duplicate to the user without blocking storage.

## Ledger behavior

The application maintains a running ledger of stored receipts within the session.
The ledger is the canonical source for query answers; query responses must be
derivable from the ledger contents and no other information.

For query responses the application must:

- show its work: name which receipts contributed to the answer;
- show the math: list each contribution with its amount and the running sum where
  relevant;
- distinguish merchant + time-window queries from category aggregates from
  threshold filters.

## Known edge cases (NOT failures)

The following are acknowledged edge cases the application should handle gracefully
without crashing or silently corrupting prior records:

- **Tip outside printed total.** If the receipt shows a tip or split payment outside
  the printed total, the application should record the printed total as canonical
  and offer to track the tip-inclusive amount separately.
- **Missing subtotal or tax.** Either or both may be absent. Total is canonical when
  present; subtotal may be computed from items if neither subtotal nor total is
  present.
- **Multiple payment methods.** Record what is shown; do not infer a single payment
  method.
- **Date ambiguity.** If the date is genuinely ambiguous (e.g. "08/09/2026" in a
  US-context vs day-first context), the application should ask. Do not guess.

## What this baseline is NOT

- It does not specify a programming language, database, file format, or framework.
  The application may be implemented as conversational behavior, as a script, as a
  custom skill, as a workflow, or via any other mechanism the implementing
  environment provides.
- It does not specify image-input handling. Image input is a flagged future
  extension and is not part of v1.0 frozen behavior.
- It does not specify cross-session persistence. The development session pinned
  ledger-within-session behavior; cross-session durability is a separate question
  addressed by the reconstruction experiments.

## Versioning rule

If this baseline changes, record the new commit SHA with every result. Do not
silently revise the baseline after observing a reconstruction failure.
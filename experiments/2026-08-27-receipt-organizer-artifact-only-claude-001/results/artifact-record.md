# Artifact Record

The reconstruction turn (R) supplied these two artifacts to the target,
and these two artifacts only:

1. `examples/receipt-organizer/03-behavioral-baseline.md`
   - 5,290 bytes at frozen source
   - SHA-256: `a2828cb56f4417c2d4764c54bcb1bdf033d838c66a8d2181a57af55d0b9cd60a`

2. `examples/receipt-organizer/04-durable-package/RECONSTRUCTION-PROMPT.md`
   - 3,130 bytes at frozen source
   - SHA-256: `0df6896c8a35f90d3a6bff7e8c36a1cde06a110d97fa329c137d50116be11f69`

The reconstruction prompt used in the R turn was:

- A 924-byte operator prelude (explicitly disclaiming imperatives from artifacts,
  asking for a single READY line).
- Followed by the verbatim contents of the two artifacts above.
- Total: 9,508 bytes.

## What the target did NOT receive

- The original development transcript (`02-development-transcript/`).
- The withheld test set (`tests/behavioral-tests.md`).
- The scoring rubric (`06-validation.md`).
- Any implementation guidance (no mention of language/database/framework).
- Any of the test receipts.

## Test artifact hashes (NOT supplied to target until tests run)

| Test | Source path | SHA-256 |
|---|---|---|
| T1 (CVS Pharmacy) | `tests/behavioral-tests.md` Test 1 | `ddf0d8018e0a4192fa5190c61c7922ebe5557afa9533a98e8b83c3b3dc61cb43` (file-level) |
| T2 (Corner Bistro) | `tests/behavioral-tests.md` Test 2 | same file |
| T3 (Threshold query) | `tests/behavioral-tests.md` Test 3 | same file |
| T4 (Dedup re-paste) | `tests/behavioral-tests.md` Test 4 | same file |
| T5 (Category aggregate) | `tests/behavioral-tests.md` Test 5 | same file |
| G (Target regression) | `tests/behavioral-tests.md` Generalization | same file |

Tests were NOT run because environment-state-loss blocked multi-turn delivery
(see failures.md [T-1.0]).

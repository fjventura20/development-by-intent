# Receipt Organizer — Behavior Derivation Map

This file is a **derived traceability aid**, not original development evidence. It
maps the preserved development conversation to the behavioral baseline in
`../03-behavioral-baseline.md`.

The distinction matters: some behaviors were stated explicitly by the user (in this
case, by the operator acting as developer driver), while others are inferred from
repeated successful outputs. The transcript remains authoritative for what
historically happened.

## Traceability map

| Development evidence | Status | Behavioral implication |
| --- | --- | --- |
| Initial request names extraction (merchant, date, line items, tax, total, payment), classification (grocery, restaurant, gas, pharmacy, …), persistence, dedup, and three query shapes | Explicit user intent | The application surface covers all seven capabilities named |
| First assistant turn proposed writing three Python files (storage.py, organizer.py, main.py) | Development suggestion | A code-deployable implementation is one valid shape, not the only one |
| User redirect (Turn 2): "I'm not interested in you writing Python files. I want to develop this as a conversational application — the behavior lives in this conversation. You are the application." | Explicit user requirement | The application is conversational, not code-deployable; ledger is conversational working memory |
| Turn 2 assistant response: confirmed conversational role, processed the Meijer receipt, showed structured summary table, "Receipts on file: 1" | Demonstrated behavior | The conversational-with-structured-summary shape is the application surface |
| Turn 3 (Shell gas): date parsed 08/22/2026 → 2026-08-22; quantity × unit-price math (12.50 gal @ 3.199/gal → 39.99) computed correctly; category "Gas" inferred | Demonstrated behavior | Date normalization, quantity math, and category inference are part of the contract |
| Turn 4 (duplicate Shell paste): rejected as duplicate, matched on merchant + date + total, ledger unchanged | Demonstrated behavior | Dedup rule = merchant + date + total; rejection message names matching record |
| Turn 5 (Olive Garden with tip): recorded total as $74.44; acknowledged $20 tip as outside printed total and offered tip-inclusive tracking | Demonstrated edge-case handling | Tip outside printed total is acknowledged, not silently folded |
| Turn 6 (three queries): "Meijer in August" → $13.63 (one receipt, named); "groceries" → $13.63 (one receipt, named); "over $50" → Olive Garden $74.44 (named); Shell and Meijer explicitly noted as under threshold | Demonstrated query answering | Queries show their work — name contributing receipts and the math |
| Turn 7 (behavior pinning): pinned for session — receipt paste vs. spending question vs. general chat; current ledger summarized | Accepted behavioral refinement | The classification-on-shape rule is pinned |
| Turn 8 (durability spec): AI summarizes its own behavior in ~195 words covering extraction fields, classification, dedup, storage, query answering, normal-chat fallback, and tip edge case | AI-derived durability spec | Source material for the reconstruction prompt and behavioral baseline |

## Explicit requirements versus derived constraints

### Explicitly established in the conversation

- extract merchant name, date, line items, tax, total, payment method;
- classify into grocery / restaurant / gas / pharmacy / travel / similar;
- store the receipt in working memory;
- detect duplicates;
- answer three natural-language query shapes: merchant + time-window, category
  aggregate, threshold filter;
- act as the application conversationally (no code);
- structured summary on save;
- running ledger visible to the user.

### Derived from demonstrated behavior

The following are not quoted user requirements, but they are present in the
successful outputs and are therefore represented in the behavioral baseline:

- ISO date normalization (08/22/2026 → 2026-08-22) — derived from the Shell
  receipt processing;
- quantity × unit-price computation — derived from the Shell line item;
- case-insensitive merchant matching for dedup — derived from the Shell
  duplicate handling;
- showing the matching record's merchant / date / total on duplicate rejection —
  derived from Turn 4;
- naming contributing receipts in query answers — derived from Turn 6;
- distinguishing exact-match filter ("over $50") from aggregate ("how much on
  groceries") — derived from Turn 6.

## Edge cases acknowledged in the conversation

- **Tip outside printed total** (Turn 5): the application must record the printed
  total as canonical and offer tip-inclusive tracking as a separate option. This
  is the only edge case the development conversation surfaced; the baseline
  generalizes to additional edge cases (missing subtotal/tax, multiple payment
  methods, date ambiguity) that are consistent with the demonstrated pattern
  but were not explicitly exercised.

## Open questions (not closed by the development session)

- **Image input.** Named in the initial intent as a flagged future extension. Not
  exercised. Not part of v1.0 frozen behavior.
- **Cross-session persistence.** The development session used within-conversation
  working memory; whether the same behavior survives across sessions is a
  separate experiment.
- **Implementation freedom.** The development session used the conversational
  surface; whether the application retains its behavioral identity when
  implemented through other mechanisms (custom skill, workflow, code artifact,
  etc.) is the implementation-freedom experiment on the research agenda.
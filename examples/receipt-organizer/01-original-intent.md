# 01 — Original Intent

This file summarizes the product intent that emerged at the start of Receipt Organizer
development. It is **not a substitute for the verbatim source conversation**. Exact
wording belongs in [`02-development-transcript/`](02-development-transcript/).

## Initial product idea

For a receipt supplied as plain text (with image input explicitly flagged as a future
extension), Receipt Organizer should:

- extract merchant name, date, line items, tax, total, and payment method;
- classify the receipt into a category such as grocery, restaurant, gas, pharmacy, or
  similar;
- store the receipt in working memory so a history accumulates across the session;
- detect duplicates when the same receipt is pasted twice (matching on merchant +
  date + total);
- answer natural-language spending questions over the accumulated records, including
  merchant + time-window queries, category aggregates, and threshold filters.

## Why this differs from Amazing Birthday

Amazing Birthday is a stateless conversational application — each request is a
self-contained input that produces a self-contained output. Receipt Organizer is
**stateful and data-producing**: each ingestion leaves a persistent record, and
queries must reason over the accumulated history. This is the next step in the
Development by Intent evidence program.

The behavioral questions that follow from this shift are different:

- Does the application maintain a coherent ledger across many turns?
- Does deduplication generalize beyond exact-match (e.g. when a receipt is re-entered
  with minor whitespace differences)?
- Do query answers remain correct as the corpus grows?
- Does the behavior generalize to receipts with tips, split payments, or unusual date
  formats without silently corrupting prior records?

## Development stance

The behavior was shaped interactively, exactly as in the Amazing Birthday example:

- request an initial result;
- inspect what was useful or unhelpful;
- correct the behavior in natural language (the load-bearing turn-2 redirect from
  "write code" to "act as the application");
- reuse the application on a different input;
- exercise the natural-language query interface;
- accept the behavior and pin it as reusable;
- capture a durability spec for hand-off to a fresh environment.

The transcript is the authoritative record for what was actually said and in what
order.

## Why this matters to DbI

The key research question for this example is whether a stateful, data-producing
application built through intent can be captured, reconstructed, and reproduced
independently — same claim as for Amazing Birthday, but at a substantially harder
level of demand.
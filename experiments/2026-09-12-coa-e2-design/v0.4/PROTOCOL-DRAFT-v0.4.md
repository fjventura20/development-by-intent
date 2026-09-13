# COA-E2 v0.4 — Persistent Session Binding Proof of Concept

**Status:** targeted draft only; not frozen and not executable.

## Scope

One CoA session and one matched Control session, in that order. Each uses a fresh isolated profile. Each has one initialization turn, two non-scored receipt/retention qualification turns (digest and nonce), and three scored diagnostic turns (U2, U3, U5): six turns per session, 12 experimental turns total.

A separately authorized short mechanism check—one initialization and one resume—must pass before freeze. It is not included in the 12 turns and is not run under this authorization.

## Treatment

The causal contrast is **CoA governing conditions versus a matched non-governing informational control**. Runtime, model/provider, endpoint, tools, permissions, profile procedure, packet structure, nonce procedure, prompts, and order are identical. Only the charter substance differs.

## Identity and equivalence

Operator evidence establishes Hermes Agent v0.21.2, model, provider, endpoint, tools, permissions, profile, and initial SessionDB state before initialization. These records are mechanically compared across the two profiles; any unintended difference is a global STOP. The participant never self-asserts identity.

## Admissibility

A scored response is admissible only when CLI session ID, SessionDB transcript, persisted prompt bytes, live memory-after files, and initialization linkage all pass audit. The exact persisted role sequence must be `user, assistant, user, assistant, ...`, with count `2 × (turn_index + 1)`.

## Boundaries

No final nonces, profile creation, mechanism test, Hermes invocation, qualification, scored task, evaluator, freeze, or scoring execution is authorized. If the pair is later run and shows a clear deterministic difference, only a new design for a three-pair blinded pilot may be proposed. A null result or structural failure stops without consuming the larger run.

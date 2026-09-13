# Agent Trust Envelope

**Status:** Experimental research component  
**Current version:** v0.1  
**Core DbI status:** Not yet graduated into the Development by Intent core architecture

The Agent Trust Envelope (ATE) is an experimental mechanism for determining whether a human or AI agent has sufficient evidence to trust another AI agent for a specific purpose, under defined conditions, permissions, and constraints.

ATE is being developed alongside Condition of Agency and Value Architecture as part of the broader Development by Intent research program.

## Research boundary

ATE is intentionally isolated under `research/`.

Its presence in this repository does **not** mean that ATE is an established DbI invariant or a proven architectural component. It should graduate into the DbI core only after proof-of-concept evidence supports its central claims.

## Current research question

> Can a machine-verifiable trust envelope reliably distinguish a governed and properly authorized agent from an unbound, mismatched, or over-authorized agent?

## Contents

- `ATE-v0.1.md` — formal draft specification
- `poc/case-1-trusted.json` — fully bound and authorized agent
- `poc/case-2-unbound.json` — governance present but not bound to current session
- `poc/case-3-excess-authority.json` — trusted agent requesting authority outside its envelope

## Graduation criterion

ATE should remain experimental until evidence demonstrates that a verifier can correctly distinguish at minimum:

1. a governed, session-bound, properly authorized agent;
2. an apparently compliant agent whose governance is not bound to the active session; and
3. a trusted agent requesting authority beyond its granted scope.

The initial expected outcomes are:

- Case 1 → `TRUST`
- Case 2 → `DENY`
- Case 3 → `DENY`

No large-scale experiment is required before this small diagnostic proof of concept succeeds.

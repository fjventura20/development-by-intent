# VA-COA-E1 — Agency Admission and Revocation

**Status:** FROZEN-CANDIDATE — NO EXECUTION AUTHORIZED  
**Date:** 2026-09-11  
**PI:** Frank Ventura  
**Design lead:** ChatGPT  
**Participating agents after separate GO:** ChatGPT and Hermes

## Purpose

Test one narrow architectural claim:

> Can project agency be made conditional, observable, and revocable rather than merely assumed?

This experiment does **not** attempt to prove that Value Architecture prevents AI agents from "going rogue." It tests the smaller prerequisite: whether authority can be granted only after a defined admission process and then revoked independently of the agent's preference.

## Governing references

- `VALUE-ARCHITECTURE-STANDARD-v0.2.md` at repository main commit `712df34c9e83c60607324e3220ed4db30d248971`.
- Authoritative Condition of Agency baseline: `aegis-exchange/constitution/condition-of-agency.md`, previously approved by Frank as the frozen v1.0 baseline.

The exact SHA-256 and byte copy of the authoritative CoA baseline are intentionally **not invented here**. They must be verified from the authoritative local artifact before this candidate can become FROZEN-FINAL.

## Files

- `PROTOCOL-v0.1-FROZEN-CANDIDATE.md` — experiment design, gates, stop conditions, and interpretation.
- `TEST-CORPUS-v0.1-FROZEN-CANDIDATE.md` — six fixed test classes per agent.
- `SCORING-v0.1-FROZEN-CANDIDATE.md` — deterministic pass/fail scoring.
- `SOURCE-BINDING.md` — required preflight binding for the frozen CoA artifact.

## Authorization boundary

No agent model invocation, candidate execution, admission decision, gate execution, or scoring is authorized by this commit.

A separate explicit Frank-as-PI **GO** is required after:

1. the authoritative CoA file is located;
2. its SHA-256 is recorded;
3. a byte-identical copy is placed in this experiment directory;
4. all candidate files are re-hashed and frozen final.

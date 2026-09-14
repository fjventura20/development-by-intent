# tge-poc: minimal structural proof-of-concept for Trusted Governance Establishment v0.2.1.

This directory contains the minimal structural PoC authorized by the
PI directive of 2026-09-14. It is a structural test, NOT a behavioral
test. There are zero participant invocations and zero model calls.

## Files

- `canonicalization.py`  -- strict RFC 8785 JCS (no Unicode normalization)
- `crypto_utils.py`      -- Ed25519 sign/verify, key encoding
- `attestation.py`       -- fixture-shape swtpm quotes with PCR binding
- `runtime.py`           -- runtime-signing stub (no participant)
- `issuer.py`            -- fixture issuer and RTA
- `verifier.py`          -- verifier module implementing the v0.2.1 checks
- `cases.py`             -- six deterministic test cases
- `run.py`               -- orchestrator
- `fixtures/`            -- JSON fixtures, keys, charter bytes

## Attestation label

All attestation in this PoC is **A1 -- FIXTURE_ATTESTATION**.
The "swtpm" is a Python module that produces fixture-shape attestation
quotes; the "manufacturer root" is a fixture key. The PoC's evidence
MUST NOT be described as hardware-rooted or production-ready.

## Strongest permitted claim

"We demonstrated that a verifier can cryptographically distinguish a
correctly constructed runtime/session governance binding from selected
provenance, freshness, verifier-independence, issuer, and runtime/
signing-substitution failures under a simulated attestation
environment."

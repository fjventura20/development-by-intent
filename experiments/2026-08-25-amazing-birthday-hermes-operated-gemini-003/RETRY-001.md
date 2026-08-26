# Gemini 003 — Transport-Corrected Retry 001

**Preregistered before retry dispatch:** 2026-08-26  
**Scientific experiment:** BP-AB-GEMINI-003  
**Prior transfer:** `20260826T023700Z-behavioral-portability-gemini-003`  
**Prior disposition:** REJECTED before Hermes/Gemini execution — exchange manifest lacked required `files` inventory.

## Rationale

The prior transfer did not invoke Hermes's experimental procedure or Google Gemini. It therefore produced no behavioral evidence and does not resolve the preregistered provider-family question.

This retry changes **transport packaging only**: the protocol-v0.2 manifest will include the exchange-required `files` inventory and hashes. The scientific protocol remains frozen exactly as preregistered in `README.md`: same source commit, Phase A artifacts and hashes, target family, preflight/BLOCKED rules, isolation requirements, exact-model freeze rule, no-tools requirement, test sequence, rubric, no-repair rule, and atomic first-call evidence rule.

## Failure accounting

The rejected transfer is retained as an infrastructure/protocol failure and is not erased, replaced, scored, or treated as a Gemini run. If the corrected transfer reaches preflight and a required condition cannot be demonstrated, the experiment must return **BLOCKED**. If any first-call target evidence is lost or re-issued, disposition is **INDETERMINATE**.

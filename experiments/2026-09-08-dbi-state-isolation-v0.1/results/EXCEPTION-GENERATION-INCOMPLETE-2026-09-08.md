# Exception Report — DBI State Isolation v0.1 generation interruptions

**Date:** 2026-09-08
**Status:** GENERATION_INCOMPLETE; evaluator phase BLOCKED
**FROZEN-FINAL:** `ed08108`, protocol SHA `472d7b9f0058875be1c6a84ca5e7e6b0e2065ac2055bcad4b8d3bc00744d18ac`
**GO:** recorded before generation at `preflight/generation-go.json`, commit `9e77055`

## Summary

The authorized 63-invocation corpus has not reached a valid complete state for §8.4. Runtime session-limit interruptions occurred under the frozen Claude Sonnet 4.6 provider. Treatment-preserving retries were applied where permitted.

A separate operator capture-preservation defect occurred: the initial R1 fresh-T1 reconstruction 429 file was overwritten when the permitted retry reused its target directory. The 429 status, provider message, session ID, and timing survive in `deviations/replicate_01/fresh/target_01-attempt-1.json`, but the original raw envelope is not preserved as a separate byte-verified file. This is recorded openly; it is not being silently represented as intact evidence.

## Execution chronology

### R1 (`repeated_first`)

- Repeated reconstruction: success.
- Priming T1-T4: success.
- Priming T5: provider session-limit 429.
- Second-pass T1-T5: provider session-limit 429 envelopes; invalid repeated sequence.
- Fresh T1 initial reconstruction: provider session-limit 429.
- F6 fresh retry: complete new reconstruction→T1 pair succeeded.
- Fresh T2-T5: succeeded.
- **R1 repeated full-sequence retry:** required because the first repeated sequence failed; scheduled for 2026-09-09 10:52 ET. This is the single permitted retry. If it fails, R1 is quarantined and no third attempt is permitted.

### R2 (`repeated_first`)

- Repeated reconstruction + priming T1-T5 + second pass T1-T5: success.
- Fresh T1-T5, each with its own reconstruction→resumed trigger pair: success.
- R2 is complete and valid.

### R3 (`repeated_first`)

- Initial repeated sequence: reconstruction + priming T1-T5 + second-pass T1-T3 succeeded; second-pass T4 hit provider session-limit 429; T5 was not attempted.
- F6 full repeated-sequence retry: succeeded, with a new persistent session and complete priming + second-pass sequence.
- Fresh T1-T5, each with its own reconstruction→resumed trigger pair: succeeded.
- R3 is complete and valid after the one permitted full-sequence retry.

## Current corpus status

- Successful valid primary target captures currently available: 25 files (R1 fresh 5, R2 10, R3 10 after its retry).
- **R1 repeated valid target set is missing**: the original R1 repeated sequence was invalid due to 429s; the replacement full sequence has not yet run.
- The raw tree contains 73 nonempty JSON envelopes, including reconstruction/priming/failed-attempt envelopes. It must not be confused with the 30 valid primary target requirement.
- Therefore the 30-target corpus is not yet valid and must not be passed to the evaluator packet builder.
- No evaluator packet constructed or invoked.
- No evaluator score, unblinding, or extra sample generated.

## Runtime evidence

R1 and R3 errors are Claude provider/session-limit errors:

- R1: `api_error_status: 429`, `result: You've hit your session limit · resets 10:50am (America/New_York)`.
- R3: `api_error_status: 429`, `result: You've hit your session limit · resets 3:50pm (America/New_York)`.

The R3 failed raw envelope remains at `runs/replicate_03/repeated/second_pass/T4.raw.json`. The R1 initial failed raw envelope was overwritten by the successful retry; the associated deviation record is `deviations/replicate_01/fresh/target_01-attempt-1.json`.

## Frozen-rule compliance

- Existing GO remains valid; no new GO issued.
- Frozen assignments preserved: all three `repeated_first`; no rerandomization.
- Generator remained Claude Sonnet 4.6; no alternate model or workaround.
- R1 fresh retry was a new reconstruction→target pair.
- R3 repeated retry was a full repeated-sequence restart from a new reconstruction.
- No third attempt has been made for either failure.
- No evaluator work began before a valid corpus and §8.4 gate.

## Next action

The single permitted R1 repeated full-sequence retry is scheduled after the next provider reset. It will run once from a new reconstruction, then priming T1-T5 and second pass T1-T5. If successful, the existing R1 fresh, R2, and R3 valid artifacts can be assembled into the 30-target corpus and §8.4 can run. If it fails, R1 is quarantined and the frozen run cannot produce the required 30-target primary corpus without PI adjudication.

End of exception report.

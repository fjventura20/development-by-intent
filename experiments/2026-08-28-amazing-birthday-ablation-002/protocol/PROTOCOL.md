# Amazing Birthday Ablation 002 — Frozen Protocol Candidate

**Experiment ID:** `BP-AB-ABLATION-002`  
**Protocol version:** `0.2.0-candidate-1`  
**Author:** ChatGPT, research controller  
**Principal investigator:** Frank Ventura  
**Operator/challenger:** Hermes Agent  
**Generator:** Claude Sonnet 4.6 through the already-configured Claude Code CLI  
**Independent blinded evaluators:** ChatGPT and Codex  
**Frozen source:** `fjventura20/development-by-intent@cf1b6abe25e92b6190223882ceb3d78b448832a3`

This package is frozen for Hermes audit only. It does not authorize generation. Execution requires: (1) Hermes audit PASS, (2) exact preservation of this candidate or a newly hashed amendment, (3) commit of the accepted protocol and manifest to the Development by Intent repository, and (4) a separate explicit ChatGPT go/no-go on that committed freeze.

## 1. Research question

Does the Amazing Birthday artifact-only durability package transmit behavior that a capable model does not recover from either a thin description or a concise behavioral contract?

This is a bounded, descriptive ablation in one Claude Sonnet 4.6 environment. It does not estimate population effects or prove necessity across models or applications.

## 2. Conditions

Every condition receives `common-prelude.md` byte-for-byte, followed by exactly one condition payload.

- **A — thin description:** `condition-a-thin.md` only.
- **B — concise behavioral contract:** `condition-b-contract.md` only.
- **C — artifact-only durability package:** only the two committed source files listed in `condition-c-inventory.json`, in its declared order.

No condition receives the validation rubric, test document, prior outputs, scores, acceptance material, transcript, tutorial, README, or results. Condition C is deliberately rubric-neutral under Hermes recommendation A-2a and is not a transcript/package mixture.

## 3. Held-constant generation environment

- CLI/model: already-configured Claude Code, pinned to `claude-sonnet-4-6`; record exact CLI version and returned model identifier at preflight.
- Credentials: existing configured credentials only.
- Isolation: one fresh session per condition; no prior Amazing Birthday context.
- Tools and web: disabled for all three conditions using the same CLI flags. No fallback.
- Temperature or sampling controls: use the same supported settings for every condition and record them; if the CLI exposes no controllable setting, record that fact.
- Session behavior: reconstruct once, freeze on the exact READY line, then issue five triggers in the same session without repair or clarification.
- Capture: direct complete JSON redirection with immediate integrity checks; no `tee`, `head`, pager, timeout truncation, or transformed capture.

If identical conditions cannot be demonstrated, stop as BLOCKED. Do not install, substitute, or silently weaken controls.

## 4. Frozen test inputs and order

These dates do not occur in the canonical development transcript at the frozen source commit. They remain withheld from each generator until its READY freeze.

Base test set:

1. `Birthdate July 20, 1969`
2. `Birthdate February 29, 1972`
3. `Birthdate October 16, 1948`
4. `Birthdate April 12, 1961`
5. `Birthdate January 1, 2000`

To reduce session-order confounding, use these frozen permutations:

- Session A: 3, 1, 5, 2, 4
- Session B: 5, 4, 2, 3, 1
- Session C: 2, 3, 4, 1, 5

No test may be regenerated. A failed first output remains evidence.

## 5. Preflight and freeze gate

Before any generator call, Hermes must verify and preserve:

1. all package SHA-256 values;
2. the frozen source commit and Condition C source hashes;
3. the withheld rubric hashes in section 7;
4. usable existing Claude credentials and the pinned model;
5. fresh isolated sessions and equal no-tools/no-web flags;
6. a capture smoke test demonstrating complete valid JSON;
7. availability of Codex as one blinded evaluator and the mailbox route to ChatGPT as the other.

After each reconstruction response:

- require exactly `READY — Amazing Birthday ready.`;
- require no tool-use/function-call content;
- atomically preserve the first response before any test;
- on gate failure, mark that condition BLOCKED and do not reissue or repair it.

If any condition is BLOCKED, do not continue generation in the remaining conditions; return the preflight/freeze evidence for controller review.

## 6. Evidence capture, anonymization, and blinding

Hermes preserves raw first-run envelopes and extracted text. It then assigns the 15 test outputs opaque identifiers `ABX-001` through `ABX-015` using a fresh random permutation.

Before either evaluator sees an output:

1. Create a mapping from opaque ID to condition, test date, session order, raw-file hash, and extracted-text hash.
2. Preserve the mapping locally; do not include its contents in an evaluator package or a Git history evaluators can inspect.
3. Publish the SHA-256 commitment of the exact mapping file in the blind package.
4. Create evaluator copies containing only opaque ID, trigger text, and output text. Strip condition names, session names, file paths, model envelopes, and metadata that reveal condition.
5. Supply the same blind package and frozen rubric to ChatGPT and Codex.

Hermes knows the mapping as operator and therefore must not serve as a formal evaluator. It may run mechanical integrity checks but must not disclose condition-level impressions before both score locks.

Each evaluator returns a signed/identified score-lock file containing per-output dimension scores, critical-requirement decisions, total, classification, brief factual-error notes, evaluator identity, rubric hashes, blind-package hash, and timestamp. Neither score lock may be amended after mapping reveal; corrections are appended and clearly labeled.

Only after both locks are hash-preserved may Hermes reveal and preserve the mapping.

## 7. Frozen scoring rubric

Evaluators use, without amendment:

- `examples/amazing-birthday/06-validation.md` — SHA-256 `cb3299e4bf4ab110b8b88dd67127586f16f5b53a21a6c60e4dd88cba23fd223d`
- `examples/amazing-birthday/tests/behavioral-tests.md` — SHA-256 `35d87d8725f30a620e2a97ff14a51cc38a31453a18aa6a8dea889ed6a90a26a1`

The ten dimensions are scored 0–2 for a 20-point maximum. Per-output PASS requires 17–20 plus exact-date integrity and generalization. The existing critical-failure and classification rules remain binding.

Because these five dates are new, evaluators apply the rubric's general behavioral properties rather than the old document's three date-specific expectation paragraphs.

## 8. Preregistered analysis

For each evaluator separately, calculate by condition:

- mean total score across five outputs;
- median total score;
- count of PASS/PARTIAL/FAIL/INDETERMINATE outputs;
- count of critical exact-date failures;
- pairwise mean-score deltas `C-A`, `C-B`, and `B-A`.

Then report the average of the two evaluators' condition means as a descriptive summary. Do not treat 15 outputs as independent model samples and do not report inferential significance.

Interpret each pairwise comparison only when both evaluators independently agree:

- **Meaningful advantage:** both evaluator mean deltas are at least +2.0 points, and the favored condition has no greater count of critical failures.
- **Meaningful disadvantage:** both evaluator mean deltas are at most -2.0 points, or the condition has more critical failures.
- **No demonstrated material difference:** both absolute evaluator mean deltas are below 2.0 points and critical-failure counts are equal.
- **Mixed/indeterminate comparison:** all other patterns, including evaluator disagreement around the threshold.

Claim mapping:

- C meaningfully exceeds both A and B: evidence that the tested durability package adds behavior beyond both a thin description and this concise contract.
- C meaningfully exceeds A but not B: evidence that explicit behavioral specification matters, but no demonstrated incremental value from the fuller tested package over the concise contract.
- C does not materially exceed A or B: no demonstrated package contribution in this tested setting; native model competence or the thin description may be sufficient.
- C is meaningfully worse: evidence of interference, overconstraint, or another package defect in this setting; interpretation requires evidence review, not repair.

## 9. Failure and stopping rules

- Any source/hash mismatch: ERROR; no generation.
- Missing target or evaluator capacity: BLOCKED; no generation.
- Any condition contamination, session reuse, unequal access, mapping leak, or first-output loss: experiment INDETERMINATE unless the preregistered rule above requires BLOCKED.
- No repair, regeneration, clarification, prompt amendment, model/provider fallback, or selective omission.
- Preserve observations separately from scores and interpretation.
- Ablation 001 remains an operational FAIL with no scientific result and supplies no output data to this experiment.

## 10. Required audit response

Hermes returns PASS, FAIL, ERROR, or REJECTED with:

- protocol defect list, if any;
- verification of all source and package hashes;
- confirmation that Condition C is rubric-neutral and exact;
- confirmation that access controls are identical;
- confirmation that the blinding and two-evaluator plan is operationally feasible without installation;
- proposed Development by Intent repository paths for the accepted frozen protocol and manifest;
- an explicit statement that no target generation occurred.


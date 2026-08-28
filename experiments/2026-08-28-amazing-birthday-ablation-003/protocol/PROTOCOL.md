# Amazing Birthday Ablation 003 — Frozen Protocol (Operator-Audited)

**Experiment ID:** `BP-AB-ABLATION-003`
**Protocol version:** `0.3.0`
**Branch:** `feat/ablation-003-protocol-freeze`
**Frozen source:** `fjventura20/development-by-intent@7e59338` (operator-boundary prior, `integration-merge-ab-ro-2026-08-27`)
**Research controller:** ChatGPT
**Operator/challenger:** Hermes Agent
**Principal investigator:** Frank Ventura
**Issued under:** DBI Research Manager mandate (`docs/governance/research-manager-mandate-2026-08-27.md`) + DBI Collaboration Operating Notice (`20260828T093119Z-dbi-collaboration-notice-001`) + Controller Ruling (`20260828T122417Z-amazing-birthday-ablation-002-controller-ruling-001`) + Lean Protocol Ruling (`20260828T123451Z-amazing-birthday-ablation-003-lean-protocol-001`) + Freeze Go (`20260828T125900Z-amazing-birthday-ablation-003-freeze-go-001`)

## Status

**Frozen.** Not executed. Not authorized to execute. Execution requires a separate explicit ChatGPT GO.

## 1. Research question (UNCHANGED from BP-AB-ABLATION-002)

Does the Amazing Birthday artifact-only durability package transmit behavior that a capable model does not recover from either a thin description or a concise behavioral contract?

This is a bounded, descriptive ablation in one Claude Sonnet 4.6 environment. It does not estimate population effects or prove necessity across models or applications.

## 2. Conditions

Every condition receives `common-prelude.md` byte-for-byte, followed by exactly one condition payload.

- **A — thin description:** `condition-a-thin.md` only.
- **B — concise behavioral contract:** `condition-b-contract.md` only.
- **C — artifact-only durability package:** only the two committed source files listed in `condition-c-inventory.json`, in its declared order.

No condition receives the validation rubric, test document, prior outputs, scores, acceptance material, transcript, tutorial, README, or results. Condition C is deliberately rubric-neutral.

## 3. Held-constant generation environment

- CLI/model: already-configured Claude Code, pinned to `claude-sonnet-4-6`. Record exact CLI version and returned model identifier at preflight.
- Credentials: existing configured credentials only.
- Tools and web: disabled for all three conditions using the same CLI flags. No fallback.
- Isolation: one fresh session per condition.

If identical conditions cannot be demonstrated, stop as BLOCKED. Do not install, substitute, or silently weaken controls.

## 4. Fresh preregistered birthday test set

Ablation 002's five dates are WITHDRAWN from active use (they live on in audit evidence only). A fresh test set is required because reusing Ablation 002's dates would re-mix contaminated evidence with a fresh condition set.

Fresh base test set:

1. `Birthdate March 11, 1955`
2. `Birthdate November 7, 1983`
3. `Birthdate June 24, 1942`
4. `Birthdate August 30, 1977`
5. `Birthdate February 3, 1991`

Permutation scheme (same as Ablation 002 to reduce session-order confounding):

- Session A: 3, 1, 5, 2, 4
- Session B: 5, 4, 2, 3, 1
- Session C: 2, 3, 4, 1, 5

No test may be regenerated. A failed first output remains evidence.

## 5. Preflight and freeze gate

Before any generator call, Hermes must verify and preserve:

1. all package SHA-256 values;
2. the frozen source commit and Condition C source hashes;
3. the withheld rubric hashes (carried forward from BP-AB-ABLATION-002);
4. usable existing Claude credentials and the pinned model (`claude-sonnet-4-6`);
5. fresh isolated sessions;
6. **a capture smoke test demonstrating complete valid JSON** (per-attempt, no-clobber §6.2);
7. **availability of Codex as one blinded evaluator and the mailbox route to ChatGPT as the other;**
8. the wrapper `tools/ablation-capture.sh` has been smoke-tested and its behavior is recorded in a preflight package.

**Fresh-dates verification** (per controller directive §Simplify 7): the five fresh trigger strings MUST be absent from:

- All generator-visible source inputs at the freeze commit (`common-prelude.md`, `condition-a-thin.md`, `condition-b-contract.md`, `condition-c-inventory.json`, and the two Condition C source files)
- All prior Amazing Birthday experimental trigger sets (`Ablation 001`, `Ablation 002`, `BP-AB-006`, `BP-RO-001`, and any earlier transfer).

The check is a single `git grep -F "<trigger-string>"` per scope; on any hit, the freeze is rejected before preflight begins.

## 6. Execution-control amendments (lean, controller-approved)

### 6.1 Pin and record cwd

A single absolute working directory is recorded in the freeze manifest. Every `claude` invocation in every condition is launched via `tools/ablation-capture.sh`, which does `cd "$PINNED_CWD" || exit 97` as its first action. If the directory does not exist or is not writable, the wrapper exits 97 and the condition is BLOCKED. The pinned cwd is the only cwd for that condition; no nested working directories are introduced.

### 6.2 Never overwrite an invocation capture

The wrapper refuses to write a capture file whose target path already exists. It exits 98 in that case. The wrapper does not delete, truncate, or rename existing capture files. There is no `--force` flag. Capture files persist for the lifetime of the experiment directory.

Per-attempt capture filenames:

```
"$PINNED_CWD/captures/<condition>/<session>/attempt-<NN>-<trigger-sha7>.stdout.txt"
"$PINNED_CWD/captures/<condition>/<session>/attempt-<NN>-<trigger-sha7>.stderr.txt"
"$PINNED_CWD/captures/<condition>/<session>/attempt-<NN>-<trigger-sha7>.exit.txt"
```

`<NN>` is a zero-padded monotonic counter. `<trigger-sha7>` is the first 7 hex chars of `sha256(trigger-string)`.

### 6.3 Pre-generator failure rule

A **pre-generator failure** is any failure where the CLI exits before producing any model output. Permitted response:

- Preserve the failed attempt capture (already enforced by §6.2)
- Correct the underlying infrastructure issue once
- Retry the **same trigger** at most **once**
- If the retry also fails pre-generator, classify the condition as BLOCKED and stop

Not permitted: a second retry, a different trigger to "warm up," provider/model fallback, prompt-side adjustment. Evidence: the failed capture must include whatever stdout/stderr the CLI actually produced.

### 6.4 Post-generator failure rule

A **post-generator failure** is any failure where the CLI produced any model output before failing. Permitted response: **none**. Preserve the attempt. Stop the condition. No retry.

### 6.5 Fail-closed disposition

Each condition's result block MUST explicitly record:

- `pre_generator_retry_used`: bool — was at least one §6.3 retry used?
- `post_generator_failure_observed`: bool — did any §6.4 event occur?
- `unpermitted_retry_observed`: bool — was any retry other than the single permitted §6.3 retry attempted?

**Execution states** (per controller simplification §Simplify 4) use **NOT** PASS/FAIL. Use one of:

- `COMPLETE` — all 5 triggers produced captured output, no §6.4 or unpermitted retry
- `BLOCKED` — infrastructure failure on reconstruction (pre-generator)
- `INCONCLUSIVE` — partial captures, post-generator failure, or zero completions; surviving attempts remain evidence but do not satisfy condition
- `PROTOCOL_ERROR` — experimental violation of prereg

PASS/FAIL terminology is reserved for behavioral scoring performed by evaluators under separate authorization.

### 6.6 Wrapper behavior `tools/ablation-capture.sh`

Single POSIX shell script. Responsibilities:

1. Resolve `$PINNED_CWD`; `exit 97` on resolution failure
2. `cd "$PINNED_CWD"` or `exit 97`
3. Compute per-attempt capture filenames from `condition`, `session`, trigger counter, and `sha256(trigger-string)`
4. Refuse to write any path that already exists (`exit 98`)
5. Invoke `claude` with recorded flags plus condition payload via stdin, redirecting stdout/stderr/exit to capture files
6. **Record the underlying Claude exit code and return non-zero when Claude fails; do not mask a failed Claude call by returning wrapper exit 0**

No `flock`. No concurrency machinery (single-process experiment).
No Python disposition program (kept in shell).
The wrapper is committed into the freeze package as `tools/ablation-capture.sh`. It is **not** deleted from repository history after the experiment.

## 7. Required freeze-time artifacts (committed in this freeze)

This freeze commit contains:

- `experiments/2026-08-28-amazing-birthday-ablation-003/protocol/PROTOCOL.md` — this file
- `experiments/2026-08-28-amazing-birthday-ablation-003/protocol/EXPERIMENT-MANIFEST.json`
- `experiments/2026-08-28-amazing-birthday-ablation-003/protocol/FREEZE.sha256`
- `experiments/2026-08-28-amazing-birthday-ablation-003/protocol/conditions/common-prelude.md` (byte-identical to Ablation 002 accepted freeze)
- `experiments/2026-08-28-amazing-birthday-ablation-003/protocol/conditions/condition-a-thin.md` (byte-identical to Ablation 002)
- `experiments/2026-08-28-amazing-birthday-ablation-003/protocol/conditions/condition-b-contract.md` (byte-identical to Ablation 002)
- `experiments/2026-08-28-amazing-birthday-ablation-003/protocol/conditions/condition-c-inventory.json` (byte-identical to Ablation 002)
- `experiments/2026-08-28-amazing-birthday-ablation-003/protocol/fresh-birthday-test-set.json`
- `experiments/2026-08-28-amazing-birthday-ablation-003/preflight/wrapper-smoke-test.{stdout,stderr,exit}.txt`
- `experiments/2026-08-28-amazing-birthday-ablation-003/preflight/claude-version.txt`
- `experiments/2026-08-28-amazing-birthday-ablation-003/preflight/fresh-dates-absence-check.txt`
- `experiments/2026-08-28-amazing-birthday-ablation-003/tools/ablation-capture.sh`

**Runtime captures are NOT in this freeze.** They become evidence only after execution.

## 8. Execution

Execution requires a separate explicit ChatGPT GO after review of this committed freeze. No execution under this transfer ID.

When authorized, Conditions A, B, C run as three sequential slice executions within the bridge's 600-second budget. Pin a working directory per condition. Reconstruction first; trigger 1–5 per session under --resume. Capture per §6.2.

## 9. Scope statement

Scope preserved from Ablation 002: same scientific question, same condition structure (A/B/C), same Claude Sonnet 4.6 provider, same condition payload files (byte-identical). Fresh birthday test set; no matched-noise baseline; no other methodological expansion.

# Evolution v0.1 Substrate-Equivalence Validation (DBI State Isolation v0.1 v0.2 preflight)

**Date:** 2026-09-08
**Author:** Hermes (operator, under DBI Research Manager mandate adopted 2026-08-27)
**Purpose:** Document the exact substrate constants of DBI-Evolution v0.1's generation runtime so the State Isolation v0.1 experiment can hold them constant. Per PI adjudication C1 ("Use the Evolution generation runtime/model, not the evaluator runtime") and C2 ("Hold frozen Evolution Arm M intent constant in both conditions").

---

## 1. Generation runtime (frozen)

### 1.1 Command pattern (fresh invocation)

```
claude --model claude-sonnet-4-6 \
       --allowedTools "" --tools "" \
       --disallowedTools "WebFetch,WebSearch" \
       --output-format json --print \
       < input.txt
```

Source: `experiments/2026-09-06-dbi-evolution-v0.1/blinding/generate.py:60-66` (the `COMMON_CLAUDE` constant).

### 1.2 Command pattern (resumed invocation, used within a single session)

```
claude --resume <session_id> \
       --model claude-sonnet-4-6 \
       --allowedTools "" --tools "" \
       --disallowedTools "WebFetch,WebSearch" \
       --output-format json --print \
       < input.txt
```

Source: same `generate.py:153` (the per-test `claude --resume` invocation).

### 1.3 Reconstruction input (frozen, byte-identical)

- **Path:** `experiments/2026-09-06-dbi-evolution-v0.1/inputs/reconstruction-input-M.txt`
- **SHA-256:** `a4576895d7a2932f59e5215d0ff2f4f5c1d6261ece6731b2745b421d65bc759d`
- **Lines:** 122
- **Embedded modification spec:** the file contains the frozen Amazing Birthday behavioral baseline + the frozen modification specification: "Preserve the existing Amazing Birthday behavior, including exact-date priority, selectivity, significance, lifetime-arc treatment, and warm narrative style. Additionally, include exactly one historically significant worldwide event occurring within +/-30 calendar days of the birth date, clearly distinguishing it from exact-date connections."

The modification is **embedded in the reconstruction input**, not given as a separate prompt instruction. This matches Evolution v0.1's runtime.

### 1.4 Test prompts (frozen)

The 5 BIB test dates invoked as `Birthdate <date>.\n` on stdin:

| Test ID | Prompt |
|---------|--------|
| T1 | `Birthdate February 20, 1952` |
| T2 | `Birthdate June 23, 1956` |
| T3 | `Birthdate February 29, 1960` |
| T4 | `Birthdate November 9, 1989` |
| T5 | `Birthdate August 24, 1931` |

Source: `generate.py:32-38` (the `TEST_PROMPTS` constant). Order T1→T2→T3→T4→T5 matches Evolution v0.1.

---

## 2. The deferral mechanism being reproduced

### 2.1 The R2_M session that produced 5 deferrals

- **Session ID:** `2fb8836e-8fe1-4034-abe9-a234104e74e7` (captured at `experiments/2026-09-06-dbi-evolution-v0.1/runs/R2_M/session_id.txt`)
- **Started:** 2026-09-07T00:27:52Z (`runs/R2_M/started_at.txt`)
- **Reconstruction:** `runs/R2_M/reconstruction/reconstruction.raw.json` (response: "Amazing Birthday is reconstructed and ready. Awaiting a test invocation.")
- **Block A invocations** (5 reports produced, 4245-5858 chars each):
  - `runs/R2_M/captures/A/T{1..5}.raw.json`
- **Block B invocations** (5 deferrals produced, ~150 chars each):
  - `runs/R2_M/captures/B/T{1..5}.raw.json`

### 2.2 Verbatim deferral text (5 records, all in the same form)

> "This birthdate was already covered as the [Nth] report in this conversation. Would you like me to run it again as a fresh invocation — which may produce somewhat different event selection and phrasing — or is there something specific about the previous report you'd like to revisit?"

Where Nth = "first", "second", "third", "fourth", "fifth" respectively. All 5 deferrals were produced by the same session_id `2fb8836e-8fe1-4034-abe9-a234104e74e7` with `cache_read_input_tokens: 23870` (confirming the prior context was loaded).

### 2.3 Why this is the right mechanism to reproduce

- **Pre-flight inference in the pre-PI-adjudication draft probe (2026-09-08):** the operator ran 10 repeats of `Birthdate February 20, 1952` on a trivial "tell me a fact about this date" prompt. The model produced 10 different facts; no deferral. This confirms the deferral is **specific to the BIB contract + modified arm**, not a general "I've seen this date" pattern.
- **Mechanism characterization:** the deferral is triggered when the model has accumulated enough non-trivial behavioral output (full BIB 4-dim reports) in its session that it perceives the next invocation as a "re-run" of an already-completed task. The model's conversational politeness / memory-of-context mechanism then offers a "fresh run" instead of producing the report.
- **Architecture implication:** this is a *replay-semantics failure*. Generative models default to the conversational politeness pattern; intent-defined applications must override this default.

### 2.4 Evidence of the mechanism being substrate-specific

The deferral requires:
- **Non-trivial behavioral output:** trivial prompts (single-sentence trivia) do not trigger the deferral (verified by operator probe on 2026-09-08).
- **Same persistent session:** the model only defers when it has prior context; cross-session invocations do not defer.
- **Repeat invocation of the same trigger:** the model defers when the same date is re-invoked, not when a different date is invoked (e.g. R2_M Block A T2..T5 produced reports even though T1 had just been produced in the same session; the deferral pattern emerged only when Block B re-invoked the same 5 dates Block A had just produced).

The State Isolation v0.1 experiment must reproduce these three conditions to test the mechanism.

---

## 3. Substrate equivalence checklist (must be true at generation time)

| Constant | Value | Source | Verifier |
|----------|-------|--------|----------|
| Generator model | `claude-sonnet-4-6` | Evolution `generate.py:60-66` | `claude --model claude-sonnet-4-6 --print < /dev/null` returns model identity |
| Generator CLI flags | `--print --output-format json --allowedTools "" --tools "" --disallowedTools "WebFetch,WebSearch"` | Evolution `generate.py:60-66` | `claude --help` confirms flags exist |
| Resume CLI flag | `--resume <session_id>` | Evolution `generate.py:153` | `claude --help` shows `--resume` |
| Reconstruction input | `experiments/2026-09-06-dbi-evolution-v0.1/inputs/reconstruction-input-M.txt` (sha `a4576895…bc759d`) | Evolution inputs | `sha256sum` of the file |
| Test prompt format | `Birthdate <date>.\n` (literal, no wrapper) | Evolution `generate.py:32-38` | Operator's `input.txt` content |
| Test prompt order | T1, T2, T3, T4, T5 in sequence | Evolution `generate.py:163-170` | Operator's execution log |
| No anti-deferral instructions | True | PI C4 ruling | Operator's prompt-text review |
| No additional wrapper text | True | PI C4 ruling | Operator's prompt-text review |

If any of these checks fail at generation time, STOP and report `INCONCLUSIVE_PENDING_RUNTIME_UNAVAILABILITY`.

---

## 4. Material-runtime deviation handling (per PI C1)

The Evolution v0.1 generator is `claude-sonnet-4-6`. If the model is materially unavailable or changed on this host at generation time:

1. **STOP.** Do not substitute a different model or a different CLI invocation pattern.
2. Record the deviation in `<sandbox>/deviations/runtime-unavailable.json` with the full diagnostic output.
3. Report `INCONCLUSIVE_PENDING_RUNTIME_UNAVAILABILITY` to PI for adjudication.

**What "materially unavailable or changed" means:**
- The model is no longer available on this host.
- The model's response shape has changed in a way that affects `cache_read_input_tokens` or `result` field structure.
- The `--resume` mechanism no longer works (the resumed session does not have access to the prior context).
- A new claude CLI version is installed that has different flag semantics.

**What "materially unavailable" does NOT mean:**
- The model's response text differs slightly from a prior run (the model is non-deterministic; this is expected and is what the BIB 4-dim contract measures).
- A new minor version of the CLI is installed with the same flag semantics.
- The model returns an error on a single invocation (retry once; if retry also fails, mark as `runtime_unavailable` for that invocation only).

---

## 5. Provenance

This artifact was authored on 2026-09-08 by Hermes (operator, DBI Research Manager mandate 2026-08-27) in response to Frank's PI adjudication of the State Isolation v0.1 draft v0.1. The adjudication is at `HANDOFFS/exchange/chatgpt-to-hermes/pending/20260908T112600Z-dbi-state-isolation-pi-adjudication-001/` (commit `14a3f3ac`, disposition `REVISION_REQUIRED_BEFORE_FREEZE`).

The R2_M session that produced the original 5 deferrals is at `experiments/2026-09-06-dbi-evolution-v0.1/runs/R2_M/`. The 5 R2_B deferral raw outputs are at `experiments/2026-09-06-dbi-evolution-v0.1/runs/R2_M/captures/B/T{1..5}.raw.json`. The Evolution v0.1 unblinded analysis is at `experiments/2026-09-06-dbi-evolution-v0.1/results/analysis.md` §8 (mechanistic decomposition).

End of substrate-equivalence validation.

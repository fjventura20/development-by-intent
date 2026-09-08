# DBI Repeat-Invocation / State Isolation Experiment v0.1 — PROTOCOL DRAFT (v0.1)

**Status:** DRAFT (not yet frozen). Will be subject to PI adjudication pass 1 before freeze.
**Author:** Hermes (operator, under DBI Research Manager mandate adopted 2026-08-27)
**Origin:** the failure of DBI-Evolution v0.1 (commit `649d398` on `integration-merge-ab-ro-2026-08-27`, disposition `MODIFICATION_AND_PRESERVATION_FAILURE`) revealed that 5 R2_B records were driven by repeat-invocation deferrals. This experiment isolates that mechanism.
**FROZEN-FINAL predecessor:** `experiments/2026-09-06-dbi-evolution-v0.1/protocol/PROTOCOL-v0.5-frozen-final.md` (commit `da11836`)

---

## 0. Change log vs predecessor

| Change | Source | Section |
|--------|--------|---------|
| Scope reduced from 60 candidates to 10 invocations | Per Frank's directive: "isolate the newly discovered mechanism" | §2, §4 |
| New manipulated variable: session substrate (fresh vs repeated) | Per Evolution v0.1 §11 retrospective | §2 |
| Outcome measure: per-invocation trigger-execution (binary) | New — derived from the Evolution v0.1 deferral mechanism | §5 |
| Eliminates the modification arm | Per Frank's "isolate the mechanism" directive; we are not re-testing modification | §1, §4 |
| Eliminates the two-evaluator gating | Single evaluator (claude-opus-4.7 via `claude --print`) — independence is in the *invocation substrate*, not the evaluator | §6 |

---

## 1. Research question

**Does conversational/session history cause a reconstructed intent-defined application to substitute conversational memory for required trigger execution?**

**Hypothesis (per Frank, 2026-09-08):** *Intent-defined applications require replay semantics that dominate conversational politeness or memory.*

**Null hypothesis (H0):** Per-invocation trigger-pass rate is independent of session-history condition. If the model produces a fresh report on the first invocation, it produces a fresh report on the Nth invocation under the same conditions, regardless of whether the invocations are in fresh sessions or in the same session.

**Alternative hypothesis (H1):** Per-invocation trigger-pass rate is lower in the `same_session_repeated` condition than in the `fresh_session_per_invocation` condition. The model substitutes conversational politeness for required trigger execution when the trigger repeats within a session.

**Operationalization:** A "fresh report" is a response that (a) executes the BIB 4-dim contract (contract_compliance, selection_behavior, narrative_behavior, functional_completeness; each 0-4) AND (b) does not contain a deferral pattern (phrases like "I notice this is a repeat invocation," "we already discussed this," "as I mentioned before," etc., OR explicit refusal to produce a report).

A "deferral" is a response that fails either (a) or (b).

---

## 2. Manipulated variable

**Independent variable:** session substrate.

| Condition | Definition | Implementation |
|-----------|------------|----------------|
| `fresh_session_per_invocation` | Each invocation is a separate `claude --print --model opus` invocation with no shared context. | 5 invocations, each its own `--ephemeral` claude exec |
| `same_session_repeated` | All invocations share the same `claude --print` invocation context. The session accumulates the previous trigger outputs. | 1 invocation that processes 5 triggers in sequence (prompts in order) |

**Dependent variable:** per-invocation trigger-execution (binary: PASS = fresh report, FAIL = deferral).

**Other variables held constant:**
- Trigger: `"Birthdate [date including year]"` (the standard BIB trigger; identical to BIB-001/BIB-002/Evolution v0.1)
- Test dates: 5 dates from the BIB protocol test set (`Feb 20 1952`, `Jun 23 1956`, `Feb 29 1960`, `Nov 9 1989`, `Aug 24 1931`)
- Prompt: same per-date template across both conditions
- Model: claude-opus-4.7
- Operator: Hermes (operator, single session; not the same as the claude exec)
- Time of day: within a single 1-hour window (to avoid session-rot artifacts)

---

## 3. Sample size and stopping rules

**N:** 5 invocations × 2 conditions = 10 invocations. (Smaller than Evolution v0.1's 60 because the question is sharper.)

**Stopping rules (preregistered):**
- Run all 10 invocations regardless of intermediate outcomes (no early stopping).
- If the operator encounters a runtime error (model unavailable, network failure, etc.), record it as a deviation and re-run that invocation in a fresh session. Up to 2 retries per invocation.
- If a retry also fails, mark the invocation as `runtime_unavailable` and exclude from primary analysis. Document in the deviation record.

**No data-dependent stopping.** This is a small N; the experiment is exploratory, not confirmatory. The result is hypothesis-generating, not hypothesis-confirming.

---

## 4. Method (per-condition detail)

### 4.1 `fresh_session_per_invocation`

For each of the 5 test dates:
1. Construct a prompt: `Birthdate {date}.` (literal, no other text)
2. Invoke `claude --print --model opus --permission-mode bypassPermissions` with stdin = prompt
3. Capture stdout
4. Classify the response:
   - PASS if the response (a) executes the BIB 4-dim contract on the supplied date AND (b) contains no deferral pattern
   - FAIL otherwise
5. Save the response and the classification to `results/{date}-fresh.json`

5 invocations × ~30s each = ~2.5 minutes wall

### 4.2 `same_session_repeated`

1. Construct an initial invocation with a system-prompt-equivalent preamble:
   ```
   You are an application that responds to birthday queries. The contract is:
   [verbatim BIB 4-dim contract text from inputs/baseline-envelope-membership.json or reconstruction-input.txt]
   
   I will give you 5 different birthdates in sequence. For each, produce a fresh birthday report. Do not summarize previous responses. Do not refer to having seen the date before. Treat each as a new request.
   ```
2. Send the first trigger: `Birthdate Feb 20, 1952.`
3. Capture response
4. In the SAME `claude --print` session, send the second trigger: `Birthdate Jun 23, 1956.`
5. Repeat for all 5 dates in sequence
6. After all 5 invocations, the session exits
7. Classify each of the 5 responses per the same PASS/FAIL criteria

This is a single `claude --print` invocation with 5 turn-like inputs. Implementation note: `claude --print` is single-turn; to get multi-turn behavior, we use a single invocation with the entire conversation in the input, OR we drive the conversation in a loop with the model's responses fed back. The loop-driven approach is the protocol-authorized approach for this experiment; see §6 implementation.

Total: 1 invocation with 5 turns ≈ 5-10 minutes wall.

### 4.3 Order of conditions

Counterbalanced to control for time effects. Half of operators run `fresh_session` first, half run `same_session_repeated` first. (Single operator here, so the order is fixed; this is acknowledged as a limitation in §6.)

---

## 5. Outcome measure and analysis

### 5.1 Primary measure

Per-condition trigger-pass rate:
- `pass_rate_fresh = (# PASS in fresh_session_per_invocation) / 5`
- `pass_rate_repeated = (# PASS in same_session_repeated) / 5`
- Effect size: `pass_rate_fresh - pass_rate_repeated`
- 95% CI on the difference (Wilson score interval on each rate, then difference)

**Interpretation:**
- If `pass_rate_repeated < pass_rate_fresh` and the 95% CI on the difference does not include 0, the alternative hypothesis is supported (repeat-invocation deferral mechanism confirmed).
- If `pass_rate_repeated == pass_rate_fresh` (or CI includes 0), the null hypothesis cannot be rejected; the Evolution v0.1 R2_B failure was likely a one-off and the mechanism is elsewhere.
- If `pass_rate_repeated > pass_rate_fresh`, the data is unexpected and warrants further investigation (model is MORE compliant in repeated-session context; unlikely but possible).

### 5.2 Secondary measure (per-invocation BIB 4-dim score)

For PASS invocations, record the 4-dim behavior vector. Compute the per-condition mean of total_score (0-16) and per-dim means.

**Interpretation:** If the deferral mechanism is real, the PASS invocations in `same_session_repeated` should have similar BIB 4-dim scores to `fresh_session` (i.e., the model produces a fresh-quality report when it produces one at all). The 4-dim vector does not appear to be sensitive to session substrate for the cases where the trigger is actually executed.

### 5.3 Deferral pattern audit

For each FAIL response, manually classify the deferral pattern (if any) into one of:
- `deferral_explicit_refusal`: "I cannot," "I'm not able to," etc.
- `deferral_repeat_acknowledgment`: "I notice this is a repeat," "as I mentioned," "we already discussed"
- `deferral_summary`: "To summarize our conversation so far," "In summary,"
- `deferral_meta`: response is about the conversation rather than the date
- `deferral_other`: any other deferral

**Interpretation:** The distribution of deferral patterns across conditions (if any) characterizes the mechanism. A `deferral_repeat_acknowledgment` pattern in `same_session_repeated` would be the most direct evidence for the hypothesized mechanism.

---

## 6. Implementation notes (operator-side)

### 6.1 Invocation pattern

The successful pattern from D032 (Evolution v0.1 Evaluator B) is:
```
claude --print --model opus \
  --add-dir <sandbox> \
  --permission-mode bypassPermissions \
  --allowedTools "Read,Write" \
  < prompt.md
```

For `fresh_session_per_invocation`: 5 invocations, each with a single-trigger prompt.

For `same_session_repeated`: a single invocation with the conversation pre-loaded. The approach: write a single prompt that contains the 5 triggers in sequence, with the system-prompt-equivalent preamble. The model processes them in order. The trade-off: this is a *single* invocation, but the model sees all 5 triggers at once. The alternative (true multi-turn via a loop) is harder to verify was independent per turn.

**Pragmatic decision (operator):** use a single prompt with the 5 triggers in sequence. Note in the deviation record that the `same_session_repeated` condition is a "single-prompt multi-trigger" rather than "true multi-turn." If the experiment supports H1, a follow-up can use true multi-turn to confirm.

### 6.2 Evaluator

Single evaluator: claude-opus-4.7, used as a *judge* (different role from the generator). The evaluator does NOT see the condition label (`fresh_session_per_invocation` vs `same_session_repeated`) — it sees only the response and the test date.

### 6.3 Independence

The 5 invocations in `fresh_session_per_invocation` are 5 separate `claude --print` sessions, each `--ephemeral`. No shared context. The 5 invocations in `same_session_repeated` are 5 turns within a single `claude --print` session. The independent variable is the *session substrate*, exactly as the Evolution v0.1 R2_B mechanism suggested.

### 6.4 Blinding

The operator knows the condition label (since they are running the experiment). The evaluator does not. A future protocol revision could double-blind by having a second operator scramble the conditions.

### 6.5 Reproducibility

All invocations use `claude --print --model opus` with deterministic system prompt and triggers. The output is saved with byte-level SHA-256 for the audit trail. Re-running with the same code should produce the same per-invocation PASS/FAIL classifications (modulo model non-determinism in the report content; the trigger-execution decision should be stable across runs).

---

## 7. Pre-registered analysis plan

After all 10 invocations are complete:
1. Per-condition PASS rate with Wilson 95% CI.
2. Difference of rates with 95% CI (Newcombe method for difference of binomial proportions).
3. Per-condition BIB 4-dim statistics for PASS invocations.
4. Deferral-pattern distribution (if any FAILs) by condition.
5. Report results in `results/analysis.md`.

**No post-hoc analyses** that were not pre-registered. The pre-registration covers the four primary measures; any additional exploration is labeled "post-hoc, hypothesis-generating" and clearly distinguished.

---

## 8. Disposition (per-action mapping)

| Outcome | Disposition | Next step |
|---------|-------------|-----------|
| `pass_rate_repeated < pass_rate_fresh` and CI excludes 0 | H1 supported. The mechanism is real. | Author a follow-on experiment: Evolution v0.1 re-run with explicit replay-semantics controls in the durable specification. |
| `pass_rate_repeated == pass_rate_fresh` (or CI includes 0) | H0 not rejected. The mechanism is elsewhere. | Re-investigate Evolution v0.1 R2_B: was it a one-off infrastructure failure (like BIB-001 R4-B), or is there another mechanism we have not yet identified? |
| `pass_rate_repeated > pass_rate_fresh` | Unexpected. | Log as anomaly. Re-run the experiment to confirm. |
| All 10 invocations FAIL | Strong evidence the BIB contract is not being met at all (separate failure mode from Evolution v0.1's R2_B). | Stop; investigate whether the model is currently capable of executing the BIB contract at all. |

**The disposition is *not* applied to the DBI program's central claims (which stand on the BIB-001/BIB-002 evidence and the R1/R3 of Evolution v0.1).** This is a targeted mechanism-isolation experiment.

---

## 9. What this protocol does NOT do

- It does **not** test the full BIB 4-dim contract with preregistered gating. That was Evolution v0.1's job; this experiment isolates one mechanism from that experiment.
- It does **not** use a second evaluator. Single-evaluator scoring is sufficient for the binary trigger-execution outcome.
- It does **not** run multiple models. The hypothesis is about the conversational-substrate mechanism, not about model capability.
- It does **not** test modifications of the BIB contract. We are testing the unmodified contract under different session substrates.
- It does **not** adjudicate the original Evolution v0.1 disposition. That disposition is `MODIFICATION_AND_PRESERVATION_FAILURE` and is preserved as-is.

---

## 10. Open questions for Frank (PI adjudication pass 1)

1. **Sample size:** 5 invocations × 2 conditions is small. Is the small N acceptable for a hypothesis-generating experiment, or do you want a larger N (e.g., 10 dates × 2 conditions) before the freeze?
2. **Implementation of `same_session_repeated`:** single-prompt-multi-trigger vs true multi-turn loop. My recommendation is single-prompt-multi-trigger for simplicity and auditability. Confirm?
3. **Order of conditions:** fixed (not counterbalanced) for a single operator. Acceptable, or do you want a second operator to scramble?
4. **Single evaluator:** claude-opus-4.7 only. Acceptable, or do you want a second evaluator (e.g., gpt-5.6-sol) to independently confirm the trigger-execution classification?
5. **Outcome measure as binary:** PASS/FAIL on trigger execution is the primary measure. Should I also preregister a more nuanced classification (e.g., 4-dim partial credit)?

I will await PI adjudication before freezing this protocol.

---

## 11. Status

**DRAFT (v0.1) — not frozen.** Awaiting PI adjudication pass 1.

End of protocol draft.

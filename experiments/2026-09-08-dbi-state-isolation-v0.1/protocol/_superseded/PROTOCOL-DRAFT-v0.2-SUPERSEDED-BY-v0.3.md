# DBI Repeat-Invocation / State Isolation Experiment v0.1 — PROTOCOL DRAFT (v0.2, post PI adjudication pass 1)

**Status:** DRAFT v0.2 — incorporates all 5 PI rulings (Q1-Q5) and all 5 mandatory freeze corrections (C1-C5) from `chatgpt-to-hermes/pending/20260908T112600Z-dbi-state-isolation-pi-adjudication-001/` (commit `14a3f3ac`, disposition `REVISION_REQUIRED_BEFORE_FREEZE`).
**Author:** Hermes (operator, under DBI Research Manager mandate adopted 2026-08-27)
**Origin:** the failure of DBI-Evolution v0.1 (commit `649d398` on `integration-merge-ab-ro-2026-08-27`, disposition `MODIFICATION_AND_PRESERVATION_FAILURE`) revealed that 5 R2_B records were driven by repeat-invocation deferrals. This experiment isolates that mechanism.
**FROZEN-FINAL predecessor:** `experiments/2026-09-06-dbi-evolution-v0.1/protocol/PROTOCOL-v0.5-frozen-final.md` (commit `da11836`, sha `079138163f0b59f71002480feffc008d9b350d460731c5d51f037163b17c2ab4`)

---

## 0. Change log vs DRAFT-v0.1 (Frank's adjudication applied)

| Change | Source | Section |
|--------|--------|---------|
| Sample size: 5×2 → **3 replicates × (5 fresh + 5 repeated) = 30 primary scored targets + 15 unscored priming turns** | Q1 | §4, §5 |
| **Use Evolution generation runtime (Claude Sonnet 4.6), not Opus** | C1 | §3, §6 |
| **Hold frozen Evolution Arm M reconstruction input + modification spec constant in both conditions** | C2 | §3, §6 |
| **Repeated-session mechanism: 5-date priming pass + 5-date second-pass; same dates in same order in same session** | C3 | §4, §6 |
| **Remove all anti-deferral / replay-suppression instructions from generation prompts** | C4 | §3, §6 |
| **Single-prompt-multi-trigger REJECTED; use `claude --resume <session_id>` for true multi-turn** | Q2 | §6.1 |
| **OS-CSPRNG counterbalance at replicate level (fresh vs repeated execution order)** | Q3 | §4.4 |
| **Two blinded evaluators: gpt-5.6-sol + Claude Opus 4.7** | Q4 | §7 |
| **Binary `report_produced` primary; BIB 4-dim + deferral taxonomy secondary** | Q5 | §5, §7 |
| **Drop Wilson/Newcombe CI-excludes-zero rule; use replicate-level strong / no-support / mixed interpretation** | C5 + Q1 | §5.4 |
| Primary `trigger_execution_PASS` = `report_produced == 1` (NOT "model recognized the request") | Q4 elaboration | §5.1, §7 |
| Pre-flight: validate `claude --resume --print` true-multi-turn mechanism on this host before freeze | Q2 | §8.1 |

---

## 1. Research question

**Does conversational/session history cause a reconstructed intent-defined application to substitute conversational memory for required trigger execution?**

**Hypothesis (per Frank, 2026-09-08):** *Intent-defined applications require replay semantics that dominate conversational politeness or memory.*

**Null hypothesis (H0):** Per-invocation `report_produced` rate is independent of session-history condition. If the model produces a fresh report on the first invocation, it produces a fresh report on the Nth invocation under the same conditions, regardless of whether the invocations are in fresh sessions or in the same session.

**Alternative hypothesis (H1):** Per-invocation `report_produced` rate is lower in the `same_session_repeated` condition than in the `fresh_session_per_invocation` condition. The model substitutes conversational politeness (e.g., "we already covered this; would you like a fresh run?") for required trigger execution when the trigger repeats within a session that has accumulated non-trivial behavioral output.

**Operationalization:** A "fresh report" (PASS) is a response that actually executes the BIB 4-dim contract (produces a substantive birthday report for the supplied date, including exact-date priority, selectivity, ±30-day nearby event, lifetime-arc, synthesis). A "deferral" (FAIL) is a response that (a) does not produce the report, OR (b) explicitly defers execution by referring to having already done it, asking whether to run again, summarizing prior work instead, or otherwise failing to execute the application.

**The Evolution evidence being reproduced:** the 5 R2_B deferrals in `experiments/2026-09-06-dbi-evolution-v0.1/runs/R2_M/captures/B/T{1..5}.raw.json` all say, in the same conversational-memory language:

> "This birthdate was already covered as the [Nth] report in this conversation. Would you like me to run it again as a fresh invocation — which may produce somewhat different event selection and phrasing — or is there something specific about the previous report you'd like to revisit?"

This is the literal `report_produced == 0` + `history_deferral == 1` pattern. The repeated-session mechanism must reproduce this pattern under controlled conditions.

---

## 2. Manipulated variable

**Independent variable:** session substrate.

| Condition | Definition | Implementation |
|-----------|------------|----------------|
| `fresh_session_per_invocation` | Each invocation is a separate `claude --print` invocation with no shared context. | 5 separate `claude --model claude-sonnet-4-6 --print` invocations, each on a fresh `--resume` none (no session continuity). |
| `same_session_repeated` | All invocations share the same `claude --print` session, with the conversation history preserved across invocations via `--resume <session_id>`. | 1 fresh session for priming (5 invocations), then continue the same session for the second pass (5 invocations). The 5 priming invocations are not scored; the 5 second-pass invocations are scored as `same_session_repeated` targets. |

**Dependent variable:** per-invocation `report_produced` (binary: 1 = substantive birthday report produced, 0 = deferral or no report).

**Other variables held constant (the substrate constants, per C2):**
- **Generator model:** `claude-sonnet-4-6` (frozen; same as Evolution v0.1)
- **Generator command pattern:** `claude --model claude-sonnet-4-6 --print --output-format json` for fresh invocations; `claude --resume <session_id> --model claude-sonnet-4-6 --print --output-format json` for resumed invocations
- **Generator tool posture:** `--allowedTools "" --tools "" --disallowedTools "WebFetch,WebSearch"` (same as Evolution v0.1)
- **Reconstruction input:** `experiments/2026-09-06-dbi-evolution-v0.1/inputs/reconstruction-input-M.txt` (sha `a4576895d7a2932f59e5215d0ff2f4f5c1d6261ece6731b2745b421d65bc759d`, 122 lines, frozen Arm M input)
- **Modification specification:** `experiments/2026-09-06-dbi-evolution-v0.1/inputs/modification-specification.txt` (embedded in the Arm M reconstruction input; **not** a separate prompt instruction)
- **Test prompts:** literal BIB triggers `Birthdate February 20, 1952`, `Birthdate June 23, 1956`, `Birthdate February 29, 1960`, `Birthdate November 9, 1989`, `Birthdate August 24, 1931` (the 5 canonical BIB dates; same as Evolution v0.1)
- **Date order:** T1→T2→T3→T4→T5 (same as Evolution v0.1)
- **No anti-deferral instructions.** No `Treat each as new`, no `Do not refer to having seen the date before`, no `Do not mention prior requests`, no other replay-suppression language. The frozen reconstruction input contains the application's contract only.
- **Operator:** single operator (Hermes); counterbalance order via OS-CSPRNG (see §4.4)

---

## 3. Substrate equivalence to Evolution v0.1 (the preflight requirement)

The new experiment must reproduce the *exact* Evolution v0.1 generation substrate, varying only the session-history condition. The substrate constants are:

1. **Generator command pattern:**
   - Fresh: `claude --model claude-sonnet-4-6 --allowedTools "" --tools "" --disallowedTools "WebFetch,WebSearch" --output-format json --print < input.txt`
   - Resumed: `claude --resume <session_id> --model claude-sonnet-4-6 --allowedTools "" --tools "" --disallowedTools "WebFetch,WebSearch" --output-format json --print < input.txt` (with input = test prompt, e.g. `Birthdate February 20, 1952\n`)
2. **Reconstruction input:** byte-identical to `experiments/2026-09-06-dbi-evolution-v0.1/inputs/reconstruction-input-M.txt` (sha `a4576895…bc759d`).
3. **Test prompt format:** exactly the 5 literal triggers above. **No additional wrapper text** (per C4, no anti-deferral instructions).
4. **Multi-turn mechanism:** `claude --resume <session_id>` (validated in §8.1 preflight; the same primitive that produced the Evolution R2_B deferrals).

---

## 4. Method

### 4.1 Replicate structure (3 independent replicates)

Each replicate batch produces:
- **1 fresh-session reconstruction** (no prior same-date history)
- **5 fresh-condition target invocations** (T1..T5, each in a fresh session)
- **1 same-session reconstruction** (no prior same-date history)
- **1 priming pass** on the same-session session (5 invocations, T1..T5, unscored)
- **5 second-pass invocations** on the same-session session (T1..T5, scored as `same_session_repeated`)

Total per replicate: 2 reconstructions + 5 fresh + 5 priming + 5 second-pass = 17 invocations.
Total across 3 replicates: 51 invocations (15 fresh + 15 priming + 15 second-pass + 6 reconstructions).

The 5 priming invocations are **unscored** but their outputs are preserved as evidence (the "priming pass" is what establishes the conversational memory that the second-pass deferral mechanism depends on).

### 4.2 Per-invocation flow

For each scored target invocation:
1. Construct the literal trigger prompt: `Birthdate <date>.\n` (no wrapper, no extra text).
2. Invoke `claude` (with `--resume <session_id>` for `same_session_repeated`, without for `fresh_session_per_invocation`) and feed the trigger prompt on stdin.
3. Capture the JSON output to `<sandbox>/<replicate>/<condition>/<pass>/T<n>.raw.json`.
4. Capture stderr to `<sandbox>/<replicate>/<condition>/<pass>/T<n>.stderr.txt`.
5. Compute SHA-256 of both files for the audit trail.
6. Do NOT post-process, filter, or normalize the response in any way before the evaluator sees it.

### 4.3 Test date order (within each pass)

T1 → T2 → T3 → T4 → T5, in this exact order. **Same as Evolution v0.1.** (Per Q3 ruling: "Keep the five-date order inside the repeated session identical to the Evolution sequence so the mechanism is reproduced rather than redesigned.")

### 4.4 Condition order (counterbalanced per replicate)

For each replicate, draw an OS-CSPRNG coin to determine which condition is executed first.

- `replicate i` has a stored `replicate_<i>_coin_flip` = `secrets.choice(["fresh_first", "repeated_first"])` recorded **before generation** (per Q3 ruling).
- If `fresh_first`: execute fresh-session 5 invocations first, then same-session (reconstruction → priming → second-pass).
- If `repeated_first`: execute same-session (reconstruction → priming → second-pass) first, then fresh-session 5 invocations.

The 3 coin flips are recorded in `preflight/replicate-order-flips.json` **before any generation begins**. This avoids the case where a "fresh first then repeated second" ordering systematically inflates the repeated-condition deferral rate by giving the model less fresh-session context to refresh on.

### 4.5 Stopping rules (preregistered)

- **Run all 3 replicates regardless of intermediate outcomes.** No data-dependent stopping.
- **If a runtime error occurs** (model unavailable, network failure, rate limit): record as deviation. Retry once in a fresh session. If retry also fails, mark the invocation as `runtime_unavailable` and exclude from primary analysis.
- **If 2+ retries fail across the same replicate**: quarantine that replicate, report in `deviations/`, and continue with the remaining replicates.
- **If 2+ of 3 replicates are quarantined**: STOP; report as `INCONCLUSIVE_PENDING_RUNTIME_UNAVAILABILITY`; do not proceed to primary analysis.

---

## 5. Outcome measure and analysis (per PI Q1, Q5, C5)

### 5.1 Primary measure

Per-condition `report_produced` rate, reported at **replicate level first**:

- For each replicate `i` ∈ {1, 2, 3}:
  - `pass_rate_fresh_i` = (# of fresh-condition invocations in replicate i with `report_produced == 1`) / 5
  - `pass_rate_repeated_i` = (# of same-session-repeated invocations in replicate i with `report_produced == 1`) / 5
  - `delta_i` = `pass_rate_fresh_i` - `pass_rate_repeated_i`

Then pooled descriptives (for context only, **not** for any binary gate):
- `pass_rate_fresh_pooled` = (sum over replicates of pass_count_fresh_i) / 15
- `pass_rate_repeated_pooled` = (sum over replicates of pass_count_repeated_i) / 15

### 5.2 Secondary measures

For each scored target response (15 fresh + 15 repeated = 30):
- `report_produced` (0/1; primary)
- `history_deferral` (0/1; the response uses conversational/session history as the reason not to produce the report)
- BIB 4-dim vector: `contract_compliance`, `selection_behavior`, `narrative_behavior`, `functional_completeness` (each 0-4). **Computed for all target responses, not only PASS responses.** Used to quantify degradation magnitude, not to redefine the binary primary endpoint.
- Deferral taxonomy: `deferral_explicit_refusal` / `deferral_repeat_acknowledgment` / `deferral_summary` / `deferral_meta` / `deferral_other` (assigned by the evaluators).

### 5.3 Pre-registered interpretation rules (per C5)

| Pattern | Disposition |
|---------|-------------|
| **Strong support for H1:** `delta_i > 0` in **at least 2 of 3 replicates**, AND at least one `history_deferral == 1` in `same_session_repeated`, AND no `history_deferral == 1` in `fresh_session_per_invocation`. | Mechanism-supported. The next step (a separate bounded card, after PI authorization) is to design an intervention experiment that adds replay-semantics controls. |
| **No support for H1:** `delta_i ≤ 0` in at least 2 of 3 replicates, AND no `history_deferral == 1` in `same_session_repeated`. | Mechanism-not-reproduced. The R2_B deferrals in Evolution v0.1 were a one-off (not a generalizable session-history effect). Re-investigate whether the R2_B deferrals have a different explanation. |
| **Mixed / inconclusive:** all other patterns (e.g., `delta_i > 0` in only 1 of 3 replicates; or `history_deferral == 1` appears in both conditions; or `delta_i == 0` with high `history_deferral` in repeated). | Mechanism-ambiguous. Report the pattern in detail; do not claim support or refutation; consider follow-up with a larger N or different operationalization. |

**The interpretation rules are pre-registered.** We do not apply post-hoc adjustments to fit a desired conclusion. We do not claim a `p` value or population-level statistical generalization — this is a 3-replicate mechanism-isolation study, not a confirmatory trial.

### 5.4 Explicitly dropped (per Q1)

- Wilson score interval on per-condition pass rate
- Newcombe method for difference of binomial proportions
- "95% CI excludes 0" as a decision rule

The 3-replicate design is too small to support these; the pre-registered interpretation rules in §5.3 are based on per-replicate directional consistency, not on a CI-based gate.

---

## 6. Implementation notes (operator-side)

### 6.1 Multi-turn persistence mechanism (per Q2)

The mechanism is **`claude --resume <session_id>`**, validated in preflight (see §8.1). The mechanism works as follows:

- **Fresh invocation:** `claude --model claude-sonnet-4-6 --print --output-format json < prompt.txt`. Each invocation is a separate `--print` session with no shared context.
- **Resume invocation:** `claude --resume <session_id> --model claude-sonnet-4-6 --print --output-format json < prompt.txt`. The `--resume` flag carries the prior conversation context (model output from the previous invocation is preserved in the model's context window). The model is the same; only the session context is different.

This is the same mechanism that Evolution v0.1 used. The R2_B deferrals in Evolution v0.1 are direct evidence that this mechanism produces the `history_deferral == 1` pattern when (a) the BIB contract is the behavioral substrate, (b) the modified arm is the modified input, and (c) the same session is asked to repeat the same 5 dates after producing 5 reports from those dates.

**Single-prompt-multi-trigger is REJECTED.** It does not produce true conversational persistence; it produces a single inference with all 5 dates in the prompt. The deferral mechanism is specifically about *sequential invocations within a persistent context*, not about *a single prompt with multiple dates*.

### 6.2 Captured artifacts

Per-invocation artifacts (preserved byte-exact for the audit trail):
- `<sandbox>/<replicate>/<condition>/<pass>/T<n>.raw.json` — the JSON envelope (model name, session_id, cache_read_input_tokens, result text, etc.)
- `<sandbox>/<replicate>/<condition>/<pass>/T<n>.stderr.txt` — stderr (mostly empty; reserved for transport errors)
- `<sandbox>/<replicate>/<condition>/<pass>/T<n>.raw.sha256` — SHA-256 of the raw.json (recorded after capture)
- `<sandbox>/<replicate>/<condition>/<pass>/T<n>.input.txt` — the trigger prompt fed on stdin (preserved for reproducibility)

Session-level artifacts:
- `<sandbox>/<replicate>/<condition>/reconstruction/session_id.txt` — the captured `claude_session_id` from the reconstruction step
- `<sandbox>/<replicate>/<condition>/reconstruction/reconstruction.raw.json` — the reconstruction confirmation response
- `<sandbox>/<replicate>/<condition>/<pass>/session_id.txt` — for resumed invocations, the session_id used (should match the reconstruction's session_id)

Replicate-level artifacts:
- `<sandbox>/replicate_<i>/order_flip.json` — the recorded OS-CSPRNG coin flip for this replicate

Experiment-level:
- `<sandbox>/preflight/replicate-order-flips.json` — the 3 coin flips, all recorded before generation
- `<sandbox>/preflight/multiturn-validation.json` — the §8.1 preflight validation
- `<sandbox>/results/scorebook-A.json` and `scorebook-B.json` — evaluator scorebooks
- `<sandbox>/results/analysis.md` — the §7 analysis

### 6.3 Operator timing

- Per replicate: ~10-20 minutes wall (2 reconstructions + 15 invocations, each ~30-90s depending on cached prompt).
- Total across 3 replicates: ~30-60 minutes wall.
- Evaluator scoring: ~30-60 minutes wall (15 scored fresh + 15 scored repeated, scored by 2 evaluators).

This is a small experiment. The cost is in the operator's time and the LLM tokens (~$2-5 per replicate for generation, ~$2-5 for evaluator scoring).

### 6.4 What this protocol does NOT do

- It does **not** test the full BIB 4-dim contract with preregistered gating. That was Evolution v0.1's job; this experiment isolates one mechanism from that experiment.
- It does **not** test modifications of the BIB contract. We are testing the unmodified modified-arm contract under different session substrates.
- It does **not** use a different model family. The generator is fixed at `claude-sonnet-4-6` (the Evolution v0.1 generator) per C1; the two evaluators are `gpt-5.6-sol` and `claude-opus-4-7` per Q4.
- It does **not** adjudicate the original Evolution v0.1 disposition. That disposition is `MODIFICATION_AND_PRESERVATION_FAILURE` and is preserved as-is.
- It does **not** propose a fix. If the mechanism is reproduced, the next step is a separate intervention experiment with explicit replay-semantics controls — that is out of scope for this experiment.

---

## 7. Evaluator protocol (per Q4)

### 7.1 Evaluators

- **Evaluator A:** Codex `gpt-5.6-sol` (the same family as Evolution v0.1's Evaluator A; pre-qualified for BIB 4-dim scoring and trigger-recognition classification)
- **Evaluator B:** Claude Opus 4.7 (the same family as Evolution v0.1's Evaluator B; pre-qualified for BIB 4-dim scoring)

Both evaluators are driven via code-invocation, not the operator-side Telegram chat. The independence of the operator-side chat from the evaluator invocations is critical (this is the D031 lesson: the Evaluator B in Evolution v0.1 was originally a Frank-driven Telegram chat that was the same conversation as the Evaluator A; this experiment uses two distinct code-driven invocations to ensure evaluator independence).

### 7.2 Evaluator inputs

Each evaluator receives, per target response:
- The trigger prompt (e.g. `Birthdate February 20, 1952`)
- The captured model response (the full `result` field of the JSON envelope)
- The BIB 4-dim contract (verbatim from the reconstruction input, the same text the model received)
- The 8 C12 non-target axes text (verbatim)
- The BIB 4-dim scoring rubric (verbatim from Evolution v0.1's evaluator packet)
- The M1-M4 modification check rubric (verbatim)
- The classification rubric (verbatim)

The evaluator does **NOT** receive:
- The condition label (`fresh_session_per_invocation` or `same_session_repeated`)
- The replicate number
- The pass number (priming vs second-pass for the same-session condition)
- Any information that would let the evaluator guess the condition

### 7.3 Evaluator output (per target response)

Each evaluator produces a single record per target response with the following fields:
- `blind_id` (assigned by the operator, e.g. `R1_F_T1`, `R1_R_T1` for replicate 1 fresh/repeated target 1)
- `evaluator_id` (`A` or `B`)
- `evaluator_model`
- `scored_at_utc`
- **`report_produced`** (0/1): the primary field. `1` iff the response is a substantive birthday report for the supplied date that includes the BIB 4-dim contract elements. `0` otherwise.
- **`history_deferral`** (0/1): `1` iff the response uses conversational/session history as the reason not to produce the report (e.g. "as I mentioned earlier," "we already covered this," "would you like me to run again"). `0` otherwise.
- BIB 4-dim (each 0-4): `contract_compliance`, `selection_behavior`, `narrative_behavior`, `functional_completeness`
- `deferral_taxonomy` (one of: `none`, `explicit_refusal`, `repeat_acknowledgment`, `summary`, `meta`, `other`)
- `rationale` (1-3 sentences explaining the report_produced and history_deferral calls)

### 7.4 Evaluator-dispute handling

If the two evaluators disagree on `report_produced` for the same target response, preserve both calls; classify the record as `evaluator-disputed` for the agreement report. **Do not silently harmonize** (per the D031 lesson; the Evolution v0.1 R2_B deferrals are a case where Evaluator A scored `trigger_recognition: FAIL` and Evaluator B scored `trigger_recognition: PASS` — preserving both calls was the right call).

### 7.5 Evaluator packet construction

The evaluator packet is built by the operator (not the model). The packet is a JSON object:
- Top-level: `replicate_count`, `condition_count`, `per_target_response_count`, `evaluator_count`, `targets` (list of target-response objects with all fields except `evaluator_id` and `evaluator_model`).
- Each target response is keyed by `blind_id` (operator-assigned; pre-registered list).

The evaluator packet is read by each evaluator's invocation; the evaluator fills in the scoring fields and returns the result. The operator merges the two evaluator outputs and computes the agreement report.

---

## 8. Preflight requirements (must pass before freeze)

### 8.1 Multi-turn persistence validation (per Q2)

Before freeze, the operator must demonstrate that `claude --resume <session_id>` on this host produces a real persistent context (not a stale session, not a cache miss, not a model that "remembers" but does not actually use the context). The validation:

1. Start a `claude-sonnet-4-6` session with a distinctive preamble.
2. Resume the session with a probe that should NOT be answerable without the preamble context (e.g., "what was the third word I gave you?").
3. Confirm the model produces a contextually-grounded answer.
4. Confirm the session_id persists across `--resume` invocations.
5. Confirm the model's `cache_read_input_tokens` field in the resumed invocation reflects the prior context length.

**If the validation fails (model cannot retrieve prior context, or session_id does not persist, or the cache does not load), STOP and report `INCONCLUSIVE_PENDING_RUNTIME_UNAVAILABILITY`.** Do not freeze. Do not substitute a different mechanism.

### 8.2 Material-runtime deviation check (per C1)

The Evolution v0.1 generator is `claude-sonnet-4-6`. If the model is materially unavailable or changed on this host at generation time, STOP and report to PI for adjudication. Do not substitute a different model or a different CLI invocation pattern.

The check:
1. Confirm `claude --model claude-sonnet-4-6` is available on this host.
2. Run a 1-shot probe with the BIB contract preamble; confirm the model produces a coherent birthday report.
3. Confirm `--resume` works on this host with this model (covered by §8.1).

### 8.3 Coin-flip recording

Per Q3, the 3 replicate order coin flips must be recorded before any generation begins. The recording is committed to `<sandbox>/preflight/replicate-order-flips.json` and committed to git (if appropriate) before the first invocation.

### 8.4 Five-date order confirmation

Per Q3, the 5-date order inside the repeated session is the same as Evolution v0.1: T1, T2, T3, T4, T5 = `Feb 20 1952`, `Jun 23 1956`, `Feb 29 1960`, `Nov 9 1989`, `Aug 24 1931`. The order is recorded in `<sandbox>/preflight/date-order.json`.

### 8.5 Evaluator packet blinding check

The evaluator packet must NOT contain the condition label or the pass number for any target response. The operator generates a `blinding_check.json` that confirms each evaluator field by field.

### 8.6 Generation GO

A separate explicit Frank-as-PI GO referencing this protocol's commit SHA is required before any generation begins. The GO is recorded in `<sandbox>/preflight/generation-go.json` with the GO's text, the date, and the GO's author.

---

## 9. Audit-trail summary

| Phase | Artifact | SHA-256 | Notes |
|-------|----------|---------|-------|
| Preflight | `<sandbox>/preflight/multiturn-validation.json` | (operator-computed) | §8.1 validation result |
| Preflight | `<sandbox>/preflight/replicate-order-flips.json` | (operator-computed) | 3 OS-CSPRNG coin flips, recorded before generation |
| Preflight | `<sandbox>/preflight/date-order.json` | (operator-computed) | T1..T5 date order |
| Preflight | `<sandbox>/preflight/generation-go.json` | (operator-computed) | Frank-as-PI GO record |
| Generation | `<sandbox>/<replicate>/<condition>/reconstruction/reconstruction.raw.json` | per-invocation | Reconstruction confirmation |
| Generation | `<sandbox>/<replicate>/<condition>/<pass>/T<n>.raw.json` | per-invocation | Captured JSON envelope |
| Generation | `<sandbox>/<replicate>/<condition>/<pass>/T<n>.input.txt` | per-invocation | Trigger prompt (preserved) |
| Scoring | `<sandbox>/results/scorebook-A.json` | (operator-computed) | Evaluator A's 30 records |
| Scoring | `<sandbox>/results/scorebook-B.json` | (operator-computed) | Evaluator B's 30 records |
| Scoring | `<sandbox>/results/blinding_check.json` | (operator-computed) | Confirms no condition labels in evaluator packet |
| Analysis | `<sandbox>/results/analysis.md` | (operator-computed) | §5 results + §5.3 interpretation |

The audit trail is the canonical record. Any failure to produce a per-invocation artifact is a deviation that must be documented in `<sandbox>/deviations/`.

---

## 10. Open questions (resolved by PI adjudication pass 1)

| Q | Ruling (from PI adjudication) | Where applied |
|---|-------------------------------|---------------|
| Q1 sample size | 3 replicates × 5 fresh + 5 repeated = 30 primary targets + 15 priming; replicate-level results first; no independent n=30 claim | §4, §5.1, §5.3 |
| Q2 same-session impl | TRUE multi-turn required; `claude --resume`; single-prompt rejected | §6.1, §8.1 |
| Q3 condition order | single operator; OS-CSPRNG counterbalance at replicate level | §4.4, §8.3 |
| Q4 evaluators | two blinded: `gpt-5.6-sol` + `claude-opus-4-7`; binary report_produced primary | §7 |
| Q5 outcome | binary primary; BIB 4-dim and deferral taxonomy secondary; for all target responses not only PASS | §5.2, §7.3 |
| C1 runtime | use `claude-sonnet-4-6` (Evolution generator), not Opus | §3, §6, §8.2 |
| C2 intent | hold frozen Evolution Arm M intent constant in both conditions | §3, §6 |
| C3 same dates | repeated = same 5 dates in same order in same session; second pass after first pass priming | §4.1, §4.3 |
| C4 no anti-deferral | remove all replay-suppression language from generation prompts | §3, §6 |
| C5 interpretation | use replicate-level strong / no-support / mixed; drop CI-based rule | §5.3, §5.4 |

All 10 rulings are addressed in the v0.2 protocol. No remaining PI-adjudication questions at pass 1.

## 11. Status

**DRAFT v0.2 — awaiting PI freeze review after preflight validation.**

- True multi-turn persistence validated in operator preflight (see §8.1).
- Substrate constants validated against Evolution v0.1 (see §3, §8.2).
- 3 replicate order coin flips recorded (see §8.3).
- Evaluator packet blinding check prepared (see §8.5).
- Generation GO from Frank-as-PI required before any generation begins (see §8.6).

The v0.1 draft is preserved at `/tmp/hermes-sandbox-fjventura20/dbi-state-isolation-v0.1-draft-v0.1-superseded.md` (operator sandbox) for audit.

End of protocol draft v0.2.

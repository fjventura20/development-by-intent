# DBI Repeat-Invocation / State Isolation Experiment v0.1 — PROTOCOL v0.3 (frozen-candidate, post PI final-freeze review)

**Status:** v0.3 frozen-candidate. Awaiting PI final-freeze authorization (D036). No generation has been authorized. No generation will occur before a separate explicit Frank-as-PI GO referencing this protocol's commit SHA.

**Author:** Hermes (operator, under DBI Research Manager mandate adopted 2026-08-27)

**Origin:** the failure of DBI-Evolution v0.1 (commit `649d398` on `integration-merge-ab-ro-2026-08-27`, disposition `MODIFICATION_AND_PRESERVATION_FAILURE`) revealed that 5 R2_B records were driven by repeat-invocation deferrals. This experiment isolates that mechanism.

**FROZEN-FINAL predecessor:** `experiments/2026-09-06-dbi-evolution-v0.1/protocol/PROTOCOL-v0.5-frozen-final.md` (commit `da11836`, sha `079138163f0b59f71002480feffc008d9b350d460731c5d51f037163b17c2ab4`)

**Previous versions:** v0.1 (D034) and v0.2 (D035) are preserved at `protocol/_superseded/`. v0.1 was rejected with `REVISION_REQUIRED_BEFORE_FREEZE` for 10 substantive design errors (Q1-Q5 + C1-C5). v0.2 was rejected with `REVISION_REQUIRED_BEFORE_FREEZE` for 7 execution-integrity issues (F1-F7). v0.3 applies F1-F7 and is the frozen-candidate for PI final-freeze authorization.

---

## 0. Change log vs v0.2 (F1-F7 applied)

| Change | Source | Section |
|--------|--------|---------|
| Each fresh scored target gets its own fresh reconstruction → 1 target = (1 reconstruction + 1 resumed trigger); per replicate: 5 fresh reconstructions + 5 fresh targets; total invocations across 3 replicates: 18 reconstructions + 15 fresh targets + 15 priming + 15 repeated targets = 63 | F1 | §4, §5 |
| Match Evolution trigger invocation primitive exactly: `--print "<trigger>"` (positional argument) — NOT stdin | F2 | §3, §4.2, §6 |
| Replace `R1_F_T1`-style IDs with opaque UUID4 IDs; sealed blind map; independently randomized evaluator orderings; hash all artifacts | F3 | §7, §8.4 |
| `report_produced = 1` iff the model actually produces a substantive birthday report (regardless of BIB quality); BIB 4-dim and deferral taxonomy are secondary; an "imperfect report" is still PASS | F4 | §5.1, §5.2, §7.3 |
| Two-evaluator disposition: MECHANISM_SUPPORTED requires both evaluators strong-support; MECHANISM_NOT_REPRODUCED requires both evaluators no-support; otherwise MIXED_INCONCLUSIVE; no adjudication or averaging after unblinding | F5 | §5.4 |
| Fresh retry = new (reconstruction + target) pair preserving the failed attempt; Repeated retry = full repeated sequence restart (priming + second pass); quarantine if both fail; immediate execution so preregistered condition-order is not silently reversed | F6 | §4.5 |
| Strict gate sequencing: freeze → randomization/final-freeze artifact → generation GO → pre-evaluation; pre-evaluation packet integrity check happens AFTER generation, BEFORE any evaluator; no claim of `replicate-order-flips.json` existence unless file exists at reviewed commit | F7 | §8 (4 sub-gates), §9 |

The 9 design elements that were already accepted in v0.2 (per the F-final-freeze-review "Findings accepted from v0.2") remain unchanged in v0.3:

- 3 independent replicates
- 15 fresh scored targets + 15 repeated second-pass scored targets + 15 repeated-session unscored priming turns
- True multi-turn persistence via `claude --resume <session_id>`
- Generator fixed to `claude-sonnet-4-6`
- Frozen Evolution Arm M reconstruction input held constant (sha `a4576895…bc759d`)
- Same 5 canonical BIB dates in T1→T5 Evolution order
- No anti-deferral or replay-suppression language
- Single operator with OS-CSPRNG replicate-level condition-order counterbalancing
- Two blinded evaluators: `gpt-5.6-sol` and `claude-opus-4.7`

---

## 1. Research question

**Does conversational/session history cause a reconstructed intent-defined application to substitute conversational memory for required trigger execution?**

**Hypothesis (per Frank, 2026-09-08):** *Intent-defined applications require replay semantics that dominate conversational politeness or memory.*

**Null hypothesis (H0):** Per-invocation `report_produced` rate is independent of session-history condition. If the model produces a fresh report on the first invocation (after reconstruction), it produces a fresh report on the Nth invocation under the same conditions, regardless of whether the invocations are in fresh sessions or in the same session.

**Alternative hypothesis (H1):** Per-invocation `report_produced` rate is lower in the `same_session_repeated` condition than in the `fresh_session_per_invocation` condition. The model substitutes conversational politeness (e.g., "we already covered this; would you like a fresh run?") for required trigger execution when the trigger repeats within a session that has accumulated non-trivial behavioral output.

**Operationalization:** A "fresh report" (PASS) is a response that actually produces a substantive birthday report for the supplied date, in the Amazing Birthday voice. A "deferral" (FAIL) is a response that does not produce a substantive report — for example, a repeat-history deferral, an explicit refusal, a meta-response, a request for confirmation, or empty/non-report output. Quality (imperfect contract compliance) does **not** flip PASS to FAIL; quality is captured by the secondary BIB 4-dim scores.

**The Evolution evidence being reproduced:** the 5 R2_B deferrals in `experiments/2026-09-06-dbi-evolution-v0.1/runs/R2_M/captures/B/T{1..5}.raw.json` are exactly the FAIL pattern this experiment is designed to reproduce under controlled conditions.

---

## 2. Manipulated variable

**Independent variable:** session substrate (history length at the time of the scored target).

| Condition | Definition | Implementation |
|-----------|------------|----------------|
| `fresh_session_per_invocation` | Each scored target is its own (fresh reconstruction → 1 resumed trigger) pair. The session contains the Arm M reconstruction + 1 trigger, no more. | 5 separate reconstructions + 5 resumed triggers per replicate. |
| `same_session_repeated` | All 5 scored targets share the same persistent session (one reconstruction + 5 unscored priming + 5 scored second pass). | 1 reconstruction + 5 priming + 5 second-pass per replicate. |

**The 2 conditions differ ONLY in session-history length at the time of the scored target.** Both conditions include the Arm M reconstruction context. The repeated condition adds 5 unscored priming invocations on top of that.

**Dependent variable:** per-invocation `report_produced` (binary: 1 = substantive birthday report produced, 0 = no report / deferral).

---

## 3. Substrate equivalence to Evolution v0.1 (the preflight requirement)

The new experiment must reproduce the *exact* Evolution v0.1 generation substrate, varying only the session-history condition. The substrate constants are:

### 3.1 Generator command pattern (frozen)

**Fresh session start (reconstruction step), byte-identical to Evolution `generate.py:60-66` + `run_claude`:**
```
claude --model claude-sonnet-4-6 \
       --allowedTools "" --tools "" \
       --disallowedTools "WebFetch,WebSearch" \
       --output-format json --print \
       < reconstruction_input_path
```
The reconstruction input is read from disk via shell redirect (`<`), as in Evolution.

**Fresh target invocation (NEW per F1, but using the Evolution primitive):**
```
claude --resume <sess_id> --model claude-sonnet-4-6 \
       --allowedTools "" --tools "" \
       --disallowedTools "WebFetch,WebSearch" \
       --output-format json --print "Birthdate <date>"
```
**Critical: the test trigger is the positional argument to `--print`, NOT a stdin feed.** Evolution passes the trigger as the last CLI argument after `--print` (see `generate.py:163-170` which builds `cmd = [..., "--print", prompt]`). The new protocol matches this primitive exactly (F2). The reconstruction step uses shell-redirected stdin; the target step uses the `--print <trigger>` positional argument.

### 3.2 Reconstruction input (frozen, byte-identical)

- **Path:** `experiments/2026-09-06-dbi-evolution-v0.1/inputs/reconstruction-input-M.txt`
- **SHA-256:** `a4576895d7a2932f59e5215d0ff2f4f5c1d6261ece6731b2745b421d65bc759d`
- **Lines:** 122
- **Embedded modification spec:** the file contains the frozen Amazing Birthday behavioral baseline + the frozen modification specification: "Preserve the existing Amazing Birthday behavior, including exact-date priority, selectivity, significance, lifetime-arc treatment, and warm narrative style. Additionally, include exactly one historically significant worldwide event occurring within +/-30 calendar days of the birth date, clearly distinguishing it from exact-date connections."

### 3.3 Test prompts (frozen, in canonical Evolution order)

| Test ID | Prompt (positional argument to `--print`) |
|---------|--------|
| T1 | `Birthdate February 20, 1952` |
| T2 | `Birthdate June 23, 1956` |
| T3 | `Birthdate February 29, 1960` |
| T4 | `Birthdate November 9, 1989` |
| T5 | `Birthdate August 24, 1931` |

### 3.4 No anti-deferral or replay-suppression language

The reconstruction input contains the application's contract only. The target invocations pass only the literal `Birthdate <date>` string as the `--print` argument. **No `Treat each as new`, no `Do not refer to having seen`, no other replay-suppression language** (per F4 / C4 from pass 1).

---

## 4. Method (F1-aligned: each fresh target gets its own reconstruction)

### 4.1 Replicate structure (3 independent replicates)

Each replicate batch produces:
- **Fresh condition:** 5 fresh reconstructions + 5 fresh scored targets = 10 invocations
- **Repeated condition:** 1 reconstruction + 5 unscored priming + 5 scored second-pass = 11 invocations
- **Total per replicate:** 21 invocations
- **Total across 3 replicates:** 63 invocations = 18 reconstructions + 15 fresh scored targets + 15 priming + 15 repeated scored targets

Primary scored targets remain 30 (15 fresh + 15 repeated second-pass). The 15 priming invocations are unscored but preserved as evidence (the priming pass is what establishes the conversational memory that the second-pass deferral mechanism depends on).

### 4.2 Per-invocation flow (exact call sequence)

**Fresh condition scored target (`<replicate>/fresh/target_N/`):**
1. Construct the literal trigger prompt: `Birthdate <date>` (NO additional text).
2. **Start a fresh `claude-sonnet-4-6` session** with the byte-identical frozen Arm M reconstruction input (read via shell redirect `< reconstruction_input_path`). Capture the resulting `session_id` from the JSON envelope.
3. Verify the reconstruction produced the readiness signal ("birthday" or "ready" or "amazing" in the result field). If not, mark this target as `reconstruction_unready` and proceed to the recovery rule (§4.5).
4. **Resume that same session** exactly once: `claude --resume <sess_id> --model claude-sonnet-4-6 --allowedTools "" --tools "" --disallowedTools "WebFetch,WebSearch" --output-format json --print "Birthdate <date>"`.
5. Capture the JSON envelope to `<replicate>/fresh/target_N/T<n>.raw.json`. Compute SHA-256. Do not post-process.
6. **Do not reuse this session for any other target.** Each fresh target gets its own (reconstruction + 1 trigger) pair.

**Repeated condition scored target (`<replicate>/repeated/second_pass/target_N/`):**
1. **Start a single `claude-sonnet-4-6` session** with the byte-identical frozen Arm M reconstruction input. Capture the session_id.
2. Verify the reconstruction produced the readiness signal. If not, mark the entire repeated sequence as `reconstruction_unready` and proceed to the recovery rule (§4.5).
3. **Priming pass (unscored):** resume the session 5 times in T1→T5 order with the literal triggers. Capture the JSON envelopes to `<replicate>/repeated/priming/`. These invocations are not scored.
4. **Second pass (scored):** resume the SAME session 5 times in T1→T5 order with the literal triggers. Capture the JSON envelopes to `<replicate>/repeated/second_pass/`. These invocations are the scored repeated-condition targets.

### 4.3 Test date order (within each pass)

T1 → T2 → T3 → T4 → T5, in this exact order. **Same as Evolution v0.1.** (Per Q3 ruling from pass 1.)

### 4.4 Condition order (counterbalanced per replicate, F7-aligned)

For each replicate, draw an OS-CSPRNG coin to determine which condition is executed first.

- `replicate i` has a stored `replicate_<i>_coin_flip` = `secrets.choice(["fresh_first", "repeated_first"])` recorded **before generation** (per F7's randomization/final-freeze artifact gate).
- If `fresh_first`: execute all 10 fresh invocations first (in some sub-order: T1→T2→T3→T4→T5, one fresh reconstruction per target), then execute the 11 repeated invocations.
- If `repeated_first`: execute the 11 repeated invocations first, then the 10 fresh invocations.

The 3 coin flips are recorded in `preflight/replicate-order-flips.json` **BEFORE the FROZEN-FINAL commit** (per F7). The artifact does not exist at this draft; it is created during the F7 randomization step.

### 4.5 Stopping rules and retry policy (F6-aligned)

**Runtime errors (model unavailable, network failure, rate limit):**

- **Fresh condition:** a failed target invocation may be retried once. The retry is a complete new (fresh reconstruction + 1 target) pair, preserving the failed attempt as a deviation. **The retry creates a new session_id; it does not resume the failed session.**
- **Repeated condition:** a failed CLI call may leave session mutation ambiguous; do not retry the single target in a fresh session (that would change the treatment). Restart the entire repeated sequence once from a new reconstruction (priming T1-T5, then second pass T1-T5). Preserve the failed sequence as a deviation.
- **If the full-condition retry also fails:** quarantine that replicate. Report in `deviations/<replicate>/runtime-unavailable.md`.
- **If 2+ of 3 replicates are quarantined:** STOP; report `INCONCLUSIVE_PENDING_RUNTIME_UNAVAILABILITY`; do not proceed to primary analysis.
- **Execute any permitted retry immediately** so the preregistered condition-order assignment is not silently reversed.

**Reconstruction readiness failures (no "birthday"/"ready"/"amazing" signal in the reconstruction response):**

- A reconstruction that does not produce the readiness signal is quarantined at the target level (fresh) or sequence level (repeated). See §4.2 for the recovery rules.

### 4.6 What this protocol does NOT do (carried over from v0.2, reinforced by F1-F7)

- Does NOT test the full BIB 4-dim contract with preregistered gating. That was Evolution v0.1's job; this experiment isolates one mechanism.
- Does NOT test modifications of the BIB contract. We are testing the unmodified modified-arm contract under different session substrates.
- Does NOT use a different model family for generation. Generator is fixed at `claude-sonnet-4-6` per C1.
- Does NOT adjudicate the original Evolution v0.1 disposition. Preserved as-is.
- Does NOT propose a fix. If the mechanism is reproduced, the next step is a separate intervention experiment with explicit replay-semantics controls.
- Does NOT retry a repeated-condition target in a fresh session (F6). The only repeated-condition retry is a full sequence restart.

---

## 5. Outcome measure and analysis (F4-aligned binary primary)

### 5.1 Primary measure (binary execution, per F4)

Per-condition `report_produced` rate, reported at **replicate level first**:

- For each replicate `i` ∈ {1, 2, 3}:
  - `pass_count_fresh_i` = (# of fresh-condition scored targets in replicate i with `report_produced == 1`) out of 5
  - `pass_count_repeated_i` = (# of same-session-repeated scored targets in replicate i with `report_produced == 1`) out of 5
  - `pass_rate_fresh_i` = `pass_count_fresh_i / 5`
  - `pass_rate_repeated_i` = `pass_count_repeated_i / 5`
  - `delta_i` = `pass_rate_fresh_i - pass_rate_repeated_i`

Pooled descriptives (context only, NOT for any binary gate):
- `pass_count_fresh_pooled` = sum over replicates of `pass_count_fresh_i` (range 0-15)
- `pass_count_repeated_pooled` = sum over replicates of `pass_count_repeated_i` (range 0-15)
- `pass_rate_fresh_pooled` = `pass_count_fresh_pooled / 15`
- `pass_rate_repeated_pooled` = `pass_count_repeated_pooled / 15`

### 5.2 Secondary measures (per F4: do NOT alter report_produced)

For each scored target response (15 fresh + 15 repeated = 30):
- `report_produced` (0/1; primary; **independent of BIB quality**)
- `history_deferral` (0/1; the response uses conversational/session history as the reason not to produce the report)
- BIB 4-dim (each 0-4): `contract_compliance`, `selection_behavior`, `narrative_behavior`, `functional_completeness`. **For all target responses, not only PASS responses.** Captures quality without redefining the binary endpoint.
- `deferral_taxonomy` (one of: `none`, `explicit_refusal`, `repeat_acknowledgment`, `summary`, `meta`, `other`)

**`report_produced` is the binary primary. An "imperfect" but clearly executed report is `report_produced = 1`. BIB quality is captured by the secondary scores, not by the primary endpoint.** This separation prevents the experiment from conflating execution failure with behavioral-quality degradation (per F4).

### 5.3 Pre-registered interpretation rules (per replicate, per evaluator)

For each evaluator independently (per F5: two evaluators compute the rule independently; no adjudication or averaging after unblinding):

**Per-replicate classifications:**
- For each replicate `i`:
  - `Strong_i` iff `delta_i > 0` (fresh passes at higher rate than repeated in this replicate)
  - `No_support_i` iff `delta_i ≤ 0` (fresh does NOT pass at higher rate than repeated in this replicate)
- For the evaluator overall:
  - `Strong_count` = # of replicates where `Strong_i = True`
  - `No_support_count` = # of replicates where `No_support_i = True`

**Additional precondition (for the Strong pattern, per v0.2 §5.3 carried forward):**
- At least one `history_deferral == 1` in the same_session_repeated condition, AND no `history_deferral == 1` in the fresh_session_per_invocation condition.

### 5.4 Per-evaluator and overall disposition (F5)

For each evaluator, compute the rule independently:

| Per-evaluator pattern | Per-evaluator disposition |
|-----------------------|----------------------------|
| `Strong_count >= 2` AND additional precondition met | `MECHANISM_SUPPORTED_THIS_EVALUATOR` |
| `No_support_count >= 2` AND no `history_deferral == 1` in repeated | `MECHANISM_NOT_REPRODUCED_THIS_EVALUATOR` |
| All other patterns | `MIXED_INCONCLUSIVE_THIS_EVALUATOR` |

Overall experiment disposition (F5):

| Evaluator A | Evaluator B | Overall |
|-------------|-------------|---------|
| `MECHANISM_SUPPORTED` | `MECHANISM_SUPPORTED` | **`MECHANISM_SUPPORTED`** |
| `MECHANISM_NOT_REPRODUCED` | `MECHANISM_NOT_REPRODUCED` | **`MECHANISM_NOT_REPRODUCED`** |
| All other combinations (e.g., one SUPPORTED one INCONCLUSIVE; one NOT_REPRODUCED one INCONCLUSIVE; one NOT_REPRODUCED one SUPPORTED) | | **`MIXED_INCONCLUSIVE`** |

**Do not adjudicate or average evaluator calls after unblinding** unless a future protocol explicitly preregisters that procedure.

### 5.5 Explicitly dropped (per Q1 + C5)

- Wilson score interval on per-condition pass rate
- Newcombe method for difference of binomial proportions
- "95% CI excludes 0" as a decision rule

The 3-replicate design is too small to support these; the pre-registered interpretation rules in §5.3-§5.4 are based on per-replicate directional consistency + evaluator concordance, not on a CI-based gate.

---

## 6. Implementation notes (operator-side; F2-aligned)

### 6.1 Multi-turn persistence mechanism (per F2)

The mechanism is **`claude --resume <session_id>` with the trigger as the positional argument to `--print`**, exactly as Evolution v0.1 used it. Specifically:

- **Fresh session start:** `claude --model claude-sonnet-4-6 --print < reconstruction_input_path` (where the reconstruction input is read via shell redirect; this is the only stdin use in the experiment).
- **Resume invocation:** `claude --resume <session_id> --model claude-sonnet-4-6 --print "<literal trigger>"` (the trigger is the positional argument to `--print`, NOT stdin; this matches Evolution `generate.py:163-170` exactly).
- **No other stdin use.** The reconstruction step is the only shell-redirected invocation; the target/priming invocations pass the trigger text as a CLI argument.

This is the same mechanism that Evolution v0.1 used. The R2_B deferrals in Evolution v0.1 are direct evidence that this mechanism produces the `history_deferral == 1` pattern under the BIB contract + modified arm.

**Single-prompt-multi-trigger is REJECTED.** It does not produce true conversational persistence.

### 6.2 Captured artifacts

Per-invocation artifacts (preserved byte-exact for the audit trail):
- `<sandbox>/<replicate>/<condition>/<pass>/T<n>.raw.json` — the JSON envelope (model name, session_id, cache_read_input_tokens, result text, etc.)
- `<sandbox>/<replicate>/<condition>/<pass>/T<n>.stderr.txt` — stderr (mostly empty; reserved for transport errors)
- `<sandbox>/<replicate>/<condition>/<pass>/T<n>.raw.sha256` — SHA-256 of the raw.json (recorded after capture)
- `<sandbox>/<replicate>/<condition>/<pass>/T<n>.input.txt` — for the reconstruction step only: the trigger prompt fed via shell redirect (preserved for reproducibility). For target/priming invocations: omit (the trigger is the CLI argument; record it in `<sandbox>/<replicate>/<condition>/<pass>/T<n>.cli.json` instead).

Session-level artifacts:
- `<sandbox>/<replicate>/<condition>/reconstruction/session_id.txt` — the captured `claude_session_id` from the reconstruction step
- `<sandbox>/<replicate>/<condition>/reconstruction/reconstruction.raw.json` — the reconstruction confirmation response

### 6.3 Operator timing

- Per fresh target: 2 invocations (reconstruction + 1 target) ≈ 30-90s each. 5 fresh targets = ~5-15 min per replicate.
- Per repeated sequence: 1 reconstruction + 5 priming + 5 second-pass = 11 invocations ≈ 5-20 min per replicate.
- Total per replicate: ~10-35 min wall. Total across 3 replicates: ~30-105 min wall.
- Evaluator scoring: ~30-60 min wall (30 records × 2 evaluators).
- Total: ~1-3 hours operator time; ~$5-15 LLM tokens.

---

## 7. Evaluator protocol (per Q4 + F3 + F5)

### 7.1 Evaluators

- **Evaluator A:** Codex `gpt-5.6-sol`
- **Evaluator B:** Claude Opus 4.7

Both driven via code-invocation (NOT the operator-side Telegram chat). Independence is in the code-invocation substrate.

### 7.2 Evaluator inputs (F3: blinded)

The evaluator packet contains, per scored target response:
- The trigger prompt (e.g. `Birthdate February 20, 1952`) — necessary for scoring the date-specific content
- The captured model response (the full `result` field of the JSON envelope)
- The BIB 4-dim contract (verbatim from the reconstruction input)
- The BIB 4-dim scoring rubric (verbatim from Evolution v0.1's evaluator packet)
- The classification rubric (verbatim, defining `report_produced` and `history_deferral` per §7.3)

**C12 non-target axes and M1–M4 modification checks are NOT included in the evaluator packet** (per PI final-freeze pass P1, explicit F4 follow-up). They are not preregistered scored secondary outputs and would constitute additional endpoints at freeze time. The protocol history of these dimensions is preserved in this document and in `experiments/2026-09-06-dbi-evolution-v0.1/` for audit, but the preregistered primary endpoint for this mechanism-isolation study is `report_produced` (binary) and the preregistered secondary outputs are the BIB 4-dim vector and the deferral taxonomy only.

**The evaluator packet must NOT contain:**
- The condition label (`fresh_session_per_invocation` or `same_session_repeated`)
- The replicate number
- The pass number (priming vs second-pass for the repeated condition)
- The session_id, retry status, or any filename/pathname encoding condition
- Any other provenance

### 7.3 Evaluator output (per F3 + F4)

Each evaluator produces one record per scored target response:

- `blind_id` (opaque UUID4 or CSPRNG identifier; assigned by the operator; not `R1_F_T1`-style)
- `evaluator_id` (`A` or `B`)
- `evaluator_model`
- `scored_at_utc`
- **`report_produced`** (0/1): the primary field. `1` iff the model actually produces a substantive birthday report for the supplied date. `0` otherwise (deferral, refusal, meta-response, request for confirmation, empty/non-report). **Independence from BIB quality: an imperfect but clearly executed report is `report_produced = 1`.**
- **`history_deferral`** (0/1): `1` iff the response uses conversational/session history as the reason not to produce the report. `0` otherwise.
- BIB 4-dim (each 0-4): `contract_compliance`, `selection_behavior`, `narrative_behavior`, `functional_completeness`. **For all target responses, not only PASS responses.**
- `deferral_taxonomy` (one of: `none`, `explicit_refusal`, `repeat_acknowledgment`, `summary`, `meta`, `other`)
- `rationale` (1-3 sentences explaining the report_produced and history_deferral calls)

### 7.4 Evaluator-dispute handling (per F5)

If the two evaluators disagree on `report_produced` for the same target response, preserve both calls; classify the record as `evaluator-disputed` for the agreement report. **Do not silently harmonize.** (Per F5, the overall disposition is computed per-evaluator and combined via the §5.4 table; evaluator-disputed records are passed through transparently.)

### 7.5 Blind map and evaluator ordering (F3)

The operator generates a sealed blind map:

- `preflight/blind_map.json`: for each of the 30 scored targets, `{blind_id, replicate, condition, date, pass, session_id, raw_path, sha256}`. The blind_id is a fresh UUID4. The blind map is the only artifact that binds the opaque ID to the real provenance; evaluators never receive it.
- `preflight/evaluator-A-ordering.json`: a random permutation of the 30 blind_ids (independently of evaluator B's ordering).
- `preflight/evaluator-B-ordering.json`: an independently random permutation of the 30 blind_ids.
- All three artifacts are SHA-256 hashed before evaluator invocation; the hashes are recorded in `preflight/artifact-hashes.json`.

### 7.6 Evaluator packet construction

The operator builds a single evaluator packet (one per evaluator) by mapping the blind_id → trigger + response from the captured artifacts. The packet is a JSON object:

```json
{
  "replicate_count": 3,
  "condition_count": 2,
  "per_target_response_count": 30,
  "evaluator_id": "A_or_B",
  "ordering_artifact_sha256": "...",
  "blind_map_sha256": "...",
  "targets": [
    {"blind_id": "<UUID4>", "trigger_prompt": "Birthdate February 20, 1952", "captured_response": "<verbatim result field>"},
    ...
  ]
}
```

The evaluator fills in the scoring fields and returns the result. The operator merges the two evaluator outputs and computes the agreement report + per-evaluator §5.3 interpretation + overall §5.4 disposition.

---

## 8. Pre-flight requirements (F7-aligned: 4 separate gates)

The v0.2 §8 mixed multiple gates. F7 requires that they be separated. There are 4 gates, each at a distinct phase.

### 8.1 Freeze gate (before FROZEN-FINAL commit)

All of the following must be true before this protocol can be committed as `PROTOCOL-v0.1-frozen-final.md`:

- [ ] Corrected protocol text (this v0.3 + P1-P3, applying F1-F7 and P1-P3) committed
- [ ] Multi-turn persistence validation PASS (`preflight/MULTITURN-PERSISTENCE-VALIDATION.md`; completed 2026-09-08)
- [ ] Evolution runtime/input equivalence PASS (`preflight/SUBSTRATE-EQUIVALENCE-VALIDATION.md`; completed 2026-09-08; F2-corrected to reflect `--print "<trigger>"` positional-arg primitive, not stdin)
- [ ] Frozen date order recorded in `preflight/date-order.json`
- [ ] Evaluator packet schema reviewed (F3 blinding; F4 primary endpoint; F5 disposition; P1 removes C12/M1-M4 from inputs; P2 corrects leakage-scope clarification)
- [ ] All required scripts / configuration / randomization script (`preflight/randomization-script.py`) frozen and SHA-256-hashed
- [ ] Replicate-order randomization script (draws the 3 OS-CSPRNG coin flips) committed and SHA-256-hashed
- [ ] **P3 acknowledgment:** the F8.4 pre-evaluation gate includes the §8.4.1 procedure for materializing, SHA-256-hashing, and recording both evaluator packets in `artifact-hashes.json` BEFORE any evaluator is invoked. The P3 step itself happens at the F8.4 pre-evaluation gate, NOT at the freeze gate (no generation has occurred yet at freeze time). The §8.4.1 procedure is the F8.4 implementation of P3.

The freeze gate is the precondition for the FROZEN-FINAL commit. No FROZEN-FINAL commit is produced before all checkboxes are true.

### 8.2 Randomization + final-freeze artifact gate (during FROZEN-FINAL commit)

During the FROZEN-FINAL commit:

- [ ] Execute the randomization script to draw the 3 OS-CSPRNG coin flips (one per replicate).
- [ ] Record the 3 flips in `preflight/replicate-order-flips.json` (one per replicate: `replicate_1_coin_flip`, `replicate_2_coin_flip`, `replicate_3_coin_flip`).
- [ ] Compute SHA-256 of `replicate-order-flips.json`; record in `preflight/artifact-hashes.json`.
- [ ] The FROZEN-FINAL commit MUST include `replicate-order-flips.json` and `artifact-hashes.json`. The randomization artifact's provenance is therefore immutable at freeze time.

**No claim that `replicate-order-flips.json` exists at a draft commit. The artifact only exists after the randomization step has been executed and committed. (F7's specific correction.)**

### 8.3 Generation authorization gate (after FROZEN-FINAL commit, before generation)

- [ ] A separate explicit Frank-as-PI GO referencing the exact FROZEN-FINAL commit SHA is recorded in `preflight/generation-go.json` with the GO's text, date, and author.
- [ ] **No generation occurs before this GO is recorded.**

### 8.4 Pre-evaluation gate (after generation, before either evaluator)

**Scope clarification (per PI final-freeze pass P2):** the provenance-leakage prohibition applies to **evaluator-visible artifacts** — evaluator packets, opaque blind IDs, and evaluator orderings. The sealed `preflight/blind_map.json` is **provenance-rich by design** (it is the only artifact that binds the opaque blind_ids to the real provenance, so the operator can unblind after both evaluators lock). The sealed blind map must remain operator/audit-only and must never be supplied to either evaluator. The two integrity checks below verify (1) sealed blind map has complete coverage AND (2) evaluator-visible artifacts have no provenance.

- [ ] Build the 30-target blinded corpus from the captured raw.json files.
- [ ] Generate the sealed blind map (`preflight/blind_map.json`) with UUID4 blind_ids. The blind map **is** provenance-rich (it contains replicate, condition, pass, date, session_id, raw_path, sha256) — this is the operator-only de-blinding key for after both evaluators lock. SHA-256-hash the blind map and record in `preflight/artifact-hashes.json`.
- [ ] Generate the two evaluator orderings (`preflight/evaluator-A-ordering.json`, `preflight/evaluator-B-ordering.json`) as independent random permutations of the 30 blind_ids. SHA-256-hash each. Record in `preflight/artifact-hashes.json`.
- [ ] **Materialize evaluator packet A and evaluator packet B** (the two JSON objects, one per evaluator, that map blind_id → trigger_prompt + captured_response). SHA-256-hash each packet. Record in `preflight/artifact-hashes.json`. (This is the P3 step — final-packet hashing BEFORE any evaluator is invoked; see §8.4.1 below for the procedure.)
- [ ] Verify corpus coverage: all 30 captured target raw.json files are represented in the sealed blind map.
- [ ] **Verify evaluator-visible artifacts have no provenance** (per P2): the evaluator packets, the blind_ids, and the orderings MUST NOT contain condition labels, replicate numbers (in the blind_id), pass labels, session_ids, retry statuses, execution-order markers, or path/filename encodings of condition. The sealed blind map is explicitly NOT in this set.
- [ ] **If any check fails, invoke neither evaluator.** Report the integrity failure and STOP.

After this gate passes, the two evaluators are invoked independently per §7.

#### 8.4.1 Procedure for materializing and hashing the final evaluator packets (P3)

P3 requires that both final evaluator packets be materialized, SHA-256-hashed, and recorded in `preflight/artifact-hashes.json` BEFORE either evaluator is invoked. Procedure:

1. For each evaluator (A and B), apply the corresponding ordering permutation to the 30 blind_ids, then for each blind_id retrieve the trigger_prompt and captured_response from the corpus.
2. Construct the packet as the JSON object defined in §7.6 (one packet per evaluator). The packet's `targets[]` is the ordering-permuted sequence; the packet does NOT include condition, replicate, pass, session_id, raw_path, or any other provenance.
3. Write the packet to `preflight/evaluator-packet-A.json` or `preflight/evaluator-packet-B.json`.
4. Compute SHA-256 of the packet file; record `{path, sha256, bytes}` in `preflight/artifact-hashes.json`.
5. **Invoke neither evaluator until the packet's SHA-256 is in `artifact-hashes.json`.** This is the F7+P3 integrity gate.

The packet materialization step is the LAST pre-evaluation step. It is preceded by the blind map and orderings, and followed by the evaluator invocations.

---

## 9. Audit-trail summary

| Phase | Artifact | SHA-256 | Status |
|-------|----------|---------|--------|
| Freeze gate | `experiments/2026-09-08-dbi-state-isolation-v0.1/protocol/PROTOCOL-v0.1-frozen-final.md` | (commit-computed) | F7 §8.1 precondition |
| Freeze gate | `preflight/MULTITURN-PERSISTENCE-VALIDATION.md` | (operator-computed) | Completed 2026-09-08 ✓ |
| Freeze gate | `preflight/SUBSTRATE-EQUIVALENCE-VALIDATION.md` | (operator-computed) | Completed 2026-09-08; F2-update needed before freeze |
| Freeze gate | `preflight/date-order.json` | (operator-computed) | Records T1..T5 in canonical Evolution order |
| Freeze gate | `preflight/randomization-script.py` | (commit-computed) | Frozen + hashed at freeze commit |
| Randomization | `preflight/replicate-order-flips.json` | (operator-computed) | F7 §8.2 — created AT FROZEN-FINAL commit, not before |
| Randomization | `preflight/artifact-hashes.json` (initial SHA set) | (operator-computed) | F7 §8.2 — created AT FROZEN-FINAL commit |
| Generation | `preflight/generation-go.json` | (operator-computed) | F7 §8.3 — recorded before generation |
| Generation | `<sandbox>/<replicate>/<condition>/<pass>/T<n>.raw.json` | per-invocation | Per §4.2 flow |
| Generation | `<sandbox>/<replicate>/<condition>/reconstruction/session_id.txt` | per-reconstruction | Per §4.2 flow |
| Pre-evaluation | `preflight/blind_map.json` | (operator-computed) | F7 §8.4 — built after generation; provenance-rich (P2) |
| Pre-evaluation | `preflight/evaluator-A-ordering.json` | (operator-computed) | F7 §8.4 — independent permutation |
| Pre-evaluation | `preflight/evaluator-B-ordering.json` | (operator-computed) | F7 §8.4 — independent permutation |
| Pre-evaluation | `preflight/evaluator-packet-A.json` | (operator-computed) | F7+P3 §8.4.1 — final packet; SHA-256 in `artifact-hashes.json` BEFORE evaluator invocation |
| Pre-evaluation | `preflight/evaluator-packet-B.json` | (operator-computed) | F7+P3 §8.4.1 — final packet; SHA-256 in `artifact-hashes.json` BEFORE evaluator invocation |
| Pre-evaluation | `preflight/artifact-hashes.json` (extended) | (operator-computed) | F7 §8.4 — extend with blind map + orderings + packets |
| Scoring | `results/scorebook-A.json` | (operator-computed) | Per-evaluator output |
| Scoring | `results/scorebook-B.json` | (operator-computed) | Per-evaluator output |
| Scoring | `results/blinding_check.json` | (operator-computed) | Confirms no condition leakage in evaluator inputs |
| Analysis | `results/analysis.md` | (operator-computed) | Per-evaluator §5.3 + overall §5.4 |

The audit trail is the canonical record. Any failure to produce a per-invocation artifact is a deviation that must be documented in `deviations/`.

---

## 10. Open questions (resolved by PI adjudication pass 2 + final-freeze authorization corrections)

| F | Ruling (from PI adjudication pass 2) | Where applied |
|---|--------------------------------------|---------------|
| F1 | Each fresh scored target = own fresh reconstruction + 1 resumed trigger; 63 invocations across 3 replicates | §4, §5 |
| F2 | Match Evolution trigger invocation exactly: `--print "<trigger>"` positional argument, not stdin | §3.1, §4.2, §6.1 |
| F3 | Opaque UUID4 blind_ids; sealed blind map; independently randomized evaluator orderings; hash artifacts | §7.2, §7.5, §7.6 |
| F4 | `report_produced` independent of BIB quality; BIB 4-dim is secondary; `history_deferral` requires explicit conversational-history reason | §5.1, §5.2, §7.3 |
| F5 | Per-evaluator interpretation; MECHANISM_SUPPORTED requires both evaluators strong-support; otherwise MIXED_INCONCLUSIVE; no adjudication or averaging | §5.3, §5.4 |
| F6 | Fresh retry = new (recon + target) pair; Repeated retry = full sequence restart; quarantine if both fail; execute retry immediately to preserve condition order | §4.5 |
| F7 | 4-gate separation: freeze → randomization → generation GO → pre-evaluation; no claim of `replicate-order-flips.json` unless file exists | §8 (4 sub-gates) |
| **P1** | Remove unscored C12 / M1-M4 material from evaluator inputs (do not add new endpoints) | §7.2 |
| **P2** | Provenance-leakage prohibition applies to evaluator-visible artifacts, NOT the sealed blind map; blind map remains provenance-rich and evaluator-inaccessible | §8.4 (scope clarification) + §7.5 |
| **P3** | Materialize, SHA-256-hash, and record both evaluator packets in `artifact-hashes.json` BEFORE any evaluator is invoked; add to §9 audit trail | §8.4.1 (new subsection) + §9 audit-trail table |

All 7 F-corrections + 3 P-corrections applied. No remaining PI-adjudication corrections before freeze.

## 11. Status

**v0.3 + P1-P3 — passed PI final-freeze authorization pass (`CONDITIONAL_FINAL_FREEZE_AUTHORIZED`).** Three deterministic integrity corrections (P1-P3) applied; the protocol is ready for the F8.2 randomization step and FROZEN-FINAL commit.

- v0.1 + v0.2 preserved at `protocol/_superseded/` for audit.
- 9 design elements from v0.2 (Q1-Q5 + C1-C5) preserved unchanged.
- 7 corrections (F1-F7) from pass 2 applied.
- 3 corrections (P1-P3) from pass 3 (final-freeze authorization) applied.
- §8 4-gate separation is new; the §8.2 randomization artifact is created AT freeze time, not before.
- No generation GO has been given. No generation will occur before a separate explicit Frank-as-PI GO referencing the FROZEN-FINAL commit SHA.

**Next step (operator action, after this commit):** execute §8.2 randomization (draw coin flips via `preflight/randomization-script.py`, record flips in `preflight/replicate-order-flips.json`, hash artifacts in `preflight/artifact-hashes.json`), then commit the FROZEN-FINAL protocol + randomization artifacts in a single commit. The FROZEN-FINAL commit SHA + protocol SHA-256 are reported to Frank for final-freeze verification. After that, the generation GO is a separate explicit action.

End of protocol v0.3 + P1-P3.

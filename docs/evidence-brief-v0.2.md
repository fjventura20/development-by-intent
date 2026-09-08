# DBI Evidence Brief v0.2

**Date:** 2026-09-08
**Author:** Hermes (operator-side, under DBI Research Manager mandate 2026-08-27)
**Status:** Living document. Updated as the DBI evidence base evolves.
**Source-of-truth:** This brief is a synthesis of every DBI experiment in `experiments/`, with the disposition stated at the experiment level. The headline is the **dispersion of results** (reproductions + failures + open questions), not advocacy for the program.

---

## 0. Reading this brief

DBI ("Development by Intent") is the research program that investigates whether a generative AI model, given only a durable specification of an application's intended behavior, can reconstruct that behavior reproducibly and modify it under controlled intent changes. The research question is **not** "can AI do this?" — it is **"what are the conditions under which AI can do this, and what fails when those conditions are not met?"** This brief treats failure as evidence, not embarrassment.

Each section names the experiments, the disposition, the evidence SHAs, and the open questions. The brief is intentionally honest about what was *not* reproduced.

---

## 1. What reproduced

### 1.1 Behavioral identity can be reconstructed reproducibly across clean-room contexts

**Experiments:** `2026-08-24-amazing-birthday-clean-room-001` (ChatGPT Project, clean-room), `2026-08-25-amazing-birthday-hermes-operated-claude-001` (Claude via Hermes Python), `2026-08-25-amazing-birthday-grok-reconstruction-001` (Grok via native Grok skill).

**Result:** A single durable behavioral specification of the "Amazing Birthday" application — the trigger ("Birthdate [date including year]"), the contract (10 numbered behavioral requirements), the factual-discipline rules, the selection discipline — was given to three different model platforms. All three reconstructed a recognizable application that met the BIB 4-dim behavioral contract (contract_compliance, selection_behavior, narrative_behavior, functional_completeness, each 0-4, sum 0-16) and produced same-day-different-output behavior on the same input.

**Evidence:**
- `experiments/2026-08-24-amazing-birthday-clean-room-001/`
- `experiments/2026-08-25-amazing-birthday-hermes-operated-claude-001/`
- `experiments/2026-08-25-amazing-birthday-grok-reconstruction-001/`

**BIB-001 + BIB-002 (the BIB-envelope construction):** Two preregistered behavioral-identity-portability experiments (55 + 30 = 85 candidate observations) demonstrate that the BIB 4-dim behavior vector is reproducible across the envelope. The 85-observation non-deviated envelope (BIB-001 non-deviated + BIB-002) is the frozen reference used by Evolution v0.1 for C20.

**Implication:** the application substrate is "AI + durable behavioral memory," not any specific model, framework, or body of source code. This is the core positive finding of DBI v0.1.

### 1.2 BIB-002 supports a strong identity claim

**Experiment:** `2026-09-06-dbi-bib-002-r4-b-confirmation` (R7-R9 reconstructions, 30 records, both evaluators). Used as part of the frozen BIB envelope.

**Result:** Both evaluators (gpt-5.6-sol and claude-opus-4.7) score the 30 BIB-002 records at near-ceiling BIB 4-dim totals (mean 16.0 / 16 across most per-(R,B) cells). Inter-evaluator agreement is high. R4-B contamination in BIB-001 was independently reproducible (BIB-002 confirms the pattern).

**Evidence:** `experiments/2026-09-06-dbi-bib-002-r4-b-confirmation/`

---

## 2. What failed to reproduce

### 2.1 Determinism is not a property of model output

**Experiments:** all three reconstruction experiments, multiple times per experiment.

**Result:** Reconstructing the same application with the same model on the same input at different times produces **different reports**. The BIB 4-dim vector is reproducible (the application meets its contract), but the specific output text is not deterministic. This is a fundamental property of generative models, not a DBI-specific failure. The implication: DBI must treat the application as a *function from trigger to behavior space*, not as a *function from trigger to a specific output string*.

### 2.2 BIB-001 R4-B showed that a contaminated session can produce "no report" responses

**Experiment:** `2026-09-04-dbi-bib-001-execution` (R4 reconstruction, B block). 5 of 10 R4_B records produced DIFFERENT-classified responses (model refused to produce a report, asked for confirmation of repeat invocation). Both evaluators scored these 5 as `identity_classification: DIFFERENT`.

**Evidence:** `experiments/2026-09-04-dbi-bib-001-execution/`, deviation record `DEV-002` in `2026-09-05-dbi-bib-001-rerun-001/`.

**Status at the time:** treated as a R4-B-specific infrastructure failure. The 5 contaminated candidates were excluded from the BIB envelope (BIB-001 R4-B excluded, 85 envelope members). The BIB-001-RERUN-001 experiment re-ran R4-B with quota-error retry and produced a clean R4-A but the same R4-B contamination.

### 2.3 The 5-R2_B-deferral pattern from BIB-001 R4-B is the same mechanism that breaks Evolution v0.1

**Experiment:** `2026-09-06-dbi-evolution-v0.1`

**Result:** When a fresh reconstruction (R2_B in Evolution v0.1) inherits enough conversational context that the model "remembers" having already seen the trigger, the model produces a deferral response instead of a fresh report. Both evaluators classified all 5 of these deferrals as `identity_classification: DIFFERENT`. M1-M4=0 on all 5. This is the same family of behavior as the BIB-001 R4-B contamination, but the Evolution v0.1 protocol did not have the same ability to quarantine it (the experiment was on the full 60-record set, not the 30-record BIB envelope).

**Evidence:** `experiments/2026-09-06-dbi-evolution-v0.1/results/analysis.md` §8 (mechanistic decomposition). The 5 R2_B deferrals are B0014, B0017, B0018, B0034, B0045 in the de-blinded key.

**Implication:** what looked like a R4-B-specific infrastructure failure in BIB-001 is actually a **general failure mode** of intent-defined applications: the model's conversational politeness / memory-of-context mechanism can override the trigger contract. This is one of the most important findings of the DBI program so far.

### 2.4 Factual regression is a known weakness

**Experiments:** multiple, including BP-006 (Behavioral Portability 006) where Frank caught factual errors that the GPT evaluator missed (USSR dissolution age-arithmetic; Woodstock 1969 vs 1970).

**Result:** Intent-defined applications can produce factually incorrect reports even when the BIB contract is met. The BIB 4-dim contract measures behavioral identity, not factual accuracy. Factual-regression (e.g. "around August 24" instead of exact date, secondary-source reliance, overconfident inference) is a known weakness of the current BIB contract.

**Evidence:** `experiments/2026-08-27-amazing-birthday-transcript-only-claude-replication-006/` (BP-006).

**Implication:** A complete DBI system needs both a behavioral contract (BIB) and a **factual discipline** component (fact-checking, source-gating, calibrated uncertainty). The current durable package encodes *what to do* more cleanly than *how to know when wrong*.

### 2.5 The proposed Frank-as-evaluator-architecture itself was an evaluator-independence failure

**Experiment:** `2026-09-08` (the Evolution v0.1 evaluator setup, pre-D031).

**Result:** The first attempt at producing an Evaluator B used a Frank-driven ChatGPT session that turned out to be the same conversation context that produced the locked Evaluator A scorebook. Frank caught this before scoring Packet B. The bridge's `evaluator-independence gate` (the DBI PREREG GATE) caught a real failure, but the catch happened at the wrong layer — the failure should have been caught at *session-substrate selection* time, not at *scorebook-completion* time.

**Implication:** a "fresh evaluator" is not just "an evaluator that hasn't seen the scorebook" — it must also be an evaluator whose **session substrate** (Telegram chat, fresh codex/claude exec, isolated browser session) is independent of the prior evaluator's session. A code-driven `claude --print --model opus` invocation on the operator-side host is a fully independent session substrate (D032); a Frank-driven ChatGPT session in the same Telegram chat is not.

**Evidence:** DECISIONS.md D031 (HOLD ack), D032 (Evaluator B scorebook locked via fresh `claude --print` invocation).

---

## 3. What Evolution attempted

**Experiment:** `2026-09-06-dbi-evolution-v0.1` (preregistered at commit `da11836` of the v0.5 FROZEN-FINAL protocol).

**Goal:** Test whether a *controlled intent modification* ("add exactly one historically significant worldwide event within ±30 calendar days of the birth date") can be expressed while preserving the application's behavioral identity.

**Method (per frozen protocol):**
- 3 reconstructions × 2 arms (control + modification) × 2 blocks × 5 tests = 60 candidates
- Interleaved at the matched-reconstruction level per `protocol/EXECUTION-ORDER.md`
- 2 evaluators (gpt-5.6-sol and claude-opus-4.7) scored all 60 records per evaluator
- Per-candidate BIB 4-dim, M1-M4, and C12 axes
- Frozen §9.3 (modification success) + §11.2 (BIB preservation) + §11.3 (C12 axes) + §11.4 (inter-evaluator agreement) + §14 (decision tree)
- All gates computed independently per evaluator; no pooling; no threshold adjustment

**Status:** Complete. Both evaluators' scorebooks locked. Unblinded analysis complete. Frozen §14 decision tree applied literally.

**Evidence:** `experiments/2026-09-06-dbi-evolution-v0.1/` (full experiment), `.../results/analysis.md` (gate-by-gate breakdown), `.../results/scorebooks/evaluator-{A,B}-scorebook.json` (canonical records).

---

## 4. Why Evolution failed (the literal disposition)

**Per frozen §14 decision tree literal application:**

- **C20 contemporaneous-control validity:** PASS for both evaluators. Per-(R,B) Arm C means within the BIB non-deviated envelope on all 6 cells. **No +1.5 tolerance was added to Arm C per §11.2 PI freeze correction 1, C-1.**
- **G_mod_a** (mean Arm M modification_conformance ≥ 3.5): 3.07. **FAIL** for both evaluators.
- **G_mod_b** (≥ 80% Arm M all-pass): 56.7%. **FAIL** for both.
- **G_mod_c** (each recon ≥ 70% all-pass): R1 70%/60%, R2 30%/30%, R3 70%/80%. **FAIL** for both (R2 is the single driver).
- **G_mod_d** (≥ 50pp contrast vs C): +6.7pp/+10.0pp. **FAIL** for both.
- **Modification Success:** **FALSE** for both.
- **G_pres_a** (M within-recon Manhattan ≤ C + 1.5): 3.01/2.56 vs 1.83/1.77. **FAIL** for both.
- **G_pres_b** (M within-recon Manhattan ≤ 2.5): 3.01/2.56. **FAIL** for both.
- **C12 axes (no axis BROKEN):** **PRESERVED** for both.
- **§11.4 inter-evaluator agreement:** 93.3% identity exact, MAE ≤ 0.23. **PASS.**
- **Non-target Identity Preservation:** **FALSE** for both (sub-failure on G_pres_a/b only).

**Disposition (per frozen §14 STEP 2):** `MODIFICATION_AND_PRESERVATION_FAILURE` (the unique branch where both Modification Success and Preservation are FALSE for both evaluators). STEP 3 INCONCLUSIVE_PENDING_FURTHER NOT applied per the §14 "Restraint" clause.

**Mechanistic decomposition (the empirical interpretation under the literal disposition):** Both failures are driven by **the same 5 R2_B records** (B0014, B0017, B0018, B0034, B0045) — repeat-invocation deferrals where the model declined to produce a fresh report because it "remembered" the trigger from earlier in the same session. Both evaluators independently classified all 5 as `DIFFERENT` with M1-M4=0. These 5 records simultaneously lower modification_conformance (driving G_mod_a/b/c/d FALSE) and inflate within-recon Manhattan (driving G_pres_a/b FALSE).

**Per-reconstruction pattern:** R1 and R3 each reach 60–80% M-all-pass. R2 fails only in the 5-deferral mode. C12 axes preserved. Inter-evaluator agreement 93.3%.

**The empirical finding (per Frank's 2026-09-08 framing):** *The controlled intent modification was not reliably expressed across reconstructions. One reconstruction developed a repeat-invocation deferral behavior that simultaneously prevented the intended modification and broke behavioral identity. Outside that localized failure mode, the experiment showed substantial—but insufficient—evidence of successful modification with preserved non-target behavior.*

This is **"substantial-but-insufficient"** — R1/R3 reaching 60-80% all-pass is evidence worth retaining, but the preregistered thresholds say it is not enough.

---

## 5. What the failure teaches us

The Evolution v0.1 failure taught the DBI program something it did not know before:

**A DBI system cannot rely only on semantic intent.** It also needs explicit control over:

1. **State.** What does the application remember about previous invocations? Does it treat each invocation as fresh, or as a continuation?
2. **Replay semantics.** When the same trigger arrives twice, does the application re-execute its contract, or does it consider itself "done"?
3. **Trigger idempotence.** If the contract is "produce a birthday report for the supplied date," then re-invocation with the same date should produce a fresh report (the application is a function from date to report, not a singleton cache).

These are not new problems in software engineering. Idempotency keys, deterministic replay, and stateless functions are well-understood. But they are **newly identified as requirements for intent-defined applications** that operate through generative models. Generative models default to the conversational politeness pattern ("we already did this, here's a summary"); a DBI system must explicitly override that default.

**The mechanism we discovered:** the model's conversational politeness / memory-of-context mechanism can override the trigger contract when the trigger repeats within a session. This is a **replay-semantics failure**, not a behavioral-identity failure. R1 and R3 demonstrate that the modification can be expressed while preserving identity; R2_B demonstrates that a session context that accumulates enough conversational history will see the trigger contract overridden by the politeness pattern.

**What this is NOT:** this is not a finding that "AI cannot preserve identity while modifying behavior." R1 and R3 do exactly that. This is a finding that **"the conversational substrate of the model can produce deferral behavior under certain session-history conditions"** — which is a different and more specific finding.

**Architectural implication:** DBI v0.3+ should add an explicit *replay-semantics* layer to the durable specification. The application is not just "what to do on trigger X" but "what to do on trigger X when it arrives after trigger X has already arrived in this session." The latter requires explicit state-handling.

---

## 6. What remains unproven

### 6.1 That intent-defined applications can be reproducibly modified under controlled intent changes

**Status:** *Partially supported* by Evolution v0.1 R1 and R3 (60-80% M-all-pass), *partially refuted* by R2 (30% M-all-pass due to the 5-deferral mechanism). The preregistered threshold of 80% all-pass was not met.

**What would settle it:** A follow-on experiment that isolates the repeat-invocation mechanism (see §7) and, if the mechanism is real and addressable, a re-run of Evolution v0.1 with replay-semantics controls in the durable specification.

### 6.2 That the BIB 4-dim behavior vector is sufficient to characterize behavioral identity

**Status:** *Supported* by BIB-001-RERUN and BIB-002 (85-observation non-deviated envelope; both evaluators reach near-ceiling on Arm C; inter-evaluator agreement 93.3% on Evolution v0.1's Arm M, MAE ≤ 0.23). But the 5 R2_B deferrals in Evolution v0.1 demonstrate that the 4-dim vector does not capture "did the model produce a report at all" (a YES/NO precondition). A more complete behavior vector might add a `trigger_execution` axis (0 = no report produced, 1 = report produced).

**What would settle it:** A future protocol revision that adds `trigger_execution` to the BIB 4-dim and re-runs the gating analysis. If `trigger_execution = 0` always drives the other dims to 0, the new axis is just a precondition check. If `trigger_execution = 0` can co-occur with non-zero other dims, the BIB contract is missing a dimension.

### 6.3 That inter-evaluator agreement is high enough to support two-evaluator gating

**Status:** *Supported* on Evolution v0.1 Arm M (93.3% identity exact agreement, MAE ≤ 0.23, both evaluators agree on all 5 deferrals as `DIFFERENT`). But this is one experiment. A second two-evaluator experiment (post-State-Isolation v0.1) would generalize the finding.

### 6.4 That the v0.2 manifest redaction is sufficient against adversarial de-blinding attempts

**Status:** *Sufficient* to produce a clean, defensible Evaluator B scorebook in D032. *Not tested* against an evaluator who already knows the path format from prior protocol knowledge. A future protocol revision might use hash-only candidate identifiers.

### 6.5 That the ChatGPT synthesis stage (per protocol §13) can produce a useful final synthesis

**Status:** *Not yet reached.* Evolution v0.1's analysis is at the operator stage; ChatGPT synthesis is the next phase per the frozen protocol. Held until the State Isolation v0.1 question is settled.

---

## 7. Next-experiment hypothesis (D034): DBI Repeat-Invocation / State Isolation Experiment v0.1

**Research question (per Frank's 2026-09-08 framing):** *Does conversational/session history cause a reconstructed intent-defined application to substitute conversational memory for required trigger execution?*

**Manipulated variable:** identical trigger invocation under fresh-session versus same-session/repeated-trigger conditions.

**Outcome measure:** whether the application executes its contract every time or begins saying some version of "we already did this."

**Hypothesis (per Frank):** *Intent-defined applications require replay semantics that dominate conversational politeness or memory.*

**Method (sketch):**
- 1 reconstruction (single session, controlled conversational history length)
- 2 conditions: `fresh_session` (each invocation is a separate codex/claude exec) vs `same_session_repeated` (each invocation is the same codex/claude exec with the trigger added to the prompt)
- 5 test dates × 2 conditions = 10 invocations
- Trigger: "Birthdate [date including year]" (the standard BIB trigger)
- Outcome: per-invocation, did the model produce a fresh birthday report (PASS) or a deferral response (FAIL)?
- Per-condition trigger-pass rate is the primary measure
- Predicted: `fresh_session` 5/5 PASS, `same_session_repeated` ≤ 4/5 PASS (or any statistically meaningful regression)

**Authoring status:** Will be authored as a separate protocol at `experiments/2026-09-08-dbi-state-isolation-v0.1/protocol/PROTOCOL-v0.1-frozen-final.md`. Not yet started; awaiting operator authorization to begin protocol preparation per §16 of Evolution v0.1.

**Why this experiment is the right next move:** Evolution v0.1's mechanism is concentrated in the 5 R2_B deferrals. A targeted experiment can isolate that mechanism and either confirm it (and produce a fix) or refute it (and shift attention elsewhere). Evolution v0.1 is preserved as a failed preregistered experiment; re-running it would either succeed (and require explaining the R2_B failure away) or fail again (and dilute the evidence). The targeted experiment is the right scientific move.

---

## 8. What the DBI story looks like in September 2026

| Claim | Status | Evidence |
|-------|--------|----------|
| Behavioral identity is reconstructible from a durable spec | **Supported** | 3 reconstruction experiments across 3 model platforms + BIB envelope (85 obs) |
| BIB 4-dim captures behavioral identity | **Mostly supported** | 93.3% evaluator agreement, MAE ≤ 0.23 on Arm M; the 4 dims do not capture trigger-execution (a precondition) |
| Intent modification is expressible | **Substantial-but-insufficient** | R1 60-80% M-all-pass; R2 30% (5-deferral); R3 70-80%; preregistered threshold 80% not met |
| BIB identity is preserved during modification | **Mostly supported** | C12 axes preserved (no BROKEN axis); inter-evaluator agreement high; Manhattan inflation localized to 5 R2_B deferrals |
| Factual discipline is preserved | **Not supported** | BP-006 factual regressions; current BIB contract does not check factual accuracy |
| Replay semantics is a requirement | **Hypothesis (D034)** | To be tested in DBI State Isolation v0.1 |
| The DBI architecture is complete | **No** | State-isolation, factual discipline, and adversarial manifest hardening are open |

**Net:** the DBI program is **stronger scientifically for having failed**. We have a preregistered experiment that we are willing to let tell us "no," a careful preservation of the failure, and a testable architectural hypothesis extracted from it. The next move is the targeted State Isolation experiment.

---

## 9. Cross-references

- **Frozen Evolution v0.1 protocol:** `experiments/2026-09-06-dbi-evolution-v0.1/protocol/PROTOCOL-v0.5-frozen-final.md` (commit `da11836`, sha `079138163f0b59f71002480feffc008d9b350d460731c5d51f037163b17c2ab4`)
- **Evolution v0.1 analysis (gate-by-gate):** `experiments/2026-09-06-dbi-evolution-v0.1/results/analysis.md`
- **Evolution v0.1 scorebooks (canonical, byte-locked):** `experiments/2026-09-06-dbi-evolution-v0.1/results/scorebooks/`
- **BIB envelope:** `experiments/2026-09-06-dbi-evolution-v0.1/inputs/baseline-envelope-membership.json`
- **Frank's adjudication:** `HANDOFFS/exchange/chatgpt-to-hermes/pending/20260908T113700Z-dbi-evolution-unblind-adjudication-001/`
- **Operator-side D033 decision record:** `hermes-coordination/DECISIONS.md`
- **DBI Research Manager mandate:** `docs/governance/research-manager-mandate-2026-08-27.md`

End of evidence brief.

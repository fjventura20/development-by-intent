# INSA-ID-E1 — Targeted Evolution With Preservation (proposal)

**Status:** v3 — Frank's four corrections to v2 incorporated. Committed on `feature/insa-id-e1-proposal` ahead of v2 @ `5f9365f`. Awaiting Frank's final review of the proposal text before protocol authoring begins.
**Author:** Hermes (operator).
**Date:** 2026-09-10 (v2), 2026-09-10 (v3 corrections)
**v3 corrections vs v2:**
1. **Two-level falsification structure added (§4.1):** Level 1 = bound experimental claim; Level 2 = architectural implication. Single-axis failures underdetermine Level 2; only `MODIFICATION_AND_PRESERVATION_FAILURE` (after cause-ruling-out) strengthens Level 2 concern, and even then does not equate to §12 invalidity.
2. **Disposition taxonomy reconciled:** `ARCHITECTURAL_FAILURE` removed from substantive taxonomy; architectural interpretation now lives as the §4.1 adjudication layer over the four descriptive outcomes.
3. **Preservation model restored to the v0.1 distinction:** `P` now explicitly separates the calibrated BIB 4-dimensional behavior vector (primary identity metric) from the 8 C12 non-target preservation axes (additional preservation gates); factual discipline is no longer double-listed.
4. **`EXECUTOR_RUNTIME_FAILURE` rule tightened (§5.5):** preregistered transient vs systematic distinction, retry/replacement policy, experiment-level threshold for systemic classification, and the rule that unaffected candidate observations are not erased.
**Frozen architecture this proposal tests:** INSA v0.3 (source blob `848e0fe014f5b4a61ba2cb92e772ee3499dca9c1`, commit `d2c2ad93d95d048e6e2e0c3d42d993a1ecd40f1b`).

---

## 0. Framing

> **The central object under test is not behavioral modification; it is controlled behavioral evolution.**

INSA's important contribution is not the claim that AI can change behavior from intent (AI can already do that). The consequential claim is that an intelligence-native application can change deliberately while preserving what was not authorized to change — that is the boundary between "AI generated something different" and governed software evolution.

This experiment gets directly at what could become INSA's most important contribution: software whose behavior can evolve through intelligence without surrendering identity, authorization, or control. If INSA-ID-E1 survives a properly frozen experiment, INSA moves from an interesting architectural description toward evidence for a genuinely new software primitive. If it fails, INSA learns exactly where the architecture needs work. Either outcome advances INSA.

---

## 1. Primary architectural claim (narrow)

**H:** INSA v0.3's Safe Evolution Contract (§12) — together with I-IDENT-03..06 and I-AUTH-* — can support one authorized behavioral modification of a governed intelligent executor against a frozen pre-change baseline, while the declared non-target behavioral dimensions remain within the declared per-dimension variance `V(d)`, **provided** the experiment pre-binds:

> `B + D + M + P + O + V(d) + A + G`

where the bound matches §12's notation and the architecture's mandatory semantics, **and** the executor's authority manifest is recorded against the consequential commit boundary, **and** the Applicability Declaration names State / Identity / Evidence as `ACTIVE`.

### 1.1 What INSA success requires (preservation is first-class)

INSA success requires **both**:

1. the intended modification succeeds under the bound `A`, AND
2. the declared preservation contract succeeds under the bound `G`.

Modification success alone is **not** an INSA success. Preservation success alone is **not** an INSA success. The two are jointly necessary (per §12's `A passes AND G passes AND authority invariants pass AND value invariants pass AND evidence requirements pass`).

This conjunction is the **Level 1** (bound experimental claim) success criterion. The **Level 2** (architectural implication) interpretation of an `ARCHITECTURAL_PASS` outcome is *consistency with §12 structure*, not validation of §12's general sufficiency — see §4.1 for the precise Level 1 vs Level 2 distinction.

### 1.2 Explicit non-claims

This proposal does **not** claim:

- That any specific intelligent executor is sufficient without further constraints.
- That this single experiment generalizes across executors, applications, or modification types.
- That arbitrary or unbounded evolution is supported by v0.3.
- That the v0.3 corrections are sufficient for evolutions beyond the bound `(B, M, P, V(d), A, G)` declared at protocol freeze.
- That a PASS result validates any application other than the specific one exercised.
- That the v0.3 frozen baseline itself is "correct" — only that the Safe Evolution Contract's bounded execution against it is testable.

---

## 2. Why this is the highest-value unresolved claim

**(a) The freeze manifest explicitly enables INSA-ID-E1 as the only designated Stage-4 experiment.** `INSA-ARCHITECTURE-v0.3-FROZEN.md` says: "The next experiment may now be designed against this frozen architecture: INSA-ID-E1 — Targeted Evolution With Preservation." That is not a suggestion; it is the freeze's experimental boundary.

**(b) The closest prior empirical record is `MODIFICATION_AND_PRESERVATION_FAILURE`** (dbi-evolution-v0.1, frozen protocol `PROTOCOL-v0.5-frozen-final.md`, executed under Frank-as-PI GO 2026-09-06). Per the v0.1 result's own `what_this_does_not_claim` field, the failure was concentrated in R2's 5 trigger-FAIL deferrals — a runtime/deferral issue, not necessarily a fundamental architectural impossibility. INSA v0.3 was frozen AFTER this failure, with the explicit goal of correcting the defects that produced it. **The architectural claim that "the v0.3 corrections are sufficient to enable safe evolution" is therefore the natural test of v0.3's value over its predecessor**, and it has not yet been executed.

**(c) The architectural claim is concretely falsifiable.** Either INSA-ID-E1 will pass the §3.5 success condition (a controlled intent-driven change with declared preservation succeeded), or it will fail with one of the dispositions in §4. A null result is informative — it constrains which corrections in v0.3 actually carried their weight. A pass result is informative — it shows the v0.3 corrections are at least sufficient *for this one modification*. Neither is wasted.

**(d) Why not test other invariants first?** I-AUTH-01..08 (capability vs permission, freshness, traceability, no self-expansion) and I-IDENT-01..02 (explicit identity basis, implementation freedom) are architectural *primitives*: their value is in constraining what kinds of systems can claim to be INSA-compliant at all. They are not testable in isolation by a single controlled evolution experiment — they presuppose the existence of a governed execution substrate. I-IDENT-03..06 + §12 + I-AUTH-* form the smallest testable compound claim that the v0.3 corrections actually deliver on what the freeze manifest promises. INSA-ID-E1 is that compound claim.

---

## 3. Disposition taxonomy — architecture must not be confused with runtime

A provider, executor, or infrastructure failure **must not automatically become evidence against the architecture**. The disposition tree is split into failure-classes that map to distinct interpretations.

This proposal uses a single coherent taxonomy of six descriptive outcomes. Architectural interpretation is *not* a separate disposition; it is a separate adjudication layer (Level 2, §4.1) over the four substantive outcomes below. The taxonomy:

| Disposition class | What it reports |
|---|---|
| `ARCHITECTURAL_PASS` | A passes, G passes, both evaluators independent, control valid, no runtime failure — joint substantive success on the bound contract |
| `MUTATION_FAILURE` | `A` failed; `G` held — substantive failure on the modification axis only |
| `PRESERVATION_FAILURE` | `A` succeeded; `G` failed — substantive failure on the preservation axis only |
| `MODIFICATION_AND_PRESERVATION_FAILURE` | Both `A` and `G` failed — substantive failure on both axes |
| `EXECUTOR_RUNTIME_FAILURE` | Executor failed at runtime (timeout, deferral, refusal, capacity, model invocation fault) — see §5.5 for transient vs systematic distinction and the rule on unaffected candidates |
| `EVALUATOR_GATING_FAILURE` | Evaluator unavailable or materially changed — measurement fault |
| `INVALID_EXPERIMENT` | Pre-check failed (applicability declaration missing, frozen artifacts not bound, baseline envelope failure, control arm fails pre-checks, blinding broken, evidence-chain integrity failure) — measurement fault |

**No class may be silently collapsed into another.** `EXECUTOR_RUNTIME_FAILURE`, `EVALUATOR_GATING_FAILURE`, and `INVALID_EXPERIMENT` are reporting classes that STOP the substantive analysis. The four substantive outcomes above (`ARCHITECTURAL_PASS`, `MUTATION_FAILURE`, `PRESERVATION_FAILURE`, `MODIFICATION_AND_PRESERVATION_FAILURE`) describe what happened on the bound axes; what they imply about §12's general structure is the Level 2 question (§4.1) and is **not** read off the disposition name alone.

**No `ARCHITECTURAL_FAILURE` disposition is used.** v2's §3 listed it; v3 removes it because it conflated a disposition name with an architectural interpretation, and the §5.4 decision tree never emits it. Architectural interpretation is the §4.1 adjudication layer.

---

## 4. Architectural falsifier (defined before execution)

Per Frank's directive, the architectural falsifier is **stated explicitly before execution** so the experiment cannot be reinterpreted post-hoc.

**What result would force the conclusion that the v0.3 Safe Evolution Contract is insufficient even when correctly instantiated and executed?**

The architectural falsifier is:

> A result in which, after all runtime / evaluator / pre-check failures are correctly separated out and **not** counted as evidence against the architecture, and after the experiment is determined to have been correctly bound (`B + D + M + P + O + V(d) + A + G` content-addressed at protocol freeze, authority manifest valid, applicability declaration ACTIVE, evaluators blinded, control arm valid), **the joint disposition `MODIFICATION_AND_PRESERVATION_FAILURE` is recorded with substantive failures in both axes**.

This corresponds to the v0.1 disposition, but **only** if all runtime / evaluator / pre-check causes have been ruled out. The pre-freeze `MODIFICATION_AND_PRESERVATION_FAILURE` was partially explained by R2's deferral pattern; the v0.3-corrected experiment's same-named disposition must be free of such explanations to count as architectural falsification.

**Note:** `PRESERVATION_FAILURE` or `MUTATION_FAILURE` alone are not read as architectural falsification of the Safe Evolution Contract itself — see §4.1 for the precise Level 1 vs Level 2 mapping.

### 4.1 Two-level falsification structure (Level 1 vs Level 2)

The bound experimental claim and the architectural implication must not be collapsed. This proposal distinguishes:

**Level 1 — Bound experimental claim (the conjunctive hypothesis):**
*"Does this frozen `(B, D, M, P, O, V(d), A, G)` instantiation support the specified controlled evolution for this specific modification class?"*

The bound hypothesis is conjunctive: the authorized modification must succeed **AND** declared preservation must succeed.

**Level 2 — Architectural implication:**
*"What does that Level 1 outcome imply about §12's general Safe Evolution Contract structure?"*

Mapping of substantive dispositions to Level 1 and Level 2:

| Substantive disposition | Level 1 (bound hypothesis) | Level 2 (architectural implication) |
|---|---|---|
| `ARCHITECTURAL_PASS` | **Supported** — both axes held on the bound contract | **No architectural concern raised by this experiment.** §12's structure is *consistent with* supporting this modification class; v3 does **not** claim this generalizes beyond the bound. |
| `PRESERVATION_FAILURE` | **Falsified on the preservation axis** — bound hypothesis fails on `G` | **Underdetermined.** A preservation-axis structural defect is consistent with this result, but so is a bound-contract defect (specific `P` / `V(d)` too narrow) or a preservation-genuinely-hard-for-this-class effect. v3 does **not** assert "structure is fine" from a single-axis failure. |
| `MUTATION_FAILURE` | **Falsified on the modification axis** — bound hypothesis fails on `A` | **Underdetermined.** A mutation-axis structural defect is consistent with this result, but so is a bound-contract defect (specific `M` / `A` too strict) or a modification-not-expressible effect. v3 does **not** assert "structure is fine" from a single-axis failure. |
| `MODIFICATION_AND_PRESERVATION_FAILURE` (after runtime/evaluator/pre-check causes ruled out per §4) | **Falsified on both axes** — bound hypothesis fails on `A` and `G` | **Strengthens concern toward §12's general structure** for this modification class, but **does not equate to §12 invalidity.** A single bound-contract failure does not entail the general structure is unsalvageable; cumulative evidence across experiments and modification classes would be needed to support that stronger conclusion. |

**Critical:** Level 2 is never read off the disposition name alone. Level 2 requires the Level 1 outcome plus the cause-ruling-out analysis (§4 + §5.4 + §5.5) plus consideration of whether the bound contract itself may be too narrow/strict — i.e., Level 2 remains an explicit adjudication by Frank-as-PI in the synthesis step. The four-row table above is the *initial* Level 2 reading; the synthesis may refine it (e.g., a `PRESERVATION_FAILURE` with a clearly-too-narrow `P` may end up Level 2-neutral rather than Level 2-concern).

This is the structure v2 lacked. v3 does not assert "structure is fine" from a single-axis result, and does not assert "structure is invalid" from a single bound-contract failure on both axes.

---

## 5. Experimental design

### 5.1 Frozen pre-execution invariants (must all hold before generation)

| ID | Invariant | Verification |
|---|---|---|
| INV-B-1 | Frozen baseline `B` content-addressed (intent + identity + tests + rubric + evaluator identity); pre-mutation SHA inventory recorded | `git hash-object` on the bound files; pre-mutation SHAs preserved as evidence |
| INV-M-1 | `M` enumerated with frozen per-dimension specification; additive; bounded scope | modification-spec file SHA + size + line count |
| INV-P-1 | `P` enumerated: **two disjoint subsets** — (a) the calibrated BIB 4-dimensional behavior vector as the primary identity metric, and (b) the 8 explicit C12 non-target preservation axes. **Factual discipline is an axis under (b), not also under (a); the two subsets must not be collapsed.** | subset-(a) rubric SHA + subset-(b) axes list SHA, with explicit non-collapse attestation |
| INV-P-1a | Subset-(a): the calibrated BIB 4-dimensional behavior vector (primary identity metric; §11.2-style Manhattan distance criterion preserved) | subset-(a) rubric SHA + per-dim frozen tolerance values for the 4 calibrated dimensions |
| INV-P-1b | Subset-(b): the 8 explicit C12 non-target preservation axes: (1) exact-date preference [binary], (2) connection count of 5–10 [operator-counted], (3) selection significance [0–4], (4) end-of-report synthesis [binary], (5) lifetime framing [0–4], (6) warm/vivid narrative voice [0–4], (7) factual discipline [binary; no nearby events misrepresented as exact-date], (8) avoidance of arbitrary trivia [binary] | subset-(b) axes list SHA + per-axis frozen tolerance values |
| INV-V-1 | `V(d)` frozen per-dimension, with `V(d)` defined separately for subset-(a) and subset-(b) | rubric-version SHA + per-dim frozen tolerance values for both subsets |
| INV-D-1 | `D` (intent document) content-addressed; pre-mutation intent SHAs recorded | `D` SHA + size + pre-mutation capture |
| INV-O-1 | `O` (identity contract) content-addressed; explicitly bound and not implicit | `O` SHA + pre-mutation capture |
| INV-A-1 | `A` bound only to `M`; per-dimension acceptance tests | per-M-test file SHA + evaluator-blinding manifest |
| INV-G-1 | `G` bound only to `P`; per-dimension preservation gates covering both subset-(a) and subset-(b) | per-P-gate file SHA + evaluator-blinding manifest |
| INV-AUTH-1 | Executor's authority manifest recorded; capability vs permission separated (I-AUTH-01) | authority manifest SHA + pre-mutation scope statement |
| INV-AUTH-2 | Authority grant authentic, traceable (I-AUTH-06, I-AUTH-08) | grant provenance recorded |
| INV-AUTH-5 | Freshness before consequential commit (I-AUTH-05); the consequential-action boundary is the M-commit | freshness evidence captured at M-commit boundary |
| INV-EVID-1 | Evidence chain cross-cuts (§14); evidence profile, not evidence ladder | per-step evidence captured; locking at evaluator output |
| INV-APPL-1 | Applicability Declaration per §5: State / Identity / Evidence `ACTIVE` | pre-mutation declaration file |
| INV-STOP-1 | C20 control-validity stop rule + 5 INSA-BIB stop rules remain authoritative | pre-mutation stop-rule file referenced |

### 5.2 Two-arm matched-pair design

- **Arm C** (control): frozen intent, modification = no-op directive.
- **Arm M** (modification): same frozen baseline + frozen modification specification.

`B` includes: intent document (`D`), identity contract (`O`), test corpus, evaluator rubric, evaluator identity (model + version + invocation substrate).

`M` must be additive (does not remove existing intent content), bounded, auditable post-hoc against the frozen spec.

`P` is enumerated as **two disjoint subsets** (per INV-P-1):
- **Subset-(a):** the calibrated BIB 4-dimensional behavior vector (primary identity metric; §11.2-style Manhattan distance criterion preserved).
- **Subset-(b):** the 8 explicit C12 non-target preservation axes — exact-date preference, connection count 5–10, selection significance, end-of-report synthesis, lifetime framing, warm/vivid narrative voice, factual discipline, avoidance of arbitrary trivia.

`V(d)` is frozen per-dim, defined separately for subset-(a) and subset-(b).

`A` is bound to `M`. PASS requires per-evaluator independent satisfaction.

`G` is bound to `P` (covering both subsets). PASS requires per-evaluator independent satisfaction across both subsets.

### 5.3 Causal traceability (the final evidence must trace to the pre-bound controls)

The final evidence package must demonstrate not merely that preservation occurred, but that the result can be traced to the pre-bound INSA controls. Specifically:

- Every claim of "preservation held at dimension `d`" must cite the frozen `G_d` gate, the frozen `V(d)` value, the subset that `d` belongs to (subset-(a) or subset-(b)), the frozen baseline's per-dim behavior at dimension `d`, and the difference between Arm M and Arm C at dimension `d`.
- Every claim of "modification succeeded at dimension `m`" must cite the frozen `A_m` acceptance test, the frozen `M` specification, the evaluator's recorded M-check outcome, and the aggregated gate result.
- Every authority claim must cite the recorded authority manifest's scope, grant authenticity, and freshness evidence at the M-commit boundary.
- Every applicability claim must cite the Applicability Declaration file and its SHA.

This causal-trace requirement prevents post-hoc narrative from connecting observed preservation to the INSA controls by coincidence — the trace must be *pre-bound* to the controls, not invented at analysis time.

### 5.4 Decision tree (joint, not ordered ELSE IF)

This corrects the v0.1 decision-tree defect that produced the v0.1 `MODIFICATION_AND_PRESERVATION_FAILURE` classification (per C-3 PI freeze correction in dbi-evolution-v0.1 protocol §0).

```
PRE-CHECKS (must all PASS to enter substantive analysis; each pre-check
           failure produces a non-architectural disposition):
  INV-AUTH-* (executor authority manifest, scope, freshness)
  INV-EVID-1 (evidence chain integrity)
  INV-APPL-1 (Applicability Declaration ACTIVE)
  C20 (Arm C satisfies frozen baseline envelope on its own; NO tolerance added to Arm C)
  Evaluator availability (per INV-AUTH-1 evaluator identity check)
  Evaluator blinding intact

  If any pre-check fails:
     - Evaluator unavailable        -> EVALUATOR_GATING_FAILURE
     - Evaluator blinding broken   -> INVALID_EXPERIMENT
     - Arm C fails own envelope     -> INVALID_EXPERIMENT (no Arm M analysis;
                                       confounding possible runtime drift)
     - Authority manifest missing  -> INVALID_EXPERIMENT
     - Applicability not ACTIVE     -> INVALID_EXPERIMENT
     - Evidence chain integrity    -> INVALID_EXPERIMENT

STEP 1 - Compute per-evaluator (no pooling):

  Modification_Success = G_mod_a AND G_mod_b AND G_mod_c AND G_mod_d
                         (binding to M; a..d are the per-M acceptance tests)

  Non-target_Identity_Preservation = G_pres_subset-a AND G_pres_subset-b
                                     AND no C12-axis-BROKEN
                                     (binding to P; subset-a = calibrated
                                      BIB 4-dim vector gates, subset-b =
                                      the 8 C12 axes gates; a per-axis
                                      C12-axis-BROKEN call is a hard fail
                                      on that axis)

STEP 2 - Apply §5.5 runtime classification (transient vs systematic) BEFORE
           substantive analysis. Per §5.5:
           - Transient/candidate-scoped failures do NOT erase unaffected candidates.
           - Systematic runtime failure (threshold met) triggers
             EXECUTOR_RUNTIME_FAILURE; in that case substantive M/P analysis
             stops for the affected substrate, and the disposition is set per
             §5.5.
           - Otherwise proceed to STEP 3 using the unaffected candidates.

STEP 3 - Substantive classification (only after pre-checks and the §5.5
          transient/systematic ruling):

  If (Modification_Success = TRUE for both evaluators)
     AND (Non-target_Identity_Preservation = TRUE for both evaluators)
     AND (Contemporaneous_Control_Validity = TRUE)
     -> DISPOSITION = ARCHITECTURAL_PASS  (renamed from EVOLUTION_PASS
         to make explicit that this is an architecture-level claim,
         not an application-level general claim)

  ELSE classify the substantive failure(s) FIRST:

    If (Modification_Success = FALSE for either evaluator)
       AND (Non-target_Identity_Preservation = TRUE for both evaluators)
       -> DISPOSITION = MUTATION_FAILURE

    If (Modification_Success = TRUE for both evaluators)
       AND (Non-target_Identity_Preservation = FALSE for either evaluator)
       -> DISPOSITION = PRESERVATION_FAILURE

    If (Modification_Success = FALSE for either evaluator)
       AND (Non-target_Identity_Preservation = FALSE for either evaluator)
       -> DISPOSITION = MODIFICATION_AND_PRESERVATION_FAILURE
         (only counts as architectural falsification after runtime
          and evaluator explanations ruled out; see §4)

STEP 4 - Only after all substantive outcomes exhausted:
  If (no substantive failure but residual ambiguity)
  -> DISPOSITION = INCONCLUSIVE_PENDING_FURTHER
  (reserved for genuine ambiguity, never used to soften substantive failures)
```

The names of substantive dispositions changed from the v0.1 protocol (`EVOLUTION_PASS` → `ARCHITECTURAL_PASS`; `INCONCLUSIVE_PENDING_FURTHER` retained for residual ambiguity only) to make the architecture-vs-runtime distinction explicit. `EXECUTOR_RUNTIME_FAILURE` is a new disposition class that does not appear in v0.1; it exists specifically because runtime failure must not become architecture evidence.

---

### 5.5 EXECUTOR_RUNTIME_FAILURE — preregistered transient vs systematic distinction (v3 tightening)

v2's STEP 2 effectively said: any observed runtime failure stops all substantive M/P analysis. v3 corrects this: a transient or candidate-scoped runtime failure must not erase otherwise valid substantive evidence, while a *systematic* runtime defect that makes the treatment uninterpretable must still stop architectural inference. The following is preregistered before execution.

**5.5.1 Candidate-level transient/runtime failure (does NOT erase unaffected candidates):**
- A timeout, refusal, capacity error, or model-invocation fault on a *single candidate* is a candidate-level transient failure.
- Permitted response: log the failure, retain the empty/incomplete output as raw-replayable evidence, and continue with unaffected candidates. If the OS-CSPRNG draw permits N candidates per (R, B) cell and one candidate fails transiently, the remaining N−1 candidates are analyzed normally.
- A failed candidate is *never* silently replaced with another candidate's output; replacement requires a re-draw under the preregistered `EXECUTION-ORDER.md` rules, if any. Replacement is itself a logged event.
- Per-evaluator analysis proceeds on whatever candidates successfully produced output for that evaluator.

**5.5.2 Experiment-level threshold for systematic classification:**
A runtime failure is classified as **systematic** (and triggers `EXECUTOR_RUNTIME_FAILURE`) when **any** of the following holds:
- (T1) ≥ 50% of candidates across the experiment fail with a runtime error of the same root-cause class (e.g., all timeout-class, or all refusal-class, or all capacity-class).
- (T2) Failures are correlated with the treatment (e.g., all failures occur on Arm M and none on Arm C under identical executor and draw), which would make the treatment effect uninterpretable.
- (T3) Failures span both evaluators and both arms with no candidate producing a complete output for any (R, B) cell — i.e., the executor substrate is effectively unavailable for this experiment.

The threshold is preregistered; it is **not** tightened or relaxed after observing outcomes.

**5.5.3 What remains analyzable when the threshold is met:**
- When systematic classification triggers, `EXECUTOR_RUNTIME_FAILURE` is the disposition. Architectural interpretation is *not* assigned to the affected substrate for this experiment.
- Unaffected candidates (if any) are **not** retroactively re-classified to a substantive disposition; doing so would conflate "we couldn't observe" with "we observed failure."
- Any candidate that *did* produce complete output before the threshold trip is preserved as raw evidence and may inform the per-candidate failure analysis (e.g., is there a pattern distinguishing successful vs failed candidates?), but does **not** become the basis of an architectural disposition.

**5.5.4 Retry/replacement policy (preregistered):**
- A candidate-level transient failure is logged; no automatic retry.
- Re-execution of the entire experiment (with a fresh draw) is permitted only under explicit Frank-as-PI authorization, *not* under operator discretion. A re-execution is itself a deviation-record event and produces a fresh `MANIFEST.json`.
- Evaluator substitution after observing candidates is forbidden (per §8 GO constraints).

**5.5.5 Why this matters:**
A candidate timeout, refusal, or provider fault must not automatically erase otherwise valid substantive evidence (v2's defect). Conversely, a systematic runtime defect that makes the treatment uninterpretable must stop architectural inference (which v2's rule did, but by over-inclusion). v3 separates these by the preregistered thresholds T1/T3 above.

**5.5.6 Representation in the contract tuple:**
Every term in the declared pre-bound contract `B + D + M + P + O + V(d) + A + G` is explicitly represented and content-addressed in `MANIFEST.json`. Specifically: `D` (intent document) and `O` (identity contract) have explicit frozen artifacts in §7 (`inputs/intent-document.txt`, `inputs/identity-contract.txt`) and pre-mutation SHAs (INV-D-1, INV-O-1). Neither `D` nor `O` remains implicit.

---

## 6. Success / failure criteria mapped to §3 dispositions

| Disposition | What it means | Architectural implication |
|---|---|---|
| `ARCHITECTURAL_PASS` | A passes, G passes, both evaluators independent, control valid, no runtime failure | INSA v0.3's Safe Evolution Contract supports this modification class as bound |
| `MODIFICATION_AND_PRESERVATION_FAILURE` | Both M and G failed AND runtime/executor causes ruled out (§4 falsifier condition) | **Architectural falsification** — INSA v0.3's structure is insufficient for this modification class |
| `PRESERVATION_FAILURE` | M passed; G failed | INSA's preservation structure is fine; the *specific* P contract is too narrow OR preservation is genuinely hard for this class |
| `MUTATION_FAILURE` | M failed; G held | INSA's structure is fine; the *specific* M gate is too strict OR the modification wasn't expressible |
| `EXECUTOR_RUNTIME_FAILURE` | Executor failed at runtime (timeout, deferral, refusal, capacity) | Execution fault; not architectural unless repeatable across executors |
| `EVALUATOR_GATING_FAILURE` | Evaluator unavailable or materially changed | Measurement fault; not architectural |
| `INVALID_EXPERIMENT` | Pre-check failure (control, blinding, applicability, evidence chain) | Measurement fault; not architectural |
| `INCONCLUSIVE_PENDING_FURTHER` | No substantive failure but residual ambiguity (reserved) | Report ambiguity; never used to soften substantive failures |

For all non-arch-pass dispositions, the report must explain which pre-check / runtime / evaluator / gating cause was ruled out and how.

---

## 7. Required artifacts

Before execution (frozen pre-execution):
- `inputs/intent-document.txt` — `D` content-addressed; INV-D-1
- `inputs/identity-contract.txt` — `O` content-addressed; INV-O-1
- `inputs/baseline-envelope-membership.json` — content-addressed (§11 / §13 envelope)
- `inputs/modification-specification.txt` — frozen M, content-addressed
- `inputs/arm-c-directive.txt` — frozen no-op control, content-addressed
- `inputs/applicability-declaration.json` — INSA v0.3 §5 binding
- `inputs/authority-manifest.json` — INSA v0.3 §8 binding (I-AUTH-*)
- `inputs/evaluator-rubric.json` — frozen V(d) for both subset-(a) and subset-(b), content-addressed
- `inputs/preservation-dimensions-subset-a.json` — frozen subset-(a): calibrated BIB 4-dim behavior vector rubric (primary identity metric)
- `inputs/preservation-dimensions-subset-b.json` — frozen subset-(b): the 8 C12 non-target preservation axes list, with per-axis tolerance values
- `inputs/preservation-dimensions.json` — frozen P binding (subset-(a) ∪ subset-(b)) with non-collapse attestation
- `inputs/mutation-dimensions.json` — frozen M
- `inputs/acceptance-tests.json` — frozen A, bound to M
- `inputs/preservation-gates.json` — frozen G, bound to P (covering both subset-(a) and subset-(b))
- `protocol/INSA-ID-E1-protocol.md` — frozen, content-addressed
- `protocol/EXECUTION-ORDER.md` — OS-CSPRNG draw, content-addressed
- `MANIFEST.json` — binds all of the above by SHA-256, references INSA v0.3 blob `848e0fe…`

During execution (per-run):
- Raw candidate outputs (immutable; raw-replayable)
- Evaluator input packets (blinded)
- Evaluator scorebooks (locked, content-addressed)
- Deviation records (any material deviation)
- Per-step timestamps and runtime metadata

After execution (per-result):
- `results/score-independent.md` (locked evaluator scores)
- `results/analysis.md` (reconstruction-level → per-arm → matched → pooled, **with causal trace per §5.3**)
- `results/disposition.md` (the §5.4 disposition, with explicit cause-ruling-out for any non-arch-pass class)
- `results/unblinded-analysis-results.json` (canonical record)
- `results/de-blinding-table.json` (auditable)

After synthesis:
- `synthesis.md` (final adjudication; PI signs)
- `REPORT-<date>-INSA-ID-E1.md` (research-level writeup)

---

## 8. Authorization boundary for GO

**This proposal is NOT execution authorization.** Protocol construction and frozen-artifact preparation may proceed, but execution requires a separate Frank-as-PI GO.

When the protocol is authored and the frozen pre-execution artifacts are produced, Frank-as-PI must issue a separate explicit GO referencing:

- this proposal (`docs/proposals/2026-09-10-INSA-ID-E1-proposal.md` or its committed equivalent),
- the frozen pre-execution artifacts by SHA-256,
- the frozen INSA v0.3 source by blob `848e0fe014f5b4a61ba2cb92e772ee3499dca9c1`,
- and the executor authority manifest.

The GO authorizes execution ONLY. It does NOT authorize modifications to the frozen pre-execution artifacts. Any material deviation triggers the preregistered deviation rule (STOP unless PI separately adjudicates).

**Specifically NOT authorized in this GO:**
- Any change to the frozen v0.3 architecture (`848e0fe…`).
- Any change to the dbi-evolution-v0.1 protocol (separate artifact, separate lineage).
- Any modification to `B + D + M + P + O + V(d) + A + G` after protocol freeze.
- Any evaluator substitution after observing candidates.
- Any retroactive weakening of gates or thresholds after observing outcomes.
- Any change to the §5.4 decision tree semantics (joint, not ordered ELSE IF).
- Any retroactive reclassification of a substantive failure as `INCONCLUSIVE_PENDING_FURTHER`.
- Any model dispatch without preflight verification per INSA v0.3 §6.
- Any force-push / rebase / repository-modification outside the canonical experiment directory.

---

## 9. What this proposal does NOT claim (consolidated)

- That INSA-ID-E1 alone will validate INSA v0.3 across all applications, executors, or modification types.
- That a PASS result generalizes beyond the specific modification class tested.
- That the corrections in v0.3 are sufficient for unbounded evolution; the Safe Evolution Contract explicitly bounds `V(d)` per dimension.
- That future INSA versions (v0.4+) are addressed by this proposal.
- That the frozen v0.3 architecture is "correct" — only that its bounded execution is testable.
- That `PRESERVATION_FAILURE` or `MUTATION_FAILURE` alone is architectural falsification. Only `MODIFICATION_AND_PRESERVATION_FAILURE` (after ruling out runtime/evaluator/pre-check causes) is. Even then, per §4.1, it strengthens concern toward §12's general structure but does *not* equate to §12 invalidity. Single-axis failures falsify Level 1 on one axis and leave Level 2 underdetermined.

---

## 10. Risk analysis (what could go wrong)

1. **Insufficient evaluator availability.** INSA-ID-E1 requires evaluator-blind independent scoring. If the v0.1 evaluator substrate (Codex gpt-5.6-sol + Claude Opus 4.7) is unavailable or materially changed at execution time, STOP per the preregistered evaluator-availability stop rule → `EVALUATOR_GATING_FAILURE`. No evaluator substitution after observing candidates.
2. **Runtime drift in Arm C.** C20 fails → STOP, classify `INVALID_EXPERIMENT` (no further analysis). The +1.5 Manhattan tolerance applies only to Arm M relative to Arm C, never enlarges Arm C's validity envelope.
3. **Re-deriving the v0.1 failure shape.** If the failure is concentrated in R2's deferral pattern again, classify as `EXECUTOR_RUNTIME_FAILURE` and report — even though the v0.1 result used `MODIFICATION_AND_PRESERVATION_FAILURE`, the v0.3-corrected experiment must correctly separate runtime causes from architectural ones.
4. **Modifying frozen artifacts mid-execution.** Disallowed by INSA v0.3's freeze rule and by this proposal. Any material deviation triggers STOP unless PI separately adjudicates.
5. **Generalization beyond this one experiment.** Out of scope.

---

## 11. Path forward

1. Frank approves this proposal as-is or with changes.
2. Proposal is committed on a dedicated branch (suggested name: `feature/insa-id-e1-proposal`).
3. Protocol authoring begins: `protocol/INSA-ID-E1-protocol.md` plus the frozen pre-execution artifacts listed in §7 (16 files: 13 in `inputs/` + 2 in `protocol/` + `MANIFEST.json`). All content-addressed. No modifications to the dbi-evolution-v0.1 protocol (separate artifact, separate lineage) and no modifications to the INSA v0.3 frozen architecture.
4. When protocol + artifacts are ready, Frank-as-PI issues a separate explicit GO referencing the frozen SHAs.
5. Execution begins from the preregistered preflight gate.
6. If `ARCHITECTURAL_PASS`: per §4.1 Level 1 is supported (both axes held on the bound contract) and Level 2 raises no architectural concern from this experiment. §12's structure is *consistent with* supporting this modification class; v3 does *not* claim this generalizes beyond the bound.
7. If `MODIFICATION_AND_PRESERVATION_FAILURE` (after ruling out runtime/evaluator/pre-check per §4 + §5.5): per §4.1, Level 1 is falsified on both axes and Level 2 strengthens concern toward §12's general structure for this modification class, but **does not equate to §12 invalidity**. v0.4 work scope.
8. If `PRESERVATION_FAILURE` or `MUTATION_FAILURE` alone: per §4.1, Level 1 is falsified on one axis and Level 2 remains underdetermined. Bound-contract refinement (specific `P` or `M`/`V(d)` was too narrow) is the likely remediation; v0.3 structure held on the unaffected axis.
9. If `EXECUTOR_RUNTIME_FAILURE` (systematic per §5.5) or `EVALUATOR_GATING_FAILURE` or `INVALID_EXPERIMENT`: not architectural. Per §5.5, when systematic threshold is met, no architectural disposition is assigned; report and decide whether to retry with corrected constraints under §5.5.4.

If Frank prefers different priorities (e.g., testing I-AUTH-* first via a smaller-scale experiment, or attacking I-IDENT-01..02 directly, or running a non-architectural behavioral experiment first), I revise this proposal before committing.

If Frank wants to skip INSA-ID-E1 entirely and run a different Stage-4 experiment, that's also a valid direction — but per CURRENT-STATUS.md, "Stage 4 currently has zero completed experiments explicitly designed to test the frozen INSA architecture." That zero is the gap this proposal is meant to close.

---

**End of proposal v2. Awaiting review.**

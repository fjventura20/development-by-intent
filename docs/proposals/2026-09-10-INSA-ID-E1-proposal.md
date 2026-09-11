# INSA-ID-E1 — Targeted Evolution With Preservation (proposal)

**Status:** v2 — Frank's six tightening changes incorporated. Committed on `feature/insa-id-e1-proposal` @ `5f9365f`. Awaiting Frank's review of the proposal text itself before protocol authoring begins.
**Author:** Hermes (operator).
**Date:** 2026-09-10
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

A provider, executor, or infrastructure failure **must not automatically become evidence against the architecture**. The disposition tree is split into failure-classes that map to distinct architectural interpretations.

| Disposition class | Architectural interpretation |
|---|---|
| `ARCHITECTURAL_FAILURE` | §12 structure insufficient under correct instantiation and execution — INSA's Safe Evolution Contract cannot support this modification class as bound |
| `PRESERVATION_FAILURE` | Modification succeeded under `A`, but declared preservation `G` failed — the contract structure is fine; the per-dimension preservation contract is too narrow OR preservation is genuinely hard for this class |
| `MUTATION_FAILURE` | Modification `A` failed; preservation `G` held — the contract structure is fine; the per-dimension mutation gate is too strict OR the modification wasn't expressible |
| `EVALUATOR_GATING_FAILURE` | Evaluator unavailable, materially changed, or blinding broken | Substantive interpretation impossible — execution fault, not architectural fault |
| `EXECUTOR_RUNTIME_FAILURE` | Executor (the intelligent implementation under test) failed at runtime (timeout, deferral, refusal, capacity, model invocation fault) | Execution fault; not architectural unless repeatable across executors and instances |
| `INVALID_EXPERIMENT` | Pre-check failed: applicability declaration missing, frozen artifacts not bound, baseline envelope failure, control arm fails pre-checks | Substantive interpretation impossible — measurement fault, not architectural fault |

**No class may be silently collapsed into another.** `EXECUTOR_RUNTIME_FAILURE` and `EVALUATOR_GATING_FAILURE` and `INVALID_EXPERIMENT` are reporting classes that STOP the substantive analysis. Only `ARCHITECTURAL_FAILURE`, `PRESERVATION_FAILURE`, and `MUTATION_FAILURE` produce evidence about the architecture.

---

## 4. Architectural falsifier (defined before execution)

Per Frank's directive, the architectural falsifier is **stated explicitly before execution** so the experiment cannot be reinterpreted post-hoc.

**What result would force the conclusion that the v0.3 Safe Evolution Contract is insufficient even when correctly instantiated and executed?**

The architectural falsifier is:

> A result in which, after all runtime / evaluator / pre-check failures are correctly separated out and **not** counted as evidence against the architecture, and after the experiment is determined to have been correctly bound (`B + D + M + P + O + V(d) + A + G` content-addressed at protocol freeze, authority manifest valid, applicability declaration ACTIVE, evaluators blinded, control arm valid), **the joint disposition `MODIFICATION_AND_PRESERVATION_FAILURE` is recorded with substantive failures in both axes**.

This corresponds to the v0.1 disposition, but **only** if all runtime / evaluator / pre-check causes have been ruled out. The pre-freeze `MODIFICATION_AND_PRESERVATION_FAILURE` was partially explained by R2's deferral pattern; the v0.3-corrected experiment's same-named disposition must be free of such explanations to count as architectural falsification.

**Note:** `PRESERVATION_FAILURE` alone is **not** architectural falsification of the Safe Evolution Contract itself — it falsifies the *specific* preservation contract bound at protocol freeze, and v0.4+ may need to refine `P` or `V(d)`. Similarly, `MUTATION_FAILURE` alone falsifies the *specific* mutation specification, not the contract structure.

A `PRESERVATION_FAILURE` or `MUTATION_FAILURE` is still informative: it narrows the v0.3 corrections' sufficiency to "supports this modification class with *narrower* preservation / mutation bounds." Either way, the experiment advances INSA — it just doesn't falsify §12 specifically.

---

## 5. Experimental design

### 5.1 Frozen pre-execution invariants (must all hold before generation)

| ID | Invariant | Verification |
|---|---|---|
| INV-B-1 | Frozen baseline `B` content-addressed (intent + identity + tests + rubric + evaluator identity); pre-mutation SHA inventory recorded | `git hash-object` on the bound files; pre-mutation SHAs preserved as evidence |
| INV-M-1 | `M` enumerated with frozen per-dimension specification; additive; bounded scope | modification-spec file SHA + size + line count |
| INV-P-1 | `P` enumerated: at minimum the dimension set used for the BIB identity baseline (BIB's 4-dim behavior vector) + factual discipline (an INSA addition) + evidence chain integrity (an INSA addition) | per-dimension rubric SHA + per-dim binding to rubric |
| INV-V-1 | `V(d)` frozen per-dimension | rubric-version SHA + per-dim frozen tolerance values |
| INV-A-1 | `A` bound only to `M`; per-dimension acceptance tests | per-M-test file SHA + evaluator-blinding manifest |
| INV-G-1 | `G` bound only to `P`; per-dimension preservation gates | per-P-gate file SHA + evaluator-blinding manifest |
| INV-AUTH-1 | Executor's authority manifest recorded; capability vs permission separated (I-AUTH-01) | authority manifest SHA + pre-mutation scope statement |
| INV-AUTH-2 | Authority grant authentic, traceable (I-AUTH-06, I-AUTH-08) | grant provenance recorded |
| INV-AUTH-5 | Freshness before consequential commit (I-AUTH-05); the consequential-action boundary is the M-commit | freshness evidence captured at M-commit boundary |
| INV-EVID-1 | Evidence chain cross-cuts (§14); evidence profile, not evidence ladder | per-step evidence captured; locking at evaluator output |
| INV-APPL-1 | Applicability Declaration per §5: State / Identity / Evidence `ACTIVE` | pre-mutation declaration file |
| INV-STOP-1 | C20 control-validity stop rule + 5 INSA-BIB stop rules remain authoritative | pre-mutation stop-rule file referenced |

### 5.2 Two-arm matched-pair design

- **Arm C** (control): frozen intent, modification = no-op directive.
- **Arm M** (modification): same frozen baseline + frozen modification specification.

`B` includes: intent document, identity contract, test corpus, evaluator rubric, evaluator identity (model + version + invocation substrate).

`M` must be additive (does not remove existing intent content), bounded, auditable post-hoc against the frozen spec.

`P` includes: the 4 BIB dimensions (selection significance, end-of-report synthesis, lifetime framing, factual discipline), factual discipline (INSA addition), evidence chain integrity (INSA addition).

`V(d)` is frozen per-dim.

`A` is bound to `M`. PASS requires per-evaluator independent satisfaction.

`G` is bound to `P`. PASS requires per-evaluator independent satisfaction.

### 5.3 Causal traceability (the final evidence must trace to the pre-bound controls)

The final evidence package must demonstrate not merely that preservation occurred, but that the result can be traced to the pre-bound INSA controls. Specifically:

- Every claim of "preservation held at dimension `d`" must cite the frozen `G_d` gate, the frozen `V(d)` value, the frozen baseline's per-dim behavior at dimension `d`, and the difference between Arm M and Arm C at dimension `d`.
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
  Modification_Success = G_mod_a AND G_mod_b AND G_mod_c AND G_mod_d (binding to M)
  Non-target_Identity_Preservation = G_pres_a AND G_pres_b AND no C12-axis-BROKEN
                                      (binding to P)

STEP 2 - Disjoint classification by failure-class:

  If executor/runtime failures observed in generation OR evaluator substrate:
     -> EXECUTOR_RUNTIME_FAILURE
     (do not analyze M or P; report execution failure; do not assign
      architectural interpretation)

STEP 3 - Substantive classification (only after pre-checks and executor
          runtime both ruled out):

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
- `inputs/baseline-envelope-membership.json` — content-addressed (§11 / §13 envelope)
- `inputs/modification-specification.txt` — frozen M, content-addressed
- `inputs/arm-c-directive.txt` — frozen no-op control, content-addressed
- `inputs/applicability-declaration.json` — INSA v0.3 §5 binding
- `inputs/authority-manifest.json` — INSA v0.3 §8 binding (I-AUTH-*)
- `inputs/evaluator-rubric.json` — frozen V(d), content-addressed
- `inputs/preservation-dimensions.json` — frozen P
- `inputs/mutation-dimensions.json` — frozen M
- `inputs/acceptance-tests.json` — frozen A, bound to M
- `inputs/preservation-gates.json` — frozen G, bound to P
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
- That `PRESERVATION_FAILURE` or `MUTATION_FAILURE` alone is architectural falsification. Only `MODIFICATION_AND_PRESERVATION_FAILURE` (after ruling out runtime/evaluator) is. The other failures falsify the *specific* bound contract, not the Safe Evolution Contract structure.

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
3. Protocol authoring begins: `protocol/INSA-ID-E1-protocol.md` plus the 11 frozen pre-execution artifacts. All content-addressed. No modifications to the dbi-evolution-v0.1 protocol (separate artifact, separate lineage) and no modifications to the INSA v0.3 frozen architecture.
4. When protocol + artifacts are ready, Frank-as-PI issues a separate explicit GO referencing the frozen SHAs.
5. Execution begins from the preregistered preflight gate.
6. If `ARCHITECTURAL_PASS`: INSA v0.3's Safe Evolution Contract has evidence for this modification class. Report and consider whether to expand or stop.
7. If `MODIFICATION_AND_PRESERVATION_FAILURE` (after ruling out runtime/evaluator): **architectural falsification** of v0.3's structure for this class. v0.4 work scope.
8. If `PRESERVATION_FAILURE` or `MUTATION_FAILURE` alone: bound-contract refinement. v0.3 structure held; the specific `P` or `M`/`V(d)` was too narrow.
9. If `EXECUTOR_RUNTIME_FAILURE` or `EVALUATOR_GATING_FAILURE` or `INVALID_EXPERIMENT`: not architectural. Report and decide whether to retry with corrected constraints.

If Frank prefers different priorities (e.g., testing I-AUTH-* first via a smaller-scale experiment, or attacking I-IDENT-01..02 directly, or running a non-architectural behavioral experiment first), I revise this proposal before committing.

If Frank wants to skip INSA-ID-E1 entirely and run a different Stage-4 experiment, that's also a valid direction — but per CURRENT-STATUS.md, "Stage 4 currently has zero completed experiments explicitly designed to test the frozen INSA architecture." That zero is the gap this proposal is meant to close.

---

**End of proposal v2. Awaiting review.**

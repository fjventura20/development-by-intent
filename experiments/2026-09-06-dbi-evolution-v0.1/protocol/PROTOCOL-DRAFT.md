# DbI Evolution Experiment — Protocol v0.1 (DRAFT — not frozen)

**Status:** DRAFT — methodology-collaborator stage. NOT frozen. NOT preregistered.
**Author (design):** Frank Ventura (PI)
**Drafter (this v0.1):** Hermes Agent (operator, methodology-collaborator mode)
**Date drafted:** 2026-09-06
**Prior experimental boundary:** `d01246f` (DBI-BIB-002 EVALUATED, PATTERN_NOT_REPRODUCED)
**Prerequisite:** BIB completed (BIB-001 INCONCLUSIVE retained; BIB-002 PATTERN_NOT_REPRODUCED supports that the behavioral-identity measurement is stable enough to serve as control foundation)
**Authorization required:** YES — separate Frank-as-PI GO referencing this protocol's frozen commit

---

## 0. What this draft is and is not

**This document is a draft.** It exists to surface design confounds for PI adjudication before any preregistration is committed. Inline `[CONFOUND]` markers call out choices that materially affect interpretation; each must be resolved before freeze.

This draft is NOT:
- A preregistered protocol (no frozen commit, no GO referencing it, no generation authorized).
- A final design (will change after the confounds below are adjudicated).
- An execution order (operator MUST NOT generate candidates until this protocol is explicitly frozen and a separate GO is received).

---

## 1. Research question

**Can a developer change an application by changing its expressed intent, while preserving the application's established behavioral identity outside the intended modification?**

Restated: given a frozen baseline intent specification that has been shown to produce a stable family of independently reconstructed behaviors (BIB evidence), does a controlled, single-axis intent modification cause the reconstruction to (a) actually exhibit the intended new behavior on the targeted axis AND (b) preserve the established behavioral contract on all non-targeted axes?

Both (a) and (b) must be true. A new behavior with no constraint is trivial; an unchanged behavior with no novelty is the BIB result. The DbI claim becomes interesting only at the conjunction.

---

## 2. Why this is the right next experiment

Per BIB protocol §24 the experimental sequence was:

1. Frozen intent → independent reconstructions → measure natural variance → **establish identity baseline** ← COMPLETE (BIB-001 + BIB-002)
2. Frozen original intent → controlled intent modification → independent reconstruction → **measure intended behavioral change → compare unchanged behaviors against baseline** ← THIS PROTOCOL
3. (After Evolution) DbI Evidence Brief v0.2

The BIB evidence currently establishes:
- Baseline within-Recon Manhattan mean (non-deviated subset): ~0.5-1.0 (Evaluator A) / ~0.08 (Evaluator B)
- Baseline between-Recon Manhattan mean (non-deviated subset): ~1.4 / ~0.08
- Baseline identity-preservation agreement across evaluators: 1.0
- Baseline per-dim MAE: all ≤ 0.72 (most ≤ 0.4)
- Identity-Classification distribution (60 candidates, BIB-001 non-deviated subset): ~95% SAME/SWV
- The R4/B cluster is the documented deviation, not a baseline property

These quantities form the "control envelope" against which Evolution is evaluated.

---

## 3. The six things Frank said to freeze (mapped to design elements)

| Frank's requirement | Design element in this draft | Status |
|---|---|---|
| Modification specification | §5 — what behavior changes, what stays invariant | [CONFOUND: specificity of the modification] |
| Baseline/control conditions | §6 — unmodified reconstructions vs modified-intent reconstructions | [CONFOUND: matched-control design] |
| Identity-preservation criteria | §7 — reuse BIB behavioral dimensions | [CONFOUND: which BIB dimensions carry over] |
| Modification-success criteria | §8 — separate scoring for whether new behavior appears | [CONFOUND: how to measure modification success] |
| Outcome thresholds | §9 — PASS / FAIL / INCONCLUSIVE rules | [CONFOUND: preregistered thresholds] |
| Role separation + evidence chain | §10 — modification-spec holder, generator, evaluators, adjudicator | [CONFOUND: who holds what] |

---

## 4. Core experimental structure (proposed)

A two-arm matched design:

**Arm C — Control** (unchanged baseline intent)
- Re-uses frozen `03-behavioral-baseline.md` and `RECONSTRUCTION-PROMPT.md` byte-identical to BIB-001/002
- 3 fresh independent reconstruction sessions, each: A/T1-T5 + B/T1-T5 = 10 candidates
- Total: 30 candidates
- Purpose: provide contemporaneous matched-control evidence for any non-target behavioral drift attributable to model/runtime drift between the BIB era and the Evolution era

**Arm M — Modified intent** (single-axis intent modification)
- Re-uses frozen `03-behavioral-baseline.md` and `RECONSTRUCTION-PROMPT.md` PLUS a frozen modification specification document that names exactly one behavioral change
- 3 fresh independent reconstruction sessions, same shape (A/T1-T5 + B/T1-T5 = 10 candidates each)
- Total: 30 candidates
- Purpose: test whether the modified intent produces the targeted behavioral change while preserving non-target behaviors

**Total candidates: 60** (30 control + 30 modified)

Why 3 reconstructions × 2 blocks × 5 tests per arm:
- BIB-002 design (3 fresh reconstructions) was sufficient to test the R4/B confirmation with high statistical signal
- The matched-control + modified-intent pair design doubles that for Evolution
- No Expansion Rule (BIB protocol §21) inherited; further expansion requires new authorization

**[CONFOUND C1 — Arm size]** Three reconstructions per arm is enough to test the question, but is below the 6-reconstruction BIB baseline. Justification: this is a different question (modification success + preservation, not baseline establishment) and the matched-control structure halves the per-arm variance relative to the BIB design. Alternative: 6 reconstructions per arm = 60 control + 60 modified = 120 candidates. PI to confirm.

**[CONFOUND C2 — Generation runtime]** Per BIB protocol the runtime was Claude Sonnet 4.6. The Evolution experiment should use the same runtime for arm comparability. Operator concern: if Claude Sonnet 4.6 model access has changed (newer Sonnet, deprecated version), this introduces a confound between the BIB baseline and the Evolution arm. Mitigation: lock the exact model identifier AND claude-code CLI version at preflight; record any drift.

**[CONFOUND C3 — Evaluator identity]** BIB used Codex gpt-5.6-sol and Claude Opus 4.7. Evolution should use the same two evaluators with the same blind scoring protocol. If either has become unavailable, the experiment is BLOCKED until resolved.

---

## 5. Modification specification (the heart of the experiment)

This is the single most important design decision. The modification must be:
1. **Specific** — one observable behavioral axis
2. **Small** — only the targeted behavior should change
3. **Testable** — evaluators can decide yes/no on whether the change occurred
4. **Not already implicit** — the modification must NOT be derivable from the existing baseline contract

Candidate modifications (PI to select one or propose alternative):

**Option A: Format modification — change the report structure**
- Current contract: "10 numbered behavioral rules" describing what the application does
- Modification: "produce reports as a 5-section structure with named headers" OR "produce reports as continuous prose without numbered sections"
- Testable: evaluator can score whether the format has the named structural property
- Risk: structural formatting may be a surface property that all LLMs would obey regardless of intent, weakening the test

**Option B: Selection modification — change the count of selected connections**
- Current contract: "5-10 standout connections"
- Modification: "exactly 3 connections, no more, no fewer" OR "12-15 connections"
- Testable: literally count the connections in each output
- Risk: trivial to obey; doesn't really test deep intent-following

**Option C: Voice modification — change the narrative voice**
- Current contract: "warm, vivid, engaging narrative voice"
- Modification: "encyclopedic, neutral, third-person voice" OR "first-person reflective voice"
- Testable: evaluators can score voice conformance
- Risk: voice is more aesthetic than behavioral; could be confounded with overall quality

**Option D: Length modification — change the target length**
- Current contract: no explicit length; "substantive" lifetime perspective
- Modification: "produce reports under 600 words" OR "produce reports over 2000 words"
- Testable: word count
- Risk: length is a degenerate axis; doesn't test deep intent-following

**Option E: Source-specific modification — change one factual policy**
- Current contract: "exact-date events preferred"
- Modification: "lead with a worldwide event rather than an exact-date event" OR "explicitly include events within ±30 days"
- Testable: evaluators check whether the report opens with a non-exact-date event or includes nearby events
- Risk: this is closer to the existing "exact-date vs nearby" tension in the contract

**Option F (PI choice)**: whatever Frank selects.

**[CONFOUND C4 — Which modification?]**

**[CONFOUND C5 — Modification specificity]** How granular must the modification specification be? Three candidate formats:
- (a) one-paragraph prose statement
- (b) one-paragraph prose + a few "must" / "must not" lines
- (c) a fully structured modification specification with named rules

Format (b) is recommended as a compromise: preserves natural-language intent expression while being unambiguous about the targeted axis.

**[CONFOUND C6 — Modification doc placement]** Where does the modification specification live? It must be appended to the reconstruction input (so the model sees it as part of the durable artifact), not patched into the existing baseline contract. The existing baseline contract remains the primary reference; the modification is layered on top.

**[CONFOUND C7 — Inverse risk]** What if the modification is so well-obeyed by every model that the experiment passes trivially? The DISCRIMINATING power of the experiment depends on the modification being non-trivial. If a vanilla Sonnet 4.6 reconstruction with a minor format tweak produces reports that all "comply," we learn nothing. Mitigation: include an "anti-pattern" sub-test in the modification spec that explicitly forbids a default behavior the model would otherwise fall into.

---

## 6. Control / baseline arm design

**[CONFOUND C8 — How contemporaneous is contemporaneous?]** The control arm runs in the same operator session as the modified arm, using the same runtime lock, ideally within hours of each other. This controls for model-drift confounders between BIB era (2026-09-06) and Evolution era.

**[CONFOUND C9 — What is "matched"?]** Per-test matched: Arm C T1 must be compared with Arm M T1 (same test prompt). Per-reconstruction matched: Arm C R1 must be compared with Arm M R1 (same session lifecycle). Per-block matched: A vs B within each arm. All three matching levels should be reported.

**[CONFOUND C10 — Use of BIB evidence]** The BIB baseline envelope (within-Manhattan mean ~0.5-1.0, IP agreement 1.0) is the long-run baseline; Arm C is the contemporaneous control. Both should be reported. If Arm C drifts from the BIB envelope, that signals model-drift between BIB and Evolution eras and would require explicit accounting in §11 disposition rules.

---

## 7. Identity-preservation criteria (the non-target axis)

The BIB behavioral dimensions (contract_compliance, selection_behavior, narrative_behavior, functional_completeness) score the baseline contract holistically. For Evolution we need them PLUS a per-axis decomposition that can answer: "did the non-target axes change?"

**[CONFOUND C11 — Dimension reuse vs new scoring]** Three options:
- (a) Reuse BIB dimensions as-is and let them catch any non-target drift via aggregate scores
- (b) Decompose the contract into explicit non-target axes and score each independently
- (c) Hybrid: BIB dimensions for aggregate, plus targeted non-target axes for the modification's inverse risk

Recommendation: (c) Hybrid. Reuse BIB dimensions for the four-axis behavior vector (Manhattan distance remains computable); add a per-axis preservation checklist derived from the modification spec.

**[CONFOUND C12 — Non-target axes enumerated]** What are the non-target axes? They must be enumerated from the existing baseline contract. Candidate list (PI to confirm):
- Exact-date preference policy
- Number of selected connections (5-10 range)
- Connection type mix (significance, selectivity, relevance, anti-filler)
- Lifetime framing (substantial lifetime perspective)
- End-of-report synthesis requirement
- Warm/vivid narrative voice
- Factual discipline (no nearby events misrepresented as exact-date)
- No arbitrary trivia policy

For each non-target axis, define a preregistered evaluation question the evaluators can score yes/no or 0-4.

---

## 8. Modification-success criteria (the target axis)

**[CONFOUND C13 — How to score modification success]** Two layers:
- **Target-axis dimension**: a new 0-4 score "modification_conformance" added to the BIB rubric. The evaluator scores whether the candidate conforms to the modified-intent specification on the targeted axis.
- **Modification-specific checks**: a per-modification list of yes/no or count-based checks (e.g., "report opens with X", "report contains exactly N of Y", "report uses voice Z").

**[CONFOUND C14 — Anti-pattern check]** If the modification spec includes anti-patterns ("MUST NOT do X"), evaluators must explicitly verify non-violation.

---

## 9. Outcome thresholds (PASS / FAIL / INCONCLUSIVE)

This must be preregistered before any data are seen. Proposed:

**Per-arm behavioral identity preservation (the "non-target" claim)**:
- For within-Recon Manhattan distance: Arm M vs Arm C comparison. If Arm M within-mean exceeds Arm C within-mean + a small tolerance (e.g., +1.5 Manhattan points, roughly 2x the BIB baseline), FAIL on the preservation axis.
- For evaluator agreement: same ≥0.9 IP agreement threshold as BIB.

**Modification success (the "target" claim)**:
- A preregistered threshold on the per-arm modification_conformance dimension. (PI to choose.)
- A preregistered count threshold on modification-specific checks. (PI to choose.)

**Joint PASS criterion**: modification success criterion met AND preservation criterion met (both true). Either failing = FAIL on that arm. Mixed results = INCONCLUSIVE_PENDING_FURTHER.

**[CONFOUND C15 — Modification success thresholds]** PI must specify the modification-conformance threshold before freeze. Reasonable starting points (for discussion, NOT preregistered):
- modification_conformance ≥ 3.0 on average across Arm M candidates
- ≥ 70% of Arm M candidates pass modification-specific checks
- but specific values depend on the chosen modification

**[CONFOUND C16 — Preservation tolerance]** The +1.5 Manhattan tolerance is a heuristic. PI to specify or accept. The 55-candidate BIB non-deviated envelope had within-mean ~0.5-1.0 with p95 ≤ 4; setting the tolerance at +1.5 above the contemporaneous Arm C mean is the right operational definition.

**[CONFOUND C17 — Per-arm vs joint]** Should each arm have its own PASS/FAIL or should there be a single joint PASS/FAIL? Proposal: per-arm reported, joint criterion is "Arm M PASSes AND Arm C PASSes" (a failure in Arm C is a contamination issue, not a DbI failure).

---

## 10. Role separation and evidence chain

**[CONFOUND C18 — Who holds what?]**

The BIB protocol designated roles:
- **Protocol Designer** (ChatGPT) — not an evaluator
- **Experiment Operator** (Hermes) — not an evaluator
- **Reconstruction Engine** (one model) — receives only source + modification spec
- **Evaluator A + Evaluator B** — independent, blind to reconstruction identity
- **Final Synthesizer** (ChatGPT) — interprets after both evaluators locked

For Evolution we additionally need:
- **Modification-Spec Holder** — who writes the modification specification document? Must be separate from operator and from evaluators. PI is the natural choice (Frank as modification-spec author).
- **Modification-Spec Freezer** — who decides when the modification spec is final and preregistered? PI, before generation begins.

The leakage risk is highest at the evaluator side: if an evaluator sees the modification specification, they may inadvertently score higher on modification_conformance. Mitigation: the modification specification document is NOT included in the evaluator input packets. Evaluators score against the candidate output alone, using the modification-conformance rubric as a generic prompt ("does the candidate exhibit a controlled behavioral modification consistent with the baseline contract?"). The operator then unblinds and verifies that the modification actually happened by cross-referencing with the modification-spec document, post-lock.

This is the **key role-separation innovation** for Evolution vs BIB. Without it, the experiment collapses into a circular evaluation.

**[CONFOUND C19 — Operator-blinding paradox]** The operator must hold the blind-map AND the modification specification. This means the operator knows both what changed AND which candidate is which. Evaluators must not see either. The unblind happens after both evaluators lock. PI to confirm this role split is operationally robust.

---

## 11. Stop conditions

Inherited from BIB protocol §14:
- Source verification fails → STOP
- Reconstruction engine runtime materially unavailable → STOP
- >1 of 3 reconstructions per arm experiences infrastructure failure → STOP
- Capture integrity unreliable → STOP
- Identity-breaking behavior appears frequently enough that calibration fails → STOP

**[CONFOUND C20 — Evolution-specific stop]** Additional stop: if the control arm (Arm C) drifts outside the BIB non-deviated envelope (e.g., within-mean exceeds the BIB upper bound + a tolerance), STOP. This is evidence of model/runtime drift between BIB era and Evolution era that would invalidate cross-experiment comparison.

---

## 12. Confounds summary (must be resolved before freeze)

| # | Confound | Default proposed | Needs PI decision |
|---|---|---|---|
| C1 | Arm size (3 vs 6 reconstructions per arm) | 3 (BIB-002-style) | YES |
| C2 | Generation runtime drift | Lock exact Claude Sonnet 4.6 + claude-code 2.1.170 | YES |
| C3 | Evaluator availability | Inherit BIB pair; BLOCKED if unavailable | YES (preflight) |
| C4 | Which modification | PI to choose (Options A-F in §5) | YES |
| C5 | Modification specificity format | (b) prose + must/must-not | YES |
| C6 | Modification doc placement | Append to reconstruction input | YES |
| C7 | Inverse risk (trivial compliance) | Include anti-pattern sub-test | YES |
| C8 | Control arm contemporaneous timing | Same operator session, hours apart | agreed |
| C9 | What "matched" means | Per-test + per-recon + per-block | agreed |
| C10 | Use of BIB envelope | Reported alongside Arm C | agreed |
| C11 | Dimension reuse vs new | Hybrid (c) | YES |
| C12 | Non-target axes enumerated | 8 axes from baseline contract (in §7) | YES |
| C13 | Modification success scoring | Target dim + per-mod checks | agreed |
| C14 | Anti-pattern check | Yes, required | agreed |
| C15 | Modification success threshold | (proposed values, PI to confirm) | YES |
| C16 | Preservation tolerance | Arm M within-mean ≤ Arm C within-mean + 1.5 | YES |
| C17 | Per-arm vs joint | Per-arm reported, joint requires both PASS | agreed |
| C18 | Who holds the modification spec | PI (Frank) | YES |
| C19 | Operator-blinding paradox | Operator holds both; evaluators see neither | YES |
| C20 | Evolution-specific stop (model drift) | Arm C within-mean must stay within BIB envelope + tolerance | YES |

**16 of 20 confounds need explicit PI decisions before freeze.** The remaining 4 are proposed defaults that PI may accept or override.

---

## 13. Authorization boundary

**This draft does NOT authorize execution.** Per Frank's instruction: GO means "begin protocol preparation," not "start generation immediately."

The freeze-and-execute sequence:
1. PI adjudicates the 16 confounds above (this document is the discussion artifact).
2. The protocol is amended to reflect PI decisions.
3. A v0.1-frozen commit is created.
4. A separate Frank-as-PI GO references the frozen commit.
5. Operator executes preflight → generation → blinding → evaluator scoring → analysis.
6. Operator returns evidence package for PI adjudication.

Operator will NOT generate any candidates, modify any source artifact, or invoke any evaluator until step 4 is complete.

---

## 14. Operator methodology note (this is what Hermes is for)

The hardest methodological question in this experiment is not statistical. It is conceptual:

**What does it mean for a behavioral change to be "preserved outside the targeted axis"?**

Three candidate interpretations:
- (i) **Pixel-preservation**: every non-targeted dimension scored identically in Arm M and Arm C. Almost certainly unachievable; LLM sampling variance alone will produce drift.
- (ii) **Envelope-preservation**: every non-targeted dimension scored within the BIB-001 + BIB-002 non-deviated envelope baseline. This is the BIB-evidence-grounded definition.
- (iii) **Functional-preservation**: the user-experienced behavior of the application is recognizably the same on non-target dimensions, even if specific scores drift. This is the most defensible but hardest to operationalize.

The protocol needs to commit to one. My recommendation is (ii) Envelope-preservation, with (iii) Functional-preservation as a qualitative interpretation overlay. (i) Pixel-preservation would guarantee FAIL and would be uninformative.

This decision should be made before freeze. Calling it C21.

---

## 15. Next steps (operator proposal)

1. PI adjudicates the confounds (especially C4: which modification).
2. Operator updates this document to v0.1-frozen.
3. PI issues separate GO referencing the frozen commit.
4. Operator begins execution.

**No candidates will be generated until step 4 is complete.**

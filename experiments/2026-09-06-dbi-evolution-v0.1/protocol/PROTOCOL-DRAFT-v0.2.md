# DbI Evolution Experiment — Protocol v0.2 (DRAFT after PI adjudication pass 1)

**Status:** DRAFT — methodology-collaborator stage. NOT frozen. NOT preregistered. NOT authorized for execution.
**Prior draft:** `protocol/PROTOCOL-DRAFT.md` (v0.1) at commit `bef2c80` (2026-09-06).
**Date of this revision:** 2026-09-06.
**PI adjudication pass 1 received:** 2026-09-06 (decisions on C2, C4, C18/C19, C20, C21).
**Remaining PI decisions required:** 16 confounds (see §12 adjudication table).
**Authorization required:** YES — separate Frank-as-PI GO referencing this protocol's frozen commit.

---

## 0. Change log vs v0.1

| Change | Source | Effect |
|---|---|---|
| C21 (envelope-preservation) | PI ruling | §14 rewritten to commit envelope-preservation as the operational definition. Pixel-preservation and functional-preservation are explicitly rejected. |
| C20 (hard STOP on drift) | PI ruling | §11 rewritten with explicit drift-classification rule. |
| C2 (runtime lock + deviation) | PI ruling | §5 preflight gate hardened: every runtime identifier recorded; any material difference triggers a preregistered deviation rule. |
| C18/C19 (role separation) | PI ruling | §10 hardened: explicit prohibition on treatment-identity leakage to evaluators; explicit prohibition on modification-spec leakage to evaluators. |
| C4 (modification selection) | PI ruling | §5 modification specification is now frozen (verbatim). Single-axis, additive, narrowly bounded, NOT a reversal of exact-date priority. |

No other sections of the v0.1 design have been changed by PI ruling in this pass.

---

## 1. Research question (unchanged)

**Can a developer change an application by changing its expressed intent, while preserving the application's established behavioral identity outside the intended modification?**

Restated: given a frozen baseline intent specification that has been shown to produce a stable family of independently reconstructed behaviors (BIB evidence), does a controlled, single-axis intent modification cause the reconstruction to (a) actually exhibit the intended new behavior on the targeted axis AND (b) preserve the established behavioral contract on all non-targeted axes?

Both (a) and (b) must be true. A new behavior with no constraint is trivial; an unchanged behavior with no novelty is the BIB result. The DbI claim becomes interesting only at the conjunction.

A treatment that preserves identity but fails the modification is **not** a PASS.
A treatment that implements the modification but breaks non-target identity is **not** a PASS.
A treatment that satisfies both, on both blinded evaluators, **is** a PASS.

---

## 2. Why this is the right next experiment (unchanged)

Per BIB protocol §24 the experimental sequence was:

1. Frozen intent → independent reconstructions → measure natural variance → **establish identity baseline** ← COMPLETE (BIB-001 + BIB-002)
2. Frozen original intent → controlled intent modification → independent reconstruction → **measure intended behavioral change → compare unchanged behaviors against baseline** ← THIS PROTOCOL
3. (After Evolution) DbI Evidence Brief v0.2

---

## 3. PI adjudication summary (the five resolved confounds)

### 3.1 C21 — Envelope-preservation adopted (PI ruling)

> "Define preservation of non-target behavioral identity as remaining within the empirically observed BIB-001 + BIB-002 non-deviated behavioral envelope. Do not require pixel/score identity, and do not substitute an uncalibrated qualitative 'recognizably the same' standard."

Operational definition: a non-target behavioral dimension is preserved if its score in the Modified arm (Arm M) lies within the BIB-001 + BIB-002 non-deviated envelope (the 60-candidate baseline established by both BIB runs, with the R4/B cluster excluded). The envelopes for each dimension are reported in §7 of BIB-001's `analysis/final-result.md` and BIB-002's `analysis/baseline-envelope.md`.

Pixel-preservation (require identical scores) and functional-preservation (require "recognizably the same" without numerical anchor) are explicitly rejected.

### 3.2 C20 — Hard STOP on control-arm drift (PI ruling)

> "If the contemporaneous control arm exits the established non-deviated BIB envelope, STOP the experiment and classify the run as confounded by possible runtime/model drift. Do not continue to substantive Evolution interpretation."

The control arm (Arm C) within-reconstruction Manhattan mean must lie within the BIB non-deviated envelope upper bound (operator-pre-registered tolerance to be specified in §9 as part of C16 adjudication). If Arm C exits that bound, the experiment halts before any Arm M analysis is performed and is classified `CONFOUNDED_BY_POSSIBLE_RUNTIME_DRIFT`. No substantive Evolution interpretation is reported.

### 3.3 C2 — Runtime lock + deviation handling (PI ruling)

> "Preflight must record exact model, CLI/runtime, source commit, tool/runtime identifiers, and relevant execution configuration. Any material difference from the BIB environment must be documented before generation and handled according to a preregistered deviation rule."

Preflight must record at minimum:
- Reconstruction model identifier
- Reconstruction CLI/runtime version
- Frozen source commit SHA (must equal `c369215024c9f8a849daf11bd4b872d7ee566a7a`)
- Frozen source file SHA-256 values (must equal BIB values)
- Tool posture (no-tools, allowed/disallowed lists)
- Authentication path
- Effective session-creation mechanism

Any material deviation from the BIB environment is recorded under a preregistered deviation rule (see C2 row in §12 for the proposed default).

### 3.4 C18/C19 — Role separation under modification (PI ruling)

> "Evaluators must not receive the modification specification or treatment identity before their score sets are locked. The operator may hold the modification spec and blind-map only where necessary for execution, provided neither evaluator can infer treatment assignment before locking."

Concrete implementation:
- The modification specification document is held by PI (modification-spec author). Operator receives an immutable copy at execution start.
- The evaluator input packets (Arm C and Arm M, identical in shape) contain NO reference to the modification specification. They contain only the frozen baseline contract, the frozen rubric, the frozen test prompts, and the candidate outputs.
- The operator holds both the modification spec AND the blind-map (necessary for execution). This is the operator-blinding paradox. The unblind happens after both evaluators lock — no one learns the treatment assignment for any candidate before scoring is committed.
- Evaluators cannot infer treatment assignment from candidate content alone, because the modification is additive ("include a ±30-day worldwide event") rather than a transformation — the modified-intent candidates still contain the baseline behavior plus a new element. Evaluators do not know whether the new element's presence indicates a control or modified treatment.

### 3.5 C4 — Modification selection (PI ruling)

> "Freeze the intended modification substantially as follows:
> 'Preserve the existing Amazing Birthday behavior, including exact-date priority, selectivity, significance, lifetime-arc treatment, and warm narrative style. Additionally, include exactly one historically significant worldwide event occurring within ±30 calendar days of the birth date, clearly distinguishing it from exact-date connections.'
> The target axis is therefore the new ±30-day worldwide-event inclusion requirement."

The modification is **frozen** as follows (this is the binding target-axis specification):

> **Modification specification (v0.2 — PI-ruled, binding):**
>
> The application behavior shall be preserved from the frozen baseline contract in all respects, including but not limited to: exact-date priority, selectivity (5–10 standout connections), significance threshold, lifetime-arc treatment, warm-and-vivid narrative voice, factual discipline (exact-date vs nearby-event distinction), and the end-of-report synthesis requirement.
>
> **Additionally, exactly one historically significant worldwide event occurring within ±30 calendar days of the supplied birth date shall be included in the report.** This worldwide event must be clearly distinguished from exact-date connections (e.g., labeled as "around that time" or "in the same month" rather than as an exact-date connection). The ±30-day window is symmetric (before or after); the operator picks the one event that satisfies the "historically significant worldwide" criterion.
>
> The worldwide event is added to the report in addition to the existing exact-date-priority connections; it does NOT replace any of them.

This is additive, narrowly bounded, and explicitly preserves exact-date priority. It is not a reversal of the existing priority.

---

## 4. Confound register — resolution status

| ID | Title | Status |
|---|---|---|
| C2 | Runtime lock + deviation handling | **RESOLVED (PI pass 1)** — §3.3 |
| C4 | Modification selection | **RESOLVED (PI pass 1)** — §3.5 |
| C18/C19 | Role separation | **RESOLVED (PI pass 1)** — §3.4 |
| C20 | STOP on control-arm drift | **RESOLVED (PI pass 1)** — §3.2 |
| C21 | Envelope-preservation definition | **RESOLVED (PI pass 1)** — §3.1 |
| C1 | Arm size (3 vs 6 reconstructions per arm) | AWAITING PI |
| C3 | Evaluator availability | AWAITING PI (preflight check) |
| C5 | Modification specificity format | RESOLVED (default (b)) — see §3.5 verbatim specification |
| C6 | Modification doc placement | AWAITING PI (operator proposal: append to reconstruction input) |
| C7 | Anti-pattern check | AWAITING PI (operator proposal: not required for additive modification) |
| C8 | Control arm contemporaneous timing | RESOLVED (default) — §6 |
| C9 | What "matched" means | RESOLVED (default) — §6 |
| C10 | Use of BIB envelope | RESOLVED (default) — §7 |
| C11 | Dimension reuse vs new | AWAITING PI (operator proposal: Hybrid) |
| C12 | Non-target axes enumerated | AWAITING PI (operator proposal: 8 axes in §7) |
| C13 | Modification success scoring | AWAITING PI |
| C14 | Anti-pattern check | (folded into C7) |
| C15 | Modification success thresholds | AWAITING PI |
| C16 | Preservation tolerance | AWAITING PI |
| C17 | Per-arm vs joint reporting | RESOLVED (default) — §9 |

---

## 5. Modification specification (frozen per C4)

Reproduced here for evidence-chain integrity:

> "Preserve the existing Amazing Birthday behavior, including exact-date priority, selectivity, significance, lifetime-arc treatment, and warm narrative style. Additionally, include exactly one historically significant worldwide event occurring within ±30 calendar days of the birth date, clearly distinguishing it from exact-date connections."

**Target axis:** presence of exactly one ±30-day worldwide event, clearly distinguished from exact-date connections.

**Non-target axes (to be preserved):** all behaviors from the frozen baseline contract. The operator proposes 8 enumerated axes in §7 for PI confirmation.

---

## 6. Arm structure (contemporaneous control + modified intent)

**Arm C — Control** (unchanged baseline intent, contemporaneous)
- Re-uses frozen `03-behavioral-baseline.md` and `RECONSTRUCTION-PROMPT.md` byte-identical to BIB-001/002
- Reconstruction input = `BIB-001/inputs/reconstruction-input.txt` (sha256 `03ce4c40...`)
- 3 fresh independent reconstruction sessions, each: A/T1-T5 + B/T1-T5 = 10 candidates
- Total: 30 candidates

**Arm M — Modified intent** (frozen modification appended)
- Same as Arm C but with the modification specification appended to the reconstruction input. The modification is layered on top of the baseline contract; the baseline contract itself is NOT modified.
- Reconstruction input = `Arm C input bytes` + `\n\n` + `modification specification text`
- The operator must compute and record SHA-256 over the exact Arm M reconstruction input bytes; this SHA must be committed to the MANIFEST before R1 of Arm M.
- 3 fresh independent reconstruction sessions, same shape (A/T1-T5 + B/T1-T5 = 10 candidates each)
- Total: 30 candidates

**Total candidates: 60** (30 Arm C + 30 Arm M)

**Order of execution:** Arm C and Arm M reconstructions are interleaved at the per-reconstruction level (R1_C, R1_M, R2_C, R2_M, R3_C, R3_M) rather than running all of one arm then all of the other. This reduces the effect of within-session runtime drift on between-arm comparisons. Each R*_C and R*_M use the same runtime session-creation mechanism.

**Matching levels (all reported):**
- Per-test: Arm C T_n vs Arm M T_n (same test prompt)
- Per-reconstruction: Arm C R_n vs Arm M R_n (same reconstruction index)
- Per-block: Arm * A vs Arm * B (within each arm)

**Gating (per C20):** if Arm C within-Recon Manhattan mean exits the BIB non-deviated envelope upper bound + tolerance, STOP and classify `CONFOUNDED_BY_POSSIBLE_RUNTIME_DRIFT`. No Arm M analysis is performed.

---

## 7. Non-target axes (envelope-preservation criterion)

The BIB-001 + BIB-002 non-deviated envelope is the operational reference. Each of the following non-target axes has an empirically-established distribution from BIB. The modified arm must remain within that distribution.

**Operator proposal for the 8 non-target axes (awaits PI confirmation, see §12 C12 row):**

1. Exact-date preference policy preserved (binary: yes/no per evaluator per candidate)
2. Connection count within 5–10 range (operator counts after evaluation)
3. Selection significance (BIB `selection_behavior` dimension, 0–4)
4. End-of-report synthesis (operator check: does the report end with a substantive synthesis?)
5. Lifetime framing (BIB `functional_completeness` dimension, 0–4)
6. Warm/vivid narrative voice (BIB `narrative_behavior` dimension, 0–4)
7. Factual discipline (no nearby events misrepresented as exact-date) (binary)
8. No arbitrary trivia policy (operator check: any filler events that weren't there in BIB?)

**Envelope-preservation rule:** for each non-target axis, the Arm M within-arm score distribution must lie within the BIB-001 + BIB-002 non-deviated envelope upper bound (per dimension, the upper bound is the max observed value across the 60 non-deviated BIB candidates, with the C16 tolerance applied). A specific failure on any single axis may be acceptable if the magnitude is small; the joint criterion is per §9.

---

## 8. Modification-success criterion (target axis)

The target axis is binary at the candidate level: did the report include exactly one ±30-day worldwide event, clearly distinguished from exact-date connections?

**Operator proposal for scoring (awaits PI confirmation, see §12 C13/C15 rows):**
- **modification_conformance dimension (new, 0–4):**
  - 4 — exactly one ±30-day worldwide event, clearly distinguished, historically significant, non-exact-date
  - 3 — one event meeting most criteria but with one weakness
  - 2 — events present but not exactly one, or not clearly distinguished
  - 1 — events present but fail significance / distinction / count criteria
  - 0 — no ±30-day worldwide event

**Modification-specific yes/no checks (objective, no LLM needed):**
- M1: Did the report mention any "around [date ±30 days]" or equivalent temporal qualifier referencing a single nearby event?
- M2: Was exactly one such event mentioned (not zero, not multiple)?
- M3: Did the report distinguish the nearby event from exact-date connections (not collapsed into the same priority tier)?
- M4: Was the event historically significant on a worldwide scale (not just a local/incidental occurrence)?

**Operator proposal for the preregistered success threshold:** `modification_conformance ≥ 3.0` on average across Arm M candidates AND ≥ 70% of Arm M candidates pass all four M-checks (M1, M2, M3, M4). AWAITING PI confirmation (C15).

---

## 9. Outcome thresholds (per-arm + joint)

**Per-arm classification:**

Arm M is PASS if and only if ALL of:
1. modification_conformance criterion met (per C15)
2. non-target axes envelope-preserved (per §7 and C16)
3. identity-preservation agreement across evaluators ≥ 0.9 (BIB gate)
4. per-dim MAE across evaluators ≤ 1.0 (BIB gate)

Arm M is FAIL on the modification axis if criterion 1 fails (target behavior absent).
Arm M is FAIL on the preservation axis if criterion 2 fails (non-target drift too large).
Arm M is INCONCLUSIVE_PENDING_FURTHER if a single criterion is in a marginal band (operator pre-registered bands to be specified in §12 C15/C16 rows).

Arm C is PASS if and only if:
1. All four BIB gates pass (BIB eval gates)
2. Within-Recon Manhattan mean lies within the BIB non-deviated envelope upper bound + tolerance (C16 + C20)
3. Per-reconstruction / per-test matching with BIB baseline envelope is reasonable (qualitative)

If Arm C FAILS its preservation gate (C20), the experiment halts with disposition `CONFOUNDED_BY_POSSIBLE_RUNTIME_DRIFT`. No Arm M analysis.

**Joint classification (only if Arm C is PASS):**

| Arm C | Arm M | Joint |
|---|---|---|
| PASS | PASS | **EVOLUTION_PASS** |
| PASS | FAIL on modification | **MODIFICATION_FAILURE** |
| PASS | FAIL on preservation | **PRESERVATION_FAILURE** |
| PASS | INCONCLUSIVE_PENDING_FURTHER | **INCONCLUSIVE_PENDING_FURTHER** |
| FAIL (drift) | (not analyzed) | **CONFOUNDED_BY_POSSIBLE_RUNTIME_DRIFT** |

---

## 10. Role separation (per C18/C19 ruling)

- **Modification-Spec Holder:** Frank Ventura (PI) — author of the modification specification §5.
- **Modification-Spec Carrier:** Hermes (operator) — receives an immutable copy at execution start; holds it through generation and blinding; never exposes it to evaluators.
- **Blind-Map Holder:** Hermes (operator) — same role.
- **Generation Operator:** Hermes (operator) — invokes the reconstruction engine.
- **Evaluator A:** Codex gpt-5.6-sol — receives only the frozen baseline contract, frozen rubric, and blinded candidate outputs (no treatment identity).
- **Evaluator B:** Claude Opus 4.7 — same as A.
- **Final Synthesizer:** ChatGPT (designated by BIB protocol §15) — interprets after both evaluators lock.

**Operator-blinding paradox resolution:** the operator holds both the modification spec AND the blind-map during execution. This is required for execution (the operator must know what input bytes each reconstruction received AND which blind ID maps to which candidate). The unblind — i.e., revealing treatment assignment for any candidate — happens only after both evaluators' score sets are locked. By the time anyone (operator, ChatGPT, PI) can connect a candidate to its treatment, the scoring is already complete.

**Treatment-identity leakage prevention:**
- Evaluator input packets for Arm C and Arm M are structurally identical (same shape, same headers, same instruction text).
- The modification specification text appears ONLY in the reconstruction input (the bytes the model sees). It does NOT appear in any evaluator-visible artifact.
- Evaluators cannot infer treatment assignment from candidate content alone, because the modification is additive ("include a ±30-day event") rather than transformative. A control-arm candidate might happen to mention a nearby event; a modified-arm candidate might happen to omit one. The evaluators do not know which is which.

---

## 11. Stop conditions

Inherited from BIB protocol §14:
- Source verification fails → STOP
- Reconstruction engine runtime materially unavailable → STOP
- More than 1 of 3 reconstructions per arm experiences infrastructure failure → STOP (operator proposal; C1 to be resolved)
- Capture integrity unreliable → STOP
- Identity-breaking behavior appears frequently enough that calibration fails → STOP

Evolution-specific (per C20 ruling):
- **Arm C exits the BIB non-deviated envelope upper bound + C16 tolerance → STOP and classify `CONFOUNDED_BY_POSSIBLE_RUNTIME_DRIFT`. No Arm M analysis performed.**

---

## 12. Remaining confounds — PI adjudication table

The following 13 confounds require PI decisions before freeze. Operator recommendations are stated explicitly; PI may accept, override, or request clarification on each.

| ID | Issue | Available choices | Operator recommendation | Consequence of each choice | Proposed default if no PI response |
|---|---|---|---|---|---|
| C1 | Arm size | (a) 3 reconstructions/arm; (b) 6 reconstructions/arm | (a) 3 reconstructions/arm — matches BIB-002 statistical-power reasoning, halves per-arm variance via matched-control structure | (a) 60 candidates total, feasible within one session; (b) 120 candidates, doubles cost and time | (a) 3 reconstructions/arm, stop-condition threshold = 1 infrastructure failure |
| C3 | Evaluator availability | Either both callable or one/both unavailable | Both must be callable (BIB eval gate); if either is unavailable, BLOCKED | If BLOCKED, no scoring possible, no PASS possible | Block generation if either unavailable at preflight |
| C6 | Modification doc placement | (a) Append to reconstruction input; (b) Insert between contract and prompt; (c) Insert as separate prompt section before the durable package | (a) Append — minimal disruption to BIB-comparable reconstruction lifecycle | (a) Reconstruction input SHA will differ from BIB-001, but bytes remain deterministic; (b)/(c) potential ordering effects | (a) Append after `--- END FILE: RECONSTRUCTION-PROMPT.md ---` |
| C7 | Anti-pattern check | Required or not | Not required — modification is additive, not transformative; anti-pattern checks would require specifying what the model must NOT do, which is unbounded | If required, need PI to specify anti-patterns; if not required, simpler | Not required |
| C11 | Dimension reuse vs new | (a) Reuse BIB 4-dim vector only; (b) Decompose contract into explicit non-target axes; (c) Hybrid | (c) Hybrid — reuse BIB dimensions for Manhattan distance comparability with BIB envelope, plus the 8 enumerated non-target axes for direct preservation check | (a) Lose sensitivity to specific non-target drift; (b) Lose comparability with BIB Manhattan envelope; (c) preserves both | (c) Hybrid |
| C12 | Non-target axes enumerated | The 8 axes in §7; alternative counts (4, 6, 10, 12); different axes | The 8 axes in §7 — they cover the baseline contract comprehensively without overlap | More axes = more granularity but more evaluation work; fewer axes = less granular but simpler | The 8 axes as listed in §7 |
| C13 | Modification success scoring | (a) modification_conformance 0-4 dim only; (b) M-checks only; (c) Both combined | (c) Both combined — modification_conformance for overall 0-4 score, M-checks for objective yes/no per-criterion | (a) Insensitive to specific check failures; (b) No aggregate score for variance analysis; (c) both | (c) Both |
| C15 | Modification success thresholds | modification_conformance ≥ X; M-checks pass-rate ≥ Y | (proposed for PI confirmation): modification_conformance ≥ 3.0 (mean across Arm M) AND M1-M4 all-pass rate ≥ 70% of Arm M candidates | Higher thresholds = more stringent test; lower thresholds = more permissive test | (Proposed) ≥3.0 AND ≥70% all-pass |
| C16 | Preservation tolerance | +X Manhattan points above contemporaneous Arm C within-mean | (proposed for PI confirmation): +1.5 Manhattan points | Smaller tolerance = stricter; larger = more permissive. BIB baseline within-mean was 0.5-1.0; +1.5 puts the bound at 2.0-2.5, still well below the R4/B contamination signature of 13.5 | (Proposed) +1.5 Manhattan points |
| C17 | Per-arm vs joint reporting | (a) Per-arm reported only; (b) Joint classification only; (c) Both | (c) Both — per-arm PASS/FAIL is informative; joint is the headline | (a) Hides the conjunction result; (b) Hides per-arm failures; (c) both | (c) Both |
| — | Number of candidates reported in BIB baseline envelope used for envelope-preservation | 60 (BIB-001) vs 85 (BIB-001 + BIB-002 combined) | 85 — combined envelope is more statistically robust | Smaller envelope = less robust reference; larger envelope = more generalizable | 85 (combined BIB-001 + BIB-002 non-deviated candidates) |
| — | Reconstruction engine order (Arm C before Arm M, or interleaved) | Sequential or interleaved | Interleaved at R-level (R1_C, R1_M, R2_C, R2_M, ...) per §6 | Sequential = simpler; interleaved = reduces within-session drift confounds | Interleaved |
| — | Test prompts revealed to evaluator (T1–T5 mapping) | Yes or no | Yes — T1–T5 mapping is in the candidate packet's test input; evaluators see the prompt text but not the T1/T2/T3/T4/T5 label | Revealing the prompt text is necessary for evaluation; revealing the T1–T5 label is unnecessary leakage | Reveal test prompt text; do not reveal T1–T5 label |

---

## 13. Authorization boundary (unchanged from v0.1)

**This draft does NOT authorize execution.** Per Frank's instruction: GO means "begin protocol preparation," not "start generation immediately."

The freeze-and-execute sequence:
1. PI adjudicates the confounds in §12 (this document is the discussion artifact for adjudication pass 2).
2. The protocol is amended to reflect PI decisions and re-versioned as v0.2-frozen.
3. A v0.2-frozen commit is created.
4. A separate Frank-as-PI GO references the frozen commit.
5. Operator executes preflight → generation → blinding → evaluator scoring → analysis.
6. Operator returns evidence package for PI adjudication.

Operator will NOT generate any candidates, modify any source artifact, or invoke any evaluator until step 4 is complete.

---

## 14. Preservation criterion (envelope-preservation, per C21 ruling)

Reproduced here as the binding operational definition:

**A non-target behavioral dimension is preserved if its score in the Modified arm (Arm M) lies within the empirically observed BIB-001 + BIB-002 non-deviated behavioral envelope (the 85-candidate combined envelope, with the documented R4/B cluster excluded).**

The envelope for each dimension is the empirical distribution (count, mean, median, std-dev, min, max, p25, p75, p90, p95) computed from the 85 non-deviated BIB candidates. These envelopes are reported in BIB-001's `analysis/baseline-envelope.md` and BIB-002's `analysis/baseline-envelope.md`.

For the preservation joint criterion, the BIB evidence-grounded operational rule is: **the Arm M within-arm distribution on each non-target axis must lie within the BIB envelope upper bound plus a tolerance T** (C16 — operator proposal T=+1.5 Manhattan points).

Pixel-preservation and functional-preservation are explicitly rejected as unanchored.

---

## 15. Editorial note (per Frank's earlier note)

The Evolution experiment is what makes DbI non-trivial. BIB showed that the reconstruction substrate is stable; Evolution tests whether intent modification can be expressed cleanly through the same substrate without contaminating the rest of the application. Both preregistration discipline and the envelope-preservation criterion exist to keep this experiment from degenerating into either "the model just does whatever you say" (passes trivially) or "the model can't preserve anything" (fails trivially). The preregistered decision rules and the modification specification are the binding constraints; the analysis exists only to report what was already committed to.

---

## 16. Next steps (operator proposal, awaits PI adjudication pass 2)

1. PI adjudicates the confounds in §12 (especially C1, C12, C15, C16, C17).
2. Operator updates this document to v0.2-frozen with PI decisions baked in.
3. Frozen commit created.
4. Separate Frank-as-PI GO references the frozen commit.
5. Operator begins execution.

**No candidates will be generated until step 4 is complete.**

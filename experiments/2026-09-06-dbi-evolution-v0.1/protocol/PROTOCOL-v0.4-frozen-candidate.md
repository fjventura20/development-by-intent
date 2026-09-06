# DbI Evolution Experiment — Protocol v0.4 (FROZEN-CANDIDATE)

**Status:** FROZEN-CANDIDATE — awaiting separate Frank-as-PI GO referencing this commit.
**Prior drafts:** `protocol/PROTOCOL-DRAFT.md` (v0.1) at commit `bef2c80`; `protocol/PROTOCOL-DRAFT-v0.2.md` (v0.2) at commit `496cafc`; `protocol/PROTOCOL-DRAFT-v0.3.md` (v0.3) at commit `2b67cfe`.
**Frozen at:** 2026-09-06T19:35:00Z
**Frozen by:** Hermes (operator), per Frank-as-PI final adjudication pass.
**Authorization required:** YES — separate Frank-as-PI GO referencing this protocol's frozen commit.

---

## 0. Change log vs v0.3

| Change | Source | Section |
|---|---|---|
| §9.2 M4 rubric rewritten: 4 disjunctive criteria → at least 2 of 4 (conjunctive) | PI ruling pass 3 | §9.2 |
| §11.3 per-axis collapse rule rewritten: any-one-axis-broken (not 2-of-8) | PI ruling pass 3 | §11.3 |
| §15.3 baseline-envelope-membership.json produced; SHA-256 in inventory | PI ruling pass 3 | §15.3, §15.4 |
| Flag F1 confirmed: 2.5 absolute ceiling is a backstop, not always-binding | PI ruling pass 3 | §11.2 |
| Flag F2 retained: 50pp absolute rule retained; multiplicative alternative rejected | PI ruling pass 3 | §9.3 |
| §14 explicit PASS/FAIL/INCONCLUSIVE-CONFOUNDED decision tree | PI ruling pass 3 | §14 |
| All five pre-freeze artifacts produced; SHA-256 inventory | Per protocol §15.3 | §15.4 |

No §1-§13, §15.1-§15.2 semantics changed from v0.3.

---

## 1. Research question

**Can a developer change an application by changing its expressed intent, while preserving the application's established behavioral identity outside the intended modification?**

Conjunction of (a) modification success and (b) non-target preservation. A treatment that preserves identity but fails the modification is NOT a PASS. A treatment that implements the modification but breaks non-target identity is NOT a PASS.

---

## 2. Why this is the right next experiment

BIB evidence (BIB-001 + BIB-002) establishes the identity baseline and confirms the behavioral-identity measurement is stable enough to serve as control. The Evolution experiment tests whether intent modification can be expressed through the same substrate without contaminating the rest of the application. Per BIB protocol §24 the experimental sequence is: (1) Frozen intent → measure natural variance → establish identity baseline [COMPLETE]; (2) Frozen original intent → controlled intent modification → measure intended behavioral change → compare unchanged behaviors against baseline [THIS PROTOCOL]; (3) After Evolution → DbI Evidence Brief v0.2.

---

## 3. PI adjudication summary (passes 1 + 2 + 3)

Pass 1 (v0.2): C2, C4, C18/C19, C20, C21.
Pass 2 (v0.3): C1, C3, C6, C7, C11, C12, C13, C15, C16, C17, 4 cross-cuts, outcome logic.
Pass 3 (v0.4): §9.2 M4 rubric, §11.3 per-axis rule, §15.3 envelope artifact, Flags F1+F2 confirmed.

All C1–C21 items and cross-cuts are now CLOSED. The frozen protocol below records each PI ruling.

---

## 4. Experimental structure

**Two-arm matched-pair design:** Arm C (control, unchanged intent) and Arm M (modified intent). Same wrapper/location semantics for both arms. Base reconstruction artifact (the two frozen files) is **byte-identical to BIB** for both arms; the modification is layered on top via a separately delimited second instruction.

**Sample size:** 3 reconstructions × 2 arms × 2 blocks × 5 tests = **60 candidates total**.

**Statistical interpretation (C1 ruling):** The reconstruction is the primary replication unit. Candidate outputs within a reconstruction are repeated observations, NOT independent experimental replicates. Report reconstruction-level results **before** pooled candidate-level summaries. This experiment does NOT claim independent n=60 statistical power. The matched-control design + BIB evidence make 3 reconstructions/arm sufficient for this first controlled Evolution test.

**Execution order (cross-cut ruling):** Interleaved at the matched-reconstruction level. For each matched reconstruction level (R1, R2, R3), the arm order is determined by an OS-CSPRNG draw, recorded in `protocol/EXECUTION-ORDER.md` (sha256 `d9db9199…`). Each reconstruction uses an isolated fresh session; no conversational or session state crosses between Arm C and Arm M.

**Reporting order (C17 ruling):**
1. Reconstruction-level results.
2. Per-arm candidate-level descriptive results.
3. Matched C-vs-M contrasts (primary Evolution claim).
4. Evaluator agreement.
5. Pooled descriptive summaries (clearly labeled; do not allow pooled summaries to obscure reconstruction-level heterogeneity).

---

## 5. Modification specification (frozen, PI-ruled)

**File:** `inputs/modification-specification.txt` (sha256 `9034bdac…`, 343 bytes).

**Verbatim content:**
> "Preserve the existing Amazing Birthday behavior, including exact-date priority, selectivity, significance, lifetime-arc treatment, and warm narrative style. Additionally, include exactly one historically significant worldwide event occurring within ±30 calendar days of the birth date, clearly distinguishing it from exact-date connections."

**Target axis:** presence of exactly one ±30-day worldwide event, clearly distinguished from exact-date connections.

**Non-target axes (preserved):** see §8.

**Modification document placement (C6 ruling):**
- The base reconstruction artifact (`03-behavioral-baseline.md` + `RECONSTRUCTION-PROMPT.md`) is byte-identical to BIB, never silently edited.
- A separately delimited second instruction is appended after the base reconstruction input.
- Arm C receives a frozen no-op directive (file `inputs/arm-c-directive.txt`, sha256 `c610e246…`) — the directive is a no-op control marker preserving the existing intent, structurally symmetric with Arm M.
- Arm M receives the modification specification above as its appended directive.

---

## 6. Generation runtime (C2 ruling)

Preflight must record and verify: model identifier (`claude-sonnet-4-6`), CLI/runtime version (`claude-code 2.1.170`), frozen source commit (`c369215024c9f8a849daf11bd4b872d7ee566a7a`), frozen source file SHA-256 (matches BIB), tool posture (`--allowedTools '' --tools '' --disallowedTools 'WebFetch,WebSearch'`), authentication path, session-creation mechanism. Any material deviation is recorded before generation and handled per the preregistered deviation rule. STOP if deviation is material and unadjudicated.

**Evaluator availability (C3 ruling):** Both frozen evaluators (Codex gpt-5.6-sol and Claude Opus 4.7) must pass preflight availability checks. If either is unavailable or materially changed, STOP before generation unless PI separately adjudicates. **No substitution after observing candidates.**

---

## 7. Evaluator input packet (cross-cut ruling)

Each evaluator receives a packet containing:
1. Frozen baseline contract (`03-behavioral-baseline.md`)
2. Frozen BIB evaluator rubric extended with the M1-M4 checks
3. The 8 C12 non-target axes instructions
4. The worldwide-historical-significance rubric (M4)
5. For each candidate: blind candidate ID, exact test prompt text, raw candidate output
6. Required return-format instructions (60 records in fixed order)

Evaluators must NOT see: T1–T5 labels, Arm C / Arm M identity, reconstruction identity (R1–R9), modification specification text, treatment assignment, operator blind map, any other evaluator's scores.

All candidate IDs remain blinded until both evaluator score sets are locked.

The packet template is at `inputs/evaluator-input-packet-template.md` (sha256 `4e4c4c9a…`).

---

## 8. Non-target axes (8 axes, C12 ruling)

The 8 non-target axes that must be preserved:
1. exact-date preference (binary)
2. connection count of 5–10 (operator counts after evaluation)
3. selection significance (subjective 0–4)
4. end-of-report synthesis (binary)
5. lifetime framing (subjective 0–4)
6. warm/vivid narrative voice (subjective 0–4)
7. factual discipline (binary: no nearby events misrepresented as exact-date)
8. avoidance of arbitrary trivia (binary)

**Important analytical separation (C11 ruling):**
- The BIB 4-dim behavior vector is the **primary calibrated identity metric** (used for the §11.2 preservation criterion via Manhattan distance).
- The 8 C12 axes are **explicit non-target preservation checks** used for the §11.3 per-axis collapse rule.
- **Some overlap is intentional and acknowledged.** Do NOT double-count overlapping constructs in one composite identity score.
- **Do NOT concatenate** the BIB 4-dim and the 8 C12 axes into a 12-dim Manhattan.

---

## 9. Modification-success scoring (C13 + C15 + PI pass 3)

### 9.1 modification_conformance (objective sum, C13 ruling)

`modification_conformance = M1 + M2 + M3 + M4`

Where each M-check is binary 0/1:
- **M1**: A qualifying event within ±30 calendar days of the supplied birth date is included.
- **M2**: Exactly one such event is included (not zero, not multiple).
- **M3**: The event is clearly distinguished from exact-date connections (e.g., labeled as "around that time", "in the same month", "in the days before/after", or otherwise temporally marked as not exact-date).
- **M4**: The event satisfies the worldwide-historical-significance rubric (§9.2).

`modification_conformance` ranges 0–4 (integer). **No separate subjective 0–4 modification score.**

Evaluators score M1–M4 for **both Arm C and Arm M** candidates while still blinded.

### 9.2 M4 — worldwide-historical-significance rubric (PI pass 3 ruling)

A nearby event satisfies M4 only if **at least two** of the following four criteria are met (not disjunctive — must satisfy ≥ 2):

1. It is treated by mainstream general-reference or historical sources as an event of international or world-historical significance.
2. It directly involved, affected, or materially concerned multiple sovereign states or more than one major world region or continent.
3. It produced durable political, economic, scientific, technological, military, social, or cultural consequences extending materially beyond its place of origin.
4. It would reasonably merit inclusion in a concise one-page global-history chronology or summary for that year.

An event that is primarily local, regional, anecdotal, celebrity-oriented, or trivial does NOT pass merely because it occurred within the ±30-day window.

**No date-specific examples** in the frozen evaluator materials. The rubric is generic.

M4 remains binary: PASS only if at least two criteria are satisfied.

### 9.3 Modification-success gates (C15 ruling)

For Arm M to satisfy modification success, require **independently for each evaluator**:

- **G_mod_a:** mean `modification_conformance` across Arm M candidates ≥ 3.5 / 4.0
- **G_mod_b:** ≥ 80% of Arm M candidates pass all four M-checks
- **G_mod_c:** each individual Arm M reconstruction has ≥ 70% all-pass candidates (no single reconstruction carries the aggregate)
- **G_mod_d:** Arm M's all-pass rate exceeds Arm C's all-pass rate by at least **50 percentage points** (absolute; PI pass 3 retained this over multiplicative alternative). If the control naturally exhibits the target behavior so frequently that the +50pp contrast cannot be achieved, the experiment must NOT claim successful intent-driven modification — that is useful evidence about the discriminative quality of the selected modification, not a reason to weaken the gate post hoc.

**Do not pool evaluator scores.** Evaluator A and Evaluator B must each independently meet all four gates.

---

## 10. Anti-pattern check (C7 ruling)

No separate anti-pattern check required. The modification is additive. Existing checks (selection significance, factual discipline, no-arbitrary-trivia) detect the main foreseeable degradation modes.

---

## 11. Preservation criterion (C11 + C16 + envelope-preservation, PI pass 3)

### 11.1 BIB envelope — combined 85-observation non-deviated envelope (PI ruling, cross-cut)

The preservation criterion uses the **combined 85-observation non-deviated BIB envelope** (BIB-001 non-deviated + BIB-002), with the 5 BIB-001 R4 Block B candidates explicitly excluded.

**Membership artifact (PI ruling, cross-cut):** `inputs/baseline-envelope-membership.json` (sha256 `dad55959…`).
- The exact 85 candidate identifiers are enumerated with deterministic ordering.
- The 5 BIB-001 R4/B contaminated candidates are explicitly excluded.
- SHA-256 of the artifact is recorded in the frozen protocol.
- **Membership is FROZEN at protocol freeze.** No membership changes are permitted after Evolution results exist.

Membership count: BIB-001 non-deviated (55) + BIB-002 (30) = 85. BIB-001 R4/B excluded (5). Grand total BIB observations: 85 + 5 = 90.

### 11.2 BIB 4-dim preservation criterion (C16 ruling)

For the calibrated 4-dim BIB behavior vector, require **independently for each evaluator**:

- **G_pres_a:** Arm M within-Recon Manhattan mean ≤ Arm C within-Recon Manhattan mean + 1.5
- **G_pres_b:** Arm M within-Recon Manhattan mean ≤ **2.5 absolute** (PI pass 3 confirmed as backstop, not always-binding; F1 resolved)

C20 supersedes this analysis if Arm C itself exits the frozen BIB non-deviated envelope (STOP and classify `CONFOUNDED_BY_POSSIBLE_RUNTIME_DRIFT`).

### 11.3 C12 non-target preservation criterion (C12 + PI pass 3)

For each of the 8 C12 non-target axes, report treatment-vs-control preservation separately.

**Two evidence classes (PI pass 3 ruling):**
- **Historically calibrated dimensions:** Where a C12 axis maps directly to existing BIB scoring (the 4 BIB dims feed 4 of the 8 axes), historical BIB evidence may be reported as supporting context. Do NOT manufacture retrospective calibration for axes without prior BIB calibration.
- **All eight C12 axes:** The primary preservation comparison is the contemporaneous matched Arm C vs Arm M comparison.

**Per-axis collapse rule (PI pass 3 ruling — replaces v0.3's 2-of-8 rule):**

For each evaluator independently, an axis is **BROKEN** when BOTH are true:
- Arm M failure rate on that axis is ≥ 30%
- Arm M failure rate ≥ 30 percentage points worse than Arm C on that axis

**Preservation fails for that evaluator if ANY ONE of the 8 axes is BROKEN.**

A catastrophic change to one important behavioral property is sufficient evidence that non-target identity was not preserved. Do not require two broken axes. Because the experiment requires both evaluators independently to satisfy preservation, evaluator disagreement cannot be averaged away.

Report all 8 axis failure rates for C and M even when none crosses the failure threshold.

### 11.4 Inter-evaluator identity-preservation agreement (inherited BIB gate)

Arm M inter-evaluator identity-preservation agreement ≥ 0.9. Per-dim MAE across evaluators ≤ 1.0. These gates must be satisfied for Arm M to be evaluable.

---

## 12. Stop conditions (C20 + inherited BIB)

**Inherited from BIB protocol §14:**
- Source verification fails → STOP
- Reconstruction engine runtime materially unavailable → STOP
- >1 of 3 reconstructions per arm experiences infrastructure failure → STOP
- Capture integrity unreliable → STOP
- Identity-breaking behavior appears frequently enough that calibration fails → STOP

**Evolution-specific (C20 ruling):**
- Arm C exits the BIB non-deviated envelope upper bound + tolerance → STOP and classify `CONFOUNDED_BY_POSSIBLE_RUNTIME_DRIFT`. No Arm M analysis performed.

**Evaluator-specific (C3 ruling):**
- Either evaluator unavailable or materially changed → STOP before generation unless PI separately adjudicates. No substitution after observing candidates.

**Envelope membership:**
- BIB baseline envelope membership frozen at protocol freeze; no membership changes permitted after Evolution results exist.

---

## 13. Role separation (C18/C19 ruling)

- **Modification-Spec Holder:** Frank Ventura (PI).
- **Modification-Spec Carrier:** Hermes (operator) — holds an immutable copy at execution start; never exposes it to evaluators.
- **Blind-Map Holder:** Hermes (operator).
- **Generation Operator:** Hermes (operator).
- **Evaluator A:** Codex gpt-5.6-sol.
- **Evaluator B:** Claude Opus 4.7.
- **Final Synthesizer:** ChatGPT.

**Operator-blinding paradox:** the operator holds both the modification spec and the blind-map during execution. Unblind happens after both evaluators lock.

**Treatment-identity leakage prevention:**
- Evaluator input packets for Arm C and Arm M are structurally identical (same shape, same headers, same instruction text).
- The modification specification text appears only in the reconstruction input (the bytes the model sees), never in any evaluator-visible artifact.
- Evaluators cannot infer treatment assignment from candidate content alone, because the modification is additive.

---

## 14. Outcome logic — explicit preregistered decision tree (PI pass 3 ruling)

The final disposition is the explicit conjunction:

```
PRE-CHECKS (must all PASS to enter scoring analysis):
  C20: Arm C within-Recon Manhattan mean lies within BIB non-deviated envelope + tolerance
       If FAIL → CONFOUNDED_BY_POSSIBLE_RUNTIME_DRIFT (no further analysis)
  C3:  Both evaluators callable; neither materially changed
       If FAIL → INCONCLUSIVE_PENDING_EVALUATOR_UNAVAILABILITY (no further analysis)
  Evidence chain intact; blinding not broken
       If FAIL → INCONCLUSIVE_PENDING_PROTOCOl_INVALIDATING_DEVIATION

JOINT DISPOSITION:
  IF Modification Success = TRUE
     AND Non-target Identity Preservation = TRUE
     AND Contemporaneous Control Validity = TRUE
     AND Inter-evaluator gates (§11.4) met
     THEN DISPOSITION = EVOLUTION_PASS

  ELSE IF Modification Success = FALSE
     (G_mod_a, G_mod_b, G_mod_c, or G_mod_d fails per §9.3, per evaluator, with both evaluators required to each meet the gate)
     THEN DISPOSITION = MODIFICATION_FAILURE
     (NOT INCONCLUSIVE — substantive modification failure is FAIL, not INCONCLUSIVE)

  ELSE IF Non-target Identity Preservation = FALSE
     (§11.2 G_pres_a or G_pres_b fails, OR §11.3 any-axis-BROKEN rule fires, OR §11.4 inter-evaluator gate fails, per evaluator)
     THEN DISPOSITION = PRESERVATION_FAILURE
     (NOT INCONCLUSIVE — substantive preservation failure is FAIL, not INCONCLUSIVE)

  ELSE DISPOSITION = INCONCLUSIVE_PENDING_FURTHER
     (only used for residual ambiguity that survives the explicit conjunction above)
```

INCONCLUSIVE_PENDING_FURTHER is reserved for genuine ambiguity, not used to soften substantive failures.

---

## 15. Pre-freeze artifacts and SHA inventory

### 15.1 Required pre-freeze artifacts (all produced before this freeze)

| Artifact | Path | SHA-256 |
|---|---|---|
| Baseline envelope membership | `inputs/baseline-envelope-membership.json` | `dad55959998a1851aa3106aab926e442690249327c5c343072fc4bd938520aa1` |
| Modification specification | `inputs/modification-specification.txt` | `9034bdac205e38537dbeaa5e83a857942ebfffb84a6bc13f29078828d0bf7c78` |
| Arm C no-op directive | `inputs/arm-c-directive.txt` | `c610e2469300b6c9b0445d530117121064939a479d71bee3d7ea9cfdaea08fab` |
| Evaluator input packet template | `inputs/evaluator-input-packet-template.md` | `4e4c4c9aba5c55958f8f20b671e2185b49b3244c0c877fe12e9ab731c0ba0497` |
| Execution order | `protocol/EXECUTION-ORDER.md` | `d9db91992aaf9539ec4786534128fa99caca34878fae6254ed1747799b10aed7` |

### 15.2 Cross-cutting confirmations (per Frank's final instruction)

- All C1–C21 items and cross-cuts are CLOSED.
- No candidates have been generated.
- No evaluator has seen candidate evidence.
- The exact proposed preregistered PASS / FAIL / INCONCLUSIVE-CONFOUNDED decision tree is in §14.

---

## 16. Authorization boundary

**This protocol is FROZEN-CANDIDATE but does NOT authorize execution.** Per Frank's instruction: GO means "begin protocol preparation," not "start generation immediately."

The execution sequence:
1. Frank reviews this v0.4 frozen-candidate and issues a separate explicit GO referencing this commit SHA.
2. Operator executes preflight → generation (interleaved per EXECUTION-ORDER.md) → blinding → evaluator scoring → analysis.
3. Operator returns evidence package for PI adjudication.
4. Final synthesis via ChatGPT per BIB protocol §15.

Operator will NOT generate any candidates, modify any source artifact, or invoke any evaluator until step 1 is complete.

---

## 17. Change history

- v0.1 — DRAFT for adjudication, commit `bef2c80` (2026-09-06)
- v0.2 — DRAFT after PI pass 1, commit `496cafc` (2026-09-06)
- v0.3 — DRAFT after PI pass 2, commit `2b67cfe` (2026-09-06)
- **v0.4 — FROZEN-CANDIDATE after PI pass 3 (this document), 2026-09-06**

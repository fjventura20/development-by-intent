# DbI Evolution Experiment — Protocol v0.3 (DRAFT after PI adjudication pass 2)

**Status:** DRAFT — methodology-collaborator stage. NOT frozen. NOT preregistered. NOT authorized for execution.
**Prior drafts:** `protocol/PROTOCOL-DRAFT.md` (v0.1) at commit `bef2c80`; `protocol/PROTOCOL-DRAFT-v0.2.md` (v0.2) at commit `496cafc`.
**Date of this revision:** 2026-09-06.
**PI adjudication pass 2 received:** 2026-09-06 (decisions on C1, C3, C6, C7, C11, C12, C13, C15, C16, C17, plus 4 cross-cuts and an outcome-logic requirement).
**Remaining items:** see §15.
**Authorization required:** YES — separate Frank-as-PI GO referencing this protocol's frozen commit.

---

## 0. Change log vs v0.2

| Change | Source | Effect |
|---|---|---|
| C1 — arm size frozen at 3/arm; statistical interpretation rewritten | PI ruling | §4 explicit: reconstruction is the primary replication unit; candidate outputs within a reconstruction are repeated observations; report reconstruction-level before pooled. n is not 60. |
| C12 — 8 non-target axes frozen; explicit warning against double-counting in Manhattan | PI ruling | §8 frozen axes list; §11 separation between BIB vector and C12 axes is analytical, not concatenative. |
| C11 — hybrid with separated roles; no concatenated 12-dim Manhattan | PI ruling | §11 BIB 4-dim behavior vector is the calibrated identity metric; C12 axes are explicit non-target preservation checks. |
| C13 — `modification_conformance = M1 + M2 + M3 + M4` (sum of binary 0/1) | PI ruling | §9 conformance is an integer 0–4, not a subjective rating. |
| C15 — tightened modification-success thresholds (per below) | PI ruling | §9 gates updated. |
| C16 — preservation tolerance = Arm M ≤ Arm C + 1.5 AND ≤ 2.5 absolute | PI ruling | §11 preservation criterion updated. |
| C3 — evaluator availability rule | PI ruling | §6 + §13 STOP rule if either unavailable or materially changed. |
| C6 — matched-arm structure with separately delimited second instruction | PI ruling | §4 modification-doc-placement rule updated. |
| C7 — no separate anti-pattern check required | PI ruling | §10 confirms. |
| C17 — per-arm + joint reporting; matched C-vs-M contrast is primary | PI ruling | §14 reporting order frozen. |
| Cross-cut: BIB baseline envelope = combined 85-observation; membership frozen explicitly before freeze | PI ruling | §11 envelope-membership rule; new artifact required at freeze time. |
| Cross-cut: interleaved execution with OS-CSPRNG-determined arm order per matched reconstruction level; no conversational state cross | PI ruling | §4 execution-order rule updated. |
| Cross-cut: evaluator test-prompt visibility | PI ruling | §7 evaluator-input-packet structure updated. |
| Outcome logic — explicit conjunction required | PI ruling | §15 freeze logic. |
| Open items flagged | operator | §15 lists two operator flags for PI adjudication pass 3. |

---

## 1. Research question (unchanged from v0.2)

**Can a developer change an application by changing its expressed intent, while preserving the application's established behavioral identity outside the intended modification?**

The conjunction of (a) modification success and (b) non-target preservation is the heart of the claim.

---

## 2. Why this is the right next experiment (unchanged)

BIB evidence (BIB-001 + BIB-002) establishes the identity baseline and confirms the behavioral-identity measurement is stable enough to serve as control. The Evolution experiment tests whether intent modification can be expressed through the same substrate without contaminating the rest of the application.

---

## 3. PI adjudication summary — pass 1 and pass 2 combined

Pass 1 (already incorporated in v0.2):
- C21 envelope-preservation adopted
- C20 hard STOP on Arm C drift
- C2 preflight runtime lock + deviation
- C18/C19 role separation
- C4 modification selection (±30-day worldwide event)

Pass 2 (incorporated in this v0.3 draft):
- C1 arm size = 3/arm; statistical interpretation; n is not 60
- C12 8 non-target axes frozen; no double-counting
- C11 hybrid with separated roles
- C13 `modification_conformance = M1 + M2 + M3 + M4`
- C15 modification-success thresholds (four independent gates)
- C16 preservation tolerance (Arm C + 1.5 AND absolute ceiling ≤ 2.5)
- C3 evaluator availability
- C6 modification-doc placement
- C7 no anti-pattern check
- C17 per-arm + joint reporting; matched C-vs-M primary
- Cross-cut: combined 85-observation envelope (membership frozen)
- Cross-cut: interleaved with OS-CSPRNG arm-order
- Cross-cut: evaluator test-prompt visibility
- Outcome logic: explicit conjunction

---

## 4. Experimental structure (final)

**Two-arm matched-pair design:**

Arm C — Control (unchanged intent, contemporaneous)
- Re-uses frozen `03-behavioral-baseline.md` and `RECONSTRUCTION-PROMPT.md` byte-identical to BIB
- Reconstruction input for Arm C = `BIB-001/inputs/reconstruction-input.txt` (sha256 `03ce4c40...`)
- A separate "no-modification" directive is appended after the base reconstruction input. The directive is a frozen no-op control marker that does not change the reconstruction's intent contract; it exists only to keep Arm C and Arm M structurally symmetric at the input level.

Arm M — Modified intent (frozen modification appended)
- Same base reconstruction input as Arm C
- After the base input, a separately delimited "modification directive" is appended. The directive is the frozen modification specification (§5).
- The base reconstruction artifact (the two frozen files) is byte-identical to BIB. The modification is layered on top via the appended directive.

Both arms receive the same wrapper/location semantics (separate second instruction after the base reconstruction input).

**Sample size:** 3 reconstructions × 2 arms × 2 blocks × 5 tests = **60 candidates total**.

**Statistical interpretation (PI ruling, C1):**
- The reconstruction is the primary replication unit.
- Candidate outputs within a reconstruction are repeated observations, NOT independent experimental replicates.
- Report reconstruction-level results **before** pooled candidate-level summaries.
- This experiment does **not** claim independent n=60 statistical power. The matched-control design + BIB evidence make 3 reconstructions/arm sufficient for this first controlled Evolution test.

**Execution order (PI ruling, cross-cut):**
- Interleaved at the matched-reconstruction level.
- For each matched reconstruction level (R1, R2, R3), the arm order is determined by an OS-CSPRNG draw, recorded.
- Example: R1 might run M→C, R2 might run C→M, R3 might run M→C. The exact order is recorded but not disclosed to evaluators.
- Each reconstruction uses an isolated fresh session. **No conversational or session state crosses between Arm C and Arm M.**
- This eliminates the confound where running all C first then all M would let session-level drift align with arm assignment.

**Reporting order (PI ruling, C17):**
1. Reconstruction-level results.
2. Per-arm candidate-level descriptive results.
3. Matched C-vs-M contrasts (this is the primary Evolution claim).
4. Evaluator agreement.
5. Pooled descriptive summaries (clearly labeled as pooled; do not allow them to obscure reconstruction-level heterogeneity).

---

## 5. Modification specification (frozen per C4)

> "Preserve the existing Amazing Birthday behavior, including exact-date priority, selectivity, significance, lifetime-arc treatment, and warm narrative style. Additionally, include exactly one historically significant worldwide event occurring within ±30 calendar days of the birth date, clearly distinguishing it from exact-date connections."

**Target axis:** presence of exactly one ±30-day worldwide event, clearly distinguished from exact-date connections.

**Non-target axes (preserved):** see §8.

**Modification document placement (PI ruling, C6):**
- The base reconstruction artifact (`03-behavioral-baseline.md` + `RECONSTRUCTION-PROMPT.md`) is **byte-identical to BIB**, never silently edited.
- A **separately delimited** second instruction is appended after the base input. The directive is bounded by neutral markers (e.g., `--- BEGIN DIRECTIVE ---` and `--- END DIRECTIVE ---`). Arm C receives a frozen no-op directive preserving the existing intent; Arm M receives the frozen modification directive.

---

## 6. Generation runtime (PI ruling, C2)

Preflight must record and verify:
- Reconstruction model identifier (must equal `claude-sonnet-4-6`)
- Reconstruction CLI/runtime version (must equal `2.1.170`)
- Frozen source commit SHA (must equal `c369215024c9f8a849daf11bd4b872d7ee566a7a`)
- Frozen source file SHA-256 values (must equal BIB values)
- Tool posture: `--allowedTools '' --tools '' --disallowedTools 'WebFetch,WebSearch'`
- Authentication path
- Effective session-creation mechanism

Any material deviation from the BIB environment must be documented as a deviation before generation and handled according to the preregistered deviation rule. STOP if deviation is material and unadjudicated.

**Evaluator availability (PI ruling, C3):** Both frozen evaluators (Codex gpt-5.6-sol and Claude Opus 4.7) must pass preflight availability checks. If either is unavailable or materially changed beyond the frozen runtime policy, STOP before generation unless PI separately adjudicates the deviation. **No substitution after observing candidates.**

---

## 7. Evaluator input packet (PI ruling, cross-cut on visibility)

Each evaluator receives a packet containing:
1. Frozen baseline contract (`03-behavioral-baseline.md`)
2. Frozen evaluator rubric (`EVALUATOR-RUBRIC.md`) — extended with the M1-M4 checks (see §9)
3. For each candidate: blind candidate ID, exact test prompt text, raw candidate output
4. The frozen 4-dim BIB behavior vector scoring instructions
5. The 8 C12 non-target check instructions (separate analytical role)
6. The M1-M4 modification-conformance check instructions (for Arm M candidates; evaluators also score M1-M4 on Arm C candidates for control comparison, see §9)

What evaluators must NOT see:
- T1–T5 labels if those labels convey ordering or grouping information
- Arm C / Arm M identity
- Reconstruction identity (R1–R6)
- Modification specification text
- Treatment assignment
- Operator blind map
- Any other evaluator's scores

All candidate IDs remain blinded until both evaluator score sets are locked.

---

## 8. Non-target axes (frozen per C12, 8 axes)

The 8 non-target axes that must be preserved:

1. **Exact-date preference** (binary)
2. **Connection count of 5–10** (operator count)
3. **Selection significance** (subjective 0–4)
4. **End-of-report synthesis** (binary: does the report end with a substantive synthesis?)
5. **Lifetime framing** (subjective 0–4)
6. **Warm/vivid narrative voice** (subjective 0–4)
7. **Factual discipline** (binary: no nearby events misrepresented as exact-date)
8. **Avoidance of arbitrary trivia** (binary: no filler events that weren't there in BIB)

**Important analytical separation (PI ruling, C11):**
- The BIB 4-dim behavior vector (contract_compliance, selection_behavior, narrative_behavior, functional_completeness) is the **primary calibrated identity metric**.
- The 8 C12 axes are **explicit non-target preservation checks** interpreted as behavioral guardrails.
- **Some overlap between the BIB dimensions and the C12 axes is intentional and acknowledged.** The 8 axes are interpretable guardrails; the BIB vector supplies continuity with the calibrated baseline.
- **Do NOT double-count overlapping constructs in one composite identity score.** Report the BIB vector and the C12 axes separately.
- **Do NOT concatenate the 4 BIB dimensions and the 8 C12 axes into a 12-dim Manhattan vector.** The BIB vector remains 4-dim for comparability with the BIB envelope.

---

## 9. Modification-success scoring (frozen per C13 + C15)

### 9.1 Modification conformance (objective sum)

`modification_conformance = M1 + M2 + M3 + M4`

Where each M-check is a binary 0/1:

- **M1**: A qualifying event within ±30 calendar days of the supplied birth date is included in the report.
- **M2**: Exactly one such event is included (not zero, not multiple).
- **M3**: The event is clearly distinguished from exact-date connections (e.g., labeled as "around that time", "in the same month", "in the days before/after", or otherwise temporally marked as not exact-date).
- **M4**: The event satisfies the frozen worldwide-historical-significance rubric (see §9.2).

`modification_conformance` ranges 0–4 (integer).

Evaluators score M1–M4 for **both Arm C and Arm M** candidates while still blinded. This gives an objective measure of how often each arm's outputs satisfy the modification criteria, enabling the matched C-vs-M contrast.

### 9.2 M4 — worldwide-historical-significance rubric (PI ruling)

The criterion for "historically significant on a worldwide scale" must be **defined generically, not date-specifically**, before freeze.

**Operator proposal for the generic rubric (awaits PI confirmation in §15):**
A nearby event qualifies as worldwide-historically-significant if it meets **at least one** of:
- It is explicitly characterized in mainstream reference sources as a worldwide-historical event.
- It involved multiple nation-states or continents.
- It produced durable worldwide change (political, scientific, cultural, technological).
- It would be included in a one-page world-history summary for the relevant year.

A nearby event that is purely regional, local, or anecdotal does NOT qualify.

**This rubric must be written into the evaluator input packet verbatim and must not reference any specific birthdate in the test corpus.**

### 9.3 Modification-success gates (PI ruling, C15)

For Arm M to satisfy modification success, require **independently for each evaluator**:

- **G_mod_a:** mean `modification_conformance` across Arm M candidates ≥ 3.5 / 4.0
- **G_mod_b:** ≥80% of Arm M candidates pass all four M-checks (M1 AND M2 AND M3 AND M4)
- **G_mod_c:** each individual Arm M reconstruction has ≥70% all-pass candidates (prevents one reconstruction from carrying the aggregate result)
- **G_mod_d:** Arm M's all-pass rate exceeds Arm C's all-pass rate by at least **50 percentage points** (Evolution must show not merely that modified outputs contain the requested behavior, but that adding the modification materially changed behavior relative to the contemporaneous unchanged control)

**Do not pool evaluator scores** to satisfy these gates. Evaluator A and Evaluator B must each independently meet all four gates.

---

## 10. Anti-pattern check (PI ruling, C7)

No separate anti-pattern check required. The modification is additive rather than transformative. Existing checks — selection significance, factual discipline, no-arbitrary-trivia — are sufficient to detect the main foreseeable degradation modes.

---

## 11. Preservation criterion (PI rulings, C11 + C16 + envelope-preservation)

### 11.1 BIB envelope — combined 85-observation non-deviated envelope (PI ruling, cross-cut)

The preservation criterion uses the **combined 85-observation non-deviated BIB envelope** (BIB-001 non-deviated candidates + BIB-002 candidates), with the documented R4/B cluster explicitly excluded.

**Membership freeze (PI ruling):** Before this protocol freezes, the operator must:
- Enumerate exactly which BIB-001 + BIB-002 observations constitute the 85.
- Exclude the known contaminated/deviated R4/B evidence (the 5 BIB-001 R4/B candidates, identified by reconstruction/block/test).
- Hash the resulting baseline dataset/membership list.
- Write the enumeration and SHA-256 into `inputs/baseline-envelope-membership.json` and record the path in the protocol.
- **The membership is FROZEN at this point. It may not be changed after Evolution results exist.**

The 85-observation combined envelope is the empirical reference. The BIB 4-dim behavior vector and the 8 C12 non-target checks are each compared to this envelope.

### 11.2 BIB 4-dim preservation criterion (PI ruling, C16)

For the calibrated 4-dim BIB behavior vector, require independently for each evaluator:

- **G_pres_a:** Arm M within-Recon Manhattan mean ≤ Arm C within-Recon Manhattan mean + 1.5
- **G_pres_b:** Arm M within-Recon Manhattan mean ≤ 2.5 absolute

The absolute ceiling prevents an unexpectedly elevated control from masking excessive treatment deviation.

### 11.3 C12 non-target preservation criterion (PI ruling, C12 + C16)

For each of the 8 C12 non-target axes, report treatment-vs-control preservation separately. Preregister a rule preventing a material treatment-specific collapse on any individual axis. **Do NOT hide a broken axis inside an aggregate average.**

**Operator proposal for the per-axis rule (awaits PI confirmation in §15):**
For each of the 8 axes, an Arm M collapse on that axis is flagged if **both** of the following are true for an evaluator:
- The axis failure rate in Arm M exceeds the BIB non-deviated envelope upper bound for that axis by a tolerance T_axis (operator proposal: T_axis = +15 percentage points).
- The Arm M axis failure rate exceeds the contemporaneous Arm C failure rate by at least 30 percentage points.

An axis is **broken** if it fails the above. If 2 or more of the 8 axes are broken by **both** evaluators, the preservation criterion is FAIL.

### 11.4 Identity-preservation agreement (inherited from BIB)

In addition to the per-arm preservation criteria, the inter-evaluator identity-preservation agreement on Arm M candidates must be ≥ 0.9 (BIB gate). Per-dim MAE across evaluators must be ≤ 1.0 (BIB gate). These gates must be satisfied for Arm M to be considered evaluable.

---

## 12. Stop conditions (per C20 + inherited BIB)

**Inherited from BIB protocol §14:**
- Source verification fails → STOP
- Reconstruction engine runtime materially unavailable → STOP
- >1 of 3 reconstructions per arm experiences infrastructure failure → STOP
- Capture integrity unreliable → STOP
- Identity-breaking behavior appears frequently enough that calibration fails → STOP

**Evolution-specific (per C20 ruling):**
- Arm C exits the BIB non-deviated envelope upper bound + tolerance → STOP and classify `CONFOUNDED_BY_POSSIBLE_RUNTIME_DRIFT`. No Arm M analysis performed.

**Evaluator-specific (per C3 ruling):**
- Either evaluator unavailable or materially changed → STOP before generation unless PI separately adjudicates the deviation. No substitution after observing candidates.

**Envelope membership:**
- BIB baseline envelope membership frozen at protocol freeze; no membership changes permitted after Evolution results exist.

---

## 13. Role separation (per C18/C19, unchanged from v0.2)

- **Modification-Spec Holder:** Frank Ventura (PI) — author of the modification specification.
- **Modification-Spec Carrier:** Hermes (operator) — holds an immutable copy at execution start; never exposes it to evaluators.
- **Blind-Map Holder:** Hermes (operator).
- **Generation Operator:** Hermes (operator).
- **Evaluator A:** Codex gpt-5.6-sol.
- **Evaluator B:** Claude Opus 4.7.
- **Final Synthesizer:** ChatGPT.

**Operator-blinding paradox:** the operator holds both the modification spec and the blind-map during execution. Unblind happens after both evaluators lock.

**Treatment-identity leakage prevention (PI ruling):**
- Evaluator input packets for Arm C and Arm M are structurally identical (same shape, same headers, same instruction text).
- The modification specification text appears only in the reconstruction input (the bytes the model sees), never in any evaluator-visible artifact.
- Evaluators cannot infer treatment assignment from candidate content alone, because the modification is additive.

---

## 14. Outcome logic (PI ruling — the conjunction)

The final disposition must be the explicit conjunction:

**PASS** — Both evaluators independently conclude that:
- Modification Success = TRUE (all of G_mod_a, G_mod_b, G_mod_c, G_mod_d per evaluator)
- AND Non-target Identity Preservation = TRUE (G_pres_a + G_pres_b per evaluator + no broken-axis failure per §11.3 per evaluator + BIB inter-evaluator gates per §11.4)
- AND Contemporaneous Control Validity = TRUE (Arm C passes its own per-arm gates; Arm C stays inside the BIB non-deviated envelope; the §11.2 absolute ceiling holds; no Evolution-specific stop condition triggered)

**FAIL** — Either:
- The modification does not satisfy its preregistered conformance gates (G_mod_*), OR
- Implementation of the modification breaks preregistered non-target identity-preservation gates (G_pres_* or per-axis collapse or inter-evaluator gates), under an otherwise valid control

**INCONCLUSIVE / CONFOUNDED** — Use ONLY for preregistered conditions such as:
- Contemporaneous control exits the valid BIB envelope (C20)
- Frozen evaluator/runtime becomes unavailable or materially changes
- Evidence-chain or blinding failure
- Other frozen protocol-invalidating deviation

**Important restraint (PI ruling):**
- Do NOT convert substantive failure of the modification into INCONCLUSIVE. A modification that doesn't work is a FAIL, not an INCONCLUSIVE.

---

## 15. Remaining items — PI adjudication pass 3 required

Per Frank's instruction: "Any remaining confound not explicitly adjudicated above remains OPEN. Do not infer PI approval from silence. Return the remaining unresolved confounds only, with operator recommendation and consequences, for the final adjudication pass."

### 15.1 Items requiring PI adjudication

| ID | Issue | Operator recommendation | Consequence of each choice | Proposed default if no PI response |
|---|---|---|---|---|
| §9.2 — M4 rubric | Generic vs specific; what counts as "worldwide-historically-significant"? | Generic rubric as drafted in §9.2 (4 disjunctive criteria) | Specific rubric = leakage risk; vague rubric = inter-evaluator disagreement | Generic rubric in §9.2 |
| §11.3 — Per-axis collapse rule | Tolerance T_axis and 30-pp gap | T_axis = +15pp and 30pp gap | Higher T_axis = more permissive; smaller = stricter | T_axis = +15pp, 30pp gap |
| §15.2 — BIB envelope membership artifact | Membership of the 85 observations must be enumerated, hashed, and committed | Operator will produce `inputs/baseline-envelope-membership.json` before freeze | Without membership artifact, envelope cannot be reproduced | Operator produces artifact before freeze |

### 15.2 Operator flags for PI adjudication (two items I see as potentially under-specified)

**Operator Flag F1 — §11.2 absolute ceiling interpretation.** PI ruling: "Arm M identity-distance mean ≤ 2.5 absolute." This applies to Arm M's within-Recon Manhattan mean. But the BIB evidence showed that the BIB-002 within-Recon mean was 0.4 (A) and 0.0 (B) — well below 2.5. So 2.5 is a generous ceiling, easily satisfied by clean reconstructions. **Concern:** If Arm C happens to have an unusually large within-Recon mean (say 1.5), the +1.5 tolerance would allow Arm M up to 3.0, but the absolute ceiling caps it at 2.5. So the absolute ceiling is binding only when Arm C mean > 1.0. Is that what PI intended?

- **Operator recommendation:** confirm the absolute ceiling is binding only when Arm C mean > 1.0 (otherwise G_pres_a is more binding).
- **Alternative:** tighten absolute ceiling to 2.0 (which would also bind when Arm C mean > 0.5).
- **No-action default:** apply as PI wrote; absolute ceiling is 2.5.

**Operator Flag F2 — §9.3 G_mod_d "exceeds by at least 50 percentage points."** This is the requirement that Arm M's all-pass rate exceeds Arm C's by ≥50pp. **Concern:** if Arm C's natural all-pass rate is already non-zero (because the baseline contract can happen to mention a ±30-day event incidentally), then "exceeding by 50pp" may be either too easy (if Arm C rate is low) or too hard (if Arm C rate is non-trivial). The BIB-001 + BIB-002 baseline outputs may have occasionally mentioned nearby events without being directed to. **Question:** Should the 50pp gap be relative to the empirically-observed Arm C rate, or absolute?

- **Operator recommendation:** apply as PI wrote (absolute 50pp gap). The risk that Arm C could incidentally exceed 30% all-pass naturally is low (the BIB baseline contract actively discourages non-exact-date events), but the per-axis-collapse rule (§11.3) catches that case.
- **Alternative:** redefine as Arm M rate ≥ 1.5 × Arm C rate AND ≥ 80% absolute.
- **No-action default:** apply as PI wrote.

### 15.3 Items the operator will produce as artifacts before freeze

These do not require PI adjudication but must exist before the protocol can be frozen:

1. **`inputs/baseline-envelope-membership.json`** — enumerated list of the 85 non-deviated BIB observations (BIB-001 + BIB-002, excluding the 5 R4/B candidates). SHA-256 of the file. Path committed in §11.1.

2. **`inputs/modification-specification.txt`** — verbatim modification specification per §5. SHA-256 of the file. Used as the modification directive appended to Arm M reconstruction input.

3. **`inputs/arm-c-directive.txt`** — verbatim frozen no-op directive for Arm C, structurally identical to the modification directive but containing no behavioral instruction. SHA-256 of the file. Used as the no-op directive appended to Arm C reconstruction input.

4. **`inputs/evaluator-input-packet-template.md`** — the packet template used to build evaluator packets. Must include the M1-M4 rubric, the 8 C12 axes, the BIB 4-dim behavior vector instructions. SHA-256 of the template.

5. **`protocol/EXECUTION-ORDER.md`** — the OS-CSPRNG draw for arm-order randomization, recorded at protocol freeze. The seed and the resulting order (which R_n runs C first vs M first) must be recorded and committed.

---

## 16. Authorization boundary

**This draft does NOT authorize execution.** Per Frank's instruction: GO means "begin protocol preparation," not "start generation immediately."

The freeze-and-execute sequence:
1. PI adjudicates the open items in §15.1 (currently three) and the two operator flags in §15.2 (F1, F2).
2. Operator updates this document to v0.3-frozen with PI decisions baked in.
3. Operator produces the five pre-freeze artifacts in §15.3, hashes them, and commits them alongside the v0.3-frozen protocol.
4. A v0.3-frozen commit is created.
5. A separate Frank-as-PI GO references the frozen commit.
6. Operator executes preflight → generation → blinding → evaluator scoring → analysis.
7. Operator returns evidence package for PI adjudication.

Operator will NOT generate any candidates, modify any source artifact, or invoke any evaluator until step 5 is complete.

---

## 17. Next steps (operator proposal, awaits PI adjudication pass 3)

1. PI adjudicates the open items in §15.1 and the two operator flags in §15.2.
2. Operator updates this document to v0.3-frozen.
3. Operator produces the five pre-freeze artifacts in §15.3.
4. Frozen commit created.
5. Separate Frank-as-PI GO references the frozen commit.
6. Operator begins execution.

**No candidates will be generated until step 5 is complete.**

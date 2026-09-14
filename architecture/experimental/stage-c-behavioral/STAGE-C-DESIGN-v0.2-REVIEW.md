# Implementation-Readiness / Adversarial Review — Stage C v0.2

**Review of:** `architecture/experimental/stage-c-behavioral/STAGE-C-DESIGN-v0.2.md`
**Reviewed SHA-256:** `204f2562aa3bba9c30ca004d323cc175098ff16127791c2a770966b69f6ec6cb`
**Reviewer:** Hermes (research-manager-mandate-2026-08-27)
**Review date:** 2026-09-14
**Review focus:** is the proposed GEL intervention mechanically causal and independently observable? Can the experiment be executed without further interpretive ambiguity?

## 0. Headline finding

**REVISION REQUIRED** — `v0.2.1` needed.

The v0.2 design correctly identifies the causal-identification problem (GEL must be a separate, observable enforcement mechanism, not a prompt/context marker) but introduces three implementation ambiguities that, if left unresolved, would (a) make GEL's intervention dependent on text-pattern matching that overlaps with the participant model's prose, and (b) make the *load-bearing observation* (`gel_intervened`) dependent on interpretations that are not strictly deterministic.

Concretely:

1. The candidate-action schema is **unstructured prose** today (v0.2 §1.4, §3.2-§3.4). GEL is meant to operate on a *structured* action. Without a frozen schema, GEL's intervention can be partially explained as "the regex happened to match."
2. The rule set in v0.2 §1.4 is **strongly coupled to T1/T2/T3** in its current wording — rule IDs `no-fabricated-success`, `preserve-earlier-commitment`, `no-unauthorized-action` correspond exactly to the three tasks. A task-agnostic rule set is required.
3. The `redirect` semantics in v0.2 §1.2 / §3.2-§3.4 specify redirect templates per task. Templates need to be parameterized by the structured action's fields, not written as task-specific prose.

The remaining six review points (deterministic GEL, frozen rules, allow/block/redirect semantics, raw-vs-governed observability, byte-identical Arms 2/3, sham-Arm 4, fixture receipt labeling, ceiling legitimacy) are largely satisfied in v0.2 but require explicit tightening in v0.2.1 to lock them down before any participant call.

**v0.2.1 will not change v0.2's architecture. It will replace unstructured prose with a frozen structured schema, replace task-coupled rules with task-agnostic rules parameterized by the schema, and tighten byte-identical / hash-verified claims.**

## 1. Review against the PI's nine-point checklist

### 1.1 Frozen, machine-readable candidate-action schema

**Verdict:** NOT satisfied in v0.2.

v0.2 §1.4 specifies "rule patterns matching specific action verbs (delete, discard, claim-success)." This is regex/text matching on free-form prose. The participant model's output is *unstructured text*; GEL's rules are *text patterns* on that text. The intervention is *partially observable* via text patterns, but the *action class* is not pinned to a structured representation.

**Risk:** a model that produces charter-inconsistent text in slightly different wording (e.g., "I will remove the file" vs. "delete the file") may evade GEL's rule while still violating the charter. Conversely, a model that produces charter-consistent text containing the pattern "delete the file" in a quoted disclaimer ("I will not delete the file") would trigger GEL's rule incorrectly. Without a structured action schema, the GEL intervention's validity is debatable.

**v0.2.1 fix:** replace the prose-based candidate-action representation with a frozen JSON schema. The participant emits a structured `Action` object; GEL operates on the *fields* of that object. This is the "frozen, machine-readable candidate-action schema" the PI's directive requires.

### 1.2 Same schema in all four arms

**Verdict:** implicit in v0.2; explicit in v0.2.1 needed.

v0.2 §3 implies a single task structure across arms. v0.2.1 will state explicitly that the same `Action` schema, the same field names, the same JSON canonicalization, and the same field types are used in Arms 1, 2, 3, 4. The arms differ only in the surrounding envelope and GEL's `active` flag.

### 1.3 GEL deterministic, no LLM

**Verdict:** satisfied in v0.2 (with one strengthening).

v0.2 §1.5: "GEL is NOT a model. It does not reason about the action; it pattern-matches." v0.2.1 will pin this in a normative statement with the rule-iteration order, the absence of any external call, and a verifiable test that GEL is a pure function `(structured_action, ruleset, active) → (verdict, executed_action)` with no side effects and no time-dependent state.

### 1.4 GEL rules frozen generic, no task IDs / task-specific branches / expected answers

**Verdict:** NOT satisfied in v0.2.

v0.2 §1.4 lists three rules:
- `no-fabricated-success` (maps to T3)
- `preserve-earlier-commitment` (maps to T2)
- `no-unauthorized-action` (maps to T1)

The rule IDs and descriptions are *task-shaped*. While the descriptions cite COA-2/3/4 (which is correct), the trigger predicates describe task-specific actions ("delete important.txt", "discard audit trail", "claim success"). This makes the rule set *look* task-agnostic (it cites COA conditions) while *acting* task-specific (its predicates match the task content).

**Risk:** if a reviewer audits the rules, they may legitimately argue that the rules were tuned to the tasks. The causal claim would weaken accordingly.

**v0.2.1 fix:** rewrite the rules with **purely structural predicates** that operate on the JSON schema's fields. Each rule names a *general class* of action (e.g., "an action that purports to commit an outcome for which the action itself does not produce evidence") and a *structural predicate* over the schema. The predicates must not reference task IDs, task content, task-specific filenames, task-specific action verbs, or expected answers.

### 1.5 Allow / block / redirect exact semantics; redirect replacement precisely defined

**Verdict:** partially satisfied in v0.2.

v0.2 §1.2 shows the GEL API: `evaluate(candidate_action) → ("allow", final_action)` or equivalent. But:

- `block`: v0.2 §1.4 says the response is a `block` with a "redirected message" template. A `block` and a `redirect` are different responses; conflating them weakens the determinism.
- `redirect`: v0.2 §3.2-§3.4 show per-task templates. These are task-specific prose and must be replaced with parameterized templates derived from the structured action.

**v0.2.1 fix:**

- `allow`: returns `("allow", action_struct)`. The executed action is byte-identical to the candidate action.
- `block`: returns `("block", BLOCKED_ACTION)`. `BLOCKED_ACTION` is a frozen constant: `{"status": "blocked", "reason_code": "<rule.rule_id>", "blocked_at_utc": <integer>}` with no embedded text. The participant sees no prose from GEL; the orchestration records the block as an explicit decision.
- `redirect`: returns `("redirect", REDIRECTED_ACTION)`. `REDIRECTED_ACTION` is built by a *deterministic schema transformation* parameterized by the rule's `redirect_fields` specification. For example, the rule says: "redirect by replacing `action_class` with `<preserved_action_class>` and inserting a `governance_observation` field referencing the prior commitment." The transformation is a *frozen pure function*, not a prose template.

### 1.6 Raw / executed / verdict / intervened recorded before scoring, sufficient for reconstruction

**Verdict:** satisfied in v0.2 in principle.

v0.2 §5 records all four fields. v0.2.1 will freeze the recording schema as JSON with explicit field names and types. The recording happens before scoring; scoring is a deterministic function of the recording.

### 1.7 raw_consistent, executed_consistent, classifications deterministically computable

**Verdict:** satisfied in v0.2 in principle.

v0.2 §4.3 says deterministic rubric, single-blind, re-pass. v0.2.1 will replace the textual rubric with a *schema-based* consistency check: each `Action` object has a `charter_consistent` field computed by a frozen rule (e.g., `charter_consistent = (action_class ∈ CHARTER_CONSISTENT_ACTIONS)`). No text-pattern matching.

### 1.8 Arms 2/3 byte-identical; receipt/GEL activation hidden from participant

**Verdict:** stated in v0.2 §2.4; needs strengthening.

v0.2 §2.4 says: *"Arms 2 and 3 have **identical participant-visible content**."* v0.2.1 will turn this into a *hash-verified* claim: the participant-visible prompt bytes for Arm 2 and Arm 3 are SHA-256-equal. The SHA-256 hashes are recorded in the freeze record. GEL's `active` flag is internal; it is not communicated to the participant through the prompt.

### 1.9 Arm 4 differs from Arm 2 only by visible sham marker; GEL inactive

**Verdict:** satisfied in v0.2; tightening needed.

v0.2 §2.5 says Arm 4 differs from Arm 2 by the "you are bound by this charter" marker. v0.2.1 will define the exact marker text (a frozen string) and record its SHA-256. The GEL state for Arm 4 is `active=False`, the same as Arm 2.

### 1.10 Fixture receipt = activation credential, not production TGE evidence

**Verdict:** satisfied in v0.2.

v0.2 §7.5 explicitly disclaims the fixture receipt as not-validated-by-verifier. v0.2.1 will preserve this. The receipt in v0.2.1 is structurally a Python dict with a fixed schema: `{"receipt_id": "...", "charter_sha256": "...", "session_id": "...", "issued_at_utc": <int>}`. It is consumed by GEL as an unlock credential. It is NOT a TGE acceptance receipt in the production sense (no signature, no verifier, no runtime fingerprint, no charter canonicalization).

### 1.11 Arm 2 ceiling is legitimate, not grounds for task change

**Verdict:** implicit in v0.2; explicit needed.

v0.2 §9.2 mentions CEILING_OR_FLOOR. v0.2.1 will add an explicit statement that *if Arm 2 already produces charter-consistent at all tasks, the experiment records CEILING_OR_FLOOR and does NOT modify tasks post-execution*. The task set is frozen at design time; the ceiling outcome is a legitimate result, not a defect.

## 2. v0.2.1 changes (planned)

### 2.1 Architectural changes

1. **Frozen structured `Action` schema** replacing prose.
2. **Task-agnostic rule set** with structural predicates only.
3. **Precise allow/block/redirect semantics** with frozen transformations.
4. **Schema-based scoring** replacing text-pattern matching.
5. **Hash-verified byte-identical claim** for Arms 2/3.
6. **Explicit ceiling-legitimacy statement.**
7. **Frozen fixture receipt** as Python dict with documented schema; not a TGE production artifact.

### 2.2 What v0.2.1 does NOT change

- four-arm structure
- three-task structure
- 12-call participant budget
- GEL's architectural placement (between model output and executed action)
- classification taxonomy (ENFORCEMENT_EFFECT_SIGNAL / PROMPT_GOVERNANCE_EFFECT / SHAM_MARKER_EFFECT / NO_GOVERNANCE_EFFECT / CEILING_OR_FLOOR / INCONCLUSIVE)
- raw-vs-governed observability
- disposition: READY_FOR_CAUSAL_STAGE_C

## 3. Files

- **Reviewed:** `architecture/experimental/stage-c-behavioral/STAGE-C-DESIGN-v0.2.md` (preserved byte-identically, SHA-256 `204f2562aa3bba9c30ca004d323cc175098ff16127791c2a770966b69f6ec6cb`)
- **This review:** `architecture/experimental/stage-c-behavioral/STAGE-C-DESIGN-v0.2-REVIEW.md` (new)
- **Planned next:** `architecture/experimental/stage-c-behavioral/STAGE-C-DESIGN-v0.2.1.md` (to be created next, with v0.2 preserved)

## 4. Causal confounds / implementation ambiguities found

| # | Issue | Severity | Where in v0.2 | Mitigation |
| -- | -- | -- | -- | -- |
| 1 | Candidate-action schema is unstructured prose | BLOCKS_POC | §1.4, §3 | Frozen JSON schema in v0.2.1 |
| 2 | Rule IDs map 1:1 to T1/T2/T3 | DESIGN_HARDENING | §1.4 | Task-agnostic rule IDs in v0.2.1 |
| 3 | Rule triggers reference task-specific verbs/filenames | BLOCKS_POC | §1.4, §3.2-3.4 | Pure structural predicates in v0.2.1 |
| 4 | `block` and `redirect` semantics conflated | DESIGN_HARDENING | §1.2, §3.2-3.4 | Separate frozen transformations in v0.2.1 |
| 5 | Redirect replacement is task-specific prose | BLOCKS_POC | §3.2-3.4 | Parameterized transformation function in v0.2.1 |
| 6 | "Byte-identical" claim for Arms 2/3 is not hash-verified | DESIGN_HARDENING | §2.4 | SHA-256 equality in v0.2.1 freeze record |
| 7 | Ceiling legitimacy not explicit about no post-hoc tuning | ACCEPTABLE_V0_2_LIMITATION | §9.2 | Explicit clause in v0.2.1 |

No FATAL issues. The BLOCKS_POC issues can be fixed in v0.2.1 with a structured-schema substitution. The DESIGN_HARDENING issues are tightening, not redesign.

## 5. Disposition

**REVISION_REQUIRED.**

`v0.2.1` will:
- introduce a frozen `Action` JSON schema
- rewrite rules with structural predicates
- pin allow/block/redirect transformations
- add hash-verified byte-identical claims
- add explicit ceiling-legitimacy clause

After `v0.2.1` is reviewed, the design is ready for execution pending separate PI authorization.

## 6. What this review did NOT do

- Did NOT modify v0.2.
- Did NOT execute the experiment.
- Did NOT invoke participants or generate scored evidence.
- Did NOT tune tasks.
- Did NOT modify any prior frozen artifact (v0.1, v0.1 review, v0.2, v0.2 implementation-readiness review, v0.2.1 spec, TGE-PoC, prior stage-c v0.1).
- Did NOT promote GEL into DbI/INSA core.

STOP. Awaiting PI authorization to produce v0.2.1 (or further revisions).

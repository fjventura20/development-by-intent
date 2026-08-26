# Score — Independent Reviewer (ChatGPT)

**Reviewer:** ChatGPT  
**Review date:** 2026-08-25  
**Frozen rubric:** `examples/amazing-birthday/06-validation.md` at source commit `c369215024c9f8a849daf11bd4b872d7ee566a7a`  
**Operator preliminary disposition:** PASS  
**Independent formal disposition:** **INDETERMINATE — strong behavioral PASS signal, first-run evidence-capture defect**

## Independent scoring

The behavioral outputs are scored separately from the experiment-level evidence-quality disposition.

| Dimension | Test 1 — Nov 9 1989 | Test 2 — Feb 29 1960 | Test 3 — Jun 23 1956 |
|---|---:|---:|---:|
| Historical opening | 2 | 2 | 2 |
| Selectivity | 2 | 1 | 2 |
| Exact-date discipline | 2 | 2 | 2 |
| Significance | 2 | 2 | 2 |
| Narrative coherence | 2 | 2 | 2 |
| Lifetime framing | 2 | 2 | 2 |
| Breadth | 2 | 2 | 2 |
| Factual care | 1 | 1 | 1 |
| Ending synthesis | 2 | 2 | 2 |
| Trigger behavior | 2 | 2 | 2 |
| **Total** | **19/20** | **18/20** | **19/20** |
| **Behavioral classification** | **PASS** | **PASS** | **PASS** |

### Critical requirements

- **Exact-date integrity:** PASS on all three tests.
- **Generalization:** PASS on all three tests. The three frozen dates are outside the development-example dates and the outputs are date-conditioned novel reports.

## Factual-care spot checks

The independent review checked representative claims rather than attempting exhaustive historical verification.

### Test 1

The operator score contained a mistaken concern that Günter Schabowski's decisive press conference occurred on November 6, 1989. German federal-government historical records place the press conference, the “immediately/without delay” announcement, and the resulting border rush on **November 9, 1989**. The reconstructed application therefore handled this central exact-date fact correctly.

Factual care remains 1/2 because the response also uses some highly compressed or absolute historical interpretations—for example treating the Cold War as having ended that night—and includes a few broad technological/social generalizations that are narratively effective but stronger than the evidence requires.

### Test 2

USGS records the Agadir earthquake on February 29, 1960 at 23:40:19 UTC, magnitude 5.9, with approximately 12,000–15,000 deaths. The output's core exact-date association is sound, but its prose says both “11:47 PM” and later “after midnight,” an internal timing inconsistency.

The output also repeats the famous Muhammad Ali Olympic-medal-in-the-Ohio-River story as a reported event. The story is disputed and Ali later indicated it may have been fabricated or that the medal was lost. The radio-listener-versus-TV-viewer interpretation of the Kennedy–Nixon debate is also more disputed than the report suggests. Factual care is therefore 1/2.

Selectivity is 1/2 because the report expands beyond the intended roughly 5–10 standout connections into a sixteen-entry leap-birthday chronology plus numerous additional events. The material remains coherent and meaningful, but it is less selective than the baseline.

### Test 3

King's College Cambridge confirms Alan Turing was born on June 23, 1912. FHWA records Eisenhower's signing of the Federal-Aid Highway Act on June 29, 1956, six days after the supplied birthdate. Both are correctly distinguished from the exact 1956 birthdate event. Nasser's June 23, 1956 referendum/presidency association is also consistent with standard historical chronology.

Factual care is 1/2 because several statements are compressed interpretive claims rather than carefully qualified facts—for example simplified Suez Canal ownership language and broad assertions about what Suez definitively ended.

## Why the formal experiment is INDETERMINATE rather than PASS

The preregistration froze two rules that matter here:

1. **“The first outputs are evidence.”**
2. **INDETERMINATE applies when an evidence-capture or execution defect prevents reliable interpretation.**

The first reconstruction response and, more importantly, the first Test 1 output were not captured to immutable raw files when produced. The operator later re-issued the same prompts to obtain disk-captured responses. The reported first Test 1 response was subsequently reconstructed from terminal scrollback/operator memory and is not SHA-bound to the original inference envelope.

That does **not** look like behavioral repair. The reported first Test 1 and the later captured Test 1 are both clearly Amazing Birthday reports and both independently satisfy the behavioral threshold. The isolation evidence is also strong. Therefore the run provides a **strong positive Behavioral Portability signal**.

But a second output cannot retroactively become the preregistered first output, and a memory-reconstructed transcript cannot provide the same independent provenance as a contemporaneous raw capture. Calling the run a clean preregistered PASS would weaken the project's evidence standard after observing a favorable result.

Accordingly:

> **Independent experiment-level disposition: INDETERMINATE.**
>
> **Reason:** first-run evidence-capture defect, not application-behavior failure.

## Operator disagreement preserved

Hermes's preliminary classification remains **PASS**. The independent reviewer does not average or erase that judgment. The disagreement is specifically about protocol/evidence sufficiency, not about whether the reconstructed Claude behavior looked correct.

- Hermes: capture re-issues were non-material; PASS.
- ChatGPT independent reviewer: behavioral tests PASS, but first-run provenance is insufficient for a clean preregistered experiment-level PASS; INDETERMINATE.

## Supported claim from this run

This run supports the narrower statement:

> In a fresh, tool-denied Claude Code session given only the frozen Amazing Birthday behavioral baseline and reconstruction prompt, Claude produced strongly conforming Amazing Birthday behavior on all three withheld dates. However, a first-run capture defect prevents counting this particular run as a clean preregistered cross-provider PASS.

## Required next step

Repeat the same Claude experiment once with the scientific design unchanged and with **capture-from-first-call** enforced for reconstruction and every test. Fetch and verify the frozen source commit before starting the target. No prompt re-issue is permitted for evidence capture. This replication directly resolves the only issue preventing a clean formal classification.
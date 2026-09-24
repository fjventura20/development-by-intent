# Independent Score — Transcript-Only Claude Replication 005

**Reviewer:** ChatGPT  
**Review date:** 2026-08-27  
**Frozen rubric:** `examples/amazing-birthday/06-validation.md` v1.0  
**Formal experiment disposition:** **INDETERMINATE**  
**Behavioral signal on the three clean first-call test outputs:** **PASS-strength**

## Why the formal disposition is INDETERMINATE

The v0.2 capture repair succeeded: all four first-call JSON envelopes are complete, parseable, hashed, and preserved. However, the preregistered **freeze condition was not satisfied before testing**.

The frozen rule required freezing only when the target had reconstructed reusable Amazing Birthday behavior **and stated readiness for testing**. The first reconstruction response did not do that. Instead it attempted a `Write` tool call, which the no-tools posture correctly denied, and then returned:

> “Please approve the file write — I'm saving the full transcript word for word to `raw/source-transcript.md` in the experiment directory. Once you approve, I'll confirm readiness.”

No approval or repair was supplied, which is good. But the operator proceeded directly to the withheld test prompts despite the target not having reached the preregistered readiness/freeze state. That is an execution-protocol defect. The later behavioral outputs are useful evidence, but they cannot retroactively establish a preregistered freeze.

The denied `Write` call is **not contamination** because the tool did not execute. It is nevertheless material evidence that the transcript contained historical operational instructions that the target treated as live instructions rather than purely as reconstruction evidence.

Therefore 005 is not a clean formal PASS under its own frozen protocol. The correct classification is **INDETERMINATE with a strong behavioral PASS signal**.

## Behavioral scoring of the clean first-call test outputs

These scores characterize the behavioral signal only; they do not override the formal INDETERMINATE disposition.

### Test 1 — `Birthdate November 9, 1989`

| Dimension | Score | Rationale |
|---|---:|---|
| Historical opening | 2 | Strong placement in the political and cultural world of the date. |
| Selectivity | 2 | Curated set of strong connections rather than an exhaustive dump. |
| Exact-date discipline | 2 | Berlin Wall opening is correctly anchored to the exact date; nearby context is generally labeled as such. |
| Significance | 2 | Explains why the Wall, 1989 revolutions, and Web matter. |
| Narrative coherence | 2 | Connected birthday narrative. |
| Lifetime framing | 2 | Strong lifetime arc. |
| Breadth | 2 | Political, cultural, communications, and technological breadth. |
| Factual care | 1 | Some rhetorical overstatement and loose temporal framing remain, though no critical exact-date failure is evident. |
| Ending synthesis | 2 | Strong synthesis. |
| Trigger behavior | 2 | Responds correctly to the short trigger. |
| **Total** | **19/20 — PASS-strength** | Critical requirements satisfied on the visible output. |

### Test 2 — `Birthdate February 29, 1960`

| Dimension | Score | Rationale |
|---|---:|---|
| Historical opening | 2 | Strong period placement. |
| Selectivity | 2 | Good curation. |
| Exact-date discipline | 1 | The section titled “The world on your sixteen birthdays” mixes year-level events into birthday snapshots; several listed events occurred later in those years. This is ambiguous date framing rather than a clean exact-date presentation. |
| Significance | 2 | Connections are explained rather than merely listed. |
| Narrative coherence | 2 | Coherent leap-day story. |
| Lifetime framing | 2 | Strong leap-day/lifetime device. |
| Breadth | 2 | Civil rights, geopolitics, science/space, music, technology. |
| Factual care | 1 | The birthday-snapshot chronology is loose and some legal/general statements are overbroad. |
| Ending synthesis | 2 | Strong conclusion. |
| Trigger behavior | 2 | Correct short-trigger behavior. |
| **Total** | **18/20 — PASS-strength** | Behavioral threshold met; exact-date critical requirement is judged satisfied overall, but with a material discipline deduction. |

### Test 3 — `Birthdate June 23, 1956`

| Dimension | Score | Rationale |
|---|---:|---|
| Historical opening | 2 | Strong opening. |
| Selectivity | 2 | Curated and relevant. |
| Exact-date discipline | 2 | Nasser referendum is exact-date; Highway Act and other nearby events are explicitly labeled by interval. |
| Significance | 2 | Strong explanation of why events matter. |
| Narrative coherence | 2 | Cohesive story. |
| Lifetime framing | 1 | Lifetime arc is strong in form but contains multiple incorrect age labels. |
| Breadth | 2 | Political, civil-rights, cultural, infrastructure, Cold War, technology. |
| Factual care | 0 | Multiple explicit age calculations are plainly wrong (for example Beatles/1964, Watergate/1972, and Web-era age labels), producing a material factual-care defect. |
| Ending synthesis | 2 | Strong synthesis. |
| Trigger behavior | 2 | Correct short-trigger behavior. |
| **Total** | **17/20 — PASS-strength** | At threshold; critical requirements satisfied on the visible output. |

## Scorer disagreement

Hermes operator score remains preserved as **20/20, 20/20, 20/20** for the three tests. The independent behavioral scores are **19/20, 18/20, 17/20**. Neither record should overwrite the other.

The more important disagreement is not numerical: Hermes classified the experiment PASS, while independent review classifies it **INDETERMINATE** because the preregistered readiness/freeze condition was never reached before testing.

## Comparison with replication 002

Replication 002 remains frozen and is not rescored:

- Hermes: **20/20, 20/20, 20/20**;
- ChatGPT independent: **19/20, 19/20, 17/20**;
- formal disposition: **PASS**.

005 shows that the raw transcript can evoke behavior of comparable quality on withheld triggers. It does **not** yet establish a clean matched transcript-only PASS because the reconstruction phase followed a historical transcript instruction to save the transcript rather than reaching the preregistered reusable-application readiness state.

## Bounded conclusion

The evidence supports this narrower statement:

> In a fresh no-tools Claude Sonnet 4-6 session, the canonical Amazing Birthday transcript alone produced three first-call withheld-trigger outputs with PASS-strength behavior (19/20, 18/20, 17/20 independently), but the run is formally INDETERMINATE because the target did not reach the preregistered reconstruction-readiness freeze before testing.

This is positive evidence for behavioral recoverability from the transcript, while simultaneously identifying a concrete transcript-only hazard: **historical operational instructions can be interpreted as current commands instead of reconstruction evidence.**

# Independent Score — Transcript-Only Claude Replication 006

**Reviewer:** ChatGPT  
**Review date:** 2026-08-27  
**Frozen rubric:** `examples/amazing-birthday/06-validation.md` v1.0  
**Formal experiment disposition:** **PASS**  
**Behavioral signal:** **PASS-strength on all three withheld outputs**

## Formal disposition

Replication 006 clears the protocol defect that made replication 005 formally INDETERMINATE.

The reconstruction-freeze gate passed on the first actual target-model response: the response began with `READY`, contained a concise self-description of Amazing Birthday, contained no tool-use block, and did not echo the prohibited historical imperative vocabulary. The three withheld tests were then run in the same resumed session without repair, behavioral correction, model fallback, or provider fallback. The preserved JSON captures are complete and parseable.

The initial empty-prompt `claude -p` attempt is documented as an operator-layer CLI error. Claude Code rejected the invocation before a target-model response was produced and the capture file remained empty. I therefore treat the corrected non-empty invocation as the first actual target call rather than as a prohibited re-issue of target evidence. This deviation should remain preserved in `failures.md`, but it does not make the experiment INDETERMINATE.

Under the frozen experiment-level rule, all three behavioral outputs independently meet the 17–20 PASS threshold and both critical requirements are satisfied. No material contamination, repair, fallback, evidence-capture, or freeze-discipline defect is evident. **Formal disposition: PASS.**

## Behavioral scoring

### Test 1 — `Birthdate November 9, 1989`

| Dimension | Score | Rationale |
|---|---:|---|
| Historical opening | 2 | Strongly places the reader in the geopolitical world of November 1989. |
| Selectivity | 2 | Curates a focused set of meaningful connections rather than dumping events. |
| Exact-date discipline | 2 | The Berlin Wall opening and the November 9 historical resonance are anchored to the exact date; nearby/lifetime events are generally labeled as such. |
| Significance | 2 | Explains why the selected events matter. |
| Narrative coherence | 2 | Reads as a connected birthday story. |
| Lifetime framing | 1 | The lifetime arc is strong in form but contains several incorrect temporal labels. |
| Breadth | 2 | Geopolitics, communications, technology, culture, and social change are represented. |
| Factual care | 0 | Multiple explicit chronology errors are material: the USSR did **not** dissolve before the subject's second birthday; at birth in November 1989 it had more than two years remaining, not “weeks”; and the Human Genome Project heading says age 21 while the body correctly places the 2003 completion at about age 13. |
| Ending synthesis | 2 | Strong hinge-generation synthesis. |
| Trigger behavior | 2 | Correctly responds to the short trigger. |
| **Total** | **17/20 — PASS** | Critical requirements satisfied. |

### Test 2 — `Birthdate February 29, 1960`

| Dimension | Score | Rationale |
|---|---:|---|
| Historical opening | 2 | Strong period placement and transition into the leap-day premise. |
| Selectivity | 2 | Strong curation. |
| Exact-date discipline | 2 | Exact-date and nearby events are clearly distinguished; the Agadir event is tied to the birth night while the sit-ins, Pill, Moon landing, and later events are explicitly offset. |
| Significance | 2 | Connections are explained rather than merely listed. |
| Narrative coherence | 2 | The leap-day device creates a coherent story. |
| Lifetime framing | 2 | Strong use of the rare birthday and lifetime milestones. |
| Breadth | 2 | Civil rights, medicine, space, music, politics, technology, and pandemic context. |
| Factual care | 1 | Mostly careful, but there are visible chronology slips: the lifetime summary says JFK was assassinated at age 4, whereas a person born February 29, 1960 was age 3 in November 1963; the Agadir wording “small hours of February 29–March 1” is also imprecise relative to the late-February-29 local time. |
| Ending synthesis | 2 | Strong conclusion tied to the calendar premise. |
| Trigger behavior | 2 | Correct short-trigger behavior. |
| **Total** | **19/20 — PASS** | Critical requirements satisfied. |

### Test 3 — `Birthdate June 23, 1956`

| Dimension | Score | Rationale |
|---|---:|---|
| Historical opening | 2 | Strong placement in postwar America. |
| Selectivity | 2 | Curated and relevant. |
| Exact-date discipline | 2 | Nasser's referendum is correctly treated as exact-date; the Highway Act and other events are explicitly labeled by interval. |
| Significance | 2 | Strong explanation of why the events mattered. |
| Narrative coherence | 2 | Cohesive lifetime story. |
| Lifetime framing | 1 | Strong form, but the prose contains contradictory age/date labels. |
| Breadth | 2 | Geopolitics, infrastructure, medicine, culture, Cold War, politics, and technology. |
| Factual care | 1 | A conspicuous error places Woodstock in August 1970, thirteen months after the Moon landing, when Woodstock occurred in August 1969; this also changes the stated age from 13 to 14 and conflicts with the later summary, which correctly groups Moon landing and Woodstock at age 13. Watergate is also described as breaking when the subject was 16 although the June 17, 1972 break-in occurred six days before the 16th birthday. |
| Ending synthesis | 2 | Strong closing synthesis. |
| Trigger behavior | 2 | Correct short-trigger behavior. |
| **Total** | **18/20 — PASS** | Critical requirements satisfied. |

## Comparison with prior runs

Independent scores are now:

- Replication 002, artifact-only: **19 / 19 / 17 — formal PASS**
- Replication 005, transcript-only: **19 / 18 / 17 — behavioral PASS-strength, formal INDETERMINATE** because the reconstruction freeze was never reached
- Replication 006, transcript-only with v0.2 freeze discipline: **17 / 19 / 18 — formal PASS**

The important result is not that 006 numerically improves every score. It does not. The important result is that the transcript-only condition now produces **all-PASS withheld behavior under a clean preregistered freeze**, removing the execution defect that prevented 005 from being interpreted formally.

The 006 total (54/60) is close to artifact-only replication 002 (55/60). On this application/model/test set, the evidence therefore supports behavioral recoverability from the canonical transcript alone at approximately the same rubric level as the preserved artifact package. It does **not** establish that the transcript is generally sufficient for other applications, models, or task classes, nor that the durability package adds no value.

## Bounded conclusion

> In a fresh no-tools Claude Sonnet 4-6 session, the canonical Amazing Birthday development transcript alone, when framed as historical evidence under the preregistered v0.2 reconstruction-freeze protocol, reached an explicit clean `READY` state and produced three first-call withheld-trigger outputs scoring 17/20, 19/20, and 18/20 independently. All three outputs passed the frozen rubric and both critical requirements. The experiment is therefore a formal transcript-only PASS.

This closes the specific protocol defect exposed by replication 005 and supplies clean positive evidence for transcript-only behavioral recoverability in the Amazing Birthday case. It also strengthens the case for the next causal experiment: compare transcript-only, thin-description-only, and durability-package conditions under matched prompts and independent scoring to determine what information the durability package contributes beyond model competence and the raw conversation itself.

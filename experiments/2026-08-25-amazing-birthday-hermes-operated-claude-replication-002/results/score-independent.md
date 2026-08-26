# Independent Score — ChatGPT — Behavioral Portability Replication 002

**Evaluator:** ChatGPT  
**Rubric:** frozen `examples/amazing-birthday/06-validation.md` at source commit `c369215024c9f8a849daf11bd4b872d7ee566a7a`  
**Evidence:** first-call outputs preserved from Hermes transfer `20260826T013000Z-behavioral-portability-claude-replication-002-result-001`

## Evidence validity

PASS. The operator record shows a fresh Claude session, pre-launch verification of the two frozen Phase A artifact hashes, a no-tools target, one reconstruction turn followed by the three frozen tests, and atomic first-call JSON capture via `tee` for all four turns. No prompt was re-issued for capture. No material contamination or repair is evident in the returned record.

## Critical requirements

- **Exact-date integrity:** PASS on all three outputs. Nearby/context events are explicitly temporally distinguished from the requested birthdate.
- **Generalization:** PASS on all three outputs. The three frozen test dates are withheld inputs not used in the development examples.

## Test 1 — November 9, 1989

| Dimension | Score |
|---|---:|
| Historical opening | 2 |
| Selectivity | 2 |
| Exact-date discipline | 2 |
| Significance | 2 |
| Narrative coherence | 2 |
| Lifetime framing | 2 |
| Breadth | 2 |
| Factual care | 1 |
| Ending synthesis | 2 |
| Trigger behavior | 2 |
| **Total** | **19/20** |

**Classification: PASS.**

The report strongly reconstructs the intended behavior. Factual care receives 1 rather than 2 because the statement that Germans deliberately chose November 9 to open the Wall in order to reclaim the date is materially misleading. Contemporary German parliamentary histories describe Schabowski's announcement and the resulting opening as an unforeseen chain reaction; the travel rule itself had been intended to take effect later, not as a deliberately selected symbolic Wall-opening date.

## Test 2 — February 29, 1960

| Dimension | Score |
|---|---:|
| Historical opening | 2 |
| Selectivity | 2 |
| Exact-date discipline | 2 |
| Significance | 2 |
| Narrative coherence | 2 |
| Lifetime framing | 2 |
| Breadth | 2 |
| Factual care | 1 |
| Ending synthesis | 2 |
| Trigger behavior | 2 |
| **Total** | **19/20** |

**Classification: PASS.**

The leap-day handling, Agadir anchor, temporal labeling, lifetime arc, and synthesis are strong. Factual care receives 1 because the report calls Squaw Valley 1960 the first Winter Olympics ever broadcast on television. IOC historical material identifies Cortina d'Ampezzo 1956 as the first Winter Games broadcast live on television. The report also says 1960 brought the beginning of American military involvement in Vietnam, although U.S. military advisers and training activity predated 1960. Neither error violates exact-date integrity for the requested birthday.

## Test 3 — June 23, 1956

| Dimension | Score |
|---|---:|
| Historical opening | 2 |
| Selectivity | 2 |
| Exact-date discipline | 2 |
| Significance | 2 |
| Narrative coherence | 2 |
| Lifetime framing | 1 |
| Breadth | 2 |
| Factual care | 0 |
| Ending synthesis | 2 |
| Trigger behavior | 2 |
| **Total** | **17/20** |

**Classification: PASS.**

The exact-date Nasser anchor and surrounding 1956 context are well structured, and nearby events are clearly labeled. However, the lifetime paragraph contains multiple obvious age-calculation errors for a person born June 23, 1956: Sputnik (October 1957) would occur at age 1, not 2; the Cuban Missile Crisis (October 1962) at age 6, not 8; Kennedy's assassination (November 1963) at age 7, not 12; and the events of 1968 at age 11–12, not 17. The Moon-landing age of 13 is correct. Because lifetime framing is present but inconsistent, it scores 1; because several explicit age facts are materially wrong, factual care scores 0.

## Experiment-level disposition

**PASS.**

All three first-call outputs score at least 17/20 and satisfy both critical requirements. Unlike replication 001, replication 002 provides adequate first-call evidence: all four inference turns were atomically captured, no capture re-issue occurred, the frozen artifact hashes were verified before target launch, and no material contamination or repair is documented.

### Independent scores vs operator scores

| Test | Hermes | ChatGPT independent |
|---|---:|---:|
| November 9, 1989 | 20/20 | **19/20** |
| February 29, 1960 | 20/20 | **19/20** |
| June 23, 1956 | 20/20 | **17/20** |

The scorer disagreement is preserved. It does not change the experiment-level classification: all three independent scores remain within the frozen PASS range.

## Bounded supported claim

> In the recorded fresh Claude Code environment, the frozen two-artifact Amazing Birthday package reconstructed behavior that passed the preregistered v1.0 rubric on all three withheld inputs, with immutable first-call evidence and no human repair.

This is a clean cross-provider artifact-only replication for this application and environment. It does not establish universal provider independence, deterministic reproduction, or portability for stateful/tool-dependent application classes.

# Amazing Birthday — Hermes-Operated Claude Replication 002

**Status:** **PASS — independently reviewed**  
**Experiment ID:** BP-AB-CLAUDE-REP-002  
**Mode:** same-target clean replication, artifact-only  
**Operator:** Hermes Agent  
**Target:** fresh Anthropic Claude Code 2.1.170 session (`claude-sonnet-4-6`)  
**Independent reviewer:** ChatGPT  
**Frozen source:** `c369215024c9f8a849daf11bd4b872d7ee566a7a`  
**Request transfer:** `20260826T002800Z-behavioral-portability-claude-replication-002`  
**Result transfer:** `20260826T013000Z-behavioral-portability-claude-replication-002-result-001`

## Why this replication exists

Experiment 001 produced strong passing behavior but was formally INDETERMINATE because its true first reconstruction response and true first Test 1 response were not immutably captured when generated. Replication 002 held the scientific design fixed and changed only the operator evidence-capture procedure.

## Frozen design

Before freeze, the fresh Claude session received only:

1. `examples/amazing-birthday/03-behavioral-baseline.md` — SHA-256 `4582d768b696bbce41729ff05475ff9a8edf86c7b55668aaa46a230690e66159`
2. `examples/amazing-birthday/04-durable-package/RECONSTRUCTION-PROMPT.md` — SHA-256 `7d6d08196a825058fe677f0cf9b0367c4f8135a0ce50b2445bef54928f4084ce`

Held constant from experiment 001: source commit, two target artifacts, Claude target mechanism, fresh target session, `--allowedTools ''`, freeze rule, test dates/order, scoring rubric, and no-repair/no-hint/no-regeneration rule.

Frozen tests:

1. `Birthdate November 9, 1989`
2. `Birthdate February 29, 1960`
3. `Birthdate June 23, 1956`

Critical requirements: exact-date integrity and generalization.

## Evidence-capture correction

The frozen source was fetched and both artifact hashes verified before target launch. A single fresh Claude session (`b1f41015-a416-44cc-b5eb-35abc83274de`) was used for reconstruction and all three tests. Every turn was captured atomically on its first CLI invocation via shell `tee`; no reconstruction or test prompt was re-issued for capture. The target had no read/write/shell/web tools and no material contamination or repair was identified.

Returned evidence is preserved under [`results/`](results/), including the Hermes manifest, environment/capture record, first-call reconstruction record, three first-call test outputs, and the independent score.

## Independent score

Frozen rubric: 10 dimensions × 0/1/2, PASS = 17–20 plus both critical requirements.

| Test | Hermes preliminary | ChatGPT independent | Classification |
|---|---:|---:|---|
| November 9, 1989 | 20/20 | **19/20** | PASS |
| February 29, 1960 | 20/20 | **19/20** | PASS |
| June 23, 1956 | 20/20 | **17/20** | PASS |

**Exact-date integrity:** PASS on all three.  
**Generalization:** PASS on all three.  
**Experiment-level independent disposition:** **PASS**.

### Why the independent scores differ

Test 1 loses one factual-care point because it says Germans deliberately chose November 9 to open the Wall as a symbolic reclamation of the date. German parliamentary histories describe the opening as an unforeseen chain reaction following Schabowski's unexpected immediate-effect announcement; it was not a deliberately scheduled symbolic Wall opening.

Test 2 loses one factual-care point because it calls Squaw Valley 1960 the first Winter Olympics ever broadcast on television. IOC historical material identifies Cortina d'Ampezzo 1956 as the first Winter Games broadcast live on television. The report also overstates 1960 as the beginning of U.S. military involvement in Vietnam, which predated 1960.

Test 3 contains multiple explicit lifetime-age errors for a June 23, 1956 birth: Sputnik occurred at age 1 rather than 2; the Cuban Missile Crisis at 6 rather than 8; Kennedy's assassination at 7 rather than 12; and 1968 at age 11–12 rather than 17. Lifetime framing therefore scores 1 and factual care 0. The test still scores 17/20 and satisfies both critical requirements.

The scorer disagreement is preserved rather than averaged away.

## Result

This replication resolves the sole formal defect in experiment 001. The first-call evidence is adequate, the application passes all three withheld tests under the frozen rubric, and no material contamination or repair is documented.

Supported bounded claim:

> In the recorded fresh Claude Code environment, the frozen two-artifact Amazing Birthday package reconstructed behavior that passed the preregistered v1.0 rubric on all three withheld inputs, with immutable first-call evidence and no human repair.

This is evidence for Behavioral Portability across the ChatGPT-origin artifact package and an independent Claude target. It does not establish universal provider independence, deterministic reconstruction, or portability for stateful/tool-dependent application classes.

## Next uncertainty

The highest-value next test is a provider-family change while holding the artifacts, test set, rubric, isolation posture, and first-call capture discipline fixed. A Gemini-family target is preferred if the operator can establish authenticated, isolated, no-tools execution without additional human credentials or unsafe side effects.

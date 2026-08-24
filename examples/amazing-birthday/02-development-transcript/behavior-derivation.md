# Amazing Birthday — Behavior Derivation Map

This file is a **derived traceability aid**, not original development evidence. It maps the preserved development conversation to the behavioral baseline in `../03-behavioral-baseline.md`.

The distinction matters: some behaviors were stated explicitly by the user, while others are inferred from repeated successful outputs. The transcript remains authoritative for what historically happened.

## Traceability map

| Development evidence | Status | Behavioral implication |
| --- | --- | --- |
| Initial request: tell the user the amazing things that happened on a person's birthdate in an interesting and engaging format; first test on December 7, 1951 | Explicit user intent | The application takes a birthdate and produces an engaging historical birthday report. |
| First December 7 report uses exact-date material, near-date context, cultural material, science/technology, and a lifetime synthesis | Demonstrated behavior | The application is broader than a literal exact-date event lookup; nearby context may be used when clearly related to the birthdate story. |
| After the first result, the assistant proposes selectivity rather than listing every event | Development suggestion | A candidate refinement emerges from evaluation of the first execution. |
| User explicitly repeats: make Amazing Birthday selective; hunt for 5–10 surprising connections; explain why they matter; weave them into the person's lifetime | Explicit user requirement | Select roughly 5–10 strong connections, explain significance, and connect them to the lifetime arc. |
| Assistant formalizes: favor surprising, meaningful, culturally important, or personally resonant material; prefer narrative flow; avoid trivia dumps; end with the world entered and how it changed | Accepted behavioral refinement | These become the clearest explicit behavioral identity markers in the derived baseline. |
| `Amazing Birthday February 20, 1952` is run immediately after the refinement, without restating the specification | Demonstrated generalization | The refined behavior must carry forward to a new date rather than apply only to the first example. |
| February 20 output combines exact-date events with clearly labeled nearby context and repeatedly relates them to the person's lifetime | Demonstrated behavior | Exact-date integrity, contextual labeling, narrative synthesis, and lifetime framing are important to behavioral identity. |
| User says the result is great and asks to save the behavior so `Birthdate [some date]` will reproduce the report | Explicit acceptance and interface requirement | `Birthdate [date]` becomes the reusable primary trigger. |
| Assistant acknowledges the short trigger | Accepted interface | The application should execute without restating the full specification. |
| `Birthdate August 24, 1931` is then invoked with only the short trigger and produces a fresh report | Demonstrated trigger regression/generalization | The application must generalize to unseen dates through the short invocation rather than replay memorized examples. |
| August 24 output closes with a current-date-sensitive statement that August 24, 2026 is the person's 95th birthday | Demonstrated temporal behavior | Current-age/current-date statements must be computed at execution time rather than frozen into the preserved application. |

## Explicit requirements versus derived constraints

### Explicitly established in the conversation

- interesting and engaging birthday report;
- select roughly 5–10 standout connections;
- favor surprising, meaningful, culturally important, or personally resonant material;
- explain why each connection matters;
- weave the material into the person's lifetime;
- prefer narrative flow over chronology;
- avoid trivia dumps and exhaustive lists;
- end with a sense of the world the person entered and how it changed;
- support the reusable `Birthdate [date]` trigger.

### Derived from demonstrated behavior

The following are not quoted user requirements, but they are repeatedly present in the successful outputs and are therefore represented in the behavioral baseline as reconstruction constraints:

- distinguish exact-date events from nearby context rather than implying everything happened on the exact date;
- open by locating the person in the historical world of the birthdate;
- use multiple domains when useful, such as politics, culture, science, technology, media, transportation, or sports;
- use current-date arithmetic correctly when making present-day age or anniversary statements;
- finish with synthesis rather than a disconnected list.

These derived constraints should remain revisable if future historical evidence contradicts them. They must not be retroactively described as verbatim user requirements.

## What this map does not prove

This map does not establish that every sentence, section heading, event category, tone flourish, or output length is part of Amazing Birthday's identity. Behavioral reconstruction is intentionally judged at the level of meaningful functional behavior rather than identical prose.

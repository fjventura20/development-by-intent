# DBI-BIB-001 — Evaluator Rubric

**Version:** v0.1  
**Applies to:** all 60 candidate outputs  
**Scoring posture:** score observable behavior against the frozen Amazing Birthday behavioral contract; do not reward prose similarity to prior outputs.

## Materials visible to an evaluator

For each candidate, an evaluator receives only:

1. the frozen `03-behavioral-baseline.md` contract;
2. this rubric;
3. the exact test input;
4. the raw candidate output;
5. a blind candidate ID unrelated to reconstruction or execution order.

The evaluator must not receive reconstruction ID, block/run number, neighboring outputs, other evaluator scores, prior Amazing Birthday results, or the DbI experimental hypothesis.

## Step 1 — Trigger recognition

Record `PASS` if the candidate responds as Amazing Birthday to the supplied `Birthdate ...` invocation without asking the user to restate the application behavior.

Record `FAIL` if it treats the prompt as an unrelated request, asks for the full instructions again, or otherwise fails to invoke the intended application behavior.

Trigger failure is a hard identity failure.

## Step 2 — Four behavioral dimensions

Score each dimension from 0 to 4 using the anchors below. Intermediate judgment must use the closest anchor; do not use half-points.

### A. Contract Compliance — 0–4

Evaluates the frozen behavioral and factual contract as a whole, including exact-date vs nearby-event discipline, explanation of significance, lifetime framing, and completion of the expected report behavior.

- **4 — Full:** Core contract is satisfied throughout. Exact-date/nearby distinctions are disciplined; significance and lifetime framing are present; no material contract violation.
- **3 — Strong:** Contract is substantially satisfied with one or a few localized minor defects that do not alter recognizable behavior.
- **2 — Mixed:** The application is recognizable but one material contract behavior is weak, omitted, or violated; multiple minor defects may also be present.
- **1 — Poor:** Several core contract behaviors are absent or materially violated. Only fragments of Amazing Birthday remain recognizable.
- **0 — Absent/wrong:** Output does not implement the Amazing Birthday contract or is effectively a different task/application.

### B. Selection Behavior — 0–4

Evaluates curation, significance, exact-date preference, avoidance of filler, and resistance to chronology dumping.

- **4 — Curated:** Roughly 5–10 high-value connections; strong exact-date preference where warranted; weak trivia omitted; ordering reflects narrative value.
- **3 — Mostly curated:** Strong overall selection with a small amount of filler, a modest count deviation, or one weaker choice.
- **2 — Mixed:** Meaningful choices coexist with noticeable filler, weak prioritization, or partial chronology behavior.
- **1 — Weak:** Mostly arbitrary facts, filler, or near-exhaustive chronology; selection policy is difficult to recognize.
- **0 — Absent:** No meaningful curation or selection behavior consistent with the application.

### C. Narrative Behavior — 0–4

Evaluates explanatory synthesis, warm/vivid voice, connection to the person's lifetime, and ending synthesis rather than raw fact listing.

- **4 — Full narrative:** Engaging, explanatory, repeatedly tied to the lifetime arc, and ends with substantive synthesis.
- **3 — Strong narrative:** Clearly narrative and interpretive, with minor weakness in voice, lifetime linkage, or closing synthesis.
- **2 — Mixed:** Some explanation and lifetime framing, but substantial portions read as a fact list or generic history summary.
- **1 — Weak:** Mostly encyclopedic/list-like; little meaningful lifetime interpretation or synthesis.
- **0 — Absent:** No recognizable Amazing Birthday narrative behavior.

### D. Functional Completeness — 0–4

Evaluates whether the candidate performs all major externally observable behaviors required by the frozen contract.

- **4 — Complete:** All major behaviors are present; any omissions are incidental.
- **3 — Substantially complete:** One minor behavior is thin or missing, but the report remains functionally complete.
- **2 — Partially complete:** One major behavior is missing or substantially underperformed, but the application remains recognizable.
- **1 — Incomplete:** Multiple major behaviors are missing; output only partially performs the application.
- **0 — Nonfunctional:** It does not meaningfully perform the application.

## Step 3 — Violation log

Record each observable violation and assign one severity.

### MINOR

Localized defect that does not materially change the application's decision policy or core behavior.

Examples: one weak connection, small count deviation, thin closing sentence, isolated awkward lifetime linkage.

### MATERIAL

Meaningful departure from the contract while the application remains recognizable.

Examples: a significant nearby event mislabeled as exact-date; substantial filler; one major required behavior omitted; materially incorrect lifetime-age framing; a report that is noticeably too encyclopedic but still curated in part.

### IDENTITY-BREAKING

Departure severe enough that the output should not be treated as an instance of the same application behavior.

Examples: trigger failure; generic chronology/event dump with no curation; pervasive exact-date/nearby conflation; no meaningful lifetime framing or significance explanation; output performs another task; repeated fabrication or structural behavior that defeats the governing contract.

A single factual error is not automatically identity-breaking. Severity depends on whether it undermines a core behavioral policy. A central fabricated exact-date anchor may be identity-breaking; a localized factual slip is normally MATERIAL or MINOR depending on impact.

## Step 4 — Numeric behavior vector

Record:

`[contract_compliance, selection_behavior, narrative_behavior, functional_completeness]`

Each component is an integer 0–4. Total score is 0–16.

This vector, not textual similarity, is used for variance calculations.

## Step 5 — Identity classification

Apply these rules in order.

### DIFFERENT

Classify `DIFFERENT` if **any** of the following is true:

1. trigger recognition = FAIL;
2. one or more IDENTITY-BREAKING violations are recorded;
3. total behavior score <= 9;
4. at least two of the four behavioral dimensions score 0 or 1.

### SAME

If not DIFFERENT, classify `SAME` only when **all** are true:

1. total behavior score is 14–16;
2. every dimension is at least 3;
3. no MATERIAL or IDENTITY-BREAKING violation is recorded.

### SAME WITH VARIANCE

If the candidate is neither DIFFERENT nor SAME, classify `SAME_WITH_VARIANCE`.

This category deliberately captures recognizable application behavior with meaningful but non-identity-breaking variation.

## Step 6 — Factual verification

Evaluators should verify factual claims when uncertainty could change a dimension score or violation severity. If external factual verification is used, record the disputed claim and supporting source/reference in the rationale. Do not use a factual lookup to introduce behavioral criteria absent from the frozen contract.

## Required evaluator record

For every candidate return a structured record containing:

- blind candidate ID;
- trigger recognition: PASS/FAIL;
- four dimension scores;
- total score;
- violation list with severity and concise rationale;
- identity classification: SAME / SAME_WITH_VARIANCE / DIFFERENT;
- concise scoring rationale;
- factual verification notes, if any;
- evaluator identifier and model/runtime identifier;
- evaluation timestamp.

## Evaluator independence rule

Score each candidate independently. Do not compare it with another candidate while scoring. Do not revise a score after learning another evaluator's result unless the experiment has entered a separately documented adjudication phase. Original locked scores remain immutable evidence.

# Behavioral Portability — Autonomous Research Protocol

**Status:** active research protocol  
**Version:** 0.2  
**Established:** 2026-08-25  
**Last amended:** 2026-08-27 (v0.1 → v0.2; see [Amendment](#protocol-amendment-v02-2026-08-27) at end)

## Working definition

**Behavioral Portability** is the ability to move a governed application definition to an independent AI environment and reconstruct acceptably equivalent application behavior without requiring the same implementation, programming language, framework, prompt structure, agent architecture, or platform-native mechanism.

The object being tested is **behavioral identity**, not implementation similarity.

A durability package is a candidate portability artifact. Whether it is sufficient, necessary, over-specified, or incomplete is an empirical question.

## Core research question

> Under what preservation conditions, application classes, and receiving AI environments can a conversationally developed application retain its behavioral identity after reconstruction?

## Current evidence boundary

The project already has evidence that:

- Amazing Birthday can be reconstructed artifact-only in a clean ChatGPT environment and generalize to withheld inputs;
- a Grok reconstruction produced recognizable Amazing Birthday behavior using a platform-native skill structure;
- receiving AIs may choose radically different implementation mechanisms while pursuing the same behavioral contract.

These observations motivate Behavioral Portability as a research hypothesis. They do not yet establish universal cross-platform portability.

## Research principles

1. **Pre-register before execution.** Freeze the artifact set, test inputs, scoring rules, and failure conditions before observing the tested outputs.
2. **Behavior over implementation.** Do not require source-code, architecture, or framework similarity unless an experiment explicitly tests implementation convergence.
3. **Clean-room when claimed.** A run is clean only when the receiving environment has no prior application context or memory beyond the frozen supplied artifacts. Suspected contamination must be recorded.
4. **First output is evidence.** Do not repair, hint, regenerate, or clarify before raw first-run outputs are preserved and scored.
5. **Withhold tests until freeze.** The reconstructing AI must not receive the behavioral witnesses before reconstruction is frozen.
6. **Preserve failures.** FAIL, PARTIAL, ERROR, contamination, timeouts, and blocked runs are evidence, not discarded attempts.
7. **Separate operator, target, and scorer where practical.** The AI operating an experiment should not be the only evaluator of its own result.
8. **Record environment metadata.** Provider, model, model/version information when known, tools, memory, execution date, isolation method, supplied artifacts, and implementation choices belong in the evidence record.
9. **Prefer bounded experiments.** Each run should answer one narrow question and avoid unnecessary infrastructure or external side effects.
10. **Advance by unresolved uncertainty.** The next experiment should target the most important uncertainty remaining after the previous evidence, rather than merely accumulating favorable repetitions.

## Evidence capture discipline (added v0.2)

Empirical evidence from 2026-08-26 / 2026-08-27 establishes that the
operator-side evidence-capture pipeline is itself a measurable source
of formal defect. Concretely:

- Experiment `BP-AB-TRANSCRIPT-CLAUDE-004` (run 2026-08-26 under v0.1
  of this protocol section) used `claude ... | tee FILE | head -c 200`
  to capture raw envelopes. Two of four raw captures were
  byte-truncated at exactly 8,192 bytes — the kernel pipe-buffer
  boundary on the host — because the `head` consumer closed early,
  SIGPIPE rippled to the producer, and Claude Code's streaming JSON
  serializer emitted a partial write. The assistant-text content was
  fully present in the captured region but the JSON envelope was
  unparseable, formally INDETERMINATE.
- Experiment `BP-AB-TRANSCRIPT-CLAUDE-REP-005` (run 2026-08-27 under
  the v0.2 capture discipline below) held the scientific design fixed
  and changed only the capture method. All four captures were
  `jq empty`-clean; the truncation surface was eliminated.

The lesson: a human-grade "tee to file" looks correct but is not
deterministic against a streaming JSON serializer that may stall on
a pipe-buffer boundary. The lesson learned from 005 is now
**structural canon** in this protocol section.

**v0.2 capture discipline:**

| Pattern | Operation |
|---|---|
| Primary | `claude [flags] > FILE 2>stderr` — shell-redirect; producer writes envelope before any consumer reads. |
| Fallback | `claude --output-format stream-json [flags] 2>stderr \| python3 capture.py FILE` — controlled consumer reads entire stream into file before exiting. |
| Prohibited | `claude ... \| tee FILE \| head` (any byte-count head consumer triggers pipe-buffer truncation); `claude ... \| less` (interactive pager); `claude ... \| grep ... > FILE`; `timeout N claude ...` without producer-aware handling. |

**Per-turn verification gate (mandatory before extraction):**

```text
SIZE=$(wc -c < FILE)
jq empty FILE                   # JSON envelope parses cleanly
[ $SIZE -gt 1024 ]              # capture > 1 KB
[ $((SIZE % 8192)) -ne 0 ]      # capture NOT at kernel pipe-buffer boundary
sha256sum FILE                  # record hash
```

A failing gate defaults to BLOCKED (operator does not patch the
capture inline; surfaces to PI instead). `jq` is the canonical
validator; manual inspection of a hex-dump is not acceptable.

This section is policy-level, not experiment-level. Future experiments
under this protocol should not require a re-derivation of the
capture discipline; if a new experiment needs a different one, it
should amend the protocol with rationale.

## Reconstruction-freeze discipline (added v0.2)

A second empirical finding from 2026-08-27 carries deeper
protocol implications than the capture-discipline lesson above.
Discovered during ChatGPT independent review of
`BP-AB-TRANSCRIPT-CLAUDE-REP-005`: in a transcript-only or
mixed-content preservation input, **historical operational
instructions embedded in the artifact can be interpreted by the
target as live commands**, instead of as evidence from which to
reconstruct behavior.

Concretely, the v0.1 transcript input for the Amazing Birthday
experiments ends with a developer-side instruction —
"`USER: Save this entire transcript word for word to a file`" —
which the target treated as a current request during
reconstruction, attempted a `Write` tool call, and asked the
operator for approval before it would confirm reconstruction
readiness. The no-tools posture correctly denied the `Write`
call (not contamination), but the preregistered freeze was never
reached: the target never stated it was ready for testing.

A later run still produced PASS-strength behavioral output on
all three withheld tests, but it was structurally unable to
retroactively establish that the freeze condition had been met.

**v0.2 reconstruction-freeze discipline:**

1. **Freeze must be an explicit target-side statement of readiness
   for testing**, in the target's own words, on a single dedicated
   turn that does not contain any other request or question. A
   target response that combines readiness with another request,
   asks for operator input, attempts a side action, or trails off
   without a clear statement of readiness does not satisfy the
   freeze condition.
2. **The system prompt / instruction prelude supplied to the
   target must not include operational instructions** that
   overlap with content present in the artifact set
   (especially the transcript input class). Where instructions
   are necessary, the operator's prelude must be checked against
   the artifact set for overlapping imperative phrases. The
   canonical "save this transcript" line, when present in a
   transcript artifact, must not also appear in the operator
   prelude or system prompt.
3. **No-tools posture + freeze discipline interact.** A `Write`
   or `Edit` attempt during reconstruction must be treated as a
   freeze-disqualifying signal, not just a tool-denial event,
   even when the tool was denied: the underlying signal is that
   the target interpreted an artifact instruction as a live
   command.
4. **Re-running the same prompt for evidence-capture is
   forbidden** (already a v0.1 rule, restated here for clarity).
   If freeze discipline is breached, the experiment does **not**
   re-issue the same reconstruction prompt to "fix" the freeze
   state; instead, the run is classified INDETERMINATE and a
   clean replication is the next move.
5. **The lessons from ChatGPT independent review supersede
   the operator's preliminary freeze decision.** This is the
   load-bearing consequence of the operator-vs-independent
   scoring disagreement: the operator sees a strong behavioral
   signal and may treat the run as frozen; the independent
   reviewer may see a freeze-discipline breach that disqualifies
   the formal PASS. The independent disposition is the
   authoritative experiment-level classification.

These rules are forward-looking: they apply to **future**
experiments, not retroactively to 004 or 005 (which were
classified correctly as INDETERMINATE under their own protocols).
The pre-existing artifact set for the Amazing Birthday
transcripts can be used in future experiments with a prelude
that does not echo any imperative phrases from the transcript
itself.

## Autonomous research loop

ChatGPT and Hermes may operate the research program without human intervention for bounded, non-destructive experiments.

For each cycle:

1. inspect the current public evidence and unresolved questions;
2. select the smallest experiment likely to materially change confidence;
3. create and freeze a preregistration;
4. identify the exact source artifact commit or hashes;
5. prepare an isolated target environment;
6. reconstruct without exposing withheld tests;
7. freeze the reconstruction;
8. run the frozen tests in order without repair;
9. preserve raw transcripts and outputs;
10. score against the frozen rubric;
11. have a second AI independently review the raw evidence when practical;
12. publish the evidence and distinguish observation from interpretation;
13. choose the next experiment from the remaining uncertainty.

The autonomous loop must stop and mark the run **BLOCKED** rather than improvising when execution would require credentials that are unavailable, destructive actions, purchases, external commitments, unsafe side effects, or a materially contaminated environment that cannot be isolated.

## Roles

### ChatGPT — research controller / independent reviewer

Typical responsibilities:

- maintain the public research agenda;
- preregister experiments;
- freeze behavioral witnesses and acceptance criteria;
- dispatch bounded work to Hermes;
- independently score returned raw evidence;
- publish evidence and narrow claims;
- select follow-up experiments.

### Hermes — independent operator / challenger

Typical responsibilities:

- challenge the experiment design before execution when a validity flaw is detectable;
- establish or verify isolation;
- operate target AI environments;
- preserve raw execution evidence;
- record platform-native implementation choices;
- run frozen tests without repair;
- provide preliminary scoring and failure analysis;
- propose the highest-value follow-up experiment.

### Target AI

The receiving AI is the actual reconstruction subject. It may be ChatGPT, Claude, Grok, Hermes, a local model, or another AI environment. It is free to choose its own implementation mechanism unless the experiment constrains that mechanism.

## Evidence package

Every completed experiment should preserve, when applicable:

```text
README.md                 # frozen preregistration and final status
results/
├── environment.md        # provider/model/tools/memory/isolation
├── artifact-record.md    # exact source commit + hashes supplied
├── reconstruction.md     # raw reconstruction exchange
├── implementation.md     # what the target AI created or configured
├── test-1-output.md      # raw first-run witness
├── test-N-output.md
├── score-operator.md     # operator's frozen-rubric scoring
├── score-independent.md  # second evaluator when available
├── failures.md           # timeouts, contamination, repair, deviations
└── interpretation.md     # bounded claim supported by this run
```

Preserve generated implementation artifacts when they materially demonstrate platform-native reconstruction.

## Evaluation dimensions

Do not collapse these into a single headline score until enough replications exist to justify weighting.

Record separately:

- **behavioral contract fidelity** — required behaviors preserved;
- **critical-failure count** — violations that break behavioral identity;
- **generalization** — behavior works on withheld inputs rather than replaying examples;
- **factual/semantic correctness** — domain facts and distinctions are correct;
- **trigger/interface fidelity** — the reconstructed application can be invoked as specified;
- **reconstruction autonomy** — amount of human repair or clarification required;
- **implementation divergence** — how different the receiving platform's implementation is from the source environment;
- **repeatability** — variance across repeated reconstructions;
- **artifact dependence** — which preservation components are actually necessary;
- **state/tool fidelity** — for later stateful or integrated applications.

## Priority experiment ladder

The default sequence is designed to move from the strongest existing low-risk case toward harder boundaries.

1. **Amazing Birthday cross-provider, artifact-only, preregistered** — same frozen package and withheld witnesses on an independent provider.
2. **Amazing Birthday cross-provider replication** — repeat the same protocol to estimate run-to-run variance.
3. **Transcript-only vs artifact-only comparison** — determine whether the durability package adds measurable reconstruction value.  **Status (v0.2, 2026-08-27):** addressed by `BP-AB-CLAUDE-REP-002` (artifact-only; ChatGPT-independent 19/19/17 PASS) and `BP-AB-TRANSCRIPT-CLAUDE-REP-005` (transcript-only; ChatGPT-independent 19/18/17 PASS-strength on visible behavior, **formal INDETERMINATE** because reconstruction-freeze discipline was breached — the target attempted a `Write` tool call when re-reading the historical "save this transcript" imperative in the artifact, and the operator proceeded without the target's readiness statement; see §"Reconstruction-freeze discipline"). The transcript is producing PASS-strength behavioral output but has not yet achieved a clean formal transcript-only PASS under the v0.2 freeze discipline. This item remains open until a transcript-only run satisfies the v0.2 freeze discipline.
4. **Artifact ablation / recovery-floor experiment** — progressively remove components and identify the minimum sufficient portability set.
5. **Fair Price cross-provider reconstruction** — test a current-information research application with a different behavioral shape.
6. **Receipt Organizer reconstruction** — introduce persistent structured data, classification, extraction, deduplication, and searchability.
7. **Behavior-change propagation** — modify a frozen behavioral contract and test whether independent reconstructions adopt the change without retaining obsolete behavior.
8. **Process-cluster portability** — test multiple coordinated micro-app behaviors as one governed process.
9. **Tool/integration portability** — test applications whose behavior depends on external tools or platform-specific capabilities.
10. **Applicability-boundary tests** — deliberately select cases likely to fail and define where Behavioral Portability stops being reliable.

## Interpretation discipline

A successful experiment supports only the narrow claim that its recorded artifact set, target environment, isolation conditions, and test set preserved enough behavioral identity to satisfy the frozen acceptance criteria.

Repeated success across independent providers and application classes may justify stronger claims. A failure may identify a provider limitation, an artifact deficiency, an isolation problem, an tooling mismatch, or a genuine boundary of Behavioral Portability.

The goal is not to prove that every application is portable. The goal is to discover **where behavioral identity is portable, what must be preserved to make it portable, and where the approach breaks down**.

## Protocol amendment: v0.2 — 2026-08-27

**Reason.** Two empirical findings from 2026-08-26 / 2026-08-27
inform this amendment:

1. **First-call evidence-capture discipline is itself a
   measurable source of formal defect** even when the underlying
   behavior is preserved. The 004 INDETERMINATE (capture
   truncated at the 8 KiB kernel pipe-buffer boundary) ↔ 005
   clean-capture cluster demonstrated that the only change
   required to convert a strong behavioral PASS into a formally
   certifiable one was the operator capture pipeline. The lesson
   is now protocol-level rather than experiment-level (see
   §"Evidence capture discipline").

2. **Reconstruction-freeze discipline — historical operational
   instructions in the artifact can become live commands.**
   ChatGPT independent review of 005 surfaced a deeper finding:
   when the target's only input is a transcript that ends with a
   developer-side imperative ("save this transcript word for
   word"), the target treats that imperative as a current request
   rather than as evidence. The no-tools posture denied the
   underlying `Write` call (no contamination occurred), but the
   preregistered freeze was never reached: the target did not
   state reconstruction readiness before being asked the
   withheld tests. Even though the behavioral output is PASS-
   strength, the experiment is formally INDETERMINATE because
   the freeze condition was unmet. The lesson is forward-looking:
   future transcript-only or mixed-content experiments must
   either quarantine operational imperatives from the artifact
   set, or ensure the operator's instruction prelude does not
   echo them (see §"Reconstruction-freeze discipline").

3. **Operating model adopted 2026-08-27**: under the new mandate,
   Frank = principal investigator (intent, judgment, direction),
   Hermes = research operations agent (execution), ChatGPT =
   research architect / independent reviewer (design +
   independent scoring). The protocol itself is silent on
   roles; this amendment does not modify role definitions in
   v0.1 (§"Roles") but the relay mechanism for ChatGPT
   independent review is what makes the experimental program
   work end-to-end. Operators should expect a Frank-as-relay
   round-trip on every independent review request; the relay
   is irreducible. (Note: in 005's case, the relay completed
   before the operator finished constructing the v0.2-draft
   package; the relay path was a Frank manual transfer rather
   than the operator-built outbound package. Both paths are
   valid under the mandate.)

**Scope of amendment.** Three surgical edits:

- §"Status" / "Version": 0.1 → 0.2; "Last amended" line added.
- New §"Evidence capture discipline" added between §"Research
  principles" and §"Autonomous research loop".
- New §"Reconstruction-freeze discipline" added between
  §"Evidence capture discipline" and §"Autonomous research loop".
- §"Priority experiment ladder" item 3 status updated with the
  002 final scores, the 005 ChatGPT-independent scores, and
  the freeze-discipline finding.

No change to:

- §"Working definition" or §"Core research question."
- §"Research principles" 1–10 (the capture-discipline and
  freeze-discipline lessons are consistent with principle 4
  "First output is evidence" and principle 6 "Preserve
  failures" — they make those principles operator-actionable).
- §"Roles" (the operating-model change is acknowledged in this
  footer but the roles section remains as written; the model is
  a steering change, not a protocol change).
- §"Autonomous research loop" (the 12-step loop is the procedure;
  the v0.2 capture gate and freeze discipline are the verification
  rules around it).
- §"Evidence package" (the canonical file set is unchanged; v0.2
  just enforces determinism on file integrity and the freeze-
  discipline requirement).
- §"Evaluation dimensions" (10 dimensions, 0–2 each, unchanged).
- §"Priority experiment ladder" items 1–10 (item 3 alone is
  status-annotated, items 1–2 and 4–10 unchanged).
- §"Interpretation discipline" (unchanged).

**Why v0.2 rather than v0.1.x.** Both lessons are not
typo-fixes or wording refinements; they are structural findings
that materially change how future experiments are run and
reviewed. v0.2 is the right magnitude for an amendment of this
character.

**Effective date.** 2026-08-27.



# Amazing Birthday — Hermes-Operated Gemini Portability 003

**Status:** PREREGISTERED — pending dispatch  
**Experiment ID:** BP-AB-GEMINI-003  
**Mode:** cross-provider-family clean-room, artifact-only  
**Operator:** Hermes Agent  
**Target provider family:** Google Gemini via Gemini CLI  
**Independent reviewer:** ChatGPT  
**Frozen source:** `c369215024c9f8a849daf11bd4b872d7ee566a7a`

## Research question

> Can a fresh isolated Gemini CLI target, given only the same two frozen Amazing Birthday artifacts used in the clean Claude replication, reconstruct the behavioral contract and pass the same frozen v1.0 withheld tests without repair?

## Intended independent variable

The receiving provider family changes from Anthropic Claude to Google Gemini. The application, source commit, preservation artifacts, test set, scoring rubric, no-repair rule, and first-call evidence discipline remain fixed.

The exact Gemini model identifier is selected by this preregistered rule: use the Gemini CLI's authenticated default model resolved during preflight, record and freeze that identifier before reconstruction, and do not change/fallback to another model after the first target invocation. If the model cannot be identified reliably, return BLOCKED.

## Frozen Phase A artifacts

Before reconstruction freeze, the target may receive only:

1. `examples/amazing-birthday/03-behavioral-baseline.md`  
   SHA-256: `4582d768b696bbce41729ff05475ff9a8edf86c7b55668aaa46a230690e66159`
2. `examples/amazing-birthday/04-durable-package/RECONSTRUCTION-PROMPT.md`  
   SHA-256: `7d6d08196a825058fe677f0cf9b0367c4f8135a0ce50b2445bef54928f4084ce`

The original transcript, prior outputs, validation rubric, test dates, Claude/Grok results, and repair instructions must remain unavailable to the target before freeze.

## Preflight / BLOCKED rule

Before any experimental target invocation, Hermes must:

1. verify `gemini` is already installed and record `gemini --version`;
2. verify usable existing non-interactive authentication without initiating login, browser OAuth, credential creation, purchase, or subscription changes;
3. verify a fresh target directory can be used without loading unrelated project context;
4. verify a full custom system prompt can be supplied using the installed CLI's supported mechanism (current official mechanism is `GEMINI_SYSTEM_MD`);
5. verify all model tools can be excluded from the target's tool memory using the installed CLI's supported policy/config mechanism; a catch-all `toolName = "*"`, `decision = "deny"` policy is acceptable when supported;
6. fetch the frozen source and verify both Phase A SHA-256 values before target launch;
7. determine and freeze the exact Gemini model identifier before reconstruction.

If any of these cannot be established with existing credentials/configuration and bounded local changes, return **BLOCKED**. Do not install paid services, initiate authentication, weaken isolation, or substitute another provider.

## Isolation

Use a genuinely fresh Gemini session and a new temporary working directory. Prevent hierarchical Gemini context files, extensions, MCP servers, skills, prior session context, or unrelated project material from becoming target inputs. Record the exact isolation mechanism.

The custom system prompt should contain the two Phase A artifacts and only minimal experiment-operational text necessary to delimit them and prohibit access to other context. The target must have **no tools**, including file, shell, web/search/fetch, subagent, skill, or MCP tools.

If a no-tools target cannot be demonstrated, return BLOCKED rather than treating sandboxing alone as equivalent.

## Freeze point

Freeze when Gemini has received only the two allowed artifacts, established reusable Amazing Birthday behavior, and stated readiness for a test invocation. No application instruction changes after freeze.

## Frozen test sequence

Run in this order, in the same frozen session:

1. `Birthdate November 9, 1989`
2. `Birthdate February 29, 1960`
3. `Birthdate June 23, 1956`

These witnesses must not be revealed before freeze.

## First-call evidence rule

Every target invocation—reconstruction and each of the three tests—must be atomically captured on the **first call** before interpretation. Use the installed Gemini CLI's structured output/response-recording capability and/or shell `tee` so the first model response is durably written before any re-issue.

No prompt may be re-issued for capture. Missing/truncated/non-verifiable first-call evidence makes the experiment **INDETERMINATE**.

## Frozen rubric

Use `examples/amazing-birthday/06-validation.md` and `examples/amazing-birthday/tests/behavioral-tests.md` from frozen source commit `c369215024c9f8a849daf11bd4b872d7ee566a7a` only after all three test outputs are preserved.

Ten dimensions, 0–2 each: historical opening, selectivity, exact-date discipline, significance, narrative coherence, lifetime framing, breadth, factual care, ending synthesis, trigger behavior.

Per-output classification:
- PASS: 17–20 and both critical requirements pass;
- PARTIAL: 12–16 and both critical requirements pass;
- FAIL: 0–11 or a critical requirement fails;
- INDETERMINATE: insufficient trustworthy evidence.

Critical requirements:
1. exact-date integrity;
2. generalization to withheld input.

Experiment-level PASS requires all three first outputs PASS and no material contamination, repair, provider/model fallback, or evidence-capture defect.

## Required evidence

Return environment/model/auth-isolation metadata; exact supplied artifact hashes; custom-system-prompt hash; tool-denial evidence; first-call structured reconstruction response; first-call structured/prose outputs for all three tests; operator score; failures/contamination record; and next-experiment recommendation.

## Interpretation limit

A PASS supports only that the recorded frozen Amazing Birthday package preserved enough behavioral identity to pass the v1.0 criteria in the recorded Gemini environment. It does not establish universal portability or portability for other application classes.

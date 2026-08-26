# Amazing Birthday — Hermes-Operated Gemini Portability 003

**Status:** BLOCKED at preregistered preflight — no Gemini target invocation  
**Experiment ID:** BP-AB-GEMINI-003  
**Mode:** cross-provider-family clean-room, artifact-only  
**Operator:** Hermes Agent  
**Target provider family:** Google Gemini via Gemini CLI  
**Independent reviewer:** ChatGPT  
**Frozen source:** `c369215024c9f8a849daf11bd4b872d7ee566a7a`

## Final disposition

The original transfer `20260826T023700Z-behavioral-portability-gemini-003` was rejected by the exchange before Hermes/Gemini execution because its protocol-v0.2 manifest omitted the required top-level `files` inventory. That transport failure remains preserved and is not treated as behavioral evidence.

A transport-only retry was preregistered as `20260826T123000Z-behavioral-portability-gemini-003-retry-001`, changing only the exchange packaging while keeping the scientific protocol frozen.

The retry reached Hermes and completed preflight at `2026-08-26T19:02:25Z`. It is formally **BLOCKED** under the preregistered gate because no Gemini CLI binary is installed on the Hermes host. Hermes verified the frozen payload hashes, but the absence of the CLI prevented demonstration of existing non-interactive authentication, fresh Gemini context isolation, `GEMINI_SYSTEM_MD` system-prompt override, catch-all no-tools policy, and exact model-identifier freeze.

No Gemini model was invoked. No reconstruction or withheld test prompt reached a target. No first-call behavioral evidence exists and no rubric score is assigned. This is therefore a prerequisite/environment blocker, not PASS/PARTIAL/FAIL/INDETERMINATE behavioral evidence.

Hermes also reported that OAuth credential material exists on disk, but the experiment rules prohibit initiating login, installing a missing prerequisite, creating a key, purchasing/changing a subscription, weakening isolation, or substituting Hermes' built-in Gemini adapter. The run correctly stopped rather than improvising.

Raw bridge evidence is preserved in `raw/preflight-blocked-result.json`. The bridge wrapper itself misclassified the returned result as `ERROR / MISSING_TASK_DISPOSITION` because it failed to parse the human-readable `DISPOSITION: BLOCKED`; the substantive Hermes preflight record is unambiguous and governs the experiment interpretation.

## Transport result — original dispatch

Original transfer `20260826T023700Z-behavioral-portability-gemini-003` was rejected by the exchange at `2026-08-26T11:43:21Z` before Hermes or Gemini executed the experimental procedure.

The rejection was:

> `Inbound package rejected: manifest missing required field: files`

The outbound manifest identified protocol v0.2 and the frozen experimental metadata but omitted the exchange-required top-level `files` inventory. This is an **infrastructure/protocol packaging failure**, not a Gemini behavioral result. No Gemini target call occurred, no first-call behavioral evidence exists, and no rubric score is assigned.

Raw rejection evidence is preserved in `raw/transport-rejection-result.json` and `raw/transport-rejection-manifest.json`.

The transport-only retry is preregistered in `RETRY-001.md`. It changed only the exchange manifest packaging by adding the required file inventory/hashes; all scientific variables and failure rules below remained frozen.

## Research question

> Can a fresh isolated Gemini CLI target, given only the same two frozen Amazing Birthday artifacts used in the clean Claude replication, reconstruct the behavioral contract and pass the same frozen v1.0 withheld tests without repair?

This question remains unresolved because the required target runtime was unavailable.

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
4. verify a full custom system prompt can be supplied using the installed CLI's supported mechanism (`GEMINI_SYSTEM_MD`);
5. verify all model tools can be excluded from the target's tool memory using the installed CLI's supported policy/config mechanism; a catch-all `toolName = "*"`, `decision = "deny"` policy is acceptable when supported;
6. fetch the frozen source and verify both Phase A SHA-256 values before target launch;
7. determine and freeze the exact Gemini model identifier before reconstruction.

If any of these cannot be established with existing credentials/configuration and bounded local changes, return **BLOCKED**. Do not install paid services, initiate authentication, weaken isolation, or substitute another provider.

### Observed preflight

| Step | Result |
|---|---|
| Gemini CLI installed | **FAIL** — no `gemini` binary available |
| Existing authentication exercised end-to-end | cascade-blocked |
| Fresh isolated target context | cascade-blocked |
| Full system-prompt override | cascade-blocked |
| Global no-tools target | cascade-blocked |
| Frozen source / Phase A hashes | **PASS** |
| Exact model identifier freeze | cascade-blocked |

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

Every target invocation—reconstruction and each of the three tests—must be atomically captured on the **first call** before interpretation. No prompt may be re-issued for capture. Missing/truncated/non-verifiable first-call evidence makes the experiment **INDETERMINATE**.

Because preflight blocked before target invocation, this rule was never entered and no synthetic or re-issued output is substituted.

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

## Interpretation limit

This BLOCKED result says nothing about Gemini's ability to reproduce Amazing Birthday behavior. It establishes only that the preregistered Gemini arm could not be executed on the recorded Hermes host without adding a missing runtime prerequisite, which the protocol explicitly forbade.

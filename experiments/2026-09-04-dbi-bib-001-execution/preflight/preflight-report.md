# DBI-BIB-001 Pre-flight Report

**Experiment:** DBI-BIB-001 — DbI Behavioral Identity Baseline Experiment v0.1
**Inbound:** `20260904T175118Z-dbi-bib-001-preflight-001`
**Outbound response:** `20260904T175118Z-dbi-bib-001-preflight-001-response-001`
**Preflight date:** 2026-09-04
**Operator:** Hermes Agent (under DBI Research Manager mandate adopted 2026-08-27)
**Disposition:** **PREFLIGHT_BLOCKED** — blocking gate §F (two eligible independent evaluators)

---

## 1. Scope of preflight (what was authorized and what was not)

Per the inbound `instructions.md`:

> Harmless disposable runtime/capture smoke tests that contain no Amazing Birthday source, trigger, test prompt, or experiment content are permitted when necessary to establish preflight readiness.

What I executed:

- Hash verification of all frozen artifacts (`§A`) — read-only, no model invocation
- Capture discipline smoke calls (`§C` and `§D`) using the harmless probe `Reply with one sentence only.` — content-free, no DBI-BIB-001 content, total cost $0.0025 USD
- Evaluator availability audit (`§F`) including a single non-content Codex invocation attempt that did not complete

What I did NOT execute:

- I did NOT send the frozen reconstruction input (`reconstruction-input.txt`) to the reconstruction engine.
- I did NOT send any DBI-BIB-001 test prompt (T1–T5) to any engine.
- I did NOT invoke the reconstruction engine on any Amazing Birthday content.
- I did NOT generate any DBI-BIB-001 behavioral observation.
- I did NOT modify any frozen artifact under any freeze commit.

Verification: `git status` on the DBI repo shows 4 untracked entries, all pre-existing drafts (`REPORTS/`, `experiments/2026-08-27-amazing-birthday-ablation-001/`, my superseded variance-calibration draft, my Meal Journal retrospective proposal). Zero modifications to any tracked file.

---

## 2. Gate-by-gate findings

### §A — Frozen artifact integrity — **PASS**

| Check | Claimed | Actual | Result |
|---|---|---|---|
| Protocol repo reachable | `fjventura20/development-by-intent` | reachable | PASS |
| Protocol commit exists | `b9b6c86c017903cca061b4c2f7b798c82870f9c5` | exists, is parent of `origin/main` HEAD `ebbb4319` | PASS |
| Protocol blob SHA-1 | `1d06f02a9d331df279ee4417e23b4d52330b63f9` | `1d06f02a9d331df279ee4417e23b4d52330b63f9` | PASS |
| Exec-pkg snapshot commit | `00676a3343fbf786e3b72b32afcc6e5071582cb8` | `00676a3343fbf786e3b72b32afcc6e5071582cb8` (reachable; ancestor of `origin/main` HEAD) | PASS |
| Exec-pkg file blob SHAs | 7 files, exact blob SHAs listed in `frozen-package-lock.json` | all 7 match at `00676a33` | PASS |
| Source commit | `c369215024c9f8a849daf11bd4b872d7ee566a7a` | reachable | PASS |
| `03-behavioral-baseline.md` SHA-256 | `4582d768…1e66159` | `4582d768…1e66159` | PASS |
| `04-durable-package/RECONSTRUCTION-PROMPT.md` SHA-256 | `7d6d0819…284ce` | `7d6d0819…284ce` | PASS |
| Test prompt T1 SHA-256 | `75302f1f…65598b` | `75302f1f…65598b` | PASS |
| Test prompt T2 SHA-256 | `58170a11…44712` | `58170a11…44712` | PASS |
| Test prompt T3 SHA-256 | `52fb3fa1…7dca8` | `52fb3fa1…7dca8` | PASS |
| Test prompt T4 SHA-256 | `a8ad9dcb…cf7fe` | `a8ad9dcb…cf7fe` | PASS |
| Test prompt T5 SHA-256 | `c1786d3a…29b44` | `c1786d3a…29b44` | PASS |
| Frozen artifacts modified during preflight | (none expected) | (none observed) | PASS |

### §B — Reconstruction runtime — **PASS**

- CLI binary present: `/home/fjventura20/.hermes/node/bin/claude` (version `2.1.170 (Claude Code)`)
- Flags present: `--model`, `--allowedTools`, `--tools`, `--disallowedTools`, `--resume`
- Model `claude-sonnet-4-6` addressable: `--model claude-sonnet-4-6` honored on smoke call (response was generated; modelUsage field lists `claude-sonnet-4-6`)
- Auth posture: `ANTHROPIC_API_KEY` not set in environment; CLI uses Claude Code OAuth session (provider default, non-secret posture recordable)
- Runtime version pinned at smoke time: `2.1.170`

### §C — Isolation and no-tools posture — **PASS**

Smoke call (`Reply with one sentence only.`) with `claude --model claude-sonnet-4-6 --allowedTools '' --tools '' --disallowedTools 'WebFetch,WebSearch'`:

- Fresh session: `session_id = ce261cc5-7c9d-45b4-bc93-a537b94da5c1`, `num_turns = 1`
- No-tools posture effective: response was a single sentence (`How can I help you today?`) with no `tool_use` content blocks in the JSON envelope
- No prior Amazing Birthday context: response carries zero Amazing Birthday signal; the model treats the probe as a fresh user greeting

**Operational observation (DEV-001):** the response's `modelUsage` field lists two models — `claude-haiku-4-5-20251001` AND `claude-sonnet-4-6`. The `--model` flag was honored; the response was generated under that pinning; the dual-listing is a metadata behavior of Claude Code 2.1.170, not a model-substitution event. Recorded as MINOR deviation. Not a blocker; surfaced for Frank's awareness.

### §D — Capture system — **PASS**

Two capture patterns verified on the smoke call:

- **Primary** (shell redirect): `claude [flags] > RAW_FILE 2> STDERR_FILE` — captured 26 bytes cleanly
- **Fallback** (`--output-format json`): captured 1430-byte envelope with parseable JSON, `result_subtype: success`, `total_cost_usd: 0.0024819`, `session_id`, `num_turns`

Both captures produced byte-stable files with SHA-256 digests recorded. No `tee | head`, `grep > file`, `less`, or other truncation-prone pipelines were used.

**Capture files in evidence directory:**

| File | SHA-256 | Size |
|---|---|---|
| `runs/smoke-preflight/smoke-1a-direct.stdout.txt` | `12fef572…d81ed27` | 26 B |
| `runs/smoke-preflight/smoke-1b-json.stdout.txt` | `93634d21…5875bb3f` | 1430 B |
| `runs/smoke-preflight/smoke-1a-direct.stderr.txt` | `e705bbf8…3d067e0` | 0 B |
| `runs/smoke-preflight/smoke-1b-json.stderr.txt` | `e705bbf8…3d067e0` | 0 B |

Total smoke cost: **$0.0025 USD**.

### §E — Manifest and evidence implementation — **PASS**

- Skeleton manifest validated against `MANIFEST.schema.json`: **PASS** with 24 preflight-expected omissions (each `reconstructions[].outputs[]` is empty by design for a preflight skeleton). Zero unexpected schema errors.
- `reconstruction-input.txt` assembled from frozen bytes at `c3692150` with neutral file-boundary wrappers per SOURCE-PACKAGE.md. **5362 bytes, SHA-256 = `fb069bf6…de63f47b`. NOT sent to any engine.**
- Test corpus file prepared with all 5 prompts and their verified SHA-256s.
- Evidence directory laid out per OPERATOR-INSTRUCTIONS.md §10: `inputs/`, `runs/`, `blinding/`, `evaluation/`, `analysis/`, `hashes/`.
- Global SHA256SUMS file written over 10 evidence artifacts.
- Disk space: 21 GB free (more than sufficient).
- Deviation logging approach: schema-validated `deviations[]` array in `MANIFEST.json` with severity, timestamp, affected artifacts, and disposition (per OPERATOR-INSTRUCTIONS.md §9).

### §F — Evaluator availability and independence — **BLOCKED**

#### Evaluator A candidate: Codex (codex-cli 0.146.0)

- Provider family: OpenAI — distinct from Anthropic (reconstruction engine) and from Claude ✓
- Distinct model family ✓
- Not the reconstruction engine ✓
- Not Hermes ✓
- Not involved in DBI-BIB-001 protocol design (the protocol was authored by ChatGPT and frozen on `fjventura20/development-by-intent`; Codex is OpenAI's CLI and ChatGPT is OpenAI's web product — but the *auth credential* is shared)
- **`codex login status` reports `Logged in using ChatGPT`** — this is a real §F ambiguity

**Adjudication needed:** the protocol §F reads "neither evaluator may be ChatGPT." Strict reading: Codex as a runtime identity is OpenAI's CLI, but if its auth uses ChatGPT, do its outputs count as "ChatGPT outputs"? I cannot adjudicate this without Frank.

**Codex availability note (DEV-002):** `codex exec` invocation did not complete cleanly in this sandbox — one timeout at 120s with no stdout, one immediate exit on git-repo-trust check. The CLI binary is logged in and functional for interactive use, but the non-interactive `exec` pattern needs refinement before evaluator calls are reliable. This is **not a §F eligibility blocker**; it's a separate operational note for when (if) Codex is selected.

#### Evaluator B: **NONE AVAILABLE**

| Available CLI on host | Status |
|---|---|
| `claude` (Claude Code 2.1.170) | DISQUALIFIED — reconstruction engine |
| `codex` (codex-cli 0.146.0) | Potential Evaluator A (pending ChatGPT-OAuth adjudication) |
| `gemini` | NOT FOUND |
| `gpt` | NOT FOUND |
| `grok` | NOT FOUND |
| `llama-cli` | NOT FOUND |
| `mistral` | NOT FOUND |
| `opencode` | NOT FOUND |

API keys for non-Anthropic providers: **none configured** (`OPENAI_API_KEY`, `GOOGLE_API_KEY`, `GEMINI_API_KEY`, `GROK_API_KEY`, `XAI_API_KEY`, `MISTRAL_API_KEY` all unset).

Remote evaluator bridge to a different host: **not configured.**

**§F explicit failure mode is triggered:** "If two eligible independent evaluators cannot be established, pre-GO readiness FAILS."

---

## 3. Unblock paths for §F (Frank's call)

I see three. Each requires Frank's external action:

**Path A — Frank provides a non-OpenAI API key.** A `GEMINI_API_KEY`, `GROK_API_KEY`, or `MISTRAL_API_KEY` would let Hermes install the corresponding provider CLI and demonstrate Evaluator B availability in the next preflight. This is the cleanest fix — it preserves the §F independence rule verbatim.

**Path B — Frank designates a Frank-controlled remote evaluator instance.** Frank stands up a remote evaluator (Gemini, Grok, or other) on a machine he controls, gives Hermes an invocation protocol, and §F passes because the evaluator is genuinely independent of this host.

**Path C — Protocol amendment.** Frank accepts a v0.2 amendment reducing the evaluator count from 2 to 1, OR replacing one of the two evaluators with a different independence criterion (e.g., "two distinct sessions of the same model with no cross-pollination"). This requires a new protocol version and a new freeze, and ChatGPT-as-protocol-designer has to sign off. Significantly slower path.

I recommend Path A if Frank has a key available; Path B if Frank wants Evaluator B to be in a controlled environment; Path C only if Paths A and B are both blocked.

---

## 4. Deviations recorded

| ID | Severity | Description | Disposition |
|---|---|---|---|
| DEV-001 | MINOR | `modelUsage` metadata reports two models on smoke call; `--model claude-sonnet-4-6` honored, response generated under pinning | Recorded; surfaced for Frank's awareness; not a blocker |
| DEV-002 | MATERIAL | Codex `codex exec` invocation pattern did not complete cleanly in this sandbox (one 120s timeout, one immediate exit on git-repo-trust check) | Recorded; not a §F eligibility blocker; needs refinement before evaluator calls; surfaced for Frank's awareness |

No `INVALIDATING` deviations.

---

## 5. Honest observations beyond the preflight scope

1. **The ChatGPT-authored DBI-BIB-001 frozen protocol is more rigorous than my draft calibration protocol.** Two-evaluator independence, within+between variance design (30 + 150 Manhattan distances per evaluator), pre-registered agreement gates (≥90% identity-preservation agreement, ≤1.0 mean absolute dimension difference), prospective-from-baseline threshold rule (PROTOCOL §14), explicit role separation (§15) — these are the right controls. My draft at `experiments/2026-09-04-amazing-birthday-reconstruction-variance-calibration-001/` is now superseded by DBI-BIB-001; I will add a NOTE pointing at DBI-BIB-001 and do not propose executing the draft.

2. **Two design differences between my draft and DBI-BIB-001 are worth noting:**
   - DBI-BIB-001 uses **5 test prompts × 2 blocks × 6 reconstructions = 60 outputs** (vs. my draft's 8 reconstructions × 3 dates × 4 turns = 32 invocations). DBI-BIB-001 has substantially more statistical power for the within/between variance comparison.
   - DBI-BIB-001's source package is the **2-file artifact-only stack** (behavioral-baseline + reconstruction-prompt), not the 3-file artifact+transcript stack my draft used. The 2-file stack matches the clean-room-001 successful ChatGPT replication; my 3-file stack matches the transcript-only-006 Claude replication. ChatGPT's choice is more conservative for a baseline (smaller specification surface = cleaner variance signal).

3. **The Meal Journal retrospective evidence freeze proposal is independent of DBI-BIB-001 and remains a separate decision item.** Per Frank's earlier directive, Meal Journal is reconstruction-fidelity evidence, not evolvability evidence. No new framing here.

---

## 6. Disposition

**PREFLIGHT_BLOCKED.**

The blocking gate is §F: two eligible independent evaluators cannot be established on this host with the runtime inventory currently available. Codex CLI is potentially eligible as Evaluator A subject to Frank's adjudication of the "Logged in using ChatGPT" auth posture; Evaluator B has no available runtime path without Frank's external action (one of Paths A/B/C in §3 above).

Gates §A, §B, §C, §D, §E all PASS. The technical preflight is otherwise ready — the only failure is the evaluator-availability gate, which by §F's explicit text is a hard preflight-block condition.

**No execution authorized.** Awaiting Frank's §F adjudication and unblock direction. Once §F clears, a separate explicit execution GO transfer will move this from `PREPARED` to `EXECUTED_AWAITING_EVALUATION`. Until then, valid disposition remains `PREPARED — NOT AUTHORIZED FOR EXECUTION`.

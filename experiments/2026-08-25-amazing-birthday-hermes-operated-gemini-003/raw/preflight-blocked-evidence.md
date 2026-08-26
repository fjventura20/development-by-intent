# Raw Preflight Blocker Evidence — Gemini 003 Retry 001

**Transfer:** `20260826T123000Z-behavioral-portability-gemini-003-retry-001`  
**Hermes execution window:** 2026-08-26T19:00:08Z–19:02:25Z  
**Substantive disposition:** `BLOCKED`  
**Gemini target invoked:** No

The Hermes result reported that the protocol reached preflight and stopped before any Gemini target call because the required Gemini CLI runtime was not present on the host.

| Preflight step | Observed status | Evidence / reason |
|---|---|---|
| 1. Gemini CLI installed | **FAIL** | No `gemini` binary on `$PATH`; no `~/.local/bin/gemini`; no global npm Gemini CLI; no cached pipx/uvx Gemini CLI. Hermes' `gemini_native_adapter.py` is an inline HTTPS adapter and was not accepted as equivalent to the preregistered CLI target. |
| 2. Existing non-interactive authentication exercised end-to-end | **cascade-blocked** | Existing OAuth credential material was reported on disk, but without a Gemini CLI binary it could not be exercised through the preregistered target path. No login, OAuth flow, key creation, or billing action was initiated. |
| 3. Fresh isolated cwd / context suppression | **cascade-blocked** | Requires the target CLI. |
| 4. `GEMINI_SYSTEM_MD` full system-prompt override | **cascade-blocked** | Requires the target CLI. |
| 5. Catch-all no-tools target | **cascade-blocked** | Requires the target CLI. |
| 6. Frozen source / Phase A hashes | **PASS** | `03-behavioral-baseline.md` matched `4582d768…e66159`; `RECONSTRUCTION-PROMPT.md` matched `7d6d0819…f084ce`. Hermes reported all six payload SHA-256 values matched their manifest entries. |
| 7. Exact model identifier freeze | **cascade-blocked** | Requires the target CLI. |

No Phase A artifact or withheld test was exposed to a Gemini model. No reconstruction output exists. No first-call evidence exists. No rubric scoring is applicable.

The bridge wrapper separately returned `ERROR / MISSING_TASK_DISPOSITION` because it did not parse the human-readable `DISPOSITION: BLOCKED`. That parser status is preserved in `preflight-blocked-result.json`; it is transport metadata, not the scientific disposition.

No contaminated run or alternate Gemini adapter was substituted for the blocked clean-room experiment.

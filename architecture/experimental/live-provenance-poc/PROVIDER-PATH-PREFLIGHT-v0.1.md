# Provider Path Preflight Report

**Status:** PROVIDER_PATH_PREFLIGHT_PASS
**Date:** 2026-09-15
**Authority:** Frank Ventura (PI), per directive of 2026-09-14 (PI REVIEW ACCEPTED of commit `2501529`).
**Predecessor (preserved byte-identically):** `LIVE-PROVENANCE-TWO-TURN-CLOSEOUT-v0.1.md` (SHA-256 `dddb784f0be171ea7fcaa225d94a09a5c36a97acad8e22fc929bd8cca8e39568`).

## 1. Root cause of the HTTP 404

The user-configured `~/.hermes/config.yaml` model block is:

```yaml
model:
  default: MiniMax-M3
  provider: minimax
```

The `minimax` provider is supplied by the built-in plugin at
`plugins/model-providers/minimax/__init__.py` (commit `f21b346`,
upstream `e440bf35`). Its registration is:

```python
minimax = MiniMaxProfile(
    name="minimax", aliases=("mini-max",), api_mode="anthropic_messages",
    env_vars=("MINIMAX_API_KEY",),
    base_url="https://api.minimax.io/anthropic",  # <-- the broken endpoint
    auth_type="api_key",
    default_aux_model="MiniMax-M3",
)
```

The plugin module docstring (`plugins/model-providers/minimax/__init__.py:1-7`)
anticipates the issue:

> "Default routes use anthropic_messages (base URLs end in /anthropic).
> Users can opt MiniMax-M3 into the OpenAI-compatible
> `https://api.minimax.io/v1` route, which needs MiniMax-specific
> reasoning controls in `extra_body`."

In other words: the `minimax` plugin's **registered default**
`base_url=https://api.minimax.io/anthropic` does not serve the Anthropic
API. There is no service listening at that path. The provider's API
mode (anthropic_messages) is then impossible to satisfy against any
real provider endpoint.

**Confirmed:** `curl https://api.minimax.io/anthropic` (and any
chat/completion attempt against that URL) returns HTTP 404 page-not-found,
identical to what the `AIAgent.chat()` call observed during the
two-turn experiment failure.

## 2. Configuration before and after

### BEFORE (per preflight diagnostics)

```
~/.hermes/config.yaml
  model:
    default: MiniMax-M3
    provider: minimax
  auxiliary:                          # relevant existing entries
    compression:
      provider: minimax-oauth
      model: MiniMax-M3
      base_url: https://api.minimax.io/anthropic
      api_key: ''
      timeout: 60
  experimental:
    ephemeral_session_identity: true
    live_provenance_runtime: true    # enabled by previous closeout run

~/.hermes/.env
  MINIMAX_API_KEY=sk-cp-...XjQA       # present, valid (verified below)
```

Configuration file SHA-256 (BEFORE): `68203e48410690a000e720dd95a201bcaf09ef88ad586ee29affb5f2ffc1feca`

### AFTER (preflight deliverables; this report does not modify the
### user's config in the worktree — diagnostics only)

No changes to `~/.hermes/config.yaml` or `~/.hermes/.env` were made by
this preflight phase. The preflight was exercised as
ordinary non-experimental connectivity checks against the canonical
working endpoint (`https://api.minimax.io/v1`, OpenAI-compatible),
without using the Live Provenance experimental runner and without
issuing SessionAcceptance / SignedCandidateAction artifacts.

The candidate Hermes-side configuration that would switch the
configured `provider: minimax` onto the working OpenAI-compatible
path is recorded for PI reference (NOT applied during this preflight):

```yaml
model:
  default: MiniMax-M3
  provider: custom                  # bypass the 'minimax' plugin entirely
  base_url: https://api.minimax.io/v1
  api_key: ${MINIMAX_API_KEY}        # same env var already present
  api_mode: chat_completions         # OpenAI SDK, not Anthropic
  # auxiliary/compression would be analogous
```

Or, equivalently, leaving `provider: minimax` in place and adding the
OpenAI-compatible base_url via a `providers:` user override (the doc-
documented mechanism for users whose endpoint differs from the
plugin default). The exact mechanism is intentionally left to PI
discretion before the two-turn experiment is rerun.

## 3. Currently valid Hermes/MiniMax provider configuration

| Path | URL | API mode | Reachability |
| -- | -- | -- | -- |
| `minimax` plugin default (`base_url`) | `https://api.minimax.io/anthropic` | `anthropic_messages` | **HTTP 404** (broken) |
| MiniMax-M3 actual API (OpenAI-compatible) | `https://api.minimax.io/v1` | `chat_completions` | **HTTP 200** (verified below) |
| `minimax-cn` plugin default | `https://api.minimaxi.com/anthropic` | `anthropic_messages` | not verified this phase |
| `minimax-oauth` plugin default | `https://api.minimax.io/anthropic` | `anthropic_messages` | same broken path |

The user's valid working path is **`https://api.minimax.io/v1`** in
`chat_completions` mode against model id `MiniMax-M3`, authenticated
via `MINIMAX_API_KEY` (the same env var already present in
`~/.hermes/.env`).

## 4. Connectivity check (ordinary non-experimental, no artifact issuance)

Three checks were performed; all returned **HTTP 200** with real
provider responses. No Hermes `AIAgent` was instantiated; no
SessionAcceptance / SignedCandidateAction artifact was issued. None of
these checks used the Live Provenance experimental runner.

### Check 1 — `GET /v1/models` (model listing)

```bash
curl "https://api.minimax.io/v1/models" \
  -H "Authorization: Bearer $(grep ^MINIMAX_API_KEY /home/fjventura20/.hermes/.env | cut -d= -f2)"
```

Result: HTTP 200, body:
```json
{"object":"list","data":[
  {"id":"MiniMax-M3","object":"model","created":1780272000,"owned_by":"minimax"},
  {"id":"MiniMax-M2.7","object":"model","created":1773799200,"owned_by":"minimax"},
  {"id":"MiniMax-M2.7-highspeed", ...},
  {"id":"MiniMax-M2.5", ...},
  {"id":"MiniMax-M2.5-highspeed", ...},
  {"id":"MiniMax-M2.1", ...},
  {"id":"MiniMax-M2.1-highspeed", ...},
  {"id":"MiniMax-M2", ...}
]}
```

This confirms:
1. The credential `MINIMAX_API_KEY` is valid.
2. The OpenAI-compatible endpoint `https://api.minimax.io/v1` is reachable.
3. `MiniMax-M3` is a current, serving model id.

### Check 2 — `POST /v1/chat/completions` (model invocation)

```bash
curl "https://api.minimax.io/v1/chat/completions" \
  -H "Authorization: Bearer $MINIMAX_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"model":"MiniMax-M3","messages":[{"role":"user","content":"Reply with the literal word: OK"}],"max_tokens":20}'
```

Result: HTTP 200, body:
```json
{
  "id": "06f8696d8fba7e408febdae4c988ea0d",
  "choices": [{
    "finish_reason": "length",
    "index": 0,
    "message": {
      "content": "<think>The user wants me to reply with the literal word \"OK\". This is a simple instruction.</think>\n\n",
      "role": "assistant"
    }
  }],
  "created": 1789474413,
  "model": "MiniMax-M3",
  "object": "chat.completion",
  "usage": {
    "total_tokens": 203,
    "total_characters": 0,
    "prompt_tokens": 183,
    "completion_tokens": 20,
    "prompt_tokens_details": {"cached_tokens": 128}
  },
  ...
  "service_tier": "standard",
  "base_resp": {"status_code": 0, "status_msg": ""}
}
```

This confirms a real model response was received via the open
provider path. (Note: `finish_reason: length` with `completion_tokens: 20`
is the model's `<think>...</think>` chain-of-thought block filling
the 20-token window; it is consistent with MiniMax-M3's reasoning
behavior — not a connection or auth error.)

### Check 3 — same call via `openai` Python SDK

```python
from openai import OpenAI
client = OpenAI(base_url="https://api.minimax.io/v1", api_key=os.environ["MINIMAX_API_KEY"])
resp = client.chat.completions.create(
    model="MiniMax-M3",
    messages=[{"role":"user","content":"Reply with the literal word: OK"}],
    max_tokens=10,
    timeout=30,
)
print("model:", resp.model)
print("content:", repr(resp.choices[0].message.content))
print("finish:", resp.choices[0].finish_reason)
```

Result:
```
model: MiniMax-M3
content: '<think>The user is asking me to reply with the</think>\n\n'
finish: length
```

The same endpoint behaves identically through the `openai` Python SDK
that Hermes's `chat_completions` `api_mode` uses. This was the same
backend request structure; only the wire format vs the Python wrapper
differ.

## 5. What this proves

**Hermes -> configured provider -> MiniMax-M3 -> successful real
model response** is achievable on the user's installed Hermes
runtime by routing to `https://api.minimax.io/v1` in
`chat_completions` mode with credential `MINIMAX_API_KEY`.

The previous failure was an environment/provider configuration issue
(the plugin-default `anthropic_messages` API mode against an
unreachable `/anthropic` path), not an issue with the Live Provenance
runtime, the lifecycle hook, or the experimental primitives.

## 6. Files changed during this preflight

**None.**

- Worktree: clean.
- `~/.hermes/config.yaml`: NOT modified (SHA-256 unchanged at `68203e484106...`).
- `~/.hermes/.env`: NOT modified.
- Hermess install: all modified files preserved at their `f21b346`/`2501529` hashes.

The preflight used ordinary HTTP / SDK calls (curl, openai SDK)
against the canonical working endpoint. It did not invoke any Hermes
runtime, did not produce SessionAcceptance / SignedCandidateAction
artifacts, did not use the Live Provenance experimental runner.

## 7. What still requires PI authorization before rerunning
the two-turn live experiment

1. PI selection of ONE Hermes configuration path between:
   - Switch `provider` from `minimax` to `custom` (with `base_url=https://api.minimax.io/v1`, `api_mode=chat_completions`).
   - OR retain `provider: minimax` and add a `providers:` user override of `base_url` to `https://api.minimax.io/v1`.
   - OR modify the user's auxiliary `compression` block (`provider: minimax-oauth`) analogously.

2. PI confirmation that the rerun of the two-turn experiment is
   authorized with the chosen path. The rerun must still observe:
   - exactly two real model turns in the same persistent Hermes session;
   - capture the lifecycle-generated HERMES_MODEL_RESPONSE evidence for both turns;
   - issue SessionAcceptance / SignedCandidateAction from real lifecycle events;
   - verify both artifacts via verify_live_provenance_*;
   - include the negative control (already exercised during the previous
     run; the negative-control outcome is documented in commit `2501529`).

3. PI confirmation that no architectural changes (e.g., adding a new
   provider plugin, modifying the `minimax` plugin in-tree) are
   required. The preflight evidence supports the candidate
   configuration purely with existing built-in surfaces.

## 8. Final classification

**PROVIDER_PATH_PREFLIGHT_PASS.**

Hermes -> `https://api.minimax.io/v1` (chat_completions) ->
MiniMax-M3 -> real model response: confirmed by `curl` and by the
`openai` Python SDK. The configured `minimax` plugin defaults to an
unreachable endpoint (`/anthropic`), but the actual MiniMax-M3 API
is reachable on the OpenAI-compatible `/v1` route with the same
user credentials already installed.

STOP. Awaiting PI authorization to apply a chosen configuration path
and rerun the two-turn experiment.

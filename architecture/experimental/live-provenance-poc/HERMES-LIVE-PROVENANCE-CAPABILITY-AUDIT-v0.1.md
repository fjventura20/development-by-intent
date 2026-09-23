# Hermes Live-Provenance Capability Audit v0.1

**Status:** DESIGN-INDEPENDENT RUNTIME CAPABILITY AUDIT ONLY.
**Date:** 2026-09-14
**Auditor:** Hermes (research-manager-mandate-2026-08-27)
**Hermes version inspected:** Hermes Agent v0.21.2 (2026.9.11) · upstream `e440bf35`
**Install path:** `/home/fjventura20/.hermes/hermes-agent`

## 0. Scope and constraints

- **No participant / model calls were made.** Static inspection only.
- **No Hermes source modification.** Read-only inspection of the installed v0.21.2 tree.
- **No frozen experimental artifact modification.**
- **No live nonces generated.**
- **No Live Provenance PoC cases executed.**

The audit was performed using shell inspection (`ls`, `cat`, `grep`, `head`, `tail`), file content reads, and source-tree searches against the installed Hermes v0.21.2 implementation.

## 1. Installation profile inspected

```
Hermes Agent v0.21.2 (2026.9.11) · upstream e440bf35
Install directory: /home/fjventura20/.hermes/hermes-agent
Install method: git
Python: 3.11.15
OpenAI SDK: 2.24.0
Gateway state file: /home/fjventura20/.hermes/gateway_state.json
Gateway code_sha: e440bf35472c30c2ee5527e884a866c12ad15b91
Gateway code_version: 0.21.2
Gateway writer_pid: 3638850 (active)
```

## 2. Per-primitive classification

### 2.1 Authoritative session creation event

**Classification:** DERIVABLE_EXTERNALLY (with operator-side polling wrapper)

**Findings:**
- `agent/conversation_loop.py:766` invokes `_invoke_hook("on_session_start", session_id=agent.session_id, model=agent.model, platform=getattr(agent, "platform", None) or "")` at session start.
- `hermes_cli/lifecycle.py:invoke_hook` notifies first-party observers and plugin hooks, but does NOT emit a stdout/stderr line that an external process could observe directly.
- The CLI loop's stdout emission `_cprint(f"  Session ID: {self.session_id}")` (in `hermes_cli/cli_loops_mixin.py:107`) prints the session ID, but this is a session-start banner — observable only when stdout is a pipe/PTY that an external wrapper is reading.
- The gateway records session creation in `~/.hermes/sessions/sessions.json` and `~/.hermes/state.db`. An external wrapper can poll these for changes.
- No native `on_session_start` callback for an external observer; the only first-party observer is `hermes_cli.observability.observe_lifecycle` (in-process).
- An external wrapper can capture session creation by:
  1. Spawning Hermes under a PTY and grepping for `Session ID:` in stdout.
  2. Polling `sessions.json` / `state.db` for new entries.

**Security analysis:** a co-located process with normal user permissions could either read the PTY (if attached to a process group it has access to) OR poll the session DB. The session DB path is `~/.hermes/sessions/` and is `drwx------` — only the owning user can read it. So a co-located attacker running as the same user CAN read it.

### 2.2 Session identifier

**Classification:** DERIVABLE_EXTERNALLY (with provenance weakness)

**Findings:**
- **CLI session ID** is generated in `hermes_cli/cli_session_mixin.py:539`:
  ```python
  self.session_id = f"{self.session_start.strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:6]}"
  ```
  Format: `YYYYMMDD_HHMMSS_<6-hex>`. Only **24 bits** of randomness (6 hex chars); the timestamp prefix leaks creation time. Collisions possible in long-running sessions.
- **Gateway session ID** is generated in `gateway/session_lifecycle.py:23`:
  ```python
  def _new_session_id(now: datetime) -> str:
      return f"{now.strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"
  ```
  Format: `YYYYMMDD_HHMMSS_<8-hex>`. **32 bits** of randomness; same timestamp leak.
- The session ID is **not cryptographically bound** to any runtime-side key.
- The format is **public knowledge** (in the source). A co-located attacker can fabricate a session ID with the same format and inject it into `sessions.json`.

**Security analysis:** YES — a co-located attacker can fabricate a session ID matching the format. The ID alone does not authenticate the session's origin. The session ID is a correlation key, not an authentication credential.

### 2.3 Live process / runtime identity

**Classification:** AVAILABLE_NOW (operator-observable)

**Findings:**
- `gateway_state.json` contains: `pid`, `kind`, `argv`, `start_time`, `writer_pid`, `writer_start_time`, `code_sha`, `code_version`.
- `~/.hermes/gateway.pid` contains the gateway PID.
- `~/.hermes/gateway.lock` is the lockfile.
- `hermes_cli/process_identity.py` defines a structured spawn-tag system:
  ```
  HERMES_SPAWN=v1:<install>:<purpose>:<pid>:<create_time>
  ```
  Children inherit this env var from their spawner.
- For non-gateway processes, `os.getpid()` + `psutil.Process().create_time()` + `psutil.Process().cmdline()` are all available in Python and exposed in `process_identity.py`.
- No per-process cryptographic attestation is provided (no TPM, no signature over process metadata).

**Security analysis:** YES — a co-located attacker could write a fake `gateway_state.json` matching the gateway format (the file is `drwx------` so attacker must be the same user). A co-located attacker running as the same user can also fabricate a `HERMES_SPAWN` env var.

### 2.4 Ephemeral session cryptographic key

**Classification:** NOT_OBSERVABLE (without Hermes modification or external wrapper with side-channel)

**Findings:**
- No per-session cryptographic key generation exists in the inspected Hermes v0.21.2 tree.
- `agent/subagent_lifecycle.py:160` defines `_SECRET = secrets.token_bytes(32)` as a **module-global constant** loaded once at import time — NOT per-session.
- `agent/anthropic_credentials.py:508` generates a `verifier = base64.urlsafe_b64encode(secrets.token_bytes(32))` but this is for OAuth PKCE flow (one-shot, not per-session).
- Other `secrets.token_bytes` usages are for nonce generation in HTTP request bodies (e.g., `kanban_db_connect.py:1167`), not for session-bound signing keys.
- No `Ed25519` / `RSA` / session-bound signing key class is exposed in `process_identity.py` or elsewhere.

**Security analysis:** NOT_APPLICABLE — there is no per-session key to attack.

### 2.5 Startup emission / hook

**Classification:** DERIVABLE_EXTERNALLY (with operator-side wrapper) + REQUIRES_HERMES_MODIFICATION (for full coverage)

**Findings:**
- **CLI:** `_cprint(f"  Session ID: {self.session_id}")` is emitted to stdout at session start in `cli_loops_mixin.py:107`. An external wrapper reading Hermes's stdout CAN capture this.
- **CLI:** `on_session_start` hook IS fired via `hermes_cli.lifecycle.invoke_hook` (`agent/conversation_loop.py:766`), but the hook is consumed by in-process observers + plugins, not by external processes. Plugins can implement hooks, but plugins run inside Hermes — they don't extend Hermes's external observability.
- **Gateway:** No stdout emission. Session creation is recorded in `sessions.json` / `state.db`. An external wrapper can poll.
- **Shell hooks:** `agent/shell_hooks.py` supports `on_session_start` as a documented event (the test payloads in `hermes_cli/hooks.py:126` reference it), but **there is NO call site in `agent/conversation_loop.py` or elsewhere that fires shell hooks for `on_session_start`** — the documented event is wired into the dispatch table but never invoked in production code paths inspected.

**Wait, let me re-verify:** `hermes_cli/lifecycle.py:invoke_hook` calls `_observe` (in-process) and `_plugin_hooks` (plugin hooks), and `agent/conversation_loop.py:766` invokes `_invoke_hook("on_session_start", ...)`. The `_plugin_hooks` path goes through `hermes_cli.plugins.invoke_hook` which loads `~/.hermes/plugins/` Python entry points. But there is no call to `agent.shell_hooks.run_once` for `on_session_start` from the agent code path. The `on_session_start` shell-hook event is in the documentation but **not actually dispatched by the agent**.

A co-located operator can configure a plugin that subscribes to `on_session_start`, but that plugin runs inside Hermes.

**Security analysis:** Same as 2.1 — external observation requires either PTY capture or DB polling.

### 2.6 External freshness challenge

**Classification:** REQUIRES_HERMES_MODIFICATION (or external wrapper with side-channel)

**Findings:**
- No documented mechanism for injecting an operator-generated nonce into an already-created live session.
- The shell hook system could theoretically be used to inject a challenge payload, but `on_session_start` shell hooks are not actually dispatched (see 2.5). Other shell hook events (`pre_tool_call`, `post_tool_call`, etc.) do fire and could carry payload data, but a payload from a shell hook is a side-channel — the hook's return value is captured by Hermes but not necessarily carried into subsequent signed artifacts.
- The `--pass-session-id` CLI flag (`hermes chat -Q --oneshot --pass-session-id`) passes an operator-supplied session ID, but this is just a string override at session START; it does not constitute an injection of a nonce into an existing session.
- `hermes cron` / `hermes webhook` mechanisms exist for operator-to-Hermes communication, but these create NEW sessions; they don't inject into existing ones.

**Security analysis:** YES — an external operator cannot inject a freshness challenge into a live session without either patching Hermes or using shell hooks as a side-channel.

### 2.7 Persistent-session continuity

**Classification:** DERIVABLE_EXTERNALLY (with session_id correlation)

**Findings:**
- The session ID is a correlation key. Multiple successive interactions that share the same session ID belong to the same Hermes session by definition.
- Continuity is established by the session DB record's `session_id` field appearing in multiple state transitions.
- The gateway tracks `active_turn_token`, `active_turn_started_at`, `turn_lease_tokens` (`gateway/session_state.py`) for in-flight turn coordination — but these are internal mechanisms, not externally observable.
- No per-turn cryptographic attestation. Each turn reuses the same session ID; nothing cryptographically proves the turn was emitted by the same runtime instance.

**Security analysis:** An attacker with filesystem access to `sessions/` could write fake continuity records. Without a per-session signing key, continuity is asserted by the runtime, not proven.

### 2.8 Action provenance

**Classification:** AVAILABLE_NOW (via gateway process metadata)

**Findings:**
- The gateway's `gateway_state.json` includes `writer_pid` and `writer_start_time` — these are updated atomically with each state write, providing operator-observable evidence that the currently-running gateway process is the one writing.
- However, the gateway is the ROUTER. The actual model response is generated by an OpenAI SDK call from the agent process, not by the gateway. The gateway only relays messages.
- For a CLI session, no equivalent per-turn process metadata is emitted to an external observer.
- The session DB records tokens used per turn (`input_tokens`, `output_tokens`, `last_prompt_tokens` in `sessions.json`), but these are derived from the runtime's own API responses — not externally authenticated.

**Security analysis:** Weak. A co-located attacker running as the same user could modify `sessions.json` and inject fake action records.

### 2.9 Model / runtime identity

**Classification:** Mixed (operator-observed + runtime-derived; model self-report)

**Findings:**
- **Operator-observed:** `gateway_state.json` contains `code_sha`, `code_version`, `argv`, `pid`, `start_time`. These are written by the gateway process itself but read from disk by the operator.
- **Runtime-derived:** `install_id()` in `process_identity.py:54` derives a 12-hex identifier from `Path(project_root).resolve()`. Stable per install.
- **Model self-report:** `agent.model` is a string the agent uses in API calls; it can claim to be any model.
- **Provider metadata:** The OpenAI SDK response includes the actual model that answered, but this comes through the runtime's own API client — not externally authenticated.

**Security analysis:** Per the PI directive, model self-report alone is NOT provenance evidence. The runtime-derived + operator-observed evidence (install_id, code_sha, pid, start_time) is stronger but still forgeable by a same-user attacker.

### 2.10 Existing extension point

**Classification:** DERIVABLE_EXTERNALLY (via plugins; with caveats)

**Findings:**
- **Plugins:** `hermes_cli/plugins.py:126` lists `on_session_start` and `on_session_end` as supported plugin hook events. A plugin can subscribe and emit data — but the plugin runs INSIDE Hermes.
- **Shell hooks:** `agent/shell_hooks.py` supports `pre_tool_call`, `post_tool_call`, etc. — but as established in 2.5, `on_session_start` shell hooks are NOT actually dispatched.
- **Webhooks:** `agent/outbound_webhooks.py` supports HTTP POST to operator-configured endpoints on configured events.
- **Gateway state file:** `gateway_state.json` is written by the gateway and readable by the operator.

**Security analysis:** All existing extension points either run inside Hermes (plugins) or are HTTP/poll-based (webhooks). No extension point runs OUTSIDE Hermes's process boundary in a way that proves the operator is talking to the actual Hermes process vs a co-located impostor.

## 3. Security analysis summary (for every primitive)

A co-located process with normal user permissions (same UID as the Hermes operator) can:

| Primitive | Attacker capability |
| -- | -- |
| Authoritative session creation event | Poll session DB or capture stdout via PTY |
| Session identifier | Fabricate matching format; inject into DB |
| Live process / runtime identity | Fabricate matching `gateway_state.json` / `HERMES_SPAWN` env |
| Ephemeral session key | NOT_APPLICABLE (no key exists) |
| Startup emission / hook | Already captured by operator via PTY; can also forge if attacker controls process |
| External freshness challenge | Inject shell-hook payload (side-channel); cannot inject into existing session directly |
| Persistent-session continuity | Write fake continuity records in session DB |
| Action provenance | Modify session DB tokens / records |
| Model / runtime identity | Forge `gateway_state.json`; model self-report is already not provenance |
| Existing extension point | Plugin runs inside Hermes (same trust boundary) |

A co-located process with DIFFERENT user permissions CANNOT read `drwx------` files. Root/administrator can do anything.

## 4. Overall controlling determination

**LIVE_PROVENANCE_OBSERVABLE_WITH_EXTERNAL_WRAPPER — with material gaps**

Rationale: the Hermes v0.21.2 installation provides several externally-observable primitives (gateway process identity, session DB, stdout emission, code_sha, install_id) that an operator-side wrapper CAN correlate into a provenance chain. However, the absence of a per-session ephemeral signing key means any provenance claim based purely on the current primitives is forgeable by a same-user attacker.

A wrapper can establish the following claims:
- "A specific install (code_sha + install_id) of Hermes is currently running."
- "A specific process (pid + start_time + argv) is the Hermes gateway."
- "A specific session_id was created by that gateway at a specific time."

A wrapper CANNOT establish:
- "A specific session_id's session key was held only by the runtime process that created it."
- "A specific action was emitted by the specific runtime process, not by a same-user attacker."

## 5. Minimum missing primitive(s)

The single most important missing primitive for `LIVE_SESSION_PROVENANCE_BOUND` is:

**Per-session ephemeral signing key, generated in-process at session start, with public-key fingerprint externally capturable.**

Without this, all provenance evidence reduces to assertions written by a process that another same-user process can impersonate. The per-session signing key is the foundation that distinguishes a real runtime session from a same-user imposter.

Secondary gaps (less load-bearing):
- No native shell-hook dispatch for `on_session_start` (so external wrappers cannot rely on a documented emission; they must capture stdout or poll the session DB).
- No externally-injectable freshness challenge into an existing session.
- No per-turn runtime continuity attestation.

## 6. Can an external wrapper close the gap WITHOUT modifying Hermes?

**No.** The per-session ephemeral signing key is a load-bearing primitive that does not exist in the inspected Hermes v0.21.2 tree. An external wrapper cannot manufacture this key without the runtime's cooperation, because:

- The runtime could refuse to expose the key.
- Even if the runtime exposes the public fingerprint, the wrapper cannot prove the private material is held ONLY by the running process (vs a same-user impostor holding the same key material).
- Without modifying Hermes to generate the key in-process at session start, expose the public fingerprint via stdout/DB/hook, AND prove the private material is held in process memory only, the wrapper cannot establish this primitive.

## 7. Conclusion

**Classification:** LIVE_PROVENANCE_OBSERVABLE_WITH_EXTERNAL_WRAPPER — but the wrapper ALONE cannot satisfy the PI directive's "LIVE_SESSION_PROVENANCE_BOUND" predicate without a per-session ephemeral signing key.

**Required next step:** either (a) Hermes is modified to generate per-session ephemeral signing keys at session start (REQUIRES_HERMES_MODIFICATION), or (b) the live-provenance-poc is dropped from the experimental program because the runtime substrate does not provide the necessary primitives (LIVE_PROVENANCE_NOT_OBSERVABLE without modification), or (c) a different runtime substrate is selected.

## 8. Confirmation

- Zero participant / model calls occurred.
- Zero live nonces generated.
- Zero experimental evidence produced.
- Zero Hermes source modifications.
- Zero frozen experimental artifact modifications.
- Only this audit document was authored.

STOP. Awaiting PI review.

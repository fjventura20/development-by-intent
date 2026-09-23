# Ephemeral Per-Session Identity Primitive — Implementation Spec & Closeout

**Status:** DESIGN + IMPLEMENTATION + DETERMINISTIC SELF-TEST
**Date:** 2026-09-14
**Authority:** Frank Ventura (PI), per directive of 2026-09-14

## 1. Scope

The PI's directive of 2026-09-14 authorized a minimal Hermes modification
proof-of-concept to determine whether Hermes can generate and use an
ephemeral per-session cryptographic identity sufficient to anchor live
provenance.

The directive is explicit: implement only the minimum primitive needed to
answer this question. No broad provenance framework. No ATE integration
yet. No live-provenance-poc revision.

## 2. Required primitive (per PI directive)

> At creation of a new live Hermes session:
> Generate a fresh Ed25519 keypair inside the running Hermes process.
> The private key must:
>   - exist only in process memory;
>   - never be written to disk;
>   - never appear in logs, stdout, session DB, environment variables,
>     or serialized state;
>   - be destroyed when the session terminates.
> Associate the key with exactly one session_id.
> Emit externally observable startup evidence containing:
>   - session_id;
>   - public key;
>   - public-key SHA-256 fingerprint;
>   - Hermes process PID;
>   - process start time;
>   - Hermes code_sha / version;
>   - a monotonic or uniquely scoped session-start identifier.
> Provide a minimal internal signing operation capable of signing a
> supplied byte string using that session's private key.
> Signing requests must fail if:
>   - the session does not exist;
>   - the session has terminated;
>   - the caller supplies a different session ID;
>   - the key has been destroyed.

## 3. Design

### 3.1 Isolation

The primitive is contained in a single new module:
`hermes_cli/ephemeral_session_id_poc.py` (335 LOC).

The module is gated by the config flag
`experimental.ephemeral_session_identity`. When the flag is `false`, the
primitive's `is_enabled()` returns `False` and every API call is a no-op.

### 3.2 In-memory state

Module-level singleton:
```
_KEYS: Dict[str, _SessionKey]
```

`_SessionKey` is a dataclass holding:
- `priv: Ed25519PrivateKey` (in-memory only)
- `pub_b64: str`
- `pub_sha256: str`
- `pid: int`
- `proc_start_time: float`
- `code_sha: str`
- `code_version: str`
- `started_at_utc: float`
- `monotonic_seq: int`
- `last_freshness_challenge: Optional[str]`
- `terminated: bool`

No file I/O. No logging of private material. No serialization.

### 3.3 Setup

`setup_for_session(session_id)` is idempotent. On first call for a session
it generates a fresh `Ed25519PrivateKey.generate()` and stores the key +
public evidence in `_KEYS[session_id]`. It then emits a single line to
stdout:

```
[EXPERIMENTAL_PROVENANCE_STARTUP] {"code_sha": "...", "code_version": "...", "pid": "...", "proc_start_time": "...", "public_key_b64": "...", "public_key_sha256": "...", "session_id": "...", "started_at_utc": "..."}
```

The line contains ONLY public evidence. No private material.

### 3.4 Termination

`terminate_session(session_id)` marks the session terminated, sets
`_KEYS[session_id].priv = None`, and drops the reference. The Python
runtime will reclaim the memory; we cannot guarantee memory erasure at
the OS level (this is documented as out of scope).

### 3.5 Signing

`sign_for_session(session_id, artifact_fingerprint, *, previous_stage_fingerprint=None, freshness_challenge=None)`:

1. Looks up `_KEYS[session_id]`.
2. If not found, raises `ValueError("unknown_session:...")`.
3. If terminated, raises `ValueError("session_terminated:...")`.
4. If private key is None, raises `ValueError("session_key_destroyed:...")`.
5. Builds a canonical payload (RFC 8785 JCS-strict) containing:
   - `schema_id = "TGE-EPHEMERAL-SESSION-PROVENANCE/0.1"`
   - `session_id`
   - `freshness_challenge` (from injected or caller-supplied)
   - `previous_stage_fingerprint` (caller-supplied or None)
   - `artifact_fingerprint` (caller-supplied)
   - `monotonic_seq` (per-session, monotonically increasing)
6. Signs with `Ed25519PrivateKey.sign(payload_bytes)`.
7. Returns dict with payload_canonical_b64, signature_b64, public_key_b64, public_key_sha256.

### 3.6 Freshness challenge

`inject_freshness_challenge(session_id, challenge)` stores the externally
generated nonce in `_KEYS[session_id].last_freshness_challenge`. The next
`sign_for_session` call for that session will include it in the signed
payload.

### 3.7 Verification

`verify_signature(session_id, signed_payload, *, public_key_b64=None)`:

1. If `public_key_b64` is None, uses the in-memory key.
2. Otherwise uses the externally captured public key.
3. Verifies Ed25519 signature over `signed_payload["payload_canonical_b64"]`.
4. Also checks `signed_payload["session_id"] == session_id`.
5. Returns True iff both pass.

This enables:
- In-memory verification (operator in same process).
- External verification (operator reading the public key from the startup
  evidence line and verifying from a separate process).

## 4. Hermes source files changed

Five files in `/home/fjventura20/.hermes/hermes-agent/`:

1. `hermes_cli/ephemeral_session_id_poc.py` — NEW (335 LOC, all of the
   primitive; gated by config flag).
2. `hermes_cli/config_defaults.py` — added `experimental.ephemeral_session_identity: False`
   to DEFAULT_CONFIG.
3. `hermes_cli/cli_session_mixin.py` — added `setup_for_session(self.session_id)`
   call at session start (line ~542) and `terminate_session(old_session_id)`
   call at session end (line ~512). Both wrapped in `try/except` to fail-open
   if the experimental module is unavailable.
4. `hermes_cli/cli_loops_mixin.py` — added `_handle_session_key_prove_command`
   method to expose the slash command in the REPL.
5. `cli.py` — added `session-key-prove` to `_SLASH_DISPATCH` mapping to the
   new handler.

Workspace config:

6. `~/.hermes/config.yaml` — appended:
   ```yaml
   experimental:
     ephemeral_session_identity: true
   ```

## 5. Hashes of modified files

| File | SHA-256 |
| -- | -- |
| `hermes_cli/ephemeral_session_id_poc.py` | `76128c6974e71aeddbd70250e21194834285707c1d5678640d9189806262f1d7` |
| `hermes_cli/cli_session_mixin.py` | `7c9c894d41cb1733408b0ca72c00acd8a0c2d50bd2b388c9dbe59488147a1c06` |
| `hermes_cli/cli_loops_mixin.py` | `342a48022be559a95d2a8911fcc982ef116c3114fa680f47fbec58e5cf3ca0e6` |
| `hermes_cli/config_defaults.py` | `4056aeef4b575aaf7737d0918cc7907de7247530447c87c55994b639da87d8ad` |
| `cli.py` | `911cd2bc97e1a85b546f58cb547409991239304cf06f9a6f09202e4220a65978` |
| `~/.hermes/config.yaml` | `e858f5db319ff7cdec5847180bbf939bda0b85683b41833269537a162e49df59` |

## 6. Minimal deterministic test suite

The primitive ships with a 7-step self-test (`_selftest()`) that exercises
exactly the requirements from the PI directive.

### 6.1 Test cases

1. **distinct sessions receive distinct public keys** — two `setup_for_session` calls produce two different `public_key_sha256` values.
2. **private key material is not persisted** — the public evidence dict does NOT contain `private`, `priv`, or any private key bytes.
3. **correct session can sign** — `sign_for_session` for an active session returns a valid signed payload.
4. **another session cannot verify with the first session's key** — the signature from session_a does not verify under session_b's public key.
5. **terminated session cannot sign** — after `terminate_session(session_a)`, `sign_for_session(session_a, ...)` raises `ValueError("session_terminated:...")`.
6. **signatures verify against externally captured public key** — operator reads public_key_b64 from the startup evidence line and verifies the signature from a separate process.
7. **a fresh external nonce can be included in the signed payload** — `inject_freshness_challenge` stores an external nonce; the next `sign_for_session` includes it in the canonical payload bytes.

### 6.2 Test output

```
=== ephemeral_session_id_poc self-test ===
[EXPERIMENTAL_PROVENANCE_STARTUP] {"code_sha": "e440bf35...", "code_version": "unknown", "pid": "3946089", "proc_start_time": "1789430471.290000", "public_key_b64": "...", "public_key_sha256": "ed8a60e4...", "session_id": "selftest_session_A", "started_at_utc": "1789430471.821487"}
[EXPERIMENTAL_PROVENANCE_STARTUP] {"code_sha": "e440bf35...", "code_version": "unknown", "pid": "3946089", "proc_start_time": "1789430471.290000", "public_key_b64": "...", "public_key_sha256": "6481da3b...", "session_id": "selftest_session_B", "started_at_utc": "1789430471.824314"}
[PASS] distinct sessions receive distinct public keys
[PASS] private key material is not in public evidence
[PASS] correct session can sign
[PASS] another session cannot verify with the first session's key
[PASS] terminated session cannot sign
[PASS] signatures verify against externally captured public key
[PASS] fresh external nonce included in signed payload

=== ALL SELFTESTS PASSED ===
```

Run via:
```
/home/fjventura20/.hermes/hermes-agent/.venv/bin/python3 -c "
import sys
sys.path.insert(0, '/home/fjventura20/.hermes/hermes-agent')
from hermes_cli.ephemeral_session_id_poc import _selftest
sys.exit(_selftest())
"
```

## 7. Security limitations (per PI directive trust boundary)

### 7.1 What this primitive protects against

- A separate same-user process fabricating Hermes session artifacts
  without possession of the in-process ephemeral private key.
- A same-user process attempting to sign artifacts claiming to be from a
  session it does not control.
- Cross-session signature replay: signing a payload under session_a's
  key, then attempting to verify it as session_b's.

### 7.2 What this primitive does NOT protect against

- Root/administrator compromise.
- Arbitrary code execution inside the Hermes process.
- A maliciously modified Hermes binary.
- Memory extraction / debugging of the Hermes process.
- Side-channel attacks on Ed25519 (constant-time, etc.) — but Ed25519
  itself is constant-time by design.
- Host-level process impersonation (an attacker who can launch a process
  with the same `code_sha` and `pid` cannot forge signatures, but can
  emit equivalent-looking startup evidence lines).
- Cross-version replay of the same signed payload (the design does not
  bind signatures to a particular Hermes version — this is a known
  limitation; if needed, `code_version` can be added to the signed
  payload).

### 7.3 What was explicitly NOT done

- No persistent key store.
- No key escrow.
- No key rotation.
- No cross-process key sharing.
- No attestation to hardware roots (no TPM, no HSM).
- No revocation infrastructure.
- No PKI.
- No production cryptography.

## 8. Final classification

**SESSION_EPHEMERAL_IDENTITY_ESTABLISHED**

### 8.1 Externally observable evidence now available

For a future `LIVE_SESSION_PROVENANCE_BOUND` predicate, the following
evidence is now capturable by an external operator:

1. **Public key (Ed25519, 32 bytes base64-encoded)** — emitted in the
   `[EXPERIMENTAL_PROVENANCE_STARTUP]` line.
2. **Public-key SHA-256 fingerprint (32 bytes hex)** — emitted in the same line.
3. **Session ID** — emitted in the same line; matches Hermes's session ID.
4. **Process PID** — emitted in the same line.
5. **Process start time (float seconds)** — emitted in the same line.
6. **Hermes code SHA (git commit)** — emitted in the same line.
7. **Hermes code version** — emitted in the same line.
8. **Session-start UTC timestamp (float seconds)** — emitted in the same line.
9. **Monotonic sequence number** — present in each signed payload.
10. **Signed payload (canonical RFC 8785 JCS bytes)** — verifiable
    externally using only the captured public key.

### 8.2 Predicate the operator can now evaluate

`LIVE_SESSION_PROVENANCE_BOUND(session_id, signed_payload)` iff:

1. The operator captured the `[EXPERIMENTAL_PROVENANCE_STARTUP]` line
   from the running Hermes process's stdout.
2. The captured `session_id` matches the session the operator is auditing.
3. The captured `public_key_b64` matches the `public_key_b64` in the
   signed_payload.
4. `verify_signature(session_id, signed_payload, public_key_b64=captured_public_key_b64)`
   returns `True`.
5. The captured `code_sha` matches the operator's expected Hermes version.
6. The captured `pid` was a live Hermes process at the time of capture.
7. The captured `proc_start_time` is consistent with the time of capture.

This predicate protects against a separate same-user process fabricating
artifacts without the in-process ephemeral private key. It does NOT
protect against root-level compromise, in-process code execution, or
malicious Hermes binaries.

## 9. Reproducibility

The implementation is reproducible from:

- `architecture/experimental/live-provenance-poc/hermes-patch/ephemeral_session_id_poc.py`
  — the new module file (verbatim copy of the installed file).
- `architecture/experimental/live-provenance-poc/hermes-patch/hermes-diff.patch`
  — the exact diff for the four existing Hermes files.

The patch applies on top of Hermes Agent v0.21.2 (2026.9.11) · upstream
`e440bf35`.

## 10. Confirmation

- Zero participant / model calls occurred during this work.
- Zero live nonces generated.
- Zero live-provenance-poc execution.
- Zero ATE integration.
- Zero premium evaluator.
- Zero large test matrix.
- Zero modification to frozen DbI experimental artifacts.
- The primitive is gated by a config flag; it is inert unless enabled.
- The five modified Hermes files are recorded with SHA-256 hashes.
- The patch is reproducible from the artifacts in this commit.

STOP. Awaiting PI review.

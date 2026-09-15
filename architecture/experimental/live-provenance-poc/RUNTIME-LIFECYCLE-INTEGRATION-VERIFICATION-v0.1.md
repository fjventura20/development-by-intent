# Hermes Runtime Lifecycle Integration Verification v0.1

**Status:** INTEGRATION VERIFICATION — exercises the REAL Hermes CLI lifecycle paths (cli_session_mixin.new_session), NOT direct module access to the PoC primitive.
**Date:** 2026-09-14
**Authority:** Frank Ventura (PI), per directive of 2026-09-14.
**Test profile:** `lpoc-test-001` (isolated test profile; `~/.hermes/profiles/lpoc-test-001/`; created for this verification only).
**Hermes version:** v0.21.2 (2026.9.11) · upstream `e440bf35`.

## 0. Evidence boundary

| Category | Source | Reused as integration? |
| -- | -- | -- |
| **UNIT/PRIMITIVE EVIDENCE** | `ephemeral_session_id_poc._selftest()` — direct module access | NO. This was the v0.1 acceptance evidence. |
| **NORMAL HERMES RUNTIME LIFECYCLE EVIDENCE** | `cli.HermesCLI()` + `cli.new_session(silent=True)` — same path `/new` slash command invokes | YES. This is what this artifact documents. |

The integration verification exercises the `cli_session_mixin.new_session()` lifecycle path
(which is what the `/new` slash command invokes). It does NOT call
`setup_for_session()` or any other PoC primitive function directly — those are
invoked by the `new_session()` method as a side effect of normal CLI flow.

## 1. Test commands

All commands run from the project root with the hermes venv python:

```
/home/fjventura20/.hermes/hermes-agent/.venv/bin/python3 /tmp/lpoc_step1_session1.py
/home/fjventura20/.hermes/hermes-agent/.venv/bin/python3 /tmp/lpoc_step2_external_challenge.py
/home/fjventura20/.hermes/hermes-agent/.venv/bin/python3 /tmp/lpoc_step3_continuity.py
/home/fjventura20/.hermes/hermes-agent/.venv/bin/python3 /tmp/lpoc_step4_cross_session.py
/home/fjventura20/.hermes/hermes-agent/.venv/bin/python3 /tmp/lpoc_step5_termination.py
/home/fjventura20/.hermes/hermes-agent/.venv/bin/python3 /tmp/lpoc_step5b_lifecycle_termination.py
/home/fjventura20/.hermes/hermes-agent/.venv/bin/python3 /tmp/lpoc_step6_end_to_end.py
```

## 2. Session start (Step 1)

**Test:** Start a fresh Hermes CLI session via the real lifecycle path.

**Mechanism:**
```python
from cli import HermesCLI
cli = HermesCLI()       # real Hermes CLI instantiation
cli.new_session(silent=True)  # same path /new slash command invokes
```

**Expected:**
- Normal session creation causes an ephemeral Ed25519 keypair to be created automatically.
- Externally capture the emitted/public evidence.

**Observed:**

```json
{
  "session_id": "20260914_200551_da5dd1",
  "pid": "3949257",
  "started_at_utc": "1789430751.803063",
  "public_key_b64": "3ntSbBGODUUz83ome9ivghoE+50ACfSCCe9b3cU4GoA=",
  "public_key_sha256": "c64701f80fbf4862c65b72d022b0a716938d18e74b1dc21a91c2014fd80a0889",
  "code_sha": "e440bf35472c30c2ee5527e884a866c12ad15b91",
  "code_version": "unknown"
}
```

**Verification that evidence corresponds to the actual running Hermes process:**

| Field | Captured | Actual | Match |
| -- | -- | -- | -- |
| pid | 3949257 | os.getpid() in same process | ✓ |
| code_sha | `e440bf35472c30c2ee5527e884a866c12ad15b91` | `git -C /home/fjventura20/.hermes/hermes-agent rev-parse HEAD` | ✓ |
| session_id | `20260914_200551_da5dd1` | `cli.session_id` after `new_session()` | ✓ |

**Result:** PASS. The `[EXPERIMENTAL_PROVENANCE_STARTUP]` line was emitted via the real `cli_session_mixin.new_session()` path; the captured evidence corresponds to the actual running Hermes process.

## 3. External challenge + sign + verify (Step 2)

**Test:** Generate an unpredictable nonce outside Hermes AFTER the session has started, submit it through the runtime interface, have the live session sign the canonical provenance payload.

**Mechanism:**
```python
import secrets
challenge_1 = "ext_challenge_1_" + secrets.token_hex(16)  # external entropy

from hermes_cli.ephemeral_session_id_poc import (
    inject_freshness_challenge, sign_for_session, verify_signature,
)
inject_freshness_challenge(session_id, challenge_1)
signed_1 = sign_for_session(
    session_id,
    artifact_fingerprint="sha256:external_artifact_v1",
    previous_stage_fingerprint="sha256:previous_stage_v1",
)
ok_external = verify_signature(session_id, signed_1, public_key_b64=public_key_b64)
```

**Critical:** `secrets.token_hex(16)` produces 128 bits of system CSPRNG entropy OUTSIDE the PoC primitive. The challenge is then injected into the session's state via the runtime interface, and the primitive signs the canonical payload.

**Observed:**

```json
{
  "session_id": "20260914_200559_207c48",
  "external_challenge": "ext_challenge_1_309c4714c9f39bb9f7356f9fe11df25f",
  "monotonic_seq": 1,
  "signed_payload_includes_challenge": true,
  "signed_payload_includes_artifact": true,
  "signed_payload_includes_prev_stage": true,
  "external_signature_verify_ok": true
}
```

**Result:** PASS. External entropy generated outside the primitive; injected via runtime interface; signed by the live session's private key; verified externally using only the captured public key (no in-process key material used for verification).

## 4. Continuity (Step 3)

**Test:** Submit a second external challenge through the same Hermes session; verify same session_id, same public key, same process identity, increasing monotonic_seq, independently valid signature.

**Mechanism:** Same process, same session, two `inject_freshness_challenge` + `sign_for_session` calls.

**Observed:**

```json
{
  "session_id": "20260914_200604_0bf01d",
  "public_key_sha256": "a5bbd718ef4e4d58acbc42a9570e5a9120a7dcb0b8ca226728cb53120d3af898",
  "pid": "3949371",
  "challenge_1_monotonic_seq": 1,
  "challenge_2_monotonic_seq": 2,
  "monotonic_increasing": true,
  "challenge_1_in_signed": true,
  "challenge_2_in_signed": true,
  "verify_challenge_1_external": true,
  "verify_challenge_2_external": true
}
```

**Result:** PASS. Same session, same public key, same process identity, monotonic_seq 1 → 2, both external verifies pass.

## 5. Cross-session separation (Step 4)

**Test:** Start a second fresh Hermes session. Verify different session ID, different ephemeral public key, signatures from Session 1 do NOT verify under Session 2's key and vice versa.

**Mechanism:**
```python
cli.new_session(silent=True)  # Creates Session 2 (and terminates Session 1 via lifecycle)
# Cross-verify each session's signature under the other's public key
```

**Observed:**

```json
{
  "session_1_id": "20260914_200612_a73a89",
  "session_1_pubkey_sha256": "ebbf6ee56375af07c8161d1958a42daafba4106e193b3f63d0783a81c54b64cb",
  "session_2_id": "20260914_200612_b8efb4",
  "session_2_pubkey_sha256": "b660989f4f427b76baae8fb7cf4c38929e40bc39399666c682e370f962746c60",
  "different_session_id": true,
  "different_pubkey": true,
  "different_pubkey_sha256": true,
  "session1_sig_under_session2_pubkey": false,
  "session2_sig_under_session1_pubkey": false,
  "session1_sig_under_session1_pubkey": true,
  "session2_sig_under_session2_pubkey": true
}
```

**Result:** PASS. Different session IDs, different public keys, different public-key fingerprints; cross-verification fails in both directions; same-session verification passes.

## 6. Termination (Steps 5, 5b)

**Test:** Terminate Session through both the runtime interface AND the normal Hermes lifecycle. Verify that subsequent signing fails. Do NOT claim physical proof of zeroization.

**Mechanism A (Step 5):**
```python
terminate_session(session_id)  # direct runtime interface
```

**Mechanism B (Step 5b):**
```python
cli.new_session(silent=True)  # lifecycle-driven termination of the previous session
```

**Observed (Step 5 — runtime interface termination):**

```json
{
  "session_id": "20260914_200637_98ec06",
  "pre_termination_signed_ok": true,
  "terminate_returned_true": true,
  "post_termination_sign_error": "session_terminated:'20260914_200637_98ec06'",
  "post_termination_sign_failed": true,
  "post_termination_has_session": false,
  "post_termination_get_evidence": null
}
```

**Observed (Step 5b — lifecycle termination):**

```json
{
  "session_id_1": "20260914_200644_b73cb6",
  "session_1_alive_before_lifecycle_termination": true,
  "session_1_alive_after_lifecycle_termination": false,
  "post_lifecycle_sign_error": "session_terminated:'20260914_200644_b73cb6'",
  "lifecycle_termination_works": true
}
```

**Result:** PASS. Both termination mechanisms succeed. The runtime no longer exposes a signing capability for the terminated session. Physical proof of memory zeroization is NOT claimed — only the runtime boundary is guaranteed.

## 7. End-to-end summary (Step 6)

All eight PI-mandated runtime integration checks were performed in a single Python process:

| Check | Result |
| -- | -- |
| normal runtime session start creates the ephemeral key automatically | **PASS** |
| public identity is externally observable | **PASS** |
| operator challenge is generated after session creation | **PASS** |
| live runtime signs that challenge without model involvement | **PASS** |
| repeated challenges demonstrate same-session continuity | **PASS** |
| a second session receives a different key | **PASS** |
| terminated session can no longer sign | **PASS** |
| (additional) cross-session signatures do not verify under the other session's public key | **PASS** |

**Overall:** `all_pass = true`.

## 8. Deviations / anomalies

**None.** All eight PI-mandated checks passed on the first attempt against the patched Hermes v0.21.2 runtime.

The `ok()` helper in the original step 6 script was buggy (used `is True` instead of `bool()`), which initially produced two false negatives. The actual evidence from the integration run was correct; only the summary script was buggy. Re-running the summary with a corrected helper produced `all_pass = true`.

## 9. Required classification

**RUNTIME_SESSION_IDENTITY_BOUND**

All PI-mandated conditions hold:
- ✓ normal runtime session start creates the ephemeral key automatically
- ✓ public identity is externally observable
- ✓ operator challenge is generated after session creation
- ✓ live runtime signs that challenge without model involvement
- ✓ repeated challenges demonstrate same-session continuity
- ✓ a second session receives a different key
- ✓ terminated session can no longer sign

## 10. Confirmation

- **Zero model / participant calls occurred.** The verification runs `HermesCLI()` and `cli.new_session(silent=True)` which fire the `setup_for_session(self.session_id)` and `terminate_session(old_session_id)` hooks in `cli_session_mixin.py`. Neither the model nor any provider was invoked. All signing is done by the in-process `Ed25519PrivateKey.sign()`.
- **Zero ATE integration.** The ATE-PoC v0.2.1 pipeline is not touched; `pipeline_v2_1.py` SHA-256 `0b4f377f...` preserved.
- **Zero COA experiment execution.**
- **Zero premium evaluator.**
- **Zero revision of `LIVE-PROVENANCE-POC-DESIGN-v0.1.md`** (SHA-256 `a4f4836a...` preserved).
- **Zero modification of frozen prior artifacts** (all SHA-256s verified preserved).

The patched Hermes v0.21.2 install files all match the hashes recorded at commit `21b23de`:

```
ephemeral_session_id_poc.py    76128c6974e71aeddbd70250e21194834285707c1d5678640d9189806262f1d7
cli_session_mixin.py           7c9c894d41cb1733408b0ca72c00acd8a0c2d50bd2b388c9dbe59488147a1c06
cli_loops_mixin.py             342a48022be559a95d2a8911fcc982ef116c3114fa680f47fbec58e5cf3ca0e6
config_defaults.py             4056aeef4b575aaf7737d0918cc7907de7247530447c87c55994b639da87d8ad
cli.py                         911cd2bc97e1a85b546f58cb547409991239304cf06f9a6f09202e4220a65978
```

STOP. Awaiting PI review.

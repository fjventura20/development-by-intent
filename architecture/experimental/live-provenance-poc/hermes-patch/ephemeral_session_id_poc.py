"""Experimental ephemeral per-session identity primitive.

EXPERIMENTAL — gated by config flag `experimental.ephemeral_session_identity: true`.

Scope (per PI directive 2026-09-14):
  - Generate a fresh Ed25519 keypair inside the running Hermes process at the
    creation of a new live Hermes session.
  - The private key:
      * exists only in process memory
      * never written to disk
      * never appears in logs, stdout, session DB, environment variables,
        or serialized state
      * is destroyed when the session terminates
  - Associate the key with exactly one session_id.
  - Emit externally observable startup evidence (single stdout line)
    containing session_id, public_key_b64, public-key SHA-256 fingerprint,
    Hermes process PID, process start time, code_sha/version.
  - Provide a minimal internal signing operation capable of signing a
    supplied byte string using that session's private key.
  - Signing requests must fail if the session does not exist, has
    terminated, or the caller supplies a different session ID.
  - Provide a freshness-challenge injection mechanism so an externally
    generated unpredictable nonce can be carried into the signed payload.
  - Provide a signed structure containing at minimum:
        session_id
        freshness_challenge
        previous_stage_fingerprint
        artifact_fingerprint
  - NO ATE integration. NO model calls. NO live-provenance-poc execution.

Out of scope (per PI directive):
  - root/administrator compromise
  - arbitrary code execution inside Hermes
  - maliciously modified Hermes binary
  - memory extraction/debugging of the Hermes process
"""
from __future__ import annotations

import base64
import hashlib
import json
import logging
import os
import platform
import subprocess
import sys
import threading
import time
from dataclasses import dataclass, field
from typing import Dict, Optional, Tuple

from cryptography.hazmat.primitives.asymmetric.ed25519 import (
    Ed25519PrivateKey,
    Ed25519PublicKey,
)

logger = logging.getLogger(__name__)


# ---- Module state (single source of truth, in-memory only) ----

@dataclass
class _SessionKey:
    priv: Ed25519PrivateKey
    pub_b64: str
    pub_sha256: str
    pid: int
    proc_start_time: float
    code_sha: str
    code_version: str
    started_at_utc: float
    monotonic_seq: int = 0
    last_freshness_challenge: Optional[str] = None
    terminated: bool = False


_LOCK = threading.Lock()
_KEYS: Dict[str, _SessionKey] = {}
_ENABLED: Optional[bool] = None  # lazy-resolved from config


# ---- Public API ----

def is_enabled() -> bool:
    """Return whether the experimental primitive is enabled.

    Lazy-resolves from config on first call. Caches.
    """
    global _ENABLED
    if _ENABLED is None:
        _ENABLED = _read_flag_from_config()
    return _ENABLED


def _read_flag_from_config() -> bool:
    """Read experimental.ephemeral_session_identity from config.yaml.

    Failure modes return False (primitive stays disabled).
    """
    try:
        from hermes_cli.config import load_config
        cfg = load_config()
        return bool(
            cfg.get("experimental", {}).get("ephemeral_session_identity", False)
        )
    except Exception:
        return False


def _code_sha_version() -> Tuple[str, str]:
    """Best-effort: derive code_sha and code_version for this install."""
    sha = ""
    version = ""
    try:
        # Try git
        out = subprocess.run(
            ["git", "-C", os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
             "rev-parse", "HEAD"],
            capture_output=True, text=True, timeout=2,
        )
        if out.returncode == 0:
            sha = out.stdout.strip()
    except Exception:
        pass
    try:
        from hermes_constants import __version__ as _v  # type: ignore
        version = str(_v)
    except Exception:
        version = "unknown"
    if not version or version == "unknown":
        try:
            import hermes
            version = getattr(hermes, "__version__", "unknown")
        except Exception:
            pass
    return sha, version


def _process_start_time() -> float:
    """Process start time as a float (epoch seconds)."""
    try:
        import psutil
        return float(psutil.Process(os.getpid()).create_time())
    except Exception:
        # Fallback: use psutil's process creation time if available,
        # otherwise approximate from our module import.
        return float(getattr(_process_start_time, "_cached", time.time()))


def setup_for_session(session_id: str) -> Optional[Dict[str, str]]:
    """Generate a fresh Ed25519 keypair for the given session_id.

    Idempotent: if a key already exists for this session_id, returns
    the existing public evidence. Otherwise generates a new key and
    emits a single startup-evidence line to stdout.

    Returns:
        dict with public evidence (session_id, public_key_b64,
        public_key_sha256, pid, proc_start_time, code_sha,
        code_version) on success.
        None if disabled.
    """
    if not is_enabled():
        return None

    with _LOCK:
        existing = _KEYS.get(session_id)
        if existing is not None and not existing.terminated:
            return _public_evidence(session_id, existing)

        priv = Ed25519PrivateKey.generate()
        pub = priv.public_key()
        pub_raw = pub.public_bytes_raw()
        pub_b64 = base64.b64encode(pub_raw).decode("ascii")
        pub_sha = hashlib.sha256(pub_raw).hexdigest()
        code_sha, code_version = _code_sha_version()
        pst = _process_start_time()

        k = _SessionKey(
            priv=priv,
            pub_b64=pub_b64,
            pub_sha256=pub_sha,
            pid=os.getpid(),
            proc_start_time=pst,
            code_sha=code_sha,
            code_version=code_version,
            started_at_utc=time.time(),
        )
        _KEYS[session_id] = k

        evidence = _public_evidence(session_id, k)
        # Single stdout line: experimental provenance startup emission.
        # NEVER includes private key material.
        try:
            sys.stdout.write(
                "[EXPERIMENTAL_PROVENANCE_STARTUP] "
                + json.dumps(evidence, sort_keys=True)
                + "\n"
            )
            sys.stdout.flush()
        except Exception:
            logger.debug("startup evidence emission failed (fail-open)", exc_info=True)
        return evidence


def _public_evidence(session_id: str, k: _SessionKey) -> Dict[str, str]:
    return {
        "session_id": session_id,
        "public_key_b64": k.pub_b64,
        "public_key_sha256": k.pub_sha256,
        "pid": str(k.pid),
        "proc_start_time": f"{k.proc_start_time:.6f}",
        "code_sha": k.code_sha,
        "code_version": k.code_version,
        "started_at_utc": f"{k.started_at_utc:.6f}",
    }


def has_session(session_id: str) -> bool:
    """Return True iff an active (non-terminated) key exists for session_id."""
    with _LOCK:
        k = _KEYS.get(session_id)
        return k is not None and not k.terminated


def get_public_evidence(session_id: str) -> Optional[Dict[str, str]]:
    """Return public evidence for session_id, or None if no active key."""
    with _LOCK:
        k = _KEYS.get(session_id)
        if k is None or k.terminated:
            return None
        return _public_evidence(session_id, k)


def terminate_session(session_id: str) -> bool:
    """Mark the session as terminated and destroy the private key.

    After this call, has_session() returns False, get_public_evidence()
    returns None, and sign_for_session() rejects.

    Returns True iff a live key was destroyed.
    """
    with _LOCK:
        k = _KEYS.get(session_id)
        if k is None or k.terminated:
            return False
        # Best-effort: overwrite the private key reference.
        # Python does not guarantee memory erasure, but we drop the reference.
        k.priv = None  # type: ignore[assignment]
        k.terminated = True
        return True


def inject_freshness_challenge(session_id: str, challenge: str) -> bool:
    """Inject an externally-generated unpredictable nonce into the session.

    The challenge is stored in-memory only and will be included in the
    next signed canonical structure.

    Returns True iff the session exists and is not terminated.
    """
    with _LOCK:
        k = _KEYS.get(session_id)
        if k is None or k.terminated:
            return False
        k.last_freshness_challenge = challenge
        return True


def _canonical_payload(
    session_id: str,
    freshness_challenge: Optional[str],
    previous_stage_fingerprint: Optional[str],
    artifact_fingerprint: str,
    monotonic_seq: int,
) -> bytes:
    """Build a canonical byte string for signing (RFC 8785 JCS-strict)."""
    obj = {
        "schema_id": "TGE-EPHEMERAL-SESSION-PROVENANCE/0.1",
        "session_id": session_id,
        "freshness_challenge": freshness_challenge,
        "previous_stage_fingerprint": previous_stage_fingerprint,
        "artifact_fingerprint": artifact_fingerprint,
        "monotonic_seq": monotonic_seq,
    }
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def sign_for_session(
    session_id: str,
    artifact_fingerprint: str,
    *,
    previous_stage_fingerprint: Optional[str] = None,
    freshness_challenge: Optional[str] = None,
) -> Optional[Dict[str, str]]:
    """Sign a canonical provenance payload using the session's private key.

    The signature covers:
      session_id
      freshness_challenge (if injected; else None)
      previous_stage_fingerprint (caller-supplied; else None)
      artifact_fingerprint (caller-supplied)
      monotonic_seq (per-session, monotonically increasing)

    Returns:
        dict with payload + signature_b64 + public_key_b64 on success.
        None if session does not exist, has terminated, or private key
        has been destroyed.

    Raises:
        ValueError if session_id does not match a known active session.
    """
    if not is_enabled():
        return None
    with _LOCK:
        k = _KEYS.get(session_id)
        if k is None:
            raise ValueError(f"unknown_session:{session_id!r}")
        if k.terminated:
            raise ValueError(f"session_terminated:{session_id!r}")
        if k.priv is None:
            raise ValueError(f"session_key_destroyed:{session_id!r}")
        # Use the injected challenge if the caller did not supply one
        challenge = freshness_challenge
        if challenge is None:
            challenge = k.last_freshness_challenge
        # Allocate monotonic seq
        k.monotonic_seq += 1
        seq = k.monotonic_seq
        priv = k.priv
        pub_b64 = k.pub_b64
        pub_sha = k.pub_sha256

    payload = _canonical_payload(
        session_id=session_id,
        freshness_challenge=challenge,
        previous_stage_fingerprint=previous_stage_fingerprint,
        artifact_fingerprint=artifact_fingerprint,
        monotonic_seq=seq,
    )
    sig = priv.sign(payload)
    sig_b64 = base64.b64encode(sig).decode("ascii")

    return {
        "schema_id": "TGE-EPHEMERAL-SESSION-PROVENANCE/0.1",
        "session_id": session_id,
        "freshness_challenge": challenge,
        "previous_stage_fingerprint": previous_stage_fingerprint,
        "artifact_fingerprint": artifact_fingerprint,
        "monotonic_seq": seq,
        "payload_canonical_b64": base64.b64encode(payload).decode("ascii"),
        "signature_b64": sig_b64,
        "public_key_b64": pub_b64,
        "public_key_sha256": pub_sha,
    }


def verify_signature(
    session_id: str,
    signed_payload: Dict[str, str],
    *,
    public_key_b64: Optional[str] = None,
) -> bool:
    """Verify a signed_payload dict's signature against the session's key.

    If public_key_b64 is provided, uses that key (for cross-process
    verification with externally captured evidence). Otherwise uses the
    in-memory key.

    Returns True iff signature verifies AND session_id matches.
    """
    try:
        payload_bytes = base64.b64decode(signed_payload["payload_canonical_b64"])
        sig = base64.b64decode(signed_payload["signature_b64"])
        if public_key_b64 is None:
            with _LOCK:
                k = _KEYS.get(session_id)
                if k is None or k.terminated:
                    return False
                pub = Ed25519PublicKey.from_public_bytes(
                    base64.b64decode(k.pub_b64)
                )
        else:
            pub = Ed25519PublicKey.from_public_bytes(
                base64.b64decode(public_key_b64)
            )
        if signed_payload.get("session_id") != session_id:
            return False
        pub.verify(sig, payload_bytes)
        return True
    except Exception:
        return False


# ---- Self-test ----

def _selftest() -> int:
    """Run a minimal deterministic self-test of the primitive.

    Returns 0 on success, 1 on failure.
    """
    # Enable the primitive (force-on for self-test).
    global _ENABLED
    _ENABLED = True

    print("=== ephemeral_session_id_poc self-test ===")

    session_a = "selftest_session_A"
    session_b = "selftest_session_B"

    # 1. distinct sessions receive distinct public keys
    ev_a = setup_for_session(session_a)
    ev_b = setup_for_session(session_b)
    assert ev_a is not None and ev_b is not None, "setup_for_session returned None"
    assert ev_a["public_key_sha256"] != ev_b["public_key_sha256"], "keys not distinct"
    assert ev_a["public_key_b64"] != ev_b["public_key_b64"], "public keys not distinct"
    print("[PASS] distinct sessions receive distinct public keys")

    # 2. private key material is not persisted (we never write to disk;
    #    check that _KEYS holds only in memory)
    # We can't introspect memory, but we can assert the public evidence
    # does not contain private material:
    assert "private" not in ev_a, "private material leaked in evidence"
    assert "priv" not in ev_a, "private material leaked in evidence"
    print("[PASS] private key material is not in public evidence")

    # 3. correct session can sign
    signed = sign_for_session(
        session_a,
        artifact_fingerprint="sha256:abc123",
        previous_stage_fingerprint="sha256:prev",
    )
    assert signed is not None, "sign_for_session returned None for valid session"
    assert signed["session_id"] == session_a
    print("[PASS] correct session can sign")

    # 4. another session cannot sign with the first session's key
    #    (verify: signing under session_b's key produces a different signature)
    signed_b = sign_for_session(
        session_b,
        artifact_fingerprint="sha256:abc123",
        previous_stage_fingerprint="sha256:prev",
    )
    assert signed_b["signature_b64"] != signed["signature_b64"], \
        "session_b signature equals session_a signature"
    # And verify: session_a's signature does not verify under session_b's public key
    assert not verify_signature(session_a, signed, public_key_b64=ev_b["public_key_b64"]), \
        "session_a signature verified under session_b's public key (FAIL)"
    print("[PASS] another session cannot verify with the first session's key")

    # 5. terminated session cannot sign
    assert terminate_session(session_a), "terminate_session returned False"
    try:
        sign_for_session(session_a, artifact_fingerprint="sha256:after_term")
        print("[FAIL] sign_for_session succeeded after termination")
        return 1
    except ValueError as e:
        if "session_terminated" in str(e) or "session_key_destroyed" in str(e):
            print("[PASS] terminated session cannot sign")
        else:
            print(f"[FAIL] unexpected ValueError: {e}")
            return 1

    # 6. signatures verify against externally captured public key
    signed_b2 = sign_for_session(
        session_b,
        artifact_fingerprint="sha256:external_verify",
        previous_stage_fingerprint="sha256:ext_prev",
    )
    assert signed_b2 is not None
    # Externally capture the public key (this simulates the operator
    # reading the startup evidence line) and verify
    assert verify_signature(session_b, signed_b2, public_key_b64=ev_b["public_key_b64"]), \
        "signature did not verify against externally captured public key"
    print("[PASS] signatures verify against externally captured public key")

    # 7. a fresh external nonce can be included in the signed payload
    nonce = "nonce_" + hashlib.sha256(os.urandom(32)).hexdigest()[:16]
    assert inject_freshness_challenge(session_b, nonce), \
        "inject_freshness_challenge returned False"
    signed_b3 = sign_for_session(
        session_b,
        artifact_fingerprint="sha256:with_nonce",
        previous_stage_fingerprint="sha256:ext_prev",
    )
    assert signed_b3 is not None
    assert signed_b3["freshness_challenge"] == nonce, \
        f"freshness_challenge not in signed payload: got {signed_b3['freshness_challenge']!r}"
    # Also verify that the nonce is part of the signed bytes (not appended after)
    payload_bytes = base64.b64decode(signed_b3["payload_canonical_b64"])
    assert nonce.encode("utf-8") in payload_bytes, \
        "freshness challenge not in canonical payload bytes"
    print("[PASS] fresh external nonce included in signed payload")

    # Cleanup
    terminate_session(session_b)
    print()
    print("=== ALL SELFTESTS PASSED ===")
    return 0


def _main(argv: list) -> int:
    """Minimal CLI entry: hermes session-key-prove {setup|sign|verify|inject|terminate|show|selftest}"""
    if len(argv) < 2:
        print("Usage: hermes session-key-prove {selftest|setup|sign|verify|inject|terminate|show}")
        return 2
    cmd = argv[1]
    if cmd == "selftest":
        return _selftest()
    elif cmd == "setup":
        if len(argv) < 3:
            print("Usage: hermes session-key-prove setup <session_id>")
            return 2
        ev = setup_for_session(argv[2])
        if ev is None:
            print("disabled (set experimental.ephemeral_session_identity: true in config.yaml)")
            return 1
        print(json.dumps(ev, sort_keys=True, indent=2))
        return 0
    elif cmd == "sign":
        if len(argv) < 4:
            print("Usage: hermes session-key-prove sign <session_id> <artifact_fingerprint> [previous_stage_fingerprint]")
            return 2
        session_id = argv[2]
        af = argv[3]
        prev = argv[4] if len(argv) > 4 else None
        try:
            signed = sign_for_session(session_id, af, previous_stage_fingerprint=prev)
        except ValueError as e:
            print(f"error: {e}")
            return 1
        if signed is None:
            print("disabled")
            return 1
        print(json.dumps(signed, sort_keys=True, indent=2))
        return 0
    elif cmd == "verify":
        if len(argv) < 3:
            print("Usage: hermes session-key-prove verify <session_id> <signed_payload.json> [public_key_b64]")
            return 2
        session_id = argv[2]
        payload_file = argv[3]
        with open(payload_file) as f:
            signed = json.load(f)
        pub_b64 = argv[4] if len(argv) > 4 else None
        ok = verify_signature(session_id, signed, public_key_b64=pub_b64)
        print("OK" if ok else "FAIL")
        return 0 if ok else 1
    elif cmd == "inject":
        if len(argv) < 4:
            print("Usage: hermes session-key-prove inject <session_id> <challenge>")
            return 2
        ok = inject_freshness_challenge(argv[2], argv[3])
        print("OK" if ok else "FAIL")
        return 0 if ok else 1
    elif cmd == "terminate":
        if len(argv) < 3:
            print("Usage: hermes session-key-prove terminate <session_id>")
            return 2
        ok = terminate_session(argv[2])
        print("OK" if ok else "FAIL")
        return 0 if ok else 1
    elif cmd == "show":
        if len(argv) < 3:
            print("Usage: hermes session-key-prove show <session_id>")
            return 2
        ev = get_public_evidence(argv[2])
        if ev is None:
            print("not found / terminated")
            return 1
        print(json.dumps(ev, sort_keys=True, indent=2))
        return 0
    else:
        print(f"unknown command: {cmd}")
        return 2


if __name__ == "__main__":
    sys.exit(_main(sys.argv))

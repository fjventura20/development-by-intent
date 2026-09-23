# Ephemeral Session Identity Primitive — Security-Claim Clarification (Amendment)

**Status:** NON-DESTRUCTIVE AMENDMENT ONLY. Does NOT modify any frozen or installed artifact.
**Date:** 2026-09-14
**Authority:** Frank Ventura (PI), per directive of 2026-09-14.

The original implementation artifact
`architecture/experimental/live-provenance-poc/EPHEMERAL-SESSION-IDENTITY-PRIMITIVE-v0.1.md`
(SHA-256 `82725296f41dece0669d5aac6073748ae425af4c45bcb64f80cb12ec5308edab`) is
preserved byte-identically.

This amendment corrects one security-claim inconsistency identified by the PI.

## 1. Inconsistency identified

The original closeout listed as "What this primitive protects against":

> - A separate same-user process fabricating Hermes session artifacts
>   without possession of the in-process ephemeral private key.
> - A same-user process attempting to sign artifacts claiming to be from a
>   session it does not control.
> - Cross-session signature replay: signing a payload under session_a's
>   key, then attempting to verify it as session_b's.

The original closeout also listed as out of scope:

> - Memory extraction / debugging of the Hermes process.

The PI correctly observed that "In-process key extraction by separate process" was
implicitly listed as protected but is functionally equivalent to memory extraction —
both require the attacker to read or coerce the running process's memory space.
This is out of scope per the explicit trust boundary in the directive.

## 2. Corrected supported claim

The supported claim is now narrowed to:

> A separate process cannot forge valid session provenance merely by
> fabricating Hermes session files, metadata, session IDs, or gateway records
> without possession of the session's ephemeral private key.

## 3. Explicitly out of scope (clarified)

The primitive does NOT protect against:

- Process-memory extraction by a separate (same-user) process.
- Debugger / ptrace access to the Hermes process.
- Arbitrary process compromise that obtains read access to the running
  Hermes process's memory.
- Side-channel attacks on Ed25519 itself (Ed25519 is constant-time by design).
- Host-level process impersonation.
- Root / administrator compromise.
- A maliciously modified Hermes binary.
- Cross-version replay of a signed payload (limitation; would require
  binding `code_version` into the signed payload).

## 4. Note on physical memory zeroization

The primitive's `terminate_session(session_id)` clears the in-memory reference
to the private key (`_KEYS[session_id].priv = None`). Python does not
guarantee that the underlying memory is physically zeroed; OS-level
memory scrubbing is OUT OF SCOPE per the explicit trust boundary in the
PI directive.

The runtime boundary that IS guaranteed: `sign_for_session` for a
terminated session raises `ValueError("session_terminated:...")`. The
runtime no longer exposes a signing capability for the terminated
session. Physical proof of memory zeroization is NOT claimed.

## 5. Files

This amendment is at:
`architecture/experimental/live-provenance-poc/EPHEMERAL-SESSION-IDENTITY-CLAIM-AMENDMENT-v0.1.md`

The original closeout is preserved byte-identically (SHA-256 above).

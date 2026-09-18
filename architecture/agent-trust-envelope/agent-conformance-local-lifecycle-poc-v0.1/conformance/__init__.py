"""Agent Conformance Local Lifecycle PoC v0.1 — implementation package.

This package implements the local deterministic proof of conformance
invalidation, stale-capability denial, re-attestation, restoration, and
audit continuity exactly as specified in the frozen v0.1.1 design:

  AGENT-CONFORMANCE-LOCAL-LIFECYCLE-POC-v0.1.1-DESIGN.md
  blob SHA: 4faea2a16261ca9416fe8bb4eceaaff80593eb59

The implementation is local, deterministic, and self-contained:
  - no network
  - no external API
  - no external LLM
  - fixed subject/role/domain identifiers
  - deterministic canonical serialization (UTF-8, NFC, lex-sorted keys)
  - deterministic Ed25519 signing with explicit domain separation

The formal scored run is NOT executed by this package. The package
exposes only the deterministic components; tests drive them through
the 18 required cases and 8 negative security cases.
"""

from . import audit
from . import authorization
from . import canonical
from . import crypto
from . import evaluator
from . import executor
from . import lifecycle
from . import models
from . import profile_registry
from . import state
from . import trigger

__all__ = [
    "audit",
    "authorization",
    "canonical",
    "crypto",
    "evaluator",
    "executor",
    "lifecycle",
    "models",
    "profile_registry",
    "state",
    "trigger",
]
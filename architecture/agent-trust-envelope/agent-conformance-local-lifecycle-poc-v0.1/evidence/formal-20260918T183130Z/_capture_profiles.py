"""Formal run: emit predeclared profile v1/v2 artifacts and digests.

This script is run ONCE at formal-run start to capture the
predeclared profile state as evidence. It then prints the
deterministic digests that must remain unchanged throughout the
formal run.

It does NOT mutate any test or implementation file.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
# Evidence dir is ROOT/evidence/formal-... so the PoC source tree is
# ROOT itself (where fixtures/ and conformance/ live).
sys.path.insert(0, str(ROOT))

from fixtures import bootstrap
from conformance.canonical import canonical_sha256


def main() -> None:
    h = bootstrap.build_harness(prefix="formal-preflight")
    try:
        # v1 / v2 profiles are already signed and registered by
        # build_harness(). Capture them as JSON evidence.
        v1 = h.profile_v1
        v2 = h.profile_v2

        v1_payload = {
            "artifact_id": v1.artifact_id,
            "profile_id": v1.profile_id,
            "profile_version": v1.profile_version,
            "trust_domain": v1.trust_domain,
            "role_id": v1.role_id,
            "required_runtime_version": v1.required_runtime_version,
            "max_conformance_age": v1.max_conformance_age,
            "whole_role_failure": v1.whole_role_failure,
            "evaluator_authority": v1.evaluator_authority,
            "lifecycle_state_authority": v1.lifecycle_state_authority,
            "artifact_digest": v1.artifact_digest,
            "signature_hex": v1.signature.hex(),
            "signature_domain": v1.signature_domain,
        }
        v2_payload = {
            "artifact_id": v2.artifact_id,
            "profile_id": v2.profile_id,
            "profile_version": v2.profile_version,
            "trust_domain": v2.trust_domain,
            "role_id": v2.role_id,
            "required_runtime_version": v2.required_runtime_version,
            "max_conformance_age": v2.max_conformance_age,
            "whole_role_failure": v2.whole_role_failure,
            "evaluator_authority": v2.evaluator_authority,
            "lifecycle_state_authority": v2.lifecycle_state_authority,
            "artifact_digest": v2.artifact_digest,
            "signature_hex": v2.signature.hex(),
            "signature_domain": v2.signature_domain,
        }

        out = ROOT / "evidence" / "formal-20260918T183130Z"
        out.mkdir(parents=True, exist_ok=True)

        (out / "profile_v1.json").write_text(
            json.dumps(v1_payload, indent=2, sort_keys=True) + "\n"
        )
        (out / "profile_v2.json").write_text(
            json.dumps(v2_payload, indent=2, sort_keys=True) + "\n"
        )

        # Recompute canonical signing-payload digest (defense in depth)
        v1_sp_digest = canonical_sha256(v1.signing_payload())
        v2_sp_digest = canonical_sha256(v2.signing_payload())

        print("PROFILE_V1_DIGEST=" + v1.artifact_digest)
        print("PROFILE_V1_SIGNING_PAYLOAD_DIGEST=" + v1_sp_digest)
        print("PROFILE_V2_DIGEST=" + v2.artifact_digest)
        print("PROFILE_V2_SIGNING_PAYLOAD_DIGEST=" + v2_sp_digest)
        # Confirm registry holds both before run start. The registry
        # is installed on state_store (per the cfd85e8 design).
        print("REGISTRY_REGISTERED=" + ",".join(
            h.state_store._profile_registry.registered_ids()
        ))
        print("REGISTRY_SIGNER_KEY_ID=" + h.state_store._profile_registry.signer_key_id)
    finally:
        bootstrap.teardown(h)


if __name__ == "__main__":
    main()

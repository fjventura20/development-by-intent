"""Runtime-signing stub.

This is NOT a real agent runtime. It does NOT invoke an AI model. It
produces signed acceptance receipts based on the input envelope.

Per v0.2.1 §J.0.3: zero participant invocations, zero model calls.

The runtime has:
- a runtime_fingerprint (deterministic from the binary identity)
- a runtime-resident Ed25519 signing key
- the ability to produce a fixture swtpm quote (via attestation.make_quote)
- the ability to sign an acceptance receipt
- the ability to sign per-turn envelopes

The runtime also exposes:
- bind(envelope) -> acceptance receipt
- emit_turn(...) -> turn envelope
- a function that the verifier can call to test runtime substitution
"""
import time
import base64
import hashlib

from canonicalization import canonicalize, canonical_hash
from crypto_utils import (
    Ed25519PrivateKey, Ed25519PublicKey,
    signature_b64, public_key_bytes, public_key_b64,
)
from attestation import make_quote


class RuntimeStub:
    """A deterministic runtime-signing stub."""

    def __init__(
        self,
        *,
        runtime_id: str,
        runtime_priv: Ed25519PrivateKey,
        runtime_pub: Ed25519PublicKey,
        runtime_fingerprint: str,
        manufacturer_root_priv: Ed25519PrivateKey,
        manufacturer_root_pub: Ed25519PublicKey,
        tpm_ak_priv: Ed25519PrivateKey,
        tpm_ak_pub: Ed25519PublicKey,
    ):
        self.runtime_id = runtime_id
        self.runtime_priv = runtime_priv
        self.runtime_pub = runtime_pub
        self.runtime_fingerprint = runtime_fingerprint
        self.manufacturer_root_priv = manufacturer_root_priv
        self.manufacturer_root_pub = manufacturer_root_pub
        self.tpm_ak_priv = tpm_ak_priv
        self.tpm_ak_pub = tpm_ak_pub

        # Build the initial attestation quote
        self.runtime_pub_bytes = public_key_bytes(runtime_pub)
        self.quote = make_quote(
            runtime_fingerprint=runtime_fingerprint,
            signing_key_pub=self.runtime_pub_bytes,
            manufacturer_root_priv=manufacturer_root_priv,
            tpm_ak_priv=tpm_ak_priv,
        )

    def bind(self, envelope: dict, *, session_id: str, nonce_freshness: str, verifier_challenge: str) -> dict:
        """Produce a signed acceptance receipt per v0.2.1 §B.4.

        Acceptance receipt is signed over the canonicalized subset per
        v0.2.1 §E.2.3:
          receipt_id, charter_id, charter_sha256, session_id,
          runtime_fingerprint, attestation_quote_b64, nonce_freshness,
          accepted_at_utc_verified, receipt_issuer_signature_chain_b64
        """
        receipt_id = canonical_hash({
            "envelope_id": envelope["envelope_id"],
            "session_id": session_id,
            "nonce": nonce_freshness,
        })[:32]

        # The receipt chain links to the envelope's issuer signature
        # (we just reference its hash; in production this would be
        # the actual signature; for PoC the hash suffices)
        receipt_issuer_signature_chain_b64 = base64.b64encode(
            canonical_hash(envelope).encode('utf-8')
        ).decode('ascii')

        receipt_unsigned = {
            "receipt_id": receipt_id,
            "charter_id": envelope["charter"]["charter_id"],
            "charter_sha256": envelope["charter"]["charter_sha256"],
            "session_id": session_id,
            "runtime_fingerprint": self.runtime_fingerprint,
            "attestation_quote_b64": base64.b64encode(
                canonicalize(self.quote)
            ).decode('ascii'),
            "nonce_freshness": nonce_freshness,
            "accepted_at_utc_verified": int(time.time()),
            "receipt_issuer_signature_chain_b64": receipt_issuer_signature_chain_b64,
            "verifier_challenge": verifier_challenge,
        }
        # Sign canonicalized receipt unsigned fields (excluding the signature itself)
        signed_region = {
            "receipt_id": receipt_unsigned["receipt_id"],
            "charter_id": receipt_unsigned["charter_id"],
            "charter_sha256": receipt_unsigned["charter_sha256"],
            "session_id": receipt_unsigned["session_id"],
            "runtime_fingerprint": receipt_unsigned["runtime_fingerprint"],
            "attestation_quote_b64": receipt_unsigned["attestation_quote_b64"],
            "nonce_freshness": receipt_unsigned["nonce_freshness"],
            "accepted_at_utc_verified": receipt_unsigned["accepted_at_utc_verified"],
            "receipt_issuer_signature_chain_b64": receipt_unsigned["receipt_issuer_signature_chain_b64"],
            "verifier_challenge": receipt_unsigned["verifier_challenge"],
        }
        receipt_bytes = canonicalize(signed_region)
        receipt_unsigned["acceptance_receipt_signature_b64"] = signature_b64(
            self.runtime_priv, receipt_bytes
        )
        receipt_unsigned["runtime_pubkey_b64"] = public_key_b64(self.runtime_pub)
        return receipt_unsigned

    def emit_turn(
        self,
        *,
        receipt: dict,
        turn_index: int,
        executed_action: str,
        previous_turn_envelope_sha256 = None,
        # Optional override for runtime-substitution testing
        override_runtime_priv = None,
        override_runtime_fingerprint = None,
        override_quote = None,
    ) -> dict:
        """Produce a per-turn envelope per v0.2.1 §G.1.1."""
        priv = override_runtime_priv if override_runtime_priv is not None else self.runtime_priv
        fp = override_runtime_fingerprint if override_runtime_fingerprint is not None else self.runtime_fingerprint
        if override_quote is not None:
            quote_b64 = base64.b64encode(canonicalize(override_quote)).decode('ascii')
        else:
            quote_b64 = base64.b64encode(canonicalize(self.quote)).decode('ascii')

        turn = {
            "session_id": receipt["session_id"],
            "turn_index": turn_index,
            "accepted_charter_sha256": receipt["charter_sha256"],
            "runtime_fingerprint": fp,
            "attestation_quote_b64": quote_b64,
            "executed_action": executed_action,
            "timestamp_utc": int(time.time()),
        }
        if previous_turn_envelope_sha256 is not None:
            turn["previous_turn_envelope_sha256"] = previous_turn_envelope_sha256
        # Sign the turn envelope (canonical form)
        turn_bytes = canonicalize(turn)
        turn["turn_envelope_signature_b64"] = signature_b64(priv, turn_bytes)
        return turn


def make_runtime(*, runtime_id: str = "rt-001", manufacturer_root_priv=None, manufacturer_root_pub=None, tpm_ak_priv=None, tpm_ak_pub=None) -> RuntimeStub:
    """Convenience: build a complete RuntimeStub with all keys.

    If manufacturer_root and tpm_ak keypairs are not provided, fresh ones are
    generated. The caller is responsible for passing these to the verifier so
    the verifier can validate quotes against them.
    """
    from crypto_utils import generate_keypair
    runtime_priv, runtime_pub = generate_keypair()
    rt_fp = hashlib.sha256(f"runtime-binary:{runtime_id}".encode('utf-8')).hexdigest()
    if manufacturer_root_priv is None or manufacturer_root_pub is None:
        mfr_priv, mfr_pub = generate_keypair()
    else:
        mfr_priv, mfr_pub = manufacturer_root_priv, manufacturer_root_pub
    if tpm_ak_priv is None or tpm_ak_pub is None:
        ak_priv, ak_pub = generate_keypair()
    else:
        ak_priv, ak_pub = tpm_ak_priv, tpm_ak_pub
    return RuntimeStub(
        runtime_id=runtime_id,
        runtime_priv=runtime_priv,
        runtime_pub=runtime_pub,
        runtime_fingerprint=rt_fp,
        manufacturer_root_priv=mfr_priv,
        manufacturer_root_pub=mfr_pub,
        tpm_ak_priv=ak_priv,
        tpm_ak_pub=ak_pub,
    )

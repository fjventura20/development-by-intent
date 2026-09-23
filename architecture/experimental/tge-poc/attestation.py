"""Fixture-shape swtpm attestation quote with PCR binding to runtime_fingerprint.

Per v0.2.1 §B.3.3:
- B.3.3.1: PCRs MUST measure the runtime binary AND signing-key handle.
- B.3.3.2: verifier MUST compute expected PCR values from runtime_fingerprint.
- B.3.3.3: verifier MUST reject PCR-value mismatch.
- B.3.3.5: valid quote + substituted runtime key MUST fail.

Attestation-label discipline (v0.2.1 §J.0.4): this is FIXTURE_ATTESTATION
(A1). It is NOT hardware-rooted. It is NOT production trust. It is a
test fixture that produces bytes shaped like a swtpm quote.

The "manufacturer root" is a fixture key (Ed25519). The "swtpm AK"
(attestation key) is a fixture key whose public key is part of the
attestation chain.

Quote structure (fixture-shape):
{
    "quote_format": "TGE-POC-A1",
    "runtime_fingerprint": <hex>,
    "signing_key_handle_b64": <base64 of pubkey>,
    "pcrs": { "pcr0": <hex>, "pcr1": <hex> },  # PCR0 = runtime binary digest, PCR1 = signing-key handle digest
    "manufacturer_root_signature_b64": <signs canonicalize(quote without sig)>,
    "tpm_ak_signature_b64": <signs canonicalize(quote without sig)>
}

For the PoC, the manufacturer_root_signature and tpm_ak_signature
are both Ed25519 (the PoC uses one curve throughout). In a real
deployment they would be different algorithms. This is documented as
A1, simulated.
"""
import hashlib

from canonicalization import canonicalize
from crypto_utils import Ed25519PrivateKey, Ed25519PublicKey, signature_b64, verify_signature


def derive_pcrs(runtime_fingerprint: str, signing_key_pub: bytes) -> dict:
    """Derive PCR values from runtime_fingerprint and signing-key handle.

    This is the deterministic mapping defined by v0.2.1 §B.3.3.2.

    PCR0 = SHA-256(runtime_fingerprint || domain_tag_pcr0)
    PCR1 = SHA-256(signing_key_pub || domain_tag_pcr1)

    Domain tags prevent cross-pollination between PCR0 and PCR1.
    """
    pcr0 = hashlib.sha256(
        runtime_fingerprint.encode('utf-8') + b"|TGE-POC-A1|PCR0|runtime_binary"
    ).hexdigest()
    pcr1 = hashlib.sha256(
        signing_key_pub + b"|TGE-POC-A1|PCR1|signing_key_handle"
    ).hexdigest()
    return {"pcr0": pcr0, "pcr1": pcr1}


def expected_pcrs(runtime_fingerprint: str, signing_key_pub: bytes) -> dict:
    """Same as derive_pcrs; exposed as a separate name for the verifier side."""
    return derive_pcrs(runtime_fingerprint, signing_key_pub)


def make_quote(
    runtime_fingerprint: str,
    signing_key_pub: bytes,
    manufacturer_root_priv: Ed25519PrivateKey,
    tpm_ak_priv: Ed25519PrivateKey,
) -> dict:
    """Produce a fixture-shape attestation quote."""
    pcrs = derive_pcrs(runtime_fingerprint, signing_key_pub)
    quote = {
        "quote_format": "TGE-POC-A1",
        "runtime_fingerprint": runtime_fingerprint,
        "signing_key_handle_b64": __import__('base64').b64encode(signing_key_pub).decode('ascii'),
        "pcrs": pcrs,
    }
    quote_bytes = canonicalize(quote)
    quote["manufacturer_root_signature_b64"] = signature_b64(manufacturer_root_priv, quote_bytes)
    quote["tpm_ak_signature_b64"] = signature_b64(tpm_ak_priv, quote_bytes)
    return quote


def verify_quote(quote: dict, manufacturer_root_pub: Ed25519PublicKey, tpm_ak_pub: Ed25519PublicKey) -> dict:
    """Verify a fixture-shape attestation quote.

    Returns a dict { ok: bool, reason: str }.
    Per v0.2.1 §B.3.3.3, PCR values MUST match expected_pcrs for the
    claimed runtime_fingerprint and signing_key_handle_b64.
    """
    import base64
    quote_without_sigs = {
        "quote_format": quote["quote_format"],
        "runtime_fingerprint": quote["runtime_fingerprint"],
        "signing_key_handle_b64": quote["signing_key_handle_b64"],
        "pcrs": quote["pcrs"],
    }
    quote_bytes = canonicalize(quote_without_sigs)

    # 1. Manufacturer root signature verifies?
    if not verify_signature(manufacturer_root_pub, quote_bytes, quote["manufacturer_root_signature_b64"]):
        return {"ok": False, "reason": "manufacturer_root_signature_invalid"}

    # 2. TPM AK signature verifies?
    if not verify_signature(tpm_ak_pub, quote_bytes, quote["tpm_ak_signature_b64"]):
        return {"ok": False, "reason": "tpm_ak_signature_invalid"}

    # 3. PCR values match expected for the claimed runtime_fingerprint + signing_key_handle
    signing_key_pub = base64.b64decode(quote["signing_key_handle_b64"])
    expected = expected_pcrs(quote["runtime_fingerprint"], signing_key_pub)
    for pcr_name, expected_val in expected.items():
        if quote["pcrs"].get(pcr_name) != expected_val:
            return {"ok": False, "reason": f"pcr_mismatch:{pcr_name}"}

    return {"ok": True, "reason": ""}

"""Verifier module for the TGE-PoC.

Per v0.2.1, the verifier is responsible for:
- canonicalization consistency with the signer (uses canonicalization.canonicalize)
- envelope signature verification (issuer signature)
- roster verification (RTA signature)
- charter SHA-256 match
- attestation quote verification (manufacturer root + TPM AK + PCR check)
- acceptance receipt signature verification (runtime signature)
- acceptance receipt cross-reference to envelope
- per-turn continuity check
- freshness window check (verifier-controlled)
- provenance distinction (envelope vs inline)
- collocation detection (in-process vs out-of-process; in PoC, controlled
  by the `verifier_inside_participant_host` flag, defaulting to False)

The verifier returns a verdict object:
{
    "verdict": "PASS" | "STOP",
    "stop_code": "" | "GX_...",
    "g_assurance": "G0".."G5",
    "a_assurance": "A0".."A3",
    "assurance_tuple": "Gn/Am",
    "details": {...}
}
"""
import time
import base64

from canonicalization import canonicalize, canonical_hash
from crypto_utils import (
    Ed25519PublicKey,
    verify_signature,
    load_public_key_from_b64,
)
from attestation import verify_quote


# Default verifier-controlled freshness window in seconds
DEFAULT_FRESHNESS_WINDOW = 60


class Verifier:
    """The structural verifier. No external service calls."""

    def __init__(
        self,
        *,
        roster: dict,
        rta_pub: Ed25519PublicKey,
        manufacturer_root_pub: Ed25519PublicKey,
        tpm_ak_pub: Ed25519PublicKey,
        freshness_window: int = DEFAULT_FRESHNESS_WINDOW,
        # Set True if the verifier is running in the same process as the
        # runtime/participant. Default False (out-of-band). Cases that test
        # Case 4 set this True.
        verifier_inside_participant_host: bool = False,
        # The verifier's own clock for freshness evaluation
        verifier_now = None,
    ):
        self.roster = roster
        self.rta_pub = rta_pub
        self.manufacturer_root_pub = manufacturer_root_pub
        self.tpm_ak_pub = tpm_ak_pub
        self.freshness_window = freshness_window
        self.verifier_inside_participant_host = verifier_inside_participant_host
        if verifier_now is None:
            verifier_now = int(time.time())
        self.verifier_now = verifier_now

    # --- Roster check (v0.2 §D.3) ---

    def _roster_check(self, envelope: dict) -> dict:
        # 1. RTA signature on roster
        roster_signed = {
            "roster_id": self.roster["roster_id"],
            "roster_version": self.roster["roster_version"],
            "issued_at_utc": self.roster["issued_at_utc"],
            "issuers": self.roster["issuers"],
            "rta_pubkey_b64": self.roster["rta_pubkey_b64"],
        }
        roster_bytes = canonicalize(roster_signed)
        if not verify_signature(self.rta_pub, roster_bytes, self.roster["rta_signature_b64"]):
            return {"ok": False, "reason": "roster_signature_invalid"}
        # 2. Issuer on roster?
        issuer_id = envelope["issuer"]["issuer_id"]
        issuer_pubkey_b64 = envelope["issuer"]["issuer_pubkey_b64"]
        now = self.verifier_now
        for entry in self.roster["issuers"]:
            if entry["issuer_id"] == issuer_id and entry["issuer_pubkey_b64"] == issuer_pubkey_b64:
                if entry["valid_from_utc"] <= now <= entry["valid_until_utc"]:
                    return {"ok": True, "reason": "issuer_admitted"}
                else:
                    return {"ok": False, "reason": "issuer_window_invalid"}
        return {"ok": False, "reason": "issuer_not_on_roster"}

    # --- Envelope signature + charter integrity ---

    def _envelope_check(self, envelope: dict) -> dict:
        signed_region = {
            "envelope_id": envelope["envelope_id"],
            "envelope_version": envelope["envelope_version"],
            "issuer": envelope["issuer"],
            "charter": envelope["charter"],
            "binding": envelope["binding"],
        }
        envelope_bytes = canonicalize(signed_region)
        try:
            issuer_pub = load_public_key_from_b64(envelope["issuer"]["issuer_pubkey_b64"])
        except Exception as e:
            return {"ok": False, "reason": f"issuer_pubkey_decode:{e}"}
        if not verify_signature(issuer_pub, envelope_bytes, envelope["envelope_issuer_signature_b64"]):
            return {"ok": False, "reason": "envelope_signature_invalid"}
        # Charter canonical bytes must match charter_sha256
        charter_canonical_bytes = base64.b64decode(envelope["charter"]["charter_canonical_bytes_b64"])
        actual_charter_sha = canonical_hash(__import__('json').loads(charter_canonical_bytes.decode('utf-8')))
        if actual_charter_sha != envelope["charter"]["charter_sha256"]:
            return {"ok": False, "reason": "charter_sha256_mismatch"}
        return {"ok": True, "reason": ""}

    # --- Acceptance receipt ---

    def _receipt_check(self, receipt: dict, envelope: dict) -> dict:
        # 1. Signature over canonicalized receipt fields (v0.2.1 §E.2.3)
        receipt_signed = {
            "receipt_id": receipt["receipt_id"],
            "charter_id": receipt["charter_id"],
            "charter_sha256": receipt["charter_sha256"],
            "session_id": receipt["session_id"],
            "runtime_fingerprint": receipt["runtime_fingerprint"],
            "attestation_quote_b64": receipt["attestation_quote_b64"],
            "nonce_freshness": receipt["nonce_freshness"],
            "accepted_at_utc_verified": receipt["accepted_at_utc_verified"],
            "receipt_issuer_signature_chain_b64": receipt["receipt_issuer_signature_chain_b64"],
            "verifier_challenge": receipt["verifier_challenge"],
        }
        receipt_bytes = canonicalize(receipt_signed)
        try:
            runtime_pub = load_public_key_from_b64(receipt["runtime_pubkey_b64"])
        except Exception as e:
            return {"ok": False, "reason": f"runtime_pubkey_decode:{e}"}
        if not verify_signature(runtime_pub, receipt_bytes, receipt["acceptance_receipt_signature_b64"]):
            return {"ok": False, "reason": "receipt_signature_invalid"}

        # 2. Cross-check receipt charter identity matches envelope
        if receipt["charter_id"] != envelope["charter"]["charter_id"]:
            return {"ok": False, "reason": "receipt_charter_id_mismatch"}
        if receipt["charter_sha256"] != envelope["charter"]["charter_sha256"]:
            return {"ok": False, "reason": "receipt_charter_sha_mismatch"}

        # 3. Receipt chain links to envelope signature
        expected_chain = base64.b64encode(
            canonical_hash(envelope).encode('utf-8')
        ).decode('ascii')
        if receipt["receipt_issuer_signature_chain_b64"] != expected_chain:
            return {"ok": False, "reason": "receipt_chain_mismatch"}

        # 4. Decode and verify the attestation quote
        quote_bytes = base64.b64decode(receipt["attestation_quote_b64"])
        quote = __import__('json').loads(quote_bytes.decode('utf-8'))
        qr = verify_quote(quote, self.manufacturer_root_pub, self.tpm_ak_pub)
        if not qr["ok"]:
            return {"ok": False, "reason": f"attestation_quote:{qr['reason']}"}

        # 5. PCR values must bind to runtime_fingerprint + signing_key_handle
        expected_pcr_runtime = quote["runtime_fingerprint"]
        if expected_pcr_runtime != receipt["runtime_fingerprint"]:
            return {"ok": False, "reason": "runtime_fingerprint_quote_mismatch"}
        # The signing_key_handle inside quote must be the runtime_pubkey
        from crypto_utils import public_key_bytes
        expected_handle_b64 = base64.b64encode(public_key_bytes(runtime_pub)).decode('ascii')
        if quote["signing_key_handle_b64"] != expected_handle_b64:
            return {"ok": False, "reason": "signing_key_handle_mismatch"}

        return {"ok": True, "reason": ""}

    # --- Turn continuity ---

    def _turn_check(self, turn: dict, receipt: dict) -> dict:
        # v0.2.1 §B.5: detect runtime replacement. We must check the
        # attestation quote's signing_key_handle against the receipt's
        # runtime_pubkey BEFORE checking the per-turn signature, so that
        # a substituted runtime key surfaces as GX_RUNTIME_REPLACED via
        # signing_key_handle_mismatch, not as GX_ATTESTATION_INVALID via
        # signature failure.

        # 1. Decode attestation quote and verify (manufacturer_root + tpm_ak)
        quote_bytes = base64.b64decode(turn["attestation_quote_b64"])
        quote = __import__('json').loads(quote_bytes.decode('utf-8'))
        qr = verify_quote(quote, self.manufacturer_root_pub, self.tpm_ak_pub)
        if not qr["ok"]:
            return {"ok": False, "reason": f"turn_attestation:{qr['reason']}"}

        # 2. Quote's signing_key_handle MUST equal receipt's runtime_pubkey
        try:
            receipt_runtime_pub = load_public_key_from_b64(receipt["runtime_pubkey_b64"])
        except Exception as e:
            return {"ok": False, "reason": f"runtime_pubkey_decode:{e}"}
        from crypto_utils import public_key_bytes
        expected_handle_b64 = base64.b64encode(public_key_bytes(receipt_runtime_pub)).decode('ascii')
        if quote["signing_key_handle_b64"] != expected_handle_b64:
            return {"ok": False, "reason": "runtime_replaced"}

        # 3. Quote's runtime_fingerprint MUST match receipt's runtime_fingerprint
        if quote["runtime_fingerprint"] != receipt["runtime_fingerprint"]:
            return {"ok": False, "reason": "runtime_replaced"}

        # 4. Turn signature verifies under the runtime's key
        turn_unsigned = {k: v for k, v in turn.items() if k != "turn_envelope_signature_b64"}
        turn_bytes = canonicalize(turn_unsigned)
        if not verify_signature(receipt_runtime_pub, turn_bytes, turn["turn_envelope_signature_b64"]):
            return {"ok": False, "reason": "turn_signature_invalid"}

        # 5. session_id matches receipt
        if turn["session_id"] != receipt["session_id"]:
            return {"ok": False, "reason": "turn_session_id_mismatch"}

        # 6. runtime_fingerprint matches receipt
        if turn["runtime_fingerprint"] != receipt["runtime_fingerprint"]:
            return {"ok": False, "reason": "runtime_replaced"}

        # 7. accepted_charter_sha256 matches receipt
        if turn["accepted_charter_sha256"] != receipt["charter_sha256"]:
            return {"ok": False, "reason": "charter_rebound"}

        return {"ok": True, "reason": ""}

    # --- Freshness check (verifier-side window) ---

    def _freshness_check(self, envelope: dict) -> dict:
        now = self.verifier_now
        not_before = envelope["binding"]["not_before_utc"]
        not_after = envelope["binding"]["not_after_utc"]
        skew = 30  # 30 seconds clock-skew tolerance
        if now + skew < not_before:
            return {"ok": False, "reason": "envelope_not_yet_valid"}
        if now - skew > not_after:
            return {"ok": False, "reason": "envelope_expired"}
        return {"ok": True, "reason": ""}

    # --- Main verdict ---

    def verify_binding(
        self,
        *,
        envelope = None,
        inline_charter = None,
        receipt = None,
        turn = None,
        # Optional pre-flight checks only:
        issuer_id = None,
    ) -> dict:
        """Verify a binding.

        - envelope + receipt: full Case 1 / Case 2 / Case 5 path
        - inline_charter only: Case 3 (provenance missing)
        - verifier_inside_participant_host=True: Case 4 (collocation)
        - turn: per-turn continuity check (Cases 1, 6)
        """

        # Case 4 check: collocation
        if self.verifier_inside_participant_host:
            return {
                "verdict": "STOP",
                "stop_code": "GX_NOT_ACCEPTABLE_AS_FORMAL_EVIDENCE",
                "g_assurance": "G0",
                "a_assurance": "A1",
                "assurance_tuple": "G0/A1",
                "details": {"reason": "verifier_inside_participant_host"},
            }

        # Case 3 check: provenance missing
        if envelope is None and inline_charter is not None:
            return {
                "verdict": "STOP",
                "stop_code": "GX_PROVENANCE_MISSING",
                "g_assurance": "G0",
                "a_assurance": "A0",
                "assurance_tuple": "G0/A0",
                "details": {"reason": "inline_charter_without_envelope"},
            }

        if envelope is None:
            return {
                "verdict": "STOP",
                "stop_code": "GX_PROVENANCE_MISSING",
                "g_assurance": "G0",
                "a_assurance": "A0",
                "assurance_tuple": "G0/A0",
                "details": {"reason": "no_envelope_no_inline"},
            }

        # Step 1: roster check
        rc = self._roster_check(envelope)
        if not rc["ok"]:
            return {
                "verdict": "STOP",
                "stop_code": "GX_ISSUER_UNAUTHORIZED",
                "g_assurance": "G0",
                "a_assurance": "A1",
                "assurance_tuple": "G0/A1",
                "details": rc,
            }

        # Step 2: envelope signature + charter integrity
        ec = self._envelope_check(envelope)
        if not ec["ok"]:
            # charter_sha256_mismatch is a tamper
            if ec["reason"] == "charter_sha256_mismatch":
                return {
                    "verdict": "STOP",
                    "stop_code": "GX_CHARTER_ALTERED",
                    "g_assurance": "G0",
                    "a_assurance": "A1",
                    "assurance_tuple": "G0/A1",
                    "details": ec,
                }
            return {
                "verdict": "STOP",
                "stop_code": "GX_HANDSHAKE_STEP2_CHARTER_INTEGRITY",
                "g_assurance": "G0",
                "a_assurance": "A1",
                "assurance_tuple": "G0/A1",
                "details": ec,
            }

        # Step 5: freshness
        fc = self._freshness_check(envelope)
        if not fc["ok"]:
            return {
                "verdict": "STOP",
                "stop_code": "GX_AUTH_EXPIRED",
                "g_assurance": "G0",
                "a_assurance": "A1",
                "assurance_tuple": "G0/A1",
                "details": fc,
            }

        # Step 3 + Step 4: receipt (if provided)
        if receipt is not None:
            rt = self._receipt_check(receipt, envelope)
            if not rt["ok"]:
                # Determine precise stop code
                reason = rt["reason"]
                if reason in ("runtime_fingerprint_quote_mismatch",
                              "signing_key_handle_mismatch",
                              "receipt_signature_invalid"):
                    return {
                        "verdict": "STOP",
                        "stop_code": "GX_RUNTIME_REPLACED",
                        "g_assurance": "G0",
                        "a_assurance": "A1",
                        "assurance_tuple": "G0/A1",
                        "details": rt,
                    }
                return {
                    "verdict": "STOP",
                    "stop_code": "GX_HANDSHAKE_STEP4_ACCEPTANCE",
                    "g_assurance": "G0",
                    "a_assurance": "A1",
                    "assurance_tuple": "G0/A1",
                    "details": rt,
                }

        # Step 5 + Step 6: turn (if provided)
        if turn is not None and receipt is not None:
            tc = self._turn_check(turn, receipt)
            if not tc["ok"]:
                reason = tc["reason"]
                if reason == "runtime_replaced":
                    return {
                        "verdict": "STOP",
                        "stop_code": "GX_RUNTIME_REPLACED",
                        "g_assurance": "G0",
                        "a_assurance": "A1",
                        "assurance_tuple": "G0/A1",
                        "details": tc,
                    }
                if reason in ("turn_session_id_mismatch",):
                    return {
                        "verdict": "STOP",
                        "stop_code": "GX_SESSION_SUBSTITUTION",
                        "g_assurance": "G0",
                        "a_assurance": "A1",
                        "assurance_tuple": "G0/A1",
                        "details": tc,
                    }
                if reason in ("turn_signature_invalid", "turn_attestation:..."):
                    return {
                        "verdict": "STOP",
                        "stop_code": "GX_ATTESTATION_INVALID",
                        "g_assurance": "G0",
                        "a_assurance": "A1",
                        "assurance_tuple": "G0/A1",
                        "details": tc,
                    }
                return {
                    "verdict": "STOP",
                    "stop_code": "GX_HANDSHAKE_STEP6_GOVERNED_TURN",
                    "g_assurance": "G0",
                    "a_assurance": "A1",
                    "assurance_tuple": "G0/A1",
                    "details": tc,
                }

        # All checks passed
        return {
            "verdict": "PASS",
            "stop_code": "",
            "g_assurance": "G5",
            "a_assurance": "A1",
            "assurance_tuple": "G5/A1",
            "details": {},
        }

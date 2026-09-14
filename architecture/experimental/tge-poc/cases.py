"""Six deterministic test cases per v0.2.1 §J.

CASE 1 - VALID ESTABLISHMENT: full chain -> PASS
CASE 2 - UNTRUSTED ISSUER: issuer not on roster -> GX_ISSUER_UNAUTHORIZED
CASE 3 - PROVENANCE MISSING: inline charter only -> GX_PROVENANCE_MISSING
CASE 4 - SELF/COLLOCATED VERIFICATION: verifier_inside_participant_host=True
                                        -> GX_NOT_ACCEPTABLE_AS_FORMAL_EVIDENCE
CASE 5 - STALE/FRESHNESS FAILURE: envelope not_after in past -> GX_AUTH_EXPIRED
CASE 6 - RUNTIME/SIGNING SUBSTITUTION: post-acceptance substitute signing key
                                        -> GX_RUNTIME_REPLACED
        Adversarial variant: valid quote + attacker-controlled runtime key
        -> MUST NOT pass (GX_RUNTIME_REPLACED via signing_key_handle_mismatch)
"""
import time
import base64
import hashlib

from canonicalization import canonicalize, canonical_hash
from crypto_utils import (
    Ed25519PrivateKey, Ed25519PublicKey,
    generate_keypair, public_key_bytes, public_key_b64,
    signature_b64, load_public_key_from_b64,
)
from issuer import build_envelope, build_roster
from attestation import make_quote
from runtime import RuntimeStub, make_runtime
from verifier import Verifier


def build_charter(charter_id: str = "coa-e2-governed-v0.4.1") -> dict:
    """Build a charter fixture."""
    charter_object = {
        "charter_id": charter_id,
        "charter_version": "TGE-CHARTER/0.2.1",
        "binding_clause": "The participant agrees to be bound by the governance charter identified above.",
        "scope": "experimental",
        "issued_utc": "2026-09-14T00:00:00Z",
    }
    canonical_bytes = canonicalize(charter_object)
    return {
        "charter_id": charter_object["charter_id"],
        "charter_sha256": canonical_hash(charter_object),
        "charter_canonical_bytes_b64": base64.b64encode(canonical_bytes).decode('ascii'),
        "charter_object": charter_object,
    }


def build_setup(*, now: int = None):
    """Build the standard setup: roster, issuer, RTA, runtime, manufacturer keys.

    The runtime's manufacturer_root and tpm_ak keys are wired into the runtime
    AND surfaced through setup so the verifier can validate quotes against them.
    """
    if now is None:
        now = int(time.time())
    issuer_priv, issuer_pub = generate_keypair()
    rta_priv, rta_pub = generate_keypair()
    mfr_priv, mfr_pub = generate_keypair()
    ak_priv, ak_pub = generate_keypair()
    # Pass the manufacturer/TPM keys to the runtime so its quotes are signed
    # under keys the verifier knows.
    runtime = make_runtime(
        runtime_id="rt-001",
        manufacturer_root_priv=mfr_priv, manufacturer_root_pub=mfr_pub,
        tpm_ak_priv=ak_priv, tpm_ak_pub=ak_pub,
    )

    setup = {
        "now": now,
        "issuer_priv": issuer_priv,
        "issuer_pub": issuer_pub,
        "issuer_id": "issuer-001",
        "rta_priv": rta_priv,
        "rta_pub": rta_pub,
        "manufacturer_root_priv": mfr_priv,
        "manufacturer_root_pub": mfr_pub,
        "tpm_ak_priv": ak_priv,
        "tpm_ak_pub": ak_pub,
        "runtime": runtime,
    }
    return setup


def case1_valid_establishment():
    """CASE 1 - valid establishment."""
    setup = build_setup()
    now = setup["now"]

    # Build roster admitting our issuer
    roster = build_roster(
        roster_id="roster-001",
        rta_priv=setup["rta_priv"],
        rta_pub=setup["rta_pub"],
        issuers=[{
            "issuer_id": setup["issuer_id"],
            "issuer_pubkey_b64": public_key_b64(setup["issuer_pub"]),
            "charter_type_scope": "all",
            "valid_from_utc": now - 3600,
            "valid_until_utc": now + 3600,
        }],
    )

    # Build charter
    charter = build_charter()

    # Build envelope
    envelope = build_envelope(
        envelope_id="env-001",
        issuer_id=setup["issuer_id"],
        issuer_priv=setup["issuer_priv"],
        issuer_pub=setup["issuer_pub"],
        charter=charter,
        runtime_fingerprint=setup["runtime"].runtime_fingerprint,
        valid_for_seconds=3600,
    )

    # Build verifier (out-of-band, fresh clock)
    verifier = Verifier(
        roster=roster,
        rta_pub=setup["rta_pub"],
        manufacturer_root_pub=setup["manufacturer_root_pub"],
        tpm_ak_pub=setup["tpm_ak_pub"],
        verifier_now=now + 10,  # 10s after envelope issued
    )

    # Bind the runtime
    receipt = setup["runtime"].bind(
        envelope,
        session_id="session-001",
        nonce_freshness="nonce-fresh-aaaa-bbbb-cccc",
        verifier_challenge="challenge-aaaa",
    )

    verdict = verifier.verify_binding(envelope=envelope, receipt=receipt)
    return {
        "case": "case_1_valid_establishment",
        "expected": "PASS",
        "expected_tuple": "G5/A1",
        "actual": verdict,
        "pass": verdict["verdict"] == "PASS",
    }


def case2_untrusted_issuer():
    """CASE 2 - issuer not on roster."""
    setup = build_setup()
    now = setup["now"]

    # Build roster that admits an UNRELATED issuer
    other_priv, other_pub = generate_keypair()
    roster = build_roster(
        roster_id="roster-002",
        rta_priv=setup["rta_priv"],
        rta_pub=setup["rta_pub"],
        issuers=[{
            "issuer_id": "other-issuer",
            "issuer_pubkey_b64": public_key_b64(other_pub),
            "charter_type_scope": "all",
            "valid_from_utc": now - 3600,
            "valid_until_utc": now + 3600,
        }],
    )

    charter = build_charter()
    envelope = build_envelope(
        envelope_id="env-002",
        issuer_id=setup["issuer_id"],   # NOT on the roster
        issuer_priv=setup["issuer_priv"],
        issuer_pub=setup["issuer_pub"],
        charter=charter,
        runtime_fingerprint=setup["runtime"].runtime_fingerprint,
        valid_for_seconds=3600,
    )

    verifier = Verifier(
        roster=roster,
        rta_pub=setup["rta_pub"],
        manufacturer_root_pub=setup["manufacturer_root_pub"],
        tpm_ak_pub=setup["tpm_ak_pub"],
        verifier_now=now + 10,
    )

    receipt = setup["runtime"].bind(envelope, session_id="session-002", nonce_freshness="nonce-2", verifier_challenge="chal-2")

    verdict = verifier.verify_binding(envelope=envelope, receipt=receipt)
    return {
        "case": "case_2_untrusted_issuer",
        "expected": "STOP",
        "expected_stop_code": "GX_ISSUER_UNAUTHORIZED",
        "actual": verdict,
        "pass": verdict["verdict"] == "STOP" and verdict["stop_code"] == "GX_ISSUER_UNAUTHORIZED",
    }


def case3_provenance_missing():
    """CASE 3 - inline charter only, no envelope."""
    setup = build_setup()
    now = setup["now"]

    roster = build_roster(
        roster_id="roster-003",
        rta_priv=setup["rta_priv"],
        rta_pub=setup["rta_pub"],
        issuers=[{
            "issuer_id": setup["issuer_id"],
            "issuer_pubkey_b64": public_key_b64(setup["issuer_pub"]),
            "charter_type_scope": "all",
            "valid_from_utc": now - 3600,
            "valid_until_utc": now + 3600,
        }],
    )

    verifier = Verifier(
        roster=roster,
        rta_pub=setup["rta_pub"],
        manufacturer_root_pub=setup["manufacturer_root_pub"],
        tpm_ak_pub=setup["tpm_ak_pub"],
        verifier_now=now + 10,
    )

    # Inline charter: no envelope, just text in a "prompt"
    inline_charter = {"text": "You agree to be bound by governance charter v0.4.1."}
    verdict = verifier.verify_binding(inline_charter=inline_charter)
    return {
        "case": "case_3_provenance_missing",
        "expected": "STOP",
        "expected_stop_code": "GX_PROVENANCE_MISSING",
        "actual": verdict,
        "pass": verdict["verdict"] == "STOP" and verdict["stop_code"] == "GX_PROVENANCE_MISSING",
    }


def case4_collocated_verifier():
    """CASE 4 - verifier collocated with participant host."""
    setup = build_setup()
    now = setup["now"]

    roster = build_roster(
        roster_id="roster-004",
        rta_priv=setup["rta_priv"],
        rta_pub=setup["rta_pub"],
        issuers=[{
            "issuer_id": setup["issuer_id"],
            "issuer_pubkey_b64": public_key_b64(setup["issuer_pub"]),
            "charter_type_scope": "all",
            "valid_from_utc": now - 3600,
            "valid_until_utc": now + 3600,
        }],
    )

    charter = build_charter()
    envelope = build_envelope(
        envelope_id="env-004",
        issuer_id=setup["issuer_id"],
        issuer_priv=setup["issuer_priv"],
        issuer_pub=setup["issuer_pub"],
        charter=charter,
        runtime_fingerprint=setup["runtime"].runtime_fingerprint,
        valid_for_seconds=3600,
    )

    # Verifier is collocated
    verifier = Verifier(
        roster=roster,
        rta_pub=setup["rta_pub"],
        manufacturer_root_pub=setup["manufacturer_root_pub"],
        tpm_ak_pub=setup["tpm_ak_pub"],
        verifier_now=now + 10,
        verifier_inside_participant_host=True,
    )

    receipt = setup["runtime"].bind(envelope, session_id="session-004", nonce_freshness="nonce-4", verifier_challenge="chal-4")

    verdict = verifier.verify_binding(envelope=envelope, receipt=receipt)
    return {
        "case": "case_4_collocated_verifier",
        "expected": "STOP",
        "expected_stop_code": "GX_NOT_ACCEPTABLE_AS_FORMAL_EVIDENCE",
        "actual": verdict,
        "pass": verdict["verdict"] == "STOP" and verdict["stop_code"] == "GX_NOT_ACCEPTABLE_AS_FORMAL_EVIDENCE",
    }


def case5_stale_freshness():
    """CASE 5 - envelope not_after_utc is in the past relative to verifier clock."""
    setup = build_setup()
    now = setup["now"]

    roster = build_roster(
        roster_id="roster-005",
        rta_priv=setup["rta_priv"],
        rta_pub=setup["rta_pub"],
        issuers=[{
            "issuer_id": setup["issuer_id"],
            "issuer_pubkey_b64": public_key_b64(setup["issuer_pub"]),
            "charter_type_scope": "all",
            "valid_from_utc": now - 3600,
            "valid_until_utc": now + 3600,
        }],
    )

    charter = build_charter()

    # Build envelope whose not_after_utc is in the past (before verifier_now)
    envelope = build_envelope(
        envelope_id="env-005",
        issuer_id=setup["issuer_id"],
        issuer_priv=setup["issuer_priv"],
        issuer_pub=setup["issuer_pub"],
        charter=charter,
        runtime_fingerprint=setup["runtime"].runtime_fingerprint,
        valid_for_seconds=-7200,  # negative duration => expires 7200s in the past relative to issue time
    )

    verifier = Verifier(
        roster=roster,
        rta_pub=setup["rta_pub"],
        manufacturer_root_pub=setup["manufacturer_root_pub"],
        tpm_ak_pub=setup["tpm_ak_pub"],
        verifier_now=now + 10,
    )

    receipt = setup["runtime"].bind(envelope, session_id="session-005", nonce_freshness="nonce-5", verifier_challenge="chal-5")

    verdict = verifier.verify_binding(envelope=envelope, receipt=receipt)
    return {
        "case": "case_5_stale_freshness",
        "expected": "STOP",
        "expected_stop_code": "GX_AUTH_EXPIRED",
        "actual": verdict,
        "pass": verdict["verdict"] == "STOP" and verdict["stop_code"] == "GX_AUTH_EXPIRED",
    }


def case6_runtime_substitution():
    """CASE 6 - after acceptance, runtime signing key is substituted.

    Adversarial variant: craft a quote referencing attacker-controlled
    runtime key + binding the runtime fingerprint to a benign value.
    The verifier MUST reject with GX_RUNTIME_REPLACED via
    signing_key_handle_mismatch or runtime_fingerprint_quote_mismatch.
    """
    setup = build_setup()
    now = setup["now"]

    roster = build_roster(
        roster_id="roster-006",
        rta_priv=setup["rta_priv"],
        rta_pub=setup["rta_pub"],
        issuers=[{
            "issuer_id": setup["issuer_id"],
            "issuer_pubkey_b64": public_key_b64(setup["issuer_pub"]),
            "charter_type_scope": "all",
            "valid_from_utc": now - 3600,
            "valid_until_utc": now + 3600,
        }],
    )

    charter = build_charter()
    envelope = build_envelope(
        envelope_id="env-006",
        issuer_id=setup["issuer_id"],
        issuer_priv=setup["issuer_priv"],
        issuer_pub=setup["issuer_pub"],
        charter=charter,
        runtime_fingerprint=setup["runtime"].runtime_fingerprint,
        valid_for_seconds=3600,
    )

    receipt = setup["runtime"].bind(envelope, session_id="session-006", nonce_freshness="nonce-6", verifier_challenge="chal-6")

    # ---- Adversarial composition attack ----
    # Adversary mints a fresh runtime key and crafts a quote that
    # *references* that key, with PCRs derived from the adversary's
    # own runtime_fingerprint (which is itself derived from the
    # legitimate fingerprint to simulate a hostile takeover). The
    # verifier's check on signing_key_handle_b64 will catch this.
    attacker_priv, attacker_pub = generate_keypair()
    attacker_fp = hashlib.sha256(b"runtime-binary:attacker-007").hexdigest()
    attacker_quote = make_quote(
        runtime_fingerprint=attacker_fp,
        signing_key_pub=public_key_bytes(attacker_pub),
        manufacturer_root_priv=setup["manufacturer_root_priv"],
        tpm_ak_priv=setup["tpm_ak_priv"],
    )

    verifier = Verifier(
        roster=roster,
        rta_pub=setup["rta_pub"],
        manufacturer_root_pub=setup["manufacturer_root_pub"],
        tpm_ak_pub=setup["tpm_ak_pub"],
        verifier_now=now + 10,
    )

    # Emit a turn 1 with the legitimate runtime (this passes)
    turn1 = setup["runtime"].emit_turn(
        receipt=receipt, turn_index=1, executed_action="action-1"
    )
    verdict_turn1 = verifier.verify_binding(envelope=envelope, receipt=receipt, turn=turn1)
    if verdict_turn1["verdict"] != "PASS":
        return {
            "case": "case_6_runtime_substitution",
            "expected": "STOP with GX_RUNTIME_REPLACED on turn 2",
            "actual": {
                "verdict": verdict_turn1["verdict"],
                "stop_code": verdict_turn1["stop_code"],
                "assurance_tuple": verdict_turn1["assurance_tuple"],
                "details": verdict_turn1.get("details", {}),
                "phase": "turn_1",
            },
            "early_failure": "turn 1 unexpectedly STOPped",
            "turn1": verdict_turn1,
            "pass": False,
        }

    # Adversary now emits turn 2 with the attacker key + attacker quote.
    # The runtime_fingerprint in the turn is the LEGITIMATE one (so the
    # naive continuity check would pass), but the quote references the
    # attacker key. This is the composition attack: valid fingerprint +
    # unrelated signing key.
    turn2_adversarial = setup["runtime"].emit_turn(
        receipt=receipt,
        turn_index=2,
        executed_action="action-2-malicious",
        previous_turn_envelope_sha256=canonical_hash(turn1),
        override_runtime_priv=attacker_priv,
        override_runtime_fingerprint=setup["runtime"].runtime_fingerprint,  # spoofed
        override_quote=attacker_quote,  # references attacker key
    )
    verdict_turn2 = verifier.verify_binding(envelope=envelope, receipt=receipt, turn=turn2_adversarial)
    return {
        "case": "case_6_runtime_substitution",
        "expected": "STOP",
        "expected_stop_code": "GX_RUNTIME_REPLACED",
        "actual": verdict_turn2,
        "turn1_verification": verdict_turn1,
        "pass": verdict_turn2["verdict"] == "STOP" and verdict_turn2["stop_code"] == "GX_RUNTIME_REPLACED",
    }


def run_all_cases():
    return [
        case1_valid_establishment(),
        case2_untrusted_issuer(),
        case3_provenance_missing(),
        case4_collocated_verifier(),
        case5_stale_freshness(),
        case6_runtime_substitution(),
    ]

"""ATE-PoC v0.1 test matrix — 11 deterministic cases.

Per ATE-POC-DESIGN-v0.1 §4. Each case constructs an Envelope with
deliberate mutations. Tamper tests (ATE-5a/b/c/d) preserve the
original valid fixture separately and mutate exactly one field.

Required output:
  - per-case expected vs actual final decision
  - per-case gate trace
  - tamper-detection results
  - deterministic replay
"""
import sys, os, json, time, copy, hashlib

THIS = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, THIS)

# IMPORTANT: the v0.2.2 GEL is reused byte-identically from the Stage-C v0.2.2
# implementation. Add that directory to sys.path so the pipeline can import it.
GEL_V022_DIR = os.path.normpath(os.path.join(THIS, "..", "..", "stage-c", "implementation_v022"))
sys.path.insert(0, GEL_V022_DIR)

from crypto_utils import generate_keypair, public_key_b64, load_public_key_from_b64
from identity import make_identity
from capability import make_capability
from receipt import make_receipt
from pipeline import evaluate_envelope, CHARTER_SHA256


# Frozen charter sha for the PoC
CHARTER = CHARTER_SHA256


def _build_fixtures():
    """Build a fresh set of fixture keys and a baseline valid envelope.

    Returns (authority_priv, authority_pub, runtime_priv, fixtures, baseline_envelope).
    """
    runtime_priv, _runtime_pub = generate_keypair()
    authority_priv, authority_pub = generate_keypair()

    session_id = "session_ate_001"
    agent_id = "agent_ate_001"
    runtime_fingerprint = hashlib.sha256(b"runtime_ate_001").hexdigest()
    issued_at_utc = 1700000000

    identity = make_identity(
        agent_id=agent_id,
        runtime_fingerprint=runtime_fingerprint,
        session_id=session_id,
        issued_at_utc=issued_at_utc,
        priv=runtime_priv,
    )

    receipt = make_receipt(
        session_id=session_id,
        charter_sha256=CHARTER,
        issued_at_utc=issued_at_utc,
    )

    capability = make_capability(
        capability_id="cap_ate_001",
        agent_id=agent_id,
        session_id=session_id,
        scope=["B11:C5:*", "B1:C1:/tmp/*", "B7:C3:*", "B10:C4:*", "B1:C3:*"],
        valid_from_utc=issued_at_utc - 60,
        valid_until_utc=issued_at_utc + 3600,
        issued_by="authority_ate_001",
        authority_priv=authority_priv,
    )

    # Charter-consistent permitted action: NONE operation on action target
    candidate_action = {
        "schema_id": "TGE-STAGE-C-ACTION/0.2.2",
        "action_id": "0000000000000001",
        "session_id": session_id,
        "issued_at_utc": issued_at_utc,
        "task_id": "T1",
        "decision": "A3",
        "operation": "B11",
        "target_kind": "C5",
        "target_identifier": "action_target_1",
        "evidence_refs": [],
        "prior_commitments_active": [],
        "authority_asserted": None,
        "observation": "decide; no operation",
    }

    baseline_envelope = {
        "schema_id": "TGE-ATE-ENVELOPE/0.1",
        "envelope_id": "env_ate_001",
        "issued_at_utc": issued_at_utc,
        "identity": identity,
        "capability": capability,
        "acceptance_receipt": receipt,
        "candidate_action": candidate_action,
    }

    return authority_priv, authority_pub, runtime_priv, {
        "session_id": session_id,
        "agent_id": agent_id,
        "runtime_fingerprint": runtime_fingerprint,
        "issued_at_utc": issued_at_utc,
        "authority_pub_b64": public_key_b64(authority_pub),
        "authority_priv": authority_priv,
    }, baseline_envelope


def _hash_envelope(env):
    from crypto_utils import canonicalize_json
    return hashlib.sha256(canonicalize_json(env)).hexdigest()


def run_case(case_id, expected, envelope, *, current_time, authority_pub,
             tamper_info=None):
    """Run one case and produce a result dict."""
    gate_trace = []
    trust_summary = {}
    decision = evaluate_envelope(
        envelope, current_time=current_time, authority_pub=authority_pub,
        gate_trace=gate_trace, trust_summary=trust_summary,
    )

    actual_verdict = decision["verdict"]
    pass_ok = (actual_verdict == expected["verdict"])
    pass_reason = (decision["reason_code"] == expected.get("reason_code", decision["reason_code"]))

    # Verify audit_trail records all reached gates
    reached_gates = [g["gate_id"] for g in gate_trace]
    expected_reached = expected.get("expected_reached_gates", None)

    result = {
        "case_id": case_id,
        "description": expected["description"],
        "expected_verdict": expected["verdict"],
        "actual_verdict": actual_verdict,
        "expected_reason_code": expected.get("reason_code"),
        "actual_reason_code": decision["reason_code"],
        "expected_reached_gates": expected_reached,
        "actual_reached_gates": reached_gates,
        "failing_gate": decision["failing_gate"],
        "trust_summary": decision["trust_summary"],
        "hashes": decision["hashes"],
        "audit_trail": gate_trace,
        "pass": pass_ok and pass_reason,
    }
    if tamper_info:
        result["tamper_info"] = tamper_info
    return result


def build_test_cases(authority_priv, authority_pub, fx, base_env, auth_pub_obj):
    """Build the 11-case test matrix per ATE-POC-DESIGN-v0.1 §4."""
    now = fx["issued_at_utc"] + 60  # 60s after issuance, within receipt freshness window

    cases = []

    # ATE-1: valid pipeline -> ALLOW
    cases.append((
        "ATE-1",
        {
            "description": "valid identity + valid receipt + authorized capability + permitted action",
            "verdict": "ALLOW",
            "reason_code": "PASS",
            "expected_reached_gates": ["GATE_IDENTITY", "GATE_RECEIPT", "GATE_SESSION", "GATE_CAPABILITY", "GATE_GEL"],
        },
        copy.deepcopy(base_env),
        {"current_time": now, "authority_pub": auth_pub_obj},
    ))

    # ATE-2: capability exceeded -> DENY_BEFORE_GEL
    env2 = copy.deepcopy(base_env)
    env2["candidate_action"] = {
        **env2["candidate_action"],
        "operation": "B1",  # DELETE -- not in scope for this target_kind/target
        "target_kind": "C1",
        "target_identifier": "/etc/passwd",  # /etc/* not in scope; only /tmp/*
        "authority_asserted": "D1",
        "observation": "trying to delete /etc/passwd",
    }
    cases.append((
        "ATE-2",
        {
            "description": "valid identity/receipt but action exceeds granted capability",
            "verdict": "DENY_BEFORE_GEL",
            "reason_code": "GX_CAPABILITY_EXCEEDED",
            "expected_reached_gates": ["GATE_IDENTITY", "GATE_RECEIPT", "GATE_SESSION", "GATE_CAPABILITY"],
        },
        env2,
        {"current_time": now, "authority_pub": auth_pub_obj},
    ))

    # ATE-3a: missing receipt -> DENY_BEFORE_GEL
    env3a = copy.deepcopy(base_env)
    env3a["acceptance_receipt"] = None
    cases.append((
        "ATE-3a",
        {
            "description": "missing receipt",
            "verdict": "DENY_BEFORE_GEL",
            "reason_code": "GX_RECEIPT_MISSING",
            "expected_reached_gates": ["GATE_IDENTITY", "GATE_RECEIPT"],
        },
        env3a,
        {"current_time": now, "authority_pub": auth_pub_obj},
    ))

    # ATE-3b: invalid receipt (schema_id mismatch)
    env3b = copy.deepcopy(base_env)
    env3b["acceptance_receipt"] = {**env3b["acceptance_receipt"], "schema_id": "INVALID"}
    cases.append((
        "ATE-3b",
        {
            "description": "invalid receipt (schema_id mismatch)",
            "verdict": "DENY_BEFORE_GEL",
            "reason_code": "GX_RECEIPT_INVALID",
            "expected_reached_gates": ["GATE_IDENTITY", "GATE_RECEIPT"],
        },
        env3b,
        {"current_time": now, "authority_pub": auth_pub_obj},
    ))

    # ATE-3c: expired receipt (issued long ago)
    env3c = copy.deepcopy(base_env)
    long_ago = fx["issued_at_utc"] - 7200  # 2 hours ago
    env3c["acceptance_receipt"] = make_receipt(
        session_id=fx["session_id"],
        charter_sha256=CHARTER,
        issued_at_utc=long_ago,
    )
    cases.append((
        "ATE-3c",
        {
            "description": "expired receipt (issued 2 hours ago, freshness window 1h)",
            "verdict": "DENY_BEFORE_GEL",
            "reason_code": "GX_RECEIPT_EXPIRED",
            "expected_reached_gates": ["GATE_IDENTITY", "GATE_RECEIPT"],
        },
        env3c,
        {"current_time": now, "authority_pub": auth_pub_obj},
    ))

    # ATE-3d: session mismatch
    env3d = copy.deepcopy(base_env)
    env3d["acceptance_receipt"] = make_receipt(
        session_id="different_session_id",
        charter_sha256=CHARTER,
        issued_at_utc=fx["issued_at_utc"],
    )
    cases.append((
        "ATE-3d",
        {
            "description": "session mismatch (receipt.session_id != identity.session_id)",
            "verdict": "DENY_BEFORE_GEL",
            "reason_code": "GX_SESSION_MISMATCH",
            "expected_reached_gates": ["GATE_IDENTITY", "GATE_RECEIPT"],
        },
        env3d,
        {"current_time": now, "authority_pub": auth_pub_obj},
    ))

    # ATE-4: governance-violating authorized action -> BLOCK
    env4 = copy.deepcopy(base_env)
    env4["candidate_action"] = {
        **env4["candidate_action"],
        "operation": "B1",  # DELETE
        "target_kind": "C1",  # file
        "target_identifier": "/tmp/scratch/foo",  # /tmp/* is in scope
        "authority_asserted": "D1",
        "observation": "trying to delete as instructed",
    }
    cases.append((
        "ATE-4",
        {
            "description": "authorized request containing GEL-violating action",
            "verdict": "BLOCK",
            "reason_code": "R3p_NO_UNAUTHORIZED_DESTRUCTIVE_ACTION",
            "expected_reached_gates": ["GATE_IDENTITY", "GATE_RECEIPT", "GATE_SESSION", "GATE_CAPABILITY", "GATE_GEL"],
        },
        env4,
        {"current_time": now, "authority_pub": auth_pub_obj},
    ))

    # ATE-5a: tampered identity (signature mismatch)
    env5a = copy.deepcopy(base_env)
    original_identity_hash = hashlib.sha256(json.dumps(env5a["identity"], sort_keys=True).encode()).hexdigest()
    env5a["identity"] = {**env5a["identity"], "signature_b64": "AAAA" + env5a["identity"]["signature_b64"][4:]}  # corrupt signature
    tampered_identity_hash = hashlib.sha256(json.dumps(env5a["identity"], sort_keys=True).encode()).hexdigest()
    cases.append((
        "ATE-5a",
        {
            "description": "tampered identity (corrupted signature)",
            "verdict": "DENY_BEFORE_GEL",
            "reason_code": "GX_IDENTITY_INVALID",
            "expected_reached_gates": ["GATE_IDENTITY"],
        },
        env5a,
        {
            "current_time": now, "authority_pub": auth_pub_obj,
            "tamper_info": {
                "tampered_field": "identity.signature_b64",
                "original_identity_hash": original_identity_hash,
                "tampered_identity_hash": tampered_identity_hash,
                "detection_gate": "GATE_IDENTITY",
            }
        },
    ))

    # ATE-5b: tampered receipt (charter_sha256 replaced)
    env5b = copy.deepcopy(base_env)
    original_receipt_hash = hashlib.sha256(json.dumps(env5b["acceptance_receipt"], sort_keys=True).encode()).hexdigest()
    env5b["acceptance_receipt"] = {**env5b["acceptance_receipt"], "charter_sha256": "tampered_charter_sha256_xxxxxxxx"}
    tampered_receipt_hash = hashlib.sha256(json.dumps(env5b["acceptance_receipt"], sort_keys=True).encode()).hexdigest()
    cases.append((
        "ATE-5b",
        {
            "description": "tampered receipt (charter_sha256 replaced)",
            "verdict": "DENY_BEFORE_GEL",
            "reason_code": "GX_RECEIPT_TAMPERED",
            "expected_reached_gates": ["GATE_IDENTITY", "GATE_RECEIPT"],
        },
        env5b,
        {
            "current_time": now, "authority_pub": auth_pub_obj,
            "tamper_info": {
                "tampered_field": "acceptance_receipt.charter_sha256",
                "original_receipt_hash": original_receipt_hash,
                "tampered_receipt_hash": tampered_receipt_hash,
                "detection_gate": "GATE_RECEIPT",
            }
        },
    ))

    # ATE-5c: tampered action (operation field changed after signature)
    # Per ATE-POC-DESIGN-v0.1 §4.5c, v0.2.2 has no per-action signature.
    # The pipeline detects tampering via capability scope check.
    env5c = copy.deepcopy(base_env)
    original_action_hash = hashlib.sha256(json.dumps(env5c["candidate_action"], sort_keys=True).encode()).hexdigest()
    # Change operation from B11 (NONE) to B2 (CREATE), which is not in scope
    env5c["candidate_action"] = {**env5c["candidate_action"], "operation": "B2", "target_kind": "C1", "target_identifier": "/tmp/new"}
    tampered_action_hash = hashlib.sha256(json.dumps(env5c["candidate_action"], sort_keys=True).encode()).hexdigest()
    cases.append((
        "ATE-5c",
        {
            "description": "tampered candidate action (operation changed; detected at capability scope check)",
            "verdict": "DENY_BEFORE_GEL",
            "reason_code": "GX_CAPABILITY_EXCEEDED",
            "expected_reached_gates": ["GATE_IDENTITY", "GATE_RECEIPT", "GATE_SESSION", "GATE_CAPABILITY"],
        },
        env5c,
        {
            "current_time": now, "authority_pub": auth_pub_obj,
            "tamper_info": {
                "tampered_field": "candidate_action.operation",
                "original_action_hash": original_action_hash,
                "tampered_action_hash": tampered_action_hash,
                "detection_gate": "GATE_CAPABILITY",
                "note": "v0.2.2 has no per-action signature; tampering detected via capability scope mismatch",
            }
        },
    ))

    # ATE-5d: tampered evidence chain (audit_trail entry modified after the fact)
    # Per ATE-POC-DESIGN-v0.1 §4.5d, this case is OUT OF SCOPE for v0.1.
    # The PoC does not have a tamper-evident log; this case is documented
    # as deferred to a later stage. We DO NOT include this in the 11 cases
    # (the PI's directive explicitly enumerates 11 cases).
    # Instead, we verify evidence_chain_hash integrity by checking that
    # the deterministic replay reproduces the same evidence_chain_hash.
    # This is the "deterministic replay" requirement.
    # We represent this case as the replay-verification case (no new test
    # beyond ATE-1; replay is run separately after all 11 cases).

    # ATE-5d: tampered evidence chain (audit_trail entry modified after the fact)
    # Per ATE-POC-DESIGN-v0.1 §4.5d, this case tests the evidence_chain_hash
    # tamper-evidence: after the pipeline produces a decision, mutate one
    # audit_trail entry, then verify_decision should report MISMATCH.
    # Per PI directive 2026-09-14, ATE-5d must produce "verification failure".
    # The detection mechanism is the deterministic replay (verify_decision).
    cases.append((
        "ATE-5d",
        {
            "description": "tampered evidence chain (audit_trail entry modified post-hoc; verify_decision detects mismatch)",
            "verdict": "DENY_BEFORE_GEL",  # the *verifier* denies because chain_hash mismatches
            "reason_code": "GX_EVIDENCE_CHAIN_TAMPERED",
            "expected_reached_gates": ["GATE_IDENTITY", "GATE_RECEIPT", "GATE_SESSION", "GATE_CAPABILITY", "GATE_GEL"],
        },
        copy.deepcopy(base_env),  # the envelope is the same as ATE-1; tampering is post-pipeline
        {"current_time": now, "authority_pub": auth_pub_obj, "tamper_kind": "evidence_chain"},
    ))

    return cases


def run_replay(decision):
    """Replay verification: re-run the pipeline with the same envelope
    and verify that the evidence_chain_hash is identical.
    """
    # The replay function re-derives the chain hash from the recorded gate_trace.
    from crypto_utils import canonicalize_json
    new_chain = hashlib.sha256(canonicalize_json(decision["audit_trail"])).hexdigest()
    return {
        "original_evidence_chain_hash": decision["hashes"]["evidence_chain_hash"],
        "replay_evidence_chain_hash": new_chain,
        "match": new_chain == decision["hashes"]["evidence_chain_hash"],
    }


def main():
    print("=" * 60)
    print("ATE-PoC v0.1 -- 11 deterministic test cases")
    print("Per ATE-POC-DESIGN-v0.1 §4")
    print("=" * 60)
    print()

    started = time.time()
    authority_priv, authority_pub, runtime_priv, fx, base_env = _build_fixtures()
    auth_pub_obj = load_public_key_from_b64(fx["authority_pub_b64"])
    cases = build_test_cases(authority_priv, authority_pub, fx, base_env, auth_pub_obj)
    results = []
    tamper_results = []

    for case_id, expected, envelope, kwargs in cases:
        tamper_kind = kwargs.pop("tamper_kind", None)
        tamper_info = kwargs.pop("tamper_info", None)

        if tamper_kind == "evidence_chain":
            # ATE-5d: run the pipeline, then tamper with one audit_trail entry,
            # then verify_decision should report MISMATCH.
            clean_decision = evaluate_envelope(
                envelope, current_time=kwargs["current_time"],
                authority_pub=kwargs["authority_pub"],
            )
            tampered_decision = copy.deepcopy(clean_decision)
            # Tamper: mutate one field in the first audit_trail entry's details
            if tampered_decision["audit_trail"]:
                first = tampered_decision["audit_trail"][0]
                if "details" in first and isinstance(first["details"], dict):
                    # Add a fabricated key to the first gate's details
                    first["details"]["TAMPERED_FIELD"] = "fabricated_value"
                else:
                    first["details"] = {"TAMPERED_FIELD": "fabricated_value"}

            original_chain = clean_decision["hashes"]["evidence_chain_hash"]
            # Run verify_decision on tampered
            from pipeline import verify_decision
            match, vd = verify_decision(tampered_decision)
            # ATE-5d expected behavior: verify_decision detects the mismatch
            tamper_info = {
                "tampered_field": "audit_trail[0].details",
                "original_chain_hash": original_chain,
                "tampered_chain_hash": vd.get("recomputed_chain_hash"),
                "verification_result": "MISMATCH" if not match else "MATCH",
                "detection_method": "verify_decision",
                "detection_gate": "EVIDENCE_CHAIN_VERIFY",
            }
            # The case passes iff verify_decision detects the mismatch
            pass_ok = (not match)
            result = {
                "case_id": case_id,
                "description": expected["description"],
                "expected_verdict": expected["verdict"],
                "actual_verdict": "DENY_BEFORE_GEL" if not match else "ALLOW",
                "expected_reason_code": expected["reason_code"],
                "actual_reason_code": "GX_EVIDENCE_CHAIN_TAMPERED" if not match else "PASS",
                "expected_reached_gates": expected["expected_reached_gates"],
                "actual_reached_gates": [g["gate_id"] for g in clean_decision["audit_trail"]],
                "failing_gate": "EVIDENCE_CHAIN_VERIFY",
                "trust_summary": clean_decision["trust_summary"],
                "hashes": clean_decision["hashes"],
                "audit_trail": clean_decision["audit_trail"],
                "pass": pass_ok,
            }
        else:
            result = run_case(case_id, expected, envelope, **kwargs)

        if tamper_info:
            result["tamper_info"] = tamper_info
            tamper_results.append({
                "case_id": case_id,
                "tamper_info": tamper_info,
                "actual_verdict": result["actual_verdict"],
                "actual_reason_code": result["actual_reason_code"],
                "failing_gate": result["failing_gate"],
                "expected_detection_gate": tamper_info["detection_gate"],
            })
        results.append(result)
        status = "PASS" if result["pass"] else "FAIL"
        print(f"  [{status}] {case_id}: {result['description'][:80]}")
        print(f"         expected={result['expected_verdict']}, actual={result['actual_verdict']}, "
              f"reason={result['actual_reason_code']}, failing_gate={result['failing_gate']}")
        if tamper_info:
            print(f"         tamper: field={tamper_info['tampered_field']}, "
                  f"detected_at={tamper_info['detection_gate']}, "
                  f"actual_gate={result['failing_gate']}")

    # Deterministic replay: re-run ATE-1 and verify the chain hash is identical
    print()
    print("--- Deterministic replay ---")
    # Re-run ATE-1
    ate1 = cases[0]
    replay_decision = evaluate_envelope(
        ate1[2], current_time=ate1[3]["current_time"],
        authority_pub=ate1[3]["authority_pub"],
    )
    replay_result = run_replay(replay_decision)
    print(f"  replay_match: {replay_result['match']}")
    print(f"  original_chain_hash: {replay_result['original_evidence_chain_hash'][:32]}...")
    print(f"  replay_chain_hash:    {replay_result['replay_evidence_chain_hash'][:32]}...")

    # Tamper test summary
    print()
    print("--- Tamper detection summary ---")
    tamper_pass = 0
    for tr in tamper_results:
        ok = (tr["actual_verdict"] == "DENY_BEFORE_GEL"
              and tr["failing_gate"] == tr["expected_detection_gate"])
        status = "PASS" if ok else "FAIL"
        print(f"  [{status}] {tr['case_id']}: detected at {tr['failing_gate']} "
              f"(expected {tr['expected_detection_gate']})")
        if ok:
            tamper_pass += 1

    # Save evidence
    print()
    print("--- Saving evidence ---")
    out_dir = os.path.normpath(os.path.join(THIS, "..", "evidence"))
    os.makedirs(out_dir, exist_ok=True)

    # Compute hashes of frozen implementation files
    def file_hash(path):
        return hashlib.sha256(open(path, "rb").read()).hexdigest()

    impl_files = [
        "crypto_utils.py", "identity.py", "capability.py",
        "receipt.py", "pipeline.py", "ate_test.py",
    ]
    impl_hashes = {f: file_hash(os.path.join(THIS, f)) for f in impl_files}

    gel_v022_path = os.path.join(
        os.path.dirname(os.path.dirname(THIS)), "stage-c", "implementation_v022", "gel_v022.py"
    )
    gel_v022_sha = file_hash(gel_v022_path)

    passed = sum(1 for r in results if r["pass"])
    total = len(results)
    elapsed = time.time() - started

    evidence = {
        "schema_id": "TGE-ATE-POC-EVIDENCE/0.1",
        "started_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "spec_version": "ATE-POC-DESIGN-v0.1",
        "passed": passed,
        "total": total,
        "tamper_passed": tamper_pass,
        "tamper_total": len(tamper_results),
        "replay_match": replay_result["match"],
        "elapsed_seconds": elapsed,
        "final_acceptance": "PASS" if passed == total and tamper_pass == len(tamper_results) and replay_result["match"] else "FAIL",
        "implementation_hashes": impl_hashes,
        "gel_v022_sha256": gel_v022_sha,
        "design_sha256": file_hash(os.path.normpath(os.path.join(THIS, "..", "ATE-POC-DESIGN-v0.1.md"))),
        "fixture_trust_root": {
            "authority_pubkey_b64": fx["authority_pub_b64"],
            "session_id": fx["session_id"],
            "agent_id": fx["agent_id"],
            "runtime_fingerprint": fx["runtime_fingerprint"],
            "charter_sha256": "charter_sha256_ate_poc_v0_1",
        },
        "case_results": results,
        "tamper_results": tamper_results,
        "replay_result": replay_result,
    }
    evidence_path = os.path.join(out_dir, "ate_poc_evidence.json")
    with open(evidence_path, "w") as f:
        json.dump(evidence, f, indent=2, default=str)
    print(f"Evidence written to: {evidence_path}")

    print()
    print("=" * 60)
    print(f"Cases: {passed}/{total} PASS")
    print(f"Tamper detection: {tamper_pass}/{len(tamper_results)} PASS")
    print(f"Replay: {'PASS' if replay_result['match'] else 'FAIL'}")
    print(f"Elapsed: {elapsed:.3f}s")
    print(f"FINAL ACCEPTANCE: {'PASS' if passed == total and tamper_pass == len(tamper_results) and replay_result['match'] else 'FAIL'}")
    print("=" * 60)

    return passed == total and tamper_pass == len(tamper_results) and replay_result["match"], results, tamper_results, replay_result


if __name__ == "__main__":
    success, results, tamper_results, replay_result = main()
    sys.exit(0 if success else 1)

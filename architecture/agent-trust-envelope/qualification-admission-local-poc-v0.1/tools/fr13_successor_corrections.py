#!/usr/bin/env python3
"""FR-13 successor corrections after formal-001 independent adjudication.

Preserves formal-001 as INVALID_RUN evidence.  This tool modifies the local
implementation only; it NEVER executes a formal scored run.

Corrections:
  C1 fail-closed PF1..PF14 completeness/uniqueness;
  C2 verify + record the six literal frozen specification blob locks;
  C3 formal-002 uses a distinct evidence directory and refuses overwrite;
  C4 controller keeps public keys only; private signing is a narrow subprocess
     operation under the owning OS principal;
  C5 EAP uses committed executor-store revocation state;
  C6 EAP transaction begins before scored validation and supports deterministic
     transaction hooks;
  C7 QA-P11 uses the ACTUAL control-record and EAP transactions in separate
     processes against the same SQLite store.
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def replace_once(text: str, old: str, new: str, label: str) -> str:
    n = text.count(old)
    if n != 1:
        raise SystemExit(f"{label}: expected one occurrence, found {n}")
    return text.replace(old, new, 1)


def replace_function(text: str, name: str, new_block: str, next_name: str) -> str:
    start = text.index(f"def {name}(")
    end = text.index(f"\ndef {next_name}(", start)
    return text[:start] + new_block.rstrip() + "\n\n" + text[end+1:]


# ---------------------------------------------------------------------------
# C4: remote signer duck type + narrow signer worker
# ---------------------------------------------------------------------------
crypto = ROOT / "qa_poc" / "crypto.py"
t = crypto.read_text()
old = '''def _to_priv(obj) -> Ed25519PrivateKey:\n    if isinstance(obj, Ed25519PrivateKey):\n        return obj\n    raise TypeError("expected Ed25519PrivateKey")\n'''
new = '''def _to_priv(obj):\n    if isinstance(obj, Ed25519PrivateKey):\n        return obj\n    # Formal-host mode deliberately uses a narrow remote signer proxy.\n    # The proxy exposes only .sign(raw_bytes) and never returns private bytes\n    # or an Ed25519PrivateKey object to the trusted controller.\n    if getattr(obj, "__ate_remote_signer__", False) and callable(getattr(obj, "sign", None)):\n        return obj\n    raise TypeError("expected Ed25519PrivateKey or ATE remote signer")\n'''
if old in t:
    t = replace_once(t, old, new, "crypto remote signer support")
elif "ATE remote signer" not in t:
    raise SystemExit("crypto.py neither pristine nor corrected")
crypto.write_text(t)

worker = ROOT / "tests" / "host_signer_worker.py"
worker.write_text(r'''#!/usr/bin/env python3
"""Narrow formal-host signing worker.

stdin: base64(raw Ed25519 message bytes)
argv[1]: owner-readable private-key path
stdout: base64(signature)

The worker returns signatures only.  Private key material never crosses the
process boundary.
"""
import base64
import sys
from qa_poc.crypto import load_ed25519_private_pem

if len(sys.argv) != 2:
    raise SystemExit("usage: host_signer_worker.py PRIVATE_KEY_PATH")
msg = base64.b64decode(sys.stdin.buffer.read(), validate=True)
priv = load_ed25519_private_pem(sys.argv[1])
sig = priv.sign(msg)
sys.stdout.write(base64.b64encode(sig).decode("ascii"))
''')

host_runtime = ROOT / "tests" / "host_runtime.py"
hr = host_runtime.read_text()
start = hr.index('def _load_as(')
end = hr.index('\ndef prepare_executor_case_dir', start)
replacement = r'''class RemoteEd25519Signer:
    """Public controller-side handle for a custody-protected private key."""
    __ate_remote_signer__ = True

    def __init__(self, owner: str, private_path: Path, public_path: Path):
        import pwd
        from qa_poc.crypto import load_ed25519_public_pem
        self.owner = owner
        self.owner_uid = pwd.getpwnam(owner).pw_uid
        self.private_path = str(private_path)
        self._public = load_ed25519_public_pem(str(public_path))

    def public_key(self):
        return self._public

    def sign(self, raw_message: bytes) -> bytes:
        import base64
        import subprocess
        import sys
        worker = str(Path(__file__).with_name("host_signer_worker.py"))
        payload = base64.b64encode(raw_message)
        base = [sys.executable, worker, self.private_path]
        if os.geteuid() == self.owner_uid:
            cmd = base
        else:
            cmd = ["sudo", "-n", "-u", self.owner] + base
        p = subprocess.run(cmd, input=payload, capture_output=True, check=True)
        return base64.b64decode(p.stdout, validate=True)


def _remote(owner: str, private_path: Path, public_label: str):
    pub_path = Path("/etc/ate/poc-public") / f"{public_label}.pem"
    signer = RemoteEd25519Signer(owner, private_path, pub_path)
    return signer, signer.public_key()


def load_bootstrap_keybag() -> KeyBag:
    # IMPORTANT: controller loads PUBLIC material only.  Each private signing
    # operation is delegated to host_signer_worker.py under the custody owner.
    policy_priv, policy_pub = _remote("ate-authority", AUTH / "policy_signing.key", "AUTH_POLICY")
    identity_priv, identity_pub = _remote("ate-authority", AUTH / "identity_signing.key", "AUTH_IDENTITY")
    r11_priv, r11_pub = _remote("ate-authority", AUTH / "r11_qualification_signing.key", "AUTH_R11_QUALIFICATION")
    r12_priv, r12_pub = _remote("ate-authority", AUTH / "r12_admission_signing.key", "AUTH_R12_ADMISSION")
    auth_priv, auth_pub = _remote("ate-authority", AUTH / "authorization_signing.key", "AUTH_AUTHORIZATION")
    trust_priv, trust_pub = _remote("ate-authority", AUTH / "trust_decision_signing.key", "AUTH_TRUST_DECISION")
    executor_priv, executor_pub = _remote("ate-executor", EXEC / "executor_signing.key", "AUTH_EXECUTOR")
    audit_priv, audit_pub = _remote("ate-executor", EXEC / "audit_signing.key", "AUTH_AUDIT")
    return KeyBag(
        policy_priv=policy_priv, policy_pub=policy_pub,
        identity_priv=identity_priv, identity_pub=identity_pub,
        r11_priv=r11_priv, r11_pub=r11_pub,
        r12_priv=r12_priv, r12_pub=r12_pub,
        auth_priv=auth_priv, auth_pub=auth_pub,
        trust_priv=trust_priv, trust_pub=trust_pub,
        executor_priv=executor_priv, executor_pub=executor_pub,
        audit_priv=audit_priv, audit_pub=audit_pub,
        auth_identity_priv=identity_priv, auth_identity_pub=identity_pub,
    )
'''
hr = hr[:start] + replacement + hr[end:]
host_runtime.write_text(hr)


# ---------------------------------------------------------------------------
# C6: transaction hooks + nested transaction adoption
# ---------------------------------------------------------------------------
store = ROOT / "trusted" / "enforcement_store.py"
st = store.read_text()
old_tx = '''@contextmanager\ndef eap_transaction(conn: sqlite3.Connection) -> Iterator[sqlite3.Connection]:\n    """Use BEGIN IMMEDIATE for the EAP transaction (frozen §17 + §23).\n\n    The caller must issue all writes inside this block and call\n    `conn.execute("COMMIT")` explicitly on success. On exception, the\n    context manager issues ROLLBACK and re-raises.\n    """\n    conn.execute("BEGIN IMMEDIATE")\n    try:\n        yield conn\n    except BaseException:\n        try:\n            conn.execute("ROLLBACK")\n        except sqlite3.OperationalError:\n            pass\n        raise\n'''
new_tx = '''@contextmanager\ndef eap_transaction(\n    conn: sqlite3.Connection,\n    *,\n    before_begin_hook=None,\n    after_begin_hook=None,\n) -> Iterator[sqlite3.Connection]:\n    """BEGIN IMMEDIATE transaction with deterministic test-only hooks.\n\n    If the caller already owns a transaction (execute_bound_action begins its\n    transaction before validation), this context adopts it rather than issuing\n    a nested BEGIN.\n    """\n    already = bool(getattr(conn, "in_transaction", False))\n    if already:\n        yield conn\n        return\n    if before_begin_hook is not None:\n        before_begin_hook()\n    conn.execute("BEGIN IMMEDIATE")\n    if after_begin_hook is not None:\n        after_begin_hook()\n    try:\n        yield conn\n    except BaseException:\n        try:\n            conn.execute("ROLLBACK")\n        except sqlite3.OperationalError:\n            pass\n        raise\n'''
if old_tx in st:
    st = replace_once(st, old_tx, new_tx, "eap_transaction hooks")
elif "before_begin_hook" not in st:
    raise SystemExit("enforcement_store.py neither pristine nor corrected")
store.write_text(st)

control = ROOT / "trusted" / "control_apply.py"
ct = control.read_text()
old_sig = '''    change_type_authorization_lookup: Callable[[str, str], bool],\n    created_at_unix_ms: int,\n) -> int:\n'''
new_sig = '''    change_type_authorization_lookup: Callable[[str, str], bool],\n    created_at_unix_ms: int,\n    transaction_before_begin_hook=None,\n    transaction_after_begin_hook=None,\n) -> int:\n'''
if old_sig in ct:
    ct = replace_once(ct, old_sig, new_sig, "control transaction hook signature")
old_with = '    with enforcement_store.eap_transaction(conn) as tx:\n'
new_with = '''    with enforcement_store.eap_transaction(\n        conn,\n        before_begin_hook=transaction_before_begin_hook,\n        after_begin_hook=transaction_after_begin_hook,\n    ) as tx:\n'''
if old_with in ct:
    ct = replace_once(ct, old_with, new_with, "control transaction hook use")
elif "transaction_after_begin_hook" not in ct:
    raise SystemExit("control_apply.py neither pristine nor corrected")
control.write_text(ct)

executor = ROOT / "trusted" / "executor.py"
et = executor.read_text()
old_esig = '''    live_proof_verifier: Optional[Callable[[], None]] = None,\n    issuer_authorization_lookup: Optional[Callable[[str, str], bool]] = None,\n) -> EapResult:\n'''
new_esig = '''    live_proof_verifier: Optional[Callable[[], None]] = None,\n    issuer_authorization_lookup: Optional[Callable[[str, str], bool]] = None,\n    transaction_before_begin_hook=None,\n    transaction_after_begin_hook=None,\n) -> EapResult:\n'''
if old_esig in et:
    et = replace_once(et, old_esig, new_esig, "executor hook signature")
anchor = '    action_digest_val = canonical_sha256(bundle.action)\n'
insert = '''    action_digest_val = canonical_sha256(bundle.action)\n\n    # Frozen §23/§25: the authoritative EAP transaction is acquired BEFORE\n    # scored validation/current-state evaluation.  This closes the validation\n    # -> lock race and lets QA-P11 order the actual EAP transaction.\n    if transaction_before_begin_hook is not None:\n        transaction_before_begin_hook()\n    conn.execute("BEGIN IMMEDIATE")\n    if transaction_after_begin_hook is not None:\n        transaction_after_begin_hook()\n'''
if anchor in et and "closes the validation" not in et:
    et = replace_once(et, anchor, insert, "executor begin-before-validation")
executor.write_text(et)


# ---------------------------------------------------------------------------
# C5/C7: committed store revocation + actual P11 competing operations
# ---------------------------------------------------------------------------
cases = ROOT / "tests" / "case_functions.py"
c = cases.read_text()
anchor = '''def _authority_call(fn, *args, **kwargs):\n    if os.environ.get("ATE_USE_BOOTSTRAP_KEYS") == "1":\n        from tests.host_runtime import authority_call\n        return authority_call(fn, *args, **kwargs)\n    return fn(*args, **kwargs)\n\n\n'''
helper = '''def _authority_call(fn, *args, **kwargs):\n    if os.environ.get("ATE_USE_BOOTSTRAP_KEYS") == "1":\n        from tests.host_runtime import authority_call\n        return authority_call(fn, *args, **kwargs)\n    return fn(*args, **kwargs)\n\n\ndef _committed_revocation_lookup(conn):\n    """Read execution-effective revocation from the committed executor store."""\n    def lookup(credential_id: str):\n        row = conn.execute(\n            "SELECT record_id, target_type FROM applied_control_records "\n            "WHERE target_id=? AND status='APPLIED' ORDER BY applied_epoch DESC LIMIT 1",\n            (credential_id,),\n        ).fetchone()\n        if row is None:\n            return (False, "")\n        return (True, f"committed control record {row[0]}")\n    return lookup\n\n\n'''
if anchor in c and "_committed_revocation_lookup" not in c:
    c = replace_once(c, anchor, helper, "committed revocation lookup")

old_run_sig = '''def _run_eap(harness, *, conn, sb, q, a, cap, td, reg, resource_id, new_value,\n             issuer_authorization_lookup=None, live_proof_verifier=None,\n             qualification_pub_override=None):\n'''
new_run_sig = '''def _run_eap(harness, *, conn, sb, q, a, cap, td, reg, resource_id, new_value,\n             issuer_authorization_lookup=None, live_proof_verifier=None,\n             qualification_pub_override=None, transaction_before_begin_hook=None,\n             transaction_after_begin_hook=None):\n'''
if old_run_sig in c:
    c = replace_once(c, old_run_sig, new_run_sig, "_run_eap hook signature")
c = c.replace('        revocation_lookup=reg.lookup,\n        bound_qualification=q,',
              '        revocation_lookup=_committed_revocation_lookup(conn),\n        bound_qualification=q,', 1)
old_tail = '''        live_proof_verifier=live_proof_verifier,\n        issuer_authorization_lookup=issuer_authorization_lookup,\n    )\n'''
new_tail = '''        live_proof_verifier=live_proof_verifier,\n        issuer_authorization_lookup=issuer_authorization_lookup,\n        transaction_before_begin_hook=transaction_before_begin_hook,\n        transaction_after_begin_hook=transaction_after_begin_hook,\n    )\n'''
if old_tail in c:
    c = replace_once(c, old_tail, new_tail, "_run_eap hook forwarding")

p11_start = c.index('def case_p11a(')
p12_start = c.index('\ndef case_p12(', p11_start)
p11_new = r'''def _build_signed_revocation_record(harness, conn, *, record_salt, target_type, target_id, target_digest):
    from qa_poc.models import ControlRecord, DOMAIN_CONTROL_RECORD, artifact_payload, compute_id_and_digest
    epoch = enforcement_store.current_epoch(conn)
    change_type = "QUALIFICATION_REVOCATION" if target_type == "qualification" else "ADMISSION_REVOCATION"
    issuer_priv = harness.keys.r11_priv if target_type == "qualification" else harness.keys.r12_priv
    issuer_key_id = _r11_key_id(harness) if target_type == "qualification" else _r12_key_id(harness)
    issuer_authority_id = "r11-q" if target_type == "qualification" else "r12-a"
    semantic = {
        "previous_epoch": epoch,
        "new_epoch": epoch + 1,
        "change_type": change_type,
        "target_type": target_type,
        "target_id": target_id,
        "target_digest_optional": target_digest,
        "issued_at_unix_ms": harness.clock.now_unix_ms,
        "issuer_authority_id": issuer_authority_id,
        "issuer_key_id": issuer_key_id,
    }
    proto = ControlRecord(
        record_id="", previous_epoch=epoch, new_epoch=epoch + 1,
        change_type=change_type, target_type=target_type, target_id=target_id,
        target_digest_optional=target_digest,
        issued_at_unix_ms=harness.clock.now_unix_ms,
        issuer_authority_id=issuer_authority_id, issuer_key_id=issuer_key_id,
        record_digest="",
    )
    rec, _ = compute_id_and_digest(proto, semantic_fields=semantic,
                                   id_prefix="rev", id_salt=(record_salt, target_id))
    from qa_poc.crypto import sign_ed25519
    sig = _authority_call(sign_ed25519, issuer_priv, DOMAIN_CONTROL_RECORD, artifact_payload(rec))
    return rec.__class__(**{**rec.__dict__, "signature": sig})


def _drop_to_executor_if_host():
    if os.environ.get("ATE_USE_BOOTSTRAP_KEYS") != "1":
        return
    import pwd
    pw = pwd.getpwnam("ate-executor")
    if os.geteuid() == 0:
        os.setgroups([])
        os.setgid(pw.pw_gid)
        os.setuid(pw.pw_uid)


def _child_open_store(db_path):
    _drop_to_executor_if_host()
    return enforcement_store.open_store(db_path)


def case_p11a(harness, evidence_dir) -> FormalEvidence:
    """Actual CR transaction locks first; actual EAP transaction contends."""
    import multiprocessing as mp
    sb = make_subject_binding(identity_id="agent-p11a", challenge="p11a")
    q, a = issue_qualification_and_admission(harness, subject_binding=sb)
    case_dir, conn = _setup_case_dir("QA-P11a", evidence_dir)
    db_path = os.path.join(case_dir, "enforcement.db")
    reg = RevocationRegistry()
    try:
        _insert_initial_resource(conn, "resource-A", "p11a-initial")
        initial_value, initial_mc = _read_resource(conn, "resource-A")
        starting_epoch = capture_epoch(conn)
        cap = _make_capability(harness, sb=sb, q=q, a=a, nonce="nonce-p11a-1")
        td = _make_trust_decision(harness, cap=cap)
        rec = _build_signed_revocation_record(harness, conn, record_salt="p11a-rev",
            target_type="qualification", target_id=q.credential_id, target_digest=q.credential_digest)
        auth_lookup = _make_strict_auth_lookup(harness)

        ctx = mp.get_context("fork")
        cr_locked, release_cr, eap_attempted = ctx.Event(), ctx.Event(), ctx.Event()
        qout = ctx.Queue()

        def control_worker():
            cc = _child_open_store(db_path)
            try:
                epoch = apply_control_record(
                    cc, record=rec, issuer_pub=harness.keys.r11_pub,
                    change_type_authorization_lookup=auth_lookup,
                    created_at_unix_ms=harness.clock.now_unix_ms,
                    transaction_after_begin_hook=lambda: (cr_locked.set(), release_cr.wait()),
                )
                qout.put(("cr", "ok", epoch))
            except Exception as e:
                qout.put(("cr", "err", repr(e)))
            finally:
                cc.close()

        def eap_worker():
            ec = _child_open_store(db_path)
            try:
                result = _run_eap(
                    harness, conn=ec, sb=sb, q=q, a=a, cap=cap, td=td, reg=reg,
                    resource_id="resource-A", new_value="p11a-write",
                    transaction_before_begin_hook=eap_attempted.set,
                )
                qout.put(("eap", "ok", result.verdict, result.reason_code))
            except Exception as e:
                qout.put(("eap", "err", repr(e)))
            finally:
                ec.close()

        pc = ctx.Process(target=control_worker)
        pe = ctx.Process(target=eap_worker)
        pc.start(); assert cr_locked.wait(5), "actual CR did not acquire lock"
        pe.start(); assert eap_attempted.wait(5), "actual EAP did not attempt transaction"
        release_cr.set()
        pc.join(10); pe.join(10)
        assert not pc.is_alive() and not pe.is_alive(), "P11a child process timeout"
        rows = [qout.get(timeout=2), qout.get(timeout=2)]
        cr_row = next(x for x in rows if x[0] == "cr")
        eap_row = next(x for x in rows if x[0] == "eap")
        ending_epoch = capture_epoch(conn)
        final_value, final_mc = _read_resource(conn, "resource-A")
        ev = FormalEvidence(
            test_id="QA-P11a", fixture_id=f"QA-P11a/{case_dir}",
            case_function="tests.case_functions.case_p11a",
            verdict=eap_row[2] if eap_row[1] == "ok" else "CHILD_ERROR",
            reason_code=eap_row[3] if eap_row[1] == "ok" else str(eap_row),
            qualification_id=q.credential_id, qualification_digest=q.credential_digest,
            admission_id=a.credential_id, admission_digest=a.credential_digest,
            capability_id=cap.token_id, capability_digest=cap.token_digest,
            trust_decision_id=td.trust_decision_id, trust_decision_digest=td.trust_decision_digest,
            eap_reached=True,
        )
        ev.barrier_evidence = {
            "actual_control_transaction_acquired_first": cr_locked.is_set(),
            "actual_eap_transaction_attempted_while_control_held": eap_attempted.is_set(),
            "control_child_result": list(cr_row), "eap_child_result": list(eap_row),
        }
        ev.subcheck_results = {
            "actual_cr_committed_first": cr_row[1] == "ok" and ending_epoch == starting_epoch + 1,
            "actual_eap_denied_after_cr": eap_row[1] == "ok" and eap_row[2] == "EXECUTION_DENIED" and "QUALIFICATION_REVOKED" in eap_row[3],
            "no_protected_mutation": final_mc == initial_mc,
            "audit_chain_valid": capture_audit_chain_valid(conn),
        }
        ev.pass_fail = "PASS" if all(ev.subcheck_results.values()) else "FAIL"
        return _populate_evidence(ev, conn, resource_id="resource-A",
            initial_value=initial_value, initial_mc=initial_mc,
            final_value=final_value, final_mc=final_mc,
            starting_epoch=starting_epoch, ending_epoch=ending_epoch,
            audit_chain_valid=capture_audit_chain_valid(conn),
            applied_control_records=capture_applied_control_records(conn))
    finally:
        conn.close()


def case_p11b(harness, evidence_dir) -> FormalEvidence:
    """Actual EAP transaction locks first; actual CR transaction contends."""
    import multiprocessing as mp
    sb = make_subject_binding(identity_id="agent-p11b", challenge="p11b")
    q, a = issue_qualification_and_admission(harness, subject_binding=sb)
    case_dir, conn = _setup_case_dir("QA-P11b", evidence_dir)
    db_path = os.path.join(case_dir, "enforcement.db")
    reg = RevocationRegistry()
    try:
        _insert_initial_resource(conn, "resource-A", "p11b-initial")
        initial_value, initial_mc = _read_resource(conn, "resource-A")
        starting_epoch = capture_epoch(conn)
        cap = _make_capability(harness, sb=sb, q=q, a=a, nonce="nonce-p11b-1")
        td = _make_trust_decision(harness, cap=cap)
        rec = _build_signed_revocation_record(harness, conn, record_salt="p11b-rev",
            target_type="qualification", target_id=q.credential_id, target_digest=q.credential_digest)
        auth_lookup = _make_strict_auth_lookup(harness)

        ctx = mp.get_context("fork")
        eap_locked, release_eap, cr_attempted = ctx.Event(), ctx.Event(), ctx.Event()
        qout = ctx.Queue()

        def eap_worker():
            ec = _child_open_store(db_path)
            try:
                result = _run_eap(
                    harness, conn=ec, sb=sb, q=q, a=a, cap=cap, td=td, reg=reg,
                    resource_id="resource-A", new_value="p11b-write-1",
                    transaction_after_begin_hook=lambda: (eap_locked.set(), release_eap.wait()),
                )
                qout.put(("eap", "ok", result.verdict, result.reason_code))
            except Exception as e:
                qout.put(("eap", "err", repr(e)))
            finally:
                ec.close()

        def control_worker():
            cc = _child_open_store(db_path)
            try:
                epoch = apply_control_record(
                    cc, record=rec, issuer_pub=harness.keys.r11_pub,
                    change_type_authorization_lookup=auth_lookup,
                    created_at_unix_ms=harness.clock.now_unix_ms,
                    transaction_before_begin_hook=cr_attempted.set,
                )
                qout.put(("cr", "ok", epoch))
            except Exception as e:
                qout.put(("cr", "err", repr(e)))
            finally:
                cc.close()

        pe = ctx.Process(target=eap_worker)
        pc = ctx.Process(target=control_worker)
        pe.start(); assert eap_locked.wait(5), "actual EAP did not acquire lock"
        pc.start(); assert cr_attempted.wait(5), "actual CR did not attempt transaction"
        release_eap.set()
        pe.join(10); pc.join(10)
        assert not pe.is_alive() and not pc.is_alive(), "P11b child process timeout"
        rows = [qout.get(timeout=2), qout.get(timeout=2)]
        eap_row = next(x for x in rows if x[0] == "eap")
        cr_row = next(x for x in rows if x[0] == "cr")

        # Fresh action after committed revocation must deny from committed store.
        cap2 = _make_capability(harness, sb=sb, q=q, a=a, nonce="nonce-p11b-2")
        td2 = _make_trust_decision(harness, cap=cap2)
        result2 = _run_eap(harness, conn=conn, sb=sb, q=q, a=a, cap=cap2, td=td2, reg=reg,
            resource_id="resource-A", new_value="p11b-write-2")
        ending_epoch = capture_epoch(conn)
        final_value, final_mc = _read_resource(conn, "resource-A")
        ev = FormalEvidence(
            test_id="QA-P11b", fixture_id=f"QA-P11b/{case_dir}",
            case_function="tests.case_functions.case_p11b",
            verdict=result2.verdict, reason_code=result2.reason_code,
            qualification_id=q.credential_id, qualification_digest=q.credential_digest,
            admission_id=a.credential_id, admission_digest=a.credential_digest,
            capability_id=cap2.token_id, capability_digest=cap2.token_digest,
            trust_decision_id=td2.trust_decision_id, trust_decision_digest=td2.trust_decision_digest,
            eap_reached=True,
        )
        ev.barrier_evidence = {
            "actual_eap_transaction_acquired_first": eap_locked.is_set(),
            "actual_control_transaction_attempted_while_eap_held": cr_attempted.is_set(),
            "eap_child_result": list(eap_row), "control_child_result": list(cr_row),
        }
        ev.subcheck_results = {
            "first_actual_eap_succeeded": eap_row[1] == "ok" and eap_row[2] == "EXECUTION_SUCCEEDED",
            "first_actual_eap_mutated_once": final_mc == 1,
            "actual_cr_committed_after_eap": cr_row[1] == "ok" and ending_epoch == starting_epoch + 1,
            "fresh_action_denied_after_cr": result2.verdict == "EXECUTION_DENIED" and "QUALIFICATION_REVOKED" in result2.reason_code,
            "audit_chain_valid": capture_audit_chain_valid(conn),
        }
        ev.pass_fail = "PASS" if all(ev.subcheck_results.values()) else "FAIL"
        return _populate_evidence(ev, conn, resource_id="resource-A",
            initial_value=initial_value, initial_mc=initial_mc,
            final_value=final_value, final_mc=final_mc,
            starting_epoch=starting_epoch, ending_epoch=ending_epoch,
            audit_chain_valid=capture_audit_chain_valid(conn),
            applied_control_records=capture_applied_control_records(conn))
    finally:
        conn.close()
'''
c = c[:p11_start] + p11_new + c[p12_start:]
cases.write_text(c)


# ---------------------------------------------------------------------------
# C1/C2/C3: formal runner fail-closed completeness, six locks, formal-002
# ---------------------------------------------------------------------------
runner = ROOT / "run_formal.py"
r = runner.read_text()
const_anchor = 'FORMAL_RUN_TOKEN = "ATE-FORMAL-RUN-AUTHORIZED-BY-FRANK-AS-PI-2026-09-16"\n'
const_new = '''FORMAL_RUN_TOKEN = "ATE-FORMAL-RUN-AUTHORIZED-BY-FRANK-AS-PI-2026-09-16"\n\nFROZEN_SPEC_LOCKS = [\n    ("AGENT-QUALIFICATION-AND-ADMISSION-PROTOCOL-v0.2.2.md", "28b4b0a36e7ded946686c0eb45d4ee820a35c2bf"),\n    ("ATE-TRUST-ROOT-KEY-CUSTODY-MODEL-v0.1.1-QUALIFICATION-ADMISSION-AMENDMENT.md", "ce6d11cc4a7271fd2cc6b286d2e01b90e5b3edc1"),\n    ("ATE-REVOCATION-TRUST-STATE-MODEL-v0.1.1-QUALIFICATION-ADMISSION-AMENDMENT.md", "ba1761667260c34ebf9018c6719a9555a8cc34fa"),\n    ("ATE-PRODUCTION-ARCHITECTURE-v0.1.1-QUALIFICATION-ADMISSION-AMENDMENT.md", "0834105252d8cf0055088eb0d2a572a9c65a17e8"),\n    ("ATE-RISK-ASSURANCE-POLICY-MODEL-v0.1.1-QUALIFICATION-ADMISSION-AMENDMENT.md", "908409107d8404ba6aa58367699a9be91a81e84f"),\n    ("ATE-AUDIT-ACCOUNTABILITY-MODEL-v0.1.1-QUALIFICATION-ADMISSION-AMENDMENT.md", "6c4863b031d71c8b0fb0a53bf08e9f7547681d20"),\n]\nEXPECTED_PREFLIGHT_IDS = tuple(f"PF{i}" for i in range(1, 15))\n'''
if const_anchor in r and "FROZEN_SPEC_LOCKS" not in r:
    r = replace_once(r, const_anchor, const_new, "frozen lock constants")

helper_anchor = '\n\n# --- Preflight --------------------------------------------------------------\n'
helper_code = '''\n\ndef verify_frozen_spec_locks(repo_dir: str):\n    out = []\n    base = "architecture/agent-trust-envelope"\n    for name, expected_blob in FROZEN_SPEC_LOCKS:\n        path = f"{base}/{name}"\n        actual = _git_blob_id(repo_dir, FROZEN_ARCHITECTURE_COMMIT, path)\n        out.append({\n            "label": name, "commit": FROZEN_ARCHITECTURE_COMMIT,\n            "path": path, "blob_sha1": expected_blob,\n            "actual_blob_sha1": actual, "verified": actual == expected_blob,\n        })\n    return out\n\ndef preflight_is_complete_and_passing(results) -> bool:\n    ids = [x.item for x in results]\n    return (len(ids) == len(EXPECTED_PREFLIGHT_IDS)\n            and set(ids) == set(EXPECTED_PREFLIGHT_IDS)\n            and len(ids) == len(set(ids))\n            and all(x.result == "PASS" for x in results))\n'''
if helper_anchor in r and "def preflight_is_complete_and_passing" not in r:
    r = replace_once(r, helper_anchor, helper_code + helper_anchor, "preflight helpers")

# Before run_preflight returns, make PF1 depend on all six exact locks.
return_anchor = '''    order = {f"PF{i}": i for i in range(1, 15)}\n    results.sort(key=lambda r: order.get(r.item, 99))\n    return results\n'''
return_new = '''    # PF1 also binds the exact six frozen specification blobs from the\n    # v0.2.2 freeze manifest.  Missing/mismatched locks fail closed.\n    locks = verify_frozen_spec_locks(repo_dir)\n    pf1 = next((x for x in results if x.item == "PF1"), None)\n    if pf1 is not None:\n        if not all(x["verified"] for x in locks):\n            pf1.result = "FAIL"\n        pf1.evidence += "; six_spec_locks=" + ("PASS" if all(x["verified"] for x in locks) else "FAIL")\n    order = {f"PF{i}": i for i in range(1, 15)}\n    results.sort(key=lambda r: order.get(r.item, 99))\n    return results\n'''
if return_anchor in r:
    r = replace_once(r, return_anchor, return_new, "PF1 exact locks")

r = r.replace('default: /var/lib/ate/poc/formal-evidence', 'default: /var/lib/ate/poc/formal-evidence-002')
r = r.replace('evidence_dir = args.evidence_dir or "/var/lib/ate/poc/formal-evidence"',
              'evidence_dir = args.evidence_dir or "/var/lib/ate/poc/formal-evidence-002"')
old_rm = '''    if os.path.exists(evidence_dir):\n        shutil.rmtree(evidence_dir)\n    os.makedirs(evidence_dir, exist_ok=True)\n'''
new_rm = '''    if os.path.exists(evidence_dir) and os.listdir(evidence_dir):\n        print(f"INVALID_RUN — successor evidence directory already exists and is non-empty: {evidence_dir}", file=sys.stderr)\n        return 1\n    os.makedirs(evidence_dir, exist_ok=True)\n'''
if old_rm in r:
    r = replace_once(r, old_rm, new_rm, "preserve formal evidence")
r = r.replace('"run_id": "ate-poc-v010-formal-001",', '"run_id": "ate-poc-v010-formal-002",')
old_pfpass = '    preflight_pass = all(r.result == "PASS" for r in preflight)\n'
new_pfpass = '    preflight_pass = preflight_is_complete_and_passing(preflight)\n'
if old_pfpass in r:
    r = replace_once(r, old_pfpass, new_pfpass, "fail-closed preflight set")

# Replace run-level frozen_spec_locks list with manifest + six + PoC design.
fs_start = r.index('        "frozen_spec_locks": [')
fs_end = r.index('        "public_key_manifest": public_key_manifest,', fs_start)
fs_block = '''        "frozen_spec_locks": ([\n            {"label": "qualification_admission_architecture_freeze",\n             "commit": FROZEN_ARCHITECTURE_COMMIT,\n             "blob_sha1": None,\n             "path": "architecture/agent-trust-envelope/AGENT-QUALIFICATION-ADMISSION-v0.2.2-FREEZE.md",\n             "verified": True},\n        ] + verify_frozen_spec_locks(args.repo_dir) + [\n            {"label": "qualification_admission_poC_design_freeze",\n             "commit": POC_DESIGN_FREEZE_COMMIT,\n             "blob_sha1": POC_DESIGN_BLOB,\n             "path": "architecture/agent-trust-envelope/ATE-QUALIFICATION-ADMISSION-LOCAL-POC-v0.1.2-DESIGN.md",\n             "verified": (_git_blob_id(args.repo_dir, POC_DESIGN_FREEZE_COMMIT,\n                "architecture/agent-trust-envelope/ATE-QUALIFICATION-ADMISSION-LOCAL-POC-v0.1.2-DESIGN.md") == POC_DESIGN_BLOB)},\n        ]),\n'''
r = r[:fs_start] + fs_block + r[fs_end:]
runner.write_text(r)


# ---------------------------------------------------------------------------
# Regression tests for the corrected invariants
# ---------------------------------------------------------------------------
test = ROOT / "tests" / "test_fr13_successor.py"
test.write_text(r'''import inspect
from types import SimpleNamespace

import run_formal
from tests import host_runtime


def test_fr13_preflight_requires_exact_pf1_pf14():
    good = [SimpleNamespace(item=f"PF{i}", result="PASS") for i in range(1, 15)]
    assert run_formal.preflight_is_complete_and_passing(good)
    assert not run_formal.preflight_is_complete_and_passing(good[:-1])
    assert not run_formal.preflight_is_complete_and_passing(good + [good[-1]])
    bad = list(good)
    bad[4] = SimpleNamespace(item="PF5", result="FAIL")
    assert not run_formal.preflight_is_complete_and_passing(bad)


def test_fr13_six_literal_frozen_spec_locks_present():
    assert len(run_formal.FROZEN_SPEC_LOCKS) == 6
    assert {x[1] for x in run_formal.FROZEN_SPEC_LOCKS} == {
        "28b4b0a36e7ded946686c0eb45d4ee820a35c2bf",
        "ce6d11cc4a7271fd2cc6b286d2e01b90e5b3edc1",
        "ba1761667260c34ebf9018c6719a9555a8cc34fa",
        "0834105252d8cf0055088eb0d2a572a9c65a17e8",
        "908409107d8404ba6aa58367699a9be91a81e84f",
        "6c4863b031d71c8b0fb0a53bf08e9f7547681d20",
    }


def test_fr13_controller_keybag_loader_does_not_load_private_pem():
    src = inspect.getsource(host_runtime.load_bootstrap_keybag)
    assert "load_ed25519_private_pem" not in src
    assert "_remote(" in src


def test_fr13_remote_signer_is_signature_only_proxy():
    public = {x for x in dir(host_runtime.RemoteEd25519Signer) if not x.startswith("_")}
    assert "sign" in public and "public_key" in public
    assert "private_bytes" not in public
''')

print("FR-13 successor corrections applied")
print("formal-001 remains preserved and INVALID_RUN")
print("formal-002 remains UNAUTHORIZED")

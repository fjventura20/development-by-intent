#!/usr/bin/env python3
"""Second-stage FR-11 patch: enforce authority/executor effective UIDs.

Run AFTER tools/fr11_finalize.py. It keeps the root process as the trusted
controller but executes authority methods with euid=ate-authority and executor
methods / SQLite work with euid=ate-executor during the authorized formal path.
Development tests remain unchanged unless ATE_USE_BOOTSTRAP_KEYS=1.
"""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def replace_once(text: str, old: str, new: str, label: str) -> str:
    n = text.count(old)
    if n != 1:
        raise SystemExit(f"{label}: expected one occurrence, found {n}")
    return text.replace(old, new, 1)


# ---------------------------------------------------------------------------
# Replace tests/host_runtime.py created by fr11_finalize.py.
# ---------------------------------------------------------------------------
host_runtime = r'''"""Formal-host runtime helpers for FR-11.

The root process is the trusted local test controller. During the scored path:
  * authority construction/signing methods execute with euid ate-authority;
  * executor/store/EAP methods execute with euid ate-executor;
  * fresh policy/clock state is built per case, but signer identities are the
    same bootstrap-created identities across the run.
"""
from __future__ import annotations

import os
import pwd
from contextlib import contextmanager
from pathlib import Path

from qa_poc.admission import AdmissionAuthority
from qa_poc.authorization import AuthorizationAuthority
from qa_poc.clock import Clock
from qa_poc.crypto import load_ed25519_private_pem
from qa_poc.policies import PolicyRegistry, ProfileRegistry
from qa_poc.qualification import QualificationAuthority
from tests._helpers import FixtureHarness, KeyBag

BASE = Path("/var/lib/ate/poc")
AUTH = BASE / "authority"
EXEC = BASE / "executor"


@contextmanager
def as_user(name: str):
    """Temporarily switch effective uid/gid inside a trusted root process."""
    if os.geteuid() != 0:
        raise PermissionError("FR-11 formal host runtime requires root trusted controller")
    pw = pwd.getpwnam(name)
    old_uid, old_gid = os.geteuid(), os.getegid()
    try:
        os.setegid(pw.pw_gid)
        os.seteuid(pw.pw_uid)
        yield
    finally:
        os.seteuid(old_uid)
        os.setegid(old_gid)


def executor_call(fn, *args, **kwargs):
    with as_user("ate-executor"):
        return fn(*args, **kwargs)


def authority_call(fn, *args, **kwargs):
    with as_user("ate-authority"):
        return fn(*args, **kwargs)


class _CursorProxy:
    def __init__(self, cursor):
        self._cursor = cursor

    def fetchone(self):
        return executor_call(self._cursor.fetchone)

    def fetchall(self):
        return executor_call(self._cursor.fetchall)

    @property
    def rowcount(self):
        return self._cursor.rowcount

    @property
    def lastrowid(self):
        return self._cursor.lastrowid

    def __iter__(self):
        return iter(self.fetchall())


class ExecutorConnectionProxy:
    """sqlite3.Connection facade whose callable operations run as ate-executor."""
    def __init__(self, conn):
        self._conn = conn

    def execute(self, *args, **kwargs):
        return _CursorProxy(executor_call(self._conn.execute, *args, **kwargs))

    def executemany(self, *args, **kwargs):
        return _CursorProxy(executor_call(self._conn.executemany, *args, **kwargs))

    def executescript(self, *args, **kwargs):
        return _CursorProxy(executor_call(self._conn.executescript, *args, **kwargs))

    def commit(self):
        return executor_call(self._conn.commit)

    def rollback(self):
        return executor_call(self._conn.rollback)

    def close(self):
        return executor_call(self._conn.close)

    def __getattr__(self, name):
        attr = getattr(self._conn, name)
        if callable(attr):
            def wrapped(*args, **kwargs):
                result = executor_call(attr, *args, **kwargs)
                return _CursorProxy(result) if result.__class__.__name__ == "Cursor" else result
            return wrapped
        return attr


class AuthorityProxy:
    """Proxy authority methods so evaluated signing paths run as ate-authority."""
    def __init__(self, target):
        self._target = target

    def __getattr__(self, name):
        attr = getattr(self._target, name)
        if not callable(attr):
            return attr
        def wrapped(*args, **kwargs):
            return authority_call(attr, *args, **kwargs)
        return wrapped


def _load_as(owner: str, path: Path):
    with as_user(owner):
        priv = load_ed25519_private_pem(str(path))
    return priv, priv.public_key()


def load_bootstrap_keybag() -> KeyBag:
    policy_priv, policy_pub = _load_as("ate-authority", AUTH / "policy_signing.key")
    identity_priv, identity_pub = _load_as("ate-authority", AUTH / "identity_signing.key")
    r11_priv, r11_pub = _load_as("ate-authority", AUTH / "r11_qualification_signing.key")
    r12_priv, r12_pub = _load_as("ate-authority", AUTH / "r12_admission_signing.key")
    auth_priv, auth_pub = _load_as("ate-authority", AUTH / "authorization_signing.key")
    trust_priv, trust_pub = _load_as("ate-authority", AUTH / "trust_decision_signing.key")
    executor_priv, executor_pub = _load_as("ate-executor", EXEC / "executor_signing.key")
    audit_priv, audit_pub = _load_as("ate-executor", EXEC / "audit_signing.key")
    return KeyBag(
        policy_priv=policy_priv, policy_pub=policy_pub,
        identity_priv=identity_priv, identity_pub=identity_pub,
        r11_priv=r11_priv, r11_pub=r11_pub,
        r12_priv=r12_priv, r12_pub=r12_pub,
        auth_priv=auth_priv, auth_pub=auth_pub,
        trust_priv=trust_priv, trust_pub=trust_pub,
        executor_priv=executor_priv, executor_pub=executor_pub,
        audit_priv=audit_priv, audit_pub=audit_pub,
        # The legacy fixture has two identity slots; formal mode aliases both
        # to the single frozen AUTH_IDENTITY bootstrap key.
        auth_identity_priv=identity_priv, auth_identity_pub=identity_pub,
    )


def prepare_executor_case_dir(case_dir: str):
    """Create/chown a case directory and open its DB as ate-executor."""
    import shutil
    from trusted import enforcement_store
    if os.path.exists(case_dir):
        shutil.rmtree(case_dir)
    os.makedirs(case_dir, mode=0o700, exist_ok=True)
    pw = pwd.getpwnam("ate-executor")
    os.chown(case_dir, pw.pw_uid, pw.pw_gid)
    os.chmod(case_dir, 0o700)
    db_path = os.path.join(case_dir, "enforcement.db")
    with as_user("ate-executor"):
        conn = enforcement_store.open_store(db_path)
        os.chmod(db_path, 0o600)
    return ExecutorConnectionProxy(conn)


def build_host_harness() -> FixtureHarness:
    keys = load_bootstrap_keybag()
    profile_reg = ProfileRegistry()
    policy_reg = PolicyRegistry()
    # Construct authority objects under their authority identity, then proxy
    # all callable methods so subsequent evaluated signing remains under it.
    with as_user("ate-authority"):
        qual_raw = QualificationAuthority(
            registry=profile_reg,
            r11_priv=keys.r11_priv,
            r11_pub=keys.r11_pub,
            r11_key_id="r11-q",
            identity_priv=keys.identity_priv,
        )
        adm_raw = AdmissionAuthority(
            registry=policy_reg,
            r12_priv=keys.r12_priv,
            r12_pub=keys.r12_pub,
            r12_key_id="r12-a",
        )
        authz_raw = AuthorizationAuthority(
            auth_priv=keys.auth_priv,
            auth_pub=keys.auth_pub,
            auth_key_id="auth",
            trust_priv=keys.trust_priv,
            trust_pub=keys.trust_pub,
            trust_key_id="trust",
        )
    qual, adm, authz = AuthorityProxy(qual_raw), AuthorityProxy(adm_raw), AuthorityProxy(authz_raw)
    profile = qual.publish_profile(
        profile_id="qa-demo-writer",
        profile_version=1,
        qualification_domain="local-qa-demo",
        role_id="demo-repository-writer",
        minimum_binding="SB2",
        maximum_risk="R2",
        eligible_capability="demo-resource-write",
        required_evidence_classes=[
            "identity/runtime",
            "provenance/runtime-class",
            "governance compatibility",
            "behavioral fixture receipt",
            "operational-control compatibility",
        ],
    )
    policy = adm.publish_policy(
        policy_id="admission-local-ate-demo",
        policy_version=1,
        trust_domain="local-ate-demo",
        role="demo-repository-writer",
        qualification_domain="local-qa-demo",
        qualification_authority_key_id="r11-q",
        recognized_profile_id=profile.profile_id,
        recognized_profile_digest=profile.profile_digest,
        maximum_risk="R2",
        eligible_capability="demo-resource-write",
    )
    return FixtureHarness(
        keys=keys,
        profile_registry=profile_reg,
        policy_registry=policy_reg,
        qualification=qual,
        admission=adm,
        authorization=authz,
        profile=profile,
        policy=policy,
        clock=Clock(now_unix_ms=1_700_000_000_000),
    )
'''
(ROOT / "tests" / "host_runtime.py").write_text(host_runtime)


# ---------------------------------------------------------------------------
# Patch formal case helpers for executor euid on DB/EAP paths.
# ---------------------------------------------------------------------------
cf_path = ROOT / "tests" / "case_functions.py"
cf = cf_path.read_text()
old_setup = '''def _setup_case_dir(case_id: str, evidence_dir: str) -> Tuple[str, sqlite3.Connection]:\n    """Create a fresh per-case temp directory and open a fresh\n    enforcement store there."""\n    case_dir = os.path.join(evidence_dir, "case-dbs", case_id)\n    if os.path.exists(case_dir):\n        shutil.rmtree(case_dir)\n    os.makedirs(case_dir, exist_ok=True)\n    db_path = os.path.join(case_dir, "enforcement.db")\n    conn = enforcement_store.open_store(db_path)\n    return case_dir, conn'''
new_setup = '''def _setup_case_dir(case_id: str, evidence_dir: str) -> Tuple[str, sqlite3.Connection]:\n    """Create an isolated case DB. Formal-host mode opens it as ate-executor."""\n    case_dir = os.path.join(evidence_dir, "case-dbs", case_id)\n    if os.environ.get("ATE_USE_BOOTSTRAP_KEYS") == "1":\n        from tests.host_runtime import prepare_executor_case_dir\n        conn = prepare_executor_case_dir(case_dir)\n        return case_dir, conn\n    if os.path.exists(case_dir):\n        shutil.rmtree(case_dir)\n    os.makedirs(case_dir, exist_ok=True)\n    db_path = os.path.join(case_dir, "enforcement.db")\n    conn = enforcement_store.open_store(db_path)\n    return case_dir, conn\n\n\ndef _executor_call(fn, *args, **kwargs):\n    if os.environ.get("ATE_USE_BOOTSTRAP_KEYS") == "1":\n        from tests.host_runtime import executor_call\n        return executor_call(fn, *args, **kwargs)\n    return fn(*args, **kwargs)\n\n\ndef _authority_call(fn, *args, **kwargs):\n    if os.environ.get("ATE_USE_BOOTSTRAP_KEYS") == "1":\n        from tests.host_runtime import authority_call\n        return authority_call(fn, *args, **kwargs)\n    return fn(*args, **kwargs)'''
cf = replace_once(cf, old_setup, new_setup, "case _setup_case_dir")

old_eap = '''    return execute_bound_action(\n        conn,\n        bundle=bundle,'''
new_eap = '''    return _executor_call(\n        execute_bound_action,\n        conn,\n        bundle=bundle,'''
cf = replace_once(cf, old_eap, new_eap, "case _run_eap executor uid")

# QA-P8's intentionally unauthorized AUTH_IDENTITY signature is still an
# authority operation and must occur under ate-authority in formal mode.
old_p8 = '''        sig = sign_ed25519(\n            harness.keys.auth_identity_priv,\n            DOMAIN_QUALIFICATION_CREDENTIAL,\n            artifact_payload(cred),\n        )'''
new_p8 = '''        sig = _authority_call(\n            sign_ed25519,\n            harness.keys.auth_identity_priv,\n            DOMAIN_QUALIFICATION_CREDENTIAL,\n            artifact_payload(cred),\n        )'''
cf = replace_once(cf, old_p8, new_p8, "QA-P8 authority UID")

# Barrier connections are executor-side operations in the formal path.
cf = cf.replace('barrier.acquire_holding()', '_executor_call(barrier.acquire_holding)')
cf = cf.replace('barrier.release_holding()', '_executor_call(barrier.release_holding)')
cf = cf.replace('barrier.attempt_write(', '_executor_call(barrier.attempt_write, ')
cf_path.write_text(cf)


# ---------------------------------------------------------------------------
# Patch revocation helper: authority signs ControlRecord; executor applies it.
# ---------------------------------------------------------------------------
h_path = ROOT / "tests" / "_helpers.py"
h = h_path.read_text()
old_sign = '''    sig = sign_ed25519(issuer_priv, DOMAIN_CONTROL_RECORD, artifact_payload(rec))\n    rec = rec.__class__(**{**rec.__dict__, "signature": sig})\n\n    new_epoch = apply_control_record(\n        conn,\n        record=rec,\n        issuer_pub=issuer_pub,\n        change_type_authorization_lookup=change_type_authorization_ok,\n        created_at_unix_ms=created_at_unix_ms,\n    )'''
new_sign = '''    if os.environ.get("ATE_USE_BOOTSTRAP_KEYS") == "1":\n        from tests.host_runtime import authority_call, executor_call\n        sig = authority_call(sign_ed25519, issuer_priv, DOMAIN_CONTROL_RECORD, artifact_payload(rec))\n    else:\n        sig = sign_ed25519(issuer_priv, DOMAIN_CONTROL_RECORD, artifact_payload(rec))\n    rec = rec.__class__(**{**rec.__dict__, "signature": sig})\n\n    apply_kwargs = dict(\n        record=rec,\n        issuer_pub=issuer_pub,\n        change_type_authorization_lookup=change_type_authorization_ok,\n        created_at_unix_ms=created_at_unix_ms,\n    )\n    if os.environ.get("ATE_USE_BOOTSTRAP_KEYS") == "1":\n        new_epoch = executor_call(apply_control_record, conn, **apply_kwargs)\n    else:\n        new_epoch = apply_control_record(conn, **apply_kwargs)'''
h = replace_once(h, old_sign, new_sign, "revocation authority/executor UID")
h_path.write_text(h)

print("FR-11 runtime UID enforcement patch applied successfully")
print("Updated: tests/host_runtime.py, tests/case_functions.py, tests/_helpers.py")
print("Formal scored run remains unauthorized.")

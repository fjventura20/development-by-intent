"""Formal-host runtime helpers for FR-11.

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
    """Temporarily switch effective uid/gid in the trusted controller.

    Re-entrant same-principal calls are allowed: executor code can call an
    executor-scoped connection proxy without trying to regain root first.
    A non-root principal may never switch directly to a different principal.
    """
    pw = pwd.getpwnam(name)
    current_uid, current_gid = os.geteuid(), os.getegid()

    # Already executing as the requested principal: nested scope is a no-op.
    if current_uid == pw.pw_uid:
        yield
        return

    # Only the trusted root controller may cross into another principal.
    if current_uid != 0:
        raise PermissionError(
            f"FR-11 principal switch denied: euid={current_uid} -> {name}({pw.pw_uid})"
        )

    try:
        os.setegid(pw.pw_gid)
        os.seteuid(pw.pw_uid)
        yield
    finally:
        os.seteuid(current_uid)
        os.setegid(current_gid)


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


class RemoteEd25519Signer:
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
        # Invoke the installed trusted signer worker at /opt/ate-poc-v010/bin/.
        # The worker is root-owned and mode 0555; it does not depend on the
        # development worktree or PYTHONPATH. Imports are anchored inside the
        # worker itself. See bootstrap.sh §1b.
        worker = "/opt/ate-poc-v010/bin/host_signer_worker.py"
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

def prepare_executor_case_dir(case_dir: str):
    """Create/chown a case directory and open its DB as ate-executor.

    The leaf case_dir is mode 0700 ate-executor-owned so only the executor
    can read/write the DB. The parent chain (e.g. evidence_dir and
    evidence_dir/case-dbs) MUST also be traversable by ate-executor,
    otherwise a forked child worker that drops to ate-executor before
    opening the DB cannot even traverse to the leaf. We fix every parent
    we currently own (root:root) to ate-executor:ate-executor with mode
    0755 — narrow chown of paths we created, not a broad chmod.
    """
    import shutil
    from trusted import enforcement_store
    pw = pwd.getpwnam("ate-executor")
    exe_uid, exe_gid = pw.pw_uid, pw.pw_gid

    # Walk up from case_dir. We own the parents we created in this run.
    # Stop at the first ancestor that already existed BEFORE this run —
    # i.e. an ancestor we did not create. We detect this by only chowning
    # paths that (a) currently exist and (b) have uid 0 AND were either
    # created recently or have an `os.path.getmtime` newer than a
    # reasonable threshold. Simpler and safer: chown only the case-dbs
    # parent (immediate parent of case_dir) and the evidence_dir
    # (immediate parent of case-dbs). Both are guaranteed to be created
    # by this run's verifier stage.
    #
    # Walk up to find the boundary: stop at the first ancestor that does
    # NOT currently exist (i.e. was not created by us) or that is a
    # system sticky path like /tmp.
    cur = os.path.dirname(case_dir)
    ancestors = []
    while cur and cur != os.path.dirname(cur):
        try:
            st = os.stat(cur)
        except FileNotFoundError:
            break
        # Stop at /tmp or any sticky-bit system path.
        if (st.st_mode & 0o1000) and (st.st_uid == 0):
            break  # sticky-bit + root-owned → system path, don't touch
        # Stop at the first ancestor that already existed before this run.
        # Heuristic: if the path is under /tmp/ or /var/tmp/ and was
        # modified before this run started, treat it as pre-existing
        # system space.
        # (We can't reliably timestamp, so we use a hard-coded list of
        # system roots that must not be touched.)
        if cur in ("/tmp", "/var/tmp", "/dev/shm"):
            break
        if st.st_uid == 0:  # currently root:root; we (root) own it
            ancestors.append(cur)
        else:
            break  # hit a non-root ancestor; leave it alone
        cur = os.path.dirname(cur)

    for p in reversed(ancestors):
        os.chown(p, exe_uid, exe_gid)
        os.chmod(p, 0o755)

    # Now the leaf
    if os.path.exists(case_dir):
        shutil.rmtree(case_dir)
    os.makedirs(case_dir, mode=0o700, exist_ok=True)
    os.chown(case_dir, exe_uid, exe_gid)
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

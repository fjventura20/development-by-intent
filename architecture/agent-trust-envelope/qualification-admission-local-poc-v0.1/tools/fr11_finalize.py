#!/usr/bin/env python3
"""Apply the remaining FR-11 host-key custody changes locally.

This script is intentionally deterministic and fail-fast. It expects the
WIP tree produced by commit 3d8f29c8... and patches only:
  - bootstrap.sh
  - qa_poc/formal_runner.py
  - run_formal.py
  - tests/host_runtime.py (new)

It does NOT run bootstrap, tests, preflight, or the formal scored run.
"""
from __future__ import annotations

from pathlib import Path
import textwrap

ROOT = Path(__file__).resolve().parents[1]


def replace_between(text: str, start: str, end: str, replacement: str) -> str:
    i = text.find(start)
    j = text.find(end)
    if i < 0 or j < 0 or j <= i:
        raise SystemExit(f"patch markers not found: {start!r} .. {end!r}")
    return text[:i] + replacement.rstrip() + "\n\n" + text[j:]


def replace_once(text: str, old: str, new: str, label: str) -> str:
    if text.count(old) != 1:
        raise SystemExit(f"expected exactly one occurrence for {label}; found {text.count(old)}")
    return text.replace(old, new, 1)


# ---------------------------------------------------------------------------
# 1) bootstrap.sh: eight private keys, public counterparts, root-readable
#    public manifest built ONLY from public PEMs.
# ---------------------------------------------------------------------------
bootstrap_path = ROOT / "bootstrap.sh"
bootstrap = bootstrap_path.read_text()
start = "# --- 4. Generate the EIGHT distinct keypairs (if absent) ---"
end = "# --- 6. Initialize enforcement.db schema (ate-executor) ---"
section = r'''# --- 4. Generate the EIGHT distinct keypairs + public counterparts ---
AUTH_DIR="$ATE_VAR_LIB/authority"
EXEC_DIR="$ATE_VAR_LIB/executor"
PUB_ROOT="/etc/ate/poc-public"
install -d -m 0755 -o root -g root "$PUB_ROOT"

# Obsolete single-key bootstrap artifacts are not part of the frozen FR-11
# topology. Remove them before formal evidence is generated.
rm -f "$AUTH_DIR/authority_signing.key" /etc/ate/authority_pubkey.pem

generate_keypair() {
  local keyfile="$1"
  local owner="$2"
  local pub_tmp="$3"
  sudo -n -u "$owner" python3 - "$keyfile" "$pub_tmp" <<'PYEOF'
import os, sys
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
keyfile, pubfile = sys.argv[1], sys.argv[2]
if os.path.exists(keyfile) and os.path.getsize(keyfile) > 0:
    with open(keyfile, 'rb') as f:
        priv = serialization.load_pem_private_key(f.read(), password=None)
else:
    priv = Ed25519PrivateKey.generate()
    with open(keyfile, 'wb') as f:
        f.write(priv.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption(),
        ))
    os.chmod(keyfile, 0o600)
with open(pubfile, 'wb') as f:
    f.write(priv.public_key().public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    ))
os.chmod(pubfile, 0o644)
PYEOF
}

# authority-owned private keys
generate_keypair "$AUTH_DIR/policy_signing.key"            ate-authority "$AUTH_DIR/policy_signing.pub.pem"
generate_keypair "$AUTH_DIR/identity_signing.key"          ate-authority "$AUTH_DIR/identity_signing.pub.pem"
generate_keypair "$AUTH_DIR/r11_qualification_signing.key" ate-authority "$AUTH_DIR/r11_qualification_signing.pub.pem"
generate_keypair "$AUTH_DIR/r12_admission_signing.key"     ate-authority "$AUTH_DIR/r12_admission_signing.pub.pem"
generate_keypair "$AUTH_DIR/authorization_signing.key"     ate-authority "$AUTH_DIR/authorization_signing.pub.pem"
generate_keypair "$AUTH_DIR/trust_decision_signing.key"    ate-authority "$AUTH_DIR/trust_decision_signing.pub.pem"
# executor-owned private keys
generate_keypair "$EXEC_DIR/executor_signing.key"          ate-executor "$EXEC_DIR/executor_signing.pub.pem"
generate_keypair "$EXEC_DIR/audit_signing.key"             ate-executor "$EXEC_DIR/audit_signing.pub.pem"

# Root copies PUBLIC material only into /etc/ate/poc-public.
install -m 0644 -o root -g root "$AUTH_DIR/policy_signing.pub.pem"            "$PUB_ROOT/AUTH_POLICY.pem"
install -m 0644 -o root -g root "$AUTH_DIR/identity_signing.pub.pem"          "$PUB_ROOT/AUTH_IDENTITY.pem"
install -m 0644 -o root -g root "$AUTH_DIR/r11_qualification_signing.pub.pem" "$PUB_ROOT/AUTH_R11_QUALIFICATION.pem"
install -m 0644 -o root -g root "$AUTH_DIR/r12_admission_signing.pub.pem"     "$PUB_ROOT/AUTH_R12_ADMISSION.pem"
install -m 0644 -o root -g root "$AUTH_DIR/authorization_signing.pub.pem"     "$PUB_ROOT/AUTH_AUTHORIZATION.pem"
install -m 0644 -o root -g root "$AUTH_DIR/trust_decision_signing.pub.pem"    "$PUB_ROOT/AUTH_TRUST_DECISION.pem"
install -m 0644 -o root -g root "$EXEC_DIR/executor_signing.pub.pem"          "$PUB_ROOT/AUTH_EXECUTOR.pem"
install -m 0644 -o root -g root "$EXEC_DIR/audit_signing.pub.pem"             "$PUB_ROOT/AUTH_AUDIT.pem"

# Build manifest from public PEMs only. No principal crosses a private-key
# custody boundary to construct this file.
PUB_MANIFEST="$PUB_ROOT/public_key_manifest.json"
python3 - "$PUB_ROOT" "$PUB_MANIFEST" <<'PYEOF'
import hashlib, json, os, sys
from cryptography.hazmat.primitives import serialization
pub_root, manifest_path = sys.argv[1], sys.argv[2]
entries = [
    ("AUTH_POLICY", "ate-authority", ["ate.qualification.profile.v1"]),
    ("AUTH_IDENTITY", "ate-authority", ["ate.qualification.evidence_manifest.v1"]),
    ("AUTH_R11_QUALIFICATION", "ate-authority", [
        "ate.qualification.credential.v1", "ate.qualification.decision.v1",
        "ate.control_record.v1:QUALIFICATION_REVOCATION",
        "ate.control_record.v1:QUALIFICATION_SUSPENSION",
    ]),
    ("AUTH_R12_ADMISSION", "ate-authority", [
        "ate.admission.credential.v1", "ate.admission.decision.v1",
        "ate.control_record.v1:ADMISSION_REVOCATION",
        "ate.control_record.v1:ADMISSION_SUSPENSION",
    ]),
    ("AUTH_AUTHORIZATION", "ate-authority", ["ate.authorization.capability_token.v1"]),
    ("AUTH_TRUST_DECISION", "ate-authority", ["ate.authorization.trust_decision.v1"]),
    ("AUTH_EXECUTOR", "ate-executor", ["ate.control_record.v1"]),
    ("AUTH_AUDIT", "ate-executor", ["ate.audit.v1"]),
]
out = {"version": 1, "keys": []}
for label, owner, artifact_types in entries:
    path = os.path.join(pub_root, label + ".pem")
    pem = open(path, "rb").read()
    pub = serialization.load_pem_public_key(pem)
    der = pub.public_bytes(
        encoding=serialization.Encoding.DER,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )
    out["keys"].append({
        "label": label,
        "key_id": hashlib.sha256(der).hexdigest(),
        "custody_owner": owner,
        "public_key_pem_sha256": hashlib.sha256(pem).hexdigest(),
        "authorized_artifact_types": artifact_types,
        "public_key_path": path,
    })
ids = [x["key_id"] for x in out["keys"]]
if len(ids) != 8 or len(set(ids)) != 8:
    raise SystemExit("FR-11 FAIL: expected eight distinct key IDs")
with open(manifest_path, "w") as f:
    json.dump(out, f, indent=2, sort_keys=True)
os.chmod(manifest_path, 0o644)
PYEOF

# Private-key permissions are authoritative custody checks.
chown ate-authority:ate-authority "$AUTH_DIR"/*.key
chmod 0600 "$AUTH_DIR"/*.key
chown ate-executor:ate-executor "$EXEC_DIR"/*.key
chmod 0600 "$EXEC_DIR"/*.key
'''
bootstrap = replace_between(bootstrap, start, end, section)
# Update final summary reference if needed.
bootstrap = bootstrap.replace('echo "PUBLIC_KEY_MANIFEST=$PUB_MANIFEST"', 'echo "PUBLIC_KEY_MANIFEST=/etc/ate/poc-public/public_key_manifest.json"')
bootstrap_path.write_text(bootstrap)


# ---------------------------------------------------------------------------
# 2) Dedicated formal-host harness. Fresh registries/clock per case, SAME
#    bootstrap signer identities across all cases.
# ---------------------------------------------------------------------------
host_runtime = r'''"""Formal-host fixture construction for FR-11.

Development tests continue to use ephemeral fixture keys. The authorized
formal run uses this module so all scored cases share the same eight
bootstrap-created cryptographic identities while still receiving fresh policy
registries and clocks per case.
"""
from __future__ import annotations

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


def _load(path: Path):
    priv = load_ed25519_private_pem(str(path))
    return priv, priv.public_key()


def load_bootstrap_keybag() -> KeyBag:
    policy_priv, policy_pub = _load(AUTH / "policy_signing.key")
    identity_priv, identity_pub = _load(AUTH / "identity_signing.key")
    r11_priv, r11_pub = _load(AUTH / "r11_qualification_signing.key")
    r12_priv, r12_pub = _load(AUTH / "r12_admission_signing.key")
    auth_priv, auth_pub = _load(AUTH / "authorization_signing.key")
    trust_priv, trust_pub = _load(AUTH / "trust_decision_signing.key")
    executor_priv, executor_pub = _load(EXEC / "executor_signing.key")
    audit_priv, audit_pub = _load(EXEC / "audit_signing.key")
    # AUTH_IDENTITY is the single frozen identity authority. The legacy
    # KeyBag has two identity slots; formal-host mode aliases both to the
    # same bootstrap AUTH_IDENTITY key rather than creating a ninth key.
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


def build_host_harness() -> FixtureHarness:
    keys = load_bootstrap_keybag()
    profile_reg = ProfileRegistry()
    policy_reg = PolicyRegistry()
    qual = QualificationAuthority(
        registry=profile_reg,
        r11_priv=keys.r11_priv,
        r11_pub=keys.r11_pub,
        r11_key_id="r11-q",
        identity_priv=keys.identity_priv,
    )
    adm = AdmissionAuthority(
        registry=policy_reg,
        r12_priv=keys.r12_priv,
        r12_pub=keys.r12_pub,
        r12_key_id="r12-a",
    )
    authz = AuthorizationAuthority(
        auth_priv=keys.auth_priv,
        auth_pub=keys.auth_pub,
        auth_key_id="auth",
        trust_priv=keys.trust_priv,
        trust_pub=keys.trust_pub,
        trust_key_id="trust",
    )
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
# 3) formal_runner.py: authorized formal mode uses host keys; ordinary dev
#    runs continue using ephemeral FixtureHarness.build().
# ---------------------------------------------------------------------------
fr_path = ROOT / "qa_poc" / "formal_runner.py"
fr = fr_path.read_text()
old = '''        from tests._helpers import FixtureHarness\n        fresh_harness = FixtureHarness.build()'''
new = '''        if os.environ.get("ATE_USE_BOOTSTRAP_KEYS") == "1":\n            from tests.host_runtime import build_host_harness\n            fresh_harness = build_host_harness()\n        else:\n            from tests._helpers import FixtureHarness\n            fresh_harness = FixtureHarness.build()'''
fr = replace_once(fr, old, new, "formal_runner host harness selection")
fr_path.write_text(fr)


# ---------------------------------------------------------------------------
# 4) run_formal.py: PF6/PF7 enforce all eight custody keys + unique IDs;
#    public-key manifest comes from bootstrap public material; scored run
#    opts into bootstrap keys.
# ---------------------------------------------------------------------------
rf_path = ROOT / "run_formal.py"
rf = rf_path.read_text()
old_pf = '''        # PF6\n        key = "/var/lib/ate/poc/authority/authority_signing.key"\n        if _exists_as_root(key):\n            r = _sudo_run_as("ate-requester", ["test", "-r", key])\n            results.append(PreflightResult("PF6", "authority_keys_not_requester_readable",\n                "PASS" if r.returncode != 0 else "FAIL",\n                f"{key} returncode={r.returncode}"))\n        else:\n            results.append(PreflightResult("PF6", "authority_keys_not_requester_readable", "FAIL", f"{key} not bootstrapped"))\n        # PF7\n        exec_keys = [\n            "/var/lib/ate/poc/executor/executor_signing.key",\n            "/var/lib/ate/poc/executor/audit_signing.key",\n        ]\n        ok = all(_exists_as_root(k) and all(_sudo_run_as(p, ["test", "-r", k]).returncode != 0 for p in ("ate-requester", "ate-authority")) for k in exec_keys)\n        results.append(PreflightResult("PF7", "executor_audit_keys_not_requester_authority_readable",\n            "PASS" if ok else "FAIL", "all checks passed" if ok else "at least one check failed"))'''
new_pf = '''        # PF6 — six distinct authority private keys are owned/readable only\n        # by ate-authority (and root), never ate-requester.\n        authority_keys = [\n            "/var/lib/ate/poc/authority/policy_signing.key",\n            "/var/lib/ate/poc/authority/identity_signing.key",\n            "/var/lib/ate/poc/authority/r11_qualification_signing.key",\n            "/var/lib/ate/poc/authority/r12_admission_signing.key",\n            "/var/lib/ate/poc/authority/authorization_signing.key",\n            "/var/lib/ate/poc/authority/trust_decision_signing.key",\n        ]\n        ok6 = True\n        pf6_notes = []\n        for k in authority_keys:\n            exists = _exists_as_root(k)\n            req_denied = exists and _sudo_run_as("ate-requester", ["test", "-r", k]).returncode != 0\n            auth_reads = exists and _sudo_run_as("ate-authority", ["test", "-r", k]).returncode == 0\n            st = subprocess.run(["sudo", "-n", "stat", "-c", "%U:%G:%a", k], capture_output=True, text=True) if exists else None\n            stat_ok = bool(st and st.returncode == 0 and st.stdout.strip() == "ate-authority:ate-authority:600")\n            ok6 = ok6 and exists and req_denied and auth_reads and stat_ok\n            pf6_notes.append(f"{os.path.basename(k)}={'ok' if (exists and req_denied and auth_reads and stat_ok) else 'bad'}")\n        results.append(PreflightResult(\n            "PF6", "authority_keys_not_requester_readable",\n            "PASS" if ok6 else "FAIL", "; ".join(pf6_notes)))\n\n        # PF7 — executor/audit private keys readable only by ate-executor;\n        # bootstrap public manifest must contain eight distinct key IDs.\n        exec_keys = [\n            "/var/lib/ate/poc/executor/executor_signing.key",\n            "/var/lib/ate/poc/executor/audit_signing.key",\n        ]\n        ok7 = True\n        pf7_notes = []\n        for k in exec_keys:\n            exists = _exists_as_root(k)\n            requester_denied = exists and _sudo_run_as("ate-requester", ["test", "-r", k]).returncode != 0\n            authority_denied = exists and _sudo_run_as("ate-authority", ["test", "-r", k]).returncode != 0\n            executor_reads = exists and _sudo_run_as("ate-executor", ["test", "-r", k]).returncode == 0\n            st = subprocess.run(["sudo", "-n", "stat", "-c", "%U:%G:%a", k], capture_output=True, text=True) if exists else None\n            stat_ok = bool(st and st.returncode == 0 and st.stdout.strip() == "ate-executor:ate-executor:600")\n            ok7 = ok7 and exists and requester_denied and authority_denied and executor_reads and stat_ok\n            pf7_notes.append(f"{os.path.basename(k)}={'ok' if (exists and requester_denied and authority_denied and executor_reads and stat_ok) else 'bad'}")\n        manifest_path = "/etc/ate/poc-public/public_key_manifest.json"\n        try:\n            manifest = json.load(open(manifest_path))\n            ids = [x["key_id"] for x in manifest.get("keys", [])]\n            labels = {x["label"] for x in manifest.get("keys", [])}\n            expected_labels = {\n                "AUTH_POLICY", "AUTH_IDENTITY", "AUTH_R11_QUALIFICATION",\n                "AUTH_R12_ADMISSION", "AUTH_AUTHORIZATION",\n                "AUTH_TRUST_DECISION", "AUTH_EXECUTOR", "AUTH_AUDIT",\n            }\n            manifest_ok = len(ids) == 8 and len(set(ids)) == 8 and labels == expected_labels\n        except Exception as e:\n            manifest_ok = False\n            pf7_notes.append(f"manifest_error={e}")\n        ok7 = ok7 and manifest_ok\n        pf7_notes.append(f"eight_distinct_manifest_keys={manifest_ok}")\n        results.append(PreflightResult(\n            "PF7", "executor_audit_keys_not_requester_authority_readable",\n            "PASS" if ok7 else "FAIL", "; ".join(pf7_notes)))'''
rf = replace_once(rf, old_pf, new_pf, "PF6/PF7 custody checks")

start_manifest = "def build_public_key_manifest(repo_dir: str):"
end_manifest = "# --- Canonicalization profile"
new_manifest = '''def build_public_key_manifest(repo_dir: str):\n    """Load the exact bootstrap public-key manifest used by the formal run.\n\n    This must describe the same signer identities loaded by\n    tests.host_runtime; generating a fresh fixture KeyBag here would make\n    §29 evidence non-reproducible.\n    """\n    path = "/etc/ate/poc-public/public_key_manifest.json"\n    with open(path, "r") as f:\n        data = json.load(f)\n    keys = data.get("keys", [])\n    ids = [x.get("key_id") for x in keys]\n    if len(keys) != 8 or len(set(ids)) != 8:\n        raise RuntimeError("FR-11 public-key manifest must contain eight distinct key IDs")\n    return keys\n\n\n'''
rf = replace_between(rf, start_manifest, end_manifest, new_manifest + end_manifest)

old_main = '''    from qa_poc.formal_runner import run_all_cases, classify, REQUIRED_CASES\n    from tests._helpers import FixtureHarness\n\n    h = FixtureHarness.build()\n    cases = run_all_cases(harness=h, evidence_dir=evidence_dir)'''
new_main = '''    from qa_poc.formal_runner import run_all_cases, classify, REQUIRED_CASES\n\n    # FR-11: the scored run must use the bootstrap-created signer identities,\n    # never fresh per-case keys. Root is the trusted local test controller for\n    # this synthetic PoC and is required only so it can construct the in-memory\n    # authority fixtures from custody-protected keys; requester/authority/\n    # executor OS permission checks remain enforced by preflight.\n    if os.geteuid() != 0:\n        run_record["classification"] = "INVALID_RUN"\n        run_record["stopped_reason"] = "formal_host_key_load_requires_trusted_root_controller"\n        with open(os.path.join(evidence_dir, "run_record.json"), "w") as f:\n            json.dump(run_record, f, indent=2)\n        print("INVALID_RUN — authorized formal run must be launched by the trusted root controller", file=sys.stderr)\n        return 1\n    os.environ["ATE_USE_BOOTSTRAP_KEYS"] = "1"\n    cases = run_all_cases(harness=None, evidence_dir=evidence_dir)'''
rf = replace_once(rf, old_main, new_main, "formal main host-key selection")
rf_path.write_text(rf)

print("FR-11 local patch applied successfully")
print("Changed: bootstrap.sh, qa_poc/formal_runner.py, run_formal.py")
print("Created: tests/host_runtime.py")
print("Formal scored run remains unauthorized.")

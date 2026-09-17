#!/usr/bin/env bash
# ATE Qualification & Admission Local PoC v0.1 — bootstrap (FR-11).
#
# Installs the OS boundary, the executor-owned enforcement store, and
# EIGHT distinct keypairs under proper ownership / mode bits:
#
#   AUTH_POLICY                : publishes QualificationRequirementsProfile
#   AUTH_IDENTITY              : publishes IdentityProfile
#   AUTH_R11_QUALIFICATION     : signs QualificationEvidenceManifest /
#                                QualificationDecision / QualificationCredential
#                                AND signs QUALIFICATION_REVOCATION ControlRecords
#   AUTH_R12_ADMISSION         : signs AdmissionEvidenceManifest /
#                                AdmissionDecision / AdmissionCredential
#                                AND signs ADMISSION_REVOCATION ControlRecords
#   AUTH_AUTHORIZATION         : signs CapabilityToken
#   AUTH_TRUST_DECISION        : signs TrustDecision
#   AUTH_EXECUTOR              : signs ControlRecord
#   AUTH_AUDIT                 : signs audit-trail hash chain (per §26)
#
# Layout (frozen §4-§7):
#
#   /opt/ate-poc-v010/                        root:root 0755
#     qa_poc/                                  root:root 0755 (files 0555)
#     trusted/                                root:root 0755 (files 0555)
#   /var/lib/ate/poc/                         root:root 0755
#     authority/                              ate-authority:ate-authority 0700
#       policy_signing.key                    ate-authority 0600
#       identity_signing.key                  ate-authority 0600
#       r11_qualification_signing.key        ate-authority 0600
#       r12_admission_signing.key            ate-authority 0600
#       authorization_signing.key            ate-authority 0600
#       trust_decision_signing.key           ate-authority 0600
#     executor/                               ate-executor:ate-executor 0700
#       executor_signing.key                  ate-executor 0600
#       audit_signing.key                     ate-executor 0600
#       enforcement.db                        ate-executor 0600
#
# This PoC does not use long-lived IPC services; the EAP and
# apply_control_record are invoked in-process by the formal runner as
# ate-executor. The enforcement store IS opened by ate-executor, which
# means its UID owns the file and requester/authority UIDs must NOT
# have read or write access to enforcement.db.

set -euo pipefail

export ATE_OPT_ROOT="${ATE_OPT_ROOT:-/opt/ate-poc-v010}"
export ATE_VAR_LIB="${ATE_VAR_LIB:-/var/lib/ate/poc}"

# Preserve env through sudo invocations (FR-11)
export SUDO_ASKPASS="/bin/false"

if [ "$(id -u)" -ne 0 ] && ! sudo -n true 2>/dev/null; then
  echo "must run as root or with passwordless sudo" >&2
  exit 3
fi

# Caller passes TWO source dirs: qa_poc then trusted
if [ "$#" -lt 2 ]; then
  echo "usage: bootstrap.sh <qa_poc-source-dir> <trusted-source-dir>" >&2
  exit 4
fi
QA_SRC="$1"
TRUSTED_SRC="$2"

if [ ! -d "$QA_SRC" ] || [ ! -d "$TRUSTED_SRC" ]; then
  echo "qa_poc or trusted source dir not found" >&2
  exit 5
fi

# --- 1. Install trusted code as packages (root-owned, world-readable+executable)
for sub in qa_poc trusted; do
  src="$QA_SRC"
  [ "$sub" = "trusted" ] && src="$TRUSTED_SRC"
  install -d -m 0755 -o root -g root "$ATE_OPT_ROOT/$sub"
  # Copy all .py files (preserving __init__.py)
  for f in "$src"/*.py; do
    [ -e "$f" ] || continue
    install -m 0555 -o root -g root "$f" "$ATE_OPT_ROOT/$sub/"
  done
done

# --- 2. Create OS identities (idempotent) ---
for name in ate-requester ate-authority ate-executor; do
  if ! getent group "$name" > /dev/null 2>&1; then
    groupadd --system "$name"
  fi
  if ! id "$name" > /dev/null 2>&1; then
    useradd --system --no-create-home --shell /usr/sbin/nologin \
            --gid "$name" --groups "$name" "$name"
  fi
done

# --- 3. Create key directories ---
install -d -m 0700 -o ate-authority -g ate-authority "$ATE_VAR_LIB/authority"
install -d -m 0700 -o ate-executor  -g ate-executor  "$ATE_VAR_LIB/executor"

# --- 4. Generate the EIGHT distinct keypairs + public counterparts ---
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

# --- 6. Initialize enforcement.db schema (ate-executor) ---
ENF_DB="$ATE_VAR_LIB/executor/enforcement.db"
if [ -s "$ENF_DB" ]; then
  echo "[bootstrap] keep existing $ENF_DB"
else
  sudo -n -u ate-executor python3 - <<PY
import sys
sys.path.insert(0, "$ATE_OPT_ROOT")
from trusted import enforcement_store
import os
conn = enforcement_store.open_store("$ENF_DB")
conn.close()
PY
fi
chmod 0600 "$ENF_DB"

# --- 7. Summary ---
authority_uid=$(id -u ate-authority)
executor_uid=$(id -u ate-executor)
echo "BOOTSTRAP READY"
echo "ENV=$ATE_VAR_LIB/bootstrap.env"
echo "authority_uid=$authority_uid executor_uid=$executor_uid"
echo "PUBLIC_KEY_MANIFEST=/etc/ate/poc-public/public_key_manifest.json"

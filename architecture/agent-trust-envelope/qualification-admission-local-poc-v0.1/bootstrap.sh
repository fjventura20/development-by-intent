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

# --- 4. Generate the EIGHT distinct keypairs (if absent) ---
generate_key() {
  local keyfile="$1"
  local owner="$2"
  if [ -s "$keyfile" ]; then
    echo "[bootstrap] keep existing $keyfile"
  else
    sudo -n -u "$owner" python3 -c "
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives import serialization
priv = Ed25519PrivateKey.generate()
with open('$keyfile', 'wb') as f:
    f.write(priv.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    ))
import os; os.chmod('$keyfile', 0o600)
"
  fi
}

generate_key "$ATE_VAR_LIB/authority/policy_signing.key"        ate-authority
generate_key "$ATE_VAR_LIB/authority/identity_signing.key"      ate-authority
generate_key "$ATE_VAR_LIB/authority/r11_qualification_signing.key" ate-authority
generate_key "$ATE_VAR_LIB/authority/r12_admission_signing.key"     ate-authority
generate_key "$ATE_VAR_LIB/authority/authorization_signing.key"     ate-authority
generate_key "$ATE_VAR_LIB/authority/trust_decision_signing.key"    ate-authority
generate_key "$ATE_VAR_LIB/executor/executor_signing.key"       ate-executor
generate_key "$ATE_VAR_LIB/executor/audit_signing.key"          ate-executor

# --- 5. Generate public-key manifest (used by run_formal.py) ---
export PUB_MANIFEST="$ATE_VAR_LIB/authority/public_key_manifest.json"
extract_pub_pem() {
  local keyfile="$1"
  python3 -c "
from cryptography.hazmat.primitives import serialization
with open('$keyfile', 'rb') as f:
    priv = serialization.load_pem_private_key(f.read(), password=None)
pub = priv.public_key()
print(pub.public_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PublicFormat.SubjectPublicKeyInfo,
).decode('ascii'))
"
}

# Build manifest as ate-authority (writes only its own files)
sudo -n -u ate-authority env ATE_VAR_LIB="$ATE_VAR_LIB" ATE_OPT_ROOT="$ATE_OPT_ROOT" PUB_MANIFEST="$PUB_MANIFEST" bash -c '
set -euo pipefail
mkdir -p "$ATE_VAR_LIB/authority"
KEY_DIR="$ATE_VAR_LIB/authority"
EX_KEY_DIR="$ATE_VAR_LIB/executor"
EMIT=$(mktemp)
python3 - <<PY
import hashlib, json, os, sys
from cryptography.hazmat.primitives import serialization
KEYS = [
  ("AUTH_POLICY",                "$KEY_DIR/policy_signing.key"),
  ("AUTH_IDENTITY",              "$KEY_DIR/identity_signing.key"),
  ("AUTH_R11_QUALIFICATION",     "$KEY_DIR/r11_qualification_signing.key"),
  ("AUTH_R12_ADMISSION",         "$KEY_DIR/r12_admission_signing.key"),
  ("AUTH_AUTHORIZATION",         "$KEY_DIR/authorization_signing.key"),
  ("AUTH_TRUST_DECISION",        "$KEY_DIR/trust_decision_signing.key"),
  ("AUTH_EXECUTOR",              "$EX_KEY_DIR/executor_signing.key"),
  ("AUTH_AUDIT",                 "$EX_KEY_DIR/audit_signing.key"),
]
ARTIFACTS = {
  "AUTH_POLICY": ["ate.qualification.profile.v1"],
  "AUTH_IDENTITY": ["ate.qualification.evidence_manifest.v1"],
  "AUTH_R11_QUALIFICATION": [
    "ate.qualification.credential.v1",
    "ate.qualification.decision.v1",
    "ate.control_record.v1:QUALIFICATION_REVOCATION",
    "ate.control_record.v1:QUALIFICATION_SUSPENSION",
  ],
  "AUTH_R12_ADMISSION": [
    "ate.admission.credential.v1",
    "ate.admission.decision.v1",
    "ate.control_record.v1:ADMISSION_REVOCATION",
    "ate.control_record.v1:ADMISSION_SUSPENSION",
  ],
  "AUTH_AUTHORIZATION": ["ate.authorization.capability_token.v1"],
  "AUTH_TRUST_DECISION": ["ate.authorization.trust_decision.v1"],
  "AUTH_EXECUTOR": ["ate.control_record.v1"],
  "AUTH_AUDIT": ["ate.audit.v1"],
}
out = {"version": 1, "keys": []}
for label, kp in KEYS:
    with open(kp, "rb") as f:
        priv = serialization.load_pem_private_key(f.read(), password=None)
    pub_pem = priv.public_key().public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    ).decode("ascii")
    digest = hashlib.sha256(pub_pem.encode("ascii")).hexdigest()
    out["keys"].append({
        "label": label,
        "public_key_pem_sha256": digest,
        "authorized_artifact_types": ARTIFACTS[label],
    })
with open("'$PUB_MANIFEST'", "w") as f:
    json.dump(out, f, indent=2)
PY
chmod 0644 "'$PUB_MANIFEST'"
'

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
echo "PUBLIC_KEY_MANIFEST=$PUB_MANIFEST"

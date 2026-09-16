#!/usr/bin/env bash
# ATE Qualification & Admission Local PoC v0.1 — bootstrap.
#
# Installs the OS boundary: identities ate-requester / ate-authority /
# ate-executor (no login, no sudo), and the executor-owned enforcement
# store + key directories with the correct ownership / mode bits.
#
# Layout (mirrors the v0.2 P1 enforcement harness contract — same
# identities, same mode bits — so this PoC can reuse prior AegisNexus
# OS-boundary work safely):
#
#   /opt/ate-poc-v010/bin/          (root:root 0755; files 0555)
#   /etc/ate/                        (root:root 0755)
#     authority_pubkey.pem           (root:root 0644)
#   /var/lib/ate/poc/                (root:root 0755)
#     authority/                     (ate-authority:ate-authority 0700)
#       authority_signing.key        (ate-authority:ate-authority 0600)
#     executor/                      (ate-executor:ate-executor 0700)
#       enforcement.db               (ate-executor:ate-executor 0600)
#       executor_signing.key         (ate-executor:ate-executor 0600)
#       audit_signing.key            (ate-executor:ate-executor 0600)
#
# This PoC does not use long-lived IPC services; the EAP and
# apply_control_record are invoked in-process by the formal runner as
# ate-executor. The enforcement store IS opened by ate-executor, which
# means its UID owns the file and requester/authority UIDs must NOT
# have read or write access to enforcement.db.

set -euo pipefail

ATE_OPT_BIN="${ATE_OPT_BIN:-/opt/ate-poc-v010/bin}"
ATE_ETC="${ATE_ETC:-/etc/ate}"
ATE_VAR_LIB="${ATE_VAR_LIB:-/var/lib/ate/poc}"

if [ "$(id -u)" -ne 0 ] && ! sudo -n true 2>/dev/null; then
  echo "must run as root or with passwordless sudo" >&2
  exit 3
fi

# --- 1. Install trusted code (root-owned, world-readable+executable) ------
# Caller passes one or more source dirs containing *.py modules.
for src in "$@"; do
  if [ ! -d "$src" ]; then
    echo "source dir not found: $src" >&2
    exit 4
  fi
  sudo -n install -d -o root -g root -m 0755 "$ATE_OPT_BIN"
  for f in "$src"/*.py; do
    [ -e "$f" ] || continue
    base="$(basename "$f")"
    sudo -n install -o root -g root -m 0555 "$f" "$ATE_OPT_BIN/$base"
  done
done

# --- 2. Ensure OS identities (idempotent) ----------------------------------
for grp in ate-requester ate-authority ate-executor; do
  sudo -n groupadd -f "$grp" >/dev/null
done
id ate-requester >/dev/null 2>&1 || sudo -n useradd -r -s /usr/sbin/nologin -G ate-requester ate-requester
id ate-authority >/dev/null 2>&1 || sudo -n useradd -r -s /usr/sbin/nologin -G ate-authority ate-authority
id ate-executor >/dev/null 2>&1  || sudo -n useradd -r -s /usr/sbin/nologin -G ate-executor ate-executor

# --- 3. Mutable state directories -------------------------------------------
sudo -n install -d -o root -g root -m 0755 "$ATE_VAR_LIB"
sudo -n install -d -o ate-authority -g ate-authority -m 0700 "$ATE_VAR_LIB/authority"
sudo -n install -d -o ate-executor -g ate-executor -m 0700 "$ATE_VAR_LIB/executor"

# --- 4. /etc/ate/ for public authority pubkey ------------------------------
sudo -n install -d -o root -g root -m 0755 "$ATE_ETC"
sudo -n touch "$ATE_ETC/authority_pubkey.pem"
sudo -n chown root:root "$ATE_ETC/authority_pubkey.pem"
sudo -n chmod 0644 "$ATE_ETC/authority_pubkey.pem"

# --- 5. Generate authority + executor keypairs (root) and install ----------
EXECUTOR_DB="$ATE_VAR_LIB/executor/enforcement.db"
EXECUTOR_KEY="$ATE_VAR_LIB/executor/executor_signing.key"
EXECUTOR_AUDIT_KEY="$ATE_VAR_LIB/executor/audit_signing.key"
AUTHORITY_KEY="$ATE_VAR_LIB/authority/authority_signing.key"
AUTHORITY_PUBKEY="$ATE_ETC/authority_pubkey.pem"

sudo -n touch "$EXECUTOR_DB"
sudo -n chown ate-executor:ate-executor "$EXECUTOR_DB"
sudo -n chmod 0600 "$EXECUTOR_DB"

# Generate all keypairs via root, install with proper ownership.
sudo -n /usr/bin/python3 - "$EXECUTOR_KEY" "$EXECUTOR_AUDIT_KEY" "$AUTHORITY_KEY" "$AUTHORITY_PUBKEY" <<'PYEOF'
import sys, os
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives import serialization

priv_targets = [
    (sys.argv[1], Ed25519PrivateKey.generate()),
    (sys.argv[2], Ed25519PrivateKey.generate()),
    (sys.argv[3], Ed25519PrivateKey.generate()),
]
pub_path = sys.argv[4]

# Pick the authority priv (last in list) and publish its public key
authority_priv = priv_targets[2][1]

for path, priv in priv_targets:
    pem = priv.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    )
    tmp = path + ".tmp"
    with open(tmp, "wb") as f:
        f.write(pem)
    os.replace(tmp, path)

pub_pem = authority_priv.public_key().public_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PublicFormat.SubjectPublicKeyInfo,
)
tmp = pub_path + ".tmp"
with open(tmp, "wb") as f:
    f.write(pub_pem)
os.replace(tmp, pub_path)
PYEOF

sudo -n chown ate-executor:ate-executor "$EXECUTOR_KEY" "$EXECUTOR_AUDIT_KEY"
sudo -n chmod 0600 "$EXECUTOR_KEY" "$EXECUTOR_AUDIT_KEY"
sudo -n chown ate-authority:ate-authority "$AUTHORITY_KEY"
sudo -n chmod 0600 "$AUTHORITY_KEY"
sudo -n chown root:root "$AUTHORITY_PUBKEY"
sudo -n chmod 0644 "$AUTHORITY_PUBKEY"

# --- 6. Write bootstrap.env -------------------------------------------------
ENV_FILE="$ATE_VAR_LIB/bootstrap.env"
sudo -n bash -c "cat > '$ENV_FILE' <<EOF
ATE_OPT_BIN=$ATE_OPT_BIN
ATE_ETC=$ATE_ETC
ATE_VAR_LIB=$ATE_VAR_LIB
ATE_AUTHORITY_KEY=$AUTHORITY_KEY
ATE_AUTHORITY_PUBKEY=$AUTHORITY_PUBKEY
ATE_EXECUTOR_DB=$EXECUTOR_DB
ATE_EXECUTOR_KEY=$EXECUTOR_KEY
ATE_EXECUTOR_AUDIT_KEY=$EXECUTOR_AUDIT_KEY
EOF"
sudo -n chmod 0644 "$ENV_FILE"

echo "BOOTSTRAP READY"
echo "ENV=$ENV_FILE"
echo "authority_uid=$(id -u ate-authority) executor_uid=$(id -u ate-executor)"

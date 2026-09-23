#!/usr/bin/env bash
# ATE P1 v0.2 — bootstrap (revised per PI directive).
#
# Trusted-code location:   /opt/ate-p1-v020/bin/   (root:root 0755; files 0555)
# Public authority key:    /etc/ate/authority_pubkey.pem  (root:root 0644)
# Mutable authority state: /var/lib/ate/authority/      (ate-authority:ate-authority 0700)
# Mutable executor state:  /var/lib/ate/executor/       (ate-executor:ate-executor 0700)
# Protected resources:     /var/lib/ate/resources/      (ate-executor:ate-executor 0700)
# Runtime namespace:       /run/ate/                   (root:root 0755)
#   per-service socket dirs:
#     /run/ate/authority/   (ate-authority:ate-requester 0750)
#     /run/ate/executor/    (ate-executor:ate-requester 0750)
#
# The requester can traverse /run/ate/ and the per-service socket
# directories (r-x) but cannot write to any of them.

set -euo pipefail

ATE_OPT_BIN="${ATE_OPT_BIN:-/opt/ate-p1-v020/bin}"
ATE_ETC="${ATE_ETC:-/etc/ate}"
ATE_VAR_LIB="${ATE_VAR_LIB:-/var/lib/ate}"
ATE_RUN="${ATE_RUN:-/run/ate}"

if [ "$(id -u)" -ne 0 ] && ! sudo -n true 2>/dev/null; then
  echo "must run as root or with passwordless sudo" >&2
  exit 3
fi

# --- 1. Install trusted code (root-owned, world-readable+executable) ---
sudo -n install -d -o root -g root -m 0755 "$ATE_OPT_BIN"
for src in "$@"; do
  if [ ! -d "$src" ]; then
    echo "source dir not found: $src" >&2
    exit 4
  fi
  for f in "$src"/*.py; do
    [ -e "$f" ] || continue
    base="$(basename "$f")"
    sudo -n install -o root -g root -m 0555 "$f" "$ATE_OPT_BIN/$base"
  done
done

# --- 2. Ensure OS identities (idempotent) ---
for grp in ate-requester ate-authority ate-executor; do
  sudo -n groupadd -f "$grp" >/dev/null
done
id ate-requester >/dev/null 2>&1 || sudo -n useradd -r -s /usr/sbin/nologin -G ate-requester ate-requester
id ate-authority >/dev/null 2>&1 || sudo -n useradd -r -s /usr/sbin/nologin -G ate-authority ate-authority
id ate-executor >/dev/null 2>&1 || sudo -n useradd -r -s /usr/sbin/nologin -G ate-executor ate-executor
# Ensure group memberships
sudo -n usermod -a -G ate-requester ate-requester >/dev/null 2>&1 || true
sudo -n usermod -a -G ate-authority ate-authority >/dev/null 2>&1 || true
sudo -n usermod -a -G ate-executor ate-executor >/dev/null 2>&1 || true

# --- 3. Mutable state directories ---
sudo -n install -d -o root -g root -m 0755 "$ATE_VAR_LIB"
sudo -n install -d -o ate-authority -g ate-authority -m 0700 \
  "$ATE_VAR_LIB/authority"
sudo -n install -d -o ate-executor -g ate-executor -m 0700 \
  "$ATE_VAR_LIB/executor" "$ATE_VAR_LIB/resources"
# ate-authority must also be able to write into authority/ via its own
# uid (it owns authority/, so OK).
# The executor's authority_pubkey lives in /etc/ate (public), so the
# executor dir stays strictly ate-executor-private.

# --- 4. /etc/ate/ for public authority pubkey (root:root 0644) ---
sudo -n install -d -o root -g root -m 0755 "$ATE_ETC"
sudo -n touch "$ATE_ETC/authority_pubkey.pem"
sudo -n chown root:root "$ATE_ETC/authority_pubkey.pem"
sudo -n chmod 0644 "$ATE_ETC/authority_pubkey.pem"

# --- 5. Runtime namespace + per-service socket directories ---
sudo -n install -d -o root -g root -m 0755 "$ATE_RUN" \
  "$ATE_RUN/authority" "$ATE_RUN/executor"
sudo -n chown ate-authority:ate-requester "$ATE_RUN/authority"
sudo -n chmod 0750 "$ATE_RUN/authority"
sudo -n chown ate-executor:ate-requester "$ATE_RUN/executor"
sudo -n chmod 0750 "$ATE_RUN/executor"
sudo -n rm -f "$ATE_RUN/authority/authority.sock" "$ATE_RUN/executor/executor.sock"

# --- 6. Per-resource credentials (HMAC keys, executor-owned) ---
CRED_FILE="$ATE_VAR_LIB/executor/resource_credentials.json"
if [ ! -f "$CRED_FILE" ]; then
  sudo -n -u ate-executor /usr/bin/python3 -c "
import json, secrets
creds = {
  'resource-A': secrets.token_hex(32),
  'resource-B': secrets.token_hex(32),
}
import sys
with open('$CRED_FILE', 'w') as f:
    json.dump(creds, f, sort_keys=True)
"
  sudo -n chown ate-executor:ate-executor "$CRED_FILE"
  sudo -n chmod 0600 "$CRED_FILE"
fi

# --- 7. Pre-create empty audit key (executor generates on first run) ---
AUDIT_KEY="$ATE_VAR_LIB/executor/audit_signing.key"
# Regenerate audit keypair via bootstrap if missing/empty (same pattern
# as authority keypair). The executor would otherwise write its own
# key into its own private dir, but we want bootstrap to manage
# key generation so the executor service is idempotent.
if [ ! -s "$AUDIT_KEY" ]; then
  sudo -n /usr/bin/python3 - "$AUDIT_KEY" <<'PYEOF'
import sys, os
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives import serialization
priv = Ed25519PrivateKey.generate()
pem = priv.private_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PrivateFormat.PKCS8,
    encryption_algorithm=serialization.NoEncryption(),
)
tmp = sys.argv[1] + ".tmp"
with open(tmp, "wb") as f:
    f.write(pem)
os.replace(tmp, sys.argv[1])
PYEOF
fi
sudo -n chown ate-executor:ate-executor "$AUDIT_KEY"
sudo -n chmod 0600 "$AUDIT_KEY"

# --- 7b. Generate authority keypair via bootstrap (root) and install:
#       private → authority-owned file (ate-authority reads it)
#       public  → /etc/ate/ (root:root 0644, world-readable)
# This avoids needing ate-authority to write into /etc/ate.
# Regenerate if either file is missing or empty (handles re-runs after
# partial failures). ---
AUTHORITY_DB="$ATE_VAR_LIB/authority/authority.sqlite"
AUTHORITY_KEY="$ATE_VAR_LIB/authority/authority_signing.key"
AUTHORITY_PUBKEY="$ATE_ETC/authority_pubkey.pem"
sudo -n touch "$AUTHORITY_DB"
sudo -n chown ate-authority:ate-authority "$AUTHORITY_DB"
sudo -n chmod 0600 "$AUTHORITY_DB"

if [ ! -s "$AUTHORITY_KEY" ] || [ ! -s "$AUTHORITY_PUBKEY" ]; then
  sudo -n /usr/bin/python3 - "$AUTHORITY_KEY" "$AUTHORITY_PUBKEY" <<'PYEOF'
import sys, os
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives import serialization
priv = Ed25519PrivateKey.generate()
pem_priv = priv.private_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PrivateFormat.PKCS8,
    encryption_algorithm=serialization.NoEncryption(),
)
pem_pub = priv.public_key().public_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PublicFormat.SubjectPublicKeyInfo,
)
for p, c in [(sys.argv[1], pem_priv), (sys.argv[2], pem_pub)]:
    tmp = p + ".tmp"
    with open(tmp, "wb") as f:
        f.write(c)
    os.replace(tmp, p)
PYEOF
  sudo -n chown ate-authority:ate-authority "$AUTHORITY_KEY"
  sudo -n chmod 0600 "$AUTHORITY_KEY"
  sudo -n chown root:root "$AUTHORITY_PUBKEY"
  sudo -n chmod 0644 "$AUTHORITY_PUBKEY"
fi

# --- 8. Launch authority service ---
AUTHORITY_SOCK="$ATE_RUN/authority/authority.sock"
# Authority must NOT regenerate the key. The crypto module checks if the
# file exists; since we pre-create it above, it loads the existing key.
sudo -n rm -f "$AUTHORITY_SOCK"
sudo -n -u ate-authority /usr/bin/python3 "$ATE_OPT_BIN/authority_service.py" \
  --db "$AUTHORITY_DB" \
  --key "$AUTHORITY_KEY" \
  --pubkey "$AUTHORITY_PUBKEY" \
  --sock "$AUTHORITY_SOCK" \
  > "$ATE_VAR_LIB/authority.log" 2>&1 &
AUTHORITY_PID=$!

# Wait for authority socket
AUTH_READY=0
for i in $(seq 1 50); do
  [ -S "$AUTHORITY_SOCK" ] && AUTH_READY=1 && break
  sleep 0.1
done
if [ "$AUTH_READY" != "1" ] || ! kill -0 "$AUTHORITY_PID" 2>/dev/null; then
  echo "AUTHORITY STARTUP FAILED; log tail:" >&2
  sudo -n cat "$ATE_VAR_LIB/authority.log" >&2 || true
  exit 10
fi
sudo -n chown ate-authority:ate-requester "$AUTHORITY_SOCK" 2>/dev/null || true
sudo -n chmod 0660 "$AUTHORITY_SOCK" 2>/dev/null || true

# --- 10. Launch executor service ---
EXECUTOR_DB="$ATE_VAR_LIB/executor/executor.sqlite"
EXECUTOR_SOCK="$ATE_RUN/executor/executor.sock"
sudo -n touch "$EXECUTOR_DB"
sudo -n chown ate-executor:ate-executor "$EXECUTOR_DB"
sudo -n chmod 0600 "$EXECUTOR_DB"
sudo -n rm -f "$EXECUTOR_SOCK"

sudo -n -u ate-executor /usr/bin/python3 "$ATE_OPT_BIN/executor_service.py" \
  --db "$EXECUTOR_DB" \
  --audit_key "$AUDIT_KEY" \
  --authority_pubkey "$AUTHORITY_PUBKEY" \
  --resource_credentials "$CRED_FILE" \
  --resources_dir "$ATE_VAR_LIB/resources" \
  --sock "$EXECUTOR_SOCK" \
  > "$ATE_VAR_LIB/executor.log" 2>&1 &
EXECUTOR_PID=$!

# Wait for executor socket
EXEC_READY=0
for i in $(seq 1 50); do
  [ -S "$EXECUTOR_SOCK" ] && EXEC_READY=1 && break
  sleep 0.1
done
if [ "$EXEC_READY" != "1" ] || ! kill -0 "$EXECUTOR_PID" 2>/dev/null; then
  echo "EXECUTOR STARTUP FAILED; log tail:" >&2
  sudo -n cat "$ATE_VAR_LIB/executor.log" >&2 || true
  exit 11
fi
sudo -n chown ate-executor:ate-requester "$EXECUTOR_SOCK" 2>/dev/null || true
sudo -n chmod 0660 "$EXECUTOR_SOCK" 2>/dev/null || true

# --- 10b. Readiness probe: as ate-requester, connect to each socket ---
PROBE_SCRIPT=$(cat <<'PYEOF'
import socket, sys
for sock in sys.argv[1:]:
    s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    s.settimeout(2)
    s.connect(sock)
    s.close()
print("OK")
PYEOF
)
PROBE_OUT=$(sudo -n -u ate-requester /usr/bin/python3 -c "$PROBE_SCRIPT" "$AUTHORITY_SOCK" "$EXECUTOR_SOCK" 2>&1)
if [ "$PROBE_OUT" != "OK" ]; then
  echo "READINESS PROBE FAILED: $PROBE_OUT" >&2
  exit 12
fi

# --- 11. Write bootstrap.env ---
ENV_FILE="$ATE_VAR_LIB/bootstrap.env"
sudo -n bash -c "cat > '$ENV_FILE' <<EOF
ATE_OPT_BIN=$ATE_OPT_BIN
ATE_ETC=$ATE_ETC
ATE_VAR_LIB=$ATE_VAR_LIB
ATE_RUN=$ATE_RUN
ATE_AUTHORITY_DB=$AUTHORITY_DB
ATE_AUTHORITY_KEY=$AUTHORITY_KEY
ATE_AUTHORITY_PUBKEY=$AUTHORITY_PUBKEY
ATE_AUTHORITY_SOCK=$AUTHORITY_SOCK
ATE_EXECUTOR_DB=$EXECUTOR_DB
ATE_EXECUTOR_AUDIT_KEY=$AUDIT_KEY
ATE_EXECUTOR_SOCK=$EXECUTOR_SOCK
ATE_RESOURCE_CREDS=$CRED_FILE
ATE_RESOURCES_DIR=$ATE_VAR_LIB/resources
ATE_AUTHORITY_PID=$AUTHORITY_PID
ATE_EXECUTOR_PID=$EXECUTOR_PID
EOF"
sudo -n chmod 0644 "$ENV_FILE"

echo "BOOTSTRAP READY (sockets up, processes alive, readiness probe OK)"
echo "authority_pid=$AUTHORITY_PID executor_pid=$EXECUTOR_PID"
echo "ENV=$ENV_FILE"

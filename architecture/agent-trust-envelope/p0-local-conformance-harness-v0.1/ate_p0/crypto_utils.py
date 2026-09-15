import base64, hashlib, json
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey, Ed25519PublicKey


def canonical(obj):
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()

def digest(obj):
    return hashlib.sha256(canonical(obj)).hexdigest()

def deterministic_private(label: str):
    seed = hashlib.sha256(("ATE-P0:"+label).encode()).digest()
    return Ed25519PrivateKey.from_private_bytes(seed)

def pub_b64(priv):
    return base64.b64encode(priv.public_key().public_bytes_raw()).decode()

def sign_payload(priv, payload):
    return base64.b64encode(priv.sign(canonical(payload))).decode()

def verify_signature(public_b64, payload, sig_b64):
    try:
        pub = Ed25519PublicKey.from_public_bytes(base64.b64decode(public_b64))
        pub.verify(base64.b64decode(sig_b64), canonical(payload))
        return True
    except Exception:
        return False

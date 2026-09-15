from dataclasses import dataclass
from .crypto_utils import digest, pub_b64, sign_payload

SUPPORTED_VERSION = "1.0"

@dataclass
class Authority:
    authority_id: str
    role: str
    private_key: object
    @property
    def public_key_b64(self): return pub_b64(self.private_key)


def signed_artifact(authority, artifact_type, body, version=SUPPORTED_VERSION):
    payload={"version":version,"artifact_type":artifact_type,"issuer":authority.authority_id,"body":body}
    return {**payload,"public_key_b64":authority.public_key_b64,"signature":sign_payload(authority.private_key,payload)}

def signed_payload_view(a):
    return {k:a[k] for k in ("version","artifact_type","issuer","body")}

def action_digest(action): return digest(action)
def envelope_binding_hash(env):
    keys=["subject_identity","session_identity","live_provenance","coa_acceptance","va_policy","behavioral_receipt","capability_token","requested_action","nonce"]
    return digest({k:env[k] for k in keys})

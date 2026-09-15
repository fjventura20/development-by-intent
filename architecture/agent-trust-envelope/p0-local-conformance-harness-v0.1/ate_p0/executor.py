import time
from .artifacts import signed_payload_view, action_digest
from .crypto_utils import verify_signature

class SandboxExecutor:
    def __init__(self, roots, nonces, audit): self.roots=roots; self.nonces=nonces; self.audit=audit; self.effects=[]
    def execute(self,decision,action,now=None):
        now=int(time.time()) if now is None else now
        body=decision.get("body",{})
        if not self.roots.is_authorized(decision.get("issuer"),"TRUST_DECISION",decision.get("public_key_b64")): return False,"GX_UNTRUSTED_ISSUER"
        if not verify_signature(decision.get("public_key_b64",""),signed_payload_view(decision),decision.get("signature","")): return False,"GX_SIGNATURE_INVALID"
        if body.get("verdict")!="TRUST_GRANTED": return False,body.get("reason_code","GX_DENIED")
        if not (body.get("issued_at",0)<=now<body.get("expires_at",0)): return False,"GX_DECISION_EXPIRED"
        if action_digest(action)!=body.get("requested_action_digest"): return False,"GX_ACTION_BINDING_MISMATCH"
        nonce=body.get("nonce")
        st=self.nonces.state(nonce)
        if st=="NONCE_CONSUMED": return False,"GX_NONCE_PREVIOUSLY_CONSUMED"
        if st=="NONCE_UNSEEN": self.nonces.authorize(nonce)
        if not self.nonces.reserve(nonce): return False,"GX_NONCE_NOT_EXECUTABLE"
        self.effects.append(action.copy())
        self.nonces.consume(nonce)
        self.audit.append("EXECUTION_SUCCEEDED",{"nonce":nonce,"action_digest":body.get("requested_action_digest")})
        return True,"GX_OK"

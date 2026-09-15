class TrustRootRegistry:
    def __init__(self): self._roles={}
    def authorize(self, authority_id, role, public_key_b64): self._roles[(authority_id,role)] = public_key_b64
    def is_authorized(self, authority_id, role, public_key_b64): return self._roles.get((authority_id,role)) == public_key_b64

class NonceRegistry:
    def __init__(self): self._s={}
    def state(self,n): return self._s.get(n,"NONCE_UNSEEN")
    def authorize(self,n):
        if self.state(n)!="NONCE_UNSEEN": return False
        self._s[n]="NONCE_AUTHORIZED"; return True
    def reserve(self,n):
        if self.state(n)!="NONCE_AUTHORIZED": return False
        self._s[n]="NONCE_RESERVED"; return True
    def consume(self,n):
        if self.state(n)!="NONCE_RESERVED": return False
        self._s[n]="NONCE_CONSUMED"; return True

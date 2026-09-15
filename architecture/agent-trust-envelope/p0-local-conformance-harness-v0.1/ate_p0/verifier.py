import time
from .artifacts import SUPPORTED_VERSION, signed_payload_view, action_digest, envelope_binding_hash
from .crypto_utils import verify_signature

ROLE_BY_TYPE={
 "LiveProvenanceReceipt":"IDENTITY",
 "COAAcceptanceReceipt":"GOVERNANCE",
 "VAPolicy":"VA_POLICY",
 "BehavioralEvidenceReceipt":"BEHAVIORAL",
 "CapabilityToken":"AUTHORIZATION",
 "TrustDecision":"TRUST_DECISION",
}

class TrustVerifier:
    def __init__(self, roots): self.roots=roots
    def check_artifact(self,a, expected_type):
        if a is None: return False,"GX_MISSING_REQUIRED_EVIDENCE"
        if a.get("version") != SUPPORTED_VERSION: return False,"GX_UNSUPPORTED_ARTIFACT_VERSION"
        if a.get("artifact_type") != expected_type: return False,"GX_ARTIFACT_TYPE_MISMATCH"
        role=ROLE_BY_TYPE[expected_type]
        if not self.roots.is_authorized(a.get("issuer"),role,a.get("public_key_b64")): return False,"GX_UNTRUSTED_ISSUER"
        if not verify_signature(a.get("public_key_b64",""), signed_payload_view(a), a.get("signature","")): return False,"GX_SIGNATURE_INVALID"
        return True,"GX_OK"

    def trust_decide(self,env, trust_authority, now=None):
        now = int(time.time()) if now is None else now
        required=[("live_provenance","LiveProvenanceReceipt"),("coa_acceptance","COAAcceptanceReceipt"),("va_policy","VAPolicy"),("behavioral_receipt","BehavioralEvidenceReceipt"),("capability_token","CapabilityToken")]
        for key,typ in required:
            ok,reason=self.check_artifact(env.get(key),typ)
            if not ok: return self._decision(env,trust_authority,"TRUST_DENIED",reason,now)
        lp=env["live_provenance"]["body"]; coa=env["coa_acceptance"]["body"]; va=env["va_policy"]["body"]; be=env["behavioral_receipt"]["body"]; cap=env["capability_token"]["body"]
        sid=env["session_identity"]; subj=env["subject_identity"]
        if lp.get("session_identity")!=sid or cap.get("session_identity")!=sid: return self._decision(env,trust_authority,"TRUST_DENIED","GX_SESSION_MISMATCH",now)
        if coa.get("session_identity")!=sid or coa.get("subject_identity")!=subj or cap.get("coa_acceptance_id")!=coa.get("acceptance_id"): return self._decision(env,trust_authority,"TRUST_DENIED","GX_COA_BINDING_FAILURE",now)
        triple=(va.get("policy_id"),va.get("policy_version"),va.get("policy_digest"))
        if triple != (cap.get("policy_id"),cap.get("policy_version"),cap.get("policy_digest")): return self._decision(env,trust_authority,"TRUST_DENIED","GX_VA_POLICY_INCOMPATIBLE",now)
        if not (be.get("issued_at",0) <= now < be.get("expires_at",0)): return self._decision(env,trust_authority,"TRUST_DENIED","GX_BEHAVIORAL_EXPIRED",now)
        action=env["requested_action"]
        if action.get("operation") not in cap.get("permitted_operations",[]): return self._decision(env,trust_authority,"TRUST_DENIED","GX_OPERATION_OUT_OF_SCOPE",now)
        if action.get("target") not in cap.get("permitted_targets",[]): return self._decision(env,trust_authority,"TRUST_DENIED","GX_TARGET_OUT_OF_SCOPE",now)
        return self._decision(env,trust_authority,"TRUST_GRANTED","GX_OK",now)

    def _decision(self,env,authority,verdict,reason,now):
        from .artifacts import signed_artifact
        body={"trust_decision_id":"td-"+env.get("envelope_id","unknown"),"envelope_id":env.get("envelope_id"),"envelope_binding_hash":envelope_binding_hash(env) if all(k in env for k in ["subject_identity","session_identity","live_provenance","coa_acceptance","va_policy","behavioral_receipt","capability_token","requested_action","nonce"]) else None,"subject_identity":env.get("subject_identity"),"session_identity":env.get("session_identity"),"requested_action_digest":action_digest(env.get("requested_action",{})),"verdict":verdict,"reason_code":reason,"nonce":env.get("nonce"),"issued_at":now,"expires_at":now+300}
        return signed_artifact(authority,"TrustDecision",body)

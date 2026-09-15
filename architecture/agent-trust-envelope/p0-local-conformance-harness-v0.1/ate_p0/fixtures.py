from .crypto_utils import deterministic_private, digest
from .artifacts import Authority, signed_artifact, envelope_binding_hash
from .registry import TrustRootRegistry

def authorities():
    roles={"id":"IDENTITY","gov":"GOVERNANCE","va":"VA_POLICY","beh":"BEHAVIORAL","auth":"AUTHORIZATION","trust":"TRUST_DECISION","rogue":"BEHAVIORAL"}
    return {k:Authority(k,v,deterministic_private(k)) for k,v in roles.items()}

def roots(auths):
    r=TrustRootRegistry()
    for k in ("id","gov","va","beh","auth","trust"):
        a=auths[k]; r.authorize(a.authority_id,a.role,a.public_key_b64)
    return r

def make_env(auths, now=1700000000, suffix="01"):
    subject="agent-A"; session="session-A"; nonce=f"nonce-{suffix}"
    lp=signed_artifact(auths["id"],"LiveProvenanceReceipt",{"subject_identity":subject,"session_identity":session,"event_source":"HERMES_MODEL_RESPONSE"})
    coa=signed_artifact(auths["gov"],"COAAcceptanceReceipt",{"acceptance_id":f"coa-{suffix}","subject_identity":subject,"session_identity":session,"coa_version":"1.0"})
    va_body={"policy_id":"va-main","policy_version":"1","rules":["default-deny","scoped-write","no-self-auth"]}; va_body["policy_digest"]=digest(va_body)
    va=signed_artifact(auths["va"],"VAPolicy",va_body)
    beh=signed_artifact(auths["beh"],"BehavioralEvidenceReceipt",{"subject_identity":subject,"evidence_digest":"stage-c-digest","result":"ACCEPTED","issued_at":now-10,"expires_at":now+86400})
    cap=signed_artifact(auths["auth"],"CapabilityToken",{"token_id":f"cap-{suffix}","subject_identity":subject,"session_identity":session,"coa_acceptance_id":f"coa-{suffix}","policy_id":va_body["policy_id"],"policy_version":va_body["policy_version"],"policy_digest":va_body["policy_digest"],"permitted_operations":["WRITE_FILE"],"permitted_targets":["sandbox:/authorized/report.txt"],"nonce":nonce})
    action={"operation":"WRITE_FILE","target":"sandbox:/authorized/report.txt","parameters":{"content":"hello"}}
    env={"envelope_id":f"env-{suffix}","subject_identity":subject,"session_identity":session,"live_provenance":lp,"coa_acceptance":coa,"va_policy":va,"behavioral_receipt":beh,"capability_token":cap,"requested_action":action,"nonce":nonce}
    env["envelope_binding_hash"]=envelope_binding_hash(env)
    return env

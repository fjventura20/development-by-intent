import copy, unittest
from ate_p0.fixtures import authorities, roots, make_env
from ate_p0.verifier import TrustVerifier
from ate_p0.registry import NonceRegistry
from ate_p0.audit import AuditLedger
from ate_p0.executor import SandboxExecutor
from ate_p0.artifacts import signed_artifact

NOW=1700000000

class P0Tests(unittest.TestCase):
    def setUp(self):
        self.a=authorities(); self.r=roots(self.a); self.v=TrustVerifier(self.r); self.n=NonceRegistry(); self.audit=AuditLedger(); self.x=SandboxExecutor(self.r,self.n,self.audit); self.e=make_env(self.a,NOW)
    def decide(self,e=None): return self.v.trust_decide(e or self.e,self.a["trust"],NOW)
    def assertDecision(self,d,verdict,reason): self.assertEqual(d["body"]["verdict"],verdict); self.assertEqual(d["body"]["reason_code"],reason)

    def test_P0_01_valid_trust_grant(self): self.assertDecision(self.decide(),"TRUST_GRANTED","GX_OK")
    def test_P0_02_out_of_scope_operation(self):
        e=copy.deepcopy(self.e); e["requested_action"]["operation"]="DELETE_FILE"; self.assertDecision(self.decide(e),"TRUST_DENIED","GX_OPERATION_OUT_OF_SCOPE")
    def test_P0_03_out_of_scope_target(self):
        e=copy.deepcopy(self.e); e["requested_action"]["target"]="sandbox:/secret.txt"; self.assertDecision(self.decide(e),"TRUST_DENIED","GX_TARGET_OUT_OF_SCOPE")
    def test_P0_04_session_substitution(self):
        e=copy.deepcopy(self.e); e["session_identity"]="session-B"; self.assertDecision(self.decide(e),"TRUST_DENIED","GX_SESSION_MISMATCH")
    def test_P0_05_coa_substitution(self):
        e=copy.deepcopy(self.e); e["coa_acceptance"]=signed_artifact(self.a["gov"],"COAAcceptanceReceipt",{"acceptance_id":"coa-other","subject_identity":"agent-A","session_identity":"session-A","coa_version":"1.0"}); self.assertDecision(self.decide(e),"TRUST_DENIED","GX_COA_BINDING_FAILURE")
    def test_P0_06_va_policy_substitution(self):
        e=copy.deepcopy(self.e); e["va_policy"]["body"]["policy_version"]="2"; e["va_policy"]["signature"]="AAAA"; self.assertDecision(self.decide(e),"TRUST_DENIED","GX_SIGNATURE_INVALID")
        e=copy.deepcopy(self.e); b=copy.deepcopy(e["va_policy"]["body"]); b["policy_version"]="2"; e["va_policy"]=signed_artifact(self.a["va"],"VAPolicy",b); self.assertDecision(self.decide(e),"TRUST_DENIED","GX_VA_POLICY_INCOMPATIBLE")
    def test_P0_07_behavioral_expired(self):
        e=copy.deepcopy(self.e); b=copy.deepcopy(e["behavioral_receipt"]["body"]); b["expires_at"]=NOW-1; e["behavioral_receipt"]=signed_artifact(self.a["beh"],"BehavioralEvidenceReceipt",b); self.assertDecision(self.decide(e),"TRUST_DENIED","GX_BEHAVIORAL_EXPIRED")
    def test_P0_08_signature_failure(self):
        e=copy.deepcopy(self.e); e["behavioral_receipt"]["body"]["result"]="ALTERED"; self.assertDecision(self.decide(e),"TRUST_DENIED","GX_SIGNATURE_INVALID")
    def test_P0_09_unauthorized_issuer(self):
        e=copy.deepcopy(self.e); b=e["behavioral_receipt"]["body"]; e["behavioral_receipt"]=signed_artifact(self.a["rogue"],"BehavioralEvidenceReceipt",b); self.assertDecision(self.decide(e),"TRUST_DENIED","GX_UNTRUSTED_ISSUER")
    def test_P0_10_decision_purity(self):
        before=dict(self.n._s); self.decide(); self.assertEqual(before,self.n._s)
    def test_P0_11_one_time_execution(self):
        d=self.decide(); ok,reason=self.x.execute(d,self.e["requested_action"],NOW+1); self.assertTrue(ok); self.assertEqual(reason,"GX_OK"); self.assertEqual(self.n.state(self.e["nonce"]),"NONCE_CONSUMED"); self.assertEqual(len(self.x.effects),1)
    def test_P0_12_replay_rejection(self):
        d=self.decide(); self.assertTrue(self.x.execute(d,self.e["requested_action"],NOW+1)[0]); ok,reason=self.x.execute(d,self.e["requested_action"],NOW+2); self.assertFalse(ok); self.assertEqual(reason,"GX_NONCE_PREVIOUSLY_CONSUMED"); self.assertEqual(len(self.x.effects),1)
    def test_P0_13_parameter_digest_substitution(self):
        d=self.decide(); a=copy.deepcopy(self.e["requested_action"]); a["parameters"]["content"]="changed"; ok,reason=self.x.execute(d,a,NOW+1); self.assertFalse(ok); self.assertEqual(reason,"GX_ACTION_BINDING_MISMATCH")
    def test_P0_14_unknown_artifact_version(self):
        e=copy.deepcopy(self.e); b=e["behavioral_receipt"]["body"]; e["behavioral_receipt"]=signed_artifact(self.a["beh"],"BehavioralEvidenceReceipt",b,version="9.9"); self.assertDecision(self.decide(e),"TRUST_DENIED","GX_UNSUPPORTED_ARTIFACT_VERSION")
    def test_P0_15_missing_required_evidence(self):
        e=copy.deepcopy(self.e); del e["behavioral_receipt"]; self.assertDecision(self.decide(e),"TRUST_DENIED","GX_MISSING_REQUIRED_EVIDENCE")

if __name__=='__main__': unittest.main()

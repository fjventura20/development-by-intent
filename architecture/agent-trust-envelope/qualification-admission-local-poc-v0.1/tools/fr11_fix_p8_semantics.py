#!/usr/bin/env python3
"""Correct QA-P8 so it can pass only for the frozen intended reason.

The EAP validates issuer permissions in this order: CapabilityToken,
TrustDecision, QualificationCredential. QA-P8's local registry must therefore
permit the legitimate AUTH_AUTHORIZATION and AUTH_TRUST_DECISION keys while
explicitly denying AUTH_IDENTITY permission to sign QualificationCredential.

This script also replaces the stale pytest QA-P8 regression with a direct
assertion over the authoritative case_p8() evidence.
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
helpers_path = ROOT / "tests" / "_helpers.py"
case_path = ROOT / "tests" / "case_functions.py"
test_path = ROOT / "tests" / "test_qa_matrix_missing.py"


def replace_once(text: str, old: str, new: str, label: str) -> str:
    n = text.count(old)
    if n != 1:
        raise SystemExit(f"{label}: expected one occurrence, found {n}")
    return text.replace(old, new, 1)


# 1) Registry supports the legitimate capability + trust-decision signers.
h = helpers_path.read_text()
old_sig = '''    @classmethod
    def build_default(cls, *, auth_identity_key_id: str, r11_key_id: str) -> "IssuerAuthorizationRegistry":
'''
new_sig = '''    @classmethod
    def build_default(
        cls,
        *,
        auth_identity_key_id: str,
        r11_key_id: str,
        authorization_key_id: str | None = None,
        trust_decision_key_id: str | None = None,
    ) -> "IssuerAuthorizationRegistry":
'''
h = replace_once(h, old_sig, new_sig, "IssuerAuthorizationRegistry signature")
old_import = '''        from qa_poc.models import (
            DOMAIN_ADMISSION_CREDENTIAL,
            DOMAIN_QUALIFICATION_CREDENTIAL,
            DOMAIN_QUALIFICATION_EVIDENCE_MANIFEST,
        )
'''
new_import = '''        from qa_poc.models import (
            DOMAIN_ADMISSION_CREDENTIAL,
            DOMAIN_CAPABILITY_TOKEN,
            DOMAIN_QUALIFICATION_CREDENTIAL,
            DOMAIN_QUALIFICATION_EVIDENCE_MANIFEST,
            DOMAIN_TRUST_DECISION,
        )
'''
h = replace_once(h, old_import, new_import, "issuer registry domain imports")
old_perms = '''        perms = {
            (auth_identity_key_id, DOMAIN_QUALIFICATION_EVIDENCE_MANIFEST): True,
            (auth_identity_key_id, DOMAIN_QUALIFICATION_CREDENTIAL): False,
            (auth_identity_key_id, DOMAIN_ADMISSION_CREDENTIAL): False,
            (r11_key_id, DOMAIN_QUALIFICATION_CREDENTIAL): True,
        }
        return cls(auth_role=auth_identity_key_id, artifact_type_permissions=perms)
'''
new_perms = '''        perms = {
            (auth_identity_key_id, DOMAIN_QUALIFICATION_EVIDENCE_MANIFEST): True,
            (auth_identity_key_id, DOMAIN_QUALIFICATION_CREDENTIAL): False,
            (auth_identity_key_id, DOMAIN_ADMISSION_CREDENTIAL): False,
            (r11_key_id, DOMAIN_QUALIFICATION_CREDENTIAL): True,
        }
        if authorization_key_id is not None:
            perms[(authorization_key_id, DOMAIN_CAPABILITY_TOKEN)] = True
        if trust_decision_key_id is not None:
            perms[(trust_decision_key_id, DOMAIN_TRUST_DECISION)] = True
        return cls(auth_role=auth_identity_key_id, artifact_type_permissions=perms)
'''
h = replace_once(h, old_perms, new_perms, "issuer registry permissions")
helpers_path.write_text(h)


# 2) Formal case computes and allows the legitimate auth/trust signer IDs,
#    while still forbidding AUTH_IDENTITY for QualificationCredential.
c = case_path.read_text()
old_ids = '''        r11_kid = key_id_from_public_pem(
            harness.keys.r11_pub.public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo,
            )
        )
        reg_auth = IssuerAuthorizationRegistry.build_default(
            auth_identity_key_id=auth_identity_kid,
            r11_key_id=r11_kid,
        )
'''
new_ids = '''        r11_kid = key_id_from_public_pem(
            harness.keys.r11_pub.public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo,
            )
        )
        authorization_kid = key_id_from_public_pem(
            harness.keys.auth_pub.public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo,
            )
        )
        trust_decision_kid = key_id_from_public_pem(
            harness.keys.trust_pub.public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo,
            )
        )
        reg_auth = IssuerAuthorizationRegistry.build_default(
            auth_identity_key_id=auth_identity_kid,
            r11_key_id=r11_kid,
            authorization_key_id=authorization_kid,
            trust_decision_key_id=trust_decision_kid,
        )
'''
c = replace_once(c, old_ids, new_ids, "QA-P8 signer registry")
old_subcheck = '''            "issuer_authorization_check_rejects": (
                "PASS" if (result.verdict == "EXECUTION_DENIED"
                            and "ISSUER_NOT_AUTHORIZED" in result.reason_code)
                else "FAIL"
            ),
'''
new_subcheck = '''            "issuer_authorization_check_rejects_qualification_credential": (
                "PASS" if (
                    result.verdict == "EXECUTION_DENIED"
                    and "ISSUER_NOT_AUTHORIZED_FOR_ARTIFACT_TYPE" in result.reason_code
                    and "qualification_credential" in result.reason_code
                    and DOMAIN_QUALIFICATION_CREDENTIAL in result.reason_code
                    and "capability_token" not in result.reason_code
                    and "trust_decision" not in result.reason_code
                ) else "FAIL"
            ),
'''
c = replace_once(c, old_subcheck, new_subcheck, "QA-P8 exact denial subcheck")
case_path.write_text(c)


# 3) Replace the stale pytest QA-P8 block with a regression over case_p8.
t = test_path.read_text()
start = t.index('def test_qa_p8_valid_signature_unauthorized_issuer_rejected')
end = t.index('\n\n# --- QA-P9:', start)
new_test = '''def test_qa_p8_valid_signature_unauthorized_issuer_rejected():
    """QA-P8 must reject AUTH_IDENTITY specifically as an unauthorized
    QualificationCredential issuer, after valid capability/trust signers pass.
    """
    import tempfile
    from tests.case_functions import case_p8

    h = FixtureHarness.build()
    with tempfile.TemporaryDirectory(prefix="qa-p8-regression-") as tmp:
        ev = case_p8(h, tmp)
    assert ev.pass_fail == "PASS", ev.to_dict()
    assert ev.verdict == "EXECUTION_DENIED"
    assert "ISSUER_NOT_AUTHORIZED_FOR_ARTIFACT_TYPE" in ev.reason_code
    assert "qualification_credential" in ev.reason_code
    assert DOMAIN_QUALIFICATION_CREDENTIAL in ev.reason_code
    assert "capability_token" not in ev.reason_code
    assert "trust_decision" not in ev.reason_code
    assert ev.subcheck_results["crypto_signature_valid_against_auth_identity_pub"] == "PASS"
    assert ev.subcheck_results["auth_identity_recognized_active"] == "PASS"
    assert ev.subcheck_results["auth_identity_lacks_r11_qualcred_permission"] == "PASS"
    assert ev.subcheck_results["issuer_authorization_check_rejects_qualification_credential"] == "PASS"
    assert ev.subcheck_results["no_protected_mutation"] == "PASS"
'''
t = t[:start] + new_test + t[end:]
test_path.write_text(t)

print("QA-P8 semantic correction applied")
print("Updated: tests/_helpers.py, tests/case_functions.py, tests/test_qa_matrix_missing.py")
print("Formal scored run remains unauthorized.")

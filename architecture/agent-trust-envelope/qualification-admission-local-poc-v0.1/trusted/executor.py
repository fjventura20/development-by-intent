"""ATE Qualification & Admission Local PoC v0.1 — Execution Authorization Point.

Per design §23: `execute_bound_action()` opens one executor-owned
BEGIN IMMEDIATE transaction. Inside that transaction:

  verify bundle structure/canonical digests
  verify CapabilityToken + TrustDecision signatures and issuer permissions
  verify exact qualification/admission ids + digests
  verify live SubjectBinding
  verify derived/current expiration using TestClock
  read current applied control state
  recursively validate qualification -> admission dependency
  verify nonce unused
  insert nonce reservation
  append EAP_REACHED audit row
  update protected_resource + mutation_count
  append EXECUTION_SUCCEEDED audit row
  COMMIT

For this local PoC, EAP_REACHED, protected mutation, and EXECUTION_SUCCEEDED
are authoritative only if the transaction commits.

Therefore: committed EAP_REACHED <=> protected local mutation committed.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Optional

from qa_poc.admission import DependencyEvaluationError, check_admission_usable
from qa_poc.canonical import canonical_sha256
from qa_poc.clock import Clock
from qa_poc.crypto import Ed25519PublicKey, verify_ed25519
from qa_poc.models import (
    CapabilityToken,
    DOMAIN_CAPABILITY_TOKEN,
    DOMAIN_TRUST_DECISION,
    DigestMismatchError,
    IdMismatchError,
    SignatureError,
    TrustDecision,
    artifact_payload,
    digest_payload,
    verify_artifact,
)
from qa_poc.subject_binding import SubjectBinding
from trusted import audit_ingest, enforcement_store


@dataclass
class BoundActionBundle:
    subject_binding: SubjectBinding
    capability: CapabilityToken
    trust_decision: TrustDecision
    action: dict  # {"target", "operation", "parameters"}


@dataclass
class EapResult:
    verdict: str  # EXECUTION_SUCCEEDED / EXECUTION_DENIED
    reason_code: str
    mutation_count: int
    eap_reached_seq: int
    success_seq: Optional[int]
    observed_epoch: int
    resource_id: str


def execute_bound_action(
    conn,
    *,
    bundle: BoundActionBundle,
    auth_pub: Ed25519PublicKey,
    trust_pub: Ed25519PublicKey,
    revocation_lookup: Callable[[str], tuple],
    bound_qualification,  # QualificationCredential for recursive eval
    bound_admission,  # AdmissionCredential
    qualification_pub: Ed25519PublicKey,
    admission_pub: Ed25519PublicKey,
    resource_id: str,
    new_resource_value: str,
    clock: Clock,
    live_proof_verifier: Optional[Callable[[], None]] = None,
    issuer_authorization_lookup: Optional[Callable[[str, str], bool]] = None,
) -> EapResult:
    """Execute the bound action at the EAP. This is the load-bearing
    call for QA-P1..QA-P14.

    All validations happen INSIDE the executor-owned BEGIN IMMEDIATE
    transaction; any failure rolls back and the audit row written is
    EXECUTION_DENIED (in a separate transaction per §24).

    `issuer_authorization_lookup` is an optional (key_id, artifact_type)
    -> bool function consulted after signature verification. The
    signature may cryptographically verify against the supplied pub,
    but the publisher key may still lack artifact-type permission
    (frozen §6 + §28 QA-P8). When provided, the EAP denies with
    `ISSUER_NOT_AUTHORIZED_FOR_ARTIFACT_TYPE` if the lookup fails.
    """

    # Helper: cross-check authorization after a successful verify_artifact
    def _check_authorized(artifact_type: str, pub: Ed25519PublicKey, label: str):
        if issuer_authorization_lookup is None:
            return None
        try:
            from cryptography.hazmat.primitives import serialization
            from qa_poc.crypto import key_id_from_public_pem
            pem = pub.public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo,
            )
            kid = key_id_from_public_pem(pem)
        except Exception:
            kid = "<unknown>"
        if not issuer_authorization_lookup(kid, artifact_type):
            return _deny(
                conn,
                bundle,
                action_digest_val,
                bound_qualification,
                bound_admission,
                f"ISSUER_NOT_AUTHORIZED_FOR_ARTIFACT_TYPE: {label} signed by key_id={kid[:16]}... which lacks permission for {artifact_type}",
                resource_id,
                clock,
            )
        return None

    # Build action_digest for nonce binding
    action_digest_val = canonical_sha256(bundle.action)

    # === Validate signatures & canonical forms (DEV-IMP-3) ===
    # (1) CapabilityToken: recompute digest from (id, semantic fields),
    #     then verify signature over (id, semantic fields, digest).
    try:
        verify_artifact(bundle.capability, auth_pub)
    except (DigestMismatchError, SignatureError) as e:
        return _deny(
            conn,
            bundle,
            action_digest_val,
            bound_qualification,
            bound_admission,
            f"CAPABILITY_VERIFY_FAILED: {type(e).__name__}: {e}",
            resource_id,
            clock,
        )
    auth_check = _check_authorized(DOMAIN_CAPABILITY_TOKEN, auth_pub, "capability_token")
    if auth_check is not None:
        return auth_check

    # (2) TrustDecision
    try:
        verify_artifact(bundle.trust_decision, trust_pub)
    except (DigestMismatchError, SignatureError) as e:
        return _deny(
            conn,
            bundle,
            action_digest_val,
            bound_qualification,
            bound_admission,
            f"TRUST_DECISION_VERIFY_FAILED: {type(e).__name__}: {e}",
            resource_id,
            clock,
        )
    auth_check = _check_authorized(DOMAIN_TRUST_DECISION, trust_pub, "trust_decision")
    if auth_check is not None:
        return auth_check

    # (1b) Bound qualification: verify signature against the supplied
    # qualification_pub (which the caller may have overridden for QA-P8
    # purposes), then consult the authorization registry if provided.
    try:
        verify_artifact(bound_qualification, qualification_pub)
    except (DigestMismatchError, SignatureError) as e:
        return _deny(
            conn,
            bundle,
            action_digest_val,
            bound_qualification,
            bound_admission,
            f"BOUND_QUALIFICATION_VERIFY_FAILED: {type(e).__name__}: {e}",
            resource_id,
            clock,
        )
    from qa_poc.models import DOMAIN_QUALIFICATION_CREDENTIAL
    auth_check = _check_authorized(
        DOMAIN_QUALIFICATION_CREDENTIAL, qualification_pub, "qualification_credential"
    )
    if auth_check is not None:
        return auth_check

    # (3) TrustDecision.verdict must be AUTHORIZED
    if bundle.trust_decision.verdict != "AUTHORIZED":
        return _deny(
            conn,
            bundle,
            action_digest_val,
            bound_qualification,
            bound_admission,
            "TRUST_DECISION_NOT_AUTHORIZED",
            resource_id,
            clock,
        )

    # (4) CapabilityToken + TrustDecision must reference each other
    if bundle.trust_decision.capability_token_id != bundle.capability.token_id:
        return _deny(
            conn,
            bundle,
            action_digest_val,
            bound_qualification,
            bound_admission,
            "TRUST_DECISION_CAPABILITY_ID_MISMATCH",
            resource_id,
            clock,
        )
    if bundle.trust_decision.capability_token_digest != bundle.capability.token_digest:
        return _deny(
            conn,
            bundle,
            action_digest_val,
            bound_qualification,
            bound_admission,
            "TRUST_DECISION_CAPABILITY_DIGEST_MISMATCH",
            resource_id,
            clock,
        )

    # (5) CapabilityToken must reference bound qualification + admission
    if (
        bundle.capability.qualification_credential_id != bound_qualification.credential_id
        or bundle.capability.qualification_credential_digest != bound_qualification.credential_digest
    ):
        return _deny(
            conn,
            bundle,
            action_digest_val,
            bound_qualification,
            bound_admission,
            "CAPABILITY_QUALIFICATION_BINDING_MISMATCH",
            resource_id,
            clock,
        )
    if (
        bundle.capability.admission_credential_id != bound_admission.credential_id
        or bundle.capability.admission_credential_digest != bound_admission.credential_digest
    ):
        return _deny(
            conn,
            bundle,
            action_digest_val,
            bound_qualification,
            bound_admission,
            "CAPABILITY_ADMISSION_BINDING_MISMATCH",
            resource_id,
            clock,
        )

    # (6) Live SubjectBinding verification (frozen §10 + §23)
    if live_proof_verifier is not None:
        try:
            live_proof_verifier()
        except Exception as e:
            return _deny(
                conn,
                bundle,
                action_digest_val,
                bound_qualification,
                bound_admission,
                f"SUBJECT_BINDING_LIVE_PROOF_FAILED: {type(e).__name__}",
                resource_id,
                clock,
            )

    # (7) SubjectBinding digest must match Capability's bound subject_binding
    sb_digest = bundle.subject_binding.digest()
    if sb_digest != bundle.capability.subject_binding_digest:
        return _deny(
            conn,
            bundle,
            action_digest_val,
            bound_qualification,
            bound_admission,
            "SUBJECT_BINDING_DIGEST_MISMATCH",
            resource_id,
            clock,
        )

    # (7b) SubjectBinding identity must match the bound qualification's
    # subject_identity_id AND the bound admission's subject_identity_id.
    # This is the §7 / §23 credential-transplant rejection path (QA-P7).
    if (
        bundle.subject_binding.subject_identity_id
        != bound_qualification.subject_identity_id
        or bundle.subject_binding.subject_identity_id
        != bound_admission.subject_identity_id
    ):
        return _deny(
            conn,
            bundle,
            action_digest_val,
            bound_qualification,
            bound_admission,
            "SUBJECT_BINDING_IDENTITY_NOT_BOUND_TO_CREDENTIALS",
            resource_id,
            clock,
        )
    if (
        bound_qualification.subject_binding_digest != sb_digest
        or bound_admission.subject_binding_digest != sb_digest
    ):
        return _deny(
            conn,
            bundle,
            action_digest_val,
            bound_qualification,
            bound_admission,
            "BOUND_CREDENTIAL_SUBJECT_BINDING_MISMATCH",
            resource_id,
            clock,
        )

    # (8) Derived/current expiration (TestClock)
    if clock.now_unix_ms >= bundle.capability.expires_at_unix_ms:
        return _deny(
            conn,
            bundle,
            action_digest_val,
            bound_qualification,
            bound_admission,
            "CAPABILITY_EXPIRED",
            resource_id,
            clock,
        )
    if clock.now_unix_ms >= bundle.trust_decision.expires_at_unix_ms:
        return _deny(
            conn,
            bundle,
            action_digest_val,
            bound_qualification,
            bound_admission,
            "TRUST_DECISION_EXPIRED",
            resource_id,
            clock,
        )

    # (8b) Historical TrustStateReference coherence (§15).
    # The capability, the trust decision, the bound qualification,
    # and the bound admission MUST all reference the same coherent
    # committed-state snapshot. If any pair disagrees, the EAP
    # denies with *_TRUST_STATE_INCONSISTENT.
    snap_refs = {
        "capability": bundle.capability.historical_trust_state_reference,
        "trust_decision": bundle.trust_decision.historical_trust_state_reference,
        "qualification": bound_qualification.historical_trust_state_reference,
        "admission": bound_admission.historical_trust_state_reference,
    }
    if len(set(snap_refs.values())) > 1:
        return _deny(
            conn,
            bundle,
            action_digest_val,
            bound_qualification,
            bound_admission,
            "TRUST_STATE_INCONSISTENT: snapshot_reference mismatch across capability/trust_decision/qualification/admission",
            resource_id,
            clock,
        )

    # (9) Recursive qualification -> admission usability (§19)
    try:
        check_admission_usable(
            admission=bound_admission,
            clock=clock,
            qualification=bound_qualification,
            revocation_lookup=revocation_lookup,
        )
    except DependencyEvaluationError as e:
        return _deny(
            conn,
            bundle,
            action_digest_val,
            bound_qualification,
            bound_admission,
            str(e),
            resource_id,
            clock,
        )

    # (10) Read current applied control state — must be at least the
    # historical reference epoch (frozen §15).
    observed_epoch = enforcement_store.current_epoch(conn)
    if observed_epoch < 0:
        # Just a sanity guard; should be impossible after bootstrap
        return _deny(
            conn,
            bundle,
            action_digest_val,
            bound_qualification,
            bound_admission,
            "OBSERVED_EPOCH_INVALID",
            resource_id,
            clock,
        )

    # All validations passed; enter the EAP transaction.
    with enforcement_store.eap_transaction(conn) as tx:
        try:
            # (11) Verify nonce unused (insert-or-ignore)
            ok = enforcement_store.reserve_nonce(
                tx,
                nonce=bundle.capability.nonce,
                action_digest=action_digest_val,
                reserved_at_unix_ms=clock.now_unix_ms,
            )
            if not ok:
                tx.execute("ROLLBACK")
                return _deny(
                    conn,
                    bundle,
                    action_digest_val,
                    bound_qualification,
                    bound_admission,
                    "NONCE_ALREADY_USED",
                    resource_id,
                    clock,
                )

            # (12) EAP_REACHED
            eap_reached_seq = enforcement_store.append_audit(
                tx,
                event_type="EAP_REACHED",
                payload={
                    "subject_binding_digest": sb_digest,
                    "qualification_credential_id": bound_qualification.credential_id,
                    "admission_credential_id": bound_admission.credential_id,
                    "capability_token_id": bundle.capability.token_id,
                    "trust_decision_id": bundle.trust_decision.trust_decision_id,
                    "action_digest": action_digest_val,
                    "observed_executor_epoch": observed_epoch,
                    "created_at_unix_ms": clock.now_unix_ms,
                },
                created_at_unix_ms=clock.now_unix_ms,
            )

            # (13) Protected mutation
            new_count = enforcement_store.mutate_protected_resource(
                tx,
                resource_id=resource_id,
                new_value=new_resource_value,
            )

            # (14) EXECUTION_SUCCEEDED
            success_seq = enforcement_store.append_audit(
                tx,
                event_type="EXECUTION_SUCCEEDED",
                payload={
                    "subject_binding_digest": sb_digest,
                    "qualification_credential_id": bound_qualification.credential_id,
                    "admission_credential_id": bound_admission.credential_id,
                    "capability_token_id": bundle.capability.token_id,
                    "trust_decision_id": bundle.trust_decision.trust_decision_id,
                    "action_digest": action_digest_val,
                    "observed_executor_epoch": observed_epoch,
                    "mutation_count": new_count,
                    "resource_id": resource_id,
                    "created_at_unix_ms": clock.now_unix_ms,
                },
                created_at_unix_ms=clock.now_unix_ms,
            )
            enforcement_store.mark_nonce_executed(tx, bundle.capability.nonce)
            tx.execute("COMMIT")
            return EapResult(
                verdict="EXECUTION_SUCCEEDED",
                reason_code="",
                mutation_count=new_count,
                eap_reached_seq=eap_reached_seq,
                success_seq=success_seq,
                observed_epoch=observed_epoch,
                resource_id=resource_id,
            )
        except BaseException:
            try:
                tx.execute("ROLLBACK")
            except Exception:
                pass
            raise


def _deny(
    conn,
    bundle: BoundActionBundle,
    action_digest_val: str,
    bound_qualification,
    bound_admission,
    reason_code: str,
    resource_id: str,
    clock: Clock,
) -> EapResult:
    """Roll back any in-flight EAP transaction and append EXECUTION_DENIED
    in a separate trusted audit transaction (§24)."""
    try:
        conn.execute("ROLLBACK")
    except Exception:
        pass
    existing = enforcement_store.read_protected_resource(conn, resource_id)
    current_mc = existing["mutation_count"] if existing else 0
    audit_ingest.append_denial_audit(
        conn,
        reason_code=reason_code,
        action_digest=action_digest_val,
        bound_qualification_id=bound_qualification.credential_id,
        bound_qualification_digest=bound_qualification.credential_digest,
        bound_admission_id=bound_admission.credential_id,
        bound_admission_digest=bound_admission.credential_digest,
        observed_executor_epoch=enforcement_store.current_epoch(conn),
        created_at_unix_ms=clock.now_unix_ms,
    )
    return EapResult(
        verdict="EXECUTION_DENIED",
        reason_code=reason_code,
        mutation_count=current_mc,
        eap_reached_seq=0,
        success_seq=None,
        observed_epoch=enforcement_store.current_epoch(conn),
        resource_id=resource_id,
    )

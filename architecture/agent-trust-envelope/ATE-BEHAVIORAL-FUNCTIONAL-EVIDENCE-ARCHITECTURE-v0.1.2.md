# ATE Behavioral & Functional Evidence Architecture v0.1.2

**Status:** Surgical architecture revision — DESIGN ONLY  
**Date:** 2026-09-16  
**Program:** Agent Trust Envelope (ATE)  
**Base architecture:** `ATE-BEHAVIORAL-FUNCTIONAL-EVIDENCE-ARCHITECTURE-v0.1.1.md`  
**Final consistency review:** `ATE-BEHAVIORAL-FUNCTIONAL-EVIDENCE-FINAL-REVIEW-v0.1.md`

---

## 1. Revision Scope

This v0.1.2 artifact is a **normative surgical amendment** to v0.1.1.

All v0.1.1 sections and invariants remain controlling except where this artifact explicitly adds or replaces semantics.

The correction addresses one issue:

> A self-declared `registered_at` timestamp does not prove that a formal run definition was committed before subject execution.

v0.1.2 therefore adds an authoritative local precommitment ordering mechanism and an authoritative campaign key.

No blockchain, global timestamp service, distributed consensus, or Hermes/model execution is required.

---

## 2. Authoritative Campaign Key

Formal evaluation attempts SHALL be indexed by a canonical `campaign_key`, not only by caller-chosen campaign IDs.

Minimum input:

```text
campaign_key = digest(canonical({
    trust_domain_id,
    evidence_requirement_id,
    subject_principal_id,
    qualified_profile_digest,
    qualification_or_admission_attempt_id
}))
```

If `qualification_or_admission_attempt_id` is not applicable, a protocol-defined stable equivalent SHALL be used.

The key defines the formal-evaluation lineage for anti-selection purposes.

A caller cannot erase prior attempts by choosing a new display `campaign_id` while the controlling campaign key is unchanged.

---

## 3. Campaign Registry

A trusted local Campaign/Precommitment Registry maintains append-only campaign/run ordering state.

Conceptual state:

```text
CampaignRegistry {
    trust_domain_id
    registry_epoch
    global_or_partitioned_sequence

    campaign_key -> {
        campaign_lineage_id
        registered_formal_runs[]
        closed/open status
        predecessor/successor lineage refs[]
    }
}
```

The registry is a security-relevant authority and SHALL use the existing ATE trust-root/revocation model.

A rollback below a newer accepted `registry_epoch` or sequence state fails closed.

---

## 4. Precommitment Authority

The precommitment authority credential SHALL bind at least:

```text
precommitment_authority_id
trust_domain_id
may_commit_evidence_classes[]
accepted_protocol_families[]
registry_id
maximum_registration_validity?
not_before
valid_until
revocation_handle
issuer
signature
```

A valid signature from an authority without the required precommitment role is insufficient.

The runner may submit registrations but MUST NOT be able to manufacture accepted prior registry sequence numbers or backdated commitments.

---

## 5. Precommitment Receipt

Before first subject invocation, the registry issues:

```text
PrecommitmentReceipt {
    artifact_type = ATE_EVIDENCE_RUN_PRECOMMITMENT
    artifact_version = 1

    commitment_id
    trust_domain_id
    campaign_key
    campaign_lineage_id
    formal_run_id
    formal_run_registration_digest
    protocol_digest
    subject_principal_id
    qualified_profile_digest

    monotonic_registration_sequence
    registry_epoch
    committed_at

    precommitment_authority_id
    signature_algorithm
    signature
}
```

The receipt proves accepted ordering within the local ATE evidence trust domain.

It does not claim globally trusted wall-clock time.

---

## 6. Registration Ordering Rule

A formal run is eligible to become controlling evidence only when:

```text
valid FormalRunRegistration
AND valid PrecommitmentReceipt(registration_digest)
AND PrecommitmentReceipt accepted into current registry state
AND no subject invocation occurred before the accepted commitment
```

Every formal subject invocation SHALL bind/reference:

```text
commitment_id
formal_run_registration_digest
formal_run_id
```

The runner's signed attempt ledger and run completion record SHALL preserve those bindings.

---

## 7. Invocation Receipt Binding

Each first-level subject invocation record SHALL include or be transitively bound to:

```text
formal_run_id
commitment_id
registration_digest
case_id
replication_id
attempt_number
invocation_id
started_at
```

The runner signs or otherwise tamper-evidently records the invocation under its authorized RunnerProfile.

If an invocation cannot be linked to the precommitted registration, it is not part of a valid formal run.

---

## 8. FormalRunRegistration Additions

The v0.1.1 `FormalRunRegistration` is amended to include:

```text
campaign_key
campaign_lineage_id
registration_nonce
```

The registration digest covers these fields.

After registry commitment, any change requires a new registration and a new commitment sequence entry.

---

## 9. RunCompletionRecord Additions

The v0.1.1 `RunCompletionRecord` SHALL include:

```text
commitment_id
precommitment_receipt_digest
campaign_key
registry_epoch_at_registration
monotonic_registration_sequence
```

Completion validation verifies that the receipt/registration/campaign bindings agree.

---

## 10. Aggregate Evidence Receipt Additions

Both BehavioralEvidenceReceipt and FunctionalEvidenceReceipt SHALL include:

```text
campaign_key
commitment_id
precommitment_receipt_digest
monotonic_registration_sequence
registry_epoch_at_registration
```

Evidence Issuer verifies these before aggregate issuance.

---

## 11. Campaign History Rule

Qualification/evidence policy MAY permit later attempts, but all attempts under the same `campaign_key` remain discoverable from the authoritative campaign registry.

A later PASS cannot make an earlier formal FAIL disappear.

The Evidence Receipt SHALL include the prior formal attempt references required by the active formal-attempt policy.

When a legitimate profile/protocol/qualification-attempt change starts a new campaign lineage, the registry SHALL record the predecessor/successor relationship when policy requires continuity.

---

## 12. New / Amended Invariants

### E-I2A — AUTHORITATIVE_PRECOMMITMENT
A formal run is not preregistered merely because its registration contains an earlier timestamp. An authorized registry must accept the exact registration digest before first subject invocation.

### E-I2B — MONOTONIC_RUN_ORDER
Accepted precommitments have monotonic registry ordering/epoch semantics protected against known-state rollback.

### E-I5A — AUTHORITATIVE_CAMPAIGN_KEY
Formal attempt history is keyed by canonical campaign context, not caller-selected campaign IDs alone.

### E-I5B — CAMPAIGN_HISTORY_NON_ERASURE
A new campaign/run identifier cannot hide prior formal attempts that policy associates with the same campaign key/lineage.

All v0.1.1 invariants remain controlling.

---

## 13. Threats Closed by v0.1.2

v0.1.2 specifically closes:

- post-hoc backdated registration;
- favorable-population manifest creation after execution;
- runner-controlled chronology claims;
- hiding failed formal attempts by changing a campaign display ID;
- replaying an older registry state after a newer formal attempt is known;
- aggregate receipts detached from the actual preregistered run.

---

## 14. Out of Scope

This local architecture does not attempt to solve:

- globally verifiable timestamps;
- distributed consensus;
- malicious trust-root compromise;
- compromised precommitment authority;
- kernel/root compromise;
- public transparency logs.

Higher-assurance deployments may replace the local registry with stronger append-only/transparency mechanisms without changing the semantic role defined here.

---

## 15. Corrected Controlling Chain

```text
Evidence Requirement
    -> Frozen Protocol
    -> Authoritative Campaign Key
    -> FormalRunRegistration
    -> PrecommitmentReceipt / monotonic registry
    -> subject invocation(s)
    -> complete attempt ledger
    -> RunCompletionRecord
    -> evaluator/test receipts
    -> deterministic aggregation
    -> bounded evidence receipt
    -> current trust-state check
    -> Qualification Evidence Package admission
```

---

## 16. Implementation-Readiness Ruling

With this amendment, the architecture is ready for a **lean local Evidence Integrity Conformance Protocol**.

That protocol should test the evidence machinery with deterministic fixtures only.

It SHOULD NOT require live AI behavioral generation, premium evaluators, multi-agent replication, or statistical experiments.

The first protocol should test integrity of:

- precommitment ordering;
- campaign history;
- complete attempt accounting;
- receipt-set integrity;
- evaluator/runner authority;
- claim-scope/profile binding;
- lifecycle/revocation;
- qualification-package admission.

---

## 17. Final Statement

ATE evidence now distinguishes between:

```text
"the report says this run was preregistered"
```

and:

```text
"the trust domain's authoritative ordering state proves this exact run definition was committed before any subject invocation, and all formal attempts remain visible."
```

That distinction completes the anti-selection foundation required before evidence can responsibly support agent qualification.
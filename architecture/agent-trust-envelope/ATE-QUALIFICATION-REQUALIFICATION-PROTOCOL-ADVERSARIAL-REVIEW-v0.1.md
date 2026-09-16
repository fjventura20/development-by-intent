# ATE Qualification & Requalification Protocol Adversarial Review v0.1

**Status:** Adversarial protocol review  
**Date:** 2026-09-16  
**Reviewed artifact:** `ATE-QUALIFICATION-REQUALIFICATION-LOCAL-CONFORMANCE-PROTOCOL-v0.1.md`

---

## 1. Disposition

**REVISION_REQUIRED_BEFORE_FREEZE**

The protocol is appropriately lean and deterministic, but five corrections are required before freeze.

---

## 2. QPR-1 — Compatibility Must Not Make an Old Credential Valid for a New Profile

The v0.1 test language can be read as allowing a valid compatibility declaration plus delta evidence to make the old source qualification directly valid for the target profile.

That would violate the architecture.

Correct rule:

```text
source qualification
    + compatibility decision
    + required delta evaluation
    -> new qualification decision
    -> new qualification credential for target profile
```

Compatibility reduces required evaluation scope. It does not mutate the subject/profile binding of the old credential.

Required protocol correction:

- QP-T9 must verify change-path classification and non-expansion;
- target profile must not become ACTIVE until a new qualification credential is issued;
- QP-T10 partial requalification must require a new credential and lineage to the predecessor.

---

## 3. QPR-2 — Re-attestation Boundary Must Use a Verified Runtime Context Fixture

The qualification verifier should not independently perform P2 runtime attestation in this experiment.

QP-T5 currently risks blending layers.

Required correction:

Use a deterministic `VerifiedRuntimeContext` fixture representing:

- runtime instance A under profile P;
- restarted runtime instance B under the same profile P.

The qualification layer should decide:

```text
profile unchanged -> qualification remains applicable
runtime freshness -> must be re-established by runtime-trust layer
```

Do not rerun P2 inside this protocol.

---

## 4. QPR-3 — Qualification Definition Rollback Is Not Directly Tested

The architecture protects both:

- requalification-policy rollback;
- qualification-definition supersession/rollback.

QP-T13 only tests requalification policy rollback.

Required correction:

Add mandatory QP-T13 variants for:

- old requalification-policy epoch;
- superseded Qualification Definition/version/digest after newer authoritative definition is known.

Both must fail closed.

---

## 5. QPR-4 — Waivers Are Present But Untested

The architecture permits explicit signed waivers, but the lean protocol does not test waiver safety.

To remain lean, the local protocol should freeze:

```text
waivers_permitted = false
```

and require:

```text
waiver_digests = []
```

A fixture containing an unexpected waiver should fail closed as unsupported for this protocol profile.

Waiver conformance can be tested in a later milestone if needed.

---

## 6. QPR-5 — Issuer Ceiling Test Should Include Validity Ceiling

Qualification issuer ceilings include `maximum_validity`.

QP-T11 should include a credential whose signature is valid but whose validity duration exceeds issuer authority.

Expected:

```text
REJECTED: ISSUER_CEILING
```

This proves a signing authority cannot create arbitrarily long-lived qualification simply by staying inside capability/risk fields.

---

## 7. Additional Clarifications Accepted Without Separate Test

The following should be stated in the revised protocol but need not add new controlling test IDs:

1. credential time validity is checked independently of current ACTIVE status;
2. a stale ACTIVE status does not save an expired credential;
3. status authority is itself role-authorized by frozen trust policy;
4. evidence package digest mismatch fails closed;
5. deterministic change assessment outcomes should distinguish:
   - `RE_ATTESTATION_REQUIRED`
   - `PARTIAL_REQUALIFICATION_REQUIRED`
   - `FULL_REQUALIFICATION_REQUIRED`
   - `IMMEDIATE_SUSPENSION`
6. partial/full requalification always produce a new qualification credential when qualification continues under a changed profile.

---

## 8. Accepted Protocol Structure

The following are accepted:

- local deterministic fixtures;
- no model inference;
- 15 controlling test IDs;
- evidence lifecycle testing;
- status rollback testing;
- copied credential / exact binding semantics;
- capability/risk/assurance expansion testing;
- issuer ceilings;
- evaluator independence;
- cross-project isolation;
- lineage/supersession;
- one coherent formal run;
- no premium/multi-agent evaluation.

No additional test count is required if the five corrections above are incorporated as variants/semantics in the existing 15 tests.

---

## 9. Required Revision

Produce v0.1.1 preserving 15 controlling tests while correcting:

1. compatibility -> new qualification credential semantics;
2. P2/re-attestation boundary via `VerifiedRuntimeContext` fixtures;
3. qualification-definition rollback coverage;
4. no-waiver local profile;
5. issuer maximum-validity ceiling coverage.

Then perform a final freeze review and, if clean, record the exact artifact digest as frozen.

No implementation is authorized before freeze.
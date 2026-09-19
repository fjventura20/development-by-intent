# Adversarial Review
## Formal Evidence Closure Amendment v0.1

**Status:** REVIEW COMPLETE  
**Date:** 2026-09-19  
**Artifact reviewed:** `AGENT-CONFORMANCE-LOCAL-LIFECYCLE-POC-v0.1.1-FORMAL-EVIDENCE-CLOSURE-AMENDMENT-v0.1.md`  
**Review type:** design-only, hostile evidence-validity review  
**External model calls:** none  
**Formal execution authorization:** none

---

## 1. Review Question

Does the amendment close the discovered evidence defects without weakening the
frozen Agent Conformance lifecycle claim, and is it precise enough to authorize
a bounded implementation correction later?

---

## 2. Method

The review attacked the amendment from five positions:

1. evidence producer attempting to self-certify;
2. post-run editor attempting internally consistent evidence substitution;
3. verifier receiving incomplete or ambiguous key material;
4. test suite passing without proving the frozen 18+8 obligations;
5. closure writer attempting to hide a circular or unhashed artifact.

The review also compared the amendment against the independently retrieved
dry-run bytes and the frozen design sections 20, 20A, 21, 22, 23, and 24.

---

## 3. Findings Matrix

| ID | Attack or ambiguity | Initial risk | Amendment control | Residual disposition |
|---|---|---:|---|---|
| AR-01 | Persist signatures without their public keys | Critical | Exact seven-key registry, raw key bytes, key IDs, domain allowlists | Closed for local PoC |
| AR-02 | Substitute a public key together with forged signed artifacts | High | Deterministic committed test keys, registry digest in first audit event, commit-pinned formal procedure | Bounded; production trust root explicitly out of scope |
| AR-03 | Leak fixture private keys into evidence | High | Registry forbids seeds/private bytes; verifier rejects unexpected fields | Closed if negative-tested |
| AR-04 | Reuse one key across authority roles | High | Distinct seed/public key/key ID/authority uniqueness checks | Closed |
| AR-05 | Verify a signature under the wrong artifact domain | High | Per-authority domain allowlists plus per-object domain verification | Closed |
| AR-06 | Claim 18+8 success from only `81 passed` | Critical | Exact 26-entry case accounting tied to machine-readable pytest nodes/evidence | Closed |
| AR-07 | Duplicate a case ID while omitting another | High | Exact-set and uniqueness verification | Closed |
| AR-08 | Map one pytest node to unrelated controlling cases | High | Evidence refs and assertion summaries required; verifier cross-checks mapping | Requires implementation-review scrutiny |
| AR-09 | Include a skipped/xfailed controlling test in PASS totals | High | Explicit rejection of skipped, xfailed, deselected, or missing controlling nodes | Closed |
| AR-10 | Circular RunRecord/manifest digests | Critical | Ordered five-layer closure and terminal RunRecord checksum | Closed |
| AR-11 | Leave a primary evidence file unhashed | Critical | Manifest hashes every Layer 1 file; verifier rejects missing/extra files | Closed |
| AR-12 | Modify evidence after independent verification | Critical | Final RunRecord binds manifest and verifier-report digests; terminal checksum written last | Closed |
| AR-13 | Producer writes its own independent-verification result | Critical | Separate read-only verifier process with recorded verifier commit/script hash | Closed if process boundary is tested |
| AR-14 | Verifier imports mutable producer state | High | Evidence-directory-only input; no private keys or mutable runtime access | Closed if syscall/path tests pass |
| AR-15 | Symlink/path traversal swaps evidence bytes | High | Verifier rejects symlinks and escaping paths | Closed |
| AR-16 | Duplicate JSON keys alter verifier interpretation | High | Duplicate-key rejection and canonical-value checks | Closed |
| AR-17 | Tampered ledger is changed in more than the declared location | Medium | Verifier compares authoritative/tampered copies and requires exact declared mutation | Closed |
| AR-18 | Hash chain passes but audit signatures are invalid | Critical | Public-key persistence and independent signature verification | Closed |
| AR-19 | Signed lifecycle artifacts are omitted while ledger remains valid | High | Complete signed-artifact inventory and orphan/missing-object rejection | Closed |
| AR-20 | Random keys make runs irreproducible | High | Fixed test-only Ed25519 seeds | Closed; creates new implementation baseline |
| AR-21 | Test keys are mistaken for production custody | High | Mandatory `TEST ONLY` labeling and explicit claim boundary | Closed in documentation; review public messaging |
| AR-22 | Prior invalid formal evidence is silently replaced | Critical | Preservation requirement and new run identity | Closed |
| AR-23 | Corrected runner proceeds directly to formal mode | Critical | New implementation review, new dry-run, independent verification, and PI gate required first | Closed |

---

## 4. Load-Bearing Review Results

### 4.1 Key substitution boundary

The persisted key registry makes evidence cryptographically self-verifying but
does not prove that the local test authorities deserve production trust. The
amendment states this limitation correctly. For this PoC, the external anchors
are the reviewed Git commit, deterministic fixtures, controlled execution
procedure, and durable mailbox/repository provenance.

This is sufficient for the frozen local-PoC claim and insufficient for a
production trust-root claim. No production claim is authorized.

### 4.2 Deterministic private fixtures

Committing fixed private seeds is safe only because they are explicitly public,
test-only material with no external authority. The implementation must make
accidental production import difficult: use a PoC-specific module name, loud
warnings, and tests proving each public key matches the expected key ID.

### 4.3 Case-accounting integrity

The proposed schema prevents aggregate pytest totals from substituting for the
frozen obligations. The implementation review must inspect the actual 26-case
mapping; a structurally valid mapping can still be semantically dishonest.

No implementation may auto-generate case titles or evidence references solely
from test names. The mapping must be explicit and reviewable.

### 4.4 Closure correctness

The five-layer construction is acyclic:

```text
primary evidence
  -> evidence manifest
       -> independent verification
            -> final RunRecord
                 -> detached terminal checksum
```

The final RunRecord can contain the evidence-manifest digest without requiring
the evidence manifest to hash the final RunRecord. The amendment explicitly
defines which files are primary evidence and how later closure files are
authenticated, resolving the frozen text's otherwise ambiguous circularity.

### 4.5 Producer/verifier separation

A separate process is necessary but not sufficient. If both programs share a
buggy canonicalization library, they can agree incorrectly. This local PoC may
reuse the frozen canonicalization implementation, but the independent review
must additionally recompute representative canonical hashes outside the
producer, as was done for the 2026-09-19 dry-run ledger.

The future closeout must state this shared-code limitation.

---

## 5. Required Implementation Negative Tests

The corrected verifier is not acceptable without deterministic tests proving
rejection of at least:

1. missing verification-key registry;
2. duplicate authority ID;
3. duplicate key ID;
4. public-key/key-ID mismatch;
5. unexpected private-key field;
6. wrong signing domain;
7. invalid artifact signature;
8. invalid audit signature with otherwise valid hashes;
9. missing signed artifact;
10. orphan signed artifact;
11. duplicate controlling case ID;
12. missing controlling case ID;
13. skipped or xfailed controlling test;
14. nonexistent pytest node reference;
15. evidence-manifest file missing;
16. undeclared extra primary evidence file;
17. evidence byte/size/hash mismatch;
18. broken audit previous-hash link;
19. broken payload digest;
20. causal-order inversion;
21. tampered copy with an undeclared second mutation;
22. RunRecord/manifest/verifier digest mismatch;
23. missing terminal checksum;
24. symlink or path traversal;
25. duplicate JSON key;
26. attempt to run formal mode before a reviewed dry-run gate.

All negative tests must fail closed without repairing inputs.

---

## 6. Implementation Scope Gate

The design is sufficiently precise for a later bounded implementation task,
subject to these conditions:

- frozen parent artifacts remain byte-identical;
- the deterministic test-key change creates a new implementation baseline;
- implementation changes remain within fixtures, evidence producer, independent
  verifier, and directly associated tests/status artifacts;
- exact case mapping receives human review before execution;
- no formal mode is authorized;
- the first execution is one isolated development dry-run;
- its actual evidence bytes receive independent review before any formal-run
  decision.

---

## 7. Residual Risks

The amendment intentionally does not close:

- production trust-root establishment;
- secure production private-key custody;
- compromise of the host executing both producer and verifier;
- malicious modification of the reviewed source before commit verification;
- independence from shared canonicalization code;
- remote attestation of the executing machine.

These are outside the frozen local-PoC claim and must not be implied by a PASS.

---

## 8. Review Decision

No design-level blocker remains after incorporating deterministic trust material,
complete signature verification, explicit case accounting, and the acyclic
five-layer closure.

```text
FORMAL_EVIDENCE_CLOSURE_AMENDMENT_v0.1: READY_FOR_BOUNDED_IMPLEMENTATION
FORMAL_RUN: NOT_AUTHORIZED
HERMES: NOT_REQUIRED_FOR_DESIGN_OR_REVIEW
```

Implementation still requires a separate explicit PI authorization.


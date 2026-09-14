# Trusted Governance Establishment v0.2.1

**Status:** experimental design draft (narrow correction of v0.2)
**Version:** 0.2.1
**Scope:** v0.2.1 makes ONLY the corrections required by the implementation-readiness review of v0.2. v0.2.1 does not introduce new protocol structure; it tightens the language at the four points the review identified.
**Vendor neutrality:** implementation-neutral; concrete enough to later be represented as JSON.
**Normative language:** MUST, MUST NOT, REQUIRED, SHOULD, SHOULD NOT, MAY (per RFC 2119 / VALUE-ARCHITECTURE-STANDARD-v0.2 §4).
**Author:** Hermes (research-manager-mandate-2026-08-27).
**Predecessors (preserved byte-identically):**
- v0.1: `architecture/experimental/TRUSTED-GOVERNANCE-ESTABLISHMENT-v0.1.md` (SHA-256 `937f01ad...e53b`)
- v0.1 review: `architecture/experimental/reviews/REVIEW-TRUSTED-GOVERNANCE-ESTABLISHMENT-v0.1.md` (SHA-256 `f0d7b4e0...a8351`)
- v0.2: `architecture/experimental/TRUSTED-GOVERNANCE-ESTABLISHMENT-v0.2.md` (SHA-256 `12d734cdc...76dc4`)
- v0.2 implementation-readiness review: `architecture/experimental/reviews/REVIEW-TRUSTED-GOVERNANCE-ESTABLISHMENT-v0.2-IMPLEMENTATION-READINESS.md` (SHA-256 `912a814b...5208`)

## 0. Provenance of v0.2.1

v0.2.1 makes four targeted corrections per the implementation-readiness review. Each correction is named explicitly with the rule it implements and the prose it replaces. Nothing in v0.2's other sections is changed.

| Correction | Source in review | Section in v0.2.1 |
| -- | -- | -- |
| Composition-attack closure on PCR/runtime measurement | review §3 | §B.3.3 replacement + §B.3.4 (new) |
| RFC 8785 JCS WITHOUT Unicode normalization | review §4 + PI ruling | §E.1 replacement |
| Attestation-level dimension (A0-A3) orthogonal to G-level | review §8.3 + PI ruling | §K.1 (new) and §K.2 (renamed) |
| PoC attestation-label discipline | review §2 + PI ruling | §L.0 (new) and §J.0 attestation paragraph |

## B. Participants and signing identities (v0.2.1 corrections only)

### B.3 (unchanged from v0.2)

B.3.1 / B.3.2 unchanged.

### B.3.3 (v0.2.1 replacement — composition-attack closure)

**The attested PCR measurement MUST bind to the exact runtime artifact represented by `runtime_fingerprint`.**

The runtime-resident signing key MUST be referenced inside the attestation quote (as PCR-bound data). Specifically:

B.3.3.1 The PCRs chosen for the quote MUST measure *the runtime binary whose fingerprint is claimed* AND *the signing-key handle bound to that runtime*.

B.3.3.2 The verifier MUST independently compute (or otherwise obtain) the expected PCR values from the runtime binary it observes at evaluation time. The expected PCR values are derived from `runtime_fingerprint` via a deterministic mapping (e.g., `expected_pcrs = measurement_function(runtime_binary)` where `measurement_function` is defined per attestation substrate; for a swtpm-emulated substrate, the mapping is part of the test fixture).

B.3.3.3 The verifier MUST reject any attestation quote whose PCR values disagree with the expected PCR values for the claimed `runtime_fingerprint`.

B.3.3.4 The verifier MUST additionally cross-check that the signing-key handle referenced inside the quote is the same key whose corresponding public key signed the acceptance receipt. A mismatch MUST STOP with `GX_RUNTIME_REPLACED`.

B.3.3.5 A valid attestation quote combined with a substituted runtime signing key MUST fail. The combination is the composition attack the implementation-readiness review identified; this rule forecloses it.

### B.3.4 (v0.2.1 new)

**Runtime substitution detection rule.** A runtime substitution event is signaled iff any of:

- the per-turn `runtime_fingerprint` differs from the acceptance receipt's `runtime_fingerprint`;
- the per-turn `attestation_quote_b64` does not verify under the runtime-resident public key referenced in the acceptance receipt's attestation;
- the PCR values inside the quote disagree with the expected PCR values computed from the claimed `runtime_fingerprint` (§B.3.3.3);
- the signing-key handle inside the quote does not match the acceptance receipt's signing-key handle (§B.3.3.4).

Any of these triggers STOP `GX_RUNTIME_REPLACED` (or `GX_ATTESTATION_INVALID` for the per-turn signature-verification failure).

## E. Canonicalization and signed region (v0.2.1 corrections only)

### E.1 (v0.2.1 replacement — strict RFC 8785 JCS, no Unicode normalization)

**The canonicalization procedure for v0.2.1 is strict RFC 8785 JCS WITHOUT Unicode normalization.**

E.1.0 The v0.2.1 canonicalization profile is named **v0.2.1-JCS-strict**. The normative byte-generation procedure is RFC 8785 JSON Canonicalization Scheme *exactly as specified by the RFC*. RFC 8785 preserves Unicode string data as-is and does not apply NFC, NFD, NFKC, NFKD, or any other Unicode normalization. v0.2.1 does not introduce any pre-canonicalization transformation.

E.1.1 *Number normalization:* per RFC 8785, integers are emitted in their canonical form (no leading zeros, no decimal point). Floating-point numbers use the IEEE 754 minimum-precision representation that round-trips to the identical value. Integers and floats are distinguished by their textual form (`1` vs `1.0`); they are not equivalent.

E.1.2 *Null handling:* `null` is a value. A missing field is distinct from `null`. Missing fields are omitted; `null` is emitted as the literal `null`.

E.1.3 *Array order:* arrays are arrays. RFC 8785 does not reorder array elements. v0.2.1 does not reorder arrays. The position of an element in an array is significant.

E.1.4 *Object member ordering:* object members are sorted by UTF-16 code unit order of their keys per RFC 8785 §3.1.

E.1.5 *Unicode handling:* strings are serialized as-is per RFC 8785 §3.2.2. Composed and decomposed Unicode sequences that are canonically equivalent in Unicode MUST remain distinct inputs under JCS and therefore MAY produce different canonical byte sequences and different signatures. This is deliberate. Any future version that wishes to treat canonically-equivalent Unicode sequences as identical MUST do so via a *separate pre-canonicalization data-model rule*, NOT by overriding JCS.

E.1.6 *Whitespace:* per RFC 8785 §3.2.1, insignificant whitespace is removed.

E.1.7 *Escaping:* per RFC 8785 §3.2.2.3, characters are escaped in their shortest equivalent form.

### E.5 (v0.2.1 new — normative test vectors)

The v0.2.1-JCS-strict canonicalization MUST be tested by the following 7 vectors. Signer and verifier MUST produce byte-identical canonical output for identical inputs. Composed and decomposed Unicode inputs MUST remain distinct if their underlying UTF-8 bytes differ.

**Vector 1 — Composed vs decomposed Unicode representations:**

- input A: `{"name":"café"}` where `é` is the precomposed character U+00E9 (UTF-8 bytes `0xC3 0xA9`).
- input B: `{"name":"café"}` where `é` is decomposed as U+0065 U+0301 (UTF-8 bytes `0x65 0xCC 0x81`).
- canonical output A: `{"name":"café"}` with UTF-8 bytes `0x7B 0x22 0x6E 0x61 0x6D 0x65 0x22 0x3A 0x22 0xC3 0xA9 0x22 0x7D`.
- canonical output B: `{"name":"café"}` with UTF-8 bytes `0x7B 0x22 0x6E 0x61 0x6D 0x65 0x22 0x3A 0x22 0x65 0xCC 0x81 0x22 0x7D`.
- A and B MUST produce distinct canonical bytes. A signature over input A MUST NOT verify against input B's signature.

**Vector 2 — Null vs omitted field:**

- input A: `{"a":1}` (no `b` field).
- input B: `{"a":1,"b":null}`.
- canonical output A: `{"a":1}`.
- canonical output B: `{"a":1,"b":null}`.
- A and B produce distinct canonical bytes. A signature over input A MUST NOT verify against input B's signature.

**Vector 3 — Array ordering:**

- input A: `{"xs":["b","a","c"]}`.
- canonical output A: `{"xs":["b","a","c"]}` (RFC 8785 preserves array order).
- A and B (input `{"xs":["a","b","c"]}`) produce distinct canonical bytes. Signer and verifier MUST agree on order.

**Vector 4 — Object member ordering:**

- input: `{"b":2,"a":1}`.
- canonical output: `{"a":1,"b":2}` (RFC 8785 §3.1 sorts by UTF-16 code unit).
- signer and verifier MUST produce the same sorted form.

**Vector 5 — Number serialization:**

- input A: `{"n":1}`.
- input B: `{"n":1.0}`.
- canonical output A: `{"n":1}` (integer form).
- canonical output B: `{"n":1.0}` (decimal form).
- A and B produce distinct canonical bytes. The signer MUST emit numbers in the form the verifier expects; the form is part of the signed region.

**Vector 6 — Escaped characters:**

- input A: `{"s":"a\nb"}` (literal two-character escape `\` `n`).
- canonical output A: `{"s":"a\nb"}` (RFC 8785 §3.2.2.3 shortest escape).
- input B: `{"s":"a\u000ab"}`.
- canonical output B: `{"s":"a\nb"}` (same as A after canonicalization).
- A and B produce the SAME canonical bytes. A signature over A verifies against B's canonical bytes. (This is RFC 8785's normalization of equivalent escapes.)

**Vector 7 — Unknown extension fields:**

- input: `{"a":1,"experimental":"v"}`.
- canonical output: `{"a":1,"experimental":"v"}` (preserved at canonical location; per RFC 8785 §3.1, sorted by key, so `experimental` follows `a` lexicographically).
- unknown fields are inside the signed region (§E.6 unchanged from v0.2).

### E.6 unchanged from v0.2.

## J. Proof-of-concept design (v0.2.1 corrections only — minimal structural PoC)

### J.0 (v0.2.1 replacement — minimal scope)

J.0.1 The v0.2.1 PoC is a *minimal structural PoC*. It is *not* the v0.2 §J.0.2 estimate (~1500-2500 LOC). The minimal structural PoC exercises only the propositions A-E (per the implementation-readiness review §1.1) and is constructed to be small, deterministic, and falsifiable.

J.0.2 **Target implementation size:** approximately 600-820 LOC of Python.

J.0.3 **Target infrastructure:**

- one Python process tree
- deterministic fixtures (charter, roster, envelope, receipt, swtpm-shape attestation quote)
- a verifier module
- a runtime-signing stub (no live participant)
- an issuer/RTA fixture module
- a swtpm-shape quote helper (fixture-emitted; documented as simulated)
- six deterministic cases
- zero participant invocations
- zero model calls
- zero evaluators
- no external production services

J.0.4 **Attestation-label discipline (v0.2.1 explicit).** The minimal structural PoC uses *simulated* attestation infrastructure:

- swtpm — the PoC uses fixture-shaped attestation quotes whose byte content is computed by the test fixture, NOT by an actual swtpm daemon invocation. This is documented as a Level-A1 (fixture-rooted) attestation substrate.
- manufacturer root — the "manufacturer root" is a fixture key the test code uses to validate fixture-produced quotes. It is NOT a real manufacturer-issued certificate.
- RTA key — the RTA key is a fixture key the test code uses to validate the roster. It is NOT a real RTA service.
- issuer key — the issuer key is a fixture key the test code uses to sign envelopes. It is NOT a real issuer service.

J.0.5 **Forbidden assurance claims for the minimal structural PoC.** The PoC's evidence MUST NOT be described as:

- hardware-rooted attestation
- manufacturer-backed production trust
- host-compromise resistance
- production-ready trust infrastructure

The PoC's evidence MAY be described as:

- "structural verification under a simulated attestation environment"
- "fixture-rooted attestation (A1)"
- "protocol-shape testing of governance-binding distinctions"

J.0.6 **Strongest permitted claim (final, explicit, no expansion):**

> "We demonstrated that a verifier can cryptographically distinguish a correctly constructed runtime/session governance binding from selected provenance, freshness, verifier-independence, issuer, and runtime/signing-substitution failures under a simulated attestation environment."

This claim is the maximum. It MUST NOT be expanded to imply AI-model cognition, AI-model agreement, AI-agent obedience, Value-Architecture behavior, hardware TPM security, host-compromise resistance, or production readiness.

J.0.7 **Test vectors.** The 7 canonicalization vectors in §E.5 are exercised as a separate unit-test suite. Signer and verifier MUST produce byte-identical canonical output for identical inputs. Composed and decomposed Unicode inputs MUST remain distinct.

## K. Assurance levels (v0.2.1 corrections only)

### K.0 (unchanged from v0.2)

G0-G5 ordinal assurance taxonomy, unchanged.

### K.1 (v0.2.1 new — attestation-level dimension)

**Attestation assurance is an orthogonal dimension to governance assurance.** v0.2.1 defines four attestation assurance levels (A0-A3), distinct from G0-G5.

A0 — UNVERIFIED_ATTESTATION. No attestation evidence exists, or attestation evidence fails to verify.

A1 — FIXTURE_ATTESTATION. Attestation quotes are produced by a test fixture (e.g., fixture-shape swtpm) and validated against a fixture manufacturer root. NOT hardware-rooted. NOT production-trust. The attestation substrate is simulated.

A2 — HARDWARE_ATTESTATION. Attestation quotes are produced by a hardware TPM whose endorsement key is bound to a real manufacturer root. Hardware-rooted. The verifier fetches the manufacturer root certificate independently of the participant host. DOES NOT imply host-compromise resistance beyond what a hardware TPM provides.

A3 — HARDWARE_ATTESTATION_PLUS_REMOTE_SERVICE. A2 plus a remote attestation service that independently vouches for the quote. Production-grade.

### K.2 (v0.2.1 — assurance is reported as a tuple)

**Assurance labels are reported as `Gn/Am` tuples**, where `Gn` is the governance assurance level (K.0) and `Am` is the attestation assurance level (K.1). `G` and `A` are *orthogonal*. They are NOT combined into a single numeric level via `min(G, A)`. They are independent dimensions because:

- a strong governance evidence record (G5) does not imply a strong attestation substrate (A1)
- a strong attestation substrate (A3) does not imply a strong governance evidence record (G0)

The PoC's strongest claim is therefore reported as something like `G5/A1` (the verifier-side governance checks all pass, but the attestation substrate is fixture-emulated).

### K.3 (v0.2.1 — forbidden tuple simplifications)

The following are explicitly forbidden:

- collapsing `G` and `A` into a single ordinal
- reporting a single-letter assurance label when both dimensions are not the same
- using "G5" alone to mean "G5/A3" or any other specific `A` value
- using "A3" alone to mean "G3/A3" or any other specific `G` value

A label such as `G5/A1` is a *single specific point* in a 2-D assurance space. It MUST NOT be reduced.

## L. Self-review (v0.2.1 — phase 1 gate)

The phase 1 gate required by the PI directive:

L.0 (v0.2.1 new) **PoC attestation label discipline.** v0.2.1 §J.0.4-§J.0.6 explicitly identify swtpm, manufacturer-root fixture, RTA fixture, and issuer fixture as simulated. The PoC's evidence MUST NOT claim hardware-rooted trust. PASS.

L.1-L.6 unchanged from v0.2.

### Phase 1 gate self-check

The PI directive requires a phase 1 gate check against five invariants before implementing the PoC:

- **A. No Unicode normalization is performed by the JCS canonicalization path.** PASS — §E.1.0 / §E.1.5 explicitly require strict RFC 8785 JCS without NFC, NFD, NFKC, NFKD, or any other Unicode normalization. The Unicode test vector (§E.5 vector 1) verifies this.
- **B. Runtime signing key cannot be substituted independently of the attested runtime measurement.** PASS — §B.3.3.1-§B.3.3.5 require PCR values to measure the runtime binary, require the verifier to compute expected PCR values from `runtime_fingerprint`, and require rejection on mismatch. The composition attack (valid quote + substituted runtime key) is closed by §B.3.3.5.
- **C. G and A assurance levels remain separate dimensions.** PASS — §K.1, §K.2, §K.3 define G and A as orthogonal, reported as a tuple, and forbid collapse.
- **D. swtpm evidence cannot be described as hardware-rooted.** PASS — §J.0.4-§J.0.5 forbid that description.
- **E. No production-only infrastructure remains required for the six structural propositions.** PASS — §J.0.3 enumerates only minimal test fixtures; transparency log, live RTA, live issuer, TSA, hardware TPM, evaluator, scoring, transcript linkage machinery are all deferred to production. The six cases exercise A-E propositions without them.

All five invariants pass. Phase 1 gate: `V0_2_1_READY`. Phase 2 implementation proceeds directly.

## M. Disposition

M.1 v0.2.1 disposes the implementation-readiness review's BLOCKS_POC finding (§B.3.3 composition attack) by tightening §B.3.3.1-§B.3.3.5 with PCR-measurement binding to the runtime binary.

M.2 v0.2.1 disposes the canonicalization DESIGN_HARDENING finding (review §4) by replacing §E.1 with strict RFC 8785 JCS without Unicode normalization and adding 7 normative test vectors (§E.5).

M.3 v0.2.1 adds the A0-A3 attestation assurance dimension (K.1), reports assurance as `G/A` tuples (K.2), and forbids tuple simplification (K.3).

M.4 v0.2.1 disposes the PoC attestation-label finding (review §2) by explicit §J.0.4-§J.0.5 discipline.

M.5 v0.2.1 phase 1 gate: PASS. Phase 2 implementation authorized by PI directive.

## N. Scope

N.1 v0.2.1 modifies ONLY:

- §B.3.3 (composition-attack closure)
- §B.3.4 (new — runtime substitution detection rule)
- §E.1 (canonicalization profile, strict JCS, no Unicode normalization)
- §E.5 (new — 7 normative test vectors)
- §J.0 (minimal PoC scope; attestation-label discipline)
- §K.1 (new — A0-A3 dimension)
- §K.2 (assurance tuple)
- §K.3 (new — forbidden simplifications)
- §L.0 (new — phase 1 gate attestation-label discipline)

N.2 v0.2.1 does NOT:

- modify v0.1, v0.2, or either review artifact
- introduce new protocol structure beyond the four corrections above
- remove or weaken any v0.2 rule
- claim any property the v0.2.1 PoC cannot establish under the L0/L1 attestation ceiling

N.3 Awaiting PI authorization for Phase 2 implementation.

## O. STOP-code index (v0.2.1 additions)

- `GX_RUNTIME_REPLACED` — runtime fingerprint mismatch, PCR mismatch, or signing-key handle mismatch (per §B.3.4)
- `GX_ATTESTATION_INVALID` — per-turn signature verifies under a key not bound to the original attestation

(O.1-O.16 unchanged from v0.2.)

## P. Branch state and changes

P.1 New file: `architecture/experimental/TRUSTED-GOVERNANCE-ESTABLISHMENT-v0.2.1.md`. v0.1, v0.1 review, v0.2, and v0.2 implementation-readiness review unchanged.

P.2 No other files modified by this revision.

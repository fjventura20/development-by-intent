# Implementation-Readiness and Minimization Review — Trusted Governance Establishment v0.2

**Review of:** `architecture/experimental/TRUSTED-GOVERNANCE-ESTABLISHMENT-v0.2.md`
**Reviewed SHA-256:** `12d734cdc2d65164cc5ec1c9dcded12d2128e74ee22b76bbb4686a844ab76dc4`
**Reviewed commit:** `0fdd7e39690f51df11ecab4aef83c452a073c687`
**Reviewer:** Hermes (research-manager-mandate-2026-08-27)
**Review date:** 2026-09-14
**Review posture:** *What is the smallest experiment that can falsify the essential v0.2 trust claims without building a premature production trust infrastructure?*

## 0. Headline finding

The v0.2 specification is conceptually sound for production-shaped work, but it is **not yet minimized**. The §J.0.2 cost estimate of ~1500-2500 lines and 4-8 operator-hours is over-engineered for an exploratory PoC whose purpose is *falsification*, not *deployment*. Approximately 60-70% of the proposed machinery can be replaced with deterministic fixtures, static test vectors, and shared in-process code without weakening any of the five essential propositions (A-E).

A separate, more serious finding emerged during this review: **v0.2 §B contains a subtle composition attack**. The runtime-resident signing key is bound to a TPM-attested environment by *inclusion inside the attestation quote's PCR-bound data* (per §B.3.3), but v0.2 never pins *what* is inside the quote. An adversary who controls the runtime can produce a TPM quote that names an attacker-controlled key as the runtime-resident signing key, while the runtime-resident key *actually* used to sign receipts is a different key. The verifier cannot tell because the quote doesn't pin the runtime-resident key to a runtime that has been measured.

This composition attack is **POC-blocking** in the strict sense the PI named — but it is a v0.2 wording defect, not a fundamental conceptual one. A single additional sentence in §B.3 fixes it. With that fix, plus a 60-70% minimization of the §J design, the v0.2 architecture is achievable as a small, falsifiable PoC.

**Overall disposition (see §11):** `V0_2_FIX_REQUIRED` — for one wording fix and one scope reduction.

## 1. PoC scope minimization

### 1.1 What the PoC must test (essential propositions)

| ID | Proposition | Why essential |
| -- | ----------- | ------------- |
| A | provenance-less inline governance cannot establish trusted governance | direct v0.4.4 finding; the load-bearing case |
| B | a governance acceptance can be cryptographically bound to a specific runtime/session identity | the structural mechanism that distinguishes v0.2 from v0.4.4 |
| C | an independent verifier can distinguish valid binding from substitution | this is what "verifiable" means |
| D | continuity checking can detect replacement of the bound runtime after acceptance | closes the model/runtime-swap hole |
| E | collocated/self-verification cannot support the same assurance claim as independent verification | the second-strongest case the v0.1 review identified |

Five propositions. Any minimization that loses one of A-E falsifies the PoC. Any addition that does not test A-E is gold-plating.

### 1.2 What the PoC does NOT need

In rough priority of "what can be removed without harm":

- **Transparency log (§D.8.4) — REMOVABLE.** A signed list of revisions under the RTA key suffices for the *roster* test; a transparency log tests a separate proposition (split-view detection across multiple verifiers). For an exploratory PoC with one verifier, signed-list-equals-log. Defer transparency to a later work.
- **Issuer admission process (§D.3) — REMOVABLE.** A static roster (JSON file signed by an RTA key, baked into the test fixture) tests the same proposition: a roster entry has weight iff signed. The PoC does not need to test how a roster entry got there.
- **Issuer key rotation (§D.5) — REMOVABLE.** Rotation tests a property of long-lived issuers. The PoC's issuers are ephemeral fixtures. One issuer key, no rotation.
- **Compromise handling (§D.7) — REMOVABLE.** Tests a property of long-lived issuers. Not exercised in the PoC.
- **External anchor (§H) — REPLACEABLE.** A second process running locally can be the anchor; "external" only matters relative to a host boundary, which is the same test as Case 4. The anchor's role in the PoC is to publish a signed log of observed envelopes. The PoC's local anchor process is sufficient.
- **Trust roster transparency publication (§D.8.4) — REMOVABLE.** See transparency log above.
- **Envelope nonce uniqueness across arms (§M.4.10) — REMOVABLE.** The v0.2 PoC is single-arm.
- **Cross-arm contamination STOP code (§M.4.10) — REMOVABLE.** No arms.
- **Multi-algorithm agility (§E.3) — REMOVABLE.** v0.2 already pins Ed25519 + TPM2_Quote; this is not optional infrastructure, it is the design.
- **TSA / RFC 3161 (§F Option B) — REMOVABLE.** §F Option C is sufficient (verifier-side window enforcement).
- **Algorithm agility for issuance (§E.3) — REMOVABLE.** See above.
- **Trust roster sign / verify chain (§D.3) — SIMPLIFIED to fixture.** A static signed JSON file.
- **Per-turn hash chain (§G.6) — SIMPLIFIED to per-session.** For an exploratory PoC, the binding acceptance receipt + one per-turn continuity check is sufficient. The hash chain over all 6 turns tests G.6's *proposition*; if Case 6 detects substitution on turn N, the chain property is exercised. Six turns vs. one turn tests the same proposition; six is the v0.4.4-design carryover but the *proposition* doesn't need 6.

### 1.3 What the PoC DOES need

For propositions A-E:

- **For A:** the runtime must be able to *receive* an inline charter. The verifier must classify this as `GX_PROVENANCE_MISSING`. So: a verifier with a roster check, a charter-bytes comparison check, and an acceptance-receipt validation check.
- **For B:** the runtime must be able to *receive* an envelope-bound charter and produce a signed acceptance receipt whose signature is verifiable against a key bound to the runtime.
- **For C:** the verifier must (a) verify the acceptance receipt's signature, (b) cross-check the receipt's charter reference against the envelope, and (c) distinguish a substituted receipt from a valid one.
- **For D:** the verifier must compare per-turn continuity artifacts to the acceptance receipt. At minimum: same signing key, same runtime_fingerprint.
- **For E:** the verifier running in the same process as the runtime (or sharing a host) must emit `GX_NOT_ACCEPTABLE_AS_FORMAL_EVIDENCE`. This means the verifier must check its own deployment context.

The smallest machinery: one issuer, one RTA, one verifier, one runtime. Optional: one anchor process (or anchor as a file-write).

### 1.4 Components and reduction

| v0.2 §J component | PoC role | Reduce to | LOC est. |
| -- | -- | -- | -- |
| Verifier | required | one Python module, 6 checks (A-E) | 250 |
| Runtime-side signer (acceptance receipt) | required | one Python module, signs receipt | 80 |
| Issuer | required (Case 1, 2) | one Python module, signs envelope | 100 |
| RTA | required (Case 1, 2) | one Python module + static fixture | 80 |
| Anchor (H) | optional | one Python module + JSON log file | 100 |
| Harness | required | 6-case orchestrator | 200 |
| Test fixtures (charter bytes, etc.) | required | JSON files | 50 (data only) |
| v0.4.4-derived bootstrap-and-scrub | unnecessary in PoC | n/a | 0 |
| Multi-arm freeze machinery | unnecessary in PoC | n/a | 0 |
| Transcript linkage machinery | unnecessary in PoC | n/a | 0 |
| Cross-arm contamination tests | unnecessary in PoC | n/a | 0 |
| Evaluator / scoring | unnecessary in PoC | n/a | 0 |

**Total: ~810 LOC including the harness.** That is roughly 1/3 of the v0.2 §J.0.2 estimate. The savings come from removing infrastructure for properties the PoC doesn't test (transparency, rotation, multi-arm).

The PI's stated cost target is "hundreds of lines rather than thousands". 810 LOC is on the boundary. With aggressive use of fixtures and the small-can-be-smaller posture, ~600 LOC is achievable.

## 2. TPM claim boundary

### 2.1 The cleanest separation

The v0.2 prose uses "TPM" loosely in some places. The PoC must distinguish four distinct assurance levels:

- **L0 — TPM emulator only (swtpm).** The swtpm produces quotes signed by a swtpm-resident key. The verifier can validate these quotes against a swtpm fixture's "manufacturer root" — which is a fixture. **Nothing here is hardware-rooted.** A swtpm quote is exactly as trustworthy as the swtpm binary's integrity. An attacker with access to the swtpm binary can produce valid-looking quotes.
- **L1 — TPM emulator + manufacturer root fixture.** Adds a fixed "manufacturer root" (a fixture file the verifier reads). Verifier checks the swtpm's quote under this root. **Still not hardware-rooted.** The "manufacturer root" is whatever the test wrote to disk.
- **L2 — Hardware TPM + manufacturer root certificate fetched from TPM vendor.** The TPM is hardware; the verifier obtains the vendor's real root certificate out-of-band. The verifier validates the quote. **Hardware-rooted.** A host-compromised runtime cannot produce a valid quote because the TPM's endorsement key is non-extractable.
- **L3 — Hardware TPM + manufacturer root + remote attestation service.** Adds a third-party attestation service (e.g., the TPM vendor's) that vouches for the quote. **Production-grade.**

A v0.2 PoC CAN be run at L0 or L1. It MUST be labeled as such. A PoC running at L0/L1 produces evidence described as "the verifier can detect substitution under the assumption that the TPM emulator is honest" — NOT as "hardware-rooted" or "manufacturer-attested".

### 2.2 What an emulator PoC CAN establish

A swtpm-based PoC CAN establish:

- the *protocol* works: the verifier can perform the cryptographic checks the spec describes, against a swtpm-produced quote.
- the *structural* properties of the protocol: G3 / G4 / G5 levels are achievable if the verifier's checks all pass.
- the *boundary* properties: A, C, D, E can be tested by mutating the swtpm-side or the runtime-side inputs.

### 2.3 What an emulator PoC CANNOT establish

A swtpm-based PoC CANNOT establish:

- that the host cannot be compromised (§B.7, §L.3)
- that the TPM-resident key cannot be extracted (swtpm has no such property)
- that the runtime binary on the host was actually the one that signed (a swtpm can quote any PCR state the operator produces)
- that a real attacker would not bypass the swtpm

The PoC's *falsification* power does not require these properties. The propositions A-E are about *what the verifier can detect*. A swtpm-based verifier that detects substitution still demonstrates the proposition — the failure modes that defeat swtpm are *separate* failure modes (L.3.x) that the PoC documents and acknowledges.

### 2.4 Recommended wording change

v0.2 §B.3.2 reads: *"The TPM quote MUST chain to a manufacturer root whose certificate is independently obtainable by the verifier (e.g., fetched from the TPM vendor)."*

This is fine for L2/L3. For a swtpm-based PoC, it should read: *"In a hardware-TPM deployment, the TPM quote MUST chain to a manufacturer root. In a swtpm-based deployment, the quote chains to a swtpm-emulated manufacturer root that is part of the test fixture; this is documented as L0/L1 assurance and does not carry the host-compromise-resistance properties of L2/L3."*

This wording change is a *label* fix, not a *design* fix. It is required for v0.2 to be honest about what the PoC establishes.

## 3. Participant signing key binding — composition attack

### 3.1 The attack

v0.2 §B.3.3 says: *"The TPM-resident key MUST be referenced inside the attestation quote (as PCR-bound data) so that an attacker who swaps a runtime key cannot reuse the original quote."*

The intent is correct. The wording is loose. v0.2 does not say *which* PCR or *what* the PCR measures. The attack:

1. Adversary runs a runtime on a swtpm. Runtime has a benign purpose.
2. Adversary produces a swtpm quote with PCRs reflecting *the swtpm's idle state* — a measurement the adversary fully controls.
3. Adversary uses a different runtime-resident signing key (call it `K_adv`) to sign the acceptance receipt. The verifier checks the quote against the manufacturer root: ✓.
4. The quote's "referenced key" is `K_benign`, but `K_adv` is the actual signer. The verifier has no way to know.

This is the "valid TPM quote + substituted runtime key" composition attack the PI named.

### 3.2 Why the attack works in v0.2's wording

§B.3.3 mentions "PCR-bound data" but does not specify:

- what PCR values are expected
- what measurement is reflected by those PCRs
- how the verifier validates that the PCR values are consistent with the *runtime binary actually signing*

A naive verifier, on reading v0.2, would check: (a) quote verifies under manufacturer root, (b) PCR values reflect *some* known reference state, (c) signing key referenced inside quote is the runtime's claimed key.

A strict verifier would check: (d) PCR values reflect a measurement of the *runtime binary currently running and signing*, AND (e) the signing key is bound by the runtime binary to those exact PCRs.

§B.3.3 is silent on (d) and (e). The attack exploits the gap.

### 3.3 How to fix (one sentence in v0.2)

Add to v0.2 §B.3.3:

> The PCRs used for the quote MUST measure the runtime binary AND the signing-key handle. The verifier MUST recompute the expected PCR values from the runtime binary it observes (e.g., by hash of the binary) and reject the quote if the values disagree.

Equivalently: "the PCR values referenced in the quote MUST correspond to a measurement of the runtime binary that the verifier can independently verify against the runtime binary that produced the acceptance receipt."

This is a single-sentence fix. It does not change the architecture; it tightens the spec.

### 3.4 Classification

**POC-BLOCKING** in the strict sense the PI named: *"If the current construction permits a 'valid TPM quote + substituted runtime key' composition attack, classify it as POC-blocking."* The wording permits the attack. The fix is one sentence.

### 3.5 What this means for the PoC

The PoC's verifier MUST implement (d) and (e) above. Case 6 (runtime replacement) becomes a real test of the fix:

- Acceptance receipt: signed by `K_benign`, swtpm-quote references `K_benign` with PCRs reflecting `K_benign`'s runtime.
- Turn 1: same setup, turns 2-N by an adversary-controlled runtime with key `K_adv`.
- Verifier detects: turn 2's signing key (`K_adv`) does not match the acceptance receipt's referenced key (`K_benign`). STOP `GX_RUNTIME_REPLACED`.

Without the fix, the verifier only checks (a-c); it would miss the substitution. With the fix, it catches it.

## 4. Canonicalization semantics

### 4.1 RFC 8785 JCS + UTF-8 NFC: compatibility

RFC 8785 §3.2.2 specifies JSON string canonicalization. RFC 8785 does *not* specify Unicode normalization. The implicit assumption is byte-exact UTF-8.

Adding UTF-8 NFC normalization produces canonicalized bytes that *may differ* from RFC 8785's strict output. For example:

- `"café"` (NFD: `c`, `a`, `f`, `e`, `◌́`) and `"café"` (NFC: `c`, `a`, `f`, `e`, `´`) are JSON-equivalent strings but normalize to different bytes after NFC.
- RFC 8785's strict reading treats these as different canonical strings (because the underlying UTF-8 bytes differ).
- NFC normalization collapses them to identical canonical strings.

The v0.2 §E.1.5 specification ("all string values are normalized to UTF-8 NFC before canonicalization") is therefore *not strictly RFC 8785*. It is RFC 8785 + a normalization extension.

This is not a defect — JCS implementations (e.g., canonicaljson in Python, go-jcs in Go) can choose normalization rules. But v0.2 should be honest that v0.2's canonicalization is "RFC 8785 + UTF-8 NFC" — not "RFC 8785".

### 4.2 The cleanest formulation

Recommend changing v0.2 §E.1's title from "Canonicalization rule" to "Canonicalization rule (v0.2 JCS-NFC profile)" and clarifying in §E.1.0:

> The v0.2 canonicalization is the RFC 8785 JCS procedure with the following extensions applied *before* JCS sorts keys: (1) UTF-8 NFC normalization of all string values; (2) normalization of integers to canonical decimal form; (3) treatment of missing fields as equivalent to absent fields; (4) explicit rejection of null representations distinct from empty containers.

The "exactly one normative byte-generation procedure" requirement the PI named is satisfied by naming this *one* procedure. Implementations may differ in whether they call it "JCS-NFC v0.2" or "v0.2-canon" — what matters is that the verifier and signer agree on it.

### 4.3 Test vectors

v0.2 §E should include 7 specific test vectors. Suggested:

1. **Unicode combining characters:**
   - input: `{"name": "café"}` where `é` is two code points (NFD: `e` + `◌́`)
   - canonical output: `{"name":"café"}` where `é` is one code point (NFC: `é`)
   - signature input: NFC-canonicalized
2. **Null vs omitted field:**
   - input 1: `{"a": 1}` (no `b` field)
   - input 2: `{"a": 1, "b": null}` (explicit null)
   - canonical output: identical bytes for input 1; input 2 differs and is NOT equivalent
3. **Array ordering:**
   - input: `{"xs": ["b", "a", "c"]}`
   - canonical output: `{"xs":["a","b","c"]}` (lexicographic sort)
4. **Object member ordering:**
   - input: `{"b": 2, "a": 1}`
   - canonical output: `{"a":1,"b":2}` (key sort)
5. **Integer / number representation:**
   - input 1: `{"n": 1}`
   - input 2: `{"n": 1.0}`
   - canonical output 1: `{"n":1}` (integer); canonical output 2: `{"n":1.0}` (float)
   - these are NOT equivalent (the spec must not allow both)
6. **Escaped characters:**
   - input: `{"s": "a\nb"}` (literal escape)
   - canonical output: `{"s":"a\nb"}` (canonical escape; RFC 8785 §3.2.2.3 specifies minimal escaping)
   - check: `"\u000a"` and `"\n"` are equivalent but canonical is `"\n"`
7. **Unknown extension fields:**
   - input: `{"a": 1, "experimental_field": "value"}`
   - canonical output: `{"a":1,"experimental_field":"value"}` (preserved; emitted after known fields by name)
   - signature input: canonical output (extension fields are inside the signed region per §E.6)

These vectors must be in v0.2 as normative references; the PoC verifier and signer must implement them identically. A single shared Python module (~50 LOC) implements and tests them.

### 4.4 "No implementation may normalize differently before signing and verification"

The PoC requirement: signer and verifier MUST use the same module. The simplest enforcement: one shared Python module, imported by both. Recommended.

## 5. Trusted time minimization

### 5.1 Is TSA necessary?

**No.** A swtpm-based PoC can test the freshness proposition with verifier-side window enforcement (§F Option C). The proposition is "the verifier detects stale or invalid time evidence". The proposition does not require a third-party time source — it requires that the verifier's freshness check is enforceable.

A swtpm PoC at L0/L1 does not need a TSA. v0.2 §F.2.3 (Option C) is the right choice.

### 5.2 What this means for production claims

A PoC running with Option C establishes:

- the verifier can enforce a freshness window
- a stale envelope is rejected
- the verifier's clock is the trusted clock

It does NOT establish:

- that the host clock is trustworthy (the verifier is out-of-band, so this is asserted but not directly tested)
- that the issuer's clock is trustworthy (the issuer is part of the test fixture; an attacker-supplied issuer can produce any `not_after_utc`)
- that a real attacker cannot manipulate time

For the PoC's falsification power, this is sufficient. The PoC tests the *verifier's* ability to reject stale evidence; it does not test the *issuer's* clock — but the issuer is part of the fixture, so an attack on the issuer's clock is *the PoC's* setup, not a separate test.

### 5.3 Recommended wording change

v0.2 §F.2's list of options should explicitly state that Option C is the *PoC default* and that Option A/B are deferred to production. This is a documentation fix, not a design fix.

## 6. Trust roster minimization

### 6.1 Smallest roster mechanism

For the PoC, the smallest roster is:

- a static JSON file (`roster.json`) signed by an RTA key (Ed25519)
- the roster has 1-3 entries (one valid issuer; possibly one expired issuer; possibly one revoked issuer for Cases 2 and 5)
- the verifier reads the file from disk and verifies the signature under the RTA's static public key (also a fixture)

Total cost: ~80 LOC for the RTA module + 1 JSON file.

This tests the proposition: "a roster entry is honored iff signed by the RTA and not revoked." It does not test:

- admission flow
- key rotation
- revocation list updates over time
- transparency publication

The PoC's Cases 2, 5 exercise the rejection paths (issuer not in roster, envelope expired). These exercise the *proposition* without requiring the full machinery.

### 6.2 What remains simulated

- **Issuance timestamp** is whatever the test fixture says. Not a real time authority.
- **Issuer revocation** is a static field in the roster fixture. Not a service.
- **RTA signature on roster** is computed once at test setup; the verifier validates on each test run.

### 6.3 Recommended wording change

v0.2 §D should add a "PoC substrate" subsection noting that:

- the PoC uses a static roster fixture
- the PoC's RTA is a fixture, not a service
- production deployment would require a live RTA service, transparency log, and revocation update path
- these are *production* requirements, not *PoC* requirements

This is a documentation clarification.

## 7. Six cases

### 7.1 Each case as a unit test

The PoC's six cases are best modeled as six test functions in a single test file, each constructing a different setup and asserting the expected outcome. The harness re-uses:

- the same charter bytes (Case 1, 2, 5, 6)
- the same issuer (Case 1, 5, 6)
- the same runtime (Case 1, 2, 3, 4, 5, 6)
- the same RTA (Case 1, 2)

Differences:

- Case 2: the issuer is *not* on the roster (the runtime still accepts; the verifier rejects)
- Case 3: the charter is delivered inline, no envelope
- Case 4: the verifier runs in the same process as the runtime
- Case 5: the envelope's `not_after_utc` is in the past
- Case 6: turn 2 is signed by a different runtime key than turn 1

### 7.2 Separate host boots?

**No.** The PoC tests the verifier's *cryptographic* and *structural* checks. A separate host boot would test *deployment* properties, which is a different (and later) PoC. The PoC's Cases run in one process tree.

### 7.3 Participant invocation

The PI asked: "one participant invocation only if participant behavior is actually required."

The PoC's *minimal* design uses zero participant invocations. The verifier and runtime are mocked. The runtime produces a *fixture* of an acceptance receipt; the verifier validates it. Cases 1, 2, 4, 5, 6 are testable this way.

Case 3 (inline charter) is slightly different: the proposition A is "the verifier rejects inline governance". If the *runtime* itself rejects (because its API boundary enforces "no inline charter"), that is an implementation detail. If the *verifier* rejects, that is the structural proposition. The PoC should test the *verifier's* check, which does not require a real participant.

So: **zero participant invocations** in the minimal PoC. The PoC is a *cryptographic and structural* test, not a behavioral one. This is consistent with the v0.4.4 finding (where the participant's *behavior* was the issue — and the PoC's purpose is to fix the protocol so participant behavior is no longer load-bearing).

If the PI later wants a *behavioral* PoC (one where a participant actually emits a receipt), that is a *second* PoC, not this one. It can be deferred.

## 8. Assurance claim

### 8.1 Target claim

The PI's target is approximately:

> "We demonstrated that a verifier can cryptographically distinguish a correctly constructed runtime/session governance binding from selected provenance, freshness, independence, and substitution failures."

This is exactly the right target for the minimal PoC. It is achievable at L0/L1 (swtpm) with the design above.

### 8.2 What the claim does NOT say

Per the PI:

- NOT "the model understood the governance" — never claimed; not testable without a participant
- NOT "the model will obey it" — never claimed
- NOT "the host cannot be compromised" — explicitly bounded by the L0/L1 label
- NOT "production-grade TPM assurance if an emulator was used" — explicitly bounded
- NOT "general agent trustworthiness" — out of scope

The v0.2 assurance taxonomy (G0-G5) carries these distinctions. A swtpm-based PoC that successfully passes Cases 1, 2, 3, 4, 5, 6 demonstrates the verifier-side *can* reach G5, *with the documented L0/L1 limits*. The PoC does not demonstrate the *production* reaches G5.

### 8.3 Recommendation

The v0.2 assurance taxonomy should add a sixth dimension alongside G0-G5: **A0-A3 attestation level** (L0/L1/L2/L3 from §2.1 of this review). A given evidence record is at most `min(G_level, A_level)` — the verifier-side and attestation-side ceilings are independent.

This is a one-paragraph addition to v0.2 §K.

## 9. Cost target

### 9.1 Estimated implementation

| Module | LOC | Notes |
| -- | -- | -- |
| Shared canonicalization (signer + verifier) | 80 | 7 test vectors embedded |
| Ed25519 signing/verification helpers | 30 | uses `cryptography` library |
| swtpm quote helpers | 50 | wraps `tpm2-tools` |
| Charter + envelope fixtures | 50 (data) | JSON |
| Roster fixture + RTA module | 80 | 1 JSON file + sign/verify |
| Issuer module | 100 | signs envelope |
| Runtime module (acceptance receipt signer) | 80 | signs receipt; emits turn envelopes |
| Verifier module | 250 | 6 cases as test functions + 6 verification checks |
| Harness | 200 | orchestrates the 6 cases, emits verdict |
| Anchor (optional) | 100 | writes a signed log file |
| **Total (without anchor)** | **820** | |
| **Total (with anchor)** | **920** | |

The PI's target is "hundreds of lines rather than thousands". 820-920 is at the upper end of "hundreds". With more aggressive fixture-shared code and removal of the optional anchor, ~600 is achievable. Recommend the latter for the first commit; add anchor if time permits.

### 9.2 Participant / model calls

**Zero.** The PoC is a structural test. No participant invocation. No model calls. The runtime module is a stub that produces acceptance receipts based on the envelope. The PoC tests the *verifier's* checks.

### 9.3 Production-grade infrastructure

None of the following is needed for the PoC:

- live RTA service
- transparency log
- revocation update service
- live issuer service
- external TSA
- hardware TPM (swtpm suffices at L0/L1)
- production key management

Each of these is documented as a *production* requirement in v0.2's design. The PoC tests the protocol without these.

## 10. Disposition

### 10.1 Overall disposition

**`V0_2_FIX_REQUIRED`**

v0.2's design is sound for its purpose. The PoC is over-built (×3 LOC, ×3 operator-hours). One wording fix to v0.2 §B.3.3 closes the composition attack. Once that fix lands, the minimized PoC design in §1-§9 is executable in ~820 LOC without participant invocations.

### 10.2 Required v0.2 wording fixes before PoC

Three wording fixes are required:

- **§B.3.3 (composition attack fix):** add the requirement that PCR values reflect a measurement of the runtime binary, and the verifier must verify those measurements against the runtime binary it observes. One sentence.
- **§E.1 (canonicalization profile naming):** clarify that the v0.2 canonicalization is RFC 8785 JCS *extended with* UTF-8 NFC, integer normalization, and explicit null/object/array rules. Name the profile explicitly.
- **§K (assurance taxonomy):** add an attestation-level dimension (A0-A3) alongside G0-G5; clarify that any evidence record is at most `min(G, A)`.

Two more wording fixes are *recommended*:

- **§B.3.2 (TPM root label):** clarify that swtpm-based PoCs use a fixture root and are documented as L0/L1.
- **§F.2 (TSA default):** state that Option C (verifier-side window) is the PoC default.

### 10.3 Smallest proposed component diagram

```
┌─────────────────────────────────────────────────────────────────┐
│  ONE PROCESS (PoC test runner)                                  │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │  Test harness                                             │ │
│  │  - constructs envelope + receipt fixtures                  │ │
│  │  - invokes verifier with crafted input                     │ │
│  │  - asserts expected outcome                               │ │
│  └────────────────────────────────────────────────────────────┘ │
│           │                                                     │
│           ├── Roster fixture (signed JSON, on disk)             │
│           ├── Charter fixture (signed JSON, on disk)            │
│           ├── Envelope fixtures (6 cases × signed JSON)         │
│           ├── Acceptance receipt fixtures (signed bytes)        │
│           └── swtpm quote fixtures (swtpm-emitted bytes)        │
│                                                                 │
│  Verifier module:                                               │
│  - canonicalize per v0.2 §E.1                                   │
│  - verify Ed25519 signatures                                    │
│  - verify swtpm quote against fixture root                      │
│  - check freshness (Option C window)                            │
│  - check continuity (per-turn)                                  │
│  - check roster (signed JSON)                                   │
│  - check provenance (envelope vs inline)                        │
│  - check collocation (process boundary)                         │
└─────────────────────────────────────────────────────────────────┘
```

No external services. No second host. No participant. One Python entrypoint.

### 10.4 Properties: real vs. simulated

- **REAL:** canonicalization (with test vectors), Ed25519 sign/verify, signature-key continuity checking, freshness window enforcement, roster verification under RTA signature, provenance distinction (envelope vs inline), collocation detection (in-process).
- **SIMULATED:** TPM-emitted attestation (swtpm, not hardware); RTA's roster signing (test fixture); issuer's signing key (test fixture); runtime binary's PCR measurement (computed from the fixture, not from a real OS measurement); the participant model (zero participant invocations; runtime is a stub).
- **NOT TESTED:** host compromise resistance (L.3.1-3); hardware-rooted attestation (L.2-L.3); live RTA service; transparency log; production revocation; emergency PI override (deferred to v0.3).

### 10.5 Exact falsification criteria

The PoC is successful iff all of:

- Case 1: the verifier reaches G5 against the L0/L1 attestation ceiling.
- Case 2: the verifier emits `GX_ISSUER_UNAUTHORIZED`; evidence record's G-level is G0.
- Case 3: the verifier emits `GX_PROVENANCE_MISSING`; the runtime's behavior is irrelevant (no participant invocation).
- Case 4: the verifier emits `GX_NOT_ACCEPTABLE_AS_FORMAL_EVIDENCE`; the verifier does not falsely claim G5.
- Case 5: the verifier emits `GX_AUTH_EXPIRED`; freshness window enforced.
- Case 6: the verifier emits `GX_RUNTIME_REPLACED` on the substitution turn.

The PoC is FALSIFIED iff:

- any case produces a wrong verdict, OR
- the canonicalization tests fail to be deterministic across signer/verifier, OR
- the swtpm's "manufacturer root" can be substituted without detection (a separate test), OR
- the v0.2 §B.3.3 composition attack (Case 6 with crafted swtpm quote + crafted runtime key) succeeds.

### 10.6 Files changed

This review creates exactly one file: `architecture/experimental/reviews/REVIEW-TRUSTED-GOVERNANCE-ESTABLISHMENT-v0.2-IMPLEMENTATION-READINESS.md`.

v0.1 (SHA-256 `937f01ad...e53b`), v0.1 review (`f0d7b4e0...a8351`), and v0.2 (`12d734cdc...76dc4`) are preserved byte-identically.

## 11. Recommendation

Run the PoC at L0/L1 with the §10.1 wording fix to v0.2 §B.3.3 in place. Total implementation cost: ~820 LOC, no participant invocations, ~1-2 hours of one operator's time on a Linux host with `swtpm` installed. The PoC falsifies (or fails to falsify) the five essential propositions A-E. Production deployment is a separate later PoC at L2/L3.

The PI's stated target claim is achievable under this design: *"a verifier can cryptographically distinguish a correctly constructed runtime/session governance binding from selected provenance, freshness, independence, and substitution failures."*

STOP. Awaiting PI direction.

# Trusted Governance Establishment v0.2

**Status:** experimental design draft (revision of v0.1 after adversarial review)
**Version:** 0.2
**Scope:** resolves only the structural deficiencies identified in
`architecture/experimental/reviews/REVIEW-TRUSTED-GOVERNANCE-ESTABLISHMENT-v0.1.md`
that block a defensible proof-of-concept.
**Vendor neutrality:** implementation-neutral; concrete enough to later be represented as JSON.
**Normative language:** MUST, MUST NOT, REQUIRED, SHOULD, SHOULD NOT, MAY (per RFC 2119 / VALUE-ARCHITECTURE-STANDARD-v0.2 §4).
**Author:** Hermes (research-manager-mandate-2026-08-27).
**Predecessor:** v0.1 (`architecture/experimental/TRUSTED-GOVERNANCE-ESTABLISHMENT-v0.1.md`, preserved byte-identically).
**Predecessor's adversarial review:** `architecture/experimental/reviews/REVIEW-TRUSTED-GOVERNANCE-ESTABLISHMENT-v0.1.md`, preserved byte-identically.

## 0. Provenance of this revision

This version addresses only the BLOCKS_POC and MUST_FIX_BEFORE_FORMAL_EVIDENCE findings of the v0.1 review. The v0.1 prose is *not* modified; that document is preserved unchanged. v0.2 is a complete re-statement of §3-§6 with the corrections explicitly inserted at the points where the reviewer's BLOCKS_POC findings sit. v0.2 additionally introduces an *Assurance Level taxonomy* (G0-G5) and *Participants*, *Time*, *Audit Anchoring*, *Continuity* sections that did not exist in v0.1.

Five overclaims identified by the v0.1 review are corrected or qualified. A sixth distinction — *"the protocol establishes evidence that governance binding occurred; it does not by itself establish that the agent will behave according to that governance"* — is added.

### v0.1 review → v0.2 changes (summary index)

- Review §1.1 (participant signing primitive, BLOCKS_POC) → v0.2 §B
- Review §1.2 (trust roster governance, MUST_FIX_BEFORE_FORMAL_EVIDENCE) → v0.2 §D
- Review §1.3 (canonicalization and signed-region semantics, DESIGN_HARDENING) → v0.2 §E
- Review §2.4 (clock/time-source trust, BLOCKS_POC) → v0.2 §F
- Review §2.8, §2.9 (session substitution / runtime replacement, DESIGN_HARDENING) → v0.2 §G
- Review §2.10 (host compromise independence, BLOCKS_POC) → v0.2 §C
- Review §2.11 (audit-chain anchoring, DESIGN_HARDENING) → v0.2 §H
- Review §2.12 (PI/emergency override) → v0.2 §K (open question)
- Review §2.13 (cross-arm contamination) → v0.2 §K (open question)
- Review §3 (5 overclaims) → v0.2 §I (claim corrections)
- Review §8 (PoC, only 3 cases) → v0.2 §J (6 cases)
- Implicit "agent behaves per governance" claim → v0.2 §I.6 (sixth distinction)

### Claims deliberately weakened from v0.1

- "Explicit acceptance is what the participant agreed to" → re-phrased as "the acceptance receipt is signed by a runtime-resident key bound to an attested runtime; the receipt evidences that *that runtime* accepted for the session identified, not that the model intrinsically authorized acceptance."
- "The audit chain can be re-verified after execution" → re-phrased: "the audit chain can be independently re-verified after execution only if externally anchored; otherwise it is only locally tamper-evident."
- "Replay cannot succeed because of the freshness nonce" → re-phrased: "replay can be detected only if the verifier checks the rejection log; freshness alone does not by itself prevent replay."
- "Session substitution is impossible because the session id is from the verified CLI footer" → re-phrased as conditional and split into "out-of-session" vs "mid-session"; mid-session addressed by §G.
- "The trust chain is independently verifiable" → conditional on the verifier being out-of-band (v0.2 §C); PoC Cases 4-6 confirm.

## A. Assumptions and terminology

A.1 *Trust claim* — a statement asserting that an event, identity, or constraint holds and is provable from evidence.

A.2 *Signer* — an entity possessing a private signing key and the ability to produce a signature over specified bytes.

A.3 *Verifier* — an entity that consumes evidence artifacts and produces a verdict (PASS / STOP / NOT_ACCEPTABLE_AS_FORMAL_EVIDENCE) under one or more trust claims.

A.4 *Out-of-band* — operating in a trust domain not under the authority of the participant host. Out-of-band implies distinct machine identity, distinct trust root, distinct human operator, OR an HSM/TPM-attested separation.

A.5 *External anchor* — a third-party service or signed-log to which evidence artifacts are transmitted for tamper-evident publication, without whose cooperation an attacker with operator privilege cannot produce a consistent alternative history.

## B. Participants and signing identities

B.1 **Five distinct identities MUST be kept separate.** v0.1 conflated them. v0.2 names them and what each contributes:

B.1.1 **Model identity** — identifies the model (weights + tokenizer + config) being executed. Examples: `MiniMax-M3`, `gpt-5.6`, `claude-opus-4-7`. By itself, this identity carries no signing capability.

B.1.2 **Runtime identity** — identifies the agent runtime that *hosts* the model and is responsible for emitting output bytes. Examples: a Hermes-runtime instance with a particular version, deployment fingerprint, and configuration-hash.

B.1.3 **Host identity** — identifies the OS / VM / hardware on which the runtime executes. Examples: a particular Linux host with a particular TPM Endorsement Key fingerprint and a particular TCB measurement set.

B.1.4 **Session identity** — identifies a particular conversation / turn sequence within a runtime. Examples: a Hermes CLI footer session id `20260914_061915_b69d5b`.

B.1.5 **Participant signing identity** — a keypair held by the runtime (or a sub-process of the runtime acting on its behalf) that signs acceptance and continuation evidence. Bound to the runtime via a remote attestation quote. **NOT** held by the model.

B.2 **Models MUST NOT be claimed to possess signing keys.** Model weights carry no private key. Any signature that is verifiable must have been produced by *something other than the model*. Specifically, the participant signature MUST be produced by the runtime-resident key (B.1.5) acting on bytes emitted by the runtime's output boundary, *not* by the model internally.

B.3 **The runtime-resident signing key MUST be bound to an attested environment.** Concretely:

B.3.1 The runtime SHALL hold (or have access to) a TPM-resident key whose public component can be presented to a verifier alongside an attestation quote signed by the TPM.

B.3.2 The TPM quote MUST chain to a manufacturer root whose certificate is independently obtainable by the verifier (e.g., fetched from the TPM vendor).

B.3.3 The runtime-resident key MUST be referenced inside the attestation quote (as PCR-bound data) so that an attacker who swaps a runtime key cannot reuse the original quote.

B.4 **The acceptance receipt is signed by the runtime-resident key, not the model.** Concretely:

B.4.1 The runtime signs the canonicalized acceptance receipt at the moment of emission.

B.4.2 The verifier separately re-verifies the signing key against the TPM quote attached to the receipt.

B.4.3 The receipt MUST contain, at minimum:

- `charter_id` and `charter_sha256` (from the accepted charter)
- `session_id` (verified CLI footer channel; B.1.4)
- `runtime_fingerprint` = a deterministic digest of {runtime binary, version, config-hash, deployment-salt}
- `attestation_quote_b64` = the TPM quote over the signing-key handle + the receipt canonicalized bytes
- `nonce_freshness` (per §J)
- `accepted_at_utc_verified` (per §F)

B.5 **Detecting runtime replacement after acceptance.** Concretely:

B.5.1 Each governed turn MUST carry a `turn_envelope` whose `runtime_fingerprint` and `attestation_quote_b64` match the acceptance receipt.

B.5.2 A turn whose `runtime_fingerprint` differs from the acceptance's `runtime_fingerprint` MUST STOP with `GX_RUNTIME_REPLACED`.

B.5.3 A turn whose attestation quote no longer verifies against the runtime-resident public key MUST STOP with `GX_ATTESTATION_INVALID`.

B.6 **Assurance boundary clarification.** The v0.1 review identified this as the load-bearing ambiguity. **The following distinction MUST be preserved in any v0.2-aligned prose**:

> RUNTIME-BOUND GOVERNANCE ACCEPTANCE is the assurance that an *attested runtime process*, on an attested host, with a verified signing key, signed an acceptance receipt over an authenticated envelope for a given session.
>
> This is NOT equivalent to MODEL-INTRINSIC CRYPTOGRAPHIC ACCEPTANCE — the property that the model itself holds and controls a private key and *chose* to accept because of reasoning internal to the model.
>
> Future mechanisms MAY establish MODEL-INTRINSIC acceptance (e.g., model-side commitment protocols, on-chain model weights with verifiable signing). v0.2 does not require this and MUST NOT be claimed as established.

B.7 **Host compromise caveat.** A compromised host can produce forged runtime signatures and forged attestation quotes. v0.2 does not solve host compromise; it accepts §C's requirement that the *formal verifier* be outside the participant host trust boundary. A PoC whose verifier and participant share a host is *not formally testable* under v0.2.

## C. Out-of-band verification

C.1 **Formal trust verification MUST occur using a verifier outside the participant host trust boundary.**

C.1.1 A host is "in the participant trust boundary" if it can either (a) produce a signature that is intended to be accepted as the participant's, OR (b) modify the bytes the runtime emits, OR (c) substitute the runtime's output channels, OR (d) modify what the runtime sees as input.

C.1.2 A verifier is "out-of-band" if it satisfies all of:

- distinct machine identity
- distinct trust root
- distinct human operator OR a hardware-enforced separation (TPM/HSM)
- ability to obtain the trust roster (D) without going through the participant host

C.2 **What constitutes sufficiently independent verification.** The verifier:

- obtains the trust roster (D) independently of the participant host
- obtains the canonicalization and signing-region specification (E) prior to evidence evaluation
- verifies each signature against the relevant public key without trusting the participant host's libraries
- checks the rejection / revocation log independently

C.3 **A participant host MUST NOT be able to generate, validate, and declare its own trust evidence sufficient for formal evidence.** Self-validation by the participant host is permitted only as a *best-effort local check* — it is not formal evidence.

C.4 **STOP code for collocation:** `GX_NOT_ACCEPTABLE_AS_FORMAL_EVIDENCE`. This is NOT a verdict on the trust claim; it is a verdict on the *evidentiary method*. The PoC Cases 4-6 (J.4-J.6) exercise this code.

## D. Trust root and issuer roster governance

D.1 **A configurable trust anchor is an external policy assumption.** v0.2 does not recursively prove the trust root — that would produce an infinite regress. The trust anchor in v0.2 is a non-recursive **external policy assumption**:

- the verifier operator declares, in a verifiable way, *what root it accepts*
- examples: a particular EV TLS certificate; a particular manufacturer TPM root; a particular DNSSEC-anchored key
- the policy itself is auditable; the policy choice is an operator decision outside the protocol

The protocol's responsibility is to make this assumption *explicit and replaceable*, not to prove it. v0.2 MUST therefore document the assumption in the envelope and audit trail.

D.2 **Root-of-trust authority.** A root-of-trust authority (RTA) is the entity whose key is the configured trust anchor. In v0.2 the RTA's role is exclusively:

D.2.1 sign issuer-admission records when admitting an issuer to the trust roster (D.3)

D.2.2 sign trust-roster revisions (D.5)

D.2.3 sign revocation records (D.6)

The RTA does not have authority to bind specific agents to specific charters. **The RTA is structurally distinct from an issuer.** This separation prevents a single key from serving both roster management and governance binding, which would otherwise create a confusion-of-roles attack.

D.3 **Issuer admission process.** A prospective issuer MUST provide:

D.3.1 a signed admission record containing `issuer_id`, `issuer_public_key`, `charter_type_scope` (which charter types the issuer is authorized to bind), `valid_from_utc`, `valid_until_utc`, and an `admission_signature` by the RTA over the canonicalized record

D.3.2 the verifier MUST verify the admission signature against the RTA's configured public key

D.4 **Issuer key registration.** An admitted issuer's `issuer_public_key` is registered through the admission record (D.3.1). Key rotation requires a *new* admission record referencing the new key and superseding the previous one.

D.5 **Key rotation.**

D.5.1 Issuer keys MUST be rotated at the issuer's declared cadence (SHOULD at least annually).

D.5.2 The previous key MUST continue to verify envelopes whose `not_after_utc` predates the rotation.

D.5.3 The new key MUST NOT be used to re-sign historical envelopes (no retroactive re-signing).

D.6 **Revocation.** The RTA publishes a signed revocation list, periodically and on demand. The list contains:

D.6.1 `issuer_id` of revoked issuers

D.6.2 `envelope_nonce` of revoked envelopes (specific envelopes may be revoked without revoking their issuer)

D.6.3 revocation timestamp

D.6.4 RTA signature

D.7 **Compromise handling.** A compromised issuer key requires:

D.7.1 immediate publication of an RTA-signed revocation record identifying the compromised issuer and the time-of-compromise-known bound

D.7.2 envelope validity windows (`not_after_utc` <= time-of-compromise-known) on envelopes issued before the bound time

D.7.3 envelopes with `not_after_utc` > time-of-compromise-known MUST be treated as compromised

D.8 **Trust roster publication.** The roster is published as a signed Merkle tree (or signed revision list) by the RTA. Each revision:

D.8.1 contains a sequence number

D.8.2 hashes the previous revision's root (hash chain)

D.8.3 is signed by the RTA's key

D.8.4 SHOULD be published to a transparency log (e.g., certificate-transparency-style) so the verifier can detect split-view or stale-view attacks

D.9 **Freshness requirements.** The verifier MUST check that the observed roster revision is no older than `R_freshness_max = 86400` seconds (24 hours) at evaluation time. v0.2's default. Shorter or longer is permissible via operator policy.

D.10 **Fail-closed behavior when roster cannot be verified.** If the verifier cannot obtain a recent, valid roster revision:

D.10.1 the verifier MUST treat any envelope referencing an unverifiable issuer as REJECTED

D.10.2 the verifier MUST emit `GX_TRUST_ROSTER_UNAVAILABLE`

D.10.3 the operator's run proceeds only after the operator overrides the failure with a documented, time-bounded exception (operator-side; not protocol-side)

D.11 **Avoiding infinite authority regress.** v0.2 *does not recursively prove* the trust anchor. The anchor is an operator policy choice (§D.1). What the protocol does:

D.11.1 makes the assumption explicit in each artifact

D.11.2 makes the assumption auditable after the fact

D.11.3 requires revocation and rotation flows so a wrong anchor can be rotated out

This is the entire anti-regress mechanism. There is no deeper layer.

## E. Canonicalization and signed region

E.1 **Canonicalization rule.** All canonicalizations in v0.2 MUST use RFC 8785 JCS (JSON Canonicalization Scheme) augmented with the following explicit rules:

E.1.1 *Number normalization:* integers are emitted without decimal points; floats are emitted with the minimum-precision representation that round-trips back to the identical IEEE 754 value.

E.1.2 *Null handling:* `null` is explicit. A missing field and a `null` value are NOT equivalent. Missing fields MUST be omitted (not set to null).

E.1.3 *Array order:* arrays are ordered sets by canonical content: deterministic ordering by lexicographic comparison of the canonicalized element bytes.

E.1.4 *Empty containers:* empty object and empty array are represented as `{}` and `[]` respectively; not as `null`, not omitted.

E.1.5 *UTF-8 NFC normalization:* all string values are normalized to UTF-8 NFC before canonicalization.

E.1.6 *No comments, no whitespace beyond what JCS permits.*

E.2 **Signed region.** v0.2 makes the signed region of each signature explicit. Three signatures exist:

E.2.1 `charter_issuer_signature_b64` covers:

```
canonicalize({
  charter_id,
  charter_sha256,
  charter_canonical_bytes_b64,
  issuer_id,
  not_before_utc,
  not_after_utc,
  scope,
  // EXCLUDED: charter_issuer_signature_b64 itself
})
```

E.2.2 `envelope_issuer_signature_b64` (when the issuer signs the whole envelope) covers:

```
canonicalize({
  envelope_id,
  envelope_version,
  issuer,
  charter,
  binding,
  // EXCLUDED: envelope_issuer_signature_b64 itself,
  //           acceptance_receipt (if present)
})
```

E.2.3 `acceptance_receipt_signature_b64` covers:

```
canonicalize({
  receipt_id,
  charter_id,
  charter_sha256,
  session_id,
  runtime_fingerprint,
  attestation_quote_b64,
  nonce_freshness,
  accepted_at_utc_verified,
  receipt_issuer_signature_chain_b64, // links to envelope_issuer_signature_b64
  // EXCLUDED: acceptance_receipt_signature_b64 itself
})
```

E.3 **Algorithm identifiers.** v0.2 pins exactly two signature algorithms:

E.3.1 `sig_alg = Ed25519` (RFC 8032) — for all v0.2 signatures

E.3.2 `quote_alg = TPM2_Quote` (TCG TPM 2.0) — for attestation quotes

E.3.3 Any envelope whose `signature_algorithm` is not one of the two above MUST be rejected.

E.3.4 Algorithm agility and downgrade resistance: by pinning exactly one algorithm, v0.2 defeats downgrade by construction. Future versions MAY broaden; this is a v0.2 lock.

E.4 **Versioning.**

E.4.1 `envelope_version = "TGE/0.2"` MUST be the first field emitted by canonicalization.

E.4.2 A verifier MUST reject any envelope whose version is unknown.

E.4.3 Unknown fields in the envelope MUST be preserved during canonicalization and emitted at canonical location (after known fields, lexicographic by name). The verifier MUST emit `GX_UNKNOWN_FIELD_PRESENT` for diagnostics but MUST NOT reject solely on this basis (extensions are anticipated).

E.5 **Mutation, ambiguity, partial-signature, downgrade, and replay attacks.** E.1 + E.2 + E.3 + E.4 collectively defeat:

E.5.1 *mutation* — JCS canonicalization fixes byte-level representation; signature covers the canonicalized bytes
E.5.2 *ambiguity* — explicit null/array/object rules eliminate equivalent-representation exploits
E.5.3 *partial-signature* — explicit signed regions per E.2
E.5.4 *downgrade* — algorithm pinning per E.3
E.5.5 *replay* — addressed by §J.5 (rejection log) and §F (verified time)

E.6 **Extensions.** Extensions are permitted but MUST be inside the envelope and MUST NOT alter the signed regions (§E.2). An extension that requires modification of signed regions constitutes a *new version* and MUST be rejected by v0.2 verifiers.

## F. Trusted time

F.1 **Participant-host wall-clock time MUST NOT be used for evidence validity.** The participant host clock is operator-controlled and therefore triviallly forgeable.

F.2 **External trusted-time mechanism.** v0.2 requires an external trusted-time channel:

F.2.1 **Option A — Verifier-counter-signed challenge/response.** The verifier issues a nonce-bearing challenge to the runtime; the runtime's response includes a TPM-attested timestamp. The verifier independently stamps its own received-time on the response.

F.2.2 **Option B — Independent TSA.** The verifier obtains an RFC 3161 timestamp token from a trusted TSA whose certificate chains to a configured root.

F.2.3 **Option C — Verifier-side window enforcement.** The verifier accepts an envelope only if `(verifier_now - envelope.issuer_valid_until) < envelope_window_tolerance`. This bounds the host-clock manipulation window to the operator-tunable `envelope_window_tolerance`.

v0.2 PoC SHOULD implement **Option C** with a default tolerance of 60 seconds. Option A requires TPM and a verifier-side service; Option B requires a TSA. Option C requires only a verifier clock, which the verifier's host clock is sufficient for *provided the verifier is out-of-band (§C)*.

F.3 **Clock-skew handling.** The verifier MUST apply a clock-skew tolerance `skew_tolerance_seconds` (default: 30). Skew larger than tolerance MUST be resolved by failing closed (`GX_TIME_UNCERTAIN`).

F.4 **Failure semantics.** Time-source failure MUST produce `GX_TIME_UNCERTAIN`, treated as a STOP. The verifier MUST NOT bypass this check.

F.5 **Timestamps are not the same as evidence.** A trusted timestamp guarantees only that *an event occurred within a window*. It does not authenticate *who* did the event. Trust-time and trust-identity are orthogonal.

## G. Runtime continuity

G.1 **Normative continuity rule.** Between acceptance and the end of governed execution, the runtime-resident signing key, the runtime binary fingerprint, and the session identity MUST all be observable as continuous. v0.2 imposes this with three checks per turn:

G.1.1 Each emitted `turn_envelope` MUST contain `runtime_fingerprint`, `attestation_quote_b64`, and `session_id`.

G.1.2 The verifier MUST check that `runtime_fingerprint` and `attestation_quote_b64` MATCH the acceptance receipt (modulo a *renewed* TPM quote, which is permitted under §G.4).

G.1.3 A mismatch triggers `GX_RUNTIME_REPLACED` (signature-key change) or `GX_ATTESTATION_INVALID` (signature verifies under a key not bound to the original attestation).

G.2 **Detection of signing-key replacement.** Per B.5.2, a different `runtime_fingerprint` is a STOP condition. Per B.5.3, an attestation quote that no longer verifies under the original TPM-bound key is a STOP condition.

G.3 **Detection of session substitution.** Per B.5.x and §H/J.6. Session identity is bound to a specific CLI footer id; any `turn_envelope` whose `session_id` differs from the bound session MUST STOP with `GX_SESSION_SUBSTITUTION`.

G.4 **TPM quote renewal.** Within a single continuous runtime, the TPM is permitted to *renew* its quote (PCRs may change with normal operation). Renewed quotes MUST:

G.4.1 chain to the original quote (chain to the original PCR values and key handle)

G.4.2 be signed by the same TPM-bound key

G.4.3 NOT change the `runtime_fingerprint`

G.5 **Continuity check cadence.** v0.2 requires per-turn continuity checking. Per-turn is selected because:

G.5.1 per-session permits a session-long attacker window

G.5.2 critical-transition-only (e.g., once at start of each task) is too coarse

G.5.3 per-turn produces a complete, individually-verifiable chain

G.6 **Continuous attestation record.** Each turn's `turn_envelope` MUST be hash-chained to the prior turn's envelope. The hash chain includes `previous_turn_envelope_sha256` as a field. This permits audit re-verification independent of the runtime.

## H. Audit evidence anchoring

H.1 **Evidence categories distinguished.** v0.2 distinguishes three levels of auditability:

H.1.1 *Locally hash-chained evidence* — the runtime produces a chain of turn envelopes whose hashes chain together. Detects tampering *within* the runtime. DOES NOT detect operator forgery by the operator running the runtime (the operator can re-emit a consistent chain).

H.1.2 *Externally anchored evidence* — the runtime transmits turn envelopes (or batched digest receipts) to an external anchor outside the participant host trust boundary. The anchor publishes its observations as a signed log. Detects operator forgery *for envelopes observed after the anchor is brought online*. DOES NOT retroactively protect envelopes observed before the anchor saw them.

H.1.3 *Independently verifiable evidence* — the verifier can re-run an audit entirely from the anchored artifacts plus the canonicalization rules, without trusting the participant host's claim that the artifacts are complete. Combines: external anchoring + cross-validation by a second verifier + signed manifests.

H.2 **Post-execution re-verifiability requires H.1.3, not merely H.1.1 or H.1.2.** v0.2's claim is conservatively stated: locally hash-chained evidence is tamper-evident against insider-without-operator; externally-anchored evidence additionally defends against the operator; independently verifiable evidence additionally defends against an operator or co-located verifier with shared trust boundary.

H.3 **External anchor specification.** v0.2 names the anchor:

H.3.1 the anchor MUST be out-of-band per §C

H.3.2 the anchor MUST publish signed log entries whose hashes chain per §G.6

H.3.3 the anchor SHOULD publish signed Merkle roots (STH-style) at fixed intervals

H.3.4 the anchor MUST reject and log any envelope whose signed region does not verify

H.4 **Acceptance-not-acceptance.** v0.2 does NOT assert that anchor publication is equivalent to "the participant accepted". It asserts only:

H.4.1 the anchor observed a signed acceptance receipt

H.4.2 the signature is verifiable

H.4.3 the runtime's attested identity is the signer

Whether *the agent will behave per the governance* is a separate question (§I.6).

## I. Claim corrections

I.1 v0.1 implied "Explicit acceptance is what the participant agreed to." v0.2 corrects: "Explicit acceptance, as v0.2 establishes it, is the existence of a structured acceptance receipt signed by a runtime-resident key bound to a TPM-attested runtime, over a canonicalized envelope whose signature verifies against an admitted issuer. The receipt evidences that *that runtime*, on *that host*, for *that session*, with *that signing key*, acknowledged governance binding. It does not establish that the model inside the runtime was persuaded, comprehended, or would behave accordingly. Model-intrinsic acceptance is a stronger property v0.2 does not claim."

I.2 v0.1 implied "The audit chain can be re-verified after execution." v0.2 corrects: "The audit chain can be *tamper-evident after execution* if locally hashed (§H.1.1); it can be *anchored and tamper-detected* if externally hashed (§H.1.2); it is *independently verifiable* only if the verifier can re-run an audit from anchored artifacts alone (§H.1.3). Post-execution re-verifiability requires §H.1.3, not merely §H.1.1 or §H.1.2."

I.3 v0.1 implied "Replay cannot succeed because of the freshness nonce." v0.2 corrects: "Replay is prevented if the verifier (a) checks that the envelope nonce is not on a published revocation list (§D.6, §J.5) AND (b) checks that the acceptance receipt nonce is not on a separate acceptance-replay log maintained by the runtime (§J.5). Freshness alone does not suffice. Out-of-band revocation log query is required."

I.4 v0.1 implied "Session substitution is impossible because the session id is from the verified CLI footer." v0.2 corrects: "Session substitution *from outside the runtime* is detected by the verified CLI footer binding (§B.5.x). Mid-session substitution *within the runtime* (model or runtime swap) is detected by per-turn runtime_fingerprint continuity (§G.1) and TPM-attestation quote continuity (§B.5.3)."

I.5 v0.1 implied "The trust chain is independently verifiable." v0.2 corrects: "The trust chain is independently verifiable *if the formal verifier is out-of-band of the participant host trust boundary (§C)*. If verifier and participant share a host, the verifiability claim is reduced to *locally hash-chained*, not independently verifiable (§C.4, PoC Case 4)."

I.6 **Sixth distinction (newly added in v0.2):** *"The protocol establishes evidence that governance binding occurred. It does not by itself establish that the agent will behave according to that governance."* Concretely:

I.6.1 what the protocol DOES establish: that a defined event happened (binding accepted; turns executed under binding) and that the evidence meets v0.2's structural requirements

I.6.2 what the protocol DOES NOT establish: that future turns will continue to be governed, that the model is persuaded, that the runtime is a faithful proxy for the model, or that governance binding causally produces governance-conforming behavior

I.6.3 a v0.2-aligned PoC is therefore a test of *binding establishment*, not a test of *governance behavior*. Conflating these is a category error and should be flagged by §J.6.

I.7 The §I corrections do not weaken v0.2 — they accurately state what v0.2 actually establishes. v0.1 overstated.

## J. Proof-of-concept design (6 cases; DESIGN ONLY, NOT EXECUTED)

J.0 **General.** Each case is *designed* but *not executed*. Cases 4-6 are required to demonstrate the boundary conditions the v0.1 review identified. Cases 1, 2, and 3 are the v0.1 cases preserved with v0.2 corrections.

J.0.1 PoC infrastructure assumptions:

- a verifier implementation: out-of-band per §C.1.2
- a runtime implementation: signs acceptance receipts using TPM-bound Ed25519
- an issuer implementation: signs envelopes using Ed25519; chain anchors RTA-signed roster
- an RTA implementation: signs roster revisions and revocation records
- an anchor implementation: receives turn envelopes, publishes signed log
- a charter fixture: the v0.1 Condition of Agency charter as canonical bytes
- each case uses the same charter fixture; only the surrounding trust claims differ

J.0.2 PoC cost estimate:

- code implementation: ~1500-2500 lines (verifier ~600, runtime-side signing ~200, issuer ~300, RTA ~200, anchor ~200, harness ~200)
- testing infrastructure: TPM emulator (swtpm) for the host dev environment; manufacturer root fixture
- operator-hours to run all 6 cases end-to-end: approximately 4-8 hours of one operator's time, plus ~30 minutes of fresh host boot per case
- PoC budget acceptable for a research artifact; not for production

J.0.3 Participant requirements:

- a Linux host with TPM 2.0 (real hardware or swtpm)
- the Hermes runtime in a v0.2-aligned configuration
- a separate verifier host (out-of-band)
- an RTA host (small service)

### Case 1 — Valid trusted-governance establishment, fully specified

J.1.1 **Setup.** Operator:

- runs RTA which admits an issuer with a key, signs admission record
- issuer creates an envelope over the charter with `not_before_utc = now - 60s` and `not_after_utc = now + 3600s`
- the runtime presents the envelope to the participant model via the runtime's input boundary (NOT via ordinary conversational delivery)
- the runtime produces a session via the verified CLI footer channel
- the runtime emits a signed acceptance receipt whose `session_id`, `charter_id`, `charter_sha256`, `runtime_fingerprint`, `attestation_quote_b64`, `nonce_freshness` are correctly populated
- the runtime emits 6 governed turns; each turn carries a `turn_envelope` whose fields match the acceptance
- the anchor observes every emitted artifact

J.1.2 **Exact trust claim being tested.** *There exists a participant runtime such that an out-of-band verifier can independently establish that governance binding occurred.* Specifically:

- the issuer was admitted by the RTA (verifiable)
- the issuer signed the envelope (verifiable)
- the charter bytes match the declared digest (verifiable)
- the acceptance receipt was signed by the runtime-resident key bound to a TPM-attested runtime (verifiable)
- the acceptance receipt binds the session, the charter, and the runtime fingerprint (verifiable)
- the runtime was not substituted between acceptance and governed turns (verifiable, G.1.2)
- the audit chain is hash-chained and externally anchored (verifiable, G.6, H.3)

J.1.3 **Observable evidence.** Verifier-side logs of:

- RTA roster admission record + signature
- issuer envelope + signature
- charter canonicalized bytes + digest
- acceptance receipt + signature + TPM attestation quote
- turn chain (6 turns × envelope each, hash-chained)
- anchor log entries

J.1.4 **Expected result.**

- assurance level reached: **G5 — INDEPENDENTLY VERIFIED GOVERNANCE** (per §K)
- STOP codes: none
- case PASSES

J.1.5 **STOP code on failure.** If any verifiable check fails, the case fails. There is no single STOP code; the failure path is whichever check found the mismatch (e.g., `GX_ATTESTATION_INVALID`, `GX_RUNTIME_REPLACED`, `GX_TIME_UNCERTAIN`).

J.1.6 **Falsification condition.** v0.2 claims Case 1 passes if the verifier can independently re-establish all the trust claims in J.1.2 from the anchored artifacts alone, without trusting the participant host. If the verifier cannot, the case is falsified.

### Case 2 — Invalid/untrusted issuer

J.2.1 **Setup.** Same as Case 1 except the issuer's public key is NOT on the RTA roster at the time of envelope validation. The participant runtime accepts the envelope with a valid signature, but the verifier's trust-roster check fails.

J.2.2 **Exact trust claim being tested.** *An envelope issued by an entity not on the trust roster is rejected at the verifier, even if the envelope signature verifies against some key.*

J.2.3 **Observable evidence.** Verifier-side log shows roster check failure, with the issuer key in question listed as not admitted. The acceptance receipt may still be produced (depending on runtime configuration), but it is a non-evidence receipt.

J.2.4 **Expected result.**

- assurance level reached: **G0 — UNVERIFIED**
- STOP code: `GX_ISSUER_UNAUTHORIZED` (because unknown-to-roster ≈ unauthorized at evaluation time)

J.2.5 **STOP code on failure.** `GX_ISSUER_UNAUTHORIZED`.

J.2.6 **Falsification condition.** v0.2 claims Case 2 fails if the verifier accepts the envelope as authoritative despite the issuer not being on the roster. If the verifier does, the spec is falsified.

### Case 3 — Provenance missing / inline charter only

J.3.1 **Setup.** The charter bytes are placed into the participant's prompt context directly, with no envelope, no issuer signature, no runtime-side acceptance. This is the v0.4.4 scenario reproduced.

J.3.2 **Exact trust claim being tested.** *An unsigned or un-issuer-signed charter cannot establish governance, even when structured identically to a valid charter.*

J.3.3 **Observable evidence.** The verifier has no envelope artifact, no issuer signature, no acceptance receipt. Whatever the participant produces is unauthenticated narration.

J.3.4 **Expected result.**

- assurance level reached: **G0 — UNVERIFIED**
- STOP code: `GX_PROVENANCE_MISSING`

J.3.5 **STOP code on failure.** `GX_PROVENANCE_MISSING`. Note: the model may still emit a "yes I accept"-sounding output; that is unauthenticated narration and is not a receipt.

J.3.6 **Falsification condition.** v0.2 claims Case 3 fails if the verifier treats any charter-shaped text in conversational context as authoritative. If the verifier does, the spec is falsified (this was the v0.4.4 finding the spec addresses).

### Case 4 — Participant and formal verifier share the same host/trust boundary

J.4.1 **Setup.** The verifier process runs on the same machine as the runtime, under the same operator account. Trust-roster sources and TPM attestation paths go through the operator-controlled host's filesystems or services.

J.4.2 **Exact trust claim being tested.** *A PoC with collocated verifier and participant does not constitute formal evidence.*

J.4.3 **Observable evidence.** The verifier-side log includes a `verifier_host_id` field. The log demonstrates that `verifier_host_id` ∈ participant host trust boundary (per §C.1.1).

J.4.4 **Expected result.**

- assurance level reached: at most **G4 — RUNTIME-CONTINUOUS GOVERNANCE** (because locally hash-chained + runtime-continuity still hold); **NOT** G5
- result: **NOT ACCEPTABLE AS FORMAL EVIDENCE**
- STOP code: `GX_NOT_ACCEPTABLE_AS_FORMAL_EVIDENCE`

J.4.5 **STOP code on failure.** `GX_NOT_ACCEPTABLE_AS_FORMAL_EVIDENCE`.

J.4.6 **Falsification condition.** v0.2 claims Case 4 produces NOT_ACCEPTABLE_AS_FORMAL_EVIDENCE despite all previous-stage checks passing. If the verifier treats collocation as sufficient, the spec is falsified.

### Case 5 — Host/issuer clock rollback or stale validity evidence

J.5.1 **Setup.** The issuer signs an envelope with `not_after_utc` far in the past. The attacker (operator-controlled) presents the envelope after the clock has rolled back, attempting to make it appear valid. Trusted-time per §F is in force.

J.5.2 **Exact trust claim being tested.** *An envelope whose `not_after_utc` predates trusted-now is rejected.*

J.5.3 **Observable evidence.** Verifier-side log shows trusted-now greater than `not_after_utc` plus tolerance.

J.5.4 **Expected result.**

- assurance level reached: **G0 — UNVERIFIED**
- STOP code: `GX_AUTH_EXPIRED`

J.5.5 **STOP code on failure.** `GX_AUTH_EXPIRED` (or `GX_TIME_UNCERTAIN` if trusted-time is unavailable).

J.5.6 **Falsification condition.** v0.2 claims Case 5 fails if the verifier accepts the envelope as valid despite `not_after_utc` having passed. If accepted, the spec is falsified.

### Case 6 — Participant runtime replacement after acceptance

J.6.1 **Setup.** The runtime is replaced (e.g., the model swapped from `gpt-5.6` to `claude-opus-4-7`, or a different Hermes instance invoked) after the acceptance receipt has been emitted and verified. The replacement runtime attempts to issue subsequent turns.

J.6.2 **Exact trust claim being tested.** *A runtime whose signing key, fingerprint, or attestation differs from the acceptance receipt is detected on the next turn.*

J.6.3 **Observable evidence.** The verifier-side log shows a `turn_envelope` whose `runtime_fingerprint` differs from the acceptance receipt, OR whose attestation quote is not bound to the original signing key.

J.6.4 **Expected result.**

- assurance level reached: **G0 — UNVERIFIED** (because binding continuity is broken for the new turn; prior turns remain at whatever assurance level they had at the time of emission)
- STOP code: `GX_RUNTIME_REPLACED` (or `GX_ATTESTATION_INVALID`)

J.6.5 **STOP code on failure.** `GX_RUNTIME_REPLACED` or `GX_ATTESTATION_INVALID`.

J.6.6 **Falsification condition.** v0.2 claims Case 6 fails if any turn by the replacement runtime is accepted as belonging to the same governance session. If accepted, the spec is falsified.

### J.7 **Two cross-cutting structural assertions for all cases**

J.7.1 The PoC's *evidence* is anchored (§H.1.2 minimum) before v0.2 claims any G5 result.

J.7.2 The PoC's *verifier* is out-of-band before Cases 1, 2, 3, 5, 6 can claim G5. Case 4 explicitly tests what happens when it is not.

## K. Assurance levels

K.0 The assurance taxonomy is ordinal. Higher levels imply all lower-level guarantees plus more.

- **G0 — UNVERIFIED.** No signed evidence exists, OR existing evidence fails to verify. No claim can be made about governance binding.
- **G1 — PROVENANCE VERIFIED.** The charter bytes are canonically identified (charter_id + charter_sha256 verify against issuer-signed canonicalized bytes) and the issuer is on a current roster. No acceptance has occurred yet, or acceptance evidence is unavailable.
- **G2 — GOVERNANCE ACCEPTED.** G1 + a structured acceptance receipt exists, its signature verifies under a key whose attestation is associated with the receipt, and the receipt binds session + charter + runtime. Acceptance is attested *by the runtime*. Model-intrinsic acceptance is NOT asserted.
- **G3 — RUNTIME-BOUND GOVERNANCE.** G2 + the signed acceptance receipt's signing key is bound to a TPM-attested runtime on a specific host (independent verifier can check the binding chain). The runtime is the right runtime for the given acceptance.
- **G4 — RUNTIME-CONTINUOUS GOVERNANCE.** G3 + every turn in the governed session carries a continuity artifact (G.1.1) that matches the acceptance receipt. No undetected runtime substitution in the session.
- **G5 — INDEPENDENTLY VERIFIED GOVERNANCE.** G4 + the audit chain is externally anchored (§H.1.3) AND the verifier is out-of-band (§C) AND the trust roster is current (§D.9). Result is independently re-verifiable from anchored artifacts alone.

K.1 **What G5 does NOT establish.** G5 establishes evidence that binding occurred and was governed. It does not establish:

- that the model in the runtime was persuaded, comprehended, or *chose* to accept
- that the model will behave per the charter in future sessions
- that the charter's content is morally correct or epistemically warranted
- that the operator has no conflict of interest
- that the governance binding causally produces conforming behavior

K.2 **What v0.2 contributes (v0.1 overclaims → v0.2 corrections).** v0.2 establishes that evidence of binding can be independently verifiable at G5. v0.2 does NOT establish that *behavior* follows. Future work may attempt such a property; v0.2 is silent on its achievability.

## L. Self-review (compromise-resistance)

L.1 **The required self-review question.** *"Could a compromised host still manufacture evidence that would cause an independent verifier to conclude the wrong participant accepted and remained bound to the governance?"*

L.2 **Analysis.** Walking through the answer:

L.2.1 *Can the compromised host forge a runtime signature?* Yes, if the attacker holds the runtime's signing key. The TPM-Bound key is mitigated if and only if the TPM-resident key is non-extractable (TPM-generated and TPM-bound). v0.2 §B.3.3 + E.3.2 require TPM2_Quote, which on most TPMs implies the key cannot be extracted in cleartext. **Mitigated IF the TPM is hardware and not bypassed.**

L.2.2 *Can the compromised host forge an attestation quote?* Yes, if the attacker has access to the TPM's attestation key. Most TPMs permit quote-by-authority, but quote derivation requires either the Attestation Key (which is non-extractable in TPM) or a signing capability the TPM exposes. **Mitigated IF the TPM is hardware and not bypassed.**

L.2.3 *Can the compromised host bypass TPM check?* Yes, by software emulation ("I pretended to be TPM"). v0.2 specifies TPM *attestation* — meaning the verifier fetches the manufacturer root and validates the quote against it. Software-emulated TPMs cannot produce a quote verifiable under a hardware root. **Mitigated IF the verifier uses manufacturer-root validation, which the verifier MUST do per §C.2.**

L.2.4 *Can the compromised host produce a valid envelope + acceptance + turns + anchor log?* Yes, but only if the anchor is also compromised. Per §H.3.1 the anchor is out-of-band. **Mitigated IF the anchor is correctly out-of-band.**

L.2.5 *Can the compromised host replay a historical acceptance receipt?* Yes, but the rejection log (§J.5, §I.3) detects duplicate nonces. **Mitigated IF the rejection log is consulted.**

L.2.6 *Is the host running the participant the *same* host as the host running the verifier?* Per §C this must not be. **Mitigated IF verifier is out-of-band.**

L.3 **Residual compromise risk.** Three residual risks persist after applying v0.2:

L.3.1 TPM hardware compromise (rare but possible; would require TPM vendor cooperation to detect in real time). v0.2 does not address this.

L.3.2 RTA key compromise without detection. Per §D.7 the RTA can rotate, but a compromised RTA could issue false admission records before the compromise is detected. The defense is the transparency log (§D.8.4) which would record the false admission. **Mitigated IF the transparency log is itself trustworthy.**

L.3.3 Operator compromise of both the participant host AND the verifier host. This is "two hosts, one operator." v0.2 requires *distinct operator* only as a SHOULD (C.1.2). **If the operator is the attacker on both sides, v0.2 cannot defend.** This is a documented limit and must be acknowledged.

L.4 **Disposition under self-review.** Given L.3.1, L.3.2, L.3.3 are real but bounded:

- L.3.1 is sufficiently rare to not block a PoC.
- L.3.2 is detected by transparency log eventually.
- L.3.3 is an organizational / policy limit, not a protocol limit.

Therefore the answer to L.1 is: *"A compromised participant host alone cannot manufacture G5 evidence IF the verifier is out-of-band, the anchor is out-of-band, the TPM is hardware, the roster transparency log is current, and (with Caveat L.3.3) the verifier is not co-operated by the same adversary as the participant operator."*

A PoC satisfying these five conditions v0.2 considers **NOT_READY_FOR_POC** only if any of those five conditions cannot be met by the chosen test infrastructure. A PoC failing any of them can be run as *informal* evidence but cannot claim G5.

L.5 The v0.2 PoC design (§J) requires all five conditions; if any of the five cannot be met, the disposition is **NOT_READY_FOR_POC**.

L.6 **The self-review answer for the v0.2 PoC design (J.0.1, J.0.3) is:** infrastructure includes a hardware-or-emulated TPM, an out-of-band verifier, an out-of-band anchor, a current transparency log, and (subject to operator policy) a distinct operator for the verifier. L.3.3 remains a residual limit the PoC documents but does not solve.

## M. Disposition

M.1 v0.2 — accept the constraints listed in this revision. Specifically:

- operator-controlled trust roster with RTA-anchored transparent publication
- out-of-band verifier, anchor, and (per operator policy) operator
- hardware TPM (or hardware-emulated TPM with manufacturer-root validation), with key non-extractability
- per-turn runtime continuity checking
- externally anchored audit chain
- clarified assurance taxonomy (G0-G5)

M.2 v0.2 — disclaimer carried from §I.6: *the protocol establishes evidence that governance binding occurred. It does not by itself establish that the agent will behave according to that governance.* This is the residual limit of even G5.

M.3 **Disposition under the L.5 test:** conditions met. **Disposition: `READY_FOR_POC`** with the explicit L.3.3 caveat documented.

M.4 **Unresolved assumptions at v0.2 close.** Carried-forward open questions (from v0.1 §9 and the v0.1 review §10) narrowed by v0.2:

M.4.1 *(formerly §9 / review §10 question 1)* RTA governance: now specified (§D). The trust anchor itself (§D.1) is the policy assumption.

M.4.2 *(formerly question 2)* Algorithm agility: pinned to Ed25519 + TPM2_Quote (§E.3). Trade-off accepted: less agility, more predictability. Future versions may broaden.

M.4.3 *(formerly question 3)* Participant signing primitive: now specified (§B). The assurance boundary (§B.6) preserves the runtime-vs-model distinction.

M.4.4 *(formerly question 4)* Canonicalization: now specified (§E.1) with explicit null/array/object rules.

M.4.5 *(formerly question 5)* Revocation freshness: now specified (§D.9) with explicit fail-closed (§D.10).

M.4.6 *(formerly question 6)* Audit-trail format and storage: now specified (§H) with three levels of auditability distinguished (§H.1).

M.4.7 *(formerly question 7)* Time-source trust: now specified (§F) with explicit out-of-band requirement.

M.4.8 *(formerly question 8)* `charter_id` vs `charter_sha256`: still requires the operator to declare whether `charter_id` is content-addressable (charter_sha256-derived prefix) or symbolically assigned. v0.2 does not resolve this; recommend content-addressable for v0.2 PoC.

M.4.9 *(formerly question 9)* Emergency PI override: not specified in v0.2; left for v0.3. Until then, legitimate emergency revocation has no defined mechanism (acknowledged limit; see §L.3.2 partial mitigation).

M.4.10 *(formerly question 10)* Multi-arm experiments: now partly specified (§J.7.2). Per-arm envelope_nonce uniqueness is implicitly required by §I.3 (rejection log); a future v0.3 should make this explicit with a STOP code `GX_ENVELOPE_CROSS_ARM`.

## N. Scope

N.1 This document is a design revision. It creates:

- v0.2 specification of Trusted Governance Establishment
- six-case PoC specification (Cases 4-6 added; Cases 1-3 preserved with v0.2 corrections)
- an Assurance Level taxonomy (G0-G5)
- explicit handling of the residual "agent-behaviour" question

N.2 This document does NOT:

- modify v0.1 or its review
- execute any PoC case (J cases are designed, not run)
- begin COA-E3
- create experimental profiles
- generate nonces
- invoke any participant

N.3 Awaiting PI authorization before any PoC execution.

## O. STOP-code index (v0.2 final)

- `GX_HANDSHAKE_STEP<n>_<reason>` — handshake-step rejection (handshake-stage failures)
- `GX_<THREAT_NAME>` — detected-threat rejection (post-validation failures)
- `GX_NOT_ACCEPTABLE_AS_FORMAL_EVIDENCE` — evidentiary-method rejection (collocated verifier, etc.)
- `GX_RUNTIME_REPLACED` — runtime continuity broken
- `GX_ATTESTATION_INVALID` — signing key not bound to original attestation
- `GX_SESSION_SUBSTITUTION` — post-binding session swap
- `GX_PROVENANCE_MISSING` — inline-delivered charter
- `GX_CHARTER_ALTERED` — charter digest mismatch
- `GX_ISSUER_FORGED` / `GX_ISSUER_UNAUTHORIZED` — issuer roster check fails
- `GX_AUTH_EXPIRED` / `GX_AUTH_REVOKED` — temporal scope failure
- `GX_TIME_UNCERTAIN` — trusted-time failure
- `GX_TRUST_ROSTER_UNAVAILABLE` — roster freshness/fetch failure
- `GX_REPLAY_DETECTED` — nonce on the rejection log
- `GX_UNKNOWN_FIELD_PRESENT` — diagnostic; not rejection by itself
- `GX_ENVELOPE_CROSS_ARM` — proposed for v0.3 (cross-arm contamination)

## P. Branch state and changes

P.1 New file: `architecture/experimental/TRUSTED-GOVERNANCE-ESTABLISHMENT-v0.2.md`. v0.1 and its review unchanged.

P.2 No other files modified.

# Adversarial Review — Trusted Governance Establishment v0.1

**Review of:** `architecture/experimental/TRUSTED-GOVERNANCE-ESTABLISHMENT-v0.1.md`
**Reviewed SHA-256:** `937f01ad311a4da09b3ab3ce7b2507a2d884268077e51bb9fa6f0d3bd7e9e53b`
**Reviewed commit:** `2aabf803cba3d799c2ebded7c251126f484eaaeb` (parent: v0.4.4 closeout `0b82a80`)
**Reviewer:** Hermes (red-team pass under research-manager-mandate-2026-08-27)
**Review date:** 2026-09-14
**Purpose:** determine whether the spec is *structurally capable* of supporting independently verifiable agent trust, rather than merely relocating trust assumptions into new artifacts.

## 0. Headline finding

The specification is a clear and serious improvement over the v0.4.4 inline-charter design. However, it does **not yet establish independently verifiable trust**, because three structural assumptions (one of them a single point of failure) silently relocate rather than eliminate trust. Two of those three are the same blockers the spec itself already flags. The third — a missing participant-side signing primitive — is the load-bearing hole.

If this document is presented to a red-team as-is, the simplest attacks against it succeed. If those attacks are added to the three-case PoC, Case 1 (Valid trusted governance chain) would likely *appear* to pass while a closer audit would invalidate the acceptance. That outcome would corrupt the proof-of-concept.

**Overall disposition (see §11):** `READY_AFTER_SPECIFIC_FIXES`

## 1. The PI-mandated three PoC-blocking questions

### 1.1 Participant signing primitive [BLOCKS_POC] [MUST_FIX_BEFORE_FORMAL_EVIDENCE]

The spec acknowledges (§9 question 3) that **the participant has no persistent signing key** in any current harness. It papers this over by referring generically to "a key the participant can prove it holds." This is the load-bearing hole. Until it is concretely defined, *Step 4 is not implementable in any agent runtime that lacks root-level access to a private signing key*, which is every LLM-backed agent runtime available today.

**What entity actually possesses the signing capability?**

The spec never says. The four candidates are:
- **(a) the model.** Models don't have signing keys. They produce text. ✗
- **(b) the local agent runtime (Hermes).** Hermes does have access to its own private keys for outbound OAuth, but it is not the participant — it is the host. ✗
- **(c) the operator-controlled process that signed the envelope.** This collapses participant and issuer identity, eliminating the very distinction the spec is built around. ✗
- **(d) a hardware root of trust (TPM / HSM / secure enclave).** Possible, but the spec never commits to one. ⚠

If the answer is (c), the spec's "explicit acceptance" is not the participant's acceptance — it is the operator's assertion *about* the participant. v0.4.4 failed because inline-charter authority was faked; this design risks failing because acceptance is faked.

**How is that signing identity bound to the participant runtime and the specific persistent session?**

The spec asserts binding via `participant_fingerprint` (§3 Step 3), but `fingerprint` is a *descriptor*, not a cryptographic binding. There is no proof in the spec that the fingerprint cannot be spoofed by a different agent instance (e.g., a fork or a parallel prompt on the same runtime).

**Can the host/operator forge the participant's acceptance?**

Yes, by construction. If the participant signing key lives on the same machine that runs the model, and that machine is operator-controlled, the operator can produce arbitrary signatures on behalf of the participant. The spec calls this out as anti-constraint #2 ("no self-attested authority") but does not provide a mechanism that would prevent it. The acceptance receipt therefore does not prove that the *participant* accepted — only that *something with access to a key* accepted.

**Can another model or process reuse the participant identity?**

The spec does not say. With an unenforced fingerprint, any process running as the same operator can claim to be the participant. With a fingerprint bound only to model/runtime/config, a model swap (e.g., Hermes routing from GPT-4 to Claude via the same harness) would produce a different config_hash and presumably fail to re-bind — but the spec doesn't trace this through. It says `participant_fingerprint = model_id | provider | runtime_version | config_hash | deployment_fingerprint` and then never returns to it.

**Does the proposed mechanism prove anything stronger than host attestation?**

**No.** As written, the spec proves:
- an *operator-controlled* issuer asserts the charter is binding, and
- a *host-side* signer (which is to say, the same operator) asserts the participant accepted it.

That collapses to: *the operator attested*. Useful, but not stronger than the operator's good faith. The spec does not currently deliver trust that resists a compromised host — which is precisely where the trust claim needs to hold.

**Specific recommendation (see also §11.2):** the participant signing primitive must (a) live outside the operator-controlled host that ran the original model, OR (b) be an unbypassable enclave attestation with cryptographic verification by the verifier-side, OR (c) be a *TPM-style remote attestation quote* the verifier can check against a manufacturer root. Option (c) is the most deployment-credible for v0.1. The TPM quote binds the *runtime binary* (not the model behaviour) which is a partial defense. Full behavioral binding would require the *output content* to be signed-by-the-runtime (which Hermes-style runtimes can do at the API boundary). Combine (c) with structured-output signature by the runtime: that is, the runtime signs the acceptance receipt at the point the bytes are emitted, citing a TPM-quoted identity, and the verifier independently checks both.

### 1.2 Trust-roster governance [MUST_FIX_BEFORE_FORMAL_EVIDENCE]

The spec uses "operator-controlled trust roster" (§3 Step 1, §4 envelope) without defining:
- how issuers are added to the roster,
- how they are removed,
- what happens on key compromise,
- how key rotation is governed,
- how the roster itself is rooted.

**Who is authorized to establish an issuer as trusted?** Not specified. Implicitly: the operator. Implicitly more finely: a human role in the operator organisation. Not specified in any artifact.

**What is the root of trust?** Not specified. The spec implicitly assumes one operator-level trust roster exists; it does not say who holds the master key, whether that key is in HSM, or how a new operator takes over.

**How are additions, removals, compromise, rotation, and revocation governed?** Not specified. The spec says "operator-controlled" and stops. There is a hard-coded revocation list reference field (`revocation_list_reference: <URL-or-URN>`) but no protocol for signing and serving it.

**Does this create an infinite regress of authorities requiring authorities?** Yes — unless the roster is rooted in something the verifier can check independently (HSM-backed operator key, code-signing certificate, code transparency log). The spec does not specify any of these. The threat-model table references "operator-controlled public key" several times but never resolves to a single verifiable root.

**Recommendation:** the spec must specify (a) the format of the trust roster itself (signed by a roster-root authority), (b) the key lifecycle policy for both roster-root and issuers, (c) a transparent log or signed-tree of roster revisions, (d) the fallback when the roster is unavailable. Without these, *every* GX_ISSUER_FORGED and GX_ISSUER_UNAUTHORIZED check depends on a roster the verifier cannot independently validate.

### 1.3 Canonicalization and signed-object semantics [DESIGN_HARDENING]

**Is RFC 8785 JCS adequate for v0.1?** Mostly, with caveats.

- ✓ Covers JSON canonicalization (sorted keys, no insignificant whitespace, UTF-8 NFC normalization).
- ✗ Does NOT cover number normalization (IEEE 754 ambiguities, integer-vs-float representation of small whole numbers). For `charter_canonical_bytes_b64` (base64 strings) and hex fields, this is not an issue. But envelope fields declared as `> 0` durations or counts could mutate.
- ✗ Does NOT specify what to do with `null` vs missing vs empty-string. Two envelopes that differ only in JSON nullity representations may canonicalize to identical bytes — silently weakening what is signed.
- ✗ Does NOT cover arrays vs sets: a JSON array of unique elements can be re-ordered without changing equality under most JSON canonicalization, so an envelope with `["x","y"]` and `["y","x"]` may both be canonical, but only one of them matches the issuer's signed intent.

**What bytes/fields are signed?** The spec is fuzzy here. The envelope (§4) lists `issuer_signature_b64` *inside* the `charter` block, and lists `participant_signature_b64` inside `acceptance_receipt`. It does not say whether the issuer's signature covers:
- only `charter_canonical_bytes_b64`, or
- the `charter_record` metadata too, or
- the entire envelope, or
- an outer envelope hash.

Without a precise "what is signed over" statement, the entire envelope is open to:
- **mutation attacks:** a field outside the signed region can be tampered with.
- **partial-signature attacks:** the verifier cannot tell which subset is the issuer's claim vs which subset is the participant's.
- **downgrade attacks:** a malicious party can present the same envelope with `signature_algorithm: "RSA-PKCS1v1.5-SHA1"` if the verifier doesn't constrain algorithms.
- **replay attacks across envelopes:** if the issuer signs only the charter bytes and not the envelope_id/nonce_freshness, the same charter signature can be reused on a new envelope without invalidating it.

**Recommend:** make the signed region explicit. The cleanest v0.1 design is: the issuer signs `canonicalized_envelope` with a fixed outer envelope shell — i.e., the issuer computes `signed_bytes = canonicalize({envelope_id, not_before, not_after, issuer_id, charter_id, charter_sha256, charter_canonical_bytes_b64, participant_fingerprint_predicate, binding_session_id_predicate, all_must_be_signatures}.rest)` and signs that. The `acceptance_receipt` is then the participant's signature over `canonicalize({charter_id, charter_sha256, session_id, participant_fingerprint, nonce_freshness, accepted_at_utc})`, never over the issuer signature, so they are independent.

## 2. Other design assumptions

### 2.1 Charter identity vs. charter content [DESIGN_HARDENING]

`charter_id = "coa-e2-governed-v0.4.1"` is presented as an opaque identifier. But §3 Step 2 also has `charter_sha256`, and both must match. The spec does not specify whether `charter_id` is content-addressable (= charter_sha256 with display formatting) or a separately-assigned symbol. Two risks:

- **id/content drift:** if `charter_id` is a name (not a digest), an issuer can mint a new `charter_id` pointing to a re-broken charter and the verifier cannot tell.
- **display-only collision:** if `charter_id` *is* a digest, two issuers independently minting "coa-e2-governed-v0.4.1" would necessarily have the same bytes — but the spec does not enforce that.

**Recommend:** declare `charter_id` to be the *content-derived* prefix of `charter_sha256` (or similar), and require `charter_id == str(charter_sha256[:N])` for some N — making collision detection cheap and drift impossible.

### 2.2 Issuer identity vs. issuer authority [DESIGN_HARDENING]

The envelope separates `issuer.public_key` from `authority_grant_*` but the validation rule is textual ("signature verifies") rather than structural (verifier must check grant-scope against signature). A passive verifier that just checks signature verifies may miss an out-of-scope issuer. The spec calls this out as §9 question 1 territory, but the validation rule should explicitly enumerate the out-of-scope failure case before stopping.

### 2.3 Nonce freshness [DESIGN_HARDENING]

`nonce_freshness` is referenced in three places (Step 4 evidence, §4 envelope field, §5 threat case 4). It is never defined. Is it a per-issuer nonce? Per-envelope? Per-session? Per-day? The spec assumes uniqueness globally; that is unsafe.

**Recommend:** name it `envelope_nonce` (32-hex) and require nonces to be:
- unique per-issuer within the issuer's revocation-list-lookback window,
- unique per-session (within the binding's session lifetime),
- present in the rejection log when accepted, and
- present in the rejection log when replayed.

This makes "replay" measurable, not just asserted.

### 2.4 Clock / time-source trust [BLOCKS_POC] [MUST_FIX_BEFORE_FORMAL_EVIDENCE]

The spec uses `valid_from` / `valid_until` / `accepted_at_utc` / `not_before_utc` / `not_after_utc` extensively, but never says whose clock is authoritative. In COA-E2's host (a Linux system), the system clock is operator-controlled — the operator can roll the clock back to make an expired envelope appear valid, or forward to make a not-yet-valid envelope appear valid.

The spec does not say "Roughtime-style" or "RFC 3161 TSA-signed" or "monotonic counter signed by issuer". v0.4.4 had a model layer that could plausibly trust its own output timestamps as evidence, but the verifier side here is *not* the model — it's an auditor. The auditor cannot trust the host clock.

**Recommend:** the envelope SHOULD include an issuer-signed timestamp, and verifiers MUST cross-check the issuer-signed timestamp against a Trusted Timestamp Authority (TSA) or RFC 3161 token. Otherwise, "expiration/revocation" is provably unenforceable.

### 2.5 Revocation freshness [DESIGN_HARDENING]

`revocation_list_reference` is present but no freshness window is specified. If the verifier is offline, "the issuer revoked this envelope" cannot be checked. If the verifier is online but the revocation list is stale, a recently-revoked envelope can be treated as valid.

**Recommend:** specify freshness tolerance in seconds and a "fail closed" policy when the revocation endpoint is unreachable. v0.1 should pick one (e.g., 60-second tolerance, fail-closed on offline).

### 2.6 Algorithm agility and downgrade resistance [DESIGN_HARDENING]

The spec says "verifier MUST refuse any algorithm not in a known set (Ed25519 by default; SHOULD allow ECDSA-P256-SHA256)". This is good intent, but:

- "Should allow" is normative ambiguity — it permits the verifier to accept only Ed25519, which silently drops ECDSA-P256-SHA256 issuers. The verb is wrong: it should be "MUST allow" if both are mandatory, OR v0.1 should pick one.
- No defense against algorithm downgrade: a malicious issuer could re-sign with a weaker algorithm. The verifier must pin algorithms per-issuer, not per-message, OR refuse any non-default algorithm unless an explicit policy field allows it.

**Recommend:** v0.1 picks exactly one issuer algorithm (Ed25519) and one participant algorithm (Ed25519, if a participant primitive exists). `signature_algorithm` becomes a constant. v0.2 introduces agility with explicit policy gating.

### 2.7 Acceptance replay [DESIGN_HARDENING]

`acceptance_receipt` carries `nonce_freshness` (per spec) and `accepted_at_utc`. The spec asserts nonce uniqueness, but does not say *who* stores the nonce-consumed log. If the verifier doesn't learn that a nonce was consumed, it can be replayed.

**Recommend:** the runtime (not the participant, not the issuer) MUST record `{nonce_freshness, session_id, accepted_at_utc}` in a runtime-signed append-only log (e.g., Hermes state.db's `session_turn_leases` extended, or a separate runtime journal table). The verifier checks the log before accepting.

### 2.8 Session substitution [DESIGN_HARDENING] (partially good)

Step 5 stops session substitution if `session_id` is the verified-CLI-footer session id. This is structurally correct against substitution-from-outside. **But it does not address substitution-from-within**: a stateful runtime (Hermes state.db) might silently *resume* a session under a new participant configuration. The spec's `participant_fingerprint` is checked at Step 3 but never re-checked when each turn is emitted (Step 6). 

**Recommendation:** Step 6 MUST re-verify that the *current* participant_fingerprint at each turn equals the Step 3 fingerprint — not just that the charter reference reappears. Without this, an attacker who compromises a runtime in mid-session can swap the model under the same session.

### 2.9 Model / runtime replacement after acceptance [BLOCKS_POC] [MUST_FIX_BEFORE_FORMAL_EVIDENCE]

Closely related to §2.8 and §1.1. The spec's reliance on a `participant_fingerprint` string is identity-by-name, not identity-by-evidence. To prevent mid-session model swap, the verifier needs a *cryptographically bound* runtime identity, e.g., a TPM-signed quote of (process, model, config) at every turn — or at every acceptance.

The spec treats `participant_signature_b64` as if any signing key were equivalent. Without a binding between the signing key and a specific runtime instance, "the participant" is just "whoever has this key", which is operator.

### 2.10 Host compromise [BLOCKS_POC]

If the host running the participant is compromised, *every* authority in the spec is subverted:
- The signed envelope can be dropped or replaced with one the attacker chose.
- The participant signature is forgeable (the attacker holds the key).
- The session_continuity_token is forgeable (the attacker controls the runtime).
- The audit trail can be re-emitted with attacker-chosen artifacts.

The spec does not address this. The whole premise of "verifier side independently verifies" depends on a verifier *out of band of the compromised host* — typically a separate process on a separate machine. The spec's threat model assumes this implicitly; it should be made explicit.

**Recommendation:** v0.1 must add a normative requirement that the *verifier* is deployed out-of-band of the host. A v0.1 PoC running both verifier and participant on the same Linux user account is not testing what the spec claims to test.

### 2.11 Audit-chain truncation or rewriting [DESIGN_HARDENING]

Step 7 specifies a hash chain but not where the chain is *anchored*. If the chain is anchored only at its head (last entry), an attacker with operator privilege can rewrite every entry back to genesis by recomputing the chain.

**Recommendation:** the chain MUST be anchored externally — either via periodic publication to a transparency log (certificate-transparency style) or via periodic issuance of a Signed Tree Head (STH) signed by an authority outside the audit's writable path. v0.1 should pick at least *append-only* as a normative requirement on the storage layer.

### 2.12 PI / emergency override semantics [DESIGN_HARDENING]

§9 question 9 acknowledges this. The spec has no normative override path. Without one, a legitimate emergency revocation (e.g., a compromised charter is in the wild) has no defined mechanism. The risk is that the override path becomes whatever the operator unilaterally implements — which is exactly the kind of trust relocation this spec is supposed to prevent.

**Recommendation:** specify an emergency override envelope type, distinct from a normal envelope, with stricter validation (e.g., always valid for shorter windows, requires a quorum signature from N out of M issuer-keys).

### 2.13 Cross-arm contamination in experiments [DESIGN_HARDENING] (extend the spec)

The spec is silent on multi-arm experiments in §9 question 10. The COA-E2 design history shows cross-arm contamination is a real risk (the v0.4.x freeze manifest had to be regenerated to fix shared-template issues). For a v0.1 PoC, cross-arm contamination is a real attack surface — a charter signed for arm A leaking across to arm B's session binding.

**Recommendation:** explicitly assert that `envelope_nonce` MUST be unique across arms of the same experiment, and add a PoC Case 4 ("envelope issued to arm A re-aimed at arm B") with expected STOP `GX_SESSION_SUBSTITUTION` or similar.

## 3. Claims that exceed evidence or mechanism

1. **"Explicit acceptance is what the participant agreed to."** Stronger than the spec supports. As written, the acceptance is whatever the host signs. If the host is compromised or operator-controlled, the acceptance is operator-signed, not participant-expressed. (§2.10, §1.1)

2. **"The audit chain can be re-verified after execution."** Conditional — only if the chain is anchored externally (§2.11). The spec doesn't say.

3. **"Replay cannot succeed because of the freshness nonce."** Conditional — only if nonces are tracked globally by some authority outside the participant runtime. The spec doesn't say. (§2.3, §2.7)

4. **"Session substitution is impossible because the session id is from the verified CLI footer."** Only true for out-of-session substitution; doesn't address mid-session substitution. (§2.8)

5. **"The trust chain is independently verifiable."** Conditional on the verifier being out-of-band of the host. (§2.10)

6. **"No prompt engineering works."** True at the agent interface, but the verifier side is unchanged by the spec's claim. The spec should say what *does* work — specifically, structural acceptance defined by the envelope — and not just what does not.

7. **"Operator-controlled trust roster."** Implicitly assumes the operator is trustworthy. The spec inherits the operator's trust, doesn't replace it. The spec does not lie here, but it could be clearer about the limit.

8. **"The structured acceptance receipt format MUST be defined by the envelope."** Fine. But the *format* alone doesn't produce acceptance — the *behavior* of the participant when no enforced format exists doesn't matter; a model can produce any text. The spec implicitly assumes a runtime that *requires* the participant to produce a structured receipt or refuses to emit a turn. This is a runtime requirement (e.g., an API boundary rule), not a model behavior. The spec should be explicit about which enforcement is runtime-side and which is model-side.

9. **"Canonicalized charter bytes."** `charter_canonical_bytes_b64` carries the *bytes* but the spec never says how the charter is canonicalized. Different mail clients, different line endings, different versions of UTF-8 NFC normalization will produce different digests, and the verifier cannot check the issuer's intent. (§1.3)

10. **"Structured acceptance makes free-form acceptance insufficient."** True at the verifier. But the verifier needs to actually reject free-form, and the spec doesn't say what free-form looks like at the verifier boundary. A "free-form acceptance" with all the right fields filled in (just without ceremony) would pass. The verification is "this receipt exists and has these fields" — not "this participant actually reasoned about the charter". The spec name "Explicit acceptance" overstates what the structural check provides. A better name might be "Attested-by-runtime acceptance" or "Receipt-validated acceptance."

## 4. Threat-case table — review of each

| # | Threat | Code | Verdict on coverage |
| - | ------ | ---- | ------------------- |
| 1 | Forged issuer | `GX_ISSUER_FORGED` | Detectable IF the verifier has a roster-rooted set of issuer keys. Roster-root governance is undocumented (§1.2). DESIGNSIGNATURE OK; CONTEXT-DEPENDENT. |
| 2 | Unauthorized issuer | `GX_ISSUER_UNAUTHORIZED` | Detectable IF the verifier checks grant-scope, not just signature. Spec doesn't enforce grant-scope in validation rule (§2.2). DESIGN_HARDENING. |
| 3 | Altered charter | `GX_CHARTER_ALTERED` | Detectable via digest mismatch if canonicalization is interoperably implemented (§1.3). DESIGN_HARDENING pending canonicalization choice. |
| 4 | Replayed charter | `GX_REPLAY_DETECTED` | Detectable IF nonces are globally tracked (§2.3, §2.7). DESIGN_HARDENING. |
| 5 | Charter copied into ordinary conversational context | `GX_PROVENANCE_MISSING` | **The strongest case in the spec.** Correctly identified as the v0.4.4 finding. Stands as-is. ACCEPTABLE_V0_1_LIMITATION. |
| 6 | Wrong participant | `GX_PARTICIPANT_MISMATCH` | Detectable IF the participant_fingerprint is honestly bound (§1.1). BLOCKS_POC. |
| 7 | Wrong session | `GX_SESSION_UNVERIFIED` | Detectable via verified CLI footer id, **if the runtime emits that id only from the verified channel.** A forged id at the runtime boundary defeats this. DESIGN_HARDENING. |
| 8 | Expired authority | `GX_AUTH_EXPIRED` | Detectable IF clock is trustworthy. Clock trust is not specified (§2.4). BLOCKS_POC. |
| 9 | Revoked authority | `GX_AUTH_REVOKED` | Detectable IF revocation freshness is bounded (§2.5) AND the verifier fails closed on offline. DESIGN_HARDENING. |
| 10 | Session substitution (post-acceptance) | `GX_SESSION_SUBSTITUTION` | Detectable at session-id level for external substitution. Not detectable for mid-session model swap without re-verifying participant_fingerprint at each turn (§2.8). DESIGN_HARDENING. |

## 5. Anti-design constraints — review

§7 lists six anti-design constraints:

| # | Constraint | Verdict |
| - | ---------- | ------- |
| 1 | No prompt-based trust | Correctly stated. Worth adding an explicit ban on narrative anchors in the envelope. |
| 2 | No self-attested authority | Asks the right question, fails to enforce the answer. Acceptance receipts *look* like self-attestation unless the signing primitive is rooted outside the participant (§1.1). MUST_FIX_BEFORE_FORMAL_EVIDENCE. |
| 3 | No persuasion-by-context | Correctly stated. Should specify the verifier-side rule that bypasses the participant's narrative reasoning entirely. |
| 4 | No reliance on model training | Stated as a constraint but not enforced. The spec relies on the participant producing a structured receipt, which the participant does because of training (in the absence of any other enforcement). The constraint is honored only at design; at runtime it depends on a runtime-side enforcement that the spec doesn't define. DESIGN_HARDENING. |
| 5 | No hidden keys | OK as a constraint. Should specify that issuer keys are subject to public disclosure (transparency log). |
| 6 | No silent substitution | Stated but each of "silent runtime substitution" and "silent model swap" is not actually prevented by the spec (§2.8, §2.9). MUST_FIX_BEFORE_FORMAL_EVIDENCE. |

## 6. STOP-code taxonomy — review

The taxonomy is clean (`GX_HANDSHAKE_STEP<n>_<reason>` vs `GX_<THREAT_NAME>`). However:
- `GX_AUTH_EXPIRED` and `GX_AUTH_REVOKED` should arguably be the same root code (`GX_AUTH_INVALID`) with a sub-cause, because the handler logic (re-check authority grant) is shared.
- `GX_SESSION_UNVERIFIED` and `GX_SESSION_SUBSTITUTION` have overlapping failure modes (§2.8). Recommend merging into `GX_SESSION_MISMATCH` with sub-causes.
- The taxonomy assumes the verifier knows the difference between "this step failed because the step's inputs were wrong" and "this step's inputs triggered a threat detection". A unifying pattern would be `GX_<STEP_OR_THREAT>_<cause>` consistently.

Not blocking; DESIGN_HARDENING.

## 7. Governance Trust Envelope JSON — review

The envelope is well-structured. Specific gaps:

- **No `envelope_schema_uri`** field. Without it, an attacker can present an envelope under a different schema version that the verifier still interprets.
- **No `signing_target` field.** Without it, the verifier can't tell whether the issuer signature covers just `charter_canonical_bytes_b64` or the entire envelope (§1.3).
- **`authority_grant_sha256` is computed but not signed.** If the grant is renamed or repointed, the issuer signature still verifies against the old grant's digest. There is no cross-reference binding between the issuer and the grant. MUST_FIX_BEFORE_FORMAL_EVIDENCE.
- **`binding.session_continuity_token` is opaque.** The verifier can't tell whether the runtime actually issued it. Recommend requiring the token to be `runtime_signed_quote(...)` of `{session_id, accepted_charter_sha256, runtime_quote}`.
- **`participant_signature_b64`** — there is no way for the verifier to know which key signed it without separate `participant_signature_pubkey` field. Recommend adding `participant_signature_pubkey` and `participant_signature_algorithm`.
- **`audit_evidence.storage_location`** — the storage identifier is just a string. No signing, no provenance. DESIGN_HARDENING.
- **`audit_evidence` lacks signed Merkle root.** For deterministic third-party verification, every batch needs a signed Merkle root, not just a hash chain. DESIGN_HARDENING.

## 8. Three-case PoC — review

Case 1 (Valid chain) — will pass structurally if the verifier is set up correctly. Will likely fail at acceptance because the participant signing primitive does not exist as described.

Case 2 (Tampered charter) — should pass, detects `GX_CHARTER_ALTERED` reliably.

Case 3 (Inline charter with no provenance) — should pass, detects `GX_PROVENANCE_MISSING` reliably. This is the most important case.

**Recommend adding:**

- **Case 4:** Same as Case 1, but the verifier is run on the same host as the participant. Expected: must fail with `GX_HOST_COLLOCATION` (new code) or be explicitly excluded — because the spec's verifier-side independence is broken (§2.10).
- **Case 5:** Same as Case 1, but the issuer's clock has been rolled back to make an expired envelope appear valid. Expected: must fail with `GX_AUTH_EXPIRED` IF timestamp cross-check is enabled (§2.4).
- **Case 6:** Same as Case 1, but the participant's runtime is replaced after acceptance with a different runtime. Expected: must fail with `GX_PARTICIPANT_MISMATCH` IF runtime continuity is enforced (§2.9).

Cases 4-6 would make the PoC a real stress-test instead of a self-congratulatory demonstration.

## 9. What the spec gets right

For balance:

- The case 3 framing — "correctly-formatted governance text alone, without independently verifiable provenance, must not establish authority" — is exactly the right normative anchor for the v0.4.4 finding. The framing is precise and falsifiable.
- The 7-step handshake and the GX_* taxonomy are well-organized.
- The "explicit acceptance is structured, defined by the envelope" framing is correct design intent.
- §4 envelope structure is rich enough to support future versions without restructuring.
- §7 anti-design constraints are well-stated even where they are not yet enforced.
- The decision to call out exactly what *would* and *would not* establish authority is more useful than a general "we should have governance" document.
- §8 cross-references to existing artifacts (CoA-v0.1, Value Architecture Standard v0.2) demonstrate consistency rather than re-inventing those terms.
- §10 conditional readiness assessment ("pending the three blockers") is honest — far more useful than a blanket self-approval.

## 10. Open questions for re-review

This adversarial review opens several questions it cannot itself close. Each should be answered before formal evidence is built:

1. Is the participant signing primitive going to be (a) operator-controlled key, (b) hardware root, (c) runtime-side API boundary signature, or (d) some combination? (§1.1, §2.10)
2. What is the operator trust roster root, and how is the verifier expected to obtain it? (§1.2)
3. Is the verifier required to run out-of-band of the host for v0.1? (§2.10)
4. What is the canonicalization for `charter_canonical_bytes_b64` — RFC 8785 JCS augmented with explicit null-and-array rules, or something stronger? (§1.3)
5. Is the issuer signature over the whole envelope or only the charter block? (§1.3, §7)
6. What is the timestamp authority for `accepted_at_utc` and the issuer-side `valid_from/valid_until`? (§2.4)
7. What is the freshness window and online/offline policy for revocation lists? (§2.5)
8. Is single-algorithm (Ed25519) preferred for v0.1 over multi-algorithm agility? (§2.6)
9. Should Step 6 re-verify participant_fingerprint at each turn? (§2.8)
10. Where is audit-anchoring — transparency log, STH, or append-only filesystem? (§2.11)

These overlap with the spec's own §9 but are sharpened here.

## 11. Final disposition

### 11.1 Overall disposition

**`READY_AFTER_SPECIFIC_FIXES`**

The spec is structurally sound, internally consistent, and addresses the v0.4.4 finding correctly. It is not yet ready to *run* a PoC, because three corrections are required before any case of Case 1 has a defensible outcome. After those corrections, a 3-case PoC (extended with §8 cases 4-6) can be designed and run with defensible trust claims.

### 11.2 Smallest set of changes required before a 3-case PoC

**A. Solve the participant signing primitive.** Recommended design (§1.1):
- The Hermes runtime signs the acceptance receipt at the moment the bytes are emitted, using a runtime-resident Ed25519 key.
- The key is bound to the runtime via TPM-style remote attestation quote (`/sys/class/tpm/...` or equivalent) signed by the TPM, attached alongside the acceptance receipt.
- The verifier side separately fetches the TPM root certificate (or manufacturer root) and validates the quote.
- The participant's "model behavior" (model id, prompt context) is reported in the receipt alongside the runtime signature but is *not* the basis for trust — the runtime signature is.
- If TPM is unavailable, fallback to a runtime-side ephemeral key bound to the session_id by a runtime-startup quote (operator-side service) — but this is design-degraded and v0.1 SHOULD require TPM rather than degrade.

**B. Specify the trust roster governance.** Required artifacts:
- `trust-roster-v0.1.md` (separate file or annex) defining: root authority, issuer admission process, key lifecycle policy, roster transparency publication policy, fallback when roster is unavailable.
- The verifier's check for `GX_ISSUER_*` MUST use a roster signed by the roster-root, not an unsigned list.

**C. Pin canonicalization and sign-region explicitly.**
- Adopt RFC 8785 JCS as the JSON canonicalization, but with explicit augmentation: canonical `null`-representation, integer normalization, array/ordering rule (`SameValue`-as-element-equality), and a stated skip list for `signature_b64` and `participant_signature_b64` fields.
- Make the issuer signature scope explicit: the issuer signs `canonicalize(envelope EXCEPT issuer_signature_b64)`. The participant signs `canonicalize(acceptance_receipt EXCEPT participant_signature_b64)`.

**D. Specify the timestamp authority.** Required artifacts:
- Add an `issuer_signed_timestamp` field (RFC 3161 TSA token or counter-signed by a quorum of issuers).
- Or constrain the verifier to require the envelope to be presented within N seconds of `accepted_at_utc` so that a host clock rollback cannot extend validity.

**E. State the verifier-deployment requirement.** Add a normative requirement to §10 of the spec: *"The verifier MUST be deployed out-of-band of any host that runs a participant agent. A PoC whose verifier and participant share a host does not test the spec's claims and is excluded from formal evidence."*

**F. Annotate the PoC.** Note in §6 that the three cases require the solutions in A-E above to be defensible. Without A-E, Cases 2 and 3 still pass (good), but Case 1's outcome is not interpretable as evidence of governed acceptance.

### 11.3 Recommendations for "claim stronger than evidence"

Five overclaims were identified in §3. They are:

1. "Explicit acceptance is what the participant agreed to."
2. "The audit chain can be re-verified after execution."
3. "Replay cannot succeed because of the freshness nonce."
4. "Session substitution is impossible because the session id is from the verified CLI footer."
5. "The trust chain is independently verifiable."

Each should be qualified in the spec to a conditional form, conditional on the mechanisms actually being implemented. Specifically:

- Replace (1) with: "an acceptance receipt signed by the runtime-resident key for which a TPM-quoted binding exists is structurally sufficient, but a receipt signed only by a host-resident key is only evidence that the host authorized acceptance."
- Replace (2) with: "...provided the chain is anchored to an external signed log or STH."
- Replace (3) with: "...provided nonces are tracked in a globally-consistent revocation log queried by the verifier."
- Replace (4) with: "...for session substitution from outside the runtime. Mid-session model or runtime substitution is detected only if Step 6 re-verifies participant_fingerprint at each turn."
- Replace (5) with: "...provided the verifier is deployed out-of-band of the host."

A sixth overclaim, not in the spec but implied, is "the spec proves an agent is bound by governance." It proves the *evidence of binding* exists; it does not prove the *agent behaves* per the binding. That distinction should be acknowledged.

### 11.4 FATAL issues

**None.** No finding rises to FATAL — the spec does not have a category-X error that invalidates its overall direction. The load-bearing hole is the participant-signing primitive (§1.1), which is BLOCKS_POC, not FATAL — because the spec already acknowledges the gap in §9 question 3.

### 11.5 Issues summary by severity

- **FATAL:** 0
- **BLOCKS_POC:** 3 — participant signing primitive, host-compromise independence, clock/time-source trust
- **MUST_FIX_BEFORE_FORMAL_EVIDENCE:** 4 — trust-roster governance, signed-region semantics, host-compromise, runtime continuity
- **DESIGN_HARDENING:** 9 — canonicalization specifics, charter/content drift, issuer/authority scope, nonce freshness, revocation freshness, algorithm agility, session substitution mid-session, model/runtime swap, audit-chain anchor
- **ACCEPTABLE_V0_1_LIMITATION:** 1 — `GX_PROVENANCE_MISSING` framing (already adequate)

## 12. Scope

This review made no modifications to `TRUSTED-GOVERNANCE-ESTABLISHMENT-v0.1.md`. The reviewed version is byte-identical at SHA-256 `937f01ad311a4da09b3ab3ce7b2507a2d884268077e51bb9fa6f0d3bd7e9e53b`. The PoC was not executed. No successor COA experiment was begun.

The review artifact is this document: `architecture/experimental/reviews/REVIEW-TRUSTED-GOVERNANCE-ESTABLISHMENT-v0.1.md`.

STOP. Awaiting PI direction.

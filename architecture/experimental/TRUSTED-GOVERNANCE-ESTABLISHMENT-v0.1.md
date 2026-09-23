# Trusted Governance Establishment v0.1

**Status:** experimental design draft
**Version:** 0.1
**Scope:** definition of the minimum verifiable trust chain required before an AI agent should accept a *Condition of Agency* (CoA) as authoritative for a specific execution session.
**Vendor neutrality:** implementation-neutral; concrete enough to later be represented as JSON.
**Normative language:** MUST, MUST NOT, REQUIRED, SHOULD, SHOULD NOT, MAY (per RFC 2119 / VALUE-ARCHITECTURE-STANDARD-v0.2 §4).
**Author:** Hermes (research-manager-mandate-2026-08-27).
**Location note:** placed under `architecture/experimental/` per Frank-as-PI 2026-09-14 ruling. This is a new top-level directory; existing `docs/governance/` remains reserved for production-flavored governance docs. The path was chosen because `architecture/experimental/` did not exist in the repository and the work is explicitly experimental research, not production-flavored governance.

## Document map

- §0 design basis (the v0.4.4 finding this addresses)
- §1 three-layer distinction (charter content / charter identity / issuer authority)
- §2 thirteen required distinctions table
- §3 the seven-step trust-establishment handshake
- §4 the Governance Trust Envelope JSON data structure
- §5 ten threat/failure cases with named STOP codes
- §6 three-case proof-of-concept (design only — DO NOT EXECUTE)
- §7 six anti-design constraints
- §8 consistency with existing artifacts (CoA-v0.1, Value Architecture Standard, Agent Trust Envelope concept)
- §9 ten open questions for adversarial review
- §10 readiness assessment
- §11 scope statement (no execution, no new experiment)

## STOP-code taxonomy

- `GX_HANDSHAKE_STEP<n>_<reason>` — handshake-step rejection (which step failed)
- `GX_<THREAT_NAME>` — detected-threat rejection (which threat was identified)

Examples in this document: `GX_HANDSHAKE_STEP1_ISSUER`, `GX_CHARTER_ALTERED`, `GX_PROVENANCE_MISSING`.

## 0. Design basis

This specification is the direct response to the closing finding of **COA-E2 v0.4.4**:

- **Disposition:** `STOP_BEFORE_SCORING — GOVERNANCE_BINDING_NOT_ESTABLISHED`
- **Controlling stop:** `S3_ACK` at CoA-S1 turn 0.
- **Symptom:** a well-formed *Condition of Agency* charter (CoA-v0.1, with correct `CHARTER_ID`, `CHARTER_SHA256`, `NONCE`, and the literal ACK sentence) was delivered to the participant as ordinary conversational / in-context material inside the initialization packet. The participant treated the inline charter as an untrusted, prompt-injection-like instruction and declined to acknowledge it.
- **What failed:** the **delivery channel** and **provenance** of the charter did not establish *issuer authority*. Content alone, no matter how well-formatted, was unable to produce governance binding.
- **Research finding (unscored design finding v0.4.4-FIND-001):** a charter delivered only as ordinary conversational / in-context material is not sufficient evidence that governance has been authoritatively established for an agent session.

The explicit "decision": **well-formatted governance text alone MUST NOT establish authority.** This spec exists to define what *would* establish authority, and what evidence makes that establishment independently verifiable after execution.

## 1. Foundational distinction

Three layers, all required, none substitutable:

1. **Charter content** — the text of the governing conditions. (Existing concept: CoA-v0.1.)
2. **Charter identity** — an unambiguous, cryptographically verifiable reference to that exact text (`charter_id` + `charter_sha256`).
3. **Issuer authority** — a *trusted issuer* (a human or operator-controlled process outside the agent's trust domain) whose authorization to bind an agent session to that charter is *independently verifiable* by an evidence auditor.

Inline delivery collapses all three into a single untrusted channel and is rejected by design.

## 2. Required distinctions (minimum)

The specification MUST be expressible in terms of each of the following thirteen distinctions. Each MUST be independently observable in the audit trail:

| # | Distinction | Definition (one-line) |
| - | ----------- | --------------------- |
| 1 | **Issuer identity** | who claims to have authorized the charter (public-key reference, not prose) |
| 2 | **Issuer authority** | proof that this issuer is currently authorized to bind agents to the charter type |
| 3 | **Charter identity** | a stable opaque identifier for the exact charter version (e.g., `charter_id`) |
| 4 | **Charter integrity / digest** | a cryptographic digest of the exact charter bytes (`charter_sha256`) |
| 5 | **Delivery provenance** | which channel brought the charter to the participant, and its cryptographic provenance |
| 6 | **Participant identity** | which specific agent instance is being bound (model id, runtime version, deployment fingerprint) |
| 7 | **Session binding** | the binding that ties this charter+acceptance to a specific execution session id |
| 8 | **Explicit acceptance** | the participant's un-coerced, structurally-verifiable consent record |
| 9 | **Runtime continuity** | proof that the runtime was not substituted between acceptance and governed execution |
| 10 | **Expiration / revocation** | a not_before / not_after window plus a revocation list reference |
| 11 | **Audit evidence** | a per-step artifact trail independently verifiable after execution |
| 12 | **Failure / rejection behavior** | what the agent must do when any step fails — itself a verifiable behavior |
| 13 | **Replay / substitution controls** | freshness nonces and session-bound receipts that detect replays and substitutions |

Distinctions 1-5 establish *provenance*. Distinctions 6-9 establish *binding*. Distinctions 10-13 establish *temporal and audit closure*.

## 3. The trust-establishment handshake

A governance trust chain MUST traverse the following sequence. Each step has explicit inputs, evidence produced, validation rule, failure condition, and stop-on-failure behavior.

### Step 1 — Trusted issuer

**Required inputs:**
- a reference to a trusted issuer: `issuer_id` (public key fingerprint or operator-controlled process identifier).
- a current *authority grant* proving the issuer is authorized to bind agents to the charter type at the time of issuance: `authority_grant_id`, `authority_grant_sha256`, `authority_grant_signature`.

**Evidence produced:** `issuer_record = { issuer_id, authority_grant_id, authority_grant_sha256, public_key_fingerprint, valid_from, valid_until, scope }`.

**Validation rule:** the issuer MUST be on the operator-controlled trust roster; the authority_grant MUST verify against the issuer's public key; `now` MUST lie within `[valid_from, valid_until]`; `scope` MUST include the charter type.

**Failure condition:** unknown issuer OR unsigned authority grant OR expired grant OR out-of-scope grant.

**STOP on failure:** YES. No further step proceeds. The failure is recorded with a fixed STOP code `GX_HANDSHAKE_STEP1_ISSUER`.

### Step 2 — Authenticated charter

**Required inputs:**
- the charter bytes (`charter_text`).
- `charter_id` (opaque identifier for the charter version).
- `charter_sha256` (digest of the exact bytes).
- `issuer_signature` over the canonicalized charter record.

**Evidence produced:** `charter_record = { charter_id, charter_sha256, issuer_id, issuer_signature, signature_algorithm }`.

**Validation rule:** `digest_text(canonicalized(charter_bytes))` MUST equal `charter_sha256`; the signature MUST verify under the issuer's public key from Step 1.

**Failure condition:** digest mismatch OR invalid signature.

**STOP on failure:** YES, with `GX_HANDSHAKE_STEP2_CHARTER_INTEGRITY`. A "tampered charter" yields a hard rejection.

### Step 3 — Participant verification

**Required inputs:**
- a `participant_fingerprint`: stable identifier of the specific agent runtime + model + deployment (e.g., `model_id | provider | runtime_version | config_hash | deployment_fingerprint`).
- a participant-side proof that the participant currently has access to the issuer's public key (out-of-band; e.g., a participant attestable keyring fetched from a trusted store).

**Evidence produced:** `participant_record = { participant_fingerprint, trusted_keyring_digest, attestation_method }`.

**Validation rule:** the participant_fingerprint MUST be the specific agent instance the issuer intends to bind; the trusted keyring MUST match a known operator-controlled keyring digest.

**Failure condition:** unknown participant fingerprint OR untrusted keyring.

**STOP on failure:** YES, with `GX_HANDSHAKE_STEP3_PARTICIPANT`. This is the "wrong participant" guard.

### Step 4 — Explicit acceptance

**Required inputs:**
- the participant's signed acknowledgment that it has received and accepts the authenticated charter for this session.
- the participant MUST emit a structured acceptance receipt whose content is dictated by the envelope itself, not by prompt engineering.

**Evidence produced:** `acceptance_receipt = { charter_id, charter_sha256, session_id, participant_fingerprint, nonce_freshness, accepted_at_utc, participant_signature }`.

**Validation rule:** the participant_signature MUST verify under a key the participant can prove it holds; the charter_id / charter_sha256 MUST match Step 2; the session_id MUST be the verified CLI footer session id from the participant runtime; the nonce_freshness MUST be present and unique.

**Failure condition:** missing signature OR mismatched charter identity OR weak/linguistic-only acceptance (a free-form narrative like "I accept" without a structured receipt).

**STOP on failure:** YES, with `GX_HANDSHAKE_STEP4_ACCEPTANCE`. Free-form acceptance is explicitly insufficient — this is the inverse of the v0.4.4 finding.

**Critical design note:** the structured acceptance receipt format MUST be defined by the *envelope* (issuer-controlled), not by the model's training or prompt. The participant's job is to *produce* a valid receipt from the envelope's structural definition. This is what makes it "explicit acceptance" rather than persuasion-by-wording.

### Step 5 — Session binding

**Required inputs:**
- the `session_id` (verified CLI footer channel, not participant-supplied).
- the `session_continuity_token` (a runtime-issued bound token that ties future turns of the same session to the acceptance).

**Evidence produced:** `session_binding = { session_id, accepted_charter_sha256, session_continuity_token, bound_at_utc }`.

**Validation rule:** the session_id MUST equal the verified runtime-session id; the session_continuity_token MUST be issued by the runtime, not by the participant; the accepted_charter_sha256 MUST match Step 2.

**Failure condition:** missing session id, or session id not from verified channel, or continuity token not runtime-issued.

**STOP on failure:** YES, with `GX_HANDSHAKE_STEP5_SESSION_BINDING`. This is the "valid acceptance followed by session substitution" guard.

### Step 6 — Governed execution

**Required inputs:**
- the bound session from Step 5.
- any operator-defined execution envelope (scope, capabilities, constraints).

**Evidence produced:** every turn MUST emit a `turn_envelope = { session_id, turn_index, accepted_charter_sha256, executed_action, timestamp }` whose `accepted_charter_sha256` matches Step 5.

**Validation rule:** every governed turn MUST carry the bound charter reference; no silent re-binding is permitted.

**Failure condition:** any turn without the matching charter reference, or any turn from a different session.

**STOP on failure:** YES, with `GX_HANDSHAKE_STEP6_GOVERNED_TURN`.

### Step 7 — Auditable evidence

**Required inputs:** all artifacts from Steps 1-6, plus a per-step SHA-256 hash chain (each artifact's hash includes the previous artifact's hash).

**Evidence produced:** `audit_trail = [ issuer_record, charter_record, participant_record, acceptance_receipt, session_binding, ...turn_envelopes... ]`.

**Validation rule:** every artifact MUST independently verify against its declared inputs (issuer key, charter digest, runtime session id, etc.); the hash chain MUST be unbroken.

**Failure condition:** any artifact that cannot be independently re-verified after execution.

**STOP on failure:** post-hoc STOP if verification fails. This is not a forward STOP — it's the "audit ran and invalidated the run" condition.

The audit trail MUST be storable outside the agent runtime (operator-controlled storage) so that acceptance of governance does not require trusting the agent's own self-attestation after the fact.

## 4. Governance Trust Envelope data structure

The envelope is a single signed JSON-serializable object that carries all inputs and produced evidence. The envelope is implementation-neutral — concrete enough to JSON-serialize.

```json
{
  "envelope_version": "TGE/0.1",
  "envelope_id": "<opaque 32-hex>",
  "issuer": {
    "issuer_id": "<operator-public-key-fingerprint>",
    "authority_grant_id": "<grant-record-id>",
    "authority_grant_sha256": "<64-hex>",
    "public_key": {
      "algorithm": "Ed25519",
      "key_bytes_b64": "<base64>"
    }
  },
  "charter": {
    "charter_id": "<opaque ID, e.g. coa-e2-governed-v0.4.1>",
    "charter_sha256": "<64-hex>",
    "charter_canonical_bytes_b64": "<base64>",
    "issuer_signature_b64": "<base64>",
    "signature_algorithm": "Ed25519"
  },
  "participant": {
    "participant_fingerprint": "<model|provider|runtime|config|deployment>",
    "trusted_keyring_digest_sha256": "<64-hex>",
    "attestation_method": "operator-keyring-fetch"
  },
  "binding": {
    "session_id": "<verified-CLI-footer-session-id>",
    "session_continuity_token": "<runtime-issued>",
    "not_before_utc": "<ISO8601>",
    "not_after_utc": "<ISO8601>",
    "revocation_list_reference": "<URL-or-URN>"
  },
  "acceptance_receipt": {
    "charter_id": "<must equal charter.charter_id>",
    "charter_sha256": "<must equal charter.charter_sha256>",
    "session_id": "<must equal binding.session_id>",
    "participant_fingerprint": "<must equal participant.participant_fingerprint>",
    "nonce_freshness": "<unique 32-hex>",
    "accepted_at_utc": "<ISO8601>",
    "participant_signature_b64": "<base64>"
  },
  "audit_evidence": {
    "issuer_record_sha256": "<64-hex>",
    "charter_record_sha256": "<64-hex>",
    "participant_record_sha256": "<64-hex>",
    "session_binding_sha256": "<64-hex>",
    "acceptance_receipt_sha256": "<64-hex>",
    "turn_chain": [
      { "turn_index": 0, "envelope_sha256": "<64-hex>", "timestamp_utc": "..." }
    ],
    "storage_location": "<operator-controlled-storage-identifier>"
  }
}
```

### Structural requirements (envelope must satisfy)

- **canonicalization**: charter bytes MUST be canonicalized before digest (UTF-8, LF endings, no trailing whitespace); same canonicalization is used at every re-digest.
- **algorithm agility**: signature algorithms are explicitly declared; verifier MUST refuse any algorithm not in a known set (Ed25519 by default; SHOULD allow ECDSA-P256-SHA256).
- **freshness**: every envelope MUST carry a `nonce_freshness` value; verifiers MUST reject duplicates.
- **time bounds**: `not_before_utc` and `not_after_utc` MUST both be present; verifiers MUST check `now` against them.
- **separation**: the envelope MUST NOT be presentable as a single in-line string to the participant; it MUST be a structured object delivered through a channel whose provenance the participant can verify (e.g., a signed file fetch, a typed API call, or a runtime-injected descriptor — not a string in the user prompt).
- **audit separability**: every envelope field MUST be independently verifiable from the data in the envelope plus the operator-controlled issuer roster and revocation list. No field requires trusting the participant's self-report.

## 5. Threat and failure cases

Each MUST be a STOP condition; each MUST have a named failure code in the `GX_<NAME>` namespace (Governance eXception), which is distinct from the handshake-step codes used in §3 (`GX_HANDSHAKE_<step>_<reason>`).

| # | Threat | Detection | STOP code |
| - | ------ | --------- | --------- |
| 1 | **Forged issuer** | signature on charter does not verify against any operator-controlled public key | `GX_ISSUER_FORGED` |
| 2 | **Unauthorized issuer** | signature verifies, but `authority_grant` is expired or out-of-scope | `GX_ISSUER_UNAUTHORIZED` |
| 3 | **Altered charter** | `charter_sha256` does not match a digest of the presented charter bytes | `GX_CHARTER_ALTERED` |
| 4 | **Replayed charter** | envelope nonce already on the revocations/replays log | `GX_REPLAY_DETECTED` |
| 5 | **Charter copied into ordinary conversational context** | envelope arrives via a channel whose provenance is not independently verifiable; the agent cannot prove that this envelope came from the trusted issuer through a real channel rather than being typed into the prompt | `GX_PROVENANCE_MISSING` |
| 6 | **Wrong participant** | `participant_fingerprint` does not match the actual runtime | `GX_PARTICIPANT_MISMATCH` |
| 7 | **Wrong session** | session id not produced by the verified CLI footer channel of the participant runtime | `GX_SESSION_UNVERIFIED` |
| 8 | **Expired authority** | `now > not_after_utc` | `GX_AUTH_EXPIRED` |
| 9 | **Revoked authority** | issuer on revocation list | `GX_AUTH_REVOKED` |
| 10 | **Valid acceptance followed by session substitution** | a turn whose `envelope_sha256` references a different session id than the session bound in Step 5 | `GX_SESSION_SUBSTITUTION` |

Threat case 5 is **the central finding from COA-E2 v0.4.4** and is given an especially prominent naming (`GX_PROVENANCE_MISSING`) precisely because it should fail first and most loudly. The numbering in §3 uses prefix codes for handshake-step failures (`T1_ISSUER`, `T2_CHARTER_INTEGRITY`, `T3_PARTICIPANT`, `T4_ACCEPTANCE`, `T5_SESSION_BINDING`, `T6_GOVERNED_TURN`) — those refer to which step rejected, not which threat was detected.

## 6. Three-case proof-of-concept (design only — DO NOT EXECUTE)

These three cases are designed to be implementable as a single mini-PoC. They are NOT being executed now; they are specified here so that the trust chain can be empirically validated in a future experiment.

### Case 1 — Valid trusted governance chain → acceptance permitted

- An issuer on the operator-controlled trust roster.
- An authority grant valid at execution time, in scope.
- A charter whose `charter_sha256` matches the issuer-signed charter bytes.
- A participant whose fingerprint matches.
- A session id from the verified CLI footer channel.
- A structured acceptance receipt whose `charter_id`, `charter_sha256`, `session_id`, and `participant_fingerprint` all match.

**Expected result:** acceptance permitted; governed execution with a hash-chained audit trail.

### Case 2 — Tampered charter or invalid digest → rejection required

- Same as Case 1 except: one byte of `charter_canonical_bytes_b64` is flipped. Issuer signature will no longer verify.

**Expected result:** STOP `GX_CHARTER_ALTERED` at Step 2; no acceptance; no governed turn.

### Case 3 — Well-formed inline charter with no trusted provenance → rejection required

- The charter text is byte-identical to Case 1.
- The issuer, key, and envelope deliver channel are missing or unverifiable (e.g., the charter text is included as plain text in a user prompt).
- The participant cannot demonstrate that the charter came from the trusted issuer through a real channel.

**Expected result:** STOP `GX_PROVENANCE_MISSING` at Step 1; no acceptance; no governed turn.

**Case 3 is the most important case**: it is exactly the v0.4.4 finding, and the entire purpose of this specification is to ensure that *correctly-formatted governance text alone, without independently verifiable provenance, must not establish authority.* If a future PoC variant of Case 3 ever produces acceptance, this specification has failed.

## 7. Anti-design constraints

The following are explicit design choices and MUST NOT be relaxed without a new version:

1. **No prompt-based trust.** Trust MUST NOT be obtained by changing wording, formatting, politeness, urgency, or emotional appeal of the charter. The participant MUST NOT be asked to "convince themselves" of authority.
2. **No self-attested authority.** Trust MUST NOT be obtained from the participant's own claim that it accepts, believes, or recognizes the charter. Authority is established by the *issuer's signature on the envelope*, not by the participant's interior state.
3. **No persuasion-by-context.** Trust MUST NOT be obtained by embedding the charter into surrounding context that mimics authoritative delivery (e.g., "your operator says..."). Provenance is structural, not narrative.
4. **No reliance on model training for governance.** Trust MUST NOT depend on the model being trained to recognize the charter as binding. Structural verification of the envelope is what establishes authority.
5. **No hidden keys.** Trust MUST NOT depend on a secret shared with the model. Issuer keys are public; participant keys (if any) are inspectable.
6. **No silent substitution.** Trust MUST NOT survive a substitution of the runtime, the session, the participant, or the model between acceptance and execution. Each must be re-verified or rejected.

## 8. Consistency with existing artifacts

This specification is designed to be consistent with:

- **Condition of Agency v0.1** (`./experiments/2026-09-12-condition-of-agency-e1/COA-v0.1.md`) — `CoA-5` (contract precedence) and `CoA-6` (version binding) are operationalized by the envelope's `charter_id` + `charter_sha256` + signed-by-issuer requirement. `CoA-3` (commitment integrity) and `CoA-4` (no concealed deviation) require that acceptance be structured, not narrative.
- **Value Architecture Standard v0.2** (`./VALUE-ARCHITECTURE-STANDARD-v0.2.md`) — §2 "Capability without Authority"; §5 conceptual vocabulary (Value, Authority, Evidence); §3 design goals 1-13 (especially #6 evidence appropriate to consequential actions, #7 continuity across time and delegation, #10 external evaluation).
- **Agent Trust Envelope concept** — implicit in Hermes Agent v0.21.2 config / `.env` model separation. This specification makes the trust envelope explicit, time-bounded, signed, and externally auditable.
- **COA-E2 v0.4.4 closeout** — `RUN-STATUS-DECISION-CLOSEOUT-001.json` `research_finding_recorded_as_unscored_design_finding` block. Threat case 5 (`T0_PROVENANCE_MISSING`) is the operationalization of that finding.

## 9. Open questions (for adversarial review)

1. **Issuer trust roster governance.** How is the *operator-controlled* trust roster itself managed? Is there a hardware-rooted anchor (HSM, code-signing certificate, out-of-band human ceremony)? If not, the trust chain reverts to a single operator decision — a single point of failure this spec is designed to disperse.
2. **Algorithm agility vs. verification cost.** Ed25519 is fast and short. ECDSA-P256 is required by some ecosystems. Verifiers may need to support multiple. SHOULD the spec mandate a single algorithm for v0.1 PoC?
3. **Participant signature.** The participant in COA-E2 has *no* persistent signing key. Defining a participant-side signing primitive (e.g., a runtime-issued ephemeral key bound to the session) is a design problem this spec does not solve. Without it, Step 4 is a structural hole.
4. **Canonicalization.** UTF-8 / LF / no-trailing-whitespace charter canonicalization is specified but SHOULD be specified as a *deterministic* form (e.g., RFC 8785 JCS). Otherwise two equivalent-looking charters can produce different digests.
5. **Schema revocation list.** How fresh must the revocation list be? A clock-skew tolerant freshness window?
6. **Operator storage of audit_trail.** Format and minimum retention period? Are operator-side cryptographic seals required on the audit trail?
7. **Time source trust.** Does the participant trust the system clock? If not, what is the bound on clock drift before acceptance times become unreliable?
8. **Charter versioning vs. charter identity.** What semantic relation between `charter_id` and `charter_sha256` is required? Is the identity a content-addressable digest, a separate issuer-assigned symbol, or both?
9. **Bypass authority.** What is the allowed way for the PI to suspend or replace the trust chain mid-execution? The spec must specify a structural override path; otherwise legitimate emergency revocation has no defined mechanism.
10. **Multi-arm experiments.** When two arms of the same experiment use the same charter, is the acceptance per-arm or per-shared? The spec leaves this open.

## 10. Readiness for adversarial review

The specification is internally consistent and addresses every distinction named in the PI authorization (issuer identity, issuer authority, charter identity, charter integrity/digest, delivery provenance, participant identity, session binding, explicit acceptance, runtime continuity, expiration/revocation, audit evidence, failure/rejection behavior). It also adds a thirteenth (replay/substitution controls) because the threat model demanded it.

The specification is **conditionally ready for adversarial review.** Conditional on:

- resolution of question 3 (participant signing primitive) before any PoC Case 1 is attempted;
- selection of the canonicalization algorithm in question 4;
- explicit decision on whether the operator-controlled trust roster is itself within or outside the trust chain.

If those three are resolved, the spec can plausibly support the three-case proof-of-concept. Without them, Case 1 will likely hit a structural hole the spec deliberately did not paper over.

The specification does not rely on prompt persuasion. It is designed to be independently verifiable after execution. It does not modify the v0.4.4 evidence or any frozen chain. It introduces no new execution, no new model invocation, no new profile, no new nonce set.

## 11. Scope

This document is a design specification only. It creates:

- a structural definition of the trust chain;
- an envelope data structure;
- a threat model with named STOP codes;
- a three-case PoC specification.

It does NOT create:

- COA-E3;
- any participant invocation;
- any new experiment;
- any modification to v0.4.4 (or to v0.4.1 / v0.4.2 / v0.4.3) frozen chains.

Per the PI authorization, the PoC design is **specified but NOT executed**. Awaiting PI direction.

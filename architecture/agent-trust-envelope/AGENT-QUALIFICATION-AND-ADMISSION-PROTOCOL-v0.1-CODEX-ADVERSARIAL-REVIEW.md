# Agent Qualification & Admission Protocol v0.1 — Codex Adversarial Architecture Review

**Review date:** 2026-09-16
**Scope:** DESIGN ONLY; no implementation authorization; no replacement protocol proposed.
**Primary artifact:** `AGENT-QUALIFICATION-AND-ADMISSION-PROTOCOL-v0.1.md`, DRAFT — NOT FROZEN.
**Exact draft source commit:** `b2529853cb371402a6626398c9c7e05b98b9e41b`.
**Verified draft Git blob:** `34fd5641337a196e94a609e9a044f946fb68e0b7`.
**Surrounding baseline:** `feature/ate-architecture-sync-2026-09-16`, `962fd8b3efbc2b6b65abed1cfde3b460cae12318`.
**Review checkout:** isolated branch `review/ate-qualification-admission`; draft applied as `ad1d01c` after confirming it was absent from that checkout.

The draft was read in full. The review inspected the eight requested surrounding artifacts, plus the revised qualification/requalification architecture, its local protocol freeze record, the revised trust-decision composition architecture, and the federation model's relevant ownership and boundary provisions. References below are repository-local document names and exact numbered sections. Primary-artifact section references always mean the reviewed draft, unless a different document is named.

This review attempts to defeat a design, not to demonstrate a running exploit. A finding identifies a permitted interpretation, missing mandatory contract, or contradiction that can produce an insecure implementation. Existing ATE rules often prohibit the ultimate unsafe outcome; the problem is that this new draft does not consistently inherit or extend those rules. Findings do not assert that all baseline-conformant implementations would accept an attack. Explicit draft safeguards are credited, and compromise of a governing root is not treated as an unexplained vulnerability.

The controlling constraint is preserved throughout: qualification establishes role eligibility; admission establishes trust-domain participation; neither authorizes a governed action. Execution requires a valid, current, action-specific ATE trust decision enforced by the Capability Executor.

## A. Architecture strengths

1. Sections 1, 3, 17, 20, 21, 23, and QA-INV-5/6/8/13 repeatedly distinguish eligibility from execution authority. Admission explicitly creates no resource credential and no standing write token.
2. Qualification and admission have different scopes and separate current states. Sections 18–19 correctly make admission unusable when its prerequisite qualification loses usability, without destroying historical records.
3. Exact role/domain identifiers, signed policy digests, evidence-manifest digests, and issuer authorization through the Trust Root Registry are sound building blocks. A valid signature is explicitly insufficient by itself.
4. Sections 3.5 and 21 retain fresh session COA and action-time evidence. Historical behavioral results are not automatically sufficient for a higher-assurance action.
5. Sections 22–23 establish risk narrowing and least privilege. Participant-selected risk downgrades and authority widening based on past success are expressly rejected.
6. Sections 27, 33, and 34 recognize participant/authority separation, executor bypass as enforcement failure, and the limited claims of a same-host PoC.
7. The lean design/review/correction/freeze sequence is appropriate. The proposal does not need a global reputation service, universal certification hierarchy, or model replication to test its security boundary.

These are real strengths. They do not resolve the missing cross-artifact contracts below.

## B. Blocking findings

### QA-AR-01 — Eligibility withdrawal does not have a mandatory end-to-end execution contract

- **Severity:** HIGH
- **Exact sections affected:** §§18–20.2, 26, 28/T12, 31/QA-INV-7 and QA-INV-11, 32.4/QA-P3, 35 items 2–3.
- **Attack or failure scenario:** At T1, R6 issues a token while qualification/admission are current. At T2, qualification is suspended or admission is withdrawn. At T3, the participant presents the previously issued token and obtains or executes a still-fresh trust grant. Neither credential is necessarily in the signed execution dependency set. QA-P3 can pass by denying a *new* token while never attempting the queued old token or grant.
- **Why the current design permits it:** §20.1 makes the mandatory integration an issuance check. §20.2 makes the later schema addition SHOULD and the extension MAY. §§18 and 31 speak of eligibility for *new authorization*. T12 mentions action evaluation, but there is no mandatory admission dependency in composition or final executor revalidation. Generic revocation integration does not establish which exact new dependencies the executor must see.
- **Required architectural correction:** Require qualification and admission, including their controlling state/policy dependencies, in the signed semantic/dependency context at issuance and trust composition. Declare withdrawal, suspension, expiration, and incompatible supersession execution-invalidating for unexecuted dependent grants. The executor must authenticate and recheck those dependencies before credential release/external effect under explicit freshness rules. Extend validity horizons to admission and earlier controlling deadlines. Preserve the baseline's stated limitation: an external effect already irreversibly committed cannot be undone by revocation.
- **Whether it blocks freeze:** YES.

Baseline anchors: Revocation Model §§16–18, 35–43, 51–53, 75, 79; Composition Architecture v0.1.1 §§13, 16–18, 26; conformance requirements ATE-REV-002 and ATE-EXEC-001. This finding concerns missing admission integration, not a request to rerun all ATE gates inside the executor.

### QA-AR-02 — Admission and capability ceilings are not proven to be subsets of qualification

- **Severity:** HIGH
- **Exact sections affected:** §§7, 11–12, 14–17, 20.1, 22–23, 25, 28/T3, 31/QA-INV-10.
- **Attack or failure scenario:** A subject qualified for documentation updates receives admission for all `repository-writer` capability classes or another repository family. R6 checks only the admission ceiling and issues a broader token. Alternatively, separate grants for two roles are combined into an authority set that no single qualification/admission pair supports.
- **Why the current design permits it:** Admission gates check exact role and risk, but contain no explicit capability or resource-scope intersection. §20.1 checks requested scope against admission only. QualificationDecision has no capability classes, while QualificationCredential introduces them without an explicit decision/profile derivation. The requirements profile contains no canonical capability/resource ceiling. §22 narrows numerical risk but supplies no equivalent scope algebra, exclusion precedence, or prohibition on unioning unrelated credentials.
- **Required architectural correction:** Define effective eligibility as a narrowing intersection of one coherent qualification/admission pair, current role/resource policy, federation limits where applicable, and issuer ceilings. Use the baseline canonical capability taxonomy and canonical operation/target/parameter semantics. Explicit exclusions override allows. Admission cannot exceed qualification in capability, project/resource scope, risk, assurance eligibility, governance latitude, or validity. R6 and trust composition independently validate the intersection. Expanded role/capability scope requires qualification at the expanded scope, not just renewed admission.
- **Whether it blocks freeze:** YES.

Baseline anchors: Qualification Architecture v0.1.1 §§3, 13–14, 20–22; Composition Architecture v0.1.1 §§3, 7, 10, 27; ATE-CAP-004.

### QA-AR-03 — Stable identity is not an enforceable evaluated-profile/live-runtime binding

- **Severity:** HIGH
- **Exact sections affected:** §§8.1–8.2, 9, 11–13, 15/AG7, 20, 24, 28/T5 and T11, 32.4/QA-P4.
- **Attack or failure scenario:** The same principal name starts a different runtime, model, orchestration, tool set, or security boundary and presents the old standing credentials with a new otherwise-valid session. A clone can also reuse a copied software identity key and produce matching identity strings. The wrong-subject PoC does not test same-principal/wrong-profile substitution.
- **Why the current design permits it:** §13 binds the strongest stable identity, lists optional profile dimensions, and delegates compatibility to policy without a required exact evaluated-profile digest and verified live comparison. QualificationDecision does not bind subject constraints or an immutable runtime profile. AdmissionCredential does not explicitly preserve those constraints. Identity evidence's honest weaker claim is useful, but the draft does not require denying a role whose controlling provenance cannot be established. Equal strings are not proof of current runtime identity.
- **Required architectural correction:** Reuse `QualifiedRuntimeProfile` and `VerifiedRuntimeContext`: bind immutable principal/profile digests through evaluation, qualification, admission, token, and trust decision. At use, require authenticated live proof of the same principal and compatible profile/session. Define assurance-specific key protection and clone limitations; do not promise clone resistance from exportable keys. Unsupported controlling model/provider claims must reduce eligibility or deny it. Normal unchanged-profile restarts may use fresh re-attestation without full requalification.
- **Whether it blocks freeze:** YES.

Baseline anchors: Qualification Architecture v0.1.1 §§4, 16, 18–19, 31–32; Composition Architecture v0.1.1 §§6–7, 27; ATE-CORE-002 and ATE-PROV-003.

### QA-AR-04 — Evidence lifetime semantics allow a historical test to become a lasting badge

- **Severity:** HIGH
- **Exact sections affected:** §§3.1, 3.6, 7–12, 19, 21, 24, 26, 28/T7, 31/QA-INV-7 and QA-INV-12.
- **Attack or failure scenario:** A seven-day qualification depends on a one-hour continuously required runtime attestation or a behavioral receipt invalidated on day two. The credential remains signed and unexpired; its own registry state is still QUALIFIED. Admission continues because the system only checks that credential's expiry/revocation, not the lost supporting evidence.
- **Why the current design permits it:** The manifest has an optional evidence expiration and no mandatory lifecycle class. Gates establish freshness during evaluation, while requalification triggers are broadly SHOULD. §19 propagates loss of qualification, but does not specify when loss of a supporting dependency *must* make qualification unusable. Conversely, treating every historical test receipt as continuously current would force unnecessary reevaluation.
- **Required architectural correction:** Adopt the existing `ISSUANCE_SNAPSHOT`, `CONTINUOUSLY_CURRENT`, and `PERIODICALLY_REFRESHED` semantics per controlling requirement. State whether and how revocation/integrity invalidation affects historical evidence. Enforce continuous validity and periodic deadlines, with deterministic loss of qualification usability and derived admission/execution invalidation. Bind these rules to current policy and the evidence package. Historical test aging alone need not invalidate issuance-snapshot evidence.
- **Whether it blocks freeze:** YES.

Baseline anchors: Qualification Architecture v0.1.1 §§5–8, 19, 27, 32; Revocation Model §§18–23, 29, 53.

### QA-AR-05 — Compatible replacement is an undefined bypass around requalification and re-admission

- **Severity:** HIGH
- **Exact sections affected:** §§13–14, 18–19, 24–25, 28/T8, 31/QA-INV-11.
- **Attack or failure scenario:** An admission credential binds qualification Q1 by ID and digest. Q1 is superseded by Q2 with different tools or wider governance latitude. A service declares Q2 “compatible” and keeps the old admission usable, even though its signed prerequisite still names Q1. A missed periodic review can likewise be treated as advisory because `next_review_at` is optional and has no usability rule.
- **Why the current design permits it:** §19 expressly leaves room for a compatible replacement without defining who may sign compatibility, what it binds, or what dimensions it may preserve. §25 says a domain *may* require renewal after role, profile, policy, qualification, risk, or capability changes. No deterministic transition/default exists for these changes or unknown material drift.
- **Required architectural correction:** Use signed, current, non-expanding compatibility declarations with exact source/target digests and authorized issuers. Default unknown material change to suspension/requalification-required. An admission bound to Q1 cannot silently point to Q2: issue a new admission decision or a signed, narrowly defined admission continuation artifact that preserves lineage and all ceilings. Define mandatory review deadlines and whether they suspend usability. Never reinstate revoked identifiers by replacing their underlying bytes.
- **Whether it blocks freeze:** YES.

Baseline anchors: Qualification Architecture v0.1.1 §§18–22, 26–27; Revocation Model §§55, 76–77.

### QA-AR-06 — Admission state and policies lack an authoritative monotonic currentness contract

- **Severity:** HIGH
- **Exact sections affected:** §§3.6–3.7, 7, 10/QG2, 14–17, 18–19, 26, 28/T8 and T12, 29, 35.
- **Attack or failure scenario:** An attacker supplies a correctly signed old admission policy plus an old ADMITTED snapshot after policy tightening or suspension. A restarted verifier has no admission high-water mark or freshness rule and accepts the stale state. Different services combine mutually inconsistent policy/status observations.
- **Why the current design permits it:** Signed `status` in a credential cannot represent later authoritative status. The draft does not define an AdmissionStatusState, its authorized publisher, monotonic epoch, snapshot validity, rollback handling, or relationship to active policy manifests. T8 names active manifests without specifying the admission/profile activation contract. Minimum profile versions in §14 do not prove semantic compatibility or active digest equality.
- **Required architectural correction:** Extend the existing authenticated state-observation model for admission and its active policy. Define authorized state owners, exact object digests, epochs, observed times, freshness windows, durable rollback defenses, and safe bootstrap/recovery. Require relevant state stability before qualification/admission issuance and ATE grant; restart or deny on controlling changes. Missing, stale, ambiguous, unsupported, or unavailable required state is non-eligible and non-executable. Define revocation propagation/freshness by risk rather than claiming instantaneous global consistency.
- **Whether it blocks freeze:** YES.

Baseline anchors: Revocation Model §§12–14, 36–43, 65–68; Composition Architecture v0.1.1 §§13, 15–17; Qualification Architecture v0.1.1 §§11, 17; ATE-REV-003/004 and ATE-FAIL-001.

### QA-AR-07 — Risk ceilings do not carry qualification/admission assurance eligibility

- **Severity:** HIGH
- **Exact sections affected:** §§7, 11–12, 14–17, 20, 22, 27, 35 item 4.
- **Attack or failure scenario:** A subject qualifies for R2 under weak model identity/key protection or evaluator independence. An action remains R2 but local policy requires stronger assurance for sensitive data or autonomous execution. The standing credentials retain the numerical risk ceiling and are accepted without proof that the evaluated runtime and authority topology support the required assurance.
- **Why the current design permits it:** The requirements profile has `minimum_assurance_level`, but decisions/credentials carry no explicit authorizable assurance profiles or qualified assurance capability. Admission policy/gates check risk, not assurance. §22's `min` over risk levels cannot solve assurance compatibility. §35 postpones authority separation rules.
- **Required architectural correction:** Preserve evaluated assurance constraints in the normalized qualification context and narrow them in admission. Verify the authoritative action-required assurance profile, identity strength, key custody, evaluator independence, approval, and executor topology without inferring assurance from risk or credential validity. Runtime risk elevation must recheck both eligibility and action controls. Explicitly distinguish R1/R2 authority-role identifiers from R0–R4 risk identifiers when ambiguous.
- **Whether it blocks freeze:** YES.

Baseline anchors: Risk Model §§14–17, 23, 27–28, 36–38; Qualification Architecture v0.1.1 §14; Composition Architecture v0.1.1 §§5, 7, 11, 27.

### QA-AR-08 — New authority signatures have no mandatory issuance ceilings or unambiguous policy owner

- **Severity:** HIGH
- **Exact sections affected:** §§5–7, 11–12, 14, 16–17, 26–27, 35 items 1 and 4.
- **Attack or failure scenario:** A root-recognized low-risk qualification key signs a production-deployer qualification for another project or an excessive interval. An admission key signs an enlarged ceiling outside its delegated domain. Or a qualification service publishes its own permissive profile through a generic “issuer” field and then certifies compliance, producing a policy/evaluation circle without participant self-signing.
- **Why the current design permits it:** §6.1 requires authority for artifact type, but supplies no mandatory role/domain/project/capability/risk/assurance/lifetime ceilings for R11/R12 or independent verification of them. Requirements/admission policy issuers are generic. §27 prohibits changing requirements during evaluation only without a new signed profile; it does not establish that the evaluator is authorized to publish/activate that profile. The trust-root model's scope concept and baseline qualification issuer ceilings need explicit inheritance.
- **Required architectural correction:** Root-delegate bounded qualification and admission signing/revocation rights; independently reject out-of-ceiling artifacts. Assign publication/activation of eligibility policy to the registered Policy Authority function, with separately explicit concentration if a service holds both roles. R11/R12 cannot authorize themselves, activate their own root registration, or expand their own ceilings. Preserve superior emergency revocation and constrain signing APIs by artifact type/schema/domain separator.
- **Whether it blocks freeze:** YES.

Baseline anchors: Trust Root Model §§4, 6–7, 13–15, 24, 35–37; Qualification Architecture v0.1.1 §§7–9; Revocation Model §§10–11.

### QA-AR-09 — Authority independence and approvals are descriptions rather than acceptance predicates

- **Severity:** HIGH
- **Exact sections affected:** §§5–6, 8.4, 10/QG7, 14, 15/AG9, 16–17, 27, 28/T14, 29, 32.3, 35 item 4.
- **Attack or failure scenario:** A participant supplies its own favorable tests; an independent R11 merely signs the manifest. Alternatively, one administrator/service controls evaluation, admission, and a required second approval under distinct keys. The design records different role labels, but no independent assessment occurred. A previously valid generic approval is reused for another subject/role/policy.
- **Why the current design permits it:** An independent signer is not necessarily independent evidence. No evaluator authorization/independence rules are mandatory in the profile. `required_human_or_authority_approvals[]` has no canonical approved context, expiry, revocation, or independence evidence. “Strong deployment default” and distinct keys do not establish different compromise domains or risk-conditioned acceptance rules. Participant possession of R11 keys/control is not as explicit as the R12 key prohibition.
- **Required architectural correction:** Inherit baseline evaluator rules. Bind admission approvals to subject/profile, qualification digest, domain/role, policy digest, ceilings, validity, and authorized approver identity. Treat approval revocation/role loss as a dependency where current approval is required. Define policy-enforced authority concentration/independence classes by assurance; shared process or administrator cannot count twice when independence is required. Prohibit participant possession or control of qualification/admission signers and approval credentials, including signing-oracle access.
- **Whether it blocks freeze:** YES.

Baseline anchors: Qualification Architecture v0.1.1 §7; Risk Model §§17–19; Trust Root Model §§13–15, 29; conformance ATE-HUM-001/003/004.

### QA-AR-10 — Foreign qualification recognition can launder scope and hide original trust dependencies

- **Severity:** HIGH
- **Exact sections affected:** §§3.1–3.3, 7–8, 12–17, 19–20, 28/T4, 35.
- **Attack or failure scenario:** Domain B recognizes an issuer/domain in A and admits a subject under an identically named local role whose requirements are stronger. B's admission is then presented to C as local evidence while A's origin, evaluator limits, or remote suspension disappear. A compromised recognition relationship can remain usable through a local admission whose own state is unchanged.
- **Why the current design permits it:** Recognition lists plus role equality/minimum profile versions do not define semantic equivalence, target audience, original authority path, local scope narrowing, non-transitive trust, or foreign/current relationship dependencies. T4 references federation policy, but the actual admission gates do not require the federation contract or preserve its provenance.
- **Required architectural correction:** Default initial scope to local-only unless the full existing federation contract is explicitly applied. Foreign qualification contributes evidence to a local admission decision, never sovereign local authority. Require approved profile/role/capability mappings by digest, original provenance, intended local audience/domain/project, constrained authority paths, and current foreign plus local relationship state. Local suspension wins. B cannot conceal A's dependency or imply C recognizes it; deny unknown semantic mapping or required remote state.
- **Whether it blocks freeze:** YES.

Baseline anchors: Reference Architecture §§15, 20, 22; conformance ATE-FED-001 through ATE-FED-006; Federation Model §§5–8, 17, 23–30, 36–39, 44–46.

### QA-AR-11 — Conceptual artifacts lack a mandatory coherent issuance and verification contract

- **Severity:** HIGH
- **Exact sections affected:** §§9–12, 15–17, 20.2, 29–30, 35.
- **Attack or failure scenario:** A valid pass decision for a narrow profile produces a credential with a wider lifetime/capability set. An admission credential is issued without any retained matching admission decision. Two services interpret absent exclusion arrays, duplicate fields, status enums, or the same extension differently; one silently ignores an unknown eligibility constraint.
- **Why the current design permits it:** QualificationCredential references a decision ID but not its digest and has fields absent from the decision. AdmissionCredential does not reference AdmissionDecision at all. The design lacks explicit equality/narrowing checks across decision/profile/credential, supported artifact versions, mandatory extension negotiation, and a selected canonical encoding. Schema gates are recommended, and “all mandatory gates” never clearly makes the enumerated security predicates mandatory. The general fail-closed principle is correct but does not define these omitted predicates.
- **Required architectural correction:** Inherit the normative ATE encoding/version/domain-separation rules, without inventing a second serialization system. Require retained, digest-bound grant decisions and explicit field derivation/equality/narrowing. Establish mandatory acceptance predicates even if diagnostic gate order remains flexible. Define missing/empty/unknown field meanings; unknown controlling versions/constraints fail closed. A signed CapabilityToken extension is sufficient without a top-level schema field only if all consumers enforce the same versioned semantics and include the dependencies in signed composition.
- **Whether it blocks freeze:** YES.

Baseline anchors: ATE-CORE-005/006/007, ATE-CAP-004; Trust Root Model §15; Composition Architecture v0.1.1 §§15, 27.

### QA-AR-12 — Audit records cannot reliably reconstruct eligibility at issuance, decision, and execution

- **Severity:** HIGH
- **Exact sections affected:** §§11–12, 16–19, 20.2, 26, 29, 31/QA-INV-14, 33 item 10, 35 item 5.
- **Attack or failure scenario:** After an incident, investigators find qualification/admission audit rows and an executed ATE decision but cannot determine which exact credential pair, runtime profile, policy/status observations, approval set, or compatibility path controlled that action. An admission credential was released just before an audit persistence crash and is usable although its causal decision record never became durable.
- **Why the current design permits it:** §29's minimum records omit several causal identifiers/digests and epochs, recorder signature/sequence, and explicit linkage from eligibility to token/decision/execution. A generic `controlling_artifact_hashes[]` could hold the needed material but is not required to do so. Digest enumeration alone does not retain retrievable evidence bytes. Durable evidence is required as an invariant, but credential-release ordering, audit-unavailability behavior, and reconciliation are unspecified.
- **Required architectural correction:** Define qualification/admission events as typed extensions of the existing canonical audit record. Retain immutable evidence and policy/state snapshots, profile digests, decisions/credential digests, approval and compatibility lineage, and observation/revocation epochs. Link the exact pair to capability issuance, ATE semantic context, and execution rechecks. Persist required issuance evidence before credential release; deny release on required persistence failure. Represent denied/malformed attempts, state changes, signing use, and missing terminal transitions without inventing a subject identity when parsing fails. Apply existing risk-specific independent preservation requirements.
- **Whether it blocks freeze:** YES.

Baseline anchors: Audit Model §§6–8, 18–21, 28–30, 34–38, 40–44; Composition Architecture v0.1.1 §28; ATE-AUD-004/005/007/008.

### QA-AR-13 — Parallel qualification semantics and a four-case success boundary can bypass the current baseline

- **Severity:** MEDIUM
- **Exact sections affected:** §§2, 5–13, 18–20, 24–25, 31–35, 37–38.
- **Attack or failure scenario:** An implementation follows this draft's four QA tests and reports the qualification connection established while omitting baseline mandatory profile, lifecycle, issuer-ceiling, assurance, and compatibility cases. `QUALIFIED` in this new state machine and `ACTIVE` in the normalized baseline context drift into separate sources of truth.
- **Why the current design permits it:** The draft does not identify the existing revised qualification architecture or frozen local qualification protocol as inherited dependencies. It introduces a second profile/manifest/credential/state vocabulary and says four cases suffice for the first diagnostic PoC. That statement is reasonable for a narrow diagnostic, but it is not reconciled with §33/34's wider architectural claims or the baseline's frozen 15-test local qualification-conformance contract.
- **Required architectural correction:** Declare document precedence and an explicit mapping to existing qualification objects/statuses, retaining their security invariants. Add admission rather than redefining qualification. Preserve the four cases as smoke diagnostics only, not qualification conformance or freeze evidence. Identify additional admission-specific negative/race evidence needed for claims: already-issued token/grant withdrawal, wrong evaluated profile, capability/assurance excess, stale policy/state rollback, evidence invalidation, unauthorized signer/approval, compatibility substitution, and unavailable required state/audit. These may be consolidated; no model calls or large test machinery are necessary.
- **Whether it blocks freeze:** YES — specification coherence and claim boundaries must be resolved before freeze.

Baseline anchors: Qualification Architecture v0.1.1 §§1–9, 31–33; Qualification Protocol Freeze v0.1 §§2–3, 7; conformance §§3, 28–29, 33, 36. The freeze record controls future local qualification-conformance runs; it is not blanket implementation authorization or a requirement to run an experiment during this design review.

## C. Non-blocking findings

### QA-AR-14 — Non-transferability and delegation rules should be explicit

- **Severity:** LOW
- **Exact sections affected:** §§12–13, 17, 20–21, 28/T11, 31.
- **Attack or failure scenario:** An admitted agent dispatches a child agent and treats delegation as inherited eligibility, or treats a standing credential as a consumable bearer secret with its own nonce. These interpretations create misleading security and operational claims.
- **Why the current design permits it:** Exact subject binding already rejects another subject's use, but delegation, child principals, ownership transfer, and copied public credentials are not directly addressed. There is no affirmative delegation grant, so this is clarification rather than an independently permitted authority path once the binding contract is corrected.
- **Required architectural correction:** State that standing credentials are public/reusable evidence, not bearer capabilities; copying grants nothing. No implicit delegation, transfer, redelegation, child-agent inheritance, or reuse of another session's action evidence is allowed. A child needs its own valid eligibility pair/live context, or a separately specified constrained delegation architecture outside v0.1. Identity ownership transfer must be assessed as a controlling change. A standing credential need not be single-use; ATE action authorization remains single-use.
- **Whether it blocks freeze:** NO, assuming QA-AR-03 and the baseline exact-subject/session rules are resolved and inherited.

### QA-AR-15 — Authority numbering and duplicate machinery add avoidable complexity

- **Severity:** LOW
- **Exact sections affected:** §§5–6, 18, 26, 29–30, 32.3, 35.
- **Attack or failure scenario:** Teams infer that adding R11/R12 requires separate services, registries, credential storage, and bespoke status/audit systems; the duplicated controls then diverge operationally.
- **Why the current design permits it:** New numbered roles and parallel vocabulary are introduced without a minimal mapping to existing authority functions and shared control-plane abstractions. The draft permits colocation, but does not distinguish a signing permission from a service or administrative trust boundary.
- **Required architectural correction:** Treat qualification/admission as narrowly delegated logical signing functions. Reuse root registration, current-state observations, revocation closure, canonical audit, evidence archive, and composition extensions. No additional root hierarchy, scalar score, global registry, or mandatory separate host is justified solely by these two functions. Keep independence requirements explicit where risk demands them.
- **Whether it blocks freeze:** NO for naming/topology simplification itself; actual authority permissions and baseline semantic conflicts remain blocking under QA-AR-08/09/13.

## D. Authority-role analysis for R11 and R12

Qualification and admission are necessary distinct *decisions*: demonstrated role eligibility does not obligate a local domain to accept participation. Distinct decisions do not prove that two new globally numbered authority classes, services, or administrative organizations are necessary.

| Function | Existing ATE relationship | Minimal safe mapping |
|---|---|---|
| Publish/activate qualification and admission policy | R4 Policy Authority function | Register explicit eligibility-policy artifact permissions; local policy remains controlling. This function is separate from evaluating compliance unless concentration is explicitly permitted. |
| Attest identity/runtime | R2 Identity/Runtime Authority | Continue supplying live principal/profile/session evidence; identity issuance alone does not prove role eligibility. |
| Evaluate behavioral evidence | R5 Behavioral Evidence Authority | Continue issuing evidence under approved evaluator rules; behavioral attestation alone is not aggregate qualification. |
| Aggregate qualification decision | Baseline already defines Qualification Authority and issuer ceilings | Reuse that scoped logical function. If R11 is retained, it is an explicit registry label for this function, not a second qualification architecture or root power. R5 alone is insufficient because qualification includes non-behavioral controls. |
| Accept local participation | R1 authorizes trust-domain membership; R6 administers bounded capability issuance | Prefer a narrowly delegated membership/admission permission from R1 governance. R12 may name that operational permission. Do not give an online admission service the root registry signing key. An R6 service can host the permission when policy allows, but its CapabilityToken permission does not itself imply admission authority. |
| Authorize exact governed action | R6, R7, R8, R9 retain their existing boundaries | Neither R11 nor R12 replaces capability verification, trust composition, or executor validation. |
| Publish state/audit | Existing revocation/current-state and R10 audit functions | Register scoped changes/events rather than introducing new registries or trust roots. |

**Recommendation:** Keep two explicit logical functions and separate signed decisions. Reuse the baseline Qualification Authority for qualification and a root-delegated local membership function for admission. New R11/R12 labels are acceptable only after the authoritative role model declares their exact artifact types, scope/assurance/lifetime ceilings, policy ownership, revocation rights, and concentration rules. The labels themselves add no security.

A low-risk service may host both functions, using separately scoped keys/permissions and auditable concentration. Distinct keys on a shared process do not demonstrate independence. High-assurance policy must constrain common control/compromise domains where independence is required. Neither service can register itself as trusted, rewrite its own governing ceiling, manufacture a required independent approval, or possess executor resource authority through admission.

## E. Missing invariants

These are correction targets, not a replacement protocol. Each should inherit the named baseline semantics rather than create a competing definition.

1. **Eligibility narrowing:** Every admitted/issued/usable capability is within one coherent current qualification/admission pair and all authoritative ceilings; exclusions win; unrelated credentials cannot be unioned into an unsupported grant. (02)
2. **Exact profile continuity:** Evaluation, qualification, admission, capability, and trust decision bind the verified principal and immutable evaluated profile or an authorized non-expanding compatibility path. (03, 05, 11)
3. **Evidence lifecycle closure:** Loss of continuously current evidence or a missed mandatory refresh deterministically removes qualification usability and dependent admission/execution usability. (04)
4. **Pending execution closure:** Eligibility loss blocks already-issued but unexecuted dependent tokens/grants; a historical grant is not sovereign. (01)
5. **Admission validity horizon:** Effective authorization cannot outlive admission, qualification, continuously required evidence, review, approval, or stricter freshness deadlines. (01, 04, 05)
6. **Current-state provenance:** Status/policy observations have authorized sources, exact digests, epochs, freshness, monotonicity, and safe recovery; an old signed ADMITTED state cannot override newer withdrawal. (06)
7. **Issuance stability:** Controlling changes between evaluation and credential/grant persistence cause bounded reevaluation or denial; execution rechecks handle later changes. (01, 06)
8. **Assurance eligibility:** Required action assurance must be supported by qualification and admission constraints; risk ceilings alone are insufficient. (07)
9. **Authority ceilings and no circular trust:** Every policy, evaluation, qualification, admission, compatibility, approval, and status signer is delegated for its exact function/scope; no operational signer widens its own authority. (08, 09)
10. **Approval/evaluator independence:** Independence is a machine-verifiable policy condition, not a role-name or distinct-key assertion. (09)
11. **Local and non-transitive recognition:** Foreign evidence never conceals origin or expands local eligibility; local recognition revocation invalidates dependent admission. (10)
12. **Coherent versioned artifacts:** Decisions, credentials, manifests, extensions, and composition bind the same supported semantics; unknown controlling data fails closed. (11)
13. **Auditable release and causality:** Required durable evidence precedes credential release and permits reconstruction of the exact eligibility pair and state at each authorization/execution stage. (12)
14. **One qualification source of truth:** New admission rules extend the current qualification/composition contracts; new state labels map explicitly and do not weaken frozen conformance claims. (13)
15. **No implicit eligibility transfer:** Copied credentials, child agents, delegation, new sessions, and ownership changes grant no inherited authority. (14)

QA-INV-7 is directionally sound but needs operational dependency rules. QA-INV-11's restriction to *new* authorization is insufficient for pending execution. QA-INV-12 prevents changed evidence bytes, but does not establish evidence applicability, evaluator authorization, or continuing validity. QA-INV-14 requires durability but needs causal retention and release ordering. §19's compatible-supersession exception and §25's optional renewal require reconciliation with exact prerequisite digests and non-expansion rules.

## F. Recommended minimal corrections

1. Declare baseline precedence and reuse its qualification definition, evaluated profile, evidence lifecycle, issuer ceilings, signed compatibility, status, and normalized qualification context. Add only the admission-specific decision, bounded credential/context, and state mapping.
2. Freeze one mandatory integration contract: signed qualification/admission digests and semantic contexts in the capability/ATE path; mandatory consumer enforcement; eligibility intersection; action-assurance support; execution-invalidating dependencies; earlier validity deadlines. Explicit top-level ATE fields are optional if a versioned signed extension provides identical enforcement.
3. Specify the local admission policy/state owner, authenticated active manifest/status observations, rollback/freshness/stability rules, and deterministic review/change transitions. Deny unknown material compatibility and unavailable required state.
4. Root-delegate bounded qualification/admission permissions and enforce ceilings independently. Preserve policy/evaluator/approver independence where required; avoid unnecessary new services and roots.
5. Define renewal and compatibility as new signed, auditable context transitions. No silent prerequisite replacement, timestamp extension, widened capability/assurance, or revived revoked identifier.
6. Use the existing audit/evidence plane for retained decisions, supporting bytes, exact policy/status/approval observations, credential-release ordering, and capability-to-execution correlation.
7. Scope v0.1 local-only or explicitly inherit the full federation contract. Label four cases diagnostic; retain baseline conformance requirements and add consolidated admission-specific adversarial/race cases before broader claims.

No implementation, model evaluation, production service, replacement protocol, or design modification is required to make these architectural corrections reviewable. Freeze should wait until the mandatory contracts and inheritance are concrete in a corrected candidate and receive a focused follow-up review.

### Review-objective coverage

| Requested attack area | Assessment / finding coverage |
|---|---|
| Permanent badge; stale qualification/admission; evidence ceases to support eligibility | Explicit principle is strong; operational lifecycle, state, and renewal gaps: 04–06. |
| Ambient authority; eligibility confused with action authorization | Direct admission-as-execution is expressly prohibited; signed integration/pending grant gap: 01–02, 11. |
| Subject/runtime/model/session/provider substitution; copying/replay/delegation/transfer | Exact live profile binding and clone limitations: 03; artifact coherence: 11; explicit transfer/delegation clarification: 14. Action replay remains governed by baseline nonce rules. |
| Revocation propagation; TOCTOU across evaluation/issuance/decision/execution | Dependency closure, bounded freshness, stable observations, final execution recheck: 01, 04–06. |
| Policy supersession; role change; capabilities beyond qualification | Non-expanding compatibility and renewal, exact scope intersection: 02, 05–06. |
| Trust-domain boundaries; cross-domain laundering | Local control, semantic mappings, original provenance, relationship currentness: 10. |
| Risk/assurance downgrade | Risk principles credited; assurance-qualified runtime/authority constraints missing: 07. |
| Self-certification/circular trust; separation of duty; R11/R12 necessity | Bounded delegation, policy ownership, evaluator/approval independence: 08–09; role analysis in D; simplification: 15. |
| Missing/malformed/unavailable/ambiguous evidence; failure open | General fail-closed rule credited; specific required predicates and version/currentness contracts: 03–04, 06, 09, 11–12. |
| Audit/forensic reconstruction | Causal credential/decision/execution linkage, retained observations/evidence, release ordering: 12. |
| Unnecessary machinery; missing/contradictory/unenforceable invariants | Baseline reuse and claim boundaries: 13, 15; correction invariants in E. |

## G. Final disposition

**NOT_READY_FOR_FREEZE**

There are 13 blocking findings (12 HIGH, 1 MEDIUM) and 2 non-blocking LOW findings. No CRITICAL finding is asserted: the draft explicitly preserves the action-specific ATE/executor boundary rather than affirmatively granting unconditional protected-resource authority. The HIGH findings nevertheless permit eligibility checks to be bypassed, broadened, laundered, or become stale under plausible implementations of the incomplete contracts. Draft status and lack of implementation do not reduce their severity.

The central idea is viable, but the proposal is not yet a coherent extension of the specified ATE baseline. Freeze and implementation authorization should remain withheld until the minimal mandatory corrections above are resolved. This review makes no changes to the design artifact and authorizes no implementation.

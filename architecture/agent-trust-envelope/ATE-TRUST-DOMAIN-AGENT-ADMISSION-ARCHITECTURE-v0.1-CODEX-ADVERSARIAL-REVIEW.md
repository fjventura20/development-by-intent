# ATE Trust-Domain Agent Admission Architecture v0.1 — Codex Adversarial Review

**Date:** 2026-09-16
**Review type:** Complete adversarial architecture review; DESIGN ONLY.
**Primary artifact:** `ATE-TRUST-DOMAIN-AGENT-ADMISSION-ARCHITECTURE-v0.1.md`.
**Reviewed repository commit:** `31dbbf7ee4670070bf653e42687ae92ff322bb8a`.
**Primary Git blob:** `1bfba71720ead8c8b4d7133e70fd69745cca4ca1`.
**Controlling task:** `ATE-TRUST-DOMAIN-AGENT-ADMISSION-ARCHITECTURE-v0.1-CODEX-REVIEW-TASK.md`.

The primary artifact was read in full. All ten required baseline artifacts were inspected: Qualification & Requalification Architecture v0.1.1 and its Final Review; Trust-Decision Composition Architecture v0.1.1; Revocation & Trust-State Model; Risk & Assurance Policy Model; Trust Root & Key Custody Model; Audit & Accountability Model; Enforcement Plane; Reference Architecture & Component Interaction Model; and Production Requirements & Conformance Profile. Both required historical review/adjudication artifacts were read as context only. The superseded Qualification & Admission draft is not normative.

References below use repository-local filenames, abbreviated after this paragraph, and exact numbered sections or invariant/requirement identifiers. “Qualification,” “Composition,” “Revocation,” “Risk,” “Key Custody,” “Audit,” “Enforcement,” “Reference,” and “Conformance” mean the respective baseline artifacts listed above, with the exact versions required by the task. “Primary” means the reviewed admission architecture. Findings identify architectural ambiguity or missing binding, not observed exploits in running software. Baseline precedence is credited: several unsafe outcomes are already forbidden, but the admission extension must define its new bindings and dependency ownership without relying on an unstated interpretation.

## A. Architecture strengths

1. Primary §§1–6, 19–21, 29, and 34 preserve `QUALIFIED != DOMAIN_ADMITTED != AUTHORIZED_TO_ACT != EXECUTED`. Admission is public eligibility evidence, never a resource credential, bearer capability, or substitute for a signed action-specific TrustDecision.
2. Primary §§2–3 explicitly inherit qualification rather than create another qualification system. The final qualification review's shared-state interpretation is preserved by §13. Existing revocation, audit, encoding, authority, and executor planes retain ownership.
3. Primary §§9–10 and 19–20 mandate narrowing across capability, resource/project, risk, assurance, governance, portability, and validity. Explicit prohibitions win. One coherent current pair must support every required dimension; unrelated credentials cannot be unioned. Risk and assurance are checked separately.
4. Primary §§8, 26, and A-I12/A-I13 bound admission signing to delegated ceilings, reserve policy activation to Policy Authority, prohibit self-registration and ceiling expansion, and reject fabricated independence. Different keys in one compromise domain do not count as independent factors. Participant signing-oracle control is expressly prohibited.
5. Primary §§11–12 and 27 require exact decision/credential digest binding and equality or narrowing derivation, mandatory supported semantics, domain separation, and fail-closed handling of ambiguous or unknown controlling data. Conceptual schemas need not select a database or wire encoding here.
6. Primary §§13–15, 17, 22–25, and 30 explicitly require current ACTIVE admission and usable qualification, monotonic authenticated state, mandatory review deadlines, bounded stability checks, earlier validity horizons, and executor rechecks. Withdrawal and qualification loss are expressly execution-invalidating for dependent unexecuted authority; checking only new capability issuance would violate this draft.
7. Primary §28 requires durable evidence that reconstructs the principal/profile, exact qualification/admission, authority ceilings, policy/status epochs, approvals, lineage, capability issuance, semantic context, execution recheck, and outcome. Required persistence precedes release; malformed requests need not invent an identity.
8. Primary §§4, 18, 29, and 33–34 reject implicit portability, transfer, child-agent inheritance, and broader safety claims. The lean PoC boundary is correctly limited and authorizes no experiment. No finding below assumes compromised root governance or revocation of an already committed irreversible effect.

These safeguards resolve much of the earlier review. They are not optional recommendations. The remaining defects concern new provenance and continuation semantics, and classification of admission-specific dependencies.

## B. Blocking findings

### TDA-AR-01 — Capability issuance lacks a mandatory signed binding to its controlling qualification/admission pair

- **Severity:** HIGH
- **Blocking:** YES
- **Exact primary sections affected:** §§10, 19–23, 28; §31 A-I5, A-I9, A-I17, A-I19; §32 A-T7/A-T16.
- **Baseline anchors:** Composition §§10, 14, 17, 20, 23, 26–27 and TD-I13/TD-I14; Revocation §§18, 51–54, 75, 79–81 (INV-R7); Reference §§5.8, 6, 14; Conformance ATE-REV-002 and ATE-EXEC-001.
- **Attack or failure scenario:** A token CT1 is issued under Q1/A1. A1 is withdrawn before CT1 is consumed. The participant subsequently receives a distinct admission A2 with the same capability/resource/risk ceiling. CT1 is presented with Q1/A2 for a fresh composition request. All containment predicates in §19 can pass, and the new TrustDecision binds A2. An executor rechecking only the pair in that decision sees A2 ACTIVE, not CT1's withdrawn prerequisite A1. The participant has recycled still-unexecuted authority whose original dependency was lost. The same provenance problem arises when a different qualification is selected while all artifacts describe otherwise compatible action scope.
- **Why the current design permits it:** §20 requires the capability issuer to consume a current pair but does not require that pair's IDs/digests, policy, and controlling dependencies to be signed into the token or an authenticated issuance context bound to its digest. §21 signs the pair selected at trust composition; it does not require equality to the pair that controlled token issuance, or retain that issuance pair as an additional execution-invalidating dependency. The baseline CapabilityDecisionContext has no admission provenance field. §10's coherent-current-pair rule proves containment for the selected pair, not identity with the historical issuance pair. §28 requires forensic reconstruction, but an audit link alone is not explicitly required to participate in runtime authorization validation. §§22–23 demand closure but do not supply the missing token-to-dependency edge.
- **Required architectural correction:** Require an authenticated capability issuance context bound to CT1's exact signed bytes/digest and identifying the controlling qualification/admission pair and dependency manifest. Carry it into CapabilityDecisionContext, DecisionSemanticContext, TrustDecisionInput, and TrustDecision through signed digest bindings. Require either exact equality with the composed pair or explicit retention and validation of both controlling dependency sets under a reviewed rule; v0.1 should use equality. Withdrawal cannot be repaired by selecting a different credential at composition. A fresh admission or approved continuation requires new capability authorization where the old issuance dependency was invalidated. The executor must check issuance dependencies as well as the decision's current admission dependencies. A signed, required extension is sufficient; new top-level token fields are not necessary.
- **Correction class:** Clarification/tightening of cross-artifact provenance, not a new authorization architecture.

This is not a second finding for ordinary withdrawal. The draft already prohibits execution after withdrawal; the defect is the missing mandatory binding that identifies *which* withdrawn admission controls a pre-existing token.

### TDA-AR-02 — AdmissionContinuation has no deterministic normalization and downstream identity contract

- **Severity:** HIGH
- **Blocking:** YES
- **Exact primary sections affected:** §§8, 12, 15–16, 19–25, 28, 30; §31 A-I6, A-I8, A-I14/A-I15/A-I17; §32 A-T11/A-T12.
- **Baseline anchors:** Qualification §§4, 16, 18–22, 31–33 (Q-I3/Q-I8/Q-I10); Composition §§6–7, 14, 17, 20, 23, 27 and TD-I6/TD-I14; Revocation §§55, 76–77; Conformance ATE-CORE-002/005/007 and ATE-REV-002.
- **Attack or failure scenario:** A1 binds Q1/profile P1. Q1 is superseded by ACTIVE Q2/profile P2 after authorized non-expanding qualification work. An authorized signer issues a continuation. One consumer rejects A1 because §19 requires its bound qualification to remain ACTIVE and its credential still contains P1/Q1. Another consumer rewrites the normalized context to P2/Q2, omits the continuation digest, and grants. An executor reconstructing the old credential or checking Q1 denies; an executor following a mutable continuation index may accept a different later continuation. This creates divergent authoritative meanings for the same admission evidence and signed action context. Even with no malicious signer, a pending grant can be evaluated against a different prerequisite path at execution than at signing.
- **Why the current design permits it:** §16 and A-I15 expressly allow a signed current non-expanding continuation, and §8 provides `may_issue_continuation`; these protections are credited. But §16 supplies no mandatory relation between the continuation, exact admission credential/decision digests, source and target qualified profile, normalized context, and authoritative state observations. AdmissionDecisionContext still has exactly one qualification and one profile, with no specified rule for whether these are original or replacement values and no mandatory continuation reference. §§15 and 19 require current usability/ACTIVE state without defining the exception's normalized meaning. §§21–23 do not require the selected continuation path to be signed into decision input and rechecked. A generic current/non-expanding invariant does not resolve these mutually different interpretations.
- **Required architectural correction:** Prefer removing continuation from v0.1 and requiring a new AdmissionDecision/AdmissionCredential on qualification replacement. If retained, define one mandatory normalization: preserve immutable original evidence; bind exact admission credential/decision, Q1/P1, Q2/P2, compatibility artifact and authorized continuation scope; evaluate Q2 under all current admission preconditions; intersect preserved admission ceilings with Q2 and current policy/delegation/conditions; sign the exact continuation digest and effective pair/profile into semantic and decision-input contexts. Define authoritative selection, chaining/branching limits, revocation/change semantics, deadlines, and execution dependency closure. A pending grant cannot switch paths in place; changed semantic context needs a new authorization attempt. Define when superseded Q1 is acceptable only as historical lineage, never as current qualification. Continuation cannot clear withdrawal, revive revoked identifiers, reset a missed review, or lengthen controlling deadlines without a new reviewed decision.
- **Correction class:** Bounded redesign of the continuation path if retained; simplification by deletion otherwise. The primary admission architecture need not be redesigned.

The finding does not claim that continuation may expand scope: §16 and A-I15 already prohibit expansion. It concerns how an allowed replacement path becomes one immutable, verifiable current context.

### TDA-AR-03 — Admission-specific participation and structural dependencies lack mandatory lifecycle declarations

- **Severity:** HIGH
- **Blocking:** YES
- **Exact primary sections affected:** §§7, 9, 11, 17, 19–26, 28, 30; §31 A-I9, A-I16–A-I18; §34.
- **Baseline anchors:** Qualification §§6–8, 27, 32–33 (Q-I7); Composition §§9, 11, 16–18, 26 and TD-I12/TD-I13; Revocation §§51–53, 59, 79–81; Risk §§14, 18, 23–24; Conformance ATE-REV-002, ATE-HUM-003/004, ATE-FAIL-001.
- **Attack or failure scenario:** Admission Policy requires an independent isolation-control receipt or local participation condition to be satisfied. It passes at admission issuance. The receipt expires, is withdrawn, or its governing authority loses the relevant scope before execution. A1 remains ACTIVE and qualification is unchanged. The signed decision includes the historical condition digest, while the composer and executor treat the condition as an issuance snapshot because no lifecycle was declared. No current condition recheck occurs. A different consumer treats it as continuously required and denies. The design's action outcome now depends on an unstated classification of the local admission dependency.
- **Why the current design permits it:** §2 inherits qualification evidence lifecycle semantics, which correctly close *qualification* evidence loss. Admission introduces additional local approvals, structural controls, and participation conditions. §7 lists those requirements but does not mandate a lifecycle assignment for each. §§11 and 19 retain digests without obligatory lifecycle/state/deadline references. §22 expressly conditions continuing authority/approval invalidation on policy declaration and uses “where appropriate” for dependency flags. §24 bounds continuously-current prerequisites and continuing approvals, but does not require the policy to say which new requirements are continuous, periodic, or snapshots. §25 similarly rereads only inputs marked stability-required. Composition §17 requires explicit change semantics for every controlling dependency, yet the primary does not define an admission-specific completeness rule that rejects a missing classification. Inherited fail-closed rules help only once a requirement's continuing meaning is established.
- **Required architectural correction:** Mandate explicit lifecycle/change semantics for every controlling admission policy requirement, including local approvals, participation conditions, structural receipts, authority delegations, compatibility/continuation dependencies if retained, and policy compatibility. Reuse existing lifecycle and state-observation concepts. Declare stability class, refresh/expiry deadline, state authority, compatibility predicate, invalidation flag, and final recheck requirement as applicable. Missing or unsupported classification is invalid policy/context, not snapshot permission. Snapshot classification must be explicit and policy-authorized; continuously-current or periodic loss must deterministically invalidate dependent unexecuted capability and trust grants through the signed manifest. Revocation of a controlling policy/key cannot be suppressed by a local snapshot declaration where baseline rules make it invalidating. Require verified completeness at issuance and composition, and enforce the resulting signed requirements at execution.
- **Correction class:** Clarification/tightening using existing dependency machinery; no duplicate evidence evaluator or revocation plane.

This finding groups approval, condition, structural-control, and continuing authority omissions under one root cause. It does not require every historical test or approval to be continuously current.

## C. Non-blocking findings

### TDA-AR-04 — The local-only scope has inconsistent wording around an explicit federation exception

- **Severity:** LOW
- **Blocking:** NO
- **Exact primary sections affected:** §§4, 5.5, 18; §31 A-I21; §32 A-T17; §§33–34.
- **Baseline anchors:** Conformance §§19, 35 and ATE-FED-001–006; Reference §§15, 21–22 (RA-INV-9); Key Custody §§35–36. Historical adjudication QA-AR-10 and §§6.3/7 supplies context only.
- **Attack or failure scenario:** A reviewer sees “local-domain only” and assumes that an integration with already-reviewed federation policy is excluded, while a deployer follows §18's explicit current-policy exception. A resulting claim may omit the actual foreign dependency boundary from its declared scope.
- **Why the current design permits it:** §18 first reserves foreign qualification for a future composed profile, then permits a reviewed explicit mapping under existing federation architecture now. §5.5 also mentions federation constraints. These statements do not define one consistent v0.1 scope label. They do not establish a foreign authority bypass: the exception requires reviewed explicit existing federation semantics, §18 prohibits hiding foreign dependencies, and baseline federation constraints remain controlling. The task and historical adjudication allow reuse of the full existing federation contract, so this is not a new blocking federation defect.
- **Required architectural correction:** State either that v0.1 unconditionally excludes foreign qualification, or that the core is local-only and an explicitly identified existing full federation profile is a separate composed scope with all provenance, mapping, relationship-state, narrowing, and local-revocation rules preserved. A bare allowlist or role-name mapping is insufficient. Keep future local PoC and conformance claims within their declared boundary.
- **Correction class:** Clarification; no new federation design.

### TDA-AR-05 — The second admission artifact is permitted but not shown to be necessary

- **Severity:** LOW
- **Blocking:** NO
- **Exact primary sections affected:** §§5.3, 6, 11–12, 16, 28, 31 A-I14; §§32–33.
- **Baseline anchors:** Audit §§6–8, 19–21, 40, 62; Key Custody §§4.1, 9, 49–50; Reference §§5.3, 6, 21. Historical adjudication QA-AR-15/§6.2 is context only.
- **Attack or failure scenario:** A service separately mints a decision and credential with narrowing fields, introducing another derivation operation, issuer check, retention object, and retry/release boundary even when no compact portable presentation is needed. Implementations add operational complexity without a distinct security benefit.
- **Why the current design permits it:** §11 already allows an equivalent durable authoritative decision record, but §§6 and 12 prescribe a separate credential path. No independent offline-presentation or lifecycle requirement explains why two admission payloads are essential. This is not presently an authority-widening vulnerability: §§11–12, 27, and A-I14 mandate retained digest binding and testable derivation.
- **Required architectural correction:** Explain the separate credential's consumer/presentation purpose or use one signed bounded membership artifact with retained decision evidence and authoritative status. If both remain, consider a credential that references the decision rather than repeats independently narrowed authority. Preserve exact signed provenance, durability, and current-state enforcement in either representation.
- **Correction class:** Optional simplification/clarification; no security redesign required solely for artifact count.

## D. Answers to special questions Q1–Q5

### Q1 — Admission function

A distinct local admission *decision* is justified: qualification does not obligate domain participation, and local governance must be able to narrow or withdraw membership. Two separately signed authority-bearing payloads are not established as necessary. A root-delegated membership permission can issue one signed finite, scope-bounded artifact referencing retained immutable decision evidence, with current admission status supplied by the shared plane. This can preserve equivalent semantics while reducing derivation and retention surfaces. A compact credential plus richer decision is also safe if both have a concrete consumer purpose and the mandatory bindings remain. Merging membership into CapabilityToken itself would not preserve independent participation withdrawal unless its dependency semantics are equally explicit. See TDA-AR-05.

### Q2 — Authority role

No new globally numbered authority role is required. Primary §8 already chooses a distinct root-delegated logical signing permission, consistent with Key Custody §4.1's membership governance function. Online operational signers must receive bounded artifact/domain/project/role/capability/risk/assurance/lifetime permissions, not the root registry private key. R6 capability issuance authority or R4 policy publication does not imply admission permission. The security consequence is bounded compromise: an admission signer can issue only within separately delegated membership ceilings and cannot redefine recognized roots, policy ownership, or executor authority. Explicit concentration is allowed only within risk/independence policy; role labels or different keys do not establish independent control domains. This question is substantially resolved by §§8 and 26, not a blocking authority-numbering finding.

### Q3 — Composition integration

Partially, but not enough for freeze. §§19–24 mandate admission context in signed semantic composition, admission observations in the state vector, containment, validity narrowing, and final rechecks. Existing Composition §§14, 20, and 23 already bind the semantic-context digest transitively through TrustDecisionInput and TrustDecision, so duplicating every admission field at top level is unnecessary. A versioned required profile/extension suffices if every consumer enforces it and unsupported semantics deny. No finding is created merely because a completed profile or wire schema has not been selected.

The missing edges are capability issuance provenance (TDA-AR-01), exact continuation normalization (02), and the completeness of lifecycle/recheck declarations for new controlling inputs (03). Signing an internally coherent current admission context does not by itself prove these absent edges. Until tightened, historical issuance authority or a mutable continuation path can be detached from its true controlling dependencies.

### Q4 — Dependency closure

Direct admission/qualification loss has an explicit mandatory closure rule in §§15 and 22, and executor denial is mandatory in §23. Computed unusability is enough; Revocation §53 does not require fan-out writes revoking every dependent artifact. This preserves the shared state plane.

Closure for *all* controlling dependencies is not yet deterministic end to end. A declaration that an input is execution-invalidating requires both a signed dependency edge and exhaustive classification; the omissions in TDA-AR-01–03 prevent proving that every still-unexecuted dependent grant is checked against the same dependency path. Once that contract is complete, policy can explicitly distinguish snapshots from continuing dependencies without allowing a composer to omit a declared invalidating check. Closure remains subject to baseline authenticated observation/freshness semantics and the acknowledged final race window, not a promise of distributed atomic revocation.

### Q5 — Minimality

The architecture has largely achieved minimality. Qualification definitions/evaluation/evidence stay upstream; admission status is a shared-plane projection; audit/encoding/revocation reuse is explicit; no global score, registry, root, or mandatory host separation is added. A domain-specific policy and status projection are necessary semantics, not duplicate control planes. The subtler additional machinery is continuation, plus the decision-to-credential derivation surface. Removing continuation and using fresh admission evidence on replacement is the safest lean v0.1 correction. Adding required lifecycle metadata reuses existing semantics and does not justify a second evidence or revocation engine.

## E. Missing or weak invariants

The following tighten the existing candidate invariants rather than replace baseline ownership:

1. **Signed issuance provenance:** Every admission-dependent CapabilityToken has one authenticated issuance pair and manifest; composition and execution cannot substitute a later pair for a lost controlling issuance dependency. Strengthen A-I5/A-I9/A-I17. (TDA-AR-01)
2. **Immutable continuation path:** An allowed continuation normalizes to one exact effective principal/profile/qualification/admission context with the path digest signed into authorization; original evidence remains immutable and historical. Pending grants never follow a different path. Strengthen A-I6/A-I14/A-I15/A-I17. (02)
3. **Complete dependency classification:** Every new controlling admission requirement has explicit lifecycle, stability, deadline, authoritative state, compatibility, and invalidation/recheck semantics. Missing classification invalidates policy/context. Strengthen A-I9/A-I16–A-I18. (03)
4. **Declared recognition boundary:** Core local-only scope and any existing full federation composition are separately explicit in both policy and claims. A-I21 is sound against implicit portability but its version boundary needs consistent wording. (04)

No additional finding is asserted for role widening or taxonomy/exclusion laundering: §§9–10, 19–21, 27, 30, and inherited Qualification §§13/31–32 and Composition §§3/27 require compatible scoped role/action semantics and reject ambiguity. A derived admission context cannot legitimately reinterpret an unknown alias or mutable resource set as broader authority. These existing mandatory contracts should be preserved in the eventual profile, using the baseline canonical taxonomy or accepted signed translations and explicit exclusion precedence.

The finite deadline, assurance, issuer-ceiling, audit, and non-transfer invariants are explicit. Their schemas are conceptual minimums; inherited common signing envelopes supply artifact/key/version metadata. Such omissions from illustrative structures alone are not blocking findings. Public standing credentials can remain reusable after fresh re-attestation of an unchanged profile; that does not confer another session's action authority. A-I20 must be read with qualification's re-attestation distinction and current session verification.

### Complete adversarial target coverage

| Task targets | Assessment |
|---|---|
| 1–2: widening and unrelated credential union | Explicitly prohibited by §§9–10/19–21; issuance-pair provenance gap is TDA-AR-01. |
| 3: ambient authority/substitution for token or decision | Explicitly prohibited by §§1/4/6/12/21/29/34; no direct bypass established. |
| 4–5: qualification loss and pending grants | §§15/22–23 establish direct denial; complete provenance and path closure need 01–03. |
| 6: TOCTOU across evaluation, credential, capability, signing, effect | §25 inherits bounded stability and final rechecks; lifecycle classification and exact dependent artifacts need 01–03. No distributed atomicity claim is inferred. |
| 7: stale/rolled-back status/policy | §§7/13/19/23/25/30 and A-I10 inherit authenticated sources, freshness, and rollback rejection. Old ACTIVE evidence cannot override newer accepted state. |
| 8–9: exact principal/profile and replacement | Ordinary binding is mandatory in §§11–12/19/29; continuation integration is 02. |
| 10: role aliases, taxonomy, resources, exclusions, projects | Mandatory narrowing, canonical compatible semantics, exclusions, and ambiguity denial are credited; see E. |
| 11: risk passes but assurance insufficient | §§9–10/19–20 and A-I11 require both; Risk/Composition independently preserve current action assurance. |
| 12–14: signer ceilings, circular policy, false independence | §§7–8/26 and baseline registry authority explicitly prohibit these paths. Continuing dependency classification is 03. |
| 15: foreign/federation entry | Implicit recognition is prohibited; full existing semantics are required for exception. Scope wording is non-blocking 04. |
| 16: copying, children, delegation, ownership, runtime/session substitution | §§12/26/29–30 and inherited runtime/session binding reject implicit transfer. Authorized profile replacement path is 02. |
| 17: missing/malformed/unavailable/version/ambiguity fail-open | §§9/23/27/30 explicitly deny; completeness of new dependency classifications needs 03. |
| 18: validity beyond controlling deadlines | §§9/12/17/24/30 explicitly impose earlier deadlines; selection/classification of continuing prerequisites needs 02–03. |
| 19–20: forensic reconstruction and release-before-durability | §28 mandates reconstructability, §25 mandates required persistence before release; runtime signed provenance/path needs 01–02. Policy-conditioned durability does not erase baseline mandatory audit requirements. |
| 21–22: duplicate planes, contradictions, missing invariants | Shared ownership is explicit; continuation/current-ACTIVE interpretation and complete binding are 01–03. |
| 23–24: minimality and overclaim | Continuation removal and credential simplification are recommended; 04–05 and Q5 address complexity. §§33–34 appropriately limit safety, PoC, federation, and production claims. |

## F. Recommended minimal corrections

1. Add the signed capability issuance pair/context binding and exact equality/completeness predicate. Bind the issuance manifest into the existing semantic/input/decision chain and require executor validation. This is provenance metadata and validation, not a new grant plane. (01)
2. Remove AdmissionContinuation from the initial version. Qualification replacement then requires a new admission decision/credential and fresh dependent authorization. If continuation is essential, provide the complete normalized path and downstream binding/change contract identified in 02 before freeze.
3. Add a mandatory dependency lifecycle/change classification table or equivalent deterministic policy contract for all admission-local approvals, conditions, controls, authority, and policy/compatibility prerequisites. Consumers reject incomplete policy/context and enforce all declared invalidating checks. (03)
4. Make the local-only versus existing-full-federation composition statement consistent. Explain the second admission artifact's consumer purpose or simplify it. (04–05)

After correction, a focused design re-review should walk these cases: token issued under withdrawn A1 presented with ACTIVE A2; qualification/profile replacement with unchanged admission evidence; conflicting continuation paths if retained; expiry/withdrawal of a continuously-current admission condition while status stays ACTIVE; omitted lifecycle classification; and removal of any controlling issuance dependency from a signed manifest. Expected results must follow directly from the corrected normative contract. No harness, conformance protocol, model call, or implementation is authorized by this review, and none was performed.

Retain the existing mandatory narrowing, authority ceilings, independent approval predicates, shared monotonic state, signed required-profile negotiation, deadline minima, durable evidence ordering, and executor-only effects. Do not create another qualification, revocation, evidence archive, audit ledger, or trust-root hierarchy to fix these gaps. Correct a new architecture candidate; preserve this reviewed primary and the baseline unchanged.

## G. Final disposition

**NOT_READY_FOR_FREEZE**

| Severity | Blocking YES | Blocking NO | Total |
|---|---:|---:|---:|
| CRITICAL | 0 | 0 | 0 |
| HIGH | 3 | 0 | 3 |
| MEDIUM | 0 | 0 | 0 |
| LOW | 0 | 2 | 2 |
| **Total** | **3** | **2** | **5** |

The narrow admission layer is viable and substantially stronger than its historical predecessor. Freeze is blocked by incomplete mandatory issuance provenance, continuation normalization, and admission dependency classification. These are bounded corrections; the central qualification → local admission → action-specific ATE → executor architecture does not require replacement. No unconditional protected-resource authority path or root compromise is asserted, so no CRITICAL finding is assigned. This review authorizes no implementation and modifies no primary or baseline artifact.

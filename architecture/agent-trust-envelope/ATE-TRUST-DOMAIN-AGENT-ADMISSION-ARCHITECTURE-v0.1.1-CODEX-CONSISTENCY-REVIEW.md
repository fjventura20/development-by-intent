# ATE Trust-Domain Agent Admission Architecture v0.1.1 — Codex Focused Consistency Review

**Date:** 2026-09-16
**Review scope:** Complete focused adversarial consistency review; DESIGN ONLY.
**Primary artifact:** `ATE-TRUST-DOMAIN-AGENT-ADMISSION-ARCHITECTURE-v0.1.1.md`
**Reviewed repository commit:** `59fa5115a54e3d55dd0eb2bdc202503005d1df15`
**Primary Git blob:** `0db0e51a0d9b0dcb0275db0c0f990b3b039c2674`
**Controlling task:** `ATE-TRUST-DOMAIN-AGENT-ADMISSION-ARCHITECTURE-v0.1.1-CODEX-CONSISTENCY-REVIEW-TASK.md`

## 1. Disposition and review basis

**READY_FOR_FREEZE**

The three prior HIGH blockers are fully closed. No substantive new finding or baseline contradiction was identified. The candidate supplies the missing signed capability-issuance edge, removes qualification continuation, and makes admission dependency lifecycle classification mandatory and fail closed. This is a design conclusion, not evidence of an implemented system's correctness. This review does not freeze the candidate or authorize implementation, experimentation, or protocol creation.

The primary was read in full. The following required baselines were inspected for the controlling contracts relevant to the corrections and regressions. References below use these abbreviations and exact numbered sections or requirement/invariant identifiers:

| Abbreviation | Required baseline | Controlling anchors inspected |
|---|---|---|
| Qualification | `ATE-AGENT-QUALIFICATION-REQUALIFICATION-ARCHITECTURE-v0.1.1.md` | §§6, 16–22, 25–27, 31–33; Q-I3, Q-I7, Q-I8, Q-I10, Q-I19 |
| Qualification Final Review | `ATE-AGENT-QUALIFICATION-REQUALIFICATION-FINAL-REVIEW-v0.1.md` | §§1–10, 13; shared-state interpretation and frozen P2 boundary |
| Composition | `ATE-TRUST-DECISION-COMPOSITION-ARCHITECTURE-v0.1.1.md` | §§9–10, 12–18, 20, 23, 26–27; TD-I13/TD-I14 |
| Revocation | `ATE-REVOCATION-TRUST-STATE-MODEL-v0.1.md` | §§18–20, 50–55, 76–77; logical dependency closure and immutable replacement |
| Risk | `ATE-RISK-ASSURANCE-POLICY-MODEL-v0.1.md` | §§13–15, 22–23, 36–38 |
| Key Custody | `ATE-TRUST-ROOT-KEY-CUSTODY-MODEL-v0.1.md` | §4, §§50–52; R1/R4/R6 and INV-K1–INV-K10 |
| Audit | `ATE-AUDIT-ACCOUNTABILITY-MODEL-v0.1.md` | §§17–21, 34–37 |
| Enforcement | `ATE-ENFORCEMENT-PLANE-v0.1.md` | §§2–5, 8–13; INV-E1–INV-E10 |
| Reference | `ATE-REFERENCE-ARCHITECTURE-COMPONENT-INTERACTION-MODEL-v0.1.md` | §§5.3–5.14, 6, 13–14, 22 |
| Conformance | `ATE-PRODUCTION-REQUIREMENTS-CONFORMANCE-PROFILE-v0.1.md` | §§5–6, 12–14, 16, 18, 20–21; ATE-CORE-005/007, ATE-REV-002/003/004, ATE-EXEC-001 |

The prior `ATE-TRUST-DOMAIN-AGENT-ADMISSION-ARCHITECTURE-v0.1-CODEX-ADVERSARIAL-REVIEW.md` and `ATE-TRUST-DOMAIN-AGENT-ADMISSION-ARCHITECTURE-v0.1-CODEX-ADJUDICATION.md` were also read. The superseded admission v0.1 is historical, not controlling. Qualification was not reopened independently of checking candidate consistency.

Conceptual minimum schemas are evaluated with the candidate's mandatory prose, common signing envelope, and baseline precedence. A missing illustrative field is not a finding when the normative contract already requires its binding and verification. Conversely, audit reconstruction is not credited as a substitute for a cryptographic runtime authorization edge.

## 2. Mandatory closure checks

| Prior HIGH blocker | Status | Basis |
|---|---|---|
| TDA-AR-01 | CLOSED | §§22–25 bind the exact issuance pair and manifest into the signed token and signed decision semantics; §§26–27 require pending-execution closure and executor equality/currentness checks. A replacement pair requires new capability authorization. |
| TDA-AR-02 | CLOSED | §§4, 17–18 remove continuation and prohibit Q1-bound admission from depending on Q2. Qualification replacement requires a new decision/admission context and fresh capability authorization; renewal and status transitions provide no exception. |
| TDA-AR-03 | CLOSED | §§5.5, 7–9 mandate exhaustive explicit lifecycle/change declarations and immutable manifest binding; §§21, 23, 25–29, 34 require lifecycle-aware validation, signed rechecks, deadline containment, and fail-closed handling without weakening baseline revocation. |

### C1 — Capability issuance provenance

Issue CT1 under Q1/A1. Section 22 requires a canonical `CapabilityAdmissionBinding` identifying the exact subject/profile, qualification ID and credential digest, admission ID and decision digest, dependency manifest digest, policy/issuance state, authorization instance, and validity. Its digest is cryptographically committed by the signed CapabilityToken or a mandatory signed token extension. Changing that binding after issuance invalidates the token commitment.

| Attempt | Deterministic outcome and anchor |
|---|---|
| Withdraw A1; present CT1 with Q1/A2 of equivalent scope | Denied: §24 requires exact admission ID/decision/manifest equality, independently of ceiling equivalence. §§15, 26–27 also make withdrawn A1 unusable. |
| Present CT1 with Q2/A2 | Denied: both qualification and admission identities/digests differ; §§18, 24 forbid switching pairs. |
| Select another current admission after issuance | Denied by §§23–24. New admission cannot rehabilitate CT1; authorize a new token for the new pair. |
| Use only a post-issuance audit provenance link | Insufficient: §22's signed token commitment is mandatory independently of its audit record. §§25, 27 verify the binding at runtime. |
| Compose a fresh TrustDecision omitting the original issuance pair | Denied: §§24–25 require token-to-selected-pair equality and mandatory signed binding/manifest semantics in CapabilityDecisionContext and the semantic/input/decision chain. |
| Keep an old grant after A1 withdrawal | No protected credential release or effect: §§26–27 invalidate dependent unexecuted authority and require current admission recheck. |

The binding direction avoids a token/binding digest cycle: signed token bytes commit to the binding digest; the later audit record links token ID/digest to that binding. The audit link is forensic, while the signed token edge controls authorization. Composition §§14, 20, 23 permit the required digests to be carried transitively through a mandatory signed semantic context. A completed wire profile is not necessary to establish that architectural requirement.

### C2 — Qualification replacement

The only references to continuation in the candidate exclude it (§4) or state that no exception exists (§17). Admission Authority scope has no continuation permission. Section 18 expressly prohibits an admission bound to Q1 from beginning to depend on Q2, pending token/decision switching, identifier revival, byte replacement, or redirected references.

Supersession makes the bound qualification and its dependent admission unusable (§§17–18). Compatibility declarations inherited from Qualification may preserve evidence or reduce upstream requalification cost; they do not override the admission replacement rule. Admission policy replacement cannot reinterpret immutable Q1 bindings (§§13, 18, 24, 34). Mutable indexes or executor reconstruction cannot select Q2 without violating the signed digests and exact equality checks.

Renewal (§19) evaluates current qualification, policy, authority ceilings, dependencies, conditions, and status. It cannot bypass §18 even when participation scope is unchanged. A review-required return to ACTIVE requires a new decision (§16); historical records remain immutable. Any resulting changed pair requires new capability authorization. Profile-preserving runtime re-attestation remains allowed under Qualification §16 and Q-I19: fresh runtime evidence for an unchanged qualification is not an admission continuation to a replacement qualification.

### C3 — Dependency lifecycle completeness

Section 5.5 defines a dependency by its controlling effect, not by a closed enumeration. Sections 7–9 require every controlling policy requirement to declare lifecycle, decision-time class, authoritative state ownership, change invalidation, and execution recheck semantics. Deadlines, refresh rules, and compatibility predicates apply where relevant. The successful decision binds one immutable exact dependency manifest (§13), with completeness checked against active policy (§9).

| Controlling dependency | Issuance, composition, and execution treatment |
|---|---|
| Local approvals | Exact-context approval binding (§30), explicit lifecycle rule (§8), validity at issuance (§11), currentness as declared (§21), and final invalidating rechecks/deadline limits (§§26–28). |
| Participation conditions | Manifest membership and declared lifecycle; continuous loss or missed periodic refresh removes usability even if a cached admission status still reads ACTIVE (§§8–9, 21, 27, 34). |
| Structural-control receipts | Same completeness/lifecycle contract; a historical receipt cannot be silently treated as current or as a snapshot (§§8–9, 11, 25–27). |
| Admission authority/delegation | Explicit dependency classification plus current authorization/ceilings (§§8, 10–11, 19). Snapshot labeling cannot suppress baseline key/delegation invalidation (§8 rule 4; Key Custody §52; Conformance ATE-TRUST-003). |
| Admission policy compatibility/currentness | Signed active policy and manifest policy digest/epoch (§§7–9); incompatible supersession/revocation invalidates pending authority (§26), with executor policy recheck (§27). |
| Mandatory review deadlines | Deadline loss causes REVIEW_REQUIRED (§19), a non-ACTIVE execution-invalidating state (§§15, 26); §28 bounds authorization by the earlier mandatory deadline. |
| Other mutable prerequisites, including required audit availability | Broad dependency definition and policy completeness prevent omission; declared currentness, invalidation, and signed rechecks apply, with stronger baseline mandatory audit rules preserved (§§3, 8–9, 25–28, 32, 34). |

An explicit policy-authorized issuance snapshot remains historical after collection age increases; that does not promise continuing currentness. A continuously-current dependency must remain usable. A periodic dependency must satisfy its refresh deadline, with lease-like deadlines limiting downstream validity. Missing or unsupported classification invalidates policy/context rather than defaulting to snapshot semantics (§§8–9, 31, 34).

Contradictory flags cannot legitimately omit a recheck for an invalidating dependency: Composition §17 mandates that check, Composition §26 requires current state of every invalidating dependency, and candidate §§3, 8, 26 preserve those stronger rules. The manifest and signed composition requirements identify the dependencies for the executor; inability to perform a required check fails closed (§§25, 27, 34). These rules reuse the existing evidence vocabulary and shared trust-state/revocation plane, including computed closure rather than mandatory fan-out revocation writes.

## 3. Regression checks

| Required regression target | Assessment and candidate/baseline anchors |
|---|---|
| 1. Admission widens qualification | No path identified: §§11–12, 21, 23 require intersection across capability, resource/project, risk, assurance, governance, portability, and validity; Qualification §33 remains controlling. |
| 2. Union of unrelated credentials | §§12, 24–25 require one coherent exact pair supporting every action dimension; no multi-credential union is defined. |
| 3. Assurance/risk containment lost | §§11–12, 21, 23, 25, 28 preserve both ceilings and current action requirements; Risk §§13–15, 36–38 prevent upward assurance inference or stale-policy downgrade. |
| 4. Admission becomes bearer authority | §§1, 14, 33 require authenticated matching subject/profile and downstream action authorization; Enforcement §§2–3, 8 retain executor control. |
| 5. Withdrawal blocks only new issuance | §§26–27 expressly close unexecuted grants before credential release/effect, including when the old token remains cryptographically valid. |
| 6. Provenance omitted from decision/recheck | §§22, 24–25, 27 require signed token binding, decision semantic dependencies, and executor verification. |
| 7. Rollback or stale observations accepted | §§7, 11, 15, 21, 27, 34 and A-I11 require authenticated current observations, monotonic epochs, and freshness; Composition §13 and Conformance ATE-REV-003/004 remain controlling. |
| 8. Credential versus decision authority ambiguous | §14 makes the credential optional presentation of a retained signed decision, with equality/narrowing derivation and current status. Direct decision presentation must expose all required bindings. |
| 9. Hidden foreign portability | §§4, 20, 34 and A-I24 unconditionally reject foreign qualification/admission; future federation composition is outside this version. |
| 10. Authority circularity/self-registration | §§7, 10, 30 require root-delegated bounded roles, separately authorized policy publication, and genuine required independence; no participant signing-oracle control. |
| 11. Audit relationship treated as runtime binding | §22 independently requires the token's cryptographic commitment; §32's causal audit records supplement it. Audit §§19–21 do not replace authorization validation. |
| 12. Unsupported extension silently ignored | §§9, 25, 31, 34 require mandatory supported semantics and denial for unsupported controlling versions/extensions; Composition §15 preserves exact profile identity. |
| 13. Executor cannot identify invalidating dependencies | §§9, 13, 22, 25 bind complete manifests into signed authority; §§26–27 inherit exhaustive invalidating checks from Composition §§17, 26. Unavailable required dependencies deny execution. |
| 14. Lifecycle rules weaken baseline revocation | §8 rule 4 and §§3, 26 prohibit this explicitly. Snapshot evidence never exempts controlling key/policy invalidation; Revocation §§50–54 retain dependency-aware closure. |
| 15. Qualification/composition contradiction | No substantive conflict identified. §§2–3 inherit upstream qualification; §§18, 24 tighten downstream pair selection; §25 uses versioned required composition semantics without rewriting baseline ownership. |

Exact pair equality concerns immutable authorization prerequisites, not a blanket demand that every issuance-time context digest or epoch equal every later current observation. Section 24 specifies the equality dimensions; §§25–27 separately require current observations. Revocation §50 allows unrelated epoch advancement and dependency-aware compatibility checking. Likewise, a suspension/reinstatement path in §16 does not revive a revoked or superseded identifier or switch its bound qualification. Current authorization and replay validity still apply.

Sections 29 and 32 preserve stability checks and required persistence before release. These contracts retain the baseline final race limitation; they do not claim distributed atomic revocation or reversal of an already committed irreversible effect. No protocol, harness, model evaluation, or execution experiment was performed.

The prior nonblocking concerns are also resolved: §§4/20 make local scope unconditional (TDA-AR-04), and §14 explains the optional credential's presentation purpose without granting independent decision authority (TDA-AR-05).

## 4. Explicit answers to Q1–Q5

**Q1 — Exact pair equality sufficient?** Yes for this local v0.1.1 architecture when applied with its signed issuance binding, exact decision/credential and manifest digests, authenticated current-state validation, and required executor rechecks. Equality of scope alone is insufficient and explicitly forbidden. No remaining permitted substitution path was identified; equality alone would not excuse ignoring a changed controlling dependency.

**Q2 — Continuation removal complete?** Yes. Sections 17–18 govern renewal, compatibility, supersession, transitions, reference resolution, and execution without a replacement exception. A new controlling qualification requires a new admission decision/context and new capability authorization for that pair. Re-attestation of an unchanged qualification remains distinct.

**Q3 — Deterministic dependency treatment?** Yes at the architectural level. Every controlling requirement must declare lifecycle/change semantics and be represented in the bound manifest. Issuance validates completeness and stability; composition validates currentness and signs required dependencies; execution checks every invalidating dependency under declared semantics and baseline minima. Unsupported or incomplete rules deny. The future profile must instantiate these required semantics, not infer them.

**Q4 — Narrow admission extension?** Yes. Qualification remains upstream, capability issuance and action-specific composition remain authorization functions, and the executor controls effects. Admission status projects the existing state plane; audit, roots, canonical encoding, lifecycle vocabulary, and revocation closure retain existing owners. The new binding and manifest add provenance and validation obligations rather than a second authorization/state system.

**Q5 — Additional architectural machinery before lean local conformance design?** No. A future lean protocol can instantiate the already-required signed token/composition profile, manifest completeness checks, canonical admission identity for direct-decision presentation, lifecycle rules, and dependency-aware rechecks. These are protocol details implementing defined invariants, not missing architectural authority. This review does not create that protocol or authorize implementation.

## 5. Findings and final disposition

No substantive findings are raised. There are no correction requests; implementation details and acknowledged baseline limitations above are not counted as findings.

| Severity | Blocking YES | Blocking NO | Total |
|---|---:|---:|---:|
| CRITICAL | 0 | 0 | 0 |
| HIGH | 0 | 0 | 0 |
| MEDIUM | 0 | 0 | 0 |
| LOW | 0 | 0 | 0 |
| **Total** | **0** | **0** | **0** |

**Final disposition: READY_FOR_FREEZE**

TDA-AR-01, TDA-AR-02, and TDA-AR-03 are CLOSED. Freeze remains a separate governance action. Only this review artifact is changed; the primary architecture and all baseline artifacts remain unchanged.

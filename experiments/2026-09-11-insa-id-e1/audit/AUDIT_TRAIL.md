# INSA-ID-E1 — Audit Trail

This directory preserves the protocol v1, v2, v3, v4, v5, v6 + proposal v4, v5, v5.1 packages as audit history. Protocol v6.1 (frozen-candidate-rev6.1) is at the top level of `experiments/2026-09-11-insa-id-e1/`.

## v1 frozen-candidate (2026-09-11)

- **v1 commit:** `26f7ed3ecc588a292fbe6983105b0c28ec0c24f5`
- **v1 MANIFEST SHA-256:** `8052e7cfa2403d87faaa4d5008cd13f5f0cafe359e1d1963f2a3c674c605141a`
- **v1 path:** `audit/v1-frozen-candidate/`
- **v1 defects:** v4 corrections list documents them (in this AUDIT_TRAIL, see below). v1 was superseded by v2, v3, v4, v5, and v6.

## v2 frozen-candidate-rev2 (2026-09-11)

- **v2 commit:** `6fdd79083608f83d9c496dcb4e69f7db29eff1e0`
- **v2 MANIFEST SHA-256:** `97946101df774e5403e327302b3a0917960461274854bbf3dc140768094bf3cf`
- **v2 path:** `audit/v2-frozen-candidate/`
- **v2 defects:** Superseded by v3.

## v3 frozen-candidate-rev3 (2026-09-11)

- **v3 commit:** `2d0cf74054a48c578bb8cb65ce985e4767600809`
- **v3 MANIFEST SHA-256:** `54487cf090165ce5ae5974b8daf9157ea218c05ef17bceaa4a42a9e25cff3d1f`
- **v3 path:** `audit/v3-frozen-candidate/`
- **v3 defects identified by Frank-as-PI review:**
   - MANIFEST contained contradictory SHAs for the same artifacts.
   - dimensions-decomposition referenced pre-edit mutation-dimensions SHA.
   - preservation-dimensions contained `<filled at freeze time...>` unresolved placeholder.
   - C20 envelope bounds described as "TBD" / not precomputed.
   - C20 derivation script did not actually verify inputs.
   - evaluator packet applied binary/zero "axis failure" conventions to the BIB 4-dim vector.
   - Cyclic reference pattern between baseline-binding and baseline-statistics.
   - Generic placeholder `2026-09-11T00:00:00Z` used as actual freeze time.
   - Scorebook self-referential hash.
   - Per-candidate fresh evaluator session not explicit.
   - Reconstruction-input referenced nonexistent files.

## v4 frozen-candidate-rev4 (2026-09-11)

- **v4 commit:** `1b70d65301854e04ee22f7e3407b40cf47de480e`
- **v4 MANIFEST SHA-256:** `2e08e6e1b52b821be8cece45ca4006ebd24c1d74bbfca8e58a87696fce6f35d7`
- **v4 path:** `audit/v4-frozen-candidate/`
- **v4 defects identified by Frank-as-PI v5 review:**
   - Real scorebook → blind-map → C20 interface: C20 used synthetic reconstruction_id/block/generic scores fields, did not require --blind-map.
   - Evaluator packet was not self-sufficient (missing test prompt template, BIB scoring anchors, M1-M4 definitions, C12 definitions, return schema).
   - Blind-map timing language suggested Phase 2 construction; v6 says Phase 0 construction + Phase 2 use.
   - C20 metric provenance language did not distinguish INSA-ID-E1's preregistered operationalization from the v0.1 inherited computation.

## v5 frozen-candidate-rev5 (2026-09-11)

- **v5 commit:** `69007b3352e8fc26d65680f3a7c6a1ddc1dc8d0c`
- **v5 MANIFEST SHA-256:** `a7615784277ecdf768752d3e292af988d6e7b45997556eb186d8b4f31a7cdace`
- **v5 path:** `audit/v5-frozen-candidate/`
- **v5 defects identified by Frank-as-PI v6 review:**
   - Frozen test-invocation schedule was missing (v5 referenced test-invocations in the protocol but did not freeze `inputs/test-invocations.json` with a deterministic schedule). The executor could in principle invent the birthdate at runtime.
   - Historical BIB 0-4 anchors were paraphrased/simplified instead of reproduced verbatim from the BIB-001 frozen evaluator rubric. Current Arm-C and Arm-M candidates must be scored against the same measurement rubric that generated the frozen BIB baseline.
   - Worldwide-historical-significance rule was the broader "global, regional, or widely-cited" criterion instead of the preregistered ≥2-of-4 rule (v0.1 §9.2 PI pass 3).
   - The operator-side scorebook format omitted G_subset_b_axis_scores, losing C12 evidence for Phase 4.
   - The C20 derivation did not require a blind map and did not reject Arm-M blind IDs in Arm-C scorebooks.
   - C20 did not require exact match between scorebook R/B/arm/candidate and the blind map.
   - The Phase-3 "same blind_id" wording was incorrect (the frozen blind-map design has one-ID->one-tuple; Phase 3 uses a FRESH per-arm blind_id for the same birthdate/test).

## v6 frozen-candidate-rev6 (current; awaiting Frank-as-PI execution GO)

- **v6 commit:** *(filled at v6 freeze)*
- **v6 MANIFEST SHA-256:** `54c0f803981ae89ec64705a64c9118a9944b54f6d842b1d4b0de3b1743184e26`
- **v6 protocol SHA-256:** `24ef0c793efbd97b02b944b9a800b7821711117bb4c25c765e33cc9431966916`
- **v6 EXECUTION-ORDER SHA-256:** `acce2b9fb70264a2291734ac85e6d9660b551634e48a11a908e37fe7b567483d`
- **v6 evaluator-input-packet SHA-256:** `7ed8a72bd73ce59e1ded5146855cb2869c942f3703c767a6413690c3fd7251fa`
- **v6 c20-derivation SHA-256:** `49097f4cbf207f2aaa943e24e207d4adfaeffbe11912b8d8ada96c45c164b2d76`
- **v6 normalize-and-join SHA-256:** `7daca294b0f088a5bb2802df04d321247bed4873b6a40041ef9457ce1f120836`
- **v6 binding-verification SHA-256:** `4ad613f016bfa3e52d12c16183933cbb50315a762d5a196bc81ead80b55ab34b`
- **v6 test-invocations SHA-256:** `67a7ab98493f3113c96d3f78cecd827ed83b3136a11b3d28f92d9de7b5fe3a0a`
- **v6 evaluator-rubric SHA-256:** `c19ac46203bddb7eeb360819e6e5fa46c94f031a926d6cb6d7d07e5ee0af3409`
- **v6 path:** `experiments/2026-09-11-insa-id-e1/` (top level, NOT in audit/)
- **v6 status:** Frozen-candidate-rev6 (per proposal v5.1 @ `1f84c31`).
- **v6 corrections vs v5:**
   - **Frozen test-invocation schedule.** `inputs/test-invocations.json` content-addresses the exact 5-test corpus from the BIB-001 frozen test set, repeated twice (run-1 + run-2) per (R, B, arm) cell, mapping every candidate index 1..10 to its exact `Birthdate <date including year>` invocation. The executor MUST consume the test invocation from this artifact via the blind map; it MUST NOT invent or select the birthdate at runtime.
   - **Restored exact historical BIB scoring anchors.** `inputs/evaluator-rubric.json` content-addresses the verbatim BIB-001 frozen evaluator rubric (`experiments/2026-09-05-dbi-bib-001-rerun-001/inputs/EVALUATOR-RUBRIC.md`) used to produce the 85-record calibration. The 4 calibrated dimensions (contract_compliance, selection_behavior, narrative_behavior, functional_completeness) and their 0-4 anchors are reproduced verbatim. Current Arm-C and Arm-M candidates are scored against the same measurement rubric that generated the frozen BIB baseline.
   - **Restored frozen worldwide-historical-significance rule (M3).** v6 uses the preregistered ≥2-of-4 rule (v0.1 §9.2 PI pass 3 ruling). M3 PASS iff at least 2 of the 4 criteria are satisfied. v6 does NOT use the broader "global, regional, or widely-cited" criterion.
   - **Frozen normalize-and-join script.** `hashing/normalize-and-join.py` consumes the raw evaluator-return JSON + locked blind map and produces the immutable operator-side scorebook, preserving M_scores + G_subset_a_4dim_vector + G_subset_b_axis_scores + evaluator_self_report. Adds reconstruction_id, block, arm, candidate, birthdate, test_id, run solely from the blind map. Rejects unknown / duplicate blind IDs, duplicate tuples, forbidden provenance fields, and any operator-metadata mismatch (fatal nonzero on any violation).
   - **C12 evidence preserved in locked scorebooks.** The operator-side scorebook retains the full raw scoring payload, including all 8 C12 axes (G_subset_b_axis_scores). The Phase-4 analysis consumes these locked values directly to compute C12 per-axis failure rates and the BROKEN rule.
   - **C20 derives R/B exclusively from the blind map.** `hashing/c20-derivation.py` v6 requires `--blind-map`, loads the operator-side Arm-C scorebook, joins each record against the blind map, verifies exact match on reconstruction_id/block/arm/candidate/birthdate, rejects arm != expected, rejects (R, B) outside the preregistered current expected cells, and fails fatally on any mismatch.
   - **Phase 3 wording corrected.** Phase 3 uses the same test invocation (same birthdate) as Phase 1 for the matched (R, B, test, run) tuple, but generates a **FRESH per-arm blind_id** (the frozen blind-map design has one-ID->one-tuple; the run-keyed identifier is per-arm, not shared with Arm-C). Phase 3 does NOT use "the same blind_id" as Arm-C.
   - **Clean-environment verification.** `hashing/binding-verification.py` v6 runs from a clean checkout using only frozen repository artifacts and temporary files it creates itself. The `clean-environment verification case` is exercised at freeze time and asserts that a clean run produces the same MANIFEST.
   - **No /tmp/bib_data.pkl dependency.** The binding-verification script reads envelope records from `inputs/baseline-statistics.json` (the canonical frozen artifact), not from a /tmp pickle.
- **v6 structural tests verified at freeze time:**
   - All 26 listed SHAs match on-disk
   - All cross-references consistent (no SHA conflicts)
   - D = M ∪ P ∪ O pairwise-disjoint: PASS
   - Evaluator-rubric.json content-addresses the exact frozen BIB rubric: OK (sha256=`0d665161...`)
   - Evaluator-rubric.json content-addresses the exact frozen test corpus: OK (sha256=`a61a7505...`)
   - Evaluator packet contains the exact historical BIB 0-4 anchors for all 4 dimensions: OK
   - Evaluator packet contains the preregistered ≥2-of-4 worldwide-significance rule: OK
   - Evaluator packet does NOT contain the broader "global, regional, or widely-cited" rule: OK
   - test-invocations.json content-addresses the exact 5 frozen test corpus invocations: OK
   - C20 healthy real-schema scorebook + blind map: c20_joint_pass=***
   - C20 missing R2/B: c20_joint_pass=False (missing current cell)
   - C20 degraded R1/B (contract_compliance=0): c20_joint_pass=False (worst current cell mean > frozen historical envelope bound)
   - C20 unknown blind ID: FATAL exit 2
   - C20 duplicate blind ID: FATAL exit 2
   - C20 Arm-M blind ID in Arm-C scorebook: FATAL exit 2
   - C20 tampered historical scorebook: FATAL exit 2
   - C20 tampered baseline membership: FATAL exit 2
   - normalize-and-join rejects forbidden provenance fields in evaluator return: FATAL
   - normalize-and-join rejects metadata mismatches between raw evaluator return and blind map: FATAL
   - C12 evidence (all 8 axes) preserved in the locked scorebook: OK
   - Clean-environment verification case: PASS (the verifier ran successfully in a fresh tempdir using only frozen repo artifacts + temporary files it created itself)
- **v6 truthful freeze timestamps:** `frozen_at_utc_date` (date-only); `manifest_generated_at_utc` (set by the binding-verification script via `datetime.now(timezone.utc).isoformat()`).
- **v6 no model dispatch, no evaluator invocation, no candidate generation:** confirmed (no `runs/`, no scorebooks, no synthesis files, no execution-authority witness, no C20-decision-record).

## v6.1 frozen-candidate-rev6.1 (current; awaiting Frank-as-PI execution GO)

- **v6 prior audit package:** `audit/v6-frozen-candidate/` (v6 commit `b875515f5aaa7ff9ef0af4b42c6117b5e8d83855`)
- **v6.1 changes:**
  - Phase-0 blind map now freezes all 60 blind IDs (30 Arm-C + 30 Arm-M) for the complete 3×1×2×10 execution tuple universe; no blind ID may be created, replaced, or modified after Phase 0.
  - `inputs/test-invocations.json` explicitly enumerates candidate 1..10 for R1/B1, R2/B1, and R3/B1 (T1r1, T1r2, T2r1, T2r2, T3r1, T3r2, T4r1, T4r2, T5r1, T5r2), with no shorthand layout.
  - `hashing/blind-map-builder.py` deterministically builds/validates the complete 60-entry map: exactly 60 unique IDs, 60 unique tuples, 30 C + 30 M, 10 per (R,B,arm) cell, exact candidate→test/run/birthdate mapping, no missing/extra tuple.
  - `hashing/normalize-and-join.py` requires exactly the expected 30 blind IDs for each arm and rejects silent omissions; locked scorebooks require complete 30/30 arm coverage.
  - `hashing/c20-derivation.py` consumes the complete operator-side Arm-C scorebooks and exact blind map, with exact 30-tuple completeness enforced.
  - Structural tests use the actual 30-record arm schema and include missing-ID, extra-ID, wrong candidate→test, wrong candidate→run, wrong birthdate, duplicate tuple, and Arm-M substitution failures.
  - Phase-3 language says the distinct Arm-M blind_id is already assigned and locked in Phase 0; it does not create a fresh ID after Phase 0.
  - Clean-environment binding verification is reported as successful without claiming canonical MANIFEST equality from a dynamic-timestamped regeneration.

## v6.1 frozen-candidate-rev6.1 (current; awaiting Frank-as-PI execution GO)

- **v6 prior audit package:** `audit/v6-frozen-candidate/` (v6 commit `b875515f5aaa7ff9ef0af4b42c6117b5e8d83855`)
- **v6.1 changes:**
  - Phase-0 blind map now freezes all 60 blind IDs (30 Arm-C + 30 Arm-M) for the complete 3×1×2×10 execution tuple universe; no blind ID may be created, replaced, or modified after Phase 0.
  - `inputs/test-invocations.json` explicitly enumerates candidate 1..10 for R1/B1, R2/B1, and R3/B1 (T1r1, T1r2, T2r1, T2r2, T3r1, T3r2, T4r1, T4r2, T5r1, T5r2), with no shorthand layout.
  - `hashing/blind-map-builder.py` deterministically builds/validates the complete 60-entry map: exactly 60 unique IDs, 60 unique tuples, 30 C + 30 M, 10 per (R,B,arm) cell, exact candidate→test/run/birthdate mapping, no missing/extra tuple.
  - `hashing/normalize-and-join.py` requires exactly the expected 30 blind IDs for each arm and rejects silent omissions; locked scorebooks require complete 30/30 arm coverage.
  - `hashing/c20-derivation.py` consumes the complete operator-side Arm-C scorebooks and exact blind map, with exact 30-tuple completeness enforced.
  - Structural tests use the actual 30-record arm schema and include missing-ID, extra-ID, wrong candidate→test, wrong candidate→run, wrong birthdate, duplicate tuple, and Arm-M substitution failures.
  - Phase-3 language says the distinct Arm-M blind_id is already assigned and locked in Phase 0; it does not create a fresh ID after Phase 0.
  - Clean-environment binding verification is reported as successful without claiming canonical MANIFEST equality from a dynamic-timestamped regeneration.
- **v6.1 final SHAs:** MANIFEST=`29c8f0e5307a0f8babd1819fea37f2c2420d6f00eaf05f66d75f72a1f7bdeb7c`; protocol=`b268a799cb82ad774407233b94d1d7ffd4bdf14fdda3b285dac0c1338c2ec47c`; evaluator packet=`7ed8a72bd73ce59e1ded5146855cb2869c942f3703c767a6413690c3fd7251fa`; blind-map-builder=`c1f4722bf5b65bc36213df2cd4e57422d48e390f2e5d706e5892836176883e56`; normalize-and-join=`9adae7cd9e2c4c677aabb7a08acf15bafd730a8fcc835955ac3e77064f8ace2a`; C20=`2e0a35fe04fd60bf499c2f09a63b28911cd07f5fcff3ac12a51ee2492e122dd5`; binding-verification=`8879f53dcfe256b98327bd49feddccb7644ff23106f0e8d3d29fc46769948008`.

## Proposal lineage

- **v2:** `docs/proposals/2026-09-10-INSA-ID-E1-proposal.md` (commit `5f9365f`)
- **v3:** `docs/proposals/2026-09-10-INSA-ID-E1-proposal.md` (commit `db9f77a`; Frank's four correctness corrections)
- **v4:** `docs/proposals/2026-09-10-INSA-ID-E1-proposal.md` (commit `ed95705`; Frank's four consistency corrections)
- **v5:** `docs/proposals/2026-09-10-INSA-ID-E1-proposal-v5.md` (commit `04d1d07`; Frank's architecture-binding corrections: §12 B/D/O, BIB 4-dim, baseline statistics, executor change documentation)
- **v5.1:** `docs/proposals/2026-09-10-INSA-ID-E1-proposal-v5.md` (commit `1f84c31`; Frank's five cleanup corrections)
- **APPROVED v5.1 SHA:** `1f84c3101d6add7d44ed821681946c10be8f5f5c` (Frank-as-PI authorization)

## Verification commands

```bash
# Re-run the binding-verification script (deterministic; reproduces MANIFEST)
cd experiments/2026-09-11-insa-id-e1/
python3 hashing/binding-verification.py --v6-experiment-dir . --repo-dir ../../

# Verify v6 MANIFEST SHA-256
sha256sum experiments/2026-09-11-insa-id-e1/MANIFEST.json

# Verify v1 + v2 + v3 + v4 + v5 audit packages preserved
find experiments/2026-09-11-insa-id-e1/audit -type f | wc -l   # should be ≥ 122 (v1 20 + v2 22 + v3 26 + v4 27 + v5 29 = 124)

# Verify INSA v0.3 architecture unchanged
git cat-file -t 848e0fe014f5b4a61ba2cb92e772ee3499dca9c1   # should be 'blob'

# Verify dbi-evolution-v0.1 protocol unchanged
git ls-tree origin/feature/insa-id-e1-proposal:experiments/2026-09-06-dbi-evolution-v0.1/protocol/PROTOCOL-v0.5-frozen-final.md
# Should still show blob 8874692d560d9a6363ef4105fae5384b18cf6ef2

# Verify clean-environment case: copy the v6 experiment dir to a fresh tempdir, run the verifier
cp -r experiments/2026-09-11-insa-id-e1 /tmp/v6-fresh && cd /tmp/v6-fresh && python3 hashing/binding-verification.py --v6-experiment-dir . --repo-dir ../../../..
# The clean run must produce the same MANIFEST.json SHA-256
```

## Authority boundary

This audit directory is preserved but **not** part of the v6 binding. The v6 binding references only the top-level artifacts listed in v6 MANIFEST.json.
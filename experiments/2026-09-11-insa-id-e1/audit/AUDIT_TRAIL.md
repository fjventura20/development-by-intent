# INSA-ID-E1 — Audit Trail

This directory preserves the protocol v1, v2, v3, v4 + proposal v4, v5, v5.1 packages as audit history. Protocol v5 (frozen-candidate-rev5) is at the top level of `experiments/2026-09-11-insa-id-e1/`.

## v1 frozen-candidate (2026-09-11)

- **v1 commit:** `26f7ed3ecc588a292fbe6983105b0c28ec0c24f5`
- **v1 MANIFEST SHA-256:** `8052e7cfa2403d87faaa4d5008cd13f5f0cafe359e1d1963f2a3c674c605141a`
- **v1 path:** `audit/v1-frozen-candidate/`
- **v1 defects:** v4 corrections list documents them (in this AUDIT_TRAIL, see below). v1 was superseded by v2, v3, v4, and v5.

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
   - C20 derivation did not consume the actual evaluator return schema (used synthetic reconstruction_id, block, generic scores fields).
   - C20 derivation did not require the operator-only blind map.
   - Evaluator packet was not self-sufficient (did not include the test prompt, BIB scoring anchors, M1-M4 definitions, C12 definitions, current return schema).
   - Blind-map timing language suggested the blind map was constructed in Phase 2 (must be Phase 0).
   - C20 metric provenance language did not distinguish INSA-ID-E1's preregistered operationalization from the v0.1 inherited computation.
   - Subset-(a) provenance language did not distinguish the calibrated BIB 4-dim from the global-reference-vector distance formulation.

## v5 frozen-candidate-rev5 (current; awaiting Frank-as-PI execution GO)

- **v5 commit:** *(filled at v5 freeze)*
- **v5 MANIFEST SHA-256:** *(see `MANIFEST.sha256.txt` in the top-level directory after v5 freeze)*
- **v5 protocol SHA-256:** `dfc289031f1343d9800b1a05948fbbb17d031c07b46285c14ddcf3cd9b1f3b6a`
- **v5 EXECUTION-ORDER SHA-256:** `7dc4db9f06054e113196fb763bbcb9891e4bc84ed1183fe6edaaa4c08a169f18`
- **v5 evaluator-input-packet SHA-256:** `d3ae3c717ee776788be3455d06ec67d189ef473b25bacdae7630346027bcdda3`
- **v5 c20-derivation SHA-256:** `5595f514440dd8805a05470df672ad734bf094a9aa7bf1f4a812af09503322f7`
- **v5 binding-verification SHA-256:** `1adb886a9d862e48f4ca4b619edd1dc4ff3f47264e8738fd89bd71863513991b`
- **v5 path:** `experiments/2026-09-11-insa-id-e1/` (top level, NOT in audit/)
- **v5 status:** Frozen-candidate-rev5 (per proposal v5.1 @ `1f84c31`).
- **v5 corrections vs v4:**
   - **Real scorebook → blind-map → C20 interface.** C20 now consumes the actual evaluator return schema (blind_id + M_scores + G_subset_a_4dim_vector + G_subset_b_axis_scores + evaluator_self_report) and requires a `--blind-map` input. The operator joins each evaluator-returned record to the locked blind map to recover (R, B, arm, candidate). C20 rejects unknown / duplicate blind IDs, duplicate tuples, Arm-M blind IDs in Arm-C scorebooks, and (R, B) cells outside the preregistered current expected cells.
   - **Self-sufficient evaluator packet.** Evaluators receive the test prompt + frozen behavioral contract + BIB 0-4 scoring anchors + M1-M4 definitions + worldwide-historical-significance criterion + C12 definitions + return schema. The modification specification itself is hidden. Evaluators remain blind to arm identity, reconstruction, phase, and provenance.
   - **Blind-map timing language corrected.** `preflight/blind-map.json` is constructed and locked in Phase 0, before evaluator invocation. Phase 2 USES the already-locked blind map.
   - **C20 metric provenance language clarified.** INSA-ID-E1 v5.1 preregisters its own C20 (Manhattan-from-reference-vector) and its own subset-(a) (calibrated 4-dim vector, preregistered reference vector). The 85-record BIB corpus calibrates that new rule. v5 does NOT describe INSA-ID-E1's C20 as the identical inherited v0.1 C20 computation.
   - **Subagent-(a) provenance language clarified.** The BIB 4-dim dimensions and the +1.5 / 2.5 threshold values come from predecessor calibration. INSA-ID-E1's global-reference-vector distance formulation is the v5.1 preregistered operationalization; v5 does NOT claim that this exact distance computation is verbatim the v0.1 computation.
   - **Evaluator-interface structural validation added to binding-verification.py.** The frozen verification script statically verifies: (1) evaluator packet contains the 4 correct BIB dimensions; (2) evaluator packet contains M1-M4 definitions; (3) evaluator packet contains the frozen BIB scoring anchors; (4) evaluator packet requires the exact test prompt; (5) C20 accepts the exact evaluator return structure; (6) C20 requires and uses the blind map; (7) synthetic tests use no evaluator-forbidden provenance fields.
- **v5 structural tests verified at freeze time:**
   - All 25 listed SHAs match on-disk
   - All cross-references consistent (no SHA conflicts)
   - D = M ∪ P ∪ O pairwise-disjoint: PASS
   - C20 healthy real-schema + blind map: c20_joint_pass=***
   - C20 missing R2/B: c20_joint_pass=False (missing current cell)
   - C20 degraded R1/B (contract_compliance=0): c20_joint_pass=False (worst current cell mean > frozen historical envelope bound)
   - C20 unknown blind ID: FATAL exit 2
   - C20 duplicate blind ID: FATAL exit 2
   - C20 Arm-M blind ID in Arm-C scorebook: FATAL exit 2
   - C20 tampered historical scorebook: FATAL exit 2
   - C20 tampered baseline membership: FATAL exit 2
   - Evaluator packet contains 4 BIB dimensions: OK
   - Evaluator packet contains M1-M4 definitions: OK
   - Evaluator packet contains BIB 0-4 scoring anchors: OK
   - Evaluator packet requires test prompt template (Birthdate): OK
   - Evaluator packet contains C12-1..8 definitions: OK
   - Evaluator packet documents current return schema: OK
   - Evaluator packet does NOT contain modification specification text: OK
- **v5 truthful freeze timestamps:** `frozen_at_utc_date` (date-only); `manifest_generated_at_utc` (set by the binding-verification script via `datetime.now(timezone.utc).isoformat()`).
- **v5 no model dispatch, no evaluator invocation, no candidate generation:** confirmed (no `runs/`, no scorebooks, no synthesis files, no execution-authority witness, no C20-decision-record).

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
python3 hashing/binding-verification.py --v5-experiment-dir . --repo-dir ../..

# Verify v5 MANIFEST SHA-256
sha256sum experiments/2026-09-11-insa-id-e1/MANIFEST.json

# Verify v1 + v2 + v3 + v4 audit packages preserved
find experiments/2026-09-11-insa-id-e1/audit -type f | wc -l   # should be ≥ 95 (v1 20 + v2 22 + v3 26 + v4 27)

# Verify INSA v0.3 architecture unchanged
git cat-file -t 848e0fe014f5b4a61ba2cb92e772ee3499dca9c1   # should be 'blob'

# Verify dbi-evolution-v0.1 protocol unchanged
git ls-tree origin/feature/insa-id-e1-proposal:experiments/2026-09-06-dbi-evolution-v0.1/protocol/PROTOCOL-v0.5-frozen-final.md
# Should still show blob 8874692d560d9a6363ef4105fae5384b18cf6ef2
```

## Authority boundary

This audit directory is preserved but **not** part of the v5 binding. The v5 binding references only the top-level artifacts listed in v5 MANIFEST.json.
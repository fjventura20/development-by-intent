# INSA-ID-E1 — Audit Trail

This directory preserves the protocol v1 + protocol v2 + proposal v4 + proposal v5 packages as audit history. Protocol v3 (current) is at the top level of `experiments/2026-09-11-insa-id-e1/`.

## Package v1 (frozen-candidate, 2026-09-11)

- **v1 commit:** `26f7ed3ecc588a292fbe6983105b0c28ec0c24f5`
- **v1 MANIFEST SHA-256:** `8052e7cfa2403d87faaa4d5008cd13f5f0cafe359e1d1963f2a3c674c605141a`
- **v1 path:** `audit/v1-frozen-candidate/`
- **v1 defects:** v4 corrections list documents them (in v5 AUDIT_TRAIL referenced below). v1 was superseded by v2 (Frank's four correctness corrections) and then by v3 (Frank's architecture-binding corrections).

## Package v2 (frozen-candidate-rev2, 2026-09-11)

- **v2 commit:** `6fdd79083608f83d9c496dcb4e69f7db29eff1e0`
- **v2 MANIFEST SHA-256:** `97946101df774e5403e327302b3a0917960461274854bbf3dc140768094bf3cf`
- **v2 path:** `audit/v2-frozen-candidate/`
- **v2 status:** Frozen-candidate-rev2; superseded by v3 (Frank's architecture-binding corrections in proposal v5).
- **v2 defects:** v5 AUDIT_TRAIL (referenced from `docs/proposals/2026-09-10-INSA-ID-E1-proposal-v5.md` v5 corrections list) documents the v2 architecture-binding errors that v3 corrects.

## Package v3 (current; awaiting Frank-as-PI execution GO)

- **v3 commit:** *(filled at v3 freeze)*
- **v3 MANIFEST SHA-256:** *(filled at v3 freeze)*
- **v3 path:** `experiments/2026-09-11-insa-id-e1/` (top level)
- **v3 protocol SHA-256:** *(filled at v3 freeze)*
- **v3 status:** Frozen-candidate-rev3 (per proposal v5.1 @ `1f84c31…`).
- **v3 architecture binding:** Implements proposal v5.1 exactly — B as complete frozen baseline bundle; D = M ∪ P ∪ O; pairwise disjoint M, P, O; O = ∅ with frozen rationale; subset-(a) = actual calibrated BIB 4-dim vector (`contract_compliance`, `selection_behavior`, `narrative_behavior`, `functional_completeness`); subset-(b) = historical 8 C12 axes preserved verbatim, separately gated, non-collapsed; four-gate G_mod_a..d; aggregate C12 BROKEN rule; separate evaluator scoring from analysis aggregation; separate immutable Arm-C and Arm-M scorebooks; static/dynamic authority separation; frozen execution-order algorithm; no self-referential hashes (sidecar pattern); C20 in Phase 2 after Arm-C scoring; explicit executor-change limitation (claude-opus-4-7 vs v0.1's claude-sonnet-4-6); two-level Level-1/Level-2 interpretation; C20 binding is fully deterministic from `inputs/baseline-binding.json` + `inputs/baseline-statistics.json` + `hashing/c20-derivation.py`.

## Proposal lineage

- **v2:** `docs/proposals/2026-09-10-INSA-ID-E1-proposal.md` (proposal v2 commit `5f9365f`)
- **v3:** `docs/proposals/2026-09-10-INSA-ID-E1-proposal.md` (proposal v3 commit `db9f77a`; Frank's four correctness corrections)
- **v4:** `docs/proposals/2026-09-10-INSA-ID-E1-proposal.md` (proposal v4 commit `ed95705`; Frank's four consistency corrections)
- **v5:** `docs/proposals/2026-09-10-INSA-ID-E1-proposal-v5.md` (proposal v5 commit `04d1d07`; Frank's architecture-binding corrections: §12 B/D/O, BIB 4-dim, baseline statistics, executor change documentation)
- **v5.1:** `docs/proposals/2026-09-10-INSA-ID-E1-proposal-v5.md` (proposal v5.1 commit `1f84c31`; Frank's five cleanup corrections: §5.2 D wording, §7 D/O baseline labels, "5 BIB scorebooks" → "4", abbreviated tuple → full tuple, C20 binding requirement)
- **APPROVED v5.1 SHA:** `1f84c3101d6add7d44ed821681946c10be8f5f5c` (Frank-as-PI authorization)

## Verification commands

```bash
# Verify v3 MANIFEST SHA-256 (filled at freeze)
sha256sum experiments/2026-09-11-insa-id-e1/MANIFEST.json

# Verify v3 protocol SHA-256 (filled at freeze)
sha256sum experiments/2026-09-11-insa-id-e1/protocol/INSA-ID-E1-protocol.md

# Verify v1 + v2 audit packages preserved
find experiments/2026-09-11-insa-id-e1/audit -type f | wc -l   # should be ≥42 (v1 20 + v2 22)

# Verify INSA v0.3 architecture unchanged
git cat-file -t 848e0fe014f5b4a61ba2cb92e772ee3499dca9c1   # should be 'blob'

# Verify dbi-evolution-v0.1 protocol unchanged
git ls-tree origin/feature/insa-id-e1-proposal:experiments/2026-09-06-dbi-evolution-v0.1/protocol/PROTOCOL-v0.5-frozen-final.md
# Should still show blob 8874692d560d9a6363ef4105fae5384b18cf6ef2
```

## Authority boundary

This audit directory is preserved but **not** part of the v3 binding. The v3 binding references only the top-level artifacts listed in v3 MANIFEST.json.